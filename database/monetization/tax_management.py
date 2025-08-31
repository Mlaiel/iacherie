"""
Tax Management Models - Enterprise Tax Optimization & Compliance System

Ultra-advanced tax management system for international tax compliance,
optimization strategies, and automated tax calculation for content creators.

Author: Fahed Mlaiel <mlaiel@live.de>
Project: IA Influencer Agent + Content Protection Platform
Copyright: All rights reserved. Unauthorized use, modification, or distribution prohibited.

 CRITICAL LEGAL WARNING:
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
    Column, Integer, String, DateTime, Float, Boolean, ForeignKey,
    Text, DECIMAL, JSON, BigInteger, Index, UniqueConstraint
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, backref
from sqlalchemy.dialects.postgresql import UUID, JSONB, ARRAY
from sqlalchemy.sql import func
from enum import Enum
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass

Base = declarative_base()

class TaxJurisdiction(Enum):
    """Tax jurisdiction types"""
    FEDERAL = "federal"
    STATE = "state"
    LOCAL = "local"
    INTERNATIONAL = "international"
    VAT = "vat"
    WITHHOLDING = "withholding"

class TaxType(Enum):
    """Tax type classifications"""
    INCOME_TAX = "income_tax"
    CORPORATE_TAX = "corporate_tax"
    VAT_GST = "vat_gst"
    SALES_TAX = "sales_tax"
    WITHHOLDING_TAX = "withholding_tax"
    ROYALTY_TAX = "royalty_tax"
    DIGITAL_SERVICE_TAX = "digital_service_tax"
    SOCIAL_SECURITY = "social_security"
    EXCISE_TAX = "excise_tax"

class TaxStatus(Enum):
    """Tax calculation and filing status"""
    CALCULATED = "calculated"
    PENDING_REVIEW = "pending_review"
    APPROVED = "approved"
    FILED = "filed"
    PAID = "paid"
    OVERDUE = "overdue"
    DISPUTED = "disputed"
    AMENDED = "amended"

class DeductionCategory(Enum):
    """Tax deduction categories"""
    BUSINESS_EXPENSES = "business_expenses"
    EQUIPMENT_DEPRECIATION = "equipment_depreciation"
    HOME_OFFICE = "home_office"
    TRAVEL_EXPENSES = "travel_expenses"
    MARKETING_ADVERTISING = "marketing_advertising"
    PROFESSIONAL_SERVICES = "professional_services"
    SOFTWARE_SUBSCRIPTIONS = "software_subscriptions"
    EDUCATION_TRAINING = "education_training"
    CHARITABLE_DONATIONS = "charitable_donations"

class TaxJurisdictionProfile(Base):
    """Tax jurisdiction profiles and regulations"""
    __tablename__ = 'tax_jurisdiction_profiles'
    
    # Primary identification
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    jurisdiction_code = Column(String(20), unique=True, nullable=False)
    jurisdiction_name = Column(String(200), nullable=False)
    
    # Jurisdiction details
    country_code = Column(String(2), nullable=False)
    state_province = Column(String(100))
    city_locality = Column(String(100))
    jurisdiction_type = Column(String(20), nullable=False)
    
    # Tax authority information
    tax_authority_name = Column(String(200))
    tax_authority_website = Column(String(500))
    contact_information = Column(JSONB)
    
    # Tax rates and brackets
    tax_rates = Column(JSONB, nullable=False)  # Tax rate schedules
    tax_brackets = Column(JSONB)  # Progressive tax brackets
    flat_rate = Column(Float)  # Flat tax rate if applicable
    
    # Applicable taxes
    applicable_tax_types = Column(ARRAY(String))
    withholding_requirements = Column(JSONB)
    vat_registration_threshold = Column(DECIMAL(15, 4))
    
    # Filing requirements
    filing_frequency = Column(String(20))  # monthly, quarterly, annually
    filing_deadlines = Column(JSONB)  # Deadline dates by period
    mandatory_electronic_filing = Column(Boolean, default=False)
    
    # Deductions and exemptions
    standard_deductions = Column(JSONB)
    available_deduction_types = Column(ARRAY(String))
    exemption_thresholds = Column(JSONB)
    special_provisions = Column(JSONB)
    
    # Digital economy provisions
    digital_service_tax_rate = Column(Float, default=0.0)
    digital_threshold_revenue = Column(DECIMAL(15, 4))
    platform_economy_rules = Column(JSONB)
    
    # Double taxation treaties
    treaty_countries = Column(ARRAY(String))
    treaty_provisions = Column(JSONB)
    reduced_withholding_rates = Column(JSONB)
    
    # Compliance requirements
    record_keeping_requirements = Column(JSONB)
    audit_requirements = Column(JSONB)
    penalty_structures = Column(JSONB)
    
    # Status and updates
    is_active = Column(Boolean, default=True)
    last_updated_by_authority = Column(DateTime(timezone=True))
    next_rate_review_date = Column(DateTime(timezone=True))
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), default=func.now())
    updated_at = Column(DateTime(timezone=True), default=func.now(), onupdate=func.now())
    
    # Indexes
    __table_args__ = (
        Index('idx_tax_jurisdiction_country', 'country_code', 'jurisdiction_type'),
        Index('idx_tax_jurisdiction_active', 'is_active', 'jurisdiction_type'),
    )

class CreatorTaxProfile(Base):
    """Creator tax profile and configuration"""
    __tablename__ = 'creator_tax_profiles'
    
    # Primary identification
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    creator_id = Column(UUID(as_uuid=True), unique=True, nullable=False, index=True)
    
    # Tax residence and domicile
    tax_residence_country = Column(String(2), nullable=False)
    tax_residence_state = Column(String(100))
    domicile_country = Column(String(2))
    
    # Business structure
    business_structure = Column(String(50), nullable=False)  # individual, sole_proprietorship, llc, corporation
    tax_id_number = Column(String(50))
    business_registration_number = Column(String(50))
    vat_number = Column(String(50))
    
    # Filing preferences
    filing_status = Column(String(20))  # single, married_filing_jointly, etc.
    accounting_method = Column(String(20), default='accrual')  # cash, accrual
    tax_year_end = Column(String(5), default='12-31')  # MM-DD format
    
    # Professional tax assistance
    has_tax_advisor = Column(Boolean, default=False)
    tax_advisor_details = Column(JSONB)
    accounting_firm = Column(String(200))
    
    # Applicable jurisdictions
    filing_jurisdictions = Column(ARRAY(String))  # List of jurisdiction codes
    withholding_jurisdictions = Column(ARRAY(String))
    treaty_benefits_claimed = Column(ARRAY(String))
    
    # Income sources and classification
    income_types = Column(JSONB)  # Types of income earned
    business_activity_codes = Column(ARRAY(String))
    primary_business_activity = Column(String(100))
    
    # Deduction preferences
    preferred_deduction_methods = Column(JSONB)
    home_office_deduction = Column(Boolean, default=False)
    vehicle_use_percentage = Column(Float, default=0.0)
    
    # Estimated tax payments
    makes_estimated_payments = Column(Boolean, default=False)
    estimated_payment_schedule = Column(JSONB)
    safe_harbor_election = Column(Boolean, default=False)
    
    # Record keeping
    record_keeping_system = Column(String(50))
    document_retention_period = Column(Integer, default=7)  # years
    
    # Compliance status
    compliance_score = Column(Float, default=0.0)
    last_audit_date = Column(DateTime(timezone=True))
    outstanding_issues = Column(JSONB)
    
    # Notifications and preferences
    notification_preferences = Column(JSONB)
    deadline_reminders = Column(Boolean, default=True)
    auto_calculation_enabled = Column(Boolean, default=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), default=func.now())
    updated_at = Column(DateTime(timezone=True), default=func.now(), onupdate=func.now())
    
    # Indexes
    __table_args__ = (
        Index('idx_creator_tax_residence', 'tax_residence_country', 'business_structure'),
        Index('idx_creator_tax_compliance', 'compliance_score', 'updated_at'),
    )

class TaxCalculation(Base):
    """Tax calculations for specific periods and jurisdictions"""
    __tablename__ = 'tax_calculations'
    
    # Primary identification
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    creator_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    jurisdiction_id = Column(UUID(as_uuid=True), ForeignKey('tax_jurisdiction_profiles.id'), nullable=False)
    
    # Calculation period
    tax_period_start = Column(DateTime(timezone=True), nullable=False)
    tax_period_end = Column(DateTime(timezone=True), nullable=False)
    tax_year = Column(Integer, nullable=False)
    tax_quarter = Column(Integer)
    
    # Income breakdown
    gross_income = Column(DECIMAL(15, 4), nullable=False)
    business_income = Column(DECIMAL(15, 4), default=0)
    royalty_income = Column(DECIMAL(15, 4), default=0)
    licensing_income = Column(DECIMAL(15, 4), default=0)
    other_income = Column(DECIMAL(15, 4), default=0)
    
    # Income by source
    platform_income_breakdown = Column(JSONB)
    geographic_income_breakdown = Column(JSONB)
    currency_income_breakdown = Column(JSONB)
    
    # Deductions
    total_deductions = Column(DECIMAL(15, 4), default=0)
    business_expenses = Column(DECIMAL(15, 4), default=0)
    depreciation = Column(DECIMAL(15, 4), default=0)
    professional_fees = Column(DECIMAL(15, 4), default=0)
    home_office_deduction = Column(DECIMAL(15, 4), default=0)
    
    # Detailed deduction breakdown
    deduction_breakdown = Column(JSONB)
    
    # Taxable income calculation
    adjusted_gross_income = Column(DECIMAL(15, 4), nullable=False)
    taxable_income = Column(DECIMAL(15, 4), nullable=False)
    
    # Tax calculations
    tax_type = Column(String(50), nullable=False)
    applicable_tax_rate = Column(Float, nullable=False)
    tax_before_credits = Column(DECIMAL(15, 4), nullable=False)
    tax_credits = Column(DECIMAL(15, 4), default=0)
    final_tax_liability = Column(DECIMAL(15, 4), nullable=False)
    
    # Payments and withholding
    withholding_tax_paid = Column(DECIMAL(15, 4), default=0)
    estimated_payments_made = Column(DECIMAL(15, 4), default=0)
    other_payments = Column(DECIMAL(15, 4), default=0)
    total_payments = Column(DECIMAL(15, 4), default=0)
    
    # Balance due or refund
    amount_owed = Column(DECIMAL(15, 4), default=0)
    refund_due = Column(DECIMAL(15, 4), default=0)
    
    # Calculation metadata
    calculation_method = Column(String(50), nullable=False)  # automatic, manual, hybrid
    calculation_engine_version = Column(String(20))
    confidence_score = Column(Float, default=0.0)
    
    # Supporting data
    source_transactions = Column(JSONB)  # Reference to source revenue data
    calculation_details = Column(JSONB)  # Detailed calculation breakdown
    applied_rules = Column(JSONB)  # Tax rules applied
    
    # Status and workflow
    status = Column(String(20), default=TaxStatus.CALCULATED.value)
    reviewed_by = Column(UUID(as_uuid=True))
    reviewed_at = Column(DateTime(timezone=True))
    approved_by = Column(UUID(as_uuid=True))
    approved_at = Column(DateTime(timezone=True))
    
    # Filing information
    filing_due_date = Column(DateTime(timezone=True))
    extension_requested = Column(Boolean, default=False)
    extended_due_date = Column(DateTime(timezone=True))
    filed_date = Column(DateTime(timezone=True))
    
    # Timestamps
    calculated_at = Column(DateTime(timezone=True), default=func.now())
    created_at = Column(DateTime(timezone=True), default=func.now())
    updated_at = Column(DateTime(timezone=True), default=func.now(), onupdate=func.now())
    
    # Relationships
    jurisdiction = relationship("TaxJurisdictionProfile", backref="tax_calculations")
    
    # Indexes
    __table_args__ = (
        Index('idx_tax_calc_creator_period', 'creator_id', 'tax_period_start'),
        Index('idx_tax_calc_jurisdiction_year', 'jurisdiction_id', 'tax_year'),
        Index('idx_tax_calc_status_due', 'status', 'filing_due_date'),
        UniqueConstraint('creator_id', 'jurisdiction_id', 'tax_period_start', 'tax_type', name='uq_tax_calc_unique'),
    )

class TaxDeduction(Base):
    """Individual tax deduction records"""
    __tablename__ = 'tax_deductions'
    
    # Primary identification
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    calculation_id = Column(UUID(as_uuid=True), ForeignKey('tax_calculations.id'), nullable=False)
    creator_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    
    # Deduction details
    deduction_category = Column(String(50), nullable=False)
    deduction_type = Column(String(100), nullable=False)
    description = Column(String(500), nullable=False)
    
    # Financial details
    deduction_amount = Column(DECIMAL(15, 4), nullable=False)
    currency = Column(String(3), default='USD')
    business_use_percentage = Column(Float, default=100.0)
    deductible_amount = Column(DECIMAL(15, 4), nullable=False)
    
    # Supporting information
    expense_date = Column(DateTime(timezone=True), nullable=False)
    vendor_payee = Column(String(200))
    receipt_reference = Column(String(100))
    invoice_number = Column(String(100))
    
    # Documentation
    supporting_documents = Column(JSONB)  # References to uploaded documents
    receipt_image_path = Column(String(500))
    invoice_image_path = Column(String(500))
    
    # Business justification
    business_purpose = Column(Text)
    business_activity_relation = Column(String(200))
    
    # Approval and validation
    auto_approved = Column(Boolean, default=False)
    requires_review = Column(Boolean, default=False)
    reviewed_by = Column(UUID(as_uuid=True))
    reviewed_at = Column(DateTime(timezone=True))
    approval_status = Column(String(20), default='pending')
    
    # Audit trail
    original_amount = Column(DECIMAL(15, 4))
    adjustment_reason = Column(String(200))
    adjusted_by = Column(UUID(as_uuid=True))
    adjusted_at = Column(DateTime(timezone=True))
    
    # Tax implications
    applicable_jurisdictions = Column(ARRAY(String))
    depreciation_method = Column(String(50))
    depreciation_period_years = Column(Integer)
    remaining_depreciation = Column(DECIMAL(15, 4))
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), default=func.now())
    updated_at = Column(DateTime(timezone=True), default=func.now(), onupdate=func.now())
    
    # Relationships
    tax_calculation = relationship("TaxCalculation", backref="deductions")
    
    # Indexes
    __table_args__ = (
        Index('idx_tax_deduction_creator_category', 'creator_id', 'deduction_category'),
        Index('idx_tax_deduction_calc_amount', 'calculation_id', 'deduction_amount'),
        Index('idx_tax_deduction_date', 'expense_date', 'approval_status'),
    )

class TaxOptimizationStrategy(Base):
    """Tax optimization strategies and recommendations"""
    __tablename__ = 'tax_optimization_strategies'
    
    # Primary identification
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    creator_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    
    # Strategy details
    strategy_name = Column(String(200), nullable=False)
    strategy_type = Column(String(50), nullable=False)  # timing, deduction, structure, jurisdiction
    category = Column(String(50), nullable=False)
    
    # Description and implementation
    description = Column(Text, nullable=False)
    implementation_steps = Column(JSONB)
    requirements = Column(JSONB)
    timeline = Column(String(100))
    
    # Financial impact
    estimated_tax_savings = Column(DECIMAL(15, 4))
    implementation_cost = Column(DECIMAL(15, 4), default=0)
    net_benefit = Column(DECIMAL(15, 4))
    payback_period_months = Column(Integer)
    
    # Risk and complexity
    risk_level = Column(String(20), default='medium')  # low, medium, high
    complexity_level = Column(String(20), default='medium')  # low, medium, high
    regulatory_risk = Column(Float, default=0.0)
    audit_risk_increase = Column(Float, default=0.0)
    
    # Applicability
    applicable_jurisdictions = Column(ARRAY(String))
    income_thresholds = Column(JSONB)
    business_structure_requirements = Column(ARRAY(String))
    
    # Timing and deadlines
    optimal_implementation_timing = Column(String(100))
    deadline_sensitivity = Column(Boolean, default=False)
    election_deadlines = Column(JSONB)
    
    # Professional guidance
    requires_professional_advice = Column(Boolean, default=False)
    recommended_advisors = Column(JSONB)
    legal_documentation_required = Column(Boolean, default=False)
    
    # Performance tracking
    implementation_status = Column(String(20), default='recommended')  # recommended, planned, implementing, implemented, rejected
    implemented_date = Column(DateTime(timezone=True))
    actual_savings_achieved = Column(DECIMAL(15, 4))
    effectiveness_score = Column(Float, default=0.0)
    
    # Validation and approval
    validated_by_professional = Column(Boolean, default=False)
    professional_advisor_id = Column(UUID(as_uuid=True))
    validation_date = Column(DateTime(timezone=True))
    validation_notes = Column(Text)
    
    # Updates and revisions
    strategy_version = Column(String(10), default='1.0')
    superseded_by = Column(UUID(as_uuid=True))
    superseded_date = Column(DateTime(timezone=True))
    
    # Timestamps
    recommended_at = Column(DateTime(timezone=True), default=func.now())
    created_at = Column(DateTime(timezone=True), default=func.now())
    updated_at = Column(DateTime(timezone=True), default=func.now(), onupdate=func.now())
    
    # Indexes
    __table_args__ = (
        Index('idx_tax_strategy_creator_status', 'creator_id', 'implementation_status'),
        Index('idx_tax_strategy_savings', 'estimated_tax_savings', 'risk_level'),
        Index('idx_tax_strategy_type', 'strategy_type', 'category'),
    )

class TaxDocument(Base):
    """Tax-related documents and forms"""
    __tablename__ = 'tax_documents'
    
    # Primary identification
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    creator_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    calculation_id = Column(UUID(as_uuid=True), ForeignKey('tax_calculations.id'))
    
    # Document details
    document_type = Column(String(50), nullable=False)  # tax_return, 1099, w2, receipt, etc.
    document_name = Column(String(200), nullable=False)
    form_number = Column(String(20))  # 1040, 1099-MISC, etc.
    
    # Tax period and jurisdiction
    tax_year = Column(Integer, nullable=False)
    tax_period = Column(String(20))  # annual, q1, q2, q3, q4
    jurisdiction = Column(String(20), nullable=False)
    
    # File information
    file_path = Column(String(500), nullable=False)
    file_name = Column(String(200), nullable=False)
    file_size = Column(BigInteger)
    mime_type = Column(String(100))
    file_hash = Column(String(64))  # SHA-256 hash for integrity
    
    # Document status
    status = Column(String(20), default='draft')  # draft, completed, filed, amended, archived
    is_official = Column(Boolean, default=False)
    is_signed = Column(Boolean, default=False)
    
    # Generation and processing
    generated_automatically = Column(Boolean, default=False)
    generation_engine = Column(String(50))
    source_data_version = Column(String(20))
    
    # Filing information
    filing_method = Column(String(20))  # electronic, paper
    confirmation_number = Column(String(100))
    filed_date = Column(DateTime(timezone=True))
    acceptance_status = Column(String(20))  # accepted, rejected, pending
    
    # Document relationships
    parent_document_id = Column(UUID(as_uuid=True))  # For amendments
    related_documents = Column(ARRAY(String))
    
    # Security and access
    encryption_status = Column(String(20), default='encrypted')
    access_level = Column(String(20), default='private')
    shared_with = Column(JSONB)  # Users with access
    
    # Audit and compliance
    retention_period_years = Column(Integer, default=7)
    retention_deadline = Column(DateTime(timezone=True))
    compliance_checked = Column(Boolean, default=False)
    
    # Timestamps
    document_date = Column(DateTime(timezone=True), nullable=False)
    uploaded_at = Column(DateTime(timezone=True), default=func.now())
    created_at = Column(DateTime(timezone=True), default=func.now())
    updated_at = Column(DateTime(timezone=True), default=func.now(), onupdate=func.now())
    
    # Relationships
    tax_calculation = relationship("TaxCalculation", backref="documents")
    
    # Indexes
    __table_args__ = (
        Index('idx_tax_document_creator_year', 'creator_id', 'tax_year'),
        Index('idx_tax_document_type_status', 'document_type', 'status'),
        Index('idx_tax_document_filed_date', 'filed_date', 'jurisdiction'),
    )

@dataclass
class TaxSummary:
    """Tax summary for reporting"""
    total_income: float
    total_deductions: float
    taxable_income: float
    total_tax_liability: float
    effective_tax_rate: float
    marginal_tax_rate: float
    estimated_payments: float
    refund_or_owed: float
    jurisdictions: List[str]

class TaxAlert(Base):
    """Tax-related alerts and reminders"""
    __tablename__ = 'tax_alerts'
    
    # Primary identification
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    creator_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    
    # Alert details
    alert_type = Column(String(50), nullable=False)  # deadline, opportunity, risk, compliance
    severity = Column(String(20), nullable=False)  # low, medium, high, critical
    title = Column(String(200), nullable=False)
    message = Column(Text, nullable=False)
    
    # Context and specifics
    jurisdiction = Column(String(20))
    tax_type = Column(String(50))
    tax_year = Column(Integer)
    due_date = Column(DateTime(timezone=True))
    
    # Impact assessment
    potential_penalty = Column(DECIMAL(15, 4))
    potential_savings = Column(DECIMAL(15, 4))
    urgency_score = Column(Float, default=0.0)
    
    # Recommended actions
    recommended_actions = Column(JSONB)
    auto_fix_available = Column(Boolean, default=False)
    requires_professional_help = Column(Boolean, default=False)
    
    # Status tracking
    status = Column(String(20), default='active')  # active, acknowledged, resolved, dismissed, expired
    acknowledged_at = Column(DateTime(timezone=True))
    resolved_at = Column(DateTime(timezone=True))
    resolution_notes = Column(Text)
    
    # Notification tracking
    notification_sent = Column(Boolean, default=False)
    reminder_schedule = Column(JSONB)
    last_reminder_sent = Column(DateTime(timezone=True))
    
    # Timestamps
    triggered_at = Column(DateTime(timezone=True), default=func.now())
    expires_at = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), default=func.now())
    updated_at = Column(DateTime(timezone=True), default=func.now(), onupdate=func.now())
    
    # Indexes
    __table_args__ = (
        Index('idx_tax_alert_creator_status', 'creator_id', 'status'),
        Index('idx_tax_alert_severity_due', 'severity', 'due_date'),
        Index('idx_tax_alert_type_year', 'alert_type', 'tax_year'),
    )

# Export all models for easy import
__all__ = [
    'TaxJurisdiction',
    'TaxType',
    'TaxStatus',
    'DeductionCategory',
    'TaxJurisdictionProfile',
    'CreatorTaxProfile',
    'TaxCalculation',
    'TaxDeduction',
    'TaxOptimizationStrategy',
    'TaxDocument',
    'TaxSummary',
    'TaxAlert'
]
