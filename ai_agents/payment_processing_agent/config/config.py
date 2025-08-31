"""Payment Processing Configuration - Industrial Configuration Management

Centralized configuration management for payment processing, provider settings,
security parameters, and system-wide payment policies.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️  CRITICAL LEGAL NOTICE:
This code and architectural design are the exclusive intellectual property of Fahed Mlaiel.
Unauthorized use, copying, distribution, or commercialization is strictly prohibited.
Contact: mlaiel@live.de for licensing inquiries.
"""
from datetime import timedelta
from decimal import Decimal
from typing import Dict, List, Optional, Any, Union
import os
from dataclasses import dataclass, field
from pydantic import BaseSettings, validator
from pydantic.types import SecretStr


@dataclass
class ProviderConfig:
    """Configuration for a single payment provider."""    api_key: str
    api_secret: Optional[str] = None
    webhook_secret: Optional[str] = None
    environment: str = "production"  # sandbox, production
    currency: str = "EUR"
    supported_currencies: List[str] = field(default_factory=lambda: ["EUR", "USD", "GBP"])
    fee_rate: float = 2.9  # Percentage
    fixed_fee: float = 0.30  # Fixed fee per transaction
    
    # Provider-specific settings
    extra_settings: Dict[str, Any] = field(default_factory=dict)


class PaymentConfig(BaseSettings):
    """    Comprehensive payment configuration management.
    
    Centralizes all payment-related configuration including provider settings,
    fees, limits, security parameters, and compliance requirements.
    """    
    # Database and core settings
    database_url: str = "postgresql://payment_user:payment_pass@localhost/payment_db"
    redis_url: str = "redis://localhost:6379/0"
    
    # Default currency and regional settings
    default_currency: str = "EUR"
    supported_currencies: List[str] = ["EUR", "USD", "GBP", "CHF", "SEK", "NOK", "DKK"]
    
    # Platform fees and limits
    platform_fee_rate: float = 5.0  # Percentage
    minimum_fee: float = 0.50  # Minimum fee per transaction
    minimum_payout: Decimal = Decimal("10.00")
    maximum_payout: Decimal = Decimal("100000.00")
    auto_payout_threshold: Decimal = Decimal("100.00")
    
    # Payout scheduling
    payout_schedule: str = "weekly"  # daily, weekly, biweekly, monthly
    payout_processing_days: List[int] = [1, 3, 5]  # Monday, Wednesday, Friday
    payout_cutoff_hour: int = 12  # 12:00 UTC
    
    # Security and fraud detection
    fraud_threshold: float = 0.75  # Risk score threshold
    max_daily_amount: Decimal = Decimal("10000.00")
    max_monthly_amount: Decimal = Decimal("50000.00")
    require_kyc_threshold: Decimal = Decimal("1000.00")
    
    # Rate limiting
    rate_limit_per_minute: int = 100
    rate_limit_per_hour: int = 1000
    rate_limit_per_day: int = 10000
    
    # Retry and timeout settings
    max_retries: int = 3
    retry_backoff_seconds: int = 60
    timeout_seconds: int = 30
    webhook_timeout_seconds: int = 10
    
    # Encryption and security
    encryption_key: SecretStr
    webhook_signature_tolerance: int = 300  # 5 minutes
    
    # Provider configurations
    providers: Dict[str, Dict[str, Any]] = {
        "stripe": {
            "api_key": "",
            "webhook_secret": "",
            "currency": "EUR",
            "fee_rate": 2.9,
            "fixed_fee": 0.30
        },
        "wise": {
            "api_key": "",
            "profile_id": 0,
            "currency": "EUR",
            "fee_rate": 0.5,
            "fixed_fee": 0.00
        },
        "paypal": {
            "client_id": "",
            "client_secret": "",
            "currency": "EUR",
            "fee_rate": 3.4,
            "fixed_fee": 0.35
        },
        "crypto": {
            "bitcoin_network": "mainnet",
            "ethereum_network": "mainnet",
            "fee_rate": 0.1,
            "confirmation_blocks": 6
        }
    }
    
    # Tax configuration
    tax_settings: Dict[str, Any] = {
        "default_tax_rate": 19.0,  # Germany VAT
        "withholding_countries": ["US", "CA"],
        "tax_treaty_countries": ["US", "UK", "FR", "NL", "CH"],
        "require_tax_forms": ["US", "CA"],
        "automatic_withholding": True
    }
    
    # Compliance settings
    compliance_settings: Dict[str, Any] = {
        "aml_enabled": True,
        "kyc_required": True,
        "pep_screening": True,
        "sanctions_screening": True,
        "transaction_monitoring": True,
        "suspicious_activity_threshold": 5000.00
    }
    
    # Notification settings
    notification_settings: Dict[str, Any] = {
        "email_notifications": True,
        "sms_notifications": False,
        "webhook_notifications": True,
        "slack_webhook_url": "",
        "alert_thresholds": {
            "high_fraud_score": 0.8,
            "large_transaction": 5000.00,
            "failed_payout": 3,
            "system_error": 1
        }
    }
    
    # Analytics and reporting
    analytics_settings: Dict[str, Any] = {
        "real_time_analytics": True,
        "dashboard_refresh_seconds": 30,
        "report_generation_schedule": "daily",
        "data_retention_days": 2555,  # 7 years
        "export_formats": ["pdf", "csv", "xlsx"]
    }
    
    # Environment-specific overrides
    environment: str = "production"
    debug: bool = False
    log_level: str = "INFO"
    enable_metrics: bool = True
    metrics_port: int = 8080
    
    class Config:
        env_file = ".env"
        env_prefix = "PAYMENT_"
        case_sensitive = False
        
    @validator('providers')
    def validate_providers(cls, v):
        """Validate provider configurations."""        required_fields = ["api_key", "currency", "fee_rate"]
        for provider_name, config in v.items():
            for field in required_fields:
                if field not in config or not config[field]:
                    raise ValueError(f"Provider {provider_name} missing required field: {field}")
        return v
    
    @validator('supported_currencies')
    def validate_currencies(cls, v):
        """Validate currency codes."""        valid_currencies = [
            "EUR", "USD", "GBP", "CHF", "SEK", "NOK", "DKK", 
            "CAD", "AUD", "JPY", "CNY", "INR", "BRL"
        ]
        for currency in v:
            if currency not in valid_currencies:
                raise ValueError(f"Unsupported currency: {currency}")
        return v
    
    @validator('payout_schedule')
    def validate_payout_schedule(cls, v):
        """Validate payout schedule."""        valid_schedules = ["daily", "weekly", "biweekly", "monthly"]
        if v not in valid_schedules:
            raise ValueError(f"Invalid payout schedule: {v}")
        return v
    
    def get_provider_config(self, provider_name: str) -> Optional[Dict[str, Any]]:
        """Get configuration for specific provider."""        return self.providers.get(provider_name)
    
    def is_provider_enabled(self, provider_name: str) -> bool:
        """Check if provider is enabled and configured."""        config = self.get_provider_config(provider_name)
        if not config:
            return False
        return bool(config.get("api_key"))
    
    def get_currency_config(self, currency: str) -> Dict[str, Any]:
        """Get currency-specific configuration."""        currency_configs = {
            "EUR": {
                "symbol": "€",
                "decimal_places": 2,
                "code": "978",
                "region": "Europe"
            },
            "USD": {
                "symbol": "$",
                "decimal_places": 2,
                "code": "840",
                "region": "North America"
            },
            "GBP": {
                "symbol": "£",
                "decimal_places": 2,
                "code": "826",
                "region": "United Kingdom"
            },
            "CHF": {
                "symbol": "Fr",
                "decimal_places": 2,
                "code": "756",
                "region": "Switzerland"
            }
        }
        return currency_configs.get(currency, currency_configs["EUR"])
    
    def get_fee_structure(self, provider: str, currency: str = None) -> Dict[str, float]:
        """Get fee structure for provider and currency."""        provider_config = self.get_provider_config(provider)
        if not provider_config:
            return {"rate": self.platform_fee_rate, "fixed": self.minimum_fee}
        
        return {
            "rate": provider_config.get("fee_rate", self.platform_fee_rate),
            "fixed": provider_config.get("fixed_fee", self.minimum_fee)
        }
    
    def get_payout_schedule_config(self) -> Dict[str, Any]:
        """Get payout scheduling configuration."""        schedules = {
            "daily": {"frequency_days": 1, "min_amount": self.minimum_payout},
            "weekly": {"frequency_days": 7, "min_amount": self.minimum_payout},
            "biweekly": {"frequency_days": 14, "min_amount": self.minimum_payout * 2},
            "monthly": {"frequency_days": 30, "min_amount": self.minimum_payout * 4}
        }
        
        config = schedules.get(self.payout_schedule, schedules["weekly"])
        config.update({
            "processing_days": self.payout_processing_days,
            "cutoff_hour": self.payout_cutoff_hour
        })
        
        return config
    
    def get_compliance_rules(self, country: str = "DE") -> Dict[str, Any]:
        """Get compliance rules for specific country."""        default_rules = {
            "kyc_required": self.compliance_settings["kyc_required"],
            "aml_screening": self.compliance_settings["aml_enabled"],
            "tax_withholding": country in self.tax_settings["withholding_countries"],
            "reporting_required": True,
            "transaction_limit": self.max_daily_amount
        }
        
        # Country-specific overrides
        country_rules = {
            "US": {
                "tax_forms_required": True,
                "withholding_rate": 30.0,
                "reporting_threshold": 600.00
            },
            "DE": {
                "vat_rate": 19.0,
                "income_tax_rate": 42.0,
                "withholding_rate": 5.0
            },
            "UK": {
                "vat_rate": 20.0,
                "income_tax_rate": 40.0,
                "withholding_rate": 0.0
            }
        }
        
        if country in country_rules:
            default_rules.update(country_rules[country])
            
        return default_rules
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary."""        return {
            "default_currency": self.default_currency,
            "supported_currencies": self.supported_currencies,
            "platform_fee_rate": self.platform_fee_rate,
            "minimum_payout": str(self.minimum_payout),
            "maximum_payout": str(self.maximum_payout),
            "payout_schedule": self.payout_schedule,
            "fraud_threshold": self.fraud_threshold,
            "providers": {k: {
                "currency": v.get("currency"),
                "fee_rate": v.get("fee_rate"),
                "enabled": bool(v.get("api_key"))
            } for k, v in self.providers.items()},
            "environment": self.environment,
            "debug": self.debug
        }


# Global configuration instance
_config_instance = None


def get_payment_config() -> PaymentConfig:
    """Get global payment configuration instance."""    global _config_instance
    if _config_instance is None:
        _config_instance = PaymentConfig()
    return _config_instance


def override_payment_config(config: PaymentConfig):
    """Override global configuration instance."""    global _config_instance
    _config_instance = config


# Environment-specific configurations
def get_test_config() -> PaymentConfig:
    """Get test configuration with safe defaults."""    return PaymentConfig(
        environment="test",
        debug=True,
        database_url="sqlite:///test_payments.db",
        encryption_key=SecretStr("test-encryption-key-32-characters"),
        providers={
            "stripe": {
                "api_key": "sk_test_fake_key",
                "webhook_secret": "whsec_test_secret",
                "currency": "EUR",
                "fee_rate": 2.9,
                "fixed_fee": 0.30
            }
        },
        minimum_payout=Decimal("1.00"),
        fraud_threshold=0.9,  # Higher threshold for testing
        max_daily_amount=Decimal("1000.00")
    )


def get_sandbox_config() -> PaymentConfig:
    """Get sandbox configuration for development."""    return PaymentConfig(
        environment="sandbox",
        debug=True,
        providers={
            provider: {
                **config,
                "environment": "sandbox"
            } for provider, config in PaymentConfig().providers.items()
        }
    )
