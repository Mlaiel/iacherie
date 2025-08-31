"""
Payment Processor Configuration Module
=====================================

Professional payment processing configuration for multi-platform monetization.
Supports multiple payment gateways, cryptocurrencies, and international transfers.

Author: Fahed Mlaiel <mlaiel@live.de>
Project: IA-Influencer Agent + Content Protection Platform
Team: Lead Dev IA + Backend Senior + ML Engineer + DBA + Security + Microservices + Audio + DevOps + FinTech

Copyright Notice:
This code is the intellectual property of Fahed Mlaiel.
Any unauthorized use, reproduction, or distribution of this code
without explicit written permission from the author is strictly prohibited.

Contact: mlaiel@live.de for licensing inquiries.
"""

import os
from decimal import Decimal
from typing import Dict, List, Optional, Any, Set
from dataclasses import dataclass, field
from enum import Enum
import json


class PaymentProcessor(str, Enum):
    """Supported payment processors for global monetization."""
    STRIPE = "stripe"
    PAYPAL = "paypal"
    WISE = "wise"  # Formerly TransferWise
    ADYEN = "adyen"
    SQUARE = "square"
    BRAINTREE = "braintree"
    REVOLUT = "revolut"
    KLARNA = "klarna"
    RAZORPAY = "razorpay"  # India
    MERCADO_PAGO = "mercado_pago"  # Latin America
    ALIPAY = "alipay"  # China
    WECHAT_PAY = "wechat_pay"  # China
    PAYU = "payu"  # Eastern Europe
    MOLLIE = "mollie"  # Europe
    COINBASE = "coinbase"  # Crypto
    BINANCE_PAY = "binance_pay"  # Crypto


class PaymentMethod(str, Enum):
    """Supported payment methods across all processors."""
    CREDIT_CARD = "credit_card"
    DEBIT_CARD = "debit_card"
    BANK_TRANSFER = "bank_transfer"
    DIGITAL_WALLET = "digital_wallet"
    CRYPTO = "crypto"
    ACH = "ach"  # US
    SEPA = "sepa"  # Europe
    SWIFT = "swift"  # International
    PAYPAL_WALLET = "paypal_wallet"
    VENMO = "venmo"  # PayPal's mobile payment service
    BNPL = "bnpl"  # Buy Now Pay Later
    APPLE_PAY = "apple_pay"
    GOOGLE_PAY = "google_pay"
    SAMSUNG_PAY = "samsung_pay"
    SOFORT = "sofort"  # Germany
    IDEAL = "ideal"  # Netherlands
    GIROPAY = "giropay"  # Germany
    BANCONTACT = "bancontact"  # Belgium
    P24 = "p24"  # Poland
    BLIK = "blik"  # Poland
    PIX = "pix"  # Brazil
    UPI = "upi"  # India
    ALIPAY_WALLET = "alipay_wallet"
    WECHAT_WALLET = "wechat_wallet"
    BITCOIN = "bitcoin"
    ETHEREUM = "ethereum"
    USDC = "usdc"
    USDT = "usdt"


class ProcessorCapability(str, Enum):
    """Processor capabilities for advanced features."""
    RECURRING_PAYMENTS = "recurring_payments"
    INSTANT_PAYOUTS = "instant_payouts"
    MARKETPLACE_SPLITS = "marketplace_splits"
    FRAUD_DETECTION = "fraud_detection"
    CURRENCY_CONVERSION = "currency_conversion"
    CRYPTO_SUPPORT = "crypto_support"
    MOBILE_PAYMENTS = "mobile_payments"
    B2B_PAYMENTS = "b2b_payments"
    ESCROW_SERVICES = "escrow_services"
    SUBSCRIPTION_BILLING = "subscription_billing"


@dataclass
class FeeStructure:
    """Detailed fee structure for payment processing."""
    percentage_fee: Decimal
    fixed_fee: Decimal
    currency: str
    international_fee: Optional[Decimal] = None
    currency_conversion_fee: Optional[Decimal] = None
    minimum_fee: Optional[Decimal] = None
    maximum_fee: Optional[Decimal] = None


@dataclass
class ProcessorConfig:
    """Enhanced payment processor configuration."""
    processor: PaymentProcessor
    display_name: str
    api_key: str
    secret_key: str
    webhook_secret: str
    environment: str = "production"
    enabled: bool = True
    priority: int = 1  # Lower number = higher priority
    
    # Fee Structure by Currency
    fee_structures: Dict[str, FeeStructure] = field(default_factory=dict)
    
    # Geographic and Currency Support
    supported_countries: List[str] = field(default_factory=list)
    supported_currencies: List[str] = field(default_factory=list)
    supported_methods: List[PaymentMethod] = field(default_factory=list)
    
    # Advanced Capabilities
    capabilities: List[ProcessorCapability] = field(default_factory=list)
    
    # API Configuration
    api_version: Optional[str] = None
    api_timeout_seconds: int = 30
    max_retries: int = 3
    
    # Settlement Configuration
    settlement_delay_days: int = 2
    minimum_payout_amount: Decimal = Decimal("10.00")
    maximum_transaction_amount: Optional[Decimal] = None
    
    # Security Configuration
    requires_3ds: bool = True
    fraud_detection_enabled: bool = True
    pci_compliance_level: str = "Level 1"
    
    # Webhook Configuration
    webhook_events: List[str] = field(default_factory=list)
    webhook_retry_attempts: int = 3


@dataclass
class PaymentProcessorConfig:
    """Professional payment processor configuration with global coverage."""
    
    # Default Processor Strategy
    DEFAULT_PROCESSOR: PaymentProcessor = PaymentProcessor.STRIPE
    FALLBACK_ENABLED: bool = True
    
    # Regional Processor Priority
    REGIONAL_PROCESSORS: Dict[str, List[PaymentProcessor]] = field(
        default_factory=lambda: {
            "EU": [PaymentProcessor.STRIPE, PaymentProcessor.ADYEN, PaymentProcessor.MOLLIE],
            "US": [PaymentProcessor.STRIPE, PaymentProcessor.SQUARE, PaymentProcessor.BRAINTREE],
            "GB": [PaymentProcessor.STRIPE, PaymentProcessor.ADYEN, PaymentProcessor.WISE],
            "DE": [PaymentProcessor.STRIPE, PaymentProcessor.ADYEN, PaymentProcessor.MOLLIE],
            "FR": [PaymentProcessor.STRIPE, PaymentProcessor.ADYEN, PaymentProcessor.MOLLIE],
            "IN": [PaymentProcessor.RAZORPAY, PaymentProcessor.STRIPE, PaymentProcessor.PAYPAL],
            "BR": [PaymentProcessor.MERCADO_PAGO, PaymentProcessor.STRIPE, PaymentProcessor.PAYPAL],
            "CN": [PaymentProcessor.ALIPAY, PaymentProcessor.WECHAT_PAY, PaymentProcessor.STRIPE],
            "PL": [PaymentProcessor.PAYU, PaymentProcessor.STRIPE, PaymentProcessor.ADYEN],
            "GLOBAL": [PaymentProcessor.PAYPAL, PaymentProcessor.WISE, PaymentProcessor.STRIPE]
        }
    )
    
    # Processor Configurations
    PROCESSORS: Dict[PaymentProcessor, ProcessorConfig] = field(
        default_factory=lambda: {
            PaymentProcessor.STRIPE: ProcessorConfig(
                processor=PaymentProcessor.STRIPE,
                display_name="Stripe",
                api_key=os.getenv("STRIPE_API_KEY", ""),
                secret_key=os.getenv("STRIPE_SECRET_KEY", ""),
                webhook_secret=os.getenv("STRIPE_WEBHOOK_SECRET", ""),
                environment=os.getenv("STRIPE_ENV", "production"),
                priority=1,
                fee_structures={
                    "EUR": FeeStructure(
                        percentage_fee=Decimal("1.4"),
                        fixed_fee=Decimal("0.25"),
                        currency="EUR",
                        international_fee=Decimal("0.5")
                    ),
                    "USD": FeeStructure(
                        percentage_fee=Decimal("2.9"),
                        fixed_fee=Decimal("0.30"),
                        currency="USD",
                        international_fee=Decimal("0.5")
                    ),
                    "GBP": FeeStructure(
                        percentage_fee=Decimal("1.4"),
                        fixed_fee=Decimal("0.20"),
                        currency="GBP",
                        international_fee=Decimal("0.5")
                    )
                },
                supported_countries=["US", "CA", "GB", "DE", "FR", "IT", "ES", "NL", "AU", "JP", "SG"],
                supported_currencies=["USD", "EUR", "GBP", "CAD", "AUD", "JPY", "CHF", "SEK", "NOK", "DKK"],
                supported_methods=[
                    PaymentMethod.CREDIT_CARD, PaymentMethod.DEBIT_CARD,
                    PaymentMethod.BANK_TRANSFER, PaymentMethod.DIGITAL_WALLET,
                    PaymentMethod.ACH, PaymentMethod.SEPA, PaymentMethod.APPLE_PAY,
                    PaymentMethod.GOOGLE_PAY, PaymentMethod.SOFORT, PaymentMethod.IDEAL,
                    PaymentMethod.GIROPAY, PaymentMethod.BANCONTACT, PaymentMethod.P24
                ],
                capabilities=[
                    ProcessorCapability.RECURRING_PAYMENTS, ProcessorCapability.INSTANT_PAYOUTS,
                    ProcessorCapability.MARKETPLACE_SPLITS, ProcessorCapability.FRAUD_DETECTION,
                    ProcessorCapability.CURRENCY_CONVERSION, ProcessorCapability.MOBILE_PAYMENTS,
                    ProcessorCapability.SUBSCRIPTION_BILLING
                ],
                api_version="2023-10-16",
                settlement_delay_days=2,
                minimum_payout_amount=Decimal("1.00"),
                webhook_events=["payment_intent.succeeded", "payout.paid", "charge.dispute.created"]
            ),
            
            PaymentProcessor.PAYPAL: ProcessorConfig(
                processor=PaymentProcessor.PAYPAL,
                display_name="PayPal",
                api_key=os.getenv("PAYPAL_CLIENT_ID", ""),
                secret_key=os.getenv("PAYPAL_CLIENT_SECRET", ""),
                webhook_secret=os.getenv("PAYPAL_WEBHOOK_ID", ""),
                environment=os.getenv("PAYPAL_ENV", "production"),
                priority=2,
                fee_structures={
                    "EUR": FeeStructure(
                        percentage_fee=Decimal("2.49"),
                        fixed_fee=Decimal("0.35"),
                        currency="EUR",
                        international_fee=Decimal("1.0"),
                        currency_conversion_fee=Decimal("2.5")
                    ),
                    "USD": FeeStructure(
                        percentage_fee=Decimal("2.89"),
                        fixed_fee=Decimal("0.49"),
                        currency="USD",
                        international_fee=Decimal("1.0")
                    )
                },
                supported_countries=["US", "CA", "GB", "DE", "FR", "IT", "ES", "NL", "AU", "JP", "IN", "BR", "MX"],
                supported_currencies=["USD", "EUR", "GBP", "CAD", "AUD", "JPY", "BRL", "MXN", "INR"],
                supported_methods=[
                    PaymentMethod.PAYPAL_WALLET, PaymentMethod.CREDIT_CARD,
                    PaymentMethod.DEBIT_CARD, PaymentMethod.BANK_TRANSFER,
                    PaymentMethod.VENMO, PaymentMethod.BNPL
                ],
                capabilities=[
                    ProcessorCapability.INSTANT_PAYOUTS, ProcessorCapability.MARKETPLACE_SPLITS,
                    ProcessorCapability.CURRENCY_CONVERSION, ProcessorCapability.MOBILE_PAYMENTS,
                    ProcessorCapability.B2B_PAYMENTS, ProcessorCapability.SUBSCRIPTION_BILLING
                ],
                settlement_delay_days=1,
                minimum_payout_amount=Decimal("1.00")
            ),
            
            PaymentProcessor.WISE: ProcessorConfig(
                processor=PaymentProcessor.WISE,
                display_name="Wise (TransferWise)",
                api_key=os.getenv("WISE_API_KEY", ""),
                secret_key=os.getenv("WISE_API_SECRET", ""),
                webhook_secret=os.getenv("WISE_WEBHOOK_SECRET", ""),
                environment=os.getenv("WISE_ENV", "production"),
                priority=3,
                fee_structures={
                    "EUR": FeeStructure(
                        percentage_fee=Decimal("0.43"),
                        fixed_fee=Decimal("0.00"),
                        currency="EUR",
                        currency_conversion_fee=Decimal("0.35")
                    ),
                    "USD": FeeStructure(
                        percentage_fee=Decimal("0.41"),
                        fixed_fee=Decimal("0.00"),
                        currency="USD",
                        currency_conversion_fee=Decimal("0.35")
                    )
                },
                supported_countries=["US", "GB", "DE", "FR", "IT", "ES", "NL", "AU", "CA", "JP", "SG", "HK", "IN", "BR", "MX", "ZA", "NZ", "CH", "NO", "SE", "DK", "FI", "PL", "CZ", "HU", "RO", "BG", "HR", "SI", "SK", "LT", "LV", "EE"],
                supported_currencies=["USD", "EUR", "GBP", "CAD", "AUD", "JPY", "CHF", "SGD", "HKD", "NZD", "NOK", "SEK", "DKK", "PLN", "CZK", "HUF", "INR", "BRL", "MXN", "ZAR", "KRW", "THB", "MYR", "IDR", "PHP", "VND", "TRY", "BGN", "HRK", "RON", "RSD", "BAM", "MKD", "ALL", "ISK", "RUB", "UAH", "GEL", "AMD", "AZN", "KZT", "KGS", "TJS", "UZS", "TMT", "MDL", "BYN", "EGP", "MAD", "TND", "KES", "UGX", "TZS", "GHS", "NGN", "XOF", "XAF", "CNY", "TWD", "AED", "SAR", "QAR", "KWD", "BHD", "OMR", "JOD", "LBP", "ILS", "PKR", "BDT", "LKR", "NPR", "BTN", "MVR", "AFN", "IRR", "IQD", "SYP", "YER", "UYU", "PYG", "BOB", "PEN", "COP", "VEF", "CLP", "ARS"],
                supported_methods=[
                    PaymentMethod.BANK_TRANSFER, PaymentMethod.SWIFT,
                    PaymentMethod.SEPA, PaymentMethod.ACH
                ],
                capabilities=[
                    ProcessorCapability.CURRENCY_CONVERSION, ProcessorCapability.B2B_PAYMENTS,
                    ProcessorCapability.INSTANT_PAYOUTS
                ],
                settlement_delay_days=1,
                minimum_payout_amount=Decimal("0.01")
            ),
            
            PaymentProcessor.SQUARE: ProcessorConfig(
                processor=PaymentProcessor.SQUARE,
                display_name="Square",
                api_key=os.getenv("SQUARE_APPLICATION_ID", ""),
                secret_key=os.getenv("SQUARE_ACCESS_TOKEN", ""),
                webhook_secret=os.getenv("SQUARE_WEBHOOK_SECRET", ""),
                environment=os.getenv("SQUARE_ENV", "production"),
                priority=4,
                fee_structures={
                    "USD": FeeStructure(
                        percentage_fee=Decimal("2.6"),
                        fixed_fee=Decimal("0.10"),
                        currency="USD",
                        international_fee=Decimal("0.5")
                    ),
                    "CAD": FeeStructure(
                        percentage_fee=Decimal("2.65"),
                        fixed_fee=Decimal("0.10"),
                        currency="CAD",
                        international_fee=Decimal("0.5")
                    ),
                    "GBP": FeeStructure(
                        percentage_fee=Decimal("1.4"),
                        fixed_fee=Decimal("0.20"),
                        currency="GBP",
                        international_fee=Decimal("0.5")
                    ),
                    "AUD": FeeStructure(
                        percentage_fee=Decimal("1.9"),
                        fixed_fee=Decimal("0.30"),
                        currency="AUD",
                        international_fee=Decimal("0.5")
                    )
                },
                supported_countries=["US", "CA", "GB", "AU", "JP"],
                supported_currencies=["USD", "CAD", "GBP", "AUD", "JPY"],
                supported_methods=[
                    PaymentMethod.CREDIT_CARD, PaymentMethod.DEBIT_CARD,
                    PaymentMethod.DIGITAL_WALLET, PaymentMethod.APPLE_PAY,
                    PaymentMethod.GOOGLE_PAY, PaymentMethod.ACH, PaymentMethod.BANK_TRANSFER
                ],
                capabilities=[
                    ProcessorCapability.RECURRING_PAYMENTS, ProcessorCapability.INSTANT_PAYOUTS,
                    ProcessorCapability.MARKETPLACE_SPLITS, ProcessorCapability.FRAUD_DETECTION,
                    ProcessorCapability.MOBILE_PAYMENTS, ProcessorCapability.B2B_PAYMENTS,
                    ProcessorCapability.SUBSCRIPTION_BILLING
                ],
                settlement_delay_days=1,
                minimum_payout_amount=Decimal("1.00"),
                webhook_events=["payment.updated", "refund.updated", "dispute.created"]
            ),
            
            PaymentProcessor.COINBASE: ProcessorConfig(
                processor=PaymentProcessor.COINBASE,
                display_name="Coinbase Commerce",
                api_key=os.getenv("COINBASE_API_KEY", ""),
                secret_key=os.getenv("COINBASE_API_SECRET", ""),
                webhook_secret=os.getenv("COINBASE_WEBHOOK_SECRET", ""),
                environment=os.getenv("COINBASE_ENV", "production"),
                priority=5,
                fee_structures={
                    "USD": FeeStructure(
                        percentage_fee=Decimal("1.0"),
                        fixed_fee=Decimal("0.00"),
                        currency="USD"
                    )
                },
                supported_countries=["US", "GB", "DE", "FR", "IT", "ES", "NL", "CA", "AU", "JP"],
                supported_currencies=["BTC", "ETH", "USDC", "USDT", "LTC", "BCH"],
                supported_methods=[
                    PaymentMethod.BITCOIN, PaymentMethod.ETHEREUM,
                    PaymentMethod.USDC, PaymentMethod.USDT, PaymentMethod.CRYPTO
                ],
                capabilities=[
                    ProcessorCapability.CRYPTO_SUPPORT, ProcessorCapability.INSTANT_PAYOUTS
                ],
                settlement_delay_days=0,
                minimum_payout_amount=Decimal("0.001")
            )
        }
    )
    
    # Global Configuration
    GLOBAL_SETTINGS: Dict[str, Any] = field(default_factory=lambda: {
        "max_concurrent_processors": 3,
        "processor_health_check_interval": 300,  # 5 minutes
        "automatic_failover": True,
        "circuit_breaker_enabled": True,
        "circuit_breaker_failure_threshold": 5,
        "circuit_breaker_recovery_timeout": 60,
        "transaction_timeout_seconds": 120,
        "webhook_signature_verification": True,
        "idempotency_enabled": True,
        "audit_all_transactions": True
    })
    
    # Security Configuration
    SECURITY_SETTINGS: Dict[str, Any] = field(default_factory=lambda: {
        "encryption_enabled": True,
        "pci_dss_compliance": True,
        "fraud_detection_enabled": True,
        "velocity_checks": True,
        "ip_whitelisting": False,
        "require_cvv": True,
        "require_billing_address": True,
        "max_failed_attempts": 3,
        "account_lockout_duration": 1800  # 30 minutes
    })
    
    # Rate Limiting
    RATE_LIMITS: Dict[str, Any] = field(default_factory=lambda: {
        "requests_per_minute": 1000,
        "requests_per_hour": 10000,
        "requests_per_day": 100000,
        "burst_limit": 50,
        "webhook_rate_limit": 100
    })
    
    def get_processor_config(self, processor: PaymentProcessor) -> Optional[ProcessorConfig]:
        """Get configuration for a specific payment processor."""
        return self.PROCESSORS.get(processor)
    
    def get_regional_processors(self, country_code: str) -> List[PaymentProcessor]:
        """Get recommended processors for a specific country/region."""
        return self.REGIONAL_PROCESSORS.get(
            country_code.upper(), 
            self.REGIONAL_PROCESSORS["GLOBAL"]
        )
    
    def get_enabled_processors(self) -> List[ProcessorConfig]:
        """Get all enabled payment processors sorted by priority."""
        enabled = [config for config in self.PROCESSORS.values() if config.enabled]
        return sorted(enabled, key=lambda x: x.priority)
    
    def supports_payment_method(self, processor: PaymentProcessor, 
                              method: PaymentMethod) -> bool:
        """Check if processor supports a specific payment method."""
        config = self.get_processor_config(processor)
        return config and method in config.supported_methods
    
    def get_processor_fee(self, processor: PaymentProcessor, 
                         currency: str, amount: Decimal) -> Decimal:
        """Calculate processor fee for a transaction."""
        config = self.get_processor_config(processor)
        if not config or currency not in config.fee_structures:
            return Decimal("0.00")
        
        fee_structure = config.fee_structures[currency]
        percentage_fee = amount * (fee_structure.percentage_fee / Decimal("100"))
        total_fee = percentage_fee + fee_structure.fixed_fee
        
        if fee_structure.minimum_fee and total_fee < fee_structure.minimum_fee:
            return fee_structure.minimum_fee
        if fee_structure.maximum_fee and total_fee > fee_structure.maximum_fee:
            return fee_structure.maximum_fee
            
        return total_fee


# Global configuration instance
payment_config = PaymentProcessorConfig()

import os
from decimal import Decimal
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, field
from enum import Enum


class PaymentProvider(str, Enum):
    """Supported payment providers."""
    STRIPE = "stripe"
    PAYPAL = "paypal"
    WISE = "wise"
    SQUARE = "square"
    BANK_TRANSFER = "bank_transfer"
    CRYPTO = "crypto"
    APPLE_PAY = "apple_pay"
    GOOGLE_PAY = "google_pay"
    AMAZON_PAY = "amazon_pay"
    KLARNA = "klarna"
    RAZORPAY = "razorpay"
    ADYEN = "adyen"
    BRAINTREE = "braintree"


class PaymentMethod(str, Enum):
    """Payment method types."""
    CREDIT_CARD = "credit_card"
    DEBIT_CARD = "debit_card"
    BANK_ACCOUNT = "bank_account"
    DIGITAL_WALLET = "digital_wallet"
    CRYPTOCURRENCY = "cryptocurrency"
    WIRE_TRANSFER = "wire_transfer"
    ACH_TRANSFER = "ach_transfer"
    SEPA_TRANSFER = "sepa_transfer"
    MOBILE_PAYMENT = "mobile_payment"
    VOUCHER = "voucher"
    PAYPAL_WALLET = "paypal_wallet"
    VENMO = "venmo"
    BNPL = "bnpl"
    APPLE_PAY = "apple_pay"
    GOOGLE_PAY = "google_pay"


class PaymentStatus(str, Enum):
    """Payment status types."""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    REFUNDED = "refunded"
    PARTIALLY_REFUNDED = "partially_refunded"
    DISPUTED = "disputed"
    ON_HOLD = "on_hold"


class PayoutFrequency(str, Enum):
    """Payout frequency options."""
    INSTANT = "instant"
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    ON_DEMAND = "on_demand"


@dataclass
class PaymentProviderConfig:
    """Configuration for a specific payment provider."""
    provider: PaymentProvider
    enabled: bool
    api_key: str
    api_secret: str
    webhook_secret: str
    environment: str  # sandbox, production
    supported_currencies: List[str]
    supported_countries: List[str]
    processing_fee_percentage: Decimal
    processing_fee_fixed: Decimal
    payout_fee_percentage: Decimal
    payout_fee_fixed: Decimal
    minimum_amount: Decimal
    maximum_amount: Decimal
    settlement_time_hours: int
    supports_refunds: bool = True
    supports_disputes: bool = True
    supports_subscriptions: bool = False
    supports_marketplace: bool = False
    priority: int = 1  # Lower number = higher priority


@dataclass
class PaymentSecurityConfig:
    """Security configuration for payments."""
    enable_3ds: bool = True
    enable_fraud_detection: bool = True
    enable_velocity_checks: bool = True
    max_failed_attempts: int = 3
    lockout_duration_minutes: int = 30
    enable_ip_whitelisting: bool = False
    enable_geoblocking: bool = False
    blocked_countries: List[str] = field(default_factory=list)
    require_cvv: bool = True
    require_address_verification: bool = True
    enable_risk_scoring: bool = True
    suspicious_activity_threshold: Decimal = Decimal("500.00")


@dataclass
class PaymentProcessorConfig:
    """Main payment processor configuration class."""
    
    # Environment Configuration
    ENVIRONMENT: str = os.getenv("PAYMENT_ENVIRONMENT", "sandbox")
    DEBUG_MODE: bool = os.getenv("PAYMENT_DEBUG", "false").lower() == "true"
    
    # Default Settings
    DEFAULT_CURRENCY: str = "EUR"
    DEFAULT_COUNTRY: str = "DE"
    
    # Payment Provider Configurations
    PAYMENT_PROVIDERS: Dict[PaymentProvider, PaymentProviderConfig] = field(
        default_factory=lambda: {
            PaymentProvider.STRIPE: PaymentProviderConfig(
                provider=PaymentProvider.STRIPE,
                enabled=True,
                api_key=os.getenv("STRIPE_API_KEY", ""),
                api_secret=os.getenv("STRIPE_API_SECRET", ""),
                webhook_secret=os.getenv("STRIPE_WEBHOOK_SECRET", ""),
                environment=os.getenv("STRIPE_ENVIRONMENT", "sandbox"),
                supported_currencies=[
                    "EUR", "USD", "GBP", "CAD", "AUD", "CHF", "SEK", "NOK", "DKK"
                ],
                supported_countries=[
                    "DE", "US", "GB", "FR", "IT", "ES", "NL", "BE", "AT", "CH"
                ],
                processing_fee_percentage=Decimal("2.9"),
                processing_fee_fixed=Decimal("0.30"),
                payout_fee_percentage=Decimal("0.0"),
                payout_fee_fixed=Decimal("0.25"),
                minimum_amount=Decimal("0.50"),
                maximum_amount=Decimal("999999.99"),
                settlement_time_hours=24,
                supports_refunds=True,
                supports_disputes=True,
                supports_subscriptions=True,
                supports_marketplace=True,
                priority=1
            ),
            PaymentProvider.PAYPAL: PaymentProviderConfig(
                provider=PaymentProvider.PAYPAL,
                enabled=True,
                api_key=os.getenv("PAYPAL_CLIENT_ID", ""),
                api_secret=os.getenv("PAYPAL_CLIENT_SECRET", ""),
                webhook_secret=os.getenv("PAYPAL_WEBHOOK_ID", ""),
                environment=os.getenv("PAYPAL_ENVIRONMENT", "sandbox"),
                supported_currencies=[
                    "EUR", "USD", "GBP", "CAD", "AUD", "JPY", "CHF"
                ],
                supported_countries=[
                    "DE", "US", "GB", "FR", "IT", "ES", "CA", "AU", "NL", "BE"
                ],
                processing_fee_percentage=Decimal("3.4"),
                processing_fee_fixed=Decimal("0.35"),
                payout_fee_percentage=Decimal("0.0"),
                payout_fee_fixed=Decimal("0.00"),
                minimum_amount=Decimal("1.00"),
                maximum_amount=Decimal("10000.00"),
                settlement_time_hours=48,
                supports_refunds=True,
                supports_disputes=True,
                supports_subscriptions=True,
                supports_marketplace=False,
                priority=2
            ),
            PaymentProvider.WISE: PaymentProviderConfig(
                provider=PaymentProvider.WISE,
                enabled=True,
                api_key=os.getenv("WISE_API_TOKEN", ""),
                api_secret="",  # Wise uses token-based auth
                webhook_secret="",
                environment=os.getenv("WISE_ENVIRONMENT", "sandbox"),
                supported_currencies=[
                    "EUR", "USD", "GBP", "CAD", "AUD", "CHF", "JPY", "CNY", "SGD", "HKD", "NZD", "NOK", "SEK", "DKK", "PLN", "CZK", "HUF", "INR", "BRL", "MXN", "ZAR", "KRW", "THB", "MYR", "IDR", "PHP", "VND", "TRY", "BGN", "HRK", "RON", "RSD", "BAM", "MKD", "ALL", "ISK", "RUB", "UAH", "GEL", "AMD", "AZN", "KZT", "KGS", "TJS", "UZS", "TMT", "MDL", "BYN", "EGP", "MAD", "TND", "KES", "UGX", "TZS", "GHS", "NGN", "XOF", "XAF", "TWD", "AED", "SAR", "QAR", "KWD", "BHD", "OMR", "JOD", "LBP", "ILS", "PKR", "BDT", "LKR", "NPR", "BTN", "MVR", "AFN", "IRR", "IQD", "SYP", "YER", "UYU", "PYG", "BOB", "PEN", "COP", "VEF", "CLP", "ARS"
                ],
                supported_countries=[
                    "DE", "US", "GB", "FR", "IT", "ES", "CA", "AU", "NL", "BE", "CH", "NO", "SE", "DK", "FI", "PL", "CZ", "HU", "RO", "BG", "HR", "SI", "SK", "LT", "LV", "EE", "IN", "BR", "MX", "ZA", "NZ", "SG", "HK", "JP", "CN", "KR", "TH", "MY", "ID", "PH", "VN", "TR", "UA", "GE", "AM", "AZ", "KZ", "KG", "TJ", "UZ", "TM", "MD", "BY", "EG", "MA", "TN", "KE", "UG", "TZ", "GH", "NG", "AE", "SA", "QA", "KW", "BH", "OM", "JO", "LB", "IL", "PK", "BD", "LK", "NP", "BT", "MV", "AF", "IR", "IQ", "SY", "YE", "UY", "PY", "BO", "PE", "CO", "VE", "CL", "AR"
                ],
                processing_fee_percentage=Decimal("0.5"),
                processing_fee_fixed=Decimal("0.50"),
                payout_fee_percentage=Decimal("0.4"),
                payout_fee_fixed=Decimal("0.40"),
                minimum_amount=Decimal("1.00"),
                maximum_amount=Decimal("1000000.00"),
                settlement_time_hours=24,
                supports_refunds=False,
                supports_disputes=False,
                supports_subscriptions=False,
                supports_marketplace=False,
                priority=3
            ),
            PaymentProvider.ADYEN: PaymentProviderConfig(
                provider=PaymentProvider.ADYEN,
                enabled=False,  # Enterprise level
                api_key=os.getenv("ADYEN_API_KEY", ""),
                api_secret=os.getenv("ADYEN_API_SECRET", ""),
                webhook_secret=os.getenv("ADYEN_WEBHOOK_SECRET", ""),
                environment=os.getenv("ADYEN_ENVIRONMENT", "test"),
                supported_currencies=[
                    "EUR", "USD", "GBP", "CAD", "AUD", "CHF", "JPY", "CNY", "BRL"
                ],
                supported_countries=[
                    "DE", "US", "GB", "FR", "IT", "ES", "CA", "AU", "NL", "BE", 
                    "CH", "BR", "JP", "CN", "IN"
                ],
                processing_fee_percentage=Decimal("2.6"),
                processing_fee_fixed=Decimal("0.28"),
                payout_fee_percentage=Decimal("0.0"),
                payout_fee_fixed=Decimal("0.20"),
                minimum_amount=Decimal("0.01"),
                maximum_amount=Decimal("9999999.99"),
                settlement_time_hours=24,
                supports_refunds=True,
                supports_disputes=True,
                supports_subscriptions=True,
                supports_marketplace=True,
                priority=4
            ),
            PaymentProvider.SQUARE: PaymentProviderConfig(
                provider=PaymentProvider.SQUARE,
                enabled=True,
                api_key=os.getenv("SQUARE_APPLICATION_ID", ""),
                api_secret=os.getenv("SQUARE_ACCESS_TOKEN", ""),
                webhook_secret=os.getenv("SQUARE_WEBHOOK_SECRET", ""),
                environment=os.getenv("SQUARE_ENVIRONMENT", "sandbox"),
                supported_currencies=[
                    "USD", "CAD", "GBP", "AUD", "JPY"
                ],
                supported_countries=[
                    "US", "CA", "GB", "AU", "JP"
                ],
                processing_fee_percentage=Decimal("2.6"),
                processing_fee_fixed=Decimal("0.10"),
                payout_fee_percentage=Decimal("0.0"),
                payout_fee_fixed=Decimal("0.25"),
                minimum_amount=Decimal("1.00"),
                maximum_amount=Decimal("50000.00"),
                settlement_time_hours=24,
                supports_refunds=True,
                supports_disputes=True,
                supports_subscriptions=True,
                supports_marketplace=True,
                priority=5
            )
        }
    )
    
    # Security Configuration
    SECURITY_CONFIG: PaymentSecurityConfig = field(default_factory=PaymentSecurityConfig)
    
    # Supported Payment Methods by Provider
    PROVIDER_PAYMENT_METHODS: Dict[PaymentProvider, List[PaymentMethod]] = field(
        default_factory=lambda: {
            PaymentProvider.STRIPE: [
                PaymentMethod.CREDIT_CARD,
                PaymentMethod.DEBIT_CARD,
                PaymentMethod.BANK_ACCOUNT,
                PaymentMethod.DIGITAL_WALLET,
                PaymentMethod.ACH_TRANSFER,
                PaymentMethod.SEPA_TRANSFER,
                PaymentMethod.APPLE_PAY,
                PaymentMethod.GOOGLE_PAY
            ],
            PaymentProvider.PAYPAL: [
                PaymentMethod.DIGITAL_WALLET,
                PaymentMethod.PAYPAL_WALLET,
                PaymentMethod.VENMO,
                PaymentMethod.BNPL,
                PaymentMethod.CREDIT_CARD,
                PaymentMethod.DEBIT_CARD,
                PaymentMethod.BANK_ACCOUNT
            ],
            PaymentProvider.WISE: [
                PaymentMethod.BANK_ACCOUNT,
                PaymentMethod.WIRE_TRANSFER,
                PaymentMethod.ACH_TRANSFER,
                PaymentMethod.SEPA_TRANSFER
            ],
            PaymentProvider.SQUARE: [
                PaymentMethod.CREDIT_CARD,
                PaymentMethod.DEBIT_CARD,
                PaymentMethod.DIGITAL_WALLET,
                PaymentMethod.APPLE_PAY,
                PaymentMethod.GOOGLE_PAY,
                PaymentMethod.ACH_TRANSFER,
                PaymentMethod.BANK_ACCOUNT,
                PaymentMethod.MOBILE_PAYMENT
            ],
            PaymentProvider.ADYEN: [
                PaymentMethod.CREDIT_CARD,
                PaymentMethod.DEBIT_CARD,
                PaymentMethod.DIGITAL_WALLET,
                PaymentMethod.BANK_ACCOUNT,
                PaymentMethod.MOBILE_PAYMENT
            ]
        }
    )
    
    # Webhook Configuration
    WEBHOOK_SETTINGS: Dict[str, Any] = field(default_factory=lambda: {
        "enable_webhooks": True,
        "webhook_timeout_seconds": 10,
        "max_retry_attempts": 3,
        "verify_webhook_signatures": True,
        "log_webhook_events": True,
        "webhook_endpoints": {
            "payment_success": "/api/v1/webhooks/payment/success",
            "payment_failed": "/api/v1/webhooks/payment/failed",
            "refund_processed": "/api/v1/webhooks/payment/refund",
            "dispute_created": "/api/v1/webhooks/payment/dispute",
            "payout_completed": "/api/v1/webhooks/payment/payout"
        }
    })
    
    # Payout Configuration
    PAYOUT_SETTINGS: Dict[str, Any] = field(default_factory=lambda: {
        "default_frequency": PayoutFrequency.WEEKLY,
        "minimum_payout_amount": Decimal("25.00"),
        "maximum_payout_amount": Decimal("100000.00"),
        "automatic_payouts": True,
        "payout_schedule_day": "friday",  # For weekly payouts
        "payout_schedule_date": 1,  # For monthly payouts
        "hold_period_days": 7,  # Anti-fraud hold period
        "require_bank_verification": True,
        "enable_instant_payouts": False,  # Premium feature
        "instant_payout_fee": Decimal("1.5")  # Percentage
    })
    
    # Currency Configuration
    CURRENCY_SETTINGS: Dict[str, Any] = field(default_factory=lambda: {
        "auto_currency_conversion": True,
        "conversion_spread": Decimal("0.5"),  # Our markup on exchange rates
        "settlement_currency_priority": ["EUR", "USD", "GBP"],
        "supported_cryptocurrencies": ["BTC", "ETH", "USDC", "USDT"],
        "crypto_conversion_enabled": False,
        "minimum_crypto_amount": Decimal("10.00")
    })
    
    # Compliance and Regulation
    COMPLIANCE_SETTINGS: Dict[str, Any] = field(default_factory=lambda: {
        "kyc_required": True,
        "kyc_verification_level": "full",  # basic, enhanced, full
        "aml_screening": True,
        "pci_compliance": True,
        "gdpr_compliance": True,
        "psd2_compliance": True,  # EU regulation
        "ofac_screening": True,  # US sanctions
        "transaction_reporting_threshold": Decimal("10000.00"),
        "suspicious_activity_reporting": True
    })
    
    # Rate Limiting and Performance
    PERFORMANCE_SETTINGS: Dict[str, Any] = field(default_factory=lambda: {
        "api_rate_limit_per_minute": 100,
        "burst_rate_limit": 200,
        "connection_timeout_seconds": 30,
        "read_timeout_seconds": 60,
        "max_concurrent_requests": 20,
        "circuit_breaker_enabled": True,
        "circuit_breaker_failure_threshold": 5,
        "cache_payment_methods": True,
        "cache_ttl_seconds": 3600
    })
    
    # Monitoring and Logging
    MONITORING_SETTINGS: Dict[str, Any] = field(default_factory=lambda: {
        "log_all_transactions": True,
        "log_sensitive_data": False,
        "enable_metrics": True,
        "metrics_retention_days": 90,
        "alert_on_high_failure_rate": True,
        "failure_rate_threshold": Decimal("5.0"),  # Percentage
        "alert_on_unusual_activity": True,
        "daily_reconciliation": True,
        "monthly_settlement_reports": True
    })
    
    def get_provider_config(self, provider: PaymentProvider) -> Optional[PaymentProviderConfig]:
        """Get configuration for a specific payment provider."""
        return self.PAYMENT_PROVIDERS.get(provider)
    
    def get_enabled_providers(self) -> List[PaymentProvider]:
        """Get list of enabled payment providers."""
        return [
            provider for provider, config in self.PAYMENT_PROVIDERS.items() 
            if config.enabled
        ]
    
    def get_primary_provider(self) -> Optional[PaymentProvider]:
        """Get the primary (highest priority) enabled provider."""
        enabled_providers = [
            (provider, config) for provider, config in self.PAYMENT_PROVIDERS.items() 
            if config.enabled
        ]
        if not enabled_providers:
            return None
        
        return min(enabled_providers, key=lambda x: x[1].priority)[0]
    
    def get_supported_methods(self, provider: PaymentProvider) -> List[PaymentMethod]:
        """Get supported payment methods for a provider."""
        return self.PROVIDER_PAYMENT_METHODS.get(provider, [])
    
    def calculate_processing_fee(
        self, 
        provider: PaymentProvider, 
        amount: Decimal
    ) -> Decimal:
        """Calculate processing fee for a transaction."""
        config = self.get_provider_config(provider)
        if not config:
            return Decimal("0.00")
        
        percentage_fee = amount * (config.processing_fee_percentage / Decimal("100"))
        total_fee = percentage_fee + config.processing_fee_fixed
        return total_fee.quantize(Decimal("0.01"))
    
    def calculate_payout_fee(
        self, 
        provider: PaymentProvider, 
        amount: Decimal
    ) -> Decimal:
        """Calculate payout fee for a transaction."""
        config = self.get_provider_config(provider)
        if not config:
            return Decimal("0.00")
        
        percentage_fee = amount * (config.payout_fee_percentage / Decimal("100"))
        total_fee = percentage_fee + config.payout_fee_fixed
        return total_fee.quantize(Decimal("0.01"))


# Global configuration instance
payment_config = PaymentProcessorConfig()
