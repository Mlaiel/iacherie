# -*- coding: utf-8 -*-
"""Collaboration Revenue Orchestrator - IA Influencer Agent Platform
==================================================================

Enterprise orchestrator for automated collaboration revenue sharing, partnership
payout management, and team-based project monetization with smart contract
automation and multi-party tax compliance.

Architecture: Enterprise Production-Ready (Backend Level 3)
Module: backend/monetization/collaboration_revenue_orchestrator.py
Business Logic: Collaboration → Revenue Sharing → Automated Distribution → Tax Compliance

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
from datetime import datetime, timedelta
from decimal import Decimal, ROUND_HALF_UP
from enum import Enum
from typing import Dict, List, Optional, Any, Union, Tuple, Set
from dataclasses import dataclass, field
from uuid import UUID, uuid4

import aiohttp
from pydantic import BaseModel, Field, validator
from sqlalchemy import Column, String, DateTime, Integer, Text, Boolean, DECIMAL, JSON
from sqlalchemy.ext.declarative import declarative_base

# Configure logging
logger = logging.getLogger(__name__)

Base = declarative_base()


class CollaborationType(str, Enum):
    """Types of collaboration arrangements."""
    CREATIVE_PARTNERSHIP = "creative_partnership"
    REVENUE_SHARE = "revenue_share"
    FIXED_PAYMENT = "fixed_payment"
    MILESTONE_BASED = "milestone_based"
    ROYALTY_SPLIT = "royalty_split"
    PROFIT_SHARING = "profit_sharing"
    EQUITY_PARTICIPATION = "equity_participation"
    HYBRID_MODEL = "hybrid_model"


class PayoutStatus(str, Enum):
    """Status of collaboration payouts."""
    PENDING = "pending"
    CALCULATING = "calculating"
    READY_FOR_PAYMENT = "ready_for_payment"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    DISPUTED = "disputed"
    CANCELLED = "cancelled"
    ON_HOLD = "on_hold"


class PaymentMethod(str, Enum):
    """Supported payment methods for collaboration payouts."""
    BANK_TRANSFER = "bank_transfer"
    PAYPAL = "paypal"
    STRIPE = "stripe"
    CRYPTO_WALLET = "crypto_wallet"
    WISE = "wise"
    PLATFORM_CREDITS = "platform_credits"
    CHECK = "check"


class TaxHandling(str, Enum):
    """Tax handling approaches for collaborations."""
    INDIVIDUAL = "individual"
    COLLECTIVE = "collective"
    PLATFORM_MANAGED = "platform_managed"
    CREATOR_RESPONSIBILITY = "creator_responsibility"


@dataclass
class CollaboratorProfile:
    """Profile information for collaboration participant."""
    user_id: str
    name: str
    email: str
    role: str
    contribution_type: str
    payment_method: PaymentMethod
    tax_id: Optional[str] = None
    bank_details: Dict[str, Any] = field(default_factory=dict)
    preferred_currency: str = "USD"
    minimum_payout: Decimal = Decimal('10.00')
    auto_payout_enabled: bool = True


@dataclass
class RevenueShare:
    """Revenue share configuration for collaboration."""
    collaborator_id: str
    share_percentage: Decimal
    share_type: str  # "percentage", "fixed_amount", "milestone_based"
    minimum_threshold: Decimal = Decimal('0.00')
    maximum_cap: Optional[Decimal] = None
    conditions: Dict[str, Any] = field(default_factory=dict)


@dataclass
class CollaborationContract:
    """Collaboration contract with revenue sharing terms."""
    contract_id: str
    project_id: str
    title: str
    collaboration_type: CollaborationType
    collaborators: List[CollaboratorProfile]
    revenue_shares: List[RevenueShare]
    start_date: datetime
    end_date: Optional[datetime] = None
    auto_distribution: bool = True
    tax_handling: TaxHandling = TaxHandling.INDIVIDUAL
    platform_fee: Decimal = Decimal('0.05')  # 5% platform fee
    minimum_distribution_amount: Decimal = Decimal('50.00')
    distribution_frequency: str = "monthly"  # "daily", "weekly", "monthly", "quarterly"
    terms_conditions: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class RevenueDistribution:
    """Revenue distribution transaction record."""
    distribution_id: str
    contract_id: str
    period_start: datetime
    period_end: datetime
    total_revenue: Decimal
    platform_fee: Decimal
    distributable_amount: Decimal
    collaborator_payments: Dict[str, Decimal]
    status: PayoutStatus
    created_at: datetime = field(default_factory=datetime.utcnow)
    processed_at: Optional[datetime] = None
    notes: str = ""


class CollaborationRevenueOrchestrator:
    """
    Enterprise orchestrator for collaboration revenue management.
    
    Capabilities:
    - Automated revenue sharing calculations
    - Multi-party collaboration management
    - Smart contract-based distributions
    - Tax compliance automation
    - Payment processing orchestration
    - Dispute resolution workflows
    """
    
    def __init__(
        self,
        api_base_url: str = "https://api.ainflue.com/v1",
        max_concurrent_distributions: int = 100,
        default_platform_fee: Decimal = Decimal('0.05'),
        enable_auto_distribution: bool = True,
        enable_tax_withholding: bool = True
    ):
        """Initialize Collaboration Revenue Orchestrator."""
        self.api_base_url = api_base_url
        self.max_concurrent_distributions = max_concurrent_distributions
        self.default_platform_fee = default_platform_fee
        self.enable_auto_distribution = enable_auto_distribution
        self.enable_tax_withholding = enable_tax_withholding
        
        # Active contracts and distributions
        self.active_contracts: Dict[str, CollaborationContract] = {}
        self.pending_distributions: Dict[str, RevenueDistribution] = {}
        self.collaborator_profiles: Dict[str, CollaboratorProfile] = {}
        
        # Currency conversion rates (in real implementation, this would be live data)
        self.currency_rates = {
            "USD": Decimal('1.00'),
            "EUR": Decimal('0.85'),
            "GBP": Decimal('0.73'),
            "CAD": Decimal('1.25'),
            "AUD": Decimal('1.35'),
            "JPY": Decimal('110.00')
        }
        
        # Tax rates by jurisdiction
        self.tax_rates = {
            "US": Decimal('0.24'),
            "UK": Decimal('0.20'),
            "DE": Decimal('0.26'),
            "FR": Decimal('0.30'),
            "CA": Decimal('0.26'),
            "AU": Decimal('0.25'),
            "default": Decimal('0.20')
        }
        
        logger.info("🤝💰 Collaboration Revenue Orchestrator initialized")
    
    async def create_collaboration_contract(
        self,
        project_id: str,
        title: str,
        collaboration_type: CollaborationType,
        collaborators: List[Dict[str, Any]],
        revenue_shares: List[Dict[str, Any]],
        **kwargs
    ) -> CollaborationContract:
        """
        Create new collaboration contract with revenue sharing terms.
        
        Args:
            project_id: Project identifier
            title: Contract title
            collaboration_type: Type of collaboration
            collaborators: List of collaborator information
            revenue_shares: Revenue sharing configuration
            **kwargs: Additional contract parameters
            
        Returns:
            Created collaboration contract
        """
        try:
            contract_id = str(uuid4())
            
            # Validate and create collaborator profiles
            collaborator_profiles = []
            for collab_data in collaborators:
                profile = CollaboratorProfile(
                    user_id=collab_data["user_id"],
                    name=collab_data["name"],
                    email=collab_data["email"],
                    role=collab_data["role"],
                    contribution_type=collab_data["contribution_type"],
                    payment_method=PaymentMethod(collab_data.get("payment_method", "paypal")),
                    tax_id=collab_data.get("tax_id"),
                    bank_details=collab_data.get("bank_details", {}),
                    preferred_currency=collab_data.get("preferred_currency", "USD"),
                    minimum_payout=Decimal(str(collab_data.get("minimum_payout", "10.00"))),
                    auto_payout_enabled=collab_data.get("auto_payout_enabled", True)
                )
                collaborator_profiles.append(profile)
                self.collaborator_profiles[profile.user_id] = profile
            
            # Validate and create revenue shares
            revenue_share_objects = []
            total_percentage = Decimal('0.00')
            
            for share_data in revenue_shares:
                share = RevenueShare(
                    collaborator_id=share_data["collaborator_id"],
                    share_percentage=Decimal(str(share_data["share_percentage"])),
                    share_type=share_data.get("share_type", "percentage"),
                    minimum_threshold=Decimal(str(share_data.get("minimum_threshold", "0.00"))),
                    maximum_cap=Decimal(str(share_data["maximum_cap"])) if share_data.get("maximum_cap") else None,
                    conditions=share_data.get("conditions", {})
                )
                revenue_share_objects.append(share)
                
                if share.share_type == "percentage":
                    total_percentage += share.share_percentage
            
            # Validate total percentage doesn't exceed 100%
            if total_percentage > Decimal('1.00'):
                raise ValueError(f"Total revenue share percentage exceeds 100%: {total_percentage * 100}%")
            
            # Create contract
            contract = CollaborationContract(
                contract_id=contract_id,
                project_id=project_id,
                title=title,
                collaboration_type=collaboration_type,
                collaborators=collaborator_profiles,
                revenue_shares=revenue_share_objects,
                start_date=kwargs.get("start_date", datetime.utcnow()),
                end_date=kwargs.get("end_date"),
                auto_distribution=kwargs.get("auto_distribution", True),
                tax_handling=TaxHandling(kwargs.get("tax_handling", "individual")),
                platform_fee=Decimal(str(kwargs.get("platform_fee", self.default_platform_fee))),
                minimum_distribution_amount=Decimal(str(kwargs.get("minimum_distribution_amount", "50.00"))),
                distribution_frequency=kwargs.get("distribution_frequency", "monthly"),
                terms_conditions=kwargs.get("terms_conditions", {}),
                metadata=kwargs.get("metadata", {})
            )
            
            # Store contract
            self.active_contracts[contract_id] = contract
            
            # Log contract creation
            await self._log_contract_event(contract, "contract_created")
            
            logger.info(f"🤝 Collaboration contract created: {contract_id} for project {project_id}")
            
            return contract
            
        except Exception as e:
            logger.error(f"❌ Error creating collaboration contract: {e}")
            raise
    
    async def process_revenue_distribution(
        self,
        contract_id: str,
        revenue_data: Dict[str, Decimal],
        period_start: datetime,
        period_end: datetime
    ) -> RevenueDistribution:
        """
        Process revenue distribution for collaboration contract.
        
        Args:
            contract_id: Collaboration contract ID
            revenue_data: Revenue data by source/platform
            period_start: Distribution period start
            period_end: Distribution period end
            
        Returns:
            Revenue distribution record
        """
        try:
            contract = self.active_contracts.get(contract_id)
            if not contract:
                raise ValueError(f"Contract not found: {contract_id}")
            
            # Calculate total revenue
            total_revenue = sum(revenue_data.values())
            
            # Check minimum distribution threshold
            if total_revenue < contract.minimum_distribution_amount:
                logger.info(f"⏸️ Revenue below minimum threshold: ${total_revenue} < ${contract.minimum_distribution_amount}")
                return None
            
            # Calculate platform fee
            platform_fee = (total_revenue * contract.platform_fee).quantize(
                Decimal('0.01'), rounding=ROUND_HALF_UP
            )
            
            # Calculate distributable amount
            distributable_amount = total_revenue - platform_fee
            
            # Calculate individual collaborator payments
            collaborator_payments = await self._calculate_collaborator_payments(
                contract, distributable_amount
            )
            
            # Apply tax withholding if enabled
            if self.enable_tax_withholding:
                collaborator_payments = await self._apply_tax_withholding(
                    contract, collaborator_payments
                )
            
            # Create distribution record
            distribution_id = str(uuid4())
            distribution = RevenueDistribution(
                distribution_id=distribution_id,
                contract_id=contract_id,
                period_start=period_start,
                period_end=period_end,
                total_revenue=total_revenue,
                platform_fee=platform_fee,
                distributable_amount=distributable_amount,
                collaborator_payments=collaborator_payments,
                status=PayoutStatus.READY_FOR_PAYMENT
            )
            
            # Store distribution
            self.pending_distributions[distribution_id] = distribution
            
            # Process automatic distribution if enabled
            if contract.auto_distribution and self.enable_auto_distribution:
                await self._process_automatic_distribution(distribution)
            
            # Log distribution event
            await self._log_distribution_event(distribution, "distribution_calculated")
            
            logger.info(f"💰 Revenue distribution processed: {distribution_id}, "
                       f"Total: ${total_revenue}, Distributable: ${distributable_amount}")
            
            return distribution
            
        except Exception as e:
            logger.error(f"❌ Error processing revenue distribution: {e}")
            raise
    
    async def _calculate_collaborator_payments(
        self,
        contract: CollaborationContract,
        distributable_amount: Decimal
    ) -> Dict[str, Decimal]:
        """Calculate individual payments for each collaborator."""
        try:
            payments = {}
            
            for revenue_share in contract.revenue_shares:
                collaborator_id = revenue_share.collaborator_id
                
                if revenue_share.share_type == "percentage":
                    # Percentage-based calculation
                    payment = (distributable_amount * revenue_share.share_percentage).quantize(
                        Decimal('0.01'), rounding=ROUND_HALF_UP
                    )
                elif revenue_share.share_type == "fixed_amount":
                    # Fixed amount per distribution
                    payment = revenue_share.share_percentage  # Using share_percentage field for fixed amount
                else:
                    # Default to percentage
                    payment = (distributable_amount * revenue_share.share_percentage).quantize(
                        Decimal('0.01'), rounding=ROUND_HALF_UP
                    )
                
                # Apply minimum threshold
                if payment < revenue_share.minimum_threshold:
                    payment = Decimal('0.00')
                
                # Apply maximum cap if set
                if revenue_share.maximum_cap and payment > revenue_share.maximum_cap:
                    payment = revenue_share.maximum_cap
                
                # Get collaborator profile for minimum payout check
                collaborator_profile = self.collaborator_profiles.get(collaborator_id)
                if collaborator_profile and payment < collaborator_profile.minimum_payout:
                    payment = Decimal('0.00')  # Hold payment until minimum reached
                
                payments[collaborator_id] = payment
            
            return payments
            
        except Exception as e:
            logger.error(f"❌ Error calculating collaborator payments: {e}")
            raise
    
    async def _apply_tax_withholding(
        self,
        contract: CollaborationContract,
        payments: Dict[str, Decimal]
    ) -> Dict[str, Decimal]:
        """Apply tax withholding to collaborator payments."""
        try:
            if contract.tax_handling == TaxHandling.PLATFORM_MANAGED:
                # Apply platform-managed tax withholding
                for collaborator_id, payment in payments.items():
                    collaborator_profile = self.collaborator_profiles.get(collaborator_id)
                    if collaborator_profile and collaborator_profile.tax_id:
                        # Determine tax jurisdiction (simplified - in real implementation would be more complex)
                        jurisdiction = "US"  # Default
                        tax_rate = self.tax_rates.get(jurisdiction, self.tax_rates["default"])
                        
                        # Calculate tax withholding
                        tax_amount = (payment * tax_rate).quantize(
                            Decimal('0.01'), rounding=ROUND_HALF_UP
                        )
                        
                        # Deduct tax from payment
                        payments[collaborator_id] = payment - tax_amount
                        
                        logger.debug(f"💸 Tax withheld for {collaborator_id}: ${tax_amount}")
            
            return payments
            
        except Exception as e:
            logger.error(f"❌ Error applying tax withholding: {e}")
            return payments
    
    async def _process_automatic_distribution(
        self,
        distribution: RevenueDistribution
    ) -> None:
        """Process automatic payment distribution to collaborators."""
        try:
            distribution.status = PayoutStatus.PROCESSING
            
            # Process each collaborator payment
            for collaborator_id, payment_amount in distribution.collaborator_payments.items():
                if payment_amount <= Decimal('0.00'):
                    continue
                
                collaborator_profile = self.collaborator_profiles.get(collaborator_id)
                if not collaborator_profile:
                    logger.warning(f"⚠️ Collaborator profile not found: {collaborator_id}")
                    continue
                
                # Process payment via appropriate method
                payment_success = await self._process_collaborator_payment(
                    collaborator_profile, payment_amount, distribution.distribution_id
                )
                
                if not payment_success:
                    distribution.status = PayoutStatus.FAILED
                    distribution.notes += f"Payment failed for {collaborator_id}; "
                    logger.error(f"❌ Payment failed for collaborator: {collaborator_id}")
                    return
            
            # Mark distribution as completed
            distribution.status = PayoutStatus.COMPLETED
            distribution.processed_at = datetime.utcnow()
            distribution.notes += "All payments processed successfully"
            
            logger.info(f"✅ Automatic distribution completed: {distribution.distribution_id}")
            
        except Exception as e:
            logger.error(f"❌ Error processing automatic distribution: {e}")
            distribution.status = PayoutStatus.FAILED
            distribution.notes += f"Error: {str(e)}"
    
    async def _process_collaborator_payment(
        self,
        collaborator: CollaboratorProfile,
        amount: Decimal,
        distribution_id: str
    ) -> bool:
        """Process individual collaborator payment."""
        try:
            # Convert currency if needed
            if collaborator.preferred_currency != "USD":
                conversion_rate = self.currency_rates.get(collaborator.preferred_currency, Decimal('1.00'))
                converted_amount = (amount * conversion_rate).quantize(
                    Decimal('0.01'), rounding=ROUND_HALF_UP
                )
            else:
                converted_amount = amount
            
            # Process payment based on payment method
            if collaborator.payment_method == PaymentMethod.PAYPAL:
                success = await self._process_paypal_payment(
                    collaborator.email, converted_amount, collaborator.preferred_currency
                )
            elif collaborator.payment_method == PaymentMethod.STRIPE:
                success = await self._process_stripe_payment(
                    collaborator.bank_details, converted_amount, collaborator.preferred_currency
                )
            elif collaborator.payment_method == PaymentMethod.CRYPTO_WALLET:
                success = await self._process_crypto_payment(
                    collaborator.bank_details.get("wallet_address"), converted_amount
                )
            else:
                # Default to platform credits
                success = await self._process_platform_credits(
                    collaborator.user_id, converted_amount
                )
            
            if success:
                logger.info(f"💳 Payment processed: {collaborator.user_id}, "
                           f"${converted_amount} {collaborator.preferred_currency}")
            
            return success
            
        except Exception as e:
            logger.error(f"❌ Error processing collaborator payment: {e}")
            return False
    
    async def _process_paypal_payment(
        self,
        email: str,
        amount: Decimal,
        currency: str
    ) -> bool:
        """Process PayPal payment (mock implementation)."""
        try:
            # In real implementation, this would use PayPal API
            logger.info(f"💰 PayPal payment: {email}, ${amount} {currency}")
            return True
        except Exception as e:
            logger.error(f"❌ PayPal payment failed: {e}")
            return False
    
    async def _process_stripe_payment(
        self,
        bank_details: Dict[str, Any],
        amount: Decimal,
        currency: str
    ) -> bool:
        """Process Stripe bank transfer (mock implementation)."""
        try:
            # In real implementation, this would use Stripe API
            logger.info(f"🏦 Stripe payment: ${amount} {currency}")
            return True
        except Exception as e:
            logger.error(f"❌ Stripe payment failed: {e}")
            return False
    
    async def _process_crypto_payment(
        self,
        wallet_address: str,
        amount: Decimal
    ) -> bool:
        """Process cryptocurrency payment (mock implementation)."""
        try:
            # In real implementation, this would use blockchain APIs
            logger.info(f"₿ Crypto payment: {wallet_address}, ${amount}")
            return True
        except Exception as e:
            logger.error(f"❌ Crypto payment failed: {e}")
            return False
    
    async def _process_platform_credits(
        self,
        user_id: str,
        amount: Decimal
    ) -> bool:
        """Process platform credits payment."""
        try:
            # Add credits to user account
            logger.info(f"🏆 Platform credits: {user_id}, ${amount}")
            return True
        except Exception as e:
            logger.error(f"❌ Platform credits failed: {e}")
            return False
    
    async def get_collaboration_summary(
        self,
        contract_id: str
    ) -> Dict[str, Any]:
        """Get collaboration revenue summary."""
        try:
            contract = self.active_contracts.get(contract_id)
            if not contract:
                return {"error": "Contract not found"}
            
            # Get all distributions for this contract
            contract_distributions = [
                dist for dist in self.pending_distributions.values()
                if dist.contract_id == contract_id
            ]
            
            # Calculate totals
            total_revenue = sum(dist.total_revenue for dist in contract_distributions)
            total_platform_fees = sum(dist.platform_fee for dist in contract_distributions)
            total_distributed = sum(dist.distributable_amount for dist in contract_distributions)
            
            # Calculate per-collaborator totals
            collaborator_totals = {}
            for dist in contract_distributions:
                for collab_id, amount in dist.collaborator_payments.items():
                    collaborator_totals[collab_id] = collaborator_totals.get(collab_id, Decimal('0.00')) + amount
            
            return {
                "contract_id": contract_id,
                "project_id": contract.project_id,
                "title": contract.title,
                "collaboration_type": contract.collaboration_type.value,
                "total_revenue": float(total_revenue),
                "total_platform_fees": float(total_platform_fees),
                "total_distributed": float(total_distributed),
                "distribution_count": len(contract_distributions),
                "collaborator_totals": {k: float(v) for k, v in collaborator_totals.items()},
                "contract_status": "active" if contract.end_date is None or contract.end_date > datetime.utcnow() else "expired",
                "generated_at": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ Error getting collaboration summary: {e}")
            return {"error": str(e)}
    
    async def _log_contract_event(
        self,
        contract: CollaborationContract,
        event_type: str
    ) -> None:
        """Log contract event for analytics."""
        try:
            event_data = {
                "contract_id": contract.contract_id,
                "project_id": contract.project_id,
                "event_type": event_type,
                "collaboration_type": contract.collaboration_type.value,
                "collaborator_count": len(contract.collaborators),
                "timestamp": datetime.utcnow().isoformat()
            }
            
            # In real implementation, send to analytics pipeline
            logger.debug(f"📊 Contract event logged: {event_type}")
            
        except Exception as e:
            logger.error(f"❌ Error logging contract event: {e}")
    
    async def _log_distribution_event(
        self,
        distribution: RevenueDistribution,
        event_type: str
    ) -> None:
        """Log distribution event for analytics."""
        try:
            event_data = {
                "distribution_id": distribution.distribution_id,
                "contract_id": distribution.contract_id,
                "event_type": event_type,
                "total_revenue": float(distribution.total_revenue),
                "collaborator_count": len(distribution.collaborator_payments),
                "status": distribution.status.value,
                "timestamp": datetime.utcnow().isoformat()
            }
            
            # In real implementation, send to analytics pipeline
            logger.debug(f"📊 Distribution event logged: {event_type}")
            
        except Exception as e:
            logger.error(f"❌ Error logging distribution event: {e}")


# Factory function for easy instantiation
def get_collaboration_revenue_orchestrator(**kwargs) -> CollaborationRevenueOrchestrator:
    """Get configured Collaboration Revenue Orchestrator instance."""
    return CollaborationRevenueOrchestrator(**kwargs)


if __name__ == "__main__":
    # Example usage
    async def main():
        orchestrator = get_collaboration_revenue_orchestrator()
        
        # Example collaborators
        collaborators = [
            {
                "user_id": "creator_1",
                "name": "Alice Music",
                "email": "alice@example.com",
                "role": "lead_artist",
                "contribution_type": "vocals_composition",
                "payment_method": "paypal",
                "preferred_currency": "USD",
                "minimum_payout": "25.00"
            },
            {
                "user_id": "creator_2",
                "name": "Bob Producer",
                "email": "bob@example.com",
                "role": "producer",
                "contribution_type": "production_mixing",
                "payment_method": "stripe",
                "preferred_currency": "EUR",
                "minimum_payout": "50.00"
            }
        ]
        
        # Example revenue shares
        revenue_shares = [
            {
                "collaborator_id": "creator_1",
                "share_percentage": "0.60",  # 60%
                "share_type": "percentage"
            },
            {
                "collaborator_id": "creator_2",
                "share_percentage": "0.40",  # 40%
                "share_type": "percentage"
            }
        ]
        
        # Create collaboration contract
        contract = await orchestrator.create_collaboration_contract(
            project_id="project_123",
            title="Music Track Collaboration",
            collaboration_type=CollaborationType.REVENUE_SHARE,
            collaborators=collaborators,
            revenue_shares=revenue_shares,
            auto_distribution=True
        )
        
        print(f"🤝 Contract created: {contract.contract_id}")
        
        # Process revenue distribution
        revenue_data = {
            "spotify": Decimal('150.00'),
            "youtube": Decimal('200.00'),
            "apple_music": Decimal('100.00')
        }
        
        distribution = await orchestrator.process_revenue_distribution(
            contract_id=contract.contract_id,
            revenue_data=revenue_data,
            period_start=datetime.utcnow() - timedelta(days=30),
            period_end=datetime.utcnow()
        )
        
        print(f"💰 Distribution processed: {distribution.distribution_id}")
        print(f"Total Revenue: ${distribution.total_revenue}")
        print(f"Collaborator Payments: {distribution.collaborator_payments}")
        
        # Get summary
        summary = await orchestrator.get_collaboration_summary(contract.contract_id)
        print(f"📊 Summary: {summary}")
    
    # Run example
    asyncio.run(main())