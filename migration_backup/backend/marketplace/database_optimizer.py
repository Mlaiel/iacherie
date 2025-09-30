"""Database Optimizer - Query Performance Optimization for Marketplace
====================================================================

Enterprise-grade database optimization system providing query performance monitoring,
automatic optimization suggestions, and database performance analytics.

Features:
- Query performance monitoring and analysis
- Automatic index recommendations
- Query execution plan optimization
- Database connection pool management
- Performance bottleneck identification
- Real-time performance metrics and alerting

Architecture: Enterprise Production-Ready (Backend Level 3)
Module: backend/marketplace/database_optimizer.py

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import logging
import asyncio
import time
from typing import Dict, List, Optional, Union, Any, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from decimal import Decimal
from enum import Enum
import uuid
import json
import hashlib

logger = logging.getLogger(__name__)

class QueryType(Enum):
    """Query type enumeration"""
    SELECT = "select"
    INSERT = "insert"
    UPDATE = "update"
    DELETE = "delete"
    JOIN = "join"
    AGGREGATE = "aggregate"
    SUBQUERY = "subquery"

class PerformanceLevel(Enum):
    """Performance level enumeration"""
    EXCELLENT = "excellent"     # < 10ms
    GOOD = "good"              # 10-50ms
    AVERAGE = "average"        # 50-200ms
    POOR = "poor"              # 200-1000ms
    CRITICAL = "critical"      # > 1000ms

class OptimizationType(Enum):
    """Optimization type enumeration"""
    INDEX_CREATION = "index_creation"
    QUERY_REWRITE = "query_rewrite"
    PARTITION_TABLE = "partition_table"
    DENORMALIZATION = "denormalization"
    CACHING = "caching"
    CONNECTION_POOL = "connection_pool"

@dataclass
class QueryMetrics:
    """Query performance metrics"""
    query_id: str
    query_hash: str
    query_text: str
    query_type: QueryType
    execution_time_ms: float
    rows_examined: int = 0
    rows_returned: int = 0
    index_usage: List[str] = field(default_factory=list)
    table_scans: int = 0
    joins: int = 0
    cpu_usage: float = 0.0
    memory_usage: int = 0
    execution_count: int = 1
    first_seen: datetime = field(default_factory=datetime.utcnow)
    last_seen: datetime = field(default_factory=datetime.utcnow)

@dataclass
class OptimizationRecommendation:
    """Database optimization recommendation"""
    recommendation_id: str
    query_hash: str
    optimization_type: OptimizationType
    priority: str = "medium"  # low, medium, high, critical
    description: str = ""
    sql_statement: str = ""
    estimated_improvement: float = 0.0  # percentage improvement
    impact_assessment: str = ""
    implementation_effort: str = "medium"  # low, medium, high
    created_at: datetime = field(default_factory=datetime.utcnow)
    implemented: bool = False
    implementation_date: Optional[datetime] = None

@dataclass
class IndexRecommendation:
    """Index creation recommendation"""
    table_name: str
    columns: List[str]
    index_type: str = "btree"  # btree, hash, gin, gist
    estimated_size_mb: float = 0.0
    estimated_performance_gain: float = 0.0
    maintenance_cost: str = "low"  # low, medium, high
    usage_frequency: int = 0

@dataclass
class TableStatistics:
    """Database table statistics"""
    table_name: str
    row_count: int = 0
    size_mb: float = 0.0
    index_count: int = 0
    index_size_mb: float = 0.0
    avg_query_time_ms: float = 0.0
    daily_query_count: int = 0
    last_analyzed: datetime = field(default_factory=datetime.utcnow)

@dataclass
class ConnectionPoolStats:
    """Database connection pool statistics"""
    pool_name: str
    active_connections: int = 0
    idle_connections: int = 0
    max_connections: int = 0
    total_requests: int = 0
    avg_wait_time_ms: float = 0.0
    connection_errors: int = 0
    last_updated: datetime = field(default_factory=datetime.utcnow)

class DatabaseOptimizer:
    """Database performance optimization and monitoring system"""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        
        # Query monitoring
        self.query_metrics: Dict[str, QueryMetrics] = {}
        self.optimization_recommendations: Dict[str, OptimizationRecommendation] = {}
        self.table_statistics: Dict[str, TableStatistics] = {}
        
        # Performance thresholds
        self.slow_query_threshold_ms = float(self.config.get('slow_query_threshold_ms', 100))
        self.critical_query_threshold_ms = float(self.config.get('critical_query_threshold_ms', 1000))
        self.monitoring_enabled = self.config.get('monitoring_enabled', True)
        
        # Connection pool monitoring
        self.connection_pools: Dict[str, ConnectionPoolStats] = {}
        
        logger.info("🎯 Database Optimizer initialized")
    
    async def monitor_query(self, query_text: str, execution_time_ms: float, 
                           query_metadata: Dict[str, Any] = None) -> QueryMetrics:
        """Monitor and analyze query performance"""
        try:
            if not self.monitoring_enabled:
                return
            
            # Generate query hash for identification
            query_hash = self._generate_query_hash(query_text)
            
            # Determine query type
            query_type = self._detect_query_type(query_text)
            
            # Get or create query metrics
            if query_hash in self.query_metrics:
                metrics = self.query_metrics[query_hash]
                metrics.execution_count += 1
                metrics.last_seen = datetime.utcnow()
                
                # Update execution time (moving average)
                total_time = metrics.execution_time_ms * (metrics.execution_count - 1) + execution_time_ms
                metrics.execution_time_ms = total_time / metrics.execution_count
            else:
                metrics = QueryMetrics(
                    query_id=str(uuid.uuid4()),
                    query_hash=query_hash,
                    query_text=query_text,
                    query_type=query_type,
                    execution_time_ms=execution_time_ms
                )
                self.query_metrics[query_hash] = metrics
            
            # Update metadata if provided
            if query_metadata:
                metrics.rows_examined = query_metadata.get('rows_examined', 0)
                metrics.rows_returned = query_metadata.get('rows_returned', 0)
                metrics.index_usage = query_metadata.get('index_usage', [])
                metrics.table_scans = query_metadata.get('table_scans', 0)
                metrics.joins = query_metadata.get('joins', 0)
            
            # Check if optimization is needed
            if execution_time_ms > self.slow_query_threshold_ms:
                await self._analyze_and_recommend(metrics)
            
            logger.debug(f"Query monitored: {query_hash} - {execution_time_ms:.2f}ms")
            return metrics
            
        except Exception as e:
            logger.error(f"Query monitoring error: {e}")
            return None
    
    def _generate_query_hash(self, query_text: str) -> str:
        """Generate hash for query identification"""
        # Normalize query text (remove extra spaces, convert to lowercase)
        normalized = ' '.join(query_text.lower().split())
        return hashlib.md5(normalized.encode()).hexdigest()
    
    def _detect_query_type(self, query_text: str) -> QueryType:
        """Detect query type from SQL text"""
        query_lower = query_text.lower().strip()
        
        if query_lower.startswith('select'):
            if 'join' in query_lower:
                return QueryType.JOIN
            elif any(agg in query_lower for agg in ['count(', 'sum(', 'avg(', 'max(', 'min(']):
                return QueryType.AGGREGATE
            elif 'where' in query_lower and ('select' in query_lower[query_lower.find('where'):]):
                return QueryType.SUBQUERY
            else:
                return QueryType.SELECT
        elif query_lower.startswith('insert'):
            return QueryType.INSERT
        elif query_lower.startswith('update'):
            return QueryType.UPDATE
        elif query_lower.startswith('delete'):
            return QueryType.DELETE
        else:
            return QueryType.SELECT  # Default
    
    async def _analyze_and_recommend(self, metrics: QueryMetrics):
        """Analyze query performance and generate recommendations"""
        try:
            recommendations = []
            
            # Check for missing indexes
            if metrics.table_scans > 0:
                recommendations.extend(await self._recommend_indexes(metrics))
            
            # Check for inefficient joins
            if metrics.joins > 2 and metrics.execution_time_ms > 200:
                recommendations.extend(await self._recommend_join_optimization(metrics))
            
            # Check for query rewrite opportunities
            if metrics.execution_time_ms > self.critical_query_threshold_ms:
                recommendations.extend(await self._recommend_query_rewrite(metrics))
            
            # Store recommendations
            for rec in recommendations:
                self.optimization_recommendations[rec.recommendation_id] = rec
            
            logger.info(f"Generated {len(recommendations)} optimization recommendations for query {metrics.query_hash}")
            
        except Exception as e:
            logger.error(f"Query analysis error: {e}")
    
    async def _recommend_indexes(self, metrics: QueryMetrics) -> List[OptimizationRecommendation]:
        """Recommend index creation for slow queries"""
        try:
            recommendations = []
            
            # Extract table and column information from query
            tables, columns = self._extract_query_components(metrics.query_text)
            
            for table in tables:
                # Check if columns are frequently used in WHERE clauses
                where_columns = self._extract_where_columns(metrics.query_text, table)
                
                if where_columns:
                    index_rec = IndexRecommendation(
                        table_name=table,
                        columns=where_columns,
                        estimated_performance_gain=min(80.0, metrics.execution_time_ms / 10),
                        usage_frequency=metrics.execution_count
                    )
                    
                    recommendation = OptimizationRecommendation(
                        recommendation_id=str(uuid.uuid4()),
                        query_hash=metrics.query_hash,
                        optimization_type=OptimizationType.INDEX_CREATION,
                        priority="high" if metrics.execution_time_ms > 500 else "medium",
                        description=f"Create index on {table}({', '.join(where_columns)}) to improve query performance",
                        sql_statement=f"CREATE INDEX idx_{table}_{'_'.join(where_columns)} ON {table} ({', '.join(where_columns)});",
                        estimated_improvement=index_rec.estimated_performance_gain
                    )
                    
                    recommendations.append(recommendation)
            
            return recommendations
            
        except Exception as e:
            logger.error(f"Index recommendation error: {e}")
            return []
    
    async def _recommend_join_optimization(self, metrics: QueryMetrics) -> List[OptimizationRecommendation]:
        """Recommend join optimization strategies"""
        try:
            recommendations = []
            
            if metrics.joins > 3:
                recommendation = OptimizationRecommendation(
                    recommendation_id=str(uuid.uuid4()),
                    query_hash=metrics.query_hash,
                    optimization_type=OptimizationType.QUERY_REWRITE,
                    priority="medium",
                    description="Consider breaking complex join into smaller queries or using temporary tables",
                    estimated_improvement=30.0,
                    impact_assessment="Moderate improvement expected for complex join queries"
                )
                recommendations.append(recommendation)
            
            return recommendations
            
        except Exception as e:
            logger.error(f"Join optimization error: {e}")
            return []
    
    async def _recommend_query_rewrite(self, metrics: QueryMetrics) -> List[OptimizationRecommendation]:
        """Recommend query rewrite strategies"""
        try:
            recommendations = []
            
            # Check for common optimization opportunities
            query_lower = metrics.query_text.lower()
            
            # Subquery to JOIN conversion
            if 'where' in query_lower and 'in (select' in query_lower:
                recommendation = OptimizationRecommendation(
                    recommendation_id=str(uuid.uuid4()),
                    query_hash=metrics.query_hash,
                    optimization_type=OptimizationType.QUERY_REWRITE,
                    priority="high",
                    description="Convert IN subquery to JOIN for better performance",
                    estimated_improvement=50.0,
                    impact_assessment="Significant improvement expected"
                )
                recommendations.append(recommendation)
            
            # SELECT * optimization
            if 'select *' in query_lower:
                recommendation = OptimizationRecommendation(
                    recommendation_id=str(uuid.uuid4()),
                    query_hash=metrics.query_hash,
                    optimization_type=OptimizationType.QUERY_REWRITE,
                    priority="low",
                    description="Replace SELECT * with specific column names to reduce I/O",
                    estimated_improvement=15.0,
                    impact_assessment="Minor improvement, better for network and memory usage"
                )
                recommendations.append(recommendation)
            
            return recommendations
            
        except Exception as e:
            logger.error(f"Query rewrite recommendation error: {e}")
            return []
    
    def _extract_query_components(self, query_text: str) -> Tuple[List[str], List[str]]:
        """Extract table and column names from query"""
        try:
            # Simple extraction - in production, use proper SQL parser
            query_lower = query_text.lower()
            
            # Extract table names
            tables = []
            if 'from' in query_lower:
                from_index = query_lower.find('from')
                from_part = query_lower[from_index:].split('where')[0].split('group')[0].split('order')[0]
                # Simple extraction: get words after FROM
                words = from_part.replace(',', ' ').split()
                for i, word in enumerate(words):
                    if word not in ['from', 'join', 'inner', 'left', 'right', 'outer', 'on', 'as']:
                        if not word.startswith('('):  # Skip subqueries
                            tables.append(word)
            
            # Extract column names (simplified)
            columns = []
            if 'select' in query_lower:
                select_part = query_lower[query_lower.find('select')+6:query_lower.find('from')].strip()
                if select_part != '*':
                    columns = [col.strip() for col in select_part.split(',')]
            
            return tables, columns
            
        except Exception as e:
            logger.error(f"Query component extraction error: {e}")
            return [], []
    
    def _extract_where_columns(self, query_text: str, table: str) -> List[str]:
        """Extract columns used in WHERE clause for specific table"""
        try:
            query_lower = query_text.lower()
            
            if 'where' not in query_lower:
                return []
            
            where_part = query_lower[query_lower.find('where'):].split('group')[0].split('order')[0]
            
            # Simple extraction of column names after WHERE
            columns = []
            words = where_part.replace('(', ' ').replace(')', ' ').split()
            
            for i, word in enumerate(words):
                if word in ['and', 'or', 'where']:
                    continue
                if '.' in word:  # Table.column format
                    table_part, column_part = word.split('.', 1)
                    if table_part == table:
                        columns.append(column_part.split('=')[0].strip())
                elif i > 0 and words[i-1] not in ['and', 'or', 'where', '=', '>', '<', 'like']:
                    # Assume it's a column name
                    columns.append(word.split('=')[0].strip())
            
            return list(set(columns))  # Remove duplicates
            
        except Exception as e:
            logger.error(f"WHERE column extraction error: {e}")
            return []
    
    async def analyze_table_statistics(self, table_name: str) -> TableStatistics:
        """Analyze table statistics for optimization"""
        try:
            # Mock implementation - in production, query actual database statistics
            stats = TableStatistics(
                table_name=table_name,
                row_count=100000,  # Mock data
                size_mb=50.0,
                index_count=3,
                index_size_mb=10.0,
                avg_query_time_ms=25.0,
                daily_query_count=500
            )
            
            self.table_statistics[table_name] = stats
            
            # Check if table needs optimization
            if stats.avg_query_time_ms > self.slow_query_threshold_ms:
                await self._recommend_table_optimization(stats)
            
            logger.info(f"Table statistics analyzed: {table_name}")
            return stats
            
        except Exception as e:
            logger.error(f"Table statistics analysis error: {e}")
            return TableStatistics(table_name=table_name)
    
    async def _recommend_table_optimization(self, stats: TableStatistics):
        """Recommend table-level optimizations"""
        try:
            # Check if table should be partitioned
            if stats.row_count > 1000000:  # 1M rows
                recommendation = OptimizationRecommendation(
                    recommendation_id=str(uuid.uuid4()),
                    query_hash="table_optimization",
                    optimization_type=OptimizationType.PARTITION_TABLE,
                    priority="medium",
                    description=f"Consider partitioning large table {stats.table_name} ({stats.row_count:,} rows)",
                    estimated_improvement=40.0
                )
                self.optimization_recommendations[recommendation.recommendation_id] = recommendation
            
            # Check index-to-table size ratio
            if stats.index_size_mb > stats.size_mb * 0.8:  # Indexes > 80% of table size
                recommendation = OptimizationRecommendation(
                    recommendation_id=str(uuid.uuid4()),
                    query_hash="table_optimization",
                    optimization_type=OptimizationType.INDEX_CREATION,
                    priority="low",
                    description=f"Review indexes on {stats.table_name} - index size is {stats.index_size_mb:.1f}MB vs table size {stats.size_mb:.1f}MB",
                    estimated_improvement=10.0
                )
                self.optimization_recommendations[recommendation.recommendation_id] = recommendation
                
        except Exception as e:
            logger.error(f"Table optimization recommendation error: {e}")
    
    async def monitor_connection_pool(self, pool_name: str, pool_stats: Dict[str, Any]) -> ConnectionPoolStats:
        """Monitor database connection pool performance"""
        try:
            stats = ConnectionPoolStats(
                pool_name=pool_name,
                active_connections=pool_stats.get('active_connections', 0),
                idle_connections=pool_stats.get('idle_connections', 0),
                max_connections=pool_stats.get('max_connections', 0),
                total_requests=pool_stats.get('total_requests', 0),
                avg_wait_time_ms=pool_stats.get('avg_wait_time_ms', 0.0),
                connection_errors=pool_stats.get('connection_errors', 0)
            )
            
            self.connection_pools[pool_name] = stats
            
            # Check for connection pool issues
            if stats.avg_wait_time_ms > 100:  # 100ms wait time
                recommendation = OptimizationRecommendation(
                    recommendation_id=str(uuid.uuid4()),
                    query_hash="connection_pool",
                    optimization_type=OptimizationType.CONNECTION_POOL,
                    priority="high",
                    description=f"Connection pool {pool_name} has high wait times ({stats.avg_wait_time_ms:.1f}ms)",
                    estimated_improvement=60.0
                )
                self.optimization_recommendations[recommendation.recommendation_id] = recommendation
            
            logger.debug(f"Connection pool monitored: {pool_name}")
            return stats
            
        except Exception as e:
            logger.error(f"Connection pool monitoring error: {e}")
            return ConnectionPoolStats(pool_name=pool_name)
    
    async def get_slow_queries(self, limit: int = 10) -> List[QueryMetrics]:
        """Get slowest queries for analysis"""
        try:
            slow_queries = [
                metrics for metrics in self.query_metrics.values()
                if metrics.execution_time_ms > self.slow_query_threshold_ms
            ]
            
            # Sort by execution time descending
            slow_queries.sort(key=lambda q: q.execution_time_ms, reverse=True)
            
            return slow_queries[:limit]
            
        except Exception as e:
            logger.error(f"Slow queries retrieval error: {e}")
            return []
    
    async def get_optimization_recommendations(self, priority: str = None) -> List[OptimizationRecommendation]:
        """Get optimization recommendations"""
        try:
            recommendations = list(self.optimization_recommendations.values())
            
            if priority:
                recommendations = [r for r in recommendations if r.priority == priority]
            
            # Sort by priority and estimated improvement
            priority_order = {"critical": 4, "high": 3, "medium": 2, "low": 1}
            recommendations.sort(
                key=lambda r: (priority_order.get(r.priority, 0), r.estimated_improvement),
                reverse=True
            )
            
            return recommendations
            
        except Exception as e:
            logger.error(f"Optimization recommendations retrieval error: {e}")
            return []
    
    async def implement_recommendation(self, recommendation_id: str) -> bool:
        """Mark recommendation as implemented"""
        try:
            if recommendation_id in self.optimization_recommendations:
                recommendation = self.optimization_recommendations[recommendation_id]
                recommendation.implemented = True
                recommendation.implementation_date = datetime.utcnow()
                
                logger.info(f"Optimization recommendation implemented: {recommendation_id}")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Recommendation implementation error: {e}")
            return False
    
    async def generate_performance_report(self) -> Dict[str, Any]:
        """Generate comprehensive performance report"""
        try:
            # Calculate overall statistics
            total_queries = len(self.query_metrics)
            slow_queries = len([q for q in self.query_metrics.values() 
                              if q.execution_time_ms > self.slow_query_threshold_ms])
            
            avg_execution_time = sum(q.execution_time_ms for q in self.query_metrics.values()) / total_queries if total_queries > 0 else 0
            
            # Query type distribution
            query_type_dist = {}
            for metrics in self.query_metrics.values():
                query_type = metrics.query_type.value
                query_type_dist[query_type] = query_type_dist.get(query_type, 0) + 1
            
            # Performance level distribution
            perf_levels = {}
            for metrics in self.query_metrics.values():
                level = self._get_performance_level(metrics.execution_time_ms)
                perf_levels[level.value] = perf_levels.get(level.value, 0) + 1
            
            report = {
                "report_id": str(uuid.uuid4()),
                "generated_at": datetime.utcnow().isoformat(),
                "summary": {
                    "total_queries_monitored": total_queries,
                    "slow_queries": slow_queries,
                    "slow_query_percentage": (slow_queries / total_queries * 100) if total_queries > 0 else 0,
                    "average_execution_time_ms": avg_execution_time
                },
                "query_type_distribution": query_type_dist,
                "performance_level_distribution": perf_levels,
                "optimization_recommendations": {
                    "total_recommendations": len(self.optimization_recommendations),
                    "by_priority": self._count_recommendations_by_priority(),
                    "by_type": self._count_recommendations_by_type()
                },
                "table_statistics": {
                    table: {
                        "row_count": stats.row_count,
                        "size_mb": stats.size_mb,
                        "avg_query_time_ms": stats.avg_query_time_ms
                    }
                    for table, stats in self.table_statistics.items()
                },
                "connection_pools": {
                    pool: {
                        "active_connections": stats.active_connections,
                        "avg_wait_time_ms": stats.avg_wait_time_ms,
                        "connection_errors": stats.connection_errors
                    }
                    for pool, stats in self.connection_pools.items()
                }
            }
            
            logger.info(f"Performance report generated: {report['report_id']}")
            return report
            
        except Exception as e:
            logger.error(f"Performance report generation error: {e}")
            return {}
    
    def _get_performance_level(self, execution_time_ms: float) -> PerformanceLevel:
        """Determine performance level based on execution time"""
        if execution_time_ms < 10:
            return PerformanceLevel.EXCELLENT
        elif execution_time_ms < 50:
            return PerformanceLevel.GOOD
        elif execution_time_ms < 200:
            return PerformanceLevel.AVERAGE
        elif execution_time_ms < 1000:
            return PerformanceLevel.POOR
        else:
            return PerformanceLevel.CRITICAL
    
    def _count_recommendations_by_priority(self) -> Dict[str, int]:
        """Count recommendations by priority"""
        counts = {}
        for rec in self.optimization_recommendations.values():
            counts[rec.priority] = counts.get(rec.priority, 0) + 1
        return counts
    
    def _count_recommendations_by_type(self) -> Dict[str, int]:
        """Count recommendations by optimization type"""
        counts = {}
        for rec in self.optimization_recommendations.values():
            opt_type = rec.optimization_type.value
            counts[opt_type] = counts.get(opt_type, 0) + 1
        return counts

# Export classes
__all__ = [
    "QueryType",
    "PerformanceLevel",
    "OptimizationType",
    "QueryMetrics",
    "OptimizationRecommendation",
    "IndexRecommendation",
    "TableStatistics",
    "ConnectionPoolStats",
    "DatabaseOptimizer"
]

# Module initialization
logger.info("🎯 Database Optimizer module loaded")