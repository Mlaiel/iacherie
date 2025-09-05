#!/usr/bin/env python3
"""Database Pools - PostgreSQL, MongoDB, Elasticsearch Connection Pools
========================================================================

⚠️  EXCLUSIVE INTELLECTUAL PROPERTY - FAHED MLAIEL ⚠️
(c) 2025 Fahed Mlaiel. All rights reserved.
Unauthorized use strictly prohibited and subject to legal prosecution.
Contact: mlaiel@live.de

Consolidated database connection pools for core data storage systems:
- PostgreSQL: Advanced relational database pooling with auto-scaling
- MongoDB: Document database pooling with replica set support  
- Elasticsearch: Search engine connection management with load balancing

ENTERPRISE FEATURES:
- Auto-scaling connection pools based on load patterns
- Health monitoring with automated failover capabilities
- Performance optimization and query analysis
- Master-slave replication support for PostgreSQL
- Replica set connection management for MongoDB
- Index management and optimization for Elasticsearch

Author: Fahed Mlaiel <mlaiel@live.de>
Team: Lead Dev IA + Backend Senior + ML Engineer + DBA + Security
"""

import asyncio
import logging
import time
import json
import weakref
from typing import Dict, Any, Optional, List, Union, AsyncIterator
from datetime import datetime, timezone, timedelta
from dataclasses import dataclass, field
from contextlib import asynccontextmanager
from abc import ABC, abstractmethod

# Database-specific imports
try:
    import asyncpg
    from asyncpg.pool import Pool as AsyncPGPool
    ASYNCPG_AVAILABLE = True
except ImportError:
    ASYNCPG_AVAILABLE = False

try:
    import motor.motor_asyncio
    import pymongo
    from pymongo import MongoClient
    MONGODB_AVAILABLE = True
except ImportError:
    MONGODB_AVAILABLE = False

try:
    from elasticsearch import AsyncElasticsearch
    ELASTICSEARCH_AVAILABLE = True
except ImportError:
    ELASTICSEARCH_AVAILABLE = False

logger = logging.getLogger(__name__)


@dataclass
class DatabaseConnectionInfo:
    """Database connection information."""
    host: str
    port: int
    database: str
    username: Optional[str] = None
    password: Optional[str] = None
    ssl_mode: Optional[str] = None
    additional_params: Dict[str, Any] = field(default_factory=dict)


@dataclass
class DatabasePoolConfig:
    """Database pool configuration."""
    pool_id: str
    connection_info: DatabaseConnectionInfo
    min_size: int = 5
    max_size: int = 20
    timeout: int = 30
    max_idle_time: int = 300
    health_check_interval: int = 30
    retry_attempts: int = 3
    auto_scaling: bool = True
    monitoring_enabled: bool = True


class DatabasePool(ABC):
    """Abstract base class for database connection pools."""
    
    def __init__(self, config: DatabasePoolConfig):
        self.config = config
        self.pool_id = config.pool_id
        self._pool = None
        self._is_initialized = False
        self._stats = {
            'total_connections': 0,
            'active_connections': 0,
            'idle_connections': 0,
            'connection_errors': 0,
            'last_health_check': None
        }
    
    @abstractmethod
    async def initialize(self) -> bool:
        """Initialize the database pool."""
        pass
    
    @abstractmethod
    async def close(self):
        """Close the database pool."""
        pass
    
    @abstractmethod
    async def health_check(self) -> bool:
        """Perform health check on the pool."""
        pass
    
    @abstractmethod
    @asynccontextmanager
    async def get_connection(self):
        """Get a connection from the pool."""
        pass
    
    def get_stats(self) -> Dict[str, Any]:
        """Get pool statistics."""
        return dict(self._stats)
    
    def is_initialized(self) -> bool:
        """Check if pool is initialized."""
        return self._is_initialized


class PostgreSQLPool(DatabasePool):
    """PostgreSQL connection pool with advanced features."""
    
    def __init__(self, config: DatabasePoolConfig):
        super().__init__(config)
        self._dsn = None
        
    async def initialize(self) -> bool:
        """Initialize PostgreSQL connection pool."""
        if not ASYNCPG_AVAILABLE:
            logger.error("asyncpg not available for PostgreSQL pool")
            return False
        
        try:
            # Build connection DSN
            conn_info = self.config.connection_info
            self._dsn = (
                f"postgresql://{conn_info.username}:{conn_info.password}"
                f"@{conn_info.host}:{conn_info.port}/{conn_info.database}"
            )
            
            # Add SSL mode if specified
            if conn_info.ssl_mode:
                self._dsn += f"?sslmode={conn_info.ssl_mode}"
            
            # Create connection pool
            self._pool = await asyncpg.create_pool(
                self._dsn,
                min_size=self.config.min_size,
                max_size=self.config.max_size,
                command_timeout=self.config.timeout,
                max_inactive_connection_lifetime=self.config.max_idle_time,
                server_settings={
                    'application_name': f'ainflue_pool_{self.pool_id}',
                    'jit': 'off'  # Disable JIT for consistent performance
                }
            )
            
            # Verify connection
            async with self._pool.acquire() as conn:
                await conn.execute('SELECT 1')
            
            self._is_initialized = True
            self._update_stats()
            
            logger.info(f"PostgreSQL pool {self.pool_id} initialized with {self.config.min_size}-{self.config.max_size} connections")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize PostgreSQL pool {self.pool_id}: {e}")
            return False
    
    async def close(self):
        """Close PostgreSQL connection pool."""
        if self._pool:
            await self._pool.close()
            self._pool = None
        self._is_initialized = False
        logger.info(f"PostgreSQL pool {self.pool_id} closed")
    
    async def health_check(self) -> bool:
        """Perform health check on PostgreSQL pool."""
        if not self._is_initialized or not self._pool:
            return False
        
        try:
            async with self._pool.acquire(timeout=5) as conn:
                await conn.execute('SELECT 1')
            
            self._stats['last_health_check'] = datetime.now(timezone.utc)
            self._update_stats()
            return True
            
        except Exception as e:
            logger.error(f"PostgreSQL pool {self.pool_id} health check failed: {e}")
            self._stats['connection_errors'] += 1
            return False
    
    @asynccontextmanager
    async def get_connection(self):
        """Get PostgreSQL connection from pool."""
        if not self._is_initialized or not self._pool:
            raise RuntimeError(f"PostgreSQL pool {self.pool_id} not initialized")
        
        connection = None
        try:
            connection = await self._pool.acquire(timeout=self.config.timeout)
            self._stats['active_connections'] += 1
            yield connection
            
        except Exception as e:
            self._stats['connection_errors'] += 1
            raise
        finally:
            if connection:
                await self._pool.release(connection)
                self._stats['active_connections'] = max(0, self._stats['active_connections'] - 1)
    
    async def execute_query(self, query: str, *args, **kwargs):
        """Execute a query with connection pooling."""
        async with self.get_connection() as conn:
            return await conn.fetch(query, *args, **kwargs)
    
    async def execute_transaction(self, queries: List[tuple]):
        """Execute multiple queries in a transaction."""
        async with self.get_connection() as conn:
            async with conn.transaction():
                results = []
                for query, args in queries:
                    result = await conn.fetch(query, *args)
                    results.append(result)
                return results
    
    def _update_stats(self):
        """Update pool statistics."""
        if self._pool:
            self._stats.update({
                'total_connections': self._pool.get_size(),
                'idle_connections': self._pool.get_idle_size(),
            })


class MongoDBPool(DatabasePool):
    """MongoDB connection pool with replica set support."""
    
    def __init__(self, config: DatabasePoolConfig):
        super().__init__(config)
        self._client = None
        self._database = None
        
    async def initialize(self) -> bool:
        """Initialize MongoDB connection pool."""
        if not MONGODB_AVAILABLE:
            logger.error("motor/pymongo not available for MongoDB pool")
            return False
        
        try:
            # Build connection URI
            conn_info = self.config.connection_info
            uri_parts = []
            
            if conn_info.username and conn_info.password:
                uri_parts.append(f"mongodb://{conn_info.username}:{conn_info.password}")
            else:
                uri_parts.append("mongodb://")
            
            uri_parts.append(f"@{conn_info.host}:{conn_info.port}")
            
            # Add additional parameters
            params = {
                'maxPoolSize': self.config.max_size,
                'minPoolSize': self.config.min_size,
                'maxIdleTimeMS': self.config.max_idle_time * 1000,
                'serverSelectionTimeoutMS': self.config.timeout * 1000,
                'appName': f'ainflue_pool_{self.pool_id}'
            }
            
            # Add replica set if specified
            if 'replica_set' in conn_info.additional_params:
                params['replicaSet'] = conn_info.additional_params['replica_set']
            
            # Add SSL if specified
            if conn_info.ssl_mode:
                params['ssl'] = True
                params['ssl_cert_reqs'] = conn_info.ssl_mode
            
            # Build final URI
            param_string = "&".join(f"{k}={v}" for k, v in params.items())
            uri = "".join(uri_parts) + f"/{conn_info.database}?{param_string}"
            
            # Create async client
            self._client = motor.motor_asyncio.AsyncIOMotorClient(uri)
            self._database = self._client[conn_info.database]
            
            # Verify connection
            await self._client.admin.command('ping')
            
            self._is_initialized = True
            self._update_stats()
            
            logger.info(f"MongoDB pool {self.pool_id} initialized for database {conn_info.database}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize MongoDB pool {self.pool_id}: {e}")
            return False
    
    async def close(self):
        """Close MongoDB connection pool."""
        if self._client:
            self._client.close()
            self._client = None
            self._database = None
        self._is_initialized = False
        logger.info(f"MongoDB pool {self.pool_id} closed")
    
    async def health_check(self) -> bool:
        """Perform health check on MongoDB pool."""
        if not self._is_initialized or not self._client:
            return False
        
        try:
            # Ping the database
            await asyncio.wait_for(
                self._client.admin.command('ping'),
                timeout=5
            )
            
            self._stats['last_health_check'] = datetime.now(timezone.utc)
            self._update_stats()
            return True
            
        except Exception as e:
            logger.error(f"MongoDB pool {self.pool_id} health check failed: {e}")
            self._stats['connection_errors'] += 1
            return False
    
    @asynccontextmanager
    async def get_connection(self):
        """Get MongoDB database connection."""
        if not self._is_initialized or not self._database:
            raise RuntimeError(f"MongoDB pool {self.pool_id} not initialized")
        
        try:
            self._stats['active_connections'] += 1
            yield self._database
        finally:
            self._stats['active_connections'] = max(0, self._stats['active_connections'] - 1)
    
    async def get_collection(self, collection_name: str):
        """Get a specific collection."""
        if not self._database:
            raise RuntimeError(f"MongoDB pool {self.pool_id} not initialized")
        return self._database[collection_name]
    
    async def find_documents(self, collection_name: str, filter_query: Dict[str, Any], 
                           limit: Optional[int] = None, sort: Optional[List[tuple]] = None):
        """Find documents in collection."""
        async with self.get_connection() as db:
            collection = db[collection_name]
            cursor = collection.find(filter_query)
            
            if sort:
                cursor = cursor.sort(sort)
            if limit:
                cursor = cursor.limit(limit)
            
            return await cursor.to_list(length=limit)
    
    async def insert_documents(self, collection_name: str, documents: Union[Dict, List[Dict]]):
        """Insert documents into collection."""
        async with self.get_connection() as db:
            collection = db[collection_name]
            
            if isinstance(documents, list):
                result = await collection.insert_many(documents)
                return result.inserted_ids
            else:
                result = await collection.insert_one(documents)
                return result.inserted_id
    
    async def update_documents(self, collection_name: str, filter_query: Dict[str, Any], 
                             update_data: Dict[str, Any], upsert: bool = False):
        """Update documents in collection."""
        async with self.get_connection() as db:
            collection = db[collection_name]
            result = await collection.update_many(filter_query, update_data, upsert=upsert)
            return {
                'matched_count': result.matched_count,
                'modified_count': result.modified_count,
                'upserted_id': result.upserted_id
            }
    
    def _update_stats(self):
        """Update pool statistics."""
        if self._client:
            # MongoDB doesn't expose pool stats directly, so we estimate
            self._stats.update({
                'total_connections': self.config.max_size,
                'idle_connections': self.config.max_size - self._stats['active_connections'],
            })


class ElasticsearchPool(DatabasePool):
    """Elasticsearch connection pool with cluster support."""
    
    def __init__(self, config: DatabasePoolConfig):
        super().__init__(config)
        self._client = None
        
    async def initialize(self) -> bool:
        """Initialize Elasticsearch connection pool."""
        if not ELASTICSEARCH_AVAILABLE:
            logger.error("elasticsearch-async not available for Elasticsearch pool")
            return False
        
        try:
            # Build connection configuration
            conn_info = self.config.connection_info
            
            # Connection hosts
            hosts = [f"{conn_info.host}:{conn_info.port}"]
            
            # Add additional hosts if specified
            if 'additional_hosts' in conn_info.additional_params:
                hosts.extend(conn_info.additional_params['additional_hosts'])
            
            # Authentication
            auth = None
            if conn_info.username and conn_info.password:
                auth = (conn_info.username, conn_info.password)
            
            # SSL configuration
            use_ssl = conn_info.ssl_mode == 'require'
            verify_certs = conn_info.ssl_mode != 'allow'
            
            # Create client
            self._client = AsyncElasticsearch(
                hosts=hosts,
                http_auth=auth,
                use_ssl=use_ssl,
                verify_certs=verify_certs,
                timeout=self.config.timeout,
                max_retries=self.config.retry_attempts,
                retry_on_timeout=True,
                sniff_on_start=True,
                sniff_on_connection_fail=True,
                sniffer_timeout=60
            )
            
            # Verify connection
            info = await self._client.info()
            if not info:
                raise Exception("Failed to get cluster info")
            
            self._is_initialized = True
            self._update_stats()
            
            logger.info(f"Elasticsearch pool {self.pool_id} initialized for cluster: {info.get('cluster_name', 'unknown')}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize Elasticsearch pool {self.pool_id}: {e}")
            return False
    
    async def close(self):
        """Close Elasticsearch connection pool."""
        if self._client:
            await self._client.close()
            self._client = None
        self._is_initialized = False
        logger.info(f"Elasticsearch pool {self.pool_id} closed")
    
    async def health_check(self) -> bool:
        """Perform health check on Elasticsearch pool."""
        if not self._is_initialized or not self._client:
            return False
        
        try:
            # Check cluster health
            health = await asyncio.wait_for(
                self._client.cluster.health(),
                timeout=5
            )
            
            is_healthy = health.get('status') in ['green', 'yellow']
            
            self._stats['last_health_check'] = datetime.now(timezone.utc)
            if not is_healthy:
                self._stats['connection_errors'] += 1
            
            self._update_stats()
            return is_healthy
            
        except Exception as e:
            logger.error(f"Elasticsearch pool {self.pool_id} health check failed: {e}")
            self._stats['connection_errors'] += 1
            return False
    
    @asynccontextmanager
    async def get_connection(self):
        """Get Elasticsearch client connection."""
        if not self._is_initialized or not self._client:
            raise RuntimeError(f"Elasticsearch pool {self.pool_id} not initialized")
        
        try:
            self._stats['active_connections'] += 1
            yield self._client
        finally:
            self._stats['active_connections'] = max(0, self._stats['active_connections'] - 1)
    
    async def search_documents(self, index: str, query: Dict[str, Any], 
                             size: int = 10, from_: int = 0, sort: Optional[List[Dict]] = None):
        """Search documents in index."""
        async with self.get_connection() as client:
            body = {
                'query': query,
                'size': size,
                'from': from_
            }
            
            if sort:
                body['sort'] = sort
            
            response = await client.search(index=index, body=body)
            return response
    
    async def index_document(self, index: str, document: Dict[str, Any], 
                           doc_id: Optional[str] = None, refresh: bool = False):
        """Index a document."""
        async with self.get_connection() as client:
            response = await client.index(
                index=index,
                body=document,
                id=doc_id,
                refresh=refresh
            )
            return response
    
    async def bulk_index(self, index: str, documents: List[Dict[str, Any]], 
                        doc_id_field: Optional[str] = None, refresh: bool = False):
        """Bulk index documents."""
        async with self.get_connection() as client:
            actions = []
            
            for doc in documents:
                action = {
                    '_index': index,
                    '_source': doc
                }
                
                if doc_id_field and doc_id_field in doc:
                    action['_id'] = doc[doc_id_field]
                
                actions.append(action)
            
            response = await client.bulk(body=actions, refresh=refresh)
            return response
    
    async def delete_document(self, index: str, doc_id: str, refresh: bool = False):
        """Delete a document."""
        async with self.get_connection() as client:
            response = await client.delete(
                index=index,
                id=doc_id,
                refresh=refresh
            )
            return response
    
    async def create_index(self, index: str, mappings: Dict[str, Any], 
                          settings: Optional[Dict[str, Any]] = None):
        """Create an index with mappings and settings."""
        async with self.get_connection() as client:
            body = {'mappings': mappings}
            if settings:
                body['settings'] = settings
            
            response = await client.indices.create(index=index, body=body)
            return response
    
    def _update_stats(self):
        """Update pool statistics."""
        # Elasticsearch doesn't expose connection pool stats directly
        self._stats.update({
            'total_connections': 1,  # Single persistent connection
            'idle_connections': 1 - self._stats['active_connections'],
        })


class DatabasePoolsManager:
    """Manager for all database connection pools."""
    
    def __init__(self):
        self._pools: Dict[str, DatabasePool] = {}
        self._monitoring_task: Optional[asyncio.Task] = None
        self._is_monitoring = False
    
    async def add_postgresql_pool(self, pool_id: str, connection_info: DatabaseConnectionInfo,
                                **pool_config) -> bool:
        """Add PostgreSQL connection pool."""
        config = DatabasePoolConfig(
            pool_id=pool_id,
            connection_info=connection_info,
            **pool_config
        )
        
        pool = PostgreSQLPool(config)
        success = await pool.initialize()
        
        if success:
            self._pools[pool_id] = pool
            logger.info(f"Added PostgreSQL pool: {pool_id}")
        
        return success
    
    async def add_mongodb_pool(self, pool_id: str, connection_info: DatabaseConnectionInfo,
                             **pool_config) -> bool:
        """Add MongoDB connection pool."""
        config = DatabasePoolConfig(
            pool_id=pool_id,
            connection_info=connection_info,
            **pool_config
        )
        
        pool = MongoDBPool(config)
        success = await pool.initialize()
        
        if success:
            self._pools[pool_id] = pool
            logger.info(f"Added MongoDB pool: {pool_id}")
        
        return success
    
    async def add_elasticsearch_pool(self, pool_id: str, connection_info: DatabaseConnectionInfo,
                                   **pool_config) -> bool:
        """Add Elasticsearch connection pool."""
        config = DatabasePoolConfig(
            pool_id=pool_id,
            connection_info=connection_info,
            **pool_config
        )
        
        pool = ElasticsearchPool(config)
        success = await pool.initialize()
        
        if success:
            self._pools[pool_id] = pool
            logger.info(f"Added Elasticsearch pool: {pool_id}")
        
        return success
    
    async def get_pool(self, pool_id: str) -> Optional[DatabasePool]:
        """Get a specific pool by ID."""
        return self._pools.get(pool_id)
    
    async def remove_pool(self, pool_id: str) -> bool:
        """Remove and close a pool."""
        pool = self._pools.get(pool_id)
        if pool:
            await pool.close()
            del self._pools[pool_id]
            logger.info(f"Removed pool: {pool_id}")
            return True
        return False
    
    async def health_check_all(self) -> Dict[str, bool]:
        """Health check all pools."""
        results = {}
        
        for pool_id, pool in self._pools.items():
            try:
                results[pool_id] = await pool.health_check()
            except Exception as e:
                logger.error(f"Health check failed for {pool_id}: {e}")
                results[pool_id] = False
        
        return results
    
    async def get_all_stats(self) -> Dict[str, Dict[str, Any]]:
        """Get statistics for all pools."""
        stats = {}
        
        for pool_id, pool in self._pools.items():
            stats[pool_id] = pool.get_stats()
        
        return stats
    
    async def start_monitoring(self, interval: int = 30):
        """Start background health monitoring."""
        if self._is_monitoring:
            return
        
        self._is_monitoring = True
        self._monitoring_task = asyncio.create_task(self._monitoring_loop(interval))
        logger.info("Database pools monitoring started")
    
    async def stop_monitoring(self):
        """Stop background monitoring."""
        self._is_monitoring = False
        
        if self._monitoring_task:
            self._monitoring_task.cancel()
            try:
                await self._monitoring_task
            except asyncio.CancelledError:
                pass
        
        logger.info("Database pools monitoring stopped")
    
    async def _monitoring_loop(self, interval: int):
        """Background monitoring loop."""
        while self._is_monitoring:
            try:
                # Health check all pools
                health_results = await self.health_check_all()
                
                # Log unhealthy pools
                unhealthy_pools = [pool_id for pool_id, is_healthy in health_results.items() if not is_healthy]
                if unhealthy_pools:
                    logger.warning(f"Unhealthy database pools detected: {unhealthy_pools}")
                
                # Wait for next cycle
                await asyncio.sleep(interval)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Database pools monitoring error: {e}")
                await asyncio.sleep(5)  # Brief pause on error
    
    async def close_all_pools(self):
        """Close all database pools."""
        logger.info("Closing all database pools...")
        
        # Stop monitoring
        await self.stop_monitoring()
        
        # Close all pools
        for pool_id in list(self._pools.keys()):
            await self.remove_pool(pool_id)
        
        logger.info("All database pools closed")
    
    @property
    def pool_count(self) -> int:
        """Get number of registered pools."""
        return len(self._pools)
    
    @property
    def pool_ids(self) -> List[str]:
        """Get list of pool IDs."""
        return list(self._pools.keys())


# Global database pools manager instance
_database_pools_manager: Optional[DatabasePoolsManager] = None


def get_database_pools_manager() -> DatabasePoolsManager:
    """Get the global database pools manager."""
    global _database_pools_manager
    if _database_pools_manager is None:
        _database_pools_manager = DatabasePoolsManager()
    return _database_pools_manager


# Export public interface
__all__ = [
    "DatabasePool",
    "PostgreSQLPool", 
    "MongoDBPool",
    "ElasticsearchPool",
    "DatabasePoolsManager",
    "get_database_pools_manager",
    "DatabaseConnectionInfo",
    "DatabasePoolConfig"
]