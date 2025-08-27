"""
Integrations Index Module for IA-Influencer Agent Platform
==========================================================

Centralized access point for all integration configurations and managers.
Provides simplified imports and initialization for the complete integration ecosystem.

Author: Fahed Mlaiel <mlaiel@live.de>
Project: IA-Influencer Agent + Content Protection Platform
Team: Lead Dev IA + Backend Senior + ML Engineer + DBA + Security + Microservices + Audio + DevOps

WARNING: This code is the intellectual property of Fahed Mlaiel.
Any unauthorized use, reproduction, or distribution without explicit written permission
is strictly prohibited and will be prosecuted to the full extent of the law.

Contact: mlaiel@live.de for licensing inquiries.
"""

# Import all configuration classes
from .oauth_config import (
    OAuthConfig, 
    OAuthProvider, 
    OAuthScope, 
    OAuthManager,
    oauth_config,
    oauth_manager
)

from .api_client_config import (
    APIClientConfig,
    APIProvider,
    APIClientManager,
    api_client_config,
    api_client_manager
)

from .webhook_config import (
    WebhookConfig,
    WebhookProvider,
    WebhookEvent,
    WebhookManager,
    webhook_config,
    webhook_manager
)

from .webhook_handlers_config import (
    WebhookHandlersConfig,
    WebhookHandlerRegistry,
    webhook_handlers_config,
    webhook_handler_registry
)

from .external_services_config import (
    ExternalServicesConfig,
    ServiceProvider,
    ExternalServiceManager,
    external_services_config,
    external_service_manager
)

from .data_sync_config import (
    DataSyncConfig,
    DataSyncManager,
    data_sync_config,
    data_sync_manager
)

from .integration_monitoring_config import (
    IntegrationMonitoringConfig,
    MonitoringManager,
    integration_monitoring_config,
    monitoring_manager
)

from .rate_limiting_config import (
    RateLimitingConfig,
    RateLimitManager,
    rate_limiting_config,
    rate_limit_manager
)


class IntegrationsIndex:
    """
    Centralized integration management index.
    
    Provides easy access to all integration configurations and managers
    with initialization and health check capabilities.
    """
    
    def __init__(self):
        self.initialized = False
        
        # Configuration instances
        self.oauth = oauth_config
        self.api_clients = api_client_config
        self.webhooks = webhook_config
        self.webhook_handlers = webhook_handlers_config
        self.external_services = external_services_config
        self.data_sync = data_sync_config
        self.monitoring = integration_monitoring_config
        self.rate_limiting = rate_limiting_config
        
        # Manager instances
        self.oauth_manager = oauth_manager
        self.api_client_manager = api_client_manager
        self.webhook_manager = webhook_manager
        self.webhook_handler_registry = webhook_handler_registry
        self.external_service_manager = external_service_manager
        self.data_sync_manager = data_sync_manager
        self.monitoring_manager = monitoring_manager
        self.rate_limit_manager = rate_limit_manager
    
    async def initialize(self) -> bool:
        """Initialize all integration services."""
        try:
            # Initialize API clients
            await self._initialize_api_clients()
            
            # Initialize webhook handlers
            await self._initialize_webhook_handlers()
            
            # Initialize monitoring
            await self._initialize_monitoring()
            
            # Initialize data sync
            await self._initialize_data_sync()
            
            self.initialized = True
            return True
            
        except Exception as e:
            print(f"Failed to initialize integrations: {e}")
            return False
    
    async def _initialize_api_clients(self):
        """Initialize API client configurations."""
        # Validate OAuth configurations
        for provider in OAuthProvider:
            if hasattr(self.oauth, f"{provider}_client_id"):
                self.oauth_manager.validate_provider_config(provider)
    
    async def _initialize_webhook_handlers(self):
        """Initialize webhook handlers."""
        # Register default handlers if not already registered
        if not self.webhook_handler_registry.handlers:
            from .webhook_handlers_config import DefaultHandlerConfigs
            for handler_config in DefaultHandlerConfigs.get_default_configs():
                event_type = handler_config.name.replace("_handler", "")
                self.webhook_handler_registry.register_handler(event_type, handler_config)
    
    async def _initialize_monitoring(self):
        """Initialize monitoring services."""
        # Update service status for all configured services
        for provider in ServiceProvider:
            if self.external_service_manager.is_service_enabled(provider):
                # Perform initial health check
                health_status = await self.external_service_manager.check_service_health(provider)
                from .integration_monitoring_config import HealthStatus
                status = HealthStatus.HEALTHY if health_status else HealthStatus.UNHEALTHY
                self.monitoring_manager.update_health_status(provider.value, status)
    
    async def _initialize_data_sync(self):
        """Initialize data synchronization services."""
        # Create default sync jobs if none exist
        if not self.data_sync_manager.sync_jobs:
            from .data_sync_config import DataSource, SyncStrategy, SyncDirection
            
            # Spotify sync job
            if self.oauth.spotify_sync_enabled:
                self.data_sync_manager.create_sync_job(
                    job_id="spotify_user_data",
                    source=DataSource.SPOTIFY,
                    target=DataSource.USER_PROFILES,
                    strategy=SyncStrategy.REAL_TIME,
                    direction=SyncDirection.BIDIRECTIONAL
                )
            
            # YouTube sync job
            if self.oauth.youtube_sync_enabled:
                self.data_sync_manager.create_sync_job(
                    job_id="youtube_content_data",
                    source=DataSource.YOUTUBE,
                    target=DataSource.CONTENT_FINGERPRINTS,
                    strategy=SyncStrategy.EVENT_DRIVEN,
                    direction=SyncDirection.PULL_ONLY
                )
    
    async def health_check(self) -> dict:
        """Perform comprehensive health check of all integrations."""
        health_status = {
            "initialized": self.initialized,
            "oauth": {
                "enabled_providers": len([
                    p for p in OAuthProvider 
                    if self.oauth_manager.validate_provider_config(p)
                ]),
                "total_providers": len(OAuthProvider)
            },
            "api_clients": {
                "configured_clients": len(self.api_client_manager.service_configs)
            },
            "webhooks": {
                "enabled": self.webhooks.webhook_enabled if hasattr(self.webhooks, 'webhook_enabled') else True,
                "registered_handlers": len(self.webhook_handler_registry.handlers)
            },
            "external_services": {
                "enabled_services": len(self.external_service_manager.get_enabled_services()),
                "health_status": self.monitoring_manager.get_all_health_status()
            },
            "data_sync": {
                "active_jobs": len(self.data_sync_manager.get_active_sync_jobs()),
                "sync_stats": self.data_sync_manager.get_sync_schedule()
            },
            "monitoring": {
                "stats": self.monitoring_manager.get_monitoring_statistics()
            },
            "rate_limiting": {
                "status": self.rate_limit_manager.get_rate_limit_status()
            }
        }
        
        return health_status
    
    async def shutdown(self):
        """Gracefully shutdown all integration services."""
        try:
            # Close API clients
            await self.api_client_manager.close_all_clients()
            
            # Mark as shutdown
            self.initialized = False
            
        except Exception as e:
            print(f"Error during integrations shutdown: {e}")
    
    def get_config_summary(self) -> dict:
        """Get summary of all integration configurations."""
        return {
            "oauth_providers": list(OAuthProvider),
            "api_providers": list(APIProvider),
            "webhook_providers": list(WebhookProvider),
            "service_providers": list(ServiceProvider),
            "monitoring_enabled": self.monitoring.monitoring_enabled,
            "rate_limiting_enabled": self.rate_limiting.rate_limiting_enabled,
            "data_sync_enabled": self.data_sync.sync_enabled
        }


# Global integrations index instance
integrations_index = IntegrationsIndex()

# Convenience functions for quick access
def get_oauth_manager():
    """Get OAuth manager instance."""
    return integrations_index.oauth_manager

def get_api_client_manager():
    """Get API client manager instance."""
    return integrations_index.api_client_manager

def get_webhook_manager():
    """Get webhook manager instance."""
    return integrations_index.webhook_manager

def get_monitoring_manager():
    """Get monitoring manager instance."""
    return integrations_index.monitoring_manager

async def initialize_integrations():
    """Initialize all integration services."""
    return await integrations_index.initialize()

async def health_check_integrations():
    """Perform health check on all integrations."""
    return await integrations_index.health_check()

async def shutdown_integrations():
    """Shutdown all integration services."""
    await integrations_index.shutdown()


# Export everything for easy imports
__all__ = [
    'IntegrationsIndex',
    'integrations_index',
    'get_oauth_manager',
    'get_api_client_manager', 
    'get_webhook_manager',
    'get_monitoring_manager',
    'initialize_integrations',
    'health_check_integrations',
    'shutdown_integrations'
]
