"""
⚠️ CONFIDENTIEL - Ainflue Creator Platform ⚠️

Database Performance Analyzer - Enterprise Performance Monitoring
Advanced database performance analysis for Creator Economy data layer

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

🚨 PROTECTION INTELLECTUELLE:
- Code propriétaire de Fahed Mlaiel
- Utilisation commerciale INTERDITE sans autorisation écrite
- Reverse engineering STRICTEMENT INTERDIT
- Distribution INTERDITE sans licence explicite
- Violation = Poursuites judiciaires automatiques
"""

import time
import asyncio
import asyncpg
import redis
import pymongo
from sqlalchemy import create_engine, text
from sqlalchemy.pool import QueuePool
import psycopg2
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
import logging
from collections import defaultdict, deque
import json
import statistics
from prometheus_client import Gauge, Counter, Histogram
# Safe Redis import with Python 3.12 compatibility
try:
    import aioredis
    REDIS_AVAILABLE = True
except (ImportError, TypeError) as e:
    # Handle Python 3.12 TimeoutError duplicate base class issue
    from protection.utils.redis_compat import MockRedis as aioredis, REDIS_AVAILABLE
    import logging
    logging.warning(f"Using Redis compatibility layer: {e}")
from motor.motor_asyncio import AsyncIOMotorClient

logger = logging.getLogger(__name__)

@dataclass
class QueryPerformanceMetrics:
    """Query performance metrics"""
    query_id: str
    query_text: str
    database_name: str
    execution_time_ms: float
    rows_examined: int
    rows_returned: int
    bytes_sent: int
    lock_time_ms: float
    timestamp: datetime
    user: Optional[str] = None
    table_name: Optional[str] = None
    query_type: Optional[str] = None  # SELECT, INSERT, UPDATE, DELETE
    index_used: Optional[bool] = None
    full_scan: Optional[bool] = None

@dataclass
class DatabaseConnectionMetrics:
    """Database connection pool metrics"""
    database_name: str
    database_type: str  # postgresql, redis, mongodb
    active_connections: int
    idle_connections: int
    total_connections: int
    max_connections: int
    connection_pool_usage: float
    avg_connection_time_ms: float
    failed_connections: int
    timestamp: datetime

@dataclass
class DatabaseResourceMetrics:
    """Database resource utilization metrics"""
    database_name: str
    database_type: str
    cpu_usage_percent: float
    memory_usage_mb: int
    disk_usage_gb: float
    disk_io_read_mb: float
    disk_io_write_mb: float
    network_io_mb: float
    cache_hit_ratio: float
    buffer_pool_usage: float
    timestamp: datetime

@dataclass
class SlowQueryAlert:
    """Slow query alert"""
    query_id: str
    query_text: str
    execution_time_ms: float
    threshold_ms: float
    database_name: str
    table_name: Optional[str]
    recommendation: str
    timestamp: datetime

class DatabasePerformanceAnalyzer:
    """
    Enterprise-grade database performance analyzer
    Monitors PostgreSQL, Redis, MongoDB performance and query optimization
    """
    
    def __init__(self,
                 postgresql_dsn: Optional[str] = None,
                 redis_url: Optional[str] = None,
                 mongodb_url: Optional[str] = None,
                 slow_query_threshold_ms: float = 1000,
                 collection_interval: int = 30):
        """
        Initialize database performance analyzer
        
        Args:
            postgresql_dsn: PostgreSQL connection string
            redis_url: Redis connection URL
            mongodb_url: MongoDB connection URL
            slow_query_threshold_ms: Slow query threshold in milliseconds
            collection_interval: Metrics collection interval in seconds
        """
        self.postgresql_dsn = postgresql_dsn
        self.redis_url = redis_url
        self.mongodb_url = mongodb_url
        self.slow_query_threshold_ms = slow_query_threshold_ms
        self.collection_interval = collection_interval
        
        # Database connections
        self.pg_engine = None
        self.redis_client = None
        self.mongo_client = None
        
        # Async database connections
        self.pg_pool = None
        self.redis_async = None
        self.mongo_async = None
        
        # Metrics storage
        self.query_metrics: deque = deque(maxlen=10000)
        self.connection_metrics: Dict[str, deque] = defaultdict(lambda: deque(maxlen=1000))
        self.resource_metrics: Dict[str, deque] = defaultdict(lambda: deque(maxlen=1000))
        self.slow_queries: deque = deque(maxlen=1000)
        
        # Query patterns cache
        self.query_patterns: Dict[str, Dict] = {}
        self.query_fingerprints: Dict[str, List] = defaultdict(list)
        
        # Prometheus metrics
        self._init_prometheus_metrics()
        
        # Monitoring state
        self.monitoring_active = False
        self._monitoring_task = None
    
    def _init_prometheus_metrics(self):
        """Initialize Prometheus metrics"""
        self.query_duration_histogram = Histogram(
            'database_query_duration_seconds',
            'Database query execution time',
            ['database', 'query_type', 'table'],
            buckets=[0.01, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0]
        )
        
        self.connection_pool_gauge = Gauge(
            'database_connection_pool_usage',
            'Database connection pool usage',
            ['database', 'pool_type']
        )
        
        self.slow_query_counter = Counter(
            'database_slow_queries_total',
            'Total number of slow queries',
            ['database', 'table']
        )
        
        self.cache_hit_ratio_gauge = Gauge(
            'database_cache_hit_ratio',
            'Database cache hit ratio',
            ['database']
        )
        
        self.database_size_gauge = Gauge(
            'database_size_bytes',
            'Database size in bytes',
            ['database', 'database_type']
        )
    
    async def initialize_connections(self):
        """Initialize database connections"""
        try:
            # PostgreSQL
            if self.postgresql_dsn:
                self.pg_engine = create_engine(
                    self.postgresql_dsn,
                    poolclass=QueuePool,
                    pool_size=10,
                    max_overflow=20,
                    pool_pre_ping=True
                )
                self.pg_pool = await asyncpg.create_pool(
                    self.postgresql_dsn,
                    min_size=5,
                    max_size=20
                )
                logger.info("PostgreSQL connection initialized")
            
            # Redis
            if self.redis_url:
                self.redis_client = redis.from_url(self.redis_url)
                self.redis_async = await aioredis.from_url(self.redis_url)
                logger.info("Redis connection initialized")
            
            # MongoDB
            if self.mongodb_url:
                self.mongo_client = pymongo.MongoClient(self.mongodb_url)
                self.mongo_async = AsyncIOMotorClient(self.mongodb_url)
                logger.info("MongoDB connection initialized")
                
        except Exception as e:
            logger.error(f"Error initializing database connections: {e}")
            raise
    
    async def collect_postgresql_metrics(self) -> List[QueryPerformanceMetrics]:
        """Collect PostgreSQL performance metrics"""
        if not self.pg_pool:
            return []
        
        metrics = []
        
        try:
            async with self.pg_pool.acquire() as conn:
                # Get slow queries from pg_stat_statements
                slow_queries = await conn.fetch("""
                    SELECT 
                        queryid,
                        query,
                        calls,
                        mean_exec_time,
                        max_exec_time,
                        total_exec_time,
                        rows,
                        shared_blks_hit,
                        shared_blks_read,
                        shared_blks_written,
                        temp_blks_read,
                        temp_blks_written
                    FROM pg_stat_statements 
                    WHERE mean_exec_time > $1
                    ORDER BY mean_exec_time DESC 
                    LIMIT 100
                """, self.slow_query_threshold_ms)
                
                for row in slow_queries:
                    query_metrics = QueryPerformanceMetrics(
                        query_id=str(row['queryid']),
                        query_text=row['query'][:500],  # Truncate long queries
                        database_name='postgresql',
                        execution_time_ms=row['mean_exec_time'],
                        rows_examined=row['shared_blks_read'] + row['shared_blks_hit'],
                        rows_returned=row['rows'],
                        bytes_sent=0,  # Not available in pg_stat_statements
                        lock_time_ms=0,  # Not available in pg_stat_statements
                        timestamp=datetime.utcnow(),
                        query_type=self._extract_query_type(row['query'])
                    )
                    
                    metrics.append(query_metrics)
                    
                    # Update Prometheus metrics
                    self.query_duration_histogram.labels(
                        database='postgresql',
                        query_type=query_metrics.query_type or 'unknown',
                        table='unknown'
                    ).observe(row['mean_exec_time'] / 1000)
                    
                    if row['mean_exec_time'] > self.slow_query_threshold_ms:
                        self.slow_query_counter.labels(
                            database='postgresql',
                            table='unknown'
                        ).inc()
                
                # Get connection metrics
                connection_stats = await conn.fetchrow("""
                    SELECT 
                        count(*) as total_connections,
                        count(*) FILTER (WHERE state = 'active') as active_connections,
                        count(*) FILTER (WHERE state = 'idle') as idle_connections
                    FROM pg_stat_activity
                """)
                
                # Get database size
                db_size = await conn.fetchrow("""
                    SELECT pg_database_size(current_database()) as size
                """)
                
                # Get cache hit ratio
                cache_stats = await conn.fetchrow("""
                    SELECT 
                        sum(blks_hit) as hits,
                        sum(blks_read) as reads
                    FROM pg_stat_database
                    WHERE datname = current_database()
                """)
                
                cache_hit_ratio = 0.0
                if cache_stats['hits'] and cache_stats['reads']:
                    total = cache_stats['hits'] + cache_stats['reads']
                    cache_hit_ratio = cache_stats['hits'] / total * 100
                
                # Store connection metrics
                conn_metrics = DatabaseConnectionMetrics(
                    database_name='postgresql',
                    database_type='postgresql',
                    active_connections=connection_stats['active_connections'],
                    idle_connections=connection_stats['idle_connections'],
                    total_connections=connection_stats['total_connections'],
                    max_connections=100,  # Default, should be configurable
                    connection_pool_usage=connection_stats['total_connections'] / 100 * 100,
                    avg_connection_time_ms=0,  # Not easily available
                    failed_connections=0,  # Not easily available
                    timestamp=datetime.utcnow()
                )
                
                self.connection_metrics['postgresql'].append(conn_metrics)
                
                # Update Prometheus metrics
                self.connection_pool_gauge.labels(
                    database='postgresql',
                    pool_type='active'
                ).set(connection_stats['active_connections'])
                
                self.connection_pool_gauge.labels(
                    database='postgresql',
                    pool_type='idle'
                ).set(connection_stats['idle_connections'])
                
                self.cache_hit_ratio_gauge.labels(database='postgresql').set(cache_hit_ratio)
                self.database_size_gauge.labels(
                    database='postgresql',
                    database_type='postgresql'
                ).set(db_size['size'])
                
        except Exception as e:
            logger.error(f"Error collecting PostgreSQL metrics: {e}")
        
        return metrics
    
    async def collect_redis_metrics(self) -> List[DatabaseResourceMetrics]:
        """Collect Redis performance metrics"""
        if not self.redis_async:
            return []
        
        metrics = []
        
        try:
            # Get Redis info
            info = await self.redis_async.info()
            
            # Extract relevant metrics
            memory_usage = info.get('used_memory', 0) / (1024 * 1024)  # MB
            hit_ratio = 0.0
            
            if info.get('keyspace_hits', 0) > 0 or info.get('keyspace_misses', 0) > 0:
                hits = info.get('keyspace_hits', 0)
                misses = info.get('keyspace_misses', 0)
                hit_ratio = hits / (hits + misses) * 100
            
            resource_metrics = DatabaseResourceMetrics(
                database_name='redis',
                database_type='redis',
                cpu_usage_percent=info.get('used_cpu_sys', 0) + info.get('used_cpu_user', 0),
                memory_usage_mb=memory_usage,
                disk_usage_gb=0,  # Redis is in-memory
                disk_io_read_mb=0,
                disk_io_write_mb=0,
                network_io_mb=info.get('total_net_input_bytes', 0) / (1024 * 1024),
                cache_hit_ratio=hit_ratio,
                buffer_pool_usage=0,  # Not applicable to Redis
                timestamp=datetime.utcnow()
            )
            
            metrics.append(resource_metrics)
            self.resource_metrics['redis'].append(resource_metrics)
            
            # Connection metrics
            connected_clients = info.get('connected_clients', 0)
            
            conn_metrics = DatabaseConnectionMetrics(
                database_name='redis',
                database_type='redis',
                active_connections=connected_clients,
                idle_connections=0,  # Redis doesn't distinguish
                total_connections=connected_clients,
                max_connections=info.get('maxclients', 10000),
                connection_pool_usage=connected_clients / info.get('maxclients', 10000) * 100,
                avg_connection_time_ms=0,
                failed_connections=info.get('rejected_connections', 0),
                timestamp=datetime.utcnow()
            )
            
            self.connection_metrics['redis'].append(conn_metrics)
            
            # Update Prometheus metrics
            self.cache_hit_ratio_gauge.labels(database='redis').set(hit_ratio)
            self.connection_pool_gauge.labels(
                database='redis',
                pool_type='active'
            ).set(connected_clients)
            
        except Exception as e:
            logger.error(f"Error collecting Redis metrics: {e}")
        
        return metrics
    
    async def collect_mongodb_metrics(self) -> List[DatabaseResourceMetrics]:
        """Collect MongoDB performance metrics"""
        if not self.mongo_async:
            return []
        
        metrics = []
        
        try:
            db = self.mongo_async.admin
            
            # Get server status
            server_status = await db.command("serverStatus")
            
            # Extract metrics
            connections = server_status.get('connections', {})
            memory = server_status.get('mem', {})
            opcounters = server_status.get('opcounters', {})
            
            resource_metrics = DatabaseResourceMetrics(
                database_name='mongodb',
                database_type='mongodb',
                cpu_usage_percent=0,  # Not directly available
                memory_usage_mb=memory.get('resident', 0),
                disk_usage_gb=0,  # Requires additional query
                disk_io_read_mb=0,
                disk_io_write_mb=0,
                network_io_mb=server_status.get('network', {}).get('bytesIn', 0) / (1024 * 1024),
                cache_hit_ratio=0,  # Requires WiredTiger specific metrics
                buffer_pool_usage=0,
                timestamp=datetime.utcnow()
            )
            
            metrics.append(resource_metrics)
            self.resource_metrics['mongodb'].append(resource_metrics)
            
            # Connection metrics
            conn_metrics = DatabaseConnectionMetrics(
                database_name='mongodb',
                database_type='mongodb',
                active_connections=connections.get('current', 0),
                idle_connections=0,
                total_connections=connections.get('current', 0),
                max_connections=connections.get('available', 1000),
                connection_pool_usage=connections.get('current', 0) / connections.get('available', 1000) * 100,
                avg_connection_time_ms=0,
                failed_connections=0,
                timestamp=datetime.utcnow()
            )
            
            self.connection_metrics['mongodb'].append(conn_metrics)
            
            # Update Prometheus metrics
            self.connection_pool_gauge.labels(
                database='mongodb',
                pool_type='active'
            ).set(connections.get('current', 0))
            
        except Exception as e:
            logger.error(f"Error collecting MongoDB metrics: {e}")
        
        return metrics
    
    def _extract_query_type(self, query: str) -> str:
        """Extract query type from SQL"""
        if not query:
            return 'unknown'
        
        query_lower = query.strip().lower()
        if query_lower.startswith('select'):
            return 'select'
        elif query_lower.startswith('insert'):
            return 'insert'
        elif query_lower.startswith('update'):
            return 'update'
        elif query_lower.startswith('delete'):
            return 'delete'
        elif query_lower.startswith('create'):
            return 'create'
        elif query_lower.startswith('drop'):
            return 'drop'
        elif query_lower.startswith('alter'):
            return 'alter'
        else:
            return 'other'
    
    def _generate_query_fingerprint(self, query: str) -> str:
        """Generate query fingerprint for pattern analysis"""
        import re
        
        # Normalize query for pattern matching
        normalized = re.sub(r'\b\d+\b', '?', query)  # Replace numbers with ?
        normalized = re.sub(r"'[^']*'", "'?'", normalized)  # Replace string literals
        normalized = re.sub(r'\s+', ' ', normalized)  # Normalize whitespace
        
        return normalized.strip().lower()
    
    async def analyze_query_patterns(self) -> Dict[str, Any]:
        """Analyze query patterns and identify optimization opportunities"""
        if not self.query_metrics:
            return {}
        
        patterns = defaultdict(list)
        
        # Group queries by fingerprint
        for metric in self.query_metrics:
            fingerprint = self._generate_query_fingerprint(metric.query_text)
            patterns[fingerprint].append(metric)
        
        analysis = {
            'total_unique_patterns': len(patterns),
            'most_frequent_patterns': [],
            'slowest_patterns': [],
            'optimization_recommendations': []
        }
        
        # Analyze patterns
        pattern_stats = []
        for fingerprint, queries in patterns.items():
            avg_time = sum(q.execution_time_ms for q in queries) / len(queries)
            max_time = max(q.execution_time_ms for q in queries)
            
            pattern_stats.append({
                'fingerprint': fingerprint,
                'query_count': len(queries),
                'avg_execution_time_ms': avg_time,
                'max_execution_time_ms': max_time,
                'sample_query': queries[0].query_text[:200]
            })
        
        # Most frequent patterns
        analysis['most_frequent_patterns'] = sorted(
            pattern_stats,
            key=lambda x: x['query_count'],
            reverse=True
        )[:10]
        
        # Slowest patterns
        analysis['slowest_patterns'] = sorted(
            pattern_stats,
            key=lambda x: x['avg_execution_time_ms'],
            reverse=True
        )[:10]
        
        # Generate recommendations
        for pattern in analysis['slowest_patterns'][:5]:
            if pattern['avg_execution_time_ms'] > self.slow_query_threshold_ms:
                recommendations = self._generate_optimization_recommendations(pattern)
                analysis['optimization_recommendations'].extend(recommendations)
        
        return analysis
    
    def _generate_optimization_recommendations(self, pattern: Dict) -> List[Dict[str, Any]]:
        """Generate optimization recommendations for slow query patterns"""
        recommendations = []
        query = pattern['sample_query'].lower()
        
        # Check for missing WHERE clause
        if 'select' in query and 'where' not in query and 'limit' not in query:
            recommendations.append({
                'type': 'missing_where_clause',
                'priority': 'high',
                'description': 'Query lacks WHERE clause, may scan entire table',
                'suggestion': 'Add appropriate WHERE clause to limit rows scanned'
            })
        
        # Check for potential N+1 queries
        if pattern['query_count'] > 100 and pattern['avg_execution_time_ms'] > 50:
            recommendations.append({
                'type': 'n_plus_one_query',
                'priority': 'high',
                'description': 'High frequency query with moderate execution time',
                'suggestion': 'Consider query optimization or caching'
            })
        
        # Check for missing ORDER BY with LIMIT
        if 'limit' in query and 'order by' not in query:
            recommendations.append({
                'type': 'limit_without_order',
                'priority': 'medium',
                'description': 'LIMIT clause without ORDER BY may return inconsistent results',
                'suggestion': 'Add ORDER BY clause for deterministic results'
            })
        
        # Check for potential index opportunities
        if 'where' in query and pattern['avg_execution_time_ms'] > 100:
            recommendations.append({
                'type': 'potential_index',
                'priority': 'medium',
                'description': 'Slow query with WHERE clause may benefit from index',
                'suggestion': 'Analyze WHERE conditions for index optimization'
            })
        
        return recommendations
    
    async def get_slow_query_analysis(self, hours: int = 24) -> Dict[str, Any]:
        """Get slow query analysis for the specified time period"""
        cutoff_time = datetime.utcnow() - timedelta(hours=hours)
        slow_queries = [
            q for q in self.query_metrics 
            if q.timestamp >= cutoff_time and q.execution_time_ms > self.slow_query_threshold_ms
        ]
        
        if not slow_queries:
            return {'message': 'No slow queries found in the specified time period'}
        
        # Group by database
        by_database = defaultdict(list)
        for query in slow_queries:
            by_database[query.database_name].append(query)
        
        analysis = {
            'time_period_hours': hours,
            'total_slow_queries': len(slow_queries),
            'slow_query_threshold_ms': self.slow_query_threshold_ms,
            'by_database': {}
        }
        
        for db_name, queries in by_database.items():
            execution_times = [q.execution_time_ms for q in queries]
            
            analysis['by_database'][db_name] = {
                'query_count': len(queries),
                'avg_execution_time_ms': statistics.mean(execution_times),
                'median_execution_time_ms': statistics.median(execution_times),
                'max_execution_time_ms': max(execution_times),
                'min_execution_time_ms': min(execution_times),
                'top_slow_queries': [
                    {
                        'query_text': q.query_text[:200],
                        'execution_time_ms': q.execution_time_ms,
                        'timestamp': q.timestamp.isoformat()
                    }
                    for q in sorted(queries, key=lambda x: x.execution_time_ms, reverse=True)[:5]
                ]
            }
        
        return analysis
    
    async def get_connection_pool_status(self) -> Dict[str, Any]:
        """Get connection pool status for all databases"""
        status = {}
        
        for db_name, metrics_list in self.connection_metrics.items():
            if not metrics_list:
                continue
            
            latest = metrics_list[-1]
            recent_metrics = [m for m in metrics_list if m.timestamp >= datetime.utcnow() - timedelta(minutes=5)]
            
            if recent_metrics:
                avg_usage = sum(m.connection_pool_usage for m in recent_metrics) / len(recent_metrics)
            else:
                avg_usage = latest.connection_pool_usage
            
            status[db_name] = {
                'database_type': latest.database_type,
                'current_connections': latest.total_connections,
                'max_connections': latest.max_connections,
                'usage_percent': latest.connection_pool_usage,
                'avg_usage_5min': avg_usage,
                'failed_connections': latest.failed_connections,
                'status': 'healthy' if latest.connection_pool_usage < 80 else 'warning' if latest.connection_pool_usage < 95 else 'critical'
            }
        
        return status
    
    async def start_monitoring(self):
        """Start continuous database monitoring"""
        if self.monitoring_active:
            logger.warning("Database monitoring already active")
            return
        
        await self.initialize_connections()
        self.monitoring_active = True
        self._monitoring_task = asyncio.create_task(self._monitoring_loop())
        logger.info("Database performance monitoring started")
    
    async def stop_monitoring(self):
        """Stop monitoring"""
        self.monitoring_active = False
        if self._monitoring_task:
            self._monitoring_task.cancel()
            try:
                await self._monitoring_task
            except asyncio.CancelledError:
                pass
        
        # Close connections
        if self.pg_pool:
            await self.pg_pool.close()
        if self.redis_async:
            await self.redis_async.close()
        if self.mongo_async:
            self.mongo_async.close()
        
        logger.info("Database performance monitoring stopped")
    
    async def _monitoring_loop(self):
        """Main monitoring loop"""
        while self.monitoring_active:
            try:
                # Collect metrics from all databases
                if self.postgresql_dsn:
                    pg_metrics = await self.collect_postgresql_metrics()
                    self.query_metrics.extend(pg_metrics)
                
                if self.redis_url:
                    await self.collect_redis_metrics()
                
                if self.mongodb_url:
                    await self.collect_mongodb_metrics()
                
                await asyncio.sleep(self.collection_interval)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in database monitoring loop: {e}")
                await asyncio.sleep(self.collection_interval)