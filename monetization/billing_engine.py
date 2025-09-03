"""Automated Billing Engine
Comprehensive subscription and billing management system for automated recurring payments,
invoice generation, and billing lifecycle management.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import logging
import uuid
from datetime import datetime, timedelta
from decimal import Decimal, ROUND_HALF_UP
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import json

logger = logging.getLogger(__name__)


class BillingCycle(Enum):
    """Billing cycle types"""
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    YEARLY = "yearly"
    USAGE_BASED = "usage_based"
    ONE_TIME = "one_time"


class SubscriptionStatus(Enum):
    """Subscription status types"""
    ACTIVE = "active"
    TRIALING = "trialing"
    PAST_DUE = "past_due"
    CANCELED = "canceled"
    INCOMPLETE = "incomplete"
    INCOMPLETE_EXPIRED = "incomplete_expired"
    UNPAID = "unpaid"


class InvoiceStatus(Enum):
    """Invoice status types"""
    DRAFT = "draft"
    OPEN = "open"
    PAID = "paid"
    UNCOLLECTIBLE = "uncollectible"
    VOID = "void"


class PlanTier(Enum):
    """Subscription plan tiers"""
    FREE = "free"
    CREATOR = "creator"
    PRO = "pro"
    ENTERPRISE = "enterprise"


@dataclass
class BillingPlan:
    """Billing plan configuration"""
    id: str
    name: str
    tier: PlanTier
    price: Decimal
    currency: str
    billing_cycle: BillingCycle
    trial_period_days: int = 0
    features: Dict[str, Any] = None
    usage_limits: Dict[str, int] = None
    is_active: bool = True
    metadata: Dict[str, Any] = None
    created_at: datetime = None
    updated_at: datetime = None


@dataclass
class Subscription:
    """Subscription data structure"""
    id: str
    customer_id: str
    plan_id: str
    status: SubscriptionStatus
    current_period_start: datetime
    current_period_end: datetime
    trial_start: Optional[datetime] = None
    trial_end: Optional[datetime] = None
    cancel_at_period_end: bool = False
    canceled_at: Optional[datetime] = None
    created_at: datetime = None
    metadata: Dict[str, Any] = None
    payment_method_id: Optional[str] = None
    latest_invoice_id: Optional[str] = None
    discount_id: Optional[str] = None


@dataclass
class Invoice:
    """Invoice data structure"""
    id: str
    customer_id: str
    subscription_id: Optional[str]
    status: InvoiceStatus
    amount_due: Decimal
    amount_paid: Decimal
    amount_remaining: Decimal
    currency: str
    due_date: datetime
    period_start: datetime
    period_end: datetime
    tax_amount: Decimal = Decimal('0')
    discount_amount: Decimal = Decimal('0')
    subtotal: Decimal = Decimal('0')
    created_at: datetime = None
    paid_at: Optional[datetime] = None
    line_items: List[Dict] = None
    metadata: Dict[str, Any] = None


@dataclass
class UsageRecord:
    """Usage tracking for usage-based billing"""
    id: str
    subscription_id: str
    quantity: int
    timestamp: datetime
    action: str  # API call, storage, processing, etc.
    metadata: Dict[str, Any] = None


class BillingEngine:
    """Comprehensive automated billing engine"""
    
    # Default pricing plans
    DEFAULT_PLANS = {
        PlanTier.FREE: {
            "name": "Free",
            "price": Decimal('0'),
            "currency": "EUR",
            "billing_cycle": BillingCycle.MONTHLY,
            "trial_period_days": 0,
            "features": {
                "uploads_per_month": 10,
                "fingerprinting_scans": 5,
                "collaboration_projects": 2,
                "analytics_retention_days": 30,
                "storage_gb": 1,
                "support_level": "community"
            }
        },
        PlanTier.CREATOR: {
            "name": "Creator",
            "price": Decimal('29'),
            "currency": "EUR",
            "billing_cycle": BillingCycle.MONTHLY,
            "trial_period_days": 14,
            "features": {
                "uploads_per_month": 100,
                "fingerprinting_scans": 50,
                "collaboration_projects": 10,
                "analytics_retention_days": 365,
                "storage_gb": 50,
                "support_level": "email",
                "ai_features": "basic"
            }
        },
        PlanTier.PRO: {
            "name": "Pro",
            "price": Decimal('99'),
            "currency": "EUR",
            "billing_cycle": BillingCycle.MONTHLY,
            "trial_period_days": 14,
            "features": {
                "uploads_per_month": 500,
                "fingerprinting_scans": 200,
                "collaboration_projects": 50,
                "analytics_retention_days": 1825,
                "storage_gb": 200,
                "support_level": "priority",
                "ai_features": "advanced",
                "white_label": True,
                "api_access": "limited"
            }
        },
        PlanTier.ENTERPRISE: {
            "name": "Enterprise",
            "price": Decimal('0'),  # Custom pricing
            "currency": "EUR",
            "billing_cycle": BillingCycle.YEARLY,
            "trial_period_days": 30,
            "features": {
                "uploads_per_month": -1,  # Unlimited
                "fingerprinting_scans": -1,
                "collaboration_projects": -1,
                "analytics_retention_days": -1,
                "storage_gb": -1,
                "support_level": "dedicated",
                "ai_features": "full",
                "white_label": True,
                "api_access": "full",
                "on_premise": True,
                "sla": "99.99%"
            }
        }
    }
    
    def __init__(self):
        self.plans = {}
        self.subscriptions = {}
        self.invoices = {}
        self.usage_records = {}
        self.tax_rates = {}
        self._initialize_default_plans()
        
    def _initialize_default_plans(self):
        """Initialize default billing plans"""
        for tier, config in self.DEFAULT_PLANS.items():
            plan_id = str(uuid.uuid4())
            plan = BillingPlan(
                id=plan_id,
                name=config["name"],
                tier=tier,
                price=config["price"],
                currency=config["currency"],
                billing_cycle=config["billing_cycle"],
                trial_period_days=config["trial_period_days"],
                features=config["features"],
                created_at=datetime.now()
            )
            self.plans[plan_id] = plan
            
    async def create_subscription(
        self,
        customer_id: str,
        plan_id: str,
        payment_method_id: str,
        trial_end: Optional[datetime] = None,
        metadata: Optional[Dict] = None
    ) -> Subscription:
        """Create new subscription"""
        try:
            plan = self.plans.get(plan_id)
            if not plan:
                raise ValueError(f"Plan not found: {plan_id}")
                
            subscription_id = str(uuid.uuid4())
            now = datetime.now()
            
            # Calculate trial period
            if trial_end is None and plan.trial_period_days > 0:
                trial_start = now
                trial_end = now + timedelta(days=plan.trial_period_days)
                current_period_start = trial_end
                status = SubscriptionStatus.TRIALING
            else:
                trial_start = None
                current_period_start = now
                status = SubscriptionStatus.ACTIVE
                
            # Calculate billing cycle end
            if plan.billing_cycle == BillingCycle.MONTHLY:
                current_period_end = current_period_start + timedelta(days=30)
            elif plan.billing_cycle == BillingCycle.QUARTERLY:
                current_period_end = current_period_start + timedelta(days=90)
            elif plan.billing_cycle == BillingCycle.YEARLY:
                current_period_end = current_period_start + timedelta(days=365)
            else:
                current_period_end = current_period_start + timedelta(days=30)
                
            subscription = Subscription(
                id=subscription_id,
                customer_id=customer_id,
                plan_id=plan_id,
                status=status,
                current_period_start=current_period_start,
                current_period_end=current_period_end,
                trial_start=trial_start,
                trial_end=trial_end,
                payment_method_id=payment_method_id,
                metadata=metadata or {},
                created_at=now
            )
            
            self.subscriptions[subscription_id] = subscription
            
            # Create initial invoice if not in trial
            if status == SubscriptionStatus.ACTIVE:
                await self._create_subscription_invoice(subscription, plan)
                
            logger.info(f"Subscription created: {subscription_id} for customer {customer_id}")
            return subscription
            
        except Exception as e:
            logger.error(f"Error creating subscription: {str(e)}")
            raise
            
    async def update_subscription(
        self,
        subscription_id: str,
        plan_id: Optional[str] = None,
        payment_method_id: Optional[str] = None,
        proration: bool = True
    ) -> Subscription:
        """Update existing subscription with proration"""
        try:
            subscription = self.subscriptions.get(subscription_id)
            if not subscription:
                raise ValueError(f"Subscription not found: {subscription_id}")
                
            old_plan = self.plans.get(subscription.plan_id)
            
            if plan_id and plan_id != subscription.plan_id:
                new_plan = self.plans.get(plan_id)
                if not new_plan:
                    raise ValueError(f"Plan not found: {plan_id}")
                    
                # Calculate proration if enabled
                if proration and subscription.status == SubscriptionStatus.ACTIVE:
                    await self._handle_plan_change_proration(subscription, old_plan, new_plan)
                    
                subscription.plan_id = plan_id
                
            if payment_method_id:
                subscription.payment_method_id = payment_method_id
                
            self.subscriptions[subscription_id] = subscription
            
            logger.info(f"Subscription updated: {subscription_id}")
            return subscription
            
        except Exception as e:
            logger.error(f"Error updating subscription: {str(e)}")
            raise
            
    async def cancel_subscription(
        self,
        subscription_id: str,
        at_period_end: bool = True,
        reason: Optional[str] = None
    ) -> Subscription:
        """Cancel subscription"""
        try:
            subscription = self.subscriptions.get(subscription_id)
            if not subscription:
                raise ValueError(f"Subscription not found: {subscription_id}")
                
            if at_period_end:
                subscription.cancel_at_period_end = True
            else:
                subscription.status = SubscriptionStatus.CANCELED
                subscription.canceled_at = datetime.now()
                
            if reason:
                if not subscription.metadata:
                    subscription.metadata = {}
                subscription.metadata["cancellation_reason"] = reason
                
            self.subscriptions[subscription_id] = subscription
            
            logger.info(f"Subscription canceled: {subscription_id}, at_period_end: {at_period_end}")
            return subscription
            
        except Exception as e:
            logger.error(f"Error canceling subscription: {str(e)}")
            raise
            
    async def create_invoice(
        self,
        customer_id: str,
        amount: Decimal,
        currency: str = "EUR",
        description: Optional[str] = None,
        due_date: Optional[datetime] = None,
        subscription_id: Optional[str] = None
    ) -> Invoice:
        """Create manual invoice"""
        try:
            invoice_id = str(uuid.uuid4())
            now = datetime.now()
            
            if due_date is None:
                due_date = now + timedelta(days=30)
                
            # Calculate tax
            tax_amount = await self._calculate_tax(customer_id, amount, currency)
            total_amount = amount + tax_amount
            
            invoice = Invoice(
                id=invoice_id,
                customer_id=customer_id,
                subscription_id=subscription_id,
                status=InvoiceStatus.OPEN,
                amount_due=total_amount,
                amount_paid=Decimal('0'),
                amount_remaining=total_amount,
                currency=currency,
                due_date=due_date,
                period_start=now,
                period_end=now,
                tax_amount=tax_amount,
                subtotal=amount,
                created_at=now,
                line_items=[{
                    "description": description or "Service charge",
                    "amount": amount,
                    "quantity": 1,
                    "currency": currency
                }]
            )
            
            self.invoices[invoice_id] = invoice
            
            logger.info(f"Invoice created: {invoice_id} for customer {customer_id}")
            return invoice
            
        except Exception as e:
            logger.error(f"Error creating invoice: {str(e)}")
            raise
            
    async def pay_invoice(
        self,
        invoice_id: str,
        payment_method_id: str,
        amount: Optional[Decimal] = None
    ) -> Dict[str, Any]:
        """Process invoice payment"""
        try:
            invoice = self.invoices.get(invoice_id)
            if not invoice:
                raise ValueError(f"Invoice not found: {invoice_id}")
                
            if invoice.status == InvoiceStatus.PAID:
                return {"success": True, "message": "Invoice already paid"}
                
            payment_amount = amount or invoice.amount_remaining
            
            # Process payment through payment processor
            payment_result = await self._process_invoice_payment(
                invoice, payment_method_id, payment_amount
            )
            
            if payment_result["success"]:
                invoice.amount_paid += payment_amount
                invoice.amount_remaining = invoice.amount_due - invoice.amount_paid
                
                if invoice.amount_remaining <= Decimal('0'):
                    invoice.status = InvoiceStatus.PAID
                    invoice.paid_at = datetime.now()
                    
                self.invoices[invoice_id] = invoice
                
                # Update subscription if this was a subscription invoice
                if invoice.subscription_id:
                    await self._handle_subscription_payment(invoice.subscription_id)
                    
                logger.info(f"Invoice payment processed: {invoice_id}")
                
            return payment_result
            
        except Exception as e:
            logger.error(f"Error processing invoice payment: {str(e)}")
            return {"success": False, "error": str(e)}
            
    async def track_usage(
        self,
        subscription_id: str,
        action: str,
        quantity: int = 1,
        metadata: Optional[Dict] = None
    ) -> UsageRecord:
        """Track usage for usage-based billing"""
        try:
            usage_id = str(uuid.uuid4())
            
            usage_record = UsageRecord(
                id=usage_id,
                subscription_id=subscription_id,
                quantity=quantity,
                timestamp=datetime.now(),
                action=action,
                metadata=metadata or {}
            )
            
            if subscription_id not in self.usage_records:
                self.usage_records[subscription_id] = []
            self.usage_records[subscription_id].append(usage_record)
            
            # Check if usage limits exceeded
            await self._check_usage_limits(subscription_id)
            
            logger.debug(f"Usage tracked: {action} x{quantity} for subscription {subscription_id}")
            return usage_record
            
        except Exception as e:
            logger.error(f"Error tracking usage: {str(e)}")
            raise
            
    async def generate_usage_invoice(
        self,
        subscription_id: str,
        period_start: datetime,
        period_end: datetime
    ) -> Optional[Invoice]:
        """Generate invoice based on usage"""
        try:
            subscription = self.subscriptions.get(subscription_id)
            if not subscription:
                raise ValueError(f"Subscription not found: {subscription_id}")
                
            plan = self.plans.get(subscription.plan_id)
            if plan.billing_cycle != BillingCycle.USAGE_BASED:
                return None
                
            # Calculate usage for period
            usage_charges = await self._calculate_usage_charges(
                subscription_id, period_start, period_end
            )
            
            if usage_charges["total_amount"] <= Decimal('0'):
                return None
                
            # Create usage invoice
            invoice = await self.create_invoice(
                customer_id=subscription.customer_id,
                amount=usage_charges["total_amount"],
                currency=plan.currency,
                description=f"Usage charges for {period_start.date()} to {period_end.date()}",
                subscription_id=subscription_id
            )
            
            # Add detailed line items
            invoice.line_items = usage_charges["line_items"]
            self.invoices[invoice.id] = invoice
            
            logger.info(f"Usage invoice generated: {invoice.id} for subscription {subscription_id}")
            return invoice
            
        except Exception as e:
            logger.error(f"Error generating usage invoice: {str(e)}")
            return None
            
    async def handle_dunning_management(self):
        """Handle failed payment retry logic"""
        try:
            current_time = datetime.now()
            
            # Find overdue invoices
            overdue_invoices = [
                invoice for invoice in self.invoices.values()
                if (invoice.status == InvoiceStatus.OPEN and 
                    invoice.due_date < current_time)
            ]
            
            for invoice in overdue_invoices:
                await self._process_dunning_for_invoice(invoice)
                
            # Handle subscriptions with failed payments
            past_due_subscriptions = [
                sub for sub in self.subscriptions.values()
                if sub.status == SubscriptionStatus.PAST_DUE
            ]
            
            for subscription in past_due_subscriptions:
                await self._process_subscription_dunning(subscription)
                
        except Exception as e:
            logger.error(f"Error in dunning management: {str(e)}")
            
    async def calculate_mrr(self) -> Dict[str, Decimal]:
        """Calculate Monthly Recurring Revenue"""
        try:
            mrr_by_plan = {}
            total_mrr = Decimal('0')
            
            active_subscriptions = [
                sub for sub in self.subscriptions.values()
                if sub.status in [SubscriptionStatus.ACTIVE, SubscriptionStatus.TRIALING]
            ]
            
            for subscription in active_subscriptions:
                plan = self.plans.get(subscription.plan_id)
                if not plan:
                    continue
                    
                # Convert to monthly amount
                monthly_amount = self._convert_to_monthly_amount(plan.price, plan.billing_cycle)
                
                if plan.name not in mrr_by_plan:
                    mrr_by_plan[plan.name] = Decimal('0')
                mrr_by_plan[plan.name] += monthly_amount
                total_mrr += monthly_amount
                
            return {
                "total_mrr": total_mrr,
                "mrr_by_plan": mrr_by_plan,
                "active_subscriptions": len(active_subscriptions)
            }
            
        except Exception as e:
            logger.error(f"Error calculating MRR: {str(e)}")
            return {"total_mrr": Decimal('0'), "mrr_by_plan": {}}
            
    async def _create_subscription_invoice(self, subscription: Subscription, plan: BillingPlan):
        """Create invoice for subscription billing cycle"""
        try:
            invoice = await self.create_invoice(
                customer_id=subscription.customer_id,
                amount=plan.price,
                currency=plan.currency,
                description=f"{plan.name} subscription - {subscription.current_period_start.date()} to {subscription.current_period_end.date()}",
                due_date=subscription.current_period_end,
                subscription_id=subscription.id
            )
            
            subscription.latest_invoice_id = invoice.id
            
        except Exception as e:
            logger.error(f"Error creating subscription invoice: {str(e)}")
            
    async def _handle_plan_change_proration(self, subscription: Subscription, old_plan: BillingPlan, new_plan: BillingPlan):
        """Handle proration when changing plans"""
        try:
            now = datetime.now()
            time_remaining = (subscription.current_period_end - now).total_seconds()
            period_duration = (subscription.current_period_end - subscription.current_period_start).total_seconds()
            
            if period_duration > 0:
                proration_factor = time_remaining / period_duration
                
                # Calculate credits and charges
                old_credit = old_plan.price * Decimal(str(proration_factor))
                new_charge = new_plan.price * Decimal(str(proration_factor))
                
                proration_amount = new_charge - old_credit
                
                if proration_amount > Decimal('0'):
                    # Create proration invoice
                    await self.create_invoice(
                        customer_id=subscription.customer_id,
                        amount=proration_amount,
                        currency=new_plan.currency,
                        description=f"Proration for plan change from {old_plan.name} to {new_plan.name}",
                        subscription_id=subscription.id
                    )
                    
        except Exception as e:
            logger.error(f"Error handling proration: {str(e)}")
            
    async def _calculate_tax(self, customer_id: str, amount: Decimal, currency: str) -> Decimal:
        """Calculate tax amount based on customer location"""
        try:
            # Simplified tax calculation - in production use tax service
            default_tax_rate = Decimal('0.19')  # 19% VAT for EU
            return amount * default_tax_rate
            
        except Exception as e:
            logger.error(f"Error calculating tax: {str(e)}")
            return Decimal('0')
            
    async def _process_invoice_payment(self, invoice: Invoice, payment_method_id: str, amount: Decimal) -> Dict[str, Any]:
        """Process payment for invoice"""
        try:
            # Simulate payment processing - integrate with actual payment processor
            await asyncio.sleep(0.1)
            
            # Simulate 95% success rate
            import random
            if random.random() < 0.95:
                return {
                    "success": True,
                    "transaction_id": str(uuid.uuid4()),
                    "amount": amount,
                    "currency": invoice.currency
                }
            else:
                return {
                    "success": False,
                    "error": "Payment failed"
                }
                
        except Exception as e:
            logger.error(f"Error processing payment: {str(e)}")
            return {"success": False, "error": str(e)}
            
    async def _handle_subscription_payment(self, subscription_id: str):
        """Handle successful subscription payment"""
        try:
            subscription = self.subscriptions.get(subscription_id)
            if not subscription:
                return
                
            # Update subscription status
            if subscription.status == SubscriptionStatus.PAST_DUE:
                subscription.status = SubscriptionStatus.ACTIVE
                
            # If trial ended, mark as active
            if subscription.status == SubscriptionStatus.TRIALING:
                if datetime.now() >= subscription.trial_end:
                    subscription.status = SubscriptionStatus.ACTIVE
                    
        except Exception as e:
            logger.error(f"Error handling subscription payment: {str(e)}")
            
    async def _calculate_usage_charges(self, subscription_id: str, period_start: datetime, period_end: datetime) -> Dict[str, Any]:
        """Calculate usage-based charges for period"""
        try:
            usage_records = self.usage_records.get(subscription_id, [])
            period_usage = [
                record for record in usage_records
                if period_start <= record.timestamp <= period_end
            ]
            
            # Usage pricing rules (simplified)
            pricing_rules = {
                "api_call": Decimal('0.01'),
                "storage_gb_hour": Decimal('0.001'),
                "processing_minute": Decimal('0.10'),
                "bandwidth_gb": Decimal('0.05')
            }
            
            charges_by_action = {}
            line_items = []
            total_amount = Decimal('0')
            
            for action, price in pricing_rules.items():
                usage_count = sum(
                    record.quantity for record in period_usage
                    if record.action == action
                )
                
                if usage_count > 0:
                    charge = price * usage_count
                    charges_by_action[action] = {
                        "quantity": usage_count,
                        "unit_price": price,
                        "total": charge
                    }
                    
                    line_items.append({
                        "description": f"{action.replace('_', ' ').title()}",
                        "quantity": usage_count,
                        "unit_price": price,
                        "amount": charge,
                        "currency": "EUR"
                    })
                    
                    total_amount += charge
                    
            return {
                "total_amount": total_amount,
                "charges_by_action": charges_by_action,
                "line_items": line_items,
                "usage_period": {
                    "start": period_start.isoformat(),
                    "end": period_end.isoformat()
                }
            }
            
        except Exception as e:
            logger.error(f"Error calculating usage charges: {str(e)}")
            return {"total_amount": Decimal('0'), "line_items": []}
            
    async def _check_usage_limits(self, subscription_id: str):
        """Check if subscription has exceeded usage limits"""
        try:
            subscription = self.subscriptions.get(subscription_id)
            if not subscription:
                return
                
            plan = self.plans.get(subscription.plan_id)
            if not plan or not plan.features:
                return
                
            # Check current period usage
            current_period_usage = self._get_current_period_usage(subscription_id)
            
            # Check against limits
            for limit_type, limit_value in plan.features.items():
                if limit_type.endswith('_per_month') and limit_value > 0:
                    action_type = limit_type.replace('_per_month', '')
                    current_usage = current_period_usage.get(action_type, 0)
                    
                    if current_usage >= limit_value:
                        logger.warning(f"Usage limit exceeded for subscription {subscription_id}: {action_type}")
                        # Implement limit enforcement (throttling, notifications, etc.)
                        
        except Exception as e:
            logger.error(f"Error checking usage limits: {str(e)}")
            
    def _get_current_period_usage(self, subscription_id: str) -> Dict[str, int]:
        """Get usage for current billing period"""
        try:
            subscription = self.subscriptions.get(subscription_id)
            if not subscription:
                return {}
                
            usage_records = self.usage_records.get(subscription_id, [])
            current_period_usage = {}
            
            for record in usage_records:
                if subscription.current_period_start <= record.timestamp <= subscription.current_period_end:
                    if record.action not in current_period_usage:
                        current_period_usage[record.action] = 0
                    current_period_usage[record.action] += record.quantity
                    
            return current_period_usage
            
        except Exception as e:
            logger.error(f"Error getting current period usage: {str(e)}")
            return {}
            
    async def _process_dunning_for_invoice(self, invoice: Invoice):
        """Process dunning (retry logic) for failed invoice"""
        try:
            days_overdue = (datetime.now() - invoice.due_date).days
            
            if days_overdue == 1:
                # First reminder
                await self._send_payment_reminder(invoice, "first_reminder")
            elif days_overdue == 7:
                # Second reminder
                await self._send_payment_reminder(invoice, "second_reminder")
            elif days_overdue == 14:
                # Final notice
                await self._send_payment_reminder(invoice, "final_notice")
            elif days_overdue >= 30:
                # Mark as uncollectible
                invoice.status = InvoiceStatus.UNCOLLECTIBLE
                await self._handle_uncollectible_invoice(invoice)
                
        except Exception as e:
            logger.error(f"Error processing dunning for invoice {invoice.id}: {str(e)}")
            
    async def _process_subscription_dunning(self, subscription: Subscription):
        """Process dunning for past due subscription"""
        try:
            # Retry payment for past due subscription
            if subscription.payment_method_id and subscription.latest_invoice_id:
                latest_invoice = self.invoices.get(subscription.latest_invoice_id)
                if latest_invoice and latest_invoice.status == InvoiceStatus.OPEN:
                    retry_result = await self.pay_invoice(
                        latest_invoice.id,
                        subscription.payment_method_id
                    )
                    
                    if not retry_result["success"]:
                        # Check if should cancel subscription
                        days_past_due = (datetime.now() - latest_invoice.due_date).days
                        if days_past_due >= 30:
                            await self.cancel_subscription(subscription.id, at_period_end=False)
                            
        except Exception as e:
            logger.error(f"Error processing subscription dunning: {str(e)}")
            
    async def _send_payment_reminder(self, invoice: Invoice, reminder_type: str):
        """Send payment reminder notification"""
        try:
            # Implement email/SMS notification
            logger.info(f"Payment reminder sent: {reminder_type} for invoice {invoice.id}")
            
        except Exception as e:
            logger.error(f"Error sending payment reminder: {str(e)}")
            
    async def _handle_uncollectible_invoice(self, invoice: Invoice):
        """Handle uncollectible invoice"""
        try:
            if invoice.subscription_id:
                subscription = self.subscriptions.get(invoice.subscription_id)
                if subscription:
                    await self.cancel_subscription(subscription.id, at_period_end=False)
                    
            logger.info(f"Invoice marked uncollectible: {invoice.id}")
            
        except Exception as e:
            logger.error(f"Error handling uncollectible invoice: {str(e)}")
            
    def _convert_to_monthly_amount(self, amount: Decimal, billing_cycle: BillingCycle) -> Decimal:
        """Convert amount to monthly equivalent for MRR calculation"""
        try:
            if billing_cycle == BillingCycle.MONTHLY:
                return amount
            elif billing_cycle == BillingCycle.QUARTERLY:
                return amount / 3
            elif billing_cycle == BillingCycle.YEARLY:
                return amount / 12
            else:
                return amount
                
        except Exception as e:
            logger.error(f"Error converting to monthly amount: {str(e)}")
            return Decimal('0')