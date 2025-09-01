"""Payment Transactions Database Model

Enterprise-grade SQLAlchemy model for managing financial transactions,
payments, refunds, and revenue tracking across multiple payment providers.

Author: Fahed Mlaiel <mlaiel@live.de>
Project: IA Influencer Agent + Content Protection Platform
Copyright: All rights reserved. Unauthorized use, modification, or distribution prohibited.

🚨 INTELLECTUAL PROPERTY WARNING: This code, concept, and architecture are 
the exclusive intellectual property of Fahed Mlaiel (mlaiel@live.de). 
Any use, copying, distribution, or exploitation without explicit written 
authorization is STRICTLY PROHIBITED and will be prosecuted.

Expert Project Team - Fahed Mlaiel:
- Lead AI Developer & Software Architect
- Senior Backend Engineer (Python/FastAPI/Django)  
- Machine Learning Engineer (TensorFlow/PyTorch/Hugging Face)
- Database Administrator & Data Engineer (PostgreSQL/Redis/MongoDB)
- Backend Security Specialist
- Microservices Architect
- Audio Processing Engineer
- DevOps Engineer
- AI Prompt Engineer
"""

from sqlalchemy import Column, String, Text, DateTime, Float, Integer, Boolean, JSON, ForeignKey, Index, Enum as SQLEnum, Numeric, ARRAY
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID, JSONB
from datetime import datetime, timezone
from enum import Enum
import uuid
from typing import Dict, Any, List, Optional
from decimal import Decimal

Base = declarative_base()


class TransactionType(Enum):
    """
Transaction type enumeration"""

    PAYMENT = "payment"
    REFUND = "refund"
    PAYOUT = "payout"
    SUBSCRIPTION = "subscription"
    COMMISSION = "commission"
    ROYALTY = "royalty"
    LICENSING = "licensing"
    SPONSORSHIP = "sponsorship"
    DONATION = "donation"
    TIP = "tip"
    MERCHANDISE = "merchandise"
    COLLABORATION = "collaboration"
    REVENUE_SHARE = "revenue_share"
    PLATFORM_FEE = "platform_fee"
    PROCESSING_FEE = "processing_fee"
    CHARGEBACK = "chargeback"
    DISPUTE = "dispute"
    ADJUSTMENT = "adjustment"
    BONUS = "bonus"
    PENALTY = "penalty"


class TransactionStatus(Enum):
    """Transaction status enumeration"""

    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    REFUNDED = "refunded"
    PARTIALLY_REFUNDED = "partially_refunded"
    DISPUTED = "disputed"
    CHARGEBACK = "chargeback"
    EXPIRED = "expired"
    ON_HOLD = "on_hold"
    REQUIRES_ACTION = "requires_action"
    AUTHORIZED = "authorized"
    CAPTURED = "captured"
    SETTLED = "settled"


class PaymentProvider(Enum):
    """Payment provider enumeration"""

    STRIPE = "stripe"
    PAYPAL = "paypal"
    SQUARE = "square"
    WISE = "wise"
    BANK_TRANSFER = "bank_transfer"
    CRYPTO = "crypto"
    APPLE_PAY = "apple_pay"
    GOOGLE_PAY = "google_pay"
    AMAZON_PAY = "amazon_pay"
    KLARNA = "klarna"
    AFTERPAY = "afterpay"
    VENMO = "venmo"
    CASHAPP = "cashapp"
    ZELLE = "zelle"
    SEPA = "sepa"
    ACH = "ach"
    WIRE = "wire"
    CHECK = "check"
    CASH = "cash"
    CREDIT_CARD = "credit_card"
    DEBIT_CARD = "debit_card"
    BANK_ACCOUNT = "bank_account"


class Currency(Enum):
    """Currency enumeration"""

    USD = "USD"
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
    INR = "INR"
    CNY = "CNY"
    KRW = "KRW"
    SGD = "SGD"
    HKD = "HKD"
    BTC = "BTC"
    ETH = "ETH"


class RiskLevel(Enum):
    """Transaction risk level"""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    VERY_HIGH = "very_high"
    FRAUD_SUSPECTED = "fraud_suspected"


class PaymentMethod(Enum):
    """Payment method types"""

    CREDIT_CARD = "credit_card"
    DEBIT_CARD = "debit_card"
    BANK_ACCOUNT = "bank_account"
    DIGITAL_WALLET = "digital_wallet"
    CRYPTOCURRENCY = "cryptocurrency"
    BANK_TRANSFER = "bank_transfer"
    DIRECT_DEBIT = "direct_debit"
    PREPAID_CARD = "prepaid_card"
    GIFT_CARD = "gift_card"
    STORE_CREDIT = "store_credit"
    MOBILE_PAYMENT = "mobile_payment"
    QR_CODE = "qr_code"
    NFC = "nfc"
    BNPL = "bnpl"
    IN_PERSON = "in_person"
    TERMINAL = "terminal"


class PaymentTransaction(Base):
    """
    Enterprise Payment Transaction Model
    
    Comprehensive financial transaction management with multi-provider support,
    fraud detection, compliance tracking, and detailed audit trails.
    """
    __tablename__ = 'payment_transactions'
    
    # Primary identification
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    transaction_id = Column(String(100), unique=True, nullable=False, index=True)
    external_transaction_id = Column(String(200), nullable=True, index=True)
    
    # References
    user_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    payer_user_id = Column(UUID(as_uuid=True), nullable=True, index=True)
    payee_user_id = Column(UUID(as_uuid=True), nullable=True, index=True)
    content_id = Column(UUID(as_uuid=True), ForeignKey('user_contents.id'), nullable=True, index=True)
    licensing_agreement_id = Column(UUID(as_uuid=True), ForeignKey('licensing_agreements.id'), nullable=True, index=True)
    collaboration_request_id = Column(UUID(as_uuid=True), ForeignKey('collaboration_requests.id'), nullable=True, index=True)
    
    # Transaction classification
    transaction_type = Column(SQLEnum(TransactionType), nullable=False, index=True)
    status = Column(SQLEnum(TransactionStatus), nullable=False, default=TransactionStatus.PENDING, index=True)
    payment_provider = Column(SQLEnum(PaymentProvider), nullable=False, index=True)
    payment_method = Column(SQLEnum(PaymentMethod), nullable=False, index=True)
    
    # Financial details
    amount = Column(Numeric(12, 2), nullable=False)
    currency = Column(SQLEnum(Currency), nullable=False, default=Currency.USD, index=True)
    original_amount = Column(Numeric(12, 2), nullable=True)
    original_currency = Column(SQLEnum(Currency), nullable=True)
    exchange_rate = Column(Numeric(10, 6), nullable=True)
    
    # Fees and charges
    platform_fee = Column(Numeric(10, 2), nullable=False, default=0.00)
    processing_fee = Column(Numeric(10, 2), nullable=False, default=0.00)
    gateway_fee = Column(Numeric(10, 2), nullable=False, default=0.00)
    network_fee = Column(Numeric(10, 2), nullable=False, default=0.00)
    total_fees = Column(Numeric(10, 2), nullable=False, default=0.00)
    net_amount = Column(Numeric(12, 2), nullable=False)
    
    # Tax information
    tax_amount = Column(Numeric(10, 2), nullable=True)
    tax_rate = Column(Numeric(5, 4), nullable=True)
    tax_region = Column(String(100), nullable=True)
    tax_inclusive = Column(Boolean, nullable=False, default=False)
    vat_number = Column(String(50), nullable=True)
    
    # Transaction metadata
    description = Column(Text, nullable=True)
    reference_number = Column(String(100), nullable=True, index=True)
    invoice_number = Column(String(100), nullable=True, index=True)
    purchase_order = Column(String(100), nullable=True)
    memo = Column(Text, nullable=True)
    
    # Timing information
    created_at = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc), index=True)
    updated_at = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    authorized_at = Column(DateTime(timezone=True), nullable=True)
    captured_at = Column(DateTime(timezone=True), nullable=True)
    settled_at = Column(DateTime(timezone=True), nullable=True, index=True)
    failed_at = Column(DateTime(timezone=True), nullable=True)
    refunded_at = Column(DateTime(timezone=True), nullable=True)
    expires_at = Column(DateTime(timezone=True), nullable=True, index=True)
    
    # Payment details
    payment_intent_id = Column(String(200), nullable=True)
    charge_id = Column(String(200), nullable=True)
    authorization_code = Column(String(100), nullable=True)
    receipt_url = Column(Text, nullable=True)
    receipt_number = Column(String(100), nullable=True)
    
    # Customer information
    customer_id = Column(String(200), nullable=True, index=True)
    customer_email = Column(String(200), nullable=True)
    customer_name = Column(String(200), nullable=True)
    billing_address = Column(JSONB, nullable=True)
    shipping_address = Column(JSONB, nullable=True)
    
    # Payment method details
    card_last_four = Column(String(4), nullable=True)
    card_brand = Column(String(50), nullable=True)
    card_funding = Column(String(50), nullable=True)
    card_country = Column(String(10), nullable=True)
    bank_name = Column(String(200), nullable=True)
    account_last_four = Column(String(4), nullable=True)
    
    # Risk and fraud detection
    risk_level = Column(SQLEnum(RiskLevel), nullable=False, default=RiskLevel.LOW, index=True)
    risk_score = Column(Float, nullable=True)
    fraud_score = Column(Float, nullable=True)
    fraud_indicators = Column(JSONB, nullable=True)
    verification_status = Column(String(50), nullable=True)
    cvv_check = Column(String(20), nullable=True)
    address_check = Column(String(20), nullable=True)
    zip_check = Column(String(20), nullable=True)
    
    # Geographic information
    ip_address = Column(String(45), nullable=True)
    ip_country = Column(String(10), nullable=True)
    transaction_country = Column(String(10), nullable=True, index=True)
    issuing_country = Column(String(10), nullable=True)
    geo_match = Column(Boolean, nullable=True)
    
    # Device and session information
    device_fingerprint = Column(String(200), nullable=True)
    user_agent = Column(Text, nullable=True)
    session_id = Column(String(200), nullable=True)
    browser_info = Column(JSONB, nullable=True)
    device_info = Column(JSONB, nullable=True)
    
    # Provider-specific data
    provider_response = Column(JSONB, nullable=True)
    provider_fee_details = Column(JSONB, nullable=True)
    provider_metadata = Column(JSONB, nullable=True)
    webhook_id = Column(String(200), nullable=True)
    api_version = Column(String(20), nullable=True)
    
    # Subscription and recurring
    subscription_id = Column(String(200), nullable=True, index=True)
    is_recurring = Column(Boolean, nullable=False, default=False)
    recurring_interval = Column(String(50), nullable=True)
    trial_period = Column(Boolean, nullable=False, default=False)
    next_billing_date = Column(DateTime(timezone=True), nullable=True)
    
    # Refund and dispute information
    refund_amount = Column(Numeric(10, 2), nullable=True)
    refund_reason = Column(String(200), nullable=True)
    refunded_by = Column(String(100), nullable=True)
    dispute_id = Column(String(200), nullable=True)
    dispute_reason = Column(String(200), nullable=True)
    dispute_evidence = Column(JSONB, nullable=True)
    
    # Compliance and regulatory
    aml_check_status = Column(String(50), nullable=True)
    kyc_status = Column(String(50), nullable=True)
    sanctions_check = Column(Boolean, nullable=True)
    pep_check = Column(Boolean, nullable=True)
    compliance_notes = Column(Text, nullable=True)
    
    # Revenue sharing
    revenue_shares = Column(JSONB, nullable=True)  # {user_id: {amount, percentage}}
    commission_details = Column(JSONB, nullable=True)
    royalty_details = Column(JSONB, nullable=True)
    affiliate_commission = Column(Numeric(10, 2), nullable=True)
    
    # Performance metrics
    processing_time_ms = Column(Integer, nullable=True)
    settlement_time_days = Column(Integer, nullable=True)
    retry_count = Column(Integer, nullable=False, default=0)
    success_rate = Column(Float, nullable=True)
    
    # Integration tracking
    api_call_id = Column(String(200), nullable=True)
    idempotency_key = Column(String(200), nullable=True, index=True)
    source_platform = Column(String(100), nullable=True)
    integration_version = Column(String(20), nullable=True)
    
    # Notifications and receipts
    notification_sent = Column(Boolean, nullable=False, default=False)
    receipt_sent = Column(Boolean, nullable=False, default=False)
    confirmation_email_sent = Column(Boolean, nullable=False, default=False)
    sms_confirmation_sent = Column(Boolean, nullable=False, default=False)
    
    # Analytics and reporting
    conversion_source = Column(String(100), nullable=True)
    utm_parameters = Column(JSONB, nullable=True)
    analytics_data = Column(JSONB, nullable=True)
    cohort_analysis = Column(JSONB, nullable=True)
    
    # Administrative fields
    is_test_transaction = Column(Boolean, nullable=False, default=False, index=True)
    is_internal = Column(Boolean, nullable=False, default=False)
    requires_manual_review = Column(Boolean, nullable=False, default=False)
    reviewed_by = Column(String(100), nullable=True)
    reviewed_at = Column(DateTime(timezone=True), nullable=True)
    
    # Audit trail
    created_by = Column(String(100), nullable=False)
    updated_by = Column(String(100), nullable=True)
    notes = Column(Text, nullable=True)
    admin_notes = Column(Text, nullable=True)
    
    # Advanced indexing
    __table_args__ = (
        Index('idx_payment_transaction_user_status', 'user_id', 'status'),
        Index('idx_payment_transaction_type_amount', 'transaction_type', 'amount'),
        Index('idx_payment_transaction_provider_external', 'payment_provider', 'external_transaction_id'),
        Index('idx_payment_transaction_currency_amount', 'currency', 'amount'),
        Index('idx_payment_transaction_created_settled', 'created_at', 'settled_at'),
        Index('idx_payment_transaction_risk_fraud', 'risk_level', 'fraud_score'),
        Index('idx_payment_transaction_subscription', 'subscription_id', 'is_recurring'),
        Index('idx_payment_transaction_country_currency', 'transaction_country', 'currency'),
        Index('idx_payment_transaction_fees', 'total_fees', 'net_amount'),
        Index('idx_payment_transaction_compliance', 'aml_check_status', 'kyc_status'),
    )
    
    # Relationships
    content = relationship("UserContent", back_populates="payment_transactions")
    licensing_agreement = relationship("LicensingAgreement", back_populates="payment_transactions")
    collaboration_request = relationship("CollaborationRequest", back_populates="payment_transactions")
    
    def __repr__(self):
        return f"<PaymentTransaction(id={self.id}, type={self.transaction_type.value}, amount={self.amount}, status={self.status.value})>"
    
    @classmethod
    def create_payment(
        cls, 
        user_id: str, 
        amount: Decimal, 
        currency: Currency,
        payment_provider: PaymentProvider,
        payment_method: PaymentMethod,
        description: str = None,
        **kwargs
    ) -> 'PaymentTransaction':
        """Create a new payment transaction"""
        transaction = cls(
            user_id=user_id,
            transaction_type=TransactionType.PAYMENT,
            amount=amount,
            currency=currency,
            payment_provider=payment_provider,
            payment_method=payment_method,
            description=description,
            transaction_id=f"txn_{uuid.uuid4().hex[:12]}",
            created_by=kwargs.get('created_by', 'system'),
            **{k: v for k, v in kwargs.items() if k != 'created_by'}
        )
        
        # Calculate net amount (simplified)
        transaction.calculate_fees()
        return transaction
    
    @classmethod
    def create_payout(
        cls,
        user_id: str,
        amount: Decimal,
        currency: Currency,
        payment_provider: PaymentProvider,
        description: str = None,
        **kwargs
    ) -> 'PaymentTransaction':
        """Create a payout transaction"""
        return cls(
            user_id=user_id,
            transaction_type=TransactionType.PAYOUT,
            amount=amount,
            currency=currency,
            payment_provider=payment_provider,
            payment_method=PaymentMethod.BANK_TRANSFER,
            description=description,
            transaction_id=f"payout_{uuid.uuid4().hex[:12]}",
            created_by=kwargs.get('created_by', 'system'),
            **{k: v for k, v in kwargs.items() if k != 'created_by'}
        )
    
    def calculate_fees(self) -> None:
        """Calculate transaction fees based on provider and amount"""
        # Simplified fee calculation - in production, use actual provider rates
        if self.payment_provider == PaymentProvider.STRIPE:
            self.processing_fee = self.amount * Decimal('0.029') + Decimal('0.30')
            self.platform_fee = self.amount * Decimal('0.05')  # 5% platform fee
        elif self.payment_provider == PaymentProvider.PAYPAL:
            self.processing_fee = self.amount * Decimal('0.0349') + Decimal('0.49')
            self.platform_fee = self.amount * Decimal('0.05')
        else:
            self.processing_fee = Decimal('0.00')
            self.platform_fee = self.amount * Decimal('0.03')  # 3% default platform fee
        
        self.total_fees = self.processing_fee + self.platform_fee + self.gateway_fee + self.network_fee
        self.net_amount = self.amount - self.total_fees
    
    def mark_as_completed(self, external_transaction_id: str = None, receipt_url: str = None) -> None:
        """
Mark transaction as completed"""
        self.status = TransactionStatus.COMPLETED
        self.settled_at = datetime.now(timezone.utc)
        if external_transaction_id:
            self.external_transaction_id = external_transaction_id
        if receipt_url:
            self.receipt_url = receipt_url
        self.updated_at = datetime.now(timezone.utc)
    
    def mark_as_failed(self, error_message: str, error_code: str = None) -> None:
        """
Mark transaction as failed"""
        self.status = TransactionStatus.FAILED
        self.failed_at = datetime.now(timezone.utc)
        self.provider_response = {
            'error_message': error_message,
            'error_code': error_code,
            'failed_at': datetime.now(timezone.utc).isoformat()
        }
        self.updated_at = datetime.now(timezone.utc)
    
    def process_refund(self, refund_amount: Decimal = None, reason: str = None, refunded_by: str = None) -> 'PaymentTransaction':
        """
Process a refund for this transaction"""
        if self.status != TransactionStatus.COMPLETED:
            raise ValueError("Can only refund completed transactions")
        
        refund_amount = refund_amount or self.amount
        if refund_amount > self.amount:
            raise ValueError("Refund amount cannot exceed original transaction amount")
        
        # Create refund transaction
        refund = PaymentTransaction(
            user_id=self.user_id,
            transaction_type=TransactionType.REFUND,
            amount=refund_amount,
            currency=self.currency,
            payment_provider=self.payment_provider,
            payment_method=self.payment_method,
            description=f"Refund for transaction {self.transaction_id}",
            transaction_id=f"refund_{uuid.uuid4().hex[:12]}",
            reference_number=self.transaction_id,
            refund_reason=reason,
            refunded_by=refunded_by,
            created_by="refund_system"
        )
        
        # Update original transaction
        self.refund_amount = (self.refund_amount or Decimal('0.00')) + refund_amount
        self.refunded_at = datetime.now(timezone.utc)
        self.refunded_by = refunded_by
        
        if self.refund_amount >= self.amount:
            self.status = TransactionStatus.REFUNDED
        else:
            self.status = TransactionStatus.PARTIALLY_REFUNDED
        
        self.updated_at = datetime.now(timezone.utc)
        
        return refund
    
    def calculate_risk_score(self) -> float:
        """Calculate transaction risk score"""
        risk_score = 0.0
        
        # Amount-based risk
        if self.amount > 1000:
            risk_score += 20
        elif self.amount > 500:
            risk_score += 10
        
        # Geographic risk
        if self.ip_country != self.transaction_country:
            risk_score += 15
        
        # Payment method risk
        if self.payment_method == PaymentMethod.PREPAID_CARD:
            risk_score += 25
        elif self.payment_method == PaymentMethod.CRYPTOCURRENCY:
            risk_score += 30
        
        # First-time customer risk
        if not self.customer_id:
            risk_score += 10
        
        # Device fingerprint mismatch
        if not self.device_fingerprint:
            risk_score += 5
        
        self.risk_score = min(100, risk_score)
        
        # Update risk level
        if self.risk_score >= 80:
            self.risk_level = RiskLevel.VERY_HIGH
        elif self.risk_score >= 60:
            self.risk_level = RiskLevel.HIGH
        elif self.risk_score >= 40:
            self.risk_level = RiskLevel.MEDIUM
        else:
            self.risk_level = RiskLevel.LOW
        
        return self.risk_score
    
    def distribute_revenue_shares(self) -> List['PaymentTransaction']:
        """
Distribute revenue shares to collaborators"""
        if not self.revenue_shares or self.status != TransactionStatus.COMPLETED:
            return []
        
        payout_transactions = []
        
        for user_id, share_info in self.revenue_shares.items():
            share_amount = Decimal(str(share_info['amount']))
            
            payout = PaymentTransaction(
                user_id=user_id,
                transaction_type=TransactionType.REVENUE_SHARE,
                amount=share_amount,
                currency=self.currency,
                payment_provider=PaymentProvider.BANK_TRANSFER,
                payment_method=PaymentMethod.BANK_TRANSFER,
                description=f"Revenue share from transaction {self.transaction_id}",
                transaction_id=f"share_{uuid.uuid4().hex[:12]}",
                reference_number=self.transaction_id,
                created_by="revenue_system"
            )
            
            payout_transactions.append(payout)
        
        return payout_transactions
    
    def get_transaction_summary(self) -> Dict[str, Any]:
        """Get comprehensive transaction summary"""
        return {
            'transaction_info': {
                'id': str(self.id),
                'transaction_id': self.transaction_id,
                'type': self.transaction_type.value,
                'status': self.status.value,
                'amount': float(self.amount),
                'currency': self.currency.value,
                'net_amount': float(self.net_amount)
            },
            'payment_details': {
                'provider': self.payment_provider.value,
                'method': self.payment_method.value,
                'external_id': self.external_transaction_id,
                'receipt_url': self.receipt_url
            },
            'fees': {
                'platform_fee': float(self.platform_fee),
                'processing_fee': float(self.processing_fee),
                'total_fees': float(self.total_fees)
            },
            'timing': {
                'created_at': self.created_at.isoformat() if self.created_at else None,
                'settled_at': self.settled_at.isoformat() if self.settled_at else None,
                'processing_time_ms': self.processing_time_ms
            },
            'risk_assessment': {
                'risk_level': self.risk_level.value,
                'risk_score': self.risk_score,
                'fraud_score': self.fraud_score
            }
        }
    
    def is_eligible_for_refund(self) -> bool:
        """
Check if transaction is eligible for refund"""
        return (
            self.status == TransactionStatus.COMPLETED and
            self.transaction_type in [TransactionType.PAYMENT, TransactionType.SUBSCRIPTION] and
            (self.refund_amount or Decimal('0.00')) < self.amount and
            self.settled_at and
            (datetime.now(timezone.utc) - self.settled_at).days <= 180  # 180 day refund window
        )
    
    def get_tax_summary(self) -> Dict[str, Any]:
        """
Get tax information summary"""
        return {
            'tax_amount': float(self.tax_amount) if self.tax_amount else 0.0,
            'tax_rate': float(self.tax_rate) if self.tax_rate else 0.0,
            'tax_region': self.tax_region,
            'tax_inclusive': self.tax_inclusive,
            'vat_number': self.vat_number,
            'net_amount_before_tax': float(self.amount - (self.tax_amount or Decimal('0.00')))
        }
