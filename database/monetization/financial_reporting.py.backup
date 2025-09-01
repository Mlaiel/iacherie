"""Financial Reporting Models - Enterprise Financial Reporting & Compliance System

Ultra-advanced financial reporting system for comprehensive financial analysis,
regulatory compliance, and business intelligence for content creators.

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

class ReportType(Enum):
    """Financial report types"""
    INCOME_STATEMENT = "income_statement"
    BALANCE_SHEET = "balance_sheet"
    CASH_FLOW = "cash_flow"
    PROFIT_LOSS = "profit_loss"
    TAX_REPORT = "tax_report"
    REVENUE_SUMMARY = "revenue_summary"
    EXPENSE_REPORT = "expense_report"
    ROYALTY_STATEMENT = "royalty_statement"
    COMPLIANCE_REPORT = "compliance_report"
    AUDIT_REPORT = "audit_report"

class ReportingPeriod(Enum):
    """Reporting period types"""
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    YEARLY = "yearly"
    CUSTOM = "custom"

class ReportStatus(Enum):
    """Report generation status"""
    PENDING = "pending"
    GENERATING = "generating"
    COMPLETED = "completed"
    FAILED = "failed"
    ARCHIVED = "archived"

class ComplianceStandard(Enum):
    """Financial compliance standards"""
    GAAP = "gaap"
    IFRS = "ifrs"
    SOX = "sox"
    GDPR = "gdpr"
    PCI_DSS = "pci_dss"
    ISO27001 = "iso27001"
    SOC2 = "soc2"

class FinancialReport(Base):
    """Master financial report record"""
    __tablename__ = 'financial_reports'
    
    # Primary identification
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    report_number = Column(String(100), unique=True, nullable=False)
    creator_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    
    # Report metadata
    report_type = Column(String(50), nullable=False)
    report_title = Column(String(200), nullable=False)
    report_description = Column(Text)
    
    # Reporting period
    period_type = Column(String(20), nullable=False)
    period_start = Column(DateTime(timezone=True), nullable=False)
    period_end = Column(DateTime(timezone=True), nullable=False)
    fiscal_year = Column(Integer, nullable=False)
    fiscal_quarter = Column(Integer)
    
    # Report generation
    status = Column(String(20), default=ReportStatus.PENDING.value)
    generated_by = Column(UUID(as_uuid=True), nullable=False)
    generation_started_at = Column(DateTime(timezone=True))
    generation_completed_at = Column(DateTime(timezone=True))
    generation_duration = Column(Integer)  # seconds
    
    # Report content
    total_revenue = Column(DECIMAL(15, 4), default=0)
    total_expenses = Column(DECIMAL(15, 4), default=0)
    net_income = Column(DECIMAL(15, 4), default=0)
    gross_profit = Column(DECIMAL(15, 4), default=0)
    operating_income = Column(DECIMAL(15, 4), default=0)
    
    # Currency and localization
    base_currency = Column(String(3), default='USD')
    exchange_rates = Column(JSONB)
    locale = Column(String(10), default='en_US')
    
    # File references
    pdf_file_path = Column(String(500))
    excel_file_path = Column(String(500))
    csv_file_path = Column(String(500))
    json_data = Column(JSONB)
    
    # Compliance and audit
    compliance_standards = Column(ARRAY(String))
    audit_trail = Column(JSONB)
    approval_status = Column(String(20), default='pending')
    approved_by = Column(UUID(as_uuid=True))
    approved_at = Column(DateTime(timezone=True))
    
    # Distribution
    recipients = Column(JSONB)
    distribution_status = Column(String(20), default='pending')
    distributed_at = Column(DateTime(timezone=True))
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), default=func.now())
    updated_at = Column(DateTime(timezone=True), default=func.now(), onupdate=func.now())
    
    # Indexes
    __table_args__ = (
        Index('idx_financial_report_creator', 'creator_id', 'report_type'),
        Index('idx_financial_report_period', 'period_start', 'period_end'),
        Index('idx_financial_report_fiscal', 'fiscal_year', 'fiscal_quarter'),
        Index('idx_financial_report_status', 'status', 'created_at'),
    )

class RevenueLineItem(Base):
    """Detailed revenue line items for financial reports"""
    __tablename__ = 'revenue_line_items'
    
    # Primary identification
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    report_id = Column(UUID(as_uuid=True), ForeignKey('financial_reports.id'), nullable=False)
    
    # Line item details
    line_item_number = Column(Integer, nullable=False)
    category = Column(String(100), nullable=False)
    subcategory = Column(String(100))
    description = Column(String(500), nullable=False)
    
    # Financial data
    amount = Column(DECIMAL(15, 4), nullable=False)
    currency = Column(String(3), default='USD')
    quantity = Column(Integer, default=1)
    unit_price = Column(DECIMAL(15, 4))
    
    # Platform and source
    platform_id = Column(String(100))
    platform_name = Column(String(100))
    revenue_source = Column(String(100))
    content_id = Column(UUID(as_uuid=True))
    
    # Temporal data
    transaction_date = Column(DateTime(timezone=True))
    recognition_date = Column(DateTime(timezone=True))
    payment_date = Column(DateTime(timezone=True))
    
    # Geographic data
    country_code = Column(String(2))
    region = Column(String(100))
    tax_jurisdiction = Column(String(100))
    
    # Tax information
    gross_amount = Column(DECIMAL(15, 4))
    tax_amount = Column(DECIMAL(15, 4), default=0)
    net_amount = Column(DECIMAL(15, 4))
    tax_rate = Column(Float, default=0.0)
    
    # Accounting classification
    account_code = Column(String(50))
    cost_center = Column(String(50))
    project_code = Column(String(50))
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), default=func.now())
    
    # Relationship
    financial_report = relationship("FinancialReport", backref="revenue_line_items")
    
    # Indexes
    __table_args__ = (
        Index('idx_revenue_line_report', 'report_id', 'line_item_number'),
        Index('idx_revenue_line_category', 'category', 'subcategory'),
        Index('idx_revenue_line_platform', 'platform_id', 'transaction_date'),
    )

class ExpenseLineItem(Base):
    """Detailed expense line items for financial reports"""
    __tablename__ = 'expense_line_items'
    
    # Primary identification
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    report_id = Column(UUID(as_uuid=True), ForeignKey('financial_reports.id'), nullable=False)
    
    # Line item details
    line_item_number = Column(Integer, nullable=False)
    expense_category = Column(String(100), nullable=False)
    expense_type = Column(String(100), nullable=False)
    description = Column(String(500), nullable=False)
    
    # Financial data
    amount = Column(DECIMAL(15, 4), nullable=False)
    currency = Column(String(3), default='USD')
    quantity = Column(Integer, default=1)
    unit_cost = Column(DECIMAL(15, 4))
    
    # Vendor and payment information
    vendor_name = Column(String(200))
    vendor_id = Column(UUID(as_uuid=True))
    invoice_number = Column(String(100))
    payment_method = Column(String(50))
    payment_reference = Column(String(100))
    
    # Dates
    expense_date = Column(DateTime(timezone=True), nullable=False)
    payment_date = Column(DateTime(timezone=True))
    due_date = Column(DateTime(timezone=True))
    
    # Tax and deductions
    gross_amount = Column(DECIMAL(15, 4))
    tax_deductible_amount = Column(DECIMAL(15, 4), default=0)
    tax_amount = Column(DECIMAL(15, 4), default=0)
    net_amount = Column(DECIMAL(15, 4))
    
    # Classification
    business_purpose = Column(String(500))
    account_code = Column(String(50))
    cost_center = Column(String(50))
    project_code = Column(String(50))
    is_recurring = Column(Boolean, default=False)
    
    # Approval workflow
    approval_status = Column(String(20), default='pending')
    approved_by = Column(UUID(as_uuid=True))
    approved_at = Column(DateTime(timezone=True))
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), default=func.now())
    
    # Relationship
    financial_report = relationship("FinancialReport", backref="expense_line_items")
    
    # Indexes
    __table_args__ = (
        Index('idx_expense_line_report', 'report_id', 'line_item_number'),
        Index('idx_expense_line_category', 'expense_category', 'expense_type'),
        Index('idx_expense_line_date', 'expense_date', 'payment_date'),
    )

class TaxSummary(Base):
    """Tax summary information for financial reports"""
    __tablename__ = 'tax_summaries'
    
    # Primary identification
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    report_id = Column(UUID(as_uuid=True), ForeignKey('financial_reports.id'), nullable=False)
    
    # Tax jurisdiction
    jurisdiction = Column(String(100), nullable=False)
    tax_authority = Column(String(200))
    tax_id_number = Column(String(50))
    
    # Tax calculations
    gross_income = Column(DECIMAL(15, 4), default=0)
    taxable_income = Column(DECIMAL(15, 4), default=0)
    tax_rate = Column(Float, default=0.0)
    tax_owed = Column(DECIMAL(15, 4), default=0)
    tax_paid = Column(DECIMAL(15, 4), default=0)
    tax_balance = Column(DECIMAL(15, 4), default=0)
    
    # Deductions and credits
    total_deductions = Column(DECIMAL(15, 4), default=0)
    business_expenses = Column(DECIMAL(15, 4), default=0)
    depreciation = Column(DECIMAL(15, 4), default=0)
    tax_credits = Column(DECIMAL(15, 4), default=0)
    
    # Detailed breakdowns
    income_by_source = Column(JSONB)
    deductions_by_category = Column(JSONB)
    tax_payments_by_period = Column(JSONB)
    
    # Filing information
    filing_status = Column(String(20), default='pending')
    filing_deadline = Column(DateTime(timezone=True))
    filed_date = Column(DateTime(timezone=True))
    extension_requested = Column(Boolean, default=False)
    extension_deadline = Column(DateTime(timezone=True))
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), default=func.now())
    updated_at = Column(DateTime(timezone=True), default=func.now(), onupdate=func.now())
    
    # Relationship
    financial_report = relationship("FinancialReport", backref="tax_summaries")
    
    # Indexes
    __table_args__ = (
        Index('idx_tax_summary_report', 'report_id', 'jurisdiction'),
        Index('idx_tax_summary_deadline', 'filing_deadline', 'filing_status'),
    )

class ComplianceCheck(Base):
    """Compliance verification records"""
    __tablename__ = 'compliance_checks'
    
    # Primary identification
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    report_id = Column(UUID(as_uuid=True), ForeignKey('financial_reports.id'), nullable=False)
    
    # Compliance details
    standard = Column(String(50), nullable=False)
    requirement_id = Column(String(100), nullable=False)
    requirement_description = Column(Text)
    
    # Check results
    status = Column(String(20), nullable=False)  # compliant, non_compliant, warning, pending
    severity = Column(String(20))  # low, medium, high, critical
    score = Column(Float, default=0.0)  # 0-100 compliance score
    
    # Details
    check_description = Column(Text)
    findings = Column(Text)
    recommendations = Column(Text)
    remediation_steps = Column(JSONB)
    
    # Evidence and documentation
    supporting_documents = Column(JSONB)
    evidence_links = Column(ARRAY(String))
    test_data = Column(JSONB)
    
    # Responsible parties
    checked_by = Column(UUID(as_uuid=True), nullable=False)
    reviewed_by = Column(UUID(as_uuid=True))
    approved_by = Column(UUID(as_uuid=True))
    
    # Timeline
    check_date = Column(DateTime(timezone=True), default=func.now())
    review_date = Column(DateTime(timezone=True))
    next_check_date = Column(DateTime(timezone=True))
    remediation_deadline = Column(DateTime(timezone=True))
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), default=func.now())
    updated_at = Column(DateTime(timezone=True), default=func.now(), onupdate=func.now())
    
    # Relationship
    financial_report = relationship("FinancialReport", backref="compliance_checks")
    
    # Indexes
    __table_args__ = (
        Index('idx_compliance_report_standard', 'report_id', 'standard'),
        Index('idx_compliance_status_severity', 'status', 'severity'),
        Index('idx_compliance_check_date', 'check_date', 'next_check_date'),
    )

class ReportTemplate(Base):
    """Financial report templates for standardized reporting"""
    __tablename__ = 'report_templates'
    
    # Primary identification
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    template_name = Column(String(200), nullable=False, unique=True)
    template_code = Column(String(50), nullable=False, unique=True)
    
    # Template metadata
    report_type = Column(String(50), nullable=False)
    description = Column(Text)
    version = Column(String(20), default='1.0')
    is_active = Column(Boolean, default=True)
    
    # Template structure
    sections = Column(JSONB, nullable=False)  # Report sections and structure
    required_fields = Column(JSONB)  # Required data fields
    optional_fields = Column(JSONB)  # Optional data fields
    calculations = Column(JSONB)  # Calculation formulas
    
    # Formatting and layout
    header_template = Column(Text)
    footer_template = Column(Text)
    styling_config = Column(JSONB)
    page_layout = Column(JSONB)
    
    # Compliance and standards
    compliance_standards = Column(ARRAY(String))
    regulatory_requirements = Column(JSONB)
    audit_requirements = Column(JSONB)
    
    # Usage tracking
    usage_count = Column(Integer, default=0)
    last_used_at = Column(DateTime(timezone=True))
    created_by = Column(UUID(as_uuid=True), nullable=False)
    
    # Access control
    visibility = Column(String(20), default='public')  # public, private, organization
    allowed_roles = Column(ARRAY(String))
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), default=func.now())
    updated_at = Column(DateTime(timezone=True), default=func.now(), onupdate=func.now())
    
    # Indexes
    __table_args__ = (
        Index('idx_template_type_active', 'report_type', 'is_active'),
        Index('idx_template_usage', 'usage_count', 'last_used_at'),
    )

@dataclass
class FinancialInsight:
    """Financial insight data structure"""
    insight_type: str
    category: str
    title: str
    description: str
    value: float
    change_percentage: float
    trend: str  # increasing, decreasing, stable
    significance: str  # low, medium, high
    recommendations: List[str]
    supporting_data: Dict[str, Any]

class ReportSchedule(Base):
    """Automated report generation schedules"""
    __tablename__ = 'report_schedules'
    
    # Primary identification
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    schedule_name = Column(String(200), nullable=False)
    creator_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    
    # Report configuration
    report_type = Column(String(50), nullable=False)
    template_id = Column(UUID(as_uuid=True), ForeignKey('report_templates.id'))
    report_title_template = Column(String(200))
    
    # Schedule configuration
    frequency = Column(String(20), nullable=False)  # daily, weekly, monthly, quarterly, yearly
    schedule_day = Column(Integer)  # Day of month for monthly/quarterly/yearly
    schedule_time = Column(String(8))  # HH:MM:SS format
    timezone = Column(String(50), default='UTC')
    
    # Recipients and distribution
    recipients = Column(JSONB, nullable=False)
    distribution_channels = Column(ARRAY(String))  # email, sftp, api, dashboard
    
    # Status and control
    is_active = Column(Boolean, default=True)
    last_run_at = Column(DateTime(timezone=True))
    next_run_at = Column(DateTime(timezone=True))
    run_count = Column(Integer, default=0)
    failure_count = Column(Integer, default=0)
    
    # Configuration
    auto_approve = Column(Boolean, default=False)
    include_attachments = Column(Boolean, default=True)
    compress_files = Column(Boolean, default=True)
    retention_days = Column(Integer, default=365)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), default=func.now())
    updated_at = Column(DateTime(timezone=True), default=func.now(), onupdate=func.now())
    
    # Relationship
    template = relationship("ReportTemplate", backref="schedules")
    
    # Indexes
    __table_args__ = (
        Index('idx_schedule_creator_active', 'creator_id', 'is_active'),
        Index('idx_schedule_next_run', 'next_run_at', 'is_active'),
    )

# Export all models for easy import
__all__ = [
    'ReportType',
    'ReportingPeriod',
    'ReportStatus',
    'ComplianceStandard',
    'FinancialReport',
    'RevenueLineItem',
    'ExpenseLineItem',
    'TaxSummary',
    'ComplianceCheck',
    'ReportTemplate',
    'FinancialInsight',
    'ReportSchedule'
]
