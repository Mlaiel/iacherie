#!/usr/bin/env python3
"""
Enterprise Load Balancer Controller Service
Dynamic load balancing and traffic distribution for microservices architecture

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️ STRICT COPYRIGHT WARNING ⚠️
This implementation is proprietary and confidential. Unauthorized use, reproduction,
distribution, or modification without written permission from Fahed Mlaiel
(mlaiel@live.de) is strictly prohibited and will be prosecuted to the full extent
of the law. All rights reserved.
"""

import asyncio
import time
import logging
import random
import hashlib
from typing import Dict, Any, Optional, List, Callable, Awaitable, Set, Union, Tuple
from dataclasses import dataclass, field
from enum import Enum
import threading
from datetime import datetime, timedelta
import aiohttp
import json
from collections import defaultdict
import heapq

logger = logging.getLogger(__name__)

class LoadBalancingAlgorithm(Enum):
    """Load balancing algorithm enumeration"""
    ROUND_ROBIN = "round_robin"
    WEIGHTED_ROUND_ROBIN = "weighted_round_robin"
    LEAST_CONNECTIONS = "least_connections"
    WEIGHTED_LEAST_CONNECTIONS = "weighted_least_connections"
    LEAST_RESPONSE_TIME = "least_response_time"
    WEIGHTED_RESPONSE_TIME = "weighted_response_time"
    CONSISTENT_HASH = "consistent_hash"
    RANDOM = "random"
    WEIGHTED_RANDOM = "weighted_random"
    IP_HASH = "ip_hash"
    GEOGRAPHIC = "geographic"
    HEALTH_BASED = "health_based"

class BackendState(Enum):
    """Backend server state"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    DRAINING = "draining"
    MAINTENANCE = "maintenance"
    FAILED = "failed"

class RequestPriority(Enum):
    """Request priority levels"""
    LOW = 1
    NORMAL = 2
    HIGH = 3
    CRITICAL = 4

@dataclass
class Backend:
    """Backend server configuration"""
    id: str
    endpoint: str
    weight: int = 100
    max_connections: int = 1000
    current_connections: int = 0
    state: BackendState = BackendState.ACTIVE
    region: str = "default"
    zone: str = "default"
    response_time: float = 0.0
    success_rate: float = 1.0
    health_score: float = 1.0
    last_request: float = 0.0
    total_requests: int = 0
    failed_requests: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class LoadBalancerConfig:
    """Load balancer configuration"""
    service_name: str
    algorithm: LoadBalancingAlgorithm = LoadBalancingAlgorithm.ROUND_ROBIN
    health_check_interval: float = 30.0
    health_check_timeout: float = 5.0
    session_affinity: bool = False
    session_timeout: float = 3600.0  # 1 hour
    enable_retries: bool = True
    max_retries: int = 3
    retry_delay: float = 1.0
    circuit_breaker: bool = True
    failure_threshold: int = 5
    recovery_timeout: float = 60.0
    enable_rate_limiting: bool = False
    rate_limit: int = 1000  # requests per minute
    enable_geographic_routing: bool = False

@dataclass
class RequestContext:
    """Request context information"""
    request_id: str
    client_ip: str
    user_agent: str = ""
    session_id: Optional[str] = None
    priority: RequestPriority = RequestPriority.NORMAL
    region: str = "default"
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class RoutingDecision:
    """Load balancing routing decision"""
    backend: Backend
    reason: str
    confidence: float = 1.0
    fallback: bool = False
    retry_count: int = 0

class LoadBalancerController:
    """
    Enterprise Load Balancer Controller
    
    Provides comprehensive load balancing with:
    - Multiple algorithms (round-robin, least connections, etc.)
    - Health monitoring and automatic failover
    - Session affinity and sticky sessions
    - Geographic routing
    - Circuit breaker pattern
    - Rate limiting integration
    """
    
    def __init__(self, config: LoadBalancerConfig):
        """Initialize load balancer controller"""
        self.config = config
        self.backends: Dict[str, Backend] = {}
        self.backend_order: List[str] = []  # For round-robin
        self.current_index = 0
        
        # Session affinity
        self.session_assignments: Dict[str, str] = {}  # session_id -> backend_id
        self.session_timeouts: Dict[str, float] = {}
        
        # Consistent hashing
        self.hash_ring: List[Tuple[int, str]] = []
        self.hash_ring_size = 1000
        
        # Performance tracking
        self.request_counts: Dict[str, int] = defaultdict(int)
        self.response_times: Dict[str, List[float]] = defaultdict(list)
        
        # Circuit breaker state
        self.circuit_state: Dict[str, str] = {}  # backend_id -> state (closed/open/half-open)
        self.circuit_failures: Dict[str, int] = defaultdict(int)
        self.circuit_last_failure: Dict[str, float] = {}
        
        # Rate limiting
        self.request_history: Dict[str, List[float]] = defaultdict(list)
        
        self.shutdown_event = asyncio.Event()
        self._lock = asyncio.Lock()
        
        # Health check task
        self.health_check_task: Optional[asyncio.Task] = None
        self.session: Optional[aiohttp.ClientSession] = None
        
        logger.info("LoadBalancerController initialized for service: %s", config.service_name)
    
    async def start(self):
        """Start the load balancer controller"""
        try:
            # Create HTTP session
            self.session = aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=30)
            )
            
            # Start health check task
            self.health_check_task = asyncio.create_task(self._health_check_loop())
            
            logger.info("LoadBalancerController started for service: %s", self.config.service_name)
        except Exception as e:
            logger.error("Failed to start LoadBalancerController: %s", e)
            raise
    
    async def stop(self):
        """Stop the load balancer controller"""
        try:
            self.shutdown_event.set()
            
            # Stop health check task
            if self.health_check_task:
                self.health_check_task.cancel()
                try:
                    await self.health_check_task
                except asyncio.CancelledError:
                    pass
            
            # Close HTTP session
            if self.session:
                await self.session.close()
                self.session = None
            
            logger.info("LoadBalancerController stopped for service: %s", self.config.service_name)
        except Exception as e:
            logger.error("Error stopping LoadBalancerController: %s", e)
    
    async def add_backend(self, backend: Backend):
        """Add a backend server"""
        async with self._lock:
            self.backends[backend.id] = backend
            self.backend_order.append(backend.id)
            self.circuit_state[backend.id] = "closed"
            
            # Update consistent hash ring
            await self._update_hash_ring()
        
        logger.info("Added backend %s for service %s", backend.id, self.config.service_name)
    
    async def remove_backend(self, backend_id: str):
        """Remove a backend server"""
        async with self._lock:
            if backend_id in self.backends:
                # Drain connections first
                await self._drain_backend(backend_id)
                
                # Remove from data structures
                self.backends.pop(backend_id, None)
                if backend_id in self.backend_order:
                    self.backend_order.remove(backend_id)
                
                self.circuit_state.pop(backend_id, None)
                self.circuit_failures.pop(backend_id, None)
                self.circuit_last_failure.pop(backend_id, None)
                
                # Update consistent hash ring
                await self._update_hash_ring()
                
                # Clean up session assignments
                sessions_to_remove = [
                    session_id for session_id, assigned_backend in self.session_assignments.items()
                    if assigned_backend == backend_id
                ]
                for session_id in sessions_to_remove:
                    self.session_assignments.pop(session_id, None)
                    self.session_timeouts.pop(session_id, None)
        
        logger.info("Removed backend %s from service %s", backend_id, self.config.service_name)
    
    async def route_request(self, context: RequestContext) -> Optional[RoutingDecision]:
        """Route a request to the best available backend"""
        async with self._lock:
            # Check rate limiting
            if self.config.enable_rate_limiting:
                if not await self._check_rate_limit(context.client_ip):
                    logger.warning("Rate limit exceeded for client %s", context.client_ip)
                    return None
            
            # Clean up expired sessions
            await self._cleanup_expired_sessions()
            
            # Check session affinity
            if self.config.session_affinity and context.session_id:
                assigned_backend = self.session_assignments.get(context.session_id)
                if assigned_backend and assigned_backend in self.backends:
                    backend = self.backends[assigned_backend]
                    if await self._is_backend_available(backend):
                        self.session_timeouts[context.session_id] = time.time() + self.config.session_timeout
                        return RoutingDecision(
                            backend=backend,
                            reason="session_affinity",
                            confidence=1.0
                        )
            
            # Select backend based on algorithm
            backend = await self._select_backend(context)
            if not backend:
                logger.warning("No available backends for service %s", self.config.service_name)
                return None
            
            # Update session assignment
            if self.config.session_affinity and context.session_id:
                self.session_assignments[context.session_id] = backend.id
                self.session_timeouts[context.session_id] = time.time() + self.config.session_timeout
            
            # Update connection count
            backend.current_connections += 1
            backend.last_request = time.time()
            backend.total_requests += 1
            
            return RoutingDecision(
                backend=backend,
                reason=self.config.algorithm.value,
                confidence=backend.health_score
            )
    
    async def complete_request(
        self,
        backend_id: str,
        response_time: float,
        success: bool,
        context: RequestContext
    ):
        """Mark request as completed and update metrics"""
        async with self._lock:
            backend = self.backends.get(backend_id)
            if not backend:
                return
            
            # Update connection count
            backend.current_connections = max(0, backend.current_connections - 1)
            
            # Update performance metrics
            self.request_counts[backend_id] += 1
            
            if success:
                # Update response time (running average)
                response_times = self.response_times[backend_id]
                response_times.append(response_time)
                
                # Keep only last 100 response times
                if len(response_times) > 100:
                    response_times.pop(0)
                
                backend.response_time = sum(response_times) / len(response_times)
                
                # Update success rate
                total_requests = backend.total_requests
                failed_requests = backend.failed_requests
                backend.success_rate = (total_requests - failed_requests) / total_requests if total_requests > 0 else 1.0
                
                # Circuit breaker: reset on success
                if self.config.circuit_breaker:
                    self.circuit_failures[backend_id] = 0
                    if self.circuit_state[backend_id] == "half-open":
                        self.circuit_state[backend_id] = "closed"
                        logger.info("Circuit breaker closed for backend %s", backend_id)
            
            else:
                # Update failure count
                backend.failed_requests += 1
                backend.success_rate = (backend.total_requests - backend.failed_requests) / backend.total_requests
                
                # Circuit breaker: handle failure
                if self.config.circuit_breaker:
                    self.circuit_failures[backend_id] += 1
                    self.circuit_last_failure[backend_id] = time.time()
                    
                    if (self.circuit_failures[backend_id] >= self.config.failure_threshold and
                        self.circuit_state[backend_id] == "closed"):
                        self.circuit_state[backend_id] = "open"
                        logger.warning("Circuit breaker opened for backend %s", backend_id)
            
            # Update health score
            backend.health_score = min(1.0, backend.success_rate * 
                                     (1.0 if backend.current_connections < backend.max_connections else 0.5))
    
    async def get_backend_status(self) -> Dict[str, Any]:
        """Get status of all backends"""
        async with self._lock:
            backend_statuses = []
            
            for backend in self.backends.values():
                backend_statuses.append({
                    "id": backend.id,
                    "endpoint": backend.endpoint,
                    "state": backend.state.value,
                    "weight": backend.weight,
                    "current_connections": backend.current_connections,
                    "max_connections": backend.max_connections,
                    "response_time": backend.response_time,
                    "success_rate": backend.success_rate,
                    "health_score": backend.health_score,
                    "total_requests": backend.total_requests,
                    "failed_requests": backend.failed_requests,
                    "circuit_state": self.circuit_state.get(backend.id, "unknown"),
                    "region": backend.region,
                    "zone": backend.zone
                })
            
            return {
                "service_name": self.config.service_name,
                "algorithm": self.config.algorithm.value,
                "total_backends": len(self.backends),
                "active_backends": len([b for b in self.backends.values() if b.state == BackendState.ACTIVE]),
                "total_connections": sum(b.current_connections for b in self.backends.values()),
                "session_affinity_enabled": self.config.session_affinity,
                "active_sessions": len(self.session_assignments),
                "backends": backend_statuses
            }
    
    async def _select_backend(self, context: RequestContext) -> Optional[Backend]:
        """Select backend based on configured algorithm"""
        available_backends = [
            backend for backend in self.backends.values()
            if await self._is_backend_available(backend)
        ]
        
        if not available_backends:
            return None
        
        algorithm = self.config.algorithm
        
        if algorithm == LoadBalancingAlgorithm.ROUND_ROBIN:
            return await self._round_robin_select(available_backends)
        
        elif algorithm == LoadBalancingAlgorithm.WEIGHTED_ROUND_ROBIN:
            return await self._weighted_round_robin_select(available_backends)
        
        elif algorithm == LoadBalancingAlgorithm.LEAST_CONNECTIONS:
            return min(available_backends, key=lambda b: b.current_connections)
        
        elif algorithm == LoadBalancingAlgorithm.WEIGHTED_LEAST_CONNECTIONS:
            return min(available_backends, key=lambda b: b.current_connections / max(b.weight, 1))
        
        elif algorithm == LoadBalancingAlgorithm.LEAST_RESPONSE_TIME:
            return min(available_backends, key=lambda b: b.response_time or float('inf'))
        
        elif algorithm == LoadBalancingAlgorithm.WEIGHTED_RESPONSE_TIME:
            return min(available_backends, key=lambda b: (b.response_time or float('inf')) / max(b.weight, 1))
        
        elif algorithm == LoadBalancingAlgorithm.CONSISTENT_HASH:
            return await self._consistent_hash_select(context.client_ip, available_backends)
        
        elif algorithm == LoadBalancingAlgorithm.RANDOM:
            return random.choice(available_backends)
        
        elif algorithm == LoadBalancingAlgorithm.WEIGHTED_RANDOM:
            return await self._weighted_random_select(available_backends)
        
        elif algorithm == LoadBalancingAlgorithm.IP_HASH:
            return await self._ip_hash_select(context.client_ip, available_backends)
        
        elif algorithm == LoadBalancingAlgorithm.GEOGRAPHIC:
            return await self._geographic_select(context.region, available_backends)
        
        elif algorithm == LoadBalancingAlgorithm.HEALTH_BASED:
            return max(available_backends, key=lambda b: b.health_score)
        
        else:
            # Default to round robin
            return await self._round_robin_select(available_backends)
    
    async def _round_robin_select(self, backends: List[Backend]) -> Backend:
        """Round-robin backend selection"""
        if not backends:
            raise ValueError("No backends available")
        
        # Filter backends that are in our order list
        ordered_backends = [b for b in backends if b.id in self.backend_order]
        if not ordered_backends:
            return backends[0]
        
        # Find next backend in order
        for _ in range(len(self.backend_order)):
            self.current_index = (self.current_index + 1) % len(self.backend_order)
            backend_id = self.backend_order[self.current_index]
            
            for backend in ordered_backends:
                if backend.id == backend_id:
                    return backend
        
        return ordered_backends[0]
    
    async def _weighted_round_robin_select(self, backends: List[Backend]) -> Backend:
        """Weighted round-robin selection"""
        if not backends:
            raise ValueError("No backends available")
        
        # Create weighted list
        weighted_backends = []
        for backend in backends:
            for _ in range(max(1, backend.weight // 10)):  # Scale down weights
                weighted_backends.append(backend)
        
        if not weighted_backends:
            return backends[0]
        
        return weighted_backends[self.current_index % len(weighted_backends)]
    
    async def _weighted_random_select(self, backends: List[Backend]) -> Backend:
        """Weighted random selection"""
        total_weight = sum(backend.weight for backend in backends)
        if total_weight == 0:
            return random.choice(backends)
        
        r = random.uniform(0, total_weight)
        cumulative = 0
        
        for backend in backends:
            cumulative += backend.weight
            if r <= cumulative:
                return backend
        
        return backends[-1]
    
    async def _consistent_hash_select(self, key: str, backends: List[Backend]) -> Backend:
        """Consistent hash selection"""
        if not self.hash_ring:
            await self._update_hash_ring()
        
        if not self.hash_ring:
            return backends[0] if backends else None
        
        # Hash the key
        hash_value = int(hashlib.md5(key.encode()).hexdigest(), 16) % (2**32)
        
        # Find the first backend with hash >= hash_value
        for ring_hash, backend_id in self.hash_ring:
            if ring_hash >= hash_value:
                for backend in backends:
                    if backend.id == backend_id:
                        return backend
        
        # Wrap around to first backend
        for backend in backends:
            if backend.id == self.hash_ring[0][1]:
                return backend
        
        return backends[0]
    
    async def _ip_hash_select(self, client_ip: str, backends: List[Backend]) -> Backend:
        """IP hash selection"""
        hash_value = hash(client_ip) % len(backends)
        return backends[hash_value]
    
    async def _geographic_select(self, client_region: str, backends: List[Backend]) -> Backend:
        """Geographic selection - prefer backends in same region"""
        # First try backends in same region
        same_region = [b for b in backends if b.region == client_region]
        if same_region:
            return min(same_region, key=lambda b: b.current_connections)
        
        # Fall back to any available backend
        return min(backends, key=lambda b: b.current_connections)
    
    async def _is_backend_available(self, backend: Backend) -> bool:
        """Check if backend is available for requests"""
        if backend.state not in [BackendState.ACTIVE]:
            return False
        
        if backend.current_connections >= backend.max_connections:
            return False
        
        # Check circuit breaker
        if self.config.circuit_breaker:
            circuit_state = self.circuit_state.get(backend.id, "closed")
            
            if circuit_state == "open":
                # Check if recovery timeout has passed
                last_failure = self.circuit_last_failure.get(backend.id, 0)
                if time.time() - last_failure > self.config.recovery_timeout:
                    self.circuit_state[backend.id] = "half-open"
                    logger.info("Circuit breaker half-opened for backend %s", backend.id)
                    return True
                return False
            
            elif circuit_state == "half-open":
                # Allow limited requests to test recovery
                return True
        
        return True
    
    async def _update_hash_ring(self):
        """Update consistent hash ring"""
        self.hash_ring.clear()
        
        for backend in self.backends.values():
            # Add multiple points for better distribution
            for i in range(self.hash_ring_size // len(self.backends) if self.backends else 1):
                hash_input = f"{backend.id}:{i}"
                hash_value = int(hashlib.md5(hash_input.encode()).hexdigest(), 16) % (2**32)
                self.hash_ring.append((hash_value, backend.id))
        
        # Sort by hash value
        self.hash_ring.sort()
    
    async def _check_rate_limit(self, client_ip: str) -> bool:
        """Check rate limit for client"""
        current_time = time.time()
        history = self.request_history[client_ip]
        
        # Remove old requests (older than 1 minute)
        history[:] = [t for t in history if current_time - t < 60]
        
        # Check if under limit
        if len(history) >= self.config.rate_limit:
            return False
        
        # Add current request
        history.append(current_time)
        return True
    
    async def _cleanup_expired_sessions(self):
        """Clean up expired sessions"""
        current_time = time.time()
        expired_sessions = [
            session_id for session_id, timeout in self.session_timeouts.items()
            if current_time > timeout
        ]
        
        for session_id in expired_sessions:
            self.session_assignments.pop(session_id, None)
            self.session_timeouts.pop(session_id, None)
    
    async def _drain_backend(self, backend_id: str):
        """Drain connections from a backend"""
        backend = self.backends.get(backend_id)
        if not backend:
            return
        
        backend.state = BackendState.DRAINING
        
        # Wait for connections to drain (with timeout)
        timeout = 30.0  # 30 seconds
        start_time = time.time()
        
        while backend.current_connections > 0 and (time.time() - start_time) < timeout:
            await asyncio.sleep(1.0)
        
        if backend.current_connections > 0:
            logger.warning(
                "Backend %s still has %d connections after drain timeout",
                backend_id, backend.current_connections
            )
    
    async def _health_check_loop(self):
        """Health check loop for all backends"""
        while not self.shutdown_event.is_set():
            try:
                await self._perform_health_checks()
                await asyncio.sleep(self.config.health_check_interval)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error("Error in health check loop: %s", e)
                await asyncio.sleep(self.config.health_check_interval)
    
    async def _perform_health_checks(self):
        """Perform health checks on all backends"""
        if not self.session:
            return
        
        async with self._lock:
            for backend in self.backends.values():
                if backend.state == BackendState.MAINTENANCE:
                    continue
                
                try:
                    health_endpoint = f"{backend.endpoint}/health"
                    start_time = time.time()
                    
                    async with self.session.get(
                        health_endpoint, 
                        timeout=self.config.health_check_timeout
                    ) as response:
                        response_time = time.time() - start_time
                        
                        if response.status < 400:
                            if backend.state == BackendState.FAILED:
                                backend.state = BackendState.ACTIVE
                                logger.info("Backend %s recovered", backend.id)
                        else:
                            if backend.state == BackendState.ACTIVE:
                                backend.state = BackendState.FAILED
                                logger.warning("Backend %s failed health check", backend.id)
                
                except Exception as e:
                    if backend.state == BackendState.ACTIVE:
                        backend.state = BackendState.FAILED
                        logger.warning("Backend %s failed health check: %s", backend.id, e)

# Global load balancer instances
_load_balancers: Dict[str, LoadBalancerController] = {}

async def get_load_balancer(service_name: str, config: Optional[LoadBalancerConfig] = None) -> LoadBalancerController:
    """Get load balancer instance for a service"""
    global _load_balancers
    
    if service_name not in _load_balancers:
        if not config:
            config = LoadBalancerConfig(service_name=service_name)
        
        _load_balancers[service_name] = LoadBalancerController(config)
        await _load_balancers[service_name].start()
    
    return _load_balancers[service_name]

async def shutdown_load_balancers():
    """Shutdown all load balancer instances"""
    global _load_balancers
    
    for lb in _load_balancers.values():
        await lb.stop()
    
    _load_balancers.clear()

if __name__ == "__main__":
    async def test_load_balancer():
        """Test load balancer functionality"""
        config = LoadBalancerConfig(
            service_name="test_service",
            algorithm=LoadBalancingAlgorithm.ROUND_ROBIN,
            session_affinity=True
        )
        
        lb = LoadBalancerController(config)
        await lb.start()
        
        try:
            # Add test backends
            backends = [
                Backend(id="backend_1", endpoint="http://localhost:8001", weight=100),
                Backend(id="backend_2", endpoint="http://localhost:8002", weight=80),
                Backend(id="backend_3", endpoint="http://localhost:8003", weight=60)
            ]
            
            for backend in backends:
                await lb.add_backend(backend)
            
            # Test routing
            context = RequestContext(
                request_id="test_1",
                client_ip="192.168.1.100",
                session_id="session_123"
            )
            
            decision = await lb.route_request(context)
            print(f"Routed to: {decision.backend.id if decision else None}")
            
            # Complete request
            if decision:
                await lb.complete_request(
                    decision.backend.id, 0.1, True, context
                )
            
            # Get status
            status = await lb.get_backend_status()
            print(f"Load balancer status: {status}")
            
        finally:
            await lb.stop()
    
    # Run test
    asyncio.run(test_load_balancer())