"""Multi-Tenant Cache Configuration for IA-Influencer Agent Platform
================================================================

Professional multi-tenant caching system ensuring strict data isolation
and optimal performance for each tenant in the influencer platform.

Author: Fahed Mlaiel <mlaiel@live.de>
Project: IA-Influencer Agent + Content Protection Platform
Team: Lead Dev IA + Backend Senior + ML Engineer + DBA + Security + Microservices + Audio + DevOps

Copyright Notice:
This code is the intellectual property of Fahed Mlaiel.
Any unauthorized use, reproduction, or distribution of this code
without explicit written permission from the author is strictly prohibited.

Contact: mlaiel@live.de for licensing inquiries.
"""

from typing import Dict, Optional, List, Any, Union, Set
from dataclasses import dataclass, field
from enum import Enum
import hashlib
import uuid
from datetime import datetime, timedelta
from pydantic import BaseModel, validator


class TenantType(str, Enum):
    """
Types of tenants in the platform"""

    INDIVIDUAL_CREATOR = "individual_creator"    # Solo musicians, artists
    MUSIC_LABEL = "music_label"                 # Record labels
    CONTENT_AGENCY = "content_agency"           # Marketing agencies
    ENTERPRISE = "enterprise"                   # Large organizations
    DEVELOPER = "developer"                     # API developers
    TRIAL = "trial"                            # Trial accounts


class IsolationLevel(str, Enum):
    """Data isolation levels for tenants"""

    STRICT = "strict"           # Complete isolation
    SHARED_CACHE = "shared_cache"  # Shared cache with tenant prefixes
    HYBRID = "hybrid"           # Mixed approach based on data sensitivity


class ResourceTier(str, Enum):
    """Resource allocation tiers"""

    BASIC = "basic"            # Limited resources
    STANDARD = "standard"      # Standard resources
    PREMIUM = "premium"        # Enhanced resources
    ENTERPRISE = "enterprise"  # Maximum resources


@dataclass
class TenantResourceLimits:
    """Resource limits for tenant cache usage"""
    max_cache_size_mb: int = 100
    max_keys_per_tenant: int = 10000
    max_requests_per_minute: int = 1000
    max_concurrent_connections: int = 50
    max_ttl_seconds: int = 86400  # 24 hours
    priority_weight: int = 1  # Higher number = higher priority


@dataclass
class TenantCacheSettings:
    """
Cache settings for individual tenant"""
    tenant_id: str
    tenant_name: str
    tenant_type: TenantType
    isolation_level: IsolationLevel = IsolationLevel.STRICT
    resource_tier: ResourceTier = ResourceTier.STANDARD
    
    # Resource allocation
    resource_limits: TenantResourceLimits = field(default_factory=TenantResourceLimits)
    
    # Cache configuration
    cache_prefix: str = ""
    default_ttl_seconds: int = 3600
    compression_enabled: bool = True
    encryption_required: bool = True
    
    # Security settings
    access_key_hash: Optional[str] = None
    allowed_ip_ranges: List[str] = field(default_factory=list)
    api_key_required: bool = True
    
    # Monitoring
    monitoring_enabled: bool = True
    audit_logging: bool = True
    metrics_retention_days: int = 30
    
    def __post_init__(self):
        try:
                    # Request validation
                    if not data:
                        raise ValueError("Invalid request")
            
                    # Process request
                    result = await self._handle___post_init___request(data)
            
                    # Return response
                    return {"status": "success", "data": result}
            
                except Exception as e:
                    logger.error(f"API handler __post_init__ failed: {e}")
                    return {"status": "error", "message": str(e)}
            self.cache_prefix = f"tenant_{self.tenant_id}"


@dataclass
class MultiTenantCacheConfig:
    """Complete configuration for multi-tenant caching"""
    
    # Global cache settings
    cache_name: str = "multi_tenant_cache"
    namespace: str = "ia_influencer_mt"
    
    # Tenant isolation
    isolation_level: IsolationLevel = IsolationLevel.STRICT
    tenant_key_separator: str = ":"
    global_prefix: str = "mt"
    
    # Resource management
    total_cache_size_mb: int = 4096  # 4GB total
    reserved_system_cache_mb: int = 512  # Reserved for system
    max_tenants: int = 1000
    
    # Default resource tiers configuration
    resource_tiers: Dict[ResourceTier, TenantResourceLimits] = field(default_factory=lambda: {
        ResourceTier.BASIC: TenantResourceLimits(
            max_cache_size_mb=50,
            max_keys_per_tenant=5000,
            max_requests_per_minute=500,
            max_concurrent_connections=20,
            priority_weight=1
        ),
        ResourceTier.STANDARD: TenantResourceLimits(
            max_cache_size_mb=200,
            max_keys_per_tenant=20000,
            max_requests_per_minute=2000,
            max_concurrent_connections=100,
            priority_weight=2
        ),
        ResourceTier.PREMIUM: TenantResourceLimits(
            max_cache_size_mb=500,
            max_keys_per_tenant=50000,
            max_requests_per_minute=5000,
            max_concurrent_connections=200,
            priority_weight=3
        ),
        ResourceTier.ENTERPRISE: TenantResourceLimits(
            max_cache_size_mb=1000,
            max_keys_per_tenant=100000,
            max_requests_per_minute=10000,
            max_concurrent_connections=500,
            priority_weight=5
        )
    })
    
    # Tenant configurations
    configured_tenants: Dict[str, TenantCacheSettings] = field(default_factory=dict)
    
    # Auto-scaling configuration
    auto_scaling_enabled: bool = True
    scale_up_threshold: float = 0.80  # Scale up when 80% capacity
    scale_down_threshold: float = 0.30  # Scale down when below 30%
    scaling_cooldown_minutes: int = 15
    
    # Cleanup and maintenance
    cleanup_interval_minutes: int = 30
    expired_key_cleanup: bool = True
    tenant_inactivity_threshold_days: int = 30
    auto_archive_inactive_tenants: bool = True
    
    # Security and compliance
    tenant_data_encryption: bool = True
    cross_tenant_access_prevention: bool = True
    audit_cross_tenant_attempts: bool = True
    gdpr_compliance_mode: bool = True
    
    # Monitoring and alerting
    monitoring_enabled: bool = True
    performance_metrics: bool = True
    resource_usage_alerts: bool = True
    alert_thresholds: Dict[str, Any] = field(default_factory=lambda: {
        "tenant_cache_usage_max": 0.90,
        "total_memory_usage_max": 0.85,
        "cross_tenant_access_attempts": 0,
        "tenant_request_rate_exceeded": 0.95,
        "failed_authentication_rate_max": 0.05
    })

    def add_tenant(self, tenant_settings: TenantCacheSettings) -> bool:
        """Add new tenant configuration"""
        if len(self.configured_tenants) >= self.max_tenants:
            return False
            
        # Apply resource tier limits
        if tenant_settings.resource_tier in self.resource_tiers:
            tenant_settings.resource_limits = self.resource_tiers[tenant_settings.resource_tier]
        
        self.configured_tenants[tenant_settings.tenant_id] = tenant_settings
        return True
    
    def get_tenant_cache_key(self, tenant_id: str, cache_key: str) -> str:
        """
Generate tenant-specific cache key"""
        components = [self.global_prefix, self.namespace, tenant_id, cache_key]
        return self.tenant_key_separator.join(components)
    
    def get_available_cache_size(self) -> int:
        """
Get available cache size for new tenants"""
        used_cache = sum(
            settings.resource_limits.max_cache_size_mb 
            for settings in self.configured_tenants.values()
        )
        available = (self.total_cache_size_mb - self.reserved_system_cache_mb - used_cache)
        return max(0, available)
    
    def validate_tenant_access(self, tenant_id: str, api_key: Optional[str] = None) -> bool:
        """
Validate tenant access permissions"""
        if tenant_id not in self.configured_tenants:
            return False
            
        tenant_settings = self.configured_tenants[tenant_id]
        
        if tenant_settings.api_key_required and not api_key:
            return False
            
        if api_key and tenant_settings.access_key_hash:
            provided_hash = hashlib.sha256(api_key.encode()).hexdigest()
            if provided_hash != tenant_settings.access_key_hash:
                return False
        
        return True


class MultiTenantCacheManager:
    """
Manager for multi-tenant cache operations"""
    
    def __init__(self, config: MultiTenantCacheConfig):
        self.config = config
        self._tenant_stats = {}
        self._resource_usage = {}
        self._performance_metrics = {}
    
    def create_tenant(self, tenant_name: str, tenant_type: TenantType, 
                     resource_tier: ResourceTier = ResourceTier.STANDARD) -> Optional[TenantCacheSettings]:
        """
Create new tenant with generated ID"""
        tenant_id = str(uuid.uuid4())
        
        tenant_settings = TenantCacheSettings(
            tenant_id=tenant_id,
            tenant_name=tenant_name,
            tenant_type=tenant_type,
            resource_tier=resource_tier,
            isolation_level=self.config.isolation_level
        )
        
        if self.config.add_tenant(tenant_settings):
            self._initialize_tenant_stats(tenant_id)
            return tenant_settings
        return None
    
    def get_tenant_resource_usage(self, tenant_id: str) -> Dict[str, Any]:
        """
Get current resource usage for tenant"""
        if tenant_id not in self._resource_usage:
            return {}
            
        usage = self._resource_usage[tenant_id]
        tenant_settings = self.config.configured_tenants.get(tenant_id)
        
        if not tenant_settings:
            return {}
        
        limits = tenant_settings.resource_limits
        
        return {
            "cache_usage_mb": usage.get("cache_usage_mb", 0),
            "cache_usage_percent": (usage.get("cache_usage_mb", 0) / limits.max_cache_size_mb) * 100,
            "key_count": usage.get("key_count", 0),
            "key_usage_percent": (usage.get("key_count", 0) / limits.max_keys_per_tenant) * 100,
            "requests_per_minute": usage.get("requests_per_minute", 0),
            "request_rate_percent": (usage.get("requests_per_minute", 0) / limits.max_requests_per_minute) * 100,
            "concurrent_connections": usage.get("concurrent_connections", 0)
        }
    
    def check_tenant_limits(self, tenant_id: str, operation_type: str) -> bool:
        """Check if tenant operation is within limits"""
        tenant_settings = self.config.configured_tenants.get(tenant_id)
        if not tenant_settings:
            return False
        
        usage = self.get_tenant_resource_usage(tenant_id)
        limits = tenant_settings.resource_limits
        
        # Check various limits based on operation type
        if operation_type == "cache_write":
            return usage["cache_usage_percent"] < 95  # Allow up to 95% usage
        elif operation_type == "api_request":
            return usage["request_rate_percent"] < 100
        elif operation_type == "connection":
            return usage["concurrent_connections"] < limits.max_concurrent_connections
        
        return True
    
    def get_platform_statistics(self) -> Dict[str, Any]:
        """Get comprehensive platform statistics"""
        total_tenants = len(self.config.configured_tenants)
        tenants_by_type = {}
        tenants_by_tier = {}
        
        for tenant in self.config.configured_tenants.values():
            # Count by type
            tenant_type = tenant.tenant_type.value
            tenants_by_type[tenant_type] = tenants_by_type.get(tenant_type, 0) + 1
            
            # Count by tier
            tenant_tier = tenant.resource_tier.value
            tenants_by_tier[tenant_tier] = tenants_by_tier.get(tenant_tier, 0) + 1
        
        total_allocated_cache = sum(
            tenant.resource_limits.max_cache_size_mb
            for tenant in self.config.configured_tenants.values()
        )
        
        return {
            "total_tenants": total_tenants,
            "max_tenants": self.config.max_tenants,
            "tenants_by_type": tenants_by_type,
            "tenants_by_tier": tenants_by_tier,
            "total_cache_size_mb": self.config.total_cache_size_mb,
            "allocated_cache_mb": total_allocated_cache,
            "available_cache_mb": self.config.get_available_cache_size(),
            "cache_utilization_percent": (total_allocated_cache / self.config.total_cache_size_mb) * 100,
            "average_tenant_cache_mb": total_allocated_cache / max(total_tenants, 1)
        }
    
    def _initialize_tenant_stats(self, tenant_id: str):
        """Initialize statistics tracking for new tenant"""
        self._tenant_stats[tenant_id] = {
            "created_at": datetime.now(),
            "last_access": datetime.now(),
            "total_requests": 0,
            "cache_hits": 0,
            "cache_misses": 0
        }
        
        self._resource_usage[tenant_id] = {
            "cache_usage_mb": 0,
            "key_count": 0,
            "requests_per_minute": 0,
            "concurrent_connections": 0
        }


# Environment-specific configurations
DEVELOPMENT_CONFIG = MultiTenantCacheConfig(
    cache_name="dev_multi_tenant_cache",
    total_cache_size_mb=512,  # 512MB for dev
    max_tenants=50,
    tenant_data_encryption=False,
    monitoring_enabled=False,
    auto_scaling_enabled=False
)

TESTING_CONFIG = MultiTenantCacheConfig(
    cache_name="test_multi_tenant_cache",
    total_cache_size_mb=256,  # 256MB for tests
    max_tenants=20,
    tenant_data_encryption=False,
    audit_cross_tenant_attempts=False,
    performance_metrics=False
)

PRODUCTION_CONFIG = MultiTenantCacheConfig(
    cache_name="prod_multi_tenant_cache",
    total_cache_size_mb=16384,  # 16GB for production
    max_tenants=5000,
    tenant_data_encryption=True,
    cross_tenant_access_prevention=True,
    audit_cross_tenant_attempts=True,
    monitoring_enabled=True,
    performance_metrics=True,
    gdpr_compliance_mode=True
)

# Export main classes
__all__ = [
    'TenantType',
    'IsolationLevel',
    'ResourceTier',
    'TenantResourceLimits',
    'TenantCacheSettings',
    'MultiTenantCacheConfig',
    'MultiTenantCacheManager',
    'DEVELOPMENT_CONFIG',
    'TESTING_CONFIG',
    'PRODUCTION_CONFIG'
]
