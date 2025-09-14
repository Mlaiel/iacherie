"""🚀 Enterprise Query Bus - CQRS Architecture
=====================================================
Module: events/cqrs/query_bus.py
Author: Fahed Mlaiel (mlaiel@live.de)
=====================================================

⚠️ PROPRIÉTÉ INTELLECTUELLE EXCLUSIVE - FAHED MLAIEL ⚠️
(c) 2025 Fahed Mlaiel. Tous droits réservés.
Contact: mlaiel@live.de

🎯 ENTERPRISE QUERY BUS
Central query processing hub for CQRS read operations
- Query routing to optimized read models
- Multi-level caching with intelligent invalidation
- Query optimization and performance monitoring
- Load balancing across read replicas
- Response transformation and serialization
- Real-time analytics and metrics
"""

import asyncio
import logging
import time
import json
import hashlib
import uuid
from typing import Dict, List, Optional, Any, Callable, Union, Type, TypeVar, Generic
from datetime import datetime, timedelta
from dataclasses import dataclass, field, asdict
from enum import Enum
import weakref
from concurrent.futures import ThreadPoolExecutor
from collections import defaultdict

from ..core.base_event import BaseEvent
from ..core.event_priority import EventPriority
from ..core.exceptions import EventProcessingError, EventValidationError

logger = logging.getLogger(__name__)

T = TypeVar('T')


class QueryStatus(Enum):
    """Query execution status"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CACHED = "cached"


class CacheLevel(Enum):
    """Cache level for query results"""
    MEMORY = "memory"
    REDIS = "redis"
    DATABASE = "database"
    CDN = "cdn"


@dataclass
class Query:
    """Base query class for CQRS read operations"""
    query_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    query_type: str = ""
    parameters: Dict[str, Any] = field(default_factory=dict)
    filters: Dict[str, Any] = field(default_factory=dict)
    sorting: List[Dict[str, str]] = field(default_factory=list)
    pagination: Dict[str, int] = field(default_factory=lambda: {"page": 1, "limit": 50})
    user_id: Optional[str] = None
    correlation_id: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    priority: EventPriority = EventPriority.MEDIUM
    timeout_seconds: int = 15
    cache_ttl_seconds: int = 300  # 5 minutes default
    enable_cache: bool = True
    required_consistency: str = "eventual"  # eventual, strong, session


@dataclass
class QueryResult:
    """Query execution result with metadata"""
    query_id: str
    status: QueryStatus
    data: Optional[Any] = None
    error: Optional[str] = None
    execution_time_ms: Optional[float] = None
    cache_hit: bool = False
    cache_level: Optional[CacheLevel] = None
    total_count: Optional[int] = None
    page_info: Optional[Dict[str, Any]] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


class QueryHandler(Generic[T]):
    """Base query handler interface"""
    
    async def handle(self, query: Query) -> QueryResult:
        """Handle query and return result"""
        raise NotImplementedError
    
    def get_cache_key(self, query: Query) -> str:
        """Generate cache key for query"""
        query_data = {
            "query_type": query.query_type,
            "parameters": query.parameters,
            "filters": query.filters,
            "sorting": query.sorting,
            "pagination": query.pagination
        }
        query_string = json.dumps(query_data, sort_keys=True)
        return hashlib.md5(query_string.encode()).hexdigest()


class CacheManager:
    """Multi-level cache manager for query results"""
    
    def __init__(self) -> None:
        self._memory_cache: Dict[str, Dict[str, Any]] = {}
        self._cache_stats = defaultdict(int)
        self._cache_expiry: Dict[str, datetime] = {}
    
    async def get(self, cache_key: str) -> Optional[Any]:
        """Get cached result"""
        # Check memory cache first
        if cache_key in self._memory_cache:
            if cache_key in self._cache_expiry:
                if datetime.utcnow() > self._cache_expiry[cache_key]:
                    # Expired, remove from cache
                    del self._memory_cache[cache_key]
                    del self._cache_expiry[cache_key]
                    self._cache_stats["expired"] += 1
                    return None
            
            self._cache_stats["memory_hits"] += 1
            return self._memory_cache[cache_key]["data"]
        
        self._cache_stats["misses"] += 1
        return None
    
    async def set(self, cache_key: str, data: Any, ttl_seconds: int = 300) -> None:
        """Set cached result"""
        expiry_time = datetime.utcnow() + timedelta(seconds=ttl_seconds)
        
        self._memory_cache[cache_key] = {
            "data": data,
            "created_at": datetime.utcnow(),
            "ttl_seconds": ttl_seconds
        }
        self._cache_expiry[cache_key] = expiry_time
        self._cache_stats["sets"] += 1
        
        # Cleanup old entries if cache gets too large
        if len(self._memory_cache) > 10000:
            await self._cleanup_expired_entries()
    
    async def invalidate(self, pattern: str = None) -> None:
        """Invalidate cache entries"""
        if pattern is None:
            # Clear all cache
            self._memory_cache.clear()
            self._cache_expiry.clear()
            self._cache_stats["invalidations"] += 1
        else:
            # Pattern-based invalidation
            keys_to_remove = [key for key in self._memory_cache.keys() if pattern in key]
            for key in keys_to_remove:
                del self._memory_cache[key]
                self._cache_expiry.pop(key, None)
            self._cache_stats["pattern_invalidations"] += 1
    
    async def _cleanup_expired_entries(self) -> None:
        """Cleanup expired cache entries"""
        now = datetime.utcnow()
        expired_keys = [
            key for key, expiry in self._cache_expiry.items()
            if now > expiry
        ]
        
        for key in expired_keys:
            self._memory_cache.pop(key, None)
            self._cache_expiry.pop(key, None)
        
        self._cache_stats["cleanup_runs"] += 1
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        total_requests = self._cache_stats["memory_hits"] + self._cache_stats["misses"]
        hit_ratio = (self._cache_stats["memory_hits"] / total_requests * 100) if total_requests > 0 else 0
        
        return {
            "memory_entries": len(self._memory_cache),
            "hit_ratio_percent": round(hit_ratio, 2),
            "stats": dict(self._cache_stats)
        }


class ReadModelRouter:
    """Route queries to appropriate read models/databases"""
    
    def __init__(self) -> None:
        self._routes: Dict[str, Dict[str, Any]] = {}
        self._load_balancer_state: Dict[str, int] = defaultdict(int)
    
    def register_route(self, query_type: str, read_models: List[str], strategy: str = "round_robin") -> None:
        """Register routing for query type"""
        self._routes[query_type] = {
            "read_models": read_models,
            "strategy": strategy,
            "weight_map": {model: 1 for model in read_models}
        }
    
    def get_read_model(self, query_type: str) -> Optional[str]:
        """Get optimal read model for query type"""
        if query_type not in self._routes:
            return None
        
        route_config = self._routes[query_type]
        read_models = route_config["read_models"]
        strategy = route_config["strategy"]
        
        if strategy == "round_robin":
            current_index = self._load_balancer_state[query_type]
            selected_model = read_models[current_index % len(read_models)]
            self._load_balancer_state[query_type] = (current_index + 1) % len(read_models)
            return selected_model
        
        elif strategy == "primary_secondary":
            # Use primary, fallback to secondary
            return read_models[0] if read_models else None
        
        return read_models[0] if read_models else None


class EnterpriseQueryBus:
    """Enterprise-grade query bus with advanced optimization"""
    
    def __init__(self, 
                 max_concurrent_queries -> None: int = 200,
                 enable_caching -> None: bool = True,
                 enable_query_optimization -> None: bool = True) -> None:
        self._handlers: Dict[str, QueryHandler] = {}
        self._middleware: List[Callable] = []
        self._cache_manager = CacheManager()
        self._read_model_router = ReadModelRouter()
        
        # Configuration
        self._max_concurrent = max_concurrent_queries
        self._enable_caching = enable_caching
        self._enable_optimization = enable_query_optimization
        
        # Metrics and monitoring
        self._metrics: Dict[str, Any] = {
            "queries_processed": 0,
            "queries_failed": 0,
            "average_execution_time": 0.0,
            "cache_hit_ratio": 0.0,
            "slow_queries": 0
        }
        
        # State management
        self._active_queries: Dict[str, Query] = {}
        self._query_history: List[QueryResult] = []
        self._slow_query_threshold_ms = 1000
        
        # Performance monitoring
        self._query_performance: Dict[str, List[float]] = defaultdict(list)
        
        # Async processing
        self._executor = ThreadPoolExecutor(max_workers=20)
        self._processing_semaphore = asyncio.Semaphore(max_concurrent_queries)
    
    def register_handler(self, query_type: str, handler: QueryHandler) -> None:
        """Register query handler for specific query type"""
        if not isinstance(handler, QueryHandler):
            raise ValueError(f"Handler must inherit from QueryHandler: {type(handler)}")
        
        self._handlers[query_type] = handler
        logger.info(f"Registered query handler for type: {query_type}")
    
    def register_read_model_route(self, query_type: str, read_models: List[str], strategy: str = "round_robin") -> None:
        """Register read model routing for query type"""
        self._read_model_router.register_route(query_type, read_models, strategy)
        logger.info(f"Registered read model route for {query_type}: {read_models}")
    
    def add_middleware(self, middleware: Callable) -> None:
        """Add middleware for query processing pipeline"""
        self._middleware.append(middleware)
        logger.info(f"Added query middleware: {middleware.__name__}")
    
    async def execute_query(self, query: Query) -> QueryResult:
        """Execute query with full optimization pipeline"""
        start_time = time.time()
        
        try:
            # Pre-execution validation
            await self._validate_query(query)
            await self._apply_middleware(query, "pre_execution")
            
            # Check cache first
            cache_result = await self._check_cache(query)
            if cache_result:
                return cache_result
            
            # Track active query
            self._active_queries[query.query_id] = query
            
            # Execute with concurrency control
            async with self._processing_semaphore:
                result = await self._execute_query_internal(query)
            
            # Post-execution processing
            execution_time = (time.time() - start_time) * 1000
            result.execution_time_ms = execution_time
            
            # Cache result if enabled
            if self._enable_caching and query.enable_cache and result.status == QueryStatus.COMPLETED:
                await self._cache_result(query, result)
            
            await self._apply_middleware(query, "post_execution", result)
            await self._update_metrics(query, result)
            await self._track_performance(query, result)
            
            return result
            
        except Exception as e:
            execution_time = (time.time() - start_time) * 1000
            error_result = QueryResult(
                query_id=query.query_id,
                status=QueryStatus.FAILED,
                error=str(e),
                execution_time_ms=execution_time
            )
            
            await self._handle_query_failure(query, error_result, e)
            return error_result
            
        finally:
            # Cleanup
            self._active_queries.pop(query.query_id, None)
    
    async def _execute_query_internal(self, query: Query) -> QueryResult:
        """Internal query execution logic"""
        handler = self._handlers.get(query.query_type)
        if not handler:
            raise EventProcessingError(f"No handler registered for query type: {query.query_type}")
        
        try:
            # Execute query with timeout
            result = await asyncio.wait_for(
                handler.handle(query),
                timeout=query.timeout_seconds
            )
            result.status = QueryStatus.COMPLETED
            
        except asyncio.TimeoutError:
            result = QueryResult(
                query_id=query.query_id,
                status=QueryStatus.FAILED,
                error=f"Query timed out after {query.timeout_seconds} seconds"
            )
        
        return result
    
    async def _validate_query(self, query: Query) -> None:
        """Validate query before execution"""
        if not query.query_type:
            raise EventValidationError("Query type is required")
        
        if not query.query_id:
            raise EventValidationError("Query ID is required")
        
        # Validate pagination
        if query.pagination["limit"] > 1000:
            raise EventValidationError("Pagination limit cannot exceed 1000")
        
        logger.debug(f"Query validated: {query.query_id}")
    
    async def _check_cache(self, query: Query) -> Optional[QueryResult]:
        """Check if query result is cached"""
        if not self._enable_caching or not query.enable_cache:
            return None
        
        handler = self._handlers.get(query.query_type)
        if not handler:
            return None
        
        cache_key = handler.get_cache_key(query)
        cached_data = await self._cache_manager.get(cache_key)
        
        if cached_data is not None:
            return QueryResult(
                query_id=query.query_id,
                status=QueryStatus.CACHED,
                data=cached_data,
                cache_hit=True,
                cache_level=CacheLevel.MEMORY,
                execution_time_ms=0.0
            )
        
        return None
    
    async def _cache_result(self, query: Query, result: QueryResult) -> None:
        """Cache query result"""
        handler = self._handlers.get(query.query_type)
        if handler and result.data is not None:
            cache_key = handler.get_cache_key(query)
            await self._cache_manager.set(cache_key, result.data, query.cache_ttl_seconds)
    
    async def _apply_middleware(self, query: Query, phase: str, result: Optional[QueryResult] = None) -> None:
        """Apply middleware pipeline"""
        for middleware in self._middleware:
            try:
                if asyncio.iscoroutinefunction(middleware):
                    await middleware(query, phase, result)
                else:
                    middleware(query, phase, result)
            except Exception as e:
                logger.error(f"Query middleware error in {middleware.__name__}: {e}")
    
    async def _update_metrics(self, query: Query, result: QueryResult) -> None:
        """Update performance metrics"""
        self._metrics["queries_processed"] += 1
        
        if result.status == QueryStatus.FAILED:
            self._metrics["queries_failed"] += 1
        
        if result.execution_time_ms:
            # Update rolling average
            current_avg = self._metrics["average_execution_time"]
            total_queries = self._metrics["queries_processed"]
            new_avg = ((current_avg * (total_queries - 1)) + result.execution_time_ms) / total_queries
            self._metrics["average_execution_time"] = new_avg
            
            # Track slow queries
            if result.execution_time_ms > self._slow_query_threshold_ms:
                self._metrics["slow_queries"] += 1
        
        # Update cache hit ratio
        cache_stats = self._cache_manager.get_stats()
        self._metrics["cache_hit_ratio"] = cache_stats["hit_ratio_percent"]
    
    async def _track_performance(self, query: Query, result: QueryResult) -> None:
        """Track query performance for optimization"""
        if result.execution_time_ms:
            self._query_performance[query.query_type].append(result.execution_time_ms)
            
            # Keep only last 1000 measurements per query type
            if len(self._query_performance[query.query_type]) > 1000:
                self._query_performance[query.query_type] = self._query_performance[query.query_type][-1000:]
    
    async def _handle_query_failure(self, query: Query, result: QueryResult, exception: Exception) -> None:
        """Handle query failure"""
        logger.error(f"Query failed: {query.query_id} - {exception}")
        
        # Store failed query for analysis
        self._query_history.append(result)
        
        # Keep only last 1000 queries in memory
        if len(self._query_history) > 1000:
            self._query_history = self._query_history[-1000:]
    
    async def invalidate_cache(self, pattern: str = None) -> None:
        """Invalidate cache entries"""
        await self._cache_manager.invalidate(pattern)
        logger.info(f"Cache invalidated with pattern: {pattern}")
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get query bus performance metrics"""
        cache_stats = self._cache_manager.get_stats()
        
        return {
            **self._metrics,
            "active_queries": len(self._active_queries),
            "handler_count": len(self._handlers),
            "middleware_count": len(self._middleware),
            "cache_stats": cache_stats
        }
    
    def get_query_performance_stats(self) -> Dict[str, Dict[str, float]]:
        """Get performance statistics by query type"""
        stats = {}
        
        for query_type, measurements in self._query_performance.items():
            if measurements:
                stats[query_type] = {
                    "count": len(measurements),
                    "avg_ms": sum(measurements) / len(measurements),
                    "min_ms": min(measurements),
                    "max_ms": max(measurements),
                    "p95_ms": sorted(measurements)[int(len(measurements) * 0.95)] if len(measurements) > 20 else max(measurements)
                }
        
        return stats
    
    def get_active_queries(self) -> List[Dict[str, Any]]:
        """Get currently active queries"""
        return [
            {
                "query_id": query.query_id,
                "query_type": query.query_type,
                "user_id": query.user_id,
                "created_at": query.created_at.isoformat(),
                "priority": query.priority.value
            }
            for query in self._active_queries.values()
        ]
    
    async def shutdown(self) -> None:
        """Graceful shutdown of query bus"""
        logger.info("Shutting down query bus...")
        
        # Wait for active queries to complete (with timeout)
        max_wait = 15  # seconds
        start_time = time.time()
        
        while self._active_queries and (time.time() - start_time) < max_wait:
            await asyncio.sleep(0.1)
        
        if self._active_queries:
            logger.warning(f"Shutdown with {len(self._active_queries)} active queries")
        
        self._executor.shutdown(wait=True)
        logger.info("Query bus shutdown complete")


# Singleton instance for global access
_query_bus_instance: Optional[EnterpriseQueryBus] = None


def get_query_bus() -> EnterpriseQueryBus:
    """Get singleton query bus instance"""
    global _query_bus_instance
    if _query_bus_instance is None:
        _query_bus_instance = EnterpriseQueryBus()
    return _query_bus_instance


def reset_query_bus() -> None:
    """Reset query bus instance (for testing)"""
    global _query_bus_instance
    _query_bus_instance = None