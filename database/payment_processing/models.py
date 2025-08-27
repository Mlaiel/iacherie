"""
Payment Processing Database Models - Enterprise Grade

Advanced database models for payment processing, billing management,
financial transactions, revenue tracking, and automated payouts
in the IA Influencer Agent platform.

Author: Fahed Mlaiel <mlaiel@live.de>
Team: Lead AI Developer + Backend Senior + ML Engineer + DBA + Security Expert + 
      Payment Systems Architect + Financial Technology Specialist + DevOps Engineer + 
      Microservices Expert + Audio Processing Engineer
Project: IA Influencer Agent + Content Protection Platform

Copyright: All rights reserved. Unauthorized use, modification, or distribution prohibited.
WARNING: This code is proprietary and confidential. Any unauthorized use, modification,
or distribution is strictly prohibited and may result in legal action.
Contact: mlaiel@live.de for licensing inquiries.

ENTERPRISE FEATURES:
- Multi-gateway payment processing with automatic failover
- Real-time revenue tracking with ML-powered analytics
- Automated payout distribution with intelligent scheduling
- Advanced fraud detection with behavioral analysis
- Multi-currency support with dynamic exchange rates
- Blockchain integration for secure transactions
- AI-powered financial forecasting and optimization
- Comprehensive audit logging and compliance tracking
- International tax calculation and reporting
- Advanced dispute management and resolution
"""

from sqlalchemy import (
    Column, Integer, String, DateTime, Decimal, Boolean, Text, 
    ForeignKey, Index, CheckConstraint, UniqueConstraint, JSON,
    BigInteger, Float, TIMESTAMP, Interval, ARRAY as SQLArray
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, validates
from sqlalchemy.dialects.postgresql import UUID, JSONB, ARRAY, INET, ENUM
from datetime import datetime, timezone, timedelta
from decimal import Decimal as PyDecimal
from enum import Enum
import uuid
from typing import Dict, Any, Optional, List, Union
import logging

logger = logging.getLogger(__name__)

Base = declarative_base()


class PaymentStatus(Enum):
    """Payment transaction status enumeration with comprehensive states"""
    CREATED = "created"
    PENDING = "pending"
    AUTHORIZED = "authorized"
    CAPTURED = "captured"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    EXPIRED = "expired"
    REFUNDED = "refunded"
    PARTIALLY_REFUNDED = "partially_refunded"
    DISPUTED = "disputed"
    CHARGEBACK = "chargeback"
    UNDER_REVIEW = "under_review"
    REQUIRES_ACTION = "requires_action"


class PaymentMethodType(Enum):
    """Comprehensive payment method types for global coverage"""
    # Card payments
    CREDIT_CARD = "credit_card"
    DEBIT_CARD = "debit_card"
    PREPAID_CARD = "prepaid_card"
    
    # Digital wallets
    PAYPAL = "paypal"
    APPLE_PAY = "apple_pay"
    GOOGLE_PAY = "google_pay"
    SAMSUNG_PAY = "samsung_pay"
    AMAZON_PAY = "amazon_pay"
    
    # Bank transfers
    BANK_TRANSFER = "bank_transfer"
    SEPA = "sepa"
    ACH = "ach"
    WIRE_TRANSFER = "wire_transfer"
    SWIFT = "swift"
    
    # Alternative payment methods
    PAYPAL_CREDIT = "paypal_credit"
    KLARNA = "klarna"
    AFTERPAY = "afterpay"
    AFFIRM = "affirm"
    SOFORT = "sofort"
    GIROPAY = "giropay"
    IDEAL = "ideal"
    BANCONTACT = "bancontact"
    EPS = "eps"
    P24 = "p24"
    ALIPAY = "alipay"
    WECHAT_PAY = "wechat_pay"
    
    # Cryptocurrency
    BITCOIN = "bitcoin"
    ETHEREUM = "ethereum"
    LITECOIN = "litecoin"
    RIPPLE = "ripple"
    BITCOIN_CASH = "bitcoin_cash"
    TETHER = "tether"
    BINANCE_COIN = "binance_coin"
    CARDANO = "cardano"
    DOGECOIN = "dogecoin"
    POLYGON = "polygon"
    
    # Buy now pay later
    SEZZLE = "sezzle"
    QUADPAY = "quadpay"
    SPLITIT = "splitit"
    
    # Regional payment methods
    PIX = "pix"  # Brazil
    BLIK = "blik"  # Poland
    MULTIBANCO = "multibanco"  # Portugal
    MYBANK = "mybank"  # Italy
    TRUSTLY = "trustly"  # Nordics
    PRZELEWY24 = "przelewy24"  # Poland


class PaymentProvider(Enum):
    """Enterprise payment providers with global coverage"""
    # Major gateways
    STRIPE = "stripe"
    PAYPAL = "paypal"
    SQUARE = "square"
    ADYEN = "adyen"
    WORLDPAY = "worldpay"
    BRAINTREE = "braintree"
    CHECKOUT_COM = "checkout_com"
    
    # Regional providers
    RAZORPAY = "razorpay"  # India
    MERCADOPAGO = "mercadopago"  # Latin America
    PAYU = "payu"  # Global
    FLUTTERWAVE = "flutterwave"  # Africa
    PAYSTACK = "paystack"  # Africa
    MOLLIE = "mollie"  # Europe
    KLARNA = "klarna"  # Europe/US
    
    # Cryptocurrency
    COINBASE = "coinbase"
    BINANCE = "binance"
    BITPAY = "bitpay"
    COINGATE = "coingate"
    
    # Banking/Transfer
    WISE = "wise"
    REMITLY = "remitly"
    TRANSFERGO = "transfergo"
    
    # Alternative
    AMAZON_PAYMENTS = "amazon_payments"
    APPLE_PAY_DIRECT = "apple_pay_direct"
    GOOGLE_PAY_DIRECT = "google_pay_direct"


class TransactionType(Enum):
    """Comprehensive transaction types for financial operations"""
    # Revenue transactions
    PAYMENT = "payment"
    SUBSCRIPTION = "subscription"
    ONE_TIME_PAYMENT = "one_time_payment"
    RECURRING_PAYMENT = "recurring_payment"
    
    # Payouts
    PAYOUT = "payout"
    INSTANT_PAYOUT = "instant_payout"
    SCHEDULED_PAYOUT = "scheduled_payout"
    BULK_PAYOUT = "bulk_payout"
    
    # Reversals
    REFUND = "refund"
    PARTIAL_REFUND = "partial_refund"
    CHARGEBACK = "chargeback"
    DISPUTE = "dispute"
    
    # Fees and commissions
    PLATFORM_FEE = "platform_fee"
    PROCESSING_FEE = "processing_fee"
    COMMISSION = "commission"
    REVENUE_SHARE = "revenue_share"
    
    # Content monetization
    ROYALTY = "royalty"
    STREAMING_REVENUE = "streaming_revenue"
    AD_REVENUE = "ad_revenue"
    SPONSORSHIP = "sponsorship"
    BRAND_DEAL = "brand_deal"
    MERCHANDISE = "merchandise"
    
    # Adjustments
    BONUS = "bonus"
    PENALTY = "penalty"
    ADJUSTMENT = "adjustment"
    CORRECTION = "correction"
    
    # Cryptocurrency
    CRYPTO_DEPOSIT = "crypto_deposit"
    CRYPTO_WITHDRAWAL = "crypto_withdrawal"
    CRYPTO_CONVERSION = "crypto_conversion"


class PayoutStatus(Enum):
    """Comprehensive payout status tracking"""
    CREATED = "created"
    PENDING = "pending"
    SCHEDULED = "scheduled"
    QUEUED = "queued"
    PROCESSING = "processing"
    IN_TRANSIT = "in_transit"
    SENT = "sent"
    DELIVERED = "delivered"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    RETURNED = "returned"
    REJECTED = "rejected"
    UNDER_REVIEW = "under_review"
    REQUIRES_VERIFICATION = "requires_verification"


class BillingFrequency(Enum):
    """Flexible billing frequency options"""
    ONE_TIME = "one_time"
    DAILY = "daily"
    WEEKLY = "weekly"
    BIWEEKLY = "biweekly"
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    SEMIANNUALLY = "semiannually"
    ANNUALLY = "annually"
    CUSTOM = "custom"


class CurrencyCode(Enum):
    """Comprehensive global currency support"""
    # Major Fiat Currencies
    USD = "USD"  # US Dollar
    EUR = "EUR"  # Euro
    GBP = "GBP"  # British Pound
    JPY = "JPY"  # Japanese Yen
    CAD = "CAD"  # Canadian Dollar
    AUD = "AUD"  # Australian Dollar
    CHF = "CHF"  # Swiss Franc
    CNY = "CNY"  # Chinese Yuan
    SEK = "SEK"  # Swedish Krona
    NOK = "NOK"  # Norwegian Krone
    DKK = "DKK"  # Danish Krone
    PLN = "PLN"  # Polish Zloty
    CZK = "CZK"  # Czech Koruna
    HUF = "HUF"  # Hungarian Forint
    RON = "RON"  # Romanian Leu
    BGN = "BGN"  # Bulgarian Lev
    HRK = "HRK"  # Croatian Kuna
    
    # Asian Currencies
    SGD = "SGD"  # Singapore Dollar
    HKD = "HKD"  # Hong Kong Dollar
    TWD = "TWD"  # Taiwan Dollar
    KRW = "KRW"  # South Korean Won
    THB = "THB"  # Thai Baht
    MYR = "MYR"  # Malaysian Ringgit
    IDR = "IDR"  # Indonesian Rupiah
    PHP = "PHP"  # Philippine Peso
    VND = "VND"  # Vietnamese Dong
    INR = "INR"  # Indian Rupee
    PKR = "PKR"  # Pakistani Rupee
    BDT = "BDT"  # Bangladeshi Taka
    LKR = "LKR"  # Sri Lankan Rupee
    
    # Middle East & Africa
    AED = "AED"  # UAE Dirham
    SAR = "SAR"  # Saudi Riyal
    QAR = "QAR"  # Qatari Riyal
    KWD = "KWD"  # Kuwaiti Dinar
    BHD = "BHD"  # Bahraini Dinar
    OMR = "OMR"  # Omani Rial
    JOD = "JOD"  # Jordanian Dinar
    LBP = "LBP"  # Lebanese Pound
    ILS = "ILS"  # Israeli Shekel
    EGP = "EGP"  # Egyptian Pound
    ZAR = "ZAR"  # South African Rand
    NGN = "NGN"  # Nigerian Naira
    KES = "KES"  # Kenyan Shilling
    GHS = "GHS"  # Ghanaian Cedi
    
    # Latin America
    BRL = "BRL"  # Brazilian Real
    MXN = "MXN"  # Mexican Peso
    ARS = "ARS"  # Argentine Peso
    CLP = "CLP"  # Chilean Peso
    COP = "COP"  # Colombian Peso
    PEN = "PEN"  # Peruvian Sol
    UYU = "UYU"  # Uruguayan Peso
    
    # Cryptocurrencies
    BTC = "BTC"   # Bitcoin
    ETH = "ETH"   # Ethereum
    LTC = "LTC"   # Litecoin
    XRP = "XRP"   # Ripple
    BCH = "BCH"   # Bitcoin Cash
    USDT = "USDT" # Tether
    USDC = "USDC" # USD Coin
    BNB = "BNB"   # Binance Coin
    ADA = "ADA"   # Cardano
    DOT = "DOT"   # Polkadot
    DOGE = "DOGE" # Dogecoin
    MATIC = "MATIC" # Polygon


class FraudRisk(Enum):
    """Fraud risk assessment levels"""
    VERY_LOW = "very_low"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    VERY_HIGH = "very_high"
    CRITICAL = "critical"


class SecurityLevel(Enum):
    """Security level classifications"""
    BASIC = "basic"
    STANDARD = "standard"
    ENHANCED = "enhanced"
    PREMIUM = "premium"
    ENTERPRISE = "enterprise"


class ComplianceStatus(Enum):
    """Compliance status for regulatory requirements"""
    COMPLIANT = "compliant"
    PENDING_REVIEW = "pending_review"
    NON_COMPLIANT = "non_compliant"
    UNDER_INVESTIGATION = "under_investigation"
    EXEMPTED = "exempted"


class RevenueSource(Enum):
    """Revenue source classification for analytics"""
    YOUTUBE_ADS = "youtube_ads"
    YOUTUBE_PREMIUM = "youtube_premium"
    YOUTUBE_MEMBERSHIPS = "youtube_memberships"
    YOUTUBE_SUPER_CHAT = "youtube_super_chat"
    YOUTUBE_SUPER_THANKS = "youtube_super_thanks"
    
    INSTAGRAM_REELS_BONUS = "instagram_reels_bonus"
    INSTAGRAM_BRAND_PARTNERSHIPS = "instagram_brand_partnerships"
    INSTAGRAM_SHOPPING = "instagram_shopping"
    INSTAGRAM_SUBSCRIPTIONS = "instagram_subscriptions"
    
    TIKTOK_CREATOR_FUND = "tiktok_creator_fund"
    TIKTOK_LIVE_GIFTS = "tiktok_live_gifts"
    TIKTOK_BRAND_PARTNERSHIPS = "tiktok_brand_partnerships"
    
    SPOTIFY_STREAMS = "spotify_streams"
    SPOTIFY_PODCASTS = "spotify_podcasts"
    
    TWITCH_SUBSCRIPTIONS = "twitch_subscriptions"
    TWITCH_BITS = "twitch_bits"
    TWITCH_ADS = "twitch_ads"
    
    BRAND_SPONSORSHIPS = "brand_sponsorships"
    AFFILIATE_MARKETING = "affiliate_marketing"
    MERCHANDISE_SALES = "merchandise_sales"
    DIGITAL_PRODUCTS = "digital_products"
    COURSES_EDUCATION = "courses_education"
    CONSULTING_SERVICES = "consulting_services"
    
    PLATFORM_COMMISSION = "platform_commission"
    REFERRAL_BONUS = "referral_bonus"
    OTHER = "other"


class TaxCategory(Enum):
    """Tax categories for international compliance"""
    PERSONAL_INCOME = "personal_income"
    BUSINESS_INCOME = "business_income"
    CAPITAL_GAINS = "capital_gains"
    ROYALTIES = "royalties"
    FREELANCE_INCOME = "freelance_income"
    DIGITAL_SERVICES = "digital_services"
    ENTERTAINMENT = "entertainment"
    EXEMPT = "exempt"
    PENDING = "pending"
    PROCESSING = "processing"
    AUTHORIZED = "authorized"
    CAPTURED = "captured"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    REFUNDED = "refunded"
    PARTIAL_REFUND = "partial_refund"
    DISPUTED = "disputed"
    CHARGEBACK = "chargeback"
    EXPIRED = "expired"
    DECLINED = "declined"


class PaymentMethodType(Enum):
    """Payment method type enumeration"""
    CREDIT_CARD = "credit_card"
    DEBIT_CARD = "debit_card"
    BANK_TRANSFER = "bank_transfer"
    SEPA_TRANSFER = "sepa_transfer"
    WIRE_TRANSFER = "wire_transfer"
    PAYPAL = "paypal"
    STRIPE = "stripe"
    WISE = "wise"
    CRYPTOCURRENCY = "cryptocurrency"
    BITCOIN = "bitcoin"
    ETHEREUM = "ethereum"
    APPLE_PAY = "apple_pay"
    GOOGLE_PAY = "google_pay"
    SAMSUNG_PAY = "samsung_pay"
    KLARNA = "klarna"
    SOFORT = "sofort"
    GIROPAY = "giropay"
    IDEAL = "ideal"
    BANCONTACT = "bancontact"


class PaymentProvider(Enum):
    """Payment provider enumeration"""
    STRIPE = "stripe"
    PAYPAL = "paypal"
    WISE = "wise"
    COINBASE = "coinbase"
    BINANCE = "binance"
    SQUARE = "square"
    ADYEN = "adyen"
    WORLDPAY = "worldpay"
    BRAINTREE = "braintree"
    RAZORPAY = "razorpay"


class TransactionType(Enum):
    """Transaction type enumeration"""
    PAYMENT = "payment"
    PAYOUT = "payout"
    REFUND = "refund"
    CHARGEBACK = "chargeback"
    FEE = "fee"
    COMMISSION = "commission"
    ROYALTY = "royalty"
    BONUS = "bonus"
    PENALTY = "penalty"
    ADJUSTMENT = "adjustment"


class PayoutStatus(Enum):
    """Payout status enumeration"""
    PENDING = "pending"
    SCHEDULED = "scheduled"
    PROCESSING = "processing"
    SENT = "sent"
    DELIVERED = "delivered"
    FAILED = "failed"
    CANCELLED = "cancelled"
    RETURNED = "returned"


class BillingFrequency(Enum):
    """Billing frequency enumeration"""
    ONE_TIME = "one_time"
    DAILY = "daily"
    WEEKLY = "weekly"
    BIWEEKLY = "biweekly"
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    SEMIANNUALLY = "semiannually"
    ANNUALLY = "annually"
    CUSTOM = "custom"


class CurrencyCode(Enum):
    """Supported currency codes"""
    # Major Fiat Currencies
    USD = "USD"  # US Dollar
    EUR = "EUR"  # Euro
    GBP = "GBP"  # British Pound
    JPY = "JPY"  # Japanese Yen
    CAD = "CAD"  # Canadian Dollar
    AUD = "AUD"  # Australian Dollar
    CHF = "CHF"  # Swiss Franc
    CNY = "CNY"  # Chinese Yuan
    SEK = "SEK"  # Swedish Krona
    NOK = "NOK"  # Norwegian Krone
    DKK = "DKK"  # Danish Krone
    PLN = "PLN"  # Polish Zloty
    CZK = "CZK"  # Czech Koruna
    HUF = "HUF"  # Hungarian Forint
    # Cryptocurrencies
    BTC = "BTC"  # Bitcoin
    ETH = "ETH"  # Ethereum
    USDC = "USDC"  # USD Coin
    USDT = "USDT"  # Tether
    BNB = "BNB"  # Binance Coin
    ADA = "ADA"  # Cardano
    DOT = "DOT"  # Polkadot
    MATIC = "MATIC"  # Polygon


class FraudRisk(Enum):
    """Fraud risk level enumeration"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class SecurityLevel(Enum):
    """Security level enumeration"""
    BASIC = "basic"
    ENHANCED = "enhanced"
    PREMIUM = "premium"
    ENTERPRISE = "enterprise"


class PaymentTransaction(Base):
    """
    Payment transactions model for tracking all financial transactions
    """
    __tablename__ = "payment_transactions"
    
    # Primary identifiers
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    content_id = Column(UUID(as_uuid=True), ForeignKey("contents.id"), nullable=True, index=True)
    payment_method_id = Column(UUID(as_uuid=True), ForeignKey("payment_methods.id"), nullable=True)
    
    # Transaction details
    transaction_type = Column(String(50), nullable=False, index=True)
    amount = Column(Decimal(15, 4), nullable=False)
    original_amount = Column(Decimal(15, 4), nullable=True)  # Before fees/conversions
    currency = Column(String(10), nullable=False, default="EUR")
    exchange_rate = Column(Decimal(10, 6), nullable=True)
    status = Column(String(20), nullable=False, default="pending", index=True)
    
    # External gateway references
    gateway_transaction_id = Column(String(255), nullable=True, index=True)
    gateway_reference = Column(String(255), nullable=True)
    provider = Column(String(50), nullable=True)
    gateway_status = Column(String(50), nullable=True)
    
    # Fee structure
    platform_fee = Column(Decimal(15, 4), nullable=True, default=0)
    gateway_fee = Column(Decimal(15, 4), nullable=True, default=0)
    processing_fee = Column(Decimal(15, 4), nullable=True, default=0)
    net_amount = Column(Decimal(15, 4), nullable=True)
    
    # Revenue tracking for content creators
    content_revenue = Column(Decimal(15, 4), nullable=True, default=0)
    platform_commission = Column(Decimal(15, 4), nullable=True, default=0)
    creator_earnings = Column(Decimal(15, 4), nullable=True, default=0)
    
    # Metadata and tracking
    description = Column(Text, nullable=True)
    reference_number = Column(String(100), unique=True, nullable=True, index=True)
    invoice_number = Column(String(100), nullable=True, index=True)
    
    # Security and fraud detection
    risk_score = Column(Integer, nullable=True, default=0)
    fraud_flags = Column(JSONB, nullable=True)
    ip_address = Column(INET, nullable=True)
    device_fingerprint = Column(String(255), nullable=True)
    geo_location = Column(JSONB, nullable=True)
    
    # Timestamps
    created_at = Column(TIMESTAMP(timezone=True), default=datetime.utcnow, nullable=False, index=True)
    updated_at = Column(TIMESTAMP(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)
    processed_at = Column(TIMESTAMP(timezone=True), nullable=True)
    settled_at = Column(TIMESTAMP(timezone=True), nullable=True)
    
    # Additional metadata
    metadata = Column(JSONB, nullable=True)
    tags = Column(ARRAY(String), nullable=True)
    notes = Column(Text, nullable=True)
    
    # Relationships
    payment_method = relationship("PaymentMethod", back_populates="transactions")
    billing_records = relationship("BillingRecord", back_populates="transaction")
    financial_records = relationship("FinancialRecord", back_populates="transaction")
    
    __table_args__ = (
        Index('idx_payment_transaction_user_status', 'user_id', 'status'),
        Index('idx_payment_transaction_created_status', 'created_at', 'status'),
        Index('idx_payment_transaction_amount_currency', 'amount', 'currency'),
        Index('idx_payment_transaction_type_status', 'transaction_type', 'status'),
        CheckConstraint('amount > 0', name='check_positive_amount'),
        CheckConstraint('platform_fee >= 0', name='check_positive_platform_fee'),
        CheckConstraint('gateway_fee >= 0', name='check_positive_gateway_fee'),
    )
    external_transaction_id = Column(String(255), nullable=True, index=True)
    platform_reference = Column(String(100), nullable=True)  # stripe, paypal, wise
    
    # Financial tracking
    gross_amount = Column(Decimal(15, 2), nullable=False)
    fees_amount = Column(Decimal(15, 2), nullable=False, default=0)
    net_amount = Column(Decimal(15, 2), nullable=False)
    tax_amount = Column(Decimal(15, 2), nullable=False, default=0)
    
    # Processing information
    processor = Column(String(50), nullable=False)  # stripe, paypal, wise
    processor_response = Column(JSONB, nullable=True)
    gateway_reference = Column(String(255), nullable=True)
    
    # Content monetization linking
    content_id = Column(Integer, ForeignKey("content_fingerprints.id"), nullable=True)
    revenue_tracking_id = Column(Integer, ForeignKey("revenue_tracking.id"), nullable=True)
    
    # Metadata and context
    description = Column(Text, nullable=True)
    metadata = Column(JSONB, nullable=True)
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(Text, nullable=True)
    
    # Timestamps
    initiated_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)
    processed_at = Column(DateTime(timezone=True), nullable=True)
    settled_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    payment_method = relationship("PaymentMethod", back_populates="transactions")
    billing_records = relationship("BillingRecord", back_populates="transaction")
    
    # Constraints
    __table_args__ = (
        CheckConstraint('amount > 0', name='check_amount_positive'),
        CheckConstraint('gross_amount >= net_amount', name='check_gross_net_amount'),
        Index('idx_payment_transactions_user_status', 'user_id', 'status'),
        Index('idx_payment_transactions_created_at', 'created_at'),
        Index('idx_payment_transactions_external_id', 'external_transaction_id'),
    )
    
    @validates('status')
    def validate_status(self, key, status):
        valid_statuses = [s.value for s in PaymentStatus]
        if status not in valid_statuses:
            raise ValueError(f"Invalid status: {status}")
        return status
    
    @validates('currency')
    def validate_currency(self, key, currency):
        valid_currencies = [c.value for c in CurrencyCode]
        if currency not in valid_currencies:
            raise ValueError(f"Invalid currency: {currency}")
        return currency
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert transaction to dictionary"""
        return {
            "id": str(self.id),
            "user_id": self.user_id,
            "transaction_type": self.transaction_type,
            "amount": float(self.amount),
            "currency": self.currency,
            "status": self.status,
            "processor": self.processor,
            "created_at": self.created_at.isoformat(),
            "processed_at": self.processed_at.isoformat() if self.processed_at else None,
        }


class PaymentMethod(Base):
    """
    Payment methods model for storing user payment information
    """
    __tablename__ = "payment_methods"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    
    # Method details
    method_type = Column(String(50), nullable=False)
    provider = Column(String(50), nullable=False)  # stripe, paypal, wise
    external_id = Column(String(255), nullable=True)  # provider's ID
    
    # Card/Bank details (encrypted)
    last_four_digits = Column(String(4), nullable=True)
    brand = Column(String(50), nullable=True)  # visa, mastercard, etc.
    exp_month = Column(Integer, nullable=True)
    exp_year = Column(Integer, nullable=True)
    
    # Bank account details
    bank_name = Column(String(255), nullable=True)
    account_type = Column(String(50), nullable=True)
    routing_number_last_four = Column(String(4), nullable=True)
    
    # Status and verification
    is_active = Column(Boolean, nullable=False, default=True)
    is_verified = Column(Boolean, nullable=False, default=False)
    is_default = Column(Boolean, nullable=False, default=False)
    
    # Security and compliance
    fingerprint = Column(String(255), nullable=True)
    billing_address = Column(JSONB, nullable=True)
    verification_data = Column(JSONB, nullable=True)
    
    # Metadata
    nickname = Column(String(100), nullable=True)
    metadata = Column(JSONB, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    verified_at = Column(DateTime(timezone=True), nullable=True)
    last_used_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    transactions = relationship("PaymentTransaction", back_populates="payment_method")
    
    # Constraints
    __table_args__ = (
        Index('idx_payment_methods_user_active', 'user_id', 'is_active'),
        Index('idx_payment_methods_user_default', 'user_id', 'is_default'),
        UniqueConstraint('user_id', 'external_id', 'provider', name='uq_user_external_provider'),
    )
    
    @validates('method_type')
    def validate_method_type(self, key, method_type):
        valid_types = [t.value for t in PaymentMethodType]
        if method_type not in valid_types:
            raise ValueError(f"Invalid method type: {method_type}")
        return method_type


class BillingRecord(Base):
    """
    Billing records model for subscription and recurring payments
    """
    __tablename__ = "billing_records"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    transaction_id = Column(UUID(as_uuid=True), ForeignKey("payment_transactions.id"), nullable=True)
    
    # Billing details
    subscription_type = Column(String(100), nullable=False)
    billing_frequency = Column(String(20), nullable=False)
    amount = Column(Decimal(15, 2), nullable=False)
    currency = Column(String(3), nullable=False, default="EUR")
    
    # Period information
    billing_period_start = Column(DateTime(timezone=True), nullable=False)
    billing_period_end = Column(DateTime(timezone=True), nullable=False)
    due_date = Column(DateTime(timezone=True), nullable=False)
    
    # Status tracking
    status = Column(String(20), nullable=False, default="pending")
    is_prorated = Column(Boolean, nullable=False, default=False)
    proration_details = Column(JSONB, nullable=True)
    
    # Invoice information
    invoice_number = Column(String(100), nullable=True, unique=True)
    invoice_url = Column(String(255), nullable=True)
    tax_details = Column(JSONB, nullable=True)
    
    # Usage-based billing
    usage_metrics = Column(JSONB, nullable=True)
    overage_amount = Column(Decimal(15, 2), nullable=False, default=0)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    billed_at = Column(DateTime(timezone=True), nullable=True)
    paid_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    transaction = relationship("PaymentTransaction", back_populates="billing_records")
    
    # Constraints
    __table_args__ = (
        CheckConstraint('amount > 0', name='check_billing_amount_positive'),
        CheckConstraint('billing_period_end > billing_period_start', name='check_billing_period'),
        Index('idx_billing_records_user_status', 'user_id', 'status'),
        Index('idx_billing_records_due_date', 'due_date'),
        Index('idx_billing_records_period', 'billing_period_start', 'billing_period_end'),
    )


class FinancialRecord(Base):
    """
    Financial records model for comprehensive financial tracking
    """
    __tablename__ = "financial_records"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    
    # Record classification
    record_type = Column(String(50), nullable=False)  # revenue, expense, fee, tax
    category = Column(String(100), nullable=False)
    subcategory = Column(String(100), nullable=True)
    
    # Financial amounts
    amount = Column(Decimal(15, 2), nullable=False)
    currency = Column(String(3), nullable=False, default="EUR")
    exchange_rate = Column(Decimal(10, 6), nullable=True)
    base_currency_amount = Column(Decimal(15, 2), nullable=True)
    
    # Source and reference
    source_platform = Column(String(100), nullable=True)
    reference_id = Column(String(255), nullable=True)
    external_reference = Column(String(255), nullable=True)
    
    # Content monetization link
    content_id = Column(Integer, ForeignKey("content_fingerprints.id"), nullable=True)
    revenue_source = Column(String(100), nullable=True)  # streaming, licensing, collaboration
    
    # Tax and compliance
    tax_category = Column(String(50), nullable=True)
    tax_rate = Column(Decimal(5, 4), nullable=True)
    tax_amount = Column(Decimal(15, 2), nullable=False, default=0)
    is_tax_deductible = Column(Boolean, nullable=False, default=False)
    
    # Period and timing
    transaction_date = Column(DateTime(timezone=True), nullable=False)
    recorded_date = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)
    accounting_period = Column(String(7), nullable=False)  # YYYY-MM format
    
    # Additional data
    description = Column(Text, nullable=True)
    metadata = Column(JSONB, nullable=True)
    supporting_documents = Column(ARRAY(String), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Constraints
    __table_args__ = (
        Index('idx_financial_records_user_type', 'user_id', 'record_type'),
        Index('idx_financial_records_period', 'accounting_period'),
        Index('idx_financial_records_transaction_date', 'transaction_date'),
        Index('idx_financial_records_content', 'content_id'),
    )


class AutomatedPayout(Base):
    """
    Automated payout model for managing creator payments
    """
    __tablename__ = "automated_payouts"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    payment_method_id = Column(UUID(as_uuid=True), ForeignKey("payment_methods.id"), nullable=False)
    
    # Payout configuration
    payout_frequency = Column(String(20), nullable=False)  # weekly, monthly, quarterly
    minimum_amount = Column(Decimal(15, 2), nullable=False, default=50.00)
    currency = Column(String(3), nullable=False, default="EUR")
    
    # Payout details
    total_amount = Column(Decimal(15, 2), nullable=False)
    fees_amount = Column(Decimal(15, 2), nullable=False, default=0)
    net_amount = Column(Decimal(15, 2), nullable=False)
    
    # Period covered
    period_start = Column(DateTime(timezone=True), nullable=False)
    period_end = Column(DateTime(timezone=True), nullable=False)
    
    # Processing status
    status = Column(String(20), nullable=False, default="pending")
    processor = Column(String(50), nullable=False)
    external_payout_id = Column(String(255), nullable=True)
    
    # Revenue breakdown
    revenue_breakdown = Column(JSONB, nullable=True)  # by platform, content type, etc.
    content_items_count = Column(Integer, nullable=False, default=0)
    platforms_count = Column(Integer, nullable=False, default=0)
    
    # Verification and approval
    is_approved = Column(Boolean, nullable=False, default=False)
    approved_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    approved_at = Column(DateTime(timezone=True), nullable=True)
    
    # Processing timestamps
    scheduled_at = Column(DateTime(timezone=True), nullable=False)
    processed_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    
    # Error handling
    retry_count = Column(Integer, nullable=False, default=0)
    last_error = Column(Text, nullable=True)
    error_details = Column(JSONB, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    payment_method = relationship("PaymentMethod")
    
    # Constraints
    __table_args__ = (
        CheckConstraint('total_amount > 0', name='check_payout_amount_positive'),
        CheckConstraint('period_end > period_start', name='check_payout_period'),
        CheckConstraint('retry_count >= 0', name='check_retry_count_non_negative'),
        Index('idx_automated_payouts_user_status', 'user_id', 'status'),
        Index('idx_automated_payouts_scheduled', 'scheduled_at'),
        Index('idx_automated_payouts_period', 'period_start', 'period_end'),
    )


class FinancialRecord(Base):
    """
    Financial records model for comprehensive financial tracking and reporting
    """
    __tablename__ = "financial_records"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    transaction_id = Column(UUID(as_uuid=True), ForeignKey("payment_transactions.id"), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    
    # Financial details
    record_type = Column(String(50), nullable=False, index=True)  # income, expense, fee, tax
    amount = Column(Decimal(15, 4), nullable=False)
    currency = Column(String(10), nullable=False)
    category = Column(String(100), nullable=True, index=True)
    subcategory = Column(String(100), nullable=True)
    
    # Accounting information
    account_code = Column(String(50), nullable=True)
    tax_amount = Column(Decimal(15, 4), nullable=True, default=0)
    tax_rate = Column(Decimal(5, 4), nullable=True)
    net_amount = Column(Decimal(15, 4), nullable=True)
    
    # Reporting periods
    fiscal_year = Column(Integer, nullable=True)
    fiscal_quarter = Column(Integer, nullable=True)
    accounting_period = Column(String(20), nullable=True)
    
    # Metadata
    description = Column(Text, nullable=True)
    reference_number = Column(String(100), nullable=True, index=True)
    
    # Timestamps
    recorded_at = Column(TIMESTAMP(timezone=True), default=datetime.utcnow, nullable=False)
    transaction_date = Column(TIMESTAMP(timezone=True), nullable=False, index=True)
    created_at = Column(TIMESTAMP(timezone=True), default=datetime.utcnow, nullable=False)
    updated_at = Column(TIMESTAMP(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Additional metadata
    metadata = Column(JSONB, nullable=True)
    
    # Relationships
    transaction = relationship("PaymentTransaction", back_populates="financial_records")
    
    __table_args__ = (
        Index('idx_financial_records_user_type', 'user_id', 'record_type'),
        Index('idx_financial_records_date_type', 'transaction_date', 'record_type'),
        Index('idx_financial_records_fiscal', 'fiscal_year', 'fiscal_quarter'),
        CheckConstraint('amount != 0', name='check_non_zero_amount'),
    )


class PaymentAnalytics(Base):
    """
    Payment analytics model for tracking performance metrics and insights
    """
    __tablename__ = "payment_analytics"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True, index=True)
    
    # Analytics dimensions
    metric_type = Column(String(100), nullable=False, index=True)
    metric_name = Column(String(100), nullable=False)
    metric_value = Column(Decimal(20, 4), nullable=False)
    currency = Column(String(10), nullable=True)
    
    # Time dimensions
    period_type = Column(String(20), nullable=False)  # hour, day, week, month, quarter, year
    period_start = Column(TIMESTAMP(timezone=True), nullable=False, index=True)
    period_end = Column(TIMESTAMP(timezone=True), nullable=False, index=True)
    
    # Segmentation
    segment = Column(String(100), nullable=True, index=True)
    category = Column(String(100), nullable=True, index=True)
    region = Column(String(50), nullable=True)
    platform = Column(String(50), nullable=True)
    
    # Statistical data
    count = Column(BigInteger, nullable=True, default=0)
    average = Column(Decimal(15, 4), nullable=True)
    minimum = Column(Decimal(15, 4), nullable=True)
    maximum = Column(Decimal(15, 4), nullable=True)
    standard_deviation = Column(Decimal(15, 4), nullable=True)
    
    # Metadata
    tags = Column(ARRAY(String), nullable=True)
    metadata = Column(JSONB, nullable=True)
    
    # Timestamps
    calculated_at = Column(TIMESTAMP(timezone=True), default=datetime.utcnow, nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), default=datetime.utcnow, nullable=False)
    
    __table_args__ = (
        Index('idx_payment_analytics_metric_period', 'metric_type', 'period_start', 'period_end'),
        Index('idx_payment_analytics_user_metric', 'user_id', 'metric_type'),
        Index('idx_payment_analytics_segment', 'segment', 'category'),
        UniqueConstraint('metric_type', 'period_start', 'period_end', 'user_id', 'segment', 
                        name='uq_analytics_metric_period_user_segment'),
    )


class RevenueTracking(Base):
    """
    Revenue tracking model for detailed income monitoring per content and platform
    """
    __tablename__ = "revenue_tracking"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    content_id = Column(UUID(as_uuid=True), ForeignKey("contents.id"), nullable=True, index=True)
    
    # Revenue source details
    revenue_source = Column(String(100), nullable=False, index=True)  # youtube, instagram, spotify, etc.
    platform_id = Column(String(100), nullable=True)
    content_type = Column(String(50), nullable=True)  # video, audio, image, post
    
    # Financial data
    gross_revenue = Column(Decimal(15, 4), nullable=False)
    platform_fee = Column(Decimal(15, 4), nullable=True, default=0)
    our_commission = Column(Decimal(15, 4), nullable=True, default=0)
    net_revenue = Column(Decimal(15, 4), nullable=False)
    currency = Column(String(10), nullable=False, default="EUR")
    
    # Performance metrics
    views = Column(BigInteger, nullable=True, default=0)
    clicks = Column(BigInteger, nullable=True, default=0)
    conversions = Column(BigInteger, nullable=True, default=0)
    engagement_rate = Column(Decimal(5, 4), nullable=True)
    cpm = Column(Decimal(10, 4), nullable=True)  # Cost per mille
    cpc = Column(Decimal(10, 4), nullable=True)  # Cost per click
    
    # Time tracking
    tracking_period_start = Column(TIMESTAMP(timezone=True), nullable=False, index=True)
    tracking_period_end = Column(TIMESTAMP(timezone=True), nullable=False, index=True)
    
    # Metadata
    external_reference = Column(String(255), nullable=True, index=True)
    metadata = Column(JSONB, nullable=True)
    
    # Timestamps
    created_at = Column(TIMESTAMP(timezone=True), default=datetime.utcnow, nullable=False)
    updated_at = Column(TIMESTAMP(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)
    
    __table_args__ = (
        Index('idx_revenue_tracking_user_source', 'user_id', 'revenue_source'),
        Index('idx_revenue_tracking_period', 'tracking_period_start', 'tracking_period_end'),
        Index('idx_revenue_tracking_content_source', 'content_id', 'revenue_source'),
        CheckConstraint('gross_revenue >= 0', name='check_positive_gross_revenue'),
        CheckConstraint('net_revenue >= 0', name='check_positive_net_revenue'),
    )


class PaymentWebhook(Base):
    """
    Payment webhook model for tracking external payment provider notifications
    """
    __tablename__ = "payment_webhooks"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Webhook source
    provider = Column(String(50), nullable=False, index=True)
    webhook_id = Column(String(255), nullable=True, index=True)
    event_type = Column(String(100), nullable=False, index=True)
    
    # Processing status
    status = Column(String(20), nullable=False, default="pending", index=True)
    processed_at = Column(TIMESTAMP(timezone=True), nullable=True)
    error_message = Column(Text, nullable=True)
    retry_count = Column(Integer, nullable=False, default=0)
    
    # Webhook data
    payload = Column(JSONB, nullable=False)
    headers = Column(JSONB, nullable=True)
    signature = Column(String(500), nullable=True)
    
    # Security validation
    is_verified = Column(Boolean, nullable=False, default=False)
    verification_method = Column(String(50), nullable=True)
    ip_address = Column(INET, nullable=True)
    
    # Related entities
    transaction_id = Column(UUID(as_uuid=True), ForeignKey("payment_transactions.id"), nullable=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True, index=True)
    
    # Timestamps
    received_at = Column(TIMESTAMP(timezone=True), default=datetime.utcnow, nullable=False, index=True)
    created_at = Column(TIMESTAMP(timezone=True), default=datetime.utcnow, nullable=False)
    updated_at = Column(TIMESTAMP(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Metadata
    metadata = Column(JSONB, nullable=True)
    
    __table_args__ = (
        Index('idx_payment_webhooks_provider_event', 'provider', 'event_type'),
        Index('idx_payment_webhooks_status_received', 'status', 'received_at'),
        Index('idx_payment_webhooks_transaction', 'transaction_id'),
    )


class PaymentConfiguration(Base):
    """
    Payment configuration model for storing payment gateway settings and preferences
    """
    __tablename__ = "payment_configurations"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True, index=True)
    
    # Configuration details
    config_type = Column(String(50), nullable=False, index=True)  # gateway, fee, limit, etc.
    provider = Column(String(50), nullable=True, index=True)
    environment = Column(String(20), nullable=False, default="production")  # sandbox, production
    
    # Settings
    settings = Column(JSONB, nullable=False)
    is_active = Column(Boolean, nullable=False, default=True)
    is_default = Column(Boolean, nullable=False, default=False)
    
    # Security
    encrypted_keys = Column(Text, nullable=True)  # Encrypted API keys
    webhook_secret = Column(String(500), nullable=True)
    
    # Validation
    last_validated = Column(TIMESTAMP(timezone=True), nullable=True)
    validation_status = Column(String(20), nullable=True)
    validation_errors = Column(JSONB, nullable=True)
    
    # Timestamps
    created_at = Column(TIMESTAMP(timezone=True), default=datetime.utcnow, nullable=False)
    updated_at = Column(TIMESTAMP(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Metadata
    metadata = Column(JSONB, nullable=True)
    
    __table_args__ = (
        Index('idx_payment_config_type_provider', 'config_type', 'provider'),
        Index('idx_payment_config_user_active', 'user_id', 'is_active'),
        UniqueConstraint('user_id', 'config_type', 'provider', name='uq_user_config_provider'),
    )


# Utility functions for model operations
def create_all_tables(engine):
    """Create all payment processing tables"""
    Base.metadata.create_all(bind=engine)
    logger.info("Payment processing database tables created successfully")


def get_table_names() -> List[str]:
    """Get list of all table names in this module"""
    return [table.name for table in Base.metadata.tables.values()]


def validate_financial_data(amount: PyDecimal, currency: str) -> bool:
    """Validate financial data consistency"""
    if amount <= 0:
        return False
    if currency not in [c.value for c in CurrencyCode]:
        return False
    return True
