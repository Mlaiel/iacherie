"""Comprehensive Billing Engine with Automatic Invoicing
Advanced billing system with subscription management, prorations, and automated processes.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import logging
import uuid
from typing import Dict, List, Optional, Any, Union
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from enum import Enum
from decimal import Decimal
import json

logger = logging.getLogger(__name__)


class BillingCycle(Enum):
    """Billing cycle options"""
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    ANNUAL = "annual"
    WEEKLY = "weekly"
    DAILY = "daily"


class InvoiceStatus(Enum):
    """Invoice status tracking"""
    DRAFT = "draft"
    PENDING = "pending"
    SENT = "sent"
    PAID = "paid"
    OVERDUE = "overdue"
    CANCELLED = "cancelled"
    REFUNDED = "refunded"


class SubscriptionStatus(Enum):
    """Subscription status tracking"""
    ACTIVE = "active"
    PENDING = "pending"
    CANCELLED = "cancelled"
    SUSPENDED = "suspended"
    EXPIRED = "expired"
    TRIALING = "trialing"


@dataclass
class BillingPlan:
    """Billing plan configuration"""
    id: str
    name: str
    price: Decimal
    currency: str
    billing_cycle: BillingCycle
    trial_period_days: int = 0
    features: List[str] = None
    max_users: Optional[int] = None
    max_content_gb: Optional[int] = None
    proration_enabled: bool = True
    
    def __post_init__(self):
        if self.features is None:
            self.features = []


@dataclass
class ProrationCalculation:
    """Proration calculation details"""
    old_plan_amount: Decimal
    new_plan_amount: Decimal
    used_days: int
    total_days: int
    proration_amount: Decimal
    credit_amount: Decimal
    next_charge_amount: Decimal


@dataclass
class Invoice:
    """Invoice data structure"""
    id: str
    customer_id: str
    subscription_id: Optional[str]
    amount: Decimal
    currency: str
    status: InvoiceStatus
    line_items: List[Dict[str, Any]]
    created_at: datetime
    due_date: datetime
    paid_at: Optional[datetime] = None
    payment_method_id: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    tax_amount: Decimal = Decimal("0.00")
    discount_amount: Decimal = Decimal("0.00")
    total_amount: Decimal = None
    
    def __post_init__(self):
        if self.total_amount is None:
            self.total_amount = self.amount + self.tax_amount - self.discount_amount


@dataclass
class Subscription:
    """Subscription data structure"""
    id: str
    customer_id: str
    plan_id: str
    status: SubscriptionStatus
    current_period_start: datetime
    current_period_end: datetime
    trial_end: Optional[datetime] = None
    created_at: datetime = None
    cancelled_at: Optional[datetime] = None
    quantity: int = 1
    metadata: Optional[Dict[str, Any]] = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()


class BillingEngine:
    """Comprehensive billing engine with automation"""
    
    def __init__(self):
        self.plans: Dict[str, BillingPlan] = {}
        self.subscriptions: Dict[str, Subscription] = {}
        self.invoices: Dict[str, Invoice] = {}
        self.customers: Dict[str, Dict[str, Any]] = {}
        self._initialize_default_plans()
    
    def _initialize_default_plans(self):
        """Initialize default billing plans"""
        # Creator Basic Plan
        self.plans["creator_basic"] = BillingPlan(
            id="creator_basic",
            name="Creator Basic",
            price=Decimal("29.99"),
            currency="EUR",
            billing_cycle=BillingCycle.MONTHLY,
            trial_period_days=14,
            features=["content_protection", "basic_analytics", "5gb_storage"],
            max_content_gb=5
        )
        
        # Creator Pro Plan
        self.plans["creator_pro"] = BillingPlan(
            id="creator_pro",
            name="Creator Pro",
            price=Decimal("99.99"),
            currency="EUR",
            billing_cycle=BillingCycle.MONTHLY,
            trial_period_days=14,
            features=["content_protection", "advanced_analytics", "ai_detection", "50gb_storage"],
            max_content_gb=50
        )
        
        # Enterprise Plan
        self.plans["enterprise"] = BillingPlan(
            id="enterprise",
            name="Enterprise",
            price=Decimal("499.99"),
            currency="EUR",
            billing_cycle=BillingCycle.MONTHLY,
            trial_period_days=30,
            features=["full_protection", "enterprise_analytics", "ai_detection", "unlimited_storage"],
            max_users=50
        )
    
    async def create_customer(
        self,
        customer_id: str,
        email: str,
        name: str,
        country: str,
        tax_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Create a new customer"""
        try:
            customer_data = {
                "id": customer_id,
                "email": email,
                "name": name,
                "country": country,
                "tax_id": tax_id,
                "created_at": datetime.now().isoformat(),
                "metadata": metadata or {},
                "payment_methods": [],
                "billing_address": None
            }
            
            self.customers[customer_id] = customer_data
            
            logger.info(f"Customer created: {customer_id}")
            return {"success": True, "customer": customer_data}
            
        except Exception as e:
            logger.error(f"Error creating customer: {str(e)}")
            return {"success": False, "error": str(e)}
    
    async def create_subscription(
        self,
        customer_id: str,
        plan_id: str,
        payment_method_id: Optional[str] = None,
        trial_period_days: Optional[int] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Create a new subscription with automatic billing"""
        try:
            if customer_id not in self.customers:
                return {"success": False, "error": "Customer not found"}
            
            if plan_id not in self.plans:
                return {"success": False, "error": "Plan not found"}
            
            plan = self.plans[plan_id]
            subscription_id = str(uuid.uuid4())
            
            # Calculate trial period
            trial_days = trial_period_days or plan.trial_period_days
            now = datetime.now()
            trial_end = now + timedelta(days=trial_days) if trial_days > 0 else None
            
            # Calculate billing period
            period_start = trial_end if trial_end else now
            period_end = self._calculate_period_end(period_start, plan.billing_cycle)
            
            subscription = Subscription(
                id=subscription_id,
                customer_id=customer_id,
                plan_id=plan_id,
                status=SubscriptionStatus.TRIALING if trial_end else SubscriptionStatus.ACTIVE,
                current_period_start=period_start,
                current_period_end=period_end,
                trial_end=trial_end,
                metadata=metadata
            )
            
            self.subscriptions[subscription_id] = subscription
            
            # Create initial invoice if no trial
            if not trial_end:
                await self._create_subscription_invoice(subscription)
            
            logger.info(f"Subscription created: {subscription_id}")
            return {
                "success": True,
                "subscription": asdict(subscription),
                "trial_end": trial_end.isoformat() if trial_end else None
            }
            
        except Exception as e:
            logger.error(f"Error creating subscription: {str(e)}")
            return {"success": False, "error": str(e)}
    
    async def change_subscription_plan(
        self,
        subscription_id: str,
        new_plan_id: str,
        prorate: bool = True
    ) -> Dict[str, Any]:
        """Change subscription plan with proration"""
        try:
            if subscription_id not in self.subscriptions:
                return {"success": False, "error": "Subscription not found"}
            
            if new_plan_id not in self.plans:
                return {"success": False, "error": "Plan not found"}
            
            subscription = self.subscriptions[subscription_id]
            old_plan = self.plans[subscription.plan_id]
            new_plan = self.plans[new_plan_id]
            
            proration_details = None
            if prorate and old_plan.proration_enabled and new_plan.proration_enabled:
                proration_details = await self._calculate_proration(
                    subscription, old_plan, new_plan
                )
            
            # Update subscription
            subscription.plan_id = new_plan_id
            
            # Create proration invoice if needed
            if proration_details and proration_details.proration_amount > 0:
                await self._create_proration_invoice(subscription, proration_details)
            elif proration_details and proration_details.credit_amount > 0:
                await self._apply_credit(subscription, proration_details.credit_amount)
            
            logger.info(f"Subscription plan changed: {subscription_id} -> {new_plan_id}")
            return {
                "success": True,
                "subscription": asdict(subscription),
                "proration": asdict(proration_details) if proration_details else None
            }
            
        except Exception as e:
            logger.error(f"Error changing subscription plan: {str(e)}")
            return {"success": False, "error": str(e)}
    
    async def cancel_subscription(
        self,
        subscription_id: str,
        at_period_end: bool = True,
        reason: Optional[str] = None
    ) -> Dict[str, Any]:
        """Cancel a subscription"""
        try:
            if subscription_id not in self.subscriptions:
                return {"success": False, "error": "Subscription not found"}
            
            subscription = self.subscriptions[subscription_id]
            
            if at_period_end:
                # Cancel at period end - no immediate action
                subscription.metadata = subscription.metadata or {}
                subscription.metadata["cancel_at_period_end"] = True
                subscription.metadata["cancellation_reason"] = reason
                
                logger.info(f"Subscription will cancel at period end: {subscription_id}")
                return {
                    "success": True,
                    "message": "Subscription will cancel at period end",
                    "cancel_date": subscription.current_period_end.isoformat()
                }
            else:
                # Cancel immediately
                subscription.status = SubscriptionStatus.CANCELLED
                subscription.cancelled_at = datetime.now()
                
                # Calculate prorated refund if applicable
                refund_amount = await self._calculate_cancellation_refund(subscription)
                
                logger.info(f"Subscription cancelled immediately: {subscription_id}")
                return {
                    "success": True,
                    "message": "Subscription cancelled immediately",
                    "refund_amount": float(refund_amount) if refund_amount > 0 else 0
                }
                
        except Exception as e:
            logger.error(f"Error cancelling subscription: {str(e)}")
            return {"success": False, "error": str(e)}
    
    async def process_recurring_billing(self) -> Dict[str, Any]:
        """Process all recurring billing for active subscriptions"""
        try:
            now = datetime.now()
            processed_count = 0
            failed_count = 0
            results = []
            
            for subscription in self.subscriptions.values():
                if subscription.status not in [SubscriptionStatus.ACTIVE, SubscriptionStatus.TRIALING]:
                    continue
                
                # Check if trial period ended
                if (subscription.status == SubscriptionStatus.TRIALING and 
                    subscription.trial_end and subscription.trial_end <= now):
                    subscription.status = SubscriptionStatus.ACTIVE
                    subscription.current_period_start = now
                    subscription.current_period_end = self._calculate_period_end(
                        now, self.plans[subscription.plan_id].billing_cycle
                    )
                
                # Check if billing period ended
                if subscription.current_period_end <= now:
                    try:
                        # Check for cancellation
                        if (subscription.metadata and 
                            subscription.metadata.get("cancel_at_period_end")):
                            subscription.status = SubscriptionStatus.CANCELLED
                            subscription.cancelled_at = now
                            continue
                        
                        # Create new invoice
                        invoice_result = await self._create_subscription_invoice(subscription)
                        
                        if invoice_result["success"]:
                            # Update subscription period
                            subscription.current_period_start = subscription.current_period_end
                            subscription.current_period_end = self._calculate_period_end(
                                subscription.current_period_start,
                                self.plans[subscription.plan_id].billing_cycle
                            )
                            processed_count += 1
                            results.append({
                                "subscription_id": subscription.id,
                                "status": "success",
                                "invoice_id": invoice_result["invoice_id"]
                            })
                        else:
                            failed_count += 1
                            results.append({
                                "subscription_id": subscription.id,
                                "status": "failed",
                                "error": invoice_result["error"]
                            })
                            
                    except Exception as e:
                        failed_count += 1
                        results.append({
                            "subscription_id": subscription.id,
                            "status": "failed",
                            "error": str(e)
                        })
            
            logger.info(f"Recurring billing processed: {processed_count} success, {failed_count} failed")
            return {
                "success": True,
                "processed": processed_count,
                "failed": failed_count,
                "results": results
            }
            
        except Exception as e:
            logger.error(f"Error processing recurring billing: {str(e)}")
            return {"success": False, "error": str(e)}
    
    async def _create_subscription_invoice(self, subscription: Subscription) -> Dict[str, Any]:
        """Create invoice for subscription billing"""
        try:
            plan = self.plans[subscription.plan_id]
            invoice_id = str(uuid.uuid4())
            
            line_items = [{
                "description": f"{plan.name} - {plan.billing_cycle.value}",
                "quantity": subscription.quantity,
                "unit_price": float(plan.price),
                "amount": float(plan.price * subscription.quantity)
            }]
            
            # Calculate tax
            customer = self.customers[subscription.customer_id]
            tax_amount = await self._calculate_tax(
                plan.price * subscription.quantity,
                customer["country"]
            )
            
            invoice = Invoice(
                id=invoice_id,
                customer_id=subscription.customer_id,
                subscription_id=subscription.id,
                amount=plan.price * subscription.quantity,
                currency=plan.currency,
                status=InvoiceStatus.PENDING,
                line_items=line_items,
                created_at=datetime.now(),
                due_date=datetime.now() + timedelta(days=7),
                tax_amount=tax_amount
            )
            
            self.invoices[invoice_id] = invoice
            
            # Attempt to charge immediately
            payment_result = await self._process_invoice_payment(invoice)
            
            return {
                "success": True,
                "invoice_id": invoice_id,
                "payment_status": payment_result["status"]
            }
            
        except Exception as e:
            logger.error(f"Error creating subscription invoice: {str(e)}")
            return {"success": False, "error": str(e)}
    
    async def _calculate_proration(
        self,
        subscription: Subscription,
        old_plan: BillingPlan,
        new_plan: BillingPlan
    ) -> ProrationCalculation:
        """Calculate proration for plan change"""
        try:
            now = datetime.now()
            total_days = (subscription.current_period_end - subscription.current_period_start).days
            used_days = max(0, (now - subscription.current_period_start).days)  # Ensure non-negative
            remaining_days = max(0, total_days - used_days)
            
            # Calculate unused amount from old plan
            if total_days > 0:
                daily_old_rate = old_plan.price / total_days
                unused_old_amount = daily_old_rate * remaining_days
                
                # Calculate new plan amount for remaining period
                daily_new_rate = new_plan.price / total_days
                new_amount_remaining = daily_new_rate * remaining_days
            else:
                unused_old_amount = Decimal("0")
                new_amount_remaining = Decimal("0")
            
            # Calculate proration
            proration_amount = max(Decimal("0"), new_amount_remaining - unused_old_amount)
            credit_amount = max(Decimal("0"), unused_old_amount - new_amount_remaining)
            
            return ProrationCalculation(
                old_plan_amount=old_plan.price,
                new_plan_amount=new_plan.price,
                used_days=used_days,
                total_days=total_days,
                proration_amount=proration_amount,
                credit_amount=credit_amount,
                next_charge_amount=new_plan.price
            )
            
        except Exception as e:
            logger.error(f"Error calculating proration: {str(e)}")
            return ProrationCalculation(
                old_plan_amount=old_plan.price,
                new_plan_amount=new_plan.price,
                used_days=0,
                total_days=30,
                proration_amount=Decimal("0"),
                credit_amount=Decimal("0"),
                next_charge_amount=new_plan.price
            )
    
    async def _create_proration_invoice(
        self,
        subscription: Subscription,
        proration: ProrationCalculation
    ) -> Dict[str, Any]:
        """Create proration invoice for plan upgrade"""
        try:
            invoice_id = str(uuid.uuid4())
            plan = self.plans[subscription.plan_id]
            
            line_items = [{
                "description": f"Plan upgrade proration - {plan.name}",
                "quantity": 1,
                "unit_price": float(proration.proration_amount),
                "amount": float(proration.proration_amount)
            }]
            
            customer = self.customers[subscription.customer_id]
            tax_amount = await self._calculate_tax(proration.proration_amount, customer["country"])
            
            invoice = Invoice(
                id=invoice_id,
                customer_id=subscription.customer_id,
                subscription_id=subscription.id,
                amount=proration.proration_amount,
                currency=plan.currency,
                status=InvoiceStatus.PENDING,
                line_items=line_items,
                created_at=datetime.now(),
                due_date=datetime.now() + timedelta(days=1),  # Immediate
                tax_amount=tax_amount,
                metadata={"type": "proration"}
            )
            
            self.invoices[invoice_id] = invoice
            
            # Process payment immediately
            await self._process_invoice_payment(invoice)
            
            return {"success": True, "invoice_id": invoice_id}
            
        except Exception as e:
            logger.error(f"Error creating proration invoice: {str(e)}")
            return {"success": False, "error": str(e)}
    
    async def _calculate_tax(self, amount: Decimal, country: str) -> Decimal:
        """Calculate tax amount based on jurisdiction"""
        try:
            # EU VAT rates (simplified)
            vat_rates = {
                "DE": Decimal("0.19"),  # Germany 19%
                "FR": Decimal("0.20"),  # France 20%
                "IT": Decimal("0.22"),  # Italy 22%
                "ES": Decimal("0.21"),  # Spain 21%
                "NL": Decimal("0.21"),  # Netherlands 21%
                "BE": Decimal("0.21"),  # Belgium 21%
                "AT": Decimal("0.20"),  # Austria 20%
            }
            
            vat_rate = vat_rates.get(country, Decimal("0.00"))
            return amount * vat_rate
            
        except Exception as e:
            logger.error(f"Error calculating tax: {str(e)}")
            return Decimal("0.00")
    
    async def _process_invoice_payment(self, invoice: Invoice) -> Dict[str, Any]:
        """Process payment for an invoice"""
        try:
            # In a real implementation, this would integrate with payment processor
            # For now, simulate payment processing
            
            # Simulate 90% success rate
            import random
            if random.random() < 0.9:
                invoice.status = InvoiceStatus.PAID
                invoice.paid_at = datetime.now()
                return {"status": "paid", "success": True}
            else:
                invoice.status = InvoiceStatus.OVERDUE
                return {"status": "failed", "success": False, "error": "Payment failed"}
                
        except Exception as e:
            logger.error(f"Error processing invoice payment: {str(e)}")
            return {"status": "failed", "success": False, "error": str(e)}
    
    def _calculate_period_end(self, start_date: datetime, billing_cycle: BillingCycle) -> datetime:
        """Calculate billing period end date"""
        if billing_cycle == BillingCycle.MONTHLY:
            return start_date + timedelta(days=30)
        elif billing_cycle == BillingCycle.QUARTERLY:
            return start_date + timedelta(days=90)
        elif billing_cycle == BillingCycle.ANNUAL:
            return start_date + timedelta(days=365)
        elif billing_cycle == BillingCycle.WEEKLY:
            return start_date + timedelta(days=7)
        elif billing_cycle == BillingCycle.DAILY:
            return start_date + timedelta(days=1)
        else:
            return start_date + timedelta(days=30)
    
    async def _calculate_cancellation_refund(self, subscription: Subscription) -> Decimal:
        """Calculate refund amount for immediate cancellation"""
        try:
            now = datetime.now()
            total_days = (subscription.current_period_end - subscription.current_period_start).days
            used_days = (now - subscription.current_period_start).days
            remaining_days = max(0, total_days - used_days)
            
            if remaining_days > 0:
                plan = self.plans[subscription.plan_id]
                daily_rate = plan.price / total_days
                return daily_rate * remaining_days
            
            return Decimal("0.00")
            
        except Exception as e:
            logger.error(f"Error calculating cancellation refund: {str(e)}")
            return Decimal("0.00")
    
    async def _apply_credit(self, subscription: Subscription, credit_amount: Decimal):
        """Apply credit to customer account"""
        try:
            customer = self.customers[subscription.customer_id]
            if "credits" not in customer:
                customer["credits"] = Decimal("0.00")
            
            customer["credits"] += credit_amount
            logger.info(f"Applied credit {credit_amount} to customer {subscription.customer_id}")
            
        except Exception as e:
            logger.error(f"Error applying credit: {str(e)}")
    
    async def get_subscription_details(self, subscription_id: str) -> Dict[str, Any]:
        """Get detailed subscription information"""
        try:
            if subscription_id not in self.subscriptions:
                return {"success": False, "error": "Subscription not found"}
            
            subscription = self.subscriptions[subscription_id]
            plan = self.plans[subscription.plan_id]
            
            # Get recent invoices
            recent_invoices = [
                asdict(invoice) for invoice in self.invoices.values()
                if invoice.subscription_id == subscription_id
            ]
            recent_invoices.sort(key=lambda x: x["created_at"], reverse=True)
            
            return {
                "success": True,
                "subscription": asdict(subscription),
                "plan": asdict(plan),
                "recent_invoices": recent_invoices[:5]
            }
            
        except Exception as e:
            logger.error(f"Error getting subscription details: {str(e)}")
            return {"success": False, "error": str(e)}
    
    async def generate_billing_summary(self, customer_id: str) -> Dict[str, Any]:
        """Generate billing summary for customer"""
        try:
            if customer_id not in self.customers:
                return {"success": False, "error": "Customer not found"}
            
            customer = self.customers[customer_id]
            
            # Get customer subscriptions
            customer_subscriptions = [
                s for s in self.subscriptions.values() 
                if s.customer_id == customer_id
            ]
            
            # Get customer invoices
            customer_invoices = [
                i for i in self.invoices.values()
                if i.customer_id == customer_id
            ]
            
            # Calculate totals
            total_paid = sum(
                i.total_amount for i in customer_invoices 
                if i.status == InvoiceStatus.PAID
            )
            
            total_outstanding = sum(
                i.total_amount for i in customer_invoices
                if i.status in [InvoiceStatus.PENDING, InvoiceStatus.OVERDUE]
            )
            
            return {
                "success": True,
                "customer": customer,
                "active_subscriptions": len([s for s in customer_subscriptions if s.status == SubscriptionStatus.ACTIVE]),
                "total_subscriptions": len(customer_subscriptions),
                "total_paid": float(total_paid),
                "total_outstanding": float(total_outstanding),
                "invoice_count": len(customer_invoices),
                "credits": float(customer.get("credits", 0))
            }
            
        except Exception as e:
            logger.error(f"Error generating billing summary: {str(e)}")
            return {"success": False, "error": str(e)}