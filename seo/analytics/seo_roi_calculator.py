"""SEO ROI Calculator - Comprehensive ROI Analysis for SEO Investments
Calculates return on investment for SEO activities with advanced attribution and forecasting.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import logging
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import asyncio
import numpy as np
from decimal import Decimal, ROUND_HALF_UP
import statistics

logger = logging.getLogger(__name__)


class ROIMetricType(Enum):
    """ROI metric types"""
    REVENUE_ROI = "revenue_roi"
    TRAFFIC_ROI = "traffic_roi"
    CONVERSION_ROI = "conversion_roi"
    BRAND_ROI = "brand_roi"
    LIFETIME_VALUE_ROI = "ltv_roi"


class InvestmentCategory(Enum):
    """SEO investment categories"""
    CONTENT_CREATION = "content_creation"
    TECHNICAL_SEO = "technical_seo"
    LINK_BUILDING = "link_building"
    TOOLS_SOFTWARE = "tools_software"
    PERSONNEL = "personnel"
    CONSULTING = "consulting"
    PAID_PROMOTION = "paid_promotion"


@dataclass
class SEOInvestment:
    """SEO investment record"""
    investment_id: str
    category: InvestmentCategory
    amount: Decimal
    description: str
    date: datetime
    duration_months: int = 1
    recurring: bool = False
    expected_roi: Optional[Decimal] = None
    tags: List[str] = field(default_factory=list)
    campaign_id: Optional[str] = None


@dataclass
class ROIResults:
    """ROI calculation results"""
    total_investment: Decimal
    total_revenue: Decimal
    net_profit: Decimal
    roi_percentage: Decimal
    payback_period_months: float
    break_even_point: datetime
    revenue_per_dollar: Decimal
    cost_per_acquisition: Decimal
    lifetime_value_ratio: Decimal


@dataclass
class SEOROIReport:
    """Comprehensive SEO ROI report"""
    period_start: datetime
    period_end: datetime
    overall_roi: ROIResults
    roi_by_category: Dict[InvestmentCategory, ROIResults]
    roi_by_channel: Dict[str, ROIResults]
    trend_analysis: Dict[str, List[float]]
    forecasted_roi: Dict[str, Any]
    benchmarks: Dict[str, float]
    recommendations: List[str]


class SEOROICalculator:
    """Advanced SEO ROI calculation and analysis system"""
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize SEO ROI calculator
        
        Args:
            config: Configuration including data sources, benchmarks
        """
        self.config = config
        self.investments: List[SEOInvestment] = []
        self.revenue_data: List[Dict[str, Any]] = []
        self.traffic_data: List[Dict[str, Any]] = []
        self.conversion_data: List[Dict[str, Any]] = []
        self.industry_benchmarks = self._load_industry_benchmarks()
        
    def _load_industry_benchmarks(self) -> Dict[str, float]:
        """Load industry ROI benchmarks"""
        return {
            'content_marketing_roi': 300.0,  # 3:1 average ROI
            'technical_seo_roi': 500.0,      # 5:1 average ROI
            'link_building_roi': 250.0,      # 2.5:1 average ROI
            'organic_traffic_growth': 20.0,   # 20% annual growth
            'conversion_rate': 2.5,           # 2.5% average conversion rate
            'customer_lifetime_value': 1200.0  # $1200 average CLV
        }
    
    async def add_investment(self, investment_data: Dict[str, Any]) -> str:
        """Add SEO investment record
        
        Args:
            investment_data: Investment details
            
        Returns:
            Investment ID
        """
        try:
            investment = SEOInvestment(
                investment_id=investment_data.get('investment_id', self._generate_investment_id()),
                category=InvestmentCategory(investment_data['category']),
                amount=Decimal(str(investment_data['amount'])),
                description=investment_data['description'],
                date=datetime.fromisoformat(investment_data['date']),
                duration_months=investment_data.get('duration_months', 1),
                recurring=investment_data.get('recurring', False),
                expected_roi=Decimal(str(investment_data['expected_roi'])) if investment_data.get('expected_roi') else None,
                tags=investment_data.get('tags', []),
                campaign_id=investment_data.get('campaign_id')
            )
            
            self.investments.append(investment)
            await self._store_investment(investment)
            
            logger.info(f"Added SEO investment: {investment.investment_id}")
            return investment.investment_id
            
        except Exception as e:
            logger.error(f"Error adding investment: {str(e)}")
            raise
    
    async def calculate_roi(self, 
                          start_date: datetime,
                          end_date: datetime,
                          attribution_model: str = "last_click") -> ROIResults:
        """Calculate comprehensive ROI for period
        
        Args:
            start_date: Start date for analysis
            end_date: End date for analysis
            attribution_model: Attribution model to use
            
        Returns:
            ROI calculation results
        """
        try:
            # Calculate total investment for period
            total_investment = await self._calculate_total_investment(start_date, end_date)
            
            # Calculate attributed revenue
            total_revenue = await self._calculate_attributed_revenue(
                start_date, end_date, attribution_model
            )
            
            # Calculate net profit
            net_profit = total_revenue - total_investment
            
            # Calculate ROI percentage
            roi_percentage = (net_profit / total_investment * 100) if total_investment > 0 else Decimal('0')
            
            # Calculate payback period
            payback_period_months = await self._calculate_payback_period(
                start_date, end_date, total_investment, total_revenue
            )
            
            # Calculate break-even point
            break_even_point = await self._calculate_break_even_point(
                start_date, total_investment
            )
            
            # Calculate revenue per dollar
            revenue_per_dollar = total_revenue / total_investment if total_investment > 0 else Decimal('0')
            
            # Calculate cost per acquisition
            cost_per_acquisition = await self._calculate_cost_per_acquisition(
                start_date, end_date, total_investment
            )
            
            # Calculate lifetime value ratio
            lifetime_value_ratio = await self._calculate_ltv_ratio(
                start_date, end_date, cost_per_acquisition
            )
            
            return ROIResults(
                total_investment=total_investment,
                total_revenue=total_revenue,
                net_profit=net_profit,
                roi_percentage=roi_percentage,
                payback_period_months=payback_period_months,
                break_even_point=break_even_point,
                revenue_per_dollar=revenue_per_dollar,
                cost_per_acquisition=cost_per_acquisition,
                lifetime_value_ratio=lifetime_value_ratio
            )
            
        except Exception as e:
            logger.error(f"Error calculating ROI: {str(e)}")
            raise
    
    async def _calculate_total_investment(self, start_date: datetime, end_date: datetime) -> Decimal:
        """Calculate total investment for period"""
        total = Decimal('0')
        
        for investment in self.investments:
            # Check if investment falls within period
            if start_date <= investment.date <= end_date:
                total += investment.amount
                
                # Handle recurring investments
                if investment.recurring and investment.duration_months > 1:
                    months_in_period = min(
                        investment.duration_months,
                        (end_date.year - investment.date.year) * 12 + 
                        (end_date.month - investment.date.month)
                    )
                    total += investment.amount * (months_in_period - 1)
        
        return total
    
    async def _calculate_attributed_revenue(self, 
                                          start_date: datetime,
                                          end_date: datetime,
                                          attribution_model: str) -> Decimal:
        """Calculate revenue attributed to SEO efforts"""
        # This would integrate with conversion tracking system
        # Placeholder implementation with realistic calculations
        
        # Get organic traffic data
        organic_sessions = await self._get_organic_sessions(start_date, end_date)
        
        # Get conversion rate
        conversion_rate = await self._get_conversion_rate(start_date, end_date)
        
        # Get average order value
        avg_order_value = await self._get_average_order_value(start_date, end_date)
        
        # Calculate attributed revenue
        conversions = organic_sessions * (conversion_rate / 100)
        revenue = Decimal(str(conversions)) * avg_order_value
        
        return revenue
    
    async def _calculate_payback_period(self, 
                                      start_date: datetime,
                                      end_date: datetime,
                                      investment: Decimal,
                                      revenue: Decimal) -> float:
        """Calculate payback period in months"""
        if revenue <= 0:
            return float('inf')
        
        period_months = (end_date.year - start_date.year) * 12 + (end_date.month - start_date.month)
        monthly_revenue = revenue / period_months if period_months > 0 else revenue
        
        if monthly_revenue <= 0:
            return float('inf')
        
        return float(investment / monthly_revenue)
    
    async def _calculate_break_even_point(self, start_date: datetime, investment: Decimal) -> datetime:
        """Calculate break-even point"""
        # Estimate monthly revenue growth
        monthly_revenue_growth = await self._estimate_monthly_revenue_growth()
        
        if monthly_revenue_growth <= 0:
            return start_date + timedelta(days=365 * 10)  # 10 years if no growth
        
        months_to_break_even = float(investment / Decimal(str(monthly_revenue_growth)))
        
        return start_date + timedelta(days=int(months_to_break_even * 30))
    
    async def _calculate_cost_per_acquisition(self, 
                                            start_date: datetime,
                                            end_date: datetime,
                                            investment: Decimal) -> Decimal:
        """Calculate cost per acquisition"""
        conversions = await self._get_total_conversions(start_date, end_date)
        
        if conversions <= 0:
            return Decimal('0')
        
        return investment / Decimal(str(conversions))
    
    async def _calculate_ltv_ratio(self, 
                                 start_date: datetime,
                                 end_date: datetime,
                                 cpa: Decimal) -> Decimal:
        """Calculate lifetime value to cost ratio"""
        avg_ltv = await self._get_average_customer_lifetime_value()
        
        if cpa <= 0:
            return Decimal('0')
        
        return avg_ltv / cpa
    
    async def calculate_roi_by_category(self, 
                                      start_date: datetime,
                                      end_date: datetime) -> Dict[InvestmentCategory, ROIResults]:
        """Calculate ROI by investment category"""
        roi_by_category = {}
        
        for category in InvestmentCategory:
            # Filter investments by category
            category_investments = [
                inv for inv in self.investments
                if inv.category == category and start_date <= inv.date <= end_date
            ]
            
            if not category_investments:
                continue
            
            # Calculate category-specific metrics
            category_investment = sum(inv.amount for inv in category_investments)
            category_revenue = await self._calculate_category_revenue(
                category, start_date, end_date
            )
            
            # Calculate ROI for category
            net_profit = category_revenue - category_investment
            roi_percentage = (net_profit / category_investment * 100) if category_investment > 0 else Decimal('0')
            
            roi_by_category[category] = ROIResults(
                total_investment=category_investment,
                total_revenue=category_revenue,
                net_profit=net_profit,
                roi_percentage=roi_percentage,
                payback_period_months=await self._calculate_payback_period(
                    start_date, end_date, category_investment, category_revenue
                ),
                break_even_point=await self._calculate_break_even_point(
                    start_date, category_investment
                ),
                revenue_per_dollar=category_revenue / category_investment if category_investment > 0 else Decimal('0'),
                cost_per_acquisition=await self._calculate_category_cpa(
                    category, start_date, end_date
                ),
                lifetime_value_ratio=Decimal('0')  # Would be calculated based on category-specific data
            )
        
        return roi_by_category
    
    async def _calculate_category_revenue(self, 
                                        category: InvestmentCategory,
                                        start_date: datetime,
                                        end_date: datetime) -> Decimal:
        """Calculate revenue attributed to specific investment category"""
        # Different categories would have different attribution methods
        total_revenue = await self._calculate_attributed_revenue(start_date, end_date, "last_click")
        
        # Apply category-specific attribution weights
        category_weights = {
            InvestmentCategory.CONTENT_CREATION: 0.4,
            InvestmentCategory.TECHNICAL_SEO: 0.25,
            InvestmentCategory.LINK_BUILDING: 0.2,
            InvestmentCategory.TOOLS_SOFTWARE: 0.05,
            InvestmentCategory.PERSONNEL: 0.05,
            InvestmentCategory.CONSULTING: 0.03,
            InvestmentCategory.PAID_PROMOTION: 0.02
        }
        
        weight = category_weights.get(category, 0.1)
        return total_revenue * Decimal(str(weight))
    
    async def _calculate_category_cpa(self, 
                                    category: InvestmentCategory,
                                    start_date: datetime,
                                    end_date: datetime) -> Decimal:
        """Calculate cost per acquisition for category"""
        category_investment = sum(
            inv.amount for inv in self.investments
            if inv.category == category and start_date <= inv.date <= end_date
        )
        
        # Estimate conversions attributed to category
        total_conversions = await self._get_total_conversions(start_date, end_date)
        
        # Apply category attribution
        category_weights = {
            InvestmentCategory.CONTENT_CREATION: 0.4,
            InvestmentCategory.TECHNICAL_SEO: 0.25,
            InvestmentCategory.LINK_BUILDING: 0.2,
            InvestmentCategory.TOOLS_SOFTWARE: 0.05,
            InvestmentCategory.PERSONNEL: 0.05,
            InvestmentCategory.CONSULTING: 0.03,
            InvestmentCategory.PAID_PROMOTION: 0.02
        }
        
        weight = category_weights.get(category, 0.1)
        category_conversions = total_conversions * weight
        
        if category_conversions <= 0:
            return Decimal('0')
        
        return category_investment / Decimal(str(category_conversions))
    
    async def forecast_roi(self, 
                         forecast_months: int,
                         investment_plan: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Forecast ROI based on planned investments
        
        Args:
            forecast_months: Number of months to forecast
            investment_plan: Planned investments
            
        Returns:
            ROI forecast data
        """
        try:
            # Historical data for trend analysis
            historical_roi = await self._get_historical_roi_trend()
            
            # Calculate monthly growth rates
            traffic_growth_rate = await self._calculate_traffic_growth_rate()
            conversion_growth_rate = await self._calculate_conversion_growth_rate()
            revenue_growth_rate = traffic_growth_rate * conversion_growth_rate
            
            forecast_data = {
                'forecast_months': forecast_months,
                'monthly_projections': [],
                'total_forecast': {},
                'confidence_intervals': {},
                'scenario_analysis': {}
            }
            
            current_date = datetime.now()
            cumulative_investment = Decimal('0')
            cumulative_revenue = Decimal('0')
            
            for month in range(forecast_months):
                month_date = current_date + timedelta(days=30 * month)
                
                # Calculate monthly investment
                monthly_investment = Decimal('0')
                for investment in investment_plan:
                    if month >= investment.get('start_month', 0) and month <= investment.get('end_month', forecast_months):
                        monthly_investment += Decimal(str(investment['amount']))
                
                # Calculate projected revenue
                base_monthly_revenue = await self._get_base_monthly_revenue()
                growth_factor = (1 + revenue_growth_rate) ** month
                projected_revenue = base_monthly_revenue * Decimal(str(growth_factor))
                
                cumulative_investment += monthly_investment
                cumulative_revenue += projected_revenue
                
                monthly_roi = ((projected_revenue - monthly_investment) / monthly_investment * 100) if monthly_investment > 0 else Decimal('0')
                cumulative_roi = ((cumulative_revenue - cumulative_investment) / cumulative_investment * 100) if cumulative_investment > 0 else Decimal('0')
                
                forecast_data['monthly_projections'].append({
                    'month': month + 1,
                    'date': month_date.isoformat(),
                    'investment': monthly_investment,
                    'revenue': projected_revenue,
                    'monthly_roi': monthly_roi,
                    'cumulative_investment': cumulative_investment,
                    'cumulative_revenue': cumulative_revenue,
                    'cumulative_roi': cumulative_roi
                })
            
            # Total forecast summary
            forecast_data['total_forecast'] = {
                'total_investment': cumulative_investment,
                'total_revenue': cumulative_revenue,
                'net_profit': cumulative_revenue - cumulative_investment,
                'roi_percentage': ((cumulative_revenue - cumulative_investment) / cumulative_investment * 100) if cumulative_investment > 0 else Decimal('0')
            }
            
            # Confidence intervals (Monte Carlo simulation would be used in production)
            forecast_data['confidence_intervals'] = {
                'roi_95_confidence': {
                    'lower_bound': float(forecast_data['total_forecast']['roi_percentage']) * 0.8,
                    'upper_bound': float(forecast_data['total_forecast']['roi_percentage']) * 1.2
                }
            }
            
            # Scenario analysis
            forecast_data['scenario_analysis'] = await self._generate_scenario_analysis(
                cumulative_investment, revenue_growth_rate, forecast_months
            )
            
            return forecast_data
            
        except Exception as e:
            logger.error(f"Error forecasting ROI: {str(e)}")
            return {}
    
    async def _generate_scenario_analysis(self, 
                                        investment: Decimal,
                                        base_growth_rate: float,
                                        months: int) -> Dict[str, Any]:
        """Generate scenario analysis for ROI forecasting"""
        scenarios = {
            'conservative': base_growth_rate * 0.7,
            'realistic': base_growth_rate,
            'optimistic': base_growth_rate * 1.3
        }
        
        scenario_results = {}
        base_revenue = await self._get_base_monthly_revenue()
        
        for scenario_name, growth_rate in scenarios.items():
            total_revenue = Decimal('0')
            
            for month in range(months):
                growth_factor = (1 + growth_rate) ** month
                monthly_revenue = base_revenue * Decimal(str(growth_factor))
                total_revenue += monthly_revenue
            
            roi = ((total_revenue - investment) / investment * 100) if investment > 0 else Decimal('0')
            
            scenario_results[scenario_name] = {
                'total_revenue': total_revenue,
                'roi_percentage': roi,
                'growth_rate': growth_rate
            }
        
        return scenario_results
    
    async def generate_roi_report(self, 
                                start_date: datetime,
                                end_date: datetime) -> SEOROIReport:
        """Generate comprehensive ROI report
        
        Args:
            start_date: Report start date
            end_date: Report end date
            
        Returns:
            Comprehensive ROI report
        """
        try:
            # Calculate overall ROI
            overall_roi = await self.calculate_roi(start_date, end_date)
            
            # Calculate ROI by category
            roi_by_category = await self.calculate_roi_by_category(start_date, end_date)
            
            # Calculate ROI by channel (would integrate with channel data)
            roi_by_channel = await self._calculate_roi_by_channel(start_date, end_date)
            
            # Trend analysis
            trend_analysis = await self._analyze_roi_trends(start_date, end_date)
            
            # Forecast ROI
            forecasted_roi = await self.forecast_roi(6, [])  # 6-month forecast
            
            # Compare with benchmarks
            benchmarks = await self._compare_with_benchmarks(overall_roi)
            
            # Generate recommendations
            recommendations = await self._generate_roi_recommendations(
                overall_roi, roi_by_category, benchmarks
            )
            
            return SEOROIReport(
                period_start=start_date,
                period_end=end_date,
                overall_roi=overall_roi,
                roi_by_category=roi_by_category,
                roi_by_channel=roi_by_channel,
                trend_analysis=trend_analysis,
                forecasted_roi=forecasted_roi,
                benchmarks=benchmarks,
                recommendations=recommendations
            )
            
        except Exception as e:
            logger.error(f"Error generating ROI report: {str(e)}")
            raise
    
    async def _calculate_roi_by_channel(self, 
                                      start_date: datetime,
                                      end_date: datetime) -> Dict[str, ROIResults]:
        """Calculate ROI by traffic channel"""
        # This would integrate with analytics data
        # Placeholder implementation
        channels = ['organic_search', 'direct', 'social', 'referral']
        roi_by_channel = {}
        
        total_roi = await self.calculate_roi(start_date, end_date)
        
        for channel in channels:
            # Distribute ROI by channel based on traffic share
            channel_share = 0.6 if channel == 'organic_search' else 0.133  # Organic gets 60%
            
            roi_by_channel[channel] = ROIResults(
                total_investment=total_roi.total_investment * Decimal(str(channel_share)),
                total_revenue=total_roi.total_revenue * Decimal(str(channel_share)),
                net_profit=total_roi.net_profit * Decimal(str(channel_share)),
                roi_percentage=total_roi.roi_percentage,  # Same percentage
                payback_period_months=total_roi.payback_period_months,
                break_even_point=total_roi.break_even_point,
                revenue_per_dollar=total_roi.revenue_per_dollar,
                cost_per_acquisition=total_roi.cost_per_acquisition,
                lifetime_value_ratio=total_roi.lifetime_value_ratio
            )
        
        return roi_by_channel
    
    async def _analyze_roi_trends(self, 
                                start_date: datetime,
                                end_date: datetime) -> Dict[str, List[float]]:
        """Analyze ROI trends over time"""
        # This would analyze historical ROI data
        # Placeholder implementation
        months = (end_date.year - start_date.year) * 12 + (end_date.month - start_date.month)
        
        return {
            'monthly_roi': [300 + (i * 10) + np.random.normal(0, 20) for i in range(months)],
            'investment_trend': [1000 + (i * 100) for i in range(months)],
            'revenue_trend': [4000 + (i * 500) for i in range(months)]
        }
    
    async def _compare_with_benchmarks(self, roi_results: ROIResults) -> Dict[str, float]:
        """Compare ROI with industry benchmarks"""
        return {
            'industry_average_roi': self.industry_benchmarks['content_marketing_roi'],
            'performance_vs_benchmark': float(roi_results.roi_percentage) / self.industry_benchmarks['content_marketing_roi'] * 100,
            'percentile_ranking': 75.0 if roi_results.roi_percentage > Decimal('300') else 50.0
        }
    
    async def _generate_roi_recommendations(self, 
                                          overall_roi: ROIResults,
                                          roi_by_category: Dict[InvestmentCategory, ROIResults],
                                          benchmarks: Dict[str, float]) -> List[str]:
        """Generate actionable ROI recommendations"""
        recommendations = []
        
        if overall_roi.roi_percentage < Decimal('200'):
            recommendations.append("Overall ROI below industry average - focus on high-performing categories")
        
        # Find best performing category
        if roi_by_category:
            best_category = max(roi_by_category.items(), key=lambda x: x[1].roi_percentage)
            recommendations.append(f"Increase investment in {best_category[0].value} - highest ROI category")
        
        if overall_roi.payback_period_months > 12:
            recommendations.append("Payback period too long - focus on quick-win SEO activities")
        
        return recommendations
    
    # Data fetching methods (would integrate with real data sources)
    async def _get_organic_sessions(self, start_date: datetime, end_date: datetime) -> int:
        """Get organic session count"""
        return 10000  # Placeholder
    
    async def _get_conversion_rate(self, start_date: datetime, end_date: datetime) -> float:
        """Get conversion rate"""
        return 2.5  # Placeholder
    
    async def _get_average_order_value(self, start_date: datetime, end_date: datetime) -> Decimal:
        """Get average order value"""
        return Decimal('150.00')  # Placeholder
    
    async def _estimate_monthly_revenue_growth(self) -> float:
        """Estimate monthly revenue growth"""
        return 5000.0  # Placeholder
    
    async def _get_total_conversions(self, start_date: datetime, end_date: datetime) -> int:
        """Get total conversions"""
        return 250  # Placeholder
    
    async def _get_average_customer_lifetime_value(self) -> Decimal:
        """Get average customer lifetime value"""
        return Decimal('1200.00')  # Placeholder
    
    async def _get_historical_roi_trend(self) -> List[float]:
        """Get historical ROI trend"""
        return [250, 280, 320, 350, 380]  # Placeholder
    
    async def _calculate_traffic_growth_rate(self) -> float:
        """Calculate traffic growth rate"""
        return 0.05  # 5% monthly growth
    
    async def _calculate_conversion_growth_rate(self) -> float:
        """Calculate conversion growth rate"""
        return 0.02  # 2% monthly growth
    
    async def _get_base_monthly_revenue(self) -> Decimal:
        """Get base monthly revenue"""
        return Decimal('25000.00')  # Placeholder
    
    async def _store_investment(self, investment: SEOInvestment):
        """Store investment to database"""
        logger.debug(f"Storing investment: {investment.investment_id}")
    
    def _generate_investment_id(self) -> str:
        """Generate unique investment ID"""
        import uuid
        return f"inv_{uuid.uuid4().hex[:8]}"


class ROIOptimizer:
    """Optimize SEO investments for maximum ROI"""
    
    def __init__(self, calculator: SEOROICalculator):
        self.calculator = calculator
    
    async def optimize_investment_allocation(self, 
                                           total_budget: Decimal,
                                           categories: List[InvestmentCategory]) -> Dict[str, Any]:
        """Optimize budget allocation across categories for maximum ROI
        
        Args:
            total_budget: Total budget to allocate
            categories: Categories to consider
            
        Returns:
            Optimized allocation recommendations
        """
        try:
            # Get historical ROI by category
            end_date = datetime.now()
            start_date = end_date - timedelta(days=365)
            
            historical_roi = await self.calculator.calculate_roi_by_category(start_date, end_date)
            
            # Calculate optimal allocation using weighted ROI
            total_weight = sum(
                float(roi.roi_percentage) for roi in historical_roi.values()
            )
            
            optimal_allocation = {}
            
            for category in categories:
                if category in historical_roi:
                    weight = float(historical_roi[category].roi_percentage) / total_weight
                    allocation = total_budget * Decimal(str(weight))
                    optimal_allocation[category.value] = {
                        'amount': allocation,
                        'percentage': weight * 100,
                        'expected_roi': historical_roi[category].roi_percentage
                    }
            
            return {
                'total_budget': total_budget,
                'optimal_allocation': optimal_allocation,
                'expected_total_roi': sum(
                    float(data['expected_roi']) * data['percentage'] / 100
                    for data in optimal_allocation.values()
                ),
                'risk_assessment': await self._assess_allocation_risk(optimal_allocation)
            }
            
        except Exception as e:
            logger.error(f"Error optimizing investment allocation: {str(e)}")
            return {}
    
    async def _assess_allocation_risk(self, allocation: Dict[str, Any]) -> Dict[str, str]:
        """Assess risk of investment allocation"""
        risk_levels = {}
        
        for category, data in allocation.items():
            if data['percentage'] > 50:
                risk_levels[category] = "HIGH - Over-concentration in single category"
            elif data['percentage'] > 30:
                risk_levels[category] = "MEDIUM - Significant allocation"
            else:
                risk_levels[category] = "LOW - Diversified allocation"
        
        return risk_levels