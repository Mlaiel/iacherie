#!/usr/bin/env python3
"""Commission Models - Professional Data Models for Commission System
================================================================

Enterprise-grade data models and schemas for commission management,
calculation, and financial transactions in the IA Influencer Agent platform.

Version: 2.0.0
Created by: Fahed Mlaiel (mlaiel@live.de)
Expert Team: Lead Dev IA + Backend Senior + ML Engineer + DBA + Security Expert + 
            Microservices Architect + Audio Engineer + DevOps Engineer + IA Prompt Engineer

⚠️ STRICT COPYRIGHT WARNING ⚠️
© 2025 Fahed Mlaiel. ALL RIGHTS RESERVED.

AUTHORIZED USE: Contact mlaiel@live.de for licensing and authorization.
"""
from typing import Dict, List, Optional, Union, Any
from datetime import datetime, timedelta
from enum import Enum, auto
from decimal import Decimal
import uuid

from pydantic import BaseModel, Field, validator, root_validator
from sqlalchemy import Column, String, Integer, DateTime, Numeric, Text, Boolean, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.dialects.postgresql import UUID, JSONB

Base = declarative_base()

class CommissionType(str, Enum):
    """Commission type enumeration"""    PLATFORM_FEE = "platform_fee"
    PROCESSING_FEE = "processing_fee"
    PERFORMANCE_BONUS = "performance_bonus"
    REFERRAL_COMMISSION = "referral_commission"
    COLLABORATION_SHARE = "collaboration_share"
    BRAND_PARTNERSHIP = "brand_partnership"
    LICENSING_ROYALTY = "licensing_royalty"
    SUBSCRIPTION_REVENUE = "subscription_revenue"
    ADVERTISING_REVENUE = "advertising_revenue"
    MERCHANDISE_SALES = "merchandise_sales"

class CommissionStatus(str, Enum):
    """Commission status enumeration"""    PENDING = "pending"
    CALCULATING = "calculating"
    CALCULATED = "calculated"
    APPROVED = "approved"
    UNDER_REVIEW = "under_review"
    REJECTED = "rejected"
    PROCESSING = "processing"
    PAID = "paid"
    FAILED = "failed"
    REFUNDED = "refunded"
    DISPUTED = "disputed"

class CommissionTier(str, Enum):
    """Creator tier enumeration for commission rates"""    STARTER = "starter"
    STANDARD = "standard" 
    PREMIUM = "premium"
    PROFESSIONAL = "professional"
    ENTERPRISE = "enterprise"
    PLATINUM = "platinum"

class PaymentMethod(str, Enum):
    """Payment method enumeration"""    BANK_TRANSFER = "bank_transfer"
    PAYPAL = "paypal"
    STRIPE = "stripe"
    WISE = "wise"
    CRYPTO = "crypto"
    CHECK = "check"
    ESCROW = "escrow"

class Currency(str, Enum):
    """Supported currency enumeration"""    EUR = "EUR"
    USD = "USD"
    GBP = "GBP"
    JPY = "JPY"
    CAD = "CAD"
    AUD = "AUD"
    CHF = "CHF"
    BTC = "BTC"
    ETH = "ETH"

class CommissionRate(BaseModel):
    """Commission rate configuration model"""    
    rate_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    commission_type: CommissionType
    platform: str = Field(..., min_length=1, max_length=100)
    tier: CommissionTier
    base_rate: Decimal = Field(..., ge=0, le=1, decimal_places=6)
    minimum_amount: Decimal = Field(default=Decimal("0.01"), ge=0)
    maximum_amount: Optional[Decimal] = Field(default=None, ge=0)
    currency: Currency = Currency.EUR
    
    # Rate modifiers
    volume_bonus_threshold: Optional[Decimal] = Field(default=None, ge=0)
    volume_bonus_rate: Optional[Decimal] = Field(default=None, ge=0, le=1)
    loyalty_multiplier: Decimal = Field(default=Decimal("1.0"), ge=0.5, le=2.0)
    performance_multiplier: Decimal = Field(default=Decimal("1.0"), ge=0.5, le=3.0)
    
    # Validity
    effective_from: datetime = Field(default_factory=datetime.utcnow)
    effective_until: Optional[datetime] = None
    is_active: bool = True
    
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    @validator("base_rate")
    def validate_base_rate(cls, v):
        if not isinstance(v, Decimal):
            v = Decimal(str(v))
        if v < 0 or v > 1:
            raise ValueError("Base rate must be between 0 and 1")
        return v
    
    @root_validator
    def validate_amount_range(cls, values):
        min_amt = values.get("minimum_amount")
        max_amt = values.get("maximum_amount")
        if min_amt and max_amt and min_amt >= max_amt:
            raise ValueError("Minimum amount must be less than maximum amount")
        return values
    
    class Config:
        json_encoders = {
            Decimal: str,
            datetime: lambda v: v.isoformat()
        }

class CommissionStructure(BaseModel):
    """Commission structure for a specific platform/tier combination"""    
    structure_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    platform: str = Field(..., min_length=1, max_length=100)
    tier: CommissionTier
    
    # Primary commission rates
    base_commission_rate: Decimal = Field(..., ge=0, le=1)
    processing_fee_rate: Decimal = Field(..., ge=0, le=1)
    performance_bonus_rate: Decimal = Field(default=Decimal("0.0"), ge=0, le=1)
    
    # Thresholds and limits
    minimum_payout: Decimal = Field(default=Decimal("10.00"), ge=0)
    maximum_single_commission: Optional[Decimal] = Field(default=None, ge=0)
    daily_limit: Optional[Decimal] = Field(default=None, ge=0)
    monthly_limit: Optional[Decimal] = Field(default=None, ge=0)
    
    # Special rates
    referral_rate: Decimal = Field(default=Decimal("0.01"), ge=0, le=1)
    collaboration_share_rate: Decimal = Field(default=Decimal("0.5"), ge=0, le=1)
    brand_partnership_rate: Decimal = Field(default=Decimal("0.15"), ge=0, le=1)
    
    # Configuration
    enable_volume_bonuses: bool = True
    enable_performance_bonuses: bool = True
    enable_loyalty_multipliers: bool = True
    auto_approval_threshold: Decimal = Field(default=Decimal("1000.00"), ge=0)
    
    currency: Currency = Currency.EUR
    is_active: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        json_encoders = {
            Decimal: str,
            datetime: lambda v: v.isoformat()
        }

class CommissionCalculation(BaseModel):
    """Commission calculation result model"""    
    calculation_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    creator_id: str = Field(..., min_length=1)
    platform: str = Field(..., min_length=1)
    commission_type: CommissionType
    status: CommissionStatus = CommissionStatus.PENDING
    
    # Transaction details
    transaction_id: str = Field(..., min_length=1)
    transaction_amount: Decimal = Field(..., ge=0)
    transaction_currency: Currency = Currency.EUR
    transaction_date: datetime = Field(default_factory=datetime.utcnow)
    
    # Commission calculation
    base_commission_rate: Decimal = Field(..., ge=0, le=1)
    applied_multipliers: Dict[str, Decimal] = Field(default_factory=dict)
    gross_commission: Decimal = Field(..., ge=0)
    processing_fee: Decimal = Field(default=Decimal("0.00"), ge=0)
    net_commission: Decimal = Field(..., ge=0)
    commission_amount: Decimal = Field(..., ge=0)  # Final amount
    commission_currency: Currency = Currency.EUR
    
    # Metadata
    tier: CommissionTier
    calculation_method: str = "standard"
    calculation_details: Dict[str, Any] = Field(default_factory=dict)
    applied_bonuses: List[str] = Field(default_factory=list)
    
    # Audit trail
    calculated_by: Optional[str] = None
    approved_by: Optional[str] = None
    reviewed_by: Optional[str] = None
    notes: Optional[str] = None
    
    # Timing
    created_at: datetime = Field(default_factory=datetime.utcnow)
    calculated_at: Optional[datetime] = None
    approved_at: Optional[datetime] = None
    paid_at: Optional[datetime] = None
    
    @validator("commission_amount")
    def validate_commission_amount(cls, v, values):
        net_commission = values.get("net_commission", Decimal("0"))
        if v != net_commission:
            return net_commission  # Ensure consistency
        return v
    
    @root_validator
    def calculate_net_commission(cls, values):
        gross = values.get("gross_commission", Decimal("0"))
        fee = values.get("processing_fee", Decimal("0"))
        values["net_commission"] = gross - fee
        values["commission_amount"] = values["net_commission"]
        return values
    
    class Config:
        json_encoders = {
            Decimal: str,
            datetime: lambda v: v.isoformat()
        }

class CommissionTransaction(BaseModel):
    """Commission transaction record model"""    
    transaction_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    commission_calculation_id: str = Field(..., min_length=1)
    creator_id: str = Field(..., min_length=1)
    
    # Transaction details
    transaction_type: str = Field(..., min_length=1)  # "payment", "refund", "adjustment"
    amount: Decimal = Field(..., ge=0)
    currency: Currency = Currency.EUR
    exchange_rate: Optional[Decimal] = Field(default=None, gt=0)
    
    # Payment details
    payment_method: PaymentMethod
    payment_provider: str = Field(..., min_length=1)
    payment_reference: Optional[str] = None
    payment_status: str = Field(default="pending")
    
    # Recipient details
    recipient_account: str = Field(..., min_length=1)
    recipient_name: str = Field(..., min_length=1)
    recipient_country: str = Field(..., min_length=2, max_length=2)
    
    # Fees and charges
    processing_fee: Decimal = Field(default=Decimal("0.00"), ge=0)
    transfer_fee: Decimal = Field(default=Decimal("0.00"), ge=0)
    total_fees: Decimal = Field(default=Decimal("0.00"), ge=0)
    net_amount: Decimal = Field(..., ge=0)
    
    # Metadata
    metadata: Dict[str, Any] = Field(default_factory=dict)
    failure_reason: Optional[str] = None
    retry_count: int = Field(default=0, ge=0)
    
    # Timing
    created_at: datetime = Field(default_factory=datetime.utcnow)
    processed_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    
    @root_validator
    def calculate_totals(cls, values):
        processing_fee = values.get("processing_fee", Decimal("0"))
        transfer_fee = values.get("transfer_fee", Decimal("0"))
        total_fees = processing_fee + transfer_fee
        
        amount = values.get("amount", Decimal("0"))
        net_amount = amount - total_fees
        
        values["total_fees"] = total_fees
        values["net_amount"] = max(net_amount, Decimal("0"))
        return values
    
    class Config:
        json_encoders = {
            Decimal: str,
            datetime: lambda v: v.isoformat()
        }

class CommissionReport(BaseModel):
    """Commission report model"""    
    report_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    report_type: str = Field(..., min_length=1)
    report_period: str = Field(..., min_length=1)
    
    # Report scope
    creator_id: Optional[str] = None
    platform: Optional[str] = None
    commission_types: List[CommissionType] = Field(default_factory=list)
    
    # Report data
    total_commissions: Decimal = Field(default=Decimal("0.00"), ge=0)
    total_transactions: int = Field(default=0, ge=0)
    average_commission: Decimal = Field(default=Decimal("0.00"), ge=0)
    commission_breakdown: Dict[str, Decimal] = Field(default_factory=dict)
    
    # Performance metrics
    success_rate: Decimal = Field(default=Decimal("0.00"), ge=0, le=1)
    average_processing_time: Optional[Decimal] = None
    top_performers: List[Dict[str, Any]] = Field(default_factory=list)
    
    # Period comparison
    period_start: datetime
    period_end: datetime
    previous_period_comparison: Optional[Dict[str, Decimal]] = None
    growth_metrics: Optional[Dict[str, Decimal]] = None
    
    # Metadata
    generated_by: Optional[str] = None
    generated_at: datetime = Field(default_factory=datetime.utcnow)
    report_data: Dict[str, Any] = Field(default_factory=dict)
    
    class Config:
        json_encoders = {
            Decimal: str,
            datetime: lambda v: v.isoformat()
        }

class PlatformCommission(BaseModel):
    """Platform-specific commission configuration"""    
    platform_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    platform_name: str = Field(..., min_length=1, max_length=100)
    platform_type: str = Field(..., min_length=1)  # "music", "video", "social", "marketplace"
    
    # Default rates
    default_commission_rate: Decimal = Field(..., ge=0, le=1)
    default_processing_fee: Decimal = Field(..., ge=0, le=1)
    
    # Tier-based rates
    tier_rates: Dict[CommissionTier, Decimal] = Field(default_factory=dict)
    
    # Volume-based bonuses
    volume_thresholds: List[Dict[str, Decimal]] = Field(default_factory=list)
    
    # Platform-specific settings
    minimum_payout: Decimal = Field(default=Decimal("10.00"), ge=0)
    payment_frequency: str = Field(default="weekly")  # "daily", "weekly", "monthly"
    auto_approval_threshold: Decimal = Field(default=Decimal("1000.00"), ge=0)
    
    # Integration details
    api_integration: bool = False
    webhook_url: Optional[str] = None
    api_credentials: Optional[Dict[str, str]] = None
    
    # Status
    is_active: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        json_encoders = {
            Decimal: str,
            datetime: lambda v: v.isoformat()
        }

class CreatorCommission(BaseModel):
    """Creator-specific commission profile"""    
    profile_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    creator_id: str = Field(..., min_length=1)
    
    # Creator tier and status
    current_tier: CommissionTier = CommissionTier.STANDARD
    tier_updated_at: datetime = Field(default_factory=datetime.utcnow)
    next_tier_evaluation: datetime = Field(
        default_factory=lambda: datetime.utcnow() + timedelta(days=30)
    )
    
    # Performance metrics for tier evaluation
    total_revenue_generated: Decimal = Field(default=Decimal("0.00"), ge=0)
    monthly_transaction_volume: Decimal = Field(default=Decimal("0.00"), ge=0)
    collaboration_success_rate: Decimal = Field(default=Decimal("0.00"), ge=0, le=1)
    platform_diversity_score: Decimal = Field(default=Decimal("0.00"), ge=0, le=1)
    
    # Custom rate adjustments
    custom_rate_adjustments: Dict[str, Decimal] = Field(default_factory=dict)
    loyalty_bonus_multiplier: Decimal = Field(default=Decimal("1.0"), ge=1.0, le=2.0)
    performance_bonus_eligible: bool = True
    
    # Payout preferences
    preferred_payment_method: PaymentMethod = PaymentMethod.BANK_TRANSFER
    preferred_currency: Currency = Currency.EUR
    minimum_payout_amount: Decimal = Field(default=Decimal("50.00"), ge=0)
    payout_frequency: str = Field(default="weekly")
    
    # Account details
    payout_account_details: Optional[Dict[str, str]] = None
    tax_information: Optional[Dict[str, Any]] = None
    compliance_status: str = Field(default="compliant")
    
    # Statistics
    total_commissions_earned: Decimal = Field(default=Decimal("0.00"), ge=0)
    total_transactions: int = Field(default=0, ge=0)
    average_commission_per_transaction: Decimal = Field(default=Decimal("0.00"), ge=0)
    last_commission_date: Optional[datetime] = None
    
    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        json_encoders = {
            Decimal: str,
            datetime: lambda v: v.isoformat()
        }

class PartnerCommission(BaseModel):
    """Partner/referral commission model"""    
    partner_commission_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    partner_id: str = Field(..., min_length=1)
    referred_creator_id: str = Field(..., min_length=1)
    
    # Commission details
    commission_type: CommissionType = CommissionType.REFERRAL_COMMISSION
    commission_rate: Decimal = Field(..., ge=0, le=1)
    base_transaction_amount: Decimal = Field(..., ge=0)
    commission_amount: Decimal = Field(..., ge=0)
    
    # Referral tracking
    referral_code: Optional[str] = None
    referral_source: Optional[str] = None
    referral_date: datetime = Field(default_factory=datetime.utcnow)
    
    # Lifecycle tracking
    activation_date: Optional[datetime] = None
    first_transaction_date: Optional[datetime] = None
    total_referred_revenue: Decimal = Field(default=Decimal("0.00"), ge=0)
    commission_status: CommissionStatus = CommissionStatus.PENDING
    
    # Metadata
    metadata: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        json_encoders = {
            Decimal: str,
            datetime: lambda v: v.isoformat()
        }

class BrandCommission(BaseModel):
    """Brand partnership commission model"""    
    brand_commission_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    brand_id: str = Field(..., min_length=1)
    creator_id: str = Field(..., min_length=1)
    campaign_id: Optional[str] = None
    
    # Commission structure
    commission_model: str = Field(..., min_length=1)  # "percentage", "fixed", "hybrid"
    base_rate: Optional[Decimal] = Field(default=None, ge=0, le=1)
    fixed_amount: Optional[Decimal] = Field(default=None, ge=0)
    performance_bonuses: List[Dict[str, Any]] = Field(default_factory=list)
    
    # Campaign metrics
    campaign_budget: Optional[Decimal] = Field(default=None, ge=0)
    target_metrics: Dict[str, Any] = Field(default_factory=dict)
    achieved_metrics: Dict[str, Any] = Field(default_factory=dict)
    performance_score: Optional[Decimal] = Field(default=None, ge=0, le=1)
    
    # Financial details
    total_commission: Decimal = Field(default=Decimal("0.00"), ge=0)
    bonus_commission: Decimal = Field(default=Decimal("0.00"), ge=0)
    final_commission: Decimal = Field(default=Decimal("0.00"), ge=0)
    currency: Currency = Currency.EUR
    
    # Contract details
    contract_start: datetime
    contract_end: datetime
    payment_terms: str = Field(default="net_30")
    payment_milestones: List[Dict[str, Any]] = Field(default_factory=list)
    
    # Status tracking
    commission_status: CommissionStatus = CommissionStatus.PENDING
    approval_required: bool = True
    approved_by: Optional[str] = None
    approved_at: Optional[datetime] = None
    
    # Metadata
    metadata: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        json_encoders = {
            Decimal: str,
            datetime: lambda v: v.isoformat()
        }

# SQLAlchemy database models
class CommissionCalculationDB(Base):
    """SQLAlchemy model for commission calculations"""    __tablename__ = "commission_calculations"
    
    id = Column(String, primary_key=True)
    creator_id = Column(String, nullable=False, index=True)
    platform = Column(String, nullable=False, index=True)
    commission_type = Column(String, nullable=False)
    status = Column(String, nullable=False, index=True)
    
    transaction_id = Column(String, nullable=False, index=True)
    transaction_amount = Column(Numeric(12, 4), nullable=False)
    transaction_currency = Column(String(3), nullable=False)
    transaction_date = Column(DateTime, nullable=False)
    
    base_commission_rate = Column(Numeric(8, 6), nullable=False)
    gross_commission = Column(Numeric(12, 4), nullable=False)
    processing_fee = Column(Numeric(12, 4), nullable=False, default=0)
    net_commission = Column(Numeric(12, 4), nullable=False)
    commission_amount = Column(Numeric(12, 4), nullable=False)
    commission_currency = Column(String(3), nullable=False)
    
    tier = Column(String, nullable=False)
    calculation_method = Column(String, nullable=False, default="standard")
    calculation_details = Column(JSONB)
    applied_multipliers = Column(JSONB)
    applied_bonuses = Column(JSONB)
    
    calculated_by = Column(String)
    approved_by = Column(String)
    reviewed_by = Column(String)
    notes = Column(Text)
    
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    calculated_at = Column(DateTime)
    approved_at = Column(DateTime)
    paid_at = Column(DateTime)
    
    def __repr__(self):
        return f"<CommissionCalculation(id={self.id}, creator_id={self.creator_id}, amount={self.commission_amount})>"

class CommissionTransactionDB(Base):
    """SQLAlchemy model for commission transactions"""    __tablename__ = "commission_transactions"
    
    id = Column(String, primary_key=True)
    commission_calculation_id = Column(String, ForeignKey("commission_calculations.id"), nullable=False)
    creator_id = Column(String, nullable=False, index=True)
    
    transaction_type = Column(String, nullable=False)
    amount = Column(Numeric(12, 4), nullable=False)
    currency = Column(String(3), nullable=False)
    exchange_rate = Column(Numeric(10, 6))
    
    payment_method = Column(String, nullable=False)
    payment_provider = Column(String, nullable=False)
    payment_reference = Column(String)
    payment_status = Column(String, nullable=False, default="pending")
    
    recipient_account = Column(String, nullable=False)
    recipient_name = Column(String, nullable=False)
    recipient_country = Column(String(2), nullable=False)
    
    processing_fee = Column(Numeric(12, 4), nullable=False, default=0)
    transfer_fee = Column(Numeric(12, 4), nullable=False, default=0)
    total_fees = Column(Numeric(12, 4), nullable=False, default=0)
    net_amount = Column(Numeric(12, 4), nullable=False)
    
    metadata = Column(JSONB)
    failure_reason = Column(Text)
    retry_count = Column(Integer, nullable=False, default=0)
    
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    processed_at = Column(DateTime)
    completed_at = Column(DateTime)
    
    def __repr__(self):
        return f"<CommissionTransaction(id={self.id}, creator_id={self.creator_id}, amount={self.amount})>"

"""Professional Commission Data Models
© 2025 Fahed Mlaiel - Enterprise-Grade Solution

These models provide comprehensive data structures for commission management,
calculation, and financial transactions with full type safety and validation.

Key Features:
- Type-safe Pydantic models with comprehensive validation
- SQLAlchemy database models for persistence
- Multi-currency and multi-platform support
- Flexible commission structures and tiers
- Comprehensive audit trails and metadata
- Performance optimized with proper indexing

Expert Team Implementation:
- Lead Dev IA & Backend Senior Architecture
- Advanced ML/AI Engineering for intelligent pricing
- Professional Financial Data Modeling
- Enterprise Security Architecture  
- Database Optimization Mastery
- Intelligent Commission Structure Design
"""