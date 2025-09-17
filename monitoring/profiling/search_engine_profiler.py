"""⚡ Search Engine Profiling System
=================================

Advanced search engine performance monitoring for the Ainflue Creator Platform.
Provides comprehensive profiling for Elasticsearch, search queries, and indexing performance.

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
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import json
import statistics
from collections import defaultdict, deque

logger = logging.getLogger(__name__)

# Try to import Elasticsearch
try:
    from elasticsearch import Elasticsearch
    HAS_ELASTICSEARCH = True
except ImportError:
    HAS_ELASTICSEARCH = False
    logger.warning("elasticsearch not available, Elasticsearch profiling disabled")

# Try to import Solr
try:
    import pysolr
    HAS_SOLR = True
except ImportError:
    HAS_SOLR = False

# Try to import other search engines
try:
    import whoosh
    HAS_WHOOSH = True
except ImportError:
    HAS_WHOOSH = False


class SearchEngineType(Enum):
    """Types of search engines"""
    ELASTICSEARCH = "elasticsearch"
    SOLR = "solr"
    WHOOSH = "whoosh"
    OPENSEARCH = "opensearch"
    SPHINX = "sphinx"
    CUSTOM = "custom"


class SearchOperation(Enum):
    """Types of search operations"""
    SEARCH = "search"
    INDEX = "index"
    UPDATE = "update"
    DELETE = "delete"
    BULK_INDEX = "bulk_index"
    AGGREGATE = "aggregate"
    SUGGEST = "suggest"
    SCROLL = "scroll"


class SearchComplexity(Enum):
    """Search query complexity levels"""
    SIMPLE = "simple"      # Basic term queries
    MEDIUM = "medium"      # Multi-field queries  
    COMPLEX = "complex"    # Aggregations, filters
    ADVANCED = "advanced"  # Complex nested queries


@dataclass
class SearchMetadata:
    """Metadata for search operations"""
    query: str
    index_name: str
    operation: SearchOperation
    complexity: SearchComplexity
    fields: List[str] = field(default_factory=list)
    filters: Dict[str, Any] = field(default_factory=dict)
    aggregations: List[str] = field(default_factory=list)
    document_count: int = 0
    result_count: int = 0


@dataclass
class SearchMetrics:
    """Search engine performance metrics"""
    operation_id: str
    engine_type: SearchEngineType
    operation: SearchOperation
    query_time_ms: float
    index_time_ms: float
    total_hits: int
    returned_results: int
    relevance_score: float
    cpu_usage: float
    memory_usage_mb: float
    cache_hit_rate: float
    error_count: int
    timestamp: datetime
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class SearchBottleneck:
    """Search engine bottleneck information"""
    bottleneck_type: str
    severity: str
    engine_type: SearchEngineType
    description: str
    impact: str
    recommendations: List[str]
    detected_at: datetime
    metrics: Dict[str, float] = field(default_factory=dict)


class SearchEngineProfiler:
    """
    Search engine performance profiler for Creator Economy content search
    """
    
    def __init__(self, 
                 monitoring_interval: float = 5.0,
                 max_history_size: int = 10000):
        self.monitoring_interval = monitoring_interval
        self.max_history_size = max_history_size
        self.is_monitoring = False
        self.monitoring_thread = None
        
        # Metrics storage
        self.search_metrics_history: deque = deque(maxlen=max_history_size)
        self.bottlenecks_history: deque = deque(maxlen=1000)
        self.active_queries: Dict[str, Dict] = {}
        
        # Performance thresholds
        self.thresholds = {
            'slow_query_threshold': 1000.0,  # 1 second
            'index_time_threshold': 500.0,   # 500ms
            'low_relevance_threshold': 0.5,  # 50%
            'high_error_rate_threshold': 5.0, # 5%
            'cache_hit_rate_threshold': 80.0  # 80%
        }
        
        # Search engine clients
        self.search_clients = {}
        self._init_search_clients()
        
        logger.info("SearchEngineProfiler initialized")

    def _init_search_clients(self):
        """Initialize search engine clients"""
        try:
            # Initialize Elasticsearch client if available
            if HAS_ELASTICSEARCH:
                self.search_clients['elasticsearch'] = Elasticsearch([
                    {'host': 'localhost', 'port': 9200}
                ])
            
            # Initialize Solr client if available
            if HAS_SOLR:
                self.search_clients['solr'] = pysolr.Solr('http://localhost:8983/solr/')
            
            # Initialize Whoosh if available
            if HAS_WHOOSH:
                # Whoosh setup would be here
                pass
                
        except Exception as e:
            logger.warning(f"Error initializing search clients: {e}")

    def start_monitoring(self):
        """Start background search monitoring"""
        if not self.is_monitoring:
            self.is_monitoring = True
            self.monitoring_thread = threading.Thread(
                target=self._monitoring_loop,
                daemon=True
            )
            self.monitoring_thread.start()
            logger.info("Search engine monitoring started")

    def stop_monitoring(self):
        """Stop background monitoring"""
        self.is_monitoring = False
        if self.monitoring_thread:
            self.monitoring_thread.join(timeout=5.0)
        logger.info("Search engine monitoring stopped")

    def _monitoring_loop(self):
        """Background monitoring loop"""
        while self.is_monitoring:
            try:
                self._collect_search_engine_metrics()
                time.sleep(self.monitoring_interval)
            except Exception as e:
                logger.error(f"Error in search monitoring loop: {e}")

    def _collect_search_engine_metrics(self):
        """Collect search engine cluster metrics"""
        try:
            # Collect Elasticsearch cluster metrics
            if 'elasticsearch' in self.search_clients:
                self._collect_elasticsearch_metrics()
            
            # Collect Solr metrics
            if 'solr' in self.search_clients:
                self._collect_solr_metrics()
                
        except Exception as e:
            logger.error(f"Error collecting search engine metrics: {e}")

    def _collect_elasticsearch_metrics(self):
        """Collect Elasticsearch cluster metrics"""
        try:
            es = self.search_clients['elasticsearch']
            
            # Get cluster health
            health = es.cluster.health()
            
            # Get node stats
            stats = es.nodes.stats()
            
            # Calculate aggregate metrics
            total_docs = 0
            total_queries = 0
            query_time_sum = 0
            
            for node_id, node_stats in stats.get('nodes', {}).items():
                indices = node_stats.get('indices', {})
                docs = indices.get('docs', {})
                search = indices.get('search', {})
                
                total_docs += docs.get('count', 0)
                total_queries += search.get('query_total', 0)
                query_time_sum += search.get('query_time_in_millis', 0)
            
            # Create system metrics
            avg_query_time = query_time_sum / total_queries if total_queries > 0 else 0
            
            metrics = SearchMetrics(
                operation_id=f"cluster_metrics_{int(time.time())}",
                engine_type=SearchEngineType.ELASTICSEARCH,
                operation=SearchOperation.SEARCH,
                query_time_ms=avg_query_time,
                index_time_ms=0.0,
                total_hits=total_docs,
                returned_results=0,
                relevance_score=0.0,
                cpu_usage=0.0,
                memory_usage_mb=0.0,
                cache_hit_rate=0.0,
                error_count=0,
                timestamp=datetime.utcnow(),
                metadata={
                    'cluster_status': health.get('status'),
                    'number_of_nodes': health.get('number_of_nodes'),
                    'active_shards': health.get('active_shards'),
                    'total_queries': total_queries
                }
            )
            
            self.search_metrics_history.append(metrics)
            
        except Exception as e:
            logger.error(f"Error collecting Elasticsearch metrics: {e}")

    def _collect_solr_metrics(self):
        """Collect Solr metrics"""
        try:
            # Placeholder for Solr metrics collection
            pass
        except Exception as e:
            logger.error(f"Error collecting Solr metrics: {e}")

    def profile_search_query(self, 
                           query: str,
                           index_name: str,
                           engine_type: SearchEngineType = SearchEngineType.ELASTICSEARCH,
                           **kwargs) -> SearchMetrics:
        """
        Profile a search query
        
        Args:
            query: Search query
            index_name: Index/collection name
            engine_type: Type of search engine
            **kwargs: Additional search parameters
            
        Returns:
            SearchMetrics with profiling results
        """
        operation_id = f"search_{engine_type.value}_{int(time.time())}"
        start_time = time.time()
        
        try:
            # Analyze query complexity
            complexity = self._analyze_query_complexity(query, kwargs)
            
            # Track query start
            self.active_queries[operation_id] = {
                'start_time': start_time,
                'query': query,
                'index_name': index_name,
                'engine_type': engine_type
            }
            
            # Execute search based on engine type
            if engine_type == SearchEngineType.ELASTICSEARCH:
                result = self._execute_elasticsearch_search(query, index_name, **kwargs)
            elif engine_type == SearchEngineType.SOLR:
                result = self._execute_solr_search(query, index_name, **kwargs)
            else:
                result = self._execute_generic_search(query, index_name, **kwargs)
            
            end_time = time.time()
            query_time_ms = (end_time - start_time) * 1000
            
            # Calculate relevance score
            relevance_score = self._calculate_relevance_score(result)
            
            # Create metrics
            metrics = SearchMetrics(
                operation_id=operation_id,
                engine_type=engine_type,
                operation=SearchOperation.SEARCH,
                query_time_ms=query_time_ms,
                index_time_ms=0.0,
                total_hits=result.get('total_hits', 0),
                returned_results=result.get('returned_results', 0),
                relevance_score=relevance_score,
                cpu_usage=0.0,
                memory_usage_mb=0.0,
                cache_hit_rate=result.get('cache_hit_rate', 0.0),
                error_count=1 if result.get('error') else 0,
                timestamp=datetime.utcnow(),
                metadata={
                    'query': query,
                    'index_name': index_name,
                    'complexity': complexity.value,
                    'took_ms': result.get('took_ms', query_time_ms),
                    'timed_out': result.get('timed_out', False)
                }
            )
            
            # Store metrics
            self.search_metrics_history.append(metrics)
            
            # Check for bottlenecks
            self._analyze_search_bottlenecks(metrics)
            
            return metrics
            
        except Exception as e:
            logger.error(f"Error profiling search query: {e}")
            raise
        finally:
            # Remove from active queries
            self.active_queries.pop(operation_id, None)

    def _analyze_query_complexity(self, query: str, params: Dict) -> SearchComplexity:
        """Analyze query complexity"""
        complexity_score = 0
        
        # Check query length
        if len(query) > 100:
            complexity_score += 1
        
        # Check for aggregations
        if params.get('aggs') or params.get('aggregations'):
            complexity_score += 2
        
        # Check for filters
        if params.get('filter') or params.get('post_filter'):
            complexity_score += 1
        
        # Check for sorting
        if params.get('sort'):
            complexity_score += 1
        
        # Check for nested queries
        if 'nested' in query.lower() or 'bool' in query.lower():
            complexity_score += 2
        
        if complexity_score >= 4:
            return SearchComplexity.ADVANCED
        elif complexity_score >= 2:
            return SearchComplexity.COMPLEX
        elif complexity_score >= 1:
            return SearchComplexity.MEDIUM
        else:
            return SearchComplexity.SIMPLE

    def _execute_elasticsearch_search(self, query: str, index_name: str, **kwargs) -> Dict:
        """Execute Elasticsearch search"""
        result = {'error': False}
        
        if 'elasticsearch' not in self.search_clients:
            result['error'] = True
            result['error_message'] = "Elasticsearch client not available"
            return result
        
        try:
            es = self.search_clients['elasticsearch']
            
            # Build search body
            search_body = {
                'query': {
                    'query_string': {
                        'query': query
                    }
                }
            }
            
            # Add additional parameters
            if kwargs.get('size'):
                search_body['size'] = kwargs['size']
            if kwargs.get('from'):
                search_body['from'] = kwargs['from']
            if kwargs.get('sort'):
                search_body['sort'] = kwargs['sort']
            if kwargs.get('aggs'):
                search_body['aggs'] = kwargs['aggs']
            
            # Execute search
            response = es.search(
                index=index_name,
                body=search_body
            )
            
            # Extract metrics
            result['total_hits'] = response['hits']['total']['value']
            result['returned_results'] = len(response['hits']['hits'])
            result['took_ms'] = response['took']
            result['timed_out'] = response['timed_out']
            result['max_score'] = response['hits']['max_score']
            result['hits'] = response['hits']['hits']
            
        except Exception as e:
            result['error'] = True
            result['error_message'] = str(e)
        
        return result

    def _execute_solr_search(self, query: str, index_name: str, **kwargs) -> Dict:
        """Execute Solr search"""
        result = {'error': False}
        
        if 'solr' not in self.search_clients:
            result['error'] = True
            result['error_message'] = "Solr client not available"
            return result
        
        try:
            solr = self.search_clients['solr']
            
            # Execute search
            search_results = solr.search(query, **kwargs)
            
            result['total_hits'] = search_results.hits
            result['returned_results'] = len(search_results.docs)
            result['hits'] = search_results.docs
            
        except Exception as e:
            result['error'] = True
            result['error_message'] = str(e)
        
        return result

    def _execute_generic_search(self, query: str, index_name: str, **kwargs) -> Dict:
        """Execute generic search"""
        return {
            'error': False,
            'total_hits': 0,
            'returned_results': 0,
            'search_type': 'generic'
        }

    def _calculate_relevance_score(self, result: Dict) -> float:
        """Calculate relevance score from search results"""
        if result.get('error') or not result.get('hits'):
            return 0.0
        
        hits = result['hits']
        if not hits:
            return 0.0
        
        # Calculate average score
        scores = []
        for hit in hits[:10]:  # Top 10 results
            score = hit.get('_score', 0.0)
            if score:
                scores.append(score)
        
        if scores:
            max_score = result.get('max_score', max(scores))
            if max_score > 0:
                return statistics.mean(scores) / max_score
        
        return 0.0

    def _analyze_search_bottlenecks(self, metrics: SearchMetrics):
        """Analyze search bottlenecks"""
        bottlenecks = []
        
        # Check query time
        if metrics.query_time_ms > self.thresholds['slow_query_threshold']:
            bottlenecks.append(SearchBottleneck(
                bottleneck_type="slow_query",
                severity="high" if metrics.query_time_ms > 2000 else "medium",
                engine_type=metrics.engine_type,
                description=f"Search query too slow: {metrics.query_time_ms:.1f}ms",
                impact="Poor user experience, delayed search results",
                recommendations=[
                    "Optimize query structure",
                    "Add appropriate indexes",
                    "Consider query caching",
                    "Reduce result set size"
                ],
                detected_at=datetime.utcnow(),
                metrics={'query_time_ms': metrics.query_time_ms}
            ))
        
        # Check relevance
        if metrics.relevance_score < self.thresholds['low_relevance_threshold']:
            bottlenecks.append(SearchBottleneck(
                bottleneck_type="low_relevance",
                severity="medium",
                engine_type=metrics.engine_type,
                description=f"Search relevance too low: {metrics.relevance_score:.2f}",
                impact="Poor search quality, users can't find content",
                recommendations=[
                    "Improve search index configuration",
                    "Tune scoring parameters",
                    "Add synonyms and stemming",
                    "Implement machine learning ranking"
                ],
                detected_at=datetime.utcnow(),
                metrics={'relevance_score': metrics.relevance_score}
            ))
        
        # Check error rate
        if metrics.error_count > 0:
            bottlenecks.append(SearchBottleneck(
                bottleneck_type="search_errors",
                severity="high",
                engine_type=metrics.engine_type,
                description="Search errors detected",
                impact="Search functionality disrupted",
                recommendations=[
                    "Check search engine health",
                    "Validate query syntax",
                    "Monitor system resources",
                    "Check network connectivity"
                ],
                detected_at=datetime.utcnow(),
                metrics={'error_count': metrics.error_count}
            ))
        
        # Store bottlenecks
        for bottleneck in bottlenecks:
            self.bottlenecks_history.append(bottleneck)

    def profile_indexing_operation(self, 
                                 documents: List[Dict],
                                 index_name: str,
                                 engine_type: SearchEngineType = SearchEngineType.ELASTICSEARCH,
                                 **kwargs) -> SearchMetrics:
        """
        Profile an indexing operation
        
        Args:
            documents: Documents to index
            index_name: Index name
            engine_type: Search engine type
            **kwargs: Additional indexing parameters
            
        Returns:
            SearchMetrics with indexing results
        """
        operation_id = f"index_{engine_type.value}_{int(time.time())}"
        start_time = time.time()
        
        try:
            # Execute indexing based on engine type
            if engine_type == SearchEngineType.ELASTICSEARCH:
                result = self._execute_elasticsearch_indexing(documents, index_name, **kwargs)
            elif engine_type == SearchEngineType.SOLR:
                result = self._execute_solr_indexing(documents, index_name, **kwargs)
            else:
                result = self._execute_generic_indexing(documents, index_name, **kwargs)
            
            end_time = time.time()
            index_time_ms = (end_time - start_time) * 1000
            
            # Create metrics
            metrics = SearchMetrics(
                operation_id=operation_id,
                engine_type=engine_type,
                operation=SearchOperation.INDEX,
                query_time_ms=0.0,
                index_time_ms=index_time_ms,
                total_hits=len(documents),
                returned_results=result.get('indexed_count', 0),
                relevance_score=0.0,
                cpu_usage=0.0,
                memory_usage_mb=0.0,
                cache_hit_rate=0.0,
                error_count=result.get('error_count', 0),
                timestamp=datetime.utcnow(),
                metadata={
                    'index_name': index_name,
                    'document_count': len(documents),
                    'operation_type': 'bulk_index' if len(documents) > 1 else 'single_index',
                    'took_ms': result.get('took_ms', index_time_ms)
                }
            )
            
            # Store metrics
            self.search_metrics_history.append(metrics)
            
            return metrics
            
        except Exception as e:
            logger.error(f"Error profiling indexing operation: {e}")
            raise

    def _execute_elasticsearch_indexing(self, documents: List[Dict], index_name: str, **kwargs) -> Dict:
        """Execute Elasticsearch indexing"""
        result = {'error': False, 'indexed_count': 0, 'error_count': 0}
        
        if 'elasticsearch' not in self.search_clients:
            result['error'] = True
            result['error_message'] = "Elasticsearch client not available"
            return result
        
        try:
            es = self.search_clients['elasticsearch']
            
            if len(documents) == 1:
                # Single document indexing
                doc = documents[0]
                response = es.index(
                    index=index_name,
                    body=doc,
                    **kwargs
                )
                result['indexed_count'] = 1
                result['took_ms'] = 0  # ES doesn't provide timing for single docs
            else:
                # Bulk indexing
                from elasticsearch.helpers import bulk
                
                actions = []
                for doc in documents:
                    action = {
                        '_index': index_name,
                        '_source': doc
                    }
                    actions.append(action)
                
                success_count, failed_items = bulk(es, actions)
                result['indexed_count'] = success_count
                result['error_count'] = len(failed_items) if failed_items else 0
                
        except Exception as e:
            result['error'] = True
            result['error_message'] = str(e)
            result['error_count'] = len(documents)
        
        return result

    def _execute_solr_indexing(self, documents: List[Dict], index_name: str, **kwargs) -> Dict:
        """Execute Solr indexing"""
        result = {'error': False, 'indexed_count': 0, 'error_count': 0}
        
        if 'solr' not in self.search_clients:
            result['error'] = True
            result['error_message'] = "Solr client not available"
            return result
        
        try:
            solr = self.search_clients['solr']
            
            # Add documents
            solr.add(documents)
            solr.commit()
            
            result['indexed_count'] = len(documents)
            
        except Exception as e:
            result['error'] = True
            result['error_message'] = str(e)
            result['error_count'] = len(documents)
        
        return result

    def _execute_generic_indexing(self, documents: List[Dict], index_name: str, **kwargs) -> Dict:
        """Execute generic indexing"""
        return {
            'error': False,
            'indexed_count': len(documents),
            'error_count': 0,
            'index_type': 'generic'
        }

    def get_performance_summary(self) -> Dict[str, Any]:
        """Get search engine performance summary"""
        if not self.search_metrics_history:
            return {"error": "No metrics available"}
        
        recent_metrics = list(self.search_metrics_history)[-1000:]  # Last 1000 operations
        
        # Calculate statistics
        search_metrics = [m for m in recent_metrics if m.operation == SearchOperation.SEARCH]
        index_metrics = [m for m in recent_metrics if m.operation == SearchOperation.INDEX]
        
        search_times = [m.query_time_ms for m in search_metrics]
        index_times = [m.index_time_ms for m in index_metrics]
        relevance_scores = [m.relevance_score for m in search_metrics if m.relevance_score > 0]
        error_count = sum(1 for m in recent_metrics if m.error_count > 0)
        
        return {
            "summary": {
                "total_operations": len(recent_metrics),
                "search_operations": len(search_metrics),
                "index_operations": len(index_metrics),
                "avg_search_time_ms": statistics.mean(search_times) if search_times else 0,
                "p95_search_time_ms": statistics.quantiles(search_times, n=20)[18] if len(search_times) > 20 else 0,
                "avg_index_time_ms": statistics.mean(index_times) if index_times else 0,
                "avg_relevance_score": statistics.mean(relevance_scores) if relevance_scores else 0,
                "error_rate": (error_count / len(recent_metrics)) * 100,
                "active_queries": len(self.active_queries)
            },
            "by_engine_type": self._get_metrics_by_engine_type(),
            "by_operation": self._get_metrics_by_operation_type(),
            "bottlenecks": len(self.bottlenecks_history),
            "recommendations": self._get_search_optimization_recommendations()
        }

    def _get_metrics_by_engine_type(self) -> Dict[str, Dict]:
        """Get metrics grouped by engine type"""
        metrics_by_engine = defaultdict(list)
        
        for metrics in list(self.search_metrics_history)[-1000:]:
            metrics_by_engine[metrics.engine_type.value].append(metrics)
        
        result = {}
        for engine_type, metrics_list in metrics_by_engine.items():
            search_times = [m.query_time_ms for m in metrics_list if m.operation == SearchOperation.SEARCH]
            relevance_scores = [m.relevance_score for m in metrics_list if m.relevance_score > 0]
            
            result[engine_type] = {
                "operations": len(metrics_list),
                "avg_search_time_ms": statistics.mean(search_times) if search_times else 0,
                "avg_relevance_score": statistics.mean(relevance_scores) if relevance_scores else 0,
                "error_rate": (sum(1 for m in metrics_list if m.error_count > 0) / len(metrics_list)) * 100
            }
        
        return result

    def _get_metrics_by_operation_type(self) -> Dict[str, Dict]:
        """Get metrics grouped by operation type"""
        metrics_by_op = defaultdict(list)
        
        for metrics in list(self.search_metrics_history)[-1000:]:
            metrics_by_op[metrics.operation.value].append(metrics)
        
        result = {}
        for operation, metrics_list in metrics_by_op.items():
            if operation == 'search':
                times = [m.query_time_ms for m in metrics_list]
            else:
                times = [m.index_time_ms for m in metrics_list]
            
            result[operation] = {
                "operations": len(metrics_list),
                "avg_time_ms": statistics.mean(times) if times else 0,
                "error_rate": (sum(1 for m in metrics_list if m.error_count > 0) / len(metrics_list)) * 100
            }
        
        return result

    def _get_search_optimization_recommendations(self) -> List[str]:
        """Get search optimization recommendations"""
        recommendations = []
        
        if not self.search_metrics_history:
            return ["Start profiling search operations to get recommendations"]
        
        recent_metrics = list(self.search_metrics_history)[-100:]
        search_metrics = [m for m in recent_metrics if m.operation == SearchOperation.SEARCH]
        
        if search_metrics:
            avg_search_time = statistics.mean([m.query_time_ms for m in search_metrics])
            avg_relevance = statistics.mean([m.relevance_score for m in search_metrics if m.relevance_score > 0])
            error_rate = (sum(1 for m in search_metrics if m.error_count > 0) / len(search_metrics)) * 100
            
            if avg_search_time > 500:
                recommendations.append("High search latency - optimize queries and indexes")
            if avg_relevance < 0.7:
                recommendations.append("Low relevance scores - improve search configuration")
            if error_rate > 1:
                recommendations.append("Search errors detected - check engine health")
            if len(self.active_queries) > 50:
                recommendations.append("High concurrent queries - consider scaling search cluster")
        
        if not recommendations:
            recommendations.append("Search performance is optimal")
        
        return recommendations

    def get_recent_bottlenecks(self, limit: int = 10) -> List[SearchBottleneck]:
        """Get recent search bottlenecks"""
        return list(self.bottlenecks_history)[-limit:]

    def export_metrics(self, format: str = "json") -> str:
        """Export search metrics"""
        data = {
            "search_metrics": [
                {
                    "operation_id": m.operation_id,
                    "engine_type": m.engine_type.value,
                    "operation": m.operation.value,
                    "query_time_ms": m.query_time_ms,
                    "total_hits": m.total_hits,
                    "relevance_score": m.relevance_score,
                    "timestamp": m.timestamp.isoformat()
                }
                for m in list(self.search_metrics_history)[-1000:]
            ],
            "bottlenecks": [
                {
                    "type": b.bottleneck_type,
                    "severity": b.severity,
                    "engine_type": b.engine_type.value,
                    "description": b.description,
                    "detected_at": b.detected_at.isoformat()
                }
                for b in list(self.bottlenecks_history)[-100:]
            ]
        }
        
        if format == "json":
            return json.dumps(data, indent=2)
        else:
            return str(data)


# Factory function
def create_search_engine_profiler(monitoring_interval: float = 5.0,
                                max_history_size: int = 10000,
                                start_monitoring: bool = True) -> SearchEngineProfiler:
    """
    Create and configure a search engine profiler
    
    Args:
        monitoring_interval: Monitoring interval in seconds
        max_history_size: Maximum number of metrics to store
        start_monitoring: Start background monitoring
        
    Returns:
        Configured SearchEngineProfiler instance
    """
    profiler = SearchEngineProfiler(
        monitoring_interval=monitoring_interval,
        max_history_size=max_history_size
    )
    
    if start_monitoring:
        profiler.start_monitoring()
    
    return profiler


# Main execution
if __name__ == "__main__":
    # Example usage
    profiler = create_search_engine_profiler()
    
    try:
        # Example: Profile a search query
        metrics = profiler.profile_search_query(
            query="content creators video tutorial",
            index_name="creators_content",
            engine_type=SearchEngineType.ELASTICSEARCH,
            size=10
        )
        
        print(f"Search query latency: {metrics.query_time_ms:.2f}ms")
        print(f"Total hits: {metrics.total_hits}")
        print(f"Relevance score: {metrics.relevance_score:.2f}")
        
        # Get performance summary
        summary = profiler.get_performance_summary()
        print(f"Performance summary: {json.dumps(summary, indent=2)}")
        
    finally:
        profiler.stop_monitoring()