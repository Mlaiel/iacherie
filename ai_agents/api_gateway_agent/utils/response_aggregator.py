"""Response Aggregator - Multi-Service Response Processing

Advanced response aggregation, transformation, and optimization for distributed
microservices responses with intelligent caching and streaming capabilities.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️  CRITICAL LEGAL NOTICE:
This code and architectural design are the exclusive intellectual property of Fahed Mlaiel.
Unauthorized use, copying, distribution, or commercialization is strictly prohibited.
"""

import asyncio
import logging
import json
import gzip
from typing import Dict, List, Optional, Any, Union, Callable
from datetime import datetime, timedelta
from dataclasses import dataclass
import time

import aiohttp
from fastapi import Response
from fastapi.responses import StreamingResponse, JSONResponse

logger = logging.getLogger(__name__)


@dataclass
class ServiceResponse:
    """
Individual service response data"""
    service_name: str
    status_code: int
    headers: Dict[str, str]
    content: bytes
    content_type: str
    response_time: float
    error: Optional[str] = None


@dataclass
class AggregationRule:
    """
Response aggregation configuration"""
    pattern: str
    services: List[str]
    aggregation_type: str  # merge, concat, transform
    timeout: float = 30.0
    required_services: Optional[List[str]] = None
    cache_ttl: Optional[int] = None


class ResponseAggregator:
    """
    Enterprise Response Aggregator
    
    Features:
    - Multi-service response aggregation
    - Intelligent response merging
    - Response transformation
    - Streaming aggregation
    - Response caching
    - Error handling and fallbacks
    - Performance optimization
    """
    
    def __init__(self, redis_url: Optional[str] = None):
        """
Initialize response aggregator"""
        self.redis_url = redis_url
        self.redis = None
        
        # Aggregation rules
        self.aggregation_rules: Dict[str, AggregationRule] = {}
        
        # Response transformers
        self.transformers: Dict[str, Callable] = {
            "merge": self._merge_responses,
            "concat": self._concat_responses,
            "transform": self._transform_responses,
            "collect": self._collect_responses
        }
        
        # Cache for aggregated responses
        self.response_cache: Dict[str, Dict[str, Any]] = {}
        self.cache_ttl = 300  # 5 minutes default
        
        logger.info("Response aggregator initialized")
    
    async def aggregate_responses(
        self,
        request_path: str,
        service_responses: Dict[str, ServiceResponse],
        aggregation_type: str = "merge"
    ) -> Response:
        """
        Aggregate multiple service responses
        
        Args:
            request_path: Original request path
            service_responses: Dictionary of service responses
            aggregation_type: Type of aggregation to perform
            
        Returns:
            Aggregated FastAPI Response
        """
        try:
            # Check for cached response
            cache_key = self._generate_cache_key(request_path, service_responses.keys())
            cached_response = await self._get_cached_response(cache_key)
            
            if cached_response:
                return self._create_response_from_cache(cached_response)
            
            # Get aggregation rule
            rule = self._get_aggregation_rule(request_path)
            if rule:
                aggregation_type = rule.aggregation_type
            
            # Perform aggregation
            transformer = self.transformers.get(aggregation_type, self._merge_responses)
            aggregated_data = await transformer(service_responses, rule)
            
            # Create response
            response = self._create_aggregated_response(aggregated_data, service_responses)
            
            # Cache response if configured
            if rule and rule.cache_ttl:
                await self._cache_response(cache_key, response, rule.cache_ttl)
            
            return response
            
        except Exception as e:
            logger.error(f"Response aggregation error: {e}")
            return self._create_error_response(str(e), 500)
    
    async def _merge_responses(
        self, 
        service_responses: Dict[str, ServiceResponse],
        rule: Optional[AggregationRule] = None
    ) -> Dict[str, Any]:
        """Merge responses into single JSON object"""
        try:
            merged_data = {
                "data": {},
                "metadata": {
                    "aggregated_at": datetime.utcnow().isoformat(),
                    "services": list(service_responses.keys()),
                    "total_response_time": 0
                },
                "errors": []
            }
            
            total_response_time = 0
            
            for service_name, response in service_responses.items():
                total_response_time += response.response_time
                
                if response.error:
                    merged_data["errors"].append({
                        "service": service_name,
                        "error": response.error,
                        "status_code": response.status_code
                    })
                    continue
                
                # Parse response content
                try:
                    if response.content_type.startswith("application/json"):
                        service_data = json.loads(response.content.decode())
                        merged_data["data"][service_name] = service_data
                    else:
                        # Handle non-JSON responses
                        merged_data["data"][service_name] = {
                            "content": response.content.decode(),
                            "content_type": response.content_type
                        }
                except json.JSONDecodeError:
                    merged_data["data"][service_name] = {
                        "content": response.content.decode(),
                        "content_type": response.content_type
                    }
            
            merged_data["metadata"]["total_response_time"] = round(total_response_time, 3)
            
            return merged_data
            
        except Exception as e:
            logger.error(f"Response merging error: {e}")
            raise
    
    async def _concat_responses(
        self, 
        service_responses: Dict[str, ServiceResponse],
        rule: Optional[AggregationRule] = None
    ) -> Dict[str, Any]:
        """Concatenate responses into single array"""
        try:
            concatenated_data = {
                "items": [],
                "metadata": {
                    "aggregated_at": datetime.utcnow().isoformat(),
                    "services": list(service_responses.keys()),
                    "total_items": 0,
                    "total_response_time": 0
                },
                "errors": []
            }
            
            total_response_time = 0
            
            for service_name, response in service_responses.items():
                total_response_time += response.response_time
                
                if response.error:
                    concatenated_data["errors"].append({
                        "service": service_name,
                        "error": response.error,
                        "status_code": response.status_code
                    })
                    continue
                
                # Parse and concatenate response content
                try:
                    if response.content_type.startswith("application/json"):
                        service_data = json.loads(response.content.decode())
                        
                        # Handle different response formats
                        if isinstance(service_data, list):
                            concatenated_data["items"].extend(service_data)
                        elif isinstance(service_data, dict):
                            if "items" in service_data:
                                concatenated_data["items"].extend(service_data["items"])
                            elif "data" in service_data:
                                if isinstance(service_data["data"], list):
                                    concatenated_data["items"].extend(service_data["data"])
                                else:
                                    concatenated_data["items"].append(service_data["data"])
                            else:
                                concatenated_data["items"].append(service_data)
                        else:
                            concatenated_data["items"].append(service_data)
                    
                except json.JSONDecodeError:
                    concatenated_data["items"].append({
                        "service": service_name,
                        "content": response.content.decode(),
                        "content_type": response.content_type
                    })
            
            concatenated_data["metadata"]["total_items"] = len(concatenated_data["items"])
            concatenated_data["metadata"]["total_response_time"] = round(total_response_time, 3)
            
            return concatenated_data
            
        except Exception as e:
            logger.error(f"Response concatenation error: {e}")
            raise
    
    async def _transform_responses(
        self, 
        service_responses: Dict[str, ServiceResponse],
        rule: Optional[AggregationRule] = None
    ) -> Dict[str, Any]:
        """Transform responses using custom logic"""
        try:
            # This would contain custom transformation logic
            # For now, implement a generic transformation
            
            transformed_data = {
                "result": {},
                "metadata": {
                    "transformed_at": datetime.utcnow().isoformat(),
                    "transformation_rule": rule.pattern if rule else "default",
                    "services_processed": len(service_responses)
                }
            }
            
            # Apply transformations based on service types
            for service_name, response in service_responses.items():
                if response.error:
                    continue
                
                try:
                    if response.content_type.startswith("application/json"):
                        service_data = json.loads(response.content.decode())
                        
                        # Apply service-specific transformations
                        if service_name == "analytics_agent":
                            transformed_data["result"]["analytics"] = self._transform_analytics_data(service_data)
                        elif service_name == "content_agent":
                            transformed_data["result"]["content"] = self._transform_content_data(service_data)
                        elif service_name == "protection_agent":
                            transformed_data["result"]["protection"] = self._transform_protection_data(service_data)
                        else:
                            transformed_data["result"][service_name] = service_data
                
                except json.JSONDecodeError:
                    continue
            
            return transformed_data
            
        except Exception as e:
            logger.error(f"Response transformation error: {e}")
            raise
    
    async def _collect_responses(
        self, 
        service_responses: Dict[str, ServiceResponse],
        rule: Optional[AggregationRule] = None
    ) -> Dict[str, Any]:
        """Collect responses with minimal processing"""
        try:
            collection = {
                "responses": {},
                "summary": {
                    "collected_at": datetime.utcnow().isoformat(),
                    "total_services": len(service_responses),
                    "successful_services": 0,
                    "failed_services": 0
                }
            }
            
            for service_name, response in service_responses.items():
                if response.error:
                    collection["responses"][service_name] = {
                        "status": "error",
                        "error": response.error,
                        "status_code": response.status_code
                    }
                    collection["summary"]["failed_services"] += 1
                else:
                    collection["responses"][service_name] = {
                        "status": "success",
                        "status_code": response.status_code,
                        "content_type": response.content_type,
                        "response_time": response.response_time,
                        "content_length": len(response.content)
                    }
                    collection["summary"]["successful_services"] += 1
            
            return collection
            
        except Exception as e:
            logger.error(f"Response collection error: {e}")
            raise
    
    def _transform_analytics_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Transform analytics service data"""
        # Implement analytics-specific transformations
        return {
            "metrics": data.get("metrics", {}),
            "insights": data.get("insights", []),
            "performance": data.get("performance", {})
        }
    
    def _transform_content_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Transform content service data"""
        # Implement content-specific transformations
        return {
            "content_items": data.get("items", []),
            "total_count": data.get("total", 0),
            "categories": data.get("categories", [])
        }
    
    def _transform_protection_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Transform protection service data"""
        # Implement protection-specific transformations
        return {
            "protection_status": data.get("status", "unknown"),
            "violations": data.get("violations", []),
            "recommendations": data.get("recommendations", [])
        }
    
    def _get_aggregation_rule(self, request_path: str) -> Optional[AggregationRule]:
        """Get aggregation rule for request path"""
        for pattern, rule in self.aggregation_rules.items():
            if self._match_pattern(request_path, pattern):
                return rule
        return None
    
    def _match_pattern(self, path: str, pattern: str) -> bool:
        """
Match request path against pattern"""
        # Simple pattern matching - could be enhanced with regex
        if pattern.endswith("*"):
            return path.startswith(pattern[:-1])
        return path == pattern
    
    def _create_aggregated_response(
        self, 
        aggregated_data: Dict[str, Any],
        service_responses: Dict[str, ServiceResponse]
    ) -> Response:
        """Create FastAPI response from aggregated data"""
        try:
            # Determine appropriate status code
            status_code = self._determine_status_code(service_responses)
            
            # Create response headers
            headers = {
                "X-Aggregated-Services": ",".join(service_responses.keys()),
                "X-Aggregation-Time": datetime.utcnow().isoformat(),
                "Content-Type": "application/json"
            }
            
            # Add CORS headers
            headers.update({
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS",
                "Access-Control-Allow-Headers": "*"
            })
            
            return JSONResponse(
                content=aggregated_data,
                status_code=status_code,
                headers=headers
            )
            
        except Exception as e:
            logger.error(f"Error creating aggregated response: {e}")
            return self._create_error_response("Aggregation failed", 500)
    
    def _determine_status_code(self, service_responses: Dict[str, ServiceResponse]) -> int:
        """Determine appropriate HTTP status code for aggregated response"""
        try:
            if not service_responses:
                return 204  # No Content
            
            # Get all status codes
            status_codes = [resp.status_code for resp in service_responses.values()]
            
            # If any 5xx errors, return 502 (Bad Gateway)
            if any(code >= 500 for code in status_codes):
                return 502
            
            # If any 4xx errors but some success, return 207 (Multi-Status)
            if any(400 <= code < 500 for code in status_codes) and any(200 <= code < 300 for code in status_codes):
                return 207
            
            # If all 4xx errors, return first 4xx code
            if all(400 <= code < 500 for code in status_codes):
                return next(code for code in status_codes if 400 <= code < 500)
            
            # If all successful, return 200
            if all(200 <= code < 300 for code in status_codes):
                return 200
            
            # Default to 200
            return 200
            
        except Exception as e:
            logger.error(f"Error determining status code: {e}")
            return 500
    
    def _create_error_response(self, error_message: str, status_code: int) -> Response:
        """Create error response"""
        return JSONResponse(
            content={
                "error": error_message,
                "status_code": status_code,
                "timestamp": datetime.utcnow().isoformat()
            },
            status_code=status_code
        )
    
    def _generate_cache_key(self, request_path: str, service_names: List[str]) -> str:
        """Generate cache key for response"""
        import hashlib
        
        key_parts = [request_path] + sorted(service_names)
        key_string = "|".join(key_parts)
        
        return hashlib.md5(key_string.encode()).hexdigest()
    
    async def _get_cached_response(self, cache_key: str) -> Optional[Dict[str, Any]]:
        """Get cached response"""
        try:
            # Check in-memory cache first
            if cache_key in self.response_cache:
                cache_entry = self.response_cache[cache_key]
                if cache_entry["expires_at"] > time.time():
                    return cache_entry["data"]
                else:
                    # Remove expired entry
                    del self.response_cache[cache_key]
            
            # Check Redis cache if available
            if self.redis:
                cached_data = await self.redis.get(f"response_cache:{cache_key}")
                if cached_data:
                    return json.loads(cached_data)
            
            return None
            
        except Exception as e:
            logger.error(f"Error getting cached response: {e}")
            return None
    
    async def _cache_response(
        self, 
        cache_key: str, 
        response: Response, 
        ttl: int
    ):
        """Cache response"""
        try:
            # Prepare cache data
            cache_data = {
                "content": response.body.decode() if hasattr(response, 'body') else None,
                "status_code": response.status_code,
                "headers": dict(response.headers) if hasattr(response, 'headers') else {},
                "cached_at": datetime.utcnow().isoformat()
            }
            
            # Store in memory cache
            self.response_cache[cache_key] = {
                "data": cache_data,
                "expires_at": time.time() + ttl
            }
            
            # Store in Redis if available
            if self.redis:
                await self.redis.setex(
                    f"response_cache:{cache_key}",
                    ttl,
                    json.dumps(cache_data)
                )
            
        except Exception as e:
            logger.error(f"Error caching response: {e}")
    
    def _create_response_from_cache(self, cached_data: Dict[str, Any]) -> Response:
        """Create response from cached data"""
        return JSONResponse(
            content=json.loads(cached_data["content"]) if cached_data.get("content") else {},
            status_code=cached_data.get("status_code", 200),
            headers=cached_data.get("headers", {})
        )
    
    def add_aggregation_rule(self, rule: AggregationRule) -> bool:
        """Add aggregation rule"""
        try:
            self.aggregation_rules[rule.pattern] = rule
            logger.info(f"Added aggregation rule: {rule.pattern} -> {rule.aggregation_type}")
            return True
            
        except Exception as e:
            logger.error(f"Error adding aggregation rule: {e}")
            return False
    
    def remove_aggregation_rule(self, pattern: str) -> bool:
        """Remove aggregation rule"""
        try:
            if pattern in self.aggregation_rules:
                del self.aggregation_rules[pattern]
                logger.info(f"Removed aggregation rule: {pattern}")
                return True
            return False
            
        except Exception as e:
            logger.error(f"Error removing aggregation rule: {e}")
            return False
    
    async def clear_cache(self, pattern: Optional[str] = None) -> bool:
        """Clear response cache"""
        try:
            if pattern:
                # Clear specific pattern
                keys_to_remove = [
                    key for key in self.response_cache.keys() 
                    if pattern in key
                ]
                for key in keys_to_remove:
                    del self.response_cache[key]
            else:
                # Clear all cache
                self.response_cache.clear()
            
            # Clear Redis cache if available
            if self.redis:
                if pattern:
                    keys = await self.redis.keys(f"response_cache:*{pattern}*")
                    if keys:
                        await self.redis.delete(*keys)
                else:
                    await self.redis.flushdb()
            
            logger.info("Response cache cleared")
            return True
            
        except Exception as e:
            logger.error(f"Error clearing cache: {e}")
            return False
    
    def get_aggregator_stats(self) -> Dict[str, Any]:
        """Get aggregator statistics"""
        try:
            return {
                "aggregation_rules": len(self.aggregation_rules),
                "cached_responses": len(self.response_cache),
                "supported_transformers": list(self.transformers.keys()),
                "cache_hit_rate": 0.0,  # Would be calculated with metrics
                "average_aggregation_time": 0.0  # Would be calculated with metrics
            }
            
        except Exception as e:
            logger.error(f"Error getting aggregator stats: {e}")
            return {}
