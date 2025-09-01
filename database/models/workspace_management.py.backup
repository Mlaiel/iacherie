"""Workspace Management Database Model

Enterprise-grade SQLAlchemy model for comprehensive workspace management,
project organization, resource allocation, and collaborative environments.

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
from sqlalchemy import Column, String, Text, DateTime, Float, Integer, Boolean, JSON, ForeignKey, Index, Enum as SQLEnum, ARRAY
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID, JSONB
from datetime import datetime, timezone, timedelta
from enum import Enum
import uuid
from typing import Dict, Any, List, Optional, Set

Base = declarative_base()


class WorkspaceType(Enum):
    """Workspace type enumeration"""
    PERSONAL = "personal"
    TEAM = "team"
    ORGANIZATION = "organization"
    PROJECT = "project"
    CREATIVE_STUDIO = "creative_studio"
    COLLABORATION = "collaboration"
    ENTERPRISE = "enterprise"
    SANDBOX = "sandbox"
    DEVELOPMENT = "development"
    PRODUCTION = "production"
    TEMPLATE = "template"
    SHARED = "shared"


class WorkspaceStatus(Enum):
    """Workspace status enumeration"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"
    ARCHIVED = "archived"
    SETUP = "setup"
    MIGRATION = "migration"
    MAINTENANCE = "maintenance"
    DELETED = "deleted"
    FROZEN = "frozen"


class AccessLevel(Enum):
    """Access level enumeration"""
    PUBLIC = "public"
    PRIVATE = "private"
    RESTRICTED = "restricted"
    INVITATION_ONLY = "invitation_only"
    ORGANIZATION_VISIBLE = "organization_visible"
    TEAM_VISIBLE = "team_visible"


class ResourceType(Enum):
    """Resource type enumeration"""
    STORAGE = "storage"
    COMPUTE = "compute"
    BANDWIDTH = "bandwidth"
    API_CALLS = "api_calls"
    AI_PROCESSING = "ai_processing"
    CONTENT_ANALYSIS = "content_analysis"
    FINGERPRINTING = "fingerprinting"
    DISTRIBUTION = "distribution"
    COLLABORATION = "collaboration"
    INTEGRATIONS = "integrations"


class UsageStatus(Enum):
    """Usage status enumeration"""
    NORMAL = "normal"
    WARNING = "warning"
    CRITICAL = "critical"
    EXCEEDED = "exceeded"
    SUSPENDED = "suspended"


class EnvironmentType(Enum):
    """Environment type enumeration"""
    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"
    TESTING = "testing"
    SANDBOX = "sandbox"
    DEMO = "demo"


class BackupStatus(Enum):
    """Backup status enumeration"""
    ACTIVE = "active"
    SCHEDULED = "scheduled"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    EXPIRED = "expired"


class WorkspaceManagement(Base):
    """
    Enterprise Workspace Management Model
    
    Comprehensive workspace management with resource allocation,
    environment management, and collaborative features.
    """
    __tablename__ = 'workspace_management'
    
    # Primary identification
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    workspace_id = Column(String(100), unique=True, nullable=False, index=True)
    
    # Basic workspace information
    name = Column(String(200), nullable=False)
    display_name = Column(String(200), nullable=True)
    description = Column(Text, nullable=True)
    workspace_type = Column(SQLEnum(WorkspaceType), nullable=False, index=True)
    status = Column(SQLEnum(WorkspaceStatus), nullable=False, default=WorkspaceStatus.SETUP, index=True)
    access_level = Column(SQLEnum(AccessLevel), nullable=False, default=AccessLevel.PRIVATE, index=True)
    
    # Ownership and organization
    owner_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    created_by = Column(UUID(as_uuid=True), nullable=False, index=True)
    organization_id = Column(UUID(as_uuid=True), nullable=True, index=True)
    team_id = Column(UUID(as_uuid=True), nullable=True, index=True)
    parent_workspace_id = Column(UUID(as_uuid=True), ForeignKey('workspace_management.id'), nullable=True, index=True)
    
    # Temporal information
    created_at = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc), index=True)
    updated_at = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    last_accessed_at = Column(DateTime(timezone=True), nullable=True, index=True)
    activated_at = Column(DateTime(timezone=True), nullable=True)
    archived_at = Column(DateTime(timezone=True), nullable=True)
    
    # Resource management
    storage_quota_gb = Column(Float, nullable=False, default=10.0)
    storage_used_gb = Column(Float, nullable=False, default=0.0)
    compute_quota_hours = Column(Float, nullable=True)
    compute_used_hours = Column(Float, nullable=False, default=0.0)
    bandwidth_quota_gb = Column(Float, nullable=True)
    bandwidth_used_gb = Column(Float, nullable=False, default=0.0)
    api_call_quota = Column(Integer, nullable=True)
    api_calls_used = Column(Integer, nullable=False, default=0)
    
    # AI and content protection resources
    ai_processing_quota = Column(Float, nullable=True)
    ai_processing_used = Column(Float, nullable=False, default=0.0)
    fingerprinting_quota = Column(Integer, nullable=True)
    fingerprinting_used = Column(Integer, nullable=False, default=0.0)
    content_analysis_quota = Column(Integer, nullable=True)
    content_analysis_used = Column(Integer, nullable=False, default=0.0)
    
    # Usage tracking and limits
    current_usage_status = Column(SQLEnum(UsageStatus), nullable=False, default=UsageStatus.NORMAL, index=True)
    usage_alerts_enabled = Column(Boolean, nullable=False, default=True)
    usage_alert_thresholds = Column(JSONB, nullable=True)
    last_usage_reset = Column(DateTime(timezone=True), nullable=True)
    usage_reset_frequency = Column(String(20), nullable=False, default="monthly")
    
    # Environment and deployment
    environment_type = Column(SQLEnum(EnvironmentType), nullable=False, default=EnvironmentType.PRODUCTION, index=True)
    deployment_region = Column(String(50), nullable=True)
    availability_zone = Column(String(50), nullable=True)
    custom_domain = Column(String(255), nullable=True)
    ssl_enabled = Column(Boolean, nullable=False, default=True)
    
    # Security and access control
    security_settings = Column(JSONB, nullable=True)
    access_policies = Column(JSONB, nullable=True)
    ip_whitelist = Column(ARRAY(String), nullable=True)
    ip_blacklist = Column(ARRAY(String), nullable=True)
    require_vpn = Column(Boolean, nullable=False, default=False)
    require_2fa = Column(Boolean, nullable=False, default=False)
    session_timeout_minutes = Column(Integer, nullable=False, default=480)
    
    # Collaboration and sharing
    collaboration_enabled = Column(Boolean, nullable=False, default=True)
    max_collaborators = Column(Integer, nullable=True)
    current_collaborators = Column(Integer, nullable=False, default=0)
    sharing_permissions = Column(JSONB, nullable=True)
    external_sharing_enabled = Column(Boolean, nullable=False, default=False)
    
    # Project and content management
    active_projects = Column(Integer, nullable=False, default=0)
    total_content_items = Column(Integer, nullable=False, default=0)
    protected_content_items = Column(Integer, nullable=False, default=0)
    shared_content_items = Column(Integer, nullable=False, default=0)
    content_categories = Column(ARRAY(String), nullable=True)
    
    # Integration and tools
    enabled_integrations = Column(ARRAY(String), nullable=True)
    connected_platforms = Column(JSONB, nullable=True)
    third_party_tools = Column(JSONB, nullable=True)
    webhook_endpoints = Column(JSONB, nullable=True)
    api_keys = Column(JSONB, nullable=True)  # Encrypted
    
    # Backup and disaster recovery
    backup_enabled = Column(Boolean, nullable=False, default=True)
    backup_frequency = Column(String(20), nullable=False, default="daily")
    backup_retention_days = Column(Integer, nullable=False, default=30)
    last_backup_at = Column(DateTime(timezone=True), nullable=True)
    backup_status = Column(SQLEnum(BackupStatus), nullable=False, default=BackupStatus.ACTIVE)
    disaster_recovery_enabled = Column(Boolean, nullable=False, default=False)
    
    # Performance and monitoring
    performance_metrics = Column(JSONB, nullable=True)
    monitoring_enabled = Column(Boolean, nullable=False, default=True)
    alert_channels = Column(ARRAY(String), nullable=True)
    uptime_monitoring = Column(Boolean, nullable=False, default=True)
    performance_alerts = Column(JSONB, nullable=True)
    
    # Billing and subscription
    subscription_plan = Column(String(100), nullable=True)
    billing_cycle = Column(String(20), nullable=True)
    next_billing_date = Column(DateTime(timezone=True), nullable=True)
    usage_billing_enabled = Column(Boolean, nullable=False, default=False)
    cost_center = Column(String(100), nullable=True)
    budget_limit = Column(Float, nullable=True)
    current_costs = Column(Float, nullable=False, default=0.0)
    
    # AI and automation features
    ai_assistance_enabled = Column(Boolean, nullable=False, default=True)
    automated_workflows = Column(JSONB, nullable=True)
    smart_optimization = Column(Boolean, nullable=False, default=True)
    predictive_scaling = Column(Boolean, nullable=False, default=False)
    auto_cleanup_enabled = Column(Boolean, nullable=False, default=True)
    
    # Content protection and compliance
    content_protection_enabled = Column(Boolean, nullable=False, default=True)
    compliance_requirements = Column(ARRAY(String), nullable=True)
    data_residency_requirements = Column(ARRAY(String), nullable=True)
    audit_logging_enabled = Column(Boolean, nullable=False, default=True)
    retention_policies = Column(JSONB, nullable=True)
    
    # Customization and branding
    custom_theme = Column(JSONB, nullable=True)
    branding_settings = Column(JSONB, nullable=True)
    workspace_logo = Column(String(500), nullable=True)
    custom_css = Column(Text, nullable=True)
    welcome_message = Column(Text, nullable=True)
    
    # Geographic and timezone settings
    primary_timezone = Column(String(50), nullable=True)
    allowed_regions = Column(ARRAY(String), nullable=True)
    geo_restrictions = Column(JSONB, nullable=True)
    language_preferences = Column(ARRAY(String), nullable=True)
    
    # Template and cloning
    is_template = Column(Boolean, nullable=False, default=False)
    template_category = Column(String(100), nullable=True)
    cloned_from_workspace_id = Column(UUID(as_uuid=True), nullable=True)
    clone_settings = Column(JSONB, nullable=True)
    template_usage_count = Column(Integer, nullable=False, default=0)
    
    # Advanced features
    feature_flags = Column(JSONB, nullable=True)
    experimental_features = Column(ARRAY(String), nullable=True)
    beta_features_enabled = Column(Boolean, nullable=False, default=False)
    advanced_analytics = Column(Boolean, nullable=False, default=False)
    
    # Metadata and tags
    tags = Column(ARRAY(String), nullable=True)
    labels = Column(JSONB, nullable=True)
    metadata = Column(JSONB, nullable=True)
    custom_attributes = Column(JSONB, nullable=True)
    external_references = Column(JSONB, nullable=True)
    
    # Administrative fields
    is_system_workspace = Column(Boolean, nullable=False, default=False)
    migration_data = Column(JSONB, nullable=True)
    legacy_workspace_id = Column(String(100), nullable=True)
    
    # Relationships
    parent_workspace = relationship("WorkspaceManagement", remote_side=[id], backref="child_workspaces")
    
    # Advanced indexing
    __table_args__ = (
        Index('idx_workspace_management_type_status', 'workspace_type', 'status'),
        Index('idx_workspace_management_owner_org', 'owner_id', 'organization_id'),
        Index('idx_workspace_management_team_parent', 'team_id', 'parent_workspace_id'),
        Index('idx_workspace_management_access_level', 'access_level'),
        Index('idx_workspace_management_environment', 'environment_type', 'deployment_region'),
        Index('idx_workspace_management_usage_status', 'current_usage_status'),
        Index('idx_workspace_management_subscription', 'subscription_plan', 'billing_cycle'),
        Index('idx_workspace_management_backup', 'backup_enabled', 'last_backup_at'),
        Index('idx_workspace_management_security', 'require_2fa', 'require_vpn'),
        Index('idx_workspace_management_storage_usage', 'storage_used_gb', 'storage_quota_gb'),
        Index('idx_workspace_management_activity', 'last_accessed_at'),
        Index('idx_workspace_management_created_updated', 'created_at', 'updated_at'),
    )
    
    def __repr__(self):
        return f"<WorkspaceManagement(id={self.id}, name={self.name}, type={self.workspace_type.value}, status={self.status.value})>"
    
    @classmethod
    def create_workspace(
        cls,
        name: str,
        workspace_type: WorkspaceType,
        owner_id: str,
        created_by: str,
        **kwargs
    ) -> 'WorkspaceManagement':
        """Create a new workspace"""
        workspace_id = f"ws_{uuid.uuid4().hex[:12]}"
        
        return cls(
            workspace_id=workspace_id,
            name=name,
            workspace_type=workspace_type,
            owner_id=owner_id,
            created_by=created_by,
            **kwargs
        )
    
    @classmethod
    def create_from_template(
        cls,
        template_workspace: 'WorkspaceManagement',
        name: str,
        owner_id: str,
        created_by: str,
        **overrides
    ) -> 'WorkspaceManagement':
        """Create workspace from template"""
        if not template_workspace.is_template:
            raise ValueError("Source workspace is not a template")
        
        workspace_data = {
            'name': name,
            'workspace_type': template_workspace.workspace_type,
            'owner_id': owner_id,
            'created_by': created_by,
            'cloned_from_workspace_id': template_workspace.id,
            'storage_quota_gb': template_workspace.storage_quota_gb,
            'ai_assistance_enabled': template_workspace.ai_assistance_enabled,
            'content_protection_enabled': template_workspace.content_protection_enabled,
            **overrides
        }
        
        workspace = cls.create_workspace(**workspace_data)
        template_workspace.template_usage_count += 1
        
        return workspace
    
    def get_storage_usage_percentage(self) -> float:
        """Get storage usage as percentage"""
        if self.storage_quota_gb == 0:
            return 0.0
        return (self.storage_used_gb / self.storage_quota_gb) * 100
    
    def get_compute_usage_percentage(self) -> float:
        """Get compute usage as percentage"""
        if not self.compute_quota_hours or self.compute_quota_hours == 0:
            return 0.0
        return (self.compute_used_hours / self.compute_quota_hours) * 100
    
    def check_resource_limits(self) -> Dict[str, bool]:
        """Check if any resource limits are exceeded"""
        limits_status = {
            'storage_exceeded': self.storage_used_gb >= self.storage_quota_gb,
            'compute_exceeded': False,
            'bandwidth_exceeded': False,
            'api_calls_exceeded': False,
            'ai_processing_exceeded': False
        }
        
        if self.compute_quota_hours:
            limits_status['compute_exceeded'] = self.compute_used_hours >= self.compute_quota_hours
        
        if self.bandwidth_quota_gb:
            limits_status['bandwidth_exceeded'] = self.bandwidth_used_gb >= self.bandwidth_quota_gb
        
        if self.api_call_quota:
            limits_status['api_calls_exceeded'] = self.api_calls_used >= self.api_call_quota
        
        if self.ai_processing_quota:
            limits_status['ai_processing_exceeded'] = self.ai_processing_used >= self.ai_processing_quota
        
        return limits_status
    
    def update_usage_status(self) -> UsageStatus:
        """Update and return current usage status"""
        limits = self.check_resource_limits()
        
        if any(limits.values()):
            self.current_usage_status = UsageStatus.EXCEEDED
        elif self.get_storage_usage_percentage() > 90:
            self.current_usage_status = UsageStatus.CRITICAL
        elif self.get_storage_usage_percentage() > 75:
            self.current_usage_status = UsageStatus.WARNING
        else:
            self.current_usage_status = UsageStatus.NORMAL
        
        return self.current_usage_status
    
    def can_user_access(self, user_id: str, required_access: str = "read") -> bool:
        """Check if user can access workspace"""
        if self.owner_id == user_id:
            return True
        
        if self.access_level == AccessLevel.PUBLIC:
            return True
        
        # Additional checks would be implemented based on workspace members
        return False
    
    def add_storage_usage(self, gb_amount: float) -> bool:
        """Add storage usage and check limits"""
        if self.storage_used_gb + gb_amount > self.storage_quota_gb:
            return False
        
        self.storage_used_gb += gb_amount
        self.update_usage_status()
        self.last_accessed_at = datetime.now(timezone.utc)
        return True
    
    def add_compute_usage(self, hours_amount: float) -> bool:
        """Add compute usage and check limits"""
        if self.compute_quota_hours and self.compute_used_hours + hours_amount > self.compute_quota_hours:
            return False
        
        self.compute_used_hours += hours_amount
        self.update_usage_status()
        self.last_accessed_at = datetime.now(timezone.utc)
        return True
    
    def reset_usage_metrics(self) -> None:
        """Reset usage metrics for billing cycle"""
        if self.usage_reset_frequency == "monthly":
            self.compute_used_hours = 0.0
            self.bandwidth_used_gb = 0.0
            self.api_calls_used = 0
            self.ai_processing_used = 0.0
            self.fingerprinting_used = 0
            self.content_analysis_used = 0
            self.last_usage_reset = datetime.now(timezone.utc)
            self.current_costs = 0.0
            self.update_usage_status()
    
    def archive_workspace(self, archived_by: str, reason: str = None) -> None:
        """Archive the workspace"""
        self.status = WorkspaceStatus.ARCHIVED
        self.archived_at = datetime.now(timezone.utc)
        self.updated_at = datetime.now(timezone.utc)
        
        if not self.metadata:
            self.metadata = {}
        
        self.metadata['archive_info'] = {
            'archived_by': archived_by,
            'archived_at': datetime.now(timezone.utc).isoformat(),
            'reason': reason
        }
    
    def restore_workspace(self, restored_by: str) -> None:
        """Restore archived workspace"""
        self.status = WorkspaceStatus.ACTIVE
        self.archived_at = None
        self.updated_at = datetime.now(timezone.utc)
        
        if not self.metadata:
            self.metadata = {}
        
        self.metadata['restore_info'] = {
            'restored_by': restored_by,
            'restored_at': datetime.now(timezone.utc).isoformat()
        }
    
    def clone_workspace(
        self,
        new_name: str,
        new_owner_id: str,
        created_by: str,
        include_data: bool = False
    ) -> 'WorkspaceManagement':
        """Clone workspace to create a new one"""
        clone_data = {
            'name': new_name,
            'workspace_type': self.workspace_type,
            'owner_id': new_owner_id,
            'created_by': created_by,
            'cloned_from_workspace_id': self.id,
            'description': f"Cloned from {self.name}",
            'storage_quota_gb': self.storage_quota_gb,
            'compute_quota_hours': self.compute_quota_hours,
            'ai_assistance_enabled': self.ai_assistance_enabled,
            'content_protection_enabled': self.content_protection_enabled,
            'security_settings': self.security_settings,
            'feature_flags': self.feature_flags
        }
        
        cloned_workspace = self.__class__.create_workspace(**clone_data)
        
        # Record cloning in metadata
        if not cloned_workspace.metadata:
            cloned_workspace.metadata = {}
        
        cloned_workspace.metadata['clone_info'] = {
            'source_workspace_id': str(self.id),
            'cloned_at': datetime.now(timezone.utc).isoformat(),
            'include_data': include_data
        }
        
        return cloned_workspace
    
    def get_workspace_summary(self) -> Dict[str, Any]:
        """Get comprehensive workspace summary"""
        return {
            'basic_info': {
                'workspace_id': self.workspace_id,
                'name': self.name,
                'type': self.workspace_type.value,
                'status': self.status.value,
                'access_level': self.access_level.value,
                'environment': self.environment_type.value
            },
            'resources': {
                'storage': {
                    'used_gb': self.storage_used_gb,
                    'quota_gb': self.storage_quota_gb,
                    'usage_percentage': self.get_storage_usage_percentage()
                },
                'compute': {
                    'used_hours': self.compute_used_hours,
                    'quota_hours': self.compute_quota_hours,
                    'usage_percentage': self.get_compute_usage_percentage()
                },
                'ai_processing': {
                    'used': self.ai_processing_used,
                    'quota': self.ai_processing_quota
                }
            },
            'activity': {
                'created_at': self.created_at.isoformat(),
                'last_accessed': self.last_accessed_at.isoformat() if self.last_accessed_at else None,
                'days_since_creation': (datetime.now(timezone.utc) - self.created_at).days,
                'active_projects': self.active_projects,
                'total_content': self.total_content_items
            },
            'collaboration': {
                'enabled': self.collaboration_enabled,
                'current_collaborators': self.current_collaborators,
                'max_collaborators': self.max_collaborators,
                'external_sharing': self.external_sharing_enabled
            },
            'features': {
                'ai_assistance': self.ai_assistance_enabled,
                'content_protection': self.content_protection_enabled,
                'backup_enabled': self.backup_enabled,
                'monitoring_enabled': self.monitoring_enabled
            },
            'security': {
                'require_2fa': self.require_2fa,
                'require_vpn': self.require_vpn,
                'ssl_enabled': self.ssl_enabled,
                'session_timeout': self.session_timeout_minutes
            }
        }


class WorkspaceProject(Base):
    """
    Workspace Project Model
    
    Manages projects within workspaces.
    """
    __tablename__ = 'workspace_projects'
    
    # Primary identification
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id = Column(String(100), unique=True, nullable=False, index=True)
    
    # Relationships
    workspace_id = Column(UUID(as_uuid=True), ForeignKey('workspace_management.id'), nullable=False, index=True)
    
    # Project information
    name = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    status = Column(String(50), nullable=False, default="active")
    
    # Timeline
    created_at = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    due_date = Column(DateTime(timezone=True), nullable=True)
    
    # Project details
    project_type = Column(String(100), nullable=True)
    priority = Column(String(20), nullable=False, default="medium")
    tags = Column(ARRAY(String), nullable=True)
    metadata = Column(JSONB, nullable=True)
    
    # Relationships
    workspace = relationship("WorkspaceManagement", backref="projects")
    
    __table_args__ = (
        Index('idx_workspace_projects_workspace_status', 'workspace_id', 'status'),
        Index('idx_workspace_projects_created_updated', 'created_at', 'updated_at'),
    )
    
    def __repr__(self):
        return f"<WorkspaceProject(project_id={self.project_id}, name={self.name}, workspace_id={self.workspace_id})>"
