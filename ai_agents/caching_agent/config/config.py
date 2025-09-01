"""Caching Agent Configuration Examples

Professional configuration examples for different deployment scenarios
and use cases in the IA-Influencer-Agent platform.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.
"""

from .manager import CacheConfig, CachePriority
from .storage import StorageLevel, CompressionType

# Development Configuration
DEVELOPMENT_CONFIG = CacheConfig(
    max_memory_size=256 * 1024 * 1024,  # 256MB
    max_entries=50000,
    default_ttl=1800,  # 30 minutes
    compression_threshold=512,  # 512 bytes
    enable_encryption=False,
    enable_analytics=True,
    enable_distributed_coordination=False,
    cache_levels=[StorageLevel.L1_MEMORY, StorageLevel.L2_REDIS],
    redis_url="redis://localhost:6379",
    redis_db=0,
    optimization_interval=600,  # 10 minutes
    default_compression=CompressionType.GZIP
)

# Production Configuration
PRODUCTION_CONFIG = CacheConfig(
    max_memory_size=2 * 1024 * 1024 * 1024,  # 2GB
    max_entries=1000000,
    default_ttl=3600,  # 1 hour
    compression_threshold=1024,  # 1KB
    enable_encryption=True,
    enable_analytics=True,
    enable_distributed_coordination=True,
    cache_levels=[
        StorageLevel.L1_MEMORY,
        StorageLevel.L2_REDIS,
        StorageLevel.L3_DATABASE,
        StorageLevel.L4_S3_CDN
    ],
    redis_url="redis://redis-cluster:6379",
    redis_max_connections=200,
    database_url="postgresql://cache_user:password@db-cluster:5432/cache_db",
    database_pool_size=50,
    s3_bucket="ia-influencer-cache",
    s3_region="eu-central-1",
    optimization_interval=300,  # 5 minutes
    default_compression=CompressionType.ZSTD
)

# High Performance Configuration
HIGH_PERFORMANCE_CONFIG = CacheConfig(
    max_memory_size=8 * 1024 * 1024 * 1024,  # 8GB
    max_entries=5000000,
    default_ttl=7200,  # 2 hours
    compression_threshold=2048,  # 2KB
    enable_encryption=False,  # Disabled for performance
    enable_analytics=True,
    enable_distributed_coordination=True,
    cache_levels=[StorageLevel.L1_MEMORY, StorageLevel.L2_REDIS],
    redis_url="redis://high-perf-redis:6379",
    redis_max_connections=500,
    optimization_interval=180,  # 3 minutes
    default_compression=CompressionType.LZ4  # Fastest compression
)

# Content-Specific Configurations
AUDIO_PROCESSING_CONFIG = CacheConfig(
    max_memory_size=4 * 1024 * 1024 * 1024,  # 4GB
    default_ttl=86400,  # 24 hours for audio fingerprints
    compression_threshold=4096,  # 4KB - audio data is typically larger
    enable_encryption=True,  # Audio fingerprints are sensitive
    cache_levels=[StorageLevel.L1_MEMORY, StorageLevel.L2_REDIS, StorageLevel.L3_DATABASE],
    optimization_interval=900,  # 15 minutes
    invalidation_strategies=["ttl", "tag_based", "event_driven"]
)

SEO_OPTIMIZATION_CONFIG = CacheConfig(
    max_memory_size=512 * 1024 * 1024,  # 512MB
    default_ttl=43200,  # 12 hours for SEO data
    compression_threshold=256,  # Small threshold for text data
    enable_analytics=True,
    cache_levels=[StorageLevel.L1_MEMORY, StorageLevel.L2_REDIS],
    optimization_interval=1800,  # 30 minutes
    default_compression=CompressionType.GZIP
)

COLLABORATION_CONFIG = CacheConfig(
    max_memory_size=1 * 1024 * 1024 * 1024,  # 1GB
    default_ttl=7200,  # 2 hours for collaboration data
    enable_distributed_coordination=True,  # Important for multi-user features
    cache_levels=[StorageLevel.L1_MEMORY, StorageLevel.L2_REDIS],
    optimization_interval=300,  # 5 minutes - frequent optimization
    invalidation_strategies=["event_driven", "tag_based"]
)

# Geographic Distribution Configurations
EU_REGION_CONFIG = CacheConfig(
    max_memory_size=1 * 1024 * 1024 * 1024,  # 1GB
    redis_url="redis://eu-central-1-redis:6379",
    database_url="postgresql://cache@eu-central-1-db:5432/cache_db",
    s3_bucket="ia-influencer-cache-eu",
    s3_region="eu-central-1",
    default_ttl=3600,
    enable_distributed_coordination=True
)

US_REGION_CONFIG = CacheConfig(
    max_memory_size=1 * 1024 * 1024 * 1024,  # 1GB
    redis_url="redis://us-east-1-redis:6379", 
    database_url="postgresql://cache@us-east-1-db:5432/cache_db",
    s3_bucket="ia-influencer-cache-us",
    s3_region="us-east-1",
    default_ttl=3600,
    enable_distributed_coordination=True
)

# Security-Enhanced Configuration
SECURITY_ENHANCED_CONFIG = CacheConfig(
    max_memory_size=1 * 1024 * 1024 * 1024,  # 1GB
    enable_encryption=True,
    default_ttl=1800,  # Shorter TTL for security
    cache_levels=[StorageLevel.L1_MEMORY, StorageLevel.L2_REDIS],
    invalidation_strategies=["ttl", "event_driven", "security_breach"],
    optimization_interval=600,  # 10 minutes
    redis_url="redis://secure-redis:6380",  # Custom port
    database_url="postgresql://secure_user:strong_pass@secure-db:5432/secure_cache"
)

# Configuration Templates by Use Case
CONFIGURATION_TEMPLATES = {
    "development": DEVELOPMENT_CONFIG,
    "production": PRODUCTION_CONFIG,
    "high_performance": HIGH_PERFORMANCE_CONFIG,
    "audio_processing": AUDIO_PROCESSING_CONFIG,
    "seo_optimization": SEO_OPTIMIZATION_CONFIG,
    "collaboration": COLLABORATION_CONFIG,
    "eu_region": EU_REGION_CONFIG,
    "us_region": US_REGION_CONFIG,
    "security_enhanced": SECURITY_ENHANCED_CONFIG
}

def get_config_for_environment(environment: str) -> CacheConfig:
    """
    Get cache configuration for specific environment.
    
    Args:
        environment: Environment name (development, production, etc.)
        
    Returns:
        CacheConfig instance for the environment
    """
    if environment not in CONFIGURATION_TEMPLATES:
        raise ValueError(f"Unknown environment: {environment}")
    
    return CONFIGURATION_TEMPLATES[environment]

def create_custom_config(**kwargs) -> CacheConfig:
    """
    Create custom cache configuration with overrides.
    
    Args:
        **kwargs: Configuration parameters to override
        
    Returns:
        Custom CacheConfig instance
    """
    base_config = PRODUCTION_CONFIG
    
    # Override with provided parameters
    config_dict = base_config.__dict__.copy()
    config_dict.update(kwargs)
    
    return CacheConfig(**config_dict)

# Content-Type Specific TTL Recommendations
CONTENT_TYPE_TTL_MAP = {
    "audio_fingerprint": 86400,     # 24 hours - critical for protection
    "video_thumbnail": 21600,       # 6 hours - visual content
    "user_session": 3600,           # 1 hour - user data
    "analytics_data": 43200,        # 12 hours - analytics
    "ml_model_cache": 604800,       # 7 days - ML models
    "temporary_upload": 1800,       # 30 minutes - temp data
    "collaboration_data": 7200,     # 2 hours - collaboration
    "seo_metadata": 86400,          # 24 hours - SEO data
    "payment_session": 900,         # 15 minutes - payment data
    "content_protection": 172800,   # 48 hours - protection data
    "user_preferences": 43200,      # 12 hours - user prefs
    "search_results": 3600,         # 1 hour - search data
    "recommendation": 7200,         # 2 hours - recommendations
    "trend_analysis": 10800,        # 3 hours - trend data
    "social_media_data": 1800,      # 30 minutes - social data
    "notification": 3600,           # 1 hour - notifications
    "audit_log": 259200,           # 72 hours - audit data
    "backup_metadata": 604800       # 7 days - backup info
}

def get_ttl_for_content_type(content_type: str) -> int:
    """
    Get recommended TTL for specific content type.
    
    Args:
        content_type: Type of content being cached
        
    Returns:
        Recommended TTL in seconds
    """
    return CONTENT_TYPE_TTL_MAP.get(content_type, 3600)  # Default 1 hour

# Priority Mapping for Different Content Types
CONTENT_PRIORITY_MAP = {
    "payment_session": CachePriority.CRITICAL,
    "content_protection": CachePriority.CRITICAL,
    "audio_fingerprint": CachePriority.CRITICAL,
    "user_session": CachePriority.HIGH,
    "collaboration_data": CachePriority.HIGH,
    "ml_model_cache": CachePriority.HIGH,
    "analytics_data": CachePriority.NORMAL,
    "seo_metadata": CachePriority.NORMAL,
    "video_thumbnail": CachePriority.NORMAL,
    "user_preferences": CachePriority.NORMAL,
    "search_results": CachePriority.NORMAL,
    "recommendation": CachePriority.NORMAL,
    "social_media_data": CachePriority.LOW,
    "temporary_upload": CachePriority.LOW,
    "notification": CachePriority.LOW,
    "trend_analysis": CachePriority.MINIMAL,
    "backup_metadata": CachePriority.MINIMAL
}

def get_priority_for_content_type(content_type: str) -> CachePriority:
    """
    Get recommended priority for specific content type.
    
    Args:
        content_type: Type of content being cached
        
    Returns:
        Recommended cache priority
    """
    return CONTENT_PRIORITY_MAP.get(content_type, CachePriority.NORMAL)
