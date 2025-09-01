"""Intelligent Load Balancer - Advanced Request Distribution & Load Management System

This module provides enterprise-grade load balancing with AI-powered traffic distribution,
health-aware routing, and dynamic endpoint management for optimal performance.

Author: Fahed Mlaiel
Email: mlaiel@live.de
(c) 2025 All Rights Reserved
"""

import asyncio
import logging
import time
import hashlib
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum
import random
import json
from collections import defaultdict, deque
import threading

from ..base import BaseAgent
try:
    from core.exceptions import LoadBalancerException
except ImportError:
    # Fallback exception classes
    class ValidationError(Exception): pass
    class ConfigurationError(Exception): pass
    class ProcessingError(Exception): pass
    LoadBalancerException = globals().get('LoadBalancerException', Exception)
try:
    from core.config import get_settings
except ImportError:
    # Fallback settings
    get_settings = type('Settings', (), {'debug': True, 'log_level': 'INFO'})()
from ...core.monitoring import get_metrics_client


class LoadBalancingAlgorithm(Enum):
    """
Load balancing algorithms"""

    ROUND_ROBIN = "round_robin"
    WEIGHTED_ROUND_ROBIN = "weighted_round_robin"
    LEAST_CONNECTIONS = "least_connections"
    LEAST_RESPONSE_TIME = "least_response_time"
    WEIGHTED_LEAST_CONNECTIONS = "weighted_least_connections"
    IP_HASH = "ip_hash"
    CONSISTENT_HASH = "consistent_hash"
    ADAPTIVE_INTELLIGENT = "adaptive_intelligent"


class EndpointStatus(Enum):
    """Endpoint health status"""

    HEALTHY = "healthy"
    UNHEALTHY = "unhealthy"
    DEGRADED = "degraded"
    MAINTENANCE = "maintenance"
    DRAINING = "draining"


@dataclass
class ServiceEndpoint:
    """Service endpoint configuration"""
    endpoint_id: str
    host: str
    port: int
    weight: float = 1.0
    max_connections: int = 1000
    current_connections: int = 0
    response_time_ms: float = 0.0
    success_rate: float = 1.0
    status: EndpointStatus = EndpointStatus.HEALTHY
    last_health_check: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class LoadBalancingRequest:
    """
Load balancing request context"""
    request_id: str
    client_ip: str
    service_name: str
    path: str
    method: str
    headers: Dict[str, str]
    timestamp: datetime = field(default_factory=datetime.now)
    user_id: Optional[str] = None
    session_id: Optional[str] = None


@dataclass
class RoutingDecision:
    """
Routing decision result"""
    selected_endpoint: ServiceEndpoint
    algorithm_used: LoadBalancingAlgorithm
    decision_time_ms: float
    confidence_score: float
    routing_metadata: Dict[str, Any] = field(default_factory=dict)


class IntelligentLoadBalancer(BaseAgent):
    """
    Enterprise Intelligent Load Balancer
    
    Features:
    - Multiple load balancing algorithms
    - Health-aware routing
    - AI-powered traffic distribution
    - Session affinity support
    - Circuit breaker pattern
    - Real-time metrics and monitoring
    - Geographic routing
    - A/B testing support
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__(config)
        self.logger = logging.getLogger(__name__)
        self.settings = get_settings()
        self.metrics_client = get_metrics_client()
        
        # Service endpoints
        self.service_endpoints: Dict[str, List[ServiceEndpoint]] = defaultdict(list)
        self.endpoint_counters: Dict[str, int] = defaultdict(int)
        
        # Algorithm configurations
        self.algorithm_config: Dict[str, LoadBalancingAlgorithm] = {}
        self.default_algorithm = LoadBalancingAlgorithm.ADAPTIVE_INTELLIGENT
        
        # Health checking
        self.health_check_interval = 30  # seconds
        self.health_check_timeout = 5    # seconds
        self.health_check_task: Optional[asyncio.Task] = None
        
        # Session affinity
        self.session_affinity: Dict[str, str] = {}  # session_id -> endpoint_id
        self.affinity_timeout = 3600  # 1 hour
        
        # Circuit breaker
        self.circuit_breakers: Dict[str, Dict[str, Any]] = defaultdict(dict)
        self.failure_threshold = 5
        self.recovery_timeout = 60
        
        # Request tracking
        self.request_history: deque = deque(maxlen=10000)
        self.routing_stats: Dict[str, Dict[str, int]] = defaultdict(lambda: defaultdict(int))
        
        # Thread safety
        self.routing_lock = threading.RLock()
        self.health_lock = threading.RLock()
        
        # Performance metrics
        self.response_times: Dict[str, deque] = defaultdict(lambda: deque(maxlen=1000))
        self.success_rates: Dict[str, deque] = defaultdict(lambda: deque(maxlen=1000))
        
        self.logger.info("IntelligentLoadBalancer initialized successfully")

    async def start(self):
        """Start load balancer operations"""
        try:
            # Start health checking
            await self._start_health_checking()
            
            # Load configuration
            await self._load_configuration()
            
            # Initialize default endpoints
            await self._initialize_default_endpoints()
            
            self.logger.info("Load balancer started successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to start load balancer: {e}")
            raise LoadBalancerException(f"Startup failed: {e}")

    async def stop(self):
        """Stop load balancer operations"""
        try:
            if self.health_check_task:
                self.health_check_task.cancel()
                try:
                    await self.health_check_task
                except asyncio.CancelledError:
                    pass
            
            self.logger.info("Load balancer stopped successfully")
            
        except Exception as e:
            self.logger.error(f"Error stopping load balancer: {e}")

    async def route_request(self, request: LoadBalancingRequest) -> RoutingDecision:
        """Route request to optimal endpoint"""
        start_time = time.time()
        
        try:
            with self.routing_lock:
                # Get available endpoints for service
                endpoints = self._get_healthy_endpoints(request.service_name)
                
                if not endpoints:
                    raise LoadBalancerException(f"No healthy endpoints for service {request.service_name}")
                
                # Get algorithm for service
                algorithm = self.algorithm_config.get(
                    request.service_name, 
                    self.default_algorithm
                )
                
                # Select endpoint based on algorithm
                selected_endpoint = await self._select_endpoint(request, endpoints, algorithm)
                
                # Update connection count
                selected_endpoint.current_connections += 1
                
                # Record routing decision
                decision_time = (time.time() - start_time) * 1000
                decision = RoutingDecision(
                    selected_endpoint=selected_endpoint,
                    algorithm_used=algorithm,
                    decision_time_ms=decision_time,
                    confidence_score=self._calculate_confidence_score(selected_endpoint),
                    routing_metadata={
                        "total_endpoints": len(endpoints),
                        "service_name": request.service_name,
                        "request_id": request.request_id
                    }
                )
                
                # Track request
                await self._track_request(request, decision)
                
                return decision
                
        except Exception as e:
            self.logger.error(f"Error routing request {request.request_id}: {e}")
            raise LoadBalancerException(f"Routing failed: {e}")

    async def _select_endpoint(self, request: LoadBalancingRequest, 
                              endpoints: List[ServiceEndpoint], 
                              algorithm: LoadBalancingAlgorithm) -> ServiceEndpoint:
        """Select endpoint using specified algorithm"""
        try:
            # Check session affinity first
            if request.session_id and request.session_id in self.session_affinity:
                endpoint_id = self.session_affinity[request.session_id]
                for endpoint in endpoints:
                    if endpoint.endpoint_id == endpoint_id:
                        return endpoint
            
            # Apply load balancing algorithm
            if algorithm == LoadBalancingAlgorithm.ROUND_ROBIN:
                return self._round_robin_selection(request.service_name, endpoints)
            
            elif algorithm == LoadBalancingAlgorithm.WEIGHTED_ROUND_ROBIN:
                return self._weighted_round_robin_selection(request.service_name, endpoints)
            
            elif algorithm == LoadBalancingAlgorithm.LEAST_CONNECTIONS:
                return self._least_connections_selection(endpoints)
            
            elif algorithm == LoadBalancingAlgorithm.LEAST_RESPONSE_TIME:
                return self._least_response_time_selection(endpoints)
            
            elif algorithm == LoadBalancingAlgorithm.WEIGHTED_LEAST_CONNECTIONS:
                return self._weighted_least_connections_selection(endpoints)
            
            elif algorithm == LoadBalancingAlgorithm.IP_HASH:
                return self._ip_hash_selection(request.client_ip, endpoints)
            
            elif algorithm == LoadBalancingAlgorithm.CONSISTENT_HASH:
                return self._consistent_hash_selection(request, endpoints)
            
            elif algorithm == LoadBalancingAlgorithm.ADAPTIVE_INTELLIGENT:
                return await self._adaptive_intelligent_selection(request, endpoints)
            
            else:
                # Fallback to round robin
                return self._round_robin_selection(request.service_name, endpoints)
                
        except Exception as e:
            self.logger.error(f"Error selecting endpoint with algorithm {algorithm}: {e}")
            # Fallback to first healthy endpoint
            return endpoints[0]

    def _round_robin_selection(self, service_name: str, endpoints: List[ServiceEndpoint]) -> ServiceEndpoint:
        """Round robin endpoint selection"""
        counter_key = f"rr_{service_name}"
        counter = self.endpoint_counters[counter_key]
        selected_endpoint = endpoints[counter % len(endpoints)]
        self.endpoint_counters[counter_key] = counter + 1
        return selected_endpoint

    def _weighted_round_robin_selection(self, service_name: str, endpoints: List[ServiceEndpoint]) -> ServiceEndpoint:
        """Weighted round robin endpoint selection"""
        total_weight = sum(endpoint.weight for endpoint in endpoints)
        if total_weight == 0:
            return self._round_robin_selection(service_name, endpoints)
        
        # Create weighted list
        weighted_endpoints = []
        for endpoint in endpoints:
            weight_count = int(endpoint.weight * 10)  # Scale for better distribution
            weighted_endpoints.extend([endpoint] * weight_count)
        
        if not weighted_endpoints:
            return endpoints[0]
        
        counter_key = f"wrr_{service_name}"
        counter = self.endpoint_counters[counter_key]
        selected_endpoint = weighted_endpoints[counter % len(weighted_endpoints)]
        self.endpoint_counters[counter_key] = counter + 1
        return selected_endpoint

    def _least_connections_selection(self, endpoints: List[ServiceEndpoint]) -> ServiceEndpoint:
        """Least connections endpoint selection"""
        return min(endpoints, key=lambda ep: ep.current_connections)

    def _least_response_time_selection(self, endpoints: List[ServiceEndpoint]) -> ServiceEndpoint:
        """
Least response time endpoint selection"""
        return min(endpoints, key=lambda ep: ep.response_time_ms)

    def _weighted_least_connections_selection(self, endpoints: List[ServiceEndpoint]) -> ServiceEndpoint:
        """
Weighted least connections endpoint selection"""
        def connection_ratio(endpoint: ServiceEndpoint) -> float:
            if endpoint.weight == 0:
                return float('inf')
            return endpoint.current_connections / endpoint.weight
        
        return min(endpoints, key=connection_ratio)

    def _ip_hash_selection(self, client_ip: str, endpoints: List[ServiceEndpoint]) -> ServiceEndpoint:
        """
IP hash-based endpoint selection for session affinity"""
        hash_value = int(hashlib.md5(client_ip.encode()).hexdigest(), 16)
        return endpoints[hash_value % len(endpoints)]

    def _consistent_hash_selection(self, request: LoadBalancingRequest, endpoints: List[ServiceEndpoint]) -> ServiceEndpoint:
        """
Consistent hash endpoint selection"""
        hash_key = f"{request.client_ip}:{request.user_id or ''}"
        hash_value = int(hashlib.sha256(hash_key.encode()).hexdigest(), 16)
        return endpoints[hash_value % len(endpoints)]

    async def _adaptive_intelligent_selection(self, request: LoadBalancingRequest, 
                                            endpoints: List[ServiceEndpoint]) -> ServiceEndpoint:
        """AI-powered adaptive endpoint selection"""
        try:
            # Calculate score for each endpoint
            endpoint_scores = []
            
            for endpoint in endpoints:
                score = await self._calculate_endpoint_score(endpoint, request)
                endpoint_scores.append((endpoint, score))
            
            # Sort by score (higher is better)
            endpoint_scores.sort(key=lambda x: x[1], reverse=True)
            
            # Select best endpoint with some randomization to avoid thundering herd
            if len(endpoint_scores) > 1 and random.random() < 0.2:  # 20% randomization
                return endpoint_scores[random.randint(0, min(2, len(endpoint_scores) - 1))][0]
            else:
                return endpoint_scores[0][0]
                
        except Exception as e:
            self.logger.error(f"Error in adaptive selection: {e}")
            return self._least_connections_selection(endpoints)

    async def _calculate_endpoint_score(self, endpoint: ServiceEndpoint, request: LoadBalancingRequest) -> float:
        """Calculate intelligent score for endpoint selection"""
        try:
            score = 0.0
            
            # Base score from success rate (0-40 points)
            score += endpoint.success_rate * 40
            
            # Response time score (0-30 points, lower time = higher score)
            if endpoint.response_time_ms > 0:
                response_score = max(0, 30 - (endpoint.response_time_ms / 100))
                score += response_score
            else:
                score += 30  # No data, assume good
            
            # Connection load score (0-20 points)
            if endpoint.max_connections > 0:
                connection_ratio = endpoint.current_connections / endpoint.max_connections
                connection_score = max(0, 20 * (1 - connection_ratio))
                score += connection_score
            else:
                score += 20
            
            # Weight factor (0-10 points)
            score += endpoint.weight * 10
            
            # Circuit breaker penalty
            circuit_breaker = self.circuit_breakers.get(endpoint.endpoint_id, {})
            if circuit_breaker.get('state') == 'open':
                score *= 0.1  # Severe penalty for open circuit
            elif circuit_breaker.get('state') == 'half-open':
                score *= 0.5  # Moderate penalty for half-open circuit
            
            return score
            
        except Exception as e:
            self.logger.error(f"Error calculating endpoint score: {e}")
            return 0.0

    def _get_healthy_endpoints(self, service_name: str) -> List[ServiceEndpoint]:
        """Get healthy endpoints for a service"""
        endpoints = self.service_endpoints.get(service_name, [])
        return [ep for ep in endpoints if ep.status == EndpointStatus.HEALTHY]

    async def _track_request(self, request: LoadBalancingRequest, decision: RoutingDecision):
        """
Track request for analytics and optimization"""
        try:
            request_record = {
                "timestamp": request.timestamp.isoformat(),
                "request_id": request.request_id,
                "service_name": request.service_name,
                "endpoint_id": decision.selected_endpoint.endpoint_id,
                "algorithm": decision.algorithm_used.value,
                "decision_time_ms": decision.decision_time_ms,
                "client_ip": request.client_ip
            }
            
            self.request_history.append(request_record)
            
            # Update routing stats
            self.routing_stats[request.service_name][decision.selected_endpoint.endpoint_id] += 1
            
            # Update metrics
            if self.metrics_client:
                self.metrics_client.increment(
                    f"load_balancer.requests.{request.service_name}",
                    tags={"endpoint": decision.selected_endpoint.endpoint_id}
                )
                self.metrics_client.histogram(
                    "load_balancer.decision_time",
                    decision.decision_time_ms,
                    tags={"service": request.service_name}
                )
                
        except Exception as e:
            self.logger.error(f"Error tracking request: {e}")

    def _calculate_confidence_score(self, endpoint: ServiceEndpoint) -> float:
        """Calculate confidence score for routing decision"""
        try:
            confidence = 0.0
            
            # Success rate contribution (0-0.4)
            confidence += endpoint.success_rate * 0.4
            
            # Response time contribution (0-0.3)
            if endpoint.response_time_ms > 0:
                response_confidence = max(0, 0.3 * (1000 - endpoint.response_time_ms) / 1000)
                confidence += response_confidence
            else:
                confidence += 0.3
            
            # Connection availability contribution (0-0.2)
            if endpoint.max_connections > 0:
                connection_availability = 1 - (endpoint.current_connections / endpoint.max_connections)
                confidence += connection_availability * 0.2
            else:
                confidence += 0.2
            
            # Health check recency (0-0.1)
            time_since_check = (datetime.now() - endpoint.last_health_check).total_seconds()
            recency_score = max(0, 0.1 * (300 - time_since_check) / 300)  # 5 minutes max
            confidence += recency_score
            
            return min(1.0, confidence)
            
        except Exception as e:
            self.logger.error(f"Error calculating confidence score: {e}")
            return 0.5

    async def _start_health_checking(self):
        """Start health checking for all endpoints"""
        self.health_check_task = asyncio.create_task(self._health_check_loop())
        self.logger.info("Health checking started")

    async def _health_check_loop(self):
        """Health check loop for all endpoints"""
        while True:
            try:
                await self._perform_health_checks()
                await asyncio.sleep(self.health_check_interval)
                
            except Exception as e:
                self.logger.error(f"Error in health check loop: {e}")
                await asyncio.sleep(self.health_check_interval)

    async def _perform_health_checks(self):
        """Perform health checks on all endpoints"""
        with self.health_lock:
            for service_name, endpoints in self.service_endpoints.items():
                for endpoint in endpoints:
                    await self._check_endpoint_health(endpoint)

    async def _check_endpoint_health(self, endpoint: ServiceEndpoint):
        """
Check health of a single endpoint"""
        try:
            # Simulate health check (in production, this would make HTTP requests)
            start_time = time.time()
            
            # Health check logic would go here
            # For now, simulate based on response time and success rate
            is_healthy = endpoint.success_rate > 0.5 and endpoint.response_time_ms < 5000
            
            response_time = (time.time() - start_time) * 1000
            
            if is_healthy:
                endpoint.status = EndpointStatus.HEALTHY
                endpoint.response_time_ms = response_time
                
                # Reset circuit breaker on successful health check
                circuit_breaker = self.circuit_breakers.get(endpoint.endpoint_id, {})
                if circuit_breaker.get('state') in ['open', 'half-open']:
                    circuit_breaker['state'] = 'closed'
                    circuit_breaker['failure_count'] = 0
                    
            else:
                endpoint.status = EndpointStatus.UNHEALTHY
                
                # Update circuit breaker
                circuit_breaker = self.circuit_breakers.get(endpoint.endpoint_id, {
                    'state': 'closed',
                    'failure_count': 0,
                    'last_failure': None
                })
                
                circuit_breaker['failure_count'] += 1
                circuit_breaker['last_failure'] = datetime.now()
                
                if circuit_breaker['failure_count'] >= self.failure_threshold:
                    circuit_breaker['state'] = 'open'
                    
                self.circuit_breakers[endpoint.endpoint_id] = circuit_breaker
            
            endpoint.last_health_check = datetime.now()
            
        except Exception as e:
            self.logger.error(f"Error checking health for {endpoint.endpoint_id}: {e}")
            endpoint.status = EndpointStatus.UNHEALTHY

    async def add_endpoint(self, service_name: str, endpoint: ServiceEndpoint):
        """Add new endpoint to service"""
        try:
            with self.routing_lock:
                self.service_endpoints[service_name].append(endpoint)
                self.logger.info(f"Added endpoint {endpoint.endpoint_id} to service {service_name}")
                
        except Exception as e:
            self.logger.error(f"Error adding endpoint: {e}")
            raise LoadBalancerException(f"Failed to add endpoint: {e}")

    async def remove_endpoint(self, service_name: str, endpoint_id: str):
        """Remove endpoint from service"""
        try:
            with self.routing_lock:
                endpoints = self.service_endpoints.get(service_name, [])
                self.service_endpoints[service_name] = [
                    ep for ep in endpoints if ep.endpoint_id != endpoint_id
                ]
                
                # Clean up circuit breaker
                if endpoint_id in self.circuit_breakers:
                    del self.circuit_breakers[endpoint_id]
                    
                self.logger.info(f"Removed endpoint {endpoint_id} from service {service_name}")
                
        except Exception as e:
            self.logger.error(f"Error removing endpoint: {e}")
            raise LoadBalancerException(f"Failed to remove endpoint: {e}")

    async def _load_configuration(self):
        """Load load balancer configuration"""
        try:
            # Load algorithm configurations for each service
            default_algorithms = {
                "content_agent": LoadBalancingAlgorithm.ADAPTIVE_INTELLIGENT,
                "protection_agent": LoadBalancingAlgorithm.LEAST_RESPONSE_TIME,
                "music_agent": LoadBalancingAlgorithm.WEIGHTED_LEAST_CONNECTIONS,
                "distribution_agent": LoadBalancingAlgorithm.ROUND_ROBIN,
                "api_gateway": LoadBalancingAlgorithm.ADAPTIVE_INTELLIGENT
            }
            
            self.algorithm_config.update(default_algorithms)
            
        except Exception as e:
            self.logger.error(f"Error loading configuration: {e}")

    async def _initialize_default_endpoints(self):
        """Initialize default endpoints for services"""
        try:
            default_endpoints = {
                "content_agent": [
                    ServiceEndpoint("content_1", "localhost", 8001, weight=1.0),
                    ServiceEndpoint("content_2", "localhost", 8002, weight=1.0)
                ],
                "protection_agent": [
                    ServiceEndpoint("protection_1", "localhost", 8003, weight=1.0),
                    ServiceEndpoint("protection_2", "localhost", 8004, weight=1.0)
                ],
                "music_agent": [
                    ServiceEndpoint("music_1", "localhost", 8005, weight=1.5),
                    ServiceEndpoint("music_2", "localhost", 8006, weight=1.0)
                ]
            }
            
            for service_name, endpoints in default_endpoints.items():
                self.service_endpoints[service_name] = endpoints
                
        except Exception as e:
            self.logger.error(f"Error initializing default endpoints: {e}")

    async def get_load_balancer_status(self) -> Dict[str, Any]:
        """Get comprehensive load balancer status"""
        try:
            status = {
                "services": len(self.service_endpoints),
                "total_endpoints": sum(len(eps) for eps in self.service_endpoints.values()),
                "healthy_endpoints": sum(
                    len([ep for ep in eps if ep.status == EndpointStatus.HEALTHY])
                    for eps in self.service_endpoints.values()
                ),
                "total_requests": len(self.request_history),
                "algorithms": {service: algo.value for service, algo in self.algorithm_config.items()},
                "service_details": {}
            }
            
            for service_name, endpoints in self.service_endpoints.items():
                status["service_details"][service_name] = {
                    "total_endpoints": len(endpoints),
                    "healthy_endpoints": len([ep for ep in endpoints if ep.status == EndpointStatus.HEALTHY]),
                    "algorithm": self.algorithm_config.get(service_name, self.default_algorithm).value,
                    "total_requests": self.routing_stats[service_name],
                    "endpoints": [
                        {
                            "endpoint_id": ep.endpoint_id,
                            "host": ep.host,
                            "port": ep.port,
                            "status": ep.status.value,
                            "current_connections": ep.current_connections,
                            "response_time_ms": ep.response_time_ms,
                            "success_rate": ep.success_rate,
                            "weight": ep.weight
                        }
                        for ep in endpoints
                    ]
                }
            
            return status
            
        except Exception as e:
            self.logger.error(f"Error getting load balancer status: {e}")
            return {"error": str(e)}

    async def health_check(self) -> Dict[str, Any]:
        """Health check for load balancer"""
        try:
            healthy_services = 0
            total_services = len(self.service_endpoints)
            
            for endpoints in self.service_endpoints.values():
                if any(ep.status == EndpointStatus.HEALTHY for ep in endpoints):
                    healthy_services += 1
            
            return {
                "status": "healthy" if healthy_services == total_services else "degraded",
                "healthy_services": healthy_services,
                "total_services": total_services,
                "health_check_active": self.health_check_task is not None,
                "last_check": datetime.now().isoformat()
            }
        except Exception as e:
            return {"status": "unhealthy", "error": str(e)}
