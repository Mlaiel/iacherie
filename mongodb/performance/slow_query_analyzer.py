"""MongoDB Slow Query Analyzer
============================

Advanced slow query detection, analysis, and optimization recommendations.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel - All Rights Reserved
"""

import logging
import time
import json
import hashlib
from typing import Dict, Any, List, Optional, Set, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from collections import defaultdict, deque
from pymongo import MongoClient
from pymongo.collection import Collection

logger = logging.getLogger(__name__)

@dataclass
class SlowQueryInfo:
    """Slow query information and analysis."""
    query_hash: str
    collection_name: str
    operation_type: str  # find, aggregate, update, etc.
    query: Dict[str, Any]
    execution_time_ms: float
    timestamp: datetime
    documents_examined: int
    documents_returned: int
    index_used: Optional[str]
    stages: List[Dict[str, Any]]
    optimization_score: float
    recommendations: List[str]
    frequency: int = 1

@dataclass
class QueryPattern:
    """Query pattern analysis."""
    pattern_hash: str
    pattern_signature: str
    query_count: int
    avg_execution_time_ms: float
    max_execution_time_ms: float
    min_execution_time_ms: float
    total_docs_examined: int
    total_docs_returned: int
    collections: Set[str]
    indexes_used: Set[str]
    first_seen: datetime
    last_seen: datetime

@dataclass
class SlowQueryStats:
    """Slow query statistics."""
    total_slow_queries: int = 0
    unique_patterns: int = 0
    avg_execution_time_ms: float = 0.0
    worst_execution_time_ms: float = 0.0
    most_frequent_pattern: Optional[str] = None
    analysis_period_hours: float = 0.0

class SlowQueryAnalyzer:
    """Advanced slow query analyzer with pattern detection and optimization recommendations."""
    
    def __init__(self, threshold_ms -> None: float = 100, max_queries -> None: int = 10000) -> None:
        """Initialize slow query analyzer.
        
        Args:
            threshold_ms: Threshold for considering a query slow
            max_queries: Maximum number of slow queries to keep in memory
        """
        self.threshold_ms = threshold_ms
        self.max_queries = max_queries
        
        # Storage for slow queries
        self._slow_queries: deque = deque(maxlen=max_queries)
        self._query_patterns: Dict[str, QueryPattern] = {}
        self._collection_stats: Dict[str, Dict[str, Any]] = defaultdict(dict)
        
        # Analysis tracking
        self._analysis_start_time = datetime.utcnow()
        self._query_hashes: Dict[str, SlowQueryInfo] = {}
        
        # Performance thresholds
        self._performance_thresholds = {
            'excellent': 10,      # < 10ms
            'good': 50,          # < 50ms
            'acceptable': 100,   # < 100ms
            'slow': 500,         # < 500ms
            'very_slow': 1000,   # < 1000ms
            'critical': float('inf')  # >= 1000ms
        }
        
        # Optimization rules
        self._optimization_rules = self._load_optimization_rules()
    
    def analyze_query(self, collection: Collection, query: Dict[str, Any],
                     operation_type: str = "find", 
                     projection: Optional[Dict[str, Any]] = None) -> SlowQueryInfo:
        """Analyze a specific query for performance issues.
        
        Args:
            collection: MongoDB collection
            query: Query document
            operation_type: Type of operation (find, aggregate, update, etc.)
            projection: Optional projection document
            
        Returns:
            Slow query analysis information
        """
        start_time = time.time()
        
        # Execute explain for performance analysis
        try:
            if operation_type == "find":
                explain_result = collection.find(query, projection or {}).explain('executionStats')
            elif operation_type == "aggregate":
                # For aggregation, query should be the pipeline
                explain_result = collection.aggregate(query).explain('executionStats')
            else:
                # For other operations, use find as approximation
                explain_result = collection.find(query).explain('executionStats')
                
        except Exception as e:
            logger.error(f"Failed to explain query: {e}")
            return None
        
        execution_time = (time.time() - start_time) * 1000  # Convert to ms
        
        # Extract execution statistics
        exec_stats = explain_result.get('executionStats', {})
        docs_examined = exec_stats.get('totalDocsExamined', 0)
        docs_returned = exec_stats.get('totalDocsReturned', 0)
        
        # Extract stages information
        stages = self._extract_stages(explain_result)
        
        # Determine index usage
        index_used = self._extract_index_name(explain_result.get('queryPlanner', {}))
        
        # Generate query hash
        query_hash = self._generate_query_hash(collection.name, operation_type, query)
        
        # Calculate optimization score
        optimization_score = self._calculate_optimization_score(
            execution_time, docs_examined, docs_returned, index_used, stages
        )
        
        # Generate recommendations
        recommendations = self._generate_recommendations(
            collection.name, query, operation_type, execution_time,
            docs_examined, docs_returned, index_used, stages
        )
        
        # Create slow query info
        slow_query_info = SlowQueryInfo(
            query_hash=query_hash,
            collection_name=collection.name,
            operation_type=operation_type,
            query=query,
            execution_time_ms=execution_time,
            timestamp=datetime.utcnow(),
            documents_examined=docs_examined,
            documents_returned=docs_returned,
            index_used=index_used,
            stages=stages,
            optimization_score=optimization_score,
            recommendations=recommendations
        )
        
        # Store if it's slow
        if execution_time >= self.threshold_ms:
            self._record_slow_query(slow_query_info)
        
        return slow_query_info
    
    def record_slow_query_from_profiler(self, profiler_entry: Dict[str, Any]) -> None:
        """Record slow query from MongoDB profiler output.
        
        Args:
            profiler_entry: MongoDB profiler entry
        """
        try:
            # Extract information from profiler entry
            collection_name = profiler_entry.get('ns', '').split('.')[-1]
            operation_type = profiler_entry.get('op', 'unknown')
            query = profiler_entry.get('command', {})
            execution_time = profiler_entry.get('millis', 0)
            docs_examined = profiler_entry.get('docsExamined', 0)
            docs_returned = profiler_entry.get('nreturned', 0)
            
            # Generate query hash
            query_hash = self._generate_query_hash(collection_name, operation_type, query)
            
            # Create slow query info
            slow_query_info = SlowQueryInfo(
                query_hash=query_hash,
                collection_name=collection_name,
                operation_type=operation_type,
                query=query,
                execution_time_ms=execution_time,
                timestamp=datetime.utcnow(),
                documents_examined=docs_examined,
                documents_returned=docs_returned,
                index_used=profiler_entry.get('indexName'),
                stages=[],
                optimization_score=self._calculate_optimization_score(
                    execution_time, docs_examined, docs_returned, 
                    profiler_entry.get('indexName'), []
                ),
                recommendations=[]
            )
            
            self._record_slow_query(slow_query_info)
            
        except Exception as e:
            logger.error(f"Failed to process profiler entry: {e}")
    
    def get_slow_queries(self, limit: int = 100, 
                        collection_name: str = None,
                        operation_type: str = None,
                        min_execution_time: float = None) -> List[SlowQueryInfo]:
        """Get slow queries with optional filtering.
        
        Args:
            limit: Maximum number of queries to return
            collection_name: Filter by collection name
            operation_type: Filter by operation type
            min_execution_time: Filter by minimum execution time
            
        Returns:
            List of slow queries
        """
        filtered_queries = []
        
        for query_info in self._slow_queries:
            # Apply filters
            if collection_name and query_info.collection_name != collection_name:
                continue
            if operation_type and query_info.operation_type != operation_type:
                continue
            if min_execution_time and query_info.execution_time_ms < min_execution_time:
                continue
            
            filtered_queries.append(query_info)
            
            if len(filtered_queries) >= limit:
                break
        
        # Sort by execution time descending
        filtered_queries.sort(key=lambda x: x.execution_time_ms, reverse=True)
        
        return filtered_queries
    
    def get_query_patterns(self, min_frequency: int = 2) -> List[QueryPattern]:
        """Get query patterns with minimum frequency.
        
        Args:
            min_frequency: Minimum frequency for pattern inclusion
            
        Returns:
            List of query patterns
        """
        patterns = [
            pattern for pattern in self._query_patterns.values()
            if pattern.query_count >= min_frequency
        ]
        
        # Sort by frequency descending
        patterns.sort(key=lambda x: x.query_count, reverse=True)
        
        return patterns
    
    def get_collection_analysis(self, collection_name: str) -> Dict[str, Any]:
        """Get analysis for specific collection.
        
        Args:
            collection_name: Collection to analyze
            
        Returns:
            Collection analysis report
        """
        collection_queries = [
            q for q in self._slow_queries
            if q.collection_name == collection_name
        ]
        
        if not collection_queries:
            return {"error": f"No slow queries found for collection '{collection_name}'"}
        
        # Calculate statistics
        total_queries = len(collection_queries)
        avg_execution_time = sum(q.execution_time_ms for q in collection_queries) / total_queries
        max_execution_time = max(q.execution_time_ms for q in collection_queries)
        
        # Operation type distribution
        operation_distribution = defaultdict(int)
        for query in collection_queries:
            operation_distribution[query.operation_type] += 1
        
        # Index usage analysis
        index_usage = defaultdict(int)
        no_index_queries = 0
        for query in collection_queries:
            if query.index_used:
                index_usage[query.index_used] += 1
            else:
                no_index_queries += 1
        
        # Top recommendations
        all_recommendations = []
        for query in collection_queries:
            all_recommendations.extend(query.recommendations)
        
        recommendation_frequency = defaultdict(int)
        for rec in all_recommendations:
            recommendation_frequency[rec] += 1
        
        top_recommendations = sorted(
            recommendation_frequency.items(),
            key=lambda x: x[1],
            reverse=True
        )[:5]
        
        return {
            'collection_name': collection_name,
            'total_slow_queries': total_queries,
            'average_execution_time_ms': avg_execution_time,
            'max_execution_time_ms': max_execution_time,
            'operation_distribution': dict(operation_distribution),
            'index_usage': dict(index_usage),
            'queries_without_index': no_index_queries,
            'index_usage_percentage': ((total_queries - no_index_queries) / total_queries) * 100,
            'top_recommendations': top_recommendations,
            'worst_queries': [
                {
                    'query': q.query,
                    'execution_time_ms': q.execution_time_ms,
                    'optimization_score': q.optimization_score
                }
                for q in sorted(collection_queries, key=lambda x: x.execution_time_ms, reverse=True)[:5]
            ]
        }
    
    def generate_optimization_report(self) -> Dict[str, Any]:
        """Generate comprehensive optimization report.
        
        Returns:
            Optimization analysis report
        """
        if not self._slow_queries:
            return {"error": "No slow queries recorded"}
        
        stats = self.get_statistics()
        
        # Collection-wise analysis
        collections = set(q.collection_name for q in self._slow_queries)
        collection_analysis = {}
        for collection in collections:
            collection_analysis[collection] = self.get_collection_analysis(collection)
        
        # Query patterns analysis
        patterns = self.get_query_patterns(min_frequency=2)
        
        # Performance distribution
        performance_distribution = defaultdict(int)
        for query in self._slow_queries:
            category = self._categorize_performance(query.execution_time_ms)
            performance_distribution[category] += 1
        
        # Global recommendations
        global_recommendations = self._generate_global_recommendations()
        
        report = {
            'summary': {
                'analysis_period_hours': (datetime.utcnow() - self._analysis_start_time).total_seconds() / 3600,
                'total_slow_queries': len(self._slow_queries),
                'unique_query_patterns': len(self._query_patterns),
                'collections_affected': len(collections),
                'average_execution_time_ms': stats.avg_execution_time_ms,
                'worst_execution_time_ms': stats.worst_execution_time_ms
            },
            'performance_distribution': dict(performance_distribution),
            'collection_analysis': collection_analysis,
            'query_patterns': [
                {
                    'pattern_signature': p.pattern_signature,
                    'frequency': p.query_count,
                    'avg_execution_time_ms': p.avg_execution_time_ms,
                    'max_execution_time_ms': p.max_execution_time_ms,
                    'collections': list(p.collections),
                    'indexes_used': list(p.indexes_used)
                }
                for p in patterns[:10]  # Top 10 patterns
            ],
            'global_recommendations': global_recommendations,
            'worst_performing_queries': [
                {
                    'collection': q.collection_name,
                    'operation': q.operation_type,
                    'execution_time_ms': q.execution_time_ms,
                    'optimization_score': q.optimization_score,
                    'query': q.query,
                    'recommendations': q.recommendations
                }
                for q in sorted(self._slow_queries, key=lambda x: x.execution_time_ms, reverse=True)[:10]
            ]
        }
        
        return report
    
    def get_statistics(self) -> SlowQueryStats:
        """Get slow query statistics.
        
        Returns:
            Slow query statistics
        """
        if not self._slow_queries:
            return SlowQueryStats()
        
        execution_times = [q.execution_time_ms for q in self._slow_queries]
        
        # Find most frequent pattern
        most_frequent_pattern = None
        if self._query_patterns:
            most_frequent_pattern = max(
                self._query_patterns.values(),
                key=lambda p: p.query_count
            ).pattern_signature
        
        return SlowQueryStats(
            total_slow_queries=len(self._slow_queries),
            unique_patterns=len(self._query_patterns),
            avg_execution_time_ms=sum(execution_times) / len(execution_times),
            worst_execution_time_ms=max(execution_times),
            most_frequent_pattern=most_frequent_pattern,
            analysis_period_hours=(datetime.utcnow() - self._analysis_start_time).total_seconds() / 3600
        )
    
    def clear_analysis_data(self) -> None:
        """Clear all analysis data and reset counters."""
        self._slow_queries.clear()
        self._query_patterns.clear()
        self._collection_stats.clear()
        self._query_hashes.clear()
        self._analysis_start_time = datetime.utcnow()
        
        logger.info("Slow query analysis data cleared")
    
    def _record_slow_query(self, slow_query_info: SlowQueryInfo) -> None:
        """Record a slow query for analysis."""
        # Update or add to slow queries
        if slow_query_info.query_hash in self._query_hashes:
            # Update existing entry
            existing = self._query_hashes[slow_query_info.query_hash]
            existing.frequency += 1
            # Update with latest execution time if it's worse
            if slow_query_info.execution_time_ms > existing.execution_time_ms:
                existing.execution_time_ms = slow_query_info.execution_time_ms
                existing.timestamp = slow_query_info.timestamp
        else:
            # Add new entry
            self._slow_queries.append(slow_query_info)
            self._query_hashes[slow_query_info.query_hash] = slow_query_info
        
        # Update query patterns
        pattern_hash = self._generate_pattern_hash(slow_query_info.query)
        if pattern_hash in self._query_patterns:
            pattern = self._query_patterns[pattern_hash]
            pattern.query_count += 1
            pattern.avg_execution_time_ms = (
                (pattern.avg_execution_time_ms * (pattern.query_count - 1) + 
                 slow_query_info.execution_time_ms) / pattern.query_count
            )
            pattern.max_execution_time_ms = max(
                pattern.max_execution_time_ms,
                slow_query_info.execution_time_ms
            )
            pattern.min_execution_time_ms = min(
                pattern.min_execution_time_ms,
                slow_query_info.execution_time_ms
            )
            pattern.total_docs_examined += slow_query_info.documents_examined
            pattern.total_docs_returned += slow_query_info.documents_returned
            pattern.collections.add(slow_query_info.collection_name)
            if slow_query_info.index_used:
                pattern.indexes_used.add(slow_query_info.index_used)
            pattern.last_seen = slow_query_info.timestamp
        else:
            # Create new pattern
            self._query_patterns[pattern_hash] = QueryPattern(
                pattern_hash=pattern_hash,
                pattern_signature=self._generate_pattern_signature(slow_query_info.query),
                query_count=1,
                avg_execution_time_ms=slow_query_info.execution_time_ms,
                max_execution_time_ms=slow_query_info.execution_time_ms,
                min_execution_time_ms=slow_query_info.execution_time_ms,
                total_docs_examined=slow_query_info.documents_examined,
                total_docs_returned=slow_query_info.documents_returned,
                collections={slow_query_info.collection_name},
                indexes_used={slow_query_info.index_used} if slow_query_info.index_used else set(),
                first_seen=slow_query_info.timestamp,
                last_seen=slow_query_info.timestamp
            )
        
        logger.debug(f"Recorded slow query: {slow_query_info.execution_time_ms:.1f}ms "
                    f"on {slow_query_info.collection_name}")
    
    def _generate_query_hash(self, collection_name: str, operation_type: str,
                           query: Dict[str, Any]) -> str:
        """Generate unique hash for query."""
        query_data = {
            'collection': collection_name,
            'operation': operation_type,
            'query': query
        }
        query_str = json.dumps(query_data, sort_keys=True, default=str)
        return hashlib.md5(query_str.encode()).hexdigest()
    
    def _generate_pattern_hash(self, query: Dict[str, Any]) -> str:
        """Generate hash for query pattern (structure-based)."""
        # Create a structure-only version of the query
        pattern = self._extract_query_structure(query)
        pattern_str = json.dumps(pattern, sort_keys=True)
        return hashlib.md5(pattern_str.encode()).hexdigest()
    
    def _generate_pattern_signature(self, query: Dict[str, Any]) -> str:
        """Generate human-readable pattern signature."""
        structure = self._extract_query_structure(query)
        return json.dumps(structure, sort_keys=True)
    
    def _extract_query_structure(self, query: Dict[str, Any]) -> Dict[str, Any]:
        """Extract structural pattern from query (replace values with types)."""
        if isinstance(query, dict):
            result = {}
            for key, value in query.items():
                if isinstance(value, (dict, list)):
                    result[key] = self._extract_query_structure(value)
                else:
                    result[key] = type(value).__name__
            return result
        elif isinstance(query, list):
            if query:
                return [self._extract_query_structure(query[0])]
            return []
        else:
            return type(query).__name__
    
    def _extract_stages(self, explain_result: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract execution stages from explain result."""
        stages = []
        
        try:
            winning_plan = explain_result.get('queryPlanner', {}).get('winningPlan', {})
            self._extract_stages_recursive(winning_plan, stages)
        except Exception as e:
            logger.debug(f"Failed to extract stages: {e}")
        
        return stages
    
    def _extract_stages_recursive(self, plan: Dict[str, Any], stages: List[Dict[str, Any]]) -> None:
        """Recursively extract stages from query plan."""
        if 'stage' in plan:
            stage_info = {
                'stage': plan['stage'],
                'indexName': plan.get('indexName'),
                'direction': plan.get('direction'),
                'filter': plan.get('filter')
            }
            stages.append(stage_info)
        
        # Process input stages
        if 'inputStage' in plan:
            self._extract_stages_recursive(plan['inputStage'], stages)
        
        # Process input stages array
        if 'inputStages' in plan:
            for input_stage in plan['inputStages']:
                self._extract_stages_recursive(input_stage, stages)
    
    def _extract_index_name(self, query_planner: Dict[str, Any]) -> Optional[str]:
        """Extract index name from query planner."""
        winning_plan = query_planner.get('winningPlan', {})
        
        if 'indexName' in winning_plan:
            return winning_plan['indexName']
        
        # Check nested stages
        if 'inputStage' in winning_plan:
            return self._extract_index_name({'winningPlan': winning_plan['inputStage']})
        
        return None
    
    def _calculate_optimization_score(self, execution_time: float, docs_examined: int,
                                    docs_returned: int, index_used: Optional[str],
                                    stages: List[Dict[str, Any]]) -> float:
        """Calculate optimization score (0-100)."""
        score = 100.0
        
        # Execution time penalty
        if execution_time > 1000:
            score -= 50
        elif execution_time > 500:
            score -= 30
        elif execution_time > 100:
            score -= 15
        
        # Document examination efficiency
        if docs_returned > 0:
            examination_ratio = docs_examined / docs_returned
            if examination_ratio > 100:
                score -= 30
            elif examination_ratio > 10:
                score -= 20
            elif examination_ratio > 2:
                score -= 10
        
        # Index usage
        if not index_used or index_used == '_id_':
            score -= 25
        
        # Stage efficiency
        for stage in stages:
            if stage.get('stage') == 'COLLSCAN':
                score -= 20
            elif stage.get('stage') == 'SORT' and not stage.get('indexName'):
                score -= 15
        
        return max(0, min(100, score))
    
    def _generate_recommendations(self, collection_name: str, query: Dict[str, Any],
                                operation_type: str, execution_time: float,
                                docs_examined: int, docs_returned: int,
                                index_used: Optional[str], stages: List[Dict[str, Any]]) -> List[str]:
        """Generate optimization recommendations."""
        recommendations = []
        
        # Index recommendations
        if not index_used or index_used == '_id_':
            query_fields = list(query.keys())
            recommendations.append(f"Create index on fields: {query_fields}")
        
        # Collection scan detection
        for stage in stages:
            if stage.get('stage') == 'COLLSCAN':
                recommendations.append("Avoid collection scan - create appropriate index")
        
        # Examination ratio
        if docs_returned > 0:
            examination_ratio = docs_examined / docs_returned
            if examination_ratio > 10:
                recommendations.append(
                    f"Query examines {examination_ratio:.1f}x more documents than returned. "
                    "Add more selective criteria or better indexing."
                )
        
        # Execution time
        if execution_time > 1000:
            recommendations.append("Very slow query - consider query restructuring or indexing")
        elif execution_time > 500:
            recommendations.append("Slow query - optimize with better indexes or query structure")
        
        # Query-specific recommendations
        if '$or' in query:
            recommendations.append("$or queries can be slow - consider separate queries or compound indexes")
        
        if any(isinstance(v, dict) and '$regex' in v for v in query.values()):
            recommendations.append("Regex queries are slow - consider text indexes or prefix matching")
        
        if operation_type == 'aggregate' and len(query) > 5:
            recommendations.append("Long aggregation pipeline - consider early filtering stages")
        
        return recommendations
    
    def _generate_global_recommendations(self) -> List[str]:
        """Generate global optimization recommendations."""
        recommendations = []
        
        if not self._slow_queries:
            return recommendations
        
        # Collection scan frequency
        collscan_queries = sum(
            1 for q in self._slow_queries
            if any(stage.get('stage') == 'COLLSCAN' for stage in q.stages)
        )
        if collscan_queries > len(self._slow_queries) * 0.3:  # 30% threshold
            recommendations.append(
                f"{collscan_queries} queries use collection scans. "
                "Review indexing strategy for frequently queried collections."
            )
        
        # No index usage
        no_index_queries = sum(
            1 for q in self._slow_queries
            if not q.index_used or q.index_used == '_id_'
        )
        if no_index_queries > len(self._slow_queries) * 0.5:  # 50% threshold
            recommendations.append(
                f"{no_index_queries} queries don't use indexes effectively. "
                "Implement comprehensive indexing strategy."
            )
        
        # Most problematic collections
        collection_query_count = defaultdict(int)
        for query in self._slow_queries:
            collection_query_count[query.collection_name] += 1
        
        if collection_query_count:
            worst_collection = max(collection_query_count.items(), key=lambda x: x[1])
            if worst_collection[1] > 5:
                recommendations.append(
                    f"Collection '{worst_collection[0]}' has {worst_collection[1]} slow queries. "
                    "Priority optimization target."
                )
        
        return recommendations
    
    def _categorize_performance(self, execution_time_ms: float) -> str:
        """Categorize query performance."""
        for category, threshold in self._performance_thresholds.items():
            if execution_time_ms < threshold:
                return category
        return 'critical'
    
    def _load_optimization_rules(self) -> Dict[str, Any]:
        """Load optimization rules and patterns."""
        return {
            'index_recommendations': {
                'single_field_queries': ['Create single field index'],
                'compound_queries': ['Create compound index matching query pattern'],
                'range_queries': ['Ensure range fields are last in compound index'],
                'text_search': ['Use text index for text search operations']
            },
            'query_structure': {
                'or_operations': ['Consider union of separate queries', 'Use compound indexes for OR conditions'],
                'regex_operations': ['Use prefix matching where possible', 'Consider text indexes'],
                'sort_operations': ['Create index matching sort pattern', 'Limit result set before sorting']
            }
        }

# Global analyzer instance
_default_analyzer: Optional[SlowQueryAnalyzer] = None

def get_slow_query_analyzer(threshold_ms: float = 100) -> SlowQueryAnalyzer:
    """Get or create default slow query analyzer."""
    global _default_analyzer
    if _default_analyzer is None:
        _default_analyzer = SlowQueryAnalyzer(threshold_ms)
    return _default_analyzer

__all__ = [
    'SlowQueryAnalyzer', 'SlowQueryInfo', 'QueryPattern', 'SlowQueryStats',
    'get_slow_query_analyzer'
]