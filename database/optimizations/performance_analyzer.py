"""Performance Analyzer Module

Comprehensive database performance monitoring and analysis system for query optimization,
bottleneck detection, and performance trend analysis.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: All rights reserved. Unauthorized use prohibited.
"""

import asyncio
import time
import statistics
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Set, Tuple, Callable
from enum import Enum
from dataclasses import dataclass, field
from collections import defaultdict, deque
import psutil
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession
from sqlalchemy.engine.events import PoolEvents

from ...core.logging import get_logger
from ...core.config import settings
from ...core.metrics import MetricsCollector

logger = get_logger(__name__)


class PerformanceLevel(Enum):
    """
Performance level indicators"""

    EXCELLENT = "excellent"
    GOOD = "good"
    AVERAGE = "average"
    POOR = "poor"
    CRITICAL = "critical"


class BottleneckType(Enum):
    """Types of performance bottlenecks"""

    CPU = "cpu"
    MEMORY = "memory"
    DISK_IO = "disk_io"
    NETWORK = "network"
    LOCK_CONTENTION = "lock_contention"
    QUERY_OPTIMIZATION = "query_optimization"
    INDEX_MISSING = "index_missing"
    CONNECTION_POOL = "connection_pool"


@dataclass
class QueryMetrics:
    """Individual query performance metrics"""
    query_id: str
    query_text: str
    execution_count: int = 0
    total_time: float = 0.0
    min_time: float = float('inf')
    max_time: float = 0.0
    avg_time: float = 0.0
    std_dev: float = 0.0
    rows_examined: int = 0
    rows_returned: int = 0
    bytes_sent: int = 0
    first_seen: datetime = field(default_factory=datetime.now)
    last_seen: datetime = field(default_factory=datetime.now)
    error_count: int = 0
    
    # Performance indicators
    slowlog_count: int = 0
    full_scan_count: int = 0
    temp_table_count: int = 0
    
    # Execution times for statistical analysis
    _execution_times: deque = field(default_factory=lambda: deque(maxlen=1000))
    
    def add_execution(self, execution_time: float, rows_examined: int = 0, rows_returned: int = 0, error: bool = False) -> None:
        """
Add execution metrics"""
        self.execution_count += 1
        self.total_time += execution_time
        self.min_time = min(self.min_time, execution_time)
        self.max_time = max(self.max_time, execution_time)
        self.avg_time = self.total_time / self.execution_count
        self.rows_examined += rows_examined
        self.rows_returned += rows_returned
        self.last_seen = datetime.now()
        
        if error:
            self.error_count += 1
        
        # Store for statistical analysis
        self._execution_times.append(execution_time)
        
        # Calculate standard deviation
        if len(self._execution_times) > 1:
            self.std_dev = statistics.stdev(self._execution_times)
    
    @property
    def efficiency_ratio(self) -> float:
        """
Calculate query efficiency (rows returned / rows examined)"""
        if self.rows_examined == 0:
            return 1.0
        return self.rows_returned / self.rows_examined
    
    @property
    def performance_score(self) -> float:
        """
Calculate overall performance score (0-100)"""
        score = 100.0
        
        # Penalize slow queries
        if self.avg_time > 5.0:
            score -= 40
        elif self.avg_time > 1.0:
            score -= 20
        elif self.avg_time > 0.1:
            score -= 10
        
        # Penalize inefficient queries
        if self.efficiency_ratio < 0.1:
            score -= 30
        elif self.efficiency_ratio < 0.5:
            score -= 15
        
        # Penalize high variance
        if self.std_dev > self.avg_time:
            score -= 15
        
        # Penalize errors
        if self.error_count > 0:
            error_rate = self.error_count / self.execution_count
            score -= error_rate * 50
        
        return max(0.0, score)
    
    @property
    def performance_level(self) -> PerformanceLevel:
        """
Get performance level based on score"""
        score = self.performance_score
        if score >= 90:
            return PerformanceLevel.EXCELLENT
        elif score >= 75:
            return PerformanceLevel.GOOD
        elif score >= 50:
            return PerformanceLevel.AVERAGE
        elif score >= 25:
            return PerformanceLevel.POOR
        else:
            return PerformanceLevel.CRITICAL


@dataclass
class SystemMetrics:
    """
System-level performance metrics"""
    cpu_usage: float = 0.0
    memory_usage: float = 0.0
    disk_io_read: float = 0.0
    disk_io_write: float = 0.0
    network_io_recv: float = 0.0
    network_io_sent: float = 0.0
    active_connections: int = 0
    total_connections: int = 0
    lock_waits: int = 0
    deadlocks: int = 0
    timestamp: datetime = field(default_factory=datetime.now)
    
    @property
    def connection_utilization(self) -> float:
        """
Calculate connection pool utilization"""
        if self.total_connections == 0:
            return 0.0
        return self.active_connections / self.total_connections


@dataclass
class PerformanceAlert:
    """
Performance alert/anomaly"""
    alert_type: str
    severity: str
    message: str
    query_id: Optional[str] = None
    metric_value: Optional[float] = None
    threshold: Optional[float] = None
    timestamp: datetime = field(default_factory=datetime.now)
    resolved: bool = False


@dataclass
class PerformanceReport:
    """
Comprehensive performance analysis report"""
    start_time: datetime
    end_time: datetime
    total_queries: int
    slow_queries: int
    failed_queries: int
    avg_response_time: float
    p95_response_time: float
    p99_response_time: float
    throughput_qps: float
    error_rate: float
    
    # Top problematic queries
    slowest_queries: List[QueryMetrics]
    most_frequent_queries: List[QueryMetrics]
    most_error_prone_queries: List[QueryMetrics]
    
    # System metrics summary
    avg_cpu_usage: float
    avg_memory_usage: float
    avg_connection_utilization: float
    
    # Recommendations
    performance_alerts: List[PerformanceAlert]
    bottlenecks: List[Dict[str, Any]]
    recommendations: List[str]
    
    @property
    def overall_health_score(self) -> float:
        """
Calculate overall database health score"""
        score = 100.0
        
        # Error rate impact
        if self.error_rate > 0.1:
            score -= 30
        elif self.error_rate > 0.05:
            score -= 15
        elif self.error_rate > 0.01:
            score -= 5
        
        # Response time impact
        if self.avg_response_time > 2.0:
            score -= 25
        elif self.avg_response_time > 1.0:
            score -= 15
        elif self.avg_response_time > 0.5:
            score -= 10
        
        # Resource utilization impact
        if self.avg_cpu_usage > 80:
            score -= 20
        elif self.avg_cpu_usage > 60:
            score -= 10
        
        if self.avg_memory_usage > 80:
            score -= 20
        elif self.avg_memory_usage > 60:
            score -= 10
        
        # Connection utilization
        if self.avg_connection_utilization > 90:
            score -= 15
        elif self.avg_connection_utilization > 75:
            score -= 5
        
        return max(0.0, score)


class PerformanceAnalyzer:
    """
Advanced database performance analyzer"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.metrics_collector = MetricsCollector()
        
        # Query tracking
        self._query_metrics: Dict[str, QueryMetrics] = {}
        self._system_metrics: deque = deque(maxlen=1440)  # 24 hours at 1-minute intervals
        self._alerts: List[PerformanceAlert] = []
        
        # Configuration
        self.slow_query_threshold = self.config.get('slow_query_threshold', 1.0)
        self.alert_thresholds = self.config.get('alert_thresholds', {
            'cpu_usage': 80.0,
            'memory_usage': 80.0,
            'connection_utilization': 90.0,
            'error_rate': 0.05,
            'response_time': 2.0
        })
        
        # Monitoring
        self._monitoring_task: Optional[asyncio.Task] = None
        self._last_report = datetime.now()
        
        # Performance baselines
        self._baseline_metrics: Dict[str, float] = {}
    
    async def start_monitoring(self, engine: AsyncEngine) -> None:
        """
Start continuous performance monitoring"""
        try:
            logger.info("Starting performance monitoring")
            
            # Start system metrics collection
            self._monitoring_task = asyncio.create_task(self._collect_system_metrics())
            
            # Setup query event listeners
            self._setup_query_listeners(engine)
            
            logger.info("Performance monitoring started successfully")
            
        except Exception as e:
            logger.error(f"Failed to start performance monitoring: {e}")
            raise
    
    def _setup_query_listeners(self, engine: AsyncEngine) -> None:
        """Setup SQLAlchemy event listeners for query monitoring"""
        from sqlalchemy import event
        
        @event.listens_for(engine.sync_engine, "before_cursor_execute")
        def before_cursor_execute(conn, cursor, statement, parameters, context, executemany):
            """Track query start time"""
            context._query_start_time = time.time()
            context._statement = statement
        
        @event.listens_for(engine.sync_engine, "after_cursor_execute")
        def after_cursor_execute(conn, cursor, statement, parameters, context, executemany):
            """Track query completion and metrics"""
            if hasattr(context, '_query_start_time'):
                execution_time = time.time() - context._query_start_time
                
                # Extract rows info if available
                rows_returned = cursor.rowcount if hasattr(cursor, 'rowcount') else 0
                
                # Track query
                self.track_query(statement, execution_time, rows_returned=rows_returned)
        
        @event.listens_for(engine.sync_engine, "handle_error")
        def handle_error(exception_context):
            """Track query errors"""
            if hasattr(exception_context, 'statement'):
                self.track_query(
                    exception_context.statement,
                    0.0,  # Unknown execution time
                    error=True
                )
    
    def track_query(
        self,
        query: str,
        execution_time: float,
        rows_examined: int = 0,
        rows_returned: int = 0,
        error: bool = False
    ) -> None:
        """
Track query execution metrics"""
        try:
            # Generate query ID (normalized)
            query_id = self._generate_query_id(query)
            
            # Get or create query metrics
            if query_id not in self._query_metrics:
                self._query_metrics[query_id] = QueryMetrics(
                    query_id=query_id,
                    query_text=self._normalize_query(query)
                )
            
            # Update metrics
            metrics = self._query_metrics[query_id]
            metrics.add_execution(execution_time, rows_examined, rows_returned, error)
            
            # Check for slow query alert
            if execution_time > self.slow_query_threshold:
                self._create_alert(
                    "slow_query",
                    "warning",
                    f"Slow query detected: {execution_time:.2f}s",
                    query_id=query_id,
                    metric_value=execution_time,
                    threshold=self.slow_query_threshold
                )
            
            # Send metrics to collector
            self.metrics_collector.histogram(
                "database_query_duration_seconds",
                execution_time,
                {"query_id": query_id[:8]}  # Short ID for labels
            )
            
            if error:
                self.metrics_collector.counter(
                    "database_query_errors_total",
                    1,
                    {"query_id": query_id[:8]}
                )
            
        except Exception as e:
            logger.warning(f"Failed to track query metrics: {e}")
    
    def _generate_query_id(self, query: str) -> str:
        """Generate normalized query ID"""
        import hashlib
        normalized = self._normalize_query(query)
        return hashlib.md5(normalized.encode()).hexdigest()
    
    def _normalize_query(self, query: str) -> str:
        """
Normalize query for pattern matching"""
        import re
        
        # Convert to lowercase and remove extra whitespace
        normalized = re.sub(r'\s+', ' ', query.lower().strip())
        
        # Replace literals with placeholders
        normalized = re.sub(r"'[^']*'", "?", normalized)
        normalized = re.sub(r'\b\d+\b', "?", normalized)
        normalized = re.sub(r'\$\d+', "?", normalized)
        
        # Remove comments
        normalized = re.sub(r'--.*?$', '', normalized, flags=re.MULTILINE)
        normalized = re.sub(r'/\*.*?\*/', '', normalized, flags=re.DOTALL)
        
        return normalized.strip()
    
    async def _collect_system_metrics(self) -> None:
        """Collect system-level performance metrics"""
        while True:
            try:
                await asyncio.sleep(60)  # Collect every minute
                
                # CPU usage
                cpu_usage = psutil.cpu_percent(interval=1)
                
                # Memory usage
                memory = psutil.virtual_memory()
                memory_usage = memory.percent
                
                # Disk I/O
                disk_io = psutil.disk_io_counters()
                disk_read = disk_io.read_bytes if disk_io else 0
                disk_write = disk_io.write_bytes if disk_io else 0
                
                # Network I/O
                network_io = psutil.net_io_counters()
                network_recv = network_io.bytes_recv if network_io else 0
                network_sent = network_io.bytes_sent if network_io else 0
                
                # Create system metrics
                system_metrics = SystemMetrics(
                    cpu_usage=cpu_usage,
                    memory_usage=memory_usage,
                    disk_io_read=disk_read,
                    disk_io_write=disk_write,
                    network_io_recv=network_recv,
                    network_io_sent=network_sent
                )
                
                self._system_metrics.append(system_metrics)
                
                # Check for alerts
                await self._check_system_alerts(system_metrics)
                
                # Send metrics
                self.metrics_collector.gauge("system_cpu_usage_percent", cpu_usage)
                self.metrics_collector.gauge("system_memory_usage_percent", memory_usage)
                self.metrics_collector.gauge("system_disk_read_bytes", disk_read)
                self.metrics_collector.gauge("system_disk_write_bytes", disk_write)
                
            except Exception as e:
                logger.error(f"System metrics collection error: {e}")
    
    async def _check_system_alerts(self, metrics: SystemMetrics) -> None:
        """Check system metrics against alert thresholds"""
        # CPU usage alert
        if metrics.cpu_usage > self.alert_thresholds.get('cpu_usage', 80):
            self._create_alert(
                "high_cpu_usage",
                "warning",
                f"High CPU usage: {metrics.cpu_usage:.1f}%",
                metric_value=metrics.cpu_usage,
                threshold=self.alert_thresholds['cpu_usage']
            )
        
        # Memory usage alert
        if metrics.memory_usage > self.alert_thresholds.get('memory_usage', 80):
            self._create_alert(
                "high_memory_usage",
                "warning",
                f"High memory usage: {metrics.memory_usage:.1f}%",
                metric_value=metrics.memory_usage,
                threshold=self.alert_thresholds['memory_usage']
            )
        
        # Connection utilization alert
        if metrics.connection_utilization > self.alert_thresholds.get('connection_utilization', 90):
            self._create_alert(
                "high_connection_utilization",
                "critical",
                f"High connection utilization: {metrics.connection_utilization:.1f}%",
                metric_value=metrics.connection_utilization,
                threshold=self.alert_thresholds['connection_utilization']
            )
    
    def _create_alert(
        self,
        alert_type: str,
        severity: str,
        message: str,
        query_id: Optional[str] = None,
        metric_value: Optional[float] = None,
        threshold: Optional[float] = None
    ) -> None:
        """Create a performance alert"""
        alert = PerformanceAlert(
            alert_type=alert_type,
            severity=severity,
            message=message,
            query_id=query_id,
            metric_value=metric_value,
            threshold=threshold
        )
        
        self._alerts.append(alert)
        
        # Keep only recent alerts (last 24 hours)
        cutoff_time = datetime.now() - timedelta(hours=24)
        self._alerts = [a for a in self._alerts if a.timestamp > cutoff_time]
        
        logger.warning(f"Performance alert: {alert.severity.upper()} - {message}")
        
        # Send alert metric
        self.metrics_collector.counter(
            "database_performance_alerts_total",
            1,
            {"type": alert_type, "severity": severity}
        )
    
    async def generate_report(self, start_time: datetime, end_time: datetime) -> PerformanceReport:
        """Generate comprehensive performance report"""
        try:
            logger.info(f"Generating performance report from {start_time} to {end_time}")
            
            # Filter queries by time window
            relevant_queries = [
                q for q in self._query_metrics.values()
                if start_time <= q.last_seen <= end_time
            ]
            
            if not relevant_queries:
                logger.warning("No queries found in specified time window")
                return self._create_empty_report(start_time, end_time)
            
            # Calculate aggregate metrics
            total_queries = sum(q.execution_count for q in relevant_queries)
            slow_queries = sum(1 for q in relevant_queries if q.avg_time > self.slow_query_threshold)
            failed_queries = sum(q.error_count for q in relevant_queries)
            
            # Response time percentiles
            all_times = []
            for q in relevant_queries:
                all_times.extend(list(q._execution_times))
            
            if all_times:
                avg_response_time = statistics.mean(all_times)
                p95_response_time = self._percentile(all_times, 95)
                p99_response_time = self._percentile(all_times, 99)
            else:
                avg_response_time = p95_response_time = p99_response_time = 0.0
            
            # Throughput (queries per second)
            duration_seconds = (end_time - start_time).total_seconds()
            throughput_qps = total_queries / duration_seconds if duration_seconds > 0 else 0.0
            
            # Error rate
            error_rate = failed_queries / total_queries if total_queries > 0 else 0.0
            
            # Top problematic queries
            slowest_queries = sorted(relevant_queries, key=lambda q: q.avg_time, reverse=True)[:10]
            most_frequent_queries = sorted(relevant_queries, key=lambda q: q.execution_count, reverse=True)[:10]
            most_error_prone_queries = sorted(
                [q for q in relevant_queries if q.error_count > 0],
                key=lambda q: q.error_count / q.execution_count,
                reverse=True
            )[:10]
            
            # System metrics summary
            relevant_system_metrics = [
                m for m in self._system_metrics
                if start_time <= m.timestamp <= end_time
            ]
            
            if relevant_system_metrics:
                avg_cpu_usage = statistics.mean(m.cpu_usage for m in relevant_system_metrics)
                avg_memory_usage = statistics.mean(m.memory_usage for m in relevant_system_metrics)
                avg_connection_utilization = statistics.mean(
                    m.connection_utilization for m in relevant_system_metrics
                )
            else:
                avg_cpu_usage = avg_memory_usage = avg_connection_utilization = 0.0
            
            # Performance alerts
            relevant_alerts = [
                a for a in self._alerts
                if start_time <= a.timestamp <= end_time
            ]
            
            # Identify bottlenecks
            bottlenecks = self._identify_bottlenecks(relevant_queries, relevant_system_metrics)
            
            # Generate recommendations
            recommendations = self._generate_recommendations(
                relevant_queries,
                relevant_system_metrics,
                bottlenecks
            )
            
            report = PerformanceReport(
                start_time=start_time,
                end_time=end_time,
                total_queries=total_queries,
                slow_queries=slow_queries,
                failed_queries=failed_queries,
                avg_response_time=avg_response_time,
                p95_response_time=p95_response_time,
                p99_response_time=p99_response_time,
                throughput_qps=throughput_qps,
                error_rate=error_rate,
                slowest_queries=slowest_queries,
                most_frequent_queries=most_frequent_queries,
                most_error_prone_queries=most_error_prone_queries,
                avg_cpu_usage=avg_cpu_usage,
                avg_memory_usage=avg_memory_usage,
                avg_connection_utilization=avg_connection_utilization,
                performance_alerts=relevant_alerts,
                bottlenecks=bottlenecks,
                recommendations=recommendations
            )
            
            logger.info("Performance report generated successfully")
            return report
            
        except Exception as e:
            logger.error(f"Failed to generate performance report: {e}")
            raise
    
    def _create_empty_report(self, start_time: datetime, end_time: datetime) -> PerformanceReport:
        """Create empty report when no data is available"""
        return PerformanceReport(
            start_time=start_time,
            end_time=end_time,
            total_queries=0,
            slow_queries=0,
            failed_queries=0,
            avg_response_time=0.0,
            p95_response_time=0.0,
            p99_response_time=0.0,
            throughput_qps=0.0,
            error_rate=0.0,
            slowest_queries=[],
            most_frequent_queries=[],
            most_error_prone_queries=[],
            avg_cpu_usage=0.0,
            avg_memory_usage=0.0,
            avg_connection_utilization=0.0,
            performance_alerts=[],
            bottlenecks=[],
            recommendations=["No data available for analysis"]
        )
    
    def _percentile(self, data: List[float], percentile: float) -> float:
        """Calculate percentile value"""
        if not data:
            return 0.0
        
        sorted_data = sorted(data)
        index = int(len(sorted_data) * percentile / 100)
        return sorted_data[min(index, len(sorted_data) - 1)]
    
    def _identify_bottlenecks(
        self,
        queries: List[QueryMetrics],
        system_metrics: List[SystemMetrics]
    ) -> List[Dict[str, Any]]:
        """
Identify performance bottlenecks"""
        bottlenecks = []
        
        # Query-based bottlenecks
        slow_query_count = sum(1 for q in queries if q.avg_time > self.slow_query_threshold)
        if slow_query_count > len(queries) * 0.1:  # More than 10% slow queries
            bottlenecks.append({
                "type": BottleneckType.QUERY_OPTIMIZATION.value,
                "severity": "high",
                "description": f"{slow_query_count} slow queries detected",
                "impact": "High response times"
            })
        
        # Inefficient queries
        inefficient_queries = [q for q in queries if q.efficiency_ratio < 0.1]
        if inefficient_queries:
            bottlenecks.append({
                "type": BottleneckType.INDEX_MISSING.value,
                "severity": "medium",
                "description": f"{len(inefficient_queries)} inefficient queries (low row efficiency)",
                "impact": "Excessive row scanning"
            })
        
        # System resource bottlenecks
        if system_metrics:
            avg_cpu = statistics.mean(m.cpu_usage for m in system_metrics)
            avg_memory = statistics.mean(m.memory_usage for m in system_metrics)
            
            if avg_cpu > 80:
                bottlenecks.append({
                    "type": BottleneckType.CPU.value,
                    "severity": "high",
                    "description": f"High CPU usage: {avg_cpu:.1f}%",
                    "impact": "Reduced query processing capacity"
                })
            
            if avg_memory > 80:
                bottlenecks.append({
                    "type": BottleneckType.MEMORY.value,
                    "severity": "high",
                    "description": f"High memory usage: {avg_memory:.1f}%",
                    "impact": "Potential swapping and performance degradation"
                })
        
        return bottlenecks
    
    def _generate_recommendations(
        self,
        queries: List[QueryMetrics],
        system_metrics: List[SystemMetrics],
        bottlenecks: List[Dict[str, Any]]
    ) -> List[str]:
        """Generate performance optimization recommendations"""
        recommendations = []
        
        # Query optimization recommendations
        slow_queries = [q for q in queries if q.avg_time > self.slow_query_threshold]
        if slow_queries:
            recommendations.append(
                f"Optimize {len(slow_queries)} slow queries (avg time > {self.slow_query_threshold}s)"
            )
        
        # Index recommendations
        inefficient_queries = [q for q in queries if q.efficiency_ratio < 0.1]
        if inefficient_queries:
            recommendations.append(
                f"Consider adding indexes for {len(inefficient_queries)} inefficient queries"
            )
        
        # Error handling recommendations
        error_queries = [q for q in queries if q.error_count > 0]
        if error_queries:
            recommendations.append(
                f"Investigate and fix {len(error_queries)} queries with errors"
            )
        
        # System resource recommendations
        if system_metrics:
            avg_cpu = statistics.mean(m.cpu_usage for m in system_metrics)
            avg_memory = statistics.mean(m.memory_usage for m in system_metrics)
            
            if avg_cpu > 80:
                recommendations.append("Consider CPU scaling or query optimization for high CPU usage")
            
            if avg_memory > 80:
                recommendations.append("Consider memory scaling or memory-efficient query patterns")
        
        # Connection pool recommendations
        high_utilization_metrics = [
            m for m in system_metrics
            if m.connection_utilization > 0.8
        ]
        if high_utilization_metrics:
            recommendations.append("Consider increasing connection pool size for high utilization")
        
        # Caching recommendations
        frequent_queries = [q for q in queries if q.execution_count > 100]
        if frequent_queries:
            recommendations.append(
                f"Consider caching results for {len(frequent_queries)} frequently executed queries"
            )
        
        if not recommendations:
            recommendations.append("Performance looks good - no immediate optimizations needed")
        
        return recommendations
    
    async def get_real_time_stats(self) -> Dict[str, Any]:
        """Get real-time performance statistics"""
        current_time = datetime.now()
        last_hour = current_time - timedelta(hours=1)
        
        # Recent queries
        recent_queries = [
            q for q in self._query_metrics.values()
            if q.last_seen > last_hour
        ]
        
        # Recent system metrics
        recent_system_metrics = [
            m for m in self._system_metrics
            if m.timestamp > last_hour
        ]
        
        # Calculate stats
        total_queries = sum(q.execution_count for q in recent_queries) if recent_queries else 0
        avg_response_time = statistics.mean(
            [q.avg_time for q in recent_queries]
        ) if recent_queries else 0.0
        
        current_cpu = recent_system_metrics[-1].cpu_usage if recent_system_metrics else 0.0
        current_memory = recent_system_metrics[-1].memory_usage if recent_system_metrics else 0.0
        
        return {
            "timestamp": current_time.isoformat(),
            "queries_last_hour": total_queries,
            "avg_response_time": avg_response_time,
            "current_cpu_usage": current_cpu,
            "current_memory_usage": current_memory,
            "active_alerts": len([a for a in self._alerts if not a.resolved]),
            "tracked_queries": len(self._query_metrics),
            "system_metrics_points": len(self._system_metrics),
        }
    
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
    def clear_metrics(self, older_than_hours: int = 24) -> None:
        """Clear old metrics to prevent memory bloat"""
        cutoff_time = datetime.now() - timedelta(hours=older_than_hours)
        
        # Remove old query metrics
        old_queries = [
            query_id for query_id, metrics in self._query_metrics.items()
            if metrics.last_seen < cutoff_time
        ]
        
        for query_id in old_queries:
            del self._query_metrics[query_id]
        
        # Remove old alerts
        self._alerts = [a for a in self._alerts if a.timestamp > cutoff_time]
        
        logger.info(f"Cleared {len(old_queries)} old query metrics and old alerts")


# Global performance analyzer instance
_performance_analyzer: Optional[PerformanceAnalyzer] = None


def get_performance_analyzer(config: Optional[Dict[str, Any]] = None) -> PerformanceAnalyzer:
    """Get global performance analyzer instance"""
    global _performance_analyzer
    
    if _performance_analyzer is None:
        _performance_analyzer = PerformanceAnalyzer(config)
    
    return _performance_analyzer


async def start_performance_monitoring(engine: AsyncEngine, config: Optional[Dict[str, Any]] = None) -> None:
    """
Start global performance monitoring"""
    analyzer = get_performance_analyzer(config)
    await analyzer.start_monitoring(engine)


async def stop_performance_monitoring() -> None:
    """
Stop global performance monitoring"""
    global _performance_analyzer
    
    if _performance_analyzer:
        await _performance_analyzer.stop_monitoring()
        _performance_analyzer = None
