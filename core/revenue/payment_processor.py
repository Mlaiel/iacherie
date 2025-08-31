"""
Revenue Payment Processing System - Multi-Payment Gateway Integration

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: © 2025 Fahed Mlaiel. All rights reserved.

  STRICT COPYRIGHT WARNING 
This code is the exclusive intellectual property of Fahed Mlaiel.
Unauthorized use, reproduction, modification, or distribution without explicit 
written permission from the author is strictly prohibited.

Contact: mlaiel@live.de for licensing inquiries.


PAYMENT PROCESSING SYSTEM - ENTERPRISE EDITION


Developed by Expert Team:
 Lead Dev IA: Fahed Mlaiel (Advanced AI/ML Architecture)
  Backend Senior: System Architecture & Performance Optimization  
🤖 ML Engineer: Payment Intelligence & Fraud Detection
  DBA: Advanced Data Management & Analytics
 Security Expert: Enterprise-Grade Security & Encryption
 Microservices: Scalable Distributed Architecture
 Audio Expert: Audio Revenue Payment Processing
  DevOps: Production Infrastructure & Monitoring
🧠 IA Prompt Engineer: AI-Powered Payment Optimization
"""

import asyncio
import logging
from datetime import datetime, timedelta
from decimal import Decimal, ROUND_HALF_UP
from enum import Enum
from typing import Dict, List, Optional, Any, Union, Tuple
from dataclasses import dataclass, field
from abc import ABC, abstractmethod
import uuid
import json
import hmac
import hashlib
import aiohttp
import numpy as np

from ..utils.exceptions import PaymentProcessingError
from ..utils.validators import validate_payment_data
from ..utils.cache import cache_payment_results
from ..analytics.metrics import MetricsCollector
from ..security.encryption import EncryptionManager

logger = logging.getLogger(__name__)


class PaymentProvider(Enum):
    """Supported payment providers"""
    STRIPE = "stripe"
    PAYPAL = "paypal"
    WISE = "wise"
    BANK_TRANSFER = "bank_transfer"
    CRYPTOCURRENCY = "cryptocurrency"
    APPLE_PAY = "apple_pay"
    GOOGLE_PAY = "google_pay"
    REVOLUT = "revolut"
    KLARNA = "klarna"
    ADYEN = "adyen"


class PaymentType(Enum):
    """Types of payments"""
    REVENUE_PAYOUT = "revenue_payout"
    LICENSING_PAYMENT = "licensing_payment"
    ROYALTY_PAYMENT = "royalty_payment"
    COLLABORATION_SPLIT = "collaboration_split"
    REFUND = "refund"
    SUBSCRIPTION = "subscription"
    ONE_TIME_PAYMENT = "one_time_payment"


class PaymentStatus(Enum):
    """Payment processing status"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    REFUNDED = "refunded"
    ON_HOLD = "on_hold"
    REQUIRES_ACTION = "requires_action"


class PaymentFrequency(Enum):
    """Payment frequency options"""
    IMMEDIATE = "immediate"
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    YEARLY = "yearly"
    CUSTOM = "custom"


class CurrencyCode(Enum):
    """Supported currency codes"""
    USD = "USD"
    EUR = "EUR"
    GBP = "GBP"
    JPY = "JPY"
    CAD = "CAD"
    AUD = "AUD"
    CHF = "CHF"
    CNY = "CNY"
    SEK = "SEK"
    NOK = "NOK"
    DKK = "DKK"
    PLN = "PLN"
    CZK = "CZK"
    HUF = "HUF"
    BRL = "BRL"
    MXN = "MXN"
    SGD = "SGD"
    HKD = "HKD"
    NZD = "NZD"
    KRW = "KRW"


@dataclass
class PaymentAccount:
    """Payment account information"""
    account_id: str
    user_id: str
    provider: PaymentProvider
    account_type: str  # business, personal
    account_details: Dict[str, Any]  # Encrypted account details
    supported_currencies: List[CurrencyCode]
    is_verified: bool = False
    is_active: bool = True
    verification_documents: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.utcnow)
    
    @property
    def masked_account_info(self) -> Dict[str, str]:
        """Get masked account information for display"""
        masked = {}
        
        if self.provider == PaymentProvider.STRIPE:
            masked['account_id'] = f"acct_****{self.account_details.get('account_id', '')[-4:]}"
        elif self.provider == PaymentProvider.PAYPAL:
            email = self.account_details.get('email', '')
            masked['email'] = f"{email[:3]}***@{email.split('@')[1]}" if '@' in email else "***"
        elif self.provider == PaymentProvider.BANK_TRANSFER:
            iban = self.account_details.get('iban', '')
            masked['iban'] = f"****{iban[-4:]}" if iban else "****"
        
        return masked


@dataclass
class PaymentMethod:
    """Payment method configuration"""
    method_id: str
    user_id: str
    provider: PaymentProvider
    payment_type: PaymentType
    account: PaymentAccount
    priority: int = 1
    minimum_amount: Decimal = Decimal('10.00')
    maximum_amount: Optional[Decimal] = None
    fees: Dict[str, Decimal] = field(default_factory=dict)
    processing_time: timedelta = field(default_factory=lambda: timedelta(days=1))
    is_default: bool = False
    is_active: bool = True


@dataclass
class PaymentRequest:
    """Payment request structure"""
    request_id: str
    user_id: str
    recipient_id: str
    amount: Decimal
    currency: CurrencyCode
    payment_type: PaymentType
    description: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    payment_method_id: Optional[str] = None
    scheduled_date: Optional[datetime] = None
    frequency: PaymentFrequency = PaymentFrequency.IMMEDIATE
    reference: Optional[str] = None
    
    def __post_init__(self):
        if self.amount <= 0:
            raise ValueError("Payment amount must be positive")


@dataclass
class PaymentTransaction:
    """Payment transaction record"""
    transaction_id: str
    request_id: str
    user_id: str
    recipient_id: str
    amount: Decimal
    currency: CurrencyCode
    payment_provider: PaymentProvider
    provider_transaction_id: Optional[str] = None
    status: PaymentStatus = PaymentStatus.PENDING
    fees: Dict[str, Decimal] = field(default_factory=dict)
    exchange_rate: Optional[Decimal] = None
    processed_amount: Optional[Decimal] = None
    processed_currency: Optional[CurrencyCode] = None
    error_message: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.utcnow)
    processed_at: Optional[datetime] = None
    
    @property
    def net_amount(self) -> Decimal:
        """Calculate net amount after fees"""
        total_fees = sum(self.fees.values())
        return self.amount - total_fees
    
    @property
    def processing_time(self) -> Optional[timedelta]:
        """Calculate processing time"""
        if self.processed_at and self.created_at:
            return self.processed_at - self.created_at
        return None


class BasePaymentProcessor(ABC):
    """Base class for payment processors"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.session = None
        self.encryption_manager = EncryptionManager()
    
    async def initialize(self) -> None:
        """Initialize payment processor"""
        self.session = aiohttp.ClientSession()
        await self._setup_authentication()
    
    async def cleanup(self) -> None:
        """Cleanup resources"""
        if self.session:
            await self.session.close()
    
    @abstractmethod
    async def create_payment(self, request: PaymentRequest) -> PaymentTransaction:
        """Create payment transaction"""
        pass
    
    @abstractmethod
    async def process_payment(self, transaction: PaymentTransaction) -> PaymentTransaction:
        """Process payment transaction"""
        pass
    
    @abstractmethod
    async def get_transaction_status(self, transaction_id: str) -> PaymentStatus:
        """Get transaction status"""
        pass
    
    @abstractmethod
    async def cancel_payment(self, transaction_id: str) -> bool:
        """Cancel payment transaction"""
        pass
    
    @abstractmethod
    async def refund_payment(self, transaction_id: str, amount: Optional[Decimal] = None) -> PaymentTransaction:
        """Refund payment transaction"""
        pass
    
    async def _setup_authentication(self) -> None:
        """Setup authentication for payment provider"""
        pass
    
    def _calculate_fees(self, amount: Decimal, currency: CurrencyCode) -> Dict[str, Decimal]:
        """Calculate processing fees"""
        fees = {}
        
        # Base processing fee (typically percentage + fixed fee)
        base_percentage = self.config.get('base_fee_percentage', Decimal('2.9'))
        fixed_fee = self.config.get('fixed_fee', Decimal('0.30'))
        
        processing_fee = (amount * base_percentage / 100) + fixed_fee
        fees['processing'] = processing_fee.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
        
        # Currency conversion fee if applicable
        if currency != CurrencyCode.USD:
            conversion_fee = amount * self.config.get('conversion_fee_percentage', Decimal('1.0')) / 100
            fees['conversion'] = conversion_fee.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
        
        return fees


class StripePaymentProcessor(BasePaymentProcessor):
    """Stripe payment processor implementation"""
    
    async def _setup_authentication(self) -> None:
        """Setup Stripe authentication"""
        self.api_key = self.config.get('api_key')
        self.webhook_secret = self.config.get('webhook_secret')
        self.headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/x-www-form-urlencoded'
        }
    
    async def create_payment(self, request: PaymentRequest) -> PaymentTransaction:
        """Create Stripe payment"""



        try:
            transaction_id = str(uuid.uuid4())
            
            # Calculate fees
            fees = self._calculate_fees(request.amount, request.currency)
            
            # Create payment intent
            payment_data = {
                'amount': int(request.amount * 100),  # Stripe uses cents
                'currency': request.currency.value.lower(),
                'description': request.description,
                'metadata': {
                    'transaction_id': transaction_id,
                    'user_id': request.user_id,
                    'recipient_id': request.recipient_id,
                    **request.metadata
                }
            }
            
            async with self.session.post(
                'https://api.stripe.com/v1/payment_intents',
                headers=self.headers,
                data=payment_data
            ) as response:
                if response.status == 200:
                    stripe_response = await response.json()
                    
                    transaction = PaymentTransaction(
                        transaction_id=transaction_id,
                        request_id=request.request_id,
                        user_id=request.user_id,
                        recipient_id=request.recipient_id,
                        amount=request.amount,
                        currency=request.currency,
                        payment_provider=PaymentProvider.STRIPE,
                        provider_transaction_id=stripe_response['id'],
                        status=PaymentStatus.PENDING,
                        fees=fees,
                        metadata=stripe_response
                    )
                    
                    return transaction
                else:
                    error_data = await response.json()
                    raise PaymentProcessingError(f"Stripe payment creation failed: {error_data}")
                    
        except Exception as e:
            logger.error(f"Error creating Stripe payment: {e}")
            raise PaymentProcessingError(f"Stripe payment creation failed: {e}")
    
    async def process_payment(self, transaction: PaymentTransaction) -> PaymentTransaction:
        """Process Stripe payment"""



        try:
            # Confirm payment intent
            confirm_data = {
                'payment_method': 'pm_card_visa'  # Default test payment method
            }
            
            async with self.session.post(
                f"https://api.stripe.com/v1/payment_intents/{transaction.provider_transaction_id}/confirm",
                headers=self.headers,
                data=confirm_data
            ) as response:
                if response.status == 200:
                    stripe_response = await response.json()
                    
                    # Update transaction based on Stripe response
                    if stripe_response['status'] == 'succeeded':
                        transaction.status = PaymentStatus.COMPLETED
                        transaction.processed_at = datetime.utcnow()
                    elif stripe_response['status'] == 'requires_action':
                        transaction.status = PaymentStatus.REQUIRES_ACTION
                    else:
                        transaction.status = PaymentStatus.PROCESSING
                    
                    transaction.metadata.update(stripe_response)
                    
                    return transaction
                else:
                    error_data = await response.json()
                    transaction.status = PaymentStatus.FAILED
                    transaction.error_message = str(error_data)
                    return transaction
                    
        except Exception as e:
            logger.error(f"Error processing Stripe payment: {e}")
            transaction.status = PaymentStatus.FAILED
            transaction.error_message = str(e)
            return transaction
    
    async def get_transaction_status(self, transaction_id: str) -> PaymentStatus:
        """Get Stripe transaction status"""



        try:
            async with self.session.get(
                f"https://api.stripe.com/v1/payment_intents/{transaction_id}",
                headers=self.headers
            ) as response:
                if response.status == 200:
                    stripe_response = await response.json()
                    
                    status_mapping = {
                        'requires_payment_method': PaymentStatus.PENDING,
                        'requires_confirmation': PaymentStatus.PENDING,
                        'requires_action': PaymentStatus.REQUIRES_ACTION,
                        'processing': PaymentStatus.PROCESSING,
                        'succeeded': PaymentStatus.COMPLETED,
                        'canceled': PaymentStatus.CANCELLED
                    }
                    
                    return status_mapping.get(stripe_response['status'], PaymentStatus.FAILED)
                else:
                    return PaymentStatus.FAILED
                    
        except Exception as e:
            logger.error(f"Error getting Stripe transaction status: {e}")
            return PaymentStatus.FAILED
    
    async def cancel_payment(self, transaction_id: str) -> bool:
        """Cancel Stripe payment"""



        try:
            async with self.session.post(
                f"https://api.stripe.com/v1/payment_intents/{transaction_id}/cancel",
                headers=self.headers
            ) as response:
                return response.status == 200
                
        except Exception as e:
            logger.error(f"Error cancelling Stripe payment: {e}")
            return False
    
    async def refund_payment(self, transaction_id: str, amount: Optional[Decimal] = None) -> PaymentTransaction:
        """Refund Stripe payment"""



        try:
            refund_data = {
                'payment_intent': transaction_id
            }
            
            if amount:
                refund_data['amount'] = int(amount * 100)  # Stripe uses cents
            
            async with self.session.post(
                'https://api.stripe.com/v1/refunds',
                headers=self.headers,
                data=refund_data
            ) as response:
                if response.status == 200:
                    stripe_response = await response.json()
                    
                    # Create refund transaction
                    refund_transaction = PaymentTransaction(
                        transaction_id=str(uuid.uuid4()),
                        request_id=f"refund_{transaction_id}",
                        user_id="system",
                        recipient_id="system",
                        amount=amount or Decimal(str(stripe_response['amount'] / 100)),
                        currency=CurrencyCode(stripe_response['currency'].upper()),
                        payment_provider=PaymentProvider.STRIPE,
                        provider_transaction_id=stripe_response['id'],
                        status=PaymentStatus.COMPLETED if stripe_response['status'] == 'succeeded' else PaymentStatus.PROCESSING,
                        processed_at=datetime.utcnow(),
                        metadata=stripe_response
                    )
                    
                    return refund_transaction
                else:
                    error_data = await response.json()
                    raise PaymentProcessingError(f"Stripe refund failed: {error_data}")
                    
        except Exception as e:
            logger.error(f"Error refunding Stripe payment: {e}")
            raise PaymentProcessingError(f"Stripe refund failed: {e}")


class PayPalPaymentProcessor(BasePaymentProcessor):
    """PayPal payment processor implementation"""
    
    async def _setup_authentication(self) -> None:
        """Setup PayPal authentication"""
        self.client_id = self.config.get('client_id')
        self.client_secret = self.config.get('client_secret')
        self.base_url = self.config.get('base_url', 'https://api.paypal.com')
        
        # Get access token
        await self._get_access_token()
    
    async def _get_access_token(self) -> None:
        """Get PayPal access token"""



        try:
            auth = aiohttp.BasicAuth(self.client_id, self.client_secret)
            headers = {
                'Accept': 'application/json',
                'Accept-Language': 'en_US'
            }
            data = 'grant_type=client_credentials'
            
            async with self.session.post(
                f'{self.base_url}/v1/oauth2/token',
                headers=headers,
                data=data,
                auth=auth
            ) as response:
                if response.status == 200:
                    token_data = await response.json()
                    self.access_token = token_data['access_token']
                    self.headers = {
                        'Content-Type': 'application/json',
                        'Authorization': f"Bearer {self.access_token}"
                    }
                else:
                    raise PaymentProcessingError("PayPal authentication failed")
                    
        except Exception as e:
            logger.error(f"Error getting PayPal access token: {e}")
            raise PaymentProcessingError(f"PayPal authentication failed: {e}")
    
    async def create_payment(self, request: PaymentRequest) -> PaymentTransaction:
        """Create PayPal payment"""



        try:
            transaction_id = str(uuid.uuid4())
            
            # Calculate fees
            fees = self._calculate_fees(request.amount, request.currency)
            
            # Create PayPal payout
            payout_data = {
                "sender_batch_header": {
                    "sender_batch_id": transaction_id,
                    "email_subject": "You have a payment",
                    "email_message": request.description
                },
                "items": [
                    {
                        "recipient_type": "EMAIL",
                        "amount": {
                            "value": str(request.amount),
                            "currency": request.currency.value
                        },
                        "receiver": request.metadata.get('email', ''),
                        "note": request.description,
                        "sender_item_id": request.request_id
                    }
                ]
            }
            
            async with self.session.post(
                f'{self.base_url}/v1/payments/payouts',
                headers=self.headers,
                data=json.dumps(payout_data)
            ) as response:
                if response.status == 201:
                    paypal_response = await response.json()
                    
                    transaction = PaymentTransaction(
                        transaction_id=transaction_id,
                        request_id=request.request_id,
                        user_id=request.user_id,
                        recipient_id=request.recipient_id,
                        amount=request.amount,
                        currency=request.currency,
                        payment_provider=PaymentProvider.PAYPAL,
                        provider_transaction_id=paypal_response['batch_header']['payout_batch_id'],
                        status=PaymentStatus.PROCESSING,
                        fees=fees,
                        metadata=paypal_response
                    )
                    
                    return transaction
                else:
                    error_data = await response.json()
                    raise PaymentProcessingError(f"PayPal payment creation failed: {error_data}")
                    
        except Exception as e:
            logger.error(f"Error creating PayPal payment: {e}")
            raise PaymentProcessingError(f"PayPal payment creation failed: {e}")
    
    async def process_payment(self, transaction: PaymentTransaction) -> PaymentTransaction:
        """Process PayPal payment (already processed on creation)"""
        # PayPal payouts are processed immediately on creation
        transaction.status = PaymentStatus.PROCESSING
        return transaction
    
    async def get_transaction_status(self, transaction_id: str) -> PaymentStatus:
        """Get PayPal transaction status"""



        try:
            async with self.session.get(
                f"{self.base_url}/v1/payments/payouts/{transaction_id}",
                headers=self.headers
            ) as response:
                if response.status == 200:
                    paypal_response = await response.json()
                    
                    status_mapping = {
                        'PENDING': PaymentStatus.PENDING,
                        'PROCESSING': PaymentStatus.PROCESSING,
                        'SUCCESS': PaymentStatus.COMPLETED,
                        'FAILED': PaymentStatus.FAILED,
                        'CANCELED': PaymentStatus.CANCELLED
                    }
                    
                    return status_mapping.get(
                        paypal_response['batch_header']['batch_status'], 
                        PaymentStatus.PROCESSING
                    )
                else:
                    return PaymentStatus.FAILED
                    
        except Exception as e:
            logger.error(f"Error getting PayPal transaction status: {e}")
            return PaymentStatus.FAILED
    
    async def cancel_payment(self, transaction_id: str) -> bool:
        """Cancel PayPal payment"""
        # PayPal payouts cannot be cancelled once created
        logger.warning(f"PayPal payout {transaction_id} cannot be cancelled")
        return False
    
    async def refund_payment(self, transaction_id: str, amount: Optional[Decimal] = None) -> PaymentTransaction:
        """Refund PayPal payment"""
        # PayPal payouts cannot be refunded directly
        # This would require a separate payout to reverse the transaction
        raise PaymentProcessingError("PayPal payout refunds not supported directly")


class PaymentProcessingManager:
    """Comprehensive payment processing management system"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.processors = {}
        self.accounts = {}
        self.payment_methods = {}
        self.transactions = {}
        self.metrics_collector = MetricsCollector()
        self.encryption_manager = EncryptionManager()
        
        # Initialize payment processors
        self._initialize_processors()
    
    async def initialize(self) -> None:
        """Initialize payment processing manager"""



        try:
            # Initialize all processors
            for processor in self.processors.values():
                await processor.initialize()
            
            await self._load_payment_accounts()
            await self._setup_monitoring()
            
            logger.info("Payment processing manager initialized successfully")
            
        except Exception as e:
            logger.error(f"Error initializing payment processing manager: {e}")
            raise
    
    def _initialize_processors(self) -> None:
        """Initialize payment processors"""
        # Stripe processor
        if 'stripe' in self.config:
            self.processors[PaymentProvider.STRIPE] = StripePaymentProcessor(
                self.config['stripe']
            )
        
        # PayPal processor
        if 'paypal' in self.config:
            self.processors[PaymentProvider.PAYPAL] = PayPalPaymentProcessor(
                self.config['paypal']
            )
    
    async def create_payment_account(
        self,
        user_id: str,
        provider: PaymentProvider,
        account_details: Dict[str, Any],
        account_type: str = "personal"
    ) -> str:
        """Create payment account"""



        try:
            account_id = str(uuid.uuid4())
            
            # Encrypt sensitive account details
            encrypted_details = await self.encryption_manager.encrypt_data(account_details)
            
            # Determine supported currencies based on provider
            supported_currencies = self._get_supported_currencies(provider)
            
            account = PaymentAccount(
                account_id=account_id,
                user_id=user_id,
                provider=provider,
                account_type=account_type,
                account_details=encrypted_details,
                supported_currencies=supported_currencies
            )
            
            self.accounts[account_id] = account
            
            logger.info(f"Payment account created: {account_id} for user {user_id}")
            
            return account_id
            
        except Exception as e:
            logger.error(f"Error creating payment account: {e}")
            raise PaymentProcessingError(f"Payment account creation failed: {e}")
    
    async def create_payment_method(
        self,
        user_id: str,
        provider: PaymentProvider,
        payment_type: PaymentType,
        account_id: str,
        configuration: Optional[Dict[str, Any]] = None
    ) -> str:
        """Create payment method"""



        try:
            if account_id not in self.accounts:
                raise PaymentProcessingError(f"Payment account not found: {account_id}")
            
            account = self.accounts[account_id]
            
            if account.user_id != user_id:
                raise PaymentProcessingError("Account does not belong to user")
            
            method_id = str(uuid.uuid4())
            config = configuration or {}
            
            payment_method = PaymentMethod(
                method_id=method_id,
                user_id=user_id,
                provider=provider,
                payment_type=payment_type,
                account=account,
                minimum_amount=Decimal(str(config.get('minimum_amount', 10))),
                maximum_amount=Decimal(str(config['maximum_amount'])) if config.get('maximum_amount') else None,
                fees=config.get('fees', {}),
                processing_time=timedelta(seconds=config.get('processing_time_seconds', 86400))
            )
            
            self.payment_methods[method_id] = payment_method
            
            logger.info(f"Payment method created: {method_id} for user {user_id}")
            
            return method_id
            
        except Exception as e:
            logger.error(f"Error creating payment method: {e}")
            raise PaymentProcessingError(f"Payment method creation failed: {e}")
    
    async def process_payment(
        self,
        user_id: str,
        recipient_id: str,
        amount: Decimal,
        currency: CurrencyCode,
        payment_type: PaymentType,
        description: str,
        metadata: Optional[Dict[str, Any]] = None,
        payment_method_id: Optional[str] = None
    ) -> str:
        """Process payment transaction"""



        try:
            request_id = str(uuid.uuid4())
            
            # Create payment request
            payment_request = PaymentRequest(
                request_id=request_id,
                user_id=user_id,
                recipient_id=recipient_id,
                amount=amount,
                currency=currency,
                payment_type=payment_type,
                description=description,
                metadata=metadata or {},
                payment_method_id=payment_method_id
            )
            
            # Select payment method if not specified
            if not payment_method_id:
                payment_method = await self._select_optimal_payment_method(
                    user_id, payment_type, amount, currency
                )
            else:
                if payment_method_id not in self.payment_methods:
                    raise PaymentProcessingError(f"Payment method not found: {payment_method_id}")
                payment_method = self.payment_methods[payment_method_id]
            
            # Validate payment method
            await self._validate_payment_method(payment_method, payment_request)
            
            # Get processor
            processor = self.processors.get(payment_method.provider)
            if not processor:
                raise PaymentProcessingError(f"Processor not available for {payment_method.provider.value}")
            
            # Create and process transaction
            transaction = await processor.create_payment(payment_request)
            transaction = await processor.process_payment(transaction)
            
            # Store transaction
            self.transactions[transaction.transaction_id] = transaction
            
            # Record metrics
            await self._record_payment_metrics(transaction)
            
            logger.info(f"Payment processed: {transaction.transaction_id}")
            
            return transaction.transaction_id
            
        except Exception as e:
            logger.error(f"Error processing payment: {e}")
            raise PaymentProcessingError(f"Payment processing failed: {e}")
    
    async def get_payment_status(self, transaction_id: str) -> Dict[str, Any]:
        """Get payment transaction status"""



        try:
            if transaction_id not in self.transactions:
                raise PaymentProcessingError(f"Transaction not found: {transaction_id}")
            
            transaction = self.transactions[transaction_id]
            
            # Update status from provider
            processor = self.processors.get(transaction.payment_provider)
            if processor:
                current_status = await processor.get_transaction_status(
                    transaction.provider_transaction_id
                )
                
                if current_status != transaction.status:
                    transaction.status = current_status
                    if current_status == PaymentStatus.COMPLETED:
                        transaction.processed_at = datetime.utcnow()
            
            return {
                'transaction_id': transaction.transaction_id,
                'status': transaction.status.value,
                'amount': str(transaction.amount),
                'currency': transaction.currency.value,
                'net_amount': str(transaction.net_amount),
                'fees': {k: str(v) for k, v in transaction.fees.items()},
                'provider': transaction.payment_provider.value,
                'created_at': transaction.created_at.isoformat(),
                'processed_at': transaction.processed_at.isoformat() if transaction.processed_at else None,
                'processing_time': str(transaction.processing_time) if transaction.processing_time else None,
                'error_message': transaction.error_message
            }
            
        except Exception as e:
            logger.error(f"Error getting payment status: {e}")
            raise PaymentProcessingError(f"Payment status retrieval failed: {e}")
    
    async def cancel_payment(self, transaction_id: str) -> bool:
        """Cancel payment transaction"""



        try:
            if transaction_id not in self.transactions:
                raise PaymentProcessingError(f"Transaction not found: {transaction_id}")
            
            transaction = self.transactions[transaction_id]
            
            if transaction.status not in [PaymentStatus.PENDING, PaymentStatus.PROCESSING]:
                raise PaymentProcessingError(f"Cannot cancel transaction with status: {transaction.status.value}")
            
            # Cancel with provider
            processor = self.processors.get(transaction.payment_provider)
            if processor:
                success = await processor.cancel_payment(transaction.provider_transaction_id)
                
                if success:
                    transaction.status = PaymentStatus.CANCELLED
                    logger.info(f"Payment cancelled: {transaction_id}")
                
                return success
            
            return False
            
        except Exception as e:
            logger.error(f"Error cancelling payment: {e}")
            raise PaymentProcessingError(f"Payment cancellation failed: {e}")
    
    async def refund_payment(
        self,
        transaction_id: str,
        amount: Optional[Decimal] = None,
        reason: str = ""
    ) -> str:
        """Refund payment transaction"""



        try:
            if transaction_id not in self.transactions:
                raise PaymentProcessingError(f"Transaction not found: {transaction_id}")
            
            transaction = self.transactions[transaction_id]
            
            if transaction.status != PaymentStatus.COMPLETED:
                raise PaymentProcessingError(f"Cannot refund transaction with status: {transaction.status.value}")
            
            # Process refund with provider
            processor = self.processors.get(transaction.payment_provider)
            if processor:
                refund_transaction = await processor.refund_payment(
                    transaction.provider_transaction_id, amount
                )
                
                # Store refund transaction
                self.transactions[refund_transaction.transaction_id] = refund_transaction
                
                logger.info(f"Payment refunded: {transaction_id} -> {refund_transaction.transaction_id}")
                
                return refund_transaction.transaction_id
            
            raise PaymentProcessingError("Processor not available for refund")
            
        except Exception as e:
            logger.error(f"Error refunding payment: {e}")
            raise PaymentProcessingError(f"Payment refund failed: {e}")
    
    async def get_payment_analytics(
        self,
        user_id: Optional[str] = None,
        period_days: int = 30
    ) -> Dict[str, Any]:
        """Get payment analytics"""



        try:
            end_date = datetime.utcnow()
            start_date = end_date - timedelta(days=period_days)
            
            # Filter transactions
            filtered_transactions = []
            for transaction in self.transactions.values():
                if user_id and transaction.user_id != user_id:
                    continue
                if transaction.created_at >= start_date:
                    filtered_transactions.append(transaction)
            
            if not filtered_transactions:
                return {'message': 'No transactions found for the specified period'}
            
            # Calculate analytics
            total_amount = sum(t.amount for t in filtered_transactions)
            total_fees = sum(sum(t.fees.values()) for t in filtered_transactions)
            net_amount = total_amount - total_fees
            
            successful_transactions = [
                t for t in filtered_transactions 
                if t.status == PaymentStatus.COMPLETED
            ]
            
            success_rate = len(successful_transactions) / len(filtered_transactions) * 100
            
            # Provider breakdown
            provider_stats = {}
            for transaction in filtered_transactions:
                provider = transaction.payment_provider.value
                if provider not in provider_stats:
                    provider_stats[provider] = {
                        'count': 0,
                        'total_amount': Decimal('0'),
                        'total_fees': Decimal('0'),
                        'success_count': 0
                    }
                
                provider_stats[provider]['count'] += 1
                provider_stats[provider]['total_amount'] += transaction.amount
                provider_stats[provider]['total_fees'] += sum(transaction.fees.values())
                
                if transaction.status == PaymentStatus.COMPLETED:
                    provider_stats[provider]['success_count'] += 1
            
            # Calculate average processing times
            processing_times = [
                t.processing_time.total_seconds() 
                for t in successful_transactions 
                if t.processing_time
            ]
            
            avg_processing_time = np.mean(processing_times) if processing_times else 0
            
            return {
                'period': {
                    'start': start_date.isoformat(),
                    'end': end_date.isoformat(),
                    'days': period_days
                },
                'summary': {
                    'total_transactions': len(filtered_transactions),
                    'successful_transactions': len(successful_transactions),
                    'success_rate': round(success_rate, 2),
                    'total_amount': str(total_amount),
                    'total_fees': str(total_fees),
                    'net_amount': str(net_amount),
                    'average_processing_time_seconds': round(avg_processing_time, 2)
                },
                'provider_breakdown': {
                    provider: {
                        'transaction_count': stats['count'],
                        'total_amount': str(stats['total_amount']),
                        'total_fees': str(stats['total_fees']),
                        'success_rate': round(stats['success_count'] / stats['count'] * 100, 2) if stats['count'] > 0 else 0
                    }
                    for provider, stats in provider_stats.items()
                },
                'generated_at': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error generating payment analytics: {e}")
            raise PaymentProcessingError(f"Payment analytics generation failed: {e}")
    
    async def _select_optimal_payment_method(
        self,
        user_id: str,
        payment_type: PaymentType,
        amount: Decimal,
        currency: CurrencyCode
    ) -> PaymentMethod:
        """Select optimal payment method for transaction"""
        # Get user's payment methods
        user_methods = [
            method for method in self.payment_methods.values()
            if method.user_id == user_id and method.is_active
        ]
        
        if not user_methods:
            raise PaymentProcessingError("No payment methods available")
        
        # Filter by payment type and amount
        suitable_methods = []
        for method in user_methods:
            if method.payment_type == payment_type:
                if amount >= method.minimum_amount:
                    if not method.maximum_amount or amount <= method.maximum_amount:
                        if currency in method.account.supported_currencies:
                            suitable_methods.append(method)
        
        if not suitable_methods:
            # Fallback to any compatible method
            suitable_methods = [
                method for method in user_methods
                if amount >= method.minimum_amount and 
                (not method.maximum_amount or amount <= method.maximum_amount)
            ]
        
        if not suitable_methods:
            raise PaymentProcessingError("No suitable payment methods available")
        
        # Select method with lowest fees (simplified selection)
        return min(suitable_methods, key=lambda x: x.priority)
    
    async def _validate_payment_method(
        self,
        payment_method: PaymentMethod,
        payment_request: PaymentRequest
    ) -> None:
        """Validate payment method for request"""
        if not payment_method.is_active:
            raise PaymentProcessingError("Payment method is not active")
        
        if not payment_method.account.is_active:
            raise PaymentProcessingError("Payment account is not active")
        
        if payment_request.amount < payment_method.minimum_amount:
            raise PaymentProcessingError(f"Amount below minimum: {payment_method.minimum_amount}")
        
        if payment_method.maximum_amount and payment_request.amount > payment_method.maximum_amount:
            raise PaymentProcessingError(f"Amount exceeds maximum: {payment_method.maximum_amount}")
        
        if payment_request.currency not in payment_method.account.supported_currencies:
            raise PaymentProcessingError(f"Currency not supported: {payment_request.currency.value}")
    
    def _get_supported_currencies(self, provider: PaymentProvider) -> List[CurrencyCode]:
        """Get supported currencies for payment provider"""
        if provider == PaymentProvider.STRIPE:
            return [CurrencyCode.USD, CurrencyCode.EUR, CurrencyCode.GBP, CurrencyCode.CAD, CurrencyCode.AUD]
        elif provider == PaymentProvider.PAYPAL:
            return [CurrencyCode.USD, CurrencyCode.EUR, CurrencyCode.GBP, CurrencyCode.JPY, CurrencyCode.CAD]
        else:
            return [CurrencyCode.USD, CurrencyCode.EUR]
    
    async def _load_payment_accounts(self) -> None:
        """Load existing payment accounts"""
        # In production, load from database
        pass
    
    async def _setup_monitoring(self) -> None:
        """Setup payment monitoring"""
        pass
    
    async def _record_payment_metrics(self, transaction: PaymentTransaction) -> None:
        """Record payment metrics for monitoring"""
        metrics = {
            'transaction_id': transaction.transaction_id,
            'user_id': transaction.user_id,
            'amount': str(transaction.amount),
            'currency': transaction.currency.value,
            'provider': transaction.payment_provider.value,
            'status': transaction.status.value,
            'fees': str(sum(transaction.fees.values())),
            'created_at': transaction.created_at.isoformat()
        }
        
        await self.metrics_collector.record_payment_transaction(metrics)


def create_payment_processing_manager(config: Optional[Dict[str, Any]] = None) -> PaymentProcessingManager:
    """Factory function to create payment processing manager"""



    return PaymentProcessingManager(config)
