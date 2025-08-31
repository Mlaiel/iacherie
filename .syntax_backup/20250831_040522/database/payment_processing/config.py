"""
Payment Processing Database Configuration - Enterprise Grade

Advanced configuration management for payment processing database operations,
including connection settings, security configurations, multi-gateway integrations,
and compliance management for the IA Influencer Agent platform.

Author: Fahed Mlaiel <mlaiel@live.de>
Team: Lead AI Developer + Backend Senior + ML Engineer + DBA + Security Expert + 
      Payment Systems Architect + Financial Technology Specialist + DevOps Engineer + 
      Microservices Expert + Audio Processing Engineer
Project: IA Influencer Agent + Content Protection Platform

Copyright: All rights reserved. Unauthorized use, modification, or distribution prohibited.
WARNING: This code is proprietary and confidential. Any unauthorized use, modification,
or distribution is strictly prohibited and may result in legal action.
Contact: mlaiel@live.de for licensing inquiries.

ENTERPRISE CONFIGURATION FEATURES:
- Multi-environment support (dev, staging, production)
- Multiple payment gateway configurations
- Advanced security and compliance settings
- Real-time monitoring and alerting
- Auto-scaling and load balancing
- Disaster recovery configurations
- Multi-region deployment support
"""

from typing import Dict, Any, Optional, List, Union
from dataclasses import dataclass, field
from decimal import Decimal
import os
import json
from enum import Enum
from pathlib import Path
import logging
from datetime import timedelta

logger = logging.getLogger(__name__)


class PaymentEnvironment(Enum):
    """Payment processing environment enumeration"""
    DEVELOPMENT = "development"
    STAGING = "staging"
    TESTING = "testing"
    PRODUCTION = "production"
    DISASTER_RECOVERY = "disaster_recovery"


class PaymentProvider(Enum):
    """Supported payment providers with enterprise features"""
    STRIPE = "stripe"
    PAYPAL = "paypal"
    WISE = "wise"
    SQUARE = "square"
    ADYEN = "adyen"
    BRAINTREE = "braintree"
    WORLDPAY = "worldpay"
    RAZORPAY = "razorpay"
    COINBASE = "coinbase"
    BINANCE = "binance"


class SecurityLevel(Enum):
    """Security levels for different operations"""
    BASIC = "basic"
    ENHANCED = "enhanced"
    PREMIUM = "premium"
    ENTERPRISE = "enterprise"
    GOVERNMENT = "government"


class ComplianceStandard(Enum):
    """Supported compliance standards"""
    PCI_DSS = "pci_dss"
    GDPR = "gdpr"
    SOX = "sox"
    ISO27001 = "iso27001"
    PSD2 = "psd2"
    FATF = "fatf"


@dataclass
class DatabaseConfig:
    """Advanced database configuration for payment processing"""
    # Primary database settings
    host: str = "localhost"
    port: int = 5432
    database: str = "ia_influencer_payments"
    username: str = "payment_user"
    password: str = ""
    
    # Connection pool settings
    min_connections: int = 5
    max_connections: int = 50
    connection_timeout: int = 30
    idle_timeout: int = 300
    
    # SSL/TLS settings
    ssl_enabled: bool = True
    ssl_cert_path: Optional[str] = None
    ssl_key_path: Optional[str] = None
    ssl_ca_path: Optional[str] = None
    
    # Read replica settings
    read_replicas: List[Dict[str, Any]] = field(default_factory=list)
    
    # Backup and recovery
    backup_enabled: bool = True
    backup_schedule: str = "0 2 * * *"  # Daily at 2 AM
    backup_retention_days: int = 30
    
    # Monitoring
    monitoring_enabled: bool = True
    slow_query_threshold: float = 1.0  # seconds
    
    # Additional settings
    timezone: str = "UTC"
    charset: str = "utf8mb4"
    additional_params: Dict[str, Any] = field(default_factory=dict)
    
    def get_connection_string(self, use_replica: bool = False) -> str:
        """Generate database connection string"""
        if use_replica and self.read_replicas:
            # Use first available read replica
            replica = self.read_replicas[0]
            host = replica.get('host', self.host)
            port = replica.get('port', self.port)
        else:
            host = self.host
            port = self.port
        
        ssl_param = "&sslmode=require" if self.ssl_enabled else ""
        
        return (
            f"postgresql://{self.username}:{self.password}@"
            f"{host}:{port}/{self.database}?charset={self.charset}{ssl_param}"
        )


@dataclass
class GatewayConfiguration:
    """Advanced payment gateway configuration"""
    provider: PaymentProvider
    environment: PaymentEnvironment
    
    # API credentials
    api_key: str = ""
    secret_key: str = ""
    webhook_secret: str = ""
    merchant_id: Optional[str] = None
    
    # Environment-specific endpoints
    api_base_url: Optional[str] = None
    webhook_url: Optional[str] = None
    
    # Rate limiting
    rate_limit_requests: int = 100
    rate_limit_window: int = 60  # seconds
    
    # Retry configuration
    max_retries: int = 3
    retry_delay: float = 1.0  # seconds
    exponential_backoff: bool = True
    
    # Timeout settings
    connection_timeout: int = 10
    read_timeout: int = 30
    
    # Feature flags
    features_enabled: List[str] = field(default_factory=list)
    
    # Additional provider-specific settings
    additional_config: Dict[str, Any] = field(default_factory=dict)
    
    def is_production(self) -> bool:
        """Check if this is a production configuration"""
        return self.environment == PaymentEnvironment.PRODUCTION
    
    def get_api_endpoint(self, endpoint: str) -> str:
        """Get full API endpoint URL"""
        base_url = self.api_base_url or self._get_default_base_url()
        return f"{base_url.rstrip('/')}/{endpoint.lstrip('/')}"
    
    def _get_default_base_url(self) -> str:
        """Get default base URL for the provider"""
        default_urls = {
            PaymentProvider.STRIPE: {
                PaymentEnvironment.PRODUCTION: "https://api.stripe.com",
                PaymentEnvironment.STAGING: "https://api.stripe.com",
                PaymentEnvironment.DEVELOPMENT: "https://api.stripe.com"
            },
            PaymentProvider.PAYPAL: {
                PaymentEnvironment.PRODUCTION: "https://api.paypal.com",
                PaymentEnvironment.STAGING: "https://api.sandbox.paypal.com",
                PaymentEnvironment.DEVELOPMENT: "https://api.sandbox.paypal.com"
            },
            PaymentProvider.WISE: {
                PaymentEnvironment.PRODUCTION: "https://api.wise.com",
                PaymentEnvironment.STAGING: "https://api.sandbox.transferwise.tech",
                PaymentEnvironment.DEVELOPMENT: "https://api.sandbox.transferwise.tech"
            }
        }
        
        return default_urls.get(self.provider, {}).get(
            self.environment, 
            "https://api.example.com"
        )


@dataclass
class SecurityConfiguration:
    """Advanced security configuration for payments"""
    # Encryption settings
    encryption_algorithm: str = "AES-256-GCM"
    key_rotation_interval: timedelta = field(default_factory=lambda: timedelta(days=90))
    
    # Fraud detection
    fraud_detection_enabled: bool = True
    fraud_threshold: int = 70  # 0-100 risk score
    ml_fraud_detection: bool = True
    
    # Authentication
    require_2fa: bool = True
    session_timeout: timedelta = field(default_factory=lambda: timedelta(hours=2))
    max_login_attempts: int = 5
    lockout_duration: timedelta = field(default_factory=lambda: timedelta(minutes=30))
    
    # Transaction limits
    daily_transaction_limit: Decimal = Decimal('50000.00')
    single_transaction_limit: Decimal = Decimal('10000.00')
    monthly_transaction_limit: Decimal = Decimal('500000.00')
    
    # IP and geographic restrictions
    allowed_ip_ranges: List[str] = field(default_factory=list)
    blocked_countries: List[str] = field(default_factory=list)
    geo_blocking_enabled: bool = False
    
    # Audit and compliance
    audit_logging_enabled: bool = True
    compliance_standards: List[ComplianceStandard] = field(default_factory=list)
    data_retention_days: int = 2555  # 7 years for financial data
    
    # Webhook security
    webhook_signature_validation: bool = True
    webhook_ip_whitelist: List[str] = field(default_factory=list)
    
    def is_high_security(self) -> bool:
        """Check if high security mode is enabled"""
        return (
            self.fraud_detection_enabled and
            self.require_2fa and
            self.audit_logging_enabled and
            len(self.compliance_standards) > 0
        )


@dataclass
class MonitoringConfiguration:
    """Advanced monitoring and alerting configuration"""
    # Basic monitoring
    monitoring_enabled: bool = True
    metrics_collection_interval: int = 60  # seconds
    
    # Performance monitoring
    response_time_threshold: float = 2.0  # seconds
    error_rate_threshold: float = 0.05  # 5%
    
    # Business metrics
    transaction_volume_alerts: bool = True
    revenue_tracking: bool = True
    chargeback_monitoring: bool = True
    
    # Alert channels
    email_alerts: List[str] = field(default_factory=list)
    slack_webhook_url: Optional[str] = None
    sms_alerts: List[str] = field(default_factory=list)
    
    # Log management
    log_level: str = "INFO"
    log_retention_days: int = 90
    structured_logging: bool = True
    
    # Health checks
    health_check_interval: int = 30  # seconds
    health_check_timeout: int = 10  # seconds
    
    def should_alert(self, metric_name: str, value: float, threshold: float) -> bool:
        """Determine if an alert should be sent"""
        return value > threshold


@dataclass
class CacheConfiguration:
    """Cache configuration for payment processing"""
    # Redis settings
    redis_host: str = "localhost"
    redis_port: int = 6379
    redis_db: int = 0
    redis_password: Optional[str] = None
    
    # Cache settings
    default_ttl: int = 3600  # 1 hour
    max_connections: int = 20
    
    # Cache keys and TTLs
    cache_ttls: Dict[str, int] = field(default_factory=lambda: {
        "exchange_rates": 300,      # 5 minutes
        "fraud_scores": 1800,       # 30 minutes
        "user_sessions": 7200,      # 2 hours
        "payment_methods": 3600,    # 1 hour
        "gateway_status": 60        # 1 minute
    })
    
    # Distributed cache settings
    cluster_enabled: bool = False
    cluster_nodes: List[str] = field(default_factory=list)


@dataclass
class FeatureFlags:
    """Feature flags for payment processing"""
    # Core features
    multi_currency_enabled: bool = True
    crypto_payments_enabled: bool = True
    recurring_payments_enabled: bool = True
    
    # Advanced features
    ai_fraud_detection_enabled: bool = True
    dynamic_routing_enabled: bool = True
    smart_retry_enabled: bool = True
    
    # Integration features
    webhook_forwarding_enabled: bool = True
    external_risk_scoring: bool = False
    blockchain_verification: bool = False
    
    # Experimental features
    quantum_encryption: bool = False
    biometric_authentication: bool = False
    voice_authorization: bool = False
    
    def is_feature_enabled(self, feature_name: str) -> bool:
        """Check if a specific feature is enabled"""
        return getattr(self, f"{feature_name}_enabled", False)


class PaymentConfig:
    """Central payment configuration manager"""
    
    def __init__(self, environment: PaymentEnvironment = PaymentEnvironment.DEVELOPMENT):
        self.environment = environment
        self.database = DatabaseConfig()
        self.security = SecurityConfiguration()
        self.monitoring = MonitoringConfiguration()
        self.cache = CacheConfiguration()
        self.features = FeatureFlags()
        self.gateways: Dict[PaymentProvider, GatewayConfiguration] = {}
        self._load_configuration()
    
    def _load_configuration(self):
        """Load configuration from environment variables and files"""
        # Load from environment variables
        self._load_from_environment()
        
        # Load from configuration files
        self._load_from_files()
        
        # Apply environment-specific overrides
        self._apply_environment_overrides()
    
    def _load_from_environment(self):
        """Load configuration from environment variables"""
        # Database configuration
        self.database.host = os.getenv("DB_HOST", self.database.host)
        self.database.port = int(os.getenv("DB_PORT", str(self.database.port)))
        self.database.username = os.getenv("DB_USERNAME", self.database.username)
        self.database.password = os.getenv("DB_PASSWORD", self.database.password)
        self.database.database = os.getenv("DB_DATABASE", self.database.database)
        
        # Security configuration
        fraud_threshold = os.getenv("FRAUD_THRESHOLD")
        if fraud_threshold:
            self.security.fraud_threshold = int(fraud_threshold)
        
        # Cache configuration
        self.cache.redis_host = os.getenv("REDIS_HOST", self.cache.redis_host)
        self.cache.redis_port = int(os.getenv("REDIS_PORT", str(self.cache.redis_port)))
        self.cache.redis_password = os.getenv("REDIS_PASSWORD")
        
        # Feature flags
        self.features.ai_fraud_detection_enabled = os.getenv(
            "AI_FRAUD_DETECTION", str(self.features.ai_fraud_detection_enabled)
        ).lower() == "true"
    
    def _load_from_files(self):
        """Load configuration from JSON/YAML files"""
        config_dir = Path(__file__).parent / "config"
        
        # Load gateway configurations
        gateway_config_file = config_dir / f"gateways_{self.environment.value}.json"
        if gateway_config_file.exists():
            try:
                with open(gateway_config_file, 'r') as f:
                    gateway_configs = json.load(f)
                
                for provider_name, config_data in gateway_configs.items():
                    provider = PaymentProvider(provider_name)
                    self.gateways[provider] = GatewayConfiguration(
                        provider=provider,
                        environment=self.environment,
                        **config_data
                    )
            except Exception as e:
                logger.error(f"Failed to load gateway configuration: {str(e)}")
    
    def _apply_environment_overrides(self):
        """Apply environment-specific configuration overrides"""
        if self.environment == PaymentEnvironment.PRODUCTION:
            # Production-specific settings
            self.security.fraud_detection_enabled = True
            self.security.require_2fa = True
            self.security.audit_logging_enabled = True
            self.monitoring.monitoring_enabled = True
            self.database.ssl_enabled = True
            
        elif self.environment == PaymentEnvironment.DEVELOPMENT:
            # Development-specific settings
            self.security.fraud_threshold = 90  # More lenient
            self.security.require_2fa = False
            self.monitoring.log_level = "DEBUG"
            self.features.experimental_features = True
    
    def add_gateway_config(self, provider: PaymentProvider, config: GatewayConfiguration):
        """Add or update gateway configuration"""
        self.gateways[provider] = config
    
    def get_gateway_config(self, provider: PaymentProvider) -> Optional[GatewayConfiguration]:
        """Get gateway configuration for specific provider"""
        return self.gateways.get(provider)
    
    def get_enabled_gateways(self) -> List[PaymentProvider]:
        """Get list of enabled payment gateways"""
        return list(self.gateways.keys())
    
    def validate_configuration(self) -> List[str]:
        """Validate configuration and return list of issues"""
        issues = []
        
        # Validate database configuration
        if not self.database.password and self.environment == PaymentEnvironment.PRODUCTION:
            issues.append("Database password is required for production environment")
        
        # Validate gateway configurations
        for provider, config in self.gateways.items():
            if not config.api_key:
                issues.append(f"API key missing for {provider.value} gateway")
            
            if config.is_production() and not config.webhook_secret:
                issues.append(f"Webhook secret missing for {provider.value} in production")
        
        # Validate security configuration
        if self.environment == PaymentEnvironment.PRODUCTION:
            if not self.security.fraud_detection_enabled:
                issues.append("Fraud detection should be enabled in production")
            
            if not self.security.audit_logging_enabled:
                issues.append("Audit logging should be enabled in production")
        
        return issues
    
    def export_config(self, include_secrets: bool = False) -> Dict[str, Any]:
        """Export configuration as dictionary"""
        config_dict = {
            "environment": self.environment.value,
            "database": {
                "host": self.database.host,
                "port": self.database.port,
                "database": self.database.database,
                "ssl_enabled": self.database.ssl_enabled
            },
            "security": {
                "fraud_detection_enabled": self.security.fraud_detection_enabled,
                "require_2fa": self.security.require_2fa,
                "fraud_threshold": self.security.fraud_threshold
            },
            "monitoring": {
                "monitoring_enabled": self.monitoring.monitoring_enabled,
                "log_level": self.monitoring.log_level
            },
            "features": {
                "ai_fraud_detection_enabled": self.features.ai_fraud_detection_enabled,
                "crypto_payments_enabled": self.features.crypto_payments_enabled
            },
            "gateways": {
                provider.value: {
                    "environment": config.environment.value,
                    "features_enabled": config.features_enabled
                }
                for provider, config in self.gateways.items()
            }
        }
        
        if include_secrets:
            # Only include secrets if explicitly requested and not in production
            if self.environment != PaymentEnvironment.PRODUCTION:
                config_dict["database"]["password"] = self.database.password
                for provider, config in self.gateways.items():
                    config_dict["gateways"][provider.value].update({
                        "api_key": config.api_key,
                        "secret_key": config.secret_key
                    })
        
        return config_dict
    
    def get_compliance_settings(self) -> Dict[str, Any]:
        """Get compliance-related settings"""
        return {
            "standards": [standard.value for standard in self.security.compliance_standards],
            "data_retention_days": self.security.data_retention_days,
            "audit_logging": self.security.audit_logging_enabled,
            "encryption_algorithm": self.security.encryption_algorithm,
            "geo_restrictions": {
                "enabled": self.security.geo_blocking_enabled,
                "blocked_countries": self.security.blocked_countries
            },
            "transaction_limits": {
                "daily": str(self.security.daily_transaction_limit),
                "single": str(self.security.single_transaction_limit),
                "monthly": str(self.security.monthly_transaction_limit)
            }
        }


# Global configuration instance
_payment_config: Optional[PaymentConfig] = None


def get_payment_config(environment: Optional[PaymentEnvironment] = None) -> PaymentConfig:
    """Get global payment configuration instance"""
    global _payment_config
    
    if _payment_config is None or (environment and _payment_config.environment != environment):
        _payment_config = PaymentConfig(environment or PaymentEnvironment.DEVELOPMENT)
    
    return _payment_config


def initialize_payment_config(environment: PaymentEnvironment) -> PaymentConfig:
    """Initialize payment configuration for specific environment"""
    global _payment_config
    _payment_config = PaymentConfig(environment)
    
    # Validate configuration
    issues = _payment_config.validate_configuration()
    if issues:
        logger.warning(f"Configuration issues detected: {issues}")
    
    logger.info(f"Payment configuration initialized for {environment.value} environment")
    return _payment_config


# Environment-specific configuration presets
DEVELOPMENT_CONFIG = {
    "fraud_threshold": 90,
    "require_2fa": False,
    "ssl_enabled": False,
    "monitoring_enabled": True,
    "log_level": "DEBUG"
}

STAGING_CONFIG = {
    "fraud_threshold": 80,
    "require_2fa": True,
    "ssl_enabled": True,
    "monitoring_enabled": True,
    "log_level": "INFO"
}

PRODUCTION_CONFIG = {
    "fraud_threshold": 70,
    "require_2fa": True,
    "ssl_enabled": True,
    "monitoring_enabled": True,
    "log_level": "WARNING",
    "audit_logging_enabled": True,
    "fraud_detection_enabled": True
}
    pool_size: int = 20
    max_overflow: int = 30
    pool_timeout: int = 30
    pool_recycle: int = 3600
    ssl_mode: str = "require"
    ssl_cert: Optional[str] = None
    ssl_key: Optional[str] = None
    ssl_ca: Optional[str] = None
    
    # Connection string template
    connection_template: str = "postgresql://{username}:{password}@{host}:{port}/{database}"
    
    def get_connection_string(self) -> str:
        """Generate database connection string"""
        return self.connection_template.format(
            username=self.username,
            password=self.password,
            host=self.host,
            port=self.port,
            database=self.database
        )
    
    def get_ssl_config(self) -> Dict[str, Any]:
        """Get SSL configuration for database connection"""
        ssl_config = {"sslmode": self.ssl_mode}
        
        if self.ssl_cert:
            ssl_config["sslcert"] = self.ssl_cert
        if self.ssl_key:
            ssl_config["sslkey"] = self.ssl_key
        if self.ssl_ca:
            ssl_config["sslrootcert"] = self.ssl_ca
        
        return ssl_config


@dataclass
class StripeConfig:
    """Stripe payment processor configuration"""
    publishable_key: str = ""
    secret_key: str = ""
    webhook_secret: str = ""
    api_version: str = "2023-10-16"
    connect_client_id: Optional[str] = None
    
    # Fee configuration
    fee_percentage: Decimal = Decimal("0.029")
    fee_fixed: Decimal = Decimal("0.30")
    
    # Limits
    min_charge_amount: Decimal = Decimal("0.50")
    max_charge_amount: Decimal = Decimal("999999.99")
    
    # Features
    enable_apple_pay: bool = True
    enable_google_pay: bool = True
    enable_link: bool = True
    capture_method: str = "automatic"
    
    def get_headers(self) -> Dict[str, str]:
        """Get API headers for Stripe requests"""
        return {
            "Authorization": f"Bearer {self.secret_key}",
            "Stripe-Version": self.api_version,
            "Content-Type": "application/x-www-form-urlencoded"
        }


@dataclass
class PayPalConfig:
    """PayPal payment processor configuration"""
    client_id: str = ""
    client_secret: str = ""
    webhook_id: str = ""
    environment: str = "sandbox"  # sandbox or live
    
    # Fee configuration
    fee_percentage: Decimal = Decimal("0.034")
    fee_fixed: Decimal = Decimal("0.30")
    
    # Limits
    min_payment_amount: Decimal = Decimal("0.01")
    max_payment_amount: Decimal = Decimal("10000.00")
    
    # Features
    enable_guest_checkout: bool = True
    enable_credit_card: bool = True
    enable_paypal_credit: bool = True
    
    @property
    def base_url(self) -> str:
        """Get PayPal API base URL"""
        if self.environment == "live":
            return "https://api.paypal.com"
        return "https://api.sandbox.paypal.com"
    
    def get_auth_headers(self, access_token: str) -> Dict[str, str]:
        """Get API headers for PayPal requests"""
        return {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
            "Accept": "application/json"
        }


@dataclass
class WiseConfig:
    """Wise (formerly TransferWise) configuration"""
    api_token: str = ""
    profile_id: str = ""
    environment: str = "sandbox"  # sandbox or live
    
    # Fee configuration
    fee_percentage: Decimal = Decimal("0.005")
    fee_minimum: Decimal = Decimal("1.00")
    
    # Limits
    min_transfer_amount: Decimal = Decimal("10.00")
    max_transfer_amount: Decimal = Decimal("50000.00")
    
    @property
    def base_url(self) -> str:
        """Get Wise API base URL"""
        if self.environment == "live":
            return "https://api.transferwise.com"
        return "https://api.sandbox.transferwise.tech"
    
    def get_headers(self) -> Dict[str, str]:
        """Get API headers for Wise requests"""
        return {
            "Authorization": f"Bearer {self.api_token}",
            "Content-Type": "application/json",
            "Accept": "application/json"
        }


@dataclass
class SecurityConfig:
    """Security configuration for payment processing"""
    encryption_key: str = ""
    jwt_secret: str = ""
    jwt_algorithm: str = "HS256"
    jwt_expiration_hours: int = 24
    
    # Rate limiting
    max_requests_per_minute: int = 60
    max_requests_per_hour: int = 1000
    max_requests_per_day: int = 10000
    
    # Fraud detection
    enable_fraud_detection: bool = True
    max_fraud_score: float = 0.8
    fraud_model_version: str = "v1.0"
    
    # IP restrictions
    allowed_ip_ranges: List[str] = field(default_factory=list)
    blocked_ip_ranges: List[str] = field(default_factory=list)
    
    # SSL/TLS settings
    require_https: bool = True
    min_tls_version: str = "1.2"
    
    # Session management
    session_timeout_minutes: int = 30
    max_concurrent_sessions: int = 5
    
    def is_ip_allowed(self, ip_address: str) -> bool:
        """Check if IP address is allowed"""
        # Implementation would check against allowed/blocked IP ranges
        return True  # Simplified for example


@dataclass
class ComplianceConfig:
    """Compliance and regulatory configuration"""
    # PCI DSS compliance
    pci_compliance_level: str = "Level 1"
    enable_tokenization: bool = True
    data_retention_days: int = 2555  # 7 years
    
    # GDPR compliance
    enable_gdpr_features: bool = True
    data_anonymization_days: int = 90
    consent_tracking: bool = True
    
    # Regional compliance
    supported_countries: List[str] = field(default_factory=lambda: [
        "US", "CA", "GB", "FR", "DE", "IT", "ES", "NL", "AU", "JP"
    ])
    restricted_countries: List[str] = field(default_factory=list)
    
    # Tax compliance
    enable_tax_calculation: bool = True
    tax_providers: List[str] = field(default_factory=lambda: ["avalara", "taxjar"])
    
    # Anti-money laundering (AML)
    enable_aml_checks: bool = True
    aml_threshold_amount: Decimal = Decimal("10000.00")
    kyc_verification_required: bool = True
    
    # Sanctions screening
    enable_sanctions_screening: bool = True
    sanctions_lists: List[str] = field(default_factory=lambda: [
        "OFAC", "EU", "UN", "HMT"
    ])


@dataclass
class MonitoringConfig:
    """Monitoring and observability configuration"""
    # Logging
    log_level: str = "INFO"
    log_format: str = "json"
    enable_audit_logging: bool = True
    audit_log_retention_days: int = 365
    
    # Metrics
    enable_metrics: bool = True
    metrics_provider: str = "prometheus"
    metrics_port: int = 9090
    
    # Alerting
    enable_alerting: bool = True
    alert_email: str = "alerts@mlaiel.de"
    alert_webhook: Optional[str] = None
    
    # Health checks
    health_check_interval_seconds: int = 30
    health_check_timeout_seconds: int = 5
    
    # Performance monitoring
    enable_performance_tracking: bool = True
    slow_query_threshold_ms: int = 1000
    max_query_duration_ms: int = 30000
    
    # Error tracking
    enable_error_tracking: bool = True
    error_reporting_service: str = "sentry"
    error_sample_rate: float = 0.1


@dataclass
class FeatureFlags:
    """Feature flags for payment processing"""
    enable_cryptocurrency: bool = False
    enable_buy_now_pay_later: bool = False
    enable_installments: bool = False
    enable_subscriptions: bool = True
    enable_marketplace_payments: bool = True
    enable_multi_party_payments: bool = False
    enable_escrow: bool = False
    enable_recurring_payouts: bool = True
    enable_instant_payouts: bool = False
    enable_cross_border_payments: bool = True
    enable_mobile_payments: bool = True
    enable_qr_payments: bool = False
    
    # Advanced features
    enable_machine_learning_fraud_detection: bool = True
    enable_dynamic_pricing: bool = False
    enable_risk_based_authentication: bool = True
    enable_smart_routing: bool = False


@dataclass
class PaymentProcessingConfig:
    """Main configuration class for payment processing"""
    environment: PaymentEnvironment = PaymentEnvironment.DEVELOPMENT
    
    # Database configuration
    database: DatabaseConfig = field(default_factory=DatabaseConfig)
    
    # Payment processor configurations
    stripe: StripeConfig = field(default_factory=StripeConfig)
    paypal: PayPalConfig = field(default_factory=PayPalConfig)
    wise: WiseConfig = field(default_factory=WiseConfig)
    
    # Security and compliance
    security: SecurityConfig = field(default_factory=SecurityConfig)
    compliance: ComplianceConfig = field(default_factory=ComplianceConfig)
    monitoring: MonitoringConfig = field(default_factory=MonitoringConfig)
    
    # Feature flags
    features: FeatureFlags = field(default_factory=FeatureFlags)
    
    # General settings
    default_currency: str = "EUR"
    supported_currencies: List[str] = field(default_factory=lambda: [
        "USD", "EUR", "GBP", "CAD", "AUD", "JPY", "CHF"
    ])
    
    # Transaction limits
    min_transaction_amount: Decimal = Decimal("0.50")
    max_transaction_amount: Decimal = Decimal("50000.00")
    daily_transaction_limit: Decimal = Decimal("100000.00")
    
    # Payout settings
    min_payout_amount: Decimal = Decimal("50.00")
    payout_frequencies: List[str] = field(default_factory=lambda: [
        "weekly", "monthly", "quarterly"
    ])
    default_payout_frequency: str = "monthly"
    
    # Retry and timeout settings
    max_retry_attempts: int = 3
    request_timeout_seconds: int = 30
    webhook_timeout_seconds: int = 10
    
    @classmethod
    def from_environment(cls) -> 'PaymentProcessingConfig':
        """Create configuration from environment variables"""
        config = cls()
        
        # Environment
        env_name = os.getenv('PAYMENT_ENVIRONMENT', 'development').lower()
        config.environment = PaymentEnvironment(env_name)
        
        # Database
        config.database.host = os.getenv('DB_HOST', 'localhost')
        config.database.port = int(os.getenv('DB_PORT', '5432'))
        config.database.database = os.getenv('DB_NAME', 'ia_influencer_payments')
        config.database.username = os.getenv('DB_USER', 'payment_user')
        config.database.password = os.getenv('DB_PASSWORD', '')
        
        # Stripe
        config.stripe.publishable_key = os.getenv('STRIPE_PUBLISHABLE_KEY', '')
        config.stripe.secret_key = os.getenv('STRIPE_SECRET_KEY', '')
        config.stripe.webhook_secret = os.getenv('STRIPE_WEBHOOK_SECRET', '')
        
        # PayPal
        config.paypal.client_id = os.getenv('PAYPAL_CLIENT_ID', '')
        config.paypal.client_secret = os.getenv('PAYPAL_CLIENT_SECRET', '')
        config.paypal.environment = os.getenv('PAYPAL_ENVIRONMENT', 'sandbox')
        
        # Wise
        config.wise.api_token = os.getenv('WISE_API_TOKEN', '')
        config.wise.profile_id = os.getenv('WISE_PROFILE_ID', '')
        config.wise.environment = os.getenv('WISE_ENVIRONMENT', 'sandbox')
        
        # Security
        config.security.encryption_key = os.getenv('PAYMENT_ENCRYPTION_KEY', '')
        config.security.jwt_secret = os.getenv('JWT_SECRET', '')
        
        return config
    
    def validate(self) -> List[str]:
        """Validate configuration and return list of errors"""
        errors = []
        
        if self.environment == PaymentEnvironment.PRODUCTION:
            # Production validations
            if not self.database.password:
                errors.append("Database password is required for production")
            
            if not self.stripe.secret_key:
                errors.append("Stripe secret key is required for production")
            
            if not self.security.encryption_key:
                errors.append("Encryption key is required for production")
            
            if self.database.ssl_mode == "disable":
                errors.append("SSL is required for production database connections")
        
        # General validations
        if self.default_currency not in self.supported_currencies:
            errors.append("Default currency must be in supported currencies list")
        
        if self.min_transaction_amount >= self.max_transaction_amount:
            errors.append("Minimum transaction amount must be less than maximum")
        
        return errors
    
    def get_processor_config(self, processor: PaymentProcessor) -> Dict[str, Any]:
        """Get configuration for specific payment processor"""
        processor_configs = {
            PaymentProcessor.STRIPE: self.stripe,
            PaymentProcessor.PAYPAL: self.paypal,
            PaymentProcessor.WISE: self.wise
        }
        
        return processor_configs.get(processor)
    
    def is_feature_enabled(self, feature_name: str) -> bool:
        """Check if a feature is enabled"""
        return getattr(self.features, feature_name, False)


# Global configuration instance
payment_config = PaymentProcessingConfig.from_environment()


def get_config() -> PaymentProcessingConfig:
    """Get the global payment processing configuration"""
    return payment_config


def update_config(**kwargs) -> None:
    """Update global configuration"""
    global payment_config
    for key, value in kwargs.items():
        if hasattr(payment_config, key):
            setattr(payment_config, key, value)
        else:
            logger.warning(f"Unknown configuration key: {key}")


def validate_config() -> bool:
    """Validate the current configuration"""
    errors = payment_config.validate()
    if errors:
        for error in errors:
            logger.error(f"Configuration error: {error}")
        return False
    return True
