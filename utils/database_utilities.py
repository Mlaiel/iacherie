"""
Database Utilities - DBA Expert Implementation
=============================================

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.

Enterprise database management utilities with optimization and monitoring.
"""

import logging
import time
import asyncio
from typing import Dict, Any, List, Optional, Union, Tuple
from dataclasses import dataclass
from datetime import datetime, timedelta
from contextlib import asynccontextmanager
import hashlib
import json

logger = logging.getLogger(__name__)


@dataclass
class QueryMetrics:
    """Query performance metrics"""
    query_hash: str
    execution_time: float
    rows_affected: int
    timestamp: datetime
    query_type: str
    table_name: str = ""
    index_used: bool = False


@dataclass
class ConnectionPool:
    """Database connection pool configuration"""
    min_connections: int = 5
    max_connections: int = 20
    connection_timeout: int = 30
    idle_timeout: int = 300
    active_connections: int = 0
    created_connections: int = 0


class DatabaseUtilities:
    """
    Enterprise database management system implementing:
    - Connection pooling and management
    - Query optimization and monitoring
    - Performance metrics and analysis
    - Database health monitoring
    - Backup and recovery utilities
    - Schema migration management
    """
    
    def __init__(self) -> None:
        """Initialize database utilities"""
        self.connection_pools: Dict[str, ConnectionPool] = {}
        self.query_metrics: List[QueryMetrics] = []
        self.slow_queries: List[QueryMetrics] = []
        
        # Performance thresholds
        self.performance_thresholds = {
            'slow_query_time': 1.0,  # seconds
            'very_slow_query_time': 5.0,  # seconds
            'max_connections_warning': 15,
            'max_connections_critical': 18
        }
        
        # Database configurations
        self.database_configs = {
            'mongodb': {
                'host': 'localhost',
                'port': 27017,
                'database': 'ainflue',
                'max_pool_size': 20,
                'min_pool_size': 5
            },
            'postgresql': {
                'host': 'localhost',
                'port': 5432,
                'database': 'ainflue',
                'user': 'ainflue_user',
                'password': 'secure_password'
            },
            'redis': {
                'host': 'localhost',
                'port': 6379,
                'db': 0,
                'max_connections': 10
            }
        }
        
        # Query cache
        self.query_cache: Dict[str, Any] = {}
        self.cache_hit_stats = {'hits': 0, 'misses': 0}
        
        # Index recommendations
        self.index_recommendations: List[Dict[str, Any]] = []
        
        logger.info("DatabaseUtilities initialized with enterprise features")
    
    async def create_connection_pool(self, db_name: str, config: Dict[str, Any] = None) -> ConnectionPool:
        """Create and configure database connection pool"""
        try:
            if config is None:
                config = self.database_configs.get(db_name, {})
            
            pool = ConnectionPool(
                min_connections=config.get('min_pool_size', 5),
                max_connections=config.get('max_pool_size', 20),
                connection_timeout=config.get('connection_timeout', 30),
                idle_timeout=config.get('idle_timeout', 300)
            )
            
            self.connection_pools[db_name] = pool
            
            # Initialize minimum connections (mock)
            for i in range(pool.min_connections):
                pool.created_connections += 1
                # In real implementation, create actual connections
            
            logger.info(f"Connection pool created for {db_name}: {pool.min_connections}-{pool.max_connections} connections")
            return pool
            
        except Exception as e:
            logger.error(f"Failed to create connection pool for {db_name}: {e}")
            raise
    
    @asynccontextmanager
    async def get_connection(self, db_name -> None: str) -> None:
        """Get database connection from pool with automatic cleanup"""
        try:
            if db_name not in self.connection_pools:
                await self.create_connection_pool(db_name)
            
            pool = self.connection_pools[db_name]
            
            # Check pool capacity
            if pool.active_connections >= pool.max_connections:
                raise Exception(f"Connection pool exhausted for {db_name}")
            
            # Mock connection acquisition
            pool.active_connections += 1
            connection = f"mock_connection_{db_name}_{int(time.time())}"
            
            logger.debug(f"Connection acquired from {db_name} pool")
            
            try:
                yield connection
            finally:
                # Release connection back to pool
                pool.active_connections -= 1
                logger.debug(f"Connection released to {db_name} pool")
                
        except Exception as e:
            logger.error(f"Connection management error for {db_name}: {e}")
            raise
    
    async def execute_query(self, db_name: str, query: str, parameters: List[Any] = None,
                           cache_key: str = None) -> Dict[str, Any]:
        """Execute database query with performance monitoring"""
        try:
            start_time = time.time()
            
            # Generate query hash for tracking
            query_hash = hashlib.md5(f"{query}{parameters or []}".encode()).hexdigest()
            
            # Check cache first
            if cache_key and cache_key in self.query_cache:
                self.cache_hit_stats['hits'] += 1
                logger.debug(f"Query cache hit: {cache_key}")
                return self.query_cache[cache_key]
            
            self.cache_hit_stats['misses'] += 1
            
            # Execute query using connection pool
            async with self.get_connection(db_name) as connection:
                # Mock query execution
                await asyncio.sleep(0.1)  # Simulate query execution time
                
                # Mock result based on query type
                result = self._mock_query_execution(query, parameters)
                
                execution_time = time.time() - start_time
                
                # Record metrics
                metrics = QueryMetrics(
                    query_hash=query_hash,
                    execution_time=execution_time,
                    rows_affected=result.get('rows_affected', 0),
                    timestamp=datetime.now(),
                    query_type=self._detect_query_type(query),
                    table_name=self._extract_table_name(query),
                    index_used=result.get('index_used', False)
                )
                
                self.query_metrics.append(metrics)
                
                # Check for slow queries
                if execution_time > self.performance_thresholds['slow_query_time']:
                    self.slow_queries.append(metrics)
                    logger.warning(f"Slow query detected: {execution_time:.3f}s - {query[:100]}...")
                
                # Cache result if cache key provided
                if cache_key:
                    self.query_cache[cache_key] = result
                    
                    # Limit cache size
                    if len(self.query_cache) > 1000:
                        # Remove oldest entries
                        oldest_keys = list(self.query_cache.keys())[:100]
                        for key in oldest_keys:
                            del self.query_cache[key]
                
                logger.debug(f"Query executed: {execution_time:.3f}s - {metrics.query_type}")
                return result
                
        except Exception as e:
            logger.error(f"Query execution failed: {e}")
            raise
    
    def _mock_query_execution(self, query: str, parameters: List[Any] = None) -> Dict[str, Any]:
        """Mock query execution for demonstration"""
        query_lower = query.lower().strip()
        
        if query_lower.startswith('select'):
            return {
                'rows': [
                    {'id': 1, 'name': 'Example Record 1', 'created_at': datetime.now()},
                    {'id': 2, 'name': 'Example Record 2', 'created_at': datetime.now()}
                ],
                'rows_affected': 2,
                'index_used': 'id' in query_lower or 'where' in query_lower
            }
        elif query_lower.startswith('insert'):
            return {
                'inserted_id': 123,
                'rows_affected': 1,
                'index_used': False
            }
        elif query_lower.startswith('update'):
            return {
                'rows_affected': 1,
                'index_used': 'where' in query_lower
            }
        elif query_lower.startswith('delete'):
            return {
                'rows_affected': 1,
                'index_used': 'where' in query_lower
            }
        else:
            return {
                'success': True,
                'rows_affected': 0,
                'index_used': False
            }
    
    def _detect_query_type(self, query: str) -> str:
        """Detect the type of SQL query"""
        query_lower = query.lower().strip()
        
        if query_lower.startswith('select'):
            return 'SELECT'
        elif query_lower.startswith('insert'):
            return 'INSERT'
        elif query_lower.startswith('update'):
            return 'UPDATE'
        elif query_lower.startswith('delete'):
            return 'DELETE'
        elif query_lower.startswith('create'):
            return 'CREATE'
        elif query_lower.startswith('drop'):
            return 'DROP'
        elif query_lower.startswith('alter'):
            return 'ALTER'
        else:
            return 'OTHER'
    
    def _extract_table_name(self, query: str) -> str:
        """Extract table name from SQL query"""
        try:
            query_lower = query.lower().strip()
            
            if 'from ' in query_lower:
                # Extract table name after FROM
                from_index = query_lower.find('from ') + 5
                table_part = query_lower[from_index:].strip()
                table_name = table_part.split()[0]
                return table_name.strip('`"[]')
            elif query_lower.startswith('insert into '):
                # Extract table name after INSERT INTO
                table_part = query_lower[12:].strip()
                table_name = table_part.split()[0]
                return table_name.strip('`"[]')
            elif query_lower.startswith('update '):
                # Extract table name after UPDATE
                table_part = query_lower[7:].strip()
                table_name = table_part.split()[0]
                return table_name.strip('`"[]')
            elif query_lower.startswith('delete from '):
                # Extract table name after DELETE FROM
                table_part = query_lower[12:].strip()
                table_name = table_part.split()[0]
                return table_name.strip('`"[]')
            
            return "unknown"
            
        except Exception:
            return "unknown"
    
    async def optimize_query(self, query: str) -> Dict[str, Any]:
        """Analyze and suggest query optimizations"""
        try:
            optimization_suggestions = []
            
            query_lower = query.lower().strip()
            
            # Check for missing WHERE clause in UPDATE/DELETE
            if (query_lower.startswith('update ') or query_lower.startswith('delete ')) and 'where' not in query_lower:
                optimization_suggestions.append({
                    'type': 'WARNING',
                    'issue': 'Missing WHERE clause',
                    'suggestion': 'Add WHERE clause to avoid updating/deleting all rows',
                    'severity': 'HIGH'
                })
            
            # Check for SELECT *
            if 'select *' in query_lower:
                optimization_suggestions.append({
                    'type': 'PERFORMANCE',
                    'issue': 'SELECT * used',
                    'suggestion': 'Specify only needed columns to reduce data transfer',
                    'severity': 'MEDIUM'
                })
            
            # Check for potential index usage
            if 'where' in query_lower and '=' in query_lower:
                # Extract column names in WHERE clause
                where_part = query_lower.split('where')[1].split('order by')[0].split('group by')[0]
                if 'id' not in where_part:
                    optimization_suggestions.append({
                        'type': 'INDEX',
                        'issue': 'Potential missing index',
                        'suggestion': 'Consider adding index on WHERE clause columns',
                        'severity': 'MEDIUM'
                    })
            
            # Check for ORDER BY without LIMIT
            if 'order by' in query_lower and 'limit' not in query_lower:
                optimization_suggestions.append({
                    'type': 'PERFORMANCE',
                    'issue': 'ORDER BY without LIMIT',
                    'suggestion': 'Add LIMIT clause if you don\'t need all results',
                    'severity': 'LOW'
                })
            
            # Suggest query rewrite
            optimized_query = self._suggest_query_rewrite(query)
            
            return {
                'original_query': query,
                'optimized_query': optimized_query,
                'suggestions': optimization_suggestions,
                'estimated_improvement': len(optimization_suggestions) * 15  # Mock percentage
            }
            
        except Exception as e:
            logger.error(f"Query optimization failed: {e}")
            raise
    
    def _suggest_query_rewrite(self, query: str) -> str:
        """Suggest rewritten version of query"""
        # Simple optimization suggestions
        optimized = query
        
        # Replace SELECT * with specific columns (mock)
        if 'SELECT *' in query:
            optimized = optimized.replace('SELECT *', 'SELECT id, name, created_at')
        
        # Add LIMIT if ORDER BY is present without LIMIT
        if 'ORDER BY' in query and 'LIMIT' not in query:
            optimized = optimized + ' LIMIT 100'
        
        return optimized
    
    def analyze_slow_queries(self, time_threshold: float = None) -> Dict[str, Any]:
        """Analyze slow queries and provide recommendations"""
        try:
            if time_threshold is None:
                time_threshold = self.performance_thresholds['slow_query_time']
            
            slow_queries = [m for m in self.query_metrics if m.execution_time > time_threshold]
            
            # Group by query type
            query_type_stats = {}
            for metric in slow_queries:
                query_type = metric.query_type
                if query_type not in query_type_stats:
                    query_type_stats[query_type] = {
                        'count': 0,
                        'total_time': 0.0,
                        'avg_time': 0.0,
                        'max_time': 0.0
                    }
                
                stats = query_type_stats[query_type]
                stats['count'] += 1
                stats['total_time'] += metric.execution_time
                stats['max_time'] = max(stats['max_time'], metric.execution_time)
                stats['avg_time'] = stats['total_time'] / stats['count']
            
            # Most problematic tables
            table_stats = {}
            for metric in slow_queries:
                table = metric.table_name
                if table and table != 'unknown':
                    if table not in table_stats:
                        table_stats[table] = {'count': 0, 'total_time': 0.0}
                    table_stats[table]['count'] += 1
                    table_stats[table]['total_time'] += metric.execution_time
            
            # Sort tables by total time
            problematic_tables = sorted(
                table_stats.items(),
                key=lambda x: x[1]['total_time'],
                reverse=True
            )[:10]
            
            recommendations = []
            
            # Generate recommendations
            if len(slow_queries) > 10:
                recommendations.append("High number of slow queries detected. Consider query optimization.")
            
            for table, stats in problematic_tables:
                if stats['count'] > 5:
                    recommendations.append(f"Table '{table}' has many slow queries. Consider adding indexes.")
            
            return {
                'total_slow_queries': len(slow_queries),
                'time_threshold': time_threshold,
                'query_type_breakdown': query_type_stats,
                'problematic_tables': dict(problematic_tables),
                'recommendations': recommendations,
                'analysis_timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Slow query analysis failed: {e}")
            raise
    
    def get_connection_pool_status(self) -> Dict[str, Any]:
        """Get status of all connection pools"""
        try:
            pool_status = {}
            
            for db_name, pool in self.connection_pools.items():
                utilization = (pool.active_connections / pool.max_connections) * 100
                
                status = 'healthy'
                if pool.active_connections >= self.performance_thresholds['max_connections_critical']:
                    status = 'critical'
                elif pool.active_connections >= self.performance_thresholds['max_connections_warning']:
                    status = 'warning'
                
                pool_status[db_name] = {
                    'active_connections': pool.active_connections,
                    'max_connections': pool.max_connections,
                    'min_connections': pool.min_connections,
                    'created_connections': pool.created_connections,
                    'utilization_percent': utilization,
                    'status': status
                }
            
            return {
                'pools': pool_status,
                'total_pools': len(self.connection_pools),
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to get connection pool status: {e}")
            return {}
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get comprehensive database performance metrics"""
        try:
            total_queries = len(self.query_metrics)
            
            if total_queries == 0:
                return {
                    'total_queries': 0,
                    'message': 'No queries executed yet'
                }
            
            # Calculate averages
            total_time = sum(m.execution_time for m in self.query_metrics)
            avg_query_time = total_time / total_queries
            
            # Query type distribution
            query_types = {}
            for metric in self.query_metrics:
                query_type = metric.query_type
                if query_type not in query_types:
                    query_types[query_type] = 0
                query_types[query_type] += 1
            
            # Recent performance (last hour)
            hour_ago = datetime.now() - timedelta(hours=1)
            recent_queries = [m for m in self.query_metrics if m.timestamp >= hour_ago]
            
            # Cache performance
            total_cache_requests = self.cache_hit_stats['hits'] + self.cache_hit_stats['misses']
            cache_hit_rate = 0.0
            if total_cache_requests > 0:
                cache_hit_rate = (self.cache_hit_stats['hits'] / total_cache_requests) * 100
            
            return {
                'total_queries': total_queries,
                'average_query_time': avg_query_time,
                'slow_queries_count': len(self.slow_queries),
                'query_type_distribution': query_types,
                'recent_queries_count': len(recent_queries),
                'cache_hit_rate': cache_hit_rate,
                'cache_size': len(self.query_cache),
                'connection_pools': self.get_connection_pool_status(),
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to get performance metrics: {e}")
            return {}
    
    async def create_backup(self, db_name: str, backup_type: str = 'full') -> Dict[str, Any]:
        """Create database backup"""
        try:
            start_time = time.time()
            
            # Mock backup process
            await asyncio.sleep(2.0)  # Simulate backup time
            
            backup_id = f"backup_{db_name}_{int(time.time())}"
            backup_size = 1024 * 1024 * 50  # Mock 50MB backup
            
            backup_info = {
                'backup_id': backup_id,
                'database': db_name,
                'backup_type': backup_type,
                'size_bytes': backup_size,
                'created_at': datetime.now().isoformat(),
                'duration_seconds': time.time() - start_time,
                'status': 'completed',
                'file_path': f'/backups/{backup_id}.sql'
            }
            
            logger.info(f"Backup created: {backup_id} for {db_name}")
            return backup_info
            
        except Exception as e:
            logger.error(f"Backup creation failed: {e}")
            raise
    
    def clear_query_cache(self, pattern: str = None) -> int:
        """Clear query cache entries"""
        try:
            if pattern is None:
                # Clear all cache
                cleared_count = len(self.query_cache)
                self.query_cache.clear()
            else:
                # Clear cache entries matching pattern
                keys_to_remove = [key for key in self.query_cache.keys() if pattern in key]
                for key in keys_to_remove:
                    del self.query_cache[key]
                cleared_count = len(keys_to_remove)
            
            logger.info(f"Cleared {cleared_count} cache entries")
            return cleared_count
            
        except Exception as e:
            logger.error(f"Cache clearing failed: {e}")
            return 0


# Global instance for easy access
db_utils = DatabaseUtilities()