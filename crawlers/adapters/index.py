#!/usr/bin/env python3
"""Crawlers Adapters Index - Enterprise Module Organization
=======================================================

Central index and registry for all adapter types in the IA-Influencer Agent platform.
Provides fast lookup, discovery, and management of adapter capabilities.

Business Logic: Adapter Discovery → Configuration → Initialization → Management

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: © 2025 Fahed Mlaiel. All rights reserved.

WARNING: This code is protected by copyright law. Any unauthorized copying, 
distribution, or modification is strictly prohibited and will result in 
legal action. Contact mlaiel@live.de for licensing.
"""import asyncio
import logging
from typing import Dict, List, Optional, Any, Type, Union
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)


class AdapterType(Enum):
    """Enumeration of all adapter types."""    CONTENT = "content"
    PLATFORM = "platform"
    AUTHENTICATION = "authentication"
    DATA = "data"
    STORAGE = "storage"
    FORMAT = "format"
    PROTOCOL = "protocol"
    API = "api"


class AdapterStatus(Enum):
    """Adapter status enumeration."""    INACTIVE = "inactive"
    INITIALIZING = "initializing"
    ACTIVE = "active"
    ERROR = "error"
    DEGRADED = "degraded"
    MAINTENANCE = "maintenance"


@dataclass
class AdapterInfo:
    """Adapter information and metadata."""    name: str
    adapter_type: AdapterType
    version: str
    description: str
    author: str = "Fahed Mlaiel"
    email: str = "mlaiel@live.de"
    status: AdapterStatus = AdapterStatus.INACTIVE
    capabilities: List[str] = field(default_factory=list)
    dependencies: List[str] = field(default_factory=list)
    config_schema: Optional[Dict[str, Any]] = None
    performance_metrics: Dict[str, Any] = field(default_factory=dict)
    last_health_check: Optional[datetime] = None
    error_count: int = 0
    uptime_seconds: float = 0.0


class AdapterRegistry:
    """    Enterprise Adapter Registry System
    
    Centralized registry for all adapters with advanced features:
    - Dynamic adapter discovery and registration
    - Health monitoring and status tracking
    - Performance metrics collection
    - Configuration management
    - Dependency resolution
    - Load balancing and failover
    """    
    def __init__(self):
        """Initialize the adapter registry."""        self._adapters: Dict[str, AdapterInfo] = {}
        self._instances: Dict[str, Any] = {}
        self._type_mapping: Dict[AdapterType, List[str]] = {
            adapter_type: [] for adapter_type in AdapterType
        }
        self._initialized = False
    
    def register_adapter(self, adapter_info: AdapterInfo, instance: Any = None) -> bool:
        """Register a new adapter with the registry."""        try:
            adapter_name = adapter_info.name
            
            # Validate adapter info
            if not self._validate_adapter_info(adapter_info):
                logger.error(f"Invalid adapter info for '{adapter_name}'")
                return False
            
            # Register adapter
            self._adapters[adapter_name] = adapter_info
            if instance:
                self._instances[adapter_name] = instance
            
            # Update type mapping
            if adapter_name not in self._type_mapping[adapter_info.adapter_type]:
                self._type_mapping[adapter_info.adapter_type].append(adapter_name)
            
            logger.info(f"Adapter '{adapter_name}' registered successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to register adapter '{adapter_info.name}': {e}")
            return False
    
    def unregister_adapter(self, adapter_name: str) -> bool:
        """Unregister an adapter from the registry."""        try:
            if adapter_name not in self._adapters:
                logger.warning(f"Adapter '{adapter_name}' not found in registry")
                return False
            
            adapter_info = self._adapters[adapter_name]
            
            # Remove from registry
            del self._adapters[adapter_name]
            if adapter_name in self._instances:
                del self._instances[adapter_name]
            
            # Update type mapping
            if adapter_name in self._type_mapping[adapter_info.adapter_type]:
                self._type_mapping[adapter_info.adapter_type].remove(adapter_name)
            
            logger.info(f"Adapter '{adapter_name}' unregistered successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to unregister adapter '{adapter_name}': {e}")
            return False
    
    def get_adapter(self, adapter_name: str) -> Optional[AdapterInfo]:
        """Get adapter information by name."""        return self._adapters.get(adapter_name)
    
    def get_adapter_instance(self, adapter_name: str) -> Optional[Any]:
        """Get adapter instance by name."""        return self._instances.get(adapter_name)
    
    def get_adapters_by_type(self, adapter_type: AdapterType) -> List[AdapterInfo]:
        """Get all adapters of a specific type."""        adapter_names = self._type_mapping.get(adapter_type, [])
        return [self._adapters[name] for name in adapter_names if name in self._adapters]
    
    def get_active_adapters(self) -> List[AdapterInfo]:
        """Get all active adapters."""        return [
            adapter for adapter in self._adapters.values()
            if adapter.status == AdapterStatus.ACTIVE
        ]
    
    def get_adapter_capabilities(self, adapter_name: str) -> List[str]:
        """Get capabilities of a specific adapter."""        adapter = self.get_adapter(adapter_name)
        return adapter.capabilities if adapter else []
    
    def find_adapters_by_capability(self, capability: str) -> List[AdapterInfo]:
        """Find adapters that support a specific capability."""        return [
            adapter for adapter in self._adapters.values()
            if capability in adapter.capabilities
        ]
    
    def update_adapter_status(self, adapter_name: str, status: AdapterStatus) -> bool:
        """Update adapter status."""        if adapter_name in self._adapters:
            self._adapters[adapter_name].status = status
            self._adapters[adapter_name].last_health_check = datetime.utcnow()
            return True
        return False
    
    def update_adapter_metrics(self, adapter_name: str, metrics: Dict[str, Any]) -> bool:
        """Update adapter performance metrics."""        if adapter_name in self._adapters:
            self._adapters[adapter_name].performance_metrics.update(metrics)
            return True
        return False
    
    def get_registry_status(self) -> Dict[str, Any]:
        """Get comprehensive registry status."""        total_adapters = len(self._adapters)
        active_adapters = len(self.get_active_adapters())
        
        status_counts = {}
        for status in AdapterStatus:
            status_counts[status.value] = len([
                adapter for adapter in self._adapters.values()
                if adapter.status == status
            ])
        
        type_counts = {}
        for adapter_type in AdapterType:
            type_counts[adapter_type.value] = len(self._type_mapping[adapter_type])
        
        return {
            'total_adapters': total_adapters,
            'active_adapters': active_adapters,
            'health_ratio': active_adapters / total_adapters if total_adapters > 0 else 0,
            'status_distribution': status_counts,
            'type_distribution': type_counts,
            'initialized': self._initialized,
            'timestamp': datetime.utcnow().isoformat()
        }
    
    def _validate_adapter_info(self, adapter_info: AdapterInfo) -> bool:
        """Validate adapter information."""        if not adapter_info.name:
            return False
        if not adapter_info.version:
            return False
        if not isinstance(adapter_info.adapter_type, AdapterType):
            return False
        return True
    
    async def initialize_registry(self) -> bool:
        """Initialize the adapter registry."""        try:
            logger.info("Initializing adapter registry...")
            self._register_builtin_adapters()
            self._initialized = True
            logger.info("Adapter registry initialized successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to initialize adapter registry: {e}")
            return False
    
    def _register_builtin_adapters(self):
        """Register all built-in adapters."""        
        # Content Adapters
        content_adapters = [
            AdapterInfo(
                name="content_processor",
                adapter_type=AdapterType.CONTENT,
                version="2.15.0",
                description="Advanced multi-format content processing",
                capabilities=["process", "analyze", "transform", "validate"]
            ),
            AdapterInfo(
                name="content_fingerprinter", 
                adapter_type=AdapterType.CONTENT,
                version="2.15.0",
                description="AI-powered content fingerprinting",
                capabilities=["fingerprint", "similarity", "duplicate_detection"]
            ),
            AdapterInfo(
                name="content_protector",
                adapter_type=AdapterType.CONTENT,
                version="2.15.0", 
                description="Content protection and copyright monitoring",
                capabilities=["protect", "monitor", "takedown", "copyright"]
            )
        ]
        
        # Platform Adapters
        platform_adapters = [
            AdapterInfo(
                name="youtube_adapter",
                adapter_type=AdapterType.PLATFORM,
                version="2.15.0",
                description="YouTube API integration with content monitoring",
                capabilities=["search", "upload", "analytics", "monetization"]
            ),
            AdapterInfo(
                name="spotify_adapter",
                adapter_type=AdapterType.PLATFORM,
                version="2.15.0",
                description="Spotify API integration for music creators",
                capabilities=["search", "upload", "analytics", "playlists"]
            ),
            AdapterInfo(
                name="instagram_adapter",
                adapter_type=AdapterType.PLATFORM,
                version="2.15.0",
                description="Instagram content integration and monitoring",
                capabilities=["post", "stories", "reels", "analytics"]
            )
        ]
        
        # Authentication Adapters
        auth_adapters = [
            AdapterInfo(
                name="oauth2_handler",
                adapter_type=AdapterType.AUTHENTICATION,
                version="2.15.0",
                description="OAuth2 authentication with PKCE support",
                capabilities=["oauth2", "tokens", "refresh", "pkce"]
            ),
            AdapterInfo(
                name="jwt_manager",
                adapter_type=AdapterType.AUTHENTICATION,
                version="2.15.0",
                description="JWT token management and validation",
                capabilities=["jwt", "tokens", "validation", "claims"]
            ),
            AdapterInfo(
                name="mfa_authenticator",
                adapter_type=AdapterType.AUTHENTICATION,
                version="2.15.0",
                description="Multi-factor authentication system",
                capabilities=["totp", "sms", "email", "biometric"]
            )
        ]
        
        # Register all adapters
        all_adapters = content_adapters + platform_adapters + auth_adapters
        for adapter_info in all_adapters:
            self.register_adapter(adapter_info)


# Global adapter registry instance
adapter_registry = AdapterRegistry()


class AdapterIndex:
    """    Enhanced Adapter Index System
    
    Provides fast lookup and discovery capabilities for adapters.
    """    
    def __init__(self, registry: AdapterRegistry):
        """Initialize with adapter registry."""        self.registry = registry
        self._capability_index: Dict[str, List[str]] = {}
        self._type_index: Dict[str, List[str]] = {}
        self._status_index: Dict[str, List[str]] = {}
        self._rebuild_indices()
    
    def _rebuild_indices(self):
        """Rebuild all search indices."""        self._capability_index.clear()
        self._type_index.clear()
        self._status_index.clear()
        
        for adapter_name, adapter_info in self.registry._adapters.items():
            # Capability index
            for capability in adapter_info.capabilities:
                if capability not in self._capability_index:
                    self._capability_index[capability] = []
                self._capability_index[capability].append(adapter_name)
            
            # Type index
            adapter_type = adapter_info.adapter_type.value
            if adapter_type not in self._type_index:
                self._type_index[adapter_type] = []
            self._type_index[adapter_type].append(adapter_name)
            
            # Status index
            status = adapter_info.status.value
            if status not in self._status_index:
                self._status_index[status] = []
            self._status_index[status].append(adapter_name)
    
    def search_by_capability(self, capability: str) -> List[str]:
        """Search adapters by capability."""        return self._capability_index.get(capability, [])
    
    def search_by_type(self, adapter_type: str) -> List[str]:
        """Search adapters by type."""        return self._type_index.get(adapter_type, [])
    
    def search_by_status(self, status: str) -> List[str]:
        """Search adapters by status."""        return self._status_index.get(status, [])
    
    def get_available_capabilities(self) -> List[str]:
        """Get all available capabilities."""        return list(self._capability_index.keys())
    
    def refresh_indices(self):
        """Refresh all search indices."""        self._rebuild_indices()


# Global adapter index
adapter_index = AdapterIndex(adapter_registry)


# Utility functions
async def initialize_adapter_system():
    """Initialize the complete adapter system."""    try:
        await adapter_registry.initialize_registry()
        adapter_index.refresh_indices()
        logger.info("Adapter system initialized successfully")
        return True
    except Exception as e:
        logger.error(f"Failed to initialize adapter system: {e}")
        return False


def get_adapter_summary() -> Dict[str, Any]:
    """Get a summary of all registered adapters."""    return {
        'registry_status': adapter_registry.get_registry_status(),
        'available_capabilities': adapter_index.get_available_capabilities(),
        'active_adapters': [
            adapter.name for adapter in adapter_registry.get_active_adapters()
        ]
    }


# Export public interface
__all__ = [
    'AdapterType',
    'AdapterStatus', 
    'AdapterInfo',
    'AdapterRegistry',
    'AdapterIndex',
    'adapter_registry',
    'adapter_index',
    'initialize_adapter_system',
    'get_adapter_summary'
]

import logging
import asyncio
from typing import Dict, List, Optional, Any, Type, Union, Callable
from dataclasses import dataclass
from datetime import datetime
import json
import importlib
from pathlib import Path

from . import (
    AdapterManager, 
    AdapterType, 
    AdapterInfo,
    adapter_manager,
    get_available_adapters,
    get_adapter_by_name,
    get_adapters_by_type
)

logger = logging.getLogger(__name__)

@dataclass
class AdapterConfig:
    """Configuration for adapter instances."""    adapter_name: str
    adapter_type: AdapterType
    config_params: Dict[str, Any]
    auth_config: Optional[Dict[str, Any]] = None
    performance_config: Optional[Dict[str, Any]] = None
    security_config: Optional[Dict[str, Any]] = None
    monitoring_enabled: bool = True
    auto_retry: bool = True
    max_retries: int = 3
    timeout: int = 30

class AdapterFactory:
    """Factory for creating and managing adapter instances."""    
    def __init__(self):
        """Initialize the adapter factory."""        self._instances: Dict[str, Any] = {}
        self._configs: Dict[str, AdapterConfig] = {}
        self.logger = logging.getLogger(self.__class__.__name__)
    
    async def create_adapter(self, config: AdapterConfig) -> Optional[Any]:
        """Create an adapter instance from configuration."""        try:
            # Check if instance already exists
            instance_key = f"{config.adapter_name}_{hash(str(config.config_params))}"
            if instance_key in self._instances:
                self.logger.info(f"Returning existing adapter instance: {config.adapter_name}")
                return self._instances[instance_key]
            
            # Get adapter class
            adapter_class = get_adapter_by_name(config.adapter_name)
            if not adapter_class:
                self.logger.error(f"Adapter not found: {config.adapter_name}")
                return None
            
            # Create instance with configuration
            if config.auth_config:
                instance = adapter_class(
                    credentials=config.auth_config,
                    **config.config_params
                )
            else:
                instance = adapter_class(**config.config_params)
            
            # Store instance and configuration
            self._instances[instance_key] = instance
            self._configs[instance_key] = config
            
            self.logger.info(f"✅ Created adapter instance: {config.adapter_name}")
            return instance
            
        except Exception as e:
            self.logger.error(f"Failed to create adapter {config.adapter_name}: {e}")
            return None
    
    async def create_content_adapter(self, content_type: str, **kwargs) -> Optional[Any]:
        """Create a content adapter for specific content type."""        adapter_mapping = {
            'audio': 'audio_content',
            'video': 'video_content', 
            'image': 'image_content',
            'text': 'text_content',
            'document': 'document_content'
        }
        
        adapter_name = adapter_mapping.get(content_type.lower())
        if not adapter_name:
            self.logger.error(f"Unsupported content type: {content_type}")
            return None
        
        config = AdapterConfig(
            adapter_name=adapter_name,
            adapter_type=AdapterType.CONTENT,
            config_params=kwargs
        )
        
        return await self.create_adapter(config)
    
    async def create_platform_adapter(self, platform: str, credentials: Dict[str, Any], **kwargs) -> Optional[Any]:
        """Create a platform adapter for specific social media platform."""        config = AdapterConfig(
            adapter_name=platform.lower(),
            adapter_type=AdapterType.PLATFORM,
            config_params=kwargs,
            auth_config=credentials
        )
        
        return await self.create_adapter(config)
    
    async def create_storage_adapter(self, storage_type: str, connection_config: Dict[str, Any], **kwargs) -> Optional[Any]:
        """Create a storage adapter for specific storage backend."""        config = AdapterConfig(
            adapter_name=storage_type.lower(),
            adapter_type=AdapterType.STORAGE,
            config_params={**connection_config, **kwargs}
        )
        
        return await self.create_adapter(config)
    
    def get_instance(self, adapter_name: str, config_hash: Optional[str] = None) -> Optional[Any]:
        """Get existing adapter instance."""        if config_hash:
            instance_key = f"{adapter_name}_{config_hash}"
        else:
            # Find any instance with this adapter name
            for key in self._instances:
                if key.startswith(f"{adapter_name}_"):
                    instance_key = key
                    break
            else:
                return None
        
        return self._instances.get(instance_key)
    
    def list_instances(self) -> Dict[str, AdapterConfig]:
        """List all active adapter instances."""        return {key: config for key, config in self._configs.items()}
    
    async def cleanup_instances(self):
        """Clean up all adapter instances."""        for instance_key, instance in self._instances.items():
            try:
                if hasattr(instance, 'disconnect'):
                    await instance.disconnect()
                elif hasattr(instance, 'close'):
                    await instance.close()
            except Exception as e:
                self.logger.warning(f"Error cleaning up {instance_key}: {e}")
        
        self._instances.clear()
        self._configs.clear()
        self.logger.info("✅ All adapter instances cleaned up")

class AdapterRegistry:
    """Registry for adapter discovery and metadata."""    
    def __init__(self):
        """Initialize the adapter registry."""        self.factory = AdapterFactory()
        self.manager = adapter_manager
        self.logger = logging.getLogger(self.__class__.__name__)
    
    def discover_adapters(self) -> Dict[AdapterType, List[str]]:
        """Discover all available adapters grouped by type."""        self.manager.initialize()
        
        discovered = {}
        for adapter_type in AdapterType:
            adapters = get_adapters_by_type(adapter_type)
            if adapters:
                discovered[adapter_type] = adapters
        
        return discovered
    
    def get_adapter_capabilities(self, adapter_name: str) -> Optional[Dict[str, Any]]:
        """Get comprehensive adapter capabilities and metadata."""        info = self.manager.get_adapter_info(adapter_name)
        if not info:
            return None
        
        return {
            'name': info.name,
            'type': info.adapter_type.value,
            'description': info.description,
            'supported_formats': info.supported_formats,
            'requires_auth': info.requires_auth,
            'enterprise_features': info.enterprise_features or [],
            'dependencies': info.dependencies or []
        }
    
    def search_adapters(self, 
                       adapter_type: Optional[AdapterType] = None,
                       format_support: Optional[str] = None,
                       requires_auth: Optional[bool] = None) -> List[str]:
        """Search adapters by criteria."""        all_adapters = self.manager.list_all_adapters()
        results = []
        
        for name, info in all_adapters.items():
            # Filter by type
            if adapter_type and info.adapter_type != adapter_type:
                continue
            
            # Filter by format support
            if format_support and format_support not in info.supported_formats:
                continue
            
            # Filter by auth requirements
            if requires_auth is not None and info.requires_auth != requires_auth:
                continue
            
            results.append(name)
        
        return results
    
    async def validate_adapter(self, adapter_name: str) -> Dict[str, Any]:
        """Validate adapter availability and functionality."""        try:
            # Check if adapter exists
            adapter_class = get_adapter_by_name(adapter_name)
            if not adapter_class:
                return {
                    'valid': False,
                    'error': f'Adapter {adapter_name} not found'
                }
            
            # Get adapter info
            info = self.get_adapter_capabilities(adapter_name)
            if not info:
                return {
                    'valid': False,
                    'error': f'No metadata found for {adapter_name}'
                }
            
            # Try to create minimal instance
            try:
                config = AdapterConfig(
                    adapter_name=adapter_name,
                    adapter_type=AdapterType(info['type']),
                    config_params={}
                )
                instance = await self.factory.create_adapter(config)
                
                return {
                    'valid': True,
                    'adapter_info': info,
                    'instance_created': instance is not None
                }
                
            except Exception as e:
                return {
                    'valid': False,
                    'error': f'Failed to create instance: {str(e)}',
                    'adapter_info': info
                }
                
        except Exception as e:
            return {
                'valid': False,
                'error': f'Validation failed: {str(e)}'
            }
    
    async def health_check(self) -> Dict[str, Any]:
        """Perform comprehensive health check of adapter system."""        start_time = datetime.now()
        
        # Discover all adapters
        discovered = self.discover_adapters()
        total_adapters = sum(len(adapters) for adapters in discovered.values())
        
        # Validate critical adapters
        critical_adapters = [
            'audio_content', 'video_content', 'image_content',
            'youtube', 'spotify', 'instagram',
            'rest_api', 'websocket',
            'postgresql', 'redis', 's3_storage'
        ]
        
        validation_results = {}
        for adapter_name in critical_adapters:
            try:
                result = await self.validate_adapter(adapter_name)
                validation_results[adapter_name] = result
            except Exception as e:
                validation_results[adapter_name] = {
                    'valid': False,
                    'error': str(e)
                }
        
        valid_critical = sum(1 for r in validation_results.values() if r.get('valid', False))
        
        duration = (datetime.now() - start_time).total_seconds()
        
        return {
            'status': 'healthy' if valid_critical >= len(critical_adapters) * 0.8 else 'degraded',
            'total_adapters': total_adapters,
            'adapters_by_type': {t.value: len(a) for t, a in discovered.items()},
            'critical_adapters': {
                'total': len(critical_adapters),
                'valid': valid_critical,
                'success_rate': (valid_critical / len(critical_adapters)) * 100
            },
            'validation_results': validation_results,
            'check_duration': duration,
            'timestamp': datetime.now().isoformat()
        }

# Global instances
adapter_factory = AdapterFactory()
adapter_registry = AdapterRegistry()

# Convenience functions
async def create_content_adapter(content_type: str, **kwargs):
    """Create a content adapter."""    return await adapter_factory.create_content_adapter(content_type, **kwargs)

async def create_platform_adapter(platform: str, credentials: Dict[str, Any], **kwargs):
    """Create a platform adapter."""    return await adapter_factory.create_platform_adapter(platform, credentials, **kwargs)

async def create_storage_adapter(storage_type: str, connection_config: Dict[str, Any], **kwargs):
    """Create a storage adapter."""    return await adapter_factory.create_storage_adapter(storage_type, connection_config, **kwargs)

def discover_adapters():
    """Discover all available adapters."""    return adapter_registry.discover_adapters()

def search_adapters(**criteria):
    """Search adapters by criteria."""    return adapter_registry.search_adapters(**criteria)

async def validate_system():
    """Validate entire adapter system."""    return await adapter_registry.health_check()

# Export all public functions and classes
__all__ = [
    'AdapterConfig',
    'AdapterFactory', 
    'AdapterRegistry',
    'adapter_factory',
    'adapter_registry',
    'create_content_adapter',
    'create_platform_adapter', 
    'create_storage_adapter',
    'discover_adapters',
    'search_adapters',
    'validate_system'
]
