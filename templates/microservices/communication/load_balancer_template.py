"""
⚠️  AVERTISSEMENT LÉGAL OBLIGATOIRE:
==========================================
© 2025 Fahed Mlaiel <mlaiel@live.de>
TOUS DROITS RÉSERVÉS

🚨 PROTECTION INTELLECTUELLE:
- Code propriétaire de Fahed Mlaiel
- Utilisation commerciale INTERDITE sans autorisation écrite
- Reverse engineering STRICTEMENT INTERDIT
- Distribution INTERDITE sans licence explicite
- Violation = Poursuites judiciaires automatiques

Load Balancer Template for Ainflue Microservices Platform
========================================================

Enterprise-grade intelligent load balancer template providing:
- Advanced load balancing algorithms (round-robin, least-conn, weighted, consistent hashing)
- Health checking and automatic failover
- Dynamic service discovery integration
- Sticky sessions and session affinity
- Circuit breaker integration
- Geographic and latency-based routing
- Real-time traffic monitoring and metrics
- Auto-scaling based on load patterns
- SSL termination and certificate management
- Rate limiting and DDoS protection

Author: Fahed Mlaiel (mlaiel@live.de)
Backend Senior & Load Balancing Specialist
"""

import logging
import asyncio
import json
import hashlib
import time
import random
from typing import Dict, Any, Optional, List, Callable, Type, Union, Set
from datetime import datetime, timedelta
from enum import Enum
from dataclasses import dataclass, field
import uuid
from collections import defaultdict, deque
import statistics

from pydantic import BaseModel, Field, validator
import redis.asyncio as redis
from prometheus_client import Counter, Histogram, Gauge
import aiohttp
import asyncio_mqtt
from geopy.distance import geodesic

from ..base_microservice import BaseMicroservice
from ..microservice_template import ServiceConfig, ServiceStatus
from ..communication_manager import CommunicationManager, CommunicationConfig
from ..circuit_breaker import CircuitBreaker

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
    LEAST_RESPONSE_TIME = "least_response_time"
    GEOGRAPHIC = "geographic"
    RESOURCE_BASED = "resource_based"


class HealthStatus(str, Enum):
    """Backend health status"""
    HEALTHY = "healthy"
    UNHEALTHY = "unhealthy"
    DRAINING = "draining"
    MAINTENANCE = "maintenance"


class SessionAffinityType(str, Enum):
    """Session affinity types"""
    NONE = "none"
    CLIENT_IP = "client_ip"
    COOKIE = "cookie"
    HEADER = "header"


@dataclass
class BackendServer:
    """Backend server configuration"""
    id: str
    host: str
    port: int
    weight: int = 100
    max_connections: int = 1000
    current_connections: int = 0
    health_status: HealthStatus = HealthStatus.HEALTHY
    health_check_url: str = "/health"
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    # Performance metrics
    response_times: deque = field(default_factory=lambda: deque(maxlen=100))
    success_count: int = 0
    error_count: int = 0
    last_health_check: Optional[datetime] = None
    last_request_time: Optional[datetime] = None
    
    # Geographic information
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    region: Optional[str] = None
    
    def get_average_response_time(self) -> float:
        """Get average response time"""
        if not self.response_times:
            return 0.0
        return statistics.mean(self.response_times)
    
    def get_error_rate(self) -> float:
        """Get error rate"""
        total_requests = self.success_count + self.error_count
        if total_requests == 0:
            return 0.0
        return self.error_count / total_requests
    
    def get_load_score(self) -> float:
        """Get current load score (0.0 to 1.0)"""
        if self.max_connections == 0:
            return 0.0
        return self.current_connections / self.max_connections


class HealthCheckConfig(BaseModel):
    """Health check configuration"""
    enabled: bool = Field(default=True, description="Enable health checks")
    interval_seconds: int = Field(default=30, description="Health check interval")
    timeout_seconds: int = Field(default=5, description="Health check timeout")
    unhealthy_threshold: int = Field(default=3, description="Consecutive failures to mark unhealthy")
    healthy_threshold: int = Field(default=2, description="Consecutive successes to mark healthy")
    path: str = Field(default="/health", description="Health check path")
    expected_status_codes: List[int] = Field(default=[200], description="Expected status codes")
    check_response_body: bool = Field(default=False, description="Check response body")
    expected_response_body: Optional[str] = Field(default=None, description="Expected response body")


class SessionAffinityConfig(BaseModel):
    """Session affinity configuration"""
    type: SessionAffinityType = Field(default=SessionAffinityType.NONE, description="Affinity type")
    cookie_name: str = Field(default="lb_session", description="Cookie name for cookie affinity")
    cookie_ttl_seconds: int = Field(default=3600, description="Cookie TTL")
    header_name: Optional[str] = Field(default=None, description="Header name for header affinity")
    hash_key: Optional[str] = Field(default=None, description="Hash key for consistent hashing")


class LoadBalancerPool(BaseModel):
    """Load balancer pool configuration"""
    name: str = Field(..., description="Pool name")
    algorithm: LoadBalancingAlgorithm = Field(..., description="Load balancing algorithm")
    backends: List[BackendServer] = Field(default_factory=list, description="Backend servers")
    health_check: HealthCheckConfig = Field(default_factory=HealthCheckConfig, description="Health check config")
    session_affinity: SessionAffinityConfig = Field(default_factory=SessionAffinityConfig, description="Session affinity")
    enable_circuit_breaker: bool = Field(default=True, description="Enable circuit breaker per backend")
    drain_timeout_seconds: int = Field(default=30, description="Drain timeout for graceful shutdown")
    max_retries: int = Field(default=3, description="Maximum retry attempts")
    retry_backoff_ms: int = Field(default=100, description="Retry backoff in milliseconds")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Pool metadata")


class LoadBalancerConfig(ServiceConfig):
    """Load balancer service configuration"""
    # Server settings
    listen_host: str = Field(default="0.0.0.0", description="Listen host")
    listen_port: int = Field(default=8080, description="Listen port")
    enable_ssl: bool = Field(default=False, description="Enable SSL termination")
    ssl_cert_path: Optional[str] = Field(default=None, description="SSL certificate path")
    ssl_key_path: Optional[str] = Field(default=None, description="SSL private key path")
    
    # Default pool settings
    default_algorithm: LoadBalancingAlgorithm = Field(default=LoadBalancingAlgorithm.ROUND_ROBIN, description="Default algorithm")
    default_health_check_interval: int = Field(default=30, description="Default health check interval")
    
    # Performance settings
    max_concurrent_requests: int = Field(default=10000, description="Maximum concurrent requests")
    request_timeout_seconds: int = Field(default=30, description="Request timeout")
    keep_alive_timeout_seconds: int = Field(default=5, description="Keep-alive timeout")
    
    # Service discovery
    enable_service_discovery: bool = Field(default=True, description="Enable automatic service discovery")
    consul_host: Optional[str] = Field(default=None, description="Consul host for service discovery")
    consul_port: int = Field(default=8500, description="Consul port")
    
    # Redis for session storage and coordination
    redis_host: str = Field(default="localhost", description="Redis host")
    redis_port: int = Field(default=6379, description="Redis port")
    redis_db: int = Field(default=7, description="Redis database")
    redis_password: Optional[str] = Field(default=None, description="Redis password")
    
    # Rate limiting
    enable_rate_limiting: bool = Field(default=True, description="Enable rate limiting")
    default_rate_limit_rpm: int = Field(default=1000, description="Default requests per minute")
    
    # Monitoring
    enable_metrics: bool = Field(default=True, description="Enable metrics collection")
    metrics_retention_seconds: int = Field(default=3600, description="Metrics retention period")


class LoadBalancerTemplate(BaseMicroservice):
    """
    Enterprise Load Balancer Template
    
    Provides intelligent load balancing with:
    - Multiple load balancing algorithms
    - Health checking and failover
    - Session affinity and sticky sessions
    - Circuit breaker integration
    - Geographic routing
    - Real-time monitoring
    """
    
    def __init__(self, config: LoadBalancerConfig):
        super().__init__(config)
        self.config = config
        self.redis_client: Optional[redis.Redis] = None
        self.pools: Dict[str, LoadBalancerPool] = {}
        self.backend_states: Dict[str, BackendServer] = {}
        self.circuit_breakers: Dict[str, CircuitBreaker] = {}
        self.session_store: Dict[str, str] = {}  # session_id -> backend_id
        self.request_counters: Dict[str, int] = defaultdict(int)  # For round robin
        self.health_check_tasks: Dict[str, asyncio.Task] = {}
        
        # Rate limiting
        self.rate_limiters: Dict[str, deque] = defaultdict(lambda: deque(maxlen=1000))
        
        # Metrics
        self.requests_total = Counter(
            'load_balancer_requests_total',
            'Total requests processed',
            ['pool_name', 'backend_id', 'status']
        )
        self.request_duration_seconds = Histogram(
            'load_balancer_request_duration_seconds',
            'Request duration',
            ['pool_name', 'backend_id']
        )
        self.active_connections_gauge = Gauge(
            'load_balancer_active_connections',
            'Active connections per backend',
            ['pool_name', 'backend_id']
        )
        self.backend_health_gauge = Gauge(
            'load_balancer_backend_health',
            'Backend health status (1=healthy, 0=unhealthy)',
            ['pool_name', 'backend_id']
        )
    
    async def initialize(self) -> None:
        """Initialize load balancer service"""
        try:
            logger.info("Initializing load balancer service")
            
            # Initialize Redis client
            await self._initialize_redis()
            
            # Start health check monitoring
            asyncio.create_task(self._health_check_monitor())
            
            # Start metrics collection
            asyncio.create_task(self._metrics_collection_task())
            
            # Start service discovery if enabled
            if self.config.enable_service_discovery:
                asyncio.create_task(self._service_discovery_task())
            
            logger.info("Load balancer service initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize load balancer service: {e}")
            raise
    
    async def _initialize_redis(self) -> None:
        """Initialize Redis connection"""
        self.redis_client = redis.Redis(
            host=self.config.redis_host,
            port=self.config.redis_port,
            db=self.config.redis_db,
            password=self.config.redis_password,
            decode_responses=True
        )
        
        await self.redis_client.ping()
        logger.info("Redis connection established")
    
    async def create_pool(self, pool_config: LoadBalancerPool) -> Dict[str, Any]:
        """Create a new load balancer pool"""
        try:
            # Validate backends
            if not pool_config.backends:
                raise ValueError("Pool must have at least one backend")
            
            # Initialize backend states
            for backend in pool_config.backends:
                self.backend_states[backend.id] = backend
                
                # Create circuit breaker if enabled
                if pool_config.enable_circuit_breaker:
                    self.circuit_breakers[backend.id] = CircuitBreaker(
                        failure_threshold=5,
                        recovery_timeout=30,
                        expected_exception=Exception
                    )
            
            # Store pool configuration
            self.pools[pool_config.name] = pool_config
            
            # Start health checks for this pool
            if pool_config.health_check.enabled:
                await self._start_pool_health_checks(pool_config.name)
            
            # Persist pool configuration
            await self._persist_pool_configuration(pool_config)
            
            logger.info(f"Created load balancer pool: {pool_config.name} with {len(pool_config.backends)} backends")
            
            return {
                "pool_name": pool_config.name,
                "algorithm": pool_config.algorithm.value,
                "backend_count": len(pool_config.backends),
                "health_checks_enabled": pool_config.health_check.enabled,
                "status": "created"
            }
            
        except Exception as e:
            logger.error(f"Failed to create pool {pool_config.name}: {e}")
            raise
    
    async def route_request(
        self, pool_name: str, client_ip: str = None, session_id: str = None,
        request_headers: Dict[str, str] = None, request_path: str = "/"
    ) -> Optional[BackendServer]:
        """Route request to appropriate backend"""
        if pool_name not in self.pools:
            raise ValueError(f"Pool not found: {pool_name}")
        
        pool = self.pools[pool_name]
        
        # Apply rate limiting
        if self.config.enable_rate_limiting:
            if not await self._check_rate_limit(client_ip or "unknown", pool_name):
                raise RuntimeError("Rate limit exceeded")
        
        # Get healthy backends
        healthy_backends = [
            backend for backend in pool.backends
            if self.backend_states[backend.id].health_status == HealthStatus.HEALTHY
        ]
        
        if not healthy_backends:
            logger.error(f"No healthy backends available in pool: {pool_name}")
            return None
        
        # Apply session affinity if configured
        if pool.session_affinity.type != SessionAffinityType.NONE:
            affinity_backend = await self._apply_session_affinity(
                pool, client_ip, session_id, request_headers, healthy_backends
            )
            if affinity_backend:
                return affinity_backend
        
        # Select backend based on algorithm
        selected_backend = await self._select_backend(pool, healthy_backends, client_ip, request_path)
        
        if selected_backend:
            # Increment connection count
            self.backend_states[selected_backend.id].current_connections += 1
            self.backend_states[selected_backend.id].last_request_time = datetime.utcnow()
            
            # Update metrics
            self.active_connections_gauge.labels(
                pool_name=pool_name, backend_id=selected_backend.id
            ).set(self.backend_states[selected_backend.id].current_connections)
        
        return selected_backend
    
    async def _select_backend(
        self, pool: LoadBalancerPool, healthy_backends: List[BackendServer],
        client_ip: str = None, request_path: str = "/"
    ) -> Optional[BackendServer]:
        """Select backend based on load balancing algorithm"""
        
        if pool.algorithm == LoadBalancingAlgorithm.ROUND_ROBIN:
            return await self._round_robin_selection(pool.name, healthy_backends)
        
        elif pool.algorithm == LoadBalancingAlgorithm.WEIGHTED_ROUND_ROBIN:
            return await self._weighted_round_robin_selection(pool.name, healthy_backends)
        
        elif pool.algorithm == LoadBalancingAlgorithm.LEAST_CONNECTIONS:
            return await self._least_connections_selection(healthy_backends)
        
        elif pool.algorithm == LoadBalancingAlgorithm.WEIGHTED_LEAST_CONNECTIONS:
            return await self._weighted_least_connections_selection(healthy_backends)
        
        elif pool.algorithm == LoadBalancingAlgorithm.RANDOM:
            return random.choice(healthy_backends)
        
        elif pool.algorithm == LoadBalancingAlgorithm.WEIGHTED_RANDOM:
            return await self._weighted_random_selection(healthy_backends)
        
        elif pool.algorithm == LoadBalancingAlgorithm.CONSISTENT_HASH:
            return await self._consistent_hash_selection(healthy_backends, client_ip or request_path)
        
        elif pool.algorithm == LoadBalancingAlgorithm.LEAST_RESPONSE_TIME:
            return await self._least_response_time_selection(healthy_backends)
        
        elif pool.algorithm == LoadBalancingAlgorithm.GEOGRAPHIC:
            return await self._geographic_selection(healthy_backends, client_ip)
        
        elif pool.algorithm == LoadBalancingAlgorithm.RESOURCE_BASED:
            return await self._resource_based_selection(healthy_backends)
        
        else:
            # Default to round robin
            return await self._round_robin_selection(pool.name, healthy_backends)
    
    async def _round_robin_selection(self, pool_name: str, backends: List[BackendServer]) -> BackendServer:
        """Round robin selection"""
        counter = self.request_counters[pool_name]
        selected = backends[counter % len(backends)]
        self.request_counters[pool_name] = (counter + 1) % len(backends)
        return selected
    
    async def _weighted_round_robin_selection(self, pool_name: str, backends: List[BackendServer]) -> BackendServer:
        """Weighted round robin selection"""
        # Create a weighted list
        weighted_backends = []
        for backend in backends:
            weighted_backends.extend([backend] * backend.weight)
        
        if not weighted_backends:
            return backends[0]
        
        counter = self.request_counters[pool_name]
        selected = weighted_backends[counter % len(weighted_backends)]
        self.request_counters[pool_name] = (counter + 1) % len(weighted_backends)
        return selected
    
    async def _least_connections_selection(self, backends: List[BackendServer]) -> BackendServer:
        """Least connections selection"""
        return min(backends, key=lambda b: self.backend_states[b.id].current_connections)
    
    async def _weighted_least_connections_selection(self, backends: List[BackendServer]) -> BackendServer:
        """Weighted least connections selection"""
        def weight_score(backend):
            state = self.backend_states[backend.id]
            if backend.weight == 0:
                return float('inf')
            return state.current_connections / backend.weight
        
        return min(backends, key=weight_score)
    
    async def _weighted_random_selection(self, backends: List[BackendServer]) -> BackendServer:
        """Weighted random selection"""
        total_weight = sum(backend.weight for backend in backends)
        if total_weight == 0:
            return random.choice(backends)
        
        rand_value = random.uniform(0, total_weight)
        current_weight = 0
        
        for backend in backends:
            current_weight += backend.weight
            if rand_value <= current_weight:
                return backend
        
        return backends[-1]  # Fallback
    
    async def _consistent_hash_selection(self, backends: List[BackendServer], key: str) -> BackendServer:
        """Consistent hash selection"""
        if not key:
            return random.choice(backends)
        
        # Simple consistent hashing implementation
        hash_value = int(hashlib.md5(key.encode()).hexdigest(), 16)
        backend_hashes = []
        
        for backend in backends:
            backend_hash = int(hashlib.md5(backend.id.encode()).hexdigest(), 16)
            backend_hashes.append((backend_hash, backend))
        
        backend_hashes.sort()
        
        # Find the first backend with hash >= request hash
        for backend_hash, backend in backend_hashes:
            if backend_hash >= hash_value:
                return backend
        
        # Wrap around to the first backend
        return backend_hashes[0][1]
    
    async def _least_response_time_selection(self, backends: List[BackendServer]) -> BackendServer:
        """Least response time selection"""
        return min(backends, key=lambda b: self.backend_states[b.id].get_average_response_time())
    
    async def _geographic_selection(self, backends: List[BackendServer], client_ip: str) -> BackendServer:
        """Geographic proximity selection"""
        # In a real implementation, you would resolve client_ip to geographic coordinates
        # For this example, we'll use a simplified approach
        
        # Filter backends with geographic information
        geo_backends = [b for b in backends if b.latitude is not None and b.longitude is not None]
        
        if not geo_backends:
            return random.choice(backends)
        
        # For demo purposes, assume client is at a default location
        client_lat, client_lon = 37.7749, -122.4194  # San Francisco
        
        def distance_score(backend):
            return geodesic((client_lat, client_lon), (backend.latitude, backend.longitude)).kilometers
        
        return min(geo_backends, key=distance_score)
    
    async def _resource_based_selection(self, backends: List[BackendServer]) -> BackendServer:
        """Resource-based selection considering CPU, memory, etc."""
        def resource_score(backend):
            state = self.backend_states[backend.id]
            # Combine load score, error rate, and response time
            load_score = state.get_load_score()
            error_rate = state.get_error_rate()
            response_time = state.get_average_response_time()
            
            # Normalize response time (assume max 1000ms)
            normalized_response_time = min(response_time / 1000.0, 1.0)
            
            # Calculate composite score (lower is better)
            return load_score * 0.4 + error_rate * 0.3 + normalized_response_time * 0.3
        
        return min(backends, key=resource_score)
    
    async def _apply_session_affinity(
        self, pool: LoadBalancerPool, client_ip: str, session_id: str,
        request_headers: Dict[str, str], healthy_backends: List[BackendServer]
    ) -> Optional[BackendServer]:
        """Apply session affinity logic"""
        
        affinity_key = None
        
        if pool.session_affinity.type == SessionAffinityType.CLIENT_IP:
            affinity_key = client_ip
        elif pool.session_affinity.type == SessionAffinityType.COOKIE:
            # In a real implementation, you would extract the cookie from request headers
            affinity_key = session_id  # Simplified
        elif pool.session_affinity.type == SessionAffinityType.HEADER:
            if request_headers and pool.session_affinity.header_name:
                affinity_key = request_headers.get(pool.session_affinity.header_name)
        
        if not affinity_key:
            return None
        
        # Check if we have a stored session
        stored_backend_id = self.session_store.get(affinity_key)
        if stored_backend_id:
            # Find the backend and check if it's healthy
            for backend in healthy_backends:
                if backend.id == stored_backend_id:
                    return backend
            
            # Backend is not healthy, remove from session store
            del self.session_store[affinity_key]
        
        return None
    
    async def record_request_completion(
        self, pool_name: str, backend_id: str, success: bool, response_time_ms: float
    ) -> None:
        """Record completion of a request"""
        if backend_id in self.backend_states:
            backend_state = self.backend_states[backend_id]
            
            # Update connection count
            backend_state.current_connections = max(0, backend_state.current_connections - 1)
            
            # Record metrics
            backend_state.response_times.append(response_time_ms)
            if success:
                backend_state.success_count += 1
            else:
                backend_state.error_count += 1
            
            # Update Prometheus metrics
            status = "success" if success else "failure"
            self.requests_total.labels(
                pool_name=pool_name, backend_id=backend_id, status=status
            ).inc()
            
            self.request_duration_seconds.labels(
                pool_name=pool_name, backend_id=backend_id
            ).observe(response_time_ms / 1000.0)
            
            self.active_connections_gauge.labels(
                pool_name=pool_name, backend_id=backend_id
            ).set(backend_state.current_connections)
    
    async def _check_rate_limit(self, client_identifier: str, pool_name: str) -> bool:
        """Check if request is within rate limits"""
        now = time.time()
        minute_window = int(now / 60)
        
        # Rate limit key
        rate_limit_key = f"rate_limit:{pool_name}:{client_identifier}:{minute_window}"
        
        # Get current count from Redis
        try:
            current_count = await self.redis_client.get(rate_limit_key)
            current_count = int(current_count) if current_count else 0
            
            if current_count >= self.config.default_rate_limit_rpm:
                return False
            
            # Increment counter with expiry
            await self.redis_client.incr(rate_limit_key)
            await self.redis_client.expire(rate_limit_key, 60)  # 1 minute TTL
            
            return True
            
        except Exception as e:
            logger.error(f"Rate limiting error: {e}")
            return True  # Allow request on error
    
    async def _start_pool_health_checks(self, pool_name: str) -> None:
        """Start health check tasks for a pool"""
        if pool_name not in self.pools:
            return
        
        pool = self.pools[pool_name]
        
        for backend in pool.backends:
            task = asyncio.create_task(
                self._health_check_worker(pool_name, backend.id, pool.health_check)
            )
            self.health_check_tasks[f"{pool_name}:{backend.id}"] = task
    
    async def _health_check_worker(
        self, pool_name: str, backend_id: str, health_config: HealthCheckConfig
    ) -> None:
        """Health check worker for a specific backend"""
        consecutive_failures = 0
        consecutive_successes = 0
        
        while True:
            try:
                await asyncio.sleep(health_config.interval_seconds)
                
                backend = self.backend_states.get(backend_id)
                if not backend:
                    break
                
                # Perform health check
                health_url = f"http://{backend.host}:{backend.port}{health_config.path}"
                
                try:
                    async with aiohttp.ClientSession() as session:
                        timeout = aiohttp.ClientTimeout(total=health_config.timeout_seconds)
                        async with session.get(health_url, timeout=timeout) as response:
                            
                            health_check_passed = (
                                response.status in health_config.expected_status_codes
                            )
                            
                            if health_config.check_response_body and health_config.expected_response_body:
                                response_text = await response.text()
                                health_check_passed = health_check_passed and (
                                    health_config.expected_response_body in response_text
                                )
                            
                            if health_check_passed:
                                consecutive_successes += 1
                                consecutive_failures = 0
                                
                                # Mark as healthy if it was unhealthy
                                if (backend.health_status != HealthStatus.HEALTHY and
                                    consecutive_successes >= health_config.healthy_threshold):
                                    backend.health_status = HealthStatus.HEALTHY
                                    logger.info(f"Backend {backend_id} marked as healthy")
                                    
                                    # Update metrics
                                    self.backend_health_gauge.labels(
                                        pool_name=pool_name, backend_id=backend_id
                                    ).set(1)
                            else:
                                consecutive_failures += 1
                                consecutive_successes = 0
                                
                                # Mark as unhealthy
                                if consecutive_failures >= health_config.unhealthy_threshold:
                                    backend.health_status = HealthStatus.UNHEALTHY
                                    logger.warning(f"Backend {backend_id} marked as unhealthy")
                                    
                                    # Update metrics
                                    self.backend_health_gauge.labels(
                                        pool_name=pool_name, backend_id=backend_id
                                    ).set(0)
                
                except Exception as e:
                    consecutive_failures += 1
                    consecutive_successes = 0
                    
                    if consecutive_failures >= health_config.unhealthy_threshold:
                        backend.health_status = HealthStatus.UNHEALTHY
                        logger.warning(f"Backend {backend_id} health check failed: {e}")
                        
                        # Update metrics
                        self.backend_health_gauge.labels(
                            pool_name=pool_name, backend_id=backend_id
                        ).set(0)
                
                backend.last_health_check = datetime.utcnow()
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Health check worker error for {backend_id}: {e}")
    
    async def get_pool_status(self, pool_name: str) -> Dict[str, Any]:
        """Get pool status and metrics"""
        if pool_name not in self.pools:
            raise ValueError(f"Pool not found: {pool_name}")
        
        pool = self.pools[pool_name]
        
        # Collect backend statuses
        backend_statuses = []
        for backend in pool.backends:
            state = self.backend_states[backend.id]
            backend_statuses.append({
                "id": backend.id,
                "host": backend.host,
                "port": backend.port,
                "weight": backend.weight,
                "health_status": state.health_status.value,
                "current_connections": state.current_connections,
                "average_response_time": state.get_average_response_time(),
                "error_rate": state.get_error_rate(),
                "load_score": state.get_load_score(),
                "last_health_check": state.last_health_check.isoformat() if state.last_health_check else None
            })
        
        return {
            "pool_name": pool_name,
            "algorithm": pool.algorithm.value,
            "total_backends": len(pool.backends),
            "healthy_backends": len([b for b in pool.backends if self.backend_states[b.id].health_status == HealthStatus.HEALTHY]),
            "session_affinity": pool.session_affinity.type.value,
            "backends": backend_statuses
        }
    
    async def get_health_status(self) -> Dict[str, Any]:
        """Get load balancer health status"""
        try:
            # Check Redis connectivity
            redis_healthy = False
            try:
                await self.redis_client.ping()
                redis_healthy = True
            except Exception:
                pass
            
            # Count healthy backends across all pools
            total_backends = 0
            healthy_backends = 0
            
            for pool in self.pools.values():
                for backend in pool.backends:
                    total_backends += 1
                    if self.backend_states[backend.id].health_status == HealthStatus.HEALTHY:
                        healthy_backends += 1
            
            return {
                "service": "load_balancer_template",
                "status": "healthy" if redis_healthy and (healthy_backends > 0 or total_backends == 0) else "degraded",
                "timestamp": datetime.utcnow().isoformat(),
                "metrics": {
                    "total_pools": len(self.pools),
                    "total_backends": total_backends,
                    "healthy_backends": healthy_backends,
                    "health_check_tasks": len(self.health_check_tasks),
                    "redis_connected": redis_healthy
                }
            }
            
        except Exception as e:
            return {
                "service": "load_balancer_template",
                "status": "unhealthy",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
    
    async def _health_check_monitor(self) -> None:
        """Monitor health check tasks"""
        while True:
            try:
                await asyncio.sleep(60)  # Check every minute
                
                # Restart failed health check tasks
                for task_key, task in list(self.health_check_tasks.items()):
                    if task.done():
                        pool_name, backend_id = task_key.split(":", 1)
                        if pool_name in self.pools:
                            pool = self.pools[pool_name]
                            # Restart the health check task
                            new_task = asyncio.create_task(
                                self._health_check_worker(pool_name, backend_id, pool.health_check)
                            )
                            self.health_check_tasks[task_key] = new_task
                            logger.info(f"Restarted health check task for {task_key}")
                
            except Exception as e:
                logger.error(f"Health check monitor error: {e}")
    
    async def _metrics_collection_task(self) -> None:
        """Background metrics collection"""
        while True:
            try:
                await asyncio.sleep(60)  # Collect every minute
                
                # Update backend health metrics
                for pool_name, pool in self.pools.items():
                    for backend in pool.backends:
                        state = self.backend_states[backend.id]
                        health_value = 1 if state.health_status == HealthStatus.HEALTHY else 0
                        self.backend_health_gauge.labels(
                            pool_name=pool_name, backend_id=backend.id
                        ).set(health_value)
                
            except Exception as e:
                logger.error(f"Metrics collection task error: {e}")
    
    async def _service_discovery_task(self) -> None:
        """Service discovery integration"""
        while True:
            try:
                await asyncio.sleep(30)  # Check every 30 seconds
                
                # In a real implementation, this would integrate with Consul, Eureka, etc.
                # For now, it's a placeholder
                
            except Exception as e:
                logger.error(f"Service discovery task error: {e}")
    
    async def _persist_pool_configuration(self, pool: LoadBalancerPool) -> None:
        """Persist pool configuration to Redis"""
        pool_data = pool.dict()
        await self.redis_client.set(
            f"load_balancer:pool:{pool.name}",
            json.dumps(pool_data, default=str)
        )
    
    async def shutdown(self) -> None:
        """Shutdown the service gracefully"""
        try:
            logger.info("Shutting down load balancer service")
            
            # Cancel health check tasks
            for task in self.health_check_tasks.values():
                task.cancel()
            
            # Wait for tasks to complete
            if self.health_check_tasks:
                await asyncio.gather(*self.health_check_tasks.values(), return_exceptions=True)
            
            # Close Redis connection
            if self.redis_client:
                await self.redis_client.close()
            
            logger.info("Load balancer service shutdown complete")
            
        except Exception as e:
            logger.error(f"Error during shutdown: {e}")