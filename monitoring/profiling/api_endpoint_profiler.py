"""🌐 API Endpoint Performance Profiler
=====================================

Advanced API endpoint performance profiling system for the Ainflue Creator Economy platform.
Monitors REST APIs, GraphQL endpoints, authentication overhead, and rate limiting performance.

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
from typing import Dict, List, Optional, Any, Callable, Union
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import json
import statistics
from collections import defaultdict, deque
import re

from prometheus_client import Counter, Gauge, Histogram, Summary

logger = logging.getLogger(__name__)


class APIType(Enum):
    """Types of API endpoints"""
    REST = "rest"
    GRAPHQL = "graphql"
    WEBSOCKET = "websocket"
    GRPC = "grpc"
    WEBHOOK = "webhook"
    SSE = "server_sent_events"


class HTTPMethod(Enum):
    """HTTP methods"""
    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    DELETE = "DELETE"
    PATCH = "PATCH"
    OPTIONS = "OPTIONS"
    HEAD = "HEAD"


class APICategory(Enum):
    """API endpoint categories for Creator Economy"""
    USER_MANAGEMENT = "user_management"
    CREATOR_PROFILES = "creator_profiles"
    CONTENT_MANAGEMENT = "content_management"
    COLLABORATION = "collaboration"
    ANALYTICS = "analytics"
    MONETIZATION = "monetization"
    AUTHENTICATION = "authentication"
    DISTRIBUTION = "distribution"
    AI_PROCESSING = "ai_processing"
    SEARCH = "search"
    NOTIFICATIONS = "notifications"
    ADMIN = "admin"


class AuthenticationType(Enum):
    """Types of authentication"""
    NONE = "none"
    BEARER_TOKEN = "bearer_token"
    API_KEY = "api_key"
    OAUTH2 = "oauth2"
    JWT = "jwt"
    BASIC_AUTH = "basic_auth"
    SESSION = "session"
    CUSTOM = "custom"


@dataclass
class APIRequestMetadata:
    """Metadata for API requests"""
    endpoint_path: str
    method: HTTPMethod
    api_type: APIType
    category: APICategory
    authentication_type: AuthenticationType
    
    # Request details
    request_size_bytes: int
    headers_count: int
    query_params_count: int
    path_params_count: int
    
    # User context
    user_id: Optional[str] = None
    user_role: Optional[str] = None
    api_version: str = "v1"
    client_type: str = "web"  # web, mobile, api
    
    # Rate limiting
    rate_limit_key: Optional[str] = None
    current_rate_limit: Optional[int] = None
    rate_limit_window: Optional[int] = None


@dataclass
class APIResponseMetadata:
    """Metadata for API responses"""
    status_code: int
    response_size_bytes: int
    headers_count: int
    
    # Content details
    content_type: str = "application/json"
    compression_used: bool = False
    cache_status: str = "miss"  # hit, miss, bypass
    
    # Business metrics
    data_records_count: int = 0
    pagination_enabled: bool = False
    current_page: Optional[int] = None
    total_pages: Optional[int] = None


@dataclass
class APIMetrics:
    """API endpoint performance metrics"""
    request_id: str
    endpoint_path: str
    method: HTTPMethod
    api_type: APIType
    category: APICategory
    total_time_ms: float
    
    # Request/Response metadata
    request_metadata: APIRequestMetadata
    response_metadata: Optional[APIResponseMetadata] = None
    
    # Performance metrics
    auth_time_ms: Optional[float] = None
    processing_time_ms: Optional[float] = None
    database_time_ms: Optional[float] = None
    external_api_time_ms: Optional[float] = None
    response_time_ms: Optional[float] = None
    
    # Network metrics
    dns_lookup_time_ms: Optional[float] = None
    tcp_connect_time_ms: Optional[float] = None
    tls_handshake_time_ms: Optional[float] = None
    
    # Resource usage
    memory_usage_mb: float = 0.0
    cpu_usage_percent: float = 0.0
    
    # Rate limiting metrics
    rate_limit_remaining: Optional[int] = None
    rate_limit_reset_time: Optional[datetime] = None
    rate_limited: bool = False
    
    # Quality metrics
    success: bool = True
    error_message: Optional[str] = None
    error_type: Optional[str] = None
    retry_count: int = 0
    
    timestamp: datetime = field(default_factory=datetime.utcnow)


@dataclass
class APIBottleneck:
    """API performance bottleneck detection"""
    bottleneck_id: str
    endpoint_path: str
    method: HTTPMethod
    category: APICategory
    
    # Bottleneck details
    bottleneck_type: str  # "slow_response", "high_error_rate", "auth_overhead", "rate_limiting"
    severity: str  # "low", "medium", "high", "critical"
    description: str
    
    # Performance impact
    current_performance: Dict[str, float]
    expected_performance: Dict[str, float]
    impact_percentage: float
    
    # Affected requests
    affected_requests: List[str]
    error_patterns: List[str]
    
    # Optimization recommendations
    recommendations: List[str]
    estimated_improvement: Dict[str, float]
    
    timestamp: datetime = field(default_factory=datetime.utcnow)


class APIEndpointProfiler:
    """Advanced API endpoint performance profiler"""
    
    def __init__(self,
                 monitoring_interval: float = 1.0,
                 max_history_size: int = 10000,
                 enable_detailed_timing: bool = True,
                 enable_rate_limit_tracking: bool = True,
                 slow_request_threshold_ms: float = 1000.0):
        """
        Initialize API endpoint profiler
        
        Args:
            monitoring_interval: Monitoring interval in seconds
            max_history_size: Maximum number of metrics to store
            enable_detailed_timing: Enable detailed request timing breakdown
            enable_rate_limit_tracking: Enable rate limiting tracking
            slow_request_threshold_ms: Threshold for slow request detection
        """
        self.monitoring_interval = monitoring_interval
        self.max_history_size = max_history_size
        self.enable_detailed_timing = enable_detailed_timing
        self.enable_rate_limit_tracking = enable_rate_limit_tracking
        self.slow_request_threshold_ms = slow_request_threshold_ms
        
        # Storage for metrics
        self.metrics_history: deque = deque(maxlen=max_history_size)
        self.current_requests: Dict[str, APIMetrics] = {}
        self.bottlenecks: List[APIBottleneck] = []
        self.slow_requests: deque = deque(maxlen=1000)
        
        # Endpoint pattern tracking
        self.endpoint_patterns: Dict[str, List[float]] = defaultdict(list)
        self.error_patterns: Dict[str, List[str]] = defaultdict(list)
        
        # Performance thresholds
        self.thresholds = {
            'max_response_time_ms': slow_request_threshold_ms,
            'max_auth_time_ms': 200.0,
            'max_error_rate_percent': 5.0,
            'max_memory_usage_mb': 500.0,
            'max_cpu_usage_percent': 80.0
        }
        
        # Monitoring state
        self.is_monitoring = False
        self.monitoring_task: Optional[asyncio.Task] = None
        self._lock = threading.Lock()
        
        # Prometheus metrics
        self._init_prometheus_metrics()
        
        logger.info("APIEndpointProfiler initialized for Creator Economy platform")
    
    def _init_prometheus_metrics(self):
        """Initialize Prometheus metrics"""
        self.prometheus_metrics = {
            'api_request_duration': Histogram(
                'ainflue_api_request_duration_seconds',
                'Duration of API requests',
                ['endpoint', 'method', 'category', 'status_code']
            ),
            'api_request_size': Histogram(
                'ainflue_api_request_size_bytes',
                'Size of API requests',
                ['endpoint', 'method', 'category']
            ),
            'api_response_size': Histogram(
                'ainflue_api_response_size_bytes',
                'Size of API responses',
                ['endpoint', 'method', 'category', 'status_code']
            ),
            'api_errors': Counter(
                'ainflue_api_errors_total',
                'Total API errors',
                ['endpoint', 'method', 'category', 'error_type']
            ),
            'api_rate_limits': Counter(
                'ainflue_api_rate_limits_total',
                'Total rate limit hits',
                ['endpoint', 'method', 'category']
            ),
            'api_auth_duration': Histogram(
                'ainflue_api_auth_duration_seconds',
                'Duration of API authentication',
                ['auth_type', 'category']
            ),
            'api_bottlenecks': Gauge(
                'ainflue_api_bottlenecks_active',
                'Number of active API bottlenecks',
                ['category', 'severity']
            )
        }
    
    async def start_monitoring(self):
        """Start continuous API monitoring"""
        if self.is_monitoring:
            logger.warning("API monitoring already running")
            return
        
        self.is_monitoring = True
        self.monitoring_task = asyncio.create_task(self._monitoring_loop())
        logger.info("API endpoint monitoring started")
    
    async def stop_monitoring(self):
        """Stop API monitoring"""
        if not self.is_monitoring:
            return
        
        self.is_monitoring = False
        if self.monitoring_task:
            self.monitoring_task.cancel()
            try:
                await self.monitoring_task
            except asyncio.CancelledError:
                pass
        
        logger.info("API endpoint monitoring stopped")
    
    async def profile_api_request(self,
                                request_metadata: APIRequestMetadata,
                                api_func: Callable,
                                *args, **kwargs) -> APIMetrics:
        """
        Profile an API request
        
        Args:
            request_metadata: Request metadata
            api_func: Function to execute and profile
            *args, **kwargs: Arguments for the API function
        
        Returns:
            APIMetrics: Detailed performance metrics
        """
        request_id = f"api_{int(time.time() * 1000)}"
        start_time = time.time()
        
        # Initialize metrics
        metrics = APIMetrics(
            request_id=request_id,
            endpoint_path=request_metadata.endpoint_path,
            method=request_metadata.method,
            api_type=request_metadata.api_type,
            category=request_metadata.category,
            request_metadata=request_metadata,
            total_time_ms=0.0
        )
        
        try:
            # Start timing breakdown
            timing_breakdown = {}
            
            # Simulate authentication timing if enabled
            if self.enable_detailed_timing and request_metadata.authentication_type != AuthenticationType.NONE:
                auth_start = time.time()
                # Authentication would happen here
                await asyncio.sleep(0.001)  # Simulated auth time
                auth_end = time.time()
                metrics.auth_time_ms = (auth_end - auth_start) * 1000
                timing_breakdown['auth'] = metrics.auth_time_ms
            
            # Execute the API function
            processing_start = time.time()
            result = await self._execute_api_operation(api_func, *args, **kwargs)
            processing_end = time.time()
            
            metrics.processing_time_ms = (processing_end - processing_start) * 1000
            timing_breakdown['processing'] = metrics.processing_time_ms
            
            # Extract response metadata
            metrics.response_metadata = self._extract_response_metadata(result)
            
            # Calculate total time
            end_time = time.time()
            metrics.total_time_ms = (end_time - start_time) * 1000
            
            # Set success
            metrics.success = True
            
            # Store metrics
            await self._store_metrics(metrics)
            
            # Update Prometheus metrics
            self._update_prometheus_metrics(metrics)
            
            # Track endpoint patterns
            await self._track_endpoint_patterns(metrics)
            
            # Check for bottlenecks
            await self._detect_bottlenecks(metrics)
            
            # Check for slow requests
            if metrics.total_time_ms > self.slow_request_threshold_ms:
                await self._handle_slow_request(metrics)
            
            logger.debug(f"API request profiled: {request_id} - {metrics.total_time_ms:.2f}ms")
            return metrics
            
        except Exception as e:
            # Handle API failure
            end_time = time.time()
            metrics.total_time_ms = (end_time - start_time) * 1000
            metrics.success = False
            metrics.error_message = str(e)
            metrics.error_type = type(e).__name__
            
            # Create error response metadata
            metrics.response_metadata = APIResponseMetadata(
                status_code=500,
                response_size_bytes=len(str(e)),
                headers_count=0
            )
            
            await self._store_metrics(metrics)
            self.prometheus_metrics['api_errors'].labels(
                endpoint=self._normalize_endpoint_path(metrics.endpoint_path),
                method=metrics.method.value,
                category=metrics.category.value,
                error_type=metrics.error_type
            ).inc()
            
            logger.error(f"API request failed: {request_id} - {e}")
            return metrics
    
    async def _execute_api_operation(self, operation_func: Callable, *args, **kwargs):
        """Execute API operation with proper async handling"""
        if asyncio.iscoroutinefunction(operation_func):
            return await operation_func(*args, **kwargs)
        else:
            return operation_func(*args, **kwargs)
    
    def _extract_response_metadata(self, result: Any) -> APIResponseMetadata:
        """Extract response metadata from API result"""
        if isinstance(result, dict):
            # Extract from response dict
            status_code = result.get('status_code', 200)
            response_size = len(json.dumps(result)) if result else 0
            
            return APIResponseMetadata(
                status_code=status_code,
                response_size_bytes=response_size,
                headers_count=len(result.get('headers', {})),
                content_type=result.get('content_type', 'application/json'),
                data_records_count=len(result.get('data', [])) if isinstance(result.get('data'), list) else 1
            )
        
        # Default response metadata
        return APIResponseMetadata(
            status_code=200,
            response_size_bytes=len(str(result)) if result else 0,
            headers_count=0
        )
    
    async def _store_metrics(self, metrics: APIMetrics):
        """Store metrics in history"""
        with self._lock:
            self.metrics_history.append(metrics)
            self.current_requests[metrics.request_id] = metrics
    
    def _update_prometheus_metrics(self, metrics: APIMetrics):
        """Update Prometheus metrics"""
        endpoint_normalized = self._normalize_endpoint_path(metrics.endpoint_path)
        status_code = str(metrics.response_metadata.status_code) if metrics.response_metadata else "500"
        
        # Update request duration
        self.prometheus_metrics['api_request_duration'].labels(
            endpoint=endpoint_normalized,
            method=metrics.method.value,
            category=metrics.category.value,
            status_code=status_code
        ).observe(metrics.total_time_ms / 1000)
        
        # Update request size
        self.prometheus_metrics['api_request_size'].labels(
            endpoint=endpoint_normalized,
            method=metrics.method.value,
            category=metrics.category.value
        ).observe(metrics.request_metadata.request_size_bytes)
        
        # Update response size
        if metrics.response_metadata:
            self.prometheus_metrics['api_response_size'].labels(
                endpoint=endpoint_normalized,
                method=metrics.method.value,
                category=metrics.category.value,
                status_code=status_code
            ).observe(metrics.response_metadata.response_size_bytes)
        
        # Update auth duration
        if metrics.auth_time_ms is not None:
            self.prometheus_metrics['api_auth_duration'].labels(
                auth_type=metrics.request_metadata.authentication_type.value,
                category=metrics.category.value
            ).observe(metrics.auth_time_ms / 1000)
        
        # Update rate limit hits
        if metrics.rate_limited:
            self.prometheus_metrics['api_rate_limits'].labels(
                endpoint=endpoint_normalized,
                method=metrics.method.value,
                category=metrics.category.value
            ).inc()
    
    def _normalize_endpoint_path(self, path: str) -> str:
        """Normalize endpoint path for metrics"""
        # Replace dynamic parts with placeholders
        # e.g., /api/users/123/profile -> /api/users/{id}/profile
        normalized = re.sub(r'/\d+', '/{id}', path)
        normalized = re.sub(r'/[a-f0-9-]{36}', '/{uuid}', normalized)  # UUIDs
        return normalized
    
    async def _track_endpoint_patterns(self, metrics: APIMetrics):
        """Track endpoint patterns for optimization"""
        endpoint_pattern = self._normalize_endpoint_path(metrics.endpoint_path)
        
        with self._lock:
            self.endpoint_patterns[endpoint_pattern].append(metrics.total_time_ms)
            
            # Track error patterns
            if not metrics.success:
                self.error_patterns[endpoint_pattern].append(metrics.error_message or "unknown_error")
            
            # Keep only recent patterns
            if len(self.endpoint_patterns[endpoint_pattern]) > 100:
                self.endpoint_patterns[endpoint_pattern] = self.endpoint_patterns[endpoint_pattern][-100:]
    
    async def _handle_slow_request(self, metrics: APIMetrics):
        """Handle slow request detection"""
        with self._lock:
            self.slow_requests.append(metrics)
        
        logger.warning(f"Slow API request detected: {metrics.request_id} - {metrics.total_time_ms:.2f}ms")
    
    async def _detect_bottlenecks(self, metrics: APIMetrics):
        """Detect API performance bottlenecks"""
        bottlenecks = []
        
        # Slow response detection
        if metrics.total_time_ms > self.thresholds['max_response_time_ms']:
            bottleneck = APIBottleneck(
                bottleneck_id=f"slow_response_{int(time.time())}",
                endpoint_path=metrics.endpoint_path,
                method=metrics.method,
                category=metrics.category,
                bottleneck_type="slow_response",
                severity="high" if metrics.total_time_ms > self.thresholds['max_response_time_ms'] * 2 else "medium",
                description=f"Slow API response: {metrics.total_time_ms:.2f}ms",
                current_performance={"response_time_ms": metrics.total_time_ms},
                expected_performance={"response_time_ms": self.thresholds['max_response_time_ms']},
                impact_percentage=(metrics.total_time_ms - self.thresholds['max_response_time_ms']) / self.thresholds['max_response_time_ms'] * 100,
                affected_requests=[metrics.request_id],
                error_patterns=[],
                recommendations=[
                    "Optimize database queries in endpoint",
                    "Add response caching for frequent requests",
                    "Implement pagination for large datasets",
                    "Consider async processing for heavy operations",
                    "Review N+1 query problems"
                ],
                estimated_improvement={"response_time_reduction_percent": 40.0}
            )
            bottlenecks.append(bottleneck)
        
        # Authentication overhead detection
        if (metrics.auth_time_ms is not None and 
            metrics.auth_time_ms > self.thresholds['max_auth_time_ms']):
            bottleneck = APIBottleneck(
                bottleneck_id=f"auth_overhead_{int(time.time())}",
                endpoint_path=metrics.endpoint_path,
                method=metrics.method,
                category=metrics.category,
                bottleneck_type="auth_overhead",
                severity="medium",
                description=f"High authentication overhead: {metrics.auth_time_ms:.2f}ms",
                current_performance={"auth_time_ms": metrics.auth_time_ms},
                expected_performance={"auth_time_ms": self.thresholds['max_auth_time_ms']},
                impact_percentage=(metrics.auth_time_ms - self.thresholds['max_auth_time_ms']) / self.thresholds['max_auth_time_ms'] * 100,
                affected_requests=[metrics.request_id],
                error_patterns=[],
                recommendations=[
                    "Implement token caching",
                    "Optimize JWT validation process",
                    "Consider connection pooling for auth services",
                    "Review authentication middleware performance",
                    "Implement auth result caching"
                ],
                estimated_improvement={"auth_time_reduction_percent": 50.0}
            )
            bottlenecks.append(bottleneck)
        
        # Rate limiting detection
        if metrics.rate_limited:
            bottleneck = APIBottleneck(
                bottleneck_id=f"rate_limiting_{int(time.time())}",
                endpoint_path=metrics.endpoint_path,
                method=metrics.method,
                category=metrics.category,
                bottleneck_type="rate_limiting",
                severity="high",
                description="Rate limiting affecting API performance",
                current_performance={"rate_limited": 1.0},
                expected_performance={"rate_limited": 0.0},
                impact_percentage=100.0,
                affected_requests=[metrics.request_id],
                error_patterns=["rate_limit_exceeded"],
                recommendations=[
                    "Review rate limiting thresholds",
                    "Implement request batching",
                    "Add intelligent retry logic",
                    "Consider user-based rate limiting tiers",
                    "Implement request prioritization"
                ],
                estimated_improvement={"rate_limit_reduction_percent": 80.0}
            )
            bottlenecks.append(bottleneck)
        
        # Store bottlenecks
        for bottleneck in bottlenecks:
            self.bottlenecks.append(bottleneck)
            self.prometheus_metrics['api_bottlenecks'].labels(
                category=bottleneck.category.value,
                severity=bottleneck.severity
            ).inc()
    
    async def _monitoring_loop(self):
        """Background monitoring loop"""
        while self.is_monitoring:
            try:
                # Monitor endpoint patterns
                await self._monitor_endpoint_patterns()
                
                # Monitor error rates
                await self._monitor_error_rates()
                
                # Clean up old data
                await self._cleanup_old_data()
                
                await asyncio.sleep(self.monitoring_interval)
                
            except Exception as e:
                logger.error(f"Error in API monitoring loop: {e}")
                await asyncio.sleep(self.monitoring_interval)
    
    async def _monitor_endpoint_patterns(self):
        """Monitor endpoint patterns for optimization opportunities"""
        try:
            with self._lock:
                for endpoint, times in self.endpoint_patterns.items():
                    if len(times) > 10:  # Enough data points
                        avg_time = statistics.mean(times)
                        if avg_time > self.slow_request_threshold_ms:
                            logger.warning(f"Slow endpoint pattern: {endpoint} - avg {avg_time:.2f}ms")
                        
                        # Check for high variance (inconsistent performance)
                        if len(times) > 5:
                            variance = statistics.stdev(times)
                            if variance > avg_time * 0.5:  # High variance
                                logger.warning(f"Inconsistent endpoint performance: {endpoint} - stdev {variance:.2f}ms")
        
        except Exception as e:
            logger.error(f"Error monitoring endpoint patterns: {e}")
    
    async def _monitor_error_rates(self):
        """Monitor API error rates"""
        try:
            if not self.metrics_history:
                return
            
            # Calculate error rates for recent requests
            recent_window = datetime.utcnow() - timedelta(minutes=5)
            recent_metrics = [m for m in self.metrics_history if m.timestamp > recent_window]
            
            if len(recent_metrics) > 10:  # Enough data
                error_count = sum(1 for m in recent_metrics if not m.success)
                error_rate = (error_count / len(recent_metrics)) * 100
                
                if error_rate > self.thresholds['max_error_rate_percent']:
                    logger.warning(f"High API error rate detected: {error_rate:.2f}%")
        
        except Exception as e:
            logger.error(f"Error monitoring error rates: {e}")
    
    async def _cleanup_old_data(self):
        """Clean up old monitoring data"""
        cutoff_time = datetime.utcnow() - timedelta(hours=1)
        
        # Clean up old bottlenecks
        self.bottlenecks = [b for b in self.bottlenecks if b.timestamp > cutoff_time]
        
        # Clean up old requests
        old_requests = [req_id for req_id, metrics in self.current_requests.items() 
                       if metrics.timestamp < cutoff_time]
        for req_id in old_requests:
            del self.current_requests[req_id]
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """Get API performance summary"""
        if not self.metrics_history:
            return {}
        
        recent_metrics = list(self.metrics_history)[-100:]  # Last 100 requests
        
        # Calculate averages
        avg_response_time = statistics.mean([m.total_time_ms for m in recent_metrics])
        success_rate = sum(1 for m in recent_metrics if m.success) / len(recent_metrics) * 100
        
        # Calculate auth overhead
        auth_times = [m.auth_time_ms for m in recent_metrics if m.auth_time_ms is not None]
        avg_auth_time = statistics.mean(auth_times) if auth_times else 0.0
        
        # Category breakdown
        category_breakdown = defaultdict(list)
        for metric in recent_metrics:
            category_breakdown[metric.category.value].append(metric)
        
        # Method breakdown
        method_breakdown = defaultdict(list)
        for metric in recent_metrics:
            method_breakdown[metric.method.value].append(metric)
        
        return {
            "overall_performance": {
                "average_response_time_ms": avg_response_time,
                "success_rate_percent": success_rate,
                "total_requests": len(recent_metrics),
                "average_auth_time_ms": avg_auth_time
            },
            "category_breakdown": {
                category: {
                    "request_count": len(metrics),
                    "avg_response_time_ms": statistics.mean([m.total_time_ms for m in metrics]),
                    "success_rate_percent": sum(1 for m in metrics if m.success) / len(metrics) * 100
                }
                for category, metrics in category_breakdown.items()
            },
            "method_breakdown": {
                method: {
                    "request_count": len(metrics),
                    "avg_response_time_ms": statistics.mean([m.total_time_ms for m in metrics])
                }
                for method, metrics in method_breakdown.items()
            },
            "slow_requests_count": len(self.slow_requests),
            "active_bottlenecks": len([b for b in self.bottlenecks if b.timestamp > datetime.utcnow() - timedelta(minutes=5)]),
            "timestamp": datetime.utcnow().isoformat()
        }
    
    def get_bottleneck_report(self) -> List[Dict[str, Any]]:
        """Get detailed bottleneck report"""
        return [
            {
                "bottleneck_id": b.bottleneck_id,
                "endpoint_path": b.endpoint_path,
                "method": b.method.value,
                "category": b.category.value,
                "type": b.bottleneck_type,
                "severity": b.severity,
                "description": b.description,
                "impact_percentage": b.impact_percentage,
                "affected_requests": b.affected_requests,
                "error_patterns": b.error_patterns,
                "recommendations": b.recommendations,
                "estimated_improvement": b.estimated_improvement,
                "timestamp": b.timestamp.isoformat()
            }
            for b in self.bottlenecks
        ]


class APIProfiler:
    """Simplified API profiler interface"""
    
    def __init__(self):
        self.profiler = APIEndpointProfiler()
    
    async def start_monitoring(self):
        """Start API monitoring"""
        return await self.profiler.start_monitoring()
    
    async def stop_monitoring(self):
        """Stop API monitoring"""
        return await self.profiler.stop_monitoring()
    
    async def profile_request(self,
                            endpoint_path: str,
                            method: str,
                            category: str,
                            api_func: Callable,
                            *args, **kwargs):
        """Profile an API request"""
        # Convert strings to enums
        http_method = HTTPMethod(method.upper())
        api_category = APICategory(category.lower())
        
        # Create request metadata
        request_metadata = APIRequestMetadata(
            endpoint_path=endpoint_path,
            method=http_method,
            api_type=APIType.REST,  # Default
            category=api_category,
            authentication_type=AuthenticationType.BEARER_TOKEN,  # Default
            request_size_bytes=0,  # Would be calculated from actual request
            headers_count=0,
            query_params_count=0,
            path_params_count=0
        )
        
        return await self.profiler.profile_api_request(
            request_metadata, api_func, *args, **kwargs
        )


def create_api_endpoint_profiler(
    monitoring_interval: float = 1.0,
    enable_detailed_timing: bool = True,
    enable_rate_limit_tracking: bool = True,
    slow_request_threshold_ms: float = 1000.0,
    start_monitoring: bool = False
) -> APIEndpointProfiler:
    """
    Factory function to create API endpoint profiler
    
    Args:
        monitoring_interval: Monitoring interval in seconds
        enable_detailed_timing: Enable detailed request timing breakdown
        enable_rate_limit_tracking: Enable rate limiting tracking
        slow_request_threshold_ms: Threshold for slow request detection
        start_monitoring: Start monitoring immediately
    
    Returns:
        APIEndpointProfiler: Configured API profiler instance
    """
    profiler = APIEndpointProfiler(
        monitoring_interval=monitoring_interval,
        enable_detailed_timing=enable_detailed_timing,
        enable_rate_limit_tracking=enable_rate_limit_tracking,
        slow_request_threshold_ms=slow_request_threshold_ms
    )
    
    if start_monitoring:
        import asyncio
        try:
            loop = asyncio.get_event_loop()
            loop.create_task(profiler.start_monitoring())
        except RuntimeError:
            logger.warning("No event loop running, monitoring will need to be started manually")
    
    return profiler


# Example usage for Creator Economy platform
async def example_creator_api_profiling():
    """Example of profiling Creator Economy API endpoints"""
    profiler = create_api_endpoint_profiler(start_monitoring=True)
    
    # Example: Profile creator profile API
    async def get_creator_profile(creator_id: str):
        # Simulate API call with database lookup
        await asyncio.sleep(0.05)  # Simulate database time
        return {
            "status_code": 200,
            "data": {
                "id": creator_id,
                "name": "John Creator",
                "followers": 10000,
                "category": "gaming"
            },
            "headers": {"content-type": "application/json"},
            "content_type": "application/json"
        }
    
    request_metadata = APIRequestMetadata(
        endpoint_path="/api/v1/creators/123/profile",
        method=HTTPMethod.GET,
        api_type=APIType.REST,
        category=APICategory.CREATOR_PROFILES,
        authentication_type=AuthenticationType.BEARER_TOKEN,
        request_size_bytes=256,
        headers_count=5,
        query_params_count=2,
        path_params_count=1,
        user_id="user_456",
        user_role="creator"
    )
    
    metrics = await profiler.profile_api_request(
        request_metadata,
        get_creator_profile,
        "123"
    )
    
    print(f"API profiling completed:")
    print(f"- Response time: {metrics.total_time_ms:.2f}ms")
    print(f"- Auth time: {metrics.auth_time_ms:.2f}ms" if metrics.auth_time_ms else "- No auth timing")
    print(f"- Processing time: {metrics.processing_time_ms:.2f}ms" if metrics.processing_time_ms else "- No processing timing")
    print(f"- Success: {metrics.success}")
    
    # Get performance summary
    summary = profiler.get_performance_summary()
    print(f"Performance summary: {json.dumps(summary, indent=2)}")
    
    await profiler.stop_monitoring()


if __name__ == "__main__":
    asyncio.run(example_creator_api_profiling())