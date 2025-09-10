"""Stripe Payment Gateway Integration
===================================

Comprehensive Stripe integration for payment processing, subscriptions,
and financial transactions in the Ainflue creator economy platform.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import logging
import json
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, asdict
from enum import Enum
from datetime import datetime, timedelta
import aiohttp
import stripe
from decimal import Decimal


class StripeProduct(Enum):
    """Stripe product types"""
    CONTENT_PROTECTION = "content_protection"
    AI_PROCESSING = "ai_processing"
    DISTRIBUTION = "distribution"
    COLLABORATION = "collaboration"
    PREMIUM_FEATURES = "premium_features"


class PaymentStatus(Enum):
    """Payment status enumeration"""
    PENDING = "pending"
    PROCESSING = "processing"
    SUCCEEDED = "succeeded"
    FAILED = "failed"
    CANCELED = "canceled"
    REFUNDED = "refunded"


@dataclass
class StripeConfig:
    """Stripe configuration"""
    publishable_key: str
    secret_key: str
    webhook_secret: str
    api_version: str = "2023-10-16"
    connect_client_id: Optional[str] = None
    environment: str = "sandbox"  # sandbox or production


@dataclass
class PaymentRequest:
    """Payment request structure"""
    amount: int  # Amount in cents
    currency: str = "usd"
    description: Optional[str] = None
    customer_id: Optional[str] = None
    payment_method_id: Optional[str] = None
    metadata: Optional[Dict[str, str]] = None
    automatic_payment_methods: bool = True
    return_url: Optional[str] = None


@dataclass
class SubscriptionRequest:
    """Subscription request structure"""
    customer_id: str
    price_id: str
    trial_period_days: Optional[int] = None
    metadata: Optional[Dict[str, str]] = None
    payment_behavior: str = "default_incomplete"
    expand: List[str] = None


@dataclass
class CreatorPayout:
    """Creator payout structure"""
    creator_id: str
    amount: int  # Amount in cents
    currency: str = "usd"
    description: Optional[str] = None
    metadata: Optional[Dict[str, str]] = None


class StripeIntegration:
    """Stripe payment gateway integration"""
    
    def __init__(self, config: StripeConfig, rate_limiter=None, cache_manager=None):
        """Initialize Stripe integration
        
        Args:
            config: Stripe configuration
            rate_limiter: Rate limiter instance
            cache_manager: Cache manager instance
        """
        self.config = config
        self.rate_limiter = rate_limiter
        self.cache_manager = cache_manager
        self.logger = logging.getLogger(__name__)
        
        # Configure Stripe
        stripe.api_key = config.secret_key
        stripe.api_version = config.api_version
        
        # Session for webhooks
        self.session = None
        
        # Statistics
        self.stats = {
            "payments_processed": 0,
            "total_volume": 0,
            "subscriptions_created": 0,
            "payouts_processed": 0,
            "refunds_processed": 0,
            "failed_payments": 0
        }
        
        # Product catalog
        self.products = {}
        self.prices = {}
    
    async def initialize(self):
        """Initialize the integration"""
        try:
            # Create HTTP session for webhooks
            self.session = aiohttp.ClientSession()
            
            # Setup product catalog
            await self._setup_product_catalog()
            
            # Test connection
            await self._test_connection()
            
            self.logger.info("Stripe integration initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize Stripe integration: {e}")
            raise
    
    async def shutdown(self):
        """Shutdown the integration"""
        if self.session:
            await self.session.close()
        self.logger.info("Stripe integration shutdown complete")
    
    async def _test_connection(self):
        """Test Stripe API connection"""
        try:
            # Test with a simple account retrieval
            account = stripe.Account.retrieve()
            if account:
                self.logger.info(f"Stripe connection test successful - Account: {account.id}")
            else:
                raise Exception("No account data returned")
                
        except Exception as e:
            self.logger.error(f"Stripe connection test failed: {e}")
            raise
    
    async def _setup_product_catalog(self):
        """Setup Ainflue product catalog in Stripe"""
        try:
            # Define Ainflue products
            ainflue_products = [
                {
                    "id": StripeProduct.CONTENT_PROTECTION.value,
                    "name": "Content Protection Service",
                    "description": "AI-powered content protection and DMCA monitoring",
                    "type": "service"
                },
                {
                    "id": StripeProduct.AI_PROCESSING.value,
                    "name": "AI Content Processing",
                    "description": "Advanced AI processing for content optimization",
                    "type": "service"
                },
                {
                    "id": StripeProduct.DISTRIBUTION.value,
                    "name": "Multi-Platform Distribution",
                    "description": "Automated content distribution across platforms",
                    "type": "service"
                },
                {
                    "id": StripeProduct.COLLABORATION.value,
                    "name": "Creator Collaboration Tools",
                    "description": "Advanced collaboration and matching tools",
                    "type": "service"
                },
                {
                    "id": StripeProduct.PREMIUM_FEATURES.value,
                    "name": "Premium Features",
                    "description": "Access to premium Ainflue features",
                    "type": "service"
                }
            ]
            
            # Create or retrieve products
            for product_data in ainflue_products:
                try:
                    product = stripe.Product.retrieve(product_data["id"])
                    self.products[product_data["id"]] = product
                except stripe.error.InvalidRequestError:
                    # Product doesn't exist, create it
                    product = stripe.Product.create(
                        id=product_data["id"],
                        name=product_data["name"],
                        description=product_data["description"],
                        type=product_data["type"]
                    )
                    self.products[product_data["id"]] = product
                    self.logger.info(f"Created Stripe product: {product_data['name']}")
            
            self.logger.info("Product catalog setup complete")
            
        except Exception as e:
            self.logger.error(f"Failed to setup product catalog: {e}")
    
    async def create_payment_intent(self, request: PaymentRequest) -> Dict[str, Any]:
        """Create payment intent
        
        Args:
            request: Payment request
            
        Returns:
            Dict[str, Any]: Payment intent data
        """
        try:
            # Check rate limits
            if self.rate_limiter:
                allowed = await self.rate_limiter.allow_request("stripe", rule_name="payment_intents")
                if not allowed:
                    raise Exception("Rate limit exceeded")
            
            # Prepare payment intent data
            intent_data = {
                "amount": request.amount,
                "currency": request.currency,
                "automatic_payment_methods": {
                    "enabled": request.automatic_payment_methods
                }
            }
            
            if request.description:
                intent_data["description"] = request.description
            
            if request.customer_id:
                intent_data["customer"] = request.customer_id
            
            if request.payment_method_id:
                intent_data["payment_method"] = request.payment_method_id
                intent_data["confirmation_method"] = "manual"
                intent_data["confirm"] = True
            
            if request.metadata:
                intent_data["metadata"] = request.metadata
            
            if request.return_url:
                intent_data["return_url"] = request.return_url
            
            # Create payment intent
            payment_intent = stripe.PaymentIntent.create(**intent_data)
            
            # Update statistics
            self.stats["payments_processed"] += 1
            self.stats["total_volume"] += request.amount
            
            result = {
                "id": payment_intent.id,
                "client_secret": payment_intent.client_secret,
                "status": payment_intent.status,
                "amount": payment_intent.amount,
                "currency": payment_intent.currency,
                "created": payment_intent.created,
                "metadata": payment_intent.metadata
            }
            
            self.logger.info(f"Created payment intent: {payment_intent.id}")
            return result
            
        except Exception as e:
            self.stats["failed_payments"] += 1
            self.logger.error(f"Payment intent creation failed: {e}")
            raise
    
    async def confirm_payment_intent(self, payment_intent_id: str, 
                                   payment_method_id: Optional[str] = None) -> Dict[str, Any]:
        """Confirm payment intent
        
        Args:
            payment_intent_id: Payment intent ID
            payment_method_id: Payment method ID
            
        Returns:
            Dict[str, Any]: Confirmed payment intent
        """
        try:
            confirm_data = {}
            
            if payment_method_id:
                confirm_data["payment_method"] = payment_method_id
            
            # Confirm payment intent
            payment_intent = stripe.PaymentIntent.confirm(
                payment_intent_id,
                **confirm_data
            )
            
            result = {
                "id": payment_intent.id,
                "status": payment_intent.status,
                "amount": payment_intent.amount,
                "currency": payment_intent.currency,
                "charges": payment_intent.charges.data if payment_intent.charges else []
            }
            
            self.logger.info(f"Confirmed payment intent: {payment_intent_id}")
            return result
            
        except Exception as e:
            self.logger.error(f"Payment intent confirmation failed: {e}")
            raise
    
    async def create_customer(self, email: str, name: Optional[str] = None,
                            metadata: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        """Create Stripe customer
        
        Args:
            email: Customer email
            name: Customer name
            metadata: Additional metadata
            
        Returns:
            Dict[str, Any]: Customer data
        """
        try:
            customer_data = {"email": email}
            
            if name:
                customer_data["name"] = name
            
            if metadata:
                customer_data["metadata"] = metadata
            
            customer = stripe.Customer.create(**customer_data)
            
            result = {
                "id": customer.id,
                "email": customer.email,
                "name": customer.name,
                "created": customer.created,
                "metadata": customer.metadata
            }
            
            self.logger.info(f"Created customer: {customer.id}")
            return result
            
        except Exception as e:
            self.logger.error(f"Customer creation failed: {e}")
            raise
    
    async def create_subscription(self, request: SubscriptionRequest) -> Dict[str, Any]:
        """Create subscription
        
        Args:
            request: Subscription request
            
        Returns:
            Dict[str, Any]: Subscription data
        """
        try:
            # Prepare subscription data
            subscription_data = {
                "customer": request.customer_id,
                "items": [{"price": request.price_id}],
                "payment_behavior": request.payment_behavior,
                "payment_settings": {
                    "save_default_payment_method": "on_subscription"
                },
                "expand": request.expand or ["latest_invoice.payment_intent"]
            }
            
            if request.trial_period_days:
                subscription_data["trial_period_days"] = request.trial_period_days
            
            if request.metadata:
                subscription_data["metadata"] = request.metadata
            
            # Create subscription
            subscription = stripe.Subscription.create(**subscription_data)
            
            # Update statistics
            self.stats["subscriptions_created"] += 1
            
            result = {
                "id": subscription.id,
                "status": subscription.status,
                "customer": subscription.customer,
                "current_period_start": subscription.current_period_start,
                "current_period_end": subscription.current_period_end,
                "trial_end": subscription.trial_end,
                "latest_invoice": subscription.latest_invoice,
                "metadata": subscription.metadata
            }
            
            self.logger.info(f"Created subscription: {subscription.id}")
            return result
            
        except Exception as e:
            self.logger.error(f"Subscription creation failed: {e}")
            raise
    
    async def cancel_subscription(self, subscription_id: str, 
                                at_period_end: bool = True) -> Dict[str, Any]:
        """Cancel subscription
        
        Args:
            subscription_id: Subscription ID
            at_period_end: Whether to cancel at period end
            
        Returns:
            Dict[str, Any]: Canceled subscription data
        """
        try:
            if at_period_end:
                # Cancel at period end
                subscription = stripe.Subscription.modify(
                    subscription_id,
                    cancel_at_period_end=True
                )
            else:
                # Cancel immediately
                subscription = stripe.Subscription.delete(subscription_id)
            
            result = {
                "id": subscription.id,
                "status": subscription.status,
                "canceled_at": subscription.canceled_at,
                "cancel_at_period_end": subscription.cancel_at_period_end,
                "current_period_end": subscription.current_period_end
            }
            
            self.logger.info(f"Canceled subscription: {subscription_id}")
            return result
            
        except Exception as e:
            self.logger.error(f"Subscription cancellation failed: {e}")
            raise
    
    async def create_payout(self, payout: CreatorPayout, 
                          connected_account_id: str) -> Dict[str, Any]:
        """Create payout to creator
        
        Args:
            payout: Creator payout data
            connected_account_id: Stripe connected account ID
            
        Returns:
            Dict[str, Any]: Payout data
        """
        try:
            # Create transfer to connected account
            transfer = stripe.Transfer.create(
                amount=payout.amount,
                currency=payout.currency,
                destination=connected_account_id,
                description=payout.description,
                metadata=payout.metadata or {}
            )
            
            # Update statistics
            self.stats["payouts_processed"] += 1
            
            result = {
                "id": transfer.id,
                "amount": transfer.amount,
                "currency": transfer.currency,
                "destination": transfer.destination,
                "created": transfer.created,
                "description": transfer.description,
                "metadata": transfer.metadata
            }
            
            self.logger.info(f"Created payout: {transfer.id} to {payout.creator_id}")
            return result
            
        except Exception as e:
            self.logger.error(f"Payout creation failed: {e}")
            raise
    
    async def create_refund(self, payment_intent_id: str, amount: Optional[int] = None,
                          reason: Optional[str] = None) -> Dict[str, Any]:
        """Create refund
        
        Args:
            payment_intent_id: Payment intent ID
            amount: Refund amount (None for full refund)
            reason: Refund reason
            
        Returns:
            Dict[str, Any]: Refund data
        """
        try:
            refund_data = {"payment_intent": payment_intent_id}
            
            if amount:
                refund_data["amount"] = amount
            
            if reason:
                refund_data["reason"] = reason
            
            refund = stripe.Refund.create(**refund_data)
            
            # Update statistics
            self.stats["refunds_processed"] += 1
            
            result = {
                "id": refund.id,
                "amount": refund.amount,
                "currency": refund.currency,
                "payment_intent": refund.payment_intent,
                "reason": refund.reason,
                "status": refund.status,
                "created": refund.created
            }
            
            self.logger.info(f"Created refund: {refund.id}")
            return result
            
        except Exception as e:
            self.logger.error(f"Refund creation failed: {e}")
            raise
    
    async def handle_webhook(self, payload: bytes, signature: str) -> Dict[str, Any]:
        """Handle Stripe webhook
        
        Args:
            payload: Webhook payload
            signature: Webhook signature
            
        Returns:
            Dict[str, Any]: Processed event data
        """
        try:
            # Verify webhook signature
            event = stripe.Webhook.construct_event(
                payload, signature, self.config.webhook_secret
            )
            
            # Process event
            event_type = event["type"]
            event_data = event["data"]["object"]
            
            self.logger.info(f"Processing webhook event: {event_type}")
            
            # Handle different event types
            if event_type == "payment_intent.succeeded":
                await self._handle_payment_succeeded(event_data)
            elif event_type == "payment_intent.payment_failed":
                await self._handle_payment_failed(event_data)
            elif event_type == "customer.subscription.created":
                await self._handle_subscription_created(event_data)
            elif event_type == "customer.subscription.deleted":
                await self._handle_subscription_canceled(event_data)
            elif event_type == "invoice.payment_succeeded":
                await self._handle_invoice_payment_succeeded(event_data)
            elif event_type == "invoice.payment_failed":
                await self._handle_invoice_payment_failed(event_data)
            
            return {
                "event_id": event["id"],
                "event_type": event_type,
                "processed": True,
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except stripe.error.SignatureVerificationError:
            self.logger.error("Invalid webhook signature")
            raise Exception("Invalid webhook signature")
        except Exception as e:
            self.logger.error(f"Webhook processing failed: {e}")
            raise
    
    async def _handle_payment_succeeded(self, payment_intent):
        """Handle successful payment"""
        self.logger.info(f"Payment succeeded: {payment_intent['id']}")
        # Additional business logic here
    
    async def _handle_payment_failed(self, payment_intent):
        """Handle failed payment"""
        self.logger.warning(f"Payment failed: {payment_intent['id']}")
        self.stats["failed_payments"] += 1
        # Additional business logic here
    
    async def _handle_subscription_created(self, subscription):
        """Handle subscription creation"""
        self.logger.info(f"Subscription created: {subscription['id']}")
        # Additional business logic here
    
    async def _handle_subscription_canceled(self, subscription):
        """Handle subscription cancellation"""
        self.logger.info(f"Subscription canceled: {subscription['id']}")
        # Additional business logic here
    
    async def _handle_invoice_payment_succeeded(self, invoice):
        """Handle successful invoice payment"""
        self.logger.info(f"Invoice payment succeeded: {invoice['id']}")
        # Additional business logic here
    
    async def _handle_invoice_payment_failed(self, invoice):
        """Handle failed invoice payment"""
        self.logger.warning(f"Invoice payment failed: {invoice['id']}")
        # Additional business logic here
    
    async def get_payment_methods(self, customer_id: str) -> List[Dict[str, Any]]:
        """Get customer payment methods
        
        Args:
            customer_id: Customer ID
            
        Returns:
            List[Dict[str, Any]]: Payment methods
        """
        try:
            payment_methods = stripe.PaymentMethod.list(
                customer=customer_id,
                type="card"
            )
            
            return [
                {
                    "id": pm.id,
                    "type": pm.type,
                    "card": pm.card,
                    "created": pm.created
                }
                for pm in payment_methods.data
            ]
            
        except Exception as e:
            self.logger.error(f"Failed to get payment methods: {e}")
            raise
    
    async def get_usage_stats(self) -> Dict[str, Any]:
        """Get usage statistics
        
        Returns:
            Dict[str, Any]: Usage statistics
        """
        stats = self.stats.copy()
        stats["timestamp"] = datetime.utcnow().isoformat()
        
        # Calculate success rate
        total_payments = stats["payments_processed"] + stats["failed_payments"]
        if total_payments > 0:
            stats["success_rate"] = stats["payments_processed"] / total_payments
        else:
            stats["success_rate"] = 1.0
            
        return stats


# Integration factory function
def create_stripe_integration(publishable_key: str, secret_key: str, 
                            webhook_secret: str, environment: str = "sandbox",
                            rate_limiter=None, cache_manager=None) -> StripeIntegration:
    """Create Stripe integration instance
    
    Args:
        publishable_key: Stripe publishable key
        secret_key: Stripe secret key
        webhook_secret: Webhook secret
        environment: Environment (sandbox/production)
        rate_limiter: Rate limiter instance
        cache_manager: Cache manager instance
        
    Returns:
        StripeIntegration: Integration instance
    """
    config = StripeConfig(
        publishable_key=publishable_key,
        secret_key=secret_key,
        webhook_secret=webhook_secret,
        environment=environment
    )
    
    return StripeIntegration(config, rate_limiter, cache_manager)