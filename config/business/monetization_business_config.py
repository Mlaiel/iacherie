"""
Monetization Business Configuration - Enterprise Configuration Management
Enterprise configuration for monetization business logic and revenue management

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
Licensed under proprietary license - reproduction forbidden without written authorization.
"""

from typing import Dict, List, Optional, Any, Union
from enum import Enum
from dataclasses import dataclass


class PaymentGateway(str, Enum):
    """Payment gateway providers"""
    STRIPE = "stripe"
    PAYPAL = "paypal"
    WISE = "wise"
    ADYEN = "adyen"
    SQUARE = "square"
    BRAINTREE = "braintree"


class CryptoCurrency(str, Enum):
    """Supported cryptocurrencies"""
    BITCOIN = "bitcoin"
    ETHEREUM = "ethereum"
    USDC = "usdc"
    USDT = "usdt"
    CUSTOM_TOKENS = "custom_tokens"
    SOLANA = "solana"
    POLYGON = "polygon"


class RevenueStream(str, Enum):
    """Revenue stream types"""
    STREAMING_ROYALTIES = "streaming_royalties"
    ADVERTISING_REVENUE = "advertising_revenue"
    SUBSCRIPTION_FEES = "subscription_fees"
    MERCHANDISE_SALES = "merchandise_sales"
    LICENSING_FEES = "licensing_fees"
    COLLABORATION_REVENUE = "collaboration_revenue"
    SPONSORSHIP_DEALS = "sponsorship_deals"
    TIP_DONATIONS = "tip_donations"
    NFT_SALES = "nft_sales"
    LIVE_EVENTS = "live_events"


class SubscriptionTier(str, Enum):
    """Subscription tier types"""
    BASIC = "basic"
    PROFESSIONAL = "professional"
    ENTERPRISE = "enterprise"
    CUSTOM = "custom"


class BillingCycle(str, Enum):
    """Billing cycle options"""
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    YEARLY = "yearly"
    LIFETIME = "lifetime"


class PaymentMethod(str, Enum):
    """Payment method types"""
    CARD = "card"
    BANK_TRANSFER = "bank_transfer"
    DIGITAL_WALLET = "digital_wallet"
    CRYPTO = "crypto"
    CASH = "cash"
    CHECK = "check"


@dataclass
class PaymentGatewayConfig:
    """Payment gateway configuration"""
    gateway: PaymentGateway
    enabled: bool
    api_key: Optional[str]
    secret_key: Optional[str]
    webhook_url: Optional[str]
    supported_currencies: List[str]
    transaction_fee_percentage: float
    processing_time_hours: int
    security_level: str


@dataclass
class RevenueStreamConfig:
    """Revenue stream configuration"""
    stream_type: RevenueStream
    enabled: bool
    commission_rate: float
    minimum_payout: float
    payout_frequency: str
    automated_collection: bool
    analytics_tracking: bool


@dataclass
class SubscriptionConfig:
    """Subscription management configuration"""
    tier: SubscriptionTier
    price_usd: float
    billing_cycle: BillingCycle
    features: List[str]
    limits: Dict[str, Any]
    trial_period_days: int
    auto_renewal: bool


@dataclass
class CryptoPaymentConfig:
    """Crypto payment configuration"""
    currency: CryptoCurrency
    enabled: bool
    wallet_address: Optional[str]
    network: str
    confirmation_blocks: int
    transaction_fee: float
    exchange_rate_source: str


class MonetizationBusinessSettings:
    """Monetization business logic configuration settings"""
    
    def __init__(self) -> None:
        # Payment Gateway Configurations
        self.payment_gateways = {
            PaymentGateway.STRIPE: PaymentGatewayConfig(
                gateway=PaymentGateway.STRIPE,
                enabled=True,
                api_key=None,  # Set via environment variables
                secret_key=None,
                webhook_url=None,
                supported_currencies=["USD", "EUR", "GBP", "CAD", "AUD", "JPY"],
                transaction_fee_percentage=2.9,
                processing_time_hours=24,
                security_level="enterprise"
            ),
            PaymentGateway.PAYPAL: PaymentGatewayConfig(
                gateway=PaymentGateway.PAYPAL,
                enabled=True,
                api_key=None,
                secret_key=None,
                webhook_url=None,
                supported_currencies=["USD", "EUR", "GBP", "CAD", "AUD"],
                transaction_fee_percentage=3.5,
                processing_time_hours=48,
                security_level="standard"
            ),
            PaymentGateway.WISE: PaymentGatewayConfig(
                gateway=PaymentGateway.WISE,
                enabled=True,
                api_key=None,
                secret_key=None,
                webhook_url=None,
                supported_currencies=["USD", "EUR", "GBP", "CAD", "AUD", "JPY", "CHF"],
                transaction_fee_percentage=1.5,
                processing_time_hours=72,
                security_level="high"
            )
        }
        
        # Crypto Payment Configurations
        self.crypto_payments = {
            CryptoCurrency.BITCOIN: CryptoPaymentConfig(
                currency=CryptoCurrency.BITCOIN,
                enabled=True,
                wallet_address=None,
                network="mainnet",
                confirmation_blocks=3,
                transaction_fee=0.0005,
                exchange_rate_source="coinbase"
            ),
            CryptoCurrency.ETHEREUM: CryptoPaymentConfig(
                currency=CryptoCurrency.ETHEREUM,
                enabled=True,
                wallet_address=None,
                network="mainnet",
                confirmation_blocks=12,
                transaction_fee=0.001,
                exchange_rate_source="coinbase"
            ),
            CryptoCurrency.USDC: CryptoPaymentConfig(
                currency=CryptoCurrency.USDC,
                enabled=True,
                wallet_address=None,
                network="ethereum",
                confirmation_blocks=12,
                transaction_fee=0.0001,
                exchange_rate_source="coinbase"
            )
        }
        
        # Revenue Stream Configurations
        self.revenue_streams = {
            RevenueStream.STREAMING_ROYALTIES: RevenueStreamConfig(
                stream_type=RevenueStream.STREAMING_ROYALTIES,
                enabled=True,
                commission_rate=0.10,  # 10%
                minimum_payout=25.0,
                payout_frequency="monthly",
                automated_collection=True,
                analytics_tracking=True
            ),
            RevenueStream.ADVERTISING_REVENUE: RevenueStreamConfig(
                stream_type=RevenueStream.ADVERTISING_REVENUE,
                enabled=True,
                commission_rate=0.15,  # 15%
                minimum_payout=50.0,
                payout_frequency="monthly",
                automated_collection=True,
                analytics_tracking=True
            ),
            RevenueStream.SUBSCRIPTION_FEES: RevenueStreamConfig(
                stream_type=RevenueStream.SUBSCRIPTION_FEES,
                enabled=True,
                commission_rate=0.05,  # 5%
                minimum_payout=10.0,
                payout_frequency="monthly",
                automated_collection=True,
                analytics_tracking=True
            ),
            RevenueStream.LICENSING_FEES: RevenueStreamConfig(
                stream_type=RevenueStream.LICENSING_FEES,
                enabled=True,
                commission_rate=0.20,  # 20%
                minimum_payout=100.0,
                payout_frequency="quarterly",
                automated_collection=True,
                analytics_tracking=True
            ),
            RevenueStream.TIP_DONATIONS: RevenueStreamConfig(
                stream_type=RevenueStream.TIP_DONATIONS,
                enabled=True,
                commission_rate=0.05,  # 5%
                minimum_payout=5.0,
                payout_frequency="weekly",
                automated_collection=True,
                analytics_tracking=True
            )
        }
        
        # Subscription Tier Configurations
        self.subscription_tiers = {
            SubscriptionTier.BASIC: SubscriptionConfig(
                tier=SubscriptionTier.BASIC,
                price_usd=9.99,
                billing_cycle=BillingCycle.MONTHLY,
                features=[
                    "basic_content_upload",
                    "standard_protection",
                    "basic_analytics",
                    "community_support"
                ],
                limits={
                    "uploads_per_month": 50,
                    "storage_gb": 10,
                    "collaborations": 3,
                    "distribution_platforms": 3
                },
                trial_period_days=14,
                auto_renewal=True
            ),
            SubscriptionTier.PROFESSIONAL: SubscriptionConfig(
                tier=SubscriptionTier.PROFESSIONAL,
                price_usd=29.99,
                billing_cycle=BillingCycle.MONTHLY,
                features=[
                    "unlimited_content_upload",
                    "advanced_protection",
                    "comprehensive_analytics",
                    "priority_support",
                    "collaboration_tools",
                    "monetization_optimization"
                ],
                limits={
                    "uploads_per_month": -1,  # Unlimited
                    "storage_gb": 100,
                    "collaborations": 25,
                    "distribution_platforms": 10
                },
                trial_period_days=30,
                auto_renewal=True
            ),
            SubscriptionTier.ENTERPRISE: SubscriptionConfig(
                tier=SubscriptionTier.ENTERPRISE,
                price_usd=99.99,
                billing_cycle=BillingCycle.MONTHLY,
                features=[
                    "enterprise_content_management",
                    "premium_protection",
                    "advanced_analytics",
                    "dedicated_support",
                    "team_collaboration",
                    "custom_integrations",
                    "white_label_options",
                    "api_access"
                ],
                limits={
                    "uploads_per_month": -1,
                    "storage_gb": -1,  # Unlimited
                    "collaborations": -1,
                    "distribution_platforms": -1
                },
                trial_period_days=30,
                auto_renewal=True
            )
        }
        
        # Revenue Optimization Settings
        self.revenue_optimization = {
            "dynamic_pricing": True,
            "demand_forecasting": True,
            "cross_selling": True,
            "upselling": True,
            "churn_prevention": True,
            "lifetime_value_optimization": True,
            "a_b_testing": True,
            "personalized_offers": True
        }
        
        # Financial Analytics
        self.financial_analytics = {
            "revenue_tracking": True,
            "profit_margin_analysis": True,
            "customer_lifetime_value": True,
            "acquisition_cost_tracking": True,
            "churn_rate_monitoring": True,
            "conversion_rate_optimization": True,
            "payment_success_rate": True,
            "refund_rate_tracking": True
        }
        
        # Tax and Compliance
        self.tax_compliance = {
            "automated_tax_calculation": True,
            "vat_handling": True,
            "international_tax_compliance": True,
            "1099_reporting": True,
            "audit_trail": True,
            "regulatory_reporting": True
        }
        
        # Security and Fraud Prevention
        self.security_settings = {
            "fraud_detection": True,
            "3d_secure": True,
            "address_verification": True,
            "cvv_verification": True,
            "velocity_checking": True,
            "device_fingerprinting": True,
            "machine_learning_fraud_detection": True
        }
        
        # Payout Settings
        self.payout_settings = {
            "automated_payouts": True,
            "payout_scheduling": True,
            "minimum_payout_thresholds": True,
            "multi_currency_payouts": True,
            "instant_payouts": False,  # Premium feature
            "payout_notifications": True
        }
    
    def get_gateway_config(self, gateway: PaymentGateway) -> Optional[PaymentGatewayConfig]:
        """Get payment gateway configuration"""
        return self.payment_gateways.get(gateway)
    
    def is_gateway_enabled(self, gateway: PaymentGateway) -> bool:
        """Check if a payment gateway is enabled"""
        config = self.get_gateway_config(gateway)
        return config.enabled if config else False
    
    def get_crypto_config(self, currency: CryptoCurrency) -> Optional[CryptoPaymentConfig]:
        """Get crypto payment configuration"""
        return self.crypto_payments.get(currency)
    
    def is_crypto_enabled(self, currency: CryptoCurrency) -> bool:
        """Check if a cryptocurrency is enabled"""
        config = self.get_crypto_config(currency)
        return config.enabled if config else False
    
    def get_revenue_stream_config(self, stream: RevenueStream) -> Optional[RevenueStreamConfig]:
        """Get revenue stream configuration"""
        return self.revenue_streams.get(stream)
    
    def is_revenue_stream_enabled(self, stream: RevenueStream) -> bool:
        """Check if a revenue stream is enabled"""
        config = self.get_revenue_stream_config(stream)
        return config.enabled if config else False
    
    def get_subscription_config(self, tier: SubscriptionTier) -> Optional[SubscriptionConfig]:
        """Get subscription tier configuration"""
        return self.subscription_tiers.get(tier)
    
    def get_commission_rate(self, stream: RevenueStream) -> float:
        """Get commission rate for a revenue stream"""
        config = self.get_revenue_stream_config(stream)
        return config.commission_rate if config else 0.0
    
    def get_minimum_payout(self, stream: RevenueStream) -> float:
        """Get minimum payout threshold for a revenue stream"""
        config = self.get_revenue_stream_config(stream)
        return config.minimum_payout if config else 0.0
    
    def get_enabled_payment_methods(self) -> List[PaymentMethod]:
        """Get list of enabled payment methods"""
        methods = []
        
        # Check traditional payment gateways
        for gateway, config in self.payment_gateways.items():
            if config.enabled:
                if gateway in [PaymentGateway.STRIPE, PaymentGateway.PAYPAL]:
                    methods.extend([PaymentMethod.CARD, PaymentMethod.DIGITAL_WALLET])
                if gateway == PaymentGateway.WISE:
                    methods.append(PaymentMethod.BANK_TRANSFER)
        
        # Check crypto payments
        for currency, config in self.crypto_payments.items():
            if config.enabled:
                methods.append(PaymentMethod.CRYPTO)
                break
        
        return list(set(methods))
    
    def calculate_total_fees(self, amount: float, gateway: PaymentGateway, stream: RevenueStream) -> Dict[str, float]:
        """Calculate total fees for a transaction"""
        gateway_config = self.get_gateway_config(gateway)
        stream_config = self.get_revenue_stream_config(stream)
        
        if not gateway_config or not stream_config:
            return {"error": "Invalid gateway or stream"}
        
        gateway_fee = amount * (gateway_config.transaction_fee_percentage / 100)
        commission_fee = amount * stream_config.commission_rate
        net_amount = amount - gateway_fee - commission_fee
        
        return {
            "gross_amount": amount,
            "gateway_fee": gateway_fee,
            "commission_fee": commission_fee,
            "net_amount": net_amount,
            "total_fees": gateway_fee + commission_fee
        }
    
    def validate_configuration(self) -> List[str]:
        """Validate the complete monetization configuration"""
        errors = []
        
        # Validate payment gateways
        enabled_gateways = [g for g, c in self.payment_gateways.items() if c.enabled]
        if not enabled_gateways:
            errors.append("No payment gateways enabled")
        
        # Validate revenue streams
        enabled_streams = [s for s, c in self.revenue_streams.items() if c.enabled]
        if not enabled_streams:
            errors.append("No revenue streams enabled")
        
        # Validate subscription tiers
        if not self.subscription_tiers:
            errors.append("No subscription tiers configured")
        
        # Validate commission rates
        for stream, config in self.revenue_streams.items():
            if config.commission_rate < 0 or config.commission_rate > 1:
                errors.append(f"Invalid commission rate for {stream}: {config.commission_rate}")
        
        # Validate minimum payouts
        for stream, config in self.revenue_streams.items():
            if config.minimum_payout < 0:
                errors.append(f"Invalid minimum payout for {stream}: {config.minimum_payout}")
        
        # Validate subscription prices
        for tier, config in self.subscription_tiers.items():
            if config.price_usd <= 0:
                errors.append(f"Invalid price for subscription tier {tier}: {config.price_usd}")
        
        return errors


# Global monetization business settings instance
monetization_business_settings = MonetizationBusinessSettings()

__all__ = [
    "MonetizationBusinessSettings",
    "monetization_business_settings",
    "PaymentGateway",
    "CryptoCurrency",
    "RevenueStream",
    "SubscriptionTier",
    "BillingCycle",
    "PaymentMethod",
    "PaymentGatewayConfig",
    "RevenueStreamConfig",
    "SubscriptionConfig",
    "CryptoPaymentConfig"
]