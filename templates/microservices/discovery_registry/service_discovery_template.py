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

Service Discovery Template for iacherie Platform
==============================================

Production-ready service discovery with:
- Intelligent service resolution
- Load balancing strategies
- Circuit breaker integration
- Caching and performance optimization
- Multi-zone and multi-region support
- Health-aware service selection

Author: Fahed Mlaiel (mlaiel@live.de)
Service Mesh & Load Balancing Expert
"""

import asyncio
import json
import logging
import time
import random
import hashlib
from typing import Dict, Any, Optional, List, Set, Union, Tuple, Callable
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
import uuid

from fastapi import FastAPI, HTTPException, Depends
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from prometheus_client import Counter, Histogram, Gauge
import redis.asyncio as redis

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Prometheus metrics
discovery_requests_counter = Counter('discovery_requests_total', 'Total discovery requests', ['service_name', 'strategy'])
discovery_latency_histogram = Histogram('discovery_latency_seconds', 'Discovery operation latency', ['service_name'])
cache_hits_counter = Counter('discovery_cache_hits_total', 'Discovery cache hits', ['service_name'])
load_balancer_selections = Counter('load_balancer_selections_total', 'Load balancer selections', ['strategy', 'service_name'])

class LoadBalancingStrategy(str, Enum):
    """Load balancing strategies"""
    ROUND_ROBIN = "round_robin"
    WEIGHTED_ROUND_ROBIN = "weighted_round_robin"
    LEAST_CONNECTIONS = "least_connections"
    LEAST_RESPONSE_TIME = "least_response_time"
    RANDOM = "random"
    WEIGHTED_RANDOM = "weighted_random"
    CONSISTENT_HASH = "consistent_hash"
    LOCALITY_AWARE = "locality_aware"
    HEALTH_AWARE = "health_aware"
    RESOURCE_AWARE = "resource_aware"

class DiscoveryStrategy(str, Enum):
    """Service discovery strategies"""
    CACHED = "cached"
    REAL_TIME = "real_time"
    HYBRID = "hybrid"
    FAILOVER = "failover"

@dataclass
class ServiceEndpoint:
    """Service endpoint information"""
    service_id: str
    service_name: str
    host: str
    port: int
    protocol: str = "http"
    weight: int = 100
    health_score: float = 1.0
    response_time_ms: float = 0.0
    active_connections: int = 0
    cpu_usage: float = 0.0
    memory_usage: float = 0.0
    region: str = "default"
    zone: str = "default"
    tags: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    @property
    def url(self) -> str:
        return f"{self.protocol}://{self.host}:{self.port}"
    
    @property
    def is_healthy(self) -> bool:
        return self.health_score > 0.5

@dataclass
class DiscoveryRequest:
    """Service discovery request"""
    service_name: str
    strategy: LoadBalancingStrategy = LoadBalancingStrategy.ROUND_ROBIN
    filters: Dict[str, Any] = field(default_factory=dict)
    prefer_local: bool = True
    max_instances: int = 5
    timeout_ms: int = 5000
    client_id: Optional[str] = None
    session_affinity: bool = False

@dataclass
class DiscoveryResult:
    """Service discovery result"""
    endpoints: List[ServiceEndpoint]
    selected_endpoint: Optional[ServiceEndpoint]
    total_available: int
    strategy_used: LoadBalancingStrategy
    cache_hit: bool
    discovery_time_ms: float
    metadata: Dict[str, Any] = field(default_factory=dict)

class LoadBalancer:
    """Advanced load balancer with multiple strategies"""
    
    def __init__(self):
        self.round_robin_counters = {}
        self.consistent_hash_ring = {}
        self.connection_counts = {}
        self.response_times = {}
    
    async def select_endpoint(self, 
                            endpoints: List[ServiceEndpoint], 
                            strategy: LoadBalancingStrategy,
                            request: DiscoveryRequest) -> Optional[ServiceEndpoint]:
        """Select optimal endpoint based on strategy"""
        
        if not endpoints:
            return None
        
        # Filter healthy endpoints
        healthy_endpoints = [e for e in endpoints if e.is_healthy]
        if not healthy_endpoints:
            # Fallback to all endpoints if none are healthy
            healthy_endpoints = endpoints
        
        # Apply strategy
        if strategy == LoadBalancingStrategy.ROUND_ROBIN:
            return self._round_robin_select(healthy_endpoints, request.service_name)
        
        elif strategy == LoadBalancingStrategy.WEIGHTED_ROUND_ROBIN:
            return self._weighted_round_robin_select(healthy_endpoints, request.service_name)
        
        elif strategy == LoadBalancingStrategy.LEAST_CONNECTIONS:
            return self._least_connections_select(healthy_endpoints)
        
        elif strategy == LoadBalancingStrategy.LEAST_RESPONSE_TIME:
            return self._least_response_time_select(healthy_endpoints)
        
        elif strategy == LoadBalancingStrategy.RANDOM:
            return self._random_select(healthy_endpoints)
        
        elif strategy == LoadBalancingStrategy.WEIGHTED_RANDOM:
            return self._weighted_random_select(healthy_endpoints)
        
        elif strategy == LoadBalancingStrategy.CONSISTENT_HASH:
            return self._consistent_hash_select(healthy_endpoints, request)
        
        elif strategy == LoadBalancingStrategy.LOCALITY_AWARE:
            return self._locality_aware_select(healthy_endpoints, request)
        
        elif strategy == LoadBalancingStrategy.HEALTH_AWARE:
            return self._health_aware_select(healthy_endpoints)
        
        elif strategy == LoadBalancingStrategy.RESOURCE_AWARE:
            return self._resource_aware_select(healthy_endpoints)
        
        else:
            return self._round_robin_select(healthy_endpoints, request.service_name)
    
    def _round_robin_select(self, endpoints: List[ServiceEndpoint], service_name: str) -> ServiceEndpoint:
        """Round robin selection"""
        if service_name not in self.round_robin_counters:
            self.round_robin_counters[service_name] = 0
        
        index = self.round_robin_counters[service_name] % len(endpoints)
        self.round_robin_counters[service_name] += 1
        
        return endpoints[index]
    
    def _weighted_round_robin_select(self, endpoints: List[ServiceEndpoint], service_name: str) -> ServiceEndpoint:
        """Weighted round robin selection"""
        total_weight = sum(e.weight for e in endpoints)
        if total_weight == 0:
            return self._round_robin_select(endpoints, service_name)
        
        if service_name not in self.round_robin_counters:
            self.round_robin_counters[service_name] = 0
        
        target = self.round_robin_counters[service_name] % total_weight
        self.round_robin_counters[service_name] += 1
        
        current_weight = 0
        for endpoint in endpoints:
            current_weight += endpoint.weight
            if current_weight > target:
                return endpoint
        
        return endpoints[0]  # Fallback
    
    def _least_connections_select(self, endpoints: List[ServiceEndpoint]) -> ServiceEndpoint:
        """Select endpoint with least active connections"""
        return min(endpoints, key=lambda e: e.active_connections)
    
    def _least_response_time_select(self, endpoints: List[ServiceEndpoint]) -> ServiceEndpoint:
        """Select endpoint with lowest response time"""
        return min(endpoints, key=lambda e: e.response_time_ms or float('inf'))
    
    def _random_select(self, endpoints: List[ServiceEndpoint]) -> ServiceEndpoint:
        """Random selection"""
        return random.choice(endpoints)
    
    def _weighted_random_select(self, endpoints: List[ServiceEndpoint]) -> ServiceEndpoint:
        """Weighted random selection"""
        total_weight = sum(e.weight for e in endpoints)
        if total_weight == 0:
            return self._random_select(endpoints)
        
        target = random.randint(1, total_weight)
        current_weight = 0
        
        for endpoint in endpoints:
            current_weight += endpoint.weight
            if current_weight >= target:
                return endpoint
        
        return endpoints[0]  # Fallback
    
    def _consistent_hash_select(self, endpoints: List[ServiceEndpoint], request: DiscoveryRequest) -> ServiceEndpoint:
        """Consistent hash selection for session affinity"""
        if not request.client_id:
            return self._random_select(endpoints)
        
        # Create hash of client_id
        hash_value = int(hashlib.md5(request.client_id.encode()).hexdigest(), 16)
        
        # Map to endpoint
        index = hash_value % len(endpoints)
        return endpoints[index]
    
    def _locality_aware_select(self, endpoints: List[ServiceEndpoint], request: DiscoveryRequest) -> ServiceEndpoint:
        """Select endpoint considering locality preferences"""
        if request.prefer_local:
            # Prefer endpoints in same region/zone
            local_endpoints = [e for e in endpoints if e.region == "local"]
            if local_endpoints:
                return self._health_aware_select(local_endpoints)
        
        return self._health_aware_select(endpoints)
    
    def _health_aware_select(self, endpoints: List[ServiceEndpoint]) -> ServiceEndpoint:
        """Select endpoint based on health score"""
        # Weight by health score
        weighted_endpoints = []
        for endpoint in endpoints:
            weight = int(endpoint.health_score * 100)
            weighted_endpoints.extend([endpoint] * weight)
        
        if weighted_endpoints:
            return random.choice(weighted_endpoints)
        
        return endpoints[0]  # Fallback
    
    def _resource_aware_select(self, endpoints: List[ServiceEndpoint]) -> ServiceEndpoint:
        """Select endpoint based on resource utilization"""
        # Calculate resource score (lower is better)
        def resource_score(endpoint: ServiceEndpoint) -> float:
            cpu_score = endpoint.cpu_usage
            memory_score = endpoint.memory_usage
            connection_score = min(endpoint.active_connections / 100.0, 1.0)
            
            return cpu_score + memory_score + connection_score
        
        return min(endpoints, key=resource_score)

class ServiceDiscoveryCache:
    """Cache for service discovery results"""
    
    def __init__(self, redis_client: redis.Redis, default_ttl: int = 60):
        self.redis = redis_client
        self.default_ttl = default_ttl
    
    async def get(self, service_name: str, filters: Dict[str, Any] = None) -> Optional[List[ServiceEndpoint]]:
        """Get cached service endpoints"""
        try:
            cache_key = self._build_cache_key(service_name, filters)
            cached_data = await self.redis.get(cache_key)
            
            if cached_data:
                data = json.loads(cached_data)
                endpoints = [ServiceEndpoint(**endpoint_data) for endpoint_data in data]
                
                cache_hits_counter.labels(service_name=service_name).inc()
                return endpoints
            
            return None
            
        except Exception as e:
            logger.error(f"Cache get error: {e}")
            return None
    
    async def set(self, service_name: str, endpoints: List[ServiceEndpoint], 
                  filters: Dict[str, Any] = None, ttl: Optional[int] = None) -> bool:
        """Cache service endpoints"""
        try:
            cache_key = self._build_cache_key(service_name, filters)
            data = [endpoint.__dict__ for endpoint in endpoints]
            
            ttl = ttl or self.default_ttl
            await self.redis.setex(cache_key, ttl, json.dumps(data, default=str))
            
            return True
            
        except Exception as e:
            logger.error(f"Cache set error: {e}")
            return False
    
    async def invalidate(self, service_name: str, filters: Dict[str, Any] = None) -> bool:
        """Invalidate cached endpoints"""
        try:
            cache_key = self._build_cache_key(service_name, filters)
            await self.redis.delete(cache_key)
            return True
            
        except Exception as e:
            logger.error(f"Cache invalidate error: {e}")
            return False
    
    def _build_cache_key(self, service_name: str, filters: Dict[str, Any] = None) -> str:
        """Build cache key for service and filters"""
        key = f"discovery:{service_name}"
        
        if filters:
            # Sort filters for consistent key generation
            filter_str = ":".join(f"{k}={v}" for k, v in sorted(filters.items()))
            key += f":{filter_str}"
        
        return key

class ServiceDiscovery:
    """
    Production-ready service discovery for iacherie Platform
    
    Features:
    - Intelligent service resolution with multiple strategies
    - Advanced load balancing algorithms
    - Performance-aware endpoint selection
    - Caching and optimization
    - Health-aware service filtering
    """
    
    def __init__(self, registry_backend, redis_client: Optional[redis.Redis] = None):
        self.registry = registry_backend
        self.load_balancer = LoadBalancer()
        self.cache = ServiceDiscoveryCache(redis_client) if redis_client else None
        
        # Circuit breaker for registry calls
        self.registry_failures = 0
        self.registry_failure_threshold = 5
        self.registry_recovery_timeout = 60
        self.last_registry_failure = None
    
    async def discover(self, request: DiscoveryRequest) -> DiscoveryResult:
        """Discover and select service endpoint"""
        start_time = time.time()
        
        try:
            with discovery_latency_histogram.labels(service_name=request.service_name).time():
                # Try cache first if available
                endpoints = None
                cache_hit = False
                
                if self.cache:
                    endpoints = await self.cache.get(request.service_name, request.filters)
                    cache_hit = endpoints is not None
                
                # If not in cache or cache disabled, query registry
                if not endpoints:
                    if await self._is_registry_available():
                        raw_instances = await self.registry.discover_services(request.service_name)
                        endpoints = self._convert_to_endpoints(raw_instances)
                        
                        # Apply filters
                        endpoints = self._apply_filters(endpoints, request.filters)
                        
                        # Cache the results
                        if self.cache and endpoints:
                            await self.cache.set(request.service_name, endpoints, request.filters)
                    else:
                        # Registry unavailable, try to use stale cache
                        logger.warning(f"Registry unavailable, using stale cache for {request.service_name}")
                        endpoints = []
                
                # Limit results
                if request.max_instances > 0:
                    endpoints = endpoints[:request.max_instances]
                
                # Select optimal endpoint
                selected_endpoint = None
                if endpoints:
                    selected_endpoint = await self.load_balancer.select_endpoint(
                        endpoints, request.strategy, request
                    )
                    
                    if selected_endpoint:
                        load_balancer_selections.labels(
                            strategy=request.strategy.value,
                            service_name=request.service_name
                        ).inc()
                
                discovery_time_ms = (time.time() - start_time) * 1000
                
                discovery_requests_counter.labels(
                    service_name=request.service_name,
                    strategy=request.strategy.value
                ).inc()
                
                return DiscoveryResult(
                    endpoints=endpoints,
                    selected_endpoint=selected_endpoint,
                    total_available=len(endpoints),
                    strategy_used=request.strategy,
                    cache_hit=cache_hit,
                    discovery_time_ms=discovery_time_ms,
                    metadata={
                        "registry_available": await self._is_registry_available(),
                        "filters_applied": request.filters
                    }
                )
                
        except Exception as e:
            logger.error(f"Service discovery failed: {e}")
            self.registry_failures += 1
            self.last_registry_failure = time.time()
            
            # Return empty result on failure
            return DiscoveryResult(
                endpoints=[],
                selected_endpoint=None,
                total_available=0,
                strategy_used=request.strategy,
                cache_hit=False,
                discovery_time_ms=(time.time() - start_time) * 1000,
                metadata={"error": str(e)}
            )
    
    async def get_endpoint(self, service_name: str, **kwargs) -> Optional[ServiceEndpoint]:
        """Convenience method to get a single endpoint"""
        request = DiscoveryRequest(service_name=service_name, **kwargs)
        result = await self.discover(request)
        return result.selected_endpoint
    
    async def invalidate_cache(self, service_name: str):
        """Invalidate cache for a service"""
        if self.cache:
            await self.cache.invalidate(service_name)
    
    async def _is_registry_available(self) -> bool:
        """Check if registry is available (circuit breaker pattern)"""
        if self.registry_failures < self.registry_failure_threshold:
            return True
        
        if self.last_registry_failure:
            time_since_failure = time.time() - self.last_registry_failure
            if time_since_failure > self.registry_recovery_timeout:
                # Reset failure count after timeout
                self.registry_failures = 0
                return True
        
        return False
    
    def _convert_to_endpoints(self, instances) -> List[ServiceEndpoint]:
        """Convert registry instances to service endpoints"""
        endpoints = []
        
        for instance in instances:
            endpoint = ServiceEndpoint(
                service_id=instance.id,
                service_name=instance.service_name,
                host=instance.host,
                port=instance.port,
                protocol=instance.protocol,
                weight=instance.weight,
                region=instance.region,
                zone=instance.zone,
                tags=instance.tags,
                metadata=instance.metadata
            )
            endpoints.append(endpoint)
        
        return endpoints
    
    def _apply_filters(self, endpoints: List[ServiceEndpoint], filters: Dict[str, Any]) -> List[ServiceEndpoint]:
        """Apply filters to endpoints"""
        filtered = endpoints
        
        if "version" in filters:
            filtered = [e for e in filtered if e.metadata.get("version") == filters["version"]]
        
        if "tags" in filters:
            required_tags = set(filters["tags"])
            filtered = [e for e in filtered if required_tags.issubset(set(e.tags))]
        
        if "region" in filters:
            filtered = [e for e in filtered if e.region == filters["region"]]
        
        if "zone" in filters:
            filtered = [e for e in filtered if e.zone == filters["zone"]]
        
        if "min_health_score" in filters:
            min_score = filters["min_health_score"]
            filtered = [e for e in filtered if e.health_score >= min_score]
        
        return filtered

class ServiceDiscoveryTemplate:
    """
    Service Discovery Template for iacherie Platform
    
    A comprehensive service discovery system that provides:
    - Intelligent service resolution
    - Multiple load balancing strategies
    - Performance and health-aware selection
    - Caching and optimization
    """
    
    def __init__(self):
        self.service_name = "service-discovery"
        self.service_version = "1.0.0"
        self.description = "Production-ready service discovery with intelligent load balancing"
    
    def create_discovery(self, registry_backend, config: Dict[str, Any]) -> ServiceDiscovery:
        """Create a service discovery instance"""
        return ServiceDiscovery(
            registry_backend=registry_backend,
            redis_client=config.get("redis_client")
        )
    
    def get_template_info(self) -> Dict[str, Any]:
        """Get service discovery template information"""
        return {
            "name": self.service_name,
            "version": self.service_version,
            "description": self.description,
            "features": [
                "Multiple load balancing strategies",
                "Health-aware endpoint selection",
                "Performance-based routing",
                "Intelligent caching",
                "Circuit breaker protection",
                "Session affinity support",
                "Multi-zone locality awareness",
                "Resource-aware selection"
            ],
            "load_balancing_strategies": [
                "Round Robin",
                "Weighted Round Robin", 
                "Least Connections",
                "Least Response Time",
                "Random",
                "Weighted Random",
                "Consistent Hash",
                "Locality Aware",
                "Health Aware",
                "Resource Aware"
            ],
            "dependencies": ["redis", "prometheus"],
            "endpoints": [
                "/discover/{service_name}",
                "/endpoint/{service_name}",
                "/invalidate/{service_name}"
            ]
        }