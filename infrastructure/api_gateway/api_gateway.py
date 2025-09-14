"""
API Gateway - Central API Management Orchestrator
© 2025 Fahed Mlaiel. All rights reserved.

Main API Gateway orchestrating REST, GraphQL, WebSocket APIs with comprehensive
middleware, authentication, rate limiting, and monitoring for creator platform.
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Union
from datetime import datetime, timedelta
from enum import Enum
import json
import uuid

from .rest_api import RESTAPIManager, APIEndpoint, HTTPMethod
from .rate_limiter import RateLimiter

logger = logging.getLogger(__name__)


class APIGatewayMode(Enum):
    """API Gateway operation modes"""
    PRODUCTION = "production"
    DEVELOPMENT = "development"
    TESTING = "testing"
    MAINTENANCE = "maintenance"


class LoadBalancingStrategy(Enum):
    """Load balancing strategies"""
    ROUND_ROBIN = "round_robin"
    LEAST_CONNECTIONS = "least_connections"
    WEIGHTED_ROUND_ROBIN = "weighted_round_robin"
    HEALTH_BASED = "health_based"


class APIGateway:
    """
    Enterprise API Gateway for Creator Platform
    
    Central orchestrator providing:
    - Multi-protocol API support (REST, GraphQL, WebSocket)
    - Comprehensive middleware stack
    - Authentication and authorization
    - Rate limiting and throttling
    - Load balancing and failover
    - Request/response transformation
    - API versioning and compatibility
    - Monitoring and analytics
    - Creator workflow optimization
    """
    
    def __init__(self) -> None:
        # Core API managers
        self.rest_api_manager = RESTAPIManager()
        self.rate_limiter = RateLimiter()
        
        # Gateway configuration
        self.gateway_config = {
            'mode': APIGatewayMode.PRODUCTION,
            'enable_cors': True,
            'enable_compression': True,
            'enable_caching': True,
            'enable_logging': True,
            'enable_metrics': True,
            'max_request_size': 100 * 1024 * 1024,  # 100MB for creator content
            'request_timeout': 60,  # seconds
            'keepalive_timeout': 300,  # seconds
            'max_concurrent_connections': 10000,
            'load_balancing_strategy': LoadBalancingStrategy.HEALTH_BASED
        }
        
        # Middleware stack
        self.middleware_stack = []
        self.request_interceptors = []
        self.response_interceptors = []
        
        # Gateway metrics
        self.gateway_metrics = {
            'total_requests': 0,
            'successful_requests': 0,
            'failed_requests': 0,
            'average_response_time': 0.0,
            'concurrent_connections': 0,
            'cache_hit_rate': 0.0,
            'rate_limit_violations': 0,
            'authentication_failures': 0
        }
        
        # Service registry for load balancing
        self.service_registry = {}
        self.health_checks = {}
        
        # Initialize Ainflue-specific configurations
        self._initialize_ainflue_gateway()
        
        logger.info("API Gateway initialized for creator platform")
    
    def _initialize_ainflue_gateway(self) -> None:
        """Initialize Ainflue creator platform specific gateway configuration"""
        
        # Creator-specific middleware
        self.creator_middleware_config = {
            'content_validation': {
                'max_file_size': 500 * 1024 * 1024,  # 500MB for creator content
                'allowed_content_types': [
                    'audio/mpeg', 'audio/wav', 'audio/mp3',
                    'video/mp4', 'video/avi', 'video/mov',
                    'image/jpeg', 'image/png', 'image/gif',
                    'application/pdf', 'text/plain'
                ],
                'virus_scanning': True,
                'content_fingerprinting': True
            },
            'creator_authentication': {
                'multi_factor_required': True,
                'session_timeout': 3600,  # 1 hour
                'concurrent_sessions': 5,
                'geolocation_validation': True
            },
            'platform_integration_auth': {
                'oauth2_timeout': 900,  # 15 minutes
                'token_refresh_threshold': 300,  # 5 minutes
                'platform_specific_validation': True
            }
        }
        
        # Rate limiting for creator workflows
        self.creator_rate_limits = {
            'content_upload': {
                'requests_per_minute': 10,
                'burst_limit': 5,
                'concurrent_uploads': 3
            },
            'ai_processing': {
                'requests_per_minute': 20,
                'burst_limit': 10,
                'processing_queue_limit': 50
            },
            'platform_distribution': {
                'requests_per_minute': 30,
                'burst_limit': 15,
                'platforms_per_request': 10
            },
            'analytics_queries': {
                'requests_per_minute': 100,
                'burst_limit': 50,
                'data_export_limit': 5
            }
        }
        
        # Service endpoints for load balancing
        self.service_registry = {
            'content_processing_service': [
                {'url': 'https://content-proc-1.ainflue.com', 'weight': 1, 'health': 'healthy'},
                {'url': 'https://content-proc-2.ainflue.com', 'weight': 1, 'health': 'healthy'},
                {'url': 'https://content-proc-3.ainflue.com', 'weight': 2, 'health': 'healthy'}
            ],
            'ai_processing_service': [
                {'url': 'https://ai-proc-1.ainflue.com', 'weight': 2, 'health': 'healthy'},
                {'url': 'https://ai-proc-2.ainflue.com', 'weight': 2, 'health': 'healthy'},
                {'url': 'https://ai-proc-3.ainflue.com', 'weight': 1, 'health': 'healthy'}
            ],
            'platform_integration_service': [
                {'url': 'https://platform-1.ainflue.com', 'weight': 1, 'health': 'healthy'},
                {'url': 'https://platform-2.ainflue.com', 'weight': 1, 'health': 'healthy'}
            ],
            'analytics_service': [
                {'url': 'https://analytics-1.ainflue.com', 'weight': 1, 'health': 'healthy'},
                {'url': 'https://analytics-2.ainflue.com', 'weight': 1, 'health': 'healthy'}
            ]
        }
    
    async def process_request(
        self, 
        method: str,
        path: str,
        headers: Dict[str, str],
        query_params: Dict[str, Any] = None,
        body: Any = None,
        user_context: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Process incoming API request through the gateway"""
        
        request_id = str(uuid.uuid4())
        start_time = datetime.utcnow()
        
        # Create request context
        request_context = {
            'request_id': request_id,
            'method': method.upper(),
            'path': path,
            'headers': headers,
            'query_params': query_params or {},
            'body': body,
            'user_context': user_context or {},
            'start_time': start_time,
            'gateway_metadata': {
                'api_version': self._extract_api_version(path),
                'client_ip': headers.get('X-Forwarded-For', '0.0.0.0'),
                'user_agent': headers.get('User-Agent', ''),
                'content_type': headers.get('Content-Type', '')
            }
        }
        
        try:
            # Update metrics
            self.gateway_metrics['total_requests'] += 1
            
            # Apply request middleware
            processed_request = await self._apply_request_middleware(request_context)
            if processed_request.get('error'):
                return processed_request
            
            # Route to appropriate API handler
            api_response = await self._route_request(processed_request)
            
            # Apply response middleware
            final_response = await self._apply_response_middleware(api_response, request_context)
            
            # Update success metrics
            self.gateway_metrics['successful_requests'] += 1
            
            # Calculate and update response time
            response_time = (datetime.utcnow() - start_time).total_seconds() * 1000
            self._update_average_response_time(response_time)
            
            return final_response
            
        except Exception as e:
            logger.error(f"Gateway error processing request {request_id}: {e}")
            self.gateway_metrics['failed_requests'] += 1
            
            return {
                'status_code': 500,
                'error': True,
                'message': 'Internal gateway error',
                'request_id': request_id,
                'timestamp': datetime.utcnow().isoformat()
            }
    
    async def _apply_request_middleware(self, request_context: Dict[str, Any]) -> Dict[str, Any]:
        """Apply request middleware stack"""
        
        # CORS handling
        if self.gateway_config['enable_cors']:
            cors_result = await self._handle_cors(request_context)
            if cors_result.get('error'):
                return cors_result
        
        # Request size validation
        size_result = await self._validate_request_size(request_context)
        if size_result.get('error'):
            return size_result
        
        # Rate limiting
        rate_limit_result = await self._apply_rate_limiting(request_context)
        if rate_limit_result.get('error'):
            self.gateway_metrics['rate_limit_violations'] += 1
            return rate_limit_result
        
        # Authentication
        auth_result = await self._handle_authentication(request_context)
        if auth_result.get('error'):
            self.gateway_metrics['authentication_failures'] += 1
            return auth_result
        
        # Content validation for creator uploads
        if self._is_content_upload_request(request_context):
            content_result = await self._validate_content_upload(request_context)
            if content_result.get('error'):
                return content_result
        
        # Apply custom middleware
        for middleware in self.middleware_stack:
            middleware_result = await middleware(request_context)
            if middleware_result.get('error'):
                return middleware_result
        
        return {'success': True, 'request_context': request_context}
    
    async def _handle_cors(self, request_context: Dict[str, Any]) -> Dict[str, Any]:
        """Handle CORS headers and preflight requests"""
        
        method = request_context['method']
        headers = request_context['headers']
        
        # Handle preflight requests
        if method == 'OPTIONS':
            return {
                'status_code': 200,
                'headers': {
                    'Access-Control-Allow-Origin': headers.get('Origin', '*'),
                    'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, PATCH, OPTIONS',
                    'Access-Control-Allow-Headers': 'Content-Type, Authorization, X-Requested-With',
                    'Access-Control-Allow-Credentials': 'true',
                    'Access-Control-Max-Age': '86400'
                },
                'body': {}
            }
        
        return {'success': True}
    
    async def _validate_request_size(self, request_context: Dict[str, Any]) -> Dict[str, Any]:
        """Validate request size limits"""
        
        body = request_context.get('body')
        if body:
            content_length = len(json.dumps(body) if isinstance(body, dict) else str(body))
            
            max_size = self.gateway_config['max_request_size']
            if self._is_content_upload_request(request_context):
                max_size = self.creator_middleware_config['content_validation']['max_file_size']
            
            if content_length > max_size:
                return {
                    'status_code': 413,
                    'error': True,
                    'message': f'Request too large. Maximum size: {max_size} bytes'
                }
        
        return {'success': True}
    
    async def _apply_rate_limiting(self, request_context: Dict[str, Any]) -> Dict[str, Any]:
        """Apply rate limiting based on request type and user"""
        
        path = request_context['path']
        user_context = request_context['user_context']
        client_ip = request_context['gateway_metadata']['client_ip']
        
        # Determine rate limit key and limits
        rate_limit_key = self._get_rate_limit_key(path, user_context, client_ip)
        rate_limits = self._get_rate_limits_for_request(path, user_context)
        
        # Check rate limits
        rate_limit_result = await self.rate_limiter.check_rate_limit(
            key=rate_limit_key,
            limit=rate_limits['requests_per_minute'],
            window_seconds=60,
            burst_limit=rate_limits.get('burst_limit', rate_limits['requests_per_minute'])
        )
        
        if not rate_limit_result['allowed']:
            return {
                'status_code': 429,
                'error': True,
                'message': 'Rate limit exceeded',
                'retry_after': rate_limit_result.get('retry_after', 60),
                'headers': {
                    'X-RateLimit-Limit': str(rate_limits['requests_per_minute']),
                    'X-RateLimit-Remaining': str(rate_limit_result.get('remaining', 0)),
                    'X-RateLimit-Reset': str(rate_limit_result.get('reset_time', 0)),
                    'Retry-After': str(rate_limit_result.get('retry_after', 60))
                }
            }
        
        return {'success': True}
    
    async def _handle_authentication(self, request_context: Dict[str, Any]) -> Dict[str, Any]:
        """Handle request authentication"""
        
        path = request_context['path']
        headers = request_context['headers']
        
        # Skip authentication for public endpoints
        if self._is_public_endpoint(path):
            return {'success': True}
        
        # Extract and validate authentication
        auth_header = headers.get('Authorization', '')
        
        if not auth_header:
            return {
                'status_code': 401,
                'error': True,
                'message': 'Authentication required',
                'headers': {
                    'WWW-Authenticate': 'Bearer realm="Ainflue API"'
                }
            }
        
        # Validate authentication token
        auth_result = await self._validate_authentication_token(auth_header)
        if not auth_result['valid']:
            return {
                'status_code': 401,
                'error': True,
                'message': 'Invalid authentication token'
            }
        
        # Update request context with user information
        request_context['user_context'].update(auth_result['user_info'])
        
        return {'success': True}
    
    async def _validate_content_upload(self, request_context: Dict[str, Any]) -> Dict[str, Any]:
        """Validate creator content upload requests"""
        
        content_type = request_context['headers'].get('Content-Type', '')
        allowed_types = self.creator_middleware_config['content_validation']['allowed_content_types']
        
        # Validate content type
        if content_type and not any(allowed in content_type for allowed in allowed_types):
            return {
                'status_code': 415,
                'error': True,
                'message': f'Unsupported content type: {content_type}'
            }
        
        # Additional content validation would go here
        # - Virus scanning
        # - Content fingerprinting
        # - Metadata extraction
        
        return {'success': True}
    
    async def _route_request(self, processed_request: Dict[str, Any]) -> Dict[str, Any]:
        """Route request to appropriate API handler"""
        
        request_context = processed_request['request_context']
        path = request_context['path']
        method = request_context['method']
        
        # Determine API type and route accordingly
        if path.startswith('/api/'):
            # REST API
            response = await self.rest_api_manager.process_api_request(
                path=path,
                method=method,
                headers=request_context['headers'],
                query_params=request_context['query_params'],
                body=request_context['body'],
                user_context=request_context['user_context']
            )
            
            return {
                'status_code': response.status_code,
                'headers': response.headers,
                'body': response.body,
                'response_time_ms': response.response_time_ms
            }
        
        elif path.startswith('/graphql'):
            # GraphQL API (placeholder)
            return {
                'status_code': 200,
                'headers': {'Content-Type': 'application/json'},
                'body': {'data': {'message': 'GraphQL endpoint - implementation pending'}}
            }
        
        elif path.startswith('/ws/'):
            # WebSocket API (placeholder)
            return {
                'status_code': 101,
                'headers': {'Upgrade': 'websocket'},
                'body': {'message': 'WebSocket upgrade'}
            }
        
        else:
            return {
                'status_code': 404,
                'headers': {'Content-Type': 'application/json'},
                'body': {'error': True, 'message': 'Endpoint not found'}
            }
    
    async def _apply_response_middleware(
        self, 
        api_response: Dict[str, Any], 
        request_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Apply response middleware stack"""
        
        response = api_response.copy()
        
        # Add CORS headers if enabled
        if self.gateway_config['enable_cors']:
            if 'headers' not in response:
                response['headers'] = {}
            
            response['headers'].update({
                'Access-Control-Allow-Origin': request_context['headers'].get('Origin', '*'),
                'Access-Control-Allow-Credentials': 'true'
            })
        
        # Add security headers
        response['headers'].update({
            'X-Content-Type-Options': 'nosniff',
            'X-Frame-Options': 'DENY',
            'X-XSS-Protection': '1; mode=block',
            'Strict-Transport-Security': 'max-age=31536000; includeSubDomains'
        })
        
        # Add gateway identification
        response['headers']['X-Powered-By'] = 'Ainflue-API-Gateway'
        response['headers']['X-Request-ID'] = request_context['request_id']
        
        # Apply compression if enabled
        if self.gateway_config['enable_compression']:
            response['headers']['Content-Encoding'] = 'gzip'
        
        # Apply custom response middleware
        for interceptor in self.response_interceptors:
            response = await interceptor(response, request_context)
        
        return response
    
    def _is_content_upload_request(self, request_context: Dict[str, Any]) -> bool:
        """Check if request is a content upload"""
        path = request_context['path']
        method = request_context['method']
        
        return (
            method == 'POST' and 
            ('/content/upload' in path or '/creators/content' in path)
        )
    
    def _is_public_endpoint(self, path: str) -> bool:
        """Check if endpoint is public (no authentication required)"""
        public_endpoints = [
            '/api/v1/health',
            '/api/v1/status',
            '/api/v1/platforms/oauth/callback'
        ]
        
        return any(public_path in path for public_path in public_endpoints)
    
    def _extract_api_version(self, path: str) -> str:
        """Extract API version from path"""
        if '/v1/' in path:
            return 'v1'
        elif '/v2/' in path:
            return 'v2'
        else:
            return 'v1'  # default
    
    def _get_rate_limit_key(
        self, 
        path: str, 
        user_context: Dict[str, Any], 
        client_ip: str
    ) -> str:
        """Generate rate limit key for request"""
        
        user_id = user_context.get('user_id', 'anonymous')
        creator_id = user_context.get('creator_id', '')
        
        if creator_id:
            return f"creator:{creator_id}:{path}"
        elif user_id != 'anonymous':
            return f"user:{user_id}:{path}"
        else:
            return f"ip:{client_ip}:{path}"
    
    def _get_rate_limits_for_request(
        self, 
        path: str, 
        user_context: Dict[str, Any]
    ) -> Dict[str, int]:
        """Get rate limits for specific request"""
        
        # Creator-specific rate limits
        if '/creators/content/upload' in path:
            return self.creator_rate_limits['content_upload']
        elif '/ai/' in path:
            return self.creator_rate_limits['ai_processing']
        elif '/distribute' in path:
            return self.creator_rate_limits['platform_distribution']
        elif '/analytics' in path:
            return self.creator_rate_limits['analytics_queries']
        
        # Default rate limits based on user tier
        user_tier = user_context.get('tier', 'free')
        default_limits = {
            'free': {'requests_per_minute': 60, 'burst_limit': 30},
            'creator': {'requests_per_minute': 1000, 'burst_limit': 500},
            'premium': {'requests_per_minute': 5000, 'burst_limit': 2500},
            'enterprise': {'requests_per_minute': 10000, 'burst_limit': 5000}
        }
        
        return default_limits.get(user_tier, default_limits['free'])
    
    async def _validate_authentication_token(self, auth_header: str) -> Dict[str, Any]:
        """Validate authentication token"""
        
        # Placeholder authentication validation
        # In real implementation, would validate JWT, API keys, etc.
        
        if auth_header.startswith('Bearer '):
            token = auth_header[7:]  # Remove "Bearer " prefix
            
            # Mock validation
            if token and len(token) > 10:
                return {
                    'valid': True,
                    'user_info': {
                        'user_id': 'user_123',
                        'creator_id': 'creator_456',
                        'tier': 'creator',
                        'permissions': ['content_upload', 'analytics', 'distribution']
                    }
                }
        
        return {'valid': False}
    
    def _update_average_response_time(self, response_time_ms -> None: float) -> None:
        """Update average response time metric"""
        current_avg = self.gateway_metrics['average_response_time']
        total_requests = self.gateway_metrics['total_requests']
        
        # Calculate rolling average
        self.gateway_metrics['average_response_time'] = (
            (current_avg * (total_requests - 1) + response_time_ms) / total_requests
        )
    
    async def get_gateway_status(self) -> Dict[str, Any]:
        """Get comprehensive gateway status"""
        
        status = {
            'timestamp': datetime.utcnow().isoformat(),
            'gateway_mode': self.gateway_config['mode'].value,
            'health_status': 'healthy',
            'metrics': self.gateway_metrics.copy(),
            'configuration': {
                'cors_enabled': self.gateway_config['enable_cors'],
                'compression_enabled': self.gateway_config['enable_compression'],
                'caching_enabled': self.gateway_config['enable_caching'],
                'max_request_size_mb': self.gateway_config['max_request_size'] / (1024 * 1024),
                'request_timeout_seconds': self.gateway_config['request_timeout']
            },
            'service_health': {},
            'rate_limiting_status': await self.rate_limiter.get_status(),
            'api_endpoints': {
                'total_endpoints': len(self.rest_api_manager.endpoints),
                'active_endpoints': len([
                    e for e in self.rest_api_manager.endpoints.values() 
                    if e.endpoint_id in self.rest_api_manager.api_metrics['requests_by_endpoint']
                ])
            }
        }
        
        # Check service health
        for service_name, endpoints in self.service_registry.items():
            healthy_count = len([e for e in endpoints if e['health'] == 'healthy'])
            total_count = len(endpoints)
            
            status['service_health'][service_name] = {
                'healthy_instances': healthy_count,
                'total_instances': total_count,
                'health_percentage': (healthy_count / total_count) * 100 if total_count > 0 else 0
            }
        
        return status
    
    async def add_middleware(self, middleware_func) -> None:
        """Add custom middleware to the stack"""
        self.middleware_stack.append(middleware_func)
        logger.info("Custom middleware added to gateway")
    
    async def add_request_interceptor(self, interceptor_func) -> None:
        """Add request interceptor"""
        self.request_interceptors.append(interceptor_func)
        logger.info("Request interceptor added to gateway")
    
    async def add_response_interceptor(self, interceptor_func) -> None:
        """Add response interceptor"""
        self.response_interceptors.append(interceptor_func)
        logger.info("Response interceptor added to gateway")