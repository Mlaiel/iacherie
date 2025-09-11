"""Synchronous HTTP Client for Ainflue SDK

Enterprise-grade synchronous client with multi-expert design:
- Backend Senior: Thread-safe synchronous architecture
- DevOps: Connection pooling and session management  
- Sécurité: Security hardening and certificate validation
- Lead Dev IA: Intelligent retry patterns and error handling

Author: Fahed Mlaiel (mlaiel@live.de)
"""

import json
import logging
import threading
import time
from typing import Dict, Any, Optional, List, Union, BinaryIO
from datetime import datetime, timedelta
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import ssl
import certifi

from .exceptions import (
    APIError, NetworkError, TimeoutError, RateLimitError,
    AuthenticationError, ValidationError, AinflueSdkException,
    handle_api_response_error, is_retryable_error
)


class SessionManager:
    """Thread-safe session manager for connection pooling"""
    
    def __init__(self, max_connections: int = 10):
        self._sessions = {}
        self._lock = threading.Lock()
        self.max_connections = max_connections
    
    def get_session(self, thread_id: str) -> requests.Session:
        """Get or create session for current thread"""
        with self._lock:
            if thread_id not in self._sessions:
                session = requests.Session()
                
                # Configure connection pool
                adapter = HTTPAdapter(
                    pool_connections=self.max_connections,
                    pool_maxsize=self.max_connections,
                    max_retries=0  # We handle retries manually
                )
                
                session.mount('http://', adapter)
                session.mount('https://', adapter)
                
                self._sessions[thread_id] = session
            
            return self._sessions[thread_id]
    
    def close_all(self):
        """Close all sessions"""
        with self._lock:
            for session in self._sessions.values():
                session.close()
            self._sessions.clear()


class SyncMetrics:
    """Thread-safe metrics collection"""
    
    def __init__(self):
        self._lock = threading.Lock()
        self.total_requests = 0
        self.successful_requests = 0
        self.failed_requests = 0
        self.total_response_time = 0.0
        self.start_time = datetime.utcnow()
    
    def record_request(self, response_time: float, success: bool):
        """Record request metrics (thread-safe)"""
        with self._lock:
            self.total_requests += 1
            self.total_response_time += response_time
            
            if success:
                self.successful_requests += 1
            else:
                self.failed_requests += 1
    
    def get_stats(self) -> Dict[str, Any]:
        """Get metrics statistics (thread-safe)"""
        with self._lock:
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


class RateLimiter:
    """Thread-safe rate limiter"""
    
    def __init__(self, max_requests: int = 60, time_window: int = 60):
        self.max_requests = max_requests
        self.time_window = time_window
        self._requests = []
        self._lock = threading.Lock()
    
    def wait_if_needed(self):
        """Wait if rate limit would be exceeded"""
        with self._lock:
            now = time.time()
            
            # Remove old requests outside time window
            self._requests = [req_time for req_time in self._requests if now - req_time < self.time_window]
            
            # Check if we need to wait
            if len(self._requests) >= self.max_requests:
                sleep_time = self.time_window - (now - self._requests[0])
                if sleep_time > 0:
                    time.sleep(sleep_time)
                    # Re-clean the list after waiting
                    now = time.time()
                    self._requests = [req_time for req_time in self._requests if now - req_time < self.time_window]
            
            # Record this request
            self._requests.append(now)


class SyncAinflueClient:
    """High-performance synchronous HTTP client for Ainflue API
    
    Features:
    - Thread-safe operation
    - Connection pooling
    - Intelligent retry with exponential backoff
    - Rate limiting
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
        max_connections: int = 10,
        verify_ssl: bool = True,
        custom_headers: Optional[Dict[str, str]] = None,
        rate_limit_requests: int = 60,
        rate_limit_window: int = 60
    ):
        self.base_url = base_url.rstrip('/')
        self.api_key = api_key
        self.timeout = timeout
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.verify_ssl = verify_ssl
        self.custom_headers = custom_headers or {}
        
        # Initialize components
        self.logger = logging.getLogger(__name__)
        self.session_manager = SessionManager(max_connections)
        self.metrics = SyncMetrics()
        self.rate_limiter = RateLimiter(rate_limit_requests, rate_limit_window)
        
        # SSL configuration (Sécurité expertise)
        if verify_ssl:
            self.ssl_context = self._create_ssl_context()
        else:
            self.ssl_context = None
    
    def _create_ssl_context(self) -> ssl.SSLContext:
        """Create secure SSL context"""
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
            'X-Client-Type': 'sync-python',
        }
        
        if self.api_key:
            headers['Authorization'] = f'Bearer {self.api_key}'
        
        # Add custom headers
        headers.update(self.custom_headers)
        
        return headers
    
    def _get_session(self) -> requests.Session:
        """Get session for current thread"""
        thread_id = str(threading.current_thread().ident)
        session = self.session_manager.get_session(thread_id)
        
        # Configure session if not already done
        if not hasattr(session, '_ainflue_configured'):
            session.headers.update(self._get_default_headers())
            session.verify = self.ssl_context or self.verify_ssl
            session._ainflue_configured = True
        
        return session
    
    def _make_request_with_retry(
        self,
        method: str,
        endpoint: str,
        data: Optional[Dict] = None,
        params: Optional[Dict] = None,
        headers: Optional[Dict] = None,
        files: Optional[Dict] = None,
        stream: bool = False
    ) -> Union[Dict[str, Any], requests.Response]:
        """Make HTTP request with retry logic"""
        
        # Rate limiting
        self.rate_limiter.wait_if_needed()
        
        session = self._get_session()
        url = f"{self.base_url}{endpoint}"
        
        # Merge headers
        final_headers = self._get_default_headers()
        if headers:
            final_headers.update(headers)
        
        last_exception = None
        start_time = time.time()
        
        for attempt in range(self.max_retries + 1):
            try:
                self.logger.debug(f"Making {method} request to {endpoint} (attempt {attempt + 1})")
                
                # Prepare request arguments
                request_kwargs = {
                    'timeout': self.timeout,
                    'headers': final_headers,
                    'stream': stream
                }
                
                if params:
                    request_kwargs['params'] = params
                
                if files:
                    # For file uploads, don't set Content-Type header
                    request_kwargs['files'] = files
                    if data:
                        request_kwargs['data'] = data
                    # Remove Content-Type for multipart
                    if 'Content-Type' in request_kwargs['headers']:
                        del request_kwargs['headers']['Content-Type']
                elif data:
                    request_kwargs['json'] = data
                
                # Make the request
                response = session.request(method, url, **request_kwargs)
                
                if stream:
                    return response
                else:
                    return self._handle_response(response)
                
            except Exception as e:
                last_exception = e
                
                # Convert requests exceptions to SDK exceptions
                if isinstance(e, requests.exceptions.Timeout):
                    last_exception = TimeoutError(f"Request timeout after {self.timeout}s")
                elif isinstance(e, requests.exceptions.ConnectionError):
                    last_exception = NetworkError(f"Connection error: {str(e)}")
                elif isinstance(e, requests.exceptions.RequestException):
                    last_exception = NetworkError(f"Request error: {str(e)}")
                
                # Check if error is retryable
                if not is_retryable_error(last_exception) or attempt == self.max_retries:
                    break
                
                # Calculate delay with exponential backoff
                delay = self.retry_delay * (2 ** attempt)
                
                self.logger.warning(
                    f"Request failed (attempt {attempt + 1}), retrying in {delay:.2f}s: {str(e)}"
                )
                
                time.sleep(delay)
        
        # Record metrics
        response_time = time.time() - start_time
        self.metrics.record_request(response_time, False)
        
        # Raise the last exception
        if isinstance(last_exception, AinflueSdkException):
            raise last_exception
        else:
            raise NetworkError(f"Request failed after {self.max_retries + 1} attempts") from last_exception
    
    def _handle_response(self, response: requests.Response) -> Dict[str, Any]:
        """Handle HTTP response"""
        start_time = time.time()
        
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
            response_time = time.time() - start_time
            self.metrics.record_request(response_time, True)
            
            return result
            
        except AinflueSdkException:
            # Re-raise SDK exceptions
            response_time = time.time() - start_time
            self.metrics.record_request(response_time, False)
            raise
        finally:
            response.close()
    
    def _handle_streaming_response(self, response: requests.Response):
        """Handle streaming response"""
        try:
            if response.status_code >= 400:
                error_text = response.text
                try:
                    error_data = json.loads(error_text)
                except:
                    error_data = {'message': error_text}
                
                exception = handle_api_response_error(error_data, response.status_code)
                raise exception
            
            return response
            
        except AinflueSdkException:
            raise
        except Exception as e:
            raise NetworkError(f"Streaming error: {str(e)}") from e
    
    # Public API methods
    def get(
        self,
        endpoint: str,
        params: Optional[Dict] = None,
        headers: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """Make GET request"""
        return self._make_request_with_retry('GET', endpoint, params=params, headers=headers)
    
    def post(
        self,
        endpoint: str,
        data: Optional[Dict] = None,
        params: Optional[Dict] = None,
        headers: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """Make POST request"""
        return self._make_request_with_retry('POST', endpoint, data=data, params=params, headers=headers)
    
    def put(
        self,
        endpoint: str,
        data: Optional[Dict] = None,
        params: Optional[Dict] = None,
        headers: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """Make PUT request"""
        return self._make_request_with_retry('PUT', endpoint, data=data, params=params, headers=headers)
    
    def delete(
        self,
        endpoint: str,
        params: Optional[Dict] = None,
        headers: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """Make DELETE request"""
        return self._make_request_with_retry('DELETE', endpoint, params=params, headers=headers)
    
    def patch(
        self,
        endpoint: str,
        data: Optional[Dict] = None,
        params: Optional[Dict] = None,
        headers: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """Make PATCH request"""
        return self._make_request_with_retry('PATCH', endpoint, data=data, params=params, headers=headers)
    
    def stream(
        self,
        method: str,
        endpoint: str,
        data: Optional[Dict] = None,
        params: Optional[Dict] = None,
        headers: Optional[Dict] = None
    ) -> requests.Response:
        """Make streaming request"""
        response = self._make_request_with_retry(
            method, endpoint, data=data, params=params, headers=headers, stream=True
        )
        return self._handle_streaming_response(response)
    
    def upload_file(
        self,
        endpoint: str,
        file_path: str = None,
        file_obj: BinaryIO = None,
        field_name: str = "file",
        additional_data: Optional[Dict] = None,
        headers: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """Upload file with multipart form data"""
        
        if file_path and file_obj:
            raise ValidationError("Provide either file_path or file_obj, not both")
        
        if not file_path and not file_obj:
            raise ValidationError("Must provide either file_path or file_obj")
        
        files = {}
        close_file = False
        
        try:
            if file_path:
                files[field_name] = open(file_path, 'rb')
                close_file = True
            else:
                files[field_name] = file_obj
            
            return self._make_request_with_retry(
                'POST',
                endpoint,
                data=additional_data,
                headers=headers,
                files=files
            )
        
        finally:
            # Close file handle if we opened it
            if close_file and field_name in files:
                files[field_name].close()
    
    def download_file(
        self,
        endpoint: str,
        file_path: str,
        params: Optional[Dict] = None,
        headers: Optional[Dict] = None,
        chunk_size: int = 8192
    ) -> Dict[str, Any]:
        """Download file from endpoint"""
        
        response = self.stream('GET', endpoint, params=params, headers=headers)
        
        try:
            with open(file_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=chunk_size):
                    if chunk:
                        f.write(chunk)
            
            return {
                'success': True,
                'file_path': file_path,
                'size': response.headers.get('Content-Length'),
                'content_type': response.headers.get('Content-Type')
            }
        
        finally:
            response.close()
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get client metrics"""
        return {
            'client_metrics': self.metrics.get_stats(),
            'active_sessions': len(self.session_manager._sessions)
        }
    
    def health_check(self) -> Dict[str, Any]:
        """Perform health check"""
        try:
            result = self.get('/health')
            result['client_status'] = 'healthy'
            result['metrics'] = self.get_metrics()
            return result
        except Exception as e:
            return {
                'client_status': 'unhealthy',
                'error': str(e),
                'metrics': self.get_metrics()
            }
    
    def close(self):
        """Close all sessions and cleanup resources"""
        self.session_manager.close_all()
    
    def __enter__(self):
        """Context manager entry"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.close()


# Export the client
__all__ = ['SyncAinflueClient', 'SessionManager', 'SyncMetrics', 'RateLimiter']