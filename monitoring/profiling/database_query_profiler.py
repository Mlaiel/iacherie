# WARNING: Potential SQL injection risk - use parameterized queries
"""⚡ Database Query Performance Profiler
======================================

Advanced profiling system for database queries in the Creator Economy platform.
Provides real-time monitoring of SQL query execution, index usage analysis, and query optimization.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️ INTELLECTUAL PROPERTY WARNING:
=====================================
This code is proprietary to Fahed Mlaiel <mlaiel@live.de>
- Commercial use FORBIDDEN without written authorization
- Reverse engineering STRICTLY PROHIBITED
- Distribution FORBIDDEN without explicit license
- Violation = Automatic legal prosecution

🏢 ENTERPRISE USAGE:
- Enterprise license available on request
- Technical support included with license
- Maintenance and updates assured
- Technical team training provided
"""

import asyncio
import logging
import time
import threading
import hashlib
from typing import Dict, List, Optional, Any, Callable, Union, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import json
import statistics
from collections import defaultdict, deque
import re
import gc

from prometheus_client import Counter, Gauge, Histogram, Summary

logger = logging.getLogger(__name__)


class QueryType(Enum):
    """Database query types"""
    
    SELECT = "select"
    INSERT = "insert"
    UPDATE = "update"
    DELETE = "delete"
    CREATE = "create"
    ALTER = "alter"
    DROP = "drop"
    TRANSACTION = "transaction"
    STORED_PROCEDURE = "stored_procedure"
    AGGREGATE = "aggregate"
    JOIN = "join"
    SUBQUERY = "subquery"


class DatabaseEngine(Enum):
    """Supported database engines"""
    
    POSTGRESQL = "postgresql"
    MYSQL = "mysql"
    MONGODB = "mongodb"
    REDIS = "redis"
    ELASTICSEARCH = "elasticsearch"
    SQLITE = "sqlite"
    ORACLE = "oracle"
    MSSQL = "mssql"


class QueryComplexity(Enum):
    """Query complexity levels"""
    
    SIMPLE = "simple"
    MODERATE = "moderate"
    COMPLEX = "complex"
    VERY_COMPLEX = "very_complex"


@dataclass
class QueryMetadata:
    """Database query metadata"""
    
    query_hash: str
    query_text: str
    query_type: QueryType
    database_engine: DatabaseEngine
    table_names: List[str]
    index_names: List[str]
    parameters: Dict[str, Any]
    complexity: QueryComplexity
    estimated_rows: Optional[int] = None
    query_plan: Optional[Dict[str, Any]] = None
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class QueryExecutionMetrics:
    """Database query execution performance metrics"""
    
    query_metadata: QueryMetadata
    execution_time: float  # seconds
    rows_affected: int
    rows_examined: int
    bytes_sent: int
    bytes_received: int
    connection_time: float  # seconds
    lock_time: float  # seconds
    sort_time: float  # seconds
    index_hits: int
    index_misses: int
    cache_hit: bool = False
    memory_usage: int = 0  # MB
    cpu_usage: float = 0.0  # percentage
    disk_io_reads: int = 0
    disk_io_writes: int = 0
    network_latency: float = 0.0  # seconds
    connection_pool_size: int = 0
    connection_pool_active: int = 0
    transaction_isolation_level: Optional[str] = None
    error_count: int = 0
    warnings: List[str] = field(default_factory=list)
    optimization_suggestions: List[str] = field(default_factory=list)
    timestamp: datetime = field(default_factory=datetime.now)
    
    @property
    def rows_per_second(self) -> float:
        """Calculate rows processed per second"""
        return self.rows_affected / self.execution_time if self.execution_time > 0 else 0
    
    @property
    def cache_efficiency(self) -> float:
        """Calculate cache efficiency percentage"""
        total_hits = self.index_hits + self.index_misses
        return (self.index_hits / total_hits) * 100 if total_hits > 0 else 0


@dataclass
class QueryBottleneck:
    """Database query bottleneck detection"""
    
    bottleneck_type: str
    severity: str  # low, medium, high, critical
    description: str
    affected_query_type: QueryType
    database_engine: DatabaseEngine
    performance_impact: float  # percentage
    optimization_suggestions: List[str]
    index_recommendations: List[str]
    schema_recommendations: List[str]
    timestamp: datetime = field(default_factory=datetime.now)


class DatabaseQueryProfiler:
    """
    Advanced Database Query Performance Profiler
    
    Provides comprehensive profiling for database operations with focus on:
    - Real-time query execution monitoring
    - Index usage analysis
    - Query plan optimization
    - Connection pool monitoring
    - Transaction performance tracking
    """
    
    def __init__(
        self,
        enable_query_plan_analysis: bool = True,
        enable_index_monitoring: bool = True,
        enable_connection_pool_monitoring: bool = True,
        sampling_interval: float = 1.0,
        max_history_size: int = 50000,
        slow_query_threshold: float = 1.0
    ):
        """
        Initialize Database Query Profiler
        
        Args:
            enable_query_plan_analysis: Enable query execution plan analysis
            enable_index_monitoring: Enable index usage monitoring
            enable_connection_pool_monitoring: Enable connection pool tracking
            sampling_interval: Metrics collection interval in seconds
            max_history_size: Maximum number of metrics to keep
            slow_query_threshold: Threshold for slow query detection (seconds)
        """
        self.enable_query_plan_analysis = enable_query_plan_analysis
        self.enable_index_monitoring = enable_index_monitoring
        self.enable_connection_pool_monitoring = enable_connection_pool_monitoring
        self.sampling_interval = sampling_interval
        self.max_history_size = max_history_size
        self.slow_query_threshold = slow_query_threshold
        
        # Metrics storage
        self.query_metrics: deque = deque(maxlen=max_history_size)
        self.bottlenecks: deque = deque(maxlen=max_history_size)
        
        # Active profiling sessions
        self.active_sessions: Dict[str, Dict] = {}
        self.session_lock = threading.Lock()
        
        # Query pattern analysis
        self.query_patterns: Dict[str, List[float]] = defaultdict(list)
        self.slow_queries: deque = deque(maxlen=1000)
        
        # Connection pool monitoring
        self.connection_pools: Dict[str, Dict[str, Any]] = {}
        
        # Index usage tracking
        self.index_usage_stats: Dict[str, Dict[str, int]] = defaultdict(lambda: defaultdict(int))
        
        # Database connection handlers
        self.db_handlers: Dict[DatabaseEngine, Any] = {}
        
        # Prometheus metrics
        self._setup_prometheus_metrics()
        
        # Background monitoring
        self.monitoring_active = False
        self.monitoring_thread: Optional[threading.Thread] = None
        
        logger.info("DatabaseQueryProfiler initialized")
    
    def _setup_prometheus_metrics(self):
        """Setup Prometheus metrics for monitoring"""
        
        self.query_execution_time_histogram = Histogram(
            'db_query_execution_time_seconds',
            'Database query execution time',
            ['query_type', 'database_engine', 'complexity']
        )
        
        self.query_throughput_gauge = Gauge(
            'db_query_throughput_rows_per_second',
            'Database query throughput in rows per second',
            ['query_type', 'database_engine']
        )
        
        self.slow_query_counter = Counter(
            'db_slow_queries_total',
            'Total number of slow database queries',
            ['query_type', 'database_engine']
        )
        
        self.index_efficiency_gauge = Gauge(
            'db_index_efficiency_percent',
            'Database index efficiency percentage',
            ['database_engine', 'table_name']
        )
        
        self.connection_pool_gauge = Gauge(
            'db_connection_pool_size',
            'Database connection pool metrics',
            ['pool_name', 'metric_type']
        )
        
        self.cache_hit_rate_gauge = Gauge(
            'db_cache_hit_rate_percent',
            'Database cache hit rate percentage',
            ['database_engine']
        )
        
        self.bottleneck_counter = Counter(
            'db_bottlenecks_total',
            'Total database bottlenecks detected',
            ['bottleneck_type', 'severity']
        )
        
        self.error_counter = Counter(
            'db_errors_total',
            'Total database errors',
            ['database_engine', 'error_type']
        )
    
    def register_database_handler(self, engine: DatabaseEngine, handler: Any):
        """Register a database handler for specific engine"""
        self.db_handlers[engine] = handler
        logger.info("Registered database handler for %s", engine.value)
    
    def _analyze_query(self, query_text: str, database_engine: DatabaseEngine) -> QueryMetadata:
        """Analyze query to extract metadata"""
        try:
            # Normalize query text
            normalized_query = re.sub(r'\s+', ' ', query_text.strip().lower())
            
            # Generate query hash
            query_hash = hashlib.md5(normalized_query.encode()).hexdigest()
            
            # Determine query type
            query_type = self._determine_query_type(normalized_query)
            
            # Extract table names
            table_names = self._extract_table_names(normalized_query, query_type)
            
            # Extract index hints (simplified)
            index_names = self._extract_index_names(normalized_query)
            
            # Assess query complexity
            complexity = self._assess_query_complexity(normalized_query, table_names)
            
            return QueryMetadata(
                query_hash=query_hash,
                query_text=query_text,
                query_type=query_type,
                database_engine=database_engine,
                table_names=table_names,
                index_names=index_names,
                parameters={},  # To be populated with actual parameters
                complexity=complexity
            )
            
        except Exception as e:
            logger.error("Error analyzing query: %s", e)
            return QueryMetadata(
                query_hash="unknown",
                query_text=query_text,
                query_type=QueryType.SELECT,
                database_engine=database_engine,
                table_names=[],
                index_names=[],
                parameters={},
                complexity=QueryComplexity.SIMPLE
            )
    
    def _determine_query_type(self, normalized_query: str) -> QueryType:
        """Determine the type of SQL query"""
        if normalized_query.startswith('select'):
            if 'group by' in normalized_query or 'count(' in normalized_query or 'sum(' in normalized_query:
                return QueryType.AGGREGATE
            elif 'join' in normalized_query:
                return QueryType.JOIN
            elif any(sub in normalized_query for sub in ['exists', 'in (select', 'any', 'all']):
                return QueryType.SUBQUERY
            else:
                return QueryType.SELECT
        elif normalized_query.startswith('insert'):
            return QueryType.INSERT
        elif normalized_query.startswith('update'):
            return QueryType.UPDATE
        elif normalized_query.startswith('delete'):
            return QueryType.DELETE
        elif normalized_query.startswith('create'):
            return QueryType.CREATE
        elif normalized_query.startswith('alter'):
            return QueryType.ALTER
        elif normalized_query.startswith('drop'):
            return QueryType.DROP
        elif any(word in normalized_query for word in ['begin', 'commit', 'rollback']):
            return QueryType.TRANSACTION
        elif any(word in normalized_query for word in ['call', 'exec', 'execute']):
            return QueryType.STORED_PROCEDURE
        else:
            return QueryType.SELECT
    
    def _extract_table_names(self, normalized_query: str, query_type: QueryType) -> List[str]:
        """Extract table names from query"""
        table_names = []
        
        try:
            # Simple regex patterns for different query types
            if query_type == QueryType.SELECT:
                # Match FROM clause
                from_match = re.search(r'from\s+(\w+)', normalized_query)
                if from_match:
                    table_names.append(from_match.group(1))
                
                # Match JOIN clauses
                join_matches = re.findall(r'join\s+(\w+)', normalized_query)
                table_names.extend(join_matches)
            
            elif query_type == QueryType.INSERT:
                # Match INSERT INTO
                insert_match = re.search(r'insert\s+into\s+(\w+)', normalized_query)
                if insert_match:
                    table_names.append(insert_match.group(1))
            
            elif query_type == QueryType.UPDATE:
                # Match UPDATE table
                update_match = re.search(r'update\s+(\w+)', normalized_query)
                if update_match:
                    table_names.append(update_match.group(1))
            
            elif query_type == QueryType.DELETE:
                # Match DELETE FROM
                delete_match = re.search(r'delete\s+from\s+(\w+)', normalized_query)
                if delete_match:
                    table_names.append(delete_match.group(1))
            
            # Remove duplicates while preserving order
            return list(dict.fromkeys(table_names))
            
        except Exception as e:
            logger.error("Error extracting table names: %s", e)
            return []
    
    def _extract_index_names(self, normalized_query: str) -> List[str]:
        """Extract index hints from query"""
        index_names = []
        
        try:
            # Look for index hints (MySQL style)
            index_hints = re.findall(r'use\s+index\s*\(\s*(\w+)\s*\)', normalized_query)
            index_names.extend(index_hints)
            
            # Look for force index
            force_hints = re.findall(r'force\s+index\s*\(\s*(\w+)\s*\)', normalized_query)
            index_names.extend(force_hints)
            
            return list(dict.fromkeys(index_names))
            
        except Exception as e:
            logger.error("Error extracting index names: %s", e)
            return []
    
    def _assess_query_complexity(self, normalized_query: str, table_names: List[str]) -> QueryComplexity:
        """Assess the complexity of a query"""
        complexity_score = 0
        
        # Table count factor
        complexity_score += len(table_names)
        
        # JOIN complexity
        join_count = normalized_query.count('join')
        complexity_score += join_count * 2
        
        # Subquery complexity
        subquery_count = normalized_query.count('select') - 1  # Subtract main select
        complexity_score += subquery_count * 3
        
        # Function complexity
        function_patterns = ['group by', 'order by', 'having', 'union', 'distinct', 'case when']
        for pattern in function_patterns:
            if pattern in normalized_query:
                complexity_score += 1
        
        # Aggregate functions
        aggregate_functions = ['count(', 'sum(', 'avg(', 'max(', 'min(', 'group_concat(']
        for func in aggregate_functions:
            complexity_score += normalized_query.count(func)
        
        # Determine complexity level
        if complexity_score <= 2:
            return QueryComplexity.SIMPLE
        elif complexity_score <= 5:
            return QueryComplexity.MODERATE
        elif complexity_score <= 10:
            return QueryComplexity.COMPLEX
        else:
            return QueryComplexity.VERY_COMPLEX
    
    def _get_query_plan(self, query_text: str, database_engine: DatabaseEngine) -> Optional[Dict[str, Any]]:
        """Get query execution plan"""
        if not self.enable_query_plan_analysis:
            return None
        
        try:
            handler = self.db_handlers.get(database_engine)
            if not handler:
                return None
            
            if database_engine == DatabaseEngine.POSTGRESQL:
                return self._get_postgresql_plan(handler, query_text)
            elif database_engine == DatabaseEngine.MYSQL:
                return self._get_mysql_plan(handler, query_text)
            elif database_engine == DatabaseEngine.MONGODB:
                return self._get_mongodb_plan(handler, query_text)
            
            return None
            
        except Exception as e:
            logger.error("Error getting query plan: %s", e)
            return None
    
    def _get_postgresql_plan(self, connection, query_text: str) -> Dict[str, Any]:
        """Get PostgreSQL execution plan"""
        try:
            with connection.cursor() as cursor:
                cursor.execute(f"EXPLAIN (FORMAT JSON, ANALYZE, BUFFERS) {query_text}")
                plan = cursor.fetchone()[0]
                return plan[0] if plan else {}
        except Exception as e:
            logger.error("Error getting PostgreSQL plan: %s", e)
            return {}
    
    def _get_mysql_plan(self, connection, query_text: str) -> Dict[str, Any]:
        """Get MySQL execution plan"""
        try:
            with connection.cursor() as cursor:
                cursor.execute(f"EXPLAIN FORMAT=JSON {query_text}")
                plan = cursor.fetchone()[0]
                return json.loads(plan) if plan else {}
        except Exception as e:
            logger.error("Error getting MySQL plan: %s", e)
            return {}
    
    def _get_mongodb_plan(self, collection, query_text: str) -> Dict[str, Any]:
        """Get MongoDB execution plan"""
        try:
            # This is a simplified example for MongoDB
            # In practice, you'd parse the query_text and use explain()
            return {"mongodb": "plan_analysis_placeholder"}
        except Exception as e:
            logger.error("Error getting MongoDB plan: %s", e)
            return {}
    
    def start_monitoring(self):
        """Start background monitoring thread"""
        if self.monitoring_active:
            return
        
        self.monitoring_active = True
        self.monitoring_thread = threading.Thread(target=self._monitoring_loop, daemon=True)
        self.monitoring_thread.start()
        logger.info("Database query background monitoring started")
    
    def stop_monitoring(self):
        """Stop background monitoring"""
        self.monitoring_active = False
        if self.monitoring_thread:
            self.monitoring_thread.join(timeout=5.0)
        logger.info("Database query background monitoring stopped")
    
    def _monitoring_loop(self):
        """Background monitoring loop"""
        while self.monitoring_active:
            try:
                # Update connection pool metrics
                if self.enable_connection_pool_monitoring:
                    self._update_connection_pool_metrics()
                
                # Analyze for bottlenecks
                self._detect_bottlenecks()
                
                # Update index usage statistics
                if self.enable_index_monitoring:
                    self._update_index_statistics()
                
                time.sleep(self.sampling_interval)
                
            except Exception as e:
                logger.error("Error in database monitoring loop: %s", e)
                time.sleep(1.0)
    
    def start_query_profiling(
        self,
        query_text: str,
        database_engine: DatabaseEngine,
        parameters: Optional[Dict[str, Any]] = None,
        connection_pool_name: Optional[str] = None,
        session_id: Optional[str] = None
    ) -> str:
        """
        Start profiling a database query
        
        Args:
            query_text: SQL query text
            database_engine: Database engine type
            parameters: Query parameters
            connection_pool_name: Connection pool identifier
            session_id: Optional session identifier
        
        Returns:
            session_id: Unique identifier for this profiling session
        """
        if session_id is None:
            session_id = f"query_{int(time.time() * 1000)}"
        
        # Analyze query
        query_metadata = self._analyze_query(query_text, database_engine)
        
        # Update with parameters
        if parameters:
            query_metadata.parameters = parameters
        
        # Get query plan if enabled
        query_plan = self._get_query_plan(query_text, database_engine)
        if query_plan:
            query_metadata.query_plan = query_plan
        
        session_data = {
            'query_metadata': query_metadata,
            'database_engine': database_engine,
            'connection_pool_name': connection_pool_name,
            'start_time': time.time(),
            'connection_start': None,
            'execution_start': None,
            'error_count': 0,
            'warnings': []
        }
        
        with self.session_lock:
            self.active_sessions[session_id] = session_data
        
        logger.debug("Started query profiling session: %s", session_id)
        return session_id
    
    def mark_connection_start(self, session_id: str):
        """Mark the start of database connection"""
        with self.session_lock:
            if session_id in self.active_sessions:
                self.active_sessions[session_id]['connection_start'] = time.time()
    
    def mark_execution_start(self, session_id: str):
        """Mark the start of query execution"""
        with self.session_lock:
            if session_id in self.active_sessions:
                self.active_sessions[session_id]['execution_start'] = time.time()
    
    def add_warning(self, session_id: str, warning: str):
        """Add a warning to the session"""
        with self.session_lock:
            if session_id in self.active_sessions:
                self.active_sessions[session_id]['warnings'].append(warning)
    
    def increment_error_count(self, session_id: str):
        """Increment error count for the session"""
        with self.session_lock:
            if session_id in self.active_sessions:
                self.active_sessions[session_id]['error_count'] += 1
    
    def end_query_profiling(
        self,
        session_id: str,
        rows_affected: int = 0,
        rows_examined: int = 0,
        bytes_sent: int = 0,
        bytes_received: int = 0,
        index_hits: int = 0,
        index_misses: int = 0,
        cache_hit: bool = False,
        lock_time: float = 0.0,
        sort_time: float = 0.0
    ) -> QueryExecutionMetrics:
        """
        End query profiling session and return metrics
        
        Args:
            session_id: Session identifier
            rows_affected: Number of rows affected by query
            rows_examined: Number of rows examined
            bytes_sent: Bytes sent over network
            bytes_received: Bytes received over network
            index_hits: Number of index hits
            index_misses: Number of index misses
            cache_hit: Whether query result was cached
            lock_time: Time spent waiting for locks
            sort_time: Time spent on sorting
        
        Returns:
            QueryExecutionMetrics: Complete query execution metrics
        """
        with self.session_lock:
            if session_id not in self.active_sessions:
                raise ValueError(f"Session {session_id} not found")
            
            session_data = self.active_sessions.pop(session_id)
        
        end_time = time.time()
        total_time = end_time - session_data['start_time']
        
        # Calculate connection time
        connection_time = 0.0
        if session_data['connection_start']:
            if session_data['execution_start']:
                connection_time = session_data['execution_start'] - session_data['connection_start']
            else:
                connection_time = end_time - session_data['connection_start']
        
        # Calculate execution time
        execution_time = total_time - connection_time
        
        # Generate optimization suggestions
        optimization_suggestions = self._generate_optimization_suggestions(
            session_data['query_metadata'], 
            execution_time, 
            rows_affected, 
            rows_examined, 
            index_hits, 
            index_misses
        )
        
        # Create metrics object
        metrics = QueryExecutionMetrics(
            query_metadata=session_data['query_metadata'],
            execution_time=execution_time,
            rows_affected=rows_affected,
            rows_examined=rows_examined,
            bytes_sent=bytes_sent,
            bytes_received=bytes_received,
            connection_time=connection_time,
            lock_time=lock_time,
            sort_time=sort_time,
            index_hits=index_hits,
            index_misses=index_misses,
            cache_hit=cache_hit,
            error_count=session_data['error_count'],
            warnings=session_data['warnings'],
            optimization_suggestions=optimization_suggestions
        )
        
        # Store metrics
        self.query_metrics.append(metrics)
        
        # Track slow queries
        if execution_time > self.slow_query_threshold:
            self.slow_queries.append(metrics)
        
        # Update query patterns
        query_hash = session_data['query_metadata'].query_hash
        self.query_patterns[query_hash].append(execution_time)
        
        # Update index usage statistics
        if self.enable_index_monitoring:
            for table_name in session_data['query_metadata'].table_names:
                self.index_usage_stats[table_name]['hits'] += index_hits
                self.index_usage_stats[table_name]['misses'] += index_misses
        
        # Update Prometheus metrics
        self.query_execution_time_histogram.labels(
            query_type=metrics.query_metadata.query_type.value,
            database_engine=metrics.query_metadata.database_engine.value,
            complexity=metrics.query_metadata.complexity.value
        ).observe(metrics.execution_time)
        
        self.query_throughput_gauge.labels(
            query_type=metrics.query_metadata.query_type.value,
            database_engine=metrics.query_metadata.database_engine.value
        ).set(metrics.rows_per_second)
        
        if execution_time > self.slow_query_threshold:
            self.slow_query_counter.labels(
                query_type=metrics.query_metadata.query_type.value,
                database_engine=metrics.query_metadata.database_engine.value
            ).inc()
        
        if metrics.error_count > 0:
            self.error_counter.labels(
                database_engine=metrics.query_metadata.database_engine.value,
                error_type='execution_error'
            ).inc(metrics.error_count)
        
        logger.info("Query profiling completed for %s: %.3fs, %d rows affected",
                   session_id, metrics.execution_time, metrics.rows_affected)
        
        return metrics
    
    def _generate_optimization_suggestions(
        self,
        query_metadata: QueryMetadata,
        execution_time: float,
        rows_affected: int,
        rows_examined: int,
        index_hits: int,
        index_misses: int
    ) -> List[str]:
        """Generate query optimization suggestions"""
        suggestions = []
        
        # Slow query suggestions
        if execution_time > self.slow_query_threshold:
            suggestions.append(f"Query execution time ({execution_time:.2f}s) exceeds threshold")
            
            if query_metadata.complexity == QueryComplexity.VERY_COMPLEX:
                suggestions.append("Consider breaking down complex query into simpler parts")
            
            if rows_examined > rows_affected * 10:
                suggestions.append("Query examines too many rows - consider adding indexes")
        
        # Index suggestions
        if index_misses > index_hits:
            suggestions.append("Low index hit ratio - review index strategy")
            for table in query_metadata.table_names:
                suggestions.append(f"Consider adding indexes on table '{table}'")
        
        # JOIN optimization
        if query_metadata.query_type == QueryType.JOIN and len(query_metadata.table_names) > 3:
            suggestions.append("Multiple table JOIN detected - ensure proper indexing on join columns")
        
        # Aggregate optimization
        if query_metadata.query_type == QueryType.AGGREGATE:
            suggestions.append("For aggregate queries, consider using covering indexes")
        
        return suggestions
    
    def _update_connection_pool_metrics(self):
        """Update connection pool metrics"""
        for pool_name, pool_info in self.connection_pools.items():
            if 'total_size' in pool_info:
                self.connection_pool_gauge.labels(
                    pool_name=pool_name,
                    metric_type='total_size'
                ).set(pool_info['total_size'])
            
            if 'active_connections' in pool_info:
                self.connection_pool_gauge.labels(
                    pool_name=pool_name,
                    metric_type='active_connections'
                ).set(pool_info['active_connections'])
    
    def _update_index_statistics(self):
        """Update index usage statistics"""
        for table_name, stats in self.index_usage_stats.items():
            total_accesses = stats['hits'] + stats['misses']
            if total_accesses > 0:
                efficiency = (stats['hits'] / total_accesses) * 100
                self.index_efficiency_gauge.labels(
                    database_engine='postgresql',  # Default
                    table_name=table_name
                ).set(efficiency)
    
    def _detect_bottlenecks(self):
        """Detect performance bottlenecks in database queries"""
        if len(self.query_metrics) < 5:
            return
        
        recent_metrics = list(self.query_metrics)[-50:]  # Last 50 queries
        
        # Analyze slow queries
        slow_queries = [m for m in recent_metrics if m.execution_time > self.slow_query_threshold]
        if len(slow_queries) > len(recent_metrics) * 0.2:  # More than 20% slow queries
            bottleneck = QueryBottleneck(
                bottleneck_type="high_slow_query_rate",
                severity="high",
                description=f"{len(slow_queries)} out of {len(recent_metrics)} queries are slow",
                affected_query_type=QueryType.SELECT,  # Most common
                database_engine=DatabaseEngine.POSTGRESQL,  # Default
                performance_impact=(len(slow_queries) / len(recent_metrics)) * 100,
                optimization_suggestions=[
                    "Review and optimize slow queries",
                    "Add missing indexes",
                    "Update query statistics",
                    "Consider query rewriting"
                ],
                index_recommendations=[
                    "Analyze query execution plans",
                    "Add indexes on frequently used columns",
                    "Consider composite indexes for multi-column conditions",
                    "Remove unused indexes to improve write performance"
                ],
                schema_recommendations=[
                    "Normalize database schema appropriately",
                    "Consider partitioning large tables",
                    "Review table relationships",
                    "Optimize data types"
                ]
            )
            self._record_bottleneck(bottleneck)
        
        # Analyze index efficiency
        if self.enable_index_monitoring:
            for table_name, stats in self.index_usage_stats.items():
                total_accesses = stats['hits'] + stats['misses']
                if total_accesses > 100:  # Sufficient data
                    efficiency = (stats['hits'] / total_accesses) * 100
                    if efficiency < 50:  # Less than 50% index hit rate
                        bottleneck = QueryBottleneck(
                            bottleneck_type="low_index_efficiency",
                            severity="medium",
                            description=f"Table '{table_name}' has {efficiency:.1f}% index efficiency",
                            affected_query_type=QueryType.SELECT,
                            database_engine=DatabaseEngine.POSTGRESQL,
                            performance_impact=100 - efficiency,
                            optimization_suggestions=[
                                f"Improve indexing strategy for table '{table_name}'",
                                "Analyze query patterns",
                                "Consider covering indexes",
                                "Update table statistics"
                            ],
                            index_recommendations=[
                                f"Add selective indexes on table '{table_name}'",
                                "Remove redundant or unused indexes",
                                "Consider partial indexes for filtered queries",
                                "Optimize index order for multi-column indexes"
                            ],
                            schema_recommendations=[
                                "Review table design",
                                "Consider denormalization for read-heavy workloads",
                                "Optimize column order",
                                "Consider table partitioning"
                            ]
                        )
                        self._record_bottleneck(bottleneck)
        
        # Analyze connection pool utilization
        if self.enable_connection_pool_monitoring:
            for pool_name, pool_info in self.connection_pools.items():
                if 'active_connections' in pool_info and 'total_size' in pool_info:
                    utilization = (pool_info['active_connections'] / pool_info['total_size']) * 100
                    
                    if utilization > 90:  # High connection pool utilization
                        bottleneck = QueryBottleneck(
                            bottleneck_type="high_connection_pool_utilization",
                            severity="high",
                            description=f"Connection pool '{pool_name}' is {utilization:.1f}% utilized",
                            affected_query_type=QueryType.SELECT,
                            database_engine=DatabaseEngine.POSTGRESQL,
                            performance_impact=utilization - 70,
                            optimization_suggestions=[
                                "Increase connection pool size",
                                "Optimize query execution time",
                                "Implement connection pooling best practices",
                                "Monitor for connection leaks"
                            ],
                            index_recommendations=[
                                "Optimize queries to reduce execution time",
                                "Add indexes to speed up queries",
                                "Consider read replicas for read queries"
                            ],
                            schema_recommendations=[
                                "Consider database sharding",
                                "Implement read/write splitting",
                                "Optimize application architecture"
                            ]
                        )
                        self._record_bottleneck(bottleneck)
    
    def _record_bottleneck(self, bottleneck: QueryBottleneck):
        """Record a detected bottleneck"""
        self.bottlenecks.append(bottleneck)
        
        # Update Prometheus counter
        self.bottleneck_counter.labels(
            bottleneck_type=bottleneck.bottleneck_type,
            severity=bottleneck.severity
        ).inc()
        
        logger.warning("Database bottleneck detected: %s (%s severity)",
                      bottleneck.description, bottleneck.severity)
    
    def update_connection_pool_info(self, pool_name: str, total_size: int, active_connections: int):
        """Update connection pool information"""
        self.connection_pools[pool_name] = {
            'total_size': total_size,
            'active_connections': active_connections,
            'timestamp': datetime.now()
        }
    
    def get_slow_query_analysis(self, time_window: timedelta = timedelta(hours=1)) -> Dict[str, Any]:
        """
        Get analysis of slow queries
        
        Args:
            time_window: Time window for analysis
        
        Returns:
            Slow query analysis results
        """
        cutoff_time = datetime.now() - time_window
        
        # Filter recent slow queries
        recent_slow_queries = [
            q for q in self.slow_queries
            if q.timestamp >= cutoff_time
        ]
        
        if not recent_slow_queries:
            return {'error': 'No slow queries in time window'}
        
        # Analyze by query type
        query_type_analysis = defaultdict(list)
        for query in recent_slow_queries:
            query_type_analysis[query.query_metadata.query_type.value].append(query.execution_time)
        
        # Analyze by table
        table_analysis = defaultdict(list)
        for query in recent_slow_queries:
            for table in query.query_metadata.table_names:
                table_analysis[table].append(query.execution_time)
        
        return {
            'time_window': str(time_window),
            'total_slow_queries': len(recent_slow_queries),
            'avg_execution_time': statistics.mean([q.execution_time for q in recent_slow_queries]),
            'by_query_type': {
                qtype: {
                    'count': len(times),
                    'avg_time': statistics.mean(times),
                    'max_time': max(times)
                }
                for qtype, times in query_type_analysis.items()
            },
            'by_table': {
                table: {
                    'count': len(times),
                    'avg_time': statistics.mean(times),
                    'max_time': max(times)
                }
                for table, times in table_analysis.items()
            },
            'most_problematic_queries': [
                {
                    'query_hash': q.query_metadata.query_hash,
                    'execution_time': q.execution_time,
                    'query_type': q.query_metadata.query_type.value,
                    'tables': q.query_metadata.table_names
                }
                for q in sorted(recent_slow_queries, key=lambda x: x.execution_time, reverse=True)[:10]
            ]
        }
    
    def get_optimization_recommendations(
        self,
        database_engine: Optional[DatabaseEngine] = None,
        time_window: timedelta = timedelta(hours=1)
    ) -> List[Dict[str, Any]]:
        """
        Get database optimization recommendations
        
        Args:
            database_engine: Specific database engine to analyze
            time_window: Time window for analysis
        
        Returns:
            List of optimization recommendations
        """
        cutoff_time = datetime.now() - time_window
        
        # Filter recent metrics
        recent_metrics = [
            m for m in self.query_metrics
            if (m.timestamp >= cutoff_time and
                (database_engine is None or m.query_metadata.database_engine == database_engine))
        ]
        
        if not recent_metrics:
            return []
        
        recommendations = []
        
        # Analyze execution times
        execution_times = [m.execution_time for m in recent_metrics]
        avg_execution_time = statistics.mean(execution_times)
        
        if avg_execution_time > 0.5:  # Average over 500ms
            recommendations.append({
                'type': 'query_optimization',
                'priority': 'high',
                'description': f'Average query execution time is {avg_execution_time:.2f}s',
                'suggestions': [
                    'Review and optimize slow queries',
                    'Add appropriate indexes',
                    'Update database statistics',
                    'Consider query rewriting'
                ],
                'expected_improvement': 'Up to 70% query performance improvement'
            })
        
        # Analyze index efficiency
        index_metrics = [m for m in recent_metrics if m.index_hits + m.index_misses > 0]
        if index_metrics:
            avg_index_efficiency = statistics.mean([m.cache_efficiency for m in index_metrics])
            
            if avg_index_efficiency < 70:
                recommendations.append({
                    'type': 'index_optimization',
                    'priority': 'medium',
                    'description': f'Index efficiency is {avg_index_efficiency:.1f}%',
                    'suggestions': [
                        'Analyze query patterns for index opportunities',
                        'Add covering indexes for frequent queries',
                        'Remove unused indexes',
                        'Optimize existing index order'
                    ],
                    'expected_improvement': f'{(70 - avg_index_efficiency):.0f}% index efficiency improvement'
                })
        
        # Analyze cache hit rates
        cache_hits = len([m for m in recent_metrics if m.cache_hit])
        cache_hit_rate = cache_hits / len(recent_metrics)
        
        if cache_hit_rate < 0.3:
            recommendations.append({
                'type': 'cache_optimization',
                'priority': 'medium',
                'description': f'Query cache hit rate is {cache_hit_rate:.1%}',
                'suggestions': [
                    'Implement query result caching',
                    'Optimize cache eviction policies',
                    'Increase cache size if appropriate',
                    'Cache frequently accessed data'
                ],
                'expected_improvement': f'{((0.5 - cache_hit_rate) * 100):.0f}% cache efficiency improvement'
            })
        
        return recommendations
    
    def get_performance_summary(
        self,
        database_engine: Optional[DatabaseEngine] = None,
        time_window: timedelta = timedelta(hours=1)
    ) -> Dict[str, Any]:
        """
        Get performance summary for database queries
        
        Args:
            database_engine: Specific database engine to analyze
            time_window: Time window for analysis
        
        Returns:
            Performance summary dictionary
        """
        cutoff_time = datetime.now() - time_window
        
        # Filter recent metrics
        recent_metrics = [
            m for m in self.query_metrics
            if (m.timestamp >= cutoff_time and
                (database_engine is None or m.query_metadata.database_engine == database_engine))
        ]
        
        if not recent_metrics:
            return {'error': 'No metrics available'}
        
        # Calculate statistics
        execution_times = [m.execution_time for m in recent_metrics]
        throughputs = [m.rows_per_second for m in recent_metrics if m.rows_per_second > 0]
        
        summary = {
            'time_window': str(time_window),
            'total_queries': len(recent_metrics),
            'database_engines': len(set(m.query_metadata.database_engine for m in recent_metrics)),
            'query_types': len(set(m.query_metadata.query_type for m in recent_metrics)),
            'performance_metrics': {
                'avg_execution_time': statistics.mean(execution_times),
                'p95_execution_time': statistics.quantiles(execution_times, n=20)[18] if len(execution_times) >= 20 else max(execution_times),
                'slow_query_count': len([m for m in recent_metrics if m.execution_time > self.slow_query_threshold]),
                'total_errors': sum(m.error_count for m in recent_metrics),
                'cache_hit_rate': (len([m for m in recent_metrics if m.cache_hit]) / len(recent_metrics)) * 100
            }
        }
        
        if throughputs:
            summary['performance_metrics'].update({
                'avg_throughput': statistics.mean(throughputs),
                'max_throughput': max(throughputs)
            })
        
        # Query type distribution
        query_type_dist = defaultdict(int)
        for metric in recent_metrics:
            query_type_dist[metric.query_metadata.query_type.value] += 1
        summary['query_type_distribution'] = dict(query_type_dist)
        
        # Connection pool status
        if self.enable_connection_pool_monitoring:
            summary['connection_pools'] = {
                pool_name: {
                    'total_size': info['total_size'],
                    'active_connections': info['active_connections'],
                    'utilization': (info['active_connections'] / info['total_size']) * 100
                }
                for pool_name, info in self.connection_pools.items()
            }
        
        # Recent bottlenecks
        recent_bottlenecks = [b for b in self.bottlenecks if b.timestamp >= cutoff_time]
        summary['bottlenecks'] = {
            'total_count': len(recent_bottlenecks),
            'by_severity': {
                severity: len([b for b in recent_bottlenecks if b.severity == severity])
                for severity in ['low', 'medium', 'high', 'critical']
            }
        }
        
        return summary


# Context manager for easy profiling
class QueryProfiler:
    """Context manager for database query profiling"""
    
    def __init__(
        self,
        profiler: DatabaseQueryProfiler,
        query_text: str,
        database_engine: DatabaseEngine,
        parameters: Optional[Dict[str, Any]] = None,
        connection_pool_name: Optional[str] = None
    ):
        self.profiler = profiler
        self.query_text = query_text
        self.database_engine = database_engine
        self.parameters = parameters
        self.connection_pool_name = connection_pool_name
        self.session_id: Optional[str] = None
    
    def __enter__(self):
        self.session_id = self.profiler.start_query_profiling(
            query_text=self.query_text,
            database_engine=self.database_engine,
            parameters=self.parameters,
            connection_pool_name=self.connection_pool_name
        )
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        return None  # Session must be ended explicitly
    
    def mark_connection_start(self):
        if self.session_id:
            self.profiler.mark_connection_start(self.session_id)
    
    def mark_execution_start(self):
        if self.session_id:
            self.profiler.mark_execution_start(self.session_id)
    
    def end_profiling(self, **kwargs) -> QueryExecutionMetrics:
        if self.session_id:
            return self.profiler.end_query_profiling(self.session_id, **kwargs)
        raise ValueError("Session not started")


# Factory function for creating profiler instances
def create_database_query_profiler(
    enable_query_plan_analysis: bool = True,
    enable_index_monitoring: bool = True,
    enable_connection_pool_monitoring: bool = True,
    start_monitoring: bool = True
) -> DatabaseQueryProfiler:
    """
    Factory function to create and configure Database Query Profiler
    
    Args:
        enable_query_plan_analysis: Enable query plan analysis
        enable_index_monitoring: Enable index monitoring
        enable_connection_pool_monitoring: Enable connection pool monitoring
        start_monitoring: Start background monitoring immediately
    
    Returns:
        Configured DatabaseQueryProfiler instance
    """
    profiler = DatabaseQueryProfiler(
        enable_query_plan_analysis=enable_query_plan_analysis,
        enable_index_monitoring=enable_index_monitoring,
        enable_connection_pool_monitoring=enable_connection_pool_monitoring
    )
    
    if start_monitoring:
        profiler.start_monitoring()
    
    return profiler


if __name__ == "__main__":
    # Example usage
    
    # Create profiler
    profiler = create_database_query_profiler()
    
    # Example: Profile a complex SELECT query
    query = """
    SELECT u.id, u.name, c.title, COUNT(l.id) as like_count
    FROM users u
    JOIN content c ON u.id = c.creator_id
    LEFT JOIN likes l ON c.id = l.content_id
    WHERE u.created_at > '2024-01-01'
    GROUP BY u.id, u.name, c.title
    ORDER BY like_count DESC
    LIMIT 10
    """
    
    with QueryProfiler(
        profiler=profiler,
        query_text=query,
        database_engine=DatabaseEngine.POSTGRESQL,
        parameters={'min_date': '2024-01-01'},
        connection_pool_name='main_pool'
    ) as session:
        
        # Simulate query execution
        session.mark_connection_start()
        time.sleep(0.01)  # Simulate connection time
        
        session.mark_execution_start()
        time.sleep(0.15)  # Simulate query execution
        
        # End profiling with results
        metrics = session.end_profiling(
            rows_affected=10,
            rows_examined=5000,
            bytes_sent=1024,
            bytes_received=2048,
            index_hits=4500,
            index_misses=500,
            cache_hit=False
        )
    
    # Update connection pool info
    profiler.update_connection_pool_info('main_pool', total_size=20, active_connections=12)
    
    # Get slow query analysis
    slow_query_analysis = profiler.get_slow_query_analysis()
    print("Slow Query Analysis:", json.dumps(slow_query_analysis, indent=2, default=str))
    
    # Get performance summary
    summary = profiler.get_performance_summary()
    print("Performance Summary:", json.dumps(summary, indent=2, default=str))
    
    # Get optimization recommendations
    recommendations = profiler.get_optimization_recommendations()
    print("Optimization Recommendations:", json.dumps(recommendations, indent=2))
    
    # Stop monitoring
    profiler.stop_monitoring()