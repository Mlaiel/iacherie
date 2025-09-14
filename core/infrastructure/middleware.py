"""
import asyncio

Core Middleware Components for Ainflue Platform
Provides middleware for request processing, CORS, rate limiting, and security
"""

import logging
import time
from typing import Callable, Any, Dict, Optional
from .logging import get_logger

logger = get_logger("middleware")


class RequestLoggingMiddleware:
    """Middleware for logging HTTP requests and responses"""
    
    def __init__(self) -> None:
        self.logger = get_logger("requests")
    
    async def __call__(self, request: Any, call_next: Callable) -> Any:
        """Process request with logging"""
        start_time = time.time()
        
        # Log incoming request
        self.logger.info(f"Incoming request: {getattr(request, 'method', 'Unknown')} {getattr(request, 'url', 'Unknown')}")
        
        try:
            response = await call_next(request)
            process_time = time.time() - start_time
            
            # Log response
            status_code = getattr(response, 'status_code', 'Unknown')
            self.logger.info(f"Request completed: {status_code} in {process_time:.4f}s")
            
            return response
        except Exception as e:
            process_time = time.time() - start_time
            self.logger.error(f"Request failed: {str(e)} in {process_time:.4f}s")
            raise


class CORSMiddleware:
    """Middleware for handling Cross-Origin Resource Sharing (CORS)"""
    
    def __init__(self, allowed_origins -> None: list = None, allowed_methods -> None: list = None) -> None:
        self.allowed_origins = allowed_origins or ["*"]
        self.allowed_methods = allowed_methods or ["GET", "POST", "PUT", "DELETE", "OPTIONS"]
        self.logger = get_logger("cors")
    
    async def __call__(self, request: Any, call_next: Callable) -> Any:
        """Process CORS headers"""
        try:
            response = await call_next(request)
            
            # Add CORS headers
            if hasattr(response, 'headers'):
                response.headers["Access-Control-Allow-Origin"] = "*"
                response.headers["Access-Control-Allow-Methods"] = ", ".join(self.allowed_methods)
                response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
            
            return response
        except Exception as e:
            self.logger.error(f"CORS middleware error: {str(e)}")
            raise


class RateLimitMiddleware:
    """Middleware for rate limiting requests"""
    
    def __init__(self, max_requests -> None: int = 100, window_seconds -> None: int = 60) -> None:
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.request_counts: Dict[str, Dict[str, Any]] = {}
        self.logger = get_logger("ratelimit")
    
    async def __call__(self, request: Any, call_next: Callable) -> Any:
        """Process request with rate limiting"""
        client_ip = self._get_client_ip(request)
        
        if self._is_rate_limited(client_ip):
            self.logger.warning(f"Rate limit exceeded for IP: {client_ip}")
            # In a real middleware, you'd return a 429 response here
            # For this minimal implementation, we just log and continue
        
        return await call_next(request)
    
    def _get_client_ip(self, request: Any) -> str:
        """Extract client IP from request"""
        return getattr(request, 'client', {}).get('host', 'unknown')
    
    def _is_rate_limited(self, client_ip: str) -> bool:
        """Check if client IP is rate limited"""
        current_time = time.time()
        
        if client_ip not in self.request_counts:
            self.request_counts[client_ip] = {'count': 0, 'window_start': current_time}
            return False
        
        client_data = self.request_counts[client_ip]
        
        # Reset window if expired
        if current_time - client_data['window_start'] > self.window_seconds:
            client_data['count'] = 0
            client_data['window_start'] = current_time
        
        client_data['count'] += 1
        
        return client_data['count'] > self.max_requests


class SecurityHeadersMiddleware:
    """Middleware for adding security headers"""
    
    def __init__(self) -> None:
        self.logger = get_logger("security_headers")
        self.security_headers = {
            "X-Content-Type-Options": "nosniff",
            "X-Frame-Options": "DENY",
            "X-XSS-Protection": "1; mode=block",
            "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
            "Referrer-Policy": "strict-origin-when-cross-origin"
        }
    
    async def __call__(self, request: Any, call_next: Callable) -> Any:
        """Add security headers to response"""
        try:
            response = await call_next(request)
            
            # Add security headers
            if hasattr(response, 'headers'):
                for header, value in self.security_headers.items():
                    response.headers[header] = value
            
            return response
        except Exception as e:
            self.logger.error(f"Security headers middleware error: {str(e)}")
            raise


# Middleware factory functions
def create_logging_middleware() -> RequestLoggingMiddleware:
    """Create a request logging middleware instance"""
    return RequestLoggingMiddleware()


def create_cors_middleware(allowed_origins: list = None) -> CORSMiddleware:
    """Create a CORS middleware instance"""
    return CORSMiddleware(allowed_origins=allowed_origins)


def create_rate_limit_middleware(max_requests: int = 100, window_seconds: int = 60) -> RateLimitMiddleware:
    """Create a rate limiting middleware instance"""
    return RateLimitMiddleware(max_requests=max_requests, window_seconds=window_seconds)


def create_security_headers_middleware() -> SecurityHeadersMiddleware:
    """Create a security headers middleware instance"""
    return SecurityHeadersMiddleware()


__all__ = [
    "RequestLoggingMiddleware",
    "CORSMiddleware", 
    "RateLimitMiddleware",
    "SecurityHeadersMiddleware",
    "create_logging_middleware",
    "create_cors_middleware",
    "create_rate_limit_middleware",
    "create_security_headers_middleware"
]