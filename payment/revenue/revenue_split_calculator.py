"""💰 Revenue Split Calculator
============================

Advanced revenue split calculation engine for complex multi-party payments,
creator collaborations, platform fees, and automated revenue distribution.

Features:
- Complex revenue sharing algorithms
- Multi-party split calculations
- Platform fee management
- Tax withholding calculations
- Tiered commission structures
- Performance-based adjustments

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta
from decimal import Decimal, ROUND_HALF_UP
import json
import uuid
from collections import defaultdict
import math

logger = logging.getLogger(__name__)


class SplitType(Enum):
    """Types of revenue splits"""
    PERCENTAGE = "percentage"
    FIXED_AMOUNT = "fixed_amount"
    TIERED_PERCENTAGE = "tiered_percentage"
    PERFORMANCE_BASED = "performance_based"
    MINIMUM_GUARANTEE = "minimum_guarantee"
    THRESHOLD_BASED = "threshold_based"


class RevenueCategory(Enum):
    """Categories of revenue"""
    CONTENT_SALES = "content_sales"
    SUBSCRIPTION = "subscription"
    LICENSING = "licensing"
    COLLABORATION = "collaboration"
    PLATFORM_FEES = "platform_fees"
    ADVERTISING = "advertising"
    TIPS = "tips"
    MERCHANDISE = "merchandise"


class PaymentTiming(Enum):
    """When payments should be made"""
    IMMEDIATE = "immediate"
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    ON_THRESHOLD = "on_threshold"
    CUSTOM = "custom"


@dataclass
class RevenueParticipant:
    """Participant in revenue sharing"""
    participant_id: str
    name: str
    role: str  # creator, collaborator, platform, service_provider
    split_type: SplitType
    split_value: Decimal  # percentage (0-100) or fixed amount
    minimum_amount: Optional[Decimal] = None
    maximum_amount: Optional[Decimal] = None
    tier_thresholds: Optional[List[Tuple[Decimal, Decimal]]] = None  # (threshold, percentage)
    performance_metrics: Optional[Dict[str, Any]] = None
    tax_withholding_rate: Decimal = Decimal('0')
    payment_details: Optional[Dict[str, str]] = None
    active: bool = True


@dataclass
class RevenueSplitRule:
    """Rule for revenue splitting"""
    rule_id: str
    name: str
    description: str
    revenue_category: RevenueCategory
    participants: List[RevenueParticipant]
    priority: int = 1
    conditions: Optional[Dict[str, Any]] = None
    effective_date: datetime = field(default_factory=datetime.now)
    expiry_date: Optional[datetime] = None
    created_by: str = ""


@dataclass
class SplitCalculation:
    """Result of revenue split calculation"""
    calculation_id: str
    total_revenue: Decimal
    currency: str
    revenue_category: RevenueCategory
    split_rule_id: str
    
    # Participant allocations
    participant_allocations: List[Dict[str, Any]]
    
    # Fees and deductions
    platform_fees: Decimal
    processing_fees: Decimal
    tax_withholdings: Decimal
    other_deductions: Decimal
    
    # Summary
    total_allocated: Decimal
    total_fees: Decimal
    net_amount: Decimal
    
    # Metadata
    calculation_date: datetime = field(default_factory=datetime.now)
    calculated_by: str = ""
    notes: Optional[str] = None


@dataclass
class RevenueTier:
    """Revenue tier for progressive splits"""
    tier_id: str
    name: str
    threshold_min: Decimal
    threshold_max: Optional[Decimal]
    creator_percentage: Decimal
    platform_percentage: Decimal
    bonus_percentage: Decimal = Decimal('0')


class RevenueSplitCalculator:
    """
    Advanced revenue split calculation engine for complex multi-party
    payments and creator monetization scenarios.
    """
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize revenue split calculator"""
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Split rules registry
        self.split_rules: Dict[str, RevenueSplitRule] = {}
        
        # Revenue tiers
        self.revenue_tiers: List[RevenueTier] = []
        
        # Performance metrics tracking
        self.performance_history: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
        
        # Tax rates by jurisdiction
        self.tax_rates: Dict[str, Decimal] = {}
        
        # Platform fee structure
        self.platform_fees = {
            'base_percentage': Decimal('2.5'),  # 2.5% base platform fee
            'processing_fee': Decimal('0.30'),  # $0.30 processing fee
            'international_fee': Decimal('1.0')  # Additional 1% for international
        }
        
        # Calculation history
        self.calculation_history: List[SplitCalculation] = []
        
        # Minimum payout thresholds
        self.min_payout_thresholds = {
            'USD': Decimal('10.00'),
            'EUR': Decimal('8.50'),
            'GBP': Decimal('7.50')
        }
    
    async def initialize(self):
        """Initialize the revenue split calculator"""
        try:
            # Load split rules
            await self._load_split_rules()
            
            # Load revenue tiers
            await self._load_revenue_tiers()
            
            # Load tax rates
            await self._load_tax_rates()
            
            self.logger.info("Revenue split calculator initialized")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize revenue split calculator: {e}")
            raise
    
    async def calculate_revenue_split(self, total_revenue: Decimal, currency: str,
                                    revenue_category: RevenueCategory,
                                    additional_context: Optional[Dict[str, Any]] = None) -> SplitCalculation:
        """
        Calculate revenue split based on rules and context
        """
        try:
            self.logger.info(f"Calculating revenue split: {total_revenue} {currency} - {revenue_category.value}")
            
            calculation_id = f"split_{uuid.uuid4().hex[:16]}"
            
            # Find applicable split rule
            split_rule = await self._find_applicable_rule(revenue_category, additional_context)
            if not split_rule:
                raise ValueError(f"No split rule found for category: {revenue_category.value}")
            
            # Calculate platform and processing fees
            platform_fees = await self._calculate_platform_fees(total_revenue, currency, additional_context)
            processing_fees = await self._calculate_processing_fees(total_revenue, currency)
            
            # Net revenue after platform fees
            net_revenue = total_revenue - platform_fees - processing_fees
            
            # Calculate participant allocations
            participant_allocations = []
            total_allocated = Decimal('0')
            total_tax_withholdings = Decimal('0')
            
            for participant in split_rule.participants:
                if not participant.active:
                    continue
                
                allocation = await self._calculate_participant_allocation(
                    participant, net_revenue, additional_context
                )
                
                # Calculate tax withholding
                tax_withholding = allocation['gross_amount'] * participant.tax_withholding_rate / 100
                allocation['tax_withholding'] = tax_withholding
                allocation['net_amount'] = allocation['gross_amount'] - tax_withholding
                
                participant_allocations.append(allocation)
                total_allocated += allocation['gross_amount']
                total_tax_withholdings += tax_withholding
            
            # Handle rounding differences
            rounding_difference = net_revenue - total_allocated
            if rounding_difference != 0:
                # Add to platform allocation or adjust largest participant
                if participant_allocations:
                    largest_allocation = max(participant_allocations, key=lambda x: x['gross_amount'])
                    largest_allocation['gross_amount'] += rounding_difference
                    largest_allocation['net_amount'] += rounding_difference
                    total_allocated += rounding_difference
            
            calculation = SplitCalculation(
                calculation_id=calculation_id,
                total_revenue=total_revenue,
                currency=currency,
                revenue_category=revenue_category,
                split_rule_id=split_rule.rule_id,
                participant_allocations=participant_allocations,
                platform_fees=platform_fees,
                processing_fees=processing_fees,
                tax_withholdings=total_tax_withholdings,
                other_deductions=Decimal('0'),
                total_allocated=total_allocated,
                total_fees=platform_fees + processing_fees,
                net_amount=total_allocated - total_tax_withholdings
            )
            
            # Store calculation
            self.calculation_history.append(calculation)
            
            self.logger.info(f"Revenue split calculated: {calculation_id}")
            
            return calculation
            
        except Exception as e:
            self.logger.error(f"Revenue split calculation failed: {e}")
            raise
    
    async def _find_applicable_rule(self, revenue_category: RevenueCategory, 
                                  context: Optional[Dict[str, Any]] = None) -> Optional[RevenueSplitRule]:
        """Find applicable split rule for revenue category and context"""
        applicable_rules = []
        
        for rule in self.split_rules.values():
            if rule.revenue_category != revenue_category:
                continue
            
            # Check if rule is active
            now = datetime.now()
            if rule.expiry_date and now > rule.expiry_date:
                continue
            if now < rule.effective_date:
                continue
            
            # Check conditions if specified
            if rule.conditions and context:
                if not await self._evaluate_rule_conditions(rule.conditions, context):
                    continue
            
            applicable_rules.append(rule)
        
        if not applicable_rules:
            return None
        
        # Return highest priority rule
        return max(applicable_rules, key=lambda r: r.priority)
    
    async def _evaluate_rule_conditions(self, conditions: Dict[str, Any], 
                                      context: Dict[str, Any]) -> bool:
        """Evaluate if rule conditions are met"""
        for condition_key, condition_value in conditions.items():
            context_value = context.get(condition_key)
            
            if isinstance(condition_value, dict):
                # Handle range conditions
                if 'min' in condition_value:
                    if context_value < condition_value['min']:
                        return False
                if 'max' in condition_value:
                    if context_value > condition_value['max']:
                        return False
            elif isinstance(condition_value, list):
                # Handle inclusion conditions
                if context_value not in condition_value:
                    return False
            else:
                # Handle exact match conditions
                if context_value != condition_value:
                    return False
        
        return True
    
    async def _calculate_platform_fees(self, revenue: Decimal, currency: str,
                                     context: Optional[Dict[str, Any]] = None) -> Decimal:
        """Calculate platform fees"""
        base_fee = revenue * self.platform_fees['base_percentage'] / 100
        
        # Add international fee if applicable
        is_international = context and context.get('is_international', False)
        if is_international:
            international_fee = revenue * self.platform_fees['international_fee'] / 100
            base_fee += international_fee
        
        return base_fee.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
    
    async def _calculate_processing_fees(self, revenue: Decimal, currency: str) -> Decimal:
        """Calculate payment processing fees"""
        processing_fee = self.platform_fees['processing_fee']
        
        # Convert to currency if needed
        if currency != 'USD':
            # Simplified conversion - in practice, use real exchange rates
            conversion_rates = {'EUR': Decimal('0.85'), 'GBP': Decimal('0.75')}
            rate = conversion_rates.get(currency, Decimal('1.0'))
            processing_fee = processing_fee * rate
        
        return processing_fee.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
    
    async def _calculate_participant_allocation(self, participant: RevenueParticipant,
                                              net_revenue: Decimal,
                                              context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Calculate allocation for a specific participant"""
        allocation = {
            'participant_id': participant.participant_id,
            'participant_name': participant.name,
            'participant_role': participant.role,
            'split_type': participant.split_type.value,
            'gross_amount': Decimal('0'),
            'calculation_details': {}
        }
        
        if participant.split_type == SplitType.PERCENTAGE:
            # Simple percentage split
            gross_amount = net_revenue * participant.split_value / 100
            allocation['calculation_details']['percentage'] = float(participant.split_value)
            
        elif participant.split_type == SplitType.FIXED_AMOUNT:
            # Fixed amount
            gross_amount = participant.split_value
            allocation['calculation_details']['fixed_amount'] = float(participant.split_value)
            
        elif participant.split_type == SplitType.TIERED_PERCENTAGE:
            # Tiered percentage based on revenue amount
            gross_amount = await self._calculate_tiered_amount(participant, net_revenue)
            
        elif participant.split_type == SplitType.PERFORMANCE_BASED:
            # Performance-based calculation
            gross_amount = await self._calculate_performance_based_amount(
                participant, net_revenue, context
            )
            
        elif participant.split_type == SplitType.MINIMUM_GUARANTEE:
            # Minimum guarantee with percentage upside
            percentage_amount = net_revenue * participant.split_value / 100
            guaranteed_amount = participant.minimum_amount or Decimal('0')
            gross_amount = max(percentage_amount, guaranteed_amount)
            
        elif participant.split_type == SplitType.THRESHOLD_BASED:
            # Only pay if revenue exceeds threshold
            threshold = participant.minimum_amount or Decimal('0')
            if net_revenue >= threshold:
                gross_amount = net_revenue * participant.split_value / 100
            else:
                gross_amount = Decimal('0')
        
        else:
            gross_amount = Decimal('0')
        
        # Apply minimum and maximum limits
        if participant.minimum_amount:
            gross_amount = max(gross_amount, participant.minimum_amount)
        if participant.maximum_amount:
            gross_amount = min(gross_amount, participant.maximum_amount)
        
        allocation['gross_amount'] = gross_amount.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
        
        return allocation
    
    async def _calculate_tiered_amount(self, participant: RevenueParticipant, 
                                     net_revenue: Decimal) -> Decimal:
        """Calculate tiered percentage amount"""
        if not participant.tier_thresholds:
            return Decimal('0')
        
        total_amount = Decimal('0')
        remaining_revenue = net_revenue
        
        # Sort tiers by threshold
        sorted_tiers = sorted(participant.tier_thresholds, key=lambda x: x[0])
        
        for i, (threshold, percentage) in enumerate(sorted_tiers):
            if remaining_revenue <= 0:
                break
            
            # Calculate tier range
            tier_start = threshold
            tier_end = sorted_tiers[i + 1][0] if i + 1 < len(sorted_tiers) else None
            
            if net_revenue <= tier_start:
                continue
            
            # Calculate amount in this tier
            tier_revenue = remaining_revenue
            if tier_end:
                tier_revenue = min(remaining_revenue, tier_end - tier_start)
            
            tier_amount = tier_revenue * percentage / 100
            total_amount += tier_amount
            remaining_revenue -= tier_revenue
        
        return total_amount
    
    async def _calculate_performance_based_amount(self, participant: RevenueParticipant,
                                                net_revenue: Decimal,
                                                context: Optional[Dict[str, Any]] = None) -> Decimal:
        """Calculate performance-based amount"""
        if not participant.performance_metrics or not context:
            # Fallback to percentage
            return net_revenue * participant.split_value / 100
        
        base_amount = net_revenue * participant.split_value / 100
        
        # Apply performance multipliers
        performance_multiplier = Decimal('1.0')
        
        for metric, config in participant.performance_metrics.items():
            actual_value = context.get(metric, 0)
            target_value = config.get('target', 0)
            multiplier_rate = config.get('multiplier_rate', 0.1)
            
            if actual_value > target_value:
                # Bonus for exceeding target
                excess_ratio = (actual_value - target_value) / target_value
                performance_multiplier += Decimal(str(excess_ratio * multiplier_rate))
        
        # Cap performance multiplier
        performance_multiplier = min(performance_multiplier, Decimal('2.0'))  # Max 2x
        
        return base_amount * performance_multiplier
    
    async def create_split_rule(self, rule_data: Dict[str, Any]) -> RevenueSplitRule:
        """Create a new revenue split rule"""
        try:
            rule_id = f"rule_{uuid.uuid4().hex[:16]}"
            
            participants = []
            for p_data in rule_data.get('participants', []):
                participant = RevenueParticipant(
                    participant_id=p_data['participant_id'],
                    name=p_data['name'],
                    role=p_data['role'],
                    split_type=SplitType(p_data['split_type']),
                    split_value=Decimal(str(p_data['split_value'])),
                    minimum_amount=Decimal(str(p_data.get('minimum_amount', 0))) if p_data.get('minimum_amount') else None,
                    maximum_amount=Decimal(str(p_data.get('maximum_amount', 0))) if p_data.get('maximum_amount') else None,
                    tier_thresholds=p_data.get('tier_thresholds'),
                    performance_metrics=p_data.get('performance_metrics'),
                    tax_withholding_rate=Decimal(str(p_data.get('tax_withholding_rate', 0))),
                    payment_details=p_data.get('payment_details')
                )
                participants.append(participant)
            
            rule = RevenueSplitRule(
                rule_id=rule_id,
                name=rule_data['name'],
                description=rule_data['description'],
                revenue_category=RevenueCategory(rule_data['revenue_category']),
                participants=participants,
                priority=rule_data.get('priority', 1),
                conditions=rule_data.get('conditions'),
                effective_date=datetime.fromisoformat(rule_data.get('effective_date', datetime.now().isoformat())),
                expiry_date=datetime.fromisoformat(rule_data['expiry_date']) if rule_data.get('expiry_date') else None,
                created_by=rule_data.get('created_by', '')
            )
            
            # Validate rule
            await self._validate_split_rule(rule)
            
            self.split_rules[rule_id] = rule
            
            self.logger.info(f"Created split rule: {rule_id} - {rule.name}")
            
            return rule
            
        except Exception as e:
            self.logger.error(f"Failed to create split rule: {e}")
            raise
    
    async def _validate_split_rule(self, rule: RevenueSplitRule):
        """Validate split rule configuration"""
        total_percentage = Decimal('0')
        
        for participant in rule.participants:
            if participant.split_type == SplitType.PERCENTAGE:
                total_percentage += participant.split_value
        
        # Allow up to 100% for percentage splits (platform fees are separate)
        if total_percentage > 100:
            raise ValueError(f"Total percentage splits exceed 100%: {total_percentage}%")
        
        # Check for duplicate participants
        participant_ids = [p.participant_id for p in rule.participants]
        if len(participant_ids) != len(set(participant_ids)):
            raise ValueError("Duplicate participants in split rule")
    
    async def get_participant_earnings(self, participant_id: str, 
                                     start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        """Get earnings summary for a participant"""
        try:
            earnings = {
                'participant_id': participant_id,
                'period_start': start_date.isoformat(),
                'period_end': end_date.isoformat(),
                'total_gross': Decimal('0'),
                'total_net': Decimal('0'),
                'total_tax_withheld': Decimal('0'),
                'transaction_count': 0,
                'earnings_by_category': defaultdict(lambda: Decimal('0')),
                'transactions': []
            }
            
            for calculation in self.calculation_history:
                if not (start_date <= calculation.calculation_date <= end_date):
                    continue
                
                for allocation in calculation.participant_allocations:
                    if allocation['participant_id'] == participant_id:
                        earnings['total_gross'] += allocation['gross_amount']
                        earnings['total_net'] += allocation['net_amount']
                        earnings['total_tax_withheld'] += allocation.get('tax_withholding', Decimal('0'))
                        earnings['transaction_count'] += 1
                        
                        category = calculation.revenue_category.value
                        earnings['earnings_by_category'][category] += allocation['gross_amount']
                        
                        earnings['transactions'].append({
                            'calculation_id': calculation.calculation_id,
                            'date': calculation.calculation_date.isoformat(),
                            'category': category,
                            'gross_amount': float(allocation['gross_amount']),
                            'net_amount': float(allocation['net_amount'])
                        })
            
            # Convert defaultdict to regular dict for JSON serialization
            earnings['earnings_by_category'] = dict(earnings['earnings_by_category'])
            
            return earnings
            
        except Exception as e:
            self.logger.error(f"Failed to get participant earnings: {e}")
            raise
    
    async def simulate_revenue_split(self, revenue_amount: Decimal, currency: str,
                                   category: RevenueCategory, 
                                   context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Simulate revenue split without saving the calculation"""
        try:
            # Create temporary calculation
            calculation = await self.calculate_revenue_split(
                revenue_amount, currency, category, context
            )
            
            # Remove from history (simulation only)
            if self.calculation_history and self.calculation_history[-1].calculation_id == calculation.calculation_id:
                self.calculation_history.pop()
            
            # Return simulation results
            return {
                'total_revenue': float(calculation.total_revenue),
                'currency': calculation.currency,
                'platform_fees': float(calculation.platform_fees),
                'processing_fees': float(calculation.processing_fees),
                'net_amount': float(calculation.net_amount),
                'participant_allocations': [
                    {
                        'participant_name': alloc['participant_name'],
                        'role': alloc['participant_role'],
                        'gross_amount': float(alloc['gross_amount']),
                        'net_amount': float(alloc['net_amount'])
                    }
                    for alloc in calculation.participant_allocations
                ]
            }
            
        except Exception as e:
            self.logger.error(f"Revenue split simulation failed: {e}")
            raise
    
    async def _load_split_rules(self):
        """Load split rules from configuration"""
        # Default split rules for different revenue categories
        default_rules = [
            {
                'name': 'Content Sales - Standard Split',
                'description': 'Standard revenue split for content sales',
                'revenue_category': 'content_sales',
                'participants': [
                    {
                        'participant_id': 'creator',
                        'name': 'Content Creator',
                        'role': 'creator',
                        'split_type': 'percentage',
                        'split_value': 70  # 70% to creator
                    },
                    {
                        'participant_id': 'platform',
                        'name': 'Platform',
                        'role': 'platform',
                        'split_type': 'percentage',
                        'split_value': 30  # 30% to platform
                    }
                ]
            },
            {
                'name': 'Collaboration - Equal Split',
                'description': 'Equal split for collaborations',
                'revenue_category': 'collaboration',
                'participants': [
                    {
                        'participant_id': 'creator_1',
                        'name': 'Primary Creator',
                        'role': 'creator',
                        'split_type': 'percentage',
                        'split_value': 40
                    },
                    {
                        'participant_id': 'creator_2',
                        'name': 'Collaborator',
                        'role': 'collaborator',
                        'split_type': 'percentage',
                        'split_value': 40
                    },
                    {
                        'participant_id': 'platform',
                        'name': 'Platform',
                        'role': 'platform',
                        'split_type': 'percentage',
                        'split_value': 20
                    }
                ]
            }
        ]
        
        for rule_data in default_rules:
            try:
                await self.create_split_rule(rule_data)
            except Exception as e:
                self.logger.error(f"Failed to load default rule: {e}")
    
    async def _load_revenue_tiers(self):
        """Load revenue tier configurations"""
        self.revenue_tiers = [
            RevenueTier(
                tier_id='bronze',
                name='Bronze Tier',
                threshold_min=Decimal('0'),
                threshold_max=Decimal('1000'),
                creator_percentage=Decimal('60'),
                platform_percentage=Decimal('40')
            ),
            RevenueTier(
                tier_id='silver',
                name='Silver Tier',
                threshold_min=Decimal('1000'),
                threshold_max=Decimal('5000'),
                creator_percentage=Decimal('70'),
                platform_percentage=Decimal('30')
            ),
            RevenueTier(
                tier_id='gold',
                name='Gold Tier',
                threshold_min=Decimal('5000'),
                threshold_max=None,
                creator_percentage=Decimal('80'),
                platform_percentage=Decimal('20'),
                bonus_percentage=Decimal('5')
            )
        ]
    
    async def _load_tax_rates(self):
        """Load tax withholding rates by jurisdiction"""
        self.tax_rates = {
            'US': Decimal('24'),     # 24% federal withholding
            'UK': Decimal('20'),     # 20% basic rate
            'DE': Decimal('26.375'), # Solidarity surcharge included
            'FR': Decimal('30'),     # Non-resident rate
            'CA': Decimal('25'),     # Non-resident rate
            'AU': Decimal('32.5'),   # Non-resident rate
        }


# Export main classes
__all__ = [
    "RevenueSplitCalculator",
    "SplitCalculation",
    "RevenueParticipant",
    "RevenueSplitRule",
    "RevenueTier",
    "SplitType",
    "RevenueCategory",
    "PaymentTiming"
]