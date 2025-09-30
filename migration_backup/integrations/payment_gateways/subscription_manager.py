"""
Subscription Manager for Ainflue Platform
Enterprise-grade subscription billing and management system

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import json
import hmac
import hashlib
import time
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Optional, Any, Union, Callable
from decimal import Decimal
import logging
from dataclasses import dataclass, field
from enum import Enum
import uuid
import calendar
from dateutil.relativedelta import relativedelta

import aiohttp
import structlog

from ..core.base_integration import BaseIntegration
from ..core.exceptions import (
    PaymentError, InvalidConfigurationError, 
    SecurityError, ValidationError, SubscriptionError
)
from ..core.security import SecurityManager
from ..core.monitoring import MetricsCollector
from ..core.cache import CacheManager

logger = structlog.get_logger(__name__)

class SubscriptionStatus(Enum):
    """Subscription status values"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    PENDING = "pending"
    CANCELLED = "cancelled"
    EXPIRED = "expired"
    PAST_DUE = "past_due"
    TRIALING = "trialing"
    PAUSED = "paused"
    INCOMPLETE = "incomplete"
    INCOMPLETE_EXPIRED = "incomplete_expired"

class BillingPeriod(Enum):
    """Billing period intervals"""
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    ANNUALLY = "annually"
    CUSTOM = "custom"

class ProrationMode(Enum):
    """Proration handling modes"""
    CREATE_PRORATIONS = "create_prorations"
    NONE = "none"
    ALWAYS_INVOICE = "always_invoice"

class PaymentBehavior(Enum):
    """Payment behavior for billing cycles"""
    ALLOW_INCOMPLETE = "allow_incomplete"
    DEFAULT_INCOMPLETE = "default_incomplete"
    ERROR_IF_INCOMPLETE = "error_if_incomplete"
    PENDING_IF_INCOMPLETE = "pending_if_incomplete"

class InvoiceStatus(Enum):
    """Invoice status values"""
    DRAFT = "draft"
    OPEN = "open"
    PAID = "paid"
    VOID = "void"
    UNCOLLECTIBLE = "uncollectible"

@dataclass
class SubscriptionPlan:
    """Subscription plan definition"""
    id: str
    name: str
    description: str
    amount: Decimal
    currency: str
    billing_period: BillingPeriod
    billing_interval: int = 1  # e.g., every 2 months
    trial_period_days: Optional[int] = None
    setup_fee: Optional[Decimal] = None
    features: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    active: bool = True
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)

@dataclass
class Subscription:
    """Subscription instance"""
    id: str
    customer_id: str
    plan_id: str
    status: SubscriptionStatus
    current_period_start: datetime
    current_period_end: datetime
    billing_cycle_anchor: Optional[datetime] = None
    trial_start: Optional[datetime] = None
    trial_end: Optional[datetime] = None
    cancel_at_period_end: bool = False
    cancelled_at: Optional[datetime] = None
    ended_at: Optional[datetime] = None
    latest_invoice_id: Optional[str] = None
    payment_method_id: Optional[str] = None
    quantity: int = 1
    tax_percent: Optional[Decimal] = None
    discount_id: Optional[str] = None
    collection_method: str = "charge_automatically"
    days_until_due: Optional[int] = None
    proration_behavior: ProrationMode = ProrationMode.CREATE_PRORATIONS
    payment_behavior: PaymentBehavior = PaymentBehavior.DEFAULT_INCOMPLETE
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)

@dataclass
class Invoice:
    """Subscription invoice"""
    id: str
    subscription_id: str
    customer_id: str
    status: InvoiceStatus
    amount_due: Decimal
    amount_paid: Decimal
    amount_remaining: Decimal
    currency: str
    description: Optional[str] = None
    invoice_pdf: Optional[str] = None
    hosted_invoice_url: Optional[str] = None
    invoice_number: Optional[str] = None
    period_start: Optional[datetime] = None
    period_end: Optional[datetime] = None
    subtotal: Optional[Decimal] = None
    tax: Optional[Decimal] = None
    total: Optional[Decimal] = None
    due_date: Optional[datetime] = None
    finalized_at: Optional[datetime] = None
    paid_at: Optional[datetime] = None
    voided_at: Optional[datetime] = None
    attempt_count: int = 0
    next_payment_attempt: Optional[datetime] = None
    line_items: List[Dict[str, Any]] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)

@dataclass
class PaymentAttempt:
    """Payment attempt for invoice"""
    id: str
    invoice_id: str
    amount: Decimal
    currency: str
    payment_method_id: str
    status: str
    failure_reason: Optional[str] = None
    gateway_transaction_id: Optional[str] = None
    gateway_response: Optional[Dict[str, Any]] = None
    attempted_at: datetime = field(default_factory=datetime.utcnow)

@dataclass
class Customer:
    """Customer information for subscriptions"""
    id: str
    email: Optional[str] = None
    name: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[Dict[str, str]] = None
    payment_methods: List[str] = field(default_factory=list)
    default_payment_method: Optional[str] = None
    tax_exempt: bool = False
    tax_ids: List[Dict[str, str]] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)

@dataclass
class SubscriptionConfig:
    """Subscription manager configuration"""
    # Payment gateway integration
    default_payment_gateway: str = "stripe"
    gateway_configs: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    
    # Billing settings
    default_currency: str = "USD"
    default_collection_method: str = "charge_automatically"
    default_payment_behavior: PaymentBehavior = PaymentBehavior.DEFAULT_INCOMPLETE
    
    # Trial settings
    default_trial_period_days: int = 14
    trial_requires_payment_method: bool = True
    
    # Invoice settings
    invoice_prefix: str = "INV"
    invoice_footer: Optional[str] = None
    auto_advance_invoices: bool = True
    days_until_due: int = 30
    
    # Retry settings
    max_payment_attempts: int = 3
    retry_schedule: List[int] = field(default_factory=lambda: [1, 3, 7])  # days
    
    # Webhooks
    webhook_endpoints: List[str] = field(default_factory=list)
    webhook_secret: Optional[str] = None
    
    # Features
    enable_proration: bool = True
    enable_usage_billing: bool = False
    enable_metered_billing: bool = False
    enable_tax_calculation: bool = False
    
    # Notifications
    send_invoice_emails: bool = True
    send_payment_failed_emails: bool = True
    send_subscription_updates: bool = True

class SubscriptionManager(BaseIntegration):
    """
    Enterprise Subscription Manager for Ainflue platform
    
    Features:
    - Complete subscription lifecycle management
    - Multi-gateway payment processing
    - Automatic billing and invoicing
    - Proration and plan changes
    - Trial period management
    - Dunning management and retry logic
    - Tax calculation and compliance
    - Usage-based and metered billing
    - Comprehensive analytics and reporting
    - Webhook event handling
    - Customer portal integration
    """

    def __init__(self, config: SubscriptionConfig):
        super().__init__("subscription_manager")
        self.config = config
        self.security_manager = SecurityManager()
        self.metrics = MetricsCollector()
        self.cache = CacheManager()
        
        # Storage
        self._plans: Dict[str, SubscriptionPlan] = {}
        self._subscriptions: Dict[str, Subscription] = {}
        self._customers: Dict[str, Customer] = {}
        self._invoices: Dict[str, Invoice] = {}
        self._payment_attempts: Dict[str, List[PaymentAttempt]] = {}
        
        # Event handlers
        self._event_handlers: Dict[str, List[Callable]] = {}
        
        # Billing scheduler
        self._scheduled_jobs: List[Dict[str, Any]] = []
        
        # Invoice counter
        self._invoice_counter = 1
        
        logger.info("Subscription manager initialized",
                   default_gateway=config.default_payment_gateway,
                   features={
                       "proration": config.enable_proration,
                       "usage_billing": config.enable_usage_billing,
                       "tax_calculation": config.enable_tax_calculation
                   })

    async def create_plan(self, plan_data: Dict[str, Any]) -> SubscriptionPlan:
        """
        Create a new subscription plan
        
        Args:
            plan_data: Plan information
            
        Returns:
            Created subscription plan
        """
        try:
            plan_id = plan_data.get("id") or str(uuid.uuid4())
            
            plan = SubscriptionPlan(
                id=plan_id,
                name=plan_data["name"],
                description=plan_data.get("description", ""),
                amount=Decimal(str(plan_data["amount"])),
                currency=plan_data.get("currency", self.config.default_currency),
                billing_period=BillingPeriod(plan_data["billing_period"]),
                billing_interval=plan_data.get("billing_interval", 1),
                trial_period_days=plan_data.get("trial_period_days"),
                setup_fee=Decimal(str(plan_data["setup_fee"])) if plan_data.get("setup_fee") else None,
                features=plan_data.get("features", []),
                metadata=plan_data.get("metadata", {})
            )
            
            # Store plan
            self._plans[plan_id] = plan
            
            # Cache plan
            await self.cache.set(
                f"subscription_plan:{plan_id}",
                plan,
                ttl=86400  # 24 hours
            )
            
            self.metrics.increment("subscriptions.plans.created")
            
            logger.info("Subscription plan created",
                       plan_id=plan_id,
                       name=plan.name,
                       amount=float(plan.amount),
                       billing_period=plan.billing_period.value)
            
            return plan
            
        except Exception as e:
            self.metrics.increment("subscriptions.plans.creation_failed")
            logger.error("Failed to create subscription plan", error=str(e))
            raise ValidationError(f"Plan creation failed: {e}")

    async def create_customer(self, customer_data: Dict[str, Any]) -> Customer:
        """
        Create a new customer
        
        Args:
            customer_data: Customer information
            
        Returns:
            Created customer
        """
        try:
            customer_id = customer_data.get("id") or str(uuid.uuid4())
            
            customer = Customer(
                id=customer_id,
                email=customer_data.get("email"),
                name=customer_data.get("name"),
                phone=customer_data.get("phone"),
                address=customer_data.get("address"),
                payment_methods=customer_data.get("payment_methods", []),
                default_payment_method=customer_data.get("default_payment_method"),
                tax_exempt=customer_data.get("tax_exempt", False),
                tax_ids=customer_data.get("tax_ids", []),
                metadata=customer_data.get("metadata", {})
            )
            
            # Store customer
            self._customers[customer_id] = customer
            
            # Cache customer
            await self.cache.set(
                f"subscription_customer:{customer_id}",
                customer,
                ttl=3600  # 1 hour
            )
            
            self.metrics.increment("subscriptions.customers.created")
            
            logger.info("Customer created",
                       customer_id=customer_id,
                       email=customer.email)
            
            return customer
            
        except Exception as e:
            self.metrics.increment("subscriptions.customers.creation_failed")
            logger.error("Failed to create customer", error=str(e))
            raise ValidationError(f"Customer creation failed: {e}")

    async def create_subscription(self, subscription_data: Dict[str, Any]) -> Subscription:
        """
        Create a new subscription
        
        Args:
            subscription_data: Subscription information
            
        Returns:
            Created subscription
        """
        try:
            # Validate plan exists
            plan_id = subscription_data["plan_id"]
            plan = self._plans.get(plan_id)
            if not plan:
                raise ValidationError(f"Plan {plan_id} not found")
            
            # Validate customer exists
            customer_id = subscription_data["customer_id"]
            customer = self._customers.get(customer_id)
            if not customer:
                raise ValidationError(f"Customer {customer_id} not found")
            
            subscription_id = subscription_data.get("id") or str(uuid.uuid4())
            
            # Calculate billing periods
            current_period_start = datetime.utcnow()
            
            # Handle trial period
            trial_start = None
            trial_end = None
            if plan.trial_period_days and plan.trial_period_days > 0:
                trial_start = current_period_start
                trial_end = current_period_start + timedelta(days=plan.trial_period_days)
                current_period_end = trial_end
                status = SubscriptionStatus.TRIALING
            else:
                current_period_end = self._calculate_next_billing_date(
                    current_period_start, plan.billing_period, plan.billing_interval
                )
                status = SubscriptionStatus.ACTIVE
            
            subscription = Subscription(
                id=subscription_id,
                customer_id=customer_id,
                plan_id=plan_id,
                status=status,
                current_period_start=current_period_start,
                current_period_end=current_period_end,
                trial_start=trial_start,
                trial_end=trial_end,
                payment_method_id=subscription_data.get("payment_method_id"),
                quantity=subscription_data.get("quantity", 1),
                tax_percent=Decimal(str(subscription_data["tax_percent"])) if subscription_data.get("tax_percent") else None,
                collection_method=subscription_data.get("collection_method", self.config.default_collection_method),
                payment_behavior=PaymentBehavior(subscription_data.get("payment_behavior", self.config.default_payment_behavior.value)),
                metadata=subscription_data.get("metadata", {})
            )
            
            # Store subscription
            self._subscriptions[subscription_id] = subscription
            
            # Cache subscription
            await self.cache.set(
                f"subscription:{subscription_id}",
                subscription,
                ttl=3600  # 1 hour
            )
            
            # Create initial invoice if not in trial
            if status == SubscriptionStatus.ACTIVE:
                initial_invoice = await self._create_subscription_invoice(subscription, plan)
                subscription.latest_invoice_id = initial_invoice.id
            
            # Schedule next billing
            await self._schedule_next_billing(subscription)
            
            # Emit event
            await self._emit_event("subscription.created", {
                "subscription": subscription,
                "plan": plan,
                "customer": customer
            })
            
            self.metrics.increment("subscriptions.created")
            
            logger.info("Subscription created",
                       subscription_id=subscription_id,
                       customer_id=customer_id,
                       plan_id=plan_id,
                       status=status.value)
            
            return subscription
            
        except Exception as e:
            self.metrics.increment("subscriptions.creation_failed")
            logger.error("Failed to create subscription", error=str(e))
            raise SubscriptionError(f"Subscription creation failed: {e}")

    def _calculate_next_billing_date(self, 
                                   start_date: datetime, 
                                   billing_period: BillingPeriod, 
                                   interval: int) -> datetime:
        """Calculate next billing date based on period and interval"""
        try:
            if billing_period == BillingPeriod.DAILY:
                return start_date + timedelta(days=interval)
            elif billing_period == BillingPeriod.WEEKLY:
                return start_date + timedelta(weeks=interval)
            elif billing_period == BillingPeriod.MONTHLY:
                return start_date + relativedelta(months=interval)
            elif billing_period == BillingPeriod.QUARTERLY:
                return start_date + relativedelta(months=3 * interval)
            elif billing_period == BillingPeriod.ANNUALLY:
                return start_date + relativedelta(years=interval)
            else:
                # Default to monthly
                return start_date + relativedelta(months=interval)
                
        except Exception as e:
            logger.error("Failed to calculate next billing date", error=str(e))
            return start_date + relativedelta(months=1)  # Fallback

    async def _create_subscription_invoice(self, 
                                         subscription: Subscription, 
                                         plan: SubscriptionPlan) -> Invoice:
        """Create invoice for subscription billing period"""
        try:
            invoice_id = str(uuid.uuid4())
            
            # Calculate amounts
            subtotal = plan.amount * subscription.quantity
            tax_amount = Decimal("0")
            
            if subscription.tax_percent:
                tax_amount = subtotal * (subscription.tax_percent / 100)
            
            total = subtotal + tax_amount
            
            # Add setup fee if applicable
            if plan.setup_fee and subscription.status != SubscriptionStatus.TRIALING:
                subtotal += plan.setup_fee
                if subscription.tax_percent:
                    tax_amount += plan.setup_fee * (subscription.tax_percent / 100)
                total = subtotal + tax_amount
            
            # Generate invoice number
            invoice_number = f"{self.config.invoice_prefix}-{self._invoice_counter:06d}"
            self._invoice_counter += 1
            
            invoice = Invoice(
                id=invoice_id,
                subscription_id=subscription.id,
                customer_id=subscription.customer_id,
                status=InvoiceStatus.OPEN,
                amount_due=total,
                amount_paid=Decimal("0"),
                amount_remaining=total,
                currency=plan.currency,
                description=f"Subscription to {plan.name}",
                invoice_number=invoice_number,
                period_start=subscription.current_period_start,
                period_end=subscription.current_period_end,
                subtotal=subtotal,
                tax=tax_amount,
                total=total,
                due_date=datetime.utcnow() + timedelta(days=self.config.days_until_due),
                line_items=[
                    {
                        "type": "subscription",
                        "plan_id": plan.id,
                        "description": plan.name,
                        "quantity": subscription.quantity,
                        "amount": float(plan.amount),
                        "currency": plan.currency,
                        "period_start": subscription.current_period_start.isoformat(),
                        "period_end": subscription.current_period_end.isoformat()
                    }
                ]
            )
            
            # Store invoice
            self._invoices[invoice_id] = invoice
            
            # Cache invoice
            await self.cache.set(
                f"subscription_invoice:{invoice_id}",
                invoice,
                ttl=86400  # 24 hours
            )
            
            self.metrics.increment("subscriptions.invoices.created")
            
            logger.info("Subscription invoice created",
                       invoice_id=invoice_id,
                       subscription_id=subscription.id,
                       amount=float(total))
            
            return invoice
            
        except Exception as e:
            logger.error("Failed to create subscription invoice", error=str(e))
            raise SubscriptionError(f"Invoice creation failed: {e}")

    async def _schedule_next_billing(self, subscription: Subscription):
        """Schedule next billing for subscription"""
        try:
            if subscription.status not in [SubscriptionStatus.ACTIVE, SubscriptionStatus.TRIALING]:
                return
            
            next_billing_date = subscription.current_period_end
            
            # Add to scheduled jobs
            job = {
                "id": str(uuid.uuid4()),
                "type": "billing",
                "subscription_id": subscription.id,
                "scheduled_for": next_billing_date,
                "created_at": datetime.utcnow()
            }
            
            self._scheduled_jobs.append(job)
            
            logger.info("Next billing scheduled",
                       subscription_id=subscription.id,
                       next_billing_date=next_billing_date.isoformat())
            
        except Exception as e:
            logger.error("Failed to schedule next billing", error=str(e))

    async def process_scheduled_billing(self):
        """Process all scheduled billing jobs"""
        try:
            current_time = datetime.utcnow()
            processed_jobs = []
            
            for job in self._scheduled_jobs:
                if (job["type"] == "billing" and 
                    job["scheduled_for"] <= current_time):
                    
                    subscription_id = job["subscription_id"]
                    subscription = self._subscriptions.get(subscription_id)
                    
                    if subscription and subscription.status in [SubscriptionStatus.ACTIVE, SubscriptionStatus.TRIALING]:
                        await self._process_subscription_billing(subscription)
                    
                    processed_jobs.append(job)
            
            # Remove processed jobs
            for job in processed_jobs:
                self._scheduled_jobs.remove(job)
            
            if processed_jobs:
                self.metrics.increment("subscriptions.billing.processed", len(processed_jobs))
                logger.info("Processed scheduled billing jobs", count=len(processed_jobs))
            
        except Exception as e:
            logger.error("Failed to process scheduled billing", error=str(e))

    async def _process_subscription_billing(self, subscription: Subscription):
        """Process billing for a specific subscription"""
        try:
            plan = self._plans.get(subscription.plan_id)
            if not plan:
                logger.error("Plan not found for subscription", subscription_id=subscription.id)
                return
            
            # Handle trial expiration
            if (subscription.status == SubscriptionStatus.TRIALING and 
                subscription.trial_end and 
                datetime.utcnow() >= subscription.trial_end):
                
                subscription.status = SubscriptionStatus.ACTIVE
                
                # Emit trial ended event
                await self._emit_event("subscription.trial_ended", {
                    "subscription": subscription
                })
            
            # Create invoice for new period
            # Update subscription period
            subscription.current_period_start = subscription.current_period_end
            subscription.current_period_end = self._calculate_next_billing_date(
                subscription.current_period_start,
                plan.billing_period,
                plan.billing_interval
            )
            subscription.updated_at = datetime.utcnow()
            
            # Create new invoice
            invoice = await self._create_subscription_invoice(subscription, plan)
            subscription.latest_invoice_id = invoice.id
            
            # Attempt payment
            if subscription.payment_method_id:
                payment_success = await self._attempt_payment(invoice, subscription.payment_method_id)
                
                if payment_success:
                    invoice.status = InvoiceStatus.PAID
                    invoice.paid_at = datetime.utcnow()
                    invoice.amount_paid = invoice.total
                    invoice.amount_remaining = Decimal("0")
                else:
                    subscription.status = SubscriptionStatus.PAST_DUE
                    # Schedule retry
                    await self._schedule_payment_retry(invoice)
            
            # Schedule next billing
            await self._schedule_next_billing(subscription)
            
            # Update cache
            await self.cache.set(f"subscription:{subscription.id}", subscription, ttl=3600)
            await self.cache.set(f"subscription_invoice:{invoice.id}", invoice, ttl=86400)
            
            # Emit billing event
            await self._emit_event("subscription.billing_processed", {
                "subscription": subscription,
                "invoice": invoice
            })
            
            logger.info("Subscription billing processed",
                       subscription_id=subscription.id,
                       invoice_id=invoice.id,
                       amount=float(invoice.total))
            
        except Exception as e:
            logger.error("Failed to process subscription billing",
                        subscription_id=subscription.id,
                        error=str(e))

    async def _attempt_payment(self, invoice: Invoice, payment_method_id: str) -> bool:
        """Attempt payment for invoice"""
        try:
            attempt_id = str(uuid.uuid4())
            
            # Create payment attempt record
            attempt = PaymentAttempt(
                id=attempt_id,
                invoice_id=invoice.id,
                amount=invoice.amount_due,
                currency=invoice.currency,
                payment_method_id=payment_method_id,
                status="pending"
            )
            
            if invoice.id not in self._payment_attempts:
                self._payment_attempts[invoice.id] = []
            self._payment_attempts[invoice.id].append(attempt)
            
            # Simulate payment processing (integrate with actual payment gateway)
            # In production, this would call the configured payment gateway
            await asyncio.sleep(0.1)  # Simulate network delay
            
            # For demo, assume 90% success rate
            import random
            payment_success = random.random() > 0.1
            
            if payment_success:
                attempt.status = "succeeded"
                attempt.gateway_transaction_id = f"txn_{uuid.uuid4().hex[:16]}"
                
                self.metrics.increment("subscriptions.payments.succeeded")
                
                logger.info("Payment succeeded",
                           invoice_id=invoice.id,
                           attempt_id=attempt_id,
                           amount=float(invoice.amount_due))
                
                return True
            else:
                attempt.status = "failed"
                attempt.failure_reason = "card_declined"
                
                invoice.attempt_count += 1
                
                self.metrics.increment("subscriptions.payments.failed")
                
                logger.warning("Payment failed",
                             invoice_id=invoice.id,
                             attempt_id=attempt_id,
                             reason=attempt.failure_reason)
                
                return False
            
        except Exception as e:
            logger.error("Payment attempt failed",
                        invoice_id=invoice.id,
                        error=str(e))
            return False

    async def _schedule_payment_retry(self, invoice: Invoice):
        """Schedule payment retry for failed invoice"""
        try:
            if invoice.attempt_count >= self.config.max_payment_attempts:
                logger.info("Max payment attempts reached",
                           invoice_id=invoice.id,
                           attempts=invoice.attempt_count)
                return
            
            # Get retry delay
            retry_index = min(invoice.attempt_count - 1, len(self.config.retry_schedule) - 1)
            retry_days = self.config.retry_schedule[retry_index]
            
            next_attempt = datetime.utcnow() + timedelta(days=retry_days)
            invoice.next_payment_attempt = next_attempt
            
            # Schedule retry job
            job = {
                "id": str(uuid.uuid4()),
                "type": "payment_retry",
                "invoice_id": invoice.id,
                "scheduled_for": next_attempt,
                "created_at": datetime.utcnow()
            }
            
            self._scheduled_jobs.append(job)
            
            logger.info("Payment retry scheduled",
                       invoice_id=invoice.id,
                       retry_date=next_attempt.isoformat(),
                       attempt_number=invoice.attempt_count + 1)
            
        except Exception as e:
            logger.error("Failed to schedule payment retry", error=str(e))

    async def cancel_subscription(self, 
                                subscription_id: str, 
                                at_period_end: bool = True,
                                cancellation_reason: Optional[str] = None) -> Subscription:
        """
        Cancel a subscription
        
        Args:
            subscription_id: Subscription ID to cancel
            at_period_end: Whether to cancel at period end or immediately
            cancellation_reason: Reason for cancellation
            
        Returns:
            Updated subscription
        """
        try:
            subscription = self._subscriptions.get(subscription_id)
            if not subscription:
                raise ValidationError(f"Subscription {subscription_id} not found")
            
            if at_period_end:
                subscription.cancel_at_period_end = True
                subscription.cancelled_at = datetime.utcnow()
                
                # Emit event
                await self._emit_event("subscription.cancelled", {
                    "subscription": subscription,
                    "cancellation_reason": cancellation_reason,
                    "at_period_end": True
                })
                
                logger.info("Subscription scheduled for cancellation",
                           subscription_id=subscription_id,
                           end_date=subscription.current_period_end.isoformat())
            else:
                subscription.status = SubscriptionStatus.CANCELLED
                subscription.cancelled_at = datetime.utcnow()
                subscription.ended_at = datetime.utcnow()
                
                # Emit event
                await self._emit_event("subscription.cancelled", {
                    "subscription": subscription,
                    "cancellation_reason": cancellation_reason,
                    "at_period_end": False
                })
                
                logger.info("Subscription cancelled immediately",
                           subscription_id=subscription_id)
            
            subscription.updated_at = datetime.utcnow()
            
            # Update cache
            await self.cache.set(f"subscription:{subscription_id}", subscription, ttl=3600)
            
            self.metrics.increment("subscriptions.cancelled")
            
            return subscription
            
        except Exception as e:
            self.metrics.increment("subscriptions.cancellation_failed")
            logger.error("Failed to cancel subscription",
                        subscription_id=subscription_id,
                        error=str(e))
            raise SubscriptionError(f"Subscription cancellation failed: {e}")

    async def update_subscription(self, 
                                subscription_id: str, 
                                updates: Dict[str, Any]) -> Subscription:
        """
        Update a subscription
        
        Args:
            subscription_id: Subscription ID to update
            updates: Fields to update
            
        Returns:
            Updated subscription
        """
        try:
            subscription = self._subscriptions.get(subscription_id)
            if not subscription:
                raise ValidationError(f"Subscription {subscription_id} not found")
            
            old_plan_id = subscription.plan_id
            
            # Apply updates
            for field, value in updates.items():
                if hasattr(subscription, field):
                    if field == "plan_id":
                        # Handle plan change with proration
                        await self._handle_plan_change(subscription, value)
                    else:
                        setattr(subscription, field, value)
            
            subscription.updated_at = datetime.utcnow()
            
            # Update cache
            await self.cache.set(f"subscription:{subscription_id}", subscription, ttl=3600)
            
            # Emit event
            await self._emit_event("subscription.updated", {
                "subscription": subscription,
                "updates": updates,
                "plan_changed": old_plan_id != subscription.plan_id
            })
            
            self.metrics.increment("subscriptions.updated")
            
            logger.info("Subscription updated",
                       subscription_id=subscription_id,
                       updates=list(updates.keys()))
            
            return subscription
            
        except Exception as e:
            self.metrics.increment("subscriptions.update_failed")
            logger.error("Failed to update subscription",
                        subscription_id=subscription_id,
                        error=str(e))
            raise SubscriptionError(f"Subscription update failed: {e}")

    async def _handle_plan_change(self, subscription: Subscription, new_plan_id: str):
        """Handle subscription plan change with proration"""
        try:
            if not self.config.enable_proration:
                subscription.plan_id = new_plan_id
                return
            
            old_plan = self._plans.get(subscription.plan_id)
            new_plan = self._plans.get(new_plan_id)
            
            if not old_plan or not new_plan:
                raise ValidationError("Plan not found")
            
            # Calculate proration
            current_time = datetime.utcnow()
            period_elapsed = (current_time - subscription.current_period_start).total_seconds()
            period_total = (subscription.current_period_end - subscription.current_period_start).total_seconds()
            period_remaining = max(0, (subscription.current_period_end - current_time).total_seconds())
            
            # Calculate prorated amounts
            old_amount_unused = old_plan.amount * Decimal(str(period_remaining / period_total))
            new_amount_prorated = new_plan.amount * Decimal(str(period_remaining / period_total))
            
            proration_amount = new_amount_prorated - old_amount_unused
            
            # Create proration invoice if there's a difference
            if proration_amount != 0:
                await self._create_proration_invoice(subscription, proration_amount, old_plan, new_plan)
            
            # Update subscription
            subscription.plan_id = new_plan_id
            
            logger.info("Plan change processed with proration",
                       subscription_id=subscription.id,
                       old_plan=old_plan.id,
                       new_plan=new_plan.id,
                       proration_amount=float(proration_amount))
            
        except Exception as e:
            logger.error("Failed to handle plan change", error=str(e))
            raise SubscriptionError(f"Plan change failed: {e}")

    async def _create_proration_invoice(self, 
                                      subscription: Subscription, 
                                      amount: Decimal, 
                                      old_plan: SubscriptionPlan, 
                                      new_plan: SubscriptionPlan):
        """Create proration invoice for plan change"""
        try:
            invoice_id = str(uuid.uuid4())
            
            invoice = Invoice(
                id=invoice_id,
                subscription_id=subscription.id,
                customer_id=subscription.customer_id,
                status=InvoiceStatus.OPEN,
                amount_due=amount,
                amount_paid=Decimal("0"),
                amount_remaining=amount,
                currency=new_plan.currency,
                description=f"Proration for plan change from {old_plan.name} to {new_plan.name}",
                subtotal=amount,
                total=amount,
                due_date=datetime.utcnow(),  # Due immediately
                line_items=[
                    {
                        "type": "proration",
                        "description": f"Plan change: {old_plan.name} → {new_plan.name}",
                        "amount": float(amount),
                        "currency": new_plan.currency
                    }
                ]
            )
            
            # Store invoice
            self._invoices[invoice_id] = invoice
            
            # Attempt immediate payment if positive amount
            if amount > 0 and subscription.payment_method_id:
                await self._attempt_payment(invoice, subscription.payment_method_id)
            
            logger.info("Proration invoice created",
                       invoice_id=invoice_id,
                       subscription_id=subscription.id,
                       amount=float(amount))
            
        except Exception as e:
            logger.error("Failed to create proration invoice", error=str(e))

    async def get_subscription_analytics(self, 
                                       start_date: Optional[datetime] = None,
                                       end_date: Optional[datetime] = None) -> Dict[str, Any]:
        """
        Get subscription analytics
        
        Args:
            start_date: Start date for analytics
            end_date: End date for analytics
            
        Returns:
            Analytics data
        """
        try:
            if not start_date:
                start_date = datetime.utcnow() - timedelta(days=30)
            if not end_date:
                end_date = datetime.utcnow()
            
            # Calculate metrics
            total_subscriptions = len(self._subscriptions)
            active_subscriptions = len([
                s for s in self._subscriptions.values() 
                if s.status == SubscriptionStatus.ACTIVE
            ])
            trialing_subscriptions = len([
                s for s in self._subscriptions.values() 
                if s.status == SubscriptionStatus.TRIALING
            ])
            cancelled_subscriptions = len([
                s for s in self._subscriptions.values() 
                if s.status == SubscriptionStatus.CANCELLED
            ])
            
            # Calculate MRR (Monthly Recurring Revenue)
            mrr = Decimal("0")
            for subscription in self._subscriptions.values():
                if subscription.status in [SubscriptionStatus.ACTIVE, SubscriptionStatus.TRIALING]:
                    plan = self._plans.get(subscription.plan_id)
                    if plan:
                        # Normalize to monthly amount
                        monthly_amount = self._normalize_to_monthly(plan.amount, plan.billing_period, plan.billing_interval)
                        mrr += monthly_amount * subscription.quantity
            
            # Calculate churn rate
            period_cancelled = len([
                s for s in self._subscriptions.values()
                if (s.cancelled_at and 
                    start_date <= s.cancelled_at <= end_date)
            ])
            
            period_start_active = len([
                s for s in self._subscriptions.values()
                if (s.created_at < start_date and
                    s.status != SubscriptionStatus.CANCELLED)
            ])
            
            churn_rate = (period_cancelled / max(period_start_active, 1)) * 100
            
            analytics = {
                "period": {
                    "start_date": start_date.isoformat(),
                    "end_date": end_date.isoformat()
                },
                "subscriptions": {
                    "total": total_subscriptions,
                    "active": active_subscriptions,
                    "trialing": trialing_subscriptions,
                    "cancelled": cancelled_subscriptions
                },
                "revenue": {
                    "mrr": float(mrr),
                    "currency": self.config.default_currency
                },
                "metrics": {
                    "churn_rate_percent": float(churn_rate),
                    "active_rate_percent": (active_subscriptions / max(total_subscriptions, 1)) * 100
                },
                "plans": {
                    plan_id: len([
                        s for s in self._subscriptions.values()
                        if s.plan_id == plan_id and s.status == SubscriptionStatus.ACTIVE
                    ])
                    for plan_id in self._plans.keys()
                }
            }
            
            self.metrics.increment("subscriptions.analytics.generated")
            
            return analytics
            
        except Exception as e:
            self.metrics.increment("subscriptions.analytics.failed")
            logger.error("Failed to generate subscription analytics", error=str(e))
            return {}

    def _normalize_to_monthly(self, amount: Decimal, period: BillingPeriod, interval: int) -> Decimal:
        """Normalize billing amount to monthly equivalent"""
        if period == BillingPeriod.DAILY:
            return amount * 30 / interval
        elif period == BillingPeriod.WEEKLY:
            return amount * 4.33 / interval  # 4.33 weeks per month
        elif period == BillingPeriod.MONTHLY:
            return amount / interval
        elif period == BillingPeriod.QUARTERLY:
            return amount / (3 * interval)
        elif period == BillingPeriod.ANNUALLY:
            return amount / (12 * interval)
        else:
            return amount  # Default to monthly

    async def _emit_event(self, event_type: str, data: Dict[str, Any]):
        """Emit subscription event"""
        try:
            event = {
                "id": str(uuid.uuid4()),
                "type": event_type,
                "data": data,
                "timestamp": datetime.utcnow().isoformat()
            }
            
            # Call registered handlers
            handlers = self._event_handlers.get(event_type, [])
            for handler in handlers:
                try:
                    await handler(event)
                except Exception as e:
                    logger.error("Event handler failed",
                               event_type=event_type,
                               error=str(e))
            
            # Send webhooks
            await self._send_webhooks(event)
            
            self.metrics.increment(f"subscriptions.events.{event_type}")
            
        except Exception as e:
            logger.error("Failed to emit event", error=str(e))

    async def _send_webhooks(self, event: Dict[str, Any]):
        """Send event webhooks to configured endpoints"""
        try:
            if not self.config.webhook_endpoints:
                return
            
            webhook_payload = json.dumps(event)
            
            # Create signature if secret is configured
            signature = None
            if self.config.webhook_secret:
                signature = hmac.new(
                    self.config.webhook_secret.encode(),
                    webhook_payload.encode(),
                    hashlib.sha256
                ).hexdigest()
            
            # Send to all endpoints
            for endpoint in self.config.webhook_endpoints:
                try:
                    headers = {
                        "Content-Type": "application/json",
                        "User-Agent": "Ainflue-Subscriptions/1.0"
                    }
                    
                    if signature:
                        headers["X-Ainflue-Signature"] = f"sha256={signature}"
                    
                    async with aiohttp.ClientSession() as session:
                        async with session.post(
                            endpoint,
                            data=webhook_payload,
                            headers=headers,
                            timeout=aiohttp.ClientTimeout(total=10)
                        ) as response:
                            
                            if response.status == 200:
                                self.metrics.increment("subscriptions.webhooks.sent")
                            else:
                                self.metrics.increment("subscriptions.webhooks.failed")
                                logger.warning("Webhook delivery failed",
                                             endpoint=endpoint,
                                             status=response.status)
                
                except Exception as e:
                    self.metrics.increment("subscriptions.webhooks.failed")
                    logger.error("Webhook send failed",
                               endpoint=endpoint,
                               error=str(e))
            
        except Exception as e:
            logger.error("Failed to send webhooks", error=str(e))

    def register_event_handler(self, event_type: str, handler: Callable):
        """Register event handler for subscription events"""
        if event_type not in self._event_handlers:
            self._event_handlers[event_type] = []
        
        self._event_handlers[event_type].append(handler)
        
        logger.info("Event handler registered",
                   event_type=event_type,
                   handler_count=len(self._event_handlers[event_type]))

    async def health_check(self) -> Dict[str, Any]:
        """
        Check subscription manager health
        
        Returns:
            Health status information
        """
        try:
            health_status = {
                "service": "subscription_manager",
                "status": "healthy",
                "timestamp": datetime.utcnow().isoformat(),
                "version": "1.0.0",
                "config": {
                    "default_gateway": self.config.default_payment_gateway,
                    "features": {
                        "proration": self.config.enable_proration,
                        "usage_billing": self.config.enable_usage_billing,
                        "tax_calculation": self.config.enable_tax_calculation
                    }
                },
                "metrics": {
                    "total_plans": len(self._plans),
                    "total_subscriptions": len(self._subscriptions),
                    "total_customers": len(self._customers),
                    "total_invoices": len(self._invoices),
                    "scheduled_jobs": len(self._scheduled_jobs)
                }
            }
            
            return health_status
            
        except Exception as e:
            return {
                "service": "subscription_manager",
                "status": "unhealthy",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }

# Factory function for easy setup
def create_subscription_manager(**kwargs) -> SubscriptionManager:
    """
    Factory function to create subscription manager
    
    Args:
        **kwargs: Configuration options
        
    Returns:
        Configured subscription manager instance
    """
    config = SubscriptionConfig(**kwargs)
    return SubscriptionManager(config)

# Example usage for Ainflue platform
async def example_subscription_flow():
    """Example subscription management usage"""
    
    # Initialize subscription manager
    sub_manager = create_subscription_manager(
        default_payment_gateway="stripe",
        default_currency="USD",
        enable_proration=True,
        default_trial_period_days=14,
        webhook_endpoints=["https://ainflue.com/webhooks/subscriptions"]
    )
    
    try:
        # Create subscription plans
        basic_plan = await sub_manager.create_plan({
            "name": "Ainflue Basic",
            "description": "Basic creator tools and analytics",
            "amount": "9.99",
            "currency": "USD",
            "billing_period": "monthly",
            "trial_period_days": 14,
            "features": ["basic_analytics", "content_upload", "basic_protection"]
        })
        
        premium_plan = await sub_manager.create_plan({
            "name": "Ainflue Premium",
            "description": "Advanced creator tools and AI features",
            "amount": "29.99",
            "currency": "USD",
            "billing_period": "monthly",
            "trial_period_days": 7,
            "features": ["advanced_analytics", "ai_content_generation", "advanced_protection", "collaboration_tools"]
        })
        
        print(f"Created plans: {basic_plan.name}, {premium_plan.name}")
        
        # Create customer
        customer = await sub_manager.create_customer({
            "email": "creator@ainflue.com",
            "name": "Alice Creator",
            "payment_methods": ["pm_123456789"],
            "default_payment_method": "pm_123456789"
        })
        
        print(f"Created customer: {customer.email}")
        
        # Create subscription
        subscription = await sub_manager.create_subscription({
            "customer_id": customer.id,
            "plan_id": basic_plan.id,
            "payment_method_id": "pm_123456789",
            "metadata": {
                "platform": "ainflue",
                "signup_source": "web"
            }
        })
        
        print(f"Created subscription: {subscription.id}, status: {subscription.status.value}")
        
        # Simulate plan upgrade
        await asyncio.sleep(1)  # Wait a moment
        
        updated_subscription = await sub_manager.update_subscription(
            subscription.id,
            {"plan_id": premium_plan.id}
        )
        
        print(f"Upgraded to premium plan: {updated_subscription.plan_id}")
        
        # Get analytics
        analytics = await sub_manager.get_subscription_analytics()
        print(f"Analytics - Total subscriptions: {analytics['subscriptions']['total']}")
        print(f"MRR: ${analytics['revenue']['mrr']:.2f}")
        
        # Health check
        health = await sub_manager.health_check()
        print(f"Subscription manager health: {health['status']}")
        
    except Exception as e:
        print(f"Subscription management error: {e}")

if __name__ == "__main__":
    asyncio.run(example_subscription_flow())