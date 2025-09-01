"""Payment APIs Configuration - Financial Services & Payment Processor Integration
Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

This module configures payment processing APIs for automated monetization,
revenue tracking, and financial transactions across multiple providers.
"""

import os
from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional
from enum import Enum
from decimal import Decimal

class PaymentProviderType(Enum):
    """
Payment provider types"""

    CREDIT_CARD = "credit_card"
    DIGITAL_WALLET = "digital_wallet"
    BANK_TRANSFER = "bank_transfer"
    CRYPTOCURRENCY = "cryptocurrency"
    MONEY_TRANSFER = "money_transfer"

class PaymentMethod(Enum):
    """Supported payment methods"""

    CARD = "card"
    PAYPAL = "paypal"
    APPLE_PAY = "apple_pay"
    GOOGLE_PAY = "google_pay"
    SEPA = "sepa"
    ACH = "ach"
    WIRE = "wire"
    CRYPTO = "crypto"

@dataclass
class PaymentAPIConfig:
    """Configuration class for payment APIs"""
    provider_name: str
    provider_type: PaymentProviderType
    base_url: str
    api_version: str
    
    # API Credentials (from environment)
    api_key: Optional[str] = None
    secret_key: Optional[str] = None
    publishable_key: Optional[str] = None
    merchant_id: Optional[str] = None
    webhook_secret: Optional[str] = None
    
    # Supported features
    supported_methods: List[PaymentMethod] = field(default_factory=list)
    supported_currencies: List[str] = field(default_factory=list)
    supported_countries: List[str] = field(default_factory=list)
    
    # Transaction limits
    min_amount: Decimal = Decimal("0.50")
    max_amount: Decimal = Decimal("999999.99")
    daily_limit: Optional[Decimal] = None
    monthly_limit: Optional[Decimal] = None
    
    # Fee structure
    processing_fee_percentage: float = 2.9
    fixed_fee_amount: Decimal = Decimal("0.30")
    international_fee_percentage: float = 1.5
    currency_conversion_fee: float = 1.0
    
    # Settlement
    settlement_delay_days: int = 2
    supports_instant_payout: bool = False
    payout_schedule: str = "daily"  # daily, weekly, monthly
    
    # Security & Compliance
    pci_compliant: bool = True
    supports_3d_secure: bool = False
    fraud_detection: bool = True
    
    # Rate limiting
    rate_limit_per_minute: int = 100
    timeout_seconds: int = 30
    
    # Environment configurations
    environments: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    
    def get_environment_config(self, environment: str = "production") -> Dict[str, Any]:
        """Get configuration for specific environment"""
        base_config = self.__dict__.copy()
        env_config = self.environments.get(environment, {})
        base_config.update(env_config)
        return base_config

# Stripe Configuration
STRIPE_CONFIG = PaymentAPIConfig(
    provider_name="stripe",
    provider_type=PaymentProviderType.CREDIT_CARD,
    base_url="https://api.stripe.com",
    api_version="2023-10-16",
    api_key=os.getenv("STRIPE_SECRET_KEY"),
    publishable_key=os.getenv("STRIPE_PUBLISHABLE_KEY"),
    webhook_secret=os.getenv("STRIPE_WEBHOOK_SECRET"),
    supported_methods=[
        PaymentMethod.CARD,
        PaymentMethod.APPLE_PAY,
        PaymentMethod.GOOGLE_PAY,
        PaymentMethod.SEPA,
        PaymentMethod.ACH
    ],
    supported_currencies=[
        "USD", "EUR", "GBP", "CAD", "AUD", "JPY", "CHF", "SEK", "NOK", "DKK",
        "PLN", "CZK", "HUF", "BGN", "RON", "HRK", "RSD", "BAM", "MKD", "ALL"
    ],
    supported_countries=[
        "US", "CA", "GB", "DE", "FR", "IT", "ES", "NL", "BE", "AT", "CH", "SE",
        "NO", "DK", "FI", "PL", "CZ", "HU", "SK", "SI", "HR", "EE", "LV", "LT"
    ],
    processing_fee_percentage=2.9,
    fixed_fee_amount=Decimal("0.30"),
    international_fee_percentage=1.5,
    settlement_delay_days=2,
    supports_instant_payout=True,
    supports_3d_secure=True,
    fraud_detection=True,
    environments={
        "development": {
            "api_key": os.getenv("STRIPE_TEST_SECRET_KEY"),
            "publishable_key": os.getenv("STRIPE_TEST_PUBLISHABLE_KEY")
        },
        "staging": {
            "api_key": os.getenv("STRIPE_TEST_SECRET_KEY"),
            "publishable_key": os.getenv("STRIPE_TEST_PUBLISHABLE_KEY")
        }
    }
)

# PayPal Configuration
PAYPAL_CONFIG = PaymentAPIConfig(
    provider_name="paypal",
    provider_type=PaymentProviderType.DIGITAL_WALLET,
    base_url="https://api-m.paypal.com",
    api_version="v2",
    api_key=os.getenv("PAYPAL_CLIENT_ID"),
    secret_key=os.getenv("PAYPAL_CLIENT_SECRET"),
    webhook_secret=os.getenv("PAYPAL_WEBHOOK_SECRET"),
    supported_methods=[PaymentMethod.PAYPAL],
    supported_currencies=[
        "USD", "EUR", "GBP", "CAD", "AUD", "JPY", "CHF", "SEK", "NOK", "DKK",
        "PLN", "CZK", "HUF", "ILS", "MXN", "BRL", "SGD", "HKD", "TWD", "THB"
    ],
    supported_countries=[
        "US", "CA", "GB", "DE", "FR", "IT", "ES", "NL", "BE", "AT", "CH", "SE",
        "NO", "DK", "FI", "PL", "CZ", "HU", "SK", "SI", "IE", "PT", "GR", "LU"
    ],
    processing_fee_percentage=3.49,
    fixed_fee_amount=Decimal("0.49"),
    international_fee_percentage=5.4,
    settlement_delay_days=1,
    supports_instant_payout=True,
    environments={
        "development": {
            "base_url": "https://api-m.sandbox.paypal.com",
            "api_key": os.getenv("PAYPAL_SANDBOX_CLIENT_ID"),
            "secret_key": os.getenv("PAYPAL_SANDBOX_CLIENT_SECRET")
        },
        "staging": {
            "base_url": "https://api-m.sandbox.paypal.com",
            "api_key": os.getenv("PAYPAL_SANDBOX_CLIENT_ID"),
            "secret_key": os.getenv("PAYPAL_SANDBOX_CLIENT_SECRET")
        }
    }
)

# Wise (TransferWise) Configuration
WISE_CONFIG = PaymentAPIConfig(
    provider_name="wise",
    provider_type=PaymentProviderType.MONEY_TRANSFER,
    base_url="https://api.transferwise.com",
    api_version="v1",
    api_key=os.getenv("WISE_API_TOKEN"),
    webhook_secret=os.getenv("WISE_WEBHOOK_SECRET"),
    supported_methods=[PaymentMethod.WIRE, PaymentMethod.SEPA, PaymentMethod.ACH],
    supported_currencies=[
        "USD", "EUR", "GBP", "CAD", "AUD", "JPY", "CHF", "SEK", "NOK", "DKK",
        "PLN", "CZK", "HUF", "BGN", "RON", "HRK", "RSD", "TRY", "ZAR", "INR",
        "BRL", "MXN", "SGD", "HKD", "NZD", "ILS", "AED", "THB", "MYR", "PHP"
    ],
    supported_countries=[
        "US", "CA", "GB", "DE", "FR", "IT", "ES", "NL", "BE", "AT", "CH", "SE",
        "NO", "DK", "FI", "PL", "CZ", "HU", "SK", "SI", "EE", "LV", "LT", "IE",
        "PT", "GR", "LU", "MT", "CY", "BG", "RO", "HR", "TR", "ZA", "IN", "BR"
    ],
    processing_fee_percentage=0.5,  # Much lower fees
    fixed_fee_amount=Decimal("1.00"),
    international_fee_percentage=0.5,
    settlement_delay_days=1,
    supports_instant_payout=False,
    environments={
        "development": {
            "base_url": "https://api.sandbox.transferwise.tech",
            "api_key": os.getenv("WISE_SANDBOX_API_TOKEN")
        },
        "staging": {
            "base_url": "https://api.sandbox.transferwise.tech",
            "api_key": os.getenv("WISE_SANDBOX_API_TOKEN")
        }
    }
)

# Square Configuration
SQUARE_CONFIG = PaymentAPIConfig(
    provider_name="square",
    provider_type=PaymentProviderType.CREDIT_CARD,
    base_url="https://connect.squareup.com",
    api_version="2023-12-13",
    api_key=os.getenv("SQUARE_ACCESS_TOKEN"),
    webhook_secret=os.getenv("SQUARE_WEBHOOK_SECRET"),
    supported_methods=[
        PaymentMethod.CARD,
        PaymentMethod.APPLE_PAY,
        PaymentMethod.GOOGLE_PAY
    ],
    supported_currencies=["USD", "CAD", "GBP", "EUR", "AUD", "JPY"],
    supported_countries=["US", "CA", "GB", "IE", "AU", "JP"],
    processing_fee_percentage=2.9,
    fixed_fee_amount=Decimal("0.30"),
    settlement_delay_days=1,
    supports_instant_payout=True,
    environments={
        "development": {
            "base_url": "https://connect.squareupsandbox.com",
            "api_key": os.getenv("SQUARE_SANDBOX_ACCESS_TOKEN")
        },
        "staging": {
            "base_url": "https://connect.squareupsandbox.com",
            "api_key": os.getenv("SQUARE_SANDBOX_ACCESS_TOKEN")
        }
    }
)

# Apple Pay Configuration
APPLE_PAY_CONFIG = PaymentAPIConfig(
    provider_name="apple_pay",
    provider_type=PaymentProviderType.DIGITAL_WALLET,
    base_url="https://apple-pay-gateway.apple.com",
    api_version="v1",
    merchant_id=os.getenv("APPLE_PAY_MERCHANT_ID"),
    supported_methods=[PaymentMethod.APPLE_PAY],
    supported_currencies=["USD", "EUR", "GBP", "CAD", "AUD", "JPY", "CHF"],
    processing_fee_percentage=0.15,  # Apple's fee
    settlement_delay_days=1,
    supports_3d_secure=True
)

# Google Pay Configuration
GOOGLE_PAY_CONFIG = PaymentAPIConfig(
    provider_name="google_pay",
    provider_type=PaymentProviderType.DIGITAL_WALLET,
    base_url="https://payments.developers.google.com",
    api_version="v1",
    merchant_id=os.getenv("GOOGLE_PAY_MERCHANT_ID"),
    supported_methods=[PaymentMethod.GOOGLE_PAY],
    supported_currencies=["USD", "EUR", "GBP", "CAD", "AUD", "JPY", "INR"],
    processing_fee_percentage=0.0,  # No additional fee from Google
    settlement_delay_days=1
)

# Coinbase Commerce Configuration (Cryptocurrency)
COINBASE_CONFIG = PaymentAPIConfig(
    provider_name="coinbase",
    provider_type=PaymentProviderType.CRYPTOCURRENCY,
    base_url="https://api.commerce.coinbase.com",
    api_version="2018-03-22",
    api_key=os.getenv("COINBASE_COMMERCE_API_KEY"),
    webhook_secret=os.getenv("COINBASE_COMMERCE_WEBHOOK_SECRET"),
    supported_methods=[PaymentMethod.CRYPTO],
    supported_currencies=["BTC", "ETH", "LTC", "BCH", "DAI", "USDC"],
    processing_fee_percentage=1.0,
    settlement_delay_days=0,  # Instant for crypto
    environments={
        "development": {
            "base_url": "https://api.commerce.coinbase.com"  # Same for all envs
        }
    }
)

# BitPay Configuration (Cryptocurrency - 15+ supported)
BITPAY_CONFIG = PaymentAPIConfig(
    provider_name="bitpay",
    provider_type=PaymentProviderType.CRYPTOCURRENCY,
    base_url="https://bitpay.com/api",
    api_version="v1",
    api_key=os.getenv("BITPAY_API_TOKEN"),
    webhook_secret=os.getenv("BITPAY_WEBHOOK_SECRET"),
    supported_methods=[PaymentMethod.CRYPTO],
    supported_currencies=[
        "BTC", "ETH", "LTC", "BCH", "XRP", "ADA", "DOT", "UNI", "LINK", 
        "MATIC", "USDC", "USDT", "DAI", "BUSD", "SHIB", "DOGE", "XLM"
    ],
    processing_fee_percentage=1.0,
    settlement_delay_days=0,  # Instant for crypto
    min_amount=Decimal("1.00"),
    max_amount=Decimal("100000.00"),
    environments={
        "development": {
            "base_url": "https://test.bitpay.com/api"
        },
        "staging": {
            "base_url": "https://test.bitpay.com/api"
        }
    }
)

# Crypto.com Pay Configuration (Cryptocurrency - Wallet Integration)
CRYPTO_COM_PAY_CONFIG = PaymentAPIConfig(
    provider_name="crypto_com_pay",
    provider_type=PaymentProviderType.CRYPTOCURRENCY,
    base_url="https://pay-api.crypto.com",
    api_version="v1",
    api_key=os.getenv("CRYPTO_COM_PAY_API_KEY"),
    secret_key=os.getenv("CRYPTO_COM_PAY_SECRET_KEY"),
    webhook_secret=os.getenv("CRYPTO_COM_PAY_WEBHOOK_SECRET"),
    supported_methods=[PaymentMethod.CRYPTO],
    supported_currencies=[
        "BTC", "ETH", "CRO", "USDC", "USDT", "BNB", "ADA", "DOT", "MATIC", 
        "LINK", "UNI", "AAVE", "COMP", "SOL", "AVAX"
    ],
    processing_fee_percentage=0.5,  # Lower fees for Crypto.com ecosystem
    settlement_delay_days=0,  # Instant for crypto
    min_amount=Decimal("0.10"),
    max_amount=Decimal("500000.00"),
    environments={
        "development": {
            "base_url": "https://uat-pay-api.crypto.com"
        },
        "staging": {
            "base_url": "https://uat-pay-api.crypto.com"
        }
    }
)

# Adyen Configuration (Global payment platform)
ADYEN_CONFIG = PaymentAPIConfig(
    provider_name="adyen",
    provider_type=PaymentProviderType.CREDIT_CARD,
    base_url="https://checkout-live.adyen.com",
    api_version="v71",
    api_key=os.getenv("ADYEN_API_KEY"),
    merchant_id=os.getenv("ADYEN_MERCHANT_ACCOUNT"),
    supported_methods=[
        PaymentMethod.CARD,
        PaymentMethod.PAYPAL,
        PaymentMethod.APPLE_PAY,
        PaymentMethod.GOOGLE_PAY,
        PaymentMethod.SEPA
    ],
    supported_currencies=[
        "USD", "EUR", "GBP", "CAD", "AUD", "JPY", "CHF", "SEK", "NOK", "DKK",
        "PLN", "CZK", "HUF", "BGN", "RON", "HRK", "TRY", "ZAR", "INR", "BRL",
        "MXN", "SGD", "HKD", "NZD", "ILS", "AED", "THB", "MYR", "PHP", "KRW"
    ],
    processing_fee_percentage=2.95,
    fixed_fee_amount=Decimal("0.28"),
    international_fee_percentage=1.0,
    settlement_delay_days=1,
    supports_instant_payout=True,
    supports_3d_secure=True,
    fraud_detection=True,
    environments={
        "development": {
            "base_url": "https://checkout-test.adyen.com",
            "api_key": os.getenv("ADYEN_TEST_API_KEY")
        },
        "staging": {
            "base_url": "https://checkout-test.adyen.com",
            "api_key": os.getenv("ADYEN_TEST_API_KEY")
        }
    }
)

# Payment configurations registry
PAYMENT_CONFIGS: Dict[str, PaymentAPIConfig] = {
    "stripe": STRIPE_CONFIG,
    "paypal": PAYPAL_CONFIG,
    "wise": WISE_CONFIG,
    "square": SQUARE_CONFIG,
    "apple_pay": APPLE_PAY_CONFIG,
    "google_pay": GOOGLE_PAY_CONFIG,
    "coinbase": COINBASE_CONFIG,
    "bitpay": BITPAY_CONFIG,
    "crypto_com_pay": CRYPTO_COM_PAY_CONFIG,
    "adyen": ADYEN_CONFIG
}

def get_payment_config(provider: str) -> Optional[PaymentAPIConfig]:
    """Get payment configuration by provider name"""
    return PAYMENT_CONFIGS.get(provider.lower())

def get_providers_by_type(provider_type: PaymentProviderType) -> List[PaymentAPIConfig]:
    """
Get all payment providers of specific type"""
    return [config for config in PAYMENT_CONFIGS.values() 
            if config.provider_type == provider_type]

def get_providers_by_currency(currency: str) -> List[PaymentAPIConfig]:
    """
Get payment providers supporting specific currency"""
    return [config for config in PAYMENT_CONFIGS.values() 
            if currency.upper() in config.supported_currencies]

def get_providers_by_country(country: str) -> List[PaymentAPIConfig]:
    """
Get payment providers supporting specific country"""
    return [config for config in PAYMENT_CONFIGS.values() 
            if country.upper() in config.supported_countries]
