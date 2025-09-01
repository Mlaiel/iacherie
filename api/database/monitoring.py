"""Database Monitoring and Health Management - IA Influencer Agent Platform
Enterprise-grade database monitoring, health checks, and performance analytics

Author: Fahed Mlaiel <mlaiel@live.de>
Team Specialties: Lead AI Developer, Senior Backend Engineer, ML Engineer, 
Database Administrator, Security Expert, Microservices Architect, Audio Engineer, 
DevOps Engineer, AI Prompt Engineer

WARNING: This code is protected by copyright. Any unauthorized use, reproduction,
or distribution without written permission from Fahed Mlaiel is strictly prohibited.
Contact: mlaiel@live.de for licensing and permissions.
"""

import asyncio
import psutil
import time
import json
from typing import Dict, List, Optional, Any, Callable, NamedTuple
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from enum import Enum
from abc import ABC, abstractmethod
import logging
from contextlib import asynccontextmanager

from sqlalchemy import text, func
from sqlalchemy.ext.asyncio import AsyncSession
import redis
import asyncpg

from ..core.config import get_settings
from ..core.logging import get_logger
from .connection import DatabaseConnection, SessionManager
from .cache import get_cache

logger = get_logger(__name__)
settings = get_settings()


class HealthStatus(Enum):
    """
Health check status enumeration"""

    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    CRITICAL = "critical"
    UNKNOWN = "unknown"


class AlertLevel(Enum):
    """Alert severity levels"""

    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


@dataclass
class DatabaseMetrics:
    """Database performance metrics"""
    # Connection metrics
    active_connections: int = 0
    idle_connections: int = 0
    max_connections: int = 0
    connection_pool_usage: float = 0.0
    
    # Query performance
    avg_query_time: float = 0.0
    slow_queries_count: int = 0
    queries_per_second: float = 0.0
    
    # Resource usage
    cpu_usage: float = 0.0
    memory_usage_mb: int = 0
    disk_usage_mb: int = 0
    disk_io_read_mb: float = 0.0
    disk_io_write_mb: float = 0.0
    
    # Database specific
    cache_hit_ratio: float = 0.0
    index_usage_ratio: float = 0.0
    lock_waits: int = 0
    deadlocks: int = 0
    
    # Replication (if applicable)
    replication_lag_ms: int = 0
    replica_health: bool = True
    
    # Timestamps
    collected_at: datetime = None
    collection_duration_ms: float = 0.0
    
    def __post_init__(self):
        if self.collected_at is None:
            self.collected_at = datetime.utcnow()


@dataclass
class HealthCheckResult:
    """
Health check result"""
    component: str
    status: HealthStatus
    response_time_ms: float
    message: str
    details: Optional[Dict[str, Any]] = None
    checked_at: datetime = None
    
    def __post_init__(self):
        if self.checked_at is None:
            self.checked_at = datetime.utcnow()


@dataclass
class AlertRule:
    """
Alert rule configuration"""
    name: str
    metric_path: str
    operator: str  # gt, gte, lt, lte, eq, ne
    threshold: float
    level: AlertLevel
    window_minutes: int = 5
    min_occurrences: int = 2
    enabled: bool = True
    description: str = ""


@dataclass
class Alert:
    """Generated alert"""
    rule_name: str
    level: AlertLevel
    message: str
    value: float
    threshold: float
    component: str
    triggered_at: datetime
    resolved_at: Optional[datetime] = None
    acknowledged_at: Optional[datetime] = None
    metadata: Optional[Dict[str, Any]] = None


class MetricsCollector(ABC):
    """
Abstract metrics collector interface"""
    
    @abstractmethod
    async def collect_metrics(self) -> Dict[str, Any]:
        """
Collect metrics from the monitored component"""
        pass
    
    @abstractmethod
    async def check_health(self) -> HealthCheckResult:
        """
Perform health check"""
        pass


class PostgreSQLMetricsCollector(MetricsCollector):
    """
PostgreSQL metrics collector"""
    
    def __init__(self, connection: DatabaseConnection):
        self.connection = connection
        self.session_manager = SessionManager()
    
    async def collect_metrics(self) -> Dict[str, Any]:
        """
Collect PostgreSQL metrics"""
        start_time = time.time()
        
        try:
            async with self.session_manager.get_async_session() as session:
                # Connection metrics
                connection_stats = await self._get_connection_stats(session)
                
                # Query performance metrics
                query_stats = await self._get_query_stats(session)
                
                # Database statistics
                db_stats = await self._get_database_stats(session)
                
                # Index usage statistics
                index_stats = await self._get_index_stats(session)
                
                # Lock statistics
                lock_stats = await self._get_lock_stats(session)
                
                # Replication statistics (if applicable)
                replication_stats = await self._get_replication_stats(session)
                
                # System resource usage
                system_stats = self._get_system_stats()
                
                collection_time = (time.time() - start_time) * 1000
                
                return DatabaseMetrics(
                    # Connection metrics
                    active_connections=connection_stats.get('active', 0),
                    idle_connections=connection_stats.get('idle', 0),
                    max_connections=connection_stats.get('max_conn', 100),
                    connection_pool_usage=connection_stats.get('usage_ratio', 0.0),
                    
                    # Query performance
                    avg_query_time=query_stats.get('avg_time', 0.0),
                    slow_queries_count=query_stats.get('slow_queries', 0),
                    queries_per_second=query_stats.get('qps', 0.0),
                    
                    # Resource usage
                    cpu_usage=system_stats.get('cpu_percent', 0.0),
                    memory_usage_mb=system_stats.get('memory_mb', 0),
                    disk_usage_mb=system_stats.get('disk_mb', 0),
                    disk_io_read_mb=system_stats.get('disk_read_mb', 0.0),
                    disk_io_write_mb=system_stats.get('disk_write_mb', 0.0),
                    
                    # Database specific
                    cache_hit_ratio=db_stats.get('cache_hit_ratio', 0.0),
                    index_usage_ratio=index_stats.get('usage_ratio', 0.0),
                    lock_waits=lock_stats.get('lock_waits', 0),
                    deadlocks=lock_stats.get('deadlocks', 0),
                    
                    # Replication
                    replication_lag_ms=replication_stats.get('lag_ms', 0),
                    replica_health=replication_stats.get('healthy', True),
                    
                    collection_duration_ms=collection_time
                )
        
        except Exception as e:
            logger.error(f"Error collecting PostgreSQL metrics: {e}")
            return DatabaseMetrics(collection_duration_ms=(time.time() - start_time) * 1000)
    
    async def check_health(self) -> HealthCheckResult:
        """Perform PostgreSQL health check"""
        start_time = time.time()
        
        try:
            async with self.session_manager.get_async_session() as session:
                # Simple SELECT 1 test
                result = await session.execute(text("SELECT 1 as test"))
                row = result.fetchone()
                
                response_time = (time.time() - start_time) * 1000
                
                if row and row.test == 1:
                    if response_time < 100:
                        status = HealthStatus.HEALTHY
                        message = "PostgreSQL is healthy"
                    elif response_time < 1000:
                        status = HealthStatus.DEGRADED
                        message = f"PostgreSQL responding slowly ({response_time:.1f}ms)"
                    else:
                        status = HealthStatus.UNHEALTHY
                        message = f"PostgreSQL very slow response ({response_time:.1f}ms)"
                else:
                    status = HealthStatus.CRITICAL
                    message = "PostgreSQL query failed"
                
                return HealthCheckResult(
                    component="postgresql",
                    status=status,
                    response_time_ms=response_time,
                    message=message,
                    details={"query": "SELECT 1"}
                )
        
        except Exception as e:
            response_time = (time.time() - start_time) * 1000
            logger.error(f"PostgreSQL health check failed: {e}")
            
            return HealthCheckResult(
                component="postgresql",
                status=HealthStatus.CRITICAL,
                response_time_ms=response_time,
                message=f"PostgreSQL connection failed: {str(e)}"
            )
    
    async def _get_connection_stats(self, session: AsyncSession) -> Dict[str, Any]:
        """Get connection statistics"""
        try:
            query = text("""
                SELECT 
                    state,
                    COUNT(*) as count
                FROM pg_stat_activity 
                WHERE datname = current_database()
                GROUP BY state
            """)
            
            result = await session.execute(query)
            rows = result.fetchall()
            
            stats = {}
            total_connections = 0
            
            for row in rows:
                stats[row.state or 'unknown'] = row.count
                total_connections += row.count
            
            # Get max connections
            max_conn_result = await session.execute(text("SHOW max_connections"))
            max_connections = int(max_conn_result.scalar())
            
            return {
                'active': stats.get('active', 0),
                'idle': stats.get('idle', 0),
                'total': total_connections,
                'max_conn': max_connections,
                'usage_ratio': total_connections / max_connections if max_connections > 0 else 0
            }
            
        except Exception as e:
            logger.error(f"Error getting connection stats: {e}")
            return {}
    
    async def _get_query_stats(self, session: AsyncSession) -> Dict[str, Any]:
        """Get query performance statistics"""
        try:
            # Check if pg_stat_statements extension is available
            ext_check = await session.execute(text("""
                SELECT 1 FROM pg_extension WHERE extname = 'pg_stat_statements'
            """))
            
            if not ext_check.scalar():
                return {}
            
            query = text("""
                SELECT 
                    COALESCE(AVG(mean_time), 0) as avg_time,
                    COUNT(CASE WHEN mean_time > 1000 THEN 1 END) as slow_queries,
                    COALESCE(SUM(calls), 0) as total_calls
                FROM pg_stat_statements 
                WHERE dbid = (SELECT oid FROM pg_database WHERE datname = current_database())
                AND query NOT LIKE '%pg_stat_statements%'
            """)
            
            result = await session.execute(query)
            row = result.fetchone()
            
            if row:
                return {
                    'avg_time': float(row.avg_time),
                    'slow_queries': int(row.slow_queries),
                    'qps': float(row.total_calls) / 60  # Approximate QPS over last minute
                }
            
            return {}
            
        except Exception as e:
            logger.debug(f"pg_stat_statements not available: {e}")
            return {}
    
    async def _get_database_stats(self, session: AsyncSession) -> Dict[str, Any]:
        """Get database-level statistics"""
        try:
            query = text("""
                SELECT 
                    CASE 
                        WHEN (blks_hit + blks_read) > 0 
                        THEN (blks_hit::float / (blks_hit + blks_read)) * 100 
                        ELSE 0 
                    END as cache_hit_ratio
                FROM pg_stat_database 
                WHERE datname = current_database()
            """)
            
            result = await session.execute(query)
            row = result.fetchone()
            
            if row:
                return {
                    'cache_hit_ratio': float(row.cache_hit_ratio)
                }
            
            return {}
            
        except Exception as e:
            logger.error(f"Error getting database stats: {e}")
            return {}
    
    async def _get_index_stats(self, session: AsyncSession) -> Dict[str, Any]:
        """Get index usage statistics"""
        try:
            query = text("""
                SELECT 
                    CASE 
                        WHEN SUM(idx_scan + seq_scan) > 0 
                        THEN (SUM(idx_scan)::float / SUM(idx_scan + seq_scan)) * 100 
                        ELSE 0 
                    END as index_usage_ratio
                FROM pg_stat_user_tables
            """)
            
            result = await session.execute(query)
            row = result.fetchone()
            
            if row:
                return {
                    'usage_ratio': float(row.index_usage_ratio or 0)
                }
            
            return {}
            
        except Exception as e:
            logger.error(f"Error getting index stats: {e}")
            return {}
    
    async def _get_lock_stats(self, session: AsyncSession) -> Dict[str, Any]:
        """Get lock statistics"""
        try:
            query = text("""
                SELECT 
                    COUNT(CASE WHEN NOT granted THEN 1 END) as lock_waits
                FROM pg_locks 
                WHERE database = (SELECT oid FROM pg_database WHERE datname = current_database())
            """)
            
            result = await session.execute(query)
            row = result.fetchone()
            
            return {
                'lock_waits': int(row.lock_waits) if row else 0,
                'deadlocks': 0  # Would need deadlock extension or log parsing
            }
            
        except Exception as e:
            logger.error(f"Error getting lock stats: {e}")
            return {}
    
    async def _get_replication_stats(self, session: AsyncSession) -> Dict[str, Any]:
        """Get replication statistics"""
        try:
            # Check if this is a master with replicas
            query = text("""
                SELECT 
                    client_addr,
                    state,
                    EXTRACT(EPOCH FROM (now() - backend_start)) * 1000 as lag_ms
                FROM pg_stat_replication
            """)
            
            result = await session.execute(query)
            rows = result.fetchall()
            
            if rows:
                max_lag = max(row.lag_ms for row in rows)
                healthy_replicas = sum(1 for row in rows if row.state == 'streaming')
                
                return {
                    'lag_ms': int(max_lag),
                    'healthy': healthy_replicas == len(rows),
                    'replica_count': len(rows)
                }
            
            return {
                'lag_ms': 0,
                'healthy': True,
                'replica_count': 0
            }
            
        except Exception as e:
            logger.debug(f"Replication stats not available: {e}")
            return {'lag_ms': 0, 'healthy': True}
    
    def _get_system_stats(self) -> Dict[str, Any]:
        """Get system resource statistics"""
        try:
            # CPU usage
            cpu_percent = psutil.cpu_percent(interval=1)
            
            # Memory usage
            memory = psutil.virtual_memory()
            memory_mb = memory.used // (1024 * 1024)
            
            # Disk usage
            disk = psutil.disk_usage('/')
            disk_mb = disk.used // (1024 * 1024)
            
            # Disk I/O
            disk_io = psutil.disk_io_counters()
            disk_read_mb = disk_io.read_bytes / (1024 * 1024) if disk_io else 0
            disk_write_mb = disk_io.write_bytes / (1024 * 1024) if disk_io else 0
            
            return {
                'cpu_percent': cpu_percent,
                'memory_mb': memory_mb,
                'disk_mb': disk_mb,
                'disk_read_mb': disk_read_mb,
                'disk_write_mb': disk_write_mb
            }
            
        except Exception as e:
            logger.error(f"Error getting system stats: {e}")
            return {}


class RedisMetricsCollector(MetricsCollector):
    """Redis metrics collector"""
    
    def __init__(self, redis_client: redis.Redis):
        self.redis = redis_client
    
    async def collect_metrics(self) -> Dict[str, Any]:
        """
Collect Redis metrics"""
        try:
            info = await self.redis.info()
            
            return {
                'connected_clients': info.get('connected_clients', 0),
                'used_memory': info.get('used_memory', 0),
                'used_memory_human': info.get('used_memory_human', '0B'),
                'hit_rate': self._calculate_hit_rate(info),
                'ops_per_second': info.get('instantaneous_ops_per_sec', 0),
                'keyspace_hits': info.get('keyspace_hits', 0),
                'keyspace_misses': info.get('keyspace_misses', 0),
                'evicted_keys': info.get('evicted_keys', 0),
                'expired_keys': info.get('expired_keys', 0)
            }
            
        except Exception as e:
            logger.error(f"Error collecting Redis metrics: {e}")
            return {}
    
    async def check_health(self) -> HealthCheckResult:
        """Perform Redis health check"""
        start_time = time.time()
        
        try:
            # Simple PING test
            response = await self.redis.ping()
            response_time = (time.time() - start_time) * 1000
            
            if response:
                if response_time < 50:
                    status = HealthStatus.HEALTHY
                    message = "Redis is healthy"
                elif response_time < 200:
                    status = HealthStatus.DEGRADED
                    message = f"Redis responding slowly ({response_time:.1f}ms)"
                else:
                    status = HealthStatus.UNHEALTHY
                    message = f"Redis very slow response ({response_time:.1f}ms)"
            else:
                status = HealthStatus.CRITICAL
                message = "Redis PING failed"
            
            return HealthCheckResult(
                component="redis",
                status=status,
                response_time_ms=response_time,
                message=message
            )
            
        except Exception as e:
            response_time = (time.time() - start_time) * 1000
            logger.error(f"Redis health check failed: {e}")
            
            return HealthCheckResult(
                component="redis",
                status=HealthStatus.CRITICAL,
                response_time_ms=response_time,
                message=f"Redis connection failed: {str(e)}"
            )
    
    def _calculate_hit_rate(self, info: Dict[str, Any]) -> float:
        """Calculate cache hit rate"""
        hits = info.get('keyspace_hits', 0)
        misses = info.get('keyspace_misses', 0)
        
        if hits + misses == 0:
            return 0.0
        
        return (hits / (hits + misses)) * 100


class DatabaseMonitor:
    """
    Comprehensive database monitoring system with health checks,
    metrics collection, alerting, and performance analysis
    """
    
    def __init__(self):
        self.collectors: Dict[str, MetricsCollector] = {}
        self.alert_rules: Dict[str, AlertRule] = {}
        self.active_alerts: Dict[str, Alert] = {}
        self.metrics_history: List[Dict[str, Any]] = []
        self.health_history: List[HealthCheckResult] = []
        self.monitoring_tasks: Dict[str, asyncio.Task] = {}
        self.cache = None
        self._monitoring_active = False
        self.collection_interval = 60  # seconds
        self.health_check_interval = 30  # seconds
    
    async def initialize(self):
        """
Initialize monitoring system"""
        try:
            # Get database connection
            db_connection = await DatabaseConnection.get_instance()
            
            # Initialize PostgreSQL collector
            pg_collector = PostgreSQLMetricsCollector(db_connection)
            self.collectors['postgresql'] = pg_collector
            
            # Initialize Redis collector if available
            redis_conn = db_connection.connections.get('redis_primary')
            if redis_conn:
                redis_collector = RedisMetricsCollector(redis_conn)
                self.collectors['redis'] = redis_collector
            
            # Initialize cache
            self.cache = await get_cache()
            
            # Setup default alert rules
            self._setup_default_alert_rules()
            
            logger.info("Database monitoring system initialized")
            
        except Exception as e:
            logger.error(f"Monitor initialization error: {e}")
            raise
    
    def _setup_default_alert_rules(self):
        """Setup default monitoring alert rules"""
        # Connection pool usage alert
        self.alert_rules['connection_pool_usage'] = AlertRule(
            name="High Connection Pool Usage",
            metric_path="connection_pool_usage",
            operator="gt",
            threshold=80.0,
            level=AlertLevel.WARNING,
            window_minutes=5,
            description="Connection pool usage above 80%"
        )
        
        # Response time alert
        self.alert_rules['slow_response'] = AlertRule(
            name="Slow Database Response",
            metric_path="avg_query_time",
            operator="gt",
            threshold=1000.0,
            level=AlertLevel.ERROR,
            window_minutes=3,
            description="Average query time above 1 second"
        )
        
        # Memory usage alert
        self.alert_rules['high_memory'] = AlertRule(
            name="High Memory Usage",
            metric_path="memory_usage_mb",
            operator="gt",
            threshold=8192.0,  # 8GB
            level=AlertLevel.WARNING,
            window_minutes=10,
            description="Database memory usage above 8GB"
        )
        
        # Cache hit ratio alert
        self.alert_rules['low_cache_hit'] = AlertRule(
            name="Low Cache Hit Ratio",
            metric_path="cache_hit_ratio",
            operator="lt",
            threshold=85.0,
            level=AlertLevel.WARNING,
            window_minutes=15,
            description="Cache hit ratio below 85%"
        )
        
        # Lock waits alert
        self.alert_rules['lock_waits'] = AlertRule(
            name="Database Lock Waits",
            metric_path="lock_waits",
            operator="gt",
            threshold=10.0,
            level=AlertLevel.ERROR,
            window_minutes=2,
            description="High number of lock waits"
        )
    
    async def start_monitoring(self):
        """Start monitoring tasks"""
        if self._monitoring_active:
            logger.warning("Monitoring already active")
            return
        
        self._monitoring_active = True
        
        # Start metrics collection task
        self.monitoring_tasks['metrics'] = asyncio.create_task(
            self._metrics_collection_loop()
        )
        
        # Start health check task
        self.monitoring_tasks['health'] = asyncio.create_task(
            self._health_check_loop()
        )
        
        # Start alert evaluation task
        self.monitoring_tasks['alerts'] = asyncio.create_task(
            self._alert_evaluation_loop()
        )
        
        logger.info("Database monitoring started")
    
    async def stop_monitoring(self):
        """Stop monitoring tasks"""
        self._monitoring_active = False
        
        for task_name, task in self.monitoring_tasks.items():
            if not task.done():
                task.cancel()
                try:
                    await task
                except asyncio.CancelledError:
                    logger.info(f"Cancelled monitoring task: {task_name}")
        
        self.monitoring_tasks.clear()
        logger.info("Database monitoring stopped")
    
    async def _metrics_collection_loop(self):
        """Continuous metrics collection loop"""
        while self._monitoring_active:
            try:
                await self._collect_all_metrics()
                await asyncio.sleep(self.collection_interval)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Metrics collection error: {e}")
                await asyncio.sleep(10)  # Short delay on error
    
    async def _health_check_loop(self):
        """Continuous health check loop"""
        while self._monitoring_active:
            try:
                await self._perform_all_health_checks()
                await asyncio.sleep(self.health_check_interval)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Health check error: {e}")
                await asyncio.sleep(10)  # Short delay on error
    
    async def _alert_evaluation_loop(self):
        """Continuous alert evaluation loop"""
        while self._monitoring_active:
            try:
                await self._evaluate_alert_rules()
                await asyncio.sleep(30)  # Check alerts every 30 seconds
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Alert evaluation error: {e}")
                await asyncio.sleep(10)  # Short delay on error
    
    async def _collect_all_metrics(self):
        """Collect metrics from all registered collectors"""
        timestamp = datetime.utcnow()
        all_metrics = {'timestamp': timestamp}
        
        for component, collector in self.collectors.items():
            try:
                component_metrics = await collector.collect_metrics()
                all_metrics[component] = component_metrics
                
                # Cache individual component metrics
                if self.cache:
                    cache_key = f"metrics:{component}:latest"
                    await self.cache.set(cache_key, component_metrics, ttl=300)
                
            except Exception as e:
                logger.error(f"Error collecting metrics for {component}: {e}")
                all_metrics[component] = {}
        
        # Store in history (keep last 1000 entries)
        self.metrics_history.append(all_metrics)
        if len(self.metrics_history) > 1000:
            self.metrics_history.pop(0)
        
        # Cache aggregated metrics
        if self.cache:
            await self.cache.set('metrics:latest', all_metrics, ttl=120)
    
    async def _perform_all_health_checks(self):
        """Perform health checks on all components"""
        health_results = []
        
        for component, collector in self.collectors.items():
            try:
                health_result = await collector.check_health()
                health_results.append(health_result)
                
                # Cache individual health status
                if self.cache:
                    cache_key = f"health:{component}:latest"
                    await self.cache.set(cache_key, asdict(health_result), ttl=60)
                
            except Exception as e:
                logger.error(f"Error checking health for {component}: {e}")
                health_results.append(HealthCheckResult(
                    component=component,
                    status=HealthStatus.UNKNOWN,
                    response_time_ms=0,
                    message=f"Health check failed: {str(e)}"
                ))
        
        # Store in history (keep last 500 entries)
        self.health_history.extend(health_results)
        if len(self.health_history) > 500:
            self.health_history = self.health_history[-500:]
        
        # Cache aggregated health status
        if self.cache:
            await self.cache.set('health:latest', 
                               [asdict(result) for result in health_results], 
                               ttl=60)
    
    async def _evaluate_alert_rules(self):
        """Evaluate alert rules against current metrics"""
        if not self.metrics_history:
            return
        
        latest_metrics = self.metrics_history[-1]
        
        for rule_name, rule in self.alert_rules.items():
            if not rule.enabled:
                continue
            
            try:
                # Extract metric value
                value = self._extract_metric_value(latest_metrics, rule.metric_path)
                if value is None:
                    continue
                
                # Check threshold
                threshold_breached = self._check_threshold(value, rule.operator, rule.threshold)
                
                if threshold_breached:
                    await self._trigger_alert(rule_name, rule, value)
                else:
                    await self._resolve_alert(rule_name)
                
            except Exception as e:
                logger.error(f"Error evaluating alert rule {rule_name}: {e}")
    
    def _extract_metric_value(self, metrics: Dict[str, Any], metric_path: str) -> Optional[float]:
        """Extract metric value using dot notation path"""
        try:
            parts = metric_path.split('.')
            value = metrics
            
            for part in parts:
                if isinstance(value, dict) and part in value:
                    value = value[part]
                elif hasattr(value, part):
                    value = getattr(value, part)
                else:
                    return None
            
            return float(value) if value is not None else None
            
        except (ValueError, TypeError):
            return None
    
    def _check_threshold(self, value: float, operator: str, threshold: float) -> bool:
        """
Check if value breaches threshold according to operator"""
        if operator == "gt":
            return value > threshold
        elif operator == "gte":
            return value >= threshold
        elif operator == "lt":
            return value < threshold
        elif operator == "lte":
            return value <= threshold
        elif operator == "eq":
            return value == threshold
        elif operator == "ne":
            return value != threshold
        else:
            logger.warning(f"Unknown operator: {operator}")
            return False
    
    async def _trigger_alert(self, rule_name: str, rule: AlertRule, value: float):
        """Trigger an alert"""
        # Check if alert is already active
        if rule_name in self.active_alerts:
            return
        
        alert = Alert(
            rule_name=rule_name,
            level=rule.level,
            message=f"{rule.description}. Current value: {value}, Threshold: {rule.threshold}",
            value=value,
            threshold=rule.threshold,
            component=rule.metric_path.split('.')[0] if '.' in rule.metric_path else 'unknown',
            triggered_at=datetime.utcnow()
        )
        
        self.active_alerts[rule_name] = alert
        
        # Log alert
        logger.warning(f"ALERT TRIGGERED: {alert.message}")
        
        # Cache alert
        if self.cache:
            await self.cache.set(f"alert:{rule_name}", asdict(alert), ttl=3600)
    
    async def _resolve_alert(self, rule_name: str):
        """Resolve an active alert"""
        if rule_name not in self.active_alerts:
            return
        
        alert = self.active_alerts[rule_name]
        alert.resolved_at = datetime.utcnow()
        
        logger.info(f"ALERT RESOLVED: {rule_name}")
        
        # Remove from active alerts
        del self.active_alerts[rule_name]
        
        # Update cached alert
        if self.cache:
            await self.cache.set(f"alert:{rule_name}:resolved", asdict(alert), ttl=3600)
            await self.cache.delete(f"alert:{rule_name}")
    
    async def get_current_metrics(self) -> Optional[Dict[str, Any]]:
        """Get current metrics"""
        if self.cache:
            return await self.cache.get('metrics:latest')
        
        return self.metrics_history[-1] if self.metrics_history else None
    
    async def get_current_health(self) -> Optional[List[Dict[str, Any]]]:
        """
Get current health status"""
        if self.cache:
            return await self.cache.get('health:latest')
        
        return [asdict(result) for result in self.health_history[-len(self.collectors):]] if self.health_history else None
    
    async def get_metrics_history(self, 
                                 component: Optional[str] = None,
                                 hours: int = 24) -> List[Dict[str, Any]]:
        """
Get metrics history"""
        cutoff_time = datetime.utcnow() - timedelta(hours=hours)
        
        history = [
            metrics for metrics in self.metrics_history
            if metrics.get('timestamp', datetime.min) >= cutoff_time
        ]
        
        if component:
            return [
                {
                    'timestamp': metrics.get('timestamp'),
                    component: metrics.get(component, {})
                }
                for metrics in history
            ]
        
        return history
    
    async def get_active_alerts(self) -> List[Dict[str, Any]]:
        """
Get active alerts"""
        return [asdict(alert) for alert in self.active_alerts.values()]


class PerformanceMonitor:
    """
Database performance monitoring and optimization recommendations"""
    
    def __init__(self, database_monitor: DatabaseMonitor):
        self.monitor = database_monitor
        self.performance_thresholds = {
            'slow_query_time': 1000,      # ms
            'high_cpu_usage': 80,         # %
            'low_cache_hit_ratio': 85,    # %
            'high_connection_usage': 80,   # %
            'high_lock_waits': 5          # count
        }
    
    async def analyze_performance(self, hours: int = 1) -> Dict[str, Any]:
        """
Analyze database performance over time period"""
        metrics_history = await self.monitor.get_metrics_history(hours=hours)
        
        if not metrics_history:
            return {'error': 'No metrics data available'}
        
        analysis = {
            'period_hours': hours,
            'data_points': len(metrics_history),
            'performance_score': 0,
            'issues': [],
            'recommendations': [],
            'trends': {},
            'summary': {}
        }
        
        # Analyze trends
        analysis['trends'] = self._analyze_trends(metrics_history)
        
        # Identify performance issues
        analysis['issues'] = self._identify_issues(metrics_history)
        
        # Generate recommendations
        analysis['recommendations'] = self._generate_recommendations(analysis['issues'])
        
        # Calculate performance score
        analysis['performance_score'] = self._calculate_performance_score(analysis['issues'])
        
        # Create summary
        analysis['summary'] = self._create_performance_summary(analysis)
        
        return analysis
    
    def _analyze_trends(self, metrics_history: List[Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
        """
Analyze metric trends"""
        trends = {}
        
        # Define metrics to analyze
        metric_paths = [
            'postgresql.avg_query_time',
            'postgresql.connection_pool_usage',
            'postgresql.cache_hit_ratio',
            'postgresql.cpu_usage',
            'postgresql.memory_usage_mb',
            'redis.hit_rate',
            'redis.ops_per_second'
        ]
        
        for path in metric_paths:
            values = []
            for metrics in metrics_history:
                value = self.monitor._extract_metric_value(metrics, path)
                if value is not None:
                    values.append(value)
            
            if len(values) >= 2:
                trend_direction = 'stable'
                if values[-1] > values[0] * 1.1:
                    trend_direction = 'increasing'
                elif values[-1] < values[0] * 0.9:
                    trend_direction = 'decreasing'
                
                trends[path] = {
                    'direction': trend_direction,
                    'current': values[-1],
                    'previous': values[0],
                    'change_percent': ((values[-1] - values[0]) / values[0]) * 100 if values[0] != 0 else 0,
                    'min': min(values),
                    'max': max(values),
                    'avg': sum(values) / len(values)
                }
        
        return trends
    
    def _identify_issues(self, metrics_history: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
Identify performance issues"""
        issues = []
        
        if not metrics_history:
            return issues
        
        latest_metrics = metrics_history[-1]
        
        # Check slow queries
        avg_query_time = self.monitor._extract_metric_value(
            latest_metrics, 'postgresql.avg_query_time'
        )
        if avg_query_time and avg_query_time > self.performance_thresholds['slow_query_time']:
            issues.append({
                'type': 'slow_queries',
                'severity': 'high',
                'description': f"Average query time is {avg_query_time:.1f}ms (threshold: {self.performance_thresholds['slow_query_time']}ms)",
                'metric': 'postgresql.avg_query_time',
                'value': avg_query_time
            })
        
        # Check CPU usage
        cpu_usage = self.monitor._extract_metric_value(
            latest_metrics, 'postgresql.cpu_usage'
        )
        if cpu_usage and cpu_usage > self.performance_thresholds['high_cpu_usage']:
            issues.append({
                'type': 'high_cpu',
                'severity': 'medium',
                'description': f"High CPU usage at {cpu_usage:.1f}% (threshold: {self.performance_thresholds['high_cpu_usage']}%)",
                'metric': 'postgresql.cpu_usage',
                'value': cpu_usage
            })
        
        # Check cache hit ratio
        cache_hit_ratio = self.monitor._extract_metric_value(
            latest_metrics, 'postgresql.cache_hit_ratio'
        )
        if cache_hit_ratio and cache_hit_ratio < self.performance_thresholds['low_cache_hit_ratio']:
            issues.append({
                'type': 'low_cache_hit',
                'severity': 'medium',
                'description': f"Low cache hit ratio at {cache_hit_ratio:.1f}% (threshold: {self.performance_thresholds['low_cache_hit_ratio']}%)",
                'metric': 'postgresql.cache_hit_ratio',
                'value': cache_hit_ratio
            })
        
        # Check connection pool usage
        conn_usage = self.monitor._extract_metric_value(
            latest_metrics, 'postgresql.connection_pool_usage'
        )
        if conn_usage and conn_usage > self.performance_thresholds['high_connection_usage']:
            issues.append({
                'type': 'high_connections',
                'severity': 'high',
                'description': f"High connection pool usage at {conn_usage:.1f}% (threshold: {self.performance_thresholds['high_connection_usage']}%)",
                'metric': 'postgresql.connection_pool_usage',
                'value': conn_usage
            })
        
        # Check lock waits
        lock_waits = self.monitor._extract_metric_value(
            latest_metrics, 'postgresql.lock_waits'
        )
        if lock_waits and lock_waits > self.performance_thresholds['high_lock_waits']:
            issues.append({
                'type': 'lock_contention',
                'severity': 'high',
                'description': f"High lock waits at {lock_waits} (threshold: {self.performance_thresholds['high_lock_waits']})",
                'metric': 'postgresql.lock_waits',
                'value': lock_waits
            })
        
        return issues
    
    def _generate_recommendations(self, issues: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Generate optimization recommendations based on issues"""
        recommendations = []
        
        for issue in issues:
            issue_type = issue['type']
            
            if issue_type == 'slow_queries':
                recommendations.extend([
                    {
                        'category': 'query_optimization',
                        'priority': 'high',
                        'title': 'Optimize Slow Queries',
                        'description': 'Review and optimize queries taking longer than 1 second',
                        'actions': [
                            'Enable pg_stat_statements extension for query analysis',
                            'Add missing indexes on frequently queried columns',
                            'Rewrite complex queries with better logic',
                            'Consider query result caching'
                        ]
                    }
                ])
            
            elif issue_type == 'high_cpu':
                recommendations.append({
                    'category': 'resource_optimization',
                    'priority': 'medium',
                    'title': 'Reduce CPU Usage',
                    'description': 'Database CPU usage is high',
                    'actions': [
                        'Review CPU-intensive queries',
                        'Consider connection pooling',
                        'Scale database resources',
                        'Optimize query plans'
                    ]
                })
            
            elif issue_type == 'low_cache_hit':
                recommendations.append({
                    'category': 'memory_optimization',
                    'priority': 'medium',
                    'title': 'Improve Cache Hit Ratio',
                    'description': 'Database cache efficiency is low',
                    'actions': [
                        'Increase shared_buffers setting',
                        'Optimize frequently accessed queries',
                        'Review table partitioning strategy',
                        'Consider read replicas for read-heavy workloads'
                    ]
                })
            
            elif issue_type == 'high_connections':
                recommendations.append({
                    'category': 'connection_management',
                    'priority': 'high',
                    'title': 'Optimize Connection Usage',
                    'description': 'Connection pool usage is high',
                    'actions': [
                        'Implement connection pooling (PgBouncer)',
                        'Review application connection handling',
                        'Increase max_connections if needed',
                        'Monitor for connection leaks'
                    ]
                })
            
            elif issue_type == 'lock_contention':
                recommendations.append({
                    'category': 'concurrency_optimization',
                    'priority': 'high',
                    'title': 'Reduce Lock Contention',
                    'description': 'High number of lock waits detected',
                    'actions': [
                        'Review transaction isolation levels',
                        'Optimize long-running transactions',
                        'Consider table partitioning',
                        'Use advisory locks where appropriate'
                    ]
                })
        
        return recommendations
    
    def _calculate_performance_score(self, issues: List[Dict[str, Any]]) -> int:
        """
Calculate overall performance score (0-100)"""
        base_score = 100
        
        for issue in issues:
            severity = issue['severity']
            if severity == 'high':
                base_score -= 20
            elif severity == 'medium':
                base_score -= 10
            elif severity == 'low':
                base_score -= 5
        
        return max(0, base_score)
    
    def _create_performance_summary(self, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """
Create performance summary"""
        issues = analysis.get('issues', [])
        score = analysis.get('performance_score', 0)
        
        high_priority_issues = len([i for i in issues if i.get('severity') == 'high'])
        medium_priority_issues = len([i for i in issues if i.get('severity') == 'medium'])
        
        if score >= 90:
            status = 'excellent'
        elif score >= 80:
            status = 'good'
        elif score >= 70:
            status = 'fair'
        elif score >= 60:
            status = 'poor'
        else:
            status = 'critical'
        
        return {
            'status': status,
            'score': score,
            'total_issues': len(issues),
            'high_priority_issues': high_priority_issues,
            'medium_priority_issues': medium_priority_issues,
            'recommendations_count': len(analysis.get('recommendations', []))
        }


class HealthChecker:
    """
Comprehensive database health checker"""
    
    def __init__(self, database_monitor: DatabaseMonitor):
        self.monitor = database_monitor
    
    async def comprehensive_health_check(self) -> Dict[str, Any]:
        """
Perform comprehensive health check"""
        health_report = {
            'timestamp': datetime.utcnow(),
            'overall_status': HealthStatus.UNKNOWN,
            'components': {},
            'summary': {},
            'recommendations': []
        }
        
        # Get current health status
        current_health = await self.monitor.get_current_health()
        
        if not current_health:
            health_report['overall_status'] = HealthStatus.UNKNOWN
            health_report['summary'] = {'error': 'No health data available'}
            return health_report
        
        # Process component health
        component_statuses = []
        
        for health_data in current_health:
            component = health_data['component']
            status = HealthStatus(health_data['status'])
            response_time = health_data['response_time_ms']
            
            health_report['components'][component] = {
                'status': status.value,
                'response_time_ms': response_time,
                'message': health_data['message'],
                'checked_at': health_data['checked_at']
            }
            
            component_statuses.append(status)
        
        # Determine overall status
        health_report['overall_status'] = self._determine_overall_status(component_statuses)
        
        # Create summary
        health_report['summary'] = self._create_health_summary(component_statuses)
        
        # Generate health recommendations
        health_report['recommendations'] = self._generate_health_recommendations(
            health_report['components']
        )
        
        return health_report
    
    def _determine_overall_status(self, statuses: List[HealthStatus]) -> HealthStatus:
        """
Determine overall health status from component statuses"""
        if not statuses:
            return HealthStatus.UNKNOWN
        
        if any(status == HealthStatus.CRITICAL for status in statuses):
            return HealthStatus.CRITICAL
        elif any(status == HealthStatus.UNHEALTHY for status in statuses):
            return HealthStatus.UNHEALTHY
        elif any(status == HealthStatus.DEGRADED for status in statuses):
            return HealthStatus.DEGRADED
        elif all(status == HealthStatus.HEALTHY for status in statuses):
            return HealthStatus.HEALTHY
        else:
            return HealthStatus.UNKNOWN
    
    def _create_health_summary(self, statuses: List[HealthStatus]) -> Dict[str, Any]:
        """
Create health summary"""
        status_counts = {}
        for status in statuses:
            status_counts[status.value] = status_counts.get(status.value, 0) + 1
        
        return {
            'total_components': len(statuses),
            'healthy_components': status_counts.get('healthy', 0),
            'degraded_components': status_counts.get('degraded', 0),
            'unhealthy_components': status_counts.get('unhealthy', 0),
            'critical_components': status_counts.get('critical', 0),
            'unknown_components': status_counts.get('unknown', 0)
        }
    
    def _generate_health_recommendations(self, components: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
Generate health-based recommendations"""
        recommendations = []
        
        for component, health_data in components.items():
            status = health_data['status']
            response_time = health_data['response_time_ms']
            
            if status == 'critical':
                recommendations.append({
                    'component': component,
                    'priority': 'critical',
                    'title': f'{component.title()} Service Critical',
                    'description': f'{component} service is not responding or has critical issues',
                    'actions': [
                        f'Check {component} service status',
                        'Review error logs',
                        'Restart service if needed',
                        'Escalate to infrastructure team'
                    ]
                })
            
            elif status == 'unhealthy':
                recommendations.append({
                    'component': component,
                    'priority': 'high',
                    'title': f'{component.title()} Service Unhealthy',
                    'description': f'{component} service is experiencing issues',
                    'actions': [
                        f'Monitor {component} service closely',
                        'Check resource usage',
                        'Review recent changes',
                        'Consider service restart'
                    ]
                })
            
            elif status == 'degraded' or response_time > 1000:
                recommendations.append({
                    'component': component,
                    'priority': 'medium',
                    'title': f'{component.title()} Performance Degraded',
                    'description': f'{component} is responding slowly ({response_time:.1f}ms)',
                    'actions': [
                        'Check resource utilization',
                        'Review performance metrics',
                        'Consider scaling resources',
                        'Optimize configuration'
                    ]
                })
        
        return recommendations


class AlertManager:
    """
Alert management system"""
    
    def __init__(self, database_monitor: DatabaseMonitor):
        self.monitor = database_monitor
        self.notification_handlers = []
        self.alert_history = []
    
    def add_notification_handler(self, handler: Callable[[Alert], None]):
        """
Add alert notification handler"""
        self.notification_handlers.append(handler)
    
    async def process_alert(self, alert: Alert):
        """
Process and notify about alert"""
        # Add to history
        self.alert_history.append(alert)
        
        # Keep history manageable
        if len(self.alert_history) > 1000:
            self.alert_history.pop(0)
        
        # Notify handlers
        for handler in self.notification_handlers:
            try:
                handler(alert)
            except Exception as e:
                logger.error(f"Alert notification handler error: {e}")
    
    async def acknowledge_alert(self, rule_name: str, user_id: Optional[str] = None):
        """Acknowledge an active alert"""
        if rule_name in self.monitor.active_alerts:
            alert = self.monitor.active_alerts[rule_name]
            alert.acknowledged_at = datetime.utcnow()
            alert.metadata = alert.metadata or {}
            alert.metadata['acknowledged_by'] = user_id
            
            logger.info(f"Alert acknowledged: {rule_name} by {user_id}")
    
    async def get_alert_history(self, hours: int = 24) -> List[Dict[str, Any]]:
        """Get alert history"""
        cutoff_time = datetime.utcnow() - timedelta(hours=hours)
        
        return [
            asdict(alert) for alert in self.alert_history
            if alert.triggered_at >= cutoff_time
        ]


# Global monitor instance
_monitor_instance: Optional[DatabaseMonitor] = None


async def get_database_monitor() -> DatabaseMonitor:
    """
Get global database monitor instance"""
    global _monitor_instance
    
    if _monitor_instance is None:
        _monitor_instance = DatabaseMonitor()
        await _monitor_instance.initialize()
        await _monitor_instance.start_monitoring()
    
    return _monitor_instance


async def get_performance_monitor() -> PerformanceMonitor:
    """
Get performance monitor instance"""
    monitor = await get_database_monitor()
    return PerformanceMonitor(monitor)


async def get_health_checker() -> HealthChecker:
    """
Get health checker instance"""
    monitor = await get_database_monitor()
    return HealthChecker(monitor)
