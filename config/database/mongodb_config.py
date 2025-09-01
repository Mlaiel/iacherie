"""MongoDB Configuration Module for IA-Influencer Agent Platform
============================================================

Professional MongoDB database configuration for content fingerprinting,
media storage, and real-time analytics in multi-tenant environment.

Author: Fahed Mlaiel <mlaiel@live.de>
Project: IA-Influencer Agent + Content Protection Platform
Team: Lead Dev IA + Backend Senior + ML Engineer + DBA + Security + Microservices + Audio + DevOps

Copyright Notice:
This code is the intellectual property of Fahed Mlaiel. 
Any unauthorized use, reproduction, or distribution of this code 
without explicit written permission from the author is strictly prohibited.

Contact: mlaiel@live.de for licensing inquiries.
"""

import os
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, field
from enum import Enum
import pymongo
from pymongo import MongoClient, WriteConcern, ReadPreference
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError
from motor.motor_asyncio import AsyncIOMotorClient
import ssl
import logging
from urllib.parse import quote_plus

logger = logging.getLogger(__name__)


class MongoDBEnvironment(Enum):
    """
MongoDB environment configurations"""

    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"
    TESTING = "testing"


class MongoDBClusterType(Enum):
    """MongoDB cluster deployment types"""

    STANDALONE = "standalone"
    REPLICA_SET = "replica_set"
    SHARDED = "sharded"


class MongoDBWorkloadType(Enum):
    """MongoDB workload optimization types"""

    MEDIA_STORAGE = "media_storage"
    ANALYTICS = "analytics" 
    REAL_TIME = "real_time"
    CONTENT_PROTECTION = "content_protection"
    MONETIZATION = "monetization"


@dataclass
class MongoDBCredentials:
    """MongoDB authentication credentials"""
    username: str
    password: str
    auth_source: str = "admin"
    auth_mechanism: str = "SCRAM-SHA-256"
    hosts: List[str] = field(default_factory=list)
    replica_set: Optional[str] = None
    ssl_enabled: bool = True
    ssl_cert_path: Optional[str] = None
    ssl_key_path: Optional[str] = None
    ssl_ca_path: Optional[str] = None


@dataclass
class MongoDBPoolConfig:
    """MongoDB connection pool configuration"""
    max_pool_size: int = 100
    min_pool_size: int = 10
    max_idle_time_ms: int = 30000
    wait_queue_timeout_ms: int = 10000
    server_selection_timeout_ms: int = 30000
    socket_timeout_ms: int = 20000
    connect_timeout_ms: int = 20000
    heartbeat_frequency_ms: int = 10000
    retry_writes: bool = True
    retry_reads: bool = True


@dataclass
class MongoDBPerformanceConfig:
    """
MongoDB performance optimization settings"""
    read_preference: str = "secondaryPreferred"
    write_concern_w: Union[int, str] = "majority"
    write_concern_j: bool = True
    write_concern_wtimeout: int = 10000
    read_concern_level: str = "majority"
    compression: List[str] = field(default_factory=lambda: ["zstd", "snappy", "zlib"])
    max_staleness_seconds: int = 120
    local_threshold_ms: int = 15


@dataclass
class MongoDBIndexConfig:
    """MongoDB indexing configuration for different collections"""
    content_fingerprints: List[Dict[str, Any]] = field(default_factory=lambda: [
        {"fingerprint_hash": 1, "content_type": 1},
        {"creator_id": 1, "created_at": -1},
        {"platform": 1, "status": 1},
        {"similarity_score": 1}
    ])
    analytics_events: List[Dict[str, Any]] = field(default_factory=lambda: [
        {"event_type": 1, "timestamp": -1},
        {"user_id": 1, "session_id": 1},
        {"platform": 1, "created_at": -1}
    ])
    media_metadata: List[Dict[str, Any]] = field(default_factory=lambda: [
        {"content_id": 1, "media_type": 1},
        {"creator_id": 1, "upload_date": -1},
        {"file_hash": 1}
    ])
    monetization_tracking: List[Dict[str, Any]] = field(default_factory=lambda: [
        {"content_id": 1, "platform": 1, "date": -1},
        {"creator_id": 1, "revenue_date": -1},
        {"transaction_id": 1}
    ])


class MongoDBConfig:
    """
    Professional MongoDB configuration manager for IA-Influencer Agent Platform
    
    Handles document storage for content fingerprinting, media metadata,
    real-time analytics, and monetization tracking across multi-tenant platform.
    """
    def __init__(self, 
                 environment: MongoDBEnvironment = MongoDBEnvironment.DEVELOPMENT,
                 workload_type: MongoDBWorkloadType = MongoDBWorkloadType.MEDIA_STORAGE):
        self.environment = environment
        self.workload_type = workload_type
        self.credentials = self._load_credentials()
        self.pool_config = self._get_pool_config()
        self.performance_config = self._get_performance_config()
        self.index_config = MongoDBIndexConfig()
        self._clients: Dict[str, MongoClient] = {}
        self._async_clients: Dict[str, AsyncIOMotorClient] = {}
        self._setup_logging()

    def _setup_logging(self) -> None:
        """
Setup MongoDB-specific logging"""
        self.logger = logging.getLogger(f"mongodb.{self.environment.value}")
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
            self.logger.setLevel(logging.INFO)

    def _load_credentials(self) -> MongoDBCredentials:
        """Load MongoDB credentials from environment"""
        hosts_str = os.getenv(f"MONGODB_HOSTS_{self.environment.value.upper()}", "localhost:27017")
        hosts = [host.strip() for host in hosts_str.split(",")]
        
        return MongoDBCredentials(
            username=os.getenv(f"MONGODB_USERNAME_{self.environment.value.upper()}", "mongodb"),
            password=os.getenv(f"MONGODB_PASSWORD_{self.environment.value.upper()}", ""),
            auth_source=os.getenv(f"MONGODB_AUTH_SOURCE_{self.environment.value.upper()}", "admin"),
            auth_mechanism=os.getenv(f"MONGODB_AUTH_MECHANISM_{self.environment.value.upper()}", "SCRAM-SHA-256"),
            hosts=hosts,
            replica_set=os.getenv(f"MONGODB_REPLICA_SET_{self.environment.value.upper()}"),
            ssl_enabled=os.getenv(f"MONGODB_SSL_ENABLED_{self.environment.value.upper()}", "true").lower() == "true",
            ssl_cert_path=os.getenv(f"MONGODB_SSL_CERT_{self.environment.value.upper()}"),
            ssl_key_path=os.getenv(f"MONGODB_SSL_KEY_{self.environment.value.upper()}"),
            ssl_ca_path=os.getenv(f"MONGODB_SSL_CA_{self.environment.value.upper()}")
        )

    def _get_pool_config(self) -> MongoDBPoolConfig:
        """Get connection pool configuration based on environment and workload"""
        base_config = {
            MongoDBEnvironment.DEVELOPMENT: MongoDBPoolConfig(
                max_pool_size=20, min_pool_size=5
            ),
            MongoDBEnvironment.STAGING: MongoDBPoolConfig(
                max_pool_size=50, min_pool_size=10
            ),
            MongoDBEnvironment.PRODUCTION: MongoDBPoolConfig(
                max_pool_size=100, min_pool_size=20,
                server_selection_timeout_ms=60000,
                socket_timeout_ms=30000
            ),
            MongoDBEnvironment.TESTING: MongoDBPoolConfig(
                max_pool_size=10, min_pool_size=2
            )
        }.get(self.environment, MongoDBPoolConfig())

        # Adjust based on workload type
        if self.workload_type == MongoDBWorkloadType.REAL_TIME:
            base_config.max_pool_size *= 2
            base_config.socket_timeout_ms = 5000
        elif self.workload_type == MongoDBWorkloadType.ANALYTICS:
            base_config.socket_timeout_ms = 60000
            base_config.server_selection_timeout_ms = 60000

        return base_config

    def _get_performance_config(self) -> MongoDBPerformanceConfig:
        """
Get performance configuration based on workload type"""
        configs = {
            MongoDBWorkloadType.MEDIA_STORAGE: MongoDBPerformanceConfig(
                read_preference="secondaryPreferred",
                write_concern_w="majority",
                compression=["zstd", "snappy"]
            ),
            MongoDBWorkloadType.ANALYTICS: MongoDBPerformanceConfig(
                read_preference="secondary",
                write_concern_w=1,
                write_concern_j=False,
                max_staleness_seconds=300
            ),
            MongoDBWorkloadType.REAL_TIME: MongoDBPerformanceConfig(
                read_preference="primary",
                write_concern_w="majority",
                write_concern_wtimeout=5000,
                read_concern_level="linearizable"
            ),
            MongoDBWorkloadType.CONTENT_PROTECTION: MongoDBPerformanceConfig(
                read_preference="primaryPreferred",
                write_concern_w="majority",
                write_concern_j=True
            ),
            MongoDBWorkloadType.MONETIZATION: MongoDBPerformanceConfig(
                read_preference="primary",
                write_concern_w="majority",
                write_concern_j=True,
                read_concern_level="majority"
            )
        }
        return configs.get(self.workload_type, MongoDBPerformanceConfig())

    def get_connection_string(self, database_name: Optional[str] = None) -> str:
        """
        Generate MongoDB connection string with authentication and SSL
        
        Args:
            database_name: Optional specific database name
            
        Returns:
            MongoDB connection string
        """
        try:
            # URL encode credentials
            username = quote_plus(self.credentials.username)
            password = quote_plus(self.credentials.password)
            
            # Build connection string
            hosts_str = ",".join(self.credentials.hosts)
            connection_string = f"mongodb://{username}:{password}@{hosts_str}/"
            
            if database_name:
                connection_string += database_name
            
            # Add connection options
            options = []
            options.append(f"authSource={self.credentials.auth_source}")
            options.append(f"authMechanism={self.credentials.auth_mechanism}")
            
            if self.credentials.replica_set:
                options.append(f"replicaSet={self.credentials.replica_set}")
            
            if self.credentials.ssl_enabled:
                options.append("ssl=true")
                if self.credentials.ssl_cert_path:
                    options.append(f"sslCertificateKeyFile={self.credentials.ssl_cert_path}")
                if self.credentials.ssl_ca_path:
                    options.append(f"sslCAFile={self.credentials.ssl_ca_path}")
            
            # Add performance options
            options.extend([
                f"maxPoolSize={self.pool_config.max_pool_size}",
                f"minPoolSize={self.pool_config.min_pool_size}",
                f"maxIdleTimeMS={self.pool_config.max_idle_time_ms}",
                f"serverSelectionTimeoutMS={self.pool_config.server_selection_timeout_ms}",
                f"socketTimeoutMS={self.pool_config.socket_timeout_ms}",
                f"connectTimeoutMS={self.pool_config.connect_timeout_ms}",
                f"retryWrites={str(self.pool_config.retry_writes).lower()}",
                f"retryReads={str(self.pool_config.retry_reads).lower()}",
                f"compressors={','.join(self.performance_config.compression)}"
            ])
            
            if options:
                connection_string += "?" + "&".join(options)
            
            return connection_string
            
        except Exception as e:
            self.logger.error(f"Failed to generate MongoDB connection string: {str(e)}")
            raise

    def create_client(self, database_name: Optional[str] = None, **kwargs) -> MongoClient:
        """
        Create MongoDB client with optimized configuration
        
        Args:
            database_name: Optional specific database name
            **kwargs: Additional client parameters
            
        Returns:
            Configured MongoDB client
        """
        client_key = database_name or "default"
        
        if client_key in self._clients:
            return self._clients[client_key]
        
        try:
            connection_string = self.get_connection_string(database_name)
            
            # Configure read and write preferences
            read_pref = getattr(ReadPreference, self.performance_config.read_preference.upper())
            write_concern = WriteConcern(
                w=self.performance_config.write_concern_w,
                j=self.performance_config.write_concern_j,
                wtimeout=self.performance_config.write_concern_wtimeout
            )
            
            client_config = {
                "read_preference": read_pref,
                "write_concern": write_concern,
                "read_concern_level": self.performance_config.read_concern_level,
                "local_threshold_ms": self.performance_config.local_threshold_ms,
                **kwargs
            }
            
            if self.performance_config.max_staleness_seconds > 90:
                client_config["max_staleness_seconds"] = self.performance_config.max_staleness_seconds
            
            client = MongoClient(connection_string, **client_config)
            
            # Test connection
            client.admin.command('ping')
            
            self._clients[client_key] = client
            self.logger.info(f"MongoDB client created successfully for {client_key}")
            
            return client
            
        except Exception as e:
            self.logger.error(f"Failed to create MongoDB client: {str(e)}")
            raise

    def create_async_client(self, database_name: Optional[str] = None, **kwargs) -> AsyncIOMotorClient:
        """
        Create async MongoDB client for real-time operations
        
        Args:
            database_name: Optional specific database name
            **kwargs: Additional client parameters
            
        Returns:
            Configured async MongoDB client
        """
        client_key = f"async_{database_name or 'default'}"
        
        if client_key in self._async_clients:
            return self._async_clients[client_key]
        
        try:
            connection_string = self.get_connection_string(database_name)
            
            # Configure read and write preferences for async
            read_pref = getattr(ReadPreference, self.performance_config.read_preference.upper())
            write_concern = WriteConcern(
                w=self.performance_config.write_concern_w,
                j=self.performance_config.write_concern_j,
                wtimeout=self.performance_config.write_concern_wtimeout
            )
            
            client_config = {
                "read_preference": read_pref,
                "write_concern": write_concern,
                "read_concern_level": self.performance_config.read_concern_level,
                "io_loop": None,  # Use default event loop
                **kwargs
            }
            
            client = AsyncIOMotorClient(connection_string, **client_config)
            self._async_clients[client_key] = client
            
            self.logger.info(f"MongoDB async client created successfully for {client_key}")
            return client
            
        except Exception as e:
            self.logger.error(f"Failed to create MongoDB async client: {str(e)}")
            raise

    def get_content_protection_client(self) -> MongoClient:
        """Get MongoDB client optimized for content protection operations"""
        return self.create_client("ia_influencer_content_protection")

    def get_analytics_client(self) -> MongoClient:
        """Get MongoDB client optimized for analytics workloads"""
        analytics_config = MongoDBConfig(self.environment, MongoDBWorkloadType.ANALYTICS)
        return analytics_config.create_client("ia_influencer_analytics")

    def get_media_storage_client(self) -> MongoClient:
        """Get MongoDB client optimized for media storage"""
        return self.create_client("ia_influencer_media")

    def get_monetization_client(self) -> MongoClient:
        """Get MongoDB client optimized for monetization tracking"""
        monetization_config = MongoDBConfig(self.environment, MongoDBWorkloadType.MONETIZATION)
        return monetization_config.create_client("ia_influencer_monetization")

    def get_real_time_client(self) -> AsyncIOMotorClient:
        """Get async MongoDB client for real-time operations"""
        real_time_config = MongoDBConfig(self.environment, MongoDBWorkloadType.REAL_TIME)
        return real_time_config.create_async_client("ia_influencer_realtime")

    def setup_indexes(self, client: MongoClient, database_name: str) -> None:
        """
        Setup optimized indexes for different collection types
        
        Args:
            client: MongoDB client
            database_name: Target database name
        """
        try:
            db = client[database_name]
            
            # Content fingerprints indexes
            fingerprints_collection = db.content_fingerprints
            for index_spec in self.index_config.content_fingerprints:
                fingerprints_collection.create_index(list(index_spec.items()), background=True)
            
            # Analytics events indexes
            analytics_collection = db.analytics_events
            for index_spec in self.index_config.analytics_events:
                analytics_collection.create_index(list(index_spec.items()), background=True)
            
            # Media metadata indexes
            media_collection = db.media_metadata
            for index_spec in self.index_config.media_metadata:
                media_collection.create_index(list(index_spec.items()), background=True)
            
            # Monetization tracking indexes
            monetization_collection = db.monetization_tracking
            for index_spec in self.index_config.monetization_tracking:
                monetization_collection.create_index(list(index_spec.items()), background=True)
            
            self.logger.info(f"Indexes created successfully for database: {database_name}")
            
        except Exception as e:
            self.logger.error(f"Failed to setup indexes: {str(e)}")
            raise

    def health_check(self) -> Dict[str, Any]:
        """
        Perform comprehensive health check on MongoDB connections
        
        Returns:
            Health check results dictionary
        """
        health_status = {
            "status": "healthy",
            "environment": self.environment.value,
            "workload_type": self.workload_type.value,
            "clients": {},
            "timestamp": None
        }
        
        import datetime
        health_status["timestamp"] = datetime.datetime.utcnow().isoformat()
        
        try:
            # Test main client
            main_client = self.create_client()
            
            # Get server info
            server_info = main_client.server_info()
            admin_stats = main_client.admin.command("serverStatus")
            
            health_status["clients"]["main"] = {
                "status": "healthy",
                "mongodb_version": server_info.get("version"),
                "uptime_seconds": admin_stats.get("uptime"),
                "connections_current": admin_stats.get("connections", {}).get("current"),
                "connections_available": admin_stats.get("connections", {}).get("available"),
                "memory_resident": admin_stats.get("mem", {}).get("resident"),
                "memory_virtual": admin_stats.get("mem", {}).get("virtual")
            }
            
            # Test database connectivity
            databases = main_client.list_database_names()
            health_status["databases"] = databases
            
        except (ConnectionFailure, ServerSelectionTimeoutError) as e:
            health_status["status"] = "unhealthy"
            health_status["clients"]["main"] = {
                "status": "unhealthy",
                "error": str(e)
            }
            self.logger.error(f"MongoDB health check failed: {str(e)}")
        except Exception as e:
            health_status["status"] = "unhealthy"
            health_status["error"] = str(e)
            self.logger.error(f"MongoDB health check error: {str(e)}")
        
        return health_status

    def close_all_connections(self) -> None:
        """Close all MongoDB connections and cleanup resources"""
        # Close sync clients
        for client_name, client in self._clients.items():
            try:
                client.close()
                self.logger.info(f"Closed MongoDB client: {client_name}")
            except Exception as e:
                self.logger.error(f"Error closing client {client_name}: {str(e)}")
        
        # Close async clients
        for client_name, client in self._async_clients.items():
            try:
                client.close()
                self.logger.info(f"Closed MongoDB async client: {client_name}")
            except Exception as e:
                self.logger.error(f"Error closing async client {client_name}: {str(e)}")
        
        self._clients.clear()
        self._async_clients.clear()

    def __del__(self):
        """Cleanup on object destruction"""
        self.close_all_connections()
