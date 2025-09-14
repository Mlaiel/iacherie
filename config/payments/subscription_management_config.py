"""
Subscription Management Configuration - Enterprise Configuration Management
Enterprise configuration for subscription and revenue management business logic

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
Licensed under proprietary license - reproduction forbidden without written authorization.
"""

from typing import Dict, List, Optional, Any, Union
from enum import Enum
from dataclasses import dataclass
from datetime import datetime, timedelta

try:
    from pydantic_settings import BaseSettings
    from pydantic import Field, validator
except ImportError:
    # Fallback for environments without pydantic_settings
    class BaseSettings:
    """BaseSettings: class implementation"""
        def __init__(self, **kwargs) -> None:
            for key, value in kwargs.items():
                setattr(self, key, value)
        
        class Config:
    """Config: class implementation"""
            env_prefix = ""
            case_sensitive = False
            extra = "allow"
    
    def Field(**kwargs) -> None:
        return kwargs.get('default_factory', kwargs.get('default'))()
    
    def validator(field_name) -> None:
        def decorator(func) -> None:
            return func
        return decorator


class SubscriptionTier(str, Enum):
    """Subscription tier levels"""
    BASIC = "basic"
    PROFESSIONAL = "professional"
    ENTERPRISE = "enterprise"
    CUSTOM = "custom"
    TRIAL = "trial"
    FREEMIUM = "freemium"


class BillingCycle(str, Enum):
    """Billing cycle types"""
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    YEARLY = "yearly"
    WEEKLY = "weekly"
    BIANNUAL = "biannual"
    TRIENNIAL = "triennial"


class SubscriptionStatus(str, Enum):
    """Subscription status types"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    PENDING = "pending"
    SUSPENDED = "suspended"
    CANCELLED = "cancelled"
    EXPIRED = "expired"
    TRIAL = "trial"
    PAST_DUE = "past_due"


class PricingModel(str, Enum):
    """Pricing model types"""
    FIXED = "fixed"
    USAGE_BASED = "usage_based"
    TIERED = "tiered"
    PER_SEAT = "per_seat"
    FREEMIUM = "freemium"
    HYBRID = "hybrid"
    DYNAMIC = "dynamic"
    CUSTOM = "custom"


class RevenueModel(str, Enum):
    """Revenue model types"""
    SUBSCRIPTION = "subscription"
    ONE_TIME = "one_time"
    USAGE_BASED = "usage_based"
    COMMISSION = "commission"
    FREEMIUM = "freemium"
    ADVERTISING = "advertising"
    MARKETPLACE = "marketplace"


class ChurnPredictionLevel(str, Enum):
    """Churn prediction risk levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class SubscriptionTierConfig:
    """Subscription tier configuration"""
    tier: SubscriptionTier
    name: str
    description: str
    pricing_model: PricingModel
    base_price: float
    currency: str
    billing_cycles: List[BillingCycle]
    features: List[str]
    limits: Dict[str, Any]
    trial_period_days: int
    setup_fee: float
    cancellation_fee: float
    upgrade_allowed: bool
    downgrade_allowed: bool


@dataclass
class BillingConfiguration:
    """Billing configuration"""
    cycle: BillingCycle
    price_modifier: float  # Multiplier for base price
    discount_percentage: float
    trial_period_days: int
    grace_period_days: int
    dunning_attempts: int
    auto_renewal: bool
    proration_enabled: bool


@dataclass
class RevenueOptimization:
    """Revenue optimization configuration"""
    dynamic_pricing: bool
    demand_forecasting: bool
    price_elasticity_analysis: bool
    cohort_analysis: bool
    lifetime_value_tracking: bool
    churn_prediction: bool
    upselling_enabled: bool
    cross_selling_enabled: bool


@dataclass
class ChurnPreventionConfig:
    """Churn prevention configuration"""
    prediction_enabled: bool
    early_warning_days: int
    intervention_strategies: List[str]
    retention_campaigns: List[str]
    win_back_campaigns: List[str]
    discount_offers: Dict[str, float]
    personalization_enabled: bool
    success_metrics: List[str]


class SubscriptionManagementSettings(BaseSettings):
    """Subscription management configuration settings"""
    
    # Subscription Tier Configurations
    subscription_tiers: Dict[str, SubscriptionTierConfig] = Field(
        default_factory=lambda: {
            "basic": SubscriptionTierConfig(
                tier=SubscriptionTier.BASIC,
                name="Basic Creator",
                description="Essential tools for individual creators",
                pricing_model=PricingModel.FIXED,
                base_price=9.99,
                currency="USD",
                billing_cycles=[BillingCycle.MONTHLY, BillingCycle.YEARLY],
                features=[
                    "content_upload", "basic_analytics", "copyright_protection",
                    "monetization_tools", "community_access", "email_support"
                ],
                limits={
                    "uploads_per_month": 100,
                    "storage_gb": 10,
                    "bandwidth_gb": 50,
                    "collaboration_projects": 3,
                    "ai_processing_hours": 5
                },
                trial_period_days=14,
                setup_fee=0.00,
                cancellation_fee=0.00,
                upgrade_allowed=True,
                downgrade_allowed=True
            ),
            "professional": SubscriptionTierConfig(
                tier=SubscriptionTier.PROFESSIONAL,
                name="Professional Creator",
                description="Advanced tools for professional creators",
                pricing_model=PricingModel.TIERED,
                base_price=29.99,
                currency="USD",
                billing_cycles=[BillingCycle.MONTHLY, BillingCycle.QUARTERLY, BillingCycle.YEARLY],
                features=[
                    "unlimited_content_upload", "advanced_analytics", "premium_copyright_protection",
                    "advanced_monetization", "collaboration_tools", "priority_support",
                    "custom_branding", "api_access", "white_label_options"
                ],
                limits={
                    "uploads_per_month": -1,  # Unlimited
                    "storage_gb": 100,
                    "bandwidth_gb": 500,
                    "collaboration_projects": 15,
                    "ai_processing_hours": 25,
                    "team_members": 5
                },
                trial_period_days=30,
                setup_fee=0.00,
                cancellation_fee=0.00,
                upgrade_allowed=True,
                downgrade_allowed=True
            ),
            "enterprise": SubscriptionTierConfig(
                tier=SubscriptionTier.ENTERPRISE,
                name="Enterprise Solution",
                description="Complete solution for large organizations",
                pricing_model=PricingModel.CUSTOM,
                base_price=199.99,
                currency="USD",
                billing_cycles=[BillingCycle.MONTHLY, BillingCycle.QUARTERLY, BillingCycle.YEARLY],
                features=[
                    "unlimited_everything", "enterprise_analytics", "enterprise_protection",
                    "custom_monetization", "full_collaboration_suite", "dedicated_support",
                    "custom_integrations", "sla_guarantees", "compliance_tools",
                    "advanced_security", "multi_tenant_support"
                ],
                limits={
                    "uploads_per_month": -1,  # Unlimited
                    "storage_gb": -1,  # Unlimited
                    "bandwidth_gb": -1,  # Unlimited
                    "collaboration_projects": -1,  # Unlimited
                    "ai_processing_hours": -1,  # Unlimited
                    "team_members": -1  # Unlimited
                },
                trial_period_days=30,
                setup_fee=499.00,
                cancellation_fee=0.00,
                upgrade_allowed=False,  # Already top tier
                downgrade_allowed=True
            ),
            "freemium": SubscriptionTierConfig(
                tier=SubscriptionTier.FREEMIUM,
                name="Free Creator",
                description="Free tier with basic features",
                pricing_model=PricingModel.FREEMIUM,
                base_price=0.00,
                currency="USD",
                billing_cycles=[],  # No billing
                features=[
                    "limited_content_upload", "basic_analytics", "basic_protection",
                    "community_access"
                ],
                limits={
                    "uploads_per_month": 10,
                    "storage_gb": 1,
                    "bandwidth_gb": 5,
                    "collaboration_projects": 1,
                    "ai_processing_hours": 1
                },
                trial_period_days=0,
                setup_fee=0.00,
                cancellation_fee=0.00,
                upgrade_allowed=True,
                downgrade_allowed=False
            )
        }
    )
    
    # Billing Configurations
    billing_configurations: Dict[str, BillingConfiguration] = Field(
        default_factory=lambda: {
            "monthly": BillingConfiguration(
                cycle=BillingCycle.MONTHLY,
                price_modifier=1.0,
                discount_percentage=0.0,
                trial_period_days=14,
                grace_period_days=3,
                dunning_attempts=3,
                auto_renewal=True,
                proration_enabled=True
            ),
            "quarterly": BillingConfiguration(
                cycle=BillingCycle.QUARTERLY,
                price_modifier=2.85,  # 5% discount
                discount_percentage=5.0,
                trial_period_days=14,
                grace_period_days=7,
                dunning_attempts=4,
                auto_renewal=True,
                proration_enabled=True
            ),
            "yearly": BillingConfiguration(
                cycle=BillingCycle.YEARLY,
                price_modifier=10.0,  # 17% discount (12 months for 10)
                discount_percentage=17.0,
                trial_period_days=30,
                grace_period_days=14,
                dunning_attempts=5,
                auto_renewal=True,
                proration_enabled=True
            )
        }
    )
    
    # Revenue Optimization Configuration
    revenue_optimization: RevenueOptimization = Field(
        default_factory=lambda: RevenueOptimization(
            dynamic_pricing=True,
            demand_forecasting=True,
            price_elasticity_analysis=True,
            cohort_analysis=True,
            lifetime_value_tracking=True,
            churn_prediction=True,
            upselling_enabled=True,
            cross_selling_enabled=True
        )
    )
    
    # Churn Prevention Configuration
    churn_prevention: ChurnPreventionConfig = Field(
        default_factory=lambda: ChurnPreventionConfig(
            prediction_enabled=True,
            early_warning_days=30,
            intervention_strategies=[
                "personalized_outreach", "feature_recommendations",
                "usage_tutorials", "success_manager_assignment",
                "community_engagement", "exclusive_content_access"
            ],
            retention_campaigns=[
                "win_back_email_series", "discount_offers",
                "feature_previews", "success_stories",
                "community_challenges", "personalized_demos"
            ],
            win_back_campaigns=[
                "special_pricing", "extended_trial",
                "premium_features_free", "personal_consultation",
                "migration_assistance", "success_guarantee"
            ],
            discount_offers={
                "first_time_cancellation": 25.0,
                "high_value_customer": 50.0,
                "long_term_customer": 30.0,
                "enterprise_retention": 40.0
            },
            personalization_enabled=True,
            success_metrics=[
                "retention_rate", "churn_rate", "lifetime_value",
                "engagement_score", "feature_adoption", "satisfaction_score"
            ]
        )
    )
    
    # Subscription Management Settings
    subscription_management: Dict[str, Any] = Field(
        default_factory=lambda: {
            "auto_provisioning": True,
            "instant_upgrades": True,
            "proration_on_changes": True,
            "grace_period_enabled": True,
            "dunning_management": True,
            "failed_payment_retry": True,
            "automatic_suspension": True,
            "subscription_recovery": True,
            "usage_tracking": True,
            "overage_billing": True
        }
    )
    
    # Payment and Billing Settings
    payment_billing: Dict[str, Any] = Field(
        default_factory=lambda: {
            "multiple_payment_methods": True,
            "payment_method_backup": True,
            "automatic_payment_retry": True,
            "invoice_generation": True,
            "receipt_automation": True,
            "tax_calculation": True,
            "currency_conversion": True,
            "billing_address_required": True,
            "payment_reminders": True,
            "overdue_notifications": True
        }
    )
    
    # Trial and Freemium Settings
    trial_freemium: Dict[str, Any] = Field(
        default_factory=lambda: {
            "trial_period_enabled": True,
            "trial_credit_card_required": False,
            "trial_extension_allowed": True,
            "freemium_tier_enabled": True,
            "freemium_to_paid_conversion": True,
            "trial_reminders": True,
            "conversion_campaigns": True,
            "feature_gating": True,
            "usage_limits_enforcement": True,
            "upgrade_suggestions": True
        }
    )
    
    # Analytics and Reporting
    analytics_reporting: Dict[str, Any] = Field(
        default_factory=lambda: {
            "revenue_analytics": True,
            "subscription_metrics": True,
            "churn_analysis": True,
            "cohort_analysis": True,
            "ltv_calculation": True,
            "conversion_tracking": True,
            "usage_analytics": True,
            "financial_reporting": True,
            "dashboard_reporting": True,
            "custom_reports": True
        }
    )
    
    # Customer Success Settings
    customer_success: Dict[str, Any] = Field(
        default_factory=lambda: {
            "onboarding_automation": True,
            "success_milestones": True,
            "engagement_tracking": True,
            "health_scoring": True,
            "proactive_outreach": True,
            "usage_optimization": True,
            "feature_adoption_tracking": True,
            "satisfaction_surveys": True,
            "success_manager_assignment": True,
            "community_building": True
        }
    )
    
    # Integration Settings
    integration_settings: Dict[str, Any] = Field(
        default_factory=lambda: {
            "payment_gateway_integration": True,
            "crm_integration": True,
            "analytics_integration": True,
            "email_marketing_integration": True,
            "support_desk_integration": True,
            "accounting_integration": True,
            "webhook_support": True,
            "api_access": True,
            "third_party_apps": True,
            "data_export": True
        }
    )
    
    # Compliance and Security
    compliance_security: Dict[str, Any] = Field(
        default_factory=lambda: {
            "gdpr_compliance": True,
            "ccpa_compliance": True,
            "pci_compliance": True,
            "data_encryption": True,
            "audit_logging": True,
            "access_control": True,
            "data_retention_policies": True,
            "privacy_controls": True,
            "security_monitoring": True,
            "compliance_reporting": True
        }
    )
    
    class Config:
    """Config: class implementation"""
        env_prefix = "SUBSCRIPTION_MANAGEMENT_"
        case_sensitive = False
        extra = "allow"
    
    def get_tier_config(self, tier: str) -> Optional[SubscriptionTierConfig]:
        """Get subscription tier configuration"""
        return self.subscription_tiers.get(tier)
    
    def get_billing_config(self, cycle: str) -> Optional[BillingConfiguration]:
        """Get billing configuration by cycle"""
        return self.billing_configurations.get(cycle)
    
    def get_tier_price(self, tier: str, billing_cycle: str) -> float:
        """Calculate tier price for billing cycle"""
        tier_config = self.get_tier_config(tier)
        billing_config = self.get_billing_config(billing_cycle)
        
        if not tier_config or not billing_config:
            return 0.0
        
        base_price = tier_config.base_price
        price_modifier = billing_config.price_modifier
        
        return base_price * price_modifier
    
    def get_tier_features(self, tier: str) -> List[str]:
        """Get features for subscription tier"""
        config = self.get_tier_config(tier)
        return config.features if config else []
    
    def get_tier_limits(self, tier: str) -> Dict[str, Any]:
        """Get limits for subscription tier"""
        config = self.get_tier_config(tier)
        return config.limits if config else {}
    
    def is_upgrade_allowed(self, from_tier: str, to_tier: str) -> bool:
        """Check if upgrade is allowed between tiers"""
        from_config = self.get_tier_config(from_tier)
        to_config = self.get_tier_config(to_tier)
        
        if not from_config or not to_config:
            return False
        
        # Define tier hierarchy
        tier_hierarchy = {
            SubscriptionTier.FREEMIUM: 0,
            SubscriptionTier.TRIAL: 1,
            SubscriptionTier.BASIC: 2,
            SubscriptionTier.PROFESSIONAL: 3,
            SubscriptionTier.ENTERPRISE: 4,
            SubscriptionTier.CUSTOM: 5
        }
        
        from_level = tier_hierarchy.get(from_config.tier, 0)
        to_level = tier_hierarchy.get(to_config.tier, 0)
        
        return from_config.upgrade_allowed and to_level > from_level
    
    def is_downgrade_allowed(self, from_tier: str, to_tier: str) -> bool:
        """Check if downgrade is allowed between tiers"""
        from_config = self.get_tier_config(from_tier)
        to_config = self.get_tier_config(to_tier)
        
        if not from_config or not to_config:
            return False
        
        # Define tier hierarchy
        tier_hierarchy = {
            SubscriptionTier.FREEMIUM: 0,
            SubscriptionTier.TRIAL: 1,
            SubscriptionTier.BASIC: 2,
            SubscriptionTier.PROFESSIONAL: 3,
            SubscriptionTier.ENTERPRISE: 4,
            SubscriptionTier.CUSTOM: 5
        }
        
        from_level = tier_hierarchy.get(from_config.tier, 0)
        to_level = tier_hierarchy.get(to_config.tier, 0)
        
        return from_config.downgrade_allowed and to_level < from_level
    
    def get_trial_period(self, tier: str) -> int:
        """Get trial period for tier in days"""
        config = self.get_tier_config(tier)
        return config.trial_period_days if config else 0
    
    def get_discount_percentage(self, billing_cycle: str) -> float:
        """Get discount percentage for billing cycle"""
        config = self.get_billing_config(billing_cycle)
        return config.discount_percentage if config else 0.0
    
    def calculate_ltv(self, monthly_revenue: float, churn_rate: float) -> float:
        """Calculate customer lifetime value"""
        if churn_rate <= 0:
            return float('inf')
        return monthly_revenue / churn_rate
    
    def get_churn_intervention_strategies(self, risk_level: str) -> List[str]:
        """Get intervention strategies for churn risk level"""
        base_strategies = self.churn_prevention.intervention_strategies
        
        if risk_level == ChurnPredictionLevel.CRITICAL:
            return base_strategies + ["executive_outreach", "custom_solutions"]
        elif risk_level == ChurnPredictionLevel.HIGH:
            return base_strategies + ["success_manager_call", "discount_offer"]
        elif risk_level == ChurnPredictionLevel.MEDIUM:
            return base_strategies[:3]  # First 3 strategies
        else:
            return base_strategies[:2]  # First 2 strategies
    
    def validate_configuration(self) -> List[str]:
        """Validate the complete subscription management configuration"""
        errors = []
        
        # Validate subscription tiers
        for tier_name, config in self.subscription_tiers.items():
            if config.base_price < 0:
                errors.append(f"Tier '{tier_name}' has negative base price")
            if config.trial_period_days < 0:
                errors.append(f"Tier '{tier_name}' has negative trial period")
            if not config.features:
                errors.append(f"Tier '{tier_name}' has no features defined")
        
        # Validate billing configurations
        for cycle_name, config in self.billing_configurations.items():
            if config.price_modifier <= 0:
                errors.append(f"Billing cycle '{cycle_name}' has invalid price modifier")
            if config.discount_percentage < 0 or config.discount_percentage > 100:
                errors.append(f"Billing cycle '{cycle_name}' has invalid discount percentage")
            if config.dunning_attempts <= 0:
                errors.append(f"Billing cycle '{cycle_name}' has invalid dunning attempts")
        
        # Check that at least one paid tier exists
        paid_tiers = [
            tier for tier, config in self.subscription_tiers.items()
            if config.base_price > 0
        ]
        if not paid_tiers:
            errors.append("No paid subscription tiers configured")
        
        return errors


# Global subscription management settings instance
subscription_management_settings = SubscriptionManagementSettings()

__all__ = [
    "SubscriptionManagementSettings",
    "subscription_management_settings",
    "SubscriptionTier",
    "BillingCycle",
    "SubscriptionStatus",
    "PricingModel",
    "RevenueModel",
    "ChurnPredictionLevel",
    "SubscriptionTierConfig",
    "BillingConfiguration",
    "RevenueOptimization",
    "ChurnPreventionConfig"
]