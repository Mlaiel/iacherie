"""Production Connection Pool Configuration

This module provides production-grade connection pooling configuration
that acts as a pgbouncer equivalent with advanced features.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel - All Rights Reserved
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, field
from enum import Enum
import json
import time
from datetime import datetime, timedelta
import asyncpg
from sqlalchemy.ext.asyncio import create_async_engine, AsyncEngine
from sqlalchemy import pool
import os

logger = logging.getLogger(__name__)

class PoolMode(str, Enum):
    """Connection pool modes (similar to pgbouncer)."""
    SESSION = "session"          # One connection per session
    TRANSACTION = "transaction"  # Connection released after transaction
    STATEMENT = "statement"      # Connection released after statement

@dataclass
class ProductionPoolConfig:
    """Production connection pool configuration."""
    # Pool sizing
    pool_size: int = 25
    max_overflow: int = 25
    
    # Connection management
    pool_timeout: int = 30
    pool_recycle: int = 3600
    pool_pre_ping: bool = True
    
    # Production-specific settings
    pool_mode: PoolMode = PoolMode.TRANSACTION
    default_pool_size: int = 20
    max_client_conn: int = 1000
    reserve_pool_size: int = 5
    
    # SSL and security
    ssl_mode: str = "require"
    ssl_cert_path: Optional[str] = None
    ssl_key_path: Optional[str] = None
    ssl_ca_path: Optional[str] = None
    
    # Monitoring and stats
    stats_period: int = 60
    log_connections: bool = True
    log_disconnections: bool = True
    log_pooler_errors: bool = True
    
    # Performance tuning
    server_round_robin: bool = True
    ignore_startup_parameters: str = "extra_float_digits,search_path"
    
    # Timeouts
    server_idle_timeout: int = 600
    server_connect_timeout: int = 15
    server_login_retry: int = 15
    client_idle_timeout: int = 0
    
    # Load balancing
    enable_load_balancing: bool = True
    read_replica_hosts: List[str] = field(default_factory=list)
    write_host: str = "localhost"

class ProductionConnectionPool:
    """Production-grade connection pool manager."""
    
    def __init__(self, config: ProductionPoolConfig):
        self.config = config
        self.engines: Dict[str, AsyncEngine] = {}
        self.stats: Dict[str, Any] = {}
        self.is_monitoring = False
        self._monitor_task: Optional[asyncio.Task] = None
    
    def _get_database_url(self, host: str, read_only: bool = False) -> str:
        """Get database URL with production settings."""
        base_url = "postgresql+asyncpg://{user}:{password}@{host}:{port}/{database}".format(
            user=os.getenv('POSTGRES_USER_PRODUCTION', 'ainflue_user'),
            password=os.getenv('POSTGRES_PASSWORD_PRODUCTION', ''),
            host=host,
            port=os.getenv('POSTGRES_PORT_PRODUCTION', '5432'),
            database=os.getenv('POSTGRES_DB_PRODUCTION', 'ainflue_production'),
        )
        
        # Add SSL parameters
        ssl_params = []
        if self.config.ssl_mode:
            ssl_params.append(f"sslmode={self.config.ssl_mode}")
        if self.config.ssl_cert_path:
            ssl_params.append(f"sslcert={self.config.ssl_cert_path}")
        if self.config.ssl_key_path:
            ssl_params.append(f"sslkey={self.config.ssl_key_path}")
        if self.config.ssl_ca_path:
            ssl_params.append(f"sslrootcert={self.config.ssl_ca_path}")
        
        # Add read-only parameter for replicas
        if read_only:
            ssl_params.append("default_transaction_read_only=on")
        
        if ssl_params:
            base_url += "?" + "&".join(ssl_params)
        
        return base_url
    
    async def initialize(self):
        """Initialize connection pools."""
        logger.info("Initializing production connection pools...")
        
        # Create write engine
        write_url = self._get_database_url(self.config.write_host)
        self.engines['write'] = create_async_engine(
            write_url,
            pool_size=self.config.pool_size,
            max_overflow=self.config.max_overflow,
            pool_timeout=self.config.pool_timeout,
            pool_recycle=self.config.pool_recycle,
            pool_pre_ping=self.config.pool_pre_ping,
            poolclass=pool.QueuePool,
            connect_args={
                "server_settings": {
                    "application_name": "ainflue_production_write",
                    "tcp_keepalives_idle": "300",
                    "tcp_keepalives_interval": "30",
                    "tcp_keepalives_count": "3"
                }
            }
        )
        
        # Create read engines for load balancing
        for i, replica_host in enumerate(self.config.read_replica_hosts):
            replica_url = self._get_database_url(replica_host, read_only=True)
            engine_name = f'read_{i}'
            
            self.engines[engine_name] = create_async_engine(
                replica_url,
                pool_size=self.config.pool_size // 2,  # Smaller pools for read replicas
                max_overflow=self.config.max_overflow // 2,
                pool_timeout=self.config.pool_timeout,
                pool_recycle=self.config.pool_recycle,
                pool_pre_ping=self.config.pool_pre_ping,
                poolclass=pool.QueuePool,
                connect_args={
                    "server_settings": {
                        "application_name": f"ainflue_production_read_{i}",
                        "default_transaction_read_only": "on",
                        "tcp_keepalives_idle": "300",
                        "tcp_keepalives_interval": "30",
                        "tcp_keepalives_count": "3"
                    }
                }
            )
        
        # If no read replicas, use write engine for reads
        if not self.config.read_replica_hosts:
            self.engines['read_0'] = self.engines['write']
        
        # Initialize statistics
        self.stats = {
            'connections_created': 0,
            'connections_closed': 0,
            'active_connections': 0,
            'pool_size': self.config.pool_size,
            'queries_executed': 0,
            'avg_query_time': 0.0,
            'start_time': datetime.utcnow()
        }
        
        # Start monitoring
        await self.start_monitoring()
        
        logger.info(f"Initialized {len(self.engines)} connection pools")
    
    def get_engine(self, operation_type: str = 'read') -> AsyncEngine:
        """Get appropriate engine based on operation type."""
        if operation_type in ('write', 'insert', 'update', 'delete'):
            return self.engines['write']
        
        # Load balance read operations
        read_engines = [name for name in self.engines.keys() if name.startswith('read_')]
        if not read_engines:
            return self.engines['write']
        
        if self.config.server_round_robin:
            # Round-robin load balancing
            current_time = int(time.time())
            selected_index = current_time % len(read_engines)
            selected_engine = read_engines[selected_index]
        else:
            # Always use first read replica
            selected_engine = read_engines[0]
        
        return self.engines[selected_engine]
    
    async def execute_query(self, query: str, params: Optional[Dict] = None, 
                          operation_type: str = 'read') -> Any:
        """Execute query with automatic engine selection."""
        engine = self.get_engine(operation_type)
        start_time = time.time()
        
        try:
            async with engine.begin() as conn:
                if params:
                    result = await conn.execute(query, params)
                else:
                    result = await conn.execute(query)
                
                # Update statistics
                execution_time = time.time() - start_time
                self.stats['queries_executed'] += 1
                
                # Update average query time
                current_avg = self.stats['avg_query_time']
                query_count = self.stats['queries_executed']
                self.stats['avg_query_time'] = (current_avg * (query_count - 1) + execution_time) / query_count
                
                return result
                
        except Exception as e:
            logger.error(f"Query execution failed: {e}")
            raise
    
    async def get_connection(self, operation_type: str = 'read'):
        """Get a connection from the appropriate pool."""
        engine = self.get_engine(operation_type)
        return engine.connect()
    
    async def start_monitoring(self):
        """Start connection pool monitoring."""
        if self.is_monitoring:
            return
        
        self.is_monitoring = True
        self._monitor_task = asyncio.create_task(self._monitor_pools())
        logger.info("Started connection pool monitoring")
    
    async def stop_monitoring(self):
        """Stop connection pool monitoring."""
        self.is_monitoring = False
        if self._monitor_task:
            self._monitor_task.cancel()
            try:
                await self._monitor_task
            except asyncio.CancelledError:
                pass
        logger.info("Stopped connection pool monitoring")
    
    async def _monitor_pools(self):
        """Monitor connection pools and log statistics."""
        while self.is_monitoring:
            try:
                # Collect pool statistics
                for engine_name, engine in self.engines.items():
                    pool = engine.pool
                    
                    pool_stats = {
                        'engine': engine_name,
                        'pool_size': pool.size(),
                        'checked_in': pool.checkedin(),
                        'checked_out': pool.checkedout(),
                        'overflow': pool.overflow(),
                        'invalid': pool.invalid(),
                        'timestamp': datetime.utcnow().isoformat()
                    }
                    
                    if self.config.log_connections:
                        logger.info(f"Pool stats: {json.dumps(pool_stats)}")
                
                # Log overall statistics
                overall_stats = {
                    **self.stats,
                    'uptime_seconds': (datetime.utcnow() - self.stats['start_time']).total_seconds(),
                    'timestamp': datetime.utcnow().isoformat()
                }
                
                logger.info(f"Overall stats: {json.dumps(overall_stats, default=str)}")
                
                await asyncio.sleep(self.config.stats_period)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Monitoring error: {e}")
                await asyncio.sleep(self.config.stats_period)
    
    async def health_check(self) -> Dict[str, Any]:
        """Perform health check on all pools."""
        health_status = {
            'timestamp': datetime.utcnow().isoformat(),
            'overall_healthy': True,
            'engines': {}
        }
        
        for engine_name, engine in self.engines.items():
            try:
                async with engine.connect() as conn:
                    await conn.execute("SELECT 1")
                
                pool = engine.pool
                engine_health = {
                    'healthy': True,
                    'pool_size': pool.size(),
                    'checked_out': pool.checkedout(),
                    'overflow': pool.overflow(),
                    'response_time_ms': 0  # Could measure actual response time
                }
                
            except Exception as e:
                engine_health = {
                    'healthy': False,
                    'error': str(e)
                }
                health_status['overall_healthy'] = False
            
            health_status['engines'][engine_name] = engine_health
        
        return health_status
    
    async def get_statistics(self) -> Dict[str, Any]:
        """Get comprehensive pool statistics."""
        pool_stats = {}
        
        for engine_name, engine in self.engines.items():
            pool = engine.pool
            pool_stats[engine_name] = {
                'pool_size': pool.size(),
                'checked_in': pool.checkedin(),
                'checked_out': pool.checkedout(),
                'overflow': pool.overflow(),
                'invalid': pool.invalid()
            }
        
        return {
            'pool_statistics': pool_stats,
            'overall_statistics': self.stats,
            'configuration': {
                'pool_size': self.config.pool_size,
                'max_overflow': self.config.max_overflow,
                'pool_mode': self.config.pool_mode,
                'ssl_mode': self.config.ssl_mode
            },
            'timestamp': datetime.utcnow().isoformat()
        }
    
    async def close(self):
        """Close all connection pools."""
        await self.stop_monitoring()
        
        for engine_name, engine in self.engines.items():
            logger.info(f"Closing engine: {engine_name}")
            await engine.dispose()
        
        self.engines.clear()
        logger.info("All connection pools closed")

# Global production pool instance
_production_pool: Optional[ProductionConnectionPool] = None

async def get_production_pool() -> ProductionConnectionPool:
    """Get or create production connection pool."""
    global _production_pool
    
    if _production_pool is None:
        config = ProductionPoolConfig(
            write_host=os.getenv('POSTGRES_HOST_PRODUCTION', 'localhost'),
            read_replica_hosts=os.getenv('POSTGRES_READ_REPLICAS', '').split(',') if os.getenv('POSTGRES_READ_REPLICAS') else [],
            pool_size=int(os.getenv('POSTGRES_POOL_SIZE', '25')),
            max_overflow=int(os.getenv('POSTGRES_MAX_OVERFLOW', '25')),
            ssl_mode=os.getenv('POSTGRES_SSL_MODE', 'require')
        )
        
        _production_pool = ProductionConnectionPool(config)
        await _production_pool.initialize()
    
    return _production_pool

async def close_production_pool():
    """Close production connection pool."""
    global _production_pool
    
    if _production_pool:
        await _production_pool.close()
        _production_pool = None