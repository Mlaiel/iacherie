"""Application Configuration - IA Influencer Agent Platform
Core application settings and environment-specific configurations

Author: Fahed Mlaiel <mlaiel@live.de>
WARNING: This code is protected by copyright. Any unauthorized use, reproduction,
or distribution without written permission from Fahed Mlaiel is strictly prohibited.
"""

import os
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from datetime import timedelta
import secrets


@dataclass
class AppConfig:
    """
Base application configuration class"""
    
    # Application Identity
    app_name: str = "IA Influencer Agent Platform"
    app_version: str = "2.0.0"
    app_description: str = "AI-powered content protection and monetization platform for creators"
    author: str = "Fahed Mlaiel"
    contact_email: str = "mlaiel@live.de"
    
    # Environment Settings
    environment: str = field(default_factory=lambda: os.getenv("ENVIRONMENT", "development"))
    debug: bool = field(default_factory=lambda: os.getenv("DEBUG", "False").lower() == "true")
    testing: bool = field(default_factory=lambda: os.getenv("TESTING", "False").lower() == "true")
    
    # Server Configuration
    host: str = field(default_factory=lambda: os.getenv("HOST", "0.0.0.0"))
    port: int = field(default_factory=lambda: int(os.getenv("PORT", "8000")))
    workers: int = field(default_factory=lambda: int(os.getenv("WORKERS", "4")))
    reload: bool = field(default_factory=lambda: os.getenv("RELOAD", "False").lower() == "true")
    
    # Security Configuration
    secret_key: str = field(default_factory=lambda: os.getenv("SECRET_KEY", secrets.token_hex(32)))
    jwt_secret: str = field(default_factory=lambda: os.getenv("JWT_SECRET", secrets.token_hex(32)))
    encryption_key: str = field(default_factory=lambda: os.getenv("ENCRYPTION_KEY", secrets.token_hex(32)))
    password_salt: str = field(default_factory=lambda: os.getenv("PASSWORD_SALT", secrets.token_hex(16)))
    
    # Session Management
    session_timeout: timedelta = field(default_factory=lambda: timedelta(hours=24))
    jwt_access_token_expire: timedelta = field(default_factory=lambda: timedelta(hours=1))
    jwt_refresh_token_expire: timedelta = field(default_factory=lambda: timedelta(days=30))
    
    # CORS Configuration
    cors_origins: List[str] = field(default_factory=lambda: [
        "http://localhost:3000",
        "http://localhost:8080",
        "https://app.ia-influencer-agent.com",
        "https://dashboard.ia-influencer-agent.com"
    ])
    cors_methods: List[str] = field(default_factory=lambda: ["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"])
    cors_headers: List[str] = field(default_factory=lambda: ["*"])
    
    # Database Configuration
    database_url: str = field(default_factory=lambda: os.getenv("DATABASE_URL", 
        "postgresql://postgres:password@localhost:5432/ia_influencer_agent"))
    database_host: str = field(default_factory=lambda: os.getenv("DB_HOST", "localhost"))
    database_port: int = field(default_factory=lambda: int(os.getenv("DB_PORT", "5432")))
    database_name: str = field(default_factory=lambda: os.getenv("DB_NAME", "ia_influencer_agent"))
    database_username: str = field(default_factory=lambda: os.getenv("DB_USERNAME", "postgres"))
    database_password: str = field(default_factory=lambda: os.getenv("DB_PASSWORD", "password"))
    database_ssl_mode: str = field(default_factory=lambda: os.getenv("DB_SSL_MODE", "prefer"))
    database_max_connections: int = field(default_factory=lambda: int(os.getenv("DB_MAX_CONNECTIONS", "100")))
    database_pool_size: int = field(default_factory=lambda: int(os.getenv("DB_POOL_SIZE", "20")))
    database_pool_overflow: int = field(default_factory=lambda: int(os.getenv("DB_POOL_OVERFLOW", "30")))
    
    # Redis Configuration
    redis_url: str = field(default_factory=lambda: os.getenv("REDIS_URL", "redis://localhost:6379"))
    redis_host: str = field(default_factory=lambda: os.getenv("REDIS_HOST", "localhost"))
    redis_port: int = field(default_factory=lambda: int(os.getenv("REDIS_PORT", "6379")))
    redis_db: int = field(default_factory=lambda: int(os.getenv("REDIS_DB", "0")))
    redis_password: Optional[str] = field(default_factory=lambda: os.getenv("REDIS_PASSWORD"))
    redis_max_connections: int = field(default_factory=lambda: int(os.getenv("REDIS_MAX_CONNECTIONS", "100")))
    
    # MongoDB Configuration
    mongodb_url: str = field(default_factory=lambda: os.getenv("MONGODB_URL", 
        "mongodb://localhost:27017/ia_influencer_agent"))
    mongodb_host: str = field(default_factory=lambda: os.getenv("MONGODB_HOST", "localhost"))
    mongodb_port: int = field(default_factory=lambda: int(os.getenv("MONGODB_PORT", "27017")))
    mongodb_database: str = field(default_factory=lambda: os.getenv("MONGODB_DATABASE", "ia_influencer_agent"))
    mongodb_username: Optional[str] = field(default_factory=lambda: os.getenv("MONGODB_USERNAME"))
    mongodb_password: Optional[str] = field(default_factory=lambda: os.getenv("MONGODB_PASSWORD"))
    
    # Elasticsearch Configuration
    elasticsearch_url: str = field(default_factory=lambda: os.getenv("ELASTICSEARCH_URL", 
        "http://localhost:9200"))
    elasticsearch_username: Optional[str] = field(default_factory=lambda: os.getenv("ELASTICSEARCH_USERNAME"))
    elasticsearch_password: Optional[str] = field(default_factory=lambda: os.getenv("ELASTICSEARCH_PASSWORD"))
    elasticsearch_index_prefix: str = field(default_factory=lambda: os.getenv("ELASTICSEARCH_INDEX_PREFIX", 
        "ia_influencer"))
    
    # Vector Database Configuration (FAISS)
    vector_db_path: str = field(default_factory=lambda: os.getenv("VECTOR_DB_PATH", 
        "/data/vector_db"))
    vector_dimension: int = field(default_factory=lambda: int(os.getenv("VECTOR_DIMENSION", "512")))
    vector_index_type: str = field(default_factory=lambda: os.getenv("VECTOR_INDEX_TYPE", "IndexFlatL2"))
    
    # Celery Configuration
    celery_broker_url: str = field(default_factory=lambda: os.getenv("CELERY_BROKER_URL", 
        "redis://localhost:6379/1"))
    celery_result_backend: str = field(default_factory=lambda: os.getenv("CELERY_RESULT_BACKEND", 
        "redis://localhost:6379/2"))
    celery_task_serializer: str = "json"
    celery_result_serializer: str = "json"
    celery_accept_content: List[str] = field(default_factory=lambda: ["json"])
    celery_timezone: str = "UTC"
    celery_worker_concurrency: int = field(default_factory=lambda: int(os.getenv("CELERY_CONCURRENCY", "4")))
    
    # Storage Configuration (S3/MinIO)
    storage_type: str = field(default_factory=lambda: os.getenv("STORAGE_TYPE", "s3"))  # s3, minio, local
    s3_access_key: Optional[str] = field(default_factory=lambda: os.getenv("S3_ACCESS_KEY"))
    s3_secret_key: Optional[str] = field(default_factory=lambda: os.getenv("S3_SECRET_KEY"))
    s3_bucket_name: str = field(default_factory=lambda: os.getenv("S3_BUCKET_NAME", "ia-influencer-storage"))
    s3_region: str = field(default_factory=lambda: os.getenv("S3_REGION", "us-east-1"))
    s3_endpoint_url: Optional[str] = field(default_factory=lambda: os.getenv("S3_ENDPOINT_URL"))
    
    # Local Storage Configuration
    local_storage_path: str = field(default_factory=lambda: os.getenv("LOCAL_STORAGE_PATH", "/data/uploads"))
    max_upload_size: int = field(default_factory=lambda: int(os.getenv("MAX_UPLOAD_SIZE", "104857600")))  # 100MB
    
    # Logging Configuration
    log_level: str = field(default_factory=lambda: os.getenv("LOG_LEVEL", "INFO"))
    log_format: str = field(default_factory=lambda: os.getenv("LOG_FORMAT", 
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"))
    log_file_path: str = field(default_factory=lambda: os.getenv("LOG_FILE_PATH", "/var/log/ia_influencer.log"))
    log_max_size: int = field(default_factory=lambda: int(os.getenv("LOG_MAX_SIZE", "10485760")))  # 10MB
    log_backup_count: int = field(default_factory=lambda: int(os.getenv("LOG_BACKUP_COUNT", "5")))
    structured_logging: bool = field(default_factory=lambda: os.getenv("STRUCTURED_LOGGING", "true").lower() == "true")
    log_to_console: bool = field(default_factory=lambda: os.getenv("LOG_TO_CONSOLE", "true").lower() == "true")
    
    # Monitoring Configuration
    prometheus_host: str = field(default_factory=lambda: os.getenv("PROMETHEUS_HOST", "localhost"))
    prometheus_port: int = field(default_factory=lambda: int(os.getenv("PROMETHEUS_PORT", "9090")))
    grafana_host: str = field(default_factory=lambda: os.getenv("GRAFANA_HOST", "localhost"))
    grafana_port: int = field(default_factory=lambda: int(os.getenv("GRAFANA_PORT", "3000")))
    metrics_retention: str = field(default_factory=lambda: os.getenv("METRICS_RETENTION", "15d"))
    alerts_webhook: Optional[str] = field(default_factory=lambda: os.getenv("ALERTS_WEBHOOK"))
    
    # Rate Limiting Configuration
    rate_limit_per_minute: int = field(default_factory=lambda: int(os.getenv("RATE_LIMIT_PER_MINUTE", "100")))
    rate_limit_per_hour: int = field(default_factory=lambda: int(os.getenv("RATE_LIMIT_PER_HOUR", "1000")))
    rate_limit_per_day: int = field(default_factory=lambda: int(os.getenv("RATE_LIMIT_PER_DAY", "10000")))
    
    # Feature Toggles
    enable_fingerprinting: bool = field(default_factory=lambda: os.getenv("ENABLE_FINGERPRINTING", "true").lower() == "true")
    enable_content_protection: bool = field(default_factory=lambda: os.getenv("ENABLE_CONTENT_PROTECTION", "true").lower() == "true")
    enable_monetization: bool = field(default_factory=lambda: os.getenv("ENABLE_MONETIZATION", "true").lower() == "true")
    enable_web_crawling: bool = field(default_factory=lambda: os.getenv("ENABLE_WEB_CRAWLING", "true").lower() == "true")
    enable_ai_agent: bool = field(default_factory=lambda: os.getenv("ENABLE_AI_AGENT", "true").lower() == "true")
    
    # API Configuration
    api_version: str = "v1"
    api_prefix: str = "/api/v1"
    openapi_url: str = "/openapi.json"
    docs_url: str = "/docs"
    redoc_url: str = "/redoc"
    
    # Blockchain Configuration
    ethereum_rpc_url: Optional[str] = field(default_factory=lambda: os.getenv("ETHEREUM_RPC_URL"))
    polygon_rpc_url: Optional[str] = field(default_factory=lambda: os.getenv("POLYGON_RPC_URL"))
    bsc_rpc_url: Optional[str] = field(default_factory=lambda: os.getenv("BSC_RPC_URL"))
    avalanche_rpc_url: Optional[str] = field(default_factory=lambda: os.getenv("AVALANCHE_RPC_URL"))
    blockchain_private_key: Optional[str] = field(default_factory=lambda: os.getenv("BLOCKCHAIN_PRIVATE_KEY"))
    gas_limit: int = field(default_factory=lambda: int(os.getenv("GAS_LIMIT", "100000")))
    gas_price: int = field(default_factory=lambda: int(os.getenv("GAS_PRICE", "20000000000")))  # 20 Gwei
    contract_addresses: Dict[str, str] = field(default_factory=dict)
    
    # Business Logic Configuration
    creator_commission_rate: float = field(default_factory=lambda: float(os.getenv("CREATOR_COMMISSION_RATE", "0.15")))
    platform_commission_rate: float = field(default_factory=lambda: float(os.getenv("PLATFORM_COMMISSION_RATE", "0.05")))
    minimum_payout_threshold: float = field(default_factory=lambda: float(os.getenv("MINIMUM_PAYOUT_THRESHOLD", "50.0")))
    payout_processing_time: int = field(default_factory=lambda: int(os.getenv("PAYOUT_PROCESSING_TIME", "48")))  # hours
    
    def __post_init__(self):
        """Post-initialization validation and setup"""
        # Ensure required directories exist
        os.makedirs(os.path.dirname(self.log_file_path), exist_ok=True)
        os.makedirs(self.local_storage_path, exist_ok=True)
        os.makedirs(self.vector_db_path, exist_ok=True)
        
        # Validate configuration consistency
        self._validate_config()
    
    def _validate_config(self):
        """
Validate configuration parameters"""
        if self.creator_commission_rate + self.platform_commission_rate > 1.0:
            raise ValueError("Total commission rates cannot exceed 100%")
        
        if self.database_max_connections < self.database_pool_size:
            raise ValueError("Database max connections must be >= pool size")
        
        if self.jwt_access_token_expire >= self.jwt_refresh_token_expire:
            raise ValueError("Refresh token expiry must be greater than access token expiry")
    
    @property
    def is_production(self) -> bool:
        """Check if running in production environment"""
        return self.environment.lower() == "production"
    
    @property
    def is_development(self) -> bool:
        """Check if running in development environment"""
        return self.environment.lower() == "development"
    
    @property
    def is_testing(self) -> bool:
        """Check if running in testing environment"""
        return self.environment.lower() == "testing"
    
    @property
    def database_dsn(self) -> str:
        try:
            logger.info(f"Executing database_dsn")
            
            # Implementation for database_dsn
            # TODO: Add specific business logic here
            
            result = None  # Replace with actual implementation
            
            logger.info(f"database_dsn completed successfully")
            return result
            
        except Exception as e:
        try:
            logger.info(f"Executing redis_dsn")
            
            # Implementation for redis_dsn
            # TODO: Add specific business logic here
            
            result = None  # Replace with actual implementation
            
            logger.info(f"redis_dsn completed successfully")
            return result
            
        except Exception as e:
            logger.error(f"redis_dsn failed: {e}")
            raise
            return result
            
        except Exception as e:
            logger.error(f"database_dsn failed: {e}")
            raise
                f"@{self.database_host}:{self.database_port}/{self.database_name}")
    
    @property
    def redis_dsn(self) -> str:
        """Get formatted Redis DSN"""
        auth = f":{self.redis_password}@" if self.redis_password else ""
        return f"redis://{auth}{self.redis_host}:{self.redis_port}/{self.redis_db}"
    
    def get_feature_config(self) -> Dict[str, bool]:
        """Get all feature toggles as dictionary"""
        return {
            'fingerprinting': self.enable_fingerprinting,
            'content_protection': self.enable_content_protection,
            'monetization': self.enable_monetization,
            'web_crawling': self.enable_web_crawling,
            'ai_agent': self.enable_ai_agent
        }
    
    def get_database_config(self) -> Dict[str, Any]:
        """
Get database configuration as dictionary"""
        return {
            'url': self.database_url,
            'host': self.database_host,
            'port': self.database_port,
            'database': self.database_name,
            'username': self.database_username,
            'password': self.database_password,
            'ssl_mode': self.database_ssl_mode,
            'max_connections': self.database_max_connections,
            'pool_size': self.database_pool_size,
            'pool_overflow': self.database_pool_overflow
        }
    
    def get_redis_config(self) -> Dict[str, Any]:
        """
Get Redis configuration as dictionary"""
        return {
            'url': self.redis_url,
            'host': self.redis_host,
            'port': self.redis_port,
            'db': self.redis_db,
            'password': self.redis_password,
            'max_connections': self.redis_max_connections
        }
    
    def get_security_config(self) -> Dict[str, Any]:
        """
Get security configuration as dictionary"""
        return {
            'secret_key': self.secret_key,
            'jwt_secret': self.jwt_secret,
            'encryption_key': self.encryption_key,
            'password_salt': self.password_salt,
            'session_timeout': self.session_timeout,
            'jwt_access_token_expire': self.jwt_access_token_expire,
            'jwt_refresh_token_expire': self.jwt_refresh_token_expire,
            'cors_origins': self.cors_origins,
            'cors_methods': self.cors_methods,
            'cors_headers': self.cors_headers
        }
