"""
Subscription Management Core - Advanced Subscription and Revenue Management System
=================================================================================

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

Core business logic for managing subscriptions, recurring payments, billing automation,
and revenue optimization across multiple tiers and payment models.
"""

import asyncio
from typing import Dict, List, Optional, Any, Tuple, Union
from enum import Enum
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import logging
import json
import hashlib
import uuid
from decimal import Decimal

# Get logger
logger = logging.getLogger(__name__)

class SubscriptionStatus(Enum):
    """Subscription status types"""
    ACTIVE = "active"
    PENDING = "pending"
    CANCELLED = "cancelled"
    EXPIRED = "expired"
    SUSPENDED = "suspended"
    TRIAL = "trial"
    PAST_DUE = "past_due"

class BillingCycle(Enum):
    """Billing cycle options"""
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    SEMI_ANNUAL = "semi_annual"
    ANNUAL = "annual"
    WEEKLY = "weekly"
    DAILY = "daily"

class SubscriptionTier(Enum):
    """Subscription tier levels"""
    BASIC = "basic"
    PROFESSIONAL = "professional"
    ENTERPRISE = "enterprise"
    CUSTOM = "custom"
    TRIAL = "trial"

class BillingAction(Enum):
    """Billing action types"""
    CHARGE = "charge"
    REFUND = "refund"
    PRORATION = "proration"
    CREDIT = "credit"
    ADJUSTMENT = "adjustment"

class RevenueType(Enum):
    """Revenue type categories"""
    SUBSCRIPTION = "subscription"
    ONE_TIME = "one_time"
    USAGE_BASED = "usage_based"
    COMMISSION = "commission"
    TRANSACTION_FEE = "transaction_fee"

@dataclass
class SubscriptionPlan:
    """Subscription plan definition"""
    plan_id: str
    name: str
    description: str
    tier: SubscriptionTier
    price: Decimal
    currency: str
    billing_cycle: BillingCycle
    trial_period_days: int
    features: List[str]
    usage_limits: Dict[str, Any]
    is_active: bool = True
    created_at: datetime = field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class Subscription:
    """Active subscription record"""
    subscription_id: str
    customer_id: str
    plan_id: str
    status: SubscriptionStatus
    current_period_start: datetime
    current_period_end: datetime
    trial_end: Optional[datetime]
    billing_cycle: BillingCycle
    price: Decimal
    currency: str
    quantity: int = 1
    discount_amount: Decimal = field(default=Decimal('0'))
    tax_amount: Decimal = field(default=Decimal('0'))
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    cancelled_at: Optional[datetime] = None
    cancellation_reason: Optional[str] = None
    payment_method_id: Optional[str] = None
    next_billing_date: Optional[datetime] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class BillingTransaction:
    """Billing transaction record"""
    transaction_id: str
    subscription_id: str
    customer_id: str
    action: BillingAction
    amount: Decimal
    currency: str
    period_start: datetime
    period_end: datetime
    invoice_id: Optional[str] = None
    payment_transaction_id: Optional[str] = None
    status: str = "pending"
    created_at: datetime = field(default_factory=datetime.utcnow)
    processed_at: Optional[datetime] = None
    description: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class Invoice:
    """Invoice record"""
    invoice_id: str
    subscription_id: str
    customer_id: str
    invoice_number: str
    amount_due: Decimal
    amount_paid: Decimal
    currency: str
    period_start: datetime
    period_end: datetime
    status: str = "draft"
    due_date: datetime = field(default_factory=lambda: datetime.utcnow() + timedelta(days=30))
    created_at: datetime = field(default_factory=datetime.utcnow)
    paid_at: Optional[datetime] = None
    line_items: List[Dict[str, Any]] = field(default_factory=list)
    tax_details: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class RevenueRecord:
    """Revenue tracking record"""
    record_id: str
    customer_id: str
    subscription_id: Optional[str]
    revenue_type: RevenueType
    amount: Decimal
    currency: str
    recognized_at: datetime
    billing_period: Optional[Tuple[datetime, datetime]] = None
    commission_rate: Optional[Decimal] = None
    source_transaction_id: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = field(default_factory=dict)

class PlanManager:
    """Subscription plan management system"""
    
    def __init__(self):
        self.plans = {}
        self.plan_features = {}
        self.tier_configs = {}
        
        # Initialize default plans
        self._initialize_default_plans()
        
        logger.info("Plan Manager initialized")

    def _initialize_default_plans(self):
        """Initialize default subscription plans"""
        default_plans = [
            {
                "plan_id": "basic_monthly",
                "name": "Basic Monthly",
                "description": "Essential features for individual creators",
                "tier": SubscriptionTier.BASIC,
                "price": Decimal('9.99'),
                "currency": "USD",
                "billing_cycle": BillingCycle.MONTHLY,
                "trial_period_days": 7,
                "features": [
                    "content_upload_5gb",
                    "basic_analytics",
                    "email_support",
                    "watermark_removal",
                    "basic_monetization"
                ],
                "usage_limits": {
                    "storage_gb": 5,
                    "uploads_per_month": 50,
                    "api_calls_per_day": 1000,
                    "bandwidth_gb": 10
                }
            },
            {
                "plan_id": "professional_monthly",
                "name": "Professional Monthly",
                "description": "Advanced features for professional creators",
                "tier": SubscriptionTier.PROFESSIONAL,
                "price": Decimal('29.99'),
                "currency": "USD",
                "billing_cycle": BillingCycle.MONTHLY,
                "trial_period_days": 14,
                "features": [
                    "content_upload_50gb",
                    "advanced_analytics",
                    "priority_support",
                    "custom_branding",
                    "advanced_monetization",
                    "collaboration_tools",
                    "api_access"
                ],
                "usage_limits": {
                    "storage_gb": 50,
                    "uploads_per_month": 500,
                    "api_calls_per_day": 10000,
                    "bandwidth_gb": 100
                }
            },
            {
                "plan_id": "enterprise_monthly",
                "name": "Enterprise Monthly",
                "description": "Full-featured solution for enterprise clients",
                "tier": SubscriptionTier.ENTERPRISE,
                "price": Decimal('99.99'),
                "currency": "USD",
                "billing_cycle": BillingCycle.MONTHLY,
                "trial_period_days": 30,
                "features": [
                    "unlimited_storage",
                    "enterprise_analytics",
                    "dedicated_support",
                    "white_label",
                    "enterprise_monetization",
                    "team_collaboration",
                    "full_api_access",
                    "custom_integrations",
                    "sla_guarantee"
                ],
                "usage_limits": {
                    "storage_gb": -1,  # Unlimited
                    "uploads_per_month": -1,
                    "api_calls_per_day": 100000,
                    "bandwidth_gb": 1000
                }
            }
        ]
        
        for plan_data in default_plans:
            plan = SubscriptionPlan(**plan_data)
            self.plans[plan.plan_id] = plan

    async def create_plan(self, plan_data: Dict[str, Any]) -> str:
        """Create new subscription plan"""
        try:
            plan_id = plan_data.get("plan_id", f"plan_{uuid.uuid4().hex[:12]}")
            
            plan = SubscriptionPlan(
                plan_id=plan_id,
                name=plan_data["name"],
                description=plan_data["description"],
                tier=SubscriptionTier(plan_data["tier"]),
                price=Decimal(str(plan_data["price"])),
                currency=plan_data["currency"],
                billing_cycle=BillingCycle(plan_data["billing_cycle"]),
                trial_period_days=plan_data.get("trial_period_days", 0),
                features=plan_data.get("features", []),
                usage_limits=plan_data.get("usage_limits", {}),
                metadata=plan_data.get("metadata", {})
            )
            
            self.plans[plan_id] = plan
            
            logger.info(f"Subscription plan created: {plan_id}")
            return plan_id
            
        except Exception as e:
            logger.error(f"Error creating plan: {str(e)}")
            raise

    async def update_plan(self, plan_id: str, updates: Dict[str, Any]) -> bool:
        """Update existing subscription plan"""
        try:
            if plan_id not in self.plans:
                raise ValueError(f"Plan not found: {plan_id}")
            
            plan = self.plans[plan_id]
            
            # Update allowed fields
            if "name" in updates:
                plan.name = updates["name"]
            if "description" in updates:
                plan.description = updates["description"]
            if "price" in updates:
                plan.price = Decimal(str(updates["price"]))
            if "features" in updates:
                plan.features = updates["features"]
            if "usage_limits" in updates:
                plan.usage_limits.update(updates["usage_limits"])
            if "is_active" in updates:
                plan.is_active = updates["is_active"]
            if "metadata" in updates:
                plan.metadata.update(updates["metadata"])
            
            logger.info(f"Plan updated: {plan_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error updating plan: {str(e)}")
            return False

    async def get_plan(self, plan_id: str) -> Optional[SubscriptionPlan]:
        """Get subscription plan by ID"""
        return self.plans.get(plan_id)

    async def list_plans(self, tier: Optional[SubscriptionTier] = None, active_only: bool = True) -> List[SubscriptionPlan]:
        """List subscription plans with optional filtering"""
        plans = list(self.plans.values())
        
        if active_only:
            plans = [p for p in plans if p.is_active]
        
        if tier:
            plans = [p for p in plans if p.tier == tier]
        
        return plans

    async def calculate_proration(self, old_plan: SubscriptionPlan, new_plan: SubscriptionPlan, 
                                days_remaining: int, billing_cycle_days: int) -> Dict[str, Any]:
        """Calculate proration for plan changes"""
        try:
            # Calculate remaining value of old plan
            old_daily_rate = old_plan.price / billing_cycle_days
            old_remaining_value = old_daily_rate * days_remaining
            
            # Calculate prorated amount for new plan
            new_daily_rate = new_plan.price / billing_cycle_days
            new_prorated_amount = new_daily_rate * days_remaining
            
            # Calculate credit/charge
            proration_amount = new_prorated_amount - old_remaining_value
            
            proration_details = {
                "old_plan_id": old_plan.plan_id,
                "new_plan_id": new_plan.plan_id,
                "days_remaining": days_remaining,
                "billing_cycle_days": billing_cycle_days,
                "old_remaining_value": float(old_remaining_value),
                "new_prorated_amount": float(new_prorated_amount),
                "proration_amount": float(proration_amount),
                "is_upgrade": proration_amount > 0,
                "calculated_at": datetime.utcnow().isoformat()
            }
            
            return proration_details
            
        except Exception as e:
            logger.error(f"Error calculating proration: {str(e)}")
            raise

class BillingEngine:
    """Automated billing processing engine"""
    
    def __init__(self):
        self.billing_transactions = {}
        self.invoices = {}
        self.billing_rules = {}
        self.tax_rules = {}
        
        # Initialize billing rules
        self._initialize_billing_rules()
        
        logger.info("Billing Engine initialized")

    def _initialize_billing_rules(self):
        """Initialize billing and tax rules"""
        self.billing_rules = {
            "retry_failed_payments": {
                "max_retries": 3,
                "retry_intervals": [1, 3, 7],  # Days
                "final_action": "suspend"
            },
            "grace_period": {
                "days": 3,
                "send_reminders": True,
                "reminder_intervals": [1, 3]
            },
            "proration": {
                "enabled": True,
                "minimum_amount": Decimal('1.00'),
                "round_to_cents": True
            }
        }
        
        self.tax_rules = {
            "US": {
                "tax_rate": Decimal('0.08'),  # 8% average
                "tax_name": "Sales Tax",
                "applies_to": ["subscription", "one_time"]
            },
            "EU": {
                "tax_rate": Decimal('0.20'),  # 20% VAT
                "tax_name": "VAT",
                "applies_to": ["subscription", "one_time"]
            },
            "UK": {
                "tax_rate": Decimal('0.20'),  # 20% VAT
                "tax_name": "VAT",
                "applies_to": ["subscription", "one_time"]
            }
        }

    async def process_billing_cycle(self, subscription: Subscription) -> Dict[str, Any]:
        """Process billing for subscription cycle"""
        try:
            # Calculate billing amount
            billing_amount = await self._calculate_billing_amount(subscription)
            
            # Calculate taxes
            tax_amount = await self._calculate_taxes(subscription, billing_amount["subtotal"])
            
            # Create invoice
            invoice = await self._create_invoice(subscription, billing_amount, tax_amount)
            
            # Create billing transaction
            transaction = await self._create_billing_transaction(subscription, invoice)
            
            # Process payment
            payment_result = await self._process_payment(subscription, transaction)
            
            billing_result = {
                "subscription_id": subscription.subscription_id,
                "invoice_id": invoice.invoice_id,
                "transaction_id": transaction.transaction_id,
                "amount_charged": float(billing_amount["total"]),
                "tax_amount": float(tax_amount),
                "payment_success": payment_result["success"],
                "next_billing_date": self._calculate_next_billing_date(subscription).isoformat(),
                "processed_at": datetime.utcnow().isoformat()
            }
            
            if not payment_result["success"]:
                billing_result["error"] = payment_result.get("error")
                billing_result["retry_scheduled"] = True
            
            return billing_result
            
        except Exception as e:
            logger.error(f"Billing cycle processing error: {str(e)}")
            raise

    async def _calculate_billing_amount(self, subscription: Subscription) -> Dict[str, Any]:
        """Calculate total billing amount for subscription"""
        base_amount = subscription.price * subscription.quantity
        discount_amount = subscription.discount_amount
        subtotal = base_amount - discount_amount
        
        # Add usage-based charges if applicable
        usage_charges = await self._calculate_usage_charges(subscription)
        subtotal += usage_charges
        
        return {
            "base_amount": float(base_amount),
            "discount_amount": float(discount_amount),
            "usage_charges": float(usage_charges),
            "subtotal": float(subtotal),
            "total": float(subtotal)  # Before tax
        }

    async def _calculate_usage_charges(self, subscription: Subscription) -> Decimal:
        """Calculate usage-based charges"""
        # Mock usage calculation - would integrate with usage tracking
        usage_data = subscription.metadata.get("usage_data", {})
        overage_charges = Decimal('0')
        
        # Example: API call overage
        api_calls = usage_data.get("api_calls", 0)
        api_limit = subscription.metadata.get("api_limit", 10000)
        
        if api_calls > api_limit:
            overage_calls = api_calls - api_limit
            overage_rate = Decimal('0.01')  # $0.01 per extra call
            overage_charges += overage_calls * overage_rate
        
        return overage_charges

    async def _calculate_taxes(self, subscription: Subscription, subtotal: Decimal) -> Decimal:
        """Calculate applicable taxes"""
        customer_country = subscription.metadata.get("billing_country", "US")
        tax_rule = self.tax_rules.get(customer_country, {"tax_rate": Decimal('0')})
        
        tax_rate = tax_rule["tax_rate"]
        tax_amount = subtotal * tax_rate
        
        return tax_amount

    async def _create_invoice(self, subscription: Subscription, billing_amount: Dict[str, Any], 
                            tax_amount: Decimal) -> Invoice:
        """Create invoice for billing cycle"""
        invoice_id = f"inv_{uuid.uuid4().hex[:12]}"
        invoice_number = f"INV-{datetime.utcnow().strftime('%Y%m%d')}-{invoice_id[-6:].upper()}"
        
        total_amount = Decimal(str(billing_amount["total"])) + tax_amount
        
        invoice = Invoice(
            invoice_id=invoice_id,
            subscription_id=subscription.subscription_id,
            customer_id=subscription.customer_id,
            invoice_number=invoice_number,
            amount_due=total_amount,
            amount_paid=Decimal('0'),
            currency=subscription.currency,
            period_start=subscription.current_period_start,
            period_end=subscription.current_period_end,
            line_items=[
                {
                    "description": f"Subscription: {subscription.plan_id}",
                    "quantity": subscription.quantity,
                    "unit_price": float(subscription.price),
                    "amount": billing_amount["base_amount"]
                }
            ],
            tax_details={
                "tax_amount": float(tax_amount),
                "tax_rate": float(self.tax_rules.get(
                    subscription.metadata.get("billing_country", "US"), {}
                ).get("tax_rate", 0))
            }
        )
        
        if billing_amount["discount_amount"] > 0:
            invoice.line_items.append({
                "description": "Discount",
                "quantity": 1,
                "unit_price": -billing_amount["discount_amount"],
                "amount": -billing_amount["discount_amount"]
            })
        
        if billing_amount["usage_charges"] > 0:
            invoice.line_items.append({
                "description": "Usage overage charges",
                "quantity": 1,
                "unit_price": billing_amount["usage_charges"],
                "amount": billing_amount["usage_charges"]
            })
        
        self.invoices[invoice_id] = invoice
        return invoice

    async def _create_billing_transaction(self, subscription: Subscription, invoice: Invoice) -> BillingTransaction:
        """Create billing transaction record"""
        transaction_id = f"btxn_{uuid.uuid4().hex[:12]}"
        
        transaction = BillingTransaction(
            transaction_id=transaction_id,
            subscription_id=subscription.subscription_id,
            customer_id=subscription.customer_id,
            action=BillingAction.CHARGE,
            amount=invoice.amount_due,
            currency=subscription.currency,
            period_start=subscription.current_period_start,
            period_end=subscription.current_period_end,
            invoice_id=invoice.invoice_id,
            description=f"Billing for period {subscription.current_period_start.date()} to {subscription.current_period_end.date()}"
        )
        
        self.billing_transactions[transaction_id] = transaction
        return transaction

    async def _process_payment(self, subscription: Subscription, transaction: BillingTransaction) -> Dict[str, Any]:
        """Process payment for billing transaction"""
        try:
            # Mock payment processing - would integrate with payment gateway
            payment_success = True  # Mock success
            
            if payment_success:
                transaction.status = "completed"
                transaction.processed_at = datetime.utcnow()
                
                # Update invoice
                invoice = self.invoices[transaction.invoice_id]
                invoice.amount_paid = transaction.amount
                invoice.status = "paid"
                invoice.paid_at = datetime.utcnow()
                
                return {
                    "success": True,
                    "payment_transaction_id": f"pay_{uuid.uuid4().hex[:12]}",
                    "processed_at": datetime.utcnow().isoformat()
                }
            else:
                transaction.status = "failed"
                return {
                    "success": False,
                    "error": "Payment processing failed"
                }
                
        except Exception as e:
            logger.error(f"Payment processing error: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }

    def _calculate_next_billing_date(self, subscription: Subscription) -> datetime:
        """Calculate next billing date based on cycle"""
        current_end = subscription.current_period_end
        
        if subscription.billing_cycle == BillingCycle.MONTHLY:
            return current_end + timedelta(days=30)
        elif subscription.billing_cycle == BillingCycle.QUARTERLY:
            return current_end + timedelta(days=90)
        elif subscription.billing_cycle == BillingCycle.ANNUAL:
            return current_end + timedelta(days=365)
        elif subscription.billing_cycle == BillingCycle.WEEKLY:
            return current_end + timedelta(days=7)
        else:
            return current_end + timedelta(days=30)  # Default to monthly

    async def retry_failed_payment(self, transaction_id: str) -> Dict[str, Any]:
        """Retry failed payment transaction"""
        try:
            if transaction_id not in self.billing_transactions:
                raise ValueError(f"Transaction not found: {transaction_id}")
            
            transaction = self.billing_transactions[transaction_id]
            
            if transaction.status != "failed":
                return {
                    "success": False,
                    "error": "Transaction is not in failed status"
                }
            
            # Mock retry payment
            retry_success = True  # Mock success
            
            if retry_success:
                transaction.status = "completed"
                transaction.processed_at = datetime.utcnow()
                
                return {
                    "success": True,
                    "retry_attempt": transaction.metadata.get("retry_count", 0) + 1,
                    "processed_at": datetime.utcnow().isoformat()
                }
            else:
                retry_count = transaction.metadata.get("retry_count", 0) + 1
                transaction.metadata["retry_count"] = retry_count
                
                return {
                    "success": False,
                    "retry_attempt": retry_count,
                    "error": "Retry payment failed"
                }
                
        except Exception as e:
            logger.error(f"Payment retry error: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }

class RevenueAnalytics:
    """Revenue analytics and reporting system"""
    
    def __init__(self):
        self.revenue_records = {}
        self.revenue_metrics = {}
        
        logger.info("Revenue Analytics initialized")

    async def record_revenue(self, revenue_data: Dict[str, Any]) -> str:
        """Record revenue transaction"""
        try:
            record_id = f"rev_{uuid.uuid4().hex[:12]}"
            
            revenue_record = RevenueRecord(
                record_id=record_id,
                customer_id=revenue_data["customer_id"],
                subscription_id=revenue_data.get("subscription_id"),
                revenue_type=RevenueType(revenue_data["revenue_type"]),
                amount=Decimal(str(revenue_data["amount"])),
                currency=revenue_data["currency"],
                recognized_at=datetime.fromisoformat(revenue_data.get("recognized_at", datetime.utcnow().isoformat())),
                billing_period=revenue_data.get("billing_period"),
                commission_rate=Decimal(str(revenue_data["commission_rate"])) if revenue_data.get("commission_rate") else None,
                source_transaction_id=revenue_data.get("source_transaction_id"),
                metadata=revenue_data.get("metadata", {})
            )
            
            self.revenue_records[record_id] = revenue_record
            
            logger.info(f"Revenue recorded: {record_id}")
            return record_id
            
        except Exception as e:
            logger.error(f"Error recording revenue: {str(e)}")
            raise

    async def calculate_mrr(self, as_of_date: Optional[datetime] = None) -> Dict[str, Any]:
        """Calculate Monthly Recurring Revenue (MRR)"""
        try:
            if not as_of_date:
                as_of_date = datetime.utcnow()
            
            # Filter subscription revenue records
            subscription_records = [
                r for r in self.revenue_records.values()
                if r.revenue_type == RevenueType.SUBSCRIPTION and r.recognized_at <= as_of_date
            ]
            
            # Group by customer and subscription
            customer_subscriptions = {}
            for record in subscription_records:
                key = f"{record.customer_id}_{record.subscription_id}"
                if key not in customer_subscriptions:
                    customer_subscriptions[key] = []
                customer_subscriptions[key].append(record)
            
            total_mrr = Decimal('0')
            customer_count = len(customer_subscriptions)
            
            # Calculate MRR for each subscription
            for subscription_records in customer_subscriptions.values():
                # Get latest record for each subscription
                latest_record = max(subscription_records, key=lambda r: r.recognized_at)
                # Convert to monthly amount (assuming monthly billing for simplicity)
                monthly_amount = latest_record.amount
                total_mrr += monthly_amount
            
            arpu = total_mrr / customer_count if customer_count > 0 else Decimal('0')
            
            mrr_analysis = {
                "mrr": float(total_mrr),
                "customer_count": customer_count,
                "arpu": float(arpu),
                "calculated_at": as_of_date.isoformat(),
                "currency": "USD"  # Default currency
            }
            
            return mrr_analysis
            
        except Exception as e:
            logger.error(f"MRR calculation error: {str(e)}")
            raise

    async def calculate_arr(self, as_of_date: Optional[datetime] = None) -> Dict[str, Any]:
        """Calculate Annual Recurring Revenue (ARR)"""
        try:
            mrr_data = await self.calculate_mrr(as_of_date)
            arr = mrr_data["mrr"] * 12
            
            return {
                "arr": arr,
                "mrr": mrr_data["mrr"],
                "customer_count": mrr_data["customer_count"],
                "arpu_annual": mrr_data["arpu"] * 12,
                "calculated_at": mrr_data["calculated_at"],
                "currency": mrr_data["currency"]
            }
            
        except Exception as e:
            logger.error(f"ARR calculation error: {str(e)}")
            raise

    async def analyze_churn(self, period_days: int = 30) -> Dict[str, Any]:
        """Analyze customer churn rate"""
        try:
            end_date = datetime.utcnow()
            start_date = end_date - timedelta(days=period_days)
            
            # Mock churn analysis - would integrate with subscription data
            total_customers_start = 1000  # Mock data
            churned_customers = 50  # Mock data
            new_customers = 80  # Mock data
            total_customers_end = total_customers_start - churned_customers + new_customers
            
            churn_rate = churned_customers / total_customers_start if total_customers_start > 0 else 0
            growth_rate = new_customers / total_customers_start if total_customers_start > 0 else 0
            net_growth_rate = growth_rate - churn_rate
            
            churn_analysis = {
                "period_days": period_days,
                "period_start": start_date.isoformat(),
                "period_end": end_date.isoformat(),
                "customers_start_period": total_customers_start,
                "customers_end_period": total_customers_end,
                "churned_customers": churned_customers,
                "new_customers": new_customers,
                "churn_rate": churn_rate,
                "growth_rate": growth_rate,
                "net_growth_rate": net_growth_rate,
                "calculated_at": datetime.utcnow().isoformat()
            }
            
            return churn_analysis
            
        except Exception as e:
            logger.error(f"Churn analysis error: {str(e)}")
            raise

    async def generate_revenue_report(self, start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        """Generate comprehensive revenue report"""
        try:
            # Filter revenue records for period
            period_records = [
                r for r in self.revenue_records.values()
                if start_date <= r.recognized_at <= end_date
            ]
            
            if not period_records:
                return {
                    "period_start": start_date.isoformat(),
                    "period_end": end_date.isoformat(),
                    "total_revenue": 0,
                    "record_count": 0,
                    "breakdown": {}
                }
            
            # Calculate total revenue
            total_revenue = sum(r.amount for r in period_records)
            
            # Revenue breakdown by type
            revenue_by_type = {}
            for record in period_records:
                revenue_type = record.revenue_type.value
                if revenue_type not in revenue_by_type:
                    revenue_by_type[revenue_type] = {"amount": Decimal('0'), "count": 0}
                revenue_by_type[revenue_type]["amount"] += record.amount
                revenue_by_type[revenue_type]["count"] += 1
            
            # Convert to float for JSON serialization
            for type_data in revenue_by_type.values():
                type_data["amount"] = float(type_data["amount"])
            
            # Revenue breakdown by currency
            revenue_by_currency = {}
            for record in period_records:
                currency = record.currency
                if currency not in revenue_by_currency:
                    revenue_by_currency[currency] = Decimal('0')
                revenue_by_currency[currency] += record.amount
            
            revenue_by_currency = {k: float(v) for k, v in revenue_by_currency.items()}
            
            revenue_report = {
                "period_start": start_date.isoformat(),
                "period_end": end_date.isoformat(),
                "total_revenue": float(total_revenue),
                "record_count": len(period_records),
                "average_transaction": float(total_revenue / len(period_records)),
                "breakdown_by_type": revenue_by_type,
                "breakdown_by_currency": revenue_by_currency,
                "generated_at": datetime.utcnow().isoformat()
            }
            
            return revenue_report
            
        except Exception as e:
            logger.error(f"Revenue report generation error: {str(e)}")
            raise

class SubscriptionManagementCore:
    """Main Subscription Management Core System"""
    
    def __init__(self, level: str = "enterprise"):
        self.version = "2.1.0"
        self.level = level
        self.plan_manager = PlanManager()
        self.billing_engine = BillingEngine()
        self.revenue_analytics = RevenueAnalytics()
        self.subscriptions = {}
        
        logger.info("Subscription Management Core initialized")

    async def create_subscription(self, subscription_data: Dict[str, Any]) -> str:
        """Create new subscription"""
        try:
            subscription_id = f"sub_{uuid.uuid4().hex[:12]}"
            
            # Get plan details
            plan = await self.plan_manager.get_plan(subscription_data["plan_id"])
            if not plan:
                raise ValueError(f"Plan not found: {subscription_data['plan_id']}")
            
            # Calculate trial and billing periods
            current_time = datetime.utcnow()
            trial_end = None
            
            if plan.trial_period_days > 0:
                trial_end = current_time + timedelta(days=plan.trial_period_days)
                current_period_start = current_time
                current_period_end = trial_end
                status = SubscriptionStatus.TRIAL
            else:
                current_period_start = current_time
                current_period_end = self._calculate_period_end(current_time, plan.billing_cycle)
                status = SubscriptionStatus.ACTIVE
            
            # Create subscription
            subscription = Subscription(
                subscription_id=subscription_id,
                customer_id=subscription_data["customer_id"],
                plan_id=plan.plan_id,
                status=status,
                current_period_start=current_period_start,
                current_period_end=current_period_end,
                trial_end=trial_end,
                billing_cycle=plan.billing_cycle,
                price=plan.price,
                currency=plan.currency,
                quantity=subscription_data.get("quantity", 1),
                payment_method_id=subscription_data.get("payment_method_id"),
                next_billing_date=current_period_end if status == SubscriptionStatus.ACTIVE else trial_end,
                metadata=subscription_data.get("metadata", {})
            )
            
            self.subscriptions[subscription_id] = subscription
            
            # Record initial revenue if not trial
            if status == SubscriptionStatus.ACTIVE:
                await self.revenue_analytics.record_revenue({
                    "customer_id": subscription.customer_id,
                    "subscription_id": subscription_id,
                    "revenue_type": "subscription",
                    "amount": float(subscription.price * subscription.quantity),
                    "currency": subscription.currency,
                    "recognized_at": current_time.isoformat(),
                    "billing_period": (current_period_start, current_period_end)
                })
            
            logger.info(f"Subscription created: {subscription_id}")
            return subscription_id
            
        except Exception as e:
            logger.error(f"Error creating subscription: {str(e)}")
            raise

    async def update_subscription(self, subscription_id: str, updates: Dict[str, Any]) -> bool:
        """Update existing subscription"""
        try:
            if subscription_id not in self.subscriptions:
                raise ValueError(f"Subscription not found: {subscription_id}")
            
            subscription = self.subscriptions[subscription_id]
            
            # Handle plan changes
            if "plan_id" in updates:
                new_plan_id = updates["plan_id"]
                await self._change_subscription_plan(subscription, new_plan_id)
            
            # Handle other updates
            if "quantity" in updates:
                subscription.quantity = updates["quantity"]
            if "payment_method_id" in updates:
                subscription.payment_method_id = updates["payment_method_id"]
            if "metadata" in updates:
                subscription.metadata.update(updates["metadata"])
            
            subscription.updated_at = datetime.utcnow()
            
            logger.info(f"Subscription updated: {subscription_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error updating subscription: {str(e)}")
            return False

    async def cancel_subscription(self, subscription_id: str, cancellation_reason: str = "", 
                                immediate: bool = False) -> bool:
        """Cancel subscription"""
        try:
            if subscription_id not in self.subscriptions:
                raise ValueError(f"Subscription not found: {subscription_id}")
            
            subscription = self.subscriptions[subscription_id]
            
            if immediate:
                subscription.status = SubscriptionStatus.CANCELLED
                subscription.cancelled_at = datetime.utcnow()
                subscription.current_period_end = datetime.utcnow()
            else:
                # Cancel at end of current period
                subscription.status = SubscriptionStatus.CANCELLED
                subscription.cancelled_at = datetime.utcnow()
                # Keep current_period_end as is for end-of-period cancellation
            
            subscription.cancellation_reason = cancellation_reason
            subscription.updated_at = datetime.utcnow()
            
            logger.info(f"Subscription cancelled: {subscription_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error cancelling subscription: {str(e)}")
            return False

    async def process_subscription_billing(self, subscription_id: str) -> Dict[str, Any]:
        """Process billing for specific subscription"""
        try:
            if subscription_id not in self.subscriptions:
                raise ValueError(f"Subscription not found: {subscription_id}")
            
            subscription = self.subscriptions[subscription_id]
            
            # Check if billing is due
            if datetime.utcnow() < subscription.next_billing_date:
                return {
                    "success": False,
                    "error": "Billing not due yet",
                    "next_billing_date": subscription.next_billing_date.isoformat()
                }
            
            # Process billing cycle
            billing_result = await self.billing_engine.process_billing_cycle(subscription)
            
            if billing_result["payment_success"]:
                # Update subscription period
                subscription.current_period_start = subscription.current_period_end
                subscription.current_period_end = datetime.fromisoformat(billing_result["next_billing_date"])
                subscription.next_billing_date = subscription.current_period_end
                subscription.updated_at = datetime.utcnow()
                
                # Record revenue
                await self.revenue_analytics.record_revenue({
                    "customer_id": subscription.customer_id,
                    "subscription_id": subscription_id,
                    "revenue_type": "subscription",
                    "amount": billing_result["amount_charged"],
                    "currency": subscription.currency,
                    "recognized_at": datetime.utcnow().isoformat(),
                    "source_transaction_id": billing_result["transaction_id"]
                })
            else:
                # Handle failed payment
                subscription.status = SubscriptionStatus.PAST_DUE
                subscription.updated_at = datetime.utcnow()
            
            return billing_result
            
        except Exception as e:
            logger.error(f"Subscription billing error: {str(e)}")
            raise

    async def get_subscription_analytics(self, customer_id: Optional[str] = None) -> Dict[str, Any]:
        """Get subscription analytics"""
        try:
            # Filter subscriptions
            if customer_id:
                subscriptions = [s for s in self.subscriptions.values() if s.customer_id == customer_id]
            else:
                subscriptions = list(self.subscriptions.values())
            
            if not subscriptions:
                return {
                    "customer_id": customer_id,
                    "total_subscriptions": 0,
                    "analytics": {}
                }
            
            # Calculate analytics
            total_subscriptions = len(subscriptions)
            active_subscriptions = len([s for s in subscriptions if s.status == SubscriptionStatus.ACTIVE])
            trial_subscriptions = len([s for s in subscriptions if s.status == SubscriptionStatus.TRIAL])
            cancelled_subscriptions = len([s for s in subscriptions if s.status == SubscriptionStatus.CANCELLED])
            
            # Revenue analytics
            total_mrr = sum(s.price * s.quantity for s in subscriptions if s.status == SubscriptionStatus.ACTIVE)
            
            # Plan distribution
            plan_distribution = {}
            for subscription in subscriptions:
                plan_id = subscription.plan_id
                if plan_id not in plan_distribution:
                    plan_distribution[plan_id] = 0
                plan_distribution[plan_id] += 1
            
            analytics = {
                "customer_id": customer_id,
                "total_subscriptions": total_subscriptions,
                "active_subscriptions": active_subscriptions,
                "trial_subscriptions": trial_subscriptions,
                "cancelled_subscriptions": cancelled_subscriptions,
                "total_mrr": float(total_mrr),
                "plan_distribution": plan_distribution,
                "generated_at": datetime.utcnow().isoformat()
            }
            
            return analytics
            
        except Exception as e:
            logger.error(f"Subscription analytics error: {str(e)}")
            raise

    def _calculate_period_end(self, start_date: datetime, billing_cycle: BillingCycle) -> datetime:
        """Calculate period end based on billing cycle"""
        if billing_cycle == BillingCycle.MONTHLY:
            return start_date + timedelta(days=30)
        elif billing_cycle == BillingCycle.QUARTERLY:
            return start_date + timedelta(days=90)
        elif billing_cycle == BillingCycle.ANNUAL:
            return start_date + timedelta(days=365)
        elif billing_cycle == BillingCycle.WEEKLY:
            return start_date + timedelta(days=7)
        else:
            return start_date + timedelta(days=30)  # Default to monthly

    async def _change_subscription_plan(self, subscription: Subscription, new_plan_id: str):
        """Handle subscription plan change with proration"""
        try:
            # Get new plan
            new_plan = await self.plan_manager.get_plan(new_plan_id)
            if not new_plan:
                raise ValueError(f"New plan not found: {new_plan_id}")
            
            old_plan = await self.plan_manager.get_plan(subscription.plan_id)
            
            # Calculate proration
            days_remaining = (subscription.current_period_end - datetime.utcnow()).days
            billing_cycle_days = self._get_billing_cycle_days(subscription.billing_cycle)
            
            proration = await self.plan_manager.calculate_proration(
                old_plan, new_plan, days_remaining, billing_cycle_days
            )
            
            # Apply changes
            subscription.plan_id = new_plan.plan_id
            subscription.price = new_plan.price
            subscription.billing_cycle = new_plan.billing_cycle
            
            # Record proration transaction if needed
            if abs(proration["proration_amount"]) >= 1.00:  # Minimum proration threshold
                await self._record_proration_transaction(subscription, proration)
            
        except Exception as e:
            logger.error(f"Plan change error: {str(e)}")
            raise

    def _get_billing_cycle_days(self, billing_cycle: BillingCycle) -> int:
        """Get number of days in billing cycle"""
        cycle_days = {
            BillingCycle.WEEKLY: 7,
            BillingCycle.MONTHLY: 30,
            BillingCycle.QUARTERLY: 90,
            BillingCycle.ANNUAL: 365
        }
        return cycle_days.get(billing_cycle, 30)

    async def _record_proration_transaction(self, subscription: Subscription, proration: Dict[str, Any]):
        """Record proration transaction"""
        transaction_id = f"pro_{uuid.uuid4().hex[:12]}"
        
        proration_transaction = BillingTransaction(
            transaction_id=transaction_id,
            subscription_id=subscription.subscription_id,
            customer_id=subscription.customer_id,
            action=BillingAction.PRORATION,
            amount=Decimal(str(abs(proration["proration_amount"]))),
            currency=subscription.currency,
            period_start=subscription.current_period_start,
            period_end=subscription.current_period_end,
            description=f"Plan change proration: {proration['old_plan_id']} -> {proration['new_plan_id']}",
            metadata=proration
        )
        
        self.billing_engine.billing_transactions[transaction_id] = proration_transaction

    async def get_system_health(self) -> Dict[str, Any]:
        """Get system health and statistics"""
        total_subscriptions = len(self.subscriptions)
        total_plans = len(self.plan_manager.plans)
        total_transactions = len(self.billing_engine.billing_transactions)
        total_invoices = len(self.billing_engine.invoices)
        total_revenue_records = len(self.revenue_analytics.revenue_records)
        
        # Subscription status distribution
        status_distribution = {}
        for subscription in self.subscriptions.values():
            status = subscription.status.value
            status_distribution[status] = status_distribution.get(status, 0) + 1
        
        return {
            "version": self.version,
            "total_subscriptions": total_subscriptions,
            "total_plans": total_plans,
            "total_billing_transactions": total_transactions,
            "total_invoices": total_invoices,
            "total_revenue_records": total_revenue_records,
            "subscription_status_distribution": status_distribution,
            "system_status": "healthy",
            "last_health_check": datetime.utcnow().isoformat()
        }

# Global instance
subscription_management_core = SubscriptionManagementCore()

# Export main functions
__all__ = [
    "SubscriptionStatus",
    "BillingCycle",
    "SubscriptionTier",
    "BillingAction",
    "RevenueType",
    "SubscriptionPlan",
    "Subscription",
    "BillingTransaction",
    "Invoice",
    "RevenueRecord",
    "SubscriptionManagementCore",
    "subscription_management_core"
]

if __name__ == "__main__":
    logger.info("Subscription Management Core module loaded successfully")