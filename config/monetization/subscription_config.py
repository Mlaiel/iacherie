"""
Subscription Configuration Module
================================

Professional subscription management configuration for IA-Influencer platform.
Advanced subscription lifecycle, billing management, and customer retention features.

Author: Fahed Mlaiel <mlaiel@live.de>
Project: IA-Influencer Agent + Content Protection Platform
Team: Lead Dev IA + Backend Senior + ML Engineer + DBA + Security + Microservices + Audio + DevOps + Product Strategy

Copyright Notice:
This code is the intellectual property of Fahed Mlaiel.
Any unauthorized use, reproduction, or distribution of this code
without explicit written permission from the author is strictly prohibited.

Contact: mlaiel@live.de for licensing inquiries.
"""

import os
from decimal import Decimal
from typing import Dict, List, Optional, Any, Set, Union
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta


class SubscriptionStatus(str, Enum):
    """Comprehensive subscription status states."""
    ACTIVE = "active"
    INACTIVE = "inactive"
    PENDING = "pending"
    TRIALING = "trialing"
    PAUSED = "paused"
    SUSPENDED = "suspended"
    CANCELLED = "cancelled"
    EXPIRED = "expired"
    PENDING_CANCELLATION = "pending_cancellation"
    PAST_DUE = "past_due"
    UNPAID = "unpaid"
    INCOMPLETE = "incomplete"
    INCOMPLETE_EXPIRED = "incomplete_expired"
    CHURNED = "churned"
    REACTIVATED = "reactivated"


class SubscriptionType(str, Enum):
    """Types of subscriptions available."""
    STANDARD = "standard"
    PREMIUM = "premium"
    ENTERPRISE = "enterprise"
    CUSTOM = "custom"
    ADDON = "addon"
    BUNDLE = "bundle"
    USAGE_BASED = "usage_based"
    HYBRID = "hybrid"
    PARTNER = "partner"
    RESELLER = "reseller"


class BillingInterval(str, Enum):
    """Billing frequency options."""
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    SEMI_ANNUALLY = "semi_annually"
    ANNUALLY = "annually"
    BIANNUALLY = "biannually"
    USAGE_BASED = "usage_based"
    ONE_TIME = "one_time"


class PaymentStatus(str, Enum):
    """Payment attempt status."""
    PENDING = "pending"
    PROCESSING = "processing"
    SUCCEEDED = "succeeded"
    FAILED = "failed"
    CANCELLED = "cancelled"
    REFUNDED = "refunded"
    PARTIALLY_REFUNDED = "partially_refunded"
    DISPUTED = "disputed"
    CHARGEBACK = "chargeback"
    AUTHORIZED = "authorized"
    CAPTURED = "captured"


class RenewalAction(str, Enum):
    """Actions to take on subscription renewal."""
    AUTO_RENEW = "auto_renew"
    REQUIRE_CONFIRMATION = "require_confirmation"
    PAUSE = "pause"
    CANCEL = "cancel"
    DOWNGRADE = "downgrade"
    UPGRADE = "upgrade"
    CUSTOM_ACTION = "custom_action"


class ChurnReason(str, Enum):
    """Reasons for subscription cancellation."""
    PRICE_TOO_HIGH = "price_too_high"
    LACK_OF_FEATURES = "lack_of_features"
    POOR_PERFORMANCE = "poor_performance"
    CUSTOMER_SUPPORT = "customer_support"
    COMPETITOR_OFFERING = "competitor_offering"
    BUSINESS_CLOSURE = "business_closure"
    TECHNICAL_ISSUES = "technical_issues"
    NOT_USING_ENOUGH = "not_using_enough"
    FOUND_ALTERNATIVE = "found_alternative"
    OTHER = "other"


@dataclass
class BillingCycle:
    """Comprehensive billing cycle configuration."""
    interval: BillingInterval
    interval_count: int = 1  # e.g., every 2 months
    anchor_day: Optional[int] = None  # Day of month for billing
    trial_period_days: int = 0
    grace_period_days: int = 3  # Grace period for failed payments
    
    # Proration settings
    prorate_upgrades: bool = True
    prorate_downgrades: bool = False
    
    # Invoice settings
    invoice_generation_days_before: int = 7
    payment_due_days: int = 7
    late_fee_enabled: bool = False
    late_fee_amount: Decimal = Decimal("0.00")
    late_fee_percentage: Decimal = Decimal("0.00")


@dataclass
class RetryPolicy:
    """Payment retry configuration for failed payments."""
    enabled: bool = True
    max_attempts: int = 4
    retry_schedule_days: List[int] = field(default_factory=lambda: [3, 7, 14, 21])
    exponential_backoff: bool = False
    
    # Smart retry features
    adapt_to_payment_method: bool = True
    avoid_weekends: bool = True
    consider_timezone: bool = True
    
    # Dunning management
    send_retry_notifications: bool = True
    escalate_to_collections: bool = True
    auto_cancel_after_retries: bool = True


@dataclass
class TrialConfiguration:
    """Free trial configuration options."""
    enabled: bool = True
    duration_days: int = 14
    
    # Trial types
    credit_card_required: bool = True
    auto_convert: bool = True
    send_trial_reminders: bool = True
    reminder_schedule_days: List[int] = field(default_factory=lambda: [7, 3, 1])
    
    # Trial extensions
    allow_extensions: bool = False
    max_extensions: int = 1
    extension_duration_days: int = 7
    
    # Feature access during trial
    full_feature_access: bool = True
    limited_usage_trial: bool = False
    trial_usage_limits: Dict[str, int] = field(default_factory=dict)


@dataclass
class CancellationPolicy:
    """Subscription cancellation and retention policies."""
    # Immediate vs. end of period cancellation
    immediate_cancellation: bool = False
    cancel_at_period_end: bool = True
    
    # Retention efforts
    enable_retention_offers: bool = True
    pause_option_enabled: bool = True
    max_pause_duration_months: int = 3
    
    # Win-back campaigns
    enable_winback: bool = True
    winback_discount_percentage: Decimal = Decimal("25.0")
    winback_duration_months: int = 6
    
    # Refund policy
    refund_policy_days: int = 30
    pro_rated_refunds: bool = True
    administrative_fee: Decimal = Decimal("0.00")


@dataclass
class UsageTrackingConfig:
    """Configuration for usage-based billing components."""
    enabled: bool = True
    
    # Tracking settings
    real_time_tracking: bool = True
    batch_processing: bool = False
    batch_interval_hours: int = 24
    
    # Usage aggregation
    aggregation_period: str = "monthly"  # hourly, daily, weekly, monthly
    usage_rounding_precision: int = 2
    minimum_usage_charge: Decimal = Decimal("0.01")
    
    # Overage handling
    overage_notifications: bool = True
    overage_thresholds: List[int] = field(default_factory=lambda: [80, 90, 100])
    auto_upgrade_on_overage: bool = False
    overage_cap_enabled: bool = True
    overage_cap_amount: Optional[Decimal] = None


@dataclass
class AddOnConfiguration:
    """Add-on products and services configuration."""
    enabled: bool = True
    
    # Available add-ons
    available_addons: Dict[str, Dict[str, Any]] = field(default_factory=lambda: {
        "extra_storage": {
            "name": "Extra Storage",
            "description": "Additional cloud storage space",
            "price_per_gb": Decimal("0.10"),
            "billing_interval": BillingInterval.MONTHLY,
            "minimum_purchase": 10
        },
        "priority_support": {
            "name": "Priority Support",
            "description": "24/7 priority customer support",
            "monthly_price": Decimal("29.99"),
            "billing_interval": BillingInterval.MONTHLY
        },
        "advanced_analytics": {
            "name": "Advanced Analytics",
            "description": "Comprehensive analytics and insights",
            "monthly_price": Decimal("19.99"),
            "billing_interval": BillingInterval.MONTHLY
        },
        "white_label": {
            "name": "White Label",
            "description": "Custom branding and white-label solution",
            "monthly_price": Decimal("99.99"),
            "billing_interval": BillingInterval.MONTHLY,
            "minimum_tier": "professional"
        },
        "api_access": {
            "name": "Extended API Access",
            "description": "Higher API rate limits and advanced features",
            "monthly_price": Decimal("49.99"),
            "billing_interval": BillingInterval.MONTHLY,
            "rate_limit_multiplier": 10
        }
    })
    
    # Add-on management
    allow_midcycle_changes: bool = True
    prorate_addon_changes: bool = True
    minimum_addon_duration_months: int = 1


@dataclass
class SubscriptionMetrics:
    """Subscription business metrics configuration."""
    # Key metrics tracking
    track_churn_rate: bool = True
    track_ltv: bool = True
    track_mrr: bool = True
    track_arr: bool = True
    
    # Cohort analysis
    cohort_analysis_enabled: bool = True
    cohort_periods: List[str] = field(default_factory=lambda: ["monthly", "quarterly", "yearly"])
    
    # Revenue recognition
    revenue_recognition_method: str = "accrual"  # accrual or cash
    deferred_revenue_tracking: bool = True
    
    # Customer segmentation
    segment_by_value: bool = True
    segment_by_usage: bool = True
    segment_by_tenure: bool = True
    
    # Predictive analytics
    churn_prediction_enabled: bool = True
    ltv_prediction_enabled: bool = True
    upsell_prediction_enabled: bool = True


@dataclass
class NotificationConfig:
    """Subscription-related notification configuration."""
    # Payment notifications
    payment_succeeded: bool = True
    payment_failed: bool = True
    payment_retry: bool = True
    
    # Subscription lifecycle
    subscription_created: bool = True
    subscription_updated: bool = True
    subscription_cancelled: bool = True
    subscription_reactivated: bool = True
    
    # Trial notifications
    trial_started: bool = True
    trial_ending_reminder: bool = True
    trial_converted: bool = True
    trial_expired: bool = True
    
    # Usage notifications
    usage_threshold_reached: bool = True
    overage_alert: bool = True
    usage_report: bool = True
    
    # Invoice notifications
    invoice_generated: bool = True
    invoice_payment_due: bool = True
    invoice_overdue: bool = True
    
    # Delivery channels
    email_notifications: bool = True
    webhook_notifications: bool = True
    in_app_notifications: bool = True
    sms_notifications: bool = False


@dataclass
class SubscriptionConfig:
    """Professional subscription management configuration."""
    
    # Global Subscription Settings
    ENABLE_SUBSCRIPTIONS: bool = True
    DEFAULT_CURRENCY: str = "EUR"
    DEFAULT_BILLING_INTERVAL: BillingInterval = BillingInterval.MONTHLY
    
    # Subscription Lifecycle
    AUTO_RENEWAL_ENABLED: bool = True
    GRACE_PERIOD_ENABLED: bool = True
    DEFAULT_GRACE_PERIOD_DAYS: int = 3
    
    # Trial Configuration
    TRIAL_CONFIG: TrialConfiguration = TrialConfiguration()
    
    # Billing Cycles
    AVAILABLE_BILLING_CYCLES: Dict[BillingInterval, BillingCycle] = field(
        default_factory=lambda: {
            BillingInterval.MONTHLY: BillingCycle(
                interval=BillingInterval.MONTHLY,
                trial_period_days=14,
                grace_period_days=3,
                invoice_generation_days_before=7,
                payment_due_days=7
            ),
            BillingInterval.QUARTERLY: BillingCycle(
                interval=BillingInterval.QUARTERLY,
                trial_period_days=14,
                grace_period_days=5,
                invoice_generation_days_before=14,
                payment_due_days=14
            ),
            BillingInterval.ANNUALLY: BillingCycle(
                interval=BillingInterval.ANNUALLY,
                trial_period_days=30,
                grace_period_days=7,
                invoice_generation_days_before=30,
                payment_due_days=30
            )
        }
    )
    
    # Payment Retry Policy
    RETRY_POLICY: RetryPolicy = RetryPolicy()
    
    # Cancellation Settings
    CANCELLATION_POLICY: CancellationPolicy = CancellationPolicy()
    
    # Usage-Based Billing
    USAGE_TRACKING: UsageTrackingConfig = UsageTrackingConfig()
    
    # Add-ons Configuration
    ADDONS_CONFIG: AddOnConfiguration = AddOnConfiguration()
    
    # Subscription Status Transitions
    ALLOWED_STATUS_TRANSITIONS: Dict[SubscriptionStatus, List[SubscriptionStatus]] = field(
        default_factory=lambda: {
            SubscriptionStatus.PENDING: [
                SubscriptionStatus.ACTIVE,
                SubscriptionStatus.CANCELLED,
                SubscriptionStatus.EXPIRED
            ],
            SubscriptionStatus.TRIALING: [
                SubscriptionStatus.ACTIVE,
                SubscriptionStatus.CANCELLED,
                SubscriptionStatus.EXPIRED
            ],
            SubscriptionStatus.ACTIVE: [
                SubscriptionStatus.PAUSED,
                SubscriptionStatus.SUSPENDED,
                SubscriptionStatus.CANCELLED,
                SubscriptionStatus.PENDING_CANCELLATION,
                SubscriptionStatus.PAST_DUE
            ],
            SubscriptionStatus.PAUSED: [
                SubscriptionStatus.ACTIVE,
                SubscriptionStatus.CANCELLED,
                SubscriptionStatus.EXPIRED
            ],
            SubscriptionStatus.SUSPENDED: [
                SubscriptionStatus.ACTIVE,
                SubscriptionStatus.CANCELLED
            ],
            SubscriptionStatus.PAST_DUE: [
                SubscriptionStatus.ACTIVE,
                SubscriptionStatus.CANCELLED,
                SubscriptionStatus.UNPAID
            ],
            SubscriptionStatus.CANCELLED: [
                SubscriptionStatus.REACTIVATED
            ]
        }
    )
    
    # Subscription Business Rules
    BUSINESS_RULES: Dict[str, Any] = field(default_factory=lambda: {
        "allow_plan_changes": True,
        "immediate_plan_changes": False,
        "prorate_plan_changes": True,
        "allow_multiple_subscriptions": False,
        "require_payment_method": True,
        "auto_pause_on_failed_payment": False,
        "max_failed_payments_before_cancellation": 3,
        "send_payment_reminders": True,
        "dunning_management_enabled": True,
        "retention_campaigns_enabled": True
    })
    
    # Metrics and Analytics
    METRICS_CONFIG: SubscriptionMetrics = SubscriptionMetrics()
    
    # Notifications
    NOTIFICATION_CONFIG: NotificationConfig = NotificationConfig()
    
    # Subscription Tiers Integration
    TIER_SPECIFIC_SETTINGS: Dict[str, Dict[str, Any]] = field(default_factory=lambda: {
        "free": {
            "max_subscriptions": 1,
            "require_credit_card": False,
            "auto_cancel_on_upgrade": True,
            "retention_efforts": False
        },
        "basic": {
            "max_subscriptions": 1,
            "require_credit_card": True,
            "allow_pause": True,
            "retention_discount_max": Decimal("20.0")
        },
        "professional": {
            "max_subscriptions": 5,
            "priority_support": True,
            "extended_trial": 30,
            "retention_discount_max": Decimal("30.0")
        },
        "premium": {
            "max_subscriptions": 10,
            "dedicated_support": True,
            "custom_billing_terms": True,
            "retention_discount_max": Decimal("40.0")
        },
        "enterprise": {
            "max_subscriptions": -1,  # unlimited
            "custom_contracts": True,
            "sla_guarantees": True,
            "negotiated_terms": True
        }
    })
    
    # Compliance and Legal
    COMPLIANCE_SETTINGS: Dict[str, Any] = field(default_factory=lambda: {
        "gdpr_compliant": True,
        "ccpa_compliant": True,
        "pci_dss_compliant": True,
        "auto_delete_cancelled_data_days": 90,
        "data_retention_years": 7,
        "consent_tracking": True,
        "right_to_be_forgotten": True,
        "data_portability": True
    })
    
    # Performance and Scalability
    PERFORMANCE_SETTINGS: Dict[str, Any] = field(default_factory=lambda: {
        "subscription_cache_ttl_seconds": 300,
        "batch_billing_enabled": True,
        "batch_size": 1000,
        "async_processing": True,
        "rate_limiting_enabled": True,
        "circuit_breaker_enabled": True,
        "health_check_interval_minutes": 5
    })
    
    # Webhook Configuration
    WEBHOOK_SETTINGS: Dict[str, Any] = field(default_factory=lambda: {
        "enabled": True,
        "retry_attempts": 3,
        "timeout_seconds": 30,
        "signature_verification": True,
        "events": [
            "subscription.created",
            "subscription.updated",
            "subscription.cancelled",
            "subscription.reactivated",
            "payment.succeeded",
            "payment.failed",
            "trial.ended",
            "invoice.created",
            "invoice.paid"
        ]
    })
    
    def get_billing_cycle_config(self, interval: BillingInterval) -> Optional[BillingCycle]:
        """Get billing cycle configuration for specific interval."""



        return self.AVAILABLE_BILLING_CYCLES.get(interval)
    
    def is_status_transition_allowed(self, from_status: SubscriptionStatus, 
                                   to_status: SubscriptionStatus) -> bool:
        """Check if status transition is allowed."""
        allowed_transitions = self.ALLOWED_STATUS_TRANSITIONS.get(from_status, [])
        return to_status in allowed_transitions
    
    def get_tier_settings(self, tier: str) -> Dict[str, Any]:
        """Get tier-specific subscription settings."""



        return self.TIER_SPECIFIC_SETTINGS.get(tier.lower(), {})
    
    def calculate_proration(self, old_price: Decimal, new_price: Decimal, 
                           days_remaining: int, days_in_period: int) -> Decimal:
        """Calculate prorated amount for plan changes."""
        if not self.BUSINESS_RULES.get("prorate_plan_changes", True):
            return Decimal("0.00")
        
        # Calculate unused portion of current period
        unused_amount = old_price * (Decimal(str(days_remaining)) / Decimal(str(days_in_period)))
        
        # Calculate new amount for remaining period
        new_amount = new_price * (Decimal(str(days_remaining)) / Decimal(str(days_in_period)))
        
        # Return the difference (can be positive or negative)
        return new_amount - unused_amount
    
    def get_retention_offer(self, subscription_value: Decimal, 
                           tier: str, churn_reason: ChurnReason) -> Dict[str, Any]:
        """Generate retention offer based on subscription value and churn reason."""
        tier_settings = self.get_tier_settings(tier)
        max_discount = tier_settings.get("retention_discount_max", Decimal("20.0"))
        
        # Base retention offers by churn reason
        retention_offers = {
            ChurnReason.PRICE_TOO_HIGH: {
                "discount_percentage": min(max_discount, Decimal("30.0")),
                "duration_months": 6,
                "offer_type": "discount"
            },
            ChurnReason.LACK_OF_FEATURES: {
                "upgrade_discount": Decimal("50.0"),
                "duration_months": 3,
                "offer_type": "upgrade_discount"
            },
            ChurnReason.NOT_USING_ENOUGH: {
                "pause_months": 3,
                "offer_type": "pause"
            },
            ChurnReason.TECHNICAL_ISSUES: {
                "free_months": 1,
                "priority_support": True,
                "offer_type": "compensation"
            }
        }
        
        return retention_offers.get(churn_reason, {
            "discount_percentage": Decimal("15.0"),
            "duration_months": 3,
            "offer_type": "generic_discount"
        })


# Global configuration instance
subscription_config = SubscriptionConfig()

import os
from decimal import Decimal
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta


class SubscriptionStatus(str, Enum):
    """Subscription status types."""
    ACTIVE = "active"
    TRIAL = "trial"
    PAST_DUE = "past_due"
    CANCELLED = "cancelled"
    SUSPENDED = "suspended"
    EXPIRED = "expired"
    PENDING = "pending"
    INCOMPLETE = "incomplete"
    PAUSED = "paused"


class BillingCycle(str, Enum):
    """Billing cycle options."""
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    SEMI_ANNUALLY = "semi_annually"
    ANNUALLY = "annually"
    LIFETIME = "lifetime"


class SubscriptionEvent(str, Enum):
    """Subscription event types."""
    CREATED = "created"
    ACTIVATED = "activated"
    RENEWED = "renewed"
    UPGRADED = "upgraded"
    DOWNGRADED = "downgraded"
    CANCELLED = "cancelled"
    SUSPENDED = "suspended"
    RESUMED = "resumed"
    EXPIRED = "expired"
    PAYMENT_FAILED = "payment_failed"
    PAYMENT_SUCCEEDED = "payment_succeeded"
    TRIAL_STARTED = "trial_started"
    TRIAL_ENDED = "trial_ended"


class RenewalPolicy(str, Enum):
    """Subscription renewal policies."""
    AUTOMATIC = "automatic"
    MANUAL = "manual"
    GRACE_PERIOD = "grace_period"
    IMMEDIATE_CANCEL = "immediate_cancel"


@dataclass
class TrialConfig:
    """Trial period configuration."""
    enabled: bool = True
    duration_days: int = 14
    requires_payment_method: bool = True
    auto_convert: bool = True
    notification_days_before_end: List[int] = field(default_factory=lambda: [7, 3, 1])
    max_trials_per_user: int = 1
    trial_extensions_allowed: int = 0


@dataclass
class GracePeriodConfig:
    """Grace period configuration for failed payments."""
    enabled: bool = True
    duration_days: int = 5
    retry_attempts: int = 3
    retry_interval_hours: int = 24
    downgrade_after_grace: bool = False
    cancel_after_grace: bool = True


@dataclass
class ProrationConfig:
    """Proration configuration for subscription changes."""
    enabled: bool = True
    prorate_upgrades: bool = True
    prorate_downgrades: bool = False
    credit_unused_time: bool = True
    minimum_proration_amount: Decimal = Decimal("1.00")


@dataclass
class CancellationConfig:
    """Cancellation policy configuration."""
    allow_immediate_cancellation: bool = True
    allow_end_of_period_cancellation: bool = True
    cancellation_survey_required: bool = True
    retention_offers_enabled: bool = True
    refund_policy_days: int = 30
    partial_refunds_enabled: bool = True
    exit_survey_incentive: Optional[Decimal] = None


@dataclass
class SubscriptionTierConfig:
    """Configuration for subscription tiers."""
    tier_id: str
    name: str
    description: str
    monthly_price: Decimal
    quarterly_price: Optional[Decimal]
    semi_annual_price: Optional[Decimal]
    annual_price: Decimal
    currency: str
    features: List[str]
    usage_limits: Dict[str, Union[int, str]]
    trial_config: TrialConfig
    is_popular: bool = False
    is_enterprise: bool = False
    minimum_commitment_months: int = 0
    setup_fee: Decimal = Decimal("0.00")
    early_termination_fee: Decimal = Decimal("0.00")


@dataclass
class SubscriptionConfig:
    """Main subscription configuration class."""
    
    # Database Configuration
    DATABASE_URL: str = os.getenv(
        "SUBSCRIPTION_DB_URL", 
        "postgresql://user:pass@localhost:5432/subscription_db"
    )
    
    # Default Settings
    DEFAULT_CURRENCY: str = "EUR"
    DEFAULT_BILLING_CYCLE: BillingCycle = BillingCycle.MONTHLY
    DEFAULT_RENEWAL_POLICY: RenewalPolicy = RenewalPolicy.AUTOMATIC
    
    # Global Trial Configuration
    GLOBAL_TRIAL_CONFIG: TrialConfig = TrialConfig(
        enabled=True,
        duration_days=14,
        requires_payment_method=True,
        auto_convert=True,
        notification_days_before_end=[7, 3, 1],
        max_trials_per_user=1,
        trial_extensions_allowed=1
    )
    
    # Grace Period Configuration
    GRACE_PERIOD_CONFIG: GracePeriodConfig = GracePeriodConfig(
        enabled=True,
        duration_days=5,
        retry_attempts=3,
        retry_interval_hours=24,
        downgrade_after_grace=False,
        cancel_after_grace=True
    )
    
    # Proration Configuration
    PRORATION_CONFIG: ProrationConfig = ProrationConfig(
        enabled=True,
        prorate_upgrades=True,
        prorate_downgrades=False,
        credit_unused_time=True,
        minimum_proration_amount=Decimal("1.00")
    )
    
    # Cancellation Configuration
    CANCELLATION_CONFIG: CancellationConfig = CancellationConfig(
        allow_immediate_cancellation=True,
        allow_end_of_period_cancellation=True,
        cancellation_survey_required=True,
        retention_offers_enabled=True,
        refund_policy_days=30,
        partial_refunds_enabled=True,
        exit_survey_incentive=Decimal("5.00")
    )
    
    # Subscription Tiers Configuration
    SUBSCRIPTION_TIERS: Dict[str, SubscriptionTierConfig] = field(
        default_factory=lambda: {
            "free": SubscriptionTierConfig(
                tier_id="free",
                name="Free Starter",
                description="Perfect for exploring content protection",
                monthly_price=Decimal("0.00"),
                quarterly_price=None,
                semi_annual_price=None,
                annual_price=Decimal("0.00"),
                currency="EUR",
                features=[
                    "10 content uploads per month",
                    "1 GB storage",
                    "100 fingerprint checks",
                    "2 platforms monitored",
                    "Basic email support"
                ],
                usage_limits={
                    "uploads": 10,
                    "storage_gb": 1,
                    "fingerprint_checks": 100,
                    "platforms": 2,
                    "api_calls": 1000
                },
                trial_config=TrialConfig(enabled=False, duration_days=0)
            ),
            "creator_basic": SubscriptionTierConfig(
                tier_id="creator_basic",
                name="Creator Basic",
                description="Essential tools for content creators",
                monthly_price=Decimal("19.99"),
                quarterly_price=Decimal("54.99"),  # 8% discount
                semi_annual_price=Decimal("104.99"),  # 13% discount
                annual_price=Decimal("199.99"),  # 17% discount
                currency="EUR",
                features=[
                    "100 content uploads per month",
                    "10 GB storage",
                    "1,000 fingerprint checks",
                    "5 platforms monitored",
                    "Revenue tracking",
                    "Priority email support",
                    "Mobile app access"
                ],
                usage_limits={
                    "uploads": 100,
                    "storage_gb": 10,
                    "fingerprint_checks": 1000,
                    "platforms": 5,
                    "api_calls": 10000,
                    "revenue_tracking": "basic"
                },
                trial_config=TrialConfig(
                    enabled=True,
                    duration_days=14,
                    requires_payment_method=True,
                    auto_convert=True
                )
            ),
            "creator_pro": SubscriptionTierConfig(
                tier_id="creator_pro",
                name="Creator Pro",
                description="Advanced features for serious creators",
                monthly_price=Decimal("49.99"),
                quarterly_price=Decimal("134.99"),  # 10% discount
                semi_annual_price=Decimal("254.99"),  # 15% discount
                annual_price=Decimal("499.99"),  # 17% discount
                currency="EUR",
                features=[
                    "500 content uploads per month",
                    "50 GB storage",
                    "5,000 fingerprint checks",
                    "10 platforms monitored",
                    "Advanced revenue tracking",
                    "Detailed analytics",
                    "Priority support",
                    "API access",
                    "Bulk operations"
                ],
                usage_limits={
                    "uploads": 500,
                    "storage_gb": 50,
                    "fingerprint_checks": 5000,
                    "platforms": 10,
                    "api_calls": 50000,
                    "revenue_tracking": "advanced",
                    "analytics": "detailed"
                },
                trial_config=TrialConfig(
                    enabled=True,
                    duration_days=14,
                    requires_payment_method=True,
                    auto_convert=True
                ),
                is_popular=True
            ),
            "creator_premium": SubscriptionTierConfig(
                tier_id="creator_premium",
                name="Creator Premium",
                description="Complete solution for professional creators",
                monthly_price=Decimal("99.99"),
                quarterly_price=Decimal("269.99"),  # 10% discount
                semi_annual_price=Decimal("519.99"),  # 13% discount
                annual_price=Decimal("999.99"),  # 17% discount
                currency="EUR",
                features=[
                    "Unlimited content uploads",
                    "200 GB storage",
                    "Unlimited fingerprint checks",
                    "All platforms monitored",
                    "Enterprise revenue tracking",
                    "Advanced analytics",
                    "24/7 priority support",
                    "Full API access",
                    "White-label options",
                    "Custom integrations"
                ],
                usage_limits={
                    "uploads": "unlimited",
                    "storage_gb": 200,
                    "fingerprint_checks": "unlimited",
                    "platforms": "unlimited",
                    "api_calls": "unlimited",
                    "revenue_tracking": "enterprise",
                    "analytics": "advanced",
                    "white_label": True
                },
                trial_config=TrialConfig(
                    enabled=True,
                    duration_days=14,
                    requires_payment_method=True,
                    auto_convert=True
                )
            ),
            "enterprise": SubscriptionTierConfig(
                tier_id="enterprise",
                name="Enterprise",
                description="Tailored solution for large organizations",
                monthly_price=Decimal("499.99"),
                quarterly_price=Decimal("1349.99"),  # 10% discount
                semi_annual_price=Decimal("2599.99"),  # 13% discount
                annual_price=Decimal("4999.99"),  # 17% discount
                currency="EUR",
                features=[
                    "Unlimited everything",
                    "Unlimited storage",
                    "Dedicated infrastructure",
                    "Custom development",
                    "SLA guarantee",
                    "Dedicated support team",
                    "On-premise deployment option",
                    "Advanced security features",
                    "Custom reporting"
                ],
                usage_limits={
                    "uploads": "unlimited",
                    "storage_gb": "unlimited",
                    "fingerprint_checks": "unlimited",
                    "platforms": "unlimited",
                    "api_calls": "unlimited",
                    "users": "unlimited",
                    "custom_features": True
                },
                trial_config=TrialConfig(
                    enabled=True,
                    duration_days=30,
                    requires_payment_method=False,
                    auto_convert=False
                ),
                is_enterprise=True,
                minimum_commitment_months=12,
                setup_fee=Decimal("1000.00")
            )
        }
    )
    
    # Billing Configuration
    BILLING_SETTINGS: Dict[str, Any] = field(default_factory=lambda: {
        "invoice_generation_enabled": True,
        "auto_send_invoices": True,
        "invoice_due_days": 30,
        "late_payment_fee": Decimal("5.00"),
        "currency_conversion_enabled": True,
        "tax_calculation_enabled": True,
        "dunning_management_enabled": True,
        "billing_threshold": Decimal("1.00"),  # Minimum billable amount
        "consolidate_billing": True,
        "proration_precision": 2  # Decimal places
    })
    
    # Payment Retry Configuration
    PAYMENT_RETRY_CONFIG: Dict[str, Any] = field(default_factory=lambda: {
        "max_retry_attempts": 3,
        "retry_intervals_hours": [24, 72, 168],  # 1 day, 3 days, 1 week
        "smart_retry_enabled": True,
        "retry_different_payment_methods": True,
        "notify_user_on_retry": True,
        "escalate_after_final_failure": True,
        "automatic_downgrade_enabled": False,
        "suspend_after_retries": True
    })
    
    # Upgrade/Downgrade Configuration
    TIER_CHANGE_CONFIG: Dict[str, Any] = field(default_factory=lambda: {
        "allow_upgrades": True,
        "allow_downgrades": True,
        "effective_immediately": True,
        "prorate_changes": True,
        "downgrade_restrictions": {
            "enterprise": ["creator_premium"],  # Can only downgrade to premium
            "creator_premium": ["creator_pro", "creator_basic"],
            "creator_pro": ["creator_basic", "free"],
            "creator_basic": ["free"]
        },
        "upgrade_incentives_enabled": True,
        "downgrade_surveys_enabled": True,
        "retention_offers_on_downgrade": True
    })
    
    # Notification Configuration
    NOTIFICATION_CONFIG: Dict[str, Any] = field(default_factory=lambda: {
        "email_notifications": True,
        "sms_notifications": False,
        "push_notifications": True,
        "in_app_notifications": True,
        "webhook_notifications": True,
        "notification_events": [
            "subscription_created",
            "trial_started",
            "trial_ending",
            "payment_succeeded",
            "payment_failed",
            "subscription_renewed",
            "subscription_cancelled",
            "subscription_upgraded",
            "subscription_downgraded",
            "subscription_expired"
        ],
        "notification_preferences_customizable": True,
        "batch_notifications": True,
        "notification_throttling": True
    })
    
    # Metrics and Analytics Configuration
    ANALYTICS_CONFIG: Dict[str, Any] = field(default_factory=lambda: {
        "track_subscription_metrics": True,
        "churn_analysis_enabled": True,
        "cohort_analysis_enabled": True,
        "revenue_forecasting": True,
        "usage_analytics": True,
        "customer_lifetime_value": True,
        "retention_rate_tracking": True,
        "metrics_retention_days": 2555,  # 7 years
        "real_time_metrics": True,
        "custom_metrics_enabled": True
    })
    
    # Security Configuration
    SECURITY_CONFIG: Dict[str, Any] = field(default_factory=lambda: {
        "require_2fa_for_billing_changes": True,
        "audit_all_subscription_changes": True,
        "encrypt_payment_data": True,
        "pci_compliance_enabled": True,
        "fraud_detection_enabled": True,
        "suspicious_activity_monitoring": True,
        "ip_whitelisting_for_enterprise": True,
        "data_retention_policy_days": 2555  # 7 years for tax purposes
    })
    
    def get_tier_config(self, tier_id: str) -> Optional[SubscriptionTierConfig]:
        """Get configuration for a specific subscription tier."""



        return self.SUBSCRIPTION_TIERS.get(tier_id)
    
    def get_available_tiers(self) -> List[str]:
        """Get list of available subscription tiers."""



        return list(self.SUBSCRIPTION_TIERS.keys())
    
    def calculate_proration(
        self,
        old_price: Decimal,
        new_price: Decimal,
        days_remaining: int,
        days_in_cycle: int
    ) -> Decimal:
        """Calculate proration amount for subscription changes."""
        if not self.PRORATION_CONFIG.enabled:
            return Decimal("0.00")
        
        daily_old_rate = old_price / days_in_cycle
        daily_new_rate = new_price / days_in_cycle
        
        credit_amount = daily_old_rate * days_remaining
        charge_amount = daily_new_rate * days_remaining
        
        proration = charge_amount - credit_amount
        
        if proration.abs() < self.PRORATION_CONFIG.minimum_proration_amount:
            return Decimal("0.00")
        
        return proration.quantize(Decimal("0.01"))
    
    def get_next_billing_date(
        self,
        current_date: datetime,
        billing_cycle: BillingCycle
    ) -> datetime:
        """Calculate next billing date based on cycle."""
        if billing_cycle == BillingCycle.MONTHLY:
            return current_date + timedelta(days=30)
        elif billing_cycle == BillingCycle.QUARTERLY:
            return current_date + timedelta(days=90)
        elif billing_cycle == BillingCycle.SEMI_ANNUALLY:
            return current_date + timedelta(days=180)
        elif billing_cycle == BillingCycle.ANNUALLY:
            return current_date + timedelta(days=365)
        else:
            return current_date + timedelta(days=30)  # Default to monthly
    
    def calculate_annual_savings(self, tier_id: str) -> Decimal:
        """Calculate savings percentage for annual billing."""
        tier_config = self.get_tier_config(tier_id)
        if not tier_config:
            return Decimal("0.00")
        
        monthly_annual_cost = tier_config.monthly_price * 12
        if monthly_annual_cost == Decimal("0.00"):
            return Decimal("0.00")
        
        savings = monthly_annual_cost - tier_config.annual_price
        return (savings / monthly_annual_cost * 100).quantize(Decimal("0.1"))
    
    def is_upgrade(self, from_tier: str, to_tier: str) -> bool:
        """Determine if a tier change is an upgrade."""
        tier_hierarchy = [
            "free", "creator_basic", "creator_pro", "creator_premium", "enterprise"
        ]
        
        try:
            from_index = tier_hierarchy.index(from_tier)
            to_index = tier_hierarchy.index(to_tier)
            return to_index > from_index
        except ValueError:
            return False


# Global configuration instance
subscription_config = SubscriptionConfig()
