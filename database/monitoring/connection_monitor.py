"""Database Connection Monitor

Advanced database connection pool monitoring and management system.
Tracks connection usage, detects leaks, and optimizes pool configuration.

Author: Fahed Mlaiel <mlaiel@live.de>
Project: IA Influencer Agent + Content Protection Platform
Copyright: All rights reserved. Unauthorized use, modification, or distribution prohibited.

⚠️  AVERTISSEMENT STRICT ⚠️
Toute utilisation, modification ou distribution non autorisée de ce code est strictement interdite.
Propriété intellectuelle de Fahed Mlaiel (mlaiel@live.de).
"""
import asyncio
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, asdict
from enum import Enum
import logging
from collections import defaultdict, deque
import json
import traceback
import psutil

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.pool import QueuePool
import asyncpg

from ..core.database import get_database_session, get_connection_pool
from ..models.monitoring import ConnectionMetrics, ConnectionEvent
from ...core.config import Settings
from ...utils.cache import RedisCache
from ...utils.alerting import AlertManager


class ConnectionState(Enum):
    """Database connection states"""    ACTIVE = "active"
    IDLE = "idle"
    IDLE_IN_TRANSACTION = "idle_in_transaction"
    IDLE_IN_TRANSACTION_ABORTED = "idle_in_transaction_aborted"
    FASTPATH_FUNCTION_CALL = "fastpath_function_call"
    DISABLED = "disabled"
    UNKNOWN = "unknown"


class PoolHealth(Enum):
    """Connection pool health status"""    HEALTHY = "healthy"
    WARNING = "warning"
    CRITICAL = "critical"
    EMERGENCY = "emergency"


@dataclass
class ConnectionInfo:
    """Individual connection information"""    connection_id: str
    client_addr: str
    client_hostname: Optional[str]
    client_port: int
    backend_start: datetime
    query_start: Optional[datetime]
    state_change: datetime
    state: ConnectionState
    current_query: Optional[str]
    wait_event_type: Optional[str]
    wait_event: Optional[str]
    application_name: str
    username: str
    database_name: str
    duration_ms: float
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""        data = asdict(self)
        data['backend_start'] = self.backend_start.isoformat()
        data['query_start'] = self.query_start.isoformat() if self.query_start else None
        data['state_change'] = self.state_change.isoformat()
        data['state'] = self.state.value
        return data


@dataclass
class PoolMetrics:
    """Connection pool metrics"""    pool_name: str
    total_connections: int
    active_connections: int
    idle_connections: int
    waiting_connections: int
    max_connections: int
    min_connections: int
    pool_size: int
    overflow: int
    checked_in: int
    checked_out: int
    invalidated: int
    connection_requests_per_second: float
    average_checkout_time_ms: float
    max_checkout_time_ms: float
    pool_utilization_percent: float
    health_status: PoolHealth
    timestamp: datetime
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""        data = asdict(self)
        data['health_status'] = self.health_status.value
        data['timestamp'] = self.timestamp.isoformat()
        return data


@dataclass
class ConnectionLeak:
    """Connection leak detection"""    connection_id: str
    duration_hours: float
    last_query: Optional[str]
    client_info: str
    stack_trace: Optional[str]
    severity: str
    detected_at: datetime
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""        data = asdict(self)
        data['detected_at'] = self.detected_at.isoformat()
        return data


class ConnectionMonitor:
    """    Advanced database connection monitoring system.
    
    Features:
    - Real-time connection tracking
    - Pool utilization monitoring
    - Connection leak detection
    - Automated pool optimization
    - Performance analytics
    - Alerting and notifications
    """    
    def __init__(self, settings: Settings):
        self.settings = settings
        self.logger = logging.getLogger(__name__)
        self.cache = RedisCache()
        self.alert_manager = AlertManager()
        
        # Monitoring state
        self.monitoring_active = False
        self.pool_metrics_history: deque = deque(maxlen=1440)  # 24 hours
        self.connection_events: deque = deque(maxlen=10000)
        self.active_connections: Dict[str, ConnectionInfo] = {}
        self.leaked_connections: List[ConnectionLeak] = []
        
        # Configuration
        self.leak_threshold_hours = 1.0
        self.high_utilization_threshold = 0.8
        self.critical_utilization_threshold = 0.95
        self.max_idle_time_minutes = 30
        
        # Callbacks
        self.alert_callbacks: List[Callable] = []
        
        # Metrics tracking
        self.checkout_times: deque = deque(maxlen=1000)
        self.connection_requests: deque = deque(maxlen=1000)
        
        self.logger.info("Connection Monitor initialized")
    
    async def start_monitoring(self, interval: int = 30) -> None:
        """        Start connection monitoring
        
        Args:
            interval: Monitoring interval in seconds
        """        if self.monitoring_active:
            self.logger.warning("Connection monitoring already active")
            return
        
        self.monitoring_active = True
        self.logger.info(f"Starting connection monitoring with {interval}s interval")
        
        try:
            # Start monitoring tasks
            await asyncio.gather(
                self._monitor_connections(interval),
                self._monitor_pool_metrics(interval),
                self._detect_connection_leaks(interval * 2),
                return_exceptions=True
            )
        except Exception as e:
            self.logger.error(f"Connection monitoring error: {e}")
            self.monitoring_active = False
            raise
    
    async def stop_monitoring(self) -> None:
        """Stop connection monitoring"""        self.monitoring_active = False
        self.logger.info("Connection monitoring stopped")
    
    async def _monitor_connections(self, interval: int) -> None:
        """Monitor individual database connections"""        while self.monitoring_active:
            try:
                await self._collect_connection_data()
                await asyncio.sleep(interval)
            except Exception as e:
                self.logger.error(f"Connection monitoring error: {e}")
                await asyncio.sleep(interval)
    
    async def _monitor_pool_metrics(self, interval: int) -> None:
        """Monitor connection pool metrics"""        while self.monitoring_active:
            try:
                metrics = await self._collect_pool_metrics()
                if metrics:
                    self.pool_metrics_history.append(metrics)
                    await self._process_pool_metrics(metrics)
                
                await asyncio.sleep(interval)
            except Exception as e:
                self.logger.error(f"Pool metrics monitoring error: {e}")
                await asyncio.sleep(interval)
    
    async def _detect_connection_leaks(self, interval: int) -> None:
        """Detect and report connection leaks"""        while self.monitoring_active:
            try:
                await self._check_for_leaks()
                await asyncio.sleep(interval)
            except Exception as e:
                self.logger.error(f"Leak detection error: {e}")
                await asyncio.sleep(interval)
    
    async def _collect_connection_data(self) -> None:
        """Collect current connection information"""        try:
            async with get_database_session() as session:
                # Get active connections
                result = await session.execute(text("""                    SELECT 
                        pid as connection_id,
                        client_addr,
                        client_hostname,
                        client_port,
                        backend_start,
                        query_start,
                        state_change,
                        state,
                        query as current_query,
                        wait_event_type,
                        wait_event,
                        application_name,
                        usename as username,
                        datname as database_name,
                        EXTRACT(EPOCH FROM (now() - backend_start)) * 1000 as duration_ms
                    FROM pg_stat_activity
                    WHERE pid != pg_backend_pid()
                    AND state IS NOT NULL
                """))
                
                current_connections = {}
                
                for row in result:
                    connection_id = str(row.connection_id)
                    
                    # Parse connection state
                    try:
                        state = ConnectionState(row.state.lower())
                    except ValueError:
                        state = ConnectionState.UNKNOWN
                    
                    connection_info = ConnectionInfo(
                        connection_id=connection_id,
                        client_addr=row.client_addr or "unknown",
                        client_hostname=row.client_hostname,
                        client_port=row.client_port or 0,
                        backend_start=row.backend_start,
                        query_start=row.query_start,
                        state_change=row.state_change,
                        state=state,
                        current_query=row.current_query,
                        wait_event_type=row.wait_event_type,
                        wait_event=row.wait_event,
                        application_name=row.application_name or "unknown",
                        username=row.username or "unknown",
                        database_name=row.database_name or "unknown",
                        duration_ms=row.duration_ms or 0
                    )
                    
                    current_connections[connection_id] = connection_info
                
                # Update active connections
                self.active_connections = current_connections
                
                # Cache connection data
                await self.cache.set(
                    "connections:active",
                    json.dumps({
                        conn_id: conn.to_dict() 
                        for conn_id, conn in current_connections.items()
                    }),
                    expire=300
                )
                
        except Exception as e:
            self.logger.error(f"Error collecting connection data: {e}")
    
    async def _collect_pool_metrics(self) -> Optional[PoolMetrics]:
        """Collect connection pool metrics"""        try:
            # Get pool instance
            pool = get_connection_pool()
            if not pool:
                return None
            
            # Collect basic pool stats
            pool_size = getattr(pool, 'size', 0)
            checked_out = getattr(pool, 'checkedout', 0)
            overflow = getattr(pool, 'overflow', 0)
            checked_in = getattr(pool, 'checkedin', 0)
            invalidated = getattr(pool, 'invalidated', 0)
            
            # Calculate connection statistics
            async with get_database_session() as session:
                result = await session.execute(text("""                    SELECT 
                        count(*) as total_connections,
                        count(*) filter (where state = 'active') as active_connections,
                        count(*) filter (where state = 'idle') as idle_connections,
                        max_conn.setting::int as max_connections
                    FROM pg_stat_activity, 
                         (SELECT setting FROM pg_settings WHERE name = 'max_connections') max_conn
                    WHERE pid != pg_backend_pid()
                """))
                
                stats = result.fetchone()
                
                total_connections = stats.total_connections if stats else 0
                active_connections = stats.active_connections if stats else 0
                idle_connections = stats.idle_connections if stats else 0
                max_connections = stats.max_connections if stats else 100
            
            # Calculate rates and utilization
            connection_requests_per_second = self._calculate_request_rate()
            avg_checkout_time = self._calculate_average_checkout_time()
            max_checkout_time = self._calculate_max_checkout_time()
            utilization_percent = (active_connections / max_connections) * 100
            
            # Determine health status
            health_status = self._determine_pool_health(utilization_percent, active_connections)
            
            metrics = PoolMetrics(
                pool_name="main",
                total_connections=total_connections,
                active_connections=active_connections,
                idle_connections=idle_connections,
                waiting_connections=0,  # PostgreSQL doesn't directly expose this
                max_connections=max_connections,
                min_connections=getattr(pool, 'min_size', 5),
                pool_size=pool_size,
                overflow=overflow,
                checked_in=checked_in,
                checked_out=checked_out,
                invalidated=invalidated,
                connection_requests_per_second=connection_requests_per_second,
                average_checkout_time_ms=avg_checkout_time,
                max_checkout_time_ms=max_checkout_time,
                pool_utilization_percent=utilization_percent,
                health_status=health_status,
                timestamp=datetime.utcnow()
            )
            
            return metrics
            
        except Exception as e:
            self.logger.error(f"Error collecting pool metrics: {e}")
            return None
    
    def _calculate_request_rate(self) -> float:
        """Calculate connection requests per second"""        if len(self.connection_requests) < 2:
            return 0.0
        
        # Calculate rate over last minute
        now = time.time()
        recent_requests = [
            req_time for req_time in self.connection_requests
            if now - req_time <= 60
        ]
        
        return len(recent_requests) / 60.0
    
    def _calculate_average_checkout_time(self) -> float:
        """Calculate average connection checkout time"""        if not self.checkout_times:
            return 0.0
        
        return sum(self.checkout_times) / len(self.checkout_times)
    
    def _calculate_max_checkout_time(self) -> float:
        """Calculate maximum connection checkout time"""        if not self.checkout_times:
            return 0.0
        
        return max(self.checkout_times)
    
    def _determine_pool_health(self, utilization_percent: float, active_connections: int) -> PoolHealth:
        """Determine connection pool health status"""        if utilization_percent >= self.critical_utilization_threshold * 100:
            return PoolHealth.EMERGENCY
        elif utilization_percent >= self.high_utilization_threshold * 100:
            return PoolHealth.CRITICAL
        elif utilization_percent >= 70:
            return PoolHealth.WARNING
        else:
            return PoolHealth.HEALTHY
    
    async def _process_pool_metrics(self, metrics: PoolMetrics) -> None:
        """Process pool metrics and generate alerts"""        try:
            # Cache metrics
            await self.cache.set(
                "pool:metrics",
                json.dumps(metrics.to_dict()),
                expire=300
            )
            
            # Check for alerts
            await self._check_pool_alerts(metrics)
            
        except Exception as e:
            self.logger.error(f"Error processing pool metrics: {e}")
    
    async def _check_pool_alerts(self, metrics: PoolMetrics) -> None:
        """Check for pool-related alerts"""        alerts = []
        
        # High utilization alert
        if metrics.pool_utilization_percent >= self.critical_utilization_threshold * 100:
            alerts.append({
                "type": "pool_utilization_critical",
                "severity": "critical",
                "message": f"Connection pool utilization critical: {metrics.pool_utilization_percent:.1f}%",
                "metrics": metrics.to_dict(),
                "suggestions": [
                    "Increase max_connections",
                    "Optimize connection usage",
                    "Implement connection pooling at application level"
                ]
            })
        elif metrics.pool_utilization_percent >= self.high_utilization_threshold * 100:
            alerts.append({
                "type": "pool_utilization_high",
                "severity": "warning",
                "message": f"Connection pool utilization high: {metrics.pool_utilization_percent:.1f}%",
                "metrics": metrics.to_dict(),
                "suggestions": [
                    "Monitor connection usage patterns",
                    "Consider increasing pool size"
                ]
            })
        
        # High checkout time alert
        if metrics.average_checkout_time_ms > 1000:  # > 1 second
            alerts.append({
                "type": "slow_connection_checkout",
                "severity": "warning",
                "message": f"Slow connection checkout: {metrics.average_checkout_time_ms:.1f}ms",
                "metrics": metrics.to_dict(),
                "suggestions": [
                    "Check database connectivity",
                    "Optimize connection establishment"
                ]
            })
        
        # Send alerts
        for alert in alerts:
            await self._send_alert(alert)
    
    async def _check_for_leaks(self) -> None:
        """Check for connection leaks"""        try:
            current_time = datetime.utcnow()
            potential_leaks = []
            
            for conn_id, conn_info in self.active_connections.items():
                # Check connection duration
                duration_hours = conn_info.duration_ms / (1000 * 60 * 60)
                
                if duration_hours > self.leak_threshold_hours:
                    # Check if connection is actually idle
                    if (conn_info.state == ConnectionState.IDLE and 
                        conn_info.query_start and
                        current_time - conn_info.query_start > timedelta(minutes=self.max_idle_time_minutes)):
                        
                        leak = ConnectionLeak(
                            connection_id=conn_id,
                            duration_hours=duration_hours,
                            last_query=conn_info.current_query,
                            client_info=f"{conn_info.client_addr}:{conn_info.client_port}",
                            stack_trace=None,
                            severity="warning" if duration_hours < 2 else "critical",
                            detected_at=current_time
                        )
                        
                        potential_leaks.append(leak)
            
            # Update leaked connections
            self.leaked_connections = potential_leaks
            
            # Cache leak information
            if potential_leaks:
                await self.cache.set(
                    "connections:leaks",
                    json.dumps([leak.to_dict() for leak in potential_leaks]),
                    expire=300
                )
                
                # Send leak alerts
                for leak in potential_leaks:
                    await self._send_leak_alert(leak)
            
        except Exception as e:
            self.logger.error(f"Error checking for leaks: {e}")
    
    async def _send_alert(self, alert: Dict[str, Any]) -> None:
        """Send connection pool alert"""        try:
            # Store alert
            await self.cache.lpush(
                "connections:alerts",
                json.dumps(alert)
            )
            
            # Notify callbacks
            for callback in self.alert_callbacks:
                try:
                    await callback(alert)
                except Exception as e:
                    self.logger.error(f"Alert callback error: {e}")
            
            self.logger.warning(f"Connection alert: {alert['message']}")
            
        except Exception as e:
            self.logger.error(f"Error sending alert: {e}")
    
    async def _send_leak_alert(self, leak: ConnectionLeak) -> None:
        """Send connection leak alert"""        try:
            alert = {
                "type": "connection_leak",
                "severity": leak.severity,
                "message": f"Connection leak detected: {leak.connection_id} ({leak.duration_hours:.1f}h)",
                "leak_info": leak.to_dict(),
                "suggestions": [
                    "Review application connection handling",
                    "Ensure proper connection cleanup",
                    "Check for transaction rollbacks"
                ]
            }
            
            await self._send_alert(alert)
            
        except Exception as e:
            self.logger.error(f"Error sending leak alert: {e}")
    
    async def get_connection_summary(self) -> Dict[str, Any]:
        """Get connection summary"""        try:
            total_connections = len(self.active_connections)
            state_counts = defaultdict(int)
            
            for conn in self.active_connections.values():
                state_counts[conn.state.value] += 1
            
            # Get latest pool metrics
            latest_metrics = None
            if self.pool_metrics_history:
                latest_metrics = self.pool_metrics_history[-1].to_dict()
            
            summary = {
                "total_active_connections": total_connections,
                "connections_by_state": dict(state_counts),
                "detected_leaks": len(self.leaked_connections),
                "pool_metrics": latest_metrics,
                "monitoring_active": self.monitoring_active,
                "last_update": datetime.utcnow().isoformat()
            }
            
            return summary
            
        except Exception as e:
            self.logger.error(f"Error getting connection summary: {e}")
            return {"error": str(e)}
    
    async def get_connection_details(self, connection_id: str = None) -> Dict[str, Any]:
        """Get detailed connection information"""        try:
            if connection_id:
                # Get specific connection
                if connection_id in self.active_connections:
                    return self.active_connections[connection_id].to_dict()
                else:
                    return {"error": "Connection not found"}
            else:
                # Get all connections
                return {
                    conn_id: conn.to_dict()
                    for conn_id, conn in self.active_connections.items()
                }
                
        except Exception as e:
            self.logger.error(f"Error getting connection details: {e}")
            return {"error": str(e)}
    
    async def get_pool_metrics_history(self, hours: int = 24) -> List[Dict[str, Any]]:
        """Get pool metrics history"""        try:
            cutoff_time = datetime.utcnow() - timedelta(hours=hours)
            
            recent_metrics = [
                metrics.to_dict() for metrics in self.pool_metrics_history
                if metrics.timestamp >= cutoff_time
            ]
            
            return recent_metrics
            
        except Exception as e:
            self.logger.error(f"Error getting pool metrics history: {e}")
            return []
    
    async def get_leak_report(self) -> Dict[str, Any]:
        """Get connection leak report"""        try:
            report = {
                "total_leaks": len(self.leaked_connections),
                "leaks_by_severity": defaultdict(int),
                "leaked_connections": [leak.to_dict() for leak in self.leaked_connections],
                "leak_threshold_hours": self.leak_threshold_hours,
                "generated_at": datetime.utcnow().isoformat()
            }
            
            # Count by severity
            for leak in self.leaked_connections:
                report["leaks_by_severity"][leak.severity] += 1
            
            report["leaks_by_severity"] = dict(report["leaks_by_severity"])
            
            return report
            
        except Exception as e:
            self.logger.error(f"Error getting leak report: {e}")
            return {"error": str(e)}
    
    def add_alert_callback(self, callback: Callable) -> None:
        """Add alert callback function"""        self.alert_callbacks.append(callback)
    
    def track_connection_request(self) -> None:
        """Track a connection request"""        self.connection_requests.append(time.time())
    
    def track_checkout_time(self, checkout_time_ms: float) -> None:
        """Track connection checkout time"""        self.checkout_times.append(checkout_time_ms)
    
    async def kill_connection(self, connection_id: str, reason: str = "Manual termination") -> bool:
        """Kill a specific database connection"""        try:
            async with get_database_session() as session:
                result = await session.execute(text(f"SELECT pg_terminate_backend({connection_id})"))
                success = result.scalar()
                
                if success:
                    self.logger.info(f"Terminated connection {connection_id}: {reason}")
                    
                    # Remove from active connections
                    if connection_id in self.active_connections:
                        del self.active_connections[connection_id]
                    
                    return True
                else:
                    self.logger.warning(f"Failed to terminate connection {connection_id}")
                    return False
                    
        except Exception as e:
            self.logger.error(f"Error killing connection {connection_id}: {e}")
            return False
    
    async def kill_idle_connections(self, idle_threshold_minutes: int = 30) -> int:
        """Kill idle connections older than threshold"""        try:
            killed_count = 0
            current_time = datetime.utcnow()
            
            for conn_id, conn_info in list(self.active_connections.items()):
                if (conn_info.state == ConnectionState.IDLE and
                    conn_info.query_start and
                    current_time - conn_info.query_start > timedelta(minutes=idle_threshold_minutes)):
                    
                    if await self.kill_connection(conn_id, f"Idle for {idle_threshold_minutes}+ minutes"):
                        killed_count += 1
            
            if killed_count > 0:
                self.logger.info(f"Killed {killed_count} idle connections")
            
            return killed_count
            
        except Exception as e:
            self.logger.error(f"Error killing idle connections: {e}")
            return 0
