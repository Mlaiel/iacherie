"""API Performance SLA Monitoring System
Advanced SLA tracking for API response times, throughput, availability, and performance metrics.

⚠️ PROPRIETARY CODE - Fahed Mlaiel (mlaiel@live.de)
© 2025 Fahed Mlaiel. All rights reserved.
Unauthorized use, distribution, or modification is strictly prohibited.
"""

import asyncio
import logging
import statistics
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union
from collections import deque, defaultdict
import json
import time
from enum import Enum

class APIEndpointCategory(Enum):
    """API endpoint categories for SLA tracking"""
    CREATOR_MANAGEMENT = "creator_management"
    CONTENT_PROCESSING = "content_processing"
    MONETIZATION = "monetization"
    COLLABORATION = "collaboration"
    ANALYTICS = "analytics"
    AUTHENTICATION = "authentication"
    NOTIFICATION = "notification"
    SEARCH = "search"
    UPLOAD = "upload"
    STREAMING = "streaming"

class HTTPMethod(Enum):
    """HTTP methods for API tracking"""
    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    DELETE = "DELETE"
    PATCH = "PATCH"
    OPTIONS = "OPTIONS"
    HEAD = "HEAD"

class APIErrorType(Enum):
    """Types of API errors for tracking"""
    TIMEOUT = "timeout"
    SERVER_ERROR = "server_error"
    CLIENT_ERROR = "client_error"
    RATE_LIMIT = "rate_limit"
    AUTHENTICATION = "authentication"
    AUTHORIZATION = "authorization"
    VALIDATION = "validation"
    NETWORK = "network"

@dataclass
class APIPerformanceMetric:
    """API performance metric with SLA targets"""
    metric_name: str
    target_value: float
    current_value: float = 0.0
    unit: str = ""
    endpoint_category: APIEndpointCategory = APIEndpointCategory.CREATOR_MANAGEMENT
    http_method: HTTPMethod = HTTPMethod.GET
    measurement_window: int = 300  # 5 minutes default
    last_measurement: datetime = field(default_factory=datetime.now)
    violation_count: int = 0
    success_rate: float = 100.0

@dataclass
class APIPerformanceSLATargets:
    """Comprehensive API Performance SLA targets"""
    # Response Time SLA
    api_response_time_p95_ms: float = 200.0  # <200ms P95 response time
    api_response_time_p99_ms: float = 500.0  # <500ms P99 response time
    api_response_time_avg_ms: float = 100.0  # <100ms average response time
    
    # Throughput SLA
    api_throughput_rps: float = 10000.0  # >10K requests per second
    peak_throughput_rps: float = 25000.0  # >25K RPS peak capacity
    concurrent_connections: int = 5000  # 5000 concurrent connections
    
    # Availability SLA
    api_availability_percentage: float = 99.99  # 99.99% availability
    api_uptime_percentage: float = 99.99  # 99.99% uptime
    max_downtime_minutes_monthly: float = 43.2  # 43.2 minutes max downtime/month
    
    # Error Rate SLA
    api_error_rate_percentage: float = 0.1  # <0.1% error rate
    server_error_rate_percentage: float = 0.05  # <0.05% 5xx error rate
    client_error_rate_percentage: float = 1.0  # <1% 4xx error rate
    
    # Rate Limiting SLA
    rate_limit_compliance_percentage: float = 99.9  # 99.9% rate limit compliance
    rate_limit_burst_capacity: int = 1000  # 1000 requests burst capacity
    rate_limit_window_seconds: int = 60  # 60 second rate limit window
    
    # Scalability SLA
    auto_scaling_response_seconds: float = 30.0  # <30s auto-scaling response
    load_balancer_response_ms: float = 10.0  # <10ms load balancer response
    cdn_cache_hit_ratio: float = 90.0  # >90% CDN cache hit ratio
    
    # Security SLA
    ssl_handshake_ms: float = 100.0  # <100ms SSL handshake
    authentication_response_ms: float = 50.0  # <50ms authentication
    authorization_response_ms: float = 25.0  # <25ms authorization
    
    # Data Transfer SLA
    upload_speed_mbps: float = 100.0  # >100 Mbps upload speed
    download_speed_mbps: float = 500.0  # >500 Mbps download speed
    compression_ratio: float = 70.0  # >70% compression ratio

class APIPerformanceSLA:
    """
    Advanced API Performance SLA monitoring system
    Tracks response times, throughput, availability, and error rates for all API endpoints
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.targets = APIPerformanceSLATargets()
        self.metrics: Dict[str, APIPerformanceMetric] = {}
        self.measurements: Dict[str, deque] = defaultdict(lambda: deque(maxlen=1000))
        self.alerts: List[Dict[str, Any]] = []
        
        # API performance tracking
        self.endpoint_performance: Dict[str, Dict[str, Any]] = {}
        self.request_tracking: Dict[str, Dict[str, Any]] = {}
        self.error_tracking: Dict[str, Dict[str, Any]] = {}
        self.rate_limit_tracking: Dict[str, Dict[str, Any]] = {}
        
        # Performance monitoring
        self.response_times: Dict[str, deque] = defaultdict(lambda: deque(maxlen=1000))
        self.throughput_tracking: Dict[str, deque] = defaultdict(lambda: deque(maxlen=100))
        self.error_rates: Dict[str, deque] = defaultdict(lambda: deque(maxlen=100))
        self.availability_tracking: Dict[str, deque] = defaultdict(lambda: deque(maxlen=100))
        
        self._setup_default_metrics()
        
    def _setup_default_metrics(self):
        """Initialize default API performance metrics"""
        default_metrics = [
            ("api_response_time", self.targets.api_response_time_p95_ms, "milliseconds", APIEndpointCategory.CREATOR_MANAGEMENT, HTTPMethod.GET),
            ("api_throughput", self.targets.api_throughput_rps, "requests_per_second", APIEndpointCategory.CREATOR_MANAGEMENT, HTTPMethod.GET),
            ("api_availability", self.targets.api_availability_percentage, "percentage", APIEndpointCategory.CREATOR_MANAGEMENT, HTTPMethod.GET),
            ("api_error_rate", self.targets.api_error_rate_percentage, "percentage", APIEndpointCategory.CREATOR_MANAGEMENT, HTTPMethod.GET),
            ("rate_limit_compliance", self.targets.rate_limit_compliance_percentage, "percentage", APIEndpointCategory.CREATOR_MANAGEMENT, HTTPMethod.GET),
            ("ssl_handshake_time", self.targets.ssl_handshake_ms, "milliseconds", APIEndpointCategory.AUTHENTICATION, HTTPMethod.POST),
        ]
        
        for metric_name, target, unit, category, method in default_metrics:
            self.metrics[metric_name] = APIPerformanceMetric(
                metric_name=metric_name,
                target_value=target,
                unit=unit,
                endpoint_category=category,
                http_method=method
            )
    
    async def track_api_request(self, request_id: str, endpoint: str, method: HTTPMethod,
                              category: APIEndpointCategory, start_time: datetime,
                              end_time: datetime, status_code: int, response_size_bytes: int,
                              user_id: Optional[str] = None, error_type: Optional[APIErrorType] = None) -> Dict[str, Any]:
        """Track individual API request performance"""
        try:
            response_time = (end_time - start_time).total_seconds() * 1000  # Convert to milliseconds
            is_success = 200 <= status_code < 300
            is_client_error = 400 <= status_code < 500
            is_server_error = status_code >= 500
            
            # Update response time metric
            response_metric = self.metrics["api_response_time"]
            response_metric.current_value = response_time
            response_metric.last_measurement = end_time
            response_metric.endpoint_category = category
            response_metric.http_method = method
            
            # Check response time SLA compliance
            response_compliant = response_time <= self.targets.api_response_time_p95_ms
            
            if not response_compliant:
                response_metric.violation_count += 1
                await self._generate_alert(
                    "API Response Time SLA Violation",
                    f"Request {request_id} to {endpoint} took {response_time:.2f}ms (target: {self.targets.api_response_time_p95_ms}ms)",
                    "medium",
                    {
                        "request_id": request_id,
                        "endpoint": endpoint,
                        "method": method.value,
                        "category": category.value,
                        "response_time": response_time,
                        "status_code": status_code,
                        "user_id": user_id
                    }
                )
            
            # Track errors
            if is_server_error:
                await self._generate_alert(
                    "API Server Error",
                    f"Request {request_id} to {endpoint} returned {status_code}",
                    "critical" if status_code >= 500 else "high",
                    {
                        "request_id": request_id,
                        "endpoint": endpoint,
                        "method": method.value,
                        "status_code": status_code,
                        "error_type": error_type.value if error_type else "unknown",
                        "user_id": user_id
                    }
                )
            
            # Store measurements
            self.measurements["api_response_time"].append({
                "timestamp": end_time,
                "value": response_time,
                "request_id": request_id,
                "endpoint": endpoint,
                "method": method.value,
                "category": category.value,
                "status_code": status_code,
                "response_size_bytes": response_size_bytes,
                "user_id": user_id,
                "is_success": is_success,
                "is_client_error": is_client_error,
                "is_server_error": is_server_error,
                "error_type": error_type.value if error_type else None,
                "response_compliant": response_compliant
            })
            
            # Update tracking data
            endpoint_key = f"{method.value}:{endpoint}"
            if endpoint_key not in self.endpoint_performance:
                self.endpoint_performance[endpoint_key] = {
                    "total_requests": 0,
                    "successful_requests": 0,
                    "client_errors": 0,
                    "server_errors": 0,
                    "total_response_time": 0.0,
                    "avg_response_time": 0.0,
                    "min_response_time": float('inf'),
                    "max_response_time": 0.0,
                    "last_updated": end_time
                }
            
            perf = self.endpoint_performance[endpoint_key]
            perf["total_requests"] += 1
            perf["total_response_time"] += response_time
            perf["avg_response_time"] = perf["total_response_time"] / perf["total_requests"]
            perf["min_response_time"] = min(perf["min_response_time"], response_time)
            perf["max_response_time"] = max(perf["max_response_time"], response_time)
            perf["last_updated"] = end_time
            
            if is_success:
                perf["successful_requests"] += 1
            elif is_client_error:
                perf["client_errors"] += 1
            elif is_server_error:
                perf["server_errors"] += 1
            
            # Update tracking for metrics
            self.response_times[endpoint_key].append(response_time)
            self.request_tracking[request_id] = {
                "endpoint": endpoint,
                "method": method,
                "category": category,
                "start_time": start_time,
                "end_time": end_time,
                "response_time": response_time,
                "status_code": status_code,
                "response_size_bytes": response_size_bytes,
                "user_id": user_id,
                "is_success": is_success,
                "error_type": error_type
            }
            
            if error_type:
                self.error_tracking[request_id] = {
                    "endpoint": endpoint,
                    "error_type": error_type,
                    "status_code": status_code,
                    "timestamp": end_time,
                    "user_id": user_id
                }
            
            self.logger.info(f"API request tracked - {method.value} {endpoint}: {response_time:.2f}ms, Status: {status_code}")
            
            return {
                "request_id": request_id,
                "endpoint": endpoint,
                "method": method.value,
                "category": category.value,
                "response_time": response_time,
                "status_code": status_code,
                "is_success": is_success,
                "response_compliant": response_compliant,
                "response_size_bytes": response_size_bytes
            }
            
        except Exception as e:
            self.logger.error(f"Error tracking API request: {e}")
            raise
    
    async def track_api_throughput(self, measurement_id: str, endpoint_category: APIEndpointCategory,
                                 measurement_start: datetime, measurement_end: datetime,
                                 total_requests: int, successful_requests: int,
                                 concurrent_connections: int) -> Dict[str, Any]:
        """Track API throughput and capacity SLA compliance"""
        try:
            measurement_duration = (measurement_end - measurement_start).total_seconds()
            requests_per_second = total_requests / measurement_duration if measurement_duration > 0 else 0
            success_rate = (successful_requests / total_requests * 100) if total_requests > 0 else 100
            
            # Update throughput metric
            throughput_metric = self.metrics["api_throughput"]
            throughput_metric.current_value = requests_per_second
            throughput_metric.last_measurement = measurement_end
            throughput_metric.endpoint_category = endpoint_category
            throughput_metric.success_rate = success_rate
            
            # Check throughput SLA compliance
            throughput_compliant = requests_per_second >= self.targets.api_throughput_rps
            capacity_compliant = concurrent_connections <= self.targets.concurrent_connections
            
            if not throughput_compliant:
                throughput_metric.violation_count += 1
                await self._generate_alert(
                    "API Throughput SLA Violation",
                    f"Throughput {requests_per_second:.2f} RPS below target {self.targets.api_throughput_rps} RPS",
                    "high",
                    {
                        "measurement_id": measurement_id,
                        "category": endpoint_category.value,
                        "requests_per_second": requests_per_second,
                        "total_requests": total_requests,
                        "successful_requests": successful_requests,
                        "measurement_duration": measurement_duration
                    }
                )
            
            if not capacity_compliant:
                await self._generate_alert(
                    "API Concurrent Connection Limit Exceeded",
                    f"Concurrent connections {concurrent_connections} exceeded limit {self.targets.concurrent_connections}",
                    "critical",
                    {
                        "measurement_id": measurement_id,
                        "category": endpoint_category.value,
                        "concurrent_connections": concurrent_connections,
                        "limit": self.targets.concurrent_connections
                    }
                )
            
            # Store measurements
            self.measurements["api_throughput"].append({
                "timestamp": measurement_end,
                "value": requests_per_second,
                "measurement_id": measurement_id,
                "category": endpoint_category.value,
                "total_requests": total_requests,
                "successful_requests": successful_requests,
                "concurrent_connections": concurrent_connections,
                "success_rate": success_rate,
                "measurement_duration": measurement_duration,
                "throughput_compliant": throughput_compliant,
                "capacity_compliant": capacity_compliant
            })
            
            # Update throughput tracking
            self.throughput_tracking[endpoint_category.value].append(requests_per_second)
            
            self.logger.info(f"API throughput tracked - Category: {endpoint_category.value}, RPS: {requests_per_second:.2f}")
            
            return {
                "measurement_id": measurement_id,
                "category": endpoint_category.value,
                "requests_per_second": requests_per_second,
                "total_requests": total_requests,
                "successful_requests": successful_requests,
                "success_rate": success_rate,
                "concurrent_connections": concurrent_connections,
                "throughput_compliant": throughput_compliant,
                "capacity_compliant": capacity_compliant
            }
            
        except Exception as e:
            self.logger.error(f"Error tracking API throughput: {e}")
            raise
    
    async def track_api_availability(self, availability_id: str, endpoint_category: APIEndpointCategory,
                                   check_start: datetime, check_end: datetime,
                                   uptime_percentage: float, downtime_minutes: float,
                                   health_check_success: bool) -> Dict[str, Any]:
        """Track API availability and uptime SLA compliance"""
        try:
            check_duration = (check_end - check_start).total_seconds() / 60  # Convert to minutes
            
            # Update availability metric
            availability_metric = self.metrics["api_availability"]
            availability_metric.current_value = uptime_percentage
            availability_metric.last_measurement = check_end
            availability_metric.endpoint_category = endpoint_category
            availability_metric.success_rate = uptime_percentage
            
            # Check availability SLA compliance
            availability_compliant = uptime_percentage >= self.targets.api_availability_percentage
            downtime_compliant = downtime_minutes <= self.targets.max_downtime_minutes_monthly
            
            if not availability_compliant:
                availability_metric.violation_count += 1
                await self._generate_alert(
                    "API Availability SLA Violation",
                    f"Availability {uptime_percentage:.3f}% below target {self.targets.api_availability_percentage}%",
                    "critical",
                    {
                        "availability_id": availability_id,
                        "category": endpoint_category.value,
                        "uptime_percentage": uptime_percentage,
                        "downtime_minutes": downtime_minutes,
                        "health_check_success": health_check_success
                    }
                )
            
            if not downtime_compliant:
                await self._generate_alert(
                    "API Downtime SLA Violation",
                    f"Downtime {downtime_minutes:.2f} minutes exceeded monthly limit {self.targets.max_downtime_minutes_monthly} minutes",
                    "critical",
                    {
                        "availability_id": availability_id,
                        "category": endpoint_category.value,
                        "downtime_minutes": downtime_minutes,
                        "monthly_limit": self.targets.max_downtime_minutes_monthly
                    }
                )
            
            if not health_check_success:
                await self._generate_alert(
                    "API Health Check Failure",
                    f"Health check failed for category {endpoint_category.value}",
                    "high",
                    {
                        "availability_id": availability_id,
                        "category": endpoint_category.value,
                        "check_duration": check_duration
                    }
                )
            
            # Store measurements
            self.measurements["api_availability"].append({
                "timestamp": check_end,
                "value": uptime_percentage,
                "availability_id": availability_id,
                "category": endpoint_category.value,
                "uptime_percentage": uptime_percentage,
                "downtime_minutes": downtime_minutes,
                "health_check_success": health_check_success,
                "check_duration": check_duration,
                "availability_compliant": availability_compliant,
                "downtime_compliant": downtime_compliant
            })
            
            # Update availability tracking
            self.availability_tracking[endpoint_category.value].append(uptime_percentage)
            
            self.logger.info(f"API availability tracked - Category: {endpoint_category.value}, Uptime: {uptime_percentage:.3f}%")
            
            return {
                "availability_id": availability_id,
                "category": endpoint_category.value,
                "uptime_percentage": uptime_percentage,
                "downtime_minutes": downtime_minutes,
                "health_check_success": health_check_success,
                "availability_compliant": availability_compliant,
                "downtime_compliant": downtime_compliant
            }
            
        except Exception as e:
            self.logger.error(f"Error tracking API availability: {e}")
            raise
    
    async def track_rate_limiting(self, rate_limit_id: str, endpoint: str, user_id: str,
                                window_start: datetime, window_end: datetime,
                                requests_made: int, rate_limit: int,
                                limit_exceeded: bool, burst_requests: int = 0) -> Dict[str, Any]:
        """Track rate limiting compliance and performance"""
        try:
            window_duration = (window_end - window_start).total_seconds()
            requests_per_second = requests_made / window_duration if window_duration > 0 else 0
            utilization_percentage = (requests_made / rate_limit * 100) if rate_limit > 0 else 0
            
            # Update rate limiting metric
            rate_limit_metric = self.metrics["rate_limit_compliance"]
            rate_limit_metric.current_value = 100.0 if not limit_exceeded else 0.0
            rate_limit_metric.last_measurement = window_end
            rate_limit_metric.success_rate = 100.0 - utilization_percentage
            
            # Check rate limiting SLA compliance
            compliance_rate = 100.0 if not limit_exceeded else 0.0
            rate_limit_compliant = compliance_rate >= self.targets.rate_limit_compliance_percentage
            burst_compliant = burst_requests <= self.targets.rate_limit_burst_capacity
            
            if not rate_limit_compliant:
                rate_limit_metric.violation_count += 1
                await self._generate_alert(
                    "Rate Limiting SLA Violation",
                    f"User {user_id} exceeded rate limit on {endpoint}: {requests_made}/{rate_limit} requests",
                    "medium",
                    {
                        "rate_limit_id": rate_limit_id,
                        "endpoint": endpoint,
                        "user_id": user_id,
                        "requests_made": requests_made,
                        "rate_limit": rate_limit,
                        "utilization_percentage": utilization_percentage,
                        "burst_requests": burst_requests
                    }
                )
            
            if not burst_compliant:
                await self._generate_alert(
                    "Rate Limit Burst Capacity Exceeded",
                    f"User {user_id} burst requests {burst_requests} exceeded capacity {self.targets.rate_limit_burst_capacity}",
                    "high",
                    {
                        "rate_limit_id": rate_limit_id,
                        "endpoint": endpoint,
                        "user_id": user_id,
                        "burst_requests": burst_requests,
                        "burst_capacity": self.targets.rate_limit_burst_capacity
                    }
                )
            
            # Store measurements
            self.measurements["rate_limit_compliance"].append({
                "timestamp": window_end,
                "value": compliance_rate,
                "rate_limit_id": rate_limit_id,
                "endpoint": endpoint,
                "user_id": user_id,
                "requests_made": requests_made,
                "rate_limit": rate_limit,
                "limit_exceeded": limit_exceeded,
                "burst_requests": burst_requests,
                "utilization_percentage": utilization_percentage,
                "window_duration": window_duration,
                "rate_limit_compliant": rate_limit_compliant,
                "burst_compliant": burst_compliant
            })
            
            # Update rate limiting tracking
            self.rate_limit_tracking[rate_limit_id] = {
                "endpoint": endpoint,
                "user_id": user_id,
                "requests_made": requests_made,
                "rate_limit": rate_limit,
                "limit_exceeded": limit_exceeded,
                "burst_requests": burst_requests,
                "utilization_percentage": utilization_percentage,
                "timestamp": window_end
            }
            
            self.logger.info(f"Rate limiting tracked - Endpoint: {endpoint}, User: {user_id}, Utilization: {utilization_percentage:.2f}%")
            
            return {
                "rate_limit_id": rate_limit_id,
                "endpoint": endpoint,
                "user_id": user_id,
                "requests_made": requests_made,
                "rate_limit": rate_limit,
                "limit_exceeded": limit_exceeded,
                "burst_requests": burst_requests,
                "utilization_percentage": utilization_percentage,
                "rate_limit_compliant": rate_limit_compliant,
                "burst_compliant": burst_compliant
            }
            
        except Exception as e:
            self.logger.error(f"Error tracking rate limiting: {e}")
            raise
    
    async def get_api_performance_summary(self, time_window_hours: int = 24,
                                        endpoint_category: Optional[APIEndpointCategory] = None,
                                        endpoint: Optional[str] = None) -> Dict[str, Any]:
        """Get comprehensive API performance SLA summary"""
        try:
            cutoff_time = datetime.now() - timedelta(hours=time_window_hours)
            summary = {
                "time_window_hours": time_window_hours,
                "cutoff_time": cutoff_time.isoformat(),
                "overall_compliance": {},
                "metric_summaries": {},
                "endpoint_performance": {},
                "response_time_analytics": {},
                "throughput_analytics": {},
                "availability_analytics": {},
                "error_analytics": {},
                "rate_limiting_analytics": {},
                "recommendations": []
            }
            
            # Calculate overall compliance for each metric
            for metric_name, metric in self.metrics.items():
                measurements = [
                    m for m in self.measurements[metric_name]
                    if m["timestamp"] >= cutoff_time
                ]
                
                # Apply filters
                if endpoint_category:
                    measurements = [m for m in measurements if m.get("category") == endpoint_category.value]
                if endpoint:
                    measurements = [m for m in measurements if m.get("endpoint") == endpoint]
                
                if measurements:
                    if metric_name == "api_response_time":
                        compliant_count = sum(1 for m in measurements if m.get("response_compliant", True))
                        compliance_rate = (compliant_count / len(measurements)) * 100
                    elif metric_name in ["api_availability", "rate_limit_compliance"]:
                        compliance_rate = statistics.mean([m["value"] for m in measurements])
                    else:
                        compliant_count = sum(1 for m in measurements if m.get("throughput_compliant", True))
                        compliance_rate = (compliant_count / len(measurements)) * 100
                    
                    avg_value = statistics.mean([m["value"] for m in measurements])
                    p95_value = statistics.quantiles([m["value"] for m in measurements], n=20)[18] if len(measurements) >= 20 else max([m["value"] for m in measurements])
                    p99_value = statistics.quantiles([m["value"] for m in measurements], n=100)[98] if len(measurements) >= 100 else max([m["value"] for m in measurements])
                    
                    summary["metric_summaries"][metric_name] = {
                        "compliance_rate": compliance_rate,
                        "measurement_count": len(measurements),
                        "avg_value": avg_value,
                        "p95_value": p95_value,
                        "p99_value": p99_value,
                        "target_value": metric.target_value,
                        "unit": metric.unit,
                        "violation_count": metric.violation_count
                    }
                    
                    summary["overall_compliance"][metric_name] = compliance_rate >= 95.0
            
            # Endpoint performance analysis
            for endpoint_key, perf in self.endpoint_performance.items():
                if perf["last_updated"] >= cutoff_time:
                    error_rate = ((perf["client_errors"] + perf["server_errors"]) / perf["total_requests"] * 100) if perf["total_requests"] > 0 else 0
                    success_rate = (perf["successful_requests"] / perf["total_requests"] * 100) if perf["total_requests"] > 0 else 0
                    
                    # Calculate P95 response time from recent measurements
                    recent_times = [t for t in self.response_times[endpoint_key] if len(self.response_times[endpoint_key]) > 0]
                    p95_response = statistics.quantiles(recent_times, n=20)[18] if len(recent_times) >= 20 else perf["max_response_time"]
                    
                    summary["endpoint_performance"][endpoint_key] = {
                        "total_requests": perf["total_requests"],
                        "success_rate": success_rate,
                        "error_rate": error_rate,
                        "avg_response_time": perf["avg_response_time"],
                        "p95_response_time": p95_response,
                        "min_response_time": perf["min_response_time"],
                        "max_response_time": perf["max_response_time"]
                    }
            
            # Response time analytics
            all_response_times = []
            for times in self.response_times.values():
                all_response_times.extend(list(times))
            
            if all_response_times:
                summary["response_time_analytics"] = {
                    "avg_response_time": statistics.mean(all_response_times),
                    "p95_response_time": statistics.quantiles(all_response_times, n=20)[18] if len(all_response_times) >= 20 else max(all_response_times),
                    "p99_response_time": statistics.quantiles(all_response_times, n=100)[98] if len(all_response_times) >= 100 else max(all_response_times),
                    "min_response_time": min(all_response_times),
                    "max_response_time": max(all_response_times),
                    "total_requests": len(all_response_times)
                }
            
            # Throughput analytics
            all_throughput = []
            for throughput in self.throughput_tracking.values():
                all_throughput.extend(list(throughput))
            
            if all_throughput:
                summary["throughput_analytics"] = {
                    "avg_throughput_rps": statistics.mean(all_throughput),
                    "peak_throughput_rps": max(all_throughput),
                    "min_throughput_rps": min(all_throughput),
                    "throughput_measurements": len(all_throughput)
                }
            
            # Availability analytics
            all_availability = []
            for availability in self.availability_tracking.values():
                all_availability.extend(list(availability))
            
            if all_availability:
                summary["availability_analytics"] = {
                    "avg_availability": statistics.mean(all_availability),
                    "min_availability": min(all_availability),
                    "availability_measurements": len(all_availability)
                }
            
            # Error analytics
            recent_errors = [
                error for error in self.error_tracking.values()
                if error["timestamp"] >= cutoff_time
            ]
            
            if recent_errors:
                error_by_type = defaultdict(int)
                for error in recent_errors:
                    error_by_type[error["error_type"].value] += 1
                
                summary["error_analytics"] = {
                    "total_errors": len(recent_errors),
                    "errors_by_type": dict(error_by_type),
                    "most_common_error": max(error_by_type.items(), key=lambda x: x[1])[0] if error_by_type else None
                }
            
            # Rate limiting analytics
            recent_rate_limits = [
                rl for rl in self.rate_limit_tracking.values()
                if rl["timestamp"] >= cutoff_time
            ]
            
            if recent_rate_limits:
                exceeded_limits = [rl for rl in recent_rate_limits if rl["limit_exceeded"]]
                avg_utilization = statistics.mean([rl["utilization_percentage"] for rl in recent_rate_limits])
                
                summary["rate_limiting_analytics"] = {
                    "total_rate_limit_checks": len(recent_rate_limits),
                    "limits_exceeded": len(exceeded_limits),
                    "avg_utilization": avg_utilization,
                    "limit_violation_rate": (len(exceeded_limits) / len(recent_rate_limits) * 100) if recent_rate_limits else 0
                }
            
            # Generate recommendations
            for metric_name, compliance in summary["overall_compliance"].items():
                if not compliance:
                    if metric_name == "api_response_time":
                        summary["recommendations"].append("Optimize API response times: implement caching, database query optimization, and CDN")
                    elif metric_name == "api_throughput":
                        summary["recommendations"].append("Scale API infrastructure: add load balancers, implement auto-scaling, optimize connection pooling")
                    elif metric_name == "api_availability":
                        summary["recommendations"].append("Improve API reliability: implement redundancy, health checks, and failover mechanisms")
                    elif metric_name == "api_error_rate":
                        summary["recommendations"].append("Reduce API errors: enhance error handling, input validation, and monitoring")
                    elif metric_name == "rate_limit_compliance":
                        summary["recommendations"].append("Optimize rate limiting: implement intelligent throttling and user education")
            
            return summary
            
        except Exception as e:
            self.logger.error(f"Error generating API performance summary: {e}")
            raise
    
    async def _generate_alert(self, title: str, message: str, severity: str, metadata: Dict[str, Any]):
        """Generate SLA violation alert"""
        alert = {
            "timestamp": datetime.now().isoformat(),
            "title": title,
            "message": message,
            "severity": severity,
            "component": "api_performance_sla",
            "metadata": metadata
        }
        
        self.alerts.append(alert)
        self.logger.warning(f"API Performance SLA Alert - {title}: {message}")
        
        # Keep only last 1000 alerts
        if len(self.alerts) > 1000:
            self.alerts = self.alerts[-1000:]
    
    async def get_real_time_api_metrics(self) -> Dict[str, Any]:
        """Get real-time API performance metrics for monitoring dashboards"""
        try:
            current_time = datetime.now()
            
            metrics_data = {}
            for metric_name, metric in self.metrics.items():
                # Get recent measurements (last 5 minutes)
                recent_measurements = [
                    m for m in self.measurements[metric_name]
                    if (current_time - m["timestamp"]).total_seconds() <= 300
                ]
                
                if recent_measurements:
                    if metric_name == "api_response_time":
                        current_avg = statistics.mean([m["value"] for m in recent_measurements])
                        compliance_rate = (sum(1 for m in recent_measurements if m.get("response_compliant", True)) / len(recent_measurements)) * 100
                    elif metric_name in ["api_availability", "rate_limit_compliance"]:
                        current_avg = statistics.mean([m["value"] for m in recent_measurements])
                        compliance_rate = current_avg
                    else:
                        current_avg = statistics.mean([m["value"] for m in recent_measurements])
                        compliance_rate = (sum(1 for m in recent_measurements if m.get("throughput_compliant", True)) / len(recent_measurements)) * 100
                else:
                    current_avg = metric.current_value
                    compliance_rate = 100.0 if metric.current_value <= metric.target_value else 0.0
                
                metrics_data[metric_name] = {
                    "current_value": current_avg,
                    "target_value": metric.target_value,
                    "compliance_rate": compliance_rate,
                    "unit": metric.unit,
                    "status": "compliant" if compliance_rate >= 95.0 else "violation",
                    "last_updated": metric.last_measurement.isoformat(),
                    "recent_measurements_count": len(recent_measurements),
                    "success_rate": metric.success_rate
                }
            
            # Calculate API health indicators
            recent_requests = len([
                req for req in self.request_tracking.values()
                if (current_time - req["end_time"]).total_seconds() <= 300  # Last 5 minutes
            ])
            
            recent_errors = len([
                error for error in self.error_tracking.values()
                if (current_time - error["timestamp"]).total_seconds() <= 300  # Last 5 minutes
            ])
            
            api_health = {
                "requests_last_5_minutes": recent_requests,
                "errors_last_5_minutes": recent_errors,
                "error_rate_last_5_minutes": (recent_errors / recent_requests * 100) if recent_requests > 0 else 0,
                "active_endpoints": len(self.endpoint_performance),
                "rate_limit_violations_last_hour": len([
                    rl for rl in self.rate_limit_tracking.values()
                    if (current_time - rl["timestamp"]).total_seconds() <= 3600 and rl["limit_exceeded"]
                ])
            }
            
            return {
                "timestamp": current_time.isoformat(),
                "metrics": metrics_data,
                "api_health": api_health,
                "overall_status": "healthy" if all(m["compliance_rate"] >= 95.0 for m in metrics_data.values()) else "degraded",
                "active_alerts_count": len([a for a in self.alerts if (current_time - datetime.fromisoformat(a["timestamp"])).total_seconds() <= 3600])
            }
            
        except Exception as e:
            self.logger.error(f"Error getting real-time API metrics: {e}")
            raise

# Global instance for easy access
api_performance_sla = APIPerformanceSLA()