"""
Core interfaces module for IA Influencer Agent with Content Protection.

This module defines the foundational interfaces for:
- Content processing and protection
- AI agent interactions
- Multi-format content handling
- Monetization and collaboration systems
- Platform integrations

Author: Fahed Mlaiel <mlaiel@live.de>
Project: IA Influencer Agent - Industrial Content Protection Platform
© 2025 - All rights reserved. Unauthorized use, copying, or distribution prohibited.
"""

from .content_interfaces import (
    ContentProcessorInterface,
    ContentProtectionInterface,
    ContentFingerprinterInterface,
    ContentValidatorInterface,
    ContentMetadataInterface
)

from .ai_interfaces import (
    AIAgentInterface,
    AIProcessorInterface,
    AIRecommendationInterface,
    AIAnalyticsInterface,
    AIGenerationInterface
)

from .platform_interfaces import (
    PlatformConnectorInterface,
    PlatformAuthInterface,
    PlatformDataInterface,
    PlatformDistributionInterface,
    PlatformMonetizationInterface
)

from .user_interfaces import (
    UserManagerInterface,
    UserPreferencesInterface,
    UserCollaborationInterface,
    UserSecurityInterface,
    UserAnalyticsInterface
)

from .monetization_interfaces import (
    RevenueTrackerInterface,
    PaymentProcessorInterface,
    LicensingInterface,
    RevenueSharingInterface,
    FinancialReportingInterface
)

from .collaboration_interfaces import (
    CollaborationMatchingInterface,
    ProjectManagerInterface,
    CommunicationInterface,
    ContractManagerInterface,
    TeamworkInterface
)

from .security_interfaces import (
    SecurityManagerInterface,
    AuthenticationInterface,
    AuthorizationInterface,
    EncryptionInterface,
    AuditInterface
)

from .monitoring_interfaces import (
    MonitoringInterface,
    AlertManagerInterface,
    PerformanceTrackerInterface,
    SystemHealthInterface,
    ComplianceMonitorInterface
)

from .storage_interfaces import (
    StorageInterface,
    DatabaseInterface,
    CacheInterface,
    FileSystemInterface,
    BackupInterface
)

from .integration_interfaces import (
    ThirdPartyIntegrationInterface,
    APIClientInterface,
    WebhookInterface,
    DataSyncInterface,
    MigrationInterface
)

__all__ = [
    # Content Interfaces
    "ContentProcessorInterface",
    "ContentProtectionInterface", 
    "ContentFingerprinterInterface",
    "ContentValidatorInterface",
    "ContentMetadataInterface",
    
    # AI Interfaces
    "AIAgentInterface",
    "AIProcessorInterface",
    "AIRecommendationInterface",
    "AIAnalyticsInterface",
    "AIGenerationInterface",
    
    # Platform Interfaces
    "PlatformConnectorInterface",
    "PlatformAuthInterface",
    "PlatformDataInterface",
    "PlatformDistributionInterface",
    "PlatformMonetizationInterface",
    
    # User Interfaces
    "UserManagerInterface",
    "UserPreferencesInterface",
    "UserCollaborationInterface",
    "UserSecurityInterface",
    "UserAnalyticsInterface",
    
    # Monetization Interfaces
    "RevenueTrackerInterface",
    "PaymentProcessorInterface",
    "LicensingInterface",
    "RevenueSharingInterface",
    "FinancialReportingInterface",
    
    # Collaboration Interfaces
    "CollaborationMatchingInterface",
    "ProjectManagerInterface",
    "CommunicationInterface",
    "ContractManagerInterface",
    "TeamworkInterface",
    
    # Security Interfaces
    "SecurityManagerInterface",
    "AuthenticationInterface",
    "AuthorizationInterface",
    "EncryptionInterface",
    "AuditInterface",
    
    # Monitoring Interfaces
    "MonitoringInterface",
    "AlertManagerInterface",
    "PerformanceTrackerInterface",
    "SystemHealthInterface",
    "ComplianceMonitorInterface",
    
    # Storage Interfaces
    "StorageInterface",
    "DatabaseInterface",
    "CacheInterface",
    "FileSystemInterface",
    "BackupInterface",
    
    # Integration Interfaces
    "ThirdPartyIntegrationInterface",
    "APIClientInterface",
    "WebhookInterface",
    "DataSyncInterface",
    "MigrationInterface"
]
