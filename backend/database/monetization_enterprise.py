"""💰 Monetization & Revenue Enterprise Database Module - Ultra-Advanced Revenue Systems
=========================================================================================
Module: backend/database/monetization_enterprise.py
Author: Fahed Mlaiel (mlaiel@live.de)
Team: Lead Dev IA + Backend Senior + ML Engineer + DBA + Security + Microservices + Audio + DevOps + IA Prompt Engineer
Type: Consolidated Monetization & Revenue Database - Ultra Enterprise Production-Ready
Responsibility: Multi-platform revenue tracking, payment processing, and AI-powered monetization optimization
====================================================================================================

⚠️  EXCLUSIVE INTELLECTUAL PROPERTY - FAHED MLAIEL ⚠️
(c) 2025 Fahed Mlaiel. All rights reserved.
Unauthorized use strictly prohibited and subject to legal prosecution.
Contact: mlaiel@live.de

This consolidated module provides comprehensive database schemas and operations for:
- Real-time revenue tracking across multiple platforms
- AI-powered monetization strategy optimization
- Multi-provider payment processing
- Subscription and recurring payment management
- Cryptocurrency transaction handling
- Tax compliance and multi-jurisdiction reporting
- Dynamic pricing optimization with ML

BUSINESS LOGIC INTEGRATION:
Content Distribution → Revenue Generation → Payment Processing → Tax Compliance → Optimization
"""

from sqlalchemy import Column, String, Text, DateTime, Float, Integer, Boolean, JSON, ForeignKey, Index, Enum as SQLEnum, Numeric, BigInteger
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID, ARRAY, JSONB, MONEY
from datetime import datetime, timezone
from enum import Enum
from typing import Optional, Dict, Any, List
from decimal import Decimal
import uuid
import logging

logger = logging.getLogger(__name__)

# Create independent declarative base to avoid conflicts
from sqlalchemy.ext.declarative import declarative_base
Base = declarative_base()


# ================================
# ENUMERATIONS
# ================================

class RevenueSource(Enum):
    """Revenue source types."""
    STREAMING = "streaming"
    DOWNLOADS = "downloads"
    LICENSING = "licensing"
    MERCHANDISE = "merchandise"
    LIVE_PERFORMANCES = "live_performances"
    SUBSCRIPTIONS = "subscriptions"
    ADVERTISING = "advertising"
    TIPS_DONATIONS = "tips_donations"
    NFT_SALES = "nft_sales"
    CRYPTO_REWARDS = "crypto_rewards"
    COLLABORATION = "collaboration"
    REMIX_RIGHTS = "remix_rights"


class PaymentStatus(Enum):
    """Payment processing status."""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    REFUNDED = "refunded"
    DISPUTED = "disputed"
    CHARGEBACK = "chargeback"


class PaymentMethod(Enum):
    """Payment method types."""
    CREDIT_CARD = "credit_card"
    DEBIT_CARD = "debit_card"
    BANK_TRANSFER = "bank_transfer"
    PAYPAL = "paypal"
    STRIPE = "stripe"
    CRYPTO_WALLET = "crypto_wallet"
    DIGITAL_WALLET = "digital_wallet"
    WIRE_TRANSFER = "wire_transfer"
    CHECK = "check"
    CASH = "cash"


class SubscriptionStatus(Enum):
    """Subscription status types."""
    ACTIVE = "active"
    INACTIVE = "inactive"
    CANCELLED = "cancelled"
    EXPIRED = "expired"
    PAUSED = "paused"
    TRIAL = "trial"
    PENDING = "pending"
    PAST_DUE = "past_due"


class CryptoCurrency(Enum):
    """Supported cryptocurrency types."""
    BITCOIN = "bitcoin"
    ETHEREUM = "ethereum"
    LITECOIN = "litecoin"
    CARDANO = "cardano"
    SOLANA = "solana"
    POLYGON = "polygon"
    BINANCE_COIN = "binance_coin"
    CHAINLINK = "chainlink"
    USDC = "usdc"
    USDT = "usdt"


class TaxJurisdiction(Enum):
    """Tax jurisdiction types."""
    US_FEDERAL = "us_federal"
    US_STATE = "us_state"
    EU_VAT = "eu_vat"
    UK_VAT = "uk_vat"
    CANADA_GST = "canada_gst"
    AUSTRALIA_GST = "australia_gst"
    INTERNATIONAL = "international"


# ================================
# REVENUE TRACKING SCHEMAS
# ================================

class RevenueTracking(Base):
    """Real-time revenue tracking across all platforms and sources."""
    __tablename__ = 'revenue_tracking'
    __table_args__ = (
        Index('idx_revenue_tracking_user', 'user_id'),
        Index('idx_revenue_tracking_source', 'revenue_source'),
        Index('idx_revenue_tracking_platform', 'platform_name'),
        Index('idx_revenue_tracking_date', 'revenue_date'),
        Index('idx_revenue_tracking_amount', 'gross_amount'),
    )

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    content_id = Column(String(255), nullable=True, index=True)
    
    # Revenue details
    revenue_source = Column(SQLEnum(RevenueSource), nullable=False)
    platform_name = Column(String(100), nullable=False)
    platform_transaction_id = Column(String(255), nullable=True)
    
    # Financial amounts
    gross_amount = Column(Numeric(15, 4), nullable=False)
    net_amount = Column(Numeric(15, 4), nullable=False)
    platform_fee = Column(Numeric(15, 4), default=0)
    service_fee = Column(Numeric(15, 4), default=0)
    tax_amount = Column(Numeric(15, 4), default=0)
    currency_code = Column(String(3), nullable=False, default='USD')
    
    # Exchange rate information
    exchange_rate = Column(Numeric(10, 6), default=1.0)
    base_currency_amount = Column(Numeric(15, 4), nullable=True)
    base_currency_code = Column(String(3), default='USD')
    
    # Transaction metadata
    transaction_type = Column(String(50), nullable=False)
    transaction_metadata = Column(JSONB, default={})
    payout_eligible = Column(Boolean, default=True)
    
    # Performance metrics
    units_sold = Column(Integer, default=0)
    streams_plays = Column(BigInteger, default=0)
    downloads = Column(BigInteger, default=0)
    engagement_metrics = Column(JSONB, default={})
    
    # Geographic and demographic data
    country_code = Column(String(2), nullable=True)
    region = Column(String(100), nullable=True)
    audience_demographics = Column(JSONB, default={})
    
    # Timestamps
    revenue_date = Column(DateTime(timezone=True), nullable=False)
    recorded_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    payout_date = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    payments = relationship("PaymentTransaction", back_populates="revenue")
    tax_records = relationship("TaxRecord", back_populates="revenue")


class MonetizationStrategy(Base):
    """AI-powered monetization strategies and optimization."""
    __tablename__ = 'monetization_strategies'
    __table_args__ = (
        Index('idx_monetization_strategy_user', 'user_id'),
        Index('idx_monetization_strategy_type', 'strategy_type'),
        Index('idx_monetization_strategy_status', 'status'),
        Index('idx_monetization_strategy_performance', 'performance_score'),
    )

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    content_id = Column(String(255), nullable=True)
    
    # Strategy details
    strategy_name = Column(String(255), nullable=False)
    strategy_type = Column(String(100), nullable=False)
    strategy_description = Column(Text, nullable=True)
    
    # AI recommendations
    ai_generated = Column(Boolean, default=False)
    ai_model_version = Column(String(50), nullable=True)
    ai_confidence_score = Column(Float, nullable=True)
    recommendation_factors = Column(JSONB, default={})
    
    # Configuration
    target_revenue_monthly = Column(Numeric(12, 2), nullable=True)
    target_audience_size = Column(BigInteger, nullable=True)
    preferred_platforms = Column(ARRAY(String), default=[])
    pricing_tiers = Column(JSONB, default={})
    
    # Performance tracking
    status = Column(String(50), default='draft')  # draft, active, paused, completed
    performance_score = Column(Float, nullable=True)  # 0.0-1.0
    roi_percentage = Column(Float, nullable=True)
    
    # Results and analytics
    total_revenue_generated = Column(Numeric(15, 4), default=0)
    conversion_rate = Column(Float, nullable=True)
    audience_growth_rate = Column(Float, nullable=True)
    engagement_improvement = Column(Float, nullable=True)
    
    # Optimization parameters
    auto_optimization_enabled = Column(Boolean, default=True)
    last_optimization_at = Column(DateTime(timezone=True), nullable=True)
    next_optimization_at = Column(DateTime(timezone=True), nullable=True)
    optimization_frequency_days = Column(Integer, default=7)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    activated_at = Column(DateTime(timezone=True), nullable=True)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)


# ================================
# PAYMENT PROCESSING SCHEMAS
# ================================

class PaymentProvider(Base):
    """Payment provider configurations and credentials."""
    __tablename__ = 'payment_providers'
    __table_args__ = (
        Index('idx_payment_provider_type', 'provider_type'),
        Index('idx_payment_provider_status', 'status'),
    )

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Provider details
    provider_name = Column(String(100), nullable=False, unique=True)
    provider_type = Column(String(50), nullable=False)
    provider_url = Column(Text, nullable=True)
    
    # Configuration
    api_endpoint = Column(Text, nullable=True)
    api_version = Column(String(20), nullable=True)
    supported_currencies = Column(ARRAY(String), default=[])
    supported_countries = Column(ARRAY(String), default=[])
    
    # Credentials (encrypted)
    api_key_encrypted = Column(Text, nullable=True)
    secret_key_encrypted = Column(Text, nullable=True)
    webhook_secret_encrypted = Column(Text, nullable=True)
    merchant_id = Column(String(255), nullable=True)
    
    # Limits and fees
    minimum_transaction_amount = Column(Numeric(10, 2), default=0)
    maximum_transaction_amount = Column(Numeric(15, 2), nullable=True)
    transaction_fee_percentage = Column(Float, default=0)
    fixed_transaction_fee = Column(Numeric(5, 2), default=0)
    
    # Status and health
    status = Column(String(50), default='active')  # active, inactive, maintenance
    last_health_check = Column(DateTime(timezone=True), nullable=True)
    health_status = Column(String(50), default='unknown')  # healthy, degraded, down
    
    # Performance metrics
    success_rate_24h = Column(Float, nullable=True)
    average_processing_time_ms = Column(Integer, nullable=True)
    total_transactions_processed = Column(BigInteger, default=0)
    total_volume_processed = Column(Numeric(15, 2), default=0)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    transactions = relationship("PaymentTransaction", back_populates="provider")


class PaymentTransaction(Base):
    """Payment transactions and processing records."""
    __tablename__ = 'payment_transactions'
    __table_args__ = (
        Index('idx_payment_transaction_user', 'user_id'),
        Index('idx_payment_transaction_status', 'payment_status'),
        Index('idx_payment_transaction_provider', 'provider_id'),
        Index('idx_payment_transaction_created', 'created_at'),
        Index('idx_payment_transaction_amount', 'amount'),
    )

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    revenue_id = Column(UUID(as_uuid=True), ForeignKey('revenue_tracking.id'), nullable=True)
    provider_id = Column(UUID(as_uuid=True), ForeignKey('payment_providers.id'), nullable=False)
    
    # Transaction details
    transaction_id = Column(String(255), nullable=False, unique=True)
    external_transaction_id = Column(String(255), nullable=True)
    payment_status = Column(SQLEnum(PaymentStatus), default=PaymentStatus.PENDING)
    payment_method = Column(SQLEnum(PaymentMethod), nullable=False)
    
    # Financial details
    amount = Column(Numeric(15, 4), nullable=False)
    currency_code = Column(String(3), nullable=False)
    fee_amount = Column(Numeric(15, 4), default=0)
    net_amount = Column(Numeric(15, 4), nullable=False)
    
    # Payer information
    payer_name = Column(String(255), nullable=True)
    payer_email = Column(String(255), nullable=True)
    payer_metadata = Column(JSONB, default={})
    
    # Payment metadata
    description = Column(Text, nullable=True)
    reference_number = Column(String(100), nullable=True)
    invoice_number = Column(String(100), nullable=True)
    payment_metadata = Column(JSONB, default={})
    
    # Processing details
    processing_fee = Column(Numeric(8, 4), default=0)
    processing_time_ms = Column(Integer, nullable=True)
    retry_count = Column(Integer, default=0)
    
    # Risk assessment
    risk_score = Column(Float, nullable=True)  # 0.0-1.0
    fraud_check_passed = Column(Boolean, default=True)
    fraud_check_details = Column(JSONB, default={})
    
    # Geographic information
    ip_address = Column(String(45), nullable=True)
    country_code = Column(String(2), nullable=True)
    region = Column(String(100), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    processed_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    revenue = relationship("RevenueTracking", back_populates="payments")
    provider = relationship("PaymentProvider", back_populates="transactions")


# ================================
# SUBSCRIPTION MANAGEMENT SCHEMAS
# ================================

class SubscriptionPlan(Base):
    """Subscription plans and pricing tiers."""
    __tablename__ = 'subscription_plans'
    __table_args__ = (
        Index('idx_subscription_plan_status', 'status'),
        Index('idx_subscription_plan_price', 'price_monthly'),
    )

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Plan details
    plan_name = Column(String(255), nullable=False)
    plan_code = Column(String(50), nullable=False, unique=True)
    plan_description = Column(Text, nullable=True)
    plan_category = Column(String(100), nullable=False)
    
    # Pricing
    price_monthly = Column(Numeric(10, 2), nullable=False)
    price_yearly = Column(Numeric(10, 2), nullable=True)
    currency_code = Column(String(3), nullable=False, default='USD')
    setup_fee = Column(Numeric(10, 2), default=0)
    
    # Plan features
    features = Column(JSONB, default={})
    limits = Column(JSONB, default={})
    benefits = Column(JSONB, default={})
    
    # Trial configuration
    trial_period_days = Column(Integer, default=0)
    trial_price = Column(Numeric(10, 2), default=0)
    
    # Status and availability
    status = Column(String(50), default='active')  # active, inactive, deprecated
    public_availability = Column(Boolean, default=True)
    target_audience = Column(JSONB, default={})
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    subscriptions = relationship("UserSubscription", back_populates="plan")


class UserSubscription(Base):
    """User subscription records and management."""
    __tablename__ = 'user_subscriptions'
    __table_args__ = (
        Index('idx_user_subscription_user', 'user_id'),
        Index('idx_user_subscription_plan', 'plan_id'),
        Index('idx_user_subscription_status', 'subscription_status'),
        Index('idx_user_subscription_expires', 'expires_at'),
    )

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    plan_id = Column(UUID(as_uuid=True), ForeignKey('subscription_plans.id'), nullable=False)
    
    # Subscription details
    subscription_status = Column(SQLEnum(SubscriptionStatus), default=SubscriptionStatus.ACTIVE)
    external_subscription_id = Column(String(255), nullable=True)
    
    # Billing cycle
    billing_cycle = Column(String(20), nullable=False)  # monthly, yearly, custom
    current_period_start = Column(DateTime(timezone=True), nullable=False)
    current_period_end = Column(DateTime(timezone=True), nullable=False)
    
    # Pricing (can override plan pricing)
    current_price = Column(Numeric(10, 2), nullable=False)
    currency_code = Column(String(3), nullable=False)
    discount_percentage = Column(Float, default=0)
    promo_code = Column(String(50), nullable=True)
    
    # Trial information
    trial_start = Column(DateTime(timezone=True), nullable=True)
    trial_end = Column(DateTime(timezone=True), nullable=True)
    in_trial = Column(Boolean, default=False)
    
    # Usage tracking
    usage_metrics = Column(JSONB, default={})
    last_usage_date = Column(DateTime(timezone=True), nullable=True)
    
    # Cancellation
    cancelled_at = Column(DateTime(timezone=True), nullable=True)
    cancellation_reason = Column(Text, nullable=True)
    cancel_at_period_end = Column(Boolean, default=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    activated_at = Column(DateTime(timezone=True), nullable=True)
    expires_at = Column(DateTime(timezone=True), nullable=True)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    plan = relationship("SubscriptionPlan", back_populates="subscriptions")


# ================================
# CRYPTOCURRENCY SCHEMAS
# ================================

class CryptoWallet(Base):
    """User cryptocurrency wallets and addresses."""
    __tablename__ = 'crypto_wallets'
    __table_args__ = (
        Index('idx_crypto_wallet_user', 'user_id'),
        Index('idx_crypto_wallet_currency', 'currency_type'),
        Index('idx_crypto_wallet_status', 'wallet_status'),
    )

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    
    # Wallet details
    wallet_name = Column(String(255), nullable=False)
    currency_type = Column(SQLEnum(CryptoCurrency), nullable=False)
    wallet_address = Column(String(255), nullable=False)
    public_key = Column(Text, nullable=True)
    
    # Wallet metadata
    wallet_type = Column(String(50), nullable=False)  # hot, cold, hardware, exchange
    wallet_provider = Column(String(100), nullable=True)
    network = Column(String(50), nullable=False)  # mainnet, testnet, etc.
    
    # Balance tracking
    current_balance = Column(Numeric(25, 8), default=0)
    last_balance_update = Column(DateTime(timezone=True), nullable=True)
    balance_usd_equivalent = Column(Numeric(15, 2), nullable=True)
    
    # Security
    is_multisig = Column(Boolean, default=False)
    required_signatures = Column(Integer, default=1)
    backup_seed_stored = Column(Boolean, default=False)
    
    # Status
    wallet_status = Column(String(50), default='active')  # active, inactive, frozen, compromised
    verification_status = Column(String(50), default='unverified')  # unverified, pending, verified
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    verified_at = Column(DateTime(timezone=True), nullable=True)
    last_transaction_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    transactions = relationship("CryptoTransaction", back_populates="wallet")


class CryptoTransaction(Base):
    """Cryptocurrency transaction records."""
    __tablename__ = 'crypto_transactions'
    __table_args__ = (
        Index('idx_crypto_transaction_wallet', 'wallet_id'),
        Index('idx_crypto_transaction_hash', 'transaction_hash'),
        Index('idx_crypto_transaction_status', 'transaction_status'),
        Index('idx_crypto_transaction_created', 'created_at'),
    )

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    wallet_id = Column(UUID(as_uuid=True), ForeignKey('crypto_wallets.id'), nullable=False)
    
    # Transaction details
    transaction_hash = Column(String(255), nullable=False, unique=True)
    block_number = Column(BigInteger, nullable=True)
    block_hash = Column(String(255), nullable=True)
    transaction_index = Column(Integer, nullable=True)
    
    # Transfer details
    from_address = Column(String(255), nullable=False)
    to_address = Column(String(255), nullable=False)
    amount = Column(Numeric(25, 8), nullable=False)
    currency_type = Column(SQLEnum(CryptoCurrency), nullable=False)
    
    # Transaction metadata
    transaction_type = Column(String(50), nullable=False)  # send, receive, stake, unstake, swap
    transaction_status = Column(String(50), default='pending')  # pending, confirmed, failed
    confirmations = Column(Integer, default=0)
    required_confirmations = Column(Integer, default=6)
    
    # Fees
    gas_used = Column(BigInteger, nullable=True)
    gas_price = Column(Numeric(25, 8), nullable=True)
    transaction_fee = Column(Numeric(25, 8), nullable=True)
    
    # USD equivalent (at time of transaction)
    usd_amount = Column(Numeric(15, 2), nullable=True)
    exchange_rate = Column(Numeric(15, 8), nullable=True)
    
    # Network information
    network = Column(String(50), nullable=False)
    contract_address = Column(String(255), nullable=True)  # For token transactions
    
    # Additional data
    transaction_data = Column(Text, nullable=True)
    memo = Column(Text, nullable=True)
    transaction_metadata = Column(JSONB, default={})
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    confirmed_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    wallet = relationship("CryptoWallet", back_populates="transactions")


# ================================
# TAX COMPLIANCE SCHEMAS
# ================================

class TaxRecord(Base):
    """Tax records and compliance tracking."""
    __tablename__ = 'tax_records'
    __table_args__ = (
        Index('idx_tax_record_user', 'user_id'),
        Index('idx_tax_record_jurisdiction', 'tax_jurisdiction'),
        Index('idx_tax_record_year', 'tax_year'),
        Index('idx_tax_record_revenue', 'revenue_id'),
    )

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    revenue_id = Column(UUID(as_uuid=True), ForeignKey('revenue_tracking.id'), nullable=True)
    
    # Tax details
    tax_jurisdiction = Column(SQLEnum(TaxJurisdiction), nullable=False)
    tax_year = Column(Integer, nullable=False)
    tax_period = Column(String(20), nullable=False)  # Q1, Q2, Q3, Q4, annual
    
    # Financial amounts
    taxable_income = Column(Numeric(15, 2), nullable=False)
    tax_rate_percentage = Column(Float, nullable=False)
    tax_amount_owed = Column(Numeric(15, 2), nullable=False)
    tax_amount_paid = Column(Numeric(15, 2), default=0)
    
    # Tax categories
    income_category = Column(String(100), nullable=False)
    deductions = Column(Numeric(15, 2), default=0)
    credits = Column(Numeric(15, 2), default=0)
    
    # Compliance status
    filing_status = Column(String(50), default='pending')  # pending, filed, paid, overdue
    filing_deadline = Column(DateTime(timezone=True), nullable=False)
    filed_at = Column(DateTime(timezone=True), nullable=True)
    
    # Documentation
    supporting_documents = Column(ARRAY(String), default=[])
    tax_form_type = Column(String(50), nullable=True)
    tax_form_data = Column(JSONB, default={})
    
    # Geographic information
    country_code = Column(String(2), nullable=False)
    state_province = Column(String(100), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    revenue = relationship("RevenueTracking", back_populates="tax_records")


class PricingOptimization(Base):
    """Dynamic pricing optimization using AI/ML."""
    __tablename__ = 'pricing_optimizations'
    __table_args__ = (
        Index('idx_pricing_optimization_content', 'content_id'),
        Index('idx_pricing_optimization_status', 'optimization_status'),
        Index('idx_pricing_optimization_performance', 'performance_score'),
    )

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    content_id = Column(String(255), nullable=False, index=True)
    user_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    
    # Optimization details
    optimization_type = Column(String(50), nullable=False)  # dynamic, a_b_test, ml_predicted
    optimization_status = Column(String(50), default='active')  # active, paused, completed
    
    # Current pricing
    current_price = Column(Numeric(10, 2), nullable=False)
    recommended_price = Column(Numeric(10, 2), nullable=True)
    price_change_percentage = Column(Float, nullable=True)
    
    # AI/ML model information
    model_name = Column(String(100), nullable=True)
    model_version = Column(String(50), nullable=True)
    prediction_confidence = Column(Float, nullable=True)
    
    # Market factors
    market_demand_score = Column(Float, nullable=True)
    competition_analysis = Column(JSONB, default={})
    seasonal_factors = Column(JSONB, default={})
    audience_willingness_to_pay = Column(Float, nullable=True)
    
    # Performance metrics
    performance_score = Column(Float, nullable=True)  # 0.0-1.0
    revenue_impact = Column(Numeric(12, 2), nullable=True)
    conversion_rate_change = Column(Float, nullable=True)
    unit_sales_change = Column(Float, nullable=True)
    
    # Test parameters (for A/B testing)
    test_duration_days = Column(Integer, nullable=True)
    test_sample_size = Column(Integer, nullable=True)
    control_group_price = Column(Numeric(10, 2), nullable=True)
    test_group_price = Column(Numeric(10, 2), nullable=True)
    
    # Optimization results
    optimization_results = Column(JSONB, default={})
    recommendations = Column(JSONB, default={})
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    started_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    next_optimization_at = Column(DateTime(timezone=True), nullable=True)


# ================================
# EXPORT FUNCTIONS
# ================================

def get_monetization_enterprise_models() -> None:
    """Get all monetization and enterprise models."""
    return [
        RevenueTracking,
        MonetizationStrategy,
        PaymentProvider,
        PaymentTransaction,
        SubscriptionPlan,
        UserSubscription,
        CryptoWallet,
        CryptoTransaction,
        TaxRecord,
        PricingOptimization,
    ]


def create_monetization_enterprise_tables(engine) -> None:
    """Create all monetization and enterprise tables."""
    try:
        Base.metadata.create_all(engine, tables=[model.__table__ for model in get_monetization_enterprise_models()])
        logger.info("Successfully created monetization and enterprise tables")
        return True
    except Exception as e:
        logger.error(f"Failed to create monetization and enterprise tables: {str(e)}")
        return False


# Export all models and functions
__all__ = [
    # Enums
    'RevenueSource', 'PaymentStatus', 'PaymentMethod', 'SubscriptionStatus', 
    'CryptoCurrency', 'TaxJurisdiction',
    
    # Models
    'RevenueTracking', 'MonetizationStrategy', 'PaymentProvider', 'PaymentTransaction',
    'SubscriptionPlan', 'UserSubscription', 'CryptoWallet', 'CryptoTransaction',
    'TaxRecord', 'PricingOptimization',
    
    # Functions
    'get_monetization_enterprise_models', 'create_monetization_enterprise_tables'
]