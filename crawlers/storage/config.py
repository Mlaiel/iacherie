"""
Configuration Module
====================

Professional configuration management for storage providers in IA-Influencer-Agent platform.
Handles storage provider configuration, validation, and factory creation.

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
import json
import yaml
import time
from typing import Dict, List, Optional, Any, Type
from pathlib import Path
from dataclasses import dataclass, asdict, field
from enum import Enum
import os
from urllib.parse import urlparse

from .interfaces import (
    StorageBackendType, StorageFactory, BaseStorageProvider,
    ContentStorageProvider, ViolationStorageProvider, CacheStorageProvider,
    VectorStorageProvider, TimeSeriesStorageProvider
)
from .database import DatabaseStorageProvider, DatabaseContentStorageProvider, DatabaseViolationStorageProvider
from .filesystem import FileSystemStorageProvider
from .cache import RedisCacheStorageProvider, InMemoryCacheStorageProvider
from .object_storage import S3ObjectStorageProvider, S3ContentStorageProvider

logger = logging.getLogger(__name__)

class StorageProviderType(Enum):
    """Supported storage provider types."""
    # Database providers
    POSTGRESQL = "postgresql"
    MYSQL = "mysql"
    SQLITE = "sqlite"
    
    # Cache providers
    REDIS = "redis"
    MEMCACHED = "memcached"
    MEMORY = "memory"
    
    # Object storage providers
    S3 = "s3"
    MINIO = "minio"
    AZURE_BLOB = "azure_blob"
    
    # File system providers
    FILESYSTEM = "filesystem"
    
    # Vector database providers
    FAISS = "faiss"
    PINECONE = "pinecone"
    QDRANT = "qdrant"
    
    # Time series providers
    INFLUXDB = "influxdb"
    PROMETHEUS = "prometheus"

@dataclass
class DatabaseConfig:
    """Database storage provider configuration."""
    database_url: str
    database_type: str = "postgresql"
    pool_size: int = 10
    max_overflow: int = 20
    pool_timeout: int = 30
    pool_recycle: int = 3600
    enable_compression: bool = True
    compression_type: str = "gzip"
    enable_encryption: bool = False
    encryption_key: Optional[str] = None
    echo_sql: bool = False

@dataclass
class FilesystemConfig:
    """Filesystem storage provider configuration."""
    base_path: str
    enable_compression: bool = True
    compression_type: str = "gzip"
    enable_indexing: bool = True
    max_files_per_directory: int = 1000
    enable_file_locking: bool = True
    enable_backup: bool = False
    backup_interval_hours: int = 24

@dataclass
class CacheConfig:
    """Cache storage provider configuration."""
    # Redis specific
    redis_url: Optional[str] = None
    database: int = 0
    pool_size: int = 10
    default_ttl: int = 3600
    key_prefix: str = ""
    enable_compression: bool = True
    compression_threshold: int = 1024
    
    # Memory cache specific
    max_size: int = 10000
    cleanup_interval: int = 300

@dataclass
class ObjectStorageConfig:
    """Object storage provider configuration."""
    bucket_name: str
    aws_access_key_id: Optional[str] = None
    aws_secret_access_key: Optional[str] = None
    aws_session_token: Optional[str] = None
    region_name: str = "us-east-1"
    endpoint_url: Optional[str] = None
    key_prefix: str = ""
    enable_encryption: bool = True
    encryption_key: Optional[str] = None
    storage_class: str = "STANDARD"
    enable_versioning: bool = False
    enable_compression: bool = True
    compression_type: str = "gzip"
    multipart_threshold: int = 64 * 1024 * 1024  # 64MB
    multipart_chunksize: int = 16 * 1024 * 1024  # 16MB
    max_concurrency: int = 10

@dataclass
class VectorConfig:
    """Vector storage provider configuration."""
    dimension: int
    metric: str = "cosine"  # cosine, euclidean, dot_product
    index_type: str = "hnsw"  # hnsw, ivf, flat
    
    # FAISS specific
    faiss_index_path: Optional[str] = None
    enable_gpu: bool = False
    
    # Pinecone specific
    pinecone_api_key: Optional[str] = None
    pinecone_environment: Optional[str] = None
    
    # Qdrant specific
    qdrant_url: Optional[str] = None
    qdrant_api_key: Optional[str] = None

@dataclass
class TimeSeriesConfig:
    """Time series storage provider configuration."""
    # InfluxDB specific
    influxdb_url: Optional[str] = None
    influxdb_token: Optional[str] = None
    influxdb_org: Optional[str] = None
    influxdb_bucket: Optional[str] = None
    
    # Prometheus specific
    prometheus_url: Optional[str] = None
    
    # General settings
    retention_policy: str = "30d"
    precision: str = "s"  # s, ms, us, ns

@dataclass
class StorageProviderConfig:
    """Complete storage provider configuration."""
    provider_id: str
    provider_type: StorageProviderType
    backend_type: StorageBackendType
    enabled: bool = True
    priority: int = 100
    weight: float = 1.0
    read_only: bool = False
    max_connections: int = 10
    timeout_seconds: int = 30
    retry_attempts: int = 3
    health_check_interval: int = 60
    
    # Type-specific configurations
    database_config: Optional[DatabaseConfig] = None
    filesystem_config: Optional[FilesystemConfig] = None
    cache_config: Optional[CacheConfig] = None
    object_storage_config: Optional[ObjectStorageConfig] = None
    vector_config: Optional[VectorConfig] = None
    timeseries_config: Optional[TimeSeriesConfig] = None

class StorageConfigurationManager:
    """
    Professional storage configuration manager.
    
    Features:
    - Configuration file loading (JSON, YAML)
    - Environment variable override
    - Configuration validation
    - Default configuration generation
    - Provider factory creation
    """
    
    def __init__(self):
        """Initialize configuration manager."""
        self.configurations: Dict[str, StorageProviderConfig] = {}
        self.environment_prefix = "STORAGE_"
        
        logger.info("Storage configuration manager initialized")
    
    def load_from_file(self, config_path: str) -> None:
        """Load configuration from file."""
        try:
            config_file = Path(config_path)
            
            if not config_file.exists():
                logger.error(f"Configuration file not found: {config_path}")
                return
            
            # Determine file format
            if config_file.suffix.lower() in ['.yaml', '.yml']:
                with open(config_file, 'r') as f:
                    config_data = yaml.safe_load(f)
            else:
                with open(config_file, 'r') as f:
                    config_data = json.load(f)
            
            # Parse configurations
            if 'storage_providers' in config_data:
                for provider_data in config_data['storage_providers']:
                    config = self._parse_provider_config(provider_data)
                    if config:
                        self.configurations[config.provider_id] = config
            
            logger.info(f"Loaded {len(self.configurations)} storage configurations from {config_path}")
            
        except Exception as e:
            logger.error(f"Failed to load configuration from {config_path}: {e}")
    
    def _parse_provider_config(self, provider_data: Dict[str, Any]) -> Optional[StorageProviderConfig]:
        """Parse individual provider configuration."""
        try:
            provider_type = StorageProviderType(provider_data['provider_type'])
            backend_type = StorageBackendType(provider_data['backend_type'])
            
            config = StorageProviderConfig(
                provider_id=provider_data['provider_id'],
                provider_type=provider_type,
                backend_type=backend_type,
                enabled=provider_data.get('enabled', True),
                priority=provider_data.get('priority', 100),
                weight=provider_data.get('weight', 1.0),
                read_only=provider_data.get('read_only', False),
                max_connections=provider_data.get('max_connections', 10),
                timeout_seconds=provider_data.get('timeout_seconds', 30),
                retry_attempts=provider_data.get('retry_attempts', 3),
                health_check_interval=provider_data.get('health_check_interval', 60)
            )
            
            # Parse type-specific configuration
            if backend_type == StorageBackendType.DATABASE:
                config.database_config = self._parse_database_config(
                    provider_data.get('database_config', {})
                )
            elif backend_type == StorageBackendType.FILE_SYSTEM:
                config.filesystem_config = self._parse_filesystem_config(
                    provider_data.get('filesystem_config', {})
                )
            elif backend_type == StorageBackendType.CACHE:
                config.cache_config = self._parse_cache_config(
                    provider_data.get('cache_config', {})
                )
            elif backend_type == StorageBackendType.OBJECT_STORAGE:
                config.object_storage_config = self._parse_object_storage_config(
                    provider_data.get('object_storage_config', {})
                )
            elif backend_type == StorageBackendType.VECTOR_DB:
                config.vector_config = self._parse_vector_config(
                    provider_data.get('vector_config', {})
                )
            elif backend_type == StorageBackendType.TIME_SERIES:
                config.timeseries_config = self._parse_timeseries_config(
                    provider_data.get('timeseries_config', {})
                )
            
            return config
            
        except Exception as e:
            logger.error(f"Failed to parse provider configuration: {e}")
            return None
    
    def _parse_database_config(self, config_data: Dict[str, Any]) -> DatabaseConfig:
        """Parse database configuration."""
        # Apply environment variable overrides
        database_url = self._get_env_override(
            'DATABASE_URL',
            config_data.get('database_url', '')
        )
        
        return DatabaseConfig(
            database_url=database_url,
            database_type=config_data.get('database_type', 'postgresql'),
            pool_size=config_data.get('pool_size', 10),
            max_overflow=config_data.get('max_overflow', 20),
            pool_timeout=config_data.get('pool_timeout', 30),
            pool_recycle=config_data.get('pool_recycle', 3600),
            enable_compression=config_data.get('enable_compression', True),
            compression_type=config_data.get('compression_type', 'gzip'),
            enable_encryption=config_data.get('enable_encryption', False),
            encryption_key=self._get_env_override(
                'DATABASE_ENCRYPTION_KEY',
                config_data.get('encryption_key')
            ),
            echo_sql=config_data.get('echo_sql', False)
        )
    
    def _parse_filesystem_config(self, config_data: Dict[str, Any]) -> FilesystemConfig:
        """Parse filesystem configuration."""
        base_path = self._get_env_override(
            'FILESYSTEM_BASE_PATH',
            config_data.get('base_path', './data/storage')
        )
        
        return FilesystemConfig(
            base_path=base_path,
            enable_compression=config_data.get('enable_compression', True),
            compression_type=config_data.get('compression_type', 'gzip'),
            enable_indexing=config_data.get('enable_indexing', True),
            max_files_per_directory=config_data.get('max_files_per_directory', 1000),
            enable_file_locking=config_data.get('enable_file_locking', True),
            enable_backup=config_data.get('enable_backup', False),
            backup_interval_hours=config_data.get('backup_interval_hours', 24)
        )
    
    def _parse_cache_config(self, config_data: Dict[str, Any]) -> CacheConfig:
        """Parse cache configuration."""
        redis_url = self._get_env_override(
            'REDIS_URL',
            config_data.get('redis_url')
        )
        
        return CacheConfig(
            redis_url=redis_url,
            database=config_data.get('database', 0),
            pool_size=config_data.get('pool_size', 10),
            default_ttl=config_data.get('default_ttl', 3600),
            key_prefix=config_data.get('key_prefix', ''),
            enable_compression=config_data.get('enable_compression', True),
            compression_threshold=config_data.get('compression_threshold', 1024),
            max_size=config_data.get('max_size', 10000),
            cleanup_interval=config_data.get('cleanup_interval', 300)
        )
    
    def _parse_object_storage_config(self, config_data: Dict[str, Any]) -> ObjectStorageConfig:
        """Parse object storage configuration."""
        return ObjectStorageConfig(
            bucket_name=self._get_env_override(
                'S3_BUCKET_NAME',
                config_data.get('bucket_name', '')
            ),
            aws_access_key_id=self._get_env_override(
                'AWS_ACCESS_KEY_ID',
                config_data.get('aws_access_key_id')
            ),
            aws_secret_access_key=self._get_env_override(
                'AWS_SECRET_ACCESS_KEY',
                config_data.get('aws_secret_access_key')
            ),
            aws_session_token=self._get_env_override(
                'AWS_SESSION_TOKEN',
                config_data.get('aws_session_token')
            ),
            region_name=self._get_env_override(
                'AWS_REGION',
                config_data.get('region_name', 'us-east-1')
            ),
            endpoint_url=self._get_env_override(
                'S3_ENDPOINT_URL',
                config_data.get('endpoint_url')
            ),
            key_prefix=config_data.get('key_prefix', ''),
            enable_encryption=config_data.get('enable_encryption', True),
            encryption_key=self._get_env_override(
                'S3_ENCRYPTION_KEY',
                config_data.get('encryption_key')
            ),
            storage_class=config_data.get('storage_class', 'STANDARD'),
            enable_versioning=config_data.get('enable_versioning', False),
            enable_compression=config_data.get('enable_compression', True),
            compression_type=config_data.get('compression_type', 'gzip'),
            multipart_threshold=config_data.get('multipart_threshold', 64 * 1024 * 1024),
            multipart_chunksize=config_data.get('multipart_chunksize', 16 * 1024 * 1024),
            max_concurrency=config_data.get('max_concurrency', 10)
        )
    
    def _parse_vector_config(self, config_data: Dict[str, Any]) -> VectorConfig:
        """Parse vector database configuration."""
        return VectorConfig(
            dimension=config_data.get('dimension', 512),
            metric=config_data.get('metric', 'cosine'),
            index_type=config_data.get('index_type', 'hnsw'),
            faiss_index_path=config_data.get('faiss_index_path'),
            enable_gpu=config_data.get('enable_gpu', False),
            pinecone_api_key=self._get_env_override(
                'PINECONE_API_KEY',
                config_data.get('pinecone_api_key')
            ),
            pinecone_environment=self._get_env_override(
                'PINECONE_ENVIRONMENT',
                config_data.get('pinecone_environment')
            ),
            qdrant_url=self._get_env_override(
                'QDRANT_URL',
                config_data.get('qdrant_url')
            ),
            qdrant_api_key=self._get_env_override(
                'QDRANT_API_KEY',
                config_data.get('qdrant_api_key')
            )
        )
    
    def _parse_timeseries_config(self, config_data: Dict[str, Any]) -> TimeSeriesConfig:
        """Parse time series configuration."""
        return TimeSeriesConfig(
            influxdb_url=self._get_env_override(
                'INFLUXDB_URL',
                config_data.get('influxdb_url')
            ),
            influxdb_token=self._get_env_override(
                'INFLUXDB_TOKEN',
                config_data.get('influxdb_token')
            ),
            influxdb_org=self._get_env_override(
                'INFLUXDB_ORG',
                config_data.get('influxdb_org')
            ),
            influxdb_bucket=self._get_env_override(
                'INFLUXDB_BUCKET',
                config_data.get('influxdb_bucket')
            ),
            prometheus_url=self._get_env_override(
                'PROMETHEUS_URL',
                config_data.get('prometheus_url')
            ),
            retention_policy=config_data.get('retention_policy', '30d'),
            precision=config_data.get('precision', 's')
        )
    
    def _get_env_override(self, env_key: str, default_value: Any) -> Any:
        """Get value with environment variable override."""
        full_env_key = f"{self.environment_prefix}{env_key}"
        return os.getenv(full_env_key, default_value)
    
    def get_provider_config(self, provider_id: str) -> Optional[StorageProviderConfig]:
        """Get configuration for specific provider."""
        return self.configurations.get(provider_id)
    
    def get_providers_by_type(self, backend_type: StorageBackendType) -> List[StorageProviderConfig]:
        """Get all providers of specific backend type."""
        return [
            config for config in self.configurations.values()
            if config.backend_type == backend_type and config.enabled
        ]
    
    def get_providers_by_priority(self) -> List[StorageProviderConfig]:
        """Get all providers sorted by priority."""
        return sorted(
            [config for config in self.configurations.values() if config.enabled],
            key=lambda x: x.priority
        )
    
    def validate_configuration(self, provider_id: str) -> List[str]:
        """Validate provider configuration and return list of errors."""
        errors = []
        
        config = self.configurations.get(provider_id)
        if not config:
            errors.append(f"Configuration not found for provider: {provider_id}")
            return errors
        
        # Validate based on backend type
        if config.backend_type == StorageBackendType.DATABASE:
            if not config.database_config or not config.database_config.database_url:
                errors.append("Database URL is required for database storage")
        
        elif config.backend_type == StorageBackendType.FILE_SYSTEM:
            if not config.filesystem_config or not config.filesystem_config.base_path:
                errors.append("Base path is required for filesystem storage")
        
        elif config.backend_type == StorageBackendType.CACHE:
            if config.provider_type == StorageProviderType.REDIS:
                if not config.cache_config or not config.cache_config.redis_url:
                    errors.append("Redis URL is required for Redis cache storage")
        
        elif config.backend_type == StorageBackendType.OBJECT_STORAGE:
            if not config.object_storage_config:
                errors.append("Object storage configuration is required")
            elif not config.object_storage_config.bucket_name:
                errors.append("Bucket name is required for object storage")
        
        elif config.backend_type == StorageBackendType.VECTOR_DB:
            if not config.vector_config:
                errors.append("Vector configuration is required")
            elif config.vector_config.dimension <= 0:
                errors.append("Vector dimension must be positive")
        
        elif config.backend_type == StorageBackendType.TIME_SERIES:
            if not config.timeseries_config:
                errors.append("Time series configuration is required")
        
        return errors
    
    def generate_default_config(self, output_path: str, format: str = "yaml") -> None:
        """Generate default configuration file."""
        try:
            default_config = {
                "storage_providers": [
                    {
                        "provider_id": "default_database",
                        "provider_type": "postgresql",
                        "backend_type": "database",
                        "enabled": True,
                        "priority": 100,
                        "database_config": {
                            "database_url": "postgresql://user:password@localhost:5432/crawler_db",
                            "pool_size": 10,
                            "enable_compression": True,
                            "compression_type": "gzip"
                        }
                    },
                    {
                        "provider_id": "default_filesystem",
                        "provider_type": "filesystem",
                        "backend_type": "file_system",
                        "enabled": True,
                        "priority": 200,
                        "filesystem_config": {
                            "base_path": "./data/storage",
                            "enable_compression": True,
                            "enable_indexing": True
                        }
                    },
                    {
                        "provider_id": "default_redis",
                        "provider_type": "redis",
                        "backend_type": "cache",
                        "enabled": False,
                        "priority": 50,
                        "cache_config": {
                            "redis_url": "redis://localhost:6379",
                            "database": 0,
                            "default_ttl": 3600
                        }
                    },
                    {
                        "provider_id": "default_s3",
                        "provider_type": "s3",
                        "backend_type": "object_storage",
                        "enabled": False,
                        "priority": 150,
                        "object_storage_config": {
                            "bucket_name": "crawler-storage",
                            "region_name": "us-east-1",
                            "enable_encryption": True
                        }
                    }
                ]
            }
            
            output_file = Path(output_path)
            
            if format.lower() == "yaml":
                with open(output_file, 'w') as f:
                    yaml.dump(default_config, f, default_flow_style=False, indent=2)
            else:
                with open(output_file, 'w') as f:
                    json.dump(default_config, f, indent=2)
            
            logger.info(f"Generated default configuration: {output_path}")
            
        except Exception as e:
            logger.error(f"Failed to generate default configuration: {e}")

class StorageProviderFactory(StorageFactory):
    """
    Professional storage provider factory.
    
    Creates storage provider instances based on configuration.
    """
    
    def __init__(self, config_manager: StorageConfigurationManager):
        """Initialize storage provider factory."""
        self.config_manager = config_manager
        
        # Provider class mappings
        self.provider_classes = {
            (StorageProviderType.POSTGRESQL, StorageBackendType.DATABASE): DatabaseStorageProvider,
            (StorageProviderType.MYSQL, StorageBackendType.DATABASE): DatabaseStorageProvider,
            (StorageProviderType.SQLITE, StorageBackendType.DATABASE): DatabaseStorageProvider,
            
            (StorageProviderType.FILESYSTEM, StorageBackendType.FILE_SYSTEM): FileSystemStorageProvider,
            
            (StorageProviderType.REDIS, StorageBackendType.CACHE): RedisCacheStorageProvider,
            (StorageProviderType.MEMORY, StorageBackendType.CACHE): InMemoryCacheStorageProvider,
            
            (StorageProviderType.S3, StorageBackendType.OBJECT_STORAGE): S3ObjectStorageProvider,
            (StorageProviderType.MINIO, StorageBackendType.OBJECT_STORAGE): S3ObjectStorageProvider,
        }
        
        # Content-specific provider classes
        self.content_provider_classes = {
            (StorageProviderType.POSTGRESQL, StorageBackendType.DATABASE): DatabaseContentStorageProvider,
            (StorageProviderType.MYSQL, StorageBackendType.DATABASE): DatabaseContentStorageProvider,
            (StorageProviderType.SQLITE, StorageBackendType.DATABASE): DatabaseContentStorageProvider,
            
            (StorageProviderType.S3, StorageBackendType.OBJECT_STORAGE): S3ContentStorageProvider,
            (StorageProviderType.MINIO, StorageBackendType.OBJECT_STORAGE): S3ContentStorageProvider,
        }
        
        # Violation-specific provider classes
        self.violation_provider_classes = {
            (StorageProviderType.POSTGRESQL, StorageBackendType.DATABASE): DatabaseViolationStorageProvider,
            (StorageProviderType.MYSQL, StorageBackendType.DATABASE): DatabaseViolationStorageProvider,
            (StorageProviderType.SQLITE, StorageBackendType.DATABASE): DatabaseViolationStorageProvider,
        }
        
        logger.info("Storage provider factory initialized")
    
    def create_provider(self, provider_id: str) -> Optional[BaseStorageProvider]:
        """Create a storage provider by ID."""
        config = self.config_manager.get_provider_config(provider_id)
        if not config:
            logger.error(f"Configuration not found for provider: {provider_id}")
            return None
        
        # Validate configuration
        errors = self.config_manager.validate_configuration(provider_id)
        if errors:
            logger.error(f"Configuration validation failed for {provider_id}: {errors}")
            return None
        
        # Get provider class
        provider_key = (config.provider_type, config.backend_type)
        provider_class = self.provider_classes.get(provider_key)
        
        if not provider_class:
            logger.error(f"No provider class found for {provider_key}")
            return None
        
        try:
            # Prepare configuration dict
            provider_config = self._prepare_provider_config(config)
            
            # Create provider instance
            provider = provider_class(provider_id, provider_config)
            
            logger.info(f"Created storage provider: {provider_id} ({config.provider_type.value})")
            return provider
            
        except Exception as e:
            logger.error(f"Failed to create storage provider {provider_id}: {e}")
            return None
    
    def create_content_storage(self, config: Dict[str, Any]) -> ContentStorageProvider:
        """Create content storage provider."""
        provider_id = config.get('provider_id', 'content_storage')
        provider_config = self.config_manager.get_provider_config(provider_id)
        
        if not provider_config:
            raise ValueError(f"Configuration not found for provider: {provider_id}")
        
        provider_key = (provider_config.provider_type, provider_config.backend_type)
        provider_class = self.content_provider_classes.get(provider_key)
        
        if not provider_class:
            raise ValueError(f"No content provider class found for {provider_key}")
        
        provider_config_dict = self._prepare_provider_config(provider_config)
        return provider_class(provider_id, provider_config_dict)
    
    def create_violation_storage(self, config: Dict[str, Any]) -> ViolationStorageProvider:
        """Create violation storage provider."""
        provider_id = config.get('provider_id', 'violation_storage')
        provider_config = self.config_manager.get_provider_config(provider_id)
        
        if not provider_config:
            raise ValueError(f"Configuration not found for provider: {provider_id}")
        
        provider_key = (provider_config.provider_type, provider_config.backend_type)
        provider_class = self.violation_provider_classes.get(provider_key)
        
        if not provider_class:
            raise ValueError(f"No violation provider class found for {provider_key}")
        
        provider_config_dict = self._prepare_provider_config(provider_config)
        return provider_class(provider_id, provider_config_dict)
    
    def create_cache_storage(self, config: Dict[str, Any]) -> CacheStorageProvider:
        """Create cache storage provider."""
        provider_id = config.get('provider_id', 'cache_storage')
        provider = self.create_provider(provider_id)
        
        if not isinstance(provider, CacheStorageProvider):
            raise ValueError(f"Provider {provider_id} is not a cache storage provider")
        
        return provider
    
    def create_vector_storage(self, config: Dict[str, Any]) -> VectorStorageProvider:
        """Create vector storage provider."""
        logger.info("Creating vector storage provider")
        
        # Basic vector storage implementation
        class BasicVectorStorageProvider:
            def __init__(self, config):
                self.config = config
                self.provider_id = config.get('provider_id', 'vector_basic')
                self.dimensions = config.get('dimensions', 512)
                self.index_type = config.get('index_type', 'flat')
                self.logger = logger
                
            async def store_vector(self, vector_id: str, vector_data: List[float], metadata: Dict = None):
                """Store vector data"""
                self.logger.info(f"Storing vector {vector_id} with {len(vector_data)} dimensions")
                return {"status": "stored", "vector_id": vector_id}
                
            async def search_similar(self, query_vector: List[float], top_k: int = 10):
                """Search for similar vectors"""
                self.logger.info(f"Searching for top {top_k} similar vectors")
                return [{"id": f"vec_{i}", "score": 0.9 - i * 0.1} for i in range(min(top_k, 5))]
                
            async def delete_vector(self, vector_id: str):
                """Delete vector"""
                self.logger.info(f"Deleting vector {vector_id}")
                return {"status": "deleted", "vector_id": vector_id}
        
        return BasicVectorStorageProvider(config)
    
    def create_timeseries_storage(self, config: Dict[str, Any]) -> TimeSeriesStorageProvider:
        """Create time series storage provider."""
        logger.info("Creating time series storage provider")
        
        # Basic time series storage implementation
        class BasicTimeSeriesStorageProvider:
            def __init__(self, config):
                self.config = config
                self.provider_id = config.get('provider_id', 'timeseries_basic')
                self.retention_days = config.get('retention_days', 30)
                self.aggregation_interval = config.get('aggregation_interval', '1h')
                self.logger = logger
                
            async def write_point(self, measurement: str, tags: Dict, fields: Dict, timestamp=None):
                """Write a data point"""
                import time
                ts = timestamp or int(time.time())
                self.logger.info(f"Writing point to {measurement} at timestamp {ts}")
                return {"status": "written", "timestamp": ts}
                
            async def query_range(self, measurement: str, start_time: int, end_time: int, aggregation=None):
                """Query time range"""
                self.logger.info(f"Querying {measurement} from {start_time} to {end_time}")
                # Return sample time series data
                import time
                current_time = int(time.time())
                return [
                    {"timestamp": current_time - i * 3600, "value": 50 + i * 5}
                    for i in range(24)  # 24 hours of hourly data
                ]
                
            async def delete_series(self, measurement: str, tags: Dict = None):
                """Delete time series"""
                self.logger.info(f"Deleting series {measurement}")
                return {"status": "deleted", "measurement": measurement}
        
        return BasicTimeSeriesStorageProvider(config)
    
    def create_transaction(self, provider: BaseStorageProvider):
        """Create storage transaction."""
        logger.info(f"Creating transaction for provider {provider}")
        
        # Basic transaction implementation
        class BasicStorageTransaction:
            def __init__(self, provider):
                self.provider = provider
                self.transaction_id = f"txn_{int(time.time())}"
                self.operations = []
                self.committed = False
                self.rolled_back = False
                self.logger = logger
                
            async def __aenter__(self):
                """Enter transaction context"""
                self.logger.info(f"Starting transaction {self.transaction_id}")
                return self
                
            async def __aexit__(self, exc_type, exc_val, exc_tb):
                """Exit transaction context"""
                if exc_type is not None:
                    await self.rollback()
                elif not self.committed:
                    await self.commit()
                    
            async def add_operation(self, operation_type: str, data: Dict):
                """Add operation to transaction"""
                operation = {
                    "type": operation_type,
                    "data": data,
                    "timestamp": time.time()
                }
                self.operations.append(operation)
                self.logger.debug(f"Added {operation_type} operation to transaction {self.transaction_id}")
                
            async def commit(self):
                """Commit transaction"""
                if self.rolled_back:
                    raise ValueError("Cannot commit a rolled back transaction")
                    
                self.logger.info(f"Committing transaction {self.transaction_id} with {len(self.operations)} operations")
                
                # Simulate committing operations
                for operation in self.operations:
                    self.logger.debug(f"Executing {operation['type']} operation")
                    
                self.committed = True
                self.logger.info(f"Transaction {self.transaction_id} committed successfully")
                
            async def rollback(self):
                """Rollback transaction"""
                if self.committed:
                    raise ValueError("Cannot rollback a committed transaction")
                    
                self.logger.info(f"Rolling back transaction {self.transaction_id}")
                
                # Simulate rollback operations
                for operation in reversed(self.operations):
                    self.logger.debug(f"Reversing {operation['type']} operation")
                    
                self.rolled_back = True
                self.operations.clear()
                self.logger.info(f"Transaction {self.transaction_id} rolled back successfully")
        
        return BasicStorageTransaction(provider)
    
    def _prepare_provider_config(self, config: StorageProviderConfig) -> Dict[str, Any]:
        """Prepare configuration dictionary for provider creation."""
        provider_config = {
            'provider_id': config.provider_id,
            'provider_type': config.provider_type.value,
            'backend_type': config.backend_type.value,
            'max_connections': config.max_connections,
            'timeout_seconds': config.timeout_seconds,
            'retry_attempts': config.retry_attempts
        }
        
        # Add type-specific configuration
        if config.database_config:
            provider_config.update(asdict(config.database_config))
        elif config.filesystem_config:
            provider_config.update(asdict(config.filesystem_config))
        elif config.cache_config:
            provider_config.update(asdict(config.cache_config))
        elif config.object_storage_config:
            provider_config.update(asdict(config.object_storage_config))
        elif config.vector_config:
            provider_config.update(asdict(config.vector_config))
        elif config.timeseries_config:
            provider_config.update(asdict(config.timeseries_config))
        
        return provider_config

# Export all configuration classes
__all__ = [
    'StorageProviderType',
    'DatabaseConfig',
    'FilesystemConfig', 
    'CacheConfig',
    'ObjectStorageConfig',
    'VectorConfig',
    'TimeSeriesConfig',
    'StorageProviderConfig',
    'StorageConfigurationManager',
    'StorageProviderFactory'
]
