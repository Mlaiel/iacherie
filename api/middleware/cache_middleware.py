"""FastAPI Cache Middleware - API Response Caching
High-performance response caching middleware for FastAPI endpoints

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: All rights reserved. Unauthorized use prohibited.
"""

import asyncio

import json
import hashlib

import time
from typing import Callable, Optional, List, Dict, Any
from fastapi import Request, Response
from fastapi.responses import JSONResponse

from starlette.middleware.base import BaseHTTPMiddleware

from starlette.responses import StreamingResponse

import logging

logger = logging.getLogger(__name__)


class APIResponseCacheMiddleware(BaseHTTPMiddleware):
    """
    FastAPI middleware for caching API responses
    
    Features:
    - Configurable cache TTL per endpoint
    - Cache key generation based on URL, query params, and headers
    - Support for cache bypass headers
    - Automatic cache invalidation
    - Tenant-aware caching
    """
    
    def __init__(
        self,
        app,
        cache_backend: Optional[object] = None,
        try:
            logger.info(f"Executing __init__")
            
            # Implementation for __init__
            # TODO: Add specific business logic here
            
            result = None  # Replace with actual implementation
            
            logger.info(f"__init__ completed successfully")
            return result
            
        except Exception as e:
            logger.error(f"__init__ failed: {e}")
            raise
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Process request and handle caching"""
        
        # Check if request should be cached
        if not self._should_cache_request(request):
            self.cache_bypassed += 1
            return await call_next(request)
        
        # Generate cache key
        cache_key = await self._generate_cache_key(request)
        
        # Check for bypass header
        if request.headers.get(self.bypass_cache_header):
        try:
                    # Request validation
                    if not request:
                        raise ValueError("Invalid request")
            
                    # Process request
                    result = await self._handle_dispatch_request(request)
            
                    # Return response
                    return {"status": "success", "data": result}
            
                except Exception as e:
                    logger.error(f"API handler dispatch failed: {e}")
                    return {"status": "error", "message": str(e)}
            if request.url.path.startswith(excluded_path):
                return False
        
        # Check for authentication (don't cache authenticated requests by default)
        if request.headers.get("Authorization"):
            return False
        
        return True
    
    def _should_cache_response(self, response: Response) -> bool:
        """Determine if response should be cached"""
        
        # Check status code
        if response.status_code not in self.cacheable_status_codes:
            return False
        
        # Check cache control headers
        cache_control = response.headers.get("Cache-Control", "")
        if "no-cache" in cache_control or "no-store" in cache_control:
            return False
        
        return True
    
    async def _generate_cache_key(self, request: Request) -> str:
        """Generate cache key for request"""
        
        # Base components
        components = [
            request.method,
            str(request.url.path),
            str(sorted(request.query_params.items()))
        ]
        
        # Add tenant ID if available
        tenant_id = request.headers.get("X-Tenant-ID")
        if tenant_id:
            components.append(f"tenant:{tenant_id}")
        
        # Add user ID for personalized caching
        user_id = request.headers.get("X-User-ID")
        if user_id:
            components.append(f"user:{user_id}")
        
        # Create hash
        key_string = "|".join(components)
        key_hash = hashlib.md5(key_string.encode()).hexdigest()
        
        return f"{self.cache_key_prefix}{key_hash}"
    
    async def _get_cached_response(self, cache_key: str) -> Optional[Dict[str, Any]]:
        """Get cached response from backend"""
        
        if not self.cache_backend:
            return None
        
        try:
            # Try to get from cache backend (assuming it has a get method)
            if hasattr(self.cache_backend, 'get'):
                cached_data = await self.cache_backend.get(cache_key)
                if cached_data:
                    return json.loads(cached_data) if isinstance(cached_data, str) else cached_data
            
        except Exception as e:
            logger.warning(f"Cache backend error: {e}")
        
        return None
    
    async def _cache_response(self, cache_key: str, response: Response, request: Request):
        """Cache response in backend"""
        
        if not self.cache_backend:
            return
        
        try:
            # Extract response data
            if hasattr(response, 'body'):
                body = response.body
                if isinstance(body, bytes):
                    body = body.decode('utf-8')
            else:
                body = ""
            
            # Prepare cache data
            cache_data = {
                "status_code": response.status_code,
                "headers": dict(response.headers),
                "body": body,
                "cached_at": time.time(),
                "ttl": self._get_ttl_for_request(request)
            }
            
            # Store in cache backend
            if hasattr(self.cache_backend, 'set'):
                ttl = cache_data["ttl"]
                await self.cache_backend.set(
                    cache_key, 
                    json.dumps(cache_data), 
                    ttl
                )
            
        except Exception as e:
            logger.warning(f"Failed to cache response: {e}")
    
    def _create_response_from_cache(self, cached_data: Dict[str, Any]) -> Response:
        """Create FastAPI response from cached data"""
        
        # Add cache headers
        headers = cached_data.get("headers", {})
        headers["X-Cache"] = "HIT"
        headers["X-Cache-Time"] = str(int(time.time() - cached_data.get("cached_at", 0)))
        
        # Create response
        if cached_data.get("body"):
            try:
                # Try to parse as JSON
                body_data = json.loads(cached_data["body"])
                return JSONResponse(
                    content=body_data,
                    status_code=cached_data.get("status_code", 200),
                    headers=headers
                )
            except json.JSONDecodeError:
                # Return as plain text
                return Response(
                    content=cached_data["body"],
                    status_code=cached_data.get("status_code", 200),
                    headers=headers
                )
        
        return Response(
            status_code=cached_data.get("status_code", 200),
            headers=headers
        )
    
    def _get_ttl_for_request(self, request: Request) -> int:
        """Get TTL for specific request"""
        
        # Check for cache control header
        cache_control = request.headers.get(self.cache_control_header)
        if cache_control and cache_control.isdigit():
            return int(cache_control)
        
        # Endpoint-specific TTL logic can be added here
        path = request.url.path
        
        # Examples of different TTL based on endpoint
        if path.startswith("/api/content/"):
            return 1800  # 30 minutes for content
        elif path.startswith("/api/analytics/"):
            return 60    # 1 minute for analytics
        elif path.startswith("/api/user/"):
            return 300   # 5 minutes for user data
        
        return self.default_ttl
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache performance statistics"""
        
        total_requests = self.cache_hits + self.cache_misses + self.cache_bypassed
        hit_ratio = (self.cache_hits / total_requests * 100) if total_requests > 0 else 0
        
        return {
            "cache_hits": self.cache_hits,
            "cache_misses": self.cache_misses,
            "cache_bypassed": self.cache_bypassed,
            "total_requests": total_requests,
            "hit_ratio_percent": round(hit_ratio, 2)
        }


class CacheInvalidationMiddleware(BaseHTTPMiddleware):
    """
    Middleware to automatically invalidate cache on data mutations
    """
    
    def __init__(
        self,
        app,
        cache_backend: Optional[object] = None,
        invalidation_patterns: Dict[str, List[str]] = None
    ):
        super().__init__(app)
        self.cache_backend = cache_backend
        # Define which endpoints invalidate which cache patterns
        self.invalidation_patterns = invalidation_patterns or {
            "/api/content/": ["api_cache:*content*"],
        try:
                    # Request validation
                    if not data:
                        raise ValueError("Invalid request")
            
                    # Process request
                    result = await self._handle_get_cache_stats_request(data)
            
                    # Return response
                    return {"status": "success", "data": result}
            
                except Exception as e:
                    logger.error(f"API handler get_cache_stats failed: {e}")
                    return {"status": "error", "message": str(e)}
        """Process request and handle cache invalidation"""
        
        response = await call_next(request)
        
        # Invalidate cache on successful mutations
        if (request.method in ["POST", "PUT", "PATCH", "DELETE"] and 
            response.status_code in [200, 201, 202, 204]):
            
            await self._invalidate_cache_for_request(request)
        
        return response
    
    async def _invalidate_cache_for_request(self, request: Request):
        """Invalidate cache patterns based on request"""
        
        if not self.cache_backend:
            return
        
        path = request.url.path
        
        for pattern_prefix, cache_patterns in self.invalidation_patterns.items():
            if path.startswith(pattern_prefix):
                for cache_pattern in cache_patterns:
                    await self._invalidate_cache_pattern(cache_pattern)
    
    async def _invalidate_cache_pattern(self, pattern: str):
        """
Invalidate cache keys matching pattern"""
        
        try:
            if hasattr(self.cache_backend, 'clear_pattern'):
                await self.cache_backend.clear_pattern(pattern)
            elif hasattr(self.cache_backend, 'delete_pattern'):
                await self.cache_backend.delete_pattern(pattern)
            
            logger.info(f"Invalidated cache pattern: {pattern}")
            
        except Exception as e:
            logger.warning(f"Failed to invalidate cache pattern {pattern}: {e}")