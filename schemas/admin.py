"""
Admin & System Management Schemas for IA Influencer Agent Platform
Comprehensive system administration, user management, and platform governance schemas

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

🚨 INTELLECTUAL PROPERTY WARNING: Unauthorized use prohibited.
Contact: mlaiel@live.de for licensing and permissions.
"""

from datetime import datetime, date
from decimal import Decimal
from typing import Any, Dict, List, Optional, Union
from uuid import UUID

from pydantic import Field, EmailStr, HttpUrl, validator

from .base import BaseSchema, TimestampSchema, UUIDSchema, AuditSchema


class AdminUser(UUIDSchema, TimestampSchema, AuditSchema):
    """Administrative user management schema."""
    
    username: str = Field(description="Admin username")
    email: EmailStr = Field(description="Admin email address")
    full_name: str = Field(description="Full name")
    employee_id: Optional[str] = Field(None, description="Employee ID")
    
    # Role and permissions
    admin_role: str = Field(description="Administrative role")
    permission_level: int = Field(ge=1, le=10, description="Permission level (1-10)")
    assigned_permissions: List[str] = Field(description="Specific permissions granted")
    restricted_actions: List[str] = Field(default_factory=list)
    
    # Access control
    department: str = Field(description="Department/team")
    reporting_manager: Optional[UUID] = Field(None, description="Manager's user ID")
    access_scope: List[str] = Field(description="Scope of access")
    geographic_restrictions: List[str] = Field(default_factory=list)
    
    # Authentication
    mfa_enabled: bool = Field(default=True, description="Multi-factor authentication")
    last_password_change: Optional[datetime] = None
    password_expiry_date: Optional[datetime] = None
    failed_login_attempts: int = Field(default=0, ge=0)
    account_locked: bool = Field(default=False)
    
    # Activity tracking
    last_login: Optional[datetime] = None
    last_activity: Optional[datetime] = None
    login_count: int = Field(default=0, ge=0)
    total_session_time: int = Field(default=0, ge=0, description="Total session time in minutes")
    
    # Status and compliance
    account_status: str = Field(default="active")
    employment_status: str = Field(description="Employment status")
    security_clearance: Optional[str] = None
    compliance_training_completed: bool = Field(default=False)
    
    # Contact and emergency
    phone_number: Optional[str] = None
    emergency_contact: Optional[Dict[str, str]] = None
    work_location: Optional[str] = None
    timezone: str = Field(default="UTC")
    
    @validator('admin_role')
    def validate_admin_role(cls, v):
        """Validate admin role."""
        allowed_roles = {
            "super_admin", "system_admin", "user_admin", "content_moderator",
            "security_admin", "billing_admin", "analytics_admin", "support_admin",
            "compliance_officer", "technical_lead", "operations_manager"
        }
        if v not in allowed_roles:
            raise ValueError(f'Admin role must be one of: {", ".join(allowed_roles)}')
        return v


class SystemConfiguration(UUIDSchema, TimestampSchema, AuditSchema):
    """System-wide configuration management schema."""
    
    config_category: str = Field(description="Configuration category")
    config_name: str = Field(description="Configuration parameter name")
    config_key: str = Field(description="Unique configuration key")
    
    # Configuration value
    config_value: Union[str, int, float, bool, Dict[str, Any]] = Field(
        description="Configuration value"
    )
    default_value: Union[str, int, float, bool, Dict[str, Any]] = Field(
        description="Default configuration value"
    )
    value_type: str = Field(description="Data type of the configuration value")
    
    # Validation and constraints
    validation_rules: List[str] = Field(default_factory=list)
    allowed_values: Optional[List[Any]] = None
    min_value: Optional[Union[int, float]] = None
    max_value: Optional[Union[int, float]] = None
    
    # Configuration metadata
    description: str = Field(description="Configuration description")
    impact_level: str = Field(description="Impact level of changing this config")
    requires_restart: bool = Field(default=False)
    environment_specific: bool = Field(default=False)
    
    # Access control
    read_permissions: List[str] = Field(description="Roles that can read this config")
    write_permissions: List[str] = Field(description="Roles that can modify this config")
    sensitive_data: bool = Field(default=False)
    
    # Change management
    change_approval_required: bool = Field(default=False)
    approval_workflow: Optional[str] = None
    change_history: List[Dict[str, Any]] = Field(default_factory=list)
    rollback_supported: bool = Field(default=True)
    
    # Status and monitoring
    is_active: bool = Field(default=True)
    last_modified_by: UUID = Field(description="Last modifier user ID")
    validation_status: str = Field(default="valid")
    
    # Environment deployment
    development_value: Optional[Any] = None
    staging_value: Optional[Any] = None
    production_value: Optional[Any] = None
    
    @validator('config_category')
    def validate_config_category(cls, v):
        """Validate configuration category."""
        allowed_categories = {
            "authentication", "security", "database", "storage", "api_limits",
            "email_settings", "notification", "monitoring", "backup", "logging",
            "performance", "feature_flags", "integration", "compliance"
        }
        if v not in allowed_categories:
            raise ValueError(f'Config category must be one of: {", ".join(allowed_categories)}')
        return v


class AuditLog(UUIDSchema, TimestampSchema):
    """Comprehensive audit logging schema."""
    
    event_type: str = Field(description="Type of audited event")
    event_category: str = Field(description="Category of the event")
    severity_level: str = Field(description="Event severity level")
    
    # Event details
    event_description: str = Field(description="Detailed event description")
    event_source: str = Field(description="Source system/component")
    event_target: Optional[str] = Field(None, description="Target of the event")
    
    # Actor information
    user_id: Optional[UUID] = Field(None, description="User performing the action")
    user_type: str = Field(description="Type of user (admin, regular, system)")
    session_id: Optional[str] = Field(None, description="Session identifier")
    ip_address: str = Field(description="Source IP address")
    
    # Context and metadata
    request_id: Optional[str] = Field(None, description="Request correlation ID")
    user_agent: Optional[str] = Field(None, description="User agent string")
    geolocation: Optional[Dict[str, str]] = Field(None, description="Geographic location")
    device_info: Optional[Dict[str, str]] = Field(None, description="Device information")
    
    # Action details
    action_performed: str = Field(description="Specific action performed")
    resource_affected: Optional[str] = Field(None, description="Resource that was affected")
    resource_id: Optional[UUID] = Field(None, description="ID of affected resource")
    before_state: Optional[Dict[str, Any]] = Field(None, description="State before action")
    after_state: Optional[Dict[str, Any]] = Field(None, description="State after action")
    
    # Outcome and impact
    action_result: str = Field(description="Result of the action")
    error_details: Optional[str] = Field(None, description="Error details if failed")
    impact_assessment: Optional[str] = Field(None, description="Impact assessment")
    
    # Security and compliance
    security_event: bool = Field(default=False)
    compliance_relevant: bool = Field(default=False)
    privacy_impact: bool = Field(default=False)
    data_classification: str = Field(description="Data classification level")
    
    # Investigation and response
    requires_investigation: bool = Field(default=False)
    investigation_status: Optional[str] = None
    assigned_investigator: Optional[UUID] = None
    resolution_notes: Optional[str] = None
    
    @validator('event_type')
    def validate_event_type(cls, v):
        """Validate event type."""
        allowed_types = {
            "authentication", "authorization", "data_access", "data_modification",
            "system_configuration", "user_management", "security_incident",
            "compliance_event", "performance_issue", "error", "backup_restore"
        }
        if v not in allowed_types:
            raise ValueError(f'Event type must be one of: {", ".join(allowed_types)}')
        return v


class UserManagement(UUIDSchema, TimestampSchema, AuditSchema):
    """Comprehensive user management schema."""
    
    target_user_id: UUID = Field(description="User being managed")
    action_type: str = Field(description="Type of management action")
    admin_user_id: UUID = Field(description="Admin performing the action")
    
    # Action details
    action_description: str = Field(description="Description of action taken")
    action_reason: str = Field(description="Reason for the action")
    effective_date: datetime = Field(description="When the action takes effect")
    expiration_date: Optional[datetime] = Field(None, description="When the action expires")
    
    # User account modifications
    account_status_change: Optional[str] = None
    permission_changes: List[str] = Field(default_factory=list)
    role_changes: List[str] = Field(default_factory=list)
    profile_modifications: Optional[Dict[str, Any]] = None
    
    # Security actions
    password_reset_forced: bool = Field(default=False)
    mfa_requirement_changed: bool = Field(default=False)
    security_clearance_modified: Optional[str] = None
    access_restrictions_applied: List[str] = Field(default_factory=list)
    
    # Disciplinary actions
    warning_issued: bool = Field(default=False)
    suspension_applied: bool = Field(default=False)
    suspension_duration: Optional[int] = Field(None, description="Suspension duration in days")
    termination_initiated: bool = Field(default=False)
    
    # Communication
    notification_sent: bool = Field(default=True)
    notification_channels: List[str] = Field(default_factory=list)
    user_acknowledgment_required: bool = Field(default=False)
    user_acknowledgment_received: bool = Field(default=False)
    
    # Documentation
    supporting_documents: List[HttpUrl] = Field(default_factory=list)
    incident_reference: Optional[str] = None
    policy_violations: List[str] = Field(default_factory=list)
    
    # Review and approval
    approval_required: bool = Field(default=False)
    approved_by: Optional[UUID] = None
    approval_date: Optional[datetime] = None
    review_scheduled: bool = Field(default=False)
    review_date: Optional[datetime] = None
    
    @validator('action_type')
    def validate_action_type(cls, v):
        """Validate action type."""
        allowed_types = {
            "account_creation", "account_modification", "account_suspension",
            "account_termination", "permission_grant", "permission_revoke",
            "role_assignment", "role_removal", "password_reset", "security_update",
            "warning_issued", "disciplinary_action", "account_recovery"
        }
        if v not in allowed_types:
            raise ValueError(f'Action type must be one of: {", ".join(allowed_types)}')
        return v


class SystemHealth(UUIDSchema, TimestampSchema):
    """System health monitoring schema."""
    
    component_name: str = Field(description="System component name")
    health_status: str = Field(description="Overall health status")
    health_score: float = Field(ge=0.0, le=100.0, description="Health score percentage")
    
    # Performance metrics
    response_time: float = Field(ge=0.0, description="Average response time in ms")
    throughput: int = Field(ge=0, description="Requests per second")
    error_rate: float = Field(ge=0.0, le=100.0, description="Error rate percentage")
    cpu_usage: float = Field(ge=0.0, le=100.0, description="CPU usage percentage")
    memory_usage: float = Field(ge=0.0, le=100.0, description="Memory usage percentage")
    
    # Availability metrics
    uptime_percentage: float = Field(ge=0.0, le=100.0)
    downtime_minutes: int = Field(ge=0, description="Downtime in last 24 hours")
    last_outage: Optional[datetime] = None
    mttr: Optional[float] = Field(None, description="Mean Time To Recovery in minutes")
    
    # Resource utilization
    disk_usage: float = Field(ge=0.0, le=100.0)
    network_io: Dict[str, float] = Field(default_factory=dict)
    database_connections: int = Field(ge=0)
    cache_hit_rate: float = Field(ge=0.0, le=100.0)
    
    # Health indicators
    active_connections: int = Field(ge=0)
    queue_length: int = Field(ge=0)
    background_jobs: Dict[str, int] = Field(default_factory=dict)
    external_dependencies: Dict[str, str] = Field(default_factory=dict)
    
    # Alerts and warnings
    critical_alerts: int = Field(ge=0)
    warning_alerts: int = Field(ge=0)
    active_incidents: int = Field(ge=0)
    maintenance_scheduled: bool = Field(default=False)
    
    # Predictions and trends
    capacity_projection: Optional[Dict[str, float]] = None
    performance_trend: str = Field(description="Performance trend direction")
    resource_exhaustion_prediction: Optional[datetime] = None
    
    @validator('health_status')
    def validate_health_status(cls, v):
        """Validate health status."""
        allowed_statuses = {"healthy", "warning", "critical", "maintenance", "degraded", "outage"}
        if v not in allowed_statuses:
            raise ValueError(f'Health status must be one of: {", ".join(allowed_statuses)}')
        return v


class BackupConfiguration(UUIDSchema, TimestampSchema, AuditSchema):
    """System backup configuration and management schema."""
    
    backup_name: str = Field(description="Backup configuration name")
    backup_type: str = Field(description="Type of backup")
    backup_scope: str = Field(description="Scope of backup")
    
    # Backup schedule
    schedule_enabled: bool = Field(default=True)
    backup_frequency: str = Field(description="Backup frequency")
    backup_time: str = Field(description="Preferred backup time")
    retention_policy: str = Field(description="Backup retention policy")
    
    # Backup targets
    source_systems: List[str] = Field(description="Systems to backup")
    data_types: List[str] = Field(description="Types of data to backup")
    include_patterns: List[str] = Field(default_factory=list)
    exclude_patterns: List[str] = Field(default_factory=list)
    
    # Storage configuration
    storage_location: str = Field(description="Backup storage location")
    storage_type: str = Field(description="Type of storage")
    encryption_enabled: bool = Field(default=True)
    compression_enabled: bool = Field(default=True)
    
    # Performance settings
    backup_window: str = Field(description="Allowed backup window")
    bandwidth_limit: Optional[int] = Field(None, description="Bandwidth limit in MB/s")
    parallel_streams: int = Field(default=1, ge=1, description="Number of parallel streams")
    
    # Verification and testing
    integrity_check: bool = Field(default=True)
    test_restore_frequency: str = Field(description="Test restore frequency")
    last_test_restore: Optional[datetime] = None
    test_restore_success: Optional[bool] = None
    
    # Monitoring and alerts
    monitoring_enabled: bool = Field(default=True)
    alert_on_failure: bool = Field(default=True)
    alert_recipients: List[EmailStr] = Field(default_factory=list)
    sla_requirements: Dict[str, Any] = Field(default_factory=dict)
    
    # Backup statistics
    last_backup_date: Optional[datetime] = None
    last_backup_size: Optional[int] = Field(None, description="Last backup size in MB")
    average_backup_time: Optional[int] = Field(None, description="Average backup time in minutes")
    success_rate: float = Field(default=100.0, ge=0.0, le=100.0)
    
    # Disaster recovery
    disaster_recovery_tier: str = Field(description="DR tier classification")
    rpo_target: int = Field(description="Recovery Point Objective in minutes")
    rto_target: int = Field(description="Recovery Time Objective in minutes")
    geographic_replication: bool = Field(default=False)
    
    @validator('backup_type')
    def validate_backup_type(cls, v):
        """Validate backup type."""
        allowed_types = {
            "full_backup", "incremental_backup", "differential_backup",
            "transaction_log_backup", "file_backup", "database_backup",
            "system_state_backup", "application_backup"
        }
        if v not in allowed_types:
            raise ValueError(f'Backup type must be one of: {", ".join(allowed_types)}')
        return v


class ComplianceReport(UUIDSchema, TimestampSchema, AuditSchema):
    """Compliance monitoring and reporting schema."""
    
    report_name: str = Field(description="Compliance report name")
    compliance_framework: str = Field(description="Compliance framework/regulation")
    reporting_period_start: date
    reporting_period_end: date
    
    # Compliance status
    overall_compliance_score: float = Field(ge=0.0, le=100.0)
    compliance_status: str = Field(description="Overall compliance status")
    critical_violations: int = Field(ge=0)
    minor_violations: int = Field(ge=0)
    
    # Framework requirements
    total_requirements: int = Field(ge=1)
    compliant_requirements: int = Field(ge=0)
    non_compliant_requirements: int = Field(ge=0)
    partially_compliant_requirements: int = Field(ge=0)
    
    # Compliance areas
    data_protection_score: float = Field(ge=0.0, le=100.0)
    privacy_protection_score: float = Field(ge=0.0, le=100.0)
    security_compliance_score: float = Field(ge=0.0, le=100.0)
    operational_compliance_score: float = Field(ge=0.0, le=100.0)
    
    # Risk assessment
    compliance_risks: List[Dict[str, Any]] = Field(default_factory=list)
    risk_level: str = Field(description="Overall compliance risk level")
    mitigation_strategies: List[str] = Field(default_factory=list)
    
    # Remediation tracking
    open_findings: int = Field(ge=0)
    resolved_findings: int = Field(ge=0)
    overdue_actions: int = Field(ge=0)
    average_resolution_time: Optional[int] = Field(None, description="Average resolution time in days")
    
    # Audit information
    audit_scope: List[str] = Field(description="Scope of compliance audit")
    auditor_information: Dict[str, str] = Field(default_factory=dict)
    audit_methodology: str = Field(description="Audit methodology used")
    supporting_evidence: List[HttpUrl] = Field(default_factory=list)
    
    # Recommendations
    immediate_actions: List[str] = Field(default_factory=list)
    strategic_recommendations: List[str] = Field(default_factory=list)
    investment_requirements: Optional[Decimal] = Field(None, ge=0)
    
    # Certification status
    certification_status: Optional[str] = None
    certification_expiry: Optional[date] = None
    next_audit_date: Optional[date] = None
    continuous_monitoring: bool = Field(default=True)
    
    @validator('compliance_framework')
    def validate_compliance_framework(cls, v):
        """Validate compliance framework."""
        allowed_frameworks = {
            "GDPR", "CCPA", "HIPAA", "SOX", "PCI_DSS", "ISO_27001",
            "SOC2", "COPPA", "FERPA", "PIPEDA", "LGPD", "custom"
        }
        if v not in allowed_frameworks:
            raise ValueError(f'Compliance framework must be one of: {", ".join(allowed_frameworks)}')
        return v


class PlatformSettings(UUIDSchema, TimestampSchema, AuditSchema):
    """Platform-wide settings and configuration schema."""
    
    setting_category: str = Field(description="Settings category")
    setting_name: str = Field(description="Setting name")
    setting_description: str = Field(description="Setting description")
    
    # Setting value
    current_value: Union[str, int, float, bool, Dict[str, Any]] = Field(
        description="Current setting value"
    )
    default_value: Union[str, int, float, bool, Dict[str, Any]] = Field(
        description="Default setting value"
    )
    
    # Feature flags
    feature_enabled: bool = Field(default=True)
    beta_feature: bool = Field(default=False)
    rollout_percentage: float = Field(default=100.0, ge=0.0, le=100.0)
    target_user_groups: List[str] = Field(default_factory=list)
    
    # Business rules
    business_impact: str = Field(description="Business impact of this setting")
    user_impact: str = Field(description="User impact of this setting")
    revenue_impact: Optional[str] = None
    
    # Validation and constraints
    validation_rules: List[str] = Field(default_factory=list)
    allowed_values: Optional[List[Any]] = None
    dependencies: List[str] = Field(default_factory=list)
    conflicts: List[str] = Field(default_factory=list)
    
    # Change management
    change_approval_required: bool = Field(default=False)
    testing_required: bool = Field(default=False)
    rollback_plan: Optional[str] = None
    
    # Monitoring
    monitoring_enabled: bool = Field(default=True)
    alert_on_change: bool = Field(default=False)
    performance_impact_monitoring: bool = Field(default=False)
    
    # A/B testing
    ab_test_enabled: bool = Field(default=False)
    test_variants: Optional[Dict[str, Any]] = None
    success_metrics: List[str] = Field(default_factory=list)
    
    @validator('setting_category')
    def validate_setting_category(cls, v):
        """Validate setting category."""
        allowed_categories = {
            "user_experience", "security", "performance", "monetization",
            "content_policy", "api_limits", "feature_flags", "integration",
            "notification", "analytics", "compliance", "experimental"
        }
        if v not in allowed_categories:
            raise ValueError(f'Setting category must be one of: {", ".join(allowed_categories)}')
        return v
