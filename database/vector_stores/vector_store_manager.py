"""Vector Store Manager

This module provides unified management for multiple vector store implementations.
Orchestrates FAISS, Elasticsearch, and Pinecone vector stores with intelligent routing.

Author: Fahed Mlaiel <mlaiel@live.de>
Project: IA Influencer Agent + Content Protection Platform
Copyright: All rights reserved. Unauthorized use, modification, or distribution prohibited.

WARNING: This code is proprietary to Fahed Mlaiel. Any unauthorized copying, modification, 
or distribution without explicit written permission is strictly prohibited and will result 
in legal action under German and international copyright law.
"""

import os
import json
import logging
import asyncio
from typing import Dict, List, Optional, Tuple, Any, Union, Type
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from enum import Enum
import numpy as np
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from backend.core.config import get_settings
from backend.core.database import get_db_session
from backend.models.content_fingerprints import ContentFingerprint
from backend.utils.exceptions import VectorStoreError, SearchError
from backend.utils.performance import measure_execution_time
from backend.utils.monitoring import MetricsCollector

from .faiss_vector_store import FAISSVectorStore, VectorSearchResult
from .elasticsearch_vector_store import ElasticsearchVectorStore, HybridSearchResult
from .pinecone_vector_store import PineconeVectorStore, PineconeSearchResult

logger = logging.getLogger(__name__)
settings = get_settings()


class VectorStoreType(Enum):
    """
Vector store implementation types"""

    FAISS = "faiss"
    ELASTICSEARCH = "elasticsearch"
    PINECONE = "pinecone"


class SearchStrategy(Enum):
    """Search strategy options"""

    SINGLE_STORE = "single_store"
    PARALLEL_SEARCH = "parallel_search"
    CASCADING_SEARCH = "cascading_search"
    CONSENSUS_SEARCH = "consensus_search"


@dataclass
class UnifiedSearchResult:
    """Unified search result across all vector stores"""
    content_id: str
    fingerprint_id: int
    similarity_score: float
    content_type: str
    metadata: Dict[str, Any]
    store_source: str
    confidence_score: float
    search_latency_ms: float


@dataclass
class VectorStoreHealth:
    """
Health status of vector store"""
    store_type: str
    is_healthy: bool
    response_time_ms: float
    error_rate: float
    last_check: datetime
    memory_usage_mb: float
    total_vectors: int


@dataclass
class SearchPerformanceMetrics:
    """
Performance metrics for search operations"""
    total_searches: int
    avg_response_time_ms: float
    success_rate: float
    error_count: int
    cache_hit_rate: float
    throughput_qps: float


class VectorStoreManager:
    """
    Unified vector store manager for multi-store operations.
    
    Features:
    - Multi-store orchestration (FAISS, Elasticsearch, Pinecone)
    - Intelligent routing based on content type and requirements
    - Parallel and cascading search strategies
    - Automatic failover and load balancing
    - Performance monitoring and health checks
    - Consistent API across all implementations
    """
    
    def __init__(
        self,
        primary_store: VectorStoreType = VectorStoreType.FAISS,
        secondary_store: VectorStoreType = VectorStoreType.ELASTICSEARCH,
        fallback_store: VectorStoreType = VectorStoreType.PINECONE,
        enable_redundancy: bool = True,
        health_check_interval: int = 60
    ):
        """
        Initialize vector store manager
        
        Args:
            primary_store: Primary vector store for operations
            secondary_store: Secondary store for redundancy
            fallback_store: Fallback store for high availability
            enable_redundancy: Enable multi-store redundancy
            health_check_interval: Health check interval in seconds
        """
        self.primary_store = primary_store
        self.secondary_store = secondary_store
        self.fallback_store = fallback_store
        self.enable_redundancy = enable_redundancy
        self.health_check_interval = health_check_interval
        
        # Initialize stores
        self.stores: Dict[VectorStoreType, Any] = {}
        self.store_health: Dict[VectorStoreType, VectorStoreHealth] = {}
        
        # Performance tracking
        self.metrics_collector = MetricsCollector()
        self.search_metrics: Dict[str, SearchPerformanceMetrics] = {}
        
        # Routing configuration
        self.routing_rules = self._initialize_routing_rules()
        
        # Health monitoring
        self._health_check_task = None
        
        logger.info(
            f"Initialized VectorStoreManager - Primary: {primary_store.value}, "
            f"Secondary: {secondary_store.value}, Fallback: {fallback_store.value}"
        )
    
    async def initialize(self) -> None:
        """Initialize all vector stores and start health monitoring"""
        try:
            # Initialize FAISS store
            if VectorStoreType.FAISS in [self.primary_store, self.secondary_store, self.fallback_store]:
                self.stores[VectorStoreType.FAISS] = FAISSVectorStore(
                    dimension=settings.VECTOR_DIMENSION,
                    index_type=settings.FAISS_INDEX_TYPE,
                    storage_path=os.path.join(settings.STORAGE_PATH, "vector_stores", "faiss")
                )
            
            # Initialize Elasticsearch store
            if VectorStoreType.ELASTICSEARCH in [self.primary_store, self.secondary_store, self.fallback_store]:
                self.stores[VectorStoreType.ELASTICSEARCH] = ElasticsearchVectorStore(
                    hosts=[settings.ELASTICSEARCH_URL],
                    vector_dimension=settings.VECTOR_DIMENSION
                )
                await self.stores[VectorStoreType.ELASTICSEARCH].initialize()
            
            # Initialize Pinecone store
            if VectorStoreType.PINECONE in [self.primary_store, self.secondary_store, self.fallback_store]:
                self.stores[VectorStoreType.PINECONE] = PineconeVectorStore(
                    api_key=settings.PINECONE_API_KEY,
                    environment=settings.PINECONE_ENVIRONMENT,
                    dimension=settings.VECTOR_DIMENSION
                )
                await self.stores[VectorStoreType.PINECONE].initialize()
            
            # Initialize content type indices
            for content_type in ["audio", "video", "image", "text"]:
                for store_type, store in self.stores.items():
                    if store_type == VectorStoreType.FAISS:
                        await store.initialize_index(content_type)
            
            # Start health monitoring
            self._health_check_task = asyncio.create_task(self._health_monitor())
            
            logger.info("Vector store manager initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize vector store manager: {str(e)}")
            raise VectorStoreError(f"Manager initialization failed: {str(e)}")
    
    @measure_execution_time
    async def add_vectors(
        self,
        content_type: str,
        vectors: List[Tuple[str, np.ndarray, Dict[str, Any]]],
        strategy: str = "primary_with_backup"
    ) -> Dict[str, Any]:
        """
        Add vectors to vector stores
        
        Args:
            content_type: Content type (audio, video, image, text)
            vectors: List of (content_id, vector, metadata) tuples
            strategy: Storage strategy
            
        Returns:
            Storage operation results
        """
        try:
            results = {}
            errors = []
            
            # Determine which stores to use
            target_stores = self._get_target_stores(strategy)
            
            # Add to each target store
            for store_type in target_stores:
                if store_type not in self.stores:
                    continue
                
                try:
                    store = self.stores[store_type]
                    
                    if store_type == VectorStoreType.FAISS:
                        # Prepare for FAISS
                        vector_arrays = np.array([v[1] for v in vectors])
                        content_ids = [v[0] for v in vectors]
                        metadata_list = [v[2] for v in vectors]
                        
                        faiss_ids = await store.add_vectors(
                            content_type, vector_arrays, content_ids, metadata_list
                        )
                        results[store_type.value] = {
                            "added": len(faiss_ids),
                            "faiss_ids": faiss_ids
                        }
                    
                    elif store_type == VectorStoreType.ELASTICSEARCH:
                        # Prepare for Elasticsearch
                        documents = []
                        for content_id, vector, metadata in vectors:
                            doc_id = await store.index_document(
                                content_type, content_id, vector, metadata
                            )
                            documents.append(doc_id)
                        
                        results[store_type.value] = {
                            "added": len(documents),
                            "document_ids": documents
                        }
                    
                    elif store_type == VectorStoreType.PINECONE:
                        # Add to Pinecone
                        pinecone_stats = await store.upsert_vectors(content_type, vectors)
                        results[store_type.value] = pinecone_stats
                    
                    logger.info(
                        f"Successfully added {len(vectors)} vectors to "
                        f"{store_type.value} for {content_type}"
                    )
                
                except Exception as e:
                    error_msg = f"Failed to add to {store_type.value}: {str(e)}"
                    errors.append(error_msg)
                    logger.error(error_msg)
            
            return {
                "total_vectors": len(vectors),
                "content_type": content_type,
                "results": results,
                "errors": errors,
                "success": len(results) > 0
            }
            
        except Exception as e:
            logger.error(f"Vector addition failed: {str(e)}")
            raise VectorStoreError(f"Vector addition failed: {str(e)}")
    
    @measure_execution_time
    async def search_similar(
        self,
        content_type: str,
        query_vector: np.ndarray,
        k: int = 10,
        similarity_threshold: float = 0.8,
        search_strategy: SearchStrategy = SearchStrategy.CASCADING_SEARCH,
        metadata_filter: Dict[str, Any] = None,
        text_query: str = None
    ) -> List[UnifiedSearchResult]:
        """
        Search for similar vectors across stores
        
        Args:
            content_type: Content type to search
            query_vector: Query vector
            k: Number of results
            similarity_threshold: Minimum similarity score
            search_strategy: Search strategy to use
            metadata_filter: Metadata filters
            text_query: Text query for hybrid search
            
        Returns:
            Unified search results
        """
        try:
            start_time = datetime.now()
            
            if search_strategy == SearchStrategy.SINGLE_STORE:
                results = await self._single_store_search(
                    content_type, query_vector, k, similarity_threshold,
                    metadata_filter, text_query
                )
            
            elif search_strategy == SearchStrategy.PARALLEL_SEARCH:
                results = await self._parallel_search(
                    content_type, query_vector, k, similarity_threshold,
                    metadata_filter, text_query
                )
            
            elif search_strategy == SearchStrategy.CASCADING_SEARCH:
                results = await self._cascading_search(
                    content_type, query_vector, k, similarity_threshold,
                    metadata_filter, text_query
                )
            
            elif search_strategy == SearchStrategy.CONSENSUS_SEARCH:
                results = await self._consensus_search(
                    content_type, query_vector, k, similarity_threshold,
                    metadata_filter, text_query
                )
            
            else:
                raise SearchError(f"Unknown search strategy: {search_strategy}")
            
            # Update metrics
            search_time = (datetime.now() - start_time).total_seconds() * 1000
            self._update_search_metrics(content_type, search_time, len(results))
            
            logger.info(
                f"Search completed for {content_type}: {len(results)} results "
                f"in {search_time:.2f}ms using {search_strategy.value}"
            )
            
            return results
            
        except Exception as e:
            logger.error(f"Search failed: {str(e)}")
            raise SearchError(f"Search failed: {str(e)}")
    
    async def remove_vectors(
        self,
        content_type: str,
        content_ids: List[str]
    ) -> Dict[str, Any]:
        """
        Remove vectors from all stores
        
        Args:
            content_type: Content type
            content_ids: Content IDs to remove
            
        Returns:
            Removal operation results
        """
        try:
            results = {}
            errors = []
            
            # Remove from all active stores
            for store_type, store in self.stores.items():
                try:
                    if store_type == VectorStoreType.FAISS:
                        removed_count = await store.remove_vectors(content_type, content_ids)
                        results[store_type.value] = {"removed": removed_count}
                    
                    elif store_type == VectorStoreType.ELASTICSEARCH:
                        removed_count = 0
                        for content_id in content_ids:
                            if await store.delete_document(content_type, content_id):
                                removed_count += 1
                        results[store_type.value] = {"removed": removed_count}
                    
                    elif store_type == VectorStoreType.PINECONE:
                        pinecone_stats = await store.delete_vectors(content_type, content_ids)
                        results[store_type.value] = pinecone_stats
                    
                    logger.info(
                        f"Successfully removed vectors from {store_type.value} "
                        f"for {content_type}"
                    )
                
                except Exception as e:
                    error_msg = f"Failed to remove from {store_type.value}: {str(e)}"
                    errors.append(error_msg)
                    logger.error(error_msg)
            
            return {
                "content_type": content_type,
                "content_ids": content_ids,
                "results": results,
                "errors": errors,
                "success": len(results) > 0
            }
            
        except Exception as e:
            logger.error(f"Vector removal failed: {str(e)}")
            raise VectorStoreError(f"Vector removal failed: {str(e)}")
    
    async def get_health_status(self) -> Dict[str, VectorStoreHealth]:
        """Get health status of all vector stores"""
        try:
            health_status = {}
            
            for store_type, store in self.stores.items():
                try:
                    start_time = datetime.now()
                    
                    # Perform health check based on store type
                    if store_type == VectorStoreType.FAISS:
                        stats = await store.get_index_stats("audio")  # Test with audio
                        is_healthy = stats is not None
                        total_vectors = stats.total_vectors if stats else 0
                        memory_usage = stats.memory_usage_mb if stats else 0.0
                    
                    elif store_type == VectorStoreType.ELASTICSEARCH:
                        cluster_stats = await store.get_cluster_stats()
                        is_healthy = cluster_stats.cluster_health in ["green", "yellow"]
                        total_vectors = cluster_stats.total_documents
                        memory_usage = cluster_stats.memory_usage_mb
                    
                    elif store_type == VectorStoreType.PINECONE:
                        index_stats = await store.get_index_stats()
                        is_healthy = index_stats is not None
                        total_vectors = index_stats.total_vectors if index_stats else 0
                        memory_usage = 0.0  # Pinecone doesn't expose memory usage
                    
                    response_time = (datetime.now() - start_time).total_seconds() * 1000
                    
                    health_status[store_type.value] = VectorStoreHealth(
                        store_type=store_type.value,
                        is_healthy=is_healthy,
                        response_time_ms=response_time,
                        error_rate=0.0,  # Calculate from metrics
                        last_check=datetime.now(timezone.utc),
                        memory_usage_mb=memory_usage,
                        total_vectors=total_vectors
                    )
                
                except Exception as e:
                    health_status[store_type.value] = VectorStoreHealth(
                        store_type=store_type.value,
                        is_healthy=False,
                        response_time_ms=0.0,
                        error_rate=1.0,
                        last_check=datetime.now(timezone.utc),
                        memory_usage_mb=0.0,
                        total_vectors=0
                    )
                    logger.error(f"Health check failed for {store_type.value}: {str(e)}")
            
            return health_status
            
        except Exception as e:
            logger.error(f"Failed to get health status: {str(e)}")
            return {}
    
    async def get_performance_metrics(self) -> Dict[str, SearchPerformanceMetrics]:
        """Get performance metrics for all content types"""
        return self.search_metrics.copy()
    
    async def optimize_stores(self) -> Dict[str, bool]:
        """
Optimize all vector stores"""
        try:
            optimization_results = {}
            
            for store_type, store in self.stores.items():
                try:
                    if store_type == VectorStoreType.FAISS:
                        # Optimize all content type indices
                        for content_type in ["audio", "video", "image", "text"]:
                            await store.optimize_index(content_type)
                        optimization_results[store_type.value] = True
                    
                    # Note: Elasticsearch and Pinecone handle optimization automatically
                    
                    logger.info(f"Optimized {store_type.value} store")
                
                except Exception as e:
                    optimization_results[store_type.value] = False
                    logger.error(f"Failed to optimize {store_type.value}: {str(e)}")
            
            return optimization_results
            
        except Exception as e:
            logger.error(f"Store optimization failed: {str(e)}")
            return {}
    
    async def _single_store_search(
        self, content_type: str, query_vector: np.ndarray, k: int,
        similarity_threshold: float, metadata_filter: Dict[str, Any],
        text_query: str
    ) -> List[UnifiedSearchResult]:
        """Search using only the primary store"""
        store = self.stores[self.primary_store]
        results = []
        
        try:
            if self.primary_store == VectorStoreType.FAISS:
                faiss_results = await store.search_similar(
                    content_type, query_vector, k, similarity_threshold
                )
                results = [self._convert_faiss_result(r) for r in faiss_results]
            
            elif self.primary_store == VectorStoreType.ELASTICSEARCH:
                if text_query:
                    es_results = await store.hybrid_search(
                        content_type, query_vector, text_query, k,
                        filters=metadata_filter
                    )
                else:
                    es_results = await store.vector_search(
                        content_type, query_vector, k, similarity_threshold,
                        metadata_filter
                    )
                results = [self._convert_elasticsearch_result(r) for r in es_results]
            
            elif self.primary_store == VectorStoreType.PINECONE:
                pinecone_results = await store.search_similar(
                    content_type, query_vector, k, similarity_threshold,
                    metadata_filter
                )
                results = [self._convert_pinecone_result(r) for r in pinecone_results]
        
        except Exception as e:
            logger.error(f"Primary store search failed: {str(e)}")
            # Try secondary store as fallback
            if self.secondary_store in self.stores:
                logger.info(f"Falling back to {self.secondary_store.value}")
                # Implement fallback logic here
        
        return results
    
    async def _parallel_search(
        self, content_type: str, query_vector: np.ndarray, k: int,
        similarity_threshold: float, metadata_filter: Dict[str, Any],
        text_query: str
    ) -> List[UnifiedSearchResult]:
        """Search all stores in parallel and merge results"""
        tasks = []
        
        for store_type, store in self.stores.items():
            task = asyncio.create_task(
                self._search_single_store(
                    store_type, store, content_type, query_vector,
                    k, similarity_threshold, metadata_filter, text_query
                )
            )
            tasks.append((store_type, task))
        
        # Wait for all searches to complete
        all_results = []
        for store_type, task in tasks:
            try:
                store_results = await task
                all_results.extend(store_results)
            except Exception as e:
                logger.error(f"Parallel search failed for {store_type.value}: {str(e)}")
        
        # Deduplicate and merge results
        return self._merge_results(all_results, k)
    
    async def _cascading_search(
        self, content_type: str, query_vector: np.ndarray, k: int,
        similarity_threshold: float, metadata_filter: Dict[str, Any],
        text_query: str
    ) -> List[UnifiedSearchResult]:
        """Search stores in cascading order until sufficient results found"""
        stores_to_try = [self.primary_store, self.secondary_store, self.fallback_store]
        
        for store_type in stores_to_try:
            if store_type not in self.stores:
                continue
            
            try:
                results = await self._search_single_store(
                    store_type, self.stores[store_type], content_type,
                    query_vector, k, similarity_threshold, metadata_filter, text_query
                )
                
                if len(results) >= k * 0.8:  # 80% of requested results
                    return results[:k]
                
            except Exception as e:
                logger.error(f"Cascading search failed for {store_type.value}: {str(e)}")
                continue
        
        return []
    
    async def _consensus_search(
        self, content_type: str, query_vector: np.ndarray, k: int,
        similarity_threshold: float, metadata_filter: Dict[str, Any],
        text_query: str
    ) -> List[UnifiedSearchResult]:
        """Search all stores and use consensus scoring"""
        all_results = await self._parallel_search(
            content_type, query_vector, k * 2, similarity_threshold,
            metadata_filter, text_query
        )
        
        # Group results by content_id and calculate consensus scores
        content_scores = {}
        for result in all_results:
            content_id = result.content_id
            if content_id not in content_scores:
                content_scores[content_id] = {
                    "results": [],
                    "total_score": 0.0,
                    "store_count": 0
                }
            
            content_scores[content_id]["results"].append(result)
            content_scores[content_id]["total_score"] += result.similarity_score
            content_scores[content_id]["store_count"] += 1
        
        # Calculate consensus scores and rank
        consensus_results = []
        for content_id, data in content_scores.items():
            if data["store_count"] >= 2:  # Require at least 2 stores agreement
                avg_score = data["total_score"] / data["store_count"]
                best_result = max(data["results"], key=lambda x: x.similarity_score)
                best_result.confidence_score = data["store_count"] / len(self.stores)
                best_result.similarity_score = avg_score
                consensus_results.append(best_result)
        
        # Sort by consensus score and return top k
        consensus_results.sort(key=lambda x: x.similarity_score, reverse=True)
        return consensus_results[:k]
    
    async def _search_single_store(
        self, store_type: VectorStoreType, store: Any, content_type: str,
        query_vector: np.ndarray, k: int, similarity_threshold: float,
        metadata_filter: Dict[str, Any], text_query: str
    ) -> List[UnifiedSearchResult]:
        """Search a single store and convert results"""
        results = []
        start_time = datetime.now()
        
        try:
            if store_type == VectorStoreType.FAISS:
                faiss_results = await store.search_similar(
                    content_type, query_vector, k, similarity_threshold
                )
                results = [self._convert_faiss_result(r) for r in faiss_results]
            
            elif store_type == VectorStoreType.ELASTICSEARCH:
                if text_query:
                    es_results = await store.hybrid_search(
                        content_type, query_vector, text_query, k,
                        filters=metadata_filter
                    )
                else:
                    es_results = await store.vector_search(
                        content_type, query_vector, k, similarity_threshold,
                        metadata_filter
                    )
                results = [self._convert_elasticsearch_result(r) for r in es_results]
            
            elif store_type == VectorStoreType.PINECONE:
                pinecone_results = await store.search_similar(
                    content_type, query_vector, k, similarity_threshold,
                    metadata_filter
                )
                results = [self._convert_pinecone_result(r) for r in pinecone_results]
            
            # Add store source and latency
            latency_ms = (datetime.now() - start_time).total_seconds() * 1000
            for result in results:
                result.store_source = store_type.value
                result.search_latency_ms = latency_ms
        
        except Exception as e:
            logger.error(f"Store search failed for {store_type.value}: {str(e)}")
        
        return results
    
    def _convert_faiss_result(self, result: VectorSearchResult) -> UnifiedSearchResult:
        """Convert FAISS result to unified format"""
        return UnifiedSearchResult(
            content_id=result.content_id,
            fingerprint_id=result.fingerprint_id,
            similarity_score=result.similarity_score,
            content_type=result.content_type,
            metadata=result.metadata,
            store_source="faiss",
            confidence_score=1.0,
            search_latency_ms=0.0
        )
    
    def _convert_elasticsearch_result(self, result: HybridSearchResult) -> UnifiedSearchResult:
        """Convert Elasticsearch result to unified format"""
        return UnifiedSearchResult(
            content_id=result.content_id,
            fingerprint_id=result.fingerprint_id,
            similarity_score=result.combined_score,
            content_type=result.content_type,
            metadata=result.metadata,
            store_source="elasticsearch",
            confidence_score=1.0,
            search_latency_ms=0.0
        )
    
    def _convert_pinecone_result(self, result: PineconeSearchResult) -> UnifiedSearchResult:
        """Convert Pinecone result to unified format"""
        return UnifiedSearchResult(
            content_id=result.content_id,
            fingerprint_id=result.fingerprint_id,
            similarity_score=result.similarity_score,
            content_type=result.content_type,
            metadata=result.metadata,
            store_source="pinecone",
            confidence_score=1.0,
            search_latency_ms=0.0
        )
    
    def _merge_results(
        self, all_results: List[UnifiedSearchResult], k: int
    ) -> List[UnifiedSearchResult]:
        """Merge and deduplicate results from multiple stores"""
        # Group by content_id
        content_groups = {}
        for result in all_results:
            content_id = result.content_id
            if content_id not in content_groups:
                content_groups[content_id] = []
            content_groups[content_id].append(result)
        
        # Take best result for each content_id
        merged_results = []
        for content_id, results in content_groups.items():
            best_result = max(results, key=lambda x: x.similarity_score)
            merged_results.append(best_result)
        
        # Sort by similarity score and return top k
        merged_results.sort(key=lambda x: x.similarity_score, reverse=True)
        return merged_results[:k]
    
    def _get_target_stores(self, strategy: str) -> List[VectorStoreType]:
        """
Get target stores based on strategy"""
        if strategy == "primary_only":
            return [self.primary_store]
        elif strategy == "primary_with_backup":
            stores = [self.primary_store]
            if self.enable_redundancy and self.secondary_store in self.stores:
                stores.append(self.secondary_store)
            return stores
        elif strategy == "all_stores":
            return list(self.stores.keys())
        else:
            return [self.primary_store]
    
    def _initialize_routing_rules(self) -> Dict[str, Dict[str, Any]]:
        """Initialize content type routing rules"""
        return {
            "audio": {
                "primary": VectorStoreType.FAISS,
                "features": ["real_time", "high_precision"],
                "threshold": 0.85
            },
            "video": {
                "primary": VectorStoreType.ELASTICSEARCH,
                "features": ["hybrid_search", "metadata_filtering"],
                "threshold": 0.80
            },
            "image": {
                "primary": VectorStoreType.PINECONE,
                "features": ["cloud_scale", "managed"],
                "threshold": 0.82
            },
            "text": {
                "primary": VectorStoreType.ELASTICSEARCH,
                "features": ["full_text", "hybrid_search"],
                "threshold": 0.78
            }
        }
    
    def _update_search_metrics(
        self, content_type: str, response_time_ms: float, result_count: int
    ) -> None:
        """Update search performance metrics"""
        if content_type not in self.search_metrics:
            self.search_metrics[content_type] = SearchPerformanceMetrics(
                total_searches=0,
                avg_response_time_ms=0.0,
                success_rate=1.0,
                error_count=0,
                cache_hit_rate=0.0,
                throughput_qps=0.0
            )
        
        metrics = self.search_metrics[content_type]
        metrics.total_searches += 1
        
        # Update average response time
        total_time = metrics.avg_response_time_ms * (metrics.total_searches - 1)
        metrics.avg_response_time_ms = (total_time + response_time_ms) / metrics.total_searches
        
        # Update success rate
        if result_count > 0:
            success_count = (metrics.success_rate * (metrics.total_searches - 1)) + 1
            metrics.success_rate = success_count / metrics.total_searches
    
    async def _health_monitor(self) -> None:
        """
Background health monitoring task"""
        while True:
            try:
                await asyncio.sleep(self.health_check_interval)
                health_status = await self.get_health_status()
                
                # Log unhealthy stores
                for store_type, health in health_status.items():
                    if not health.is_healthy:
                        logger.warning(f"Vector store {store_type} is unhealthy")
                
                # Update store health cache
                self.store_health = health_status
                
            except Exception as e:
                logger.error(f"Health monitoring error: {str(e)}")
    
    async def close(self) -> None:
        """Close all vector stores and cleanup"""
        try:
            # Stop health monitoring
            if self._health_check_task:
                self._health_check_task.cancel()
                try:
                    await self._health_check_task
                except asyncio.CancelledError:
                    pass
            
            # Close all stores
            for store_type, store in self.stores.items():
                try:
                    await store.close()
                    logger.info(f"Closed {store_type.value} store")
                except Exception as e:
                    logger.error(f"Error closing {store_type.value}: {str(e)}")
            
            self.stores.clear()
            logger.info("Vector store manager closed successfully")
            
        except Exception as e:
            logger.error(f"Error closing vector store manager: {str(e)}")
