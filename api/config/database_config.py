"""Database Configuration - IA Influencer Agent Platform
Advanced database configuration for PostgreSQL, Redis, MongoDB, Elasticsearch

Author: Fahed Mlaiel <mlaiel@live.de>
WARNING: This code is protected by copyright. Any unauthorized use, reproduction,
or distribution without written permission from Fahed Mlaiel is strictly prohibited.
"""
import os
from typing import Dict, Optional, List, Any
from dataclasses import dataclass, field
from sqlalchemy import create_engine
from sqlalchemy.pool import QueuePool
import redis
from pymongo import MongoClient
from elasticsearch import Elasticsearch


@dataclass
class DatabaseConfig:
    """PostgreSQL database configuration"""    
    # Connection Parameters
    host: str = field(default_factory=lambda: os.getenv("DB_HOST", "localhost"))
    port: int = field(default_factory=lambda: int(os.getenv("DB_PORT", "5432")))
    database: str = field(default_factory=lambda: os.getenv("DB_NAME", "ia_influencer_agent"))
    username: str = field(default_factory=lambda: os.getenv("DB_USERNAME", "postgres"))
    password: str = field(default_factory=lambda: os.getenv("DB_PASSWORD", "password"))
    
    # SSL Configuration
    ssl_mode: str = field(default_factory=lambda: os.getenv("DB_SSL_MODE", "prefer"))
    ssl_cert: Optional[str] = field(default_factory=lambda: os.getenv("DB_SSL_CERT"))
    ssl_key: Optional[str] = field(default_factory=lambda: os.getenv("DB_SSL_KEY"))
    ssl_ca: Optional[str] = field(default_factory=lambda: os.getenv("DB_SSL_CA"))
    
    # Connection Pool Configuration
    max_connections: int = field(default_factory=lambda: int(os.getenv("DB_MAX_CONNECTIONS", "100")))
    min_connections: int = field(default_factory=lambda: int(os.getenv("DB_MIN_CONNECTIONS", "5")))
    pool_size: int = field(default_factory=lambda: int(os.getenv("DB_POOL_SIZE", "20")))
    pool_overflow: int = field(default_factory=lambda: int(os.getenv("DB_POOL_OVERFLOW", "30")))
    pool_timeout: int = field(default_factory=lambda: int(os.getenv("DB_POOL_TIMEOUT", "30")))
    pool_recycle: int = field(default_factory=lambda: int(os.getenv("DB_POOL_RECYCLE", "3600")))
    
    # Query Configuration
    statement_timeout: int = field(default_factory=lambda: int(os.getenv("DB_STATEMENT_TIMEOUT", "30000")))  # ms
    lock_timeout: int = field(default_factory=lambda: int(os.getenv("DB_LOCK_TIMEOUT", "10000")))  # ms
    idle_in_transaction_session_timeout: int = field(default_factory=lambda: 
        int(os.getenv("DB_IDLE_TIMEOUT", "60000")))  # ms
    
    # Performance Tuning
    shared_preload_libraries: List[str] = field(default_factory=lambda: [
        "pg_stat_statements", "auto_explain", "pg_hint_plan"
    ])
    max_connections_per_database: int = field(default_factory=lambda: 
        int(os.getenv("DB_MAX_CONN_PER_DB", "50")))
    
    # Monitoring
    enable_query_logging: bool = field(default_factory=lambda: 
        os.getenv("DB_ENABLE_QUERY_LOGGING", "false").lower() == "true")
    log_slow_queries: bool = field(default_factory=lambda: 
        os.getenv("DB_LOG_SLOW_QUERIES", "true").lower() == "true")
    slow_query_threshold: float = field(default_factory=lambda: 
        float(os.getenv("DB_SLOW_QUERY_THRESHOLD", "1.0")))  # seconds
    
    @property
    def connection_url(self) -> str:
        """Generate SQLAlchemy connection URL"""        return (f"postgresql://{self.username}:{self.password}"
                f"@{self.host}:{self.port}/{self.database}")
    
    @property
    def async_connection_url(self) -> str:
        """Generate async SQLAlchemy connection URL"""        return (f"postgresql+asyncpg://{self.username}:{self.password}"
                f"@{self.host}:{self.port}/{self.database}")
    
    def create_engine(self):
        """Create SQLAlchemy engine with optimized configuration"""        connection_args = {
            "sslmode": self.ssl_mode,
            "application_name": "ia_influencer_agent",
            "statement_timeout": self.statement_timeout,
            "lock_timeout": self.lock_timeout,
            "idle_in_transaction_session_timeout": self.idle_in_transaction_session_timeout
        }
        
        if self.ssl_cert:
            connection_args.update({
                "sslcert": self.ssl_cert,
                "sslkey": self.ssl_key,
                "sslrootcert": self.ssl_ca
            })
        
        return create_engine(
            self.connection_url,
            poolclass=QueuePool,
            pool_size=self.pool_size,
            pool_overflow=self.pool_overflow,
            pool_timeout=self.pool_timeout,
            pool_recycle=self.pool_recycle,
            connect_args=connection_args,
            echo=self.enable_query_logging
        )


@dataclass
class RedisConfig:
    """Redis configuration for caching and session management"""    
    # Connection Parameters
    host: str = field(default_factory=lambda: os.getenv("REDIS_HOST", "localhost"))
    port: int = field(default_factory=lambda: int(os.getenv("REDIS_PORT", "6379")))
    db: int = field(default_factory=lambda: int(os.getenv("REDIS_DB", "0")))
    password: Optional[str] = field(default_factory=lambda: os.getenv("REDIS_PASSWORD"))
    username: Optional[str] = field(default_factory=lambda: os.getenv("REDIS_USERNAME"))
    
    # SSL Configuration
    ssl_enabled: bool = field(default_factory=lambda: 
        os.getenv("REDIS_SSL_ENABLED", "false").lower() == "true")
    ssl_cert: Optional[str] = field(default_factory=lambda: os.getenv("REDIS_SSL_CERT"))
    ssl_key: Optional[str] = field(default_factory=lambda: os.getenv("REDIS_SSL_KEY"))
    ssl_ca: Optional[str] = field(default_factory=lambda: os.getenv("REDIS_SSL_CA"))
    
    # Connection Pool Configuration
    max_connections: int = field(default_factory=lambda: int(os.getenv("REDIS_MAX_CONNECTIONS", "100")))
    connection_timeout: int = field(default_factory=lambda: int(os.getenv("REDIS_TIMEOUT", "10")))
    socket_keepalive: bool = field(default_factory=lambda: 
        os.getenv("REDIS_SOCKET_KEEPALIVE", "true").lower() == "true")
    socket_keepalive_options: Dict = field(default_factory=dict)
    
    # Performance Configuration
    decode_responses: bool = True
    socket_connect_timeout: int = 10
    socket_timeout: int = 10
    retry_on_timeout: bool = True
    
    # Cache Configuration
    default_ttl: int = field(default_factory=lambda: int(os.getenv("REDIS_DEFAULT_TTL", "3600")))  # 1 hour
    session_ttl: int = field(default_factory=lambda: int(os.getenv("REDIS_SESSION_TTL", "86400")))  # 24 hours
    cache_key_prefix: str = field(default_factory=lambda: os.getenv("REDIS_KEY_PREFIX", "ia_influencer:"))
    
    # Cluster Configuration
    cluster_enabled: bool = field(default_factory=lambda: 
        os.getenv("REDIS_CLUSTER_ENABLED", "false").lower() == "true")
    cluster_nodes: List[Dict[str, Any]] = field(default_factory=list)
    
    @property
    def connection_url(self) -> str:
        """Generate Redis connection URL"""        auth = ""
        if self.username and self.password:
            auth = f"{self.username}:{self.password}@"
        elif self.password:
            auth = f":{self.password}@"
        
        protocol = "rediss" if self.ssl_enabled else "redis"
        return f"{protocol}://{auth}{self.host}:{self.port}/{self.db}"
    
    def create_connection_pool(self):
        """Create Redis connection pool"""        connection_kwargs = {
            "host": self.host,
            "port": self.port,
            "db": self.db,
            "password": self.password,
            "username": self.username,
            "decode_responses": self.decode_responses,
            "socket_connect_timeout": self.socket_connect_timeout,
            "socket_timeout": self.socket_timeout,
            "socket_keepalive": self.socket_keepalive,
            "socket_keepalive_options": self.socket_keepalive_options,
            "retry_on_timeout": self.retry_on_timeout
        }
        
        if self.ssl_enabled:
            connection_kwargs.update({
                "ssl": True,
                "ssl_certfile": self.ssl_cert,
                "ssl_keyfile": self.ssl_key,
                "ssl_ca_certs": self.ssl_ca
            })
        
        return redis.ConnectionPool(
            max_connections=self.max_connections,
            **connection_kwargs
        )
    
    def create_client(self) -> redis.Redis:
        """Create Redis client"""        return redis.Redis(connection_pool=self.create_connection_pool())


@dataclass
class MongoDBConfig:
    """MongoDB configuration for document storage"""    
    # Connection Parameters
    host: str = field(default_factory=lambda: os.getenv("MONGODB_HOST", "localhost"))
    port: int = field(default_factory=lambda: int(os.getenv("MONGODB_PORT", "27017")))
    database: str = field(default_factory=lambda: os.getenv("MONGODB_DATABASE", "ia_influencer_agent"))
    username: Optional[str] = field(default_factory=lambda: os.getenv("MONGODB_USERNAME"))
    password: Optional[str] = field(default_factory=lambda: os.getenv("MONGODB_PASSWORD"))
    
    # Authentication
    auth_source: str = field(default_factory=lambda: os.getenv("MONGODB_AUTH_SOURCE", "admin"))
    auth_mechanism: str = field(default_factory=lambda: os.getenv("MONGODB_AUTH_MECHANISM", "SCRAM-SHA-1"))
    
    # Connection Pool Configuration
    max_pool_size: int = field(default_factory=lambda: int(os.getenv("MONGODB_MAX_POOL_SIZE", "100")))
    min_pool_size: int = field(default_factory=lambda: int(os.getenv("MONGODB_MIN_POOL_SIZE", "10")))
    max_idle_time: int = field(default_factory=lambda: int(os.getenv("MONGODB_MAX_IDLE_TIME", "60000")))  # ms
    
    # SSL Configuration
    ssl_enabled: bool = field(default_factory=lambda: 
        os.getenv("MONGODB_SSL_ENABLED", "false").lower() == "true")
    ssl_cert_file: Optional[str] = field(default_factory=lambda: os.getenv("MONGODB_SSL_CERT"))
    ssl_key_file: Optional[str] = field(default_factory=lambda: os.getenv("MONGODB_SSL_KEY"))
    ssl_ca_file: Optional[str] = field(default_factory=lambda: os.getenv("MONGODB_SSL_CA"))
    
    # Replica Set Configuration
    replica_set: Optional[str] = field(default_factory=lambda: os.getenv("MONGODB_REPLICA_SET"))
    read_preference: str = field(default_factory=lambda: os.getenv("MONGODB_READ_PREFERENCE", "primary"))
    write_concern: int = field(default_factory=lambda: int(os.getenv("MONGODB_WRITE_CONCERN", "1")))
    
    # Timeout Configuration
    server_selection_timeout: int = field(default_factory=lambda: 
        int(os.getenv("MONGODB_SERVER_SELECTION_TIMEOUT", "30000")))  # ms
    socket_timeout: int = field(default_factory=lambda: 
        int(os.getenv("MONGODB_SOCKET_TIMEOUT", "20000")))  # ms
    connect_timeout: int = field(default_factory=lambda: 
        int(os.getenv("MONGODB_CONNECT_TIMEOUT", "20000")))  # ms
    
    @property
    def connection_url(self) -> str:
        """Generate MongoDB connection URL"""        auth = ""
        if self.username and self.password:
            auth = f"{self.username}:{self.password}@"
        
        options = []
        if self.auth_source:
            options.append(f"authSource={self.auth_source}")
        if self.auth_mechanism:
            options.append(f"authMechanism={self.auth_mechanism}")
        if self.replica_set:
            options.append(f"replicaSet={self.replica_set}")
        if self.ssl_enabled:
            options.append("ssl=true")
        
        options_str = "&".join(options)
        options_str = f"?{options_str}" if options_str else ""
        
        return f"mongodb://{auth}{self.host}:{self.port}/{self.database}{options_str}"
    
    def create_client(self) -> MongoClient:
        """Create MongoDB client"""        client_kwargs = {
            "host": self.connection_url,
            "maxPoolSize": self.max_pool_size,
            "minPoolSize": self.min_pool_size,
            "maxIdleTimeMS": self.max_idle_time,
            "serverSelectionTimeoutMS": self.server_selection_timeout,
            "socketTimeoutMS": self.socket_timeout,
            "connectTimeoutMS": self.connect_timeout
        }
        
        if self.ssl_enabled:
            client_kwargs.update({
                "ssl": True,
                "ssl_certfile": self.ssl_cert_file,
                "ssl_keyfile": self.ssl_key_file,
                "ssl_ca_certs": self.ssl_ca_file
            })
        
        return MongoClient(**client_kwargs)


@dataclass
class ElasticsearchConfig:
    """Elasticsearch configuration for search and analytics"""    
    # Connection Parameters
    hosts: List[str] = field(default_factory=lambda: 
        os.getenv("ELASTICSEARCH_HOSTS", "localhost:9200").split(","))
    username: Optional[str] = field(default_factory=lambda: os.getenv("ELASTICSEARCH_USERNAME"))
    password: Optional[str] = field(default_factory=lambda: os.getenv("ELASTICSEARCH_PASSWORD"))
    api_key: Optional[str] = field(default_factory=lambda: os.getenv("ELASTICSEARCH_API_KEY"))
    
    # SSL Configuration
    use_ssl: bool = field(default_factory=lambda: 
        os.getenv("ELASTICSEARCH_USE_SSL", "false").lower() == "true")
    verify_certs: bool = field(default_factory=lambda: 
        os.getenv("ELASTICSEARCH_VERIFY_CERTS", "true").lower() == "true")
    ssl_cert: Optional[str] = field(default_factory=lambda: os.getenv("ELASTICSEARCH_SSL_CERT"))
    ssl_key: Optional[str] = field(default_factory=lambda: os.getenv("ELASTICSEARCH_SSL_KEY"))
    ssl_ca: Optional[str] = field(default_factory=lambda: os.getenv("ELASTICSEARCH_SSL_CA"))
    
    # Connection Configuration
    timeout: int = field(default_factory=lambda: int(os.getenv("ELASTICSEARCH_TIMEOUT", "30")))
    max_retries: int = field(default_factory=lambda: int(os.getenv("ELASTICSEARCH_MAX_RETRIES", "3")))
    retry_on_timeout: bool = field(default_factory=lambda: 
        os.getenv("ELASTICSEARCH_RETRY_ON_TIMEOUT", "true").lower() == "true")
    
    # Index Configuration
    index_prefix: str = field(default_factory=lambda: 
        os.getenv("ELASTICSEARCH_INDEX_PREFIX", "ia_influencer"))
    number_of_shards: int = field(default_factory=lambda: 
        int(os.getenv("ELASTICSEARCH_SHARDS", "1")))
    number_of_replicas: int = field(default_factory=lambda: 
        int(os.getenv("ELASTICSEARCH_REPLICAS", "1")))
    refresh_interval: str = field(default_factory=lambda: 
        os.getenv("ELASTICSEARCH_REFRESH_INTERVAL", "1s"))
    
    # Search Configuration
    max_result_window: int = field(default_factory=lambda: 
        int(os.getenv("ELASTICSEARCH_MAX_RESULT_WINDOW", "10000")))
    default_page_size: int = field(default_factory=lambda: 
        int(os.getenv("ELASTICSEARCH_DEFAULT_PAGE_SIZE", "50")))
    
    def create_client(self) -> Elasticsearch:
        """Create Elasticsearch client"""        client_kwargs = {
            "hosts": self.hosts,
            "timeout": self.timeout,
            "max_retries": self.max_retries,
            "retry_on_timeout": self.retry_on_timeout
        }
        
        if self.username and self.password:
            client_kwargs["http_auth"] = (self.username, self.password)
        elif self.api_key:
            client_kwargs["api_key"] = self.api_key
        
        if self.use_ssl:
            client_kwargs.update({
                "use_ssl": True,
                "verify_certs": self.verify_certs,
                "ssl_cert": self.ssl_cert,
                "ssl_key": self.ssl_key,
                "ca_certs": self.ssl_ca
            })
        
        return Elasticsearch(**client_kwargs)
    
    def get_index_name(self, suffix: str) -> str:
        """Generate index name with prefix"""        return f"{self.index_prefix}_{suffix}"
    
    def get_index_settings(self) -> Dict[str, Any]:
        """Get default index settings"""        return {
            "settings": {
                "number_of_shards": self.number_of_shards,
                "number_of_replicas": self.number_of_replicas,
                "refresh_interval": self.refresh_interval,
                "max_result_window": self.max_result_window,
                "analysis": {
                    "analyzer": {
                        "content_analyzer": {
                            "type": "custom",
                            "tokenizer": "standard",
                            "filter": ["lowercase", "stop", "snowball"]
                        }
                    }
                }
            }
        }


@dataclass
class VectorDatabaseConfig:
    """FAISS Vector Database configuration for similarity search"""    
    # Storage Configuration
    index_path: str = field(default_factory=lambda: 
        os.getenv("VECTOR_DB_INDEX_PATH", "/data/vector_db/indexes"))
    metadata_path: str = field(default_factory=lambda: 
        os.getenv("VECTOR_DB_METADATA_PATH", "/data/vector_db/metadata"))
    
    # Vector Configuration
    dimension: int = field(default_factory=lambda: int(os.getenv("VECTOR_DIMENSION", "512")))
    index_type: str = field(default_factory=lambda: os.getenv("VECTOR_INDEX_TYPE", "IndexFlatL2"))
    metric_type: str = field(default_factory=lambda: os.getenv("VECTOR_METRIC_TYPE", "L2"))
    
    # Performance Configuration
    nlist: int = field(default_factory=lambda: int(os.getenv("VECTOR_NLIST", "100")))
    nprobe: int = field(default_factory=lambda: int(os.getenv("VECTOR_NPROBE", "10")))
    m: int = field(default_factory=lambda: int(os.getenv("VECTOR_M", "8")))
    nbits: int = field(default_factory=lambda: int(os.getenv("VECTOR_NBITS", "8")))
    
    # Search Configuration
    similarity_threshold: float = field(default_factory=lambda: 
        float(os.getenv("VECTOR_SIMILARITY_THRESHOLD", "0.8")))
    max_results: int = field(default_factory=lambda: int(os.getenv("VECTOR_MAX_RESULTS", "100")))
    
    # Content Type Configurations
    audio_dimension: int = field(default_factory=lambda: int(os.getenv("AUDIO_VECTOR_DIMENSION", "512")))
    video_dimension: int = field(default_factory=lambda: int(os.getenv("VIDEO_VECTOR_DIMENSION", "512")))
    image_dimension: int = field(default_factory=lambda: int(os.getenv("IMAGE_VECTOR_DIMENSION", "512")))
    text_dimension: int = field(default_factory=lambda: int(os.getenv("TEXT_VECTOR_DIMENSION", "768")))
    
    def __post_init__(self):
        """Create necessary directories"""        os.makedirs(self.index_path, exist_ok=True)
        os.makedirs(self.metadata_path, exist_ok=True)
    
    def get_index_path(self, content_type: str) -> str:
        """Get index file path for specific content type"""        return os.path.join(self.index_path, f"{content_type}_index.faiss")
    
    def get_metadata_path(self, content_type: str) -> str:
        """Get metadata file path for specific content type"""        return os.path.join(self.metadata_path, f"{content_type}_metadata.json")
    
    def get_dimension_for_content_type(self, content_type: str) -> int:
        """Get vector dimension for specific content type"""        dimension_map = {
            "audio": self.audio_dimension,
            "video": self.video_dimension,
            "image": self.image_dimension,
            "text": self.text_dimension
        }
        return dimension_map.get(content_type, self.dimension)
