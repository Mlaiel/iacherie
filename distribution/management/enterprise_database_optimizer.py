"""
Enterprise Database Optimizer - Advanced Database Performance & Management System
Author: Fahed Mlaiel (mlaiel@live.de)
Role: DBA + Database Architect + Performance Engineer
Version: 2.0 Enterprise Production
"""

import asyncio
import logging
import json
import time
from typing import Dict, List, Any, Optional, Union, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import numpy as np
import hashlib

# Database imports
import asyncpg
import motor.motor_asyncio
import redis.asyncio as redis
from pymongo import MongoClient
import sqlalchemy
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text, inspect

# Monitoring and metrics
import psutil
from prometheus_client import Counter, Histogram, Gauge

class DatabaseType(Enum):
    """Supported database types"""
    POSTGRESQL = "postgresql"
    MONGODB = "mongodb"
    REDIS = "redis"
    MYSQL = "mysql"
    CASSANDRA = "cassandra"

class IndexType(Enum):
    """Database index types"""
    BTREE = "btree"
    HASH = "hash"
    GIN = "gin"
    GIST = "gist"
    BRIN = "brin"
    COMPOUND = "compound"
    TEXT = "text"
    SPARSE = "sparse"

@dataclass
class DatabaseConfig:
    """Database configuration"""
    db_id: str
    db_type: DatabaseType
    connection_string: str
    pool_size: int = 20
    max_overflow: int = 10
    pool_timeout: int = 30
    pool_recycle: int = 3600
    echo: bool = False
    charset: str = "utf8mb4"
    ssl_required: bool = True

@dataclass
class QueryMetrics:
    """Query performance metrics"""
    query_id: str
    query_hash: str
    execution_time: float
    rows_returned: int
    rows_examined: int
    index_used: bool
    memory_usage: int
    cpu_usage: float
    timestamp: datetime
    database_name: str
    table_name: str
    query_type: str  # SELECT, INSERT, UPDATE, DELETE

@dataclass
class IndexRecommendation:
    """Index recommendation"""
    table_name: str
    columns: List[str]
    index_type: IndexType
    estimated_improvement: float
    usage_frequency: int
    priority: str  # high, medium, low
    estimated_size: int
    reason: str

@dataclass
class PerformanceAlert:
    """Performance alert"""
    alert_id: str
    severity: str  # critical, warning, info
    alert_type: str
    message: str
    metric_value: float
    threshold: float
    timestamp: datetime
    database_name: str
    recommendations: List[str]

class QueryAnalyzer:
    """Advanced query analysis and optimization"""
    
    def __init__(self):
        self.slow_query_threshold = 1.0  # seconds
        self.query_cache: Dict[str, List[QueryMetrics]] = {}
        self.query_patterns: Dict[str, int] = {}
        
    def analyze_query(self, query: str, metrics: QueryMetrics) -> Dict[str, Any]:
        """Analyze query performance and provide optimization suggestions"""
        query_hash = self._hash_query(query)
        metrics.query_hash = query_hash
        
        # Store metrics
        if query_hash not in self.query_cache:
            self.query_cache[query_hash] = []
        self.query_cache[query_hash].append(metrics)
        
        # Update pattern frequency
        pattern = self._extract_query_pattern(query)
        self.query_patterns[pattern] = self.query_patterns.get(pattern, 0) + 1
        
        # Analyze performance
        analysis = {
            'is_slow': metrics.execution_time > self.slow_query_threshold,
            'efficiency_score': self._calculate_efficiency_score(metrics),
            'optimization_suggestions': self._generate_optimization_suggestions(query, metrics),
            'index_recommendations': self._recommend_indexes(query, metrics),
            'query_pattern': pattern,
            'frequency': self.query_patterns[pattern]
        }
        
        return analysis
    
    def _hash_query(self, query: str) -> str:
        """Generate hash for query normalization"""
        # Normalize query (remove literals, whitespace, etc.)
        normalized = self._normalize_query(query)
        return hashlib.md5(normalized.encode()).hexdigest()
    
    def _normalize_query(self, query: str) -> str:
        """Normalize query for pattern matching"""
        import re
        
        # Convert to lowercase
        normalized = query.lower().strip()
        
        # Replace string literals with placeholder
        normalized = re.sub(r"'[^']*'", "'?'", normalized)
        
        # Replace numeric literals with placeholder
        normalized = re.sub(r'\b\d+\b', '?', normalized)
        
        # Normalize whitespace
        normalized = re.sub(r'\s+', ' ', normalized)
        
        return normalized
    
    def _extract_query_pattern(self, query: str) -> str:
        """Extract query pattern for categorization"""
        normalized = self._normalize_query(query)
        
        # Extract basic pattern
        if normalized.startswith('select'):
            if 'join' in normalized:
                return 'select_join'
            elif 'group by' in normalized:
                return 'select_aggregate'
            elif 'order by' in normalized:
                return 'select_ordered'
            else:
                return 'select_simple'
        elif normalized.startswith('insert'):
            return 'insert'
        elif normalized.startswith('update'):
            return 'update'
        elif normalized.startswith('delete'):
            return 'delete'
        else:
            return 'other'
    
    def _calculate_efficiency_score(self, metrics: QueryMetrics) -> float:
        """Calculate query efficiency score (0-1, higher is better)"""
        base_score = 1.0
        
        # Penalize slow execution
        if metrics.execution_time > 0.1:
            base_score *= 0.8
        if metrics.execution_time > 1.0:
            base_score *= 0.5
        if metrics.execution_time > 5.0:
            base_score *= 0.2
        
        # Penalize high row examination ratio
        if metrics.rows_returned > 0:
            examination_ratio = metrics.rows_examined / metrics.rows_returned
            if examination_ratio > 10:
                base_score *= 0.7
            elif examination_ratio > 100:
                base_score *= 0.4
        
        # Penalize lack of index usage
        if not metrics.index_used:
            base_score *= 0.6
        
        # Penalize high memory usage
        if metrics.memory_usage > 100 * 1024 * 1024:  # 100MB
            base_score *= 0.8
        
        return max(0.0, min(1.0, base_score))
    
    def _generate_optimization_suggestions(self, query: str, metrics: QueryMetrics) -> List[str]:
        """Generate query optimization suggestions"""
        suggestions = []
        
        if metrics.execution_time > self.slow_query_threshold:
            suggestions.append("Query execution time is slow - consider optimization")
        
        if not metrics.index_used:
            suggestions.append("Query is not using indexes - add appropriate indexes")
        
        if metrics.rows_examined > metrics.rows_returned * 10:
            suggestions.append("Query examines too many rows - add more selective WHERE clauses")
        
        if 'select *' in query.lower():
            suggestions.append("Avoid SELECT * - specify only needed columns")
        
        if 'order by' in query.lower() and not metrics.index_used:
            suggestions.append("Add index on ORDER BY columns for better performance")
        
        if metrics.memory_usage > 50 * 1024 * 1024:  # 50MB
            suggestions.append("Query uses high memory - consider result set limitation")
        
        return suggestions
    
    def _recommend_indexes(self, query: str, metrics: QueryMetrics) -> List[IndexRecommendation]:
        """Recommend indexes based on query analysis"""
        recommendations = []
        
        # Simple heuristic-based recommendations
        # In production, this would use more sophisticated analysis
        
        if not metrics.index_used and 'where' in query.lower():
            # Extract WHERE conditions (simplified)
            import re
            where_match = re.search(r'where\s+(\w+)', query.lower())
            if where_match:
                column = where_match.group(1)
                recommendations.append(IndexRecommendation(
                    table_name=metrics.table_name,
                    columns=[column],
                    index_type=IndexType.BTREE,
                    estimated_improvement=0.7,
                    usage_frequency=self.query_patterns.get(self._extract_query_pattern(query), 1),
                    priority="high",
                    estimated_size=1024 * 1024,  # 1MB estimate
                    reason="Missing index on frequently queried column"
                ))
        
        return recommendations

class ConnectionPoolManager:
    """Advanced connection pool management"""
    
    def __init__(self):
        self.pools: Dict[str, Any] = {}
        self.pool_metrics: Dict[str, Dict[str, Any]] = {}
        
    async def create_postgresql_pool(self, config: DatabaseConfig) -> asyncpg.Pool:
        """Create PostgreSQL connection pool"""
        pool = await asyncpg.create_pool(
            config.connection_string,
            min_size=config.pool_size // 4,
            max_size=config.pool_size,
            command_timeout=config.pool_timeout,
            server_settings={
                'jit': 'off',  # Disable JIT for consistent performance
                'application_name': 'ainflue_distribution'
            }
        )
        
        self.pools[config.db_id] = pool
        self.pool_metrics[config.db_id] = {
            'type': 'postgresql',
            'created_at': datetime.utcnow(),
            'connections_created': 0,
            'connections_closed': 0,
            'active_connections': 0
        }
        
        return pool
    
    async def create_mongodb_pool(self, config: DatabaseConfig) -> motor.motor_asyncio.AsyncIOMotorClient:
        """Create MongoDB connection pool"""
        client = motor.motor_asyncio.AsyncIOMotorClient(
            config.connection_string,
            maxPoolSize=config.pool_size,
            minPoolSize=config.pool_size // 4,
            maxIdleTimeMS=config.pool_recycle * 1000,
            serverSelectionTimeoutMS=config.pool_timeout * 1000
        )
        
        self.pools[config.db_id] = client
        self.pool_metrics[config.db_id] = {
            'type': 'mongodb',
            'created_at': datetime.utcnow(),
            'connections_created': 0,
            'connections_closed': 0,
            'active_connections': 0
        }
        
        return client
    
    async def create_redis_pool(self, config: DatabaseConfig) -> redis.Redis:
        """Create Redis connection pool"""
        pool = redis.ConnectionPool.from_url(
            config.connection_string,
            max_connections=config.pool_size,
            retry_on_timeout=True,
            health_check_interval=30
        )
        
        client = redis.Redis(connection_pool=pool)
        
        self.pools[config.db_id] = client
        self.pool_metrics[config.db_id] = {
            'type': 'redis',
            'created_at': datetime.utcnow(),
            'connections_created': 0,
            'connections_closed': 0,
            'active_connections': 0
        }
        
        return client
    
    async def get_pool_stats(self, db_id: str) -> Dict[str, Any]:
        """Get connection pool statistics"""
        if db_id not in self.pools:
            return {'error': 'Pool not found'}
        
        pool = self.pools[db_id]
        metrics = self.pool_metrics[db_id]
        
        stats = {
            'db_id': db_id,
            'type': metrics['type'],
            'created_at': metrics['created_at'].isoformat(),
            'uptime_seconds': (datetime.utcnow() - metrics['created_at']).total_seconds()
        }
        
        if metrics['type'] == 'postgresql' and hasattr(pool, 'get_size'):
            stats.update({
                'pool_size': pool.get_size(),
                'max_size': pool.get_max_size(),
                'min_size': pool.get_min_size(),
                'idle_connections': pool.get_idle_size(),
                'active_connections': pool.get_size() - pool.get_idle_size()
            })
        
        return stats

class PerformanceMonitor:
    """Database performance monitoring system"""
    
    def __init__(self):
        self.metrics_history: List[Dict[str, Any]] = []
        self.alerts: List[PerformanceAlert] = []
        self.thresholds = {
            'cpu_usage': 80.0,
            'memory_usage': 85.0,
            'connection_usage': 90.0,
            'query_response_time': 2.0,
            'lock_wait_time': 1.0,
            'deadlock_rate': 0.1
        }
        
        # Prometheus metrics
        self.query_duration = Histogram('db_query_duration_seconds', 'Query duration', ['database', 'query_type'])
        self.connection_usage = Gauge('db_connections_active', 'Active connections', ['database'])
        self.cache_hit_ratio = Gauge('db_cache_hit_ratio', 'Cache hit ratio', ['database'])
        
    async def collect_metrics(self, db_id: str, db_type: DatabaseType, connection) -> Dict[str, Any]:
        """Collect comprehensive database metrics"""
        metrics = {
            'timestamp': datetime.utcnow(),
            'db_id': db_id,
            'db_type': db_type.value
        }
        
        try:
            if db_type == DatabaseType.POSTGRESQL:
                metrics.update(await self._collect_postgresql_metrics(connection))
            elif db_type == DatabaseType.MONGODB:
                metrics.update(await self._collect_mongodb_metrics(connection))
            elif db_type == DatabaseType.REDIS:
                metrics.update(await self._collect_redis_metrics(connection))
            
            # Add system metrics
            metrics.update(self._collect_system_metrics())
            
            # Store metrics
            self.metrics_history.append(metrics)
            
            # Keep only last 1000 entries
            if len(self.metrics_history) > 1000:
                self.metrics_history = self.metrics_history[-1000:]
            
            # Check for alerts
            await self._check_performance_alerts(metrics)
            
            return metrics
            
        except Exception as e:
            logging.error(f"Failed to collect metrics for {db_id}: {str(e)}")
            return {'error': str(e)}
    
    async def _collect_postgresql_metrics(self, connection) -> Dict[str, Any]:
        """Collect PostgreSQL-specific metrics"""
        metrics = {}
        
        try:
            # Database size and statistics
            result = await connection.fetch("""
                SELECT 
                    pg_database_size(current_database()) as db_size,
                    (SELECT count(*) FROM pg_stat_activity WHERE state = 'active') as active_connections,
                    (SELECT count(*) FROM pg_stat_activity) as total_connections
            """)
            
            if result:
                row = result[0]
                metrics.update({
                    'database_size_bytes': row['db_size'],
                    'active_connections': row['active_connections'],
                    'total_connections': row['total_connections']
                })
            
            # Cache hit ratio
            cache_result = await connection.fetch("""
                SELECT 
                    sum(heap_blks_hit) / (sum(heap_blks_hit) + sum(heap_blks_read) + 1) as cache_hit_ratio
                FROM pg_statio_user_tables
            """)
            
            if cache_result and cache_result[0]['cache_hit_ratio']:
                metrics['cache_hit_ratio'] = float(cache_result[0]['cache_hit_ratio'])
            
            # Lock information
            lock_result = await connection.fetch("""
                SELECT count(*) as lock_count
                FROM pg_locks 
                WHERE NOT granted
            """)
            
            if lock_result:
                metrics['waiting_locks'] = lock_result[0]['lock_count']
            
            # Index usage statistics
            index_result = await connection.fetch("""
                SELECT 
                    schemaname,
                    tablename,
                    indexname,
                    idx_scan,
                    idx_tup_read,
                    idx_tup_fetch
                FROM pg_stat_user_indexes
                ORDER BY idx_scan DESC
                LIMIT 10
            """)
            
            metrics['top_indexes'] = [dict(row) for row in index_result]
            
        except Exception as e:
            logging.error(f"PostgreSQL metrics collection failed: {str(e)}")
            metrics['collection_error'] = str(e)
        
        return metrics
    
    async def _collect_mongodb_metrics(self, client) -> Dict[str, Any]:
        """Collect MongoDB-specific metrics"""
        metrics = {}
        
        try:
            # Server status
            admin_db = client.admin
            server_status = await admin_db.command("serverStatus")
            
            metrics.update({
                'connections_current': server_status.get('connections', {}).get('current', 0),
                'connections_available': server_status.get('connections', {}).get('available', 0),
                'memory_resident': server_status.get('mem', {}).get('resident', 0),
                'memory_virtual': server_status.get('mem', {}).get('virtual', 0),
                'operations_insert': server_status.get('opcounters', {}).get('insert', 0),
                'operations_query': server_status.get('opcounters', {}).get('query', 0),
                'operations_update': server_status.get('opcounters', {}).get('update', 0),
                'operations_delete': server_status.get('opcounters', {}).get('delete', 0)
            })
            
            # Database statistics
            db_stats = await admin_db.command("dbStats")
            metrics.update({
                'database_size_bytes': db_stats.get('dataSize', 0),
                'index_size_bytes': db_stats.get('indexSize', 0),
                'collection_count': db_stats.get('collections', 0)
            })
            
        except Exception as e:
            logging.error(f"MongoDB metrics collection failed: {str(e)}")
            metrics['collection_error'] = str(e)
        
        return metrics
    
    async def _collect_redis_metrics(self, client) -> Dict[str, Any]:
        """Collect Redis-specific metrics"""
        metrics = {}
        
        try:
            info = await client.info()
            
            metrics.update({
                'connected_clients': info.get('connected_clients', 0),
                'used_memory': info.get('used_memory', 0),
                'used_memory_peak': info.get('used_memory_peak', 0),
                'keyspace_hits': info.get('keyspace_hits', 0),
                'keyspace_misses': info.get('keyspace_misses', 0),
                'expired_keys': info.get('expired_keys', 0),
                'evicted_keys': info.get('evicted_keys', 0)
            })
            
            # Calculate hit ratio
            hits = metrics['keyspace_hits']
            misses = metrics['keyspace_misses']
            if hits + misses > 0:
                metrics['cache_hit_ratio'] = hits / (hits + misses)
            
        except Exception as e:
            logging.error(f"Redis metrics collection failed: {str(e)}")
            metrics['collection_error'] = str(e)
        
        return metrics
    
    def _collect_system_metrics(self) -> Dict[str, Any]:
        """Collect system-level metrics"""
        return {
            'cpu_usage_percent': psutil.cpu_percent(),
            'memory_usage_percent': psutil.virtual_memory().percent,
            'disk_usage_percent': psutil.disk_usage('/').percent,
            'disk_io_read_bytes': psutil.disk_io_counters().read_bytes if psutil.disk_io_counters() else 0,
            'disk_io_write_bytes': psutil.disk_io_counters().write_bytes if psutil.disk_io_counters() else 0,
            'network_bytes_sent': psutil.net_io_counters().bytes_sent if psutil.net_io_counters() else 0,
            'network_bytes_recv': psutil.net_io_counters().bytes_recv if psutil.net_io_counters() else 0
        }
    
    async def _check_performance_alerts(self, metrics: Dict[str, Any]):
        """Check metrics against thresholds and generate alerts"""
        alerts_to_add = []
        
        # CPU usage alert
        cpu_usage = metrics.get('cpu_usage_percent', 0)
        if cpu_usage > self.thresholds['cpu_usage']:
            alerts_to_add.append(PerformanceAlert(
                alert_id=f"cpu_alert_{int(time.time())}",
                severity="warning" if cpu_usage < 90 else "critical",
                alert_type="cpu_usage",
                message=f"High CPU usage: {cpu_usage:.1f}%",
                metric_value=cpu_usage,
                threshold=self.thresholds['cpu_usage'],
                timestamp=datetime.utcnow(),
                database_name=metrics['db_id'],
                recommendations=["Consider scaling up CPU resources", "Optimize slow queries", "Add query caching"]
            ))
        
        # Memory usage alert
        memory_usage = metrics.get('memory_usage_percent', 0)
        if memory_usage > self.thresholds['memory_usage']:
            alerts_to_add.append(PerformanceAlert(
                alert_id=f"memory_alert_{int(time.time())}",
                severity="warning" if memory_usage < 95 else "critical",
                alert_type="memory_usage",
                message=f"High memory usage: {memory_usage:.1f}%",
                metric_value=memory_usage,
                threshold=self.thresholds['memory_usage'],
                timestamp=datetime.utcnow(),
                database_name=metrics['db_id'],
                recommendations=["Increase available memory", "Optimize memory-intensive queries", "Implement query result caching"]
            ))
        
        # Connection usage alert
        if 'total_connections' in metrics and 'active_connections' in metrics:
            connection_usage = (metrics['active_connections'] / max(1, metrics['total_connections'])) * 100
            if connection_usage > self.thresholds['connection_usage']:
                alerts_to_add.append(PerformanceAlert(
                    alert_id=f"connection_alert_{int(time.time())}",
                    severity="warning" if connection_usage < 95 else "critical",
                    alert_type="connection_usage",
                    message=f"High connection usage: {connection_usage:.1f}%",
                    metric_value=connection_usage,
                    threshold=self.thresholds['connection_usage'],
                    timestamp=datetime.utcnow(),
                    database_name=metrics['db_id'],
                    recommendations=["Increase connection pool size", "Implement connection pooling", "Optimize connection usage patterns"]
                ))
        
        # Add alerts
        self.alerts.extend(alerts_to_add)
        
        # Keep only recent alerts (last 24 hours)
        cutoff_time = datetime.utcnow() - timedelta(hours=24)
        self.alerts = [alert for alert in self.alerts if alert.timestamp > cutoff_time]

class IndexManager:
    """Advanced database index management"""
    
    def __init__(self):
        self.index_usage_stats: Dict[str, Dict[str, Any]] = {}
        self.recommendations: List[IndexRecommendation] = []
        
    async def analyze_index_usage(self, db_type: DatabaseType, connection) -> Dict[str, Any]:
        """Analyze index usage patterns"""
        try:
            if db_type == DatabaseType.POSTGRESQL:
                return await self._analyze_postgresql_indexes(connection)
            elif db_type == DatabaseType.MONGODB:
                return await self._analyze_mongodb_indexes(connection)
            else:
                return {'error': 'Index analysis not supported for this database type'}
        except Exception as e:
            logging.error(f"Index analysis failed: {str(e)}")
            return {'error': str(e)}
    
    async def _analyze_postgresql_indexes(self, connection) -> Dict[str, Any]:
        """Analyze PostgreSQL index usage"""
        # Get index usage statistics
        index_stats = await connection.fetch("""
            SELECT 
                schemaname,
                tablename,
                indexname,
                idx_scan,
                idx_tup_read,
                idx_tup_fetch,
                pg_size_pretty(pg_relation_size(indexrelid)) as index_size,
                pg_relation_size(indexrelid) as index_size_bytes
            FROM pg_stat_user_indexes
            ORDER BY idx_scan DESC
        """)
        
        # Get unused indexes
        unused_indexes = await connection.fetch("""
            SELECT 
                schemaname,
                tablename,
                indexname,
                pg_size_pretty(pg_relation_size(indexrelid)) as index_size,
                pg_relation_size(indexrelid) as index_size_bytes
            FROM pg_stat_user_indexes
            WHERE idx_scan = 0
            AND indexname NOT LIKE '%_pkey'
            ORDER BY pg_relation_size(indexrelid) DESC
        """)
        
        # Get duplicate indexes
        duplicate_indexes = await connection.fetch("""
            SELECT 
                t1.schemaname,
                t1.tablename,
                t1.indexname as index1,
                t2.indexname as index2,
                pg_get_indexdef(t1.indexrelid) as index1_def,
                pg_get_indexdef(t2.indexrelid) as index2_def
            FROM pg_stat_user_indexes t1
            JOIN pg_stat_user_indexes t2 ON (
                t1.schemaname = t2.schemaname AND
                t1.tablename = t2.tablename AND
                t1.indexname < t2.indexname AND
                pg_get_indexdef(t1.indexrelid) = pg_get_indexdef(t2.indexrelid)
            )
        """)
        
        # Get table sizes for context
        table_sizes = await connection.fetch("""
            SELECT 
                schemaname,
                tablename,
                pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) as table_size,
                pg_total_relation_size(schemaname||'.'||tablename) as table_size_bytes,
                n_tup_ins + n_tup_upd + n_tup_del as total_writes,
                seq_scan,
                seq_tup_read,
                idx_scan,
                idx_tup_fetch
            FROM pg_stat_user_tables
            ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC
        """)
        
        return {
            'index_usage_stats': [dict(row) for row in index_stats],
            'unused_indexes': [dict(row) for row in unused_indexes],
            'duplicate_indexes': [dict(row) for row in duplicate_indexes],
            'table_statistics': [dict(row) for row in table_sizes],
            'total_indexes': len(index_stats),
            'unused_count': len(unused_indexes),
            'duplicate_count': len(duplicate_indexes)
        }
    
    async def _analyze_mongodb_indexes(self, client) -> Dict[str, Any]:
        """Analyze MongoDB index usage"""
        analysis_results = {}
        
        # Get all databases
        db_names = await client.list_database_names()
        
        for db_name in db_names:
            if db_name in ['admin', 'local', 'config']:
                continue
                
            db = client[db_name]
            collection_names = await db.list_collection_names()
            
            db_analysis = {}
            
            for collection_name in collection_names:
                collection = db[collection_name]
                
                # Get index information
                indexes = await collection.list_indexes().to_list(length=None)
                
                # Get index stats (if available)
                try:
                    index_stats = await collection.aggregate([
                        {"$indexStats": {}}
                    ]).to_list(length=None)
                except:
                    index_stats = []
                
                db_analysis[collection_name] = {
                    'indexes': indexes,
                    'index_stats': index_stats,
                    'index_count': len(indexes)
                }
            
            analysis_results[db_name] = db_analysis
        
        return analysis_results
    
    async def generate_index_recommendations(self, query_analyzer: QueryAnalyzer) -> List[IndexRecommendation]:
        """Generate index recommendations based on query analysis"""
        recommendations = []
        
        # Analyze query patterns from the query analyzer
        for query_hash, metrics_list in query_analyzer.query_cache.items():
            if not metrics_list:
                continue
                
            # Get most recent metrics
            latest_metrics = metrics_list[-1]
            
            # Check if index recommendations are needed
            if not latest_metrics.index_used and latest_metrics.execution_time > 0.5:
                # This is a simplified recommendation logic
                # In production, this would involve more sophisticated analysis
                
                recommendation = IndexRecommendation(
                    table_name=latest_metrics.table_name,
                    columns=["inferred_column"],  # Would be extracted from actual query
                    index_type=IndexType.BTREE,
                    estimated_improvement=0.6,
                    usage_frequency=len(metrics_list),
                    priority="medium",
                    estimated_size=1024 * 1024,  # 1MB
                    reason="Slow query without index usage"
                )
                recommendations.append(recommendation)
        
        # Sort by priority and estimated improvement
        recommendations.sort(key=lambda x: (
            {'high': 3, 'medium': 2, 'low': 1}[x.priority],
            x.estimated_improvement
        ), reverse=True)
        
        return recommendations[:10]  # Return top 10 recommendations

class EnterpriseDatabaseOptimizer:
    """Central database optimization and management system"""
    
    def __init__(self):
        self.databases: Dict[str, DatabaseConfig] = {}
        self.connection_manager = ConnectionPoolManager()
        self.performance_monitor = PerformanceMonitor()
        self.query_analyzer = QueryAnalyzer()
        self.index_manager = IndexManager()
        
        self.optimization_tasks: List[asyncio.Task] = []
        self.monitoring_active = False
        
        self.logger = logging.getLogger(__name__)
    
    async def register_database(self, config: DatabaseConfig):
        """Register a database for optimization"""
        self.databases[config.db_id] = config
        
        # Create connection pool
        if config.db_type == DatabaseType.POSTGRESQL:
            await self.connection_manager.create_postgresql_pool(config)
        elif config.db_type == DatabaseType.MONGODB:
            await self.connection_manager.create_mongodb_pool(config)
        elif config.db_type == DatabaseType.REDIS:
            await self.connection_manager.create_redis_pool(config)
        
        self.logger.info(f"Database registered: {config.db_id}")
    
    async def start_monitoring(self):
        """Start continuous performance monitoring"""
        if self.monitoring_active:
            return
        
        self.monitoring_active = True
        
        # Start monitoring tasks for each database
        for db_id, config in self.databases.items():
            task = asyncio.create_task(self._monitoring_loop(db_id, config))
            self.optimization_tasks.append(task)
        
        self.logger.info("Database monitoring started")
    
    async def stop_monitoring(self):
        """Stop performance monitoring"""
        self.monitoring_active = False
        
        # Cancel monitoring tasks
        for task in self.optimization_tasks:
            task.cancel()
        
        # Wait for tasks to complete
        await asyncio.gather(*self.optimization_tasks, return_exceptions=True)
        self.optimization_tasks.clear()
        
        self.logger.info("Database monitoring stopped")
    
    async def _monitoring_loop(self, db_id: str, config: DatabaseConfig):
        """Continuous monitoring loop for a database"""
        while self.monitoring_active:
            try:
                connection = self.connection_manager.pools.get(db_id)
                if connection:
                    metrics = await self.performance_monitor.collect_metrics(
                        db_id, config.db_type, connection
                    )
                    
                    # Log significant metrics
                    if 'cpu_usage_percent' in metrics and metrics['cpu_usage_percent'] > 80:
                        self.logger.warning(f"High CPU usage on {db_id}: {metrics['cpu_usage_percent']:.1f}%")
                
                await asyncio.sleep(60)  # Collect metrics every minute
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"Monitoring error for {db_id}: {str(e)}")
                await asyncio.sleep(60)
    
    async def optimize_database(self, db_id: str) -> Dict[str, Any]:
        """Perform comprehensive database optimization"""
        if db_id not in self.databases:
            return {'error': 'Database not found'}
        
        config = self.databases[db_id]
        connection = self.connection_manager.pools.get(db_id)
        
        if not connection:
            return {'error': 'Database connection not available'}
        
        try:
            optimization_results = {
                'db_id': db_id,
                'optimization_timestamp': datetime.utcnow().isoformat(),
                'results': {}
            }
            
            # 1. Analyze current performance
            metrics = await self.performance_monitor.collect_metrics(
                db_id, config.db_type, connection
            )
            optimization_results['results']['current_metrics'] = metrics
            
            # 2. Analyze index usage
            index_analysis = await self.index_manager.analyze_index_usage(
                config.db_type, connection
            )
            optimization_results['results']['index_analysis'] = index_analysis
            
            # 3. Generate index recommendations
            index_recommendations = await self.index_manager.generate_index_recommendations(
                self.query_analyzer
            )
            optimization_results['results']['index_recommendations'] = [
                {
                    'table': rec.table_name,
                    'columns': rec.columns,
                    'type': rec.index_type.value,
                    'priority': rec.priority,
                    'reason': rec.reason,
                    'estimated_improvement': rec.estimated_improvement
                }
                for rec in index_recommendations
            ]
            
            # 4. Query optimization suggestions
            query_suggestions = self._generate_query_optimization_suggestions(metrics)
            optimization_results['results']['query_suggestions'] = query_suggestions
            
            # 5. Configuration recommendations
            config_recommendations = self._generate_configuration_recommendations(metrics, config)
            optimization_results['results']['configuration_recommendations'] = config_recommendations
            
            return optimization_results
            
        except Exception as e:
            self.logger.error(f"Database optimization failed for {db_id}: {str(e)}")
            return {
                'error': str(e),
                'db_id': db_id
            }
    
    def _generate_query_optimization_suggestions(self, metrics: Dict[str, Any]) -> List[str]:
        """Generate query optimization suggestions based on metrics"""
        suggestions = []
        
        if metrics.get('cache_hit_ratio', 1.0) < 0.9:
            suggestions.append("Low cache hit ratio - consider increasing shared buffers or implementing query caching")
        
        if metrics.get('waiting_locks', 0) > 5:
            suggestions.append("High number of waiting locks - review query patterns and consider lock optimization")
        
        if metrics.get('active_connections', 0) > metrics.get('total_connections', 100) * 0.8:
            suggestions.append("High connection usage - consider connection pooling optimization")
        
        if metrics.get('cpu_usage_percent', 0) > 80:
            suggestions.append("High CPU usage - analyze and optimize slow queries")
        
        return suggestions
    
    def _generate_configuration_recommendations(self, metrics: Dict[str, Any], config: DatabaseConfig) -> List[str]:
        """Generate database configuration recommendations"""
        recommendations = []
        
        if config.db_type == DatabaseType.POSTGRESQL:
            if metrics.get('cache_hit_ratio', 1.0) < 0.95:
                recommendations.append("Consider increasing shared_buffers (25-40% of RAM)")
            
            if metrics.get('active_connections', 0) > config.pool_size * 0.8:
                recommendations.append("Consider increasing max_connections and pool size")
            
            recommendations.append("Enable pg_stat_statements for query analysis")
            recommendations.append("Consider setting effective_cache_size to 75% of RAM")
        
        elif config.db_type == DatabaseType.MONGODB:
            if metrics.get('memory_resident', 0) > metrics.get('memory_virtual', 1) * 0.8:
                recommendations.append("Consider increasing WiredTiger cache size")
            
            recommendations.append("Enable slow operation profiling")
            recommendations.append("Consider read preferences for read-heavy workloads")
        
        elif config.db_type == DatabaseType.REDIS:
            if metrics.get('cache_hit_ratio', 1.0) < 0.9:
                recommendations.append("Consider increasing maxmemory and optimizing eviction policies")
            
            if metrics.get('used_memory', 0) > metrics.get('used_memory_peak', 1) * 0.9:
                recommendations.append("Monitor memory usage and consider scaling")
        
        return recommendations
    
    async def get_optimization_status(self) -> Dict[str, Any]:
        """Get comprehensive optimization status"""
        status = {
            'total_databases': len(self.databases),
            'monitoring_active': self.monitoring_active,
            'recent_alerts': len([alert for alert in self.performance_monitor.alerts 
                                if alert.timestamp > datetime.utcnow() - timedelta(hours=1)]),
            'databases': {}
        }
        
        for db_id, config in self.databases.items():
            pool_stats = await self.connection_manager.get_pool_stats(db_id)
            
            # Get recent metrics
            recent_metrics = None
            for metrics in reversed(self.performance_monitor.metrics_history):
                if metrics.get('db_id') == db_id:
                    recent_metrics = metrics
                    break
            
            status['databases'][db_id] = {
                'type': config.db_type.value,
                'pool_stats': pool_stats,
                'recent_metrics': recent_metrics,
                'last_optimization': None  # Would track last optimization time
            }
        
        return status
    
    async def execute_query_with_analysis(self, db_id: str, query: str, params: List[Any] = None) -> Dict[str, Any]:
        """Execute query with performance analysis"""
        if db_id not in self.databases:
            return {'error': 'Database not found'}
        
        config = self.databases[db_id]
        connection = self.connection_manager.pools.get(db_id)
        
        if not connection:
            return {'error': 'Database connection not available'}
        
        start_time = time.time()
        
        try:
            if config.db_type == DatabaseType.POSTGRESQL:
                if hasattr(connection, 'acquire'):
                    async with connection.acquire() as conn:
                        result = await conn.fetch(query, *(params or []))
                else:
                    result = await connection.fetch(query, *(params or []))
                
                execution_time = time.time() - start_time
                
                # Create query metrics
                query_metrics = QueryMetrics(
                    query_id=f"query_{int(time.time())}",
                    query_hash="",
                    execution_time=execution_time,
                    rows_returned=len(result),
                    rows_examined=len(result),  # Simplified
                    index_used=True,  # Would need EXPLAIN to determine
                    memory_usage=0,  # Would need monitoring
                    cpu_usage=0.0,  # Would need monitoring
                    timestamp=datetime.utcnow(),
                    database_name=db_id,
                    table_name="unknown",  # Would parse from query
                    query_type=query.strip().split()[0].upper()
                )
                
                # Analyze query
                analysis = self.query_analyzer.analyze_query(query, query_metrics)
                
                return {
                    'status': 'success',
                    'result': [dict(row) for row in result],
                    'execution_time': execution_time,
                    'rows_returned': len(result),
                    'analysis': analysis
                }
            
            else:
                return {'error': 'Query execution not implemented for this database type'}
                
        except Exception as e:
            execution_time = time.time() - start_time
            self.logger.error(f"Query execution failed: {str(e)}")
            
            return {
                'status': 'error',
                'error': str(e),
                'execution_time': execution_time
            }

# Factory function
async def create_enterprise_database_optimizer() -> EnterpriseDatabaseOptimizer:
    """Factory function to create database optimizer"""
    optimizer = EnterpriseDatabaseOptimizer()
    return optimizer

# Export main components
__all__ = [
    'EnterpriseDatabaseOptimizer',
    'DatabaseConfig',
    'DatabaseType',
    'QueryMetrics',
    'IndexRecommendation',
    'PerformanceAlert',
    'QueryAnalyzer',
    'PerformanceMonitor',
    'IndexManager',
    'ConnectionPoolManager',
    'create_enterprise_database_optimizer'
]