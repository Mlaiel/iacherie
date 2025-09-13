"""API Gateway - Internal API Gateway Management
===========================================

Centralized API gateway for managing all third-party integration requests.
Provides routing, load balancing, monitoring, and security enforcement.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import logging
import time
from typing import Dict, List, Optional, Any, Callable, Union
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import json
import hashlib
from urllib.parse import urljoin, urlparse

import httpx
import aiohttp
from tenacity import retry, stop_after_attempt, wait_exponential


class RequestMethod(Enum):
    """HTTP request methods."""
    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    PATCH = "PATCH"
    DELETE = "DELETE"
    HEAD = "HEAD"
    OPTIONS = "OPTIONS"


class LoadBalancingStrategy(Enum):
    """Load balancing strategies."""
    ROUND_ROBIN = "round_robin"
    WEIGHTED_ROUND_ROBIN = "weighted_round_robin"
    LEAST_CONNECTIONS = "least_connections"
    HEALTH_BASED = "health_based"
    RESPONSE_TIME = "response_time"


@dataclass
class APIEndpoint:
    """API endpoint configuration."""
    name: str
    base_url: str
    integration_name: str
    weight: int = 1
    max_connections: int = 100
    timeout: int = 30
    health_check_path: str = "/health"
    health_check_interval: int = 60  # seconds
    is_healthy: bool = True
    current_connections: int = 0
    total_requests: int = 0
    failed_requests: int = 0
    average_response_time: float = 0.0
    last_health_check: Optional[datetime] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class APIRequest:
    """API request wrapper."""
    integration_name: str
    method: RequestMethod
    endpoint: str
    headers: Dict[str, str] = field(default_factory=dict)
    params: Dict[str, Any] = field(default_factory=dict)
    data: Optional[Union[Dict[str, Any], str, bytes]] = None
    json_data: Optional[Dict[str, Any]] = None
    timeout: Optional[int] = None
    retries: int = 3
    user_id: Optional[str] = None
    request_id: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class APIResponse:
    """API response wrapper."""
    status_code: int
    headers: Dict[str, str]
    content: bytes
    text: str
    json_data: Optional[Dict[str, Any]] = None
    response_time: float = 0.0
    endpoint_used: str = ""
    cached: bool = False
    request_id: str = ""
    error: Optional[str] = None


class APIGateway:
    """Internal API gateway for third-party integration management.
    
    Provides centralized routing, load balancing, health monitoring,
    and request/response transformation for all external API calls.
    """
    
    def __init__(self):
        """Initialize API gateway."""
        self.logger = logging.getLogger(__name__)
        
        # Endpoint registry by integration
        self.endpoints: Dict[str, List[APIEndpoint]] = {}
        
        # Load balancing state
        self.round_robin_state: Dict[str, int] = {}
        
        # HTTP clients pool
        self.http_clients: Dict[str, httpx.AsyncClient] = {}
        
        # Request/response middleware
        self.request_middleware: List[Callable] = []
        self.response_middleware: List[Callable] = []
        
        # Health monitoring
        self.health_monitor_task: Optional[asyncio.Task] = None
        
        # Global settings
        self.default_timeout = 30
        self.max_retries = 3
        self.load_balancing_strategy = LoadBalancingStrategy.HEALTH_BASED
        
        # Metrics
        self.global_metrics = {
            "total_requests": 0,
            "successful_requests": 0,
            "failed_requests": 0,
            "average_response_time": 0.0,
            "active_connections": 0
        }
        
        # Initialize default middleware
        self._initialize_default_middleware()
    
    def _initialize_default_middleware(self) -> None:
        """Initialize default request/response middleware."""
        
        async def request_logger(request: APIRequest) -> APIRequest:
            """Log outgoing requests."""
            self.logger.debug(
                f"API Request: {request.method.value} {request.integration_name}/{request.endpoint}"
            )
            return request
        
        async def response_logger(response: APIResponse) -> APIResponse:
            """Log incoming responses."""
            self.logger.debug(
                f"API Response: {response.status_code} ({response.response_time:.3f}s) {response.endpoint_used}"
            )
            return response
        
        async def add_request_id(request: APIRequest) -> APIRequest:
            """Add unique request ID to headers."""
            if not request.request_id:
                request.request_id = hashlib.md5(
                    f"{request.integration_name}{request.endpoint}{time.time()}".encode()
                ).hexdigest()[:16]
            
            request.headers["X-Request-ID"] = request.request_id
            request.headers["X-Integration"] = request.integration_name
            
            return request
        
        async def add_user_agent(request: APIRequest) -> APIRequest:
            """Add Ainflue user agent."""
            request.headers["User-Agent"] = "Ainflue-Integration-Gateway/1.0"
            return request
        
        # Register middleware
        self.request_middleware.extend([
            add_request_id,
            add_user_agent,
            request_logger
        ])
        
        self.response_middleware.extend([
            response_logger
        ])
    
    async def register_endpoint(self, endpoint: APIEndpoint) -> bool:
        """Register API endpoint for integration."""
        try:
            integration_name = endpoint.integration_name
            
            if integration_name not in self.endpoints:
                self.endpoints[integration_name] = []
                self.round_robin_state[integration_name] = 0
            
            # Validate endpoint
            if not await self._validate_endpoint(endpoint):
                return False
            
            # Add to endpoints list
            self.endpoints[integration_name].append(endpoint)
            
            # Create HTTP client for this endpoint
            client_key = f"{integration_name}_{endpoint.name}"
            self.http_clients[client_key] = httpx.AsyncClient(
                timeout=httpx.Timeout(endpoint.timeout),
                limits=httpx.Limits(max_connections=endpoint.max_connections)
            )
            
            self.logger.info(f"API endpoint registered: {endpoint.name} for {integration_name}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to register endpoint {endpoint.name}: {str(e)}")
            return False
    
    async def unregister_endpoint(self, integration_name: str, endpoint_name: str) -> bool:
        """Unregister API endpoint."""
        try:
            if integration_name not in self.endpoints:
                return False
            
            # Find and remove endpoint
            self.endpoints[integration_name] = [
                ep for ep in self.endpoints[integration_name]
                if ep.name != endpoint_name
            ]
            
            # Close HTTP client
            client_key = f"{integration_name}_{endpoint_name}"
            if client_key in self.http_clients:
                await self.http_clients[client_key].aclose()
                del self.http_clients[client_key]
            
            self.logger.info(f"API endpoint unregistered: {endpoint_name} from {integration_name}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to unregister endpoint {endpoint_name}: {str(e)}")
            return False
    
    async def execute_request(
        self,
        integration_name: str,
        method: str,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        timeout: Optional[int] = None,
        user_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Execute API request through gateway."""
        try:
            # Create request object
            request = APIRequest(
                integration_name=integration_name,
                method=RequestMethod(method.upper()),
                endpoint=endpoint,
                headers=headers or {},
                json_data=data,
                timeout=timeout or self.default_timeout,
                user_id=user_id
            )
            
            # Apply request middleware
            for middleware in self.request_middleware:
                request = await middleware(request)
            
            # Select endpoint using load balancing
            api_endpoint = await self._select_endpoint(integration_name)
            if not api_endpoint:
                raise ValueError(f"No healthy endpoints available for {integration_name}")
            
            # Execute request with retry logic
            response = await self._execute_with_retries(request, api_endpoint)
            
            # Apply response middleware
            for middleware in self.response_middleware:
                response = await middleware(response)
            
            # Update metrics
            await self._update_metrics(api_endpoint, response)
            
            # Return standardized response
            return {
                "status_code": response.status_code,
                "data": response.json_data,
                "headers": response.headers,
                "response_time": response.response_time,
                "endpoint_used": response.endpoint_used,
                "request_id": response.request_id,
                "cached": response.cached,
                "success": 200 <= response.status_code < 300
            }
            
        except Exception as e:
            self.logger.error(f"API request failed for {integration_name}: {str(e)}")
            self.global_metrics["failed_requests"] += 1
            
            return {
                "status_code": 500,
                "data": None,
                "error": str(e),
                "success": False,
                "integration_name": integration_name
            }
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=10)
    )
    async def _execute_with_retries(self, request: APIRequest, endpoint: APIEndpoint) -> APIResponse:
        """Execute request with automatic retries."""
        start_time = time.time()
        
        try:
            # Get HTTP client
            client_key = f"{endpoint.integration_name}_{endpoint.name}"
            client = self.http_clients.get(client_key)
            
            if not client:
                raise ValueError(f"HTTP client not found for {client_key}")
            
            # Increment connection count
            endpoint.current_connections += 1
            
            # Construct full URL
            full_url = urljoin(endpoint.base_url, request.endpoint.lstrip('/'))
            
            # Prepare request parameters
            request_kwargs = {
                "method": request.method.value,
                "url": full_url,
                "headers": request.headers,
                "timeout": request.timeout
            }
            
            if request.json_data:
                request_kwargs["json"] = request.json_data
            elif request.data:
                if isinstance(request.data, (dict, list)):
                    request_kwargs["json"] = request.data
                else:
                    request_kwargs["content"] = request.data
            
            if request.params:
                request_kwargs["params"] = request.params
            
            # Execute HTTP request
            http_response = await client.request(**request_kwargs)
            
            # Calculate response time
            response_time = time.time() - start_time
            
            # Parse response
            content = http_response.content
            text = http_response.text
            
            json_data = None
            try:
                json_data = http_response.json()
            except Exception:
                pass
            
            # Create response object
            response = APIResponse(
                status_code=http_response.status_code,
                headers=dict(http_response.headers),
                content=content,
                text=text,
                json_data=json_data,
                response_time=response_time,
                endpoint_used=endpoint.name,
                request_id=request.request_id
            )
            
            # Check if response indicates an error that should be retried
            if http_response.status_code >= 500:
                raise httpx.HTTPStatusError(
                    f"Server error: {http_response.status_code}",
                    request=http_response.request,
                    response=http_response
                )
            
            return response
            
        except Exception as e:
            endpoint.failed_requests += 1
            raise
        
        finally:
            # Decrement connection count
            endpoint.current_connections = max(0, endpoint.current_connections - 1)
    
    async def _select_endpoint(self, integration_name: str) -> Optional[APIEndpoint]:
        """Select best endpoint using load balancing strategy."""
        if integration_name not in self.endpoints:
            return None
        
        endpoints = self.endpoints[integration_name]
        healthy_endpoints = [ep for ep in endpoints if ep.is_healthy]
        
        if not healthy_endpoints:
            # Fallback to any available endpoint
            healthy_endpoints = endpoints
        
        if not healthy_endpoints:
            return None
        
        if self.load_balancing_strategy == LoadBalancingStrategy.ROUND_ROBIN:
            return self._select_round_robin(integration_name, healthy_endpoints)
        elif self.load_balancing_strategy == LoadBalancingStrategy.WEIGHTED_ROUND_ROBIN:
            return self._select_weighted_round_robin(integration_name, healthy_endpoints)
        elif self.load_balancing_strategy == LoadBalancingStrategy.LEAST_CONNECTIONS:
            return self._select_least_connections(healthy_endpoints)
        elif self.load_balancing_strategy == LoadBalancingStrategy.RESPONSE_TIME:
            return self._select_fastest_response(healthy_endpoints)
        else:  # HEALTH_BASED
            return self._select_healthiest(healthy_endpoints)
    
    def _select_round_robin(self, integration_name: str, endpoints: List[APIEndpoint]) -> APIEndpoint:
        """Select endpoint using round-robin."""
        current_index = self.round_robin_state[integration_name]
        selected = endpoints[current_index % len(endpoints)]
        self.round_robin_state[integration_name] = (current_index + 1) % len(endpoints)
        return selected
    
    def _select_weighted_round_robin(self, integration_name: str, endpoints: List[APIEndpoint]) -> APIEndpoint:
        """Select endpoint using weighted round-robin."""
        total_weight = sum(ep.weight for ep in endpoints)
        current_index = self.round_robin_state[integration_name]
        
        # Calculate weighted position
        current_weight = 0
        for i, endpoint in enumerate(endpoints):
            current_weight += endpoint.weight
            if current_index < current_weight:
                self.round_robin_state[integration_name] = (current_index + 1) % total_weight
                return endpoint
        
        # Fallback to first endpoint
        return endpoints[0]
    
    def _select_least_connections(self, endpoints: List[APIEndpoint]) -> APIEndpoint:
        """Select endpoint with least active connections."""
        return min(endpoints, key=lambda ep: ep.current_connections)
    
    def _select_fastest_response(self, endpoints: List[APIEndpoint]) -> APIEndpoint:
        """Select endpoint with fastest average response time."""
        return min(endpoints, key=lambda ep: ep.average_response_time or float('inf'))
    
    def _select_healthiest(self, endpoints: List[APIEndpoint]) -> APIEndpoint:
        """Select healthiest endpoint based on multiple factors."""
        def health_score(endpoint: APIEndpoint) -> float:
            # Calculate composite health score
            success_rate = 1.0 - (endpoint.failed_requests / max(endpoint.total_requests, 1))
            connection_load = 1.0 - (endpoint.current_connections / max(endpoint.max_connections, 1))
            response_factor = 1.0 / (1.0 + endpoint.average_response_time)
            
            return (success_rate * 0.4 + connection_load * 0.3 + response_factor * 0.3) * endpoint.weight
        
        return max(endpoints, key=health_score)
    
    async def _validate_endpoint(self, endpoint: APIEndpoint) -> bool:
        """Validate endpoint configuration."""
        try:
            # Validate URL
            parsed = urlparse(endpoint.base_url)
            if not parsed.scheme or not parsed.netloc:
                return False
            
            # Test basic connectivity
            client_key = f"{endpoint.integration_name}_{endpoint.name}"
            if client_key not in self.http_clients:
                self.http_clients[client_key] = httpx.AsyncClient(timeout=10)
            
            client = self.http_clients[client_key]
            
            try:
                response = await client.head(endpoint.base_url)
                endpoint.is_healthy = response.status_code < 500
            except Exception:
                endpoint.is_healthy = False
            
            return True
            
        except Exception as e:
            self.logger.error(f"Endpoint validation failed: {str(e)}")
            return False
    
    async def _update_metrics(self, endpoint: APIEndpoint, response: APIResponse) -> None:
        """Update endpoint and global metrics."""
        # Update endpoint metrics
        endpoint.total_requests += 1
        
        # Update average response time (exponential moving average)
        alpha = 0.1  # Smoothing factor
        endpoint.average_response_time = (
            alpha * response.response_time + 
            (1 - alpha) * endpoint.average_response_time
        )
        
        # Update global metrics
        self.global_metrics["total_requests"] += 1
        
        if 200 <= response.status_code < 300:
            self.global_metrics["successful_requests"] += 1
        else:
            self.global_metrics["failed_requests"] += 1
            endpoint.failed_requests += 1
        
        # Update global average response time
        total_requests = self.global_metrics["total_requests"]
        current_avg = self.global_metrics["average_response_time"]
        self.global_metrics["average_response_time"] = (
            (current_avg * (total_requests - 1) + response.response_time) / total_requests
        )
    
    async def start_health_monitoring(self, interval: int = 60) -> None:
        """Start health monitoring for all endpoints."""
        if self.health_monitor_task:
            return
        
        async def health_monitor():
            while True:
                try:
                    await self._check_all_endpoints_health()
                    await asyncio.sleep(interval)
                except asyncio.CancelledError:
                    break
                except Exception as e:
                    self.logger.error(f"Health monitoring error: {str(e)}")
                    await asyncio.sleep(interval)
        
        self.health_monitor_task = asyncio.create_task(health_monitor())
        self.logger.info("Health monitoring started")
    
    async def stop_health_monitoring(self) -> None:
        """Stop health monitoring."""
        if self.health_monitor_task:
            self.health_monitor_task.cancel()
            try:
                await self.health_monitor_task
            except asyncio.CancelledError:
                pass
            self.health_monitor_task = None
            self.logger.info("Health monitoring stopped")
    
    async def _check_all_endpoints_health(self) -> None:
        """Check health of all registered endpoints."""
        for integration_name, endpoints in self.endpoints.items():
            for endpoint in endpoints:
                await self._check_endpoint_health(endpoint)
    
    async def _check_endpoint_health(self, endpoint: APIEndpoint) -> None:
        """Check health of specific endpoint."""
        try:
            client_key = f"{endpoint.integration_name}_{endpoint.name}"
            client = self.http_clients.get(client_key)
            
            if not client:
                endpoint.is_healthy = False
                return
            
            # Perform health check
            health_url = urljoin(endpoint.base_url, endpoint.health_check_path.lstrip('/'))
            
            start_time = time.time()
            response = await client.get(health_url, timeout=10)
            response_time = time.time() - start_time
            
            # Update health status
            endpoint.is_healthy = response.status_code == 200
            endpoint.last_health_check = datetime.utcnow()
            
            # Update response time if healthy
            if endpoint.is_healthy:
                alpha = 0.2
                endpoint.average_response_time = (
                    alpha * response_time + 
                    (1 - alpha) * endpoint.average_response_time
                )
            
        except Exception as e:
            endpoint.is_healthy = False
            endpoint.last_health_check = datetime.utcnow()
            self.logger.debug(f"Health check failed for {endpoint.name}: {str(e)}")
    
    async def get_endpoint_status(self, integration_name: str) -> Dict[str, Any]:
        """Get status of all endpoints for integration."""
        if integration_name not in self.endpoints:
            return {"error": "Integration not found"}
        
        endpoints_status = []
        for endpoint in self.endpoints[integration_name]:
            success_rate = 1.0 - (endpoint.failed_requests / max(endpoint.total_requests, 1))
            
            endpoints_status.append({
                "name": endpoint.name,
                "base_url": endpoint.base_url,
                "is_healthy": endpoint.is_healthy,
                "current_connections": endpoint.current_connections,
                "max_connections": endpoint.max_connections,
                "total_requests": endpoint.total_requests,
                "failed_requests": endpoint.failed_requests,
                "success_rate": round(success_rate, 3),
                "average_response_time": round(endpoint.average_response_time, 3),
                "weight": endpoint.weight,
                "last_health_check": endpoint.last_health_check.isoformat() if endpoint.last_health_check else None
            })
        
        return {
            "integration_name": integration_name,
            "endpoints": endpoints_status,
            "load_balancing_strategy": self.load_balancing_strategy.value,
            "total_endpoints": len(endpoints_status),
            "healthy_endpoints": len([ep for ep in endpoints_status if ep["is_healthy"]])
        }
    
    async def get_global_status(self) -> Dict[str, Any]:
        """Get global API gateway status."""
        total_endpoints = sum(len(endpoints) for endpoints in self.endpoints.values())
        healthy_endpoints = sum(
            len([ep for ep in endpoints if ep.is_healthy])
            for endpoints in self.endpoints.values()
        )
        
        success_rate = (
            self.global_metrics["successful_requests"] / 
            max(self.global_metrics["total_requests"], 1)
        )
        
        return {
            "total_integrations": len(self.endpoints),
            "total_endpoints": total_endpoints,
            "healthy_endpoints": healthy_endpoints,
            "health_percentage": round((healthy_endpoints / max(total_endpoints, 1)) * 100, 1),
            "load_balancing_strategy": self.load_balancing_strategy.value,
            "global_metrics": {
                "total_requests": self.global_metrics["total_requests"],
                "successful_requests": self.global_metrics["successful_requests"],
                "failed_requests": self.global_metrics["failed_requests"],
                "success_rate": round(success_rate, 3),
                "average_response_time": round(self.global_metrics["average_response_time"], 3)
            },
            "active_http_clients": len(self.http_clients)
        }
    
    async def add_request_middleware(self, middleware: Callable) -> None:
        """Add request middleware."""
        self.request_middleware.append(middleware)
    
    async def add_response_middleware(self, middleware: Callable) -> None:
        """Add response middleware."""
        self.response_middleware.append(middleware)
    
    async def set_load_balancing_strategy(self, strategy: LoadBalancingStrategy) -> None:
        """Set load balancing strategy."""
        self.load_balancing_strategy = strategy
        self.logger.info(f"Load balancing strategy set to: {strategy.value}")
    
    async def shutdown(self) -> None:
        """Shutdown API gateway."""
        self.logger.info("Shutting down API gateway...")
        
        # Stop health monitoring
        await self.stop_health_monitoring()
        
        # Close all HTTP clients
        for client in self.http_clients.values():
            await client.aclose()
        
        self.http_clients.clear()
        self.endpoints.clear()
        
        self.logger.info("API gateway shutdown complete")