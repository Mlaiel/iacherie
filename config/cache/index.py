"""Cache Configuration Index for IA-Influencer Agent Platform
===========================================================

Centralized access to all cache configuration components and utilities
for simplified integration and management.

Author: Fahed Mlaiel <mlaiel@live.de>
Project: IA-Influencer Agent + Content Protection Platform
Team: Lead Dev IA + Backend Senior + ML Engineer + DBA + Security + Microservices + Audio + DevOps

Copyright Notice:
This code is the intellectual property of Fahed Mlaiel.
Any unauthorized use, reproduction, or distribution of this code
without explicit written permission from the author is strictly prohibited.

Contact: mlaiel@live.de for licensing inquiries.
"""

from typing import Dict, Any, Optional, Union
from enum import Enum
import os
from dataclasses import dataclass

from . import (
    # Redis
    RedisCacheConfig,
    REDIS_DEVELOPMENT_CONFIG,
    REDIS_PRODUCTION_CONFIG,
    REDIS_TESTING_CONFIG,
    
    # Memcached
    MemcachedConfig,
    MEMCACHED_DEVELOPMENT_CONFIG,
    MEMCACHED_PRODUCTION_CONFIG,
    MEMCACHED_TESTING_CONFIG,
    
    # Strategies
    CacheStrategiesConfig,
    STRATEGIES_DEVELOPMENT_CONFIG,
    STRATEGIES_PRODUCTION_CONFIG,
    STRATEGIES_TESTING_CONFIG,
    
    # Invalidation
    CacheInvalidationConfig,
    INVALIDATION_DEVELOPMENT_CONFIG,
    INVALIDATION_PRODUCTION_CONFIG,
    
    # Distributed
    DistributedCacheConfig,
    SINGLE_REGION_CONFIG,
    MULTI_REGION_CONFIG,
    HIGH_AVAILABILITY_CONFIG,
    
    # Warming
    CacheWarmingConfig,
    WARMING_DEVELOPMENT_CONFIG,
    WARMING_PRODUCTION_CONFIG,
    
    # Metrics
    CacheMetricsConfig,
    METRICS_DEVELOPMENT_CONFIG,
    METRICS_PRODUCTION_CONFIG,
    
    # Compression
    CacheCompressionConfig,
    COMPRESSION_DEVELOPMENT_CONFIG,
    COMPRESSION_PRODUCTION_CONFIG,
    
    # Content Fingerprint - NEW
    ContentFingerprintCacheConfig,
    CONTENT_FINGERPRINT_DEVELOPMENT_CONFIG,
    CONTENT_FINGERPRINT_PRODUCTION_CONFIG,
    CONTENT_FINGERPRINT_TESTING_CONFIG,
    
    # ML Model Cache - NEW
    MLModelCacheConfig,
    ML_MODEL_DEVELOPMENT_CONFIG,
    ML_MODEL_PRODUCTION_CONFIG,
    ML_MODEL_TESTING_CONFIG,
    
    # Platform API Cache - NEW
    PlatformAPICacheConfig,
    PLATFORM_API_DEVELOPMENT_CONFIG,
    PLATFORM_API_PRODUCTION_CONFIG,
    PLATFORM_API_TESTING_CONFIG,
    
    # Multi-Tenant Cache - NEW
    MultiTenantCacheConfig,
    MULTI_TENANT_DEVELOPMENT_CONFIG,
    MULTI_TENANT_PRODUCTION_CONFIG,
    MULTI_TENANT_TESTING_CONFIG,
    
    # Content Vector Cache - NEW
    ContentVectorCacheConfig,
    CONTENT_VECTOR_DEVELOPMENT_CONFIG,
    CONTENT_VECTOR_PRODUCTION_CONFIG,
    CONTENT_VECTOR_TESTING_CONFIG,
    
    # Revenue Cache - NEW
    RevenueCacheConfig,
    REVENUE_DEVELOPMENT_CONFIG,
    REVENUE_PRODUCTION_CONFIG,
    REVENUE_TESTING_CONFIG
)


class Environment(str, Enum):
    """
Deployment environments"""

    DEVELOPMENT = "development"
    TESTING = "testing"
    PRODUCTION = "production"
    STAGING = "staging"


class CacheType(str, Enum):
    """Cache system types"""

    REDIS = "redis"
    MEMCACHED = "memcached"
    HYBRID = "hybrid"  # Both Redis and Memcached


@dataclass
class CacheConfigurationBundle:
    """Complete cache configuration bundle for an environment"""
    environment: Environment
    cache_type: CacheType
    
    # Core configurations
    redis_config: Optional[RedisCacheConfig] = None
    memcached_config: Optional[MemcachedConfig] = None
    strategies_config: Optional[CacheStrategiesConfig] = None
    invalidation_config: Optional[CacheInvalidationConfig] = None
    distributed_config: Optional[DistributedCacheConfig] = None
    warming_config: Optional[CacheWarmingConfig] = None
    metrics_config: Optional[CacheMetricsConfig] = None
    compression_config: Optional[CacheCompressionConfig] = None
    
    # NEW IA-Influencer specific configurations
    content_fingerprint_config: Optional[ContentFingerprintCacheConfig] = None
    ml_model_config: Optional[MLModelCacheConfig] = None
    platform_api_config: Optional[PlatformAPICacheConfig] = None
    multi_tenant_config: Optional[MultiTenantCacheConfig] = None
    content_vector_config: Optional[ContentVectorCacheConfig] = None
    revenue_config: Optional[RevenueCacheConfig] = None
    
    def validate(self) -> bool:
        """
Validate configuration bundle consistency"""
        if self.cache_type == CacheType.REDIS and not self.redis_config:
            return False
        
        if self.cache_type == CacheType.MEMCACHED and not self.memcached_config:
            return False
        
        if self.cache_type == CacheType.HYBRID:
            if not (self.redis_config and self.memcached_config):
                return False
        
        return True
    
    def get_summary(self) -> Dict[str, Any]:
        """
Get configuration bundle summary"""
        return {
            "environment": self.environment,
            "cache_type": self.cache_type,
            "components": {
                # Core components
                "redis": self.redis_config is not None,
                "memcached": self.memcached_config is not None,
                "strategies": self.strategies_config is not None,
                "invalidation": self.invalidation_config is not None,
                "distributed": self.distributed_config is not None,
                "warming": self.warming_config is not None,
                "metrics": self.metrics_config is not None,
                "compression": self.compression_config is not None,
                # NEW IA-Influencer components
                "content_fingerprint": self.content_fingerprint_config is not None,
                "ml_model": self.ml_model_config is not None,
                "platform_api": self.platform_api_config is not None,
                "multi_tenant": self.multi_tenant_config is not None,
                "content_vector": self.content_vector_config is not None,
                "revenue": self.revenue_config is not None
            },
            "validated": self.validate()
        }


class CacheConfigurationFactory:
    """Factory for creating complete cache configuration bundles"""
    
    @staticmethod
    def create_development_bundle(cache_type: CacheType = CacheType.REDIS) -> CacheConfigurationBundle:
        """
Create development environment configuration bundle"""
        bundle = CacheConfigurationBundle(
            environment=Environment.DEVELOPMENT,
            cache_type=cache_type
        )
        
        if cache_type in [CacheType.REDIS, CacheType.HYBRID]:
            bundle.redis_config = REDIS_DEVELOPMENT_CONFIG
        
        if cache_type in [CacheType.MEMCACHED, CacheType.HYBRID]:
            bundle.memcached_config = MEMCACHED_DEVELOPMENT_CONFIG
        
        # Core configurations
        bundle.strategies_config = STRATEGIES_DEVELOPMENT_CONFIG
        bundle.invalidation_config = INVALIDATION_DEVELOPMENT_CONFIG
        bundle.distributed_config = SINGLE_REGION_CONFIG
        bundle.warming_config = WARMING_DEVELOPMENT_CONFIG
        bundle.metrics_config = METRICS_DEVELOPMENT_CONFIG
        bundle.compression_config = COMPRESSION_DEVELOPMENT_CONFIG
        
        # NEW IA-Influencer configurations
        bundle.content_fingerprint_config = CONTENT_FINGERPRINT_DEVELOPMENT_CONFIG
        bundle.ml_model_config = ML_MODEL_DEVELOPMENT_CONFIG
        bundle.platform_api_config = PLATFORM_API_DEVELOPMENT_CONFIG
        bundle.multi_tenant_config = MULTI_TENANT_DEVELOPMENT_CONFIG
        bundle.content_vector_config = CONTENT_VECTOR_DEVELOPMENT_CONFIG
        bundle.revenue_config = REVENUE_DEVELOPMENT_CONFIG
        
        return bundle
    
    @staticmethod
    def create_production_bundle(cache_type: CacheType = CacheType.HYBRID,
                               multi_region: bool = True) -> CacheConfigurationBundle:
        """
Create production environment configuration bundle"""
        bundle = CacheConfigurationBundle(
            environment=Environment.PRODUCTION,
            cache_type=cache_type
        )
        
        if cache_type in [CacheType.REDIS, CacheType.HYBRID]:
            bundle.redis_config = REDIS_PRODUCTION_CONFIG
        
        if cache_type in [CacheType.MEMCACHED, CacheType.HYBRID]:
            bundle.memcached_config = MEMCACHED_PRODUCTION_CONFIG
        
        bundle.strategies_config = STRATEGIES_PRODUCTION_CONFIG
        bundle.invalidation_config = INVALIDATION_PRODUCTION_CONFIG
        
        if multi_region:
            bundle.distributed_config = MULTI_REGION_CONFIG
        else:
            bundle.distributed_config = HIGH_AVAILABILITY_CONFIG
        
        bundle.warming_config = WARMING_PRODUCTION_CONFIG
        bundle.metrics_config = METRICS_PRODUCTION_CONFIG
        bundle.compression_config = COMPRESSION_PRODUCTION_CONFIG
        
        return bundle
    
    @staticmethod
    def create_testing_bundle(cache_type: CacheType = CacheType.REDIS) -> CacheConfigurationBundle:
        """
Create testing environment configuration bundle"""
        bundle = CacheConfigurationBundle(
            environment=Environment.TESTING,
            cache_type=cache_type
        )
        
        if cache_type in [CacheType.REDIS, CacheType.HYBRID]:
            bundle.redis_config = REDIS_TESTING_CONFIG
        
        if cache_type in [CacheType.MEMCACHED, CacheType.HYBRID]:
            bundle.memcached_config = MEMCACHED_TESTING_CONFIG
        
        bundle.strategies_config = STRATEGIES_TESTING_CONFIG
        bundle.distributed_config = SINGLE_REGION_CONFIG
        
        # Minimal configuration for testing
        bundle.warming_config = WARMING_DEVELOPMENT_CONFIG
        bundle.metrics_config = METRICS_DEVELOPMENT_CONFIG
        bundle.compression_config = COMPRESSION_DEVELOPMENT_CONFIG
        
        return bundle
    
    @staticmethod
    def create_custom_bundle(environment: Environment,
                           cache_type: CacheType,
                           **component_configs) -> CacheConfigurationBundle:
        """
Create custom configuration bundle"""
        bundle = CacheConfigurationBundle(
            environment=environment,
            cache_type=cache_type
        )
        
        # Apply custom configurations
        for component, config in component_configs.items():
            if hasattr(bundle, component):
                setattr(bundle, component, config)
        
        return bundle


class CacheConfigurationManager:
    """
Manager for cache configurations across the application"""
    
    def __init__(self):
        self._bundles: Dict[str, CacheConfigurationBundle] = {}
        self._active_bundle: Optional[CacheConfigurationBundle] = None
        self._environment = self._detect_environment()
    
    def _detect_environment(self) -> Environment:
        """
Detect current environment from environment variables"""
        env = os.getenv("ENVIRONMENT", "development").lower()
        
        if env in ["prod", "production"]:
            return Environment.PRODUCTION
        elif env in ["test", "testing"]:
            return Environment.TESTING
        elif env in ["stage", "staging"]:
            return Environment.STAGING
        else:
            return Environment.DEVELOPMENT
    
    def register_bundle(self, name: str, bundle: CacheConfigurationBundle):
        """Register a configuration bundle"""
        if not bundle.validate():
            raise ValueError(f"Invalid configuration bundle: {name}")
        
        self._bundles[name] = bundle
    
    def get_bundle(self, name: str) -> Optional[CacheConfigurationBundle]:
        """Get registered configuration bundle"""
        return self._bundles.get(name)
    
    def set_active_bundle(self, name: str):
        """
Set active configuration bundle"""
        if name not in self._bundles:
            raise ValueError(f"Bundle not found: {name}")
        
        self._active_bundle = self._bundles[name]
    
    def get_active_bundle(self) -> Optional[CacheConfigurationBundle]:
        """Get active configuration bundle"""
        return self._active_bundle
    
    def auto_configure(self, cache_type: CacheType = None) -> CacheConfigurationBundle:
        """
Auto-configure based on detected environment"""
        if cache_type is None:
            cache_type = CacheType.REDIS if self._environment == Environment.TESTING else CacheType.HYBRID
        
        if self._environment == Environment.PRODUCTION:
            bundle = CacheConfigurationFactory.create_production_bundle(cache_type)
        elif self._environment == Environment.TESTING:
            bundle = CacheConfigurationFactory.create_testing_bundle(cache_type)
        else:  # Development or Staging
            bundle = CacheConfigurationFactory.create_development_bundle(cache_type)
        
        bundle_name = f"auto_{self._environment}_{cache_type}"
        self.register_bundle(bundle_name, bundle)
        self.set_active_bundle(bundle_name)
        
        return bundle
    
    def get_configuration_summary(self) -> Dict[str, Any]:
        """Get complete configuration summary"""
        return {
            "detected_environment": self._environment,
            "registered_bundles": list(self._bundles.keys()),
            "active_bundle": self._active_bundle.get_summary() if self._active_bundle else None,
            "total_bundles": len(self._bundles)
        }
    
    def validate_all_bundles(self) -> Dict[str, bool]:
        """Validate all registered bundles"""
        return {name: bundle.validate() for name, bundle in self._bundles.items()}


# Global configuration manager instance
config_manager = CacheConfigurationManager()

# Convenience functions for quick setup
def get_default_config(environment: Environment = None,
                      cache_type: CacheType = None) -> CacheConfigurationBundle:
    """
Get default configuration for environment"""
    if environment is None:
        environment = config_manager._detect_environment()
    
    if cache_type is None:
        cache_type = CacheType.REDIS if environment == Environment.TESTING else CacheType.HYBRID
    
    if environment == Environment.PRODUCTION:
        return CacheConfigurationFactory.create_production_bundle(cache_type)
    elif environment == Environment.TESTING:
        return CacheConfigurationFactory.create_testing_bundle(cache_type)
    else:
        return CacheConfigurationFactory.create_development_bundle(cache_type)


def setup_cache_config(environment: Environment = None,
                      cache_type: CacheType = None,
                      auto_activate: bool = True) -> CacheConfigurationBundle:
    """
Setup cache configuration with automatic detection"""
    bundle = config_manager.auto_configure(cache_type)
    
    if auto_activate:
        # Additional setup logic would go here
        # e.g., initialize connections, start monitoring, etc.
        pass
    
    return bundle


# Pre-configured bundles for common scenarios
ENTERPRISE_PRODUCTION_BUNDLE = CacheConfigurationFactory.create_production_bundle(
    CacheType.HYBRID, multi_region=True
)

SIMPLE_PRODUCTION_BUNDLE = CacheConfigurationFactory.create_production_bundle(
    CacheType.REDIS, multi_region=False
)

DEVELOPMENT_BUNDLE = CacheConfigurationFactory.create_development_bundle(
    CacheType.REDIS
)

TESTING_BUNDLE = CacheConfigurationFactory.create_testing_bundle(
    CacheType.REDIS
)

# Register default bundles
config_manager.register_bundle("enterprise_production", ENTERPRISE_PRODUCTION_BUNDLE)
config_manager.register_bundle("simple_production", SIMPLE_PRODUCTION_BUNDLE)
config_manager.register_bundle("development", DEVELOPMENT_BUNDLE)
config_manager.register_bundle("testing", TESTING_BUNDLE)


__all__ = [
    'Environment',
    'CacheType',
    'CacheConfigurationBundle',
    'CacheConfigurationFactory',
    'CacheConfigurationManager',
    'config_manager',
    'get_default_config',
    'setup_cache_config',
    'ENTERPRISE_PRODUCTION_BUNDLE',
    'SIMPLE_PRODUCTION_BUNDLE',
    'DEVELOPMENT_BUNDLE',
    'TESTING_BUNDLE'
]
