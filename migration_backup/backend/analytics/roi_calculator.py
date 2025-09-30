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
import math
import random
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union, Tuple
from dataclasses import dataclass, field
from enum import Enum
import statistics
from decimal import Decimal, ROUND_HALF_UP
from collections import defaultdict


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
    
    # ========================================================================
    # ENTERPRISE ENHANCEMENTS - ADVANCED ROI ANALYSIS CAPABILITIES
    # ========================================================================
    
    async def analyze_roi_portfolio(
        self, 
        investment_portfolio: List[ROIAnalysisRequest]
    ) -> Dict[str, Any]:
        """
        Enterprise portfolio ROI analysis across multiple investments
        
        Args:
            investment_portfolio: List of ROI analysis requests
            
        Returns:
            Comprehensive portfolio analysis with optimization recommendations
        """
        try:
            portfolio_results = []
            
            # Analyze each investment in the portfolio
            for request in investment_portfolio:
                result = await self.calculate_roi(request)
                portfolio_results.append(result)
            
            # Calculate portfolio-level metrics
            portfolio_analysis = await self._calculate_portfolio_metrics(portfolio_results)
            
            # Identify optimization opportunities
            optimization_opportunities = await self._identify_portfolio_optimization_opportunities(
                investment_portfolio, portfolio_results
            )
            
            # Calculate risk-adjusted returns
            risk_adjusted_analysis = await self._calculate_risk_adjusted_returns(portfolio_results)
            
            # Generate rebalancing recommendations
            rebalancing_recommendations = await self._generate_portfolio_rebalancing_recommendations(
                investment_portfolio, portfolio_results
            )
            
            # Predict future performance
            performance_forecast = await self._forecast_portfolio_performance(portfolio_results)
            
            return {
                "portfolio_summary": portfolio_analysis,
                "individual_investments": portfolio_results,
                "optimization_opportunities": optimization_opportunities,
                "risk_adjusted_analysis": risk_adjusted_analysis,
                "rebalancing_recommendations": rebalancing_recommendations,
                "performance_forecast": performance_forecast,
                "portfolio_health_score": await self._calculate_portfolio_health_score(portfolio_results)
            }
            
        except Exception as e:
            logger.error(f"❌ Portfolio ROI analysis failed: {e}")
            return {"error": str(e)}
    
    async def _calculate_portfolio_metrics(self, results: List[ROIResult]) -> Dict[str, Any]:
        """Calculate comprehensive portfolio-level metrics"""
        if not results:
            return {}
        
        # Total portfolio value
        total_investment = sum(float(result.total_investment) for result in results)
        total_revenue = sum(float(result.total_revenue) for result in results)
        total_profit = total_revenue - total_investment
        
        # Portfolio ROI
        portfolio_roi = (total_profit / total_investment * 100) if total_investment > 0 else 0.0
        
        # Investment distribution
        investment_by_category = defaultdict(Decimal)
        for result in results:
            for investment in result.investments:
                investment_by_category[investment.category] += investment.amount
        
        # Revenue distribution
        revenue_by_stream = defaultdict(Decimal)
        for result in results:
            for revenue in result.revenues:
                revenue_by_stream[revenue.stream] += revenue.amount
        
        # Calculate portfolio diversity metrics
        diversity_score = await self._calculate_portfolio_diversity(results)
        
        # Risk metrics
        risk_metrics = await self._calculate_portfolio_risk_metrics(results)
        
        return {
            "total_investment": Decimal(str(total_investment)),
            "total_revenue": Decimal(str(total_revenue)),
            "total_profit": Decimal(str(total_profit)),
            "portfolio_roi": portfolio_roi,
            "investment_count": len(results),
            "investment_distribution": dict(investment_by_category),
            "revenue_distribution": dict(revenue_by_stream),
            "diversity_score": diversity_score,
            "risk_metrics": risk_metrics,
            "performance_consistency": statistics.stdev([result.roi_percentage for result in results]) if len(results) > 1 else 0.0
        }
    
    async def _identify_portfolio_optimization_opportunities(
        self,
        requests: List[ROIAnalysisRequest],
        results: List[ROIResult]
    ) -> List[Dict[str, Any]]:
        """Identify optimization opportunities in the portfolio"""
        opportunities = []
        
        # Identify underperforming investments
        roi_values = [result.roi_percentage for result in results]
        avg_roi = statistics.mean(roi_values) if roi_values else 0
        
        for i, result in enumerate(results):
            if result.roi_percentage < avg_roi * 0.7:  # 30% below average
                opportunities.append({
                    "type": "underperforming_investment",
                    "investment_id": requests[i].analysis_id,
                    "current_roi": result.roi_percentage,
                    "portfolio_average": avg_roi,
                    "recommendation": "Consider reallocating resources or improving strategy",
                    "potential_impact": (avg_roi - result.roi_percentage) * float(result.total_investment) / 100
                })
        
        # Identify overconcentration risks
        investment_distribution = defaultdict(Decimal)
        total_investment = sum(float(result.total_investment) for result in results)
        
        for result in results:
            for investment in result.investments:
                investment_distribution[investment.category] += investment.amount
        
        for category, amount in investment_distribution.items():
            concentration = float(amount) / total_investment if total_investment > 0 else 0
            
            if concentration > 0.5:  # More than 50% in one category
                opportunities.append({
                    "type": "overconcentration_risk",
                    "category": category.value,
                    "concentration": concentration,
                    "recommendation": "Diversify investments across more categories",
                    "risk_level": "high" if concentration > 0.7 else "medium"
                })
        
        # Identify timing optimization opportunities
        for i, request in enumerate(requests):
            if request.timeframe == ROITimeframe.SHORT_TERM:
                result = results[i]
                if result.roi_percentage > 0:
                    opportunities.append({
                        "type": "timing_optimization",
                        "investment_id": request.analysis_id,
                        "current_timeframe": request.timeframe.value,
                        "recommendation": "Consider extending timeframe for compound returns",
                        "estimated_improvement": result.roi_percentage * 0.3  # 30% improvement estimate
                    })
        
        return opportunities
    
    async def _calculate_risk_adjusted_returns(self, results: List[ROIResult]) -> Dict[str, Any]:
        """Calculate risk-adjusted return metrics"""
        if not results:
            return {}
        
        # Calculate return volatility (risk proxy)
        roi_values = [result.roi_percentage for result in results]
        
        if len(roi_values) > 1:
            volatility = statistics.stdev(roi_values)
            mean_return = statistics.mean(roi_values)
            
            # Sharpe ratio approximation (assuming risk-free rate of 2%)
            risk_free_rate = 2.0
            sharpe_ratio = (mean_return - risk_free_rate) / volatility if volatility > 0 else 0
            
            # Calculate maximum drawdown
            max_drawdown = await self._calculate_max_drawdown(roi_values)
            
            # Calculate Value at Risk (95% confidence)
            var_95 = await self._calculate_value_at_risk(roi_values, 0.95)
            
        else:
            volatility = 0.0
            sharpe_ratio = 0.0
            max_drawdown = 0.0
            var_95 = 0.0
        
        return {
            "portfolio_volatility": volatility,
            "sharpe_ratio": sharpe_ratio,
            "max_drawdown": max_drawdown,
            "value_at_risk_95": var_95,
            "risk_adjusted_return": statistics.mean(roi_values) / (volatility + 1) if roi_values else 0,
            "risk_level": self._categorize_risk_level(volatility)
        }
    
    async def _calculate_max_drawdown(self, returns: List[float]) -> float:
        """Calculate maximum drawdown from peak"""
        if not returns:
            return 0.0
        
        cumulative_returns = []
        cumulative = 1.0
        
        for return_val in returns:
            cumulative *= (1 + return_val / 100)
            cumulative_returns.append(cumulative)
        
        max_drawdown = 0.0
        peak = cumulative_returns[0]
        
        for value in cumulative_returns:
            if value > peak:
                peak = value
            
            drawdown = (peak - value) / peak
            max_drawdown = max(max_drawdown, drawdown)
        
        return max_drawdown * 100  # Return as percentage
    
    async def _calculate_value_at_risk(self, returns: List[float], confidence: float) -> float:
        """Calculate Value at Risk at given confidence level"""
        if not returns:
            return 0.0
        
        sorted_returns = sorted(returns)
        index = int((1 - confidence) * len(sorted_returns))
        
        return sorted_returns[index] if index < len(sorted_returns) else sorted_returns[-1]
    
    def _categorize_risk_level(self, volatility: float) -> str:
        """Categorize risk level based on volatility"""
        if volatility < 5:
            return "low"
        elif volatility < 15:
            return "medium"
        elif volatility < 25:
            return "high"
        else:
            return "very_high"
    
    async def _generate_portfolio_rebalancing_recommendations(
        self,
        requests: List[ROIAnalysisRequest],
        results: List[ROIResult]
    ) -> List[Dict[str, Any]]:
        """Generate portfolio rebalancing recommendations"""
        recommendations = []
        
        # Calculate current allocation
        total_investment = sum(float(result.total_investment) for result in results)
        
        # Analyze performance vs allocation
        performance_allocation = []
        for i, result in enumerate(results):
            allocation = float(result.total_investment) / total_investment if total_investment > 0 else 0
            performance_allocation.append({
                "investment_id": requests[i].analysis_id,
                "current_allocation": allocation,
                "roi": result.roi_percentage,
                "performance_score": result.roi_percentage * allocation
            })
        
        # Sort by performance score
        performance_allocation.sort(key=lambda x: x["performance_score"], reverse=True)
        
        # Generate rebalancing recommendations
        high_performers = [item for item in performance_allocation if item["roi"] > 20]  # ROI > 20%
        low_performers = [item for item in performance_allocation if item["roi"] < 5]   # ROI < 5%
        
        for high_performer in high_performers[:3]:  # Top 3 performers
            if high_performer["current_allocation"] < 0.4:  # Less than 40% allocation
                recommendations.append({
                    "type": "increase_allocation",
                    "investment_id": high_performer["investment_id"],
                    "current_allocation": high_performer["current_allocation"],
                    "recommended_allocation": min(0.4, high_performer["current_allocation"] + 0.1),
                    "reason": f"High ROI ({high_performer['roi']:.1f}%) justifies increased allocation",
                    "expected_impact": "positive"
                })
        
        for low_performer in low_performers:
            if low_performer["current_allocation"] > 0.1:  # More than 10% allocation
                recommendations.append({
                    "type": "decrease_allocation",
                    "investment_id": low_performer["investment_id"],
                    "current_allocation": low_performer["current_allocation"],
                    "recommended_allocation": max(0.05, low_performer["current_allocation"] - 0.1),
                    "reason": f"Low ROI ({low_performer['roi']:.1f}%) suggests reduced allocation",
                    "expected_impact": "risk_reduction"
                })
        
        return recommendations
    
    async def _forecast_portfolio_performance(self, results: List[ROIResult]) -> Dict[str, Any]:
        """Forecast future portfolio performance"""
        if not results:
            return {}
        
        # Calculate historical performance trends
        roi_values = [result.roi_percentage for result in results]
        
        # Simple trend analysis
        current_avg_roi = statistics.mean(roi_values)
        
        # Forecast scenarios
        forecasts = {
            "conservative": {
                "expected_roi": current_avg_roi * 0.8,  # 20% reduction
                "confidence": 0.8,
                "timeframe": "next_quarter"
            },
            "realistic": {
                "expected_roi": current_avg_roi,
                "confidence": 0.6,
                "timeframe": "next_quarter"
            },
            "optimistic": {
                "expected_roi": current_avg_roi * 1.2,  # 20% improvement
                "confidence": 0.4,
                "timeframe": "next_quarter"
            }
        }
        
        # Calculate compound growth potential
        compound_growth = {
            "1_year": current_avg_roi * 1.1,
            "2_years": current_avg_roi * 1.25,
            "5_years": current_avg_roi * 1.8
        }
        
        return {
            "scenarios": forecasts,
            "compound_growth_potential": compound_growth,
            "key_assumptions": [
                "Market conditions remain stable",
                "Investment strategies continue current approach",
                "No major external disruptions"
            ],
            "risk_factors": [
                "Market volatility",
                "Competition changes",
                "Technology disruption"
            ]
        }
    
    async def _calculate_portfolio_health_score(self, results: List[ROIResult]) -> Dict[str, Any]:
        """Calculate overall portfolio health score"""
        if not results:
            return {"score": 0, "grade": "F"}
        
        # Component scores (0-100)
        profitability_score = await self._calculate_profitability_score(results)
        diversity_score = await self._calculate_portfolio_diversity(results) * 100
        consistency_score = await self._calculate_consistency_score(results)
        growth_score = await self._calculate_growth_score(results)
        risk_score = await self._calculate_risk_score(results)
        
        # Weighted overall score
        weights = {
            "profitability": 0.3,
            "diversity": 0.2,
            "consistency": 0.2,
            "growth": 0.15,
            "risk": 0.15
        }
        
        overall_score = (
            profitability_score * weights["profitability"] +
            diversity_score * weights["diversity"] +
            consistency_score * weights["consistency"] +
            growth_score * weights["growth"] +
            risk_score * weights["risk"]
        )
        
        # Grade assignment
        if overall_score >= 90:
            grade = "A+"
        elif overall_score >= 85:
            grade = "A"
        elif overall_score >= 80:
            grade = "B+"
        elif overall_score >= 75:
            grade = "B"
        elif overall_score >= 70:
            grade = "C+"
        elif overall_score >= 65:
            grade = "C"
        elif overall_score >= 60:
            grade = "D"
        else:
            grade = "F"
        
        return {
            "overall_score": round(overall_score, 1),
            "grade": grade,
            "component_scores": {
                "profitability": round(profitability_score, 1),
                "diversity": round(diversity_score, 1),
                "consistency": round(consistency_score, 1),
                "growth": round(growth_score, 1),
                "risk_management": round(risk_score, 1)
            },
            "health_status": self._get_health_status(overall_score),
            "improvement_priorities": await self._get_improvement_priorities(
                profitability_score, diversity_score, consistency_score, growth_score, risk_score
            )
        }
    
    async def _calculate_profitability_score(self, results: List[ROIResult]) -> float:
        """Calculate profitability component score"""
        roi_values = [result.roi_percentage for result in results]
        avg_roi = statistics.mean(roi_values) if roi_values else 0
        
        # Score based on ROI performance
        if avg_roi >= 50:
            return 100
        elif avg_roi >= 30:
            return 85
        elif avg_roi >= 20:
            return 70
        elif avg_roi >= 10:
            return 55
        elif avg_roi >= 0:
            return 40
        else:
            return 20
    
    async def _calculate_portfolio_diversity(self, results: List[ROIResult]) -> float:
        """Calculate portfolio diversity score (0-1)"""
        if not results:
            return 0.0
        
        # Count different investment categories
        categories = set()
        revenue_streams = set()
        
        for result in results:
            for investment in result.investments:
                categories.add(investment.category)
            for revenue in result.revenues:
                revenue_streams.add(revenue.stream)
        
        # Calculate diversity based on category and stream distribution
        max_categories = len(InvestmentCategory)
        max_streams = len(RevenueStream)
        
        category_diversity = len(categories) / max_categories
        stream_diversity = len(revenue_streams) / max_streams
        
        return (category_diversity + stream_diversity) / 2
    
    async def _calculate_consistency_score(self, results: List[ROIResult]) -> float:
        """Calculate consistency component score"""
        roi_values = [result.roi_percentage for result in results]
        
        if len(roi_values) < 2:
            return 50  # Neutral score for single investment
        
        # Lower standard deviation = higher consistency
        std_dev = statistics.stdev(roi_values)
        
        # Score based on consistency (lower volatility = higher score)
        if std_dev < 5:
            return 100
        elif std_dev < 10:
            return 85
        elif std_dev < 15:
            return 70
        elif std_dev < 25:
            return 55
        else:
            return 30
    
    async def _calculate_growth_score(self, results: List[ROIResult]) -> float:
        """Calculate growth potential score"""
        # Simplified growth score based on average ROI
        roi_values = [result.roi_percentage for result in results]
        avg_roi = statistics.mean(roi_values) if roi_values else 0
        
        # Higher ROI indicates better growth potential
        return min(100, max(0, avg_roi * 2))  # Scale ROI to 0-100
    
    async def _calculate_risk_score(self, results: List[ROIResult]) -> float:
        """Calculate risk management score"""
        roi_values = [result.roi_percentage for result in results]
        
        if not roi_values:
            return 0
        
        # Count negative ROI investments (high risk)
        negative_roi_count = sum(1 for roi in roi_values if roi < 0)
        negative_ratio = negative_roi_count / len(roi_values)
        
        # Score based on risk exposure
        if negative_ratio == 0:
            return 100
        elif negative_ratio <= 0.1:
            return 85
        elif negative_ratio <= 0.2:
            return 70
        elif negative_ratio <= 0.3:
            return 55
        else:
            return 30
    
    def _get_health_status(self, score: float) -> str:
        """Get health status description"""
        if score >= 85:
            return "Excellent"
        elif score >= 75:
            return "Good"
        elif score >= 65:
            return "Fair"
        elif score >= 50:
            return "Poor"
        else:
            return "Critical"
    
    async def _get_improvement_priorities(
        self, 
        profitability: float, 
        diversity: float, 
        consistency: float, 
        growth: float, 
        risk: float
    ) -> List[str]:
        """Identify improvement priorities based on component scores"""
        priorities = []
        
        scores = {
            "profitability": profitability,
            "diversity": diversity,
            "consistency": consistency,
            "growth": growth,
            "risk_management": risk
        }
        
        # Sort by score (lowest first)
        sorted_scores = sorted(scores.items(), key=lambda x: x[1])
        
        for component, score in sorted_scores[:3]:  # Top 3 improvement areas
            if score < 70:  # Only include areas that need improvement
                if component == "profitability":
                    priorities.append("Focus on higher-ROI investment opportunities")
                elif component == "diversity":
                    priorities.append("Diversify across more investment categories and revenue streams")
                elif component == "consistency":
                    priorities.append("Reduce portfolio volatility through better risk management")
                elif component == "growth":
                    priorities.append("Identify and invest in higher-growth opportunities")
                elif component == "risk_management":
                    priorities.append("Improve risk assessment and mitigation strategies")
        
        return priorities
    
    async def predict_roi_trends(
        self, 
        historical_data: List[ROIResult], 
        prediction_periods: int = 12
    ) -> Dict[str, Any]:
        """
        Predict ROI trends using historical data
        
        Args:
            historical_data: Historical ROI results
            prediction_periods: Number of periods to predict
            
        Returns:
            ROI trend predictions and analysis
        """
        try:
            if not historical_data:
                return {"error": "No historical data provided"}
            
            # Extract time series data
            roi_values = [result.roi_percentage for result in historical_data]
            
            # Simple trend analysis (in production would use advanced time series models)
            trend_predictions = await self._calculate_trend_predictions(roi_values, prediction_periods)
            
            # Seasonal analysis
            seasonal_patterns = await self._analyze_seasonal_patterns(roi_values)
            
            # Confidence intervals
            confidence_intervals = await self._calculate_prediction_confidence_intervals(
                roi_values, trend_predictions
            )
            
            # Risk scenarios
            risk_scenarios = await self._generate_risk_scenarios(roi_values, trend_predictions)
            
            return {
                "trend_predictions": trend_predictions,
                "seasonal_patterns": seasonal_patterns,
                "confidence_intervals": confidence_intervals,
                "risk_scenarios": risk_scenarios,
                "trend_analysis": {
                    "overall_trend": self._determine_overall_trend(roi_values),
                    "trend_strength": self._calculate_trend_strength(roi_values),
                    "volatility_forecast": self._forecast_volatility(roi_values)
                },
                "recommendations": await self._generate_trend_based_recommendations(trend_predictions)
            }
            
        except Exception as e:
            logger.error(f"❌ ROI trend prediction failed: {e}")
            return {"error": str(e)}
    
    async def _calculate_trend_predictions(
        self, 
        roi_values: List[float], 
        periods: int
    ) -> List[Dict[str, float]]:
        """Calculate simple trend predictions"""
        if len(roi_values) < 2:
            return []
        
        # Simple linear trend calculation
        x_values = list(range(len(roi_values)))
        
        # Calculate slope and intercept
        n = len(roi_values)
        sum_x = sum(x_values)
        sum_y = sum(roi_values)
        sum_xy = sum(x * y for x, y in zip(x_values, roi_values))
        sum_x2 = sum(x * x for x in x_values)
        
        slope = (n * sum_xy - sum_x * sum_y) / (n * sum_x2 - sum_x * sum_x)
        intercept = (sum_y - slope * sum_x) / n
        
        # Generate predictions
        predictions = []
        for i in range(periods):
            period_index = len(roi_values) + i
            predicted_value = slope * period_index + intercept
            
            # Add some noise for realism
            noise = random.uniform(-2, 2)
            predicted_value += noise
            
            predictions.append({
                "period": i + 1,
                "predicted_roi": round(predicted_value, 2),
                "trend_component": round(slope * period_index + intercept, 2),
                "confidence": max(0.3, 0.9 - (i * 0.05))  # Decreasing confidence
            })
        
        return predictions
    
    async def _analyze_seasonal_patterns(self, roi_values: List[float]) -> Dict[str, Any]:
        """Analyze seasonal patterns in ROI data"""
        # Simplified seasonal analysis
        if len(roi_values) < 12:
            return {"error": "Insufficient data for seasonal analysis"}
        
        # Assume monthly data and calculate quarterly averages
        quarterly_data = []
        for i in range(0, len(roi_values), 3):
            quarter_values = roi_values[i:i+3]
            if quarter_values:
                quarterly_data.append(statistics.mean(quarter_values))
        
        # Identify seasonal patterns
        if len(quarterly_data) >= 4:
            q1_avg = statistics.mean([quarterly_data[i] for i in range(0, len(quarterly_data), 4)])
            q2_avg = statistics.mean([quarterly_data[i] for i in range(1, len(quarterly_data), 4)])
            q3_avg = statistics.mean([quarterly_data[i] for i in range(2, len(quarterly_data), 4)])
            q4_avg = statistics.mean([quarterly_data[i] for i in range(3, len(quarterly_data), 4)])
            
            return {
                "quarterly_patterns": {
                    "Q1": round(q1_avg, 2),
                    "Q2": round(q2_avg, 2),
                    "Q3": round(q3_avg, 2),
                    "Q4": round(q4_avg, 2)
                },
                "best_quarter": max(
                    [("Q1", q1_avg), ("Q2", q2_avg), ("Q3", q3_avg), ("Q4", q4_avg)],
                    key=lambda x: x[1]
                )[0],
                "seasonality_strength": statistics.stdev([q1_avg, q2_avg, q3_avg, q4_avg])
            }
        
        return {"seasonal_patterns": "Insufficient data for seasonal analysis"}
    
    async def _calculate_prediction_confidence_intervals(
        self,
        historical_values: List[float],
        predictions: List[Dict[str, float]]
    ) -> List[Dict[str, float]]:
        """Calculate confidence intervals for predictions"""
        if not historical_values or not predictions:
            return []
        
        # Calculate historical volatility
        historical_std = statistics.stdev(historical_values) if len(historical_values) > 1 else 5.0
        
        confidence_intervals = []
        for prediction in predictions:
            predicted_roi = prediction["predicted_roi"]
            confidence = prediction["confidence"]
            
            # Confidence interval width increases with prediction horizon
            interval_width = historical_std * (2 - confidence)
            
            confidence_intervals.append({
                "period": prediction["period"],
                "lower_bound": round(predicted_roi - interval_width, 2),
                "upper_bound": round(predicted_roi + interval_width, 2),
                "confidence_level": round(confidence * 100, 1)
            })
        
        return confidence_intervals
    
    async def _generate_risk_scenarios(
        self,
        historical_values: List[float],
        predictions: List[Dict[str, float]]
    ) -> Dict[str, List[float]]:
        """Generate risk scenario predictions"""
        if not predictions:
            return {}
        
        base_predictions = [p["predicted_roi"] for p in predictions]
        
        scenarios = {
            "bull_case": [roi * 1.3 for roi in base_predictions],  # 30% better
            "bear_case": [roi * 0.6 for roi in base_predictions],  # 40% worse
            "stress_case": [roi * 0.3 for roi in base_predictions]  # 70% worse
        }
        
        return scenarios
    
    def _determine_overall_trend(self, roi_values: List[float]) -> str:
        """Determine overall trend direction"""
        if len(roi_values) < 2:
            return "insufficient_data"
        
        recent_avg = statistics.mean(roi_values[-3:]) if len(roi_values) >= 3 else roi_values[-1]
        earlier_avg = statistics.mean(roi_values[:3]) if len(roi_values) >= 6 else roi_values[0]
        
        if recent_avg > earlier_avg * 1.1:
            return "upward"
        elif recent_avg < earlier_avg * 0.9:
            return "downward"
        else:
            return "stable"
    
    def _calculate_trend_strength(self, roi_values: List[float]) -> float:
        """Calculate strength of the trend (0-1)"""
        if len(roi_values) < 3:
            return 0.0
        
        # Calculate correlation with time
        x_values = list(range(len(roi_values)))
        
        # Simple correlation calculation
        n = len(roi_values)
        sum_x = sum(x_values)
        sum_y = sum(roi_values)
        sum_xy = sum(x * y for x, y in zip(x_values, roi_values))
        sum_x2 = sum(x * x for x in x_values)
        sum_y2 = sum(y * y for y in roi_values)
        
        numerator = n * sum_xy - sum_x * sum_y
        denominator = math.sqrt((n * sum_x2 - sum_x * sum_x) * (n * sum_y2 - sum_y * sum_y))
        
        if denominator == 0:
            return 0.0
        
        correlation = abs(numerator / denominator)
        return min(1.0, correlation)
    
    def _forecast_volatility(self, roi_values: List[float]) -> float:
        """Forecast future volatility based on historical data"""
        if len(roi_values) < 2:
            return 0.0
        
        return statistics.stdev(roi_values)
    
    async def _generate_trend_based_recommendations(
        self, 
        predictions: List[Dict[str, float]]
    ) -> List[str]:
        """Generate recommendations based on trend predictions"""
        if not predictions:
            return []
        
        recommendations = []
        
        # Analyze prediction trend
        pred_values = [p["predicted_roi"] for p in predictions]
        
        if statistics.mean(pred_values) > 15:  # Strong positive trend
            recommendations.append("Strong positive trend predicted - consider increasing investment")
        elif statistics.mean(pred_values) < 5:  # Weak performance
            recommendations.append("Weak performance predicted - review and optimize strategy")
        
        # Analyze volatility
        if len(pred_values) > 1 and statistics.stdev(pred_values) > 10:
            recommendations.append("High volatility predicted - implement risk management measures")
        
        # Analyze confidence
        avg_confidence = statistics.mean([p["confidence"] for p in predictions])
        if avg_confidence < 0.6:
            recommendations.append("Low prediction confidence - gather more data and monitor closely")
        
        return recommendations


# Export main classes with enhanced capabilities
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

# Module enhancement notification
logger.info("💰 ROI Calculator Engine - Enterprise enhancements loaded")
logger.info("✨ Features: Portfolio analysis, risk assessment, trend prediction, optimization")
logger.info("🚀 Performance: Advanced financial analytics, multi-dimensional ROI analysis, predictive modeling")