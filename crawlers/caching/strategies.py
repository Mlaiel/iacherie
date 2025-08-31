#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Cache Strategies - Intelligent Caching Strategies and Policies
=============================================================

Advanced caching strategies with adaptive algorithms, intelligent
decision making, and machine learning-based optimization.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: All rights reserved. Unauthorized use, reproduction, or distribution prohibited.
"""

import asyncio
import logging
import random
import math
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Union, Callable, Tuple
from dataclasses import dataclass, field
from enum import Enum
from collections import defaultdict, Counter
import json

from ...core.config import get_settings
from ...core.utils import generate_uuid, get_timestamp

logger = logging.getLogger(__name__)

class StrategyType(Enum):
    """Cache strategy types."""
    LRU = "lru"                    # Least Recently Used
    LFU = "lfu"                    # Least Frequently Used
    FIFO = "fifo"                  # First In, First Out
    LIFO = "lifo"                  # Last In, First Out
    TTL = "ttl"                    # Time To Live
    SIZE = "size"                  # Size-based
    ADAPTIVE = "adaptive"          # Adaptive strategy
    ML_OPTIMIZED = "ml_optimized"  # Machine Learning optimized
    CONTENT_AWARE = "content_aware" # Content-aware strategy

class CacheDecision(Enum):
    """Cache operation decisions."""
    CACHE = "cache"
    NO_CACHE = "no_cache"
    EVICT = "evict"
    COMPRESS = "compress"
    ENCRYPT = "encrypt"

@dataclass
class CacheEntry:
    """Cache entry with strategy metadata."""
    key: str
    value: Any
    created_at: datetime
    last_accessed: datetime
    access_count: int = 0
    size_bytes: int = 0
    priority: float = 1.0
    ttl_seconds: Optional[int] = None
    content_type: Optional[str] = None
    tags: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def is_expired(self) -> bool:
        """Check if entry is expired."""
        if self.ttl_seconds is None:
            return False
        expires_at = self.created_at + timedelta(seconds=self.ttl_seconds)
        return datetime.now() > expires_at
    
    def age_seconds(self) -> float:
        """Get entry age in seconds."""



        return (datetime.now() - self.created_at).total_seconds()
    
    def idle_seconds(self) -> float:
        """Get idle time since last access."""



        return (datetime.now() - self.last_accessed).total_seconds()

@dataclass
class StrategyMetrics:
    """Strategy performance metrics."""
    hit_rate: float = 0.0
    miss_rate: float = 0.0
    eviction_rate: float = 0.0
    average_response_time: float = 0.0
    memory_efficiency: float = 0.0
    cost_effectiveness: float = 0.0

class CacheStrategy:
    """
    Base cache strategy implementation.
    
    Provides foundation for all caching strategies with
    configurable policies and adaptive behavior.
    """
    
    def __init__(self, strategy_type: StrategyType, config: Optional[Dict[str, Any]] = None):
        """Initialize cache strategy."""
        self.strategy_type = strategy_type
        self.config = config or {}
        self.logger = logging.getLogger(f"{__name__}.{strategy_type.value.upper()}Strategy")
        
        # Strategy configuration
        self.max_size = self.config.get('max_size', 1000)
        self.max_memory = self.config.get('max_memory', 104857600)  # 100MB
        self.default_ttl = self.config.get('default_ttl', 3600)
        
        # Entry tracking
        self.entries: Dict[str, CacheEntry] = {}
        self.access_order: List[str] = []
        self.frequency_counter: Counter = Counter()
        
        # Metrics
        self.metrics = StrategyMetrics()
        self.total_requests = 0
        self.cache_hits = 0
        self.cache_misses = 0
        self.evictions = 0
        
        self.logger.info(f"Cache strategy {strategy_type.value} initialized")
    
    async def should_cache(self, key: str, value: Any, 
                          metadata: Optional[Dict[str, Any]] = None) -> CacheDecision:
        """
        Decide whether to cache a value.
        
        Args:
            key: Cache key
            value: Value to potentially cache
            metadata: Additional metadata
            
        Returns:
            Cache decision
        """
        # Basic size check
        if self._estimate_size(value) > self.max_memory:
            return CacheDecision.NO_CACHE
        
        # Check capacity
        if len(self.entries) >= self.max_size:
            # Need to evict first
            return CacheDecision.EVICT
        
        return CacheDecision.CACHE
    
    async def should_evict(self, key: str) -> bool:
        """Decide whether to evict a specific entry."""
        entry = self.entries.get(key)
        if not entry:
            return False
        
        # Check expiration
        if entry.is_expired():
            return True
        
        # Strategy-specific logic
        return await self._strategy_should_evict(entry)
    
    async def select_eviction_candidates(self, count: int = 1) -> List[str]:
        """
        Select entries for eviction.
        
        Args:
            count: Number of entries to evict
            
        Returns:
            List of keys to evict
        """
        if not self.entries:
            return []
        
        # Remove expired entries first
        expired_keys = [
            key for key, entry in self.entries.items()
            if entry.is_expired()
        ]
        
        if len(expired_keys) >= count:
            return expired_keys[:count]
        
        # Use strategy-specific selection
        remaining_count = count - len(expired_keys)
        strategy_candidates = await self._strategy_select_candidates(remaining_count)
        
        return expired_keys + strategy_candidates
    
    async def record_access(self, key: str) -> None:
        """Record cache access for strategy optimization."""
        self.total_requests += 1
        
        if key in self.entries:
            # Cache hit
            self.cache_hits += 1
            entry = self.entries[key]
            entry.last_accessed = datetime.now()
            entry.access_count += 1
            
            # Update access order
            if key in self.access_order:
                self.access_order.remove(key)
            self.access_order.append(key)
            
            # Update frequency
            self.frequency_counter[key] += 1
            
        else:
            # Cache miss
            self.cache_misses += 1
        
        # Update metrics
        await self._update_metrics()
    
    async def add_entry(self, key: str, value: Any, 
                       metadata: Optional[Dict[str, Any]] = None) -> bool:
        """Add entry to cache with strategy tracking."""



        try:
            entry = CacheEntry(
                key=key,
                value=value,
                created_at=datetime.now(),
                last_accessed=datetime.now(),
                size_bytes=self._estimate_size(value),
                ttl_seconds=metadata.get('ttl') if metadata else self.default_ttl
            )
            
            if metadata:
                entry.content_type = metadata.get('content_type')
                entry.tags = metadata.get('tags', [])
                entry.priority = metadata.get('priority', 1.0)
                entry.metadata = metadata
            
            self.entries[key] = entry
            
            # Update tracking structures
            self.access_order.append(key)
            self.frequency_counter[key] = 1
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error adding entry {key}: {e}")
            return False
    
    async def remove_entry(self, key: str) -> bool:
        """Remove entry from cache and tracking."""



        try:
            if key in self.entries:
                del self.entries[key]
                
                # Update tracking structures
                if key in self.access_order:
                    self.access_order.remove(key)
                
                if key in self.frequency_counter:
                    del self.frequency_counter[key]
                
                self.evictions += 1
                return True
            
            return False
            
        except Exception as e:
            self.logger.error(f"Error removing entry {key}: {e}")
            return False
    
    def _estimate_size(self, value: Any) -> int:
        """Estimate memory size of value."""
        if isinstance(value, str):
            return len(value.encode('utf-8'))
        elif isinstance(value, bytes):
            return len(value)
        elif isinstance(value, (dict, list)):
            return len(json.dumps(value).encode('utf-8'))
        else:
            # Rough estimation
            return 1024  # 1KB default
    
    async def _strategy_should_evict(self, entry: CacheEntry) -> bool:
        """Strategy-specific eviction decision."""
        # Base implementation - override in subclasses
        return False
    
    async def _strategy_select_candidates(self, count: int) -> List[str]:
        """Strategy-specific candidate selection."""
        # Base implementation - LRU
        return self.access_order[:count]
    
    async def _update_metrics(self) -> None:
        """Update strategy metrics."""
        if self.total_requests > 0:
            self.metrics.hit_rate = self.cache_hits / self.total_requests
            self.metrics.miss_rate = self.cache_misses / self.total_requests
        
        if self.cache_hits + self.cache_misses > 0:
            self.metrics.eviction_rate = self.evictions / (self.cache_hits + self.cache_misses)
    
    async def get_metrics(self) -> StrategyMetrics:
        """Get current strategy metrics."""
        await self._update_metrics()
        return self.metrics
    
    async def optimize(self) -> Dict[str, Any]:
        """Optimize strategy based on current performance."""
        # Base optimization - override in subclasses
        return {"optimizations_applied": []}

class AdaptiveStrategy(CacheStrategy):
    """
    Adaptive cache strategy that learns and optimizes itself.
    
    Combines multiple strategies and adapts based on workload patterns.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize adaptive strategy."""
        super().__init__(StrategyType.ADAPTIVE, config)
        self.logger = logging.getLogger(f"{__name__}.AdaptiveStrategy")
        
        # Available sub-strategies
        self.strategies = {
            'lru': self._lru_score,
            'lfu': self._lfu_score,
            'ttl': self._ttl_score,
            'size': self._size_score
        }
        
        # Strategy weights (learned over time)
        self.strategy_weights = {name: 1.0 for name in self.strategies.keys()}
        
        # Learning parameters
        self.learning_rate = 0.1
        self.exploration_rate = 0.1
        self.adaptation_interval = 100  # requests
        self.requests_since_adaptation = 0
        
        # Performance tracking
        self.strategy_performance = defaultdict(list)
        
    async def should_cache(self, key: str, value: Any,
                          metadata: Optional[Dict[str, Any]] = None) -> CacheDecision:
        """Adaptive caching decision."""
        # Use weighted combination of strategies
        scores = {}
        for strategy_name, strategy_func in self.strategies.items():
            scores[strategy_name] = await strategy_func(key, value, metadata)
        
        # Calculate weighted score
        total_score = sum(
            score * self.strategy_weights[name]
            for name, score in scores.items()
        )
        
        total_weight = sum(self.strategy_weights.values())
        final_score = total_score / total_weight if total_weight > 0 else 0
        
        # Make decision based on score
        if final_score > 0.7:
            return CacheDecision.CACHE
        elif final_score > 0.4:
            return CacheDecision.COMPRESS  # Cache with compression
        else:
            return CacheDecision.NO_CACHE
    
    async def select_eviction_candidates(self, count: int = 1) -> List[str]:
        """Adaptive eviction candidate selection."""
        if not self.entries:
            return []
        
        # Score all entries using current strategy weights
        entry_scores = {}
        
        for key, entry in self.entries.items():
            scores = {}
            for strategy_name, strategy_func in self.strategies.items():
                scores[strategy_name] = await strategy_func(key, entry.value, entry.metadata)
            
            # Calculate weighted eviction score (lower = more likely to evict)
            total_score = sum(
                score * self.strategy_weights[name]
                for name, score in scores.items()
            )
            
            entry_scores[key] = total_score
        
        # Sort by score (ascending - lowest scores evicted first)
        sorted_entries = sorted(entry_scores.items(), key=lambda x: x[1])
        
        return [key for key, score in sorted_entries[:count]]
    
    async def record_access(self, key: str) -> None:
        """Record access and potentially adapt strategy."""
        await super().record_access(key)
        
        self.requests_since_adaptation += 1
        
        # Adapt strategy weights periodically
        if self.requests_since_adaptation >= self.adaptation_interval:
            await self._adapt_strategy()
            self.requests_since_adaptation = 0
    
    async def _adapt_strategy(self) -> None:
        """Adapt strategy weights based on performance."""



        try:
            # Calculate recent performance for each strategy
            current_hit_rate = self.metrics.hit_rate
            
            # Adjust weights based on performance
            for strategy_name in self.strategies.keys():
                # Simple reinforcement learning
                if current_hit_rate > 0.8:  # Good performance
                    self.strategy_weights[strategy_name] *= (1 + self.learning_rate)
                elif current_hit_rate < 0.6:  # Poor performance
                    self.strategy_weights[strategy_name] *= (1 - self.learning_rate)
                
                # Ensure weights don't go below minimum
                self.strategy_weights[strategy_name] = max(0.1, self.strategy_weights[strategy_name])
            
            # Add exploration noise
            if random.random() < self.exploration_rate:
                random_strategy = random.choice(list(self.strategies.keys()))
                self.strategy_weights[random_strategy] *= 1.2
            
            # Normalize weights
            total_weight = sum(self.strategy_weights.values())
            if total_weight > 0:
                for name in self.strategy_weights:
                    self.strategy_weights[name] /= total_weight
            
            self.logger.debug(f"Adapted strategy weights: {self.strategy_weights}")
            
        except Exception as e:
            self.logger.error(f"Error adapting strategy: {e}")
    
    async def _lru_score(self, key: str, value: Any, 
                        metadata: Optional[Dict[str, Any]] = None) -> float:
        """LRU-based scoring."""
        if key in self.entries:
            entry = self.entries[key]
            idle_time = entry.idle_seconds()
            # Score decreases with idle time
            return max(0, 1 - idle_time / 3600)  # 1 hour max
        return 0.5  # Neutral for new entries
    
    async def _lfu_score(self, key: str, value: Any,
                        metadata: Optional[Dict[str, Any]] = None) -> float:
        """LFU-based scoring."""
        if key in self.entries:
            entry = self.entries[key]
            frequency = entry.access_count
            max_frequency = max(e.access_count for e in self.entries.values()) if self.entries else 1
            return frequency / max_frequency if max_frequency > 0 else 0
        return 0.1  # Low score for new entries
    
    async def _ttl_score(self, key: str, value: Any,
                        metadata: Optional[Dict[str, Any]] = None) -> float:
        """TTL-based scoring."""
        if key in self.entries:
            entry = self.entries[key]
            if entry.ttl_seconds:
                remaining_ratio = 1 - (entry.age_seconds() / entry.ttl_seconds)
                return max(0, remaining_ratio)
        return 0.5  # Neutral for entries without TTL
    
    async def _size_score(self, key: str, value: Any,
                         metadata: Optional[Dict[str, Any]] = None) -> float:
        """Size-based scoring."""
        size = self._estimate_size(value)
        # Prefer smaller items (inverse scoring)
        max_size = 1048576  # 1MB
        return max(0, 1 - size / max_size)
    
    async def optimize(self) -> Dict[str, Any]:
        """Optimize adaptive strategy."""
        optimizations = []
        
        # Analyze strategy performance
        best_strategy = max(self.strategy_weights.items(), key=lambda x: x[1])
        worst_strategy = min(self.strategy_weights.items(), key=lambda x: x[1])
        
        optimizations.append(f"Best performing strategy: {best_strategy[0]} ({best_strategy[1]:.3f})")
        optimizations.append(f"Worst performing strategy: {worst_strategy[0]} ({worst_strategy[1]:.3f})")
        
        # Suggest configuration changes
        if self.metrics.hit_rate < 0.7:
            optimizations.append("Consider increasing cache size or adjusting TTL")
        
        if self.metrics.eviction_rate > 0.2:
            optimizations.append("High eviction rate - consider memory optimization")
        
        return {
            "optimizations_applied": optimizations,
            "strategy_weights": self.strategy_weights.copy(),
            "current_metrics": await self.get_metrics()
        }

# Strategy factory
def create_strategy(strategy_type: StrategyType, 
                   config: Optional[Dict[str, Any]] = None) -> CacheStrategy:
    """Create cache strategy instance."""
    if strategy_type == StrategyType.ADAPTIVE:
        return AdaptiveStrategy(config)
    else:
        return CacheStrategy(strategy_type, config)
