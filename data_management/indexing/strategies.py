"""IA Influencer Agent - Advanced Indexing Strategies
==================================================

Strategy pattern implementations for content indexing, vector embeddings,
similarity search, and ranking algorithms with enterprise optimization.

Author: Fahed Mlaiel <mlaiel@live.de>
Project: IA Influencer Agent - Content Protection Platform

⚠️  INTELLECTUAL PROPERTY WARNING ⚠️
This code is the exclusive property of Fahed Mlaiel.
Any unauthorized use, copying, distribution, or reproduction
without explicit written permission is strictly prohibited.
Contact: mlaiel@live.de
"""

import asyncio
import logging
import math
from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Union, Any, Tuple
from dataclasses import dataclass
from datetime import datetime, timezone, timedelta
import numpy as np
from enum import Enum

logger = logging.getLogger(__name__)


class IndexingStrategy(Enum):
    """
Indexing strategy types"""

    BATCH = "batch"
    REALTIME = "realtime"
    HYBRID = "hybrid"
    PRIORITY = "priority"


class SimilarityAlgorithm(Enum):
    """Similarity calculation algorithms"""

    COSINE = "cosine"
    EUCLIDEAN = "euclidean"
    MANHATTAN = "manhattan"
    JACCARD = "jaccard"
    HAMMING = "hamming"


class RankingMethod(Enum):
    """Ranking methods for search results"""

    RELEVANCE = "relevance"
    RECENCY = "recency"
    POPULARITY = "popularity"
    CREATOR_SCORE = "creator_score"
    HYBRID_SCORE = "hybrid_score"


@dataclass
class IndexingContext:
    """Context for indexing operations"""
    content_id: str
    content_type: str
    creator_id: str
    file_size: int
    priority: int = 5  # 1-10, 10 being highest
    metadata: Dict[str, Any] = None
    processing_hints: Dict[str, Any] = None


@dataclass
class SimilarityContext:
    """
Context for similarity calculations"""
    query_type: str
    content_types: List[str]
    algorithm: SimilarityAlgorithm
    threshold: float
    weights: Dict[str, float] = None


@dataclass
class RankingContext:
    """
Context for ranking operations"""
    user_preferences: Dict[str, Any] = None
    creator_weights: Dict[str, float] = None
    content_type_weights: Dict[str, float] = None
    temporal_decay: float = 0.1
    boost_factors: Dict[str, float] = None


class BaseStrategy(ABC):
    """
Abstract base class for all strategies"""
    
    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
        self._metrics = {
            "operations_count": 0,
            "total_processing_time": 0.0,
            "success_rate": 0.0,
            "last_operation": None
        }
    
    def update_metrics(self, processing_time: float, success: bool) -> None:
        """Update strategy performance metrics"""
        self._metrics["operations_count"] += 1
        self._metrics["total_processing_time"] += processing_time
        
        # Update success rate
        if self._metrics["operations_count"] == 1:
            self._metrics["success_rate"] = 1.0 if success else 0.0
        else:
            current_successes = self._metrics["success_rate"] * (self._metrics["operations_count"] - 1)
            if success:
                current_successes += 1
            self._metrics["success_rate"] = current_successes / self._metrics["operations_count"]
        
        self._metrics["last_operation"] = datetime.now(timezone.utc)
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get strategy performance metrics"""
        avg_time = 0.0
        if self._metrics["operations_count"] > 0:
            avg_time = self._metrics["total_processing_time"] / self._metrics["operations_count"]
        
        return {
            **self._metrics,
            "average_processing_time": avg_time
        }


class ContentIndexingStrategy(BaseStrategy):
    """Strategy for optimizing content indexing operations"""
    
    def __init__(self):
        super().__init__()
        self.batch_queue = []
        self.priority_queue = []
        self.processing_strategy = IndexingStrategy.HYBRID
    
    async def optimize_index(self, content_id: str, record: Any) -> Dict[str, Any]:
        """
Optimize indexing based on content characteristics"""
        try:
            start_time = datetime.now()
            
            context = IndexingContext(
                content_id=content_id,
                content_type=getattr(record, 'content_type', 'unknown'),
                creator_id=getattr(record, 'creator_id', ''),
                file_size=getattr(record, 'metadata', {}).get('file_size', 0),
                metadata=getattr(record, 'metadata', {})
            )
            
            # Determine processing strategy
            strategy = await self._determine_processing_strategy(context)
            
            # Apply optimization based on strategy
            optimization_result = await self._apply_optimization(context, strategy)
            
            # Update metrics
            processing_time = (datetime.now() - start_time).total_seconds()
            self.update_metrics(processing_time, optimization_result["success"])
            
            return optimization_result
            
        except Exception as e:
            self.logger.error(f"Failed to optimize index for {content_id}: {e}")
            return {"success": False, "error": str(e)}
    
    async def _determine_processing_strategy(self, context: IndexingContext) -> IndexingStrategy:
        """Determine optimal processing strategy based on context"""
        try:
            # Priority-based decision
            if context.priority >= 8:
                return IndexingStrategy.REALTIME
            
            # Size-based decision
            if context.file_size > 100 * 1024 * 1024:  # > 100MB
                return IndexingStrategy.BATCH
            
            # Content type based decision
            if context.content_type in ["video", "audio"]:
                if context.file_size > 50 * 1024 * 1024:  # > 50MB
                    return IndexingStrategy.BATCH
                else:
                    return IndexingStrategy.HYBRID
            
            # Default strategy
            return IndexingStrategy.HYBRID
            
        except Exception as e:
            self.logger.error(f"Failed to determine processing strategy: {e}")
            return IndexingStrategy.HYBRID
    
    async def _apply_optimization(self, context: IndexingContext, 
                                strategy: IndexingStrategy) -> Dict[str, Any]:
        """Apply optimization based on strategy"""
        try:
            optimization_hints = {
                "processing_strategy": strategy.value,
                "recommended_batch_size": 1,
                "parallel_processing": False,
                "cache_embeddings": True,
                "generate_thumbnails": False,
                "extract_metadata": True
            }
            
            if strategy == IndexingStrategy.BATCH:
                optimization_hints.update({
                    "recommended_batch_size": 10,
                    "parallel_processing": True,
                    "defer_non_critical": True
                })
            
            elif strategy == IndexingStrategy.REALTIME:
                optimization_hints.update({
                    "immediate_processing": True,
                    "skip_heavy_operations": False,
                    "priority_boost": True
                })
            
            elif strategy == IndexingStrategy.HYBRID:
                optimization_hints.update({
                    "recommended_batch_size": 5,
                    "parallel_processing": True,
                    "adaptive_quality": True
                })
            
            # Content-specific optimizations
            if context.content_type == "image":
                optimization_hints.update({
                    "generate_thumbnails": True,
                    "extract_exif": True,
                    "ocr_processing": context.file_size < 10 * 1024 * 1024
                })
            
            elif context.content_type == "audio":
                optimization_hints.update({
                    "extract_waveform": True,
                    "generate_spectrogram": context.file_size < 20 * 1024 * 1024,
                    "speech_to_text": True
                })
            
            elif context.content_type == "video":
                optimization_hints.update({
                    "extract_keyframes": True,
                    "generate_thumbnails": True,
                    "extract_audio": True,
                    "scene_detection": context.file_size < 100 * 1024 * 1024
                })
            
            return {
                "success": True,
                "strategy": strategy.value,
                "optimization_hints": optimization_hints,
                "estimated_processing_time": self._estimate_processing_time(context, strategy)
            }
            
        except Exception as e:
            self.logger.error(f"Failed to apply optimization: {e}")
            return {"success": False, "error": str(e)}
    
    def _estimate_processing_time(self, context: IndexingContext, 
                                strategy: IndexingStrategy) -> float:
        """Estimate processing time based on context and strategy"""
        try:
            base_time = 1.0  # Base processing time in seconds
            
            # File size factor
            size_factor = max(1.0, context.file_size / (10 * 1024 * 1024))  # 10MB baseline
            
            # Content type factor
            type_factors = {
                "text": 0.5,
                "image": 1.0,
                "audio": 2.0,
                "video": 3.0
            }
            type_factor = type_factors.get(context.content_type, 1.0)
            
            # Strategy factor
            strategy_factors = {
                IndexingStrategy.REALTIME: 0.8,
                IndexingStrategy.HYBRID: 1.0,
                IndexingStrategy.BATCH: 1.2
            }
            strategy_factor = strategy_factors.get(strategy, 1.0)
            
            estimated_time = base_time * size_factor * type_factor * strategy_factor
            
            return min(estimated_time, 300.0)  # Cap at 5 minutes
            
        except Exception as e:
            self.logger.error(f"Failed to estimate processing time: {e}")
            return 60.0  # Default to 1 minute
    
    async def batch_optimize(self, contents: List[Tuple[str, Any]]) -> Dict[str, Any]:
        """Optimize batch indexing operations"""
        try:
            if not contents:
                return {"success": True, "optimized_batches": []}
            
            # Group by characteristics
            batches = self._group_contents_for_batching(contents)
            
            optimization_result = {
                "success": True,
                "optimized_batches": [],
                "total_estimated_time": 0.0,
                "parallel_batches": []
            }
            
            for batch_key, batch_contents in batches.items():
                batch_info = {
                    "batch_id": batch_key,
                    "content_count": len(batch_contents),
                    "processing_strategy": "batch",
                    "estimated_time": 0.0,
                    "content_ids": [cid for cid, _ in batch_contents]
                }
                
                # Calculate total estimated time for batch
                for content_id, record in batch_contents:
                    context = IndexingContext(
                        content_id=content_id,
                        content_type=getattr(record, 'content_type', 'unknown'),
                        creator_id=getattr(record, 'creator_id', ''),
                        file_size=getattr(record, 'metadata', {}).get('file_size', 0)
                    )
                    
                    batch_info["estimated_time"] += self._estimate_processing_time(
                        context, IndexingStrategy.BATCH
                    )
                
                optimization_result["optimized_batches"].append(batch_info)
                optimization_result["total_estimated_time"] += batch_info["estimated_time"]
            
            # Determine parallel processing opportunities
            optimization_result["parallel_batches"] = self._identify_parallel_batches(
                optimization_result["optimized_batches"]
            )
            
            return optimization_result
            
        except Exception as e:
            self.logger.error(f"Failed to optimize batch: {e}")
            return {"success": False, "error": str(e)}
    
    def _group_contents_for_batching(self, contents: List[Tuple[str, Any]]) -> Dict[str, List]:
        """Group contents for optimal batching"""
        try:
            batches = {}
            
            for content_id, record in contents:
                content_type = getattr(record, 'content_type', 'unknown')
                file_size = getattr(record, 'metadata', {}).get('file_size', 0)
                
                # Create batch key based on content type and size category
                size_category = "small" if file_size < 10 * 1024 * 1024 else "large"
                batch_key = f"{content_type}_{size_category}"
                
                if batch_key not in batches:
                    batches[batch_key] = []
                
                batches[batch_key].append((content_id, record))
            
            return batches
            
        except Exception as e:
            self.logger.error(f"Failed to group contents for batching: {e}")
            return {}
    
    def _identify_parallel_batches(self, batches: List[Dict]) -> List[List[str]]:
        """Identify batches that can be processed in parallel"""
        try:
            parallel_groups = []
            
            # Group by estimated processing time
            light_batches = [b for b in batches if b["estimated_time"] < 30]
            heavy_batches = [b for b in batches if b["estimated_time"] >= 30]
            
            if light_batches:
                parallel_groups.append([b["batch_id"] for b in light_batches])
            
            for heavy_batch in heavy_batches:
                parallel_groups.append([heavy_batch["batch_id"]])
            
            return parallel_groups
            
        except Exception as e:
            self.logger.error(f"Failed to identify parallel batches: {e}")
            return []


class VectorEmbeddingStrategy(BaseStrategy):
    """Strategy for optimizing vector embedding generation and storage"""
    
    def __init__(self):
        super().__init__()
        self.embedding_cache = {}
        self.model_performance = {}
    
    async def optimize_embedding(self, content_type: str, text_data: str, 
                               context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
Optimize embedding generation based on content characteristics"""
        try:
            start_time = datetime.now()
            
            # Determine optimal embedding approach
            embedding_config = await self._determine_embedding_config(
                content_type, text_data, context or {}
            )
            
            # Apply text preprocessing optimizations
            processed_text = await self._optimize_text_preprocessing(text_data, embedding_config)
            
            # Determine if caching is beneficial
            cache_strategy = await self._determine_cache_strategy(processed_text, content_type)
            
            result = {
                "success": True,
                "embedding_config": embedding_config,
                "processed_text": processed_text,
                "cache_strategy": cache_strategy,
                "optimization_applied": True
            }
            
            # Update metrics
            processing_time = (datetime.now() - start_time).total_seconds()
            self.update_metrics(processing_time, True)
            
            return result
            
        except Exception as e:
            self.logger.error(f"Failed to optimize embedding: {e}")
            return {"success": False, "error": str(e)}
    
    async def _determine_embedding_config(self, content_type: str, text_data: str, 
                                        context: Dict[str, Any]) -> Dict[str, Any]:
        """Determine optimal embedding configuration"""
        try:
            config = {
                "model_name": "sentence-transformers/all-MiniLM-L6-v2",
                "max_length": 512,
                "batch_size": 1,
                "normalize_embeddings": True,
                "pooling_strategy": "mean"
            }
            
            text_length = len(text_data)
            
            # Adjust based on text length
            if text_length > 2000:
                config["max_length"] = 1024
                config["model_name"] = "sentence-transformers/all-mpnet-base-v2"
            elif text_length < 100:
                config["max_length"] = 256
            
            # Content type specific optimizations
            if content_type == "audio":
                # For audio transcriptions, use specialized model
                config["model_name"] = "sentence-transformers/distilbert-base-nli-mean-tokens"
                config["pooling_strategy"] = "cls"
            
            elif content_type == "video":
                # For video descriptions, use multimodal-friendly model
                config["model_name"] = "sentence-transformers/clip-ViT-B-32"
            
            elif content_type == "image":
                # For image descriptions/OCR, use vision-language model
                config["model_name"] = "sentence-transformers/clip-ViT-B-32"
                config["normalize_embeddings"] = True
            
            # Performance optimizations
            if context.get("priority", 5) >= 8:
                config["batch_size"] = 1  # Immediate processing
            else:
                config["batch_size"] = min(8, max(1, text_length // 500))
            
            return config
            
        except Exception as e:
            self.logger.error(f"Failed to determine embedding config: {e}")
            return {}
    
    async def _optimize_text_preprocessing(self, text: str, config: Dict[str, Any]) -> str:
        """Optimize text preprocessing for embedding generation"""
        try:
            processed_text = text
            
            # Basic cleaning
            processed_text = processed_text.strip()
            
            # Remove excessive whitespace
            processed_text = " ".join(processed_text.split())
            
            # Truncate to max length if needed
            max_length = config.get("max_length", 512)
            if len(processed_text) > max_length * 4:  # Approximate token count
                processed_text = processed_text[:max_length * 4]
            
            # Content-specific preprocessing
            if config.get("content_type") == "audio":
                # Clean up transcription artifacts
                processed_text = processed_text.replace("[MUSIC]", "")
                processed_text = processed_text.replace("[NOISE]", "")
            
            return processed_text
            
        except Exception as e:
            self.logger.error(f"Failed to optimize text preprocessing: {e}")
            return text
    
    async def _determine_cache_strategy(self, text: str, content_type: str) -> Dict[str, Any]:
        """Determine optimal caching strategy for embeddings"""
        try:
            strategy = {
                "use_cache": True,
                "cache_ttl": 3600,  # 1 hour
                "cache_key_strategy": "hash",
                "invalidation_strategy": "ttl"
            }
            
            text_hash = hash(text)
            
            # Check if similar text was recently processed
            if text_hash in self.embedding_cache:
                strategy["cache_hit"] = True
                strategy["cached_embedding"] = self.embedding_cache[text_hash]
            else:
                strategy["cache_hit"] = False
            
            # Adjust cache TTL based on content type
            if content_type in ["audio", "video"]:
                strategy["cache_ttl"] = 7200  # 2 hours for media content
            elif content_type == "text":
                strategy["cache_ttl"] = 1800  # 30 minutes for text content
            
            return strategy
            
        except Exception as e:
            self.logger.error(f"Failed to determine cache strategy: {e}")
            return {"use_cache": False}
    
    async def batch_embedding_optimization(self, batch_data: List[Tuple[str, str, str]]) -> Dict[str, Any]:
        """Optimize batch embedding generation"""
        try:
            if not batch_data:
                return {"success": True, "optimized_batches": []}
            
            # Group by content type and text length
            grouped_batches = {}
            
            for content_id, content_type, text in batch_data:
                text_length_category = "short" if len(text) < 500 else "long"
                batch_key = f"{content_type}_{text_length_category}"
                
                if batch_key not in grouped_batches:
                    grouped_batches[batch_key] = []
                
                grouped_batches[batch_key].append((content_id, content_type, text))
            
            # Optimize each batch
            optimized_batches = []
            for batch_key, batch_items in grouped_batches.items():
                content_type = batch_key.split("_")[0]
                
                batch_config = await self._determine_embedding_config(
                    content_type, "", {"batch_size": len(batch_items)}
                )
                
                optimized_batch = {
                    "batch_key": batch_key,
                    "item_count": len(batch_items),
                    "config": batch_config,
                    "estimated_time": len(batch_items) * 0.5,  # 0.5s per item
                    "content_ids": [item[0] for item in batch_items]
                }
                
                optimized_batches.append(optimized_batch)
            
            return {
                "success": True,
                "optimized_batches": optimized_batches,
                "total_items": len(batch_data),
                "batch_count": len(optimized_batches)
            }
            
        except Exception as e:
            self.logger.error(f"Failed to optimize batch embeddings: {e}")
            return {"success": False, "error": str(e)}


class SimilaritySearchStrategy(BaseStrategy):
    """Strategy for optimizing similarity search operations"""
    
    def __init__(self):
        super().__init__()
        self.search_cache = {}
        self.algorithm_performance = {}
    
    async def optimize_search(self, query_vector: List[float], 
                            context: SimilarityContext) -> Dict[str, Any]:
        """
Optimize similarity search based on context"""
        try:
            start_time = datetime.now()
            
            # Determine optimal search algorithm
            optimal_algorithm = await self._determine_optimal_algorithm(query_vector, context)
            
            # Optimize search parameters
            search_params = await self._optimize_search_parameters(query_vector, context, optimal_algorithm)
            
            # Determine pre-filtering strategy
            prefilter_strategy = await self._determine_prefilter_strategy(context)
            
            result = {
                "success": True,
                "optimal_algorithm": optimal_algorithm.value,
                "search_params": search_params,
                "prefilter_strategy": prefilter_strategy,
                "cache_strategy": await self._determine_search_cache_strategy(query_vector, context)
            }
            
            # Update metrics
            processing_time = (datetime.now() - start_time).total_seconds()
            self.update_metrics(processing_time, True)
            
            return result
            
        except Exception as e:
            self.logger.error(f"Failed to optimize search: {e}")
            return {"success": False, "error": str(e)}
    
    async def _determine_optimal_algorithm(self, query_vector: List[float], 
                                         context: SimilarityContext) -> SimilarityAlgorithm:
        """Determine optimal similarity algorithm"""
        try:
            # Default to cosine similarity
            algorithm = SimilarityAlgorithm.COSINE
            
            # Consider vector characteristics
            vector_norm = np.linalg.norm(query_vector)
            vector_sparsity = np.count_nonzero(query_vector) / len(query_vector)
            
            # Algorithm selection logic
            if context.query_type == "fingerprint":
                algorithm = SimilarityAlgorithm.HAMMING
            elif context.query_type == "categorical":
                algorithm = SimilarityAlgorithm.JACCARD
            elif vector_sparsity < 0.1:  # Very sparse vector
                algorithm = SimilarityAlgorithm.MANHATTAN
            elif vector_norm > 100:  # High magnitude vector
                algorithm = SimilarityAlgorithm.EUCLIDEAN
            else:
                algorithm = SimilarityAlgorithm.COSINE
            
            # Override with context preference if specified
            if context.algorithm != SimilarityAlgorithm.COSINE:
                algorithm = context.algorithm
            
            return algorithm
            
        except Exception as e:
            self.logger.error(f"Failed to determine optimal algorithm: {e}")
            return SimilarityAlgorithm.COSINE
    
    async def _optimize_search_parameters(self, query_vector: List[float], 
                                        context: SimilarityContext,
                                        algorithm: SimilarityAlgorithm) -> Dict[str, Any]:
        """Optimize search parameters"""
        try:
            params = {
                "threshold": context.threshold,
                "max_results": 100,
                "early_termination": True,
                "approximate_search": False,
                "index_hints": []
            }
            
            # Algorithm-specific optimizations
            if algorithm == SimilarityAlgorithm.COSINE:
                params["normalize_vectors"] = True
                params["use_dot_product"] = True
            
            elif algorithm == SimilarityAlgorithm.EUCLIDEAN:
                params["early_termination_distance"] = context.threshold * 2
                params["approximate_search"] = len(query_vector) > 512
            
            elif algorithm == SimilarityAlgorithm.HAMMING:
                params["bit_parallel"] = len(query_vector) <= 64
                params["max_distance"] = int(len(query_vector) * (1 - context.threshold))
            
            # Content type optimizations
            if "audio" in context.content_types:
                params["max_results"] = 50  # Smaller result set for audio
                params["index_hints"].append("audio_optimized")
            
            if "image" in context.content_types:
                params["approximate_search"] = True  # Use approximate for images
                params["index_hints"].append("visual_features")
            
            return params
            
        except Exception as e:
            self.logger.error(f"Failed to optimize search parameters: {e}")
            return {}
    
    async def _determine_prefilter_strategy(self, context: SimilarityContext) -> Dict[str, Any]:
        """Determine optimal pre-filtering strategy"""
        try:
            strategy = {
                "use_prefilter": False,
                "filter_fields": [],
                "filter_selectivity": 1.0,
                "estimated_reduction": 0.0
            }
            
            # Use pre-filtering if we have specific content types
            if context.content_types and len(context.content_types) < 3:
                strategy["use_prefilter"] = True
                strategy["filter_fields"].append("content_type")
                strategy["estimated_reduction"] = 0.7  # Assume 70% reduction
            
            # Add temporal filtering for recent content preference
            if context.weights and context.weights.get("recency", 0) > 0.5:
                strategy["filter_fields"].append("created_at")
                strategy["estimated_reduction"] += 0.3
            
            return strategy
            
        except Exception as e:
            self.logger.error(f"Failed to determine prefilter strategy: {e}")
            return {"use_prefilter": False}
    
    async def _determine_search_cache_strategy(self, query_vector: List[float], 
                                             context: SimilarityContext) -> Dict[str, Any]:
        """Determine search caching strategy"""
        try:
            strategy = {
                "use_cache": True,
                "cache_ttl": 300,  # 5 minutes
                "cache_key": self._generate_cache_key(query_vector, context),
                "invalidation_triggers": ["content_update", "index_rebuild"]
            }
            
            # Adjust TTL based on query characteristics
            if context.threshold < 0.9:  # High similarity searches cache longer
                strategy["cache_ttl"] = 900  # 15 minutes
            
            if len(context.content_types) == 1:  # Specific content type searches
                strategy["cache_ttl"] = 600  # 10 minutes
            
            return strategy
            
        except Exception as e:
            self.logger.error(f"Failed to determine search cache strategy: {e}")
            return {"use_cache": False}
    
    def _generate_cache_key(self, query_vector: List[float], 
                          context: SimilarityContext) -> str:
        """Generate cache key for search"""
        try:
            # Create a hash of the query vector and context
            vector_hash = hash(tuple(query_vector[:10]))  # Use first 10 elements
            context_hash = hash((
                context.query_type,
                tuple(sorted(context.content_types)),
                context.algorithm.value,
                context.threshold
            ))
            
            return f"search_{vector_hash}_{context_hash}"
            
        except Exception as e:
            self.logger.error(f"Failed to generate cache key: {e}")
            return f"search_{hash(str(query_vector))}"
    
    def calculate_similarity(self, vector1: List[float], vector2: List[float], 
                           algorithm: SimilarityAlgorithm) -> float:
        """Calculate similarity between two vectors using specified algorithm"""
        try:
            v1 = np.array(vector1)
            v2 = np.array(vector2)
            
            if algorithm == SimilarityAlgorithm.COSINE:
                dot_product = np.dot(v1, v2)
                norm1 = np.linalg.norm(v1)
                norm2 = np.linalg.norm(v2)
                
                if norm1 == 0 or norm2 == 0:
                    return 0.0
                
                return dot_product / (norm1 * norm2)
            
            elif algorithm == SimilarityAlgorithm.EUCLIDEAN:
                distance = np.linalg.norm(v1 - v2)
                # Convert distance to similarity (0-1 range)
                max_possible_distance = np.sqrt(len(v1) * 2)  # Assuming normalized vectors
                return 1.0 - (distance / max_possible_distance)
            
            elif algorithm == SimilarityAlgorithm.MANHATTAN:
                distance = np.sum(np.abs(v1 - v2))
                max_possible_distance = len(v1) * 2  # Assuming normalized vectors
                return 1.0 - (distance / max_possible_distance)
            
            elif algorithm == SimilarityAlgorithm.JACCARD:
                # Treat vectors as sets (non-zero elements)
                set1 = set(np.nonzero(v1)[0])
                set2 = set(np.nonzero(v2)[0])
                intersection = len(set1.intersection(set2))
                union = len(set1.union(set2))
                
                if union == 0:
                    return 0.0
                
                return intersection / union
            
            else:
                # Default to cosine similarity
                return self.calculate_similarity(vector1, vector2, SimilarityAlgorithm.COSINE)
            
        except Exception as e:
            self.logger.error(f"Failed to calculate similarity: {e}")
            return 0.0


class RankingStrategy(BaseStrategy):
    """Strategy for ranking search results"""
    
    def __init__(self):
        super().__init__()
        self.ranking_weights = {
            "relevance": 0.4,
            "recency": 0.2,
            "popularity": 0.2,
            "creator_score": 0.1,
            "quality": 0.1
        }
    
    async def rank_results(self, results: List[Dict[str, Any]], 
                         search_request: Any) -> List[Dict[str, Any]]:
        """Rank search results based on multiple factors"""
        try:
            if not results:
                return results
            
            start_time = datetime.now()
            
            # Determine ranking method
            ranking_method = self._determine_ranking_method(search_request)
            
            # Calculate scores for each result
            scored_results = []
            for result in results:
                score = await self._calculate_composite_score(result, ranking_method, search_request)
                result["final_score"] = score
                result["ranking_method"] = ranking_method.value
                scored_results.append(result)
            
            # Sort by score
            ranked_results = sorted(scored_results, key=lambda x: x["final_score"], reverse=True)
            
            # Add ranking positions
            for i, result in enumerate(ranked_results):
                result["rank"] = i + 1
            
            # Update metrics
            processing_time = (datetime.now() - start_time).total_seconds()
            self.update_metrics(processing_time, True)
            
            return ranked_results
            
        except Exception as e:
            self.logger.error(f"Failed to rank results: {e}")
            return results
    
    def _determine_ranking_method(self, search_request: Any) -> RankingMethod:
        """Determine optimal ranking method based on search request"""
        try:
            # Check if sort preference is specified
            sort_by = getattr(search_request, 'sort_by', 'relevance')
            
            if sort_by == "created_at" or sort_by == "recency":
                return RankingMethod.RECENCY
            elif sort_by == "popularity":
                return RankingMethod.POPULARITY
            elif sort_by == "creator_score":
                return RankingMethod.CREATOR_SCORE
            elif sort_by == "relevance":
                return RankingMethod.RELEVANCE
            else:
                return RankingMethod.HYBRID_SCORE
            
        except Exception as e:
            self.logger.error(f"Failed to determine ranking method: {e}")
            return RankingMethod.HYBRID_SCORE
    
    async def _calculate_composite_score(self, result: Dict[str, Any], 
                                       ranking_method: RankingMethod,
                                       search_request: Any) -> float:
        """Calculate composite score for a search result"""
        try:
            if ranking_method == RankingMethod.RELEVANCE:
                return self._calculate_relevance_score(result, search_request)
            
            elif ranking_method == RankingMethod.RECENCY:
                return self._calculate_recency_score(result)
            
            elif ranking_method == RankingMethod.POPULARITY:
                return self._calculate_popularity_score(result)
            
            elif ranking_method == RankingMethod.CREATOR_SCORE:
                return self._calculate_creator_score(result)
            
            else:  # HYBRID_SCORE
                return self._calculate_hybrid_score(result, search_request)
            
        except Exception as e:
            self.logger.error(f"Failed to calculate composite score: {e}")
            return 0.0
    
    def _calculate_relevance_score(self, result: Dict[str, Any], search_request: Any) -> float:
        """Calculate relevance score"""
        try:
            # Base relevance from similarity or search score
            base_relevance = result.get("similarity_score", result.get("score", 0.5))
            
            # Boost for exact matches in title/description
            query_text = getattr(search_request, 'query_text', '')
            if query_text:
                title = result.get("title", "").lower()
                description = result.get("description", "").lower()
                query_lower = query_text.lower()
                
                if query_lower in title:
                    base_relevance += 0.2
                elif any(word in title for word in query_lower.split()):
                    base_relevance += 0.1
                
                if query_lower in description:
                    base_relevance += 0.1
            
            # Content type preference
            preferred_types = getattr(search_request, 'content_types', [])
            if preferred_types and result.get("content_type") in preferred_types:
                base_relevance += 0.1
            
            return min(1.0, base_relevance)
            
        except Exception as e:
            self.logger.error(f"Failed to calculate relevance score: {e}")
            return 0.5
    
    def _calculate_recency_score(self, result: Dict[str, Any]) -> float:
        """Calculate recency score"""
        try:
            created_at = result.get("created_at")
            if not created_at:
                return 0.5
            
            if isinstance(created_at, str):
                try:
                    created_at = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                except:
                    return 0.5
            
            # Calculate age in days
            now = datetime.now(timezone.utc)
            age_days = (now - created_at).days
            
            # Score decreases exponentially with age
            # Recent content (< 7 days) gets highest score
            if age_days <= 7:
                return 1.0
            elif age_days <= 30:
                return 0.8
            elif age_days <= 90:
                return 0.6
            elif age_days <= 365:
                return 0.4
            else:
                return 0.2
            
        except Exception as e:
            self.logger.error(f"Failed to calculate recency score: {e}")
            return 0.5
    
    def _calculate_popularity_score(self, result: Dict[str, Any]) -> float:
        """Calculate popularity score"""
        try:
            # Use metadata to determine popularity
            metadata = result.get("metadata", {})
            
            # Combine various popularity indicators
            view_count = metadata.get("view_count", 0)
            like_count = metadata.get("like_count", 0)
            share_count = metadata.get("share_count", 0)
            download_count = metadata.get("download_count", 0)
            
            # Normalize scores (logarithmic scale for large numbers)
            view_score = min(1.0, math.log10(max(1, view_count)) / 6)  # Max at 1M views
            like_score = min(1.0, math.log10(max(1, like_count)) / 5)   # Max at 100K likes
            share_score = min(1.0, math.log10(max(1, share_count)) / 4) # Max at 10K shares
            download_score = min(1.0, math.log10(max(1, download_count)) / 4)
            
            # Weighted combination
            popularity_score = (
                view_score * 0.4 +
                like_score * 0.3 +
                share_score * 0.2 +
                download_score * 0.1
            )
            
            return popularity_score
            
        except Exception as e:
            self.logger.error(f"Failed to calculate popularity score: {e}")
            return 0.5
    
    def _calculate_creator_score(self, result: Dict[str, Any]) -> float:
        """Calculate creator score"""
        try:
            creator_id = result.get("creator_id", "")
            if not creator_id:
                return 0.5
            
            # This would typically come from a creator reputation system
            # For now, we'll use simple heuristics
            metadata = result.get("metadata", {})
            
            # Creator metrics from metadata
            creator_follower_count = metadata.get("creator_follower_count", 0)
            creator_content_count = metadata.get("creator_content_count", 0)
            creator_verification = metadata.get("creator_verified", False)
            
            # Calculate creator score
            follower_score = min(1.0, math.log10(max(1, creator_follower_count)) / 6)
            content_score = min(1.0, creator_content_count / 100)  # Max at 100 pieces
            verification_bonus = 0.2 if creator_verification else 0.0
            
            creator_score = (follower_score * 0.5 + content_score * 0.3 + verification_bonus)
            
            return min(1.0, creator_score)
            
        except Exception as e:
            self.logger.error(f"Failed to calculate creator score: {e}")
            return 0.5
    
    def _calculate_hybrid_score(self, result: Dict[str, Any], search_request: Any) -> float:
        """Calculate hybrid score combining all factors"""
        try:
            relevance_score = self._calculate_relevance_score(result, search_request)
            recency_score = self._calculate_recency_score(result)
            popularity_score = self._calculate_popularity_score(result)
            creator_score = self._calculate_creator_score(result)
            
            # Quality score based on content characteristics
            quality_score = self._calculate_quality_score(result)
            
            # Combine with weights
            hybrid_score = (
                relevance_score * self.ranking_weights["relevance"] +
                recency_score * self.ranking_weights["recency"] +
                popularity_score * self.ranking_weights["popularity"] +
                creator_score * self.ranking_weights["creator_score"] +
                quality_score * self.ranking_weights["quality"]
            )
            
            return hybrid_score
            
        except Exception as e:
            self.logger.error(f"Failed to calculate hybrid score: {e}")
            return 0.5
    
    def _calculate_quality_score(self, result: Dict[str, Any]) -> float:
        """Calculate content quality score"""
        try:
            metadata = result.get("metadata", {})
            
            # Content completeness
            title_quality = 1.0 if result.get("title", "").strip() else 0.0
            description_quality = min(1.0, len(result.get("description", "")) / 200)
            tags_quality = min(1.0, len(result.get("tags", [])) / 5)
            
            # Technical quality indicators
            file_size = metadata.get("file_size", 0)
            content_type = result.get("content_type", "")
            
            technical_quality = 0.5  # Default
            
            if content_type == "image":
                resolution = metadata.get("width", 0) * metadata.get("height", 0)
                technical_quality = min(1.0, resolution / (1920 * 1080))  # HD baseline
            
            elif content_type == "audio":
                bitrate = metadata.get("bitrate", 0)
                technical_quality = min(1.0, bitrate / 320000)  # 320kbps baseline
            
            elif content_type == "video":
                fps = metadata.get("fps", 0)
                resolution = metadata.get("width", 0) * metadata.get("height", 0)
                technical_quality = min(1.0, (fps / 30) * 0.5 + (resolution / (1920 * 1080)) * 0.5)
            
            # Combine quality factors
            quality_score = (
                title_quality * 0.2 +
                description_quality * 0.2 +
                tags_quality * 0.2 +
                technical_quality * 0.4
            )
            
            return quality_score
            
        except Exception as e:
            self.logger.error(f"Failed to calculate quality score: {e}")
            return 0.5
    
    def update_ranking_weights(self, weights: Dict[str, float]) -> None:
        """Update ranking weights"""
        try:
            # Validate weights sum to 1.0
            total_weight = sum(weights.values())
            if abs(total_weight - 1.0) > 0.01:
                # Normalize weights
                weights = {k: v / total_weight for k, v in weights.items()}
            
            self.ranking_weights.update(weights)
            self.logger.info(f"Updated ranking weights: {self.ranking_weights}")
            
        except Exception as e:
            self.logger.error(f"Failed to update ranking weights: {e}")
