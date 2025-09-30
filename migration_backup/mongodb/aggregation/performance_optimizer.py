"""Performance Optimizer for Aggregation Pipelines
=================================================

Query optimization, caching, and performance monitoring for aggregation pipelines.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel - All Rights Reserved
"""

import logging
import hashlib
import time
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class PerformanceOptimizer:
    """Aggregation pipeline performance optimizer."""
    
    def __init__(self):
        """Initialize performance optimizer."""
        self._query_cache: Dict[str, Any] = {}
        self._performance_stats: Dict[str, List[float]] = {}
        self._cache_ttl = 300  # 5 minutes
        self._slow_query_threshold_ms = 1000  # 1 second
    
    def optimize_pipeline(self, pipeline: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Optimize aggregation pipeline for better performance."""
        optimized = pipeline.copy()
        
        # Apply optimization rules
        optimized = self._move_match_early(optimized)
        optimized = self._combine_consecutive_matches(optimized)
        optimized = self._add_index_hints(optimized)
        optimized = self._optimize_projections(optimized)
        
        return optimized
    
    def _move_match_early(self, pipeline: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Move $match stages as early as possible."""
        matches = [stage for stage in pipeline if "$match" in stage]
        non_matches = [stage for stage in pipeline if "$match" not in stage]
        
        return matches + non_matches
    
    def _combine_consecutive_matches(self, pipeline: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Combine consecutive $match stages."""
        result = []
        current_match = None
        
        for stage in pipeline:
            if "$match" in stage:
                if current_match is None:
                    current_match = stage
                else:
                    # Combine with previous match
                    current_match["$match"].update(stage["$match"])
            else:
                if current_match:
                    result.append(current_match)
                    current_match = None
                result.append(stage)
        
        if current_match:
            result.append(current_match)
        
        return result
    
    def _add_index_hints(self, pipeline: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Add index hints based on query patterns."""
        # This would analyze the pipeline and suggest indexes
        # For now, return as-is
        return pipeline
    
    def _optimize_projections(self, pipeline: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Optimize projection stages."""
        # Move projections earlier when safe to reduce data size
        return pipeline
    
    def cache_result(self, pipeline: List[Dict[str, Any]], result: Any, 
                    execution_time_ms: float) -> str:
        """Cache aggregation result."""
        cache_key = self._generate_cache_key(pipeline)
        
        cache_entry = {
            "result": result,
            "cached_at": datetime.utcnow(),
            "execution_time_ms": execution_time_ms,
            "hit_count": 0
        }
        
        self._query_cache[cache_key] = cache_entry
        return cache_key
    
    def get_cached_result(self, pipeline: List[Dict[str, Any]]) -> Optional[Any]:
        """Get cached result if available and valid."""
        cache_key = self._generate_cache_key(pipeline)
        
        if cache_key not in self._query_cache:
            return None
        
        cache_entry = self._query_cache[cache_key]
        
        # Check if cache entry is still valid
        age = datetime.utcnow() - cache_entry["cached_at"]
        if age.total_seconds() > self._cache_ttl:
            del self._query_cache[cache_key]
            return None
        
        # Update hit count
        cache_entry["hit_count"] += 1
        
        return cache_entry["result"]
    
    def _generate_cache_key(self, pipeline: List[Dict[str, Any]]) -> str:
        """Generate cache key for pipeline."""
        pipeline_str = str(sorted(str(stage) for stage in pipeline))
        return hashlib.md5(pipeline_str.encode()).hexdigest()
    
    def record_performance(self, pipeline_hash: str, execution_time_ms: float):
        """Record pipeline performance metrics."""
        if pipeline_hash not in self._performance_stats:
            self._performance_stats[pipeline_hash] = []
        
        self._performance_stats[pipeline_hash].append(execution_time_ms)
        
        # Keep only last 100 measurements
        if len(self._performance_stats[pipeline_hash]) > 100:
            self._performance_stats[pipeline_hash] = self._performance_stats[pipeline_hash][-100:]
        
        # Log slow queries
        if execution_time_ms > self._slow_query_threshold_ms:
            logger.warning(f"Slow aggregation query detected: {execution_time_ms}ms")
    
    def get_performance_stats(self) -> Dict[str, Any]:
        """Get performance statistics."""
        stats = {
            "cache_entries": len(self._query_cache),
            "cache_hit_rate": self._calculate_cache_hit_rate(),
            "tracked_pipelines": len(self._performance_stats),
            "slow_queries": self._count_slow_queries(),
            "avg_execution_time": self._calculate_avg_execution_time()
        }
        
        return stats
    
    def _calculate_cache_hit_rate(self) -> float:
        """Calculate cache hit rate."""
        if not self._query_cache:
            return 0.0
        
        total_hits = sum(entry["hit_count"] for entry in self._query_cache.values())
        total_entries = len(self._query_cache)
        
        return total_hits / total_entries if total_entries > 0 else 0.0
    
    def _count_slow_queries(self) -> int:
        """Count slow queries."""
        slow_count = 0
        for times in self._performance_stats.values():
            slow_count += sum(1 for t in times if t > self._slow_query_threshold_ms)
        return slow_count
    
    def _calculate_avg_execution_time(self) -> float:
        """Calculate average execution time across all queries."""
        all_times = []
        for times in self._performance_stats.values():
            all_times.extend(times)
        
        return sum(all_times) / len(all_times) if all_times else 0.0

# Global performance optimizer instance
_default_optimizer: Optional[PerformanceOptimizer] = None

def get_performance_optimizer() -> PerformanceOptimizer:
    """Get or create default performance optimizer."""
    global _default_optimizer
    if _default_optimizer is None:
        _default_optimizer = PerformanceOptimizer()
    return _default_optimizer

__all__ = ['PerformanceOptimizer', 'get_performance_optimizer']