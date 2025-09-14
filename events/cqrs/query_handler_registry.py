"""🚀 Enterprise Query Handler Registry - CQRS Architecture
========================================================
Module: events/cqrs/query_handler_registry.py
Author: Fahed Mlaiel (mlaiel@live.de)
========================================================

⚠️ PROPRIÉTÉ INTELLECTUELLE EXCLUSIVE - FAHED MLAIEL ⚠️
(c) 2025 Fahed Mlaiel. Tous droits réservés.
Contact: mlaiel@live.de

🎯 ENTERPRISE QUERY HANDLER REGISTRY
Advanced query handler management with caching and optimization
- Dynamic query handler registration and versioning
- Intelligent caching strategies per handler
- Query optimization and performance monitoring
- Read model synchronization and consistency management
- Auto-scaling and load balancing
- Real-time performance analytics and adaptation
"""

import asyncio
import logging
import inspect
import time
import uuid
import hashlib
import json
from typing import Dict, List, Optional, Any, Callable, Union, Type, TypeVar, get_type_hints
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
import weakref
from concurrent.futures import ThreadPoolExecutor
from collections import defaultdict, deque
import importlib

from .query_bus import Query, QueryResult, QueryStatus, QueryHandler, CacheLevel
from ..core.base_event import BaseEvent
from ..core.event_priority import EventPriority
from ..core.exceptions import EventProcessingError, EventValidationError

logger = logging.getLogger(__name__)

T = TypeVar('T')


class QueryHandlerState(Enum):
    """Query handler lifecycle states"""
    REGISTERED = "registered"
    INITIALIZING = "initializing"
    ACTIVE = "active"
    DEGRADED = "degraded"
    CACHE_WARMING = "cache_warming"
    DISABLED = "disabled"
    UNREGISTERED = "unregistered"


class CacheStrategy(Enum):
    """Cache strategies for query handlers"""
    NO_CACHE = "no_cache"
    TIME_BASED = "time_based"
    INVALIDATION_BASED = "invalidation_based"
    ADAPTIVE = "adaptive"
    AGGRESSIVE = "aggressive"
    LAZY = "lazy"


@dataclass
class QueryHandlerMetadata:
    """Metadata for query handlers"""
    handler_id: str
    query_type: str
    handler_class: Type[QueryHandler]
    version: str = "1.0.0"
    description: str = ""
    tags: List[str] = field(default_factory=list)
    read_models: List[str] = field(default_factory=list)
    cache_strategy: CacheStrategy = CacheStrategy.TIME_BASED
    cache_ttl_seconds: int = 300
    cache_max_size: int = 1000
    performance_sla_ms: int = 1000
    consistency_level: str = "eventual"
    supports_pagination: bool = True
    supports_filtering: bool = True
    supports_sorting: bool = True
    geographic_regions: List[str] = field(default_factory=list)
    resource_requirements: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class QueryHandlerInstance:
    """Query handler instance with runtime state and metrics"""
    metadata: QueryHandlerMetadata
    instance: QueryHandler
    state: QueryHandlerState = QueryHandlerState.REGISTERED
    created_at: datetime = field(default_factory=datetime.utcnow)
    last_health_check: datetime = field(default_factory=datetime.utcnow)
    total_queries: int = 0
    successful_queries: int = 0
    failed_queries: int = 0
    cache_hits: int = 0
    cache_misses: int = 0
    average_response_time: float = 0.0
    p95_response_time: float = 0.0
    last_error: Optional[str] = None
    last_error_time: Optional[datetime] = None
    performance_history: deque = field(default_factory=lambda: deque(maxlen=1000))
    cache_performance: Dict[str, Any] = field(default_factory=dict)
    read_model_sync_status: Dict[str, datetime] = field(default_factory=dict)


class QueryCacheManager:
    """Advanced cache management for query handlers"""
    
    def __init__(self) -> None:
        self._cache_stores: Dict[str, Dict[str, Any]] = defaultdict(dict)
        self._cache_metadata: Dict[str, Dict[str, Any]] = defaultdict(dict)
        self._invalidation_patterns: Dict[str, List[str]] = defaultdict(list)
        self._cache_stats = defaultdict(lambda: {"hits": 0, "misses": 0, "invalidations": 0})
    
    async def get(self, handler_id: str, cache_key: str) -> Optional[Any]:
        """Get cached query result"""
        cache_store = self._cache_stores[handler_id]
        
        if cache_key in cache_store:
            cache_entry = cache_store[cache_key]
            
            # Check TTL
            if cache_entry["expires_at"] > datetime.utcnow():
                self._cache_stats[handler_id]["hits"] += 1
                return cache_entry["data"]
            else:
                # Expired, remove
                del cache_store[cache_key]
                self._cache_metadata[handler_id].pop(cache_key, None)
        
        self._cache_stats[handler_id]["misses"] += 1
        return None
    
    async def set(self, handler_id: str, cache_key: str, data: Any, 
                 ttl_seconds: int = 300, metadata: Dict[str, Any] = None) -> None:
        """Set cached query result"""
        cache_store = self._cache_stores[handler_id]
        expires_at = datetime.utcnow() + timedelta(seconds=ttl_seconds)
        
        cache_store[cache_key] = {
            "data": data,
            "created_at": datetime.utcnow(),
            "expires_at": expires_at,
            "access_count": 0,
            "last_accessed": datetime.utcnow()
        }
        
        if metadata:
            self._cache_metadata[handler_id][cache_key] = metadata
        
        # Cleanup if cache is too large
        await self._cleanup_cache_if_needed(handler_id)
    
    async def invalidate(self, handler_id: str, pattern: str = None) -> int:
        """Invalidate cache entries"""
        cache_store = self._cache_stores[handler_id]
        invalidated_count = 0
        
        if pattern is None:
            # Clear all cache for handler
            invalidated_count = len(cache_store)
            cache_store.clear()
            self._cache_metadata[handler_id].clear()
        else:
            # Pattern-based invalidation
            keys_to_remove = [key for key in cache_store.keys() if pattern in key]
            for key in keys_to_remove:
                cache_store.pop(key, None)
                self._cache_metadata[handler_id].pop(key, None)
                invalidated_count += 1
        
        self._cache_stats[handler_id]["invalidations"] += invalidated_count
        return invalidated_count
    
    async def _cleanup_cache_if_needed(self, handler_id: str, max_size: int = 1000) -> None:
        """Cleanup cache if it exceeds max size"""
        cache_store = self._cache_stores[handler_id]
        
        if len(cache_store) > max_size:
            # Remove oldest entries
            sorted_entries = sorted(
                cache_store.items(), 
                key=lambda x: x[1]["last_accessed"]
            )
            
            entries_to_remove = len(cache_store) - max_size
            for i in range(entries_to_remove):
                key = sorted_entries[i][0]
                cache_store.pop(key, None)
                self._cache_metadata[handler_id].pop(key, None)
    
    def get_cache_stats(self, handler_id: str) -> Dict[str, Any]:
        """Get cache statistics for handler"""
        stats = dict(self._cache_stats[handler_id])
        cache_store = self._cache_stores[handler_id]
        
        total_requests = stats["hits"] + stats["misses"]
        hit_ratio = (stats["hits"] / total_requests * 100) if total_requests > 0 else 0
        
        return {
            **stats,
            "cache_size": len(cache_store),
            "hit_ratio_percent": round(hit_ratio, 2)
        }
    
    def register_invalidation_pattern(self, handler_id: str, event_type: str, pattern: str) -> None:
        """Register cache invalidation pattern for event type"""
        self._invalidation_patterns[f"{handler_id}:{event_type}"].append(pattern)
    
    async def handle_invalidation_event(self, event: BaseEvent) -> None:
        """Handle event that may trigger cache invalidation"""
        for pattern_key, patterns in self._invalidation_patterns.items():
            if f":{event.event_type}" in pattern_key:
                handler_id = pattern_key.split(":")[0]
                for pattern in patterns:
                    await self.invalidate(handler_id, pattern)


class ReadModelSyncManager:
    """Manage read model synchronization for query handlers"""
    
    def __init__(self) -> None:
        self._sync_status: Dict[str, Dict[str, Any]] = defaultdict(dict)
        self._sync_strategies: Dict[str, Callable] = {}
    
    def register_sync_strategy(self, read_model_type: str, strategy: Callable) -> None:
        """Register synchronization strategy for read model type"""
        self._sync_strategies[read_model_type] = strategy
    
    async def sync_read_model(self, handler_id: str, read_model_type: str) -> bool:
        """Synchronize read model for handler"""
        if read_model_type not in self._sync_strategies:
            logger.warning(f"No sync strategy for read model type: {read_model_type}")
            return False
        
        try:
            strategy = self._sync_strategies[read_model_type]
            await strategy(handler_id, read_model_type)
            
            self._sync_status[handler_id][read_model_type] = {
                "last_sync": datetime.utcnow(),
                "status": "synchronized",
                "error": None
            }
            
            return True
            
        except Exception as e:
            logger.error(f"Read model sync failed for {handler_id}:{read_model_type} - {e}")
            
            self._sync_status[handler_id][read_model_type] = {
                "last_sync": datetime.utcnow(),
                "status": "failed",
                "error": str(e)
            }
            
            return False
    
    def get_sync_status(self, handler_id: str) -> Dict[str, Any]:
        """Get synchronization status for handler"""
        return dict(self._sync_status[handler_id])


class PerformanceOptimizer:
    """Optimize query handler performance"""
    
    def __init__(self) -> None:
        self._optimization_rules: List[Callable] = []
        self._performance_profiles: Dict[str, Dict[str, Any]] = defaultdict(dict)
    
    def add_optimization_rule(self, rule: Callable[[Query, QueryHandlerInstance], Query]) -> None:
        """Add query optimization rule"""
        self._optimization_rules.append(rule)
    
    async def optimize_query(self, query: Query, handler_instance: QueryHandlerInstance) -> Query:
        """Optimize query based on handler performance profile"""
        optimized_query = query
        
        # Apply optimization rules
        for rule in self._optimization_rules:
            try:
                if asyncio.iscoroutinefunction(rule):
                    optimized_query = await rule(optimized_query, handler_instance)
                else:
                    optimized_query = rule(optimized_query, handler_instance)
            except Exception as e:
                logger.error(f"Query optimization rule failed: {e}")
        
        # Update performance profile
        await self._update_performance_profile(query, handler_instance)
        
        return optimized_query
    
    async def _update_performance_profile(self, query: Query, handler_instance: QueryHandlerInstance) -> None:
        """Update performance profile for query pattern"""
        profile_key = f"{query.query_type}:{handler_instance.metadata.handler_id}"
        
        profile = self._performance_profiles[profile_key]
        
        # Calculate query complexity
        complexity_score = self._calculate_query_complexity(query)
        profile["complexity_scores"] = profile.get("complexity_scores", [])
        profile["complexity_scores"].append(complexity_score)
        
        # Keep only recent scores
        if len(profile["complexity_scores"]) > 100:
            profile["complexity_scores"] = profile["complexity_scores"][-100:]
    
    def _calculate_query_complexity(self, query: Query) -> float:
        """Calculate query complexity score"""
        score = 1.0
        
        # Factor in filters
        score += len(query.filters) * 0.2
        
        # Factor in sorting
        score += len(query.sorting) * 0.3
        
        # Factor in pagination size
        limit = query.pagination.get("limit", 50)
        score += (limit / 100) * 0.5
        
        # Factor in parameter complexity
        param_complexity = sum(len(str(v)) for v in query.parameters.values()) / 1000
        score += param_complexity
        
        return score
    
    def get_optimization_recommendations(self, handler_id: str) -> List[str]:
        """Get optimization recommendations for handler"""
        recommendations = []
        
        # Analyze performance profiles
        handler_profiles = {
            k: v for k, v in self._performance_profiles.items()
            if handler_id in k
        }
        
        for profile_key, profile in handler_profiles.items():
            if "complexity_scores" in profile:
                avg_complexity = sum(profile["complexity_scores"]) / len(profile["complexity_scores"])
                
                if avg_complexity > 5.0:
                    recommendations.append(f"High query complexity detected for {profile_key} - consider query optimization")
        
        return recommendations


# Decorator for automatic query handler registration
def query_handler(query_type -> None: str, version -> None: str = "1.0.0", description -> None: str = "",
                 cache_strategy -> None: CacheStrategy = CacheStrategy.TIME_BASED,
                 cache_ttl_seconds -> None: int = 300, performance_sla_ms -> None: int = 1000,
                 read_models -> None: List[str] = None, consistency_level -> None: str = "eventual") -> None:
    """Decorator for automatic query handler registration"""
    
    def decorator(handler_class -> None: Type[QueryHandler]) -> None:
        # Store metadata in class
        handler_class._query_metadata = QueryHandlerMetadata(
            handler_id=f"{query_type}_handler_{version}",
            query_type=query_type,
            handler_class=handler_class,
            version=version,
            description=description,
            read_models=read_models or [],
            cache_strategy=cache_strategy,
            cache_ttl_seconds=cache_ttl_seconds,
            performance_sla_ms=performance_sla_ms,
            consistency_level=consistency_level
        )
        
        return handler_class
    
    return decorator


class EnterpriseQueryHandlerRegistry:
    """Enterprise query handler registry with advanced caching and optimization"""
    
    def __init__(self) -> None:
        self._handlers: Dict[str, QueryHandlerInstance] = {}
        self._query_type_mapping: Dict[str, List[str]] = defaultdict(list)
        self._cache_manager = QueryCacheManager()
        self._sync_manager = ReadModelSyncManager()
        self._performance_optimizer = PerformanceOptimizer()
        
        # Configuration
        self._auto_cache_warming = True
        self._health_check_enabled = True
        self._performance_monitoring_enabled = True
        self._auto_scaling_enabled = True
        
        # Metrics
        self._metrics = {
            "handlers_registered": 0,
            "handlers_active": 0,
            "total_queries": 0,
            "failed_queries": 0,
            "cache_hits": 0,
            "cache_misses": 0,
            "average_response_time": 0.0,
            "sla_violations": 0
        }
        
        # Background tasks
        self._health_check_task: Optional[asyncio.Task] = None
        self._cache_warming_task: Optional[asyncio.Task] = None
        
        # Start background tasks
        self._start_background_tasks()
    
    def register_handler(self, metadata: QueryHandlerMetadata, 
                        dependencies: Dict[str, Any] = None) -> str:
        """Register query handler with metadata"""
        # Validate handler class
        if not issubclass(metadata.handler_class, QueryHandler):
            raise EventValidationError(f"Handler must inherit from QueryHandler: {metadata.handler_class}")
        
        # Create handler instance
        try:
            handler_dependencies = dependencies or {}
            handler_instance_obj = metadata.handler_class(**handler_dependencies)
        except Exception as e:
            raise EventProcessingError(f"Failed to create handler instance: {e}")
        
        # Create handler registry entry
        handler_instance = QueryHandlerInstance(
            metadata=metadata,
            instance=handler_instance_obj,
            state=QueryHandlerState.INITIALIZING
        )
        
        # Initialize handler
        try:
            if hasattr(handler_instance_obj, "initialize"):
                if asyncio.iscoroutinefunction(handler_instance_obj.initialize):
                    asyncio.create_task(handler_instance_obj.initialize())
                else:
                    handler_instance_obj.initialize()
            
            handler_instance.state = QueryHandlerState.ACTIVE
            
        except Exception as e:
            logger.error(f"Handler initialization failed: {e}")
            handler_instance.state = QueryHandlerState.DEGRADED
        
        # Register handler
        self._handlers[metadata.handler_id] = handler_instance
        self._query_type_mapping[metadata.query_type].append(metadata.handler_id)
        
        # Setup cache invalidation patterns if defined
        if hasattr(handler_instance_obj, "get_cache_invalidation_patterns"):
            patterns = handler_instance_obj.get_cache_invalidation_patterns()
            for event_type, pattern in patterns.items():
                self._cache_manager.register_invalidation_pattern(
                    metadata.handler_id, event_type, pattern
                )
        
        self._metrics["handlers_registered"] += 1
        if handler_instance.state == QueryHandlerState.ACTIVE:
            self._metrics["handlers_active"] += 1
        
        logger.info(f"Registered query handler: {metadata.handler_id} for type {metadata.query_type}")
        
        # Start cache warming if enabled
        if self._auto_cache_warming and metadata.cache_strategy != CacheStrategy.NO_CACHE:
            asyncio.create_task(self._warm_cache_for_handler(handler_instance))
        
        return metadata.handler_id
    
    def get_handler(self, query_type: str, version: str = None) -> Optional[QueryHandlerInstance]:
        """Get handler for query type"""
        handler_ids = self._query_type_mapping.get(query_type, [])
        
        if not handler_ids:
            return None
        
        # Filter by version if specified
        if version:
            for handler_id in handler_ids:
                handler = self._handlers[handler_id]
                if (handler.metadata.version == version and 
                    handler.state in [QueryHandlerState.ACTIVE, QueryHandlerState.CACHE_WARMING]):
                    return handler
        
        # Return best performing active handler
        active_handlers = [
            self._handlers[handler_id] for handler_id in handler_ids
            if self._handlers[handler_id].state in [QueryHandlerState.ACTIVE, QueryHandlerState.CACHE_WARMING]
        ]
        
        if active_handlers:
            # Select handler with best performance metrics
            return min(active_handlers, key=lambda h: h.average_response_time)
        
        return None
    
    async def execute_query(self, query: Query) -> QueryResult:
        """Execute query with full optimization and caching pipeline"""
        handler_instance = self.get_handler(query.query_type)
        if not handler_instance:
            raise EventProcessingError(f"No handler registered for query type: {query.query_type}")
        
        start_time = time.time()
        
        try:
            # Optimize query
            optimized_query = await self._performance_optimizer.optimize_query(query, handler_instance)
            
            # Check cache first
            cache_result = await self._check_cache(optimized_query, handler_instance)
            if cache_result:
                await self._update_handler_metrics(handler_instance, 0, True, True)
                return cache_result
            
            # Execute query
            result = await self._execute_query_with_handler(optimized_query, handler_instance)
            
            # Cache result if successful and caching is enabled
            if (result.status == QueryStatus.COMPLETED and 
                handler_instance.metadata.cache_strategy != CacheStrategy.NO_CACHE):
                await self._cache_result(optimized_query, result, handler_instance)
            
            # Update metrics
            execution_time = (time.time() - start_time) * 1000
            sla_violation = execution_time > handler_instance.metadata.performance_sla_ms
            success = result.status == QueryStatus.COMPLETED
            
            await self._update_handler_metrics(handler_instance, execution_time, success, False)
            
            if sla_violation:
                self._metrics["sla_violations"] += 1
                logger.warning(f"SLA violation for {query.query_type}: {execution_time}ms > {handler_instance.metadata.performance_sla_ms}ms")
            
            return result
            
        except Exception as e:
            execution_time = (time.time() - start_time) * 1000
            error_result = QueryResult(
                query_id=query.query_id,
                status=QueryStatus.FAILED,
                error=str(e),
                execution_time_ms=execution_time
            )
            
            await self._update_handler_metrics(handler_instance, execution_time, False, False)
            
            # Update handler state
            handler_instance.last_error = str(e)
            handler_instance.last_error_time = datetime.utcnow()
            
            raise
    
    async def _check_cache(self, query: Query, handler_instance: QueryHandlerInstance) -> Optional[QueryResult]:
        """Check cache for query result"""
        if handler_instance.metadata.cache_strategy == CacheStrategy.NO_CACHE:
            return None
        
        cache_key = handler_instance.instance.get_cache_key(query)
        cached_data = await self._cache_manager.get(handler_instance.metadata.handler_id, cache_key)
        
        if cached_data is not None:
            handler_instance.cache_hits += 1
            self._metrics["cache_hits"] += 1
            
            return QueryResult(
                query_id=query.query_id,
                status=QueryStatus.CACHED,
                data=cached_data,
                cache_hit=True,
                cache_level=CacheLevel.MEMORY,
                execution_time_ms=0.0
            )
        
        handler_instance.cache_misses += 1
        self._metrics["cache_misses"] += 1
        return None
    
    async def _cache_result(self, query: Query, result: QueryResult, handler_instance: QueryHandlerInstance) -> None:
        """Cache query result"""
        cache_key = handler_instance.instance.get_cache_key(query)
        
        # Determine TTL based on cache strategy
        ttl = handler_instance.metadata.cache_ttl_seconds
        
        if handler_instance.metadata.cache_strategy == CacheStrategy.ADAPTIVE:
            # Adaptive TTL based on query frequency and complexity
            complexity = self._performance_optimizer._calculate_query_complexity(query)
            ttl = max(60, int(ttl / complexity))  # Higher complexity = shorter TTL
        
        await self._cache_manager.set(
            handler_instance.metadata.handler_id,
            cache_key,
            result.data,
            ttl,
            metadata={"query_type": query.query_type, "complexity": complexity if handler_instance.metadata.cache_strategy == CacheStrategy.ADAPTIVE else 1.0}
        )
    
    async def _execute_query_with_handler(self, query: Query, handler_instance: QueryHandlerInstance) -> QueryResult:
        """Execute query with specific handler instance"""
        try:
            if asyncio.iscoroutinefunction(handler_instance.instance.handle):
                result = await handler_instance.instance.handle(query)
            else:
                result = handler_instance.instance.handle(query)
            
            if not isinstance(result, QueryResult):
                # Wrap result if handler doesn't return QueryResult
                result = QueryResult(
                    query_id=query.query_id,
                    status=QueryStatus.COMPLETED,
                    data=result
                )
            
            return result
            
        except Exception as e:
            return QueryResult(
                query_id=query.query_id,
                status=QueryStatus.FAILED,
                error=str(e)
            )
    
    async def _update_handler_metrics(self, handler_instance: QueryHandlerInstance, 
                                    execution_time: float, success: bool, cache_hit: bool) -> None:
        """Update handler performance metrics"""
        handler_instance.total_queries += 1
        
        if success:
            handler_instance.successful_queries += 1
        else:
            handler_instance.failed_queries += 1
        
        if not cache_hit and execution_time > 0:
            # Update average response time (excluding cache hits)
            total_non_cached = handler_instance.total_queries - handler_instance.cache_hits
            if total_non_cached > 0:
                handler_instance.average_response_time = (
                    (handler_instance.average_response_time * (total_non_cached - 1) + execution_time) /
                    total_non_cached
                )
            
            # Add to performance history
            handler_instance.performance_history.append({
                "execution_time": execution_time,
                "success": success,
                "timestamp": datetime.utcnow(),
                "cache_hit": cache_hit
            })
            
            # Update P95 response time
            recent_times = [
                h["execution_time"] for h in handler_instance.performance_history
                if not h["cache_hit"] and datetime.utcnow() - h["timestamp"] < timedelta(minutes=10)
            ]
            
            if len(recent_times) >= 20:  # Need enough samples for P95
                sorted_times = sorted(recent_times)
                p95_index = int(len(sorted_times) * 0.95)
                handler_instance.p95_response_time = sorted_times[p95_index]
        
        # Update global metrics
        self._metrics["total_queries"] += 1
        if not success:
            self._metrics["failed_queries"] += 1
        
        # Update global average response time
        if not cache_hit:
            current_avg = self._metrics["average_response_time"]
            total_non_cached = self._metrics["total_queries"] - self._metrics["cache_hits"]
            if total_non_cached > 0:
                new_avg = ((current_avg * (total_non_cached - 1)) + execution_time) / total_non_cached
                self._metrics["average_response_time"] = new_avg
    
    async def _warm_cache_for_handler(self, handler_instance: QueryHandlerInstance) -> None:
        """Warm cache for handler with common queries"""
        if not hasattr(handler_instance.instance, "get_cache_warming_queries"):
            return
        
        handler_instance.state = QueryHandlerState.CACHE_WARMING
        
        try:
            warming_queries = handler_instance.instance.get_cache_warming_queries()
            
            for query in warming_queries:
                try:
                    result = await self._execute_query_with_handler(query, handler_instance)
                    if result.status == QueryStatus.COMPLETED:
                        await self._cache_result(query, result, handler_instance)
                except Exception as e:
                    logger.error(f"Cache warming failed for query {query.query_id}: {e}")
            
            logger.info(f"Cache warming completed for handler {handler_instance.metadata.handler_id}")
            
        except Exception as e:
            logger.error(f"Cache warming failed for handler {handler_instance.metadata.handler_id}: {e}")
        
        finally:
            if handler_instance.state == QueryHandlerState.CACHE_WARMING:
                handler_instance.state = QueryHandlerState.ACTIVE
    
    def _start_background_tasks(self) -> None:
        """Start background tasks"""
        if self._health_check_enabled:
            self._health_check_task = asyncio.create_task(self._health_check_loop())
    
    async def _health_check_loop(self) -> None:
        """Background health check loop"""
        while True:
            try:
                await self._perform_health_checks()
                await asyncio.sleep(60)  # Check every minute
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Health check loop error: {e}")
                await asyncio.sleep(60)
    
    async def _perform_health_checks(self) -> None:
        """Perform health checks on all handlers"""
        for handler_instance in self._handlers.values():
            try:
                # Check handler health
                if hasattr(handler_instance.instance, "health_check"):
                    if asyncio.iscoroutinefunction(handler_instance.instance.health_check):
                        is_healthy = await handler_instance.instance.health_check()
                    else:
                        is_healthy = handler_instance.instance.health_check()
                    
                    if not is_healthy and handler_instance.state == QueryHandlerState.ACTIVE:
                        handler_instance.state = QueryHandlerState.DEGRADED
                        self._metrics["handlers_active"] -= 1
                        logger.warning(f"Query handler {handler_instance.metadata.handler_id} degraded")
                    
                    elif is_healthy and handler_instance.state == QueryHandlerState.DEGRADED:
                        handler_instance.state = QueryHandlerState.ACTIVE
                        self._metrics["handlers_active"] += 1
                        logger.info(f"Query handler {handler_instance.metadata.handler_id} recovered")
                
                # Check read model sync status
                for read_model in handler_instance.metadata.read_models:
                    await self._sync_manager.sync_read_model(
                        handler_instance.metadata.handler_id, read_model
                    )
                
                handler_instance.last_health_check = datetime.utcnow()
                
            except Exception as e:
                logger.error(f"Health check failed for handler {handler_instance.metadata.handler_id}: {e}")
                if handler_instance.state == QueryHandlerState.ACTIVE:
                    handler_instance.state = QueryHandlerState.DEGRADED
                    self._metrics["handlers_active"] -= 1
    
    async def invalidate_cache(self, handler_id: str = None, pattern: str = None) -> int:
        """Invalidate cache entries"""
        if handler_id:
            return await self._cache_manager.invalidate(handler_id, pattern)
        else:
            # Invalidate all handlers
            total_invalidated = 0
            for handler_id in self._handlers.keys():
                total_invalidated += await self._cache_manager.invalidate(handler_id, pattern)
            return total_invalidated
    
    async def handle_cache_invalidation_event(self, event: BaseEvent) -> None:
        """Handle event that triggers cache invalidation"""
        await self._cache_manager.handle_invalidation_event(event)
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get registry metrics"""
        total_cache_requests = self._metrics["cache_hits"] + self._metrics["cache_misses"]
        cache_hit_ratio = (
            self._metrics["cache_hits"] / total_cache_requests * 100
        ) if total_cache_requests > 0 else 0
        
        return {
            **self._metrics,
            "cache_hit_ratio_percent": round(cache_hit_ratio, 2)
        }
    
    def get_handler_health_status(self) -> Dict[str, Dict[str, Any]]:
        """Get health status of all handlers"""
        status = {}
        
        for handler_id, handler_instance in self._handlers.items():
            cache_stats = self._cache_manager.get_cache_stats(handler_id)
            sync_status = self._sync_manager.get_sync_status(handler_id)
            
            status[handler_id] = {
                "query_type": handler_instance.metadata.query_type,
                "version": handler_instance.metadata.version,
                "state": handler_instance.state.value,
                "total_queries": handler_instance.total_queries,
                "successful_queries": handler_instance.successful_queries,
                "failed_queries": handler_instance.failed_queries,
                "success_rate": (
                    handler_instance.successful_queries / handler_instance.total_queries * 100
                ) if handler_instance.total_queries > 0 else 0,
                "average_response_time": handler_instance.average_response_time,
                "p95_response_time": handler_instance.p95_response_time,
                "cache_stats": cache_stats,
                "sync_status": sync_status,
                "last_health_check": handler_instance.last_health_check.isoformat(),
                "last_error": handler_instance.last_error,
                "last_error_time": handler_instance.last_error_time.isoformat() if handler_instance.last_error_time else None,
                "performance_sla_ms": handler_instance.metadata.performance_sla_ms,
                "consistency_level": handler_instance.metadata.consistency_level
            }
        
        return status
    
    def get_performance_insights(self) -> Dict[str, Any]:
        """Get performance insights and optimization recommendations"""
        insights = {
            "slow_handlers": [],
            "cache_performance": {},
            "sla_violations": self._metrics["sla_violations"],
            "optimization_recommendations": []
        }
        
        # Identify slow handlers
        for handler_id, handler_instance in self._handlers.items():
            if (handler_instance.average_response_time > handler_instance.metadata.performance_sla_ms and
                handler_instance.total_queries > 10):
                insights["slow_handlers"].append({
                    "handler_id": handler_id,
                    "query_type": handler_instance.metadata.query_type,
                    "average_response_time": handler_instance.average_response_time,
                    "sla_ms": handler_instance.metadata.performance_sla_ms
                })
        
        # Cache performance analysis
        for handler_id in self._handlers.keys():
            cache_stats = self._cache_manager.get_cache_stats(handler_id)
            insights["cache_performance"][handler_id] = cache_stats
        
        # Generate optimization recommendations
        for handler_id in self._handlers.keys():
            recommendations = self._performance_optimizer.get_optimization_recommendations(handler_id)
            insights["optimization_recommendations"].extend(recommendations)
        
        return insights
    
    async def shutdown(self) -> None:
        """Graceful shutdown of registry"""
        logger.info("Shutting down query handler registry...")
        
        # Cancel background tasks
        if self._health_check_task:
            self._health_check_task.cancel()
            try:
                await self._health_check_task
            except asyncio.CancelledError:
                pass
        
        # Cleanup all handlers
        for handler_id in list(self._handlers.keys()):
            handler_instance = self._handlers[handler_id]
            
            try:
                if hasattr(handler_instance.instance, "cleanup"):
                    if asyncio.iscoroutinefunction(handler_instance.instance.cleanup):
                        await handler_instance.instance.cleanup()
                    else:
                        handler_instance.instance.cleanup()
            except Exception as e:
                logger.error(f"Handler cleanup failed for {handler_id}: {e}")
            
            del self._handlers[handler_id]
        
        self._query_type_mapping.clear()
        
        logger.info("Query handler registry shutdown complete")


# Singleton instance for global access
_query_handler_registry_instance: Optional[EnterpriseQueryHandlerRegistry] = None


def get_query_handler_registry() -> EnterpriseQueryHandlerRegistry:
    """Get singleton query handler registry instance"""
    global _query_handler_registry_instance
    if _query_handler_registry_instance is None:
        _query_handler_registry_instance = EnterpriseQueryHandlerRegistry()
    return _query_handler_registry_instance


def reset_query_handler_registry() -> None:
    """Reset query handler registry instance (for testing)"""
    global _query_handler_registry_instance
    if _query_handler_registry_instance:
        asyncio.create_task(_query_handler_registry_instance.shutdown())
    _query_handler_registry_instance = None