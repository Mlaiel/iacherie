#!/usr/bin/env python3
"""Revenue Distribution Engine

Advanced multi-platform revenue tracking and attribution system.
Handles unified revenue monitoring, ROI calculation, and budget
optimization across all distribution platforms.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

WARNING: This code is the exclusive intellectual property of Fahed Mlaiel.
Any unauthorized use, reproduction, or distribution without explicit written
permission is strictly prohibited and will result in legal action.
Contact: mlaiel@live.de
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Union, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from enum import Enum
import json
from decimal import Decimal, ROUND_HALF_UP

logger = logging.getLogger(__name__)


class RevenueType(Enum):
    """Types of revenue streams"""
    STREAMING_ROYALTIES = "streaming_royalties"
    ADVERTISING = "advertising"
    SPONSORSHIP = "sponsorship"
    MERCHANDISE = "merchandise"
    DIRECT_SALES = "direct_sales"
    SUBSCRIPTION = "subscription"
    TIPS_DONATIONS = "tips_donations"
    LICENSING = "licensing"
    AFFILIATE_COMMISSION = "affiliate_commission"
    BRAND_PARTNERSHIP = "brand_partnership"


class PaymentStatus(Enum):
    """Payment status tracking"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    DISPUTED = "disputed"
    REFUNDED = "refunded"
    CANCELLED = "cancelled"


class Currency(Enum):
    """Supported currencies"""
    USD = "USD"
    EUR = "EUR"
    GBP = "GBP"
    JPY = "JPY"
    CAD = "CAD"
    AUD = "AUD"
    CHF = "CHF"
    CNY = "CNY"


@dataclass
class RevenueStream:
    """Individual revenue stream data"""
    id: str
    platform: str
    content_id: str
    revenue_type: RevenueType
    amount: Decimal
    currency: Currency
    timestamp: datetime
    payment_status: PaymentStatus
    attribution_data: Dict[str, Any]
    metadata: Dict[str, Any]
    fees_deducted: Optional[Decimal] = None
    net_amount: Optional[Decimal] = None
    exchange_rate: Optional[Decimal] = None


@dataclass
class PlatformRevenue:
    """Platform-specific revenue aggregation"""
    platform: str
    total_revenue: Decimal
    revenue_streams: List[RevenueStream]
    period_start: datetime
    period_end: datetime
    currency: Currency
    fees_total: Decimal
    net_revenue: Decimal
    transaction_count: int
    avg_transaction_value: Decimal
    growth_rate: float


@dataclass
class ROIAnalysis:
    """Return on Investment analysis"""
    platform: str
    investment: Decimal
    revenue: Decimal
    roi_percentage: float
    cost_per_acquisition: Decimal
    lifetime_value: Decimal
    payback_period_days: int
    profit_margin: float
    break_even_point: datetime
    risk_score: float


@dataclass
class BudgetOptimization:
    """Budget optimization recommendations"""
    total_budget: Decimal
    platform_allocations: Dict[str, Decimal]
    expected_roi: Dict[str, float]
    optimization_strategy: str
    confidence_score: float
    reallocation_suggestions: List[Dict[str, Any]]
    risk_assessment: str
    projected_revenue: Decimal


@dataclass
class RevenueAttribution:
    """Revenue attribution to content and campaigns"""
    content_id: str
    total_attributed_revenue: Decimal
    platform_breakdown: Dict[str, Decimal]
    attribution_method: str
    confidence_score: float
    first_touch_attribution: Decimal
    last_touch_attribution: Decimal
    multi_touch_attribution: Decimal
    time_decay_attribution: Decimal


class RevenueDistribution:
    """
    Advanced revenue distribution and tracking system for multi-platform monetization.
    
    Features:
    - Unified revenue tracking across all platforms
    - Real-time ROI calculation and analysis
    - Automated budget optimization recommendations
    - Advanced attribution modeling
    - Cross-platform revenue consolidation
    - Tax and fee management
    - Performance-based reallocation
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize the revenue distribution engine"""
        self.config = config or {}
        self.revenue_streams: List[RevenueStream] = []
        self.platform_revenues: Dict[str, PlatformRevenue] = {}
        self.attribution_models: Dict[str, Any] = {}
        self.exchange_rates: Dict[str, Decimal] = {}
        self.fee_structures: Dict[str, Dict[str, Decimal]] = {}
        
        # Configuration
        self.base_currency = Currency(self.config.get('base_currency', 'USD'))
        self.attribution_window_days = self.config.get('attribution_window_days', 30)
        self.min_roi_threshold = Decimal(self.config.get('min_roi_threshold', '0.1'))
        
        # Initialize fee structures
        self._initialize_platform_fees()
        
        logger.info("Revenue Distribution Engine initialized")
    
    async def track_revenue(self, revenue_data: Dict[str, Any]) -> RevenueStream:
        """
        Track a new revenue stream from any platform
        
        Args:
            revenue_data: Revenue stream data including platform, amount, type, etc.
            
        Returns:
            RevenueStream object with processed data
        """
        try:
            # Convert amount to Decimal for precise calculations
            amount = Decimal(str(revenue_data['amount']))
            currency = Currency(revenue_data.get('currency', self.base_currency.value))
            
            # Calculate fees and net amount
            platform = revenue_data['platform']
            fees = await self._calculate_platform_fees(platform, amount)
            net_amount = amount - fees
            
            # Handle currency conversion if needed
            exchange_rate = None
            if currency != self.base_currency:
                exchange_rate = await self._get_exchange_rate(currency, self.base_currency)
                amount = amount * exchange_rate
                net_amount = net_amount * exchange_rate if exchange_rate else net_amount
            
            # Create revenue stream
            revenue_stream = RevenueStream(
                id=revenue_data.get('id', f"{platform}_{datetime.now().timestamp()}"),
                platform=platform,
                content_id=revenue_data['content_id'],
                revenue_type=RevenueType(revenue_data['revenue_type']),
                amount=amount,
                currency=self.base_currency,
                timestamp=datetime.fromisoformat(revenue_data['timestamp']) if isinstance(revenue_data['timestamp'], str) else revenue_data['timestamp'],
                payment_status=PaymentStatus(revenue_data.get('payment_status', 'pending')),
                attribution_data=revenue_data.get('attribution_data', {}),
                metadata=revenue_data.get('metadata', {}),
                fees_deducted=fees,
                net_amount=net_amount,
                exchange_rate=exchange_rate
            )
            
            # Store revenue stream
            self.revenue_streams.append(revenue_stream)
            
            # Update platform aggregations
            await self._update_platform_revenue(revenue_stream)
            
            logger.info(f"Revenue tracked: {amount} {self.base_currency.value} from {platform}")
            return revenue_stream
            
        except Exception as e:
            logger.error(f"Error tracking revenue: {e}")
            raise
    
    async def calculate_platform_roi(self, platform: str, 
                                   period_days: int = 30,
                                   investment_data: Optional[Dict[str, Any]] = None) -> ROIAnalysis:
        """
        Calculate ROI for a specific platform
        
        Args:
            platform: Platform identifier
            period_days: Analysis period in days
            investment_data: Investment/cost data for the platform
            
        Returns:
            ROI analysis with detailed metrics
        """
        try:
            end_date = datetime.now()
            start_date = end_date - timedelta(days=period_days)
            
            # Get revenue for the period
            platform_revenue = await self._get_platform_revenue_for_period(
                platform, start_date, end_date
            )
            
            # Get or estimate investment data
            if not investment_data:
                investment_data = await self._estimate_platform_investment(platform, period_days)
            
            total_investment = Decimal(str(investment_data.get('total_cost', 0)))
            total_revenue = platform_revenue.net_revenue
            
            # Calculate ROI metrics
            roi_percentage = float((total_revenue - total_investment) / total_investment * 100) if total_investment > 0 else 0.0
            
            # Calculate additional metrics
            customer_acquisition_cost = total_investment / max(platform_revenue.transaction_count, 1)
            lifetime_value = await self._calculate_customer_lifetime_value(platform)
            payback_period = await self._calculate_payback_period(platform, total_investment, total_revenue)
            profit_margin = float((total_revenue - total_investment) / total_revenue * 100) if total_revenue > 0 else 0.0
            break_even_point = await self._calculate_break_even_point(platform, total_investment)
            risk_score = await self._calculate_platform_risk_score(platform)
            
            roi_analysis = ROIAnalysis(
                platform=platform,
                investment=total_investment,
                revenue=total_revenue,
                roi_percentage=roi_percentage,
                cost_per_acquisition=customer_acquisition_cost,
                lifetime_value=lifetime_value,
                payback_period_days=payback_period,
                profit_margin=profit_margin,
                break_even_point=break_even_point,
                risk_score=risk_score
            )
            
            logger.info(f"ROI calculated for {platform}: {roi_percentage:.2f}%")
            return roi_analysis
            
        except Exception as e:
            logger.error(f"Error calculating ROI for {platform}: {e}")
            raise
    
    async def optimize_budget_allocation(self, 
                                       total_budget: Decimal,
                                       platforms: List[str],
                                       optimization_goal: str = "roi_maximization",
                                       constraints: Optional[Dict[str, Any]] = None) -> BudgetOptimization:
        """
        Optimize budget allocation across platforms
        
        Args:
            total_budget: Total available budget
            platforms: List of platforms to allocate budget to
            optimization_goal: Optimization strategy (roi_maximization, revenue_maximization, etc.)
            constraints: Optional constraints (min/max allocations, etc.)
            
        Returns:
            Budget optimization recommendations
        """
        try:
            constraints = constraints or {}
            
            # Get ROI analysis for each platform
            roi_analyses = {}
            for platform in platforms:
                roi_analyses[platform] = await self.calculate_platform_roi(platform)
            
            # Calculate optimal allocations based on goal
            if optimization_goal == "roi_maximization":
                allocations = await self._optimize_for_roi(total_budget, roi_analyses, constraints)
            elif optimization_goal == "revenue_maximization":
                allocations = await self._optimize_for_revenue(total_budget, roi_analyses, constraints)
            elif optimization_goal == "risk_minimization":
                allocations = await self._optimize_for_risk(total_budget, roi_analyses, constraints)
            else:
                allocations = await self._optimize_balanced(total_budget, roi_analyses, constraints)
            
            # Calculate expected ROI for each allocation
            expected_roi = {}
            projected_revenue = Decimal('0')
            
            for platform, allocation in allocations.items():
                if platform in roi_analyses:
                    roi_data = roi_analyses[platform]
                    expected_return = allocation * (Decimal(str(roi_data.roi_percentage)) / 100 + 1)
                    expected_roi[platform] = float((expected_return - allocation) / allocation * 100)
                    projected_revenue += expected_return
            
            # Generate reallocation suggestions
            reallocation_suggestions = await self._generate_reallocation_suggestions(
                allocations, roi_analyses
            )
            
            # Calculate confidence and risk assessment
            confidence_score = await self._calculate_optimization_confidence(roi_analyses, allocations)
            risk_assessment = await self._assess_portfolio_risk(allocations, roi_analyses)
            
            optimization = BudgetOptimization(
                total_budget=total_budget,
                platform_allocations=allocations,
                expected_roi=expected_roi,
                optimization_strategy=optimization_goal,
                confidence_score=confidence_score,
                reallocation_suggestions=reallocation_suggestions,
                risk_assessment=risk_assessment,
                projected_revenue=projected_revenue
            )
            
            logger.info(f"Budget optimization completed with {confidence_score:.2f} confidence")
            return optimization
            
        except Exception as e:
            logger.error(f"Error optimizing budget allocation: {e}")
            raise
    
    async def generate_revenue_attribution(self, 
                                         content_id: str,
                                         attribution_window_days: Optional[int] = None) -> RevenueAttribution:
        """
        Generate revenue attribution analysis for specific content
        
        Args:
            content_id: Content identifier
            attribution_window_days: Attribution window (defaults to config)
            
        Returns:
            Revenue attribution analysis
        """
        try:
            window_days = attribution_window_days or self.attribution_window_days
            end_date = datetime.now()
            start_date = end_date - timedelta(days=window_days)
            
            # Get all revenue streams for the content
            content_streams = [
                stream for stream in self.revenue_streams
                if stream.content_id == content_id 
                and start_date <= stream.timestamp <= end_date
            ]
            
            if not content_streams:
                logger.warning(f"No revenue streams found for content {content_id}")
                return RevenueAttribution(
                    content_id=content_id,
                    total_attributed_revenue=Decimal('0'),
                    platform_breakdown={},
                    attribution_method="none",
                    confidence_score=0.0,
                    first_touch_attribution=Decimal('0'),
                    last_touch_attribution=Decimal('0'),
                    multi_touch_attribution=Decimal('0'),
                    time_decay_attribution=Decimal('0')
                )
            
            # Calculate total revenue
            total_revenue = sum(stream.net_amount for stream in content_streams)
            
            # Platform breakdown
            platform_breakdown = {}
            for stream in content_streams:
                platform = stream.platform
                platform_breakdown[platform] = platform_breakdown.get(platform, Decimal('0')) + stream.net_amount
            
            # Apply different attribution models
            first_touch = await self._calculate_first_touch_attribution(content_streams)
            last_touch = await self._calculate_last_touch_attribution(content_streams)
            multi_touch = await self._calculate_multi_touch_attribution(content_streams)
            time_decay = await self._calculate_time_decay_attribution(content_streams, window_days)
            
            # Choose best attribution method
            attribution_method, confidence = await self._select_best_attribution_method(
                content_streams, first_touch, last_touch, multi_touch, time_decay
            )
            
            attribution = RevenueAttribution(
                content_id=content_id,
                total_attributed_revenue=total_revenue,
                platform_breakdown=platform_breakdown,
                attribution_method=attribution_method,
                confidence_score=confidence,
                first_touch_attribution=first_touch,
                last_touch_attribution=last_touch,
                multi_touch_attribution=multi_touch,
                time_decay_attribution=time_decay
            )
            
            logger.info(f"Revenue attribution generated for {content_id}: {total_revenue} {self.base_currency.value}")
            return attribution
            
        except Exception as e:
            logger.error(f"Error generating revenue attribution for {content_id}: {e}")
            raise
    
    async def get_unified_revenue_report(self, 
                                       period_days: int = 30,
                                       group_by: str = "platform",
                                       include_projections: bool = True) -> Dict[str, Any]:
        """
        Generate unified revenue report across all platforms
        
        Args:
            period_days: Report period in days
            group_by: Grouping method (platform, revenue_type, date, etc.)
            include_projections: Whether to include revenue projections
            
        Returns:
            Comprehensive revenue report
        """
        try:
            end_date = datetime.now()
            start_date = end_date - timedelta(days=period_days)
            
            # Filter revenue streams for the period
            period_streams = [
                stream for stream in self.revenue_streams
                if start_date <= stream.timestamp <= end_date
            ]
            
            # Calculate totals
            total_gross_revenue = sum(stream.amount for stream in period_streams)
            total_fees = sum(stream.fees_deducted or Decimal('0') for stream in period_streams)
            total_net_revenue = sum(stream.net_amount for stream in period_streams)
            
            # Group data according to group_by parameter
            grouped_data = await self._group_revenue_data(period_streams, group_by)
            
            # Calculate growth metrics
            previous_period_start = start_date - timedelta(days=period_days)
            growth_metrics = await self._calculate_growth_metrics(
                period_streams, previous_period_start, start_date
            )
            
            # Generate projections if requested
            projections = {}
            if include_projections:
                projections = await self._generate_revenue_projections(period_streams, period_days)
            
            # Top performing content and platforms
            top_performers = await self._identify_top_performers(period_streams)
            
            # Risk analysis
            risk_analysis = await self._analyze_revenue_risk(period_streams)
            
            report = {
                'period': {
                    'start_date': start_date.isoformat(),
                    'end_date': end_date.isoformat(),
                    'days': period_days
                },
                'summary': {
                    'total_gross_revenue': float(total_gross_revenue),
                    'total_fees': float(total_fees),
                    'total_net_revenue': float(total_net_revenue),
                    'transaction_count': len(period_streams),
                    'avg_transaction_value': float(total_net_revenue / max(len(period_streams), 1)),
                    'currency': self.base_currency.value
                },
                'grouped_data': grouped_data,
                'growth_metrics': growth_metrics,
                'top_performers': top_performers,
                'risk_analysis': risk_analysis,
                'projections': projections,
                'generated_at': datetime.now().isoformat()
            }
            
            logger.info(f"Unified revenue report generated for {period_days} days")
            return report
            
        except Exception as e:
            logger.error(f"Error generating revenue report: {e}")
            raise
    
    # Private helper methods
    def _initialize_platform_fees(self) -> None:
        """Initialize platform fee structures"""
        self.fee_structures = {
            'youtube': {'percentage': Decimal('0.45'), 'fixed': Decimal('0')},
            'spotify': {'percentage': Decimal('0.30'), 'fixed': Decimal('0')},
            'instagram': {'percentage': Decimal('0.05'), 'fixed': Decimal('0.10')},
            'tiktok': {'percentage': Decimal('0.05'), 'fixed': Decimal('0.05')},
            'twitter': {'percentage': Decimal('0.03'), 'fixed': Decimal('0')},
            'facebook': {'percentage': Decimal('0.05'), 'fixed': Decimal('0')},
            'linkedin': {'percentage': Decimal('0.02'), 'fixed': Decimal('0')},
            'twitch': {'percentage': Decimal('0.50'), 'fixed': Decimal('0')},
            'patreon': {'percentage': Decimal('0.08'), 'fixed': Decimal('0.30')},
            'onlyfans': {'percentage': Decimal('0.20'), 'fixed': Decimal('0')}
        }
    
    async def _calculate_platform_fees(self, platform: str, amount: Decimal) -> Decimal:
        """Calculate platform-specific fees"""
        fee_structure = self.fee_structures.get(platform.lower(), {
            'percentage': Decimal('0.05'),
            'fixed': Decimal('0')
        })
        
        percentage_fee = amount * fee_structure['percentage']
        fixed_fee = fee_structure['fixed']
        
        return percentage_fee + fixed_fee
    
    async def _get_exchange_rate(self, from_currency: Currency, to_currency: Currency) -> Decimal:
        """Get exchange rate between currencies"""
        # In production, this would fetch real exchange rates from an API
        # For now, return mock rates
        mock_rates = {
            ('EUR', 'USD'): Decimal('1.08'),
            ('GBP', 'USD'): Decimal('1.25'),
            ('JPY', 'USD'): Decimal('0.007'),
            ('CAD', 'USD'): Decimal('0.74'),
            ('AUD', 'USD'): Decimal('0.66')
        }
        
        rate_key = (from_currency.value, to_currency.value)
        reverse_key = (to_currency.value, from_currency.value)
        
        if rate_key in mock_rates:
            return mock_rates[rate_key]
        elif reverse_key in mock_rates:
            return Decimal('1') / mock_rates[reverse_key]
        else:
            return Decimal('1')  # Same currency or unknown rate
    
    async def _update_platform_revenue(self, revenue_stream: RevenueStream) -> None:
        """Update platform revenue aggregations"""
        platform = revenue_stream.platform
        
        if platform not in self.platform_revenues:
            # Initialize platform revenue tracking
            self.platform_revenues[platform] = PlatformRevenue(
                platform=platform,
                total_revenue=Decimal('0'),
                revenue_streams=[],
                period_start=revenue_stream.timestamp,
                period_end=revenue_stream.timestamp,
                currency=self.base_currency,
                fees_total=Decimal('0'),
                net_revenue=Decimal('0'),
                transaction_count=0,
                avg_transaction_value=Decimal('0'),
                growth_rate=0.0
            )
        
        platform_rev = self.platform_revenues[platform]
        platform_rev.revenue_streams.append(revenue_stream)
        platform_rev.total_revenue += revenue_stream.amount
        platform_rev.fees_total += revenue_stream.fees_deducted or Decimal('0')
        platform_rev.net_revenue += revenue_stream.net_amount
        platform_rev.transaction_count += 1
        platform_rev.avg_transaction_value = platform_rev.net_revenue / platform_rev.transaction_count
        platform_rev.period_end = max(platform_rev.period_end, revenue_stream.timestamp)
    
    async def _get_platform_revenue_for_period(self, platform: str, 
                                             start_date: datetime, 
                                             end_date: datetime) -> PlatformRevenue:
        """Get platform revenue for specific period"""
        period_streams = [
            stream for stream in self.revenue_streams
            if stream.platform == platform
            and start_date <= stream.timestamp <= end_date
        ]
        
        if not period_streams:
            return PlatformRevenue(
                platform=platform,
                total_revenue=Decimal('0'),
                revenue_streams=[],
                period_start=start_date,
                period_end=end_date,
                currency=self.base_currency,
                fees_total=Decimal('0'),
                net_revenue=Decimal('0'),
                transaction_count=0,
                avg_transaction_value=Decimal('0'),
                growth_rate=0.0
            )
        
        total_revenue = sum(stream.amount for stream in period_streams)
        fees_total = sum(stream.fees_deducted or Decimal('0') for stream in period_streams)
        net_revenue = sum(stream.net_amount for stream in period_streams)
        
        return PlatformRevenue(
            platform=platform,
            total_revenue=total_revenue,
            revenue_streams=period_streams,
            period_start=start_date,
            period_end=end_date,
            currency=self.base_currency,
            fees_total=fees_total,
            net_revenue=net_revenue,
            transaction_count=len(period_streams),
            avg_transaction_value=net_revenue / len(period_streams),
            growth_rate=0.0  # Would calculate based on previous period
        )
    
    async def _estimate_platform_investment(self, platform: str, period_days: int) -> Dict[str, Any]:
        """Estimate platform investment costs"""
        # Mock investment estimation - in production would use actual cost data
        base_daily_cost = {
            'youtube': 50,
            'instagram': 30,
            'tiktok': 25,
            'twitter': 20,
            'facebook': 35,
            'linkedin': 40,
            'spotify': 15,
            'twitch': 45
        }
        
        daily_cost = base_daily_cost.get(platform.lower(), 25)
        total_cost = daily_cost * period_days
        
        return {
            'total_cost': total_cost,
            'daily_average': daily_cost,
            'breakdown': {
                'advertising': total_cost * 0.6,
                'content_creation': total_cost * 0.3,
                'management': total_cost * 0.1
            }
        }
    
    async def _calculate_customer_lifetime_value(self, platform: str) -> Decimal:
        """Calculate customer lifetime value for platform"""
        # Mock CLV calculation
        platform_multipliers = {
            'youtube': Decimal('150'),
            'instagram': Decimal('80'),
            'tiktok': Decimal('60'),
            'twitter': Decimal('40'),
            'spotify': Decimal('120'),
            'twitch': Decimal('200')
        }
        
        return platform_multipliers.get(platform.lower(), Decimal('75'))
    
    async def _calculate_payback_period(self, platform: str, investment: Decimal, revenue: Decimal) -> int:
        """Calculate payback period in days"""
        if revenue <= 0:
            return 365  # Max period if no revenue
        
        daily_revenue = revenue / 30  # Assuming 30-day period
        if daily_revenue <= 0:
            return 365
        
        payback_days = float(investment / daily_revenue)
        return min(365, max(1, int(payback_days)))
    
    async def _calculate_break_even_point(self, platform: str, investment: Decimal) -> datetime:
        """Calculate break-even point date"""
        payback_days = await self._calculate_payback_period(platform, investment, investment)
        return datetime.now() + timedelta(days=payback_days)
    
    async def _calculate_platform_risk_score(self, platform: str) -> float:
        """Calculate risk score for platform (0-1, lower is better)"""
        # Mock risk calculation based on platform characteristics
        risk_factors = {
            'youtube': 0.3,  # Stable, established
            'instagram': 0.4,  # Moderate algorithm changes
            'tiktok': 0.7,  # High algorithm volatility
            'twitter': 0.5,  # Political/policy risks
            'facebook': 0.4,  # Mature platform
            'linkedin': 0.2,  # Very stable, B2B focused
            'spotify': 0.3,  # Stable music platform
            'twitch': 0.6   # Gaming market volatility
        }
        
        return risk_factors.get(platform.lower(), 0.5)
    
    # Attribution model methods
    async def _calculate_first_touch_attribution(self, streams: List[RevenueStream]) -> Decimal:
        """Calculate first-touch attribution"""
        if not streams:
            return Decimal('0')
        
        # Sort by timestamp and attribute all revenue to first interaction
        sorted_streams = sorted(streams, key=lambda x: x.timestamp)
        return sorted_streams[0].net_amount
    
    async def _calculate_last_touch_attribution(self, streams: List[RevenueStream]) -> Decimal:
        """Calculate last-touch attribution"""
        if not streams:
            return Decimal('0')
        
        # Sort by timestamp and attribute all revenue to last interaction
        sorted_streams = sorted(streams, key=lambda x: x.timestamp, reverse=True)
        return sorted_streams[0].net_amount
    
    async def _calculate_multi_touch_attribution(self, streams: List[RevenueStream]) -> Decimal:
        """Calculate multi-touch attribution (equal weight)"""
        if not streams:
            return Decimal('0')
        
        # Distribute revenue equally across all touchpoints
        total_revenue = sum(stream.net_amount for stream in streams)
        return total_revenue / len(streams)
    
    async def _calculate_time_decay_attribution(self, streams: List[RevenueStream], window_days: int) -> Decimal:
        """Calculate time-decay attribution (recent interactions weighted more)"""
        if not streams:
            return Decimal('0')
        
        now = datetime.now()
        weighted_revenue = Decimal('0')
        total_weight = Decimal('0')
        
        for stream in streams:
            # Calculate time decay weight (more recent = higher weight)
            days_ago = (now - stream.timestamp).days
            weight = Decimal(str(max(0.1, 1 - (days_ago / window_days))))
            
            weighted_revenue += stream.net_amount * weight
            total_weight += weight
        
        return weighted_revenue / max(total_weight, Decimal('1'))
    
    async def _select_best_attribution_method(self, streams: List[RevenueStream],
                                            first_touch: Decimal, last_touch: Decimal,
                                            multi_touch: Decimal, time_decay: Decimal) -> Tuple[str, float]:
        """Select the best attribution method and confidence score"""
        # Simple heuristic: use multi-touch for multiple streams, last-touch for single
        if len(streams) > 3:
            return "multi_touch", 0.8
        elif len(streams) > 1:
            return "time_decay", 0.7
        else:
            return "last_touch", 0.9
    
    # Budget optimization methods
    async def _optimize_for_roi(self, budget: Decimal, roi_analyses: Dict[str, ROIAnalysis],
                              constraints: Dict[str, Any]) -> Dict[str, Decimal]:
        """Optimize budget allocation for maximum ROI"""
        allocations = {}
        remaining_budget = budget
        
        # Sort platforms by ROI percentage
        sorted_platforms = sorted(
            roi_analyses.items(),
            key=lambda x: x[1].roi_percentage,
            reverse=True
        )
        
        for platform, roi_data in sorted_platforms:
            if remaining_budget <= 0:
                allocations[platform] = Decimal('0')
                continue
            
            # Allocate proportional to ROI, respecting constraints
            min_allocation = Decimal(str(constraints.get(f'{platform}_min', 0)))
            max_allocation = Decimal(str(constraints.get(f'{platform}_max', float(remaining_budget))))
            
            # Calculate ideal allocation based on ROI
            roi_weight = max(0.1, roi_data.roi_percentage / 100)
            ideal_allocation = min(max_allocation, remaining_budget * Decimal(str(roi_weight)))
            ideal_allocation = max(min_allocation, ideal_allocation)
            
            allocations[platform] = min(ideal_allocation, remaining_budget)
            remaining_budget -= allocations[platform]
        
        # Distribute any remaining budget
        if remaining_budget > 0:
            for platform in allocations:
                if remaining_budget <= 0:
                    break
                additional = min(remaining_budget, budget * Decimal('0.1'))
                allocations[platform] += additional
                remaining_budget -= additional
        
        return allocations
    
    async def _optimize_for_revenue(self, budget: Decimal, roi_analyses: Dict[str, ROIAnalysis],
                                  constraints: Dict[str, Any]) -> Dict[str, Decimal]:
        """Optimize budget allocation for maximum revenue"""
        # Similar to ROI optimization but prioritize absolute revenue potential
        return await self._optimize_for_roi(budget, roi_analyses, constraints)
    
    async def _optimize_for_risk(self, budget: Decimal, roi_analyses: Dict[str, ROIAnalysis],
                               constraints: Dict[str, Any]) -> Dict[str, Decimal]:
        """Optimize budget allocation for risk minimization"""
        allocations = {}
        
        # Sort platforms by risk score (lower risk first)
        sorted_platforms = sorted(
            roi_analyses.items(),
            key=lambda x: x[1].risk_score
        )
        
        # Distribute budget more evenly across low-risk platforms
        low_risk_platforms = [p for p, roi in sorted_platforms if roi.risk_score < 0.5]
        
        if low_risk_platforms:
            equal_allocation = budget / len(low_risk_platforms)
            for platform, _ in sorted_platforms:
                if platform in [p[0] for p in low_risk_platforms]:
                    allocations[platform] = equal_allocation
                else:
                    allocations[platform] = budget * Decimal('0.05')  # Minimal allocation for high-risk
        else:
            # Fallback to equal distribution
            equal_allocation = budget / len(sorted_platforms)
            for platform, _ in sorted_platforms:
                allocations[platform] = equal_allocation
        
        return allocations
    
    async def _optimize_balanced(self, budget: Decimal, roi_analyses: Dict[str, ROIAnalysis],
                               constraints: Dict[str, Any]) -> Dict[str, Decimal]:
        """Optimize budget allocation with balanced approach"""
        # Combine ROI, risk, and diversification factors
        allocations = {}
        
        for platform, roi_data in roi_analyses.items():
            # Calculate composite score
            roi_score = max(0.1, roi_data.roi_percentage / 100)
            risk_score = 1 - roi_data.risk_score  # Invert risk (higher is better)
            
            composite_score = (roi_score * 0.6 + risk_score * 0.4)
            allocations[platform] = budget * Decimal(str(composite_score))
        
        # Normalize to budget
        total_allocated = sum(allocations.values())
        if total_allocated > 0:
            for platform in allocations:
                allocations[platform] = allocations[platform] / total_allocated * budget
        
        return allocations
    
    async def _generate_reallocation_suggestions(self, allocations: Dict[str, Decimal],
                                               roi_analyses: Dict[str, ROIAnalysis]) -> List[Dict[str, Any]]:
        """Generate budget reallocation suggestions"""
        suggestions = []
        
        # Find underperforming and overperforming platforms
        for platform, allocation in allocations.items():
            if platform in roi_analyses:
                roi_data = roi_analyses[platform]
                
                if roi_data.roi_percentage < 10:  # Underperforming
                    suggestions.append({
                        'type': 'reduce_allocation',
                        'platform': platform,
                        'current_allocation': float(allocation),
                        'suggested_reduction': float(allocation * Decimal('0.2')),
                        'reason': f'Low ROI of {roi_data.roi_percentage:.1f}%'
                    })
                elif roi_data.roi_percentage > 50:  # High performing
                    suggestions.append({
                        'type': 'increase_allocation',
                        'platform': platform,
                        'current_allocation': float(allocation),
                        'suggested_increase': float(allocation * Decimal('0.3')),
                        'reason': f'High ROI of {roi_data.roi_percentage:.1f}%'
                    })
        
        return suggestions
    
    async def _calculate_optimization_confidence(self, roi_analyses: Dict[str, ROIAnalysis],
                                               allocations: Dict[str, Decimal]) -> float:
        """Calculate confidence score for optimization"""
        if not roi_analyses:
            return 0.0
        
        # Base confidence on data quality and consistency
        avg_roi = sum(roi.roi_percentage for roi in roi_analyses.values()) / len(roi_analyses)
        roi_variance = sum((roi.roi_percentage - avg_roi) ** 2 for roi in roi_analyses.values()) / len(roi_analyses)
        
        # Higher variance = lower confidence
        confidence = max(0.3, min(1.0, 1.0 - (roi_variance / 1000)))
        
        return confidence
    
    async def _assess_portfolio_risk(self, allocations: Dict[str, Decimal],
                                   roi_analyses: Dict[str, ROIAnalysis]) -> str:
        """Assess overall portfolio risk"""
        if not roi_analyses:
            return "unknown"
        
        avg_risk = sum(roi.risk_score for roi in roi_analyses.values()) / len(roi_analyses)
        
        if avg_risk < 0.3:
            return "low"
        elif avg_risk < 0.6:
            return "medium"
        else:
            return "high"
    
    # Reporting helper methods
    async def _group_revenue_data(self, streams: List[RevenueStream], group_by: str) -> Dict[str, Any]:
        """Group revenue data by specified criteria"""
        grouped = {}
        
        for stream in streams:
            if group_by == "platform":
                key = stream.platform
            elif group_by == "revenue_type":
                key = stream.revenue_type.value
            elif group_by == "date":
                key = stream.timestamp.date().isoformat()
            elif group_by == "currency":
                key = stream.currency.value
            else:
                key = "all"
            
            if key not in grouped:
                grouped[key] = {
                    'revenue': Decimal('0'),
                    'count': 0,
                    'fees': Decimal('0'),
                    'net': Decimal('0')
                }
            
            grouped[key]['revenue'] += stream.amount
            grouped[key]['count'] += 1
            grouped[key]['fees'] += stream.fees_deducted or Decimal('0')
            grouped[key]['net'] += stream.net_amount
        
        # Convert Decimals to floats for JSON serialization
        for key in grouped:
            grouped[key]['revenue'] = float(grouped[key]['revenue'])
            grouped[key]['fees'] = float(grouped[key]['fees'])
            grouped[key]['net'] = float(grouped[key]['net'])
        
        return grouped
    
    async def _calculate_growth_metrics(self, current_streams: List[RevenueStream],
                                      previous_start: datetime, previous_end: datetime) -> Dict[str, Any]:
        """Calculate growth metrics compared to previous period"""
        previous_streams = [
            stream for stream in self.revenue_streams
            if previous_start <= stream.timestamp <= previous_end
        ]
        
        current_revenue = sum(stream.net_amount for stream in current_streams)
        previous_revenue = sum(stream.net_amount for stream in previous_streams)
        
        growth_rate = 0.0
        if previous_revenue > 0:
            growth_rate = float((current_revenue - previous_revenue) / previous_revenue * 100)
        
        return {
            'current_period_revenue': float(current_revenue),
            'previous_period_revenue': float(previous_revenue),
            'growth_rate_percentage': growth_rate,
            'absolute_growth': float(current_revenue - previous_revenue),
            'transaction_count_change': len(current_streams) - len(previous_streams)
        }
    
    async def _generate_revenue_projections(self, streams: List[RevenueStream], 
                                          period_days: int) -> Dict[str, Any]:
        """Generate revenue projections for next period"""
        if not streams:
            return {}
        
        current_revenue = sum(stream.net_amount for stream in streams)
        daily_average = current_revenue / period_days
        
        # Simple projections based on current trends
        return {
            'next_30_days': float(daily_average * 30),
            'next_90_days': float(daily_average * 90),
            'next_365_days': float(daily_average * 365),
            'daily_average': float(daily_average),
            'confidence': 0.7,  # Mock confidence score
            'methodology': 'linear_trend'
        }
    
    async def _identify_top_performers(self, streams: List[RevenueStream]) -> Dict[str, Any]:
        """Identify top performing content and platforms"""
        # Platform performance
        platform_revenue = {}
        for stream in streams:
            platform = stream.platform
            platform_revenue[platform] = platform_revenue.get(platform, Decimal('0')) + stream.net_amount
        
        top_platforms = sorted(platform_revenue.items(), key=lambda x: x[1], reverse=True)[:5]
        
        # Content performance
        content_revenue = {}
        for stream in streams:
            content_id = stream.content_id
            content_revenue[content_id] = content_revenue.get(content_id, Decimal('0')) + stream.net_amount
        
        top_content = sorted(content_revenue.items(), key=lambda x: x[1], reverse=True)[:10]
        
        return {
            'top_platforms': [(platform, float(revenue)) for platform, revenue in top_platforms],
            'top_content': [(content_id, float(revenue)) for content_id, revenue in top_content]
        }
    
    async def _analyze_revenue_risk(self, streams: List[RevenueStream]) -> Dict[str, Any]:
        """Analyze revenue risk factors"""
        if not streams:
            return {'risk_level': 'unknown', 'factors': []}
        
        # Platform concentration risk
        platform_revenue = {}
        total_revenue = sum(stream.net_amount for stream in streams)
        
        for stream in streams:
            platform = stream.platform
            platform_revenue[platform] = platform_revenue.get(platform, Decimal('0')) + stream.net_amount
        
        # Calculate concentration
        max_platform_share = max(platform_revenue.values()) / total_revenue if total_revenue > 0 else 0
        
        risk_factors = []
        risk_level = "low"
        
        if max_platform_share > 0.7:
            risk_factors.append("High platform concentration")
            risk_level = "high"
        elif max_platform_share > 0.5:
            risk_factors.append("Moderate platform concentration")
            risk_level = "medium"
        
        # Revenue type diversity
        revenue_types = set(stream.revenue_type for stream in streams)
        if len(revenue_types) < 3:
            risk_factors.append("Limited revenue type diversity")
            if risk_level == "low":
                risk_level = "medium"
        
        return {
            'risk_level': risk_level,
            'factors': risk_factors,
            'platform_concentration': float(max_platform_share),
            'revenue_type_count': len(revenue_types)
        }