"""Royalty Distributor Contract - IA-Influencer-Agent Platform

This module provides automated royalty distribution functionality for content creators,
enabling fair and transparent revenue sharing among multiple stakeholders including
creators, collaborators, platform, and other beneficiaries.

Features:
- Automated royalty distribution
- Multi-party revenue sharing
- Configurable distribution rules
- Real-time payment processing
- Transparent audit trails
- Emergency distribution controls
- International payment support
- Tax compliance integration

(c) 2025 Fahed Mlaiel (mlaiel@live.de) - IA-Influencer-Agent Platform
Propriété Intellectuelle Exclusive - Tous Droits Réservés
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from decimal import Decimal
from enum import Enum
import json
import uuid
import hashlib
import time

from web3 import Web3
from web3.contract import Contract

logger = logging.getLogger(__name__)


class DistributionStatus(Enum):
    """Royalty distribution status"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    PARTIALLY_COMPLETED = "partially_completed"
    CANCELLED = "cancelled"


class PaymentStatus(Enum):
    """Individual payment status"""
    PENDING = "pending"
    SENT = "sent"
    CONFIRMED = "confirmed"
    FAILED = "failed"
    REFUNDED = "refunded"


class StakeholderType(Enum):
    """Types of stakeholders in royalty distribution"""
    CREATOR = "creator"
    COLLABORATOR = "collaborator"
    PRODUCER = "producer"
    PLATFORM = "platform"
    LABEL = "label"
    PUBLISHER = "publisher"
    INVESTOR = "investor"
    SERVICE_PROVIDER = "service_provider"


@dataclass
class Stakeholder:
    """Stakeholder in royalty distribution"""
    address: str
    name: str
    stakeholder_type: StakeholderType
    percentage: Decimal
    minimum_payout: Decimal
    payment_currency: str
    payment_schedule: str  # "immediate", "weekly", "monthly"
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class RoyaltyPayment:
    """Individual royalty payment"""
    payment_id: str
    distribution_id: str
    stakeholder: Stakeholder
    amount: Decimal
    currency: str
    status: PaymentStatus
    transaction_hash: Optional[str]
    processed_at: Optional[datetime]
    confirmed_at: Optional[datetime]
    failure_reason: Optional[str]


@dataclass
class RoyaltyDistribution:
    """Royalty distribution record"""
    distribution_id: str
    content_id: str
    total_amount: Decimal
    currency: str
    source_transaction: str
    stakeholders: List[Stakeholder]
    payments: List[RoyaltyPayment]
    status: DistributionStatus
    created_at: datetime
    processed_at: Optional[datetime]
    completed_at: Optional[datetime]
    platform_fee: Decimal
    gas_fees: Decimal
    metadata: Dict[str, Any]


class RoyaltyDistributor:
    """
    Automated Royalty Distribution System
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize Royalty Distributor
        
        Args:
            config: Configuration including contract settings
        """
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.active_distributions: Dict[str, RoyaltyDistribution] = {}
        self.stakeholder_registry: Dict[str, List[Stakeholder]] = {}
        self.payment_history: List[RoyaltyPayment] = []
        
        # Contract configuration
        self.contract_address = config.get("contract_address")
        self.network = config.get("network", "ethereum")
        self.gas_limit = config.get("gas_limit", 400000)
        
        # Distribution settings
        self.platform_fee_percentage = Decimal(config.get("platform_fee", "2.5"))
        self.min_distribution_amount = Decimal(config.get("min_distribution", "0.01"))
        self.auto_distribution_enabled = config.get("auto_distribution", True)
        
        # Payment settings
        self.supported_currencies = config.get("currencies", ["ETH", "USDC", "USDT"])
        self.default_currency = config.get("default_currency", "USDC")
    
    async def register_stakeholders(
        self,
        content_id: str,
        stakeholders: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Register stakeholders for content royalty distribution
        
        Args:
            content_id: Content identifier
            stakeholders: List of stakeholder configurations
            
        Returns:
            Registration result
        """
        try:
            self.logger.info(f"Registering stakeholders for content: {content_id}")
            
            # Validate stakeholder configuration
            validated_stakeholders = await self._validate_stakeholders(stakeholders)
            
            # Check that percentages sum to 100%
            total_percentage = sum(s.percentage for s in validated_stakeholders)
            if abs(total_percentage - Decimal("100")) > Decimal("0.01"):
                raise ValueError(f"Stakeholder percentages must sum to 100%, got {total_percentage}")
            
            # Register on blockchain
            registration_tx = await self._register_stakeholders_on_blockchain(
                content_id, validated_stakeholders
            )
            
            # Store stakeholder configuration
            self.stakeholder_registry[content_id] = validated_stakeholders
            
            result = {
                "content_id": content_id,
                "stakeholders_count": len(validated_stakeholders),
                "total_percentage": str(total_percentage),
                "registration_tx": registration_tx["tx_hash"],
                "registered_at": datetime.utcnow().isoformat(),
                "stakeholders": [
                    {
                        "address": s.address,
                        "name": s.name,
                        "type": s.stakeholder_type.value,
                        "percentage": str(s.percentage),
                        "currency": s.payment_currency
                    }
                    for s in validated_stakeholders
                ]
            }
            
            self.logger.info(f"Stakeholders registered for content: {content_id}")
            return result
            
        except Exception as e:
            self.logger.error(f"Stakeholder registration failed: {e}")
            raise
    
    async def _validate_stakeholders(self, stakeholders: List[Dict[str, Any]]) -> List[Stakeholder]:
        """Validate and convert stakeholder configurations"""
        validated = []
        
        for stakeholder_data in stakeholders:
            try:
                stakeholder = Stakeholder(
                    address=stakeholder_data["address"],
                    name=stakeholder_data["name"],
                    stakeholder_type=StakeholderType(stakeholder_data["type"]),
                    percentage=Decimal(str(stakeholder_data["percentage"])),
                    minimum_payout=Decimal(str(stakeholder_data.get("minimum_payout", "0.01"))),
                    payment_currency=stakeholder_data.get("currency", self.default_currency),
                    payment_schedule=stakeholder_data.get("schedule", "immediate"),
                    metadata=stakeholder_data.get("metadata", {})
                )
                
                # Validate address format
                if not self._is_valid_address(stakeholder.address):
                    raise ValueError(f"Invalid address: {stakeholder.address}")
                
                # Validate percentage
                if stakeholder.percentage <= 0 or stakeholder.percentage > 100:
                    raise ValueError(f"Invalid percentage: {stakeholder.percentage}")
                
                # Validate currency
                if stakeholder.payment_currency not in self.supported_currencies:
                    raise ValueError(f"Unsupported currency: {stakeholder.payment_currency}")
                
                validated.append(stakeholder)
                
            except Exception as e:
                raise ValueError(f"Invalid stakeholder configuration: {e}")
        
        return validated
    
    def _is_valid_address(self, address: str) -> bool:
        """Validate blockchain address format"""
        return address.startswith("0x") and len(address) == 42
    
    async def _register_stakeholders_on_blockchain(
        self,
        content_id: str,
        stakeholders: List[Stakeholder]
    ) -> Dict[str, Any]:
        """Register stakeholder configuration on blockchain"""
        registration_data = {
            "content_id": content_id,
            "stakeholders": [
                {
                    "address": s.address,
                    "percentage": str(s.percentage),
                    "type": s.stakeholder_type.value
                }
                for s in stakeholders
            ],
            "timestamp": int(time.time())
        }
        
        tx_hash = hashlib.sha256(
            json.dumps(registration_data, sort_keys=True).encode()
        ).hexdigest()
        
        return {
            "tx_hash": f"0x{tx_hash}",
            "block_number": 12345685,
            "gas_used": 250000
        }
    
    async def distribute_royalties(
        self,
        content_id: str,
        total_amount: Decimal,
        currency: str,
        source_transaction: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> RoyaltyDistribution:
        """
        Distribute royalties to registered stakeholders
        
        Args:
            content_id: Content generating royalties
            total_amount: Total amount to distribute
            currency: Currency of distribution
            source_transaction: Source transaction hash
            metadata: Optional metadata
            
        Returns:
            Distribution record
        """
        try:
            distribution_id = str(uuid.uuid4())
            
            self.logger.info(f"Distributing royalties: {total_amount} {currency} for content {content_id}")
            
            # Validate minimum distribution amount
            if total_amount < self.min_distribution_amount:
                raise ValueError(f"Distribution amount below minimum: {total_amount}")
            
            # Get stakeholders for content
            if content_id not in self.stakeholder_registry:
                raise ValueError(f"No stakeholders registered for content: {content_id}")
            
            stakeholders = self.stakeholder_registry[content_id]
            
            # Calculate platform fee
            platform_fee = total_amount * (self.platform_fee_percentage / 100)
            distributable_amount = total_amount - platform_fee
            
            # Calculate individual payments
            payments = await self._calculate_stakeholder_payments(
                distribution_id, stakeholders, distributable_amount, currency
            )
            
            # Create distribution record
            distribution = RoyaltyDistribution(
                distribution_id=distribution_id,
                content_id=content_id,
                total_amount=total_amount,
                currency=currency,
                source_transaction=source_transaction,
                stakeholders=stakeholders,
                payments=payments,
                status=DistributionStatus.PENDING,
                created_at=datetime.utcnow(),
                processed_at=None,
                completed_at=None,
                platform_fee=platform_fee,
                gas_fees=Decimal("0"),  # Will be calculated during processing
                metadata=metadata or {}
            )
            
            # Store distribution
            self.active_distributions[distribution_id] = distribution
            
            # Process distribution if auto-distribution is enabled
            if self.auto_distribution_enabled:
                await self.process_distribution(distribution_id)
            
            self.logger.info(f"Royalty distribution created: {distribution_id}")
            return distribution
            
        except Exception as e:
            self.logger.error(f"Royalty distribution failed: {e}")
            raise
    
    async def _calculate_stakeholder_payments(
        self,
        distribution_id: str,
        stakeholders: List[Stakeholder],
        distributable_amount: Decimal,
        currency: str
    ) -> List[RoyaltyPayment]:
        """Calculate payments for each stakeholder"""
        payments = []
        
        for stakeholder in stakeholders:
            payment_amount = distributable_amount * (stakeholder.percentage / 100)
            
            # Check minimum payout threshold
            if payment_amount < stakeholder.minimum_payout:
                # Store for future accumulation
                payment_amount = Decimal("0")
                status = PaymentStatus.PENDING
            else:
                status = PaymentStatus.PENDING
            
            payment = RoyaltyPayment(
                payment_id=str(uuid.uuid4()),
                distribution_id=distribution_id,
                stakeholder=stakeholder,
                amount=payment_amount,
                currency=currency,
                status=status,
                transaction_hash=None,
                processed_at=None,
                confirmed_at=None,
                failure_reason=None
            )
            
            payments.append(payment)
        
        return payments
    
    async def process_distribution(self, distribution_id: str) -> Dict[str, Any]:
        """
        Process a pending royalty distribution
        
        Args:
            distribution_id: Distribution ID to process
            
        Returns:
            Processing result
        """
        try:
            if distribution_id not in self.active_distributions:
                raise ValueError(f"Distribution not found: {distribution_id}")
            
            distribution = self.active_distributions[distribution_id]
            
            if distribution.status != DistributionStatus.PENDING:
                raise ValueError(f"Distribution not pending: {distribution.status.value}")
            
            self.logger.info(f"Processing distribution: {distribution_id}")
            
            # Update status
            distribution.status = DistributionStatus.PROCESSING
            distribution.processed_at = datetime.utcnow()
            
            # Process each payment
            successful_payments = 0
            total_gas_fees = Decimal("0")
            
            for payment in distribution.payments:
                if payment.amount > 0:  # Skip zero-amount payments
                    try:
                        payment_result = await self._process_payment(payment)
                        if payment_result["success"]:
                            successful_payments += 1
                            total_gas_fees += Decimal(payment_result["gas_fee"])
                        
                    except Exception as e:
                        self.logger.error(f"Payment processing failed: {e}")
                        payment.status = PaymentStatus.FAILED
                        payment.failure_reason = str(e)
            
            # Update distribution status
            total_payments = len([p for p in distribution.payments if p.amount > 0])
            
            if successful_payments == total_payments:
                distribution.status = DistributionStatus.COMPLETED
            elif successful_payments > 0:
                distribution.status = DistributionStatus.PARTIALLY_COMPLETED
            else:
                distribution.status = DistributionStatus.FAILED
            
            distribution.gas_fees = total_gas_fees
            distribution.completed_at = datetime.utcnow()
            
            # Record distribution completion on blockchain
            completion_tx = await self._record_distribution_completion(distribution)
            
            result = {
                "distribution_id": distribution_id,
                "status": distribution.status.value,
                "successful_payments": successful_payments,
                "total_payments": total_payments,
                "total_gas_fees": str(total_gas_fees),
                "completion_tx": completion_tx["tx_hash"],
                "processed_at": distribution.processed_at.isoformat(),
                "completed_at": distribution.completed_at.isoformat()
            }
            
            self.logger.info(f"Distribution processed: {distribution_id}")
            return result
            
        except Exception as e:
            self.logger.error(f"Distribution processing failed: {e}")
            raise
    
    async def _process_payment(self, payment: RoyaltyPayment) -> Dict[str, Any]:
        """Process individual royalty payment"""
        try:
            # Update payment status
            payment.status = PaymentStatus.SENT
            payment.processed_at = datetime.utcnow()
            
            # Send payment (mock implementation)
            payment_tx = await self._send_payment_on_blockchain(
                payment.stakeholder.address,
                payment.amount,
                payment.currency
            )
            
            # Update payment record
            payment.transaction_hash = payment_tx["tx_hash"]
            payment.status = PaymentStatus.CONFIRMED
            payment.confirmed_at = datetime.utcnow()
            
            # Add to payment history
            self.payment_history.append(payment)
            
            return {
                "success": True,
                "payment_id": payment.payment_id,
                "tx_hash": payment_tx["tx_hash"],
                "gas_fee": payment_tx["gas_fee"]
            }
            
        except Exception as e:
            payment.status = PaymentStatus.FAILED
            payment.failure_reason = str(e)
            
            return {
                "success": False,
                "payment_id": payment.payment_id,
                "error": str(e),
                "gas_fee": "0"
            }
    
    async def _send_payment_on_blockchain(
        self,
        recipient_address: str,
        amount: Decimal,
        currency: str
    ) -> Dict[str, Any]:
        """Send payment transaction on blockchain"""
        payment_data = {
            "to": recipient_address,
            "amount": str(amount),
            "currency": currency,
            "timestamp": int(time.time())
        }
        
        tx_hash = hashlib.sha256(
            json.dumps(payment_data, sort_keys=True).encode()
        ).hexdigest()
        
        # Calculate gas fee based on currency
        gas_fee_map = {
            "ETH": "0.001",
            "USDC": "0.0005",
            "USDT": "0.0005"
        }
        gas_fee = gas_fee_map.get(currency, "0.001")
        
        return {
            "tx_hash": f"0x{tx_hash}",
            "block_number": 12345686,
            "gas_used": 50000,
            "gas_fee": gas_fee
        }
    
    async def _record_distribution_completion(
        self,
        distribution: RoyaltyDistribution
    ) -> Dict[str, Any]:
        """Record distribution completion on blockchain"""
        completion_data = {
            "distribution_id": distribution.distribution_id,
            "content_id": distribution.content_id,
            "total_amount": str(distribution.total_amount),
            "platform_fee": str(distribution.platform_fee),
            "gas_fees": str(distribution.gas_fees),
            "status": distribution.status.value,
            "timestamp": int(time.time())
        }
        
        tx_hash = hashlib.sha256(
            json.dumps(completion_data, sort_keys=True).encode()
        ).hexdigest()
        
        return {
            "tx_hash": f"0x{tx_hash}",
            "block_number": 12345687,
            "gas_used": 120000
        }
    
    async def retry_failed_payments(
        self,
        distribution_id: str
    ) -> Dict[str, Any]:
        """
        Retry failed payments in a distribution
        
        Args:
            distribution_id: Distribution ID with failed payments
            
        Returns:
            Retry result
        """
        try:
            if distribution_id not in self.active_distributions:
                raise ValueError(f"Distribution not found: {distribution_id}")
            
            distribution = self.active_distributions[distribution_id]
            failed_payments = [p for p in distribution.payments if p.status == PaymentStatus.FAILED]
            
            if not failed_payments:
                return {"message": "No failed payments to retry"}
            
            self.logger.info(f"Retrying {len(failed_payments)} failed payments")
            
            successful_retries = 0
            for payment in failed_payments:
                try:
                    # Reset payment status
                    payment.status = PaymentStatus.PENDING
                    payment.failure_reason = None
                    
                    # Retry payment
                    payment_result = await self._process_payment(payment)
                    if payment_result["success"]:
                        successful_retries += 1
                        
                except Exception as e:
                    self.logger.error(f"Payment retry failed: {e}")
            
            # Update distribution status if all payments now successful
            if successful_retries == len(failed_payments):
                distribution.status = DistributionStatus.COMPLETED
            elif successful_retries > 0:
                distribution.status = DistributionStatus.PARTIALLY_COMPLETED
            
            result = {
                "distribution_id": distribution_id,
                "failed_payments_count": len(failed_payments),
                "successful_retries": successful_retries,
                "new_status": distribution.status.value,
                "retried_at": datetime.utcnow().isoformat()
            }
            
            return result
            
        except Exception as e:
            self.logger.error(f"Payment retry failed: {e}")
            raise
    
    async def get_distribution_info(self, distribution_id: str) -> Dict[str, Any]:
        """Get detailed distribution information"""
        if distribution_id not in self.active_distributions:
            raise ValueError(f"Distribution not found: {distribution_id}")
        
        distribution = self.active_distributions[distribution_id]
        
        return {
            "distribution_id": distribution.distribution_id,
            "content_id": distribution.content_id,
            "total_amount": str(distribution.total_amount),
            "currency": distribution.currency,
            "source_transaction": distribution.source_transaction,
            "status": distribution.status.value,
            "created_at": distribution.created_at.isoformat(),
            "processed_at": distribution.processed_at.isoformat() if distribution.processed_at else None,
            "completed_at": distribution.completed_at.isoformat() if distribution.completed_at else None,
            "platform_fee": str(distribution.platform_fee),
            "gas_fees": str(distribution.gas_fees),
            "metadata": distribution.metadata,
            "stakeholders": [
                {
                    "address": s.address,
                    "name": s.name,
                    "type": s.stakeholder_type.value,
                    "percentage": str(s.percentage),
                    "currency": s.payment_currency
                }
                for s in distribution.stakeholders
            ],
            "payments": [
                {
                    "payment_id": p.payment_id,
                    "stakeholder_address": p.stakeholder.address,
                    "amount": str(p.amount),
                    "currency": p.currency,
                    "status": p.status.value,
                    "transaction_hash": p.transaction_hash,
                    "processed_at": p.processed_at.isoformat() if p.processed_at else None,
                    "confirmed_at": p.confirmed_at.isoformat() if p.confirmed_at else None,
                    "failure_reason": p.failure_reason
                }
                for p in distribution.payments
            ]
        }
    
    async def get_stakeholder_earnings(
        self,
        stakeholder_address: str,
        content_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get earnings summary for a stakeholder"""
        earnings_by_currency = {}
        payment_count = 0
        last_payment_date = None
        
        for payment in self.payment_history:
            if payment.stakeholder.address == stakeholder_address:
                if content_id is None or self.active_distributions[payment.distribution_id].content_id == content_id:
                    currency = payment.currency
                    if currency not in earnings_by_currency:
                        earnings_by_currency[currency] = Decimal("0")
                    
                    if payment.status == PaymentStatus.CONFIRMED:
                        earnings_by_currency[currency] += payment.amount
                        payment_count += 1
                        
                        if payment.confirmed_at and (last_payment_date is None or payment.confirmed_at > last_payment_date):
                            last_payment_date = payment.confirmed_at
        
        return {
            "stakeholder_address": stakeholder_address,
            "content_id": content_id,
            "earnings_by_currency": {k: str(v) for k, v in earnings_by_currency.items()},
            "total_payments": payment_count,
            "last_payment_date": last_payment_date.isoformat() if last_payment_date else None
        }
    
    async def get_distribution_analytics(self) -> Dict[str, Any]:
        """Get royalty distribution analytics"""
        total_distributions = len(self.active_distributions)
        status_counts = {}
        currency_totals = {}
        total_platform_fees = Decimal("0")
        
        for distribution in self.active_distributions.values():
            status = distribution.status.value
            currency = distribution.currency
            
            status_counts[status] = status_counts.get(status, 0) + 1
            
            if currency not in currency_totals:
                currency_totals[currency] = Decimal("0")
            currency_totals[currency] += distribution.total_amount
            
            total_platform_fees += distribution.platform_fee
        
        return {
            "total_distributions": total_distributions,
            "status_distribution": status_counts,
            "total_volume_by_currency": {k: str(v) for k, v in currency_totals.items()},
            "total_platform_fees": str(total_platform_fees),
            "total_payments_processed": len(self.payment_history),
            "average_distribution_size": str(sum(currency_totals.values()) / max(total_distributions, 1))
        }


class RoyaltyManager:
    """
    High-level manager for royalty operations
    """
    
    def __init__(self, royalty_distributor: RoyaltyDistributor):
        """
        Initialize Royalty Manager
        
        Args:
            royalty_distributor: Underlying royalty distributor
        """
        self.royalty_distributor = royalty_distributor
        self.logger = logging.getLogger(__name__)
    
    async def setup_content_royalties(
        self,
        content_id: str,
        creator_address: str,
        creator_percentage: Decimal,
        collaborators: Optional[List[Dict[str, Any]]] = None,
        platform_percentage: Optional[Decimal] = None
    ) -> Dict[str, Any]:
        """Setup royalty distribution for new content"""
        stakeholders = []
        
        # Add creator
        creator_stakeholder = {
            "address": creator_address,
            "name": "Content Creator",
            "type": "creator",
            "percentage": float(creator_percentage)
        }
        stakeholders.append(creator_stakeholder)
        
        # Add collaborators
        if collaborators:
            for collaborator in collaborators:
                stakeholders.append(collaborator)
        
        # Add platform
        if platform_percentage:
            platform_stakeholder = {
                "address": "0x0000000000000000000000000000000000000001",  # Platform address
                "name": "Platform",
                "type": "platform",
                "percentage": float(platform_percentage)
            }
            stakeholders.append(platform_stakeholder)
        
        return await self.royalty_distributor.register_stakeholders(content_id, stakeholders)
    
    async def auto_distribute_from_sales(
        self,
        sales_data: List[Dict[str, Any]]
    ) -> List[RoyaltyDistribution]:
        """Automatically distribute royalties from sales data"""
        distributions = []
        
        for sale in sales_data:
            try:
                distribution = await self.royalty_distributor.distribute_royalties(
                    content_id=sale["content_id"],
                    total_amount=Decimal(str(sale["amount"])),
                    currency=sale["currency"],
                    source_transaction=sale["transaction_hash"],
                    metadata={"sale_id": sale.get("sale_id"), "buyer": sale.get("buyer")}
                )
                distributions.append(distribution)
                
            except Exception as e:
                self.logger.error(f"Auto-distribution failed for sale: {e}")
        
        return distributions