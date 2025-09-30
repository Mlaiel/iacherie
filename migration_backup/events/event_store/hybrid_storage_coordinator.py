"""🚀 Hybrid Storage Coordinator - IA Influencer Agent Platform
==============================================================
Module: events/event_store/hybrid_storage_coordinator.py
Author: Fahed Mlaiel (mlaiel@live.de)
==============================================================

⚠️ PROPRIÉTÉ INTELLECTUELLE EXCLUSIVE - FAHED MLAIEL ⚠️
(c) 2025 Fahed Mlaiel. Tous droits réservés.
Contact: mlaiel@live.de

🎯 HYBRID STORAGE COORDINATOR
Orchestrates multi-backend storage with intelligent routing, failover,
synchronization, and optimization for Ainflue platform events.

Key Features:
- Intelligent routing based on Ainflue business logic
- Automatic failover and load balancing
- Cross-backend synchronization and consistency
- Performance optimization and cost management
- Real-time health monitoring and alerting
- Storage tier management (hot/warm/cold)
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from enum import Enum
from dataclasses import dataclass, field
import json

from ..core.base_event import BaseEvent
from .enterprise_store_interface import (
    IEventStoreBackend, EnterpriseEventStore, StorageBackendType, StorageStrategy,
    EventQuery, StreamConfig, StoreResult, StorageMetrics, OptimizationResult
)

logger = logging.getLogger(__name__)


class StorageTier(Enum):
    """Storage tiers for lifecycle management"""
    HOT = "hot"          # 0-30 days - Frequent access
    WARM = "warm"        # 30-365 days - Occasional access
    COLD = "cold"        # 1-7 years - Archive for compliance
    FROZEN = "frozen"    # >7 years - Long-term with encryption


class RoutingRule(Enum):
    """Routing rules for different scenarios"""
    PERFORMANCE_FIRST = "performance_first"
    RELIABILITY_FIRST = "reliability_first"
    COST_OPTIMIZED = "cost_optimized"
    COMPLIANCE_REQUIRED = "compliance_required"
    ANALYTICS_OPTIMIZED = "analytics_optimized"


@dataclass
class SynchronizationStatus:
    """Status of cross-backend synchronization"""
    backend_pair: Tuple[StorageBackendType, StorageBackendType]
    last_sync_time: datetime
    events_synchronized: int
    sync_lag_seconds: float
    errors: List[str] = field(default_factory=list)
    is_healthy: bool = True


@dataclass
class FailoverConfig:
    """Configuration for failover behavior"""
    enabled: bool = True
    max_retry_attempts: int = 3
    retry_delay_seconds: float = 2.0
    failover_backends: List[StorageBackendType] = field(default_factory=list)
    circuit_breaker_threshold: int = 5
    circuit_breaker_timeout: int = 60


@dataclass
class LoadBalancingConfig:
    """Configuration for load balancing"""
    strategy: str = "round_robin"  # round_robin, weighted, least_connections
    weights: Dict[StorageBackendType, float] = field(default_factory=dict)
    health_check_interval: int = 30
    enable_sticky_sessions: bool = False


class HybridStorageCoordinator:
    """
    Coordinates multi-backend storage for Ainflue platform
    
    Manages:
    - Intelligent event routing based on business logic
    - Automatic failover and recovery
    - Cross-backend synchronization
    - Performance optimization
    - Cost management across storage tiers
    - Real-time monitoring and alerting
    """
    
    def __init__(self):
        self._backends: Dict[StorageBackendType, IEventStoreBackend] = {}
        self._backend_health: Dict[StorageBackendType, bool] = {}
        self._routing_rules: Dict[str, RoutingRule] = {}
        self._failover_config = FailoverConfig()
        self._load_balancing_config = LoadBalancingConfig()
        self._synchronization_status: List[SynchronizationStatus] = []
        self._performance_metrics: Dict[str, Any] = {}
        self._circuit_breakers: Dict[StorageBackendType, Dict[str, Any]] = {}
        self._is_initialized = False
        
        # Initialize Ainflue business routing
        self._initialize_business_routing()
    
    def _initialize_business_routing(self):
        """Initialize Ainflue-specific routing rules"""
        
        # Content lifecycle events require reliability
        content_events = [
            'content.uploaded', 'content.processed', 'content.published',
            'content.protected', 'content.distributed'
        ]
        for event_type in content_events:
            self._routing_rules[event_type] = RoutingRule.RELIABILITY_FIRST
        
        # Revenue events require compliance and reliability
        revenue_events = [
            'revenue.generated', 'payment.processed', 'payout.completed',
            'monetization.licensing.granted'
        ]
        for event_type in revenue_events:
            self._routing_rules[event_type] = RoutingRule.COMPLIANCE_REQUIRED
        
        # Analytics events prioritize analytics optimization
        analytics_events = [
            'analytics.engagement.calculated', 'analytics.performance.updated',
            'content.viewed', 'content.liked', 'content.shared'
        ]
        for event_type in analytics_events:
            self._routing_rules[event_type] = RoutingRule.ANALYTICS_OPTIMIZED
        
        # Performance events need immediate access
        performance_events = [
            'system.health.check', 'performance.alert', 'system.error'
        ]
        for event_type in performance_events:
            self._routing_rules[event_type] = RoutingRule.PERFORMANCE_FIRST
    
    async def initialize(self, backends: Dict[StorageBackendType, IEventStoreBackend]):
        """Initialize coordinator with backends"""
        
        self._backends = backends
        
        # Initialize backend health status
        for backend_type in self._backends.keys():
            self._backend_health[backend_type] = False
            self._circuit_breakers[backend_type] = {
                'failures': 0,
                'last_failure': None,
                'is_open': False
            }
        
        # Perform initial health checks
        await self._perform_health_checks()
        
        # Start background tasks
        asyncio.create_task(self._health_monitor_task())
        asyncio.create_task(self._synchronization_task())
        asyncio.create_task(self._optimization_task())
        
        self._is_initialized = True
        logger.info("Hybrid Storage Coordinator initialized successfully")
    
    async def store_event_coordinated(self, event: BaseEvent) -> StoreResult:
        """Store event with coordinated multi-backend strategy"""
        
        if not self._is_initialized:
            raise RuntimeError("Coordinator not initialized")
        
        # Determine routing strategy
        routing_rule = self._get_routing_rule(event)
        target_backends = self._get_target_backends(event, routing_rule)
        
        # Execute storage with coordination
        return await self._execute_coordinated_storage(event, target_backends, routing_rule)
    
    def _get_routing_rule(self, event: BaseEvent) -> RoutingRule:
        """Get routing rule for event based on business logic"""
        
        # Check explicit rules first
        if event.event_type in self._routing_rules:
            return self._routing_rules[event.event_type]
        
        # Check event priority
        if hasattr(event, 'priority'):
            priority_str = str(getattr(event, 'priority', '')).upper()
            if 'CRITICAL' in priority_str:
                return RoutingRule.RELIABILITY_FIRST
            elif 'HIGH' in priority_str:
                return RoutingRule.PERFORMANCE_FIRST
        
        # Check for business context
        if event.data:
            data = event.data
            
            # Revenue events need compliance
            if 'revenue' in str(data) or 'payment' in str(data):
                return RoutingRule.COMPLIANCE_REQUIRED
            
            # Analytics events need analytics optimization
            if 'analytics' in event.event_type or 'metrics' in event.event_type:
                return RoutingRule.ANALYTICS_OPTIMIZED
            
            # Large files need cost optimization
            if data.get('file_size', 0) > 100_000_000:  # >100MB
                return RoutingRule.COST_OPTIMIZED
        
        # Default to performance first
        return RoutingRule.PERFORMANCE_FIRST
    
    def _get_target_backends(self, event: BaseEvent, 
                           routing_rule: RoutingRule) -> List[StorageBackendType]:
        """Get target backends based on routing rule"""
        
        # Filter healthy backends
        healthy_backends = [
            backend_type for backend_type, is_healthy in self._backend_health.items()
            if is_healthy and not self._is_circuit_breaker_open(backend_type)
        ]
        
        if not healthy_backends:
            # Emergency: use any available backend
            return list(self._backends.keys())
        
        # Apply routing rule
        if routing_rule == RoutingRule.PERFORMANCE_FIRST:
            # Prefer fast backends (PostgreSQL, Redis)
            preferred = [StorageBackendType.POSTGRESQL, StorageBackendType.REDIS]
            return [b for b in preferred if b in healthy_backends] or healthy_backends[:1]
        
        elif routing_rule == RoutingRule.RELIABILITY_FIRST:
            # Use multiple backends for redundancy
            preferred = [StorageBackendType.POSTGRESQL, StorageBackendType.MONGODB]
            return [b for b in preferred if b in healthy_backends]
        
        elif routing_rule == RoutingRule.COMPLIANCE_REQUIRED:
            # Use ACID-compliant backends
            preferred = [StorageBackendType.POSTGRESQL]
            return [b for b in preferred if b in healthy_backends] or healthy_backends[:1]
        
        elif routing_rule == RoutingRule.ANALYTICS_OPTIMIZED:
            # Use analytics-friendly backends
            preferred = [StorageBackendType.MONGODB, StorageBackendType.ELASTICSEARCH]
            return [b for b in preferred if b in healthy_backends]
        
        elif routing_rule == RoutingRule.COST_OPTIMIZED:
            # Use cost-effective backends
            preferred = [StorageBackendType.MONGODB]
            return [b for b in preferred if b in healthy_backends] or healthy_backends[:1]
        
        # Default: use first healthy backend
        return healthy_backends[:1]
    
    async def _execute_coordinated_storage(self, event: BaseEvent,
                                         target_backends: List[StorageBackendType],
                                         routing_rule: RoutingRule) -> StoreResult:
        """Execute storage across multiple backends with coordination"""
        
        start_time = datetime.utcnow()
        results = []
        used_backends = []
        errors = []
        
        # Execute storage in parallel or sequential based on rule
        if routing_rule == RoutingRule.PERFORMANCE_FIRST:
            # Sequential for fastest response
            for backend_type in target_backends:
                result = await self._store_with_failover(event, backend_type)
                if result.success:
                    used_backends.append(backend_type)
                    results.append(result)
                    break  # Stop after first success for performance
                else:
                    errors.extend(result.errors)
        
        else:
            # Parallel for reliability/compliance
            tasks = []
            for backend_type in target_backends:
                task = asyncio.create_task(
                    self._store_with_failover(event, backend_type)
                )
                tasks.append((backend_type, task))
            
            # Wait for all tasks
            for backend_type, task in tasks:
                try:
                    result = await task
                    if result.success:
                        used_backends.append(backend_type)
                        results.append(result)
                    else:
                        errors.extend(result.errors)
                except Exception as e:
                    errors.append(f"{backend_type}: {str(e)}")
        
        # Calculate overall metrics
        latency = (datetime.utcnow() - start_time).total_seconds() * 1000
        success = len(used_backends) > 0
        
        # Schedule asynchronous synchronization if needed
        if len(used_backends) > 1:
            asyncio.create_task(
                self._schedule_synchronization(event, used_backends)
            )
        
        return StoreResult(
            success=success,
            event_id=event.event_id,
            backends_used=used_backends,
            latency_ms=latency,
            errors=errors,
            metadata={
                'routing_rule': routing_rule.value,
                'coordination_strategy': 'hybrid',
                'parallel_storage': len(target_backends) > 1
            }
        )
    
    async def _store_with_failover(self, event: BaseEvent,
                                 backend_type: StorageBackendType) -> StoreResult:
        """Store event with failover logic"""
        
        if backend_type not in self._backends:
            return StoreResult(
                success=False,
                event_id=event.event_id,
                backends_used=[],
                latency_ms=0,
                errors=[f"Backend {backend_type} not available"]
            )
        
        backend = self._backends[backend_type]
        
        # Check circuit breaker
        if self._is_circuit_breaker_open(backend_type):
            return StoreResult(
                success=False,
                event_id=event.event_id,
                backends_used=[],
                latency_ms=0,
                errors=[f"Circuit breaker open for {backend_type}"]
            )
        
        # Attempt storage with retries
        for attempt in range(self._failover_config.max_retry_attempts):
            try:
                result = await backend.store_event(event)
                
                if result.success:
                    # Reset circuit breaker on success
                    self._reset_circuit_breaker(backend_type)
                    return result
                else:
                    # Record failure
                    self._record_failure(backend_type)
                    
                    if attempt < self._failover_config.max_retry_attempts - 1:
                        await asyncio.sleep(self._failover_config.retry_delay_seconds)
                    
            except Exception as e:
                self._record_failure(backend_type)
                logger.error(f"Storage attempt {attempt + 1} failed for {backend_type}: {e}")
                
                if attempt < self._failover_config.max_retry_attempts - 1:
                    await asyncio.sleep(self._failover_config.retry_delay_seconds)
        
        return StoreResult(
            success=False,
            event_id=event.event_id,
            backends_used=[],
            latency_ms=0,
            errors=[f"All retry attempts failed for {backend_type}"]
        )
    
    def _is_circuit_breaker_open(self, backend_type: StorageBackendType) -> bool:
        """Check if circuit breaker is open for backend"""
        
        if backend_type not in self._circuit_breakers:
            return False
        
        breaker = self._circuit_breakers[backend_type]
        
        if not breaker['is_open']:
            return False
        
        # Check if timeout has passed
        if breaker['last_failure']:
            timeout_passed = (
                datetime.utcnow() - breaker['last_failure']
            ).total_seconds() > self._failover_config.circuit_breaker_timeout
            
            if timeout_passed:
                breaker['is_open'] = False
                breaker['failures'] = 0
                logger.info(f"Circuit breaker reset for {backend_type}")
                return False
        
        return True
    
    def _record_failure(self, backend_type: StorageBackendType):
        """Record failure and update circuit breaker"""
        
        if backend_type not in self._circuit_breakers:
            self._circuit_breakers[backend_type] = {
                'failures': 0,
                'last_failure': None,
                'is_open': False
            }
        
        breaker = self._circuit_breakers[backend_type]
        breaker['failures'] += 1
        breaker['last_failure'] = datetime.utcnow()
        
        # Open circuit breaker if threshold exceeded
        if breaker['failures'] >= self._failover_config.circuit_breaker_threshold:
            breaker['is_open'] = True
            logger.warning(f"Circuit breaker opened for {backend_type}")
    
    def _reset_circuit_breaker(self, backend_type: StorageBackendType):
        """Reset circuit breaker on success"""
        
        if backend_type in self._circuit_breakers:
            self._circuit_breakers[backend_type].update({
                'failures': 0,
                'last_failure': None,
                'is_open': False
            })
    
    async def _schedule_synchronization(self, event: BaseEvent,
                                      backends: List[StorageBackendType]):
        """Schedule asynchronous synchronization between backends"""
        
        # This is a simplified implementation
        # In production, implement proper sync queues and conflict resolution
        logger.info(f"Scheduling synchronization for event {event.event_id} across {backends}")
    
    async def retrieve_events_coordinated(self, query: EventQuery) -> List[BaseEvent]:
        """Retrieve events with coordinated query optimization"""
        
        # Select optimal backend for query
        optimal_backend = self._select_optimal_query_backend(query)
        
        if optimal_backend and optimal_backend in self._backends:
            try:
                backend = self._backends[optimal_backend]
                return await backend.retrieve_events(query)
            except Exception as e:
                logger.error(f"Query failed on {optimal_backend}: {e}")
        
        # Fallback: try other backends
        for backend_type, backend in self._backends.items():
            if backend_type != optimal_backend and self._backend_health.get(backend_type, False):
                try:
                    return await backend.retrieve_events(query)
                except Exception as e:
                    logger.error(f"Fallback query failed on {backend_type}: {e}")
        
        raise RuntimeError("All backends failed for query")
    
    def _select_optimal_query_backend(self, query: EventQuery) -> Optional[StorageBackendType]:
        """Select optimal backend for query based on characteristics"""
        
        # Analytics queries → MongoDB
        if query.event_types:
            analytics_patterns = ['analytics', 'metrics', 'engagement']
            if any(pattern in event_type for event_type in query.event_types 
                   for pattern in analytics_patterns):
                return StorageBackendType.MONGODB
        
        # Recent transactional queries → PostgreSQL
        if query.is_recent() and query.is_transactional():
            return StorageBackendType.POSTGRESQL
        
        # Text search → Elasticsearch
        if hasattr(query, 'search_text') and getattr(query, 'search_text'):
            return StorageBackendType.ELASTICSEARCH
        
        # Default to PostgreSQL for reliability
        return StorageBackendType.POSTGRESQL
    
    async def _perform_health_checks(self):
        """Perform health checks on all backends"""
        
        for backend_type, backend in self._backends.items():
            try:
                health = await backend.health_check()
                self._backend_health[backend_type] = health
                
                if health:
                    logger.info(f"Backend {backend_type} is healthy")
                else:
                    logger.warning(f"Backend {backend_type} is unhealthy")
                    
            except Exception as e:
                logger.error(f"Health check failed for {backend_type}: {e}")
                self._backend_health[backend_type] = False
    
    async def _health_monitor_task(self):
        """Background task for continuous health monitoring"""
        
        while self._is_initialized:
            try:
                await self._perform_health_checks()
                await asyncio.sleep(self._load_balancing_config.health_check_interval)
            except Exception as e:
                logger.error(f"Health monitoring task error: {e}")
                await asyncio.sleep(10)  # Shorter retry interval on error
    
    async def _synchronization_task(self):
        """Background task for cross-backend synchronization"""
        
        while self._is_initialized:
            try:
                await self._perform_synchronization_check()
                await asyncio.sleep(60)  # Check every minute
            except Exception as e:
                logger.error(f"Synchronization task error: {e}")
                await asyncio.sleep(30)  # Shorter retry on error
    
    async def _perform_synchronization_check(self):
        """Check synchronization status between backends"""
        
        # Simplified implementation - check event counts and timestamps
        # In production, implement proper sync comparison
        
        healthy_backends = [
            backend_type for backend_type, is_healthy in self._backend_health.items()
            if is_healthy
        ]
        
        for i, backend1 in enumerate(healthy_backends):
            for backend2 in healthy_backends[i+1:]:
                try:
                    # Compare recent event counts (last hour)
                    recent_query = EventQuery(
                        start_time=datetime.utcnow() - timedelta(hours=1),
                        limit=1000
                    )
                    
                    events1 = await self._backends[backend1].retrieve_events(recent_query)
                    events2 = await self._backends[backend2].retrieve_events(recent_query)
                    
                    sync_status = SynchronizationStatus(
                        backend_pair=(backend1, backend2),
                        last_sync_time=datetime.utcnow(),
                        events_synchronized=min(len(events1), len(events2)),
                        sync_lag_seconds=abs(len(events1) - len(events2)),
                        is_healthy=abs(len(events1) - len(events2)) < 10
                    )
                    
                    # Update synchronization status
                    existing_status = next(
                        (s for s in self._synchronization_status 
                         if s.backend_pair == (backend1, backend2) or 
                            s.backend_pair == (backend2, backend1)),
                        None
                    )
                    
                    if existing_status:
                        existing_status.last_sync_time = sync_status.last_sync_time
                        existing_status.events_synchronized = sync_status.events_synchronized
                        existing_status.sync_lag_seconds = sync_status.sync_lag_seconds
                        existing_status.is_healthy = sync_status.is_healthy
                    else:
                        self._synchronization_status.append(sync_status)
                    
                    if not sync_status.is_healthy:
                        logger.warning(
                            f"Synchronization lag detected between {backend1} and {backend2}: "
                            f"{sync_status.sync_lag_seconds} events"
                        )
                    
                except Exception as e:
                    logger.error(f"Synchronization check failed for {backend1}-{backend2}: {e}")
    
    async def _optimization_task(self):
        """Background task for performance optimization"""
        
        while self._is_initialized:
            try:
                await self._perform_optimization_analysis()
                await asyncio.sleep(300)  # Optimize every 5 minutes
            except Exception as e:
                logger.error(f"Optimization task error: {e}")
                await asyncio.sleep(60)
    
    async def _perform_optimization_analysis(self):
        """Analyze performance and suggest optimizations"""
        
        # Collect metrics from all backends
        backend_metrics = {}
        for backend_type, backend in self._backends.items():
            try:
                metrics = await backend.get_metrics()
                backend_metrics[backend_type] = metrics
            except Exception as e:
                logger.error(f"Failed to get metrics from {backend_type}: {e}")
        
        # Analyze and optimize
        optimizations = []
        
        # Check for performance issues
        for backend_type, metrics in backend_metrics.items():
            avg_latency = metrics.get('average_latency_ms', 0)
            error_rate = metrics.get('error_rate', 0)
            
            if avg_latency > 100:  # >100ms average latency
                optimizations.append(f"High latency detected in {backend_type}: {avg_latency}ms")
            
            if error_rate > 0.01:  # >1% error rate
                optimizations.append(f"High error rate in {backend_type}: {error_rate:.2%}")
        
        # Log optimization recommendations
        if optimizations:
            logger.info(f"Performance optimizations recommended: {optimizations}")
    
    async def get_coordination_metrics(self) -> Dict[str, Any]:
        """Get comprehensive coordination metrics"""
        
        # Backend health summary
        health_summary = {
            'healthy_backends': sum(1 for h in self._backend_health.values() if h),
            'total_backends': len(self._backend_health),
            'backend_status': dict(self._backend_health)
        }
        
        # Circuit breaker status
        circuit_breaker_summary = {
            backend_type: {
                'is_open': breaker['is_open'],
                'failures': breaker['failures']
            }
            for backend_type, breaker in self._circuit_breakers.items()
        }
        
        # Synchronization summary
        sync_summary = {
            'sync_pairs': len(self._synchronization_status),
            'healthy_sync_pairs': sum(1 for s in self._synchronization_status if s.is_healthy),
            'max_sync_lag': max(
                (s.sync_lag_seconds for s in self._synchronization_status),
                default=0
            )
        }
        
        return {
            'coordinator_status': 'healthy' if self._is_initialized else 'not_initialized',
            'health_summary': health_summary,
            'circuit_breakers': circuit_breaker_summary,
            'synchronization': sync_summary,
            'routing_rules': len(self._routing_rules),
            'timestamp': datetime.utcnow().isoformat()
        }
    
    async def optimize_coordination(self) -> OptimizationResult:
        """Optimize coordination performance"""
        
        optimizations = []
        recommendations = []
        
        # Analyze backend performance
        metrics = await self.get_coordination_metrics()
        
        # Check health
        health_summary = metrics['health_summary']
        if health_summary['healthy_backends'] < health_summary['total_backends']:
            recommendations.append("Some backends are unhealthy - check backend configuration")
        
        # Check synchronization
        sync_summary = metrics['synchronization']
        if sync_summary['max_sync_lag'] > 50:
            recommendations.append("High synchronization lag detected - consider optimization")
            optimizations.append("sync_optimization_recommended")
        
        # Check circuit breakers
        open_breakers = [
            backend for backend, status in metrics['circuit_breakers'].items()
            if status['is_open']
        ]
        if open_breakers:
            recommendations.append(f"Circuit breakers open for: {open_breakers}")
        
        return OptimizationResult(
            optimizations_applied=optimizations,
            performance_improvement=0.0,  # Would measure actual improvement
            storage_saved_bytes=0,
            recommendations=recommendations
        )


# Export public APIs
__all__ = [
    'HybridStorageCoordinator',
    'StorageTier',
    'RoutingRule',
    'SynchronizationStatus',
    'FailoverConfig',
    'LoadBalancingConfig'
]