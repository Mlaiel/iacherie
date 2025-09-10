"""Stripe Integration - Comprehensive Payment Processing Platform
==============================================================

Enterprise-grade Stripe integration supporting payments, subscriptions,
marketplace functionality, and advanced financial operations.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import logging
import json
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import uuid
from decimal import Decimal

import stripe
import httpx
from stripe.error import (
    StripeError, CardError, RateLimitError, InvalidRequestError,
    AuthenticationError, APIConnectionError, APIError
)


class PaymentStatus(Enum):
    """Payment status types."""
    PENDING = "pending"
    PROCESSING = "processing"
    SUCCEEDED = "succeeded"
    FAILED = "failed"
    CANCELED = "canceled"
    REQUIRES_ACTION = "requires_action"
    REQUIRES_CONFIRMATION = "requires_confirmation"
    REQUIRES_PAYMENT_METHOD = "requires_payment_method"


class SubscriptionStatus(Enum):
    """Subscription status types."""
    INCOMPLETE = "incomplete"
    INCOMPLETE_EXPIRED = "incomplete_expired"
    TRIALING = "trialing"
    ACTIVE = "active"
    PAST_DUE = "past_due"
    CANCELED = "canceled"
    UNPAID = "unpaid"


class PayoutStatus(Enum):
    """Payout status types."""
    PENDING = "pending"
    PAID = "paid"
    FAILED = "failed"
    CANCELED = "canceled"
    IN_TRANSIT = "in_transit"


@dataclass
class PaymentMethod:
    """Payment method information."""
    id: str
    type: str  # card, bank_account, etc.
    details: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: Optional[datetime] = None
    last_used: Optional[datetime] = None


@dataclass
class Customer:
    """Customer information."""
    id: str
    email: Optional[str] = None
    name: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[Dict[str, str]] = None
    payment_methods: List[PaymentMethod] = field(default_factory=list)
    default_payment_method: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: Optional[datetime] = None


@dataclass
class PaymentIntent:
    """Payment intent information."""
    id: str
    amount: int  # Amount in cents
    currency: str
    status: PaymentStatus
    customer_id: Optional[str] = None
    payment_method_id: Optional[str] = None
    description: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


@dataclass
class Subscription:
    """Subscription information."""
    id: str
    customer_id: str
    status: SubscriptionStatus
    current_period_start: datetime
    current_period_end: datetime
    plan_id: Optional[str] = None
    items: List[Dict[str, Any]] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: Optional[datetime] = None


@dataclass
class ConnectedAccount:
    """Stripe Connect account information."""
    id: str
    type: str  # standard, express, custom
    country: str
    email: Optional[str] = None
    business_profile: Dict[str, Any] = field(default_factory=dict)
    capabilities: Dict[str, str] = field(default_factory=dict)
    requirements: Dict[str, Any] = field(default_factory=dict)
    payouts_enabled: bool = False
    charges_enabled: bool = False
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: Optional[datetime] = None


class StripeIntegration:
    """Comprehensive Stripe payment integration."""
    
    def __init__(
        self,
        api_key: str,
        webhook_secret: Optional[str] = None,
        config: Optional[Dict[str, Any]] = None
    ):
        self.api_key = api_key
        self.webhook_secret = webhook_secret
        self.config = config or {}
        self.logger = logging.getLogger(__name__)
        
        # Configure Stripe
        stripe.api_key = api_key
        stripe.api_version = "2023-10-16"
        
        # Rate limiting and retry configuration
        self.max_retries = self.config.get('max_retries', 3)
        self.retry_delay = self.config.get('retry_delay', 1.0)
        
        # Performance metrics
        self.metrics = {
            'total_requests': 0,
            'successful_requests': 0,
            'failed_requests': 0,
            'total_amount_processed': 0,  # in cents
            'total_fees_collected': 0,
            'average_response_time': 0.0,
            'error_types': {},
            'payment_methods': {},
            'currencies': {}
        }
        
        # Event handlers
        self.event_handlers: Dict[str, List[callable]] = {}
        
        # Cache for frequently accessed data
        self.customer_cache: Dict[str, Customer] = {}
        self.cache_ttl = timedelta(minutes=15)
        
    async def initialize(self):
        """Initialize the Stripe integration."""
        # Test API connectivity
        try:
            balance = stripe.Balance.retrieve()
            self.logger.info(f"Stripe connected successfully. Balance: {balance.available}")
        except Exception as e:
            self.logger.error(f"Stripe initialization failed: {e}")
            raise
        
        self.logger.info("Stripe integration initialized")
    
    # Customer Management
    async def create_customer(
        self,
        email: Optional[str] = None,
        name: Optional[str] = None,
        phone: Optional[str] = None,
        address: Optional[Dict[str, str]] = None,
        payment_method_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Customer:
        """Create a new customer."""
        try:
            customer_data = {}
            if email:
                customer_data['email'] = email
            if name:
                customer_data['name'] = name
            if phone:
                customer_data['phone'] = phone
            if address:
                customer_data['address'] = address
            if payment_method_id:
                customer_data['payment_method'] = payment_method_id
            if metadata:
                customer_data['metadata'] = metadata
            
            stripe_customer = stripe.Customer.create(**customer_data)
            
            customer = Customer(
                id=stripe_customer.id,
                email=stripe_customer.email,
                name=stripe_customer.name,
                phone=stripe_customer.phone,
                address=stripe_customer.address,
                metadata=stripe_customer.metadata,
                created_at=datetime.fromtimestamp(stripe_customer.created)
            )
            
            # Cache the customer
            self.customer_cache[customer.id] = customer
            
            await self._update_metrics('create_customer', success=True)
            self.logger.info(f"Created customer: {customer.id}")
            return customer
            
        except StripeError as e:
            await self._update_metrics('create_customer', success=False, error=e)
            self.logger.error(f"Failed to create customer: {e}")
            raise
    
    async def get_customer(self, customer_id: str) -> Optional[Customer]:
        """Get customer by ID."""
        # Check cache first
        if customer_id in self.customer_cache:
            return self.customer_cache[customer_id]
        
        try:
            stripe_customer = stripe.Customer.retrieve(customer_id)
            
            customer = Customer(
                id=stripe_customer.id,
                email=stripe_customer.email,
                name=stripe_customer.name,
                phone=stripe_customer.phone,
                address=stripe_customer.address,
                metadata=stripe_customer.metadata,
                created_at=datetime.fromtimestamp(stripe_customer.created)
            )
            
            # Cache the customer
            self.customer_cache[customer_id] = customer
            
            await self._update_metrics('get_customer', success=True)
            return customer
            
        except StripeError as e:
            await self._update_metrics('get_customer', success=False, error=e)
            self.logger.error(f"Failed to get customer {customer_id}: {e}")
            return None
    
    async def update_customer(
        self,
        customer_id: str,
        email: Optional[str] = None,
        name: Optional[str] = None,
        phone: Optional[str] = None,
        address: Optional[Dict[str, str]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Customer:
        """Update customer information."""
        try:
            update_data = {}
            if email is not None:
                update_data['email'] = email
            if name is not None:
                update_data['name'] = name
            if phone is not None:
                update_data['phone'] = phone
            if address is not None:
                update_data['address'] = address
            if metadata is not None:
                update_data['metadata'] = metadata
            
            stripe_customer = stripe.Customer.modify(customer_id, **update_data)
            
            customer = Customer(
                id=stripe_customer.id,
                email=stripe_customer.email,
                name=stripe_customer.name,
                phone=stripe_customer.phone,
                address=stripe_customer.address,
                metadata=stripe_customer.metadata,
                created_at=datetime.fromtimestamp(stripe_customer.created)
            )
            
            # Update cache
            self.customer_cache[customer_id] = customer
            
            await self._update_metrics('update_customer', success=True)
            self.logger.info(f"Updated customer: {customer_id}")
            return customer
            
        except StripeError as e:
            await self._update_metrics('update_customer', success=False, error=e)
            self.logger.error(f"Failed to update customer {customer_id}: {e}")
            raise
    
    # Payment Processing
    async def create_payment_intent(
        self,
        amount: int,
        currency: str,
        customer_id: Optional[str] = None,
        payment_method_id: Optional[str] = None,
        description: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
        automatic_payment_methods: bool = True,
        capture_method: str = "automatic"
    ) -> PaymentIntent:
        """Create a payment intent."""
        try:
            intent_data = {
                'amount': amount,
                'currency': currency.lower(),
                'capture_method': capture_method
            }
            
            if customer_id:
                intent_data['customer'] = customer_id
            if payment_method_id:
                intent_data['payment_method'] = payment_method_id
            if description:
                intent_data['description'] = description
            if metadata:
                intent_data['metadata'] = metadata
            if automatic_payment_methods:
                intent_data['automatic_payment_methods'] = {'enabled': True}
            
            stripe_intent = stripe.PaymentIntent.create(**intent_data)
            
            payment_intent = PaymentIntent(
                id=stripe_intent.id,
                amount=stripe_intent.amount,
                currency=stripe_intent.currency,
                status=PaymentStatus(stripe_intent.status),
                customer_id=stripe_intent.customer,
                payment_method_id=stripe_intent.payment_method,
                description=stripe_intent.description,
                metadata=stripe_intent.metadata,
                created_at=datetime.fromtimestamp(stripe_intent.created)
            )
            
            await self._update_metrics('create_payment_intent', success=True)
            self.metrics['total_amount_processed'] += amount
            self.metrics['currencies'][currency] = self.metrics['currencies'].get(currency, 0) + 1
            
            self.logger.info(f"Created payment intent: {payment_intent.id}")
            return payment_intent
            
        except StripeError as e:
            await self._update_metrics('create_payment_intent', success=False, error=e)
            self.logger.error(f"Failed to create payment intent: {e}")
            raise
    
    async def confirm_payment_intent(
        self,
        payment_intent_id: str,
        payment_method_id: Optional[str] = None,
        return_url: Optional[str] = None
    ) -> PaymentIntent:
        """Confirm a payment intent."""
        try:
            confirm_data = {}
            if payment_method_id:
                confirm_data['payment_method'] = payment_method_id
            if return_url:
                confirm_data['return_url'] = return_url
            
            stripe_intent = stripe.PaymentIntent.confirm(payment_intent_id, **confirm_data)
            
            payment_intent = PaymentIntent(
                id=stripe_intent.id,
                amount=stripe_intent.amount,
                currency=stripe_intent.currency,
                status=PaymentStatus(stripe_intent.status),
                customer_id=stripe_intent.customer,
                payment_method_id=stripe_intent.payment_method,
                description=stripe_intent.description,
                metadata=stripe_intent.metadata,
                created_at=datetime.fromtimestamp(stripe_intent.created)
            )
            
            await self._update_metrics('confirm_payment_intent', success=True)
            self.logger.info(f"Confirmed payment intent: {payment_intent_id}")
            return payment_intent
            
        except StripeError as e:
            await self._update_metrics('confirm_payment_intent', success=False, error=e)
            self.logger.error(f"Failed to confirm payment intent {payment_intent_id}: {e}")
            raise
    
    async def capture_payment_intent(self, payment_intent_id: str) -> PaymentIntent:
        """Capture a payment intent (for manual capture)."""
        try:
            stripe_intent = stripe.PaymentIntent.capture(payment_intent_id)
            
            payment_intent = PaymentIntent(
                id=stripe_intent.id,
                amount=stripe_intent.amount,
                currency=stripe_intent.currency,
                status=PaymentStatus(stripe_intent.status),
                customer_id=stripe_intent.customer,
                payment_method_id=stripe_intent.payment_method,
                description=stripe_intent.description,
                metadata=stripe_intent.metadata,
                created_at=datetime.fromtimestamp(stripe_intent.created)
            )
            
            await self._update_metrics('capture_payment_intent', success=True)
            self.logger.info(f"Captured payment intent: {payment_intent_id}")
            return payment_intent
            
        except StripeError as e:
            await self._update_metrics('capture_payment_intent', success=False, error=e)
            self.logger.error(f"Failed to capture payment intent {payment_intent_id}: {e}")
            raise
    
    # Subscription Management
    async def create_subscription(
        self,
        customer_id: str,
        price_id: str,
        payment_behavior: str = "default_incomplete",
        trial_period_days: Optional[int] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Subscription:
        """Create a subscription."""
        try:
            subscription_data = {
                'customer': customer_id,
                'items': [{'price': price_id}],
                'payment_behavior': payment_behavior,
                'expand': ['latest_invoice.payment_intent']
            }
            
            if trial_period_days:
                subscription_data['trial_period_days'] = trial_period_days
            if metadata:
                subscription_data['metadata'] = metadata
            
            stripe_subscription = stripe.Subscription.create(**subscription_data)
            
            subscription = Subscription(
                id=stripe_subscription.id,
                customer_id=stripe_subscription.customer,
                status=SubscriptionStatus(stripe_subscription.status),
                current_period_start=datetime.fromtimestamp(stripe_subscription.current_period_start),
                current_period_end=datetime.fromtimestamp(stripe_subscription.current_period_end),
                plan_id=price_id,
                items=[item for item in stripe_subscription.items.data],
                metadata=stripe_subscription.metadata,
                created_at=datetime.fromtimestamp(stripe_subscription.created)
            )
            
            await self._update_metrics('create_subscription', success=True)
            self.logger.info(f"Created subscription: {subscription.id}")
            return subscription
            
        except StripeError as e:
            await self._update_metrics('create_subscription', success=False, error=e)
            self.logger.error(f"Failed to create subscription: {e}")
            raise
    
    async def cancel_subscription(
        self,
        subscription_id: str,
        at_period_end: bool = True
    ) -> Subscription:
        """Cancel a subscription."""
        try:
            if at_period_end:
                stripe_subscription = stripe.Subscription.modify(
                    subscription_id,
                    cancel_at_period_end=True
                )
            else:
                stripe_subscription = stripe.Subscription.delete(subscription_id)
            
            subscription = Subscription(
                id=stripe_subscription.id,
                customer_id=stripe_subscription.customer,
                status=SubscriptionStatus(stripe_subscription.status),
                current_period_start=datetime.fromtimestamp(stripe_subscription.current_period_start),
                current_period_end=datetime.fromtimestamp(stripe_subscription.current_period_end),
                items=[item for item in stripe_subscription.items.data],
                metadata=stripe_subscription.metadata,
                created_at=datetime.fromtimestamp(stripe_subscription.created)
            )
            
            await self._update_metrics('cancel_subscription', success=True)
            self.logger.info(f"Canceled subscription: {subscription_id}")
            return subscription
            
        except StripeError as e:
            await self._update_metrics('cancel_subscription', success=False, error=e)
            self.logger.error(f"Failed to cancel subscription {subscription_id}: {e}")
            raise
    
    # Stripe Connect (Marketplace)
    async def create_connected_account(
        self,
        account_type: str = "express",
        country: str = "US",
        email: Optional[str] = None,
        business_profile: Optional[Dict[str, Any]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> ConnectedAccount:
        """Create a connected account for marketplace."""
        try:
            account_data = {
                'type': account_type,
                'country': country
            }
            
            if email:
                account_data['email'] = email
            if business_profile:
                account_data['business_profile'] = business_profile
            if metadata:
                account_data['metadata'] = metadata
            
            stripe_account = stripe.Account.create(**account_data)
            
            connected_account = ConnectedAccount(
                id=stripe_account.id,
                type=stripe_account.type,
                country=stripe_account.country,
                email=stripe_account.email,
                business_profile=stripe_account.business_profile or {},
                capabilities=stripe_account.capabilities or {},
                requirements=stripe_account.requirements or {},
                payouts_enabled=stripe_account.payouts_enabled,
                charges_enabled=stripe_account.charges_enabled,
                metadata=stripe_account.metadata,
                created_at=datetime.fromtimestamp(stripe_account.created)
            )
            
            await self._update_metrics('create_connected_account', success=True)
            self.logger.info(f"Created connected account: {connected_account.id}")
            return connected_account
            
        except StripeError as e:
            await self._update_metrics('create_connected_account', success=False, error=e)
            self.logger.error(f"Failed to create connected account: {e}")
            raise
    
    async def create_account_link(
        self,
        account_id: str,
        refresh_url: str,
        return_url: str,
        type: str = "account_onboarding"
    ) -> str:
        """Create an account link for onboarding."""
        try:
            account_link = stripe.AccountLink.create(
                account=account_id,
                refresh_url=refresh_url,
                return_url=return_url,
                type=type
            )
            
            await self._update_metrics('create_account_link', success=True)
            self.logger.info(f"Created account link for: {account_id}")
            return account_link.url
            
        except StripeError as e:
            await self._update_metrics('create_account_link', success=False, error=e)
            self.logger.error(f"Failed to create account link for {account_id}: {e}")
            raise
    
    async def create_transfer(
        self,
        amount: int,
        currency: str,
        destination: str,
        description: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Create a transfer to a connected account."""
        try:
            transfer_data = {
                'amount': amount,
                'currency': currency.lower(),
                'destination': destination
            }
            
            if description:
                transfer_data['description'] = description
            if metadata:
                transfer_data['metadata'] = metadata
            
            transfer = stripe.Transfer.create(**transfer_data)
            
            await self._update_metrics('create_transfer', success=True)
            self.logger.info(f"Created transfer: {transfer.id}")
            return transfer
            
        except StripeError as e:
            await self._update_metrics('create_transfer', success=False, error=e)
            self.logger.error(f"Failed to create transfer: {e}")
            raise
    
    # Webhook Processing
    async def process_webhook(
        self,
        payload: str,
        signature: str
    ) -> Dict[str, Any]:
        """Process Stripe webhook event."""
        try:
            if not self.webhook_secret:
                raise ValueError("Webhook secret not configured")
            
            event = stripe.Webhook.construct_event(
                payload, signature, self.webhook_secret
            )
            
            # Process the event
            await self._handle_webhook_event(event)
            
            self.logger.info(f"Processed webhook event: {event['type']}")
            return event
            
        except ValueError as e:
            self.logger.error(f"Invalid webhook payload: {e}")
            raise
        except stripe.error.SignatureVerificationError as e:
            self.logger.error(f"Invalid webhook signature: {e}")
            raise
    
    async def _handle_webhook_event(self, event: Dict[str, Any]):
        """Handle specific webhook events."""
        event_type = event['type']
        
        # Call registered event handlers
        if event_type in self.event_handlers:
            for handler in self.event_handlers[event_type]:
                try:
                    await handler(event)
                except Exception as e:
                    self.logger.error(f"Event handler failed for {event_type}: {e}")
        
        # Built-in event handling
        if event_type == 'payment_intent.succeeded':
            await self._handle_payment_succeeded(event['data']['object'])
        elif event_type == 'payment_intent.payment_failed':
            await self._handle_payment_failed(event['data']['object'])
        elif event_type == 'customer.subscription.created':
            await self._handle_subscription_created(event['data']['object'])
        elif event_type == 'customer.subscription.deleted':
            await self._handle_subscription_deleted(event['data']['object'])
    
    async def _handle_payment_succeeded(self, payment_intent: Dict[str, Any]):
        """Handle successful payment."""
        self.logger.info(f"Payment succeeded: {payment_intent['id']}")
        # Add custom logic here
    
    async def _handle_payment_failed(self, payment_intent: Dict[str, Any]):
        """Handle failed payment."""
        self.logger.warning(f"Payment failed: {payment_intent['id']}")
        # Add custom logic here
    
    async def _handle_subscription_created(self, subscription: Dict[str, Any]):
        """Handle subscription creation."""
        self.logger.info(f"Subscription created: {subscription['id']}")
        # Add custom logic here
    
    async def _handle_subscription_deleted(self, subscription: Dict[str, Any]):
        """Handle subscription deletion."""
        self.logger.info(f"Subscription deleted: {subscription['id']}")
        # Add custom logic here
    
    # Event Handler Registration
    def register_event_handler(self, event_type: str, handler: callable):
        """Register event handler for webhook events."""
        if event_type not in self.event_handlers:
            self.event_handlers[event_type] = []
        self.event_handlers[event_type].append(handler)
        
        self.logger.info(f"Registered event handler for: {event_type}")
    
    def unregister_event_handler(self, event_type: str, handler: callable):
        """Unregister event handler."""
        if event_type in self.event_handlers:
            try:
                self.event_handlers[event_type].remove(handler)
                self.logger.info(f"Unregistered event handler for: {event_type}")
            except ValueError:
                pass
    
    # Metrics and Monitoring
    async def _update_metrics(
        self,
        operation: str,
        success: bool,
        error: Optional[Exception] = None,
        processing_time: float = 0.0
    ):
        """Update integration metrics."""
        self.metrics['total_requests'] += 1
        
        if success:
            self.metrics['successful_requests'] += 1
        else:
            self.metrics['failed_requests'] += 1
            
            if error:
                error_type = type(error).__name__
                self.metrics['error_types'][error_type] = (
                    self.metrics['error_types'].get(error_type, 0) + 1
                )
        
        # Update average response time
        if processing_time > 0:
            total_requests = self.metrics['total_requests']
            current_avg = self.metrics['average_response_time']
            self.metrics['average_response_time'] = (
                (current_avg * (total_requests - 1) + processing_time) / total_requests
            )
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get integration metrics."""
        return {
            'requests': {
                'total': self.metrics['total_requests'],
                'successful': self.metrics['successful_requests'],
                'failed': self.metrics['failed_requests'],
                'success_rate': (
                    self.metrics['successful_requests'] / max(self.metrics['total_requests'], 1)
                ) * 100
            },
            'financial': {
                'total_amount_processed': self.metrics['total_amount_processed'],
                'total_fees_collected': self.metrics['total_fees_collected'],
                'currencies': self.metrics['currencies']
            },
            'performance': {
                'average_response_time': self.metrics['average_response_time']
            },
            'errors': self.metrics['error_types'],
            'payment_methods': self.metrics['payment_methods']
        }
    
    async def health_check(self) -> Dict[str, Any]:
        """Perform health check."""
        try:
            # Test API connectivity
            balance = stripe.Balance.retrieve()
            
            return {
                'status': 'healthy',
                'api_accessible': True,
                'balance_available': len(balance.available) > 0,
                'last_check': datetime.now().isoformat()
            }
        except Exception as e:
            return {
                'status': 'unhealthy',
                'api_accessible': False,
                'error': str(e),
                'last_check': datetime.now().isoformat()
            }


# Example usage
if __name__ == "__main__":
    async def main():
        # Initialize Stripe integration
        stripe_integration = StripeIntegration(
            api_key="sk_test_your_stripe_key",
            webhook_secret="whsec_your_webhook_secret"
        )
        
        await stripe_integration.initialize()
        
        # Create customer
        customer = await stripe_integration.create_customer(
            email="customer@example.com",
            name="John Doe"
        )
        print(f"Created customer: {customer.id}")
        
        # Create payment intent
        payment_intent = await stripe_integration.create_payment_intent(
            amount=2000,  # $20.00
            currency="usd",
            customer_id=customer.id,
            description="Test payment"
        )
        print(f"Created payment intent: {payment_intent.id}")
        
        # Get metrics
        metrics = stripe_integration.get_metrics()
        print(f"Metrics: {json.dumps(metrics, indent=2)}")
    
    # asyncio.run(main())