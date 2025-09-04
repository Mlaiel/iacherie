"""ROI Calculator - Advanced Return on Investment Analysis Engine
==============================================================

Comprehensive ROI calculation system for content creators and influencers,
providing multi-dimensional analysis of investments, returns, and optimization
strategies across all monetization channels.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️ STRICT COPYRIGHT WARNING - INTELLECTUAL PROPERTY PROTECTION
================================================================
This code and concept are the EXCLUSIVE PROPERTY of Fahed Mlaiel.
Unauthorized access, copying, modification, distribution, reverse engineering,
or commercialization without explicit written permission from Fahed Mlaiel
(mlaiel@live.de) is STRICTLY PROHIBITED and will result in immediate legal
action under German and International copyright laws.
"""

import asyncio
import logging
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union, Tuple
from dataclasses import dataclass, field
from enum import Enum
import statistics
from decimal import Decimal, ROUND_HALF_UP


# Configure logging
logger = logging.getLogger(__name__)


class InvestmentCategory(Enum):
    """Categories of investments for ROI calculation"""
    CONTENT_CREATION = "content_creation"
    EQUIPMENT = "equipment"
    MARKETING = "marketing"
    PLATFORM_FEES = "platform_fees"
    COLLABORATION = "collaboration"
    EDUCATION = "education"
    SOFTWARE_TOOLS = "software_tools"
    TIME_INVESTMENT = "time_investment"


class RevenueStream(Enum):
    """Types of revenue streams"""
    AD_REVENUE = "ad_revenue"
    SPONSORSHIPS = "sponsorships"
    AFFILIATE_MARKETING = "affiliate_marketing"
    MERCHANDISE = "merchandise"
    SUBSCRIPTIONS = "subscriptions"
    DONATIONS = "donations"
    COURSE_SALES = "course_sales"
    CONSULTING = "consulting"
    LICENSING = "licensing"


class ROITimeframe(Enum):
    """ROI calculation timeframes"""
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    YEARLY = "yearly"
    LIFETIME = "lifetime"


class ROIMetric(Enum):
    """ROI metrics and calculations"""
    BASIC_ROI = "basic_roi"
    ANNUALIZED_ROI = "annualized_roi"
    NET_PRESENT_VALUE = "net_present_value"
    INTERNAL_RATE_RETURN = "internal_rate_return"
    PAYBACK_PERIOD = "payback_period"
    RETURN_ON_AD_SPEND = "return_on_ad_spend"


@dataclass
class Investment:
    """Investment data structure"""
    investment_id: str
    category: InvestmentCategory
    amount: Decimal
    date: datetime
    description: str
    is_recurring: bool = False
    recurring_frequency: Optional[str] = None  # monthly, yearly, etc.
    depreciation_rate: Optional[float] = None
    expected_lifespan: Optional[timedelta] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Revenue:
    """Revenue data structure"""
    revenue_id: str
    stream: RevenueStream
    amount: Decimal
    date: datetime
    source: str
    is_recurring: bool = False
    recurring_frequency: Optional[str] = None
    related_content_id: Optional[str] = None
    commission_rate: Optional[float] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ROIAnalysisRequest:
    """ROI analysis request data structure"""
    analysis_id: str
    creator_id: str
    timeframe: ROITimeframe
    start_date: datetime
    end_date: datetime
    investments: List[Investment]
    revenues: List[Revenue]
    include_time_value: bool = True
    discount_rate: float = 0.05  # 5% default discount rate
    target_roi: Optional[float] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ROIResult:
    """ROI calculation result data structure"""
    analysis_id: str
    creator_id: str
    timeframe: ROITimeframe
    total_investment: Decimal
    total_revenue: Decimal
    net_profit: Decimal
    roi_percentage: float
    annualized_roi: float
    payback_period: Optional[timedelta]
    break_even_point: Optional[datetime]
    category_breakdown: Dict[str, Dict[str, Any]]
    revenue_breakdown: Dict[str, Dict[str, Any]]
    roi_metrics: Dict[ROIMetric, float]
    optimization_suggestions: List[str]
    performance_indicators: Dict[str, float]
    calculated_at: datetime
    metadata: Dict[str, Any] = field(default_factory=dict)


class ROICalculator:
    """
    Advanced ROI Calculator for Content Creators
    
    Provides comprehensive return on investment analysis including:
    - Multi-category investment tracking
    - Revenue stream analysis
    - Time value of money calculations
    - Optimization recommendations
    - Performance benchmarking
    """
    
    def __init__(self, 
                 default_discount_rate: float = 0.05,
                 currency: str = "USD"):
        """
        Initialize ROI Calculator
        
        Args:
            default_discount_rate: Default discount rate for NPV calculations
            currency: Currency for calculations
        """
        self.logger = logging.getLogger(self.__class__.__name__)
        self.default_discount_rate = default_discount_rate
        self.currency = currency
        
        # ROI benchmarks by industry/category
        self.roi_benchmarks = {
            InvestmentCategory.CONTENT_CREATION: {"good": 0.3, "excellent": 0.5},
            InvestmentCategory.EQUIPMENT: {"good": 0.2, "excellent": 0.4},
            InvestmentCategory.MARKETING: {"good": 0.4, "excellent": 0.8},
            InvestmentCategory.EDUCATION: {"good": 0.5, "excellent": 1.0},
            InvestmentCategory.SOFTWARE_TOOLS: {"good": 0.6, "excellent": 1.2},
        }
        
        # Revenue stream performance indicators
        self.revenue_benchmarks = {
            RevenueStream.AD_REVENUE: {"cpm": 2.0, "rpm": 1.5},
            RevenueStream.SPONSORSHIPS: {"rate_per_1k": 10.0, "conversion": 0.05},
            RevenueStream.AFFILIATE_MARKETING: {"conversion": 0.03, "commission": 0.05},
            RevenueStream.MERCHANDISE: {"margin": 0.4, "conversion": 0.02},
            RevenueStream.SUBSCRIPTIONS: {"churn": 0.05, "ltv_ratio": 12.0},
        }
        
        # Time investment hourly rates by activity
        self.time_value_rates = {
            "content_creation": 50.0,
            "editing": 40.0,
            "marketing": 35.0,
            "administration": 25.0,
            "research": 30.0,
            "collaboration": 45.0
        }
        
        self.logger.info("💰 ROI Calculator initialized")
    
    async def calculate_roi(self, request: ROIAnalysisRequest) -> ROIResult:
        """
        Calculate comprehensive ROI analysis
        
        Args:
            request: ROI analysis request with investments and revenues
            
        Returns:
            Detailed ROI analysis result
        """
        try:
            self.logger.info(f"🔢 Starting ROI calculation for {request.analysis_id}")
            
            # Calculate totals
            total_investment = await self._calculate_total_investment(request.investments, request.timeframe)
            total_revenue = await self._calculate_total_revenue(request.revenues, request.timeframe)
            net_profit = total_revenue - total_investment
            
            # Calculate basic ROI
            roi_percentage = await self._calculate_roi_percentage(total_investment, total_revenue)
            
            # Calculate annualized ROI
            annualized_roi = await self._calculate_annualized_roi(
                roi_percentage, request.start_date, request.end_date
            )
            
            # Calculate payback period
            payback_period = await self._calculate_payback_period(
                request.investments, request.revenues
            )
            
            # Calculate break-even point
            break_even_point = await self._calculate_break_even_point(
                request.investments, request.revenues, request.start_date
            )
            
            # Calculate category breakdown
            category_breakdown = await self._calculate_category_breakdown(
                request.investments, request.revenues
            )
            
            # Calculate revenue breakdown
            revenue_breakdown = await self._calculate_revenue_breakdown(request.revenues)
            
            # Calculate advanced ROI metrics
            roi_metrics = await self._calculate_advanced_metrics(request)
            
            # Generate optimization suggestions
            optimization_suggestions = await self._generate_optimization_suggestions(
                request, roi_percentage, category_breakdown, revenue_breakdown
            )
            
            # Calculate performance indicators
            performance_indicators = await self._calculate_performance_indicators(
                request, roi_percentage, annualized_roi
            )
            
            # Create result
            result = ROIResult(
                analysis_id=request.analysis_id,
                creator_id=request.creator_id,
                timeframe=request.timeframe,
                total_investment=total_investment,
                total_revenue=total_revenue,
                net_profit=net_profit,
                roi_percentage=roi_percentage,
                annualized_roi=annualized_roi,
                payback_period=payback_period,
                break_even_point=break_even_point,
                category_breakdown=category_breakdown,
                revenue_breakdown=revenue_breakdown,
                roi_metrics=roi_metrics,
                optimization_suggestions=optimization_suggestions,
                performance_indicators=performance_indicators,
                calculated_at=datetime.now(),
                metadata={
                    "currency": self.currency,
                    "discount_rate": request.discount_rate,
                    "period_days": (request.end_date - request.start_date).days,
                    "investment_count": len(request.investments),
                    "revenue_count": len(request.revenues)
                }
            )
            
            self.logger.info(
                f"✅ ROI calculation completed: {roi_percentage:.1%} ROI, "
                f"{self.currency} {net_profit:,.2f} net profit"
            )
            
            return result
            
        except Exception as e:
            self.logger.error(f"❌ ROI calculation failed for {request.analysis_id}: {str(e)}")
            raise
    
    async def batch_calculate_roi(self, requests: List[ROIAnalysisRequest]) -> List[ROIResult]:
        """
        Calculate ROI for multiple analysis requests
        
        Args:
            requests: List of ROI analysis requests
            
        Returns:
            List of ROI analysis results
        """
        try:
            self.logger.info(f"🔄 Processing batch ROI calculation for {len(requests)} analyses")
            
            # Process calculations concurrently
            tasks = [self.calculate_roi(request) for request in requests]
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Filter successful results
            successful_results = [
                result for result in results 
                if isinstance(result, ROIResult)
            ]
            
            self.logger.info(
                f"✅ Batch ROI calculation completed: {len(successful_results)}/{len(requests)} successful"
            )
            
            return successful_results
            
        except Exception as e:
            self.logger.error(f"❌ Batch ROI calculation failed: {str(e)}")
            raise
    
    async def compare_investments(self, 
                                investments: List[Investment],
                                revenues: List[Revenue]) -> Dict[str, Any]:
        """
        Compare ROI across different investment categories
        
        Args:
            investments: List of investments to compare
            revenues: Related revenues
            
        Returns:
            Investment comparison analysis
        """
        try:
            comparison = {}
            
            # Group investments by category
            category_groups = {}
            for investment in investments:
                category = investment.category.value
                if category not in category_groups:
                    category_groups[category] = []
                category_groups[category].append(investment)
            
            # Calculate ROI for each category
            for category, category_investments in category_groups.items():
                category_total = sum(inv.amount for inv in category_investments)
                
                # Allocate revenue proportionally (simplified)
                total_investment = sum(inv.amount for inv in investments)
                revenue_allocation = sum(rev.amount for rev in revenues) * (category_total / total_investment)
                
                category_roi = float((revenue_allocation - category_total) / category_total) if category_total > 0 else 0
                
                # Compare against benchmarks
                benchmark = self.roi_benchmarks.get(InvestmentCategory(category), {"good": 0.2, "excellent": 0.4})
                
                comparison[category] = {
                    "total_investment": float(category_total),
                    "allocated_revenue": float(revenue_allocation),
                    "roi_percentage": category_roi,
                    "benchmark_good": benchmark["good"],
                    "benchmark_excellent": benchmark["excellent"],
                    "performance_rating": self._rate_performance(category_roi, benchmark),
                    "investment_count": len(category_investments)
                }
            
            # Rank categories by ROI
            sorted_categories = sorted(
                comparison.items(), 
                key=lambda x: x[1]["roi_percentage"], 
                reverse=True
            )
            
            return {
                "category_comparison": comparison,
                "ranked_categories": [{"category": cat, **data} for cat, data in sorted_categories],
                "best_performing": sorted_categories[0][0] if sorted_categories else None,
                "worst_performing": sorted_categories[-1][0] if sorted_categories else None,
                "analysis_date": datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"❌ Investment comparison failed: {str(e)}")
            raise
    
    async def forecast_roi(self, 
                          historical_data: ROIResult,
                          forecast_months: int = 12) -> Dict[str, Any]:
        """
        Forecast future ROI based on historical performance
        
        Args:
            historical_data: Historical ROI analysis result
            forecast_months: Number of months to forecast
            
        Returns:
            ROI forecast analysis
        """
        try:
            # Calculate monthly trends
            monthly_investment = float(historical_data.total_investment) / 12  # Assuming annual data
            monthly_revenue = float(historical_data.total_revenue) / 12
            monthly_growth_rate = 0.05  # 5% monthly growth assumption
            
            forecast = []
            cumulative_investment = 0
            cumulative_revenue = 0
            
            for month in range(1, forecast_months + 1):
                # Apply growth rate
                projected_investment = monthly_investment * (1 + monthly_growth_rate) ** month
                projected_revenue = monthly_revenue * (1 + monthly_growth_rate * 1.2) ** month  # Revenue grows faster
                
                cumulative_investment += projected_investment
                cumulative_revenue += projected_revenue
                
                monthly_roi = (projected_revenue - projected_investment) / projected_investment if projected_investment > 0 else 0
                cumulative_roi = (cumulative_revenue - cumulative_investment) / cumulative_investment if cumulative_investment > 0 else 0
                
                forecast.append({
                    "month": month,
                    "projected_investment": round(projected_investment, 2),
                    "projected_revenue": round(projected_revenue, 2),
                    "monthly_roi": round(monthly_roi, 4),
                    "cumulative_investment": round(cumulative_investment, 2),
                    "cumulative_revenue": round(cumulative_revenue, 2),
                    "cumulative_roi": round(cumulative_roi, 4)
                })
            
            # Calculate forecast confidence
            confidence_score = min(0.95, 0.7 + (historical_data.roi_percentage * 0.5))
            
            return {
                "forecast_period_months": forecast_months,
                "monthly_forecast": forecast,
                "projected_total_investment": round(cumulative_investment, 2),
                "projected_total_revenue": round(cumulative_revenue, 2),
                "projected_final_roi": round(cumulative_roi, 4),
                "confidence_score": confidence_score,
                "assumptions": {
                    "monthly_growth_rate": monthly_growth_rate,
                    "revenue_acceleration": 1.2,
                    "market_conditions": "stable"
                },
                "forecast_date": datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"❌ ROI forecast failed: {str(e)}")
            raise
    
    async def _calculate_total_investment(self, 
                                        investments: List[Investment],
                                        timeframe: ROITimeframe) -> Decimal:
        """Calculate total investment amount"""
        total = Decimal('0')
        
        for investment in investments:
            amount = investment.amount
            
            # Handle recurring investments
            if investment.is_recurring:
                # Calculate number of recurrences in timeframe
                # This is a simplified calculation
                if investment.recurring_frequency == "monthly":
                    multiplier = 12 if timeframe == ROITimeframe.YEARLY else 1
                elif investment.recurring_frequency == "yearly":
                    multiplier = 1
                else:
                    multiplier = 1
                
                amount *= multiplier
            
            # Apply depreciation if applicable
            if investment.depreciation_rate and investment.expected_lifespan:
                # Simple straight-line depreciation
                depreciation_factor = 1 - investment.depreciation_rate
                amount *= Decimal(str(depreciation_factor))
            
            total += amount
        
        return total.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
    
    async def _calculate_total_revenue(self, 
                                     revenues: List[Revenue],
                                     timeframe: ROITimeframe) -> Decimal:
        """Calculate total revenue amount"""
        total = Decimal('0')
        
        for revenue in revenues:
            amount = revenue.amount
            
            # Handle recurring revenues
            if revenue.is_recurring:
                if revenue.recurring_frequency == "monthly":
                    multiplier = 12 if timeframe == ROITimeframe.YEARLY else 1
                elif revenue.recurring_frequency == "yearly":
                    multiplier = 1
                else:
                    multiplier = 1
                
                amount *= multiplier
            
            # Apply commission/fee deductions
            if revenue.commission_rate:
                amount *= Decimal(str(1 - revenue.commission_rate))
            
            total += amount
        
        return total.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
    
    async def _calculate_roi_percentage(self, 
                                      investment: Decimal,
                                      revenue: Decimal) -> float:
        """Calculate basic ROI percentage"""
        if investment == 0:
            return 0.0
        
        roi = float((revenue - investment) / investment)
        return round(roi, 4)
    
    async def _calculate_annualized_roi(self, 
                                      roi_percentage: float,
                                      start_date: datetime,
                                      end_date: datetime) -> float:
        """Calculate annualized ROI"""
        period_days = (end_date - start_date).days
        if period_days <= 0:
            return roi_percentage
        
        # Annualize the ROI
        years = period_days / 365.25
        annualized_roi = (1 + roi_percentage) ** (1 / years) - 1
        
        return round(annualized_roi, 4)
    
    async def _calculate_payback_period(self, 
                                      investments: List[Investment],
                                      revenues: List[Revenue]) -> Optional[timedelta]:
        """Calculate payback period"""
        try:
            # Sort by date
            sorted_investments = sorted(investments, key=lambda x: x.date)
            sorted_revenues = sorted(revenues, key=lambda x: x.date)
            
            cumulative_investment = Decimal('0')
            cumulative_revenue = Decimal('0')
            
            # Find break-even point
            for revenue in sorted_revenues:
                cumulative_revenue += revenue.amount
                
                # Add investments up to this revenue date
                for investment in sorted_investments:
                    if investment.date <= revenue.date:
                        cumulative_investment += investment.amount
                
                if cumulative_revenue >= cumulative_investment:
                    # Calculate payback period
                    first_investment_date = sorted_investments[0].date if sorted_investments else revenue.date
                    return revenue.date - first_investment_date
            
            return None  # Payback not achieved
            
        except Exception:
            return None
    
    async def _calculate_break_even_point(self, 
                                        investments: List[Investment],
                                        revenues: List[Revenue],
                                        start_date: datetime) -> Optional[datetime]:
        """Calculate break-even point date"""
        try:
            # Sort by date
            sorted_revenues = sorted(revenues, key=lambda x: x.date)
            total_investment = sum(inv.amount for inv in investments)
            
            cumulative_revenue = Decimal('0')
            
            for revenue in sorted_revenues:
                cumulative_revenue += revenue.amount
                if cumulative_revenue >= total_investment:
                    return revenue.date
            
            return None  # Break-even not achieved
            
        except Exception:
            return None
    
    async def _calculate_category_breakdown(self, 
                                          investments: List[Investment],
                                          revenues: List[Revenue]) -> Dict[str, Dict[str, Any]]:
        """Calculate investment breakdown by category"""
        breakdown = {}
        total_investment = sum(inv.amount for inv in investments)
        total_revenue = sum(rev.amount for rev in revenues)
        
        # Group by category
        category_groups = {}
        for investment in investments:
            category = investment.category.value
            if category not in category_groups:
                category_groups[category] = []
            category_groups[category].append(investment)
        
        for category, category_investments in category_groups.items():
            category_total = sum(inv.amount for inv in category_investments)
            category_percentage = float(category_total / total_investment) if total_investment > 0 else 0
            
            # Allocate revenue proportionally
            allocated_revenue = total_revenue * Decimal(str(category_percentage))
            category_roi = float((allocated_revenue - category_total) / category_total) if category_total > 0 else 0
            
            breakdown[category] = {
                "total_amount": float(category_total),
                "percentage_of_total": category_percentage,
                "allocated_revenue": float(allocated_revenue),
                "roi_percentage": category_roi,
                "investment_count": len(category_investments),
                "average_investment": float(category_total / len(category_investments))
            }
        
        return breakdown
    
    async def _calculate_revenue_breakdown(self, revenues: List[Revenue]) -> Dict[str, Dict[str, Any]]:
        """Calculate revenue breakdown by stream"""
        breakdown = {}
        total_revenue = sum(rev.amount for rev in revenues)
        
        # Group by revenue stream
        stream_groups = {}
        for revenue in revenues:
            stream = revenue.stream.value
            if stream not in stream_groups:
                stream_groups[stream] = []
            stream_groups[stream].append(revenue)
        
        for stream, stream_revenues in stream_groups.items():
            stream_total = sum(rev.amount for rev in stream_revenues)
            stream_percentage = float(stream_total / total_revenue) if total_revenue > 0 else 0
            
            breakdown[stream] = {
                "total_amount": float(stream_total),
                "percentage_of_total": stream_percentage,
                "revenue_count": len(stream_revenues),
                "average_revenue": float(stream_total / len(stream_revenues)),
                "is_recurring": any(rev.is_recurring for rev in stream_revenues)
            }
        
        return breakdown
    
    async def _calculate_advanced_metrics(self, request: ROIAnalysisRequest) -> Dict[ROIMetric, float]:
        """Calculate advanced ROI metrics"""
        metrics = {}
        
        total_investment = float(await self._calculate_total_investment(request.investments, request.timeframe))
        total_revenue = float(await self._calculate_total_revenue(request.revenues, request.timeframe))
        
        # Basic ROI
        metrics[ROIMetric.BASIC_ROI] = (total_revenue - total_investment) / total_investment if total_investment > 0 else 0
        
        # Annualized ROI
        period_years = (request.end_date - request.start_date).days / 365.25
        metrics[ROIMetric.ANNUALIZED_ROI] = (1 + metrics[ROIMetric.BASIC_ROI]) ** (1 / period_years) - 1 if period_years > 0 else 0
        
        # Net Present Value (simplified)
        discount_rate = request.discount_rate
        npv = total_revenue / (1 + discount_rate) ** period_years - total_investment
        metrics[ROIMetric.NET_PRESENT_VALUE] = npv
        
        # Return on Ad Spend (for marketing investments)
        marketing_investment = sum(
            float(inv.amount) for inv in request.investments 
            if inv.category == InvestmentCategory.MARKETING
        )
        if marketing_investment > 0:
            metrics[ROIMetric.RETURN_ON_AD_SPEND] = total_revenue / marketing_investment
        else:
            metrics[ROIMetric.RETURN_ON_AD_SPEND] = 0
        
        return metrics
    
    async def _generate_optimization_suggestions(self, 
                                               request: ROIAnalysisRequest,
                                               roi_percentage: float,
                                               category_breakdown: Dict[str, Dict[str, Any]],
                                               revenue_breakdown: Dict[str, Dict[str, Any]]) -> List[str]:
        """Generate ROI optimization suggestions"""
        suggestions = []
        
        # ROI performance analysis
        if roi_percentage < 0.2:  # Less than 20% ROI
            suggestions.append("Consider reallocating budget from underperforming investments")
            suggestions.append("Focus on higher-ROI activities and revenue streams")
        
        # Category-specific suggestions
        lowest_roi_category = min(
            category_breakdown.items(),
            key=lambda x: x[1]["roi_percentage"],
            default=(None, {"roi_percentage": 0})
        )
        
        if lowest_roi_category[0] and lowest_roi_category[1]["roi_percentage"] < 0.1:
            suggestions.append(f"Reduce investment in {lowest_roi_category[0]} or improve its efficiency")
        
        # Revenue stream optimization
        highest_revenue_stream = max(
            revenue_breakdown.items(),
            key=lambda x: x[1]["total_amount"],
            default=(None, {"total_amount": 0})
        )
        
        if highest_revenue_stream[0]:
            suggestions.append(f"Scale up {highest_revenue_stream[0]} as it's your top revenue stream")
        
        # Investment efficiency
        avg_investment_per_category = statistics.mean([
            cat_data["average_investment"] 
            for cat_data in category_breakdown.values()
        ])
        
        high_investment_categories = [
            category for category, data in category_breakdown.items()
            if data["average_investment"] > avg_investment_per_category * 1.5
        ]
        
        if high_investment_categories:
            suggestions.append(f"Review high-investment categories: {', '.join(high_investment_categories)}")
        
        # Time-based suggestions
        period_days = (request.end_date - request.start_date).days
        if period_days < 90:  # Less than 3 months
            suggestions.append("Consider longer analysis periods for more accurate ROI insights")
        
        # Diversification suggestions
        if len(revenue_breakdown) < 3:
            suggestions.append("Diversify revenue streams to reduce risk and increase stability")
        
        return suggestions[:5]  # Limit to top 5 suggestions
    
    async def _calculate_performance_indicators(self, 
                                              request: ROIAnalysisRequest,
                                              roi_percentage: float,
                                              annualized_roi: float) -> Dict[str, float]:
        """Calculate performance indicators"""
        indicators = {}
        
        # ROI performance rating (0-1 scale)
        indicators["roi_performance"] = min(max(roi_percentage / 0.5, 0), 1)  # 50% ROI = perfect score
        
        # Investment efficiency
        total_investment = float(await self._calculate_total_investment(request.investments, request.timeframe))
        total_revenue = float(await self._calculate_total_revenue(request.revenues, request.timeframe))
        indicators["investment_efficiency"] = total_revenue / total_investment if total_investment > 0 else 0
        
        # Revenue consistency (simplified)
        indicators["revenue_consistency"] = 0.8  # Placeholder - would calculate variance in actual implementation
        
        # Growth potential
        indicators["growth_potential"] = min(annualized_roi / 0.3, 1) if annualized_roi > 0 else 0
        
        # Risk score (inverse of diversification)
        revenue_streams = len(set(rev.stream for rev in request.revenues))
        indicators["risk_score"] = max(0, 1 - (revenue_streams / 5))  # Lower risk with more streams
        
        return indicators
    
    def _rate_performance(self, roi: float, benchmark: Dict[str, float]) -> str:
        """Rate performance against benchmarks"""
        if roi >= benchmark["excellent"]:
            return "excellent"
        elif roi >= benchmark["good"]:
            return "good"
        elif roi >= 0:
            return "fair"
        else:
            return "poor"


# Export main classes
__all__ = [
    "ROICalculator",
    "ROIAnalysisRequest", 
    "ROIResult",
    "Investment",
    "Revenue",
    "InvestmentCategory",
    "RevenueStream",
    "ROITimeframe",
    "ROIMetric"
]