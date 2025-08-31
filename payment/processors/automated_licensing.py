"""⚖️ Automated Licensing Payment Processor
========================================

Automated licensing and royalty payment processor with smart contracts,
usage tracking, and multi-party revenue distribution for content licensing.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: © 2025 Fahed Mlaiel. All rights reserved.
"""
import asyncio
import logging
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta
from decimal import Decimal, ROUND_HALF_UP
import uuid
import json

logger = logging.getLogger(__name__)


class LicenseType(Enum):
    """Content license types"""    SYNC_RIGHTS = "sync_rights"
    MECHANICAL = "mechanical"
    PERFORMANCE = "performance"
    MASTER_USE = "master_use"
    PUBLISHING = "publishing"
    SAMPLING = "sampling"
    REMIX = "remix"
    COVER_VERSION = "cover_version"
    COMMERCIAL_USE = "commercial_use"
    BROADCAST = "broadcast"
    STREAMING = "streaming"
    DOWNLOAD = "download"


class UsageType(Enum):
    """Content usage types"""    PLAY = "play"
    DOWNLOAD = "download"
    STREAM = "stream"
    SYNC = "sync"
    BROADCAST = "broadcast"
    PERFORMANCE = "performance"
    REMIX = "remix"
    SAMPLE = "sample"


class LicenseStatus(Enum):
    """License status"""    ACTIVE = "active"
    PENDING = "pending"
    EXPIRED = "expired"
    SUSPENDED = "suspended"
    CANCELLED = "cancelled"
    DISPUTED = "disputed"


class RoyaltyType(Enum):
    """Royalty distribution types"""    MECHANICAL = "mechanical"
    PERFORMANCE = "performance"
    SYNCHRONIZATION = "synchronization"
    MASTER_RECORDING = "master_recording"
    PUBLISHING = "publishing"
    NEIGHBORING_RIGHTS = "neighboring_rights"


@dataclass
class LicenseAgreement:
    """Content licensing agreement"""    id: str
    content_id: str
    licensee_id: str
    licensor_id: str
    license_type: LicenseType
    usage_type: UsageType
    status: LicenseStatus
    rate_per_use: Decimal
    minimum_guarantee: Decimal
    territory: List[str]  # Country codes
    term_start: datetime
    term_end: datetime
    usage_limit: Optional[int] = None
    revenue_share_percent: Optional[Decimal] = None
    advance_payment: Optional[Decimal] = None
    created_at: datetime = field(default_factory=datetime.now)
    last_updated: datetime = field(default_factory=datetime.now)


@dataclass
class UsageReport:
    """Content usage reporting"""    id: str
    content_id: str
    license_id: str
    usage_type: UsageType
    usage_count: int
    usage_date: datetime
    territory: str
    platform: str
    revenue_generated: Optional[Decimal] = None
    user_demographics: Optional[Dict[str, Any]] = None
    reported_at: datetime = field(default_factory=datetime.now)


@dataclass
class RoyaltyDistribution:
    """Royalty payment distribution"""    id: str
    content_id: str
    license_id: str
    usage_report_id: str
    total_revenue: Decimal
    distribution_date: datetime
    payments: List[Dict[str, Any]]  # List of individual payments
    currency: str = "USD"
    processing_fee: Decimal = Decimal("0")
    net_revenue: Decimal = Decimal("0")


@dataclass
class RevenueShare:
    """Revenue sharing configuration"""    participant_id: str
    participant_type: str  # artist, producer, songwriter, publisher, etc.
    share_percentage: Decimal
    minimum_payout: Decimal
    payment_method: str
    contact_info: Dict[str, str]


class AutomatedLicensingProcessor:
    """    Automated licensing payment processor
    
    Handles content licensing agreements, usage tracking, royalty calculations,
    and automated multi-party revenue distribution with smart contract integration.
    """    
    def __init__(
        self,
        blockchain_config: Optional[Dict[str, Any]] = None,
        payment_processors: Optional[Dict[str, Any]] = None
    ):
        """Initialize automated licensing processor"""        self.blockchain_config = blockchain_config or {}
        self.payment_processors = payment_processors or {}
        self.logger = logging.getLogger(__name__)
        
        # Processing fees
        self.processing_fee_percent = Decimal("0.025")  # 2.5%
        self.minimum_processing_fee = Decimal("0.50")
        
        # Payout thresholds
        self.minimum_payout_amount = Decimal("10.00")
        self.payout_frequency_days = 30
        
        # Usage rate calculations
        self.base_rates = {
            UsageType.STREAM: Decimal("0.003"),
            UsageType.DOWNLOAD: Decimal("0.10"),
            UsageType.PLAY: Decimal("0.001"),
            UsageType.SYNC: Decimal("100.00"),
            UsageType.BROADCAST: Decimal("50.00"),
            UsageType.PERFORMANCE: Decimal("0.10"),
            UsageType.SAMPLE: Decimal("25.00")
        }
    
    async def create_license_agreement(
        self,
        content_id: str,
        licensee_id: str,
        licensor_id: str,
        license_type: LicenseType,
        usage_type: UsageType,
        rate_per_use: Decimal,
        territory: List[str],
        term_months: int,
        minimum_guarantee: Optional[Decimal] = None,
        revenue_share_percent: Optional[Decimal] = None
    ) -> LicenseAgreement:
        """Create a new licensing agreement"""        try:
            license_id = f"lic_{uuid.uuid4().hex[:12]}"
            
            term_start = datetime.now()
            term_end = term_start + timedelta(days=term_months * 30)
            
            agreement = LicenseAgreement(
                id=license_id,
                content_id=content_id,
                licensee_id=licensee_id,
                licensor_id=licensor_id,
                license_type=license_type,
                usage_type=usage_type,
                status=LicenseStatus.PENDING,
                rate_per_use=rate_per_use,
                minimum_guarantee=minimum_guarantee or Decimal("0"),
                territory=territory,
                term_start=term_start,
                term_end=term_end,
                revenue_share_percent=revenue_share_percent
            )
            
            # Deploy smart contract if blockchain is enabled
            if self.blockchain_config.get("enabled"):
                contract_address = await self._deploy_license_contract(agreement)
                self.logger.info(f"License contract deployed: {contract_address}")
            
            self.logger.info(f"Created license agreement: {license_id}")
            return agreement
            
        except Exception as e:
            self.logger.error(f"Failed to create license agreement: {e}")
            raise
    
    async def activate_license(self, license_id: str) -> Dict[str, Any]:
        """Activate a pending license agreement"""        try:
            # Verify all requirements are met
            verification_result = await self._verify_license_requirements(license_id)
            
            if not verification_result["valid"]:
                return {
                    "success": False,
                    "error": "License requirements not met",
                    "missing_requirements": verification_result["missing"]
                }
            
            # Process advance payment if required
            advance_payment_result = await self._process_advance_payment(license_id)
            
            if not advance_payment_result["success"]:
                return {
                    "success": False,
                    "error": "Advance payment failed",
                    "details": advance_payment_result
                }
            
            # Activate license
            activation_time = datetime.now()
            
            return {
                "success": True,
                "license_id": license_id,
                "status": "active",
                "activated_at": activation_time.isoformat(),
                "advance_payment": advance_payment_result
            }
            
        except Exception as e:
            self.logger.error(f"Failed to activate license {license_id}: {e}")
            return {"success": False, "error": str(e)}
    
    async def report_usage(
        self,
        content_id: str,
        license_id: str,
        usage_type: UsageType,
        usage_count: int,
        territory: str,
        platform: str,
        usage_date: Optional[datetime] = None,
        revenue_generated: Optional[Decimal] = None
    ) -> UsageReport:
        """Report content usage for royalty calculation"""        try:
            report_id = f"usage_{uuid.uuid4().hex[:12]}"
            
            if not usage_date:
                usage_date = datetime.now()
            
            usage_report = UsageReport(
                id=report_id,
                content_id=content_id,
                license_id=license_id,
                usage_type=usage_type,
                usage_count=usage_count,
                usage_date=usage_date,
                territory=territory,
                platform=platform,
                revenue_generated=revenue_generated
            )
            
            # Calculate royalties for this usage
            royalty_calculation = await self._calculate_royalties(usage_report)
            
            # If revenue threshold is met, trigger automatic distribution
            if royalty_calculation["total_royalties"] >= self.minimum_payout_amount:
                await self._trigger_royalty_distribution(usage_report, royalty_calculation)
            
            self.logger.info(f"Recorded usage report: {report_id}")
            return usage_report
            
        except Exception as e:
            self.logger.error(f"Failed to report usage: {e}")
            raise
    
    async def calculate_royalty_distribution(
        self,
        usage_report: UsageReport,
        revenue_shares: List[RevenueShare]
    ) -> RoyaltyDistribution:
        """Calculate royalty distribution for stakeholders"""        try:
            distribution_id = f"dist_{uuid.uuid4().hex[:12]}"
            
            # Get license agreement
            license_agreement = await self._get_license_agreement(usage_report.license_id)
            
            # Calculate total revenue
            if usage_report.revenue_generated:
                total_revenue = usage_report.revenue_generated
            else:
                # Calculate based on usage and rates
                rate = license_agreement.rate_per_use
                total_revenue = rate * Decimal(str(usage_report.usage_count))
            
            # Calculate processing fee
            processing_fee = max(
                total_revenue * self.processing_fee_percent,
                self.minimum_processing_fee
            )
            net_revenue = total_revenue - processing_fee
            
            # Distribute among stakeholders
            payments = []
            for revenue_share in revenue_shares:
                share_amount = net_revenue * (revenue_share.share_percentage / Decimal("100"))
                
                if share_amount >= revenue_share.minimum_payout:
                    payment = {
                        "participant_id": revenue_share.participant_id,
                        "participant_type": revenue_share.participant_type,
                        "amount": float(share_amount),
                        "percentage": float(revenue_share.share_percentage),
                        "payment_method": revenue_share.payment_method,
                        "status": "pending"
                    }
                    payments.append(payment)
            
            distribution = RoyaltyDistribution(
                id=distribution_id,
                content_id=usage_report.content_id,
                license_id=usage_report.license_id,
                usage_report_id=usage_report.id,
                total_revenue=total_revenue,
                distribution_date=datetime.now(),
                payments=payments,
                processing_fee=processing_fee,
                net_revenue=net_revenue
            )
            
            self.logger.info(f"Calculated royalty distribution: {distribution_id}")
            return distribution
            
        except Exception as e:
            self.logger.error(f"Failed to calculate royalty distribution: {e}")
            raise
    
    async def execute_royalty_payments(
        self,
        distribution: RoyaltyDistribution
    ) -> Dict[str, Any]:
        """Execute royalty payments to all stakeholders"""        try:
            payment_results = []
            
            for payment in distribution.payments:
                try:
                    # Execute payment based on method
                    if payment["payment_method"] == "stripe":
                        result = await self._process_stripe_payout(payment)
                    elif payment["payment_method"] == "paypal":
                        result = await self._process_paypal_payout(payment)
                    elif payment["payment_method"] == "wise":
                        result = await self._process_wise_payout(payment)
                    elif payment["payment_method"] == "crypto":
                        result = await self._process_crypto_payout(payment)
                    else:
                        result = {"success": False, "error": "Unsupported payment method"}
                    
                    payment["status"] = "completed" if result["success"] else "failed"
                    payment["transaction_id"] = result.get("transaction_id")
                    payment["error"] = result.get("error")
                    
                    payment_results.append({
                        "participant_id": payment["participant_id"],
                        "success": result["success"],
                        "amount": payment["amount"],
                        "transaction_id": result.get("transaction_id"),
                        "error": result.get("error")
                    })
                    
                except Exception as e:
                    self.logger.error(f"Payment failed for {payment['participant_id']}: {e}")
                    payment["status"] = "failed"
                    payment["error"] = str(e)
                    
                    payment_results.append({
                        "participant_id": payment["participant_id"],
                        "success": False,
                        "amount": payment["amount"],
                        "error": str(e)
                    })
            
            # Calculate success metrics
            successful_payments = sum(1 for result in payment_results if result["success"])
            total_payments = len(payment_results)
            total_paid = sum(result["amount"] for result in payment_results if result["success"])
            
            return {
                "distribution_id": distribution.id,
                "total_payments": total_payments,
                "successful_payments": successful_payments,
                "failed_payments": total_payments - successful_payments,
                "total_amount_paid": total_paid,
                "payment_results": payment_results,
                "execution_time": datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Failed to execute royalty payments: {e}")
            return {"success": False, "error": str(e)}
    
    async def generate_licensing_report(
        self,
        period_start: datetime,
        period_end: datetime,
        content_id: Optional[str] = None,
        licensee_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Generate comprehensive licensing and royalty report"""        try:
            # Mock report data (in production, query actual database)
            total_licenses = 45
            active_licenses = 38
            total_usage_events = 125000
            total_revenue = Decimal("15750.50")
            total_royalties_paid = Decimal("12600.40")
            
            # Usage breakdown by type
            usage_breakdown = {
                "streams": {"count": 100000, "revenue": 300.00},
                "downloads": {"count": 15000, "revenue": 1500.00},
                "sync_uses": {"count": 25, "revenue": 2500.00},
                "broadcasts": {"count": 50, "revenue": 2500.00},
                "performances": {"count": 5000, "revenue": 500.00}
            }
            
            # Top performing content
            top_content = [
                {"content_id": "content_1", "usage_count": 25000, "revenue": 2500.00},
                {"content_id": "content_2", "usage_count": 20000, "revenue": 2000.00},
                {"content_id": "content_3", "usage_count": 15000, "revenue": 1500.00}
            ]
            
            # Revenue by territory
            territory_revenue = {
                "US": 8000.00,
                "GB": 3000.00,
                "DE": 2000.00,
                "FR": 1500.00,
                "CA": 1250.50
            }
            
            return {
                "report_period": {
                    "start": period_start.isoformat(),
                    "end": period_end.isoformat()
                },
                "summary": {
                    "total_licenses": total_licenses,
                    "active_licenses": active_licenses,
                    "total_usage_events": total_usage_events,
                    "total_revenue": float(total_revenue),
                    "total_royalties_paid": float(total_royalties_paid),
                    "platform_fee": float(total_revenue - total_royalties_paid)
                },
                "usage_breakdown": usage_breakdown,
                "top_content": top_content,
                "territory_revenue": territory_revenue,
                "license_types": {
                    "sync_rights": 15,
                    "streaming": 20,
                    "mechanical": 8,
                    "performance": 2
                },
                "payment_methods": {
                    "stripe": 60,
                    "paypal": 25,
                    "wise": 10,
                    "crypto": 5
                },
                "generated_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Failed to generate licensing report: {e}")
            return {"error": str(e)}
    
    async def _deploy_license_contract(self, agreement: LicenseAgreement) -> str:
        """Deploy smart contract for license agreement"""        # Mock smart contract deployment
        contract_address = f"0x{uuid.uuid4().hex[:40]}"
        
        # In production, deploy actual smart contract with:
        # - License terms
        # - Automatic royalty distribution
        # - Usage tracking
        # - Payment escrow
        
        return contract_address
    
    async def _verify_license_requirements(self, license_id: str) -> Dict[str, Any]:
        """Verify all license requirements are met"""        # Mock verification (in production, check actual requirements)
        return {
            "valid": True,
            "missing": [],
            "verified_at": datetime.now().isoformat()
        }
    
    async def _process_advance_payment(self, license_id: str) -> Dict[str, Any]:
        """Process advance payment for license"""        # Mock advance payment processing
        return {
            "success": True,
            "amount": 500.00,
            "transaction_id": f"adv_{uuid.uuid4().hex[:12]}",
            "processed_at": datetime.now().isoformat()
        }
    
    async def _get_license_agreement(self, license_id: str) -> LicenseAgreement:
        """Get license agreement by ID"""        # Mock license agreement (in production, fetch from database)
        return LicenseAgreement(
            id=license_id,
            content_id="content_123",
            licensee_id="licensee_456",
            licensor_id="licensor_789",
            license_type=LicenseType.STREAMING,
            usage_type=UsageType.STREAM,
            status=LicenseStatus.ACTIVE,
            rate_per_use=Decimal("0.003"),
            minimum_guarantee=Decimal("100.00"),
            territory=["US", "CA"],
            term_start=datetime.now(),
            term_end=datetime.now() + timedelta(days=365)
        )
    
    async def _calculate_royalties(self, usage_report: UsageReport) -> Dict[str, Any]:
        """Calculate royalties for usage report"""        base_rate = self.base_rates.get(usage_report.usage_type, Decimal("0.001"))
        total_royalties = base_rate * Decimal(str(usage_report.usage_count))
        
        return {
            "usage_report_id": usage_report.id,
            "base_rate": float(base_rate),
            "usage_count": usage_report.usage_count,
            "total_royalties": float(total_royalties),
            "calculated_at": datetime.now().isoformat()
        }
    
    async def _trigger_royalty_distribution(
        self,
        usage_report: UsageReport,
        royalty_calculation: Dict[str, Any]
    ) -> None:
        """Trigger automatic royalty distribution"""        self.logger.info(f"Triggering royalty distribution for usage {usage_report.id}")
        # In production, queue distribution job
    
    async def _process_stripe_payout(self, payment: Dict[str, Any]) -> Dict[str, Any]:
        """Process Stripe payout"""        # Mock Stripe payout
        return {
            "success": True,
            "transaction_id": f"po_stripe_{uuid.uuid4().hex[:12]}",
            "amount": payment["amount"],
            "fee": payment["amount"] * 0.025
        }
    
    async def _process_paypal_payout(self, payment: Dict[str, Any]) -> Dict[str, Any]:
        """Process PayPal payout"""        # Mock PayPal payout
        return {
            "success": True,
            "transaction_id": f"pp_payout_{uuid.uuid4().hex[:12]}",
            "amount": payment["amount"],
            "fee": payment["amount"] * 0.02
        }
    
    async def _process_wise_payout(self, payment: Dict[str, Any]) -> Dict[str, Any]:
        """Process Wise payout"""        # Mock Wise payout
        return {
            "success": True,
            "transaction_id": f"wise_transfer_{uuid.uuid4().hex[:12]}",
            "amount": payment["amount"],
            "fee": payment["amount"] * 0.005
        }
    
    async def _process_crypto_payout(self, payment: Dict[str, Any]) -> Dict[str, Any]:
        """Process cryptocurrency payout"""        # Mock crypto payout
        return {
            "success": True,
            "transaction_id": f"crypto_tx_{uuid.uuid4().hex[:12]}",
            "amount": payment["amount"],
            "fee": 0.50  # Fixed crypto fee
        }


# Export the main class
__all__ = [
    "AutomatedLicensingProcessor",
    "LicenseAgreement",
    "UsageReport",
    "RoyaltyDistribution",
    "RevenueShare",
    "LicenseType",
    "UsageType",
    "RoyaltyType"
]