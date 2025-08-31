"""Configuration Manager - IA Influencer Agent Platform

Centralized configuration management for database connections:
- Environment-specific configurations
- Dynamic configuration updates
- Configuration validation and defaults
- Secure credential management
- Multi-tenant configuration isolation
- Configuration monitoring and auditing

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.
"""import asyncio
import logging
import os
import json
import yaml
from typing import Dict, Any, Optional, List, Union, Type
from dataclasses import dataclass, field, asdict
from datetime import datetime
from pathlib import Path
from enum import Enum
import re
from cryptography.fernet import Fernet
import base64


class Environment(Enum):
    """Deployment environments"""    DEVELOPMENT = "development"
    TESTING = "testing"
    STAGING = "staging"
    PRODUCTION = "production"


class ConfigurationSource(Enum):
    """Configuration sources"""    FILE = "file"
    ENVIRONMENT = "environment"
    DATABASE = "database"
    VAULT = "vault"
    REMOTE = "remote"


@dataclass
class DatabaseConfig:
    """Database configuration"""    host: str
    port: int
    database: str
    username: str
    password: str
    ssl_mode: str = "prefer"
    pool_size: int = 10
    max_overflow: int = 20
    pool_timeout: int = 30
    pool_recycle: int = 3600
    pool_pre_ping: bool = True
    connect_timeout: int = 10
    command_timeout: int = 30
    retry_attempts: int = 3
    retry_delay: float = 1.0
    
    def to_url(self, driver: str = "postgresql+asyncpg") -> str:
        """Convert to database URL"""        return (
            f"{driver}://{self.username}:{self.password}@"
            f"{self.host}:{self.port}/{self.database}"
        )


@dataclass
class RedisConfig:
    """Redis configuration"""    host: str
    port: int = 6379
    db: int = 0
    password: Optional[str] = None
    ssl: bool = False
    socket_timeout: int = 30
    socket_connect_timeout: int = 30
    connection_pool_size: int = 50
    max_connections: int = 100
    retry_on_timeout: bool = True
    health_check_interval: int = 30
    
    # Sentinel configuration
    sentinel_hosts: Optional[List[str]] = None
    sentinel_service_name: Optional[str] = None
    
    # Cluster configuration
    cluster_nodes: Optional[List[str]] = None


@dataclass
class MongoConfig:
    """MongoDB configuration"""    host: str
    port: int = 27017
    database: str
    username: Optional[str] = None
    password: Optional[str] = None
    auth_source: str = "admin"
    replica_set: Optional[str] = None
    ssl: bool = False
    ssl_ca_certs: Optional[str] = None
    max_pool_size: int = 100
    min_pool_size: int = 0
    max_idle_time_ms: int = 0
    connect_timeout_ms: int = 20000
    server_selection_timeout_ms: int = 30000
    
    def to_url(self) -> str:
        """Convert to MongoDB URL"""        auth = ""
        if self.username and self.password:
            auth = f"{self.username}:{self.password}@"
        
        options = []
        if self.auth_source:
            options.append(f"authSource={self.auth_source}")
        if self.replica_set:
            options.append(f"replicaSet={self.replica_set}")
        if self.ssl:
            options.append("ssl=true")
        
        options_str = "?" + "&".join(options) if options else ""
        
        return f"mongodb://{auth}{self.host}:{self.port}/{self.database}{options_str}"


@dataclass
class ElasticsearchConfig:
    """Elasticsearch configuration"""    hosts: List[str]
    username: Optional[str] = None
    password: Optional[str] = None
    api_key: Optional[str] = None
    ssl: bool = False
    verify_certs: bool = True
    ca_certs: Optional[str] = None
    timeout: int = 30
    max_retries: int = 3
    retry_on_timeout: bool = True
    sniff_on_start: bool = False
    sniff_on_connection_fail: bool = False
    sniffer_timeout: int = 0.1


@dataclass
class VectorStoreConfig:
    """Vector store configuration"""    provider: str  # faiss, pinecone, weaviate, etc.
    
    # FAISS specific
    index_path: Optional[str] = None
    dimension: int = 768
    
    # Pinecone specific
    api_key: Optional[str] = None
    environment: Optional[str] = None
    index_name: Optional[str] = None
    
    # Weaviate specific
    url: Optional[str] = None
    auth_client_secret: Optional[str] = None
    
    # Common settings
    metric: str = "cosine"
    max_connections: int = 100


@dataclass
class ObjectStorageConfig:
    """Object storage configuration"""    provider: str  # s3, minio, gcs, azure
    
    # S3/MinIO
    endpoint_url: Optional[str] = None
    access_key_id: Optional[str] = None
    secret_access_key: Optional[str] = None
    region_name: str = "us-east-1"
    bucket_name: Optional[str] = None
    
    # Common settings
    use_ssl: bool = True
    max_pool_connections: int = 50
    retry_attempts: int = 3
    connect_timeout: int = 60
    read_timeout: int = 60


@dataclass
class TenantConfig:
    """Tenant-specific configuration"""    tenant_id: str
    name: str
    database_config: Optional[DatabaseConfig] = None
    redis_config: Optional[RedisConfig] = None
    mongo_config: Optional[MongoConfig] = None
    elasticsearch_config: Optional[ElasticsearchConfig] = None
    vector_store_config: Optional[VectorStoreConfig] = None
    object_storage_config: Optional[ObjectStorageConfig] = None
    
    # Tenant limits
    max_connections: int = 100
    max_storage_gb: int = 100
    max_requests_per_minute: int = 1000
    
    # Features
    features_enabled: List[str] = field(default_factory=list)
    
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)


class DatabaseConfigurationManager:
    """    Centralized database configuration manager.
    
    Provides:
    - Environment-specific configurations
    - Dynamic configuration updates
    - Configuration validation
    - Secure credential management
    - Multi-tenant configuration isolation
    - Configuration monitoring and auditing
    """    
    def __init__(self, environment: Environment = Environment.DEVELOPMENT):
        self.logger = logging.getLogger(__name__)
        self.environment = environment
        
        # Configuration storage
        self.global_config: Dict[str, Any] = {}
        self.tenant_configs: Dict[str, TenantConfig] = {}
        
        # Configuration sources
        self.config_sources: List[ConfigurationSource] = [
            ConfigurationSource.ENVIRONMENT,
            ConfigurationSource.FILE
        ]
        
        # Configuration files
        self.config_dir = Path("config")
        self.config_files = {
            "global": "database.yml",
            "tenants": "tenants.yml",
            "secrets": "secrets.yml"
        }
        
        # Encryption for sensitive data
        self.encryption_key = self._get_encryption_key()
        self.cipher_suite = Fernet(self.encryption_key) if self.encryption_key else None
        
        # Configuration validation
        self.validation_rules: Dict[str, Dict[str, Any]] = {}
        
        # Monitoring
        self.config_change_callbacks: List[callable] = []
        self.audit_log: List[Dict[str, Any]] = []
        
        # Defaults
        self._setup_defaults()
    
    def _get_encryption_key(self) -> Optional[bytes]:
        """Get encryption key for sensitive data"""        key_env = os.getenv("DATABASE_CONFIG_ENCRYPTION_KEY")
        if key_env:
            try:
                return base64.urlsafe_b64decode(key_env.encode())
            except Exception:
                pass
        
        # Generate new key if not provided (development only)
        if self.environment == Environment.DEVELOPMENT:
            key = Fernet.generate_key()
            self.logger.warning(
                f"Generated new encryption key for development: {base64.urlsafe_b64encode(key).decode()}"
            )
            return key
        
        return None
    
    def _setup_defaults(self) -> None:
        """Setup default configurations"""        
        # PostgreSQL defaults
        self.global_config["postgresql"] = {
            "host": os.getenv("POSTGRES_HOST", "localhost"),
            "port": int(os.getenv("POSTGRES_PORT", "5432")),
            "database": os.getenv("POSTGRES_DB", "ia_influencer"),
            "username": os.getenv("POSTGRES_USER", "postgres"),
            "password": os.getenv("POSTGRES_PASSWORD", ""),
            "pool_size": int(os.getenv("POSTGRES_POOL_SIZE", "10")),
            "max_overflow": int(os.getenv("POSTGRES_MAX_OVERFLOW", "20"))
        }
        
        # Redis defaults
        self.global_config["redis"] = {
            "host": os.getenv("REDIS_HOST", "localhost"),
            "port": int(os.getenv("REDIS_PORT", "6379")),
            "db": int(os.getenv("REDIS_DB", "0")),
            "password": os.getenv("REDIS_PASSWORD"),
            "connection_pool_size": int(os.getenv("REDIS_POOL_SIZE", "50"))
        }
        
        # MongoDB defaults
        self.global_config["mongodb"] = {
            "host": os.getenv("MONGO_HOST", "localhost"),
            "port": int(os.getenv("MONGO_PORT", "27017")),
            "database": os.getenv("MONGO_DB", "ia_influencer"),
            "username": os.getenv("MONGO_USER"),
            "password": os.getenv("MONGO_PASSWORD")
        }
        
        # Elasticsearch defaults
        self.global_config["elasticsearch"] = {
            "hosts": [os.getenv("ELASTICSEARCH_HOST", "localhost:9200")],
            "username": os.getenv("ELASTICSEARCH_USER"),
            "password": os.getenv("ELASTICSEARCH_PASSWORD")
        }
        
        # Vector store defaults
        self.global_config["vector_store"] = {
            "provider": os.getenv("VECTOR_STORE_PROVIDER", "faiss"),
            "index_path": os.getenv("VECTOR_STORE_INDEX_PATH", "./data/vector_index"),
            "dimension": int(os.getenv("VECTOR_STORE_DIMENSION", "768"))
        }
        
        # Object storage defaults
        self.global_config["object_storage"] = {
            "provider": os.getenv("OBJECT_STORAGE_PROVIDER", "minio"),
            "endpoint_url": os.getenv("OBJECT_STORAGE_ENDPOINT", "http://localhost:9000"),
            "access_key_id": os.getenv("OBJECT_STORAGE_ACCESS_KEY", "minioadmin"),
            "secret_access_key": os.getenv("OBJECT_STORAGE_SECRET_KEY", "minioadmin"),
            "bucket_name": os.getenv("OBJECT_STORAGE_BUCKET", "ia-influencer")
        }
    
    async def initialize(self, config_dir: Optional[str] = None) -> None:
        """Initialize configuration manager"""        
        if config_dir:
            self.config_dir = Path(config_dir)
        
        # Load configurations from all sources
        await self._load_configurations()
        
        # Validate configurations
        await self._validate_configurations()
        
        # Setup monitoring
        await self._setup_monitoring()
        
        self.logger.info("Configuration manager initialized")
    
    async def _load_configurations(self) -> None:
        """Load configurations from all sources"""        
        for source in self.config_sources:
            try:
                if source == ConfigurationSource.FILE:
                    await self._load_from_files()
                elif source == ConfigurationSource.ENVIRONMENT:
                    await self._load_from_environment()
                elif source == ConfigurationSource.DATABASE:
                    await self._load_from_database()
                elif source == ConfigurationSource.VAULT:
                    await self._load_from_vault()
                    
            except Exception as e:
                self.logger.warning(f"Failed to load configuration from {source.value}: {e}")
    
    async def _load_from_files(self) -> None:
        """Load configuration from files"""        
        # Load global configuration
        global_config_path = self.config_dir / self.config_files["global"]
        if global_config_path.exists():
            with open(global_config_path, 'r') as f:
                file_config = yaml.safe_load(f)
                if file_config:
                    # Merge with existing config
                    self._deep_merge(self.global_config, file_config)
        
        # Load tenant configurations
        tenants_config_path = self.config_dir / self.config_files["tenants"]
        if tenants_config_path.exists():
            with open(tenants_config_path, 'r') as f:
                tenants_config = yaml.safe_load(f)
                if tenants_config and "tenants" in tenants_config:
                    for tenant_data in tenants_config["tenants"]:
                        tenant_config = TenantConfig(**tenant_data)
                        self.tenant_configs[tenant_config.tenant_id] = tenant_config
    
    async def _load_from_environment(self) -> None:
        """Load configuration from environment variables"""        # Environment variables are already loaded in _setup_defaults
        pass
    
    async def _load_from_database(self) -> None:
        """Load configuration from database (placeholder)"""        # This would load configuration from a configuration database
        pass
    
    async def _load_from_vault(self) -> None:
        """Load configuration from secure vault (placeholder)"""        # This would load sensitive configuration from a secure vault
        pass
    
    def _deep_merge(self, target: Dict[str, Any], source: Dict[str, Any]) -> None:
        """Deep merge two dictionaries"""        for key, value in source.items():
            if key in target and isinstance(target[key], dict) and isinstance(value, dict):
                self._deep_merge(target[key], value)
            else:
                target[key] = value
    
    async def _validate_configurations(self) -> None:
        """Validate all configurations"""        
        # Validate global configuration
        for db_type, config in self.global_config.items():
            if not self._validate_config(db_type, config):
                raise ValueError(f"Invalid configuration for {db_type}")
        
        # Validate tenant configurations
        for tenant_id, tenant_config in self.tenant_configs.items():
            if not self._validate_tenant_config(tenant_config):
                raise ValueError(f"Invalid configuration for tenant {tenant_id}")
    
    def _validate_config(self, db_type: str, config: Dict[str, Any]) -> bool:
        """Validate specific database configuration"""        
        try:
            if db_type == "postgresql":
                DatabaseConfig(**config)
            elif db_type == "redis":
                RedisConfig(**config)
            elif db_type == "mongodb":
                MongoConfig(**config)
            elif db_type == "elasticsearch":
                ElasticsearchConfig(**config)
            elif db_type == "vector_store":
                VectorStoreConfig(**config)
            elif db_type == "object_storage":
                ObjectStorageConfig(**config)
            
            return True
            
        except Exception as e:
            self.logger.error(f"Configuration validation failed for {db_type}: {e}")
            return False
    
    def _validate_tenant_config(self, tenant_config: TenantConfig) -> bool:
        """Validate tenant configuration"""        
        # Basic validation
        if not tenant_config.tenant_id or not tenant_config.name:
            return False
        
        # Validate tenant ID format
        if not re.match(r'^[a-zA-Z0-9_-]+$', tenant_config.tenant_id):
            return False
        
        # Validate limits
        if tenant_config.max_connections <= 0:
            return False
        
        return True
    
    async def _setup_monitoring(self) -> None:
        """Setup configuration monitoring"""        # This would setup file watchers for configuration changes
        pass
    
    def get_database_config(self, 
                           db_type: str, 
                           tenant_id: Optional[str] = None) -> Optional[Union[DatabaseConfig, RedisConfig, MongoConfig]]:
        """Get database configuration"""        
        # Check tenant-specific configuration first
        if tenant_id and tenant_id in self.tenant_configs:
            tenant_config = self.tenant_configs[tenant_id]
            
            if db_type == "postgresql" and tenant_config.database_config:
                return tenant_config.database_config
            elif db_type == "redis" and tenant_config.redis_config:
                return tenant_config.redis_config
            elif db_type == "mongodb" and tenant_config.mongo_config:
                return tenant_config.mongo_config
            elif db_type == "elasticsearch" and tenant_config.elasticsearch_config:
                return tenant_config.elasticsearch_config
        
        # Fallback to global configuration
        config_data = self.global_config.get(db_type)
        if not config_data:
            return None
        
        try:
            if db_type == "postgresql":
                return DatabaseConfig(**config_data)
            elif db_type == "redis":
                return RedisConfig(**config_data)
            elif db_type == "mongodb":
                return MongoConfig(**config_data)
            elif db_type == "elasticsearch":
                return ElasticsearchConfig(**config_data)
            elif db_type == "vector_store":
                return VectorStoreConfig(**config_data)
            elif db_type == "object_storage":
                return ObjectStorageConfig(**config_data)
        
        except Exception as e:
            self.logger.error(f"Failed to create configuration for {db_type}: {e}")
            return None
    
    def get_tenant_config(self, tenant_id: str) -> Optional[TenantConfig]:
        """Get tenant configuration"""        return self.tenant_configs.get(tenant_id)
    
    def list_tenants(self) -> List[str]:
        """List all configured tenants"""        return list(self.tenant_configs.keys())
    
    async def add_tenant(self, tenant_config: TenantConfig) -> bool:
        """Add new tenant configuration"""        
        try:
            # Validate configuration
            if not self._validate_tenant_config(tenant_config):
                return False
            
            # Check if tenant already exists
            if tenant_config.tenant_id in self.tenant_configs:
                raise ValueError(f"Tenant {tenant_config.tenant_id} already exists")
            
            # Add tenant
            self.tenant_configs[tenant_config.tenant_id] = tenant_config
            
            # Audit log
            self._log_config_change("add_tenant", tenant_config.tenant_id, asdict(tenant_config))
            
            # Notify callbacks
            await self._notify_config_change("tenant_added", tenant_config.tenant_id)
            
            self.logger.info(f"Added tenant configuration: {tenant_config.tenant_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to add tenant {tenant_config.tenant_id}: {e}")
            return False
    
    async def update_tenant(self, tenant_id: str, updates: Dict[str, Any]) -> bool:
        """Update tenant configuration"""        
        try:
            if tenant_id not in self.tenant_configs:
                return False
            
            tenant_config = self.tenant_configs[tenant_id]
            
            # Apply updates
            for key, value in updates.items():
                if hasattr(tenant_config, key):
                    setattr(tenant_config, key, value)
            
            tenant_config.updated_at = datetime.utcnow()
            
            # Validate updated configuration
            if not self._validate_tenant_config(tenant_config):
                return False
            
            # Audit log
            self._log_config_change("update_tenant", tenant_id, updates)
            
            # Notify callbacks
            await self._notify_config_change("tenant_updated", tenant_id)
            
            self.logger.info(f"Updated tenant configuration: {tenant_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to update tenant {tenant_id}: {e}")
            return False
    
    async def remove_tenant(self, tenant_id: str) -> bool:
        """Remove tenant configuration"""        
        try:
            if tenant_id not in self.tenant_configs:
                return False
            
            # Remove tenant
            del self.tenant_configs[tenant_id]
            
            # Audit log
            self._log_config_change("remove_tenant", tenant_id, None)
            
            # Notify callbacks
            await self._notify_config_change("tenant_removed", tenant_id)
            
            self.logger.info(f"Removed tenant configuration: {tenant_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to remove tenant {tenant_id}: {e}")
            return False
    
    def _log_config_change(self, action: str, target: str, data: Any) -> None:
        """Log configuration change for auditing"""        
        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "action": action,
            "target": target,
            "data": data,
            "environment": self.environment.value
        }
        
        self.audit_log.append(log_entry)
        
        # Keep only last 1000 entries
        if len(self.audit_log) > 1000:
            self.audit_log = self.audit_log[-1000:]
    
    async def _notify_config_change(self, change_type: str, target: str) -> None:
        """Notify configuration change callbacks"""        
        for callback in self.config_change_callbacks:
            try:
                await callback(change_type, target)
            except Exception as e:
                self.logger.error(f"Configuration change callback error: {e}")
    
    def register_change_callback(self, callback: callable) -> None:
        """Register callback for configuration changes"""        self.config_change_callbacks.append(callback)
    
    def encrypt_sensitive_data(self, data: str) -> Optional[str]:
        """Encrypt sensitive configuration data"""        if not self.cipher_suite:
            return data
        
        try:
            encrypted = self.cipher_suite.encrypt(data.encode())
            return base64.urlsafe_b64encode(encrypted).decode()
        except Exception as e:
            self.logger.error(f"Failed to encrypt data: {e}")
            return None
    
    def decrypt_sensitive_data(self, encrypted_data: str) -> Optional[str]:
        """Decrypt sensitive configuration data"""        if not self.cipher_suite:
            return encrypted_data
        
        try:
            encrypted_bytes = base64.urlsafe_b64decode(encrypted_data.encode())
            decrypted = self.cipher_suite.decrypt(encrypted_bytes)
            return decrypted.decode()
        except Exception as e:
            self.logger.error(f"Failed to decrypt data: {e}")
            return None
    
    async def save_configuration(self) -> bool:
        """Save current configuration to files"""        
        try:
            # Ensure config directory exists
            self.config_dir.mkdir(parents=True, exist_ok=True)
            
            # Save global configuration
            global_config_path = self.config_dir / self.config_files["global"]
            with open(global_config_path, 'w') as f:
                yaml.dump(self.global_config, f, default_flow_style=False)
            
            # Save tenant configurations
            tenants_config_path = self.config_dir / self.config_files["tenants"]
            tenants_data = {
                "tenants": [asdict(config) for config in self.tenant_configs.values()]
            }
            with open(tenants_config_path, 'w') as f:
                yaml.dump(tenants_data, f, default_flow_style=False)
            
            self.logger.info("Configuration saved successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to save configuration: {e}")
            return False
    
    async def get_metrics(self) -> Dict[str, Any]:
        """Get configuration manager metrics"""        
        return {
            "environment": self.environment.value,
            "total_tenants": len(self.tenant_configs),
            "total_config_changes": len(self.audit_log),
            "config_sources": [source.value for source in self.config_sources],
            "encryption_enabled": self.cipher_suite is not None,
            "tenants": {
                tenant_id: {
                    "name": config.name,
                    "created_at": config.created_at.isoformat(),
                    "updated_at": config.updated_at.isoformat(),
                    "max_connections": config.max_connections,
                    "features_enabled": config.features_enabled
                }
                for tenant_id, config in self.tenant_configs.items()
            },
            "recent_changes": self.audit_log[-10:] if self.audit_log else []
        }
    
    async def shutdown(self) -> None:
        """Shutdown configuration manager"""        self.logger.info("Shutting down configuration manager...")
        
        # Save current configuration
        await self.save_configuration()
        
        # Clear data structures
        self.global_config.clear()
        self.tenant_configs.clear()
        self.config_change_callbacks.clear()
        self.audit_log.clear()
        
        self.logger.info("Configuration manager shutdown completed")
