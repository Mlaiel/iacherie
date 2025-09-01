"""API Scraper - IA-Influencer-Agent
=================================

Specialized scraper for API-based data collection.
Handles authentication, rate limiting, and API-specific protocols.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: All rights reserved. Unauthorized use, reproduction, or distribution prohibited.

⚠️ CRITICAL LEGAL WARNING ⚠️
UNAUTHORIZED USE, COPYING, OR DISTRIBUTION IS STRICTLY PROHIBITED AND WILL RESULT IN IMMEDIATE LEGAL ACTION.
This technology is EXCLUSIVE property of Fahed Mlaiel. Contact: mlaiel@live.de for licensing.
"""

import asyncio
import aiohttp
import logging
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass
from datetime import datetime, timedelta
import json
import time
import hashlib
import base64
from urllib.parse import urlencode, urlparse
import jwt
from collections import defaultdict

@dataclass
class ApiConfig:
    """
API configuration settings."""
    base_url: str
    api_key: Optional[str] = None
    secret_key: Optional[str] = None
    auth_type: str = 'api_key'  # api_key, oauth, jwt, basic
    rate_limit: int = 100  # requests per minute
    timeout: int = 30
    retry_attempts: int = 3
    retry_delay: int = 1
    headers: Optional[Dict[str, str]] = None
    version: Optional[str] = None

@dataclass
class ApiEndpoint:
    """
API endpoint definition."""
    name: str
    path: str
    method: str = 'GET'
    auth_required: bool = True
    rate_limit: Optional[int] = None
    parameters: Dict[str, Any] = None
    response_format: str = 'json'

class ApiScraper:
    """
    Professional API scraper with comprehensive features.
    
    Features:
    - Multiple authentication methods
    - Rate limiting and throttling
    - Request/response caching
    - Error handling and retries
    - Pagination support
    - Real-time data streaming
    - Webhook handling
    - API monitoring
    """
    
    def __init__(self, config: ApiConfig):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.session: Optional[aiohttp.ClientSession] = None
        
        # Rate limiting
        self.rate_limiter = {}
        self.request_history = defaultdict(list)
        
        # Caching
        self.cache = {}
        self.cache_ttl = 300  # 5 minutes default
        
        # Statistics
        self.stats = {
            'total_requests': 0,
            'successful_requests': 0,
            'failed_requests': 0,
            'cached_responses': 0,
            'rate_limited_requests': 0
        }
        
    async def __aenter__(self):
        """
Async context manager entry."""
        await self._initialize_session()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """
Async context manager exit."""
        if self.session:
            await self.session.close()
            
    async def _initialize_session(self):
        """
Initialize HTTP session with authentication."""
        headers = {
            'User-Agent': 'IA-Influencer-Agent/1.0',
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        }
        
        # Add custom headers
        if self.config.headers:
            headers.update(self.config.headers)
            
        # Add API version header if specified
        if self.config.version:
            headers['API-Version'] = self.config.version
            
        # Add authentication headers
        auth_headers = await self._get_auth_headers()
        headers.update(auth_headers)
        
        connector = aiohttp.TCPConnector(
            limit=50,
            limit_per_host=10,
            ttl_dns_cache=300
        )
        
        timeout = aiohttp.ClientTimeout(total=self.config.timeout)
        
        self.session = aiohttp.ClientSession(
            connector=connector,
            timeout=timeout,
            headers=headers
        )
        
    async def _get_auth_headers(self) -> Dict[str, str]:
        """
Generate authentication headers."""
        headers = {}
        
        if self.config.auth_type == 'api_key':
            if self.config.api_key:
                headers['Authorization'] = f'Bearer {self.config.api_key}'
                
        elif self.config.auth_type == 'basic':
            if self.config.api_key and self.config.secret_key:
                credentials = base64.b64encode(
                    f'{self.config.api_key}:{self.config.secret_key}'.encode()
                ).decode()
                headers['Authorization'] = f'Basic {credentials}'
                
        elif self.config.auth_type == 'jwt':
            if self.config.secret_key:
                payload = {
                    'iss': 'ia-influencer-agent',
                    'iat': int(time.time()),
                    'exp': int(time.time()) + 3600  # 1 hour
                }
                token = jwt.encode(payload, self.config.secret_key, algorithm='HS256')
                headers['Authorization'] = f'Bearer {token}'
                
        elif self.config.auth_type == 'oauth':
            # OAuth implementation would go here
            pass
            
        return headers
        
    async def _check_rate_limit(self, endpoint: str):
        """
Check and enforce rate limiting."""
        now = time.time()
        
        # Clean old requests (older than 1 minute)
        cutoff = now - 60
        self.request_history[endpoint] = [
            req_time for req_time in self.request_history[endpoint]
            if req_time > cutoff
        ]
        
        # Check if we're within rate limit
        requests_in_minute = len(self.request_history[endpoint])
        rate_limit = self.config.rate_limit
        
        if requests_in_minute >= rate_limit:
            wait_time = 60 - (now - self.request_history[endpoint][0])
            if wait_time > 0:
                self.logger.warning(f"Rate limit exceeded for {endpoint}, waiting {wait_time:.2f}s")
                self.stats['rate_limited_requests'] += 1
                await asyncio.sleep(wait_time)
                
        # Record this request
        self.request_history[endpoint].append(now)
        
    async def make_request(self, endpoint: ApiEndpoint, 
                          params: Optional[Dict[str, Any]] = None,
                          data: Optional[Dict[str, Any]] = None,
                          use_cache: bool = True) -> Dict[str, Any]:
        """Make API request with error handling and retries."""
        if not self.session:
            await self._initialize_session()
            
        # Generate cache key
        cache_key = self._generate_cache_key(endpoint, params, data)
        
        # Check cache first
        if use_cache and cache_key in self.cache:
            cached_response = self.cache[cache_key]
            if datetime.now() < cached_response['expires']:
                self.stats['cached_responses'] += 1
                return cached_response['data']
            else:
                del self.cache[cache_key]
                
        # Apply rate limiting
        await self._check_rate_limit(endpoint.name)
        
        # Prepare request
        url = f"{self.config.base_url.rstrip('/')}/{endpoint.path.lstrip('/')}"
        
        # Add parameters
        if params:
            if endpoint.method.upper() == 'GET':
                url += '?' + urlencode(params)
            elif data is None:
                data = params
                
        # Make request with retries
        for attempt in range(self.config.retry_attempts):
            try:
                self.stats['total_requests'] += 1
                
                if endpoint.method.upper() == 'GET':
                    async with self.session.get(url) as response:
                        return await self._process_response(response, cache_key, use_cache)
                        
                elif endpoint.method.upper() == 'POST':
                    async with self.session.post(url, json=data) as response:
                        return await self._process_response(response, cache_key, use_cache)
                        
                elif endpoint.method.upper() == 'PUT':
                    async with self.session.put(url, json=data) as response:
                        return await self._process_response(response, cache_key, use_cache)
                        
                elif endpoint.method.upper() == 'DELETE':
                    async with self.session.delete(url) as response:
                        return await self._process_response(response, cache_key, use_cache)
                        
            except Exception as e:
                self.logger.warning(f"Request attempt {attempt + 1} failed: {e}")
                
                if attempt == self.config.retry_attempts - 1:
                    self.stats['failed_requests'] += 1
                    raise
                    
                # Exponential backoff
                await asyncio.sleep(self.config.retry_delay * (2 ** attempt))
                
    async def _process_response(self, response: aiohttp.ClientResponse,
                              cache_key: str, use_cache: bool) -> Dict[str, Any]:
        """Process API response."""
        if response.status == 200:
            self.stats['successful_requests'] += 1
            
            if response.content_type == 'application/json':
                data = await response.json()
            else:
                text = await response.text()
                data = {'content': text, 'content_type': response.content_type}
                
            # Cache successful response
            if use_cache:
                self.cache[cache_key] = {
                    'data': data,
                    'expires': datetime.now() + timedelta(seconds=self.cache_ttl)
                }
                
            return data
            
        elif response.status == 429:  # Rate limited
            self.stats['rate_limited_requests'] += 1
            retry_after = int(response.headers.get('Retry-After', 60))
            self.logger.warning(f"Rate limited by API, waiting {retry_after}s")
            await asyncio.sleep(retry_after)
            raise Exception("Rate limited by API")
            
        else:
            self.stats['failed_requests'] += 1
            error_text = await response.text()
            raise Exception(f"API request failed with status {response.status}: {error_text}")
            
    def _generate_cache_key(self, endpoint: ApiEndpoint,
                           params: Optional[Dict[str, Any]],
                           data: Optional[Dict[str, Any]]) -> str:
        """Generate cache key for request."""
        key_components = [
            endpoint.name,
            endpoint.path,
            endpoint.method,
            json.dumps(params, sort_keys=True) if params else '',
            json.dumps(data, sort_keys=True) if data else ''
        ]
        
        key_string = '|'.join(key_components)
        return hashlib.md5(key_string.encode()).hexdigest()
        
    async def paginate_request(self, endpoint: ApiEndpoint,
                             params: Optional[Dict[str, Any]] = None,
                             page_param: str = 'page',
                             limit_param: str = 'limit',
                             max_pages: int = 10) -> List[Dict[str, Any]]:
        """
Handle paginated API requests."""
        all_results = []
        page = 1
        
        if not params:
            params = {}
            
        while page <= max_pages:
            # Set pagination parameters
            paginated_params = params.copy()
            paginated_params[page_param] = page
            
            if limit_param not in paginated_params:
                paginated_params[limit_param] = 100  # Default page size
                
            try:
                response = await self.make_request(endpoint, paginated_params)
                
                # Extract data (adapt based on API response structure)
                if 'data' in response:
                    page_data = response['data']
                elif 'results' in response:
                    page_data = response['results']
                elif 'items' in response:
                    page_data = response['items']
                else:
                    page_data = response
                    
                if not page_data:
                    break  # No more data
                    
                all_results.extend(page_data)
                
                # Check if there are more pages
                if len(page_data) < paginated_params[limit_param]:
                    break  # Last page
                    
                page += 1
                
            except Exception as e:
                self.logger.error(f"Pagination failed at page {page}: {e}")
                break
                
        return all_results
        
    async def stream_data(self, endpoint: ApiEndpoint,
                         params: Optional[Dict[str, Any]] = None,
                         interval: int = 60) -> AsyncGenerator[Dict[str, Any], None]:
        """Stream data from API at regular intervals."""
        while True:
            try:
                data = await self.make_request(endpoint, params, use_cache=False)
                yield data
                await asyncio.sleep(interval)
                
            except Exception as e:
                self.logger.error(f"Streaming error: {e}")
                await asyncio.sleep(interval)
                
    async def batch_request(self, requests: List[Dict[str, Any]],
                           concurrent_limit: int = 5) -> List[Dict[str, Any]]:
        """Execute multiple API requests concurrently."""
        semaphore = asyncio.Semaphore(concurrent_limit)
        
        async def make_single_request(request_data: Dict[str, Any]) -> Dict[str, Any]:
            async with semaphore:
                endpoint = request_data['endpoint']
                params = request_data.get('params')
                data = request_data.get('data')
                
                try:
                    result = await self.make_request(endpoint, params, data)
                    return {'success': True, 'data': result, 'request': request_data}
                except Exception as e:
                    return {'success': False, 'error': str(e), 'request': request_data}
                    
        tasks = [make_single_request(req) for req in requests]
        results = await asyncio.gather(*tasks)
        
        return results
        
    async def webhook_handler(self, webhook_data: Dict[str, Any]) -> Dict[str, Any]:
        """
Handle incoming webhook data."""
        try:
            # Validate webhook (implement signature verification if needed)
            if not self._validate_webhook(webhook_data):
                return {'status': 'error', 'message': 'Invalid webhook'}
                
            # Process webhook data
            processed_data = await self._process_webhook_data(webhook_data)
            
            return {'status': 'success', 'data': processed_data}
            
        except Exception as e:
            self.logger.error(f"Webhook processing error: {e}")
            return {'status': 'error', 'message': str(e)}
            
    def _validate_webhook(self, webhook_data: Dict[str, Any]) -> bool:
        """Validate webhook authenticity."""
        # Implement webhook signature validation
        return True  # Placeholder
        
    async def _process_webhook_data(self, webhook_data: Dict[str, Any]) -> Dict[str, Any]:
        """
Process incoming webhook data."""
        # Implement webhook data processing logic
        return webhook_data
        
    async def get_api_status(self) -> Dict[str, Any]:
        """
Get API health and status information."""
        try:
            # Create a simple health check endpoint
            health_endpoint = ApiEndpoint(
                name='health',
                path='/health',
                method='GET',
                auth_required=False
            )
            
            response = await self.make_request(health_endpoint, use_cache=False)
            
            return {
                'status': 'healthy',
                'response_time': response.get('response_time', 0),
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                'status': 'unhealthy',
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
            
    def get_stats(self) -> Dict[str, Any]:
        """
Get API scraper statistics."""
        return {
            **self.stats,
            'cache_size': len(self.cache),
            'rate_limit_remaining': self._get_remaining_rate_limit(),
            'endpoints_monitored': len(self.request_history),
            'uptime': (datetime.now() - datetime.now()).total_seconds()  # Placeholder
        }
        
    def _get_remaining_rate_limit(self) -> int:
        """
Get remaining rate limit for current minute."""
        now = time.time()
        cutoff = now - 60
        
        total_recent_requests = sum(
            len([req for req in requests if req > cutoff])
            for requests in self.request_history.values()
        )
        
        return max(0, self.config.rate_limit - total_recent_requests)
        
    def clear_cache(self):
        """
Clear response cache."""
        self.cache.clear()
        self.logger.info("API response cache cleared")
        
    async def refresh_auth(self):
        """Refresh authentication credentials."""
        if self.session:
            auth_headers = await self._get_auth_headers()
            self.session.headers.update(auth_headers)
            self.logger.info("Authentication credentials refreshed")
