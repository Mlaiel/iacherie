"""Enterprise Database Performance Monitor
Advanced database performance monitoring, optimization and alerting system

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: All rights reserved - Unauthorized use prohibited

AVERTISSEMENT LEGAL:
Ce code est la propriété intellectuelle exclusive de Fahed Mlaiel.
Toute utilisation, copie, modification ou distribution sans autorisation
écrite explicite est strictement interdite et passible de poursuites judiciaires.
Contact: mlaiel@live.de

ÉQUIPE PROJET SPÉCIALISÉE:
- Lead Developer IA: Fahed Mlaiel
- Backend Senior Engineer: Fahed Mlaiel  
- ML Engineer: Fahed Mlaiel
- Database Administrator: Fahed Mlaiel
- Sécurité Expert: Fahed Mlaiel
- Microservices Architect: Fahed Mlaiel
- Audio Processing Engineer: Fahed Mlaiel
- DevOps Engineer: Fahed Mlaiel
- IA Prompt Engineer: Fahed Mlaiel

⚠️ ATTENTION IMPORTANTE ⚠️
Toute tentative de vol, copie, ou utilisation non autorisée de ce code, 
concept ou idée sans autorisation écrite explicite de Fahed Mlaiel 
sera poursuivie selon la loi allemande et internationale.

Contact autorisé: mlaiel@live.de
"""
import asyncio
import threading
import time
import statistics
from typing import Dict, List, Optional, Any, Tuple, NamedTuple
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
from collections import deque, defaultdict
import psutil
import numpy as np
from concurrent.futures import ThreadPoolExecutor
import json

from backend.core.config import get_database_settings, get_monitoring_settings
from backend.core.logging import get_logger
from backend.core.monitoring import MetricsCollector
from backend.deployment.database.postgresql_manager import get_postgresql_manager


class PerformanceMetricType(Enum):
    """Types of performance metrics"""    CONNECTION = "connection"
    QUERY = "query"
    MEMORY = "memory"
    DISK = "disk"
    CPU = "cpu"
    LOCK = "lock"
    INDEX = "index"
    CACHE = "cache"
    REPLICATION = "replication"
    TRANSACTION = "transaction"


class AlertSeverity(Enum):
    """Alert severity levels"""    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class PerformanceStatus(Enum):
    """Overall performance status"""    EXCELLENT = "excellent"
    GOOD = "good"
    WARNING = "warning"
    CRITICAL = "critical"
    DEGRADED = "degraded"


@dataclass
class PerformanceMetric:
    """Individual performance metric"""    metric_type: PerformanceMetricType
    name: str
    value: float
    unit: str
    timestamp: datetime
    threshold_warning: Optional[float] = None
    threshold_critical: Optional[float] = None
    tags: Dict[str, str] = field(default_factory=dict)


@dataclass
class PerformanceAlert:
    """Performance alert"""    alert_id: str
    metric_name: str
    severity: AlertSeverity
    message: str
    current_value: float
    threshold_value: float
    timestamp: datetime
    resolved: bool = False
    resolved_at: Optional[datetime] = None


@dataclass
class QueryPerformance:
    """Query performance statistics"""    query_hash: str
    query_text: str
    calls: int
    total_exec_time: float
    mean_exec_time: float
    min_exec_time: float
    max_exec_time: float
    stddev_exec_time: float
    rows_returned: int
    shared_blks_hit: int
    shared_blks_read: int
    shared_blks_dirtied: int
    hit_ratio: float
    last_executed: datetime


class LockInfo(NamedTuple):
    """Database lock information"""    locktype: str
    database: str
    relation: str
    page: Optional[int]
    tuple: Optional[int]
    virtualxid: Optional[str]
    transactionid: Optional[str]
    mode: str
    granted: bool
    pid: int
    wait_start: Optional[datetime]


class DatabasePerformanceMonitor:
    """    Enterprise database performance monitoring system with features:
    - Real-time performance metrics collection
    - Query performance analysis and optimization suggestions
    - Resource utilization monitoring (CPU, memory, disk, I/O)
    - Lock detection and deadlock analysis
    - Cache hit ratio optimization
    - Index usage analytics
    - Automated alert generation and escalation
    - Historical trend analysis and capacity planning
    - Performance baseline establishment
    - Automated performance tuning recommendations
    """    
    def __init__(self):
        self.logger = get_logger(__name__)
        self.db_config = get_database_settings()
        self.monitoring_config = get_monitoring_settings()
        self.db_manager = get_postgresql_manager()
        self.metrics_collector = MetricsCollector()
        
        # Monitoring state
        self.is_monitoring = False
        self.monitor_thread: Optional[threading.Thread] = None
        self.collection_interval = self.monitoring_config.COLLECTION_INTERVAL or 30
        
        # Metrics storage
        self.metrics_history: Dict[str, deque] = defaultdict(lambda: deque(maxlen=1000))
        self.query_performance_cache: Dict[str, QueryPerformance] = {}
        self.active_alerts: Dict[str, PerformanceAlert] = {}
        
        # Performance thresholds
        self.thresholds = self._initialize_thresholds()
        
        # Performance baselines
        self.baselines: Dict[str, float] = {}
        
        # Query optimization recommendations
        self.optimization_suggestions: List[Dict[str, Any]] = []
        
        self._initialize_monitoring()
    
    def _initialize_thresholds(self) -> Dict[str, Dict[str, float]]:
        """Initialize performance monitoring thresholds"""        return {
            'cpu_usage': {'warning': 70.0, 'critical': 90.0},
            'memory_usage': {'warning': 80.0, 'critical': 95.0},
            'disk_usage': {'warning': 80.0, 'critical': 95.0},
            'connection_usage': {'warning': 80.0, 'critical': 95.0},
            'cache_hit_ratio': {'warning': 95.0, 'critical': 90.0},  # Lower is worse
            'query_duration': {'warning': 1.0, 'critical': 5.0},  # seconds
            'lock_wait_time': {'warning': 10.0, 'critical': 30.0},  # seconds
            'replication_lag': {'warning': 1024*1024, 'critical': 10*1024*1024},  # bytes
            'transactions_per_second': {'warning': 1000, 'critical': 2000},
            'deadlocks_per_minute': {'warning': 1, 'critical': 5}
        }
    
    def _initialize_monitoring(self) -> None:
        """Initialize monitoring components"""        try:
            # Enable pg_stat_statements extension
            self._enable_pg_stat_statements()
            
            # Initialize baseline metrics
            self._establish_performance_baselines()
            
            self.logger.info("Performance monitoring initialized")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize monitoring: {e}")
    
    def _enable_pg_stat_statements(self) -> None:
        """Enable pg_stat_statements extension for query tracking"""        try:
            # Check if extension exists
            check_query = """                SELECT EXISTS(
                    SELECT 1 FROM pg_extension WHERE extname = 'pg_stat_statements'
                )
            """            
            result = self.db_manager.execute_query(check_query)
            extension_exists = result[0][0] if result else False
            
            if not extension_exists:
                try:
                    create_query = "CREATE EXTENSION IF NOT EXISTS pg_stat_statements"
                    self.db_manager.execute_query(create_query, fetch_results=False)
                    self.logger.info("Enabled pg_stat_statements extension")
                except Exception as e:
                    self.logger.warning(f"Could not enable pg_stat_statements: {e}")
            
        except Exception as e:
            self.logger.error(f"Failed to check pg_stat_statements: {e}")
    
    def _establish_performance_baselines(self) -> None:
        """Establish performance baselines for comparison"""        try:
            baseline_metrics = [
                'cpu_usage', 'memory_usage', 'cache_hit_ratio',
                'connections_active', 'transactions_per_second'
            ]
            
            for metric_name in baseline_metrics:
                current_value = self._collect_single_metric(metric_name)
                if current_value is not None:
                    self.baselines[metric_name] = current_value
            
            self.logger.info(f"Established baselines for {len(self.baselines)} metrics")
            
        except Exception as e:
            self.logger.error(f"Failed to establish baselines: {e}")
    
    def start_monitoring(self) -> None:
        """Start continuous performance monitoring"""        try:
            if self.is_monitoring:
                self.logger.warning("Performance monitoring already active")
                return
            
            self.is_monitoring = True
            
            self.monitor_thread = threading.Thread(
                target=self._monitoring_loop,
                daemon=True
            )
            self.monitor_thread.start()
            
            self.logger.info(f"Started performance monitoring (interval: {self.collection_interval}s)")
            
        except Exception as e:
            self.logger.error(f"Failed to start monitoring: {e}")
    
    def stop_monitoring(self) -> None:
        """Stop performance monitoring"""        try:
            self.is_monitoring = False
            
            if self.monitor_thread:
                self.monitor_thread.join(timeout=30)
            
            self.logger.info("Stopped performance monitoring")
            
        except Exception as e:
            self.logger.error(f"Failed to stop monitoring: {e}")
    
    def _monitoring_loop(self) -> None:
        """Main monitoring loop"""        while self.is_monitoring:
            try:
                start_time = time.time()
                
                # Collect all performance metrics
                self._collect_all_metrics()
                
                # Analyze query performance
                self._analyze_query_performance()
                
                # Check for performance issues
                self._check_performance_alerts()
                
                # Update optimization suggestions
                self._update_optimization_suggestions()
                
                # Calculate sleep time to maintain interval
                elapsed_time = time.time() - start_time
                sleep_time = max(0, self.collection_interval - elapsed_time)
                
                if sleep_time > 0:
                    time.sleep(sleep_time)
                
            except Exception as e:
                self.logger.error(f"Monitoring loop error: {e}")
                time.sleep(5)  # Short delay on error
    
    def _collect_all_metrics(self) -> None:
        """Collect all performance metrics"""        try:
            current_time = datetime.now()
            
            # System metrics
            self._collect_system_metrics(current_time)
            
            # Database connection metrics
            self._collect_connection_metrics(current_time)
            
            # Database activity metrics
            self._collect_activity_metrics(current_time)
            
            # Cache and buffer metrics
            self._collect_cache_metrics(current_time)
            
            # Lock and transaction metrics
            self._collect_lock_metrics(current_time)
            
            # Index usage metrics
            self._collect_index_metrics(current_time)
            
            # Replication metrics (if applicable)
            self._collect_replication_metrics(current_time)
            
        except Exception as e:
            self.logger.error(f"Failed to collect metrics: {e}")
    
    def _collect_system_metrics(self, timestamp: datetime) -> None:
        """Collect system-level metrics"""        try:
            # CPU usage
            cpu_usage = psutil.cpu_percent(interval=1)
            self._record_metric("cpu_usage", cpu_usage, "%", timestamp)
            
            # Memory usage
            memory = psutil.virtual_memory()
            memory_usage = memory.percent
            self._record_metric("memory_usage", memory_usage, "%", timestamp)
            self._record_metric("memory_available", memory.available / (1024**3), "GB", timestamp)
            
            # Disk usage
            disk_usage = psutil.disk_usage('/').percent
            self._record_metric("disk_usage", disk_usage, "%", timestamp)
            
            # Network I/O
            net_io = psutil.net_io_counters()
            self._record_metric("network_bytes_sent", net_io.bytes_sent, "bytes", timestamp)
            self._record_metric("network_bytes_recv", net_io.bytes_recv, "bytes", timestamp)
            
        except Exception as e:
            self.logger.error(f"Failed to collect system metrics: {e}")
    
    def _collect_connection_metrics(self, timestamp: datetime) -> None:
        """Collect database connection metrics"""        try:
            # Active connections
            connections_query = """                SELECT 
                    count(*) as total_connections,
                    count(*) FILTER (WHERE state = 'active') as active_connections,
                    count(*) FILTER (WHERE state = 'idle') as idle_connections,
                    count(*) FILTER (WHERE state = 'idle in transaction') as idle_in_transaction
                FROM pg_stat_activity
                WHERE pid <> pg_backend_pid()
            """            
            result = self.db_manager.execute_query(connections_query)
            
            if result:
                total, active, idle, idle_in_tx = result[0]
                self._record_metric("connections_total", total, "count", timestamp)
                self._record_metric("connections_active", active, "count", timestamp)
                self._record_metric("connections_idle", idle, "count", timestamp)
                self._record_metric("connections_idle_in_transaction", idle_in_tx, "count", timestamp)
                
                # Calculate connection usage percentage
                max_connections_query = "SHOW max_connections"
                max_result = self.db_manager.execute_query(max_connections_query)
                if max_result:
                    max_connections = int(max_result[0][0])
                    connection_usage = (total / max_connections) * 100
                    self._record_metric("connection_usage", connection_usage, "%", timestamp)
            
        except Exception as e:
            self.logger.error(f"Failed to collect connection metrics: {e}")
    
    def _collect_activity_metrics(self, timestamp: datetime) -> None:
        """Collect database activity metrics"""        try:
            # Transaction statistics
            activity_query = """                SELECT 
                    sum(xact_commit) as total_commits,
                    sum(xact_rollback) as total_rollbacks,
                    sum(blks_read) as blocks_read,
                    sum(blks_hit) as blocks_hit,
                    sum(tup_returned) as tuples_returned,
                    sum(tup_fetched) as tuples_fetched,
                    sum(tup_inserted) as tuples_inserted,
                    sum(tup_updated) as tuples_updated,
                    sum(tup_deleted) as tuples_deleted
                FROM pg_stat_database
                WHERE datname = current_database()
            """            
            result = self.db_manager.execute_query(activity_query)
            
            if result:
                commits, rollbacks, blks_read, blks_hit, tup_ret, tup_fetch, tup_ins, tup_upd, tup_del = result[0]
                
                # Calculate rates (if we have previous values)
                self._record_metric("transactions_committed", commits or 0, "count", timestamp)
                self._record_metric("transactions_rollback", rollbacks or 0, "count", timestamp)
                self._record_metric("blocks_read", blks_read or 0, "count", timestamp)
                self._record_metric("blocks_hit", blks_hit or 0, "count", timestamp)
                self._record_metric("tuples_returned", tup_ret or 0, "count", timestamp)
                self._record_metric("tuples_fetched", tup_fetch or 0, "count", timestamp)
                self._record_metric("tuples_inserted", tup_ins or 0, "count", timestamp)
                self._record_metric("tuples_updated", tup_upd or 0, "count", timestamp)
                self._record_metric("tuples_deleted", tup_del or 0, "count", timestamp)
            
            # Deadlock statistics
            deadlock_query = """                SELECT deadlocks 
                FROM pg_stat_database 
                WHERE datname = current_database()
            """            
            deadlock_result = self.db_manager.execute_query(deadlock_query)
            if deadlock_result:
                deadlocks = deadlock_result[0][0] or 0
                self._record_metric("deadlocks_total", deadlocks, "count", timestamp)
            
        except Exception as e:
            self.logger.error(f"Failed to collect activity metrics: {e}")
    
    def _collect_cache_metrics(self, timestamp: datetime) -> None:
        """Collect cache and buffer metrics"""        try:
            # Buffer hit ratio
            cache_query = """                SELECT 
                    sum(blks_hit) as total_hit,
                    sum(blks_read) as total_read,
                    CASE 
                        WHEN sum(blks_hit) + sum(blks_read) = 0 THEN 0
                        ELSE round(sum(blks_hit) * 100.0 / (sum(blks_hit) + sum(blks_read)), 2)
                    END as hit_ratio
                FROM pg_stat_database
            """            
            result = self.db_manager.execute_query(cache_query)
            
            if result:
                total_hit, total_read, hit_ratio = result[0]
                self._record_metric("cache_blocks_hit", total_hit or 0, "count", timestamp)
                self._record_metric("cache_blocks_read", total_read or 0, "count", timestamp)
                self._record_metric("cache_hit_ratio", hit_ratio or 0, "%", timestamp)
            
            # Shared buffer statistics
            buffer_query = """                SELECT 
                    setting::int * 8192 / 1024 / 1024 as shared_buffers_mb
                FROM pg_settings 
                WHERE name = 'shared_buffers'
            """            
            buffer_result = self.db_manager.execute_query(buffer_query)
            if buffer_result:
                shared_buffers_mb = buffer_result[0][0]
                self._record_metric("shared_buffers", shared_buffers_mb, "MB", timestamp)
            
        except Exception as e:
            self.logger.error(f"Failed to collect cache metrics: {e}")
    
    def _collect_lock_metrics(self, timestamp: datetime) -> None:
        """Collect lock and blocking metrics"""        try:
            # Current locks
            locks_query = """                SELECT 
                    mode,
                    count(*) as lock_count
                FROM pg_locks 
                WHERE granted = true
                GROUP BY mode
            """            
            result = self.db_manager.execute_query(locks_query)
            
            total_locks = 0
            if result:
                for mode, count in result:
                    total_locks += count
                    self._record_metric(f"locks_{mode.lower()}", count, "count", timestamp)
            
            self._record_metric("locks_total", total_locks, "count", timestamp)
            
            # Waiting locks
            waiting_query = """                SELECT count(*) as waiting_locks
                FROM pg_locks 
                WHERE granted = false
            """            
            waiting_result = self.db_manager.execute_query(waiting_query)
            if waiting_result:
                waiting_locks = waiting_result[0][0]
                self._record_metric("locks_waiting", waiting_locks, "count", timestamp)
            
            # Lock wait time
            lock_wait_query = """                SELECT 
                    EXTRACT(EPOCH FROM (now() - query_start)) as wait_seconds
                FROM pg_stat_activity 
                WHERE wait_event_type = 'Lock' AND state = 'active'
                ORDER BY wait_seconds DESC
                LIMIT 1
            """            
            wait_result = self.db_manager.execute_query(lock_wait_query)
            if wait_result and wait_result[0][0]:
                max_wait_time = wait_result[0][0]
                self._record_metric("lock_max_wait_time", max_wait_time, "seconds", timestamp)
            
        except Exception as e:
            self.logger.error(f"Failed to collect lock metrics: {e}")
    
    def _collect_index_metrics(self, timestamp: datetime) -> None:
        """Collect index usage metrics"""        try:
            # Index usage statistics
            index_query = """                SELECT 
                    schemaname,
                    tablename,
                    indexname,
                    idx_scan,
                    idx_tup_read,
                    idx_tup_fetch
                FROM pg_stat_user_indexes
                ORDER BY idx_scan DESC
                LIMIT 10
            """            
            result = self.db_manager.execute_query(index_query)
            
            if result:
                total_scans = sum(row[3] for row in result if row[3])
                self._record_metric("index_scans_total", total_scans, "count", timestamp)
            
            # Unused indexes
            unused_indexes_query = """                SELECT count(*)
                FROM pg_stat_user_indexes 
                WHERE idx_scan = 0
            """            
            unused_result = self.db_manager.execute_query(unused_indexes_query)
            if unused_result:
                unused_count = unused_result[0][0]
                self._record_metric("indexes_unused", unused_count, "count", timestamp)
            
        except Exception as e:
            self.logger.error(f"Failed to collect index metrics: {e}")
    
    def _collect_replication_metrics(self, timestamp: datetime) -> None:
        """Collect replication metrics if applicable"""        try:
            # Check if replication is active
            replication_query = """                SELECT 
                    client_addr,
                    state,
                    pg_wal_lsn_diff(pg_current_wal_lsn(), sent_lsn) as lag_bytes,
                    EXTRACT(EPOCH FROM (now() - reply_time)) as reply_lag_seconds
                FROM pg_stat_replication
            """            
            result = self.db_manager.execute_query(replication_query)
            
            if result:
                total_replicas = len(result)
                max_lag_bytes = max(row[2] for row in result if row[2] is not None)
                max_reply_lag = max(row[3] for row in result if row[3] is not None)
                
                self._record_metric("replication_replicas", total_replicas, "count", timestamp)
                self._record_metric("replication_max_lag_bytes", max_lag_bytes or 0, "bytes", timestamp)
                self._record_metric("replication_max_reply_lag", max_reply_lag or 0, "seconds", timestamp)
            
        except Exception as e:
            self.logger.error(f"Failed to collect replication metrics: {e}")
    
    def _analyze_query_performance(self) -> None:
        """Analyze query performance using pg_stat_statements"""        try:
            # Get query statistics
            query_stats_query = """                SELECT 
                    queryid,
                    query,
                    calls,
                    total_exec_time,
                    mean_exec_time,
                    min_exec_time,
                    max_exec_time,
                    stddev_exec_time,
                    rows,
                    shared_blks_hit,
                    shared_blks_read,
                    shared_blks_dirtied,
                    CASE 
                        WHEN shared_blks_hit + shared_blks_read = 0 THEN 0
                        ELSE round(shared_blks_hit * 100.0 / (shared_blks_hit + shared_blks_read), 2)
                    END as hit_ratio
                FROM pg_stat_statements
                WHERE calls > 10  -- Only include frequently executed queries
                ORDER BY total_exec_time DESC
                LIMIT 50
            """            
            result = self.db_manager.execute_query(query_stats_query)
            
            if result:
                for row in result:
                    queryid, query_text, calls, total_time, mean_time, min_time, max_time, stddev_time, rows, hit, read, dirty, hit_ratio = row
                    
                    query_hash = str(queryid)
                    
                    query_perf = QueryPerformance(
                        query_hash=query_hash,
                        query_text=query_text[:500],  # Truncate long queries
                        calls=calls,
                        total_exec_time=total_time,
                        mean_exec_time=mean_time,
                        min_exec_time=min_time,
                        max_exec_time=max_time,
                        stddev_exec_time=stddev_time or 0,
                        rows_returned=rows,
                        shared_blks_hit=hit,
                        shared_blks_read=read,
                        shared_blks_dirtied=dirty,
                        hit_ratio=hit_ratio or 0,
                        last_executed=datetime.now()
                    )
                    
                    self.query_performance_cache[query_hash] = query_perf
            
        except Exception as e:
            self.logger.error(f"Failed to analyze query performance: {e}")
    
    def _record_metric(self, name: str, value: float, unit: str, timestamp: datetime) -> None:
        """Record a performance metric"""        try:
            metric = PerformanceMetric(
                metric_type=self._get_metric_type(name),
                name=name,
                value=value,
                unit=unit,
                timestamp=timestamp,
                threshold_warning=self.thresholds.get(name, {}).get('warning'),
                threshold_critical=self.thresholds.get(name, {}).get('critical')
            )
            
            # Store in history
            self.metrics_history[name].append(metric)
            
            # Send to metrics collector
            self.metrics_collector.record_gauge(f"db.{name}", value)
            
        except Exception as e:
            self.logger.error(f"Failed to record metric {name}: {e}")
    
    def _get_metric_type(self, metric_name: str) -> PerformanceMetricType:
        """Determine metric type from name"""        if metric_name.startswith('connection'):
            return PerformanceMetricType.CONNECTION
        elif metric_name.startswith('cache') or metric_name.startswith('buffer'):
            return PerformanceMetricType.CACHE
        elif metric_name.startswith('lock'):
            return PerformanceMetricType.LOCK
        elif metric_name.startswith('index'):
            return PerformanceMetricType.INDEX
        elif metric_name.startswith('cpu'):
            return PerformanceMetricType.CPU
        elif metric_name.startswith('memory'):
            return PerformanceMetricType.MEMORY
        elif metric_name.startswith('disk'):
            return PerformanceMetricType.DISK
        elif metric_name.startswith('replication'):
            return PerformanceMetricType.REPLICATION
        elif metric_name.startswith('transaction'):
            return PerformanceMetricType.TRANSACTION
        else:
            return PerformanceMetricType.QUERY
    
    def _check_performance_alerts(self) -> None:
        """Check for performance alerts"""        try:
            current_time = datetime.now()
            
            for metric_name, history in self.metrics_history.items():
                if not history:
                    continue
                
                latest_metric = history[-1]
                thresholds = self.thresholds.get(metric_name, {})
                
                if not thresholds:
                    continue
                
                warning_threshold = thresholds.get('warning')
                critical_threshold = thresholds.get('critical')
                
                # Check critical threshold
                if critical_threshold is not None:
                    if self._check_threshold_breach(latest_metric.value, critical_threshold, metric_name):
                        self._create_alert(
                            metric_name,
                            AlertSeverity.CRITICAL,
                            latest_metric.value,
                            critical_threshold,
                            current_time
                        )
                
                # Check warning threshold
                elif warning_threshold is not None:
                    if self._check_threshold_breach(latest_metric.value, warning_threshold, metric_name):
                        self._create_alert(
                            metric_name,
                            AlertSeverity.HIGH,
                            latest_metric.value,
                            warning_threshold,
                            current_time
                        )
                
                # Check if alert should be resolved
                self._check_alert_resolution(metric_name, latest_metric.value)
            
        except Exception as e:
            self.logger.error(f"Failed to check performance alerts: {e}")
    
    def _check_threshold_breach(self, value: float, threshold: float, metric_name: str) -> bool:
        """Check if metric value breaches threshold"""        # For metrics where lower is better (like cache hit ratio)
        if metric_name in ['cache_hit_ratio']:
            return value < threshold
        else:
            return value > threshold
    
    def _create_alert(
        self, 
        metric_name: str, 
        severity: AlertSeverity, 
        current_value: float, 
        threshold_value: float,
        timestamp: datetime
    ) -> None:
        """Create performance alert"""        try:
            alert_id = f"{metric_name}_{timestamp.strftime('%Y%m%d_%H%M%S')}"
            
            # Check if similar alert already exists
            existing_alert = None
            for alert in self.active_alerts.values():
                if alert.metric_name == metric_name and not alert.resolved:
                    existing_alert = alert
                    break
            
            if existing_alert:
                # Update existing alert if severity increased
                if severity.value > existing_alert.severity.value:
                    existing_alert.severity = severity
                    existing_alert.current_value = current_value
                    existing_alert.timestamp = timestamp
                return
            
            # Create new alert
            message = self._generate_alert_message(metric_name, current_value, threshold_value)
            
            alert = PerformanceAlert(
                alert_id=alert_id,
                metric_name=metric_name,
                severity=severity,
                message=message,
                current_value=current_value,
                threshold_value=threshold_value,
                timestamp=timestamp
            )
            
            self.active_alerts[alert_id] = alert
            
            # Log alert
            self.logger.warning(f"Performance alert: {message}")
            
            # Send to metrics collector
            self.metrics_collector.record_alert(alert_id, {
                'metric': metric_name,
                'severity': severity.value,
                'value': current_value,
                'threshold': threshold_value
            })
            
        except Exception as e:
            self.logger.error(f"Failed to create alert: {e}")
    
    def _generate_alert_message(self, metric_name: str, current_value: float, threshold_value: float) -> str:
        """Generate alert message"""        if metric_name == 'cache_hit_ratio':
            return f"Cache hit ratio below threshold: {current_value:.1f}% < {threshold_value:.1f}%"
        elif 'usage' in metric_name:
            return f"{metric_name.replace('_', ' ').title()} high: {current_value:.1f}% > {threshold_value:.1f}%"
        elif 'lag' in metric_name:
            return f"Replication lag high: {current_value:.0f} bytes > {threshold_value:.0f} bytes"
        elif 'wait' in metric_name:
            return f"Lock wait time high: {current_value:.1f}s > {threshold_value:.1f}s"
        else:
            return f"{metric_name.replace('_', ' ').title()}: {current_value:.2f} > {threshold_value:.2f}"
    
    def _check_alert_resolution(self, metric_name: str, current_value: float) -> None:
        """Check if alerts should be resolved"""        try:
            alerts_to_resolve = []
            
            for alert_id, alert in self.active_alerts.items():
                if alert.metric_name == metric_name and not alert.resolved:
                    # Check if value is back within threshold
                    if self._is_value_within_threshold(current_value, alert.threshold_value, metric_name):
                        alert.resolved = True
                        alert.resolved_at = datetime.now()
                        alerts_to_resolve.append(alert_id)
            
            # Log resolved alerts
            for alert_id in alerts_to_resolve:
                alert = self.active_alerts[alert_id]
                self.logger.info(f"Performance alert resolved: {alert.message}")
            
        except Exception as e:
            self.logger.error(f"Failed to check alert resolution: {e}")
    
    def _is_value_within_threshold(self, value: float, threshold: float, metric_name: str) -> bool:
        """Check if value is within acceptable threshold"""        # Add some hysteresis to prevent flapping
        hysteresis_factor = 0.95
        
        if metric_name in ['cache_hit_ratio']:
            return value > threshold * hysteresis_factor
        else:
            return value < threshold * hysteresis_factor
    
    def _collect_single_metric(self, metric_name: str) -> Optional[float]:
        """Collect a single metric value"""        try:
            if metric_name == 'cpu_usage':
                return psutil.cpu_percent(interval=1)
            elif metric_name == 'memory_usage':
                return psutil.virtual_memory().percent
            elif metric_name == 'cache_hit_ratio':
                query = """                    SELECT CASE 
                        WHEN sum(blks_hit) + sum(blks_read) = 0 THEN 0
                        ELSE round(sum(blks_hit) * 100.0 / (sum(blks_hit) + sum(blks_read)), 2)
                    END as hit_ratio
                    FROM pg_stat_database
                """                result = self.db_manager.execute_query(query)
                return result[0][0] if result else None
            elif metric_name == 'connections_active':
                query = "SELECT count(*) FROM pg_stat_activity WHERE state = 'active'"
                result = self.db_manager.execute_query(query)
                return result[0][0] if result else None
            elif metric_name == 'transactions_per_second':
                # This would require calculating rate from previous measurement
                return None
            
            return None
            
        except Exception as e:
            self.logger.error(f"Failed to collect metric {metric_name}: {e}")
            return None
    
    def _update_optimization_suggestions(self) -> None:
        """Update query optimization suggestions"""        try:
            suggestions = []
            
            # Analyze slow queries
            for query_hash, query_perf in self.query_performance_cache.items():
                if query_perf.mean_exec_time > 1.0:  # Queries taking more than 1 second
                    suggestion = {
                        'type': 'slow_query',
                        'query_hash': query_hash,
                        'query_text': query_perf.query_text[:200],
                        'mean_exec_time': query_perf.mean_exec_time,
                        'calls': query_perf.calls,
                        'recommendation': self._generate_optimization_recommendation(query_perf)
                    }
                    suggestions.append(suggestion)
            
            # Check for unused indexes
            if 'indexes_unused' in self.metrics_history:
                unused_count = self.metrics_history['indexes_unused'][-1].value
                if unused_count > 0:
                    suggestions.append({
                        'type': 'unused_indexes',
                        'count': unused_count,
                        'recommendation': 'Consider dropping unused indexes to improve write performance'
                    })
            
            # Check cache hit ratio
            if 'cache_hit_ratio' in self.metrics_history:
                hit_ratio = self.metrics_history['cache_hit_ratio'][-1].value
                if hit_ratio < 95:
                    suggestions.append({
                        'type': 'low_cache_hit_ratio',
                        'hit_ratio': hit_ratio,
                        'recommendation': 'Consider increasing shared_buffers parameter'
                    })
            
            self.optimization_suggestions = suggestions[:10]  # Keep top 10 suggestions
            
        except Exception as e:
            self.logger.error(f"Failed to update optimization suggestions: {e}")
    
    def _generate_optimization_recommendation(self, query_perf: QueryPerformance) -> str:
        """Generate optimization recommendation for a query"""        recommendations = []
        
        if query_perf.hit_ratio < 90:
            recommendations.append("Consider adding indexes to improve cache hit ratio")
        
        if query_perf.stddev_exec_time > query_perf.mean_exec_time:
            recommendations.append("Query execution time is inconsistent, check for parameter sniffing")
        
        if query_perf.calls > 1000 and query_perf.mean_exec_time > 0.1:
            recommendations.append("High-frequency query with significant execution time, consider optimization")
        
        if not recommendations:
            recommendations.append("Review query plan and consider adding appropriate indexes")
        
        return "; ".join(recommendations)
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """Get comprehensive performance summary"""        try:
            current_time = datetime.now()
            
            summary = {
                'timestamp': current_time.isoformat(),
                'overall_status': self._calculate_overall_status(),
                'active_alerts': len([a for a in self.active_alerts.values() if not a.resolved]),
                'critical_alerts': len([a for a in self.active_alerts.values() 
                                      if not a.resolved and a.severity == AlertSeverity.CRITICAL]),
                'metrics': {},
                'top_slow_queries': [],
                'optimization_suggestions': self.optimization_suggestions[:5],
                'trends': {}
            }
            
            # Add latest metrics
            for metric_name, history in self.metrics_history.items():
                if history:
                    latest = history[-1]
                    summary['metrics'][metric_name] = {
                        'value': latest.value,
                        'unit': latest.unit,
                        'timestamp': latest.timestamp.isoformat()
                    }
            
            # Add top slow queries
            sorted_queries = sorted(
                self.query_performance_cache.values(),
                key=lambda q: q.total_exec_time,
                reverse=True
            )
            
            for query in sorted_queries[:5]:
                summary['top_slow_queries'].append({
                    'query_text': query.query_text[:200],
                    'mean_exec_time': query.mean_exec_time,
                    'total_exec_time': query.total_exec_time,
                    'calls': query.calls,
                    'hit_ratio': query.hit_ratio
                })
            
            # Add trends
            summary['trends'] = self._calculate_trends()
            
            return summary
            
        except Exception as e:
            self.logger.error(f"Failed to get performance summary: {e}")
            return {'error': str(e)}
    
    def _calculate_overall_status(self) -> str:
        """Calculate overall performance status"""        try:
            critical_alerts = [a for a in self.active_alerts.values() 
                             if not a.resolved and a.severity == AlertSeverity.CRITICAL]
            
            if critical_alerts:
                return PerformanceStatus.CRITICAL.value
            
            high_alerts = [a for a in self.active_alerts.values() 
                          if not a.resolved and a.severity == AlertSeverity.HIGH]
            
            if high_alerts:
                return PerformanceStatus.WARNING.value
            
            medium_alerts = [a for a in self.active_alerts.values() 
                           if not a.resolved and a.severity == AlertSeverity.MEDIUM]
            
            if medium_alerts:
                return PerformanceStatus.GOOD.value
            
            return PerformanceStatus.EXCELLENT.value
            
        except Exception as e:
            self.logger.error(f"Failed to calculate overall status: {e}")
            return PerformanceStatus.DEGRADED.value
    
    def _calculate_trends(self) -> Dict[str, Any]:
        """Calculate performance trends"""        try:
            trends = {}
            
            for metric_name, history in self.metrics_history.items():
                if len(history) < 10:  # Need enough data points
                    continue
                
                # Get recent values
                recent_values = [m.value for m in list(history)[-10:]]
                
                # Calculate trend
                x = list(range(len(recent_values)))
                trend_slope = np.polyfit(x, recent_values, 1)[0]
                
                trend_direction = 'stable'
                if abs(trend_slope) > 0.1:  # Threshold for significant trend
                    trend_direction = 'increasing' if trend_slope > 0 else 'decreasing'
                
                trends[metric_name] = {
                    'direction': trend_direction,
                    'slope': trend_slope,
                    'recent_average': statistics.mean(recent_values),
                    'recent_std': statistics.stdev(recent_values) if len(recent_values) > 1 else 0
                }
            
            return trends
            
        except Exception as e:
            self.logger.error(f"Failed to calculate trends: {e}")
            return {}
    
    def get_detailed_lock_info(self) -> List[LockInfo]:
        """Get detailed information about current locks"""        try:
            lock_query = """                SELECT 
                    l.locktype,
                    d.datname as database,
                    c.relname as relation,
                    l.page,
                    l.tuple,
                    l.virtualxid,
                    l.transactionid,
                    l.mode,
                    l.granted,
                    a.pid,
                    a.query_start
                FROM pg_locks l
                LEFT JOIN pg_database d ON l.database = d.oid
                LEFT JOIN pg_class c ON l.relation = c.oid
                LEFT JOIN pg_stat_activity a ON l.pid = a.pid
                WHERE NOT l.granted
                ORDER BY a.query_start
            """            
            result = self.db_manager.execute_query(lock_query)
            
            locks = []
            if result:
                for row in result:
                    lock_info = LockInfo(
                        locktype=row[0],
                        database=row[1] or '',
                        relation=row[2] or '',
                        page=row[3],
                        tuple=row[4],
                        virtualxid=row[5],
                        transactionid=row[6],
                        mode=row[7],
                        granted=row[8],
                        pid=row[9],
                        wait_start=row[10]
                    )
                    locks.append(lock_info)
            
            return locks
            
        except Exception as e:
            self.logger.error(f"Failed to get lock info: {e}")
            return []
    
    def generate_performance_report(self, hours: int = 24) -> Dict[str, Any]:
        """Generate comprehensive performance report"""        try:
            end_time = datetime.now()
            start_time = end_time - timedelta(hours=hours)
            
            report = {
                'report_period': {
                    'start_time': start_time.isoformat(),
                    'end_time': end_time.isoformat(),
                    'duration_hours': hours
                },
                'summary': self.get_performance_summary(),
                'alerts_summary': self._get_alerts_summary(start_time, end_time),
                'query_analysis': self._get_query_analysis_report(),
                'resource_utilization': self._get_resource_utilization_report(),
                'recommendations': self.optimization_suggestions
            }
            
            return report
            
        except Exception as e:
            self.logger.error(f"Failed to generate performance report: {e}")
            return {'error': str(e)}
    
    def _get_alerts_summary(self, start_time: datetime, end_time: datetime) -> Dict[str, Any]:
        """Get alerts summary for time period"""        try:
            period_alerts = [
                alert for alert in self.active_alerts.values()
                if start_time <= alert.timestamp <= end_time
            ]
            
            summary = {
                'total_alerts': len(period_alerts),
                'by_severity': {},
                'by_metric': {},
                'resolved_alerts': len([a for a in period_alerts if a.resolved]),
                'unresolved_alerts': len([a for a in period_alerts if not a.resolved])
            }
            
            # Group by severity
            for alert in period_alerts:
                severity = alert.severity.value
                summary['by_severity'][severity] = summary['by_severity'].get(severity, 0) + 1
            
            # Group by metric
            for alert in period_alerts:
                metric = alert.metric_name
                summary['by_metric'][metric] = summary['by_metric'].get(metric, 0) + 1
            
            return summary
            
        except Exception as e:
            self.logger.error(f"Failed to get alerts summary: {e}")
            return {}
    
    def _get_query_analysis_report(self) -> Dict[str, Any]:
        """Get query analysis report"""        try:
            if not self.query_performance_cache:
                return {'total_queries': 0}
            
            queries = list(self.query_performance_cache.values())
            
            # Sort by different criteria
            slowest_queries = sorted(queries, key=lambda q: q.mean_exec_time, reverse=True)[:10]
            most_frequent = sorted(queries, key=lambda q: q.calls, reverse=True)[:10]
            highest_total_time = sorted(queries, key=lambda q: q.total_exec_time, reverse=True)[:10]
            
            report = {
                'total_queries': len(queries),
                'slowest_queries': [
                    {
                        'query_text': q.query_text[:200],
                        'mean_exec_time': q.mean_exec_time,
                        'calls': q.calls,
                        'total_exec_time': q.total_exec_time
                    }
                    for q in slowest_queries
                ],
                'most_frequent_queries': [
                    {
                        'query_text': q.query_text[:200],
                        'calls': q.calls,
                        'mean_exec_time': q.mean_exec_time
                    }
                    for q in most_frequent
                ],
                'highest_total_time_queries': [
                    {
                        'query_text': q.query_text[:200],
                        'total_exec_time': q.total_exec_time,
                        'calls': q.calls,
                        'mean_exec_time': q.mean_exec_time
                    }
                    for q in highest_total_time
                ]
            }
            
            return report
            
        except Exception as e:
            self.logger.error(f"Failed to get query analysis report: {e}")
            return {}
    
    def _get_resource_utilization_report(self) -> Dict[str, Any]:
        """Get resource utilization report"""        try:
            resource_metrics = ['cpu_usage', 'memory_usage', 'disk_usage', 'connection_usage']
            
            report = {}
            
            for metric_name in resource_metrics:
                if metric_name in self.metrics_history:
                    history = list(self.metrics_history[metric_name])
                    values = [m.value for m in history]
                    
                    if values:
                        report[metric_name] = {
                            'current': values[-1],
                            'average': statistics.mean(values),
                            'minimum': min(values),
                            'maximum': max(values),
                            'standard_deviation': statistics.stdev(values) if len(values) > 1 else 0
                        }
            
            return report
            
        except Exception as e:
            self.logger.error(f"Failed to get resource utilization report: {e}")
            return {}


# Singleton instance
_performance_monitor = None

def get_performance_monitor() -> DatabasePerformanceMonitor:
    """Get performance monitor singleton instance"""    global _performance_monitor
    if _performance_monitor is None:
        _performance_monitor = DatabasePerformanceMonitor()
    return _performance_monitor

import time
import threading
from typing import Dict, List, Optional, Any, Callable
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from collections import defaultdict, deque
import psutil
import json

from backend.core.config import get_database_settings
from backend.core.logging import get_logger
from backend.core.monitoring import MetricsCollector
from .postgresql_manager import get_postgresql_manager


@dataclass
class QueryMetrics:
    """Query performance metrics"""    query_hash: str
    query_text: str
    execution_count: int
    total_time_ms: float
    avg_time_ms: float
    min_time_ms: float
    max_time_ms: float
    rows_returned: int
    first_seen: datetime
    last_seen: datetime


@dataclass
class ConnectionMetrics:
    """Database connection metrics"""    active_connections: int
    idle_connections: int
    waiting_connections: int
    max_connections: int
    connection_utilization: float
    avg_connection_age: float


@dataclass
class PerformanceAlert:
    """Performance alert information"""    alert_id: str
    alert_type: str
    severity: str
    message: str
    metrics: Dict[str, Any]
    created_at: datetime
    resolved_at: Optional[datetime] = None


class DatabasePerformanceMonitor:
    """    Advanced database performance monitoring system:
    - Real-time query performance tracking
    - Connection pool monitoring
    - Lock detection and analysis
    - Resource utilization tracking
    - Automated alert generation
    - Performance trend analysis
    - Optimization recommendations
    """    
    def __init__(self, monitoring_interval: int = 30):
        self.logger = get_logger(__name__)
        self.config = get_database_settings()
        self.db_manager = get_postgresql_manager()
        self.metrics_collector = MetricsCollector()
        
        self.monitoring_interval = monitoring_interval
        self.is_monitoring = False
        self.monitor_thread: Optional[threading.Thread] = None
        
        # Performance data storage
        self.query_metrics: Dict[str, QueryMetrics] = {}
        self.performance_history: deque = deque(maxlen=1000)
        self.active_alerts: Dict[str, PerformanceAlert] = {}
        
        # Alert thresholds
        self.alert_thresholds = {
            'slow_query_ms': 5000,
            'connection_utilization': 0.8,
            'lock_wait_time_ms': 1000,
            'cpu_utilization': 0.85,
            'memory_utilization': 0.9,
            'disk_utilization': 0.85
        }
        
        # Query pattern analysis
        self.query_patterns: Dict[str, int] = defaultdict(int)
        self.slow_queries: deque = deque(maxlen=100)
        
        self._initialize_monitoring()
    
    def _initialize_monitoring(self) -> None:
        """Initialize performance monitoring"""        try:
            # Enable pg_stat_statements if available
            self._enable_pg_stat_statements()
            
            # Initialize baseline metrics
            self._collect_baseline_metrics()
            
            self.logger.info("Database performance monitoring initialized")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize performance monitoring: {e}")
    
    def _enable_pg_stat_statements(self) -> None:
        """Enable pg_stat_statements extension for query tracking"""        try:
            # Check if extension exists
            check_query = """                SELECT EXISTS (
                    SELECT 1 FROM pg_extension 
                    WHERE extname = 'pg_stat_statements'
                )
            """            
            result = self.db_manager.execute_query(check_query)
            
            if result and not result[0][0]:
                # Try to create extension
                create_query = "CREATE EXTENSION IF NOT EXISTS pg_stat_statements"
                self.db_manager.execute_query(create_query, fetch_results=False)
                self.logger.info("pg_stat_statements extension enabled")
            
        except Exception as e:
            self.logger.warning(f"Could not enable pg_stat_statements: {e}")
    
    def _collect_baseline_metrics(self) -> None:
        """Collect baseline performance metrics"""        try:
            baseline = {
                'timestamp': datetime.now(),
                'connections': self._get_connection_metrics(),
                'database_size': self._get_database_size(),
                'index_usage': self._get_index_usage_stats(),
                'table_stats': self._get_table_statistics()
            }
            
            self.performance_history.append(baseline)
            
        except Exception as e:
            self.logger.error(f"Failed to collect baseline metrics: {e}")
    
    def start_monitoring(self) -> None:
        """Start continuous performance monitoring"""        if self.is_monitoring:
            self.logger.warning("Performance monitoring already started")
            return
        
        self.is_monitoring = True
        self.monitor_thread = threading.Thread(
            target=self._monitoring_loop,
            daemon=True
        )
        self.monitor_thread.start()
        
        self.logger.info(f"Started database performance monitoring (interval: {self.monitoring_interval}s)")
    
    def stop_monitoring(self) -> None:
        """Stop performance monitoring"""        self.is_monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=10)
        
        self.logger.info("Stopped database performance monitoring")
    
    def _monitoring_loop(self) -> None:
        """Main monitoring loop"""        while self.is_monitoring:
            try:
                # Collect current metrics
                current_metrics = self._collect_current_metrics()
                
                # Analyze performance
                self._analyze_performance(current_metrics)
                
                # Check for alerts
                self._check_performance_alerts(current_metrics)
                
                # Update query metrics
                self._update_query_metrics()
                
                # Store historical data
                self.performance_history.append(current_metrics)
                
                # Sleep until next iteration
                time.sleep(self.monitoring_interval)
                
            except Exception as e:
                self.logger.error(f"Performance monitoring error: {e}")
                time.sleep(self.monitoring_interval)
    
    def _collect_current_metrics(self) -> Dict[str, Any]:
        """Collect current performance metrics"""        try:
            metrics = {
                'timestamp': datetime.now(),
                'connections': self._get_connection_metrics(),
                'query_performance': self._get_query_performance(),
                'lock_status': self._get_lock_status(),
                'resource_usage': self._get_resource_usage(),
                'cache_performance': self._get_cache_performance(),
                'wal_status': self._get_wal_status()
            }
            
            return metrics
            
        except Exception as e:
            self.logger.error(f"Failed to collect current metrics: {e}")
            return {'timestamp': datetime.now(), 'error': str(e)}
    
    def _get_connection_metrics(self) -> ConnectionMetrics:
        """Get database connection metrics"""        try:
            query = """                SELECT 
                    count(*) FILTER (WHERE state = 'active') as active,
                    count(*) FILTER (WHERE state = 'idle') as idle,
                    count(*) FILTER (WHERE state = 'idle in transaction') as idle_in_transaction,
                    count(*) as total
                FROM pg_stat_activity
                WHERE pid <> pg_backend_pid()
            """            
            result = self.db_manager.execute_query(query)
            
            if result:
                active, idle, idle_in_tx, total = result[0]
                
                # Get max connections
                max_conn_query = "SHOW max_connections"
                max_result = self.db_manager.execute_query(max_conn_query)
                max_connections = int(max_result[0][0]) if max_result else 100
                
                utilization = total / max_connections if max_connections > 0 else 0
                
                return ConnectionMetrics(
                    active_connections=active,
                    idle_connections=idle,
                    waiting_connections=idle_in_tx,
                    max_connections=max_connections,
                    connection_utilization=utilization,
                    avg_connection_age=0  # Calculate if needed
                )
            
            return ConnectionMetrics(0, 0, 0, 100, 0, 0)
            
        except Exception as e:
            self.logger.error(f"Failed to get connection metrics: {e}")
            return ConnectionMetrics(0, 0, 0, 100, 0, 0)
    
    def _get_query_performance(self) -> Dict[str, Any]:
        """Get query performance statistics"""        try:
            # Try to use pg_stat_statements if available
            query = """                SELECT 
                    queryid,
                    query,
                    calls,
                    total_exec_time,
                    mean_exec_time,
                    min_exec_time,
                    max_exec_time,
                    rows
                FROM pg_stat_statements 
                ORDER BY total_exec_time DESC 
                LIMIT 10
            """            
            try:
                result = self.db_manager.execute_query(query)
                
                if result:
                    queries = []
                    for row in result:
                        queries.append({
                            'queryid': str(row[0]),
                            'query': row[1][:200] + '...' if len(row[1]) > 200 else row[1],
                            'calls': row[2],
                            'total_time_ms': row[3],
                            'avg_time_ms': row[4],
                            'min_time_ms': row[5],
                            'max_time_ms': row[6],
                            'rows': row[7]
                        })
                    
                    return {'top_queries': queries}
            
            except Exception:
                # Fallback if pg_stat_statements not available
                pass
            
            # Fallback to basic activity monitoring
            activity_query = """                SELECT 
                    pid,
                    state,
                    query_start,
                    now() - query_start as duration,
                    query
                FROM pg_stat_activity 
                WHERE state = 'active' 
                AND pid <> pg_backend_pid()
                ORDER BY query_start
            """            
            result = self.db_manager.execute_query(activity_query)
            
            active_queries = []
            if result:
                for row in result:
                    active_queries.append({
                        'pid': row[0],
                        'state': row[1],
                        'duration': str(row[3]) if row[3] else '0',
                        'query': row[4][:200] + '...' if row[4] and len(row[4]) > 200 else row[4]
                    })
            
            return {'active_queries': active_queries}
            
        except Exception as e:
            self.logger.error(f"Failed to get query performance: {e}")
            return {}
    
    def _get_lock_status(self) -> Dict[str, Any]:
        """Get database lock information"""        try:
            query = """                SELECT 
                    mode,
                    locktype,
                    count(*) as lock_count
                FROM pg_locks 
                WHERE NOT granted
                GROUP BY mode, locktype
            """            
            result = self.db_manager.execute_query(query)
            
            locks = []
            if result:
                for row in result:
                    locks.append({
                        'mode': row[0],
                        'locktype': row[1],
                        'count': row[2]
                    })
            
            # Get waiting queries
            waiting_query = """                SELECT 
                    blocked_locks.pid AS blocked_pid,
                    blocked_activity.query AS blocked_query,
                    blocking_locks.pid AS blocking_pid,
                    blocking_activity.query AS blocking_query
                FROM pg_catalog.pg_locks blocked_locks
                JOIN pg_catalog.pg_stat_activity blocked_activity 
                    ON blocked_activity.pid = blocked_locks.pid
                JOIN pg_catalog.pg_locks blocking_locks 
                    ON blocking_locks.locktype = blocked_locks.locktype
                    AND blocking_locks.database IS NOT DISTINCT FROM blocked_locks.database
                    AND blocking_locks.relation IS NOT DISTINCT FROM blocked_locks.relation
                    AND blocking_locks.page IS NOT DISTINCT FROM blocked_locks.page
                    AND blocking_locks.tuple IS NOT DISTINCT FROM blocked_locks.tuple
                    AND blocking_locks.virtualxid IS NOT DISTINCT FROM blocked_locks.virtualxid
                    AND blocking_locks.transactionid IS NOT DISTINCT FROM blocked_locks.transactionid
                    AND blocking_locks.classid IS NOT DISTINCT FROM blocked_locks.classid
                    AND blocking_locks.objid IS NOT DISTINCT FROM blocked_locks.objid
                    AND blocking_locks.objsubid IS NOT DISTINCT FROM blocked_locks.objsubid
                    AND blocking_locks.pid != blocked_locks.pid
                JOIN pg_catalog.pg_stat_activity blocking_activity 
                    ON blocking_activity.pid = blocking_locks.pid
                WHERE NOT blocked_locks.granted
            """            
            waiting_result = self.db_manager.execute_query(waiting_query)
            
            waiting_queries = []
            if waiting_result:
                for row in waiting_result:
                    waiting_queries.append({
                        'blocked_pid': row[0],
                        'blocked_query': row[1][:100] + '...' if row[1] and len(row[1]) > 100 else row[1],
                        'blocking_pid': row[2],
                        'blocking_query': row[3][:100] + '...' if row[3] and len(row[3]) > 100 else row[3]
                    })
            
            return {
                'locks': locks,
                'waiting_queries': waiting_queries,
                'total_locks': len(locks),
                'total_waiting': len(waiting_queries)
            }
            
        except Exception as e:
            self.logger.error(f"Failed to get lock status: {e}")
            return {}
    
    def _get_resource_usage(self) -> Dict[str, Any]:
        """Get system resource usage"""        try:
            # CPU usage
            cpu_percent = psutil.cpu_percent(interval=1)
            
            # Memory usage
            memory = psutil.virtual_memory()
            
            # Disk usage
            disk = psutil.disk_usage('/')
            
            # Database-specific memory usage
            db_memory_query = """                SELECT 
                    sum(shared_blks_hit) as shared_blks_hit,
                    sum(shared_blks_read) as shared_blks_read,
                    sum(shared_blks_hit) + sum(shared_blks_read) as total_blks
                FROM pg_stat_database
            """            
            db_memory_result = self.db_manager.execute_query(db_memory_query)
            
            cache_hit_ratio = 0
            if db_memory_result and db_memory_result[0][2] > 0:
                hit, read, total = db_memory_result[0]
                cache_hit_ratio = hit / total if total > 0 else 0
            
            return {
                'cpu_percent': cpu_percent,
                'memory_percent': memory.percent,
                'memory_available_gb': memory.available / (1024**3),
                'disk_percent': disk.percent,
                'disk_free_gb': disk.free / (1024**3),
                'db_cache_hit_ratio': cache_hit_ratio
            }
            
        except Exception as e:
            self.logger.error(f"Failed to get resource usage: {e}")
            return {}
    
    def _get_cache_performance(self) -> Dict[str, Any]:
        """Get database cache performance metrics"""        try:
            query = """                SELECT 
                    datname,
                    blks_read,
                    blks_hit,
                    blk_read_time,
                    blk_write_time,
                    case when blks_hit + blks_read = 0 then 0 
                         else blks_hit::float / (blks_hit + blks_read) 
                    end as hit_ratio
                FROM pg_stat_database 
                WHERE datname IS NOT NULL
            """            
            result = self.db_manager.execute_query(query)
            
            databases = []
            if result:
                for row in result:
                    databases.append({
                        'database': row[0],
                        'blocks_read': row[1],
                        'blocks_hit': row[2],
                        'read_time_ms': row[3],
                        'write_time_ms': row[4],
                        'hit_ratio': row[5]
                    })
            
            return {'databases': databases}
            
        except Exception as e:
            self.logger.error(f"Failed to get cache performance: {e}")
            return {}
    
    def _get_wal_status(self) -> Dict[str, Any]:
        """Get WAL (Write-Ahead Log) status"""        try:
            query = """                SELECT 
                    pg_current_wal_lsn() as current_lsn,
                    pg_wal_lsn_diff(pg_current_wal_lsn(), '0/0') as wal_bytes
            """            
            result = self.db_manager.execute_query(query)
            
            if result:
                return {
                    'current_lsn': result[0][0],
                    'wal_bytes': result[0][1]
                }
            
            return {}
            
        except Exception as e:
            self.logger.error(f"Failed to get WAL status: {e}")
            return {}
    
    def _get_database_size(self) -> Dict[str, Any]:
        """Get database size information"""        try:
            query = """                SELECT 
                    datname,
                    pg_size_pretty(pg_database_size(datname)) as size,
                    pg_database_size(datname) as size_bytes
                FROM pg_database 
                WHERE datname NOT IN ('template0', 'template1', 'postgres')
                ORDER BY pg_database_size(datname) DESC
            """            
            result = self.db_manager.execute_query(query)
            
            databases = []
            if result:
                for row in result:
                    databases.append({
                        'name': row[0],
                        'size_formatted': row[1],
                        'size_bytes': row[2]
                    })
            
            return {'databases': databases}
            
        except Exception as e:
            self.logger.error(f"Failed to get database size: {e}")
            return {}
    
    def _get_index_usage_stats(self) -> Dict[str, Any]:
        """Get index usage statistics"""        try:
            query = """                SELECT 
                    schemaname,
                    tablename,
                    indexname,
                    idx_scan,
                    idx_tup_read,
                    idx_tup_fetch
                FROM pg_stat_user_indexes 
                ORDER BY idx_scan DESC 
                LIMIT 20
            """            
            result = self.db_manager.execute_query(query)
            
            indexes = []
            if result:
                for row in result:
                    indexes.append({
                        'schema': row[0],
                        'table': row[1],
                        'index': row[2],
                        'scans': row[3],
                        'tuples_read': row[4],
                        'tuples_fetched': row[5]
                    })
            
            return {'indexes': indexes}
            
        except Exception as e:
            self.logger.error(f"Failed to get index usage stats: {e}")
            return {}
    
    def _get_table_statistics(self) -> Dict[str, Any]:
        """Get table usage statistics"""        try:
            query = """                SELECT 
                    schemaname,
                    relname,
                    seq_scan,
                    seq_tup_read,
                    idx_scan,
                    idx_tup_fetch,
                    n_tup_ins,
                    n_tup_upd,
                    n_tup_del,
                    n_live_tup,
                    n_dead_tup
                FROM pg_stat_user_tables 
                ORDER BY seq_scan + idx_scan DESC 
                LIMIT 20
            """            
            result = self.db_manager.execute_query(query)
            
            tables = []
            if result:
                for row in result:
                    tables.append({
                        'schema': row[0],
                        'table': row[1],
                        'seq_scans': row[2],
                        'seq_tuples_read': row[3],
                        'index_scans': row[4],
                        'index_tuples_fetched': row[5],
                        'inserts': row[6],
                        'updates': row[7],
                        'deletes': row[8],
                        'live_tuples': row[9],
                        'dead_tuples': row[10]
                    })
            
            return {'tables': tables}
            
        except Exception as e:
            self.logger.error(f"Failed to get table statistics: {e}")
            return {}
    
    def _analyze_performance(self, metrics: Dict[str, Any]) -> None:
        """Analyze performance metrics and identify issues"""        try:
            # Analyze connection utilization
            connections = metrics.get('connections')
            if connections and connections.connection_utilization > 0.8:
                self.logger.warning(
                    f"High connection utilization: {connections.connection_utilization:.2%}"
                )
            
            # Analyze resource usage
            resources = metrics.get('resource_usage', {})
            
            if resources.get('cpu_percent', 0) > 85:
                self.logger.warning(f"High CPU usage: {resources['cpu_percent']}%")
            
            if resources.get('memory_percent', 0) > 90:
                self.logger.warning(f"High memory usage: {resources['memory_percent']}%")
            
            # Analyze cache performance
            cache_hit_ratio = resources.get('db_cache_hit_ratio', 1)
            if cache_hit_ratio < 0.9:
                self.logger.warning(f"Low cache hit ratio: {cache_hit_ratio:.2%}")
            
            # Analyze locks
            locks = metrics.get('lock_status', {})
            waiting_queries = locks.get('total_waiting', 0)
            if waiting_queries > 0:
                self.logger.warning(f"Queries waiting for locks: {waiting_queries}")
            
        except Exception as e:
            self.logger.error(f"Performance analysis failed: {e}")
    
    def _check_performance_alerts(self, metrics: Dict[str, Any]) -> None:
        """Check for performance alerts"""        try:
            current_time = datetime.now()
            
            # Check connection utilization alert
            connections = metrics.get('connections')
            if connections and connections.connection_utilization > self.alert_thresholds['connection_utilization']:
                alert_id = 'connection_utilization'
                if alert_id not in self.active_alerts:
                    alert = PerformanceAlert(
                        alert_id=alert_id,
                        alert_type='connection_utilization',
                        severity='warning',
                        message=f"High connection utilization: {connections.connection_utilization:.2%}",
                        metrics={'utilization': connections.connection_utilization},
                        created_at=current_time
                    )
                    self.active_alerts[alert_id] = alert
                    self._trigger_alert(alert)
            
            # Check CPU utilization alert
            resources = metrics.get('resource_usage', {})
            cpu_percent = resources.get('cpu_percent', 0)
            if cpu_percent > self.alert_thresholds['cpu_utilization'] * 100:
                alert_id = 'cpu_utilization'
                if alert_id not in self.active_alerts:
                    alert = PerformanceAlert(
                        alert_id=alert_id,
                        alert_type='cpu_utilization',
                        severity='critical',
                        message=f"High CPU utilization: {cpu_percent}%",
                        metrics={'cpu_percent': cpu_percent},
                        created_at=current_time
                    )
                    self.active_alerts[alert_id] = alert
                    self._trigger_alert(alert)
            
            # Check memory utilization alert
            memory_percent = resources.get('memory_percent', 0)
            if memory_percent > self.alert_thresholds['memory_utilization'] * 100:
                alert_id = 'memory_utilization'
                if alert_id not in self.active_alerts:
                    alert = PerformanceAlert(
                        alert_id=alert_id,
                        alert_type='memory_utilization',
                        severity='critical',
                        message=f"High memory utilization: {memory_percent}%",
                        metrics={'memory_percent': memory_percent},
                        created_at=current_time
                    )
                    self.active_alerts[alert_id] = alert
                    self._trigger_alert(alert)
            
        except Exception as e:
            self.logger.error(f"Alert checking failed: {e}")
    
    def _trigger_alert(self, alert: PerformanceAlert) -> None:
        """Trigger performance alert"""        try:
            # Log alert
            self.logger.critical(f"PERFORMANCE ALERT: {alert.message}")
            
            # Record metric
            self.metrics_collector.record_counter(
                'performance.alerts.triggered',
                tags={'type': alert.alert_type, 'severity': alert.severity}
            )
            
            # Send notification (implement your notification system)
            # Example: send to Slack, email, PagerDuty, etc.
            
        except Exception as e:
            self.logger.error(f"Failed to trigger alert: {e}")
    
    def _update_query_metrics(self) -> None:
        """Update query performance metrics"""        try:
            # This would be implemented with pg_stat_statements
            # or custom query tracking
            pass
            
        except Exception as e:
            self.logger.error(f"Failed to update query metrics: {e}")
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """Get comprehensive performance summary"""        try:
            if not self.performance_history:
                return {'error': 'No performance data available'}
            
            latest_metrics = self.performance_history[-1]
            
            summary = {
                'timestamp': latest_metrics['timestamp'].isoformat(),
                'overall_status': 'healthy',  # Calculate based on metrics
                'connections': latest_metrics.get('connections'),
                'resource_usage': latest_metrics.get('resource_usage'),
                'active_alerts': len(self.active_alerts),
                'alert_details': [asdict(alert) for alert in self.active_alerts.values()],
                'top_queries': latest_metrics.get('query_performance', {}),
                'lock_status': latest_metrics.get('lock_status', {}),
                'recommendations': self._generate_recommendations(latest_metrics)
            }
            
            # Determine overall status
            if self.active_alerts:
                critical_alerts = [a for a in self.active_alerts.values() if a.severity == 'critical']
                if critical_alerts:
                    summary['overall_status'] = 'critical'
                else:
                    summary['overall_status'] = 'warning'
            
            return summary
            
        except Exception as e:
            self.logger.error(f"Failed to get performance summary: {e}")
            return {'error': str(e)}
    
    def _generate_recommendations(self, metrics: Dict[str, Any]) -> List[str]:
        """Generate performance optimization recommendations"""        recommendations = []
        
        try:
            connections = metrics.get('connections')
            if connections and connections.connection_utilization > 0.7:
                recommendations.append(
                    "Consider increasing connection pool size or optimizing connection usage"
                )
            
            resources = metrics.get('resource_usage', {})
            
            if resources.get('db_cache_hit_ratio', 1) < 0.9:
                recommendations.append(
                    "Consider increasing shared_buffers to improve cache hit ratio"
                )
            
            if resources.get('cpu_percent', 0) > 70:
                recommendations.append(
                    "High CPU usage detected. Consider query optimization or scaling up"
                )
            
            locks = metrics.get('lock_status', {})
            if locks.get('total_waiting', 0) > 0:
                recommendations.append(
                    "Lock contention detected. Review long-running transactions and query optimization"
                )
            
        except Exception as e:
            self.logger.error(f"Failed to generate recommendations: {e}")
        
        return recommendations
    
    def get_historical_trends(self, hours: int = 24) -> Dict[str, Any]:
        """Get historical performance trends"""        try:
            cutoff_time = datetime.now() - timedelta(hours=hours)
            
            historical_data = [
                entry for entry in self.performance_history
                if entry['timestamp'] > cutoff_time
            ]
            
            if not historical_data:
                return {'error': 'No historical data available for the specified period'}
            
            # Calculate trends
            trends = {
                'time_range': f"Last {hours} hours",
                'data_points': len(historical_data),
                'connection_trend': self._calculate_trend(historical_data, 'connections'),
                'cpu_trend': self._calculate_trend(historical_data, 'resource_usage.cpu_percent'),
                'memory_trend': self._calculate_trend(historical_data, 'resource_usage.memory_percent'),
                'cache_hit_trend': self._calculate_trend(historical_data, 'resource_usage.db_cache_hit_ratio')
            }
            
            return trends
            
        except Exception as e:
            self.logger.error(f"Failed to get historical trends: {e}")
            return {'error': str(e)}
    
    def _calculate_trend(self, data: List[Dict], metric_path: str) -> Dict[str, Any]:
        """Calculate trend for a specific metric"""        try:
            values = []
            
            for entry in data:
                value = entry
                for key in metric_path.split('.'):
                    if isinstance(value, dict) and key in value:
                        value = value[key]
                    else:
                        value = None
                        break
                
                if value is not None:
                    if hasattr(value, 'connection_utilization'):
                        # Handle ConnectionMetrics object
                        values.append(value.connection_utilization)
                    elif isinstance(value, (int, float)):
                        values.append(value)
            
            if not values:
                return {'trend': 'no_data', 'values': []}
            
            # Calculate trend direction
            if len(values) > 1:
                recent_avg = sum(values[-5:]) / min(5, len(values))
                older_avg = sum(values[:5]) / min(5, len(values))
                
                if recent_avg > older_avg * 1.1:
                    trend = 'increasing'
                elif recent_avg < older_avg * 0.9:
                    trend = 'decreasing'
                else:
                    trend = 'stable'
            else:
                trend = 'insufficient_data'
            
            return {
                'trend': trend,
                'current_value': values[-1] if values else None,
                'min_value': min(values) if values else None,
                'max_value': max(values) if values else None,
                'avg_value': sum(values) / len(values) if values else None
            }
            
        except Exception as e:
            self.logger.error(f"Failed to calculate trend for {metric_path}: {e}")
            return {'trend': 'error', 'error': str(e)}


# Singleton instance
_performance_monitor = None

def get_performance_monitor() -> DatabasePerformanceMonitor:
    """Get database performance monitor singleton instance"""    global _performance_monitor
    if _performance_monitor is None:
        _performance_monitor = DatabasePerformanceMonitor()
    return _performance_monitor
