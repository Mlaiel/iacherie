"""Monetization Configuration - IA Influencer Agent + Content Protection Platform

Ultra-advanced configuration management for enterprise monetization system
including payment gateways, revenue optimization, compliance, and financial settings.

Author: Fahed Mlaiel <mlaiel@live.de>
Project: IA Influencer Agent + Content Protection Platform
Copyright: All rights reserved. Unauthorized use, modification, or distribution prohibited.

🚨 CRITICAL LEGAL WARNING:
This code and all associated intellectual property belong exclusively to Fahed Mlaiel.
Any unauthorized use, copying, modification, distribution, or commercialization 
is STRICTLY PROHIBITED and will result in immediate legal action.

Contact: mlaiel@live.de for licensing inquiries and authorization.

Expert Project Team - Fahed Mlaiel:
- Lead AI Developer & Solution Architect
- Senior Backend Engineer (Python/FastAPI/Django)
- Machine Learning Engineer (TensorFlow/PyTorch/Hugging Face)
- Database Administrator & Data Engineer (PostgreSQL/Redis/MongoDB)
- Backend Security Specialist
- Microservices Architect
- Audio Processing Engineer
- DevOps Engineer
- AI Prompt Engineer & Automation Specialist
"""
import os
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from decimal import Decimal
from enum import Enum
import yaml
import json

class CurrencyCode(str, Enum):
    """Supported currency codes"""
    USD = "USD"  # US Dollar
    EUR = "EUR"  # Euro
    GBP = "GBP"  # British Pound
    JPY = "JPY"  # Japanese Yen
    CAD = "CAD"  # Canadian Dollar
    AUD = "AUD"  # Australian Dollar
    CHF = "CHF"  # Swiss Franc
    CNY = "CNY"  # Chinese Yuan
    BTC = "BTC"  # Bitcoin
    ETH = "ETH"  # Ethereum

class PaymentGateway(str, Enum):
    """Supported payment gateways"""
    STRIPE = "stripe"
    PAYPAL = "paypal"
    SQUARE = "square"
    BRAINTREE = "braintree"
    ADYEN = "adyen"
    RAZORPAY = "razorpay"
    KLARNA = "klarna"
    COINBASE = "coinbase"
    BINANCE = "binance"

class TaxJurisdiction(str, Enum):
    """Supported tax jurisdictions"""
    US = "US"        # United States
    EU = "EU"        # European Union
    UK = "UK"        # United Kingdom
    CA = "CA"        # Canada
    AU = "AU"        # Australia
    JP = "JP"        # Japan
    SG = "SG"        # Singapore
    HK = "HK"        # Hong Kong
    CH = "CH"        # Switzerland
    DE = "DE"        # Germany
    FR = "FR"        # France

@dataclass
class PaymentGatewayConfig:
    """Payment gateway configuration"""
    enabled: bool = True
    api_key: str = ""
    secret_key: str = ""
    webhook_secret: str = ""
    environment: str = "sandbox"  # sandbox or production
    supported_currencies: List[CurrencyCode] = field(default_factory=list)
    transaction_fee_percentage: Decimal = Decimal("2.9")
    fixed_fee_amount: Decimal = Decimal("0.30")
    payout_schedule: str = "daily"  # daily, weekly, monthly

@dataclass
class RevenueOptimizationConfig:
    """Revenue optimization configuration"""
    enabled: bool = True
    ai_optimization: bool = True
    dynamic_pricing: bool = True
    market_analysis: bool = True
    competitor_tracking: bool = True
    price_testing: bool = True
    optimization_interval_hours: int = 6
    minimum_data_points: int = 100
    confidence_threshold: float = 0.85
    max_price_increase_percentage: float = 25.0
    max_price_decrease_percentage: float = 15.0

@dataclass
class TaxConfig:
    """Tax configuration"""
    enabled: bool = True
    auto_calculation: bool = True
    jurisdiction: TaxJurisdiction = TaxJurisdiction.US
    vat_rate: Decimal = Decimal("0.0")
    sales_tax_rate: Decimal = Decimal("0.0")
    digital_services_tax: bool = False
    withholding_tax_rate: Decimal = Decimal("0.0")
    tax_optimization: bool = True
    deduction_tracking: bool = True

@dataclass
class ComplianceConfig:
    """Regulatory compliance configuration"""
    enabled: bool = True
    gdpr_compliance: bool = True
    ccpa_compliance: bool = True
    pci_dss_compliance: bool = True
    kyc_verification: bool = True
    aml_screening: bool = True
    fatca_reporting: bool = False
    crs_reporting: bool = False
    audit_trail_retention_days: int = 2555  # 7 years
    data_encryption: bool = True

@dataclass
class SubscriptionConfig:
    """Subscription management configuration"""
    enabled: bool = True
    trial_period_days: int = 14
    grace_period_days: int = 3
    dunning_management: bool = True
    churn_prediction: bool = True
    usage_tracking: bool = True
    metered_billing: bool = True
    proration: bool = True
    automatic_renewal: bool = True
    cancellation_survey: bool = True

@dataclass
class AnalyticsConfig:
    """Analytics and reporting configuration"""
    enabled: bool = True
    real_time_analytics: bool = True
    predictive_analytics: bool = True
    cohort_analysis: bool = True
    ltv_calculation: bool = True
    churn_analysis: bool = True
    revenue_forecasting: bool = True
    performance_benchmarking: bool = True
    custom_dashboards: bool = True
    data_retention_days: int = 1095  # 3 years

@dataclass
class SecurityConfig:
    """Security configuration"""
    enabled: bool = True
    encryption_at_rest: bool = True
    encryption_in_transit: bool = True
    api_rate_limiting: bool = True
    fraud_detection: bool = True
    suspicious_activity_monitoring: bool = True
    multi_factor_authentication: bool = True
    role_based_access_control: bool = True
    audit_logging: bool = True
    vulnerability_scanning: bool = True

class MonetizationConfig:
    """Main monetization configuration class"""
    
    def __init__(self, config_file: Optional[str] = None):
        """Initialize configuration"""
        self.config_file = config_file or os.getenv("MONETIZATION_CONFIG_FILE", "monetization_config.yml")
        
        # Default configurations
        self.payment_gateways: Dict[PaymentGateway, PaymentGatewayConfig] = {}
        self.revenue_optimization = RevenueOptimizationConfig()
        self.tax_config = TaxConfig()
        self.compliance_config = ComplianceConfig()
        self.subscription_config = SubscriptionConfig()
        self.analytics_config = AnalyticsConfig()
        self.security_config = SecurityConfig()
        
        # Load configuration
        self._load_default_config()
        self._load_config_file()
        self._load_environment_variables()
    
    def _load_default_config(self) -> None:
        """Load default payment gateway configurations"""
        
        # Stripe configuration
        self.payment_gateways[PaymentGateway.STRIPE] = PaymentGatewayConfig(
            enabled=True,
            api_key=os.getenv("STRIPE_API_KEY", ""),
            secret_key=os.getenv("STRIPE_SECRET_KEY", ""),
            webhook_secret=os.getenv("STRIPE_WEBHOOK_SECRET", ""),
            environment=os.getenv("STRIPE_ENVIRONMENT", "sandbox"),
            supported_currencies=[
                CurrencyCode.USD, CurrencyCode.EUR, CurrencyCode.GBP,
                CurrencyCode.CAD, CurrencyCode.AUD, CurrencyCode.JPY
            ],
            transaction_fee_percentage=Decimal("2.9"),
            fixed_fee_amount=Decimal("0.30")
        )
        
        # PayPal configuration
        self.payment_gateways[PaymentGateway.PAYPAL] = PaymentGatewayConfig(
            enabled=True,
            api_key=os.getenv("PAYPAL_CLIENT_ID", ""),
            secret_key=os.getenv("PAYPAL_CLIENT_SECRET", ""),
            webhook_secret=os.getenv("PAYPAL_WEBHOOK_ID", ""),
            environment=os.getenv("PAYPAL_ENVIRONMENT", "sandbox"),
            supported_currencies=[
                CurrencyCode.USD, CurrencyCode.EUR, CurrencyCode.GBP,
                CurrencyCode.CAD, CurrencyCode.AUD, CurrencyCode.JPY
            ],
            transaction_fee_percentage=Decimal("3.49"),
            fixed_fee_amount=Decimal("0.49")
        )
        
        # Coinbase configuration for crypto
        self.payment_gateways[PaymentGateway.COINBASE] = PaymentGatewayConfig(
            enabled=False,
            api_key=os.getenv("COINBASE_API_KEY", ""),
            secret_key=os.getenv("COINBASE_API_SECRET", ""),
            webhook_secret=os.getenv("COINBASE_WEBHOOK_SECRET", ""),
            environment=os.getenv("COINBASE_ENVIRONMENT", "sandbox"),
            supported_currencies=[CurrencyCode.BTC, CurrencyCode.ETH],
            transaction_fee_percentage=Decimal("1.49"),
            fixed_fee_amount=Decimal("0.00")
        )
    
    def _load_config_file(self) -> None:
        """Load configuration from YAML file"""
        
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r') as f:
                    config_data = yaml.safe_load(f)
                
                # Update configurations from file
                if 'revenue_optimization' in config_data:
                    self._update_config_from_dict(
                        self.revenue_optimization, 
                        config_data['revenue_optimization']
                    )
                
                if 'tax_config' in config_data:
                    self._update_config_from_dict(
                        self.tax_config,
                        config_data['tax_config']
                    )
                
                # Add more config sections as needed
                
            except Exception as e:
                print(f"Warning: Could not load config file {self.config_file}: {e}")
    
    def _load_environment_variables(self) -> None:
        """Load configuration from environment variables"""
        
        # Revenue optimization
        if os.getenv("REVENUE_OPTIMIZATION_ENABLED"):
            self.revenue_optimization.enabled = os.getenv("REVENUE_OPTIMIZATION_ENABLED").lower() == "true"
        
        if os.getenv("AI_OPTIMIZATION_ENABLED"):
            self.revenue_optimization.ai_optimization = os.getenv("AI_OPTIMIZATION_ENABLED").lower() == "true"
        
        # Tax configuration
        if os.getenv("TAX_JURISDICTION"):
            self.tax_config.jurisdiction = TaxJurisdiction(os.getenv("TAX_JURISDICTION"))
        
        if os.getenv("VAT_RATE"):
            self.tax_config.vat_rate = Decimal(os.getenv("VAT_RATE"))
        
        # Security configuration
        if os.getenv("ENCRYPTION_ENABLED"):
            self.security_config.encryption_at_rest = os.getenv("ENCRYPTION_ENABLED").lower() == "true"
    
    def _update_config_from_dict(self, config_obj: Any, config_dict: Dict[str, Any]) -> None:
        """Update configuration object from dictionary"""
        
        for key, value in config_dict.items():
            if hasattr(config_obj, key):
                setattr(config_obj, key, value)
    
    def save_config(self, file_path: Optional[str] = None) -> None:
        """Save current configuration to file"""
        
        output_file = file_path or self.config_file
        
        config_data = {
            'revenue_optimization': self._dataclass_to_dict(self.revenue_optimization),
            'tax_config': self._dataclass_to_dict(self.tax_config),
            'compliance_config': self._dataclass_to_dict(self.compliance_config),
            'subscription_config': self._dataclass_to_dict(self.subscription_config),
            'analytics_config': self._dataclass_to_dict(self.analytics_config),
            'security_config': self._dataclass_to_dict(self.security_config)
        }
        
        with open(output_file, 'w') as f:
            yaml.dump(config_data, f, default_flow_style=False)
    
    def _dataclass_to_dict(self, obj: Any) -> Dict[str, Any]:
        """Convert dataclass to dictionary"""
        
        result = {}
        for key, value in obj.__dict__.items():
            if isinstance(value, Decimal):
                result[key] = float(value)
            elif isinstance(value, Enum):
                result[key] = value.value
            else:
                result[key] = value
        
        return result
    
    def get_payment_gateway_config(self, gateway: PaymentGateway) -> Optional[PaymentGatewayConfig]:
        """Get configuration for specific payment gateway"""
        return self.payment_gateways.get(gateway)
    
    def is_gateway_enabled(self, gateway: PaymentGateway) -> bool:
        """Check if payment gateway is enabled"""
        config = self.get_payment_gateway_config(gateway)
        return config is not None and config.enabled
    
    def get_supported_currencies(self) -> List[CurrencyCode]:
        """Get all supported currencies across enabled gateways"""
        
        currencies = set()
        for gateway, config in self.payment_gateways.items():
            if config.enabled:
                currencies.update(config.supported_currencies)
        
        return list(currencies)
    
    def validate_config(self) -> bool:
        """Validate configuration settings"""
        
        errors = []
        
        # Check if at least one payment gateway is enabled
        enabled_gateways = [g for g, c in self.payment_gateways.items() if c.enabled]
        if not enabled_gateways:
            errors.append("No payment gateways are enabled")
        
        # Validate tax rates
        if self.tax_config.vat_rate < 0 or self.tax_config.vat_rate > 1:
            errors.append("VAT rate must be between 0 and 1")
        
        # Validate revenue optimization settings
        if self.revenue_optimization.confidence_threshold < 0.5 or self.revenue_optimization.confidence_threshold > 1:
            errors.append("Confidence threshold must be between 0.5 and 1")
        
        if errors:
            print("Configuration validation errors:")
            for error in errors:
                print(f"  - {error}")
            return False
        
        return True

# Global configuration instance
monetization_config = MonetizationConfig()

def get_config() -> MonetizationConfig:
    """Get global monetization configuration"""
    return monetization_config

def reload_config() -> MonetizationConfig:
    """Reload configuration from files"""
    global monetization_config
    monetization_config = MonetizationConfig()
    return monetization_config
