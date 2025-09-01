"""Adapter Registry and Factory - Enterprise Adapter Management

This module provides centralized registry and factory management for all
platform adapters, enabling dynamic adapter discovery, lifecycle management,
and unified configuration across the enterprise platform ecosystem.

Author: Fahed Mlaiel
Email: mlaiel@live.de
Copyright: All rights reserved. Unauthorized use, reproduction, or distribution
of this code is strictly prohibited without explicit written permission.

Features:
- Centralized adapter registry and discovery
- Dynamic adapter loading and configuration
- Health monitoring and status tracking
- Load balancing and failover management
- Configuration validation and security
- Performance metrics and optimization
- Multi-tenant adapter isolation
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Union, Type, Callable
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import json
import importlib
from contextlib import asynccontextmanager
import redis

from .base_adapter import (
    BasePlatformAdapter, PlatformType, AdapterStatus, AuthenticationType,
    AdapterCredentials, RateLimitConfig, AdapterError, AuthenticationError
)

# Import all adapter factories
from .social_media_adapters import SocialMediaAdapterFactory, SocialMediaPlatform
from .music_streaming_adapters import MusicAdapterFactory, MusicPlatform
from .payment_gateway_adapters import PaymentAdapterFactory, PaymentGateway
from .cloud_storage_adapters import CloudStorageAdapterFactory, CloudProvider
from .analytics_service_adapters import AnalyticsAdapterFactory, AnalyticsPlatform

logger = logging.getLogger(__name__)

class AdapterCategory(Enum):
    """
Adapter category types."""

    SOCIAL_MEDIA = "social_media"
    MUSIC_STREAMING = "music_streaming"
    PAYMENT_GATEWAY = "payment_gateway"
    CLOUD_STORAGE = "cloud_storage"
    ANALYTICS_SERVICE = "analytics_service"
    EMAIL_SERVICE = "email_service"
    SMS_SERVICE = "sms_service"
    NOTIFICATION_SERVICE = "notification_service"
    CONTENT_DELIVERY = "content_delivery"

class AdapterPriority(Enum):
    """Adapter priority levels for load balancing."""

    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    BACKUP = "backup"

@dataclass
class AdapterConfig:
    """Configuration for adapter instances."""
    adapter_id: str
    category: AdapterCategory
    platform: str
    credentials: AdapterCredentials
    priority: AdapterPriority = AdapterPriority.MEDIUM
    enabled: bool = True
    max_retries: int = 3
    timeout: int = 30
    rate_limit_config: Optional[RateLimitConfig] = None
    custom_config: Dict[str, Any] = field(default_factory=dict)
    tags: List[str] = field(default_factory=list)
    tenant_id: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """
Convert config to dictionary."""
        return {
            'adapter_id': self.adapter_id,
            'category': self.category.value,
            'platform': self.platform,
            'priority': self.priority.value,
            'enabled': self.enabled,
            'max_retries': self.max_retries,
            'timeout': self.timeout,
            'tags': self.tags,
            'tenant_id': self.tenant_id,
            'custom_config': self.custom_config
        }

@dataclass
class AdapterInstance:
    """
Running adapter instance with metadata."""
    config: AdapterConfig
    adapter: BasePlatformAdapter
    created_at: datetime = field(default_factory=datetime.now)
    last_health_check: Optional[datetime] = None
    health_status: bool = False
    error_count: int = 0
    last_error: Optional[str] = None
    request_count: int = 0
    success_count: int = 0
    
    def get_success_rate(self) -> float:
        """
Calculate success rate percentage."""
        if self.request_count == 0:
            return 0.0
        return (self.success_count / self.request_count) * 100

class AdapterRegistry:
    """
    Centralized registry for managing platform adapters.
    
    Provides:
    - Dynamic adapter registration and discovery
    - Health monitoring and status tracking
    - Load balancing and failover management
    - Configuration validation and security
    - Performance metrics and optimization
    """
    
    def __init__(self, redis_client: Optional[redis.Redis] = None):
        self.redis_client = redis_client
        self.adapters: Dict[str, AdapterInstance] = {}
        self.factories: Dict[AdapterCategory, Any] = {
            AdapterCategory.SOCIAL_MEDIA: SocialMediaAdapterFactory,
            AdapterCategory.MUSIC_STREAMING: MusicAdapterFactory,
            AdapterCategory.PAYMENT_GATEWAY: PaymentAdapterFactory,
            AdapterCategory.CLOUD_STORAGE: CloudStorageAdapterFactory,
            AdapterCategory.ANALYTICS_SERVICE: AnalyticsAdapterFactory
        }
        self.health_check_interval = 300  # 5 minutes
        self.health_check_task: Optional[asyncio.Task] = None
        
        logger.info("Adapter registry initialized")
    
    async def register_adapter(self, config: AdapterConfig) -> str:
        """Register a new adapter instance."""
        try:
            # Validate configuration
            await self._validate_config(config)
            
            # Create adapter instance
            adapter = await self._create_adapter(config)
            
            # Connect and authenticate
            if not await adapter.connect():
                raise AdapterError(f"Failed to connect adapter: {config.adapter_id}")
            
            # Store adapter instance
            instance = AdapterInstance(
                config=config,
                adapter=adapter,
                health_status=True
            )
            
            self.adapters[config.adapter_id] = instance
            
            # Store in Redis if available
            if self.redis_client:
                await self._store_adapter_config(config)
            
            logger.info(f"Adapter registered: {config.adapter_id} ({config.category.value}/{config.platform})")
            
            # Start health monitoring if this is the first adapter
            if len(self.adapters) == 1 and not self.health_check_task:
                self.health_check_task = asyncio.create_task(self._health_monitor())
            
            return config.adapter_id
            
        except Exception as e:
            logger.error(f"Failed to register adapter {config.adapter_id}: {e}")
            raise AdapterError(f"Adapter registration failed: {e}")
    
    async def unregister_adapter(self, adapter_id: str) -> bool:
        """Unregister an adapter instance."""
        try:
            if adapter_id not in self.adapters:
                logger.warning(f"Adapter not found for unregistration: {adapter_id}")
                return False
            
            instance = self.adapters[adapter_id]
            
            # Disconnect adapter
            await instance.adapter.disconnect()
            
            # Remove from registry
            del self.adapters[adapter_id]
            
            # Remove from Redis if available
            if self.redis_client:
                self.redis_client.delete(f"adapter_config:{adapter_id}")
            
            logger.info(f"Adapter unregistered: {adapter_id}")
            
            # Stop health monitoring if no adapters left
            if len(self.adapters) == 0 and self.health_check_task:
                self.health_check_task.cancel()
                self.health_check_task = None
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to unregister adapter {adapter_id}: {e}")
            return False
    
    async def get_adapter(self, adapter_id: str) -> Optional[BasePlatformAdapter]:
        """Get adapter instance by ID."""
        instance = self.adapters.get(adapter_id)
        if instance and instance.config.enabled and instance.health_status:
            return instance.adapter
        return None
    
    async def get_adapters_by_category(self, category: AdapterCategory, 
                                      tenant_id: Optional[str] = None) -> List[BasePlatformAdapter]:
        """
Get all healthy adapters in a category."""
        adapters = []
        
        for instance in self.adapters.values():
            if (instance.config.category == category and 
                instance.config.enabled and 
                instance.health_status and
                (tenant_id is None or instance.config.tenant_id == tenant_id)):
                adapters.append(instance.adapter)
        
        # Sort by priority
        adapters.sort(key=lambda a: self._get_priority_weight(self.adapters[a.platform_name].config.priority))
        
        return adapters
    
    async def get_best_adapter(self, category: AdapterCategory, platform: str,
                              tenant_id: Optional[str] = None) -> Optional[BasePlatformAdapter]:
        """
Get the best available adapter for a platform."""
        candidates = []
        
        for instance in self.adapters.values():
            if (instance.config.category == category and
                instance.config.platform == platform and
                instance.config.enabled and
                instance.health_status and
                (tenant_id is None or instance.config.tenant_id == tenant_id)):
                candidates.append(instance)
        
        if not candidates:
            return None
        
        # Sort by priority and success rate
        candidates.sort(key=lambda i: (
            self._get_priority_weight(i.config.priority),
            i.get_success_rate()
        ), reverse=True)
        
        return candidates[0].adapter
    
    async def get_adapter_status(self, adapter_id: str) -> Optional[Dict[str, Any]]:
        """
Get detailed status information for an adapter."""
        instance = self.adapters.get(adapter_id)
        if not instance:
            return None
        
        return {
            'adapter_id': adapter_id,
            'category': instance.config.category.value,
            'platform': instance.config.platform,
            'status': instance.adapter.status.value,
            'health_status': instance.health_status,
            'enabled': instance.config.enabled,
            'priority': instance.config.priority.value,
            'created_at': instance.created_at.isoformat(),
            'last_health_check': instance.last_health_check.isoformat() if instance.last_health_check else None,
            'request_count': instance.request_count,
            'success_count': instance.success_count,
            'success_rate': instance.get_success_rate(),
            'error_count': instance.error_count,
            'last_error': instance.last_error,
            'tenant_id': instance.config.tenant_id,
            'tags': instance.config.tags,
            'metrics': instance.adapter.get_status()
        }
    
    async def get_all_statuses(self, category: Optional[AdapterCategory] = None,
                              tenant_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """
Get status for all adapters, optionally filtered."""
        statuses = []
        
        for adapter_id, instance in self.adapters.items():
            if (category is None or instance.config.category == category) and \
               (tenant_id is None or instance.config.tenant_id == tenant_id):
                status = await self.get_adapter_status(adapter_id)
                if status:
                    statuses.append(status)
        
        return statuses
    
    async def update_adapter_config(self, adapter_id: str, updates: Dict[str, Any]) -> bool:
        """
Update adapter configuration."""
        try:
            instance = self.adapters.get(adapter_id)
            if not instance:
                return False
            
            # Update configuration
            config = instance.config
            for key, value in updates.items():
                if hasattr(config, key):
                    setattr(config, key, value)
            
            # Store in Redis if available
            if self.redis_client:
                await self._store_adapter_config(config)
            
            logger.info(f"Adapter configuration updated: {adapter_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to update adapter config {adapter_id}: {e}")
            return False
    
    async def enable_adapter(self, adapter_id: str) -> bool:
        """Enable an adapter."""
        return await self.update_adapter_config(adapter_id, {'enabled': True})
    
    async def disable_adapter(self, adapter_id: str) -> bool:
        """
Disable an adapter."""
        return await self.update_adapter_config(adapter_id, {'enabled': False})
    
    async def record_request(self, adapter_id: str, success: bool, error: Optional[str] = None):
        """
Record adapter request metrics."""
        instance = self.adapters.get(adapter_id)
        if instance:
            instance.request_count += 1
            if success:
                instance.success_count += 1
            else:
                instance.error_count += 1
                instance.last_error = error
    
    async def _validate_config(self, config: AdapterConfig) -> None:
        """
Validate adapter configuration."""
        if not config.adapter_id:
            raise AdapterError("Adapter ID is required")
        
        if config.adapter_id in self.adapters:
            raise AdapterError(f"Adapter ID already exists: {config.adapter_id}")
        
        if config.category not in self.factories:
            raise AdapterError(f"Unsupported adapter category: {config.category}")
        
        if not config.credentials:
            raise AdapterError("Adapter credentials are required")
    
    async def _create_adapter(self, config: AdapterConfig) -> BasePlatformAdapter:
        """Create adapter instance from configuration."""
        factory = self.factories[config.category]
        
        # Map platform string to enum
        platform_enum = self._get_platform_enum(config.category, config.platform)
        
        return factory.create_adapter(
            platform=platform_enum,
            credentials=config.credentials,
            redis_client=self.redis_client
        )
    
    def _get_platform_enum(self, category: AdapterCategory, platform: str):
        """
Get platform enum from string."""
        mapping = {
            AdapterCategory.SOCIAL_MEDIA: SocialMediaPlatform,
            AdapterCategory.MUSIC_STREAMING: MusicPlatform,
            AdapterCategory.PAYMENT_GATEWAY: PaymentGateway,
            AdapterCategory.CLOUD_STORAGE: CloudProvider,
            AdapterCategory.ANALYTICS_SERVICE: AnalyticsPlatform
        }
        
        enum_class = mapping.get(category)
        if enum_class:
            try:
                return enum_class(platform.lower())
            except ValueError:
                raise AdapterError(f"Unsupported platform {platform} for category {category}")
        
        raise AdapterError(f"No platform mapping for category {category}")
    
    def _get_priority_weight(self, priority: AdapterPriority) -> int:
        """Get numeric weight for priority sorting."""
        weights = {
            AdapterPriority.HIGH: 3,
            AdapterPriority.MEDIUM: 2,
            AdapterPriority.LOW: 1,
            AdapterPriority.BACKUP: 0
        }
        return weights.get(priority, 1)
    
    async def _store_adapter_config(self, config: AdapterConfig) -> None:
        """
Store adapter configuration in Redis."""
        try:
            key = f"adapter_config:{config.adapter_id}"
            data = json.dumps(config.to_dict(), default=str)
            self.redis_client.setex(key, 86400, data)  # 24 hours
        except Exception as e:
            logger.warning(f"Failed to store adapter config in Redis: {e}")
    
    async def _health_monitor(self) -> None:
        """Background task for monitoring adapter health."""
        while True:
            try:
                await asyncio.sleep(self.health_check_interval)
                
                # Check health of all adapters
                for adapter_id, instance in self.adapters.items():
                    try:
                        health_status = await instance.adapter.health_check()
                        instance.health_status = health_status
                        instance.last_health_check = datetime.now()
                        
                        if not health_status:
                            logger.warning(f"Adapter health check failed: {adapter_id}")
                        
                    except Exception as e:
                        instance.health_status = False
                        instance.last_health_check = datetime.now()
                        instance.error_count += 1
                        instance.last_error = str(e)
                        logger.error(f"Health check error for adapter {adapter_id}: {e}")
                
                logger.debug(f"Health check completed for {len(self.adapters)} adapters")
                
            except asyncio.CancelledError:
                logger.info("Health monitor task cancelled")
                break
            except Exception as e:
                logger.error(f"Health monitor error: {e}")

# Global registry instance
_registry_instance: Optional[AdapterRegistry] = None

def get_adapter_registry(redis_client: Optional[redis.Redis] = None) -> AdapterRegistry:
    """Get singleton adapter registry instance."""
    global _registry_instance
    
    if _registry_instance is None:
        _registry_instance = AdapterRegistry(redis_client)
    
    return _registry_instance

@asynccontextmanager
async def adapter_context(config: AdapterConfig):
    """
Context manager for temporary adapter usage."""
    registry = get_adapter_registry()
    adapter_id = None
    
    try:
        adapter_id = await registry.register_adapter(config)
        adapter = await registry.get_adapter(adapter_id)
        yield adapter
    finally:
        if adapter_id:
            await registry.unregister_adapter(adapter_id)

# Convenience functions for common operations
async def get_social_media_adapter(platform: str, credentials: AdapterCredentials,
                                  tenant_id: Optional[str] = None) -> Optional[BasePlatformAdapter]:
    """
Get social media adapter by platform name."""
    registry = get_adapter_registry()
    return await registry.get_best_adapter(
        AdapterCategory.SOCIAL_MEDIA, 
        platform, 
        tenant_id
    )

async def get_music_adapter(platform: str, credentials: AdapterCredentials,
                           tenant_id: Optional[str] = None) -> Optional[BasePlatformAdapter]:
    """
Get music streaming adapter by platform name."""
    registry = get_adapter_registry()
    return await registry.get_best_adapter(
        AdapterCategory.MUSIC_STREAMING, 
        platform, 
        tenant_id
    )

async def get_payment_adapter(gateway: str, credentials: AdapterCredentials,
                             tenant_id: Optional[str] = None) -> Optional[BasePlatformAdapter]:
    """
Get payment gateway adapter by gateway name."""
    registry = get_adapter_registry()
    return await registry.get_best_adapter(
        AdapterCategory.PAYMENT_GATEWAY, 
        gateway, 
        tenant_id
    )

async def get_storage_adapter(provider: str, credentials: AdapterCredentials,
                             tenant_id: Optional[str] = None) -> Optional[BasePlatformAdapter]:
    """
Get cloud storage adapter by provider name."""
    registry = get_adapter_registry()
    return await registry.get_best_adapter(
        AdapterCategory.CLOUD_STORAGE, 
        provider, 
        tenant_id
    )

async def get_analytics_adapter(platform: str, credentials: AdapterCredentials,
                               tenant_id: Optional[str] = None) -> Optional[BasePlatformAdapter]:
    """
Get analytics adapter by platform name."""
    registry = get_adapter_registry()
    return await registry.get_best_adapter(
        AdapterCategory.ANALYTICS_SERVICE, 
        platform, 
        tenant_id
    )

# Export all classes and functions
__all__ = [
    'AdapterCategory',
    'AdapterPriority', 
    'AdapterConfig',
    'AdapterInstance',
    'AdapterRegistry',
    'get_adapter_registry',
    'adapter_context',
    'get_social_media_adapter',
    'get_music_adapter',
    'get_payment_adapter',
    'get_storage_adapter',
    'get_analytics_adapter'
]
