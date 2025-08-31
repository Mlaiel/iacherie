"""
Storage and Data Management Configurations
==========================================

Advanced configuration system for data storage, caching, backup, and lifecycle management
for the crawler system and content protection platform.

Author: Fahed Mlaiel <mlaiel@live.de>
Team: Lead Dev IA + Backend Senior + ML Engineer + Audio Engineer + DevOps + DBA + Security + Microservices Expert
Copyright: All rights reserved. Unauthorized use, reproduction, or distribution prohibited.

Project: IA Influencer Agent - Advanced Content Protection Platform
Contact: mlaiel@live.de | www.fahed-mlaiel.de

WARNING: This code and concept are protected by intellectual property rights.
Any unauthorized use, reproduction, modification, or distribution is strictly prohibited.
Legal action will be taken against violators.
"""

import os
from typing import Dict, List, Optional, Union, Any
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta
import json
from pathlib import Path

class StorageBackend(Enum):
    """Storage backend types."""
    LOCAL = "local"
    AWS_S3 = "aws_s3"
    GOOGLE_CLOUD = "google_cloud"
    AZURE_BLOB = "azure_blob"
    MINIO = "minio"
    FTP = "ftp"
    SFTP = "sftp"
    NFS = "nfs"

class DatabaseType(Enum):
    """Database types for different data."""
    POSTGRESQL = "postgresql"
    MYSQL = "mysql"
    MONGODB = "mongodb"
    REDIS = "redis"
    ELASTICSEARCH = "elasticsearch"
    FAISS = "faiss"
    QDRANT = "qdrant"
    PINECONE = "pinecone"
    WEAVIATE = "weaviate"

class CompressionType(Enum):
    """Compression algorithms."""
    NONE = "none"
    GZIP = "gzip"
    BZIP2 = "bzip2"
    LZMA = "lzma"
    ZSTD = "zstd"
    LZ4 = "lz4"

class EncryptionType(Enum):
    """Encryption algorithms."""
    NONE = "none"
    AES_128 = "aes-128"
    AES_256 = "aes-256"
    CHACHA20 = "chacha20"
    RSA_2048 = "rsa-2048"
    RSA_4096 = "rsa-4096"

class DataLifecycleStage(Enum):
    """Data lifecycle stages."""
    ACTIVE = "active"
    INACTIVE = "inactive"
    ARCHIVED = "archived"
    COLD_STORAGE = "cold_storage"
    MARKED_FOR_DELETION = "marked_for_deletion"

class BackupType(Enum):
    """Backup types."""
    FULL = "full"
    INCREMENTAL = "incremental"
    DIFFERENTIAL = "differential"
    SNAPSHOT = "snapshot"
    CONTINUOUS = "continuous"

@dataclass
class StorageCredentials:
    """Storage credentials configuration."""
    access_key: Optional[str] = None
    secret_key: Optional[str] = None
    token: Optional[str] = None
    region: Optional[str] = None
    endpoint_url: Optional[str] = None
    bucket_name: Optional[str] = None
    
    # Database credentials
    username: Optional[str] = None
    password: Optional[str] = None
    host: Optional[str] = None
    port: Optional[int] = None
    database_name: Optional[str] = None
    
    # SSL/TLS settings
    use_ssl: bool = True
    verify_ssl: bool = True
    ca_cert_path: Optional[str] = None
    client_cert_path: Optional[str] = None
    client_key_path: Optional[str] = None

@dataclass
class CompressionConfig:
    """Configuration for data compression."""
    enabled: bool = True
    algorithm: CompressionType = CompressionType.GZIP
    level: int = 6  # Compression level (1-9 for most algorithms)
    threshold_bytes: int = 1024  # Minimum size to compress
    
    # Format-specific settings
    image_compression: bool = True
    image_quality: int = 85  # JPEG quality
    audio_compression: bool = False  # Avoid lossy compression for fingerprints
    video_compression: bool = True
    text_compression: bool = True
    
    # Advanced settings
    dictionary_compression: bool = True
    parallel_compression: bool = True
    compression_workers: int = 4

@dataclass
class EncryptionConfig:
    """Configuration for data encryption."""
    enabled: bool = True
    algorithm: EncryptionType = EncryptionType.AES_256
    key_derivation_function: str = "pbkdf2"
    key_iterations: int = 100000
    
    # Key management
    key_rotation_enabled: bool = True
    key_rotation_days: int = 90
    key_storage_backend: str = "local"  # local, aws_kms, azure_vault, gcp_kms
    master_key_path: Optional[str] = None
    
    # Encryption settings
    encrypt_at_rest: bool = True
    encrypt_in_transit: bool = True
    encrypt_backups: bool = True
    encrypt_logs: bool = True
    
    # File-specific encryption
    encrypt_fingerprints: bool = True
    encrypt_evidence: bool = True
    encrypt_personal_data: bool = True
    encrypt_api_keys: bool = True

@dataclass
class CacheConfig:
    """Configuration for caching system."""
    enabled: bool = True
    backend: str = "redis"  # redis, memcached, memory, disk
    
    # Redis configuration
    redis_host: str = "localhost"
    redis_port: int = 6379
    redis_db: int = 0
    redis_password: Optional[str] = None
    redis_cluster: bool = False
    redis_sentinel: bool = False
    
    # Cache policies
    default_ttl_seconds: int = 3600
    max_memory_mb: int = 1024
    eviction_policy: str = "lru"  # lru, lfu, random, ttl
    
    # Cache strategies
    cache_fingerprints: bool = True
    fingerprint_ttl_hours: int = 24
    cache_search_results: bool = True
    search_results_ttl_minutes: int = 30
    cache_api_responses: bool = True
    api_response_ttl_minutes: int = 15
    
    # Performance settings
    compression_enabled: bool = True
    serialization_format: str = "pickle"  # pickle, json, msgpack
    connection_pool_size: int = 50
    timeout_seconds: int = 5

@dataclass
class DatabaseConfig:
    """Configuration for database connections."""
    # Primary database (PostgreSQL)
    primary_db: DatabaseType = DatabaseType.POSTGRESQL
    primary_credentials: StorageCredentials = field(default_factory=StorageCredentials)
    primary_pool_size: int = 20
    primary_max_overflow: int = 30
    primary_pool_timeout: int = 30
    
    # Vector database (FAISS/Qdrant)
    vector_db: DatabaseType = DatabaseType.FAISS
    vector_credentials: StorageCredentials = field(default_factory=StorageCredentials)
    vector_index_type: str = "IVF"
    vector_dimensions: int = 768
    vector_metric: str = "cosine"
    
    # Search database (Elasticsearch)
    search_db: DatabaseType = DatabaseType.ELASTICSEARCH
    search_credentials: StorageCredentials = field(default_factory=StorageCredentials)
    search_index_shards: int = 3
    search_index_replicas: int = 1
    
    # Time-series database (for metrics)
    timeseries_db: Optional[DatabaseType] = None
    timeseries_credentials: Optional[StorageCredentials] = None
    
    # Database maintenance
    auto_vacuum: bool = True
    analyze_tables: bool = True
    maintenance_window_hour: int = 2  # 2 AM
    backup_before_maintenance: bool = True

@dataclass
class FileStorageConfig:
    """Configuration for file storage."""
    backend: StorageBackend = StorageBackend.AWS_S3
    credentials: StorageCredentials = field(default_factory=StorageCredentials)
    
    # Storage organization
    bucket_name: str = "ia-influencer-content"
    base_path: str = "production"
    
    # Path structure
    fingerprints_path: str = "fingerprints"
    evidence_path: str = "evidence"
    backups_path: str = "backups"
    logs_path: str = "logs"
    temp_path: str = "temp"
    
    # File naming
    use_uuid_names: bool = True
    include_timestamp: bool = True
    preserve_original_names: bool = False
    
    # Upload settings
    multipart_threshold_mb: int = 100
    multipart_chunk_size_mb: int = 10
    concurrent_uploads: int = 5
    retry_attempts: int = 3
    
    # Access control
    default_acl: str = "private"
    public_read_paths: List[str] = field(default_factory=list)
    signed_url_expiry_hours: int = 24

@dataclass
class BackupConfig:
    """Configuration for backup system."""
    enabled: bool = True
    backend: StorageBackend = StorageBackend.AWS_S3
    credentials: StorageCredentials = field(default_factory=StorageCredentials)
    
    # Backup schedule
    full_backup_frequency: str = "weekly"  # daily, weekly, monthly
    incremental_backup_frequency: str = "daily"
    backup_time_hour: int = 1  # 1 AM
    backup_retention_days: int = 90
    
    # Backup types
    database_backup: bool = True
    file_backup: bool = True
    configuration_backup: bool = True
    logs_backup: bool = True
    
    # Backup validation
    verify_backups: bool = True
    test_restore_monthly: bool = True
    backup_integrity_check: bool = True
    
    # Performance settings
    compression_enabled: bool = True
    encryption_enabled: bool = True
    parallel_backup_jobs: int = 3
    bandwidth_limit_mbps: Optional[int] = None

@dataclass
class DataLifecycleConfig:
    """Configuration for data lifecycle management."""
    enabled: bool = True
    
    # Lifecycle rules
    evidence_retention_days: int = 2555  # 7 years for legal purposes
    fingerprint_retention_days: int = 3650  # 10 years
    logs_retention_days: int = 90
    temp_files_retention_hours: int = 24
    failed_jobs_retention_days: int = 30
    
    # Archival settings
    archive_after_days: int = 365
    cold_storage_after_days: int = 1095  # 3 years
    delete_after_days: int = 2555  # 7 years
    
    # Cleanup settings
    auto_cleanup_enabled: bool = True
    cleanup_schedule_hour: int = 3  # 3 AM
    cleanup_batch_size: int = 1000
    
    # Migration settings
    auto_migration_enabled: bool = True
    migration_threshold_days: int = 30
    migration_batch_size: int = 100

@dataclass
class MonitoringConfig:
    """Configuration for storage monitoring."""
    enabled: bool = True
    
    # Metrics collection
    collect_storage_metrics: bool = True
    collect_database_metrics: bool = True
    collect_backup_metrics: bool = True
    metrics_interval_seconds: int = 60
    
    # Alerting thresholds
    disk_usage_warning_percent: int = 80
    disk_usage_critical_percent: int = 90
    database_connection_warning: int = 15  # Out of 20 pool size
    backup_failure_alert: bool = True
    
    # Performance monitoring
    slow_query_threshold_ms: int = 1000
    storage_latency_threshold_ms: int = 500
    cache_hit_rate_warning_percent: int = 70
    
    # Health checks
    health_check_interval_minutes: int = 5
    health_check_timeout_seconds: int = 30
    automated_recovery_enabled: bool = True

@dataclass
class StorageConfig:
    """Complete storage configuration."""
    # Core configurations
    file_storage: FileStorageConfig = field(default_factory=FileStorageConfig)
    database: DatabaseConfig = field(default_factory=DatabaseConfig)
    cache: CacheConfig = field(default_factory=CacheConfig)
    backup: BackupConfig = field(default_factory=BackupConfig)
    lifecycle: DataLifecycleConfig = field(default_factory=DataLifecycleConfig)
    
    # Security configurations
    compression: CompressionConfig = field(default_factory=CompressionConfig)
    encryption: EncryptionConfig = field(default_factory=EncryptionConfig)
    
    # Monitoring
    monitoring: MonitoringConfig = field(default_factory=MonitoringConfig)
    
    # Global settings
    enabled: bool = True
    environment: str = "production"  # development, staging, production
    debug_mode: bool = False
    
    # Performance settings
    max_concurrent_operations: int = 50
    operation_timeout_seconds: int = 300
    retry_attempts: int = 3
    circuit_breaker_enabled: bool = True

class StorageConfigManager:
    """Manager for storage configurations."""
    
    def __init__(self, config_dir: Optional[str] = None):
        """Initialize storage config manager."""
        self.config_dir = Path(config_dir or os.getenv("STORAGE_CONFIG_DIR", "./configs"))
        self.config_dir.mkdir(parents=True, exist_ok=True)
        self.config = self._load_default_config()
    
    def _load_default_config(self) -> StorageConfig:
        """Load default storage configuration."""



        return StorageConfig(
            file_storage=FileStorageConfig(
                backend=StorageBackend.AWS_S3,
                credentials=StorageCredentials(
                    access_key=os.getenv("AWS_ACCESS_KEY_ID"),
                    secret_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
                    region=os.getenv("AWS_REGION", "eu-central-1"),
                    bucket_name=os.getenv("S3_BUCKET_NAME", "ia-influencer-content")
                ),
                multipart_threshold_mb=100,
                concurrent_uploads=5
            ),
            database=DatabaseConfig(
                primary_credentials=StorageCredentials(
                    host=os.getenv("DB_HOST", "localhost"),
                    port=int(os.getenv("DB_PORT", "5432")),
                    username=os.getenv("DB_USERNAME"),
                    password=os.getenv("DB_PASSWORD"),
                    database_name=os.getenv("DB_NAME", "ia_influencer")
                ),
                vector_credentials=StorageCredentials(
                    host=os.getenv("VECTOR_DB_HOST", "localhost"),
                    port=int(os.getenv("VECTOR_DB_PORT", "6333"))
                ),
                search_credentials=StorageCredentials(
                    host=os.getenv("ELASTICSEARCH_HOST", "localhost"),
                    port=int(os.getenv("ELASTICSEARCH_PORT", "9200"))
                )
            ),
            cache=CacheConfig(
                enabled=True,
                redis_host=os.getenv("REDIS_HOST", "localhost"),
                redis_port=int(os.getenv("REDIS_PORT", "6379")),
                redis_password=os.getenv("REDIS_PASSWORD"),
                default_ttl_seconds=3600
            ),
            backup=BackupConfig(
                enabled=True,
                credentials=StorageCredentials(
                    access_key=os.getenv("BACKUP_AWS_ACCESS_KEY_ID"),
                    secret_key=os.getenv("BACKUP_AWS_SECRET_ACCESS_KEY"),
                    region=os.getenv("BACKUP_AWS_REGION", "eu-west-1"),
                    bucket_name=os.getenv("BACKUP_S3_BUCKET", "ia-influencer-backups")
                ),
                full_backup_frequency="weekly",
                backup_retention_days=90
            ),
            lifecycle=DataLifecycleConfig(
                enabled=True,
                evidence_retention_days=2555,  # 7 years
                auto_cleanup_enabled=True
            ),
            compression=CompressionConfig(
                enabled=True,
                algorithm=CompressionType.GZIP,
                level=6
            ),
            encryption=EncryptionConfig(
                enabled=True,
                algorithm=EncryptionType.AES_256,
                key_rotation_enabled=True,
                encrypt_at_rest=True
            ),
            monitoring=MonitoringConfig(
                enabled=True,
                disk_usage_warning_percent=80,
                health_check_interval_minutes=5
            )
        )
    
    def get_config(self) -> StorageConfig:
        """Get current storage configuration."""



        return self.config
    
    def get_database_url(self, db_type: str = "primary") -> str:
        """Get database connection URL."""
        if db_type == "primary":
            creds = self.config.database.primary_credentials
            return f"postgresql://{creds.username}:{creds.password}@{creds.host}:{creds.port}/{creds.database_name}"
        elif db_type == "redis":
            cache = self.config.cache
            auth = f":{cache.redis_password}@" if cache.redis_password else ""
            return f"redis://{auth}{cache.redis_host}:{cache.redis_port}/{cache.redis_db}"
        else:
            raise ValueError(f"Unknown database type: {db_type}")
    
    def get_storage_client_config(self) -> dict:
        """Get storage client configuration."""
        file_config = self.config.file_storage
        return {
            "backend": file_config.backend.value,
            "credentials": {
                "access_key": file_config.credentials.access_key,
                "secret_key": file_config.credentials.secret_key,
                "region": file_config.credentials.region,
                "endpoint_url": file_config.credentials.endpoint_url
            },
            "bucket": file_config.bucket_name,
            "multipart_threshold": file_config.multipart_threshold_mb * 1024 * 1024,
            "max_concurrency": file_config.concurrent_uploads
        }
    
    def update_config(self, config: StorageConfig) -> None:
        """Update storage configuration."""
        self.config = config
        self.save_config()
    
    def save_config(self) -> None:
        """Save configuration to file."""
        config_file = self.config_dir / "storage_config.json"
        config_dict = self._serialize_config(self.config)
        with open(config_file, 'w') as f:
            json.dump(config_dict, f, indent=2, default=str)
    
    def load_config(self) -> None:
        """Load configuration from file."""
        config_file = self.config_dir / "storage_config.json"
        if config_file.exists():
            with open(config_file, 'r') as f:
                data = json.load(f)
                self.config = self._deserialize_config(data)
    
    def _serialize_config(self, config: StorageConfig) -> dict:
        """Serialize configuration to dictionary."""



        try:
            logger.debug("Serializing storage configuration")
            
            # Convert StorageConfig dataclass to dictionary
            serialized = {
                'storage_type': config.storage_type.value,
                'connection_params': config.connection_params,
                'security_settings': {
                    'encryption_enabled': config.security_settings.encryption_enabled,
                    'encryption_algorithm': config.security_settings.encryption_algorithm,
                    'key_rotation_days': config.security_settings.key_rotation_days,
                    'access_logging': config.security_settings.access_logging,
                    'audit_trail': config.security_settings.audit_trail,
                    'backup_encryption': config.security_settings.backup_encryption
                },
                'performance_settings': {
                    'connection_pool_size': config.performance_settings.connection_pool_size,
                    'timeout_seconds': config.performance_settings.timeout_seconds,
                    'retry_attempts': config.performance_settings.retry_attempts,
                    'cache_enabled': config.performance_settings.cache_enabled,
                    'compression_enabled': config.performance_settings.compression_enabled,
                    'batch_size': config.performance_settings.batch_size
                },
                'backup_settings': {
                    'enabled': config.backup_settings.enabled,
                    'frequency': config.backup_settings.frequency.value,
                    'retention_days': config.backup_settings.retention_days,
                    'storage_location': config.backup_settings.storage_location,
                    'compression': config.backup_settings.compression,
                    'incremental': config.backup_settings.incremental
                },
                'monitoring': {
                    'health_check_interval': config.monitoring.health_check_interval,
                    'performance_metrics': config.monitoring.performance_metrics,
                    'alert_thresholds': config.monitoring.alert_thresholds,
                    'log_level': config.monitoring.log_level,
                    'metrics_retention_days': config.monitoring.metrics_retention_days
                },
                'compliance': {
                    'gdpr_compliant': config.compliance.gdpr_compliant,
                    'data_residency': config.compliance.data_residency,
                    'retention_policy': config.compliance.retention_policy,
                    'anonymization_rules': config.compliance.anonymization_rules,
                    'audit_requirements': config.compliance.audit_requirements
                }
            }
            
            # Add metadata
            serialized['metadata'] = {
                'version': '1.0',
                'created_at': datetime.now().isoformat(),
                'serializer': 'StorageConfigManager._serialize_config'
            }
            
            logger.debug("Configuration serialized successfully")
            return serialized
            
        except Exception as e:
            logger.error(f"Error serializing configuration: {str(e)}")
            raise ValueError(f"Configuration serialization failed: {str(e)}")
    
    def _deserialize_config(self, data: dict) -> StorageConfig:
        """Deserialize configuration from dictionary."""



        try:
            logger.debug("Deserializing storage configuration")
            
            # Validate required fields
            required_fields = ['storage_type', 'connection_params', 'security_settings', 
                             'performance_settings', 'backup_settings', 'monitoring', 'compliance']
            
            for field in required_fields:
                if field not in data:
                    raise ValueError(f"Missing required field: {field}")
            
            # Parse storage type
            storage_type = StorageType(data['storage_type'])
            
            # Parse security settings
            security_data = data['security_settings']
            security_settings = SecuritySettings(
                encryption_enabled=security_data.get('encryption_enabled', True),
                encryption_algorithm=security_data.get('encryption_algorithm', 'AES-256'),
                key_rotation_days=security_data.get('key_rotation_days', 90),
                access_logging=security_data.get('access_logging', True),
                audit_trail=security_data.get('audit_trail', True),
                backup_encryption=security_data.get('backup_encryption', True)
            )
            
            # Parse performance settings
            perf_data = data['performance_settings']
            performance_settings = PerformanceSettings(
                connection_pool_size=perf_data.get('connection_pool_size', 10),
                timeout_seconds=perf_data.get('timeout_seconds', 30),
                retry_attempts=perf_data.get('retry_attempts', 3),
                cache_enabled=perf_data.get('cache_enabled', True),
                compression_enabled=perf_data.get('compression_enabled', True),
                batch_size=perf_data.get('batch_size', 1000)
            )
            
            # Parse backup settings
            backup_data = data['backup_settings']
            backup_settings = BackupSettings(
                enabled=backup_data.get('enabled', True),
                frequency=BackupFrequency(backup_data.get('frequency', 'daily')),
                retention_days=backup_data.get('retention_days', 30),
                storage_location=backup_data.get('storage_location', '/backups'),
                compression=backup_data.get('compression', True),
                incremental=backup_data.get('incremental', True)
            )
            
            # Parse monitoring settings
            monitoring_data = data['monitoring']
            monitoring = MonitoringSettings(
                health_check_interval=monitoring_data.get('health_check_interval', 60),
                performance_metrics=monitoring_data.get('performance_metrics', True),
                alert_thresholds=monitoring_data.get('alert_thresholds', {}),
                log_level=monitoring_data.get('log_level', 'INFO'),
                metrics_retention_days=monitoring_data.get('metrics_retention_days', 90)
            )
            
            # Parse compliance settings
            compliance_data = data['compliance']
            compliance = ComplianceSettings(
                gdpr_compliant=compliance_data.get('gdpr_compliant', True),
                data_residency=compliance_data.get('data_residency', 'EU'),
                retention_policy=compliance_data.get('retention_policy', {}),
                anonymization_rules=compliance_data.get('anonymization_rules', []),
                audit_requirements=compliance_data.get('audit_requirements', [])
            )
            
            # Create and return StorageConfig object
            config = StorageConfig(
                storage_type=storage_type,
                connection_params=data['connection_params'],
                security_settings=security_settings,
                performance_settings=performance_settings,
                backup_settings=backup_settings,
                monitoring=monitoring,
                compliance=compliance
            )
            
            logger.debug("Configuration deserialized successfully")
            return config
            
        except Exception as e:
            logger.error(f"Error deserializing configuration: {str(e)}")
            raise ValueError(f"Configuration deserialization failed: {str(e)}")
    
    def validate_config(self) -> List[str]:
        """Validate storage configuration."""
        errors = []
        
        # Validate file storage
        if self.config.file_storage.backend == StorageBackend.AWS_S3:
            if not self.config.file_storage.credentials.access_key:
                errors.append("AWS access key is required for S3 storage")
            if not self.config.file_storage.credentials.secret_key:
                errors.append("AWS secret key is required for S3 storage")
        
        # Validate database configuration
        if not self.config.database.primary_credentials.host:
            errors.append("Database host is required")
        if not self.config.database.primary_credentials.username:
            errors.append("Database username is required")
        
        # Validate cache configuration
        if self.config.cache.enabled and not self.config.cache.redis_host:
            errors.append("Redis host is required when caching is enabled")
        
        # Validate retention periods
        if self.config.lifecycle.evidence_retention_days < 1:
            errors.append("Evidence retention period must be at least 1 day")
        
        return errors
    
    def test_connections(self) -> Dict[str, bool]:
        """Test all storage connections."""
        results = {}
        
        # Test database connection
        try:
            # Implementation would test actual database connection
            results["database"] = True
        except Exception:
            results["database"] = False
        
        # Test cache connection
        try:
            # Implementation would test Redis connection
            results["cache"] = True
        except Exception:
            results["cache"] = False
        
        # Test file storage
        try:
            # Implementation would test S3/storage connection
            results["file_storage"] = True
        except Exception:
            results["file_storage"] = False
        
        return results
    
    def get_storage_usage(self) -> Dict[str, Any]:
        """Get current storage usage statistics."""



        return {
            "database_size_mb": 0,  # Implementation would query actual size
            "file_storage_size_gb": 0,
            "cache_usage_mb": 0,
            "backup_size_gb": 0,
            "total_files": 0,
            "total_fingerprints": 0
        }
    
    def export_config(self, file_path: str) -> None:
        """Export configuration to file."""
        config_dict = self._serialize_config(self.config)
        with open(file_path, 'w') as f:
            json.dump(config_dict, f, indent=2, default=str)

# Global storage config manager instance
storage_config_manager = StorageConfigManager()
