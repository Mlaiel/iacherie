"""🚀 Enterprise Query Dispatcher - CQRS Architecture
=====================================================
Module: events/cqrs/query_dispatcher.py
Author: Fahed Mlaiel (mlaiel@live.de)
=====================================================

⚠️ PROPRIÉTÉ INTELLECTUELLE EXCLUSIVE - FAHED MLAIEL ⚠️
(c) 2025 Fahed Mlaiel. Tous droits réservés.
Contact: mlaiel@live.de

🎯 INTELLIGENT QUERY DISPATCHER
Advanced query routing and optimization orchestration
- Dynamic read model selection and load balancing
- Query optimization and transformation
- Cache-aware routing and invalidation
- Geographic distribution and affinity routing
- Real-time performance monitoring and adaptation
- Multi-tenancy and data isolation support
"""

import asyncio
import logging
import time
import uuid
import hashlib
import json
from typing import Dict, List, Optional, Any, Callable, Union, Type, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, field, asdict
from enum import Enum
import weakref
from concurrent.futures import ThreadPoolExecutor
from collections import defaultdict, deque

from .query_bus import Query, QueryResult, QueryStatus, QueryHandler, CacheLevel
from ..core.base_event import BaseEvent
from ..core.event_priority import EventPriority
from ..core.exceptions import EventProcessingError, EventValidationError

logger = logging.getLogger(__name__)


class QueryRoutingStrategy(Enum):
    """Query routing strategies"""
    PERFORMANCE_BASED = "performance_based"
    GEOGRAPHIC_AFFINITY = "geographic_affinity"
    DATA_LOCALITY = "data_locality"
    LOAD_BALANCED = "load_balanced"
    CACHE_OPTIMIZED = "cache_optimized"
    CONSISTENCY_AWARE = "consistency_aware"


class ReadModelState(Enum):
    """Read model availability state"""
    ONLINE = "online"
    DEGRADED = "degraded"
    OFFLINE = "offline"
    SYNCING = "syncing"
    MAINTENANCE = "maintenance"


@dataclass
class ReadModelInstance:
    """Read model instance with state and metrics"""
    instance_id: str
    model_type: str
    endpoint: str
    state: ReadModelState = ReadModelState.ONLINE
    active_queries: int = 0
    max_concurrent: int = 100
    total_processed: int = 0
    total_failed: int = 0
    average_response_time: float = 0.0
    data_freshness_seconds: int = 0
    geographic_region: Optional[str] = None
    consistency_level: str = "eventual"
    cache_hit_ratio: float = 0.0
    last_health_check: datetime = field(default_factory=datetime.utcnow)
    capabilities: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class QueryRoutingRule:
    """Rule for query routing decisions"""
    rule_id: str
    query_type_pattern: str
    conditions: Dict[str, Any] = field(default_factory=dict)
    target_read_models: List[str] = field(default_factory=list)
    strategy: QueryRoutingStrategy = QueryRoutingStrategy.PERFORMANCE_BASED
    priority: int = 0
    enabled: bool = True
    cache_strategy: str = "aggressive"
    consistency_requirement: str = "eventual"
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class QueryProfile:
    """Query execution profile for optimization"""
    query_type: str
    typical_response_time_ms: float = 0.0
    complexity_score: float = 1.0
    resource_requirements: Dict[str, Any] = field(default_factory=dict)
    cache_effectiveness: float = 0.0
    optimal_read_models: List[str] = field(default_factory=list)
    performance_history: deque = field(default_factory=lambda: deque(maxlen=100))


class QueryOptimizer:
    """Optimize queries for better performance"""
    
    def __init__(self) -> None:
        self._optimization_rules: List[Callable[[Query], Query]] = []
        self._query_profiles: Dict[str, QueryProfile] = {}
        self._optimization_stats = {
            "queries_optimized": 0,
            "optimization_time_saved_ms": 0.0
        }
    
    def add_optimization_rule(self, rule: Callable[[Query], Query]) -> None:
        """Add query optimization rule"""
        self._optimization_rules.append(rule)
    
    async def optimize_query(self, query: Query) -> Query:
        """Optimize query for better performance"""
        original_query = query
        optimized_query = query
        
        for rule in self._optimization_rules:
            try:
                if asyncio.iscoroutinefunction(rule):
                    optimized_query = await rule(optimized_query)
                else:
                    optimized_query = rule(optimized_query)
            except Exception as e:
                logger.error(f"Query optimization rule failed: {e}")
        
        # Update optimization stats
        if optimized_query != original_query:
            self._optimization_stats["queries_optimized"] += 1
        
        # Update query profile
        await self._update_query_profile(optimized_query)
        
        return optimized_query
    
    async def _update_query_profile(self, query: Query) -> None:
        """Update query performance profile"""
        if query.query_type not in self._query_profiles:
            self._query_profiles[query.query_type] = QueryProfile(query_type=query.query_type)
        
        profile = self._query_profiles[query.query_type]
        
        # Calculate complexity score based on query parameters
        complexity_factors = [
            len(query.filters),
            len(query.sorting),
            query.pagination.get("limit", 50) / 50,  # Normalized to typical page size
            len(str(query.parameters))
        ]
        profile.complexity_score = sum(complexity_factors) / len(complexity_factors)
    
    def get_query_profile(self, query_type: str) -> Optional[QueryProfile]:
        """Get performance profile for query type"""
        return self._query_profiles.get(query_type)
    
    def get_optimization_stats(self) -> Dict[str, Any]:
        """Get optimization statistics"""
        return dict(self._optimization_stats)


class CacheInvalidationManager:
    """Manage cache invalidation across read models"""
    
    def __init__(self) -> None:
        self._invalidation_patterns: Dict[str, List[str]] = defaultdict(list)
        self._pending_invalidations: List[Dict[str, Any]] = []
    
    def register_invalidation_pattern(self, event_type: str, cache_pattern: str) -> None:
        """Register cache invalidation pattern for event type"""
        self._invalidation_patterns[event_type].append(cache_pattern)
    
    async def handle_event(self, event: BaseEvent) -> None:
        """Handle event and trigger cache invalidations"""
        patterns = self._invalidation_patterns.get(event.event_type, [])
        
        for pattern in patterns:
            invalidation = {
                "pattern": pattern,
                "event_id": event.event_id,
                "timestamp": datetime.utcnow(),
                "metadata": event.metadata
            }
            self._pending_invalidations.append(invalidation)
        
        # Process invalidations asynchronously
        if self._pending_invalidations:
            asyncio.create_task(self._process_invalidations())
    
    async def _process_invalidations(self) -> None:
        """Process pending cache invalidations"""
        invalidations_to_process = self._pending_invalidations.copy()
        self._pending_invalidations.clear()
        
        for invalidation in invalidations_to_process:
            try:
                # In a real implementation, this would invalidate cache entries
                # matching the pattern across all read models
                logger.info(f"Processing cache invalidation: {invalidation['pattern']}")
            except Exception as e:
                logger.error(f"Cache invalidation failed: {e}")


class GeographicRouter:
    """Route queries based on geographic affinity"""
    
    def __init__(self) -> None:
        self._region_mappings: Dict[str, List[str]] = {}
        self._user_regions: Dict[str, str] = {}
    
    def map_region_to_read_models(self, region: str, read_model_ids: List[str]) -> None:
        """Map geographic region to read model instances"""
        self._region_mappings[region] = read_model_ids
    
    def set_user_region(self, user_id: str, region: str) -> None:
        """Set user's geographic region"""
        self._user_regions[user_id] = region
    
    def get_preferred_read_models(self, user_id: str) -> List[str]:
        """Get preferred read models for user based on geography"""
        user_region = self._user_regions.get(user_id)
        if user_region and user_region in self._region_mappings:
            return self._region_mappings[user_region]
        return []


class PerformanceMonitor:
    """Monitor query performance and adapt routing"""
    
    def __init__(self) -> None:
        self._performance_history: Dict[str, deque] = defaultdict(lambda: deque(maxlen=1000))
        self._anomaly_threshold = 2.0  # Standard deviations
    
    def record_query_performance(self, query_type: str, read_model_id: str, 
                                response_time_ms: float, success: bool) -> None:
        """Record query performance metrics"""
        self._performance_history[f"{query_type}:{read_model_id}"].append({
            "response_time_ms": response_time_ms,
            "success": success,
            "timestamp": datetime.utcnow()
        })
    
    def get_performance_stats(self, query_type: str, read_model_id: str) -> Dict[str, float]:
        """Get performance statistics for query type and read model"""
        key = f"{query_type}:{read_model_id}"
        history = self._performance_history[key]
        
        if not history:
            return {"avg_response_time": 0.0, "success_rate": 0.0, "sample_count": 0}
        
        recent_history = [
            h for h in history 
            if datetime.utcnow() - h["timestamp"] < timedelta(minutes=10)
        ]
        
        if not recent_history:
            return {"avg_response_time": 0.0, "success_rate": 0.0, "sample_count": 0}
        
        avg_response_time = sum(h["response_time_ms"] for h in recent_history) / len(recent_history)
        success_rate = sum(1 for h in recent_history if h["success"]) / len(recent_history)
        
        return {
            "avg_response_time": avg_response_time,
            "success_rate": success_rate,
            "sample_count": len(recent_history)
        }
    
    def detect_performance_anomalies(self, query_type: str, read_model_id: str) -> bool:
        """Detect performance anomalies"""
        stats = self.get_performance_stats(query_type, read_model_id)
        
        if stats["sample_count"] < 10:
            return False  # Not enough data
        
        # Simple anomaly detection based on success rate
        return stats["success_rate"] < 0.8  # Less than 80% success rate


class EnterpriseQueryDispatcher:
    """Enterprise query dispatcher with advanced routing and optimization"""
    
    def __init__(self) -> None:
        self._read_model_registry: Dict[str, List[ReadModelInstance]] = defaultdict(list)
        self._routing_rules: List[QueryRoutingRule] = []
        
        # Components
        self._query_optimizer = QueryOptimizer()
        self._cache_invalidation_manager = CacheInvalidationManager()
        self._geographic_router = GeographicRouter()
        self._performance_monitor = PerformanceMonitor()
        
        # Metrics and monitoring
        self._metrics = {
            "queries_dispatched": 0,
            "read_models_registered": 0,
            "cache_hits": 0,
            "cache_misses": 0,
            "average_dispatch_time": 0.0,
            "geographic_route_hits": 0
        }
        
        # State management
        self._active_dispatches: Dict[str, Dict[str, Any]] = {}
        self._dispatch_history: deque = deque(maxlen=1000)
        self._circuit_breakers: Dict[str, Dict[str, Any]] = defaultdict(lambda: {
            "failure_count": 0,
            "last_failure": None,
            "state": "closed"
        })
    
    def register_read_model(self, query_type: str, read_model: ReadModelInstance) -> None:
        """Register read model instance for query type"""
        self._read_model_registry[query_type].append(read_model)
        self._metrics["read_models_registered"] += 1
        
        logger.info(f"Registered read model {read_model.instance_id} for query type {query_type}")
    
    def add_routing_rule(self, rule: QueryRoutingRule) -> None:
        """Add query routing rule"""
        self._routing_rules.append(rule)
        self._routing_rules.sort(key=lambda r: r.priority, reverse=True)
        logger.info(f"Added routing rule: {rule.rule_id}")
    
    def add_optimization_rule(self, rule: Callable[[Query], Query]) -> None:
        """Add query optimization rule"""
        self._query_optimizer.add_optimization_rule(rule)
    
    def register_cache_invalidation_pattern(self, event_type: str, cache_pattern: str) -> None:
        """Register cache invalidation pattern"""
        self._cache_invalidation_manager.register_invalidation_pattern(event_type, cache_pattern)
    
    def map_user_to_region(self, user_id: str, region: str) -> None:
        """Map user to geographic region"""
        self._geographic_router.set_user_region(user_id, region)
    
    async def dispatch_query(self, query: Query) -> QueryResult:
        """Dispatch query with full enterprise pipeline"""
        start_time = time.time()
        dispatch_id = str(uuid.uuid4())
        
        try:
            # Track dispatch
            self._active_dispatches[dispatch_id] = {
                "query": query,
                "started_at": datetime.utcnow(),
                "status": "processing"
            }
            
            # Query optimization
            optimized_query = await self._query_optimizer.optimize_query(query)
            
            # Read model selection
            read_model_instance = await self._select_read_model(optimized_query)
            if not read_model_instance:
                raise EventProcessingError(f"No available read model for query type: {optimized_query.query_type}")
            
            # Circuit breaker check
            await self._check_circuit_breaker(read_model_instance.instance_id)
            
            # Execute query
            result = await self._execute_query_with_read_model(optimized_query, read_model_instance)
            
            # Update metrics and monitoring
            execution_time = (time.time() - start_time) * 1000
            await self._update_dispatch_metrics(optimized_query, result, execution_time)
            await self._update_performance_monitoring(optimized_query, read_model_instance, result, execution_time)
            
            return result
            
        except Exception as e:
            execution_time = (time.time() - start_time) * 1000
            error_result = QueryResult(
                query_id=query.query_id,
                status=QueryStatus.FAILED,
                error=str(e),
                execution_time_ms=execution_time
            )
            
            await self._handle_dispatch_failure(query, error_result, e)
            return error_result
            
        finally:
            # Cleanup
            self._active_dispatches.pop(dispatch_id, None)
    
    async def _select_read_model(self, query: Query) -> Optional[ReadModelInstance]:
        """Select optimal read model for query"""
        # Find applicable routing rules
        applicable_rules = [
            rule for rule in self._routing_rules
            if rule.enabled and self._rule_matches_query(rule, query)
        ]
        
        # Get candidate read models
        if applicable_rules:
            rule = applicable_rules[0]
            candidate_models = [
                model for model in self._read_model_registry.get(query.query_type, [])
                if model.instance_id in rule.target_read_models and model.state == ReadModelState.ONLINE
            ]
            strategy = rule.strategy
        else:
            candidate_models = [
                model for model in self._read_model_registry.get(query.query_type, [])
                if model.state == ReadModelState.ONLINE and model.active_queries < model.max_concurrent
            ]
            strategy = QueryRoutingStrategy.PERFORMANCE_BASED
        
        if not candidate_models:
            return None
        
        # Apply routing strategy
        return await self._apply_routing_strategy(query, candidate_models, strategy)
    
    def _rule_matches_query(self, rule: QueryRoutingRule, query: Query) -> bool:
        """Check if routing rule matches query"""
        # Pattern matching
        if rule.query_type_pattern != "*" and rule.query_type_pattern != query.query_type:
            return False
        
        # Check additional conditions
        for key, expected_value in rule.conditions.items():
            if key in query.parameters and query.parameters[key] != expected_value:
                return False
            if key in query.filters and query.filters[key] != expected_value:
                return False
        
        return True
    
    async def _apply_routing_strategy(self, query: Query, candidates: List[ReadModelInstance], 
                                    strategy: QueryRoutingStrategy) -> ReadModelInstance:
        """Apply routing strategy to select read model"""
        if strategy == QueryRoutingStrategy.PERFORMANCE_BASED:
            return self._select_by_performance(query, candidates)
        elif strategy == QueryRoutingStrategy.GEOGRAPHIC_AFFINITY:
            return self._select_by_geography(query, candidates)
        elif strategy == QueryRoutingStrategy.LOAD_BALANCED:
            return self._select_by_load(candidates)
        elif strategy == QueryRoutingStrategy.CACHE_OPTIMIZED:
            return self._select_by_cache_efficiency(candidates)
        elif strategy == QueryRoutingStrategy.CONSISTENCY_AWARE:
            return self._select_by_consistency(query, candidates)
        else:
            return candidates[0]  # Default
    
    def _select_by_performance(self, query: Query, candidates: List[ReadModelInstance]) -> ReadModelInstance:
        """Select read model based on performance metrics"""
        def score_model(model: ReadModelInstance) -> float:
            stats = self._performance_monitor.get_performance_stats(query.query_type, model.instance_id)
            
            # Lower response time and higher success rate = higher score
            response_score = 1000 / (stats["avg_response_time"] + 1)
            success_score = stats["success_rate"] * 100
            load_score = (model.max_concurrent - model.active_queries) / model.max_concurrent * 50
            
            return response_score + success_score + load_score
        
        return max(candidates, key=score_model)
    
    def _select_by_geography(self, query: Query, candidates: List[ReadModelInstance]) -> ReadModelInstance:
        """Select read model based on geographic affinity"""
        if query.user_id:
            preferred_models = self._geographic_router.get_preferred_read_models(query.user_id)
            
            # Find candidates in preferred region
            geographic_candidates = [
                model for model in candidates
                if model.instance_id in preferred_models
            ]
            
            if geographic_candidates:
                self._metrics["geographic_route_hits"] += 1
                return self._select_by_load(geographic_candidates)
        
        # Fallback to load-based selection
        return self._select_by_load(candidates)
    
    def _select_by_load(self, candidates: List[ReadModelInstance]) -> ReadModelInstance:
        """Select read model with lowest current load"""
        return min(candidates, key=lambda m: m.active_queries / m.max_concurrent)
    
    def _select_by_cache_efficiency(self, candidates: List[ReadModelInstance]) -> ReadModelInstance:
        """Select read model with highest cache hit ratio"""
        return max(candidates, key=lambda m: m.cache_hit_ratio)
    
    def _select_by_consistency(self, query: Query, candidates: List[ReadModelInstance]) -> ReadModelInstance:
        """Select read model based on consistency requirements"""
        required_consistency = query.required_consistency
        
        # Filter by consistency level
        consistent_candidates = [
            model for model in candidates
            if self._consistency_matches(model.consistency_level, required_consistency)
        ]
        
        if consistent_candidates:
            return self._select_by_performance(query, consistent_candidates)
        else:
            # No models meet consistency requirement - log warning and use best available
            logger.warning(f"No read models meet consistency requirement: {required_consistency}")
            return self._select_by_performance(query, candidates)
    
    def _consistency_matches(self, model_consistency: str, required_consistency: str) -> bool:
        """Check if model consistency level meets requirement"""
        consistency_levels = {"eventual": 1, "session": 2, "strong": 3}
        
        model_level = consistency_levels.get(model_consistency, 1)
        required_level = consistency_levels.get(required_consistency, 1)
        
        return model_level >= required_level
    
    async def _check_circuit_breaker(self, read_model_id: str) -> None:
        """Check circuit breaker state for read model"""
        breaker = self._circuit_breakers[read_model_id]
        
        if breaker["state"] == "open":
            # Check if circuit should close (after cooldown period)
            if breaker["last_failure"]:
                cooldown_period = timedelta(minutes=2)
                if datetime.utcnow() - breaker["last_failure"] > cooldown_period:
                    breaker["state"] = "half_open"
                    breaker["failure_count"] = 0
                    logger.info(f"Circuit breaker half-open for read model {read_model_id}")
                else:
                    raise EventProcessingError(f"Circuit breaker open for read model: {read_model_id}")
    
    async def _execute_query_with_read_model(self, query: Query, read_model: ReadModelInstance) -> QueryResult:
        """Execute query with specific read model instance"""
        read_model.active_queries += 1
        start_time = time.time()
        
        try:
            # In a real implementation, this would make the actual query to the read model
            # For now, we'll simulate the execution
            await asyncio.sleep(0.01)  # Simulate query execution time
            
            result = QueryResult(
                query_id=query.query_id,
                status=QueryStatus.COMPLETED,
                data={"simulated": "result", "read_model": read_model.instance_id},
                execution_time_ms=(time.time() - start_time) * 1000
            )
            
            # Update read model metrics
            read_model.total_processed += 1
            execution_time = result.execution_time_ms or 0
            
            # Update average response time
            read_model.average_response_time = (
                (read_model.average_response_time * (read_model.total_processed - 1) + execution_time) /
                read_model.total_processed
            )
            
            # Reset circuit breaker on success
            self._circuit_breakers[read_model.instance_id]["failure_count"] = 0
            self._circuit_breakers[read_model.instance_id]["state"] = "closed"
            
            return result
            
        except Exception as e:
            # Handle read model failure
            read_model.total_failed += 1
            
            # Update circuit breaker
            breaker = self._circuit_breakers[read_model.instance_id]
            breaker["failure_count"] += 1
            breaker["last_failure"] = datetime.utcnow()
            
            # Open circuit breaker if failure threshold reached
            if breaker["failure_count"] >= 5:
                breaker["state"] = "open"
                logger.warning(f"Circuit breaker opened for read model {read_model.instance_id}")
            
            raise EventProcessingError(f"Read model query failed: {e}")
            
        finally:
            read_model.active_queries -= 1
    
    async def _update_dispatch_metrics(self, query: Query, result: QueryResult, execution_time: float) -> None:
        """Update dispatch metrics"""
        self._metrics["queries_dispatched"] += 1
        
        if result.cache_hit:
            self._metrics["cache_hits"] += 1
        else:
            self._metrics["cache_misses"] += 1
        
        # Update average dispatch time
        current_avg = self._metrics["average_dispatch_time"]
        total_dispatched = self._metrics["queries_dispatched"]
        new_avg = ((current_avg * (total_dispatched - 1)) + execution_time) / total_dispatched
        self._metrics["average_dispatch_time"] = new_avg
        
        # Add to history
        self._dispatch_history.append({
            "query_id": query.query_id,
            "query_type": query.query_type,
            "status": result.status.value,
            "execution_time": execution_time,
            "cache_hit": result.cache_hit,
            "timestamp": datetime.utcnow()
        })
    
    async def _update_performance_monitoring(self, query: Query, read_model: ReadModelInstance, 
                                           result: QueryResult, execution_time: float) -> None:
        """Update performance monitoring"""
        success = result.status == QueryStatus.COMPLETED
        self._performance_monitor.record_query_performance(
            query.query_type, read_model.instance_id, execution_time, success
        )
        
        # Check for performance anomalies
        if self._performance_monitor.detect_performance_anomalies(query.query_type, read_model.instance_id):
            logger.warning(f"Performance anomaly detected for {query.query_type} on {read_model.instance_id}")
    
    async def _handle_dispatch_failure(self, query: Query, result: QueryResult, exception: Exception) -> None:
        """Handle dispatch failure"""
        logger.error(f"Query dispatch failed: {query.query_id} - {exception}")
    
    async def handle_cache_invalidation_event(self, event: BaseEvent) -> None:
        """Handle event that may trigger cache invalidation"""
        await self._cache_invalidation_manager.handle_event(event)
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get dispatcher metrics"""
        total_read_models = sum(len(models) for models in self._read_model_registry.values())
        cache_hit_ratio = (
            self._metrics["cache_hits"] / 
            (self._metrics["cache_hits"] + self._metrics["cache_misses"]) * 100
        ) if (self._metrics["cache_hits"] + self._metrics["cache_misses"]) > 0 else 0
        
        return {
            **self._metrics,
            "total_read_models": total_read_models,
            "active_dispatches": len(self._active_dispatches),
            "routing_rules": len(self._routing_rules),
            "cache_hit_ratio_percent": round(cache_hit_ratio, 2),
            "circuit_breakers_open": len([
                b for b in self._circuit_breakers.values() 
                if b["state"] == "open"
            ])
        }
    
    def get_read_model_health(self) -> Dict[str, List[Dict[str, Any]]]:
        """Get health status of all read models"""
        health_status = {}
        
        for query_type, models in self._read_model_registry.items():
            health_status[query_type] = []
            for model in models:
                health_status[query_type].append({
                    "instance_id": model.instance_id,
                    "state": model.state.value,
                    "active_queries": model.active_queries,
                    "max_concurrent": model.max_concurrent,
                    "total_processed": model.total_processed,
                    "total_failed": model.total_failed,
                    "success_rate": ((model.total_processed - model.total_failed) / model.total_processed * 100) if model.total_processed > 0 else 0,
                    "average_response_time": model.average_response_time,
                    "cache_hit_ratio": model.cache_hit_ratio,
                    "geographic_region": model.geographic_region,
                    "consistency_level": model.consistency_level
                })
        
        return health_status
    
    def get_performance_insights(self) -> Dict[str, Any]:
        """Get performance insights and recommendations"""
        optimization_stats = self._query_optimizer.get_optimization_stats()
        
        slow_query_types = []
        for query_type, models in self._read_model_registry.items():
            for model in models:
                stats = self._performance_monitor.get_performance_stats(query_type, model.instance_id)
                if stats["avg_response_time"] > 1000:  # > 1 second
                    slow_query_types.append({
                        "query_type": query_type,
                        "read_model": model.instance_id,
                        "avg_response_time": stats["avg_response_time"]
                    })
        
        return {
            "optimization_stats": optimization_stats,
            "slow_query_types": slow_query_types,
            "circuit_breaker_status": dict(self._circuit_breakers),
            "recommendations": self._generate_recommendations()
        }
    
    def _generate_recommendations(self) -> List[str]:
        """Generate performance recommendations"""
        recommendations = []
        
        # Analyze cache hit ratio
        cache_hit_ratio = self._metrics.get("cache_hits", 0) / max(
            self._metrics.get("cache_hits", 0) + self._metrics.get("cache_misses", 0), 1
        )
        
        if cache_hit_ratio < 0.6:
            recommendations.append("Consider increasing cache TTL or implementing smarter cache strategies")
        
        # Analyze geographic routing effectiveness
        if self._metrics["geographic_route_hits"] / max(self._metrics["queries_dispatched"], 1) < 0.3:
            recommendations.append("Geographic routing is underutilized - consider better user-region mapping")
        
        # Check for overloaded read models
        overloaded_models = [
            model for models in self._read_model_registry.values()
            for model in models
            if model.active_queries / model.max_concurrent > 0.8
        ]
        
        if overloaded_models:
            recommendations.append(f"Consider scaling up read models: {[m.instance_id for m in overloaded_models]}")
        
        return recommendations


# Singleton instance for global access
_query_dispatcher_instance: Optional[EnterpriseQueryDispatcher] = None


def get_query_dispatcher() -> EnterpriseQueryDispatcher:
    """Get singleton query dispatcher instance"""
    global _query_dispatcher_instance
    if _query_dispatcher_instance is None:
        _query_dispatcher_instance = EnterpriseQueryDispatcher()
    return _query_dispatcher_instance


def reset_query_dispatcher() -> None:
    """Reset query dispatcher instance (for testing)"""
    global _query_dispatcher_instance
    _query_dispatcher_instance = None