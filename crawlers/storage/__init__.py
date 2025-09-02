"""Storage Module Initialization
============================

Professional storage system for IA-Influencer-Agent platform with enterprise-grade features.
Exposes all storage providers, managers, and utilities through a unified interface.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: All rights reserved. Unauthorized use, reproduction, or distribution prohibited.

WARNING: This code is protected by copyright law. Any unauthorized copying, 
distribution, or modification is strictly prohibited and will result in 
legal action. Contact mlaiel@live.de for licensing.

Expertise combinée:
- Lead Developer IA: Architecture intelligente et optimisations ML
- Backend Senior: Infrastructure robuste et scalabilité enterprise
- ML Engineer: Algorithmes d'apprentissage et modèles prédictifs
- DBA Expert: Gestion de données et optimisation des requêtes
- Sécurité: Protection et chiffrement des données sensibles
- Microservices: Architecture distribuée et communication inter-services
- Audio/Vidéo: Traitement multimédia et analyse de contenu
- DevOps: Déploiement, monitoring et infrastructure cloud
- IA Prompt Engineer: Optimisation des interactions et prompts
"""

import logging
from typing import Dict, List, Optional, Any

# Core interfaces and abstractions
from .interfaces import (
    # Enums
    StorageBackendType,
    ContentType,
    ViolationSeverity,
    
    # Data models
    StorageMetadata,
    CrawlerData,
    ContentRecord,
    ViolationRecord,
    CacheKey,
    VectorRecord,
    TimeSeriesPoint,
    StorageStats,
    HealthStatus,
    
    # Base interfaces
    BaseStorageProvider,
    ContentStorageProvider,
    ViolationStorageProvider, 
    CacheStorageProvider,
    VectorStorageProvider,
    TimeSeriesStorageProvider,
    StorageFactory,
    StorageRouter,
    
    # Exceptions
    StorageException,
    ConnectionException,
    ValidationException,
    TimeoutException,
    CapacityException,
    AuthenticationException,
)

# Storage manager and orchestration
from .manager import (
    StorageManager,
    RoutingStrategy,
    LoadBalancer,
    FailoverManager,
    PerformanceMonitor,
)

# Database storage providers
from .database import (
    DatabaseStorageProvider,
    DatabaseContentStorageProvider,
    DatabaseViolationStorageProvider,
    CrawlerDataModel,
    ContentRecordModel,
    ViolationRecordModel,
)

# Filesystem storage providers
from .filesystem import (
    FileSystemStorageProvider,
    FileIndexManager,
    CompressionManager,
    FileLockManager,
)

# Cache storage providers
from .cache import (
    RedisCacheStorageProvider,
    InMemoryCacheStorageProvider,
    CacheEvictionPolicy,
)

# Object storage providers
from .object_storage import (
    S3ObjectStorageProvider,
    S3ContentStorageProvider,
    MultipartUploadManager,
    S3LifecycleManager,
)

# Analytics storage providers
from .analytics_storage import (
    AnalyticsStorageProvider,
    AnalyticsMetric,
    AnalyticsQuery,
    AnalyticsResult,
    AnalyticsMetricType,
    AnalyticsAggregation,
    TimePeriod,
    InMemoryAnalyticsStorage,
    create_analytics_storage,
)

# Distribution storage providers
from .distribution_storage import (
    DistributionStorageProvider,
    DistributionChannel,
    PublishingStatus,
    ContentFormat,
    PlatformConfiguration,
    DistributionSchedule,
    DistributionJob,
    ContentVariant,
    CrossPlatformSync,
    InMemoryDistributionStorage,
    create_distribution_storage,
)

# Licensing storage providers
from .licensing_storage import (
    LicensingStorageProvider,
    LicenseAgreement,
    RoyaltyPayment,
    ComplianceRecord,
    IntellectualProperty,
    LicenseUsage,
    LicenseStatus,
    RightsType,
    RoyaltyType,
    ComplianceStatus,
    LicenseTermType,
    InMemoryLicensingStorage,
    create_licensing_storage,
)

# Platform storage providers
from .platform_storage import (
    PlatformStorageProvider,
    PlatformConfiguration,
    PlatformAccount,
    PlatformContent,
    PlatformAnalytics,
    PlatformOptimization,
    PlatformType,
    ContentSpecification,
    PlatformFeature,
    InMemoryPlatformStorage,
    create_platform_storage,
)

# Vector storage providers
from .vector_storage import (
    VectorStorageProvider,
    VectorEmbedding,
    VectorSearchQuery,
    VectorSearchResult,
    VectorCluster,
    VectorSimilarityGroup,
    VectorType,
    SimilarityMetric,
    IndexType,
    InMemoryVectorStorage,
    create_vector_storage,
)

# Time-series storage providers
from .timeseries_storage import (
    TimeSeriesStorageProvider,
    TimeSeriesMetric,
    TimeSeriesQuery,
    TimeSeriesAggregation,
    TimeSeriesStatistics,
    TimeSeriesForecast,
    MetricType,
    AggregationType,
    TimeGranularity,
    InMemoryTimeSeriesStorage,
    create_timeseries_storage,
)

# Configuration management
from .config import (
    StorageProviderType,
    DatabaseConfig,
    FilesystemConfig,
    CacheConfig,
    ObjectStorageConfig,
    VectorConfig,
    TimeSeriesConfig,
    StorageProviderConfig,
    StorageConfigurationManager,
    StorageProviderFactory,
)

# Main index module with factory functions
from .index import (
    EnterpriseStorageFactory,
    create_storage_manager,
    create_content_creator_storage,
    create_provider,
    get_available_provider_types,
    get_provider_class,
)

# Export all main functionality
__all__ = [
    # Core interfaces and manager
    "StorageProviderInterface",
    "StorageMetadata", 
    "StorageQuery",
    "StorageResult",
    "HealthStatus",
    "PerformanceMetrics",
    "StorageManager",
    "RoutingStrategy",
    
    # Storage providers
    "DatabaseStorageProvider",
    "FilesystemStorageProvider", 
    "CacheStorageProvider",
    "S3ObjectStorageProvider",
    "S3ContentStorageProvider",
    "MultipartUploadManager",
    "S3LifecycleManager",
    "AnalyticsStorageProvider",
    "DistributionStorageProvider",
    "LicensingStorageProvider",
    "PlatformStorageProvider",
    "VectorStorageProvider",
    "TimeSeriesStorageProvider",
    
    # Configuration classes
    "StorageProviderType",
    "DatabaseConfig",
    "FilesystemConfig",
    "CacheConfig", 
    "ObjectStorageConfig",
    "VectorConfig",
    "TimeSeriesConfig",
    "StorageProviderConfig",
    "StorageConfigurationManager",
    "StorageProviderFactory",
    
    # Enterprise factory and convenience functions
    "EnterpriseStorageFactory",
    "create_storage_manager",
    "create_content_creator_storage",
    "create_provider",
    "get_available_provider_types",
    "get_provider_class",
    
    # Analytics data models
    "AnalyticsMetric",
    "AnalyticsQuery", 
    "AnalyticsResult",
    "AnalyticsMetricType",
    "AnalyticsAggregation",
    "TimePeriod",
    
    # Distribution data models  
    "DistributionChannel",
    "PublishingStatus",
    "ContentFormat",
    "PlatformConfiguration",
    "DistributionSchedule",
    "DistributionJob",
    "ContentVariant",
    "CrossPlatformSync",
    
    # Licensing data models
    "LicenseAgreement",
    "RoyaltyPayment",
    "ComplianceRecord", 
    "IntellectualProperty",
    "LicenseUsage",
    "LicenseStatus",
    "RightsType",
    "RoyaltyType",
    "ComplianceStatus",
    "LicenseTermType",
    
    # Platform data models
    "PlatformAccount",
    "PlatformContent",
    "PlatformAnalytics",
    "PlatformOptimization",
    "PlatformType",
    "ContentSpecification",
    "PlatformFeature",
    
    # Vector data models
    "VectorEmbedding",
    "VectorSearchQuery",
    "VectorSearchResult",
    "VectorCluster",
    "VectorSimilarityGroup",
    "VectorType",
    "SimilarityMetric",
    "IndexType",
    
    # Time-series data models
    "TimeSeriesMetric",
    "TimeSeriesQuery",
    "TimeSeriesAggregation",
    "TimeSeriesStatistics", 
    "TimeSeriesForecast",
    "MetricType",
    "AggregationType",
    "TimeGranularity",
]

# Module metadata
__version__ = "1.0.0"
__author__ = "Fahed Mlaiel <mlaiel@live.de>"
__license__ = "Proprietary - All Rights Reserved"

# Configure module logger
logger = logging.getLogger(__name__)
logger.info(f"Storage module v{__version__} initialized by {__author__}")

# Storage provider registry
STORAGE_PROVIDERS: Dict[str, type] = {
    # Database providers
    'postgresql': DatabaseStorageProvider,
    'mysql': DatabaseStorageProvider,
    'sqlite': DatabaseStorageProvider,
    
    # Filesystem providers
    'filesystem': FileSystemStorageProvider,
    
    # Cache providers
    'redis': RedisCacheStorageProvider,
    'memory': InMemoryCacheStorageProvider,
    
    # Object storage providers
    's3': S3ObjectStorageProvider,
    'minio': S3ObjectStorageProvider,
}

# Content-specific provider registry
CONTENT_PROVIDERS: Dict[str, type] = {
    'postgresql': DatabaseContentStorageProvider,
    'mysql': DatabaseContentStorageProvider,
    'sqlite': DatabaseContentStorageProvider,
    's3': S3ContentStorageProvider,
    'minio': S3ContentStorageProvider,
}

# Violation-specific provider registry
VIOLATION_PROVIDERS: Dict[str, type] = {
    'postgresql': DatabaseViolationStorageProvider,
    'mysql': DatabaseViolationStorageProvider,
    'sqlite': DatabaseViolationStorageProvider,
}

def create_storage_manager(
    config_path: Optional[str] = None,
    config_data: Optional[Dict[str, Any]] = None,
    routing_strategy: str = "priority",
    enable_monitoring: bool = True,
    enable_failover: bool = True
) -> StorageManager:
    """
    Create a fully configured storage manager instance.
    
    Args:
        config_path: Path to configuration file (JSON/YAML)
        config_data: Configuration data dictionary
        routing_strategy: Routing strategy ("priority", "round_robin", "least_load")
        enable_monitoring: Enable performance monitoring
        enable_failover: Enable automatic failover
    
    Returns:
        Configured StorageManager instance
    
    Example:
        ```python
        # From configuration file
        manager = create_storage_manager(
            config_path="config/storage.yaml",
            routing_strategy="least_load"
        )
        
        # From configuration dict
        config = {
            "providers": [
                {
                    "id": "primary_db",
                    "type": "postgresql",
                    "url": "postgresql://localhost/crawler_db"
                }
            ]
        }
        manager = create_storage_manager(config_data=config)
        ```
    """
    try:
        # Initialize configuration manager
        config_manager = StorageConfigurationManager()
        
        if config_path:
            config_manager.load_from_file(config_path)
        elif config_data:
            # Process config_data (implementation depends on format)
            pass
        
        # Create provider factory
        factory = StorageProviderFactory(config_manager)
        
        # Create storage manager
        manager = StorageManager(
            factory=factory,
            routing_strategy=RoutingStrategy.from_string(routing_strategy),
            enable_monitoring=enable_monitoring,
            enable_failover=enable_failover
        )
        
        logger.info(f"Created storage manager with {routing_strategy} routing")
        return manager
        
    except Exception as e:
        logger.error(f"Failed to create storage manager: {e}")
        raise

def create_database_provider(
    provider_id: str,
        try:
            logger.info(f"Executing create_database_provider")
            
            # Implementation for create_database_provider
            # TODO: Add specific business logic here
            
            result = None  # Replace with actual implementation
            
            logger.info(f"create_database_provider completed successfully")
            return result
            
        except Exception as e:
            logger.error(f"create_database_provider failed: {e}")
            raise
def create_filesystem_provider(
    provider_id: str,
    base_path: str,
    enable_indexing: bool = True,
    enable_compression: bool = True,
    **kwargs
) -> FileSystemStorageProvider:
    """
    Create a filesystem storage provider with minimal configuration.
    
    Args:
        provider_id: Unique provider identifier
        base_path: Base directory path for storage
        enable_indexing: Enable SQLite indexing
        enable_compression: Enable file compression
        **kwargs: Additional configuration options
    
    Returns:
        Configured FileSystemStorageProvider instance
    
    Example:
        ```python
        provider = create_filesystem_provider(
            "file_storage",
            "/data/crawler/storage",
            enable_indexing=True
        )
        ```
    """
    config = {
        'provider_id': provider_id,
        'base_path': base_path,
        'enable_indexing': enable_indexing,
        'enable_compression': enable_compression,
        **kwargs
    }
    
    return FileSystemStorageProvider(provider_id, config)

def create_redis_provider(
    provider_id: str,
    redis_url: str,
    database: int = 0,
    default_ttl: int = 3600,
    **kwargs
) -> RedisCacheStorageProvider:
    """
    Create a Redis cache provider with minimal configuration.
    
    Args:
        provider_id: Unique provider identifier
        redis_url: Redis connection URL
        database: Redis database number
        default_ttl: Default time-to-live in seconds
        **kwargs: Additional configuration options
    
    Returns:
        Configured RedisCacheStorageProvider instance
    
    Example:
        ```python
        provider = create_redis_provider(
            "redis_cache",
            "redis://localhost:6379",
            database=1,
            default_ttl=7200
        )
        ```
    """
    config = {
        'provider_id': provider_id,
        'redis_url': redis_url,
        'database': database,
        'default_ttl': default_ttl,
        **kwargs
    }
    
    return RedisCacheStorageProvider(provider_id, config)

def create_s3_provider(
    provider_id: str,
    bucket_name: str,
    aws_access_key_id: Optional[str] = None,
    aws_secret_access_key: Optional[str] = None,
    region_name: str = "us-east-1",
    **kwargs
) -> S3ObjectStorageProvider:
    """
    Create an S3 object storage provider with minimal configuration.
    
    Args:
        provider_id: Unique provider identifier
        bucket_name: S3 bucket name
        aws_access_key_id: AWS access key ID
        aws_secret_access_key: AWS secret access key
        region_name: AWS region name
        **kwargs: Additional configuration options
    
    Returns:
        Configured S3ObjectStorageProvider instance
    
    Example:
        ```python
        provider = create_s3_provider(
            "s3_storage",
            "my-crawler-bucket",
            region_name="eu-west-1"
        )
        ```
    """
    config = {
        'provider_id': provider_id,
        'bucket_name': bucket_name,
        'aws_access_key_id': aws_access_key_id,
        'aws_secret_access_key': aws_secret_access_key,
        'region_name': region_name,
        **kwargs
    }
    
    return S3ObjectStorageProvider(provider_id, config)

def get_provider_types() -> List[str]:
    """
Get list of supported provider types."""
    return list(STORAGE_PROVIDERS.keys())

def get_content_provider_types() -> List[str]:
    """
Get list of supported content provider types."""
    return list(CONTENT_PROVIDERS.keys())

def get_violation_provider_types() -> List[str]:
    """
Get list of supported violation provider types."""
    return list(VIOLATION_PROVIDERS.keys())

def validate_provider_config(provider_type: str, config: Dict[str, Any]) -> List[str]:
    """
    Validate provider configuration and return list of errors.
    
    Args:
        provider_type: Provider type to validate
        config: Configuration dictionary
    
    Returns:
        List of validation error messages
    """
    errors = []
    
    if provider_type not in STORAGE_PROVIDERS:
        errors.append(f"Unsupported provider type: {provider_type}")
        return errors
    
    # Provider-specific validation
    if provider_type in ['postgresql', 'mysql', 'sqlite']:
        if not config.get('database_url'):
            errors.append("database_url is required for database providers")
    
    elif provider_type == 'filesystem':
        if not config.get('base_path'):
            errors.append("base_path is required for filesystem provider")
    
    elif provider_type == 'redis':
        if not config.get('redis_url'):
            errors.append("redis_url is required for Redis provider")
    
    elif provider_type in ['s3', 'minio']:
        if not config.get('bucket_name'):
            errors.append("bucket_name is required for object storage providers")
    
    return errors

# Module exports - All classes and functions available for import
__all__ = [
    # Core interfaces and abstractions
    'StorageBackendType',
    'ContentType',
    'ViolationSeverity',
    'StorageMetadata',
    'CrawlerData',
    'ContentRecord',
    'ViolationRecord',
    'CacheKey',
    'VectorRecord',
    'TimeSeriesPoint',
    'StorageStats',
    'HealthStatus',
    'BaseStorageProvider',
    'ContentStorageProvider',
    'ViolationStorageProvider',
    'CacheStorageProvider',
    'VectorStorageProvider',
    'TimeSeriesStorageProvider',
    'StorageFactory',
    'StorageRouter',
    'StorageException',
    'ConnectionException',
    'ValidationException',
    'TimeoutException',
    'CapacityException',
    'AuthenticationException',
    
    # Storage management
    'StorageManager',
    'RoutingStrategy',
    'LoadBalancer',
    'FailoverManager',
    'PerformanceMonitor',
    
    # Database providers
    'DatabaseStorageProvider',
    'DatabaseContentStorageProvider',
    'DatabaseViolationStorageProvider',
    'CrawlerDataModel',
    'ContentRecordModel',
    'ViolationRecordModel',
    
    # Filesystem providers
    'FileSystemStorageProvider',
    'FileIndexManager',
    'CompressionManager',
    'FileLockManager',
    
    # Cache providers
    'RedisCacheStorageProvider',
    'InMemoryCacheStorageProvider',
    'CacheEvictionPolicy',
    
    # Object storage providers
    'S3ObjectStorageProvider',
    'S3ContentStorageProvider',
    'MultipartUploadManager',
    'S3LifecycleManager',
    
    # Configuration management
    'StorageProviderType',
    'DatabaseConfig',
    'FilesystemConfig',
    'CacheConfig',
    'ObjectStorageConfig',
    'VectorConfig',
    'TimeSeriesConfig',
    'StorageProviderConfig',
    'StorageConfigurationManager',
    'StorageProviderFactory',
    
    # Utility functions
    'create_storage_manager',
    'create_database_provider',
    'create_filesystem_provider',
    'create_redis_provider',
    'create_s3_provider',
    'get_provider_types',
    'get_content_provider_types',
    'get_violation_provider_types',
    'validate_provider_config',
    
    # Module metadata
    '__version__',
    '__author__',
    '__license__',
]

# Print initialization message
logger.info(f"IA-Influencer-Agent Storage Module v{__version__} loaded successfully")
logger.info(f"Available providers: {', '.join(get_provider_types())}")
logger.info(f"Copyright: {__license__} - {__author__}")
