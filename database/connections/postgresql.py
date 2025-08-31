"""PostgreSQL Connection Handler - IA Influencer Agent Platform

Manages PostgreSQL connections for primary relational data including:
- User accounts and authentication
- Content metadata and fingerprints
- Revenue tracking and payments
- Collaboration and distribution data
- Platform integrations and APIs

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.
"""import asyncio
import logging
from typing import Dict, Any, Optional, List, AsyncContextManager, Union
from contextlib import asynccontextmanager
from dataclasses import dataclass
from datetime import datetime, timedelta

import asyncpg
from asyncpg import Pool, Connection
from asyncpg.pool import PoolConnectionProxy

from ..encryption import DatabaseEncryption


@dataclass
class PostgreSQLConfig:
    """PostgreSQL connection configuration"""    host: str
    port: int = 5432
    database: str = "ia_influencer"
    username: str = "postgres"
    password: str = ""
    ssl_mode: str = "require"
    pool_min_size: int = 10
    pool_max_size: int = 50
    command_timeout: int = 60
    server_settings: Optional[Dict[str, str]] = None
    tenant_schema_prefix: str = "tenant_"


class PostgreSQLConnectionHandler:
    """    PostgreSQL connection handler for IA Influencer platform.
    
    Manages connections for:
    - Creator accounts and profiles
    - Content fingerprints and metadata
    - Protection alerts and monitoring
    - Revenue tracking and analytics
    - Collaboration matching
    - Platform API integrations
    """    
    def __init__(self, config: Dict[str, Any]):
        self.config = PostgreSQLConfig(**config)
        self.logger = logging.getLogger(__name__)
        
        self.pool: Optional[Pool] = None
        self.encryption = DatabaseEncryption()
        
        # Connection metrics
        self.connection_count = 0
        self.query_count = 0
        self.error_count = 0
        self.last_health_check = None
        
        # Tenant isolation
        self.tenant_pools: Dict[str, Pool] = {}
    
    async def initialize(self) -> None:
        """Initialize PostgreSQL connection pool"""        try:
            self.logger.info("Initializing PostgreSQL connection pool...")
            
            # Build connection string
            dsn = self._build_dsn()
            
            # Create main connection pool
            self.pool = await asyncpg.create_pool(
                dsn,
                min_size=self.config.pool_min_size,
                max_size=self.config.pool_max_size,
                command_timeout=self.config.command_timeout,
                server_settings=self.config.server_settings or {},
                init=self._init_connection
            )
            
            # Verify connection
            await self.health_check()
            
            self.logger.info("PostgreSQL connection pool initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize PostgreSQL pool: {e}")
            raise
    
    def _build_dsn(self) -> str:
        """Build PostgreSQL connection string"""        return (
            f"postgresql://{self.config.username}:"
            f"{self.config.password}@{self.config.host}:"
            f"{self.config.port}/{self.config.database}"
            f"?sslmode={self.config.ssl_mode}"
        )
    
    async def _init_connection(self, connection: Connection) -> None:
        """Initialize new database connection"""        # Set timezone
        await connection.execute("SET timezone = 'UTC'")
        
        # Set application name for monitoring
        await connection.execute("SET application_name = 'ia_influencer_agent'")
        
        # Enable UUID extension
        await connection.execute("CREATE EXTENSION IF NOT EXISTS \"uuid-ossp\"")
        
        # Enable trigram extension for text search
        await connection.execute("CREATE EXTENSION IF NOT EXISTS pg_trgm")
        
        # Enable btree_gin for advanced indexing
        await connection.execute("CREATE EXTENSION IF NOT EXISTS btree_gin")
    
    async def get_connection(self) -> PoolConnectionProxy:
        """Get a connection from the pool"""        if not self.pool:
            raise RuntimeError("PostgreSQL pool not initialized")
        
        connection = await self.pool.acquire()
        self.connection_count += 1
        return connection
    
    async def release_connection(self, connection: PoolConnectionProxy) -> None:
        """Release a connection back to the pool"""        if self.pool:
            await self.pool.release(connection)
    
    @asynccontextmanager
    async def connection(self) -> AsyncContextManager[PoolConnectionProxy]:
        """Context manager for database connections"""        conn = await self.get_connection()
        try:
            yield conn
        finally:
            await self.release_connection(conn)
    
    @asynccontextmanager
    async def transaction(self) -> AsyncContextManager[PoolConnectionProxy]:
        """Context manager for database transactions"""        async with self.connection() as conn:
            async with conn.transaction():
                yield conn
    
    async def execute(self, 
                     query: str, 
                     *args, 
                     connection: Optional[PoolConnectionProxy] = None) -> Any:
        """Execute a query"""        try:
            if connection:
                result = await connection.execute(query, *args)
            else:
                async with self.connection() as conn:
                    result = await conn.execute(query, *args)
            
            self.query_count += 1
            return result
            
        except Exception as e:
            self.error_count += 1
            self.logger.error(f"Query execution failed: {e}")
            raise
    
    async def fetch(self, 
                   query: str, 
                   *args, 
                   connection: Optional[PoolConnectionProxy] = None) -> List[Dict]:
        """Fetch query results"""        try:
            if connection:
                result = await connection.fetch(query, *args)
            else:
                async with self.connection() as conn:
                    result = await conn.fetch(query, *args)
            
            self.query_count += 1
            return [dict(row) for row in result]
            
        except Exception as e:
            self.error_count += 1
            self.logger.error(f"Query fetch failed: {e}")
            raise
    
    async def fetchrow(self, 
                      query: str, 
                      *args, 
                      connection: Optional[PoolConnectionProxy] = None) -> Optional[Dict]:
        """Fetch single row"""        try:
            if connection:
                result = await connection.fetchrow(query, *args)
            else:
                async with self.connection() as conn:
                    result = await conn.fetchrow(query, *args)
            
            self.query_count += 1
            return dict(result) if result else None
            
        except Exception as e:
            self.error_count += 1
            self.logger.error(f"Query fetchrow failed: {e}")
            raise
    
    async def fetchval(self, 
                      query: str, 
                      *args, 
                      connection: Optional[PoolConnectionProxy] = None) -> Any:
        """Fetch single value"""        try:
            if connection:
                result = await connection.fetchval(query, *args)
            else:
                async with self.connection() as conn:
                    result = await conn.fetchval(query, *args)
            
            self.query_count += 1
            return result
            
        except Exception as e:
            self.error_count += 1
            self.logger.error(f"Query fetchval failed: {e}")
            raise
    
    async def get_tenant_connection(self, tenant_id: str) -> PoolConnectionProxy:
        """Get tenant-specific connection with schema isolation"""        if tenant_id not in self.tenant_pools:
            await self._create_tenant_pool(tenant_id)
        
        pool = self.tenant_pools[tenant_id]
        connection = await pool.acquire()
        
        # Set search path to tenant schema
        schema_name = f"{self.config.tenant_schema_prefix}{tenant_id}"
        await connection.execute(f"SET search_path TO {schema_name}, public")
        
        return connection
    
    async def _create_tenant_pool(self, tenant_id: str) -> None:
        """Create connection pool for specific tenant"""        dsn = self._build_dsn()
        
        pool = await asyncpg.create_pool(
            dsn,
            min_size=max(2, self.config.pool_min_size // 10),
            max_size=max(5, self.config.pool_max_size // 10),
            command_timeout=self.config.command_timeout,
            init=lambda conn: self._init_tenant_connection(conn, tenant_id)
        )
        
        self.tenant_pools[tenant_id] = pool
    
    async def _init_tenant_connection(self, connection: Connection, tenant_id: str) -> None:
        """Initialize tenant-specific connection"""        await self._init_connection(connection)
        
        # Create tenant schema if not exists
        schema_name = f"{self.config.tenant_schema_prefix}{tenant_id}"
        await connection.execute(f"CREATE SCHEMA IF NOT EXISTS {schema_name}")
        
        # Set default search path
        await connection.execute(f"SET search_path TO {schema_name}, public")
    
    async def health_check(self) -> Dict[str, Any]:
        """Check PostgreSQL connection health"""        try:
            start_time = datetime.utcnow()
            
            async with self.connection() as conn:
                # Test basic connectivity
                await conn.fetchval("SELECT 1")
                
                # Check database stats
                stats = await conn.fetchrow("""                    SELECT 
                        count(*) as total_connections,
                        count(*) FILTER (WHERE state = 'active') as active_connections,
                        count(*) FILTER (WHERE state = 'idle') as idle_connections
                    FROM pg_stat_activity 
                    WHERE datname = current_database()
                """)
                
                # Check table sizes
                table_stats = await conn.fetch("""                    SELECT 
                        schemaname,
                        tablename,
                        n_tup_ins as inserts,
                        n_tup_upd as updates,
                        n_tup_del as deletes
                    FROM pg_stat_user_tables
                    ORDER BY n_tup_ins + n_tup_upd + n_tup_del DESC
                    LIMIT 10
                """)
            
            response_time = (datetime.utcnow() - start_time).total_seconds()
            self.last_health_check = datetime.utcnow()
            
            return {
                "status": "healthy",
                "response_time": response_time,
                "database": self.config.database,
                "pool_size": self.pool.get_size() if self.pool else 0,
                "pool_idle": self.pool.get_idle_size() if self.pool else 0,
                "connection_stats": dict(stats) if stats else {},
                "table_stats": [dict(row) for row in table_stats],
                "metrics": {
                    "total_connections": self.connection_count,
                    "total_queries": self.query_count,
                    "total_errors": self.error_count
                },
                "last_check": self.last_health_check.isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"PostgreSQL health check failed: {e}")
            return {
                "status": "unhealthy",
                "error": str(e),
                "last_check": datetime.utcnow().isoformat()
            }
    
    async def get_metrics(self) -> Dict[str, Any]:
        """Get detailed PostgreSQL metrics"""        if not self.pool:
            return {"status": "not_initialized"}
        
        try:
            async with self.connection() as conn:
                # Database size
                db_size = await conn.fetchval("""                    SELECT pg_size_pretty(pg_database_size(current_database()))
                """)
                
                # Connection statistics
                conn_stats = await conn.fetchrow("""                    SELECT 
                        max_conn,
                        used,
                        res_for_super,
                        max_conn - used - res_for_super as available
                    FROM (
                        SELECT 
                            setting::int as max_conn,
                            count(*) as used,
                            setting::int as res_for_super
                        FROM pg_settings, pg_stat_activity 
                        WHERE name = 'max_connections'
                        GROUP BY setting
                    ) q, (
                        SELECT setting::int as res_for_super 
                        FROM pg_settings 
                        WHERE name = 'superuser_reserved_connections'
                    ) r
                """)
                
                # Query performance stats
                query_stats = await conn.fetch("""                    SELECT 
                        query,
                        calls,
                        total_time,
                        mean_time,
                        rows
                    FROM pg_stat_statements 
                    ORDER BY total_time DESC 
                    LIMIT 10
                """)
                
                return {
                    "database_size": db_size,
                    "pool_size": self.pool.get_size(),
                    "pool_idle": self.pool.get_idle_size(),
                    "connection_stats": dict(conn_stats) if conn_stats else {},
                    "query_performance": [dict(row) for row in query_stats],
                    "tenant_pools": len(self.tenant_pools),
                    "metrics": {
                        "connection_count": self.connection_count,
                        "query_count": self.query_count,
                        "error_count": self.error_count
                    }
                }
                
        except Exception as e:
            self.logger.error(f"Failed to get PostgreSQL metrics: {e}")
            return {"error": str(e)}
    
    async def shutdown(self) -> None:
        """Shutdown PostgreSQL connections"""        self.logger.info("Shutting down PostgreSQL connections...")
        
        # Close tenant pools
        for tenant_id, pool in self.tenant_pools.items():
            await pool.close()
            self.logger.info(f"Closed tenant pool for {tenant_id}")
        
        # Close main pool
        if self.pool:
            await self.pool.close()
            self.logger.info("Closed main PostgreSQL pool")
        
        self.pool = None
        self.tenant_pools.clear()
        
        self.logger.info("PostgreSQL connections shutdown completed")
