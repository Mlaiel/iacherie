"""
External API Integrations - Unified Client & Integration Management
Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

This module provides unified external API integration with automatic client creation,
request handling, error management, and response processing for all configured platforms.
"""

import asyncio
import aiohttp
import json
import logging
from typing import Dict, List, Any, Optional, Union, Callable, Type
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from urllib.parse import urljoin, urlencode

from .api_manager import APIManager
from .authentication import APIAuthenticationManager, AuthToken
from .rate_limiting import APIRateLimiter, RateLimitResult
from .monitoring import APIMonitoringManager

logger = logging.getLogger(__name__)

class RequestMethod(Enum):
    """HTTP request methods"""
    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    DELETE = "DELETE"
    PATCH = "PATCH"
    HEAD = "HEAD"
    OPTIONS = "OPTIONS"

class ResponseFormat(Enum):
    """API response formats"""
    JSON = "json"
    XML = "xml"
    TEXT = "text"
    BINARY = "binary"

@dataclass
class APIRequest:
    """API request configuration"""
    method: RequestMethod
    endpoint: str
    params: Optional[Dict[str, Any]] = None
    data: Optional[Union[Dict[str, Any], str, bytes]] = None
    headers: Optional[Dict[str, str]] = None
    timeout: Optional[int] = None
    expected_status: List[int] = field(default_factory=lambda: [200])
    response_format: ResponseFormat = ResponseFormat.JSON
    retry_attempts: int = 3
    retry_delay: float = 1.0

@dataclass
class APIResponse:
    """API response wrapper"""
    success: bool
    status_code: int
    data: Any
    headers: Dict[str, str]
    response_time: float
    error_message: Optional[str] = None
    raw_response: Optional[str] = None

class APIClient:
    """Generic API client for external integrations"""
    
    def __init__(self, api_name: str, config: Dict[str, Any], 
                 auth_manager: APIAuthenticationManager,
                 rate_limiter: APIRateLimiter,
                 monitoring_manager: APIMonitoringManager):
        self.api_name = api_name
        self.config = config
        self.auth_manager = auth_manager
        self.rate_limiter = rate_limiter
        self.monitoring_manager = monitoring_manager
        self.base_url = config.get('base_url', '')
        self.default_headers = {
            'User-Agent': 'IA-Influencer-Agent/1.0',
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        }
        self.session: Optional[aiohttp.ClientSession] = None
    
    async def __aenter__(self):
        """Async context manager entry"""
        await self._ensure_session()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        await self.close()
    
    async def _ensure_session(self):
        """Ensure HTTP session is created"""
        if self.session is None or self.session.closed:
            # Get authentication headers
            auth_headers = self.auth_manager.get_auth_headers(self.api_name)
            headers = {**self.default_headers, **auth_headers}
            
            # Configure session
            timeout = aiohttp.ClientTimeout(
                total=self.config.get('timeout_seconds', 30),
                connect=10
            )
            
            connector = aiohttp.TCPConnector(
                limit=100,
                limit_per_host=30,
                keepalive_timeout=30,
                ssl=True
            )
            
            self.session = aiohttp.ClientSession(
                headers=headers,
                timeout=timeout,
                connector=connector,
                raise_for_status=False
            )
    
    async def close(self):
        """Close HTTP session"""
        if self.session and not self.session.closed:
            await self.session.close()
    
    async def make_request(self, request: APIRequest, user_id: Optional[str] = None) -> APIResponse:
        """
        Make API request with full error handling and monitoring
        
        Args:
            request: API request configuration
            user_id: Optional user ID for rate limiting
            
        Returns:
            APIResponse with result data
        """
        # Check rate limits
        identifier = user_id or 'default'
        rate_limit_result = await self.rate_limiter.check_rate_limit(self.api_name, identifier)
        
        if not rate_limit_result.allowed:
            return APIResponse(
                success=False,
                status_code=429,
                data=None,
                headers={},
                response_time=0.0,
                error_message=f"Rate limit exceeded. Retry after {rate_limit_result.retry_after_seconds} seconds"
            )
        
        # Ensure session is ready
        await self._ensure_session()
        
        # Prepare request
        url = urljoin(self.base_url, request.endpoint.lstrip('/'))
        headers = {**self.default_headers, **(request.headers or {})}
        
        # Add authentication headers
        auth_headers = self.auth_manager.get_auth_headers(
            self.api_name, 
            request.method.value,
            url,
            json.dumps(request.data) if isinstance(request.data, dict) else str(request.data or "")
        )
        headers.update(auth_headers)
        
        # Perform request with retries
        for attempt in range(request.retry_attempts + 1):
            start_time = datetime.utcnow()
            
            try:
                response = await self._execute_request(
                    method=request.method.value,
                    url=url,
                    params=request.params,
                    data=request.data,
                    headers=headers,
                    timeout=request.timeout
                )
                
                response_time = (datetime.utcnow() - start_time).total_seconds()
                
                # Process response
                api_response = await self._process_response(response, request, response_time)
                
                # Record metrics
                self.monitoring_manager.record_api_request(
                    self.api_name,
                    response_time,
                    api_response.success,
                    api_response.status_code,
                    api_response.error_message
                )
                
                # Return on success or non-retryable errors
                if api_response.success or api_response.status_code < 500:
                    return api_response
                
                # Retry on server errors
                if attempt < request.retry_attempts:
                    await asyncio.sleep(request.retry_delay * (attempt + 1))
                    continue
                
                return api_response
                
            except Exception as e:
                response_time = (datetime.utcnow() - start_time).total_seconds()
                error_message = str(e)
                
                # Record error
                self.monitoring_manager.record_api_request(
                    self.api_name,
                    response_time,
                    False,
                    None,
                    error_message
                )
                
                # Retry on connection errors
                if attempt < request.retry_attempts:
                    await asyncio.sleep(request.retry_delay * (attempt + 1))
                    continue
                
                return APIResponse(
                    success=False,
                    status_code=0,
                    data=None,
                    headers={},
                    response_time=response_time,
                    error_message=error_message
                )
        
        # Should not reach here, but just in case
        return APIResponse(
            success=False,
            status_code=0,
            data=None,
            headers={},
            response_time=0.0,
            error_message="Maximum retry attempts exceeded"
        )
    
    async def _execute_request(self, method: str, url: str, **kwargs) -> aiohttp.ClientResponse:
        """Execute HTTP request"""



        return await self.session.request(method, url, **kwargs)
    
    async def _process_response(self, response: aiohttp.ClientResponse, 
                               request: APIRequest, response_time: float) -> APIResponse:
        """Process HTTP response"""
        headers = dict(response.headers)
        
        try:
            # Check if status code is expected
            success = response.status in request.expected_status
            
            # Parse response data based on format
            if request.response_format == ResponseFormat.JSON:
                try:
                    data = await response.json()
                except (json.JSONDecodeError, aiohttp.ContentTypeError):
                    # Fallback to text if JSON parsing fails
                    data = await response.text()
            elif request.response_format == ResponseFormat.XML:
                data = await response.text()
                # Could add XML parsing here if needed
            elif request.response_format == ResponseFormat.BINARY:
                data = await response.read()
            else:  # TEXT
                data = await response.text()
            
            error_message = None if success else f"HTTP {response.status}: {response.reason}"
            
            return APIResponse(
                success=success,
                status_code=response.status,
                data=data,
                headers=headers,
                response_time=response_time,
                error_message=error_message,
                raw_response=str(data) if not isinstance(data, (bytes, dict)) else None
            )
            
        except Exception as e:
            return APIResponse(
                success=False,
                status_code=response.status,
                data=None,
                headers=headers,
                response_time=response_time,
                error_message=f"Response processing error: {str(e)}"
            )
    
    # Convenience methods for common HTTP operations
    async def get(self, endpoint: str, params: Optional[Dict[str, Any]] = None,
                  headers: Optional[Dict[str, str]] = None, **kwargs) -> APIResponse:
        """GET request"""
        request = APIRequest(
            method=RequestMethod.GET,
            endpoint=endpoint,
            params=params,
            headers=headers,
            **kwargs
        )
        return await self.make_request(request)
    
    async def post(self, endpoint: str, data: Optional[Union[Dict[str, Any], str]] = None,
                   params: Optional[Dict[str, Any]] = None,
                   headers: Optional[Dict[str, str]] = None, **kwargs) -> APIResponse:
        """POST request"""
        request = APIRequest(
            method=RequestMethod.POST,
            endpoint=endpoint,
            data=data,
            params=params,
            headers=headers,
            **kwargs
        )
        return await self.make_request(request)
    
    async def put(self, endpoint: str, data: Optional[Union[Dict[str, Any], str]] = None,
                  params: Optional[Dict[str, Any]] = None,
                  headers: Optional[Dict[str, str]] = None, **kwargs) -> APIResponse:
        """PUT request"""
        request = APIRequest(
            method=RequestMethod.PUT,
            endpoint=endpoint,
            data=data,
            params=params,
            headers=headers,
            **kwargs
        )
        return await self.make_request(request)
    
    async def delete(self, endpoint: str, params: Optional[Dict[str, Any]] = None,
                     headers: Optional[Dict[str, str]] = None, **kwargs) -> APIResponse:
        """DELETE request"""
        request = APIRequest(
            method=RequestMethod.DELETE,
            endpoint=endpoint,
            params=params,
            headers=headers,
            **kwargs
        )
        return await self.make_request(request)
    
    async def patch(self, endpoint: str, data: Optional[Union[Dict[str, Any], str]] = None,
                    params: Optional[Dict[str, Any]] = None,
                    headers: Optional[Dict[str, str]] = None, **kwargs) -> APIResponse:
        """PATCH request"""
        request = APIRequest(
            method=RequestMethod.PATCH,
            endpoint=endpoint,
            data=data,
            params=params,
            headers=headers,
            **kwargs
        )
        return await self.make_request(request)

class ExternalAPIIntegration:
    """Main external API integration manager"""
    
    def __init__(self):
        self.api_manager = APIManager()
        self.auth_manager = APIAuthenticationManager()
        self.rate_limiter = APIRateLimiter()
        self.monitoring_manager = APIMonitoringManager()
        self.clients: Dict[str, APIClient] = {}
        self._initialized = False
    
    async def initialize(self):
        """Initialize all components"""
        if self._initialized:
            return
        
        try:
            # Start monitoring
            await self.monitoring_manager.start_continuous_monitoring()
            
            # Initialize API clients for all registered APIs
            all_configs = self.api_manager.get_all_configs()
            
            for api_name, config in all_configs.items():
                await self._create_api_client(api_name, config)
            
            self._initialized = True
            logger.info("External API integration initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize external API integration: {e}")
            raise
    
    async def _create_api_client(self, api_name: str, config: Dict[str, Any]):
        """Create API client for specific API"""



        try:
            client = APIClient(
                api_name=api_name,
                config=config,
                auth_manager=self.auth_manager,
                rate_limiter=self.rate_limiter,
                monitoring_manager=self.monitoring_manager
            )
            
            self.clients[api_name] = client
            
            # Register monitoring
            self.monitoring_manager.register_api_monitoring(api_name, config)
            
            logger.info(f"Created API client for {api_name}")
            
        except Exception as e:
            logger.error(f"Failed to create API client for {api_name}: {e}")
            raise
    
    def get_client(self, api_name: str) -> Optional[APIClient]:
        """Get API client by name"""



        return self.clients.get(api_name)
    
    async def make_request(self, api_name: str, request: APIRequest, 
                          user_id: Optional[str] = None) -> APIResponse:
        """Make request to specific API"""
        client = self.get_client(api_name)
        if not client:
            return APIResponse(
                success=False,
                status_code=0,
                data=None,
                headers={},
                response_time=0.0,
                error_message=f"No client found for API: {api_name}"
            )
        
        return await client.make_request(request, user_id)
    
    # Platform-specific convenience methods
    async def spotify_request(self, endpoint: str, method: RequestMethod = RequestMethod.GET,
                             data: Optional[Dict[str, Any]] = None,
                             user_id: Optional[str] = None) -> APIResponse:
        """Make request to Spotify API"""
        request = APIRequest(method=method, endpoint=endpoint, data=data)
        return await self.make_request("platform_spotify", request, user_id)
    
    async def youtube_request(self, endpoint: str, method: RequestMethod = RequestMethod.GET,
                             data: Optional[Dict[str, Any]] = None,
                             user_id: Optional[str] = None) -> APIResponse:
        """Make request to YouTube API"""
        request = APIRequest(method=method, endpoint=endpoint, data=data)
        return await self.make_request("platform_youtube", request, user_id)
    
    async def instagram_request(self, endpoint: str, method: RequestMethod = RequestMethod.GET,
                               data: Optional[Dict[str, Any]] = None,
                               user_id: Optional[str] = None) -> APIResponse:
        """Make request to Instagram API"""
        request = APIRequest(method=method, endpoint=endpoint, data=data)
        return await self.make_request("platform_instagram", request, user_id)
    
    async def process_payment(self, provider: str, payment_data: Dict[str, Any],
                             user_id: Optional[str] = None) -> APIResponse:
        """Process payment through specific provider"""
        request = APIRequest(
            method=RequestMethod.POST,
            endpoint="/payments",
            data=payment_data,
            expected_status=[200, 201, 202]
        )
        return await self.make_request(f"payment_{provider}", request, user_id)
    
    async def upload_for_protection(self, service: str, file_data: bytes,
                                   metadata: Optional[Dict[str, Any]] = None,
                                   user_id: Optional[str] = None) -> APIResponse:
        """Upload content for protection analysis"""
        request = APIRequest(
            method=RequestMethod.POST,
            endpoint="/fingerprint",
            data=file_data,
            headers={'Content-Type': 'application/octet-stream'},
            response_format=ResponseFormat.JSON
        )
        return await self.make_request(f"protection_{service}", request, user_id)
    
    async def send_notification(self, service: str, notification_data: Dict[str, Any],
                               user_id: Optional[str] = None) -> APIResponse:
        """Send notification through communication service"""
        request = APIRequest(
            method=RequestMethod.POST,
            endpoint="/send",
            data=notification_data
        )
        return await self.make_request(f"communication_{service}", request, user_id)
    
    async def track_analytics_event(self, service: str, event_data: Dict[str, Any],
                                   user_id: Optional[str] = None) -> APIResponse:
        """Track analytics event"""
        request = APIRequest(
            method=RequestMethod.POST,
            endpoint="/track",
            data=event_data
        )
        return await self.make_request(f"analytics_{service}", request, user_id)
    
    async def get_monitoring_summary(self) -> Dict[str, Any]:
        """Get comprehensive monitoring summary"""



        return await self.monitoring_manager.get_monitoring_summary()
    
    async def health_check(self, api_name: Optional[str] = None) -> Dict[str, Any]:
        """Perform health check on specific API or all APIs"""
        if api_name:
            if api_name in self.clients:
                result = await self.monitoring_manager.health_checker.perform_health_check(api_name)
                return {api_name: result}
            else:
                return {api_name: {'status': 'not_found', 'message': 'API not registered'}}
        else:
            return await self.monitoring_manager.health_checker.check_all_apis()
    
    def get_api_status(self) -> Dict[str, Any]:
        """Get status of all APIs"""
        summary = {
            'total_apis': len(self.clients),
            'initialized': self._initialized,
            'apis': {}
        }
        
        for api_name, client in self.clients.items():
            summary['apis'][api_name] = {
                'base_url': client.base_url,
                'session_active': client.session is not None and not client.session.closed
            }
        
        return summary
    
    async def shutdown(self):
        """Shutdown all connections and monitoring"""



        try:
            # Stop monitoring
            self.monitoring_manager.stop_continuous_monitoring()
            
            # Close all client sessions
            for client in self.clients.values():
                await client.close()
            
            self._initialized = False
            logger.info("External API integration shutdown completed")
            
        except Exception as e:
            logger.error(f"Error during shutdown: {e}")

# Global instance
external_api = ExternalAPIIntegration()

# Convenience functions
async def initialize_external_apis():
    """Initialize external API integration"""
    await external_api.initialize()

async def get_api_client(api_name: str) -> Optional[APIClient]:
    """Get API client by name"""



    return external_api.get_client(api_name)

async def make_api_request(api_name: str, request: APIRequest, 
                          user_id: Optional[str] = None) -> APIResponse:
    """Make API request"""



    return await external_api.make_request(api_name, request, user_id)
