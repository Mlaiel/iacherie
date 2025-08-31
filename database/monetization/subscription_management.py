"""Subscription Management Models - Enterprise Subscription & Recurring Revenue System

Ultra-advanced subscription management system for recurring revenue streams,
subscription analytics, and customer lifecycle management.

Author: Fahed Mlaiel <mlaiel@live.de>
Project: IA Influencer Agent + Content Protection Platform
Copyright: All rights reserved. Unauthorized use, modification, or distribution prohibited.

🚨 CRITICAL LEGAL WARNING:
This code and all associated intellectual property belong exclusively to Fahed Mlaiel.
Any unauthorized use, copying, modification, distribution, or commercialization 
is STRICTLY PROHIBITED and will result in immediate legal action.

Contact: mlaiel@live.de for licensing inquiries and authorization.

Expert Project Team - Fahed Mlaiel:
- Lead AI Developer & Solution Architect
- Senior Backend Engineer (Python/FastAPI/Django)
- Machine Learning Engineer (TensorFlow/PyTorch/Hugging Face)
- Database Administrator & Data Engineer (PostgreSQL/Redis/MongoDB)
- Backend Security Specialist
- Microservices Architect
- Audio Processing Engineer
- DevOps Engineer
- AI Prompt Engineer & Automation Specialist
"""from sqlalchemy import (
    Column, Integer, String, DateTime, Float, Boolean, ForeignKey,
    Text, DECIMAL, JSON, BigInteger, Index, UniqueConstraint
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, backref
from sqlalchemy.dialects.postgresql import UUID, JSONB, ARRAY
from sqlalchemy.sql import func
from enum import Enum
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass

Base = declarative_base()

class SubscriptionTier(Enum):
    """Subscription tier levels"""    BASIC = "basic"
    PREMIUM = "premium"
    PROFESSIONAL = "professional"
    ENTERPRISE = "enterprise"
    CUSTOM = "custom"

class SubscriptionStatus(Enum):
    """Subscription status types"""    ACTIVE = "active"
    PENDING = "pending"
    SUSPENDED = "suspended"
    CANCELLED = "cancelled"
    EXPIRED = "expired"
    TRIAL = "trial"
    PAUSED = "paused"

class BillingCycle(Enum):
    """Billing cycle types"""    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    ANNUALLY = "annually"
    WEEKLY = "weekly"
    DAILY = "daily"
    CUSTOM = "custom"

class PaymentStatus(Enum):
    """Payment status for subscriptions"""    PENDING = "pending"
    PAID = "paid"
    FAILED = "failed"
    REFUNDED = "refunded"
    PARTIALLY_REFUNDED = "partially_refunded"
    DISPUTED = "disputed"

class ChurnReason(Enum):
    """Reasons for subscription cancellation"""    PRICE_TOO_HIGH = "price_too_high"
    LACK_OF_FEATURES = "lack_of_features"
    POOR_PERFORMANCE = "poor_performance"
    COMPETITOR = "competitor"
    FINANCIAL_CONSTRAINTS = "financial_constraints"
    TECHNICAL_ISSUES = "technical_issues"
    CUSTOMER_SERVICE = "customer_service"
    BUSINESS_CLOSURE = "business_closure"
    OTHER = "other"

class SubscriptionPlan(Base):
    """Subscription plan definitions"""    __tablename__ = 'subscription_plans'
    
    # Primary identification
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    plan_code = Column(String(50), unique=True, nullable=False)
    plan_name = Column(String(200), nullable=False)
    
    # Plan details
    tier = Column(String(20), nullable=False)
    description = Column(Text)
    features = Column(JSONB)  # List of features included
    limitations = Column(JSONB)  # Usage limitations
    
    # Pricing
    base_price = Column(DECIMAL(10, 4), nullable=False)
    currency = Column(String(3), default='USD')
    billing_cycle = Column(String(20), nullable=False)
    setup_fee = Column(DECIMAL(10, 4), default=0)
    
    # Usage limits
    max_content_uploads = Column(Integer)
    max_storage_gb = Column(Integer)
    max_api_calls_per_month = Column(Integer)
    max_collaborators = Column(Integer)
    max_projects = Column(Integer)
    
    # Trial configuration
    trial_period_days = Column(Integer, default=0)
    trial_price = Column(DECIMAL(10, 4), default=0)
    
    # Discounts and promotions
    discount_percentage = Column(Float, default=0.0)
    promotional_price = Column(DECIMAL(10, 4))
    promotion_start_date = Column(DateTime(timezone=True))
    promotion_end_date = Column(DateTime(timezone=True))
    
    # Plan status
    is_active = Column(Boolean, default=True)
    is_visible = Column(Boolean, default=True)
    requires_approval = Column(Boolean, default=False)
    
    # Metadata
    tags = Column(ARRAY(String))
    target_audience = Column(String(100))
    recommended_for = Column(Text)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), default=func.now())
    updated_at = Column(DateTime(timezone=True), default=func.now(), onupdate=func.now())
    
    # Indexes
    __table_args__ = (
        Index('idx_plan_tier_active', 'tier', 'is_active'),
        Index('idx_plan_pricing', 'base_price', 'billing_cycle'),
    )

class Subscription(Base):
    """Customer subscription records"""    __tablename__ = 'subscriptions'
    
    # Primary identification
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    subscription_number = Column(String(100), unique=True, nullable=False)
    customer_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    plan_id = Column(UUID(as_uuid=True), ForeignKey('subscription_plans.id'), nullable=False)
    
    # Subscription details
    status = Column(String(20), default=SubscriptionStatus.PENDING.value)
    tier = Column(String(20), nullable=False)
    custom_name = Column(String(200))
    
    # Billing information
    billing_cycle = Column(String(20), nullable=False)
    base_price = Column(DECIMAL(10, 4), nullable=False)
    current_price = Column(DECIMAL(10, 4), nullable=False)
    currency = Column(String(3), default='USD')
    
    # Dates and timeline
    start_date = Column(DateTime(timezone=True), nullable=False)
    end_date = Column(DateTime(timezone=True))
    trial_start_date = Column(DateTime(timezone=True))
    trial_end_date = Column(DateTime(timezone=True))
    next_billing_date = Column(DateTime(timezone=True))
    last_billing_date = Column(DateTime(timezone=True))
    
    # Payment information
    payment_method_id = Column(String(100))
    payment_gateway = Column(String(50))
    auto_renewal = Column(Boolean, default=True)
    
    # Usage tracking
    current_usage = Column(JSONB)  # Current period usage metrics
    usage_history = Column(JSONB)  # Historical usage data
    overage_charges = Column(DECIMAL(10, 4), default=0)
    
    # Customizations
    custom_features = Column(JSONB)  # Additional features
    custom_limits = Column(JSONB)  # Custom usage limits
    addon_services = Column(JSONB)  # Additional services
    
    # Lifecycle tracking
    activation_date = Column(DateTime(timezone=True))
    first_payment_date = Column(DateTime(timezone=True))
    cancellation_date = Column(DateTime(timezone=True))
    cancellation_reason = Column(String(50))
    cancellation_feedback = Column(Text)
    
    # Financial metrics
    total_revenue = Column(DECIMAL(15, 4), default=0)
    monthly_recurring_revenue = Column(DECIMAL(10, 4), default=0)
    annual_contract_value = Column(DECIMAL(15, 4), default=0)
    customer_lifetime_value = Column(DECIMAL(15, 4), default=0)
    
    # Relationship data
    referred_by = Column(UUID(as_uuid=True))
    referral_code = Column(String(50))
    acquisition_channel = Column(String(100))
    acquisition_cost = Column(DECIMAL(10, 4), default=0)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), default=func.now())
    updated_at = Column(DateTime(timezone=True), default=func.now(), onupdate=func.now())
    
    # Relationships
    plan = relationship("SubscriptionPlan", backref="subscriptions")
    
    # Indexes
    __table_args__ = (
        Index('idx_subscription_customer_status', 'customer_id', 'status'),
        Index('idx_subscription_billing_date', 'next_billing_date', 'status'),
        Index('idx_subscription_plan_tier', 'plan_id', 'tier'),
        Index('idx_subscription_dates', 'start_date', 'end_date'),
    )

class SubscriptionInvoice(Base):
    """Subscription billing invoices"""    __tablename__ = 'subscription_invoices'
    
    # Primary identification
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    invoice_number = Column(String(100), unique=True, nullable=False)
    subscription_id = Column(UUID(as_uuid=True), ForeignKey('subscriptions.id'), nullable=False)
    customer_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    
    # Invoice details
    invoice_type = Column(String(20), nullable=False)  # subscription, usage, addon, adjustment
    status = Column(String(20), default=PaymentStatus.PENDING.value)
    
    # Billing period
    billing_period_start = Column(DateTime(timezone=True), nullable=False)
    billing_period_end = Column(DateTime(timezone=True), nullable=False)
    
    # Financial details
    subtotal = Column(DECIMAL(10, 4), nullable=False)
    tax_amount = Column(DECIMAL(10, 4), default=0)
    discount_amount = Column(DECIMAL(10, 4), default=0)
    total_amount = Column(DECIMAL(10, 4), nullable=False)
    currency = Column(String(3), default='USD')
    
    # Payment information
    payment_method = Column(String(50))
    payment_gateway = Column(String(50))
    transaction_id = Column(String(100))
    gateway_reference = Column(String(100))
    
    # Dates
    issue_date = Column(DateTime(timezone=True), default=func.now())
    due_date = Column(DateTime(timezone=True), nullable=False)
    paid_date = Column(DateTime(timezone=True))
    
    # Line items
    line_items = Column(JSONB)  # Detailed billing line items
    tax_breakdown = Column(JSONB)  # Tax calculation details
    discount_details = Column(JSONB)  # Discount application details
    
    # Files and documents
    pdf_invoice_path = Column(String(500))
    receipt_path = Column(String(500))
    
    # Retry and failure handling
    payment_attempts = Column(Integer, default=0)
    last_payment_attempt = Column(DateTime(timezone=True))
    failure_reason = Column(String(200))
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), default=func.now())
    updated_at = Column(DateTime(timezone=True), default=func.now(), onupdate=func.now())
    
    # Relationships
    subscription = relationship("Subscription", backref="invoices")
    
    # Indexes
    __table_args__ = (
        Index('idx_invoice_subscription_status', 'subscription_id', 'status'),
        Index('idx_invoice_customer_date', 'customer_id', 'issue_date'),
        Index('idx_invoice_due_date', 'due_date', 'status'),
        Index('idx_invoice_billing_period', 'billing_period_start', 'billing_period_end'),
    )

class SubscriptionUsage(Base):
    """Detailed subscription usage tracking"""    __tablename__ = 'subscription_usage'
    
    # Primary identification
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    subscription_id = Column(UUID(as_uuid=True), ForeignKey('subscriptions.id'), nullable=False)
    customer_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    
    # Usage details
    feature_name = Column(String(100), nullable=False)
    usage_type = Column(String(50), nullable=False)  # count, storage, bandwidth, api_calls
    unit = Column(String(20), nullable=False)  # requests, GB, MB, hours
    
    # Usage metrics
    usage_amount = Column(BigInteger, default=0)
    limit_amount = Column(BigInteger)
    overage_amount = Column(BigInteger, default=0)
    usage_percentage = Column(Float, default=0.0)
    
    # Billing period
    billing_period_start = Column(DateTime(timezone=True), nullable=False)
    billing_period_end = Column(DateTime(timezone=True), nullable=False)
    
    # Cost calculation
    unit_price = Column(DECIMAL(10, 6), default=0)
    included_usage = Column(BigInteger, default=0)
    billable_usage = Column(BigInteger, default=0)
    usage_cost = Column(DECIMAL(10, 4), default=0)
    overage_cost = Column(DECIMAL(10, 4), default=0)
    
    # Temporal tracking
    measurement_timestamp = Column(DateTime(timezone=True), default=func.now())
    first_usage_in_period = Column(DateTime(timezone=True))
    last_usage_in_period = Column(DateTime(timezone=True))
    
    # Usage context
    source_platform = Column(String(100))
    user_agent = Column(String(500))
    ip_address = Column(String(45))
    country_code = Column(String(2))
    
    # Metadata
    usage_metadata = Column(JSONB)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), default=func.now())
    updated_at = Column(DateTime(timezone=True), default=func.now(), onupdate=func.now())
    
    # Relationships
    subscription = relationship("Subscription", backref="usage_records")
    
    # Indexes
    __table_args__ = (
        Index('idx_usage_subscription_period', 'subscription_id', 'billing_period_start'),
        Index('idx_usage_customer_feature', 'customer_id', 'feature_name'),
        Index('idx_usage_timestamp', 'measurement_timestamp'),
        UniqueConstraint('subscription_id', 'feature_name', 'billing_period_start', name='uq_usage_unique'),
    )

class SubscriptionMetrics(Base):
    """Subscription business metrics and analytics"""    __tablename__ = 'subscription_metrics'
    
    # Primary identification
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    metric_date = Column(DateTime(timezone=True), nullable=False)
    calculation_timestamp = Column(DateTime(timezone=True), default=func.now())
    
    # Revenue metrics
    monthly_recurring_revenue = Column(DECIMAL(15, 4), default=0)
    annual_recurring_revenue = Column(DECIMAL(15, 4), default=0)
    total_contract_value = Column(DECIMAL(15, 4), default=0)
    average_revenue_per_user = Column(DECIMAL(10, 4), default=0)
    
    # Customer metrics
    total_subscribers = Column(Integer, default=0)
    active_subscribers = Column(Integer, default=0)
    trial_subscribers = Column(Integer, default=0)
    churned_subscribers = Column(Integer, default=0)
    new_subscribers = Column(Integer, default=0)
    
    # Churn and retention
    churn_rate = Column(Float, default=0.0)
    retention_rate = Column(Float, default=0.0)
    gross_churn_rate = Column(Float, default=0.0)
    net_churn_rate = Column(Float, default=0.0)
    
    # Growth metrics
    growth_rate = Column(Float, default=0.0)
    customer_acquisition_cost = Column(DECIMAL(10, 4), default=0)
    customer_lifetime_value = Column(DECIMAL(10, 4), default=0)
    ltv_cac_ratio = Column(Float, default=0.0)
    
    # Conversion metrics
    trial_conversion_rate = Column(Float, default=0.0)
    upgrade_rate = Column(Float, default=0.0)
    downgrade_rate = Column(Float, default=0.0)
    
    # Tier distribution
    tier_distribution = Column(JSONB)  # Breakdown by subscription tier
    plan_distribution = Column(JSONB)  # Breakdown by plan
    
    # Geographic distribution
    geographic_distribution = Column(JSONB)
    
    # Payment metrics
    successful_payments = Column(Integer, default=0)
    failed_payments = Column(Integer, default=0)
    payment_success_rate = Column(Float, default=0.0)
    average_payment_retry_attempts = Column(Float, default=0.0)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), default=func.now())
    
    # Indexes
    __table_args__ = (
        Index('idx_metrics_date', 'metric_date'),
        Index('idx_metrics_mrr', 'monthly_recurring_revenue', 'metric_date'),
        UniqueConstraint('metric_date', name='uq_metrics_date'),
    )

class ChurnPrediction(Base):
    """ML-powered churn prediction for subscribers"""    __tablename__ = 'churn_predictions'
    
    # Primary identification
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    subscription_id = Column(UUID(as_uuid=True), ForeignKey('subscriptions.id'), nullable=False)
    customer_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    
    # Prediction details
    churn_probability = Column(Float, nullable=False)
    risk_level = Column(String(20), nullable=False)  # low, medium, high, critical
    predicted_churn_date = Column(DateTime(timezone=True))
    confidence_score = Column(Float, default=0.0)
    
    # Risk factors
    primary_risk_factors = Column(JSONB)
    risk_factor_scores = Column(JSONB)
    behavioral_indicators = Column(JSONB)
    usage_patterns = Column(JSONB)
    
    # Model information
    model_name = Column(String(100), nullable=False)
    model_version = Column(String(20), nullable=False)
    prediction_timestamp = Column(DateTime(timezone=True), default=func.now())
    
    # Intervention tracking
    intervention_recommended = Column(Boolean, default=False)
    intervention_type = Column(String(50))
    intervention_applied = Column(Boolean, default=False)
    intervention_date = Column(DateTime(timezone=True))
    intervention_result = Column(String(50))
    
    # Actual outcome tracking
    actual_churn_date = Column(DateTime(timezone=True))
    prediction_accuracy = Column(Float)
    outcome_tracked = Column(Boolean, default=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), default=func.now())
    updated_at = Column(DateTime(timezone=True), default=func.now(), onupdate=func.now())
    
    # Relationships
    subscription = relationship("Subscription", backref="churn_predictions")
    
    # Indexes
    __table_args__ = (
        Index('idx_churn_subscription_risk', 'subscription_id', 'risk_level'),
        Index('idx_churn_customer_probability', 'customer_id', 'churn_probability'),
        Index('idx_churn_prediction_date', 'predicted_churn_date', 'risk_level'),
    )

@dataclass
class SubscriptionAnalytics:
    """Subscription analytics data structure"""    total_revenue: float
    mrr: float
    arr: float
    churn_rate: float
    growth_rate: float
    ltv: float
    cac: float
    active_subscribers: int
    new_subscribers: int
    churned_subscribers: int
    tier_breakdown: Dict[str, int]
    geographic_breakdown: Dict[str, float]

class SubscriptionEvent(Base):
    """Subscription lifecycle events tracking"""    __tablename__ = 'subscription_events'
    
    # Primary identification
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    subscription_id = Column(UUID(as_uuid=True), ForeignKey('subscriptions.id'), nullable=False)
    customer_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    
    # Event details
    event_type = Column(String(50), nullable=False)  # created, activated, upgraded, downgraded, cancelled, etc.
    event_category = Column(String(30), nullable=False)  # lifecycle, billing, usage, support
    description = Column(Text)
    
    # Event data
    previous_state = Column(JSONB)
    new_state = Column(JSONB)
    change_details = Column(JSONB)
    
    # Context
    triggered_by = Column(String(50))  # user, system, admin, automation
    trigger_source = Column(String(100))  # dashboard, api, billing_system, etc.
    user_agent = Column(String(500))
    ip_address = Column(String(45))
    
    # Financial impact
    revenue_impact = Column(DECIMAL(10, 4), default=0)
    immediate_charge = Column(DECIMAL(10, 4), default=0)
    future_revenue_change = Column(DECIMAL(10, 4), default=0)
    
    # Processing
    processed = Column(Boolean, default=False)
    processing_notes = Column(Text)
    requires_manual_review = Column(Boolean, default=False)
    
    # Timestamps
    event_timestamp = Column(DateTime(timezone=True), default=func.now())
    created_at = Column(DateTime(timezone=True), default=func.now())
    
    # Relationships
    subscription = relationship("Subscription", backref="events")
    
    # Indexes
    __table_args__ = (
        Index('idx_event_subscription_type', 'subscription_id', 'event_type'),
        Index('idx_event_customer_timestamp', 'customer_id', 'event_timestamp'),
        Index('idx_event_type_timestamp', 'event_type', 'event_timestamp'),
    )

# Export all models for easy import
__all__ = [
    'SubscriptionTier',
    'SubscriptionStatus',
    'BillingCycle',
    'PaymentStatus',
    'ChurnReason',
    'SubscriptionPlan',
    'Subscription',
    'SubscriptionInvoice',
    'SubscriptionUsage',
    'SubscriptionMetrics',
    'ChurnPrediction',
    'SubscriptionAnalytics',
    'SubscriptionEvent'
]
