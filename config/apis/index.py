"""
APIs Configuration Index - Centralized API Registry & Orchestration
Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

 CRITICAL LEGAL NOTICE:
This code and concept are the exclusive intellectual property of Fahed Mlaiel.
Any unauthorized use, copying, distribution, or commercialization without explicit written permission 
from Fahed Mlaiel (mlaiel@live.de) is strictly prohibited and will result in legal action.

Team Specialties: Lead Dev IA + Backend Senior + ML Engineer + DBA + Security + 
Microservices + Audio + DevOps + IA Prompt Engineer

This index module provides centralized orchestration and registry for all API configurations,
serving as the main entry point for API management and integration services.

Business Logic: User (musician/blogger/photographer/influencer/comedian) → Multi-format upload → 
AI rights protection → Pro SEO → Collaboration matching → Multi-platform distribution
"""

import asyncio
import logging
from typing import Dict, List, Any, Optional, Union, Type
from dataclasses import dataclass
from enum import Enum
from datetime import datetime

from .api_manager import APIManager, APIStatus
from .authentication import APIAuthenticationManager
from .rate_limiting import APIRateLimiter
from .monitoring import APIMonitoringManager
from .external_integrations import ExternalAPIIntegration

# Import all configuration modules
from .platform_apis import PLATFORM_CONFIGS, PlatformAPIConfig
from .payment_apis import PAYMENT_CONFIGS, PaymentAPIConfig
from .protection_apis import PROTECTION_CONFIGS, ProtectionAPIConfig
from .cloud_apis import CLOUD_CONFIGS, CloudAPIConfig
from .analytics_apis import ANALYTICS_CONFIGS, AnalyticsAPIConfig
from .communication_apis import COMMUNICATION_CONFIGS, CommunicationAPIConfig
from .fingerprinting_apis import FINGERPRINTING_CONFIGS, FingerprintAPIConfig

logger = logging.getLogger(__name__)

class APIRegistry:
    """
    Centralized API registry and orchestration system
    """
    
    def __init__(self, environment: str = "production"):
        self.environment = environment
        self.api_manager = APIManager(environment=environment)
        self.auth_manager = APIAuthenticationManager()
        self.rate_limiter = APIRateLimiter()
        self.monitoring_manager = APIMonitoringManager()
        self.integration_client = ExternalAPIIntegration()
        
        # Registry of all configurations
        self._api_configs = {}
        self._api_clients = {}
        self._api_status = {}
        
        self._initialize_registry()
    
    def _initialize_registry(self) -> None:
        """Initialize the complete API registry"""



        try:
            # Register all API configurations
            all_configs = {
                **PLATFORM_CONFIGS,
                **PAYMENT_CONFIGS,
                **PROTECTION_CONFIGS,
                **CLOUD_CONFIGS,
                **ANALYTICS_CONFIGS,
                **COMMUNICATION_CONFIGS,
                **FINGERPRINTING_CONFIGS
            }
            
            for api_name, config in all_configs.items():
                self._api_configs[api_name] = config
                self._api_status[api_name] = APIStatus.INACTIVE
                self.api_manager.register_api_config(api_name, config)
            
            logger.info(f"API Registry initialized with {len(all_configs)} configurations")
            
        except Exception as e:
            logger.error(f"Failed to initialize API registry: {e}")
            raise
    
    async def get_authenticated_client(self, api_name: str, user_id: Optional[str] = None) -> Any:
        """
        Get authenticated client for specified API
        
        Args:
            api_name: API service name
            user_id: Optional user ID for user-specific authentication
            
        Returns:
            Authenticated API client instance
        """



        try:
            if api_name not in self._api_configs:
                raise ValueError(f"API configuration not found: {api_name}")
            
            # Check if client already exists and is valid
            client_key = f"{api_name}_{user_id or 'global'}"
            if client_key in self._api_clients:
                client = self._api_clients[client_key]
                if await self._validate_client(client):
                    return client
            
            # Create new authenticated client
            config = self._api_configs[api_name]
            client = await self.auth_manager.get_authenticated_client(
                platform=api_name,
                config=config,
                user_id=user_id
            )
            
            # Cache the client
            self._api_clients[client_key] = client
            self._api_status[api_name] = APIStatus.ACTIVE
            
            # Start monitoring
            await self.monitoring_manager.start_monitoring(api_name, client)
            
            logger.info(f"Authenticated client created for {api_name}")
            return client
            
        except Exception as e:
            logger.error(f"Failed to get authenticated client for {api_name}: {e}")
            self._api_status[api_name] = APIStatus.ERROR
            raise
    
    async def _validate_client(self, client: Any) -> bool:
        """Validate if client is still valid and authenticated"""



        try:
            # Implementation depends on client type
            # This is a simplified validation
            if hasattr(client, 'is_authenticated'):
                return await client.is_authenticated()
            return True
        except Exception:
            return False
    
    async def execute_api_request(
        self, 
        api_name: str, 
        method: str, 
        endpoint: str, 
        data: Optional[Dict[str, Any]] = None,
        user_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Execute API request with rate limiting and monitoring
        
        Args:
            api_name: API service name
            method: HTTP method
            endpoint: API endpoint
            data: Request data
            user_id: Optional user ID
            
        Returns:
            API response data
        """



        try:
            # Check rate limiting
            rate_limit_result = await self.rate_limiter.check_rate_limit(
                api_name=api_name,
                user_id=user_id
            )
            
            if not rate_limit_result.allowed:
                raise Exception(f"Rate limit exceeded for {api_name}")
            
            # Get authenticated client
            client = await self.get_authenticated_client(api_name, user_id)
            
            # Execute request through integration client
            response = await self.integration_client.execute_request(
                client=client,
                method=method,
                endpoint=endpoint,
                data=data
            )
            
            # Record metrics
            await self.monitoring_manager.record_request_metrics(
                api_name=api_name,
                method=method,
                endpoint=endpoint,
                response_time=response.get('response_time', 0),
                status_code=response.get('status_code', 200)
            )
            
            return response
            
        except Exception as e:
            logger.error(f"API request failed for {api_name}: {e}")
            await self.monitoring_manager.record_error(api_name, str(e))
            raise
    
    def get_api_status(self, api_name: Optional[str] = None) -> Dict[str, APIStatus]:
        """Get status of API(s)"""
        if api_name:
            return {api_name: self._api_status.get(api_name, APIStatus.INACTIVE)}
        return self._api_status.copy()
    
    def get_registered_apis(self) -> List[str]:
        """Get list of all registered API names"""



        return list(self._api_configs.keys())
    
    async def health_check(self, api_name: Optional[str] = None) -> Dict[str, Dict[str, Any]]:
        """
        Perform health check on API(s)
        
        Args:
            api_name: Optional specific API to check
            
        Returns:
            Health status for API(s)
        """
        health_results = {}
        apis_to_check = [api_name] if api_name else self._api_configs.keys()
        
        for api in apis_to_check:
            try:
                config = self._api_configs[api]
                health_status = await self.monitoring_manager.check_api_health(api, config)
                health_results[api] = health_status
                
            except Exception as e:
                health_results[api] = {
                    'status': 'error',
                    'error': str(e),
                    'timestamp': datetime.now().isoformat()
                }
        
        return health_results
    
    async def refresh_authentication(self, api_name: str, user_id: Optional[str] = None) -> bool:
        """
        Refresh authentication for specified API
        
        Args:
            api_name: API service name
            user_id: Optional user ID
            
        Returns:
            True if refresh successful
        """



        try:
            client_key = f"{api_name}_{user_id or 'global'}"
            
            # Remove cached client
            if client_key in self._api_clients:
                del self._api_clients[client_key]
            
            # Get new authenticated client
            await self.get_authenticated_client(api_name, user_id)
            
            logger.info(f"Authentication refreshed for {api_name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to refresh authentication for {api_name}: {e}")
            return False
    
    async def shutdown(self) -> None:
        """Gracefully shutdown API registry and cleanup resources"""



        try:
            # Stop monitoring
            await self.monitoring_manager.stop_all_monitoring()
            
            # Close clients
            for client in self._api_clients.values():
                if hasattr(client, 'close'):
                    await client.close()
            
            self._api_clients.clear()
            logger.info("API Registry shutdown completed")
            
        except Exception as e:
            logger.error(f"Error during API registry shutdown: {e}")


# Global registry instance
_global_registry: Optional[APIRegistry] = None

def get_api_registry(environment: str = "production") -> APIRegistry:
    """
    Get global API registry instance (singleton pattern)
    
    Args:
        environment: Target environment
        
    Returns:
        Global APIRegistry instance
    """
    global _global_registry
    
    if _global_registry is None:
        _global_registry = APIRegistry(environment=environment)
    
    return _global_registry

async def initialize_apis(environment: str = "production") -> APIRegistry:
    """
    Initialize and return the global API registry
    
    Args:
        environment: Target environment
        
    Returns:
        Initialized APIRegistry instance
    """
    registry = get_api_registry(environment)
    
    # Perform initial health checks
    health_status = await registry.health_check()
    healthy_apis = sum(1 for status in health_status.values() if status.get('status') == 'healthy')
    
    logger.info(f"API Registry initialized: {healthy_apis}/{len(health_status)} APIs healthy")
    return registry

# Convenience functions for common operations
async def get_platform_client(platform: str, user_id: Optional[str] = None) -> Any:
    """Get authenticated client for social media/streaming platform"""
    registry = get_api_registry()
    return await registry.get_authenticated_client(platform, user_id)

async def get_payment_client(provider: str, user_id: Optional[str] = None) -> Any:
    """Get authenticated client for payment provider"""
    registry = get_api_registry()
    return await registry.get_authenticated_client(provider, user_id)

async def get_protection_client(service: str, user_id: Optional[str] = None) -> Any:
    """Get authenticated client for content protection service"""
    registry = get_api_registry()
    return await registry.get_authenticated_client(service, user_id)

async def execute_platform_request(
    platform: str,
    method: str,
    endpoint: str,
    data: Optional[Dict[str, Any]] = None,
    user_id: Optional[str] = None
) -> Dict[str, Any]:
    """Execute request to social media/streaming platform"""
    registry = get_api_registry()
    return await registry.execute_api_request(platform, method, endpoint, data, user_id)

# Export main classes and functions
__all__ = [
    'APIRegistry',
    'get_api_registry',
    'initialize_apis',
    'get_platform_client',
    'get_payment_client', 
    'get_protection_client',
    'execute_platform_request'
]
