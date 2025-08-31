"""Pricing Configuration Module
============================

Professional pricing and subscription management configuration for creator monetization platform.

Author: Fahed Mlaiel <mlaiel@live.de>
Project: IA-Influencer Agent + Content Protection Platform
Team: Lead Dev IA + Backend Senior + ML Engineer + DBA + Security + Microservices + Audio + DevOps

Copyright Notice:
This code is the intellectual property of Fahed Mlaiel.
Any unauthorized use, reproduction, or distribution of this code
without explicit written permission from the author is strictly prohibited.

Contact: mlaiel@live.de for licensing inquiries.
"""import os
from decimal import Decimal
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, field
from enum import Enum


class PricingModel(str, Enum):
    """Available pricing models."""    FREE = "free"
    FREEMIUM = "freemium"
    SUBSCRIPTION = "subscription"
    USAGE_BASED = "usage_based"
    TIERED = "tiered"
    REVENUE_SHARE = "revenue_share"
    HYBRID = "hybrid"
    ENTERPRISE = "enterprise"
    PAY_PER_USE = "pay_per_use"


class PricingTier(str, Enum):
    """Subscription tier levels."""    FREE = "free"
    BASIC = "basic"
    PROFESSIONAL = "professional"
    PREMIUM = "premium"
    ENTERPRISE = "enterprise"
    CUSTOM = "custom"


class BillingPeriod(str, Enum):
    """Billing period options."""    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    SEMI_ANNUALLY = "semi_annually"
    ANNUALLY = "annually"
    LIFETIME = "lifetime"
    PAY_AS_YOU_GO = "pay_as_you_go"


class FeatureType(str, Enum):
    """Feature types for pricing tiers."""    CONTENT_UPLOADS = "content_uploads"
    STORAGE_GB = "storage_gb"
    BANDWIDTH_GB = "bandwidth_gb"
    API_CALLS = "api_calls"
    FINGERPRINT_CHECKS = "fingerprint_checks"
    PLATFORMS_MONITORED = "platforms_monitored"
    REVENUE_TRACKING = "revenue_tracking"
    ADVANCED_ANALYTICS = "advanced_analytics"
    PRIORITY_SUPPORT = "priority_support"
    WHITE_LABEL = "white_label"
    CUSTOM_INTEGRATIONS = "custom_integrations"
    BULK_OPERATIONS = "bulk_operations"


class DiscountType(str, Enum):
    """Discount types."""    PERCENTAGE = "percentage"
    FIXED_AMOUNT = "fixed_amount"
    FREE_PERIOD = "free_period"
    BULK_DISCOUNT = "bulk_discount"
    LOYALTY_DISCOUNT = "loyalty_discount"
    PROMOTIONAL = "promotional"


@dataclass
class Feature:
    """Feature definition with limits."""    type: FeatureType
    name: str
    description: str
    limit: Union[int, str]  # Number or "unlimited"
    unit: Optional[str] = None
    enabled: bool = True


@dataclass
class PricingTierConfig:
    """Configuration for a specific pricing tier."""    tier: PricingTier
    name: str
    description: str
    price_monthly: Decimal
    price_annually: Decimal
    currency: str
    features: List[Feature]
    is_popular: bool = False
    is_custom: bool = False
    max_users: Union[int, str] = 1
    trial_days: int = 14
    setup_fee: Decimal = Decimal("0.00")
    cancellation_fee: Decimal = Decimal("0.00")
    enabled: bool = True


@dataclass
class UsageBasedPricing:
    """Usage-based pricing configuration."""    feature: FeatureType
    base_included: int
    overage_price: Decimal
    currency: str
    billing_unit: str
    minimum_charge: Decimal = Decimal("0.00")
    maximum_charge: Optional[Decimal] = None


@dataclass
class RevenueShareConfig:
    """Revenue sharing configuration."""    platform_commission: Decimal  # Percentage we take
    creator_share: Decimal  # Percentage creator gets
    minimum_revenue: Decimal
    maximum_commission: Optional[Decimal] = None
    tier_based_rates: bool = False
    volume_discounts: Dict[Decimal, Decimal] = field(default_factory=dict)


@dataclass
class DiscountConfig:
    """Discount configuration."""    code: str
    type: DiscountType
    value: Decimal  # Percentage or fixed amount
    minimum_amount: Decimal = Decimal("0.00")
    maximum_discount: Optional[Decimal] = None
    valid_from: Optional[str] = None
    valid_until: Optional[str] = None
    max_uses: Optional[int] = None
    applies_to_tiers: List[PricingTier] = field(default_factory=list)
    first_time_only: bool = False
    enabled: bool = True


@dataclass
class PricingConfig:
    """Main pricing configuration class."""    
    # Default Settings
    DEFAULT_CURRENCY: str = "EUR"
    DEFAULT_BILLING_PERIOD: BillingPeriod = BillingPeriod.MONTHLY
    
    # Tax Configuration
    TAX_SETTINGS: Dict[str, Any] = field(default_factory=lambda: {
        "include_tax_in_price": False,
        "default_tax_rate": Decimal("19.0"),  # German VAT
        "tax_by_country": {
            "DE": Decimal("19.0"),
            "US": Decimal("0.0"),  # Varies by state
            "GB": Decimal("20.0"),
            "FR": Decimal("20.0"),
            "IT": Decimal("22.0"),
            "ES": Decimal("21.0"),
            "NL": Decimal("21.0"),
            "BE": Decimal("21.0"),
            "AT": Decimal("20.0"),
            "CH": Decimal("7.7")
        },
        "b2b_tax_exempt": True,
        "reverse_charge_enabled": True
    })
    
    # Pricing Tiers Configuration
    PRICING_TIERS: Dict[PricingTier, PricingTierConfig] = field(
        default_factory=lambda: {
            PricingTier.FREE: PricingTierConfig(
                tier=PricingTier.FREE,
                name="Free Starter",
                description="Perfect for beginners exploring content protection",
                price_monthly=Decimal("0.00"),
                price_annually=Decimal("0.00"),
                currency="EUR",
                trial_days=0,
                features=[
                    Feature(
                        type=FeatureType.CONTENT_UPLOADS,
                        name="Content Uploads",
                        description="Monthly content uploads",
                        limit=10,
                        unit="uploads"
                    ),
                    Feature(
                        type=FeatureType.STORAGE_GB,
                        name="Storage",
                        description="Cloud storage space",
                        limit=1,
                        unit="GB"
                    ),
                    Feature(
                        type=FeatureType.FINGERPRINT_CHECKS,
                        name="Fingerprint Checks",
                        description="Monthly fingerprint verifications",
                        limit=100,
                        unit="checks"
                    ),
                    Feature(
                        type=FeatureType.PLATFORMS_MONITORED,
                        name="Platforms Monitored",
                        description="Social media platforms tracked",
                        limit=2,
                        unit="platforms"
                    )
                ]
            ),
            PricingTier.BASIC: PricingTierConfig(
                tier=PricingTier.BASIC,
                name="Creator Basic",
                description="Essential tools for content creators",
                price_monthly=Decimal("19.99"),
                price_annually=Decimal("199.99"),  # 2 months free
                currency="EUR",
                trial_days=14,
                features=[
                    Feature(
                        type=FeatureType.CONTENT_UPLOADS,
                        name="Content Uploads",
                        description="Monthly content uploads",
                        limit=100,
                        unit="uploads"
                    ),
                    Feature(
                        type=FeatureType.STORAGE_GB,
                        name="Storage",
                        description="Cloud storage space",
                        limit=10,
                        unit="GB"
                    ),
                    Feature(
                        type=FeatureType.FINGERPRINT_CHECKS,
                        name="Fingerprint Checks",
                        description="Monthly fingerprint verifications",
                        limit=1000,
                        unit="checks"
                    ),
                    Feature(
                        type=FeatureType.PLATFORMS_MONITORED,
                        name="Platforms Monitored",
                        description="Social media platforms tracked",
                        limit=5,
                        unit="platforms"
                    ),
                    Feature(
                        type=FeatureType.REVENUE_TRACKING,
                        name="Revenue Tracking",
                        description="Basic revenue analytics",
                        limit="basic",
                        enabled=True
                    ),
                    Feature(
                        type=FeatureType.API_CALLS,
                        name="API Calls",
                        description="Monthly API requests",
                        limit=10000,
                        unit="calls"
                    )
                ]
            ),
            PricingTier.PROFESSIONAL: PricingTierConfig(
                tier=PricingTier.PROFESSIONAL,
                name="Creator Pro",
                description="Advanced features for serious creators",
                price_monthly=Decimal("49.99"),
                price_annually=Decimal("499.99"),  # 2 months free
                currency="EUR",
                trial_days=14,
                is_popular=True,
                features=[
                    Feature(
                        type=FeatureType.CONTENT_UPLOADS,
                        name="Content Uploads",
                        description="Monthly content uploads",
                        limit=500,
                        unit="uploads"
                    ),
                    Feature(
                        type=FeatureType.STORAGE_GB,
                        name="Storage",
                        description="Cloud storage space",
                        limit=50,
                        unit="GB"
                    ),
                    Feature(
                        type=FeatureType.FINGERPRINT_CHECKS,
                        name="Fingerprint Checks",
                        description="Monthly fingerprint verifications",
                        limit=5000,
                        unit="checks"
                    ),
                    Feature(
                        type=FeatureType.PLATFORMS_MONITORED,
                        name="Platforms Monitored",
                        description="Social media platforms tracked",
                        limit=10,
                        unit="platforms"
                    ),
                    Feature(
                        type=FeatureType.REVENUE_TRACKING,
                        name="Revenue Tracking",
                        description="Advanced revenue analytics",
                        limit="advanced",
                        enabled=True
                    ),
                    Feature(
                        type=FeatureType.ADVANCED_ANALYTICS,
                        name="Advanced Analytics",
                        description="Detailed performance insights",
                        limit="enabled",
                        enabled=True
                    ),
                    Feature(
                        type=FeatureType.API_CALLS,
                        name="API Calls",
                        description="Monthly API requests",
                        limit=50000,
                        unit="calls"
                    ),
                    Feature(
                        type=FeatureType.PRIORITY_SUPPORT,
                        name="Priority Support",
                        description="24/7 priority customer support",
                        limit="enabled",
                        enabled=True
                    )
                ]
            ),
            PricingTier.PREMIUM: PricingTierConfig(
                tier=PricingTier.PREMIUM,
                name="Creator Premium",
                description="Complete solution for professional creators",
                price_monthly=Decimal("99.99"),
                price_annually=Decimal("999.99"),  # 2 months free
                currency="EUR",
                trial_days=14,
                features=[
                    Feature(
                        type=FeatureType.CONTENT_UPLOADS,
                        name="Content Uploads",
                        description="Monthly content uploads",
                        limit="unlimited",
                        unit="uploads"
                    ),
                    Feature(
                        type=FeatureType.STORAGE_GB,
                        name="Storage",
                        description="Cloud storage space",
                        limit=200,
                        unit="GB"
                    ),
                    Feature(
                        type=FeatureType.FINGERPRINT_CHECKS,
                        name="Fingerprint Checks",
                        description="Monthly fingerprint verifications",
                        limit="unlimited",
                        unit="checks"
                    ),
                    Feature(
                        type=FeatureType.PLATFORMS_MONITORED,
                        name="Platforms Monitored",
                        description="Social media platforms tracked",
                        limit="unlimited",
                        unit="platforms"
                    ),
                    Feature(
                        type=FeatureType.REVENUE_TRACKING,
                        name="Revenue Tracking",
                        description="Enterprise revenue analytics",
                        limit="enterprise",
                        enabled=True
                    ),
                    Feature(
                        type=FeatureType.ADVANCED_ANALYTICS,
                        name="Advanced Analytics",
                        description="Comprehensive performance insights",
                        limit="enabled",
                        enabled=True
                    ),
                    Feature(
                        type=FeatureType.API_CALLS,
                        name="API Calls",
                        description="Monthly API requests",
                        limit="unlimited",
                        unit="calls"
                    ),
                    Feature(
                        type=FeatureType.PRIORITY_SUPPORT,
                        name="Priority Support",
                        description="Dedicated account manager",
                        limit="enabled",
                        enabled=True
                    ),
                    Feature(
                        type=FeatureType.WHITE_LABEL,
                        name="White Label",
                        description="Custom branding options",
                        limit="enabled",
                        enabled=True
                    ),
                    Feature(
                        type=FeatureType.CUSTOM_INTEGRATIONS,
                        name="Custom Integrations",
                        description="Bespoke API integrations",
                        limit="enabled",
                        enabled=True
                    )
                ],
                max_users=5
            ),
            PricingTier.ENTERPRISE: PricingTierConfig(
                tier=PricingTier.ENTERPRISE,
                name="Enterprise",
                description="Tailored solution for large organizations",
                price_monthly=Decimal("499.99"),
                price_annually=Decimal("4999.99"),  # 2 months free
                currency="EUR",
                trial_days=30,
                is_custom=True,
                features=[
                    Feature(
                        type=FeatureType.CONTENT_UPLOADS,
                        name="Content Uploads",
                        description="Unlimited content uploads",
                        limit="unlimited"
                    ),
                    Feature(
                        type=FeatureType.STORAGE_GB,
                        name="Storage",
                        description="Unlimited cloud storage",
                        limit="unlimited"
                    ),
                    Feature(
                        type=FeatureType.FINGERPRINT_CHECKS,
                        name="Fingerprint Checks",
                        description="Unlimited fingerprint verifications",
                        limit="unlimited"
                    ),
                    Feature(
                        type=FeatureType.PLATFORMS_MONITORED,
                        name="Platforms Monitored",
                        description="All platforms monitored",
                        limit="unlimited"
                    ),
                    Feature(
                        type=FeatureType.REVENUE_TRACKING,
                        name="Revenue Tracking",
                        description="Enterprise revenue suite",
                        limit="enterprise",
                        enabled=True
                    ),
                    Feature(
                        type=FeatureType.ADVANCED_ANALYTICS,
                        name="Advanced Analytics",
                        description="Business intelligence suite",
                        limit="enabled",
                        enabled=True
                    ),
                    Feature(
                        type=FeatureType.API_CALLS,
                        name="API Calls",
                        description="Unlimited API requests",
                        limit="unlimited"
                    ),
                    Feature(
                        type=FeatureType.PRIORITY_SUPPORT,
                        name="Enterprise Support",
                        description="24/7 dedicated support team",
                        limit="enabled",
                        enabled=True
                    ),
                    Feature(
                        type=FeatureType.WHITE_LABEL,
                        name="White Label",
                        description="Full white-label solution",
                        limit="enabled",
                        enabled=True
                    ),
                    Feature(
                        type=FeatureType.CUSTOM_INTEGRATIONS,
                        name="Custom Development",
                        description="Custom features and integrations",
                        limit="enabled",
                        enabled=True
                    ),
                    Feature(
                        type=FeatureType.BULK_OPERATIONS,
                        name="Bulk Operations",
                        description="Mass content processing",
                        limit="enabled",
                        enabled=True
                    )
                ],
                max_users="unlimited",
                setup_fee=Decimal("1000.00")
            )
        }
    )
    
    # Usage-Based Pricing Configuration
    USAGE_PRICING: Dict[FeatureType, UsageBasedPricing] = field(
        default_factory=lambda: {
            FeatureType.FINGERPRINT_CHECKS: UsageBasedPricing(
                feature=FeatureType.FINGERPRINT_CHECKS,
                base_included=0,
                overage_price=Decimal("0.01"),
                currency="EUR",
                billing_unit="per check",
                minimum_charge=Decimal("1.00")
            ),
            FeatureType.STORAGE_GB: UsageBasedPricing(
                feature=FeatureType.STORAGE_GB,
                base_included=0,
                overage_price=Decimal("0.10"),
                currency="EUR",
                billing_unit="per GB/month",
                minimum_charge=Decimal("1.00")
            ),
            FeatureType.BANDWIDTH_GB: UsageBasedPricing(
                feature=FeatureType.BANDWIDTH_GB,
                base_included=0,
                overage_price=Decimal("0.05"),
                currency="EUR",
                billing_unit="per GB",
                minimum_charge=Decimal("0.50")
            ),
            FeatureType.API_CALLS: UsageBasedPricing(
                feature=FeatureType.API_CALLS,
                base_included=0,
                overage_price=Decimal("0.001"),
                currency="EUR",
                billing_unit="per 1K calls",
                minimum_charge=Decimal("1.00")
            )
        }
    )
    
    # Revenue Share Configuration
    REVENUE_SHARE: RevenueShareConfig = RevenueShareConfig(
        platform_commission=Decimal("15.0"),  # 15% platform fee
        creator_share=Decimal("85.0"),  # 85% to creator
        minimum_revenue=Decimal("10.00"),
        tier_based_rates=True,
        volume_discounts={
            Decimal("1000.00"): Decimal("12.0"),   # 12% for >1K revenue
            Decimal("5000.00"): Decimal("10.0"),   # 10% for >5K revenue
            Decimal("25000.00"): Decimal("8.0"),   # 8% for >25K revenue
            Decimal("100000.00"): Decimal("5.0")   # 5% for >100K revenue
        }
    )
    
    # Discount Configuration
    DISCOUNTS: Dict[str, DiscountConfig] = field(
        default_factory=lambda: {
            "CREATOR50": DiscountConfig(
                code="CREATOR50",
                type=DiscountType.PERCENTAGE,
                value=Decimal("50.0"),
                minimum_amount=Decimal("19.99"),
                valid_until="2025-12-31",
                first_time_only=True,
                applies_to_tiers=[PricingTier.BASIC, PricingTier.PROFESSIONAL]
            ),
            "ANNUAL25": DiscountConfig(
                code="ANNUAL25",
                type=DiscountType.PERCENTAGE,
                value=Decimal("25.0"),
                applies_to_tiers=[
                    PricingTier.BASIC, 
                    PricingTier.PROFESSIONAL, 
                    PricingTier.PREMIUM
                ]
            ),
            "STUDENT40": DiscountConfig(
                code="STUDENT40",
                type=DiscountType.PERCENTAGE,
                value=Decimal("40.0"),
                applies_to_tiers=[PricingTier.BASIC, PricingTier.PROFESSIONAL]
            ),
            "NONPROFIT60": DiscountConfig(
                code="NONPROFIT60",
                type=DiscountType.PERCENTAGE,
                value=Decimal("60.0"),
                applies_to_tiers=[
                    PricingTier.BASIC, 
                    PricingTier.PROFESSIONAL, 
                    PricingTier.PREMIUM
                ]
            )
        }
    )
    
    # Currency Support
    SUPPORTED_CURRENCIES: List[str] = [
        "EUR", "USD", "GBP", "CAD", "AUD", "CHF", "SEK", "NOK", "DKK",
        "JPY", "CNY", "BRL", "INR", "MXN", "ZAR"
    ]
    
    # Currency Exchange Configuration
    EXCHANGE_SETTINGS: Dict[str, Any] = field(default_factory=lambda: {
        "auto_convert_pricing": True,
        "base_currency": "EUR",
        "update_frequency_hours": 6,
        "markup_percentage": Decimal("2.5"),
        "round_to_friendly_prices": True,
        "price_rounding_rules": {
            "USD": Decimal("0.99"),  # $19.99
            "EUR": Decimal("0.99"),  # €19.99
            "GBP": Decimal("0.99"),  # £19.99
            "CHF": Decimal("0.95")   # CHF 19.95
        }
    })
    
    def get_tier_config(self, tier: PricingTier) -> Optional[PricingTierConfig]:
        """Get configuration for a specific pricing tier."""        return self.PRICING_TIERS.get(tier)
    
    def get_enabled_tiers(self) -> List[PricingTier]:
        """Get list of enabled pricing tiers."""        return [
            tier for tier, config in self.PRICING_TIERS.items() 
            if config.enabled
        ]
    
    def calculate_price_with_tax(
        self, 
        base_price: Decimal, 
        country_code: str
    ) -> Decimal:
        """Calculate price including tax for a specific country."""        tax_rate = self.TAX_SETTINGS["tax_by_country"].get(
            country_code, 
            self.TAX_SETTINGS["default_tax_rate"]
        )
        
        if self.TAX_SETTINGS["include_tax_in_price"]:
            return base_price
        
        tax_amount = base_price * (tax_rate / Decimal("100"))
        return (base_price + tax_amount).quantize(Decimal("0.01"))
    
    def apply_discount(
        self, 
        price: Decimal, 
        discount_code: str, 
        tier: PricingTier
    ) -> Decimal:
        """Apply discount to price if valid."""        discount = self.DISCOUNTS.get(discount_code)
        if not discount or not discount.enabled:
            return price
        
        if tier not in discount.applies_to_tiers:
            return price
        
        if price < discount.minimum_amount:
            return price
        
        if discount.type == DiscountType.PERCENTAGE:
            discount_amount = price * (discount.value / Decimal("100"))
        else:
            discount_amount = discount.value
        
        if discount.maximum_discount:
            discount_amount = min(discount_amount, discount.maximum_discount)
        
        final_price = price - discount_amount
        return max(final_price, Decimal("0.00")).quantize(Decimal("0.01"))
    
    def get_annual_discount_percentage(self, tier: PricingTier) -> Decimal:
        """Calculate annual discount percentage for a tier."""        config = self.get_tier_config(tier)
        if not config:
            return Decimal("0.00")
        
        monthly_annual = config.price_monthly * 12
        if monthly_annual == Decimal("0.00"):
            return Decimal("0.00")
        
        savings = monthly_annual - config.price_annually
        return (savings / monthly_annual * 100).quantize(Decimal("0.1"))


# Global configuration instance
pricing_config = PricingConfig()
