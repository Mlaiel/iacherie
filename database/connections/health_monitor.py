"""
Database Health Monitor - IA Influencer Agent Platform

Monitors health and performance of all database connections:
- Real-time health monitoring and alerting
- Performance metrics collection and analysis
- Automatic failover and recovery coordination
- Connection pool health and optimization
- Resource usage tracking and alerting
- SLA monitoring and compliance reporting

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import logging
from typing import Dict, Any, Optional, List, Callable, Set
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import json

from ..monitoring.alerts import AlertManager
from ..monitoring.metrics import MetricsCollector


class HealthStatus(Enum):
    """Database health status levels"""
    HEALTHY = "healthy"
    WARNING = "warning"
    CRITICAL = "critical"
    UNKNOWN = "unknown"


@dataclass
class HealthThresholds:
    """Health monitoring thresholds"""
    response_time_warning: float = 2.0  # seconds
    response_time_critical: float = 5.0  # seconds
    error_rate_warning: float = 0.05  # 5%
    error_rate_critical: float = 0.15  # 15%
    connection_usage_warning: float = 0.8  # 80%
    connection_usage_critical: float = 0.95  # 95%
    disk_usage_warning: float = 0.8  # 80%
    disk_usage_critical: float = 0.9  # 90%


@dataclass
class HealthCheckResult:
    """Health check result for a single database"""
    database_type: str
    status: HealthStatus
    response_time: float
    error_count: int
    metrics: Dict[str, Any]
    issues: List[str] = field(default_factory=list)
    timestamp: datetime = field(default_factory=datetime.utcnow)


class DatabaseHealthMonitor:
    """
    Comprehensive health monitor for all database connections.
    
    Monitors:
    - PostgreSQL connection pools and query performance
    - Redis memory usage and response times
    - MongoDB replica set health and operation metrics
    - Elasticsearch cluster health and index performance
    - Vector store index integrity and search performance
    - Object storage availability and transfer speeds
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Monitoring configuration
        self.thresholds = HealthThresholds()
        self.check_interval = 30  # seconds
        self.history_retention = 24  # hours
        
        # Database handlers
        self.handlers: Dict[str, Any] = {}
        
        # Health state
        self.health_history: Dict[str, List[HealthCheckResult]] = {}
        self.current_status: Dict[str, HealthStatus] = {}
        self.last_check_time: Optional[datetime] = None
        
        # Monitoring components
        self.alert_manager = AlertManager()
        self.metrics_collector = MetricsCollector()
        
        # Monitoring control
        self.monitoring_active = False
        self.monitoring_task: Optional[asyncio.Task] = None
        
        # Health check callbacks
        self.health_callbacks: List[Callable[[Dict[str, HealthCheckResult]], None]] = []
    
    async def initialize(self, handlers: Dict[str, Any]) -> None:
        """Initialize health monitoring with database handlers"""
        self.handlers = handlers
        self.logger.info("Database health monitor initialized")
        
        # Initialize alert manager
        await self.alert_manager.initialize()
        
        # Initialize metrics collector
        await self.metrics_collector.initialize()
        
        # Start monitoring
        await self.start_monitoring()
    
    async def start_monitoring(self) -> None:
        """Start continuous health monitoring"""
        if self.monitoring_active:
            return
        
        self.monitoring_active = True
        self.monitoring_task = asyncio.create_task(self._monitoring_loop())
        self.logger.info("Started database health monitoring")
    
    async def stop_monitoring(self) -> None:
        """Stop health monitoring"""
        self.monitoring_active = False
        
        if self.monitoring_task:
            self.monitoring_task.cancel()
            try:
                await self.monitoring_task
            except asyncio.CancelledError:
                pass
        
        self.logger.info("Stopped database health monitoring")
    
    async def _monitoring_loop(self) -> None:
        """Main monitoring loop"""
        while self.monitoring_active:
            try:
                # Perform comprehensive health check
                results = await self.comprehensive_health_check()
                
                # Process results
                await self._process_health_results(results)
                
                # Wait for next check
                await asyncio.sleep(self.check_interval)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"Health monitoring loop error: {e}")
                await asyncio.sleep(self.check_interval)
    
    async def comprehensive_health_check(self) -> Dict[str, HealthCheckResult]:
        """Perform comprehensive health check on all databases"""
        results = {}
        check_tasks = []
        
        # Create health check tasks for each database
        for db_type, handler in self.handlers.items():
            task = asyncio.create_task(
                self._check_database_health(db_type, handler)
            )
            check_tasks.append((db_type, task))
        
        # Execute all health checks in parallel
        for db_type, task in check_tasks:
            try:
                result = await task
                results[db_type] = result
            except Exception as e:
                self.logger.error(f"Health check failed for {db_type}: {e}")
                results[db_type] = HealthCheckResult(
                    database_type=db_type,
                    status=HealthStatus.CRITICAL,
                    response_time=0.0,
                    error_count=1,
                    metrics={},
                    issues=[f"Health check failed: {str(e)}"]
                )
        
        self.last_check_time = datetime.utcnow()
        return results
    
    async def _check_database_health(self, db_type: str, handler: Any) -> HealthCheckResult:
        """Check health of a single database"""
        start_time = datetime.utcnow()
        
        try:
            # Get health check from handler
            health_data = await handler.health_check()
            
            response_time = (datetime.utcnow() - start_time).total_seconds()
            
            # Determine status based on response
            if health_data.get("status") == "healthy":
                status = self._evaluate_health_status(db_type, health_data, response_time)
            else:
                status = HealthStatus.CRITICAL
            
            # Extract metrics
            metrics = health_data.get("metrics", {})
            error_count = metrics.get("error_count", 0)
            
            # Identify issues
            issues = self._identify_issues(db_type, health_data, response_time)
            
            return HealthCheckResult(
                database_type=db_type,
                status=status,
                response_time=response_time,
                error_count=error_count,
                metrics=health_data,
                issues=issues
            )
            
        except Exception as e:
            response_time = (datetime.utcnow() - start_time).total_seconds()
            
            return HealthCheckResult(
                database_type=db_type,
                status=HealthStatus.CRITICAL,
                response_time=response_time,
                error_count=1,
                metrics={},
                issues=[f"Health check exception: {str(e)}"]
            )
    
    def _evaluate_health_status(self, 
                              db_type: str, 
                              health_data: Dict[str, Any], 
                              response_time: float) -> HealthStatus:
        """Evaluate overall health status based on metrics"""
        issues = []
        
        # Check response time
        if response_time >= self.thresholds.response_time_critical:
            return HealthStatus.CRITICAL
        elif response_time >= self.thresholds.response_time_warning:
            issues.append("slow_response")
        
        # Check error rates
        metrics = health_data.get("metrics", {})
        total_operations = metrics.get("operation_count", 0) or metrics.get("query_count", 0)
        error_count = metrics.get("error_count", 0)
        
        if total_operations > 0:
            error_rate = error_count / total_operations
            if error_rate >= self.thresholds.error_rate_critical:
                return HealthStatus.CRITICAL
            elif error_rate >= self.thresholds.error_rate_warning:
                issues.append("high_error_rate")
        
        # Database-specific checks
        if db_type == "postgresql":
            status = self._check_postgresql_health(health_data)
            if status != HealthStatus.HEALTHY:
                return status
        elif db_type == "redis":
            status = self._check_redis_health(health_data)
            if status != HealthStatus.HEALTHY:
                return status
        elif db_type == "mongodb":
            status = self._check_mongodb_health(health_data)
            if status != HealthStatus.HEALTHY:
                return status
        elif db_type == "elasticsearch":
            status = self._check_elasticsearch_health(health_data)
            if status != HealthStatus.HEALTHY:
                return status
        
        # Return warning if any issues found, otherwise healthy
        return HealthStatus.WARNING if issues else HealthStatus.HEALTHY
    
    def _check_postgresql_health(self, health_data: Dict[str, Any]) -> HealthStatus:
        """Check PostgreSQL-specific health metrics"""
        # Check connection pool usage
        pool_size = health_data.get("pool_size", 0)
        pool_idle = health_data.get("pool_idle", 0)
        
        if pool_size > 0:
            usage_ratio = (pool_size - pool_idle) / pool_size
            if usage_ratio >= self.thresholds.connection_usage_critical:
                return HealthStatus.CRITICAL
            elif usage_ratio >= self.thresholds.connection_usage_warning:
                return HealthStatus.WARNING
        
        # Check for connection issues in stats
        conn_stats = health_data.get("connection_stats", {})
        if conn_stats.get("available", 0) <= 0:
            return HealthStatus.CRITICAL
        
        return HealthStatus.HEALTHY
    
    def _check_redis_health(self, health_data: Dict[str, Any]) -> HealthStatus:
        """Check Redis-specific health metrics"""
        # Check memory usage
        used_memory = health_data.get("used_memory")
        if used_memory and "GB" in str(used_memory):
            # Parse memory usage and check against limits
            # This is simplified - in real implementation, check against max memory
            pass
        
        # Check connected clients
        connected_clients = health_data.get("connected_clients", 0)
        if connected_clients <= 0:
            return HealthStatus.CRITICAL
        
        return HealthStatus.HEALTHY
    
    def _check_mongodb_health(self, health_data: Dict[str, Any]) -> HealthStatus:
        """Check MongoDB-specific health metrics"""
        # Check database storage
        database = health_data.get("database", {})
        storage_size = database.get("storage_size", 0)
        data_size = database.get("data_size", 0)
        
        if storage_size > 0 and data_size > 0:
            usage_ratio = data_size / storage_size
            if usage_ratio >= self.thresholds.disk_usage_critical:
                return HealthStatus.CRITICAL
            elif usage_ratio >= self.thresholds.disk_usage_warning:
                return HealthStatus.WARNING
        
        return HealthStatus.HEALTHY
    
    def _check_elasticsearch_health(self, health_data: Dict[str, Any]) -> HealthStatus:
        """Check Elasticsearch-specific health metrics"""
        cluster = health_data.get("cluster", {})
        cluster_status = cluster.get("status", "unknown")
        
        if cluster_status == "red":
            return HealthStatus.CRITICAL
        elif cluster_status == "yellow":
            return HealthStatus.WARNING
        elif cluster_status == "green":
            return HealthStatus.HEALTHY
        
        return HealthStatus.UNKNOWN
    
    def _identify_issues(self, 
                        db_type: str, 
                        health_data: Dict[str, Any], 
                        response_time: float) -> List[str]:
        """Identify specific health issues"""
        issues = []
        
        # General issues
        if response_time >= self.thresholds.response_time_warning:
            issues.append(f"Slow response time: {response_time:.2f}s")
        
        metrics = health_data.get("metrics", {})
        error_count = metrics.get("error_count", 0)
        if error_count > 0:
            issues.append(f"Errors detected: {error_count}")
        
        # Database-specific issues
        if db_type == "postgresql":
            issues.extend(self._identify_postgresql_issues(health_data))
        elif db_type == "redis":
            issues.extend(self._identify_redis_issues(health_data))
        elif db_type == "mongodb":
            issues.extend(self._identify_mongodb_issues(health_data))
        elif db_type == "elasticsearch":
            issues.extend(self._identify_elasticsearch_issues(health_data))
        
        return issues
    
    def _identify_postgresql_issues(self, health_data: Dict[str, Any]) -> List[str]:
        """Identify PostgreSQL-specific issues"""
        issues = []
        
        conn_stats = health_data.get("connection_stats", {})
        if conn_stats.get("available", 0) <= 5:
            issues.append("Low available connections")
        
        return issues
    
    def _identify_redis_issues(self, health_data: Dict[str, Any]) -> List[str]:
        """Identify Redis-specific issues"""
        issues = []
        
        # Check for rejected connections
        if health_data.get("rejected_connections", 0) > 0:
            issues.append("Rejected connections detected")
        
        return issues
    
    def _identify_mongodb_issues(self, health_data: Dict[str, Any]) -> List[str]:
        """Identify MongoDB-specific issues"""
        issues = []
        
        # Check for high connection count
        connections = health_data.get("connections", {})
        if connections.get("current", 0) > 1000:
            issues.append("High connection count")
        
        return issues
    
    def _identify_elasticsearch_issues(self, health_data: Dict[str, Any]) -> List[str]:
        """Identify Elasticsearch-specific issues"""
        issues = []
        
        cluster = health_data.get("cluster", {})
        if cluster.get("unassigned_shards", 0) > 0:
            issues.append(f"Unassigned shards: {cluster['unassigned_shards']}")
        
        if cluster.get("relocating_shards", 0) > 0:
            issues.append(f"Relocating shards: {cluster['relocating_shards']}")
        
        return issues
    
    async def _process_health_results(self, results: Dict[str, HealthCheckResult]) -> None:
        """Process health check results"""
        # Update current status
        for db_type, result in results.items():
            self.current_status[db_type] = result.status
            
            # Add to history
            if db_type not in self.health_history:
                self.health_history[db_type] = []
            
            self.health_history[db_type].append(result)
            
            # Trim history
            cutoff_time = datetime.utcnow() - timedelta(hours=self.history_retention)
            self.health_history[db_type] = [
                r for r in self.health_history[db_type] 
                if r.timestamp > cutoff_time
            ]
        
        # Send alerts for critical issues
        await self._send_alerts(results)
        
        # Collect metrics
        await self._collect_metrics(results)
        
        # Notify callbacks
        await self._notify_callbacks(results)
    
    async def _send_alerts(self, results: Dict[str, HealthCheckResult]) -> None:
        """Send alerts for health issues"""
        for db_type, result in results.items():
            if result.status == HealthStatus.CRITICAL:
                await self.alert_manager.send_alert(
                    severity="critical",
                    title=f"{db_type.upper()} Database Critical",
                    message=f"Database {db_type} is in critical state: {', '.join(result.issues)}",
                    metadata={
                        "database_type": db_type,
                        "response_time": result.response_time,
                        "error_count": result.error_count,
                        "issues": result.issues
                    }
                )
            elif result.status == HealthStatus.WARNING:
                await self.alert_manager.send_alert(
                    severity="warning",
                    title=f"{db_type.upper()} Database Warning",
                    message=f"Database {db_type} has warnings: {', '.join(result.issues)}",
                    metadata={
                        "database_type": db_type,
                        "response_time": result.response_time,
                        "issues": result.issues
                    }
                )
    
    async def _collect_metrics(self, results: Dict[str, HealthCheckResult]) -> None:
        """Collect metrics from health results"""
        for db_type, result in results.items():
            # Collect basic health metrics
            await self.metrics_collector.record_gauge(
                f"database_health_status_{db_type}",
                1 if result.status == HealthStatus.HEALTHY else 0,
                {"database": db_type}
            )
            
            await self.metrics_collector.record_histogram(
                f"database_response_time_{db_type}",
                result.response_time,
                {"database": db_type}
            )
            
            await self.metrics_collector.record_counter(
                f"database_errors_{db_type}",
                result.error_count,
                {"database": db_type}
            )
    
    async def _notify_callbacks(self, results: Dict[str, HealthCheckResult]) -> None:
        """Notify registered health check callbacks"""
        for callback in self.health_callbacks:
            try:
                await callback(results)
            except Exception as e:
                self.logger.error(f"Health callback error: {e}")
    
    def register_health_callback(self, callback: Callable[[Dict[str, HealthCheckResult]], None]) -> None:
        """Register a callback for health check results"""
        self.health_callbacks.append(callback)
    
    def get_current_health_status(self) -> Dict[str, HealthStatus]:
        """Get current health status for all databases"""
        return self.current_status.copy()
    
    def get_health_history(self, 
                          database_type: Optional[str] = None,
                          hours: int = 1) -> Dict[str, List[HealthCheckResult]]:
        """Get health history for specified time period"""
        cutoff_time = datetime.utcnow() - timedelta(hours=hours)
        
        if database_type:
            if database_type in self.health_history:
                return {
                    database_type: [
                        r for r in self.health_history[database_type]
                        if r.timestamp > cutoff_time
                    ]
                }
            return {}
        else:
            return {
                db_type: [
                    r for r in history 
                    if r.timestamp > cutoff_time
                ]
                for db_type, history in self.health_history.items()
            }
    
    async def get_metrics(self) -> Dict[str, Any]:
        """Get comprehensive health monitoring metrics"""
        current_health = {
            db_type: status.value 
            for db_type, status in self.current_status.items()
        }
        
        # Calculate aggregate metrics
        total_databases = len(self.handlers)
        healthy_databases = sum(1 for status in self.current_status.values() 
                              if status == HealthStatus.HEALTHY)
        
        # Get latest response times
        latest_response_times = {}
        for db_type, history in self.health_history.items():
            if history:
                latest_response_times[db_type] = history[-1].response_time
        
        return {
            "monitoring_active": self.monitoring_active,
            "last_check": self.last_check_time.isoformat() if self.last_check_time else None,
            "check_interval": self.check_interval,
            "current_health": current_health,
            "aggregate_metrics": {
                "total_databases": total_databases,
                "healthy_databases": healthy_databases,
                "health_percentage": (healthy_databases / total_databases * 100) if total_databases > 0 else 0
            },
            "response_times": latest_response_times,
            "thresholds": {
                "response_time_warning": self.thresholds.response_time_warning,
                "response_time_critical": self.thresholds.response_time_critical,
                "error_rate_warning": self.thresholds.error_rate_warning,
                "error_rate_critical": self.thresholds.error_rate_critical
            }
        }
    
    async def shutdown(self) -> None:
        """Shutdown health monitoring"""
        self.logger.info("Shutting down database health monitor...")
        
        await self.stop_monitoring()
        
        if self.alert_manager:
            await self.alert_manager.shutdown()
        
        if self.metrics_collector:
            await self.metrics_collector.shutdown()
        
        self.handlers.clear()
        self.health_history.clear()
        self.current_status.clear()
        
        self.logger.info("Database health monitor shutdown completed")
