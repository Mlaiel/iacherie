"""Monetization Configuration Module - Consolidated Monetization Configs
=====================================================================

Consolidates all monetization-related configurations from:
- config/monetization/ (15 files)

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, field
from enum import Enum
from decimal import Decimal
import os

# ===== PAYMENT CONFIGURATION =====

class PaymentProvider(str, Enum):
    """Payment service providers"""
    STRIPE = "stripe"
    PAYPAL = "paypal"
    SQUARE = "square"
    ADYEN = "adyen"
    BRAINTREE = "braintree"
    RAZORPAY = "razorpay"
    MOLLIE = "mollie"
    CRYPTOCURRENCY = "cryptocurrency"

class CurrencyCode(str, Enum):
    """Supported currencies"""
    USD = "USD"
    EUR = "EUR"
    GBP = "GBP"
    JPY = "JPY"
    CAD = "CAD"
    AUD = "AUD"
    CHF = "CHF"
    CNY = "CNY"
    BTC = "BTC"  # Bitcoin
    ETH = "ETH"  # Ethereum

class PaymentMethod(str, Enum):
    """Payment methods"""
    CREDIT_CARD = "credit_card"
    DEBIT_CARD = "debit_card"
    BANK_TRANSFER = "bank_transfer"
    DIGITAL_WALLET = "digital_wallet"
    CRYPTOCURRENCY = "cryptocurrency"
    DIRECT_DEBIT = "direct_debit"
    WIRE_TRANSFER = "wire_transfer"

@dataclass
class PaymentConfig:
    """Payment processing configuration"""
    provider: PaymentProvider = PaymentProvider.STRIPE
    api_key: Optional[str] = None
    secret_key: Optional[str] = None
    webhook_secret: Optional[str] = None
    supported_methods: List[PaymentMethod] = field(default_factory=lambda: [
        PaymentMethod.CREDIT_CARD,
        PaymentMethod.DEBIT_CARD,
        PaymentMethod.DIGITAL_WALLET
    ])
    supported_currencies: List[CurrencyCode] = field(default_factory=lambda: [
        CurrencyCode.USD,
        CurrencyCode.EUR,
        CurrencyCode.GBP
    ])
    default_currency: CurrencyCode = CurrencyCode.USD
    enable_recurring: bool = True
    enable_refunds: bool = True
    auto_capture: bool = True

# ===== SUBSCRIPTION CONFIGURATION =====

class SubscriptionTier(str, Enum):
    """Subscription tiers"""
    FREE = "free"
    BASIC = "basic"
    PREMIUM = "premium"
    PROFESSIONAL = "professional"
    ENTERPRISE = "enterprise"

class BillingCycle(str, Enum):
    """Billing cycles"""
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    SEMI_ANNUAL = "semi_annual"
    ANNUAL = "annual"
    LIFETIME = "lifetime"

@dataclass
class SubscriptionFeature:
    """Subscription feature definition"""
    name: str
    description: str
    limit: Optional[int] = None  # None = unlimited
    enabled: bool = True

@dataclass
class SubscriptionPlan:
    """Subscription plan configuration"""
    tier: SubscriptionTier
    name: str
    description: str
    price: Decimal
    currency: CurrencyCode
    billing_cycle: BillingCycle
    features: List[SubscriptionFeature] = field(default_factory=list)
    trial_days: int = 0
    setup_fee: Decimal = Decimal("0.00")
    cancellation_policy: str = "immediate"
    auto_renewal: bool = True

@dataclass
class SubscriptionConfig:
    """Subscription configuration"""
    enabled: bool = True
    plans: List[SubscriptionPlan] = field(default_factory=list)
    allow_downgrades: bool = True
    allow_upgrades: bool = True
    proration_enabled: bool = True
    grace_period_days: int = 3
    dunning_management: bool = True
    max_retry_attempts: int = 3

# ===== REVENUE SHARING CONFIGURATION =====

class RevenueShareType(str, Enum):
    """Revenue sharing types"""
    PERCENTAGE = "percentage"
    FIXED_AMOUNT = "fixed_amount"
    TIERED = "tiered"
    HYBRID = "hybrid"

@dataclass
class RevenueShareRule:
    """Revenue sharing rule"""
    name: str
    share_type: RevenueShareType
    percentage: Optional[float] = None  # For percentage type
    fixed_amount: Optional[Decimal] = None  # For fixed amount type
    min_threshold: Decimal = Decimal("0.00")
    max_cap: Optional[Decimal] = None
    applies_to: List[str] = field(default_factory=list)  # Content types or categories

@dataclass
class RevenueShareConfig:
    """Revenue sharing configuration"""
    enabled: bool = True
    platform_fee_percentage: float = 10.0  # Platform takes 10%
    creator_share_percentage: float = 85.0  # Creator gets 85%
    collaborator_share_percentage: float = 5.0  # Collaborator gets 5%
    rules: List[RevenueShareRule] = field(default_factory=list)
    minimum_payout: Decimal = Decimal("10.00")
    payout_frequency: str = "monthly"  # daily, weekly, monthly
    auto_payout: bool = True

# ===== PRICING CONFIGURATION =====

class PricingModel(str, Enum):
    """Pricing models"""
    FREE = "free"
    FREEMIUM = "freemium"
    SUBSCRIPTION = "subscription"
    PAY_PER_USE = "pay_per_use"
    TIERED = "tiered"
    USAGE_BASED = "usage_based"

class PricingStrategy(str, Enum):
    """Pricing strategies"""
    FIXED = "fixed"
    DYNAMIC = "dynamic"
    AUCTION = "auction"
    NEGOTIATED = "negotiated"

@dataclass
class PricingTier:
    """Pricing tier definition"""
    name: str
    min_usage: int
    max_usage: Optional[int]
    price_per_unit: Decimal
    bulk_discount: float = 0.0
    overage_price: Optional[Decimal] = None

@dataclass
class PricingConfig:
    """Pricing configuration"""
    model: PricingModel = PricingModel.FREEMIUM
    strategy: PricingStrategy = PricingStrategy.FIXED
    base_price: Decimal = Decimal("0.00")
    currency: CurrencyCode = CurrencyCode.USD
    tiers: List[PricingTier] = field(default_factory=list)
    dynamic_pricing_enabled: bool = False
    regional_pricing: bool = True
    discounts_enabled: bool = True
    promotional_pricing: bool = True

# ===== MARKETPLACE CONFIGURATION =====

class CommissionType(str, Enum):
    """Commission types"""
    FLAT_FEE = "flat_fee"
    PERCENTAGE = "percentage"
    SLIDING_SCALE = "sliding_scale"
    NO_COMMISSION = "no_commission"

@dataclass
class MarketplaceConfig:
    """Marketplace configuration"""
    enabled: bool = True
    commission_type: CommissionType = CommissionType.PERCENTAGE
    commission_rate: float = 15.0  # 15% commission
    listing_fee: Decimal = Decimal("0.00")
    success_fee: Decimal = Decimal("0.00")
    escrow_enabled: bool = True
    seller_verification_required: bool = True
    buyer_protection: bool = True
    dispute_resolution: bool = True

# ===== ANALYTICS CONFIGURATION =====

@dataclass
class RevenueAnalyticsConfig:
    """Revenue analytics configuration"""
    enabled: bool = True
    real_time_tracking: bool = True
    cohort_analysis: bool = True
    ltv_calculation: bool = True
    churn_prediction: bool = True
    revenue_forecasting: bool = True
    custom_metrics: List[str] = field(default_factory=list)
    data_retention_days: int = 1095  # 3 years
    export_formats: List[str] = field(default_factory=lambda: ["csv", "json", "pdf"])

# ===== PAYOUT CONFIGURATION =====

class PayoutMethod(str, Enum):
    """Payout methods"""
    BANK_TRANSFER = "bank_transfer"
    PAYPAL = "paypal"
    STRIPE_EXPRESS = "stripe_express"
    CRYPTOCURRENCY = "cryptocurrency"
    CHECK = "check"
    WIRE_TRANSFER = "wire_transfer"

@dataclass
class PayoutConfig:
    """Payout configuration"""
    enabled: bool = True
    methods: List[PayoutMethod] = field(default_factory=lambda: [
        PayoutMethod.BANK_TRANSFER,
        PayoutMethod.PAYPAL,
        PayoutMethod.STRIPE_EXPRESS
    ])
    minimum_payout: Decimal = Decimal("50.00")
    maximum_payout: Decimal = Decimal("50000.00")
    payout_schedule: str = "monthly"  # weekly, bi-weekly, monthly
    auto_payout_threshold: Decimal = Decimal("100.00")
    payout_fee: Decimal = Decimal("2.50")
    currency_conversion_enabled: bool = True

# ===== TAX CONFIGURATION =====

class TaxType(str, Enum):
    """Tax types"""
    VAT = "vat"
    SALES_TAX = "sales_tax"
    GST = "gst"
    INCOME_TAX = "income_tax"
    WITHHOLDING_TAX = "withholding_tax"

@dataclass
class TaxRule:
    """Tax rule configuration"""
    name: str
    tax_type: TaxType
    rate: float
    applies_to_regions: List[str] = field(default_factory=list)
    threshold_amount: Decimal = Decimal("0.00")
    tax_inclusive: bool = False

@dataclass
class TaxConfig:
    """Tax configuration"""
    enabled: bool = True
    auto_calculate: bool = True
    rules: List[TaxRule] = field(default_factory=list)
    tax_reporting_enabled: bool = True
    invoice_generation: bool = True
    compliance_automation: bool = True

# ===== FINANCIAL REPORTING CONFIGURATION =====

@dataclass
class FinancialReportingConfig:
    """Financial reporting configuration"""
    enabled: bool = True
    automated_reports: bool = True
    report_frequency: str = "monthly"  # daily, weekly, monthly, quarterly
    include_forecasts: bool = True
    include_analytics: bool = True
    export_formats: List[str] = field(default_factory=lambda: ["pdf", "excel", "csv"])
    email_reports: bool = True
    dashboard_enabled: bool = True

# ===== ENVIRONMENT-SPECIFIC CONFIGURATIONS =====

def get_development_monetization_config() -> Dict[str, Any]:
    """Get development monetization configuration"""
    return {
        "payment": PaymentConfig(
            provider=PaymentProvider.STRIPE,
            api_key="sk_test_...",
            auto_capture=False
        ),
        "subscription": SubscriptionConfig(
            enabled=True,
            plans=[
                SubscriptionPlan(
                    tier=SubscriptionTier.FREE,
                    name="Free Plan",
                    description="Basic features",
                    price=Decimal("0.00"),
                    currency=CurrencyCode.USD,
                    billing_cycle=BillingCycle.MONTHLY
                )
            ]
        ),
        "revenue_share": RevenueShareConfig(
            platform_fee_percentage=5.0  # Lower fee in dev
        ),
        "marketplace": MarketplaceConfig(
            commission_rate=10.0  # Lower commission in dev
        ),
        "analytics": RevenueAnalyticsConfig(
            data_retention_days=90  # Shorter retention in dev
        )
    }

def get_production_monetization_config() -> Dict[str, Any]:
    """Get production monetization configuration"""
    return {
        "payment": PaymentConfig(
            provider=PaymentProvider.STRIPE,
            api_key=os.getenv("STRIPE_SECRET_KEY"),
            webhook_secret=os.getenv("STRIPE_WEBHOOK_SECRET"),
            auto_capture=True
        ),
        "subscription": SubscriptionConfig(
            enabled=True,
            plans=[
                SubscriptionPlan(
                    tier=SubscriptionTier.FREE,
                    name="Free Plan",
                    description="Basic features with limitations",
                    price=Decimal("0.00"),
                    currency=CurrencyCode.USD,
                    billing_cycle=BillingCycle.MONTHLY
                ),
                SubscriptionPlan(
                    tier=SubscriptionTier.PREMIUM,
                    name="Premium Plan",
                    description="Full features and priority support",
                    price=Decimal("29.99"),
                    currency=CurrencyCode.USD,
                    billing_cycle=BillingCycle.MONTHLY,
                    trial_days=14
                )
            ]
        ),
        "revenue_share": RevenueShareConfig(
            platform_fee_percentage=15.0,
            creator_share_percentage=80.0,
            collaborator_share_percentage=5.0
        ),
        "marketplace": MarketplaceConfig(
            commission_rate=20.0
        ),
        "analytics": RevenueAnalyticsConfig(
            data_retention_days=1095  # 3 years
        )
    }

def get_testing_monetization_config() -> Dict[str, Any]:
    """Get testing monetization configuration"""
    return {
        "payment": PaymentConfig(
            provider=PaymentProvider.STRIPE,
            api_key="sk_test_test",
            auto_capture=False
        ),
        "subscription": SubscriptionConfig(
            enabled=False  # Disable subscriptions in testing
        ),
        "revenue_share": RevenueShareConfig(
            platform_fee_percentage=0.0  # No fees in testing
        ),
        "marketplace": MarketplaceConfig(
            commission_rate=0.0  # No commission in testing
        ),
        "analytics": RevenueAnalyticsConfig(
            data_retention_days=7  # Short retention in testing
        )
    }

# ===== MONETIZATION CONFIGURATION FACTORY =====

class MonetizationConfigurationFactory:
    """Factory for creating monetization configurations"""
    
    @staticmethod
    def create_config(environment: str = "development") -> Dict[str, Any]:
        """Create monetization configuration for environment"""
        if environment.lower() == "production":
            return get_production_monetization_config()
        elif environment.lower() == "testing":
            return get_testing_monetization_config()
        else:
            return get_development_monetization_config()

# Export all monetization configurations
__all__ = [
    # Enums
    "PaymentProvider",
    "CurrencyCode", 
    "PaymentMethod",
    "SubscriptionTier",
    "BillingCycle",
    "RevenueShareType",
    "PricingModel",
    "PricingStrategy",
    "CommissionType",
    "PayoutMethod",
    "TaxType",
    
    # Configuration Classes
    "PaymentConfig",
    "SubscriptionFeature",
    "SubscriptionPlan",
    "SubscriptionConfig",
    "RevenueShareRule",
    "RevenueShareConfig",
    "PricingTier",
    "PricingConfig",
    "MarketplaceConfig",
    "RevenueAnalyticsConfig",
    "PayoutConfig",
    "TaxRule",
    "TaxConfig",
    "FinancialReportingConfig",
    
    # Factory and Functions
    "MonetizationConfigurationFactory",
    "get_development_monetization_config",
    "get_production_monetization_config",
    "get_testing_monetization_config"
]