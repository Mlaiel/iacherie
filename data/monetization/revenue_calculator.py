"""Revenue Calculator Engine
=========================

Advanced revenue calculation engine for content creators.
Provides multi-platform revenue calculations, commission management,
royalty distribution, tax calculations, and currency conversion.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel - All Rights Reserved

WARNING: Unauthorized use, copying, or distribution of this code is strictly 
prohibited and subject to legal action under German and international copyright law.
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, field
from enum import Enum
from decimal import Decimal, ROUND_HALF_UP
import uuid
import json

from sqlalchemy.ext.asyncio import AsyncSession
from redis import Redis

# Import from enterprise revenue intelligence for shared types
from .enterprise_revenue_intelligence_engine import (
    PlatformType, RevenueType, Currency, RevenueMetrics, RevenueProjection
)


class CalculationType(Enum):
    """Revenue calculation types"""
    GROSS_REVENUE = "gross_revenue"
    NET_REVENUE = "net_revenue"
    COMMISSION = "commission"
    ROYALTY = "royalty"
    TAX = "tax"
    FEE = "fee"
    BONUS = "bonus"
    PENALTY = "penalty"


class CommissionType(Enum):
    """Commission calculation types"""
    PERCENTAGE = "percentage"
    FIXED = "fixed"
    TIERED = "tiered"
    PERFORMANCE_BASED = "performance_based"
    HYBRID = "hybrid"


class TaxCategory(Enum):
    """Tax categories"""
    INCOME_TAX = "income_tax"
    VAT = "vat"
    SALES_TAX = "sales_tax"
    WITHHOLDING_TAX = "withholding_tax"
    SOCIAL_SECURITY = "social_security"
    SELF_EMPLOYMENT = "self_employment"


@dataclass
class RevenueCalculationRequest:
    """Revenue calculation request"""
    request_id: str
    user_id: str
    platform: PlatformType
    revenue_type: RevenueType
    base_amount: Decimal
    currency: Currency
    period_start: datetime
    period_end: datetime
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class CommissionRule:
    """Commission calculation rule"""
    rule_id: str
    commission_type: CommissionType
    rate: Decimal  # Percentage or fixed amount
    tier_thresholds: List[Decimal] = field(default_factory=list)
    tier_rates: List[Decimal] = field(default_factory=list)
    minimum_amount: Decimal = Decimal('0')
    maximum_amount: Optional[Decimal] = None
    conditions: Dict[str, Any] = field(default_factory=dict)


@dataclass
class RoyaltyRule:
    """Royalty calculation rule"""
    rule_id: str
    royalty_rate: Decimal
    base_amount_type: str  # "revenue", "sales", "usage"
    minimum_royalty: Decimal = Decimal('0')
    maximum_royalty: Optional[Decimal] = None
    escalation_schedule: List[Dict[str, Any]] = field(default_factory=list)
    territory_rates: Dict[str, Decimal] = field(default_factory=dict)


@dataclass
class TaxRule:
    """Tax calculation rule"""
    rule_id: str
    tax_category: TaxCategory
    tax_rate: Decimal
    jurisdiction: str
    exemption_threshold: Decimal = Decimal('0')
    deduction_types: List[str] = field(default_factory=list)
    filing_frequency: str = "annual"
    compliance_requirements: List[str] = field(default_factory=list)


@dataclass
class CurrencyRate:
    """Currency exchange rate"""
    from_currency: Currency
    to_currency: Currency
    rate: Decimal
    timestamp: datetime
    source: str = "market"
    spread: Decimal = Decimal('0')


@dataclass
class RevenueCalculationResult:
    """Revenue calculation result"""
    calculation_id: str
    request_id: str
    gross_revenue: Decimal
    commissions: Dict[str, Decimal]
    royalties: Dict[str, Decimal]
    taxes: Dict[str, Decimal]
    fees: Dict[str, Decimal]
    net_revenue: Decimal
    currency: Currency
    calculation_breakdown: Dict[str, Any]
    calculated_at: datetime = field(default_factory=datetime.now)


@dataclass
class RevenueOptimizer:
    """Revenue optimization configuration"""
    optimizer_id: str
    user_id: str
    optimization_goals: List[str]
    constraints: Dict[str, Any]
    strategies: List[str]
    target_metrics: Dict[str, Decimal]
    active: bool = True


@dataclass
class CommissionCalculator:
    """Commission calculation engine"""
    calculator_id: str
    default_rules: List[CommissionRule]
    user_specific_rules: Dict[str, List[CommissionRule]] = field(default_factory=dict)
    platform_rules: Dict[PlatformType, List[CommissionRule]] = field(default_factory=dict)


@dataclass
class RoyaltyCalculator:
    """Royalty calculation engine"""
    calculator_id: str
    default_rules: List[RoyaltyRule]
    content_specific_rules: Dict[str, List[RoyaltyRule]] = field(default_factory=dict)
    platform_rules: Dict[PlatformType, List[RoyaltyRule]] = field(default_factory=dict)


@dataclass
class TaxCalculator:
    """Tax calculation engine"""
    calculator_id: str
    jurisdiction_rules: Dict[str, List[TaxRule]]
    user_tax_profiles: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    deduction_rules: Dict[str, List[Dict[str, Any]]] = field(default_factory=dict)


@dataclass
class CurrencyConverter:
    """Currency conversion engine"""
    converter_id: str
    exchange_rates: Dict[str, CurrencyRate]
    rate_sources: List[str]
    update_frequency: timedelta = timedelta(minutes=15)
    last_update: Optional[datetime] = None


class RevenueCalculator:
    """
    Advanced revenue calculation engine for content creators.
    
    Provides comprehensive revenue calculations including gross/net revenue,
    commissions, royalties, taxes, fees, and currency conversions with
    real-time optimization and compliance management.
    """
    
    def __init__(self, db_session -> None: AsyncSession, redis_client -> None: Redis, 
                 content_analytics=None) -> None:
        """
        Initialize Revenue Calculator.
        
        Args:
            db_session: Async database session
            redis_client: Redis client for caching
            content_analytics: Content analytics service
        """
        self.db_session = db_session
        self.redis = redis_client
        self.content_analytics = content_analytics
        self.logger = logging.getLogger(__name__)
        
        # Initialize calculation engines
        self.commission_calculator = self._initialize_commission_calculator()
        self.royalty_calculator = self._initialize_royalty_calculator()
        self.tax_calculator = self._initialize_tax_calculator()
        self.currency_converter = self._initialize_currency_converter()
        
        # Configuration
        self.cache_ttl = 3600  # 1 hour
        self.calculation_precision = 8  # Decimal places
        self.rounding_mode = ROUND_HALF_UP
        
        # Platform-specific revenue factors
        self.platform_factors = {
            PlatformType.YOUTUBE: {
                "base_rpm": Decimal('1.50'),  # Revenue per thousand views
                "premium_multiplier": Decimal('1.25'),
                "geographic_factors": {
                    "US": Decimal('1.0'),
                    "EU": Decimal('0.85'),
                    "GLOBAL": Decimal('0.65')
                }
            },
            PlatformType.INSTAGRAM: {
                "base_engagement_rate": Decimal('0.05'),
                "story_multiplier": Decimal('0.3'),
                "reel_multiplier": Decimal('1.8'),
                "post_multiplier": Decimal('1.0')
            },
            PlatformType.TIKTOK: {
                "creator_fund_rate": Decimal('0.02'),
                "brand_partnership_rate": Decimal('15.0'),
                "live_gift_rate": Decimal('0.5')
            },
            PlatformType.SPOTIFY: {
                "stream_rate": Decimal('0.004'),
                "premium_rate": Decimal('0.006'),
                "royalty_rate": Decimal('0.70')
            }
        }
    
    async def calculate_comprehensive_revenue(self, 
                                            request: RevenueCalculationRequest) -> RevenueCalculationResult:
        """
        Calculate comprehensive revenue including all deductions and optimizations.
        
        Args:
            request: Revenue calculation request
            
        Returns:
            Comprehensive revenue calculation result
        """
        try:
            calculation_id = str(uuid.uuid4())
            
            # Step 1: Calculate gross revenue
            gross_revenue = await self._calculate_gross_revenue(request)
            
            # Step 2: Calculate commissions
            commissions = await self._calculate_commissions(request, gross_revenue)
            
            # Step 3: Calculate royalties
            royalties = await self._calculate_royalties(request, gross_revenue)
            
            # Step 4: Calculate taxes
            taxes = await self._calculate_taxes(request, gross_revenue, commissions, royalties)
            
            # Step 5: Calculate fees
            fees = await self._calculate_fees(request, gross_revenue)
            
            # Step 6: Calculate net revenue
            total_deductions = (
                sum(commissions.values()) + 
                sum(royalties.values()) + 
                sum(taxes.values()) + 
                sum(fees.values())
            )
            net_revenue = gross_revenue - total_deductions
            
            # Step 7: Create calculation breakdown
            breakdown = await self._create_calculation_breakdown(
                request, gross_revenue, commissions, royalties, taxes, fees, net_revenue
            )
            
            result = RevenueCalculationResult(
                calculation_id=calculation_id,
                request_id=request.request_id,
                gross_revenue=gross_revenue,
                commissions=commissions,
                royalties=royalties,
                taxes=taxes,
                fees=fees,
                net_revenue=net_revenue,
                currency=request.currency,
                calculation_breakdown=breakdown
            )
            
            # Store result
            await self._store_calculation_result(result)
            
            # Update analytics
            await self._update_revenue_analytics(request.user_id, result)
            
            return result
            
        except Exception as e:
            self.logger.error(f"Error calculating comprehensive revenue: {str(e)}")
            raise
    
    async def calculate_platform_revenue(self, user_id: str, platform: PlatformType,
                                       start_date: datetime, end_date: datetime) -> Decimal:
        """
        Calculate revenue for specific platform and period.
        
        Args:
            user_id: User identifier
            platform: Platform type
            start_date: Period start date
            end_date: Period end date
            
        Returns:
            Total platform revenue
        """
        try:
            # Get platform metrics
            metrics = await self._get_platform_metrics(user_id, platform, start_date, end_date)
            
            # Apply platform-specific calculations
            platform_factors = self.platform_factors.get(platform, {})
            
            if platform == PlatformType.YOUTUBE:
                revenue = await self._calculate_youtube_revenue(metrics, platform_factors)
            elif platform == PlatformType.INSTAGRAM:
                revenue = await self._calculate_instagram_revenue(metrics, platform_factors)
            elif platform == PlatformType.TIKTOK:
                revenue = await self._calculate_tiktok_revenue(metrics, platform_factors)
            elif platform == PlatformType.SPOTIFY:
                revenue = await self._calculate_spotify_revenue(metrics, platform_factors)
            else:
                revenue = await self._calculate_generic_revenue(metrics)
            
            # Apply currency conversion if needed
            revenue = await self._convert_currency(revenue, Currency.USD, Currency.EUR)
            
            return revenue
            
        except Exception as e:
            self.logger.error(f"Error calculating platform revenue: {str(e)}")
            return Decimal('0')
    
    async def calculate_content_revenue(self, content_id: str, 
                                      platform: PlatformType) -> RevenueMetrics:
        """
        Calculate revenue for specific content.
        
        Args:
            content_id: Content identifier
            platform: Platform type
            
        Returns:
            Content revenue metrics
        """
        try:
            # Get content metrics
            content_metrics = await self._get_content_metrics(content_id, platform)
            
            # Calculate base revenue
            base_revenue = await self._calculate_content_base_revenue(content_metrics, platform)
            
            # Apply content-specific bonuses/penalties
            adjustments = await self._calculate_content_adjustments(content_id, platform)
            
            # Calculate final revenue
            final_revenue = base_revenue + adjustments
            
            return RevenueMetrics(
                user_id=content_metrics.get("user_id", ""),
                platform=platform,
                revenue_type=RevenueType.AD_REVENUE,
                amount=final_revenue,
                currency=Currency.EUR,
                period_start=datetime.now() - timedelta(days=1),
                period_end=datetime.now(),
                content_id=content_id,
                metadata=content_metrics
            )
            
        except Exception as e:
            self.logger.error(f"Error calculating content revenue: {str(e)}")
            # Return zero revenue metrics
            return RevenueMetrics(
                user_id="",
                platform=platform,
                revenue_type=RevenueType.AD_REVENUE,
                amount=Decimal('0'),
                currency=Currency.EUR,
                period_start=datetime.now(),
                period_end=datetime.now(),
                content_id=content_id
            )
    
    async def optimize_revenue_strategy(self, user_id: str) -> Dict[str, Any]:
        """
        Optimize revenue strategy for user.
        
        Args:
            user_id: User identifier
            
        Returns:
            Revenue optimization recommendations
        """
        try:
            # Analyze current revenue performance
            performance_analysis = await self._analyze_revenue_performance(user_id)
            
            # Identify optimization opportunities
            opportunities = await self._identify_revenue_opportunities(user_id, performance_analysis)
            
            # Generate optimization strategies
            strategies = await self._generate_optimization_strategies(user_id, opportunities)
            
            # Calculate potential impact
            impact_analysis = await self._calculate_optimization_impact(user_id, strategies)
            
            # Prioritize recommendations
            prioritized_recommendations = await self._prioritize_recommendations(strategies, impact_analysis)
            
            return {
                "user_id": user_id,
                "current_performance": performance_analysis,
                "optimization_opportunities": opportunities,
                "recommended_strategies": prioritized_recommendations,
                "potential_impact": impact_analysis,
                "implementation_timeline": await self._create_optimization_timeline(strategies),
                "success_metrics": await self._define_optimization_metrics(user_id),
                "generated_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Error optimizing revenue strategy: {str(e)}")
            return {"error": str(e)}
    
    async def forecast_revenue(self, user_id: str, forecast_days: int = 90) -> RevenueProjection:
        """
        Forecast future revenue based on historical data and trends.
        
        Args:
            user_id: User identifier
            forecast_days: Number of days to forecast
            
        Returns:
            Revenue projection
        """
        try:
            # Get historical revenue data
            historical_data = await self._get_historical_revenue_data(user_id, 365)
            
            # Apply forecasting models
            trend_forecast = await self._calculate_trend_forecast(historical_data, forecast_days)
            seasonal_forecast = await self._calculate_seasonal_forecast(historical_data, forecast_days)
            ml_forecast = await self._calculate_ml_forecast(user_id, historical_data, forecast_days)
            
            # Combine forecasts with weights
            combined_forecast = (
                trend_forecast * Decimal('0.3') +
                seasonal_forecast * Decimal('0.3') +
                ml_forecast * Decimal('0.4')
            )
            
            # Calculate confidence score
            confidence_score = await self._calculate_forecast_confidence(
                user_id, historical_data, combined_forecast
            )
            
            return RevenueProjection(
                user_id=user_id,
                projection_id=str(uuid.uuid4()),
                projected_amount=combined_forecast,
                currency=Currency.EUR,
                confidence_score=confidence_score,
                projection_period=forecast_days,
                factors=[
                    "historical_trends",
                    "seasonal_patterns",
                    "platform_growth",
                    "content_performance",
                    "market_conditions"
                ]
            )
            
        except Exception as e:
            self.logger.error(f"Error forecasting revenue: {str(e)}")
            raise
    
    # Helper methods
    
    def _initialize_commission_calculator(self) -> CommissionCalculator:
        """Initialize commission calculator with default rules"""
        default_rules = [
            CommissionRule(
                rule_id="platform_standard",
                commission_type=CommissionType.PERCENTAGE,
                rate=Decimal('30.0'),  # 30% platform commission
                minimum_amount=Decimal('0.01')
            ),
            CommissionRule(
                rule_id="payment_processing",
                commission_type=CommissionType.PERCENTAGE,
                rate=Decimal('2.9'),  # 2.9% payment processing
                minimum_amount=Decimal('0.30')
            )
        ]
        
        return CommissionCalculator(
            calculator_id=str(uuid.uuid4()),
            default_rules=default_rules
        )
    
    def _initialize_royalty_calculator(self) -> RoyaltyCalculator:
        """Initialize royalty calculator with default rules"""
        default_rules = [
            RoyaltyRule(
                rule_id="music_streaming",
                royalty_rate=Decimal('70.0'),  # 70% to artists
                base_amount_type="revenue",
                minimum_royalty=Decimal('0.01')
            ),
            RoyaltyRule(
                rule_id="content_licensing",
                royalty_rate=Decimal('50.0'),  # 50% to content creators
                base_amount_type="sales",
                minimum_royalty=Decimal('1.00')
            )
        ]
        
        return RoyaltyCalculator(
            calculator_id=str(uuid.uuid4()),
            default_rules=default_rules
        )
    
    def _initialize_tax_calculator(self) -> TaxCalculator:
        """Initialize tax calculator with jurisdiction rules"""
        eu_rules = [
            TaxRule(
                rule_id="eu_vat",
                tax_category=TaxCategory.VAT,
                tax_rate=Decimal('19.0'),  # German VAT
                jurisdiction="EU",
                exemption_threshold=Decimal('22000.00')
            )
        ]
        
        us_rules = [
            TaxRule(
                rule_id="us_income_tax",
                tax_category=TaxCategory.INCOME_TAX,
                tax_rate=Decimal('22.0'),  # Federal income tax
                jurisdiction="US",
                exemption_threshold=Decimal('12550.00')
            )
        ]
        
        return TaxCalculator(
            calculator_id=str(uuid.uuid4()),
            jurisdiction_rules={
                "EU": eu_rules,
                "US": us_rules
            }
        )
    
    def _initialize_currency_converter(self) -> CurrencyConverter:
        """Initialize currency converter with current rates"""
        return CurrencyConverter(
            converter_id=str(uuid.uuid4()),
            exchange_rates={
                "USD_EUR": CurrencyRate(
                    from_currency=Currency.USD,
                    to_currency=Currency.EUR,
                    rate=Decimal('0.85'),
                    timestamp=datetime.now()
                ),
                "GBP_EUR": CurrencyRate(
                    from_currency=Currency.GBP,
                    to_currency=Currency.EUR,
                    rate=Decimal('1.15'),
                    timestamp=datetime.now()
                )
            },
            rate_sources=["ECB", "market_data"]
        )
    
    async def _calculate_gross_revenue(self, request: RevenueCalculationRequest) -> Decimal:
        """Calculate gross revenue"""
        # Apply platform-specific calculations
        platform_factors = self.platform_factors.get(request.platform, {})
        base_multiplier = platform_factors.get("base_multiplier", Decimal('1.0'))
        
        return request.base_amount * base_multiplier
    
    async def _calculate_commissions(self, request: RevenueCalculationRequest, 
                                   gross_revenue: Decimal) -> Dict[str, Decimal]:
        """Calculate all applicable commissions"""
        commissions = {}
        
        # Platform commission
        platform_rate = Decimal('30.0')  # 30%
        commissions["platform"] = (gross_revenue * platform_rate / Decimal('100')).quantize(
            Decimal('0.01'), rounding=self.rounding_mode
        )
        
        # Payment processing commission
        processing_rate = Decimal('2.9')  # 2.9%
        commissions["payment_processing"] = (gross_revenue * processing_rate / Decimal('100')).quantize(
            Decimal('0.01'), rounding=self.rounding_mode
        )
        
        return commissions
    
    async def _calculate_royalties(self, request: RevenueCalculationRequest,
                                 gross_revenue: Decimal) -> Dict[str, Decimal]:
        """Calculate royalty payments"""
        royalties = {}
        
        # Music royalties (if applicable)
        if request.revenue_type == RevenueType.LICENSING:
            royalty_rate = Decimal('15.0')  # 15%
            royalties["music_rights"] = (gross_revenue * royalty_rate / Decimal('100')).quantize(
                Decimal('0.01'), rounding=self.rounding_mode
            )
        
        return royalties
    
    async def _calculate_taxes(self, request: RevenueCalculationRequest,
                             gross_revenue: Decimal, commissions: Dict[str, Decimal],
                             royalties: Dict[str, Decimal]) -> Dict[str, Decimal]:
        """Calculate tax obligations"""
        taxes = {}
        
        # Simplified tax calculation
        taxable_income = gross_revenue - sum(commissions.values()) - sum(royalties.values())
        
        if taxable_income > Decimal('1000.00'):  # Threshold
            tax_rate = Decimal('19.0')  # 19% VAT
            taxes["vat"] = (taxable_income * tax_rate / Decimal('100')).quantize(
                Decimal('0.01'), rounding=self.rounding_mode
            )
        
        return taxes
    
    async def _calculate_fees(self, request: RevenueCalculationRequest,
                            gross_revenue: Decimal) -> Dict[str, Decimal]:
        """Calculate additional fees"""
        fees = {}
        
        # Transaction fee
        fees["transaction"] = Decimal('0.30').quantize(
            Decimal('0.01'), rounding=self.rounding_mode
        )
        
        return fees
    
    async def _convert_currency(self, amount: Decimal, from_currency: Currency,
                              to_currency: Currency) -> Decimal:
        """Convert currency amount"""
        if from_currency == to_currency:
            return amount
        
        # Get exchange rate
        rate_key = f"{from_currency.value}_{to_currency.value}"
        rate = self.currency_converter.exchange_rates.get(rate_key)
        
        if rate:
            return (amount * rate.rate).quantize(
                Decimal('0.01'), rounding=self.rounding_mode
            )
        
        return amount  # Return original if no rate found
    
    async def _get_platform_metrics(self, user_id: str, platform: PlatformType,
                                  start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        """Get platform-specific metrics"""
        return {
            "views": 10000,
            "engagement_rate": 0.05,
            "clicks": 500,
            "impressions": 50000,
            "revenue_events": 100
        }
    
    async def _calculate_youtube_revenue(self, metrics: Dict[str, Any],
                                       factors: Dict[str, Any]) -> Decimal:
        """Calculate YouTube-specific revenue"""
        views = metrics.get("views", 0)
        rpm = factors.get("base_rpm", Decimal('1.50'))
        
        return Decimal(str(views)) * rpm / Decimal('1000')
    
    async def _calculate_instagram_revenue(self, metrics: Dict[str, Any],
                                         factors: Dict[str, Any]) -> Decimal:
        """Calculate Instagram-specific revenue"""
        engagement = metrics.get("engagement_rate", 0.05)
        followers = metrics.get("followers", 1000)
        
        return Decimal(str(followers)) * Decimal(str(engagement)) * Decimal('0.01')
    
    async def _calculate_tiktok_revenue(self, metrics: Dict[str, Any],
                                      factors: Dict[str, Any]) -> Decimal:
        """Calculate TikTok-specific revenue"""
        views = metrics.get("views", 0)
        creator_fund_rate = factors.get("creator_fund_rate", Decimal('0.02'))
        
        return Decimal(str(views)) * creator_fund_rate / Decimal('1000')
    
    async def _calculate_spotify_revenue(self, metrics: Dict[str, Any],
                                       factors: Dict[str, Any]) -> Decimal:
        """Calculate Spotify-specific revenue"""
        streams = metrics.get("streams", 0)
        stream_rate = factors.get("stream_rate", Decimal('0.004'))
        
        return Decimal(str(streams)) * stream_rate
    
    async def _calculate_generic_revenue(self, metrics: Dict[str, Any]) -> Decimal:
        """Calculate generic platform revenue"""
        revenue_events = metrics.get("revenue_events", 0)
        avg_value = Decimal('1.00')  # €1 per revenue event
        
        return Decimal(str(revenue_events)) * avg_value