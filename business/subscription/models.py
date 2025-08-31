"""Subscription Models

Data models for subscription management system supporting multi-tier plans,
billing cycles, payment methods, and feature access control.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: © 2025 Fahed Mlaiel. All rights reserved.

WARNING: Proprietary code - Unauthorized use strictly prohibited.
"""from datetime import datetime, timedelta
from decimal import Decimal
from enum import Enum
from typing import Optional, Dict, Any, List
from dataclasses import dataclass, field
from sqlalchemy import Column, Integer, String, DateTime, Boolean, Numeric, Text, JSON, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
import uuid

Base = declarative_base()


class SubscriptionStatus(Enum):
    """Subscription status enumeration."""    ACTIVE = "active"
    INACTIVE = "inactive" 
    CANCELLED = "cancelled"
    EXPIRED = "expired"
    SUSPENDED = "suspended"
    PENDING = "pending"
    TRIAL = "trial"


class BillingCycleType(Enum):
    """Billing cycle enumeration."""    MONTHLY = "monthly"
    YEARLY = "yearly"
    QUARTERLY = "quarterly"
    LIFETIME = "lifetime"


class PaymentStatus(Enum):
    """Payment status enumeration."""    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"
    REFUNDED = "refunded"
    CANCELLED = "cancelled"


class FeatureType(Enum):
    """Feature type enumeration."""    BOOLEAN = "boolean"  # On/off feature
    QUOTA = "quota"      # Usage-based limit
    UNLIMITED = "unlimited"  # No limits


class SubscriptionPlan(Base):
    """    Subscription plan model defining available tiers and features.
    
    Supports multiple tier levels from Free to Enterprise with
    granular feature control and pricing flexibility.
    """    __tablename__ = "subscription_plans"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, unique=True)
    display_name = Column(String(150), nullable=False)
    description = Column(Text, nullable=True)
    tier_level = Column(Integer, nullable=False)  # 0=Free, 1=Basic, 2=Pro, 3=Enterprise
    
    # Pricing
    monthly_price = Column(Numeric(10, 2), default=0.00)
    yearly_price = Column(Numeric(10, 2), default=0.00)
    quarterly_price = Column(Numeric(10, 2), default=0.00)
    currency = Column(String(3), default="EUR")
    
    # Features and limits
    features = Column(JSON, nullable=False, default=dict)  # Feature definitions
    limits = Column(JSON, nullable=False, default=dict)    # Usage limits
    
    # Plan properties
    is_active = Column(Boolean, default=True)
    is_popular = Column(Boolean, default=False)
    is_enterprise = Column(Boolean, default=False)
    trial_days = Column(Integer, default=0)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    subscriptions = relationship("UserSubscription", back_populates="plan")


class UserSubscription(Base):
    """    User subscription model tracking active subscriptions and billing.
    
    Manages subscription lifecycle including trials, upgrades, downgrades,
    and automatic renewals with payment processor integration.
    """    __tablename__ = "user_subscriptions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False, index=True)
    plan_id = Column(Integer, ForeignKey("subscription_plans.id"), nullable=False)
    
    # Subscription details
    status = Column(String(20), default=SubscriptionStatus.PENDING.value)
    billing_cycle = Column(String(20), default=BillingCycleType.MONTHLY.value)
    
    # Dates
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=False)
    trial_end_date = Column(DateTime, nullable=True)
    next_billing_date = Column(DateTime, nullable=True)
    cancelled_at = Column(DateTime, nullable=True)
    
    # Payment
    payment_method_id = Column(String(100), nullable=True)  # Payment processor ID
    last_payment_date = Column(DateTime, nullable=True)
    next_payment_amount = Column(Numeric(10, 2), nullable=True)
    
    # Subscription tracking
    subscription_id = Column(String(100), unique=True)  # External subscription ID
    customer_id = Column(String(100), nullable=True)    # Payment processor customer ID
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    plan = relationship("SubscriptionPlan", back_populates="subscriptions")
    billing_cycles = relationship("BillingCycle", back_populates="subscription")
    invoices = relationship("Invoice", back_populates="subscription")
    usage_metrics = relationship("UsageMetrics", back_populates="subscription")


class BillingCycle(Base):
    """    Billing cycle tracking for subscription renewals and payments.
    
    Records each billing period with payment status and amounts
    for accurate financial tracking and revenue analytics.
    """    __tablename__ = "billing_cycles"
    
    id = Column(Integer, primary_key=True, index=True)
    subscription_id = Column(Integer, ForeignKey("user_subscriptions.id"), nullable=False)
    
    # Cycle details
    cycle_start = Column(DateTime, nullable=False)
    cycle_end = Column(DateTime, nullable=False)
    billing_amount = Column(Numeric(10, 2), nullable=False)
    currency = Column(String(3), default="EUR")
    
    # Payment tracking
    payment_status = Column(String(20), default=PaymentStatus.PENDING.value)
    payment_date = Column(DateTime, nullable=True)
    payment_method = Column(String(50), nullable=True)
    transaction_id = Column(String(100), nullable=True)
    
    # Adjustments
    prorated_amount = Column(Numeric(10, 2), default=0.00)
    discount_amount = Column(Numeric(10, 2), default=0.00)
    tax_amount = Column(Numeric(10, 2), default=0.00)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    subscription = relationship("UserSubscription", back_populates="billing_cycles")


class PaymentMethod(Base):
    """    Payment method storage for subscription billing.
    
    Securely stores payment method references from payment processors
    with support for multiple payment types and automatic billing.
    """    __tablename__ = "payment_methods"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False, index=True)
    
    # Payment method details
    payment_method_id = Column(String(100), nullable=False)  # Payment processor ID
    payment_type = Column(String(50), nullable=False)        # card, paypal, bank, etc.
    processor = Column(String(50), nullable=False)           # stripe, paypal, wise
    
    # Card/Account info (masked)
    last_four = Column(String(4), nullable=True)
    brand = Column(String(50), nullable=True)
    expiry_month = Column(Integer, nullable=True)
    expiry_year = Column(Integer, nullable=True)
    
    # Status
    is_default = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class Invoice(Base):
    """    Invoice generation and tracking for subscription billing.
    
    Maintains complete invoice history with line items, taxes,
    and payment status for financial reporting and compliance.
    """    __tablename__ = "invoices"
    
    id = Column(Integer, primary_key=True, index=True)
    subscription_id = Column(Integer, ForeignKey("user_subscriptions.id"), nullable=False)
    user_id = Column(Integer, nullable=False, index=True)
    
    # Invoice details
    invoice_number = Column(String(50), unique=True, nullable=False)
    invoice_date = Column(DateTime, nullable=False)
    due_date = Column(DateTime, nullable=False)
    
    # Amounts
    subtotal = Column(Numeric(10, 2), nullable=False)
    tax_amount = Column(Numeric(10, 2), default=0.00)
    discount_amount = Column(Numeric(10, 2), default=0.00)
    total_amount = Column(Numeric(10, 2), nullable=False)
    currency = Column(String(3), default="EUR")
    
    # Status and payment
    status = Column(String(20), default=PaymentStatus.PENDING.value)
    payment_date = Column(DateTime, nullable=True)
    payment_method = Column(String(50), nullable=True)
    
    # Line items
    line_items = Column(JSON, nullable=False, default=list)
    
    # External references
    stripe_invoice_id = Column(String(100), nullable=True)
    paypal_invoice_id = Column(String(100), nullable=True)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    subscription = relationship("UserSubscription", back_populates="invoices")


class UsageMetrics(Base):
    """    Usage tracking and quota management for subscription features.
    
    Monitors feature usage against subscription limits with
    real-time tracking and quota enforcement capabilities.
    """    __tablename__ = "usage_metrics"
    
    id = Column(Integer, primary_key=True, index=True)
    subscription_id = Column(Integer, ForeignKey("user_subscriptions.id"), nullable=False)
    user_id = Column(Integer, nullable=False, index=True)
    
    # Usage tracking
    feature_name = Column(String(100), nullable=False)
    usage_count = Column(Integer, default=0)
    quota_limit = Column(Integer, nullable=True)  # None = unlimited
    
    # Time period
    period_start = Column(DateTime, nullable=False)
    period_end = Column(DateTime, nullable=False)
    
    # Usage details
    last_usage_date = Column(DateTime, nullable=True)
    usage_data = Column(JSON, nullable=True, default=dict)  # Additional usage metadata
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    subscription = relationship("UserSubscription", back_populates="usage_metrics")


class SubscriptionHistory(Base):
    """    Subscription change history and audit trail.
    
    Tracks all subscription modifications including upgrades, downgrades,
    cancellations, and status changes for compliance and analytics.
    """    __tablename__ = "subscription_history"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False, index=True)
    subscription_id = Column(Integer, nullable=True)  # Can be null for account-level changes
    
    # Change details
    action_type = Column(String(50), nullable=False)  # upgrade, downgrade, cancel, etc.
    from_plan_id = Column(Integer, nullable=True)
    to_plan_id = Column(Integer, nullable=True)
    from_status = Column(String(20), nullable=True)
    to_status = Column(String(20), nullable=True)
    
    # Change metadata
    reason = Column(String(200), nullable=True)
    triggered_by = Column(String(50), nullable=True)  # user, system, admin
    change_data = Column(JSON, nullable=True, default=dict)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)


class FeatureAccess(Base):
    """    Feature access control matrix for subscription tiers.
    
    Defines granular feature access permissions based on subscription
    level with support for quota limits and boolean access controls.
    """    __tablename__ = "feature_access"
    
    id = Column(Integer, primary_key=True, index=True)
    plan_id = Column(Integer, ForeignKey("subscription_plans.id"), nullable=False)
    
    # Feature definition
    feature_name = Column(String(100), nullable=False)
    feature_key = Column(String(100), nullable=False)  # Technical key
    feature_type = Column(String(20), default=FeatureType.BOOLEAN.value)
    
    # Access control
    is_enabled = Column(Boolean, default=True)
    quota_limit = Column(Integer, nullable=True)  # For quota-based features
    quota_period = Column(String(20), default="monthly")  # daily, weekly, monthly
    
    # Feature metadata
    description = Column(Text, nullable=True)
    category = Column(String(50), nullable=True)  # ai, protection, analytics, etc.
    priority = Column(Integer, default=0)  # Display priority
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


@dataclass
class SubscriptionPlanConfig:
    """Configuration for subscription plan creation."""    name: str
    display_name: str
    description: str
    tier_level: int
    monthly_price: Decimal
    yearly_price: Decimal
    features: Dict[str, Any]
    limits: Dict[str, Any]
    trial_days: int = 0
    is_popular: bool = False
    is_enterprise: bool = False


@dataclass 
class UsageQuota:
    """Usage quota configuration for features."""    feature_name: str
    current_usage: int
    quota_limit: Optional[int]
    period_start: datetime
    period_end: datetime
    is_unlimited: bool = False
    
    @property
    def usage_percentage(self) -> float:
        """Calculate usage percentage."""        if self.is_unlimited or not self.quota_limit:
            return 0.0
        return (self.current_usage / self.quota_limit) * 100
    
    @property
    def is_quota_exceeded(self) -> bool:
        """Check if quota is exceeded."""        if self.is_unlimited or not self.quota_limit:
            return False
        return self.current_usage >= self.quota_limit


@dataclass
class BillingSummary:
    """Billing summary for subscription analytics."""    subscription_id: int
    current_period_start: datetime
    current_period_end: datetime
    next_billing_date: datetime
    amount_due: Decimal
    payment_status: str
    payment_method: Optional[str] = None
    proration_amount: Decimal = field(default_factory=lambda: Decimal('0.00'))


# Predefined subscription plans configuration
SUBSCRIPTION_PLANS = {
    "free": SubscriptionPlanConfig(
        name="free",
        display_name="Free Creator",
        description="Basic AI tools for new creators",
        tier_level=0,
        monthly_price=Decimal('0.00'),
        yearly_price=Decimal('0.00'),
        features={
            "ai_recommendations": True,
            "basic_analytics": True,
            "content_upload": True,
            "fingerprint_detection": True,
            "basic_protection": True
        },
        limits={
            "monthly_uploads": 10,
            "storage_gb": 1,
            "ai_requests": 100,
            "protected_content": 5
        },
        trial_days=0
    ),
    "creator": SubscriptionPlanConfig(
        name="creator",
        display_name="Creator Pro",
        description="Professional tools for growing creators",
        tier_level=1,
        monthly_price=Decimal('29.99'),
        yearly_price=Decimal('299.99'),
        features={
            "ai_recommendations": True,
            "advanced_analytics": True,
            "content_upload": True,
            "fingerprint_detection": True,
            "advanced_protection": True,
            "collaboration_tools": True,
            "seo_optimization": True
        },
        limits={
            "monthly_uploads": 100,
            "storage_gb": 50,
            "ai_requests": 1000,
            "protected_content": 100,
            "collaborators": 5
        },
        trial_days=14,
        is_popular=True
    ),
    "studio": SubscriptionPlanConfig(
        name="studio",
        display_name="Creator Studio",
        description="Complete creator management platform",
        tier_level=2,
        monthly_price=Decimal('99.99'),
        yearly_price=Decimal('999.99'),
        features={
            "ai_recommendations": True,
            "advanced_analytics": True,
            "premium_analytics": True,
            "content_upload": True,
            "fingerprint_detection": True,
            "advanced_protection": True,
            "enterprise_protection": True,
            "collaboration_tools": True,
            "seo_optimization": True,
            "revenue_tracking": True,
            "multi_platform_distribution": True,
            "api_access": True
        },
        limits={
            "monthly_uploads": 1000,
            "storage_gb": 500,
            "ai_requests": 10000,
            "protected_content": 1000,
            "collaborators": 25,
            "api_calls": 10000
        },
        trial_days=30
    ),
    "enterprise": SubscriptionPlanConfig(
        name="enterprise",
        display_name="Enterprise",
        description="Custom solutions for large organizations",
        tier_level=3,
        monthly_price=Decimal('499.99'),
        yearly_price=Decimal('4999.99'),
        features={
            "all_features": True,
            "custom_integrations": True,
            "dedicated_support": True,
            "white_label": True,
            "custom_ai_models": True,
            "enterprise_sso": True,
            "compliance_tools": True,
            "custom_analytics": True
        },
        limits={},  # No limits for enterprise
        trial_days=60,
        is_enterprise=True
    )
}


__all__ = [
    'Base',
    'SubscriptionStatus', 
    'BillingCycleType',
    'PaymentStatus',
    'FeatureType',
    'SubscriptionPlan',
    'UserSubscription',
    'BillingCycle',
    'PaymentMethod', 
    'Invoice',
    'UsageMetrics',
    'SubscriptionHistory',
    'FeatureAccess',
    'SubscriptionPlanConfig',
    'UsageQuota',
    'BillingSummary',
    'SUBSCRIPTION_PLANS'
]
