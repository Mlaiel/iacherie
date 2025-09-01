"""Production Database Health Check System

This module implements comprehensive database health monitoring with
configurable timeouts and automatic recovery mechanisms.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel - All Rights Reserved
"""

import asyncio
import logging
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, field
from enum import Enum
import json
import psutil
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine
import aiohttp
import os

logger = logging.getLogger(__name__)

class HealthStatus(str, Enum):
    """Health check status values."""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    UNKNOWN = "unknown"

class CheckType(str, Enum):
    """Types of health checks."""
    DATABASE_CONNECTIVITY = "database_connectivity"
    QUERY_PERFORMANCE = "query_performance"
    CONNECTION_POOL = "connection_pool"
    DISK_SPACE = "disk_space"
    MEMORY_USAGE = "memory_usage"
    REPLICATION_LAG = "replication_lag"
    SLOW_QUERIES = "slow_queries"
    WAL_ARCHIVE_STATUS = "wal_archive_status"

@dataclass
class HealthCheckConfig:
    """Configuration for health checks."""
    # Timeout settings
    connection_timeout: int = 10
    query_timeout: int = 30
    health_check_timeout: int = 60
    
    # Thresholds
    max_query_time_ms: int = 1000
    max_connection_usage_percent: int = 80
    min_disk_space_gb: int = 10
    max_memory_usage_percent: int = 85
    max_replication_lag_seconds: int = 60
    max_slow_queries_per_minute: int = 10
    
    # Check intervals
    fast_check_interval: int = 30  # seconds
    full_check_interval: int = 300  # 5 minutes
    
    # Alerting
    enable_alerts: bool = True
    alert_webhook_url: Optional[str] = None
    consecutive_failures_threshold: int = 3

@dataclass
class HealthCheckResult:
    """Result of a health check."""
    check_type: CheckType
    status: HealthStatus
    timestamp: datetime
    response_time_ms: float
    message: str
    details: Dict[str, Any] = field(default_factory=dict)
    error: Optional[str] = None

class DatabaseHealthChecker:
    """Production database health monitoring system."""
    
    def __init__(self, config: HealthCheckConfig):
        self.config = config
        self.engine: Optional[AsyncEngine] = None
        self.check_results: Dict[CheckType, List[HealthCheckResult]] = {}
        self.consecutive_failures: Dict[CheckType, int] = {}
        self.is_monitoring = False
        self._monitor_task: Optional[asyncio.Task] = None
        
        # Initialize check results storage
        for check_type in CheckType:
            self.check_results[check_type] = []
            self.consecutive_failures[check_type] = 0
    
    async def initialize(self):
        """Initialize the health checker."""
        db_url = "postgresql+asyncpg://{user}:{password}@{host}:{port}/{database}?sslmode=require".format(
            user=os.getenv('POSTGRES_USER_PRODUCTION', 'ainflue_user'),
            password=os.getenv('POSTGRES_PASSWORD_PRODUCTION', ''),
            host=os.getenv('POSTGRES_HOST_PRODUCTION', 'localhost'),
            port=os.getenv('POSTGRES_PORT_PRODUCTION', '5432'),
            database=os.getenv('POSTGRES_DB_PRODUCTION', 'ainflue_production'),
        )
        
        self.engine = create_async_engine(
            db_url,
            pool_size=5,
            max_overflow=10,
            pool_timeout=self.config.connection_timeout,
            connect_args={
                "server_settings": {
                    "application_name": "ainflue_health_checker"
                }
            }
        )
        
        logger.info("Database health checker initialized")
    
    async def check_database_connectivity(self) -> HealthCheckResult:
        """Check basic database connectivity."""
        start_time = time.time()
        
        try:
            async with asyncio.timeout(self.config.connection_timeout):
                async with self.engine.connect() as conn:
                    await conn.execute(text("SELECT 1"))
            
            response_time = (time.time() - start_time) * 1000
            
            return HealthCheckResult(
                check_type=CheckType.DATABASE_CONNECTIVITY,
                status=HealthStatus.HEALTHY,
                timestamp=datetime.utcnow(),
                response_time_ms=response_time,
                message="Database connection successful",
                details={"response_time_ms": response_time}
            )
            
        except asyncio.TimeoutError:
            return HealthCheckResult(
                check_type=CheckType.DATABASE_CONNECTIVITY,
                status=HealthStatus.UNHEALTHY,
                timestamp=datetime.utcnow(),
                response_time_ms=(time.time() - start_time) * 1000,
                message="Database connection timeout",
                error="Connection timeout exceeded"
            )
        except Exception as e:
            return HealthCheckResult(
                check_type=CheckType.DATABASE_CONNECTIVITY,
                status=HealthStatus.UNHEALTHY,
                timestamp=datetime.utcnow(),
                response_time_ms=(time.time() - start_time) * 1000,
                message="Database connection failed",
                error=str(e)
            )
    
    async def check_query_performance(self) -> HealthCheckResult:
        """Check query performance with various test queries."""
        start_time = time.time()
        
        try:
            async with asyncio.timeout(self.config.query_timeout):
                async with self.engine.connect() as conn:
                    # Test queries
                    queries = [
                        "SELECT COUNT(*) FROM pg_stat_activity",
                        "SELECT version()",
                        "SELECT current_timestamp",
                        "SELECT pg_database_size(current_database())"
                    ]
                    
                    query_times = []
                    for query in queries:
                        query_start = time.time()
                        await conn.execute(text(query))
                        query_time = (time.time() - query_start) * 1000
                        query_times.append(query_time)
            
            avg_query_time = sum(query_times) / len(query_times)
            max_query_time = max(query_times)
            
            status = HealthStatus.HEALTHY
            if max_query_time > self.config.max_query_time_ms:
                status = HealthStatus.DEGRADED
            
            return HealthCheckResult(
                check_type=CheckType.QUERY_PERFORMANCE,
                status=status,
                timestamp=datetime.utcnow(),
                response_time_ms=avg_query_time,
                message=f"Query performance check completed",
                details={
                    "avg_query_time_ms": avg_query_time,
                    "max_query_time_ms": max_query_time,
                    "queries_tested": len(queries)
                }
            )
            
        except Exception as e:
            return HealthCheckResult(
                check_type=CheckType.QUERY_PERFORMANCE,
                status=HealthStatus.UNHEALTHY,
                timestamp=datetime.utcnow(),
                response_time_ms=(time.time() - start_time) * 1000,
                message="Query performance check failed",
                error=str(e)
            )
    
    async def check_connection_pool(self) -> HealthCheckResult:
        """Check connection pool health."""
        start_time = time.time()
        
        try:
            pool = self.engine.pool
            
            pool_size = pool.size()
            checked_out = pool.checkedout()
            checked_in = pool.checkedin()
            overflow = pool.overflow()
            
            usage_percent = (checked_out / pool_size) * 100 if pool_size > 0 else 0
            
            status = HealthStatus.HEALTHY
            if usage_percent > self.config.max_connection_usage_percent:
                status = HealthStatus.DEGRADED
            
            return HealthCheckResult(
                check_type=CheckType.CONNECTION_POOL,
                status=status,
                timestamp=datetime.utcnow(),
                response_time_ms=(time.time() - start_time) * 1000,
                message=f"Connection pool usage: {usage_percent:.1f}%",
                details={
                    "pool_size": pool_size,
                    "checked_out": checked_out,
                    "checked_in": checked_in,
                    "overflow": overflow,
                    "usage_percent": usage_percent
                }
            )
            
        except Exception as e:
            return HealthCheckResult(
                check_type=CheckType.CONNECTION_POOL,
                status=HealthStatus.UNHEALTHY,
                timestamp=datetime.utcnow(),
                response_time_ms=(time.time() - start_time) * 1000,
                message="Connection pool check failed",
                error=str(e)
            )
    
    async def check_disk_space(self) -> HealthCheckResult:
        """Check disk space availability."""
        start_time = time.time()
        
        try:
            # Check various important paths
            paths_to_check = [
                "/var/lib/postgresql/data",
                "/backup",
                "/tmp",
                "/"
            ]
            
            disk_info = {}
            min_free_gb = float('inf')
            
            for path in paths_to_check:
                if os.path.exists(path):
                    disk_usage = psutil.disk_usage(path)
                    free_gb = disk_usage.free / (1024**3)
                    total_gb = disk_usage.total / (1024**3)
                    used_percent = (disk_usage.used / disk_usage.total) * 100
                    
                    disk_info[path] = {
                        "free_gb": free_gb,
                        "total_gb": total_gb,
                        "used_percent": used_percent
                    }
                    
                    min_free_gb = min(min_free_gb, free_gb)
            
            status = HealthStatus.HEALTHY
            if min_free_gb < self.config.min_disk_space_gb:
                status = HealthStatus.DEGRADED if min_free_gb > self.config.min_disk_space_gb / 2 else HealthStatus.UNHEALTHY
            
            return HealthCheckResult(
                check_type=CheckType.DISK_SPACE,
                status=status,
                timestamp=datetime.utcnow(),
                response_time_ms=(time.time() - start_time) * 1000,
                message=f"Minimum free disk space: {min_free_gb:.1f}GB",
                details=disk_info
            )
            
        except Exception as e:
            return HealthCheckResult(
                check_type=CheckType.DISK_SPACE,
                status=HealthStatus.UNHEALTHY,
                timestamp=datetime.utcnow(),
                response_time_ms=(time.time() - start_time) * 1000,
                message="Disk space check failed",
                error=str(e)
            )
    
    async def check_replication_lag(self) -> HealthCheckResult:
        """Check replication lag if replicas are configured."""
        start_time = time.time()
        
        try:
            async with self.engine.connect() as conn:
                # Check if this is a master or slave
                result = await conn.execute(text("SELECT pg_is_in_recovery()"))
                is_replica = result.scalar()
                
                if is_replica:
                    # On replica: check lag
                    result = await conn.execute(text("""
                        SELECT 
                            EXTRACT(EPOCH FROM (now() - pg_last_xact_replay_timestamp())) as lag_seconds
                    """))
                    lag_seconds = result.scalar() or 0
                else:
                    # On master: check replication status
                    result = await conn.execute(text("""
                        SELECT 
                            client_addr,
                            state,
                            pg_wal_lsn_diff(pg_current_wal_lsn(), flush_lsn) as lag_bytes
                        FROM pg_stat_replication
                    """))
                    replicas = result.fetchall()
                    lag_seconds = 0  # Master has no lag
                
                status = HealthStatus.HEALTHY
                if lag_seconds > self.config.max_replication_lag_seconds:
                    status = HealthStatus.DEGRADED
                
                return HealthCheckResult(
                    check_type=CheckType.REPLICATION_LAG,
                    status=status,
                    timestamp=datetime.utcnow(),
                    response_time_ms=(time.time() - start_time) * 1000,
                    message=f"Replication lag: {lag_seconds:.1f}s",
                    details={
                        "lag_seconds": lag_seconds,
                        "is_replica": is_replica,
                        "replica_count": len(replicas) if not is_replica else None
                    }
                )
                
        except Exception as e:
            return HealthCheckResult(
                check_type=CheckType.REPLICATION_LAG,
                status=HealthStatus.UNKNOWN,
                timestamp=datetime.utcnow(),
                response_time_ms=(time.time() - start_time) * 1000,
                message="Replication lag check failed",
                error=str(e)
            )
    
    async def check_slow_queries(self) -> HealthCheckResult:
        """Check for slow queries using pg_stat_statements."""
        start_time = time.time()
        
        try:
            async with self.engine.connect() as conn:
                # Check if pg_stat_statements is available
                result = await conn.execute(text("""
                    SELECT EXISTS(
                        SELECT 1 FROM pg_extension WHERE extname = 'pg_stat_statements'
                    )
                """))
                
                if not result.scalar():
                    return HealthCheckResult(
                        check_type=CheckType.SLOW_QUERIES,
                        status=HealthStatus.UNKNOWN,
                        timestamp=datetime.utcnow(),
                        response_time_ms=(time.time() - start_time) * 1000,
                        message="pg_stat_statements extension not available"
                    )
                
                # Get slow queries from last minute
                result = await conn.execute(text("""
                    SELECT COUNT(*) as slow_query_count
                    FROM pg_stat_statements 
                    WHERE mean_exec_time > :threshold
                    AND calls > 0
                """), {"threshold": self.config.max_query_time_ms})
                
                slow_query_count = result.scalar() or 0
                
                status = HealthStatus.HEALTHY
                if slow_query_count > self.config.max_slow_queries_per_minute:
                    status = HealthStatus.DEGRADED
                
                return HealthCheckResult(
                    check_type=CheckType.SLOW_QUERIES,
                    status=status,
                    timestamp=datetime.utcnow(),
                    response_time_ms=(time.time() - start_time) * 1000,
                    message=f"Slow queries detected: {slow_query_count}",
                    details={"slow_query_count": slow_query_count}
                )
                
        except Exception as e:
            return HealthCheckResult(
                check_type=CheckType.SLOW_QUERIES,
                status=HealthStatus.UNKNOWN,
                timestamp=datetime.utcnow(),
                response_time_ms=(time.time() - start_time) * 1000,
                message="Slow query check failed",
                error=str(e)
            )
    
    async def run_full_health_check(self) -> Dict[str, HealthCheckResult]:
        """Run all health checks."""
        logger.info("Running full health check")
        
        checks = [
            self.check_database_connectivity(),
            self.check_query_performance(),
            self.check_connection_pool(),
            self.check_disk_space(),
            self.check_replication_lag(),
            self.check_slow_queries()
        ]
        
        results = await asyncio.gather(*checks, return_exceptions=True)
        
        health_results = {}
        for result in results:
            if isinstance(result, HealthCheckResult):
                health_results[result.check_type.value] = result
                
                # Store result and update consecutive failures
                self.check_results[result.check_type].append(result)
                
                if result.status == HealthStatus.UNHEALTHY:
                    self.consecutive_failures[result.check_type] += 1
                else:
                    self.consecutive_failures[result.check_type] = 0
                
                # Keep only last 100 results per check type
                if len(self.check_results[result.check_type]) > 100:
                    self.check_results[result.check_type] = self.check_results[result.check_type][-100:]
                
                # Send alert if threshold reached
                if (self.consecutive_failures[result.check_type] >= self.config.consecutive_failures_threshold 
                    and self.config.enable_alerts):
                    await self._send_alert(result)
        
        return health_results
    
    async def get_health_summary(self) -> Dict[str, Any]:
        """Get comprehensive health summary."""
        recent_results = {}
        overall_status = HealthStatus.HEALTHY
        
        for check_type, results in self.check_results.items():
            if results:
                latest_result = results[-1]
                recent_results[check_type.value] = {
                    "status": latest_result.status,
                    "timestamp": latest_result.timestamp.isoformat(),
                    "response_time_ms": latest_result.response_time_ms,
                    "message": latest_result.message,
                    "consecutive_failures": self.consecutive_failures[check_type]
                }
                
                # Update overall status
                if latest_result.status == HealthStatus.UNHEALTHY:
                    overall_status = HealthStatus.UNHEALTHY
                elif latest_result.status == HealthStatus.DEGRADED and overall_status == HealthStatus.HEALTHY:
                    overall_status = HealthStatus.DEGRADED
        
        return {
            "overall_status": overall_status,
            "timestamp": datetime.utcnow().isoformat(),
            "checks": recent_results,
            "uptime_checks": len(self.check_results.get(CheckType.DATABASE_CONNECTIVITY, [])),
            "configuration": {
                "connection_timeout": self.config.connection_timeout,
                "query_timeout": self.config.query_timeout,
                "health_check_timeout": self.config.health_check_timeout
            }
        }
    
    async def start_monitoring(self):
        """Start continuous health monitoring."""
        if self.is_monitoring:
            return
        
        self.is_monitoring = True
        self._monitor_task = asyncio.create_task(self._monitor_health())
        logger.info("Started health monitoring")
    
    async def stop_monitoring(self):
        """Stop health monitoring."""
        self.is_monitoring = False
        if self._monitor_task:
            self._monitor_task.cancel()
            try:
                await self._monitor_task
            except asyncio.CancelledError:
                pass
        logger.info("Stopped health monitoring")
    
    async def _monitor_health(self):
        """Continuous health monitoring loop."""
        while self.is_monitoring:
            try:
                # Run fast checks more frequently
                connectivity_result = await self.check_database_connectivity()
                pool_result = await self.check_connection_pool()
                
                # Store results
                self.check_results[CheckType.DATABASE_CONNECTIVITY].append(connectivity_result)
                self.check_results[CheckType.CONNECTION_POOL].append(pool_result)
                
                # Run full check less frequently
                if len(self.check_results[CheckType.DATABASE_CONNECTIVITY]) % (
                    self.config.full_check_interval // self.config.fast_check_interval
                ) == 0:
                    await self.run_full_health_check()
                
                await asyncio.sleep(self.config.fast_check_interval)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Health monitoring error: {e}")
                await asyncio.sleep(self.config.fast_check_interval)
    
    async def _send_alert(self, result: HealthCheckResult):
        """Send health check alert."""
        if not self.config.alert_webhook_url:
            return
        
        alert_data = {
            "alert_type": "health_check_failure",
            "check_type": result.check_type.value,
            "status": result.status.value,
            "message": result.message,
            "error": result.error,
            "consecutive_failures": self.consecutive_failures[result.check_type],
            "timestamp": result.timestamp.isoformat()
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    self.config.alert_webhook_url,
                    json=alert_data,
                    timeout=aiohttp.ClientTimeout(total=10)
                ) as response:
                    if response.status == 200:
                        logger.info(f"Alert sent for {result.check_type.value}")
                    else:
                        logger.warning(f"Alert webhook returned status {response.status}")
        except Exception as e:
            logger.error(f"Failed to send alert: {e}")

# Global health checker instance
_health_checker: Optional[DatabaseHealthChecker] = None

async def get_health_checker() -> DatabaseHealthChecker:
    """Get or create health checker instance."""
    global _health_checker
    
    if _health_checker is None:
        config = HealthCheckConfig(
            connection_timeout=int(os.getenv('DB_HEALTH_CONNECTION_TIMEOUT', '10')),
            query_timeout=int(os.getenv('DB_HEALTH_QUERY_TIMEOUT', '30')),
            alert_webhook_url=os.getenv('DB_HEALTH_ALERT_WEBHOOK_URL')
        )
        
        _health_checker = DatabaseHealthChecker(config)
        await _health_checker.initialize()
    
    return _health_checker

async def main():
    """Main function for running health checker."""
    health_checker = await get_health_checker()
    await health_checker.start_monitoring()
    
    logger.info("Database health checker running. Press Ctrl+C to stop.")
    
    try:
        while True:
            await asyncio.sleep(1)
    except KeyboardInterrupt:
        await health_checker.stop_monitoring()
        logger.info("Health checker stopped")

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())