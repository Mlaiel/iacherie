#!/usr/bin/env python3
"""
🗄️ DATABASE PERFORMANCE OPTIMIZER
=================================

High-performance database optimization framework applied by DBA Expert.

Author: DBA Expert
Created: 2025-09-23
"""

import time
import logging
from typing import Dict, List, Any, Optional, Union
from contextlib import contextmanager
from dataclasses import dataclass
import threading
from collections import defaultdict


@dataclass
class QueryMetrics:
    """Query performance metrics"""
    query_hash: str
    execution_time: float
    rows_affected: int
    timestamp: str
    database_name: str


class DatabaseConnectionPool:
    """Optimized database connection pool"""
    
    def __init__(self, max_connections: int = 20, min_connections: int = 5):
        self.max_connections = max_connections
        self.min_connections = min_connections
        self.connections = []
        self.in_use = set()
        self.lock = threading.Lock()
        self.logger = logging.getLogger(self.__class__.__name__)
    
    @contextmanager
    def get_connection(self):
        """Get optimized database connection"""
        connection = self._acquire_connection()
        try:
            yield connection
        finally:
            self._release_connection(connection)
    
    def _acquire_connection(self):
        """Acquire connection from pool"""
        with self.lock:
            if self.connections:
                conn = self.connections.pop()
                self.in_use.add(conn)
                return conn
            elif len(self.in_use) < self.max_connections:
                conn = self._create_connection()
                self.in_use.add(conn)
                return conn
            else:
                raise Exception("Connection pool exhausted")
    
    def _release_connection(self, connection):
        """Release connection back to pool"""
        with self.lock:
            if connection in self.in_use:
                self.in_use.remove(connection)
                self.connections.append(connection)
    
    def _create_connection(self):
        """Create new database connection"""
        return {"connection_id": time.time(), "active": True}


class QueryOptimizer:
    """Database query optimization engine"""
    
    def __init__(self):
        self.query_cache = {}
        self.performance_stats = defaultdict(list)
        self.logger = logging.getLogger(self.__class__.__name__)
    
    def optimize_query(self, sql: str, params: Dict[str, Any] = None) -> str:
        """Optimize SQL query for performance"""
        # Remove extra whitespace
        optimized_sql = ' '.join(sql.split())
        
        # Add LIMIT if missing and not already present
        if 'SELECT' in optimized_sql.upper() and 'LIMIT' not in optimized_sql.upper():
            if 'ORDER BY' in optimized_sql.upper():
                optimized_sql += ' LIMIT 1000'
            else:
                optimized_sql += ' LIMIT 1000'
        
        # Add index hints for large tables
        if 'FROM' in optimized_sql.upper():
            # Suggest index usage
            optimized_sql = f"/* Use indexes for better performance */ {optimized_sql}"
        
        return optimized_sql
    
    def execute_with_metrics(self, sql: str, params: Dict[str, Any] = None) -> QueryMetrics:
        """Execute query with performance monitoring"""
        query_hash = str(hash(sql))
        
        start_time = time.time()
        
        # Simulate query execution
        time.sleep(0.001)  # Simulate execution time
        rows_affected = 1  # Simulate result
        
        execution_time = time.time() - start_time
        
        metrics = QueryMetrics(
            query_hash=query_hash,
            execution_time=execution_time,
            rows_affected=rows_affected,
            timestamp=time.strftime('%Y-%m-%d %H:%M:%S'),
            database_name="ainfluencer_db"
        )
        
        self.performance_stats[query_hash].append(metrics)
        
        # Alert for slow queries
        if execution_time > 1.0:
            self.logger.warning(f"Slow query detected: {execution_time:.4f}s")
        
        return metrics
    
    def get_slow_queries(self, threshold: float = 0.5) -> List[QueryMetrics]:
        """Get queries slower than threshold"""
        slow_queries = []
        
        for query_hash, metrics_list in self.performance_stats.items():
            avg_time = sum(m.execution_time for m in metrics_list) / len(metrics_list)
            if avg_time > threshold:
                slow_queries.extend(metrics_list)
        
        return sorted(slow_queries, key=lambda x: x.execution_time, reverse=True)
    
    def suggest_indexes(self, table_name: str, columns: List[str]) -> List[str]:
        """Suggest database indexes for performance"""
        suggestions = []
        
        # Single column indexes
        for col in columns:
            suggestions.append(f"CREATE INDEX idx_{table_name}_{col} ON {table_name}({col});")
        
        # Composite indexes for common combinations
        if len(columns) > 1:
            composite_cols = '_'.join(columns[:3])  # Max 3 columns
            suggestions.append(f"CREATE INDEX idx_{table_name}_{composite_cols} ON {table_name}({', '.join(columns[:3])});")
        
        return suggestions


class DatabasePerformanceMonitor:
    """Monitor database performance in real-time"""
    
    def __init__(self):
        self.metrics = defaultdict(list)
        self.alerts = []
        self.logger = logging.getLogger(self.__class__.__name__)
    
    def log_query_performance(self, metrics: QueryMetrics) -> None:
        """Log query performance metrics"""
        self.metrics['execution_times'].append(metrics.execution_time)
        self.metrics['timestamps'].append(metrics.timestamp)
        
        # Check for performance degradation
        if len(self.metrics['execution_times']) > 100:
            recent_avg = sum(self.metrics['execution_times'][-50:]) / 50
            overall_avg = sum(self.metrics['execution_times']) / len(self.metrics['execution_times'])
            
            if recent_avg > overall_avg * 1.3:
                alert = {
                    'type': 'performance_degradation',
                    'message': f'Query performance degraded: {recent_avg:.4f}s vs {overall_avg:.4f}s',
                    'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
                }
                self.alerts.append(alert)
                self.logger.warning(alert['message'])
    
    def get_performance_report(self) -> Dict[str, Any]:
        """Generate comprehensive performance report"""
        if not self.metrics['execution_times']:
            return {"status": "No performance data available"}
        
        execution_times = self.metrics['execution_times']
        
        return {
            "total_queries": len(execution_times),
            "avg_execution_time": sum(execution_times) / len(execution_times),
            "max_execution_time": max(execution_times),
            "min_execution_time": min(execution_times),
            "slow_queries_count": len([t for t in execution_times if t > 1.0]),
            "recent_alerts": self.alerts[-10:],  # Last 10 alerts
            "performance_trend": "improving" if len(execution_times) > 50 and 
                               sum(execution_times[-25:]) < sum(execution_times[-50:-25]) else "stable"
        }


class DatabaseSecurityHardening:
    """Database security hardening utilities"""
    
    @staticmethod
    def validate_query_safety(sql: str) -> Dict[str, Any]:
        """Validate query for security risks"""
        risks = []
        
        # Check for SQL injection patterns
        dangerous_patterns = [
            r";\s*DROP\s+TABLE",
            r";\s*DELETE\s+FROM",
            r"UNION\s+SELECT",
            r"'\s*OR\s+'1'\s*=\s*'1",
        ]
        
        for pattern in dangerous_patterns:
            if re.search(pattern, sql, re.IGNORECASE):
                risks.append(f"Potential SQL injection: {pattern}")
        
        # Check for unparameterized queries
        if "'" in sql and "?" not in sql and "%" not in sql:
            risks.append("Unparameterized query detected")
        
        return {
            "safe": len(risks) == 0,
            "risks": risks,
            "security_score": max(0, 100 - len(risks) * 25)
        }
    
    @staticmethod
    def suggest_security_improvements(table_schema: Dict[str, Any]) -> List[str]:
        """Suggest security improvements for database schema"""
        suggestions = []
        
        # Check for encryption
        for column, properties in table_schema.items():
            if 'password' in column.lower() or 'secret' in column.lower():
                suggestions.append(f"Encrypt sensitive column: {column}")
            
            if 'email' in column.lower():
                suggestions.append(f"Consider hashing or encryption for PII: {column}")
        
        # General security suggestions
        suggestions.extend([
            "Implement row-level security (RLS)",
            "Use database connection encryption (SSL/TLS)",
            "Enable query logging for audit trails",
            "Implement backup encryption",
            "Use dedicated database users with minimal privileges"
        ])
        
        return suggestions


# Factory functions
def create_connection_pool(max_connections: int = 20) -> DatabaseConnectionPool:
    """Create optimized connection pool"""
    return DatabaseConnectionPool(max_connections=max_connections)

def create_query_optimizer() -> QueryOptimizer:
    """Create query optimizer"""
    return QueryOptimizer()

def create_performance_monitor() -> DatabasePerformanceMonitor:
    """Create performance monitor"""
    return DatabasePerformanceMonitor()
