"""Ainflue Core Billing Engine - Enterprise Billing & Invoicing System
===================================================================

Advanced billing engine providing subscription billing, usage-based billing,
invoice generation, tax calculation, revenue recognition, and financial
reporting for the Ainflue platform payment core.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Union, Tuple
from dataclasses import dataclass, field
from enum import Enum
from decimal import Decimal, ROUND_HALF_UP
import time
import uuid
from datetime import datetime, timedelta
import json

logger = logging.getLogger(__name__)

class BillingModel(str, Enum):
    """Billing models"""
    SUBSCRIPTION = "subscription"
    USAGE_BASED = "usage_based"
    HYBRID = "hybrid"
    ONE_TIME = "one_time"
    TIERED = "tiered"
    VOLUME = "volume"
    METERED = "metered"

class BillingPeriod(str, Enum):
    """Billing periods"""
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    ANNUALLY = "annually"
    ON_DEMAND = "on_demand"

class InvoiceStatus(str, Enum):
    """Invoice status"""
    DRAFT = "draft"
    PENDING = "pending"
    SENT = "sent"
    PAID = "paid"
    OVERDUE = "overdue"
    CANCELLED = "cancelled"
    REFUNDED = "refunded"

class PaymentStatus(str, Enum):
    """Payment status"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    REFUNDED = "refunded"

@dataclass
class BillingPlan:
    """Billing plan configuration"""
    plan_id: str
    name: str
    billing_model: BillingModel
    billing_period: BillingPeriod
    base_price: Decimal
    currency: str = "USD"
    trial_period_days: int = 0
    setup_fee: Decimal = Decimal("0.00")
    is_active: bool = True
    metadata: Dict[str, Any] = field(default_factory=dict)
    usage_limits: Dict[str, int] = field(default_factory=dict)
    overage_rates: Dict[str, Decimal] = field(default_factory=dict)

@dataclass
class Subscription:
    """Customer subscription"""
    subscription_id: str
    customer_id: str
    plan_id: str
    status: str
    current_period_start: datetime
    current_period_end: datetime
    trial_end: Optional[datetime] = None
    cancelled_at: Optional[datetime] = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = field(default_factory=dict)
    discount_percent: Decimal = Decimal("0.00")
    usage_data: Dict[str, int] = field(default_factory=dict)

@dataclass
class InvoiceItem:
    """Invoice line item"""
    item_id: str
    description: str
    quantity: Decimal
    unit_price: Decimal
    amount: Decimal
    currency: str = "USD"
    item_type: str = "charge"
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class Invoice:
    """Customer invoice"""
    invoice_id: str
    customer_id: str
    subscription_id: Optional[str]
    status: InvoiceStatus
    amount_due: Decimal
    amount_paid: Decimal
    currency: str
    due_date: datetime
    issued_date: datetime
    paid_date: Optional[datetime] = None
    items: List[InvoiceItem] = field(default_factory=list)
    tax_amount: Decimal = Decimal("0.00")
    discount_amount: Decimal = Decimal("0.00")
    subtotal: Decimal = Decimal("0.00")
    total: Decimal = Decimal("0.00")
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class Payment:
    """Payment record"""
    payment_id: str
    invoice_id: str
    customer_id: str
    amount: Decimal
    currency: str
    status: PaymentStatus
    payment_method: str
    gateway_transaction_id: Optional[str] = None
    processed_at: Optional[datetime] = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class BillingMetrics:
    """Billing engine metrics"""
    invoices_generated: int = 0
    invoices_paid: int = 0
    invoices_overdue: int = 0
    total_revenue: Decimal = Decimal("0.00")
    monthly_recurring_revenue: Decimal = Decimal("0.00")
    annual_recurring_revenue: Decimal = Decimal("0.00")
    average_revenue_per_user: Decimal = Decimal("0.00")
    churn_rate: Decimal = Decimal("0.00")
    active_subscriptions: int = 0
    failed_payments: int = 0
    successful_payments: int = 0
    revenue_recognition: Decimal = Decimal("0.00")
    last_health_check: float = field(default_factory=time.time)

class BillingEngineCore:
    """Enterprise billing engine core management system"""
    
    def __init__(self, level -> None: str = "enterprise") -> None:
        """Initialize billing engine core"""
        self.level = level
        self.metrics = BillingMetrics()
        self.start_time = time.time()
        
        # Data storage
        self.billing_plans: Dict[str, BillingPlan] = {}
        self.subscriptions: Dict[str, Subscription] = {}
        self.invoices: Dict[str, Invoice] = {}
        self.payments: Dict[str, Payment] = {}
        self.customers: Dict[str, Dict[str, Any]] = {}
        
        # Configuration
        self.tax_rates: Dict[str, Decimal] = {
            "US": Decimal("0.08"),  # 8% average
            "EU": Decimal("0.20"),  # 20% VAT
            "UK": Decimal("0.20"),  # 20% VAT
            "CA": Decimal("0.13"),  # 13% HST
            "DEFAULT": Decimal("0.00")
        }
        
        # Processing state
        self.invoice_queue: List[str] = []
        self.payment_queue: List[str] = []
        
        # Health monitoring
        self._health_monitor_task: Optional[asyncio.Task] = None
        self._billing_processor_task: Optional[asyncio.Task] = None
        self._shutdown_event = asyncio.Event()
        
        logger.info("💰 Billing Engine Core initialized")
    
    async def initialize(self) -> bool:
        """Initialize billing engine"""
        try:
            logger.info("🚀 Initializing billing engine core")
            
            # Create default billing plans
            await self._create_default_plans()
            
            logger.info("✅ Billing engine core initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"❌ Billing engine initialization failed: {str(e)}")
            return False
    
    async def _create_default_plans(self) -> None:
        """Create default billing plans"""
        default_plans = [
            BillingPlan(
                plan_id="basic_monthly",
                name="Basic Monthly",
                billing_model=BillingModel.SUBSCRIPTION,
                billing_period=BillingPeriod.MONTHLY,
                base_price=Decimal("29.99"),
                usage_limits={"api_calls": 10000, "storage_gb": 10}
            ),
            BillingPlan(
                plan_id="pro_monthly",
                name="Pro Monthly",
                billing_model=BillingModel.HYBRID,
                billing_period=BillingPeriod.MONTHLY,
                base_price=Decimal("99.99"),
                usage_limits={"api_calls": 100000, "storage_gb": 100},
                overage_rates={"api_calls": Decimal("0.001"), "storage_gb": Decimal("0.50")}
            ),
            BillingPlan(
                plan_id="enterprise_annual",
                name="Enterprise Annual",
                billing_model=BillingModel.SUBSCRIPTION,
                billing_period=BillingPeriod.ANNUALLY,
                base_price=Decimal("2999.00"),
                usage_limits={"api_calls": -1, "storage_gb": -1}  # Unlimited
            )
        ]
        
        for plan in default_plans:
            self.billing_plans[plan.plan_id] = plan
    
    async def start(self) -> bool:
        """Start billing engine"""
        try:
            if not hasattr(self, '_initialized'):
                await self.initialize()
                self._initialized = True
            
            # Start background processors
            self._health_monitor_task = asyncio.create_task(self._health_monitor_loop())
            self._billing_processor_task = asyncio.create_task(self._billing_processor_loop())
            
            logger.info("🚀 Billing engine core started successfully")
            return True
            
        except Exception as e:
            logger.error(f"❌ Billing engine start failed: {str(e)}")
            return False
    
    async def stop(self) -> bool:
        """Stop billing engine"""
        try:
            logger.info("🛑 Stopping billing engine core")
            
            # Signal shutdown
            self._shutdown_event.set()
            
            # Cancel background tasks
            for task in [self._health_monitor_task, self._billing_processor_task]:
                if task:
                    task.cancel()
                    try:
                        await task
                    except asyncio.CancelledError:
                        pass
            
            logger.info("✅ Billing engine core stopped successfully")
            return True
            
        except Exception as e:
            logger.error(f"❌ Billing engine stop failed: {str(e)}")
            return False
    
    async def create_subscription(self, customer_id: str, plan_id: str, 
                                 metadata: Optional[Dict[str, Any]] = None) -> Optional[str]:
        """Create customer subscription"""
        try:
            if plan_id not in self.billing_plans:
                logger.error(f"Billing plan '{plan_id}' not found")
                return None
            
            plan = self.billing_plans[plan_id]
            subscription_id = str(uuid.uuid4())
            
            # Calculate billing period dates
            now = datetime.utcnow()
            if plan.billing_period == BillingPeriod.MONTHLY:
                period_end = now + timedelta(days=30)
            elif plan.billing_period == BillingPeriod.ANNUALLY:
                period_end = now + timedelta(days=365)
            elif plan.billing_period == BillingPeriod.WEEKLY:
                period_end = now + timedelta(days=7)
            else:
                period_end = now + timedelta(days=30)  # Default
            
            # Trial period
            trial_end = None
            if plan.trial_period_days > 0:
                trial_end = now + timedelta(days=plan.trial_period_days)
                period_end = trial_end
            
            subscription = Subscription(
                subscription_id=subscription_id,
                customer_id=customer_id,
                plan_id=plan_id,
                status="active",
                current_period_start=now,
                current_period_end=period_end,
                trial_end=trial_end,
                metadata=metadata or {}
            )
            
            self.subscriptions[subscription_id] = subscription
            self.metrics.active_subscriptions += 1
            
            # Generate initial invoice (if not in trial)
            if trial_end is None:
                await self._generate_subscription_invoice(subscription_id)
            
            logger.info(f"📋 Created subscription '{subscription_id}' for customer '{customer_id}'")
            return subscription_id
            
        except Exception as e:
            logger.error(f"Subscription creation failed: {str(e)}")
            return None
    
    async def _generate_subscription_invoice(self, subscription_id: str) -> Optional[str]:
        """Generate invoice for subscription"""
        try:
            subscription = self.subscriptions.get(subscription_id)
            if not subscription:
                return None
            
            plan = self.billing_plans.get(subscription.plan_id)
            if not plan:
                return None
            
            invoice_id = str(uuid.uuid4())
            
            # Create invoice items
            items = []
            
            # Base subscription charge
            base_item = InvoiceItem(
                item_id=str(uuid.uuid4()),
                description=f"{plan.name} - {plan.billing_period.value}",
                quantity=Decimal("1"),
                unit_price=plan.base_price,
                amount=plan.base_price
            )
            items.append(base_item)
            
            # Setup fee (if applicable)
            if plan.setup_fee > 0:
                setup_item = InvoiceItem(
                    item_id=str(uuid.uuid4()),
                    description="Setup Fee",
                    quantity=Decimal("1"),
                    unit_price=plan.setup_fee,
                    amount=plan.setup_fee
                )
                items.append(setup_item)
            
            # Usage-based charges
            if plan.billing_model in [BillingModel.USAGE_BASED, BillingModel.HYBRID]:
                usage_items = self._calculate_usage_charges(subscription, plan)
                items.extend(usage_items)
            
            # Calculate totals
            subtotal = sum(item.amount for item in items)
            discount_amount = subtotal * subscription.discount_percent / 100
            tax_amount = self._calculate_tax(subscription.customer_id, subtotal - discount_amount)
            total = subtotal - discount_amount + tax_amount
            
            # Create invoice
            invoice = Invoice(
                invoice_id=invoice_id,
                customer_id=subscription.customer_id,
                subscription_id=subscription_id,
                status=InvoiceStatus.PENDING,
                amount_due=total,
                amount_paid=Decimal("0.00"),
                currency=plan.currency,
                due_date=datetime.utcnow() + timedelta(days=30),
                issued_date=datetime.utcnow(),
                items=items,
                tax_amount=tax_amount,
                discount_amount=discount_amount,
                subtotal=subtotal,
                total=total
            )
            
            self.invoices[invoice_id] = invoice
            self.metrics.invoices_generated += 1
            
            # Add to processing queue
            self.invoice_queue.append(invoice_id)
            
            logger.info(f"🧾 Generated invoice '{invoice_id}' for subscription '{subscription_id}'")
            return invoice_id
            
        except Exception as e:
            logger.error(f"Invoice generation failed: {str(e)}")
            return None
    
    def _calculate_usage_charges(self, subscription: Subscription, plan: BillingPlan) -> List[InvoiceItem]:
        """Calculate usage-based charges"""
        items = []
        
        for usage_type, usage_amount in subscription.usage_data.items():
            limit = plan.usage_limits.get(usage_type, 0)
            overage_rate = plan.overage_rates.get(usage_type, Decimal("0.00"))
            
            if limit > 0 and usage_amount > limit and overage_rate > 0:
                overage_amount = usage_amount - limit
                overage_charge = Decimal(str(overage_amount)) * overage_rate
                
                item = InvoiceItem(
                    item_id=str(uuid.uuid4()),
                    description=f"Overage - {usage_type} ({overage_amount} units)",
                    quantity=Decimal(str(overage_amount)),
                    unit_price=overage_rate,
                    amount=overage_charge,
                    item_type="overage"
                )
                items.append(item)
        
        return items
    
    def _calculate_tax(self, customer_id: str, amount: Decimal) -> Decimal:
        """Calculate tax amount"""
        try:
            # Get customer's tax location (simplified)
            customer = self.customers.get(customer_id, {})
            country = customer.get("country", "DEFAULT")
            
            tax_rate = self.tax_rates.get(country, self.tax_rates["DEFAULT"])
            return (amount * tax_rate).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
            
        except Exception as e:
            logger.error(f"Tax calculation failed: {str(e)}")
            return Decimal("0.00")
    
    async def process_payment(self, invoice_id: str, payment_method: str, 
                            gateway_transaction_id: Optional[str] = None) -> Optional[str]:
        """Process payment for invoice"""
        try:
            invoice = self.invoices.get(invoice_id)
            if not invoice:
                logger.error(f"Invoice '{invoice_id}' not found")
                return None
            
            if invoice.status != InvoiceStatus.PENDING:
                logger.error(f"Invoice '{invoice_id}' is not pending")
                return None
            
            payment_id = str(uuid.uuid4())
            
            # Create payment record
            payment = Payment(
                payment_id=payment_id,
                invoice_id=invoice_id,
                customer_id=invoice.customer_id,
                amount=invoice.amount_due,
                currency=invoice.currency,
                status=PaymentStatus.PROCESSING,
                payment_method=payment_method,
                gateway_transaction_id=gateway_transaction_id
            )
            
            self.payments[payment_id] = payment
            
            # Simulate payment processing
            await asyncio.sleep(0.1)  # Simulate processing delay
            
            # Update payment status (simplified - always succeeds)
            payment.status = PaymentStatus.COMPLETED
            payment.processed_at = datetime.utcnow()
            
            # Update invoice
            invoice.status = InvoiceStatus.PAID
            invoice.amount_paid = invoice.amount_due
            invoice.paid_date = datetime.utcnow()
            
            # Update metrics
            self.metrics.invoices_paid += 1
            self.metrics.successful_payments += 1
            self.metrics.total_revenue += payment.amount
            
            logger.info(f"💳 Processed payment '{payment_id}' for invoice '{invoice_id}'")
            return payment_id
            
        except Exception as e:
            logger.error(f"Payment processing failed: {str(e)}")
            self.metrics.failed_payments += 1
            return None
    
    async def record_usage(self, subscription_id: str, usage_type: str, amount: int) -> bool:
        """Record usage for subscription"""
        try:
            subscription = self.subscriptions.get(subscription_id)
            if not subscription:
                return False
            
            subscription.usage_data[usage_type] = subscription.usage_data.get(usage_type, 0) + amount
            return True
            
        except Exception as e:
            logger.error(f"Usage recording failed: {str(e)}")
            return False
    
    async def cancel_subscription(self, subscription_id: str, reason: str = "") -> bool:
        """Cancel subscription"""
        try:
            subscription = self.subscriptions.get(subscription_id)
            if not subscription:
                return False
            
            subscription.status = "cancelled"
            subscription.cancelled_at = datetime.utcnow()
            subscription.metadata["cancellation_reason"] = reason
            
            self.metrics.active_subscriptions -= 1
            
            logger.info(f"❌ Cancelled subscription '{subscription_id}'")
            return True
            
        except Exception as e:
            logger.error(f"Subscription cancellation failed: {str(e)}")
            return False
    
    async def _billing_processor_loop(self) -> None:
        """Background billing processor"""
        while not self._shutdown_event.is_set():
            try:
                # Process pending invoices
                await self._process_pending_invoices()
                
                # Check for subscription renewals
                await self._check_subscription_renewals()
                
                # Update metrics
                await self._update_billing_metrics()
                
                await asyncio.sleep(3600)  # Process every hour
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Billing processor error: {str(e)}")
                await asyncio.sleep(1800)  # Wait 30 minutes on error
    
    async def _process_pending_invoices(self) -> None:
        """Process pending invoices"""
        current_time = datetime.utcnow()
        
        for invoice_id, invoice in self.invoices.items():
            if invoice.status == InvoiceStatus.PENDING and invoice.due_date < current_time:
                invoice.status = InvoiceStatus.OVERDUE
                self.metrics.invoices_overdue += 1
    
    async def _check_subscription_renewals(self) -> None:
        """Check for subscription renewals"""
        current_time = datetime.utcnow()
        
        for subscription in self.subscriptions.values():
            if (subscription.status == "active" and 
                subscription.current_period_end <= current_time):
                
                # Renew subscription
                await self._renew_subscription(subscription.subscription_id)
    
    async def _renew_subscription(self, subscription_id: str) -> bool:
        """Renew subscription"""
        try:
            subscription = self.subscriptions.get(subscription_id)
            if not subscription:
                return False
            
            plan = self.billing_plans.get(subscription.plan_id)
            if not plan:
                return False
            
            # Update subscription period
            if plan.billing_period == BillingPeriod.MONTHLY:
                subscription.current_period_end += timedelta(days=30)
            elif plan.billing_period == BillingPeriod.ANNUALLY:
                subscription.current_period_end += timedelta(days=365)
            else:
                subscription.current_period_end += timedelta(days=30)
            
            subscription.current_period_start = datetime.utcnow()
            
            # Reset usage data
            subscription.usage_data = {}
            
            # Generate renewal invoice
            await self._generate_subscription_invoice(subscription_id)
            
            logger.info(f"🔄 Renewed subscription '{subscription_id}'")
            return True
            
        except Exception as e:
            logger.error(f"Subscription renewal failed: {str(e)}")
            return False
    
    async def _update_billing_metrics(self) -> None:
        """Update billing metrics"""
        try:
            # Calculate MRR and ARR
            monthly_revenue = Decimal("0.00")
            for subscription in self.subscriptions.values():
                if subscription.status == "active":
                    plan = self.billing_plans.get(subscription.plan_id)
                    if plan:
                        if plan.billing_period == BillingPeriod.MONTHLY:
                            monthly_revenue += plan.base_price
                        elif plan.billing_period == BillingPeriod.ANNUALLY:
                            monthly_revenue += plan.base_price / 12
            
            self.metrics.monthly_recurring_revenue = monthly_revenue
            self.metrics.annual_recurring_revenue = monthly_revenue * 12
            
            # Calculate ARPU
            active_customers = len(set(s.customer_id for s in self.subscriptions.values() if s.status == "active"))
            if active_customers > 0:
                self.metrics.average_revenue_per_user = monthly_revenue / active_customers
            
        except Exception as e:
            logger.error(f"Metrics update failed: {str(e)}")
    
    async def health_check(self) -> bool:
        """Perform billing engine health check"""
        try:
            # Check data consistency
            if len(self.billing_plans) == 0:
                return False
            
            # Update metrics
            self.metrics.last_health_check = time.time()
            
            return True
            
        except Exception as e:
            logger.error(f"Billing engine health check failed: {str(e)}")
            return False
    
    async def _health_monitor_loop(self) -> None:
        """Health monitoring loop"""
        while not self._shutdown_event.is_set():
            try:
                await self.health_check()
                await asyncio.sleep(300)  # Check every 5 minutes
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Billing health monitor error: {str(e)}")
                await asyncio.sleep(600)
    
    def get_metrics_summary(self) -> Dict[str, Any]:
        """Get billing metrics summary"""
        return {
            "total_revenue": float(self.metrics.total_revenue),
            "monthly_recurring_revenue": float(self.metrics.monthly_recurring_revenue),
            "annual_recurring_revenue": float(self.metrics.annual_recurring_revenue),
            "average_revenue_per_user": float(self.metrics.average_revenue_per_user),
            "active_subscriptions": self.metrics.active_subscriptions,
            "invoices_generated": self.metrics.invoices_generated,
            "invoices_paid": self.metrics.invoices_paid,
            "invoices_overdue": self.metrics.invoices_overdue,
            "successful_payments": self.metrics.successful_payments,
            "failed_payments": self.metrics.failed_payments,
            "payment_success_rate": (
                self.metrics.successful_payments / 
                max(self.metrics.successful_payments + self.metrics.failed_payments, 1) * 100
            ),
            "billing_plans": len(self.billing_plans)
        }
    
    def get_invoice(self, invoice_id: str) -> Optional[Dict[str, Any]]:
        """Get invoice details"""
        invoice = self.invoices.get(invoice_id)
        if not invoice:
            return None
        
        return {
            "invoice_id": invoice.invoice_id,
            "customer_id": invoice.customer_id,
            "status": invoice.status.value,
            "amount_due": float(invoice.amount_due),
            "amount_paid": float(invoice.amount_paid),
            "currency": invoice.currency,
            "due_date": invoice.due_date.isoformat(),
            "issued_date": invoice.issued_date.isoformat(),
            "items": [
                {
                    "description": item.description,
                    "quantity": float(item.quantity),
                    "unit_price": float(item.unit_price),
                    "amount": float(item.amount)
                }
                for item in invoice.items
            ],
            "subtotal": float(invoice.subtotal),
            "tax_amount": float(invoice.tax_amount),
            "discount_amount": float(invoice.discount_amount),
            "total": float(invoice.total)
        }

# Module exports
__all__ = [
    "BillingEngineCore", "BillingPlan", "Subscription", "Invoice", "Payment",
    "BillingModel", "BillingPeriod", "InvoiceStatus", "PaymentStatus", "BillingMetrics"
]