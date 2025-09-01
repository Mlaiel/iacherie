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
