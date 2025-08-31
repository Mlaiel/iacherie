"""
Billing Management Database Model

Enterprise-grade SQLAlchemy model for comprehensive billing management,
invoice generation, payment processing, and financial compliance.

Author: Fahed Mlaiel <mlaiel@live.de>
Project: IA Influencer Agent + Content Protection Platform
Copyright: All rights reserved. Unauthorized use, modification, or distribution prohibited.

 INTELLECTUAL PROPERTY WARNING: This code, concept, and architecture are 
the exclusive intellectual property of Fahed Mlaiel (mlaiel@live.de). 
Any use, copying, distribution, or exploitation without explicit written 
authorization is STRICTLY PROHIBITED and will be prosecuted.

Expert Project Team - Fahed Mlaiel:
- Lead AI Developer & Software Architect
- Senior Backend Engineer (Python/FastAPI/Django)  
- Machine Learning Engineer (TensorFlow/PyTorch/Hugging Face)
- Database Administrator & Data Engineer (PostgreSQL/Redis/MongoDB)
- Backend Security Specialist
- Microservices Architect
- Audio Processing Engineer
- DevOps Engineer
- AI Prompt Engineer
"""

from sqlalchemy import Column, String, Text, DateTime, Float, Integer, Boolean, JSON, ForeignKey, Index, Enum as SQLEnum, ARRAY, Numeric
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID, JSONB
from datetime import datetime, timezone, timedelta
from decimal import Decimal
from enum import Enum
import uuid
from typing import Dict, Any, List, Optional

Base = declarative_base()


class BillingStatus(Enum):
    """Billing status enumeration"""
    ACTIVE = "active"
    SUSPENDED = "suspended"
    CANCELLED = "cancelled"
    PENDING_SETUP = "pending_setup"
    PAST_DUE = "past_due"
    FAILED = "failed"
    TRIAL = "trial"
    FREE = "free"
    GRACE_PERIOD = "grace_period"


class InvoiceStatus(Enum):
    """Invoice status enumeration"""
    DRAFT = "draft"
    PENDING = "pending"
    SENT = "sent"
    PAID = "paid"
    PARTIALLY_PAID = "partially_paid"
    OVERDUE = "overdue"
    CANCELLED = "cancelled"
    REFUNDED = "refunded"
    DISPUTED = "disputed"
    WRITTEN_OFF = "written_off"


class PaymentStatus(Enum):
    """Payment status enumeration"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    REFUNDED = "refunded"
    PARTIALLY_REFUNDED = "partially_refunded"
    DISPUTED = "disputed"
    CHARGEBACK = "chargeback"


class PaymentMethod(Enum):
    """Payment method enumeration"""
    CREDIT_CARD = "credit_card"
    DEBIT_CARD = "debit_card"
    BANK_TRANSFER = "bank_transfer"
    PAYPAL = "paypal"
    STRIPE = "stripe"
    WIRE_TRANSFER = "wire_transfer"
    CHECK = "check"
    CRYPTOCURRENCY = "cryptocurrency"
    APPLE_PAY = "apple_pay"
    GOOGLE_PAY = "google_pay"
    ACH = "ach"
    SEPA = "sepa"


class Currency(Enum):
    """Currency enumeration"""
    USD = "USD"
    EUR = "EUR"
    GBP = "GBP"
    JPY = "JPY"
    CAD = "CAD"
    AUD = "AUD"
    CHF = "CHF"
    CNY = "CNY"
    INR = "INR"
    BRL = "BRL"
    SEK = "SEK"
    NOK = "NOK"
    DKK = "DKK"
    PLN = "PLN"
    CZK = "CZK"


class BillingCycle(Enum):
    """Billing cycle enumeration"""
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    SEMI_ANNUALLY = "semi_annually"
    ANNUALLY = "annually"
    WEEKLY = "weekly"
    DAILY = "daily"
    ONE_TIME = "one_time"
    USAGE_BASED = "usage_based"
    CUSTOM = "custom"


class InvoiceType(Enum):
    """Invoice type enumeration"""
    SUBSCRIPTION = "subscription"
    USAGE = "usage"
    ONE_TIME = "one_time"
    CREDIT = "credit"
    REFUND = "refund"
    ADJUSTMENT = "adjustment"
    LATE_FEE = "late_fee"
    SETUP_FEE = "setup_fee"
    CANCELLATION_FEE = "cancellation_fee"


class TaxType(Enum):
    """Tax type enumeration"""
    VAT = "vat"
    GST = "gst"
    SALES_TAX = "sales_tax"
    WITHHOLDING_TAX = "withholding_tax"
    REVERSE_CHARGE = "reverse_charge"
    EXEMPT = "exempt"
    ZERO_RATED = "zero_rated"


class DiscountType(Enum):
    """Discount type enumeration"""
    PERCENTAGE = "percentage"
    FIXED_AMOUNT = "fixed_amount"
    FREE_TRIAL = "free_trial"
    PROMOTIONAL = "promotional"
    LOYALTY = "loyalty"
    VOLUME = "volume"
    EARLY_BIRD = "early_bird"
    COUPON = "coupon"


class ComplianceStandard(Enum):
    """Compliance standard enumeration"""
    PCI_DSS = "pci_dss"
    SOX = "sox"
    GDPR = "gdpr"
    CCPA = "ccpa"
    HIPAA = "hipaa"
    ISO_27001 = "iso_27001"
    SOC_2 = "soc_2"
    PSD2 = "psd2"


class BillingManagement(Base):
    """
    Enterprise Billing Management Model
    
    Comprehensive billing management with subscription handling,
    invoice generation, payment processing, and compliance tracking.
    """
    __tablename__ = 'billing_management'
    
    # Primary identification
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    billing_id = Column(String(100), unique=True, nullable=False, index=True)
    
    # Customer information
    customer_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    organization_id = Column(UUID(as_uuid=True), nullable=True, index=True)
    billing_contact_id = Column(UUID(as_uuid=True), nullable=True, index=True)
    
    # Billing configuration
    status = Column(SQLEnum(BillingStatus), nullable=False, default=BillingStatus.PENDING_SETUP, index=True)
    billing_cycle = Column(SQLEnum(BillingCycle), nullable=False, default=BillingCycle.MONTHLY, index=True)
    currency = Column(SQLEnum(Currency), nullable=False, default=Currency.USD, index=True)
    timezone = Column(String(50), nullable=False, default="UTC")
    
    # Subscription details
    subscription_plan_id = Column(String(100), nullable=True, index=True)
    subscription_start_date = Column(DateTime(timezone=True), nullable=True, index=True)
    subscription_end_date = Column(DateTime(timezone=True), nullable=True, index=True)
    trial_start_date = Column(DateTime(timezone=True), nullable=True)
    trial_end_date = Column(DateTime(timezone=True), nullable=True)
    is_trial = Column(Boolean, nullable=False, default=False)
    
    # Payment information
    primary_payment_method = Column(SQLEnum(PaymentMethod), nullable=True, index=True)
    payment_processor = Column(String(100), nullable=True)
    payment_method_token = Column(String(255), nullable=True)  # Encrypted
    automatic_payment = Column(Boolean, nullable=False, default=True)
    payment_terms_days = Column(Integer, nullable=False, default=30)
    
    # Pricing and amounts
    base_amount = Column(Numeric(10, 2), nullable=False, default=0.00)
    recurring_amount = Column(Numeric(10, 2), nullable=False, default=0.00)
    usage_amount = Column(Numeric(10, 2), nullable=False, default=0.00)
    discount_amount = Column(Numeric(10, 2), nullable=False, default=0.00)
    tax_amount = Column(Numeric(10, 2), nullable=False, default=0.00)
    total_amount = Column(Numeric(10, 2), nullable=False, default=0.00)
    
    # Billing dates
    next_billing_date = Column(DateTime(timezone=True), nullable=True, index=True)
    last_billing_date = Column(DateTime(timezone=True), nullable=True, index=True)
    created_at = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc), index=True)
    updated_at = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    
    # Usage tracking
    current_usage = Column(JSONB, nullable=True)
    usage_limits = Column(JSONB, nullable=True)
    usage_alerts = Column(JSONB, nullable=True)
    overage_charges = Column(Numeric(10, 2), nullable=False, default=0.00)
    usage_reset_date = Column(DateTime(timezone=True), nullable=True)
    
    # Tax configuration
    tax_rate = Column(Numeric(5, 4), nullable=False, default=0.0000)
    tax_type = Column(SQLEnum(TaxType), nullable=True)
    tax_exempt = Column(Boolean, nullable=False, default=False)
    tax_id = Column(String(100), nullable=True)
    tax_region = Column(String(100), nullable=True)
    reverse_charge = Column(Boolean, nullable=False, default=False)
    
    # Discount and promotional codes
    active_discounts = Column(JSONB, nullable=True)
    promotional_codes = Column(ARRAY(String), nullable=True)
    loyalty_credits = Column(Numeric(10, 2), nullable=False, default=0.00)
    referral_credits = Column(Numeric(10, 2), nullable=False, default=0.00)
    
    # Billing address and contact
    billing_address = Column(JSONB, nullable=True)
    billing_email = Column(String(255), nullable=True)
    billing_phone = Column(String(50), nullable=True)
    invoice_delivery_method = Column(String(20), nullable=False, default="email")
    
    # Payment history and statistics
    total_paid = Column(Numeric(12, 2), nullable=False, default=0.00)
    total_outstanding = Column(Numeric(12, 2), nullable=False, default=0.00)
    payment_failure_count = Column(Integer, nullable=False, default=0)
    last_payment_date = Column(DateTime(timezone=True), nullable=True)
    last_payment_amount = Column(Numeric(10, 2), nullable=True)
    last_payment_method = Column(SQLEnum(PaymentMethod), nullable=True)
    
    # Dunning and collection
    dunning_level = Column(Integer, nullable=False, default=0)
    last_dunning_date = Column(DateTime(timezone=True), nullable=True)
    collection_status = Column(String(50), nullable=True)
    collection_notes = Column(Text, nullable=True)
    
    # Financial metrics
    customer_lifetime_value = Column(Numeric(12, 2), nullable=True)
    average_revenue_per_user = Column(Numeric(10, 2), nullable=True)
    monthly_recurring_revenue = Column(Numeric(10, 2), nullable=True)
    annual_recurring_revenue = Column(Numeric(12, 2), nullable=True)
    churn_risk_score = Column(Float, nullable=True)
    
    # Integration and external systems
    external_billing_id = Column(String(255), nullable=True)
    accounting_system_id = Column(String(255), nullable=True)
    crm_system_id = Column(String(255), nullable=True)
    external_references = Column(JSONB, nullable=True)
    
    # Compliance and legal
    compliance_requirements = Column(ARRAY(SQLEnum(ComplianceStandard)), nullable=True)
    data_retention_years = Column(Integer, nullable=False, default=7)
    audit_trail = Column(JSONB, nullable=True)
    legal_entity = Column(String(255), nullable=True)
    contract_reference = Column(String(255), nullable=True)
    
    # Automation and AI features
    automated_billing = Column(Boolean, nullable=False, default=True)
    payment_retry_enabled = Column(Boolean, nullable=False, default=True)
    smart_dunning = Column(Boolean, nullable=False, default=True)
    fraud_detection = Column(Boolean, nullable=False, default=True)
    predictive_analytics = Column(Boolean, nullable=False, default=False)
    
    # Notifications and alerts
    billing_notifications = Column(JSONB, nullable=True)
    payment_reminder_settings = Column(JSONB, nullable=True)
    escalation_procedures = Column(JSONB, nullable=True)
    
    # Customization
    custom_fields = Column(JSONB, nullable=True)
    invoice_template = Column(String(100), nullable=True)
    branding_settings = Column(JSONB, nullable=True)
    
    # Metadata
    metadata = Column(JSONB, nullable=True)
    tags = Column(ARRAY(String), nullable=True)
    notes = Column(Text, nullable=True)
    
    # Advanced indexing
    __table_args__ = (
        Index('idx_billing_management_customer_status', 'customer_id', 'status'),
        Index('idx_billing_management_billing_cycle', 'billing_cycle', 'next_billing_date'),
        Index('idx_billing_management_subscription', 'subscription_plan_id', 'subscription_start_date'),
        Index('idx_billing_management_payment_method', 'primary_payment_method', 'automatic_payment'),
        Index('idx_billing_management_trial', 'is_trial', 'trial_end_date'),
        Index('idx_billing_management_amounts', 'total_amount', 'total_outstanding'),
        Index('idx_billing_management_organization', 'organization_id'),
        Index('idx_billing_management_created_updated', 'created_at', 'updated_at'),
        Index('idx_billing_management_currency_region', 'currency', 'tax_region'),
        Index('idx_billing_management_dunning', 'dunning_level', 'last_dunning_date'),
    )
    
    def __repr__(self):
        return f"<BillingManagement(id={self.id}, customer_id={self.customer_id}, status={self.status.value}, total={self.total_amount})>"
    
    @classmethod
    def create_billing_account(
        cls,
        customer_id: str,
        billing_cycle: BillingCycle = BillingCycle.MONTHLY,
        currency: Currency = Currency.USD,
        **kwargs
    ) -> 'BillingManagement':
        """Create a new billing account"""
        billing_id = f"bill_{uuid.uuid4().hex[:12]}"
        
        return cls(
            billing_id=billing_id,
            customer_id=customer_id,
            billing_cycle=billing_cycle,
            currency=currency,
            **kwargs
        )
    
    def calculate_total_amount(self) -> Decimal:
        """Calculate total billing amount"""
        subtotal = self.base_amount + self.recurring_amount + self.usage_amount + self.overage_charges
        discounted_amount = subtotal - self.discount_amount
        total_with_tax = discounted_amount + self.tax_amount
        
        self.total_amount = total_with_tax
        return total_with_tax
    
    def apply_discount(self, discount_amount: Decimal, discount_type: DiscountType, reason: str = None) -> None:
        """Apply discount to billing"""
        self.discount_amount += discount_amount
        
        if not self.active_discounts:
            self.active_discounts = []
        
        discount_record = {
            'amount': float(discount_amount),
            'type': discount_type.value,
            'applied_at': datetime.now(timezone.utc).isoformat(),
            'reason': reason
        }
        
        if isinstance(self.active_discounts, list):
            self.active_discounts.append(discount_record)
        else:
            self.active_discounts = [discount_record]
        
        self.calculate_total_amount()
    
    def calculate_tax(self, tax_rate: Decimal = None) -> Decimal:
        """Calculate tax amount"""
        if self.tax_exempt:
            self.tax_amount = Decimal('0.00')
            return self.tax_amount
        
        if tax_rate is None:
            tax_rate = self.tax_rate
        
        taxable_amount = self.base_amount + self.recurring_amount + self.usage_amount - self.discount_amount
        self.tax_amount = taxable_amount * tax_rate
        
        return self.tax_amount
    
    def update_usage(self, usage_data: Dict[str, Any]) -> None:
        """Update usage data and calculate charges"""
        if not self.current_usage:
            self.current_usage = {}
        
        self.current_usage.update(usage_data)
        
        # Calculate usage charges (simplified)
        usage_total = Decimal('0.00')
        for service, usage in usage_data.items():
            if isinstance(usage, dict) and 'amount' in usage and 'rate' in usage:
                usage_total += Decimal(str(usage['amount'])) * Decimal(str(usage['rate']))
        
        self.usage_amount = usage_total
        self.calculate_total_amount()
    
    def process_payment(self, amount: Decimal, payment_method: PaymentMethod) -> bool:
        """Process payment (simplified)"""
        # This would integrate with actual payment processors
        try:
            self.total_paid += amount
            self.total_outstanding -= amount
            self.last_payment_date = datetime.now(timezone.utc)
            self.last_payment_amount = amount
            self.last_payment_method = payment_method
            self.payment_failure_count = 0
            
            if self.total_outstanding <= Decimal('0.00'):
                self.status = BillingStatus.ACTIVE
            
            return True
        except Exception:
            self.payment_failure_count += 1
            return False
    
    def is_overdue(self) -> bool:
        """Check if billing is overdue"""
        if self.next_billing_date and self.total_outstanding > Decimal('0.00'):
            return datetime.now(timezone.utc) > self.next_billing_date
        return False
    
    def calculate_next_billing_date(self) -> datetime:
        """Calculate next billing date"""
        if not self.last_billing_date:
            self.last_billing_date = datetime.now(timezone.utc)
        
        if self.billing_cycle == BillingCycle.MONTHLY:
            self.next_billing_date = self.last_billing_date + timedelta(days=30)
        elif self.billing_cycle == BillingCycle.QUARTERLY:
            self.next_billing_date = self.last_billing_date + timedelta(days=90)
        elif self.billing_cycle == BillingCycle.ANNUALLY:
            self.next_billing_date = self.last_billing_date + timedelta(days=365)
        elif self.billing_cycle == BillingCycle.WEEKLY:
            self.next_billing_date = self.last_billing_date + timedelta(days=7)
        
        return self.next_billing_date
    
    def suspend_billing(self, reason: str = None) -> None:
        """Suspend billing account"""
        self.status = BillingStatus.SUSPENDED
        self.updated_at = datetime.now(timezone.utc)
        
        if not self.metadata:
            self.metadata = {}
        
        self.metadata['suspension'] = {
            'suspended_at': datetime.now(timezone.utc).isoformat(),
            'reason': reason
        }
    
    def reactivate_billing(self) -> None:
        """Reactivate suspended billing"""
        self.status = BillingStatus.ACTIVE
        self.updated_at = datetime.now(timezone.utc)
        
        if not self.metadata:
            self.metadata = {}
        
        self.metadata['reactivation'] = {
            'reactivated_at': datetime.now(timezone.utc).isoformat()
        }
    
    def get_billing_summary(self) -> Dict[str, Any]:
        """Get comprehensive billing summary"""



        return {
            'account_info': {
                'billing_id': self.billing_id,
                'customer_id': str(self.customer_id),
                'status': self.status.value,
                'billing_cycle': self.billing_cycle.value,
                'currency': self.currency.value
            },
            'subscription': {
                'plan_id': self.subscription_plan_id,
                'start_date': self.subscription_start_date.isoformat() if self.subscription_start_date else None,
                'end_date': self.subscription_end_date.isoformat() if self.subscription_end_date else None,
                'is_trial': self.is_trial,
                'trial_end': self.trial_end_date.isoformat() if self.trial_end_date else None
            },
            'amounts': {
                'base_amount': float(self.base_amount),
                'recurring_amount': float(self.recurring_amount),
                'usage_amount': float(self.usage_amount),
                'discount_amount': float(self.discount_amount),
                'tax_amount': float(self.tax_amount),
                'total_amount': float(self.total_amount),
                'total_paid': float(self.total_paid),
                'total_outstanding': float(self.total_outstanding)
            },
            'payment': {
                'primary_method': self.primary_payment_method.value if self.primary_payment_method else None,
                'automatic_payment': self.automatic_payment,
                'last_payment_date': self.last_payment_date.isoformat() if self.last_payment_date else None,
                'last_payment_amount': float(self.last_payment_amount) if self.last_payment_amount else None,
                'failure_count': self.payment_failure_count
            },
            'billing_schedule': {
                'next_billing_date': self.next_billing_date.isoformat() if self.next_billing_date else None,
                'last_billing_date': self.last_billing_date.isoformat() if self.last_billing_date else None,
                'is_overdue': self.is_overdue()
            },
            'metrics': {
                'customer_lifetime_value': float(self.customer_lifetime_value) if self.customer_lifetime_value else None,
                'monthly_recurring_revenue': float(self.monthly_recurring_revenue) if self.monthly_recurring_revenue else None,
                'churn_risk_score': self.churn_risk_score
            }
        }


class BillingInvoice(Base):
    """
    Billing Invoice Model
    
    Manages individual invoices with line items and payment tracking.
    """
    __tablename__ = 'billing_invoices'
    
    # Primary identification
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    invoice_number = Column(String(100), unique=True, nullable=False, index=True)
    
    # Relationships
    billing_id = Column(UUID(as_uuid=True), ForeignKey('billing_management.id'), nullable=False, index=True)
    customer_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    
    # Invoice details
    invoice_type = Column(SQLEnum(InvoiceType), nullable=False, index=True)
    status = Column(SQLEnum(InvoiceStatus), nullable=False, default=InvoiceStatus.DRAFT, index=True)
    currency = Column(SQLEnum(Currency), nullable=False, index=True)
    
    # Financial information
    subtotal = Column(Numeric(10, 2), nullable=False, default=0.00)
    tax_amount = Column(Numeric(10, 2), nullable=False, default=0.00)
    discount_amount = Column(Numeric(10, 2), nullable=False, default=0.00)
    total_amount = Column(Numeric(10, 2), nullable=False, default=0.00)
    paid_amount = Column(Numeric(10, 2), nullable=False, default=0.00)
    outstanding_amount = Column(Numeric(10, 2), nullable=False, default=0.00)
    
    # Dates
    invoice_date = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc), index=True)
    due_date = Column(DateTime(timezone=True), nullable=False, index=True)
    paid_date = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    
    # Invoice content
    line_items = Column(JSONB, nullable=True)
    billing_period_start = Column(DateTime(timezone=True), nullable=True)
    billing_period_end = Column(DateTime(timezone=True), nullable=True)
    notes = Column(Text, nullable=True)
    
    # Payment tracking
    payment_attempts = Column(Integer, nullable=False, default=0)
    last_payment_attempt = Column(DateTime(timezone=True), nullable=True)
    
    # External references
    external_invoice_id = Column(String(255), nullable=True)
    payment_processor_id = Column(String(255), nullable=True)
    
    # Metadata
    metadata = Column(JSONB, nullable=True)
    
    # Relationships
    billing_account = relationship("BillingManagement", backref="invoices")
    
    __table_args__ = (
        Index('idx_billing_invoices_billing_status', 'billing_id', 'status'),
        Index('idx_billing_invoices_customer_date', 'customer_id', 'invoice_date'),
        Index('idx_billing_invoices_due_date', 'due_date'),
        Index('idx_billing_invoices_type', 'invoice_type'),
        Index('idx_billing_invoices_amount', 'total_amount', 'outstanding_amount'),
    )
    
    def __repr__(self):
        return f"<BillingInvoice(invoice_number={self.invoice_number}, status={self.status.value}, total={self.total_amount})>"
    
    def calculate_totals(self) -> None:
        """Calculate invoice totals from line items"""
        if not self.line_items:
            return
        
        subtotal = Decimal('0.00')
        for item in self.line_items:
            if isinstance(item, dict) and 'amount' in item:
                subtotal += Decimal(str(item['amount']))
        
        self.subtotal = subtotal
        self.total_amount = self.subtotal + self.tax_amount - self.discount_amount
        self.outstanding_amount = self.total_amount - self.paid_amount
    
    def mark_as_paid(self, payment_amount: Decimal = None) -> None:
        """Mark invoice as paid"""
        if payment_amount is None:
            payment_amount = self.outstanding_amount
        
        self.paid_amount += payment_amount
        self.outstanding_amount -= payment_amount
        self.paid_date = datetime.now(timezone.utc)
        
        if self.outstanding_amount <= Decimal('0.00'):
            self.status = InvoiceStatus.PAID
        else:
            self.status = InvoiceStatus.PARTIALLY_PAID
