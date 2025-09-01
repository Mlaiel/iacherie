"""Audit Trails Models - Enterprise Audit & Security Logging System

Ultra-advanced audit trail system for comprehensive logging, compliance tracking,
security monitoring, and forensic analysis for content monetization operations.

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

class AuditEventType(Enum):
    """
Audit event type classifications"""

    AUTHENTICATION = "authentication"
    AUTHORIZATION = "authorization"
    DATA_ACCESS = "data_access"
    DATA_MODIFICATION = "data_modification"
    FINANCIAL_TRANSACTION = "financial_transaction"
    PAYMENT_PROCESSING = "payment_processing"
    COMPLIANCE_CHECK = "compliance_check"
    SECURITY_EVENT = "security_event"
    SYSTEM_CONFIGURATION = "system_configuration"
    USER_MANAGEMENT = "user_management"
    CONTENT_PROTECTION = "content_protection"
    API_ACCESS = "api_access"
    REPORTING = "reporting"
    INTEGRATION = "integration"

class AuditEventSeverity(Enum):
    """Audit event severity levels"""

    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"
    SECURITY = "security"

class AuditStatus(Enum):
    """Audit record status"""

    ACTIVE = "active"
    ARCHIVED = "archived"
    UNDER_INVESTIGATION = "under_investigation"
    FLAGGED = "flagged"
    RESOLVED = "resolved"

class AuditEventSource(Enum):
    """Source of audit events"""

    WEB_APPLICATION = "web_application"
    MOBILE_APPLICATION = "mobile_application"
    API_GATEWAY = "api_gateway"
    BACKGROUND_SERVICE = "background_service"
    PAYMENT_PROCESSOR = "payment_processor"
    EXTERNAL_INTEGRATION = "external_integration"
    SYSTEM_PROCESS = "system_process"
    ADMIN_INTERFACE = "admin_interface"

class AuditEvent(Base):
    """Comprehensive audit event logging"""
    __tablename__ = 'audit_events'
    
    # Primary identification
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    event_id = Column(String(100), unique=True, nullable=False)  # External event ID
    correlation_id = Column(String(100), index=True)  # For tracking related events
    
    # Event classification
    event_type = Column(String(50), nullable=False)
    event_category = Column(String(50), nullable=False)
    event_subcategory = Column(String(50))
    severity = Column(String(20), nullable=False)
    
    # Event details
    event_name = Column(String(200), nullable=False)
    event_description = Column(Text)
    event_outcome = Column(String(20), nullable=False)  # success, failure, partial, pending
    
    # Actor information
    user_id = Column(UUID(as_uuid=True), index=True)
    username = Column(String(100))
    user_type = Column(String(20))  # creator, admin, system, api_client
    session_id = Column(String(100))
    
    # Target information
    target_type = Column(String(50))  # user, content, payment, system
    target_id = Column(String(100), index=True)
    target_name = Column(String(200))
    affected_entities = Column(JSONB)
    
    # Request context
    source = Column(String(50), nullable=False)
    source_ip = Column(String(45))  # IPv4 or IPv6
    user_agent = Column(String(1000))
    request_method = Column(String(10))
    request_url = Column(String(2000))
    request_headers = Column(JSONB)
    
    # Response context
    response_status = Column(Integer)
    response_time_ms = Column(Integer)
    response_size_bytes = Column(BigInteger)
    error_code = Column(String(50))
    error_message = Column(Text)
    
    # Data changes
    old_values = Column(JSONB)  # Before state
    new_values = Column(JSONB)  # After state
    changed_fields = Column(ARRAY(String))
    
    # Financial context
    transaction_amount = Column(DECIMAL(15, 4))
    transaction_currency = Column(String(3))
    payment_method = Column(String(50))
    financial_impact = Column(String(20))  # none, low, medium, high
    
    # Security context
    authentication_method = Column(String(50))
    authorization_result = Column(String(20))
    security_flags = Column(ARRAY(String))
    risk_score = Column(Float, default=0.0)
    
    # Compliance context
    compliance_frameworks = Column(ARRAY(String))
    retention_period_years = Column(Integer, default=7)
    data_classification = Column(String(20))  # public, internal, confidential, restricted
    
    # Geographic context
    country_code = Column(String(2))
    region = Column(String(100))
    timezone = Column(String(50))
    
    # Technical context
    application_version = Column(String(20))
    api_version = Column(String(10))
    service_name = Column(String(100))
    instance_id = Column(String(100))
    
    # Additional metadata
    tags = Column(ARRAY(String))
    custom_attributes = Column(JSONB)
    trace_id = Column(String(100))  # Distributed tracing
    span_id = Column(String(100))
    
    # Processing and analysis
    processed = Column(Boolean, default=False)
    analysis_results = Column(JSONB)
    anomaly_score = Column(Float, default=0.0)
    
    # Status and lifecycle
    status = Column(String(30), default=AuditStatus.ACTIVE.value)
    flagged_for_review = Column(Boolean, default=False)
    reviewed_by = Column(UUID(as_uuid=True))
    reviewed_at = Column(DateTime(timezone=True))
    
    # Timestamps
    event_timestamp = Column(DateTime(timezone=True), nullable=False)
    ingested_at = Column(DateTime(timezone=True), default=func.now())
    created_at = Column(DateTime(timezone=True), default=func.now())
    
    # Indexes for performance and compliance
    __table_args__ = (
        Index('idx_audit_event_timestamp', 'event_timestamp'),
        Index('idx_audit_event_type_severity', 'event_type', 'severity'),
        Index('idx_audit_user_timestamp', 'user_id', 'event_timestamp'),
        Index('idx_audit_target_timestamp', 'target_id', 'event_timestamp'),
        Index('idx_audit_correlation', 'correlation_id'),
        Index('idx_audit_source_ip', 'source_ip', 'event_timestamp'),
        Index('idx_audit_outcome_severity', 'event_outcome', 'severity'),
        Index('idx_audit_compliance', 'compliance_frameworks'),
    )

class AuditSummary(Base):
    """
Daily audit event summaries for reporting"""
    __tablename__ = 'audit_summaries'
    
    # Primary identification
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    summary_date = Column(DateTime(timezone=True), nullable=False)
    summary_type = Column(String(20), nullable=False)  # daily, weekly, monthly
    
    # Scope
    creator_id = Column(UUID(as_uuid=True), index=True)
    event_type = Column(String(50))
    source = Column(String(50))
    
    # Event counts
    total_events = Column(BigInteger, default=0)
    successful_events = Column(BigInteger, default=0)
    failed_events = Column(BigInteger, default=0)
    security_events = Column(BigInteger, default=0)
    critical_events = Column(BigInteger, default=0)
    
    # Event type breakdown
    authentication_events = Column(BigInteger, default=0)
    data_access_events = Column(BigInteger, default=0)
    financial_events = Column(BigInteger, default=0)
    compliance_events = Column(BigInteger, default=0)
    api_events = Column(BigInteger, default=0)
    
    # User activity
    unique_users = Column(Integer, default=0)
    active_sessions = Column(Integer, default=0)
    failed_logins = Column(Integer, default=0)
    
    # Geographic distribution
    unique_countries = Column(Integer, default=0)
    top_countries = Column(JSONB)
    suspicious_locations = Column(JSONB)
    
    # Financial activity
    total_transaction_amount = Column(DECIMAL(15, 4), default=0)
    transaction_count = Column(Integer, default=0)
    failed_payments = Column(Integer, default=0)
    refund_requests = Column(Integer, default=0)
    
    # Security metrics
    anomaly_detections = Column(Integer, default=0)
    blocked_requests = Column(Integer, default=0)
    rate_limit_violations = Column(Integer, default=0)
    average_risk_score = Column(Float, default=0.0)
    
    # Performance metrics
    average_response_time = Column(Float, default=0.0)
    peak_request_rate = Column(Integer, default=0)
    error_rate_percentage = Column(Float, default=0.0)
    
    # Data quality
    incomplete_events = Column(Integer, default=0)
    data_quality_score = Column(Float, default=100.0)
    
    # Compliance tracking
    retention_compliance_score = Column(Float, default=100.0)
    gdpr_requests_processed = Column(Integer, default=0)
    audit_requests_fulfilled = Column(Integer, default=0)
    
    # Timestamps
    period_start = Column(DateTime(timezone=True), nullable=False)
    period_end = Column(DateTime(timezone=True), nullable=False)
    calculated_at = Column(DateTime(timezone=True), default=func.now())
    created_at = Column(DateTime(timezone=True), default=func.now())
    
    # Indexes
    __table_args__ = (
        Index('idx_audit_summary_date_type', 'summary_date', 'summary_type'),
        Index('idx_audit_summary_creator', 'creator_id', 'summary_date'),
        UniqueConstraint('summary_date', 'summary_type', 'creator_id', 'event_type', name='uq_audit_summary'),
    )

class DataRetentionPolicy(Base):
    """
Data retention policies for audit logs"""
    __tablename__ = 'data_retention_policies'
    
    # Primary identification
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    policy_name = Column(String(200), nullable=False, unique=True)
    policy_code = Column(String(50), nullable=False, unique=True)
    
    # Policy scope
    event_types = Column(ARRAY(String))  # Applicable event types
    data_classifications = Column(ARRAY(String))  # Applicable data classifications
    jurisdictions = Column(ARRAY(String))  # Applicable jurisdictions
    user_types = Column(ARRAY(String))  # Applicable user types
    
    # Retention rules
    retention_period_days = Column(Integer, nullable=False)
    minimum_retention_days = Column(Integer, default=30)
    maximum_retention_days = Column(Integer)
    
    # Legal and compliance basis
    legal_basis = Column(Text)
    compliance_frameworks = Column(ARRAY(String))
    regulatory_requirements = Column(JSONB)
    
    # Lifecycle management
    archival_after_days = Column(Integer)
    archival_storage_type = Column(String(50))  # cold_storage, tape, cloud_archive
    deletion_after_days = Column(Integer)
    secure_deletion_required = Column(Boolean, default=True)
    
    # Exceptions and holds
    litigation_hold_override = Column(Boolean, default=True)
    regulatory_hold_override = Column(Boolean, default=True)
    user_consent_override = Column(Boolean, default=False)
    
    # Processing rules
    anonymization_after_days = Column(Integer)
    pseudonymization_after_days = Column(Integer)
    encryption_requirements = Column(JSONB)
    
    # Implementation details
    automated_processing = Column(Boolean, default=True)
    batch_size = Column(Integer, default=1000)
    processing_frequency = Column(String(20), default='daily')
    
    # Monitoring and alerts
    monitoring_enabled = Column(Boolean, default=True)
    alert_thresholds = Column(JSONB)
    notification_recipients = Column(JSONB)
    
    # Status and control
    is_active = Column(Boolean, default=True)
    enforcement_date = Column(DateTime(timezone=True))
    last_processed_at = Column(DateTime(timezone=True))
    
    # Approval and governance
    approved_by = Column(UUID(as_uuid=True))
    approval_date = Column(DateTime(timezone=True))
    next_review_date = Column(DateTime(timezone=True))
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), default=func.now())
    updated_at = Column(DateTime(timezone=True), default=func.now(), onupdate=func.now())
    
    # Indexes
    __table_args__ = (
        Index('idx_retention_policy_active', 'is_active', 'enforcement_date'),
        Index('idx_retention_policy_processing', 'automated_processing', 'last_processed_at'),
    )

class AuditQuery(Base):
    """
Audit query history and compliance requests"""
    __tablename__ = 'audit_queries'
    
    # Primary identification
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    query_id = Column(String(100), unique=True, nullable=False)
    
    # Query details
    query_type = Column(String(50), nullable=False)  # compliance, investigation, reporting, analysis
    query_purpose = Column(String(100), nullable=False)
    query_description = Column(Text)
    
    # Requester information
    requested_by = Column(UUID(as_uuid=True), nullable=False)
    requester_role = Column(String(50))
    requester_organization = Column(String(200))
    legal_basis = Column(String(100))
    
    # Query parameters
    date_range_start = Column(DateTime(timezone=True), nullable=False)
    date_range_end = Column(DateTime(timezone=True), nullable=False)
    user_filters = Column(JSONB)
    event_type_filters = Column(ARRAY(String))
    search_criteria = Column(JSONB)
    
    # Authorization and approval
    approval_required = Column(Boolean, default=False)
    approved_by = Column(UUID(as_uuid=True))
    approval_date = Column(DateTime(timezone=True))
    approval_conditions = Column(JSONB)
    
    # Query execution
    execution_status = Column(String(20), default='pending')  # pending, running, completed, failed, cancelled
    execution_started_at = Column(DateTime(timezone=True))
    execution_completed_at = Column(DateTime(timezone=True))
    execution_duration_seconds = Column(Integer)
    
    # Results
    records_found = Column(BigInteger, default=0)
    records_returned = Column(BigInteger, default=0)
    result_format = Column(String(20))  # json, csv, pdf, xml
    result_file_path = Column(String(500))
    result_checksum = Column(String(64))
    
    # Data protection
    data_masked = Column(Boolean, default=False)
    masking_rules_applied = Column(JSONB)
    redaction_summary = Column(JSONB)
    
    # Delivery and access
    delivery_method = Column(String(50))  # download, email, secure_portal, api
    access_granted_until = Column(DateTime(timezone=True))
    download_count = Column(Integer, default=0)
    last_accessed_at = Column(DateTime(timezone=True))
    
    # Compliance tracking
    compliance_framework = Column(String(50))
    regulatory_reference = Column(String(200))
    case_number = Column(String(100))
    
    # Quality and validation
    data_quality_checks = Column(JSONB)
    validation_results = Column(JSONB)
    completeness_score = Column(Float, default=100.0)
    
    # Cost and resources
    query_cost = Column(DECIMAL(10, 4), default=0)
    resource_usage = Column(JSONB)
    priority = Column(String(20), default='normal')
    
    # Follow-up and tracking
    follow_up_required = Column(Boolean, default=False)
    follow_up_date = Column(DateTime(timezone=True))
    related_queries = Column(ARRAY(String))
    
    # Timestamps
    requested_at = Column(DateTime(timezone=True), default=func.now())
    due_date = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), default=func.now())
    updated_at = Column(DateTime(timezone=True), default=func.now(), onupdate=func.now())
    
    # Indexes
    __table_args__ = (
        Index('idx_audit_query_requester', 'requested_by', 'requested_at'),
        Index('idx_audit_query_status_due', 'execution_status', 'due_date'),
        Index('idx_audit_query_type_framework', 'query_type', 'compliance_framework'),
    )

@dataclass
class AuditMetrics:
    """
Audit metrics data structure"""
    total_events: int
    events_by_type: Dict[str, int]
    events_by_severity: Dict[str, int]
    success_rate: float
    error_rate: float
    security_incidents: int
    compliance_score: float
    data_quality_score: float
    retention_compliance: float

class ForensicInvestigation(Base):
    """
Forensic investigation case management"""
    __tablename__ = 'forensic_investigations'
    
    # Primary identification
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    case_number = Column(String(50), unique=True, nullable=False)
    case_name = Column(String(200), nullable=False)
    
    # Case details
    investigation_type = Column(String(50), nullable=False)  # security_breach, fraud, compliance, internal
    severity = Column(String(20), nullable=False)
    priority = Column(String(20), nullable=False)
    
    # Case description
    incident_description = Column(Text, nullable=False)
    initial_findings = Column(Text)
    hypothesis = Column(Text)
    scope_definition = Column(Text)
    
    # Timeline
    incident_occurred_at = Column(DateTime(timezone=True))
    incident_discovered_at = Column(DateTime(timezone=True))
    investigation_started_at = Column(DateTime(timezone=True), default=func.now())
    target_completion_date = Column(DateTime(timezone=True))
    
    # Investigation team
    lead_investigator = Column(UUID(as_uuid=True), nullable=False)
    investigation_team = Column(JSONB)
    external_experts = Column(JSONB)
    
    # Evidence collection
    evidence_collection_plan = Column(JSONB)
    evidence_preservation_methods = Column(JSONB)
    chain_of_custody = Column(JSONB)
    digital_evidence_hashes = Column(JSONB)
    
    # Analysis scope
    date_range_start = Column(DateTime(timezone=True))
    date_range_end = Column(DateTime(timezone=True))
    affected_systems = Column(JSONB)
    affected_users = Column(JSONB)
    
    # Investigation progress
    status = Column(String(20), default='active')  # active, suspended, completed, closed
    progress_percentage = Column(Float, default=0.0)
    milestones = Column(JSONB)
    current_phase = Column(String(50))
    
    # Findings and analysis
    evidence_summary = Column(JSONB)
    technical_findings = Column(Text)
    business_impact_assessment = Column(JSONB)
    root_cause_analysis = Column(Text)
    
    # Legal and regulatory
    legal_implications = Column(Text)
    regulatory_reporting_required = Column(Boolean, default=False)
    law_enforcement_involvement = Column(Boolean, default=False)
    external_counsel_engaged = Column(Boolean, default=False)
    
    # Recommendations
    immediate_actions = Column(JSONB)
    remediation_recommendations = Column(JSONB)
    preventive_measures = Column(JSONB)
    process_improvements = Column(JSONB)
    
    # Documentation
    investigation_report_path = Column(String(500))
    supporting_documents = Column(JSONB)
    communication_log = Column(JSONB)
    
    # Closure and follow-up
    resolution_summary = Column(Text)
    lessons_learned = Column(JSONB)
    follow_up_actions = Column(JSONB)
    case_closed_by = Column(UUID(as_uuid=True))
    case_closed_at = Column(DateTime(timezone=True))
    
    # Quality and review
    peer_review_required = Column(Boolean, default=True)
    reviewed_by = Column(UUID(as_uuid=True))
    review_date = Column(DateTime(timezone=True))
    quality_score = Column(Float, default=0.0)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), default=func.now())
    updated_at = Column(DateTime(timezone=True), default=func.now(), onupdate=func.now())
    
    # Indexes
    __table_args__ = (
        Index('idx_forensic_investigation_status', 'status', 'priority'),
        Index('idx_forensic_investigation_lead', 'lead_investigator', 'status'),
        Index('idx_forensic_investigation_type', 'investigation_type', 'severity'),
    )

class AuditAlert(Base):
    """
Audit-based alerts and notifications"""
    __tablename__ = 'audit_alerts'
    
    # Primary identification
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    alert_id = Column(String(100), unique=True, nullable=False)
    
    # Alert details
    alert_type = Column(String(50), nullable=False)  # anomaly, security, compliance, performance
    severity = Column(String(20), nullable=False)
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=False)
    
    # Trigger information
    triggered_by_event_id = Column(String(100))
    trigger_conditions = Column(JSONB)
    trigger_threshold = Column(Float)
    actual_value = Column(Float)
    
    # Context
    affected_user_id = Column(UUID(as_uuid=True), index=True)
    affected_system = Column(String(100))
    event_pattern = Column(JSONB)
    
    # Risk assessment
    risk_score = Column(Float, default=0.0)
    potential_impact = Column(String(20))  # low, medium, high, critical
    confidence_level = Column(Float, default=0.0)
    
    # Response information
    recommended_actions = Column(JSONB)
    automated_response_available = Column(Boolean, default=False)
    escalation_rules = Column(JSONB)
    
    # Status and handling
    status = Column(String(20), default='active')  # active, investigating, resolved, false_positive
    assigned_to = Column(UUID(as_uuid=True))
    acknowledged_at = Column(DateTime(timezone=True))
    resolved_at = Column(DateTime(timezone=True))
    resolution_notes = Column(Text)
    
    # Notification tracking
    notification_sent = Column(Boolean, default=False)
    notification_channels = Column(ARRAY(String))
    escalated = Column(Boolean, default=False)
    escalation_level = Column(Integer, default=0)
    
    # Timestamps
    triggered_at = Column(DateTime(timezone=True), default=func.now())
    expires_at = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), default=func.now())
    updated_at = Column(DateTime(timezone=True), default=func.now(), onupdate=func.now())
    
    # Indexes
    __table_args__ = (
        Index('idx_audit_alert_status_severity', 'status', 'severity'),
        Index('idx_audit_alert_user_type', 'affected_user_id', 'alert_type'),
        Index('idx_audit_alert_triggered', 'triggered_at', 'status'),
    )

# Export all models for easy import
__all__ = [
    'AuditEventType',
    'AuditEventSeverity',
    'AuditStatus',
    'AuditEventSource',
    'AuditEvent',
    'AuditSummary',
    'DataRetentionPolicy',
    'AuditQuery',
    'AuditMetrics',
    'ForensicInvestigation',
    'AuditAlert'
]
