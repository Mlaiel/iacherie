"""Asynchronous HTTP Client for Ainflue SDK

Enterprise-grade async client with multi-expert design:
- Backend Senior: High-performance async architecture 
- DevOps: Connection pooling and monitoring
- Sécurité: Security headers and certificate validation
- Lead Dev IA: Intelligent retry and circuit breaker patterns

Author: Fahed Mlaiel (mlaiel@live.de)
"""

import asyncio
import json
import logging
from typing import Dict, Any, Optional, List, Union, AsyncGenerator, Callable
from datetime import datetime, timedelta
import httpx
from contextlib import asynccontextmanager
import ssl
import certifi

from .exceptions import (
    APIError, NetworkError, TimeoutError, RateLimitError,
    AuthenticationError, ValidationError, AinflueSdkException,
    handle_api_response_error, is_retryable_error
)


class CircuitBreakerState:
    """Circuit breaker for resilient API calls"""
    
    def __init__(self, failure_threshold: int = 5, recovery_timeout: int = 60):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.failure_count = 0
        self.last_failure_time: Optional[datetime] = None
        self.state = "CLOSED"  # CLOSED, OPEN, HALF_OPEN
    
    def can_execute(self) -> bool:
        """Check if circuit breaker allows execution"""
        if self.state == "CLOSED":
            return True
        elif self.state == "OPEN":
            if (datetime.utcnow() - self.last_failure_time).seconds > self.recovery_timeout:
                self.state = "HALF_OPEN"
                return True
            return False
        else:  # HALF_OPEN
            return True
    
    def on_success(self):
        """Record successful execution"""
        self.failure_count = 0
        self.state = "CLOSED"
    
    def on_failure(self):
        """Record failed execution"""
        self.failure_count += 1
        self.last_failure_time = datetime.utcnow()
        
        if self.failure_count >= self.failure_threshold:
            self.state = "OPEN"


class RequestMetrics:
    """Request metrics for monitoring (DevOps expertise)"""
    
    def __init__(self):
        self.total_requests = 0
        self.successful_requests = 0
        self.failed_requests = 0
        self.total_response_time = 0.0
        self.start_time = datetime.utcnow()
    
    def record_request(self, response_time: float, success: bool):
        """Record request metrics"""
        self.total_requests += 1
        self.total_response_time += response_time
        
        if success:
            self.successful_requests += 1
        else:
            self.failed_requests += 1
    
    def get_stats(self) -> Dict[str, Any]:
        """Get metrics statistics"""
        uptime = (datetime.utcnow() - self.start_time).total_seconds()
        avg_response_time = self.total_response_time / max(self.total_requests, 1)
        success_rate = self.successful_requests / max(self.total_requests, 1)
        
        return {
            'total_requests': self.total_requests,
            'successful_requests': self.successful_requests,
            'failed_requests': self.failed_requests,
            'success_rate': success_rate,
            'average_response_time_ms': avg_response_time * 1000,
            'requests_per_second': self.total_requests / max(uptime, 1),
            'uptime_seconds': uptime
        }


class AsyncAinflueClient:
    """High-performance asynchronous HTTP client for Ainflue API
    
    Features:
    - Connection pooling and keep-alive
    - Intelligent retry with exponential backoff
    - Circuit breaker pattern
    - Request/response middleware
    - Performance monitoring
    - Security hardening
    """
    
    def __init__(
        self,
        base_url: str = "https://api.ainflue.com",
        api_key: Optional[str] = None,
        timeout: int = 30,
        max_retries: int = 3,
        retry_delay: float = 1.0,
        max_connections: int = 100,
        max_keepalive_connections: int = 20,
        verify_ssl: bool = True,
        custom_headers: Optional[Dict[str, str]] = None,
        middleware: Optional[List[Callable]] = None
    ):
        self.base_url = base_url.rstrip('/')
        self.api_key = api_key
        self.timeout = timeout
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.verify_ssl = verify_ssl
        self.custom_headers = custom_headers or {}
        self.middleware = middleware or []
        
        # Initialize components
        self.logger = logging.getLogger(__name__)
        self.circuit_breaker = CircuitBreakerState()
        self.metrics = RequestMetrics()
        
        # HTTP client configuration
        self._client: Optional[httpx.AsyncClient] = None
        self._client_config = {
            'timeout': httpx.Timeout(timeout),
            'limits': httpx.Limits(
                max_connections=max_connections,
                max_keepalive_connections=max_keepalive_connections
            ),
            'verify': self._get_ssl_context() if verify_ssl else False,
            'http2': True  # Enable HTTP/2 for better performance
        }
        
        # Rate limiting
        self._rate_limit_semaphore = asyncio.Semaphore(50)  # Max 50 concurrent requests
        self._last_request_times: List[datetime] = []
    
    def _get_ssl_context(self) -> ssl.SSLContext:
        """Create secure SSL context (Sécurité expertise)"""
        context = ssl.create_default_context(cafile=certifi.where())
        context.check_hostname = True
        context.verify_mode = ssl.CERT_REQUIRED
        context.minimum_version = ssl.TLSVersion.TLSv1_2
        
        # Security hardening
        context.set_ciphers('ECDHE+AESGCM:ECDHE+CHACHA20:DHE+AESGCM:DHE+CHACHA20:!aNULL:!MD5:!DSS')
        context.options |= ssl.OP_NO_SSLv2 | ssl.OP_NO_SSLv3 | ssl.OP_NO_TLSv1 | ssl.OP_NO_TLSv1_1
        
        return context
    
    def _get_default_headers(self) -> Dict[str, str]:
        """Get default request headers"""
        headers = {
            'User-Agent': 'Ainflue-Python-SDK/1.0.0',
            'Accept': 'application/json',
            'Content-Type': 'application/json',
            'X-SDK-Version': '1.0.0',
            'X-Client-Type': 'async-python',
        }
        
        if self.api_key:
            headers['Authorization'] = f'Bearer {self.api_key}'
        
        # Add custom headers
        headers.update(self.custom_headers)
        
        return headers
    
    async def __aenter__(self):
        """Async context manager entry"""
        await self._ensure_client()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        await self.close()
    
    async def _ensure_client(self):
        """Ensure HTTP client is initialized"""
        if self._client is None:
            self._client = httpx.AsyncClient(
                base_url=self.base_url,
                headers=self._get_default_headers(),
                **self._client_config
            )
    
    async def close(self):
        """Close the HTTP client"""
        if self._client:
            await self._client.aclose()
            self._client = None
    
    async def _check_rate_limit(self):
        """Check rate limiting (DevOps expertise)"""
        now = datetime.utcnow()
        
        # Remove old timestamps (older than 1 minute)
        self._last_request_times = [
            ts for ts in self._last_request_times 
            if (now - ts).total_seconds() < 60
        ]
        
        # Check if we're within rate limits (60 requests per minute)
        if len(self._last_request_times) >= 60:
            sleep_time = 60 - (now - self._last_request_times[0]).total_seconds()
            if sleep_time > 0:
                self.logger.warning(f"Rate limit reached, sleeping for {sleep_time:.2f}s")
                await asyncio.sleep(sleep_time)
        
        self._last_request_times.append(now)
    
    async def _apply_middleware(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """Apply request middleware"""
        for middleware_func in self.middleware:
            request_data = await middleware_func(request_data)
        return request_data
    
    async def _make_request_with_retry(
        self,
        method: str,
        endpoint: str,
        data: Optional[Dict] = None,
        params: Optional[Dict] = None,
        headers: Optional[Dict] = None,
        stream: bool = False
    ) -> Union[Dict[str, Any], AsyncGenerator]:
        """Make HTTP request with retry logic and circuit breaker"""
        
        # Check circuit breaker
        if not self.circuit_breaker.can_execute():
            raise APIError("Circuit breaker is open, service unavailable")
        
        # Rate limiting
        async with self._rate_limit_semaphore:
            await self._check_rate_limit()
            
            await self._ensure_client()
            
            # Prepare request data for middleware
            request_data = {
                'method': method,
                'endpoint': endpoint,
                'data': data,
                'params': params,
                'headers': headers or {}
            }
            
            # Apply middleware
            request_data = await self._apply_middleware(request_data)
            
            # Merge headers
            final_headers = self._get_default_headers()
            final_headers.update(request_data['headers'])
            
            last_exception = None
            start_time = asyncio.get_event_loop().time()
            
            for attempt in range(self.max_retries + 1):
                try:
                    self.logger.debug(f"Making {method} request to {endpoint} (attempt {attempt + 1})")
                    
                    # Make the actual request
                    if stream:
                        response = await self._client.stream(
                            method=method,
                            url=endpoint,
                            json=request_data['data'],
                            params=request_data['params'],
                            headers=final_headers
                        )
                        return self._handle_streaming_response(response)
                    else:
                        response = await self._client.request(
                            method=method,
                            url=endpoint,
                            json=request_data['data'],
                            params=request_data['params'],
                            headers=final_headers
                        )
                        
                        return await self._handle_response(response)
                
                except Exception as e:
                    last_exception = e
                    
                    # Check if error is retryable
                    if not is_retryable_error(e) or attempt == self.max_retries:
                        break
                    
                    # Calculate delay with exponential backoff and jitter
                    delay = self.retry_delay * (2 ** attempt) + (asyncio.get_event_loop().time() % 1)
                    
                    self.logger.warning(
                        f"Request failed (attempt {attempt + 1}), retrying in {delay:.2f}s: {str(e)}"
                    )
                    
                    await asyncio.sleep(delay)
            
            # Record metrics
            response_time = asyncio.get_event_loop().time() - start_time
            self.metrics.record_request(response_time, False)
            self.circuit_breaker.on_failure()
            
            # Raise the last exception
            if isinstance(last_exception, AinflueSdkException):
                raise last_exception
            else:
                raise NetworkError(f"Request failed after {self.max_retries + 1} attempts") from last_exception
    
    async def _handle_response(self, response: httpx.Response) -> Dict[str, Any]:
        """Handle HTTP response"""
        start_time = asyncio.get_event_loop().time()
        
        try:
            # Check for HTTP errors
            if response.status_code >= 400:
                error_data = {}
                try:
                    error_data = response.json()
                except:
                    error_data = {'message': response.text}
                
                exception = handle_api_response_error(error_data, response.status_code)
                raise exception
            
            # Parse JSON response
            try:
                result = response.json()
            except json.JSONDecodeError as e:
                raise ValidationError(f"Invalid JSON response: {str(e)}")
            
            # Record successful metrics
            response_time = asyncio.get_event_loop().time() - start_time
            self.metrics.record_request(response_time, True)
            self.circuit_breaker.on_success()
            
            return result
            
        except AinflueSdkException:
            # Re-raise SDK exceptions
            response_time = asyncio.get_event_loop().time() - start_time
            self.metrics.record_request(response_time, False)
            raise
    
    @asynccontextmanager
    async def _handle_streaming_response(self, response: httpx.Response) -> AsyncGenerator:
        """Handle streaming response"""
        try:
            async with response as stream:
                if stream.status_code >= 400:
                    error_text = await stream.aread()
                    try:
                        error_data = json.loads(error_text)
                    except:
                        error_data = {'message': error_text.decode()}
                    
                    exception = handle_api_response_error(error_data, stream.status_code)
                    raise exception
                
                yield stream
                
        except AinflueSdkException:
            raise
        except Exception as e:
            raise NetworkError(f"Streaming error: {str(e)}") from e
    
    # Public API methods
    async def get(
        self,
        endpoint: str,
        params: Optional[Dict] = None,
        headers: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """Make GET request"""
        return await self._make_request_with_retry('GET', endpoint, params=params, headers=headers)
    
    async def post(
        self,
        endpoint: str,
        data: Optional[Dict] = None,
        params: Optional[Dict] = None,
        headers: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """Make POST request"""
        return await self._make_request_with_retry('POST', endpoint, data=data, params=params, headers=headers)
    
    async def put(
        self,
        endpoint: str,
        data: Optional[Dict] = None,
        params: Optional[Dict] = None,
        headers: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """Make PUT request"""
        return await self._make_request_with_retry('PUT', endpoint, data=data, params=params, headers=headers)
    
    async def delete(
        self,
        endpoint: str,
        params: Optional[Dict] = None,
        headers: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """Make DELETE request"""
        return await self._make_request_with_retry('DELETE', endpoint, params=params, headers=headers)
    
    async def patch(
        self,
        endpoint: str,
        data: Optional[Dict] = None,
        params: Optional[Dict] = None,
        headers: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """Make PATCH request"""
        return await self._make_request_with_retry('PATCH', endpoint, data=data, params=params, headers=headers)
    
    @asynccontextmanager
    async def stream(
        self,
        method: str,
        endpoint: str,
        data: Optional[Dict] = None,
        params: Optional[Dict] = None,
        headers: Optional[Dict] = None
    ):
        """Make streaming request"""
        stream_generator = await self._make_request_with_retry(
            method, endpoint, data=data, params=params, headers=headers, stream=True
        )
        async with stream_generator as stream:
            yield stream
    
    async def upload_file(
        self,
        endpoint: str,
        file_path: str,
        field_name: str = "file",
        additional_data: Optional[Dict] = None,
        headers: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """Upload file with multipart form data"""
        await self._ensure_client()
        
        files = {field_name: open(file_path, 'rb')}
        data = additional_data or {}
        
        try:
            response = await self._client.post(
                endpoint,
                files=files,
                data=data,
                headers=headers
            )
            return await self._handle_response(response)
        
        finally:
            # Close file handle
            files[field_name].close()
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get client metrics"""
        return {
            'client_metrics': self.metrics.get_stats(),
            'circuit_breaker': {
                'state': self.circuit_breaker.state,
                'failure_count': self.circuit_breaker.failure_count,
                'last_failure': self.circuit_breaker.last_failure_time.isoformat() if self.circuit_breaker.last_failure_time else None
            }
        }
    
    async def health_check(self) -> Dict[str, Any]:
        """Perform health check"""
        try:
            result = await self.get('/health')
            result['client_status'] = 'healthy'
            result['metrics'] = self.get_metrics()
            return result
        except Exception as e:
            return {
                'client_status': 'unhealthy',
                'error': str(e),
                'metrics': self.get_metrics()
            }


# Export the client
__all__ = ['AsyncAinflueClient', 'CircuitBreakerState', 'RequestMetrics']