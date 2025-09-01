#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Storage Module Index
===================

Professional storage module index for IA-Influencer-Agent crawlers.

Author: Fahed Mlaiel <mlaiel@live.de>
Team: Lead Dev IA + Backend Senior + ML Engineer + DBA + Security + Microservices + Audio + DevOps + IA Prompt Engineer
Copyright: All rights reserved. Unauthorized use, reproduction, or distribution prohibited.

WARNING: This code is protected by copyright law. Any unauthorized copying, 
distribution, or modification is strictly prohibited and will result in 
legal action. Contact mlaiel@live.de for licensing.

⚠️ PROPRIETARY SOFTWARE - UNAUTHORIZED ACCESS PROHIBITED

© 2025 IA Influencer Agent Development Team. All rights reserved.
This software is proprietary and confidential. Unauthorized reproduction, 
distribution, or reverse engineering is strictly prohibited by law.

This module provides the main entry point and factory functions for the 
ultra-advanced enterprise storage system designed for content creators,
influencers, musicians, bloggers, and photographers.

Author: Senior Backend Engineering Team
Created: August 2024
Version: 1.0.0 Enterprise Edition
"""
import asyncio
import logging
from typing import Dict, List, Optional, Any, Union, Type
from pathlib import Path
import yaml
import json

# Core storage imports
from .interfaces import (
    StorageProviderInterface,
    StorageMetadata,
    StorageQuery,
    StorageResult,
    HealthStatus,
    PerformanceMetrics,
    StorageProviderType
)

from .manager import (
    StorageManager,
    RoutingStrategy,
    LoadBalancer,
    FailoverManager
)

from .config import (
    StorageProviderConfig,
    StorageConfigurationManager,
    StorageProviderFactory,
    DatabaseConfig,
    FilesystemConfig,
    CacheConfig,
    ObjectStorageConfig,
    VectorConfig,
    TimeSeriesConfig
)

# Storage provider imports
from .database_storage import DatabaseStorageProvider, create_database_provider
from .filesystem_storage import FilesystemStorageProvider, create_filesystem_provider
from .cache_storage import CacheStorageProvider, create_cache_provider
from .object_storage import S3ObjectStorageProvider, create_object_storage_provider
from .analytics_storage import AnalyticsStorageProvider, create_analytics_storage
from .distribution_storage import DistributionStorageProvider, create_distribution_storage
from .licensing_storage import LicensingStorageProvider, create_licensing_storage
from .platform_storage import PlatformStorageProvider, create_platform_storage
from .vector_storage import VectorStorageProvider, create_vector_storage
from .timeseries_storage import TimeSeriesStorageProvider, create_timeseries_storage

# Configure logging
logger = logging.getLogger(__name__)

# Enterprise storage factory registry
STORAGE_PROVIDER_REGISTRY: Dict[str, Type[StorageProviderInterface]] = {
    "database": DatabaseStorageProvider,
    "postgresql": DatabaseStorageProvider,
    "mysql": DatabaseStorageProvider,
    "sqlite": DatabaseStorageProvider,
    "filesystem": FilesystemStorageProvider,
    "file_system": FilesystemStorageProvider,
    "cache": CacheStorageProvider,
    "redis": CacheStorageProvider,
    "memory": CacheStorageProvider,
    "object_storage": S3ObjectStorageProvider,
    "s3": S3ObjectStorageProvider,
    "minio": S3ObjectStorageProvider,
    "azure_blob": S3ObjectStorageProvider,
    "analytics": AnalyticsStorageProvider,
    "distribution": DistributionStorageProvider,
    "licensing": LicensingStorageProvider,
    "platform": PlatformStorageProvider,
    "vector": VectorStorageProvider,
    "timeseries": TimeSeriesStorageProvider,
    "time_series": TimeSeriesStorageProvider
}

# Creator factory functions registry
CREATOR_FACTORY_REGISTRY: Dict[str, callable] = {
    "database": create_database_provider,
    "postgresql": create_database_provider,
    "mysql": create_database_provider,
    "sqlite": create_database_provider,
    "filesystem": create_filesystem_provider,
    "file_system": create_filesystem_provider,
    "cache": create_cache_provider,
    "redis": create_cache_provider,
    "memory": create_cache_provider,
    "object_storage": create_object_storage_provider,
    "s3": create_object_storage_provider,
    "minio": create_object_storage_provider,
    "azure_blob": create_object_storage_provider,
    "analytics": create_analytics_storage,
    "distribution": create_distribution_storage,
    "licensing": create_licensing_storage,
    "platform": create_platform_storage,
    "vector": create_vector_storage,
    "timeseries": create_timeseries_storage,
    "time_series": create_timeseries_storage
}


class EnterpriseStorageFactory:
    """
    Ultra-advanced enterprise storage factory for creating and managing
    storage providers across multiple backends and use cases.
    
    This factory supports the complete content creator ecosystem:
    - Content upload and processing
    - AI-powered protection and optimization
    - Multi-platform distribution
    - Analytics and business intelligence
    - Licensing and monetization
    """
    
    def __init__(self):
        self._logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        self._config_manager = StorageConfigurationManager()
        self._provider_factory = StorageProviderFactory()
        self._initialized_providers: Dict[str, StorageProviderInterface] = {}
    
    async def create_storage_manager(
        self,
        config_path: Optional[Union[str, Path]] = None,
        config_dict: Optional[Dict[str, Any]] = None,
        routing_strategy: str = "least_load",
        enable_failover: bool = True,
        enable_monitoring: bool = True
    ) -> StorageManager:
        """
        Create a fully configured enterprise storage manager.
        
        Args:
            config_path: Path to YAML/JSON configuration file
            config_dict: Direct configuration dictionary
            routing_strategy: Routing strategy ("priority", "round_robin", "least_load")
            enable_failover: Enable automatic failover management
            enable_monitoring: Enable performance monitoring
            
        Returns:
            Configured StorageManager instance
        """
        try:
            # Load configuration
            if config_path:
                config = await self._load_config_from_file(config_path)
            elif config_dict:
                config = config_dict
            else:
                config = self._get_default_config()
            
            # Create storage manager
            manager = StorageManager(
                routing_strategy=RoutingStrategy[routing_strategy.upper()],
                enable_failover=enable_failover,
                enable_monitoring=enable_monitoring
            )
            
            # Initialize providers from configuration
            providers = await self._create_providers_from_config(config)
            await manager.initialize(providers)
            
            self._logger.info(
                f"Created enterprise storage manager with {len(providers)} providers"
            )
            
            return manager
            
        except Exception as e:
            self._logger.error(f"Failed to create storage manager: {e}")
            raise
    
    async def create_provider(
        self,
        provider_type: str,
        provider_id: str,
        config: Dict[str, Any]
    ) -> StorageProviderInterface:
        """
        Create a single storage provider instance.
        
        Args:
            provider_type: Type of storage provider
            provider_id: Unique identifier for the provider
            config: Provider-specific configuration
            
        Returns:
            Configured storage provider instance
        """
        try:
            if provider_type not in STORAGE_PROVIDER_REGISTRY:
                raise ValueError(f"Unknown provider type: {provider_type}")
            
            # Use factory function if available
            if provider_type in CREATOR_FACTORY_REGISTRY:
                factory_func = CREATOR_FACTORY_REGISTRY[provider_type]
                provider = await factory_func(provider_id, **config)
            else:
                # Direct instantiation
                provider_class = STORAGE_PROVIDER_REGISTRY[provider_type]
                provider = provider_class(provider_id)
                await provider.initialize(config)
            
            self._initialized_providers[provider_id] = provider
            
            self._logger.info(
                f"Created {provider_type} provider '{provider_id}'"
            )
            
            return provider
            
        except Exception as e:
            self._logger.error(
                f"Failed to create provider {provider_id} ({provider_type}): {e}"
            )
            raise
    
    async def create_content_creator_storage(
        self,
        creator_id: str,
        creator_type: str = "influencer",
        platforms: Optional[List[str]] = None,
        enable_analytics: bool = True,
        enable_distribution: bool = True,
        enable_licensing: bool = True
    ) -> StorageManager:
        """
        Create specialized storage configuration for content creators.
        
        Args:
            creator_id: Unique creator identifier
            creator_type: Type of creator (influencer, musician, blogger, photographer)
            platforms: Target social media platforms
            enable_analytics: Enable analytics storage
            enable_distribution: Enable distribution storage
            enable_licensing: Enable licensing storage
            
        Returns:
            Specialized StorageManager for content creators
        """
        try:
            platforms = platforms or ["youtube", "instagram", "tiktok", "twitter"]
            
            # Base storage providers
            providers = []
            
            # Primary database for content metadata
            db_provider = await self.create_provider(
                "database",
                f"{creator_id}_primary_db",
                {
                    "database_url": f"postgresql://localhost/creator_{creator_id}",
                    "pool_size": 10,
                    "enable_compression": True
                }
            )
            providers.append(db_provider)
            
            # Filesystem for content files
            fs_provider = await self.create_provider(
                "filesystem",
                f"{creator_id}_content_files",
                {
                    "base_path": f"/data/creators/{creator_id}/content",
                    "enable_compression": True,
                    "enable_indexing": True
                }
            )
            providers.append(fs_provider)
            
            # Redis cache for performance
            cache_provider = await self.create_provider(
                "cache",
                f"{creator_id}_cache",
                {
                    "redis_url": "redis://localhost:6379",
                    "database": hash(creator_id) % 16,
                    "default_ttl": 3600
                }
            )
            providers.append(cache_provider)
            
            # Object storage for media files
            s3_provider = await self.create_provider(
                "s3",
                f"{creator_id}_media_storage",
                {
                    "bucket_name": f"creator-{creator_id}-media",
                    "enable_encryption": True,
                    "multipart_threshold": 64 * 1024 * 1024  # 64MB
                }
            )
            providers.append(s3_provider)
            
            # Vector storage for AI features
            vector_provider = await self.create_provider(
                "vector",
                f"{creator_id}_ai_vectors",
                {
                    "dimension": 512,
                    "index_type": "faiss",
                    "similarity_metric": "cosine"
                }
            )
            providers.append(vector_provider)
            
            # Analytics storage
            if enable_analytics:
                analytics_provider = await self.create_provider(
                    "analytics",
                    f"{creator_id}_analytics",
                    {
                        "retention_days": 365,
                        "aggregation_intervals": ["hourly", "daily", "weekly"],
                        "enable_forecasting": True
                    }
                )
                providers.append(analytics_provider)
            
            # Distribution storage
            if enable_distribution:
                distribution_provider = await self.create_provider(
                    "distribution",
                    f"{creator_id}_distribution",
                    {
                        "platforms": platforms,
                        "enable_scheduling": True,
                        "enable_optimization": True
                    }
                )
                providers.append(distribution_provider)
            
            # Licensing storage
            if enable_licensing:
                licensing_provider = await self.create_provider(
                    "licensing",
                    f"{creator_id}_licensing",
                    {
                        "enable_royalty_tracking": True,
                        "enable_compliance_monitoring": True,
                        "enable_automated_payments": True
                    }
                )
                providers.append(licensing_provider)
            
            # Platform-specific storage
            platform_provider = await self.create_provider(
                "platform",
                f"{creator_id}_platforms",
                {
                    "platforms": platforms,
                    "enable_sync": True,
                    "enable_optimization": True
                }
            )
            providers.append(platform_provider)
            
            # Time-series storage for metrics
            timeseries_provider = await self.create_provider(
                "timeseries",
                f"{creator_id}_metrics",
                {
                    "retention_days": 730,  # 2 years
                    "compression_enabled": True,
                    "aggregation_functions": ["sum", "avg", "max", "min"]
                }
            )
            providers.append(timeseries_provider)
            
            # Create specialized storage manager
            manager = StorageManager(
                routing_strategy=RoutingStrategy.LEAST_LOAD,
                enable_failover=True,
                enable_monitoring=True
            )
            
            await manager.initialize(providers)
            
            self._logger.info(
                f"Created specialized storage for {creator_type} '{creator_id}' "
                f"with {len(providers)} providers for platforms: {platforms}"
            )
            
            return manager
            
        except Exception as e:
            self._logger.error(
                f"Failed to create content creator storage for {creator_id}: {e}"
            )
            raise
    
    async def _load_config_from_file(self, config_path: Union[str, Path]) -> Dict[str, Any]:
        """Load configuration from YAML or JSON file."""
        config_path = Path(config_path)
        
        if not config_path.exists():
            raise FileNotFoundError(f"Configuration file not found: {config_path}")
        
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                if config_path.suffix.lower() in ['.yaml', '.yml']:
                    return yaml.safe_load(f)
                elif config_path.suffix.lower() == '.json':
                    return json.load(f)
                else:
                    raise ValueError(f"Unsupported config file format: {config_path.suffix}")
                    
        except Exception as e:
            self._logger.error(f"Failed to load configuration from {config_path}: {e}")
            raise
    
    async def _create_providers_from_config(
        self, 
        config: Dict[str, Any]
    ) -> List[StorageProviderInterface]:
        """Create storage providers from configuration dictionary."""
        providers = []
        
        storage_config = config.get('storage', {})
        provider_configs = storage_config.get('providers', [])
        
        for provider_config in provider_configs:
            provider_type = provider_config.get('provider_type')
            provider_id = provider_config.get('provider_id')
            
            if not provider_type or not provider_id:
                self._logger.warning(f"Skipping invalid provider config: {provider_config}")
                continue
            
            # Extract provider-specific configuration
            config_keys = [
                'database_config', 'filesystem_config', 'cache_config',
                'object_storage_config', 'vector_config', 'timeseries_config',
                'analytics_config', 'distribution_config', 'licensing_config',
                'platform_config'
            ]
            
            provider_specific_config = {}
            for key in config_keys:
                if key in provider_config:
                    provider_specific_config.update(provider_config[key])
            
            # Add general configuration
            general_config = {k: v for k, v in provider_config.items() 
                            if k not in config_keys + ['provider_type', 'provider_id']}
            provider_specific_config.update(general_config)
            
            try:
                provider = await self.create_provider(
                    provider_type, 
                    provider_id, 
                    provider_specific_config
                )
                providers.append(provider)
                
            except Exception as e:
                self._logger.error(
                    f"Failed to create provider {provider_id} ({provider_type}): {e}"
                )
                continue
        
        return providers
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Get default enterprise storage configuration."""
        return {
            "storage": {
                "providers": [
                    {
                        "provider_id": "primary_database",
                        "provider_type": "postgresql",
                        "enabled": True,
                        "priority": 100,
                        "database_config": {
                            "database_url": "postgresql://localhost/ia_influencer",
                            "pool_size": 20,
                            "enable_compression": True
                        }
                    },
                    {
                        "provider_id": "content_cache",
                        "provider_type": "redis",
                        "enabled": True,
                        "priority": 90,
                        "cache_config": {
                            "redis_url": "redis://localhost:6379",
                            "database": 0,
                            "default_ttl": 3600
                        }
                    },
                    {
                        "provider_id": "media_storage",
                        "provider_type": "s3",
                        "enabled": True,
                        "priority": 80,
                        "object_storage_config": {
                            "bucket_name": "ia-influencer-media",
                            "enable_encryption": True
                        }
                    }
                ]
            }
        }


# Global factory instance
_enterprise_factory = EnterpriseStorageFactory()


# Convenience functions for easy access
async def create_storage_manager(
    config_path: Optional[Union[str, Path]] = None,
    config_dict: Optional[Dict[str, Any]] = None,
    routing_strategy: str = "least_load",
    enable_failover: bool = True,
    enable_monitoring: bool = True
) -> StorageManager:
    """
    Create enterprise storage manager with advanced configuration.
    
    This is the main entry point for creating a storage manager for
    the IA Influencer Agent platform.
    """
    return await _enterprise_factory.create_storage_manager(
        config_path=config_path,
        config_dict=config_dict,
        routing_strategy=routing_strategy,
        enable_failover=enable_failover,
        enable_monitoring=enable_monitoring
    )


async def create_content_creator_storage(
    creator_id: str,
    creator_type: str = "influencer",
    platforms: Optional[List[str]] = None,
    enable_analytics: bool = True,
    enable_distribution: bool = True,
    enable_licensing: bool = True
) -> StorageManager:
    """
    Create specialized storage for content creators.
    
    Optimized for influencers, musicians, bloggers, and photographers
    with support for multi-platform distribution and monetization.
    """
    return await _enterprise_factory.create_content_creator_storage(
        creator_id=creator_id,
        creator_type=creator_type,
        platforms=platforms,
        enable_analytics=enable_analytics,
        enable_distribution=enable_distribution,
        enable_licensing=enable_licensing
    )


async def create_provider(
    provider_type: str,
    provider_id: str,
    config: Dict[str, Any]
) -> StorageProviderInterface:
    """Create a single storage provider instance."""
    return await _enterprise_factory.create_provider(
        provider_type=provider_type,
        provider_id=provider_id,
        config=config
    )


def get_available_provider_types() -> List[str]:
    """Get list of available storage provider types."""
    return list(STORAGE_PROVIDER_REGISTRY.keys())


def get_provider_class(provider_type: str) -> Type[StorageProviderInterface]:
    """Get storage provider class by type."""
    if provider_type not in STORAGE_PROVIDER_REGISTRY:
        raise ValueError(f"Unknown provider type: {provider_type}")
    return STORAGE_PROVIDER_REGISTRY[provider_type]


# Export main classes and functions
__all__ = [
    # Main factory
    "EnterpriseStorageFactory",
    
    # Convenience functions
    "create_storage_manager",
    "create_content_creator_storage", 
    "create_provider",
    "get_available_provider_types",
    "get_provider_class",
    
    # Core classes (re-exported for convenience)
    "StorageManager",
    "StorageProviderInterface",
    "StorageMetadata",
    "StorageQuery",
    "StorageResult",
    "HealthStatus",
    "PerformanceMetrics",
    "RoutingStrategy",
    
    # Configuration classes
    "StorageProviderConfig",
    "StorageConfigurationManager",
    "StorageProviderFactory",
    "DatabaseConfig",
    "FilesystemConfig", 
    "CacheConfig",
    "ObjectStorageConfig",
    "VectorConfig",
    "TimeSeriesConfig",
    
    # Provider classes
    "DatabaseStorageProvider",
    "FilesystemStorageProvider",
    "CacheStorageProvider",
    "S3ObjectStorageProvider",
    "AnalyticsStorageProvider",
    "DistributionStorageProvider",
    "LicensingStorageProvider",
    "PlatformStorageProvider",
    "VectorStorageProvider",
    "TimeSeriesStorageProvider"
]


if __name__ == "__main__":
    # Example usage for testing
    async def main():
        """Example usage of the enterprise storage system."""
        
        # Create a simple storage manager
        manager = await create_storage_manager(routing_strategy="least_load")
        
        # Create specialized storage for a content creator
        creator_storage = await create_content_creator_storage(
            creator_id="creator_123",
            creator_type="musician",
            platforms=["youtube", "spotify", "instagram"],
            enable_analytics=True,
            enable_distribution=True,
            enable_licensing=True
        )
        
        print(f"Created storage manager with {len(manager._providers)} providers")
        print(f"Created creator storage with {len(creator_storage._providers)} providers")
        
        # Health check
        health = await manager.get_health_status()
        print(f"Storage system health: {health}")
    
    # Run example
    asyncio.run(main())
