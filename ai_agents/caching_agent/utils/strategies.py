"""Cache Strategies - Intelligent Caching Algorithms

Advanced cache eviction and retention strategies providing optimal cache
performance based on access patterns, content characteristics, and business logic.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.
"""import asyncio
import logging
import math
import time
from abc import ABC, abstractmethod
from collections import defaultdict, deque
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, List, Optional, Any, Set, Tuple
import heapq
import statistics

logger = logging.getLogger(__name__)

class EvictionReason(Enum):
    """Reasons for cache entry eviction"""    TTL_EXPIRED = "ttl_expired"
    MEMORY_PRESSURE = "memory_pressure"
    LRU_EVICTION = "lru_eviction"
    LFU_EVICTION = "lfu_eviction"
    PRIORITY_BASED = "priority_based"
    USER_REQUESTED = "user_requested"
    GEOGRAPHIC_LOCALITY = "geographic_locality"
    CONTENT_FRESHNESS = "content_freshness"

@dataclass
class AccessPattern:
    """Cache access pattern analysis"""    key: str
    total_accesses: int = 0
    recent_accesses: int = 0
    access_frequency: float = 0.0
    last_access_time: datetime = field(default_factory=datetime.utcnow)
    access_intervals: List[float] = field(default_factory=list)
    geographic_distribution: Dict[str, int] = field(default_factory=dict)
    user_diversity: Set[str] = field(default_factory=set)
    temporal_pattern: List[int] = field(default_factory=lambda: [0] * 24)  # Hourly access pattern

@dataclass
class EvictionCandidate:
    """Candidate for cache eviction with scoring"""    key: str
    score: float
    reason: EvictionReason
    size_bytes: int
    last_accessed: datetime
    metadata: Dict[str, Any] = field(default_factory=dict)

class CacheStrategy(ABC):
    """Abstract base class for cache strategies"""    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.access_patterns: Dict[str, AccessPattern] = {}
        
    @abstractmethod
    async def should_cache(self, key: str, value: Any, metadata: Dict[str, Any]) -> bool:
        """Determine if item should be cached"""        pass
    
    @abstractmethod
    async def select_eviction_candidates(
        self, 
        cache_entries: Dict[str, Any],
        required_space: int,
        current_usage: int,
        max_capacity: int
    ) -> List[EvictionCandidate]:
        """Select entries for eviction"""        pass
    
    @abstractmethod
    async def update_access_pattern(self, key: str, access_info: Dict[str, Any]):
        """Update access pattern for cache optimization"""        pass
    
    def record_access(self, key: str, user_id: Optional[str] = None, 
                     location: Optional[str] = None):
        """Record cache access for pattern analysis"""        if key not in self.access_patterns:
            self.access_patterns[key] = AccessPattern(key=key)
        
        pattern = self.access_patterns[key]
        current_time = datetime.utcnow()
        
        # Update access counts
        pattern.total_accesses += 1
        pattern.recent_accesses += 1
        
        # Update temporal pattern (hour of day)
        hour = current_time.hour
        pattern.temporal_pattern[hour] += 1
        
        # Calculate access interval
        if pattern.last_access_time:
            interval = (current_time - pattern.last_access_time).total_seconds()
            pattern.access_intervals.append(interval)
            # Keep only recent intervals for pattern analysis
            if len(pattern.access_intervals) > 100:
                pattern.access_intervals.pop(0)
        
        pattern.last_access_time = current_time
        
        # Update geographic distribution
        if location:
            pattern.geographic_distribution[location] = (
                pattern.geographic_distribution.get(location, 0) + 1
            )
        
        # Update user diversity
        if user_id:
            pattern.user_diversity.add(user_id)

class LRUStrategy(CacheStrategy):
    """Least Recently Used eviction strategy with enhanced analytics"""    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__(config)
        self.access_order: deque = deque()
        self.access_times: Dict[str, datetime] = {}
    
    async def should_cache(self, key: str, value: Any, metadata: Dict[str, Any]) -> bool:
        """Always cache with LRU - relies on eviction for space management"""        return True
    
    async def select_eviction_candidates(
        self,
        cache_entries: Dict[str, Any],
        required_space: int,
        current_usage: int,
        max_capacity: int
    ) -> List[EvictionCandidate]:
        """Select least recently used entries for eviction"""        candidates = []
        
        # Sort entries by last access time (oldest first)
        sorted_entries = sorted(
            cache_entries.items(),
            key=lambda x: x[1].last_accessed
        )
        
        freed_space = 0
        for key, entry in sorted_entries:
            if freed_space >= required_space:
                break
                
            candidates.append(EvictionCandidate(
                key=key,
                score=1.0 / (entry.access_count + 1),  # Lower access count = higher eviction score
                reason=EvictionReason.LRU_EVICTION,
                size_bytes=entry.size_bytes,
                last_accessed=entry.last_accessed
            ))
            
            freed_space += entry.size_bytes
        
        return candidates
    
    async def update_access_pattern(self, key: str, access_info: Dict[str, Any]):
        """Update LRU access tracking"""        self.record_access(
            key, 
            access_info.get('user_id'),
            access_info.get('location')
        )
        
        # Update access order
        if key in self.access_times:
            # Remove from current position
            try:
                self.access_order.remove(key)
            except ValueError:
                pass
        
        # Add to end (most recently used)
        self.access_order.append(key)
        self.access_times[key] = datetime.utcnow()

class TTLStrategy(CacheStrategy):
    """Time-To-Live based eviction with smart TTL adjustment"""    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__(config)
        self.default_ttl = config.get('default_ttl', 3600)  # 1 hour
        self.ttl_adjustments: Dict[str, float] = {}  # Key -> TTL multiplier
    
    async def should_cache(self, key: str, value: Any, metadata: Dict[str, Any]) -> bool:
        """Cache with TTL consideration"""        content_type = metadata.get('content_type')
        
        # Don't cache very short-lived data
        if content_type in ['real_time_data', 'live_stream']:
            return False
            
        return True
    
    async def select_eviction_candidates(
        self,
        cache_entries: Dict[str, Any],
        required_space: int,
        current_usage: int,
        max_capacity: int
    ) -> List[EvictionCandidate]:
        """Select expired and near-expiry entries"""        candidates = []
        current_time = datetime.utcnow()
        
        for key, entry in cache_entries.items():
            if not entry.ttl:
                continue
                
            # Check if expired
            expiry_time = entry.created_at + timedelta(seconds=entry.ttl)
            if current_time >= expiry_time:
                candidates.append(EvictionCandidate(
                    key=key,
                    score=1.0,  # Expired entries get highest eviction priority
                    reason=EvictionReason.TTL_EXPIRED,
                    size_bytes=entry.size_bytes,
                    last_accessed=entry.last_accessed
                ))
            else:
                # Calculate proximity to expiration
                time_remaining = (expiry_time - current_time).total_seconds()
                expiration_ratio = 1.0 - (time_remaining / entry.ttl)
                
                if expiration_ratio > 0.8:  # Near expiry (80% of TTL elapsed)
                    candidates.append(EvictionCandidate(
                        key=key,
                        score=expiration_ratio,
                        reason=EvictionReason.TTL_EXPIRED,
                        size_bytes=entry.size_bytes,
                        last_accessed=entry.last_accessed
                    ))
        
        # Sort by expiration score (closest to expiry first)
        candidates.sort(key=lambda x: x.score, reverse=True)
        
        return candidates
    
    async def update_access_pattern(self, key: str, access_info: Dict[str, Any]):
        """Update TTL based on access patterns"""        self.record_access(
            key,
            access_info.get('user_id'),
            access_info.get('location')
        )
        
        pattern = self.access_patterns[key]
        
        # Adjust TTL based on access frequency
        if pattern.total_accesses > 10:
            avg_interval = statistics.mean(pattern.access_intervals) if pattern.access_intervals else 3600
            
            # Frequently accessed items get longer TTL
            if avg_interval < 300:  # < 5 minutes between accesses
                self.ttl_adjustments[key] = 2.0
            elif avg_interval < 1800:  # < 30 minutes
                self.ttl_adjustments[key] = 1.5
            else:
                self.ttl_adjustments[key] = 1.0

class AdaptiveStrategy(CacheStrategy):
    """Intelligent adaptive strategy combining multiple algorithms"""    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__(config)
        self.lru_strategy = LRUStrategy(config)
        self.ttl_strategy = TTLStrategy(config)
        
        # Strategy weights (can be adjusted based on performance)
        self.strategy_weights = {
            'access_frequency': 0.3,
            'recency': 0.25,
            'content_importance': 0.2,
            'user_diversity': 0.15,
            'geographic_spread': 0.1
        }
        
        # Performance tracking for strategy optimization
        self.strategy_performance: Dict[str, List[float]] = defaultdict(list)
    
    async def should_cache(self, key: str, value: Any, metadata: Dict[str, Any]) -> bool:
        """Intelligent caching decision based on multiple factors"""        content_type = metadata.get('content_type', '')
        size_bytes = metadata.get('size_bytes', 0)
        priority = metadata.get('priority', 'normal')
        
        # Always cache high priority content
        if priority in ['critical', 'high']:
            return True
        
        # Don't cache very large items unless critical
        if size_bytes > 10 * 1024 * 1024:  # > 10MB
            return priority == 'critical'
        
        # Content-specific rules
        if content_type in ['user_preferences', 'session_data', 'authentication']:
            return True
        
        if content_type in ['temporary_upload', 'one_time_token']:
            return False
        
        # Use pattern analysis for decision
        if key in self.access_patterns:
            pattern = self.access_patterns[key]
            
            # Cache if frequently accessed
            if pattern.total_accesses > 5:
                return True
            
            # Cache if accessed by multiple users
            if len(pattern.user_diversity) > 3:
                return True
        
        return True  # Default to caching
    
    async def select_eviction_candidates(
        self,
        cache_entries: Dict[str, Any], 
        required_space: int,
        current_usage: int,
        max_capacity: int
    ) -> List[EvictionCandidate]:
        """Advanced eviction selection using composite scoring"""        candidates = []
        
        for key, entry in cache_entries.items():
            score = await self._calculate_eviction_score(key, entry)
            
            candidates.append(EvictionCandidate(
                key=key,
                score=score,
                reason=self._determine_eviction_reason(key, entry, score),
                size_bytes=entry.size_bytes,
                last_accessed=entry.last_accessed,
                metadata={
                    'access_count': entry.access_count,
                    'hit_count': entry.hit_count,
                    'priority': entry.priority.value if entry.priority else 'normal'
                }
            ))
        
        # Sort by eviction score (highest score = best candidate for eviction)
        candidates.sort(key=lambda x: x.score, reverse=True)
        
        return candidates
    
    async def update_access_pattern(self, key: str, access_info: Dict[str, Any]):
        """Update comprehensive access patterns"""        await self.lru_strategy.update_access_pattern(key, access_info)
        await self.ttl_strategy.update_access_pattern(key, access_info)
        
        self.record_access(
            key,
            access_info.get('user_id'),
            access_info.get('location')
        )
    
    async def _calculate_eviction_score(self, key: str, entry: Any) -> float:
        """Calculate composite eviction score"""        score = 0.0
        
        # Access frequency component (inverse - less frequent = higher eviction score)
        frequency_score = 1.0 / max(entry.access_count, 1)
        score += frequency_score * self.strategy_weights['access_frequency']
        
        # Recency component (older = higher eviction score)
        time_since_access = (datetime.utcnow() - entry.last_accessed).total_seconds()
        recency_score = min(time_since_access / 86400, 1.0)  # Normalize to days
        score += recency_score * self.strategy_weights['recency']
        
        # Content importance (lower priority = higher eviction score)
        importance_score = {
            'critical': 0.0,
            'high': 0.2,
            'normal': 0.5,
            'low': 0.8,
            'minimal': 1.0
        }.get(entry.priority.value if entry.priority else 'normal', 0.5)
        score += importance_score * self.strategy_weights['content_importance']
        
        # User diversity component (less diverse = higher eviction score)
        if key in self.access_patterns:
            pattern = self.access_patterns[key]
            diversity_score = 1.0 / max(len(pattern.user_diversity), 1)
            score += diversity_score * self.strategy_weights['user_diversity']
            
            # Geographic spread component
            geo_score = 1.0 / max(len(pattern.geographic_distribution), 1)
            score += geo_score * self.strategy_weights['geographic_spread']
        
        return score
    
    def _determine_eviction_reason(self, key: str, entry: Any, score: float) -> EvictionReason:
        """Determine primary reason for eviction"""        if entry.ttl and (datetime.utcnow() - entry.created_at).total_seconds() >= entry.ttl:
            return EvictionReason.TTL_EXPIRED
        
        if entry.access_count < 2:
            return EvictionReason.LRU_EVICTION
        
        if entry.priority and entry.priority.value in ['minimal', 'low']:
            return EvictionReason.PRIORITY_BASED
        
        return EvictionReason.LRU_EVICTION

class GeographicStrategy(CacheStrategy):
    """Geographic locality-aware caching strategy"""    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__(config)
        self.regional_preferences: Dict[str, Set[str]] = defaultdict(set)
        self.location_access_counts: Dict[Tuple[str, str], int] = defaultdict(int)
    
    async def should_cache(self, key: str, value: Any, metadata: Dict[str, Any]) -> bool:
        """Cache based on geographic relevance"""        user_location = metadata.get('user_location')
        content_regions = metadata.get('relevant_regions', [])
        
        if not user_location:
            return True  # Default to caching if no location info
        
        # Always cache globally relevant content
        if 'global' in content_regions:
            return True
        
        # Cache if content is relevant to user's region
        if user_location in content_regions:
            return True
        
        # Check if this content is frequently accessed from this location
        location_key = (key, user_location)
        if self.location_access_counts[location_key] > 5:
            return True
        
        return False
    
    async def select_eviction_candidates(
        self,
        cache_entries: Dict[str, Any],
        required_space: int,
        current_usage: int,
        max_capacity: int
    ) -> List[EvictionCandidate]:
        """Select entries with poor geographic relevance"""        candidates = []
        
        for key, entry in cache_entries.items():
            if key not in self.access_patterns:
                continue
                
            pattern = self.access_patterns[key]
            
            # Calculate geographic diversity score
            geo_diversity = len(pattern.geographic_distribution)
            if geo_diversity == 0:
                geo_score = 1.0  # No geographic data = candidate for eviction
            else:
                # More diverse = less likely to evict
                geo_score = 1.0 / geo_diversity
            
            candidates.append(EvictionCandidate(
                key=key,
                score=geo_score,
                reason=EvictionReason.GEOGRAPHIC_LOCALITY,
                size_bytes=entry.size_bytes,
                last_accessed=entry.last_accessed,
                metadata={
                    'geographic_diversity': geo_diversity,
                    'regions': list(pattern.geographic_distribution.keys())
                }
            ))
        
        candidates.sort(key=lambda x: x.score, reverse=True)
        return candidates
    
    async def update_access_pattern(self, key: str, access_info: Dict[str, Any]):
        """Update geographic access patterns"""        self.record_access(
            key,
            access_info.get('user_id'),
            access_info.get('location')
        )
        
        location = access_info.get('location')
        if location:
            location_key = (key, location)
            self.location_access_counts[location_key] += 1
            
            # Update regional preferences
            self.regional_preferences[location].add(key)

class ContentAwareStrategy(CacheStrategy):
    """Content-type aware caching with specialized handling"""    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__(config)
        
        # Content-specific TTL and priority rules
        self.content_rules = {
            'audio_fingerprint': {'ttl': 86400, 'priority': 'high'},  # 24 hours
            'video_thumbnail': {'ttl': 21600, 'priority': 'normal'},  # 6 hours
            'user_session': {'ttl': 3600, 'priority': 'high'},  # 1 hour
            'analytics_data': {'ttl': 43200, 'priority': 'normal'},  # 12 hours
            'ml_model_cache': {'ttl': 604800, 'priority': 'critical'},  # 7 days
            'temporary_upload': {'ttl': 1800, 'priority': 'low'},  # 30 minutes
            'collaboration_data': {'ttl': 7200, 'priority': 'high'},  # 2 hours
            'seo_metadata': {'ttl': 86400, 'priority': 'normal'},  # 24 hours
            'payment_session': {'ttl': 900, 'priority': 'critical'},  # 15 minutes
            'content_protection': {'ttl': 172800, 'priority': 'critical'}  # 48 hours
        }
    
    async def should_cache(self, key: str, value: Any, metadata: Dict[str, Any]) -> bool:
        """Content-aware caching decisions"""        content_type = metadata.get('content_type')
        
        if not content_type:
            return True
        
        # Check content-specific rules
        if content_type in self.content_rules:
            rules = self.content_rules[content_type]
            
            # Don't cache critical data with very short TTL unless specifically requested
            if rules['priority'] == 'critical' and rules['ttl'] < 300:
                return metadata.get('force_cache', False)
        
        # Special handling for different content types
        if content_type.startswith('real_time_'):
            return False  # Don't cache real-time data
        
        if content_type.endswith('_backup'):
            return True  # Always cache backup data
        
        return True
    
    async def select_eviction_candidates(
        self,
        cache_entries: Dict[str, Any],
        required_space: int, 
        current_usage: int,
        max_capacity: int
    ) -> List[EvictionCandidate]:
        """Content-aware eviction selection"""        candidates = []
        
        for key, entry in cache_entries.items():
            content_type = entry.content_type or 'unknown'
            
            # Get content-specific rules
            rules = self.content_rules.get(content_type, {'priority': 'normal'})
            
            # Calculate content-aware eviction score
            priority_scores = {
                'critical': 0.1,
                'high': 0.3,
                'normal': 0.5,
                'low': 0.8,
                'minimal': 1.0
            }
            
            base_score = priority_scores.get(rules['priority'], 0.5)
            
            # Adjust score based on content freshness
            if entry.ttl:
                age_ratio = (datetime.utcnow() - entry.created_at).total_seconds() / entry.ttl
                freshness_score = min(age_ratio, 1.0)
                score = base_score * (0.5 + 0.5 * freshness_score)
            else:
                score = base_score
            
            candidates.append(EvictionCandidate(
                key=key,
                score=score,
                reason=EvictionReason.CONTENT_FRESHNESS,
                size_bytes=entry.size_bytes,
                last_accessed=entry.last_accessed,
                metadata={
                    'content_type': content_type,
                    'content_priority': rules['priority']
                }
            ))
        
        candidates.sort(key=lambda x: x.score, reverse=True)
        return candidates
    
    async def update_access_pattern(self, key: str, access_info: Dict[str, Any]):
        """Update content-aware access patterns"""        self.record_access(
            key,
            access_info.get('user_id'), 
            access_info.get('location')
        )
        
        content_type = access_info.get('content_type')
        if content_type and content_type not in self.content_rules:
            # Learn new content type patterns
            await self._analyze_new_content_type(content_type, access_info)
    
    async def _analyze_new_content_type(self, content_type: str, access_info: Dict[str, Any]):
        """Analyze and create rules for new content types"""        # This would implement ML-based content type analysis
        # For now, use heuristics based on content type name
        
        if 'critical' in content_type or 'security' in content_type:
            self.content_rules[content_type] = {'ttl': 3600, 'priority': 'critical'}
        elif 'temp' in content_type or 'temporary' in content_type:
            self.content_rules[content_type] = {'ttl': 1800, 'priority': 'low'}
        elif 'user' in content_type or 'session' in content_type:
            self.content_rules[content_type] = {'ttl': 3600, 'priority': 'high'}
        else:
            self.content_rules[content_type] = {'ttl': 7200, 'priority': 'normal'}
            
        logger.info(f"Created new content type rule for '{content_type}': {self.content_rules[content_type]}")
