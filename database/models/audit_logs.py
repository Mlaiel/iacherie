"""Audit Logs Database Model

Enterprise-grade SQLAlchemy model for comprehensive audit logging, compliance tracking,
and security monitoring across the entire platform.

Author: Fahed Mlaiel <mlaiel@live.de>
Project: IA Influencer Agent + Content Protection Platform
Copyright: All rights reserved. Unauthorized use, modification, or distribution prohibited.

🚨 INTELLECTUAL PROPERTY WARNING: This code, concept, and architecture are 
the exclusive intellectual property of Fahed Mlaiel (mlaiel@live.de). 
Any use, copying, distribution, or exploitation without explicit written 
authorization is STRICTLY PROHIBITED and will be prosecuted.

Expert Project Team - Fahed Mlaiel:
- Lead AI Developer & Software Architect
- Senior Backend Engineer (Python/FastAPI/Django)  
- Machine Learning Engineer (TensorFlow/PyTorch/Hugging Face)
- Database Administrator & Data Engineer (PostgreSQL/Redis/MongoDB)
- Backend Security Specialist
- Microservices Architect
- Audio Processing Engineer
- DevOps Engineer
- AI Prompt Engineer
"""

from sqlalchemy import Column, String, Text, DateTime, Float, Integer, Boolean, JSON, ForeignKey, Index, Enum as SQLEnum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID, INET, ARRAY
from datetime import datetime, timezone
from enum import Enum
import uuid
from typing import Dict, Any, List, Optional

Base = declarative_base()


class ActionType(Enum):
    """
Audit action types"""

    CREATE = "create"
    READ = "read"
    UPDATE = "update"
    DELETE = "delete"
    LOGIN = "login"
    LOGOUT = "logout"
    UPLOAD = "upload"
    DOWNLOAD = "download"
    PUBLISH = "publish"
    UNPUBLISH = "unpublish"
    SHARE = "share"
    COLLABORATE = "collaborate"
    MONETIZE = "monetize"
    PROTECT = "protect"
    FINGERPRINT = "fingerprint"
    DETECT_VIOLATION = "detect_violation"
    SEND_DMCA = "send_dmca"
    PROCESS_PAYMENT = "process_payment"
    SYNC_PLATFORM = "sync_platform"
    APPROVE = "approve"
    REJECT = "reject"
    SUSPEND = "suspend"
    RESTORE = "restore"
    EXPORT = "export"
    IMPORT = "import"
    BACKUP = "backup"
    RESTORE_BACKUP = "restore_backup"
    CONFIGURE = "configure"
    INTEGRATE = "integrate"
    AUTHENTICATE = "authenticate"
    AUTHORIZE = "authorize"
    REVOKE = "revoke"
    ENCRYPT = "encrypt"
    DECRYPT = "decrypt"
    VALIDATE = "validate"
    VERIFY = "verify"
    ANALYZE = "analyze"
    OPTIMIZE = "optimize"
    MIGRATE = "migrate"
    ALERT = "alert"
    NOTIFY = "notify"
    ESCALATE = "escalate"
    RESOLVE = "resolve"
    ARCHIVE = "archive"
    PURGE = "purge"


class EntityType(Enum):
    """Entity types being audited"""

    USER = "user"
    CONTENT = "content"
    FINGERPRINT = "fingerprint"
    ALERT = "alert"
    REVENUE = "revenue"
    LICENSE = "license"
    PLATFORM_INTEGRATION = "platform_integration"
    COLLABORATION = "collaboration"
    PAYMENT = "payment"
    METADATA = "metadata"
    MONETIZATION_RULE = "monetization_rule"
    SYSTEM = "system"
    API = "api"
    DATABASE = "database"
    FILE = "file"
    CONFIGURATION = "configuration"
    WORKFLOW = "workflow"
    NOTIFICATION = "notification"
    REPORT = "report"
    BACKUP = "backup"
    SECURITY = "security"
    COMPLIANCE = "compliance"


class Severity(Enum):
    """Log severity levels"""

    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"
    DEBUG = "debug"


class Status(Enum):
    """Action status"""

    SUCCESS = "success"
    FAILURE = "failure"
    PARTIAL = "partial"
    PENDING = "pending"
    CANCELLED = "cancelled"
    TIMEOUT = "timeout"
    ERROR = "error"
    WARNING = "warning"


class Source(Enum):
    """Audit log sources"""

    WEB_APP = "web_app"
    MOBILE_APP = "mobile_app"
    API = "api"
    SYSTEM = "system"
    BACKGROUND_TASK = "background_task"
    WEBHOOK = "webhook"
    CRON_JOB = "cron_job"
    MIGRATION = "migration"
    ADMIN_PANEL = "admin_panel"
    CLI = "cli"
    THIRD_PARTY = "third_party"
    AUTOMATION = "automation"
    AI_AGENT = "ai_agent"
    SECURITY_SCANNER = "security_scanner"
    MONITORING = "monitoring"


class AuditLog(Base):
    """
    Enterprise Audit Log Model
    
    Comprehensive audit logging system for security, compliance, and operational
    monitoring with advanced analytics and forensic capabilities.
    """
    __tablename__ = "audit_logs"
    
    # Primary identification
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Foreign key relationships (nullable for system events)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=True, index=True)
    content_fingerprint_id = Column(UUID(as_uuid=True), ForeignKey('content_fingerprints.id'), nullable=True, index=True)
    protection_alert_id = Column(UUID(as_uuid=True), ForeignKey('protection_alerts.id'), nullable=True, index=True)
    revenue_tracking_id = Column(UUID(as_uuid=True), ForeignKey('revenue_tracking.id'), nullable=True, index=True)
    licensing_agreement_id = Column(UUID(as_uuid=True), ForeignKey('licensing_agreements.id'), nullable=True, index=True)
    platform_integration_id = Column(UUID(as_uuid=True), ForeignKey('platform_integrations.id'), nullable=True, index=True)
    
    # Action classification
    action_type = Column(SQLEnum(ActionType), nullable=False, index=True)
    entity_type = Column(SQLEnum(EntityType), nullable=False, index=True)
    entity_id = Column(String(255), nullable=True, index=True)
    entity_name = Column(String(500), nullable=True)
    
    # Event details
    event_name = Column(String(255), nullable=False)
    event_description = Column(Text, nullable=True)
    event_category = Column(String(100), nullable=True)
    event_subcategory = Column(String(100), nullable=True)
    
    # Status and severity
    status = Column(SQLEnum(Status), nullable=False, index=True)
    severity = Column(SQLEnum(Severity), default=Severity.INFO, index=True)
    risk_level = Column(String(50), default="low")
    
    # Source and context
    source = Column(SQLEnum(Source), nullable=False, index=True)
    source_module = Column(String(255), nullable=True)
    source_function = Column(String(255), nullable=True)
    source_version = Column(String(50), nullable=True)
    
    # User and session information
    username = Column(String(255), nullable=True)
    user_email = Column(String(255), nullable=True)
    session_id = Column(String(255), nullable=True, index=True)
    request_id = Column(String(255), nullable=True, index=True)
    correlation_id = Column(String(255), nullable=True, index=True)
    
    # Network and device information
    ip_address = Column(INET, nullable=True, index=True)
    user_agent = Column(Text, nullable=True)
    device_info = Column(JSON, nullable=True)
    browser_info = Column(JSON, nullable=True)
    geolocation = Column(JSON, nullable=True)
    
    # API and HTTP details
    http_method = Column(String(10), nullable=True)
    endpoint = Column(String(500), nullable=True)
    api_version = Column(String(20), nullable=True)
    response_code = Column(Integer, nullable=True)
    response_time = Column(Float, nullable=True)  # Response time in seconds
    
    # Data changes
    before_data = Column(JSON, nullable=True)  # Data before change
    after_data = Column(JSON, nullable=True)   # Data after change
    changed_fields = Column(ARRAY(String), nullable=True)
    change_summary = Column(Text, nullable=True)
    
    # Additional context
    metadata = Column(JSON, nullable=True)
    tags = Column(ARRAY(String), nullable=True, index=True)
    labels = Column(JSON, nullable=True)
    custom_fields = Column(JSON, nullable=True)
    
    # Error and exception details
    error_code = Column(String(100), nullable=True)
    error_message = Column(Text, nullable=True)
    error_details = Column(JSON, nullable=True)
    stack_trace = Column(Text, nullable=True)
    exception_type = Column(String(255), nullable=True)
    
    # Performance metrics
    execution_time = Column(Float, nullable=True)  # Execution time in seconds
    memory_usage = Column(Integer, nullable=True)  # Memory usage in bytes
    cpu_usage = Column(Float, nullable=True)      # CPU usage percentage
    disk_usage = Column(Integer, nullable=True)   # Disk usage in bytes
    network_usage = Column(Integer, nullable=True) # Network usage in bytes
    
    # Business context
    business_impact = Column(String(100), nullable=True)
    financial_impact = Column(Float, nullable=True)
    compliance_relevance = Column(ARRAY(String), nullable=True)
    regulatory_impact = Column(JSON, nullable=True)
    
    # Security context
    security_event = Column(Boolean, default=False, index=True)
    threat_level = Column(String(50), nullable=True)
    security_classification = Column(String(50), nullable=True)
    suspicious_activity = Column(Boolean, default=False)
    fraud_indicator = Column(Float, default=0.0)
    
    # Content protection context
    copyright_event = Column(Boolean, default=False)
    violation_detected = Column(Boolean, default=False)
    protection_action_taken = Column(String(255), nullable=True)
    content_matches = Column(JSON, nullable=True)
    platform_response = Column(JSON, nullable=True)
    
    # Monetization context
    revenue_event = Column(Boolean, default=False)
    revenue_amount = Column(Float, nullable=True)
    currency = Column(String(3), nullable=True)
    payment_reference = Column(String(255), nullable=True)
    transaction_id = Column(String(255), nullable=True)
    
    # Automation and AI context
    automated_action = Column(Boolean, default=False)
    ai_decision = Column(Boolean, default=False)
    ai_confidence = Column(Float, nullable=True)
    ml_model_version = Column(String(50), nullable=True)
    automation_rule = Column(String(255), nullable=True)
    
    # Workflow and approval context
    workflow_stage = Column(String(100), nullable=True)
    approval_required = Column(Boolean, default=False)
    approved_by = Column(String(255), nullable=True)
    approval_timestamp = Column(DateTime(timezone=True), nullable=True)
    workflow_metadata = Column(JSON, nullable=True)
    
    # Compliance and audit trails
    compliance_event = Column(Boolean, default=False)
    retention_period = Column(Integer, nullable=True)  # Retention in days
    immutable = Column(Boolean, default=True)
    archived = Column(Boolean, default=False)
    archive_location = Column(String(500), nullable=True)
    
    # Alert and notification context
    alert_triggered = Column(Boolean, default=False)
    notification_sent = Column(Boolean, default=False)
    escalation_level = Column(Integer, default=0)
    recipients = Column(ARRAY(String), nullable=True)
    notification_methods = Column(ARRAY(String), nullable=True)
    
    # Integration and synchronization
    external_system = Column(String(255), nullable=True)
    external_reference = Column(String(255), nullable=True)
    sync_status = Column(String(50), nullable=True)
    sync_timestamp = Column(DateTime(timezone=True), nullable=True)
    
    # Timestamps
    timestamp = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False, index=True)
    event_timestamp = Column(DateTime(timezone=True), nullable=True)  # Actual event time (may differ from log time)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    expires_at = Column(DateTime(timezone=True), nullable=True)
    
    # Status flags
    is_processed = Column(Boolean, default=False)
    is_analyzed = Column(Boolean, default=False)
    requires_review = Column(Boolean, default=False)
    is_sensitive = Column(Boolean, default=False)
    is_anomaly = Column(Boolean, default=False)
    
    # Relationships
    content_fingerprint = relationship("ContentFingerprint", back_populates="audit_logs")
    protection_alert = relationship("ProtectionAlert", back_populates="audit_logs")
    revenue_tracking = relationship("RevenueTracking", back_populates="audit_logs")
    licensing_agreement = relationship("LicensingAgreement", back_populates="audit_logs")
    platform_integration = relationship("PlatformIntegration", back_populates="audit_logs")
    
    # Advanced indexes for performance and compliance
    __table_args__ = (
        Index('idx_audit_timestamp_action', 'timestamp', 'action_type'),
        Index('idx_audit_user_entity', 'user_id', 'entity_type'),
        Index('idx_audit_status_severity', 'status', 'severity'),
        Index('idx_audit_security_events', 'security_event', 'threat_level'),
        Index('idx_audit_compliance_events', 'compliance_event', 'regulatory_impact'),
        Index('idx_audit_source_module', 'source', 'source_module'),
        Index('idx_audit_ip_session', 'ip_address', 'session_id'),
        Index('idx_audit_entity_id', 'entity_type', 'entity_id'),
        Index('idx_audit_correlation', 'correlation_id', 'request_id'),
        Index('idx_audit_tags', 'tags'),
        Index('idx_audit_copyright_events', 'copyright_event', 'violation_detected'),
        Index('idx_audit_revenue_events', 'revenue_event', 'revenue_amount'),
        Index('idx_audit_automated_actions', 'automated_action', 'ai_decision'),
        Index('idx_audit_alerts', 'alert_triggered', 'escalation_level'),
        Index('idx_audit_retention', 'expires_at', 'archived'),
        Index('idx_audit_anomalies', 'is_anomaly', 'fraud_indicator'),
        Index('idx_audit_performance', 'execution_time', 'response_time'),
    )
    
    def __repr__(self):
        return f"<AuditLog(id={self.id}, action={self.action_type.value}, entity={self.entity_type.value}, status={self.status.value}, timestamp={self.timestamp})>"
    
    def to_dict(self, include_sensitive: bool = False, include_performance: bool = False) -> Dict[str, Any]:
        """Convert model to dictionary for API responses"""
        base_dict = {
            "id": str(self.id),
            "user_id": str(self.user_id) if self.user_id else None,
            "content_fingerprint_id": str(self.content_fingerprint_id) if self.content_fingerprint_id else None,
            "protection_alert_id": str(self.protection_alert_id) if self.protection_alert_id else None,
            "revenue_tracking_id": str(self.revenue_tracking_id) if self.revenue_tracking_id else None,
            "licensing_agreement_id": str(self.licensing_agreement_id) if self.licensing_agreement_id else None,
            "platform_integration_id": str(self.platform_integration_id) if self.platform_integration_id else None,
            "action_type": self.action_type.value if self.action_type else None,
            "entity_type": self.entity_type.value if self.entity_type else None,
            "entity_id": self.entity_id,
            "entity_name": self.entity_name,
            "event_name": self.event_name,
            "event_description": self.event_description,
            "event_category": self.event_category,
            "event_subcategory": self.event_subcategory,
            "status": self.status.value if self.status else None,
            "severity": self.severity.value if self.severity else None,
            "risk_level": self.risk_level,
            "source": self.source.value if self.source else None,
            "source_module": self.source_module,
            "source_function": self.source_function,
            "source_version": self.source_version,
            "username": self.username,
            "user_email": self.user_email,
            "session_id": self.session_id,
            "request_id": self.request_id,
            "correlation_id": self.correlation_id,
            "ip_address": str(self.ip_address) if self.ip_address else None,
            "user_agent": self.user_agent,
            "device_info": self.device_info,
            "browser_info": self.browser_info,
            "geolocation": self.geolocation,
            "http_method": self.http_method,
            "endpoint": self.endpoint,
            "api_version": self.api_version,
            "response_code": self.response_code,
            "response_time": self.response_time,
            "changed_fields": self.changed_fields,
            "change_summary": self.change_summary,
            "metadata": self.metadata,
            "tags": self.tags,
            "labels": self.labels,
            "custom_fields": self.custom_fields,
            "error_code": self.error_code,
            "error_message": self.error_message,
            "business_impact": self.business_impact,
            "financial_impact": self.financial_impact,
            "compliance_relevance": self.compliance_relevance,
            "security_event": self.security_event,
            "threat_level": self.threat_level,
            "suspicious_activity": self.suspicious_activity,
            "fraud_indicator": self.fraud_indicator,
            "copyright_event": self.copyright_event,
            "violation_detected": self.violation_detected,
            "protection_action_taken": self.protection_action_taken,
            "revenue_event": self.revenue_event,
            "revenue_amount": self.revenue_amount,
            "currency": self.currency,
            "automated_action": self.automated_action,
            "ai_decision": self.ai_decision,
            "ai_confidence": self.ai_confidence,
            "ml_model_version": self.ml_model_version,
            "workflow_stage": self.workflow_stage,
            "approval_required": self.approval_required,
            "approved_by": self.approved_by,
            "approval_timestamp": self.approval_timestamp.isoformat() if self.approval_timestamp else None,
            "compliance_event": self.compliance_event,
            "alert_triggered": self.alert_triggered,
            "notification_sent": self.notification_sent,
            "escalation_level": self.escalation_level,
            "external_system": self.external_system,
            "external_reference": self.external_reference,
            "sync_status": self.sync_status,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
            "event_timestamp": self.event_timestamp.isoformat() if self.event_timestamp else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "expires_at": self.expires_at.isoformat() if self.expires_at else None,
            "is_processed": self.is_processed,
            "is_analyzed": self.is_analyzed,
            "requires_review": self.requires_review,
            "is_sensitive": self.is_sensitive,
            "is_anomaly": self.is_anomaly
        }
        
        if include_sensitive:
            base_dict.update({
                "before_data": self.before_data,
                "after_data": self.after_data,
                "error_details": self.error_details,
                "stack_trace": self.stack_trace,
                "payment_reference": self.payment_reference,
                "transaction_id": self.transaction_id,
                "recipients": self.recipients,
                "notification_methods": self.notification_methods
            })
        
        if include_performance:
            base_dict.update({
                "execution_time": self.execution_time,
                "memory_usage": self.memory_usage,
                "cpu_usage": self.cpu_usage,
                "disk_usage": self.disk_usage,
                "network_usage": self.network_usage
            })
        
        return base_dict
    
    def is_security_relevant(self) -> bool:
        """Check if this log entry is security-relevant"""
        return (
            self.security_event or
            self.suspicious_activity or
            self.fraud_indicator > 0.5 or
            self.threat_level in ["high", "critical"] or
            self.action_type in [ActionType.LOGIN, ActionType.AUTHENTICATE, ActionType.AUTHORIZE, ActionType.REVOKE]
        )
    
    def is_compliance_relevant(self) -> bool:
        """Check if this log entry is compliance-relevant"""
        return (
            self.compliance_event or
            bool(self.compliance_relevance) or
            bool(self.regulatory_impact) or
            self.action_type in [ActionType.DELETE, ActionType.EXPORT, ActionType.PURGE] or
            self.entity_type in [EntityType.USER, EntityType.PAYMENT, EntityType.LICENSE]
        )
    
    def get_risk_score(self) -> float:
        """
Calculate overall risk score for this event"""
        score = 0.0
        
        # Severity weight
        severity_weights = {
            Severity.CRITICAL: 10.0,
            Severity.HIGH: 7.5,
            Severity.MEDIUM: 5.0,
            Severity.LOW: 2.5,
            Severity.INFO: 1.0,
            Severity.DEBUG: 0.5
        }
        score += severity_weights.get(self.severity, 1.0)
        
        # Status weight
        if self.status == Status.FAILURE:
            score += 5.0
        elif self.status == Status.ERROR:
            score += 7.5
        
        # Security factors
        if self.security_event:
            score += 5.0
        if self.suspicious_activity:
            score += 3.0
        score += (self.fraud_indicator or 0.0) * 5.0
        
        # Business impact
        if self.financial_impact and self.financial_impact > 1000:
            score += min(self.financial_impact / 1000.0, 10.0)
        
        return min(score, 100.0)  # Cap at 100
    
    def should_alert(self) -> bool:
        """
Determine if this event should trigger an alert"""
        return (
            self.get_risk_score() > 15.0 or
            self.severity in [Severity.CRITICAL, Severity.HIGH] or
            self.security_event or
            self.violation_detected or
            self.status == Status.FAILURE and self.action_type in [
                ActionType.PROCESS_PAYMENT, ActionType.PROTECT, ActionType.AUTHENTICATE
            ]
        )
    
    @classmethod
    def create_log(cls, log_data: Dict[str, Any], user_id: str = None) -> 'AuditLog':
        """
Create AuditLog from event data"""
        return cls(
            user_id=user_id,
            action_type=ActionType(log_data.get('action_type', 'read')),
            entity_type=EntityType(log_data.get('entity_type', 'system')),
            entity_id=log_data.get('entity_id'),
            entity_name=log_data.get('entity_name'),
            event_name=log_data.get('event_name'),
            event_description=log_data.get('event_description'),
            status=Status(log_data.get('status', 'success')),
            severity=Severity(log_data.get('severity', 'info')),
            source=Source(log_data.get('source', 'system')),
            source_module=log_data.get('source_module'),
            ip_address=log_data.get('ip_address'),
            user_agent=log_data.get('user_agent'),
            session_id=log_data.get('session_id'),
            request_id=log_data.get('request_id'),
            correlation_id=log_data.get('correlation_id'),
            http_method=log_data.get('http_method'),
            endpoint=log_data.get('endpoint'),
            response_code=log_data.get('response_code'),
            response_time=log_data.get('response_time'),
            before_data=log_data.get('before_data'),
            after_data=log_data.get('after_data'),
            changed_fields=log_data.get('changed_fields'),
            metadata=log_data.get('metadata', {}),
            tags=log_data.get('tags', []),
            error_code=log_data.get('error_code'),
            error_message=log_data.get('error_message'),
            security_event=log_data.get('security_event', False),
            copyright_event=log_data.get('copyright_event', False),
            revenue_event=log_data.get('revenue_event', False),
            automated_action=log_data.get('automated_action', False),
            ai_decision=log_data.get('ai_decision', False),
            compliance_event=log_data.get('compliance_event', False),
            timestamp=log_data.get('timestamp', datetime.now(timezone.utc)),
            event_timestamp=log_data.get('event_timestamp')
        )
