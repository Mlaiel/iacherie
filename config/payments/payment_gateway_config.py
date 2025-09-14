"""
Payment Gateway Configuration - Enterprise Configuration Management
Enterprise configuration for payment gateway integration and processing business logic

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
Licensed under proprietary license - reproduction forbidden without written authorization.
"""

from typing import Dict, List, Optional, Any, Union
from enum import Enum
from dataclasses import dataclass

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


class PaymentGateway(str, Enum):
    """Payment gateway providers"""
    STRIPE = "stripe"
    PAYPAL = "paypal"
    WISE = "wise"
    ADYEN = "adyen"
    SQUARE = "square"
    BRAINTREE = "braintree"
    RAZORPAY = "razorpay"
    KLARNA = "klarna"
    PADDLE = "paddle"
    CHECKOUT_COM = "checkout_com"


class PaymentMethod(str, Enum):
    """Payment methods supported"""
    CREDIT_CARD = "credit_card"
    DEBIT_CARD = "debit_card"
    BANK_TRANSFER = "bank_transfer"
    DIGITAL_WALLET = "digital_wallet"
    CRYPTOCURRENCY = "cryptocurrency"
    ACH = "ach"
    SEPA = "sepa"
    WIRE_TRANSFER = "wire_transfer"
    APPLE_PAY = "apple_pay"
    GOOGLE_PAY = "google_pay"
    PAYPAL = "paypal"
    ALIPAY = "alipay"
    WECHAT_PAY = "wechat_pay"


class Currency(str, Enum):
    """Supported currencies"""
    USD = "USD"
    EUR = "EUR"
    GBP = "GBP"
    JPY = "JPY"
    AUD = "AUD"
    CAD = "CAD"
    CHF = "CHF"
    CNY = "CNY"
    INR = "INR"
    KRW = "KRW"
    BRL = "BRL"
    MXN = "MXN"
    SGD = "SGD"
    HKD = "HKD"
    NZD = "NZD"
    SEK = "SEK"
    NOK = "NOK"
    DKK = "DKK"
    PLN = "PLN"
    CZK = "CZK"


class TransactionType(str, Enum):
    """Transaction types"""
    PAYMENT = "payment"
    REFUND = "refund"
    CHARGEBACK = "chargeback"
    PAYOUT = "payout"
    TRANSFER = "transfer"
    HOLD = "hold"
    RELEASE = "release"
    SPLIT_PAYMENT = "split_payment"
    SUBSCRIPTION = "subscription"
    INSTALLMENT = "installment"


class TransactionStatus(str, Enum):
    """Transaction status"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    REFUNDED = "refunded"
    DISPUTED = "disputed"
    HELD = "held"
    EXPIRED = "expired"


class SecurityLevel(str, Enum):
    """Payment security levels"""
    BASIC = "basic"
    STANDARD = "standard"
    ENHANCED = "enhanced"
    PREMIUM = "premium"
    ENTERPRISE = "enterprise"


@dataclass
class GatewayConfiguration:
    """Payment gateway configuration"""
    gateway: PaymentGateway
    enabled: bool
    primary: bool
    api_credentials: Dict[str, str]
    supported_currencies: List[Currency]
    supported_methods: List[PaymentMethod]
    transaction_limits: Dict[str, float]
    fees: Dict[str, float]
    settlement_time_days: int
    security_level: SecurityLevel
    webhook_url: str
    sandbox_mode: bool


@dataclass
class PaymentMethodConfiguration:
    """Payment method configuration"""
    method: PaymentMethod
    enabled: bool
    supported_gateways: List[PaymentGateway]
    processing_fee_percentage: float
    fixed_fee: float
    minimum_amount: float
    maximum_amount: float
    currencies: List[Currency]
    verification_required: bool
    fraud_protection: bool


@dataclass
class SecurityConfiguration:
    """Payment security configuration"""
    encryption_enabled: bool
    tokenization_enabled: bool
    pci_compliance: bool
    fraud_detection: bool
    risk_scoring: bool
    two_factor_auth: bool
    address_verification: bool
    cvv_verification: bool
    velocity_checking: bool
    geolocation_filtering: bool


@dataclass
class FeeStructure:
    """Fee structure configuration"""
    gateway_fee_percentage: float
    platform_fee_percentage: float
    processing_fee_fixed: float
    currency_conversion_fee: float
    chargeback_fee: float
    refund_fee: float
    international_fee_percentage: float
    premium_feature_fee: float


class PaymentGatewaySettings(BaseSettings):
    """Payment gateway configuration settings"""
    
    # Gateway Configurations
    gateways: Dict[str, GatewayConfiguration] = Field(
        default_factory=lambda: {
            "stripe": GatewayConfiguration(
                gateway=PaymentGateway.STRIPE,
                enabled=True,
                primary=True,
                api_credentials={
                    "publishable_key": "",
                    "secret_key": "",
                    "webhook_secret": "",
                    "client_id": ""
                },
                supported_currencies=[
                    Currency.USD, Currency.EUR, Currency.GBP, Currency.CAD,
                    Currency.AUD, Currency.JPY, Currency.CHF, Currency.SEK,
                    Currency.NOK, Currency.DKK, Currency.PLN
                ],
                supported_methods=[
                    PaymentMethod.CREDIT_CARD, PaymentMethod.DEBIT_CARD,
                    PaymentMethod.APPLE_PAY, PaymentMethod.GOOGLE_PAY,
                    PaymentMethod.BANK_TRANSFER, PaymentMethod.ACH
                ],
                transaction_limits={
                    "min_amount": 0.50,
                    "max_amount": 999999.99,
                    "daily_limit": 100000.00,
                    "monthly_limit": 1000000.00
                },
                fees={
                    "card_percentage": 2.9,
                    "card_fixed": 0.30,
                    "ach_percentage": 0.8,
                    "international_percentage": 3.9
                },
                settlement_time_days=2,
                security_level=SecurityLevel.ENTERPRISE,
                webhook_url="/webhooks/stripe",
                sandbox_mode=False
            ),
            "paypal": GatewayConfiguration(
                gateway=PaymentGateway.PAYPAL,
                enabled=True,
                primary=False,
                api_credentials={
                    "client_id": "",
                    "client_secret": "",
                    "webhook_id": ""
                },
                supported_currencies=[
                    Currency.USD, Currency.EUR, Currency.GBP, Currency.JPY,
                    Currency.AUD, Currency.CAD, Currency.CHF, Currency.CNY
                ],
                supported_methods=[
                    PaymentMethod.PAYPAL, PaymentMethod.CREDIT_CARD,
                    PaymentMethod.DEBIT_CARD, PaymentMethod.BANK_TRANSFER
                ],
                transaction_limits={
                    "min_amount": 1.00,
                    "max_amount": 60000.00,
                    "daily_limit": 60000.00,
                    "monthly_limit": 500000.00
                },
                fees={
                    "paypal_percentage": 3.49,
                    "card_percentage": 3.49,
                    "international_percentage": 4.99
                },
                settlement_time_days=1,
                security_level=SecurityLevel.PREMIUM,
                webhook_url="/webhooks/paypal",
                sandbox_mode=False
            ),
            "adyen": GatewayConfiguration(
                gateway=PaymentGateway.ADYEN,
                enabled=True,
                primary=False,
                api_credentials={
                    "api_key": "",
                    "merchant_account": "",
                    "client_key": "",
                    "webhook_username": "",
                    "webhook_password": ""
                },
                supported_currencies=[
                    Currency.USD, Currency.EUR, Currency.GBP, Currency.JPY,
                    Currency.AUD, Currency.CAD, Currency.CHF, Currency.CNY,
                    Currency.INR, Currency.KRW, Currency.BRL, Currency.MXN
                ],
                supported_methods=[
                    PaymentMethod.CREDIT_CARD, PaymentMethod.DEBIT_CARD,
                    PaymentMethod.BANK_TRANSFER, PaymentMethod.DIGITAL_WALLET,
                    PaymentMethod.ALIPAY, PaymentMethod.WECHAT_PAY
                ],
                transaction_limits={
                    "min_amount": 0.01,
                    "max_amount": 999999.99,
                    "daily_limit": 500000.00,
                    "monthly_limit": 5000000.00
                },
                fees={
                    "card_percentage": 2.6,
                    "card_fixed": 0.10,
                    "alternative_percentage": 1.5,
                    "international_percentage": 3.2
                },
                settlement_time_days=1,
                security_level=SecurityLevel.ENTERPRISE,
                webhook_url="/webhooks/adyen",
                sandbox_mode=False
            ),
            "wise": GatewayConfiguration(
                gateway=PaymentGateway.WISE,
                enabled=True,
                primary=False,
                api_credentials={
                    "api_key": "",
                    "profile_id": "",
                    "private_key": ""
                },
                supported_currencies=[
                    Currency.USD, Currency.EUR, Currency.GBP, Currency.AUD,
                    Currency.CAD, Currency.CHF, Currency.JPY, Currency.SGD,
                    Currency.HKD, Currency.NZD, Currency.SEK, Currency.NOK,
                    Currency.DKK, Currency.PLN, Currency.CZK
                ],
                supported_methods=[
                    PaymentMethod.BANK_TRANSFER, PaymentMethod.WIRE_TRANSFER,
                    PaymentMethod.SEPA, PaymentMethod.ACH
                ],
                transaction_limits={
                    "min_amount": 1.00,
                    "max_amount": 1000000.00,
                    "daily_limit": 1000000.00,
                    "monthly_limit": 10000000.00
                },
                fees={
                    "transfer_percentage": 0.41,
                    "transfer_fixed": 0.50,
                    "currency_conversion": 0.35
                },
                settlement_time_days=1,
                security_level=SecurityLevel.PREMIUM,
                webhook_url="/webhooks/wise",
                sandbox_mode=False
            )
        }
    )
    
    # Payment Method Configurations
    payment_methods: Dict[str, PaymentMethodConfiguration] = Field(
        default_factory=lambda: {
            "credit_card": PaymentMethodConfiguration(
                method=PaymentMethod.CREDIT_CARD,
                enabled=True,
                supported_gateways=[
                    PaymentGateway.STRIPE, PaymentGateway.PAYPAL,
                    PaymentGateway.ADYEN, PaymentGateway.SQUARE
                ],
                processing_fee_percentage=2.9,
                fixed_fee=0.30,
                minimum_amount=0.50,
                maximum_amount=999999.99,
                currencies=[
                    Currency.USD, Currency.EUR, Currency.GBP,
                    Currency.CAD, Currency.AUD, Currency.JPY
                ],
                verification_required=True,
                fraud_protection=True
            ),
            "bank_transfer": PaymentMethodConfiguration(
                method=PaymentMethod.BANK_TRANSFER,
                enabled=True,
                supported_gateways=[
                    PaymentGateway.STRIPE, PaymentGateway.WISE,
                    PaymentGateway.ADYEN
                ],
                processing_fee_percentage=0.8,
                fixed_fee=0.00,
                minimum_amount=1.00,
                maximum_amount=1000000.00,
                currencies=[
                    Currency.USD, Currency.EUR, Currency.GBP,
                    Currency.CAD, Currency.AUD
                ],
                verification_required=True,
                fraud_protection=True
            ),
            "digital_wallet": PaymentMethodConfiguration(
                method=PaymentMethod.DIGITAL_WALLET,
                enabled=True,
                supported_gateways=[
                    PaymentGateway.STRIPE, PaymentGateway.PAYPAL,
                    PaymentGateway.ADYEN
                ],
                processing_fee_percentage=2.5,
                fixed_fee=0.25,
                minimum_amount=0.50,
                maximum_amount=50000.00,
                currencies=[
                    Currency.USD, Currency.EUR, Currency.GBP,
                    Currency.JPY, Currency.CNY
                ],
                verification_required=False,
                fraud_protection=True
            ),
            "cryptocurrency": PaymentMethodConfiguration(
                method=PaymentMethod.CRYPTOCURRENCY,
                enabled=True,
                supported_gateways=[PaymentGateway.STRIPE],  # Via crypto extension
                processing_fee_percentage=1.5,
                fixed_fee=0.00,
                minimum_amount=10.00,
                maximum_amount=100000.00,
                currencies=[Currency.USD, Currency.EUR],  # Converted from crypto
                verification_required=True,
                fraud_protection=True
            )
        }
    )
    
    # Security Configuration
    security_config: SecurityConfiguration = Field(
        default_factory=lambda: SecurityConfiguration(
            encryption_enabled=True,
            tokenization_enabled=True,
            pci_compliance=True,
            fraud_detection=True,
            risk_scoring=True,
            two_factor_auth=True,
            address_verification=True,
            cvv_verification=True,
            velocity_checking=True,
            geolocation_filtering=True
        )
    )
    
    # Fee Structures
    fee_structures: Dict[str, FeeStructure] = Field(
        default_factory=lambda: {
            "standard": FeeStructure(
                gateway_fee_percentage=2.9,
                platform_fee_percentage=1.0,
                processing_fee_fixed=0.30,
                currency_conversion_fee=1.5,
                chargeback_fee=15.00,
                refund_fee=0.00,
                international_fee_percentage=1.0,
                premium_feature_fee=0.5
            ),
            "premium": FeeStructure(
                gateway_fee_percentage=2.6,
                platform_fee_percentage=0.8,
                processing_fee_fixed=0.25,
                currency_conversion_fee=1.2,
                chargeback_fee=12.00,
                refund_fee=0.00,
                international_fee_percentage=0.8,
                premium_feature_fee=0.3
            ),
            "enterprise": FeeStructure(
                gateway_fee_percentage=2.2,
                platform_fee_percentage=0.5,
                processing_fee_fixed=0.20,
                currency_conversion_fee=1.0,
                chargeback_fee=10.00,
                refund_fee=0.00,
                international_fee_percentage=0.5,
                premium_feature_fee=0.0
            )
        }
    )
    
    # Multi-currency Settings
    multi_currency_settings: Dict[str, Any] = Field(
        default_factory=lambda: {
            "auto_conversion": True,
            "real_time_rates": True,
            "rate_provider": "xe_currency",
            "conversion_buffer_percentage": 0.5,
            "supported_currencies": [
                "USD", "EUR", "GBP", "JPY", "AUD", "CAD", "CHF",
                "CNY", "INR", "KRW", "BRL", "MXN", "SGD", "HKD"
            ],
            "base_currency": "USD",
            "settlement_currencies": ["USD", "EUR", "GBP"],
            "hedging_enabled": True
        }
    )
    
    # Payout Configuration
    payout_settings: Dict[str, Any] = Field(
        default_factory=lambda: {
            "automated_payouts": True,
            "payout_schedule": "daily",
            "minimum_payout_amount": 25.00,
            "payout_methods": [
                "bank_transfer", "wire_transfer", "digital_wallet"
            ],
            "payout_currencies": ["USD", "EUR", "GBP", "CAD", "AUD"],
            "hold_period_days": 7,
            "rolling_reserve_percentage": 5.0,
            "instant_payout_fee": 1.5
        }
    )
    
    # Compliance Settings
    compliance_settings: Dict[str, Any] = Field(
        default_factory=lambda: {
            "kyc_enabled": True,
            "aml_screening": True,
            "tax_reporting": True,
            "regulatory_reporting": True,
            "data_retention_years": 7,
            "audit_trail": True,
            "transaction_monitoring": True,
            "sanctions_screening": True
        }
    )
    
    # Integration Settings
    integration_settings: Dict[str, Any] = Field(
        default_factory=lambda: {
            "webhook_security": True,
            "api_rate_limiting": True,
            "real_time_notifications": True,
            "batch_processing": True,
            "retry_mechanism": True,
            "failover_enabled": True,
            "load_balancing": True,
            "monitoring_enabled": True
        }
    )
    
    # Performance Settings
    performance_settings: Dict[str, Any] = Field(
        default_factory=lambda: {
            "caching_enabled": True,
            "connection_pooling": True,
            "timeout_seconds": 30,
            "retry_attempts": 3,
            "circuit_breaker": True,
            "graceful_degradation": True,
            "performance_monitoring": True,
            "latency_tracking": True
        }
    )
    
    class Config:
    """Config: class implementation"""
        env_prefix = "PAYMENT_GATEWAY_"
        case_sensitive = False
        extra = "allow"
    
    def get_gateway_config(self, gateway: str) -> Optional[GatewayConfiguration]:
        """Get gateway configuration by name"""
        return self.gateways.get(gateway)
    
    def get_payment_method_config(self, method: str) -> Optional[PaymentMethodConfiguration]:
        """Get payment method configuration by name"""
        return self.payment_methods.get(method)
    
    def get_fee_structure(self, tier: str) -> Optional[FeeStructure]:
        """Get fee structure by tier"""
        return self.fee_structures.get(tier)
    
    def is_gateway_enabled(self, gateway: str) -> bool:
        """Check if gateway is enabled"""
        config = self.get_gateway_config(gateway)
        return config.enabled if config else False
    
    def is_payment_method_enabled(self, method: str) -> bool:
        """Check if payment method is enabled"""
        config = self.get_payment_method_config(method)
        return config.enabled if config else False
    
    def get_primary_gateway(self) -> Optional[str]:
        """Get the primary gateway"""
        for gateway_name, config in self.gateways.items():
            if config.enabled and config.primary:
                return gateway_name
        return None
    
    def get_supported_currencies(self, gateway: str) -> List[Currency]:
        """Get supported currencies for a gateway"""
        config = self.get_gateway_config(gateway)
        return config.supported_currencies if config else []
    
    def get_transaction_limits(self, gateway: str) -> Dict[str, float]:
        """Get transaction limits for a gateway"""
        config = self.get_gateway_config(gateway)
        return config.transaction_limits if config else {}
    
    def get_processing_fee(self, method: str) -> tuple[float, float]:
        """Get processing fee (percentage, fixed) for payment method"""
        config = self.get_payment_method_config(method)
        if config:
            return config.processing_fee_percentage, config.fixed_fee
        return 0.0, 0.0
    
    def is_currency_supported(self, gateway: str, currency: str) -> bool:
        """Check if currency is supported by gateway"""
        supported = self.get_supported_currencies(gateway)
        return Currency(currency) in supported if supported else False
    
    def get_settlement_time(self, gateway: str) -> int:
        """Get settlement time for gateway in days"""
        config = self.get_gateway_config(gateway)
        return config.settlement_time_days if config else 7
    
    def validate_configuration(self) -> List[str]:
        """Validate the complete payment gateway configuration"""
        errors = []
        
        # Check that at least one gateway is enabled and primary
        primary_gateways = [
            name for name, config in self.gateways.items()
            if config.enabled and config.primary
        ]
        if not primary_gateways:
            errors.append("No primary gateway configured")
        elif len(primary_gateways) > 1:
            errors.append("Multiple primary gateways configured")
        
        # Validate gateway configurations
        for gateway_name, config in self.gateways.items():
            if config.enabled:
                if not config.supported_currencies:
                    errors.append(f"Gateway '{gateway_name}' has no supported currencies")
                if not config.supported_methods:
                    errors.append(f"Gateway '{gateway_name}' has no supported payment methods")
                if config.settlement_time_days <= 0:
                    errors.append(f"Gateway '{gateway_name}' has invalid settlement time")
        
        # Validate payment method configurations
        for method_name, config in self.payment_methods.items():
            if config.enabled:
                if not config.supported_gateways:
                    errors.append(f"Payment method '{method_name}' has no supported gateways")
                if config.minimum_amount < 0:
                    errors.append(f"Payment method '{method_name}' has negative minimum amount")
                if config.maximum_amount <= config.minimum_amount:
                    errors.append(f"Payment method '{method_name}' has invalid amount limits")
        
        # Validate fee structures
        for tier_name, fees in self.fee_structures.items():
            if fees.gateway_fee_percentage < 0:
                errors.append(f"Fee structure '{tier_name}' has negative gateway fee")
            if fees.platform_fee_percentage < 0:
                errors.append(f"Fee structure '{tier_name}' has negative platform fee")
        
        return errors


# Global payment gateway settings instance
payment_gateway_settings = PaymentGatewaySettings()

__all__ = [
    "PaymentGatewaySettings",
    "payment_gateway_settings",
    "PaymentGateway",
    "PaymentMethod",
    "Currency",
    "TransactionType",
    "TransactionStatus",
    "SecurityLevel",
    "GatewayConfiguration",
    "PaymentMethodConfiguration",
    "SecurityConfiguration",
    "FeeStructure"
]