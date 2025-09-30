"""💳 Multi-Provider Payment Gateway
=================================

Unified payment gateway orchestrating multiple payment providers for marketplace
split payments, escrow services, international transfers, and cryptocurrency payments.

Features:
- Stripe Connect for marketplace split payments
- PayPal Business with split payments + escrow
- Wise for international payments
- Crypto support for Bitcoin, Ethereum, USDC

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass
from enum import Enum
from datetime import datetime, timedelta
from decimal import Decimal
import uuid

from .processors.stripe import StripeConnectProcessor
from .processors.paypal_business import PayPalBusinessProcessor
from .processors.wise_multi_currency import WiseMultiCurrencyProcessor
from .processors.crypto_payments import CryptoPaymentsProcessor

logger = logging.getLogger(__name__)


class PaymentProvider(Enum):
    """Supported payment providers"""
    STRIPE_CONNECT = "stripe_connect"
    PAYPAL_BUSINESS = "paypal_business"
    WISE = "wise"
    CRYPTO = "crypto"


class PaymentType(Enum):
    """Payment transaction types"""
    SIMPLE_PAYMENT = "simple_payment"
    MARKETPLACE_SPLIT = "marketplace_split"
    ESCROW_PAYMENT = "escrow_payment"
    INTERNATIONAL_TRANSFER = "international_transfer"
    CRYPTO_TRANSFER = "crypto_transfer"


class PaymentStatus(Enum):
    """Payment status"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    DISPUTED = "disputed"
    ESCROWED = "escrowed"
    RELEASED = "released"


@dataclass
class PaymentRequest:
    """Unified payment request structure"""
    amount: Decimal
    currency: str
    payment_type: PaymentType
    provider: PaymentProvider
    sender_id: str
    recipient_id: str
    description: str
    metadata: Optional[Dict[str, Any]] = None
    
    # Marketplace split payment fields
    platform_fee_percent: Optional[Decimal] = None
    recipients: Optional[List[Dict[str, Any]]] = None
    
    # Escrow fields
    escrow_release_date: Optional[datetime] = None
    escrow_conditions: Optional[Dict[str, Any]] = None
    
    # International transfer fields
    recipient_country: Optional[str] = None
    transfer_purpose: Optional[str] = None
    
    # Crypto fields
    from_address: Optional[str] = None
    to_address: Optional[str] = None
    network: Optional[str] = None


@dataclass
class PaymentResponse:
    """Unified payment response structure"""
    transaction_id: str
    status: PaymentStatus
    provider: PaymentProvider
    amount: Decimal
    currency: str
    fees: Dict[str, Decimal]
    provider_response: Dict[str, Any]
    created_at: datetime
    
    # Split payment details
    splits: Optional[List[Dict[str, Any]]] = None
    
    # Escrow details
    escrow_id: Optional[str] = None
    
    # Provider-specific data
    provider_transaction_id: Optional[str] = None
    external_url: Optional[str] = None


class MultiProviderPaymentGateway:
    """
    Unified payment gateway that orchestrates multiple payment providers
    for different payment scenarios and requirements.
    """
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize multi-provider payment gateway"""
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Initialize payment processors
        self.processors = {}
        self._initialize_processors()
        
        # Transaction tracking
        self.transactions = {}
        self.escrow_transactions = {}
        
    def _initialize_processors(self):
        """Initialize all payment processors"""
        try:
            # Stripe Connect for marketplace payments
            if "stripe" in self.config:
                self.processors[PaymentProvider.STRIPE_CONNECT] = StripeConnectProcessor(
                    api_key=self.config["stripe"].get("api_key"),
                    webhook_secret=self.config["stripe"].get("webhook_secret"),
                    connect_enabled=True
                )
            
            # PayPal Business for escrow and splits
            if "paypal" in self.config:
                self.processors[PaymentProvider.PAYPAL_BUSINESS] = PayPalBusinessProcessor(
                    client_id=self.config["paypal"].get("client_id"),
                    client_secret=self.config["paypal"].get("client_secret"),
                    environment=self.config["paypal"].get("environment", "sandbox")
                )
            
            # Wise for international transfers
            if "wise" in self.config:
                self.processors[PaymentProvider.WISE] = WiseMultiCurrencyProcessor(
                    api_token=self.config["wise"].get("api_token"),
                    webhook_secret=self.config["wise"].get("webhook_secret")
                )
            
            # Crypto processors
            if "crypto" in self.config:
                self.processors[PaymentProvider.CRYPTO] = CryptoPaymentsProcessor(
                    api_keys=self.config["crypto"].get("api_keys", {}),
                    webhook_secret=self.config["crypto"].get("webhook_secret"),
                    testnet=self.config["crypto"].get("testnet", True)
                )
                
            self.logger.info(f"Initialized {len(self.processors)} payment processors")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize processors: {e}")
            raise
    
    async def process_payment(self, request: PaymentRequest) -> PaymentResponse:
        """
        Process payment request through appropriate provider
        """
        try:
            # Validate request
            self._validate_payment_request(request)
            
            # Route to appropriate processor based on payment type
            if request.payment_type == PaymentType.MARKETPLACE_SPLIT:
                return await self._process_marketplace_split(request)
            elif request.payment_type == PaymentType.ESCROW_PAYMENT:
                return await self._process_escrow_payment(request)
            elif request.payment_type == PaymentType.INTERNATIONAL_TRANSFER:
                return await self._process_international_transfer(request)
            elif request.payment_type == PaymentType.CRYPTO_TRANSFER:
                return await self._process_crypto_transfer(request)
            else:
                return await self._process_simple_payment(request)
                
        except Exception as e:
            self.logger.error(f"Payment processing failed: {e}")
            raise
    
    async def _process_marketplace_split(self, request: PaymentRequest) -> PaymentResponse:
        """Process marketplace split payment using Stripe Connect"""
        try:
            processor = self.processors[PaymentProvider.STRIPE_CONNECT]
            
            # Calculate platform fee
            if request.platform_fee_percent:
                platform_fee = request.amount * request.platform_fee_percent
            else:
                platform_fee = request.amount * Decimal("0.025")  # Default 2.5%
            
            # Create payment intent with application fee
            payment_intent = await processor.create_payment_intent(
                amount=request.amount,
                currency=request.currency,
                connected_account_id=request.recipient_id,
                application_fee_amount=platform_fee
            )
            
            # Track transaction
            transaction_id = f"mp_{uuid.uuid4().hex[:16]}"
            
            response = PaymentResponse(
                transaction_id=transaction_id,
                status=PaymentStatus.PENDING,
                provider=PaymentProvider.STRIPE_CONNECT,
                amount=request.amount,
                currency=request.currency,
                fees={
                    "platform_fee": platform_fee,
                    "stripe_fee": request.amount * Decimal("0.029") + Decimal("0.30")
                },
                provider_response=payment_intent.__dict__,
                created_at=datetime.now(),
                provider_transaction_id=payment_intent.id
            )
            
            self.transactions[transaction_id] = response
            return response
            
        except Exception as e:
            self.logger.error(f"Marketplace split payment failed: {e}")
            raise
    
    async def _process_escrow_payment(self, request: PaymentRequest) -> PaymentResponse:
        """Process escrow payment using PayPal Business"""
        try:
            processor = self.processors[PaymentProvider.PAYPAL_BUSINESS]
            
            # Authenticate with PayPal
            await processor.authenticate()
            
            # Create PayPal order with escrow conditions
            order = await processor.create_order(
                amount=request.amount,
                currency=request.currency,
                return_url="https://platform.example.com/return",
                cancel_url="https://platform.example.com/cancel",
                payee_email=request.metadata.get("recipient_email") if request.metadata else None
            )
            
            # Create escrow record
            escrow_id = f"escrow_{uuid.uuid4().hex[:16]}"
            self.escrow_transactions[escrow_id] = {
                "transaction_id": order.id,
                "amount": request.amount,
                "currency": request.currency,
                "sender_id": request.sender_id,
                "recipient_id": request.recipient_id,
                "release_date": request.escrow_release_date,
                "conditions": request.escrow_conditions,
                "status": "escrowed",
                "created_at": datetime.now()
            }
            
            transaction_id = f"esc_{uuid.uuid4().hex[:16]}"
            
            response = PaymentResponse(
                transaction_id=transaction_id,
                status=PaymentStatus.ESCROWED,
                provider=PaymentProvider.PAYPAL_BUSINESS,
                amount=request.amount,
                currency=request.currency,
                fees={
                    "paypal_fee": request.amount * Decimal("0.0349") + Decimal("0.49")
                },
                provider_response=order.__dict__,
                created_at=datetime.now(),
                escrow_id=escrow_id,
                provider_transaction_id=order.id
            )
            
            self.transactions[transaction_id] = response
            return response
            
        except Exception as e:
            self.logger.error(f"Escrow payment failed: {e}")
            raise
    
    async def _process_international_transfer(self, request: PaymentRequest) -> PaymentResponse:
        """Process international transfer using Wise"""
        try:
            processor = self.processors[PaymentProvider.WISE]
            
            # Get exchange rate quote
            quote = await processor.create_quote(
                profile_id=123456,  # Mock profile ID
                source_currency=request.currency,
                target_currency=request.metadata.get("target_currency", "USD") if request.metadata else "USD",
                source_amount=request.amount
            )
            
            # Calculate transfer fee
            fee = processor.calculate_fee(
                amount=request.amount,
                source_currency=request.currency,
                target_currency=request.metadata.get("target_currency", "USD") if request.metadata else "USD"
            )
            
            transaction_id = f"wise_{uuid.uuid4().hex[:16]}"
            
            response = PaymentResponse(
                transaction_id=transaction_id,
                status=PaymentStatus.PENDING,
                provider=PaymentProvider.WISE,
                amount=request.amount,
                currency=request.currency,
                fees={
                    "wise_fee": fee,
                    "exchange_rate": Decimal(str(quote["rate"]))
                },
                provider_response=quote,
                created_at=datetime.now(),
                provider_transaction_id=quote["id"]
            )
            
            self.transactions[transaction_id] = response
            return response
            
        except Exception as e:
            self.logger.error(f"International transfer failed: {e}")
            raise
    
    async def _process_crypto_transfer(self, request: PaymentRequest) -> PaymentResponse:
        """Process cryptocurrency transfer"""
        try:
            processor = self.processors[PaymentProvider.CRYPTO]
            
            # Create crypto transaction using send_transaction
            from .processors.crypto_payments import CryptoCurrency, BlockchainNetwork
            
            # Convert string currency to enum
            currency_enum = CryptoCurrency(request.currency)
            network_enum = BlockchainNetwork(request.network)
            
            crypto_tx = await processor.send_transaction(
                from_address=request.from_address,
                to_address=request.to_address,
                amount=request.amount,
                currency=currency_enum,
                network=network_enum,
                private_key="mock_private_key"  # In real implementation, this would be securely handled
            )
            
            transaction_id = f"crypto_{uuid.uuid4().hex[:16]}"
            
            response = PaymentResponse(
                transaction_id=transaction_id,
                status=PaymentStatus.PENDING,
                provider=PaymentProvider.CRYPTO,
                amount=request.amount,
                currency=request.currency,
                fees={
                    "network_fee": crypto_tx.gas_fee,
                    "processing_fee": request.amount * Decimal("0.01")  # 1% processing fee
                },
                provider_response=crypto_tx.__dict__,
                created_at=datetime.now(),
                provider_transaction_id=crypto_tx.id
            )
            
            self.transactions[transaction_id] = response
            return response
            
        except Exception as e:
            self.logger.error(f"Crypto transfer failed: {e}")
            raise
    
    async def _process_simple_payment(self, request: PaymentRequest) -> PaymentResponse:
        """Process simple payment through preferred provider"""
        try:
            # Default to Stripe for simple payments
            processor = self.processors[PaymentProvider.STRIPE_CONNECT]
            
            # Create payment intent
            payment_intent = await processor.create_payment_intent(
                amount=request.amount,
                currency=request.currency,
                connected_account_id=request.recipient_id
            )
            
            transaction_id = f"simple_{uuid.uuid4().hex[:16]}"
            
            response = PaymentResponse(
                transaction_id=transaction_id,
                status=PaymentStatus.PENDING,
                provider=PaymentProvider.STRIPE_CONNECT,
                amount=request.amount,
                currency=request.currency,
                fees={
                    "stripe_fee": request.amount * Decimal("0.029") + Decimal("0.30")
                },
                provider_response=payment_intent.__dict__,
                created_at=datetime.now(),
                provider_transaction_id=payment_intent.id
            )
            
            self.transactions[transaction_id] = response
            return response
            
        except Exception as e:
            self.logger.error(f"Simple payment failed: {e}")
            raise
    
    async def release_escrow(self, escrow_id: str, release_conditions: Dict[str, Any]) -> Dict[str, Any]:
        """Release funds from escrow"""
        try:
            if escrow_id not in self.escrow_transactions:
                raise ValueError(f"Escrow transaction {escrow_id} not found")
            
            escrow = self.escrow_transactions[escrow_id]
            
            # Validate release conditions
            if escrow["status"] != "escrowed":
                raise ValueError(f"Escrow {escrow_id} is not in escrowed status")
            
            # Process release through PayPal
            processor = self.processors[PaymentProvider.PAYPAL_BUSINESS]
            await processor.authenticate()
            
            # Simulate escrow release
            release_result = {
                "success": True,
                "escrow_id": escrow_id,
                "amount": escrow["amount"],
                "currency": escrow["currency"],
                "released_at": datetime.now(),
                "release_conditions": release_conditions
            }
            
            # Update escrow status
            escrow["status"] = "released"
            escrow["released_at"] = datetime.now()
            
            self.logger.info(f"Escrow {escrow_id} released successfully")
            return release_result
            
        except Exception as e:
            self.logger.error(f"Escrow release failed: {e}")
            raise
    
    async def get_transaction_status(self, transaction_id: str) -> Dict[str, Any]:
        """Get current status of a transaction"""
        try:
            if transaction_id not in self.transactions:
                raise ValueError(f"Transaction {transaction_id} not found")
            
            transaction = self.transactions[transaction_id]
            
            # Get updated status from provider
            provider_status = await self._get_provider_status(transaction)
            
            return {
                "transaction_id": transaction_id,
                "status": transaction.status.value,
                "provider": transaction.provider.value,
                "amount": float(transaction.amount),
                "currency": transaction.currency,
                "created_at": transaction.created_at.isoformat(),
                "provider_status": provider_status,
                "fees": {k: float(v) for k, v in transaction.fees.items()}
            }
            
        except Exception as e:
            self.logger.error(f"Failed to get transaction status: {e}")
            raise
    
    async def _get_provider_status(self, transaction: PaymentResponse) -> Dict[str, Any]:
        """Get status from the payment provider"""
        try:
            # This would normally query the actual provider API
            # For now, simulate status updates
            return {
                "provider_transaction_id": transaction.provider_transaction_id,
                "status": "completed",
                "updated_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Failed to get provider status: {e}")
            return {"error": str(e)}
    
    def _validate_payment_request(self, request: PaymentRequest):
        """Validate payment request"""
        if request.amount <= 0:
            raise ValueError("Payment amount must be positive")
        
        # Allow crypto currencies which can be longer than 3 characters
        if not request.currency or (len(request.currency) not in [3, 4] and request.currency not in ["BTC", "ETH", "USDC", "USDT"]):
            raise ValueError("Invalid currency code")
        
        if request.provider not in self.processors:
            raise ValueError(f"Provider {request.provider} not available")
        
        # Payment type specific validations
        if request.payment_type == PaymentType.MARKETPLACE_SPLIT and not request.recipients:
            raise ValueError("Recipients required for marketplace split payments")
        
        if request.payment_type == PaymentType.ESCROW_PAYMENT and not request.escrow_release_date:
            raise ValueError("Escrow release date required for escrow payments")
        
        if request.payment_type == PaymentType.CRYPTO_TRANSFER:
            if not request.from_address or not request.to_address:
                raise ValueError("Crypto addresses required for crypto transfers")


# Export main classes
__all__ = [
    "MultiProviderPaymentGateway",
    "PaymentRequest", 
    "PaymentResponse",
    "PaymentProvider",
    "PaymentType",
    "PaymentStatus"
]