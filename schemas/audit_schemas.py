"""IA Influencer Agent Platform - Audit Trail and History Schemas
Comprehensive audit trail and history tracking for all platform operations.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

This module provides audit trail schemas for:
- User action tracking
- Data modification history
- System event logging
- Compliance and security auditing
- Change management and rollback
"""

from typing import Optional, List, Dict, Any, Union
from enum import Enum
from datetime import datetime
from pydantic import BaseModel, Field, validator
from .base import BaseSchema, UUIDSchema, TimestampSchema
from .primitive_types import UsernameType


class AuditAction(str, Enum):
    """Types of audit actions."""
    CREATE = "create"
    UPDATE = "update"
    DELETE = "delete"
    VIEW = "view"
    DOWNLOAD = "download"
    UPLOAD = "upload"
    LOGIN = "login"
    LOGOUT = "logout"
    APPROVE = "approve"
    REJECT = "reject"
    SHARE = "share"
    PUBLISH = "publish"
    UNPUBLISH = "unpublish"
    ARCHIVE = "archive"
    RESTORE = "restore"
    EXPORT = "export"
    IMPORT = "import"
    CONFIGURE = "configure"
    AUTHENTICATE = "authenticate"
    AUTHORIZE = "authorize"
    ENCRYPT = "encrypt"
    DECRYPT = "decrypt"


class AuditCategory(str, Enum):
    """Audit category classifications."""
    USER_MANAGEMENT = "user_management"
    CONTENT_MANAGEMENT = "content_management"
    SECURITY = "security"
    SYSTEM = "system"
    BUSINESS = "business"
    COMPLIANCE = "compliance"
    PERFORMANCE = "performance"
    INTEGRATION = "integration"
    MONETIZATION = "monetization"
    COLLABORATION = "collaboration"


class AuditSeverity(str, Enum):
    """Audit event severity levels."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"


class AuditStatus(str, Enum):
    """Audit record status."""
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    IN_PROGRESS = "in_progress"


class ChangeType(str, Enum):
    """Types of data changes."""
    FIELD_UPDATE = "field_update"
    RECORD_INSERT = "record_insert"
    RECORD_DELETE = "record_delete"
    BULK_OPERATION = "bulk_operation"
    SCHEMA_CHANGE = "schema_change"
    MIGRATION = "migration"
    ROLLBACK = "rollback"


class AuditEvent(UUIDSchema, TimestampSchema):
    """Core audit event record."""
    
    action: AuditAction = Field(..., description="Action performed")
    category: AuditCategory = Field(..., description="Audit category")
    severity: AuditSeverity = Field(AuditSeverity.INFO, description="Event severity")
    status: AuditStatus = Field(AuditStatus.COMPLETED, description="Audit status")
    
    # Actor information
    user_id: Optional[str] = Field(None, description="User who performed the action")
    username: Optional[UsernameType] = Field(None, description="Username")
    session_id: Optional[str] = Field(None, description="Session identifier")
    api_key_id: Optional[str] = Field(None, description="API key used")
    
    # Target information
    resource_type: str = Field(..., description="Type of resource affected")
    resource_id: Optional[str] = Field(None, description="ID of affected resource")
    resource_name: Optional[str] = Field(None, description="Name of affected resource")
    
    # Event details
    description: str = Field(..., description="Human-readable description")
    details: Dict[str, Any] = Field(default={}, description="Additional event details")
    
    # Context information
    ip_address: Optional[str] = Field(None, description="Source IP address")
    user_agent: Optional[str] = Field(None, description="User agent string")
    request_id: Optional[str] = Field(None, description="Request identifier")
    correlation_id: Optional[str] = Field(None, description="Correlation identifier")
    
    # System information
    system_version: Optional[str] = Field(None, description="System version")
    environment: Optional[str] = Field(None, description="Environment (dev/staging/prod)")
    hostname: Optional[str] = Field(None, description="Server hostname")
    
    # Security context
    permissions: List[str] = Field(default=[], description="Permissions used")
    security_context: Dict[str, Any] = Field(default={}, description="Security context data")
    
    # Compliance tags
    compliance_tags: List[str] = Field(default=[], description="Compliance requirement tags")
    retention_period: Optional[int] = Field(None, description="Data retention period in days")
    
    @validator('ip_address')
    def validate_ip_address(cls, v) -> None:
        """Validate IP address format."""
        if v is not None:
            import re
            ipv4_pattern = r'^(\d{1,3}\.){3}\d{1,3}$'
            ipv6_pattern = r'^([0-9a-fA-F]{1,4}:){7}[0-9a-fA-F]{1,4}$'
            if not re.match(ipv4_pattern, v) and not re.match(ipv6_pattern, v):
                raise ValueError('Invalid IP address format')
        return v


class DataChange(BaseSchema):
    """Individual data change record."""
    
    field_name: str = Field(..., description="Name of changed field")
    field_type: str = Field(..., description="Type of field")
    old_value: Any = Field(None, description="Previous value")
    new_value: Any = Field(..., description="New value")
    change_type: ChangeType = Field(..., description="Type of change")
    validation_status: str = Field("valid", description="Validation status")
    encryption_applied: bool = Field(False, description="Whether encryption was applied")


class AuditChangeSet(UUIDSchema, TimestampSchema):
    """Set of related data changes."""
    
    audit_event_id: str = Field(..., description="Related audit event ID")
    entity_type: str = Field(..., description="Type of entity changed")
    entity_id: str = Field(..., description="ID of changed entity")
    entity_version: Optional[str] = Field(None, description="Entity version")
    
    changes: List[DataChange] = Field(..., description="List of changes")
    change_summary: str = Field(..., description="Summary of changes")
    rollback_data: Dict[str, Any] = Field(default={}, description="Data needed for rollback")
    
    # Change metadata
    change_reason: Optional[str] = Field(None, description="Reason for change")
    change_ticket: Optional[str] = Field(None, description="Related ticket/issue")
    approval_required: bool = Field(False, description="Whether approval was required")
    approved_by: Optional[str] = Field(None, description="Who approved the change")
    approval_timestamp: Optional[datetime] = Field(None, description="When change was approved")


class ComplianceAudit(UUIDSchema, TimestampSchema):
    """Compliance-specific audit record."""
    
    regulation: str = Field(..., description="Applicable regulation (GDPR, CCPA, etc.)")
    requirement: str = Field(..., description="Specific requirement")
    status: str = Field(..., description="Compliance status")
    
    # Data subject information
    data_subject_id: Optional[str] = Field(None, description="Data subject identifier")
    data_categories: List[str] = Field(default=[], description="Categories of personal data")
    processing_purpose: str = Field(..., description="Purpose of data processing")
    legal_basis: str = Field(..., description="Legal basis for processing")
    
    # Consent management
    consent_given: Optional[bool] = Field(None, description="Whether consent was given")
    consent_timestamp: Optional[datetime] = Field(None, description="When consent was given")
    consent_withdrawn: Optional[bool] = Field(None, description="Whether consent was withdrawn")
    withdrawal_timestamp: Optional[datetime] = Field(None, description="When consent was withdrawn")
    
    # Data lifecycle
    data_retention_period: Optional[int] = Field(None, description="Data retention period")
    deletion_scheduled: Optional[datetime] = Field(None, description="Scheduled deletion date")
    data_minimization_applied: bool = Field(False, description="Data minimization applied")
    
    # Cross-border transfers
    transfer_country: Optional[str] = Field(None, description="Data transfer destination")
    adequacy_decision: Optional[bool] = Field(None, description="Adequacy decision exists")
    safeguards_applied: List[str] = Field(default=[], description="Applied safeguards")


class SecurityAudit(UUIDSchema, TimestampSchema):
    """Security-specific audit record."""
    
    security_event_type: str = Field(..., description="Type of security event")
    threat_level: AuditSeverity = Field(..., description="Threat severity level")
    
    # Authentication details
    authentication_method: Optional[str] = Field(None, description="Authentication method used")
    mfa_used: bool = Field(False, description="Multi-factor authentication used")
    authentication_failures: int = Field(0, description="Number of auth failures")
    
    # Authorization details
    permissions_requested: List[str] = Field(default=[], description="Requested permissions")
    permissions_granted: List[str] = Field(default=[], description="Granted permissions")
    access_denied_reason: Optional[str] = Field(None, description="Reason for access denial")
    
    # Security context
    encryption_level: Optional[str] = Field(None, description="Encryption level used")
    security_protocol: Optional[str] = Field(None, description="Security protocol")
    vulnerability_detected: bool = Field(False, description="Vulnerability detected")
    vulnerability_details: Dict[str, Any] = Field(default={}, description="Vulnerability details")
    
    # Response information
    incident_created: bool = Field(False, description="Security incident created")
    incident_id: Optional[str] = Field(None, description="Security incident ID")
    response_actions: List[str] = Field(default=[], description="Response actions taken")


class PerformanceAudit(UUIDSchema, TimestampSchema):
    """Performance-related audit record."""
    
    operation: str = Field(..., description="Operation being measured")
    duration_ms: float = Field(..., description="Operation duration in milliseconds")
    
    # Resource usage
    cpu_usage: Optional[float] = Field(None, description="CPU usage percentage")
    memory_usage: Optional[float] = Field(None, description="Memory usage in MB")
    disk_io: Optional[float] = Field(None, description="Disk I/O operations")
    network_io: Optional[float] = Field(None, description="Network I/O in bytes")
    
    # Performance metrics
    throughput: Optional[float] = Field(None, description="Operations per second")
    latency_p50: Optional[float] = Field(None, description="50th percentile latency")
    latency_p95: Optional[float] = Field(None, description="95th percentile latency")
    latency_p99: Optional[float] = Field(None, description="99th percentile latency")
    
    # Quality metrics
    error_rate: Optional[float] = Field(None, description="Error rate percentage")
    success_rate: Optional[float] = Field(None, description="Success rate percentage")
    
    # Thresholds
    performance_threshold: Optional[float] = Field(None, description="Performance threshold")
    threshold_exceeded: bool = Field(False, description="Whether threshold was exceeded")
    
    # Context
    concurrent_users: Optional[int] = Field(None, description="Number of concurrent users")
    data_volume: Optional[float] = Field(None, description="Data volume processed")


class AuditQuery(BaseSchema):
    """Audit log query parameters."""
    
    # Time range
    start_date: Optional[datetime] = Field(None, description="Query start date")
    end_date: Optional[datetime] = Field(None, description="Query end date")
    
    # Filters
    actions: List[AuditAction] = Field(default=[], description="Filter by actions")
    categories: List[AuditCategory] = Field(default=[], description="Filter by categories")
    severities: List[AuditSeverity] = Field(default=[], description="Filter by severities")
    users: List[str] = Field(default=[], description="Filter by user IDs")
    resource_types: List[str] = Field(default=[], description="Filter by resource types")
    resource_ids: List[str] = Field(default=[], description="Filter by resource IDs")
    
    # Search
    search_text: Optional[str] = Field(None, description="Text search in descriptions")
    
    # Pagination
    page: int = Field(1, ge=1, description="Page number")
    page_size: int = Field(50, ge=1, le=1000, description="Items per page")
    
    # Sorting
    sort_by: str = Field("created_at", description="Sort field")
    sort_direction: str = Field("desc", pattern="^(asc|desc)$", description="Sort direction")


class AuditStatistics(BaseSchema):
    """Audit log statistics."""
    
    total_events: int = Field(..., description="Total number of audit events")
    events_by_action: Dict[str, int] = Field(..., description="Events grouped by action")
    events_by_category: Dict[str, int] = Field(..., description="Events grouped by category")
    events_by_severity: Dict[str, int] = Field(..., description="Events grouped by severity")
    events_by_user: Dict[str, int] = Field(..., description="Events grouped by user")
    
    # Time-based statistics
    events_by_hour: Dict[str, int] = Field(default={}, description="Events by hour of day")
    events_by_day: Dict[str, int] = Field(default={}, description="Events by day")
    events_by_month: Dict[str, int] = Field(default={}, description="Events by month")
    
    # Performance statistics
    average_response_time: Optional[float] = Field(None, description="Average response time")
    error_rate: Optional[float] = Field(None, description="Overall error rate")
    
    # Security statistics
    failed_logins: int = Field(0, description="Number of failed login attempts")
    security_incidents: int = Field(0, description="Number of security incidents")
    
    # Compliance statistics
    gdpr_requests: int = Field(0, description="Number of GDPR requests")
    data_exports: int = Field(0, description="Number of data exports")
    data_deletions: int = Field(0, description="Number of data deletions")


class AuditRetentionPolicy(UUIDSchema, TimestampSchema):
    """Audit log retention policy."""
    
    name: str = Field(..., description="Policy name")
    description: str = Field(..., description="Policy description")
    
    # Retention rules
    default_retention_days: int = Field(2555, description="Default retention period (7 years)")
    category_retention: Dict[str, int] = Field(default={}, description="Retention by category")
    severity_retention: Dict[str, int] = Field(default={}, description="Retention by severity")
    
    # Compliance requirements
    compliance_requirements: List[str] = Field(default=[], description="Applicable compliance requirements")
    legal_hold_enabled: bool = Field(False, description="Legal hold enabled")
    
    # Archival settings
    archive_after_days: Optional[int] = Field(None, description="Archive after N days")
    archive_location: Optional[str] = Field(None, description="Archive storage location")
    compression_enabled: bool = Field(True, description="Enable compression")
    encryption_required: bool = Field(True, description="Encryption required")
    
    # Deletion settings
    auto_deletion_enabled: bool = Field(True, description="Enable automatic deletion")
    deletion_batch_size: int = Field(1000, description="Deletion batch size")
    deletion_schedule: str = Field("weekly", description="Deletion schedule")


class AuditConfig(BaseSchema):
    """Audit system configuration."""
    
    # Logging settings
    logging_enabled: bool = Field(True, description="Enable audit logging")
    real_time_logging: bool = Field(True, description="Enable real-time logging")
    batch_size: int = Field(100, description="Batch size for bulk operations")
    buffer_size: int = Field(1000, description="Log buffer size")
    
    # Storage settings
    storage_backend: str = Field("database", description="Storage backend type")
    storage_config: Dict[str, Any] = Field(default={}, description="Storage configuration")
    backup_enabled: bool = Field(True, description="Enable audit log backups")
    backup_frequency: str = Field("daily", description="Backup frequency")
    
    # Performance settings
    async_logging: bool = Field(True, description="Enable asynchronous logging")
    compression_enabled: bool = Field(True, description="Enable log compression")
    indexing_enabled: bool = Field(True, description="Enable search indexing")
    
    # Security settings
    encryption_at_rest: bool = Field(True, description="Encrypt logs at rest")
    encryption_in_transit: bool = Field(True, description="Encrypt logs in transit")
    access_control_enabled: bool = Field(True, description="Enable access control")
    
    # Alert settings
    alert_enabled: bool = Field(True, description="Enable alerting")
    critical_alert_threshold: int = Field(5, description="Critical alert threshold")
    security_alert_enabled: bool = Field(True, description="Enable security alerts")
    
    # Integration settings
    siem_integration: bool = Field(False, description="SIEM integration enabled")
    siem_endpoint: Optional[str] = Field(None, description="SIEM endpoint URL")
    webhook_enabled: bool = Field(False, description="Webhook notifications enabled")
    webhook_urls: List[str] = Field(default=[], description="Webhook URLs")