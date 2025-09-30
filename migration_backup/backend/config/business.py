"""Business Configuration Module - Consolidated Business Configs
=============================================================

Consolidates all business-related configurations from:
- config/business/ (26 files)

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, field
from enum import Enum
from decimal import Decimal

# ===== WORKFLOW CONFIGURATION =====

class ContentType(str, Enum):
    """Content types"""
    AUDIO = "audio"
    VIDEO = "video"
    IMAGE = "image"
    TEXT = "text"
    DOCUMENT = "document"
    PODCAST = "podcast"
    LIVESTREAM = "livestream"

class WorkflowStage(str, Enum):
    """Workflow stages"""
    UPLOAD = "upload"
    VALIDATION = "validation"
    ANALYSIS = "analysis"
    FINGERPRINTING = "fingerprinting"
    PROTECTION = "protection"
    MONETIZATION = "monetization"
    DISTRIBUTION = "distribution"
    MONITORING = "monitoring"

class ProcessingPriority(str, Enum):
    """Processing priorities"""
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"

@dataclass
class StageConfiguration:
    """Workflow stage configuration"""
    stage: WorkflowStage
    enabled: bool = True
    timeout_minutes: int = 60
    retry_attempts: int = 3
    auto_proceed: bool = True
    requires_approval: bool = False
    notification_enabled: bool = True

@dataclass
class WorkflowConfig:
    """Content workflow configuration"""
    enabled: bool = True
    default_priority: ProcessingPriority = ProcessingPriority.NORMAL
    stages: List[StageConfiguration] = field(default_factory=list)
    parallel_processing: bool = True
    max_concurrent_jobs: int = 10
    queue_processing: bool = True
    workflow_timeout_hours: int = 24
    error_handling_strategy: str = "retry_with_escalation"

# ===== TENANT CONFIGURATION =====

class TenantTier(str, Enum):
    """Tenant tiers"""
    FREE = "free"
    BASIC = "basic"
    PREMIUM = "premium"
    ENTERPRISE = "enterprise"

class TenantStatus(str, Enum):
    """Tenant status"""
    ACTIVE = "active"
    SUSPENDED = "suspended"
    TRIAL = "trial"
    EXPIRED = "expired"

class IsolationLevel(str, Enum):
    """Data isolation levels"""
    SHARED = "shared"
    DEDICATED_SCHEMA = "dedicated_schema"
    DEDICATED_DATABASE = "dedicated_database"
    DEDICATED_INSTANCE = "dedicated_instance"

@dataclass
class ResourceLimits:
    """Tenant resource limits"""
    max_storage_gb: int = 10
    max_uploads_per_month: int = 100
    max_api_calls_per_hour: int = 1000
    max_concurrent_jobs: int = 5
    max_team_members: int = 10
    max_projects: int = 5

@dataclass
class FeatureAccess:
    """Feature access configuration"""
    ai_analysis: bool = True
    advanced_fingerprinting: bool = False
    real_time_monitoring: bool = False
    custom_branding: bool = False
    api_access: bool = True
    bulk_operations: bool = False
    priority_support: bool = False

@dataclass
class TenantConfig:
    """Multi-tenant configuration"""
    enabled: bool = True
    isolation_level: IsolationLevel = IsolationLevel.SHARED
    default_tier: TenantTier = TenantTier.FREE
    auto_provisioning: bool = True
    tenant_subdomain: bool = True
    custom_domains: bool = False
    resource_limits: Dict[TenantTier, ResourceLimits] = field(default_factory=dict)
    feature_access: Dict[TenantTier, FeatureAccess] = field(default_factory=dict)

# ===== USER ROLES CONFIGURATION =====

class UserRole(str, Enum):
    """User roles"""
    OWNER = "owner"
    ADMIN = "admin"
    CREATOR = "creator"
    COLLABORATOR = "collaborator"
    VIEWER = "viewer"
    GUEST = "guest"

class Permission(str, Enum):
    """System permissions"""
    CREATE_CONTENT = "create_content"
    EDIT_CONTENT = "edit_content"
    DELETE_CONTENT = "delete_content"
    VIEW_CONTENT = "view_content"
    MANAGE_USERS = "manage_users"
    MANAGE_BILLING = "manage_billing"
    MANAGE_INTEGRATIONS = "manage_integrations"
    VIEW_ANALYTICS = "view_analytics"
    EXPORT_DATA = "export_data"

@dataclass
class RoleDefinition:
    """Role definition with permissions"""
    role: UserRole
    permissions: List[Permission]
    can_invite_users: bool = False
    max_content_uploads: int = 100
    access_to_premium_features: bool = False

@dataclass
class UserRolesConfig:
    """User roles and permissions configuration"""
    enabled: bool = True
    default_role: UserRole = UserRole.CREATOR
    role_definitions: List[RoleDefinition] = field(default_factory=list)
    permission_inheritance: bool = True
    role_based_pricing: bool = False
    custom_roles_allowed: bool = False

# ===== CONTENT LIFECYCLE CONFIGURATION =====

class ContentStatus(str, Enum):
    """Content lifecycle status"""
    DRAFT = "draft"
    PENDING = "pending"
    PROCESSING = "processing"
    ACTIVE = "active"
    PROTECTED = "protected"
    MONETIZED = "monetized"
    ARCHIVED = "archived"
    DELETED = "deleted"

class ContentEvent(str, Enum):
    """Content lifecycle events"""
    UPLOADED = "uploaded"
    ANALYZED = "analyzed"
    FINGERPRINTED = "fingerprinted"
    PROTECTED = "protected"
    MONETIZED = "monetized"
    DISTRIBUTED = "distributed"
    INFRINGEMENT_DETECTED = "infringement_detected"

@dataclass
class StateTransition:
    """Content state transition rule"""
    from_status: ContentStatus
    to_status: ContentStatus
    trigger_event: ContentEvent
    auto_transition: bool = True
    requires_approval: bool = False
    notification_enabled: bool = True

@dataclass
class ContentLifecycleConfig:
    """Content lifecycle management configuration"""
    enabled: bool = True
    auto_archival_days: int = 365
    auto_deletion_days: int = 1095  # 3 years
    version_control: bool = True
    max_versions: int = 10
    state_transitions: List[StateTransition] = field(default_factory=list)
    audit_trail: bool = True
    retention_policies: Dict[ContentType, int] = field(default_factory=dict)

# ===== COLLABORATION CONFIGURATION =====

class CollaborationType(str, Enum):
    """Types of collaboration"""
    REMIX = "remix"
    COVER = "cover"
    FEATURE = "feature"
    SAMPLE = "sample"
    MASHUP = "mashup"
    ORIGINAL = "original"

class CollaborationStatus(str, Enum):
    """Collaboration status"""
    PROPOSED = "proposed"
    ACCEPTED = "accepted"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    REJECTED = "rejected"
    CANCELLED = "cancelled"

@dataclass
class MatchingCriteria:
    """Collaboration matching criteria"""
    content_similarity_threshold: float = 0.8
    genre_matching: bool = True
    location_proximity: bool = False
    follower_count_range: tuple = (0, 1000000)
    collaboration_history: bool = True
    rating_threshold: float = 4.0

@dataclass
class RevenueShareModel:
    """Revenue sharing model for collaborations"""
    original_creator_percentage: float = 60.0
    collaborator_percentage: float = 35.0
    platform_fee_percentage: float = 5.0
    minimum_payout: Decimal = Decimal("10.00")
    payout_frequency: str = "monthly"

@dataclass
class CollaborationConfig:
    """Collaboration system configuration"""
    enabled: bool = True
    auto_matching: bool = True
    matching_criteria: MatchingCriteria = field(default_factory=MatchingCriteria)
    revenue_share: RevenueShareModel = field(default_factory=RevenueShareModel)
    collaboration_timeout_days: int = 30
    contract_templates: bool = True
    dispute_resolution: bool = True
    rating_system: bool = True

# ===== NOTIFICATION CONFIGURATION =====

class NotificationType(str, Enum):
    """Notification types"""
    CONTENT_UPLOADED = "content_uploaded"
    ANALYSIS_COMPLETE = "analysis_complete"
    INFRINGEMENT_DETECTED = "infringement_detected"
    COLLABORATION_REQUEST = "collaboration_request"
    PAYMENT_RECEIVED = "payment_received"
    SYSTEM_ALERT = "system_alert"

class NotificationChannel(str, Enum):
    """Notification channels"""
    EMAIL = "email"
    SMS = "sms"
    PUSH = "push"
    IN_APP = "in_app"
    WEBHOOK = "webhook"

@dataclass
class NotificationRule:
    """Notification rule configuration"""
    notification_type: NotificationType
    channels: List[NotificationChannel]
    enabled: bool = True
    priority: str = "normal"  # low, normal, high, urgent
    template: Optional[str] = None
    frequency_limit: Optional[int] = None  # max per hour

@dataclass
class NotificationConfig:
    """Notification system configuration"""
    enabled: bool = True
    default_channels: List[NotificationChannel] = field(default_factory=lambda: [
        NotificationChannel.EMAIL,
        NotificationChannel.IN_APP
    ])
    rules: List[NotificationRule] = field(default_factory=list)
    batch_notifications: bool = True
    quiet_hours_enabled: bool = True
    quiet_hours_start: str = "22:00"
    quiet_hours_end: str = "08:00"

# ===== FEATURE FLAGS CONFIGURATION =====

@dataclass
class FeatureFlag:
    """Feature flag definition"""
    name: str
    enabled: bool = False
    description: str = ""
    rollout_percentage: float = 0.0
    target_users: List[str] = field(default_factory=list)
    target_tiers: List[TenantTier] = field(default_factory=list)
    start_date: Optional[str] = None
    end_date: Optional[str] = None

@dataclass
class FeatureFlagsConfig:
    """Feature flags configuration"""
    enabled: bool = True
    flags: List[FeatureFlag] = field(default_factory=list)
    evaluation_interval: int = 300  # 5 minutes
    cache_enabled: bool = True
    fallback_enabled: bool = True
    logging_enabled: bool = True

# ===== COMPLIANCE CONFIGURATION =====

class ComplianceStandard(str, Enum):
    """Compliance standards"""
    GDPR = "gdpr"
    CCPA = "ccpa"
    COPPA = "coppa"
    DMCA = "dmca"
    SOX = "sox"
    HIPAA = "hipaa"

@dataclass
class CompliancePolicy:
    """Compliance policy configuration"""
    standard: ComplianceStandard
    enabled: bool = True
    data_retention_days: int = 2555  # 7 years
    data_deletion_policy: str = "automatic"
    consent_required: bool = True
    audit_logging: bool = True
    regular_reviews: bool = True

@dataclass
class ComplianceConfig:
    """Compliance management configuration"""
    enabled: bool = True
    policies: List[CompliancePolicy] = field(default_factory=list)
    privacy_by_design: bool = True
    data_minimization: bool = True
    consent_management: bool = True
    right_to_deletion: bool = True
    data_portability: bool = True
    breach_notification: bool = True

# ===== MAIN BUSINESS CONFIGURATION =====

@dataclass
class BusinessConfig:
    """Main business configuration"""
    workflow: WorkflowConfig = field(default_factory=WorkflowConfig)
    tenant: TenantConfig = field(default_factory=TenantConfig)
    user_roles: UserRolesConfig = field(default_factory=UserRolesConfig)
    content_lifecycle: ContentLifecycleConfig = field(default_factory=ContentLifecycleConfig)
    collaboration: CollaborationConfig = field(default_factory=CollaborationConfig)
    notifications: NotificationConfig = field(default_factory=NotificationConfig)
    feature_flags: FeatureFlagsConfig = field(default_factory=FeatureFlagsConfig)
    compliance: ComplianceConfig = field(default_factory=ComplianceConfig)
    business_hours: str = "09:00-17:00"
    timezone: str = "UTC"
    support_email: str = "support@ia-influencer.com"

# ===== ENVIRONMENT-SPECIFIC CONFIGURATIONS =====

def get_development_business_config() -> BusinessConfig:
    """Get development business configuration"""
    return BusinessConfig(
        tenant=TenantConfig(
            isolation_level=IsolationLevel.SHARED,
            auto_provisioning=True
        ),
        feature_flags=FeatureFlagsConfig(
            enabled=True,
            flags=[
                FeatureFlag(name="beta_features", enabled=True, rollout_percentage=100.0)
            ]
        ),
        compliance=ComplianceConfig(
            enabled=False  # Simplified compliance in dev
        )
    )

def get_production_business_config() -> BusinessConfig:
    """Get production business configuration"""
    return BusinessConfig(
        tenant=TenantConfig(
            isolation_level=IsolationLevel.DEDICATED_SCHEMA,
            auto_provisioning=False  # Manual approval in production
        ),
        feature_flags=FeatureFlagsConfig(
            enabled=True,
            flags=[
                FeatureFlag(name="advanced_analytics", enabled=True, rollout_percentage=50.0),
                FeatureFlag(name="ai_recommendations", enabled=False, rollout_percentage=10.0)
            ]
        ),
        compliance=ComplianceConfig(
            enabled=True,
            policies=[
                CompliancePolicy(standard=ComplianceStandard.GDPR, enabled=True),
                CompliancePolicy(standard=ComplianceStandard.DMCA, enabled=True)
            ]
        )
    )

def get_testing_business_config() -> BusinessConfig:
    """Get testing business configuration"""
    return BusinessConfig(
        tenant=TenantConfig(
            enabled=False  # Single tenant in testing
        ),
        feature_flags=FeatureFlagsConfig(
            enabled=False
        ),
        compliance=ComplianceConfig(
            enabled=False
        ),
        notifications=NotificationConfig(
            enabled=False  # No notifications in testing
        )
    )

# ===== BUSINESS CONFIGURATION FACTORY =====

class BusinessConfigurationFactory:
    """Factory for creating business configurations"""
    
    @staticmethod
    def create_config(environment: str = "development") -> BusinessConfig:
        """Create business configuration for environment"""
        if environment.lower() == "production":
            return get_production_business_config()
        elif environment.lower() == "testing":
            return get_testing_business_config()
        else:
            return get_development_business_config()

# Export all business configurations
__all__ = [
    # Enums
    "ContentType",
    "WorkflowStage",
    "ProcessingPriority",
    "TenantTier",
    "TenantStatus",
    "IsolationLevel",
    "UserRole",
    "Permission",
    "ContentStatus",
    "ContentEvent",
    "CollaborationType",
    "CollaborationStatus",
    "NotificationType",
    "NotificationChannel",
    "ComplianceStandard",
    
    # Configuration Classes
    "StageConfiguration",
    "WorkflowConfig",
    "ResourceLimits",
    "FeatureAccess",
    "TenantConfig",
    "RoleDefinition",
    "UserRolesConfig",
    "StateTransition",
    "ContentLifecycleConfig",
    "MatchingCriteria",
    "RevenueShareModel",
    "CollaborationConfig",
    "NotificationRule",
    "NotificationConfig",
    "FeatureFlag",
    "FeatureFlagsConfig",
    "CompliancePolicy",
    "ComplianceConfig",
    "BusinessConfig",
    
    # Factory and Functions
    "BusinessConfigurationFactory",
    "get_development_business_config",
    "get_production_business_config",
    "get_testing_business_config"
]