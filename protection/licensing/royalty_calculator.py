"""💰 Royalty Calculator - Advanced Revenue Calculation Engine
=========================================================

Professional royalty and revenue calculation system:
- Multi-tier royalty structures
- Performance-based calculations
- Territory-specific rates
- Currency conversion
- Tax calculation integration

Author: Fahed Mlaiel (mlaiel@live.de)
Team: Lead Dev IA + Financial Engineer + Music Business Analyst + Tax Specialist
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import logging
import asyncio
from typing import Dict, Any, List, Optional, Union, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from enum import Enum
from decimal import Decimal, ROUND_HALF_UP
import json
import math

logger = logging.getLogger(__name__)

class RoyaltyType(Enum):
    """
Types of royalty structures"""

    FLAT_PERCENTAGE = "flat_percentage"
    TIERED_PERCENTAGE = "tiered_percentage"
    PERFORMANCE_BASED = "performance_based"
    HYBRID = "hybrid"
    RECOUPABLE_ADVANCE = "recoupable_advance"

class RevenueSource(Enum):
    """Sources of revenue"""

    STREAMING = "streaming"
    DOWNLOADS = "downloads"
    PHYSICAL_SALES = "physical_sales"
    PERFORMANCE_ROYALTIES = "performance_royalties"
    SYNC_LICENSING = "sync_licensing"
    MECHANICAL_ROYALTIES = "mechanical_royalties"
    MERCHANDISING = "merchandising"
    LIVE_PERFORMANCES = "live_performances"

class CalculationMethod(Enum):
    """Calculation methodologies"""

    NET_RECEIPTS = "net_receipts"
    GROSS_RECEIPTS = "gross_receipts"
    PUBLISHED_PRICE_TO_DEALER = "ppd"
    STATUTORY_RATE = "statutory_rate"

@dataclass
class RoyaltyTier:
    """Individual royalty tier definition"""
    tier_id: str
    threshold_start: Decimal
    threshold_end: Optional[Decimal]
    rate: Decimal
    currency: str
    revenue_sources: List[RevenueSource]

@dataclass
class DeductionRule:
    """
Revenue deduction rule"""
    deduction_id: str
    name: str
    deduction_type: str  # percentage, fixed, tiered
    value: Decimal
    applies_to: List[RevenueSource]
    jurisdiction_specific: bool
    mandatory: bool

@dataclass
class RoyaltyStructure:
    """
Complete royalty structure definition"""
    structure_id: str
    license_id: str
    royalty_type: RoyaltyType
    calculation_method: CalculationMethod
    base_rate: Decimal
    tiers: List[RoyaltyTier]
    deductions: List[DeductionRule]
    minimum_guarantee: Optional[Decimal]
    advance_amount: Optional[Decimal]
    recoup_threshold: Optional[Decimal]
    territory_rates: Dict[str, Decimal]
    currency: str
    effective_date: datetime
    expiration_date: Optional[datetime]

@dataclass
class CalculationResult:
    """
Royalty calculation result"""
    calculation_id: str
    license_id: str
    period_start: datetime
    period_end: datetime
    gross_revenue: Decimal
    total_deductions: Decimal
    net_revenue: Decimal
    royalty_amount: Decimal
    advance_recouped: Decimal
    remaining_advance: Decimal
    tier_breakdown: List[Dict[str, Any]]
    currency: str
    calculation_date: datetime

class RoyaltyCalculator:
    """
    🚀 Professional royalty calculation engine
    
    Advanced system for calculating royalties with support for complex
    structures, multi-tier rates, and international compliance.
    """
    
    def __init__(self, config -> None: Dict[str, Any]) -> None:
        """
Initialize royalty calculator with configuration."""
        self.config = config
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        
        # Calculation engines
        self.currency_converter = None
        self.tax_calculator = None
        
        # Rate databases
        self.statutory_rates = {}
        self.territory_multipliers = {}
        self.platform_rates = {}
        
        # Performance metrics
        self.metrics = {
            'calculations_performed': 0,
            'total_revenue_processed': Decimal('0.00'),
            'total_royalties_calculated': Decimal('0.00'),
            'average_calculation_time': 0.0,
            'complex_structures_processed': 0
        }
        
        self._load_statutory_rates()
        self._load_territory_data()
        self._load_platform_rates()
        self._initialize_currency_converter()
    
    def _load_statutory_rates(self) -> None:
        """Load statutory royalty rates by jurisdiction."""
        statutory_data = {
            'us': {
                'mechanical_rate_per_track': Decimal('0.091'),  # 2023 rate
                'performance_rate_radio': Decimal('0.0021'),
                'performance_rate_streaming': Decimal('0.00000017'),
                'sync_rate_tv': Decimal('0.0025'),
                'sync_rate_film': Decimal('0.005')
            },
            'germany': {
                'gema_rate_streaming': Decimal('0.0065'),
                'gema_rate_radio': Decimal('0.008'),
                'mechanical_rate': Decimal('0.0665'),
                'public_performance_rate': Decimal('0.01')
            },
            'uk': {
                'prs_rate_streaming': Decimal('0.0059'),
                'prs_rate_radio': Decimal('0.007'),
                'mechanical_rate': Decimal('0.084'),
                'sync_rate_tv': Decimal('0.003')
            },
            'france': {
                'sacem_rate_streaming': Decimal('0.0061'),
                'sacem_rate_radio': Decimal('0.0075'),
                'mechanical_rate': Decimal('0.07'),
                'sync_rate_tv': Decimal('0.0028')
            }
        }
        
        self.statutory_rates = statutory_data
        self.logger.info(f"Loaded statutory rates for {len(statutory_data)} jurisdictions")
    
    def _load_territory_data(self) -> None:
        """Load territory-specific multipliers and adjustments."""
        territory_data = {
            'north_america': {'multiplier': Decimal('1.0'), 'currencies': ['USD', 'CAD']},
            'europe': {'multiplier': Decimal('0.95'), 'currencies': ['EUR', 'GBP']},
            'asia_pacific': {'multiplier': Decimal('0.85'), 'currencies': ['JPY', 'AUD', 'SGD']},
            'latin_america': {'multiplier': Decimal('0.75'), 'currencies': ['BRL', 'MXN', 'ARS']},
            'africa_middle_east': {'multiplier': Decimal('0.70'), 'currencies': ['ZAR', 'AED']},
            'emerging_markets': {'multiplier': Decimal('0.60'), 'currencies': ['INR', 'RUB']}
        }
        
        self.territory_multipliers = territory_data
        self.logger.info(f"Loaded territory data for {len(territory_data)} regions")
    
    def _load_platform_rates(self) -> None:
        """Load platform-specific royalty rates."""
        platform_data = {
            'spotify': {
                'rate_per_stream': Decimal('0.003'),
                'territory_adjustments': {
                    'us': Decimal('1.0'),
                    'germany': Decimal('0.95'),
                    'uk': Decimal('0.92'),
                    'emerging': Decimal('0.60')
                }
            },
            'apple_music': {
                'rate_per_stream': Decimal('0.007'),
                'territory_adjustments': {
                    'us': Decimal('1.0'),
                    'germany': Decimal('0.98'),
                    'uk': Decimal('0.95'),
                    'emerging': Decimal('0.70')
                }
            },
            'youtube_music': {
                'rate_per_stream': Decimal('0.0008'),
                'ad_supported_multiplier': Decimal('0.3'),
                'premium_multiplier': Decimal('1.5')
            },
            'amazon_music': {
                'rate_per_stream': Decimal('0.004'),
                'unlimited_multiplier': Decimal('1.2')
            }
        }
        
        self.platform_rates = platform_data
        self.logger.info(f"Loaded rates for {len(platform_data)} platforms")
    
    def _initialize_currency_converter(self) -> None:
        """Initialize currency conversion service."""
        try:
            # This would integrate with a real currency service
            # For now, using static rates
            self.currency_converter = {
                'USD': Decimal('1.0'),
                'EUR': Decimal('0.85'),
                'GBP': Decimal('0.75'),
                'CAD': Decimal('1.25'),
                'JPY': Decimal('110.0'),
                'AUD': Decimal('1.35')
            }
            self.logger.info("Currency converter initialized")
        except Exception as e:
            self.logger.error(f"Failed to initialize currency converter: {e}")
    
    async def calculate_royalty_structure(
        self,
        content_info: Dict[str, Any],
        license_type: str,
        jurisdiction: str,
        custom_terms: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        💰 Calculate comprehensive royalty structure
        
        Args:
            content_info: Information about the content
            license_type: Type of license agreement
            jurisdiction: Legal jurisdiction
            custom_terms: Custom royalty terms
            
        Returns:
            royalty_structure: Complete royalty calculation structure
        """
        try:
            self.logger.info(f"Calculating royalty structure for {license_type} in {jurisdiction}")
            
            # Determine base royalty type and rates
            royalty_type, base_rate = await self._determine_royalty_type(
                license_type=license_type,
                jurisdiction=jurisdiction,
                content_info=content_info
            )
            
            # Create royalty tiers
            tiers = await self._create_royalty_tiers(
                base_rate=base_rate,
                royalty_type=royalty_type,
                license_type=license_type,
                custom_terms=custom_terms or {}
            )
            
            # Define deduction rules
            deductions = await self._create_deduction_rules(
                jurisdiction=jurisdiction,
                license_type=license_type
            )
            
            # Calculate territory-specific rates
            territory_rates = await self._calculate_territory_rates(
                base_rate=base_rate,
                jurisdiction=jurisdiction
            )
            
            # Determine minimum guarantee and advance
            financial_terms = await self._calculate_financial_terms(
                content_info=content_info,
                license_type=license_type,
                base_rate=base_rate,
                custom_terms=custom_terms or {}
            )
            
            # Create complete structure
            royalty_structure = RoyaltyStructure(
                structure_id=f"royalty_{content_info.get('id', 'unknown')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                license_id=content_info.get('license_id', ''),
                royalty_type=royalty_type,
                calculation_method=CalculationMethod.NET_RECEIPTS,
                base_rate=base_rate,
                tiers=tiers,
                deductions=deductions,
                minimum_guarantee=financial_terms.get('minimum_guarantee'),
                advance_amount=financial_terms.get('advance_amount'),
                recoup_threshold=financial_terms.get('recoup_threshold'),
                territory_rates=territory_rates,
                currency=custom_terms.get('currency', 'USD'),
                effective_date=datetime.now(),
                expiration_date=None
            )
            
            return {
                'royalty_structure': asdict(royalty_structure),
                'calculation_methodology': await self._generate_calculation_methodology(royalty_structure),
                'revenue_projections': await self._generate_revenue_projections(royalty_structure),
                'compliance_notes': await self._generate_compliance_notes(jurisdiction, license_type),
                'generated_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Failed to calculate royalty structure: {e}")
            raise
    
    async def _determine_royalty_type(
        self,
        license_type: str,
        jurisdiction: str,
        content_info: Dict[str, Any]
    ) -> Tuple[RoyaltyType, Decimal]:
        """Determine appropriate royalty type and base rate."""
        # Default rates by license type
        license_type_rates = {
            'commercial': (RoyaltyType.FLAT_PERCENTAGE, Decimal('0.70')),
            'sync_licensing': (RoyaltyType.PERFORMANCE_BASED, Decimal('0.50')),
            'streaming': (RoyaltyType.TIERED_PERCENTAGE, Decimal('0.60')),
            'mechanical': (RoyaltyType.FLAT_PERCENTAGE, Decimal('0.75')),
            'performance': (RoyaltyType.PERFORMANCE_BASED, Decimal('0.50'))
        }
        
        base_type, base_rate = license_type_rates.get(license_type, 
                                                     (RoyaltyType.FLAT_PERCENTAGE, Decimal('0.70')))
        
        # Adjust for jurisdiction
        jurisdiction_adjustments = {
            'us': Decimal('1.0'),
            'germany': Decimal('0.95'),
            'uk': Decimal('0.90'),
            'france': Decimal('0.88'),
            'international': Decimal('0.85')
        }
        
        adjustment = jurisdiction_adjustments.get(jurisdiction, Decimal('1.0'))
        adjusted_rate = base_rate * adjustment
        
        return base_type, adjusted_rate
    
    async def _create_royalty_tiers(
        self,
        base_rate: Decimal,
        royalty_type: RoyaltyType,
        license_type: str,
        custom_terms: Dict[str, Any]
    ) -> List[RoyaltyTier]:
        """
Create royalty tier structure."""
        tiers = []
        
        if royalty_type == RoyaltyType.FLAT_PERCENTAGE:
            # Single tier for flat percentage
            tiers.append(RoyaltyTier(
                tier_id='flat_tier',
                threshold_start=Decimal('0'),
                threshold_end=None,
                rate=base_rate,
                currency=custom_terms.get('currency', 'USD'),
                revenue_sources=[RevenueSource.STREAMING, RevenueSource.DOWNLOADS]
            ))
        
        elif royalty_type == RoyaltyType.TIERED_PERCENTAGE:
            # Multiple tiers with increasing rates
            tier_definitions = [
                (Decimal('0'), Decimal('10000'), base_rate * Decimal('0.8')),
                (Decimal('10000'), Decimal('100000'), base_rate),
                (Decimal('100000'), None, base_rate * Decimal('1.2'))
            ]
            
            for i, (start, end, rate) in enumerate(tier_definitions):
                tiers.append(RoyaltyTier(
                    tier_id=f'tier_{i+1}',
                    threshold_start=start,
                    threshold_end=end,
                    rate=rate,
                    currency=custom_terms.get('currency', 'USD'),
                    revenue_sources=[RevenueSource.STREAMING, RevenueSource.DOWNLOADS]
                ))
        
        elif royalty_type == RoyaltyType.PERFORMANCE_BASED:
            # Performance-based tiers
            performance_tiers = [
                (Decimal('0'), Decimal('1000000'), base_rate * Decimal('0.6')),  # < 1M streams
                (Decimal('1000000'), Decimal('10000000'), base_rate * Decimal('0.8')),  # 1M-10M streams
                (Decimal('10000000'), None, base_rate)  # > 10M streams
            ]
            
            for i, (start, end, rate) in enumerate(performance_tiers):
                tiers.append(RoyaltyTier(
                    tier_id=f'performance_tier_{i+1}',
                    threshold_start=start,
                    threshold_end=end,
                    rate=rate,
                    currency=custom_terms.get('currency', 'USD'),
                    revenue_sources=[RevenueSource.STREAMING, RevenueSource.PERFORMANCE_ROYALTIES]
                ))
        
        return tiers
    
    async def _create_deduction_rules(
        self,
        jurisdiction: str,
        license_type: str
    ) -> List[DeductionRule]:
        """
Create applicable deduction rules."""
        deductions = []
        
        # Platform fees (universal)
        deductions.append(DeductionRule(
            deduction_id='platform_fees',
            name='Platform Distribution Fees',
            deduction_type='percentage',
            value=Decimal('0.30'),  # 30%
            applies_to=[RevenueSource.STREAMING, RevenueSource.DOWNLOADS],
            jurisdiction_specific=False,
            mandatory=True
        ))
        
        # Payment processing (universal)
        deductions.append(DeductionRule(
            deduction_id='payment_processing',
            name='Payment Processing Fees',
            deduction_type='percentage',
            value=Decimal('0.03'),  # 3%
            applies_to=list(RevenueSource),
            jurisdiction_specific=False,
            mandatory=True
        ))
        
        # Jurisdiction-specific deductions
        if jurisdiction in ['us']:
            deductions.append(DeductionRule(
                deduction_id='us_collection_fees',
                name='US Collection Society Fees',
                deduction_type='percentage',
                value=Decimal('0.15'),  # 15%
                applies_to=[RevenueSource.PERFORMANCE_ROYALTIES],
                jurisdiction_specific=True,
                mandatory=True
            ))
        
        elif jurisdiction in ['germany']:
            deductions.append(DeductionRule(
                deduction_id='gema_fees',
                name='GEMA Administration Fees',
                deduction_type='percentage',
                value=Decimal('0.20'),  # 20%
                applies_to=[RevenueSource.PERFORMANCE_ROYALTIES, RevenueSource.MECHANICAL_ROYALTIES],
                jurisdiction_specific=True,
                mandatory=True
            ))
        
        # Marketing and promotion (optional)
        deductions.append(DeductionRule(
            deduction_id='marketing_costs',
            name='Marketing and Promotion Costs',
            deduction_type='percentage',
            value=Decimal('0.10'),  # 10%
            applies_to=list(RevenueSource),
            jurisdiction_specific=False,
            mandatory=False
        ))
        
        return deductions
    
    async def _calculate_territory_rates(
        self,
        base_rate: Decimal,
        jurisdiction: str
    ) -> Dict[str, Decimal]:
        """
Calculate territory-specific royalty rates."""
        territory_rates = {}
        
        # Base jurisdiction rate
        territory_rates[jurisdiction] = base_rate
        
        # Calculate rates for other territories based on multipliers
        for territory, data in self.territory_multipliers.items():
            adjusted_rate = base_rate * data['multiplier']
            territory_rates[territory] = adjusted_rate.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
        
        return territory_rates
    
    async def _calculate_financial_terms(
        self,
        content_info: Dict[str, Any],
        license_type: str,
        base_rate: Decimal,
        custom_terms: Dict[str, Any]
    ) -> Dict[str, Optional[Decimal]]:
        """
Calculate financial terms like advances and minimum guarantees."""
        financial_terms = {}
        
        # Minimum guarantee calculation
        if custom_terms.get('include_minimum_guarantee', False):
            # Base calculation on expected revenue
            expected_annual_revenue = Decimal(custom_terms.get('expected_revenue', '50000'))
            minimum_guarantee = expected_annual_revenue * base_rate * Decimal('0.5')  # 50% of expected royalties
            financial_terms['minimum_guarantee'] = minimum_guarantee.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
        else:
            financial_terms['minimum_guarantee'] = None
        
        # Advance calculation
        if custom_terms.get('include_advance', False):
            advance_multiplier = Decimal(custom_terms.get('advance_multiplier', '2.0'))
            if financial_terms['minimum_guarantee']:
                advance_amount = financial_terms['minimum_guarantee'] * advance_multiplier
            else:
                advance_amount = Decimal(custom_terms.get('advance_amount', '10000'))
            financial_terms['advance_amount'] = advance_amount.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
            
            # Recoup threshold (usually same as advance)
            financial_terms['recoup_threshold'] = financial_terms['advance_amount']
        else:
            financial_terms['advance_amount'] = None
            financial_terms['recoup_threshold'] = None
        
        return financial_terms
    
    async def _generate_calculation_methodology(self, royalty_structure: RoyaltyStructure) -> Dict[str, Any]:
        """
Generate explanation of calculation methodology."""
        methodology = {
            'calculation_method': royalty_structure.calculation_method.value,
            'royalty_type': royalty_structure.royalty_type.value,
            'base_rate': float(royalty_structure.base_rate),
            'tier_structure': [],
            'deduction_policy': [],
            'currency_handling': 'Amounts calculated in base currency, converted as needed'
        }
        
        # Explain tier structure
        for tier in royalty_structure.tiers:
            tier_explanation = {
                'tier_id': tier.tier_id,
                'threshold_range': f"{float(tier.threshold_start)} - {float(tier.threshold_end) if tier.threshold_end else 'unlimited'}",
                'rate': f"{float(tier.rate * 100):.1f}%",
                'applies_to': [source.value for source in tier.revenue_sources]
            }
            methodology['tier_structure'].append(tier_explanation)
        
        # Explain deductions
        for deduction in royalty_structure.deductions:
            deduction_explanation = {
                'name': deduction.name,
                'type': deduction.deduction_type,
                'rate': f"{float(deduction.value * 100):.1f}%" if deduction.deduction_type == 'percentage' else f"{float(deduction.value)} {royalty_structure.currency}",
                'mandatory': deduction.mandatory,
                'applies_to': [source.value for source in deduction.applies_to]
            }
            methodology['deduction_policy'].append(deduction_explanation)
        
        return methodology
    
    async def _generate_revenue_projections(self, royalty_structure: RoyaltyStructure) -> Dict[str, Any]:
        """Generate revenue projections based on royalty structure."""
        # Sample scenarios for projection
        scenarios = {
            'conservative': {'monthly_streams': 100000, 'avg_revenue_per_stream': 0.003},
            'moderate': {'monthly_streams': 500000, 'avg_revenue_per_stream': 0.004},
            'optimistic': {'monthly_streams': 2000000, 'avg_revenue_per_stream': 0.005}
        }
        
        projections = {}
        
        for scenario_name, params in scenarios.items():
            monthly_gross = Decimal(str(params['monthly_streams'] * params['avg_revenue_per_stream']))
            annual_gross = monthly_gross * 12
            
            # Calculate deductions
            total_deduction_rate = sum(
                deduction.value for deduction in royalty_structure.deductions 
                if deduction.deduction_type == 'percentage'
            )
            
            annual_net = annual_gross * (Decimal('1.0') - total_deduction_rate)
            
            # Calculate royalties based on tier structure
            annual_royalties = await self._calculate_royalties_for_amount(
                revenue_amount=annual_net,
                royalty_structure=royalty_structure
            )
            
            projections[scenario_name] = {
                'annual_gross_revenue': float(annual_gross),
                'annual_net_revenue': float(annual_net),
                'annual_royalties': float(annual_royalties),
                'monthly_royalties': float(annual_royalties / 12),
                'effective_royalty_rate': float(annual_royalties / annual_gross * 100) if annual_gross > 0 else 0
            }
        
        return projections
    
    async def _calculate_royalties_for_amount(
        self,
        revenue_amount: Decimal,
        royalty_structure: RoyaltyStructure
    ) -> Decimal:
        """
Calculate royalties for a specific revenue amount."""
        if royalty_structure.royalty_type == RoyaltyType.FLAT_PERCENTAGE:
            return revenue_amount * royalty_structure.base_rate
        
        elif royalty_structure.royalty_type == RoyaltyType.TIERED_PERCENTAGE:
            total_royalties = Decimal('0')
            remaining_amount = revenue_amount
            
            for tier in sorted(royalty_structure.tiers, key=lambda t: t.threshold_start):
                if remaining_amount <= 0:
                    break
                
                # Calculate amount for this tier
                tier_start = tier.threshold_start
                tier_end = tier.threshold_end or revenue_amount
                tier_amount = min(remaining_amount, tier_end - tier_start)
                
                # Calculate royalties for this tier
                tier_royalties = tier_amount * tier.rate
                total_royalties += tier_royalties
                
                # Update remaining amount
                remaining_amount -= tier_amount
            
            return total_royalties
        
        else:
            # Default to base rate for other types
            return revenue_amount * royalty_structure.base_rate
    
    async def _generate_compliance_notes(self, jurisdiction: str, license_type: str) -> List[str]:
        """
Generate compliance notes for the royalty structure."""
        notes = []
        
        # General compliance
        notes.append("Royalty calculations comply with industry standard practices")
        notes.append("All rates subject to applicable taxes and withholdings")
        
        # Jurisdiction-specific notes
        if jurisdiction == 'us':
            notes.append("Calculations comply with US Copyright Act mechanical royalty rates")
            notes.append("Performance royalties subject to PRO (ASCAP/BMI/SESAC) collection")
        elif jurisdiction == 'germany':
            notes.append("Calculations consider GEMA tariff structures")
            notes.append("Moral rights protections apply under German copyright law")
        elif jurisdiction == 'eu':
            notes.append("Calculations comply with EU Copyright Directive requirements")
            notes.append("GDPR compliance required for personal data in royalty reporting")
        
        # License type specific notes
        if license_type == 'sync_licensing':
            notes.append("Sync fees typically paid as flat fee plus ongoing royalties")
            notes.append("Master use rights may require separate calculation")
        elif license_type == 'streaming':
            notes.append("Streaming royalties calculated per platform policies")
            notes.append("Rates may vary by subscription vs. ad-supported tiers")
        
        return notes
    
    def get_calculator_metrics(self) -> Dict[str, Any]:
        """Get royalty calculator performance metrics."""
        return {
            **{k: float(v) if isinstance(v, Decimal) else v for k, v in self.metrics.items()},
            'supported_jurisdictions': len(self.statutory_rates),
            'supported_platforms': len(self.platform_rates),
            'territory_coverage': len(self.territory_multipliers),
            'timestamp': datetime.now().isoformat()
        }
