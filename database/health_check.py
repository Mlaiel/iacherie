"""Database Health Check with Timeout - Production Ready
=========================================================

Comprehensive database health monitoring with timeout controls
for production database systems.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import logging
import time
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from contextlib import asynccontextmanager

try:
    import asyncpg
except ImportError:
    asyncpg = None

try:
    import psutil
except ImportError:
    psutil = None

logger = logging.getLogger(__name__)

class HealthStatus(Enum):
    """Database health status enumeration"""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    CRITICAL = "critical"
    TIMEOUT = "timeout"
    
@dataclass
class HealthCheckConfig:
    """Configuration for database health checks"""
    connection_timeout: float = 5.0
    query_timeout: float = 10.0
    max_connections_percent: float = 80.0
    max_response_time_ms: float = 1000.0
    min_free_space_gb: float = 5.0
    max_cpu_percent: float = 85.0
    max_memory_percent: float = 90.0
    replication_lag_threshold_seconds: int = 30
    check_interval_seconds: int = 30

@dataclass
class HealthCheckResult:
    """Health check result with detailed metrics"""
    status: HealthStatus
    timestamp: datetime
    response_time_ms: float
    error_message: Optional[str] = None
    details: Dict[str, Any] = field(default_factory=dict)
    metrics: Dict[str, float] = field(default_factory=dict)

class DatabaseHealthChecker:
    """Production database health checker with comprehensive monitoring"""
    
    def __init__(self, config: HealthCheckConfig, connection_pool=None):
        self.config = config
        self.connection_pool = connection_pool
        self.last_check_result: Optional[HealthCheckResult] = None
        self.check_history: List[HealthCheckResult] = []
        self.max_history_size = 100
        
    async def perform_health_check(self) -> HealthCheckResult:
        """Perform comprehensive database health check with timeout"""
        start_time = time.time()
        
        try:
            # Run health check with overall timeout
            result = await asyncio.wait_for(
                self._execute_health_checks(),
                timeout=self.config.query_timeout + 5.0
            )
            
            response_time_ms = (time.time() - start_time) * 1000
            result.response_time_ms = response_time_ms
            result.timestamp = datetime.utcnow()
            
            # Store result
            self.last_check_result = result
            self._store_check_history(result)
            
            return result
            
        except asyncio.TimeoutError:
            return HealthCheckResult(
                status=HealthStatus.TIMEOUT,
                timestamp=datetime.utcnow(),
                response_time_ms=(time.time() - start_time) * 1000,
                error_message="Health check timed out",
                details={"timeout_seconds": self.config.query_timeout + 5.0}
            )
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return HealthCheckResult(
                status=HealthStatus.CRITICAL,
                timestamp=datetime.utcnow(),
                response_time_ms=(time.time() - start_time) * 1000,
                error_message=str(e),
                details={"exception_type": type(e).__name__}
            )
    
    async def _execute_health_checks(self) -> HealthCheckResult:
        """Execute all health check components"""
        status = HealthStatus.HEALTHY
        details = {}
        metrics = {}
        error_messages = []
        
        # 1. Connection test
        try:
            connection_result = await self._check_database_connection()
            details.update(connection_result.get("details", {}))
            metrics.update(connection_result.get("metrics", {}))
            
            if not connection_result.get("success", False):
                status = HealthStatus.CRITICAL
                error_messages.append(connection_result.get("error", "Connection failed"))
        except Exception as e:
            status = HealthStatus.CRITICAL
            error_messages.append(f"Connection check failed: {e}")
        
        # 2. Query performance test
        if status != HealthStatus.CRITICAL:
            try:
                query_result = await self._check_query_performance()
                details.update(query_result.get("details", {}))
                metrics.update(query_result.get("metrics", {}))
                
                if query_result.get("slow_queries", False):
                    status = HealthStatus.DEGRADED
            except Exception as e:
                status = HealthStatus.DEGRADED
                error_messages.append(f"Query performance check failed: {e}")
        
        # 3. Resource utilization
        try:
            resource_result = await self._check_resource_utilization()
            details.update(resource_result.get("details", {}))
            metrics.update(resource_result.get("metrics", {}))
            
            if resource_result.get("high_utilization", False):
                if status == HealthStatus.HEALTHY:
                    status = HealthStatus.DEGRADED
        except Exception as e:
            error_messages.append(f"Resource check failed: {e}")
        
        # 4. Replication status (if applicable)
        try:
            replication_result = await self._check_replication_status()
            if replication_result:
                details.update(replication_result.get("details", {}))
                metrics.update(replication_result.get("metrics", {}))
                
                if replication_result.get("lag_detected", False):
                    if status == HealthStatus.HEALTHY:
                        status = HealthStatus.DEGRADED
        except Exception as e:
            error_messages.append(f"Replication check failed: {e}")
        
        return HealthCheckResult(
            status=status,
            timestamp=datetime.utcnow(),
            response_time_ms=0,  # Will be set by caller
            error_message="; ".join(error_messages) if error_messages else None,
            details=details,
            metrics=metrics
        )
    
    async def _check_database_connection(self) -> Dict[str, Any]:
        """Test database connection with timeout"""
        try:
            if self.connection_pool:
                # Use existing connection pool
                async with asyncio.timeout(self.config.connection_timeout):
                    async with self.connection_pool.acquire() as conn:
                        result = await conn.fetchval("SELECT 1")
                        active_connections = len(self.connection_pool._holders)
                        max_connections = self.connection_pool._maxsize
                        
                        return {
                            "success": True,
                            "details": {
                                "connection_method": "pool",
                                "active_connections": active_connections,
                                "max_connections": max_connections
                            },
                            "metrics": {
                                "connection_utilization_percent": (active_connections / max_connections) * 100
                            }
                        }
            else:
                # Direct connection test
                async with asyncio.timeout(self.config.connection_timeout):
                    conn = await asyncpg.connect(
                        host="localhost",
                        port=5432,
                        database="ainflue_prod",
                        user="ainflue_app",
                        timeout=self.config.connection_timeout
                    )
                    result = await conn.fetchval("SELECT 1")
                    await conn.close()
                    
                    return {
                        "success": True,
                        "details": {"connection_method": "direct"},
                        "metrics": {}
                    }
                    
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "details": {"connection_failed": True},
                "metrics": {}
            }
    
    async def _check_query_performance(self) -> Dict[str, Any]:
        """Check query performance with pg_stat_statements"""
        try:
            if not self.connection_pool:
                return {"details": {}, "metrics": {}}
            
            async with asyncio.timeout(self.config.query_timeout):
                async with self.connection_pool.acquire() as conn:
                    # Test simple query performance
                    start_time = time.time()
                    await conn.fetchval("SELECT COUNT(*) FROM pg_stat_activity")
                    query_time = (time.time() - start_time) * 1000
                    
                    # Check for slow queries
                    slow_queries = await conn.fetch("""
                        SELECT query, mean_exec_time, calls 
                        FROM pg_stat_statements 
                        WHERE mean_exec_time > $1 
                        ORDER BY mean_exec_time DESC 
                        LIMIT 5
                    """, self.config.max_response_time_ms)
                    
                    # Check active queries
                    active_queries = await conn.fetch("""
                        SELECT COUNT(*) as count, state 
                        FROM pg_stat_activity 
                        WHERE state IS NOT NULL 
                        GROUP BY state
                    """)
                    
                    return {
                        "details": {
                            "slow_queries_count": len(slow_queries),
                            "active_query_states": {row["state"]: row["count"] for row in active_queries}
                        },
                        "metrics": {
                            "simple_query_time_ms": query_time,
                            "slow_queries_detected": len(slow_queries)
                        },
                        "slow_queries": len(slow_queries) > 0
                    }
                    
        except Exception as e:
            return {
                "details": {"query_performance_error": str(e)},
                "metrics": {},
                "slow_queries": False
            }
    
    async def _check_resource_utilization(self) -> Dict[str, Any]:
        """Check database and system resource utilization"""
        try:
            if not self.connection_pool:
                return {"details": {}, "metrics": {}}
            
            async with self.connection_pool.acquire() as conn:
                # Database size and space
                db_size = await conn.fetchval("""
                    SELECT pg_size_pretty(pg_database_size(current_database()))
                """)
                
                # Table sizes (top 5)
                table_sizes = await conn.fetch("""
                    SELECT schemaname, tablename, 
                           pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) as size,
                           pg_total_relation_size(schemaname||'.'||tablename) as size_bytes
                    FROM pg_tables 
                    WHERE schemaname NOT IN ('information_schema', 'pg_catalog')
                    ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC 
                    LIMIT 5
                """)
                
                # Connection count
                connection_count = await conn.fetchval("""
                    SELECT COUNT(*) FROM pg_stat_activity
                """)
                
                # System metrics
                cpu_percent = psutil.cpu_percent(interval=1)
                memory = psutil.virtual_memory()
                disk = psutil.disk_usage('/')
                
                high_utilization = (
                    cpu_percent > self.config.max_cpu_percent or
                    memory.percent > self.config.max_memory_percent or
                    (disk.free / (1024**3)) < self.config.min_free_space_gb
                )
                
                return {
                    "details": {
                        "database_size": db_size,
                        "connection_count": connection_count,
                        "largest_tables": [
                            {"name": f"{row['schemaname']}.{row['tablename']}", "size": row["size"]}
                            for row in table_sizes
                        ]
                    },
                    "metrics": {
                        "cpu_percent": cpu_percent,
                        "memory_percent": memory.percent,
                        "disk_free_gb": disk.free / (1024**3),
                        "active_connections": connection_count
                    },
                    "high_utilization": high_utilization
                }
                
        except Exception as e:
            return {
                "details": {"resource_check_error": str(e)},
                "metrics": {},
                "high_utilization": False
            }
    
    async def _check_replication_status(self) -> Optional[Dict[str, Any]]:
        """Check replication lag and status"""
        try:
            if not self.connection_pool:
                return None
            
            async with self.connection_pool.acquire() as conn:
                # Check if this is a primary server
                is_primary = await conn.fetchval("SELECT NOT pg_is_in_recovery()")
                
                if is_primary:
                    # Check replication slots and lag
                    replication_stats = await conn.fetch("""
                        SELECT slot_name, state, active, 
                               pg_wal_lsn_diff(pg_current_wal_lsn(), restart_lsn) as lag_bytes
                        FROM pg_replication_slots
                    """)
                    
                    # Check connected replicas
                    replicas = await conn.fetch("""
                        SELECT client_addr, state, 
                               pg_wal_lsn_diff(pg_current_wal_lsn(), sent_lsn) as lag_bytes
                        FROM pg_stat_replication
                    """)
                    
                    max_lag_seconds = 0
                    if replicas:
                        for replica in replicas:
                            lag_bytes = replica.get("lag_bytes", 0) or 0
                            # Approximate lag in seconds (rough estimation)
                            lag_seconds = lag_bytes / (1024 * 1024)  # Rough approximation
                            max_lag_seconds = max(max_lag_seconds, lag_seconds)
                    
                    lag_detected = max_lag_seconds > self.config.replication_lag_threshold_seconds
                    
                    return {
                        "details": {
                            "is_primary": True,
                            "replication_slots": len(replication_stats),
                            "active_replicas": len(replicas),
                            "max_lag_estimation": f"{max_lag_seconds:.2f}s"
                        },
                        "metrics": {
                            "replication_lag_seconds": max_lag_seconds,
                            "replica_count": len(replicas)
                        },
                        "lag_detected": lag_detected
                    }
                else:
                    # This is a replica - check lag from primary
                    lag_info = await conn.fetch("""
                        SELECT NOW() - pg_last_xact_replay_timestamp() AS lag
                    """)
                    
                    lag_seconds = 0
                    if lag_info and lag_info[0]["lag"]:
                        lag_seconds = lag_info[0]["lag"].total_seconds()
                    
                    return {
                        "details": {
                            "is_primary": False,
                            "replay_lag": f"{lag_seconds:.2f}s"
                        },
                        "metrics": {
                            "replication_lag_seconds": lag_seconds
                        },
                        "lag_detected": lag_seconds > self.config.replication_lag_threshold_seconds
                    }
                    
        except Exception as e:
            logger.warning(f"Replication check failed: {e}")
            return None
    
    def _store_check_history(self, result: HealthCheckResult) -> None:
        """Store health check result in history"""
        self.check_history.append(result)
        
        # Maintain max history size
        if len(self.check_history) > self.max_history_size:
            self.check_history = self.check_history[-self.max_history_size:]
    
    def get_health_summary(self) -> Dict[str, Any]:
        """Get comprehensive health summary"""
        if not self.last_check_result:
            return {"status": "unknown", "message": "No health checks performed yet"}
        
        recent_checks = self.check_history[-10:] if len(self.check_history) >= 10 else self.check_history
        
        status_counts = {}
        for check in recent_checks:
            status = check.status.value
            status_counts[status] = status_counts.get(status, 0) + 1
        
        avg_response_time = sum(check.response_time_ms for check in recent_checks) / len(recent_checks) if recent_checks else 0
        
        return {
            "current_status": self.last_check_result.status.value,
            "last_check": self.last_check_result.timestamp.isoformat(),
            "response_time_ms": self.last_check_result.response_time_ms,
            "error_message": self.last_check_result.error_message,
            "recent_status_distribution": status_counts,
            "avg_response_time_ms": avg_response_time,
            "checks_performed": len(self.check_history),
            "details": self.last_check_result.details,
            "metrics": self.last_check_result.metrics
        }

# Health check runner for periodic monitoring
class HealthCheckRunner:
    """Periodic health check runner"""
    
    def __init__(self, health_checker: DatabaseHealthChecker):
        self.health_checker = health_checker
        self.running = False
        self.task: Optional[asyncio.Task] = None
    
    async def start_monitoring(self) -> None:
        """Start periodic health monitoring"""
        if self.running:
            return
        
        self.running = True
        self.task = asyncio.create_task(self._monitoring_loop())
        logger.info("Database health monitoring started")
    
    async def stop_monitoring(self) -> None:
        try:
                    # Collect metrics
                    metrics = {
                        "timestamp": datetime.utcnow(),
                        "metric_name": "stop_monitoring",
                        "value": data if data else 0,
                        "tags": self._get_metric_tags()
                    }
            
                    # Store metrics
                    await self._store_metric(metrics)
            
                    # Send to monitoring system
                    if hasattr(self, 'metrics_client'):
                        await self.metrics_client.send(metrics)
            
                    logger.info(f"Metric stop_monitoring collected")
                    return metrics
            
                except Exception as e:
                    logger.error(f"Metric collection stop_monitoring failed: {e}")
                    return None
    async def _monitoring_loop(self) -> None:
        """Main monitoring loop"""
        while self.running:
            try:
                result = await self.health_checker.perform_health_check()
                
                # Log result based on status
                if result.status == HealthStatus.HEALTHY:
                    logger.debug(f"Health check passed: {result.response_time_ms:.2f}ms")
                elif result.status == HealthStatus.DEGRADED:
                    logger.warning(f"Health check degraded: {result.error_message}")
                else:
                    logger.error(f"Health check failed: {result.status.value} - {result.error_message}")
                
                # Wait for next check
                await asyncio.sleep(self.health_checker.config.check_interval_seconds)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Health monitoring error: {e}")
                await asyncio.sleep(5)  # Brief pause before retry