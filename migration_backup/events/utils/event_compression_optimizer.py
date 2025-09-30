"""Event Compression Optimizer - Advanced for Ainflue Events

Advanced event compression optimizer with intelligent algorithms,
real-time optimization, and business-aware compression strategies.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import time
import json
import gzip
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class CompressionAlgorithm(Enum):
    """Supported compression algorithms"""
    NONE = "none"
    GZIP = "gzip"
    LZ4 = "lz4"
    ZSTD = "zstd"
    BROTLI = "brotli"
    CUSTOM = "custom"


class CompressionLevel(Enum):
    """Compression levels"""
    FASTEST = "fastest"
    BALANCED = "balanced"
    BEST = "best"
    ADAPTIVE = "adaptive"


@dataclass
class CompressionResult:
    """Result of compression operation"""
    original_size: int
    compressed_size: int
    compression_ratio: float
    algorithm: CompressionAlgorithm
    level: str
    compression_time: float
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class CompressionStrategy:
    """Compression strategy configuration"""
    name: str
    algorithm: CompressionAlgorithm
    level: CompressionLevel
    min_size_threshold: int = 1024  # 1KB
    max_size_threshold: int = 10485760  # 10MB
    event_patterns: List[str] = field(default_factory=list)
    business_priorities: List[str] = field(default_factory=list)
    enabled: bool = True


class EventCompressionOptimizer:
    """
    Advanced event compression optimizer for Ainflue platform
    Intelligent algorithms with business-aware compression strategies
    """
    
    def __init__(self):
        self.compression_strategies: List[CompressionStrategy] = []
        self.compression_history: List[CompressionResult] = []
        self.algorithm_performance: Dict[str, Dict[str, float]] = {}
        
        self._initialize_compression_strategies()
        self._initialize_algorithm_performance()
        
        logger.info("EventCompressionOptimizer initialized for Ainflue platform")
    
    def _initialize_compression_strategies(self):
        """Initialize compression strategies for different event types"""
        
        # High-priority real-time events - fastest compression
        real_time_strategy = CompressionStrategy(
            name="real_time_events",
            algorithm=CompressionAlgorithm.LZ4,
            level=CompressionLevel.FASTEST,
            min_size_threshold=512,  # 512 bytes
            event_patterns=["user.activity.*", "analytics.tracking.*", "api.request.*"],
            business_priorities=["critical", "high"]
        )
        
        # Content events - balanced compression
        content_strategy = CompressionStrategy(
            name="content_events",
            algorithm=CompressionAlgorithm.ZSTD,
            level=CompressionLevel.BALANCED,
            min_size_threshold=2048,  # 2KB
            event_patterns=["content.*", "media.*"],
            business_priorities=["medium", "high"]
        )
        
        # Analytics events - best compression (not time sensitive)
        analytics_strategy = CompressionStrategy(
            name="analytics_events", 
            algorithm=CompressionAlgorithm.BROTLI,
            level=CompressionLevel.BEST,
            min_size_threshold=1024,  # 1KB
            max_size_threshold=52428800,  # 50MB
            event_patterns=["analytics.*", "metrics.*", "reporting.*"],
            business_priorities=["low", "medium"]
        )
        
        # Monetization events - fast but reliable compression
        monetization_strategy = CompressionStrategy(
            name="monetization_events",
            algorithm=CompressionAlgorithm.GZIP,
            level=CompressionLevel.BALANCED,
            min_size_threshold=256,  # 256 bytes
            event_patterns=["monetization.*", "payment.*", "revenue.*"],
            business_priorities=["critical", "high"]
        )
        
        # Collaboration events - adaptive compression
        collaboration_strategy = CompressionStrategy(
            name="collaboration_events",
            algorithm=CompressionAlgorithm.ZSTD,
            level=CompressionLevel.ADAPTIVE,
            min_size_threshold=1024,
            event_patterns=["collaboration.*", "matching.*"],
            business_priorities=["medium"]
        )
        
        # Large events - maximum compression
        large_events_strategy = CompressionStrategy(
            name="large_events",
            algorithm=CompressionAlgorithm.BROTLI,
            level=CompressionLevel.BEST,
            min_size_threshold=1048576,  # 1MB
            event_patterns=["*"],  # Catch-all for large events
            business_priorities=["low", "medium", "high"]
        )
        
        self.compression_strategies = [
            real_time_strategy,
            content_strategy,
            analytics_strategy,
            monetization_strategy,
            collaboration_strategy,
            large_events_strategy
        ]
    
    def _initialize_algorithm_performance(self):
        """Initialize baseline performance metrics for algorithms"""
        
        self.algorithm_performance = {
            CompressionAlgorithm.GZIP.value: {
                "avg_compression_ratio": 3.2,
                "avg_compression_time_ms": 15.0,
                "reliability_score": 0.95
            },
            CompressionAlgorithm.LZ4.value: {
                "avg_compression_ratio": 2.1,
                "avg_compression_time_ms": 2.0,
                "reliability_score": 0.98
            },
            CompressionAlgorithm.ZSTD.value: {
                "avg_compression_ratio": 4.1,
                "avg_compression_time_ms": 8.0,
                "reliability_score": 0.96
            },
            CompressionAlgorithm.BROTLI.value: {
                "avg_compression_ratio": 4.8,
                "avg_compression_time_ms": 45.0,
                "reliability_score": 0.94
            }
        }
    
    async def optimize_event_compression(self, event_data: Dict[str, Any],
                                       business_context: Optional[Dict[str, Any]] = None) -> CompressionResult:
        """Optimize compression for an event with business awareness"""
        
        business_context = business_context or {}
        
        # Serialize event to get size
        serialized_data = json.dumps(event_data, separators=(',', ':')).encode('utf-8')
        original_size = len(serialized_data)
        
        # Find best compression strategy
        strategy = await self._select_compression_strategy(event_data, business_context, original_size)
        
        if not strategy:
            # No compression needed
            return CompressionResult(
                original_size=original_size,
                compressed_size=original_size,
                compression_ratio=1.0,
                algorithm=CompressionAlgorithm.NONE,
                level="none",
                compression_time=0.0,
                metadata={"reason": "no_strategy_matched"}
            )
        
        # Apply compression
        result = await self._apply_compression(serialized_data, strategy, business_context)
        
        # Update performance metrics
        await self._update_performance_metrics(result)
        
        # Store in history
        self.compression_history.append(result)
        
        logger.debug(f"Compressed event {event_data.get('event_id', 'unknown')} using {strategy.name}: "
                    f"{original_size} -> {result.compressed_size} bytes "
                    f"({result.compression_ratio:.2f}x compression)")
        
        return result
    
    async def _select_compression_strategy(self, event_data: Dict[str, Any],
                                         business_context: Dict[str, Any],
                                         data_size: int) -> Optional[CompressionStrategy]:
        """Select optimal compression strategy based on event and business context"""
        
        event_type = event_data.get("event_type", "")
        business_priority = business_context.get("priority", "medium")
        user_tier = business_context.get("user_tier", "free")
        real_time_required = business_context.get("real_time_required", False)
        
        # Score strategies based on multiple factors
        strategy_scores = []
        
        for strategy in self.compression_strategies:
            if not strategy.enabled:
                continue
            
            score = 0.0
            
            # Size threshold check
            if data_size < strategy.min_size_threshold or data_size > strategy.max_size_threshold:
                continue
            
            # Event pattern matching
            pattern_match = False
            for pattern in strategy.event_patterns:
                if self._matches_pattern(event_type, pattern):
                    pattern_match = True
                    score += 10.0
                    break
            
            if not pattern_match and "*" not in strategy.event_patterns:
                continue
            
            # Business priority alignment
            if business_priority in strategy.business_priorities:
                score += 8.0
            
            # Real-time performance consideration
            if real_time_required:
                if strategy.algorithm in [CompressionAlgorithm.LZ4, CompressionAlgorithm.GZIP]:
                    score += 6.0
                elif strategy.algorithm in [CompressionAlgorithm.BROTLI]:
                    score -= 4.0  # Too slow for real-time
            
            # User tier consideration
            if user_tier == "enterprise" and strategy.level in [CompressionLevel.BEST, CompressionLevel.ADAPTIVE]:
                score += 4.0
            elif user_tier == "free" and strategy.level == CompressionLevel.FASTEST:
                score += 3.0
            
            # Data size optimization
            if data_size > 1048576:  # > 1MB
                if strategy.algorithm in [CompressionAlgorithm.BROTLI, CompressionAlgorithm.ZSTD]:
                    score += 5.0
            elif data_size < 10240:  # < 10KB
                if strategy.algorithm == CompressionAlgorithm.LZ4:
                    score += 3.0
            
            # Historical performance
            algo_perf = self.algorithm_performance.get(strategy.algorithm.value, {})
            reliability = algo_perf.get("reliability_score", 0.5)
            score += reliability * 2.0
            
            strategy_scores.append((strategy, score))
        
        if not strategy_scores:
            return None
        
        # Select strategy with highest score
        best_strategy = max(strategy_scores, key=lambda x: x[1])[0]
        return best_strategy
    
    def _matches_pattern(self, event_type: str, pattern: str) -> bool:
        """Check if event type matches pattern"""
        
        if pattern == "*":
            return True
        
        if pattern.endswith("*"):
            return event_type.startswith(pattern[:-1])
        
        return event_type == pattern
    
    async def _apply_compression(self, data: bytes, strategy: CompressionStrategy,
                               business_context: Dict[str, Any]) -> CompressionResult:
        """Apply compression using specified strategy"""
        
        start_time = time.time()
        original_size = len(data)
        
        try:
            # Apply compression based on algorithm
            if strategy.algorithm == CompressionAlgorithm.GZIP:
                compressed_data = await self._compress_gzip(data, strategy.level)
            elif strategy.algorithm == CompressionAlgorithm.LZ4:
                compressed_data = await self._compress_lz4(data, strategy.level)
            elif strategy.algorithm == CompressionAlgorithm.ZSTD:
                compressed_data = await self._compress_zstd(data, strategy.level)
            elif strategy.algorithm == CompressionAlgorithm.BROTLI:
                compressed_data = await self._compress_brotli(data, strategy.level)
            elif strategy.algorithm == CompressionAlgorithm.CUSTOM:
                compressed_data = await self._compress_custom(data, strategy.level, business_context)
            else:
                compressed_data = data  # No compression
            
            compression_time = (time.time() - start_time) * 1000  # ms
            compressed_size = len(compressed_data)
            compression_ratio = original_size / compressed_size if compressed_size > 0 else 1.0
            
            return CompressionResult(
                original_size=original_size,
                compressed_size=compressed_size,
                compression_ratio=compression_ratio,
                algorithm=strategy.algorithm,
                level=strategy.level.value,
                compression_time=compression_time,
                metadata={
                    "strategy": strategy.name,
                    "success": True
                }
            )
            
        except Exception as e:
            compression_time = (time.time() - start_time) * 1000
            logger.error(f"Compression failed with {strategy.algorithm.value}: {e}")
            
            return CompressionResult(
                original_size=original_size,
                compressed_size=original_size,
                compression_ratio=1.0,
                algorithm=CompressionAlgorithm.NONE,
                level="error",
                compression_time=compression_time,
                metadata={
                    "strategy": strategy.name,
                    "success": False,
                    "error": str(e)
                }
            )
    
    async def _compress_gzip(self, data: bytes, level: CompressionLevel) -> bytes:
        """Compress using GZIP"""
        
        compression_level = {
            CompressionLevel.FASTEST: 1,
            CompressionLevel.BALANCED: 6,
            CompressionLevel.BEST: 9,
            CompressionLevel.ADAPTIVE: 6
        }.get(level, 6)
        
        return gzip.compress(data, compresslevel=compression_level)
    
    async def _compress_lz4(self, data: bytes, level: CompressionLevel) -> bytes:
        """Compress using LZ4"""
        
        try:
            import lz4.frame
            
            compression_level = {
                CompressionLevel.FASTEST: 0,
                CompressionLevel.BALANCED: 4,
                CompressionLevel.BEST: 12,
                CompressionLevel.ADAPTIVE: 4
            }.get(level, 4)
            
            return lz4.frame.compress(data, compression_level=compression_level)
            
        except ImportError:
            logger.warning("LZ4 not available, falling back to GZIP")
            return await self._compress_gzip(data, level)
    
    async def _compress_zstd(self, data: bytes, level: CompressionLevel) -> bytes:
        """Compress using Zstandard"""
        
        try:
            import zstandard as zstd
            
            compression_level = {
                CompressionLevel.FASTEST: 1,
                CompressionLevel.BALANCED: 9,
                CompressionLevel.BEST: 22,
                CompressionLevel.ADAPTIVE: 9
            }.get(level, 9)
            
            cctx = zstd.ZstdCompressor(level=compression_level)
            return cctx.compress(data)
            
        except ImportError:
            logger.warning("Zstandard not available, falling back to GZIP")
            return await self._compress_gzip(data, level)
    
    async def _compress_brotli(self, data: bytes, level: CompressionLevel) -> bytes:
        """Compress using Brotli"""
        
        try:
            import brotli
            
            compression_level = {
                CompressionLevel.FASTEST: 1,
                CompressionLevel.BALANCED: 6,
                CompressionLevel.BEST: 11,
                CompressionLevel.ADAPTIVE: 6
            }.get(level, 6)
            
            return brotli.compress(data, quality=compression_level)
            
        except ImportError:
            logger.warning("Brotli not available, falling back to GZIP")
            return await self._compress_gzip(data, level)
    
    async def _compress_custom(self, data: bytes, level: CompressionLevel,
                             business_context: Dict[str, Any]) -> bytes:
        """Custom compression for Ainflue-specific optimizations"""
        
        # Custom compression could include:
        # - Dictionary compression for repeated fields
        # - Delta compression for similar events
        # - Business-specific optimizations
        
        # For now, use adaptive algorithm selection
        data_size = len(data)
        
        if data_size < 10240:  # < 10KB - use LZ4
            return await self._compress_lz4(data, CompressionLevel.FASTEST)
        elif data_size < 1048576:  # < 1MB - use ZSTD
            return await self._compress_zstd(data, CompressionLevel.BALANCED)
        else:  # > 1MB - use Brotli
            return await self._compress_brotli(data, CompressionLevel.BEST)
    
    async def _update_performance_metrics(self, result: CompressionResult):
        """Update algorithm performance metrics"""
        
        algo_key = result.algorithm.value
        
        if algo_key not in self.algorithm_performance:
            self.algorithm_performance[algo_key] = {
                "avg_compression_ratio": result.compression_ratio,
                "avg_compression_time_ms": result.compression_time,
                "reliability_score": 1.0 if result.metadata.get("success", False) else 0.0,
                "sample_count": 1
            }
        else:
            perf = self.algorithm_performance[algo_key]
            count = perf.get("sample_count", 1)
            
            # Update running averages
            perf["avg_compression_ratio"] = (perf["avg_compression_ratio"] * count + result.compression_ratio) / (count + 1)
            perf["avg_compression_time_ms"] = (perf["avg_compression_time_ms"] * count + result.compression_time) / (count + 1)
            
            # Update reliability score
            success = 1.0 if result.metadata.get("success", False) else 0.0
            perf["reliability_score"] = (perf["reliability_score"] * count + success) / (count + 1)
            perf["sample_count"] = count + 1
    
    async def batch_optimize_compression(self, events: List[Dict[str, Any]],
                                       business_contexts: Optional[List[Dict[str, Any]]] = None) -> List[CompressionResult]:
        """Optimize compression for batch of events"""
        
        if business_contexts is None:
            business_contexts = [{}] * len(events)
        
        results = []
        
        # Group similar events for potential optimization
        event_groups = await self._group_similar_events(events)
        
        for group_events, group_indices in event_groups:
            # Optimize compression for similar events together
            group_results = await self._optimize_event_group(group_events, 
                                                           [business_contexts[i] for i in group_indices])
            
            # Map results back to original order
            for i, result in enumerate(group_results):
                original_index = group_indices[i]
                results.append((original_index, result))
        
        # Sort by original index
        results.sort(key=lambda x: x[0])
        
        return [result for _, result in results]
    
    async def _group_similar_events(self, events: List[Dict[str, Any]]) -> List[Tuple[List[Dict[str, Any]], List[int]]]:
        """Group similar events for batch optimization"""
        
        groups = {}
        
        for i, event in enumerate(events):
            event_type = event.get("event_type", "")
            
            # Group by event type prefix
            group_key = event_type.split('.')[0] if '.' in event_type else event_type
            
            if group_key not in groups:
                groups[group_key] = ([], [])
            
            groups[group_key][0].append(event)
            groups[group_key][1].append(i)
        
        return list(groups.values())
    
    async def _optimize_event_group(self, events: List[Dict[str, Any]], 
                                  business_contexts: List[Dict[str, Any]]) -> List[CompressionResult]:
        """Optimize compression for a group of similar events"""
        
        results = []
        
        # For similar events, we could potentially use dictionary compression
        # or find common patterns, but for now process individually
        
        for event, context in zip(events, business_contexts):
            result = await self.optimize_event_compression(event, context)
            results.append(result)
        
        return results
    
    def get_compression_statistics(self) -> Dict[str, Any]:
        """Get comprehensive compression statistics"""
        
        if not self.compression_history:
            return {"message": "No compression data available"}
        
        total_original = sum(r.original_size for r in self.compression_history)
        total_compressed = sum(r.compressed_size for r in self.compression_history)
        overall_ratio = total_original / total_compressed if total_compressed > 0 else 1.0
        
        # Algorithm usage
        algo_usage = {}
        for result in self.compression_history:
            algo = result.algorithm.value
            if algo not in algo_usage:
                algo_usage[algo] = {"count": 0, "total_ratio": 0.0, "total_time": 0.0}
            
            algo_usage[algo]["count"] += 1
            algo_usage[algo]["total_ratio"] += result.compression_ratio
            algo_usage[algo]["total_time"] += result.compression_time
        
        # Calculate averages
        for algo_data in algo_usage.values():
            count = algo_data["count"]
            algo_data["avg_ratio"] = algo_data["total_ratio"] / count
            algo_data["avg_time"] = algo_data["total_time"] / count
        
        return {
            "total_events_compressed": len(self.compression_history),
            "total_original_size_mb": total_original / 1024 / 1024,
            "total_compressed_size_mb": total_compressed / 1024 / 1024,
            "overall_compression_ratio": overall_ratio,
            "space_saved_mb": (total_original - total_compressed) / 1024 / 1024,
            "average_compression_time_ms": sum(r.compression_time for r in self.compression_history) / len(self.compression_history),
            "algorithm_usage": algo_usage,
            "algorithm_performance": dict(self.algorithm_performance),
            "active_strategies": len([s for s in self.compression_strategies if s.enabled]),
            "recent_performance": self._get_recent_performance_summary()
        }
    
    def _get_recent_performance_summary(self) -> Dict[str, Any]:
        """Get summary of recent compression performance"""
        
        # Last 100 compressions
        recent = self.compression_history[-100:] if len(self.compression_history) > 100 else self.compression_history
        
        if not recent:
            return {}
        
        return {
            "sample_size": len(recent),
            "avg_compression_ratio": sum(r.compression_ratio for r in recent) / len(recent),
            "avg_compression_time_ms": sum(r.compression_time for r in recent) / len(recent),
            "success_rate": sum(1 for r in recent if r.metadata.get("success", False)) / len(recent),
            "most_used_algorithm": max(
                set(r.algorithm.value for r in recent),
                key=lambda algo: sum(1 for r in recent if r.algorithm.value == algo)
            )
        }
    
    def add_compression_strategy(self, strategy: CompressionStrategy):
        """Add custom compression strategy"""
        self.compression_strategies.append(strategy)
        logger.info(f"Added compression strategy: {strategy.name}")
    
    def disable_strategy(self, strategy_name: str):
        """Disable a compression strategy"""
        for strategy in self.compression_strategies:
            if strategy.name == strategy_name:
                strategy.enabled = False
                logger.info(f"Disabled compression strategy: {strategy_name}")
                break


# Export main classes
__all__ = [
    'EventCompressionOptimizer',
    'CompressionAlgorithm',
    'CompressionLevel',
    'CompressionResult',
    'CompressionStrategy'
]