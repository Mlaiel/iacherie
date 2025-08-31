"""
User Permissions Database Model

Enterprise-grade SQLAlchemy model for managing user permissions, roles,
access control, and security policies with granular permission management.

Author: Fahed Mlaiel <mlaiel@live.de>
Project: IA Influencer Agent + Content Protection Platform
Copyright: All rights reserved. Unauthorized use, modification, or distribution prohibited.

 INTELLECTUAL PROPERTY WARNING: This code, concept, and architecture are 
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


class PermissionType(Enum):
    """Permission type enumeration"""
    READ = "read"
    WRITE = "write"
    DELETE = "delete"
    CREATE = "create"
    UPDATE = "update"
    EXECUTE = "execute"
    ADMIN = "admin"
    OWNER = "owner"
    SHARE = "share"
    COLLABORATE = "collaborate"
    PUBLISH = "publish"
    MODERATE = "moderate"
    ANALYTICS = "analytics"
    BILLING = "billing"
    SETTINGS = "settings"


class ResourceType(Enum):
    """Resource type enumeration"""
    CONTENT = "content"
    USER_PROFILE = "user_profile"
    CREATOR_PROFILE = "creator_profile"
    COLLABORATION = "collaboration"
    LICENSING = "licensing"
    ANALYTICS = "analytics"
    REVENUE = "revenue"
    PAYMENT = "payment"
    PROTECTION_POLICY = "protection_policy"
    NOTIFICATION = "notification"
    INTEGRATION = "integration"
    SUBSCRIPTION = "subscription"
    TEAM = "team"
    WORKSPACE = "workspace"
    API = "api"
    WEBHOOK = "webhook"
    EXPORT = "export"
    AUDIT_LOG = "audit_log"
    SYSTEM_SETTINGS = "system_settings"
    PLATFORM_ADMIN = "platform_admin"


class RoleType(Enum):
    """Role type enumeration"""
    SUPER_ADMIN = "super_admin"
    ADMIN = "admin"
    MODERATOR = "moderator"
    CREATOR = "creator"
    COLLABORATOR = "collaborator"
    VIEWER = "viewer"
    GUEST = "guest"
    API_USER = "api_user"
    SERVICE_ACCOUNT = "service_account"
    TEAM_MEMBER = "team_member"
    TEAM_LEADER = "team_leader"
    BILLING_ADMIN = "billing_admin"
    CONTENT_MANAGER = "content_manager"
    ANALYTICS_VIEWER = "analytics_viewer"
    SUPPORT_AGENT = "support_agent"


class PermissionScope(Enum):
    """Permission scope enumeration"""
    GLOBAL = "global"
    ORGANIZATION = "organization"
    TEAM = "team"
    PROJECT = "project"
    RESOURCE_SPECIFIC = "resource_specific"
    USER_SPECIFIC = "user_specific"
    TIME_LIMITED = "time_limited"
    IP_RESTRICTED = "ip_restricted"
    DEVICE_RESTRICTED = "device_restricted"


class AccessLevel(Enum):
    """Access level enumeration"""
    NONE = "none"
    LIMITED = "limited"
    STANDARD = "standard"
    ELEVATED = "elevated"
    FULL = "full"
    UNRESTRICTED = "unrestricted"


class PermissionStatus(Enum):
    """Permission status enumeration"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"
    EXPIRED = "expired"
    PENDING_APPROVAL = "pending_approval"
    REVOKED = "revoked"
    TEMPORARY = "temporary"


class UserPermissions(Base):
    """
    Enterprise User Permissions Model
    
    Comprehensive permission management with role-based access control,
    resource-level permissions, and temporal access management.
    """
    __tablename__ = 'user_permissions'
    
    # Primary identification
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    permission_id = Column(String(100), unique=True, nullable=False, index=True)
    
    # User and resource references
    user_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    granted_by_user_id = Column(UUID(as_uuid=True), nullable=True, index=True)
    resource_type = Column(SQLEnum(ResourceType), nullable=False, index=True)
    resource_id = Column(String(200), nullable=True, index=True)  # Specific resource ID
    
    # Permission configuration
    permission_type = Column(SQLEnum(PermissionType), nullable=False, index=True)
    role_type = Column(SQLEnum(RoleType), nullable=True, index=True)
    scope = Column(SQLEnum(PermissionScope), nullable=False, default=PermissionScope.RESOURCE_SPECIFIC, index=True)
    access_level = Column(SQLEnum(AccessLevel), nullable=False, default=AccessLevel.STANDARD, index=True)
    status = Column(SQLEnum(PermissionStatus), nullable=False, default=PermissionStatus.ACTIVE, index=True)
    
    # Permission details
    name = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    justification = Column(Text, nullable=True)
    conditions = Column(JSONB, nullable=True)
    
    # Temporal constraints
    created_at = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc), index=True)
    updated_at = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    granted_at = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))
    expires_at = Column(DateTime(timezone=True), nullable=True, index=True)
    last_used_at = Column(DateTime(timezone=True), nullable=True, index=True)
    
    # Access restrictions
    ip_whitelist = Column(ARRAY(String), nullable=True)
    ip_blacklist = Column(ARRAY(String), nullable=True)
    device_restrictions = Column(JSONB, nullable=True)
    geographic_restrictions = Column(ARRAY(String), nullable=True)
    time_restrictions = Column(JSONB, nullable=True)  # {days: [1,2,3], hours: [9,17]}
    
    # Usage tracking
    usage_count = Column(Integer, nullable=False, default=0)
    usage_limit = Column(Integer, nullable=True)
    daily_usage_limit = Column(Integer, nullable=True)
    monthly_usage_limit = Column(Integer, nullable=True)
    usage_reset_date = Column(DateTime(timezone=True), nullable=True)
    
    # Rate limiting
    rate_limit_per_minute = Column(Integer, nullable=True)
    rate_limit_per_hour = Column(Integer, nullable=True)
    rate_limit_per_day = Column(Integer, nullable=True)
    current_usage_count = Column(Integer, nullable=False, default=0)
    rate_limit_reset_at = Column(DateTime(timezone=True), nullable=True)
    
    # Delegation and inheritance
    is_delegated = Column(Boolean, nullable=False, default=False)
    delegated_from_user_id = Column(UUID(as_uuid=True), nullable=True, index=True)
    can_delegate = Column(Boolean, nullable=False, default=False)
    inherits_from_role = Column(Boolean, nullable=False, default=False)
    inherited_permissions = Column(JSONB, nullable=True)
    
    # Approval workflow
    requires_approval = Column(Boolean, nullable=False, default=False)
    approved_by_user_id = Column(UUID(as_uuid=True), nullable=True)
    approved_at = Column(DateTime(timezone=True), nullable=True)
    approval_notes = Column(Text, nullable=True)
    auto_approval_rules = Column(JSONB, nullable=True)
    
    # Risk and compliance
    risk_level = Column(String(20), nullable=False, default="low")  # low, medium, high, critical
    compliance_requirements = Column(ARRAY(String), nullable=True)
    audit_required = Column(Boolean, nullable=False, default=False)
    sensitive_data_access = Column(Boolean, nullable=False, default=False)
    pii_access = Column(Boolean, nullable=False, default=False)
    
    # Emergency access
    emergency_access = Column(Boolean, nullable=False, default=False)
    break_glass_access = Column(Boolean, nullable=False, default=False)
    emergency_justification = Column(Text, nullable=True)
    emergency_approved_by = Column(String(100), nullable=True)
    emergency_expires_at = Column(DateTime(timezone=True), nullable=True)
    
    # Integration and API access
    api_access_enabled = Column(Boolean, nullable=False, default=False)
    api_key_required = Column(Boolean, nullable=False, default=False)
    webhook_access = Column(Boolean, nullable=False, default=False)
    third_party_access = Column(Boolean, nullable=False, default=False)
    oauth_scopes = Column(ARRAY(String), nullable=True)
    
    # Multi-factor authentication
    mfa_required = Column(Boolean, nullable=False, default=False)
    mfa_methods = Column(ARRAY(String), nullable=True)
    last_mfa_verification = Column(DateTime(timezone=True), nullable=True)
    mfa_bypass_allowed = Column(Boolean, nullable=False, default=False)
    
    # Context and conditions
    contextual_permissions = Column(JSONB, nullable=True)
    conditional_access = Column(JSONB, nullable=True)
    attribute_based_rules = Column(JSONB, nullable=True)
    dynamic_permissions = Column(Boolean, nullable=False, default=False)
    
    # Team and group permissions
    team_id = Column(String(100), nullable=True, index=True)
    group_permissions = Column(JSONB, nullable=True)
    inherited_from_team = Column(Boolean, nullable=False, default=False)
    team_role = Column(String(100), nullable=True)
    
    # Data classification access
    data_classification_level = Column(String(50), nullable=True)
    security_clearance_level = Column(String(50), nullable=True)
    need_to_know = Column(Boolean, nullable=False, default=False)
    data_categories_access = Column(ARRAY(String), nullable=True)
    
    # Monitoring and alerting
    monitor_usage = Column(Boolean, nullable=False, default=True)
    alert_on_unusual_activity = Column(Boolean, nullable=False, default=True)
    log_all_access = Column(Boolean, nullable=False, default=False)
    real_time_monitoring = Column(Boolean, nullable=False, default=False)
    
    # Performance and optimization
    cache_duration_minutes = Column(Integer, nullable=False, default=5)
    background_refresh = Column(Boolean, nullable=False, default=False)
    permission_evaluation_cache = Column(JSONB, nullable=True)
    last_cache_refresh = Column(DateTime(timezone=True), nullable=True)
    
    # Metadata and tags
    tags = Column(ARRAY(String), nullable=True)
    metadata = Column(JSONB, nullable=True)
    custom_attributes = Column(JSONB, nullable=True)
    external_references = Column(JSONB, nullable=True)
    
    # Administrative fields
    is_system_permission = Column(Boolean, nullable=False, default=False)
    is_temporary = Column(Boolean, nullable=False, default=False)
    is_critical = Column(Boolean, nullable=False, default=False)
    requires_justification = Column(Boolean, nullable=False, default=False)
    
    # Audit trail
    created_by = Column(String(100), nullable=False)
    updated_by = Column(String(100), nullable=True)
    granted_by = Column(String(100), nullable=False)
    revoked_by = Column(String(100), nullable=True)
    revoked_at = Column(DateTime(timezone=True), nullable=True)
    revocation_reason = Column(Text, nullable=True)
    
    # Advanced indexing
    __table_args__ = (
        Index('idx_user_permissions_user_resource', 'user_id', 'resource_type', 'resource_id'),
        Index('idx_user_permissions_permission_type', 'permission_type', 'status'),
        Index('idx_user_permissions_role_scope', 'role_type', 'scope'),
        Index('idx_user_permissions_expires_status', 'expires_at', 'status'),
        Index('idx_user_permissions_granted_approved', 'granted_at', 'approved_at'),
        Index('idx_user_permissions_team_role', 'team_id', 'team_role'),
        Index('idx_user_permissions_risk_compliance', 'risk_level', 'compliance_requirements'),
        Index('idx_user_permissions_usage_limits', 'usage_count', 'usage_limit'),
        Index('idx_user_permissions_last_used', 'last_used_at'),
        Index('idx_user_permissions_delegated', 'is_delegated', 'delegated_from_user_id'),
    )
    
    def __repr__(self):
        return f"<UserPermissions(id={self.id}, user_id={self.user_id}, permission={self.permission_type.value}, resource={self.resource_type.value})>"
    
    @classmethod
    def grant_permission(
        cls,
        user_id: str,
        permission_type: PermissionType,
        resource_type: ResourceType,
        granted_by: str,
        resource_id: str = None,
        **kwargs
    ) -> 'UserPermissions':
        """Grant a permission to a user"""



        return cls(
            user_id=user_id,
            permission_type=permission_type,
            resource_type=resource_type,
            resource_id=resource_id,
            granted_by=granted_by,
            name=f"{permission_type.value} on {resource_type.value}",
            permission_id=f"perm_{uuid.uuid4().hex[:12]}",
            created_by=granted_by,
            **kwargs
        )
    
    @classmethod
    def grant_role(
        cls,
        user_id: str,
        role_type: RoleType,
        scope: PermissionScope,
        granted_by: str,
        **kwargs
    ) -> 'UserPermissions':
        """Grant a role to a user"""



        return cls(
            user_id=user_id,
            role_type=role_type,
            permission_type=PermissionType.ADMIN,  # Roles typically have admin-level permissions
            resource_type=ResourceType.PLATFORM_ADMIN,
            scope=scope,
            granted_by=granted_by,
            name=f"{role_type.value} role",
            permission_id=f"role_{uuid.uuid4().hex[:12]}",
            created_by=granted_by,
            **kwargs
        )
    
    def is_expired(self) -> bool:
        """Check if permission is expired"""
        if not self.expires_at:
            return False
        return datetime.now(timezone.utc) >= self.expires_at
    
    def is_active(self) -> bool:
        """Check if permission is currently active"""



        return (
            self.status == PermissionStatus.ACTIVE and
            not self.is_expired() and
            not self.is_usage_limit_exceeded()
        )
    
    def is_usage_limit_exceeded(self) -> bool:
        """Check if usage limit is exceeded"""
        if self.usage_limit and self.usage_count >= self.usage_limit:
            return True
        
        if self.daily_usage_limit:
            # Check daily usage (simplified implementation)
            return False  # Would need proper daily tracking
        
        if self.monthly_usage_limit:
            # Check monthly usage (simplified implementation)
            return False  # Would need proper monthly tracking
        
        return False
    
    def can_access_from_ip(self, ip_address: str) -> bool:
        """Check if access is allowed from given IP address"""
        if self.ip_blacklist and ip_address in self.ip_blacklist:
            return False
        
        if self.ip_whitelist and ip_address not in self.ip_whitelist:
            return False
        
        return True
    
    def can_access_at_time(self, check_time: datetime = None) -> bool:
        """Check if access is allowed at given time"""
        if not self.time_restrictions:
            return True
        
        if check_time is None:
            check_time = datetime.now(timezone.utc)
        
        allowed_days = self.time_restrictions.get('days', [])
        allowed_hours = self.time_restrictions.get('hours', [])
        
        if allowed_days and check_time.weekday() not in allowed_days:
            return False
        
        if allowed_hours and check_time.hour not in range(allowed_hours[0], allowed_hours[1] + 1):
            return False
        
        return True
    
    def record_usage(self, context: Dict[str, Any] = None) -> None:
        """Record permission usage"""
        self.usage_count += 1
        self.current_usage_count += 1
        self.last_used_at = datetime.now(timezone.utc)
        
        # Reset rate limit counter if needed
        if self.rate_limit_reset_at and datetime.now(timezone.utc) >= self.rate_limit_reset_at:
            self.current_usage_count = 1
            self.rate_limit_reset_at = datetime.now(timezone.utc) + timedelta(hours=1)
        
        # Update metadata with usage context
        if context:
            if not self.metadata:
                self.metadata = {}
            
            self.metadata['last_usage'] = {
                'timestamp': datetime.now(timezone.utc).isoformat(),
                'context': context
            }
    
    def check_rate_limit(self) -> bool:
        """Check if rate limit allows current request"""
        now = datetime.now(timezone.utc)
        
        # Reset counter if time window has passed
        if self.rate_limit_reset_at and now >= self.rate_limit_reset_at:
            self.current_usage_count = 0
            self.rate_limit_reset_at = now + timedelta(hours=1)
        
        # Check hourly limit
        if self.rate_limit_per_hour and self.current_usage_count >= self.rate_limit_per_hour:
            return False
        
        # Check daily limit
        if self.rate_limit_per_day:
            # Simplified check - in production, would need proper daily tracking
            pass
        
        return True
    
    def extend_expiration(self, additional_days: int, extended_by: str) -> None:
        """Extend permission expiration"""
        if self.expires_at:
            self.expires_at += timedelta(days=additional_days)
        else:
            self.expires_at = datetime.now(timezone.utc) + timedelta(days=additional_days)
        
        self.updated_by = extended_by
        self.updated_at = datetime.now(timezone.utc)
        
        # Log extension in metadata
        if not self.metadata:
            self.metadata = {}
        
        if 'extensions' not in self.metadata:
            self.metadata['extensions'] = []
        
        self.metadata['extensions'].append({
            'extended_by': extended_by,
            'extended_at': datetime.now(timezone.utc).isoformat(),
            'additional_days': additional_days,
            'new_expiration': self.expires_at.isoformat()
        })
    
    def revoke_permission(self, revoked_by: str, reason: str = None) -> None:
        """Revoke the permission"""
        self.status = PermissionStatus.REVOKED
        self.revoked_by = revoked_by
        self.revoked_at = datetime.now(timezone.utc)
        self.revocation_reason = reason
        self.updated_by = revoked_by
        self.updated_at = datetime.now(timezone.utc)
    
    def delegate_permission(self, to_user_id: str, delegated_by: str, expires_in_hours: int = 24) -> 'UserPermissions':
        """Delegate permission to another user"""
        if not self.can_delegate:
            raise ValueError("This permission cannot be delegated")
        
        delegated_permission = UserPermissions(
            user_id=to_user_id,
            permission_type=self.permission_type,
            resource_type=self.resource_type,
            resource_id=self.resource_id,
            scope=self.scope,
            access_level=self.access_level,
            name=f"Delegated: {self.name}",
            description=f"Delegated from user {self.user_id}",
            is_delegated=True,
            delegated_from_user_id=self.user_id,
            expires_at=datetime.now(timezone.utc) + timedelta(hours=expires_in_hours),
            granted_by=delegated_by,
            permission_id=f"delegated_{uuid.uuid4().hex[:12]}",
            created_by=delegated_by
        )
        
        return delegated_permission
    
    def get_effective_permissions(self) -> Set[str]:
        """Get all effective permissions including inherited ones"""
        permissions = {f"{self.permission_type.value}:{self.resource_type.value}"}
        
        # Add inherited permissions
        if self.inherited_permissions:
            for perm in self.inherited_permissions.get('permissions', []):
                permissions.add(perm)
        
        # Add role-based permissions
        if self.role_type:
            role_permissions = self._get_role_permissions(self.role_type)
            permissions.update(role_permissions)
        
        return permissions
    
    def _get_role_permissions(self, role: RoleType) -> Set[str]:
        """Get permissions associated with a role"""
        role_permissions = {
            RoleType.SUPER_ADMIN: {
                "admin:platform_admin", "read:*", "write:*", "delete:*", "create:*"
            },
            RoleType.ADMIN: {
                "admin:user_profile", "admin:content", "read:analytics", "write:content"
            },
            RoleType.CREATOR: {
                "create:content", "read:content", "write:content", "read:analytics"
            },
            RoleType.VIEWER: {
                "read:content", "read:user_profile"
            }
        }
        
        return role_permissions.get(role, set())
    
    def get_permission_summary(self) -> Dict[str, Any]:
        """Get comprehensive permission summary"""



        return {
            'permission_info': {
                'id': str(self.id),
                'permission_type': self.permission_type.value,
                'resource_type': self.resource_type.value,
                'resource_id': self.resource_id,
                'access_level': self.access_level.value,
                'scope': self.scope.value
            },
            'status': {
                'current_status': self.status.value,
                'is_active': self.is_active(),
                'is_expired': self.is_expired(),
                'expires_at': self.expires_at.isoformat() if self.expires_at else None
            },
            'usage': {
                'usage_count': self.usage_count,
                'usage_limit': self.usage_limit,
                'last_used_at': self.last_used_at.isoformat() if self.last_used_at else None,
                'rate_limit_remaining': (self.rate_limit_per_hour or 0) - self.current_usage_count
            },
            'restrictions': {
                'ip_restrictions': bool(self.ip_whitelist or self.ip_blacklist),
                'time_restrictions': bool(self.time_restrictions),
                'geographic_restrictions': bool(self.geographic_restrictions),
                'mfa_required': self.mfa_required
            },
            'delegation': {
                'is_delegated': self.is_delegated,
                'can_delegate': self.can_delegate,
                'delegated_from': str(self.delegated_from_user_id) if self.delegated_from_user_id else None
            }
        }
