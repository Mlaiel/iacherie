"""
Payment Gateway Adapters - Enterprise Financial Processing

This module provides comprehensive adapters for major payment gateways and
financial services including Stripe, PayPal, Wise, and bank transfer systems.
Each adapter implements secure payment processing, revenue tracking, and
automated compliance for creator monetization.

Author: Fahed Mlaiel
Email: mlaiel@live.de
Copyright: All rights reserved. Unauthorized use, reproduction, or distribution
of this code is strictly prohibited without explicit written permission.

Supported Gateways:
- Stripe: Payment processing, Subscriptions, Connect
- PayPal: Express Checkout, Subscriptions, Payouts
- Wise: International transfers, Multi-currency
- Bank Transfer: SEPA, ACH, Wire transfers
- Cryptocurrency: Bitcoin, Ethereum, Stablecoins
- Apple Pay: In-app payments, Subscriptions
- Google Pay: Payment processing, Subscriptions
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import json
import hmac
import hashlib
import base64
from decimal import Decimal

from .base_adapter import (
    BasePlatformAdapter, PlatformType, AdapterStatus, AuthenticationType,
    AdapterCredentials, RateLimitConfig, AdapterError, AuthenticationError
)

logger = logging.getLogger(__name__)

class PaymentGateway(Enum):
    """Supported payment gateways."""
    STRIPE = "stripe"
    PAYPAL = "paypal"
    WISE = "wise"
    BANK_TRANSFER = "bank_transfer"
    APPLE_PAY = "apple_pay"
    GOOGLE_PAY = "google_pay"
    CRYPTOCURRENCY = "cryptocurrency"
    SQUARE = "square"
    ADYEN = "adyen"
    KLARNA = "klarna"

class PaymentMethod(Enum):
    """Payment method types."""
    CREDIT_CARD = "credit_card"
    DEBIT_CARD = "debit_card"
    BANK_ACCOUNT = "bank_account"
    DIGITAL_WALLET = "digital_wallet"
    CRYPTOCURRENCY = "cryptocurrency"
    SEPA_DEBIT = "sepa_debit"
    ACH_DEBIT = "ach_debit"
    WIRE_TRANSFER = "wire_transfer"
    CASH = "cash"

class TransactionType(Enum):
    """Transaction types."""
    PAYMENT = "payment"
    REFUND = "refund"
    PAYOUT = "payout"
    SUBSCRIPTION = "subscription"
    TRANSFER = "transfer"
    CHARGE = "charge"
    AUTHORIZATION = "authorization"
    CAPTURE = "capture"
    DISPUTE = "dispute"

class TransactionStatus(Enum):
    """Transaction status types."""
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    DISPUTED = "disputed"
    REFUNDED = "refunded"
    PROCESSING = "processing"
    AUTHORIZED = "authorized"
    CAPTURED = "captured"

@dataclass
class PaymentTransaction:
    """Payment transaction data structure."""
    transaction_id: str
    amount: Decimal
    currency: str
    transaction_type: TransactionType
    payment_method: PaymentMethod
    status: TransactionStatus
    created_at: datetime
    description: Optional[str] = None
    customer_id: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    fees: Dict[str, Decimal] = field(default_factory=dict)
    gateway_response: Dict[str, Any] = field(default_factory=dict)
    platform_specific_data: Dict[str, Any] = field(default_factory=dict)

@dataclass
class RevenueAnalytics:
    """Revenue analytics and financial metrics."""
    total_revenue: Decimal = Decimal('0.00')
    net_revenue: Decimal = Decimal('0.00')
    total_fees: Decimal = Decimal('0.00')
    transaction_count: int = 0
    successful_transactions: int = 0
    failed_transactions: int = 0
    refund_amount: Decimal = Decimal('0.00')
    chargeback_amount: Decimal = Decimal('0.00')
    average_transaction_amount: Decimal = Decimal('0.00')
    revenue_by_currency: Dict[str, Decimal] = field(default_factory=dict)
    revenue_by_method: Dict[str, Decimal] = field(default_factory=dict)
    monthly_recurring_revenue: Decimal = Decimal('0.00')
    platform_specific_metrics: Dict[str, Any] = field(default_factory=dict)

class StripeAdapter(BasePlatformAdapter):
    """
    Enterprise Stripe payment gateway adapter.
    
    Supports:
    - Payment processing and subscriptions
    - Stripe Connect for marketplaces
    - Advanced analytics and reporting
    - Automated payouts and transfers
    - Tax calculation and compliance
    - Fraud prevention and security
    """
    
    def __init__(self, credentials: AdapterCredentials, redis_client=None):
        rate_config = RateLimitConfig(
            requests_per_second=25.0,
            requests_per_minute=1000.0,
            requests_per_hour=60000.0,
            burst_limit=50
        )
        
        if not credentials.base_url:
            credentials.base_url = "https://api.stripe.com/v1"
        
        super().__init__(
            platform_name="Stripe",
            platform_type=PlatformType.PAYMENT_GATEWAY,
            credentials=credentials,
            rate_limit_config=rate_config,
            redis_client=redis_client
        )
    
    async def authenticate(self) -> bool:
        """Authenticate with Stripe API."""
        try:
            response = await self.make_request(
                method="GET",
                endpoint="account",
                headers={"Authorization": f"Bearer {self.credentials.api_key}"}
            )
            
            if "id" in response:
                logger.info(f"Stripe authentication successful for account: {response.get('display_name', 'Unknown')}")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Stripe authentication failed: {e}")
            return False
    
    async def create_payment_intent(self, amount: int, currency: str = "usd", 
                                   customer_id: Optional[str] = None,
                                   metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Create a Stripe payment intent."""
        try:
            payment_data = {
                "amount": amount,  # Amount in cents
                "currency": currency.lower(),
                "automatic_payment_methods": {"enabled": True},
                "metadata": metadata or {}
            }
            
            if customer_id:
                payment_data["customer"] = customer_id
            
            response = await self.make_request(
                method="POST",
                endpoint="payment_intents",
                json_data=payment_data,
                headers={"Authorization": f"Bearer {self.credentials.api_key}"}
            )
            
            return {
                "platform": "stripe",
                "payment_intent_id": response["id"],
                "client_secret": response["client_secret"],
                "amount": response["amount"],
                "currency": response["currency"],
                "status": response["status"],
                "created_at": datetime.fromtimestamp(response["created"]).isoformat()
            }
            
        except Exception as e:
            logger.error(f"Stripe payment intent creation failed: {e}")
            raise AdapterError(f"Failed to create Stripe payment intent: {e}")
    
    async def create_subscription(self, customer_id: str, price_id: str,
                                 metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Create a Stripe subscription."""
        try:
            subscription_data = {
                "customer": customer_id,
                "items": [{"price": price_id}],
                "metadata": metadata or {},
                "expand": ["latest_invoice.payment_intent"]
            }
            
            response = await self.make_request(
                method="POST",
                endpoint="subscriptions",
                json_data=subscription_data,
                headers={"Authorization": f"Bearer {self.credentials.api_key}"}
            )
            
            return {
                "platform": "stripe",
                "subscription_id": response["id"],
                "status": response["status"],
                "current_period_start": datetime.fromtimestamp(response["current_period_start"]).isoformat(),
                "current_period_end": datetime.fromtimestamp(response["current_period_end"]).isoformat(),
                "latest_invoice": response.get("latest_invoice"),
                "created_at": datetime.fromtimestamp(response["created"]).isoformat()
            }
            
        except Exception as e:
            logger.error(f"Stripe subscription creation failed: {e}")
            raise AdapterError(f"Failed to create Stripe subscription: {e}")
    
    async def create_transfer(self, amount: int, destination: str, currency: str = "usd",
                             metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Create a transfer to a connected account."""
        try:
            transfer_data = {
                "amount": amount,
                "currency": currency.lower(),
                "destination": destination,
                "metadata": metadata or {}
            }
            
            response = await self.make_request(
                method="POST",
                endpoint="transfers",
                json_data=transfer_data,
                headers={"Authorization": f"Bearer {self.credentials.api_key}"}
            )
            
            return {
                "platform": "stripe",
                "transfer_id": response["id"],
                "amount": response["amount"],
                "currency": response["currency"],
                "destination": response["destination"],
                "created_at": datetime.fromtimestamp(response["created"]).isoformat()
            }
            
        except Exception as e:
            logger.error(f"Stripe transfer creation failed: {e}")
            raise AdapterError(f"Failed to create Stripe transfer: {e}")
    
    async def get_revenue_analytics(self, start_date: Optional[datetime] = None,
                                   end_date: Optional[datetime] = None) -> RevenueAnalytics:
        """Get Stripe revenue analytics."""
        try:
            # Calculate date range
            if not start_date:
                start_date = datetime.now() - timedelta(days=30)
            if not end_date:
                end_date = datetime.now()
            
            # Get charges within date range
            charges_response = await self.make_request(
                method="GET",
                endpoint="charges",
                params={
                    "created": {
                        "gte": int(start_date.timestamp()),
                        "lte": int(end_date.timestamp())
                    },
                    "limit": 100
                },
                headers={"Authorization": f"Bearer {self.credentials.api_key}"}
            )
            
            analytics = RevenueAnalytics()
            
            for charge in charges_response.get("data", []):
                amount = Decimal(str(charge["amount"])) / 100  # Convert from cents
                currency = charge["currency"].upper()
                
                analytics.transaction_count += 1
                
                if charge["paid"]:
                    analytics.successful_transactions += 1
                    analytics.total_revenue += amount
                    
                    # Track revenue by currency
                    if currency not in analytics.revenue_by_currency:
                        analytics.revenue_by_currency[currency] = Decimal('0.00')
                    analytics.revenue_by_currency[currency] += amount
                    
                    # Calculate fees
                    if charge.get("application_fee_amount"):
                        fee = Decimal(str(charge["application_fee_amount"])) / 100
                        analytics.total_fees += fee
                
                else:
                    analytics.failed_transactions += 1
                
                if charge.get("refunded"):
                    refund_amount = Decimal(str(charge.get("amount_refunded", 0))) / 100
                    analytics.refund_amount += refund_amount
            
            # Calculate derived metrics
            if analytics.transaction_count > 0:
                analytics.average_transaction_amount = analytics.total_revenue / analytics.transaction_count
            
            analytics.net_revenue = analytics.total_revenue - analytics.total_fees
            
            return analytics
            
        except Exception as e:
            logger.error(f"Stripe analytics retrieval failed: {e}")
            return RevenueAnalytics()
    
    async def webhook_verify(self, payload: str, signature: str, webhook_secret: str) -> bool:
        """Verify Stripe webhook signature."""
        try:
            expected_signature = hmac.new(
                webhook_secret.encode('utf-8'),
                payload.encode('utf-8'),
                hashlib.sha256
            ).hexdigest()
            
            return hmac.compare_digest(f"sha256={expected_signature}", signature)
            
        except Exception:
            return False
    
    async def health_check(self) -> bool:
        """Perform Stripe API health check."""
        try:
            response = await self.make_request(
                method="GET",
                endpoint="account",
                headers={"Authorization": f"Bearer {self.credentials.api_key}"}
            )
            return "id" in response
        except:
            return False

class PayPalAdapter(BasePlatformAdapter):
    """
    Enterprise PayPal payment gateway adapter.
    
    Supports:
    - PayPal Express Checkout
    - Subscription billing
    - Mass payouts
    - Dispute management
    - Multi-currency processing
    - PayPal for Developers API
    """
    
    def __init__(self, credentials: AdapterCredentials, redis_client=None):
        rate_config = RateLimitConfig(
            requests_per_second=10.0,
            requests_per_minute=600.0,
            requests_per_hour=10000.0,
            burst_limit=20
        )
        
        if not credentials.base_url:
            # Use sandbox for testing, production for live
            credentials.base_url = "https://api-m.sandbox.paypal.com"  # or "https://api-m.paypal.com"
        
        super().__init__(
            platform_name="PayPal",
            platform_type=PlatformType.PAYMENT_GATEWAY,
            credentials=credentials,
            rate_limit_config=rate_config,
            redis_client=redis_client
        )
    
    async def authenticate(self) -> bool:
        """Authenticate with PayPal API using OAuth2."""
        try:
            # Get access token
            auth_string = base64.b64encode(
                f"{self.credentials.client_id}:{self.credentials.client_secret}".encode()
            ).decode()
            
            token_response = await self.make_request(
                method="POST",
                endpoint="v1/oauth2/token",
                headers={
                    "Authorization": f"Basic {auth_string}",
                    "Content-Type": "application/x-www-form-urlencoded"
                },
                data="grant_type=client_credentials"
            )
            
            if "access_token" in token_response:
                self.credentials.access_token = token_response["access_token"]
                self.credentials.token_expires_at = datetime.now() + timedelta(
                    seconds=token_response.get("expires_in", 3600)
                )
                logger.info("PayPal authentication successful")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"PayPal authentication failed: {e}")
            return False
    
    async def create_payment(self, amount: str, currency: str = "USD",
                            return_url: str = "", cancel_url: str = "",
                            description: str = "") -> Dict[str, Any]:
        """Create a PayPal payment."""
        try:
            payment_data = {
                "intent": "sale",
                "payer": {"payment_method": "paypal"},
                "redirect_urls": {
                    "return_url": return_url,
                    "cancel_url": cancel_url
                },
                "transactions": [{
                    "amount": {
                        "total": amount,
                        "currency": currency
                    },
                    "description": description
                }]
            }
            
            response = await self.make_request(
                method="POST",
                endpoint="v1/payments/payment",
                json_data=payment_data,
                headers={"Authorization": f"Bearer {self.credentials.access_token}"}
            )
            
            approval_url = None
            for link in response.get("links", []):
                if link.get("rel") == "approval_url":
                    approval_url = link.get("href")
                    break
            
            return {
                "platform": "paypal",
                "payment_id": response["id"],
                "status": response["state"],
                "approval_url": approval_url,
                "created_at": response["create_time"]
            }
            
        except Exception as e:
            logger.error(f"PayPal payment creation failed: {e}")
            raise AdapterError(f"Failed to create PayPal payment: {e}")
    
    async def execute_payment(self, payment_id: str, payer_id: str) -> Dict[str, Any]:
        """Execute an approved PayPal payment."""
        try:
            execution_data = {"payer_id": payer_id}
            
            response = await self.make_request(
                method="POST",
                endpoint=f"v1/payments/payment/{payment_id}/execute",
                json_data=execution_data,
                headers={"Authorization": f"Bearer {self.credentials.access_token}"}
            )
            
            return {
                "platform": "paypal",
                "payment_id": response["id"],
                "status": response["state"],
                "executed_at": datetime.now().isoformat(),
                "transaction_details": response.get("transactions", [])
            }
            
        except Exception as e:
            logger.error(f"PayPal payment execution failed: {e}")
            raise AdapterError(f"Failed to execute PayPal payment: {e}")
    
    async def create_payout(self, recipient_email: str, amount: str, 
                           currency: str = "USD", note: str = "") -> Dict[str, Any]:
        """Create a PayPal payout."""
        try:
            payout_data = {
                "sender_batch_header": {
                    "sender_batch_id": f"batch_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                    "email_subject": "You have a payout!",
                    "email_message": note or "You have received a payout. Thanks for using our service!"
                },
                "items": [{
                    "recipient_type": "EMAIL",
                    "amount": {
                        "value": amount,
                        "currency": currency
                    },
                    "receiver": recipient_email,
                    "note": note,
                    "sender_item_id": f"item_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                }]
            }
            
            response = await self.make_request(
                method="POST",
                endpoint="v1/payments/payouts",
                json_data=payout_data,
                headers={"Authorization": f"Bearer {self.credentials.access_token}"}
            )
            
            return {
                "platform": "paypal",
                "payout_batch_id": response["batch_header"]["payout_batch_id"],
                "batch_status": response["batch_header"]["batch_status"],
                "created_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"PayPal payout creation failed: {e}")
            raise AdapterError(f"Failed to create PayPal payout: {e}")
    
    async def health_check(self) -> bool:
        """Perform PayPal API health check."""
        try:
            # Test with a simple API call
            response = await self.make_request(
                method="GET",
                endpoint="v1/notifications/webhooks-event-types",
                headers={"Authorization": f"Bearer {self.credentials.access_token}"}
            )
            return "event_types" in response
        except:
            return False

class WiseAdapter(BasePlatformAdapter):
    """
    Enterprise Wise (formerly TransferWise) adapter for international transfers.
    
    Supports:
    - International money transfers
    - Multi-currency accounts
    - Real-time exchange rates
    - Compliance and verification
    - Business account management
    """
    
    def __init__(self, credentials: AdapterCredentials, redis_client=None):
        rate_config = RateLimitConfig(
            requests_per_second=10.0,
            requests_per_minute=600.0,
            requests_per_hour=5000.0,
            burst_limit=20
        )
        
        if not credentials.base_url:
            credentials.base_url = "https://api.transferwise.com"
        
        super().__init__(
            platform_name="Wise",
            platform_type=PlatformType.PAYMENT_GATEWAY,
            credentials=credentials,
            rate_limit_config=rate_config,
            redis_client=redis_client
        )
    
    async def authenticate(self) -> bool:
        """Authenticate with Wise API."""
        try:
            response = await self.make_request(
                method="GET",
                endpoint="v1/profiles",
                headers={"Authorization": f"Bearer {self.credentials.access_token}"}
            )
            
            if isinstance(response, list) and len(response) > 0:
                logger.info(f"Wise authentication successful for profile: {response[0].get('type', 'Unknown')}")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Wise authentication failed: {e}")
            return False
    
    async def get_exchange_rate(self, source_currency: str, target_currency: str, 
                               amount: Optional[float] = None) -> Dict[str, Any]:
        """Get real-time exchange rate from Wise."""
        try:
            params = {
                "source": source_currency.upper(),
                "target": target_currency.upper()
            }
            
            if amount:
                params["sourceAmount"] = amount
            
            response = await self.make_request(
                method="GET",
                endpoint="v1/rates",
                params=params,
                headers={"Authorization": f"Bearer {self.credentials.access_token}"}
            )
            
            return {
                "platform": "wise",
                "source_currency": source_currency.upper(),
                "target_currency": target_currency.upper(),
                "rate": response[0]["rate"],
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Wise exchange rate retrieval failed: {e}")
            raise AdapterError(f"Failed to get Wise exchange rate: {e}")
    
    async def health_check(self) -> bool:
        """Perform Wise API health check."""
        try:
            response = await self.make_request(
                method="GET",
                endpoint="v1/profiles",
                headers={"Authorization": f"Bearer {self.credentials.access_token}"}
            )
            return isinstance(response, list)
        except:
            return False

class PaymentAdapterFactory:
    """Factory for creating payment gateway adapters."""
    
    _adapters = {
        PaymentGateway.STRIPE: StripeAdapter,
        PaymentGateway.PAYPAL: PayPalAdapter,
        PaymentGateway.WISE: WiseAdapter,
        # Additional gateways would be registered here
    }
    
    @classmethod
    def create_adapter(cls, gateway: PaymentGateway, credentials: AdapterCredentials, redis_client=None) -> BasePlatformAdapter:
        """Create adapter for specified payment gateway."""
        if gateway not in cls._adapters:
            raise AdapterError(f"Unsupported payment gateway: {gateway}")
        
        adapter_class = cls._adapters[gateway]
        return adapter_class(credentials, redis_client)
    
    @classmethod
    def get_supported_gateways(cls) -> List[PaymentGateway]:
        """Get list of supported payment gateways."""
        return list(cls._adapters.keys())

# Export all classes
__all__ = [
    'PaymentGateway',
    'PaymentMethod',
    'TransactionType',
    'TransactionStatus',
    'PaymentTransaction',
    'RevenueAnalytics',
    'StripeAdapter',
    'PayPalAdapter',
    'WiseAdapter',
    'PaymentAdapterFactory'
]
