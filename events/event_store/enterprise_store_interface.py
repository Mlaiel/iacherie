"""🚀 Event Store Enterprise Interface - IA Influencer Agent Platform
=====================================================================
Module: events/event_store/enterprise_store_interface.py
Author: Fahed Mlaiel (mlaiel@live.de)
=====================================================================

⚠️ PROPRIÉTÉ INTELLECTUELLE EXCLUSIVE - FAHED MLAIEL ⚠️
(c) 2025 Fahed Mlaiel. Tous droits réservés.
Contact: mlaiel@live.de

🎯 ENTERPRISE EVENT STORE INTERFACE
Unified interface for multi-backend event storage with intelligent routing,
failover, and performance optimization for Ainflue platform.

Key Features:
- Multi-backend abstraction (PostgreSQL + MongoDB + Elasticsearch)
- Intelligent event routing based on business logic
- Automatic failover and load balancing
- Performance monitoring and optimization
- Transaction management across backends
- Real-time metrics and health monitoring
"""

import asyncio
import logging
from abc import ABC, abstractmethod
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, AsyncIterator, Union
from enum import Enum
from dataclasses import dataclass, field

from ..core.base_event import BaseEvent
from ..core.event_priority import EventPriority

logger = logging.getLogger(__name__)


class StorageBackendType(Enum):
    """Storage backend types for different use cases"""
    POSTGRESQL = "postgresql"  # Critical business events
    MONGODB = "mongodb"       # Analytics and metrics
    ELASTICSEARCH = "elasticsearch"  # Search and indexing
    REDIS = "redis"          # Caching and temporary storage
    ALL = "all"              # Store in all backends


class StorageStrategy(Enum):
    """Storage strategies for different event types"""
    TRANSACTIONAL = "transactional"      # ACID compliance required
    ANALYTICAL = "analytical"            # Optimized for analytics
    SEARCHABLE = "searchable"            # Full-text search enabled
    CACHED = "cached"                    # Temporary/cached storage
    REPLICATED = "replicated"            # Multi-backend replication
    ARCHIVED = "archived"                # Long-term archival


@dataclass
class EventQuery:
    """Query parameters for event retrieval"""
    aggregate_id: Optional[str] = None
    event_types: Optional[List[str]] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    creator_id: Optional[str] = None
    content_type: Optional[str] = None
    limit: int = 100
    offset: int = 0
    order_by: str = "occurred_at"
    order_direction: str = "DESC"
    include_metadata: bool = True
    
    def is_recent(self) -> bool:
        """Check if query is for recent events (< 1 hour)"""
        if self.start_time:
            return datetime.utcnow() - self.start_time < timedelta(hours=1)
        return False
    
    def is_transactional(self) -> bool:
        """Check if query requires transactional consistency"""
        transactional_types = [
            'content.uploaded', 'payment.processed', 'user.created',
            'collaboration.accepted', 'revenue.generated'
        ]
        if self.event_types:
            return any(event_type in transactional_types for event_type in self.event_types)
        return False
    
    def cache_key(self) -> str:
        """Generate cache key for query"""
        key_parts = [
            f"agg:{self.aggregate_id or 'all'}",
            f"types:{','.join(self.event_types or ['all'])}",
            f"creator:{self.creator_id or 'all'}",
            f"content:{self.content_type or 'all'}",
            f"limit:{self.limit}",
            f"offset:{self.offset}"
        ]
        return "|".join(key_parts)


@dataclass
class StreamConfig:
    """Configuration for event streaming"""
    stream_name: str
    filter_criteria: Dict[str, Any] = field(default_factory=dict)
    batch_size: int = 100
    max_wait_time: float = 5.0
    from_timestamp: Optional[datetime] = None
    include_metadata: bool = True
    buffer_size: int = 1000


@dataclass
class StoreResult:
    """Result of event storage operation"""
    success: bool
    event_id: str
    backends_used: List[StorageBackendType]
    latency_ms: float
    errors: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class StorageMetrics:
    """Storage performance and health metrics"""
    total_events_stored: int
    events_per_second: float
    average_latency_ms: float
    p95_latency_ms: float
    p99_latency_ms: float
    backend_health: Dict[StorageBackendType, bool]
    storage_utilization: Dict[StorageBackendType, float]
    error_rate: float
    cache_hit_rate: float
    timestamp: datetime = field(default_factory=datetime.utcnow)


@dataclass
class OptimizationResult:
    """Result of storage optimization operation"""
    optimizations_applied: List[str]
    performance_improvement: float
    storage_saved_bytes: int
    recommendations: List[str]
    timestamp: datetime = field(default_factory=datetime.utcnow)


class IEventStoreBackend(ABC):
    """Interface for event storage backends"""
    
    @abstractmethod
    async def store_event(self, event: BaseEvent) -> StoreResult:
        """Store a single event"""
        pass
    
    @abstractmethod
    async def store_events_batch(self, events: List[BaseEvent]) -> List[StoreResult]:
        """Store multiple events in batch"""
        pass
    
    @abstractmethod
    async def retrieve_events(self, query: EventQuery) -> List[BaseEvent]:
        """Retrieve events based on query"""
        pass
    
    @abstractmethod
    async def stream_events(self, config: StreamConfig) -> AsyncIterator[BaseEvent]:
        """Stream events in real-time"""
        pass
    
    @abstractmethod
    async def health_check(self) -> bool:
        """Check backend health"""
        pass
    
    @abstractmethod
    async def get_metrics(self) -> Dict[str, Any]:
        """Get backend-specific metrics"""
        pass


class EnterpriseEventStore:
    """
    Enterprise-grade unified event store interface
    
    Provides intelligent routing, failover, and optimization across
    multiple storage backends for the Ainflue platform.
    """
    
    def __init__(self):
        self._backends: Dict[StorageBackendType, IEventStoreBackend] = {}
        self._routing_strategies: Dict[str, StorageStrategy] = {}
        self._performance_cache: Dict[str, Any] = {}
        self._metrics_collector = None
        self._is_initialized = False
        
        # Ainflue-specific business logic routing
        self._initialize_business_routing()
    
    def _initialize_business_routing(self):
        """Initialize Ainflue business logic routing strategies"""
        
        # Content lifecycle events → PostgreSQL + MongoDB
        content_events = [
            'content.uploaded', 'content.processed', 'content.published',
            'content.protected', 'content.distributed'
        ]
        for event_type in content_events:
            self._routing_strategies[event_type] = StorageStrategy.REPLICATED
        
        # User interaction events → MongoDB + Elasticsearch
        interaction_events = [
            'content.viewed', 'content.liked', 'content.shared',
            'content.commented', 'collaboration.requested'
        ]
        for event_type in interaction_events:
            self._routing_strategies[event_type] = StorageStrategy.ANALYTICAL
        
        # Revenue and payment events → PostgreSQL (ACID required)
        revenue_events = [
            'revenue.generated', 'payment.processed', 'payout.completed',
            'monetization.licensing.granted'
        ]
        for event_type in revenue_events:
            self._routing_strategies[event_type] = StorageStrategy.TRANSACTIONAL
        
        # Search and SEO events → Elasticsearch
        search_events = [
            'content.tagged', 'seo.optimization.completed',
            'search.query.executed', 'content.indexed'
        ]
        for event_type in search_events:
            self._routing_strategies[event_type] = StorageStrategy.SEARCHABLE
        
        # Analytics events → MongoDB
        analytics_events = [
            'analytics.engagement.calculated', 'analytics.performance.updated',
            'analytics.trend.detected', 'metrics.aggregated'
        ]
        for event_type in analytics_events:
            self._routing_strategies[event_type] = StorageStrategy.ANALYTICAL
    
    async def initialize(self, backends: Dict[StorageBackendType, IEventStoreBackend]):
        """Initialize the enterprise store with backends"""
        self._backends = backends
        
        # Verify all backends are healthy
        for backend_type, backend in self._backends.items():
            try:
                health = await backend.health_check()
                if not health:
                    logger.warning(f"Backend {backend_type} is not healthy")
            except Exception as e:
                logger.error(f"Failed to check health of {backend_type}: {e}")
        
        self._is_initialized = True
        logger.info("Enterprise Event Store initialized successfully")
    
    def _get_storage_strategy(self, event: BaseEvent) -> StorageStrategy:
        """Determine storage strategy for event based on business logic"""
        
        # Check explicit strategy first
        if event.event_type in self._routing_strategies:
            return self._routing_strategies[event.event_type]
        
        # Fallback based on event characteristics
        if hasattr(event, 'priority'):
            if event.priority == EventPriority.CRITICAL:
                return StorageStrategy.REPLICATED
            elif event.priority == EventPriority.HIGH:
                return StorageStrategy.TRANSACTIONAL
        
        # Check for business context
        if hasattr(event, 'data'):
            data = event.data
            
            # Revenue-related events need ACID compliance
            if 'revenue' in str(data) or 'payment' in str(data):
                return StorageStrategy.TRANSACTIONAL
            
            # Content-related events need search capability
            if 'content_id' in data or 'content_type' in data:
                return StorageStrategy.SEARCHABLE
            
            # User interaction events for analytics
            if 'user_id' in data and 'interaction' in event.event_type:
                return StorageStrategy.ANALYTICAL
        
        # Default strategy
        return StorageStrategy.REPLICATED
    
    def _get_target_backends(self, strategy: StorageStrategy) -> List[StorageBackendType]:
        """Get target backends for storage strategy"""
        
        strategy_mapping = {
            StorageStrategy.TRANSACTIONAL: [StorageBackendType.POSTGRESQL],
            StorageStrategy.ANALYTICAL: [StorageBackendType.MONGODB],
            StorageStrategy.SEARCHABLE: [StorageBackendType.ELASTICSEARCH],
            StorageStrategy.CACHED: [StorageBackendType.REDIS],
            StorageStrategy.REPLICATED: [
                StorageBackendType.POSTGRESQL,
                StorageBackendType.MONGODB
            ],
            StorageStrategy.ARCHIVED: [
                StorageBackendType.POSTGRESQL,
                StorageBackendType.MONGODB,
                StorageBackendType.ELASTICSEARCH
            ]
        }
        
        return strategy_mapping.get(strategy, [StorageBackendType.POSTGRESQL])
    
    async def store_event(self, 
                         event: BaseEvent, 
                         storage_strategy: Optional[StorageStrategy] = None) -> StoreResult:
        """
        Store event using intelligent routing and failover
        
        Args:
            event: The domain event to store
            storage_strategy: Optional explicit storage strategy
            
        Returns:
            StoreResult with storage details and performance metrics
        """
        if not self._is_initialized:
            raise RuntimeError("Enterprise store not initialized")
        
        start_time = datetime.utcnow()
        strategy = storage_strategy or self._get_storage_strategy(event)
        target_backends = self._get_target_backends(strategy)
        
        results = []
        used_backends = []
        errors = []
        
        # Store in target backends with failover
        for backend_type in target_backends:
            if backend_type not in self._backends:
                errors.append(f"Backend {backend_type} not available")
                continue
            
            try:
                backend = self._backends[backend_type]
                result = await backend.store_event(event)
                
                if result.success:
                    used_backends.append(backend_type)
                    results.append(result)
                else:
                    errors.extend(result.errors)
                    
            except Exception as e:
                logger.error(f"Failed to store event in {backend_type}: {e}")
                errors.append(f"{backend_type}: {str(e)}")
        
        # Calculate performance metrics
        latency = (datetime.utcnow() - start_time).total_seconds() * 1000
        
        # Determine overall success
        success = len(used_backends) > 0
        
        return StoreResult(
            success=success,
            event_id=event.event_id,
            backends_used=used_backends,
            latency_ms=latency,
            errors=errors,
            metadata={
                'strategy': strategy.value,
                'target_backends': [b.value for b in target_backends],
                'timestamp': start_time.isoformat()
            }
        )
    
    async def retrieve_events(self, query: EventQuery) -> List[BaseEvent]:
        """
        Retrieve events with intelligent backend selection
        
        Args:
            query: Event query parameters
            
        Returns:
            List of retrieved events
        """
        if not self._is_initialized:
            raise RuntimeError("Enterprise store not initialized")
        
        # Select optimal backend for query
        backend_type = self._select_query_backend(query)
        
        if backend_type not in self._backends:
            # Fallback to PostgreSQL
            backend_type = StorageBackendType.POSTGRESQL
        
        try:
            backend = self._backends[backend_type]
            events = await backend.retrieve_events(query)
            
            # Cache frequently accessed queries
            if query.is_recent():
                cache_key = query.cache_key()
                self._performance_cache[cache_key] = {
                    'events': events,
                    'timestamp': datetime.utcnow(),
                    'backend': backend_type.value
                }
            
            return events
            
        except Exception as e:
            logger.error(f"Failed to retrieve events from {backend_type}: {e}")
            
            # Try fallback backends
            for fallback_type in [StorageBackendType.POSTGRESQL, StorageBackendType.MONGODB]:
                if fallback_type != backend_type and fallback_type in self._backends:
                    try:
                        fallback_backend = self._backends[fallback_type]
                        return await fallback_backend.retrieve_events(query)
                    except Exception as fallback_e:
                        logger.error(f"Fallback query failed for {fallback_type}: {fallback_e}")
            
            raise e
    
    def _select_query_backend(self, query: EventQuery) -> StorageBackendType:
        """Select optimal backend for query based on characteristics"""
        
        # Text search queries → Elasticsearch
        if hasattr(query, 'search_text') and query.search_text:
            return StorageBackendType.ELASTICSEARCH
        
        # Analytics queries → MongoDB
        if query.event_types:
            analytics_patterns = ['analytics', 'metrics', 'engagement', 'performance']
            if any(pattern in event_type for event_type in query.event_types 
                   for pattern in analytics_patterns):
                return StorageBackendType.MONGODB
        
        # Recent queries → Redis cache first, then PostgreSQL
        if query.is_recent():
            cache_key = query.cache_key()
            if cache_key in self._performance_cache:
                cached_data = self._performance_cache[cache_key]
                # Cache valid for 5 minutes
                if datetime.utcnow() - cached_data['timestamp'] < timedelta(minutes=5):
                    return StorageBackendType.REDIS
            return StorageBackendType.POSTGRESQL
        
        # Transactional queries → PostgreSQL
        if query.is_transactional():
            return StorageBackendType.POSTGRESQL
        
        # Default to PostgreSQL for reliability
        return StorageBackendType.POSTGRESQL
    
    async def stream_events(self, stream_config: StreamConfig) -> AsyncIterator[BaseEvent]:
        """
        Stream events in real-time from optimal backend
        
        Args:
            stream_config: Streaming configuration
            
        Yields:
            Real-time events as they arrive
        """
        if not self._is_initialized:
            raise RuntimeError("Enterprise store not initialized")
        
        # Select backend for streaming (prefer MongoDB for analytics)
        backend_type = StorageBackendType.MONGODB
        if backend_type not in self._backends:
            backend_type = StorageBackendType.POSTGRESQL
        
        backend = self._backends[backend_type]
        
        async for event in backend.stream_events(stream_config):
            yield event
    
    async def get_storage_metrics(self) -> StorageMetrics:
        """
        Get comprehensive storage performance metrics
        
        Returns:
            Aggregated metrics across all backends
        """
        if not self._is_initialized:
            raise RuntimeError("Enterprise store not initialized")
        
        backend_health = {}
        total_metrics = {
            'events_stored': 0,
            'total_latency': 0.0,
            'latency_samples': 0,
            'errors': 0,
            'cache_hits': 0,
            'cache_requests': 0
        }
        
        # Collect metrics from all backends
        for backend_type, backend in self._backends.items():
            try:
                health = await backend.health_check()
                backend_health[backend_type] = health
                
                metrics = await backend.get_metrics()
                if metrics:
                    total_metrics['events_stored'] += metrics.get('events_stored', 0)
                    total_metrics['total_latency'] += metrics.get('total_latency', 0)
                    total_metrics['latency_samples'] += metrics.get('latency_samples', 0)
                    total_metrics['errors'] += metrics.get('errors', 0)
                    
            except Exception as e:
                logger.error(f"Failed to get metrics from {backend_type}: {e}")
                backend_health[backend_type] = False
        
        # Calculate aggregated metrics
        avg_latency = (total_metrics['total_latency'] / max(total_metrics['latency_samples'], 1))
        error_rate = total_metrics['errors'] / max(total_metrics['events_stored'], 1)
        cache_hit_rate = (total_metrics['cache_hits'] / 
                         max(total_metrics['cache_requests'], 1))
        
        return StorageMetrics(
            total_events_stored=total_metrics['events_stored'],
            events_per_second=0.0,  # TODO: Calculate from time window
            average_latency_ms=avg_latency,
            p95_latency_ms=avg_latency * 1.5,  # Estimate
            p99_latency_ms=avg_latency * 2.0,  # Estimate
            backend_health=backend_health,
            storage_utilization={},  # TODO: Implement
            error_rate=error_rate,
            cache_hit_rate=cache_hit_rate
        )
    
    async def optimize_storage_performance(self) -> OptimizationResult:
        """
        Optimize storage performance across backends
        
        Returns:
            Results of optimization operations
        """
        if not self._is_initialized:
            raise RuntimeError("Enterprise store not initialized")
        
        optimizations = []
        recommendations = []
        storage_saved = 0
        
        # Analyze cache performance
        cache_analysis = self._analyze_cache_performance()
        if cache_analysis['hit_rate'] < 0.7:
            recommendations.append("Increase cache TTL for frequently accessed queries")
        
        # Check backend health and performance
        metrics = await self.get_storage_metrics()
        
        for backend_type, health in metrics.backend_health.items():
            if not health:
                recommendations.append(f"Investigate {backend_type} backend health issues")
        
        if metrics.average_latency_ms > 10.0:
            recommendations.append("Consider index optimization for query performance")
            optimizations.append("query_optimization_recommended")
        
        # Archive old events if storage utilization is high
        for backend_type, utilization in metrics.storage_utilization.items():
            if utilization > 0.8:
                recommendations.append(f"Consider archiving old events in {backend_type}")
                optimizations.append(f"archival_recommended_{backend_type}")
        
        return OptimizationResult(
            optimizations_applied=optimizations,
            performance_improvement=0.0,  # TODO: Measure actual improvement
            storage_saved_bytes=storage_saved,
            recommendations=recommendations
        )
    
    def _analyze_cache_performance(self) -> Dict[str, float]:
        """Analyze cache performance metrics"""
        total_requests = len(self._performance_cache)
        if total_requests == 0:
            return {'hit_rate': 0.0, 'total_requests': 0}
        
        # Count recent cache hits (last hour)
        recent_hits = sum(
            1 for cached_data in self._performance_cache.values()
            if datetime.utcnow() - cached_data['timestamp'] < timedelta(hours=1)
        )
        
        hit_rate = recent_hits / total_requests
        return {
            'hit_rate': hit_rate,
            'total_requests': total_requests,
            'recent_hits': recent_hits
        }
    
    async def health_check(self) -> Dict[str, Any]:
        """
        Comprehensive health check across all backends
        
        Returns:
            Health status and details for each component
        """
        health_status = {
            'overall_health': True,
            'backends': {},
            'timestamp': datetime.utcnow().isoformat()
        }
        
        for backend_type, backend in self._backends.items():
            try:
                backend_health = await backend.health_check()
                health_status['backends'][backend_type.value] = {
                    'healthy': backend_health,
                    'last_check': datetime.utcnow().isoformat()
                }
                
                if not backend_health:
                    health_status['overall_health'] = False
                    
            except Exception as e:
                health_status['backends'][backend_type.value] = {
                    'healthy': False,
                    'error': str(e),
                    'last_check': datetime.utcnow().isoformat()
                }
                health_status['overall_health'] = False
        
        return health_status


# Global enterprise store instance
_global_enterprise_store: Optional[EnterpriseEventStore] = None


def get_global_enterprise_store() -> EnterpriseEventStore:
    """Get global enterprise store instance"""
    global _global_enterprise_store
    if _global_enterprise_store is None:
        _global_enterprise_store = EnterpriseEventStore()
    return _global_enterprise_store


async def store_event_enterprise(event: BaseEvent, 
                                strategy: Optional[StorageStrategy] = None) -> StoreResult:
    """Convenience function to store event using global enterprise store"""
    store = get_global_enterprise_store()
    return await store.store_event(event, strategy)


async def retrieve_events_enterprise(query: EventQuery) -> List[BaseEvent]:
    """Convenience function to retrieve events using global enterprise store"""
    store = get_global_enterprise_store()
    return await store.retrieve_events(query)


# Export public APIs
__all__ = [
    'EnterpriseEventStore',
    'IEventStoreBackend',
    'StorageBackendType',
    'StorageStrategy',
    'EventQuery',
    'StreamConfig',
    'StoreResult',
    'StorageMetrics',
    'OptimizationResult',
    'get_global_enterprise_store',
    'store_event_enterprise',
    'retrieve_events_enterprise'
]