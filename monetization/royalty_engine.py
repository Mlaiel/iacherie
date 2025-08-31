"""Royalty Engine - Advanced Royalty Calculation System
===================================================

Enterprise-grade royalty calculation and distribution system for content licensing.
Handles complex royalty calculations, multi-tier distributions, and automated payments.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: All rights reserved. Unauthorized use, reproduction, or distribution prohibited.
"""import logging
import asyncio
from typing import Dict, List, Optional, Any, Union
from datetime import datetime, timedelta
from decimal import Decimal, ROUND_HALF_UP
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)


class RoyaltyType(Enum):
    """Types of royalty calculations"""    FLAT_RATE = "flat_rate"
    PERCENTAGE = "percentage"
    TIERED = "tiered"
    USAGE_BASED = "usage_based"
    REVENUE_SHARE = "revenue_share"


class PaymentStatus(Enum):
    """Payment status for royalties"""    PENDING = "pending"
    PROCESSING = "processing"
    PAID = "paid"
    FAILED = "failed"
    DISPUTED = "disputed"


@dataclass
class RoyaltyCalculation:
    """Royalty calculation result"""    calculation_id: str
    license_id: int
    period_start: datetime
    period_end: datetime
    total_usage: int
    gross_revenue: Decimal
    royalty_rate: Decimal
    royalty_amount: Decimal
    deductions: Decimal
    net_royalty: Decimal
    currency: str
    calculation_date: datetime
    breakdown: Dict[str, Any]


@dataclass
class RoyaltyPayment:
    """Royalty payment record"""    payment_id: str
    calculation_id: str
    payee_id: int
    amount: Decimal
    currency: str
    payment_method: str
    status: PaymentStatus
    scheduled_date: datetime
    processed_date: Optional[datetime] = None
    transaction_id: Optional[str] = None
    fees: Decimal = Decimal("0.00")
    metadata: Dict[str, Any] = None


class RoyaltyEngine:
    """    Advanced royalty calculation and distribution engine
    
    Features:
    - Multiple royalty calculation methods
    - Tiered royalty structures
    - Automated deductions and fees
    - Multi-currency support
    - Payment scheduling and processing
    - Detailed reporting and analytics
    - Compliance tracking
    """    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize royalty engine"""        self.config = config or {}
        
        # Default royalty rates by usage type
        self.default_rates = {
            "stream": Decimal("0.004"),      # €0.004 per stream
            "download": Decimal("0.10"),     # €0.10 per download
            "sync": Decimal("0.15"),         # €0.15 per sync
            "commercial": Decimal("0.25"),   # €0.25 per commercial use
            "broadcast": Decimal("0.50"),    # €0.50 per broadcast
            "public_performance": Decimal("1.00")  # €1.00 per performance
        }
        
        # Deduction rates
        self.deduction_rates = {
            "platform_fee": Decimal("0.15"),        # 15% platform fee
            "payment_processing": Decimal("0.029"),  # 2.9% payment processing
            "tax_withholding": Decimal("0.19"),      # 19% VAT (German rate)
            "currency_conversion": Decimal("0.025")  # 2.5% currency conversion
        }
        
        # Tiered royalty structures
        self.tiered_structures = {
            "basic": [
                {"min_usage": 0, "max_usage": 1000, "rate": Decimal("0.003")},
                {"min_usage": 1001, "max_usage": 10000, "rate": Decimal("0.004")},
                {"min_usage": 10001, "max_usage": None, "rate": Decimal("0.005")}
            ],
            "premium": [
                {"min_usage": 0, "max_usage": 500, "rate": Decimal("0.005")},
                {"min_usage": 501, "max_usage": 5000, "rate": Decimal("0.006")},
                {"min_usage": 5001, "max_usage": None, "rate": Decimal("0.008")}
            ]
        }
        
        # Payment methods configuration
        self.payment_methods = {
            "bank_transfer": {"min_amount": Decimal("10.00"), "fee": Decimal("2.50")},
            "paypal": {"min_amount": Decimal("1.00"), "fee_rate": Decimal("0.034")},
            "stripe": {"min_amount": Decimal("0.50"), "fee_rate": Decimal("0.029")},
            "wise": {"min_amount": Decimal("5.00"), "fee_rate": Decimal("0.007")}
        }
        
        # Calculation cache and history
        self.calculation_cache: Dict[str, RoyaltyCalculation] = {}
        self.payment_history: List[RoyaltyPayment] = []
        
        logger.info("RoyaltyEngine initialized successfully")
    
    async def calculate_usage_royalty(
        self,
        license_data: Dict[str, Any],
        usage_type: str,
        usage_data: Dict[str, Any]
    ) -> Decimal:
        """        Calculate royalty for a single usage event
        
        Args:
            license_data: License information
            usage_type: Type of usage (stream, download, etc.)
            usage_data: Usage metadata and count
            
        Returns:
            Decimal: Calculated royalty amount
        """        try:
            # Get usage count
            usage_count = usage_data.get("count", 1)
            
            # Get royalty rate
            rate = await self._get_royalty_rate(license_data, usage_type, usage_data)
            
            # Calculate base royalty
            base_royalty = rate * Decimal(str(usage_count))
            
            # Apply quality multipliers
            quality_multiplier = await self._calculate_quality_multiplier(
                license_data, usage_data
            )
            
            # Apply territory multipliers
            territory_multiplier = await self._calculate_territory_multiplier(
                license_data, usage_data
            )
            
            # Calculate final royalty
            final_royalty = base_royalty * quality_multiplier * territory_multiplier
            
            logger.debug(
                f"Usage royalty calculated: {usage_type} x{usage_count} = €{final_royalty}"
            )
            
            return final_royalty.quantize(Decimal("0.0001"), rounding=ROUND_HALF_UP)
            
        except Exception as e:
            logger.error(f"Error calculating usage royalty: {e}")
            return Decimal("0.00")
    
    async def calculate_period_royalties(
        self,
        license_data: Dict[str, Any],
        usage_records: List[Dict[str, Any]],
        period_start: datetime,
        period_end: datetime
    ) -> Dict[str, Any]:
        """        Calculate royalties for a specific period
        
        Args:
            license_data: License information
            usage_records: List of usage records for the period
            period_start: Start of calculation period
            period_end: End of calculation period
            
        Returns:
            Dict: Comprehensive royalty calculation summary
        """        try:
            calculation_id = f"calc_{license_data['id']}_{period_start.strftime('%Y%m%d')}_{period_end.strftime('%Y%m%d')}"
            
            # Group usage by type
            usage_breakdown = {}
            total_usage = 0
            gross_revenue = Decimal("0.00")
            
            for record in usage_records:
                usage_type = record.get("usage_type", "stream")
                usage_count = record.get("usage_count", 1)
                royalty_amount = Decimal(str(record.get("royalty_amount", 0)))
                
                if usage_type not in usage_breakdown:
                    usage_breakdown[usage_type] = {
                        "count": 0,
                        "royalty": Decimal("0.00"),
                        "records": []
                    }
                
                usage_breakdown[usage_type]["count"] += usage_count
                usage_breakdown[usage_type]["royalty"] += royalty_amount
                usage_breakdown[usage_type]["records"].append(record)
                
                total_usage += usage_count
                gross_revenue += royalty_amount
            
            # Calculate effective royalty rate
            effective_rate = (gross_revenue / Decimal(str(total_usage))) if total_usage > 0 else Decimal("0.00")
            
            # Calculate deductions
            deductions = await self._calculate_deductions(
                license_data, gross_revenue, usage_breakdown
            )
            
            # Calculate net royalty
            net_royalty = gross_revenue - deductions["total"]
            
            # Create calculation record
            calculation = RoyaltyCalculation(
                calculation_id=calculation_id,
                license_id=license_data["id"],
                period_start=period_start,
                period_end=period_end,
                total_usage=total_usage,
                gross_revenue=gross_revenue,
                royalty_rate=effective_rate,
                royalty_amount=gross_revenue,
                deductions=deductions["total"],
                net_royalty=net_royalty,
                currency=license_data.get("currency", "EUR"),
                calculation_date=datetime.utcnow(),
                breakdown={
                    "usage_breakdown": usage_breakdown,
                    "deductions_breakdown": deductions,
                    "payment_due": net_royalty >= self._get_minimum_payment_threshold(license_data)
                }
            )
            
            # Cache calculation
            self.calculation_cache[calculation_id] = calculation
            
            return {
                "calculation_id": calculation_id,
                "total_amount": net_royalty,
                "gross_amount": gross_revenue,
                "deductions": deductions["total"],
                "usage_breakdown": usage_breakdown,
                "effective_rate": effective_rate,
                "payment_due": calculation.breakdown["payment_due"],
                "currency": calculation.currency,
                "period_days": (period_end - period_start).days
            }
            
        except Exception as e:
            logger.error(f"Error calculating period royalties: {e}")
            return {
                "error": str(e),
                "total_amount": Decimal("0.00"),
                "payment_due": False
            }
    
    async def schedule_payment(
        self,
        calculation_id: str,
        payee_id: int,
        payment_method: str,
        scheduled_date: Optional[datetime] = None
    ) -> Optional[RoyaltyPayment]:
        """        Schedule a royalty payment
        
        Args:
            calculation_id: ID of royalty calculation
            payee_id: ID of payee
            payment_method: Payment method to use
            scheduled_date: When to process payment (default: now)
            
        Returns:
            RoyaltyPayment: Payment record or None if failed
        """        try:
            if calculation_id not in self.calculation_cache:
                logger.error(f"Calculation not found: {calculation_id}")
                return None
            
            calculation = self.calculation_cache[calculation_id]
            
            # Validate payment method
            if payment_method not in self.payment_methods:
                logger.error(f"Invalid payment method: {payment_method}")
                return None
            
            # Check minimum payment amount
            min_amount = self.payment_methods[payment_method]["min_amount"]
            if calculation.net_royalty < min_amount:
                logger.warning(
                    f"Payment amount {calculation.net_royalty} below minimum {min_amount}"
                )
                return None
            
            # Calculate payment fees
            fees = await self._calculate_payment_fees(
                calculation.net_royalty, payment_method
            )
            
            # Create payment record
            payment = RoyaltyPayment(
                payment_id=f"pay_{calculation_id}_{datetime.utcnow().timestamp()}",
                calculation_id=calculation_id,
                payee_id=payee_id,
                amount=calculation.net_royalty - fees,
                currency=calculation.currency,
                payment_method=payment_method,
                status=PaymentStatus.PENDING,
                scheduled_date=scheduled_date or datetime.utcnow(),
                fees=fees,
                metadata={
                    "license_id": calculation.license_id,
                    "period": f"{calculation.period_start.date()} to {calculation.period_end.date()}",
                    "usage_count": calculation.total_usage
                }
            )
            
            # Add to payment history
            self.payment_history.append(payment)
            
            logger.info(f"Payment scheduled: {payment.payment_id} for €{payment.amount}")
            return payment
            
        except Exception as e:
            logger.error(f"Error scheduling payment: {e}")
            return None
    
    async def process_payment(self, payment_id: str) -> bool:
        """        Process a scheduled payment
        
        Args:
            payment_id: ID of payment to process
            
        Returns:
            bool: True if payment processed successfully
        """        try:
            # Find payment
            payment = None
            for p in self.payment_history:
                if p.payment_id == payment_id:
                    payment = p
                    break
            
            if not payment:
                logger.error(f"Payment not found: {payment_id}")
                return False
            
            if payment.status != PaymentStatus.PENDING:
                logger.warning(f"Payment not in pending status: {payment_id}")
                return False
            
            # Update status to processing
            payment.status = PaymentStatus.PROCESSING
            
            # Simulate payment processing (real implementation would integrate with payment providers)
            await asyncio.sleep(0.1)  # Simulate processing time
            
            # Generate transaction ID
            payment.transaction_id = f"txn_{datetime.utcnow().timestamp()}"
            payment.processed_date = datetime.utcnow()
            payment.status = PaymentStatus.PAID
            
            logger.info(f"Payment processed successfully: {payment_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error processing payment {payment_id}: {e}")
            
            # Update payment status to failed
            for p in self.payment_history:
                if p.payment_id == payment_id:
                    p.status = PaymentStatus.FAILED
                    break
            
            return False
    
    async def get_license_royalty_history(self, license_id: int) -> List[Dict[str, Any]]:
        """Get royalty history for a license"""        try:
            history = []
            
            # Get calculations for this license
            calculations = [
                calc for calc in self.calculation_cache.values()
                if calc.license_id == license_id
            ]
            
            # Sort by calculation date
            calculations.sort(key=lambda x: x.calculation_date, reverse=True)
            
            for calc in calculations:
                # Find associated payments
                payments = [
                    payment for payment in self.payment_history
                    if payment.calculation_id == calc.calculation_id
                ]
                
                history.append({
                    "calculation_id": calc.calculation_id,
                    "period": {
                        "start": calc.period_start.isoformat(),
                        "end": calc.period_end.isoformat()
                    },
                    "usage_count": calc.total_usage,
                    "gross_amount": float(calc.gross_revenue),
                    "net_amount": float(calc.net_royalty),
                    "deductions": float(calc.deductions),
                    "currency": calc.currency,
                    "calculation_date": calc.calculation_date.isoformat(),
                    "payments": [
                        {
                            "payment_id": payment.payment_id,
                            "amount": float(payment.amount),
                            "status": payment.status.value,
                            "processed_date": payment.processed_date.isoformat() if payment.processed_date else None
                        }
                        for payment in payments
                    ]
                })
            
            return history
            
        except Exception as e:
            logger.error(f"Error getting royalty history: {e}")
            return []
    
    async def _get_royalty_rate(
        self,
        license_data: Dict[str, Any],
        usage_type: str,
        usage_data: Dict[str, Any]
    ) -> Decimal:
        """Get royalty rate for usage type"""        try:
            # Check license-specific rates
            license_rates = license_data.get("royalty_rates", {})
            if usage_type in license_rates:
                return Decimal(str(license_rates[usage_type]))
            
            # Check tiered rates
            if license_data.get("royalty_structure") in self.tiered_structures:
                total_usage = usage_data.get("total_usage_to_date", 0)
                structure = self.tiered_structures[license_data["royalty_structure"]]
                
                for tier in structure:
                    if tier["min_usage"] <= total_usage:
                        if tier["max_usage"] is None or total_usage <= tier["max_usage"]:
                            return tier["rate"]
            
            # Use default rate
            return self.default_rates.get(usage_type, Decimal("0.00"))
            
        except Exception as e:
            logger.error(f"Error getting royalty rate: {e}")
            return Decimal("0.00")
    
    async def _calculate_quality_multiplier(
        self,
        license_data: Dict[str, Any],
        usage_data: Dict[str, Any]
    ) -> Decimal:
        """Calculate quality-based multiplier"""        try:
            quality_score = usage_data.get("quality_score", 1.0)
            
            if quality_score >= 0.9:
                return Decimal("1.2")  # 20% bonus for high quality
            elif quality_score >= 0.7:
                return Decimal("1.0")  # Standard rate
            else:
                return Decimal("0.8")  # 20% reduction for low quality
                
        except Exception:
            return Decimal("1.0")
    
    async def _calculate_territory_multiplier(
        self,
        license_data: Dict[str, Any],
        usage_data: Dict[str, Any]
    ) -> Decimal:
        """Calculate territory-based multiplier"""        try:
            territory = usage_data.get("territory", "unknown")
            license_territory = license_data.get("territory", "worldwide")
            
            # Premium territories
            premium_territories = ["US", "UK", "DE", "FR", "JP"]
            
            if territory in premium_territories:
                return Decimal("1.5")
            elif license_territory == "worldwide":
                return Decimal("1.2")
            else:
                return Decimal("1.0")
                
        except Exception:
            return Decimal("1.0")
    
    async def _calculate_deductions(
        self,
        license_data: Dict[str, Any],
        gross_revenue: Decimal,
        usage_breakdown: Dict[str, Any]
    ) -> Dict[str, Decimal]:
        """Calculate all deductions"""        try:
            deductions = {}
            
            # Platform fee
            platform_fee_rate = license_data.get("platform_fee_rate", self.deduction_rates["platform_fee"])
            deductions["platform_fee"] = gross_revenue * platform_fee_rate
            
            # Payment processing fee
            processing_fee_rate = self.deduction_rates["payment_processing"]
            deductions["payment_processing"] = gross_revenue * processing_fee_rate
            
            # Tax withholding (if applicable)
            if license_data.get("tax_withholding", False):
                tax_rate = license_data.get("tax_rate", self.deduction_rates["tax_withholding"])
                deductions["tax_withholding"] = gross_revenue * tax_rate
            else:
                deductions["tax_withholding"] = Decimal("0.00")
            
            # Currency conversion (if applicable)
            if license_data.get("currency", "EUR") != "EUR":
                conversion_fee = gross_revenue * self.deduction_rates["currency_conversion"]
                deductions["currency_conversion"] = conversion_fee
            else:
                deductions["currency_conversion"] = Decimal("0.00")
            
            # Calculate total
            deductions["total"] = sum(deductions.values())
            
            return deductions
            
        except Exception as e:
            logger.error(f"Error calculating deductions: {e}")
            return {"total": Decimal("0.00")}
    
    async def _calculate_payment_fees(
        self,
        amount: Decimal,
        payment_method: str
    ) -> Decimal:
        """Calculate payment processing fees"""        try:
            method_config = self.payment_methods.get(payment_method, {})
            
            if "fee" in method_config:
                # Flat fee
                return method_config["fee"]
            elif "fee_rate" in method_config:
                # Percentage fee
                return amount * method_config["fee_rate"]
            else:
                return Decimal("0.00")
                
        except Exception:
            return Decimal("0.00")
    
    def _get_minimum_payment_threshold(self, license_data: Dict[str, Any]) -> Decimal:
        """Get minimum payment threshold"""        return Decimal(str(license_data.get("min_payment_threshold", "10.00")))
    
    def get_engine_stats(self) -> Dict[str, Any]:
        """Get royalty engine statistics"""        try:
            total_calculations = len(self.calculation_cache)
            total_payments = len(self.payment_history)
            
            # Payment status breakdown
            payment_status_breakdown = {}
            total_payment_amount = Decimal("0.00")
            
            for payment in self.payment_history:
                status = payment.status.value
                payment_status_breakdown[status] = payment_status_breakdown.get(status, 0) + 1
                
                if payment.status == PaymentStatus.PAID:
                    total_payment_amount += payment.amount
            
            # Calculate average payment amount
            paid_payments = payment_status_breakdown.get("paid", 0)
            avg_payment_amount = (total_payment_amount / paid_payments) if paid_payments > 0 else Decimal("0.00")
            
            return {
                "version": "1.0.0",
                "calculations": {
                    "total": total_calculations,
                    "cached": len(self.calculation_cache)
                },
                "payments": {
                    "total": total_payments,
                    "status_breakdown": payment_status_breakdown,
                    "total_amount_paid": float(total_payment_amount),
                    "average_payment": float(avg_payment_amount)
                },
                "supported_usage_types": list(self.default_rates.keys()),
                "supported_payment_methods": list(self.payment_methods.keys()),
                "default_currency": "EUR"
            }
            
        except Exception as e:
            logger.error(f"Error getting engine stats: {e}")
            return {"error": str(e)}