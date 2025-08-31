"""
Regulatory Compliance Models - Enterprise Regulatory Compliance Management System

Ultra-advanced regulatory compliance system for international content protection,
financial regulations, data privacy, and platform-specific compliance requirements.

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

class ComplianceFramework(Enum):
    """Regulatory compliance frameworks"""
    GDPR = "gdpr"  # General Data Protection Regulation
    CCPA = "ccpa"  # California Consumer Privacy Act
    COPPA = "coppa"  # Children's Online Privacy Protection Act
    DMCA = "dmca"  # Digital Millennium Copyright Act
    PCI_DSS = "pci_dss"  # Payment Card Industry Data Security Standard
    SOX = "sox"  # Sarbanes-Oxley Act
    HIPAA = "hipaa"  # Health Insurance Portability and Accountability Act
    AML = "aml"  # Anti-Money Laundering
    KYC = "kyc"  # Know Your Customer
    MiFID_II = "mifid_ii"  # Markets in Financial Instruments Directive
    DSA = "dsa"  # Digital Services Act
    DMA = "dma"  # Digital Markets Act

class ComplianceStatus(Enum):
    """Compliance status levels"""
    COMPLIANT = "compliant"
    NON_COMPLIANT = "non_compliant"
    PARTIALLY_COMPLIANT = "partially_compliant"
    UNDER_REVIEW = "under_review"
    REMEDIATION_IN_PROGRESS = "remediation_in_progress"
    NOT_APPLICABLE = "not_applicable"
    PENDING_ASSESSMENT = "pending_assessment"

class RiskLevel(Enum):
    """Risk assessment levels"""
    VERY_LOW = "very_low"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class AuditType(Enum):
    """Audit types"""
    INTERNAL = "internal"
    EXTERNAL = "external"
    REGULATORY = "regulatory"
    THIRD_PARTY = "third_party"
    SELF_ASSESSMENT = "self_assessment"

class ComplianceRequirement(Base):
    """Regulatory compliance requirements database"""
    __tablename__ = 'compliance_requirements'
    
    # Primary identification
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    requirement_id = Column(String(100), unique=True, nullable=False)
    framework = Column(String(50), nullable=False)
    
    # Requirement details
    title = Column(String(500), nullable=False)
    description = Column(Text, nullable=False)
    category = Column(String(100), nullable=False)
    subcategory = Column(String(100))
    
    # Legal and regulatory context
    legal_basis = Column(Text)
    authority = Column(String(200))  # Regulatory authority
    jurisdiction = Column(String(100))
    effective_date = Column(DateTime(timezone=True))
    
    # Applicability criteria
    business_types = Column(ARRAY(String))  # Types of businesses this applies to
    revenue_thresholds = Column(JSONB)  # Revenue thresholds for applicability
    user_count_thresholds = Column(JSONB)  # User count thresholds
    geographic_scope = Column(ARRAY(String))  # Countries/regions where applicable
    
    # Requirements specification
    technical_requirements = Column(JSONB)
    operational_requirements = Column(JSONB)
    documentation_requirements = Column(JSONB)
    reporting_requirements = Column(JSONB)
    
    # Compliance criteria
    success_criteria = Column(JSONB)
    measurement_methods = Column(JSONB)
    evidence_requirements = Column(JSONB)
    
    # Penalties and consequences
    violation_penalties = Column(JSONB)
    enforcement_actions = Column(JSONB)
    reputation_risks = Column(JSONB)
    
    # Implementation guidance
    best_practices = Column(JSONB)
    implementation_steps = Column(JSONB)
    recommended_tools = Column(JSONB)
    
    # Updates and versioning
    version = Column(String(20), default='1.0')
    last_updated_by_authority = Column(DateTime(timezone=True))
    next_review_date = Column(DateTime(timezone=True))
    superseded_by = Column(UUID(as_uuid=True))
    
    # Status
    is_active = Column(Boolean, default=True)
    is_mandatory = Column(Boolean, default=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), default=func.now())
    updated_at = Column(DateTime(timezone=True), default=func.now(), onupdate=func.now())
    
    # Indexes
    __table_args__ = (
        Index('idx_compliance_req_framework', 'framework', 'is_active'),
        Index('idx_compliance_req_category', 'category', 'subcategory'),
        Index('idx_compliance_req_jurisdiction', 'jurisdiction', 'effective_date'),
    )

class CreatorComplianceProfile(Base):
    """Creator compliance profile and status"""
    __tablename__ = 'creator_compliance_profiles'
    
    # Primary identification
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    creator_id = Column(UUID(as_uuid=True), unique=True, nullable=False, index=True)
    
    # Business information
    business_type = Column(String(50), nullable=False)
    annual_revenue = Column(DECIMAL(15, 4))
    monthly_active_users = Column(BigInteger, default=0)
    operating_jurisdictions = Column(ARRAY(String))
    
    # Applicable frameworks
    applicable_frameworks = Column(ARRAY(String))
    voluntary_frameworks = Column(ARRAY(String))
    exemptions_claimed = Column(JSONB)
    
    # Overall compliance status
    overall_compliance_score = Column(Float, default=0.0)
    last_assessment_date = Column(DateTime(timezone=True))
    next_assessment_due = Column(DateTime(timezone=True))
    
    # Data protection compliance
    data_protection_officer_appointed = Column(Boolean, default=False)
    privacy_policy_updated = Column(DateTime(timezone=True))
    cookie_policy_updated = Column(DateTime(timezone=True))
    data_retention_policy_defined = Column(Boolean, default=False)
    
    # Content protection compliance
    dmca_agent_registered = Column(Boolean, default=False)
    content_id_system_implemented = Column(Boolean, default=False)
    takedown_procedures_documented = Column(Boolean, default=False)
    
    # Financial compliance
    aml_program_implemented = Column(Boolean, default=False)
    kyc_procedures_documented = Column(Boolean, default=False)
    transaction_monitoring_enabled = Column(Boolean, default=False)
    
    # Platform compliance
    platform_policies_acknowledged = Column(JSONB)
    platform_certifications = Column(JSONB)
    platform_audit_status = Column(JSONB)
    
    # Compliance team and resources
    compliance_officer = Column(UUID(as_uuid=True))
    legal_counsel = Column(JSONB)
    compliance_budget_annual = Column(DECIMAL(10, 4))
    training_completion_status = Column(JSONB)
    
    # Risk assessment
    current_risk_level = Column(String(20), default=RiskLevel.MEDIUM.value)
    risk_factors = Column(JSONB)
    mitigation_strategies = Column(JSONB)
    
    # Audit history
    last_external_audit = Column(DateTime(timezone=True))
    audit_findings_outstanding = Column(Integer, default=0)
    certification_status = Column(JSONB)
    
    # Incident management
    compliance_incidents_ytd = Column(Integer, default=0)
    last_incident_date = Column(DateTime(timezone=True))
    incident_response_plan = Column(Boolean, default=False)
    
    # Notifications and monitoring
    monitoring_enabled = Column(Boolean, default=True)
    alert_thresholds = Column(JSONB)
    notification_preferences = Column(JSONB)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), default=func.now())
    updated_at = Column(DateTime(timezone=True), default=func.now(), onupdate=func.now())
    
    # Indexes
    __table_args__ = (
        Index('idx_creator_compliance_score', 'overall_compliance_score', 'last_assessment_date'),
        Index('idx_creator_compliance_risk', 'current_risk_level', 'updated_at'),
    )

class ComplianceAssessment(Base):
    """Compliance assessment results and findings"""
    __tablename__ = 'compliance_assessments'
    
    # Primary identification
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    creator_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    requirement_id = Column(UUID(as_uuid=True), ForeignKey('compliance_requirements.id'), nullable=False)
    
    # Assessment details
    assessment_type = Column(String(20), nullable=False)
    assessment_scope = Column(String(100))
    methodology = Column(String(100))
    
    # Assessment results
    compliance_status = Column(String(30), nullable=False)
    compliance_score = Column(Float, default=0.0)  # 0-100 score
    risk_rating = Column(String(20), nullable=False)
    
    # Findings
    findings_summary = Column(Text)
    strengths_identified = Column(JSONB)
    weaknesses_identified = Column(JSONB)
    gaps_identified = Column(JSONB)
    
    # Evidence and documentation
    evidence_collected = Column(JSONB)
    documentation_reviewed = Column(JSONB)
    interviews_conducted = Column(JSONB)
    technical_tests_performed = Column(JSONB)
    
    # Recommendations
    immediate_actions_required = Column(JSONB)
    improvement_recommendations = Column(JSONB)
    best_practice_suggestions = Column(JSONB)
    timeline_for_remediation = Column(JSONB)
    
    # Assessment team
    lead_assessor = Column(UUID(as_uuid=True))
    assessment_team = Column(JSONB)
    external_auditor = Column(String(200))
    
    # Quality and validation
    review_status = Column(String(20), default='pending')
    reviewed_by = Column(UUID(as_uuid=True))
    reviewed_at = Column(DateTime(timezone=True))
    quality_score = Column(Float, default=0.0)
    
    # Follow-up and monitoring
    follow_up_required = Column(Boolean, default=False)
    next_assessment_due = Column(DateTime(timezone=True))
    monitoring_frequency = Column(String(20))  # continuous, monthly, quarterly, annual
    
    # Impact assessment
    business_impact = Column(String(20))  # low, medium, high
    financial_impact = Column(DECIMAL(15, 4))
    reputation_impact = Column(String(20))
    operational_impact = Column(String(20))
    
    # Timestamps
    assessment_date = Column(DateTime(timezone=True), nullable=False)
    assessment_period_start = Column(DateTime(timezone=True))
    assessment_period_end = Column(DateTime(timezone=True))
    report_issued_date = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), default=func.now())
    updated_at = Column(DateTime(timezone=True), default=func.now(), onupdate=func.now())
    
    # Relationships
    requirement = relationship("ComplianceRequirement", backref="assessments")
    
    # Indexes
    __table_args__ = (
        Index('idx_compliance_assess_creator_date', 'creator_id', 'assessment_date'),
        Index('idx_compliance_assess_status_risk', 'compliance_status', 'risk_rating'),
        Index('idx_compliance_assess_requirement', 'requirement_id', 'assessment_date'),
    )

class ComplianceAction(Base):
    """Compliance remediation and improvement actions"""
    __tablename__ = 'compliance_actions'
    
    # Primary identification
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    creator_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    assessment_id = Column(UUID(as_uuid=True), ForeignKey('compliance_assessments.id'))
    
    # Action details
    action_type = Column(String(50), nullable=False)  # remediation, improvement, preventive
    category = Column(String(50), nullable=False)
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=False)
    
    # Priority and urgency
    priority = Column(String(20), nullable=False)  # low, medium, high, critical
    urgency = Column(String(20), nullable=False)  # low, medium, high, urgent
    regulatory_deadline = Column(DateTime(timezone=True))
    
    # Implementation details
    implementation_plan = Column(JSONB)
    required_resources = Column(JSONB)
    estimated_cost = Column(DECIMAL(15, 4))
    estimated_duration = Column(Integer)  # days
    
    # Assignment and responsibility
    assigned_to = Column(UUID(as_uuid=True))
    responsible_team = Column(String(100))
    external_support_required = Column(Boolean, default=False)
    external_providers = Column(JSONB)
    
    # Dependencies and prerequisites
    dependencies = Column(JSONB)
    prerequisites = Column(JSONB)
    blocking_issues = Column(JSONB)
    
    # Status and progress
    status = Column(String(20), default='planned')  # planned, in_progress, completed, cancelled, on_hold
    progress_percentage = Column(Float, default=0.0)
    milestone_status = Column(JSONB)
    
    # Timeline
    planned_start_date = Column(DateTime(timezone=True))
    planned_completion_date = Column(DateTime(timezone=True))
    actual_start_date = Column(DateTime(timezone=True))
    actual_completion_date = Column(DateTime(timezone=True))
    
    # Outcomes and results
    completion_evidence = Column(JSONB)
    effectiveness_measurement = Column(JSONB)
    compliance_improvement = Column(Float, default=0.0)
    risk_reduction = Column(Float, default=0.0)
    
    # Verification and validation
    verification_required = Column(Boolean, default=True)
    verification_method = Column(String(100))
    verified_by = Column(UUID(as_uuid=True))
    verification_date = Column(DateTime(timezone=True))
    verification_status = Column(String(20), default='pending')
    
    # Communication and reporting
    stakeholder_notifications = Column(JSONB)
    progress_reports = Column(JSONB)
    escalation_triggers = Column(JSONB)
    
    # Lessons learned
    challenges_encountered = Column(JSONB)
    solutions_developed = Column(JSONB)
    best_practices_identified = Column(JSONB)
    recommendations_for_future = Column(JSONB)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), default=func.now())
    updated_at = Column(DateTime(timezone=True), default=func.now(), onupdate=func.now())
    
    # Relationships
    assessment = relationship("ComplianceAssessment", backref="actions")
    
    # Indexes
    __table_args__ = (
        Index('idx_compliance_action_creator_status', 'creator_id', 'status'),
        Index('idx_compliance_action_priority_deadline', 'priority', 'regulatory_deadline'),
        Index('idx_compliance_action_assigned', 'assigned_to', 'status'),
    )

class ComplianceMonitoring(Base):
    """Continuous compliance monitoring and alerts"""
    __tablename__ = 'compliance_monitoring'
    
    # Primary identification
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    creator_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    requirement_id = Column(UUID(as_uuid=True), ForeignKey('compliance_requirements.id'), nullable=False)
    
    # Monitoring configuration
    monitoring_type = Column(String(50), nullable=False)  # automated, manual, hybrid
    monitoring_frequency = Column(String(20), nullable=False)  # real_time, hourly, daily, weekly
    
    # Metrics and thresholds
    monitored_metrics = Column(JSONB, nullable=False)
    compliance_thresholds = Column(JSONB)
    warning_thresholds = Column(JSONB)
    critical_thresholds = Column(JSONB)
    
    # Current status
    current_status = Column(String(30), nullable=False)
    last_check_timestamp = Column(DateTime(timezone=True))
    next_check_scheduled = Column(DateTime(timezone=True))
    
    # Measurement results
    current_measurements = Column(JSONB)
    trend_analysis = Column(JSONB)
    variance_from_baseline = Column(Float, default=0.0)
    
    # Alert configuration
    alerts_enabled = Column(Boolean, default=True)
    alert_recipients = Column(JSONB)
    escalation_rules = Column(JSONB)
    
    # Performance tracking
    monitoring_reliability = Column(Float, default=0.0)
    false_positive_rate = Column(Float, default=0.0)
    response_time_metrics = Column(JSONB)
    
    # Data sources
    data_sources = Column(JSONB)
    collection_methods = Column(JSONB)
    data_quality_scores = Column(JSONB)
    
    # Automation and integration
    automated_remediation = Column(Boolean, default=False)
    integration_endpoints = Column(JSONB)
    api_configurations = Column(JSONB)
    
    # Status and control
    is_active = Column(Boolean, default=True)
    monitoring_paused = Column(Boolean, default=False)
    pause_reason = Column(String(200))
    pause_until = Column(DateTime(timezone=True))
    
    # Timestamps
    monitoring_started = Column(DateTime(timezone=True), default=func.now())
    created_at = Column(DateTime(timezone=True), default=func.now())
    updated_at = Column(DateTime(timezone=True), default=func.now(), onupdate=func.now())
    
    # Relationships
    requirement = relationship("ComplianceRequirement", backref="monitoring_configs")
    
    # Indexes
    __table_args__ = (
        Index('idx_compliance_monitoring_creator', 'creator_id', 'is_active'),
        Index('idx_compliance_monitoring_status', 'current_status', 'last_check_timestamp'),
        Index('idx_compliance_monitoring_next_check', 'next_check_scheduled', 'is_active'),
    )

class ComplianceIncident(Base):
    """Compliance incidents and violations"""
    __tablename__ = 'compliance_incidents'
    
    # Primary identification
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    incident_number = Column(String(50), unique=True, nullable=False)
    creator_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    
    # Incident classification
    incident_type = Column(String(50), nullable=False)  # violation, breach, near_miss, potential_risk
    severity = Column(String(20), nullable=False)
    category = Column(String(50), nullable=False)
    affected_frameworks = Column(ARRAY(String))
    
    # Incident details
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=False)
    root_cause_analysis = Column(Text)
    
    # Discovery and reporting
    discovered_by = Column(String(50))  # internal, external, regulatory, customer
    discovery_method = Column(String(100))
    reported_by = Column(UUID(as_uuid=True))
    external_reporter_details = Column(JSONB)
    
    # Timeline
    incident_occurred_at = Column(DateTime(timezone=True), nullable=False)
    discovered_at = Column(DateTime(timezone=True), nullable=False)
    reported_at = Column(DateTime(timezone=True), default=func.now())
    
    # Impact assessment
    affected_systems = Column(JSONB)
    affected_data_subjects = Column(Integer, default=0)
    data_compromised = Column(Boolean, default=False)
    financial_impact = Column(DECIMAL(15, 4), default=0)
    reputation_impact = Column(String(20))
    
    # Regulatory implications
    regulatory_reporting_required = Column(Boolean, default=False)
    regulatory_deadlines = Column(JSONB)
    potential_penalties = Column(DECIMAL(15, 4))
    regulatory_responses = Column(JSONB)
    
    # Response and containment
    immediate_actions_taken = Column(JSONB)
    containment_measures = Column(JSONB)
    stakeholders_notified = Column(JSONB)
    customer_notifications = Column(JSONB)
    
    # Investigation
    investigation_team = Column(JSONB)
    investigation_findings = Column(Text)
    evidence_collected = Column(JSONB)
    external_investigation_required = Column(Boolean, default=False)
    
    # Resolution and remediation
    resolution_plan = Column(JSONB)
    corrective_actions = Column(JSONB)
    preventive_measures = Column(JSONB)
    
    # Status tracking
    status = Column(String(20), default='open')  # open, investigating, resolving, closed, escalated
    assigned_to = Column(UUID(as_uuid=True))
    resolution_deadline = Column(DateTime(timezone=True))
    
    # Closure and lessons learned
    resolution_summary = Column(Text)
    lessons_learned = Column(JSONB)
    process_improvements = Column(JSONB)
    closed_by = Column(UUID(as_uuid=True))
    closed_at = Column(DateTime(timezone=True))
    
    # Follow-up and monitoring
    follow_up_required = Column(Boolean, default=False)
    monitoring_enhancements = Column(JSONB)
    similar_incident_prevention = Column(JSONB)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), default=func.now())
    updated_at = Column(DateTime(timezone=True), default=func.now(), onupdate=func.now())
    
    # Indexes
    __table_args__ = (
        Index('idx_compliance_incident_creator', 'creator_id', 'status'),
        Index('idx_compliance_incident_severity', 'severity', 'incident_occurred_at'),
        Index('idx_compliance_incident_type', 'incident_type', 'category'),
    )

@dataclass
class ComplianceDashboard:
    """Compliance dashboard data structure"""
    overall_score: float
    framework_scores: Dict[str, float]
    risk_level: str
    active_incidents: int
    overdue_actions: int
    upcoming_deadlines: List[Dict]
    recent_assessments: List[Dict]
    compliance_trends: Dict[str, Any]

class RegulatoryUpdate(Base):
    """Regulatory updates and changes tracking"""
    __tablename__ = 'regulatory_updates'
    
    # Primary identification
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    update_id = Column(String(100), unique=True, nullable=False)
    
    # Update details
    framework = Column(String(50), nullable=False)
    jurisdiction = Column(String(100), nullable=False)
    authority = Column(String(200), nullable=False)
    
    # Change information
    update_type = Column(String(50), nullable=False)  # new_regulation, amendment, clarification, enforcement_change
    title = Column(String(500), nullable=False)
    summary = Column(Text, nullable=False)
    detailed_changes = Column(Text)
    
    # Impact analysis
    affected_requirements = Column(ARRAY(String))
    business_impact = Column(String(20))  # low, medium, high
    implementation_complexity = Column(String(20))
    estimated_compliance_cost = Column(DECIMAL(15, 4))
    
    # Timeline
    announcement_date = Column(DateTime(timezone=True), nullable=False)
    effective_date = Column(DateTime(timezone=True))
    compliance_deadline = Column(DateTime(timezone=True))
    grace_period_end = Column(DateTime(timezone=True))
    
    # Implementation guidance
    implementation_guidance = Column(Text)
    recommended_actions = Column(JSONB)
    transition_provisions = Column(JSONB)
    
    # Stakeholder notifications
    affected_creators = Column(ARRAY(String))  # Creator IDs or segments
    notification_status = Column(JSONB)
    communication_plan = Column(JSONB)
    
    # Monitoring and tracking
    implementation_tracking = Column(JSONB)
    compliance_monitoring_changes = Column(JSONB)
    
    # Source and references
    official_documents = Column(JSONB)
    reference_links = Column(ARRAY(String))
    legal_opinions = Column(JSONB)
    
    # Status
    status = Column(String(20), default='active')  # active, superseded, withdrawn
    superseded_by = Column(UUID(as_uuid=True))
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), default=func.now())
    updated_at = Column(DateTime(timezone=True), default=func.now(), onupdate=func.now())
    
    # Indexes
    __table_args__ = (
        Index('idx_regulatory_update_framework', 'framework', 'effective_date'),
        Index('idx_regulatory_update_deadline', 'compliance_deadline', 'status'),
        Index('idx_regulatory_update_impact', 'business_impact', 'announcement_date'),
    )

# Export all models for easy import
__all__ = [
    'ComplianceFramework',
    'ComplianceStatus',
    'RiskLevel',
    'AuditType',
    'ComplianceRequirement',
    'CreatorComplianceProfile',
    'ComplianceAssessment',
    'ComplianceAction',
    'ComplianceMonitoring',
    'ComplianceIncident',
    'ComplianceDashboard',
    'RegulatoryUpdate'
]
