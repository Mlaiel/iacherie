"""Monetization Configuration Module for IA-Influencer Agent Platform
==================================================================

Professional monetization and revenue management configuration.
Complete ecosystem for multi-platform revenue tracking, payment processing, and fraud protection.

Author: Fahed Mlaiel <mlaiel@live.de>
Project: IA-Influencer Agent + Content Protection Platform
Team: Lead Dev IA + Backend Senior + ML Engineer + DBA + Security + Microservices + Audio + DevOps + FinTech Expert

⚠️  IMPORTANT COPYRIGHT NOTICE ⚠️
=====================================
This code is the intellectual property of Fahed Mlaiel.
Any unauthorized use, reproduction, distribution, or modification of this code
without explicit written permission from the author is STRICTLY PROHIBITED.

LEGAL WARNING: Violation of this copyright will result in:
- Immediate legal action under German and International Copyright Law
- Financial damages and compensation claims
- Criminal prosecution where applicable
- Permanent ban from all related projects and services

Contact: mlaiel@live.de for licensing inquiries and authorization.
"""# Core Revenue Management
from .revenue_config import RevenueTrackingConfig, revenue_config

# Payment Processing
from .payment_processor_config import PaymentProcessorConfig, payment_config

# Payout Management
from .payout_config import PayoutConfig, payout_config

# Pricing and Subscription
from .pricing_config import PricingConfig, pricing_config
from .subscription_config import SubscriptionConfig, subscription_config

# Royalty Management
from .royalty_config import RoyaltyConfig, royalty_config

# Invoicing
from .invoice_config import InvoiceConfig, invoice_config

# Analytics (Core)
from .analytics_config import RevenueAnalyticsConfig, analytics_config

# Advanced Analytics and ML
from .revenue_analytics_advanced_config import (
    RevenueAnalyticsAdvancedConfig, 
    revenue_analytics_advanced_config
)

# Platform Integration
from .platform_integration_config import (
    PlatformIntegrationManager,
    PlatformIntegrationConfig,
    platform_integration_config
)

# License Management
from .license_management_config import (
    LicenseManagementConfig,
    LicenseAgreement,
    license_management_config
)

# Fraud Detection and Risk Management
from .fraud_detection_config import (
    FraudDetectionConfig,
    fraud_detection_config
)

# Regulatory Compliance
from .regulatory_compliance_config import (
    RegulatoryComplianceConfig,
    regulatory_compliance_config
)

__all__ = [
    # Core Configuration Classes
    'RevenueTrackingConfig',
    'PaymentProcessorConfig', 
    'PayoutConfig',
    'PricingConfig',
    'SubscriptionConfig',
    'RoyaltyConfig',
    'InvoiceConfig',
    'RevenueAnalyticsConfig',
    
    # Advanced Configuration Classes
    'RevenueAnalyticsAdvancedConfig',
    'PlatformIntegrationManager',
    'PlatformIntegrationConfig',
    'LicenseManagementConfig',
    'LicenseAgreement',
    'FraudDetectionConfig',
    'RegulatoryComplianceConfig',
    
    # Global Configuration Instances
    'revenue_config',
    'payment_config',
    'payout_config',
    'pricing_config',
    'subscription_config',
    'royalty_config',
    'invoice_config',
    'analytics_config',
    'revenue_analytics_advanced_config',
    'platform_integration_config',
    'license_management_config',
    'fraud_detection_config',
    'regulatory_compliance_config'
]
