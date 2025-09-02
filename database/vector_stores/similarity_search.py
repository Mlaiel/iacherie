"""Similarity Search Engine

This module provides advanced similarity search capabilities across multiple vector stores
with intelligent ranking, filtering, and result optimization.

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
from typing import Dict, List, Optional, Tuple, Any, Union, Callable
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from enum import Enum
import numpy as np
import scipy.spatial.distance as distance
from sklearn.metrics.pairwise import cosine_similarity, euclidean_distances
from sklearn.preprocessing import MinMaxScaler
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_

from backend.core.config import get_settings
from backend.core.database import get_db_session
from backend.models.content_fingerprints import ContentFingerprint
from backend.models.protection_alerts import ProtectionAlert
from backend.utils.exceptions import SearchError, VectorStoreError
from backend.utils.performance import measure_execution_time
from backend.utils.caching import CacheManager
from backend.utils.ml_models import SimilarityClassifier

logger = logging.getLogger(__name__)
settings = get_settings()


class SimilarityMetric(Enum):
    """
Similarity calculation metrics"""

    COSINE = "cosine"
    EUCLIDEAN = "euclidean"
    MANHATTAN = "manhattan"
    JACCARD = "jaccard"
    HAMMING = "hamming"
    PEARSON = "pearson"


class SearchMode(Enum):
    """Search operation modes"""

    EXACT_MATCH = "exact_match"
    FUZZY_SEARCH = "fuzzy_search"
    SEMANTIC_SEARCH = "semantic_search"
    HYBRID_SEARCH = "hybrid_search"
    CONTEXTUAL_SEARCH = "contextual_search"


class RankingAlgorithm(Enum):
    """Result ranking algorithms"""

    SIMILARITY_SCORE = "similarity_score"
    WEIGHTED_FUSION = "weighted_fusion"
    RECIPROCAL_RANK = "reciprocal_rank"
    BAYESIAN_FUSION = "bayesian_fusion"
    LEARNING_TO_RANK = "learning_to_rank"


@dataclass
class SearchQuery:
    """Search query configuration"""
    content_type: str
    query_vector: np.ndarray
    text_query: Optional[str] = None
    metadata_filters: Optional[Dict[str, Any]] = None
    similarity_threshold: float = 0.8
    max_results: int = 10
    search_mode: SearchMode = SearchMode.SEMANTIC_SEARCH
    similarity_metric: SimilarityMetric = SimilarityMetric.COSINE
    ranking_algorithm: RankingAlgorithm = RankingAlgorithm.SIMILARITY_SCORE
    include_explanation: bool = False
    boost_factors: Optional[Dict[str, float]] = None


@dataclass
class SimilarityResult:
    """
Enhanced similarity search result"""
    content_id: str
    fingerprint_id: int
    similarity_score: float
    confidence_score: float
    content_type: str
    metadata: Dict[str, Any]
    explanation: Optional[Dict[str, Any]] = None
    ranking_features: Optional[Dict[str, float]] = None
    match_regions: Optional[List[Tuple[int, int]]] = None
    duplicate_probability: float = 0.0


@dataclass
class SearchExplanation:
    """
Detailed explanation of search results"""
    query_analysis: Dict[str, Any]
    matching_strategy: str
    ranking_factors: Dict[str, float]
    similarity_breakdown: Dict[str, float]
    filter_effects: Dict[str, Any]
    performance_metrics: Dict[str, float]


@dataclass
class SearchSession:
    """
Search session for tracking and optimization"""
    session_id: str
    user_id: int
    query_history: List[SearchQuery]
    result_history: List[List[SimilarityResult]]
    feedback_scores: List[float]
    session_start: datetime
    total_queries: int
    avg_response_time: float


class SimilaritySearchEngine:
    """
    Advanced similarity search engine for content fingerprint matching.
    
    Features:
    - Multi-metric similarity calculations
    - Intelligent result ranking and fusion
    - Contextual search with user behavior learning
    - Real-time search optimization
    - Detailed search explanations
    - Performance monitoring and caching
    """
    
    def __init__(
        self,
        vector_store_manager: Any,
        cache_manager: CacheManager = None,
        enable_ml_ranking: bool = True,
        session_timeout: int = 3600
    ):
        """
        Initialize similarity search engine
        
        Args:
            vector_store_manager: Vector store manager instance
            cache_manager: Cache manager for result caching
            enable_ml_ranking: Enable ML-based ranking
            session_timeout: Search session timeout in seconds
        """
        self.vector_store_manager = vector_store_manager
        self.cache_manager = cache_manager or CacheManager()
        self.enable_ml_ranking = enable_ml_ranking
        self.session_timeout = session_timeout
        
        # ML models for enhanced ranking
        self.similarity_classifier = None
        if enable_ml_ranking:
            self.similarity_classifier = SimilarityClassifier()
        
        # Search sessions
        self.active_sessions: Dict[str, SearchSession] = {}
        
        # Performance metrics
        self.search_stats = {
            "total_searches": 0,
            "cache_hits": 0,
            "cache_misses": 0,
            "avg_response_time": 0.0,
            "accuracy_scores": [],
            "user_satisfaction": 0.0
        }
        
        # Similarity calculators
        self.similarity_calculators = {
            SimilarityMetric.COSINE: self._cosine_similarity,
            SimilarityMetric.EUCLIDEAN: self._euclidean_distance,
            SimilarityMetric.MANHATTAN: self._manhattan_distance,
            SimilarityMetric.JACCARD: self._jaccard_similarity,
            SimilarityMetric.HAMMING: self._hamming_distance,
            SimilarityMetric.PEARSON: self._pearson_correlation
        }
        
        # Content type specific configurations
        self.content_configs = self._initialize_content_configs()
        
        logger.info(
            f"Initialized SimilaritySearchEngine - ML Ranking: {enable_ml_ranking}, "
            f"Cache: {cache_manager is not None}"
        )
    
    @measure_execution_time
    async def search(
        self, query: SearchQuery, session_id: str = None, user_id: int = None
    ) -> Tuple[List[SimilarityResult], Optional[SearchExplanation]]:
        """
        Perform similarity search with advanced ranking
        
        Args:
            query: Search query configuration
            session_id: Optional session ID for tracking
            user_id: Optional user ID for personalization
            
        Returns:
            Tuple of (search results, explanation)
        """
        try:
            start_time = datetime.now()
            self.search_stats["total_searches"] += 1
            
            # Generate cache key
            cache_key = self._generate_cache_key(query)
            
            # Check cache first
            cached_results = await self.cache_manager.get(cache_key)
            if cached_results:
                self.search_stats["cache_hits"] += 1
                logger.info(f"Retrieved cached results for query: {cache_key[:20]}...")
                return cached_results["results"], cached_results.get("explanation")
            
            self.search_stats["cache_misses"] += 1
            
            # Validate and preprocess query
            processed_query = await self._preprocess_query(query)
            
            # Get search session for personalization
            session = self._get_or_create_session(session_id, user_id)
            
            # Perform multi-store search
            raw_results = await self._execute_search(processed_query, session)
            
            # Calculate similarities with multiple metrics
            enhanced_results = await self._calculate_similarities(
                raw_results, processed_query
            )
            
            # Apply ranking algorithm
            ranked_results = await self._apply_ranking(
                enhanced_results, processed_query, session
            )
            
            # Apply post-processing filters
            final_results = await self._post_process_results(
                ranked_results, processed_query
            )
            
            # Generate explanation if requested
            explanation = None
            if query.include_explanation:
                explanation = await self._generate_explanation(
                    query, final_results, raw_results
                )
            
            # Cache results
            cache_data = {
                "results": final_results,
                "explanation": explanation,
                "timestamp": datetime.now().isoformat()
            }
            await self.cache_manager.set(
                cache_key, cache_data, ttl=settings.SEARCH_CACHE_TTL
            )
            
            # Update session
            if session:
                session.query_history.append(query)
                session.result_history.append(final_results)
                session.total_queries += 1
            
            # Update performance metrics
            response_time = (datetime.now() - start_time).total_seconds()
            self._update_performance_metrics(response_time, len(final_results))
            
            logger.info(
                f"Search completed: {len(final_results)} results in {response_time:.3f}s"
            )
            
            return final_results, explanation
            
        except Exception as e:
            logger.error(f"Similarity search failed: {str(e)}")
            raise SearchError(f"Similarity search failed: {str(e)}")
    
    @measure_execution_time
    async def batch_search(
        self, queries: List[SearchQuery], session_id: str = None
    ) -> List[Tuple[List[SimilarityResult], Optional[SearchExplanation]]]:
        """
        Perform batch similarity searches with optimization
        
        Args:
            queries: List of search queries
            session_id: Optional session ID
            
        Returns:
            List of search results for each query
        """
        try:
            # Group queries by content type for optimization
            grouped_queries = {}
            for i, query in enumerate(queries):
                content_type = query.content_type
                if content_type not in grouped_queries:
                    grouped_queries[content_type] = []
                grouped_queries[content_type].append((i, query))
            
            # Execute searches in parallel by content type
            all_results = [None] * len(queries)
            
            for content_type, type_queries in grouped_queries.items():
                # Parallel execution for queries of same content type
                tasks = []
                for idx, query in type_queries:
                    task = asyncio.create_task(self.search(query, session_id))
                    tasks.append((idx, task))
                
                # Wait for completion
                for idx, task in tasks:
                    try:
                        results, explanation = await task
                        all_results[idx] = (results, explanation)
                    except Exception as e:
                        logger.error(f"Batch search failed for query {idx}: {str(e)}")
                        all_results[idx] = ([], None)
            
            logger.info(f"Batch search completed: {len(queries)} queries processed")
            return all_results
            
        except Exception as e:
            logger.error(f"Batch search failed: {str(e)}")
            raise SearchError(f"Batch search failed: {str(e)}")
    
    async def find_duplicates(
        self,
        content_type: str,
        threshold: float = 0.95,
        batch_size: int = 1000
    ) -> List[Tuple[str, str, float]]:
        """
        Find potential duplicate content using similarity analysis
        
        Args:
            content_type: Content type to analyze
            threshold: Similarity threshold for duplicates
            batch_size: Processing batch size
            
        Returns:
            List of (content_id1, content_id2, similarity_score) tuples
        """
        try:
            duplicates = []
            
            # Get all fingerprints for content type
            async with get_db_session() as session:
                stmt = select(ContentFingerprint).where(
                    ContentFingerprint.content_type == content_type
                ).order_by(ContentFingerprint.id)
                
                result = await session.execute(stmt)
                fingerprints = result.scalars().all()
            
            if len(fingerprints) < 2:
                return duplicates
            
            # Process in batches to avoid memory issues
            for i in range(0, len(fingerprints), batch_size):
                batch = fingerprints[i:i + batch_size]
                
                # Compare each fingerprint with others
                for j, fp1 in enumerate(batch):
                    if not fp1.vector_embedding:
                        continue
                    
                    vector1 = np.frombuffer(fp1.vector_embedding, dtype=np.float32)
                    
                    # Compare with remaining fingerprints
                    for k in range(j + 1, len(fingerprints)):
                        fp2 = fingerprints[k]
                        if not fp2.vector_embedding:
                            continue
                        
                        vector2 = np.frombuffer(fp2.vector_embedding, dtype=np.float32)
                        
                        # Calculate similarity
                        similarity = self._cosine_similarity(vector1, vector2)
                        
                        if similarity >= threshold:
                            duplicates.append((fp1.content_id, fp2.content_id, similarity))
                
                logger.info(f"Processed batch {i//batch_size + 1} for duplicate detection")
            
            # Sort by similarity score (highest first)
            duplicates.sort(key=lambda x: x[2], reverse=True)
            
            logger.info(f"Found {len(duplicates)} potential duplicates for {content_type}")
            return duplicates
            
        except Exception as e:
            logger.error(f"Duplicate detection failed: {str(e)}")
            raise SearchError(f"Duplicate detection failed: {str(e)}")
    
    async def update_user_feedback(
        self,
        session_id: str,
        query_index: int,
        relevance_scores: List[float],
        user_rating: float
    ) -> None:
        """
        Update search quality based on user feedback
        
        Args:
            session_id: Search session ID
            query_index: Index of query in session
            relevance_scores: Relevance scores for each result
            user_rating: Overall user rating (0-1)
        """
        try:
            if session_id not in self.active_sessions:
                logger.warning(f"Session {session_id} not found for feedback")
                return
            
            session = self.active_sessions[session_id]
            
            if query_index >= len(session.feedback_scores):
                session.feedback_scores.extend([0.0] * (query_index + 1 - len(session.feedback_scores)))
            
            session.feedback_scores[query_index] = user_rating
            
            # Update ML model if enabled
            if self.enable_ml_ranking and self.similarity_classifier:
                query = session.query_history[query_index]
                results = session.result_history[query_index]
                
                # Prepare training data
                features = []
                labels = []
                
                for i, result in enumerate(results):
                    if i < len(relevance_scores):
                        feature_vector = self._extract_ranking_features(result, query)
                        features.append(feature_vector)
                        labels.append(relevance_scores[i])
                
                if features:
                    await self.similarity_classifier.update_model(features, labels)
            
            # Update global satisfaction metrics
            self.search_stats["user_satisfaction"] = (
                (self.search_stats["user_satisfaction"] * self.search_stats["total_searches"] + user_rating) /
                (self.search_stats["total_searches"] + 1)
            )
            
            logger.info(f"Updated feedback for session {session_id}, query {query_index}")
            
        except Exception as e:
            logger.error(f"Failed to update user feedback: {str(e)}")
    
    async def get_search_analytics(
        self, content_type: str = None, time_range: Tuple[datetime, datetime] = None
    ) -> Dict[str, Any]:
        """
        Get search analytics and performance metrics
        
        Args:
            content_type: Filter by content type
            time_range: Time range for analytics
            
        Returns:
            Analytics data
        """
        try:
            analytics = {
                "global_metrics": self.search_stats.copy(),
                "session_metrics": {},
                "content_type_metrics": {},
                "performance_trends": {},
                "user_behavior": {}
            }
            
            # Session metrics
            active_sessions = len(self.active_sessions)
            total_queries = sum(s.total_queries for s in self.active_sessions.values())
            avg_session_queries = total_queries / max(active_sessions, 1)
            
            analytics["session_metrics"] = {
                "active_sessions": active_sessions,
                "total_queries": total_queries,
                "avg_queries_per_session": avg_session_queries,
                "avg_session_response_time": np.mean([
                    s.avg_response_time for s in self.active_sessions.values()
                ]) if self.active_sessions else 0.0
            }
            
            # Content type specific metrics
            if content_type:
                content_sessions = [
                    s for s in self.active_sessions.values()
                    if any(q.content_type == content_type for q in s.query_history)
                ]
                
                analytics["content_type_metrics"][content_type] = {
                    "sessions": len(content_sessions),
                    "queries": sum(
                        len([q for q in s.query_history if q.content_type == content_type])
                        for s in content_sessions
                    )
                }
            
            # Database analytics
            async with get_db_session() as session:
                # Total fingerprints by type
                if content_type:
                    stmt = select(func.count(ContentFingerprint.id)).where(
                        ContentFingerprint.content_type == content_type
                    )
                else:
                    stmt = select(
                        ContentFingerprint.content_type,
                        func.count(ContentFingerprint.id)
                    ).group_by(ContentFingerprint.content_type)
                
                result = await session.execute(stmt)
                
                if content_type:
                    total_fingerprints = result.scalar()
                    analytics["content_type_metrics"][content_type]["total_fingerprints"] = total_fingerprints
                else:
                    fingerprint_counts = result.all()
                    for ct, count in fingerprint_counts:
                        if ct not in analytics["content_type_metrics"]:
                            analytics["content_type_metrics"][ct] = {}
                        analytics["content_type_metrics"][ct]["total_fingerprints"] = count
            
            return analytics
            
        except Exception as e:
            logger.error(f"Failed to get search analytics: {str(e)}")
            return {}
    
    async def _preprocess_query(self, query: SearchQuery) -> SearchQuery:
        """Preprocess and validate search query"""
        # Validate vector dimension
        if query.query_vector is not None:
            expected_dim = settings.VECTOR_DIMENSION
            if len(query.query_vector) != expected_dim:
                raise SearchError(
                    f"Vector dimension mismatch: expected {expected_dim}, "
                    f"got {len(query.query_vector)}"
                )
            
            # Normalize vector
            query.query_vector = query.query_vector / np.linalg.norm(query.query_vector)
        
        # Apply content-specific configurations
        if query.content_type in self.content_configs:
            config = self.content_configs[query.content_type]
            
            # Override default threshold if not set
            if query.similarity_threshold == 0.8:  # Default value
                query.similarity_threshold = config.get("default_threshold", 0.8)
            
            # Apply boost factors
            if not query.boost_factors:
                query.boost_factors = config.get("boost_factors", {})
        
        return query
    
    async def _execute_search(
        self, query: SearchQuery, session: Optional[SearchSession]
    ) -> List[Any]:
        """Execute search across vector stores"""
        # Choose search strategy based on mode
        if query.search_mode == SearchMode.EXACT_MATCH:
            search_strategy = "single_store"
        elif query.search_mode == SearchMode.SEMANTIC_SEARCH:
            search_strategy = "cascading_search"
        elif query.search_mode == SearchMode.HYBRID_SEARCH:
            search_strategy = "parallel_search"
        else:
            search_strategy = "cascading_search"
        
        # Use session history for personalization
        similarity_threshold = query.similarity_threshold
        if session and session.feedback_scores:
            # Adjust threshold based on user feedback
            avg_feedback = np.mean(session.feedback_scores)
            if avg_feedback < 0.5:  # User unsatisfied, lower threshold
                similarity_threshold *= 0.9
            elif avg_feedback > 0.8:  # User satisfied, raise threshold
                similarity_threshold *= 1.1
        
        # Execute search
        from .vector_store_manager import SearchStrategy
        
        if search_strategy == "single_store":
            strategy = SearchStrategy.SINGLE_STORE
        elif search_strategy == "parallel_search":
            strategy = SearchStrategy.PARALLEL_SEARCH
        elif search_strategy == "cascading_search":
            strategy = SearchStrategy.CASCADING_SEARCH
        else:
            strategy = SearchStrategy.CASCADING_SEARCH
        
        results = await self.vector_store_manager.search_similar(
            content_type=query.content_type,
            query_vector=query.query_vector,
            k=query.max_results * 2,  # Get more candidates for ranking
            similarity_threshold=similarity_threshold,
            search_strategy=strategy,
            metadata_filter=query.metadata_filters,
            text_query=query.text_query
        )
        
        return results
    
    async def _calculate_similarities(
        self, results: List[Any], query: SearchQuery
    ) -> List[SimilarityResult]:
        """Calculate similarities using multiple metrics"""
        enhanced_results = []
        
        for result in results:
            # Get vector for similarity calculation
            vector = await self._get_result_vector(result)
            if vector is None:
                continue
            
            # Calculate similarity with specified metric
            similarity = self.similarity_calculators[query.similarity_metric](
                query.query_vector, vector
            )
            
            # Calculate confidence score
            confidence = self._calculate_confidence(result, query)
            
            # Extract ranking features
            ranking_features = self._extract_ranking_features(result, query)
            
            enhanced_result = SimilarityResult(
                content_id=result.content_id,
                fingerprint_id=result.fingerprint_id,
                similarity_score=similarity,
                confidence_score=confidence,
                content_type=result.content_type,
                metadata=result.metadata,
                ranking_features=ranking_features
            )
            
            enhanced_results.append(enhanced_result)
        
        return enhanced_results
    
    async def _apply_ranking(
        self,
        results: List[SimilarityResult],
        query: SearchQuery,
        session: Optional[SearchSession]
    ) -> List[SimilarityResult]:
        """
Apply ranking algorithm to results"""
        if query.ranking_algorithm == RankingAlgorithm.SIMILARITY_SCORE:
            # Simple similarity-based ranking
            results.sort(key=lambda x: x.similarity_score, reverse=True)
        
        elif query.ranking_algorithm == RankingAlgorithm.WEIGHTED_FUSION:
            # Weighted fusion of multiple scores
            for result in results:
                weighted_score = (
                    result.similarity_score * 0.7 +
                    result.confidence_score * 0.2 +
                    (result.ranking_features.get("recency_score", 0.0) * 0.1)
                )
                result.similarity_score = weighted_score
            
            results.sort(key=lambda x: x.similarity_score, reverse=True)
        
        elif query.ranking_algorithm == RankingAlgorithm.LEARNING_TO_RANK:
            # Use ML model for ranking
            if self.enable_ml_ranking and self.similarity_classifier:
                ranked_results = await self.similarity_classifier.rank_results(
                    results, query
                )
                return ranked_results
            else:
                # Fallback to similarity ranking
                results.sort(key=lambda x: x.similarity_score, reverse=True)
        
        return results
    
    async def _post_process_results(
        self, results: List[SimilarityResult], query: SearchQuery
    ) -> List[SimilarityResult]:
        """Apply post-processing filters and enhancements"""
        # Apply boost factors
        if query.boost_factors:
            for result in results:
                for factor, boost in query.boost_factors.items():
                    if factor in result.metadata:
                        result.similarity_score *= boost
        
        # Re-sort after boosting
        results.sort(key=lambda x: x.similarity_score, reverse=True)
        
        # Limit to requested number of results
        results = results[:query.max_results]
        
        # Calculate duplicate probabilities
        for i, result in enumerate(results):
            # Simple duplicate probability based on similarity threshold
            if result.similarity_score > 0.95:
                result.duplicate_probability = 0.9
            elif result.similarity_score > 0.9:
                result.duplicate_probability = 0.7
            elif result.similarity_score > 0.85:
                result.duplicate_probability = 0.5
            else:
                result.duplicate_probability = 0.2
        
        return results
    
    async def _generate_explanation(
        self,
        query: SearchQuery,
        final_results: List[SimilarityResult],
        raw_results: List[Any]
    ) -> SearchExplanation:
        """
Generate detailed search explanation"""
        return SearchExplanation(
            query_analysis={
                "content_type": query.content_type,
                "vector_dimension": len(query.query_vector) if query.query_vector is not None else 0,
                "has_text_query": query.text_query is not None,
                "has_metadata_filters": query.metadata_filters is not None,
                "similarity_metric": query.similarity_metric.value,
                "search_mode": query.search_mode.value
            },
            matching_strategy=query.ranking_algorithm.value,
            ranking_factors={
                "similarity_weight": 0.7,
                "confidence_weight": 0.2,
                "recency_weight": 0.1
            },
            similarity_breakdown={
                "min_score": min([r.similarity_score for r in final_results]) if final_results else 0.0,
                "max_score": max([r.similarity_score for r in final_results]) if final_results else 0.0,
                "avg_score": np.mean([r.similarity_score for r in final_results]) if final_results else 0.0,
                "std_score": np.std([r.similarity_score for r in final_results]) if final_results else 0.0
            },
            filter_effects={
                "total_candidates": len(raw_results),
                "filtered_results": len(final_results),
                "filter_ratio": len(final_results) / max(len(raw_results), 1)
            },
            performance_metrics={
                "search_time_ms": 0.0,  # Will be filled by caller
                "cache_hit": False,  # Will be filled by caller
                "vector_stores_used": 1  # Will be filled by caller
            }
        )
    
    def _get_or_create_session(
        self, session_id: str, user_id: int
    ) -> Optional[SearchSession]:
        """Get existing session or create new one"""
        if not session_id:
            return None
        
        if session_id in self.active_sessions:
            session = self.active_sessions[session_id]
            # Check if session expired
            if (datetime.now() - session.session_start).seconds > self.session_timeout:
                del self.active_sessions[session_id]
                return None
            return session
        
        # Create new session
        session = SearchSession(
            session_id=session_id,
            user_id=user_id or 0,
            query_history=[],
            result_history=[],
            feedback_scores=[],
            session_start=datetime.now(),
            total_queries=0,
            avg_response_time=0.0
        )
        
        self.active_sessions[session_id] = session
        return session
    
    def _generate_cache_key(self, query: SearchQuery) -> str:
        """
Generate cache key for query"""
        import hashlib
        
        key_data = {
            "content_type": query.content_type,
            "vector_hash": hashlib.md5(query.query_vector.tobytes()).hexdigest() if query.query_vector is not None else None,
            "text_query": query.text_query,
            "filters": sorted(query.metadata_filters.items()) if query.metadata_filters else None,
            "threshold": query.similarity_threshold,
            "max_results": query.max_results,
            "mode": query.search_mode.value,
            "metric": query.similarity_metric.value
        }
        
        key_str = json.dumps(key_data, sort_keys=True, default=str)
        return hashlib.md5(key_str.encode()).hexdigest()
    
    async def _get_result_vector(self, result: Any) -> Optional[np.ndarray]:
        """Get vector embedding for result"""
        try:
            # Get from database
            async with get_db_session() as session:
                stmt = select(ContentFingerprint).where(
                    ContentFingerprint.content_id == result.content_id
                )
                db_result = await session.execute(stmt)
                fingerprint = db_result.scalar_one_or_none()
                
                if fingerprint and fingerprint.vector_embedding:
                    return np.frombuffer(fingerprint.vector_embedding, dtype=np.float32)
                
                return None
                
        except Exception as e:
            logger.error(f"Failed to get vector for {result.content_id}: {str(e)}")
            return None
    
    def _calculate_confidence(self, result: Any, query: SearchQuery) -> float:
        """Calculate confidence score for result"""
        confidence = 0.8  # Base confidence
        
        # Adjust based on metadata completeness
        if hasattr(result, 'metadata') and result.metadata:
            metadata_completeness = len(result.metadata) / 10.0  # Assume 10 ideal fields
            confidence += min(metadata_completeness * 0.1, 0.1)
        
        # Adjust based on store source reliability
        if hasattr(result, 'store_source'):
            if result.store_source == "faiss":
                confidence += 0.05  # FAISS is most reliable for exact matching
            elif result.store_source == "elasticsearch":
                confidence += 0.03  # Good for hybrid search
        
        return min(confidence, 1.0)
    
    def _extract_ranking_features(self, result: Any, query: SearchQuery) -> Dict[str, float]:
        try:
                    # AI model processing
                    if not hasattr(self, 'model') or self.model is None:
                        raise RuntimeError("AI model not initialized")
            
                    # Preprocess input
                    processed_input = await self._preprocess__extract_ranking_features_input(result)
            
                    # Run inference
                    result = await self.model.predict(processed_input)
            
                    # Postprocess result
                    final_result = await self._postprocess__extract_ranking_features_result(result)
            
                    logger.info(f"AI processing _extract_ranking_features completed")
                    return final_result
            
                except Exception as e:
                    logger.error(f"AI processing _extract_ranking_features failed: {e}")
                    raise
    def _initialize_content_configs(self) -> Dict[str, Dict[str, Any]]:
        """Initialize content type specific configurations"""
        return {
            "audio": {
                "default_threshold": 0.85,
                "boost_factors": {
                    "artist": 1.2,
                    "genre": 1.1,
                    "bpm": 1.05
                },
                "preferred_metric": SimilarityMetric.COSINE
            },
            "video": {
                "default_threshold": 0.80,
                "boost_factors": {
                    "title": 1.3,
                    "description": 1.2,
                    "duration": 1.1
                },
                "preferred_metric": SimilarityMetric.EUCLIDEAN
            },
            "image": {
                "default_threshold": 0.82,
                "boost_factors": {
                    "resolution": 1.1,
                    "format": 1.05,
                    "dominant_colors": 1.15
                },
                "preferred_metric": SimilarityMetric.COSINE
            },
            "text": {
                "default_threshold": 0.78,
                "boost_factors": {
                    "title": 1.4,
                    "author": 1.2,
                    "category": 1.1
                },
                "preferred_metric": SimilarityMetric.COSINE
            }
        }
    
    # Similarity calculation methods
    def _cosine_similarity(self, vec1: np.ndarray, vec2: np.ndarray) -> float:
        """Calculate cosine similarity"""
        return float(cosine_similarity(vec1.reshape(1, -1), vec2.reshape(1, -1))[0, 0])
    
    def _euclidean_distance(self, vec1: np.ndarray, vec2: np.ndarray) -> float:
        """
Calculate normalized euclidean distance (converted to similarity)"""
        dist = euclidean_distances(vec1.reshape(1, -1), vec2.reshape(1, -1))[0, 0]
        return 1.0 / (1.0 + dist)  # Convert distance to similarity
    
    def _manhattan_distance(self, vec1: np.ndarray, vec2: np.ndarray) -> float:
        """
Calculate normalized Manhattan distance (converted to similarity)"""
        dist = distance.cityblock(vec1, vec2)
        return 1.0 / (1.0 + dist)
    
    def _jaccard_similarity(self, vec1: np.ndarray, vec2: np.ndarray) -> float:
        """
Calculate Jaccard similarity (for binary vectors)"""
        # Convert to binary
        bin1 = (vec1 > 0.5).astype(int)
        bin2 = (vec2 > 0.5).astype(int)
        
        intersection = np.sum(bin1 & bin2)
        union = np.sum(bin1 | bin2)
        
        return intersection / max(union, 1)
    
    def _hamming_distance(self, vec1: np.ndarray, vec2: np.ndarray) -> float:
        """
Calculate normalized Hamming distance (converted to similarity)"""
        # Convert to binary
        bin1 = (vec1 > 0.5).astype(int)
        bin2 = (vec2 > 0.5).astype(int)
        
        dist = distance.hamming(bin1, bin2)
        return 1.0 - dist  # Convert distance to similarity
    
    def _pearson_correlation(self, vec1: np.ndarray, vec2: np.ndarray) -> float:
        """
Calculate Pearson correlation coefficient"""
        correlation = np.corrcoef(vec1, vec2)[0, 1]
        return (correlation + 1.0) / 2.0  # Normalize to 0-1 range
    
    def _update_performance_metrics(self, response_time: float, result_count: int) -> None:
        """
Update search performance metrics"""
        # Update average response time
        total_searches = self.search_stats["total_searches"]
        current_avg = self.search_stats["avg_response_time"]
        new_avg = ((current_avg * (total_searches - 1)) + response_time) / total_searches
        self.search_stats["avg_response_time"] = new_avg
        
        # Track accuracy (placeholder - would need user feedback)
        if result_count > 0:
            self.search_stats["accuracy_scores"].append(0.8)  # Placeholder
    
    async def close(self) -> None:
        """Close search engine and cleanup resources"""
        try:
            # Clear active sessions
            self.active_sessions.clear()
            
            # Close ML models
            if self.similarity_classifier:
                await self.similarity_classifier.close()
            
            logger.info("Similarity search engine closed successfully")
            
        except Exception as e:
            logger.error(f"Error closing similarity search engine: {str(e)}")
