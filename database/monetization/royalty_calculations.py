"""Royalty Calculations - Advanced Royalty and Revenue Calculation Engine

Ultra-sophisticated royalty calculation system with multi-tiered rates,
complex revenue sharing, automated payments, and financial compliance.

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
    ForeignKey, Index, Enum as SQLEnum, Numeric, func,
    CheckConstraint, UniqueConstraint
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, Session
from sqlalchemy.dialects.postgresql import UUID, ARRAY, JSONB
from datetime import datetime, timezone, timedelta
from decimal import Decimal, ROUND_HALF_UP
from enum import Enum
import uuid
from typing import Dict, Any, List, Optional, Union, Tuple
import math

Base = declarative_base()


class CalculationMethod(Enum):
    """Royalty calculation methods"""    SIMPLE_PERCENTAGE = "simple_percentage"
    TIERED_PERCENTAGE = "tiered_percentage"
    FLAT_FEE = "flat_fee"
    PER_UNIT = "per_unit"
    REVENUE_THRESHOLD = "revenue_threshold"
    PERFORMANCE_BASED = "performance_based"
    HYBRID_MODEL = "hybrid_model"
    CUSTOM_FORMULA = "custom_formula"
    BLOCKCHAIN_SMART_CONTRACT = "blockchain_smart_contract"


class TierCriteria(Enum):
    """Criteria for tiered calculations"""    REVENUE_AMOUNT = "revenue_amount"
    USAGE_COUNT = "usage_count"
    TIME_PERIOD = "time_period"
    GEOGRAPHIC_REACH = "geographic_reach"
    PLATFORM_TYPE = "platform_type"
    CONTENT_CATEGORY = "content_category"
    USER_TIER = "user_tier"
    COLLABORATION_SIZE = "collaboration_size"


class DeductionType(Enum):
    """Types of deductions from royalty calculations"""    PLATFORM_FEE = "platform_fee"
    SERVICE_FEE = "service_fee"
    PROCESSING_FEE = "processing_fee"
    TRANSACTION_FEE = "transaction_fee"
    CURRENCY_CONVERSION = "currency_conversion"
    TAX_WITHHOLDING = "tax_withholding"
    ADMIN_FEE = "admin_fee"
    MARKETING_DEDUCTION = "marketing_deduction"
    RECOUPMENT = "recoupment"
    ADVANCE_RECOVERY = "advance_recovery"
    CHARGEBACK = "chargeback"
    PENALTY = "penalty"
    CUSTOM_DEDUCTION = "custom_deduction"


class CalculationStatus(Enum):
    """Status of royalty calculations"""    PENDING = "pending"
    CALCULATING = "calculating"
    COMPLETED = "completed"
    VERIFIED = "verified"
    DISPUTED = "disputed"
    CORRECTED = "corrected"
    FINALIZED = "finalized"
    ARCHIVED = "archived"


class RoyaltyCalculationRule(Base):
    """    Royalty Calculation Rule Model
    
    Defines complex royalty calculation rules with support for
    multi-tiered rates, performance bonuses, and custom formulas.
    """    __tablename__ = "royalty_calculation_rules"
    
    # Primary identification
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    rule_name = Column(String(255), nullable=False, index=True)
    rule_code = Column(String(50), unique=True, nullable=False, index=True)
    
    # Rule applicability
    license_agreement_id = Column(UUID(as_uuid=True), ForeignKey('license_agreements.id'), nullable=True, index=True)
    content_fingerprint_id = Column(UUID(as_uuid=True), nullable=True, index=True)
    platform_filter = Column(ARRAY(String), nullable=True)
    territory_filter = Column(ARRAY(String), nullable=True)
    content_type_filter = Column(ARRAY(String), nullable=True)
    
    # Calculation method
    calculation_method = Column(SQLEnum(CalculationMethod), nullable=False, index=True)
    base_percentage = Column(Numeric(8, 4), nullable=True)
    flat_fee_amount = Column(Numeric(18, 6), nullable=True)
    per_unit_rate = Column(Numeric(18, 6), nullable=True)
    
    # Tiered calculation setup
    tier_criteria = Column(SQLEnum(TierCriteria), nullable=True)
    tier_configuration = Column(JSONB, nullable=True)
    tier_rates = Column(JSONB, nullable=True)
    
    # Performance bonuses
    performance_bonuses = Column(JSONB, nullable=True)
    milestone_bonuses = Column(JSONB, nullable=True)
    volume_discounts = Column(JSONB, nullable=True)
    
    # Minimum and maximum limits
    minimum_payment = Column(Numeric(18, 6), nullable=True)
    maximum_payment = Column(Numeric(18, 6), nullable=True)
    minimum_threshold = Column(Numeric(18, 6), nullable=True)
    payment_cap_per_period = Column(Numeric(18, 6), nullable=True)
    
    # Advanced calculations
    custom_formula = Column(Text, nullable=True)
    formula_variables = Column(JSONB, nullable=True)
    smart_contract_address = Column(String(255), nullable=True)
    blockchain_network = Column(String(100), nullable=True)
    
    # Deduction rules
    allowed_deductions = Column(ARRAY(SQLEnum(DeductionType)), nullable=True)
    deduction_rates = Column(JSONB, nullable=True)
    deduction_caps = Column(JSONB, nullable=True)
    
    # Time-based rules
    effective_date = Column(DateTime(timezone=True), nullable=False)
    expiration_date = Column(DateTime(timezone=True), nullable=True)
    calculation_frequency = Column(String(50), default='monthly')
    payment_delay_days = Column(Integer, default=0)
    
    # Currency and localization
    calculation_currency = Column(String(10), default='EUR')
    exchange_rate_source = Column(String(100), nullable=True)
    rounding_precision = Column(Integer, default=2)
    rounding_method = Column(String(20), default='ROUND_HALF_UP')
    
    # Metadata
    description = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True, index=True)
    priority = Column(Integer, default=1)
    created_by = Column(UUID(as_uuid=True), nullable=False)
    
    # Audit trail
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    license_agreement = relationship("LicenseAgreement", back_populates="calculation_rules")
    calculations = relationship("RoyaltyCalculation", back_populates="calculation_rule")
    
    # Indexes
    __table_args__ = (
        Index('idx_rule_license', 'license_agreement_id'),
        Index('idx_rule_method', 'calculation_method'),
        Index('idx_rule_active', 'is_active'),
        Index('idx_rule_effective', 'effective_date', 'expiration_date'),
        Index('idx_rule_priority', 'priority'),
        
        # Check constraints
        CheckConstraint('base_percentage >= 0 AND base_percentage <= 100', name='check_base_percentage'),
        CheckConstraint('minimum_payment >= 0', name='check_minimum_payment'),
        CheckConstraint('maximum_payment >= 0', name='check_maximum_payment'),
        CheckConstraint('priority > 0', name='check_priority_positive'),
    )


class RoyaltyCalculation(Base):
    """    Royalty Calculation Model
    
    Records individual royalty calculations with detailed breakdown,
    audit trail, and verification status for transparency and compliance.
    """    __tablename__ = "royalty_calculations"
    
    # Primary identification
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    calculation_reference = Column(String(100), unique=True, nullable=False, index=True)
    
    # Associated entities
    license_agreement_id = Column(UUID(as_uuid=True), ForeignKey('license_agreements.id'), nullable=False, index=True)
    calculation_rule_id = Column(UUID(as_uuid=True), ForeignKey('royalty_calculation_rules.id'), nullable=False, index=True)
    revenue_record_id = Column(UUID(as_uuid=True), ForeignKey('revenue_records.id'), nullable=True, index=True)
    
    # Calculation period
    calculation_period_start = Column(DateTime(timezone=True), nullable=False, index=True)
    calculation_period_end = Column(DateTime(timezone=True), nullable=False, index=True)
    calculation_date = Column(DateTime(timezone=True), nullable=False)
    
    # Input data for calculation
    gross_revenue = Column(Numeric(18, 6), nullable=False)
    net_revenue = Column(Numeric(18, 6), nullable=False)
    usage_count = Column(Integer, default=0)
    unique_users = Column(Integer, default=0)
    geographic_reach = Column(Integer, default=0)
    platform_count = Column(Integer, default=0)
    
    # Calculation breakdown
    base_calculation_amount = Column(Numeric(18, 6), nullable=False)
    tier_applied = Column(String(50), nullable=True)
    tier_rate_used = Column(Numeric(8, 4), nullable=True)
    performance_bonus = Column(Numeric(18, 6), default=0.0)
    milestone_bonus = Column(Numeric(18, 6), default=0.0)
    volume_adjustment = Column(Numeric(18, 6), default=0.0)
    
    # Deductions
    total_deductions = Column(Numeric(18, 6), default=0.0)
    deduction_breakdown = Column(JSONB, nullable=True)
    platform_fees = Column(Numeric(18, 6), default=0.0)
    service_fees = Column(Numeric(18, 6), default=0.0)
    processing_fees = Column(Numeric(18, 6), default=0.0)
    tax_withholdings = Column(Numeric(18, 6), default=0.0)
    other_deductions = Column(Numeric(18, 6), default=0.0)
    
    # Final calculation
    gross_royalty_amount = Column(Numeric(18, 6), nullable=False)
    net_royalty_amount = Column(Numeric(18, 6), nullable=False)
    currency = Column(String(10), nullable=False)
    
    # Currency conversion (if applicable)
    original_currency = Column(String(10), nullable=True)
    exchange_rate_used = Column(Numeric(12, 8), default=1.0)
    exchange_rate_date = Column(DateTime(timezone=True), nullable=True)
    
    # Calculation metadata
    calculation_method_used = Column(String(100), nullable=False)
    formula_applied = Column(Text, nullable=True)
    variables_used = Column(JSONB, nullable=True)
    rounding_applied = Column(Boolean, default=True)
    
    # Validation and verification
    status = Column(SQLEnum(CalculationStatus), default=CalculationStatus.PENDING, index=True)
    verification_score = Column(Float, default=1.0)
    anomaly_flags = Column(ARRAY(String), nullable=True)
    validation_errors = Column(JSONB, nullable=True)
    
    # Comparison with previous calculations
    previous_calculation_id = Column(UUID(as_uuid=True), nullable=True)
    variance_from_previous = Column(Numeric(18, 6), nullable=True)
    variance_percentage = Column(Float, nullable=True)
    
    # Processing metadata
    calculation_engine = Column(String(100), nullable=True)
    processing_time_ms = Column(Integer, nullable=True)
    data_sources = Column(ARRAY(String), nullable=True)
    
    # Notes and adjustments
    calculation_notes = Column(Text, nullable=True)
    manual_adjustments = Column(JSONB, nullable=True)
    override_reason = Column(Text, nullable=True)
    
    # Audit trail
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    calculated_by = Column(UUID(as_uuid=True), nullable=True)
    verified_by = Column(UUID(as_uuid=True), nullable=True)
    verified_at = Column(DateTime(timezone=True), nullable=True)
    approved_by = Column(UUID(as_uuid=True), nullable=True)
    approved_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    license_agreement = relationship("LicenseAgreement", back_populates="royalty_calculations")
    calculation_rule = relationship("RoyaltyCalculationRule", back_populates="calculations")
    revenue_record = relationship("RevenueRecord", back_populates="royalty_calculations")
    
    # Indexes
    __table_args__ = (
        Index('idx_calc_license_period', 'license_agreement_id', 'calculation_period_start'),
        Index('idx_calc_rule', 'calculation_rule_id'),
        Index('idx_calc_status', 'status'),
        Index('idx_calc_date', 'calculation_date'),
        Index('idx_calc_amount', 'net_royalty_amount'),
        Index('idx_calc_revenue_record', 'revenue_record_id'),
        
        # Unique constraint to prevent duplicate calculations
        UniqueConstraint('license_agreement_id', 'calculation_period_start', 
                        'calculation_period_end', 'calculation_rule_id',
                        name='uq_calculation_period_rule'),
        
        # Check constraints
        CheckConstraint('gross_revenue >= 0', name='check_gross_revenue_calc'),
        CheckConstraint('net_revenue >= 0', name='check_net_revenue_calc'),
        CheckConstraint('gross_royalty_amount >= 0', name='check_gross_royalty'),
        CheckConstraint('net_royalty_amount >= 0', name='check_net_royalty'),
        CheckConstraint('calculation_period_start <= calculation_period_end', name='check_calc_period'),
    )
    
    def __repr__(self):
        return f"<RoyaltyCalculation(id={self.id}, reference={self.calculation_reference}, amount={self.net_royalty_amount})>"
    
    @property
    def effective_rate(self) -> float:
        """Calculate the effective royalty rate as percentage of gross revenue"""        if self.gross_revenue == 0:
            return 0.0
        return float((self.gross_royalty_amount / self.gross_revenue) * 100)
    
    @property
    def deduction_percentage(self) -> float:
        """Calculate total deductions as percentage of gross royalty"""        if self.gross_royalty_amount == 0:
            return 0.0
        return float((self.total_deductions / self.gross_royalty_amount) * 100)


class TierDefinition(Base):
    """    Tier Definition Model
    
    Defines tiered royalty structures with dynamic rate adjustments
    based on performance metrics and revenue thresholds.
    """    __tablename__ = "tier_definitions"
    
    # Primary identification
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Associated rule
    calculation_rule_id = Column(UUID(as_uuid=True), ForeignKey('royalty_calculation_rules.id'), nullable=False, index=True)
    
    # Tier configuration
    tier_name = Column(String(100), nullable=False)
    tier_level = Column(Integer, nullable=False)
    tier_description = Column(Text, nullable=True)
    
    # Threshold criteria
    criteria_type = Column(SQLEnum(TierCriteria), nullable=False)
    threshold_min = Column(Numeric(18, 6), nullable=False)
    threshold_max = Column(Numeric(18, 6), nullable=True)
    
    # Rate configuration
    royalty_rate = Column(Numeric(8, 4), nullable=False)
    flat_bonus = Column(Numeric(18, 6), default=0.0)
    multiplier = Column(Numeric(8, 4), default=1.0)
    
    # Additional benefits
    performance_bonus_rate = Column(Numeric(8, 4), default=0.0)
    volume_discount_rate = Column(Numeric(8, 4), default=0.0)
    special_benefits = Column(JSONB, nullable=True)
    
    # Time-based configuration
    effective_date = Column(DateTime(timezone=True), nullable=False)
    expiration_date = Column(DateTime(timezone=True), nullable=True)
    
    # Metadata
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    
    # Relationships
    calculation_rule = relationship("RoyaltyCalculationRule", back_populates="tier_definitions")
    
    # Indexes
    __table_args__ = (
        Index('idx_tier_rule', 'calculation_rule_id'),
        Index('idx_tier_level', 'tier_level'),
        Index('idx_tier_criteria', 'criteria_type'),
        Index('idx_tier_threshold', 'threshold_min', 'threshold_max'),
        
        # Unique constraint for tier levels within a rule
        UniqueConstraint('calculation_rule_id', 'tier_level', name='uq_tier_rule_level'),
        
        # Check constraints
        CheckConstraint('tier_level > 0', name='check_tier_level_positive'),
        CheckConstraint('threshold_min >= 0', name='check_threshold_min'),
        CheckConstraint('threshold_max IS NULL OR threshold_max > threshold_min', name='check_threshold_order'),
        CheckConstraint('royalty_rate >= 0 AND royalty_rate <= 100', name='check_tier_royalty_rate'),
    )


class DeductionRule(Base):
    """    Deduction Rule Model
    
    Defines automatic deduction rules for fees, taxes, and other
    charges applied to royalty calculations.
    """    __tablename__ = "deduction_rules"
    
    # Primary identification
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Rule identification
    rule_name = Column(String(255), nullable=False)
    deduction_type = Column(SQLEnum(DeductionType), nullable=False, index=True)
    
    # Applicability
    license_agreement_id = Column(UUID(as_uuid=True), ForeignKey('license_agreements.id'), nullable=True, index=True)
    platform_filter = Column(ARRAY(String), nullable=True)
    territory_filter = Column(ARRAY(String), nullable=True)
    revenue_type_filter = Column(ARRAY(String), nullable=True)
    
    # Deduction calculation
    is_percentage = Column(Boolean, default=True)
    deduction_rate = Column(Numeric(8, 4), nullable=True)  # Percentage rate
    flat_amount = Column(Numeric(18, 6), nullable=True)   # Fixed amount
    
    # Limits and caps
    minimum_deduction = Column(Numeric(18, 6), nullable=True)
    maximum_deduction = Column(Numeric(18, 6), nullable=True)
    cap_per_transaction = Column(Numeric(18, 6), nullable=True)
    cap_per_period = Column(Numeric(18, 6), nullable=True)
    
    # Calculation method
    apply_to_gross = Column(Boolean, default=True)  # Apply to gross vs net
    cascade_order = Column(Integer, default=1)      # Order of application
    compound_with_others = Column(Boolean, default=False)
    
    # Time-based rules
    effective_date = Column(DateTime(timezone=True), nullable=False)
    expiration_date = Column(DateTime(timezone=True), nullable=True)
    
    # Metadata
    description = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True, index=True)
    is_mandatory = Column(Boolean, default=False)
    
    # Audit trail
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    created_by = Column(UUID(as_uuid=True), nullable=False)
    
    # Relationships
    license_agreement = relationship("LicenseAgreement", back_populates="deduction_rules")
    
    # Indexes
    __table_args__ = (
        Index('idx_deduction_type', 'deduction_type'),
        Index('idx_deduction_license', 'license_agreement_id'),
        Index('idx_deduction_active', 'is_active'),
        Index('idx_deduction_order', 'cascade_order'),
        
        # Check constraints
        CheckConstraint('deduction_rate IS NULL OR (deduction_rate >= 0 AND deduction_rate <= 100)', 
                       name='check_deduction_rate'),
        CheckConstraint('flat_amount IS NULL OR flat_amount >= 0', name='check_flat_amount'),
        CheckConstraint('cascade_order > 0', name='check_cascade_order'),
    )


class CalculationAudit(Base):
    """    Calculation Audit Model
    
    Comprehensive audit trail for all royalty calculations with
    detailed change tracking and compliance monitoring.
    """    __tablename__ = "calculation_audits"
    
    # Primary identification
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Audit context
    calculation_id = Column(UUID(as_uuid=True), ForeignKey('royalty_calculations.id'), nullable=False, index=True)
    audit_type = Column(String(50), nullable=False, index=True)  # creation, modification, verification, etc.
    
    # Change details
    field_changed = Column(String(100), nullable=True)
    old_value = Column(Text, nullable=True)
    new_value = Column(Text, nullable=True)
    change_reason = Column(Text, nullable=True)
    
    # Context information
    user_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    user_role = Column(String(100), nullable=True)
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(String(500), nullable=True)
    
    # Additional metadata
    calculation_engine = Column(String(100), nullable=True)
    rule_version = Column(String(50), nullable=True)
    data_snapshot = Column(JSONB, nullable=True)
    
    # Timestamp
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    
    # Relationships
    calculation = relationship("RoyaltyCalculation", back_populates="audit_trail")
    
    # Indexes
    __table_args__ = (
        Index('idx_audit_calculation', 'calculation_id'),
        Index('idx_audit_type', 'audit_type'),
        Index('idx_audit_user', 'user_id'),
        Index('idx_audit_timestamp', 'created_at'),
    )


# Utility functions for royalty calculations

def calculate_tiered_royalty(
    base_amount: Decimal,
    tier_definitions: List[Dict[str, Any]],
    criteria_value: Decimal
) -> Tuple[Decimal, str, Decimal]:
    """    Calculate royalty using tiered structure.
    
    Args:
        base_amount: Base amount to calculate royalty on
        tier_definitions: List of tier configurations
        criteria_value: Value to evaluate against tier thresholds
        
    Returns:
        Tuple of (calculated_amount, tier_applied, rate_used)
    """    applicable_tier = None
    
    # Sort tiers by threshold
    sorted_tiers = sorted(tier_definitions, key=lambda x: x['threshold_min'])
    
    # Find applicable tier
    for tier in sorted_tiers:
        if criteria_value >= tier['threshold_min']:
            if tier['threshold_max'] is None or criteria_value <= tier['threshold_max']:
                applicable_tier = tier
                break
    
    if not applicable_tier:
        return Decimal('0'), 'No applicable tier', Decimal('0')
    
    # Calculate royalty
    rate = Decimal(str(applicable_tier['royalty_rate'])) / Decimal('100')
    calculated_amount = base_amount * rate
    
    # Apply bonuses and multipliers
    if 'flat_bonus' in applicable_tier:
        calculated_amount += Decimal(str(applicable_tier['flat_bonus']))
    
    if 'multiplier' in applicable_tier:
        calculated_amount *= Decimal(str(applicable_tier['multiplier']))
    
    return calculated_amount, applicable_tier['tier_name'], Decimal(str(applicable_tier['royalty_rate']))


def apply_deductions(
    gross_amount: Decimal,
    deduction_rules: List[Dict[str, Any]]
) -> Tuple[Decimal, Dict[str, Decimal]]:
    """    Apply deduction rules to gross amount.
    
    Args:
        gross_amount: Gross amount to apply deductions to
        deduction_rules: List of deduction rule configurations
        
    Returns:
        Tuple of (net_amount, deduction_breakdown)
    """    current_amount = gross_amount
    breakdown = {}
    
    # Sort by cascade order
    sorted_rules = sorted(deduction_rules, key=lambda x: x.get('cascade_order', 1))
    
    for rule in sorted_rules:
        if not rule.get('is_active', True):
            continue
        
        deduction_amount = Decimal('0')
        
        if rule.get('is_percentage', True) and 'deduction_rate' in rule:
            rate = Decimal(str(rule['deduction_rate'])) / Decimal('100')
            if rule.get('apply_to_gross', True):
                deduction_amount = gross_amount * rate
            else:
                deduction_amount = current_amount * rate
        elif 'flat_amount' in rule:
            deduction_amount = Decimal(str(rule['flat_amount']))
        
        # Apply limits
        if 'minimum_deduction' in rule:
            deduction_amount = max(deduction_amount, Decimal(str(rule['minimum_deduction'])))
        
        if 'maximum_deduction' in rule:
            deduction_amount = min(deduction_amount, Decimal(str(rule['maximum_deduction'])))
        
        # Ensure we don't deduct more than available
        deduction_amount = min(deduction_amount, current_amount)
        
        current_amount -= deduction_amount
        breakdown[rule['deduction_type']] = deduction_amount
    
    return current_amount, breakdown


__all__ = [
    'CalculationMethod',
    'TierCriteria',
    'DeductionType',
    'CalculationStatus',
    'RoyaltyCalculationRule',
    'RoyaltyCalculation',
    'TierDefinition',
    'DeductionRule',
    'CalculationAudit',
    'calculate_tiered_royalty',
    'apply_deductions'
]
