"""Royalty Distribution Database Module

Enterprise-grade royalty distribution system for IA Influencer Agent platform.
Provides comprehensive revenue tracking, calculation, and automated payment distribution.

Author: Fahed Mlaiel <mlaiel@live.de>
Expert Team: Lead AI Developer, Backend Senior, ML Engineer, Financial Systems Expert, Payment Specialist

STRICT COPYRIGHT WARNING: This code and concept are EXCLUSIVE intellectual property of Fahed Mlaiel.
ANY unauthorized use, copying, or theft without explicit written authorization is STRICTLY PROHIBITED
and subject to immediate legal prosecution under German law.
Contact: mlaiel@live.de for ANY authorization requests.
"""
from typing import Dict, List, Optional, Any, Union, Tuple, Set
from datetime import datetime, timedelta, timezone
from enum import Enum, IntEnum
from dataclasses import dataclass, field
from decimal import Decimal, ROUND_HALF_UP, ROUND_DOWN
from uuid import UUID, uuid4
import asyncio
import json
import logging
from collections import defaultdict, deque
from concurrent.futures import ThreadPoolExecutor

from sqlalchemy import (
    Column, Integer, String, Text, DateTime, Boolean, 
    Decimal as SQLDecimal, JSON, ForeignKey, ARRAY, Index,
    CheckConstraint, UniqueConstraint, event, func, select,
    and_, or_, case, exists, desc, asc
)
from sqlalchemy.orm import relationship, Session, sessionmaker, validates
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.dialects.postgresql import UUID as PostgresUUID, JSONB
from sqlalchemy.ext.hybrid import hybrid_property, hybrid_method

import redis
from celery import Celery
from pydantic import BaseModel as PydanticModel, validator, Field
from prometheus_client import Counter, Histogram, Gauge

from ..core.database import get_database_session
from ..core.cache import CacheManager
from ..core.security import SecurityManager, encrypt_sensitive_data
from ..models.base import BaseModel, TimestampMixin, AuditMixin
from ..schemas.royalty_schemas import (
    RoyaltyCalculationSchema, PaymentDistributionSchema, RevenueReportSchema,
    RoyaltyRateSchema, PaymentScheduleSchema, TaxCalculationSchema
)
from ..integrations.payment_processors import PaymentProcessorService
from ..integrations.tax_services import TaxCalculationService
from ..integrations.banking import BankingIntegrationService
from ..integrations.blockchain import RoyaltyBlockchainService

# Metrics
royalty_payments_total = Counter('royalty_payments_total', 'Total royalty payments', ['currency', 'status'])
revenue_processed_total = Counter('revenue_processed_total', 'Total revenue processed', ['source', 'platform'])
payment_processing_time = Histogram('payment_processing_seconds', 'Payment processing time')
outstanding_royalties_gauge = Gauge('outstanding_royalties_total', 'Total outstanding royalties')

logger = logging.getLogger(__name__)

class RevenueSource(Enum):
    """Comprehensive revenue sources"""    STREAMING = "streaming"
    DOWNLOAD = "download"
    LICENSING = "licensing"
    SYNCHRONIZATION = "synchronization"
    PERFORMANCE = "performance"
    MECHANICAL = "mechanical"
    ADVERTISING = "advertising"
    SUBSCRIPTION = "subscription"
    MERCHANDISE = "merchandise"
    LIVE_PERFORMANCE = "live_performance"
    RINGTONE = "ringtone"
    KARAOKE = "karaoke"
    BACKGROUND_MUSIC = "background_music"
    FILM_TV = "film_tv"
    COMMERCIAL = "commercial"
    RADIO = "radio"
    PODCAST = "podcast"
    GAMING = "gaming"
    VR_AR = "vr_ar"
    NFT = "nft"
    BLOCKCHAIN = "blockchain"
    SOCIAL_MEDIA = "social_media"
    USER_GENERATED_CONTENT = "user_generated_content"
    COVER_VERSION = "cover_version"
    REMIX = "remix"
    SAMPLE = "sample"

class PaymentStatus(Enum):
    """Payment status tracking"""    PENDING_CALCULATION = "pending_calculation"
    CALCULATED = "calculated"
    PENDING_APPROVAL = "pending_approval"
    APPROVED = "approved"
    PROCESSING = "processing"
    SENT = "sent"
    DELIVERED = "delivered"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    DISPUTED = "disputed"
    REFUNDED = "refunded"
    ON_HOLD = "on_hold"
    MANUALLY_REVIEWED = "manually_reviewed"

class DistributionMethod(Enum):
    """Payment distribution methods"""    BANK_TRANSFER = "bank_transfer"
    WIRE_TRANSFER = "wire_transfer"
    ACH = "ach"
    SEPA = "sepa"
    PAYPAL = "paypal"
    STRIPE = "stripe"
    WISE = "wise"
    CRYPTOCURRENCY = "cryptocurrency"
    CHECK = "check"
    CASH = "cash"
    ESCROW = "escrow"
    SMART_CONTRACT = "smart_contract"

class RoyaltyType(Enum):
    """Types of royalties"""    MECHANICAL = "mechanical"
    PERFORMANCE = "performance"
    SYNC = "synchronization"
    MASTER = "master"
    PUBLISHING = "publishing"
    NEIGHBORING = "neighboring"
    DIGITAL = "digital"
    PRINT = "print"
    GRAND = "grand"
    SMALL = "small"

class TaxTreatment(Enum):
    """Tax treatment classifications"""    GROSS = "gross"
    NET_OF_TAX = "net_of_tax"
    TAX_EXEMPT = "tax_exempt"
    WITHHOLDING_TAX = "withholding_tax"
    VAT_APPLICABLE = "vat_applicable"
    TREATY_BENEFITS = "treaty_benefits"

@dataclass
class RoyaltyRateStructure:
    """Complex royalty rate structure"""    base_rate: Decimal
    minimum_rate: Decimal = Decimal('0.0000')
    maximum_rate: Decimal = Decimal('1.0000')
    escalation_tiers: List[Dict[str, Any]] = field(default_factory=list)
    volume_discounts: List[Dict[str, Any]] = field(default_factory=list)
    territory_multipliers: Dict[str, Decimal] = field(default_factory=dict)
    platform_multipliers: Dict[str, Decimal] = field(default_factory=dict)
    time_based_adjustments: List[Dict[str, Any]] = field(default_factory=list)
    performance_bonuses: List[Dict[str, Any]] = field(default_factory=list)
    
    def calculate_effective_rate(self, context: Dict[str, Any]) -> Decimal:
        """Calculate effective rate based on context"""        effective_rate = self.base_rate
        
        # Apply volume discounts
        volume = context.get('volume', 0)
        for discount in self.volume_discounts:
            if volume >= discount['threshold']:
                effective_rate *= (Decimal('1.0') - Decimal(str(discount['discount_percentage'])))
        
        # Apply territory multiplier
        territory = context.get('territory')
        if territory and territory in self.territory_multipliers:
            effective_rate *= self.territory_multipliers[territory]
        
        # Apply platform multiplier
        platform = context.get('platform')
        if platform and platform in self.platform_multipliers:
            effective_rate *= self.platform_multipliers[platform]
        
        # Ensure within bounds
        return max(self.minimum_rate, min(self.maximum_rate, effective_rate))

@dataclass
class PaymentSplit:
    """Payment split configuration"""    beneficiary_id: str
    beneficiary_type: str  # writer, publisher, performer, producer, etc.
    split_percentage: Decimal
    split_type: str  # percentage, fixed_amount, remainder
    minimum_amount: Decimal = Decimal('0.00')
    maximum_amount: Optional[Decimal] = None
    currency: str = "EUR"
    payment_method: str = "bank_transfer"
    tax_treatment: str = TaxTreatment.GROSS.value
    
    def calculate_amount(self, total_revenue: Decimal) -> Decimal:
        """Calculate split amount from total revenue"""        if self.split_type == "percentage":
            amount = total_revenue * (self.split_percentage / Decimal('100'))
        elif self.split_type == "fixed_amount":
            amount = self.split_percentage  # Used as fixed amount
        else:  # remainder
            amount = total_revenue  # Will be calculated after other splits
        
        # Apply limits
        amount = max(amount, self.minimum_amount)
        if self.maximum_amount:
            amount = min(amount, self.maximum_amount)
        
        return amount.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)

class RevenueReport(BaseModel, TimestampMixin, AuditMixin):
    """    Comprehensive revenue reporting with multi-platform aggregation.
    Tracks all revenue sources with detailed attribution and analytics.
    """    __tablename__ = "revenue_reports"
    
    # Primary identifiers
    id = Column(PostgresUUID(as_uuid=True), primary_key=True, default=uuid4)
    report_id = Column(String(100), unique=True, nullable=False)
    content_id = Column(PostgresUUID(as_uuid=True), nullable=False, index=True)
    
    # Reporting period
    period_start = Column(DateTime(timezone=True), nullable=False)
    period_end = Column(DateTime(timezone=True), nullable=False)
    reporting_frequency = Column(String(20), default="monthly")  # daily, weekly, monthly, quarterly
    
    # Revenue source identification
    platform = Column(String(100), nullable=False, index=True)
    revenue_source = Column(String(50), nullable=False)
    territory = Column(String(100), default="GLOBAL")
    currency = Column(String(3), default="EUR")
    
    # Usage metrics
    total_plays = Column(Integer, default=0)
    total_downloads = Column(Integer, default=0)
    unique_listeners = Column(Integer, default=0)
    listening_hours = Column(SQLDecimal(10, 2), default=Decimal('0.00'))
    skip_rate = Column(SQLDecimal(5, 4), default=Decimal('0.0000'))
    completion_rate = Column(SQLDecimal(5, 4), default=Decimal('0.0000'))
    
    # Revenue data
    gross_revenue = Column(SQLDecimal(12, 4), nullable=False)
    platform_fee = Column(SQLDecimal(12, 4), default=Decimal('0.0000'))
    net_revenue = Column(SQLDecimal(12, 4), nullable=False)
    exchange_rate = Column(SQLDecimal(10, 6), default=Decimal('1.000000'))
    revenue_usd = Column(SQLDecimal(12, 4))  # Normalized to USD
    
    # Attribution and splits
    rights_holders = Column(JSONB, nullable=False)  # List of rights holders and their splits
    royalty_calculations = Column(JSONB, default=dict)
    deductions = Column(JSONB, default=dict)
    adjustments = Column(JSONB, default=dict)
    
    # Detailed analytics
    demographic_data = Column(JSONB, default=dict)
    geographic_distribution = Column(JSONB, default=dict)
    device_breakdown = Column(JSONB, default=dict)
    time_based_analytics = Column(JSONB, default=dict)
    
    # Processing status
    status = Column(String(50), default="raw")  # raw, processed, distributed, archived
    processing_date = Column(DateTime(timezone=True))
    validation_status = Column(String(50), default="pending")
    validation_errors = Column(JSONB, default=list)
    
    # Data quality metrics
    data_confidence_score = Column(SQLDecimal(3, 2), default=Decimal('1.00'))
    source_reliability = Column(String(20), default="high")
    reconciliation_status = Column(String(50), default="pending")
    discrepancy_flags = Column(JSONB, default=list)
    
    # Relationships
    royalty_calculations_rel = relationship("RoyaltyCalculation", back_populates="revenue_report")
    payment_distributions = relationship("PaymentDistribution", back_populates="revenue_report")
    
    # Database constraints and indexes
    __table_args__ = (
        Index('idx_revenue_content_period', 'content_id', 'period_start', 'period_end'),
        Index('idx_revenue_platform_territory', 'platform', 'territory'),
        Index('idx_revenue_source_currency', 'revenue_source', 'currency'),
        Index('idx_revenue_status_processing', 'status', 'processing_date'),
        CheckConstraint('gross_revenue >= 0', name='check_gross_revenue_positive'),
        CheckConstraint('net_revenue >= 0', name='check_net_revenue_positive'),
        CheckConstraint('period_end > period_start', name='check_valid_period'),
        CheckConstraint('data_confidence_score >= 0 AND data_confidence_score <= 1', name='check_confidence_score_valid'),
        UniqueConstraint('content_id', 'platform', 'period_start', 'period_end', name='unique_revenue_period'),
    )
    
    @validates('revenue_source')
    def validate_revenue_source(self, key, revenue_source):
        if revenue_source not in [r.value for r in RevenueSource]:
            raise ValueError(f"Invalid revenue source: {revenue_source}")
        return revenue_source
    
    @hybrid_property
    def effective_royalty_rate(self):
        """Calculate effective royalty rate for the period"""        if self.gross_revenue > 0:
            total_royalties = sum(calc.get('total_amount', 0) for calc in self.royalty_calculations.values())
            return Decimal(str(total_royalties)) / self.gross_revenue
        return Decimal('0.0000')
    
    @hybrid_property
    def revenue_per_play(self):
        """Calculate revenue per play"""        if self.total_plays > 0:
            return self.net_revenue / Decimal(str(self.total_plays))
        return Decimal('0.0000')

class RoyaltyCalculation(BaseModel, TimestampMixin, AuditMixin):
    """    Advanced royalty calculation engine with complex rate structures.
    Supports multi-tier royalty schemes and automated calculations.
    """    __tablename__ = "royalty_calculations"
    
    # Primary identifiers
    id = Column(PostgresUUID(as_uuid=True), primary_key=True, default=uuid4)
    calculation_id = Column(String(100), unique=True, nullable=False)
    revenue_report_id = Column(PostgresUUID(as_uuid=True), ForeignKey('revenue_reports.id'), nullable=False)
    
    # Calculation metadata
    calculation_method = Column(String(50), default="standard")  # standard, pro_rata, waterfall, hybrid
    calculation_date = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    calculated_by = Column(String(50), default="system")  # system, manual, ai
    
    # Rights holder information
    rights_holder_id = Column(PostgresUUID(as_uuid=True), nullable=False, index=True)
    rights_holder_type = Column(String(50), nullable=False)  # writer, publisher, performer, producer
    ownership_percentage = Column(SQLDecimal(5, 4), nullable=False)
    
    # Royalty configuration
    royalty_type = Column(String(50), nullable=False)
    base_rate = Column(SQLDecimal(8, 6), nullable=False)
    effective_rate = Column(SQLDecimal(8, 6), nullable=False)
    rate_structure = Column(JSONB, default=dict)
    
    # Calculation details
    gross_revenue = Column(SQLDecimal(12, 4), nullable=False)
    deductions = Column(JSONB, default=dict)
    adjustments = Column(JSONB, default=dict)
    net_revenue = Column(SQLDecimal(12, 4), nullable=False)
    calculated_amount = Column(SQLDecimal(12, 4), nullable=False)
    
    # Tax and withholding
    tax_treatment = Column(String(50), default=TaxTreatment.GROSS.value)
    withholding_tax_rate = Column(SQLDecimal(5, 4), default=Decimal('0.0000'))
    withholding_tax_amount = Column(SQLDecimal(12, 4), default=Decimal('0.0000'))
    net_payable_amount = Column(SQLDecimal(12, 4), nullable=False)
    
    # Currency handling
    original_currency = Column(String(3), nullable=False)
    payment_currency = Column(String(3), nullable=False)
    exchange_rate = Column(SQLDecimal(10, 6), default=Decimal('1.000000'))
    converted_amount = Column(SQLDecimal(12, 4))
    
    # Validation and approval
    validation_status = Column(String(50), default="pending")
    validation_notes = Column(Text)
    approved_by = Column(PostgresUUID(as_uuid=True))
    approval_date = Column(DateTime(timezone=True))
    
    # Processing metadata
    calculation_complexity = Column(Integer, default=1)  # 1-5 scale
    processing_time_ms = Column(Integer)
    confidence_score = Column(SQLDecimal(3, 2), default=Decimal('1.00'))
    manual_review_required = Column(Boolean, default=False)
    
    # Relationships
    revenue_report = relationship("RevenueReport", back_populates="royalty_calculations_rel")
    payment_distributions_rel = relationship("PaymentDistribution", back_populates="royalty_calculation")
    
    # Database constraints and indexes
    __table_args__ = (
        Index('idx_royalty_holder_type', 'rights_holder_id', 'rights_holder_type'),
        Index('idx_royalty_report_calculation', 'revenue_report_id', 'calculation_date'),
        Index('idx_royalty_status_approval', 'validation_status', 'approval_date'),
        Index('idx_royalty_currency_amount', 'payment_currency', 'calculated_amount'),
        CheckConstraint('ownership_percentage > 0 AND ownership_percentage <= 1', name='check_ownership_percentage_valid'),
        CheckConstraint('base_rate >= 0 AND base_rate <= 1', name='check_base_rate_valid'),
        CheckConstraint('calculated_amount >= 0', name='check_calculated_amount_positive'),
        CheckConstraint('net_payable_amount >= 0', name='check_net_payable_positive'),
        CheckConstraint('confidence_score >= 0 AND confidence_score <= 1', name='check_confidence_score_valid'),
    )
    
    @validates('royalty_type')
    def validate_royalty_type(self, key, royalty_type):
        if royalty_type not in [r.value for r in RoyaltyType]:
            raise ValueError(f"Invalid royalty type: {royalty_type}")
        return royalty_type
    
    @hybrid_property
    def effective_royalty_percentage(self):
        """Calculate effective royalty percentage"""        return self.effective_rate * self.ownership_percentage * Decimal('100')
    
    @hybrid_property
    def total_deductions_amount(self):
        """Calculate total deductions amount"""        return sum(Decimal(str(amount)) for amount in self.deductions.values() if isinstance(amount, (int, float, str)))
    
    def recalculate(self, rate_structure: RoyaltyRateStructure, context: Dict[str, Any]) -> Decimal:
        """Recalculate royalty amount with new parameters"""        # Update effective rate based on context
        self.effective_rate = rate_structure.calculate_effective_rate(context)
        
        # Recalculate amounts
        self.calculated_amount = self.net_revenue * self.effective_rate * self.ownership_percentage
        
        # Apply tax withholding
        self.withholding_tax_amount = self.calculated_amount * self.withholding_tax_rate
        self.net_payable_amount = self.calculated_amount - self.withholding_tax_amount
        
        # Convert currency if needed
        if self.original_currency != self.payment_currency:
            self.converted_amount = self.net_payable_amount * self.exchange_rate
        else:
            self.converted_amount = self.net_payable_amount
        
        return self.converted_amount

class PaymentDistribution(BaseModel, TimestampMixin, AuditMixin):
    """    Comprehensive payment distribution with multi-method support.
    Handles complex payment routing and reconciliation.
    """    __tablename__ = "payment_distributions"
    
    # Primary identifiers
    id = Column(PostgresUUID(as_uuid=True), primary_key=True, default=uuid4)
    distribution_id = Column(String(100), unique=True, nullable=False)
    royalty_calculation_id = Column(PostgresUUID(as_uuid=True), ForeignKey('royalty_calculations.id'), nullable=False)
    revenue_report_id = Column(PostgresUUID(as_uuid=True), ForeignKey('revenue_reports.id'))
    
    # Payment details
    beneficiary_id = Column(PostgresUUID(as_uuid=True), nullable=False, index=True)
    beneficiary_type = Column(String(50), nullable=False)
    payment_amount = Column(SQLDecimal(12, 4), nullable=False)
    payment_currency = Column(String(3), nullable=False)
    
    # Payment method and routing
    distribution_method = Column(String(50), nullable=False)
    payment_processor = Column(String(100))
    payment_account_id = Column(String(255))
    routing_information = Column(JSONB, default=dict)
    
    # Scheduling and timing
    scheduled_date = Column(DateTime(timezone=True))
    payment_frequency = Column(String(20), default="monthly")  # daily, weekly, monthly, quarterly
    minimum_payment_threshold = Column(SQLDecimal(12, 4), default=Decimal('10.00'))
    
    # Status tracking
    status = Column(String(50), default=PaymentStatus.PENDING_CALCULATION.value)
    initiated_at = Column(DateTime(timezone=True))
    completed_at = Column(DateTime(timezone=True))
    failed_at = Column(DateTime(timezone=True))
    
    # Transaction details
    transaction_id = Column(String(255))
    transaction_reference = Column(String(255))
    processor_response = Column(JSONB, default=dict)
    confirmation_code = Column(String(100))
    
    # Fees and costs
    transaction_fee = Column(SQLDecimal(12, 4), default=Decimal('0.0000'))
    exchange_fee = Column(SQLDecimal(12, 4), default=Decimal('0.0000'))
    processing_fee = Column(SQLDecimal(12, 4), default=Decimal('0.0000'))
    total_fees = Column(SQLDecimal(12, 4), default=Decimal('0.0000'))
    net_amount_paid = Column(SQLDecimal(12, 4))
    
    # Error handling and retry
    retry_count = Column(Integer, default=0)
    max_retries = Column(Integer, default=3)
    last_error = Column(Text)
    error_log = Column(JSONB, default=list)
    
    # Reconciliation
    reconciliation_status = Column(String(50), default="pending")
    reconciled_at = Column(DateTime(timezone=True))
    bank_reference = Column(String(255))
    statement_match = Column(Boolean, default=False)
    
    # Compliance and reporting
    tax_reporting_required = Column(Boolean, default=True)
    tax_forms_generated = Column(JSONB, default=list)
    regulatory_reporting = Column(JSONB, default=dict)
    audit_trail = Column(JSONB, default=list)
    
    # Relationships
    royalty_calculation = relationship("RoyaltyCalculation", back_populates="payment_distributions_rel")
    revenue_report = relationship("RevenueReport", back_populates="payment_distributions")
    
    # Database constraints and indexes
    __table_args__ = (
        Index('idx_payment_beneficiary_status', 'beneficiary_id', 'status'),
        Index('idx_payment_method_processor', 'distribution_method', 'payment_processor'),
        Index('idx_payment_scheduled_completed', 'scheduled_date', 'completed_at'),
        Index('idx_payment_currency_amount', 'payment_currency', 'payment_amount'),
        Index('idx_payment_reconciliation', 'reconciliation_status', 'reconciled_at'),
        CheckConstraint('payment_amount > 0', name='check_payment_amount_positive'),
        CheckConstraint('retry_count <= max_retries', name='check_retry_count_valid'),
        CheckConstraint('total_fees >= 0', name='check_total_fees_positive'),
        CheckConstraint('net_amount_paid >= 0', name='check_net_amount_positive'),
    )
    
    @validates('status')
    def validate_status(self, key, status):
        if status not in [s.value for s in PaymentStatus]:
            raise ValueError(f"Invalid payment status: {status}")
        return status
    
    @validates('distribution_method')
    def validate_distribution_method(self, key, method):
        if method not in [m.value for m in DistributionMethod]:
            raise ValueError(f"Invalid distribution method: {method}")
        return method
    
    @hybrid_property
    def processing_time(self):
        """Calculate payment processing time"""        if self.initiated_at and self.completed_at:
            return self.completed_at - self.initiated_at
        return None
    
    @hybrid_property
    def is_overdue(self):
        """Check if payment is overdue"""        if self.scheduled_date and self.status not in [PaymentStatus.COMPLETED.value, PaymentStatus.CANCELLED.value]:
            return datetime.now(timezone.utc) > self.scheduled_date
        return False
    
    @hybrid_property
    def effective_fee_percentage(self):
        """Calculate effective fee percentage"""        if self.payment_amount > 0:
            return (self.total_fees / self.payment_amount) * Decimal('100')
        return Decimal('0.00')

class PaymentSchedule(BaseModel, TimestampMixin):
    """    Automated payment scheduling with configurable rules.
    """    __tablename__ = "payment_schedules"
    
    # Primary identifiers
    id = Column(PostgresUUID(as_uuid=True), primary_key=True, default=uuid4)
    beneficiary_id = Column(PostgresUUID(as_uuid=True), nullable=False, index=True)
    schedule_name = Column(String(255), nullable=False)
    
    # Schedule configuration
    frequency = Column(String(20), nullable=False)  # daily, weekly, monthly, quarterly, annual
    payment_day = Column(Integer)  # Day of month/week
    minimum_threshold = Column(SQLDecimal(12, 4), default=Decimal('10.00'))
    maximum_amount = Column(SQLDecimal(12, 4))
    currency = Column(String(3), default="EUR")
    
    # Distribution settings
    preferred_method = Column(String(50), nullable=False)
    backup_method = Column(String(50))
    payment_account = Column(String(255), nullable=False)
    routing_preferences = Column(JSONB, default=dict)
    
    # Automation rules
    auto_payment_enabled = Column(Boolean, default=True)
    requires_approval = Column(Boolean, default=False)
    approval_threshold = Column(SQLDecimal(12, 4), default=Decimal('1000.00'))
    notification_preferences = Column(JSONB, default=dict)
    
    # Status and lifecycle
    is_active = Column(Boolean, default=True)
    next_payment_date = Column(DateTime(timezone=True))
    last_payment_date = Column(DateTime(timezone=True))
    payments_made = Column(Integer, default=0)
    total_amount_paid = Column(SQLDecimal(12, 4), default=Decimal('0.0000'))
    
    # Database constraints and indexes
    __table_args__ = (
        Index('idx_schedule_beneficiary_active', 'beneficiary_id', 'is_active'),
        Index('idx_schedule_next_payment', 'next_payment_date', 'auto_payment_enabled'),
        Index('idx_schedule_frequency_day', 'frequency', 'payment_day'),
        CheckConstraint('minimum_threshold >= 0', name='check_minimum_threshold_positive'),
class RoyaltyDistributionService:
    """    Enterprise-grade royalty distribution service with automated calculations and payments.
    Provides comprehensive revenue processing, tax handling, and multi-currency support.
    """    
    def __init__(self, db_session: Session, cache_manager: CacheManager, security_manager: SecurityManager):
        self.db = db_session
        self.cache = cache_manager
        self.security = security_manager
        
        # Initialize external services
        self.payment_processor = PaymentProcessorService()
        self.tax_service = TaxCalculationService()
        self.banking_service = BankingIntegrationService()
        self.blockchain_service = RoyaltyBlockchainService()
        
        # Initialize Redis for task queuing
        self.redis_client = redis.Redis(host='localhost', port=6379, db=3)
        
        # Initialize executor for parallel processing
        self.executor = ThreadPoolExecutor(max_workers=20)
        
        logger.info("RoyaltyDistributionService initialized")
    
    async def process_revenue_report(self, revenue_data: Dict[str, Any]) -> RevenueReport:
        """        Process incoming revenue report with comprehensive validation and normalization.
        
        Args:
            revenue_data: Raw revenue data from platform
            
        Returns:
            RevenueReport: Processed revenue report
        """        try:
            # Generate unique report ID
            report_id = self._generate_report_id()
            
            # Validate and normalize revenue data
            normalized_data = await self._validate_and_normalize_revenue_data(revenue_data)
            
            # Create revenue report
            revenue_report = RevenueReport(
                report_id=report_id,
                content_id=normalized_data['content_id'],
                period_start=normalized_data['period_start'],
                period_end=normalized_data['period_end'],
                platform=normalized_data['platform'],
                revenue_source=normalized_data['revenue_source'],
                territory=normalized_data.get('territory', 'GLOBAL'),
                currency=normalized_data['currency'],
                total_plays=normalized_data.get('total_plays', 0),
                total_downloads=normalized_data.get('total_downloads', 0),
                unique_listeners=normalized_data.get('unique_listeners', 0),
                listening_hours=Decimal(str(normalized_data.get('listening_hours', '0.00'))),
                gross_revenue=Decimal(str(normalized_data['gross_revenue'])),
                platform_fee=Decimal(str(normalized_data.get('platform_fee', '0.0000'))),
                net_revenue=Decimal(str(normalized_data['net_revenue'])),
                exchange_rate=Decimal(str(normalized_data.get('exchange_rate', '1.000000'))),
                rights_holders=normalized_data['rights_holders'],
                demographic_data=normalized_data.get('demographic_data', {}),
                geographic_distribution=normalized_data.get('geographic_distribution', {}),
                data_confidence_score=Decimal(str(normalized_data.get('confidence_score', '1.00')))
            )
            
            # Calculate USD equivalent
            if normalized_data['currency'] != 'USD':
                usd_rate = await self._get_exchange_rate(normalized_data['currency'], 'USD')
                revenue_report.revenue_usd = revenue_report.net_revenue * usd_rate
            else:
                revenue_report.revenue_usd = revenue_report.net_revenue
            
            self.db.add(revenue_report)
            self.db.commit()
            self.db.refresh(revenue_report)
            
            # Start royalty calculation process
            asyncio.create_task(self._calculate_royalties_for_report(revenue_report))
            
            # Update metrics
            revenue_processed_total.labels(
                source=revenue_report.revenue_source,
                platform=revenue_report.platform
            ).inc()
            
            logger.info(f"Revenue report processed: {report_id}")
            return revenue_report
            
        except Exception as e:
            logger.error(f"Error processing revenue report: {e}")
            raise
    
    async def calculate_royalties(self, revenue_report_id: str, calculation_config: Dict[str, Any] = None) -> List[RoyaltyCalculation]:
        """        Calculate royalties for all rights holders with advanced rate structures.
        
        Args:
            revenue_report_id: Revenue report to process
            calculation_config: Optional calculation configuration
            
        Returns:
            List[RoyaltyCalculation]: Calculated royalties for all rights holders
        """        revenue_report = self.db.query(RevenueReport).filter(
            RevenueReport.id == revenue_report_id
        ).first()
        
        if not revenue_report:
            raise ValueError(f"Revenue report not found: {revenue_report_id}")
        
        calculations = []
        total_allocated_percentage = Decimal('0.0000')
        
        # Process each rights holder
        for rights_holder in revenue_report.rights_holders:
            try:
                # Get rights holder configuration
                rights_config = await self._get_rights_holder_config(
                    rights_holder['rights_holder_id'],
                    revenue_report.content_id
                )
                
                # Create rate structure
                rate_structure = RoyaltyRateStructure(
                    base_rate=Decimal(str(rights_config['base_rate'])),
                    minimum_rate=Decimal(str(rights_config.get('minimum_rate', '0.0000'))),
                    maximum_rate=Decimal(str(rights_config.get('maximum_rate', '1.0000'))),
                    escalation_tiers=rights_config.get('escalation_tiers', []),
                    volume_discounts=rights_config.get('volume_discounts', []),
                    territory_multipliers=rights_config.get('territory_multipliers', {}),
                    platform_multipliers=rights_config.get('platform_multipliers', {})
                )
                
                # Calculate context for rate determination
                calculation_context = {
                    'volume': revenue_report.total_plays,
                    'territory': revenue_report.territory,
                    'platform': revenue_report.platform,
                    'revenue_source': revenue_report.revenue_source,
                    'period_length_days': (revenue_report.period_end - revenue_report.period_start).days
                }
                
                # Calculate effective rate
                effective_rate = rate_structure.calculate_effective_rate(calculation_context)
                ownership_percentage = Decimal(str(rights_holder['ownership_percentage']))
                
                # Create royalty calculation
                calculation = await self._create_royalty_calculation(
                    revenue_report,
                    rights_holder,
                    rate_structure,
                    effective_rate,
                    ownership_percentage,
                    calculation_context
                )
                
                calculations.append(calculation)
                total_allocated_percentage += ownership_percentage
                
            except Exception as e:
                logger.error(f"Error calculating royalty for rights holder {rights_holder['rights_holder_id']}: {e}")
                continue
        
        # Validate total allocation
        if total_allocated_percentage > Decimal('1.0001'):  # Allow small rounding errors
            logger.warning(f"Total ownership percentage exceeds 100%: {total_allocated_percentage}")
        
        # Update revenue report status
        revenue_report.status = "processed"
        revenue_report.processing_date = datetime.now(timezone.utc)
        self.db.commit()
        
        # Start payment distribution process
        if calculation_config and calculation_config.get('auto_distribute', True):
            asyncio.create_task(self._initiate_payment_distributions(calculations))
        
        return calculations
    
    async def distribute_payments(self, calculation_ids: List[str], distribution_config: Dict[str, Any] = None) -> List[PaymentDistribution]:
        """        Distribute payments to rights holders with multi-method support.
        
        Args:
            calculation_ids: List of royalty calculations to pay
            distribution_config: Payment distribution configuration
            
        Returns:
            List[PaymentDistribution]: Created payment distributions
        """        with payment_processing_time.time():
            distributions = []
            
            for calculation_id in calculation_ids:
                try:
                    calculation = self.db.query(RoyaltyCalculation).filter(
                        RoyaltyCalculation.id == calculation_id
                    ).first()
                    
                    if not calculation:
                        logger.warning(f"Royalty calculation not found: {calculation_id}")
                        continue
                    
                    # Check if payment meets minimum threshold
                    if not await self._meets_payment_threshold(calculation):
                        logger.info(f"Payment below threshold, deferring: {calculation_id}")
                        continue
                    
                    # Get beneficiary payment preferences
                    payment_prefs = await self._get_payment_preferences(calculation.rights_holder_id)
                    
                    # Create payment distribution
                    distribution = await self._create_payment_distribution(
                        calculation,
                        payment_prefs,
                        distribution_config
                    )
                    
                    distributions.append(distribution)
                    
                except Exception as e:
                    logger.error(f"Error creating payment distribution for calculation {calculation_id}: {e}")
                    continue
            
            # Process payments in batches
            await self._process_payment_batches(distributions)
            
            return distributions
    
    async def process_payment_batch(self, distribution_ids: List[str]) -> Dict[str, Any]:
        """        Process a batch of payments with optimal routing and error handling.
        
        Args:
            distribution_ids: List of payment distributions to process
            
        Returns:
            Dict containing batch processing results
        """        batch_results = {
            'successful_payments': [],
            'failed_payments': [],
            'total_amount': Decimal('0.0000'),
            'total_fees': Decimal('0.0000'),
            'processing_time': None
        }
        
        start_time = datetime.now(timezone.utc)
        
        # Group payments by method and processor for optimization
        payment_groups = await self._group_payments_for_processing(distribution_ids)
        
        for group_key, group_distributions in payment_groups.items():
            method, processor = group_key
            
            try:
                # Process group with specific method/processor
                group_results = await self._process_payment_group(
                    group_distributions,
                    method,
                    processor
                )
                
                # Aggregate results
                batch_results['successful_payments'].extend(group_results['successful'])
                batch_results['failed_payments'].extend(group_results['failed'])
                batch_results['total_amount'] += group_results['total_amount']
                batch_results['total_fees'] += group_results['total_fees']
                
            except Exception as e:
                logger.error(f"Error processing payment group {group_key}: {e}")
                # Mark all payments in group as failed
                for dist in group_distributions:
                    dist.status = PaymentStatus.FAILED.value
                    dist.last_error = str(e)
                    dist.failed_at = datetime.now(timezone.utc)
                    batch_results['failed_payments'].append(str(dist.id))
        
        batch_results['processing_time'] = datetime.now(timezone.utc) - start_time
        self.db.commit()
        
        # Update metrics
        for success_id in batch_results['successful_payments']:
            royalty_payments_total.labels(currency='EUR', status='completed').inc()
        
        for failed_id in batch_results['failed_payments']:
            royalty_payments_total.labels(currency='EUR', status='failed').inc()
        
        return batch_results
    
    async def reconcile_payments(self, reconciliation_data: Dict[str, Any]) -> Dict[str, Any]:
        """        Reconcile payments with bank statements and external confirmations.
        
        Args:
            reconciliation_data: Bank statements and confirmation data
            
        Returns:
            Dict containing reconciliation results
        """        reconciliation_results = {
            'matched_payments': [],
            'unmatched_payments': [],
            'discrepancies': [],
            'total_reconciled_amount': Decimal('0.0000')
        }
        
        # Get pending reconciliation payments
        pending_payments = self.db.query(PaymentDistribution).filter(
            PaymentDistribution.reconciliation_status == "pending",
            PaymentDistribution.status == PaymentStatus.SENT.value
        ).all()
        
        # Process bank statement entries
        for statement_entry in reconciliation_data.get('bank_statements', []):
            matched_payment = await self._match_payment_to_statement(
                statement_entry,
                pending_payments
            )
            
            if matched_payment:
                # Update payment status
                matched_payment.reconciliation_status = "reconciled"
                matched_payment.reconciled_at = datetime.now(timezone.utc)
                matched_payment.bank_reference = statement_entry.get('reference')
                matched_payment.statement_match = True
                matched_payment.status = PaymentStatus.COMPLETED.value
                matched_payment.completed_at = datetime.now(timezone.utc)
                
                reconciliation_results['matched_payments'].append(str(matched_payment.id))
                reconciliation_results['total_reconciled_amount'] += matched_payment.net_amount_paid
                
                # Remove from pending list
                pending_payments.remove(matched_payment)
            else:
                reconciliation_results['discrepancies'].append({
                    'statement_entry': statement_entry,
                    'issue': 'no_matching_payment'
                })
        
        # Mark remaining pending payments as unmatched
        for unmatched_payment in pending_payments:
            reconciliation_results['unmatched_payments'].append(str(unmatched_payment.id))
        
        self.db.commit()
        
        return reconciliation_results
    
    async def generate_tax_reports(self, reporting_period: Dict[str, Any]) -> Dict[str, Any]:
        """        Generate comprehensive tax reports for royalty payments.
        
        Args:
            reporting_period: Period for tax reporting
            
        Returns:
            Dict containing generated tax reports
        """        period_start = reporting_period['start_date']
        period_end = reporting_period['end_date']
        
        # Get all completed payments in period
        payments = self.db.query(PaymentDistribution).filter(
            PaymentDistribution.completed_at >= period_start,
            PaymentDistribution.completed_at <= period_end,
            PaymentDistribution.status == PaymentStatus.COMPLETED.value
        ).all()
        
        # Group by beneficiary and generate tax forms
        tax_reports = {}
        
        for payment in payments:
            beneficiary_id = str(payment.beneficiary_id)
            
            if beneficiary_id not in tax_reports:
                tax_reports[beneficiary_id] = {
                    'beneficiary_id': beneficiary_id,
                    'total_payments': Decimal('0.0000'),
                    'total_withholding': Decimal('0.0000'),
                    'payment_details': [],
                    'tax_forms': []
                }
            
            # Get related royalty calculation for tax details
            calculation = payment.royalty_calculation
            
            tax_reports[beneficiary_id]['total_payments'] += payment.net_amount_paid
            tax_reports[beneficiary_id]['total_withholding'] += calculation.withholding_tax_amount
            tax_reports[beneficiary_id]['payment_details'].append({
                'payment_date': payment.completed_at.isoformat(),
                'amount': float(payment.net_amount_paid),
                'currency': payment.payment_currency,
                'withholding_tax': float(calculation.withholding_tax_amount),
                'royalty_type': calculation.royalty_type
            })
        
        # Generate specific tax forms
        for beneficiary_id, report_data in tax_reports.items():
            tax_forms = await self.tax_service.generate_tax_forms(
                beneficiary_id,
                report_data,
                reporting_period
            )
            report_data['tax_forms'] = tax_forms
        
        return tax_reports
    
    async def _validate_and_normalize_revenue_data(self, revenue_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate and normalize incoming revenue data"""        # Implementation would include comprehensive validation
        # For now, return normalized data structure
        normalized = {
            'content_id': revenue_data['content_id'],
            'period_start': revenue_data['period_start'],
            'period_end': revenue_data['period_end'],
            'platform': revenue_data['platform'],
            'revenue_source': revenue_data['revenue_source'],
            'currency': revenue_data['currency'],
            'gross_revenue': revenue_data['gross_revenue'],
            'net_revenue': revenue_data['net_revenue'],
            'rights_holders': revenue_data['rights_holders']
        }
        
        # Add optional fields with defaults
        for field in ['territory', 'total_plays', 'platform_fee', 'exchange_rate']:
            if field in revenue_data:
                normalized[field] = revenue_data[field]
        
        return normalized
    
    async def _calculate_royalties_for_report(self, revenue_report: RevenueReport):
        """Asynchronously calculate royalties for a revenue report"""        try:
            await self.calculate_royalties(str(revenue_report.id))
        except Exception as e:
            logger.error(f"Async royalty calculation failed for report {revenue_report.report_id}: {e}")
    
    async def _get_rights_holder_config(self, rights_holder_id: str, content_id: str) -> Dict[str, Any]:
        """Get rights holder configuration for royalty calculation"""        # This would query the rights holder configuration
        # For now, return default configuration
        return {
            'base_rate': '0.1500',
            'minimum_rate': '0.0500',
            'maximum_rate': '0.5000',
            'escalation_tiers': [],
            'volume_discounts': [],
            'territory_multipliers': {},
            'platform_multipliers': {}
        }
    
    async def _create_royalty_calculation(self, revenue_report: RevenueReport, rights_holder: Dict[str, Any],
                                        rate_structure: RoyaltyRateStructure, effective_rate: Decimal,
                                        ownership_percentage: Decimal, context: Dict[str, Any]) -> RoyaltyCalculation:
        """Create individual royalty calculation"""        calculation_id = self._generate_calculation_id()
        
        # Calculate base amounts
        gross_revenue = revenue_report.net_revenue
        calculated_amount = gross_revenue * effective_rate * ownership_percentage
        
        # Calculate withholding tax if applicable
        withholding_rate = Decimal(str(rights_holder.get('withholding_tax_rate', '0.0000')))
        withholding_amount = calculated_amount * withholding_rate
        net_payable = calculated_amount - withholding_amount
        
        calculation = RoyaltyCalculation(
            calculation_id=calculation_id,
            revenue_report_id=revenue_report.id,
            rights_holder_id=rights_holder['rights_holder_id'],
            rights_holder_type=rights_holder['rights_holder_type'],
            ownership_percentage=ownership_percentage,
            royalty_type=rights_holder.get('royalty_type', 'mechanical'),
            base_rate=rate_structure.base_rate,
            effective_rate=effective_rate,
            rate_structure=rate_structure.__dict__,
            gross_revenue=gross_revenue,
            net_revenue=gross_revenue,
            calculated_amount=calculated_amount,
            withholding_tax_rate=withholding_rate,
            withholding_tax_amount=withholding_amount,
            net_payable_amount=net_payable,
            original_currency=revenue_report.currency,
            payment_currency=rights_holder.get('preferred_currency', revenue_report.currency),
            validation_status="approved"
        )
        
        self.db.add(calculation)
        self.db.commit()
        self.db.refresh(calculation)
        
        return calculation
    
    def _generate_report_id(self) -> str:
        """Generate unique report ID"""        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        random_suffix = str(uuid4())[:8].upper()
        return f"RR-{timestamp}-{random_suffix}"
    
    def _generate_calculation_id(self) -> str:
        """Generate unique calculation ID"""        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        random_suffix = str(uuid4())[:6].upper()
        return f"RC-{timestamp}-{random_suffix}"
    
    def _generate_distribution_id(self) -> str:
        """Generate unique distribution ID"""        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        random_suffix = str(uuid4())[:6].upper()
        return f"PD-{timestamp}-{random_suffix}"

# Export all models and services
__all__ = [
    'RevenueReport', 'RoyaltyCalculation', 'PaymentDistribution', 'PaymentSchedule',
    'RoyaltyDistributionService', 'RevenueSource', 'PaymentStatus', 'DistributionMethod',
    'RoyaltyType', 'TaxTreatment', 'RoyaltyRateStructure', 'PaymentSplit'
]
    BRAND_PARTNERSHIP = "brand_partnership"

class PaymentStatus(Enum):
    """Statuts des paiements"""    PENDING = "pending"
    CALCULATED = "calculated"
    APPROVED = "approved"
    PROCESSING = "processing"
    PAID = "paid"
    FAILED = "failed"
    DISPUTED = "disputed"
    REFUNDED = "refunded"

class DistributionMethod(Enum):
    """Méthodes de distribution"""    EQUAL_SPLIT = "equal_split"
    OWNERSHIP_PERCENTAGE = "ownership_percentage"
    CUSTOM_SPLIT = "custom_split"
    WATERFALL = "waterfall"
    THRESHOLD_BASED = "threshold_based"

class PaymentMethod(Enum):
    """Méthodes de paiement"""    BANK_TRANSFER = "bank_transfer"
    PAYPAL = "paypal"
    STRIPE = "stripe"
    WISE = "wise"
    CRYPTOCURRENCY = "cryptocurrency"
    CHECK = "check"

@dataclass
class RoyaltyRate:
    """Structure des taux de royalties"""    platform: str
    revenue_source: RevenueSource
    base_rate: Decimal
    tier_rates: Optional[Dict[str, Decimal]] = None
    minimum_payout: Optional[Decimal] = None
    currency: str = "EUR"

@dataclass
class SplitConfiguration:
    """Configuration de répartition des revenus"""    recipient_id: int
    percentage: Decimal
    role: str
    minimum_amount: Optional[Decimal] = None
    priority: int = 0

class RoyaltyCalculation(BaseModel):
    """    Modèle de calcul des royalties.
    Gère tous les calculs de distribution de revenus.
    """    __tablename__ = "royalty_calculations"

    # Identifiants
    id = Column(Integer, primary_key=True, index=True)
    calculation_id = Column(String(50), unique=True, index=True, nullable=False)
    
    # Relations
    content_id = Column(Integer, ForeignKey("content_items.id"), nullable=False)
    license_agreement_id = Column(Integer, ForeignKey("license_agreements.id"))
    
    # Période de calcul
    period_start = Column(DateTime, nullable=False)
    period_end = Column(DateTime, nullable=False)
    calculation_date = Column(DateTime, default=datetime.utcnow)
    
    # Revenus de base
    gross_revenue = Column(SQLDecimal(15, 4), nullable=False)
    net_revenue = Column(SQLDecimal(15, 4), nullable=False)
    currency = Column(String(3), default="EUR")
    
    # Détails par source
    revenue_breakdown = Column(JSON, nullable=False)  # Par plateforme/source
    platform_fees = Column(JSON)  # Frais des plateformes
    processing_fees = Column(SQLDecimal(10, 4), default=Decimal('0'))
    
    # Configuration de split
    split_configuration = Column(JSON, nullable=False)
    distribution_method = Column(String(30), nullable=False)
    
    # Résultats
    total_distributed = Column(SQLDecimal(15, 4))
    distribution_details = Column(JSON)
    
    # Statut et validation
    status = Column(String(20), default=PaymentStatus.PENDING.value)
    validated_by_user_id = Column(Integer, ForeignKey("users.id"))
    validation_date = Column(DateTime)
    validation_notes = Column(Text)
    
    # Relations
    content = relationship("ContentItem", back_populates="royalty_calculations")
    license_agreement = relationship("LicenseAgreement")
    validator = relationship("User")
    payments = relationship("RoyaltyPayment", back_populates="calculation")
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if not self.calculation_id:
            self.calculation_id = f"RC-{uuid.uuid4().hex[:8].upper()}"

    def calculate_distributions(self) -> Dict[int, Decimal]:
        """Calcule la distribution des royalties selon la configuration"""        
        if not self.split_configuration:
            raise ValueError("Configuration de split manquante")
        
        distributions = {}
        remaining_amount = self.net_revenue
        
        # Tri par priorité
        splits = sorted(self.split_configuration, key=lambda x: x.get('priority', 0))
        
        for split in splits:
            recipient_id = split['recipient_id']
            percentage = Decimal(str(split['percentage']))
            minimum_amount = Decimal(str(split.get('minimum_amount', 0)))
            
            if self.distribution_method == DistributionMethod.OWNERSHIP_PERCENTAGE.value:
                calculated_amount = self.net_revenue * (percentage / 100)
            elif self.distribution_method == DistributionMethod.WATERFALL.value:
                calculated_amount = min(remaining_amount, minimum_amount) if minimum_amount > 0 else remaining_amount * (percentage / 100)
            else:  # EQUAL_SPLIT ou CUSTOM_SPLIT
                calculated_amount = self.net_revenue * (percentage / 100)
            
            # Application du minimum
            final_amount = max(calculated_amount, minimum_amount)
            
            distributions[recipient_id] = final_amount.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
            remaining_amount -= final_amount
        
        self.distribution_details = {
            str(k): float(v) for k, v in distributions.items()
        }
        self.total_distributed = sum(distributions.values())
        
        return distributions

    def validate_calculation(self, validator_user_id: int, notes: Optional[str] = None) -> bool:
        """Valide le calcul de royalties"""        
        # Vérifications de base
        if self.total_distributed != self.net_revenue:
            raise ValueError("Le total distribué ne correspond pas au revenu net")
        
        if not self.distribution_details:
            raise ValueError("Détails de distribution manquants")
        
        self.status = PaymentStatus.APPROVED.value
        self.validated_by_user_id = validator_user_id
        self.validation_date = datetime.utcnow()
        self.validation_notes = notes
        
        return True

    def to_dict(self) -> Dict[str, Any]:
        """Convertit le calcul en dictionnaire"""        return {
            "id": self.id,
            "calculation_id": self.calculation_id,
            "period_start": self.period_start.isoformat(),
            "period_end": self.period_end.isoformat(),
            "gross_revenue": float(self.gross_revenue),
            "net_revenue": float(self.net_revenue),
            "currency": self.currency,
            "total_distributed": float(self.total_distributed) if self.total_distributed else None,
            "distribution_details": self.distribution_details,
            "status": self.status,
            "created_at": self.created_at.isoformat()
        }

class RoyaltyPayment(BaseModel):
    """    Modèle des paiements de royalties.
    Gère les paiements individuels vers chaque bénéficiaire.
    """    __tablename__ = "royalty_payments"

    # Identifiants
    id = Column(Integer, primary_key=True, index=True)
    payment_id = Column(String(50), unique=True, index=True, nullable=False)
    
    # Relations
    calculation_id = Column(Integer, ForeignKey("royalty_calculations.id"), nullable=False)
    recipient_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Détails du paiement
    amount = Column(SQLDecimal(12, 4), nullable=False)
    currency = Column(String(3), default="EUR")
    payment_method = Column(String(30), nullable=False)
    
    # Informations bancaires/paiement
    payment_details = Column(JSON)  # IBAN, PayPal, etc.
    transaction_reference = Column(String(100))
    external_transaction_id = Column(String(100))
    
    # Statut et suivi
    status = Column(String(20), default=PaymentStatus.PENDING.value)
    scheduled_date = Column(DateTime)
    processed_date = Column(DateTime)
    completed_date = Column(DateTime)
    
    # Frais et ajustements
    processing_fee = Column(SQLDecimal(10, 4), default=Decimal('0'))
    net_amount = Column(SQLDecimal(12, 4))
    exchange_rate = Column(SQLDecimal(10, 6))
    original_currency = Column(String(3))
    
    # Erreurs et retry
    failure_reason = Column(Text)
    retry_count = Column(Integer, default=0)
    max_retries = Column(Integer, default=3)
    
    # Relations
    calculation = relationship("RoyaltyCalculation", back_populates="payments")
    recipient = relationship("User", back_populates="royalty_payments")
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if not self.payment_id:
            self.payment_id = f"RP-{uuid.uuid4().hex[:8].upper()}"
        
        # Calcul du montant net
        if self.amount and self.processing_fee:
            self.net_amount = self.amount - self.processing_fee

    def can_retry(self) -> bool:
        """Vérifie si le paiement peut être retenté"""        return (
            self.status == PaymentStatus.FAILED.value and
            self.retry_count < self.max_retries
        )

    def mark_as_processed(self, transaction_ref: str, external_id: Optional[str] = None):
        """Marque le paiement comme traité"""        self.status = PaymentStatus.PROCESSING.value
        self.processed_date = datetime.utcnow()
        self.transaction_reference = transaction_ref
        self.external_transaction_id = external_id

    def mark_as_completed(self):
        """Marque le paiement comme terminé"""        self.status = PaymentStatus.PAID.value
        self.completed_date = datetime.utcnow()

    def mark_as_failed(self, reason: str):
        """Marque le paiement comme échoué"""        self.status = PaymentStatus.FAILED.value
        self.failure_reason = reason
        self.retry_count += 1

    def to_dict(self) -> Dict[str, Any]:
        """Convertit le paiement en dictionnaire"""        return {
            "id": self.id,
            "payment_id": self.payment_id,
            "recipient_id": self.recipient_id,
            "amount": float(self.amount),
            "net_amount": float(self.net_amount) if self.net_amount else None,
            "currency": self.currency,
            "payment_method": self.payment_method,
            "status": self.status,
            "scheduled_date": self.scheduled_date.isoformat() if self.scheduled_date else None,
            "completed_date": self.completed_date.isoformat() if self.completed_date else None,
            "created_at": self.created_at.isoformat()
        }

class RevenueAnalytics(BaseModel):
    """    Modèle d'analytics des revenus.
    Stocke les métriques et analyses de performance.
    """    __tablename__ = "revenue_analytics"

    # Identifiants
    id = Column(Integer, primary_key=True, index=True)
    analytics_id = Column(String(50), unique=True, index=True, nullable=False)
    
    # Relations
    content_id = Column(Integer, ForeignKey("content_items.id"))
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Période d'analyse
    period_start = Column(DateTime, nullable=False)
    period_end = Column(DateTime, nullable=False)
    analysis_date = Column(DateTime, default=datetime.utcnow)
    
    # Métriques de revenus
    total_revenue = Column(SQLDecimal(15, 4), nullable=False)
    revenue_by_source = Column(JSON, nullable=False)
    revenue_by_platform = Column(JSON, nullable=False)
    
    # Métriques de performance
    total_streams = Column(Integer, default=0)
    total_downloads = Column(Integer, default=0)
    unique_listeners = Column(Integer, default=0)
    geographical_distribution = Column(JSON)
    
    # Analytics avancées
    growth_metrics = Column(JSON)
    trend_analysis = Column(JSON)
    predictive_metrics = Column(JSON)
    
    # Comparaisons
    previous_period_comparison = Column(JSON)
    industry_benchmarks = Column(JSON)
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if not self.analytics_id:
            self.analytics_id = f"RA-{uuid.uuid4().hex[:8].upper()}"

class RoyaltyDistributionManager:
    """    Gestionnaire pour la distribution des royalties.
    Fournit une interface complète pour la gestion des paiements.
    """
    def __init__(self, db_session: Session):
        self.db = db_session
        self.logger = logging.getLogger(__name__)
        
        # Configuration des taux par défaut
        self.default_rates = self._load_default_rates()

    def create_calculation(
        self,
        content_id: int,
        period_start: datetime,
        period_end: datetime,
        revenue_data: Dict[str, Any],
        split_config: List[SplitConfiguration],
        distribution_method: DistributionMethod = DistributionMethod.OWNERSHIP_PERCENTAGE
    ) -> RoyaltyCalculation:
        """Crée un nouveau calcul de royalties"""        
        try:
            # Calcul des revenus nets
            gross_revenue = Decimal(str(revenue_data['gross_revenue']))
            platform_fees = self._calculate_platform_fees(revenue_data)
            processing_fees = gross_revenue * Decimal('0.029')  # 2.9% processing fee
            net_revenue = gross_revenue - platform_fees - processing_fees
            
            # Création du calcul
            calculation = RoyaltyCalculation(
                content_id=content_id,
                period_start=period_start,
                period_end=period_end,
                gross_revenue=gross_revenue,
                net_revenue=net_revenue,
                revenue_breakdown=revenue_data,
                processing_fees=processing_fees,
                split_configuration=[asdict(split) for split in split_config],
                distribution_method=distribution_method.value
            )
            
            # Calcul des distributions
            calculation.calculate_distributions()
            
            self.db.add(calculation)
            self.db.commit()
            self.db.refresh(calculation)
            
            self.logger.info(f"Calcul de royalties créé: {calculation.calculation_id}")
            return calculation
            
        except Exception as e:
            self.db.rollback()
            self.logger.error(f"Erreur création calcul: {str(e)}")
            raise

    def process_payments(
        self,
        calculation_id: str,
        scheduled_date: Optional[datetime] = None
    ) -> List[RoyaltyPayment]:
        """Traite les paiements pour un calcul donné"""        
        try:
            calculation = self.db.query(RoyaltyCalculation).filter(
                RoyaltyCalculation.calculation_id == calculation_id
            ).first()
            
            if not calculation:
                raise ValueError(f"Calcul non trouvé: {calculation_id}")
            
            if calculation.status != PaymentStatus.APPROVED.value:
                raise ValueError("Calcul non approuvé")
            
            payments = []
            scheduled_date = scheduled_date or datetime.utcnow()
            
            for recipient_id_str, amount in calculation.distribution_details.items():
                recipient_id = int(recipient_id_str)
                
                # Récupération des informations de paiement du bénéficiaire
                payment_info = self._get_recipient_payment_info(recipient_id)
                
                if not payment_info:
                    self.logger.warning(f"Infos paiement manquantes pour user {recipient_id}")
                    continue
                
                # Création du paiement
                payment = RoyaltyPayment(
                    calculation_id=calculation.id,
                    recipient_id=recipient_id,
                    amount=Decimal(str(amount)),
                    payment_method=payment_info['method'],
                    payment_details=payment_info['details'],
                    scheduled_date=scheduled_date
                )
                
                payments.append(payment)
                self.db.add(payment)
            
            # Mise à jour du statut du calcul
            calculation.status = PaymentStatus.PROCESSING.value
            
            self.db.commit()
            
            self.logger.info(f"{len(payments)} paiements créés pour {calculation_id}")
            return payments
            
        except Exception as e:
            self.db.rollback()
            self.logger.error(f"Erreur traitement paiements: {str(e)}")
            raise

    def execute_payment(self, payment_id: str) -> bool:
        """Exécute un paiement individuel"""        
        try:
            payment = self.db.query(RoyaltyPayment).filter(
                RoyaltyPayment.payment_id == payment_id
            ).first()
            
            if not payment:
                raise ValueError(f"Paiement non trouvé: {payment_id}")
            
            # Exécution selon la méthode
            success = False
            transaction_ref = None
            
            if payment.payment_method == PaymentMethod.STRIPE.value:
                success, transaction_ref = self._execute_stripe_payment(payment)
            elif payment.payment_method == PaymentMethod.PAYPAL.value:
                success, transaction_ref = self._execute_paypal_payment(payment)
            elif payment.payment_method == PaymentMethod.WISE.value:
                success, transaction_ref = self._execute_wise_payment(payment)
            elif payment.payment_method == PaymentMethod.BANK_TRANSFER.value:
                success, transaction_ref = self._execute_bank_transfer(payment)
            
            if success and transaction_ref:
                payment.mark_as_processed(transaction_ref)
                # Note: Le mark_as_completed sera fait par webhook/callback
                self.db.commit()
                self.logger.info(f"Paiement exécuté: {payment_id}")
                return True
            else:
                payment.mark_as_failed("Échec de l'exécution du paiement")
                self.db.commit()
                return False
                
        except Exception as e:
            self.logger.error(f"Erreur exécution paiement {payment_id}: {str(e)}")
            return False

    def generate_revenue_report(
        self,
        user_id: int,
        start_date: datetime,
        end_date: datetime,
        content_ids: Optional[List[int]] = None
    ) -> Dict[str, Any]:
        """Génère un rapport de revenus détaillé"""        
        # Récupération des calculs pour la période
        query = self.db.query(RoyaltyCalculation).filter(
            RoyaltyCalculation.period_start >= start_date,
            RoyaltyCalculation.period_end <= end_date
        )
        
        if content_ids:
            query = query.filter(RoyaltyCalculation.content_id.in_(content_ids))
        
        calculations = query.all()
        
        # Récupération des paiements pour l'utilisateur
        payments = self.db.query(RoyaltyPayment).filter(
            RoyaltyPayment.recipient_id == user_id,
            RoyaltyPayment.created_at >= start_date,
            RoyaltyPayment.created_at <= end_date
        ).all()
        
        # Calculs d'agrégation
        total_earned = sum([p.amount for p in payments if p.status == PaymentStatus.PAID.value])
        total_pending = sum([p.amount for p in payments if p.status in [PaymentStatus.PENDING.value, PaymentStatus.PROCESSING.value]])
        
        # Analyse par source
        revenue_by_source = defaultdict(Decimal)
        revenue_by_platform = defaultdict(Decimal)
        
        for calc in calculations:
            if calc.distribution_details and str(user_id) in calc.distribution_details:
                user_amount = Decimal(str(calc.distribution_details[str(user_id)]))
                
                # Répartition par source
                for source, amount in calc.revenue_breakdown.items():
                    proportion = Decimal(str(amount)) / calc.gross_revenue
                    allocated_amount = user_amount * proportion
                    revenue_by_source[source] += allocated_amount
        
        # Création du rapport
        report = {
            "user_id": user_id,
            "period": {
                "start": start_date.isoformat(),
                "end": end_date.isoformat()
            },
            "summary": {
                "total_earned": float(total_earned),
                "total_pending": float(total_pending),
                "payment_count": len(payments),
                "calculation_count": len(calculations)
            },
            "revenue_breakdown": {
                "by_source": {k: float(v) for k, v in revenue_by_source.items()},
                "by_platform": {k: float(v) for k, v in revenue_by_platform.items()}
            },
            "payments": [p.to_dict() for p in payments[-10:]],  # Derniers 10 paiements
            "performance_metrics": self._calculate_performance_metrics(user_id, start_date, end_date),
            "generated_at": datetime.utcnow().isoformat()
        }
        
        return report

    def retry_failed_payments(self) -> List[str]:
        """Retente les paiements échoués éligibles"""        
        failed_payments = self.db.query(RoyaltyPayment).filter(
            RoyaltyPayment.status == PaymentStatus.FAILED.value
        ).all()
        
        retried_payments = []
        
        for payment in failed_payments:
            if payment.can_retry():
                success = self.execute_payment(payment.payment_id)
                if success:
                    retried_payments.append(payment.payment_id)
        
        return retried_payments

    def _calculate_platform_fees(self, revenue_data: Dict[str, Any]) -> Decimal:
        """Calcule les frais des plateformes"""        
        total_fees = Decimal('0')
        
        platform_fee_rates = {
            "spotify": Decimal('0.30'),      # 30%
            "apple_music": Decimal('0.30'),   # 30%
            "youtube": Decimal('0.45'),       # 45%
            "instagram": Decimal('0.00'),     # Gratuit
            "tiktok": Decimal('0.50'),        # 50%
        }
        
        for platform, revenue in revenue_data.get('by_platform', {}).items():
            fee_rate = platform_fee_rates.get(platform.lower(), Decimal('0.35'))  # 35% par défaut
            fee = Decimal(str(revenue)) * fee_rate
            total_fees += fee
        
        return total_fees

    def _get_recipient_payment_info(self, user_id: int) -> Optional[Dict[str, Any]]:
        """Récupère les informations de paiement d'un utilisateur"""        logger = logging.getLogger(__name__)
        
        try:
            # Récupérer depuis la base de données en production
            # Pour maintenant, simulation sécurisée avec validation
            
            # Cache check first
            cache_manager = CacheManager()
            cache_key = f"user_payment_info:{user_id}"
            cached_info = cache_manager.get(cache_key)
            
            if cached_info:
                logger.debug(f"Retrieved cached payment info for user {user_id}")
                return json.loads(cached_info)
            
            # Simulate database query
            # En production, ceci interrogerait user_payment_methods table
            payment_info = self._simulate_user_payment_lookup(user_id)
            
            if payment_info:
                # Cache for 1 hour
                cache_manager.set(cache_key, json.dumps(payment_info), ttl=3600)
                logger.info(f"Retrieved payment info for user {user_id}")
                return payment_info
            else:
                logger.warning(f"No payment info found for user {user_id}")
                return None
                
        except Exception as e:
            logger.error(f"Error retrieving payment info for user {user_id}: {e}")
            return None
    
    def _simulate_user_payment_lookup(self, user_id: int) -> Optional[Dict[str, Any]]:
        """Simulate user payment method lookup"""        # En production, ceci serait une vraie requête SQL
        # Simulation basée sur l'ID utilisateur pour la cohérence
        
        payment_methods = [
            {
                "method": PaymentMethod.STRIPE.value,
                "details": {
                    "stripe_account_id": f"acct_{user_id}stripe{hash(user_id) % 10000}",
                    "currency": "EUR",
                    "verified": True
                }
            },
            {
                "method": PaymentMethod.PAYPAL.value,
                "details": {
                    "paypal_email": f"user{user_id}@example.com",
                    "verified": True
                }
            },
            {
                "method": PaymentMethod.BANK_TRANSFER.value,
                "details": {
                    "iban": f"DE89370400440532{user_id:06d}",
                    "bic": "COBADEFFXXX",
                    "account_holder": f"User {user_id}",
                    "bank_name": "Commerzbank AG"
                }
            }
        ]
        
        # Retourner la méthode préférée basée sur l'ID utilisateur
        preferred_method_index = user_id % len(payment_methods)
        return payment_methods[preferred_method_index]

    def _execute_stripe_payment(self, payment: RoyaltyPayment) -> Tuple[bool, Optional[str]]:
        """Exécute un paiement via Stripe"""        logger = logging.getLogger(__name__)
        
        try:
            # Validation des données de paiement
            if not payment.amount or payment.amount <= 0:
                logger.error("Invalid payment amount for Stripe")
                return False, None
            
            # Récupérer les détails du destinataire
            recipient_info = self._get_recipient_payment_info(payment.user_id)
            if not recipient_info or recipient_info.get('method') != PaymentMethod.STRIPE.value:
                logger.error(f"No valid Stripe account for user {payment.user_id}")
                return False, None
            
            stripe_details = recipient_info.get('details', {})
            stripe_account_id = stripe_details.get('stripe_account_id')
            
            if not stripe_account_id:
                logger.error(f"No Stripe account ID for user {payment.user_id}")
                return False, None
            
            # Simulation sécurisée du paiement Stripe
            # En production, ceci utiliserait l'API Stripe réelle
            transaction_id = f"stripe_payout_{uuid4().hex[:12]}"
            
            # Log de la transaction simulée
            payout_data = {
                "amount": str(payment.amount),
                "currency": payment.currency.value,
                "destination": stripe_account_id,
                "source_transaction": None,
                "description": f"Royalty payout for user {payment.user_id}",
                "metadata": {
                    "user_id": payment.user_id,
                    "calculation_id": getattr(payment, 'calculation_id', None),
                    "period": getattr(payment, 'period', None)
                }
            }
            
            logger.info(f"Stripe payout simulated: {transaction_id} - {payout_data}")
            
            # En production:
            # stripe.Payout.create(**payout_data)
            
            return True, transaction_id
            
        except Exception as e:
            logger.error(f"Stripe payment execution failed: {e}")
            return False, None

    def _execute_paypal_payment(self, payment: RoyaltyPayment) -> Tuple[bool, Optional[str]]:
        """Exécute un paiement via PayPal"""        logger = logging.getLogger(__name__)
        
        try:
            # Validation des données de paiement
            if not payment.amount or payment.amount <= 0:
                logger.error("Invalid payment amount for PayPal")
                return False, None
            
            # Minimum payout check (PayPal requirement)
            if payment.amount < Decimal('1.00'):
                logger.error(f"PayPal minimum payout is 1.00, got {payment.amount}")
                return False, None
            
            # Récupérer les détails du destinataire
            recipient_info = self._get_recipient_payment_info(payment.user_id)
            if not recipient_info or recipient_info.get('method') != PaymentMethod.PAYPAL.value:
                logger.error(f"No valid PayPal account for user {payment.user_id}")
                return False, None
            
            paypal_details = recipient_info.get('details', {})
            paypal_email = paypal_details.get('paypal_email')
            
            if not paypal_email:
                logger.error(f"No PayPal email for user {payment.user_id}")
                return False, None
            
            # Simulation sécurisée du paiement PayPal
            # En production, ceci utiliserait l'API PayPal Payouts
            transaction_id = f"paypal_payout_{uuid4().hex[:12]}"
            
            # Données de paiement PayPal
            payout_data = {
                "sender_batch_header": {
                    "sender_batch_id": transaction_id,
                    "email_subject": "Royalty Payment",
                    "email_message": f"Your royalty payment for period {getattr(payment, 'period', 'current')}"
                },
                "items": [{
                    "recipient_type": "EMAIL",
                    "amount": {
                        "value": str(payment.amount),
                        "currency": payment.currency.value
                    },
                    "receiver": paypal_email,
                    "note": f"Royalty payout for user {payment.user_id}",
                    "sender_item_id": f"royalty_{payment.user_id}_{uuid4().hex[:8]}"
                }]
            }
            
            logger.info(f"PayPal payout simulated: {transaction_id} - {payout_data}")
            
            # En production:
            # paypal_client.payouts().create(payout_data)
            
            return True, transaction_id
            
        except Exception as e:
            logger.error(f"PayPal payment execution failed: {e}")
            return False, None

    def _execute_wise_payment(self, payment: RoyaltyPayment) -> Tuple[bool, Optional[str]]:
        """Exécute un paiement via Wise"""        logger = logging.getLogger(__name__)
        
        try:
            # Validation des données de paiement
            if not payment.amount or payment.amount <= 0:
                logger.error("Invalid payment amount for Wise")
                return False, None
            
            # Minimum payout check (Wise requirement)
            if payment.amount < Decimal('10.00'):
                logger.error(f"Wise minimum payout is 10.00, got {payment.amount}")
                return False, None
            
            # Récupérer les détails du destinataire
            recipient_info = self._get_recipient_payment_info(payment.user_id)
            if not recipient_info or recipient_info.get('method') != PaymentMethod.WISE.value:
                logger.error(f"No valid Wise account for user {payment.user_id}")
                return False, None
            
            wise_details = recipient_info.get('details', {})
            wise_recipient_id = wise_details.get('wise_recipient_id')
            
            if not wise_recipient_id:
                logger.error(f"No Wise recipient ID for user {payment.user_id}")
                return False, None
            
            # Simulation sécurisée du paiement Wise
            # En production, ceci utiliserait l'API Wise Transfers
            transaction_id = f"wise_transfer_{uuid4().hex[:12]}"
            
            # Données de transfert Wise
            transfer_data = {
                "targetAccount": wise_recipient_id,
                "quoteUuid": f"quote_{uuid4().hex[:8]}",
                "customerTransactionId": transaction_id,
                "details": {
                    "reference": f"Royalty payment for user {payment.user_id}",
                    "transferPurpose": "VERIFICATION_OF_DEPOSIT",
                    "sourceOfFunds": "ROYALTY_PAYMENTS"
                }
            }
            
            logger.info(f"Wise transfer simulated: {transaction_id} - {transfer_data}")
            
            # En production:
            # wise_client.transfers.create(transfer_data)
            
            return True, transaction_id
            
        except Exception as e:
            logger.error(f"Wise payment execution failed: {e}")
            return False, None

    def _execute_bank_transfer(self, payment: RoyaltyPayment) -> Tuple[bool, Optional[str]]:
        """Exécute un virement bancaire"""        logger = logging.getLogger(__name__)
        
        try:
            # Validation des données de paiement
            if not payment.amount or payment.amount <= 0:
                logger.error("Invalid payment amount for bank transfer")
                return False, None
            
            # Minimum transfer check
            if payment.amount < Decimal('50.00'):
                logger.warning(f"Bank transfer amount below recommended minimum: {payment.amount}")
            
            # Récupérer les détails du destinataire
            recipient_info = self._get_recipient_payment_info(payment.user_id)
            if not recipient_info or recipient_info.get('method') != PaymentMethod.BANK_TRANSFER.value:
                logger.error(f"No valid bank account for user {payment.user_id}")
                return False, None
            
            bank_details = recipient_info.get('details', {})
            iban = bank_details.get('iban')
            bic = bank_details.get('bic')
            account_holder = bank_details.get('account_holder')
            
            if not all([iban, bic, account_holder]):
                logger.error(f"Incomplete bank details for user {payment.user_id}")
                return False, None
            
            # Validation IBAN basique
            if not self._validate_iban(iban):
                logger.error(f"Invalid IBAN for user {payment.user_id}: {iban}")
                return False, None
            
            # Simulation sécurisée du virement bancaire
            # En production, ceci utiliserait l'API bancaire ou SEPA
            transaction_id = f"bank_transfer_{uuid4().hex[:12]}"
            
            # Données de virement
            transfer_data = {
                "debtor_account": "DE89370400440532000000",  # Compte de l'entreprise
                "debtor_name": "Ainflue Platform",
                "creditor_account": iban,
                "creditor_name": account_holder,
                "creditor_bic": bic,
                "amount": str(payment.amount),
                "currency": payment.currency.value,
                "reference": f"ROYALTY PAYOUT USER {payment.user_id}",
                "instruction_id": transaction_id,
                "end_to_end_id": f"ROY{payment.user_id}{uuid4().hex[:8].upper()}"
            }
            
            logger.info(f"Bank transfer simulated: {transaction_id} - {transfer_data}")
            
            # En production:
            # banking_api.execute_sepa_transfer(transfer_data)
            
            return True, transaction_id
            
        except Exception as e:
            logger.error(f"Bank transfer execution failed: {e}")
            return False, None
    
    def _validate_iban(self, iban: str) -> bool:
        """Validation basique de l'IBAN"""        try:
            # Supprimer les espaces et convertir en majuscules
            iban = iban.replace(' ', '').upper()
            
            # Vérifier la longueur (entre 15 et 34 caractères)
            if len(iban) < 15 or len(iban) > 34:
                return False
            
            # Vérifier que les 2 premiers caractères sont des lettres
            if not iban[:2].isalpha():
                return False
            
            # Vérifier que les caractères 3-4 sont des chiffres
            if not iban[2:4].isdigit():
                return False
            
            # Validation modulo 97 simplifiée (pour la démo)
            # En production, utiliser une bibliothèque IBAN complète
            return True
            
        except Exception:
            return False

    def _load_default_rates(self) -> Dict[str, RoyaltyRate]:
        """Charge les taux de royalties par défaut"""        
        return {
            "spotify_streaming": RoyaltyRate(
                platform="spotify",
                revenue_source=RevenueSource.STREAMING,
                base_rate=Decimal('0.004'),  # 0.4 cents par stream
                tier_rates={
                    "premium": Decimal('0.006'),
                    "free": Decimal('0.002')
                }
            ),
            "youtube_advertising": RoyaltyRate(
                platform="youtube",
                revenue_source=RevenueSource.ADVERTISING,
                base_rate=Decimal('0.55'),  # 55% de partage
                minimum_payout=Decimal('100.00')
            )
        }

    def _calculate_performance_metrics(
        self,
        user_id: int,
        start_date: datetime,
        end_date: datetime
    ) -> Dict[str, Any]:
        """Calcule les métriques de performance"""        logger = logging.getLogger(__name__)
        
        try:
            # Période de calcul
            period_days = (end_date - start_date).days
            
            # Simulation de récupération des données de revenus
            # En production, ceci interrogerait les tables de revenus et de contenu
            current_revenue = self._get_period_revenue(user_id, start_date, end_date)
            previous_start = start_date - timedelta(days=period_days)
            previous_end = start_date
            previous_revenue = self._get_period_revenue(user_id, previous_start, previous_end)
            
            # Calcul de la croissance
            revenue_growth = 0.0
            if previous_revenue > 0:
                revenue_growth = ((current_revenue - previous_revenue) / previous_revenue) * 100
            
            # Analyse du contenu le plus performant
            best_content = self._get_best_performing_content(user_id, start_date, end_date)
            
            # Source de revenus principale
            revenue_sources = self._analyze_revenue_sources(user_id, start_date, end_date)
            top_source = max(revenue_sources.items(), key=lambda x: x[1]) if revenue_sources else ("unknown", 0)
            
            # Revenus moyens mensuels
            monthly_revenue = current_revenue
            if period_days > 30:
                monthly_revenue = current_revenue * (30 / period_days)
            
            # Métriques de tendance
            trend_data = self._calculate_trend_metrics(user_id, start_date, end_date)
            
            # Métriques de diversification
            diversification_score = self._calculate_diversification_score(revenue_sources)
            
            metrics = {
                "period": {
                    "start_date": start_date.isoformat(),
                    "end_date": end_date.isoformat(),
                    "duration_days": period_days
                },
                "revenue": {
                    "current_period": float(current_revenue),
                    "previous_period": float(previous_revenue),
                    "growth_percentage": round(revenue_growth, 2),
                    "average_monthly": round(float(monthly_revenue), 2)
                },
                "performance": {
                    "best_performing_content": best_content,
                    "top_revenue_source": top_source[0],
                    "top_source_amount": float(top_source[1]),
                    "diversification_score": diversification_score
                },
                "trends": trend_data,
                "sources_breakdown": {
                    source: float(amount) for source, amount in revenue_sources.items()
                },
                "insights": self._generate_performance_insights(
                    revenue_growth, diversification_score, trend_data
                )
            }
            
            logger.info(f"Performance metrics calculated for user {user_id}: {metrics['revenue']['growth_percentage']}% growth")
            return metrics
            
        except Exception as e:
            logger.error(f"Error calculating performance metrics for user {user_id}: {e}")
            return {
                "error": str(e),
                "revenue_growth": 0.0,
                "best_performing_content": "Data unavailable",
                "top_revenue_source": "unknown",
                "average_monthly_revenue": 0.0
            }
    
    def _get_period_revenue(self, user_id: int, start_date: datetime, end_date: datetime) -> Decimal:
        """Récupère les revenus pour une période donnée"""        # Simulation basée sur l'ID utilisateur et la période
        base_revenue = Decimal(str(100 + (user_id % 1000)))
        period_multiplier = Decimal(str((end_date - start_date).days / 30))
        growth_factor = Decimal('1.05') ** ((datetime.utcnow() - start_date).days / 30)
        
        return base_revenue * period_multiplier * growth_factor
    
    def _get_best_performing_content(self, user_id: int, start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        """Identifie le contenu le plus performant"""        # Simulation
        content_types = ["Music Track", "Video Content", "Podcast Episode", "Digital Art", "Audio Sample"]
        content_type = content_types[user_id % len(content_types)]
        
        return {
            "title": f"{content_type} - User {user_id} Best",
            "type": content_type.lower().replace(" ", "_"),
            "revenue": float(50 + (user_id % 200)),
            "engagement_score": round(0.5 + (user_id % 50) / 100, 2)
        }
    
    def _analyze_revenue_sources(self, user_id: int, start_date: datetime, end_date: datetime) -> Dict[str, Decimal]:
        """Analyse les sources de revenus"""        # Simulation de répartition des sources
        total_revenue = self._get_period_revenue(user_id, start_date, end_date)
        
        # Répartition variable selon l'utilisateur
        if user_id % 3 == 0:  # Utilisateur orienté streaming
            return {
                "streaming": total_revenue * Decimal('0.6'),
                "downloads": total_revenue * Decimal('0.25'),
                "licensing": total_revenue * Decimal('0.15')
            }
        elif user_id % 3 == 1:  # Utilisateur orienté licensing
            return {
                "licensing": total_revenue * Decimal('0.5'),
                "streaming": total_revenue * Decimal('0.3'),
                "sync_licensing": total_revenue * Decimal('0.2')
            }
        else:  # Utilisateur diversifié
            return {
                "streaming": total_revenue * Decimal('0.35'),
                "downloads": total_revenue * Decimal('0.25'),
                "licensing": total_revenue * Decimal('0.20'),
                "sync_licensing": total_revenue * Decimal('0.20')
            }
    
    def _calculate_trend_metrics(self, user_id: int, start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        """Calcule les métriques de tendance"""        return {
            "momentum": "increasing" if user_id % 2 == 0 else "stable",
            "volatility": "low" if user_id % 4 == 0 else "medium",
            "seasonality_factor": round(0.8 + (user_id % 20) / 50, 2),
            "prediction_confidence": round(0.7 + (user_id % 30) / 100, 2)
        }
    
    def _calculate_diversification_score(self, revenue_sources: Dict[str, Decimal]) -> float:
        """Calcule le score de diversification (0-1)"""        if not revenue_sources:
            return 0.0
        
        # Calcul de l'entropie pour mesurer la diversification
        total = sum(revenue_sources.values())
        if total == 0:
            return 0.0
        
        entropy = 0.0
        for amount in revenue_sources.values():
            if amount > 0:
                ratio = float(amount / total)
                entropy -= ratio * (ratio.bit_length() - 1) if ratio > 0 else 0
        
        # Normaliser l'entropie (score entre 0 et 1)
        max_entropy = (len(revenue_sources).bit_length() - 1) if len(revenue_sources) > 1 else 1
        return round(entropy / max_entropy if max_entropy > 0 else 0, 2)
    
    def _generate_performance_insights(self, growth: float, diversification: float, trends: Dict[str, Any]) -> List[str]:
        """Génère des insights sur la performance"""        insights = []
        
        if growth > 10:
            insights.append("Strong revenue growth indicates successful content strategy")
        elif growth < -5:
            insights.append("Revenue decline suggests need for strategy adjustment")
        
        if diversification > 0.7:
            insights.append("Well-diversified revenue streams reduce risk")
        elif diversification < 0.3:
            insights.append("Consider diversifying revenue sources")
        
        if trends.get("momentum") == "increasing":
            insights.append("Positive momentum suggests continued growth potential")
        
        if trends.get("volatility") == "high":
            insights.append("High volatility indicates unpredictable revenue patterns")
        
        return insights
