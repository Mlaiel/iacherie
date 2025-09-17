"""⚡ API Endpoint Profiling System
===============================

Advanced API endpoint performance monitoring for the Ainflue Creator Platform.
Provides comprehensive profiling for REST APIs, GraphQL, and microservices endpoints.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️ INTELLECTUAL PROPERTY WARNING:
=====================================
This code is proprietary to Fahed Mlaiel <mlaiel@live.de>
- Commercial use FORBIDDEN without written authorization  
- Reverse engineering STRICTLY PROHIBITED
- Distribution FORBIDDEN without explicit license
- Violation = Automatic legal prosecution

🏢 ENTERPRISE USAGE:
- Enterprise license available on request
- Technical support included with license
- Maintenance and updates assured
- Technical team training provided
"""

import asyncio
import logging
import time
import threading
from typing import Dict, List, Optional, Any, Union, Callable
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import json
import statistics
from collections import defaultdict, deque
import urllib.parse
import hashlib

logger = logging.getLogger(__name__)

# Try to import HTTP libraries
try:
    import requests
    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False

try:
    import aiohttp
    HAS_AIOHTTP = True
except ImportError:
    HAS_AIOHTTP = False

try:
    from fastapi import Request, Response
    HAS_FASTAPI = True
except ImportError:
    HAS_FASTAPI = False


class APIType(Enum):
    """Types of API"""
    REST = "rest"
    GRAPHQL = "graphql"
    WEBSOCKET = "websocket"
    GRPC = "grpc"
    WEBHOOK = "webhook"
    MICROSERVICE = "microservice"


class HTTPMethod(Enum):
    """HTTP methods"""
    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    DELETE = "DELETE"
    PATCH = "PATCH"
    HEAD = "HEAD"
    OPTIONS = "OPTIONS"


class EndpointCategory(Enum):
    """API endpoint categories"""
    AUTHENTICATION = "authentication"
    CONTENT_UPLOAD = "content_upload"
    CONTENT_PROCESSING = "content_processing"
    USER_MANAGEMENT = "user_management"
    SEARCH = "search"
    ANALYTICS = "analytics"
    PAYMENT = "payment"
    NOTIFICATION = "notification"
    COLLABORATION = "collaboration"
    SEO = "seo"


@dataclass
class EndpointMetadata:
    """Metadata for API endpoints"""
    endpoint_path: str
    method: HTTPMethod
    api_type: APIType
    category: EndpointCategory
    version: str = "v1"
    requires_auth: bool = True
    rate_limited: bool = True
    cache_enabled: bool = False
    payload_size: int = 0
    user_agent: Optional[str] = None
    client_ip: Optional[str] = None


@dataclass
class APIMetrics:
    """API endpoint performance metrics"""
    request_id: str
    endpoint_path: str
    method: HTTPMethod
    api_type: APIType
    category: EndpointCategory
    response_time_ms: float
    status_code: int
    payload_size_bytes: int
    response_size_bytes: int
    auth_time_ms: float
    database_time_ms: float
    external_api_time_ms: float
    cache_hit: bool
    rate_limit_remaining: int
    error_type: Optional[str]
    timestamp: datetime
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class APIBottleneck:
    """API endpoint bottleneck information"""
    bottleneck_type: str
    severity: str
    endpoint_path: str
    method: HTTPMethod
    description: str
    impact: str
    recommendations: List[str]
    detected_at: datetime
    metrics: Dict[str, float] = field(default_factory=dict)


class APIEndpointProfiler:
    """
    API endpoint performance profiler for Creator Economy platform
    """
    
    def __init__(self, 
                 monitoring_interval: float = 5.0,
                 max_history_size: int = 50000):
        self.monitoring_interval = monitoring_interval
        self.max_history_size = max_history_size
        self.is_monitoring = False
        self.monitoring_thread = None
        
        # Metrics storage
        self.api_metrics_history: deque = deque(maxlen=max_history_size)
        self.bottlenecks_history: deque = deque(maxlen=1000)
        self.active_requests: Dict[str, Dict] = {}
        
        # Performance thresholds
        self.thresholds = {
            'slow_request_threshold': 1000.0,    # 1 second
            'very_slow_request_threshold': 5000.0, # 5 seconds
            'high_error_rate_threshold': 5.0,    # 5%
            'auth_time_threshold': 200.0,        # 200ms
            'db_time_threshold': 500.0,          # 500ms
            'payload_size_threshold': 10 * 1024 * 1024  # 10MB
        }
        
        # Endpoint patterns and categories
        self.endpoint_patterns = self._init_endpoint_patterns()
        
        # Request interceptors
        self.request_interceptors: List[Callable] = []
        self.response_interceptors: List[Callable] = []
        
        logger.info("APIEndpointProfiler initialized")

    def _init_endpoint_patterns(self) -> Dict[str, EndpointCategory]:
        """Initialize endpoint patterns for categorization"""
        return {
            '/auth/': EndpointCategory.AUTHENTICATION,
            '/login': EndpointCategory.AUTHENTICATION,
            '/register': EndpointCategory.AUTHENTICATION,
            '/upload': EndpointCategory.CONTENT_UPLOAD,
            '/content/': EndpointCategory.CONTENT_PROCESSING,
            '/process': EndpointCategory.CONTENT_PROCESSING,
            '/users/': EndpointCategory.USER_MANAGEMENT,
            '/profile': EndpointCategory.USER_MANAGEMENT,
            '/search': EndpointCategory.SEARCH,
            '/analytics': EndpointCategory.ANALYTICS,
            '/metrics': EndpointCategory.ANALYTICS,
            '/payment': EndpointCategory.PAYMENT,
            '/subscribe': EndpointCategory.PAYMENT,
            '/notify': EndpointCategory.NOTIFICATION,
            '/collaborate': EndpointCategory.COLLABORATION,
            '/share': EndpointCategory.COLLABORATION,
            '/seo': EndpointCategory.SEO,
            '/sitemap': EndpointCategory.SEO
        }

    def start_monitoring(self):
        """Start background API monitoring"""
        if not self.is_monitoring:
            self.is_monitoring = True
            self.monitoring_thread = threading.Thread(
                target=self._monitoring_loop,
                daemon=True
            )
            self.monitoring_thread.start()
            logger.info("API endpoint monitoring started")

    def stop_monitoring(self):
        """Stop background monitoring"""
        self.is_monitoring = False
        if self.monitoring_thread:
            self.monitoring_thread.join(timeout=5.0)
        logger.info("API endpoint monitoring stopped")

    def _monitoring_loop(self):
        """Background monitoring loop"""
        while self.is_monitoring:
            try:
                self._collect_api_health_metrics()
                self._cleanup_stale_requests()
                time.sleep(self.monitoring_interval)
            except Exception as e:
                logger.error(f"Error in API monitoring loop: {e}")

    def _collect_api_health_metrics(self):
        """Collect overall API health metrics"""
        try:
            # Calculate request rates
            now = datetime.utcnow()
            recent_metrics = [
                m for m in list(self.api_metrics_history)[-1000:]
                if (now - m.timestamp).total_seconds() < 300  # Last 5 minutes
            ]
            
            if recent_metrics:
                request_rate = len(recent_metrics) / 5.0  # requests per second
                avg_response_time = statistics.mean([m.response_time_ms for m in recent_metrics])
                error_rate = (sum(1 for m in recent_metrics if m.status_code >= 400) / len(recent_metrics)) * 100
                
                # Create system metrics
                system_metrics = APIMetrics(
                    request_id=f"system_health_{int(time.time())}",
                    endpoint_path="/system/health",
                    method=HTTPMethod.GET,
                    api_type=APIType.REST,
                    category=EndpointCategory.ANALYTICS,
                    response_time_ms=avg_response_time,
                    status_code=200,
                    payload_size_bytes=0,
                    response_size_bytes=0,
                    auth_time_ms=0.0,
                    database_time_ms=0.0,
                    external_api_time_ms=0.0,
                    cache_hit=False,
                    rate_limit_remaining=1000,
                    error_type=None,
                    timestamp=now,
                    metadata={
                        'request_rate_per_sec': request_rate,
                        'active_requests': len(self.active_requests),
                        'error_rate_percent': error_rate,
                        'system_health_check': True
                    }
                )
                
                # Don't add to history to avoid skewing metrics
                # self.api_metrics_history.append(system_metrics)
                
        except Exception as e:
            logger.error(f"Error collecting API health metrics: {e}")

    def _cleanup_stale_requests(self):
        """Clean up stale active requests"""
        now = time.time()
        stale_threshold = 300  # 5 minutes
        
        stale_requests = [
            req_id for req_id, req_data in self.active_requests.items()
            if now - req_data.get('start_time', now) > stale_threshold
        ]
        
        for req_id in stale_requests:
            self.active_requests.pop(req_id, None)

    def categorize_endpoint(self, endpoint_path: str) -> EndpointCategory:
        """Categorize endpoint based on path patterns"""
        path_lower = endpoint_path.lower()
        
        for pattern, category in self.endpoint_patterns.items():
            if pattern in path_lower:
                return category
        
        # Default category
        return EndpointCategory.USER_MANAGEMENT

    def profile_api_request(self,
                          endpoint_path: str,
                          method: HTTPMethod,
                          api_type: APIType = APIType.REST,
                          **kwargs) -> str:
        """
        Start profiling an API request
        
        Args:
            endpoint_path: API endpoint path
            method: HTTP method
            api_type: Type of API
            **kwargs: Additional request metadata
            
        Returns:
            Request ID for tracking
        """
        request_id = self._generate_request_id(endpoint_path, method)
        start_time = time.time()
        
        # Categorize endpoint
        category = self.categorize_endpoint(endpoint_path)
        
        # Store request start info
        self.active_requests[request_id] = {
            'start_time': start_time,
            'endpoint_path': endpoint_path,
            'method': method,
            'api_type': api_type,
            'category': category,
            'metadata': kwargs
        }
        
        return request_id

    def complete_api_request(self,
                           request_id: str,
                           status_code: int,
                           response_size_bytes: int = 0,
                           auth_time_ms: float = 0.0,
                           database_time_ms: float = 0.0,
                           external_api_time_ms: float = 0.0,
                           cache_hit: bool = False,
                           rate_limit_remaining: int = 1000,
                           error_type: Optional[str] = None,
                           **kwargs) -> APIMetrics:
        """
        Complete profiling an API request
        
        Args:
            request_id: Request ID from profile_api_request
            status_code: HTTP status code
            response_size_bytes: Size of response
            auth_time_ms: Time spent on authentication
            database_time_ms: Time spent on database operations
            external_api_time_ms: Time spent on external API calls
            cache_hit: Whether response was served from cache
            rate_limit_remaining: Remaining rate limit quota
            error_type: Type of error if any
            **kwargs: Additional response metadata
            
        Returns:
            APIMetrics with profiling results
        """
        end_time = time.time()
        
        # Get request info
        request_info = self.active_requests.get(request_id)
        if not request_info:
            raise ValueError(f"Request ID {request_id} not found")
        
        start_time = request_info['start_time']
        response_time_ms = (end_time - start_time) * 1000
        
        # Create metrics
        metrics = APIMetrics(
            request_id=request_id,
            endpoint_path=request_info['endpoint_path'],
            method=request_info['method'],
            api_type=request_info['api_type'],
            category=request_info['category'],
            response_time_ms=response_time_ms,
            status_code=status_code,
            payload_size_bytes=request_info['metadata'].get('payload_size', 0),
            response_size_bytes=response_size_bytes,
            auth_time_ms=auth_time_ms,
            database_time_ms=database_time_ms,
            external_api_time_ms=external_api_time_ms,
            cache_hit=cache_hit,
            rate_limit_remaining=rate_limit_remaining,
            error_type=error_type,
            timestamp=datetime.utcnow(),
            metadata={
                **request_info['metadata'],
                **kwargs,
                'user_agent': request_info['metadata'].get('user_agent'),
                'client_ip': request_info['metadata'].get('client_ip')
            }
        )
        
        # Store metrics
        self.api_metrics_history.append(metrics)
        
        # Remove from active requests
        self.active_requests.pop(request_id, None)
        
        # Check for bottlenecks
        self._analyze_api_bottlenecks(metrics)
        
        return metrics

    def _generate_request_id(self, endpoint_path: str, method: HTTPMethod) -> str:
        """Generate unique request ID"""
        timestamp = str(time.time())
        content = f"{endpoint_path}_{method.value}_{timestamp}"
        return hashlib.md5(content.encode()).hexdigest()[:16]

    def _analyze_api_bottlenecks(self, metrics: APIMetrics):
        """Analyze API bottlenecks"""
        bottlenecks = []
        
        # Check response time
        if metrics.response_time_ms > self.thresholds['very_slow_request_threshold']:
            severity = "critical"
        elif metrics.response_time_ms > self.thresholds['slow_request_threshold']:
            severity = "high"
        else:
            severity = None
        
        if severity:
            bottlenecks.append(APIBottleneck(
                bottleneck_type="slow_response",
                severity=severity,
                endpoint_path=metrics.endpoint_path,
                method=metrics.method,
                description=f"API response too slow: {metrics.response_time_ms:.1f}ms",
                impact="Poor user experience, potential timeouts",
                recommendations=[
                    "Optimize database queries",
                    "Implement caching",
                    "Reduce payload size",
                    "Add async processing"
                ],
                detected_at=datetime.utcnow(),
                metrics={'response_time_ms': metrics.response_time_ms}
            ))
        
        # Check authentication time
        if metrics.auth_time_ms > self.thresholds['auth_time_threshold']:
            bottlenecks.append(APIBottleneck(
                bottleneck_type="slow_authentication",
                severity="medium",
                endpoint_path=metrics.endpoint_path,
                method=metrics.method,
                description=f"Authentication too slow: {metrics.auth_time_ms:.1f}ms",
                impact="Delayed API responses",
                recommendations=[
                    "Optimize authentication logic",
                    "Cache user sessions",
                    "Use faster JWT validation",
                    "Implement auth microservice"
                ],
                detected_at=datetime.utcnow(),
                metrics={'auth_time_ms': metrics.auth_time_ms}
            ))
        
        # Check database time
        if metrics.database_time_ms > self.thresholds['db_time_threshold']:
            bottlenecks.append(APIBottleneck(
                bottleneck_type="slow_database",
                severity="high",
                endpoint_path=metrics.endpoint_path,
                method=metrics.method,
                description=f"Database operations too slow: {metrics.database_time_ms:.1f}ms",
                impact="Major performance bottleneck",
                recommendations=[
                    "Add database indexes",
                    "Optimize queries",
                    "Implement query caching",
                    "Use read replicas"
                ],
                detected_at=datetime.utcnow(),
                metrics={'database_time_ms': metrics.database_time_ms}
            ))
        
        # Check payload size
        if metrics.payload_size_bytes > self.thresholds['payload_size_threshold']:
            bottlenecks.append(APIBottleneck(
                bottleneck_type="large_payload",
                severity="medium",
                endpoint_path=metrics.endpoint_path,
                method=metrics.method,
                description=f"Payload too large: {metrics.payload_size_bytes / 1024 / 1024:.1f}MB",
                impact="Increased network latency and processing time",
                recommendations=[
                    "Implement payload compression",
                    "Split large requests",
                    "Use multipart uploads",
                    "Validate payload size limits"
                ],
                detected_at=datetime.utcnow(),
                metrics={'payload_size_mb': metrics.payload_size_bytes / 1024 / 1024}
            ))
        
        # Check for errors
        if metrics.status_code >= 500:
            bottlenecks.append(APIBottleneck(
                bottleneck_type="server_error",
                severity="critical",
                endpoint_path=metrics.endpoint_path,
                method=metrics.method,
                description=f"Server error: {metrics.status_code}",
                impact="API functionality disrupted",
                recommendations=[
                    "Check server logs",
                    "Monitor system resources",
                    "Implement error handling",
                    "Add health checks"
                ],
                detected_at=datetime.utcnow(),
                metrics={'status_code': metrics.status_code}
            ))
        elif metrics.status_code >= 400:
            bottlenecks.append(APIBottleneck(
                bottleneck_type="client_error",
                severity="low",
                endpoint_path=metrics.endpoint_path,
                method=metrics.method,
                description=f"Client error: {metrics.status_code}",
                impact="Invalid requests from clients",
                recommendations=[
                    "Improve API documentation",
                    "Add request validation",
                    "Enhance error messages",
                    "Monitor client patterns"
                ],
                detected_at=datetime.utcnow(),
                metrics={'status_code': metrics.status_code}
            ))
        
        # Store bottlenecks
        for bottleneck in bottlenecks:
            self.bottlenecks_history.append(bottleneck)

    def get_performance_summary(self) -> Dict[str, Any]:
        """Get API performance summary"""
        if not self.api_metrics_history:
            return {"error": "No metrics available"}
        
        recent_metrics = list(self.api_metrics_history)[-5000:]  # Last 5000 requests
        
        # Calculate statistics
        response_times = [m.response_time_ms for m in recent_metrics]
        error_count = sum(1 for m in recent_metrics if m.status_code >= 400)
        auth_times = [m.auth_time_ms for m in recent_metrics if m.auth_time_ms > 0]
        db_times = [m.database_time_ms for m in recent_metrics if m.database_time_ms > 0]
        cache_hits = sum(1 for m in recent_metrics if m.cache_hit)
        
        return {
            "summary": {
                "total_requests": len(recent_metrics),
                "avg_response_time_ms": statistics.mean(response_times) if response_times else 0,
                "p50_response_time_ms": statistics.median(response_times) if response_times else 0,
                "p95_response_time_ms": statistics.quantiles(response_times, n=20)[18] if len(response_times) > 20 else 0,
                "p99_response_time_ms": statistics.quantiles(response_times, n=100)[98] if len(response_times) > 100 else 0,
                "error_rate": (error_count / len(recent_metrics)) * 100,
                "avg_auth_time_ms": statistics.mean(auth_times) if auth_times else 0,
                "avg_db_time_ms": statistics.mean(db_times) if db_times else 0,
                "cache_hit_rate": (cache_hits / len(recent_metrics)) * 100,
                "active_requests": len(self.active_requests),
                "requests_per_minute": len(recent_metrics) / max(1, len(recent_metrics) / 1000) * 60
            },
            "by_endpoint": self._get_metrics_by_endpoint(),
            "by_method": self._get_metrics_by_method(),
            "by_category": self._get_metrics_by_category(),
            "by_status_code": self._get_metrics_by_status_code(),
            "bottlenecks": len(self.bottlenecks_history),
            "recommendations": self._get_api_optimization_recommendations()
        }

    def _get_metrics_by_endpoint(self) -> Dict[str, Dict]:
        """Get metrics grouped by endpoint"""
        metrics_by_endpoint = defaultdict(list)
        
        for metrics in list(self.api_metrics_history)[-1000:]:
            metrics_by_endpoint[metrics.endpoint_path].append(metrics)
        
        result = {}
        for endpoint, metrics_list in metrics_by_endpoint.items():
            response_times = [m.response_time_ms for m in metrics_list]
            error_count = sum(1 for m in metrics_list if m.status_code >= 400)
            
            result[endpoint] = {
                "requests": len(metrics_list),
                "avg_response_time_ms": statistics.mean(response_times) if response_times else 0,
                "error_rate": (error_count / len(metrics_list)) * 100,
                "cache_hit_rate": (sum(1 for m in metrics_list if m.cache_hit) / len(metrics_list)) * 100
            }
        
        return dict(sorted(result.items(), key=lambda x: x[1]['requests'], reverse=True)[:10])

    def _get_metrics_by_method(self) -> Dict[str, Dict]:
        """Get metrics grouped by HTTP method"""
        metrics_by_method = defaultdict(list)
        
        for metrics in list(self.api_metrics_history)[-1000:]:
            metrics_by_method[metrics.method.value].append(metrics)
        
        result = {}
        for method, metrics_list in metrics_by_method.items():
            response_times = [m.response_time_ms for m in metrics_list]
            error_count = sum(1 for m in metrics_list if m.status_code >= 400)
            
            result[method] = {
                "requests": len(metrics_list),
                "avg_response_time_ms": statistics.mean(response_times) if response_times else 0,
                "error_rate": (error_count / len(metrics_list)) * 100
            }
        
        return result

    def _get_metrics_by_category(self) -> Dict[str, Dict]:
        """Get metrics grouped by endpoint category"""
        metrics_by_category = defaultdict(list)
        
        for metrics in list(self.api_metrics_history)[-1000:]:
            metrics_by_category[metrics.category.value].append(metrics)
        
        result = {}
        for category, metrics_list in metrics_by_category.items():
            response_times = [m.response_time_ms for m in metrics_list]
            error_count = sum(1 for m in metrics_list if m.status_code >= 400)
            
            result[category] = {
                "requests": len(metrics_list),
                "avg_response_time_ms": statistics.mean(response_times) if response_times else 0,
                "error_rate": (error_count / len(metrics_list)) * 100
            }
        
        return result

    def _get_metrics_by_status_code(self) -> Dict[str, int]:
        """Get request count by status code"""
        status_counts = defaultdict(int)
        
        for metrics in list(self.api_metrics_history)[-1000:]:
            status_counts[str(metrics.status_code)] += 1
        
        return dict(status_counts)

    def _get_api_optimization_recommendations(self) -> List[str]:
        """Get API optimization recommendations"""
        recommendations = []
        
        if not self.api_metrics_history:
            return ["Start profiling API requests to get recommendations"]
        
        recent_metrics = list(self.api_metrics_history)[-1000:]
        
        # Calculate key metrics
        avg_response_time = statistics.mean([m.response_time_ms for m in recent_metrics])
        error_rate = (sum(1 for m in recent_metrics if m.status_code >= 400) / len(recent_metrics)) * 100
        cache_hit_rate = (sum(1 for m in recent_metrics if m.cache_hit) / len(recent_metrics)) * 100
        avg_db_time = statistics.mean([m.database_time_ms for m in recent_metrics if m.database_time_ms > 0])
        
        if avg_response_time > 1000:
            recommendations.append("High response times - optimize slow endpoints")
        if error_rate > 5:
            recommendations.append("High error rate - investigate and fix API issues")
        if cache_hit_rate < 50:
            recommendations.append("Low cache hit rate - implement better caching strategy")
        if avg_db_time > 500:
            recommendations.append("Slow database operations - optimize queries and indexes")
        if len(self.active_requests) > 100:
            recommendations.append("High concurrent requests - consider scaling infrastructure")
        
        # Check for specific endpoint issues
        endpoint_metrics = self._get_metrics_by_endpoint()
        slow_endpoints = [ep for ep, data in endpoint_metrics.items() if data['avg_response_time_ms'] > 2000]
        if slow_endpoints:
            recommendations.append(f"Slow endpoints detected: {', '.join(slow_endpoints[:3])}")
        
        if not recommendations:
            recommendations.append("API performance is optimal")
        
        return recommendations

    def get_recent_bottlenecks(self, limit: int = 10) -> List[APIBottleneck]:
        """Get recent API bottlenecks"""
        return list(self.bottlenecks_history)[-limit:]

    def add_request_interceptor(self, interceptor: Callable):
        """Add request interceptor for custom profiling"""
        self.request_interceptors.append(interceptor)

    def add_response_interceptor(self, interceptor: Callable):
        """Add response interceptor for custom profiling"""
        self.response_interceptors.append(interceptor)

    def create_fastapi_middleware(self):
        """Create FastAPI middleware for automatic profiling"""
        if not HAS_FASTAPI:
            raise ImportError("FastAPI not available")
        
        async def api_profiling_middleware(request: Request, call_next):
            # Start profiling
            request_id = self.profile_api_request(
                endpoint_path=str(request.url.path),
                method=HTTPMethod(request.method),
                api_type=APIType.REST,
                user_agent=request.headers.get('user-agent'),
                client_ip=request.client.host if request.client else None,
                payload_size=int(request.headers.get('content-length', 0))
            )
            
            # Process request
            start_time = time.time()
            response = await call_next(request)
            auth_time = time.time() - start_time  # Simplified
            
            # Complete profiling
            self.complete_api_request(
                request_id=request_id,
                status_code=response.status_code,
                response_size_bytes=0,  # Would need to measure actual response size
                auth_time_ms=auth_time * 1000,
                cache_hit=response.headers.get('x-cache-hit') == 'true'
            )
            
            return response
        
        return api_profiling_middleware

    def export_metrics(self, format: str = "json") -> str:
        """Export API metrics"""
        data = {
            "api_metrics": [
                {
                    "request_id": m.request_id,
                    "endpoint_path": m.endpoint_path,
                    "method": m.method.value,
                    "category": m.category.value,
                    "response_time_ms": m.response_time_ms,
                    "status_code": m.status_code,
                    "cache_hit": m.cache_hit,
                    "timestamp": m.timestamp.isoformat()
                }
                for m in list(self.api_metrics_history)[-1000:]
            ],
            "bottlenecks": [
                {
                    "type": b.bottleneck_type,
                    "severity": b.severity,
                    "endpoint": b.endpoint_path,
                    "method": b.method.value,
                    "description": b.description,
                    "detected_at": b.detected_at.isoformat()
                }
                for b in list(self.bottlenecks_history)[-100:]
            ]
        }
        
        if format == "json":
            return json.dumps(data, indent=2)
        else:
            return str(data)


# Factory function
def create_api_endpoint_profiler(monitoring_interval: float = 5.0,
                               max_history_size: int = 50000,
                               start_monitoring: bool = True) -> APIEndpointProfiler:
    """
    Create and configure an API endpoint profiler
    
    Args:
        monitoring_interval: Monitoring interval in seconds
        max_history_size: Maximum number of metrics to store
        start_monitoring: Start background monitoring
        
    Returns:
        Configured APIEndpointProfiler instance
    """
    profiler = APIEndpointProfiler(
        monitoring_interval=monitoring_interval,
        max_history_size=max_history_size
    )
    
    if start_monitoring:
        profiler.start_monitoring()
    
    return profiler


# Main execution
if __name__ == "__main__":
    # Example usage
    profiler = create_api_endpoint_profiler()
    
    try:
        # Example: Profile an API request manually
        request_id = profiler.profile_api_request(
            endpoint_path="/api/v1/content/upload",
            method=HTTPMethod.POST,
            api_type=APIType.REST,
            payload_size=1024 * 1024  # 1MB
        )
        
        # Simulate some processing time
        time.sleep(0.1)
        
        # Complete the request
        metrics = profiler.complete_api_request(
            request_id=request_id,
            status_code=201,
            response_size_bytes=512,
            auth_time_ms=50.0,
            database_time_ms=75.0,
            cache_hit=False
        )
        
        print(f"API request response time: {metrics.response_time_ms:.2f}ms")
        print(f"Status code: {metrics.status_code}")
        print(f"Category: {metrics.category.value}")
        
        # Get performance summary
        summary = profiler.get_performance_summary()
        print(f"Performance summary: {json.dumps(summary, indent=2)}")
        
    finally:
        profiler.stop_monitoring()