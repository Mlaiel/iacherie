"""Distribution Gateway - Unified API Gateway for Distribution Services
===================================================================

Centralized gateway providing unified access to all distribution services
with authentication, rate limiting, monitoring, and service orchestration.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: © 2025 Fahed Mlaiel. All rights reserved.
"""
import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple, Callable
from enum import Enum
from dataclasses import dataclass, field
from uuid import UUID, uuid4
import json
import time
from collections import defaultdict, deque
import jwt
import hashlib

from ..security.auth import AuthenticationManager
from ..monitoring.metrics import MetricsCollector
from ..core.events import EventEmitter


class RequestMethod(Enum):
    """HTTP request methods."""    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    DELETE = "DELETE"
    PATCH = "PATCH"
    OPTIONS = "OPTIONS"
    HEAD = "HEAD"


class ServiceStatus(Enum):
    """Service status enumeration."""    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    MAINTENANCE = "maintenance"
    OFFLINE = "offline"


class RateLimitType(Enum):
    """Rate limit type enumeration."""    REQUESTS_PER_MINUTE = "requests_per_minute"
    REQUESTS_PER_HOUR = "requests_per_hour"
    REQUESTS_PER_DAY = "requests_per_day"
    CONCURRENT_REQUESTS = "concurrent_requests"
    BANDWIDTH = "bandwidth"


@dataclass
class APIRequest:
    """API request data structure."""    request_id: UUID = field(default_factory=uuid4)
    
    # Request details
    method: RequestMethod = RequestMethod.GET
    endpoint: str = ""
    path: str = ""
    query_params: Dict[str, Any] = field(default_factory=dict)
    headers: Dict[str, str] = field(default_factory=dict)
    body: Optional[Dict[str, Any]] = None
    
    # Authentication
    user_id: Optional[UUID] = None
    api_key: Optional[str] = None
    jwt_token: Optional[str] = None
    permissions: List[str] = field(default_factory=list)
    
    # Routing
    service_name: str = ""
    service_version: str = "v1"
    target_url: str = ""
    
    # Context
    client_ip: str = ""
    user_agent: str = ""
    correlation_id: UUID = field(default_factory=uuid4)
    
    # Timing
    received_at: datetime = field(default_factory=datetime.utcnow)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    
    # Metadata
    request_size: int = 0
    response_size: int = 0
    cache_hit: bool = False


@dataclass
class APIResponse:
    """API response data structure."""    request_id: UUID
    
    # Response details
    status_code: int = 200
    headers: Dict[str, str] = field(default_factory=dict)
    body: Optional[Dict[str, Any]] = None
    
    # Performance
    processing_time: float = 0.0
    service_time: float = 0.0
    total_time: float = 0.0
    
    # Error information
    error_code: Optional[str] = None
    error_message: Optional[str] = None
    error_details: Optional[Dict[str, Any]] = None
    
    # Metadata
    served_from_cache: bool = False
    service_version: str = "v1"
    
    # Timestamps
    generated_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class RateLimitRule:
    """Rate limit rule configuration."""    rule_id: UUID = field(default_factory=uuid4)
    name: str = ""
    description: str = ""
    
    # Rule configuration
    limit_type: RateLimitType = RateLimitType.REQUESTS_PER_MINUTE
    limit_value: int = 100
    window_size: int = 60  # seconds
    
    # Scope
    applies_to: str = "global"  # global, user, api_key, ip, endpoint
    target_values: List[str] = field(default_factory=list)
    endpoints: List[str] = field(default_factory=list)
    
    # Behavior
    block_on_exceed: bool = True
    response_delay: float = 0.0  # seconds
    custom_response: Optional[Dict[str, Any]] = None
    
    # Metadata
    enabled: bool = True
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class ServiceEndpoint:
    """Service endpoint configuration."""    endpoint_id: UUID = field(default_factory=uuid4)
    service_name: str = ""
    
    # Endpoint details
    path: str = ""
    method: RequestMethod = RequestMethod.GET
    target_url: str = ""
    description: str = ""
    
    # Configuration
    authentication_required: bool = True
    required_permissions: List[str] = field(default_factory=list)
    rate_limit_rules: List[UUID] = field(default_factory=list)
    
    # Behavior
    timeout: float = 30.0  # seconds
    retry_attempts: int = 3
    retry_delay: float = 1.0  # seconds
    circuit_breaker_enabled: bool = True
    
    # Caching
    cache_enabled: bool = False
    cache_ttl: int = 300  # seconds
    cache_key_strategy: str = "default"
    
    # Monitoring
    health_check_path: str = ""
    expected_response_time: float = 1.0  # seconds
    
    # Metadata
    version: str = "v1"
    deprecated: bool = False
    enabled: bool = True
    created_at: datetime = field(default_factory=datetime.utcnow)


class DistributionGateway:
    """    Distribution Gateway Engine
    
    Unified API gateway providing centralized access to all distribution services
    with comprehensive security, monitoring, and optimization features.
    """    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize distribution gateway."""        self.config = config or {}
        self.logger = logging.getLogger(__name__)
        
        # Core components
        self.auth_manager = AuthenticationManager()
        self.metrics_collector = MetricsCollector()
        self.event_emitter = EventEmitter()
        
        # Gateway configuration
        self.service_endpoints: Dict[str, ServiceEndpoint] = {}
        self.rate_limit_rules: Dict[UUID, RateLimitRule] = {}
        self.service_instances: Dict[str, List[Dict[str, Any]]] = {}
        
        # Request management
        self.active_requests: Dict[UUID, APIRequest] = {}
        self.request_history: deque = deque(maxlen=10000)
        self.response_cache: Dict[str, Dict[str, Any]] = {}
        
        # Rate limiting
        self.rate_limit_counters: Dict[str, Dict[str, Any]] = defaultdict(lambda: defaultdict(int))
        self.rate_limit_windows: Dict[str, Dict[str, datetime]] = defaultdict(dict)
        
        # Circuit breakers
        self.circuit_breakers: Dict[str, Dict[str, Any]] = {}
        
        # Load balancing
        self.load_balancer_state: Dict[str, Dict[str, Any]] = {}
        
        # System configuration
        self.is_initialized = False
        self.gateway_port = config.get('port', 8080)
        self.enable_cors = config.get('enable_cors', True)
        self.enable_compression = config.get('enable_compression', True)
        self.enable_ssl = config.get('enable_ssl', False)
        self.ssl_cert_path = config.get('ssl_cert_path', '')
        self.ssl_key_path = config.get('ssl_key_path', '')
        
        # Performance settings
        self.max_concurrent_requests = config.get('max_concurrent_requests', 1000)
        self.request_timeout = config.get('request_timeout', 30.0)
        self.connection_pool_size = config.get('connection_pool_size', 100)
        
        # Metrics
        self.gateway_metrics = {
            'total_requests': 0,
            'successful_requests': 0,
            'failed_requests': 0,
            'rate_limited_requests': 0,
            'cached_responses': 0,
            'average_response_time': 0.0,
            'current_active_requests': 0,
            'circuit_breaker_trips': 0,
            'service_errors': 0
        }
    
    async def initialize(self) -> bool:
        """        Initialize the distribution gateway.
        
        Returns:
            bool: True if initialization successful
        """        try:
            self.logger.info("Initializing Distribution Gateway")
            
            # Initialize core components
            await self.auth_manager.initialize()
            await self.metrics_collector.initialize()
            await self.event_emitter.initialize()
            
            # Load service endpoints
            await self._load_service_endpoints()
            
            # Load rate limit rules
            await self._load_rate_limit_rules()
            
            # Initialize service discovery
            await self._initialize_service_discovery()
            
            # Initialize circuit breakers
            await self._initialize_circuit_breakers()
            
            # Start background tasks
            await self._start_background_tasks()
            
            # Start gateway server
            await self._start_gateway_server()
            
            self.is_initialized = True
            
            self.logger.info(f"Distribution Gateway initialized successfully on port {self.gateway_port}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to initialize Distribution Gateway: {e}")
            return False
    
    async def shutdown(self) -> None:
        """Shutdown the distribution gateway."""        try:
            self.logger.info("Shutting down Distribution Gateway")
            
            # Stop gateway server
            await self._stop_gateway_server()
            
            # Complete active requests
            await self._complete_active_requests()
            
            # Save metrics and state
            await self._save_gateway_state()
            
            # Clear memory
            self.active_requests.clear()
            self.response_cache.clear()
            
            self.is_initialized = False
            
            self.logger.info("Distribution Gateway shutdown complete")
            
        except Exception as e:
            self.logger.error(f"Error during Distribution Gateway shutdown: {e}")
    
    async def handle_request(self, request: APIRequest) -> APIResponse:
        """        Handle incoming API request.
        
        Args:
            request: API request to handle
            
        Returns:
            APIResponse: Response from handling the request
        """        if not self.is_initialized:
            return self._create_error_response(
                request.request_id, 503, "SERVICE_UNAVAILABLE", "Gateway not initialized"
            )
        
        start_time = time.time()
        request.started_at = datetime.utcnow()
        
        self.logger.debug(f"Handling request {request.request_id} to {request.endpoint}")
        
        try:
            # Add to active requests
            self.active_requests[request.request_id] = request
            self.gateway_metrics['current_active_requests'] = len(self.active_requests)
            
            # Check rate limits
            rate_limit_result = await self._check_rate_limits(request)
            if not rate_limit_result['allowed']:
                self.gateway_metrics['rate_limited_requests'] += 1
                return self._create_error_response(
                    request.request_id, 429, "RATE_LIMIT_EXCEEDED", 
                    rate_limit_result['message']
                )
            
            # Authenticate request
            auth_result = await self._authenticate_request(request)
            if not auth_result['authenticated']:
                return self._create_error_response(
                    request.request_id, 401, "AUTHENTICATION_FAILED", 
                    auth_result['message']
                )
            
            # Update request with auth info
            request.user_id = auth_result.get('user_id')
            request.permissions = auth_result.get('permissions', [])
            
            # Find service endpoint
            endpoint = await self._find_service_endpoint(request)
            if not endpoint:
                return self._create_error_response(
                    request.request_id, 404, "ENDPOINT_NOT_FOUND", 
                    f"Endpoint {request.endpoint} not found"
                )
            
            # Check permissions
            permission_result = await self._check_permissions(request, endpoint)
            if not permission_result['authorized']:
                return self._create_error_response(
                    request.request_id, 403, "INSUFFICIENT_PERMISSIONS", 
                    permission_result['message']
                )
            
            # Check cache
            if endpoint.cache_enabled:
                cached_response = await self._check_response_cache(request, endpoint)
                if cached_response:
                    self.gateway_metrics['cached_responses'] += 1
                    cached_response.served_from_cache = True
                    return cached_response
            
            # Check circuit breaker
            circuit_breaker_result = await self._check_circuit_breaker(endpoint)
            if not circuit_breaker_result['allow_request']:
                return self._create_error_response(
                    request.request_id, 503, "SERVICE_UNAVAILABLE", 
                    circuit_breaker_result['message']
                )
            
            # Route request to service
            response = await self._route_request_to_service(request, endpoint)
            
            # Update circuit breaker
            await self._update_circuit_breaker(endpoint, response.status_code < 500)
            
            # Cache response if applicable
            if endpoint.cache_enabled and response.status_code == 200:
                await self._cache_response(request, endpoint, response)
            
            # Calculate timing
            total_time = time.time() - start_time
            response.total_time = total_time
            response.processing_time = total_time - response.service_time
            
            # Update metrics
            self.gateway_metrics['total_requests'] += 1
            if response.status_code < 400:
                self.gateway_metrics['successful_requests'] += 1
            else:
                self.gateway_metrics['failed_requests'] += 1
                if response.status_code >= 500:
                    self.gateway_metrics['service_errors'] += 1
            
            # Update average response time
            self.gateway_metrics['average_response_time'] = (
                (self.gateway_metrics['average_response_time'] * (self.gateway_metrics['total_requests'] - 1) + total_time) /
                self.gateway_metrics['total_requests']
            )
            
            # Log metrics
            await self._log_request_metrics(request, response)
            
            # Emit events
            await self.event_emitter.emit('request_completed', {
                'request_id': str(request.request_id),
                'endpoint': request.endpoint,
                'status_code': response.status_code,
                'response_time': total_time,
                'user_id': str(request.user_id) if request.user_id else None
            })
            
            request.completed_at = datetime.utcnow()
            
            self.logger.debug(f"Request {request.request_id} completed with status {response.status_code}")
            
            return response
            
        except Exception as e:
            self.logger.error(f"Error handling request {request.request_id}: {e}")
            
            self.gateway_metrics['total_requests'] += 1
            self.gateway_metrics['failed_requests'] += 1
            self.gateway_metrics['service_errors'] += 1
            
            return self._create_error_response(
                request.request_id, 500, "INTERNAL_SERVER_ERROR", 
                f"Internal server error: {str(e)}"
            )
            
        finally:
            # Remove from active requests
            self.active_requests.pop(request.request_id, None)
            self.gateway_metrics['current_active_requests'] = len(self.active_requests)
            
            # Add to request history
            self.request_history.append({
                'request_id': str(request.request_id),
                'endpoint': request.endpoint,
                'method': request.method.value,
                'status_code': getattr(response if 'response' in locals() else None, 'status_code', 500),
                'response_time': time.time() - start_time,
                'timestamp': request.received_at.isoformat(),
                'user_id': str(request.user_id) if request.user_id else None
            })
    
    async def register_service_endpoint(self, endpoint: ServiceEndpoint) -> bool:
        """        Register new service endpoint.
        
        Args:
            endpoint: Service endpoint to register
            
        Returns:
            bool: True if registration successful
        """        try:
            # Validate endpoint configuration
            if not endpoint.service_name or not endpoint.path:
                raise ValueError("Service name and path are required")
            
            if not endpoint.target_url:
                raise ValueError("Target URL is required")
            
            # Create endpoint key
            endpoint_key = f"{endpoint.method.value}:{endpoint.path}"
            
            # Register endpoint
            self.service_endpoints[endpoint_key] = endpoint
            
            # Initialize circuit breaker for endpoint
            if endpoint.circuit_breaker_enabled:
                await self._initialize_endpoint_circuit_breaker(endpoint)
            
            # Initialize load balancer state
            await self._initialize_endpoint_load_balancer(endpoint)
            
            self.logger.info(f"Registered service endpoint: {endpoint_key} -> {endpoint.target_url}")
            
            # Emit event
            await self.event_emitter.emit('endpoint_registered', {
                'endpoint_id': str(endpoint.endpoint_id),
                'service_name': endpoint.service_name,
                'path': endpoint.path,
                'method': endpoint.method.value
            })
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to register service endpoint: {e}")
            return False
    
    async def unregister_service_endpoint(self, endpoint_key: str) -> bool:
        """        Unregister service endpoint.
        
        Args:
            endpoint_key: Endpoint key to unregister
            
        Returns:
            bool: True if unregistration successful
        """        try:
            if endpoint_key in self.service_endpoints:
                endpoint = self.service_endpoints[endpoint_key]
                
                # Remove endpoint
                del self.service_endpoints[endpoint_key]
                
                # Cleanup circuit breaker
                circuit_breaker_key = f"{endpoint.service_name}:{endpoint.path}"
                self.circuit_breakers.pop(circuit_breaker_key, None)
                
                # Cleanup load balancer state
                self.load_balancer_state.pop(circuit_breaker_key, None)
                
                self.logger.info(f"Unregistered service endpoint: {endpoint_key}")
                
                # Emit event
                await self.event_emitter.emit('endpoint_unregistered', {
                    'endpoint_id': str(endpoint.endpoint_id),
                    'service_name': endpoint.service_name,
                    'path': endpoint.path
                })
                
                return True
            else:
                self.logger.warning(f"Endpoint {endpoint_key} not found for unregistration")
                return False
                
        except Exception as e:
            self.logger.error(f"Failed to unregister service endpoint: {e}")
            return False
    
    async def add_rate_limit_rule(self, rule: RateLimitRule) -> bool:
        """        Add rate limit rule.
        
        Args:
            rule: Rate limit rule to add
            
        Returns:
            bool: True if rule added successfully
        """        try:
            # Validate rule
            if rule.limit_value <= 0:
                raise ValueError("Limit value must be positive")
            
            if rule.window_size <= 0:
                raise ValueError("Window size must be positive")
            
            # Add rule
            self.rate_limit_rules[rule.rule_id] = rule
            
            self.logger.info(f"Added rate limit rule: {rule.name} ({rule.limit_value} {rule.limit_type.value})")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to add rate limit rule: {e}")
            return False
    
    async def remove_rate_limit_rule(self, rule_id: UUID) -> bool:
        """        Remove rate limit rule.
        
        Args:
            rule_id: Rule ID to remove
            
        Returns:
            bool: True if rule removed successfully
        """        try:
            if rule_id in self.rate_limit_rules:
                rule = self.rate_limit_rules[rule_id]
                del self.rate_limit_rules[rule_id]
                
                self.logger.info(f"Removed rate limit rule: {rule.name}")
                return True
            else:
                self.logger.warning(f"Rate limit rule {rule_id} not found")
                return False
                
        except Exception as e:
            self.logger.error(f"Failed to remove rate limit rule: {e}")
            return False
    
    async def get_service_health(self) -> Dict[str, Any]:
        """        Get overall service health status.
        
        Returns:
            Dict containing service health information
        """        try:
            service_health = {}
            
            for endpoint_key, endpoint in self.service_endpoints.items():
                # Check circuit breaker status
                circuit_breaker_key = f"{endpoint.service_name}:{endpoint.path}"
                circuit_breaker = self.circuit_breakers.get(circuit_breaker_key, {})
                
                # Determine service status
                if circuit_breaker.get('state') == 'open':
                    status = ServiceStatus.UNHEALTHY
                elif circuit_breaker.get('failure_rate', 0) > 0.5:
                    status = ServiceStatus.DEGRADED
                else:
                    status = ServiceStatus.HEALTHY
                
                service_health[endpoint.service_name] = {
                    'status': status.value,
                    'endpoint': endpoint_key,
                    'target_url': endpoint.target_url,
                    'circuit_breaker_state': circuit_breaker.get('state', 'unknown'),
                    'failure_rate': circuit_breaker.get('failure_rate', 0),
                    'last_failure': circuit_breaker.get('last_failure'),
                    'response_time': circuit_breaker.get('avg_response_time', 0)
                }
            
            # Calculate overall health
            healthy_services = len([s for s in service_health.values() if s['status'] == 'healthy'])
            total_services = len(service_health)
            overall_health = 'healthy' if healthy_services == total_services else 'degraded' if healthy_services > 0 else 'unhealthy'
            
            return {
                'overall_status': overall_health,
                'total_services': total_services,
                'healthy_services': healthy_services,
                'service_details': service_health,
                'gateway_metrics': self.gateway_metrics,
                'active_requests': len(self.active_requests),
                'timestamp': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Error getting service health: {e}")
            return {
                'overall_status': 'unknown',
                'error': str(e),
                'timestamp': datetime.utcnow().isoformat()
            }
    
    async def get_gateway_metrics(self) -> Dict[str, Any]:
        """        Get comprehensive gateway metrics.
        
        Returns:
            Dict containing gateway metrics
        """        try:
            # Calculate additional metrics
            current_time = datetime.utcnow()
            
            # Request rate metrics
            recent_requests = [
                req for req in self.request_history
                if datetime.fromisoformat(req['timestamp']) > current_time - timedelta(minutes=5)
            ]
            
            requests_per_minute = len(recent_requests) / 5.0
            
            # Success rate
            successful_recent = len([req for req in recent_requests if req['status_code'] < 400])
            success_rate = successful_recent / max(len(recent_requests), 1)
            
            # Circuit breaker metrics
            circuit_breakers_open = len([cb for cb in self.circuit_breakers.values() if cb.get('state') == 'open'])
            
            return {
                'basic_metrics': self.gateway_metrics,
                'performance_metrics': {
                    'requests_per_minute': requests_per_minute,
                    'success_rate': success_rate,
                    'cache_hit_rate': self.gateway_metrics['cached_responses'] / max(self.gateway_metrics['total_requests'], 1),
                    'circuit_breakers_open': circuit_breakers_open,
                    'average_response_time': self.gateway_metrics['average_response_time']
                },
                'service_metrics': {
                    'total_endpoints': len(self.service_endpoints),
                    'enabled_endpoints': len([ep for ep in self.service_endpoints.values() if ep.enabled]),
                    'rate_limit_rules': len(self.rate_limit_rules),
                    'active_rate_limits': len([rule for rule in self.rate_limit_rules.values() if rule.enabled])
                },
                'system_metrics': {
                    'active_requests': len(self.active_requests),
                    'cached_responses': len(self.response_cache),
                    'rate_limit_counters': len(self.rate_limit_counters),
                    'circuit_breaker_states': len(self.circuit_breakers)
                },
                'timestamp': current_time.isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Error getting gateway metrics: {e}")
            return {
                'error': str(e),
                'timestamp': datetime.utcnow().isoformat()
            }
    
    # Internal implementation methods
    async def _load_service_endpoints(self) -> None:
        """Load service endpoints configuration."""        # Load default distribution service endpoints
        default_endpoints = [
            ServiceEndpoint(
                service_name="distribution_manager",
                path="/api/v1/distribution/distribute",
                method=RequestMethod.POST,
                target_url="http://localhost:8081/distribute",
                description="Main content distribution endpoint",
                authentication_required=True,
                required_permissions=["distribution.create"],
                timeout=60.0,
                retry_attempts=3
            ),
            ServiceEndpoint(
                service_name="distribution_manager",
                path="/api/v1/distribution/status",
                method=RequestMethod.GET,
                target_url="http://localhost:8081/status",
                description="Distribution status endpoint",
                authentication_required=True,
                required_permissions=["distribution.read"],
                cache_enabled=True,
                cache_ttl=60
            ),
            ServiceEndpoint(
                service_name="distribution_scheduler",
                path="/api/v1/scheduler/schedule",
                method=RequestMethod.POST,
                target_url="http://localhost:8082/schedule",
                description="Content scheduling endpoint",
                authentication_required=True,
                required_permissions=["scheduling.create"],
                timeout=30.0
            ),
            ServiceEndpoint(
                service_name="distribution_analytics",
                path="/api/v1/analytics/query",
                method=RequestMethod.POST,
                target_url="http://localhost:8083/query",
                description="Analytics query endpoint",
                authentication_required=True,
                required_permissions=["analytics.read"],
                timeout=45.0
            ),
            ServiceEndpoint(
                service_name="distribution_validator",
                path="/api/v1/validator/validate",
                method=RequestMethod.POST,
                target_url="http://localhost:8084/validate",
                description="Content validation endpoint",
                authentication_required=True,
                required_permissions=["validation.execute"],
                timeout=120.0
            ),
            ServiceEndpoint(
                service_name="distribution_optimizer",
                path="/api/v1/optimizer/optimize",
                method=RequestMethod.POST,
                target_url="http://localhost:8085/optimize",
                description="Distribution optimization endpoint",
                authentication_required=True,
                required_permissions=["optimization.execute"],
                timeout=90.0
            )
        ]
        
        for endpoint in default_endpoints:
            endpoint_key = f"{endpoint.method.value}:{endpoint.path}"
            self.service_endpoints[endpoint_key] = endpoint
        
        self.logger.info(f"Loaded {len(default_endpoints)} default service endpoints")
    
    async def _load_rate_limit_rules(self) -> None:
        """Load rate limit rules configuration."""        default_rules = [
            RateLimitRule(
                name="Global Request Limit",
                description="Global rate limit for all requests",
                limit_type=RateLimitType.REQUESTS_PER_MINUTE,
                limit_value=1000,
                window_size=60,
                applies_to="global"
            ),
            RateLimitRule(
                name="User Request Limit",
                description="Per-user rate limit",
                limit_type=RateLimitType.REQUESTS_PER_MINUTE,
                limit_value=100,
                window_size=60,
                applies_to="user"
            ),
            RateLimitRule(
                name="Distribution API Limit",
                description="Rate limit for distribution endpoints",
                limit_type=RateLimitType.REQUESTS_PER_HOUR,
                limit_value=500,
                window_size=3600,
                applies_to="endpoint",
                endpoints=["/api/v1/distribution/distribute"]
            ),
            RateLimitRule(
                name="Analytics API Limit",
                description="Rate limit for analytics endpoints",
                limit_type=RateLimitType.REQUESTS_PER_HOUR,
                limit_value=1000,
                window_size=3600,
                applies_to="endpoint",
                endpoints=["/api/v1/analytics/query"]
            )
        ]
        
        for rule in default_rules:
            self.rate_limit_rules[rule.rule_id] = rule
        
        self.logger.info(f"Loaded {len(default_rules)} default rate limit rules")
    
    async def _initialize_service_discovery(self) -> None:
        """Initialize service discovery mechanism."""        # Mock service discovery - in production this would integrate with 
        # service discovery systems like Consul, etcd, or Kubernetes
        self.service_instances = {
            'distribution_manager': [
                {'url': 'http://localhost:8081', 'health': 'healthy', 'weight': 1.0}
            ],
            'distribution_scheduler': [
                {'url': 'http://localhost:8082', 'health': 'healthy', 'weight': 1.0}
            ],
            'distribution_analytics': [
                {'url': 'http://localhost:8083', 'health': 'healthy', 'weight': 1.0}
            ],
            'distribution_validator': [
                {'url': 'http://localhost:8084', 'health': 'healthy', 'weight': 1.0}
            ],
            'distribution_optimizer': [
                {'url': 'http://localhost:8085', 'health': 'healthy', 'weight': 1.0}
            ]
        }
    
    async def _initialize_circuit_breakers(self) -> None:
        """Initialize circuit breakers for all services."""        for endpoint in self.service_endpoints.values():
            if endpoint.circuit_breaker_enabled:
                await self._initialize_endpoint_circuit_breaker(endpoint)
    
    async def _initialize_endpoint_circuit_breaker(self, endpoint: ServiceEndpoint) -> None:
        """Initialize circuit breaker for specific endpoint."""        circuit_breaker_key = f"{endpoint.service_name}:{endpoint.path}"
        
        self.circuit_breakers[circuit_breaker_key] = {
            'state': 'closed',  # closed, open, half_open
            'failure_count': 0,
            'success_count': 0,
            'last_failure': None,
            'last_success': None,
            'failure_threshold': 5,
            'recovery_timeout': 60,  # seconds
            'failure_rate': 0.0,
            'avg_response_time': 0.0,
            'total_requests': 0
        }
    
    async def _initialize_endpoint_load_balancer(self, endpoint: ServiceEndpoint) -> None:
        """Initialize load balancer state for endpoint."""        load_balancer_key = f"{endpoint.service_name}:{endpoint.path}"
        
        self.load_balancer_state[load_balancer_key] = {
            'algorithm': 'round_robin',  # round_robin, weighted, least_connections
            'current_index': 0,
            'instance_weights': {},
            'instance_connections': {}
        }
    
    async def _start_background_tasks(self) -> None:
        """Start background maintenance tasks."""        asyncio.create_task(self._cleanup_rate_limit_counters())
        asyncio.create_task(self._monitor_circuit_breakers())
        asyncio.create_task(self._cleanup_response_cache())
        asyncio.create_task(self._health_check_services())
    
    async def _start_gateway_server(self) -> None:
        """Start the gateway HTTP server."""        # In a real implementation, this would start an HTTP server
        # For now, just log that the server would be started
        self.logger.info(f"Gateway server would start on port {self.gateway_port}")
    
    async def _stop_gateway_server(self) -> None:
        """Stop the gateway HTTP server."""        self.logger.info("Gateway server would stop")
    
    async def _complete_active_requests(self) -> None:
        """Complete all active requests before shutdown."""        if self.active_requests:
            self.logger.info(f"Waiting for {len(self.active_requests)} active requests to complete")
            
            # Wait for active requests to complete (with timeout)
            timeout = 30.0  # 30 seconds
            start_time = time.time()
            
            while self.active_requests and (time.time() - start_time) < timeout:
                await asyncio.sleep(0.1)
            
            if self.active_requests:
                self.logger.warning(f"{len(self.active_requests)} requests did not complete before timeout")
    
    async def _save_gateway_state(self) -> None:
        """Save gateway state to persistent storage."""        # In production, this would save state to database or file system
        pass
    
    # Request processing methods
    async def _check_rate_limits(self, request: APIRequest) -> Dict[str, Any]:
        """Check if request is within rate limits."""        current_time = datetime.utcnow()
        
        for rule in self.rate_limit_rules.values():
            if not rule.enabled:
                continue
            
            # Check if rule applies to this request
            if not self._rule_applies_to_request(rule, request):
                continue
            
            # Generate rate limit key
            rate_limit_key = self._generate_rate_limit_key(rule, request)
            
            # Check window
            window_start = self.rate_limit_windows[rule.applies_to].get(rate_limit_key)
            if not window_start or (current_time - window_start).total_seconds() > rule.window_size:
                # Reset window
                self.rate_limit_windows[rule.applies_to][rate_limit_key] = current_time
                self.rate_limit_counters[rule.applies_to][rate_limit_key] = 0
            
            # Increment counter
            self.rate_limit_counters[rule.applies_to][rate_limit_key] += 1
            current_count = self.rate_limit_counters[rule.applies_to][rate_limit_key]
            
            # Check limit
            if current_count > rule.limit_value:
                return {
                    'allowed': False,
                    'message': f'Rate limit exceeded: {current_count}/{rule.limit_value} {rule.limit_type.value}',
                    'rule_name': rule.name,
                    'retry_after': rule.window_size
                }
        
        return {'allowed': True}
    
    async def _authenticate_request(self, request: APIRequest) -> Dict[str, Any]:
        """Authenticate the request."""        try:
            # Check for JWT token
            if request.jwt_token:
                auth_result = await self.auth_manager.validate_jwt_token(request.jwt_token)
                if auth_result['valid']:
                    return {
                        'authenticated': True,
                        'user_id': UUID(auth_result['user_id']),
                        'permissions': auth_result.get('permissions', [])
                    }
            
            # Check for API key
            if request.api_key:
                auth_result = await self.auth_manager.validate_api_key(request.api_key)
                if auth_result['valid']:
                    return {
                        'authenticated': True,
                        'user_id': UUID(auth_result['user_id']),
                        'permissions': auth_result.get('permissions', [])
                    }
            
            # Check authorization header
            auth_header = request.headers.get('Authorization', '')
            if auth_header.startswith('Bearer '):
                token = auth_header[7:]
                auth_result = await self.auth_manager.validate_jwt_token(token)
                if auth_result['valid']:
                    return {
                        'authenticated': True,
                        'user_id': UUID(auth_result['user_id']),
                        'permissions': auth_result.get('permissions', [])
                    }
            
            return {
                'authenticated': False,
                'message': 'No valid authentication credentials provided'
            }
            
        except Exception as e:
            return {
                'authenticated': False,
                'message': f'Authentication error: {str(e)}'
            }
    
    async def _find_service_endpoint(self, request: APIRequest) -> Optional[ServiceEndpoint]:
        """Find matching service endpoint for request."""        endpoint_key = f"{request.method.value}:{request.path}"
        
        # Exact match
        if endpoint_key in self.service_endpoints:
            endpoint = self.service_endpoints[endpoint_key]
            if endpoint.enabled:
                return endpoint
        
        # Pattern matching (for path parameters)
        for key, endpoint in self.service_endpoints.items():
            if endpoint.enabled and self._path_matches_pattern(request.path, endpoint.path):
                return endpoint
        
        return None
    
    async def _check_permissions(self, request: APIRequest, endpoint: ServiceEndpoint) -> Dict[str, Any]:
        """Check if request has required permissions for endpoint."""        if not endpoint.authentication_required:
            return {'authorized': True}
        
        if not endpoint.required_permissions:
            return {'authorized': True}
        
        user_permissions = set(request.permissions)
        required_permissions = set(endpoint.required_permissions)
        
        if required_permissions.issubset(user_permissions):
            return {'authorized': True}
        else:
            missing_permissions = required_permissions - user_permissions
            return {
                'authorized': False,
                'message': f'Missing required permissions: {", ".join(missing_permissions)}'
            }
    
    async def _check_response_cache(self, request: APIRequest, endpoint: ServiceEndpoint) -> Optional[APIResponse]:
        """Check if response is cached."""        if not endpoint.cache_enabled:
            return None
        
        cache_key = self._generate_cache_key(request, endpoint)
        cached_data = self.response_cache.get(cache_key)
        
        if cached_data:
            # Check if cache is still valid
            cached_time = cached_data['cached_at']
            if (datetime.utcnow() - cached_time).total_seconds() < endpoint.cache_ttl:
                # Return cached response
                response = cached_data['response']
                response.served_from_cache = True
                return response
            else:
                # Remove expired cache entry
                del self.response_cache[cache_key]
        
        return None
    
    async def _check_circuit_breaker(self, endpoint: ServiceEndpoint) -> Dict[str, Any]:
        """Check circuit breaker status for endpoint."""        if not endpoint.circuit_breaker_enabled:
            return {'allow_request': True}
        
        circuit_breaker_key = f"{endpoint.service_name}:{endpoint.path}"
        circuit_breaker = self.circuit_breakers.get(circuit_breaker_key, {})
        
        state = circuit_breaker.get('state', 'closed')
        
        if state == 'closed':
            return {'allow_request': True}
        elif state == 'open':
            # Check if recovery timeout has passed
            last_failure = circuit_breaker.get('last_failure')
            if last_failure:
                recovery_timeout = circuit_breaker.get('recovery_timeout', 60)
                time_since_failure = (datetime.utcnow() - last_failure).total_seconds()
                
                if time_since_failure > recovery_timeout:
                    # Move to half-open state
                    circuit_breaker['state'] = 'half_open'
                    return {'allow_request': True}
            
            return {
                'allow_request': False,
                'message': f'Circuit breaker is open for {endpoint.service_name}',
                'state': 'open'
            }
        elif state == 'half_open':
            # Allow limited requests to test service recovery
            return {'allow_request': True}
        
        return {'allow_request': True}
    
    async def _route_request_to_service(self, request: APIRequest, endpoint: ServiceEndpoint) -> APIResponse:
        """Route request to appropriate service instance."""        service_start_time = time.time()
        
        try:
            # Select service instance using load balancing
            service_url = await self._select_service_instance(endpoint)
            
            # Prepare request
            full_url = f"{service_url}{endpoint.path}"
            if request.query_params:
                query_string = "&".join([f"{k}={v}" for k, v in request.query_params.items()])
                full_url += f"?{query_string}"
            
            # Mock service call - in real implementation this would make HTTP request
            # using aiohttp or similar HTTP client
            
            # Simulate service response time
            await asyncio.sleep(0.1)  # 100ms simulated response time
            
            service_time = time.time() - service_start_time
            
            # Create successful response
            response = APIResponse(
                request_id=request.request_id,
                status_code=200,
                headers={'Content-Type': 'application/json'},
                body={'status': 'success', 'message': 'Request processed successfully'},
                service_time=service_time
            )
            
            return response
            
        except Exception as e:
            service_time = time.time() - service_start_time
            
            self.logger.error(f"Error routing request to service: {e}")
            
            return APIResponse(
                request_id=request.request_id,
                status_code=500,
                headers={'Content-Type': 'application/json'},
                body={'error': 'Service error', 'message': str(e)},
                service_time=service_time,
                error_code='SERVICE_ERROR',
                error_message=str(e)
            )
    
    async def _select_service_instance(self, endpoint: ServiceEndpoint) -> str:
        """Select service instance using load balancing algorithm."""        service_instances = self.service_instances.get(endpoint.service_name, [])
        
        if not service_instances:
            raise RuntimeError(f"No healthy instances available for service {endpoint.service_name}")
        
        # Filter healthy instances
        healthy_instances = [inst for inst in service_instances if inst['health'] == 'healthy']
        
        if not healthy_instances:
            raise RuntimeError(f"No healthy instances available for service {endpoint.service_name}")
        
        # Simple round-robin load balancing
        load_balancer_key = f"{endpoint.service_name}:{endpoint.path}"
        lb_state = self.load_balancer_state.get(load_balancer_key, {'current_index': 0})
        
        current_index = lb_state['current_index']
        selected_instance = healthy_instances[current_index % len(healthy_instances)]
        
        # Update index for next request
        lb_state['current_index'] = (current_index + 1) % len(healthy_instances)
        self.load_balancer_state[load_balancer_key] = lb_state
        
        return selected_instance['url']
    
    async def _update_circuit_breaker(self, endpoint: ServiceEndpoint, success: bool) -> None:
        """Update circuit breaker state based on request result."""        if not endpoint.circuit_breaker_enabled:
            return
        
        circuit_breaker_key = f"{endpoint.service_name}:{endpoint.path}"
        circuit_breaker = self.circuit_breakers.get(circuit_breaker_key, {})
        
        current_time = datetime.utcnow()
        
        if success:
            circuit_breaker['success_count'] = circuit_breaker.get('success_count', 0) + 1
            circuit_breaker['last_success'] = current_time
            
            # If in half-open state and success, move to closed
            if circuit_breaker.get('state') == 'half_open':
                circuit_breaker['state'] = 'closed'
                circuit_breaker['failure_count'] = 0
        else:
            circuit_breaker['failure_count'] = circuit_breaker.get('failure_count', 0) + 1
            circuit_breaker['last_failure'] = current_time
            
            # Check if should open circuit breaker
            failure_threshold = circuit_breaker.get('failure_threshold', 5)
            if circuit_breaker['failure_count'] >= failure_threshold:
                circuit_breaker['state'] = 'open'
                self.gateway_metrics['circuit_breaker_trips'] += 1
        
        # Update failure rate
        total_requests = circuit_breaker.get('success_count', 0) + circuit_breaker.get('failure_count', 0)
        if total_requests > 0:
            circuit_breaker['failure_rate'] = circuit_breaker.get('failure_count', 0) / total_requests
        
        circuit_breaker['total_requests'] = total_requests
        self.circuit_breakers[circuit_breaker_key] = circuit_breaker
    
    async def _cache_response(self, request: APIRequest, endpoint: ServiceEndpoint, response: APIResponse) -> None:
        """Cache response for future requests."""        cache_key = self._generate_cache_key(request, endpoint)
        
        self.response_cache[cache_key] = {
            'response': response,
            'cached_at': datetime.utcnow(),
            'ttl': endpoint.cache_ttl
        }
    
    async def _log_request_metrics(self, request: APIRequest, response: APIResponse) -> None:
        """Log request metrics."""        await self.metrics_collector.record_request({
            'request_id': str(request.request_id),
            'endpoint': request.endpoint,
            'method': request.method.value,
            'status_code': response.status_code,
            'response_time': response.total_time,
            'service_time': response.service_time,
            'user_id': str(request.user_id) if request.user_id else None,
            'timestamp': request.received_at.isoformat(),
            'cached': response.served_from_cache
        })
    
    # Utility methods
    def _create_error_response(self, request_id: UUID, status_code: int, error_code: str, message: str) -> APIResponse:
        """Create error response."""        return APIResponse(
            request_id=request_id,
            status_code=status_code,
            headers={'Content-Type': 'application/json'},
            body={'error': error_code, 'message': message},
            error_code=error_code,
            error_message=message
        )
    
    def _rule_applies_to_request(self, rule: RateLimitRule, request: APIRequest) -> bool:
        """Check if rate limit rule applies to request."""        if rule.applies_to == "global":
            return True
        elif rule.applies_to == "user" and request.user_id:
            return True
        elif rule.applies_to == "api_key" and request.api_key:
            return True
        elif rule.applies_to == "ip" and request.client_ip:
            return True
        elif rule.applies_to == "endpoint":
            return request.path in rule.endpoints
        
        return False
    
    def _generate_rate_limit_key(self, rule: RateLimitRule, request: APIRequest) -> str:
        """Generate rate limit key for request."""        if rule.applies_to == "global":
            return "global"
        elif rule.applies_to == "user":
            return f"user:{request.user_id}"
        elif rule.applies_to == "api_key":
            return f"api_key:{request.api_key}"
        elif rule.applies_to == "ip":
            return f"ip:{request.client_ip}"
        elif rule.applies_to == "endpoint":
            return f"endpoint:{request.path}"
        
        return "unknown"
    
    def _generate_cache_key(self, request: APIRequest, endpoint: ServiceEndpoint) -> str:
        """Generate cache key for request."""        key_parts = [
            endpoint.path,
            request.method.value,
            json.dumps(request.query_params, sort_keys=True) if request.query_params else "",
            str(request.user_id) if request.user_id else ""
        ]
        
        cache_key = ":".join(key_parts)
        return hashlib.md5(cache_key.encode()).hexdigest()
    
    def _path_matches_pattern(self, request_path: str, endpoint_path: str) -> bool:
        """Check if request path matches endpoint path pattern."""        # Simple pattern matching - in production this would be more sophisticated
        # For now, just exact match
        return request_path == endpoint_path
    
    # Background task methods
    async def _cleanup_rate_limit_counters(self) -> None:
        """Clean up expired rate limit counters."""        while self.is_initialized:
            try:
                current_time = datetime.utcnow()
                
                # Clean up expired windows
                for applies_to in self.rate_limit_windows:
                    expired_keys = []
                    for key, window_start in self.rate_limit_windows[applies_to].items():
                        if (current_time - window_start).total_seconds() > 3600:  # 1 hour
                            expired_keys.append(key)
                    
                    for key in expired_keys:
                        del self.rate_limit_windows[applies_to][key]
                        if key in self.rate_limit_counters[applies_to]:
                            del self.rate_limit_counters[applies_to][key]
                
                await asyncio.sleep(300)  # Clean every 5 minutes
                
            except Exception as e:
                self.logger.error(f"Error cleaning rate limit counters: {e}")
                await asyncio.sleep(300)
    
    async def _monitor_circuit_breakers(self) -> None:
        """Monitor and update circuit breaker states."""        while self.is_initialized:
            try:
                current_time = datetime.utcnow()
                
                for cb_key, circuit_breaker in self.circuit_breakers.items():
                    # Auto-recovery for open circuit breakers
                    if circuit_breaker.get('state') == 'open':
                        last_failure = circuit_breaker.get('last_failure')
                        if last_failure:
                            recovery_timeout = circuit_breaker.get('recovery_timeout', 60)
                            time_since_failure = (current_time - last_failure).total_seconds()
                            
                            if time_since_failure > recovery_timeout:
                                circuit_breaker['state'] = 'half_open'
                                self.logger.info(f"Circuit breaker {cb_key} moved to half-open state")
                
                await asyncio.sleep(30)  # Check every 30 seconds
                
            except Exception as e:
                self.logger.error(f"Error monitoring circuit breakers: {e}")
                await asyncio.sleep(30)
    
    async def _cleanup_response_cache(self) -> None:
        """Clean up expired response cache entries."""        while self.is_initialized:
            try:
                current_time = datetime.utcnow()
                expired_keys = []
                
                for cache_key, cached_data in self.response_cache.items():
                    cached_time = cached_data['cached_at']
                    ttl = cached_data['ttl']
                    
                    if (current_time - cached_time).total_seconds() > ttl:
                        expired_keys.append(cache_key)
                
                for key in expired_keys:
                    del self.response_cache[key]
                
                await asyncio.sleep(60)  # Clean every minute
                
            except Exception as e:
                self.logger.error(f"Error cleaning response cache: {e}")
                await asyncio.sleep(60)
    
    async def _health_check_services(self) -> None:
        """Perform health checks on registered services."""        while self.is_initialized:
            try:
                for service_name, instances in self.service_instances.items():
                    for instance in instances:
                        # Mock health check - in production this would make actual HTTP requests
                        # For now, just keep instances healthy
                        instance['health'] = 'healthy'
                        instance['last_health_check'] = datetime.utcnow()
                
                await asyncio.sleep(30)  # Health check every 30 seconds
                
            except Exception as e:
                self.logger.error(f"Error during health checks: {e}")
                await asyncio.sleep(30)
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get current system status."""        return {
            'initialized': self.is_initialized,
            'gateway_port': self.gateway_port,
            'enable_cors': self.enable_cors,
            'enable_ssl': self.enable_ssl,
            'service_endpoints': len(self.service_endpoints),
            'rate_limit_rules': len(self.rate_limit_rules),
            'active_requests': len(self.active_requests),
            'cached_responses': len(self.response_cache),
            'circuit_breakers': len(self.circuit_breakers),
            'service_instances': {k: len(v) for k, v in self.service_instances.items()},
            'metrics': self.gateway_metrics,
            'max_concurrent_requests': self.max_concurrent_requests,
            'request_timeout': self.request_timeout
        }
