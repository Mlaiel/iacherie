#!/usr/bin/env python3
"""Pool Failover - High Availability and Recovery Management
===========================================================

Automated failover mechanisms, circuit breaker patterns, and recovery strategies
for all database pools in the IA Influencer Agent + Content Protection Platform.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.
Contact: mlaiel@live.de for licensing inquiries.
"""

import asyncio
import logging
from typing import Dict, Any, Optional, List, Union, Callable
from dataclasses import dataclass, field
from datetime import datetime, timezone, timedelta
from enum import Enum
import time

logger = logging.getLogger(__name__)

class FailoverState(Enum):
    """Failover system states"""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    FAILING = "failing"
    FAILED = "failed"
    RECOVERING = "recovering"

class CircuitState(Enum):
    """Circuit breaker states"""
    CLOSED = "closed"      # Normal operation
    OPEN = "open"          # Failing fast
    HALF_OPEN = "half_open"  # Testing recovery

class RecoveryStrategy(Enum):
    """Recovery strategies"""
    IMMEDIATE = "immediate"
    GRADUAL = "gradual"
    EXPONENTIAL_BACKOFF = "exponential_backoff"
    MANUAL = "manual"

@dataclass
class FailoverConfig:
    """Failover configuration for a pool"""
    pool_id: str
    primary_endpoint: str
    secondary_endpoints: List[str] = field(default_factory=list)
    health_check_interval: float = 10.0
    failure_threshold: int = 3
    recovery_threshold: int = 2
    timeout_seconds: float = 5.0
    circuit_breaker_enabled: bool = True
    recovery_strategy: RecoveryStrategy = RecoveryStrategy.GRADUAL
    auto_failback: bool = True
    failback_delay_seconds: float = 30.0

@dataclass
class FailoverEvent:
    """Failover event record"""
    event_id: str
    pool_id: str
    event_type: str  # failover, failback, recovery_attempt
    from_endpoint: str
    to_endpoint: str
    triggered_at: datetime
    completed_at: Optional[datetime] = None
    success: bool = False
    error_message: str = ""
    duration_ms: float = 0.0

@dataclass
class CircuitBreakerState:
    """Circuit breaker state tracking"""
    pool_id: str
    endpoint: str
    state: CircuitState = CircuitState.CLOSED
    failure_count: int = 0
    success_count: int = 0
    last_failure_time: Optional[datetime] = None
    last_success_time: Optional[datetime] = None
    opened_at: Optional[datetime] = None
    next_attempt_time: Optional[datetime] = None

class CircuitBreaker:
    """Circuit breaker implementation for database connections"""
    
    def __init__(self, pool_id: str, endpoint: str, config: FailoverConfig):
        self.pool_id = pool_id
        self.endpoint = endpoint
        self.config = config
        self.state = CircuitBreakerState(pool_id, endpoint)
        self._lock = asyncio.Lock()
        
        logger.debug(f"🔄 Circuit breaker created for {pool_id}:{endpoint}")

    async def call(self, func: Callable, *args, **kwargs):
        """Execute function with circuit breaker protection"""
        async with self._lock:
            # Check if circuit is open
            if self.state.state == CircuitState.OPEN:
                if self._should_attempt_reset():
                    self.state.state = CircuitState.HALF_OPEN
                    logger.info(f"🔄 Circuit breaker half-open for {self.pool_id}:{self.endpoint}")
                else:
                    raise Exception(f"Circuit breaker open for {self.pool_id}:{self.endpoint}")
            
            try:
                # Execute the function
                start_time = time.time()
                result = await asyncio.wait_for(
                    func(*args, **kwargs), 
                    timeout=self.config.timeout_seconds
                )
                duration = (time.time() - start_time) * 1000
                
                # Record success
                await self._record_success()
                
                logger.debug(f"✅ Circuit breaker success for {self.pool_id}:{self.endpoint} ({duration:.1f}ms)")
                return result
                
            except Exception as e:
                # Record failure
                await self._record_failure(str(e))
                logger.error(f"❌ Circuit breaker failure for {self.pool_id}:{self.endpoint}: {e}")
                raise

    def _should_attempt_reset(self) -> bool:
        """Check if circuit should attempt reset"""
        if not self.state.opened_at:
            return True
        
        # Use exponential backoff for reset attempts
        time_since_open = datetime.now(timezone.utc) - self.state.opened_at
        min_wait_time = timedelta(seconds=5 * (2 ** min(self.state.failure_count, 6)))  # Cap at 320 seconds
        
        return time_since_open > min_wait_time

    async def _record_success(self):
        """Record successful operation"""
        self.state.success_count += 1
        self.state.last_success_time = datetime.now(timezone.utc)
        
        if self.state.state == CircuitState.HALF_OPEN:
            if self.state.success_count >= self.config.recovery_threshold:
                self.state.state = CircuitState.CLOSED
                self.state.failure_count = 0
                self.state.opened_at = None
                logger.info(f"✅ Circuit breaker closed for {self.pool_id}:{self.endpoint}")

    async def _record_failure(self, error: str):
        """Record failed operation"""
        self.state.failure_count += 1
        self.state.last_failure_time = datetime.now(timezone.utc)
        
        if self.state.failure_count >= self.config.failure_threshold:
            if self.state.state != CircuitState.OPEN:
                self.state.state = CircuitState.OPEN
                self.state.opened_at = datetime.now(timezone.utc)
                self.state.success_count = 0
                logger.warning(f"⚠️ Circuit breaker opened for {self.pool_id}:{self.endpoint}")

class FailoverManager:
    """Manages failover for a specific database pool"""
    
    def __init__(self, config: FailoverConfig):
        self.config = config
        self.current_endpoint = config.primary_endpoint
        self.state = FailoverState.HEALTHY
        self.circuit_breakers: Dict[str, CircuitBreaker] = {}
        self.failover_history: List[FailoverEvent] = []
        self._health_check_task: Optional[asyncio.Task] = None
        self._recovery_task: Optional[asyncio.Task] = None
        self._lock = asyncio.Lock()
        
        # Initialize circuit breakers
        if config.circuit_breaker_enabled:
            self._initialize_circuit_breakers()
        
        logger.info(f"🛡️ Failover manager created for pool {config.pool_id}")

    def _initialize_circuit_breakers(self):
        """Initialize circuit breakers for all endpoints"""
        all_endpoints = [self.config.primary_endpoint] + self.config.secondary_endpoints
        
        for endpoint in all_endpoints:
            self.circuit_breakers[endpoint] = CircuitBreaker(
                self.config.pool_id, endpoint, self.config
            )

    async def start_monitoring(self):
        """Start health monitoring and failover detection"""
        if self._health_check_task and not self._health_check_task.done():
            logger.warning(f"Health monitoring already running for {self.config.pool_id}")
            return
        
        self._health_check_task = asyncio.create_task(self._health_check_loop())
        logger.info(f"🔄 Health monitoring started for {self.config.pool_id}")

    async def stop_monitoring(self):
        """Stop health monitoring"""
        if self._health_check_task:
            self._health_check_task.cancel()
            try:
                await self._health_check_task
            except asyncio.CancelledError:
                pass
            self._health_check_task = None
        
        if self._recovery_task:
            self._recovery_task.cancel()
            try:
                await self._recovery_task
            except asyncio.CancelledError:
                pass
            self._recovery_task = None
        
        logger.info(f"⏹️ Health monitoring stopped for {self.config.pool_id}")

    async def _health_check_loop(self):
        """Main health check loop"""
        while True:
            try:
                await asyncio.sleep(self.config.health_check_interval)
                await self._perform_health_checks()
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"❌ Health check loop error for {self.config.pool_id}: {e}")

    async def _perform_health_checks(self):
        """Perform health checks on all endpoints"""
        current_healthy = await self._check_endpoint_health(self.current_endpoint)
        
        if not current_healthy and self.state != FailoverState.FAILED:
            logger.warning(f"⚠️ Current endpoint unhealthy: {self.current_endpoint}")
            await self._attempt_failover()
        
        elif current_healthy and self.state == FailoverState.FAILED:
            if self.config.auto_failback and self.current_endpoint != self.config.primary_endpoint:
                # Check if primary is healthy for failback
                primary_healthy = await self._check_endpoint_health(self.config.primary_endpoint)
                if primary_healthy:
                    await self._attempt_failback()

    async def _check_endpoint_health(self, endpoint: str) -> bool:
        """Check health of a specific endpoint"""
        try:
            if self.config.circuit_breaker_enabled and endpoint in self.circuit_breakers:
                circuit_breaker = self.circuit_breakers[endpoint]
                
                # Use circuit breaker for health check
                await circuit_breaker.call(self._mock_health_check, endpoint)
                return True
            else:
                # Direct health check
                await self._mock_health_check(endpoint)
                return True
                
        except Exception as e:
            logger.debug(f"Health check failed for {endpoint}: {e}")
            return False

    async def _mock_health_check(self, endpoint: str):
        """Mock health check implementation"""
        # In real implementation, this would actually connect to the database
        await asyncio.sleep(0.1)  # Simulate network delay
        
        # Simulate occasional failures for testing
        import random
        if random.random() < 0.1:  # 10% failure rate
            raise Exception(f"Mock health check failure for {endpoint}")

    async def _attempt_failover(self):
        """Attempt to failover to a healthy secondary endpoint"""
        async with self._lock:
            if self.state == FailoverState.FAILED:
                return  # Already failed over
            
            logger.warning(f"🔄 Attempting failover for {self.config.pool_id}")
            self.state = FailoverState.FAILING
            
            # Try secondary endpoints
            for secondary in self.config.secondary_endpoints:
                if await self._check_endpoint_health(secondary):
                    await self._execute_failover(secondary)
                    return
            
            # No healthy endpoints found
            logger.error(f"❌ No healthy endpoints available for {self.config.pool_id}")
            self.state = FailoverState.FAILED
            
            # Start recovery attempts
            if not self._recovery_task or self._recovery_task.done():
                self._recovery_task = asyncio.create_task(self._recovery_loop())

    async def _execute_failover(self, new_endpoint: str):
        """Execute failover to new endpoint"""
        start_time = time.time()
        old_endpoint = self.current_endpoint
        
        try:
            # Record failover event
            event = FailoverEvent(
                event_id=f"failover_{int(time.time())}",
                pool_id=self.config.pool_id,
                event_type="failover",
                from_endpoint=old_endpoint,
                to_endpoint=new_endpoint,
                triggered_at=datetime.now(timezone.utc)
            )
            
            # Switch to new endpoint
            self.current_endpoint = new_endpoint
            self.state = FailoverState.DEGRADED
            
            # Complete event record
            event.completed_at = datetime.now(timezone.utc)
            event.success = True
            event.duration_ms = (time.time() - start_time) * 1000
            
            self.failover_history.append(event)
            
            logger.info(f"✅ Failover completed: {old_endpoint} → {new_endpoint} ({event.duration_ms:.1f}ms)")
            
        except Exception as e:
            # Record failed failover
            event.completed_at = datetime.now(timezone.utc)
            event.success = False
            event.error_message = str(e)
            event.duration_ms = (time.time() - start_time) * 1000
            
            self.failover_history.append(event)
            
            logger.error(f"❌ Failover failed: {old_endpoint} → {new_endpoint}: {e}")
            self.state = FailoverState.FAILED

    async def _attempt_failback(self):
        """Attempt to failback to primary endpoint"""
        if self.current_endpoint == self.config.primary_endpoint:
            return
        
        logger.info(f"🔙 Attempting failback to primary for {self.config.pool_id}")
        
        # Wait for failback delay
        await asyncio.sleep(self.config.failback_delay_seconds)
        
        # Double-check primary health
        if await self._check_endpoint_health(self.config.primary_endpoint):
            await self._execute_failback()

    async def _execute_failback(self):
        """Execute failback to primary endpoint"""
        start_time = time.time()
        old_endpoint = self.current_endpoint
        
        try:
            # Record failback event
            event = FailoverEvent(
                event_id=f"failback_{int(time.time())}",
                pool_id=self.config.pool_id,
                event_type="failback",
                from_endpoint=old_endpoint,
                to_endpoint=self.config.primary_endpoint,
                triggered_at=datetime.now(timezone.utc)
            )
            
            # Switch back to primary
            self.current_endpoint = self.config.primary_endpoint
            self.state = FailoverState.HEALTHY
            
            # Complete event record
            event.completed_at = datetime.now(timezone.utc)
            event.success = True
            event.duration_ms = (time.time() - start_time) * 1000
            
            self.failover_history.append(event)
            
            logger.info(f"✅ Failback completed: {old_endpoint} → {self.config.primary_endpoint} ({event.duration_ms:.1f}ms)")
            
        except Exception as e:
            # Record failed failback
            event.completed_at = datetime.now(timezone.utc)
            event.success = False
            event.error_message = str(e)
            event.duration_ms = (time.time() - start_time) * 1000
            
            self.failover_history.append(event)
            
            logger.error(f"❌ Failback failed: {old_endpoint} → {self.config.primary_endpoint}: {e}")

    async def _recovery_loop(self):
        """Recovery loop for failed pools"""
        attempt = 0
        
        while self.state == FailoverState.FAILED:
            try:
                attempt += 1
                logger.info(f"🔄 Recovery attempt #{attempt} for {self.config.pool_id}")
                
                # Try all endpoints again
                all_endpoints = [self.config.primary_endpoint] + self.config.secondary_endpoints
                
                for endpoint in all_endpoints:
                    if await self._check_endpoint_health(endpoint):
                        await self._execute_recovery(endpoint)
                        return
                
                # No endpoints healthy, wait before next attempt
                if self.config.recovery_strategy == RecoveryStrategy.EXPONENTIAL_BACKOFF:
                    wait_time = min(60, 5 * (2 ** min(attempt, 6)))  # Cap at 60 seconds
                else:
                    wait_time = 10
                
                logger.info(f"⏳ Waiting {wait_time}s before next recovery attempt")
                await asyncio.sleep(wait_time)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"❌ Recovery attempt error: {e}")
                await asyncio.sleep(10)

    async def _execute_recovery(self, endpoint: str):
        """Execute recovery to healthy endpoint"""
        start_time = time.time()
        
        try:
            # Record recovery event
            event = FailoverEvent(
                event_id=f"recovery_{int(time.time())}",
                pool_id=self.config.pool_id,
                event_type="recovery",
                from_endpoint="failed",
                to_endpoint=endpoint,
                triggered_at=datetime.now(timezone.utc)
            )
            
            # Switch to healthy endpoint
            self.current_endpoint = endpoint
            self.state = FailoverState.RECOVERING if endpoint != self.config.primary_endpoint else FailoverState.HEALTHY
            
            # Complete event record
            event.completed_at = datetime.now(timezone.utc)
            event.success = True
            event.duration_ms = (time.time() - start_time) * 1000
            
            self.failover_history.append(event)
            
            logger.info(f"✅ Recovery completed: failed → {endpoint} ({event.duration_ms:.1f}ms)")
            
        except Exception as e:
            # Record failed recovery
            event.completed_at = datetime.now(timezone.utc)
            event.success = False
            event.error_message = str(e)
            event.duration_ms = (time.time() - start_time) * 1000
            
            self.failover_history.append(event)
            
            logger.error(f"❌ Recovery failed: failed → {endpoint}: {e}")

    def get_status(self) -> Dict[str, Any]:
        """Get current failover status"""
        circuit_status = {}
        if self.config.circuit_breaker_enabled:
            circuit_status = {
                endpoint: {
                    'state': cb.state.state.value,
                    'failure_count': cb.state.failure_count,
                    'success_count': cb.state.success_count,
                    'last_failure': cb.state.last_failure_time.isoformat() if cb.state.last_failure_time else None
                }
                for endpoint, cb in self.circuit_breakers.items()
            }
        
        return {
            'pool_id': self.config.pool_id,
            'state': self.state.value,
            'current_endpoint': self.current_endpoint,
            'primary_endpoint': self.config.primary_endpoint,
            'secondary_endpoints': self.config.secondary_endpoints,
            'monitoring_active': self._health_check_task is not None and not self._health_check_task.done(),
            'circuit_breakers': circuit_status,
            'recent_events': [
                {
                    'event_type': event.event_type,
                    'from_endpoint': event.from_endpoint,
                    'to_endpoint': event.to_endpoint,
                    'triggered_at': event.triggered_at.isoformat(),
                    'success': event.success,
                    'duration_ms': event.duration_ms
                }
                for event in self.failover_history[-5:]  # Last 5 events
            ]
        }

class PoolFailoverManager:
    """Central failover manager for all database pools"""
    
    def __init__(self):
        self.failover_managers: Dict[str, FailoverManager] = {}
        self._initialized = False
        
        logger.info("🛡️ Pool Failover Manager initialized")

    async def register_pool(self, config: FailoverConfig):
        """Register a pool for failover management"""
        if config.pool_id in self.failover_managers:
            logger.warning(f"Pool {config.pool_id} already registered for failover")
            return
        
        manager = FailoverManager(config)
        self.failover_managers[config.pool_id] = manager
        
        # Start monitoring if we're already initialized
        if self._initialized:
            await manager.start_monitoring()
        
        logger.info(f"✅ Pool {config.pool_id} registered for failover")

    async def start_all_monitoring(self):
        """Start monitoring for all registered pools"""
        for manager in self.failover_managers.values():
            await manager.start_monitoring()
        
        self._initialized = True
        logger.info("🔄 Failover monitoring started for all pools")

    async def stop_all_monitoring(self):
        """Stop monitoring for all pools"""
        for manager in self.failover_managers.values():
            await manager.stop_monitoring()
        
        self._initialized = False
        logger.info("⏹️ Failover monitoring stopped for all pools")

    def get_pool_status(self, pool_id: str) -> Optional[Dict[str, Any]]:
        """Get failover status for a specific pool"""
        manager = self.failover_managers.get(pool_id)
        return manager.get_status() if manager else None

    def get_all_status(self) -> Dict[str, Dict[str, Any]]:
        """Get failover status for all pools"""
        return {
            pool_id: manager.get_status()
            for pool_id, manager in self.failover_managers.items()
        }

    def get_summary(self) -> Dict[str, Any]:
        """Get failover system summary"""
        total_pools = len(self.failover_managers)
        healthy_pools = sum(
            1 for manager in self.failover_managers.values()
            if manager.state == FailoverState.HEALTHY
        )
        failed_pools = sum(
            1 for manager in self.failover_managers.values()
            if manager.state == FailoverState.FAILED
        )
        
        return {
            'total_pools': total_pools,
            'healthy_pools': healthy_pools,
            'degraded_pools': total_pools - healthy_pools - failed_pools,
            'failed_pools': failed_pools,
            'monitoring_active': self._initialized,
            'pool_states': {
                pool_id: manager.state.value
                for pool_id, manager in self.failover_managers.items()
            }
        }

# Global failover manager instance
_failover_manager: Optional[PoolFailoverManager] = None

def get_failover_manager() -> PoolFailoverManager:
    """Get the global failover manager"""
    global _failover_manager
    if _failover_manager is None:
        _failover_manager = PoolFailoverManager()
    return _failover_manager

# Export public interface
__all__ = [
    'PoolFailoverManager',
    'get_failover_manager',
    'FailoverManager',
    'CircuitBreaker',
    'FailoverConfig',
    'FailoverEvent',
    'FailoverState',
    'CircuitState',
    'RecoveryStrategy'
]