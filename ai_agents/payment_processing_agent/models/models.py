"""Payment Processing Models - Industrial Data Models

Complete data models for payment transactions, revenue tracking, payouts,
compliance, and financial analytics in the IA Influencer payment ecosystem.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️  CRITICAL LEGAL NOTICE:
This code and architectural design are the exclusive intellectual property of Fahed Mlaiel.
Unauthorized use, copying, distribution, or commercialization is strictly prohibited.
Contact: mlaiel@live.de for licensing inquiries.
"""from datetime import datetime, timedelta
from decimal import Decimal
from enum import Enum
from typing import Dict, List, Optional, Any, Union
from uuid import uuid4
import json

from sqlalchemy import (
    Column, String, Integer, DateTime, Boolean, Text, 
    Numeric, JSON, ForeignKey, Index, UniqueConstraint
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, validates
from sqlalchemy.dialects.postgresql import UUID, JSONB
from pydantic import BaseModel, Field, validator
from pydantic.types import EmailStr

Base = declarative_base()


class PaymentStatus(str, Enum):
    """Payment transaction status enumeration."""    PENDING = "pending"
    PROCESSING = "processing" 
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    REFUNDED = "refunded"
    DISPUTED = "disputed"


class PayoutStatus(str, Enum):
    """Payout status enumeration."""    SCHEDULED = "scheduled"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    ON_HOLD = "on_hold"


class PaymentMethodType(str, Enum):
    """Payment method type enumeration."""    BANK_TRANSFER = "bank_transfer"
    CREDIT_CARD = "credit_card"
    DEBIT_CARD = "debit_card"
    PAYPAL = "paypal"
    WISE = "wise"
    CRYPTOCURRENCY = "cryptocurrency"
    DIGITAL_WALLET = "digital_wallet"


class TransactionType(str, Enum):
    """Transaction type enumeration."""    REVENUE = "revenue"
    PAYOUT = "payout"
    REFUND = "refund"
    FEE = "fee"
    TAX = "tax"
    CHARGEBACK = "chargeback"
    ADJUSTMENT = "adjustment"


class PaymentTransaction(Base):
    """    Core payment transaction model for all financial operations.
    
    Stores complete transaction history with audit trail, compliance data,
    and fraud detection information.
    """    __tablename__ = "payment_transactions"
    
    # Primary identifiers
    id = Column(String, primary_key=True, default=lambda: str(uuid4()))
    external_id = Column(String, nullable=True, index=True)  # Provider transaction ID
    
    # Transaction details
    creator_id = Column(String, nullable=False, index=True)
    content_id = Column(String, nullable=True, index=True)
    transaction_type = Column(String, nullable=False, index=True)
    
    # Financial amounts (stored as precise decimals)
    amount = Column(Numeric(12, 2), nullable=False)
    currency = Column(String(3), nullable=False, default="EUR")
    fees = Column(Numeric(12, 2), nullable=False, default=Decimal("0.00"))
    taxes = Column(Numeric(12, 2), nullable=False, default=Decimal("0.00"))
    net_amount = Column(Numeric(12, 2), nullable=False)
    
    # Status and processing
    status = Column(String, nullable=False, default=PaymentStatus.PENDING, index=True)
    payment_provider = Column(String, nullable=True)
    payment_method = Column(String, nullable=True)
    
    # Revenue source tracking
    source = Column(String, nullable=True, index=True)  # spotify_royalties, youtube_ads, etc.
    platform_reference = Column(String, nullable=True)  # External platform transaction ID
    
    # Fraud and security
    fraud_score = Column(Numeric(3, 2), nullable=True)  # 0.00 to 1.00
    risk_flags = Column(JSONB, nullable=True)
    security_checks = Column(JSONB, nullable=True)
    
    # Processing timestamps
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)
    processing_started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    failed_at = Column(DateTime, nullable=True)
    
    # Error handling
    error_code = Column(String, nullable=True)
    error_message = Column(Text, nullable=True)
    retry_count = Column(Integer, nullable=False, default=0)
    
    # Metadata and audit trail
    metadata = Column(JSONB, nullable=True, default=dict)
    audit_trail = Column(JSONB, nullable=True, default=list)
    
    # Indexes for performance
    __table_args__ = (
        Index('idx_creator_status_date', 'creator_id', 'status', 'created_at'),
        Index('idx_content_revenue', 'content_id', 'transaction_type', 'created_at'),
        Index('idx_amount_currency', 'currency', 'amount'),
        Index('idx_fraud_score', 'fraud_score'),
    )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert transaction to dictionary."""        return {
            "id": self.id,
            "external_id": self.external_id,
            "creator_id": self.creator_id,
            "content_id": self.content_id,
            "transaction_type": self.transaction_type,
            "amount": str(self.amount),
            "currency": self.currency,
            "fees": str(self.fees),
            "taxes": str(self.taxes),
            "net_amount": str(self.net_amount),
            "status": self.status,
            "payment_provider": self.payment_provider,
            "payment_method": self.payment_method,
            "source": self.source,
            "fraud_score": str(self.fraud_score) if self.fraud_score else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "metadata": self.metadata or {}
        }


class PayoutSchedule(Base):
    """    Payout scheduling and execution tracking.
    
    Manages automated and manual payouts to creators with scheduling,
    batching, and compliance validation.
    """    __tablename__ = "payout_schedules"
    
    # Primary identifiers
    id = Column(String, primary_key=True, default=lambda: str(uuid4()))
    external_id = Column(String, nullable=True, index=True)
    
    # Payout details
    creator_id = Column(String, nullable=False, index=True)
    amount = Column(Numeric(12, 2), nullable=False)
    currency = Column(String(3), nullable=False, default="EUR")
    
    # Payment method and processing
    payment_method = Column(String, nullable=False)
    payment_provider = Column(String, nullable=True)
    
    # Scheduling
    scheduled_date = Column(DateTime, nullable=False, index=True)
    priority = Column(Integer, nullable=False, default=1)  # 1=high, 5=low
    batch_id = Column(String, nullable=True, index=True)
    
    # Status and processing
    status = Column(String, nullable=False, default=PayoutStatus.SCHEDULED, index=True)
    
    # Processing timestamps
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    processing_started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    failed_at = Column(DateTime, nullable=True)
    
    # Error handling
    error_code = Column(String, nullable=True)
    error_message = Column(Text, nullable=True)
    retry_count = Column(Integer, nullable=False, default=0)
    max_retries = Column(Integer, nullable=False, default=3)
    
    # Compliance and validation
    compliance_checks = Column(JSONB, nullable=True)
    tax_withholding = Column(Numeric(12, 2), nullable=False, default=Decimal("0.00"))
    
    # Metadata and audit
    metadata = Column(JSONB, nullable=True, default=dict)
    
    # Relationships
    transactions = relationship(
        "PaymentTransaction", 
        foreign_keys="PaymentTransaction.creator_id",
        primaryjoin="PayoutSchedule.creator_id == PaymentTransaction.creator_id"
    )
    
    __table_args__ = (
        Index('idx_creator_status_scheduled', 'creator_id', 'status', 'scheduled_date'),
        Index('idx_batch_processing', 'batch_id', 'status'),
    )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert payout to dictionary."""        return {
            "id": self.id,
            "creator_id": self.creator_id,
            "amount": str(self.amount),
            "currency": self.currency,
            "payment_method": self.payment_method,
            "status": self.status,
            "scheduled_date": self.scheduled_date.isoformat() if self.scheduled_date else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "metadata": self.metadata or {}
        }


class PaymentMethod(Base):
    """    Creator payment method storage and management.
    
    Securely stores tokenized payment method information with
    validation, compliance checks, and usage tracking.
    """    __tablename__ = "payment_methods"
    
    # Primary identifiers
    id = Column(String, primary_key=True, default=lambda: str(uuid4()))
    creator_id = Column(String, nullable=False, index=True)
    method_id = Column(String, nullable=False)  # Internal method identifier
    
    # Method details
    method_type = Column(String, nullable=False)
    provider = Column(String, nullable=False)  # stripe, wise, paypal, etc.
    
    # Tokenized information (never store raw payment data)
    token = Column(String, nullable=False)  # Payment provider token
    encrypted_details = Column(Text, nullable=True)  # Encrypted method details
    
    # Display information (safe to show)
    display_name = Column(String, nullable=True)  # "Bank ending in 1234"
    currency_support = Column(JSONB, nullable=True)  # Supported currencies
    
    # Status and validation
    is_active = Column(Boolean, nullable=False, default=True)
    is_verified = Column(Boolean, nullable=False, default=False)
    is_default = Column(Boolean, nullable=False, default=False)
    
    # Compliance and limits
    kyc_status = Column(String, nullable=True)
    monthly_limit = Column(Numeric(12, 2), nullable=True)
    daily_limit = Column(Numeric(12, 2), nullable=True)
    
    # Usage tracking
    last_used_at = Column(DateTime, nullable=True)
    usage_count = Column(Integer, nullable=False, default=0)
    total_processed = Column(Numeric(12, 2), nullable=False, default=Decimal("0.00"))
    
    # Timestamps
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    verified_at = Column(DateTime, nullable=True)
    expires_at = Column(DateTime, nullable=True)
    
    # Metadata
    metadata = Column(JSONB, nullable=True, default=dict)
    
    __table_args__ = (
        UniqueConstraint('creator_id', 'method_id', name='uq_creator_method'),
        Index('idx_creator_active', 'creator_id', 'is_active'),
    )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert payment method to dictionary (safe data only)."""        return {
            "id": self.id,
            "method_id": self.method_id,
            "method_type": self.method_type,
            "provider": self.provider,
            "display_name": self.display_name,
            "is_active": self.is_active,
            "is_verified": self.is_verified,
            "is_default": self.is_default,
            "currency_support": self.currency_support or [],
            "created_at": self.created_at.isoformat() if self.created_at else None
        }


class RevenueAllocation(Base):
    """    Revenue allocation and split management.
    
    Handles complex revenue sharing scenarios including collaborations,
    licensing agreements, and multi-party content monetization.
    """    __tablename__ = "revenue_allocations"
    
    # Primary identifiers
    id = Column(String, primary_key=True, default=lambda: str(uuid4()))
    content_id = Column(String, nullable=False, index=True)
    allocation_name = Column(String, nullable=False)
    
    # Allocation rules
    allocation_type = Column(String, nullable=False)  # collaboration, licensing, etc.
    total_percentage = Column(Numeric(5, 2), nullable=False, default=Decimal("100.00"))
    
    # Participant allocations
    allocations = Column(JSONB, nullable=False)  # {"creator_id": percentage, ...}
    
    # Status and validation
    is_active = Column(Boolean, nullable=False, default=True)
    is_verified = Column(Boolean, nullable=False, default=False)
    
    # Effective dates
    effective_from = Column(DateTime, nullable=False, default=datetime.utcnow)
    effective_until = Column(DateTime, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=True)
    
    # Metadata and documentation
    metadata = Column(JSONB, nullable=True, default=dict)
    agreement_reference = Column(String, nullable=True)
    
    __table_args__ = (
        Index('idx_content_active', 'content_id', 'is_active'),
        Index('idx_effective_dates', 'effective_from', 'effective_until'),
    )
    
    @validates('allocations')
    def validate_allocations(self, key, value):
        """Validate allocation percentages sum to total_percentage."""        if isinstance(value, dict):
            total = sum(Decimal(str(v)) for v in value.values())
            if abs(total - self.total_percentage) > Decimal("0.01"):
                raise ValueError(f"Allocations sum to {total}%, expected {self.total_percentage}%")
        return value


class TaxConfiguration(Base):
    """    Tax configuration and compliance settings.
    
    Manages tax rates, withholding requirements, and jurisdiction-specific
    tax compliance rules for different creator locations and revenue types.
    """    __tablename__ = "tax_configurations"
    
    # Primary identifiers
    id = Column(String, primary_key=True, default=lambda: str(uuid4()))
    creator_id = Column(String, nullable=True, index=True)  # None for global rules
    country_code = Column(String(2), nullable=False, index=True)
    tax_jurisdiction = Column(String, nullable=True)
    
    # Tax rates
    income_tax_rate = Column(Numeric(5, 2), nullable=False, default=Decimal("0.00"))
    vat_rate = Column(Numeric(5, 2), nullable=False, default=Decimal("0.00"))
    withholding_rate = Column(Numeric(5, 2), nullable=False, default=Decimal("0.00"))
    
    # Tax thresholds
    tax_free_threshold = Column(Numeric(12, 2), nullable=True)
    withholding_threshold = Column(Numeric(12, 2), nullable=True)
    
    # Revenue type specific rates
    royalty_tax_rate = Column(Numeric(5, 2), nullable=True)
    performance_tax_rate = Column(Numeric(5, 2), nullable=True)
    licensing_tax_rate = Column(Numeric(5, 2), nullable=True)
    
    # Status and validation
    is_active = Column(Boolean, nullable=False, default=True)
    
    # Effective dates
    effective_from = Column(DateTime, nullable=False, default=datetime.utcnow)
    effective_until = Column(DateTime, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=True)
    
    # Compliance information
    tax_treaty_applicable = Column(Boolean, nullable=False, default=False)
    tax_identification_required = Column(Boolean, nullable=False, default=False)
    
    # Metadata
    metadata = Column(JSONB, nullable=True, default=dict)
    
    __table_args__ = (
        UniqueConstraint('creator_id', 'country_code', 'effective_from', 
                        name='uq_tax_config_period'),
        Index('idx_country_active', 'country_code', 'is_active'),
    )


class PaymentProvider(Base):
    """    Payment provider configuration and status tracking.
    
    Manages payment provider integrations, API configurations,
    health status, and performance metrics.
    """    __tablename__ = "payment_providers"
    
    # Primary identifiers
    id = Column(String, primary_key=True, default=lambda: str(uuid4()))
    provider_name = Column(String, nullable=False, unique=True)
    
    # Configuration
    api_version = Column(String, nullable=True)
    supported_currencies = Column(JSONB, nullable=True)
    supported_methods = Column(JSONB, nullable=True)
    supported_countries = Column(JSONB, nullable=True)
    
    # Limits and fees
    min_payout = Column(Numeric(12, 2), nullable=True)
    max_payout = Column(Numeric(12, 2), nullable=True)
    fee_structure = Column(JSONB, nullable=True)  # Complex fee configurations
    
    # Status and health
    is_active = Column(Boolean, nullable=False, default=True)
    is_healthy = Column(Boolean, nullable=False, default=True)
    last_health_check = Column(DateTime, nullable=True)
    
    # Performance metrics
    success_rate = Column(Numeric(5, 2), nullable=True)
    average_processing_time = Column(Integer, nullable=True)  # seconds
    
    # Timestamps
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=True)
    
    # Configuration metadata
    metadata = Column(JSONB, nullable=True, default=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert provider to dictionary."""        return {
            "id": self.id,
            "provider_name": self.provider_name,
            "api_version": self.api_version,
            "supported_currencies": self.supported_currencies or [],
            "supported_methods": self.supported_methods or [],
            "is_active": self.is_active,
            "is_healthy": self.is_healthy,
            "success_rate": str(self.success_rate) if self.success_rate else None,
            "metadata": self.metadata or {}
        }


# Pydantic models for API serialization
class PaymentTransactionCreate(BaseModel):
    """Pydantic model for creating payment transactions."""    creator_id: str = Field(..., description="Creator account identifier")
    content_id: Optional[str] = Field(None, description="Content being monetized")
    transaction_type: TransactionType = Field(..., description="Type of transaction")
    amount: Decimal = Field(..., ge=0, description="Transaction amount")
    currency: str = Field("EUR", description="Currency code")
    source: Optional[str] = Field(None, description="Revenue source")
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict)
    
    @validator('currency')
    def validate_currency(cls, v):
        """Validate currency code format."""        if len(v) != 3 or not v.isupper():
            raise ValueError('Currency must be 3-letter uppercase code')
        return v


class PayoutScheduleCreate(BaseModel):
    """Pydantic model for creating payout schedules."""    creator_id: str = Field(..., description="Creator account identifier")
    amount: Decimal = Field(..., ge=0, description="Payout amount")
    currency: str = Field("EUR", description="Currency code")
    payment_method: str = Field(..., description="Payment method identifier")
    scheduled_date: Optional[datetime] = Field(None, description="Scheduled execution date")
    priority: int = Field(1, ge=1, le=5, description="Payout priority")
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict)


class PaymentMethodCreate(BaseModel):
    """Pydantic model for adding payment methods."""    method_type: PaymentMethodType = Field(..., description="Payment method type")
    provider: str = Field(..., description="Payment provider name")
    token: str = Field(..., description="Payment provider token")
    display_name: Optional[str] = Field(None, description="Display name for method")
    currency_support: Optional[List[str]] = Field(default_factory=list)
    is_default: bool = Field(False, description="Set as default method")
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict)


class RevenueAllocationCreate(BaseModel):
    """Pydantic model for creating revenue allocations."""    content_id: str = Field(..., description="Content identifier")
    allocation_name: str = Field(..., description="Allocation name")
    allocation_type: str = Field(..., description="Type of allocation")
    allocations: Dict[str, float] = Field(..., description="Creator ID to percentage mapping")
    effective_from: Optional[datetime] = Field(None, description="Effective start date")
    effective_until: Optional[datetime] = Field(None, description="Effective end date")
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict)
    
    @validator('allocations')
    def validate_allocation_sum(cls, v):
        """Validate allocation percentages sum to 100."""        total = sum(v.values())
        if abs(total - 100.0) > 0.01:
            raise ValueError(f'Allocations must sum to 100%, got {total}%')
        return v


# Response models for API
class PaymentTransactionResponse(BaseModel):
    """API response model for payment transactions."""    id: str
    creator_id: str
    content_id: Optional[str]
    transaction_type: str
    amount: str
    currency: str
    fees: str
    taxes: str
    net_amount: str
    status: str
    source: Optional[str]
    fraud_score: Optional[str]
    created_at: datetime
    completed_at: Optional[datetime]
    metadata: Dict[str, Any]
    
    class Config:
        from_attributes = True


class PayoutScheduleResponse(BaseModel):
    """API response model for payout schedules."""    id: str
    creator_id: str
    amount: str
    currency: str
    payment_method: str
    status: str
    scheduled_date: datetime
    created_at: datetime
    completed_at: Optional[datetime]
    metadata: Dict[str, Any]
    
    class Config:
        from_attributes = True
