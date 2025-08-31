"""
Revenue Security Configuration Module
====================================

Advanced revenue security and monetization configuration for IA Influencer Agent platform.
Provides comprehensive security settings for payment processing, revenue tracking,
financial fraud detection, and creator monetization protection.

Business Logic Integration:
- Secure revenue tracking across multiple platforms
- Payment processing security and compliance
- Financial fraud detection and prevention
- Creator revenue protection and distribution

Author: Fahed Mlaiel <mlaiel@live.de>
Team: Lead Dev IA + Backend + Security + FinTech Engineers

 COPYRIGHT WARNING:
This code is proprietary and belongs to Fahed Mlaiel.
Any unauthorized use, copying, or distribution without explicit 
written permission from Fahed Mlaiel is strictly prohibited.
Contact: mlaiel@live.de for licensing inquiries.
"""

import os
from typing import Dict, List, Optional, Any, Set
from dataclasses import dataclass, field
from datetime import timedelta
from decimal import Decimal
from enum import Enum


class PaymentProvider(Enum):
    """Supported payment providers."""
    STRIPE = "stripe"
    PAYPAL = "paypal"
    WISE = "wise"
    BANK_TRANSFER = "bank_transfer"
    CRYPTOCURRENCY = "crypto"
    APPLE_PAY = "apple_pay"
    GOOGLE_PAY = "google_pay"


class RevenueSource(Enum):
    """Revenue sources for content creators."""
    SPOTIFY_ROYALTIES = "spotify_royalties"
    YOUTUBE_ADSENSE = "youtube_adsense"
    INSTAGRAM_CREATOR = "instagram_creator"
    TIKTOK_CREATOR = "tiktok_creator"
    DIRECT_SALES = "direct_sales"
    LICENSING_FEES = "licensing_fees"
    BRAND_PARTNERSHIPS = "brand_partnerships"
    MERCHANDISE = "merchandise"
    SUBSCRIPTION = "subscription"
    DONATIONS = "donations"


class FraudRiskLevel(Enum):
    """Fraud risk assessment levels."""
    VERY_LOW = "very_low"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    VERY_HIGH = "very_high"
    CRITICAL = "critical"


class ComplianceRegion(Enum):
    """Financial compliance regions."""
    EU = "eu"
    US = "us"
    UK = "uk"
    CANADA = "canada"
    AUSTRALIA = "australia"
    GLOBAL = "global"


@dataclass
class PaymentSecurityConfig:
    """Payment processing security configuration."""
    # PCI DSS compliance
    pci_compliance_level: str = "Level 1"
    tokenization_enabled: bool = True
    vault_storage: bool = True
    
    # Encryption
    payment_data_encryption: str = "AES-256-GCM"
    key_management: str = "HSM"  # Hardware Security Module
    end_to_end_encryption: bool = True
    
    # Security controls
    card_verification: bool = True
    address_verification: bool = True
    cvv_verification: bool = True
    three_d_secure: bool = True
    
    # Payment limits
    daily_limit_eur: Decimal = Decimal("50000.00")
    monthly_limit_eur: Decimal = Decimal("500000.00")
    transaction_limit_eur: Decimal = Decimal("10000.00")
    
    # Multi-factor authentication for payments
    mfa_required_above_eur: Decimal = Decimal("1000.00")
    biometric_verification: bool = True
    
    # Provider configurations
    provider_configs: Dict[PaymentProvider, Dict[str, Any]] = field(default_factory=lambda: {
        PaymentProvider.STRIPE: {
            "api_key": os.getenv("STRIPE_SECRET_KEY", ""),
            "webhook_secret": os.getenv("STRIPE_WEBHOOK_SECRET", ""),
            "connect_enabled": True,
            "instant_payouts": True
        },
        PaymentProvider.PAYPAL: {
            "client_id": os.getenv("PAYPAL_CLIENT_ID", ""),
            "client_secret": os.getenv("PAYPAL_CLIENT_SECRET", ""),
            "sandbox_mode": False,
            "partner_attribution_id": "IA_INFLUENCER_AGENT"
        },
        PaymentProvider.WISE: {
            "api_key": os.getenv("WISE_API_KEY", ""),
            "profile_id": os.getenv("WISE_PROFILE_ID", ""),
            "webhook_secret": os.getenv("WISE_WEBHOOK_SECRET", "")
        }
    })


@dataclass
class FraudDetectionConfig:
    """Financial fraud detection configuration."""
    # AI-powered fraud detection
    ml_fraud_detection: bool = True
    real_time_analysis: bool = True
    behavioral_analytics: bool = True
    
    # Risk scoring
    risk_scoring_model: str = "gradient_boosting"
    risk_threshold_block: float = 0.85
    risk_threshold_review: float = 0.65
    risk_threshold_monitor: float = 0.35
    
    # Fraud indicators
    velocity_checks: bool = True
    geolocation_checks: bool = True
    device_fingerprinting: bool = True
    ip_reputation_checks: bool = True
    
    # Transaction patterns
    unusual_amount_detection: bool = True
    frequency_analysis: bool = True
    cross_platform_correlation: bool = True
    
    # Data sources for fraud detection
    fraud_databases: List[str] = field(default_factory=lambda: [
        "kount",
        "sift",
        "forter",
        "internal_blacklist"
    ])
    
    # Response actions by risk level
    risk_responses: Dict[FraudRiskLevel, List[str]] = field(default_factory=lambda: {
        FraudRiskLevel.VERY_LOW: ["allow", "log"],
        FraudRiskLevel.LOW: ["allow", "monitor"],
        FraudRiskLevel.MEDIUM: ["review", "additional_verification"],
        FraudRiskLevel.HIGH: ["block", "manual_review", "alert"],
        FraudRiskLevel.VERY_HIGH: ["block", "freeze_account", "investigate"],
        FraudRiskLevel.CRITICAL: ["block", "freeze_account", "legal_review", "law_enforcement"]
    })


@dataclass
class RevenueTrackingConfig:
    """Revenue tracking and analytics configuration."""
    # Real-time tracking
    real_time_tracking: bool = True
    tracking_interval_minutes: int = 15
    
    # Platform API configurations
    platform_apis: Dict[str, Dict[str, Any]] = field(default_factory=lambda: {
        "spotify": {
            "api_endpoint": "https://api.spotify.com/v1",
            "auth_method": "oauth2",
            "rate_limit": "100/minute",
            "data_lag_hours": 24
        },
        "youtube": {
            "api_endpoint": "https://www.googleapis.com/youtube/analytics/v2",
            "auth_method": "oauth2",
            "rate_limit": "10000/day",
            "data_lag_hours": 48
        },
        "instagram": {
            "api_endpoint": "https://graph.facebook.com/v18.0",
            "auth_method": "oauth2",
            "rate_limit": "200/hour",
            "data_lag_hours": 24
        },
        "tiktok": {
            "api_endpoint": "https://business-api.tiktok.com/open_api/v1.3",
            "auth_method": "oauth2",
            "rate_limit": "1000/day",
            "data_lag_hours": 72
        }
    })
    
    # Revenue calculation
    commission_rates: Dict[RevenueSource, Decimal] = field(default_factory=lambda: {
        RevenueSource.SPOTIFY_ROYALTIES: Decimal("0.05"),
        RevenueSource.YOUTUBE_ADSENSE: Decimal("0.10"),
        RevenueSource.INSTAGRAM_CREATOR: Decimal("0.08"),
        RevenueSource.TIKTOK_CREATOR: Decimal("0.12"),
        RevenueSource.DIRECT_SALES: Decimal("0.15"),
        RevenueSource.LICENSING_FEES: Decimal("0.20"),
        RevenueSource.BRAND_PARTNERSHIPS: Decimal("0.25"),
        RevenueSource.MERCHANDISE: Decimal("0.10"),
        RevenueSource.SUBSCRIPTION: Decimal("0.05"),
        RevenueSource.DONATIONS: Decimal("0.03")
    })
    
    # Revenue validation
    anomaly_detection: bool = True
    revenue_reconciliation: bool = True
    cross_platform_validation: bool = True
    
    # Reporting and analytics
    automated_reporting: bool = True
    predictive_analytics: bool = True
    revenue_forecasting: bool = True


@dataclass
class PayoutConfig:
    """Automated payout configuration."""
    # Payout frequency
    default_frequency: str = "weekly"
    minimum_payout_amount: Decimal = Decimal("25.00")
    maximum_payout_amount: Decimal = Decimal("25000.00")
    
    # Payout scheduling
    payout_days: List[str] = field(default_factory=lambda: ["friday"])
    payout_time_utc: str = "14:00"
    holiday_delay: bool = True
    
    # Payout methods by creator tier
    payout_methods: Dict[str, List[PaymentProvider]] = field(default_factory=lambda: {
        "free": [PaymentProvider.PAYPAL],
        "professional": [PaymentProvider.STRIPE, PaymentProvider.PAYPAL, PaymentProvider.WISE],
        "enterprise": [PaymentProvider.STRIPE, PaymentProvider.WISE, PaymentProvider.BANK_TRANSFER]
    })
    
    # Currency support
    supported_currencies: List[str] = field(default_factory=lambda: [
        "EUR", "USD", "GBP", "CAD", "AUD", "JPY", "CHF", "SEK", "NOK", "DKK"
    ])
    
    # Tax and compliance
    tax_withholding: bool = True
    tax_forms_required: bool = True
    compliance_checks: bool = True
    
    # Payout security
    dual_approval_above_eur: Decimal = Decimal("5000.00")
    verification_required: bool = True
    cooling_off_period_hours: int = 24


@dataclass
class AuditConfig:
    """Financial audit and compliance configuration."""
    # Audit trail
    comprehensive_logging: bool = True
    immutable_records: bool = True
    blockchain_verification: bool = False
    
    # Compliance requirements
    sox_compliance: bool = True
    gdpr_financial_data: bool = True
    pci_audit_logs: bool = True
    
    # Retention policies
    transaction_retention_years: int = 7
    audit_log_retention_years: int = 10
    tax_document_retention_years: int = 7
    
    # Regular auditing
    automated_reconciliation: bool = True
    daily_balance_checks: bool = True
    monthly_compliance_reports: bool = True
    quarterly_financial_audits: bool = True
    
    # External auditing
    third_party_audits: bool = True
    penetration_testing: bool = True
    compliance_certifications: List[str] = field(default_factory=lambda: [
        "PCI DSS Level 1",
        "SOC 2 Type II",
        "ISO 27001"
    ])


@dataclass
class DisputeResolutionConfig:
    """Payment dispute and chargeback configuration."""
    # Dispute handling
    automated_dispute_response: bool = True
    evidence_collection: bool = True
    representment_automation: bool = True
    
    # Chargeback protection
    chargeback_alerts: bool = True
    liability_shift: bool = True
    issuer_declined_optimization: bool = True
    
    # Dispute categories
    dispute_types: Dict[str, Dict[str, Any]] = field(default_factory=lambda: {
        "fraudulent": {
            "auto_response": True,
            "evidence_required": ["transaction_log", "user_verification", "device_fingerprint"],
            "success_rate_target": 0.75
        },
        "unrecognized": {
            "auto_response": True,
            "evidence_required": ["transaction_details", "communication_log"],
            "success_rate_target": 0.85
        },
        "duplicate": {
            "auto_response": True,
            "evidence_required": ["transaction_uniqueness", "system_log"],
            "success_rate_target": 0.90
        },
        "subscription_cancelled": {
            "auto_response": False,
            "evidence_required": ["cancellation_policy", "usage_data"],
            "success_rate_target": 0.60
        }
    })
    
    # Response timeframes
    response_timeframes: Dict[str, int] = field(default_factory=lambda: {
        "initial_response_hours": 24,
        "evidence_submission_days": 7,
        "representment_days": 10
    })


@dataclass
class TaxComplianceConfig:
    """Tax compliance and reporting configuration."""
    # Tax calculation
    automated_tax_calculation: bool = True
    real_time_tax_rates: bool = True
    multi_jurisdiction_support: bool = True
    
    # Tax providers
    tax_service_providers: List[str] = field(default_factory=lambda: [
        "avalara",
        "taxjar",
        "vertex"
    ])
    
    # Tax types
    supported_tax_types: List[str] = field(default_factory=lambda: [
        "vat",
        "gst",
        "sales_tax",
        "income_tax_withholding",
        "digital_services_tax"
    ])
    
    # Compliance by region
    regional_compliance: Dict[ComplianceRegion, Dict[str, Any]] = field(default_factory=lambda: {
        ComplianceRegion.EU: {
            "vat_required": True,
            "oss_registration": True,
            "digital_services_directive": True,
            "gdpr_compliance": True
        },
        ComplianceRegion.US: {
            "sales_tax_nexus": True,
            "1099_reporting": True,
            "state_compliance": True,
            "marketplace_facilitator": True
        },
        ComplianceRegion.UK: {
            "vat_required": True,
            "making_tax_digital": True,
            "cis_scheme": False
        }
    })
    
    # Reporting
    automated_tax_reporting: bool = True
    quarterly_reports: bool = True
    annual_summaries: bool = True


@dataclass
class RevenueSecurityConfig:
    """Main revenue security configuration container."""
    payment_security: PaymentSecurityConfig = field(default_factory=PaymentSecurityConfig)
    fraud_detection: FraudDetectionConfig = field(default_factory=FraudDetectionConfig)
    revenue_tracking: RevenueTrackingConfig = field(default_factory=RevenueTrackingConfig)
    payout: PayoutConfig = field(default_factory=PayoutConfig)
    audit: AuditConfig = field(default_factory=AuditConfig)
    dispute_resolution: DisputeResolutionConfig = field(default_factory=DisputeResolutionConfig)
    tax_compliance: TaxComplianceConfig = field(default_factory=TaxComplianceConfig)
    
    # Global revenue security settings
    encryption_at_rest: bool = True
    encryption_in_transit: bool = True
    zero_knowledge_architecture: bool = False
    
    # Creator protection
    creator_revenue_insurance: bool = True
    creator_fraud_protection: bool = True
    creator_dispute_support: bool = True
    
    # Platform integration security
    api_rate_limiting: bool = True
    webhook_verification: bool = True
    secure_api_gateways: bool = True
    
    # Emergency procedures
    circuit_breaker_enabled: bool = True
    emergency_stop_procedures: bool = True
    incident_response_plan: bool = True


# Default configuration instance
revenue_security_config = RevenueSecurityConfig()


def get_revenue_security_config() -> RevenueSecurityConfig:
    """Get the revenue security configuration instance."""



    return revenue_security_config


def validate_revenue_security_config(config: RevenueSecurityConfig) -> bool:
    """Validate revenue security configuration settings."""
    # Validate payment limits
    if config.payment_security.transaction_limit_eur <= 0:
        raise ValueError("Transaction limit must be positive")
    
    if config.payment_security.daily_limit_eur < config.payment_security.transaction_limit_eur:
        raise ValueError("Daily limit must be >= transaction limit")
    
    # Validate fraud thresholds
    fraud_config = config.fraud_detection
    if not 0.0 <= fraud_config.risk_threshold_monitor <= fraud_config.risk_threshold_review <= fraud_config.risk_threshold_block <= 1.0:
        raise ValueError("Fraud risk thresholds must be in ascending order between 0 and 1")
    
    # Validate payout configuration
    if config.payout.minimum_payout_amount <= 0:
        raise ValueError("Minimum payout amount must be positive")
    
    if config.payout.maximum_payout_amount <= config.payout.minimum_payout_amount:
        raise ValueError("Maximum payout must be > minimum payout")
    
    # Validate commission rates
    for source, rate in config.revenue_tracking.commission_rates.items():
        if not 0.0 <= rate <= 1.0:
            raise ValueError(f"Invalid commission rate for {source}: {rate}")
    
    return True


def get_creator_tier_config(tier: str) -> Dict[str, Any]:
    """Get revenue configuration overrides for creator tiers."""
    tier_configs = {
        "free": {
            "payment_security.daily_limit_eur": Decimal("1000.00"),
            "payment_security.monthly_limit_eur": Decimal("5000.00"),
            "payout.minimum_payout_amount": Decimal("50.00"),
            "revenue_tracking.tracking_interval_minutes": 60
        },
        "professional": {
            "payment_security.daily_limit_eur": Decimal("10000.00"),
            "payment_security.monthly_limit_eur": Decimal("100000.00"),
            "payout.minimum_payout_amount": Decimal("25.00"),
            "revenue_tracking.tracking_interval_minutes": 15
        },
        "enterprise": {
            "payment_security.daily_limit_eur": Decimal("50000.00"),
            "payment_security.monthly_limit_eur": Decimal("500000.00"),
            "payout.minimum_payout_amount": Decimal("10.00"),
            "revenue_tracking.tracking_interval_minutes": 5
        }
    }
    
    return tier_configs.get(tier, tier_configs["free"])
