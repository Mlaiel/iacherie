"""PostgreSQL Configuration Module for IA-Influencer Agent Platform
===============================================================

Professional PostgreSQL database configuration for multi-tenant content protection,
monetization tracking, and AI agent analytics.

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
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from enum import Enum
from sqlalchemy import create_engine, pool
from sqlalchemy.engine import Engine
from sqlalchemy.pool import QueuePool
from cryptography.fernet import Fernet
import logging

logger = logging.getLogger(__name__)


class PostgreSQLEnvironment(Enum):
    """PostgreSQL environment configurations"""
    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"
    TESTING = "testing"


class ConnectionPoolStrategy(Enum):
    """Connection pool strategies for different workloads"""
    HIGH_PERFORMANCE = "high_performance"
    BALANCED = "balanced"
    MEMORY_OPTIMIZED = "memory_optimized"
    ANALYTICS_HEAVY = "analytics_heavy"


@dataclass
class PostgreSQLCredentials:
    """Encrypted PostgreSQL credentials management"""
    host: str
    port: int
    database: str
    username: str
    password_encrypted: str
    encryption_key: str
    ssl_mode: str = "require"
    ssl_cert_path: Optional[str] = None
    ssl_key_path: Optional[str] = None
    ssl_ca_path: Optional[str] = None

    def get_decrypted_password(self) -> str:
        """Decrypt password using encryption key"""
        try:
            fernet = Fernet(self.encryption_key.encode())
            return fernet.decrypt(self.password_encrypted.encode()).decode()
        except Exception as e:
            logger.error(f"Password decryption failed: {str(e)}")
            raise


@dataclass
class PostgreSQLPoolConfig:
    """PostgreSQL connection pool configuration"""
    pool_size: int = 20
    max_overflow: int = 30
    pool_timeout: int = 30
    pool_recycle: int = 3600
    pool_pre_ping: bool = True
    pool_reset_on_return: str = "commit"
    echo: bool = False
    echo_pool: bool = False


@dataclass
class PostgreSQLPerformanceConfig:
    """PostgreSQL performance optimization settings"""
    work_mem: str = "4MB"
    maintenance_work_mem: str = "64MB"
    shared_buffers: str = "256MB"
    effective_cache_size: str = "1GB"
    random_page_cost: float = 1.1
    seq_page_cost: float = 1.0
    cpu_tuple_cost: float = 0.01
    cpu_index_tuple_cost: float = 0.005
    cpu_operator_cost: float = 0.0025
    effective_io_concurrency: int = 200
    wal_buffers: str = "16MB"
    checkpoint_completion_target: float = 0.7
    max_connections: int = 100
    shared_preload_libraries: List[str] = field(default_factory=lambda: ["pg_stat_statements", "auto_explain"])


@dataclass
class PostgreSQLSecurityConfig:
    """PostgreSQL security configuration"""
    row_security: bool = True
    force_ssl: bool = True
    audit_logging: bool = True
    log_connections: bool = True
    log_disconnections: bool = True
    log_statement: str = "all"
    log_min_duration_statement: int = 1000
    password_encryption: str = "scram-sha-256"
    idle_in_transaction_session_timeout: int = 300000
    statement_timeout: int = 0
    lock_timeout: int = 30000


class PostgreSQLConfig:
    """
    Professional PostgreSQL configuration manager for IA-Influencer Agent Platform
    
    Handles multi-tenant database configuration, connection pooling, security,
    and performance optimization for content protection and monetization workflows.
    """
    def __init__(self, environment: PostgreSQLEnvironment = PostgreSQLEnvironment.DEVELOPMENT):
        self.environment = environment
        self.credentials = self._load_credentials()
        self.pool_config = self._get_pool_config()
        self.performance_config = self._get_performance_config()
        self.security_config = self._get_security_config()
        self._engines: Dict[str, Engine] = {}
        self._setup_logging()

    def _setup_logging(self) -> None:
        """Setup PostgreSQL-specific logging"""
        self.logger = logging.getLogger(f"postgresql.{self.environment.value}")
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
            self.logger.setLevel(logging.INFO)

    def _load_credentials(self) -> PostgreSQLCredentials:
        """Load PostgreSQL credentials from environment"""
        return PostgreSQLCredentials(
            host=os.getenv(f"POSTGRES_HOST_{self.environment.value.upper()}", "localhost"),
            port=int(os.getenv(f"POSTGRES_PORT_{self.environment.value.upper()}", "5432")),
            database=os.getenv(f"POSTGRES_DB_{self.environment.value.upper()}", "ia_influencer_agent"),
            username=os.getenv(f"POSTGRES_USER_{self.environment.value.upper()}", "postgres"),
            password_encrypted=os.getenv(f"POSTGRES_PASSWORD_ENCRYPTED_{self.environment.value.upper()}", ""),
            encryption_key=os.getenv("POSTGRES_ENCRYPTION_KEY", ""),
            ssl_mode=os.getenv(f"POSTGRES_SSL_MODE_{self.environment.value.upper()}", "require"),
            ssl_cert_path=os.getenv(f"POSTGRES_SSL_CERT_{self.environment.value.upper()}"),
            ssl_key_path=os.getenv(f"POSTGRES_SSL_KEY_{self.environment.value.upper()}"),
            ssl_ca_path=os.getenv(f"POSTGRES_SSL_CA_{self.environment.value.upper()}")
        )

    def _get_pool_config(self) -> PostgreSQLPoolConfig:
        """Get connection pool configuration based on environment"""
        pool_configs = {
            PostgreSQLEnvironment.DEVELOPMENT: PostgreSQLPoolConfig(
                pool_size=5, max_overflow=10, echo=True
            ),
            PostgreSQLEnvironment.STAGING: PostgreSQLPoolConfig(
                pool_size=10, max_overflow=20
            ),
            PostgreSQLEnvironment.PRODUCTION: PostgreSQLPoolConfig(
                pool_size=20, max_overflow=30, pool_timeout=60
            ),
            PostgreSQLEnvironment.TESTING: PostgreSQLPoolConfig(
                pool_size=2, max_overflow=5, echo=True
            )
        }
        return pool_configs.get(self.environment, PostgreSQLPoolConfig())

    def _get_performance_config(self) -> PostgreSQLPerformanceConfig:
        """Get performance configuration based on environment"""
        if self.environment == PostgreSQLEnvironment.PRODUCTION:
            return PostgreSQLPerformanceConfig(
                work_mem="8MB",
                maintenance_work_mem="128MB",
                shared_buffers="512MB",
                effective_cache_size="4GB",
                max_connections=200
            )
        elif self.environment == PostgreSQLEnvironment.STAGING:
            return PostgreSQLPerformanceConfig(
                work_mem="6MB",
                maintenance_work_mem="96MB",
                shared_buffers="384MB",
                effective_cache_size="2GB",
                max_connections=150
            )
        else:
            return PostgreSQLPerformanceConfig()

    def _get_security_config(self) -> PostgreSQLSecurityConfig:
        """Get security configuration based on environment"""
        if self.environment == PostgreSQLEnvironment.PRODUCTION:
            return PostgreSQLSecurityConfig(
                row_security=True,
                force_ssl=True,
                audit_logging=True,
                log_min_duration_statement=500
            )
        elif self.environment == PostgreSQLEnvironment.DEVELOPMENT:
            return PostgreSQLSecurityConfig(
                row_security=False,
                force_ssl=False,
                audit_logging=False,
                log_statement="mod"
            )
        else:
            return PostgreSQLSecurityConfig()

    def get_connection_url(self, database_name: Optional[str] = None) -> str:
        """
        Generate PostgreSQL connection URL with security parameters
        
        Args:
            database_name: Optional specific database name
            
        Returns:
            Secure PostgreSQL connection URL
        """
        try:
            password = self.credentials.get_decrypted_password()
            db_name = database_name or self.credentials.database
            
            base_url = (
                f"postgresql://{self.credentials.username}:{password}@"
                f"{self.credentials.host}:{self.credentials.port}/{db_name}"
            )
            
            # Add SSL parameters
            ssl_params = []
            ssl_params.append(f"sslmode={self.credentials.ssl_mode}")
            
            if self.credentials.ssl_cert_path:
                ssl_params.append(f"sslcert={self.credentials.ssl_cert_path}")
            if self.credentials.ssl_key_path:
                ssl_params.append(f"sslkey={self.credentials.ssl_key_path}")
            if self.credentials.ssl_ca_path:
                ssl_params.append(f"sslrootcert={self.credentials.ssl_ca_path}")
            
            if ssl_params:
                base_url += "?" + "&".join(ssl_params)
            
            return base_url
        except Exception as e:
            self.logger.error(f"Failed to generate connection URL: {str(e)}")
            raise

    def create_engine(self, database_name: Optional[str] = None, **kwargs) -> Engine:
        """
        Create SQLAlchemy engine with optimized configuration
        
        Args:
            database_name: Optional specific database name
            **kwargs: Additional engine parameters
            
        Returns:
            Configured SQLAlchemy engine
        """
        engine_key = database_name or "default"
        
        if engine_key in self._engines:
            return self._engines[engine_key]
        
        try:
            connection_url = self.get_connection_url(database_name)
            
            engine_config = {
                "poolclass": QueuePool,
                "pool_size": self.pool_config.pool_size,
                "max_overflow": self.pool_config.max_overflow,
                "pool_timeout": self.pool_config.pool_timeout,
                "pool_recycle": self.pool_config.pool_recycle,
                "pool_pre_ping": self.pool_config.pool_pre_ping,
                "pool_reset_on_return": self.pool_config.pool_reset_on_return,
                "echo": self.pool_config.echo,
                "echo_pool": self.pool_config.echo_pool,
                "connect_args": {
                    "options": f"-c work_mem={self.performance_config.work_mem}"
                },
                **kwargs
            }
            
            engine = create_engine(connection_url, **engine_config)
            self._engines[engine_key] = engine
            
            self.logger.info(f"PostgreSQL engine created successfully for {engine_key}")
            return engine
            
        except Exception as e:
            self.logger.error(f"Failed to create PostgreSQL engine: {str(e)}")
            raise

    def get_tenant_engine(self, tenant_id: str) -> Engine:
        """
        Get or create tenant-specific database engine
        
        Args:
            tenant_id: Unique tenant identifier
            
        Returns:
            Tenant-specific SQLAlchemy engine
        """
        tenant_db_name = f"{self.credentials.database}_tenant_{tenant_id}"
        return self.create_engine(tenant_db_name)

    def get_analytics_engine(self) -> Engine:
        """Get analytics-optimized database engine"""
        analytics_db_name = f"{self.credentials.database}_analytics"
        
        # Analytics-specific configuration
        analytics_config = {
            "pool_size": self.pool_config.pool_size * 2,
            "connect_args": {
                "options": f"-c work_mem={self.performance_config.work_mem} "
                          f"-c maintenance_work_mem={self.performance_config.maintenance_work_mem}"
            }
        }
        
        return self.create_engine(analytics_db_name, **analytics_config)

    def get_content_protection_engine(self) -> Engine:
        """Get content protection database engine with security focus"""
        protection_db_name = f"{self.credentials.database}_content_protection"
        
        # Security-focused configuration
        protection_config = {
            "connect_args": {
                "options": f"-c row_security={'on' if self.security_config.row_security else 'off'} "
                          f"-c log_statement={self.security_config.log_statement}"
            }
        }
        
        return self.create_engine(protection_db_name, **protection_config)

    def get_monetization_engine(self) -> Engine:
        """Get monetization tracking database engine"""
        monetization_db_name = f"{self.credentials.database}_monetization"
        return self.create_engine(monetization_db_name)

    def health_check(self) -> Dict[str, Any]:
        """
        Perform comprehensive health check on PostgreSQL connections
        
        Returns:
            Health check results dictionary
        """
        health_status = {
            "status": "healthy",
            "environment": self.environment.value,
            "engines": {},
            "timestamp": None
        }
        
        import datetime
        health_status["timestamp"] = datetime.datetime.utcnow().isoformat()
        
        try:
            # Test main engine
            main_engine = self.create_engine()
            with main_engine.connect() as conn:
                result = conn.execute("SELECT 1 as test, version() as pg_version")
                row = result.fetchone()
                health_status["engines"]["main"] = {
                    "status": "healthy",
                    "pg_version": row[1] if row else "unknown",
                    "pool_size": main_engine.pool.size(),
                    "checked_in": main_engine.pool.checkedin(),
                    "checked_out": main_engine.pool.checkedout(),
                    "overflow": main_engine.pool.overflow(),
                }
            
        except Exception as e:
            health_status["status"] = "unhealthy"
            health_status["engines"]["main"] = {
                "status": "unhealthy",
                "error": str(e)
            }
            self.logger.error(f"PostgreSQL health check failed: {str(e)}")
        
        return health_status

    def close_all_connections(self) -> None:
        """Close all database connections and cleanup resources"""
        for engine_name, engine in self._engines.items():
            try:
                engine.dispose()
                self.logger.info(f"Closed PostgreSQL engine: {engine_name}")
            except Exception as e:
                self.logger.error(f"Error closing engine {engine_name}: {str(e)}")
        
        self._engines.clear()

    def __del__(self):
        """Cleanup on object destruction"""
        self.close_all_connections()
