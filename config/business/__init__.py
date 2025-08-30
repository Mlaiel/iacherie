"""
Business Configuration Module for IA-Influencer Agent Platform
==============================================================

Professional business logic and workflow configuration management.
Comprehensive enterprise-grade configuration system for multi-format content platform.

Author: Fahed Mlaiel <mlaiel@live.de>
Project: IA-Influencer Agent + Content Protection Platform
Team: Lead Dev IA + Backend Senior + ML Engineer + DBA + Security + Microservices + Audio + DevOps

⚠️  INTELLECTUAL PROPERTY WARNING ⚠️
=====================================
This code is the exclusive intellectual property of Fahed Mlaiel (mlaiel@live.de).
Any unauthorized use, copying, modification, or distribution of this code
without explicit written permission from Fahed Mlaiel is STRICTLY PROHIBITED
and will result in immediate legal action under German and International law.

For licensing, collaboration, or business inquiries:
📧 Contact: mlaiel@live.de
🌐 Official Project: IA-Influencer Agent Platform
"""

# Import all business configuration modules
from .workflow_config import (
    WorkflowConfig,
    ContentType,
    WorkflowStage,
    ProcessingPriority,
    StageConfiguration
)

from .tenant_config import (
    TenantConfig,
    TenantTier,
    TenantStatus,
    IsolationLevel,
    RegionCode,
    ResourceLimits,
    FeatureAccess
)

from .user_roles_config import (
    UserRolesConfig,
    UserRole,
    Permission,
    ResourceType,
    PermissionScope,
    RoleDefinition
)

from .content_lifecycle_config import (
    ContentLifecycleConfig,
    ContentStatus,
    ContentEvent,
    ContentPriority,
    ContentCategory,
    StateTransition,
    ContentMetadata
)

from .collaboration_config import (
    CollaborationConfig,
    CollaborationType,
    CollaborationStatus,
    MatchingCriteria,
    RevenueShareModel,
    CollaborationTerms,
    CreatorProfile
)

from .notification_config import (
    NotificationConfig,
    NotificationType,
    NotificationChannel,
    NotificationPriority,
    NotificationFrequency,
    NotificationTemplate,
    NotificationRule
)

from .feature_flags_config import (
    FeatureFlagsConfig,
    FeatureState,
    RolloutStrategy,
    FeatureCategory,
    FeatureEnvironment,
    FeatureFlag,
    ABTestConfig
)

from .compliance_config import (
    ComplianceConfig,
    ComplianceStandard,
    DataCategory,
    ProcessingPurpose,
    RetentionPeriod,
    DataProcessingRecord,
    ConsentRecord,
    CompliancePolicy
)

# Import new advanced business configuration modules
from .advanced_monetization_config import (
    AdvancedMonetizationConfig,
    advanced_monetization_config,
    RevenueStream,
    PaymentMethod,
    PricingTier,
    RevenueStreamConfig,
    PlatformCommissionConfig,
    PayoutConfig,
    get_revenue_stream_config,
    get_pricing_tier_config,
    calculate_creator_payout
)

from .content_management_config import (
    ContentManagementConfig,
    content_management_config,
    ContentType as CMContentType,
    ContentStatus as CMContentStatus,
    QualityLevel,
    ProcessingPriority as CMProcessingPriority,
    ContentFormatConfig,
    ContentProcessingPipeline,
    ContentMetadata as CMContentMetadata,
    get_content_format_config,
    get_content_processing_pipeline,
    validate_content_upload
)

# Export all classes and enums for external use
__all__ = [
    # Main configuration classes
    'WorkflowConfig',
    'TenantConfig', 
    'UserRolesConfig',
    'ContentLifecycleConfig',
    'CollaborationConfig',
    'NotificationConfig',
    'FeatureFlagsConfig',
    'ComplianceConfig',
    
    # Workflow related
    'ContentType',
    'WorkflowStage', 
    'ProcessingPriority',
    'StageConfiguration',
    
    # Tenant related
    'TenantTier',
    'TenantStatus',
    'IsolationLevel',
    'RegionCode',
    'ResourceLimits',
    'FeatureAccess',
    
    # User roles related
    'UserRole',
    'Permission',
    'ResourceType',
    'PermissionScope',
    'RoleDefinition',
    
    # Content lifecycle related
    'ContentStatus',
    'ContentEvent',
    'ContentPriority',
    'ContentCategory',
    'StateTransition',
    'ContentMetadata',
    
    # Collaboration related
    'CollaborationType',
    'CollaborationStatus',
    'MatchingCriteria',
    'RevenueShareModel',
    'CollaborationTerms',
    'CreatorProfile',
    
    # Notification related
    'NotificationType',
    'NotificationChannel',
    'NotificationPriority',
    'NotificationFrequency',
    'NotificationTemplate',
    'NotificationRule',
    
    # Feature flags related
    'FeatureState',
    'RolloutStrategy',
    'FeatureCategory',
    'FeatureEnvironment',
    'FeatureFlag',
    'ABTestConfig',
    
    # Compliance related
    'ComplianceStandard',
    'DataCategory',
    'ProcessingPurpose',
    'RetentionPeriod',
    'DataProcessingRecord',
    'ConsentRecord',
    'CompliancePolicy'
]

# Business configuration version and metadata
__version__ = "2.0.0"
__author__ = "Fahed Mlaiel <mlaiel@live.de>"
__description__ = "Enterprise business configuration system for IA-Influencer Agent Platform"
__copyright__ = "© 2025 Fahed Mlaiel. All rights reserved."
