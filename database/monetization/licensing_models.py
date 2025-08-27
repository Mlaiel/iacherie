"""
Licensing Models - Enterprise Licensing and Rights Management

Ultra-advanced licensing system for content rights, royalty management,
and automated licensing agreement processing for content creators.

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
"""

from sqlalchemy import (
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


class LicenseType(Enum):
    """Types of content licenses"""
    # Music licensing
    SYNCHRONIZATION = "synchronization"  # Sync rights for media
    MECHANICAL = "mechanical"  # Reproduction rights
    PERFORMANCE = "performance"  # Public performance rights
    MASTER_RECORDING = "master_recording"  # Master use license
    PUBLISHING = "publishing"  # Publishing rights
    
    # Video and visual content
    VIDEO_SYNC = "video_sync"  # Video synchronization
    BROADCAST = "broadcast"  # Broadcasting rights
    STREAMING = "streaming"  # Streaming platform rights
    THEATRICAL = "theatrical"  # Cinema/theater rights
    
    # Digital and online
    DIGITAL_DISTRIBUTION = "digital_distribution"
    PODCAST_USE = "podcast_use"
    YOUTUBE_CONTENT = "youtube_content"
    SOCIAL_MEDIA = "social_media"
    INFLUENCER_USE = "influencer_use"
    
    # Commercial usage
    ADVERTISING = "advertising"  # Commercial advertisements
    BRAND_CONTENT = "brand_content"  # Brand promotional content
    CORPORATE_USE = "corporate_use"  # Internal corporate use
    EDUCATIONAL = "educational"  # Educational licensing
    
    # Creative commons and open
    CREATIVE_COMMONS = "creative_commons"
    ROYALTY_FREE = "royalty_free"
    PUBLIC_DOMAIN = "public_domain"
    
    # Collaboration and remix
    REMIX_RIGHTS = "remix_rights"
    COLLABORATION = "collaboration"
    DERIVATIVE_WORKS = "derivative_works"
    
    # Special cases
    EXCLUSIVE = "exclusive"
    NON_EXCLUSIVE = "non_exclusive"
    BUYOUT = "buyout"
    WORK_FOR_HIRE = "work_for_hire"
    CUSTOM = "custom"


class LicenseStatus(Enum):
    """License agreement status"""
    DRAFT = "draft"
    PENDING_REVIEW = "pending_review"
    UNDER_NEGOTIATION = "under_negotiation"
    APPROVED = "approved"
    ACTIVE = "active"
    SUSPENDED = "suspended"
    TERMINATED = "terminated"
    EXPIRED = "expired"
    DISPUTED = "disputed"
    CANCELLED = "cancelled"


class RoyaltyType(Enum):
    """Types of royalty calculations"""
    PERCENTAGE = "percentage"  # Percentage of revenue
    FLAT_FEE = "flat_fee"  # Fixed amount
    PER_UNIT = "per_unit"  # Per play/download/view
    TIERED = "tiered"  # Tiered rates based on volume
    REVENUE_SHARING = "revenue_sharing"  # Revenue split
    HYBRID = "hybrid"  # Combination of methods
    NEGOTIATED = "negotiated"  # Custom negotiated terms


class PaymentFrequency(Enum):
    """Payment frequency for royalties"""
    REAL_TIME = "real_time"
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    ANNUALLY = "annually"
    ON_DEMAND = "on_demand"
    MILESTONE_BASED = "milestone_based"


class Territory(Enum):
    """Geographic territories for licensing"""
    WORLDWIDE = "worldwide"
    NORTH_AMERICA = "north_america"
    EUROPE = "europe"
    ASIA_PACIFIC = "asia_pacific"
    LATIN_AMERICA = "latin_america"
    MIDDLE_EAST_AFRICA = "middle_east_africa"
    # Specific countries
    UNITED_STATES = "united_states"
    CANADA = "canada"
    UNITED_KINGDOM = "united_kingdom"
    GERMANY = "germany"
    FRANCE = "france"
    SPAIN = "spain"
    ITALY = "italy"
    NETHERLANDS = "netherlands"
    SWEDEN = "sweden"
    NORWAY = "norway"
    DENMARK = "denmark"
    JAPAN = "japan"
    SOUTH_KOREA = "south_korea"
    CHINA = "china"
    INDIA = "india"
    AUSTRALIA = "australia"
    BRAZIL = "brazil"
    MEXICO = "mexico"
    CUSTOM = "custom"


class UsageRights(Enum):
    """Specific usage rights granted"""
    REPRODUCTION = "reproduction"
    DISTRIBUTION = "distribution"
    PUBLIC_PERFORMANCE = "public_performance"
    PUBLIC_DISPLAY = "public_display"
    ADAPTATION = "adaptation"
    TRANSLATION = "translation"
    DIGITIZATION = "digitization"
    SYNCHRONIZATION = "synchronization"
    BROADCAST = "broadcast"
    STREAMING = "streaming"
    DOWNLOAD = "download"
    REMIX = "remix"
    SAMPLING = "sampling"
    COVER_VERSION = "cover_version"
    LIVE_PERFORMANCE = "live_performance"


class LicenseAgreement(Base):
    """
    License Agreement Model
    
    Comprehensive licensing agreement management with automated
    terms processing, compliance tracking, and revenue allocation.
    """
    __tablename__ = "license_agreements"
    
    # Primary identification
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    agreement_number = Column(String(100), unique=True, nullable=False, index=True)
    
    # Parties involved
    licensor_user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False, index=True)
    licensee_user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=True, index=True)
    licensee_company_name = Column(String(255), nullable=True)
    licensee_contact_info = Column(JSONB, nullable=True)
    
    # Content being licensed
    content_fingerprint_id = Column(UUID(as_uuid=True), ForeignKey('content_fingerprints.id'), nullable=False, index=True)
    content_title = Column(String(500), nullable=False)
    content_description = Column(Text, nullable=True)
    content_metadata = Column(JSONB, nullable=True)
    
    # License details
    license_type = Column(SQLEnum(LicenseType), nullable=False, index=True)
    license_status = Column(SQLEnum(LicenseStatus), default=LicenseStatus.DRAFT, index=True)
    is_exclusive = Column(Boolean, default=False, index=True)
    is_transferable = Column(Boolean, default=False)
    is_sub_licensable = Column(Boolean, default=False)
    
    # Geographic scope
    territories = Column(ARRAY(SQLEnum(Territory)), nullable=False)
    excluded_territories = Column(ARRAY(SQLEnum(Territory)), nullable=True)
    territory_restrictions = Column(JSONB, nullable=True)
    
    # Usage rights
    granted_rights = Column(ARRAY(SQLEnum(UsageRights)), nullable=False)
    restricted_uses = Column(ARRAY(String), nullable=True)
    usage_limitations = Column(JSONB, nullable=True)
    
    # Time periods
    effective_date = Column(DateTime(timezone=True), nullable=False)
    expiration_date = Column(DateTime(timezone=True), nullable=True)
    notice_period_days = Column(Integer, default=30)
    auto_renewal = Column(Boolean, default=False)
    renewal_period_months = Column(Integer, nullable=True)
    
    # Financial terms
    royalty_type = Column(SQLEnum(RoyaltyType), nullable=False)
    royalty_rate_percentage = Column(Numeric(8, 4), nullable=True)
    flat_fee_amount = Column(Numeric(18, 6), nullable=True)
    per_unit_rate = Column(Numeric(18, 6), nullable=True)
    minimum_guarantee = Column(Numeric(18, 6), nullable=True)
    advance_payment = Column(Numeric(18, 6), nullable=True)
    
    # Payment terms
    payment_frequency = Column(SQLEnum(PaymentFrequency), default=PaymentFrequency.MONTHLY)
    payment_currency = Column(String(10), default='EUR')
    payment_threshold = Column(Numeric(18, 6), default=Decimal('10.00'))
    payment_method = Column(String(100), nullable=True)
    payment_details = Column(JSONB, nullable=True)
    
    # Revenue sharing (for collaborations)
    revenue_split_percentage = Column(Numeric(8, 4), nullable=True)
    revenue_calculation_method = Column(String(100), nullable=True)
    deduction_allowances = Column(JSONB, nullable=True)
    
    # Performance metrics and tracking
    usage_tracking_required = Column(Boolean, default=True)
    reporting_frequency = Column(String(50), default='monthly')
    performance_metrics = Column(JSONB, nullable=True)
    usage_caps = Column(JSONB, nullable=True)
    
    # Legal and compliance
    governing_law = Column(String(100), nullable=True)
    jurisdiction = Column(String(100), nullable=True)
    dispute_resolution = Column(String(100), nullable=True)
    compliance_requirements = Column(JSONB, nullable=True)
    
    # Contract terms
    termination_conditions = Column(JSONB, nullable=True)
    breach_consequences = Column(JSONB, nullable=True)
    force_majeure_clause = Column(Text, nullable=True)
    confidentiality_terms = Column(Text, nullable=True)
    
    # Documentation
    contract_document_url = Column(String(500), nullable=True)
    signed_contract_url = Column(String(500), nullable=True)
    amendments = Column(JSONB, nullable=True)
    notes = Column(Text, nullable=True)
    
    # Signatures and approval
    licensor_signed = Column(Boolean, default=False)
    licensor_signed_date = Column(DateTime(timezone=True), nullable=True)
    licensor_signature_hash = Column(String(255), nullable=True)
    licensee_signed = Column(Boolean, default=False)
    licensee_signed_date = Column(DateTime(timezone=True), nullable=True)
    licensee_signature_hash = Column(String(255), nullable=True)
    
    # Workflow and approvals
    approval_workflow = Column(JSONB, nullable=True)
    current_approver = Column(UUID(as_uuid=True), nullable=True)
    approval_history = Column(JSONB, nullable=True)
    
    # Integration and automation
    blockchain_hash = Column(String(255), nullable=True)
    smart_contract_address = Column(String(255), nullable=True)
    automated_payments = Column(Boolean, default=False)
    api_integration_config = Column(JSONB, nullable=True)
    
    # Audit and tracking
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(UUID(as_uuid=True), nullable=False)
    last_modified_by = Column(UUID(as_uuid=True), nullable=True)
    version = Column(Integer, default=1)
    
    # Relationships
    licensor = relationship("User", foreign_keys=[licensor_user_id], back_populates="licensed_content")
    licensee = relationship("User", foreign_keys=[licensee_user_id], back_populates="acquired_licenses")
    content_fingerprint = relationship("ContentFingerprint", back_populates="license_agreements")
    royalty_payments = relationship("RoyaltyPayment", back_populates="license_agreement")
    usage_reports = relationship("LicenseUsageReport", back_populates="license_agreement")
    
    # Indexes and constraints
    __table_args__ = (
        Index('idx_license_licensor', 'licensor_user_id'),
        Index('idx_license_licensee', 'licensee_user_id'),
        Index('idx_license_content', 'content_fingerprint_id'),
        Index('idx_license_type_status', 'license_type', 'license_status'),
        Index('idx_license_dates', 'effective_date', 'expiration_date'),
        Index('idx_license_exclusive', 'is_exclusive'),
        Index('idx_license_territory', 'territories'),
        
        # Check constraints
        CheckConstraint('effective_date <= expiration_date', name='check_date_order'),
        CheckConstraint('royalty_rate_percentage >= 0 AND royalty_rate_percentage <= 100', name='check_royalty_rate'),
        CheckConstraint('revenue_split_percentage >= 0 AND revenue_split_percentage <= 100', name='check_revenue_split'),
        CheckConstraint('notice_period_days >= 0', name='check_notice_period'),
        CheckConstraint('minimum_guarantee >= 0', name='check_minimum_guarantee'),
        CheckConstraint('advance_payment >= 0', name='check_advance_payment'),
    )
    
    def __repr__(self):
        return f"<LicenseAgreement(id={self.id}, agreement_number={self.agreement_number}, type={self.license_type.value})>"
    
    @property
    def is_active(self) -> bool:
        """Check if license is currently active"""
        now = datetime.utcnow()
        return (
            self.license_status == LicenseStatus.ACTIVE and
            self.effective_date <= now and
            (self.expiration_date is None or self.expiration_date > now)
        )
    
    @property
    def days_until_expiration(self) -> Optional[int]:
        """Calculate days until license expiration"""
        if self.expiration_date:
            delta = self.expiration_date - datetime.utcnow()
            return max(0, delta.days)
        return None
    
    @property
    def is_renewable(self) -> bool:
        """Check if license can be renewed"""
        return self.auto_renewal or self.license_status == LicenseStatus.ACTIVE


class RoyaltyPayment(Base):
    """
    Royalty Payment Model
    
    Tracks individual royalty payments generated from license agreements
    with detailed calculation breakdown and payment processing.
    """
    __tablename__ = "royalty_payments"
    
    # Primary identification
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    payment_reference = Column(String(100), unique=True, nullable=False, index=True)
    
    # Associated license
    license_agreement_id = Column(UUID(as_uuid=True), ForeignKey('license_agreements.id'), nullable=False, index=True)
    
    # Payment period
    period_start = Column(DateTime(timezone=True), nullable=False, index=True)
    period_end = Column(DateTime(timezone=True), nullable=False, index=True)
    reporting_date = Column(DateTime(timezone=True), nullable=False)
    
    # Usage metrics that generated this payment
    total_plays = Column(Integer, default=0)
    total_downloads = Column(Integer, default=0)
    total_streams = Column(Integer, default=0)
    total_views = Column(Integer, default=0)
    unique_users = Column(Integer, default=0)
    usage_breakdown = Column(JSONB, nullable=True)
    
    # Revenue calculation
    gross_revenue = Column(Numeric(18, 6), nullable=False)
    net_revenue = Column(Numeric(18, 6), nullable=False)
    royalty_rate_applied = Column(Numeric(8, 4), nullable=False)
    calculated_royalty = Column(Numeric(18, 6), nullable=False)
    
    # Deductions and adjustments
    platform_fees = Column(Numeric(18, 6), default=0.0)
    processing_fees = Column(Numeric(18, 6), default=0.0)
    tax_withholdings = Column(Numeric(18, 6), default=0.0)
    adjustments = Column(Numeric(18, 6), default=0.0)
    final_payment_amount = Column(Numeric(18, 6), nullable=False)
    
    # Currency and exchange
    original_currency = Column(String(10), nullable=False)
    payment_currency = Column(String(10), nullable=False)
    exchange_rate = Column(Numeric(12, 8), default=1.0)
    
    # Payment processing
    payment_status = Column(String(50), default='pending', index=True)
    payment_method = Column(String(100), nullable=True)
    payment_processor = Column(String(100), nullable=True)
    payment_transaction_id = Column(String(255), nullable=True)
    payment_processed_date = Column(DateTime(timezone=True), nullable=True)
    payment_received_date = Column(DateTime(timezone=True), nullable=True)
    
    # Geographic breakdown
    revenue_by_territory = Column(JSONB, nullable=True)
    usage_by_territory = Column(JSONB, nullable=True)
    
    # Platform breakdown
    revenue_by_platform = Column(JSONB, nullable=True)
    usage_by_platform = Column(JSONB, nullable=True)
    
    # Additional metadata
    calculation_notes = Column(Text, nullable=True)
    payment_notes = Column(Text, nullable=True)
    dispute_status = Column(String(50), nullable=True)
    
    # Audit trail
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    calculated_by = Column(UUID(as_uuid=True), nullable=True)
    approved_by = Column(UUID(as_uuid=True), nullable=True)
    approved_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    license_agreement = relationship("LicenseAgreement", back_populates="royalty_payments")
    
    # Indexes
    __table_args__ = (
        Index('idx_royalty_license_period', 'license_agreement_id', 'period_start', 'period_end'),
        Index('idx_royalty_payment_status', 'payment_status'),
        Index('idx_royalty_reporting_date', 'reporting_date'),
        Index('idx_royalty_amount', 'final_payment_amount'),
        
        # Unique constraint to prevent duplicate payments for same period
        UniqueConstraint('license_agreement_id', 'period_start', 'period_end', 
                        name='uq_royalty_license_period'),
        
        # Check constraints
        CheckConstraint('gross_revenue >= 0', name='check_gross_revenue_positive'),
        CheckConstraint('net_revenue >= 0', name='check_net_revenue_positive'),
        CheckConstraint('calculated_royalty >= 0', name='check_calculated_royalty_positive'),
        CheckConstraint('final_payment_amount >= 0', name='check_final_payment_positive'),
        CheckConstraint('period_start <= period_end', name='check_period_order'),
    )


class LicenseUsageReport(Base):
    """
    License Usage Report Model
    
    Detailed usage reporting for licensed content with comprehensive
    analytics and compliance tracking.
    """
    __tablename__ = "license_usage_reports"
    
    # Primary identification
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    report_reference = Column(String(100), unique=True, nullable=False, index=True)
    
    # Associated license
    license_agreement_id = Column(UUID(as_uuid=True), ForeignKey('license_agreements.id'), nullable=False, index=True)
    
    # Reporting period
    report_period_start = Column(DateTime(timezone=True), nullable=False, index=True)
    report_period_end = Column(DateTime(timezone=True), nullable=False, index=True)
    report_generated_date = Column(DateTime(timezone=True), nullable=False)
    report_type = Column(String(50), nullable=False)  # standard, detailed, audit, custom
    
    # Usage statistics
    total_usage_events = Column(Integer, default=0)
    unique_users_reached = Column(Integer, default=0)
    total_plays = Column(Integer, default=0)
    total_downloads = Column(Integer, default=0)
    total_streams = Column(Integer, default=0)
    total_views = Column(Integer, default=0)
    total_shares = Column(Integer, default=0)
    total_likes = Column(Integer, default=0)
    total_comments = Column(Integer, default=0)
    
    # Platform breakdown
    usage_by_platform = Column(JSONB, nullable=True)
    top_performing_platforms = Column(ARRAY(String), nullable=True)
    platform_growth_rates = Column(JSONB, nullable=True)
    
    # Geographic breakdown
    usage_by_country = Column(JSONB, nullable=True)
    usage_by_region = Column(JSONB, nullable=True)
    top_countries = Column(ARRAY(String), nullable=True)
    international_usage_percentage = Column(Float, nullable=True)
    
    # Demographic insights
    audience_demographics = Column(JSONB, nullable=True)
    user_behavior_patterns = Column(JSONB, nullable=True)
    engagement_metrics = Column(JSONB, nullable=True)
    
    # Revenue attribution
    attributed_revenue = Column(Numeric(18, 6), default=0.0)
    revenue_by_platform = Column(JSONB, nullable=True)
    revenue_by_territory = Column(JSONB, nullable=True)
    revenue_per_usage_event = Column(Numeric(18, 8), nullable=True)
    
    # Compliance and monitoring
    license_compliance_score = Column(Float, default=1.0)
    violations_detected = Column(Integer, default=0)
    violation_details = Column(JSONB, nullable=True)
    compliance_notes = Column(Text, nullable=True)
    
    # Performance analytics
    growth_rate_percentage = Column(Float, nullable=True)
    trend_analysis = Column(JSONB, nullable=True)
    seasonal_patterns = Column(JSONB, nullable=True)
    anomaly_detection = Column(JSONB, nullable=True)
    
    # Quality metrics
    data_quality_score = Column(Float, default=1.0)
    data_completeness_percentage = Column(Float, default=100.0)
    data_accuracy_score = Column(Float, default=1.0)
    
    # Report generation metadata
    generation_method = Column(String(100), nullable=True)  # automated, manual, api
    data_sources = Column(ARRAY(String), nullable=True)
    processing_time_ms = Column(Integer, nullable=True)
    
    # Additional context
    notes = Column(Text, nullable=True)
    recommendations = Column(JSONB, nullable=True)
    action_items = Column(JSONB, nullable=True)
    
    # Audit trail
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    generated_by = Column(UUID(as_uuid=True), nullable=True)
    reviewed_by = Column(UUID(as_uuid=True), nullable=True)
    reviewed_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    license_agreement = relationship("LicenseAgreement", back_populates="usage_reports")
    
    # Indexes
    __table_args__ = (
        Index('idx_usage_license_period', 'license_agreement_id', 'report_period_start'),
        Index('idx_usage_report_date', 'report_generated_date'),
        Index('idx_usage_type', 'report_type'),
        Index('idx_usage_compliance', 'license_compliance_score'),
        Index('idx_usage_revenue', 'attributed_revenue'),
    )


class LicenseTemplate(Base):
    """
    License Template Model
    
    Pre-configured license templates for rapid agreement generation
    with standardized terms and automated contract creation.
    """
    __tablename__ = "license_templates"
    
    # Primary identification
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    template_name = Column(String(255), nullable=False, index=True)
    template_code = Column(String(50), unique=True, nullable=False, index=True)
    
    # Template metadata
    description = Column(Text, nullable=True)
    category = Column(String(100), nullable=False, index=True)
    industry_focus = Column(String(100), nullable=True)
    content_types = Column(ARRAY(String), nullable=True)
    
    # Default license terms
    default_license_type = Column(SQLEnum(LicenseType), nullable=False)
    default_territories = Column(ARRAY(SQLEnum(Territory)), nullable=False)
    default_rights = Column(ARRAY(SQLEnum(UsageRights)), nullable=False)
    default_exclusivity = Column(Boolean, default=False)
    
    # Default financial terms
    default_royalty_type = Column(SQLEnum(RoyaltyType), nullable=False)
    default_royalty_rate = Column(Numeric(8, 4), nullable=True)
    default_payment_frequency = Column(SQLEnum(PaymentFrequency), nullable=False)
    default_minimum_guarantee = Column(Numeric(18, 6), nullable=True)
    
    # Template configuration
    customizable_fields = Column(ARRAY(String), nullable=True)
    required_fields = Column(ARRAY(String), nullable=True)
    validation_rules = Column(JSONB, nullable=True)
    
    # Legal framework
    template_contract_text = Column(Text, nullable=True)
    legal_jurisdiction = Column(String(100), nullable=True)
    governing_law = Column(String(100), nullable=True)
    
    # Usage and status
    is_active = Column(Boolean, default=True, index=True)
    usage_count = Column(Integer, default=0)
    success_rate = Column(Float, default=0.0)
    
    # Version control
    version = Column(String(20), default='1.0')
    parent_template_id = Column(UUID(as_uuid=True), nullable=True)
    
    # Audit trail
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(UUID(as_uuid=True), nullable=False)
    
    # Indexes
    __table_args__ = (
        Index('idx_template_category', 'category'),
        Index('idx_template_active', 'is_active'),
        Index('idx_template_type', 'default_license_type'),
        Index('idx_template_usage', 'usage_count'),
    )


# Event listeners for automatic calculations and validations
@event.listens_for(LicenseAgreement, 'before_insert')
@event.listens_for(LicenseAgreement, 'before_update')
def validate_license_agreement(mapper, connection, target):
    """Validate license agreement data before database operations"""
    # Ensure agreement number is generated if not provided
    if not target.agreement_number:
        target.agreement_number = f"LIC-{datetime.utcnow().strftime('%Y%m%d')}-{str(uuid.uuid4())[:8].upper()}"
    
    # Validate date relationships
    if target.expiration_date and target.effective_date:
        if target.expiration_date <= target.effective_date:
            raise ValueError("Expiration date must be after effective date")
    
    # Validate royalty terms
    if target.royalty_type == RoyaltyType.PERCENTAGE:
        if not target.royalty_rate_percentage:
            raise ValueError("Percentage royalty type requires royalty rate")
    elif target.royalty_type == RoyaltyType.FLAT_FEE:
        if not target.flat_fee_amount:
            raise ValueError("Flat fee royalty type requires fee amount")


@event.listens_for(RoyaltyPayment, 'before_insert')
@event.listens_for(RoyaltyPayment, 'before_update')
def calculate_final_payment(mapper, connection, target):
    """Calculate final payment amount before database operations"""
    if not target.payment_reference:
        target.payment_reference = f"ROY-{datetime.utcnow().strftime('%Y%m%d')}-{str(uuid.uuid4())[:8].upper()}"
    
    # Calculate final payment amount
    target.final_payment_amount = (
        target.calculated_royalty - 
        target.platform_fees - 
        target.processing_fees - 
        target.tax_withholdings + 
        target.adjustments
    )
    
    # Ensure final amount is not negative
    if target.final_payment_amount < 0:
        target.final_payment_amount = Decimal('0.00')


__all__ = [
    'LicenseType',
    'LicenseStatus',
    'RoyaltyType',
    'PaymentFrequency',
    'Territory',
    'UsageRights',
    'LicenseAgreement',
    'RoyaltyPayment',
    'LicenseUsageReport',
    'LicenseTemplate'
]
