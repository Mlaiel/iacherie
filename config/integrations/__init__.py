"""Integrations Configuration Module for IA-Influencer Agent Platform
==================================================================

Professional third-party integrations configuration management for the complete
IA-Influencer Agent + Content Protection Platform ecosystem.

This module provides comprehensive configuration management for:
- OAuth2 authentication with multiple platforms (Spotify, YouTube, Instagram, TikTok, etc.)
- API client configurations with rate limiting and error handling
- Webhook management for real-time notifications and events
- External services integration (cloud storage, vector databases, payment processing)
- Data synchronization across platforms and services
- Advanced monitoring and alerting for all integrations
- Professional rate limiting with adaptive strategies

Author: Fahed Mlaiel <mlaiel@live.de>
Project: IA-Influencer Agent + Content Protection Platform
Team: Lead Dev IA + Backend Senior + ML Engineer + DBA + Security + Microservices + Audio + DevOps

WARNING: This code is the intellectual property of Fahed Mlaiel.
Any unauthorized use, reproduction, or distribution of this code without explicit 
written permission from the author is strictly prohibited and will be prosecuted 
to the full extent of the law.

Contact: mlaiel@live.de for licensing inquiries.
"""
# Core integration configurations
from .oauth_config import (
    OAuthConfig, 
    OAuthProvider, 
    OAuthScope, 
    OAuthEndpoints, 
    OAuthManager,
    oauth_config,
    oauth_manager
)

from .api_client_config import (
    APIClientConfig,
    APIProvider,
    RateLimitConfig,
    TimeoutConfig,
    APIEndpoints,
    APIClientManager,
    api_client_config,
    api_client_manager
)

from .webhook_config import (
    WebhookConfig,
    WebhookProvider,
    WebhookEvent,
    WebhookSecurity,
    WebhookRetry,
    WebhookEndpoints,
    WebhookManager,
    webhook_config,
    webhook_manager
)

from .webhook_handlers_config import (
    WebhookHandlersConfig,
    HandlerPriority,
    HandlerStatus,
    HandlerResult,
    HandlerConfig,
    WebhookHandlerRegistry,
    DefaultHandlerConfigs,
    webhook_handlers_config,
    webhook_handler_registry
)

from .external_services_config import (
    ExternalServicesConfig,
    ServiceCategory,
    ServiceProvider,
    ServiceHealthConfig,
    ServiceLimits,
    ExternalServiceManager,
    external_services_config,
    external_service_manager
)

from .data_sync_config import (
    DataSyncConfig,
    SyncDirection,
    SyncStrategy,
    ConflictResolution,
    SyncStatus,
    DataSource,
    SyncMetrics,
    SyncMapping,
    SyncFilter,
    DataSyncManager,
    data_sync_config,
    data_sync_manager
)

from .integration_monitoring_config import (
    IntegrationMonitoringConfig,
    MonitoringLevel,
    AlertSeverity,
    MetricType,
    HealthStatus,
    HealthCheckConfig,
    MetricConfig,
    AlertRule,
    MonitoringManager,
    integration_monitoring_config,
    monitoring_manager
)

from .rate_limiting_config import (
    RateLimitingConfig,
    RateLimitStrategy,
    RateLimitScope,
    RateLimitAction,
    PriorityLevel,
    RateLimitRule,
    QuotaConfig,
    BackoffConfig,
    RateLimitManager,
    rate_limiting_config,
    rate_limit_manager
)

# Convenience imports for backward compatibility
WebhookConfig = WebhookConfig
OAuthConfig = OAuthConfig
APIClientConfig = APIClientConfig
WebhookHandlersConfig = WebhookHandlersConfig
ExternalServicesConfig = ExternalServicesConfig
DataSyncConfig = DataSyncConfig
IntegrationMonitoringConfig = IntegrationMonitoringConfig
RateLimitingConfig = RateLimitingConfig

__all__ = [
    # Configuration classes
    'OAuthConfig',
    'APIClientConfig',
    'WebhookConfig',
    'WebhookHandlersConfig',
    'ExternalServicesConfig',
    'DataSyncConfig',
    'IntegrationMonitoringConfig',
    'RateLimitingConfig',
    
    # Enums and types
    'OAuthProvider',
    'OAuthScope',
    'APIProvider',
    'WebhookProvider',
    'WebhookEvent',
    'HandlerPriority',
    'HandlerStatus',
    'ServiceCategory',
    'ServiceProvider',
    'SyncDirection',
    'SyncStrategy',
    'ConflictResolution',
    'SyncStatus',
    'DataSource',
    'MonitoringLevel',
    'AlertSeverity',
    'MetricType',
    'HealthStatus',
    'RateLimitStrategy',
    'RateLimitScope',
    'RateLimitAction',
    'PriorityLevel',
    
    # Data classes and configurations
    'RateLimitConfig',
    'TimeoutConfig',
    'WebhookSecurity',
    'WebhookRetry',
    'HandlerResult',
    'HandlerConfig',
    'ServiceHealthConfig',
    'ServiceLimits',
    'SyncMetrics',
    'SyncMapping',
    'SyncFilter',
    'HealthCheckConfig',
    'MetricConfig',
    'AlertRule',
    'RateLimitRule',
    'QuotaConfig',
    'BackoffConfig',
    
    # Managers and utilities
    'OAuthManager',
    'APIClientManager',
    'WebhookManager',
    'WebhookHandlerRegistry',
    'DefaultHandlerConfigs',
    'ExternalServiceManager',
    'DataSyncManager',
    'MonitoringManager',
    'RateLimitManager',
    
    # Endpoints and helpers
    'OAuthEndpoints',
    'APIEndpoints',
    'WebhookEndpoints',
    
    # Global instances
    'oauth_config',
    'oauth_manager',
    'api_client_config',
    'api_client_manager',
    'webhook_config',
    'webhook_manager',
    'webhook_handlers_config',
    'webhook_handler_registry',
    'external_services_config',
    'external_service_manager',
    'data_sync_config',
    'data_sync_manager',
    'integration_monitoring_config',
    'monitoring_manager',
    'rate_limiting_config',
    'rate_limit_manager'
]

# Version information
__version__ = "2.0.0"
__author__ = "Fahed Mlaiel"
__email__ = "mlaiel@live.de"
__license__ = "Proprietary - All Rights Reserved"
