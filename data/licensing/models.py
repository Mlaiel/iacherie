"""Licensing Data Models
===================

Professional data models for licensing management, royalty calculation,
and revenue distribution in the IA Influencer Agent platform.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: © 2025 Fahed Mlaiel - All Rights Reserved
"""from datetime import datetime, date
from typing import Optional, Dict, List, Any, Union
from decimal import Decimal
from enum import Enum
import uuid

from sqlalchemy import (
    Column, String, Text, DateTime, Boolean, Integer, 
    Float, JSON, DECIMAL, ForeignKey, Date, Index
)
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.dialects.postgresql import UUID, ARRAY
from sqlalchemy.sql import func

Base = declarative_base()


class LicenseType(Enum):
    """License type enumeration"""    SYNC_LICENSING = "sync_licensing"
    MECHANICAL = "mechanical"
    PERFORMANCE = "performance"
    MASTER_USE = "master_use"
    SYNCHRONIZATION = "synchronization"
    DERIVATIVE = "derivative"
    EXCLUSIVE = "exclusive"
    NON_EXCLUSIVE = "non_exclusive"
    ROYALTY_FREE = "royalty_free"
    CREATIVE_COMMONS = "creative_commons"


class LicenseStatus(Enum):
    """License status enumeration"""    DRAFT = "draft"
    PENDING = "pending"
    ACTIVE = "active"
    SUSPENDED = "suspended"
    EXPIRED = "expired"
    TERMINATED = "terminated"
    BREACHED = "breached"


class PaymentStatus(Enum):
    """Payment status enumeration"""    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    DISPUTED = "disputed"
    REFUNDED = "refunded"
    CANCELLED = "cancelled"


class RevenueSource(Enum):
    """Revenue source enumeration"""    STREAMING = "streaming"
    DOWNLOAD = "download"
    SYNC_LICENSE = "sync_license"
    PERFORMANCE = "performance"
    MECHANICAL = "mechanical"
    ADVERTISING = "advertising"
    SUBSCRIPTION = "subscription"
    MERCHANDISE = "merchandise"
    LIVE_PERFORMANCE = "live_performance"
    BRAND_PARTNERSHIP = "brand_partnership"


class TerritoryScope(Enum):
    """Territory scope enumeration"""    WORLDWIDE = "worldwide"
    NORTH_AMERICA = "north_america"
    EUROPE = "europe"
    ASIA_PACIFIC = "asia_pacific"
    LATIN_AMERICA = "latin_america"
    AFRICA = "africa"
    SPECIFIC_COUNTRIES = "specific_countries"


class UsageType(Enum):
    """Usage type enumeration"""    COMMERCIAL = "commercial"
    NON_COMMERCIAL = "non_commercial"
    EDUCATIONAL = "educational"
    PROMOTIONAL = "promotional"
    BROADCAST = "broadcast"
    DIGITAL_DISTRIBUTION = "digital_distribution"
    PHYSICAL_DISTRIBUTION = "physical_distribution"
    STREAMING_ONLY = "streaming_only"


class LicenseAgreement(Base):
    """License agreement data model"""    __tablename__ = "license_agreements"
    
    # Primary identifiers
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    license_number = Column(String(50), unique=True, nullable=False)
    
    # Parties
    licensor_id = Column(UUID(as_uuid=True), nullable=False)
    licensee_id = Column(UUID(as_uuid=True), nullable=False)
    content_id = Column(UUID(as_uuid=True), nullable=False)
    
    # License details
    license_type = Column(String(50), nullable=False)
    status = Column(String(20), default=LicenseStatus.DRAFT.value)
    title = Column(String(255), nullable=False)
    description = Column(Text)
    
    # Terms and conditions
    territory = Column(String(50), default=TerritoryScope.WORLDWIDE.value)
    usage_rights = Column(ARRAY(String), nullable=False)
    exclusivity = Column(Boolean, default=False)
    
    # Financial terms
    license_fee = Column(DECIMAL(12, 2), default=0)
    royalty_rate = Column(Float, default=0.0)  # Percentage
    minimum_guarantee = Column(DECIMAL(12, 2), default=0)
    advance_payment = Column(DECIMAL(12, 2), default=0)
    currency = Column(String(3), default="USD")
    
    # Duration
    start_date = Column(Date, nullable=False)
    end_date = Column(Date)
    auto_renewal = Column(Boolean, default=False)
    renewal_period_months = Column(Integer, default=12)
    
    # Payment terms
    payment_schedule = Column(String(20), default="monthly")  # monthly, quarterly, annually
    payment_due_days = Column(Integer, default=30)
    late_fee_percentage = Column(Float, default=1.5)
    
    # Compliance and restrictions
    content_restrictions = Column(JSON)
    geographical_restrictions = Column(JSON)
    platform_restrictions = Column(ARRAY(String))
    
    # Legal and compliance
    governing_law = Column(String(100))
    jurisdiction = Column(String(100))
    dispute_resolution = Column(String(50), default="arbitration")
    
    # Metadata
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    created_by = Column(UUID(as_uuid=True))
    last_modified_by = Column(UUID(as_uuid=True))
    
    # Additional terms
    custom_terms = Column(JSON)
    contract_document_url = Column(String(500))
    digital_signature_hash = Column(String(255))
    blockchain_tx_id = Column(String(255))
    
    # Relationships
    royalty_calculations = relationship("RoyaltyCalculation", back_populates="license_agreement")
    usage_tracking = relationship("LicenseUsageTracking", back_populates="license_agreement")
    payment_records = relationship("PaymentRecord", back_populates="license_agreement")
    compliance_reports = relationship("ComplianceReport", back_populates="license_agreement")
    
    # Indexes
    __table_args__ = (
        Index('idx_license_licensor', 'licensor_id'),
        Index('idx_license_licensee', 'licensee_id'),
        Index('idx_license_content', 'content_id'),
        Index('idx_license_status', 'status'),
        Index('idx_license_dates', 'start_date', 'end_date'),
    )


class RoyaltyCalculation(Base):
    """Royalty calculation data model"""    __tablename__ = "royalty_calculations"
    
    # Primary identifiers
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    calculation_id = Column(String(50), unique=True, nullable=False)
    license_agreement_id = Column(UUID(as_uuid=True), ForeignKey("license_agreements.id"))
    
    # Calculation period
    reporting_period_start = Column(Date, nullable=False)
    reporting_period_end = Column(Date, nullable=False)
    calculation_date = Column(DateTime, default=func.now())
    
    # Revenue data
    gross_revenue = Column(DECIMAL(12, 2), nullable=False)
    platform_fees = Column(DECIMAL(12, 2), default=0)
    taxes = Column(DECIMAL(12, 2), default=0)
    other_deductions = Column(DECIMAL(12, 2), default=0)
    net_revenue = Column(DECIMAL(12, 2), nullable=False)
    
    # Royalty calculation
    royalty_rate = Column(Float, nullable=False)
    royalty_amount = Column(DECIMAL(12, 2), nullable=False)
    advance_balance = Column(DECIMAL(12, 2), default=0)
    amount_due = Column(DECIMAL(12, 2), nullable=False)
    
    # Usage metrics
    total_plays = Column(Integer, default=0)
    total_streams = Column(Integer, default=0)
    total_downloads = Column(Integer, default=0)
    unique_users = Column(Integer, default=0)
    
    # Geographic breakdown
    revenue_by_territory = Column(JSON)
    usage_by_territory = Column(JSON)
    
    # Platform breakdown
    revenue_by_platform = Column(JSON)
    usage_by_platform = Column(JSON)
    
    # Payment status
    payment_status = Column(String(20), default=PaymentStatus.PENDING.value)
    payment_due_date = Column(Date)
    payment_processed_date = Column(Date)
    
    # Currency and exchange
    currency = Column(String(3), default="USD")
    exchange_rate = Column(Float, default=1.0)
    original_currency = Column(String(3))
    
    # Metadata
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    calculated_by = Column(UUID(as_uuid=True))
    
    # Additional data
    calculation_method = Column(String(50))
    adjustment_reason = Column(Text)
    supporting_documents = Column(ARRAY(String))
    
    # Relationships
    license_agreement = relationship("LicenseAgreement", back_populates="royalty_calculations")
    payment_records = relationship("PaymentRecord", back_populates="royalty_calculation")
    
    # Indexes
    __table_args__ = (
        Index('idx_royalty_license', 'license_agreement_id'),
        Index('idx_royalty_period', 'reporting_period_start', 'reporting_period_end'),
        Index('idx_royalty_status', 'payment_status'),
        Index('idx_royalty_due_date', 'payment_due_date'),
    )


class LicenseUsageTracking(Base):
    """License usage tracking data model"""    __tablename__ = "license_usage_tracking"
    
    # Primary identifiers
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tracking_id = Column(String(50), unique=True, nullable=False)
    license_agreement_id = Column(UUID(as_uuid=True), ForeignKey("license_agreements.id"))
    
    # Usage details
    usage_date = Column(DateTime, nullable=False)
    usage_type = Column(String(50), nullable=False)
    platform = Column(String(100))
    territory = Column(String(100))
    
    # Metrics
    play_count = Column(Integer, default=0)
    stream_count = Column(Integer, default=0)
    download_count = Column(Integer, default=0)
    view_count = Column(Integer, default=0)
    impression_count = Column(Integer, default=0)
    click_count = Column(Integer, default=0)
    share_count = Column(Integer, default=0)
    
    # Duration and engagement
    total_play_duration = Column(Integer, default=0)  # seconds
    average_play_duration = Column(Integer, default=0)  # seconds
    completion_rate = Column(Float, default=0.0)  # percentage
    
    # Revenue data
    revenue_generated = Column(DECIMAL(10, 2), default=0)
    revenue_currency = Column(String(3), default="USD")
    
    # User demographics
    age_group_breakdown = Column(JSON)
    gender_breakdown = Column(JSON)
    device_breakdown = Column(JSON)
    
    # Technical details
    ip_address = Column(String(45))  # IPv6 support
    user_agent = Column(Text)
    referrer_url = Column(String(500))
    session_id = Column(String(255))
    
    # Quality metrics
    bitrate_used = Column(Integer)
    quality_level = Column(String(20))
    buffer_events = Column(Integer, default=0)
    
    # Compliance tracking
    terms_compliance = Column(Boolean, default=True)
    geographical_compliance = Column(Boolean, default=True)
    platform_compliance = Column(Boolean, default=True)
    
    # Metadata
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Additional data
    custom_metadata = Column(JSON)
    tracking_source = Column(String(100))
    verification_status = Column(String(20), default="verified")
    
    # Relationships
    license_agreement = relationship("LicenseAgreement", back_populates="usage_tracking")
    
    # Indexes
    __table_args__ = (
        Index('idx_usage_license', 'license_agreement_id'),
        Index('idx_usage_date', 'usage_date'),
        Index('idx_usage_platform', 'platform'),
        Index('idx_usage_territory', 'territory'),
        Index('idx_usage_type', 'usage_type'),
    )


class PaymentRecord(Base):
    """Payment record data model"""    __tablename__ = "payment_records"
    
    # Primary identifiers
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    payment_id = Column(String(50), unique=True, nullable=False)
    license_agreement_id = Column(UUID(as_uuid=True), ForeignKey("license_agreements.id"))
    royalty_calculation_id = Column(UUID(as_uuid=True), ForeignKey("royalty_calculations.id"))
    
    # Payment details
    payment_type = Column(String(50), nullable=False)  # royalty, license_fee, advance
    amount = Column(DECIMAL(12, 2), nullable=False)
    currency = Column(String(3), default="USD")
    exchange_rate = Column(Float, default=1.0)
    
    # Payment parties
    payer_id = Column(UUID(as_uuid=True), nullable=False)
    payee_id = Column(UUID(as_uuid=True), nullable=False)
    
    # Status and dates
    status = Column(String(20), default=PaymentStatus.PENDING.value)
    initiated_date = Column(DateTime, default=func.now())
    due_date = Column(Date)
    processed_date = Column(DateTime)
    completed_date = Column(DateTime)
    
    # Payment method
    payment_method = Column(String(50))  # bank_transfer, paypal, stripe, crypto, check
    payment_processor = Column(String(100))
    transaction_id = Column(String(255))
    external_reference = Column(String(255))
    
    # Banking details (encrypted)
    bank_account_hash = Column(String(255))
    routing_info_hash = Column(String(255))
    
    # Fees and adjustments
    processing_fee = Column(DECIMAL(10, 2), default=0)
    adjustment_amount = Column(DECIMAL(10, 2), default=0)
    adjustment_reason = Column(Text)
    
    # Tax information
    tax_withheld = Column(DECIMAL(10, 2), default=0)
    tax_jurisdiction = Column(String(100))
    tax_form_url = Column(String(500))
    
    # Compliance and reporting
    compliance_checked = Column(Boolean, default=False)
    aml_checked = Column(Boolean, default=False)
    sanctions_checked = Column(Boolean, default=False)
    
    # Metadata
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    created_by = Column(UUID(as_uuid=True))
    
    # Error handling
    error_code = Column(String(50))
    error_message = Column(Text)
    retry_count = Column(Integer, default=0)
    
    # Additional data
    notes = Column(Text)
    supporting_documents = Column(ARRAY(String))
    blockchain_tx_hash = Column(String(255))
    
    # Relationships
    license_agreement = relationship("LicenseAgreement", back_populates="payment_records")
    royalty_calculation = relationship("RoyaltyCalculation", back_populates="payment_records")
    
    # Indexes
    __table_args__ = (
        Index('idx_payment_license', 'license_agreement_id'),
        Index('idx_payment_royalty', 'royalty_calculation_id'),
        Index('idx_payment_status', 'status'),
        Index('idx_payment_dates', 'due_date', 'processed_date'),
        Index('idx_payment_parties', 'payer_id', 'payee_id'),
    )


class ComplianceReport(Base):
    """Compliance report data model"""    __tablename__ = "compliance_reports"
    
    # Primary identifiers
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    report_id = Column(String(50), unique=True, nullable=False)
    license_agreement_id = Column(UUID(as_uuid=True), ForeignKey("license_agreements.id"))
    
    # Report details
    report_type = Column(String(50), nullable=False)
    report_date = Column(Date, nullable=False)
    reporting_period_start = Column(Date, nullable=False)
    reporting_period_end = Column(Date, nullable=False)
    
    # Compliance status
    overall_compliance_status = Column(String(20), default="compliant")
    compliance_score = Column(Float, default=100.0)  # 0-100 percentage
    
    # Violations and issues
    violations_found = Column(Integer, default=0)
    critical_violations = Column(Integer, default=0)
    warnings = Column(Integer, default=0)
    
    # Detailed findings
    territorial_compliance = Column(JSON)
    usage_compliance = Column(JSON)
    payment_compliance = Column(JSON)
    technical_compliance = Column(JSON)
    
    # Actions taken
    corrective_actions = Column(JSON)
    penalties_applied = Column(DECIMAL(10, 2), default=0)
    
    # Risk assessment
    risk_level = Column(String(20), default="low")  # low, medium, high, critical
    risk_factors = Column(JSON)
    
    # Audit trail
    auditor_id = Column(UUID(as_uuid=True))
    audit_methodology = Column(String(100))
    evidence_collected = Column(ARRAY(String))
    
    # Metadata
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Report documents
    report_document_url = Column(String(500))
    supporting_documents = Column(ARRAY(String))
    
    # Next review
    next_review_date = Column(Date)
    review_frequency = Column(String(20), default="quarterly")
    
    # Relationships
    license_agreement = relationship("LicenseAgreement", back_populates="compliance_reports")
    
    # Indexes
    __table_args__ = (
        Index('idx_compliance_license', 'license_agreement_id'),
        Index('idx_compliance_date', 'report_date'),
        Index('idx_compliance_status', 'overall_compliance_status'),
        Index('idx_compliance_risk', 'risk_level'),
    )


class RightsOwnership(Base):
    """Rights ownership data model"""    __tablename__ = "rights_ownership"
    
    # Primary identifiers
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    ownership_id = Column(String(50), unique=True, nullable=False)
    content_id = Column(UUID(as_uuid=True), nullable=False)
    
    # Owner details
    owner_id = Column(UUID(as_uuid=True), nullable=False)
    owner_type = Column(String(50), nullable=False)  # individual, company, estate
    ownership_percentage = Column(Float, nullable=False)  # 0-100
    
    # Rights details
    rights_type = Column(String(50), nullable=False)  # master, publishing, sync, etc.
    rights_scope = Column(ARRAY(String), nullable=False)
    territorial_scope = Column(String(50), default=TerritoryScope.WORLDWIDE.value)
    
    # Acquisition details
    acquisition_date = Column(Date, nullable=False)
    acquisition_method = Column(String(50))  # creation, purchase, inheritance, assignment
    acquisition_price = Column(DECIMAL(12, 2))
    acquisition_currency = Column(String(3), default="USD")
    
    # Validity period
    start_date = Column(Date, nullable=False)
    end_date = Column(Date)
    perpetual_rights = Column(Boolean, default=False)
    
    # Transfer restrictions
    transferable = Column(Boolean, default=True)
    transfer_restrictions = Column(JSON)
    first_right_of_refusal = Column(Boolean, default=False)
    
    # Legal documentation
    legal_document_url = Column(String(500))
    registration_number = Column(String(100))
    copyright_office = Column(String(100))
    
    # Blockchain verification
    blockchain_verified = Column(Boolean, default=False)
    blockchain_tx_id = Column(String(255))
    smart_contract_address = Column(String(255))
    
    # Metadata
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    verified_by = Column(UUID(as_uuid=True))
    
    # Status
    status = Column(String(20), default="active")
    dispute_status = Column(String(20), default="none")
    
    # Indexes
    __table_args__ = (
        Index('idx_rights_content', 'content_id'),
        Index('idx_rights_owner', 'owner_id'),
        Index('idx_rights_type', 'rights_type'),
        Index('idx_rights_dates', 'start_date', 'end_date'),
    )


class ContractTerms(Base):
    """Contract terms data model"""    __tablename__ = "contract_terms"
    
    # Primary identifiers
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    terms_id = Column(String(50), unique=True, nullable=False)
    license_agreement_id = Column(UUID(as_uuid=True), ForeignKey("license_agreements.id"))
    
    # Term categories
    category = Column(String(50), nullable=False)
    subcategory = Column(String(100))
    term_type = Column(String(50), nullable=False)  # condition, obligation, right, restriction
    
    # Term content
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    legal_language = Column(Text)
    
    # Enforceability
    mandatory = Column(Boolean, default=True)
    negotiable = Column(Boolean, default=False)
    precedence_order = Column(Integer, default=0)
    
    # Conditions
    conditions = Column(JSON)
    triggers = Column(JSON)
    dependencies = Column(ARRAY(UUID))
    
    # Penalties and remedies
    penalty_amount = Column(DECIMAL(10, 2), default=0)
    penalty_type = Column(String(50))  # fixed, percentage, variable
    remedy_actions = Column(JSON)
    
    # Validity
    effective_date = Column(Date)
    expiry_date = Column(Date)
    auto_renewal = Column(Boolean, default=False)
    
    # Compliance tracking
    compliance_required = Column(Boolean, default=True)
    monitoring_frequency = Column(String(20), default="continuous")
    last_compliance_check = Column(DateTime)
    
    # Metadata
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    created_by = Column(UUID(as_uuid=True))
    
    # Version control
    version = Column(String(20), default="1.0")
    parent_term_id = Column(UUID(as_uuid=True))
    
    # Indexes
    __table_args__ = (
        Index('idx_terms_license', 'license_agreement_id'),
        Index('idx_terms_category', 'category'),
        Index('idx_terms_type', 'term_type'),
        Index('idx_terms_dates', 'effective_date', 'expiry_date'),
    )


class RevenueDistribution(Base):
    """Revenue distribution data model"""    __tablename__ = "revenue_distributions"
    
    # Primary identifiers
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    distribution_id = Column(String(50), unique=True, nullable=False)
    royalty_calculation_id = Column(UUID(as_uuid=True), ForeignKey("royalty_calculations.id"))
    
    # Distribution details
    distribution_date = Column(DateTime, default=func.now())
    total_amount = Column(DECIMAL(12, 2), nullable=False)
    currency = Column(String(3), default="USD")
    
    # Recipients
    recipient_count = Column(Integer, nullable=False)
    distribution_breakdown = Column(JSON, nullable=False)  # recipient_id: amount mapping
    
    # Distribution rules
    distribution_method = Column(String(50), default="proportional")
    priority_rules = Column(JSON)
    minimum_payment_threshold = Column(DECIMAL(10, 2), default=10.00)
    
    # Processing status
    status = Column(String(20), default="pending")
    processed_date = Column(DateTime)
    completion_date = Column(DateTime)
    
    # Fees and deductions
    processing_fees = Column(DECIMAL(10, 2), default=0)
    platform_fees = Column(DECIMAL(10, 2), default=0)
    total_deductions = Column(DECIMAL(10, 2), default=0)
    net_distributed = Column(DECIMAL(12, 2))
    
    # Audit and verification
    audit_trail = Column(JSON)
    verification_status = Column(String(20), default="pending")
    verified_by = Column(UUID(as_uuid=True))
    verification_date = Column(DateTime)
    
    # Error handling
    failed_payments = Column(Integer, default=0)
    error_details = Column(JSON)
    retry_count = Column(Integer, default=0)
    
    # Metadata
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    created_by = Column(UUID(as_uuid=True))
    
    # Additional data
    notes = Column(Text)
    supporting_documents = Column(ARRAY(String))
    
    # Indexes
    __table_args__ = (
        Index('idx_distribution_royalty', 'royalty_calculation_id'),
        Index('idx_distribution_date', 'distribution_date'),
        Index('idx_distribution_status', 'status'),
    )
