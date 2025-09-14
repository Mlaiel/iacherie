"""
Ainflue Core Infrastructure - Load Balancer Core
================================================

Enterprise-grade load balancing system with multiple algorithms, health checking,
sticky sessions, and circuit breaker integration. Provides intelligent traffic
distribution for all Ainflue core services.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import hashlib
import logging
import random
import time
from typing import Dict, List, Optional, Any, Union, Callable, Protocol
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta
from collections import defaultdict, deque
import threading

logger = logging.getLogger(__name__)

class LoadBalancingAlgorithm(str, Enum):
    """Load balancing algorithms"""
    ROUND_ROBIN = "round_robin"
    WEIGHTED_ROUND_ROBIN = "weighted_round_robin"
    LEAST_CONNECTIONS = "least_connections"
    WEIGHTED_LEAST_CONNECTIONS = "weighted_least_connections"
    RANDOM = "random"
    WEIGHTED_RANDOM = "weighted_random"
    CONSISTENT_HASH = "consistent_hash"
    IP_HASH = "ip_hash"
    LEAST_RESPONSE_TIME = "least_response_time"
    RESOURCE_BASED = "resource_based"

class BackendStatus(str, Enum):
    """Backend server status"""
    HEALTHY = "healthy"
    UNHEALTHY = "unhealthy"
    DRAINING = "draining"
    MAINTENANCE = "maintenance"
    UNKNOWN = "unknown"

@dataclass
class Backend:
    """Backend server configuration"""
    id: str
    host: str
    port: int
    weight: int = 100
    max_connections: int = 1000
    current_connections: int = 0
    status: BackendStatus = BackendStatus.HEALTHY
    response_times: deque = field(default_factory=lambda: deque(maxlen=100))
    total_requests: int = 0
    failed_requests: int = 0
    last_check: Optional[datetime] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    @property
    def url(self) -> str:
        """Get backend URL"""
        return f"http://{self.host}:{self.port}"
    
    @property
    def avg_response_time(self) -> float:
        """Get average response time"""
        if not self.response_times:
            return 0.0
        return sum(self.response_times) / len(self.response_times)
    
    @property
    def error_rate(self) -> float:
        """Get error rate"""
        if self.total_requests == 0:
            return 0.0
        return self.failed_requests / self.total_requests
    
    @property
    def connection_utilization(self) -> float:
        """Get connection utilization percentage"""
        if self.max_connections == 0:
            return 0.0
        return (self.current_connections / self.max_connections) * 100

@dataclass
class LoadBalancerRule:
    """Load balancer routing rule"""
    name: str
    condition: Callable[[Dict[str, Any]], bool]
    backend_pool: str
    priority: int = 0
    enabled: bool = True

@dataclass
class StickySession:
    """Sticky session information"""
    session_id: str
    backend_id: str
    created_at: datetime
    last_used: datetime
    ttl_seconds: int = 3600

@dataclass
class BalancerMetrics:
    """Load balancer metrics"""
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    total_backends: int = 0
    healthy_backends: int = 0
    unhealthy_backends: int = 0
    avg_response_time: float = 0.0
    requests_per_second: float = 0.0
    error_rate: float = 0.0
    last_reset: datetime = field(default_factory=datetime.utcnow)

class LoadBalancerRequest:
    """Load balancer request context"""
    
    def __init__(self, client_ip -> None: str, headers -> None: Dict[str, str], path -> None: str, method -> None: str) -> None:
        self.client_ip = client_ip
        self.headers = headers
        self.path = path
        self.method = method
        self.session_id = headers.get('session-id', '')
        self.timestamp = time.time()

class LoadBalancerCore:
    """Enterprise load balancing system"""
    
    def __init__(self, level -> None: str = "enterprise") -> None:
        """Initialize load balancer core"""
        self.level = level
        self.backend_pools: Dict[str, List[Backend]] = {}
        self.algorithms: Dict[str, LoadBalancingAlgorithm] = {}
        self.rules: List[LoadBalancerRule] = []
        self.sticky_sessions: Dict[str, StickySession] = {}
        self.metrics = BalancerMetrics()
        
        # Algorithm state
        self._round_robin_indices: Dict[str, int] = defaultdict(int)
        self._consistent_hash_rings: Dict[str, Dict[str, str]] = {}
        
        # Health checking
        self.health_check_enabled = True
        self.health_check_interval = 30
        self._health_check_task: Optional[asyncio.Task] = None
        
        # Circuit breaker integration
        self.circuit_breaker_threshold = 5  # failures
        self.circuit_breaker_timeout = 60  # seconds
        self._circuit_breakers: Dict[str, Dict[str, Any]] = {}
        
        # Thread safety
        self._lock = asyncio.Lock()
        
        # Performance tracking
        self._request_times: deque = deque(maxlen=1000)
        self._request_counter = 0
        self._last_metrics_update = time.time()
        
        logger.info(f"⚖️ Load Balancer Core initialized - Level: {level}")

    async def add_backend_pool(self, pool_name -> None: str, algorithm -> None: LoadBalancingAlgorithm = LoadBalancingAlgorithm.ROUND_ROBIN) -> None:
        """Add a backend pool"""
        async with self._lock:
            self.backend_pools[pool_name] = []
            self.algorithms[pool_name] = algorithm
            
            # Initialize algorithm state
            if algorithm == LoadBalancingAlgorithm.CONSISTENT_HASH:
                self._consistent_hash_rings[pool_name] = {}
            
            logger.info(f"📝 Added backend pool '{pool_name}' with algorithm {algorithm.value}")

    async def add_backend(self, pool_name -> None: str, backend -> None: Backend) -> None:
        """Add backend to pool"""
        async with self._lock:
            if pool_name not in self.backend_pools:
                await self.add_backend_pool(pool_name)
            
            self.backend_pools[pool_name].append(backend)
            self.metrics.total_backends += 1
            
            # Update consistent hash ring
            if self.algorithms.get(pool_name) == LoadBalancingAlgorithm.CONSISTENT_HASH:
                self._update_consistent_hash_ring(pool_name)
            
            logger.info(f"🔗 Added backend {backend.id} to pool '{pool_name}'")

    async def remove_backend(self, pool_name -> None: str, backend_id -> None: str) -> None:
        """Remove backend from pool"""
        async with self._lock:
            if pool_name in self.backend_pools:
                backends = self.backend_pools[pool_name]
                for i, backend in enumerate(backends):
                    if backend.id == backend_id:
                        backends.pop(i)
                        self.metrics.total_backends -= 1
                        
                        # Update consistent hash ring
                        if self.algorithms.get(pool_name) == LoadBalancingAlgorithm.CONSISTENT_HASH:
                            self._update_consistent_hash_ring(pool_name)
                        
                        logger.info(f"🗑️ Removed backend {backend_id} from pool '{pool_name}'")
                        break

    def _update_consistent_hash_ring(self, pool_name -> None: str) -> None:
        """Update consistent hash ring for pool"""
        ring = {}
        backends = self.backend_pools[pool_name]
        
        # Create virtual nodes for each backend
        for backend in backends:
            if backend.status == BackendStatus.HEALTHY:
                # Create multiple virtual nodes based on weight
                virtual_nodes = max(1, backend.weight // 10)
                for i in range(virtual_nodes):
                    virtual_key = f"{backend.id}:{i}"
                    hash_value = hashlib.md5(virtual_key.encode()).hexdigest()
                    ring[hash_value] = backend.id
        
        self._consistent_hash_rings[pool_name] = ring

    async def select_backend(self, pool_name: str, request: LoadBalancerRequest) -> Optional[Backend]:
        """Select backend based on configured algorithm"""
        async with self._lock:
            if pool_name not in self.backend_pools:
                return None
            
            backends = self.backend_pools[pool_name]
            healthy_backends = [b for b in backends if b.status == BackendStatus.HEALTHY]
            
            if not healthy_backends:
                logger.warning(f"No healthy backends in pool '{pool_name}'")
                return None
            
            # Check for sticky session
            if request.session_id and request.session_id in self.sticky_sessions:
                session = self.sticky_sessions[request.session_id]
                backend = self._find_backend_by_id(pool_name, session.backend_id)
                if backend and backend.status == BackendStatus.HEALTHY:
                    session.last_used = datetime.utcnow()
                    return backend
            
            algorithm = self.algorithms[pool_name]
            selected_backend = await self._apply_algorithm(algorithm, pool_name, healthy_backends, request)
            
            # Create sticky session if enabled
            if request.session_id and selected_backend:
                self._create_sticky_session(request.session_id, selected_backend.id)
            
            return selected_backend

    async def _apply_algorithm(
        self, 
        algorithm: LoadBalancingAlgorithm, 
        pool_name: str, 
        backends: List[Backend], 
        request: LoadBalancerRequest
    ) -> Optional[Backend]:
        """Apply load balancing algorithm"""
        
        if algorithm == LoadBalancingAlgorithm.ROUND_ROBIN:
            return self._round_robin(pool_name, backends)
        
        elif algorithm == LoadBalancingAlgorithm.WEIGHTED_ROUND_ROBIN:
            return self._weighted_round_robin(pool_name, backends)
        
        elif algorithm == LoadBalancingAlgorithm.LEAST_CONNECTIONS:
            return self._least_connections(backends)
        
        elif algorithm == LoadBalancingAlgorithm.WEIGHTED_LEAST_CONNECTIONS:
            return self._weighted_least_connections(backends)
        
        elif algorithm == LoadBalancingAlgorithm.RANDOM:
            return random.choice(backends)
        
        elif algorithm == LoadBalancingAlgorithm.WEIGHTED_RANDOM:
            return self._weighted_random(backends)
        
        elif algorithm == LoadBalancingAlgorithm.CONSISTENT_HASH:
            return self._consistent_hash(pool_name, backends, request)
        
        elif algorithm == LoadBalancingAlgorithm.IP_HASH:
            return self._ip_hash(backends, request)
        
        elif algorithm == LoadBalancingAlgorithm.LEAST_RESPONSE_TIME:
            return self._least_response_time(backends)
        
        elif algorithm == LoadBalancingAlgorithm.RESOURCE_BASED:
            return self._resource_based(backends)
        
        else:
            return self._round_robin(pool_name, backends)

    def _round_robin(self, pool_name: str, backends: List[Backend]) -> Backend:
        """Round robin algorithm"""
        index = self._round_robin_indices[pool_name]
        backend = backends[index % len(backends)]
        self._round_robin_indices[pool_name] = (index + 1) % len(backends)
        return backend

    def _weighted_round_robin(self, pool_name: str, backends: List[Backend]) -> Backend:
        """Weighted round robin algorithm"""
        total_weight = sum(b.weight for b in backends)
        if total_weight == 0:
            return self._round_robin(pool_name, backends)
        
        # Create weighted list
        weighted_backends = []
        for backend in backends:
            count = max(1, backend.weight)
            weighted_backends.extend([backend] * count)
        
        index = self._round_robin_indices[pool_name]
        backend = weighted_backends[index % len(weighted_backends)]
        self._round_robin_indices[pool_name] = (index + 1) % len(weighted_backends)
        return backend

    def _least_connections(self, backends: List[Backend]) -> Backend:
        """Least connections algorithm"""
        return min(backends, key=lambda b: b.current_connections)

    def _weighted_least_connections(self, backends: List[Backend]) -> Backend:
        """Weighted least connections algorithm"""
        def score(backend: Backend) -> float:
            if backend.weight == 0:
                return float('inf')
            return backend.current_connections / backend.weight
        
        return min(backends, key=score)

    def _weighted_random(self, backends: List[Backend]) -> Backend:
        """Weighted random algorithm"""
        total_weight = sum(b.weight for b in backends)
        if total_weight == 0:
            return random.choice(backends)
        
        threshold = random.uniform(0, total_weight)
        current_weight = 0
        
        for backend in backends:
            current_weight += backend.weight
            if current_weight >= threshold:
                return backend
        
        return backends[-1]

    def _consistent_hash(self, pool_name: str, backends: List[Backend], request: LoadBalancerRequest) -> Backend:
        """Consistent hash algorithm"""
        ring = self._consistent_hash_rings.get(pool_name, {})
        if not ring:
            return random.choice(backends)
        
        # Hash the client IP
        client_hash = hashlib.md5(request.client_ip.encode()).hexdigest()
        
        # Find the first node in the ring
        sorted_hashes = sorted(ring.keys())
        for hash_key in sorted_hashes:
            if hash_key >= client_hash:
                backend_id = ring[hash_key]
                return self._find_backend_by_id_in_list(backends, backend_id)
        
        # Wrap around to the first node
        if sorted_hashes:
            backend_id = ring[sorted_hashes[0]]
            return self._find_backend_by_id_in_list(backends, backend_id)
        
        return random.choice(backends)

    def _ip_hash(self, backends: List[Backend], request: LoadBalancerRequest) -> Backend:
        """IP hash algorithm"""
        ip_hash = hash(request.client_ip)
        index = ip_hash % len(backends)
        return backends[index]

    def _least_response_time(self, backends: List[Backend]) -> Backend:
        """Least response time algorithm"""
        return min(backends, key=lambda b: b.avg_response_time or 0)

    def _resource_based(self, backends: List[Backend]) -> Backend:
        """Resource-based algorithm (CPU + Memory + Connections)"""
        def resource_score(backend: Backend) -> float:
            # Lower score is better
            connection_score = backend.connection_utilization / 100
            response_time_score = min(backend.avg_response_time / 1000, 1.0)  # Normalize to 0-1
            error_score = backend.error_rate
            
            return connection_score + response_time_score + error_score
        
        return min(backends, key=resource_score)

    def _find_backend_by_id(self, pool_name: str, backend_id: str) -> Optional[Backend]:
        """Find backend by ID in pool"""
        if pool_name not in self.backend_pools:
            return None
        
        return self._find_backend_by_id_in_list(self.backend_pools[pool_name], backend_id)

    def _find_backend_by_id_in_list(self, backends: List[Backend], backend_id: str) -> Optional[Backend]:
        """Find backend by ID in list"""
        for backend in backends:
            if backend.id == backend_id:
                return backend
        return None

    def _create_sticky_session(self, session_id -> None: str, backend_id -> None: str) -> None:
        """Create sticky session"""
        session = StickySession(
            session_id=session_id,
            backend_id=backend_id,
            created_at=datetime.utcnow(),
            last_used=datetime.utcnow()
        )
        self.sticky_sessions[session_id] = session

    async def record_request(self, backend -> None: Backend, response_time -> None: float, success -> None: bool) -> None:
        """Record request metrics"""
        async with self._lock:
            backend.total_requests += 1
            backend.response_times.append(response_time)
            
            if success:
                backend.current_connections = max(0, backend.current_connections - 1)
                self.metrics.successful_requests += 1
            else:
                backend.failed_requests += 1
                self.metrics.failed_requests += 1
            
            # Update global metrics
            self.metrics.total_requests += 1
            self._request_times.append(response_time)
            self._request_counter += 1
            
            # Update circuit breaker
            await self._update_circuit_breaker(backend, success)

    async def _update_circuit_breaker(self, backend -> None: Backend, success -> None: bool) -> None:
        """Update circuit breaker state"""
        cb_key = f"{backend.id}"
        
        if cb_key not in self._circuit_breakers:
            self._circuit_breakers[cb_key] = {
                'failures': 0,
                'last_failure': None,
                'state': 'closed'  # closed, open, half-open
            }
        
        cb = self._circuit_breakers[cb_key]
        
        if success:
            cb['failures'] = 0
            cb['state'] = 'closed'
        else:
            cb['failures'] += 1
            cb['last_failure'] = time.time()
            
            if cb['failures'] >= self.circuit_breaker_threshold:
                cb['state'] = 'open'
                backend.status = BackendStatus.UNHEALTHY
                logger.warning(f"🔌 Circuit breaker opened for backend {backend.id}")

    async def add_rule(self, rule -> None: LoadBalancerRule) -> None:
        """Add routing rule"""
        self.rules.append(rule)
        self.rules.sort(key=lambda r: r.priority, reverse=True)
        logger.info(f"📋 Added load balancer rule '{rule.name}'")

    async def remove_rule(self, rule_name -> None: str) -> None:
        """Remove routing rule"""
        self.rules = [r for r in self.rules if r.name != rule_name]
        logger.info(f"🗑️ Removed load balancer rule '{rule_name}'")

    async def evaluate_rules(self, request: LoadBalancerRequest) -> Optional[str]:
        """Evaluate routing rules to determine backend pool"""
        context = {
            'path': request.path,
            'method': request.method,
            'client_ip': request.client_ip,
            'headers': request.headers
        }
        
        for rule in self.rules:
            if rule.enabled and rule.condition(context):
                return rule.backend_pool
        
        return None

    async def cleanup_sticky_sessions(self) -> None:
        """Clean up expired sticky sessions"""
        current_time = datetime.utcnow()
        expired_sessions = []
        
        for session_id, session in self.sticky_sessions.items():
            if current_time - session.last_used > timedelta(seconds=session.ttl_seconds):
                expired_sessions.append(session_id)
        
        for session_id in expired_sessions:
            del self.sticky_sessions[session_id]
        
        if expired_sessions:
            logger.info(f"🧹 Cleaned up {len(expired_sessions)} expired sticky sessions")

    async def update_backend_status(self, pool_name -> None: str, backend_id -> None: str, status -> None: BackendStatus) -> None:
        """Update backend status"""
        async with self._lock:
            backend = self._find_backend_by_id(pool_name, backend_id)
            if backend:
                old_status = backend.status
                backend.status = status
                
                # Update metrics
                if old_status != status:
                    if status == BackendStatus.HEALTHY:
                        self.metrics.healthy_backends += 1
                        if old_status == BackendStatus.UNHEALTHY:
                            self.metrics.unhealthy_backends -= 1
                    elif status == BackendStatus.UNHEALTHY:
                        self.metrics.unhealthy_backends += 1
                        if old_status == BackendStatus.HEALTHY:
                            self.metrics.healthy_backends -= 1
                
                logger.info(f"🔄 Updated backend {backend_id} status: {old_status.value} -> {status.value}")

    def get_pool_status(self, pool_name: str) -> Dict[str, Any]:
        """Get pool status"""
        if pool_name not in self.backend_pools:
            return {}
        
        backends = self.backend_pools[pool_name]
        healthy_count = len([b for b in backends if b.status == BackendStatus.HEALTHY])
        
        return {
            'pool_name': pool_name,
            'algorithm': self.algorithms[pool_name].value,
            'total_backends': len(backends),
            'healthy_backends': healthy_count,
            'unhealthy_backends': len(backends) - healthy_count,
            'backends': [
                {
                    'id': b.id,
                    'host': b.host,
                    'port': b.port,
                    'status': b.status.value,
                    'weight': b.weight,
                    'connections': b.current_connections,
                    'avg_response_time': b.avg_response_time,
                    'error_rate': b.error_rate
                } for b in backends
            ]
        }

    def get_metrics(self) -> BalancerMetrics:
        """Get load balancer metrics"""
        # Update real-time metrics
        current_time = time.time()
        time_diff = current_time - self._last_metrics_update
        
        if time_diff > 0:
            self.metrics.requests_per_second = self._request_counter / time_diff
            self._request_counter = 0
            self._last_metrics_update = current_time
        
        if self._request_times:
            self.metrics.avg_response_time = sum(self._request_times) / len(self._request_times)
        
        if self.metrics.total_requests > 0:
            self.metrics.error_rate = self.metrics.failed_requests / self.metrics.total_requests
        
        return self.metrics

    async def health_check(self) -> bool:
        """Health check for load balancer"""
        try:
            # Check if we have any backend pools
            if not self.backend_pools:
                return True  # No pools configured is OK
            
            # Check if at least one pool has healthy backends
            for pool_name, backends in self.backend_pools.items():
                healthy_backends = [b for b in backends if b.status == BackendStatus.HEALTHY]
                if healthy_backends:
                    return True
            
            logger.warning("No healthy backends available in any pool")
            return False
            
        except Exception as e:
            logger.error(f"Load balancer health check failed: {str(e)}")
            return False

# Module exports
__all__ = [
    "LoadBalancerCore", "Backend", "LoadBalancerRequest", "LoadBalancerRule",
    "StickySession", "BalancerMetrics", "LoadBalancingAlgorithm", "BackendStatus"
]

logger.info("⚖️ Load Balancer Core module loaded")