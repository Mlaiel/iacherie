"""Database Performance Monitor

Advanced real-time database performance monitoring with AI-powered optimization recommendations.
Tracks query execution times, resource utilization, and provides intelligent performance insights.

Author: Fahed Mlaiel <mlaiel@live.de>
Project: IA Influencer Agent + Content Protection Platform
Copyright: All rights reserved. Unauthorized use, modification, or distribution prohibited.

⚠️  AVERTISSEMENT STRICT ⚠️
Toute utilisation, modification ou distribution non autorisée de ce code est strictement interdite.
Propriété intellectuelle de Fahed Mlaiel (mlaiel@live.de).
"""import asyncio
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, asdict
from enum import Enum
import psutil
import asyncpg
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
import logging
from collections import defaultdict, deque
import statistics
import json

from ..core.database import get_database_session
from ..models.monitoring import PerformanceMetric, QueryStatistics
from ...core.config import Settings
from ...utils.cache import RedisCache
from ...ai.analysis.performance_ai import PerformanceAnalysisAI


class PerformanceLevel(Enum):
    """Performance level classification"""    EXCELLENT = "excellent"
    GOOD = "good"
    WARNING = "warning"
    CRITICAL = "critical"
    EMERGENCY = "emergency"


@dataclass
class PerformanceSnapshot:
    """Single performance measurement snapshot"""    timestamp: datetime
    cpu_usage: float
    memory_usage: float
    disk_io: Dict[str, float]
    active_connections: int
    query_count: int
    slow_queries: int
    avg_query_time: float
    cache_hit_ratio: float
    lock_waits: int
    deadlocks: int
    performance_level: PerformanceLevel
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""        data = asdict(self)
        data['timestamp'] = self.timestamp.isoformat()
        data['performance_level'] = self.performance_level.value
        return data


@dataclass
class PerformanceAlert:
    """Performance alert definition"""    alert_id: str
    severity: str
    metric: str
    threshold: float
    current_value: float
    message: str
    timestamp: datetime
    suggested_actions: List[str]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""        data = asdict(self)
        data['timestamp'] = self.timestamp.isoformat()
        return data


class DatabasePerformanceMonitor:
    """    Advanced database performance monitoring system with AI-powered insights.
    
    Features:
    - Real-time performance tracking
    - AI-powered analysis and recommendations
    - Automated alerting system
    - Performance trend analysis
    - Query optimization suggestions
    - Resource utilization monitoring
    """    
    def __init__(self, settings: Settings):
        self.settings = settings
        self.logger = logging.getLogger(__name__)
        self.cache = RedisCache()
        self.ai_analyzer = PerformanceAnalysisAI()
        
        # Performance data storage
        self.performance_history: deque = deque(maxlen=1440)  # 24 hours of minutes
        self.alert_callbacks: List[Callable] = []
        self.monitoring_active = False
        
        # Metrics tracking
        self.query_times: defaultdict = defaultdict(list)
        self.connection_pool_stats = defaultdict(int)
        self.cache_stats = defaultdict(int)
        
        # Alert thresholds
        self.thresholds = {
            'cpu_usage': 80.0,
            'memory_usage': 85.0,
            'avg_query_time': 1000.0,  # milliseconds
            'cache_hit_ratio': 0.8,
            'active_connections': 100,
            'slow_queries_per_minute': 10
        }
        
        self.logger.info("Database Performance Monitor initialized")
    
    async def start_monitoring(self, interval: int = 60) -> None:
        """        Start continuous performance monitoring
        
        Args:
            interval: Monitoring interval in seconds
        """        if self.monitoring_active:
            self.logger.warning("Performance monitoring already active")
            return
        
        self.monitoring_active = True
        self.logger.info(f"Starting performance monitoring with {interval}s interval")
        
        try:
            while self.monitoring_active:
                snapshot = await self._collect_performance_snapshot()
                await self._process_snapshot(snapshot)
                await asyncio.sleep(interval)
        except Exception as e:
            self.logger.error(f"Performance monitoring error: {e}")
            self.monitoring_active = False
            raise
    
    async def stop_monitoring(self) -> None:
        """Stop performance monitoring"""        self.monitoring_active = False
        self.logger.info("Performance monitoring stopped")
    
    async def _collect_performance_snapshot(self) -> PerformanceSnapshot:
        """Collect current performance metrics"""        try:
            # System metrics
            cpu_usage = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk_io = psutil.disk_io_counters()._asdict()
            
            # Database metrics
            async with get_database_session() as session:
                db_stats = await self._get_database_statistics(session)
            
            # Calculate performance level
            performance_level = self._calculate_performance_level(
                cpu_usage, memory.percent, db_stats
            )
            
            snapshot = PerformanceSnapshot(
                timestamp=datetime.utcnow(),
                cpu_usage=cpu_usage,
                memory_usage=memory.percent,
                disk_io=disk_io,
                active_connections=db_stats.get('active_connections', 0),
                query_count=db_stats.get('query_count', 0),
                slow_queries=db_stats.get('slow_queries', 0),
                avg_query_time=db_stats.get('avg_query_time', 0),
                cache_hit_ratio=db_stats.get('cache_hit_ratio', 0),
                lock_waits=db_stats.get('lock_waits', 0),
                deadlocks=db_stats.get('deadlocks', 0),
                performance_level=performance_level
            )
            
            return snapshot
            
        except Exception as e:
            self.logger.error(f"Error collecting performance snapshot: {e}")
            raise
    
    async def _get_database_statistics(self, session: AsyncSession) -> Dict[str, Any]:
        """Get current database statistics"""        stats = {}
        
        try:
            # Active connections
            result = await session.execute(text("""                SELECT count(*) as active_connections
                FROM pg_stat_activity 
                WHERE state = 'active'
            """))
            stats['active_connections'] = result.scalar() or 0
            
            # Query statistics
            result = await session.execute(text("""                SELECT 
                    sum(calls) as query_count,
                    avg(mean_exec_time) as avg_query_time,
                    count(*) filter (where mean_exec_time > 1000) as slow_queries
                FROM pg_stat_statements 
                WHERE query != '<insufficient privilege>'
            """))
            row = result.fetchone()
            if row:
                stats['query_count'] = row.query_count or 0
                stats['avg_query_time'] = row.avg_query_time or 0
                stats['slow_queries'] = row.slow_queries or 0
            
            # Cache hit ratio
            result = await session.execute(text("""                SELECT 
                    sum(heap_blks_hit) / nullif(sum(heap_blks_hit + heap_blks_read), 0) as cache_hit_ratio
                FROM pg_statio_user_tables
            """))
            stats['cache_hit_ratio'] = result.scalar() or 0
            
            # Lock waits and deadlocks
            result = await session.execute(text("""                SELECT 
                    count(*) filter (where wait_event_type = 'Lock') as lock_waits,
                    (SELECT sum(deadlocks) FROM pg_stat_database) as deadlocks
                FROM pg_stat_activity
            """))
            row = result.fetchone()
            if row:
                stats['lock_waits'] = row.lock_waits or 0
                stats['deadlocks'] = row.deadlocks or 0
            
        except Exception as e:
            self.logger.error(f"Error getting database statistics: {e}")
        
        return stats
    
    def _calculate_performance_level(
        self, 
        cpu_usage: float, 
        memory_usage: float, 
        db_stats: Dict[str, Any]
    ) -> PerformanceLevel:
        """Calculate overall performance level"""        
        # Critical conditions
        if (cpu_usage > 95 or memory_usage > 95 or 
            db_stats.get('avg_query_time', 0) > 5000):
            return PerformanceLevel.EMERGENCY
        
        # Warning conditions
        critical_count = 0
        if cpu_usage > self.thresholds['cpu_usage']:
            critical_count += 1
        if memory_usage > self.thresholds['memory_usage']:
            critical_count += 1
        if db_stats.get('avg_query_time', 0) > self.thresholds['avg_query_time']:
            critical_count += 1
        if db_stats.get('cache_hit_ratio', 1) < self.thresholds['cache_hit_ratio']:
            critical_count += 1
        
        if critical_count >= 3:
            return PerformanceLevel.CRITICAL
        elif critical_count >= 2:
            return PerformanceLevel.WARNING
        elif critical_count >= 1:
            return PerformanceLevel.GOOD
        else:
            return PerformanceLevel.EXCELLENT
    
    async def _process_snapshot(self, snapshot: PerformanceSnapshot) -> None:
        """Process performance snapshot and generate alerts"""        # Store snapshot
        self.performance_history.append(snapshot)
        
        # Cache recent data
        await self.cache.set(
            "performance:latest",
            json.dumps(snapshot.to_dict()),
            expire=300
        )
        
        # Check for alerts
        alerts = await self._check_performance_alerts(snapshot)
        
        # Send alerts
        for alert in alerts:
            await self._send_alert(alert)
        
        # AI analysis for optimization recommendations
        if len(self.performance_history) >= 10:
            await self._run_ai_analysis()
    
    async def _check_performance_alerts(
        self, 
        snapshot: PerformanceSnapshot
    ) -> List[PerformanceAlert]:
        """Check for performance alerts"""        alerts = []
        
        # CPU usage alert
        if snapshot.cpu_usage > self.thresholds['cpu_usage']:
            alerts.append(PerformanceAlert(
                alert_id=f"cpu_high_{int(time.time())}",
                severity="warning" if snapshot.cpu_usage < 90 else "critical",
                metric="cpu_usage",
                threshold=self.thresholds['cpu_usage'],
                current_value=snapshot.cpu_usage,
                message=f"High CPU usage: {snapshot.cpu_usage:.1f}%",
                timestamp=snapshot.timestamp,
                suggested_actions=[
                    "Check for resource-intensive queries",
                    "Consider query optimization",
                    "Review connection pool settings"
                ]
            ))
        
        # Memory usage alert
        if snapshot.memory_usage > self.thresholds['memory_usage']:
            alerts.append(PerformanceAlert(
                alert_id=f"memory_high_{int(time.time())}",
                severity="warning" if snapshot.memory_usage < 90 else "critical",
                metric="memory_usage",
                threshold=self.thresholds['memory_usage'],
                current_value=snapshot.memory_usage,
                message=f"High memory usage: {snapshot.memory_usage:.1f}%",
                timestamp=snapshot.timestamp,
                suggested_actions=[
                    "Check for memory leaks",
                    "Optimize query result sets",
                    "Consider increasing available memory"
                ]
            ))
        
        # Slow queries alert
        if snapshot.avg_query_time > self.thresholds['avg_query_time']:
            alerts.append(PerformanceAlert(
                alert_id=f"slow_queries_{int(time.time())}",
                severity="warning",
                metric="avg_query_time",
                threshold=self.thresholds['avg_query_time'],
                current_value=snapshot.avg_query_time,
                message=f"High average query time: {snapshot.avg_query_time:.1f}ms",
                timestamp=snapshot.timestamp,
                suggested_actions=[
                    "Analyze slow query log",
                    "Add missing indexes",
                    "Optimize query patterns"
                ]
            ))
        
        # Cache hit ratio alert
        if snapshot.cache_hit_ratio < self.thresholds['cache_hit_ratio']:
            alerts.append(PerformanceAlert(
                alert_id=f"cache_low_{int(time.time())}",
                severity="warning",
                metric="cache_hit_ratio",
                threshold=self.thresholds['cache_hit_ratio'],
                current_value=snapshot.cache_hit_ratio,
                message=f"Low cache hit ratio: {snapshot.cache_hit_ratio:.1%}",
                timestamp=snapshot.timestamp,
                suggested_actions=[
                    "Increase shared_buffers",
                    "Optimize query patterns",
                    "Consider query result caching"
                ]
            ))
        
        return alerts
    
    async def _send_alert(self, alert: PerformanceAlert) -> None:
        """Send performance alert"""        try:
            # Store alert
            await self.cache.lpush(
                "performance:alerts",
                json.dumps(alert.to_dict())
            )
            
            # Notify callbacks
            for callback in self.alert_callbacks:
                try:
                    await callback(alert)
                except Exception as e:
                    self.logger.error(f"Alert callback error: {e}")
            
            self.logger.warning(f"Performance alert: {alert.message}")
            
        except Exception as e:
            self.logger.error(f"Error sending alert: {e}")
    
    async def _run_ai_analysis(self) -> None:
        """Run AI analysis on performance data"""        try:
            # Get recent performance data
            recent_data = list(self.performance_history)[-60:]  # Last hour
            
            # Run AI analysis
            recommendations = await self.ai_analyzer.analyze_performance_trends(
                [snapshot.to_dict() for snapshot in recent_data]
            )
            
            # Store recommendations
            await self.cache.set(
                "performance:ai_recommendations",
                json.dumps(recommendations),
                expire=3600
            )
            
        except Exception as e:
            self.logger.error(f"AI analysis error: {e}")
    
    async def get_performance_summary(
        self, 
        hours: int = 24
    ) -> Dict[str, Any]:
        """Get performance summary for specified hours"""        try:
            cutoff_time = datetime.utcnow() - timedelta(hours=hours)
            recent_snapshots = [
                s for s in self.performance_history 
                if s.timestamp >= cutoff_time
            ]
            
            if not recent_snapshots:
                return {"error": "No performance data available"}
            
            # Calculate statistics
            cpu_values = [s.cpu_usage for s in recent_snapshots]
            memory_values = [s.memory_usage for s in recent_snapshots]
            query_times = [s.avg_query_time for s in recent_snapshots]
            
            summary = {
                "period_hours": hours,
                "sample_count": len(recent_snapshots),
                "cpu_usage": {
                    "avg": statistics.mean(cpu_values),
                    "max": max(cpu_values),
                    "min": min(cpu_values),
                    "std": statistics.stdev(cpu_values) if len(cpu_values) > 1 else 0
                },
                "memory_usage": {
                    "avg": statistics.mean(memory_values),
                    "max": max(memory_values),
                    "min": min(memory_values),
                    "std": statistics.stdev(memory_values) if len(memory_values) > 1 else 0
                },
                "query_performance": {
                    "avg_time": statistics.mean(query_times),
                    "max_time": max(query_times),
                    "min_time": min(query_times),
                    "std": statistics.stdev(query_times) if len(query_times) > 1 else 0
                },
                "performance_levels": {
                    level.value: sum(1 for s in recent_snapshots if s.performance_level == level)
                    for level in PerformanceLevel
                },
                "latest_snapshot": recent_snapshots[-1].to_dict()
            }
            
            return summary
            
        except Exception as e:
            self.logger.error(f"Error getting performance summary: {e}")
            return {"error": str(e)}
    
    def add_alert_callback(self, callback: Callable) -> None:
        """Add alert callback function"""        self.alert_callbacks.append(callback)
    
    async def get_recent_alerts(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Get recent performance alerts"""        try:
            alerts_data = await self.cache.lrange("performance:alerts", 0, limit - 1)
            return [json.loads(alert) for alert in alerts_data]
        except Exception as e:
            self.logger.error(f"Error getting recent alerts: {e}")
            return []
    
    async def get_ai_recommendations(self) -> Dict[str, Any]:
        """Get latest AI performance recommendations"""        try:
            recommendations_data = await self.cache.get("performance:ai_recommendations")
            if recommendations_data:
                return json.loads(recommendations_data)
            return {"recommendations": [], "analysis_timestamp": None}
        except Exception as e:
            self.logger.error(f"Error getting AI recommendations: {e}")
            return {"error": str(e)}
