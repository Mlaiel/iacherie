#!/usr/bin/env python3
"""
Platform Gateway Manager - Platform Core Enterprise Architecture

© 2025 Fahed Mlaiel. All rights reserved.
This software and associated documentation files are proprietary and confidential.
Unauthorized copying, distribution, or modification is strictly prohibited.
Licensed under Enterprise Commercial License.

Author: Fahed Mlaiel (mlaiel@live.de)
Lead Developer & AI Architect - API gateway orchestration and management
Backend Senior Engineer - API security and rate limiting
Microservices Architect - Gateway routing and load balancing
DevOps Engineer - Gateway infrastructure automation
Security Engineer - Authentication and authorization enforcement

⚠️ STRICT WARNING: Any attempt to steal, copy, or use this concept, idea, or code
without written personal authorization from Fahed Mlaiel (mlaiel@live.de) is
strictly prohibited and will be prosecuted to the full extent of the law.
"""

import asyncio
import logging
import json
import hashlib
import time
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, field
from enum import Enum
import aiohttp
import jwt
from pathlib import Path
import yaml

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class GatewayType(Enum):
    """API Gateway implementation types"""
    NGINX_PLUS = "nginx_plus"
    ENVOY_PROXY = "envoy_proxy"
    KONG = "kong"
    AMBASSADOR = "ambassador"
    ISTIO_GATEWAY = "istio_gateway"
    AWS_API_GATEWAY = "aws_api_gateway"

class AuthenticationType(Enum):
    """Authentication methods"""
    JWT = "jwt"
    OAUTH2 = "oauth2"
    API_KEY = "api_key"
    BASIC_AUTH = "basic_auth"
    MUTUAL_TLS = "mutual_tls"
    CUSTOM = "custom"

class RateLimitType(Enum):
    """Rate limiting strategies"""
    REQUESTS_PER_SECOND = "requests_per_second"
    REQUESTS_PER_MINUTE = "requests_per_minute"
    REQUESTS_PER_HOUR = "requests_per_hour"
    CONCURRENT_REQUESTS = "concurrent_requests"
    BANDWIDTH = "bandwidth"

class LoadBalancingStrategy(Enum):
    """Load balancing algorithms"""
    ROUND_ROBIN = "round_robin"
    LEAST_CONNECTIONS = "least_connections"
    WEIGHTED_ROUND_ROBIN = "weighted_round_robin"
    IP_HASH = "ip_hash"
    LEAST_RESPONSE_TIME = "least_response_time"
    GEOGRAPHIC = "geographic"

class RouteStatus(Enum):
    """Route configuration status"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    MAINTENANCE = "maintenance"
    DEPRECATED = "deprecated"

@dataclass
class APIEndpoint:
    """API endpoint configuration"""
    path: str
    method: str
    service_name: str
    service_host: str
    service_port: int
    authentication_required: bool = True
    rate_limit: Optional[int] = None
    timeout_seconds: int = 30
    retry_attempts: int = 3
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class RouteConfiguration:
    """Route configuration for API gateway"""
    name: str
    path_pattern: str
    methods: List[str]
    upstream_service: str
    upstream_host: str
    upstream_port: int
    status: RouteStatus = RouteStatus.ACTIVE
    authentication_type: AuthenticationType = AuthenticationType.JWT
    rate_limit_config: Dict[str, Any] = field(default_factory=dict)
    load_balancing: LoadBalancingStrategy = LoadBalancingStrategy.ROUND_ROBIN
    headers: Dict[str, str] = field(default_factory=dict)
    middleware: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

@dataclass
class RateLimitRule:
    """Rate limiting rule configuration"""
    name: str
    pattern: str
    limit_type: RateLimitType
    limit_value: int
    window_seconds: int
    identifier: str = "ip"  # ip, user_id, api_key
    block_duration_seconds: int = 300
    whitelist: List[str] = field(default_factory=list)
    blacklist: List[str] = field(default_factory=list)

@dataclass
class GatewayMetrics:
    """Gateway performance metrics"""
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    average_response_time: float = 0.0
    requests_per_second: float = 0.0
    error_rate: float = 0.0
    rate_limited_requests: int = 0
    authenticated_requests: int = 0
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

class PlatformGatewayManager:
    """
    Enterprise API gateway manager for request routing,
    load balancing, authentication, and rate limiting
    """
    
    def __init__(self, gateway_type: GatewayType = GatewayType.NGINX_PLUS):
        self.gateway_type = gateway_type
        self.routes: Dict[str, RouteConfiguration] = {}
        self.rate_limit_rules: Dict[str, RateLimitRule] = {}
        self.metrics: GatewayMetrics = GatewayMetrics()
        self.active_connections: Dict[str, int] = {}
        self.request_history: List[Dict[str, Any]] = []
        self.config_path = Path("./config/api_gateway")
        self.config_path.mkdir(parents=True, exist_ok=True)
        
        # Rate limiting tracking
        self.rate_limit_counters: Dict[str, Dict[str, Any]] = {}
        
        # Authentication handlers
        self.auth_handlers: Dict[AuthenticationType, Callable] = {
            AuthenticationType.JWT: self._validate_jwt_token,
            AuthenticationType.API_KEY: self._validate_api_key,
            AuthenticationType.OAUTH2: self._validate_oauth2_token,
            AuthenticationType.BASIC_AUTH: self._validate_basic_auth
        }
        
        logger.info(f"PlatformGatewayManager initialized with {gateway_type.value}")
    
    async def initialize_gateway(self) -> bool:
        """Initialize API gateway infrastructure"""
        try:
            logger.info("Initializing API gateway infrastructure...")
            
            # Load existing configuration
            await self._load_gateway_configuration()
            
            # Initialize gateway backend
            if await self._setup_gateway_backend():
                logger.info("Gateway backend initialized successfully")
                
                # Configure default routes
                await self._setup_default_routes()
                
                # Initialize monitoring
                await self._start_metrics_collection()
                
                # Setup health checks
                await self._setup_health_checks()
                
                return True
            else:
                logger.error("Failed to initialize gateway backend")
                return False
                
        except Exception as e:
            logger.error(f"Failed to initialize API gateway: {e}")
            return False
    
    async def register_route(self, route: RouteConfiguration) -> bool:
        """Register a new API route"""
        try:
            logger.info(f"Registering route: {route.name}")
            
            # Validate route configuration
            if not self._validate_route_config(route):
                logger.error(f"Invalid route configuration: {route.name}")
                return False
            
            # Check for conflicts
            if await self._check_route_conflicts(route):
                logger.error(f"Route conflict detected: {route.name}")
                return False
            
            # Store route configuration
            self.routes[route.name] = route
            
            # Apply route to gateway backend
            if await self._apply_route_config(route):
                logger.info(f"Route {route.name} registered successfully")
                
                # Save configuration
                await self._save_route_config(route)
                
                return True
            else:
                logger.error(f"Failed to apply route configuration: {route.name}")
                return False
                
        except Exception as e:
            logger.error(f"Failed to register route {route.name}: {e}")
            return False
    
    async def configure_rate_limiting(self, rule: RateLimitRule) -> bool:
        """Configure rate limiting rule"""
        try:
            logger.info(f"Configuring rate limiting rule: {rule.name}")
            
            # Validate rate limit rule
            if not self._validate_rate_limit_rule(rule):
                logger.error(f"Invalid rate limiting rule: {rule.name}")
                return False
            
            # Store rule configuration
            self.rate_limit_rules[rule.name] = rule
            
            # Apply rate limiting configuration
            if await self._apply_rate_limiting_config(rule):
                logger.info(f"Rate limiting rule {rule.name} configured successfully")
                return True
            else:
                logger.error(f"Failed to apply rate limiting rule: {rule.name}")
                return False
                
        except Exception as e:
            logger.error(f"Failed to configure rate limiting {rule.name}: {e}")
            return False
    
    async def handle_request(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle incoming API request through gateway"""
        try:
            request_id = request_data.get('id', f"req_{int(time.time() * 1000)}")
            path = request_data.get('path', '/')
            method = request_data.get('method', 'GET')
            headers = request_data.get('headers', {})
            client_ip = request_data.get('client_ip', '127.0.0.1')
            
            logger.debug(f"Handling request {request_id}: {method} {path}")
            
            # Find matching route
            route = await self._find_matching_route(path, method)
            if not route:
                return self._create_error_response(404, "Route not found", request_id)
            
            # Check if route is active
            if route.status != RouteStatus.ACTIVE:
                return self._create_error_response(503, "Route unavailable", request_id)
            
            # Apply rate limiting
            rate_limit_result = await self._check_rate_limits(client_ip, path, headers)
            if not rate_limit_result['allowed']:
                self.metrics.rate_limited_requests += 1
                return self._create_error_response(
                    429, 
                    f"Rate limit exceeded: {rate_limit_result['message']}", 
                    request_id
                )
            
            # Authenticate request
            auth_result = await self._authenticate_request(route, headers)
            if not auth_result['authenticated']:
                return self._create_error_response(
                    401, 
                    f"Authentication failed: {auth_result['message']}", 
                    request_id
                )
            
            self.metrics.authenticated_requests += 1
            
            # Route request to upstream service
            upstream_response = await self._route_to_upstream(route, request_data)
            
            # Update metrics
            self._update_request_metrics(upstream_response['status_code'])
            
            # Log request
            await self._log_request(request_id, route, upstream_response, client_ip)
            
            return upstream_response
            
        except Exception as e:
            logger.error(f"Failed to handle request: {e}")
            self.metrics.failed_requests += 1
            return self._create_error_response(500, "Internal gateway error", request_data.get('id', 'unknown'))
    
    async def manage_load_balancing(self, service_name: str, strategy: LoadBalancingStrategy) -> bool:
        """Configure load balancing for a service"""
        try:
            logger.info(f"Configuring load balancing for {service_name}: {strategy.value}")
            
            # Find routes for the service
            service_routes = [r for r in self.routes.values() if r.upstream_service == service_name]
            
            if not service_routes:
                logger.error(f"No routes found for service: {service_name}")
                return False
            
            # Apply load balancing strategy
            for route in service_routes:
                route.load_balancing = strategy
                
                # Update gateway configuration
                if await self._apply_load_balancing_config(route):
                    logger.info(f"Load balancing updated for route: {route.name}")
                else:
                    logger.error(f"Failed to update load balancing for route: {route.name}")
                    return False
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to manage load balancing for {service_name}: {e}")
            return False
    
    async def get_gateway_metrics(self) -> Dict[str, Any]:
        """Get comprehensive gateway metrics"""
        try:
            # Calculate current metrics
            current_time = datetime.now(timezone.utc)
            time_window = timedelta(minutes=5)
            recent_requests = [
                req for req in self.request_history 
                if current_time - req['timestamp'] <= time_window
            ]
            
            if recent_requests:
                self.metrics.requests_per_second = len(recent_requests) / 300  # 5 minutes in seconds
                
                response_times = [req['response_time'] for req in recent_requests if 'response_time' in req]
                if response_times:
                    self.metrics.average_response_time = sum(response_times) / len(response_times)
            
            return {
                'gateway_type': self.gateway_type.value,
                'total_routes': len(self.routes),
                'active_routes': len([r for r in self.routes.values() if r.status == RouteStatus.ACTIVE]),
                'rate_limit_rules': len(self.rate_limit_rules),
                'metrics': {
                    'total_requests': self.metrics.total_requests,
                    'successful_requests': self.metrics.successful_requests,
                    'failed_requests': self.metrics.failed_requests,
                    'error_rate': self.metrics.error_rate,
                    'average_response_time': self.metrics.average_response_time,
                    'requests_per_second': self.metrics.requests_per_second,
                    'rate_limited_requests': self.metrics.rate_limited_requests,
                    'authenticated_requests': self.metrics.authenticated_requests
                },
                'active_connections': sum(self.active_connections.values()),
                'timestamp': current_time.isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to get gateway metrics: {e}")
            return {}
    
    async def optimize_gateway_performance(self) -> bool:
        """Optimize gateway performance based on metrics"""
        try:
            logger.info("Optimizing gateway performance...")
            
            # Get current metrics
            metrics_data = await self.get_gateway_metrics()
            
            optimization_actions = []
            
            # Analyze performance issues
            if metrics_data.get('metrics', {}).get('error_rate', 0) > 5.0:
                optimization_actions.append('increase_upstream_health_checks')
            
            if metrics_data.get('metrics', {}).get('average_response_time', 0) > 1000:
                optimization_actions.append('optimize_connection_pooling')
            
            if metrics_data.get('metrics', {}).get('requests_per_second', 0) > 1000:
                optimization_actions.append('enable_response_caching')
            
            # Apply optimizations
            success_count = 0
            for action in optimization_actions:
                if await self._apply_performance_optimization(action):
                    success_count += 1
                    logger.info(f"Applied optimization: {action}")
                else:
                    logger.error(f"Failed to apply optimization: {action}")
            
            logger.info(f"Applied {success_count}/{len(optimization_actions)} optimizations")
            return success_count == len(optimization_actions)
            
        except Exception as e:
            logger.error(f"Failed to optimize gateway performance: {e}")
            return False
    
    # ========================================================================
    # PRIVATE HELPER METHODS
    # ========================================================================
    
    async def _find_matching_route(self, path: str, method: str) -> Optional[RouteConfiguration]:
        """Find matching route for request path and method"""
        for route in self.routes.values():
            if method in route.methods and self._path_matches_pattern(path, route.path_pattern):
                return route
        return None
    
    def _path_matches_pattern(self, path: str, pattern: str) -> bool:
        """Check if path matches route pattern"""
        # Simple pattern matching - in production would use regex
        if pattern == path:
            return True
        
        # Handle wildcard patterns
        if pattern.endswith('/*'):
            prefix = pattern[:-2]
            return path.startswith(prefix)
        
        return False
    
    async def _check_rate_limits(self, client_ip: str, path: str, headers: Dict[str, str]) -> Dict[str, Any]:
        """Check if request is within rate limits"""
        current_time = time.time()
        
        for rule in self.rate_limit_rules.values():
            # Check if rule applies to this request
            if not self._rule_applies_to_request(rule, path, client_ip, headers):
                continue
            
            # Get identifier for rate limiting
            identifier = self._get_rate_limit_identifier(rule, client_ip, headers)
            
            # Check whitelist
            if identifier in rule.whitelist:
                continue
            
            # Check blacklist
            if identifier in rule.blacklist:
                return {'allowed': False, 'message': 'Blocked by blacklist'}
            
            # Initialize counter if not exists
            if identifier not in self.rate_limit_counters:
                self.rate_limit_counters[identifier] = {
                    'count': 0,
                    'window_start': current_time,
                    'blocked_until': 0
                }
            
            counter = self.rate_limit_counters[identifier]
            
            # Check if still blocked
            if current_time < counter['blocked_until']:
                return {'allowed': False, 'message': 'Temporarily blocked'}
            
            # Reset window if expired
            if current_time - counter['window_start'] > rule.window_seconds:
                counter['count'] = 0
                counter['window_start'] = current_time
            
            # Check limit
            if counter['count'] >= rule.limit_value:
                counter['blocked_until'] = current_time + rule.block_duration_seconds
                return {'allowed': False, 'message': f'Rate limit exceeded: {rule.limit_value}/{rule.window_seconds}s'}
            
            # Increment counter
            counter['count'] += 1
        
        return {'allowed': True, 'message': 'Within rate limits'}
    
    def _rule_applies_to_request(self, rule: RateLimitRule, path: str, client_ip: str, headers: Dict[str, str]) -> bool:
        """Check if rate limit rule applies to request"""
        return self._path_matches_pattern(path, rule.pattern)
    
    def _get_rate_limit_identifier(self, rule: RateLimitRule, client_ip: str, headers: Dict[str, str]) -> str:
        """Get identifier for rate limiting"""
        if rule.identifier == "ip":
            return client_ip
        elif rule.identifier == "api_key":
            return headers.get('X-API-Key', client_ip)
        elif rule.identifier == "user_id":
            return headers.get('X-User-ID', client_ip)
        else:
            return client_ip
    
    async def _authenticate_request(self, route: RouteConfiguration, headers: Dict[str, str]) -> Dict[str, Any]:
        """Authenticate request based on route configuration"""
        if not route.authentication_required:
            return {'authenticated': True, 'message': 'No authentication required'}
        
        auth_handler = self.auth_handlers.get(route.authentication_type)
        if not auth_handler:
            return {'authenticated': False, 'message': 'Unsupported authentication type'}
        
        return await auth_handler(headers)
    
    async def _validate_jwt_token(self, headers: Dict[str, str]) -> Dict[str, Any]:
        """Validate JWT token"""
        try:
            auth_header = headers.get('Authorization', '')
            if not auth_header.startswith('Bearer '):
                return {'authenticated': False, 'message': 'Missing or invalid Authorization header'}
            
            token = auth_header[7:]  # Remove 'Bearer ' prefix
            
            # In production, use proper JWT validation with secret key
            # For simulation, just check if token exists and is not expired
            if len(token) > 20:  # Simple validation
                return {'authenticated': True, 'message': 'Valid JWT token'}
            else:
                return {'authenticated': False, 'message': 'Invalid JWT token'}
                
        except Exception as e:
            return {'authenticated': False, 'message': f'JWT validation error: {e}'}
    
    async def _validate_api_key(self, headers: Dict[str, str]) -> Dict[str, Any]:
        """Validate API key"""
        api_key = headers.get('X-API-Key', '')
        if not api_key:
            return {'authenticated': False, 'message': 'Missing API key'}
        
        # In production, validate against database
        # For simulation, just check if key is present
        if len(api_key) >= 32:
            return {'authenticated': True, 'message': 'Valid API key'}
        else:
            return {'authenticated': False, 'message': 'Invalid API key'}
    
    async def _route_to_upstream(self, route: RouteConfiguration, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """Route request to upstream service"""
        try:
            start_time = time.time()
            
            # Simulate upstream request
            await asyncio.sleep(0.1)  # Simulate network latency
            
            response_time = (time.time() - start_time) * 1000  # Convert to milliseconds
            
            # Simulate successful response
            response = {
                'status_code': 200,
                'body': {'message': 'Success', 'service': route.upstream_service},
                'headers': {'Content-Type': 'application/json'},
                'response_time': response_time
            }
            
            return response
            
        except Exception as e:
            logger.error(f"Failed to route to upstream: {e}")
            return {
                'status_code': 502,
                'body': {'error': 'Bad Gateway'},
                'headers': {'Content-Type': 'application/json'},
                'response_time': 0
            }
    
    def _create_error_response(self, status_code: int, message: str, request_id: str) -> Dict[str, Any]:
        """Create error response"""
        return {
            'status_code': status_code,
            'body': {
                'error': message,
                'request_id': request_id,
                'timestamp': datetime.now(timezone.utc).isoformat()
            },
            'headers': {'Content-Type': 'application/json'}
        }
    
    def _update_request_metrics(self, status_code: int):
        """Update request metrics"""
        self.metrics.total_requests += 1
        
        if 200 <= status_code < 400:
            self.metrics.successful_requests += 1
        else:
            self.metrics.failed_requests += 1
        
        if self.metrics.total_requests > 0:
            self.metrics.error_rate = (self.metrics.failed_requests / self.metrics.total_requests) * 100
    
    def get_route_health(self, route_name: str) -> Dict[str, Any]:
        """Get health information for a specific route"""
        if route_name not in self.routes:
            return {'error': 'Route not found'}
        
        route = self.routes[route_name]
        
        return {
            'route_name': route_name,
            'status': route.status.value,
            'path_pattern': route.path_pattern,
            'methods': route.methods,
            'upstream_service': route.upstream_service,
            'upstream_endpoint': f"{route.upstream_host}:{route.upstream_port}",
            'authentication_type': route.authentication_type.value,
            'load_balancing': route.load_balancing.value,
            'created_at': route.created_at.isoformat(),
            'last_check': datetime.now(timezone.utc).isoformat()
        }

# ============================================================================
# EXAMPLE USAGE AND TESTING
# ============================================================================

async def example_gateway_management():
    """Example usage of PlatformGatewayManager"""
    try:
        # Initialize gateway manager
        gateway = PlatformGatewayManager(GatewayType.NGINX_PLUS)
        
        # Initialize gateway
        await gateway.initialize_gateway()
        
        # Register API routes
        content_route = RouteConfiguration(
            name="content-api",
            path_pattern="/api/v1/content/*",
            methods=["GET", "POST", "PUT", "DELETE"],
            upstream_service="content-service",
            upstream_host="content-service.ainflue.svc.cluster.local",
            upstream_port=8080,
            authentication_type=AuthenticationType.JWT,
            load_balancing=LoadBalancingStrategy.ROUND_ROBIN
        )
        
        user_route = RouteConfiguration(
            name="user-api",
            path_pattern="/api/v1/users/*",
            methods=["GET", "POST", "PUT"],
            upstream_service="user-service",
            upstream_host="user-service.ainflue.svc.cluster.local",
            upstream_port=8081,
            authentication_type=AuthenticationType.API_KEY,
            load_balancing=LoadBalancingStrategy.LEAST_CONNECTIONS
        )
        
        await gateway.register_route(content_route)
        await gateway.register_route(user_route)
        
        # Configure rate limiting
        api_rate_limit = RateLimitRule(
            name="api-rate-limit",
            pattern="/api/*",
            limit_type=RateLimitType.REQUESTS_PER_MINUTE,
            limit_value=1000,
            window_seconds=60,
            identifier="api_key"
        )
        
        await gateway.configure_rate_limiting(api_rate_limit)
        
        # Simulate handling requests
        test_request = {
            'id': 'test-001',
            'path': '/api/v1/content/upload',
            'method': 'POST',
            'headers': {
                'Authorization': 'Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...',
                'Content-Type': 'application/json'
            },
            'client_ip': '192.168.1.100',
            'body': {'title': 'Test Content'}
        }
        
        response = await gateway.handle_request(test_request)
        logger.info(f"Request response: {json.dumps(response, indent=2)}")
        
        # Get gateway metrics
        metrics = await gateway.get_gateway_metrics()
        logger.info(f"Gateway metrics: {json.dumps(metrics, indent=2)}")
        
        return True
        
    except Exception as e:
        logger.error(f"Example gateway management failed: {e}")
        return False

if __name__ == "__main__":
    asyncio.run(example_gateway_management())