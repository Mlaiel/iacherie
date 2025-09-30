"""MongoDB Monitoring and Health Checks
====================================

Comprehensive monitoring system for MongoDB health, performance metrics,
and operational status in the Ainflue platform.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel - All Rights Reserved
"""

import asyncio
import logging
import time
from typing import Dict, Any, Optional, List, Callable
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum

try:
    import motor.motor_asyncio
    import pymongo
    from pymongo.errors import ServerSelectionTimeoutError, NetworkTimeout
    MONGODB_AVAILABLE = True
except ImportError:
    MONGODB_AVAILABLE = False
    # Create mock classes to prevent NameError
    class motor:
        class motor_asyncio:
            pass
    class pymongo:
        pass

from .connection import MongoDBConnection, get_connection

logger = logging.getLogger(__name__)

class HealthStatus(Enum):
    """Health status enumeration."""
    HEALTHY = "healthy"
    WARNING = "warning"
    CRITICAL = "critical"
    UNKNOWN = "unknown"

@dataclass
class DatabaseMetrics:
    """Database-level metrics."""
    total_size_bytes: int = 0
    data_size_bytes: int = 0
    index_size_bytes: int = 0
    collection_count: int = 0
    index_count: int = 0
    avg_obj_size: float = 0.0
    storage_size_bytes: int = 0

@dataclass
class ConnectionMetrics:
    """Connection pool metrics."""
    current_connections: int = 0
    available_connections: int = 0
    created_connections: int = 0
    active_connections: int = 0
    max_pool_size: int = 0

@dataclass
class PerformanceMetrics:
    """Performance metrics."""
    operations_per_second: float = 0.0
    avg_response_time_ms: float = 0.0
    queries_per_second: float = 0.0
    inserts_per_second: float = 0.0
    updates_per_second: float = 0.0
    deletes_per_second: float = 0.0
    slow_queries_count: int = 0

@dataclass
class HealthCheckResult:
    """Health check result."""
    status: HealthStatus
    message: str
    timestamp: datetime
    metrics: Dict[str, Any] = field(default_factory=dict)
    details: Dict[str, Any] = field(default_factory=dict)

class MongoDBMonitor:
    """MongoDB monitoring and health checking system."""
    
    def __init__(self, connection: Optional[MongoDBConnection] = None):
        """Initialize MongoDB monitor."""
        if not MONGODB_AVAILABLE:
            raise ImportError("MongoDB dependencies not available")
        
        self.connection = connection or get_connection()
        self._monitoring = False
        self._monitor_task: Optional[asyncio.Task] = None
        self._health_callbacks: List[Callable[[HealthCheckResult], None]] = []
        self._metrics_history: List[Dict[str, Any]] = []
        self._max_history_size = 1000
        
    async def check_health(self) -> HealthCheckResult:
        """Perform comprehensive health check."""
        try:
            start_time = time.time()
            
            if not self.connection.is_connected:
                return HealthCheckResult(
                    status=HealthStatus.CRITICAL,
                    message="Not connected to MongoDB",
                    timestamp=datetime.utcnow()
                )
            
            # Test basic connectivity
            ping_result = await self.connection.ping()
            if not ping_result:
                return HealthCheckResult(
                    status=HealthStatus.CRITICAL,
                    message="MongoDB ping failed",
                    timestamp=datetime.utcnow()
                )
            
            # Get server status
            server_status = await self._get_server_status()
            if not server_status:
                return HealthCheckResult(
                    status=HealthStatus.WARNING,
                    message="Failed to get server status",
                    timestamp=datetime.utcnow()
                )
            
            # Calculate health score based on various metrics
            health_score = await self._calculate_health_score(server_status)
            
            # Determine status
            if health_score >= 0.9:
                status = HealthStatus.HEALTHY
                message = "MongoDB is healthy"
            elif health_score >= 0.7:
                status = HealthStatus.WARNING
                message = "MongoDB has some performance issues"
            else:
                status = HealthStatus.CRITICAL
                message = "MongoDB has critical issues"
            
            response_time = (time.time() - start_time) * 1000
            
            result = HealthCheckResult(
                status=status,
                message=message,
                timestamp=datetime.utcnow(),
                metrics={
                    "response_time_ms": response_time,
                    "health_score": health_score,
                    "uptime_seconds": server_status.get("uptime", 0)
                },
                details=server_status
            )
            
            return result
            
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return HealthCheckResult(
                status=HealthStatus.CRITICAL,
                message=f"Health check error: {str(e)}",
                timestamp=datetime.utcnow()
            )
    
    async def _get_server_status(self) -> Dict[str, Any]:
        """Get MongoDB server status."""
        try:
            return await self.connection.database.command("serverStatus")
        except Exception as e:
            logger.error(f"Failed to get server status: {e}")
            return {}
    
    async def _calculate_health_score(self, server_status: Dict[str, Any]) -> float:
        """Calculate health score from 0.0 to 1.0."""
        score = 1.0
        
        # Check connection metrics
        connections = server_status.get("connections", {})
        current = connections.get("current", 0)
        available = connections.get("available", 1)
        
        if available > 0:
            connection_ratio = current / (current + available)
            if connection_ratio > 0.9:
                score -= 0.2  # High connection usage
            elif connection_ratio > 0.7:
                score -= 0.1
        
        # Check memory usage
        mem = server_status.get("mem", {})
        resident_mb = mem.get("resident", 0)
        virtual_mb = mem.get("virtual", 0)
        
        if resident_mb > 8000:  # More than 8GB RAM usage
            score -= 0.1
        
        # Check operation counters
        opcounters = server_status.get("opcounters", {})
        total_ops = sum(opcounters.values()) if opcounters else 0
        
        if total_ops > 10000:  # High operation count
            score -= 0.05
        
        # Check lock status
        locks = server_status.get("locks", {})
        global_lock = locks.get("Global", {})
        if global_lock:
            lock_ratio = global_lock.get("acquireWaitCount", {}).get("r", 0)
            if lock_ratio > 100:
                score -= 0.1
        
        return max(0.0, min(1.0, score))
    
    async def get_database_metrics(self, database_name: Optional[str] = None) -> DatabaseMetrics:
        """Get database-level metrics."""
        try:
            db_name = database_name or self.connection.config.database
            db_stats = await self.connection.database.command("dbStats")
            
            return DatabaseMetrics(
                total_size_bytes=db_stats.get("dataSize", 0) + db_stats.get("indexSize", 0),
                data_size_bytes=db_stats.get("dataSize", 0),
                index_size_bytes=db_stats.get("indexSize", 0),
                collection_count=db_stats.get("collections", 0),
                index_count=db_stats.get("indexes", 0),
                avg_obj_size=db_stats.get("avgObjSize", 0.0),
                storage_size_bytes=db_stats.get("storageSize", 0)
            )
            
        except Exception as e:
            logger.error(f"Failed to get database metrics: {e}")
            return DatabaseMetrics()
    
    async def get_connection_metrics(self) -> ConnectionMetrics:
        """Get connection pool metrics."""
        try:
            server_status = await self._get_server_status()
            connections = server_status.get("connections", {})
            
            return ConnectionMetrics(
                current_connections=connections.get("current", 0),
                available_connections=connections.get("available", 0),
                created_connections=connections.get("totalCreated", 0),
                active_connections=connections.get("active", 0),
                max_pool_size=self.connection.config.max_pool_size
            )
            
        except Exception as e:
            logger.error(f"Failed to get connection metrics: {e}")
            return ConnectionMetrics()
    
    async def get_performance_metrics(self) -> PerformanceMetrics:
        """Get performance metrics."""
        try:
            server_status = await self._get_server_status()
            opcounters = server_status.get("opcounters", {})
            
            # Calculate operations per second (simplified)
            total_ops = sum(opcounters.values()) if opcounters else 0
            uptime = server_status.get("uptime", 1)
            ops_per_second = total_ops / uptime if uptime > 0 else 0
            
            return PerformanceMetrics(
                operations_per_second=ops_per_second,
                queries_per_second=opcounters.get("query", 0) / uptime if uptime > 0 else 0,
                inserts_per_second=opcounters.get("insert", 0) / uptime if uptime > 0 else 0,
                updates_per_second=opcounters.get("update", 0) / uptime if uptime > 0 else 0,
                deletes_per_second=opcounters.get("delete", 0) / uptime if uptime > 0 else 0,
                avg_response_time_ms=0.0,  # Would need profiling data
                slow_queries_count=0  # Would need profiler analysis
            )
            
        except Exception as e:
            logger.error(f"Failed to get performance metrics: {e}")
            return PerformanceMetrics()
    
    async def get_collection_stats(self, collection_name: str) -> Dict[str, Any]:
        """Get detailed collection statistics."""
        try:
            stats = await self.connection.database.command("collStats", collection_name)
            return {
                "size_bytes": stats.get("size", 0),
                "count": stats.get("count", 0),
                "avg_obj_size": stats.get("avgObjSize", 0),
                "storage_size": stats.get("storageSize", 0),
                "total_index_size": stats.get("totalIndexSize", 0),
                "index_count": len(stats.get("indexSizes", {})),
                "capped": stats.get("capped", False)
            }
        except Exception as e:
            logger.error(f"Failed to get collection stats for {collection_name}: {e}")
            return {}
    
    async def start_monitoring(self, interval_seconds: int = 60):
        """Start continuous monitoring."""
        if self._monitoring:
            logger.warning("Monitoring already started")
            return
        
        self._monitoring = True
        self._monitor_task = asyncio.create_task(self._monitoring_loop(interval_seconds))
        logger.info(f"Started MongoDB monitoring with {interval_seconds}s interval")
    
    async def stop_monitoring(self):
        """Stop continuous monitoring."""
        self._monitoring = False
        if self._monitor_task:
            self._monitor_task.cancel()
            try:
                await self._monitor_task
            except asyncio.CancelledError:
                pass
        logger.info("Stopped MongoDB monitoring")
    
    async def _monitoring_loop(self, interval_seconds: int):
        """Main monitoring loop."""
        while self._monitoring:
            try:
                # Perform health check
                health_result = await self.check_health()
                
                # Get metrics
                db_metrics = await self.get_database_metrics()
                conn_metrics = await self.get_connection_metrics()
                perf_metrics = await self.get_performance_metrics()
                
                # Store metrics history
                metrics_snapshot = {
                    "timestamp": datetime.utcnow().isoformat(),
                    "health": health_result.__dict__,
                    "database": db_metrics.__dict__,
                    "connections": conn_metrics.__dict__,
                    "performance": perf_metrics.__dict__
                }
                
                self._metrics_history.append(metrics_snapshot)
                
                # Limit history size
                if len(self._metrics_history) > self._max_history_size:
                    self._metrics_history = self._metrics_history[-self._max_history_size:]
                
                # Notify callbacks
                for callback in self._health_callbacks:
                    try:
                        callback(health_result)
                    except Exception as e:
                        logger.error(f"Health callback error: {e}")
                
                await asyncio.sleep(interval_seconds)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Monitoring loop error: {e}")
                await asyncio.sleep(interval_seconds)
    
    def add_health_callback(self, callback: Callable[[HealthCheckResult], None]):
        """Add health status callback."""
        self._health_callbacks.append(callback)
    
    def remove_health_callback(self, callback: Callable[[HealthCheckResult], None]):
        """Remove health status callback."""
        if callback in self._health_callbacks:
            self._health_callbacks.remove(callback)
    
    def get_metrics_history(self, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """Get metrics history."""
        if limit:
            return self._metrics_history[-limit:]
        return self._metrics_history.copy()
    
    async def generate_report(self) -> Dict[str, Any]:
        """Generate comprehensive monitoring report."""
        health_result = await self.check_health()
        db_metrics = await self.get_database_metrics()
        conn_metrics = await self.get_connection_metrics()
        perf_metrics = await self.get_performance_metrics()
        
        # Get collection statistics
        collections = await self.connection.database.list_collection_names()
        collection_stats = {}
        for coll_name in collections[:10]:  # Limit to prevent long execution
            collection_stats[coll_name] = await self.get_collection_stats(coll_name)
        
        return {
            "report_generated": datetime.utcnow().isoformat(),
            "connection_info": self.connection.connection_info,
            "health": health_result.__dict__,
            "database_metrics": db_metrics.__dict__,
            "connection_metrics": conn_metrics.__dict__,
            "performance_metrics": perf_metrics.__dict__,
            "collection_stats": collection_stats,
            "metrics_history_count": len(self._metrics_history)
        }

# Global monitor instance
_default_monitor: Optional[MongoDBMonitor] = None

def get_monitor(connection: Optional[MongoDBConnection] = None) -> MongoDBMonitor:
    """Get or create default MongoDB monitor."""
    global _default_monitor
    if _default_monitor is None:
        _default_monitor = MongoDBMonitor(connection)
    return _default_monitor

# Health check callback example
def default_health_callback(result: HealthCheckResult):
    """Default health status callback."""
    if result.status == HealthStatus.CRITICAL:
        logger.error(f"MongoDB CRITICAL: {result.message}")
    elif result.status == HealthStatus.WARNING:
        logger.warning(f"MongoDB WARNING: {result.message}")
    else:
        logger.info(f"MongoDB {result.status.value}: {result.message}")

# Export main classes and functions
__all__ = [
    'HealthStatus',
    'DatabaseMetrics',
    'ConnectionMetrics',
    'PerformanceMetrics',
    'HealthCheckResult',
    'MongoDBMonitor',
    'get_monitor',
    'default_health_callback'
]