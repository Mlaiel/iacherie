"""Payment Models - Enterprise Database Models for Payment Processing

Ultra-advanced SQLAlchemy models for comprehensive payment processing across multiple
gateways including Stripe, Wise, PayPal with advanced financial tracking and security.

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
"""from sqlalchemy import (
    Column, String, Text, DateTime, Float, Integer, Boolean, JSON, 
    ForeignKey, Index, Enum as SQLEnum, Numeric, UniqueConstraint,
    CheckConstraint, event
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, Session
from sqlalchemy.dialects.postgresql import UUID, ARRAY, JSONB
from datetime import datetime, timezone, timedelta
from decimal import Decimal
from enum import Enum
import uuid
from typing import Dict, Any, List, Optional, Union

Base = declarative_base()


class PaymentGateway(Enum):
    """Supported payment gateway providers"""    STRIPE = "stripe"
    WISE = "wise"
    PAYPAL = "paypal"
    BANK_TRANSFER = "bank_transfer"
    CRYPTOCURRENCY = "cryptocurrency"
    APPLE_PAY = "apple_pay"
    GOOGLE_PAY = "google_pay"
    KLARNA = "klarna"
    REVOLUT = "revolut"


class PaymentStatus(Enum):
    """Payment processing status tracking"""    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    REFUNDED = "refunded"
    PARTIALLY_REFUNDED = "partially_refunded"
    DISPUTED = "disputed"
    CHARGEBACK = "chargeback"
    EXPIRED = "expired"


class PaymentType(Enum):
    """Types of payments in the system"""    REVENUE_PAYOUT = "revenue_payout"
    LICENSING_FEE = "licensing_fee"
    SUBSCRIPTION_PAYMENT = "subscription_payment"
    ONE_TIME_PURCHASE = "one_time_purchase"
    COMMISSION_PAYMENT = "commission_payment"
    PLATFORM_FEE = "platform_fee"
    WITHDRAWAL = "withdrawal"
    DEPOSIT = "deposit"
    TRANSFER = "transfer"
    REFUND = "refund"


class Currency(Enum):
    """Supported currencies for international operations"""    USD = "USD"
    EUR = "EUR"
    GBP = "GBP"
    CAD = "CAD"
    AUD = "AUD"
    JPY = "JPY"
    CHF = "CHF"
    SEK = "SEK"
    NOK = "NOK"
    DKK = "DKK"
    PLN = "PLN"
    CZK = "CZK"
    HUF = "HUF"
    BRL = "BRL"
    MXN = "MXN"
    CNY = "CNY"
    KRW = "KRW"
    INR = "INR"
    SGD = "SGD"
    HKD = "HKD"
    BTC = "BTC"
    ETH = "ETH"


class PaymentAccount(Base):
    """User payment accounts for different gateways and currencies"""    __tablename__ = "payment_accounts"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    
    # Account identification
    gateway = Column(SQLEnum(PaymentGateway), nullable=False)
    gateway_account_id = Column(String(255), nullable=False)
    account_name = Column(String(255), nullable=False)
    account_email = Column(String(255))
    
    # Currency and region
    primary_currency = Column(SQLEnum(Currency), nullable=False, default=Currency.EUR)
    supported_currencies = Column(ARRAY(String))
    country_code = Column(String(3))
    region = Column(String(50))
    
    # Account status and verification
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    verification_level = Column(String(50))
    verification_date = Column(DateTime(timezone=True))
    
    # Account limits and capabilities
    daily_limit = Column(Numeric(15, 2))
    monthly_limit = Column(Numeric(15, 2))
    annual_limit = Column(Numeric(15, 2))
    min_payout_amount = Column(Numeric(10, 2))
    max_transaction_amount = Column(Numeric(15, 2))
    
    # Security and compliance
    kyc_status = Column(String(50))
    aml_status = Column(String(50))
    risk_level = Column(String(20))
    compliance_flags = Column(JSONB)
    
    # Gateway-specific configuration
    gateway_config = Column(JSONB)
    webhook_endpoints = Column(JSONB)
    api_credentials_hash = Column(String(255))
    
    # Metadata and tracking
    metadata = Column(JSONB)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)
    last_used_at = Column(DateTime(timezone=True))
    
    # Relationships
    transactions = relationship("PaymentTransaction", back_populates="account")
    payouts = relationship("RevenuePayout", back_populates="payment_account")
    
    # Indexes
    __table_args__ = (
        Index("idx_payment_accounts_user_gateway", "user_id", "gateway"),
        Index("idx_payment_accounts_gateway_account", "gateway", "gateway_account_id"),
        Index("idx_payment_accounts_status", "is_active", "is_verified"),
        UniqueConstraint("user_id", "gateway", "gateway_account_id", name="uq_user_gateway_account"),
    )


class PaymentTransaction(Base):
    """Comprehensive payment transaction tracking"""    __tablename__ = "payment_transactions"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Transaction identification
    transaction_id = Column(String(255), unique=True, nullable=False)
    gateway_transaction_id = Column(String(255))
    parent_transaction_id = Column(UUID(as_uuid=True), ForeignKey("payment_transactions.id"))
    
    # Account and user references
    account_id = Column(UUID(as_uuid=True), ForeignKey("payment_accounts.id"), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    revenue_record_id = Column(UUID(as_uuid=True), ForeignKey("revenue_records.id"))
    
    # Transaction details
    payment_type = Column(SQLEnum(PaymentType), nullable=False)
    gateway = Column(SQLEnum(PaymentGateway), nullable=False)
    status = Column(SQLEnum(PaymentStatus), nullable=False, default=PaymentStatus.PENDING)
    
    # Financial details
    amount = Column(Numeric(15, 2), nullable=False)
    currency = Column(SQLEnum(Currency), nullable=False)
    original_amount = Column(Numeric(15, 2))
    original_currency = Column(SQLEnum(Currency))
    exchange_rate = Column(Numeric(10, 6))
    
    # Fees and charges
    gateway_fee = Column(Numeric(10, 2))
    platform_fee = Column(Numeric(10, 2))
    processing_fee = Column(Numeric(10, 2))
    tax_amount = Column(Numeric(10, 2))
    net_amount = Column(Numeric(15, 2))
    
    # Transaction flow
    description = Column(Text)
    reference_number = Column(String(255))
    invoice_id = Column(String(255))
    receipt_url = Column(Text)
    
    # Security and fraud detection
    risk_score = Column(Float)
    fraud_indicators = Column(JSONB)
    security_checks = Column(JSONB)
    ip_address = Column(String(45))
    user_agent = Column(Text)
    
    # Gateway-specific data
    gateway_response = Column(JSONB)
    gateway_metadata = Column(JSONB)
    webhook_data = Column(JSONB)
    
    # Processing timestamps
    initiated_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)
    processed_at = Column(DateTime(timezone=True))
    completed_at = Column(DateTime(timezone=True))
    failed_at = Column(DateTime(timezone=True))
    
    # Error handling
    error_code = Column(String(50))
    error_message = Column(Text)
    retry_count = Column(Integer, default=0)
    max_retries = Column(Integer, default=3)
    
    # Audit and compliance
    compliance_status = Column(String(50))
    audit_trail = Column(JSONB)
    metadata = Column(JSONB)
    
    # Relationships
    account = relationship("PaymentAccount", back_populates="transactions")
    revenue_record = relationship("RevenueRecord", back_populates="payment_transactions")
    child_transactions = relationship("PaymentTransaction", backref="parent_transaction", remote_side=[id])
    
    # Indexes
    __table_args__ = (
        Index("idx_payment_transactions_user", "user_id"),
        Index("idx_payment_transactions_account", "account_id"),
        Index("idx_payment_transactions_status", "status"),
        Index("idx_payment_transactions_gateway", "gateway"),
        Index("idx_payment_transactions_date", "initiated_at"),
        Index("idx_payment_transactions_amount", "amount", "currency"),
        Index("idx_payment_transactions_type", "payment_type"),
        CheckConstraint("amount >= 0", name="chk_positive_amount"),
        CheckConstraint("gateway_fee >= 0", name="chk_positive_gateway_fee"),
        CheckConstraint("platform_fee >= 0", name="chk_positive_platform_fee"),
    )


class RevenuePayout(Base):
    """Revenue distribution and payout tracking"""    __tablename__ = "revenue_payouts"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Payout identification
    payout_id = Column(String(255), unique=True, nullable=False)
    batch_id = Column(String(255))
    
    # User and account references
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    payment_account_id = Column(UUID(as_uuid=True), ForeignKey("payment_accounts.id"), nullable=False)
    
    # Payout period and source
    period_start = Column(DateTime(timezone=True), nullable=False)
    period_end = Column(DateTime(timezone=True), nullable=False)
    revenue_source = Column(String(100))
    platform_sources = Column(ARRAY(String))
    
    # Financial calculations
    gross_revenue = Column(Numeric(15, 2), nullable=False)
    platform_commission = Column(Numeric(10, 2))
    gateway_fees = Column(Numeric(10, 2))
    tax_withholding = Column(Numeric(10, 2))
    adjustments = Column(Numeric(10, 2))
    net_payout = Column(Numeric(15, 2), nullable=False)
    
    # Currency handling
    currency = Column(SQLEnum(Currency), nullable=False)
    original_currency = Column(SQLEnum(Currency))
    exchange_rate = Column(Numeric(10, 6))
    exchange_date = Column(DateTime(timezone=True))
    
    # Status and processing
    status = Column(SQLEnum(PaymentStatus), nullable=False, default=PaymentStatus.PENDING)
    gateway = Column(SQLEnum(PaymentGateway), nullable=False)
    gateway_payout_id = Column(String(255))
    
    # Revenue breakdown
    revenue_breakdown = Column(JSONB)
    content_breakdown = Column(JSONB)
    platform_breakdown = Column(JSONB)
    
    # Processing timeline
    calculated_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    scheduled_at = Column(DateTime(timezone=True))
    processed_at = Column(DateTime(timezone=True))
    completed_at = Column(DateTime(timezone=True))
    
    # Documentation and compliance
    invoice_generated = Column(Boolean, default=False)
    invoice_url = Column(Text)
    tax_document_url = Column(Text)
    payment_receipt_url = Column(Text)
    
    # Error handling and retry logic
    error_message = Column(Text)
    retry_count = Column(Integer, default=0)
    last_retry_at = Column(DateTime(timezone=True))
    
    # Metadata
    notes = Column(Text)
    metadata = Column(JSONB)
    
    # Relationships
    payment_account = relationship("PaymentAccount", back_populates="payouts")
    payout_items = relationship("PayoutItem", back_populates="payout")
    
    # Indexes
    __table_args__ = (
        Index("idx_revenue_payouts_user", "user_id"),
        Index("idx_revenue_payouts_period", "period_start", "period_end"),
        Index("idx_revenue_payouts_status", "status"),
        Index("idx_revenue_payouts_gateway", "gateway"),
        Index("idx_revenue_payouts_batch", "batch_id"),
        CheckConstraint("gross_revenue >= 0", name="chk_positive_gross_revenue"),
        CheckConstraint("net_payout >= 0", name="chk_positive_net_payout"),
        CheckConstraint("period_end > period_start", name="chk_valid_period"),
    )


class PayoutItem(Base):
    """Individual revenue items within a payout"""    __tablename__ = "payout_items"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # References
    payout_id = Column(UUID(as_uuid=True), ForeignKey("revenue_payouts.id"), nullable=False)
    revenue_record_id = Column(UUID(as_uuid=True), ForeignKey("revenue_records.id"), nullable=False)
    content_id = Column(UUID(as_uuid=True), ForeignKey("content_fingerprints.id"))
    
    # Item details
    platform = Column(String(50), nullable=False)
    content_type = Column(String(50))
    content_title = Column(String(255))
    
    # Financial breakdown
    gross_amount = Column(Numeric(12, 2), nullable=False)
    platform_fee = Column(Numeric(10, 2))
    net_amount = Column(Numeric(12, 2), nullable=False)
    currency = Column(SQLEnum(Currency), nullable=False)
    
    # Performance metrics
    streams_count = Column(Integer)
    downloads_count = Column(Integer)
    views_count = Column(Integer)
    engagement_score = Column(Float)
    
    # Time period
    period_start = Column(DateTime(timezone=True), nullable=False)
    period_end = Column(DateTime(timezone=True), nullable=False)
    
    # Metadata
    platform_data = Column(JSONB)
    metadata = Column(JSONB)
    
    # Relationships
    payout = relationship("RevenuePayout", back_populates="payout_items")
    revenue_record = relationship("RevenueRecord", back_populates="payout_items")
    
    # Indexes
    __table_args__ = (
        Index("idx_payout_items_payout", "payout_id"),
        Index("idx_payout_items_revenue", "revenue_record_id"),
        Index("idx_payout_items_platform", "platform"),
        Index("idx_payout_items_period", "period_start", "period_end"),
        CheckConstraint("gross_amount >= 0", name="chk_positive_gross_amount"),
        CheckConstraint("net_amount >= 0", name="chk_positive_net_amount"),
    )


class PaymentMethodConfiguration(Base):
    """Configuration for different payment methods and gateways"""    __tablename__ = "payment_method_configurations"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Configuration identification
    name = Column(String(100), nullable=False)
    gateway = Column(SQLEnum(PaymentGateway), nullable=False)
    environment = Column(String(20), nullable=False)  # sandbox, production
    
    # Gateway configuration
    api_endpoint = Column(String(255))
    api_version = Column(String(20))
    webhook_endpoint = Column(String(255))
    
    # Financial settings
    supported_currencies = Column(ARRAY(String))
    minimum_amount = Column(Numeric(10, 2))
    maximum_amount = Column(Numeric(15, 2))
    fee_structure = Column(JSONB)
    
    # Processing settings
    auto_capture = Column(Boolean, default=True)
    settlement_delay_days = Column(Integer, default=0)
    retry_configuration = Column(JSONB)
    
    # Security and compliance
    encryption_key_id = Column(String(255))
    compliance_requirements = Column(JSONB)
    risk_management_rules = Column(JSONB)
    
    # Status and availability
    is_active = Column(Boolean, default=True)
    is_default = Column(Boolean, default=False)
    availability_regions = Column(ARRAY(String))
    
    # Configuration metadata
    configuration_data = Column(JSONB)
    last_tested_at = Column(DateTime(timezone=True))
    test_status = Column(String(50))
    
    # Audit
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(UUID(as_uuid=True))
    
    # Indexes
    __table_args__ = (
        Index("idx_payment_config_gateway", "gateway"),
        Index("idx_payment_config_active", "is_active"),
        Index("idx_payment_config_environment", "environment"),
        UniqueConstraint("gateway", "environment", "name", name="uq_gateway_env_name"),
    )


# SQLAlchemy event listeners for audit trail and validation
@event.listens_for(PaymentTransaction, 'before_insert')
def payment_transaction_before_insert(mapper, connection, target):
    """Validate payment transaction before insert"""    if not target.transaction_id:
        target.transaction_id = f"{target.gateway.value}_{uuid.uuid4().hex[:12]}"
    
    # Calculate net amount if not provided
    if target.net_amount is None and target.amount is not None:
        fees = (target.gateway_fee or 0) + (target.platform_fee or 0) + (target.processing_fee or 0)
        target.net_amount = target.amount - fees


@event.listens_for(RevenuePayout, 'before_insert')
def revenue_payout_before_insert(mapper, connection, target):
    """Generate payout ID and validate amounts"""    if not target.payout_id:
        target.payout_id = f"PAYOUT_{datetime.now().strftime('%Y%m%d')}_{uuid.uuid4().hex[:8].upper()}"
    
    # Validate net payout calculation
    if target.net_payout is None and target.gross_revenue is not None:
        deductions = (target.platform_commission or 0) + (target.gateway_fees or 0) + \
                    (target.tax_withholding or 0) - (target.adjustments or 0)
        target.net_payout = target.gross_revenue - deductions


# Export all models
__all__ = [
    'PaymentGateway', 'PaymentStatus', 'PaymentType', 'Currency',
    'PaymentAccount', 'PaymentTransaction', 'RevenuePayout', 'PayoutItem',
    'PaymentMethodConfiguration'
]
