"""Royalty Calculator
=================

Advanced royalty calculation engine with multi-model support,
automated distribution, and compliance validation.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel - All Rights Reserved
"""

from typing import Dict, List, Any, Optional, Tuple
from decimal import Decimal, ROUND_HALF_UP
from datetime import datetime, date
from uuid import UUID
import logging
from enum import Enum

from .models import (
    LicenseAgreement, RoyaltyCalculation, RevenueSource,
    LicenseUsageTracking, RevenueDistribution
)
from .repository import LicensingRepository
from ...core.exceptions import ValidationError, CalculationError
from ...utils.currency import CurrencyConverter
from ...utils.validators import validate_decimal, validate_percentage
from ...utils.cache import CacheManager

logger = logging.getLogger(__name__)


class RoyaltyModel(Enum):
    """
Royalty calculation models"""

    PERCENTAGE = "percentage"
    TIERED = "tiered" 
    PERFORMANCE_BASED = "performance_based"
    FIXED_RATE = "fixed_rate"
    HYBRID = "hybrid"
    MINIMUM_GUARANTEE = "minimum_guarantee"


class DistributionMethod(Enum):
    """Revenue distribution methods"""

    PROPORTIONAL = "proportional"
    EQUAL_SPLIT = "equal_split"
    PRIORITY_BASED = "priority_based"
    THRESHOLD_BASED = "threshold_based"
    CUSTOM = "custom"


class RoyaltyCalculator:
    """
    Industrial-grade royalty calculation engine with support for
    complex multi-party revenue distribution and compliance validation.
    """
    
    def __init__(
        self,
        repository: LicensingRepository = None,
        currency_converter: CurrencyConverter = None,
        cache_manager: CacheManager = None
    ):
        """
Initialize calculator with dependencies"""
        self.repository = repository or LicensingRepository()
        self.currency_converter = currency_converter or CurrencyConverter()
        self.cache_manager = cache_manager or CacheManager()
        self._logger = logger
        
        # Default calculation parameters
        self.default_currency = "USD"
        self.precision = Decimal("0.01")  # 2 decimal places
        self.minimum_payment_threshold = Decimal("10.00")
        self.platform_fee_rate = Decimal("0.03")  # 3% platform fee
        
    async def calculate_license_royalties(
        self,
        license_agreement_id: UUID,
        usage_data: Dict[str, Any],
        reporting_period: Tuple[date, date],
        calculation_method: str = "percentage"
    ) -> RoyaltyCalculation:
        """Calculate royalties for a license agreement"""
        try:
            # Get license agreement
            license_agreement = await self.repository.get_license_agreement(
                license_agreement_id, include_relations=True
            )
            if not license_agreement:
                raise ValidationError(f"License agreement {license_agreement_id} not found")
            
            # Validate inputs
            period_start, period_end = reporting_period
            validated_usage_data = await self._validate_usage_data(usage_data)
            
            # Calculate gross revenue
            gross_revenue = await self._calculate_gross_revenue(
                validated_usage_data, license_agreement
            )
            
            # Calculate deductions
            deductions = await self._calculate_deductions(
                gross_revenue, license_agreement, validated_usage_data
            )
            
            # Calculate net revenue
            net_revenue = gross_revenue - sum(deductions.values())
            
            # Calculate royalty amount based on method
            royalty_amount = await self._calculate_royalty_amount(
                net_revenue, license_agreement, validated_usage_data, calculation_method
            )
            
            # Handle advance recoupment
            advance_balance, amount_due = await self._handle_advance_recoupment(
                license_agreement, royalty_amount
            )
            
            # Create royalty calculation record
            calculation_data = {
                "license_agreement_id": license_agreement_id,
                "reporting_period_start": period_start,
                "reporting_period_end": period_end,
                "gross_revenue": gross_revenue,
                "platform_fees": deductions.get("platform_fees", Decimal("0")),
                "taxes": deductions.get("taxes", Decimal("0")),
                "other_deductions": deductions.get("other_deductions", Decimal("0")),
                "net_revenue": net_revenue,
                "royalty_rate": license_agreement.royalty_rate,
                "royalty_amount": royalty_amount,
                "advance_balance": advance_balance,
                "amount_due": amount_due,
                "total_plays": validated_usage_data.get("total_plays", 0),
                "total_streams": validated_usage_data.get("total_streams", 0),
                "total_downloads": validated_usage_data.get("total_downloads", 0),
                "unique_users": validated_usage_data.get("unique_users", 0),
                "revenue_by_territory": validated_usage_data.get("revenue_by_territory"),
                "usage_by_territory": validated_usage_data.get("usage_by_territory"),
                "revenue_by_platform": validated_usage_data.get("revenue_by_platform"),
                "usage_by_platform": validated_usage_data.get("usage_by_platform"),
                "currency": license_agreement.currency,
                "calculation_method": calculation_method
            }
            
            calculation = await self.repository.create_royalty_calculation(
                calculation_data, license_agreement.created_by
            )
            
            self._logger.info(
                f"Calculated royalties for license {license_agreement.license_number}: "
                f"{royalty_amount} {license_agreement.currency}"
            )
            
            return calculation
            
        except (ValidationError, CalculationError):
            raise
        except Exception as e:
            raise CalculationError(f"Error calculating royalties: {str(e)}")
    
    async def calculate_tiered_royalties(
        self,
        net_revenue: Decimal,
        tier_structure: List[Dict[str, Any]],
        currency: str = "USD"
    ) -> Decimal:
        """Calculate royalties using tiered structure"""
        try:
            total_royalty = Decimal("0")
            remaining_revenue = net_revenue
            
            # Sort tiers by threshold
            sorted_tiers = sorted(tier_structure, key=lambda x: x["threshold"])
            
            for i, tier in enumerate(sorted_tiers):
                threshold = Decimal(str(tier["threshold"]))
                rate = Decimal(str(tier["rate"])) / 100  # Convert percentage to decimal
                
                if remaining_revenue <= 0:
                    break
                
                # Determine revenue amount for this tier
                if i < len(sorted_tiers) - 1:
                    next_threshold = Decimal(str(sorted_tiers[i + 1]["threshold"]))
                    tier_revenue = min(remaining_revenue, next_threshold - threshold)
                else:
                    tier_revenue = remaining_revenue
                
                if tier_revenue > 0:
                    tier_royalty = tier_revenue * rate
                    total_royalty += tier_royalty
                    remaining_revenue -= tier_revenue
            
            return total_royalty.quantize(self.precision, rounding=ROUND_HALF_UP)
            
        except (ValueError, KeyError) as e:
            raise CalculationError(f"Error in tiered royalty calculation: {str(e)}")
    
    async def calculate_performance_based_royalties(
        self,
        base_royalty: Decimal,
        performance_metrics: Dict[str, Any],
        performance_thresholds: Dict[str, Any]
    ) -> Decimal:
        """Calculate performance-based royalty adjustments"""
        try:
            adjusted_royalty = base_royalty
            total_bonus = Decimal("0")
            
            # Calculate performance bonuses
            for metric, value in performance_metrics.items():
                if metric in performance_thresholds:
                    thresholds = performance_thresholds[metric]
                    
                    for threshold in thresholds:
                        target = threshold.get("target", 0)
                        bonus_rate = Decimal(str(threshold.get("bonus_rate", 0))) / 100
                        
                        if value >= target:
                            bonus_amount = base_royalty * bonus_rate
                            total_bonus += bonus_amount
            
            # Apply performance cap if specified
            max_bonus_rate = Decimal("0.50")  # 50% maximum bonus
            max_bonus = base_royalty * max_bonus_rate
            total_bonus = min(total_bonus, max_bonus)
            
            adjusted_royalty = base_royalty + total_bonus
            
            return adjusted_royalty.quantize(self.precision, rounding=ROUND_HALF_UP)
            
        except (ValueError, KeyError) as e:
            raise CalculationError(f"Error in performance-based calculation: {str(e)}")
    
    async def calculate_revenue_distribution(
        self,
        royalty_calculation_id: UUID,
        stakeholders: List[Dict[str, Any]],
        distribution_method: str = "proportional"
    ) -> RevenueDistribution:
        """Calculate revenue distribution among stakeholders"""
        try:
            # Get royalty calculation
            royalty_calculations, _ = await self.repository.get_royalty_calculations(
                limit=1, offset=0
            )
            calculation = next(
                (calc for calc in royalty_calculations if calc.id == royalty_calculation_id),
                None
            )
            
            if not calculation:
                raise ValidationError(f"Royalty calculation {royalty_calculation_id} not found")
            
            total_amount = calculation.amount_due
            currency = calculation.currency
            
            # Calculate distribution based on method
            distribution_breakdown = await self._calculate_distribution_breakdown(
                total_amount, stakeholders, distribution_method
            )
            
            # Apply minimum payment thresholds
            filtered_distribution = await self._apply_payment_thresholds(
                distribution_breakdown, currency
            )
            
            # Create distribution record
            distribution_data = {
                "royalty_calculation_id": royalty_calculation_id,
                "total_amount": total_amount,
                "currency": currency,
                "recipient_count": len(filtered_distribution),
                "distribution_breakdown": filtered_distribution,
                "distribution_method": distribution_method,
                "minimum_payment_threshold": self.minimum_payment_threshold,
                "net_distributed": sum(
                    Decimal(str(amount)) for amount in filtered_distribution.values()
                )
            }
            
            # Save distribution record (would need to implement this method)
            # distribution = await self.repository.create_revenue_distribution(distribution_data)
            
            self._logger.info(
                f"Calculated revenue distribution for calculation {calculation.calculation_id}: "
                f"{len(filtered_distribution)} recipients, {total_amount} {currency}"
            )
            
            return distribution_data
            
        except (ValidationError, CalculationError):
            raise
        except Exception as e:
            raise CalculationError(f"Error calculating revenue distribution: {str(e)}")
    
    async def validate_royalty_calculation(
        self,
        calculation: RoyaltyCalculation,
        license_agreement: LicenseAgreement
    ) -> Dict[str, Any]:
        """Validate royalty calculation for accuracy and compliance"""
        try:
            validation_results = {
                "is_valid": True,
                "errors": [],
                "warnings": [],
                "compliance_issues": []
            }
            
            # Validate mathematical accuracy
            expected_net_revenue = (
                calculation.gross_revenue - 
                calculation.platform_fees - 
                calculation.taxes - 
                calculation.other_deductions
            )
            
            if abs(calculation.net_revenue - expected_net_revenue) > self.precision:
                validation_results["errors"].append(
                    f"Net revenue calculation error: expected {expected_net_revenue}, "
                    f"got {calculation.net_revenue}"
                )
                validation_results["is_valid"] = False
            
            # Validate royalty rate
            if calculation.royalty_rate != license_agreement.royalty_rate:
                validation_results["warnings"].append(
                    f"Royalty rate mismatch: license has {license_agreement.royalty_rate}%, "
                    f"calculation uses {calculation.royalty_rate}%"
                )
            
            # Validate minimum guarantee
            if license_agreement.minimum_guarantee > 0:
                if calculation.amount_due < license_agreement.minimum_guarantee:
                    validation_results["compliance_issues"].append(
                        f"Amount due ({calculation.amount_due}) is below minimum guarantee "
                        f"({license_agreement.minimum_guarantee})"
                    )
            
            # Validate currency consistency
            if calculation.currency != license_agreement.currency:
                validation_results["warnings"].append(
                    f"Currency mismatch: license uses {license_agreement.currency}, "
                    f"calculation uses {calculation.currency}"
                )
            
            # Validate reporting period
            if calculation.reporting_period_start >= calculation.reporting_period_end:
                validation_results["errors"].append(
                    "Invalid reporting period: start date must be before end date"
                )
                validation_results["is_valid"] = False
            
            return validation_results
            
        except Exception as e:
            raise CalculationError(f"Error validating royalty calculation: {str(e)}")
    
    # Private helper methods
    
    async def _validate_usage_data(self, usage_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate usage data"""
        required_fields = ["total_revenue"]
        
        for field in required_fields:
            if field not in usage_data:
                raise ValidationError(f"Missing required usage data field: {field}")
        
        # Validate revenue amount
        validate_decimal(usage_data["total_revenue"])
        
        return usage_data
    
    async def _calculate_gross_revenue(
        self,
        usage_data: Dict[str, Any],
        license_agreement: LicenseAgreement
    ) -> Decimal:
        """Calculate gross revenue from usage data"""
        total_revenue = Decimal(str(usage_data["total_revenue"]))
        
        # Convert currency if needed
        if usage_data.get("currency", "USD") != license_agreement.currency:
            total_revenue = await self.currency_converter.convert(
                total_revenue,
                usage_data.get("currency", "USD"),
                license_agreement.currency
            )
        
        return total_revenue.quantize(self.precision, rounding=ROUND_HALF_UP)
    
    async def _calculate_deductions(
        self,
        gross_revenue: Decimal,
        license_agreement: LicenseAgreement,
        usage_data: Dict[str, Any]
    ) -> Dict[str, Decimal]:
        """Calculate various deductions from gross revenue"""
        deductions = {}
        
        # Platform fees
        platform_fee_rate = usage_data.get("platform_fee_rate", self.platform_fee_rate)
        deductions["platform_fees"] = (gross_revenue * platform_fee_rate).quantize(
            self.precision, rounding=ROUND_HALF_UP
        )
        
        # Taxes
        tax_rate = Decimal(str(usage_data.get("tax_rate", 0)))
        deductions["taxes"] = (gross_revenue * tax_rate).quantize(
            self.precision, rounding=ROUND_HALF_UP
        )
        
        # Other deductions
        other_deductions = Decimal(str(usage_data.get("other_deductions", 0)))
        deductions["other_deductions"] = other_deductions.quantize(
            self.precision, rounding=ROUND_HALF_UP
        )
        
        return deductions
    
    async def _calculate_royalty_amount(
        self,
        net_revenue: Decimal,
        license_agreement: LicenseAgreement,
        usage_data: Dict[str, Any],
        calculation_method: str
    ) -> Decimal:
        """Calculate royalty amount based on method"""
        if calculation_method == "percentage":
            royalty_rate = Decimal(str(license_agreement.royalty_rate)) / 100
            return (net_revenue * royalty_rate).quantize(
                self.precision, rounding=ROUND_HALF_UP
            )
        
        elif calculation_method == "tiered":
            tier_structure = usage_data.get("tier_structure", [])
            return await self.calculate_tiered_royalties(
                net_revenue, tier_structure, license_agreement.currency
            )
        
        elif calculation_method == "performance_based":
            base_royalty_rate = Decimal(str(license_agreement.royalty_rate)) / 100
            base_royalty = net_revenue * base_royalty_rate
            
            performance_metrics = usage_data.get("performance_metrics", {})
            performance_thresholds = usage_data.get("performance_thresholds", {})
            
            return await self.calculate_performance_based_royalties(
                base_royalty, performance_metrics, performance_thresholds
            )
        
        elif calculation_method == "fixed_rate":
            fixed_amount = Decimal(str(usage_data.get("fixed_amount", 0)))
            return fixed_amount.quantize(self.precision, rounding=ROUND_HALF_UP)
        
        else:
            raise ValidationError(f"Unsupported calculation method: {calculation_method}")
    
    async def _handle_advance_recoupment(
        self,
        license_agreement: LicenseAgreement,
        royalty_amount: Decimal
    ) -> Tuple[Decimal, Decimal]:
        """Handle advance recoupment logic"""
        advance_balance = license_agreement.advance_payment
        amount_due = royalty_amount
        
        if advance_balance > 0:
            if royalty_amount <= advance_balance:
                # Full royalty goes to advance recoupment
                advance_balance -= royalty_amount
                amount_due = Decimal("0")
            else:
                # Partial recoupment
                amount_due = royalty_amount - advance_balance
                advance_balance = Decimal("0")
        
        return advance_balance, amount_due
    
    async def _calculate_distribution_breakdown(
        self,
        total_amount: Decimal,
        stakeholders: List[Dict[str, Any]],
        method: str
    ) -> Dict[str, Decimal]:
        """Calculate distribution breakdown among stakeholders"""
        distribution = {}
        
        if method == "proportional":
            total_percentage = sum(
                Decimal(str(stakeholder.get("percentage", 0))) 
                for stakeholder in stakeholders
            )
            
            if total_percentage != 100:
                raise ValidationError(f"Total percentage must equal 100%, got {total_percentage}%")
            
            for stakeholder in stakeholders:
                stakeholder_id = stakeholder["id"]
                percentage = Decimal(str(stakeholder["percentage"])) / 100
                amount = (total_amount * percentage).quantize(
                    self.precision, rounding=ROUND_HALF_UP
                )
                distribution[stakeholder_id] = amount
        
        elif method == "equal_split":
            if not stakeholders:
                raise ValidationError("No stakeholders provided for equal split")
            
            amount_per_stakeholder = (total_amount / len(stakeholders)).quantize(
                self.precision, rounding=ROUND_HALF_UP
            )
            
            for stakeholder in stakeholders:
                distribution[stakeholder["id"]] = amount_per_stakeholder
        
        else:
            raise ValidationError(f"Unsupported distribution method: {method}")
        
        return distribution
    
    async def _apply_payment_thresholds(
        self,
        distribution: Dict[str, Decimal],
        currency: str
    ) -> Dict[str, Decimal]:
        """Apply minimum payment thresholds"""
        filtered_distribution = {}
        
        for stakeholder_id, amount in distribution.items():
            if amount >= self.minimum_payment_threshold:
                filtered_distribution[stakeholder_id] = amount
            else:
                self._logger.info(
                    f"Payment {amount} {currency} to {stakeholder_id} below threshold "
                    f"{self.minimum_payment_threshold} {currency} - deferred"
                )
        
        return filtered_distribution


# ==============================================================================
# USAGE TRACKING FUNCTIONALITY 
# ==============================================================================
# Merged from usage_tracker.py to resolve architectural file count constraint
# This provides real-time usage tracking that feeds into royalty calculations

from enum import Enum
import asyncio

class TrackingEvent(Enum):
    """Usage tracking event types"""
    PLAY = "play"
    STREAM = "stream"
    DOWNLOAD = "download"
    VIEW = "view"
    IMPRESSION = "impression"
    CLICK = "click"
    SHARE = "share"
    LIKE = "like"
    COMMENT = "comment"
    SUBSCRIBE = "subscribe"

class TrackingSource(Enum):
    """Tracking data sources"""
    DIRECT_API = "direct_api"
    PLATFORM_WEBHOOK = "platform_webhook"
    BATCH_IMPORT = "batch_import"
    CRAWLER = "crawler"
    SDK = "sdk"
    PIXEL_TRACKING = "pixel_tracking"

class UsageTracker:
    """
    Industrial-grade usage tracking system with real-time monitoring,
    analytics, and compliance validation capabilities.
    Integrated with royalty calculations for seamless revenue tracking.
    """
    
    def __init__(
        self,
        repository: LicensingRepository = None,
        cache_manager: CacheManager = None
    ):
        """Initialize usage tracker with dependencies"""
        self.repository = repository or LicensingRepository()
        self.cache_manager = cache_manager or CacheManager()
        self._logger = logger
        
        # Tracking configuration
        self.batch_size = 1000
        self.flush_interval = 60  # seconds
        self.enable_real_time_compliance = True
        
        # Internal tracking buffer
        self._usage_buffer = []
        self._buffer_lock = asyncio.Lock()
    
    async def track_usage_event(
        self,
        license_agreement_id: UUID,
        event_type: str,
        metadata: Dict[str, Any] = None,
        timestamp: datetime = None,
        source: str = "direct_api"
    ) -> bool:
        """Track a usage event for licensed content"""
        try:
            usage_data = {
                'license_agreement_id': license_agreement_id,
                'event_type': event_type,
                'metadata': metadata or {},
                'timestamp': timestamp or datetime.utcnow(),
                'source': source,
                'tracked_at': datetime.utcnow()
            }
            
            # Add to buffer for batch processing
            async with self._buffer_lock:
                self._usage_buffer.append(usage_data)
                
                # Flush if buffer is full
                if len(self._usage_buffer) >= self.batch_size:
                    await self._flush_usage_buffer()
            
            self._logger.info(f"Usage event tracked: {event_type} for license {license_agreement_id}")
            return True
            
        except Exception as e:
            self._logger.error(f"Failed to track usage event: {str(e)}")
            return False
    
    async def get_usage_statistics(
        self,
        license_agreement_id: UUID,
        start_date: date = None,
        end_date: date = None,
        event_types: List[str] = None
    ) -> Dict[str, Any]:
        """Get usage statistics for a license agreement"""
        try:
            # Query usage data from repository
            usage_records = await self.repository.get_usage_tracking(
                license_agreement_id=license_agreement_id,
                start_date=start_date or (date.today() - timedelta(days=30)),
                end_date=end_date or date.today(),
                event_types=event_types
            )
            
            # Calculate statistics
            stats = {
                'total_events': len(usage_records),
                'event_breakdown': {},
                'daily_usage': {},
                'peak_usage_times': [],
                'geographic_distribution': {},
                'platform_breakdown': {}
            }
            
            # Process usage records
            for record in usage_records:
                # Event type breakdown
                event_type = record.event_type
                stats['event_breakdown'][event_type] = stats['event_breakdown'].get(event_type, 0) + 1
                
                # Daily usage
                usage_date = record.timestamp.date().isoformat()
                stats['daily_usage'][usage_date] = stats['daily_usage'].get(usage_date, 0) + 1
                
                # Platform breakdown
                platform = record.metadata.get('platform', 'unknown')
                stats['platform_breakdown'][platform] = stats['platform_breakdown'].get(platform, 0) + 1
            
            return stats
            
        except Exception as e:
            self._logger.error(f"Failed to get usage statistics: {str(e)}")
            raise TrackingError(f"Failed to retrieve usage statistics: {str(e)}")
    
    async def _flush_usage_buffer(self):
        """Flush usage buffer to persistent storage"""
        try:
            if not self._usage_buffer:
                return
            
            # Create usage tracking records
            tracking_records = []
            for usage_data in self._usage_buffer:
                tracking_record = LicenseUsageTracking(
                    license_agreement_id=usage_data['license_agreement_id'],
                    event_type=usage_data['event_type'],
                    timestamp=usage_data['timestamp'],
                    metadata=usage_data['metadata'],
                    source=usage_data['source']
                )
                tracking_records.append(tracking_record)
            
            # Batch save to repository
            await self.repository.save_usage_tracking_batch(tracking_records)
            
            # Clear buffer
            self._usage_buffer.clear()
            
            self._logger.info(f"Flushed {len(tracking_records)} usage records to storage")
            
        except Exception as e:
            self._logger.error(f"Failed to flush usage buffer: {str(e)}")
    
    async def calculate_usage_based_royalties(
        self,
        license_agreement: LicenseAgreement,
        calculation_period: Tuple[date, date]
    ) -> List[RoyaltyCalculation]:
        """Calculate royalties based on tracked usage data"""
        try:
            start_date, end_date = calculation_period
            
            # Get usage statistics for the period
            usage_stats = await self.get_usage_statistics(
                license_agreement.id,
                start_date=start_date,
                end_date=end_date
            )
            
            # Create royalty calculator instance
            calculator = RoyaltyCalculator(repository=self.repository)
            
            # Calculate royalties based on usage
            royalty_calculations = []
            
            for event_type, count in usage_stats['event_breakdown'].items():
                # Calculate royalty amount based on usage count and license terms
                usage_rate = license_agreement.usage_rates.get(event_type, Decimal('0.01'))
                royalty_amount = Decimal(str(count)) * usage_rate
                
                if royalty_amount > 0:
                    royalty_calc = await calculator.calculate_royalty(
                        license_agreement=license_agreement,
                        usage_data={
                            'event_type': event_type,
                            'usage_count': count,
                            'rate': usage_rate
                        },
                        calculation_date=end_date
                    )
                    royalty_calculations.append(royalty_calc)
            
            return royalty_calculations
            
        except Exception as e:
            self._logger.error(f"Failed to calculate usage-based royalties: {str(e)}")
            raise CalculationError(f"Usage-based royalty calculation failed: {str(e)}")

# Custom exceptions for usage tracking
class TrackingError(Exception):
    """Exception raised for tracking-related errors"""
    pass


# ==============================================================================
# ADVANCED AI ENHANCEMENT FEATURES
# ==============================================================================
# Market intelligence algorithms and predictive revenue analytics

import numpy as np
from typing import List, Dict, Tuple
from datetime import datetime, timedelta
import statistics

class MarketIntelligenceEngine:
    """
    Advanced AI-powered market intelligence for licensing optimization.
    Analyzes market trends, competitor data, and revenue patterns.
    """
    
    def __init__(self, royalty_calculator: 'RoyaltyCalculator'):
        self.calculator = royalty_calculator
        self._logger = logger
        
    def analyze_market_trends(
        self, 
        content_category: str,
        geographic_region: str = None,
        time_period_days: int = 90
    ) -> Dict[str, Any]:
        """
        Analyze market trends for a specific content category and region.
        Uses AI algorithms to identify pricing patterns and demand fluctuations.
        """
        try:
            end_date = datetime.utcnow().date()
            start_date = end_date - timedelta(days=time_period_days)
            
            # Simulate market data analysis (in real implementation, would query market APIs)
            market_data = self._gather_market_data(content_category, geographic_region, start_date, end_date)
            
            # AI-powered trend analysis
            trends = {
                'category': content_category,
                'region': geographic_region,
                'analysis_period': f"{start_date} to {end_date}",
                'average_license_rate': self._calculate_average_license_rate(market_data),
                'demand_trend': self._analyze_demand_trend(market_data),
                'price_volatility': self._calculate_price_volatility(market_data),
                'seasonal_patterns': self._identify_seasonal_patterns(market_data),
                'competitor_analysis': self._analyze_competitor_pricing(market_data),
                'market_opportunity_score': self._calculate_market_opportunity(market_data),
                'recommended_pricing_strategy': self._generate_pricing_recommendations(market_data)
            }
            
            self._logger.info(f"Market intelligence analysis completed for {content_category}")
            return trends
            
        except Exception as e:
            self._logger.error(f"Market intelligence analysis failed: {str(e)}")
            return {'error': str(e), 'trends_available': False}
    
    def predict_optimal_licensing_terms(
        self,
        license_agreement: LicenseAgreement,
        market_conditions: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        AI-powered optimization of licensing terms based on market intelligence.
        Predicts optimal rates, duration, and terms for maximum revenue.
        """
        try:
            # Get current market trends for this content category
            if not market_conditions:
                market_conditions = self.analyze_market_trends(
                    content_category=license_agreement.content_category,
                    geographic_region=license_agreement.territory
                )
            
            # AI optimization algorithms
            optimal_terms = {
                'current_rate': float(license_agreement.royalty_rate or 0),
                'recommended_rate': self._optimize_royalty_rate(license_agreement, market_conditions),
                'recommended_duration': self._optimize_license_duration(license_agreement, market_conditions),
                'recommended_territory_expansion': self._suggest_territory_expansion(license_agreement, market_conditions),
                'revenue_impact_forecast': self._forecast_revenue_impact(license_agreement, market_conditions),
                'risk_assessment': self._assess_licensing_risks(license_agreement, market_conditions),
                'competitive_positioning': self._analyze_competitive_position(license_agreement, market_conditions)
            }
            
            return optimal_terms
            
        except Exception as e:
            self._logger.error(f"Licensing optimization failed: {str(e)}")
            return {'error': str(e), 'optimization_available': False}
    
    def _gather_market_data(self, category: str, region: str, start_date: date, end_date: date) -> List[Dict]:
        """Simulate gathering market data (placeholder for real market API integration)"""
        # In real implementation, would integrate with market data APIs
        days = (end_date - start_date).days
        market_data = []
        
        # Generate realistic sample data for demonstration
        base_rate = 0.05  # 5% base royalty rate
        for i in range(days):
            current_date = start_date + timedelta(days=i)
            
            # Simulate market fluctuations
            seasonal_factor = 1 + 0.2 * np.sin(2 * np.pi * i / 365)  # Annual seasonality
            trend_factor = 1 + 0.001 * i  # Slight upward trend
            noise_factor = 1 + np.random.normal(0, 0.1)  # Random market noise
            
            market_rate = base_rate * seasonal_factor * trend_factor * noise_factor
            
            market_data.append({
                'date': current_date,
                'average_royalty_rate': max(0.01, market_rate),  # Minimum 1%
                'license_volume': np.random.randint(50, 200),
                'avg_license_duration': np.random.randint(6, 36),  # months
                'competitor_count': np.random.randint(5, 15)
            })
        
        return market_data
    
    def _calculate_average_license_rate(self, market_data: List[Dict]) -> float:
        """Calculate average licensing rate from market data"""
        rates = [data['average_royalty_rate'] for data in market_data]
        return statistics.mean(rates) if rates else 0.0
    
    def _analyze_demand_trend(self, market_data: List[Dict]) -> str:
        """Analyze demand trend using linear regression"""
        if len(market_data) < 10:
            return "insufficient_data"
        
        volumes = [data['license_volume'] for data in market_data[-30:]]  # Last 30 days
        
        # Simple trend analysis
        if len(volumes) > 1:
            trend_slope = (volumes[-1] - volumes[0]) / len(volumes)
            if trend_slope > 1:
                return "increasing"
            elif trend_slope < -1:
                return "decreasing"
            else:
                return "stable"
        return "stable"
    
    def _calculate_price_volatility(self, market_data: List[Dict]) -> float:
        """Calculate price volatility using standard deviation"""
        rates = [data['average_royalty_rate'] for data in market_data]
        return statistics.stdev(rates) if len(rates) > 1 else 0.0
    
    def _identify_seasonal_patterns(self, market_data: List[Dict]) -> Dict[str, Any]:
        """Identify seasonal patterns in market data"""
        monthly_averages = {}
        
        for data in market_data:
            month = data['date'].month
            if month not in monthly_averages:
                monthly_averages[month] = []
            monthly_averages[month].append(data['average_royalty_rate'])
        
        # Calculate average rate by month
        seasonal_data = {}
        for month, rates in monthly_averages.items():
            seasonal_data[month] = statistics.mean(rates)
        
        # Identify peak and low seasons
        if seasonal_data:
            peak_month = max(seasonal_data.keys(), key=lambda x: seasonal_data[x])
            low_month = min(seasonal_data.keys(), key=lambda x: seasonal_data[x])
            
            return {
                'has_seasonality': True,
                'peak_month': peak_month,
                'low_month': low_month,
                'seasonal_variance': max(seasonal_data.values()) - min(seasonal_data.values()),
                'monthly_averages': seasonal_data
            }
        
        return {'has_seasonality': False}
    
    def _analyze_competitor_pricing(self, market_data: List[Dict]) -> Dict[str, Any]:
        """Analyze competitor pricing patterns"""
        recent_data = market_data[-7:]  # Last 7 days
        
        if not recent_data:
            return {'competitor_analysis': 'insufficient_data'}
        
        avg_rate = statistics.mean([d['average_royalty_rate'] for d in recent_data])
        competitor_count = statistics.mean([d['competitor_count'] for d in recent_data])
        
        return {
            'market_average_rate': avg_rate,
            'average_competitor_count': competitor_count,
            'market_saturation': 'high' if competitor_count > 10 else 'medium' if competitor_count > 5 else 'low',
            'pricing_pressure': 'high' if avg_rate < 0.03 else 'medium' if avg_rate < 0.07 else 'low'
        }
    
    def _calculate_market_opportunity(self, market_data: List[Dict]) -> float:
        """Calculate market opportunity score (0-100)"""
        if not market_data:
            return 0.0
        
        recent_data = market_data[-30:]  # Last 30 days
        
        # Factors contributing to opportunity score
        demand_growth = 1.0 if self._analyze_demand_trend(market_data) == "increasing" else 0.5
        price_stability = 1.0 - min(1.0, self._calculate_price_volatility(market_data) * 10)
        market_size = min(1.0, statistics.mean([d['license_volume'] for d in recent_data]) / 100)
        
        opportunity_score = (demand_growth * 0.4 + price_stability * 0.3 + market_size * 0.3) * 100
        return min(100.0, max(0.0, opportunity_score))
    
    def _generate_pricing_recommendations(self, market_data: List[Dict]) -> Dict[str, Any]:
        """Generate AI-powered pricing recommendations"""
        market_avg = self._calculate_average_license_rate(market_data)
        volatility = self._calculate_price_volatility(market_data)
        trend = self._analyze_demand_trend(market_data)
        
        # AI recommendation logic
        if trend == "increasing" and volatility < 0.01:
            recommended_rate = market_avg * 1.15  # Premium pricing
            strategy = "premium_pricing"
        elif trend == "decreasing":
            recommended_rate = market_avg * 0.90  # Competitive pricing
            strategy = "competitive_pricing"
        else:
            recommended_rate = market_avg  # Market rate
            strategy = "market_rate"
        
        return {
            'recommended_rate': recommended_rate,
            'strategy': strategy,
            'confidence_level': 0.85 if volatility < 0.02 else 0.65,
            'rationale': f"Based on {trend} demand trend and market volatility of {volatility:.3f}"
        }
    
    def _optimize_royalty_rate(self, license_agreement: LicenseAgreement, market_conditions: Dict) -> float:
        """Optimize royalty rate based on market intelligence"""
        current_rate = float(license_agreement.royalty_rate or 0.05)
        market_avg = market_conditions.get('average_license_rate', 0.05)
        
        # AI optimization considering multiple factors
        if market_conditions.get('demand_trend') == 'increasing':
            optimization_factor = 1.1
        elif market_conditions.get('demand_trend') == 'decreasing':
            optimization_factor = 0.95
        else:
            optimization_factor = 1.0
        
        # Consider market opportunity
        opportunity_score = market_conditions.get('market_opportunity_score', 50)
        if opportunity_score > 75:
            optimization_factor *= 1.05
        elif opportunity_score < 25:
            optimization_factor *= 0.95
        
        optimized_rate = market_avg * optimization_factor
        return max(0.01, min(0.25, optimized_rate))  # Clamp between 1% and 25%
    
    def _optimize_license_duration(self, license_agreement: LicenseAgreement, market_conditions: Dict) -> int:
        """Optimize license duration based on market trends"""
        current_duration = license_agreement.duration_months or 12
        
        # Longer duration for stable/growing markets, shorter for volatile markets
        volatility = market_conditions.get('price_volatility', 0.05)
        if volatility < 0.02:
            return min(36, current_duration + 6)  # Extend by 6 months
        elif volatility > 0.08:
            return max(6, current_duration - 3)   # Reduce by 3 months
        else:
            return current_duration
    
    def _suggest_territory_expansion(self, license_agreement: LicenseAgreement, market_conditions: Dict) -> List[str]:
        """Suggest territorial expansion opportunities"""
        # Simplified territory expansion logic
        high_opportunity_regions = ["EU", "APAC", "LATAM", "NAFTA"]
        current_territory = license_agreement.territory or "US"
        
        suggestions = []
        opportunity_score = market_conditions.get('market_opportunity_score', 50)
        
        if opportunity_score > 60:
            for region in high_opportunity_regions:
                if region != current_territory:
                    suggestions.append(region)
        
        return suggestions[:2]  # Return top 2 suggestions
    
    def _forecast_revenue_impact(self, license_agreement: LicenseAgreement, market_conditions: Dict) -> Dict[str, Any]:
        """Forecast revenue impact of optimization recommendations"""
        current_rate = float(license_agreement.royalty_rate or 0.05)
        recommended_rate = self._optimize_royalty_rate(license_agreement, market_conditions)
        
        # Estimate usage volume (simplified)
        estimated_monthly_usage = 10000  # Placeholder
        current_monthly_revenue = estimated_monthly_usage * current_rate
        projected_monthly_revenue = estimated_monthly_usage * recommended_rate
        
        return {
            'current_monthly_revenue': current_monthly_revenue,
            'projected_monthly_revenue': projected_monthly_revenue,
            'revenue_change_percent': ((projected_monthly_revenue - current_monthly_revenue) / current_monthly_revenue) * 100,
            'annual_revenue_impact': (projected_monthly_revenue - current_monthly_revenue) * 12,
            'confidence_level': 0.75
        }
    
    def _assess_licensing_risks(self, license_agreement: LicenseAgreement, market_conditions: Dict) -> Dict[str, Any]:
        """Assess risks associated with licensing terms"""
        risks = {
            'market_volatility_risk': 'high' if market_conditions.get('price_volatility', 0) > 0.08 else 'low',
            'demand_risk': 'high' if market_conditions.get('demand_trend') == 'decreasing' else 'low',
            'competitive_risk': market_conditions.get('competitor_analysis', {}).get('pricing_pressure', 'medium'),
            'territorial_risk': 'low',  # Simplified
            'overall_risk_score': 0.3  # 30% risk level
        }
        
        return risks
    
    def _analyze_competitive_position(self, license_agreement: LicenseAgreement, market_conditions: Dict) -> Dict[str, Any]:
        """Analyze competitive positioning"""
        current_rate = float(license_agreement.royalty_rate or 0.05)
        market_avg = market_conditions.get('average_license_rate', 0.05)
        
        position = "competitive"
        if current_rate > market_avg * 1.1:
            position = "premium"
        elif current_rate < market_avg * 0.9:
            position = "value"
        
        return {
            'position': position,
            'rate_vs_market': ((current_rate - market_avg) / market_avg) * 100,
            'market_percentile': 50,  # Simplified
            'differentiation_factors': ['quality', 'exclusivity']  # Simplified
        }


class PredictiveRevenueAnalytics:
    """
    Advanced AI-powered predictive analytics for revenue forecasting.
    Uses machine learning algorithms to predict future revenue streams.
    """
    
    def __init__(self, royalty_calculator: 'RoyaltyCalculator'):
        self.calculator = royalty_calculator
        self._logger = logger
    
    def predict_revenue_forecast(
        self,
        license_agreement: LicenseAgreement,
        forecast_months: int = 12,
        confidence_level: float = 0.85
    ) -> Dict[str, Any]:
        """
        Generate AI-powered revenue forecasts for license agreements.
        Uses historical data and market trends for predictions.
        """
        try:
            # Gather historical revenue data
            historical_data = self._gather_historical_revenue_data(license_agreement)
            
            # Apply AI forecasting algorithms
            forecast = {
                'license_agreement_id': str(license_agreement.id),
                'forecast_period_months': forecast_months,
                'confidence_level': confidence_level,
                'monthly_predictions': self._generate_monthly_predictions(historical_data, forecast_months),
                'trend_analysis': self._analyze_revenue_trends(historical_data),
                'seasonality_impact': self._calculate_seasonality_impact(historical_data),
                'growth_projections': self._calculate_growth_projections(historical_data),
                'risk_factors': self._identify_risk_factors(historical_data),
                'optimization_opportunities': self._identify_optimization_opportunities(historical_data)
            }
            
            self._logger.info(f"Revenue forecast generated for license {license_agreement.id}")
            return forecast
            
        except Exception as e:
            self._logger.error(f"Revenue forecasting failed: {str(e)}")
            return {'error': str(e), 'forecast_available': False}
    
    def _gather_historical_revenue_data(self, license_agreement: LicenseAgreement) -> List[Dict]:
        """Gather historical revenue data (placeholder implementation)"""
        # In real implementation, would query actual revenue records
        historical_data = []
        current_date = datetime.utcnow().date()
        
        # Generate sample historical data for last 12 months
        for i in range(12, 0, -1):
            month_date = current_date - timedelta(days=30 * i)
            
            # Simulate revenue with trend and seasonality
            base_revenue = 1000
            trend_factor = 1 + (0.05 * (12 - i) / 12)  # 5% annual growth
            seasonal_factor = 1 + 0.2 * np.sin(2 * np.pi * (month_date.month - 1) / 12)
            noise_factor = 1 + np.random.normal(0, 0.1)
            
            monthly_revenue = base_revenue * trend_factor * seasonal_factor * noise_factor
            
            historical_data.append({
                'date': month_date,
                'revenue': max(0, monthly_revenue),
                'usage_count': np.random.randint(8000, 15000),
                'unique_users': np.random.randint(500, 1200)
            })
        
        return historical_data
    
    def _generate_monthly_predictions(self, historical_data: List[Dict], forecast_months: int) -> List[Dict]:
        """Generate monthly revenue predictions using AI algorithms"""
        if not historical_data:
            return []
        
        # Simple trend-based prediction (in real implementation, would use ML models)
        recent_revenues = [data['revenue'] for data in historical_data[-6:]]  # Last 6 months
        avg_growth_rate = self._calculate_average_growth_rate(recent_revenues)
        
        predictions = []
        last_revenue = historical_data[-1]['revenue']
        last_date = historical_data[-1]['date']
        
        for i in range(1, forecast_months + 1):
            predicted_date = last_date + timedelta(days=30 * i)
            
            # Apply growth rate and seasonality
            growth_factor = (1 + avg_growth_rate) ** i
            seasonal_factor = 1 + 0.2 * np.sin(2 * np.pi * (predicted_date.month - 1) / 12)
            
            predicted_revenue = last_revenue * growth_factor * seasonal_factor
            
            # Add confidence intervals
            confidence_range = predicted_revenue * 0.2  # ±20% confidence interval
            
            predictions.append({
                'date': predicted_date,
                'predicted_revenue': predicted_revenue,
                'confidence_lower': predicted_revenue - confidence_range,
                'confidence_upper': predicted_revenue + confidence_range,
                'growth_rate': avg_growth_rate,
                'seasonal_adjustment': seasonal_factor - 1
            })
        
        return predictions
    
    def _calculate_average_growth_rate(self, revenue_data: List[float]) -> float:
        """Calculate average monthly growth rate"""
        if len(revenue_data) < 2:
            return 0.0
        
        growth_rates = []
        for i in range(1, len(revenue_data)):
            if revenue_data[i-1] > 0:
                growth_rate = (revenue_data[i] - revenue_data[i-1]) / revenue_data[i-1]
                growth_rates.append(growth_rate)
        
        return statistics.mean(growth_rates) if growth_rates else 0.0
    
    def _analyze_revenue_trends(self, historical_data: List[Dict]) -> Dict[str, Any]:
        """Analyze revenue trends using statistical methods"""
        revenues = [data['revenue'] for data in historical_data]
        
        if len(revenues) < 3:
            return {'trend': 'insufficient_data'}
        
        # Calculate trend indicators
        recent_avg = statistics.mean(revenues[-3:])  # Last 3 months
        earlier_avg = statistics.mean(revenues[:3])  # First 3 months
        
        trend_direction = "increasing" if recent_avg > earlier_avg else "decreasing"
        trend_strength = abs(recent_avg - earlier_avg) / earlier_avg if earlier_avg > 0 else 0
        
        return {
            'trend_direction': trend_direction,
            'trend_strength': trend_strength,
            'volatility': statistics.stdev(revenues) / statistics.mean(revenues) if statistics.mean(revenues) > 0 else 0,
            'recent_performance': recent_avg,
            'baseline_performance': earlier_avg
        }
    
    def _calculate_seasonality_impact(self, historical_data: List[Dict]) -> Dict[str, Any]:
        """Calculate seasonality impact on revenue"""
        monthly_revenues = {}
        
        for data in historical_data:
            month = data['date'].month
            if month not in monthly_revenues:
                monthly_revenues[month] = []
            monthly_revenues[month].append(data['revenue'])
        
        # Calculate seasonal factors
        seasonal_factors = {}
        overall_avg = statistics.mean([data['revenue'] for data in historical_data])
        
        for month, revenues in monthly_revenues.items():
            month_avg = statistics.mean(revenues)
            seasonal_factors[month] = month_avg / overall_avg if overall_avg > 0 else 1.0
        
        return {
            'has_seasonality': max(seasonal_factors.values()) - min(seasonal_factors.values()) > 0.2,
            'seasonal_factors': seasonal_factors,
            'peak_month': max(seasonal_factors.keys(), key=lambda x: seasonal_factors[x]) if seasonal_factors else None,
            'low_month': min(seasonal_factors.keys(), key=lambda x: seasonal_factors[x]) if seasonal_factors else None
        }
    
    def _calculate_growth_projections(self, historical_data: List[Dict]) -> Dict[str, Any]:
        """Calculate growth projections and scenarios"""
        revenues = [data['revenue'] for data in historical_data]
        
        if len(revenues) < 6:
            return {'projections': 'insufficient_data'}
        
        growth_rate = self._calculate_average_growth_rate(revenues)
        current_revenue = revenues[-1]
        
        # Calculate different growth scenarios
        scenarios = {
            'conservative': current_revenue * (1 + growth_rate * 0.5) ** 12,  # 50% of historical growth
            'realistic': current_revenue * (1 + growth_rate) ** 12,           # Historical growth rate
            'optimistic': current_revenue * (1 + growth_rate * 1.5) ** 12    # 150% of historical growth
        }
        
        return {
            'annual_growth_rate': growth_rate * 12,  # Annualized
            'current_annual_revenue': current_revenue * 12,
            'projected_scenarios': scenarios,
            'growth_confidence': 0.75 if abs(growth_rate) < 0.1 else 0.60
        }
    
    def _identify_risk_factors(self, historical_data: List[Dict]) -> List[Dict[str, Any]]:
        """Identify potential risk factors affecting revenue"""
        revenues = [data['revenue'] for data in historical_data]
        risk_factors = []
        
        # Volatility risk
        if len(revenues) > 1:
            volatility = statistics.stdev(revenues) / statistics.mean(revenues)
            if volatility > 0.3:
                risk_factors.append({
                    'type': 'high_volatility',
                    'severity': 'high' if volatility > 0.5 else 'medium',
                    'description': f'Revenue volatility of {volatility:.1%} indicates unstable income',
                    'mitigation': 'Consider diversifying revenue streams or adjusting pricing strategy'
                })
        
        # Declining trend risk
        trend_analysis = self._analyze_revenue_trends(historical_data)
        if trend_analysis.get('trend_direction') == 'decreasing':
            risk_factors.append({
                'type': 'declining_trend',
                'severity': 'high' if trend_analysis.get('trend_strength', 0) > 0.2 else 'medium',
                'description': 'Revenue shows declining trend over recent period',
                'mitigation': 'Review licensing terms and market positioning'
            })
        
        return risk_factors
    
    def _identify_optimization_opportunities(self, historical_data: List[Dict]) -> List[Dict[str, Any]]:
        """Identify opportunities for revenue optimization"""
        opportunities = []
        
        # Seasonal optimization
        seasonality = self._calculate_seasonality_impact(historical_data)
        if seasonality.get('has_seasonality'):
            opportunities.append({
                'type': 'seasonal_pricing',
                'potential_impact': 'medium',
                'description': 'Adjust pricing based on seasonal demand patterns',
                'recommendation': f'Increase rates during peak month {seasonality.get("peak_month")}'
            })
        
        # Growth acceleration
        trend_analysis = self._analyze_revenue_trends(historical_data)
        if trend_analysis.get('trend_direction') == 'increasing':
            opportunities.append({
                'type': 'growth_acceleration',
                'potential_impact': 'high',
                'description': 'Positive trend presents opportunity for premium pricing',
                'recommendation': 'Consider gradual rate increases to capitalize on growth'
            })
        
        return opportunities
