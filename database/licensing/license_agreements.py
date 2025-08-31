"""License Agreements Database Module

Enterprise-grade license agreements management for IA Influencer Agent platform.
Provides comprehensive contract management, legal validation, and automated agreement processing.

Author: Fahed Mlaiel <mlaiel@live.de>
Expert Team: Lead AI Developer, Backend Senior, ML Engineer, DBA, Legal Compliance Expert, Contract Specialist

STRICT COPYRIGHT WARNING: This code and concept are EXCLUSIVE intellectual property of Fahed Mlaiel.
ANY unauthorized use, copying, or theft without explicit written authorization is STRICTLY PROHIBITED
and subject to immediate legal prosecution under German law.
Contact: mlaiel@live.de for ANY authorization requests.
"""from typing import Dict, List, Optional, Any, Union, Tuple, Set, Callable
from datetime import datetime, timedelta, timezone
from enum import Enum, IntEnum
from dataclasses import dataclass, field
from decimal import Decimal, ROUND_HALF_UP
from uuid import UUID, uuid4
import asyncio
import json
import hashlib
import logging
from pathlib import Path
from collections import defaultdict

from sqlalchemy import (
    Column, Integer, String, Text, DateTime, Boolean, 
    Decimal as SQLDecimal, JSON, ForeignKey, ARRAY, Index,
    CheckConstraint, UniqueConstraint, event, func, select,
    and_, or_, case, exists, desc
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
from ..schemas.licensing_schemas import (
    LicenseAgreementSchema, LicenseTermsSchema, LicenseValidationSchema,
    ContractClauseSchema, RightsPackageSchema, ComplianceCheckSchema
)
from ..ai.contract_generator import ContractGenerator
from ..ai.legal_analyzer import LegalAnalyzer
from ..integrations.digital_signature import DigitalSignatureService
from ..integrations.legal_services import ContractLegalService

# Metrics
license_agreements_total = Counter('license_agreements_total', 'Total license agreements', ['type', 'status'])
contract_generation_time = Histogram('contract_generation_seconds', 'Contract generation time')
legal_validation_time = Histogram('legal_validation_seconds', 'Legal validation time')
active_agreements_gauge = Gauge('active_agreements_total', 'Total active agreements')

logger = logging.getLogger(__name__)

class LicenseType(Enum):
    """Comprehensive license types with industry standards"""    STANDARD = "standard"
    PREMIUM = "premium"
    EXCLUSIVE = "exclusive"
    NON_EXCLUSIVE = "non_exclusive"
    COMMERCIAL = "commercial"
    NON_COMMERCIAL = "non_commercial"
    EDUCATIONAL = "educational"
    EDITORIAL = "editorial"
    CREATIVE_COMMONS = "creative_commons"
    ROYALTY_FREE = "royalty_free"
    RIGHTS_MANAGED = "rights_managed"
    REVENUE_SHARE = "revenue_share"
    SYNC_LICENSE = "sync_license"
    MASTER_LICENSE = "master_license"
    MECHANICAL_LICENSE = "mechanical_license"
    PERFORMANCE_LICENSE = "performance_license"
    PRINT_LICENSE = "print_license"
    DIGITAL_LICENSE = "digital_license"
    BROADCAST_LICENSE = "broadcast_license"
    STREAMING_LICENSE = "streaming_license"
    EXHIBITION_LICENSE = "exhibition_license"
    DISTRIBUTION_LICENSE = "distribution_license"
    ADAPTATION_LICENSE = "adaptation_license"
    TRANSLATION_LICENSE = "translation_license"
    MERCHANDISING_LICENSE = "merchandising_license"
    SAMPLING_LICENSE = "sampling_license"
    CUSTOM = "custom"

class LicenseStatus(Enum):
    """Comprehensive license status tracking"""    DRAFT = "draft"
    TEMPLATE_GENERATED = "template_generated"
    UNDER_REVIEW = "under_review"
    LEGAL_REVIEW = "legal_review"
    COMPLIANCE_CHECK = "compliance_check"
    PENDING_SIGNATURE = "pending_signature"
    PARTIALLY_SIGNED = "partially_signed"
    FULLY_EXECUTED = "fully_executed"
    ACTIVE = "active"
    SUSPENDED = "suspended"
    EXPIRED = "expired"
    TERMINATED = "terminated"
    BREACHED = "breached"
    DISPUTED = "disputed"
    RENEWED = "renewed"
    CANCELLED = "cancelled"
    ARCHIVED = "archived"

class ContractComplexity(IntEnum):
    """Contract complexity levels for AI processing"""    SIMPLE = 1
    STANDARD = 2
    INTERMEDIATE = 3
    COMPLEX = 4
    HIGHLY_COMPLEX = 5

class SignatureType(Enum):
    """Digital signature types"""    ELECTRONIC = "electronic"
    DIGITAL = "digital"
    BIOMETRIC = "biometric"
    BLOCKCHAIN = "blockchain"
    NOTARIZED = "notarized"
    WET_SIGNATURE = "wet_signature"

class ValidationLevel(Enum):
    """Legal validation levels"""    BASIC = "basic"
    STANDARD = "standard"
    COMPREHENSIVE = "comprehensive"
    EXPERT_REVIEW = "expert_review"
    MULTI_JURISDICTION = "multi_jurisdiction"

@dataclass
class ContractTerms:
    """Comprehensive contract terms structure"""    grant_of_rights: Dict[str, Any] = field(default_factory=dict)
    usage_restrictions: Dict[str, Any] = field(default_factory=dict)
    territory: List[str] = field(default_factory=list)
    duration: Dict[str, Any] = field(default_factory=dict)
    exclusivity: Dict[str, Any] = field(default_factory=dict)
    payment_terms: Dict[str, Any] = field(default_factory=dict)
    royalty_terms: Dict[str, Any] = field(default_factory=dict)
    attribution_requirements: Dict[str, Any] = field(default_factory=dict)
    quality_standards: Dict[str, Any] = field(default_factory=dict)
    delivery_specifications: Dict[str, Any] = field(default_factory=dict)
    warranty_disclaimers: Dict[str, Any] = field(default_factory=dict)
    indemnification: Dict[str, Any] = field(default_factory=dict)
    termination_clauses: Dict[str, Any] = field(default_factory=dict)
    force_majeure: Dict[str, Any] = field(default_factory=dict)
    governing_law: str = "international"
    dispute_resolution: Dict[str, Any] = field(default_factory=dict)

@dataclass
class RightsPackage:
    """Rights package definition"""    reproduction_rights: bool = False
    distribution_rights: bool = False
    public_performance_rights: bool = False
    public_display_rights: bool = False
    digital_transmission_rights: bool = False
    synchronization_rights: bool = False
    mechanical_rights: bool = False
    adaptation_rights: bool = False
    translation_rights: bool = False
    merchandising_rights: bool = False
    moral_rights: Dict[str, Any] = field(default_factory=dict)
    ancillary_rights: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'reproduction_rights': self.reproduction_rights,
            'distribution_rights': self.distribution_rights,
            'public_performance_rights': self.public_performance_rights,
            'public_display_rights': self.public_display_rights,
            'digital_transmission_rights': self.digital_transmission_rights,
            'synchronization_rights': self.synchronization_rights,
            'mechanical_rights': self.mechanical_rights,
            'adaptation_rights': self.adaptation_rights,
            'translation_rights': self.translation_rights,
            'merchandising_rights': self.merchandising_rights,
            'moral_rights': self.moral_rights,
            'ancillary_rights': self.ancillary_rights
        }

class LicenseAgreement(BaseModel, TimestampMixin, AuditMixin):
    """    Enterprise-grade license agreement model with AI-powered contract generation.
    Supports complex multi-party agreements and automated legal compliance.
    """    __tablename__ = "license_agreements"
    
    # Primary identifiers
    id = Column(PostgresUUID(as_uuid=True), primary_key=True, default=uuid4)
    agreement_number = Column(String(100), unique=True, nullable=False)
    template_id = Column(PostgresUUID(as_uuid=True))
    parent_agreement_id = Column(PostgresUUID(as_uuid=True), ForeignKey('license_agreements.id'))
    
    # Agreement metadata
    title = Column(String(500), nullable=False)
    description = Column(Text)
    license_type = Column(String(50), nullable=False)
    status = Column(String(50), default=LicenseStatus.DRAFT.value)
    complexity_level = Column(Integer, default=ContractComplexity.STANDARD)
    
    # Parties involved
    licensor_id = Column(PostgresUUID(as_uuid=True), nullable=False, index=True)
    licensee_id = Column(PostgresUUID(as_uuid=True), nullable=False, index=True)
    additional_parties = Column(JSONB, default=list)  # Agents, brokers, guarantors
    
    # Content and rights
    content_id = Column(PostgresUUID(as_uuid=True), nullable=False, index=True)
    content_type = Column(String(50), nullable=False)
    rights_package = Column(JSONB, nullable=False)
    usage_rights = Column(JSONB, nullable=False)
    restrictions = Column(JSONB, default=dict)
    
    # Financial terms
    license_fee = Column(SQLDecimal(12, 4), default=Decimal('0.0000'))
    royalty_rate = Column(SQLDecimal(5, 4), default=Decimal('0.0000'))
    minimum_guarantee = Column(SQLDecimal(12, 4), default=Decimal('0.0000'))
    advance_payment = Column(SQLDecimal(12, 4), default=Decimal('0.0000'))
    payment_schedule = Column(JSONB, default=dict)
    currency = Column(String(3), default="EUR")
    
    # Territory and duration
    territory = Column(ARRAY(String), default=list)
    territory_restrictions = Column(JSONB, default=dict)
    effective_date = Column(DateTime(timezone=True))
    expiration_date = Column(DateTime(timezone=True))
    auto_renewal = Column(Boolean, default=False)
    renewal_terms = Column(JSONB, default=dict)
    
    # Contract content
    contract_template = Column(Text)
    contract_content = Column(Text)
    contract_hash = Column(String(255))
    contract_version = Column(String(20), default="1.0.0")
    contract_language = Column(String(10), default="en")
    
    # Legal and compliance
    governing_law = Column(String(100), default="international")
    jurisdiction = Column(String(100))
    dispute_resolution = Column(JSONB, default=dict)
    compliance_requirements = Column(JSONB, default=dict)
    legal_review_required = Column(Boolean, default=True)
    legal_reviewer_id = Column(PostgresUUID(as_uuid=True))
    
    # Signatures and execution
    signature_type = Column(String(50), default=SignatureType.DIGITAL.value)
    signatures_required = Column(Integer, default=2)
    signatures_collected = Column(Integer, default=0)
    signature_data = Column(JSONB, default=dict)
    execution_date = Column(DateTime(timezone=True))
    
    # Performance and monitoring
    performance_metrics = Column(JSONB, default=dict)
    milestone_tracking = Column(JSONB, default=dict)
    compliance_monitoring = Column(Boolean, default=True)
    automatic_reporting = Column(Boolean, default=False)
    
    # Risk and security
    risk_assessment = Column(JSONB, default=dict)
    security_classification = Column(String(50), default="standard")
    confidentiality_level = Column(String(50), default="normal")
    data_protection_clauses = Column(JSONB, default=dict)
    
    # AI and automation
    ai_generated = Column(Boolean, default=False)
    ai_model_version = Column(String(50))
    automation_level = Column(Integer, default=1)
    smart_contract_address = Column(String(255))
    blockchain_recorded = Column(Boolean, default=False)
    
    # Relationships
    clauses = relationship("ContractClause", back_populates="agreement")
    amendments = relationship("AgreementAmendment", back_populates="agreement")
    child_agreements = relationship("LicenseAgreement", remote_side=[parent_agreement_id])
    validation_records = relationship("AgreementValidation", back_populates="agreement")
    
    # Database constraints and indexes
    __table_args__ = (
        Index('idx_agreement_licensor_licensee', 'licensor_id', 'licensee_id'),
        Index('idx_agreement_content_type', 'content_id', 'content_type'),
        Index('idx_agreement_status_effective', 'status', 'effective_date'),
        Index('idx_agreement_expiration', 'expiration_date', 'status'),
        Index('idx_agreement_territory', 'territory'),
        CheckConstraint('license_fee >= 0', name='check_license_fee_positive'),
        CheckConstraint('royalty_rate >= 0 AND royalty_rate <= 1', name='check_royalty_rate_valid'),
        CheckConstraint('signatures_collected <= signatures_required', name='check_signatures_valid'),
        CheckConstraint('complexity_level >= 1 AND complexity_level <= 5', name='check_complexity_valid'),
    )
    
    @validates('status')
    def validate_status(self, key, status):
        if status not in [s.value for s in LicenseStatus]:
            raise ValueError(f"Invalid license status: {status}")
        return status
    
    @validates('license_type')
    def validate_license_type(self, key, license_type):
        if license_type not in [t.value for t in LicenseType]:
            raise ValueError(f"Invalid license type: {license_type}")
        return license_type
    
    @hybrid_property
    def is_active(self):
        return self.status in [LicenseStatus.ACTIVE.value, LicenseStatus.FULLY_EXECUTED.value]
    
    @hybrid_property
    def is_expired(self):
        return self.expiration_date and datetime.now(timezone.utc) > self.expiration_date
    
    @hybrid_property
    def is_fully_signed(self):
        return self.signatures_collected >= self.signatures_required
    
    @hybrid_property
    def completion_percentage(self):
        """Calculate agreement completion percentage"""        total_steps = 10  # draft, review, legal, compliance, signatures, etc.
        completed_steps = 0
        
        if self.status != LicenseStatus.DRAFT.value:
            completed_steps += 1
        if self.contract_content:
            completed_steps += 1
        if self.legal_reviewer_id:
            completed_steps += 2
        if self.compliance_requirements:
            completed_steps += 1
        completed_steps += self.signatures_collected
        if self.execution_date:
            completed_steps += 2
        
        return min((completed_steps / total_steps) * 100, 100)
    
    def can_execute(self) -> bool:
        """Check if agreement can be executed"""        return (
            self.is_fully_signed and
            self.status in [LicenseStatus.PENDING_SIGNATURE.value, LicenseStatus.PARTIALLY_SIGNED.value] and
            not self.is_expired and
            self.legal_review_required == False or self.legal_reviewer_id is not None
        )

class ContractClause(BaseModel, TimestampMixin):
    """    Individual contract clauses with AI-powered generation and validation.
    """    __tablename__ = "contract_clauses"
    
    # Primary identifiers
    id = Column(PostgresUUID(as_uuid=True), primary_key=True, default=uuid4)
    agreement_id = Column(PostgresUUID(as_uuid=True), ForeignKey('license_agreements.id'), nullable=False)
    clause_id = Column(String(100), nullable=False)  # e.g., "grant_of_rights", "payment_terms"
    
    # Clause metadata
    clause_name = Column(String(255), nullable=False)
    clause_category = Column(String(100), nullable=False)
    clause_type = Column(String(50), nullable=False)  # standard, custom, conditional
    priority = Column(Integer, default=100)
    is_mandatory = Column(Boolean, default=False)
    
    # Content and structure
    clause_content = Column(Text, nullable=False)
    variables = Column(JSONB, default=dict)
    conditions = Column(JSONB, default=dict)
    dependencies = Column(ARRAY(String), default=list)  # Other clause IDs this depends on
    
    # Legal and compliance
    legal_basis = Column(String(255))
    jurisdiction_specific = Column(Boolean, default=False)
    applicable_jurisdictions = Column(ARRAY(String), default=list)
    compliance_tags = Column(ARRAY(String), default=list)
    
    # AI and generation
    ai_generated = Column(Boolean, default=False)
    template_source = Column(String(255))
    customization_level = Column(Integer, default=1)  # 1-5 scale
    validation_score = Column(SQLDecimal(3, 2), default=Decimal('0.00'))
    
    # Status and approval
    status = Column(String(50), default="draft")
    approved_by = Column(PostgresUUID(as_uuid=True))
    approval_date = Column(DateTime(timezone=True))
    modification_count = Column(Integer, default=0)
    
    # Relationships
    agreement = relationship("LicenseAgreement", back_populates="clauses")
    
    # Database constraints and indexes
    __table_args__ = (
        Index('idx_clause_agreement_category', 'agreement_id', 'clause_category'),
        Index('idx_clause_type_priority', 'clause_type', 'priority'),
        Index('idx_clause_status_approval', 'status', 'approval_date'),
        UniqueConstraint('agreement_id', 'clause_id', name='unique_agreement_clause'),
        CheckConstraint('priority >= 1 AND priority <= 999', name='check_priority_range'),
        CheckConstraint('customization_level >= 1 AND customization_level <= 5', name='check_customization_valid'),
        CheckConstraint('validation_score >= 0 AND validation_score <= 1', name='check_validation_score_valid'),
    )

class AgreementAmendment(BaseModel, TimestampMixin, AuditMixin):
    """    Agreement amendments and modifications tracking.
    """    __tablename__ = "agreement_amendments"
    
    # Primary identifiers
    id = Column(PostgresUUID(as_uuid=True), primary_key=True, default=uuid4)
    agreement_id = Column(PostgresUUID(as_uuid=True), ForeignKey('license_agreements.id'), nullable=False)
    amendment_number = Column(String(100), nullable=False)
    
    # Amendment details
    amendment_type = Column(String(50), nullable=False)  # modification, extension, termination
    reason = Column(Text, nullable=False)
    description = Column(Text)
    
    # Changes made
    original_terms = Column(JSONB, nullable=False)
    modified_terms = Column(JSONB, nullable=False)
    affected_clauses = Column(ARRAY(String), default=list)
    
    # Approval and execution
    proposed_by = Column(PostgresUUID(as_uuid=True), nullable=False)
    approved_by = Column(ARRAY(String), default=list)
    requires_all_party_approval = Column(Boolean, default=True)
    approval_deadline = Column(DateTime(timezone=True))
    
    # Status tracking
    status = Column(String(50), default="proposed")
    effective_date = Column(DateTime(timezone=True))
    signatures_required = Column(Integer, default=2)
    signatures_collected = Column(Integer, default=0)
    
    # Legal review
    legal_review_required = Column(Boolean, default=True)
    legal_reviewer_id = Column(PostgresUUID(as_uuid=True))
    legal_opinion = Column(Text)
    
    # Relationships
    agreement = relationship("LicenseAgreement", back_populates="amendments")
    
    # Database constraints and indexes
    __table_args__ = (
        Index('idx_amendment_agreement_type', 'agreement_id', 'amendment_type'),
        Index('idx_amendment_status_effective', 'status', 'effective_date'),
        UniqueConstraint('agreement_id', 'amendment_number', name='unique_agreement_amendment'),
    )

class AgreementValidation(BaseModel, TimestampMixin):
    """    Legal and compliance validation records for agreements.
    """    __tablename__ = "agreement_validations"
    
    # Primary identifiers
    id = Column(PostgresUUID(as_uuid=True), primary_key=True, default=uuid4)
    agreement_id = Column(PostgresUUID(as_uuid=True), ForeignKey('license_agreements.id'), nullable=False)
    validation_id = Column(String(100), unique=True, nullable=False)
    
    # Validation details
    validation_type = Column(String(50), nullable=False)  # legal, compliance, technical, business
    validation_level = Column(String(50), default=ValidationLevel.STANDARD.value)
    validator_id = Column(PostgresUUID(as_uuid=True))
    validator_type = Column(String(50))  # human, ai, system, third_party
    
    # Validation process
    started_at = Column(DateTime(timezone=True), nullable=False)
    completed_at = Column(DateTime(timezone=True))
    duration_minutes = Column(Integer)
    
    # Results and findings
    result = Column(String(50), nullable=False)  # passed, failed, conditional, requires_changes
    overall_score = Column(SQLDecimal(3, 2), default=Decimal('0.00'))
    findings = Column(JSONB, default=list)
    recommendations = Column(JSONB, default=list)
    required_changes = Column(JSONB, default=list)
    
    # Risk assessment
    risk_level = Column(String(20), default="medium")
    risk_factors = Column(JSONB, default=list)
    mitigation_strategies = Column(JSONB, default=list)
    
    # Compliance checking
    compliance_standards = Column(ARRAY(String), default=list)
    compliance_gaps = Column(JSONB, default=list)
    regulatory_requirements = Column(JSONB, default=dict)
    
    # Documentation
    validation_report = Column(Text)
    supporting_documents = Column(JSONB, default=list)
    external_opinions = Column(JSONB, default=list)
    
    # Relationships
    agreement = relationship("LicenseAgreement", back_populates="validation_records")
    
    # Database constraints and indexes
    __table_args__ = (
        Index('idx_validation_agreement_type', 'agreement_id', 'validation_type'),
        Index('idx_validation_result_score', 'result', 'overall_score'),
        Index('idx_validation_validator_type', 'validator_type', 'completed_at'),
class LicenseAgreementService:
    """    Enterprise-grade license agreement service with AI-powered contract generation.
    Provides comprehensive agreement lifecycle management and automated legal compliance.
    """    
    def __init__(self, db_session: Session, cache_manager: CacheManager, security_manager: SecurityManager):
        self.db = db_session
        self.cache = cache_manager
        self.security = security_manager
        
        # Initialize AI services
        self.contract_generator = ContractGenerator()
        self.legal_analyzer = LegalAnalyzer()
        
        # Initialize external services
        self.signature_service = DigitalSignatureService()
        self.legal_service = ContractLegalService()
        
        # Initialize Redis for task queuing
        self.redis_client = redis.Redis(host='localhost', port=6379, db=2)
        
        logger.info("LicenseAgreementService initialized")
    
    async def create_license_agreement(self, agreement_data: Dict[str, Any]) -> LicenseAgreement:
        """        Create new license agreement with AI-powered contract generation.
        
        Args:
            agreement_data: Complete agreement information
            
        Returns:
            LicenseAgreement: Created agreement record
        """        with contract_generation_time.time():
            try:
                # Generate unique agreement number
                agreement_number = self._generate_agreement_number()
                
                # Create rights package
                rights_package = self._create_rights_package(agreement_data.get('rights', {}))
                
                # Create agreement record
                agreement = LicenseAgreement(
                    agreement_number=agreement_number,
                    title=agreement_data['title'],
                    description=agreement_data.get('description'),
                    license_type=agreement_data['license_type'],
                    licensor_id=agreement_data['licensor_id'],
                    licensee_id=agreement_data['licensee_id'],
                    content_id=agreement_data['content_id'],
                    content_type=agreement_data['content_type'],
                    rights_package=rights_package.to_dict(),
                    usage_rights=agreement_data['usage_rights'],
                    license_fee=Decimal(str(agreement_data.get('license_fee', '0.0000'))),
                    royalty_rate=Decimal(str(agreement_data.get('royalty_rate', '0.0000'))),
                    territory=agreement_data.get('territory', []),
                    effective_date=agreement_data.get('effective_date'),
                    expiration_date=agreement_data.get('expiration_date'),
                    governing_law=agreement_data.get('governing_law', 'international'),
                    complexity_level=self._assess_complexity(agreement_data)
                )
                
                self.db.add(agreement)
                self.db.commit()
                self.db.refresh(agreement)
                
                # Generate contract content
                contract_content = await self._generate_contract_content(agreement, agreement_data)
                agreement.contract_content = contract_content['content']
                agreement.contract_hash = self._calculate_contract_hash(contract_content['content'])
                agreement.ai_generated = contract_content['ai_generated']
                agreement.ai_model_version = contract_content.get('model_version')
                
                # Create contract clauses
                await self._create_contract_clauses(agreement, contract_content['clauses'])
                
                # Update status
                agreement.status = LicenseStatus.TEMPLATE_GENERATED.value
                self.db.commit()
                
                # Start validation process
                if agreement_data.get('auto_validate', True):
                    asyncio.create_task(self._initiate_validation_process(agreement))
                
                # Update metrics
                license_agreements_total.labels(
                    type=agreement.license_type,
                    status=agreement.status
                ).inc()
                
                logger.info(f"License agreement created: {agreement.agreement_number}")
                return agreement
                
            except Exception as e:
                logger.error(f"Error creating license agreement: {e}")
                raise
    
    async def validate_agreement(self, agreement_id: str, validation_type: str = "comprehensive") -> AgreementValidation:
        """        Comprehensive agreement validation with AI-powered legal analysis.
        
        Args:
            agreement_id: Agreement to validate
            validation_type: Type of validation to perform
            
        Returns:
            AgreementValidation: Validation result
        """        with legal_validation_time.time():
            agreement = self.db.query(LicenseAgreement).filter(
                LicenseAgreement.id == agreement_id
            ).first()
            
            if not agreement:
                raise ValueError(f"Agreement not found: {agreement_id}")
            
            validation_id = self._generate_validation_id()
            
            validation = AgreementValidation(
                agreement_id=agreement.id,
                validation_id=validation_id,
                validation_type=validation_type,
                validation_level=ValidationLevel.COMPREHENSIVE.value,
                validator_type="ai",
                started_at=datetime.now(timezone.utc)
            )
            
            try:
                # Perform AI-powered legal analysis
                legal_analysis = await self.legal_analyzer.analyze_agreement(agreement)
                
                # Check compliance requirements
                compliance_check = await self._check_compliance_requirements(agreement)
                
                # Validate contract clauses
                clause_validation = await self._validate_contract_clauses(agreement)
                
                # Risk assessment
                risk_assessment = await self._assess_agreement_risks(agreement)
                
                # Compile validation results
                validation.completed_at = datetime.now(timezone.utc)
                validation.duration_minutes = int((validation.completed_at - validation.started_at).total_seconds() / 60)
                
                overall_score = self._calculate_validation_score(legal_analysis, compliance_check, clause_validation, risk_assessment)
                validation.overall_score = overall_score
                
                if overall_score >= Decimal('0.8'):
                    validation.result = "passed"
                    agreement.status = LicenseStatus.COMPLIANCE_CHECK.value
                elif overall_score >= Decimal('0.6'):
                    validation.result = "conditional"
                    validation.required_changes = legal_analysis.get('required_changes', [])
                else:
                    validation.result = "failed"
                    validation.required_changes = legal_analysis.get('critical_issues', [])
                
                validation.findings = legal_analysis.get('findings', [])
                validation.recommendations = legal_analysis.get('recommendations', [])
                validation.risk_level = risk_assessment.get('overall_risk', 'medium')
                validation.risk_factors = risk_assessment.get('factors', [])
                validation.compliance_gaps = compliance_check.get('gaps', [])
                
                self.db.add(validation)
                self.db.commit()
                
                logger.info(f"Agreement validation completed: {validation.result}")
                return validation
                
            except Exception as e:
                validation.completed_at = datetime.now(timezone.utc)
                validation.result = "failed"
                validation.validation_report = f"Validation failed: {str(e)}"
                self.db.add(validation)
                self.db.commit()
                raise
    
    async def initiate_signature_process(self, agreement_id: str, signature_data: Dict[str, Any]) -> Dict[str, Any]:
        """        Initiate digital signature process for agreement execution.
        
        Args:
            agreement_id: Agreement to sign
            signature_data: Signature configuration and parties
            
        Returns:
            Dict containing signature process information
        """        agreement = self.db.query(LicenseAgreement).filter(
            LicenseAgreement.id == agreement_id
        ).first()
        
        if not agreement:
            raise ValueError(f"Agreement not found: {agreement_id}")
        
        if not agreement.can_execute():
            raise ValueError("Agreement is not ready for signature")
        
        # Prepare signature package
        signature_package = {
            'agreement_id': str(agreement.id),
            'agreement_number': agreement.agreement_number,
            'contract_content': agreement.contract_content,
            'contract_hash': agreement.contract_hash,
            'parties': [
                {
                    'party_id': str(agreement.licensor_id),
                    'role': 'licensor',
                    'signature_required': True
                },
                {
                    'party_id': str(agreement.licensee_id),
                    'role': 'licensee',
                    'signature_required': True
                }
            ]
        }
        
        # Add additional parties if present
        for party in agreement.additional_parties or []:
            if party.get('requires_signature', False):
                signature_package['parties'].append({
                    'party_id': party['party_id'],
                    'role': party['role'],
                    'signature_required': True
                })
        
        # Initiate signature process
        signature_result = await self.signature_service.initiate_signature_process(
            signature_package,
            signature_data
        )
        
        if signature_result['success']:
            agreement.status = LicenseStatus.PENDING_SIGNATURE.value
            agreement.signature_data = {
                'process_id': signature_result['process_id'],
                'signature_urls': signature_result['signature_urls'],
                'deadline': signature_result['deadline'],
                'initiated_at': datetime.now(timezone.utc).isoformat()
            }
            self.db.commit()
        
        return signature_result
    
    async def process_signature_completion(self, agreement_id: str, signature_event: Dict[str, Any]) -> bool:
        """        Process signature completion event and update agreement status.
        
        Args:
            agreement_id: Agreement being signed
            signature_event: Signature completion event data
            
        Returns:
            bool: True if agreement is fully executed
        """        agreement = self.db.query(LicenseAgreement).filter(
            LicenseAgreement.id == agreement_id
        ).first()
        
        if not agreement:
            raise ValueError(f"Agreement not found: {agreement_id}")
        
        # Update signature count
        agreement.signatures_collected += 1
        
        # Update signature data
        signature_data = agreement.signature_data or {}
        signatures = signature_data.get('signatures', [])
        signatures.append({
            'party_id': signature_event['party_id'],
            'signed_at': signature_event['signed_at'],
            'signature_hash': signature_event['signature_hash'],
            'ip_address': signature_event.get('ip_address'),
            'device_info': signature_event.get('device_info')
        })
        signature_data['signatures'] = signatures
        agreement.signature_data = signature_data
        
        # Check if fully signed
        if agreement.is_fully_signed:
            agreement.status = LicenseStatus.FULLY_EXECUTED.value
            agreement.execution_date = datetime.now(timezone.utc)
            
            # Activate the agreement
            await self._activate_agreement(agreement)
            
            # Update metrics
            active_agreements_gauge.inc()
            
            logger.info(f"Agreement fully executed: {agreement.agreement_number}")
            self.db.commit()
            return True
        else:
            agreement.status = LicenseStatus.PARTIALLY_SIGNED.value
            self.db.commit()
            return False
    
    async def create_amendment(self, agreement_id: str, amendment_data: Dict[str, Any]) -> AgreementAmendment:
        """        Create agreement amendment with change tracking.
        
        Args:
            agreement_id: Agreement to amend
            amendment_data: Amendment details and changes
            
        Returns:
            AgreementAmendment: Created amendment
        """        agreement = self.db.query(LicenseAgreement).filter(
            LicenseAgreement.id == agreement_id
        ).first()
        
        if not agreement:
            raise ValueError(f"Agreement not found: {agreement_id}")
        
        amendment_number = self._generate_amendment_number(agreement.agreement_number)
        
        # Capture original terms before changes
        original_terms = {
            'license_fee': float(agreement.license_fee),
            'royalty_rate': float(agreement.royalty_rate),
            'territory': agreement.territory,
            'expiration_date': agreement.expiration_date.isoformat() if agreement.expiration_date else None,
            'usage_rights': agreement.usage_rights,
            'restrictions': agreement.restrictions
        }
        
        amendment = AgreementAmendment(
            agreement_id=agreement.id,
            amendment_number=amendment_number,
            amendment_type=amendment_data['type'],
            reason=amendment_data['reason'],
            description=amendment_data.get('description'),
            original_terms=original_terms,
            modified_terms=amendment_data['modified_terms'],
            proposed_by=amendment_data['proposed_by'],
            approval_deadline=amendment_data.get('approval_deadline'),
            signatures_required=amendment_data.get('signatures_required', 2)
        )
        
        self.db.add(amendment)
        self.db.commit()
        self.db.refresh(amendment)
        
        # Notify parties about amendment
        await self._notify_amendment_parties(amendment)
        
        return amendment
    
    def _create_rights_package(self, rights_data: Dict[str, Any]) -> RightsPackage:
        """Create standardized rights package"""        return RightsPackage(
            reproduction_rights=rights_data.get('reproduction_rights', False),
            distribution_rights=rights_data.get('distribution_rights', False),
            public_performance_rights=rights_data.get('public_performance_rights', False),
            public_display_rights=rights_data.get('public_display_rights', False),
            digital_transmission_rights=rights_data.get('digital_transmission_rights', False),
            synchronization_rights=rights_data.get('synchronization_rights', False),
            mechanical_rights=rights_data.get('mechanical_rights', False),
            adaptation_rights=rights_data.get('adaptation_rights', False),
            translation_rights=rights_data.get('translation_rights', False),
            merchandising_rights=rights_data.get('merchandising_rights', False),
            moral_rights=rights_data.get('moral_rights', {}),
            ancillary_rights=rights_data.get('ancillary_rights', {})
        )
    
    def _assess_complexity(self, agreement_data: Dict[str, Any]) -> int:
        """Assess agreement complexity for AI processing"""        complexity_score = 1
        
        # Multiple parties increase complexity
        if len(agreement_data.get('additional_parties', [])) > 0:
            complexity_score += 1
        
        # Multiple territories
        if len(agreement_data.get('territory', [])) > 3:
            complexity_score += 1
        
        # Complex payment terms
        if agreement_data.get('royalty_rate', 0) > 0 and agreement_data.get('license_fee', 0) > 0:
            complexity_score += 1
        
        # Custom terms and conditions
        if agreement_data.get('custom_clauses'):
            complexity_score += 1
        
        return min(complexity_score, 5)
    
    async def _generate_contract_content(self, agreement: LicenseAgreement, agreement_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate contract content using AI"""        contract_data = {
            'agreement': agreement,
            'template_preferences': agreement_data.get('template_preferences', {}),
            'custom_clauses': agreement_data.get('custom_clauses', []),
            'jurisdiction_requirements': agreement_data.get('jurisdiction_requirements', {}),
            'industry_standards': agreement_data.get('industry_standards', [])
        }
        
        return await self.contract_generator.generate_contract(contract_data)
    
    async def _create_contract_clauses(self, agreement: LicenseAgreement, clauses_data: List[Dict[str, Any]]):
        """Create individual contract clauses"""        for clause_data in clauses_data:
            clause = ContractClause(
                agreement_id=agreement.id,
                clause_id=clause_data['clause_id'],
                clause_name=clause_data['name'],
                clause_category=clause_data['category'],
                clause_type=clause_data.get('type', 'standard'),
                clause_content=clause_data['content'],
                variables=clause_data.get('variables', {}),
                is_mandatory=clause_data.get('mandatory', False),
                ai_generated=clause_data.get('ai_generated', False),
                priority=clause_data.get('priority', 100)
            )
            self.db.add(clause)
        
        self.db.commit()
    
    def _calculate_contract_hash(self, contract_content: str) -> str:
        """Calculate SHA-256 hash of contract content"""        return hashlib.sha256(contract_content.encode('utf-8')).hexdigest()
    
    def _generate_agreement_number(self) -> str:
        """Generate unique agreement number"""        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        random_suffix = str(uuid4())[:8].upper()
        return f"LA-{timestamp}-{random_suffix}"
    
    def _generate_validation_id(self) -> str:
        """Generate unique validation ID"""        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        random_suffix = str(uuid4())[:6].upper()
        return f"VAL-{timestamp}-{random_suffix}"
    
    def _generate_amendment_number(self, base_agreement_number: str) -> str:
        """Generate amendment number based on agreement number"""        # Count existing amendments
        amendment_count = self.db.query(AgreementAmendment).join(LicenseAgreement).filter(
            LicenseAgreement.agreement_number == base_agreement_number
        ).count()
        
        return f"{base_agreement_number}-AMD-{amendment_count + 1:03d}"
    
    async def _initiate_validation_process(self, agreement: LicenseAgreement):
        """Start automated validation process"""        try:
            await self.validate_agreement(str(agreement.id), "comprehensive")
        except Exception as e:
            logger.error(f"Validation process failed for agreement {agreement.agreement_number}: {e}")
    
    async def _check_compliance_requirements(self, agreement: LicenseAgreement) -> Dict[str, Any]:
        """Check agreement against compliance requirements"""        return await self.legal_service.check_agreement_compliance(agreement)
    
    async def _validate_contract_clauses(self, agreement: LicenseAgreement) -> Dict[str, Any]:
        """Validate individual contract clauses"""        clauses = self.db.query(ContractClause).filter(
            ContractClause.agreement_id == agreement.id
        ).all()
        
        validation_results = []
        for clause in clauses:
            clause_validation = await self.legal_analyzer.validate_clause(clause)
            validation_results.append(clause_validation)
        
        return {
            'total_clauses': len(clauses),
            'validated_clauses': len([r for r in validation_results if r['valid']]),
            'issues_found': [r for r in validation_results if not r['valid']],
            'overall_valid': all(r['valid'] for r in validation_results)
        }
    
    async def _assess_agreement_risks(self, agreement: LicenseAgreement) -> Dict[str, Any]:
        """Assess legal and business risks"""        return await self.legal_analyzer.assess_risks(agreement)
    
    def _calculate_validation_score(self, legal_analysis: Dict, compliance_check: Dict, 
                                   clause_validation: Dict, risk_assessment: Dict) -> Decimal:
        """Calculate overall validation score"""        legal_score = legal_analysis.get('score', 0.5)
        compliance_score = 1.0 if compliance_check.get('compliant', False) else 0.3
        clause_score = 1.0 if clause_validation.get('overall_valid', False) else 0.5
        risk_score = 1.0 - risk_assessment.get('overall_risk_score', 0.5)
        
        overall_score = (legal_score * 0.3 + compliance_score * 0.3 + clause_score * 0.2 + risk_score * 0.2)
        return Decimal(str(round(overall_score, 2)))
    
    async def _activate_agreement(self, agreement: LicenseAgreement):
        """Activate agreement and set up monitoring"""        agreement.status = LicenseStatus.ACTIVE.value
        
        # Set up performance monitoring if required
        if agreement.compliance_monitoring:
            await self._setup_compliance_monitoring(agreement)
        
        # Create blockchain record if enabled
        if agreement.blockchain_recorded:
            await self._record_agreement_on_blockchain(agreement)
    
    async def _setup_compliance_monitoring(self, agreement: LicenseAgreement):
        """Set up automated compliance monitoring"""        # Implementation would set up monitoring tasks
        pass
    
    async def _record_agreement_on_blockchain(self, agreement: LicenseAgreement):
        """Record agreement execution on blockchain"""        # Implementation would integrate with blockchain service
        pass
    
    async def _notify_amendment_parties(self, amendment: AgreementAmendment):
        """Notify all parties about proposed amendment"""        # Implementation would send notifications
        pass

# Export all models and services
__all__ = [
    'LicenseAgreement', 'ContractClause', 'AgreementAmendment', 'AgreementValidation',
    'LicenseAgreementService', 'LicenseType', 'LicenseStatus', 'ContractComplexity',
    'SignatureType', 'ValidationLevel', 'ContractTerms', 'RightsPackage'
]
    PENDING = "pending"
    ACTIVE = "active"
    SUSPENDED = "suspended"
    EXPIRED = "expired"
    TERMINATED = "terminated"
    DISPUTED = "disputed"

class TerritoryScope(Enum):
    """Portée territoriale des licences"""    WORLDWIDE = "worldwide"
    NORTH_AMERICA = "north_america"
    EUROPE = "europe"
    ASIA_PACIFIC = "asia_pacific"
    SPECIFIC_COUNTRIES = "specific_countries"
    REGIONAL = "regional"

@dataclass
class LicenseTerms:
    """Structure des termes de licence"""    duration_months: int
    territory_scope: TerritoryScope
    usage_rights: List[str]
    restrictions: List[str]
    royalty_rate: Optional[Decimal] = None
    minimum_guarantee: Optional[Decimal] = None
    revenue_share_percentage: Optional[Decimal] = None
    attribution_required: bool = True
    commercial_use_allowed: bool = False
    modification_allowed: bool = False
    distribution_allowed: bool = True
    sublicensing_allowed: bool = False

class LicenseAgreement(BaseModel):
    """    Modèle de base de données pour les accords de licence.
    Gère tous les aspects légaux et commerciaux des licences.
    """    __tablename__ = "license_agreements"

    # Identifiants
    id = Column(Integer, primary_key=True, index=True)
    agreement_id = Column(String(50), unique=True, index=True, nullable=False)
    external_reference = Column(String(100), index=True)
    
    # Relations
    licensor_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    licensee_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    content_id = Column(Integer, ForeignKey("content_items.id"), nullable=False)
    
    # Informations de base
    license_type = Column(String(30), nullable=False)
    status = Column(String(20), default=LicenseStatus.DRAFT.value)
    title = Column(String(200), nullable=False)
    description = Column(Text)
    
    # Termes de la licence
    terms = Column(JSON, nullable=False)
    legal_text = Column(Text)
    custom_clauses = Column(JSON)
    
    # Période de validité
    effective_date = Column(DateTime, nullable=False)
    expiration_date = Column(DateTime)
    auto_renewal = Column(Boolean, default=False)
    renewal_period_months = Column(Integer, default=12)
    
    # Conditions financières
    license_fee = Column(Decimal(12, 2))
    currency = Column(String(3), default="EUR")
    payment_terms = Column(String(50))
    royalty_rate = Column(Decimal(5, 4))
    minimum_guarantee = Column(Decimal(12, 2))
    
    # Métadonnées
    signed_date = Column(DateTime)
    signed_by_licensor = Column(Boolean, default=False)
    signed_by_licensee = Column(Boolean, default=False)
    digital_signature_licensor = Column(Text)
    digital_signature_licensee = Column(Text)
    
    # Audit et compliance
    legal_review_status = Column(String(20), default="pending")
    legal_reviewer_id = Column(Integer, ForeignKey("users.id"))
    compliance_checked = Column(Boolean, default=False)
    compliance_notes = Column(Text)
    
    # Relations
    licensor = relationship("User", foreign_keys=[licensor_id], back_populates="licenses_granted")
    licensee = relationship("User", foreign_keys=[licensee_id], back_populates="licenses_acquired")
    content = relationship("ContentItem", back_populates="licenses")
    legal_reviewer = relationship("User", foreign_keys=[legal_reviewer_id])
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if not self.agreement_id:
            self.agreement_id = f"LIC-{uuid.uuid4().hex[:8].upper()}"

    def to_dict(self) -> Dict[str, Any]:
        """Convertit l'accord en dictionnaire"""        data = {
            "id": self.id,
            "agreement_id": self.agreement_id,
            "license_type": self.license_type,
            "status": self.status,
            "title": self.title,
            "description": self.description,
            "terms": self.terms,
            "effective_date": self.effective_date.isoformat() if self.effective_date else None,
            "expiration_date": self.expiration_date.isoformat() if self.expiration_date else None,
            "license_fee": float(self.license_fee) if self.license_fee else None,
            "currency": self.currency,
            "is_signed": self.is_fully_signed(),
            "is_active": self.is_active(),
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }
        return data

    def is_fully_signed(self) -> bool:
        """Vérifie si l'accord est entièrement signé"""        return self.signed_by_licensor and self.signed_by_licensee

    def is_active(self) -> bool:
        """Vérifie si l'accord est actuellement actif"""        now = datetime.utcnow()
        return (
            self.status == LicenseStatus.ACTIVE.value and
            self.effective_date <= now and
            (self.expiration_date is None or self.expiration_date > now) and
            self.is_fully_signed()
        )

    def is_expired(self) -> bool:
        """Vérifie si l'accord a expiré"""        if not self.expiration_date:
            return False
        return datetime.utcnow() > self.expiration_date

    def days_until_expiration(self) -> Optional[int]:
        """Retourne le nombre de jours avant expiration"""        if not self.expiration_date:
            return None
        delta = self.expiration_date - datetime.utcnow()
        return max(0, delta.days)

    def can_auto_renew(self) -> bool:
        """Vérifie si l'accord peut être renouvelé automatiquement"""        return (
            self.auto_renewal and
            self.is_active() and
            self.days_until_expiration() is not None and
            self.days_until_expiration() <= 30
        )

    def calculate_revenue_share(self, gross_revenue: Decimal) -> Decimal:
        """Calcule la part de revenus selon les termes de la licence"""        if not self.terms or not isinstance(self.terms, dict):
            return Decimal('0')
        
        revenue_share_pct = self.terms.get('revenue_share_percentage', 0)
        if revenue_share_pct:
            return gross_revenue * (Decimal(str(revenue_share_pct)) / 100)
        
        if self.royalty_rate:
            return gross_revenue * self.royalty_rate
        
        return Decimal('0')

class LicenseAgreementManager:
    """    Gestionnaire pour les opérations sur les accords de licence.
    Fournit une interface haut niveau pour la gestion des licences.
    """    def __init__(self, db_session: Session):
        self.db = db_session
        self.logger = logging.getLogger(__name__)

    def create_agreement(
        self,
        licensor_id: int,
        licensee_id: int,
        content_id: int,
        license_type: LicenseType,
        terms: LicenseTerms,
        title: str,
        description: Optional[str] = None,
        custom_clauses: Optional[Dict] = None
    ) -> LicenseAgreement:
        """Crée un nouvel accord de licence"""        
        try:
            # Validation des données
            self._validate_agreement_data(licensor_id, licensee_id, content_id)
            
            # Calcul de la date d'expiration
            effective_date = datetime.utcnow()
            expiration_date = effective_date + timedelta(days=terms.duration_months * 30)
            
            # Création de l'accord
            agreement = LicenseAgreement(
                licensor_id=licensor_id,
                licensee_id=licensee_id,
                content_id=content_id,
                license_type=license_type.value,
                title=title,
                description=description,
                terms=asdict(terms),
                custom_clauses=custom_clauses or {},
                effective_date=effective_date,
                expiration_date=expiration_date,
                status=LicenseStatus.DRAFT.value
            )
            
            self.db.add(agreement)
            self.db.commit()
            self.db.refresh(agreement)
            
            self.logger.info(f"Accord de licence créé: {agreement.agreement_id}")
            return agreement
            
        except Exception as e:
            self.db.rollback()
            self.logger.error(f"Erreur création accord: {str(e)}")
            raise

    def get_agreement_by_id(self, agreement_id: str) -> Optional[LicenseAgreement]:
        """Récupère un accord par son ID"""        return self.db.query(LicenseAgreement).filter(
            LicenseAgreement.agreement_id == agreement_id
        ).first()

    def get_user_agreements(
        self,
        user_id: int,
        as_licensor: bool = True,
        status: Optional[LicenseStatus] = None
    ) -> List[LicenseAgreement]:
        """Récupère les accords d'un utilisateur"""        
        query = self.db.query(LicenseAgreement)
        
        if as_licensor:
            query = query.filter(LicenseAgreement.licensor_id == user_id)
        else:
            query = query.filter(LicenseAgreement.licensee_id == user_id)
        
        if status:
            query = query.filter(LicenseAgreement.status == status.value)
        
        return query.order_by(LicenseAgreement.created_at.desc()).all()

    def sign_agreement(
        self,
        agreement_id: str,
        user_id: int,
        digital_signature: str
    ) -> bool:
        """Signe un accord de licence"""        
        try:
            agreement = self.get_agreement_by_id(agreement_id)
            if not agreement:
                raise ValueError(f"Accord non trouvé: {agreement_id}")
            
            # Vérification des droits de signature
            if user_id == agreement.licensor_id:
                agreement.signed_by_licensor = True
                agreement.digital_signature_licensor = digital_signature
            elif user_id == agreement.licensee_id:
                agreement.signed_by_licensee = True
                agreement.digital_signature_licensee = digital_signature
            else:
                raise ValueError("Utilisateur non autorisé à signer cet accord")
            
            # Si entièrement signé, activation
            if agreement.is_fully_signed():
                agreement.status = LicenseStatus.ACTIVE.value
                agreement.signed_date = datetime.utcnow()
            
            self.db.commit()
            self.logger.info(f"Accord signé: {agreement_id} par utilisateur {user_id}")
            return True
            
        except Exception as e:
            self.db.rollback()
            self.logger.error(f"Erreur signature accord: {str(e)}")
            raise

    def terminate_agreement(
        self,
        agreement_id: str,
        reason: str,
        terminating_user_id: int
    ) -> bool:
        """Termine un accord de licence"""        
        try:
            agreement = self.get_agreement_by_id(agreement_id)
            if not agreement:
                raise ValueError(f"Accord non trouvé: {agreement_id}")
            
            # Vérification des droits
            if terminating_user_id not in [agreement.licensor_id, agreement.licensee_id]:
                raise ValueError("Utilisateur non autorisé à terminer cet accord")
            
            agreement.status = LicenseStatus.TERMINATED.value
            agreement.compliance_notes = f"Terminé par utilisateur {terminating_user_id}. Raison: {reason}"
            
            self.db.commit()
            self.logger.info(f"Accord terminé: {agreement_id}")
            return True
            
        except Exception as e:
            self.db.rollback()
            self.logger.error(f"Erreur termination accord: {str(e)}")
            raise

    def check_expiring_agreements(self, days_ahead: int = 30) -> List[LicenseAgreement]:
        """Trouve les accords qui expirent bientôt"""        
        cutoff_date = datetime.utcnow() + timedelta(days=days_ahead)
        
        return self.db.query(LicenseAgreement).filter(
            LicenseAgreement.status == LicenseStatus.ACTIVE.value,
            LicenseAgreement.expiration_date <= cutoff_date,
            LicenseAgreement.expiration_date > datetime.utcnow()
        ).all()

    def auto_renew_agreements(self) -> List[str]:
        """Renouvelle automatiquement les accords éligibles"""        
        renewed_agreements = []
        expiring_agreements = self.check_expiring_agreements(30)
        
        for agreement in expiring_agreements:
            if agreement.can_auto_renew():
                try:
                    # Extension de la période
                    new_expiration = agreement.expiration_date + timedelta(
                        days=agreement.renewal_period_months * 30
                    )
                    agreement.expiration_date = new_expiration
                    
                    self.db.commit()
                    renewed_agreements.append(agreement.agreement_id)
                    self.logger.info(f"Accord renouvelé automatiquement: {agreement.agreement_id}")
                    
                except Exception as e:
                    self.logger.error(f"Erreur renouvellement {agreement.agreement_id}: {str(e)}")
                    continue
        
        return renewed_agreements

    def _validate_agreement_data(self, licensor_id: int, licensee_id: int, content_id: int):
        """Valide les données avant création d'accord"""        
        if licensor_id == licensee_id:
            raise ValueError("Le concédant et le licencié ne peuvent pas être la même personne")
        
        # Vérification que l'utilisateur possède le contenu
        from ..models.content import ContentItem
        content = self.db.query(ContentItem).filter(
            ContentItem.id == content_id,
            ContentItem.owner_id == licensor_id
        ).first()
        
        if not content:
            raise ValueError("Le concédant ne possède pas ce contenu")

    def generate_license_report(self, user_id: int) -> Dict[str, Any]:
        """Génère un rapport complet des licences pour un utilisateur"""        
        granted_licenses = self.get_user_agreements(user_id, as_licensor=True)
        acquired_licenses = self.get_user_agreements(user_id, as_licensor=False)
        
        # Calculs de statistiques
        total_granted = len(granted_licenses)
        total_acquired = len(acquired_licenses)
        active_granted = len([l for l in granted_licenses if l.is_active()])
        active_acquired = len([l for l in acquired_licenses if l.is_active()])
        
        # Revenus estimés
        total_revenue = sum([
            l.calculate_revenue_share(Decimal('1000'))  # Exemple avec 1000 EUR
            for l in granted_licenses if l.is_active()
        ])
        
        return {
            "user_id": user_id,
            "summary": {
                "total_granted": total_granted,
                "total_acquired": total_acquired,
                "active_granted": active_granted,
                "active_acquired": active_acquired,
                "estimated_monthly_revenue": float(total_revenue)
            },
            "granted_licenses": [l.to_dict() for l in granted_licenses[:10]],
            "acquired_licenses": [l.to_dict() for l in acquired_licenses[:10]],
            "expiring_soon": [
                l.to_dict() for l in granted_licenses + acquired_licenses
                if l.is_active() and l.days_until_expiration() and l.days_until_expiration() <= 30
            ]
        }
