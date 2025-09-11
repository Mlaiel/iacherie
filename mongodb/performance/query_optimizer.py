"""MongoDB Query Optimizer
=========================

Intelligent query optimization and execution planning for MongoDB operations.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel - All Rights Reserved
"""

import logging
import time
from typing import Dict, Any, List, Optional, Union
from dataclasses import dataclass
from pymongo import MongoClient
from pymongo.collection import Collection
from pymongo.cursor import Cursor

logger = logging.getLogger(__name__)

@dataclass
class QueryPlan:
    """Query execution plan information."""
    query: Dict[str, Any]
    collection_name: str
    execution_time_ms: float
    documents_examined: int
    documents_returned: int
    index_used: Optional[str]
    optimization_score: float
    recommendations: List[str]

@dataclass
class IndexRecommendation:
    """Index recommendation for query optimization."""
    collection_name: str
    fields: List[str]
    index_type: str  # compound, single, text, geospatial
    estimated_impact: float
    priority: int  # 1-5, 5 being highest

class QueryOptimizer:
    """Advanced MongoDB query optimizer with machine learning insights."""
    
    def __init__(self, client: MongoClient):
        """Initialize query optimizer.
        
        Args:
            client: MongoDB client instance
        """
        self.client = client
        self._query_history: List[QueryPlan] = []
        self._index_recommendations: List[IndexRecommendation] = []
        self._optimization_cache: Dict[str, QueryPlan] = {}
        
    def analyze_query(self, collection: Collection, query: Dict[str, Any], 
                     projection: Optional[Dict[str, Any]] = None) -> QueryPlan:
        """Analyze query performance and generate optimization recommendations.
        
        Args:
            collection: MongoDB collection
            query: Query document
            projection: Optional projection document
            
        Returns:
            QueryPlan with optimization analysis
        """
        start_time = time.time()
        
        # Execute explain() to get query plan
        explain_result = collection.find(query, projection or {}).explain('executionStats')
        execution_time = (time.time() - start_time) * 1000  # Convert to ms
        
        # Extract execution statistics
        exec_stats = explain_result.get('executionStats', {})
        docs_examined = exec_stats.get('totalDocsExamined', 0)
        docs_returned = exec_stats.get('totalDocsReturned', 0)
        
        # Determine index usage
        winning_plan = explain_result.get('queryPlanner', {}).get('winningPlan', {})
        index_used = self._extract_index_name(winning_plan)
        
        # Calculate optimization score (0-100)
        optimization_score = self._calculate_optimization_score(
            docs_examined, docs_returned, execution_time, index_used
        )
        
        # Generate recommendations
        recommendations = self._generate_recommendations(
            collection.name, query, docs_examined, docs_returned, index_used
        )
        
        query_plan = QueryPlan(
            query=query,
            collection_name=collection.name,
            execution_time_ms=execution_time,
            documents_examined=docs_examined,
            documents_returned=docs_returned,
            index_used=index_used,
            optimization_score=optimization_score,
            recommendations=recommendations
        )
        
        # Store in history and cache
        self._query_history.append(query_plan)
        query_hash = self._hash_query(query)
        self._optimization_cache[query_hash] = query_plan
        
        logger.info(f"Query analyzed: {optimization_score:.1f}% optimized, "
                   f"{execution_time:.2f}ms execution time")
        
        return query_plan
    
    def optimize_query(self, collection: Collection, query: Dict[str, Any]) -> Dict[str, Any]:
        """Optimize query structure for better performance.
        
        Args:
            collection: MongoDB collection
            query: Original query document
            
        Returns:
            Optimized query document
        """
        optimized_query = query.copy()
        
        # Reorder query fields for optimal index usage
        optimized_query = self._reorder_query_fields(collection, optimized_query)
        
        # Convert inefficient regex to index-friendly patterns
        optimized_query = self._optimize_regex_queries(optimized_query)
        
        # Optimize range queries
        optimized_query = self._optimize_range_queries(optimized_query)
        
        # Add query hints if beneficial
        hints = self._generate_query_hints(collection, optimized_query)
        
        logger.debug(f"Query optimized: {len(hints)} hints generated")
        
        return optimized_query
    
    def recommend_indexes(self, collection_name: str, 
                         min_priority: int = 3) -> List[IndexRecommendation]:
        """Generate index recommendations based on query patterns.
        
        Args:
            collection_name: Name of collection to analyze
            min_priority: Minimum priority level (1-5)
            
        Returns:
            List of index recommendations
        """
        # Analyze query patterns for this collection
        collection_queries = [
            qp for qp in self._query_history 
            if qp.collection_name == collection_name
        ]
        
        if not collection_queries:
            return []
        
        # Group queries by field patterns
        field_patterns = self._analyze_field_patterns(collection_queries)
        
        # Generate index recommendations
        recommendations = []
        for pattern, queries in field_patterns.items():
            recommendation = self._create_index_recommendation(
                collection_name, pattern, queries
            )
            if recommendation.priority >= min_priority:
                recommendations.append(recommendation)
        
        # Sort by priority and estimated impact
        recommendations.sort(key=lambda x: (x.priority, x.estimated_impact), reverse=True)
        
        logger.info(f"Generated {len(recommendations)} index recommendations "
                   f"for collection '{collection_name}'")
        
        return recommendations
    
    def get_slow_queries(self, threshold_ms: float = 100) -> List[QueryPlan]:
        """Get queries that exceed performance threshold.
        
        Args:
            threshold_ms: Execution time threshold in milliseconds
            
        Returns:
            List of slow queries
        """
        slow_queries = [
            qp for qp in self._query_history 
            if qp.execution_time_ms > threshold_ms
        ]
        
        # Sort by execution time descending
        slow_queries.sort(key=lambda x: x.execution_time_ms, reverse=True)
        
        logger.info(f"Found {len(slow_queries)} slow queries above {threshold_ms}ms")
        
        return slow_queries
    
    def generate_performance_report(self) -> Dict[str, Any]:
        """Generate comprehensive performance report.
        
        Returns:
            Performance analysis report
        """
        if not self._query_history:
            return {"error": "No query history available"}
        
        total_queries = len(self._query_history)
        avg_execution_time = sum(qp.execution_time_ms for qp in self._query_history) / total_queries
        slow_queries = len(self.get_slow_queries())
        
        # Collection-wise statistics
        collection_stats = {}
        for qp in self._query_history:
            if qp.collection_name not in collection_stats:
                collection_stats[qp.collection_name] = {
                    'query_count': 0,
                    'avg_execution_time': 0,
                    'slow_queries': 0,
                    'avg_optimization_score': 0
                }
            
            stats = collection_stats[qp.collection_name]
            stats['query_count'] += 1
            stats['avg_execution_time'] += qp.execution_time_ms
            stats['avg_optimization_score'] += qp.optimization_score
            if qp.execution_time_ms > 100:
                stats['slow_queries'] += 1
        
        # Calculate averages
        for stats in collection_stats.values():
            if stats['query_count'] > 0:
                stats['avg_execution_time'] /= stats['query_count']
                stats['avg_optimization_score'] /= stats['query_count']
        
        report = {
            'summary': {
                'total_queries_analyzed': total_queries,
                'average_execution_time_ms': avg_execution_time,
                'slow_queries_count': slow_queries,
                'slow_queries_percentage': (slow_queries / total_queries) * 100,
                'total_index_recommendations': len(self._index_recommendations)
            },
            'collection_statistics': collection_stats,
            'top_slow_queries': [
                {
                    'collection': qp.collection_name,
                    'execution_time_ms': qp.execution_time_ms,
                    'optimization_score': qp.optimization_score,
                    'query': qp.query
                }
                for qp in self.get_slow_queries()[:10]
            ],
            'index_recommendations': [
                {
                    'collection': rec.collection_name,
                    'fields': rec.fields,
                    'type': rec.index_type,
                    'priority': rec.priority,
                    'estimated_impact': rec.estimated_impact
                }
                for rec in self._index_recommendations[:10]
            ]
        }
        
        logger.info(f"Performance report generated: {total_queries} queries analyzed")
        
        return report
    
    def _extract_index_name(self, winning_plan: Dict[str, Any]) -> Optional[str]:
        """Extract index name from winning plan."""
        if 'indexName' in winning_plan:
            return winning_plan['indexName']
        
        # Check for nested plans (like in compound queries)
        if 'inputStage' in winning_plan:
            return self._extract_index_name(winning_plan['inputStage'])
        
        return None
    
    def _calculate_optimization_score(self, docs_examined: int, docs_returned: int,
                                    execution_time: float, index_used: Optional[str]) -> float:
        """Calculate query optimization score (0-100)."""
        score = 100.0
        
        # Penalize for examining too many documents
        if docs_returned > 0:
            examination_ratio = docs_examined / docs_returned
            if examination_ratio > 1:
                score -= min(50, (examination_ratio - 1) * 10)
        
        # Penalize for slow execution
        if execution_time > 100:
            score -= min(30, (execution_time - 100) / 10)
        
        # Bonus for index usage
        if index_used and index_used != '_id_':
            score += 10
        elif not index_used:
            score -= 20
        
        return max(0, min(100, score))
    
    def _generate_recommendations(self, collection_name: str, query: Dict[str, Any],
                                docs_examined: int, docs_returned: int,
                                index_used: Optional[str]) -> List[str]:
        """Generate optimization recommendations."""
        recommendations = []
        
        # Index recommendations
        if not index_used or index_used == '_id_':
            query_fields = list(query.keys())
            recommendations.append(
                f"Consider creating an index on fields: {query_fields}"
            )
        
        # Examination ratio recommendations
        if docs_returned > 0:
            examination_ratio = docs_examined / docs_returned
            if examination_ratio > 10:
                recommendations.append(
                    f"Query examines {examination_ratio:.1f}x more documents than returned. "
                    "Consider more selective criteria or better indexing."
                )
        
        # Query structure recommendations
        if '$or' in query:
            recommendations.append(
                "Consider restructuring $or queries or creating appropriate indexes for each condition."
            )
        
        if any(isinstance(v, dict) and '$regex' in v for v in query.values()):
            recommendations.append(
                "Regex queries can be slow. Consider using text indexes for text search."
            )
        
        return recommendations
    
    def _reorder_query_fields(self, collection: Collection, query: Dict[str, Any]) -> Dict[str, Any]:
        """Reorder query fields for optimal index usage."""
        # Get existing indexes
        try:
            indexes = list(collection.list_indexes())
            index_fields = []
            for index in indexes:
                if 'key' in index:
                    index_fields.extend(index['key'].keys())
        except Exception as e:
            logger.warning(f"Could not get index information: {e}")
            return query
        
        # Reorder query fields to match index field order
        reordered_query = {}
        
        # First add fields that have indexes
        for field in index_fields:
            if field in query:
                reordered_query[field] = query[field]
        
        # Then add remaining fields
        for field, value in query.items():
            if field not in reordered_query:
                reordered_query[field] = value
        
        return reordered_query
    
    def _optimize_regex_queries(self, query: Dict[str, Any]) -> Dict[str, Any]:
        """Optimize regex queries for better performance."""
        optimized = {}
        
        for field, value in query.items():
            if isinstance(value, dict) and '$regex' in value:
                regex_pattern = value['$regex']
                
                # If regex starts with ^, it can use index
                if not regex_pattern.startswith('^'):
                    # Try to convert to prefix match if possible
                    if regex_pattern.isalnum():
                        optimized[field] = {'$regex': f'^{regex_pattern}', '$options': 'i'}
                    else:
                        optimized[field] = value
                else:
                    optimized[field] = value
            else:
                optimized[field] = value
        
        return optimized
    
    def _optimize_range_queries(self, query: Dict[str, Any]) -> Dict[str, Any]:
        """Optimize range queries for better index usage."""
        optimized = {}
        
        for field, value in query.items():
            if isinstance(value, dict):
                # Combine separate $gte and $lte into single range
                if '$gte' in value and '$lte' in value:
                    optimized[field] = {'$gte': value['$gte'], '$lte': value['$lte']}
                else:
                    optimized[field] = value
            else:
                optimized[field] = value
        
        return optimized
    
    def _generate_query_hints(self, collection: Collection, query: Dict[str, Any]) -> List[str]:
        """Generate query hints for optimization."""
        hints = []
        
        # Suggest specific indexes based on query fields
        query_fields = list(query.keys())
        if len(query_fields) > 1:
            hints.append(f"Consider compound index on: {query_fields}")
        
        return hints
    
    def _analyze_field_patterns(self, queries: List[QueryPlan]) -> Dict[str, List[QueryPlan]]:
        """Analyze field usage patterns in queries."""
        patterns = {}
        
        for query_plan in queries:
            # Create field signature
            fields = tuple(sorted(query_plan.query.keys()))
            if fields not in patterns:
                patterns[fields] = []
            patterns[fields].append(query_plan)
        
        return patterns
    
    def _create_index_recommendation(self, collection_name: str, field_pattern: tuple,
                                   queries: List[QueryPlan]) -> IndexRecommendation:
        """Create index recommendation based on field patterns."""
        # Calculate metrics
        total_queries = len(queries)
        avg_execution_time = sum(q.execution_time_ms for q in queries) / total_queries
        avg_optimization_score = sum(q.optimization_score for q in queries) / total_queries
        
        # Determine index type
        if len(field_pattern) == 1:
            index_type = "single"
        else:
            index_type = "compound"
        
        # Calculate priority (1-5)
        priority = 1
        if total_queries > 10:
            priority += 1
        if avg_execution_time > 100:
            priority += 1
        if avg_optimization_score < 70:
            priority += 1
        if avg_execution_time > 500:
            priority += 1
        
        # Estimate impact (0-100)
        estimated_impact = min(100, (100 - avg_optimization_score) * (total_queries / 10))
        
        return IndexRecommendation(
            collection_name=collection_name,
            fields=list(field_pattern),
            index_type=index_type,
            estimated_impact=estimated_impact,
            priority=min(5, priority)
        )
    
    def _hash_query(self, query: Dict[str, Any]) -> str:
        """Generate hash for query caching."""
        import hashlib
        import json
        
        query_str = json.dumps(query, sort_keys=True, default=str)
        return hashlib.md5(query_str.encode()).hexdigest()

# Global optimizer instance
_default_optimizer: Optional[QueryOptimizer] = None

def get_query_optimizer(client: MongoClient) -> QueryOptimizer:
    """Get or create default query optimizer instance."""
    global _default_optimizer
    if _default_optimizer is None:
        _default_optimizer = QueryOptimizer(client)
    return _default_optimizer

__all__ = ['QueryOptimizer', 'QueryPlan', 'IndexRecommendation', 'get_query_optimizer']