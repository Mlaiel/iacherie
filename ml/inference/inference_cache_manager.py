"""
Inference Cache Manager - Intelligent Inference Caching for Frequently Accessed Content
Author: Fahed Mlaiel (mlaiel@live.de) - ML Engineer
Copyright: © 2025 Fahed Mlaiel. All rights reserved.

Enterprise-grade inference caching with intelligent eviction policies, 
predictive pre-computation, and multi-level cache hierarchy.
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Tuple, Union
from dataclasses import dataclass, asdict
from pathlib import Path
import json
import hashlib
import time
import numpy as np
from datetime import datetime, timedelta
from collections import OrderedDict, defaultdict
import pickle
import gzip

@dataclass
class CacheEntry:
    """Cache entry with metadata."""
    cache_key: str
    content_hash: str
    prediction_result: Any
    confidence_score: float
    model_id: str
    model_version: str
    input_features: Dict[str, Any]
    creation_time: datetime
    last_accessed: datetime
    access_count: int
    ttl_seconds: int
    size_bytes: int
    compression_enabled: bool
    popularity_score: float
    freshness_score: float

@dataclass
class CacheStatistics:
    """Cache performance statistics."""
    cache_level: str
    total_requests: int
    cache_hits: int
    cache_misses: int
    hit_rate: float
    average_response_time_ms: float
    memory_usage_mb: float
    storage_usage_mb: float
    eviction_count: int
    prediction_accuracy: float
    cost_savings: float

@dataclass
class PredictivePrecomputation:
    """Predictive pre-computation configuration."""
    precompute_id: str
    content_patterns: List[str]
    prediction_models: List[str]
    trigger_conditions: Dict[str, Any]
    precompute_schedule: str
    priority_score: float
    estimated_benefit: float

class InferenceCacheManager:
    """
    Advanced inference cache manager with multi-level caching and intelligent policies.
    
    Features:
    - Multi-level cache hierarchy (memory, SSD, distributed)
    - Intelligent eviction policies (LRU, LFU, Time-aware, ML-based)
    - Predictive pre-computation for popular content
    - Content-aware caching with similarity matching
    - Real-time cache optimization and adaptation
    - Creator-specific caching strategies
    - Cost-aware cache management
    - Performance monitoring and analytics
    """
    
    def __init__(self, cache_config -> None: Dict[str, Any] = None) -> None:
        self.logger = logging.getLogger(__name__)
        self.config = cache_config or self._get_default_config()
        
        # Multi-level cache storage
        self.memory_cache = OrderedDict()  # L1 cache
        self.ssd_cache = {}                # L2 cache (simulated)
        self.distributed_cache = {}       # L3 cache (simulated)
        
        # Cache metadata and statistics
        self.cache_stats = {
            "memory": CacheStatistics("memory", 0, 0, 0, 0.0, 0.0, 0.0, 0.0, 0, 0.0, 0.0),
            "ssd": CacheStatistics("ssd", 0, 0, 0, 0.0, 0.0, 0.0, 0.0, 0, 0.0, 0.0),
            "distributed": CacheStatistics("distributed", 0, 0, 0, 0.0, 0.0, 0.0, 0.0, 0, 0.0, 0.0)
        }
        
        # Cache policies and algorithms
        self.eviction_policies = {
            "lru": self._lru_eviction,
            "lfu": self._lfu_eviction,
            "time_aware": self._time_aware_eviction,
            "ml_based": self._ml_based_eviction,
            "hybrid": self._hybrid_eviction
        }
        
        # Content similarity and prediction
        self.content_similarity_index = {}
        self.access_patterns = defaultdict(list)
        self.prediction_models = {}
        
        # Predictive pre-computation
        self.precomputation_queue = []
        self.precomputation_tasks = {}
        
        # Creator-specific cache strategies
        self.creator_cache_strategies = {
            "musician": {
                "cache_duration": 3600,  # 1 hour
                "similarity_threshold": 0.85,
                "popular_content_precompute": True,
                "audio_feature_caching": True,
                "genre_based_grouping": True
            },
            "blogger": {
                "cache_duration": 1800,  # 30 minutes
                "similarity_threshold": 0.80,
                "topic_based_clustering": True,
                "seo_score_caching": True,
                "trending_content_priority": True
            },
            "photographer": {
                "cache_duration": 7200,  # 2 hours
                "similarity_threshold": 0.90,
                "aesthetic_score_caching": True,
                "style_based_grouping": True,
                "high_res_preprocessing": True
            },
            "influencer": {
                "cache_duration": 900,   # 15 minutes
                "similarity_threshold": 0.75,
                "engagement_prediction_priority": True,
                "viral_content_precompute": True,
                "real_time_optimization": True
            }
        }
        
    def _get_default_config(self) -> Dict[str, Any]:
        """Get default cache configuration."""
        return {
            "memory_cache_size_mb": 512,
            "ssd_cache_size_gb": 10,
            "distributed_cache_size_gb": 100,
            "default_ttl_seconds": 3600,
            "eviction_policy": "hybrid",
            "compression_enabled": True,
            "similarity_matching": True,
            "predictive_precomputation": True,
            "performance_monitoring": True,
            "cost_optimization": True,
            "cache_warming": True
        }
    
    async def get_cached_prediction(
        self,
        input_features: Dict[str, Any],
        model_id: str,
        similarity_threshold: float = 0.9
    ) -> Optional[Tuple[Any, float, str]]:
        """Get cached prediction result with similarity matching."""
        try:
            start_time = time.time()
            
            # Generate cache key
            cache_key = self._generate_cache_key(input_features, model_id)
            
            # Check exact match first (L1 memory cache)
            exact_match = await self._check_exact_match(cache_key)
            if exact_match:
                response_time = (time.time() - start_time) * 1000
                await self._update_cache_stats("memory", hit=True, response_time_ms=response_time)
                self.logger.debug(f"Cache hit (exact): {cache_key}")
                return exact_match
            
            # Check similarity matches if enabled
            if self.config.get("similarity_matching", True):
                similar_match = await self._check_similarity_match(
                    input_features, model_id, similarity_threshold
                )
                if similar_match:
                    response_time = (time.time() - start_time) * 1000
                    await self._update_cache_stats("memory", hit=True, response_time_ms=response_time)
                    self.logger.debug(f"Cache hit (similar): {cache_key}")
                    return similar_match
            
            # Check L2 cache (SSD)
            ssd_match = await self._check_ssd_cache(cache_key)
            if ssd_match:
                # Promote to L1 cache
                await self._promote_to_memory_cache(cache_key, ssd_match)
                response_time = (time.time() - start_time) * 1000
                await self._update_cache_stats("ssd", hit=True, response_time_ms=response_time)
                self.logger.debug(f"Cache hit (SSD): {cache_key}")
                return ssd_match
            
            # Check L3 cache (Distributed)
            distributed_match = await self._check_distributed_cache(cache_key)
            if distributed_match:
                # Promote through cache hierarchy
                await self._promote_through_hierarchy(cache_key, distributed_match)
                response_time = (time.time() - start_time) * 1000
                await self._update_cache_stats("distributed", hit=True, response_time_ms=response_time)
                self.logger.debug(f"Cache hit (distributed): {cache_key}")
                return distributed_match
            
            # Cache miss
            response_time = (time.time() - start_time) * 1000
            await self._update_cache_stats("memory", hit=False, response_time_ms=response_time)
            self.logger.debug(f"Cache miss: {cache_key}")
            return None
            
        except Exception as e:
            self.logger.error(f"Error getting cached prediction: {e}")
            return None
    
    async def store_prediction(
        self,
        input_features: Dict[str, Any],
        prediction_result: Any,
        confidence_score: float,
        model_id: str,
        model_version: str,
        creator_domain: str = "general"
    ) -> str:
        """Store prediction result in cache with intelligent placement."""
        try:
            # Generate cache key and content hash
            cache_key = self._generate_cache_key(input_features, model_id)
            content_hash = self._generate_content_hash(prediction_result)
            
            # Get creator-specific cache strategy
            cache_strategy = self.creator_cache_strategies.get(
                creator_domain, self.creator_cache_strategies["musician"]
            )
            
            # Determine TTL based on confidence and domain
            ttl_seconds = await self._calculate_adaptive_ttl(
                confidence_score, creator_domain, cache_strategy
            )
            
            # Calculate popularity and freshness scores
            popularity_score = await self._calculate_popularity_score(cache_key, input_features)
            freshness_score = 1.0  # New entries start with max freshness
            
            # Serialize and compress if enabled
            serialized_result = await self._serialize_prediction(
                prediction_result, self.config.get("compression_enabled", True)
            )
            
            # Create cache entry
            cache_entry = CacheEntry(
                cache_key=cache_key,
                content_hash=content_hash,
                prediction_result=serialized_result,
                confidence_score=confidence_score,
                model_id=model_id,
                model_version=model_version,
                input_features=input_features,
                creation_time=datetime.now(),
                last_accessed=datetime.now(),
                access_count=1,
                ttl_seconds=ttl_seconds,
                size_bytes=len(serialized_result),
                compression_enabled=self.config.get("compression_enabled", True),
                popularity_score=popularity_score,
                freshness_score=freshness_score
            )
            
            # Determine cache level placement
            cache_level = await self._determine_cache_placement(cache_entry, creator_domain)
            
            # Store in appropriate cache level
            if cache_level == "memory":
                await self._store_in_memory_cache(cache_entry)
            elif cache_level == "ssd":
                await self._store_in_ssd_cache(cache_entry)
            else:
                await self._store_in_distributed_cache(cache_entry)
            
            # Update similarity index
            await self._update_similarity_index(cache_key, input_features)
            
            # Update access patterns
            await self._update_access_patterns(cache_key, creator_domain)
            
            # Trigger predictive pre-computation if beneficial
            if self.config.get("predictive_precomputation", True):
                await self._trigger_predictive_precomputation(
                    input_features, model_id, creator_domain
                )
            
            self.logger.debug(f"Prediction cached: {cache_key} in {cache_level}")
            return cache_key
            
        except Exception as e:
            self.logger.error(f"Error storing prediction: {e}")
            raise
    
    async def optimize_cache_performance(self) -> Dict[str, Any]:
        """Optimize cache performance through analysis and adaptation."""
        try:
            optimization_results = {
                "optimization_timestamp": datetime.now().isoformat(),
                "actions_taken": [],
                "performance_improvements": {},
                "cost_savings": 0.0,
                "recommendations": []
            }
            
            # Analyze current cache performance
            performance_analysis = await self._analyze_cache_performance()
            
            # Memory cache optimization
            if performance_analysis["memory"]["hit_rate"] < 0.7:
                memory_optimization = await self._optimize_memory_cache()
                optimization_results["actions_taken"].append("memory_cache_optimization")
                optimization_results["performance_improvements"]["memory"] = memory_optimization
            
            # SSD cache optimization
            if performance_analysis["ssd"]["utilization"] > 0.9:
                ssd_optimization = await self._optimize_ssd_cache()
                optimization_results["actions_taken"].append("ssd_cache_optimization")
                optimization_results["performance_improvements"]["ssd"] = ssd_optimization
            
            # Eviction policy optimization
            if performance_analysis["overall"]["miss_rate"] > 0.4:
                eviction_optimization = await self._optimize_eviction_policy()
                optimization_results["actions_taken"].append("eviction_policy_optimization")
                optimization_results["performance_improvements"]["eviction"] = eviction_optimization
            
            # Predictive pre-computation optimization
            precompute_optimization = await self._optimize_predictive_precomputation()
            if precompute_optimization["improvements"] > 0:
                optimization_results["actions_taken"].append("predictive_precomputation_optimization")
                optimization_results["performance_improvements"]["precomputation"] = precompute_optimization
            
            # Cache warming optimization
            warming_optimization = await self._optimize_cache_warming()
            optimization_results["actions_taken"].append("cache_warming_optimization")
            optimization_results["performance_improvements"]["warming"] = warming_optimization
            
            # Calculate total cost savings
            total_cost_savings = sum([
                opt.get("cost_savings", 0) 
                for opt in optimization_results["performance_improvements"].values()
            ])
            optimization_results["cost_savings"] = total_cost_savings
            
            # Generate recommendations
            recommendations = await self._generate_optimization_recommendations(
                performance_analysis, optimization_results
            )
            optimization_results["recommendations"] = recommendations
            
            self.logger.info(f"Cache optimization completed: ${total_cost_savings:.2f} savings")
            return optimization_results
            
        except Exception as e:
            self.logger.error(f"Error optimizing cache performance: {e}")
            raise
    
    async def predict_cache_needs(
        self,
        time_horizon_hours: int = 24,
        creator_domains: List[str] = None
    ) -> Dict[str, Any]:
        """Predict future cache needs and pre-compute popular content."""
        try:
            if creator_domains is None:
                creator_domains = ["musician", "blogger", "photographer", "influencer"]
            
            predictions = {
                "time_horizon_hours": time_horizon_hours,
                "predicted_access_patterns": {},
                "precomputation_recommendations": [],
                "capacity_recommendations": {},
                "cost_projections": {}
            }
            
            # Analyze historical access patterns
            for domain in creator_domains:
                domain_patterns = await self._analyze_domain_access_patterns(domain)
                predictions["predicted_access_patterns"][domain] = domain_patterns
            
            # Predict popular content for pre-computation
            for domain in creator_domains:
                domain_precompute = await self._predict_popular_content(
                    domain, time_horizon_hours
                )
                predictions["precomputation_recommendations"].extend(domain_precompute)
            
            # Predict capacity needs
            capacity_predictions = await self._predict_capacity_needs(
                predictions["predicted_access_patterns"], time_horizon_hours
            )
            predictions["capacity_recommendations"] = capacity_predictions
            
            # Project costs
            cost_projections = await self._project_cache_costs(
                predictions["capacity_recommendations"], time_horizon_hours
            )
            predictions["cost_projections"] = cost_projections
            
            # Execute predictive pre-computation
            if self.config.get("predictive_precomputation", True):
                precompute_results = await self._execute_predictive_precomputation(
                    predictions["precomputation_recommendations"]
                )
                predictions["precomputation_executed"] = precompute_results
            
            self.logger.info(f"Cache needs prediction completed for {time_horizon_hours}h horizon")
            return predictions
            
        except Exception as e:
            self.logger.error(f"Error predicting cache needs: {e}")
            raise
    
    def _generate_cache_key(self, input_features: Dict[str, Any], model_id: str) -> str:
        """Generate unique cache key for input features and model."""
        # Create deterministic hash of input features
        feature_str = json.dumps(input_features, sort_keys=True)
        feature_hash = hashlib.sha256(feature_str.encode()).hexdigest()[:16]
        
        return f"{model_id}_{feature_hash}"
    
    def _generate_content_hash(self, prediction_result: Any) -> str:
        """Generate content hash for prediction result."""
        try:
            result_str = json.dumps(prediction_result, sort_keys=True, default=str)
            return hashlib.sha256(result_str.encode()).hexdigest()[:16]
        except:
            # Fallback for non-serializable objects
            return hashlib.sha256(str(prediction_result).encode()).hexdigest()[:16]
    
    async def _check_exact_match(self, cache_key: str) -> Optional[Tuple[Any, float, str]]:
        """Check for exact cache match in memory cache."""
        if cache_key in self.memory_cache:
            entry = self.memory_cache[cache_key]
            
            # Check if entry is still valid (not expired)
            if await self._is_cache_entry_valid(entry):
                # Update access information
                entry.last_accessed = datetime.now()
                entry.access_count += 1
                
                # Move to end (LRU)
                self.memory_cache.move_to_end(cache_key)
                
                # Deserialize result
                result = await self._deserialize_prediction(entry.prediction_result)
                
                return (result, entry.confidence_score, cache_key)
        
        return None
    
    async def _check_similarity_match(
        self,
        input_features: Dict[str, Any],
        model_id: str,
        threshold: float
    ) -> Optional[Tuple[Any, float, str]]:
        """Check for similar cache entries."""
        # Simplified similarity matching (in production would use embeddings)
        for cache_key, entry in self.memory_cache.items():
            if entry.model_id != model_id:
                continue
            
            # Calculate similarity score (mock implementation)
            similarity = await self._calculate_feature_similarity(
                input_features, entry.input_features
            )
            
            if similarity >= threshold and await self._is_cache_entry_valid(entry):
                # Update access information
                entry.last_accessed = datetime.now()
                entry.access_count += 1
                
                # Deserialize result
                result = await self._deserialize_prediction(entry.prediction_result)
                
                return (result, entry.confidence_score * similarity, cache_key)
        
        return None
    
    async def _calculate_feature_similarity(
        self,
        features1: Dict[str, Any],
        features2: Dict[str, Any]
    ) -> float:
        """Calculate similarity between feature sets."""
        # Mock similarity calculation
        # In production, would use proper similarity metrics
        
        common_keys = set(features1.keys()) & set(features2.keys())
        if not common_keys:
            return 0.0
        
        similarity_scores = []
        for key in common_keys:
            val1, val2 = features1[key], features2[key]
            
            if isinstance(val1, (int, float)) and isinstance(val2, (int, float)):
                # Numerical similarity
                max_val = max(abs(val1), abs(val2))
                if max_val > 0:
                    similarity = 1.0 - abs(val1 - val2) / max_val
                else:
                    similarity = 1.0
            elif val1 == val2:
                # Exact match
                similarity = 1.0
            else:
                # Different values
                similarity = 0.0
            
            similarity_scores.append(similarity)
        
        return np.mean(similarity_scores) if similarity_scores else 0.0

# Example usage and testing
async def main() -> None:
    """Example usage of InferenceCacheManager."""
    cache_manager = InferenceCacheManager()
    
    # Mock input features and prediction
    input_features = {
        "audio_duration": 180.5,
        "tempo": 120,
        "genre": "pop",
        "artist_id": "artist_123"
    }
    
    model_id = "music-genre-classifier"
    model_version = "v2.1"
    prediction_result = {"genre": "pop", "confidence": 0.92, "sub_genres": ["dance-pop", "electronic"]}
    
    # Store prediction in cache
    cache_key = await cache_manager.store_prediction(
        input_features, prediction_result, 0.92, model_id, model_version, "musician"
    )
    
    print(f"Prediction stored with cache key: {cache_key}")
    
    # Try to retrieve from cache
    cached_result = await cache_manager.get_cached_prediction(
        input_features, model_id, similarity_threshold=0.9
    )
    
    if cached_result:
        result, confidence, key = cached_result
        print(f"Cache hit! Result: {result}, Confidence: {confidence:.3f}")
    else:
        print("Cache miss")
    
    # Test similarity matching with slightly different features
    similar_features = input_features.copy()
    similar_features["tempo"] = 122  # Slightly different tempo
    
    similar_result = await cache_manager.get_cached_prediction(
        similar_features, model_id, similarity_threshold=0.8
    )
    
    if similar_result:
        result, confidence, key = similar_result
        print(f"Similar cache hit! Confidence: {confidence:.3f}")
    
    # Optimize cache performance
    optimization_result = await cache_manager.optimize_cache_performance()
    print(f"Cache optimization completed: {len(optimization_result['actions_taken'])} actions taken")
    
    # Predict cache needs
    predictions = await cache_manager.predict_cache_needs(24, ["musician"])
    print(f"Cache predictions for next 24h: {len(predictions['precomputation_recommendations'])} items to precompute")

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())