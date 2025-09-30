#!/usr/bin/env python3
"""
⚡ OPTIMIZED API HANDLER
======================

High-performance API handler with caching, rate limiting, and monitoring.

Author: Backend Senior Expert
"""

import asyncio
import time
import json
import hashlib
from typing import Dict, Any, Optional, Callable
from dataclasses import dataclass
from datetime import datetime, timedelta
import logging

@dataclass
class APIEndpoint:
    """API endpoint configuration"""
    path: str
    method: str
    handler: Callable
    rate_limit: int = 100  # requests per minute
    cache_ttl: int = 300   # seconds
    authentication_required: bool = True
    validation_schema: Optional[Dict] = None

@dataclass
class APIRequest:
    """API request representation"""
    endpoint: str
    method: str
    data: Dict[str, Any]
    user_id: Optional[str] = None
    timestamp: datetime = datetime.now()
    request_id: str = ""

class OptimizedAPIHandler:
    """High-performance API handler"""
    
    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.endpoints: Dict[str, APIEndpoint] = {}
        self.cache: Dict[str, Dict[str, Any]] = {}
        self.rate_limits: Dict[str, List[datetime]] = {}
        self.performance_metrics = {
            "total_requests": 0,
            "successful_requests": 0,
            "cached_responses": 0,
            "average_response_time": 0.0,
            "rate_limited_requests": 0
        }
    
    def register_endpoint(self, endpoint: APIEndpoint) -> bool:
        """Register an API endpoint"""
        try:
            self.endpoints[f"{endpoint.method}:{endpoint.path}"] = endpoint
            self.logger.info(f"Registered endpoint: {endpoint.method} {endpoint.path}")
            return True
        except Exception as e:
            self.logger.error(f"Failed to register endpoint: {e}")
            return False
    
    async def handle_request(self, request: APIRequest) -> Dict[str, Any]:
        """Handle an API request with optimization"""
        start_time = time.time()
        request.request_id = self._generate_request_id(request)
        
        try:
            # Find endpoint
            endpoint_key = f"{request.method}:{request.endpoint}"
            endpoint = self.endpoints.get(endpoint_key)
            
            if not endpoint:
                return self._error_response("Endpoint not found", 404)
            
            # Check rate limiting
            if not self._check_rate_limit(request, endpoint):
                self.performance_metrics["rate_limited_requests"] += 1
                return self._error_response("Rate limit exceeded", 429)
            
            # Check cache
            cache_key = self._generate_cache_key(request)
            cached_response = self._get_cached_response(cache_key, endpoint.cache_ttl)
            
            if cached_response:
                self.performance_metrics["cached_responses"] += 1
                response = cached_response
            else:
                # Process request
                response = await self._process_request(request, endpoint)
                
                # Cache successful responses
                if response.get("status") == "success":
                    self._cache_response(cache_key, response)
            
            # Update metrics
            processing_time = time.time() - start_time
            self._update_metrics(processing_time, True)
            
            return response
            
        except Exception as e:
            processing_time = time.time() - start_time
            self._update_metrics(processing_time, False)
            
            self.logger.error(f"Request {request.request_id} failed: {e}")
            return self._error_response("Internal server error", 500)
    
    def _check_rate_limit(self, request: APIRequest, endpoint: APIEndpoint) -> bool:
        """Check if request is within rate limits"""
        user_key = request.user_id or request.request_id
        now = datetime.now()
        
        if user_key not in self.rate_limits:
            self.rate_limits[user_key] = []
        
        # Remove old requests (older than 1 minute)
        cutoff_time = now - timedelta(minutes=1)
        self.rate_limits[user_key] = [
            req_time for req_time in self.rate_limits[user_key]
            if req_time > cutoff_time
        ]
        
        # Check if under limit
        if len(self.rate_limits[user_key]) >= endpoint.rate_limit:
            return False
        
        # Add current request
        self.rate_limits[user_key].append(now)
        return True
    
    def _generate_cache_key(self, request: APIRequest) -> str:
        """Generate cache key for request"""
        key_data = f"{request.endpoint}:{request.method}:{json.dumps(request.data, sort_keys=True)}"
        return hashlib.md5(key_data.encode()).hexdigest()
    
    def _get_cached_response(self, cache_key: str, ttl: int) -> Optional[Dict[str, Any]]:
        """Get cached response if still valid"""
        cached = self.cache.get(cache_key)
        if not cached:
            return None
        
        if time.time() - cached["timestamp"] > ttl:
            del self.cache[cache_key]
            return None
        
        return cached["response"]
    
    def _cache_response(self, cache_key: str, response: Dict[str, Any]) -> None:
        """Cache a response"""
        self.cache[cache_key] = {
            "response": response,
            "timestamp": time.time()
        }
        
        # Limit cache size
        if len(self.cache) > 1000:
            # Remove oldest entries
            oldest_keys = sorted(
                self.cache.keys(),
                key=lambda k: self.cache[k]["timestamp"]
            )[:100]
            for key in oldest_keys:
                del self.cache[key]
    
    async def _process_request(self, request: APIRequest, endpoint: APIEndpoint) -> Dict[str, Any]:
        """Process the actual request"""
        try:
            # Validate request data if schema provided
            if endpoint.validation_schema:
                validation_result = self._validate_request(request.data, endpoint.validation_schema)
                if not validation_result["valid"]:
                    return self._error_response(f"Validation error: {validation_result['errors']}", 400)
            
            # Call the endpoint handler
            result = await endpoint.handler(request.data)
            
            return {
                "status": "success",
                "data": result,
                "request_id": request.request_id,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            return self._error_response(f"Processing error: {str(e)}", 500)
    
    def _validate_request(self, data: Dict[str, Any], schema: Dict) -> Dict[str, Any]:
        """Validate request data against schema"""
        # Simplified validation - in real scenario would use jsonschema or pydantic
        errors = []
        
        for field, requirements in schema.items():
            if requirements.get("required", False) and field not in data:
                errors.append(f"Missing required field: {field}")
            
            if field in data:
                field_type = requirements.get("type")
                if field_type and not isinstance(data[field], field_type):
                    errors.append(f"Invalid type for {field}: expected {field_type.__name__}")
        
        return {
            "valid": len(errors) == 0,
            "errors": errors
        }
    
    def _error_response(self, message: str, status_code: int) -> Dict[str, Any]:
        """Generate error response"""
        return {
            "status": "error",
            "message": message,
            "status_code": status_code,
            "timestamp": datetime.now().isoformat()
        }
    
    def _generate_request_id(self, request: APIRequest) -> str:
        """Generate unique request ID"""
        id_data = f"{request.endpoint}:{request.timestamp}:{id(request)}"
        return hashlib.sha256(id_data.encode()).hexdigest()[:16]
    
    def _update_metrics(self, processing_time: float, success: bool) -> None:
        """Update performance metrics"""
        self.performance_metrics["total_requests"] += 1
        
        if success:
            self.performance_metrics["successful_requests"] += 1
        
        # Update average response time
        total_requests = self.performance_metrics["total_requests"]
        current_avg = self.performance_metrics["average_response_time"]
        new_avg = ((current_avg * (total_requests - 1)) + processing_time) / total_requests
        self.performance_metrics["average_response_time"] = new_avg
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get API performance metrics"""
        success_rate = (
            self.performance_metrics["successful_requests"] / 
            max(self.performance_metrics["total_requests"], 1)
        )
        
        cache_hit_rate = (
            self.performance_metrics["cached_responses"] /
            max(self.performance_metrics["total_requests"], 1)
        )
        
        return {
            **self.performance_metrics,
            "success_rate": success_rate,
            "cache_hit_rate": cache_hit_rate,
            "active_endpoints": len(self.endpoints),
            "cache_size": len(self.cache)
        }

# Global API handler instance
api_handler = OptimizedAPIHandler()
