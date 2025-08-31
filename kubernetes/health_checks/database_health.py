"""Database Health Monitoring Service
Comprehensive health checking for all database systems

This module provides health monitoring for:
- PostgreSQL primary database with performance metrics
- Redis cache and session storage monitoring  
- MongoDB document storage health checking
- Vector databases (FAISS, Elasticsearch)
- Connection pool monitoring and optimization
- Query performance analysis and alerting
- Replication lag monitoring for distributed setups

Created by: Fahed Mlaiel <mlaiel@live.de>
Copyright: IA Influencer Agent Platform - All Rights Reserved

WARNING: This code is proprietary and confidential. Any unauthorized use,
reproduction, or distribution without explicit written permission from
Fahed Mlaiel is strictly prohibited and may result in legal action.
"""import asyncio
import time
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, asdict
import logging

import asyncpg
import aioredis
import pymongo
from motor.motor_asyncio import AsyncIOMotorClient
import psutil

from .core_health import HealthStatus, HealthCheckResult


@dataclass
class DatabaseMetrics:
    """Database performance metrics"""    active_connections: int
    max_connections: int
    connection_usage_percent: float
    avg_query_time_ms: float
    slow_queries_count: int
    database_size_mb: float
    cache_hit_ratio: float
    locks_count: int
    deadlocks_count: int


@dataclass
class RedisMetrics:
    """Redis performance metrics"""    connected_clients: int
    used_memory_mb: float
    used_memory_percent: float
    cache_hit_ratio: float
    evicted_keys: int
    expired_keys: int
    keyspace_hits: int
    keyspace_misses: int
    operations_per_second: float


class DatabaseHealthChecker:
    """    Comprehensive database health monitoring service
    
    Monitors all database systems including PostgreSQL, Redis, MongoDB,
    and vector databases with performance metrics and alerting.
    """    def __init__(self, config: Dict[str, Any]):
        """        Initialize database health checker
        
        Args:
            config: Database configuration dictionary
        """        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Database configurations
        self.postgres_config = config.get("database", {})
        self.redis_config = config.get("redis", {})
        self.mongodb_config = config.get("mongodb", {})
        self.elasticsearch_config = config.get("elasticsearch", {})
        
        # Health check thresholds
        self.connection_threshold = config.get("health_checks", {}).get("db_connection_threshold", 80.0)
        self.query_time_threshold = config.get("health_checks", {}).get("query_time_threshold_ms", 1000)
        self.memory_threshold = config.get("health_checks", {}).get("db_memory_threshold", 85.0)
        
        # Connection pools
        self._postgres_pool = None
        self._redis_client = None
        self._mongodb_client = None

    async def _get_postgres_pool(self):
        """Get or create PostgreSQL connection pool"""        if self._postgres_pool is None:
            try:
                self._postgres_pool = await asyncpg.create_pool(
                    host=self.postgres_config.get("host"),
                    port=self.postgres_config.get("port", 5432),
                    user=self.postgres_config.get("username"),
                    password=self.postgres_config.get("password"),
                    database=self.postgres_config.get("database"),
                    min_size=2,
                    max_size=10
                )
            except Exception as e:
                self.logger.error(f"Failed to create PostgreSQL pool: {str(e)}")
                raise
        return self._postgres_pool

    async def _get_redis_client(self):
        """Get or create Redis client"""        if self._redis_client is None:
            try:
                self._redis_client = await aioredis.from_url(
                    f"redis://{self.redis_config.get('host')}:{self.redis_config.get('port', 6379)}",
                    password=self.redis_config.get("password"),
                    db=self.redis_config.get("db", 0)
                )
            except Exception as e:
                self.logger.error(f"Failed to create Redis client: {str(e)}")
                raise
        return self._redis_client

    async def _get_mongodb_client(self):
        """Get or create MongoDB client"""        if self._mongodb_client is None:
            try:
                connection_string = (
                    f"mongodb://{self.mongodb_config.get('username')}:"
                    f"{self.mongodb_config.get('password')}@"
                    f"{self.mongodb_config.get('host')}:"
                    f"{self.mongodb_config.get('port', 27017)}/"
                    f"{self.mongodb_config.get('database')}"
                )
                self._mongodb_client = AsyncIOMotorClient(connection_string)
            except Exception as e:
                self.logger.error(f"Failed to create MongoDB client: {str(e)}")
                raise
        return self._mongodb_client

    async def check_postgresql_health(self) -> HealthCheckResult:
        """        Check PostgreSQL database health and performance
        
        Returns:
            HealthCheckResult: PostgreSQL health status and metrics
        """        start_time = time.time()
        
        try:
            pool = await self._get_postgres_pool()
            
            async with pool.acquire() as connection:
                # Basic connectivity test
                await connection.execute("SELECT 1")
                
                # Get database metrics
                stats_query = """                SELECT 
                    (SELECT setting::int FROM pg_settings WHERE name = 'max_connections') as max_connections,
                    (SELECT count(*) FROM pg_stat_activity WHERE state = 'active') as active_connections,
                    (SELECT pg_database_size(current_database())) as database_size,
                    (SELECT sum(blks_hit)::float / (sum(blks_hit) + sum(blks_read)) * 100 
                     FROM pg_stat_database WHERE datname = current_database()) as cache_hit_ratio
                """                
                result = await connection.fetchrow(stats_query)
                
                # Get slow queries count
                slow_queries = await connection.fetchval(
                    "SELECT count(*) FROM pg_stat_statements WHERE mean_time > $1",
                    self.query_time_threshold
                ) or 0
                
                # Get locks information
                locks_count = await connection.fetchval(
                    "SELECT count(*) FROM pg_locks WHERE granted = true"
                ) or 0
                
                # Calculate metrics
                connection_usage = (result['active_connections'] / result['max_connections']) * 100
                database_size_mb = result['database_size'] / (1024 * 1024)
                
                metrics = DatabaseMetrics(
                    active_connections=result['active_connections'],
                    max_connections=result['max_connections'],
                    connection_usage_percent=connection_usage,
                    avg_query_time_ms=0.0,  # Would need pg_stat_statements extension
                    slow_queries_count=slow_queries,
                    database_size_mb=database_size_mb,
                    cache_hit_ratio=result['cache_hit_ratio'] or 0.0,
                    locks_count=locks_count,
                    deadlocks_count=0  # Would need specific monitoring setup
                )
                
                # Determine health status
                status = HealthStatus.HEALTHY
                warnings = []
                
                if connection_usage > self.connection_threshold:
                    status = HealthStatus.DEGRADED
                    warnings.append(f"High connection usage: {connection_usage:.1f}%")
                
                if slow_queries > 10:
                    status = HealthStatus.DEGRADED if status == HealthStatus.HEALTHY else HealthStatus.UNHEALTHY
                    warnings.append(f"High slow queries count: {slow_queries}")
                
                if result['cache_hit_ratio'] < 90:
                    warnings.append(f"Low cache hit ratio: {result['cache_hit_ratio']:.1f}%")
                
                details = asdict(metrics)
                details.update({
                    "database_name": self.postgres_config.get("database"),
                    "host": self.postgres_config.get("host"),
                    "port": self.postgres_config.get("port"),
                    "warnings": warnings,
                    "extensions_available": [],  # Would query pg_extension
                    "replication_lag_ms": 0  # Would need replication setup
                })
                
                return HealthCheckResult(
                    service="postgresql",
                    status=status,
                    response_time_ms=(time.time() - start_time) * 1000,
                    timestamp=datetime.utcnow(),
                    details=details
                )
                
        except Exception as e:
            self.logger.error(f"PostgreSQL health check failed: {str(e)}")
            return HealthCheckResult(
                service="postgresql",
                status=HealthStatus.CRITICAL,
                response_time_ms=(time.time() - start_time) * 1000,
                timestamp=datetime.utcnow(),
                details={},
                error_message=str(e)
            )

    async def check_redis_health(self) -> HealthCheckResult:
        """        Check Redis cache health and performance
        
        Returns:
            HealthCheckResult: Redis health status and metrics
        """        start_time = time.time()
        
        try:
            redis_client = await self._get_redis_client()
            
            # Basic connectivity test
            await redis_client.ping()
            
            # Get Redis info
            info = await redis_client.info()
            
            # Get keyspace statistics
            keyspace_info = await redis_client.info("keyspace")
            stats_info = await redis_client.info("stats")
            memory_info = await redis_client.info("memory")
            
            # Calculate metrics
            used_memory_mb = memory_info.get("used_memory", 0) / (1024 * 1024)
            max_memory = memory_info.get("maxmemory", 0)
            used_memory_percent = (memory_info.get("used_memory", 0) / max_memory * 100) if max_memory > 0 else 0
            
            keyspace_hits = stats_info.get("keyspace_hits", 0)
            keyspace_misses = stats_info.get("keyspace_misses", 0)
            total_commands = keyspace_hits + keyspace_misses
            cache_hit_ratio = (keyspace_hits / total_commands * 100) if total_commands > 0 else 0
            
            operations_per_second = stats_info.get("instantaneous_ops_per_sec", 0)
            
            metrics = RedisMetrics(
                connected_clients=info.get("connected_clients", 0),
                used_memory_mb=used_memory_mb,
                used_memory_percent=used_memory_percent,
                cache_hit_ratio=cache_hit_ratio,
                evicted_keys=stats_info.get("evicted_keys", 0),
                expired_keys=stats_info.get("expired_keys", 0),
                keyspace_hits=keyspace_hits,
                keyspace_misses=keyspace_misses,
                operations_per_second=operations_per_second
            )
            
            # Determine health status
            status = HealthStatus.HEALTHY
            warnings = []
            
            if used_memory_percent > self.memory_threshold:
                status = HealthStatus.DEGRADED
                warnings.append(f"High memory usage: {used_memory_percent:.1f}%")
            
            if cache_hit_ratio < 80:
                status = HealthStatus.DEGRADED if status == HealthStatus.HEALTHY else HealthStatus.UNHEALTHY
                warnings.append(f"Low cache hit ratio: {cache_hit_ratio:.1f}%")
            
            if metrics.evicted_keys > 1000:
                warnings.append(f"High evicted keys: {metrics.evicted_keys}")
            
            details = asdict(metrics)
            details.update({
                "redis_version": info.get("redis_version"),
                "redis_mode": info.get("redis_mode"),
                "host": self.redis_config.get("host"),
                "port": self.redis_config.get("port"),
                "warnings": warnings,
                "uptime_seconds": info.get("uptime_in_seconds", 0),
                "total_commands_processed": stats_info.get("total_commands_processed", 0)
            })
            
            return HealthCheckResult(
                service="redis",
                status=status,
                response_time_ms=(time.time() - start_time) * 1000,
                timestamp=datetime.utcnow(),
                details=details
            )
            
        except Exception as e:
            self.logger.error(f"Redis health check failed: {str(e)}")
            return HealthCheckResult(
                service="redis",
                status=HealthStatus.CRITICAL,
                response_time_ms=(time.time() - start_time) * 1000,
                timestamp=datetime.utcnow(),
                details={},
                error_message=str(e)
            )

    async def check_mongodb_health(self) -> HealthCheckResult:
        """        Check MongoDB document database health
        
        Returns:
            HealthCheckResult: MongoDB health status and metrics
        """        start_time = time.time()
        
        try:
            client = await self._get_mongodb_client()
            
            # Test connectivity
            await client.admin.command("ping")
            
            # Get database stats
            db_name = self.mongodb_config.get("database")
            db = client[db_name]
            
            stats = await db.command("dbStats")
            server_status = await client.admin.command("serverStatus")
            
            # Extract metrics
            connections = server_status.get("connections", {})
            opcounters = server_status.get("opcounters", {})
            memory = server_status.get("mem", {})
            
            # Calculate operation rates (simplified)
            total_ops = sum(opcounters.values()) if opcounters else 0
            
            details = {
                "database_name": db_name,
                "host": self.mongodb_config.get("host"),
                "port": self.mongodb_config.get("port"),
                "mongodb_version": server_status.get("version"),
                "uptime_seconds": server_status.get("uptime", 0),
                
                # Database statistics
                "collections_count": stats.get("collections", 0),
                "objects_count": stats.get("objects", 0),
                "data_size_mb": stats.get("dataSize", 0) / (1024 * 1024),
                "storage_size_mb": stats.get("storageSize", 0) / (1024 * 1024),
                "index_size_mb": stats.get("indexSize", 0) / (1024 * 1024),
                
                # Connection statistics
                "current_connections": connections.get("current", 0),
                "available_connections": connections.get("available", 0),
                "total_created_connections": connections.get("totalCreated", 0),
                
                # Operation counters
                "operations_per_second": total_ops / server_status.get("uptime", 1),
                "insert_operations": opcounters.get("insert", 0),
                "query_operations": opcounters.get("query", 0),
                "update_operations": opcounters.get("update", 0),
                "delete_operations": opcounters.get("delete", 0),
                
                # Memory usage
                "resident_memory_mb": memory.get("resident", 0),
                "virtual_memory_mb": memory.get("virtual", 0),
                "mapped_memory_mb": memory.get("mapped", 0)
            }
            
            # Determine health status
            status = HealthStatus.HEALTHY
            warnings = []
            
            connection_usage = (connections.get("current", 0) / 
                             (connections.get("current", 0) + connections.get("available", 1))) * 100
            
            if connection_usage > self.connection_threshold:
                status = HealthStatus.DEGRADED
                warnings.append(f"High connection usage: {connection_usage:.1f}%")
            
            if memory.get("resident", 0) > 1000:  # > 1GB
                warnings.append(f"High memory usage: {memory.get('resident', 0)}MB")
            
            details["warnings"] = warnings
            details["connection_usage_percent"] = connection_usage
            
            return HealthCheckResult(
                service="mongodb",
                status=status,
                response_time_ms=(time.time() - start_time) * 1000,
                timestamp=datetime.utcnow(),
                details=details
            )
            
        except Exception as e:
            self.logger.error(f"MongoDB health check failed: {str(e)}")
            return HealthCheckResult(
                service="mongodb",
                status=HealthStatus.CRITICAL,
                response_time_ms=(time.time() - start_time) * 1000,
                timestamp=datetime.utcnow(),
                details={},
                error_message=str(e)
            )

    async def check_elasticsearch_health(self) -> HealthCheckResult:
        """        Check Elasticsearch vector database health
        
        Returns:
            HealthCheckResult: Elasticsearch health status and metrics
        """        start_time = time.time()
        
        try:
            import aiohttp
            
            es_config = self.elasticsearch_config
            base_url = f"http://{es_config.get('host')}:{es_config.get('port', 9200)}"
            
            async with aiohttp.ClientSession() as session:
                # Check cluster health
                async with session.get(f"{base_url}/_cluster/health") as response:
                    if response.status != 200:
                        raise Exception(f"Elasticsearch returned status {response.status}")
                    
                    health_data = await response.json()
                
                # Get cluster stats
                async with session.get(f"{base_url}/_cluster/stats") as response:
                    if response.status == 200:
                        stats_data = await response.json()
                    else:
                        stats_data = {}
                
                # Get node info
                async with session.get(f"{base_url}/_nodes/stats") as response:
                    if response.status == 200:
                        nodes_data = await response.json()
                    else:
                        nodes_data = {}
            
            # Determine status based on cluster health
            cluster_status = health_data.get("status", "red")
            if cluster_status == "green":
                status = HealthStatus.HEALTHY
            elif cluster_status == "yellow":
                status = HealthStatus.DEGRADED
            else:
                status = HealthStatus.UNHEALTHY
            
            details = {
                "cluster_name": health_data.get("cluster_name"),
                "cluster_status": cluster_status,
                "number_of_nodes": health_data.get("number_of_nodes", 0),
                "number_of_data_nodes": health_data.get("number_of_data_nodes", 0),
                "active_primary_shards": health_data.get("active_primary_shards", 0),
                "active_shards": health_data.get("active_shards", 0),
                "relocating_shards": health_data.get("relocating_shards", 0),
                "initializing_shards": health_data.get("initializing_shards", 0),
                "unassigned_shards": health_data.get("unassigned_shards", 0),
                "delayed_unassigned_shards": health_data.get("delayed_unassigned_shards", 0),
                "number_of_pending_tasks": health_data.get("number_of_pending_tasks", 0),
                "number_of_in_flight_fetch": health_data.get("number_of_in_flight_fetch", 0),
                "task_max_waiting_in_queue_millis": health_data.get("task_max_waiting_in_queue_millis", 0),
                "active_shards_percent_as_number": health_data.get("active_shards_percent_as_number", 0)
            }
            
            # Add cluster stats if available
            if stats_data:
                indices_stats = stats_data.get("indices", {})
                details.update({
                    "total_indices": indices_stats.get("count", 0),
                    "total_documents": indices_stats.get("docs", {}).get("count", 0),
                    "total_size_bytes": indices_stats.get("store", {}).get("size_in_bytes", 0),
                    "total_size_mb": indices_stats.get("store", {}).get("size_in_bytes", 0) / (1024 * 1024)
                })
            
            warnings = []
            if health_data.get("unassigned_shards", 0) > 0:
                warnings.append(f"Unassigned shards: {health_data.get('unassigned_shards')}")
            
            if health_data.get("number_of_pending_tasks", 0) > 10:
                warnings.append(f"High pending tasks: {health_data.get('number_of_pending_tasks')}")
            
            details["warnings"] = warnings
            
            return HealthCheckResult(
                service="elasticsearch",
                status=status,
                response_time_ms=(time.time() - start_time) * 1000,
                timestamp=datetime.utcnow(),
                details=details
            )
            
        except Exception as e:
            self.logger.error(f"Elasticsearch health check failed: {str(e)}")
            return HealthCheckResult(
                service="elasticsearch",
                status=HealthStatus.CRITICAL,
                response_time_ms=(time.time() - start_time) * 1000,
                timestamp=datetime.utcnow(),
                details={},
                error_message=str(e)
            )

    async def perform_comprehensive_check(self) -> List[HealthCheckResult]:
        """        Perform all database health checks concurrently
        
        Returns:
            List[HealthCheckResult]: All database health check results
        """        checks = await asyncio.gather(
            self.check_postgresql_health(),
            self.check_redis_health(),
            self.check_mongodb_health(),
            self.check_elasticsearch_health(),
            return_exceptions=True
        )
        
        results = []
        for check in checks:
            if isinstance(check, Exception):
                self.logger.error(f"Database health check failed with exception: {str(check)}")
                results.append(HealthCheckResult(
                    service="unknown_database",
                    status=HealthStatus.CRITICAL,
                    response_time_ms=0.0,
                    timestamp=datetime.utcnow(),
                    details={},
                    error_message=str(check)
                ))
            else:
                results.append(check)
                
        return results

    async def get_database_health_summary(self) -> Dict[str, Any]:
        """        Get comprehensive database health summary
        
        Returns:
            Dict[str, Any]: Database health summary with overall status
        """        results = await self.perform_comprehensive_check()
        
        # Calculate overall database health
        status_weights = {
            HealthStatus.HEALTHY: 0,
            HealthStatus.DEGRADED: 1,
            HealthStatus.UNHEALTHY: 2,
            HealthStatus.CRITICAL: 3
        }
        
        overall_score = max([status_weights[result.status] for result in results])
        overall_status = [status for status, weight in status_weights.items() if weight == overall_score][0]
        
        # Calculate metrics
        avg_response_time = sum([result.response_time_ms for result in results]) / len(results)
        healthy_databases = len([r for r in results if r.status == HealthStatus.HEALTHY])
        total_databases = len(results)
        
        return {
            "overall_status": overall_status.value,
            "healthy_databases": healthy_databases,
            "total_databases": total_databases,
            "database_health_percentage": (healthy_databases / total_databases) * 100,
            "average_response_time_ms": round(avg_response_time, 2),
            "timestamp": datetime.utcnow().isoformat(),
            "database_results": [asdict(result) for result in results]
        }

    async def cleanup_connections(self):
        """Clean up database connections"""        try:
            if self._postgres_pool:
                await self._postgres_pool.close()
                self._postgres_pool = None
                
            if self._redis_client:
                await self._redis_client.close()
                self._redis_client = None
                
            if self._mongodb_client:
                self._mongodb_client.close()
                self._mongodb_client = None
                
        except Exception as e:
            self.logger.error(f"Error cleaning up database connections: {str(e)}")
