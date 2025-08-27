"""
Revenue Tracking Configuration Module for Content Protection
==========================================================

Professional revenue tracking configuration for content protection and monetization.
Integrates with content protection systems to track revenue from protected content
and automate licensing deals based on usage patterns.

Author: Fahed Mlaiel <mlaiel@live.de>
Project: IA-Influencer Agent + Content Protection Platform
Team: Lead Dev IA + Backend Senior + ML Engineer + DBA + Security + Microservices + Audio + DevOps + IA Prompt Engineer

⚠️  COPYRIGHT WARNING:
This code is the exclusive intellectual property of Fahed Mlaiel.
Any unauthorized use, reproduction, modification, or distribution of this code
without explicit written permission from Fahed Mlaiel (mlaiel@live.de) is strictly prohibited.
Violators will be prosecuted to the full extent of the law.

Contact: mlaiel@live.de for licensing inquiries.
"""

from typing import Dict, Any, Optional, List, Set
from dataclasses import dataclass, field
from enum import Enum
from decimal import Decimal
import os


class RevenueTrackingMode(str, Enum):
    """Revenue tracking operational modes."""
    REAL_TIME = "real_time"
    BATCH = "batch"
    HYBRID = "hybrid"
    ON_DEMAND = "on_demand"


class PlatformType(str, Enum):
    """Supported platforms for revenue tracking."""
    YOUTUBE = "youtube"
    SPOTIFY = "spotify"
    INSTAGRAM = "instagram"
    TIKTOK = "tiktok"
    TWITTER = "twitter"
    FACEBOOK = "facebook"
    SOUNDCLOUD = "soundcloud"
    BANDCAMP = "bandcamp"
    TWITCH = "twitch"
    PATREON = "patreon"
    ONLYFANS = "onlyfans"
    CUSTOM = "custom"


class RevenueStreamType(str, Enum):
    """Types of revenue streams to track."""
    STREAMING_ROYALTIES = "streaming_royalties"
    LICENSING_FEES = "licensing_fees"
    BRAND_PARTNERSHIPS = "brand_partnerships"
    MERCHANDISE_SALES = "merchandise_sales"
    LIVE_PERFORMANCES = "live_performances"
    DIGITAL_SALES = "digital_sales"
    ADVERTISING_REVENUE = "advertising_revenue"
    SUBSCRIPTION_REVENUE = "subscription_revenue"
    COLLABORATION_SPLITS = "collaboration_splits"
    COPYRIGHT_CLAIMS = "copyright_claims"


class CurrencyType(str, Enum):
    """Supported currencies for revenue tracking."""
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


class PaymentProcessor(str, Enum):
    """Supported payment processors."""
    STRIPE = "stripe"
    PAYPAL = "paypal"
    WISE = "wise"
    BLOCKCHAIN = "blockchain"
    BANK_TRANSFER = "bank_transfer"
    CRYPTO = "crypto"


@dataclass
class PlatformCredentials:
    """API credentials configuration for platform integration."""
    platform: PlatformType
    api_key: str
    api_secret: str
    client_id: Optional[str] = None
    client_secret: Optional[str] = None
    access_token: Optional[str] = None
    refresh_token: Optional[str] = None
    webhook_secret: Optional[str] = None
    environment: str = "production"  # production, staging, sandbox
    rate_limit_per_minute: int = 60
    timeout_seconds: int = 30


@dataclass
class RevenueMetricsConfig:
    """Configuration for revenue metrics calculation."""
    enable_real_time_metrics: bool = True
    enable_historical_analysis: bool = True
    enable_forecasting: bool = True
    enable_anomaly_detection: bool = True
    
    # Metrics calculation intervals
    real_time_interval_seconds: int = 30
    hourly_aggregation: bool = True
    daily_aggregation: bool = True
    weekly_aggregation: bool = True
    monthly_aggregation: bool = True
    yearly_aggregation: bool = True
    
    # Performance thresholds
    min_revenue_threshold: Decimal = Decimal("0.01")
    significant_change_threshold: Decimal = Decimal("0.05")  # 5%
    anomaly_detection_sensitivity: float = 0.95
    forecasting_horizon_days: int = 90


@dataclass
class PaymentProcessingConfig:
    """Configuration for payment processing and automation."""
    enable_automated_payments: bool = True
    payment_processors: List[PaymentProcessor] = field(
        default_factory=lambda: [PaymentProcessor.STRIPE, PaymentProcessor.PAYPAL]
    )
    
    # Payment thresholds
    minimum_payout_amount: Decimal = Decimal("50.00")
    maximum_payout_amount: Decimal = Decimal("10000.00")
    auto_payout_threshold: Decimal = Decimal("100.00")
    
    # Payment scheduling
    payment_frequency_days: int = 30
    enable_instant_payments: bool = False
    enable_scheduled_payments: bool = True
    
    # Security settings
    require_manual_approval_above: Decimal = Decimal("1000.00")
    enable_fraud_detection: bool = True
    enable_payment_verification: bool = True
    
    # Processing fees
    stripe_fee_percentage: Decimal = Decimal("2.9")
    paypal_fee_percentage: Decimal = Decimal("2.9")
    wise_fee_percentage: Decimal = Decimal("0.5")


@dataclass
class LicensingAutomationConfig:
    """Configuration for automated licensing based on content protection."""
    enable_automated_licensing: bool = True
    enable_smart_contracts: bool = True
    enable_blockchain_verification: bool = False
    
    # Licensing terms
    default_license_duration_months: int = 12
    default_territory: str = "worldwide"
    default_usage_rights: List[str] = field(
        default_factory=lambda: ["commercial", "non_commercial", "broadcast"]
    )
    
    # Pricing automation
    enable_dynamic_pricing: bool = True
    base_licensing_fee: Decimal = Decimal("100.00")
    usage_multiplier: Dict[str, Decimal] = field(
        default_factory=lambda: {
            "commercial": Decimal("2.0"),
            "broadcast": Decimal("3.0"),
            "exclusive": Decimal("5.0")
        }
    )
    
    # Revenue sharing
    default_creator_share_percentage: Decimal = Decimal("70.0")
    platform_commission_percentage: Decimal = Decimal("20.0")
    processing_fee_percentage: Decimal = Decimal("10.0")


@dataclass
class ComplianceConfig:
    """Configuration for financial and legal compliance."""
    enable_gdpr_compliance: bool = True
    enable_ccpa_compliance: bool = True
    enable_sox_compliance: bool = True
    enable_pci_dss_compliance: bool = True
    
    # Tax compliance
    enable_tax_reporting: bool = True
    tax_jurisdictions: List[str] = field(
        default_factory=lambda: ["US", "EU", "UK", "CA"]
    )
    automatic_tax_calculation: bool = True
    
    # Audit and logging
    enable_audit_trail: bool = True
    enable_financial_logging: bool = True
    audit_retention_days: int = 2555  # 7 years
    
    # Data protection
    enable_data_encryption: bool = True
    pii_anonymization: bool = True
    data_retention_days: int = 1095  # 3 years


@dataclass
class AlertingConfig:
    """Configuration for revenue tracking alerts and notifications."""
    enable_revenue_alerts: bool = True
    enable_payment_alerts: bool = True
    enable_anomaly_alerts: bool = True
    enable_compliance_alerts: bool = True
    
    # Alert thresholds
    significant_revenue_change_percentage: Decimal = Decimal("20.0")
    payment_failure_threshold: int = 3
    anomaly_score_threshold: float = 0.8
    
    # Notification channels
    email_notifications: bool = True
    webhook_notifications: bool = True
    slack_notifications: bool = False
    discord_notifications: bool = False
    
    # Notification settings
    notification_emails: List[str] = field(default_factory=list)
    webhook_urls: List[str] = field(default_factory=list)
    notification_cooldown_minutes: int = 30


@dataclass
class PerformanceConfig:
    """Performance configuration for revenue tracking system."""
    # Processing limits
    max_concurrent_requests: int = 100
    request_timeout_seconds: int = 30
    max_retry_attempts: int = 3
    backoff_multiplier: float = 2.0
    
    # Caching configuration
    enable_caching: bool = True
    cache_ttl_seconds: int = 300
    max_cache_size_mb: int = 1024
    
    # Database optimization
    enable_connection_pooling: bool = True
    max_db_connections: int = 50
    query_timeout_seconds: int = 30
    enable_query_optimization: bool = True
    
    # Background processing
    enable_background_tasks: bool = True
    task_queue_size: int = 1000
    worker_concurrency: int = 10


@dataclass
class SecurityConfig:
    """Security configuration for revenue tracking."""
    # Authentication
    require_authentication: bool = True
    token_expiry_hours: int = 24
    enable_two_factor_auth: bool = True
    
    # Encryption
    encryption_algorithm: str = "AES-256-GCM"
    enable_field_level_encryption: bool = True
    encrypt_sensitive_data: bool = True
    
    # Access control
    enable_role_based_access: bool = True
    admin_roles: List[str] = field(
        default_factory=lambda: ["admin", "finance_manager", "compliance_officer"]
    )
    user_roles: List[str] = field(
        default_factory=lambda: ["creator", "viewer", "analyst"]
    )
    
    # Rate limiting
    enable_rate_limiting: bool = True
    requests_per_minute: int = 60
    requests_per_hour: int = 1000
    
    # Monitoring
    enable_security_logging: bool = True
    enable_intrusion_detection: bool = True
    log_retention_days: int = 90


@dataclass
class RevenueTrackingConfig:
    """Main revenue tracking configuration for content protection."""
    
    # Core settings
    tracking_mode: RevenueTrackingMode = RevenueTrackingMode.HYBRID
    supported_platforms: Set[PlatformType] = field(
        default_factory=lambda: {
            PlatformType.YOUTUBE, PlatformType.SPOTIFY, PlatformType.INSTAGRAM,
            PlatformType.TIKTOK, PlatformType.TWITTER, PlatformType.SOUNDCLOUD
        }
    )
    supported_revenue_streams: Set[RevenueStreamType] = field(
        default_factory=lambda: {
            RevenueStreamType.STREAMING_ROYALTIES, RevenueStreamType.LICENSING_FEES,
            RevenueStreamType.BRAND_PARTNERSHIPS, RevenueStreamType.COPYRIGHT_CLAIMS
        }
    )
    default_currency: CurrencyType = CurrencyType.USD
    
    # Platform configurations
    platform_credentials: Dict[PlatformType, PlatformCredentials] = field(default_factory=dict)
    
    # Component configurations
    metrics_config: RevenueMetricsConfig = field(default_factory=RevenueMetricsConfig)
    payment_config: PaymentProcessingConfig = field(default_factory=PaymentProcessingConfig)
    licensing_config: LicensingAutomationConfig = field(default_factory=LicensingAutomationConfig)
    compliance_config: ComplianceConfig = field(default_factory=ComplianceConfig)
    alerting_config: AlertingConfig = field(default_factory=AlertingConfig)
    performance_config: PerformanceConfig = field(default_factory=PerformanceConfig)
    security_config: SecurityConfig = field(default_factory=SecurityConfig)
    
    # Integration settings
    enable_content_protection_integration: bool = True
    enable_fingerprinting_integration: bool = True
    enable_takedown_integration: bool = True
    enable_watermark_integration: bool = True
    
    def validate_config(self) -> bool:
        """Validate the revenue tracking configuration."""
        try:
            # Validate basic settings
            if not self.supported_platforms:
                raise ValueError("At least one platform must be supported")
            
            if not self.supported_revenue_streams:
                raise ValueError("At least one revenue stream must be supported")
            
            # Validate payment thresholds
            if self.payment_config.minimum_payout_amount <= 0:
                raise ValueError("Minimum payout amount must be positive")
            
            if (self.payment_config.minimum_payout_amount >= 
                self.payment_config.maximum_payout_amount):
                raise ValueError("Minimum payout must be less than maximum payout")
            
            # Validate performance settings
            if self.performance_config.max_concurrent_requests <= 0:
                raise ValueError("Max concurrent requests must be positive")
            
            if self.performance_config.request_timeout_seconds <= 0:
                raise ValueError("Request timeout must be positive")
            
            # Validate security settings
            if self.security_config.token_expiry_hours <= 0:
                raise ValueError("Token expiry must be positive")
            
            return True
            
        except Exception as e:
            print(f"Revenue tracking configuration validation error: {e}")
            return False
    
    @classmethod
    def from_environment(cls) -> 'RevenueTrackingConfig':
        """Create configuration from environment variables."""
        config = cls()
        
        # Load basic settings from environment
        if os.getenv('REVENUE_TRACKING_MODE'):
            config.tracking_mode = RevenueTrackingMode(os.getenv('REVENUE_TRACKING_MODE'))
        
        if os.getenv('DEFAULT_CURRENCY'):
            config.default_currency = CurrencyType(os.getenv('DEFAULT_CURRENCY'))
        
        # Load security settings
        if os.getenv('REQUIRE_AUTHENTICATION'):
            config.security_config.require_authentication = os.getenv('REQUIRE_AUTHENTICATION').lower() == 'true'
        
        if os.getenv('ENABLE_TWO_FACTOR_AUTH'):
            config.security_config.enable_two_factor_auth = os.getenv('ENABLE_TWO_FACTOR_AUTH').lower() == 'true'
        
        # Load performance settings
        if os.getenv('MAX_CONCURRENT_REQUESTS'):
            config.performance_config.max_concurrent_requests = int(os.getenv('MAX_CONCURRENT_REQUESTS'))
        
        if os.getenv('REQUEST_TIMEOUT_SECONDS'):
            config.performance_config.request_timeout_seconds = int(os.getenv('REQUEST_TIMEOUT_SECONDS'))
        
        return config
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary format."""
        return {
            'tracking_mode': self.tracking_mode.value,
            'supported_platforms': [platform.value for platform in self.supported_platforms],
            'supported_revenue_streams': [stream.value for stream in self.supported_revenue_streams],
            'default_currency': self.default_currency.value,
            'metrics_config': {
                'enable_real_time_metrics': self.metrics_config.enable_real_time_metrics,
                'enable_forecasting': self.metrics_config.enable_forecasting,
                'forecasting_horizon_days': self.metrics_config.forecasting_horizon_days
            },
            'payment_config': {
                'enable_automated_payments': self.payment_config.enable_automated_payments,
                'minimum_payout_amount': str(self.payment_config.minimum_payout_amount),
                'payment_frequency_days': self.payment_config.payment_frequency_days
            },
            'security_config': {
                'require_authentication': self.security_config.require_authentication,
                'enable_two_factor_auth': self.security_config.enable_two_factor_auth,
                'enable_rate_limiting': self.security_config.enable_rate_limiting
            }
        }


# Factory functions for common configurations

def create_production_config() -> RevenueTrackingConfig:
    """Create production-ready revenue tracking configuration."""
    config = RevenueTrackingConfig()
    
    # Production security settings
    config.security_config.require_authentication = True
    config.security_config.enable_two_factor_auth = True
    config.security_config.enable_rate_limiting = True
    config.security_config.enable_security_logging = True
    config.security_config.enable_intrusion_detection = True
    
    # Production performance settings
    config.performance_config.max_concurrent_requests = 200
    config.performance_config.enable_caching = True
    config.performance_config.enable_connection_pooling = True
    config.performance_config.enable_query_optimization = True
    
    # Production compliance settings
    config.compliance_config.enable_gdpr_compliance = True
    config.compliance_config.enable_ccpa_compliance = True
    config.compliance_config.enable_sox_compliance = True
    config.compliance_config.enable_pci_dss_compliance = True
    config.compliance_config.enable_audit_trail = True
    
    return config


def create_development_config() -> RevenueTrackingConfig:
    """Create development-friendly revenue tracking configuration."""
    config = RevenueTrackingConfig()
    
    # Development settings
    config.tracking_mode = RevenueTrackingMode.BATCH
    config.security_config.require_authentication = False
    config.security_config.enable_two_factor_auth = False
    config.performance_config.max_concurrent_requests = 10
    config.compliance_config.enable_audit_trail = False
    
    return config


def create_testing_config() -> RevenueTrackingConfig:
    """Create testing configuration for revenue tracking."""
    config = RevenueTrackingConfig()
    
    # Testing settings
    config.tracking_mode = RevenueTrackingMode.ON_DEMAND
    config.supported_platforms = {PlatformType.YOUTUBE}  # Single platform for testing
    config.security_config.require_authentication = False
    config.performance_config.max_concurrent_requests = 5
    config.compliance_config.enable_audit_trail = False
    config.alerting_config.enable_revenue_alerts = False
    
    return config
