"""Square Integration - Square Payment Processing and Point of Sale
==================================================================

Comprehensive Square API integration for payment processing, invoicing,
and point-of-sale transactions for the Ainflue platform.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import logging
import json
import time
import uuid
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, field, asdict
from datetime import datetime, timedelta
from enum import Enum
from decimal import Decimal
import hashlib
import hmac

import aiohttp
import aiofiles

logger = logging.getLogger(__name__)


class SquareEnvironment(Enum):
    """Square API environments."""
    SANDBOX = "sandbox"
    PRODUCTION = "production"


class SquarePaymentStatus(Enum):
    """Square payment status."""
    APPROVED = "APPROVED"
    PENDING = "PENDING"
    COMPLETED = "COMPLETED"
    CANCELED = "CANCELED"
    FAILED = "FAILED"


class SquareCardBrand(Enum):
    """Square card brands."""
    VISA = "VISA"
    MASTERCARD = "MASTERCARD"
    AMERICAN_EXPRESS = "AMERICAN_EXPRESS"
    DISCOVER = "DISCOVER"
    DISCOVER_DINERS = "DISCOVER_DINERS"
    JCB = "JCB"
    CHINA_UNIONPAY = "CHINA_UNIONPAY"
    SQUARE_GIFT_CARD = "SQUARE_GIFT_CARD"
    OTHER_BRAND = "OTHER_BRAND"


class SquareOrderState(Enum):
    """Square order states."""
    OPEN = "OPEN"
    COMPLETED = "COMPLETED"
    CANCELED = "CANCELED"


@dataclass
class SquareMoney:
    """Square money representation."""
    amount: int  # Amount in the smallest currency unit (cents)
    currency: str = "USD"
    
    @property
    def decimal_amount(self) -> Decimal:
        """Get decimal representation of amount."""
        return Decimal(self.amount) / 100
    
    @classmethod
    def from_decimal(cls, amount: Decimal, currency: str = "USD") -> 'SquareMoney':
        """Create from decimal amount."""
        return cls(amount=int(amount * 100), currency=currency)


@dataclass
class SquareCustomer:
    """Square customer."""
    id: str
    created_at: datetime
    updated_at: datetime
    given_name: Optional[str] = None
    family_name: Optional[str] = None
    company_name: Optional[str] = None
    nickname: Optional[str] = None
    email_address: Optional[str] = None
    phone_number: Optional[str] = None
    reference_id: Optional[str] = None
    note: Optional[str] = None
    preferences: Optional[Dict[str, Any]] = None


@dataclass
class SquareCard:
    """Square card details."""
    id: str
    card_brand: SquareCardBrand
    last_4: str
    exp_month: int
    exp_year: int
    cardholder_name: Optional[str] = None
    billing_address: Optional[Dict[str, Any]] = None
    fingerprint: Optional[str] = None
    customer_id: Optional[str] = None
    merchant_id: Optional[str] = None
    reference_id: Optional[str] = None
    enabled: bool = True


@dataclass
class SquarePayment:
    """Square payment."""
    id: str
    created_at: datetime
    updated_at: datetime
    amount_money: SquareMoney
    status: SquarePaymentStatus
    delay_duration: Optional[str] = None
    source_type: Optional[str] = None
    card_details: Optional[Dict[str, Any]] = None
    cash_details: Optional[Dict[str, Any]] = None
    bank_account_details: Optional[Dict[str, Any]] = None
    external_details: Optional[Dict[str, Any]] = None
    wallet_details: Optional[Dict[str, Any]] = None
    location_id: Optional[str] = None
    order_id: Optional[str] = None
    processing_fee: Optional[List[Dict[str, Any]]] = None
    customer_id: Optional[str] = None
    employee_id: Optional[str] = None
    refund_ids: Optional[List[str]] = None
    risk_evaluation: Optional[Dict[str, Any]] = None
    buyer_email_address: Optional[str] = None
    billing_address: Optional[Dict[str, Any]] = None
    shipping_address: Optional[Dict[str, Any]] = None
    note: Optional[str] = None
    statement_description_identifier: Optional[str] = None
    capabilities: Optional[List[str]] = None
    receipt_number: Optional[str] = None
    receipt_url: Optional[str] = None
    device_details: Optional[Dict[str, Any]] = None
    application_details: Optional[Dict[str, Any]] = None
    version_token: Optional[str] = None


@dataclass
class SquareRefund:
    """Square refund."""
    id: str
    location_id: str
    transaction_id: str
    tender_id: str
    created_at: datetime
    reason: str
    amount_money: SquareMoney
    status: str
    processing_fee_money: Optional[SquareMoney] = None
    additional_recipients: Optional[List[Dict[str, Any]]] = None


@dataclass
class SquareOrder:
    """Square order."""
    id: str
    location_id: str
    created_at: datetime
    updated_at: datetime
    state: SquareOrderState
    version: int
    total_money: Optional[SquareMoney] = None
    total_tax_money: Optional[SquareMoney] = None
    total_discount_money: Optional[SquareMoney] = None
    total_tip_money: Optional[SquareMoney] = None
    total_service_charge_money: Optional[SquareMoney] = None
    pricing_options: Optional[Dict[str, Any]] = None
    rewards: Optional[List[Dict[str, Any]]] = None
    net_amounts: Optional[Dict[str, Any]] = None
    source: Optional[Dict[str, Any]] = None
    customer_id: Optional[str] = None
    fulfillments: Optional[List[Dict[str, Any]]] = None
    metadata: Optional[Dict[str, str]] = None
    line_items: Optional[List[Dict[str, Any]]] = None
    taxes: Optional[List[Dict[str, Any]]] = None
    discounts: Optional[List[Dict[str, Any]]] = None
    service_charges: Optional[List[Dict[str, Any]]] = None
    reference_id: Optional[str] = None
    ticket_name: Optional[str] = None


class SquareAPIClient:
    """Square API client."""
    
    def __init__(self, access_token -> None: str, environment -> None: SquareEnvironment = SquareEnvironment.SANDBOX,
                 webhook_signature_key -> None: Optional[str] = None) -> None:
        self.access_token = access_token
        self.environment = environment
        self.webhook_signature_key = webhook_signature_key
        
        if environment == SquareEnvironment.SANDBOX:
            self.base_url = "https://connect.squareupsandbox.com"
        else:
            self.base_url = "https://connect.squareup.com"
        
        self.session = None
        
        # Rate limiting
        self.rate_limit_remaining = 1000
        self.rate_limit_reset = time.time()
    
    async def __aenter__(self) -> None:
        """Async context manager entry."""
        self.session = aiohttp.ClientSession(
            headers={
                "Authorization": f"Bearer {self.access_token}",
                "Content-Type": "application/json",
                "Square-Version": "2023-10-18",
                "User-Agent": "Ainflue-Integration/1.0"
            },
            timeout=aiohttp.ClientTimeout(total=30)
        )
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        """Async context manager exit."""
        if self.session:
            await self.session.close()
    
    async def _make_request(self, method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
        """Make HTTP request to Square API."""
        await self._check_rate_limit()
        
        url = f"{self.base_url}{endpoint}"
        
        try:
            async with self.session.request(method, url, **kwargs) as response:
                self._update_rate_limit(response.headers)
                
                response_data = await response.json()
                
                if response.status >= 400:
                    errors = response_data.get('errors', [])
                    error_msg = '; '.join([err.get('detail', str(err)) for err in errors])
                    logger.error(f"Square API error: {error_msg}")
                    raise Exception(f"Square API error: {error_msg}")
                
                return response_data
                
        except aiohttp.ClientError as e:
            logger.error(f"HTTP client error: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Request failed: {str(e)}")
            raise
    
    async def _check_rate_limit(self) -> None:
        """Check and enforce rate limiting."""
        current_time = time.time()
        
        if current_time > self.rate_limit_reset:
            self.rate_limit_remaining = 1000  # Reset limit
        
        if self.rate_limit_remaining <= 0:
            sleep_time = self.rate_limit_reset - current_time
            if sleep_time > 0:
                logger.warning(f"Rate limit reached, sleeping for {sleep_time:.2f}s")
                await asyncio.sleep(sleep_time)
    
    def _update_rate_limit(self, headers -> None: Dict[str, str]) -> None:
        """Update rate limit tracking from response headers."""
        if 'x-ratelimit-remaining' in headers:
            self.rate_limit_remaining = int(headers['x-ratelimit-remaining'])
        
        if 'x-ratelimit-reset' in headers:
            self.rate_limit_reset = int(headers['x-ratelimit-reset'])
    
    async def create_customer(self, given_name: str, family_name: str,
                            email_address: str, phone_number: Optional[str] = None,
                            company_name: Optional[str] = None,
                            reference_id: Optional[str] = None) -> SquareCustomer:
        """Create a new customer."""
        try:
            payload = {
                "given_name": given_name,
                "family_name": family_name,
                "email_address": email_address
            }
            
            if phone_number:
                payload["phone_number"] = phone_number
            if company_name:
                payload["company_name"] = company_name
            if reference_id:
                payload["reference_id"] = reference_id
            
            response = await self._make_request("POST", "/v2/customers", json=payload)
            
            customer_data = response["customer"]
            
            customer = SquareCustomer(
                id=customer_data["id"],
                created_at=datetime.fromisoformat(customer_data["created_at"].replace('Z', '+00:00')),
                updated_at=datetime.fromisoformat(customer_data["updated_at"].replace('Z', '+00:00')),
                given_name=customer_data.get("given_name"),
                family_name=customer_data.get("family_name"),
                company_name=customer_data.get("company_name"),
                nickname=customer_data.get("nickname"),
                email_address=customer_data.get("email_address"),
                phone_number=customer_data.get("phone_number"),
                reference_id=customer_data.get("reference_id"),
                note=customer_data.get("note"),
                preferences=customer_data.get("preferences")
            )
            
            return customer
            
        except Exception as e:
            logger.error(f"Failed to create customer: {str(e)}")
            raise
    
    async def get_customer(self, customer_id: str) -> SquareCustomer:
        """Get customer by ID."""
        try:
            response = await self._make_request("GET", f"/v2/customers/{customer_id}")
            
            customer_data = response["customer"]
            
            customer = SquareCustomer(
                id=customer_data["id"],
                created_at=datetime.fromisoformat(customer_data["created_at"].replace('Z', '+00:00')),
                updated_at=datetime.fromisoformat(customer_data["updated_at"].replace('Z', '+00:00')),
                given_name=customer_data.get("given_name"),
                family_name=customer_data.get("family_name"),
                company_name=customer_data.get("company_name"),
                nickname=customer_data.get("nickname"),
                email_address=customer_data.get("email_address"),
                phone_number=customer_data.get("phone_number"),
                reference_id=customer_data.get("reference_id"),
                note=customer_data.get("note"),
                preferences=customer_data.get("preferences")
            )
            
            return customer
            
        except Exception as e:
            logger.error(f"Failed to get customer: {str(e)}")
            raise
    
    async def create_payment(self, source_id: str, amount_money: SquareMoney,
                           location_id: str, idempotency_key: Optional[str] = None,
                           customer_id: Optional[str] = None,
                           reference_id: Optional[str] = None,
                           note: Optional[str] = None,
                           order_id: Optional[str] = None) -> SquarePayment:
        """Create a payment."""
        try:
            if not idempotency_key:
                idempotency_key = str(uuid.uuid4())
            
            payload = {
                "source_id": source_id,
                "idempotency_key": idempotency_key,
                "amount_money": {
                    "amount": amount_money.amount,
                    "currency": amount_money.currency
                },
                "location_id": location_id
            }
            
            if customer_id:
                payload["customer_id"] = customer_id
            if reference_id:
                payload["reference_id"] = reference_id
            if note:
                payload["note"] = note
            if order_id:
                payload["order_id"] = order_id
            
            response = await self._make_request("POST", "/v2/payments", json=payload)
            
            payment_data = response["payment"]
            
            payment = SquarePayment(
                id=payment_data["id"],
                created_at=datetime.fromisoformat(payment_data["created_at"].replace('Z', '+00:00')),
                updated_at=datetime.fromisoformat(payment_data["updated_at"].replace('Z', '+00:00')),
                amount_money=SquareMoney(
                    amount=payment_data["amount_money"]["amount"],
                    currency=payment_data["amount_money"]["currency"]
                ),
                status=SquarePaymentStatus(payment_data["status"]),
                delay_duration=payment_data.get("delay_duration"),
                source_type=payment_data.get("source_type"),
                card_details=payment_data.get("card_details"),
                cash_details=payment_data.get("cash_details"),
                bank_account_details=payment_data.get("bank_account_details"),
                external_details=payment_data.get("external_details"),
                wallet_details=payment_data.get("wallet_details"),
                location_id=payment_data.get("location_id"),
                order_id=payment_data.get("order_id"),
                processing_fee=payment_data.get("processing_fee"),
                customer_id=payment_data.get("customer_id"),
                employee_id=payment_data.get("employee_id"),
                refund_ids=payment_data.get("refund_ids"),
                risk_evaluation=payment_data.get("risk_evaluation"),
                buyer_email_address=payment_data.get("buyer_email_address"),
                billing_address=payment_data.get("billing_address"),
                shipping_address=payment_data.get("shipping_address"),
                note=payment_data.get("note"),
                statement_description_identifier=payment_data.get("statement_description_identifier"),
                capabilities=payment_data.get("capabilities"),
                receipt_number=payment_data.get("receipt_number"),
                receipt_url=payment_data.get("receipt_url"),
                device_details=payment_data.get("device_details"),
                application_details=payment_data.get("application_details"),
                version_token=payment_data.get("version_token")
            )
            
            return payment
            
        except Exception as e:
            logger.error(f"Failed to create payment: {str(e)}")
            raise
    
    async def get_payment(self, payment_id: str) -> SquarePayment:
        """Get payment by ID."""
        try:
            response = await self._make_request("GET", f"/v2/payments/{payment_id}")
            
            payment_data = response["payment"]
            
            payment = SquarePayment(
                id=payment_data["id"],
                created_at=datetime.fromisoformat(payment_data["created_at"].replace('Z', '+00:00')),
                updated_at=datetime.fromisoformat(payment_data["updated_at"].replace('Z', '+00:00')),
                amount_money=SquareMoney(
                    amount=payment_data["amount_money"]["amount"],
                    currency=payment_data["amount_money"]["currency"]
                ),
                status=SquarePaymentStatus(payment_data["status"]),
                delay_duration=payment_data.get("delay_duration"),
                source_type=payment_data.get("source_type"),
                card_details=payment_data.get("card_details"),
                location_id=payment_data.get("location_id"),
                order_id=payment_data.get("order_id"),
                customer_id=payment_data.get("customer_id"),
                receipt_number=payment_data.get("receipt_number"),
                receipt_url=payment_data.get("receipt_url")
            )
            
            return payment
            
        except Exception as e:
            logger.error(f"Failed to get payment: {str(e)}")
            raise
    
    async def refund_payment(self, payment_id: str, amount_money: SquareMoney,
                           idempotency_key: Optional[str] = None,
                           reason: str = "Refund") -> SquareRefund:
        """Refund a payment."""
        try:
            if not idempotency_key:
                idempotency_key = str(uuid.uuid4())
            
            payload = {
                "idempotency_key": idempotency_key,
                "amount_money": {
                    "amount": amount_money.amount,
                    "currency": amount_money.currency
                },
                "payment_id": payment_id,
                "reason": reason
            }
            
            response = await self._make_request("POST", "/v2/refunds", json=payload)
            
            refund_data = response["refund"]
            
            refund = SquareRefund(
                id=refund_data["id"],
                location_id=refund_data["location_id"],
                transaction_id=refund_data.get("transaction_id", ""),
                tender_id=refund_data.get("tender_id", ""),
                created_at=datetime.fromisoformat(refund_data["created_at"].replace('Z', '+00:00')),
                reason=refund_data["reason"],
                amount_money=SquareMoney(
                    amount=refund_data["amount_money"]["amount"],
                    currency=refund_data["amount_money"]["currency"]
                ),
                status=refund_data["status"],
                processing_fee_money=SquareMoney(
                    amount=refund_data["processing_fee_money"]["amount"],
                    currency=refund_data["processing_fee_money"]["currency"]
                ) if refund_data.get("processing_fee_money") else None
            )
            
            return refund
            
        except Exception as e:
            logger.error(f"Failed to refund payment: {str(e)}")
            raise
    
    async def create_card(self, source_id: str, verification_token: Optional[str] = None,
                        customer_id: Optional[str] = None,
                        reference_id: Optional[str] = None) -> SquareCard:
        """Create a saved card."""
        try:
            payload = {
                "source_id": source_id,
                "card": {}
            }
            
            if verification_token:
                payload["card"]["verification_token"] = verification_token
            if customer_id:
                payload["card"]["customer_id"] = customer_id
            if reference_id:
                payload["card"]["reference_id"] = reference_id
            
            response = await self._make_request("POST", "/v2/cards", json=payload)
            
            card_data = response["card"]
            
            card = SquareCard(
                id=card_data["id"],
                card_brand=SquareCardBrand(card_data["card_brand"]),
                last_4=card_data["last_4"],
                exp_month=card_data["exp_month"],
                exp_year=card_data["exp_year"],
                cardholder_name=card_data.get("cardholder_name"),
                billing_address=card_data.get("billing_address"),
                fingerprint=card_data.get("fingerprint"),
                customer_id=card_data.get("customer_id"),
                merchant_id=card_data.get("merchant_id"),
                reference_id=card_data.get("reference_id"),
                enabled=card_data.get("enabled", True)
            )
            
            return card
            
        except Exception as e:
            logger.error(f"Failed to create card: {str(e)}")
            raise
    
    async def create_order(self, location_id: str, line_items: List[Dict[str, Any]],
                         customer_id: Optional[str] = None,
                         reference_id: Optional[str] = None,
                         metadata: Optional[Dict[str, str]] = None) -> SquareOrder:
        """Create an order."""
        try:
            payload = {
                "order": {
                    "location_id": location_id,
                    "line_items": line_items
                }
            }
            
            if customer_id:
                payload["order"]["customer_id"] = customer_id
            if reference_id:
                payload["order"]["reference_id"] = reference_id
            if metadata:
                payload["order"]["metadata"] = metadata
            
            response = await self._make_request("POST", "/v2/orders", json=payload)
            
            order_data = response["order"]
            
            order = SquareOrder(
                id=order_data["id"],
                location_id=order_data["location_id"],
                created_at=datetime.fromisoformat(order_data["created_at"].replace('Z', '+00:00')),
                updated_at=datetime.fromisoformat(order_data["updated_at"].replace('Z', '+00:00')),
                state=SquareOrderState(order_data["state"]),
                version=order_data["version"],
                total_money=SquareMoney(
                    amount=order_data["total_money"]["amount"],
                    currency=order_data["total_money"]["currency"]
                ) if order_data.get("total_money") else None,
                customer_id=order_data.get("customer_id"),
                line_items=order_data.get("line_items"),
                reference_id=order_data.get("reference_id"),
                metadata=order_data.get("metadata")
            )
            
            return order
            
        except Exception as e:
            logger.error(f"Failed to create order: {str(e)}")
            raise
    
    def verify_webhook_signature(self, body: str, signature: str, notification_url: str) -> bool:
        """Verify webhook signature."""
        if not self.webhook_signature_key:
            logger.warning("No webhook signature key configured")
            return False
        
        try:
            # Square webhook verification
            string_to_sign = notification_url + body
            
            expected_signature = hmac.new(
                self.webhook_signature_key.encode(),
                string_to_sign.encode(),
                hashlib.sha256
            ).hexdigest()
            
            return hmac.compare_digest(signature, expected_signature)
            
        except Exception as e:
            logger.error(f"Failed to verify webhook signature: {str(e)}")
            return False


class SquareIntegration:
    """Main Square integration for Ainflue platform."""
    
    def __init__(self, access_token -> None: str, environment -> None: SquareEnvironment = SquareEnvironment.SANDBOX,
                 webhook_signature_key -> None: Optional[str] = None, default_location_id -> None: Optional[str] = None) -> None:
        self.access_token = access_token
        self.environment = environment
        self.webhook_signature_key = webhook_signature_key
        self.default_location_id = default_location_id
        
        # Creator subscription tracking
        self.subscriptions: Dict[str, Dict] = {}
        
        # Supported currencies for Square
        self.supported_currencies = ["USD", "CAD", "JPY", "GBP", "AUD"]
    
    async def initialize(self) -> bool:
        """Initialize Square integration."""
        try:
            async with SquareAPIClient(self.access_token, self.environment, self.webhook_signature_key) as client:
                # Test API connection
                response = await client._make_request("GET", "/v2/locations")
                locations = response.get("locations", [])
                
                if not locations:
                    raise Exception("No Square locations found")
                
                if not self.default_location_id:
                    self.default_location_id = locations[0]["id"]
                
                logger.info(f"Square integration initialized with {len(locations)} locations")
                return True
                
        except Exception as e:
            logger.error(f"Failed to initialize Square integration: {str(e)}")
            return False
    
    async def create_creator_subscription(self, creator_id: str, customer_email: str,
                                       customer_name: str, subscription_amount: Decimal,
                                       currency: str = "USD") -> Dict[str, Any]:
        """Create a subscription for a creator's content."""
        try:
            if currency not in self.supported_currencies:
                raise ValueError(f"Currency {currency} not supported by Square")
            
            async with SquareAPIClient(self.access_token, self.environment, self.webhook_signature_key) as client:
                # Create customer
                name_parts = customer_name.split(" ", 1)
                given_name = name_parts[0]
                family_name = name_parts[1] if len(name_parts) > 1 else ""
                
                customer = await client.create_customer(
                    given_name=given_name,
                    family_name=family_name,
                    email_address=customer_email,
                    reference_id=f"creator_{creator_id}_sub"
                )
                
                # Create subscription order
                subscription_data = {
                    "subscription_id": f"sub_{creator_id}_{customer.id}",
                    "creator_id": creator_id,
                    "customer_id": customer.id,
                    "customer_email": customer_email,
                    "amount": subscription_amount,
                    "currency": currency,
                    "status": "active",
                    "created_at": datetime.utcnow().isoformat(),
                    "next_billing_date": (datetime.utcnow() + timedelta(days=30)).isoformat()
                }
                
                self.subscriptions[subscription_data["subscription_id"]] = subscription_data
                
                logger.info(f"Created Square subscription for creator {creator_id}: {subscription_amount} {currency}")
                return subscription_data
                
        except Exception as e:
            logger.error(f"Failed to create creator subscription: {str(e)}")
            raise
    
    async def process_subscription_payment(self, subscription_id: str, payment_source_id: str) -> Dict[str, Any]:
        """Process a subscription payment."""
        try:
            if subscription_id not in self.subscriptions:
                raise ValueError(f"Subscription {subscription_id} not found")
            
            subscription = self.subscriptions[subscription_id]
            
            async with SquareAPIClient(self.access_token, self.environment, self.webhook_signature_key) as client:
                # Create payment
                amount_money = SquareMoney.from_decimal(
                    Decimal(str(subscription["amount"])),
                    subscription["currency"]
                )
                
                payment = await client.create_payment(
                    source_id=payment_source_id,
                    amount_money=amount_money,
                    location_id=self.default_location_id,
                    customer_id=subscription["customer_id"],
                    reference_id=subscription_id,
                    note=f"Creator subscription payment - {subscription['creator_id']}"
                )
                
                # Update subscription
                subscription["last_payment_id"] = payment.id
                subscription["last_payment_date"] = payment.created_at.isoformat()
                subscription["next_billing_date"] = (datetime.utcnow() + timedelta(days=30)).isoformat()
                
                payment_data = {
                    "payment_id": payment.id,
                    "subscription_id": subscription_id,
                    "amount": payment.amount_money.decimal_amount,
                    "currency": payment.amount_money.currency,
                    "status": payment.status.value,
                    "created_at": payment.created_at.isoformat(),
                    "receipt_url": payment.receipt_url
                }
                
                logger.info(f"Processed subscription payment: {payment.id}")
                return payment_data
                
        except Exception as e:
            logger.error(f"Failed to process subscription payment: {str(e)}")
            raise
    
    async def process_one_time_payment(self, creator_id: str, amount: Decimal,
                                     currency: str, payment_source_id: str,
                                     customer_email: str, description: str = "") -> Dict[str, Any]:
        """Process a one-time payment for creator content."""
        try:
            if currency not in self.supported_currencies:
                raise ValueError(f"Currency {currency} not supported by Square")
            
            async with SquareAPIClient(self.access_token, self.environment, self.webhook_signature_key) as client:
                # Create payment
                amount_money = SquareMoney.from_decimal(amount, currency)
                
                payment = await client.create_payment(
                    source_id=payment_source_id,
                    amount_money=amount_money,
                    location_id=self.default_location_id,
                    reference_id=f"creator_{creator_id}_onetime",
                    note=description or f"One-time payment to creator {creator_id}"
                )
                
                payment_data = {
                    "payment_id": payment.id,
                    "creator_id": creator_id,
                    "amount": payment.amount_money.decimal_amount,
                    "currency": payment.amount_money.currency,
                    "status": payment.status.value,
                    "customer_email": customer_email,
                    "description": description,
                    "created_at": payment.created_at.isoformat(),
                    "receipt_url": payment.receipt_url
                }
                
                logger.info(f"Processed one-time payment for creator {creator_id}: {amount} {currency}")
                return payment_data
                
        except Exception as e:
            logger.error(f"Failed to process one-time payment: {str(e)}")
            raise
    
    async def refund_payment(self, payment_id: str, amount: Optional[Decimal] = None,
                           reason: str = "Customer refund") -> Dict[str, Any]:
        """Refund a payment."""
        try:
            async with SquareAPIClient(self.access_token, self.environment, self.webhook_signature_key) as client:
                # Get original payment to determine refund amount
                payment = await client.get_payment(payment_id)
                
                refund_amount = amount or payment.amount_money.decimal_amount
                refund_money = SquareMoney.from_decimal(refund_amount, payment.amount_money.currency)
                
                refund = await client.refund_payment(
                    payment_id=payment_id,
                    amount_money=refund_money,
                    reason=reason
                )
                
                refund_data = {
                    "refund_id": refund.id,
                    "payment_id": payment_id,
                    "amount": refund.amount_money.decimal_amount,
                    "currency": refund.amount_money.currency,
                    "status": refund.status,
                    "reason": refund.reason,
                    "created_at": refund.created_at.isoformat()
                }
                
                logger.info(f"Processed refund: {refund.id} for payment {payment_id}")
                return refund_data
                
        except Exception as e:
            logger.error(f"Failed to refund payment: {str(e)}")
            raise
    
    async def get_payment_status(self, payment_id: str) -> Dict[str, Any]:
        """Get payment status."""
        try:
            async with SquareAPIClient(self.access_token, self.environment, self.webhook_signature_key) as client:
                payment = await client.get_payment(payment_id)
                
                return {
                    "payment_id": payment.id,
                    "status": payment.status.value,
                    "amount": payment.amount_money.decimal_amount,
                    "currency": payment.amount_money.currency,
                    "created_at": payment.created_at.isoformat(),
                    "updated_at": payment.updated_at.isoformat(),
                    "receipt_url": payment.receipt_url
                }
                
        except Exception as e:
            logger.error(f"Failed to get payment status: {str(e)}")
            raise
    
    async def cancel_subscription(self, subscription_id: str) -> bool:
        """Cancel a subscription."""
        try:
            if subscription_id not in self.subscriptions:
                raise ValueError(f"Subscription {subscription_id} not found")
            
            subscription = self.subscriptions[subscription_id]
            subscription["status"] = "cancelled"
            subscription["cancelled_at"] = datetime.utcnow().isoformat()
            
            logger.info(f"Cancelled subscription: {subscription_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to cancel subscription: {str(e)}")
            return False
    
    async def handle_webhook(self, body: str, signature: str, notification_url: str) -> Dict[str, Any]:
        """Handle Square webhook."""
        try:
            async with SquareAPIClient(self.access_token, self.environment, self.webhook_signature_key) as client:
                if not client.verify_webhook_signature(body, signature, notification_url):
                    raise ValueError("Invalid webhook signature")
                
                webhook_data = json.loads(body)
                event_type = webhook_data.get("type", "")
                
                if event_type == "payment.updated":
                    return await self._handle_payment_updated(webhook_data)
                elif event_type == "refund.updated":
                    return await self._handle_refund_updated(webhook_data)
                
                logger.info(f"Received Square webhook: {event_type}")
                return {"status": "received", "event_type": event_type}
                
        except Exception as e:
            logger.error(f"Failed to handle webhook: {str(e)}")
            raise
    
    async def _handle_payment_updated(self, webhook_data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle payment updated webhook."""
        try:
            payment_data = webhook_data.get("data", {}).get("object", {}).get("payment", {})
            payment_id = payment_data.get("id", "")
            status = payment_data.get("status", "")
            
            logger.info(f"Payment {payment_id} status updated to: {status}")
            
            return {
                "status": "processed",
                "payment_id": payment_id,
                "new_status": status
            }
            
        except Exception as e:
            logger.error(f"Failed to handle payment updated webhook: {str(e)}")
            raise
    
    async def _handle_refund_updated(self, webhook_data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle refund updated webhook."""
        try:
            refund_data = webhook_data.get("data", {}).get("object", {}).get("refund", {})
            refund_id = refund_data.get("id", "")
            status = refund_data.get("status", "")
            
            logger.info(f"Refund {refund_id} status updated to: {status}")
            
            return {
                "status": "processed",
                "refund_id": refund_id,
                "new_status": status
            }
            
        except Exception as e:
            logger.error(f"Failed to handle refund updated webhook: {str(e)}")
            raise
    
    async def get_subscription_status(self, subscription_id: str) -> Dict[str, Any]:
        """Get subscription status."""
        if subscription_id not in self.subscriptions:
            raise ValueError(f"Subscription {subscription_id} not found")
        
        return self.subscriptions[subscription_id]
    
    async def list_subscriptions(self, creator_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """List subscriptions, optionally filtered by creator."""
        if creator_id:
            return [sub for sub in self.subscriptions.values() if sub["creator_id"] == creator_id]
        
        return list(self.subscriptions.values())


# Example usage
async def main() -> None:
    """Example usage of Square integration."""
    square = SquareIntegration(
        access_token="your-square-access-token",
        environment=SquareEnvironment.SANDBOX,
        webhook_signature_key="your-webhook-signature-key"
    )
    
    # Initialize
    if await square.initialize():
        print("✅ Square integration initialized")
        
        # Create creator subscription
        subscription = await square.create_creator_subscription(
            creator_id="creator_123",
            customer_email="customer@example.com",
            customer_name="John Doe",
            subscription_amount=Decimal("9.99"),
            currency="USD"
        )
        
        print(f"💳 Created subscription: {subscription['subscription_id']}")
        print(f"💰 Amount: {subscription['amount']} {subscription['currency']}")
        
        # Process one-time payment
        payment = await square.process_one_time_payment(
            creator_id="creator_123",
            amount=Decimal("4.99"),
            currency="USD",
            payment_source_id="card-nonce-from-frontend",
            customer_email="customer@example.com",
            description="Premium content access"
        )
        
        print(f"💸 Processed payment: {payment['payment_id']}")
        print(f"🧾 Receipt: {payment['receipt_url']}")


if __name__ == "__main__":
    asyncio.run(main())