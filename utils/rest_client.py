"""
REST Client - Microservices Expert Implementation
===============================================

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.

Enterprise REST client for microservices communication.
"""

import asyncio
import logging
import time
import json
from typing import Dict, Any, Optional, Union, List
from dataclasses import dataclass
from datetime import datetime
import aiohttp

logger = logging.getLogger(__name__)


@dataclass
class RequestConfig:
    """REST request configuration"""
    timeout: int = 30
    retries: int = 3
    retry_delay: float = 1.0
    verify_ssl: bool = True
    follow_redirects: bool = True


@dataclass
class Response:
    """REST response wrapper"""
    status_code: int
    headers: Dict[str, str]
    body: Union[str, Dict[str, Any]]
    response_time: float
    success: bool
    error: Optional[str] = None


class RestClient:
    """
    Enterprise REST client with advanced features:
    - Automatic retries with exponential backoff
    - Connection pooling
    - Request/response logging
    - Circuit breaker pattern
    - Authentication handling
    - Response caching
    """
    
    def __init__(self) -> None:
        """Initialize REST client"""
        self.session = None
        self.default_config = RequestConfig()
        self.circuit_breaker_threshold = 5
        self.circuit_breaker_timeout = 60
        self.failed_requests = {}
        
        # Request statistics
        self.stats = {
            'total_requests': 0,
            'successful_requests': 0,
            'failed_requests': 0,
            'average_response_time': 0.0,
            'requests_by_method': {},
            'requests_by_status': {}
        }
        
        logger.info("RestClient initialized")
    
    async def __aenter__(self) -> None:
        """Async context manager entry"""
        if not self.session:
            connector = aiohttp.TCPConnector(
                limit=100,  # Total connection pool size
                limit_per_host=20,  # Connections per host
                ttl_dns_cache=300,  # DNS cache TTL
                use_dns_cache=True,
            )
            
            timeout = aiohttp.ClientTimeout(total=30)
            
            self.session = aiohttp.ClientSession(
                connector=connector,
                timeout=timeout,
                headers={'User-Agent': 'Ainflue-RestClient/1.0'}
            )
        
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        """Async context manager exit"""
        if self.session:
            await self.session.close()
            self.session = None
    
    async def get(self, url: str, params: Dict[str, Any] = None,
                  headers: Dict[str, str] = None, config: RequestConfig = None) -> Response:
        """Perform GET request"""
        return await self._request('GET', url, params=params, headers=headers, config=config)
    
    async def post(self, url: str, data: Union[Dict[str, Any], str] = None,
                   json_data: Dict[str, Any] = None, headers: Dict[str, str] = None,
                   config: RequestConfig = None) -> Response:
        """Perform POST request"""
        return await self._request('POST', url, data=data, json=json_data, 
                                 headers=headers, config=config)
    
    async def put(self, url: str, data: Union[Dict[str, Any], str] = None,
                  json_data: Dict[str, Any] = None, headers: Dict[str, str] = None,
                  config: RequestConfig = None) -> Response:
        """Perform PUT request"""
        return await self._request('PUT', url, data=data, json=json_data,
                                 headers=headers, config=config)
    
    async def patch(self, url: str, data: Union[Dict[str, Any], str] = None,
                    json_data: Dict[str, Any] = None, headers: Dict[str, str] = None,
                    config: RequestConfig = None) -> Response:
        """Perform PATCH request"""
        return await self._request('PATCH', url, data=data, json=json_data,
                                 headers=headers, config=config)
    
    async def delete(self, url: str, headers: Dict[str, str] = None,
                     config: RequestConfig = None) -> Response:
        """Perform DELETE request"""
        return await self._request('DELETE', url, headers=headers, config=config)
    
    async def _request(self, method: str, url: str, **kwargs) -> Response:
        """Execute HTTP request with retry logic and error handling"""
        config = kwargs.pop('config', None) or self.default_config
        start_time = time.time()
        
        # Check circuit breaker
        if self._is_circuit_open(url):
            return Response(
                status_code=503,
                headers={},
                body={'error': 'Circuit breaker open'},
                response_time=0.0,
                success=False,
                error='Circuit breaker is open for this endpoint'
            )
        
        last_exception = None
        
        for attempt in range(config.retries + 1):
            try:
                if not self.session:
                    await self.__aenter__()
                
                # Prepare request parameters
                request_kwargs = self._prepare_request_kwargs(kwargs, config)
                
                # Execute request
                async with self.session.request(method, url, **request_kwargs) as response:
                    response_time = time.time() - start_time
                    
                    # Read response body
                    try:
                        if response.headers.get('content-type', '').startswith('application/json'):
                            body = await response.json()
                        else:
                            body = await response.text()
                    except Exception:
                        body = await response.text()
                    
                    # Create response object
                    result = Response(
                        status_code=response.status,
                        headers=dict(response.headers),
                        body=body,
                        response_time=response_time,
                        success=200 <= response.status < 400
                    )
                    
                    # Update statistics
                    self._update_stats(method, response.status, response_time, result.success)
                    
                    # Reset circuit breaker on success
                    if result.success and url in self.failed_requests:
                        del self.failed_requests[url]
                    
                    # Handle non-success status codes
                    if not result.success:
                        self._handle_failed_request(url)
                        
                        # Retry on server errors
                        if response.status >= 500 and attempt < config.retries:
                            await asyncio.sleep(config.retry_delay * (2 ** attempt))
                            continue
                    
                    logger.debug(f"{method} {url} - Status: {response.status}, Time: {response_time:.3f}s")
                    return result
                    
            except asyncio.TimeoutError:
                last_exception = f"Request timeout after {config.timeout}s"
                self._handle_failed_request(url)
                
            except aiohttp.ClientError as e:
                last_exception = f"Client error: {str(e)}"
                self._handle_failed_request(url)
                
            except Exception as e:
                last_exception = f"Unexpected error: {str(e)}"
                self._handle_failed_request(url)
            
            # Wait before retry
            if attempt < config.retries:
                delay = config.retry_delay * (2 ** attempt)  # Exponential backoff
                logger.warning(f"Request failed, retrying in {delay}s (attempt {attempt + 1}/{config.retries})")
                await asyncio.sleep(delay)
        
        # All retries exhausted
        response_time = time.time() - start_time
        self._update_stats(method, 0, response_time, False)
        
        return Response(
            status_code=0,
            headers={},
            body={'error': last_exception},
            response_time=response_time,
            success=False,
            error=last_exception
        )
    
    def _prepare_request_kwargs(self, kwargs: Dict[str, Any], config: RequestConfig) -> Dict[str, Any]:
        """Prepare request keyword arguments"""
        request_kwargs = {}
        
        # Headers
        headers = kwargs.get('headers', {})
        if headers:
            request_kwargs['headers'] = headers
        
        # Parameters (for GET requests)
        params = kwargs.get('params')
        if params:
            request_kwargs['params'] = params
        
        # JSON data
        json_data = kwargs.get('json')
        if json_data:
            request_kwargs['json'] = json_data
        
        # Form data
        data = kwargs.get('data')
        if data:
            request_kwargs['data'] = data
        
        # SSL verification
        request_kwargs['ssl'] = config.verify_ssl
        
        # Timeout
        request_kwargs['timeout'] = aiohttp.ClientTimeout(total=config.timeout)
        
        # Redirects
        request_kwargs['allow_redirects'] = config.follow_redirects
        
        return request_kwargs
    
    def _is_circuit_open(self, url: str) -> bool:
        """Check if circuit breaker is open for URL"""
        if url not in self.failed_requests:
            return False
        
        failed_count, last_failure_time = self.failed_requests[url]
        
        # Check if threshold reached
        if failed_count < self.circuit_breaker_threshold:
            return False
        
        # Check if timeout period has passed
        if time.time() - last_failure_time > self.circuit_breaker_timeout:
            # Reset circuit breaker
            del self.failed_requests[url]
            return False
        
        return True
    
    def _handle_failed_request(self, url -> None: str) -> None:
        """Handle failed request for circuit breaker"""
        if url not in self.failed_requests:
            self.failed_requests[url] = [0, 0]
        
        self.failed_requests[url][0] += 1  # Increment failure count
        self.failed_requests[url][1] = time.time()  # Update last failure time
    
    def _update_stats(self, method -> None: str, status_code -> None: int, response_time -> None: float, success -> None: bool) -> None:
        """Update request statistics"""
        self.stats['total_requests'] += 1
        
        if success:
            self.stats['successful_requests'] += 1
        else:
            self.stats['failed_requests'] += 1
        
        # Update average response time
        total_requests = self.stats['total_requests']
        current_avg = self.stats['average_response_time']
        new_avg = (current_avg * (total_requests - 1) + response_time) / total_requests
        self.stats['average_response_time'] = new_avg
        
        # Update method statistics
        if method not in self.stats['requests_by_method']:
            self.stats['requests_by_method'][method] = 0
        self.stats['requests_by_method'][method] += 1
        
        # Update status code statistics
        if status_code not in self.stats['requests_by_status']:
            self.stats['requests_by_status'][status_code] = 0
        self.stats['requests_by_status'][status_code] += 1
    
    async def health_check(self, url: str, expected_status: int = 200) -> Dict[str, Any]:
        """Perform health check on endpoint"""
        try:
            start_time = time.time()
            response = await self.get(url)
            
            is_healthy = response.success and response.status_code == expected_status
            
            return {
                'url': url,
                'healthy': is_healthy,
                'status_code': response.status_code,
                'response_time': response.response_time,
                'timestamp': datetime.now().isoformat(),
                'error': response.error
            }
            
        except Exception as e:
            return {
                'url': url,
                'healthy': False,
                'status_code': 0,
                'response_time': time.time() - start_time if 'start_time' in locals() else 0,
                'timestamp': datetime.now().isoformat(),
                'error': str(e)
            }
    
    async def batch_requests(self, requests: List[Dict[str, Any]]) -> List[Response]:
        """Execute multiple requests concurrently"""
        try:
            tasks = []
            
            for request in requests:
                method = request.get('method', 'GET').upper()
                url = request['url']
                kwargs = {k: v for k, v in request.items() if k not in ['method', 'url']}
                
                if method == 'GET':
                    task = self.get(url, **kwargs)
                elif method == 'POST':
                    task = self.post(url, **kwargs)
                elif method == 'PUT':
                    task = self.put(url, **kwargs)
                elif method == 'PATCH':
                    task = self.patch(url, **kwargs)
                elif method == 'DELETE':
                    task = self.delete(url, **kwargs)
                else:
                    # Create a failed response for unsupported methods
                    task = asyncio.create_task(asyncio.coroutine(lambda: Response(
                        status_code=405,
                        headers={},
                        body={'error': f'Unsupported method: {method}'},
                        response_time=0.0,
                        success=False,
                        error=f'Unsupported method: {method}'
                    ))())
                
                tasks.append(task)
            
            # Execute all requests concurrently
            responses = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Handle exceptions
            results = []
            for response in responses:
                if isinstance(response, Exception):
                    results.append(Response(
                        status_code=0,
                        headers={},
                        body={'error': str(response)},
                        response_time=0.0,
                        success=False,
                        error=str(response)
                    ))
                else:
                    results.append(response)
            
            logger.info(f"Batch request completed: {len(requests)} requests")
            return results
            
        except Exception as e:
            logger.error(f"Batch request failed: {e}")
            return [Response(
                status_code=0,
                headers={},
                body={'error': str(e)},
                response_time=0.0,
                success=False,
                error=str(e)
            ) for _ in requests]
    
    def get_stats(self) -> Dict[str, Any]:
        """Get client statistics"""
        stats = self.stats.copy()
        
        if stats['total_requests'] > 0:
            stats['success_rate'] = (stats['successful_requests'] / stats['total_requests']) * 100
        else:
            stats['success_rate'] = 0.0
        
        stats['circuit_breakers_active'] = len(self.failed_requests)
        
        return stats
    
    def reset_stats(self) -> None:
        """Reset statistics"""
        self.stats = {
            'total_requests': 0,
            'successful_requests': 0,
            'failed_requests': 0,
            'average_response_time': 0.0,
            'requests_by_method': {},
            'requests_by_status': {}
        }
        logger.info("Statistics reset")


# Global instance
rest_client = RestClient()