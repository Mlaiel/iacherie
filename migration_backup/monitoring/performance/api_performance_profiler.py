"""
⚠️ CONFIDENTIEL - Ainflue Creator Platform ⚠️

API Performance Profiler - Enterprise Performance Monitoring
Advanced API performance profiling for Creator Economy endpoints

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

🚨 PROTECTION INTELLECTUELLE:
- Code propriétaire de Fahed Mlaiel
- Utilisation commerciale INTERDITE sans autorisation écrite
- Reverse engineering STRICTEMENT INTERDIT
- Distribution INTERDITE sans licence explicite
- Violation = Poursuites judiciaires automatiques
"""

import time
import asyncio
import json
import statistics
from typing import Dict, List, Optional, Any, Tuple, Callable
from dataclasses import dataclass, asdict, field
from datetime import datetime, timedelta
import logging
from collections import defaultdict, deque
import threading
from prometheus_client import Gauge, Counter, Histogram, Summary
import traceback
import functools
import inspect
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
import httpx
from urllib.parse import urlparse
import re

logger = logging.getLogger(__name__)

@dataclass
class ApiEndpointMetrics:
    """API endpoint performance metrics"""
    endpoint: str
    method: str
    response_time_ms: float
    status_code: int
    request_size_bytes: int
    response_size_bytes: int
    timestamp: datetime
    user_id: Optional[str] = None
    user_agent: Optional[str] = None
    ip_address: Optional[str] = None
    query_params: Optional[Dict[str, Any]] = None
    headers: Optional[Dict[str, str]] = None
    error_message: Optional[str] = None
    trace_id: Optional[str] = None

@dataclass
class ApiLatencyDistribution:
    """API latency distribution metrics"""
    endpoint: str
    method: str
    p50_ms: float
    p90_ms: float
    p95_ms: float
    p99_ms: float
    avg_ms: float
    min_ms: float
    max_ms: float
    request_count: int
    error_count: int
    error_rate: float
    timestamp: datetime

@dataclass
class RateLimitMetrics:
    """Rate limiting metrics"""
    endpoint: str
    client_id: str
    requests_per_minute: int
    limit_per_minute: int
    remaining_requests: int
    reset_time: datetime
    blocked_requests: int
    timestamp: datetime

@dataclass
class AuthenticationMetrics:
    """Authentication performance metrics"""
    auth_method: str  # jwt, oauth, api_key
    validation_time_ms: float
    success: bool
    user_id: Optional[str]
    client_id: Optional[str]
    error_reason: Optional[str]
    timestamp: datetime

@dataclass
class PayloadAnalysis:
    """Request/response payload analysis"""
    endpoint: str
    method: str
    request_size_distribution: Dict[str, float]  # percentiles
    response_size_distribution: Dict[str, float]
    avg_request_size: float
    avg_response_size: float
    large_payload_count: int  # > 1MB
    timestamp: datetime

class ApiPerformanceProfiler:
    """
    Enterprise-grade API performance profiler
    Tracks endpoint latency, throughput, rate limiting, and payload optimization
    """
    
    def __init__(self,
                 large_payload_threshold: int = 1024 * 1024,  # 1MB
                 slow_request_threshold_ms: float = 1000,
                 rate_limit_window_minutes: int = 1,
                 enable_payload_analysis: bool = True):
        """
        Initialize API performance profiler
        
        Args:
            large_payload_threshold: Threshold for large payload detection (bytes)
            slow_request_threshold_ms: Slow request threshold in milliseconds
            rate_limit_window_minutes: Rate limiting window in minutes
            enable_payload_analysis: Enable detailed payload analysis
        """
        self.large_payload_threshold = large_payload_threshold
        self.slow_request_threshold_ms = slow_request_threshold_ms
        self.rate_limit_window_minutes = rate_limit_window_minutes
        self.enable_payload_analysis = enable_payload_analysis
        
        # Metrics storage
        self.endpoint_metrics: deque = deque(maxlen=50000)
        self.latency_distributions: Dict[str, deque] = defaultdict(lambda: deque(maxlen=1000))
        self.rate_limit_metrics: Dict[str, deque] = defaultdict(lambda: deque(maxlen=1000))
        self.auth_metrics: deque = deque(maxlen=10000)
        self.payload_analysis: Dict[str, deque] = defaultdict(lambda: deque(maxlen=1000))
        
        # Real-time tracking
        self.active_requests: Dict[str, Dict] = {}
        self.request_latencies: Dict[str, deque] = defaultdict(lambda: deque(maxlen=1000))
        self.endpoint_errors: Dict[str, int] = defaultdict(int)
        
        # Rate limiting state
        self.rate_limit_buckets: Dict[str, Dict] = defaultdict(lambda: {
            'requests': deque(maxlen=1000),
            'blocked': 0,
            'limit': 60  # Default 60 requests per minute
        })
        
        # Prometheus metrics
        self._init_prometheus_metrics()
        
        # Monitoring state
        self.monitoring_active = False
        self._analysis_task = None
    
    def _init_prometheus_metrics(self):
        """Initialize Prometheus metrics"""
        self.request_duration_histogram = Histogram(
            'api_request_duration_seconds',
            'API request duration',
            ['endpoint', 'method', 'status_code'],
            buckets=[0.01, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0, 30.0]
        )
        
        self.request_size_histogram = Histogram(
            'api_request_size_bytes',
            'API request payload size',
            ['endpoint', 'method'],
            buckets=[100, 1024, 10240, 102400, 1048576, 10485760]  # 100B to 10MB
        )
        
        self.response_size_histogram = Histogram(
            'api_response_size_bytes',
            'API response payload size',
            ['endpoint', 'method', 'status_code'],
            buckets=[100, 1024, 10240, 102400, 1048576, 10485760]
        )
        
        self.requests_total_counter = Counter(
            'api_requests_total',
            'Total API requests',
            ['endpoint', 'method', 'status_code']
        )
        
        self.rate_limit_counter = Counter(
            'api_rate_limit_hits_total',
            'Total rate limit hits',
            ['endpoint', 'client_id']
        )
        
        self.auth_duration_histogram = Histogram(
            'api_auth_duration_seconds',
            'API authentication duration',
            ['auth_method', 'success']
        )
        
        self.concurrent_requests_gauge = Gauge(
            'api_concurrent_requests',
            'Current concurrent requests',
            ['endpoint']
        )
        
        self.slow_requests_counter = Counter(
            'api_slow_requests_total',
            'Total slow requests',
            ['endpoint', 'method']
        )
    
    def create_fastapi_middleware(self):
        """Create FastAPI middleware for automatic profiling"""
        
        class ApiProfilingMiddleware(BaseHTTPMiddleware):
            def __init__(self, app, profiler: 'ApiPerformanceProfiler'):
                super().__init__(app)
                self.profiler = profiler
            
            async def dispatch(self, request: Request, call_next: Callable):
                # Start request tracking
                start_time = time.time()
                request_id = self._generate_request_id()
                endpoint = self._normalize_endpoint(request.url.path)
                method = request.method
                
                # Track concurrent requests
                self.profiler._track_request_start(endpoint, request_id)
                
                # Get request size
                request_size = await self._get_request_size(request)
                
                try:
                    # Process request
                    response = await call_next(request)
                    
                    # Calculate metrics
                    end_time = time.time()
                    response_time_ms = (end_time - start_time) * 1000
                    
                    # Get response size
                    response_size = self._get_response_size(response)
                    
                    # Create metrics
                    metrics = ApiEndpointMetrics(
                        endpoint=endpoint,
                        method=method,
                        response_time_ms=response_time_ms,
                        status_code=response.status_code,
                        request_size_bytes=request_size,
                        response_size_bytes=response_size,
                        timestamp=datetime.utcnow(),
                        user_id=self._extract_user_id(request),
                        user_agent=request.headers.get('user-agent'),
                        ip_address=self._get_client_ip(request),
                        query_params=dict(request.query_params),
                        trace_id=request_id
                    )
                    
                    # Record metrics
                    self.profiler.record_request_metrics(metrics)
                    
                    return response
                    
                except Exception as e:
                    # Handle errors
                    end_time = time.time()
                    response_time_ms = (end_time - start_time) * 1000
                    
                    error_metrics = ApiEndpointMetrics(
                        endpoint=endpoint,
                        method=method,
                        response_time_ms=response_time_ms,
                        status_code=500,
                        request_size_bytes=request_size,
                        response_size_bytes=0,
                        timestamp=datetime.utcnow(),
                        error_message=str(e),
                        trace_id=request_id
                    )
                    
                    self.profiler.record_request_metrics(error_metrics)
                    raise
                
                finally:
                    # Stop request tracking
                    self.profiler._track_request_end(endpoint, request_id)
            
            def _generate_request_id(self) -> str:
                import uuid
                return str(uuid.uuid4())
            
            def _normalize_endpoint(self, path: str) -> str:
                """Normalize endpoint path for metrics"""
                # Replace path parameters with placeholders
                path = re.sub(r'/\d+', '/{id}', path)
                path = re.sub(r'/[a-f0-9-]{36}', '/{uuid}', path)
                return path
            
            async def _get_request_size(self, request: Request) -> int:
                """Get request payload size"""
                try:
                    body = await request.body()
                    return len(body)
                except:
                    return 0
            
            def _get_response_size(self, response: Response) -> int:
                """Get response payload size"""
                try:
                    if hasattr(response, 'body'):
                        return len(response.body)
                    return 0
                except:
                    return 0
            
            def _extract_user_id(self, request: Request) -> Optional[str]:
                """Extract user ID from request"""
                # Try JWT token
                auth_header = request.headers.get('authorization', '')
                if auth_header.startswith('Bearer '):
                    try:
                        import jwt
                        token = auth_header[7:]
                        decoded = jwt.decode(token, options={"verify_signature": False})
                        return decoded.get('sub') or decoded.get('user_id')
                    except:
                        pass
                
                # Try query parameter
                return request.query_params.get('user_id')
            
            def _get_client_ip(self, request: Request) -> str:
                """Get client IP address"""
                # Check for forwarded headers
                forwarded_for = request.headers.get('x-forwarded-for')
                if forwarded_for:
                    return forwarded_for.split(',')[0].strip()
                
                real_ip = request.headers.get('x-real-ip')
                if real_ip:
                    return real_ip
                
                return request.client.host if request.client else 'unknown'
        
        return ApiProfilingMiddleware
    
    def _track_request_start(self, endpoint: str, request_id: str):
        """Track request start for concurrent monitoring"""
        if endpoint not in self.active_requests:
            self.active_requests[endpoint] = {}
        
        self.active_requests[endpoint][request_id] = {
            'start_time': time.time(),
            'timestamp': datetime.utcnow()
        }
        
        # Update concurrent requests gauge
        self.concurrent_requests_gauge.labels(endpoint=endpoint).set(
            len(self.active_requests[endpoint])
        )
    
    def _track_request_end(self, endpoint: str, request_id: str):
        """Track request end"""
        if endpoint in self.active_requests and request_id in self.active_requests[endpoint]:
            del self.active_requests[endpoint][request_id]
            
            # Update concurrent requests gauge
            self.concurrent_requests_gauge.labels(endpoint=endpoint).set(
                len(self.active_requests[endpoint])
            )
    
    def record_request_metrics(self, metrics: ApiEndpointMetrics):
        """Record API request metrics"""
        # Store metrics
        self.endpoint_metrics.append(metrics)
        
        # Track latencies for distribution calculation
        endpoint_key = f"{metrics.method}:{metrics.endpoint}"
        self.request_latencies[endpoint_key].append(metrics.response_time_ms)
        
        # Track errors
        if metrics.status_code >= 400:
            self.endpoint_errors[endpoint_key] += 1
        
        # Update Prometheus metrics
        self.request_duration_histogram.labels(
            endpoint=metrics.endpoint,
            method=metrics.method,
            status_code=str(metrics.status_code)
        ).observe(metrics.response_time_ms / 1000)
        
        self.request_size_histogram.labels(
            endpoint=metrics.endpoint,
            method=metrics.method
        ).observe(metrics.request_size_bytes)
        
        self.response_size_histogram.labels(
            endpoint=metrics.endpoint,
            method=metrics.method,
            status_code=str(metrics.status_code)
        ).observe(metrics.response_size_bytes)
        
        self.requests_total_counter.labels(
            endpoint=metrics.endpoint,
            method=metrics.method,
            status_code=str(metrics.status_code)
        ).inc()
        
        # Track slow requests
        if metrics.response_time_ms > self.slow_request_threshold_ms:
            self.slow_requests_counter.labels(
                endpoint=metrics.endpoint,
                method=metrics.method
            ).inc()
        
        # Payload analysis
        if self.enable_payload_analysis:
            self._analyze_payload(metrics)
    
    def record_auth_metrics(self, metrics: AuthenticationMetrics):
        """Record authentication metrics"""
        self.auth_metrics.append(metrics)
        
        # Update Prometheus metrics
        self.auth_duration_histogram.labels(
            auth_method=metrics.auth_method,
            success=str(metrics.success)
        ).observe(metrics.validation_time_ms / 1000)
    
    def record_rate_limit_metrics(self, metrics: RateLimitMetrics):
        """Record rate limiting metrics"""
        endpoint_key = f"{metrics.endpoint}:{metrics.client_id}"
        self.rate_limit_metrics[endpoint_key].append(metrics)
        
        if metrics.blocked_requests > 0:
            self.rate_limit_counter.labels(
                endpoint=metrics.endpoint,
                client_id=metrics.client_id
            ).inc(metrics.blocked_requests)
    
    def _analyze_payload(self, metrics: ApiEndpointMetrics):
        """Analyze request/response payload patterns"""
        endpoint_key = f"{metrics.method}:{metrics.endpoint}"
        
        # Track large payloads
        large_payload = (
            metrics.request_size_bytes > self.large_payload_threshold or
            metrics.response_size_bytes > self.large_payload_threshold
        )
        
        if large_payload:
            logger.warning(
                f"Large payload detected: {endpoint_key} "
                f"req={metrics.request_size_bytes}B resp={metrics.response_size_bytes}B"
            )
    
    def calculate_latency_distributions(self, minutes: int = 5) -> Dict[str, ApiLatencyDistribution]:
        """Calculate latency distributions for endpoints"""
        cutoff_time = datetime.utcnow() - timedelta(minutes=minutes)
        recent_metrics = [m for m in self.endpoint_metrics if m.timestamp >= cutoff_time]
        
        # Group by endpoint
        by_endpoint = defaultdict(list)
        for metric in recent_metrics:
            endpoint_key = f"{metric.method}:{metric.endpoint}"
            by_endpoint[endpoint_key].append(metric)
        
        distributions = {}
        
        for endpoint_key, metrics_list in by_endpoint.items():
            if not metrics_list:
                continue
            
            method, endpoint = endpoint_key.split(':', 1)
            latencies = [m.response_time_ms for m in metrics_list]
            errors = [m for m in metrics_list if m.status_code >= 400]
            
            if len(latencies) < 2:
                continue
            
            distribution = ApiLatencyDistribution(
                endpoint=endpoint,
                method=method,
                p50_ms=statistics.quantiles(latencies, n=2)[0] if len(latencies) >= 2 else latencies[0],
                p90_ms=statistics.quantiles(latencies, n=10)[8] if len(latencies) >= 10 else max(latencies),
                p95_ms=statistics.quantiles(latencies, n=20)[18] if len(latencies) >= 20 else max(latencies),
                p99_ms=statistics.quantiles(latencies, n=100)[98] if len(latencies) >= 100 else max(latencies),
                avg_ms=statistics.mean(latencies),
                min_ms=min(latencies),
                max_ms=max(latencies),
                request_count=len(metrics_list),
                error_count=len(errors),
                error_rate=len(errors) / len(metrics_list) * 100,
                timestamp=datetime.utcnow()
            )
            
            distributions[endpoint_key] = distribution
            self.latency_distributions[endpoint_key].append(distribution)
        
        return distributions
    
    def get_top_slow_endpoints(self, limit: int = 10, minutes: int = 30) -> List[Dict[str, Any]]:
        """Get top slow endpoints"""
        distributions = self.calculate_latency_distributions(minutes)
        
        # Sort by P95 latency
        sorted_endpoints = sorted(
            distributions.values(),
            key=lambda x: x.p95_ms,
            reverse=True
        )
        
        return [
            {
                'endpoint': f"{dist.method} {dist.endpoint}",
                'p95_ms': dist.p95_ms,
                'avg_ms': dist.avg_ms,
                'request_count': dist.request_count,
                'error_rate': dist.error_rate
            }
            for dist in sorted_endpoints[:limit]
        ]
    
    def get_error_analysis(self, minutes: int = 30) -> Dict[str, Any]:
        """Get error analysis for endpoints"""
        cutoff_time = datetime.utcnow() - timedelta(minutes=minutes)
        recent_metrics = [m for m in self.endpoint_metrics if m.timestamp >= cutoff_time]
        
        total_requests = len(recent_metrics)
        error_requests = [m for m in recent_metrics if m.status_code >= 400]
        
        # Group errors by status code
        by_status = defaultdict(list)
        for error in error_requests:
            by_status[error.status_code].append(error)
        
        # Group errors by endpoint
        by_endpoint = defaultdict(list)
        for error in error_requests:
            endpoint_key = f"{error.method} {error.endpoint}"
            by_endpoint[endpoint_key].append(error)
        
        return {
            'time_window_minutes': minutes,
            'total_requests': total_requests,
            'total_errors': len(error_requests),
            'error_rate': len(error_requests) / total_requests * 100 if total_requests > 0 else 0,
            'errors_by_status': {
                status: {
                    'count': len(errors),
                    'percentage': len(errors) / len(error_requests) * 100 if error_requests else 0,
                    'sample_messages': list(set(e.error_message for e in errors[:5] if e.error_message))
                }
                for status, errors in by_status.items()
            },
            'errors_by_endpoint': {
                endpoint: {
                    'count': len(errors),
                    'error_rate': len(errors) / len([m for m in recent_metrics 
                                                   if f"{m.method} {m.endpoint}" == endpoint]) * 100
                }
                for endpoint, errors in by_endpoint.items()
            }
        }
    
    def get_throughput_analysis(self, minutes: int = 30) -> Dict[str, Any]:
        """Get throughput analysis"""
        cutoff_time = datetime.utcnow() - timedelta(minutes=minutes)
        recent_metrics = [m for m in self.endpoint_metrics if m.timestamp >= cutoff_time]
        
        if not recent_metrics:
            return {'message': 'No data available for the specified time period'}
        
        # Group by time buckets (1-minute intervals)
        time_buckets = defaultdict(int)
        
        for metric in recent_metrics:
            # Round to minute
            bucket_time = metric.timestamp.replace(second=0, microsecond=0)
            time_buckets[bucket_time] += 1
        
        if time_buckets:
            throughput_values = list(time_buckets.values())
            avg_rps = statistics.mean(throughput_values) / 60  # Convert to RPS
            max_rps = max(throughput_values) / 60
            min_rps = min(throughput_values) / 60
        else:
            avg_rps = max_rps = min_rps = 0
        
        # Group by endpoint
        by_endpoint = defaultdict(int)
        for metric in recent_metrics:
            endpoint_key = f"{metric.method} {metric.endpoint}"
            by_endpoint[endpoint_key] += 1
        
        return {
            'time_window_minutes': minutes,
            'total_requests': len(recent_metrics),
            'avg_requests_per_second': avg_rps,
            'peak_requests_per_second': max_rps,
            'min_requests_per_second': min_rps,
            'top_endpoints': [
                {'endpoint': endpoint, 'requests': count, 'rps': count / (minutes * 60)}
                for endpoint, count in sorted(by_endpoint.items(), key=lambda x: x[1], reverse=True)[:10]
            ]
        }
    
    def get_payload_optimization_recommendations(self) -> List[Dict[str, Any]]:
        """Get payload optimization recommendations"""
        recommendations = []
        
        # Analyze recent metrics for large payloads
        cutoff_time = datetime.utcnow() - timedelta(hours=1)
        recent_metrics = [m for m in self.endpoint_metrics if m.timestamp >= cutoff_time]
        
        # Group by endpoint
        by_endpoint = defaultdict(list)
        for metric in recent_metrics:
            endpoint_key = f"{metric.method} {metric.endpoint}"
            by_endpoint[endpoint_key].append(metric)
        
        for endpoint_key, metrics_list in by_endpoint.items():
            if not metrics_list:
                continue
            
            # Analyze request sizes
            request_sizes = [m.request_size_bytes for m in metrics_list]
            response_sizes = [m.response_size_bytes for m in metrics_list]
            
            avg_req_size = statistics.mean(request_sizes) if request_sizes else 0
            avg_resp_size = statistics.mean(response_sizes) if response_sizes else 0
            
            # Large request payloads
            if avg_req_size > self.large_payload_threshold / 2:  # 512KB
                recommendations.append({
                    'endpoint': endpoint_key,
                    'type': 'large_request_payload',
                    'priority': 'medium',
                    'avg_size_mb': avg_req_size / (1024 * 1024),
                    'suggestion': 'Consider request compression or pagination'
                })
            
            # Large response payloads
            if avg_resp_size > self.large_payload_threshold / 2:  # 512KB
                recommendations.append({
                    'endpoint': endpoint_key,
                    'type': 'large_response_payload',
                    'priority': 'medium',
                    'avg_size_mb': avg_resp_size / (1024 * 1024),
                    'suggestion': 'Consider response compression, pagination, or field selection'
                })
        
        return recommendations
    
    async def start_monitoring(self):
        """Start continuous analysis"""
        if self.monitoring_active:
            logger.warning("API monitoring already active")
            return
        
        self.monitoring_active = True
        self._analysis_task = asyncio.create_task(self._analysis_loop())
        logger.info("API performance monitoring started")
    
    async def stop_monitoring(self):
        """Stop monitoring"""
        self.monitoring_active = False
        if self._analysis_task:
            self._analysis_task.cancel()
            try:
                await self._analysis_task
            except asyncio.CancelledError:
                pass
        logger.info("API performance monitoring stopped")
    
    async def _analysis_loop(self):
        """Continuous analysis loop"""
        while self.monitoring_active:
            try:
                # Calculate latency distributions every 5 minutes
                self.calculate_latency_distributions(5)
                
                # Log performance warnings
                await self._check_performance_alerts()
                
                await asyncio.sleep(300)  # 5 minutes
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in API analysis loop: {e}")
                await asyncio.sleep(300)
    
    async def _check_performance_alerts(self):
        """Check for performance alerts"""
        # Check for high error rates
        error_analysis = self.get_error_analysis(5)
        if error_analysis['error_rate'] > 5:  # 5% error rate threshold
            logger.warning(f"High error rate detected: {error_analysis['error_rate']:.1f}%")
        
        # Check for slow endpoints
        slow_endpoints = self.get_top_slow_endpoints(5, 5)
        for endpoint in slow_endpoints:
            if endpoint['p95_ms'] > self.slow_request_threshold_ms:
                logger.warning(
                    f"Slow endpoint detected: {endpoint['endpoint']} "
                    f"P95={endpoint['p95_ms']:.1f}ms"
                )