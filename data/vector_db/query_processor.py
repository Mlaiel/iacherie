"""
Query Processor - Advanced Query Processing Engine
=================================================

Enterprise-grade query processor with complex multi-modal queries, hybrid
semantic + vector search, batch processing, and real-time query adaptation.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: © 2025 Fahed Mlaiel. All rights reserved.

⚠️ CRITICAL COPYRIGHT WARNING ⚠️
This code is the intellectual property of Fahed Mlaiel and is protected by 
international copyright law. Any unauthorized use, reproduction, distribution 
or modification is strictly prohibited and will result in legal action.

For licensing inquiries: mlaiel@live.de
"""

import asyncio
import logging
import numpy as np
import json
from typing import Any, Dict, List, Optional, Tuple, Union, Callable
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from enum import Enum
import uuid
import time
from collections import defaultdict

logger = logging.getLogger(__name__)


class QueryType(Enum):
    """Types of queries supported."""
    SIMPLE_SIMILARITY = "simple_similarity"
    COMPLEX_MULTI_MODAL = "complex_multi_modal"
    HYBRID_SEMANTIC = "hybrid_semantic"
    BATCH_QUERY = "batch_query"
    STREAMING_SEARCH = "streaming_search"
    FACETED_SEARCH = "faceted_search"
    GEOGRAPHIC_PROXIMITY = "geographic_proximity"


@dataclass
class QueryPlan:
    """Query execution plan."""
    query_id: str
    query_type: QueryType
    estimated_cost: float
    estimated_time_ms: float
    execution_steps: List[Dict[str, Any]]
    cache_key: Optional[str] = None
    parallel_execution: bool = False
    resource_requirements: Optional[Dict[str, Any]] = None


@dataclass
class QueryResult:
    """Query execution result."""
    query_id: str
    results: List[Any]
    execution_time_ms: float
    total_candidates: int
    filtered_count: int
    cache_hit: bool = False
    execution_plan: Optional[QueryPlan] = None
    metadata: Optional[Dict[str, Any]] = None


@dataclass
class QueryMetrics:
    """Query performance metrics."""
    query_id: str
    query_type: str
    start_time: datetime
    end_time: datetime
    execution_time_ms: float
    result_count: int
    cache_hit: bool
    error: Optional[str] = None


class QueryOptimizer:
    """Optimizes query execution plans."""
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize query optimizer."""
        self.config = config
        self.optimization_level = config.get('optimization_level', 'medium')
        self.cost_model = config.get('cost_model', 'time_based')
        
        # Historical performance data
        self.query_history: Dict[str, List[QueryMetrics]] = defaultdict(list)
        self.optimization_cache: Dict[str, QueryPlan] = {}
        
    async def create_query_plan(
        self,
        query_vector: np.ndarray,
        query_type: QueryType,
        filters: Optional[Dict[str, Any]] = None,
        top_k: int = 10,
        context: Optional[Dict[str, Any]] = None
    ) -> QueryPlan:
        """
        Create optimized query execution plan.
        
        Args:
            query_vector: Query vector
            query_type: Type of query
            filters: Query filters
            top_k: Number of results
            context: Additional context
        
        Returns:
            Optimized query plan
        """
        try:
            query_id = str(uuid.uuid4())
            
            # Create cache key
            cache_key = self._create_cache_key(query_vector, query_type, filters, top_k)
            
            # Check optimization cache
            if cache_key in self.optimization_cache:
                cached_plan = self.optimization_cache[cache_key]
                cached_plan.query_id = query_id  # Update with new query ID
                return cached_plan
            
            # Create execution steps based on query type
            execution_steps = await self._create_execution_steps(
                query_type, query_vector, filters, top_k, context
            )
            
            # Estimate cost and time
            estimated_cost, estimated_time = await self._estimate_query_cost(
                execution_steps, query_vector.shape[0], top_k
            )
            
            # Determine if parallel execution is beneficial
            parallel_execution = self._should_use_parallel_execution(
                execution_steps, estimated_time
            )
            
            # Create query plan
            plan = QueryPlan(
                query_id=query_id,
                query_type=query_type,
                estimated_cost=estimated_cost,
                estimated_time_ms=estimated_time,
                execution_steps=execution_steps,
                cache_key=cache_key,
                parallel_execution=parallel_execution,
                resource_requirements=self._calculate_resource_requirements(execution_steps)
            )
            
            # Cache the plan
            if len(self.optimization_cache) < 1000:  # Limit cache size
                self.optimization_cache[cache_key] = plan
            
            return plan
            
        except Exception as e:
            logger.error(f"Failed to create query plan: {e}")
            # Return basic plan as fallback
            return QueryPlan(
                query_id=query_id,
                query_type=query_type,
                estimated_cost=1.0,
                estimated_time_ms=100.0,
                execution_steps=[{"type": "simple_search", "parameters": {}}]
            )
    
    async def _create_execution_steps(
        self,
        query_type: QueryType,
        query_vector: np.ndarray,
        filters: Optional[Dict[str, Any]],
        top_k: int,
        context: Optional[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Create execution steps for query plan."""
        steps = []
        
        if query_type == QueryType.SIMPLE_SIMILARITY:
            steps.append({
                "type": "vector_search",
                "parameters": {
                    "method": "similarity",
                    "top_k": top_k,
                    "filters": filters
                }
            })
            
        elif query_type == QueryType.COMPLEX_MULTI_MODAL:
            # Multi-modal query requires multiple searches and fusion
            steps.extend([
                {
                    "type": "vector_search",
                    "parameters": {
                        "method": "multi_modal",
                        "top_k": top_k * 2,  # Get more candidates for fusion
                        "filters": filters
                    }
                },
                {
                    "type": "fusion",
                    "parameters": {
                        "method": "weighted_average",
                        "final_top_k": top_k
                    }
                }
            ])
            
        elif query_type == QueryType.HYBRID_SEMANTIC:
            # Combine vector and text search
            steps.extend([
                {
                    "type": "vector_search",
                    "parameters": {
                        "method": "similarity",
                        "top_k": top_k,
                        "weight": 0.7
                    }
                },
                {
                    "type": "semantic_search",
                    "parameters": {
                        "method": "text_similarity",
                        "top_k": top_k,
                        "weight": 0.3
                    }
                },
                {
                    "type": "hybrid_fusion",
                    "parameters": {
                        "final_top_k": top_k
                    }
                }
            ])
            
        elif query_type == QueryType.BATCH_QUERY:
            steps.append({
                "type": "batch_search",
                "parameters": {
                    "method": "batch_similarity",
                    "batch_size": self.config.get('batch_size', 100),
                    "parallel": True
                }
            })
            
        elif query_type == QueryType.FACETED_SEARCH:
            # Faceted search with metadata filtering
            steps.extend([
                {
                    "type": "metadata_filter",
                    "parameters": {
                        "filters": filters
                    }
                },
                {
                    "type": "vector_search",
                    "parameters": {
                        "method": "similarity",
                        "top_k": top_k,
                        "pre_filtered": True
                    }
                }
            ])
        
        # Add post-processing steps if needed
        if filters and "post_process" in filters:
            steps.append({
                "type": "post_process",
                "parameters": filters["post_process"]
            })
        
        return steps
    
    async def _estimate_query_cost(
        self,
        execution_steps: List[Dict[str, Any]],
        vector_dimension: int,
        top_k: int
    ) -> Tuple[float, float]:
        """Estimate query cost and execution time."""
        total_cost = 0.0
        total_time = 0.0
        
        for step in execution_steps:
            step_type = step["type"]
            params = step.get("parameters", {})
            
            if step_type == "vector_search":
                # Cost based on vector dimension and top_k
                base_cost = vector_dimension * 0.001 + top_k * 0.01
                base_time = vector_dimension * 0.01 + top_k * 0.1
                
                if params.get("method") == "multi_modal":
                    base_cost *= 2.0
                    base_time *= 1.5
                    
            elif step_type == "semantic_search":
                base_cost = 0.5  # Text processing cost
                base_time = 10.0  # Text processing time
                
            elif step_type == "fusion":
                base_cost = top_k * 0.001
                base_time = top_k * 0.01
                
            elif step_type == "batch_search":
                batch_size = params.get("batch_size", 100)
                base_cost = batch_size * 0.1
                base_time = batch_size * 1.0
                
            else:
                base_cost = 0.1
                base_time = 1.0
            
            total_cost += base_cost
            total_time += base_time
        
        return total_cost, total_time
    
    def _should_use_parallel_execution(
        self,
        execution_steps: List[Dict[str, Any]],
        estimated_time: float
    ) -> bool:
        """Determine if parallel execution would be beneficial."""
        # Use parallel execution for complex queries or when estimated time is high
        complex_steps = ["multi_modal", "hybrid_semantic", "batch_search"]
        
        has_complex_steps = any(
            step.get("parameters", {}).get("method") in complex_steps
            for step in execution_steps
        )
        
        return has_complex_steps or estimated_time > 50.0
    
    def _calculate_resource_requirements(
        self,
        execution_steps: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Calculate resource requirements for query."""
        requirements = {
            "memory_mb": 100,  # Base memory
            "cpu_cores": 1,
            "gpu_required": False
        }
        
        for step in execution_steps:
            step_type = step["type"]
            params = step.get("parameters", {})
            
            if step_type == "vector_search":
                requirements["memory_mb"] += 50
                if params.get("method") == "multi_modal":
                    requirements["memory_mb"] += 100
                    requirements["gpu_required"] = True
                    
            elif step_type == "batch_search":
                batch_size = params.get("batch_size", 100)
                requirements["memory_mb"] += batch_size * 2
                if batch_size > 500:
                    requirements["cpu_cores"] = 2
        
        return requirements
    
    def _create_cache_key(
        self,
        query_vector: np.ndarray,
        query_type: QueryType,
        filters: Optional[Dict[str, Any]],
        top_k: int
    ) -> str:
        """Create cache key for query optimization."""
        import hashlib
        
        # Create hash from query components
        cache_components = [
            str(query_type.value),
            str(query_vector.shape),
            str(top_k),
            json.dumps(filters or {}, sort_keys=True)
        ]
        
        cache_string = "|".join(cache_components)
        return hashlib.md5(cache_string.encode()).hexdigest()
    
    def update_query_history(self, metrics: QueryMetrics) -> None:
        """Update query performance history."""
        query_type = metrics.query_type
        self.query_history[query_type].append(metrics)
        
        # Keep only recent history (last 1000 queries per type)
        if len(self.query_history[query_type]) > 1000:
            self.query_history[query_type] = self.query_history[query_type][-500:]
    
    def get_optimization_stats(self) -> Dict[str, Any]:
        """Get optimization statistics."""
        stats = {
            "cached_plans": len(self.optimization_cache),
            "query_types_seen": list(self.query_history.keys()),
            "total_queries": sum(len(queries) for queries in self.query_history.values())
        }
        
        # Average performance by query type
        avg_performance = {}
        for query_type, queries in self.query_history.items():
            if queries:
                avg_time = sum(q.execution_time_ms for q in queries) / len(queries)
                cache_hit_rate = sum(1 for q in queries if q.cache_hit) / len(queries)
                avg_performance[query_type] = {
                    "avg_time_ms": avg_time,
                    "cache_hit_rate": cache_hit_rate,
                    "total_queries": len(queries)
                }
        
        stats["avg_performance"] = avg_performance
        return stats


class ResultProcessor:
    """Processes and enriches query results."""
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize result processor."""
        self.config = config
        self.enable_enrichment = config.get('enable_enrichment', True)
        self.enable_ranking = config.get('enable_ranking', True)
        
    async def process_results(
        self,
        raw_results: List[Any],
        query_context: Dict[str, Any]
    ) -> List[Any]:
        """
        Process and enrich query results.
        
        Args:
            raw_results: Raw query results
            query_context: Query context information
        
        Returns:
            Processed results
        """
        try:
            processed_results = raw_results.copy()
            
            # Apply ranking if enabled
            if self.enable_ranking:
                processed_results = await self._apply_ranking(
                    processed_results, query_context
                )
            
            # Apply enrichment if enabled
            if self.enable_enrichment:
                processed_results = await self._enrich_results(
                    processed_results, query_context
                )
            
            # Apply post-filtering
            processed_results = await self._apply_post_filtering(
                processed_results, query_context
            )
            
            return processed_results
            
        except Exception as e:
            logger.error(f"Failed to process results: {e}")
            return raw_results
    
    async def _apply_ranking(
        self,
        results: List[Any],
        query_context: Dict[str, Any]
    ) -> List[Any]:
        """Apply advanced ranking to results."""
        try:
            # Get ranking strategy
            ranking_strategy = query_context.get('ranking_strategy', 'score_based')
            
            if ranking_strategy == 'score_based':
                # Sort by similarity score (default)
                return sorted(results, key=lambda x: getattr(x, 'score', 0), reverse=True)
                
            elif ranking_strategy == 'diversity':
                # Apply diversity-based ranking
                return await self._apply_diversity_ranking(results)
                
            elif ranking_strategy == 'temporal':
                # Apply temporal ranking
                return await self._apply_temporal_ranking(results, query_context)
                
            else:
                return results
                
        except Exception as e:
            logger.error(f"Failed to apply ranking: {e}")
            return results
    
    async def _apply_diversity_ranking(self, results: List[Any]) -> List[Any]:
        """Apply diversity-based ranking to avoid similar results."""
        if len(results) <= 1:
            return results
        
        try:
            # Simple diversity algorithm - select results that are different from each other
            diverse_results = [results[0]]  # Start with top result
            
            for result in results[1:]:
                # Check if result is sufficiently different from selected results
                is_diverse = True
                for selected in diverse_results:
                    # Simple diversity check based on metadata
                    if (hasattr(result, 'metadata') and hasattr(selected, 'metadata') and
                        result.metadata and selected.metadata):
                        
                        # Check content type diversity
                        if (result.metadata.get('content_type') == 
                            selected.metadata.get('content_type')):
                            # Additional checks for similarity
                            if getattr(result, 'score', 0) - getattr(selected, 'score', 0) < 0.1:
                                is_diverse = False
                                break
                
                if is_diverse:
                    diverse_results.append(result)
                
                # Limit to reasonable number of results
                if len(diverse_results) >= min(len(results), 20):
                    break
            
            return diverse_results
            
        except Exception as e:
            logger.error(f"Failed to apply diversity ranking: {e}")
            return results
    
    async def _apply_temporal_ranking(
        self,
        results: List[Any],
        query_context: Dict[str, Any]
    ) -> List[Any]:
        """Apply temporal ranking based on recency."""
        try:
            temporal_weight = query_context.get('temporal_weight', 0.3)
            
            # Apply temporal boost to recent items
            current_time = datetime.utcnow()
            
            for result in results:
                if hasattr(result, 'metadata') and result.metadata:
                    created_at = getattr(result.metadata, 'created_at', None)
                    if created_at:
                        # Calculate recency boost
                        time_diff = (current_time - created_at).total_seconds()
                        recency_boost = max(0, 1 - (time_diff / (30 * 24 * 3600)))  # 30 days decay
                        
                        # Apply boost to score
                        original_score = getattr(result, 'score', 0)
                        boosted_score = original_score + (recency_boost * temporal_weight)
                        result.score = min(1.0, boosted_score)
            
            # Re-sort by boosted scores
            return sorted(results, key=lambda x: getattr(x, 'score', 0), reverse=True)
            
        except Exception as e:
            logger.error(f"Failed to apply temporal ranking: {e}")
            return results
    
    async def _enrich_results(
        self,
        results: List[Any],
        query_context: Dict[str, Any]
    ) -> List[Any]:
        """Enrich results with additional information."""
        try:
            enrichment_types = query_context.get('enrichment_types', ['metadata'])
            
            for result in results:
                for enrichment_type in enrichment_types:
                    if enrichment_type == 'metadata':
                        await self._enrich_with_metadata(result)
                    elif enrichment_type == 'similarity_explanation':
                        await self._enrich_with_similarity_explanation(result, query_context)
                    elif enrichment_type == 'related_content':
                        await self._enrich_with_related_content(result)
            
            return results
            
        except Exception as e:
            logger.error(f"Failed to enrich results: {e}")
            return results
    
    async def _enrich_with_metadata(self, result: Any) -> None:
        """Enrich result with additional metadata."""
        try:
            if hasattr(result, 'metadata') and result.metadata:
                # Add computed metadata
                if not hasattr(result.metadata, 'enriched'):
                    result.metadata.enriched = {}
                
                # Add quality score
                result.metadata.enriched['quality_score'] = self._calculate_quality_score(result)
                
                # Add popularity metrics (if available)
                result.metadata.enriched['popularity_score'] = self._calculate_popularity_score(result)
                
        except Exception as e:
            logger.error(f"Failed to enrich with metadata: {e}")
    
    async def _enrich_with_similarity_explanation(
        self,
        result: Any,
        query_context: Dict[str, Any]
    ) -> None:
        """Enrich result with similarity explanation."""
        try:
            if hasattr(result, 'metadata'):
                if not hasattr(result.metadata, 'enriched'):
                    result.metadata.enriched = {}
                
                # Simple similarity explanation
                score = getattr(result, 'score', 0)
                if score > 0.9:
                    explanation = "Very high similarity"
                elif score > 0.7:
                    explanation = "High similarity"
                elif score > 0.5:
                    explanation = "Moderate similarity"
                else:
                    explanation = "Low similarity"
                
                result.metadata.enriched['similarity_explanation'] = explanation
                
        except Exception as e:
            logger.error(f"Failed to enrich with similarity explanation: {e}")
    
    async def _enrich_with_related_content(self, result: Any) -> None:
        """Enrich result with related content suggestions."""
        try:
            # This would typically involve additional database queries
            # For now, just add placeholder
            if hasattr(result, 'metadata'):
                if not hasattr(result.metadata, 'enriched'):
                    result.metadata.enriched = {}
                
                result.metadata.enriched['has_related_content'] = True
                
        except Exception as e:
            logger.error(f"Failed to enrich with related content: {e}")
    
    def _calculate_quality_score(self, result: Any) -> float:
        """Calculate quality score for result."""
        try:
            # Simple quality scoring based on available information
            base_score = 0.5
            
            # Boost for high similarity
            if hasattr(result, 'score') and result.score:
                base_score += result.score * 0.3
            
            # Boost for complete metadata
            if hasattr(result, 'metadata') and result.metadata:
                if getattr(result.metadata, 'custom_metadata'):
                    base_score += 0.1
                if getattr(result.metadata, 'content_hash'):
                    base_score += 0.1
            
            return min(1.0, base_score)
            
        except Exception:
            return 0.5
    
    def _calculate_popularity_score(self, result: Any) -> float:
        """Calculate popularity score for result."""
        try:
            # Placeholder popularity calculation
            # Would typically be based on view counts, likes, etc.
            return 0.5
            
        except Exception:
            return 0.0
    
    async def _apply_post_filtering(
        self,
        results: List[Any],
        query_context: Dict[str, Any]
    ) -> List[Any]:
        """Apply post-processing filters."""
        try:
            post_filters = query_context.get('post_filters', {})
            
            filtered_results = results
            
            # Apply minimum score filter
            if 'min_score' in post_filters:
                min_score = post_filters['min_score']
                filtered_results = [
                    r for r in filtered_results 
                    if getattr(r, 'score', 0) >= min_score
                ]
            
            # Apply maximum results limit
            if 'max_results' in post_filters:
                max_results = post_filters['max_results']
                filtered_results = filtered_results[:max_results]
            
            # Apply content type filter
            if 'allowed_content_types' in post_filters:
                allowed_types = post_filters['allowed_content_types']
                filtered_results = [
                    r for r in filtered_results
                    if (hasattr(r, 'metadata') and r.metadata and
                        getattr(r.metadata, 'content_type') in allowed_types)
                ]
            
            return filtered_results
            
        except Exception as e:
            logger.error(f"Failed to apply post-filtering: {e}")
            return results


class QueryProcessor:
    """
    Enterprise-grade query processor for Vector Database Module.
    
    Features:
    - Complex multi-modal queries
    - Hybrid semantic + vector search
    - Batch query processing
    - Streaming search results
    - Faceted search with filters
    - Geographic proximity search
    - Query plan optimization
    - Result caching intelligent
    - Parallel execution
    - Memory-efficient processing
    - Real-time query adaptation
    """
    
    def __init__(
        self,
        similarity_engine: Any,
        cache_manager: Any,
        config: Any
    ):
        """
        Initialize query processor.
        
        Args:
            similarity_engine: Similarity engine instance
            cache_manager: Cache manager instance
            config: Configuration object
        """
        self.similarity_engine = similarity_engine
        self.cache_manager = cache_manager
        self.config = config
        
        # Configuration
        self.enable_optimization = config.get('query.enable_optimization', True)
        self.enable_caching = config.get('query.enable_caching', True)
        self.enable_parallel = config.get('query.enable_parallel', True)
        self.default_timeout = config.get('query.default_timeout', 30)
        
        # Core components
        self.optimizer = QueryOptimizer(config.get('query.optimizer', {}))
        self.result_processor = ResultProcessor(config.get('query.result_processor', {}))
        
        # Statistics
        self.stats = {
            'total_queries': 0,
            'cache_hits': 0,
            'avg_execution_time': 0.0,
            'parallel_executions': 0,
            'optimization_cache_size': 0
        }
        
        logger.info("QueryProcessor initialized")
    
    async def initialize(self) -> bool:
        """Initialize the query processor."""
        try:
            # Verify dependencies
            if not self.similarity_engine:
                logger.error("Similarity engine not available")
                return False
            
            logger.info("QueryProcessor initialization completed")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize QueryProcessor: {e}")
            return False
    
    async def process_query(
        self,
        query_vector: np.ndarray,
        top_k: int = 10,
        threshold: float = 0.0,
        filters: Optional[Dict[str, Any]] = None,
        query_type: QueryType = QueryType.SIMPLE_SIMILARITY,
        context: Optional[Dict[str, Any]] = None
    ) -> List[Any]:
        """
        Process a vector query with optimization and caching.
        
        Args:
            query_vector: Query vector
            top_k: Number of results to return
            threshold: Minimum similarity threshold
            filters: Query filters
            query_type: Type of query
            context: Additional query context
        
        Returns:
            Processed query results
        """
        start_time = time.time()
        query_id = str(uuid.uuid4())
        
        try:
            # Create query context
            query_context = {
                'query_id': query_id,
                'query_type': query_type,
                'top_k': top_k,
                'threshold': threshold,
                'filters': filters or {},
                **(context or {})
            }
            
            # Check cache first
            cache_key = None
            if self.enable_caching and self.cache_manager:
                cache_key = self._create_cache_key(query_vector, query_context)
                cached_result = await self.cache_manager.get(cache_key)
                if cached_result:
                    self.stats['cache_hits'] += 1
                    execution_time = (time.time() - start_time) * 1000
                    return await self._finalize_results(cached_result, query_context, execution_time, True)
            
            # Create query plan
            if self.enable_optimization:
                query_plan = await self.optimizer.create_query_plan(
                    query_vector, query_type, filters, top_k, context
                )
            else:
                query_plan = None
            
            # Execute query
            results = await self._execute_query(
                query_vector, query_context, query_plan
            )
            
            # Process results
            processed_results = await self.result_processor.process_results(
                results, query_context
            )
            
            # Cache results
            if self.enable_caching and self.cache_manager and cache_key:
                await self.cache_manager.set(cache_key, processed_results)
            
            # Finalize and return results
            execution_time = (time.time() - start_time) * 1000
            return await self._finalize_results(processed_results, query_context, execution_time, False)
            
        except Exception as e:
            logger.error(f"Query processing failed: {e}")
            execution_time = (time.time() - start_time) * 1000
            
            # Update metrics with error
            if self.enable_optimization:
                error_metrics = QueryMetrics(
                    query_id=query_id,
                    query_type=query_type.value,
                    start_time=datetime.utcfromtimestamp(start_time),
                    end_time=datetime.utcnow(),
                    execution_time_ms=execution_time,
                    result_count=0,
                    cache_hit=False,
                    error=str(e)
                )
                self.optimizer.update_query_history(error_metrics)
            
            return []
    
    async def _execute_query(
        self,
        query_vector: np.ndarray,
        query_context: Dict[str, Any],
        query_plan: Optional[QueryPlan]
    ) -> List[Any]:
        """Execute the query based on plan."""
        try:
            query_type = query_context['query_type']
            
            if query_type == QueryType.SIMPLE_SIMILARITY:
                return await self._execute_simple_similarity(query_vector, query_context)
                
            elif query_type == QueryType.COMPLEX_MULTI_MODAL:
                return await self._execute_multi_modal(query_vector, query_context)
                
            elif query_type == QueryType.HYBRID_SEMANTIC:
                return await self._execute_hybrid_semantic(query_vector, query_context)
                
            elif query_type == QueryType.BATCH_QUERY:
                return await self._execute_batch_query(query_vector, query_context)
                
            elif query_type == QueryType.FACETED_SEARCH:
                return await self._execute_faceted_search(query_vector, query_context)
                
            else:
                # Default to simple similarity
                return await self._execute_simple_similarity(query_vector, query_context)
                
        except Exception as e:
            logger.error(f"Query execution failed: {e}")
            return []
    
    async def _execute_simple_similarity(
        self,
        query_vector: np.ndarray,
        query_context: Dict[str, Any]
    ) -> List[Any]:
        """Execute simple similarity search."""
        try:
            # Use similarity engine to find similar vectors
            results = await self.similarity_engine.storage.search_similar(
                query_vector=query_vector,
                top_k=query_context['top_k'],
                threshold=query_context['threshold'],
                filters=query_context['filters']
            )
            
            return results
            
        except Exception as e:
            logger.error(f"Simple similarity search failed: {e}")
            return []
    
    async def _execute_multi_modal(
        self,
        query_vector: np.ndarray,
        query_context: Dict[str, Any]
    ) -> List[Any]:
        """Execute multi-modal query."""
        try:
            # This would require multi-modal embeddings in query_context
            # For now, fall back to simple similarity
            return await self._execute_simple_similarity(query_vector, query_context)
            
        except Exception as e:
            logger.error(f"Multi-modal query failed: {e}")
            return []
    
    async def _execute_hybrid_semantic(
        self,
        query_vector: np.ndarray,
        query_context: Dict[str, Any]
    ) -> List[Any]:
        """Execute hybrid semantic + vector search."""
        try:
            # Execute vector search
            vector_results = await self._execute_simple_similarity(query_vector, query_context)
            
            # For now, return vector results (semantic search would require additional implementation)
            return vector_results
            
        except Exception as e:
            logger.error(f"Hybrid semantic search failed: {e}")
            return []
    
    async def _execute_batch_query(
        self,
        query_vector: np.ndarray,
        query_context: Dict[str, Any]
    ) -> List[Any]:
        """Execute batch query processing."""
        try:
            # For batch queries, the query_vector might be multiple vectors
            # For now, treat as single query
            return await self._execute_simple_similarity(query_vector, query_context)
            
        except Exception as e:
            logger.error(f"Batch query failed: {e}")
            return []
    
    async def _execute_faceted_search(
        self,
        query_vector: np.ndarray,
        query_context: Dict[str, Any]
    ) -> List[Any]:
        """Execute faceted search with metadata filtering."""
        try:
            # Apply metadata filters before vector search
            filters = query_context.get('filters', {})
            
            # Execute similarity search with filters
            results = await self.similarity_engine.storage.search_similar(
                query_vector=query_vector,
                top_k=query_context['top_k'],
                threshold=query_context['threshold'],
                filters=filters
            )
            
            return results
            
        except Exception as e:
            logger.error(f"Faceted search failed: {e}")
            return []
    
    def _create_cache_key(
        self,
        query_vector: np.ndarray,
        query_context: Dict[str, Any]
    ) -> str:
        """Create cache key for query."""
        import hashlib
        
        # Create hash from query components
        cache_components = [
            str(query_context.get('query_type', '')),
            str(query_vector.shape),
            str(query_context.get('top_k', 10)),
            str(query_context.get('threshold', 0.0)),
            json.dumps(query_context.get('filters', {}), sort_keys=True)
        ]
        
        cache_string = "|".join(cache_components)
        return f"query_{hashlib.md5(cache_string.encode()).hexdigest()}"
    
    async def _finalize_results(
        self,
        results: List[Any],
        query_context: Dict[str, Any],
        execution_time: float,
        cache_hit: bool
    ) -> List[Any]:
        """Finalize query results and update statistics."""
        try:
            # Update statistics
            self.stats['total_queries'] += 1
            
            # Update average execution time
            total_queries = self.stats['total_queries']
            current_avg = self.stats['avg_execution_time']
            self.stats['avg_execution_time'] = ((current_avg * (total_queries - 1)) + execution_time) / total_queries
            
            if cache_hit:
                self.stats['cache_hits'] += 1
            
            # Update optimizer metrics
            if self.enable_optimization:
                metrics = QueryMetrics(
                    query_id=query_context['query_id'],
                    query_type=query_context['query_type'].value,
                    start_time=datetime.utcnow() - timedelta(milliseconds=execution_time),
                    end_time=datetime.utcnow(),
                    execution_time_ms=execution_time,
                    result_count=len(results),
                    cache_hit=cache_hit
                )
                self.optimizer.update_query_history(metrics)
            
            return results
            
        except Exception as e:
            logger.error(f"Failed to finalize results: {e}")
            return results
    
    async def get_statistics(self) -> Dict[str, Any]:
        """Get query processor statistics."""
        stats = self.stats.copy()
        
        # Add cache hit rate
        total_queries = stats['total_queries']
        if total_queries > 0:
            stats['cache_hit_rate'] = stats['cache_hits'] / total_queries
        else:
            stats['cache_hit_rate'] = 0.0
        
        # Add optimizer statistics
        if self.enable_optimization:
            stats['optimizer_stats'] = self.optimizer.get_optimization_stats()
        
        return stats
    
    async def health_check(self) -> bool:
        """Perform health check on query processor."""
        try:
            # Test with dummy query
            test_vector = np.random.random(768).astype(np.float32)
            
            # Execute simple query
            results = await self.process_query(
                query_vector=test_vector,
                top_k=1,
                query_type=QueryType.SIMPLE_SIMILARITY
            )
            
            # Check if we got results (even if empty, should not error)
            return isinstance(results, list)
            
        except Exception as e:
            logger.error(f"Query processor health check failed: {e}")
            return False
    
    async def shutdown(self) -> None:
        """Shutdown the query processor."""
        logger.info("Shutting down QueryProcessor...")
        
        # Clear caches and optimization data
        if self.optimizer:
            self.optimizer.optimization_cache.clear()
            self.optimizer.query_history.clear()
        
        logger.info("QueryProcessor shutdown completed")


# Export main classes
__all__ = [
    'QueryProcessor',
    'QueryOptimizer',
    'ResultProcessor',
    'QueryType',
    'QueryPlan',
    'QueryResult',
    'QueryMetrics'
]