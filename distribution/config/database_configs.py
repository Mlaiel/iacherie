"""
Database Configuration for Ainflue Distribution Platform

This module provides comprehensive database configuration and optimization
settings for the distribution platform's data layer.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import os
import asyncio
import logging
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class DatabaseType(Enum):
    """Supported database types"""
    POSTGRESQL = "postgresql"
    MYSQL = "mysql"
    MONGODB = "mongodb"
    REDIS = "redis"
    INFLUXDB = "influxdb"
    ELASTICSEARCH = "elasticsearch"
    CLICKHOUSE = "clickhouse"


class ConnectionPoolType(Enum):
    """Connection pool implementations"""
    ASYNCPG = "asyncpg"
    AIOPG = "aiopg"
    AIOMYSQL = "aiomysql"
    MOTOR = "motor"
    AIOREDIS = "aioredis"


class IsolationLevel(Enum):
    """Transaction isolation levels"""
    READ_UNCOMMITTED = "read_uncommitted"
    READ_COMMITTED = "read_committed"
    REPEATABLE_READ = "repeatable_read"
    SERIALIZABLE = "serializable"


@dataclass
class ConnectionPool:
    """Connection pool configuration"""
    pool_type: ConnectionPoolType
    min_connections: int = 5
    max_connections: int = 50
    max_inactive_connection_lifetime: int = 300  # seconds
    max_queries: int = 50000
    max_cached_statement_lifetime: int = 300
    max_cacheable_statement_size: int = 1024
    command_timeout: int = 60
    server_settings: Dict[str, str] = field(default_factory=dict)


@dataclass
class QueryOptimization:
    """Query optimization settings"""
    enable_query_cache: bool = True
    query_cache_size_mb: int = 256
    enable_prepared_statements: bool = True
    max_prepared_statements: int = 1000
    enable_statement_logging: bool = False
    slow_query_threshold_ms: int = 1000
    explain_analyze_threshold_ms: int = 5000
    enable_auto_vacuum: bool = True
    auto_vacuum_threshold: float = 0.2
    enable_query_planner_stats: bool = True


@dataclass
class BackupSettings:
    """Database backup configuration"""
    enable_automated_backups: bool = True
    backup_interval_hours: int = 6
    backup_retention_days: int = 30
    backup_compression: bool = True
    backup_encryption: bool = True
    backup_storage_path: str = "/backups/distribution"
    point_in_time_recovery: bool = True
    replica_backup_enabled: bool = True
    backup_verification: bool = True


@dataclass
class ReplicationConfig:
    """Database replication settings"""
    enable_replication: bool = True
    master_host: str = "localhost"
    replica_hosts: List[str] = field(default_factory=list)
    replication_mode: str = "async"  # async, sync, or semi_sync
    read_preference: str = "primary_preferred"  # primary, secondary, nearest
    replica_lag_threshold_ms: int = 1000
    auto_failover: bool = True
    failover_timeout_seconds: int = 30


@dataclass
class ShardingConfig:
    """Database sharding configuration"""
    enable_sharding: bool = False
    shard_key: str = "user_id"
    shard_count: int = 4
    shard_hosts: List[str] = field(default_factory=list)
    consistent_hashing: bool = True
    auto_rebalancing: bool = True
    shard_migration_batch_size: int = 1000


@dataclass
class CachingConfig:
    """Database caching configuration"""
    enable_query_cache: bool = True
    enable_result_cache: bool = True
    enable_connection_cache: bool = True
    cache_ttl_seconds: int = 300
    max_cache_size_mb: int = 512
    cache_eviction_policy: str = "lru"  # lru, lfu, ttl
    cache_compression: bool = True
    cache_serialization: str = "pickle"  # pickle, json, msgpack


class DatabaseConfiguration:
    """
    Comprehensive database configuration manager for distribution platform
    
    Features:
    - Multi-database support (PostgreSQL, MongoDB, Redis, etc.)
    - Connection pooling optimization
    - Query performance tuning
    - Automated backup management
    - Replication and sharding support
    - Comprehensive monitoring and alerting
    """

    def __init__(self, config_file -> None: Optional[str] = None) -> None:
        self.config_file = config_file
        self.databases = {}
        self.connection_pools = {}
        self.query_optimizations = {}
        self.backup_settings = {}
        self.replication_configs = {}
        self.sharding_configs = {}
        self.caching_configs = {}
        
        # Load configuration
        self._load_configuration()

    def _load_configuration(self) -> None:
        """Load database configuration from environment and config files"""
        
        # Primary PostgreSQL database for core data
        self.databases['primary'] = {
            'type': DatabaseType.POSTGRESQL,
            'host': os.getenv('DB_HOST', 'localhost'),
            'port': int(os.getenv('DB_PORT', '5432')),
            'database': os.getenv('DB_NAME', 'ainflue_distribution'),
            'username': os.getenv('DB_USER', 'ainflue'),
            'password': os.getenv('DB_PASSWORD', ''),
            'ssl_mode': os.getenv('DB_SSL_MODE', 'prefer'),
            'ssl_cert': os.getenv('DB_SSL_CERT', ''),
            'ssl_key': os.getenv('DB_SSL_KEY', ''),
            'ssl_ca': os.getenv('DB_SSL_CA', ''),
            'charset': 'utf8mb4',
            'timezone': 'UTC'
        }
        
        # MongoDB for analytics and flexible data
        self.databases['analytics'] = {
            'type': DatabaseType.MONGODB,
            'host': os.getenv('MONGO_HOST', 'localhost'),
            'port': int(os.getenv('MONGO_PORT', '27017')),
            'database': os.getenv('MONGO_DB', 'ainflue_analytics'),
            'username': os.getenv('MONGO_USER', ''),
            'password': os.getenv('MONGO_PASSWORD', ''),
            'auth_source': os.getenv('MONGO_AUTH_SOURCE', 'admin'),
            'replica_set': os.getenv('MONGO_REPLICA_SET', ''),
            'ssl': os.getenv('MONGO_SSL', 'false').lower() == 'true'
        }
        
        # Redis for caching and session management
        self.databases['cache'] = {
            'type': DatabaseType.REDIS,
            'host': os.getenv('REDIS_HOST', 'localhost'),
            'port': int(os.getenv('REDIS_PORT', '6379')),
            'database': int(os.getenv('REDIS_DB', '0')),
            'password': os.getenv('REDIS_PASSWORD', ''),
            'ssl': os.getenv('REDIS_SSL', 'false').lower() == 'true',
            'max_connections': int(os.getenv('REDIS_MAX_CONNECTIONS', '50'))
        }
        
        # InfluxDB for time-series metrics
        self.databases['metrics'] = {
            'type': DatabaseType.INFLUXDB,
            'host': os.getenv('INFLUX_HOST', 'localhost'),
            'port': int(os.getenv('INFLUX_PORT', '8086')),
            'database': os.getenv('INFLUX_DB', 'ainflue_metrics'),
            'username': os.getenv('INFLUX_USER', ''),
            'password': os.getenv('INFLUX_PASSWORD', ''),
            'ssl': os.getenv('INFLUX_SSL', 'false').lower() == 'true',
            'retention_policy': os.getenv('INFLUX_RETENTION', '30d')
        }
        
        # Elasticsearch for search and logging
        self.databases['search'] = {
            'type': DatabaseType.ELASTICSEARCH,
            'host': os.getenv('ES_HOST', 'localhost'),
            'port': int(os.getenv('ES_PORT', '9200')),
            'username': os.getenv('ES_USER', ''),
            'password': os.getenv('ES_PASSWORD', ''),
            'ssl': os.getenv('ES_SSL', 'false').lower() == 'true',
            'index_prefix': os.getenv('ES_INDEX_PREFIX', 'ainflue'),
            'number_of_shards': int(os.getenv('ES_SHARDS', '3')),
            'number_of_replicas': int(os.getenv('ES_REPLICAS', '1'))
        }
        
        # Initialize configurations for each database
        self._initialize_connection_pools()
        self._initialize_query_optimizations()
        self._initialize_backup_settings()
        self._initialize_replication_configs()
        self._initialize_sharding_configs()
        self._initialize_caching_configs()

    def _initialize_connection_pools(self) -> None:
        """Initialize connection pool configurations"""
        
        # PostgreSQL connection pool
        self.connection_pools['primary'] = ConnectionPool(
            pool_type=ConnectionPoolType.ASYNCPG,
            min_connections=int(os.getenv('DB_POOL_MIN', '5')),
            max_connections=int(os.getenv('DB_POOL_MAX', '50')),
            max_inactive_connection_lifetime=int(os.getenv('DB_POOL_LIFETIME', '300')),
            max_queries=int(os.getenv('DB_POOL_MAX_QUERIES', '50000')),
            command_timeout=int(os.getenv('DB_COMMAND_TIMEOUT', '60')),
            server_settings={
                'application_name': 'ainflue_distribution',
                'tcp_keepalives_idle': '600',
                'tcp_keepalives_interval': '30',
                'tcp_keepalives_count': '3'
            }
        )
        
        # MongoDB connection pool
        self.connection_pools['analytics'] = ConnectionPool(
            pool_type=ConnectionPoolType.MOTOR,
            min_connections=int(os.getenv('MONGO_POOL_MIN', '3')),
            max_connections=int(os.getenv('MONGO_POOL_MAX', '30')),
            max_inactive_connection_lifetime=int(os.getenv('MONGO_POOL_LIFETIME', '300')),
            command_timeout=int(os.getenv('MONGO_COMMAND_TIMEOUT', '30'))
        )
        
        # Redis connection pool
        self.connection_pools['cache'] = ConnectionPool(
            pool_type=ConnectionPoolType.AIOREDIS,
            min_connections=int(os.getenv('REDIS_POOL_MIN', '2')),
            max_connections=int(os.getenv('REDIS_POOL_MAX', '20')),
            max_inactive_connection_lifetime=int(os.getenv('REDIS_POOL_LIFETIME', '300')),
            command_timeout=int(os.getenv('REDIS_COMMAND_TIMEOUT', '5'))
        )

    def _initialize_query_optimizations(self) -> None:
        """Initialize query optimization settings"""
        
        # PostgreSQL optimizations
        self.query_optimizations['primary'] = QueryOptimization(
            enable_query_cache=os.getenv('DB_QUERY_CACHE', 'true').lower() == 'true',
            query_cache_size_mb=int(os.getenv('DB_QUERY_CACHE_SIZE', '256')),
            enable_prepared_statements=os.getenv('DB_PREPARED_STATEMENTS', 'true').lower() == 'true',
            max_prepared_statements=int(os.getenv('DB_MAX_PREPARED', '1000')),
            enable_statement_logging=os.getenv('DB_STATEMENT_LOGGING', 'false').lower() == 'true',
            slow_query_threshold_ms=int(os.getenv('DB_SLOW_QUERY_THRESHOLD', '1000')),
            explain_analyze_threshold_ms=int(os.getenv('DB_EXPLAIN_THRESHOLD', '5000')),
            enable_auto_vacuum=os.getenv('DB_AUTO_VACUUM', 'true').lower() == 'true',
            auto_vacuum_threshold=float(os.getenv('DB_VACUUM_THRESHOLD', '0.2'))
        )
        
        # MongoDB optimizations
        self.query_optimizations['analytics'] = QueryOptimization(
            enable_query_cache=True,
            query_cache_size_mb=128,
            enable_prepared_statements=False,  # Not applicable for MongoDB
            slow_query_threshold_ms=2000,
            enable_auto_vacuum=False  # MongoDB handles this differently
        )

    def _initialize_backup_settings(self) -> None:
        """Initialize backup configurations"""
        
        # PostgreSQL backups
        self.backup_settings['primary'] = BackupSettings(
            enable_automated_backups=os.getenv('DB_BACKUP_ENABLED', 'true').lower() == 'true',
            backup_interval_hours=int(os.getenv('DB_BACKUP_INTERVAL', '6')),
            backup_retention_days=int(os.getenv('DB_BACKUP_RETENTION', '30')),
            backup_compression=os.getenv('DB_BACKUP_COMPRESSION', 'true').lower() == 'true',
            backup_encryption=os.getenv('DB_BACKUP_ENCRYPTION', 'true').lower() == 'true',
            backup_storage_path=os.getenv('DB_BACKUP_PATH', '/backups/postgresql'),
            point_in_time_recovery=os.getenv('DB_PITR', 'true').lower() == 'true',
            replica_backup_enabled=os.getenv('DB_REPLICA_BACKUP', 'true').lower() == 'true',
            backup_verification=os.getenv('DB_BACKUP_VERIFICATION', 'true').lower() == 'true'
        )
        
        # MongoDB backups
        self.backup_settings['analytics'] = BackupSettings(
            enable_automated_backups=os.getenv('MONGO_BACKUP_ENABLED', 'true').lower() == 'true',
            backup_interval_hours=int(os.getenv('MONGO_BACKUP_INTERVAL', '12')),
            backup_retention_days=int(os.getenv('MONGO_BACKUP_RETENTION', '14')),
            backup_compression=True,
            backup_encryption=True,
            backup_storage_path=os.getenv('MONGO_BACKUP_PATH', '/backups/mongodb'),
            point_in_time_recovery=False,  # Requires MongoDB Atlas or Ops Manager
            replica_backup_enabled=True,
            backup_verification=True
        )

    def _initialize_replication_configs(self) -> None:
        """Initialize replication configurations"""
        
        # PostgreSQL replication
        self.replication_configs['primary'] = ReplicationConfig(
            enable_replication=os.getenv('DB_REPLICATION_ENABLED', 'true').lower() == 'true',
            master_host=os.getenv('DB_MASTER_HOST', self.databases['primary']['host']),
            replica_hosts=os.getenv('DB_REPLICA_HOSTS', '').split(',') if os.getenv('DB_REPLICA_HOSTS') else [],
            replication_mode=os.getenv('DB_REPLICATION_MODE', 'async'),
            read_preference=os.getenv('DB_READ_PREFERENCE', 'primary_preferred'),
            replica_lag_threshold_ms=int(os.getenv('DB_REPLICA_LAG_THRESHOLD', '1000')),
            auto_failover=os.getenv('DB_AUTO_FAILOVER', 'true').lower() == 'true',
            failover_timeout_seconds=int(os.getenv('DB_FAILOVER_TIMEOUT', '30'))
        )
        
        # MongoDB replication
        self.replication_configs['analytics'] = ReplicationConfig(
            enable_replication=True,
            replica_hosts=os.getenv('MONGO_REPLICA_HOSTS', '').split(',') if os.getenv('MONGO_REPLICA_HOSTS') else [],
            read_preference=os.getenv('MONGO_READ_PREFERENCE', 'secondaryPreferred'),
            auto_failover=True
        )

    def _initialize_sharding_configs(self) -> None:
        """Initialize sharding configurations"""
        
        # PostgreSQL sharding (manual)
        self.sharding_configs['primary'] = ShardingConfig(
            enable_sharding=os.getenv('DB_SHARDING_ENABLED', 'false').lower() == 'true',
            shard_key=os.getenv('DB_SHARD_KEY', 'user_id'),
            shard_count=int(os.getenv('DB_SHARD_COUNT', '4')),
            shard_hosts=os.getenv('DB_SHARD_HOSTS', '').split(',') if os.getenv('DB_SHARD_HOSTS') else [],
            consistent_hashing=True,
            auto_rebalancing=False,  # Manual for PostgreSQL
            shard_migration_batch_size=int(os.getenv('DB_SHARD_BATCH_SIZE', '1000'))
        )
        
        # MongoDB sharding
        self.sharding_configs['analytics'] = ShardingConfig(
            enable_sharding=os.getenv('MONGO_SHARDING_ENABLED', 'false').lower() == 'true',
            shard_key=os.getenv('MONGO_SHARD_KEY', 'user_id'),
            shard_count=int(os.getenv('MONGO_SHARD_COUNT', '2')),
            consistent_hashing=True,
            auto_rebalancing=True  # MongoDB supports auto-balancing
        )

    def _initialize_caching_configs(self) -> None:
        """Initialize caching configurations"""
        
        # Application-level caching
        self.caching_configs['application'] = CachingConfig(
            enable_query_cache=os.getenv('APP_QUERY_CACHE', 'true').lower() == 'true',
            enable_result_cache=os.getenv('APP_RESULT_CACHE', 'true').lower() == 'true',
            enable_connection_cache=os.getenv('APP_CONNECTION_CACHE', 'true').lower() == 'true',
            cache_ttl_seconds=int(os.getenv('APP_CACHE_TTL', '300')),
            max_cache_size_mb=int(os.getenv('APP_CACHE_SIZE', '512')),
            cache_eviction_policy=os.getenv('APP_CACHE_EVICTION', 'lru'),
            cache_compression=os.getenv('APP_CACHE_COMPRESSION', 'true').lower() == 'true',
            cache_serialization=os.getenv('APP_CACHE_SERIALIZATION', 'pickle')
        )
        
        # Redis caching
        self.caching_configs['redis'] = CachingConfig(
            enable_query_cache=True,
            enable_result_cache=True,
            cache_ttl_seconds=int(os.getenv('REDIS_CACHE_TTL', '600')),
            max_cache_size_mb=int(os.getenv('REDIS_CACHE_SIZE', '1024')),
            cache_eviction_policy='allkeys-lru',
            cache_compression=True
        )

    def get_database_url(self, database_name: str) -> str:
        """Get database connection URL"""
        
        if database_name not in self.databases:
            raise ValueError(f"Database '{database_name}' not configured")
        
        db_config = self.databases[database_name]
        db_type = db_config['type']
        
        if db_type == DatabaseType.POSTGRESQL:
            url = f"postgresql://{db_config['username']}:{db_config['password']}@{db_config['host']}:{db_config['port']}/{db_config['database']}"
            if db_config.get('ssl_mode') and db_config['ssl_mode'] != 'disable':
                url += f"?sslmode={db_config['ssl_mode']}"
        
        elif db_type == DatabaseType.MYSQL:
            url = f"mysql://{db_config['username']}:{db_config['password']}@{db_config['host']}:{db_config['port']}/{db_config['database']}"
        
        elif db_type == DatabaseType.MONGODB:
            if db_config.get('username') and db_config.get('password'):
                url = f"mongodb://{db_config['username']}:{db_config['password']}@{db_config['host']}:{db_config['port']}/{db_config['database']}"
            else:
                url = f"mongodb://{db_config['host']}:{db_config['port']}/{db_config['database']}"
            
            # Add replica set if configured
            if db_config.get('replica_set'):
                url += f"?replicaSet={db_config['replica_set']}"
        
        elif db_type == DatabaseType.REDIS:
            url = f"redis://:{db_config['password']}@{db_config['host']}:{db_config['port']}/{db_config['database']}" if db_config.get('password') else f"redis://{db_config['host']}:{db_config['port']}/{db_config['database']}"
        
        elif db_type == DatabaseType.INFLUXDB:
            url = f"influxdb://{db_config['username']}:{db_config['password']}@{db_config['host']}:{db_config['port']}/{db_config['database']}"
        
        elif db_type == DatabaseType.ELASTICSEARCH:
            url = f"elasticsearch://{db_config['username']}:{db_config['password']}@{db_config['host']}:{db_config['port']}" if db_config.get('username') else f"elasticsearch://{db_config['host']}:{db_config['port']}"
        
        else:
            raise ValueError(f"Unsupported database type: {db_type}")
        
        return url

    def get_connection_pool_config(self, database_name: str) -> ConnectionPool:
        """Get connection pool configuration for database"""
        
        return self.connection_pools.get(database_name, ConnectionPool(ConnectionPoolType.ASYNCPG))

    def get_query_optimization_config(self, database_name: str) -> QueryOptimization:
        """Get query optimization configuration for database"""
        
        return self.query_optimizations.get(database_name, QueryOptimization())

    def get_backup_settings(self, database_name: str) -> BackupSettings:
        """Get backup settings for database"""
        
        return self.backup_settings.get(database_name, BackupSettings())

    def get_replication_config(self, database_name: str) -> ReplicationConfig:
        """Get replication configuration for database"""
        
        return self.replication_configs.get(database_name, ReplicationConfig())

    def get_sharding_config(self, database_name: str) -> ShardingConfig:
        """Get sharding configuration for database"""
        
        return self.sharding_configs.get(database_name, ShardingConfig())

    def get_caching_config(self, cache_name: str) -> CachingConfig:
        """Get caching configuration"""
        
        return self.caching_configs.get(cache_name, CachingConfig())

    def validate_configuration(self) -> Dict[str, List[str]]:
        """Validate all database configurations"""
        
        validation_errors = {}
        
        for db_name, db_config in self.databases.items():
            errors = []
            
            # Check required fields
            required_fields = ['type', 'host', 'port']
            for field in required_fields:
                if field not in db_config or not db_config[field]:
                    errors.append(f"Missing required field: {field}")
            
            # Database-specific validations
            db_type = db_config.get('type')
            
            if db_type in [DatabaseType.POSTGRESQL, DatabaseType.MYSQL]:
                if not db_config.get('database'):
                    errors.append("Database name is required")
                if not db_config.get('username'):
                    errors.append("Username is required")
            
            elif db_type == DatabaseType.MONGODB:
                if not db_config.get('database'):
                    errors.append("Database name is required")
            
            # Validate connection pool settings
            pool_config = self.connection_pools.get(db_name)
            if pool_config:
                if pool_config.min_connections > pool_config.max_connections:
                    errors.append("min_connections cannot be greater than max_connections")
                if pool_config.max_connections > 200:
                    errors.append("max_connections should not exceed 200 for optimal performance")
            
            if errors:
                validation_errors[db_name] = errors
        
        return validation_errors

    def generate_database_scripts(self, database_name: str) -> Dict[str, str]:
        """Generate database-specific setup and optimization scripts"""
        
        if database_name not in self.databases:
            raise ValueError(f"Database '{database_name}' not configured")
        
        db_config = self.databases[database_name]
        db_type = db_config['type']
        scripts = {}
        
        if db_type == DatabaseType.POSTGRESQL:
            scripts['setup'] = self._generate_postgresql_setup_script(database_name)
            scripts['indexes'] = self._generate_postgresql_index_script(database_name)
            scripts['maintenance'] = self._generate_postgresql_maintenance_script(database_name)
        
        elif db_type == DatabaseType.MONGODB:
            scripts['setup'] = self._generate_mongodb_setup_script(database_name)
            scripts['indexes'] = self._generate_mongodb_index_script(database_name)
            scripts['sharding'] = self._generate_mongodb_sharding_script(database_name)
        
        return scripts

    def _generate_postgresql_setup_script(self, database_name: str) -> str:
        """Generate PostgreSQL setup script"""
        
        db_config = self.databases[database_name]
        
        script = f"""
-- PostgreSQL Setup Script for {database_name}
-- Generated on {datetime.utcnow().isoformat()}

-- Create database
CREATE DATABASE {db_config['database']} 
    WITH ENCODING 'UTF8' 
    LC_COLLATE='en_US.UTF-8' 
    LC_CTYPE='en_US.UTF-8' 
    TEMPLATE=template0;

-- Connect to database
\\c {db_config['database']};

-- Create extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_stat_statements";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";
CREATE EXTENSION IF NOT EXISTS "btree_gin";

-- Configure performance settings
ALTER SYSTEM SET shared_preload_libraries = 'pg_stat_statements';
ALTER SYSTEM SET max_connections = '{self.connection_pools[database_name].max_connections}';
ALTER SYSTEM SET shared_buffers = '256MB';
ALTER SYSTEM SET effective_cache_size = '1GB';
ALTER SYSTEM SET maintenance_work_mem = '64MB';
ALTER SYSTEM SET checkpoint_completion_target = 0.9;
ALTER SYSTEM SET wal_buffers = '16MB';
ALTER SYSTEM SET default_statistics_target = 100;

-- Create core tables for distribution platform
CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    username VARCHAR(255) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS content (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id),
    title TEXT NOT NULL,
    content_type VARCHAR(50) NOT NULL,
    platform VARCHAR(50) NOT NULL,
    status VARCHAR(50) DEFAULT 'draft',
    metadata JSONB DEFAULT '{{}}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS analytics_events (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    content_id UUID REFERENCES content(id),
    event_type VARCHAR(100) NOT NULL,
    event_data JSONB DEFAULT '{{}}',
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    platform VARCHAR(50),
    user_id UUID REFERENCES users(id)
);

-- Create indexes
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_username ON users(username);
CREATE INDEX idx_content_user_id ON content(user_id);
CREATE INDEX idx_content_platform ON content(platform);
CREATE INDEX idx_content_status ON content(status);
CREATE INDEX idx_content_created_at ON content(created_at);
CREATE INDEX idx_analytics_content_id ON analytics_events(content_id);
CREATE INDEX idx_analytics_timestamp ON analytics_events(timestamp);
CREATE INDEX idx_analytics_event_type ON analytics_events(event_type);

-- Create GIN indexes for JSONB
CREATE INDEX idx_content_metadata_gin ON content USING gin(metadata);
CREATE INDEX idx_analytics_event_data_gin ON analytics_events USING gin(event_data);

-- Create triggers for updated_at
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_content_updated_at BEFORE UPDATE ON content 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
"""
        
        return script

    def _generate_postgresql_index_script(self, database_name: str) -> str:
        """Generate PostgreSQL index optimization script"""
        
        script = f"""
-- PostgreSQL Index Optimization Script for {database_name}
-- Performance-focused indexes for distribution platform

-- Composite indexes for common queries
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_content_user_platform_status 
    ON content(user_id, platform, status);

CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_analytics_content_timestamp 
    ON analytics_events(content_id, timestamp DESC);

CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_analytics_platform_timestamp 
    ON analytics_events(platform, timestamp DESC);

-- Partial indexes for active content
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_content_active 
    ON content(created_at DESC) WHERE status = 'published';

-- Text search indexes
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_content_title_search 
    ON content USING gin(to_tsvector('english', title));

-- Analyze tables after index creation
ANALYZE users;
ANALYZE content;
ANALYZE analytics_events;
"""
        
        return script

    def _generate_postgresql_maintenance_script(self, database_name: str) -> str:
        """Generate PostgreSQL maintenance script"""
        
        script = f"""
-- PostgreSQL Maintenance Script for {database_name}
-- Regular maintenance tasks for optimal performance

-- Update table statistics
ANALYZE;

-- Vacuum tables
VACUUM (ANALYZE, VERBOSE) users;
VACUUM (ANALYZE, VERBOSE) content;
VACUUM (ANALYZE, VERBOSE) analytics_events;

-- Reindex if needed
REINDEX INDEX CONCURRENTLY idx_content_metadata_gin;
REINDEX INDEX CONCURRENTLY idx_analytics_event_data_gin;

-- Check and fix any corrupted indexes
SELECT schemaname, tablename, indexname, idx_tup_read, idx_tup_fetch 
FROM pg_stat_user_indexes 
WHERE idx_tup_read > 0 
ORDER BY idx_tup_read DESC;

-- Clean up old analytics data (older than 90 days)
DELETE FROM analytics_events 
WHERE timestamp < NOW() - INTERVAL '90 days';

-- Update query planner statistics
SELECT pg_stat_reset();
"""
        
        return script

    def _generate_mongodb_setup_script(self, database_name: str) -> str:
        """Generate MongoDB setup script"""
        
        db_config = self.databases[database_name]
        
        script = f"""
// MongoDB Setup Script for {database_name}
// Generated on {datetime.utcnow().isoformat()}

use {db_config['database']};

// Create collections with validation
db.createCollection("users", {{
    validator: {{
        $jsonSchema: {{
            bsonType: "object",
            required: ["username", "email", "createdAt"],
            properties: {{
                username: {{
                    bsonType: "string",
                    description: "Username must be a string and is required"
                }},
                email: {{
                    bsonType: "string",
                    pattern: "^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{{2,}}$",
                    description: "Email must be a valid email address"
                }},
                createdAt: {{
                    bsonType: "date",
                    description: "Creation timestamp is required"
                }}
            }}
        }}
    }}
}});

db.createCollection("content", {{
    validator: {{
        $jsonSchema: {{
            bsonType: "object",
            required: ["userId", "title", "contentType", "platform"],
            properties: {{
                userId: {{
                    bsonType: "objectId",
                    description: "User ID must be an ObjectId"
                }},
                title: {{
                    bsonType: "string",
                    description: "Title is required"
                }},
                contentType: {{
                    bsonType: "string",
                    enum: ["video", "image", "text", "audio"],
                    description: "Content type must be one of the allowed values"
                }},
                platform: {{
                    bsonType: "string",
                    description: "Platform is required"
                }}
            }}
        }}
    }}
}});

db.createCollection("analytics", {{
    validator: {{
        $jsonSchema: {{
            bsonType: "object",
            required: ["contentId", "eventType", "timestamp"],
            properties: {{
                contentId: {{
                    bsonType: "objectId",
                    description: "Content ID must be an ObjectId"
                }},
                eventType: {{
                    bsonType: "string",
                    description: "Event type is required"
                }},
                timestamp: {{
                    bsonType: "date",
                    description: "Timestamp is required"
                }}
            }}
        }}
    }}
}});

// Create TTL index for analytics (30 days retention)
db.analytics.createIndex(
    {{ "timestamp": 1 }}, 
    {{ expireAfterSeconds: 2592000 }}
);
"""
        
        return script

    def _generate_mongodb_index_script(self, database_name: str) -> str:
        """Generate MongoDB index script"""
        
        script = f"""
// MongoDB Index Script for {database_name}
// Performance optimization indexes

use {db_config['database']};

// Users collection indexes
db.users.createIndex({{ "email": 1 }}, {{ unique: true }});
db.users.createIndex({{ "username": 1 }}, {{ unique: true }});
db.users.createIndex({{ "createdAt": -1 }});

// Content collection indexes
db.content.createIndex({{ "userId": 1, "platform": 1 }});
db.content.createIndex({{ "platform": 1, "status": 1 }});
db.content.createIndex({{ "createdAt": -1 }});
db.content.createIndex({{ "title": "text", "description": "text" }});

// Analytics collection indexes
db.analytics.createIndex({{ "contentId": 1, "timestamp": -1 }});
db.analytics.createIndex({{ "eventType": 1, "timestamp": -1 }});
db.analytics.createIndex({{ "platform": 1, "timestamp": -1 }});

// Compound indexes for common queries
db.content.createIndex({{ 
    "userId": 1, 
    "platform": 1, 
    "status": 1, 
    "createdAt": -1 
}});
"""
        
        return script

    def _generate_mongodb_sharding_script(self, database_name: str) -> str:
        """Generate MongoDB sharding script"""
        
        sharding_config = self.sharding_configs.get(database_name)
        if not sharding_config or not sharding_config.enable_sharding:
            return "// Sharding not enabled for this database"
        
        script = f"""
// MongoDB Sharding Script for {database_name}
// Shard key: {sharding_config.shard_key}

// Enable sharding for database
sh.enableSharding("{self.databases[database_name]['database']}");

// Shard collections
sh.shardCollection(
    "{self.databases[database_name]['database']}.content", 
    {{ "{sharding_config.shard_key}": 1 }}
);

sh.shardCollection(
    "{self.databases[database_name]['database']}.analytics", 
    {{ "{sharding_config.shard_key}": 1, "timestamp": 1 }}
);

// Configure balancer
sh.setBalancerState(true);
"""
        
        return script

    def export_configuration(self) -> Dict[str, Any]:
        """Export complete database configuration"""
        
        config_export = {
            'databases': self.databases,
            'connection_pools': {k: v.__dict__ for k, v in self.connection_pools.items()},
            'query_optimizations': {k: v.__dict__ for k, v in self.query_optimizations.items()},
            'backup_settings': {k: v.__dict__ for k, v in self.backup_settings.items()},
            'replication_configs': {k: v.__dict__ for k, v in self.replication_configs.items()},
            'sharding_configs': {k: v.__dict__ for k, v in self.sharding_configs.items()},
            'caching_configs': {k: v.__dict__ for k, v in self.caching_configs.items()},
            'exported_at': datetime.utcnow().isoformat()
        }
        
        return config_export