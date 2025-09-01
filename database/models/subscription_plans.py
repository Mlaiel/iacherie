"""Subscription Plans Database Model

Enterprise-grade SQLAlchemy model for managing subscription plans,
pricing tiers, features, billing cycles, and subscription management.

Author: Fahed Mlaiel <mlaiel@live.de>
Project: IA Influencer Agent + Content Protection Platform
Copyright: All rights reserved. Unauthorized use, modification, or distribution prohibited.

🚨 INTELLECTUAL PROPERTY WARNING: This code, concept, and architecture are 
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

from sqlalchemy import Column, String, Text, DateTime, Float, Integer, Boolean, JSON, ForeignKey, Index, Enum as SQLEnum, Numeric, ARRAY
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID, JSONB
from datetime import datetime, timezone, timedelta
from enum import Enum
import uuid
from typing import Dict, Any, List, Optional
from decimal import Decimal

Base = declarative_base()


class PlanTier(Enum):
    """
Subscription plan tier enumeration"""

    FREE = "free"
    BASIC = "basic"
    STANDARD = "standard"
    PREMIUM = "premium"
    PROFESSIONAL = "professional"
    ENTERPRISE = "enterprise"
    UNLIMITED = "unlimited"
    CUSTOM = "custom"


class BillingCycle(Enum):
    """Billing cycle enumeration"""

    WEEKLY = "weekly"
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    SEMI_ANNUALLY = "semi_annually"
    ANNUALLY = "annually"
    BIANNUALLY = "biannually"
    LIFETIME = "lifetime"
    USAGE_BASED = "usage_based"
    ONE_TIME = "one_time"


class PlanStatus(Enum):
    """Plan status enumeration"""

    ACTIVE = "active"
    INACTIVE = "inactive"
    DEPRECATED = "deprecated"
    COMING_SOON = "coming_soon"
    BETA = "beta"
    ARCHIVED = "archived"
    SUSPENDED = "suspended"


class Currency(Enum):
    """Currency enumeration"""

    USD = "USD"
    EUR = "EUR"
    GBP = "GBP"
    CAD = "CAD"
    AUD = "AUD"
    JPY = "JPY"
    CHF = "CHF"
    SEK = "SEK"
    NOK = "NOK"
    DKK = "DKK"
    PLN = "PLN"
    BRL = "BRL"
    MXN = "MXN"
    INR = "INR"
    CNY = "CNY"
    KRW = "KRW"
    SGD = "SGD"


class DiscountType(Enum):
    """Discount type enumeration"""

    PERCENTAGE = "percentage"
    FIXED_AMOUNT = "fixed_amount"
    FREE_TRIAL = "free_trial"
    FIRST_MONTH_FREE = "first_month_free"
    BOGO = "bogo"
    STUDENT_DISCOUNT = "student_discount"
    CREATOR_DISCOUNT = "creator_discount"
    LOYALTY_DISCOUNT = "loyalty_discount"
    REFERRAL_DISCOUNT = "referral_discount"


class SubscriptionPlan(Base):
    """
    Enterprise Subscription Plan Model
    
    Comprehensive subscription plan management with flexible pricing,
    feature controls, billing cycles, and promotional capabilities.
    """
    __tablename__ = 'subscription_plans'
    
    # Primary identification
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    plan_id = Column(String(100), unique=True, nullable=False, index=True)
    
    # Plan classification
    tier = Column(SQLEnum(PlanTier), nullable=False, index=True)
    status = Column(SQLEnum(PlanStatus), nullable=False, default=PlanStatus.ACTIVE, index=True)
    billing_cycle = Column(SQLEnum(BillingCycle), nullable=False, index=True)
    
    # Plan metadata
    name = Column(String(200), nullable=False)
    display_name = Column(String(200), nullable=True)
    description = Column(Text, nullable=True)
    short_description = Column(String(500), nullable=True)
    tagline = Column(String(200), nullable=True)
    
    # Pricing information
    price = Column(Numeric(10, 2), nullable=False)
    currency = Column(SQLEnum(Currency), nullable=False, default=Currency.USD, index=True)
    setup_fee = Column(Numeric(10, 2), nullable=True)
    cancellation_fee = Column(Numeric(10, 2), nullable=True)
    
    # Multi-currency pricing
    pricing_tiers = Column(JSONB, nullable=True)  # {currency: {price: amount, setup_fee: amount}}
    regional_pricing = Column(JSONB, nullable=True)  # {country_code: {currency: currency, price: amount}}
    
    # Trial and free tier
    trial_period_days = Column(Integer, nullable=True)
    has_free_trial = Column(Boolean, nullable=False, default=False)
    trial_price = Column(Numeric(10, 2), nullable=True)
    grace_period_days = Column(Integer, nullable=False, default=3)
    
    # Feature limits and quotas
    content_upload_limit = Column(Integer, nullable=True)  # Number of uploads per month
    storage_limit_gb = Column(Integer, nullable=True)
    bandwidth_limit_gb = Column(Integer, nullable=True)
    api_calls_limit = Column(Integer, nullable=True)
    collaboration_limit = Column(Integer, nullable=True)
    platform_connections_limit = Column(Integer, nullable=True)
    
    # Content protection features
    copyright_protection = Column(Boolean, nullable=False, default=False)
    automated_monitoring = Column(Boolean, nullable=False, default=False)
    takedown_requests = Column(Integer, nullable=True)  # Per month
    fingerprinting_enabled = Column(Boolean, nullable=False, default=False)
    watermark_protection = Column(Boolean, nullable=False, default=False)
    legal_support = Column(Boolean, nullable=False, default=False)
    
    # AI and analytics features
    ai_recommendations = Column(Boolean, nullable=False, default=False)
    advanced_analytics = Column(Boolean, nullable=False, default=False)
    trend_analysis = Column(Boolean, nullable=False, default=False)
    sentiment_analysis = Column(Boolean, nullable=False, default=False)
    competitor_tracking = Column(Boolean, nullable=False, default=False)
    custom_reports = Column(Boolean, nullable=False, default=False)
    
    # Monetization features
    revenue_tracking = Column(Boolean, nullable=False, default=False)
    automated_payouts = Column(Boolean, nullable=False, default=False)
    multi_currency_support = Column(Boolean, nullable=False, default=False)
    tax_reporting = Column(Boolean, nullable=False, default=False)
    brand_partnerships = Column(Boolean, nullable=False, default=False)
    merchandise_integration = Column(Boolean, nullable=False, default=False)
    
    # Support and service features
    priority_support = Column(Boolean, nullable=False, default=False)
    dedicated_account_manager = Column(Boolean, nullable=False, default=False)
    phone_support = Column(Boolean, nullable=False, default=False)
    chat_support = Column(Boolean, nullable=False, default=False)
    email_support = Column(Boolean, nullable=False, default=True)
    response_time_hours = Column(Integer, nullable=True)
    
    # Platform integrations
    social_platforms_included = Column(ARRAY(String), nullable=True)
    music_platforms_included = Column(ARRAY(String), nullable=True)
    streaming_platforms_included = Column(ARRAY(String), nullable=True)
    premium_integrations = Column(Boolean, nullable=False, default=False)
    
    # Additional features
    white_label_option = Column(Boolean, nullable=False, default=False)
    custom_branding = Column(Boolean, nullable=False, default=False)
    api_access = Column(Boolean, nullable=False, default=False)
    webhook_support = Column(Boolean, nullable=False, default=False)
    sso_support = Column(Boolean, nullable=False, default=False)
    team_collaboration = Column(Boolean, nullable=False, default=False)
    
    # Feature list (detailed)
    included_features = Column(JSONB, nullable=True)
    excluded_features = Column(JSONB, nullable=True)
    feature_comparison = Column(JSONB, nullable=True)
    
    # Billing and payment
    payment_methods_accepted = Column(ARRAY(String), nullable=True)
    invoice_payment_terms = Column(Integer, nullable=True)  # Days
    auto_renewal = Column(Boolean, nullable=False, default=True)
    proration_enabled = Column(Boolean, nullable=False, default=True)
    refund_policy_days = Column(Integer, nullable=True)
    
    # Discounts and promotions
    promotional_price = Column(Numeric(10, 2), nullable=True)
    promotion_end_date = Column(DateTime(timezone=True), nullable=True)
    discount_type = Column(SQLEnum(DiscountType), nullable=True)
    discount_value = Column(Numeric(10, 2), nullable=True)
    coupon_codes = Column(ARRAY(String), nullable=True)
    
    # Upgrade/downgrade rules
    upgrade_allowed = Column(Boolean, nullable=False, default=True)
    downgrade_allowed = Column(Boolean, nullable=False, default=True)
    immediate_upgrade = Column(Boolean, nullable=False, default=True)
    end_of_cycle_downgrade = Column(Boolean, nullable=False, default=True)
    upgrade_discount = Column(Numeric(5, 2), nullable=True)  # Percentage
    
    # Usage tracking and overage
    overage_billing = Column(Boolean, nullable=False, default=False)
    overage_rates = Column(JSONB, nullable=True)  # {feature: {rate: amount, unit: "per_gb"}}
    usage_alerts = Column(Boolean, nullable=False, default=True)
    soft_limits = Column(Boolean, nullable=False, default=True)
    hard_limits = Column(Boolean, nullable=False, default=False)
    
    # Contract and terms
    minimum_commitment_months = Column(Integer, nullable=True)
    contract_length_months = Column(Integer, nullable=True)
    early_termination_fee = Column(Numeric(10, 2), nullable=True)
    terms_url = Column(Text, nullable=True)
    privacy_policy_url = Column(Text, nullable=True)
    
    # Targeting and availability
    target_audience = Column(JSONB, nullable=True)
    geographic_availability = Column(ARRAY(String), nullable=True)
    restricted_countries = Column(ARRAY(String), nullable=True)
    minimum_age = Column(Integer, nullable=True)
    business_only = Column(Boolean, nullable=False, default=False)
    
    # Marketing and presentation
    marketing_headline = Column(String(200), nullable=True)
    value_propositions = Column(ARRAY(String), nullable=True)
    comparison_points = Column(JSONB, nullable=True)
    testimonials = Column(JSONB, nullable=True)
    case_studies = Column(JSONB, nullable=True)
    
    # Visual and branding
    color_scheme = Column(String(20), nullable=True)
    icon_url = Column(Text, nullable=True)
    banner_image_url = Column(Text, nullable=True)
    badge_text = Column(String(50), nullable=True)  # "POPULAR", "BEST VALUE", etc.
    display_order = Column(Integer, nullable=False, default=0)
    
    # Analytics and performance
    subscribers_count = Column(Integer, nullable=False, default=0)
    conversion_rate = Column(Float, nullable=False, default=0.0)
    churn_rate = Column(Float, nullable=False, default=0.0)
    average_lifetime_value = Column(Numeric(10, 2), nullable=True)
    monthly_recurring_revenue = Column(Numeric(12, 2), nullable=False, default=0.00)
    
    # A/B testing
    ab_test_variant = Column(String(50), nullable=True)
    test_group = Column(String(50), nullable=True)
    control_plan = Column(Boolean, nullable=False, default=False)
    test_metrics = Column(JSONB, nullable=True)
    
    # Timing information
    created_at = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc), index=True)
    updated_at = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    launched_at = Column(DateTime(timezone=True), nullable=True, index=True)
    deprecated_at = Column(DateTime(timezone=True), nullable=True)
    
    # Administrative fields
    is_featured = Column(Boolean, nullable=False, default=False, index=True)
    is_recommended = Column(Boolean, nullable=False, default=False)
    is_popular = Column(Boolean, nullable=False, default=False)
    is_enterprise_only = Column(Boolean, nullable=False, default=False)
    requires_approval = Column(Boolean, nullable=False, default=False)
    
    # Audit trail
    created_by = Column(String(100), nullable=False)
    updated_by = Column(String(100), nullable=True)
    approved_by = Column(String(100), nullable=True)
    notes = Column(Text, nullable=True)
    
    # Advanced indexing
    __table_args__ = (
        Index('idx_subscription_plan_tier_status', 'tier', 'status'),
        Index('idx_subscription_plan_price_currency', 'price', 'currency'),
        Index('idx_subscription_plan_billing_cycle', 'billing_cycle'),
        Index('idx_subscription_plan_featured_popular', 'is_featured', 'is_popular'),
        Index('idx_subscription_plan_launched_deprecated', 'launched_at', 'deprecated_at'),
        Index('idx_subscription_plan_trial', 'has_free_trial', 'trial_period_days'),
        Index('idx_subscription_plan_conversion', 'conversion_rate'),
        Index('idx_subscription_plan_mrr', 'monthly_recurring_revenue'),
        Index('idx_subscription_plan_display_order', 'display_order'),
        Index('idx_subscription_plan_enterprise', 'is_enterprise_only', 'requires_approval'),
    )
    
    def __repr__(self):
        return f"<SubscriptionPlan(id={self.id}, name={self.name}, tier={self.tier.value}, price={self.price})>"
    
    @classmethod
    def create_basic_plan(cls) -> 'SubscriptionPlan':
        """Create a basic subscription plan"""
        return cls(
            tier=PlanTier.BASIC,
            name="Basic Plan",
            display_name="Basic",
            description="Perfect for getting started with content protection",
            price=Decimal('9.99'),
            currency=Currency.USD,
            billing_cycle=BillingCycle.MONTHLY,
            has_free_trial=True,
            trial_period_days=14,
            content_upload_limit=100,
            storage_limit_gb=10,
            copyright_protection=True,
            ai_recommendations=True,
            email_support=True,
            plan_id=f"basic_{uuid.uuid4().hex[:8]}",
            created_by="system"
        )
    
    @classmethod
    def create_premium_plan(cls) -> 'SubscriptionPlan':
        """Create a premium subscription plan"""
        return cls(
            tier=PlanTier.PREMIUM,
            name="Premium Plan",
            display_name="Premium",
            description="Advanced features for professional creators",
            price=Decimal('29.99'),
            currency=Currency.USD,
            billing_cycle=BillingCycle.MONTHLY,
            has_free_trial=True,
            trial_period_days=14,
            content_upload_limit=1000,
            storage_limit_gb=100,
            copyright_protection=True,
            automated_monitoring=True,
            takedown_requests=50,
            fingerprinting_enabled=True,
            ai_recommendations=True,
            advanced_analytics=True,
            trend_analysis=True,
            priority_support=True,
            chat_support=True,
            plan_id=f"premium_{uuid.uuid4().hex[:8]}",
            created_by="system"
        )
    
    def calculate_monthly_price(self) -> Decimal:
        """Calculate equivalent monthly price for any billing cycle"""
        if self.billing_cycle == BillingCycle.MONTHLY:
            return self.price
        elif self.billing_cycle == BillingCycle.QUARTERLY:
            return self.price / 3
        elif self.billing_cycle == BillingCycle.SEMI_ANNUALLY:
            return self.price / 6
        elif self.billing_cycle == BillingCycle.ANNUALLY:
            return self.price / 12
        elif self.billing_cycle == BillingCycle.WEEKLY:
            return self.price * 4.33  # Average weeks per month
        else:
            return self.price
    
    def calculate_annual_savings(self, monthly_plan: 'SubscriptionPlan') -> Decimal:
        """
Calculate annual savings compared to monthly billing"""
        if self.billing_cycle != BillingCycle.ANNUALLY:
            return Decimal('0.00')
        
        monthly_annual_cost = monthly_plan.price * 12
        annual_cost = self.price
        return monthly_annual_cost - annual_cost
    
    def get_effective_price(self, apply_promotion: bool = True) -> Decimal:
        """
Get effective price considering promotions"""
        base_price = self.price
        
        if apply_promotion and self.promotional_price and self.promotion_end_date:
            if datetime.now(timezone.utc) <= self.promotion_end_date:
                return self.promotional_price
        
        return base_price
    
    def is_trial_available(self) -> bool:
        """
Check if free trial is available"""
        return (
            self.has_free_trial and
            self.trial_period_days and
            self.trial_period_days > 0 and
            self.status == PlanStatus.ACTIVE
        )
    
    def get_feature_list(self) -> List[str]:
        """
Get comprehensive list of included features"""
        features = []
        
        # Storage and limits
        if self.content_upload_limit:
            features.append(f"Up to {self.content_upload_limit:,} content uploads per month")
        if self.storage_limit_gb:
            features.append(f"{self.storage_limit_gb} GB storage")
        if self.bandwidth_limit_gb:
            features.append(f"{self.bandwidth_limit_gb} GB bandwidth")
        
        # Protection features
        if self.copyright_protection:
            features.append("Copyright protection")
        if self.automated_monitoring:
            features.append("Automated content monitoring")
        if self.fingerprinting_enabled:
            features.append("Content fingerprinting")
        if self.watermark_protection:
            features.append("Watermark protection")
        if self.takedown_requests:
            features.append(f"{self.takedown_requests} takedown requests per month")
        if self.legal_support:
            features.append("Legal support")
        
        # AI features
        if self.ai_recommendations:
            features.append("AI-powered recommendations")
        if self.advanced_analytics:
            features.append("Advanced analytics")
        if self.trend_analysis:
            features.append("Trend analysis")
        if self.sentiment_analysis:
            features.append("Sentiment analysis")
        if self.competitor_tracking:
            features.append("Competitor tracking")
        
        # Support features
        if self.priority_support:
            features.append("Priority support")
        if self.phone_support:
            features.append("Phone support")
        if self.chat_support:
            features.append("Live chat support")
        if self.dedicated_account_manager:
            features.append("Dedicated account manager")
        
        # Additional features from JSONB
        if self.included_features:
            features.extend(self.included_features.get('features', []))
        
        return features
    
    def compare_with_plan(self, other_plan: 'SubscriptionPlan') -> Dict[str, Any]:
        """Compare this plan with another plan"""
        comparison = {
            'price_difference': float(other_plan.price - self.price),
            'price_difference_monthly': float(other_plan.calculate_monthly_price() - self.calculate_monthly_price()),
            'feature_differences': {
                'advantages': [],
                'disadvantages': []
            }
        }
        
        # Compare key features
        feature_map = {
            'copyright_protection': 'Copyright Protection',
            'automated_monitoring': 'Automated Monitoring',
            'ai_recommendations': 'AI Recommendations',
            'advanced_analytics': 'Advanced Analytics',
            'priority_support': 'Priority Support',
            'legal_support': 'Legal Support'
        }
        
        for feature, display_name in feature_map.items():
            self_has = getattr(self, feature, False)
            other_has = getattr(other_plan, feature, False)
            
            if self_has and not other_has:
                comparison['feature_differences']['advantages'].append(display_name)
            elif not self_has and other_has:
                comparison['feature_differences']['disadvantages'].append(display_name)
        
        return comparison
    
    def get_pricing_summary(self) -> Dict[str, Any]:
        """
Get comprehensive pricing summary"""
        return {
            'base_pricing': {
                'price': float(self.price),
                'currency': self.currency.value,
                'billing_cycle': self.billing_cycle.value,
                'monthly_equivalent': float(self.calculate_monthly_price())
            },
            'trial_info': {
                'has_trial': self.has_free_trial,
                'trial_days': self.trial_period_days,
                'trial_price': float(self.trial_price) if self.trial_price else 0.0
            },
            'additional_fees': {
                'setup_fee': float(self.setup_fee) if self.setup_fee else 0.0,
                'cancellation_fee': float(self.cancellation_fee) if self.cancellation_fee else 0.0
            },
            'promotional': {
                'promotional_price': float(self.promotional_price) if self.promotional_price else None,
                'promotion_ends': self.promotion_end_date.isoformat() if self.promotion_end_date else None,
                'discount_type': self.discount_type.value if self.discount_type else None
            }
        }
    
    def update_metrics(self, new_subscribers: int = 0, churned_subscribers: int = 0) -> None:
        """
Update plan metrics"""
        self.subscribers_count = max(0, self.subscribers_count + new_subscribers - churned_subscribers)
        
        # Calculate MRR
        monthly_price = self.calculate_monthly_price()
        self.monthly_recurring_revenue = monthly_price * self.subscribers_count
        
        self.updated_at = datetime.now(timezone.utc)
    
    def is_available_for_user(self, user_location: str = None, user_type: str = None) -> bool:
        """
Check if plan is available for a specific user"""
        if self.status != PlanStatus.ACTIVE:
            return False
        
        # Check geographic availability
        if self.geographic_availability and user_location:
            if user_location not in self.geographic_availability:
                return False
        
        if self.restricted_countries and user_location:
            if user_location in self.restricted_countries:
                return False
        
        # Check business restrictions
        if self.business_only and user_type != "business":
            return False
        
        return True
    
    def calculate_upgrade_cost(self, current_plan: 'SubscriptionPlan', days_remaining: int) -> Decimal:
        """Calculate prorated upgrade cost"""
        if not self.proration_enabled:
            return self.price
        
        # Calculate daily rates
        current_daily_rate = current_plan.calculate_monthly_price() / 30
        new_daily_rate = self.calculate_monthly_price() / 30
        
        # Calculate prorated difference
        daily_difference = new_daily_rate - current_daily_rate
        prorated_cost = daily_difference * days_remaining
        
        return max(Decimal('0.00'), prorated_cost)
