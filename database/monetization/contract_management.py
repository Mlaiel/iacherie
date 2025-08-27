"""
Contract Management - Enterprise Contract Lifecycle Management

Ultra-advanced contract management system with automated workflows,
digital signatures, compliance tracking, and AI-powered contract analysis.

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


class ContractType(Enum):
    """Types of contracts in the system"""
    LICENSE_AGREEMENT = "license_agreement"
    COLLABORATION_AGREEMENT = "collaboration_agreement"
    DISTRIBUTION_AGREEMENT = "distribution_agreement"
    PUBLISHING_AGREEMENT = "publishing_agreement"
    RECORDING_AGREEMENT = "recording_agreement"
    MANAGEMENT_AGREEMENT = "management_agreement"
    BOOKING_AGREEMENT = "booking_agreement"
    ENDORSEMENT_AGREEMENT = "endorsement_agreement"
    SPONSORSHIP_AGREEMENT = "sponsorship_agreement"
    MERCHANDISING_AGREEMENT = "merchandising_agreement"
    SYNC_LICENSE = "sync_license"
    MASTER_LICENSE = "master_license"
    WORK_FOR_HIRE = "work_for_hire"
    NON_DISCLOSURE_AGREEMENT = "non_disclosure_agreement"
    SERVICE_AGREEMENT = "service_agreement"
    CUSTOM_AGREEMENT = "custom_agreement"


class ContractStatus(Enum):
    """Contract lifecycle status"""
    DRAFT = "draft"
    UNDER_REVIEW = "under_review"
    PENDING_APPROVAL = "pending_approval"
    UNDER_NEGOTIATION = "under_negotiation"
    PENDING_SIGNATURE = "pending_signature"
    PARTIALLY_SIGNED = "partially_signed"
    FULLY_EXECUTED = "fully_executed"
    ACTIVE = "active"
    SUSPENDED = "suspended"
    TERMINATED = "terminated"
    EXPIRED = "expired"
    CANCELLED = "cancelled"
    DISPUTED = "disputed"
    ARCHIVED = "archived"


class WorkflowStatus(Enum):
    """Workflow step status"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    SKIPPED = "skipped"
    FAILED = "failed"
    CANCELLED = "cancelled"
    TIMEOUT = "timeout"


class SignatureType(Enum):
    """Types of signatures"""
    ELECTRONIC = "electronic"
    DIGITAL = "digital"
    WET_SIGNATURE = "wet_signature"
    BIOMETRIC = "biometric"
    BLOCKCHAIN = "blockchain"
    SMART_CONTRACT = "smart_contract"


class ApprovalAction(Enum):
    """Approval actions"""
    APPROVE = "approve"
    REJECT = "reject"
    REQUEST_CHANGES = "request_changes"
    DELEGATE = "delegate"
    ESCALATE = "escalate"
    WITHDRAW = "withdraw"


class Contract(Base):
    """
    Contract Model
    
    Comprehensive contract management with automated workflows,
    version control, digital signatures, and compliance tracking.
    """
    __tablename__ = "contracts"
    
    # Primary identification
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    contract_number = Column(String(100), unique=True, nullable=False, index=True)
    
    # Contract classification
    contract_type = Column(SQLEnum(ContractType), nullable=False, index=True)
    contract_status = Column(SQLEnum(ContractStatus), default=ContractStatus.DRAFT, index=True)
    title = Column(String(500), nullable=False)
    description = Column(Text, nullable=True)
    
    # Parties involved
    primary_party_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False, index=True)
    secondary_party_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=True, index=True)
    additional_parties = Column(JSONB, nullable=True)  # For multi-party contracts
    
    # Related entities
    license_agreement_id = Column(UUID(as_uuid=True), ForeignKey('license_agreements.id'), nullable=True, index=True)
    collaboration_id = Column(UUID(as_uuid=True), ForeignKey('collaboration_requests.id'), nullable=True, index=True)
    content_fingerprint_id = Column(UUID(as_uuid=True), ForeignKey('content_fingerprints.id'), nullable=True, index=True)
    
    # Contract terms and conditions
    terms_and_conditions = Column(Text, nullable=True)
    key_terms = Column(JSONB, nullable=True)
    special_provisions = Column(JSONB, nullable=True)
    payment_terms = Column(JSONB, nullable=True)
    performance_obligations = Column(JSONB, nullable=True)
    
    # Time periods
    effective_date = Column(DateTime(timezone=True), nullable=True)
    expiration_date = Column(DateTime(timezone=True), nullable=True)
    signature_deadline = Column(DateTime(timezone=True), nullable=True)
    renewal_date = Column(DateTime(timezone=True), nullable=True)
    notice_period_days = Column(Integer, default=30)
    
    # Auto-renewal settings
    auto_renewal = Column(Boolean, default=False)
    renewal_period_months = Column(Integer, nullable=True)
    renewal_notice_days = Column(Integer, default=60)
    
    # Financial terms
    contract_value = Column(Numeric(18, 6), nullable=True)
    currency = Column(String(10), default='EUR')
    payment_schedule = Column(JSONB, nullable=True)
    penalty_clauses = Column(JSONB, nullable=True)
    termination_costs = Column(JSONB, nullable=True)
    
    # Legal framework
    governing_law = Column(String(100), nullable=True)
    jurisdiction = Column(String(100), nullable=True)
    dispute_resolution = Column(String(100), nullable=True)
    arbitration_clause = Column(Text, nullable=True)
    
    # Document management
    master_document_url = Column(String(500), nullable=True)
    signed_document_url = Column(String(500), nullable=True)
    attachments = Column(JSONB, nullable=True)
    document_hash = Column(String(255), nullable=True)
    document_version = Column(String(20), default='1.0')
    
    # Template and generation
    template_id = Column(UUID(as_uuid=True), nullable=True)
    generated_from_template = Column(Boolean, default=False)
    template_variables = Column(JSONB, nullable=True)
    
    # Compliance and risk
    compliance_requirements = Column(JSONB, nullable=True)
    risk_assessment = Column(JSONB, nullable=True)
    regulatory_approvals = Column(JSONB, nullable=True)
    compliance_score = Column(Float, default=1.0)
    
    # Performance tracking
    milestone_tracking = Column(JSONB, nullable=True)
    performance_metrics = Column(JSONB, nullable=True)
    sla_requirements = Column(JSONB, nullable=True)
    breach_incidents = Column(JSONB, nullable=True)
    
    # Notification settings
    notification_preferences = Column(JSONB, nullable=True)
    reminder_schedule = Column(JSONB, nullable=True)
    escalation_rules = Column(JSONB, nullable=True)
    
    # Integration and automation
    smart_contract_address = Column(String(255), nullable=True)
    blockchain_network = Column(String(100), nullable=True)
    automated_execution = Column(Boolean, default=False)
    api_webhooks = Column(JSONB, nullable=True)
    
    # Metadata and categorization
    tags = Column(ARRAY(String), nullable=True)
    priority = Column(String(20), default='medium')
    confidentiality_level = Column(String(20), default='standard')
    business_unit = Column(String(100), nullable=True)
    
    # Audit and version control
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(UUID(as_uuid=True), nullable=False)
    last_modified_by = Column(UUID(as_uuid=True), nullable=True)
    version = Column(Integer, default=1)
    
    # Relationships
    primary_party = relationship("User", foreign_keys=[primary_party_id])
    secondary_party = relationship("User", foreign_keys=[secondary_party_id])
    license_agreement = relationship("LicenseAgreement", back_populates="contracts")
    collaboration = relationship("CollaborationRequest", back_populates="contracts")
    signatures = relationship("ContractSignature", back_populates="contract")
    workflow_steps = relationship("ContractWorkflowStep", back_populates="contract")
    approvals = relationship("ContractApproval", back_populates="contract")
    amendments = relationship("ContractAmendment", back_populates="contract")
    
    # Indexes and constraints
    __table_args__ = (
        Index('idx_contract_type_status', 'contract_type', 'contract_status'),
        Index('idx_contract_parties', 'primary_party_id', 'secondary_party_id'),
        Index('idx_contract_dates', 'effective_date', 'expiration_date'),
        Index('idx_contract_license', 'license_agreement_id'),
        Index('idx_contract_collaboration', 'collaboration_id'),
        Index('idx_contract_content', 'content_fingerprint_id'),
        Index('idx_contract_priority', 'priority'),
        Index('idx_contract_template', 'template_id'),
        
        # Check constraints
        CheckConstraint('effective_date IS NULL OR expiration_date IS NULL OR effective_date <= expiration_date', 
                       name='check_contract_date_order'),
        CheckConstraint('notice_period_days >= 0', name='check_notice_period'),
        CheckConstraint('version > 0', name='check_version_positive'),
    )
    
    def __repr__(self):
        return f"<Contract(id={self.id}, number={self.contract_number}, type={self.contract_type.value})>"
    
    @property
    def is_active(self) -> bool:
        """Check if contract is currently active"""
        now = datetime.utcnow()
        return (
            self.contract_status == ContractStatus.ACTIVE and
            (self.effective_date is None or self.effective_date <= now) and
            (self.expiration_date is None or self.expiration_date > now)
        )
    
    @property
    def days_until_expiration(self) -> Optional[int]:
        """Calculate days until contract expiration"""
        if self.expiration_date:
            delta = self.expiration_date - datetime.utcnow()
            return max(0, delta.days)
        return None
    
    @property
    def is_renewable(self) -> bool:
        """Check if contract can be renewed"""
        return self.auto_renewal or self.contract_status == ContractStatus.ACTIVE


class ContractSignature(Base):
    """
    Contract Signature Model
    
    Tracks digital signatures with advanced security, verification,
    and compliance features for legally binding agreements.
    """
    __tablename__ = "contract_signatures"
    
    # Primary identification
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Associated contract
    contract_id = Column(UUID(as_uuid=True), ForeignKey('contracts.id'), nullable=False, index=True)
    
    # Signer information
    signer_user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False, index=True)
    signer_role = Column(String(100), nullable=False)
    signer_authority = Column(String(100), nullable=True)
    
    # Signature details
    signature_type = Column(SQLEnum(SignatureType), nullable=False)
    signature_data = Column(Text, nullable=True)  # Encrypted signature data
    signature_hash = Column(String(255), nullable=False, index=True)
    certificate_fingerprint = Column(String(255), nullable=True)
    
    # Signing process
    signed_at = Column(DateTime(timezone=True), nullable=False)
    signing_ip_address = Column(String(45), nullable=True)
    signing_device = Column(String(200), nullable=True)
    signing_location = Column(JSONB, nullable=True)
    
    # Document state at signing
    document_hash_at_signing = Column(String(255), nullable=False)
    document_version_at_signing = Column(String(20), nullable=False)
    
    # Verification and validation
    is_verified = Column(Boolean, default=False, index=True)
    verification_method = Column(String(100), nullable=True)
    verification_timestamp = Column(DateTime(timezone=True), nullable=True)
    verification_certificate = Column(Text, nullable=True)
    
    # Legal compliance
    legal_name = Column(String(255), nullable=False)
    title_position = Column(String(100), nullable=True)
    company_name = Column(String(255), nullable=True)
    witness_information = Column(JSONB, nullable=True)
    notarization_details = Column(JSONB, nullable=True)
    
    # Biometric data (if applicable)
    biometric_hash = Column(String(255), nullable=True)
    biometric_template = Column(Text, nullable=True)
    biometric_confidence = Column(Float, nullable=True)
    
    # Blockchain integration
    blockchain_transaction_hash = Column(String(255), nullable=True)
    blockchain_network = Column(String(100), nullable=True)
    smart_contract_address = Column(String(255), nullable=True)
    
    # Additional security
    two_factor_verified = Column(Boolean, default=False)
    identity_verification_level = Column(String(50), nullable=True)
    signing_intent_confirmed = Column(Boolean, default=False)
    
    # Metadata
    signing_reason = Column(Text, nullable=True)
    notes = Column(Text, nullable=True)
    revoked = Column(Boolean, default=False)
    revocation_reason = Column(Text, nullable=True)
    revoked_at = Column(DateTime(timezone=True), nullable=True)
    
    # Audit trail
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    
    # Relationships
    contract = relationship("Contract", back_populates="signatures")
    signer = relationship("User", back_populates="signatures")
    
    # Indexes
    __table_args__ = (
        Index('idx_signature_contract', 'contract_id'),
        Index('idx_signature_signer', 'signer_user_id'),
        Index('idx_signature_hash', 'signature_hash'),
        Index('idx_signature_verified', 'is_verified'),
        Index('idx_signature_date', 'signed_at'),
        Index('idx_signature_revoked', 'revoked'),
        
        # Unique constraint to prevent duplicate signatures
        UniqueConstraint('contract_id', 'signer_user_id', 'signature_hash',
                        name='uq_contract_signer_signature'),
    )


class ContractWorkflowStep(Base):
    """
    Contract Workflow Step Model
    
    Manages automated workflow steps for contract processing,
    approvals, and lifecycle management.
    """
    __tablename__ = "contract_workflow_steps"
    
    # Primary identification
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Associated contract
    contract_id = Column(UUID(as_uuid=True), ForeignKey('contracts.id'), nullable=False, index=True)
    
    # Step configuration
    step_name = Column(String(255), nullable=False)
    step_type = Column(String(100), nullable=False)  # approval, review, signature, notification, etc.
    step_order = Column(Integer, nullable=False)
    
    # Step assignment
    assigned_to_user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=True)
    assigned_to_role = Column(String(100), nullable=True)
    assigned_to_group = Column(String(100), nullable=True)
    
    # Step status and timing
    status = Column(SQLEnum(WorkflowStatus), default=WorkflowStatus.PENDING, index=True)
    started_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    due_date = Column(DateTime(timezone=True), nullable=True)
    
    # Step configuration
    is_mandatory = Column(Boolean, default=True)
    is_parallel = Column(Boolean, default=False)
    auto_execute = Column(Boolean, default=False)
    timeout_hours = Column(Integer, nullable=True)
    
    # Step data and context
    step_data = Column(JSONB, nullable=True)
    input_parameters = Column(JSONB, nullable=True)
    output_results = Column(JSONB, nullable=True)
    
    # Decision and routing
    decision_made = Column(String(100), nullable=True)
    routing_rules = Column(JSONB, nullable=True)
    next_steps = Column(ARRAY(UUID), nullable=True)
    
    # Notifications and escalation
    notification_sent = Column(Boolean, default=False)
    reminder_count = Column(Integer, default=0)
    escalated = Column(Boolean, default=False)
    escalated_to = Column(UUID(as_uuid=True), nullable=True)
    escalated_at = Column(DateTime(timezone=True), nullable=True)
    
    # Error handling
    error_message = Column(Text, nullable=True)
    retry_count = Column(Integer, default=0)
    max_retries = Column(Integer, default=3)
    
    # Metadata
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    
    # Relationships
    contract = relationship("Contract", back_populates="workflow_steps")
    assigned_user = relationship("User", back_populates="assigned_workflow_steps")
    
    # Indexes
    __table_args__ = (
        Index('idx_workflow_contract', 'contract_id'),
        Index('idx_workflow_assigned', 'assigned_to_user_id'),
        Index('idx_workflow_status', 'status'),
        Index('idx_workflow_order', 'step_order'),
        Index('idx_workflow_due', 'due_date'),
        
        # Unique constraint for step order within contract
        UniqueConstraint('contract_id', 'step_order', name='uq_contract_step_order'),
    )


class ContractApproval(Base):
    """
    Contract Approval Model
    
    Tracks approval decisions with detailed comments,
    conditions, and delegation history.
    """
    __tablename__ = "contract_approvals"
    
    # Primary identification
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Associated entities
    contract_id = Column(UUID(as_uuid=True), ForeignKey('contracts.id'), nullable=False, index=True)
    workflow_step_id = Column(UUID(as_uuid=True), ForeignKey('contract_workflow_steps.id'), nullable=True, index=True)
    
    # Approver information
    approver_user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False, index=True)
    approver_role = Column(String(100), nullable=False)
    approval_authority = Column(String(100), nullable=True)
    
    # Approval decision
    action = Column(SQLEnum(ApprovalAction), nullable=False, index=True)
    decision_date = Column(DateTime(timezone=True), nullable=False)
    
    # Decision details
    comments = Column(Text, nullable=True)
    conditions = Column(JSONB, nullable=True)
    requested_changes = Column(JSONB, nullable=True)
    supporting_documents = Column(JSONB, nullable=True)
    
    # Delegation (if applicable)
    delegated_to_user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=True)
    delegation_reason = Column(Text, nullable=True)
    delegation_expiry = Column(DateTime(timezone=True), nullable=True)
    
    # Impact and consequences
    approval_level = Column(String(50), nullable=True)
    financial_impact = Column(Numeric(18, 6), nullable=True)
    risk_assessment = Column(JSONB, nullable=True)
    compliance_notes = Column(Text, nullable=True)
    
    # Process metadata
    time_to_decision_hours = Column(Float, nullable=True)
    decision_complexity = Column(String(50), nullable=True)
    review_duration_minutes = Column(Integer, nullable=True)
    
    # Audit information
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(String(500), nullable=True)
    device_fingerprint = Column(String(255), nullable=True)
    
    # Metadata
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    
    # Relationships
    contract = relationship("Contract", back_populates="approvals")
    workflow_step = relationship("ContractWorkflowStep", back_populates="approvals")
    approver = relationship("User", foreign_keys=[approver_user_id])
    delegated_to = relationship("User", foreign_keys=[delegated_to_user_id])
    
    # Indexes
    __table_args__ = (
        Index('idx_approval_contract', 'contract_id'),
        Index('idx_approval_approver', 'approver_user_id'),
        Index('idx_approval_action', 'action'),
        Index('idx_approval_date', 'decision_date'),
        Index('idx_approval_workflow', 'workflow_step_id'),
    )


class ContractAmendment(Base):
    """
    Contract Amendment Model
    
    Tracks contract modifications, addendums, and change history
    with version control and approval workflows.
    """
    __tablename__ = "contract_amendments"
    
    # Primary identification
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    amendment_number = Column(String(100), nullable=False, index=True)
    
    # Associated contract
    contract_id = Column(UUID(as_uuid=True), ForeignKey('contracts.id'), nullable=False, index=True)
    
    # Amendment details
    amendment_type = Column(String(100), nullable=False)  # modification, addendum, renewal, etc.
    title = Column(String(500), nullable=False)
    description = Column(Text, nullable=True)
    
    # Changes
    original_clauses = Column(JSONB, nullable=True)
    modified_clauses = Column(JSONB, nullable=True)
    added_clauses = Column(JSONB, nullable=True)
    removed_clauses = Column(JSONB, nullable=True)
    
    # Impact analysis
    financial_impact = Column(Numeric(18, 6), nullable=True)
    term_extension_days = Column(Integer, nullable=True)
    scope_changes = Column(JSONB, nullable=True)
    risk_impact = Column(JSONB, nullable=True)
    
    # Amendment status
    status = Column(String(50), default='draft', index=True)
    effective_date = Column(DateTime(timezone=True), nullable=True)
    requires_signatures = Column(Boolean, default=True)
    
    # Documentation
    amendment_document_url = Column(String(500), nullable=True)
    supporting_documents = Column(JSONB, nullable=True)
    legal_review_notes = Column(Text, nullable=True)
    
    # Approval workflow
    approval_required = Column(Boolean, default=True)
    approved_by = Column(UUID(as_uuid=True), nullable=True)
    approved_at = Column(DateTime(timezone=True), nullable=True)
    approval_notes = Column(Text, nullable=True)
    
    # Metadata
    reason_for_amendment = Column(Text, nullable=True)
    initiated_by = Column(UUID(as_uuid=True), nullable=False)
    version_before = Column(String(20), nullable=True)
    version_after = Column(String(20), nullable=True)
    
    # Audit trail
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    contract = relationship("Contract", back_populates="amendments")
    initiator = relationship("User", foreign_keys=[initiated_by])
    approver = relationship("User", foreign_keys=[approved_by])
    
    # Indexes
    __table_args__ = (
        Index('idx_amendment_contract', 'contract_id'),
        Index('idx_amendment_type', 'amendment_type'),
        Index('idx_amendment_status', 'status'),
        Index('idx_amendment_effective', 'effective_date'),
        Index('idx_amendment_initiator', 'initiated_by'),
        
        # Unique constraint for amendment numbers within contract
        UniqueConstraint('contract_id', 'amendment_number', name='uq_contract_amendment_number'),
    )


# Event listeners for automatic processing
@event.listens_for(Contract, 'before_insert')
def generate_contract_number(mapper, connection, target):
    """Generate contract number if not provided"""
    if not target.contract_number:
        prefix = target.contract_type.value.upper()[:3]
        timestamp = datetime.utcnow().strftime('%Y%m%d')
        unique_id = str(uuid.uuid4())[:8].upper()
        target.contract_number = f"{prefix}-{timestamp}-{unique_id}"


@event.listens_for(ContractAmendment, 'before_insert')
def generate_amendment_number(mapper, connection, target):
    """Generate amendment number if not provided"""
    if not target.amendment_number:
        timestamp = datetime.utcnow().strftime('%Y%m%d')
        unique_id = str(uuid.uuid4())[:6].upper()
        target.amendment_number = f"AMD-{timestamp}-{unique_id}"


__all__ = [
    'ContractType',
    'ContractStatus',
    'WorkflowStatus',
    'SignatureType',
    'ApprovalAction',
    'Contract',
    'ContractSignature',
    'ContractWorkflowStep',
    'ContractApproval',
    'ContractAmendment'
]
