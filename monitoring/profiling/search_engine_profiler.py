"""🔍 Search Engine Performance Profiler
========================================

Advanced search engine performance profiling system for the Ainflue Creator Economy platform.
Monitors Elasticsearch, search queries, indexing operations, and search relevance optimization.

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
from typing import Dict, List, Optional, Any, Callable, Union
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import json
import statistics
from collections import defaultdict, deque

from prometheus_client import Counter, Gauge, Histogram, Summary

logger = logging.getLogger(__name__)


class SearchEngineType(Enum):
    """Types of search engines"""
    ELASTICSEARCH = "elasticsearch"
    SOLR = "solr"
    SPHINX = "sphinx"
    ALGOLIA = "algolia"
    OPENSEARCH = "opensearch"
    LUCENE = "lucene"
    WHOOSH = "whoosh"
    CUSTOM = "custom"


class SearchOperationType(Enum):
    """Types of search operations"""
    SEARCH_QUERY = "search_query"
    INDEX_DOCUMENT = "index_document"
    UPDATE_DOCUMENT = "update_document"
    DELETE_DOCUMENT = "delete_document"
    BULK_INDEX = "bulk_index"
    AGGREGATION = "aggregation"
    SUGGESTION = "suggestion"
    AUTOCOMPLETE = "autocomplete"
    FACETED_SEARCH = "faceted_search"
    REINDEX = "reindex"


class SearchDomain(Enum):
    """Search domain categories for Creator Economy"""
    CREATOR_PROFILES = "creator_profiles"
    CONTENT_LIBRARY = "content_library"
    BRAND_PROFILES = "brand_profiles"
    COLLABORATION_OPPORTUNITIES = "collaboration_opportunities"
    ANALYTICS_DATA = "analytics_data"
    USER_GENERATED_CONTENT = "user_generated_content"
    TRENDING_TOPICS = "trending_topics"
    HASHTAGS = "hashtags"


@dataclass
class SearchQueryMetadata:
    """Metadata for search queries"""
    query_text: str
    query_type: str  # "match", "fuzzy", "wildcard", "phrase", "bool"
    fields: List[str]
    filters: Dict[str, Any]
    sort_criteria: List[str]
    page_size: int
    page_number: int
    include_aggregations: bool = False
    include_highlights: bool = False
    user_id: Optional[str] = None
    session_id: Optional[str] = None


@dataclass
class SearchIndexMetadata:
    """Metadata for search index operations"""
    index_name: str
    document_id: str
    document_type: str
    document_size_bytes: int
    field_count: int
    nested_objects: int = 0
    analyzed_fields: List[str] = field(default_factory=list)
    keyword_fields: List[str] = field(default_factory=list)


@dataclass
class SearchMetrics:
    """Search engine performance metrics"""
    operation_id: str
    engine_type: SearchEngineType
    operation_type: SearchOperationType
    domain: SearchDomain
    total_time_ms: float
    
    # Query/Index metadata
    query_metadata: Optional[SearchQueryMetadata] = None
    index_metadata: Optional[SearchIndexMetadata] = None
    
    # Performance metrics
    query_time_ms: Optional[float] = None
    fetch_time_ms: Optional[float] = None
    index_time_ms: Optional[float] = None
    
    # Result metrics
    total_hits: int = 0
    returned_results: int = 0
    search_score_max: Optional[float] = None
    search_score_avg: Optional[float] = None
    
    # Relevance metrics
    precision_at_10: Optional[float] = None
    recall_at_10: Optional[float] = None
    ndcg_score: Optional[float] = None
    
    # Resource usage
    memory_usage_mb: float = 0.0
    cpu_usage_percent: float = 0.0
    disk_io_mb: float = 0.0
    network_bytes: int = 0
    
    # Index metrics (for indexing operations)
    index_size_mb: Optional[float] = None
    shard_count: Optional[int] = None
    replica_count: Optional[int] = None
    
    # Quality metrics
    success: bool = True
    error_message: Optional[str] = None
    timeout: bool = False
    
    timestamp: datetime = field(default_factory=datetime.utcnow)


@dataclass
class SearchBottleneck:
    """Search performance bottleneck detection"""
    bottleneck_id: str
    engine_type: SearchEngineType
    domain: SearchDomain
    
    # Bottleneck details
    bottleneck_type: str  # "slow_query", "low_relevance", "indexing_lag", "memory_pressure"
    severity: str  # "low", "medium", "high", "critical"
    description: str
    
    # Performance impact
    current_performance: Dict[str, float]
    expected_performance: Dict[str, float]
    impact_percentage: float
    
    # Affected queries/operations
    affected_operations: List[str]
    query_patterns: List[str]
    
    # Optimization recommendations
    recommendations: List[str]
    estimated_improvement: Dict[str, float]
    implementation_priority: str  # "immediate", "high", "medium", "low"
    
    timestamp: datetime = field(default_factory=datetime.utcnow)


class SearchEngineProfiler:
    """Advanced search engine performance profiler"""
    
    def __init__(self,
                 monitoring_interval: float = 5.0,
                 max_history_size: int = 10000,
                 enable_query_analysis: bool = True,
                 enable_relevance_tracking: bool = True,
                 slow_query_threshold_ms: float = 1000.0):
        """
        Initialize search engine profiler
        
        Args:
            monitoring_interval: Monitoring interval in seconds
            max_history_size: Maximum number of metrics to store
            enable_query_analysis: Enable detailed query analysis
            enable_relevance_tracking: Enable search relevance tracking
            slow_query_threshold_ms: Threshold for slow query detection
        """
        self.monitoring_interval = monitoring_interval
        self.max_history_size = max_history_size
        self.enable_query_analysis = enable_query_analysis
        self.enable_relevance_tracking = enable_relevance_tracking
        self.slow_query_threshold_ms = slow_query_threshold_ms
        
        # Storage for metrics
        self.metrics_history: deque = deque(maxlen=max_history_size)
        self.current_operations: Dict[str, SearchMetrics] = {}
        self.bottlenecks: List[SearchBottleneck] = []
        self.slow_queries: deque = deque(maxlen=1000)
        
        # Query pattern tracking
        self.query_patterns: Dict[str, List[float]] = defaultdict(list)
        self.popular_queries: Dict[str, int] = defaultdict(int)
        
        # Performance thresholds
        self.thresholds = {
            'max_query_time_ms': slow_query_threshold_ms,
            'min_precision_at_10': 0.7,
            'min_recall_at_10': 0.6,
            'max_memory_usage_mb': 1000.0,
            'max_cpu_usage_percent': 80.0,
            'max_index_time_ms': 5000.0
        }
        
        # Monitoring state
        self.is_monitoring = False
        self.monitoring_task: Optional[asyncio.Task] = None
        self._lock = threading.Lock()
        
        # Prometheus metrics
        self._init_prometheus_metrics()
        
        logger.info("SearchEngineProfiler initialized for Creator Economy platform")
    
    def _init_prometheus_metrics(self):
        """Initialize Prometheus metrics"""
        self.prometheus_metrics = {
            'search_query_duration': Histogram(
                'ainflue_search_query_duration_seconds',
                'Duration of search queries',
                ['engine_type', 'operation_type', 'domain']
            ),
            'search_result_count': Histogram(
                'ainflue_search_results_count',
                'Number of search results returned',
                ['engine_type', 'domain']
            ),
            'search_relevance_score': Gauge(
                'ainflue_search_relevance_score',
                'Search relevance score',
                ['engine_type', 'domain', 'metric_type']
            ),
            'search_errors': Counter(
                'ainflue_search_errors_total',
                'Total search operation errors',
                ['engine_type', 'error_type']
            ),
            'search_bottlenecks': Gauge(
                'ainflue_search_bottlenecks_active',
                'Number of active search bottlenecks',
                ['engine_type', 'severity']
            ),
            'slow_queries': Counter(
                'ainflue_search_slow_queries_total',
                'Total slow search queries',
                ['engine_type', 'domain']
            )
        }
    
    async def start_monitoring(self):
        """Start continuous search monitoring"""
        if self.is_monitoring:
            logger.warning("Search monitoring already running")
            return
        
        self.is_monitoring = True
        self.monitoring_task = asyncio.create_task(self._monitoring_loop())
        logger.info("Search engine monitoring started")
    
    async def stop_monitoring(self):
        """Stop search monitoring"""
        if not self.is_monitoring:
            return
        
        self.is_monitoring = False
        if self.monitoring_task:
            self.monitoring_task.cancel()
            try:
                await self.monitoring_task
            except asyncio.CancelledError:
                pass
        
        logger.info("Search engine monitoring stopped")
    
    async def profile_search_query(self,
                                 engine_type: SearchEngineType,
                                 domain: SearchDomain,
                                 query_metadata: SearchQueryMetadata,
                                 search_func: Callable,
                                 *args, **kwargs) -> SearchMetrics:
        """
        Profile a search query operation
        
        Args:
            engine_type: Type of search engine
            domain: Search domain category
            query_metadata: Query metadata
            search_func: Function to execute and profile
            *args, **kwargs: Arguments for the search function
        
        Returns:
            SearchMetrics: Detailed performance metrics
        """
        operation_id = f"search_{int(time.time() * 1000)}"
        start_time = time.time()
        
        try:
            # Execute the search query
            result = await self._execute_search_operation(search_func, *args, **kwargs)
            
            # Calculate performance metrics
            end_time = time.time()
            total_time_ms = (end_time - start_time) * 1000
            
            # Extract result metrics
            total_hits = self._extract_total_hits(result)
            returned_results = self._extract_returned_results(result)
            search_scores = self._extract_search_scores(result)
            
            # Calculate relevance metrics if enabled
            relevance_metrics = {}
            if self.enable_relevance_tracking:
                relevance_metrics = await self._calculate_relevance_metrics(
                    query_metadata, result
                )
            
            # Create metrics object
            metrics = SearchMetrics(
                operation_id=operation_id,
                engine_type=engine_type,
                operation_type=SearchOperationType.SEARCH_QUERY,
                domain=domain,
                query_metadata=query_metadata,
                total_time_ms=total_time_ms,
                query_time_ms=total_time_ms,  # Simplified for basic implementation
                total_hits=total_hits,
                returned_results=returned_results,
                search_score_max=search_scores.get('max'),
                search_score_avg=search_scores.get('avg'),
                precision_at_10=relevance_metrics.get('precision_at_10'),
                recall_at_10=relevance_metrics.get('recall_at_10'),
                ndcg_score=relevance_metrics.get('ndcg_score'),
                success=True
            )
            
            # Store metrics
            await self._store_metrics(metrics)
            
            # Update Prometheus metrics
            self._update_prometheus_metrics(metrics)
            
            # Track query patterns
            await self._track_query_patterns(query_metadata, metrics)
            
            # Check for bottlenecks
            await self._detect_bottlenecks(metrics)
            
            # Check for slow queries
            if total_time_ms > self.slow_query_threshold_ms:
                await self._handle_slow_query(metrics)
            
            logger.debug(f"Search query profiled: {operation_id} - {total_time_ms:.2f}ms")
            return metrics
            
        except Exception as e:
            # Handle search failure
            end_time = time.time()
            total_time_ms = (end_time - start_time) * 1000
            
            metrics = SearchMetrics(
                operation_id=operation_id,
                engine_type=engine_type,
                operation_type=SearchOperationType.SEARCH_QUERY,
                domain=domain,
                query_metadata=query_metadata,
                total_time_ms=total_time_ms,
                success=False,
                error_message=str(e)
            )
            
            await self._store_metrics(metrics)
            self.prometheus_metrics['search_errors'].labels(
                engine_type=engine_type.value,
                error_type=type(e).__name__
            ).inc()
            
            logger.error(f"Search query failed: {operation_id} - {e}")
            return metrics
    
    async def profile_index_operation(self,
                                    engine_type: SearchEngineType,
                                    domain: SearchDomain,
                                    index_metadata: SearchIndexMetadata,
                                    index_func: Callable,
                                    *args, **kwargs) -> SearchMetrics:
        """
        Profile an indexing operation
        
        Args:
            engine_type: Type of search engine
            domain: Search domain category
            index_metadata: Index metadata
            index_func: Function to execute and profile
            *args, **kwargs: Arguments for the index function
        
        Returns:
            SearchMetrics: Detailed performance metrics
        """
        operation_id = f"index_{int(time.time() * 1000)}"
        start_time = time.time()
        
        try:
            # Execute the indexing operation
            result = await self._execute_search_operation(index_func, *args, **kwargs)
            
            # Calculate performance metrics
            end_time = time.time()
            total_time_ms = (end_time - start_time) * 1000
            
            # Create metrics object
            metrics = SearchMetrics(
                operation_id=operation_id,
                engine_type=engine_type,
                operation_type=SearchOperationType.INDEX_DOCUMENT,
                domain=domain,
                index_metadata=index_metadata,
                total_time_ms=total_time_ms,
                index_time_ms=total_time_ms,
                success=True
            )
            
            # Store metrics
            await self._store_metrics(metrics)
            
            # Update Prometheus metrics
            self._update_prometheus_metrics(metrics)
            
            # Check for bottlenecks
            await self._detect_bottlenecks(metrics)
            
            logger.debug(f"Index operation profiled: {operation_id} - {total_time_ms:.2f}ms")
            return metrics
            
        except Exception as e:
            # Handle indexing failure
            end_time = time.time()
            total_time_ms = (end_time - start_time) * 1000
            
            metrics = SearchMetrics(
                operation_id=operation_id,
                engine_type=engine_type,
                operation_type=SearchOperationType.INDEX_DOCUMENT,
                domain=domain,
                index_metadata=index_metadata,
                total_time_ms=total_time_ms,
                success=False,
                error_message=str(e)
            )
            
            await self._store_metrics(metrics)
            self.prometheus_metrics['search_errors'].labels(
                engine_type=engine_type.value,
                error_type=type(e).__name__
            ).inc()
            
            logger.error(f"Index operation failed: {operation_id} - {e}")
            return metrics
    
    async def _execute_search_operation(self, operation_func: Callable, *args, **kwargs):
        """Execute search operation with proper async handling"""
        if asyncio.iscoroutinefunction(operation_func):
            return await operation_func(*args, **kwargs)
        else:
            return operation_func(*args, **kwargs)
    
    def _extract_total_hits(self, result: Any) -> int:
        """Extract total hits from search result"""
        if isinstance(result, dict):
            # Elasticsearch format
            if 'hits' in result and 'total' in result['hits']:
                total = result['hits']['total']
                return total.get('value', 0) if isinstance(total, dict) else total
            # Simple format
            elif 'total' in result:
                return result['total']
        return 0
    
    def _extract_returned_results(self, result: Any) -> int:
        """Extract number of returned results"""
        if isinstance(result, dict):
            if 'hits' in result and 'hits' in result['hits']:
                return len(result['hits']['hits'])
            elif 'results' in result:
                return len(result['results'])
        elif isinstance(result, list):
            return len(result)
        return 0
    
    def _extract_search_scores(self, result: Any) -> Dict[str, float]:
        """Extract search scores from result"""
        scores = []
        
        if isinstance(result, dict) and 'hits' in result and 'hits' in result['hits']:
            for hit in result['hits']['hits']:
                if '_score' in hit and hit['_score'] is not None:
                    scores.append(hit['_score'])
        
        if scores:
            return {
                'max': max(scores),
                'avg': sum(scores) / len(scores),
                'min': min(scores)
            }
        
        return {}
    
    async def _calculate_relevance_metrics(self,
                                         query_metadata: SearchQueryMetadata,
                                         result: Any) -> Dict[str, float]:
        """Calculate search relevance metrics"""
        # This would implement actual relevance calculation
        # For now, return simulated metrics
        return {
            'precision_at_10': 0.8,  # Would be calculated based on actual relevance
            'recall_at_10': 0.7,
            'ndcg_score': 0.85
        }
    
    async def _store_metrics(self, metrics: SearchMetrics):
        """Store metrics in history"""
        with self._lock:
            self.metrics_history.append(metrics)
            self.current_operations[metrics.operation_id] = metrics
    
    def _update_prometheus_metrics(self, metrics: SearchMetrics):
        """Update Prometheus metrics"""
        # Update query duration
        self.prometheus_metrics['search_query_duration'].labels(
            engine_type=metrics.engine_type.value,
            operation_type=metrics.operation_type.value,
            domain=metrics.domain.value
        ).observe(metrics.total_time_ms / 1000)
        
        # Update result count
        self.prometheus_metrics['search_result_count'].labels(
            engine_type=metrics.engine_type.value,
            domain=metrics.domain.value
        ).observe(metrics.total_hits)
        
        # Update relevance scores
        if metrics.precision_at_10 is not None:
            self.prometheus_metrics['search_relevance_score'].labels(
                engine_type=metrics.engine_type.value,
                domain=metrics.domain.value,
                metric_type='precision_at_10'
            ).set(metrics.precision_at_10)
        
        if metrics.recall_at_10 is not None:
            self.prometheus_metrics['search_relevance_score'].labels(
                engine_type=metrics.engine_type.value,
                domain=metrics.domain.value,
                metric_type='recall_at_10'
            ).set(metrics.recall_at_10)
    
    async def _track_query_patterns(self, query_metadata: SearchQueryMetadata, metrics: SearchMetrics):
        """Track query patterns for optimization"""
        query_pattern = self._extract_query_pattern(query_metadata)
        
        with self._lock:
            self.query_patterns[query_pattern].append(metrics.total_time_ms)
            self.popular_queries[query_metadata.query_text] += 1
            
            # Keep only recent patterns
            if len(self.query_patterns[query_pattern]) > 100:
                self.query_patterns[query_pattern] = self.query_patterns[query_pattern][-100:]
    
    def _extract_query_pattern(self, query_metadata: SearchQueryMetadata) -> str:
        """Extract query pattern for analysis"""
        # Simplified pattern extraction
        pattern_parts = [
            query_metadata.query_type,
            f"fields_{len(query_metadata.fields)}",
            f"filters_{len(query_metadata.filters)}",
            f"page_size_{query_metadata.page_size}"
        ]
        return "_".join(pattern_parts)
    
    async def _handle_slow_query(self, metrics: SearchMetrics):
        """Handle slow query detection"""
        with self._lock:
            self.slow_queries.append(metrics)
        
        self.prometheus_metrics['slow_queries'].labels(
            engine_type=metrics.engine_type.value,
            domain=metrics.domain.value
        ).inc()
        
        logger.warning(f"Slow query detected: {metrics.operation_id} - {metrics.total_time_ms:.2f}ms")
    
    async def _detect_bottlenecks(self, metrics: SearchMetrics):
        """Detect search performance bottlenecks"""
        bottlenecks = []
        
        # Slow query detection
        if metrics.total_time_ms > self.thresholds['max_query_time_ms']:
            bottleneck = SearchBottleneck(
                bottleneck_id=f"slow_query_{int(time.time())}",
                engine_type=metrics.engine_type,
                domain=metrics.domain,
                bottleneck_type="slow_query",
                severity="high" if metrics.total_time_ms > self.thresholds['max_query_time_ms'] * 2 else "medium",
                description=f"Slow query detected: {metrics.total_time_ms:.2f}ms",
                current_performance={"query_time_ms": metrics.total_time_ms},
                expected_performance={"query_time_ms": self.thresholds['max_query_time_ms']},
                impact_percentage=(metrics.total_time_ms - self.thresholds['max_query_time_ms']) / self.thresholds['max_query_time_ms'] * 100,
                affected_operations=[metrics.operation_id],
                query_patterns=[self._extract_query_pattern(metrics.query_metadata) if metrics.query_metadata else "unknown"],
                recommendations=[
                    "Add appropriate indexes for query fields",
                    "Optimize query structure and filters",
                    "Consider query result caching",
                    "Review field mapping and analysis",
                    "Implement query timeout limits"
                ],
                estimated_improvement={"query_time_reduction_percent": 40.0},
                implementation_priority="high"
            )
            bottlenecks.append(bottleneck)
        
        # Low relevance detection
        if (metrics.precision_at_10 is not None and 
            metrics.precision_at_10 < self.thresholds['min_precision_at_10']):
            bottleneck = SearchBottleneck(
                bottleneck_id=f"low_relevance_{int(time.time())}",
                engine_type=metrics.engine_type,
                domain=metrics.domain,
                bottleneck_type="low_relevance",
                severity="medium",
                description=f"Low search relevance: {metrics.precision_at_10:.2f} precision",
                current_performance={"precision_at_10": metrics.precision_at_10},
                expected_performance={"precision_at_10": self.thresholds['min_precision_at_10']},
                impact_percentage=(self.thresholds['min_precision_at_10'] - metrics.precision_at_10) / self.thresholds['min_precision_at_10'] * 100,
                affected_operations=[metrics.operation_id],
                query_patterns=[self._extract_query_pattern(metrics.query_metadata) if metrics.query_metadata else "unknown"],
                recommendations=[
                    "Review and optimize field analyzers",
                    "Implement query boosting strategies",
                    "Add synonyms and stemming",
                    "Optimize scoring functions",
                    "Consider machine learning ranking"
                ],
                estimated_improvement={"relevance_improvement_percent": 25.0},
                implementation_priority="medium"
            )
            bottlenecks.append(bottleneck)
        
        # Store bottlenecks
        for bottleneck in bottlenecks:
            self.bottlenecks.append(bottleneck)
            self.prometheus_metrics['search_bottlenecks'].labels(
                engine_type=bottleneck.engine_type.value,
                severity=bottleneck.severity
            ).inc()
    
    async def _monitoring_loop(self):
        """Background monitoring loop"""
        while self.is_monitoring:
            try:
                # Monitor query patterns
                await self._monitor_query_patterns()
                
                # Monitor index health
                await self._monitor_index_health()
                
                # Clean up old data
                await self._cleanup_old_data()
                
                await asyncio.sleep(self.monitoring_interval)
                
            except Exception as e:
                logger.error(f"Error in search monitoring loop: {e}")
                await asyncio.sleep(self.monitoring_interval)
    
    async def _monitor_query_patterns(self):
        """Monitor query patterns for optimization opportunities"""
        try:
            # Analyze frequently used queries
            with self._lock:
                if self.popular_queries:
                    # Find queries that might benefit from caching
                    frequent_queries = {k: v for k, v in self.popular_queries.items() if v > 10}
                    if frequent_queries:
                        logger.info(f"Found {len(frequent_queries)} frequently used queries")
                
                # Analyze slow query patterns
                if self.query_patterns:
                    for pattern, times in self.query_patterns.items():
                        if len(times) > 10:  # Enough data points
                            avg_time = statistics.mean(times)
                            if avg_time > self.slow_query_threshold_ms:
                                logger.warning(f"Slow query pattern detected: {pattern} - avg {avg_time:.2f}ms")
        
        except Exception as e:
            logger.error(f"Error monitoring query patterns: {e}")
    
    async def _monitor_index_health(self):
        """Monitor search index health"""
        # This would implement actual index health monitoring
        pass
    
    async def _cleanup_old_data(self):
        """Clean up old monitoring data"""
        cutoff_time = datetime.utcnow() - timedelta(hours=1)
        
        # Clean up old bottlenecks
        self.bottlenecks = [b for b in self.bottlenecks if b.timestamp > cutoff_time]
        
        # Clean up old operations
        old_operations = [op_id for op_id, metrics in self.current_operations.items() 
                         if metrics.timestamp < cutoff_time]
        for op_id in old_operations:
            del self.current_operations[op_id]
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """Get search performance summary"""
        if not self.metrics_history:
            return {}
        
        recent_metrics = list(self.metrics_history)[-100:]  # Last 100 operations
        search_metrics = [m for m in recent_metrics if m.operation_type == SearchOperationType.SEARCH_QUERY]
        
        if not search_metrics:
            return {"message": "No search operations recorded"}
        
        # Calculate averages
        avg_query_time = statistics.mean([m.total_time_ms for m in search_metrics])
        avg_results = statistics.mean([m.total_hits for m in search_metrics])
        success_rate = sum(1 for m in search_metrics if m.success) / len(search_metrics) * 100
        
        # Relevance metrics
        precision_scores = [m.precision_at_10 for m in search_metrics if m.precision_at_10 is not None]
        avg_precision = statistics.mean(precision_scores) if precision_scores else None
        
        # Domain breakdown
        domain_breakdown = defaultdict(list)
        for metric in search_metrics:
            domain_breakdown[metric.domain.value].append(metric)
        
        return {
            "overall_performance": {
                "average_query_time_ms": avg_query_time,
                "average_results_returned": avg_results,
                "success_rate_percent": success_rate,
                "total_queries": len(search_metrics),
                "average_precision_at_10": avg_precision
            },
            "domain_breakdown": {
                domain: {
                    "query_count": len(metrics),
                    "avg_query_time_ms": statistics.mean([m.total_time_ms for m in metrics]),
                    "avg_results": statistics.mean([m.total_hits for m in metrics])
                }
                for domain, metrics in domain_breakdown.items()
            },
            "slow_queries_count": len(self.slow_queries),
            "active_bottlenecks": len([b for b in self.bottlenecks if b.timestamp > datetime.utcnow() - timedelta(minutes=5)]),
            "popular_queries": dict(list(self.popular_queries.items())[:10]),  # Top 10
            "timestamp": datetime.utcnow().isoformat()
        }
    
    def get_bottleneck_report(self) -> List[Dict[str, Any]]:
        """Get detailed bottleneck report"""
        return [
            {
                "bottleneck_id": b.bottleneck_id,
                "engine_type": b.engine_type.value,
                "domain": b.domain.value,
                "type": b.bottleneck_type,
                "severity": b.severity,
                "description": b.description,
                "impact_percentage": b.impact_percentage,
                "affected_operations": b.affected_operations,
                "query_patterns": b.query_patterns,
                "recommendations": b.recommendations,
                "estimated_improvement": b.estimated_improvement,
                "implementation_priority": b.implementation_priority,
                "timestamp": b.timestamp.isoformat()
            }
            for b in self.bottlenecks
        ]


class SearchProfiler:
    """Simplified search profiler interface"""
    
    def __init__(self):
        self.profiler = SearchEngineProfiler()
    
    async def start_monitoring(self):
        """Start search monitoring"""
        return await self.profiler.start_monitoring()
    
    async def stop_monitoring(self):
        """Stop search monitoring"""
        return await self.profiler.stop_monitoring()
    
    async def profile_search(self,
                           engine_type: str,
                           domain: str,
                           query_text: str,
                           search_func: Callable,
                           *args, **kwargs):
        """Profile a search operation"""
        # Convert strings to enums
        engine = SearchEngineType(engine_type.lower())
        search_domain = SearchDomain(domain.lower())
        
        # Create query metadata
        query_metadata = SearchQueryMetadata(
            query_text=query_text,
            query_type="match",  # Default
            fields=["title", "content"],  # Default
            filters={},
            sort_criteria=[],
            page_size=10,
            page_number=1
        )
        
        return await self.profiler.profile_search_query(
            engine, search_domain, query_metadata, search_func, *args, **kwargs
        )


def create_search_engine_profiler(
    monitoring_interval: float = 5.0,
    enable_query_analysis: bool = True,
    enable_relevance_tracking: bool = True,
    slow_query_threshold_ms: float = 1000.0,
    start_monitoring: bool = False
) -> SearchEngineProfiler:
    """
    Factory function to create search engine profiler
    
    Args:
        monitoring_interval: Monitoring interval in seconds
        enable_query_analysis: Enable detailed query analysis
        enable_relevance_tracking: Enable search relevance tracking
        slow_query_threshold_ms: Threshold for slow query detection
        start_monitoring: Start monitoring immediately
    
    Returns:
        SearchEngineProfiler: Configured search profiler instance
    """
    profiler = SearchEngineProfiler(
        monitoring_interval=monitoring_interval,
        enable_query_analysis=enable_query_analysis,
        enable_relevance_tracking=enable_relevance_tracking,
        slow_query_threshold_ms=slow_query_threshold_ms
    )
    
    if start_monitoring:
        import asyncio
        try:
            loop = asyncio.get_event_loop()
            loop.create_task(profiler.start_monitoring())
        except RuntimeError:
            logger.warning("No event loop running, monitoring will need to be started manually")
    
    return profiler


# Example usage for Creator Economy platform
async def example_creator_search_profiling():
    """Example of profiling creator search operations"""
    profiler = create_search_engine_profiler(start_monitoring=True)
    
    # Example: Profile creator search
    async def search_creators(query: str, filters: dict):
        # Simulate Elasticsearch search
        await asyncio.sleep(0.05)  # Simulate search time
        return {
            "hits": {
                "total": {"value": 1250},
                "hits": [
                    {"_id": "creator_1", "_score": 4.2, "_source": {"name": "John Creator"}},
                    {"_id": "creator_2", "_score": 3.8, "_source": {"name": "Jane Influencer"}}
                ]
            }
        }
    
    query_metadata = SearchQueryMetadata(
        query_text="gaming content creator",
        query_type="match",
        fields=["name", "bio", "tags"],
        filters={"category": "gaming", "followers": {"gte": 1000}},
        sort_criteria=["_score", "followers"],
        page_size=20,
        page_number=1
    )
    
    metrics = await profiler.profile_search_query(
        SearchEngineType.ELASTICSEARCH,
        SearchDomain.CREATOR_PROFILES,
        query_metadata,
        search_creators,
        "gaming content creator",
        {"category": "gaming"}
    )
    
    print(f"Search profiling completed:")
    print(f"- Query time: {metrics.total_time_ms:.2f}ms")
    print(f"- Total hits: {metrics.total_hits}")
    print(f"- Returned results: {metrics.returned_results}")
    print(f"- Success: {metrics.success}")
    
    # Get performance summary
    summary = profiler.get_performance_summary()
    print(f"Performance summary: {json.dumps(summary, indent=2)}")
    
    await profiler.stop_monitoring()


if __name__ == "__main__":
    asyncio.run(example_creator_search_profiling())