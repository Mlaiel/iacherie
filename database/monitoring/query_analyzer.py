"""
Advanced Query Analyzer

Intelligent SQL query analysis system with AI-powered optimization recommendations.
Analyzes query patterns, performance bottlenecks, and provides actionable insights.

Author: Fahed Mlaiel <mlaiel@live.de>
Project: IA Influencer Agent + Content Protection Platform
Copyright: All rights reserved. Unauthorized use, modification, or distribution prohibited.

⚠️  AVERTISSEMENT STRICT ⚠️
Toute utilisation, modification ou distribution non autorisée de ce code est strictement interdite.
Propriété intellectuelle de Fahed Mlaiel (mlaiel@live.de).
"""

import re
import hashlib
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Set, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import asyncio
import sqlparse
from sqlalchemy import text, inspect
from sqlalchemy.ext.asyncio import AsyncSession
import logging
from collections import defaultdict, Counter
import json

from ..core.database import get_database_session
from ..models.monitoring import QueryAnalysis, ExecutionPlan
from ...core.config import Settings
from ...utils.cache import RedisCache
from ...ai.analysis.query_optimization_ai import QueryOptimizationAI


class QueryType(Enum):
    """SQL query type classification"""
    SELECT = "select"
    INSERT = "insert"
    UPDATE = "update"
    DELETE = "delete"
    CREATE = "create"
    ALTER = "alter"
    DROP = "drop"
    INDEX = "index"
    TRANSACTION = "transaction"
    UNKNOWN = "unknown"


class OptimizationPriority(Enum):
    """Query optimization priority levels"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    NONE = "none"


@dataclass
class QueryPattern:
    """SQL query pattern analysis"""
    pattern_id: str
    normalized_query: str
    query_type: QueryType
    table_names: List[str]
    column_names: List[str]
    join_count: int
    subquery_count: int
    where_conditions: int
    order_by_columns: List[str]
    group_by_columns: List[str]
    has_aggregation: bool
    complexity_score: float
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        data = asdict(self)
        data['query_type'] = self.query_type.value
        return data


@dataclass
class QueryPerformanceMetrics:
    """Query performance metrics"""
    query_hash: str
    execution_count: int
    total_time_ms: float
    avg_time_ms: float
    min_time_ms: float
    max_time_ms: float
    rows_examined: int
    rows_returned: int
    buffer_pool_hits: int
    buffer_pool_misses: int
    disk_reads: int
    memory_usage_mb: float
    cpu_time_ms: float
    lock_wait_time_ms: float
    first_seen: datetime
    last_seen: datetime
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        data = asdict(self)
        data['first_seen'] = self.first_seen.isoformat()
        data['last_seen'] = self.last_seen.isoformat()
        return data


@dataclass
class OptimizationRecommendation:
    """Query optimization recommendation"""
    recommendation_id: str
    query_hash: str
    priority: OptimizationPriority
    category: str
    title: str
    description: str
    suggested_solution: str
    estimated_improvement: float
    implementation_effort: str
    code_example: Optional[str]
    confidence_score: float
    created_at: datetime
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        data = asdict(self)
        data['priority'] = self.priority.value
        data['created_at'] = self.created_at.isoformat()
        return data


class QueryAnalyzer:
    """
    Advanced SQL query analyzer with AI-powered optimization.
    
    Features:
    - Real-time query pattern recognition
    - Performance bottleneck identification
    - AI-powered optimization recommendations
    - Execution plan analysis
    - Index usage optimization
    - Query complexity scoring
    """
    
    def __init__(self, settings: Settings):
        self.settings = settings
        self.logger = logging.getLogger(__name__)
        self.cache = RedisCache()
        self.ai_optimizer = QueryOptimizationAI()
        
        # Query tracking
        self.query_patterns: Dict[str, QueryPattern] = {}
        self.performance_metrics: Dict[str, QueryPerformanceMetrics] = {}
        self.recommendations: Dict[str, List[OptimizationRecommendation]] = defaultdict(list)
        
        # Analysis configuration
        self.slow_query_threshold_ms = 1000
        self.frequent_query_threshold = 100
        self.analysis_window_hours = 24
        
        # Query normalization patterns
        self.normalization_patterns = [
            (r'\b\d+\b', 'N'),  # Numbers
            (r"'[^']*'", "'S'"),  # String literals
            (r'\s+', ' '),  # Multiple spaces
            (r'\(\s*\)', '()'),  # Empty parentheses
        ]
        
        self.logger.info("Query Analyzer initialized")
    
    async def analyze_query(
        self, 
        query: str, 
        execution_time_ms: float = None,
        rows_examined: int = None,
        rows_returned: int = None
    ) -> Dict[str, Any]:
        """
        Analyze a single SQL query
        
        Args:
            query: SQL query to analyze
            execution_time_ms: Query execution time
            rows_examined: Number of rows examined
            rows_returned: Number of rows returned
            
        Returns:
            Analysis results
        """
        try:
            # Parse and normalize query
            pattern = self._analyze_query_pattern(query)
            query_hash = self._get_query_hash(pattern.normalized_query)
            
            # Update performance metrics
            if execution_time_ms is not None:
                await self._update_performance_metrics(
                    query_hash, execution_time_ms, rows_examined, rows_returned
                )
            
            # Store pattern
            self.query_patterns[query_hash] = pattern
            
            # Cache analysis
            analysis_result = {
                "query_hash": query_hash,
                "pattern": pattern.to_dict(),
                "performance": None,
                "recommendations": []
            }
            
            # Get performance metrics if available
            if query_hash in self.performance_metrics:
                analysis_result["performance"] = self.performance_metrics[query_hash].to_dict()
            
            # Get optimization recommendations
            if query_hash in self.recommendations:
                analysis_result["recommendations"] = [
                    rec.to_dict() for rec in self.recommendations[query_hash]
                ]
            
            # Cache result
            await self.cache.set(
                f"query_analysis:{query_hash}",
                json.dumps(analysis_result),
                expire=3600
            )
            
            return analysis_result
            
        except Exception as e:
            self.logger.error(f"Query analysis error: {e}")
            return {"error": str(e)}
    
    def _analyze_query_pattern(self, query: str) -> QueryPattern:
        """Analyze SQL query pattern"""
        try:
            # Parse SQL
            parsed = sqlparse.parse(query)[0]
            normalized = self._normalize_query(query)
            
            # Extract basic information
            query_type = self._get_query_type(query)
            table_names = self._extract_table_names(parsed)
            column_names = self._extract_column_names(parsed)
            
            # Analyze structure
            join_count = self._count_joins(query)
            subquery_count = self._count_subqueries(query)
            where_conditions = self._count_where_conditions(query)
            order_by_columns = self._extract_order_by_columns(parsed)
            group_by_columns = self._extract_group_by_columns(parsed)
            has_aggregation = self._has_aggregation_functions(query)
            
            # Calculate complexity score
            complexity_score = self._calculate_complexity_score(
                join_count, subquery_count, where_conditions, 
                len(table_names), has_aggregation
            )
            
            pattern_id = self._get_query_hash(normalized)
            
            return QueryPattern(
                pattern_id=pattern_id,
                normalized_query=normalized,
                query_type=query_type,
                table_names=table_names,
                column_names=column_names,
                join_count=join_count,
                subquery_count=subquery_count,
                where_conditions=where_conditions,
                order_by_columns=order_by_columns,
                group_by_columns=group_by_columns,
                has_aggregation=has_aggregation,
                complexity_score=complexity_score
            )
            
        except Exception as e:
            self.logger.error(f"Pattern analysis error: {e}")
            # Return basic pattern on error
            return QueryPattern(
                pattern_id=self._get_query_hash(query),
                normalized_query=query,
                query_type=QueryType.UNKNOWN,
                table_names=[],
                column_names=[],
                join_count=0,
                subquery_count=0,
                where_conditions=0,
                order_by_columns=[],
                group_by_columns=[],
                has_aggregation=False,
                complexity_score=1.0
            )
    
    def _normalize_query(self, query: str) -> str:
        """Normalize SQL query for pattern matching"""
        normalized = query.strip().upper()
        
        # Apply normalization patterns
        for pattern, replacement in self.normalization_patterns:
            normalized = re.sub(pattern, replacement, normalized)
        
        return normalized
    
    def _get_query_type(self, query: str) -> QueryType:
        """Determine SQL query type"""
        query_upper = query.strip().upper()
        
        if query_upper.startswith('SELECT'):
            return QueryType.SELECT
        elif query_upper.startswith('INSERT'):
            return QueryType.INSERT
        elif query_upper.startswith('UPDATE'):
            return QueryType.UPDATE
        elif query_upper.startswith('DELETE'):
            return QueryType.DELETE
        elif query_upper.startswith('CREATE'):
            return QueryType.CREATE
        elif query_upper.startswith('ALTER'):
            return QueryType.ALTER
        elif query_upper.startswith('DROP'):
            return QueryType.DROP
        elif 'INDEX' in query_upper:
            return QueryType.INDEX
        elif any(keyword in query_upper for keyword in ['BEGIN', 'COMMIT', 'ROLLBACK']):
            return QueryType.TRANSACTION
        else:
            return QueryType.UNKNOWN
    
    def _extract_table_names(self, parsed) -> List[str]:
        """Extract table names from parsed SQL"""
        table_names = []
        
        def extract_from_token(token):
            if token.ttype is None and hasattr(token, 'tokens'):
                for sub_token in token.tokens:
                    extract_from_token(sub_token)
            elif token.ttype in (sqlparse.tokens.Name, sqlparse.tokens.Name.Builtin):
                # Simple heuristic to identify table names
                if not token.value.upper() in ['SELECT', 'FROM', 'WHERE', 'JOIN', 'ON', 'AND', 'OR']:
                    table_names.append(token.value)
        
        try:
            for token in parsed.tokens:
                extract_from_token(token)
        except Exception:
            pass
        
        return list(set(table_names))  # Remove duplicates
    
    def _extract_column_names(self, parsed) -> List[str]:
        """Extract column names from parsed SQL"""
        # Simplified column extraction
        column_names = []
        try:
            query_str = str(parsed)
            # Look for common column patterns
            patterns = [
                r'\bSELECT\s+(.*?)\s+FROM',
                r'\bWHERE\s+(\w+)',
                r'\bORDER\s+BY\s+(.*?)(?:\s|$)',
                r'\bGROUP\s+BY\s+(.*?)(?:\s|$)'
            ]
            
            for pattern in patterns:
                matches = re.findall(pattern, query_str, re.IGNORECASE)
                for match in matches:
                    if isinstance(match, str):
                        cols = [col.strip() for col in match.split(',')]
                        column_names.extend(cols)
        except Exception:
            pass
        
        return list(set(column_names))
    
    def _count_joins(self, query: str) -> int:
        """Count JOIN operations in query"""
        join_pattern = r'\b(?:INNER\s+|LEFT\s+|RIGHT\s+|FULL\s+)?JOIN\b'
        return len(re.findall(join_pattern, query, re.IGNORECASE))
    
    def _count_subqueries(self, query: str) -> int:
        """Count subqueries in query"""
        # Count SELECT statements (main query + subqueries)
        select_count = len(re.findall(r'\bSELECT\b', query, re.IGNORECASE))
        return max(0, select_count - 1)  # Subtract main query
    
    def _count_where_conditions(self, query: str) -> int:
        """Count WHERE conditions"""
        where_match = re.search(r'\bWHERE\s+(.*?)(?:\s+ORDER\s+BY|\s+GROUP\s+BY|\s+LIMIT|$)', 
                               query, re.IGNORECASE | re.DOTALL)
        if where_match:
            where_clause = where_match.group(1)
            # Count AND/OR operators as separators
            and_count = len(re.findall(r'\bAND\b', where_clause, re.IGNORECASE))
            or_count = len(re.findall(r'\bOR\b', where_clause, re.IGNORECASE))
            return and_count + or_count + 1  # +1 for the first condition
        return 0
    
    def _extract_order_by_columns(self, parsed) -> List[str]:
        """Extract ORDER BY columns"""
        try:
            query_str = str(parsed)
            order_match = re.search(r'\bORDER\s+BY\s+(.*?)(?:\s+LIMIT|$)', 
                                   query_str, re.IGNORECASE)
            if order_match:
                order_clause = order_match.group(1)
                columns = [col.strip().split()[0] for col in order_clause.split(',')]
                return columns
        except Exception:
            pass
        return []
    
    def _extract_group_by_columns(self, parsed) -> List[str]:
        """Extract GROUP BY columns"""
        try:
            query_str = str(parsed)
            group_match = re.search(r'\bGROUP\s+BY\s+(.*?)(?:\s+ORDER\s+BY|\s+LIMIT|$)', 
                                   query_str, re.IGNORECASE)
            if group_match:
                group_clause = group_match.group(1)
                columns = [col.strip() for col in group_clause.split(',')]
                return columns
        except Exception:
            pass
        return []
    
    def _has_aggregation_functions(self, query: str) -> bool:
        """Check if query has aggregation functions"""
        agg_functions = ['COUNT', 'SUM', 'AVG', 'MAX', 'MIN', 'GROUP_CONCAT']
        pattern = r'\b(?:' + '|'.join(agg_functions) + r')\s*\('
        return bool(re.search(pattern, query, re.IGNORECASE))
    
    def _calculate_complexity_score(
        self, 
        join_count: int, 
        subquery_count: int, 
        where_conditions: int,
        table_count: int,
        has_aggregation: bool
    ) -> float:
        """Calculate query complexity score (0-10)"""
        score = 1.0  # Base score
        
        # Add complexity factors
        score += join_count * 0.5
        score += subquery_count * 1.0
        score += where_conditions * 0.2
        score += table_count * 0.3
        
        if has_aggregation:
            score += 0.5
        
        return min(score, 10.0)  # Cap at 10
    
    def _get_query_hash(self, query: str) -> str:
        """Generate hash for query"""
        return hashlib.md5(query.encode()).hexdigest()
    
    async def _update_performance_metrics(
        self,
        query_hash: str,
        execution_time_ms: float,
        rows_examined: int = None,
        rows_returned: int = None
    ) -> None:
        """Update performance metrics for query"""
        try:
            now = datetime.utcnow()
            
            if query_hash in self.performance_metrics:
                metrics = self.performance_metrics[query_hash]
                
                # Update existing metrics
                metrics.execution_count += 1
                metrics.total_time_ms += execution_time_ms
                metrics.avg_time_ms = metrics.total_time_ms / metrics.execution_count
                metrics.min_time_ms = min(metrics.min_time_ms, execution_time_ms)
                metrics.max_time_ms = max(metrics.max_time_ms, execution_time_ms)
                metrics.last_seen = now
                
                if rows_examined is not None:
                    metrics.rows_examined += rows_examined
                if rows_returned is not None:
                    metrics.rows_returned += rows_returned
            else:
                # Create new metrics
                self.performance_metrics[query_hash] = QueryPerformanceMetrics(
                    query_hash=query_hash,
                    execution_count=1,
                    total_time_ms=execution_time_ms,
                    avg_time_ms=execution_time_ms,
                    min_time_ms=execution_time_ms,
                    max_time_ms=execution_time_ms,
                    rows_examined=rows_examined or 0,
                    rows_returned=rows_returned or 0,
                    buffer_pool_hits=0,
                    buffer_pool_misses=0,
                    disk_reads=0,
                    memory_usage_mb=0.0,
                    cpu_time_ms=0.0,
                    lock_wait_time_ms=0.0,
                    first_seen=now,
                    last_seen=now
                )
            
            # Generate recommendations for slow or frequent queries
            metrics = self.performance_metrics[query_hash]
            if (metrics.avg_time_ms > self.slow_query_threshold_ms or 
                metrics.execution_count > self.frequent_query_threshold):
                await self._generate_optimization_recommendations(query_hash)
                
        except Exception as e:
            self.logger.error(f"Error updating performance metrics: {e}")
    
    async def _generate_optimization_recommendations(self, query_hash: str) -> None:
        """Generate optimization recommendations for query"""
        try:
            if query_hash not in self.query_patterns:
                return
            
            pattern = self.query_patterns[query_hash]
            metrics = self.performance_metrics.get(query_hash)
            
            recommendations = []
            
            # High execution time recommendations
            if metrics and metrics.avg_time_ms > self.slow_query_threshold_ms:
                if pattern.join_count > 2:
                    recommendations.append(OptimizationRecommendation(
                        recommendation_id=f"join_opt_{query_hash}_{int(time.time())}",
                        query_hash=query_hash,
                        priority=OptimizationPriority.HIGH,
                        category="JOIN Optimization",
                        title="Optimize Multiple JOIN Operations",
                        description=f"Query has {pattern.join_count} JOINs which may impact performance",
                        suggested_solution="Consider denormalizing frequently joined tables or using materialized views",
                        estimated_improvement=30.0,
                        implementation_effort="Medium",
                        code_example="CREATE MATERIALIZED VIEW optimized_view AS ...",
                        confidence_score=0.8,
                        created_at=datetime.utcnow()
                    ))
                
                if not pattern.order_by_columns and pattern.query_type == QueryType.SELECT:
                    recommendations.append(OptimizationRecommendation(
                        recommendation_id=f"index_missing_{query_hash}_{int(time.time())}",
                        query_hash=query_hash,
                        priority=OptimizationPriority.MEDIUM,
                        category="Index Optimization",
                        title="Add Indexes for WHERE Conditions",
                        description="Query may benefit from indexes on filtered columns",
                        suggested_solution="Create composite indexes on WHERE clause columns",
                        estimated_improvement=50.0,
                        implementation_effort="Low",
                        code_example="CREATE INDEX idx_table_columns ON table (col1, col2);",
                        confidence_score=0.9,
                        created_at=datetime.utcnow()
                    ))
            
            # High frequency recommendations
            if metrics and metrics.execution_count > self.frequent_query_threshold:
                recommendations.append(OptimizationRecommendation(
                    recommendation_id=f"cache_freq_{query_hash}_{int(time.time())}",
                    query_hash=query_hash,
                    priority=OptimizationPriority.MEDIUM,
                    category="Caching",
                    title="Cache Frequent Query Results",
                    description=f"Query executed {metrics.execution_count} times, consider caching",
                    suggested_solution="Implement application-level caching for this query pattern",
                    estimated_improvement=60.0,
                    implementation_effort="Medium",
                    code_example="@cache(expire=300)\ndef get_cached_result():",
                    confidence_score=0.7,
                    created_at=datetime.utcnow()
                ))
            
            # Store recommendations
            if recommendations:
                self.recommendations[query_hash] = recommendations
                
                # Cache recommendations
                await self.cache.set(
                    f"recommendations:{query_hash}",
                    json.dumps([rec.to_dict() for rec in recommendations]),
                    expire=86400
                )
            
        except Exception as e:
            self.logger.error(f"Error generating recommendations: {e}")
    
    async def get_slow_queries(self, limit: int = 20) -> List[Dict[str, Any]]:
        """Get slowest queries"""
        try:
            # Sort by average execution time
            sorted_queries = sorted(
                self.performance_metrics.items(),
                key=lambda x: x[1].avg_time_ms,
                reverse=True
            )
            
            results = []
            for query_hash, metrics in sorted_queries[:limit]:
                pattern = self.query_patterns.get(query_hash)
                recommendations = self.recommendations.get(query_hash, [])
                
                results.append({
                    "query_hash": query_hash,
                    "pattern": pattern.to_dict() if pattern else None,
                    "metrics": metrics.to_dict(),
                    "recommendations_count": len(recommendations)
                })
            
            return results
            
        except Exception as e:
            self.logger.error(f"Error getting slow queries: {e}")
            return []
    
    async def get_frequent_queries(self, limit: int = 20) -> List[Dict[str, Any]]:
        """Get most frequently executed queries"""
        try:
            # Sort by execution count
            sorted_queries = sorted(
                self.performance_metrics.items(),
                key=lambda x: x[1].execution_count,
                reverse=True
            )
            
            results = []
            for query_hash, metrics in sorted_queries[:limit]:
                pattern = self.query_patterns.get(query_hash)
                recommendations = self.recommendations.get(query_hash, [])
                
                results.append({
                    "query_hash": query_hash,
                    "pattern": pattern.to_dict() if pattern else None,
                    "metrics": metrics.to_dict(),
                    "recommendations_count": len(recommendations)
                })
            
            return results
            
        except Exception as e:
            self.logger.error(f"Error getting frequent queries: {e}")
            return []
    
    async def get_optimization_recommendations(
        self, 
        priority: OptimizationPriority = None
    ) -> List[Dict[str, Any]]:
        """Get optimization recommendations"""
        try:
            all_recommendations = []
            
            for query_hash, recommendations in self.recommendations.items():
                for rec in recommendations:
                    if priority is None or rec.priority == priority:
                        all_recommendations.append(rec.to_dict())
            
            # Sort by priority and confidence
            priority_order = {
                OptimizationPriority.CRITICAL: 4,
                OptimizationPriority.HIGH: 3,
                OptimizationPriority.MEDIUM: 2,
                OptimizationPriority.LOW: 1,
                OptimizationPriority.NONE: 0
            }
            
            all_recommendations.sort(
                key=lambda x: (
                    priority_order.get(OptimizationPriority(x['priority']), 0),
                    x['confidence_score']
                ),
                reverse=True
            )
            
            return all_recommendations
            
        except Exception as e:
            self.logger.error(f"Error getting optimization recommendations: {e}")
            return []
    
    async def analyze_execution_plan(
        self, 
        query: str, 
        session: AsyncSession
    ) -> Dict[str, Any]:
        """Analyze query execution plan"""
        try:
            # Get execution plan
            plan_query = f"EXPLAIN (ANALYZE, BUFFERS, FORMAT JSON) {query}"
            result = await session.execute(text(plan_query))
            plan_data = result.scalar()
            
            if not plan_data:
                return {"error": "No execution plan available"}
            
            # Analyze plan
            analysis = {
                "execution_plan": plan_data,
                "total_cost": self._extract_total_cost(plan_data),
                "scan_types": self._analyze_scan_types(plan_data),
                "index_usage": self._analyze_index_usage(plan_data),
                "join_methods": self._analyze_join_methods(plan_data),
                "bottlenecks": self._identify_bottlenecks(plan_data),
                "optimization_suggestions": self._suggest_plan_optimizations(plan_data)
            }
            
            return analysis
            
        except Exception as e:
            self.logger.error(f"Error analyzing execution plan: {e}")
            return {"error": str(e)}
    
    def _extract_total_cost(self, plan_data: List[Dict]) -> float:
        """Extract total cost from execution plan"""
        try:
            if plan_data and len(plan_data) > 0:
                return plan_data[0].get("Plan", {}).get("Total Cost", 0.0)
        except Exception:
            pass
        return 0.0
    
    def _analyze_scan_types(self, plan_data: List[Dict]) -> Dict[str, int]:
        """Analyze scan types in execution plan"""
        scan_types = defaultdict(int)
        
        def analyze_node(node):
            if isinstance(node, dict):
                node_type = node.get("Node Type", "")
                if "Scan" in node_type:
                    scan_types[node_type] += 1
                
                # Recurse into child plans
                for plan in node.get("Plans", []):
                    analyze_node(plan)
        
        try:
            if plan_data and len(plan_data) > 0:
                analyze_node(plan_data[0].get("Plan", {}))
        except Exception:
            pass
        
        return dict(scan_types)
    
    def _analyze_index_usage(self, plan_data: List[Dict]) -> Dict[str, Any]:
        """Analyze index usage in execution plan"""
        index_info = {
            "indexes_used": [],
            "sequential_scans": 0,
            "index_scans": 0
        }
        
        def analyze_node(node):
            if isinstance(node, dict):
                node_type = node.get("Node Type", "")
                
                if node_type == "Index Scan":
                    index_info["index_scans"] += 1
                    index_name = node.get("Index Name", "")
                    if index_name:
                        index_info["indexes_used"].append(index_name)
                elif node_type == "Seq Scan":
                    index_info["sequential_scans"] += 1
                
                # Recurse into child plans
                for plan in node.get("Plans", []):
                    analyze_node(plan)
        
        try:
            if plan_data and len(plan_data) > 0:
                analyze_node(plan_data[0].get("Plan", {}))
        except Exception:
            pass
        
        return index_info
    
    def _analyze_join_methods(self, plan_data: List[Dict]) -> Dict[str, int]:
        """Analyze join methods in execution plan"""
        join_methods = defaultdict(int)
        
        def analyze_node(node):
            if isinstance(node, dict):
                node_type = node.get("Node Type", "")
                if "Join" in node_type:
                    join_methods[node_type] += 1
                
                # Recurse into child plans
                for plan in node.get("Plans", []):
                    analyze_node(plan)
        
        try:
            if plan_data and len(plan_data) > 0:
                analyze_node(plan_data[0].get("Plan", {}))
        except Exception:
            pass
        
        return dict(join_methods)
    
    def _identify_bottlenecks(self, plan_data: List[Dict]) -> List[Dict[str, Any]]:
        """Identify performance bottlenecks in execution plan"""
        bottlenecks = []
        
        def analyze_node(node, path=""):
            if isinstance(node, dict):
                node_type = node.get("Node Type", "")
                actual_time = node.get("Actual Total Time", 0)
                startup_cost = node.get("Startup Cost", 0)
                total_cost = node.get("Total Cost", 0)
                
                # Identify expensive operations
                if actual_time > 100:  # > 100ms
                    bottlenecks.append({
                        "path": path,
                        "node_type": node_type,
                        "actual_time_ms": actual_time,
                        "cost": total_cost,
                        "issue": "High execution time"
                    })
                
                if node_type == "Seq Scan":
                    bottlenecks.append({
                        "path": path,
                        "node_type": node_type,
                        "relation": node.get("Relation Name", ""),
                        "issue": "Sequential scan detected"
                    })
                
                # Recurse into child plans
                for i, plan in enumerate(node.get("Plans", [])):
                    analyze_node(plan, f"{path}.{i}")
        
        try:
            if plan_data and len(plan_data) > 0:
                analyze_node(plan_data[0].get("Plan", {}))
        except Exception:
            pass
        
        return bottlenecks
    
    def _suggest_plan_optimizations(self, plan_data: List[Dict]) -> List[str]:
        """Suggest optimizations based on execution plan"""
        suggestions = []
        
        try:
            if plan_data and len(plan_data) > 0:
                plan = plan_data[0].get("Plan", {})
                
                # Check for sequential scans
                scan_types = self._analyze_scan_types(plan_data)
                if scan_types.get("Seq Scan", 0) > 0:
                    suggestions.append("Consider adding indexes to eliminate sequential scans")
                
                # Check for nested loops with high cost
                if scan_types.get("Nested Loop", 0) > 0:
                    suggestions.append("Review nested loop joins, consider hash or merge joins")
                
                # Check for sorts
                if "Sort" in str(plan_data):
                    suggestions.append("Consider adding indexes for ORDER BY clauses")
                
                # Check total cost
                total_cost = self._extract_total_cost(plan_data)
                if total_cost > 1000:
                    suggestions.append("High query cost detected, review overall query structure")
        
        except Exception:
            pass
        
        return suggestions
