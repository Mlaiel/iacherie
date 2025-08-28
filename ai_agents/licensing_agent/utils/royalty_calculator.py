"""
Royalty Calculator - Advanced Revenue Distribution & Payment Processing System

Comprehensive royalty calculation, revenue distribution, and automated payment processing
for multi-party content licensing across all platforms and territories.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️  IMPORTANT LEGAL NOTICE:
This code and concept are the exclusive intellectual property of Fahed Mlaiel.
Any unauthorized use, copying, distribution, or commercialization without explicit written permission is strictly prohibited.
Contact: mlaiel@live.de for licensing inquiries.

Team Specialties:
- Lead AI Developer & Backend Senior Engineer
- Machine Learning Engineer & Audio Processing Specialist  
- Database Administrator & Security Expert
- Microservices Architect & DevOps Engineer
- AI Prompt Engineer & Content Protection Specialist
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
from decimal import Decimal, ROUND_HALF_UP
import json
import uuid
import numpy as np

from ...core.exceptions import RoyaltyError, PaymentError
from ...database.models import RoyaltyStatement, Payment, License
from ...integrations.payment.processors import (
    StripeProcessor, PayPalProcessor, CryptocurrencyProcessor
)
from ...integrations.banking.swift import SwiftTransferAPI
from ...integrations.tax.calculators import TaxCalculator
from ...utils.currency_converter import CurrencyConverter
from ...utils.fraud_detector import FraudDetector

logger = logging.getLogger(__name__)

class RoyaltyModel(Enum):
    """Types of royalty calculation models"""
    PERCENTAGE = "percentage"
    FIXED_RATE = "fixed_rate"
    TIERED = "tiered"
    PERFORMANCE = "performance"
    HYBRID = "hybrid"
    WATERFALL = "waterfall"

class PaymentMethod(Enum):
    """Available payment methods"""
    BANK_TRANSFER = "bank_transfer"
    PAYPAL = "paypal"
    STRIPE = "stripe"
    CRYPTOCURRENCY = "cryptocurrency"
    CHECK = "check"
    WIRE_TRANSFER = "wire_transfer"

class PaymentStatus(Enum):
    """Payment processing status"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    DISPUTED = "disputed"
    REFUNDED = "refunded"

class RevenueSource(Enum):
    """Sources of revenue"""
    STREAMING = "streaming"
    DOWNLOAD = "download"
    SYNC_LICENSE = "sync_license"
    PERFORMANCE = "performance"
    MECHANICAL = "mechanical"
    ADVERTISING = "advertising"
    SUBSCRIPTION = "subscription"
    MERCHANDISE = "merchandise"

@dataclass
class UsageMetrics:
    """Content usage metrics for royalty calculation"""
    plays: int = 0
    downloads: int = 0
    streams: int = 0
    views: int = 0
    impressions: int = 0
    clicks: int = 0
    shares: int = 0
    duration_seconds: int = 0
    unique_users: int = 0
    geography: Dict[str, int] = field(default_factory=dict)
    platforms: Dict[str, int] = field(default_factory=dict)
    demographics: Dict[str, Any] = field(default_factory=dict)

@dataclass
class RevenueData:
    """Revenue data for royalty calculation"""
    source: RevenueSource
    gross_revenue: Decimal
    platform_fees: Decimal
    taxes: Decimal
    net_revenue: Decimal
    currency: str
    period_start: datetime
    period_end: datetime
    exchange_rate: Decimal = Decimal("1.0")
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class RoyaltyCalculationResult:
    """Result of royalty calculation"""
    calculation_id: str
    content_id: str
    license_id: str
    rightholder_id: str
    period_start: datetime
    period_end: datetime
    usage_metrics: UsageMetrics
    revenue_data: List[RevenueData]
    royalty_rate: Decimal
    gross_royalty: Decimal
    deductions: Dict[str, Decimal]
    net_royalty: Decimal
    currency: str
    calculation_method: RoyaltyModel
    breakdown: Dict[str, Any]
    created_at: datetime = field(default_factory=datetime.utcnow)

@dataclass
class PaymentInstruction:
    """Payment processing instruction"""
    payment_id: str
    recipient_id: str
    recipient_info: Dict[str, Any]
    amount: Decimal
    currency: str
    payment_method: PaymentMethod
    reference: str
    metadata: Dict[str, Any]
    schedule_date: Optional[datetime] = None
    recurring: bool = False

class RoyaltyCalculator:
    """
    Advanced Royalty Calculation Engine
    
    Handles complex royalty calculations with multiple revenue streams,
    tiered rates, territorial adjustments, and multi-party distributions.
    """
    
    def __init__(self):
        self.currency_converter = CurrencyConverter()
        self.tax_calculator = TaxCalculator()
        self.fraud_detector = FraudDetector()
        
        # Calculation models
        self.calculation_models = {}
        self.rate_tables = {}
        self.territorial_adjustments = {}
        self.platform_rates = {}
        
        # Performance metrics
        self.metrics = {
            "calculations_performed": 0,
            "total_royalties_calculated": Decimal("0.00"),
            "average_calculation_time": 0.0,
            "accuracy_score": 1.0
        }

    async def initialize(self):
        """Initialize royalty calculator with rate tables and models"""
        await self._load_rate_tables()
        await self._load_calculation_models()
        await self._load_territorial_adjustments()
        await self._load_platform_rates()

    async def calculate_royalties(
        self,
        content_id: str,
        license_id: str,
        usage_metrics: UsageMetrics,
        revenue_data: List[RevenueData],
        calculation_period: Tuple[datetime, datetime],
        royalty_model: RoyaltyModel = RoyaltyModel.PERCENTAGE,
        base_rate: Optional[Decimal] = None
    ) -> RoyaltyCalculationResult:
        """
        Calculate comprehensive royalties for content usage
        
        Args:
            content_id: Content identifier
            license_id: License agreement identifier
            usage_metrics: Usage statistics and metrics
            revenue_data: Revenue information by source
            calculation_period: Start and end dates for calculation
            royalty_model: Calculation model to use
            base_rate: Base royalty rate (if applicable)
            
        Returns:
            Detailed royalty calculation result
        """
        try:
            calculation_id = str(uuid.uuid4())
            period_start, period_end = calculation_period
            
            # Get license details
            license_info = await self._get_license_details(license_id)
            if not license_info:
                raise RoyaltyError(f"License not found: {license_id}")
            
            # Determine royalty rate
            effective_rate = await self._determine_royalty_rate(
                license_info, royalty_model, base_rate, usage_metrics
            )
            
            # Process revenue data
            processed_revenue = await self._process_revenue_data(
                revenue_data, license_info["territory"], license_info["currency"]
            )
            
            # Calculate gross royalties by model
            if royalty_model == RoyaltyModel.PERCENTAGE:
                gross_royalty = await self._calculate_percentage_royalty(
                    processed_revenue, effective_rate, usage_metrics
                )
            elif royalty_model == RoyaltyModel.TIERED:
                gross_royalty = await self._calculate_tiered_royalty(
                    processed_revenue, usage_metrics, license_info
                )
            elif royalty_model == RoyaltyModel.PERFORMANCE:
                gross_royalty = await self._calculate_performance_royalty(
                    processed_revenue, usage_metrics, license_info
                )
            elif royalty_model == RoyaltyModel.WATERFALL:
                gross_royalty = await self._calculate_waterfall_royalty(
                    processed_revenue, usage_metrics, license_info
                )
            else:
                gross_royalty = await self._calculate_hybrid_royalty(
                    processed_revenue, usage_metrics, license_info, effective_rate
                )
            
            # Apply deductions
            deductions = await self._calculate_deductions(
                gross_royalty, license_info, processed_revenue
            )
            
            # Calculate net royalty
            net_royalty = gross_royalty - sum(deductions.values())
            
            # Generate calculation breakdown
            breakdown = await self._generate_calculation_breakdown(
                usage_metrics, processed_revenue, effective_rate, gross_royalty, deductions
            )
            
            # Create calculation result
            result = RoyaltyCalculationResult(
                calculation_id=calculation_id,
                content_id=content_id,
                license_id=license_id,
                rightholder_id=license_info["rightholder_id"],
                period_start=period_start,
                period_end=period_end,
                usage_metrics=usage_metrics,
                revenue_data=processed_revenue,
                royalty_rate=effective_rate,
                gross_royalty=gross_royalty,
                deductions=deductions,
                net_royalty=max(net_royalty, Decimal("0.00")),  # Ensure non-negative
                currency=license_info["currency"],
                calculation_method=royalty_model,
                breakdown=breakdown
            )
            
            # Fraud detection
            fraud_check = await self._check_for_fraud(result, usage_metrics, revenue_data)
            if fraud_check["suspicious"]:
                result.breakdown["fraud_alerts"] = fraud_check["alerts"]
            
            # Store calculation result
            await self._store_calculation_result(result)
            
            # Update metrics
            self.metrics["calculations_performed"] += 1
            self.metrics["total_royalties_calculated"] += net_royalty
            
            return result
            
        except Exception as e:
            logger.error(f"Error calculating royalties: {str(e)}")
            raise RoyaltyError(f"Failed to calculate royalties: {str(e)}")

    async def calculate_multi_party_distribution(
        self,
        content_id: str,
        total_royalty: Decimal,
        ownership_structure: List[Dict[str, Any]],
        distribution_rules: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Calculate royalty distribution among multiple rights holders
        
        Args:
            content_id: Content identifier
            total_royalty: Total royalty amount to distribute
            ownership_structure: Rights holders and their ownership percentages
            distribution_rules: Rules for distribution calculation
            
        Returns:
            List of individual royalty allocations
        """
        try:
            distributions = []
            remaining_royalty = total_royalty
            
            # Sort by priority if specified
            sorted_owners = sorted(
                ownership_structure,
                key=lambda x: x.get("priority", 999)
            )
            
            for owner_info in sorted_owners:
                # Calculate owner's share
                if distribution_rules.get("method") == "waterfall":
                    owner_royalty = await self._calculate_waterfall_share(
                        remaining_royalty, owner_info, distribution_rules
                    )
                    remaining_royalty -= owner_royalty
                else:
                    # Percentage-based distribution
                    ownership_percent = Decimal(str(owner_info["ownership_percentage"])) / 100
                    owner_royalty = total_royalty * ownership_percent
                
                # Apply minimum/maximum limits
                if "min_amount" in owner_info:
                    owner_royalty = max(owner_royalty, Decimal(str(owner_info["min_amount"])))
                if "max_amount" in owner_info:
                    owner_royalty = min(owner_royalty, Decimal(str(owner_info["max_amount"])))
                
                # Round to appropriate precision
                owner_royalty = owner_royalty.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
                
                distribution = {
                    "rightholder_id": owner_info["rightholder_id"],
                    "rightholder_name": owner_info.get("name", "Unknown"),
                    "ownership_percentage": owner_info["ownership_percentage"],
                    "royalty_amount": owner_royalty,
                    "currency": distribution_rules.get("currency", "EUR"),
                    "payment_info": owner_info.get("payment_info", {}),
                    "tax_info": owner_info.get("tax_info", {}),
                    "distribution_id": str(uuid.uuid4())
                }
                
                distributions.append(distribution)
            
            # Validate total distribution
            total_distributed = sum(d["royalty_amount"] for d in distributions)
            if abs(total_distributed - total_royalty) > Decimal("0.01"):
                logger.warning(f"Distribution mismatch: {total_distributed} vs {total_royalty}")
                # Adjust largest distribution to match total
                if distributions:
                    largest_dist = max(distributions, key=lambda x: x["royalty_amount"])
                    adjustment = total_royalty - total_distributed
                    largest_dist["royalty_amount"] += adjustment
            
            return distributions
            
        except Exception as e:
            logger.error(f"Error calculating multi-party distribution: {str(e)}")
            raise RoyaltyError(f"Failed to calculate distribution: {str(e)}")

    async def generate_royalty_statement(
        self,
        rightholder_id: str,
        period_start: datetime,
        period_end: datetime,
        include_details: bool = True
    ) -> Dict[str, Any]:
        """
        Generate comprehensive royalty statement for rights holder
        
        Args:
            rightholder_id: Rights holder identifier
            period_start: Statement period start
            period_end: Statement period end
            include_details: Whether to include detailed breakdowns
            
        Returns:
            Complete royalty statement
        """
        try:
            # Get all calculations for period
            calculations = await self._get_calculations_for_period(
                rightholder_id, period_start, period_end
            )
            
            # Aggregate totals
            total_gross = sum(calc.gross_royalty for calc in calculations)
            total_deductions = sum(
                sum(calc.deductions.values()) for calc in calculations
            )
            total_net = sum(calc.net_royalty for calc in calculations)
            
            # Group by content and revenue source
            content_breakdown = {}
            source_breakdown = {}
            
            for calc in calculations:
                # Content breakdown
                if calc.content_id not in content_breakdown:
                    content_breakdown[calc.content_id] = {
                        "content_id": calc.content_id,
                        "gross_royalty": Decimal("0.00"),
                        "net_royalty": Decimal("0.00"),
                        "calculations": []
                    }
                
                content_breakdown[calc.content_id]["gross_royalty"] += calc.gross_royalty
                content_breakdown[calc.content_id]["net_royalty"] += calc.net_royalty
                
                if include_details:
                    content_breakdown[calc.content_id]["calculations"].append(calc.__dict__)
                
                # Source breakdown
                for revenue in calc.revenue_data:
                    source = revenue.source.value
                    if source not in source_breakdown:
                        source_breakdown[source] = Decimal("0.00")
                    source_breakdown[source] += revenue.net_revenue
            
            # Calculate period-over-period changes
            previous_period_end = period_start
            previous_period_start = period_start - (period_end - period_start)
            previous_calculations = await self._get_calculations_for_period(
                rightholder_id, previous_period_start, previous_period_end
            )
            previous_total = sum(calc.net_royalty for calc in previous_calculations)
            
            period_change = ((total_net - previous_total) / previous_total * 100) if previous_total > 0 else 0
            
            # Generate payment forecast
            payment_forecast = await self._generate_payment_forecast(
                total_net, rightholder_id
            )
            
            statement = {
                "statement_id": str(uuid.uuid4()),
                "rightholder_id": rightholder_id,
                "period": {
                    "start": period_start,
                    "end": period_end
                },
                "summary": {
                    "total_gross_royalties": float(total_gross),
                    "total_deductions": float(total_deductions),
                    "total_net_royalties": float(total_net),
                    "currency": "EUR",
                    "calculation_count": len(calculations),
                    "period_change_percent": float(period_change)
                },
                "content_breakdown": list(content_breakdown.values()),
                "source_breakdown": {k: float(v) for k, v in source_breakdown.items()},
                "payment_forecast": payment_forecast,
                "generated_at": datetime.utcnow(),
                "statement_format": "comprehensive"
            }
            
            return statement
            
        except Exception as e:
            logger.error(f"Error generating royalty statement: {str(e)}")
            raise RoyaltyError(f"Failed to generate statement: {str(e)}")

    async def _calculate_percentage_royalty(
        self,
        revenue_data: List[RevenueData],
        royalty_rate: Decimal,
        usage_metrics: UsageMetrics
    ) -> Decimal:
        """Calculate royalties using percentage model"""
        total_royalty = Decimal("0.00")
        
        for revenue in revenue_data:
            # Apply base percentage
            base_royalty = revenue.net_revenue * royalty_rate
            
            # Apply usage-based adjustments
            usage_multiplier = await self._calculate_usage_multiplier(
                usage_metrics, revenue.source
            )
            
            adjusted_royalty = base_royalty * usage_multiplier
            total_royalty += adjusted_royalty
        
        return total_royalty

    async def _calculate_tiered_royalty(
        self,
        revenue_data: List[RevenueData],
        usage_metrics: UsageMetrics,
        license_info: Dict[str, Any]
    ) -> Decimal:
        """Calculate royalties using tiered model"""
        total_royalty = Decimal("0.00")
        
        # Get tier structure
        tiers = license_info.get("tier_structure", [
            {"threshold": 0, "rate": 0.10},
            {"threshold": 1000, "rate": 0.12},
            {"threshold": 10000, "rate": 0.15}
        ])
        
        total_revenue = sum(r.net_revenue for r in revenue_data)
        
        # Apply tiered rates
        remaining_revenue = total_revenue
        for i, tier in enumerate(tiers):
            if remaining_revenue <= 0:
                break
                
            # Determine tier amount
            if i + 1 < len(tiers):
                next_threshold = Decimal(str(tiers[i + 1]["threshold"]))
                current_threshold = Decimal(str(tier["threshold"]))
                tier_amount = min(remaining_revenue, next_threshold - current_threshold)
            else:
                tier_amount = remaining_revenue
            
            # Calculate tier royalty
            tier_rate = Decimal(str(tier["rate"]))
            tier_royalty = tier_amount * tier_rate
            total_royalty += tier_royalty
            
            remaining_revenue -= tier_amount
        
        return total_royalty

    async def _calculate_deductions(
        self,
        gross_royalty: Decimal,
        license_info: Dict[str, Any],
        revenue_data: List[RevenueData]
    ) -> Dict[str, Decimal]:
        """Calculate all applicable deductions"""
        deductions = {}
        
        # Platform fees
        if license_info.get("platform_fee_passthrough", False):
            platform_fees = sum(r.platform_fees for r in revenue_data)
            platform_fee_share = platform_fees * license_info.get("platform_fee_share", Decimal("1.0"))
            deductions["platform_fees"] = platform_fee_share
        
        # Administrative fees
        if "admin_fee_rate" in license_info:
            admin_fee = gross_royalty * Decimal(str(license_info["admin_fee_rate"]))
            deductions["admin_fees"] = admin_fee
        
        # Taxes (if applicable)
        if license_info.get("tax_withholding", False):
            tax_rate = Decimal(str(license_info.get("tax_rate", 0.0)))
            tax_amount = gross_royalty * tax_rate
            deductions["taxes"] = tax_amount
        
        # Currency conversion fees
        conversion_fees = Decimal("0.00")
        for revenue in revenue_data:
            if revenue.currency != license_info["currency"]:
                conversion_fee = revenue.net_revenue * Decimal("0.025")  # 2.5% conversion fee
                conversion_fees += conversion_fee
        if conversion_fees > 0:
            deductions["currency_conversion"] = conversion_fees
        
        # Minimum deduction amounts
        for deduction_type, amount in deductions.items():
            deductions[deduction_type] = amount.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        
        return deductions

    async def _load_rate_tables(self):
        """Load royalty rate tables"""
        self.rate_tables = {
            "streaming": {
                "spotify": Decimal("0.08"),
                "apple_music": Decimal("0.09"),
                "youtube_music": Decimal("0.07"),
                "default": Decimal("0.08")
            },
            "download": {
                "itunes": Decimal("0.12"),
                "amazon": Decimal("0.11"),
                "default": Decimal("0.10")
            },
            "sync": {
                "tv": Decimal("0.15"),
                "film": Decimal("0.20"),
                "advertising": Decimal("0.25"),
                "default": Decimal("0.15")
            }
        }

    async def _load_territorial_adjustments(self):
        """Load territorial adjustment factors"""
        self.territorial_adjustments = {
            "US": Decimal("1.0"),
            "EU": Decimal("0.95"),
            "UK": Decimal("0.92"),
            "JP": Decimal("1.05"),
            "default": Decimal("0.90")
        }


class RevenueDistributor:
    """
    Revenue Distribution and Payment Processing System
    """
    
    def __init__(self):
        self.payment_processors = {
            PaymentMethod.STRIPE: StripeProcessor(),
            PaymentMethod.PAYPAL: PayPalProcessor(),
            PaymentMethod.CRYPTOCURRENCY: CryptocurrencyProcessor()
        }
        self.swift_api = SwiftTransferAPI()
        
    async def process_royalty_payments(
        self,
        distributions: List[Dict[str, Any]],
        payment_schedule: Optional[datetime] = None
    ) -> List[Dict[str, Any]]:
        """Process royalty payments to rights holders"""
        try:
            payment_results = []
            
            for distribution in distributions:
                # Create payment instruction
                payment_instruction = PaymentInstruction(
                    payment_id=str(uuid.uuid4()),
                    recipient_id=distribution["rightholder_id"],
                    recipient_info=distribution["payment_info"],
                    amount=distribution["royalty_amount"],
                    currency=distribution["currency"],
                    payment_method=PaymentMethod(distribution["payment_info"].get("method", "bank_transfer")),
                    reference=f"Royalty-{distribution['distribution_id']}",
                    metadata=distribution,
                    schedule_date=payment_schedule
                )
                
                # Process payment
                result = await self._process_payment(payment_instruction)
                payment_results.append(result)
            
            return payment_results
            
        except Exception as e:
            logger.error(f"Error processing royalty payments: {str(e)}")
            raise PaymentError(f"Failed to process payments: {str(e)}")
            
    async def _process_payment(self, instruction: PaymentInstruction) -> Dict[str, Any]:
        """Process individual payment"""
        try:
            processor = self.payment_processors.get(instruction.payment_method)
            if not processor:
                raise PaymentError(f"Unsupported payment method: {instruction.payment_method}")
            
            # Execute payment
            result = await processor.process_payment(
                recipient=instruction.recipient_info,
                amount=instruction.amount,
                currency=instruction.currency,
                reference=instruction.reference,
                metadata=instruction.metadata
            )
            
            return {
                "payment_id": instruction.payment_id,
                "status": result["status"],
                "transaction_id": result["transaction_id"],
                "amount": float(instruction.amount),
                "currency": instruction.currency,
                "processed_at": datetime.utcnow()
            }
            
        except Exception as e:
            logger.error(f"Error processing payment {instruction.payment_id}: {str(e)}")
            return {
                "payment_id": instruction.payment_id,
                "status": "failed",
                "error": str(e),
                "amount": float(instruction.amount),
                "currency": instruction.currency
            }
