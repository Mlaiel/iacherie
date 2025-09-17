"""🔗 External Integration Performance Profiler
==============================================

Advanced external integration performance profiling system for the Ainflue Creator Economy platform.
Monitors third-party APIs, social media integrations, payment gateways, and webhook performance.

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
import hashlib

from prometheus_client import Counter, Gauge, Histogram, Summary

logger = logging.getLogger(__name__)


class IntegrationType(Enum):
    """Types of external integrations"""
    SOCIAL_MEDIA = "social_media"
    PAYMENT_GATEWAY = "payment_gateway"
    CDN_PROVIDER = "cdn_provider"
    ANALYTICS_PLATFORM = "analytics_platform"
    EMAIL_SERVICE = "email_service"
    SMS_SERVICE = "sms_service"
    STORAGE_SERVICE = "storage_service"
    AI_SERVICE = "ai_service"
    STREAMING_PLATFORM = "streaming_platform"
    WEBHOOK = "webhook"
    THIRD_PARTY_API = "third_party_api"
    AUTHENTICATION_PROVIDER = "authentication_provider"


class IntegrationCategory(Enum):
    """Categories of integrations for Creator Economy"""
    CONTENT_DISTRIBUTION = "content_distribution"
    MONETIZATION = "monetization"
    ANALYTICS = "analytics"
    COMMUNICATION = "communication"
    INFRASTRUCTURE = "infrastructure"
    CREATOR_TOOLS = "creator_tools"
    AUDIENCE_ENGAGEMENT = "audience_engagement"
    BRAND_COLLABORATION = "brand_collaboration"


class ProviderType(Enum):
    """External service providers"""
    # Social Media
    YOUTUBE = "youtube"
    INSTAGRAM = "instagram"
    TIKTOK = "tiktok"
    TWITTER = "twitter"
    FACEBOOK = "facebook"
    LINKEDIN = "linkedin"
    TWITCH = "twitch"
    
    # Payment
    STRIPE = "stripe"
    PAYPAL = "paypal"
    SQUARE = "square"
    RAZORPAY = "razorpay"
    
    # CDN/Storage
    CLOUDFLARE = "cloudflare"
    AWS_S3 = "aws_s3"
    GOOGLE_CLOUD = "google_cloud"
    AZURE = "azure"
    
    # Analytics
    GOOGLE_ANALYTICS = "google_analytics"
    MIXPANEL = "mixpanel"
    AMPLITUDE = "amplitude"
    
    # AI Services
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    HUGGINGFACE = "huggingface"
    
    # Communication
    SENDGRID = "sendgrid"
    TWILIO = "twilio"
    DISCORD = "discord"
    SLACK = "slack"
    
    # Other
    CUSTOM = "custom"


@dataclass
class ExternalProvider:
    """External service provider information"""
    provider_name: str
    provider_type: ProviderType
    integration_type: IntegrationType
    category: IntegrationCategory
    
    # API details
    base_url: str
    api_version: str
    
    # Authentication
    auth_method: str  # "api_key", "oauth2", "bearer", "basic"
    requires_rate_limiting: bool = True
    
    # Limits and quotas
    rate_limit_per_minute: Optional[int] = None
    rate_limit_per_hour: Optional[int] = None
    rate_limit_per_day: Optional[int] = None
    
    # Reliability
    sla_uptime_percent: float = 99.9
    expected_response_time_ms: float = 1000.0
    
    # Regional information
    region: Optional[str] = None
    data_center: Optional[str] = None


@dataclass
class IntegrationRequestMetadata:
    """Metadata for external integration requests"""
    request_id: str
    provider: ExternalProvider
    
    # Operation details
    operation_name: str
    endpoint_path: str
    http_method: str
    
    # Request characteristics
    payload_size_bytes: int
    headers_count: int
    query_params_count: int
    
    # Rate limiting
    rate_limit_bucket: Optional[str] = None
    current_quota_usage: Optional[int] = None
    
    # Retry configuration
    max_retries: int = 3
    retry_backoff_ms: int = 1000
    
    # Caching
    cacheable: bool = False
    cache_ttl_seconds: Optional[int] = None
    
    # Business context
    user_id: Optional[str] = None
    creator_id: Optional[str] = None
    content_id: Optional[str] = None
    business_operation: Optional[str] = None


@dataclass
class ExternalIntegrationMetrics:
    """External integration performance metrics"""
    request_id: str
    metadata: IntegrationRequestMetadata
    
    # Performance metrics (all in milliseconds)
    total_time_ms: float
    dns_lookup_time_ms: Optional[float] = None
    tcp_connect_time_ms: Optional[float] = None
    tls_handshake_time_ms: Optional[float] = None
    auth_time_ms: Optional[float] = None
    api_call_time_ms: Optional[float] = None
    response_processing_time_ms: Optional[float] = None
    
    # Network metrics
    bytes_sent: int = 0
    bytes_received: int = 0
    compression_ratio: Optional[float] = None
    
    # Rate limiting metrics
    rate_limited: bool = False
    rate_limit_remaining: Optional[int] = None
    rate_limit_reset_time: Optional[datetime] = None
    quota_consumed: int = 1
    
    # Retry metrics
    retry_count: int = 0
    backoff_time_ms: float = 0.0
    
    # Caching metrics
    cache_hit: bool = False
    cache_miss: bool = False
    cache_write: bool = False
    
    # Response metrics
    status_code: Optional[int] = None
    response_size_bytes: int = 0
    response_headers_count: int = 0
    
    # Business metrics
    data_records_processed: int = 0
    api_cost_usd: Optional[float] = None
    
    # Quality metrics
    success: bool = True
    error_message: Optional[str] = None
    error_type: Optional[str] = None
    provider_error_code: Optional[str] = None
    
    timestamp: datetime = field(default_factory=datetime.utcnow)


@dataclass
class IntegrationBottleneck:
    """External integration performance bottleneck detection"""
    bottleneck_id: str
    provider: ExternalProvider
    
    # Bottleneck details
    bottleneck_type: str  # "rate_limiting", "high_latency", "provider_downtime", "auth_issues"
    severity: str  # "low", "medium", "high", "critical"
    description: str
    
    # Performance impact
    current_performance: Dict[str, float]
    expected_performance: Dict[str, float]
    impact_percentage: float
    
    # Affected operations
    affected_operations: List[str]
    affected_users: List[str]
    
    # Provider analysis
    provider_status: Dict[str, Any]
    rate_limit_analysis: Dict[str, Any]
    cost_impact: Dict[str, float]
    
    # Optimization recommendations
    recommendations: List[str]
    estimated_improvement: Dict[str, float]
    alternative_providers: List[str]
    
    timestamp: datetime = field(default_factory=datetime.utcnow)


class ExternalIntegrationProfiler:
    """Advanced external integration performance profiler"""
    
    def __init__(self,
                 monitoring_interval: float = 10.0,
                 max_history_size: int = 10000,
                 enable_rate_limit_tracking: bool = True,
                 enable_cost_tracking: bool = True,
                 high_latency_threshold_ms: float = 2000.0):
        """
        Initialize external integration profiler
        
        Args:
            monitoring_interval: Monitoring interval in seconds
            max_history_size: Maximum number of metrics to store
            enable_rate_limit_tracking: Enable rate limiting tracking
            enable_cost_tracking: Enable API cost tracking
            high_latency_threshold_ms: Threshold for high latency detection
        """
        self.monitoring_interval = monitoring_interval
        self.max_history_size = max_history_size
        self.enable_rate_limit_tracking = enable_rate_limit_tracking
        self.enable_cost_tracking = enable_cost_tracking
        self.high_latency_threshold_ms = high_latency_threshold_ms
        
        # Storage for metrics
        self.metrics_history: deque = deque(maxlen=max_history_size)
        self.active_requests: Dict[str, ExternalIntegrationMetrics] = {}
        self.bottlenecks: List[IntegrationBottleneck] = []
        
        # Provider tracking
        self.registered_providers: Dict[str, ExternalProvider] = {}
        self.provider_health: Dict[str, Dict[str, Any]] = defaultdict(dict)
        
        # Rate limiting tracking
        self.rate_limit_buckets: Dict[str, Dict[str, Any]] = defaultdict(dict)
        self.quota_usage: Dict[str, Dict[str, int]] = defaultdict(lambda: defaultdict(int))
        
        # Cost tracking
        self.api_costs: Dict[str, List[float]] = defaultdict(list)
        
        # Integration patterns tracking
        self.integration_patterns: Dict[str, List[float]] = defaultdict(list)
        self.provider_reliability: Dict[str, Dict[str, float]] = defaultdict(lambda: defaultdict(float))
        
        # Performance thresholds
        self.thresholds = {
            'max_response_time_ms': high_latency_threshold_ms,
            'max_error_rate_percent': 5.0,
            'max_retry_count': 3,
            'max_cost_per_request_usd': 0.10,
            'min_success_rate_percent': 95.0
        }
        
        # Monitoring state
        self.is_monitoring = False
        self.monitoring_task: Optional[asyncio.Task] = None
        self._lock = threading.Lock()
        
        # Prometheus metrics
        self._init_prometheus_metrics()
        
        logger.info("ExternalIntegrationProfiler initialized for Creator Economy platform")
    
    def _init_prometheus_metrics(self):
        """Initialize Prometheus metrics"""
        self.prometheus_metrics = {
            'integration_request_duration': Histogram(
                'ainflue_integration_request_duration_seconds',
                'Duration of external integration requests',
                ['provider', 'integration_type', 'operation', 'status']
            ),
            'integration_rate_limits': Counter(
                'ainflue_integration_rate_limits_total',
                'Total rate limit hits',
                ['provider', 'integration_type']
            ),
            'integration_costs': Counter(
                'ainflue_integration_costs_usd_total',
                'Total integration costs in USD',
                ['provider', 'integration_type', 'operation']
            ),
            'integration_errors': Counter(
                'ainflue_integration_errors_total',
                'Total integration errors',
                ['provider', 'integration_type', 'error_type']
            ),
            'integration_quota_usage': Gauge(
                'ainflue_integration_quota_usage_percent',
                'Integration quota usage percentage',
                ['provider', 'quota_type']
            ),
            'provider_reliability': Gauge(
                'ainflue_provider_reliability_percent',
                'Provider reliability percentage',
                ['provider', 'integration_type']
            ),
            'integration_bottlenecks': Gauge(
                'ainflue_integration_bottlenecks_active',
                'Number of active integration bottlenecks',
                ['provider', 'severity']
            )
        }
    
    async def start_monitoring(self):
        """Start continuous integration monitoring"""
        if self.is_monitoring:
            logger.warning("Integration monitoring already running")
            return
        
        self.is_monitoring = True
        self.monitoring_task = asyncio.create_task(self._monitoring_loop())
        logger.info("External integration monitoring started")
    
    async def stop_monitoring(self):
        """Stop integration monitoring"""
        if not self.is_monitoring:
            return
        
        self.is_monitoring = False
        if self.monitoring_task:
            self.monitoring_task.cancel()
            try:
                await self.monitoring_task
            except asyncio.CancelledError:
                pass
        
        logger.info("External integration monitoring stopped")
    
    async def profile_integration_request(self,
                                        metadata: IntegrationRequestMetadata,
                                        integration_func: Callable,
                                        *args, **kwargs) -> ExternalIntegrationMetrics:
        """
        Profile an external integration request
        
        Args:
            metadata: Integration request metadata
            integration_func: Function to execute and profile
            *args, **kwargs: Arguments for the integration function
        
        Returns:
            ExternalIntegrationMetrics: Detailed performance metrics
        """
        start_time = time.time()
        
        # Initialize metrics
        metrics = ExternalIntegrationMetrics(
            request_id=metadata.request_id,
            metadata=metadata,
            total_time_ms=0.0
        )
        
        try:
            # Check rate limiting before request
            if self.enable_rate_limit_tracking:
                rate_check_start = time.time()
                rate_limited = await self._check_rate_limiting(metadata)
                rate_check_end = time.time()
                
                if rate_limited:
                    metrics.rate_limited = True
                    metrics.success = False
                    metrics.error_message = "Rate limit exceeded"
                    metrics.total_time_ms = (rate_check_end - start_time) * 1000
                    await self._store_metrics(metrics)
                    return metrics
            
            # Check cache if applicable
            if metadata.cacheable:
                cache_start = time.time()
                cached_result = await self._check_cache(metadata)
                cache_end = time.time()
                
                if cached_result is not None:
                    metrics.cache_hit = True
                    metrics.total_time_ms = (cache_end - start_time) * 1000
                    metrics.success = True
                    await self._store_metrics(metrics)
                    return metrics
                else:
                    metrics.cache_miss = True
            
            # Perform authentication if required
            auth_start = time.time()
            await self._perform_authentication(metadata)
            auth_end = time.time()
            metrics.auth_time_ms = (auth_end - auth_start) * 1000
            
            # Execute the integration request with retries
            retry_count = 0
            last_error = None
            
            while retry_count <= metadata.max_retries:
                try:
                    api_start = time.time()
                    result = await self._execute_integration_operation(integration_func, *args, **kwargs)
                    api_end = time.time()
                    
                    metrics.api_call_time_ms = (api_end - api_start) * 1000
                    metrics.retry_count = retry_count
                    
                    # Process successful response
                    processing_start = time.time()
                    metrics = await self._process_integration_response(result, metrics)
                    processing_end = time.time()
                    metrics.response_processing_time_ms = (processing_end - processing_start) * 1000
                    
                    # Cache result if applicable
                    if metadata.cacheable and not metrics.cache_hit:
                        await self._cache_result(metadata, result)
                        metrics.cache_write = True
                    
                    # Success - break retry loop
                    break
                    
                except Exception as e:
                    retry_count += 1
                    last_error = e
                    
                    if retry_count <= metadata.max_retries:
                        # Calculate backoff time
                        backoff_time = metadata.retry_backoff_ms * (2 ** (retry_count - 1)) / 1000
                        metrics.backoff_time_ms += backoff_time * 1000
                        await asyncio.sleep(backoff_time)
                    else:
                        # Max retries exceeded
                        metrics.error_message = str(last_error)
                        metrics.error_type = type(last_error).__name__
                        metrics.success = False
            
            # Calculate total time
            end_time = time.time()
            metrics.total_time_ms = (end_time - start_time) * 1000
            
            # Update rate limiting counters
            if self.enable_rate_limit_tracking:
                await self._update_rate_limiting(metadata, metrics.success)
            
            # Track API costs
            if self.enable_cost_tracking:
                await self._track_api_costs(metadata, metrics)
            
            # Store metrics
            await self._store_metrics(metrics)
            
            # Update Prometheus metrics
            self._update_prometheus_metrics(metrics)
            
            # Track integration patterns
            await self._track_integration_patterns(metrics)
            
            # Check for bottlenecks
            await self._detect_bottlenecks(metrics)
            
            logger.debug(f"Integration request profiled: {metadata.request_id} - {metrics.total_time_ms:.2f}ms")
            return metrics
            
        except Exception as e:
            # Handle integration failure
            end_time = time.time()
            metrics.total_time_ms = (end_time - start_time) * 1000
            metrics.success = False
            metrics.error_message = str(e)
            metrics.error_type = type(e).__name__
            
            await self._store_metrics(metrics)
            self.prometheus_metrics['integration_errors'].labels(
                provider=metadata.provider.provider_name,
                integration_type=metadata.provider.integration_type.value,
                error_type=metrics.error_type
            ).inc()
            
            logger.error(f"Integration request failed: {metadata.request_id} - {e}")
            return metrics
    
    async def _check_rate_limiting(self, metadata: IntegrationRequestMetadata) -> bool:
        """Check if request should be rate limited"""
        try:
            provider = metadata.provider
            bucket_key = f"{provider.provider_name}_{metadata.operation_name}"
            
            with self._lock:
                bucket = self.rate_limit_buckets[bucket_key]
                current_time = datetime.utcnow()
                
                # Simple rate limiting check (per minute)
                if provider.rate_limit_per_minute:
                    minute_key = current_time.strftime("%Y-%m-%d %H:%M")
                    current_count = bucket.get(minute_key, 0)
                    
                    if current_count >= provider.rate_limit_per_minute:
                        return True
                    
                    bucket[minute_key] = current_count + 1
                
                return False
        
        except Exception as e:
            logger.warning(f"Rate limiting check failed: {e}")
            return False
    
    async def _update_rate_limiting(self, metadata: IntegrationRequestMetadata, success: bool):
        """Update rate limiting counters"""
        try:
            provider = metadata.provider
            bucket_key = f"{provider.provider_name}_{metadata.operation_name}"
            
            with self._lock:
                quota_key = f"{provider.provider_name}_daily"
                self.quota_usage[quota_key]["requests"] += 1
                
                if success:
                    self.quota_usage[quota_key]["successful"] += 1
        
        except Exception as e:
            logger.warning(f"Rate limiting update failed: {e}")
    
    async def _check_cache(self, metadata: IntegrationRequestMetadata) -> Optional[Any]:
        """Check cache for cached result"""
        try:
            # Create cache key based on operation and parameters
            cache_key = self._generate_cache_key(metadata)
            
            # Simplified cache check (would integrate with actual cache)
            # For now, return None (cache miss)
            return None
        
        except Exception as e:
            logger.warning(f"Cache check failed: {e}")
            return None
    
    async def _cache_result(self, metadata: IntegrationRequestMetadata, result: Any):
        """Cache integration result"""
        try:
            cache_key = self._generate_cache_key(metadata)
            
            # Simplified cache write (would integrate with actual cache)
            # For now, just log the cache operation
            logger.debug(f"Caching result for key: {cache_key}")
        
        except Exception as e:
            logger.warning(f"Cache write failed: {e}")
    
    def _generate_cache_key(self, metadata: IntegrationRequestMetadata) -> str:
        """Generate cache key for request"""
        key_components = [
            metadata.provider.provider_name,
            metadata.operation_name,
            metadata.endpoint_path,
            str(metadata.payload_size_bytes)
        ]
        key_string = "_".join(key_components)
        return hashlib.md5(key_string.encode()).hexdigest()
    
    async def _perform_authentication(self, metadata: IntegrationRequestMetadata):
        """Perform authentication for external provider"""
        try:
            # Simulate authentication process
            await asyncio.sleep(0.01)  # Simulated auth time
        
        except Exception as e:
            logger.warning(f"Authentication failed for {metadata.provider.provider_name}: {e}")
    
    async def _execute_integration_operation(self, operation_func: Callable, *args, **kwargs):
        """Execute integration operation with proper async handling"""
        if asyncio.iscoroutinefunction(operation_func):
            return await operation_func(*args, **kwargs)
        else:
            return operation_func(*args, **kwargs)
    
    async def _process_integration_response(self, result: Any, metrics: ExternalIntegrationMetrics) -> ExternalIntegrationMetrics:
        """Process integration response and extract metrics"""
        if isinstance(result, dict):
            # Extract status code
            metrics.status_code = result.get('status_code', 200)
            
            # Extract response size
            metrics.response_size_bytes = len(json.dumps(result)) if result else 0
            
            # Extract rate limiting information
            if 'rate_limit_remaining' in result:
                metrics.rate_limit_remaining = result['rate_limit_remaining']
            
            if 'rate_limit_reset' in result:
                metrics.rate_limit_reset_time = datetime.fromisoformat(result['rate_limit_reset'])
            
            # Extract business metrics
            if 'data' in result and isinstance(result['data'], list):
                metrics.data_records_processed = len(result['data'])
            
            # Extract cost information
            if 'api_cost' in result:
                metrics.api_cost_usd = result['api_cost']
        
        return metrics
    
    async def _track_api_costs(self, metadata: IntegrationRequestMetadata, metrics: ExternalIntegrationMetrics):
        """Track API costs for integration"""
        try:
            if metrics.api_cost_usd is not None:
                provider_name = metadata.provider.provider_name
                with self._lock:
                    self.api_costs[provider_name].append(metrics.api_cost_usd)
                    
                    # Keep only recent costs
                    if len(self.api_costs[provider_name]) > 1000:
                        self.api_costs[provider_name] = self.api_costs[provider_name][-1000:]
                
                # Update Prometheus metrics
                self.prometheus_metrics['integration_costs'].labels(
                    provider=provider_name,
                    integration_type=metadata.provider.integration_type.value,
                    operation=metadata.operation_name
                ).inc(metrics.api_cost_usd)
        
        except Exception as e:
            logger.warning(f"Cost tracking failed: {e}")
    
    async def _store_metrics(self, metrics: ExternalIntegrationMetrics):
        """Store metrics in history"""
        with self._lock:
            self.metrics_history.append(metrics)
            self.active_requests[metrics.request_id] = metrics
    
    def _update_prometheus_metrics(self, metrics: ExternalIntegrationMetrics):
        """Update Prometheus metrics"""
        provider_name = metrics.metadata.provider.provider_name
        integration_type = metrics.metadata.provider.integration_type.value
        operation = metrics.metadata.operation_name
        status = "success" if metrics.success else "error"
        
        # Update request duration
        self.prometheus_metrics['integration_request_duration'].labels(
            provider=provider_name,
            integration_type=integration_type,
            operation=operation,
            status=status
        ).observe(metrics.total_time_ms / 1000)
        
        # Update rate limits
        if metrics.rate_limited:
            self.prometheus_metrics['integration_rate_limits'].labels(
                provider=provider_name,
                integration_type=integration_type
            ).inc()
        
        # Update quota usage
        if metrics.rate_limit_remaining is not None:
            quota_usage_percent = max(0, 100 - (metrics.rate_limit_remaining / 100 * 100))
            self.prometheus_metrics['integration_quota_usage'].labels(
                provider=provider_name,
                quota_type="requests"
            ).set(quota_usage_percent)
    
    async def _track_integration_patterns(self, metrics: ExternalIntegrationMetrics):
        """Track integration patterns for optimization"""
        pattern_key = f"{metrics.metadata.provider.provider_name}_{metrics.metadata.operation_name}"
        
        with self._lock:
            self.integration_patterns[pattern_key].append(metrics.total_time_ms)
            
            # Update provider reliability
            provider_name = metrics.metadata.provider.provider_name
            integration_type = metrics.metadata.provider.integration_type.value
            
            if pattern_key not in self.provider_reliability[provider_name]:
                self.provider_reliability[provider_name][integration_type] = 100.0
            
            # Simple exponential moving average for reliability
            current_reliability = self.provider_reliability[provider_name][integration_type]
            success_rate = 100.0 if metrics.success else 0.0
            new_reliability = current_reliability * 0.9 + success_rate * 0.1
            self.provider_reliability[provider_name][integration_type] = new_reliability
            
            # Update Prometheus metrics
            self.prometheus_metrics['provider_reliability'].labels(
                provider=provider_name,
                integration_type=integration_type
            ).set(new_reliability)
            
            # Keep only recent patterns
            if len(self.integration_patterns[pattern_key]) > 100:
                self.integration_patterns[pattern_key] = self.integration_patterns[pattern_key][-100:]
    
    async def _detect_bottlenecks(self, metrics: ExternalIntegrationMetrics):
        """Detect integration performance bottlenecks"""
        bottlenecks = []
        
        # High latency detection
        if metrics.total_time_ms > self.thresholds['max_response_time_ms']:
            bottleneck = IntegrationBottleneck(
                bottleneck_id=f"high_latency_{int(time.time())}",
                provider=metrics.metadata.provider,
                bottleneck_type="high_latency",
                severity="high" if metrics.total_time_ms > self.thresholds['max_response_time_ms'] * 2 else "medium",
                description=f"High integration latency: {metrics.total_time_ms:.2f}ms",
                current_performance={"latency_ms": metrics.total_time_ms},
                expected_performance={"latency_ms": self.thresholds['max_response_time_ms']},
                impact_percentage=(metrics.total_time_ms - self.thresholds['max_response_time_ms']) / self.thresholds['max_response_time_ms'] * 100,
                affected_operations=[metrics.metadata.operation_name],
                affected_users=[metrics.metadata.user_id] if metrics.metadata.user_id else [],
                provider_status={"uptime": "unknown", "region": metrics.metadata.provider.region},
                rate_limit_analysis={"remaining": metrics.rate_limit_remaining, "limited": metrics.rate_limited},
                cost_impact={"cost_per_request": metrics.api_cost_usd or 0.0},
                recommendations=[
                    "Consider implementing request caching",
                    "Optimize payload sizes and request frequency",
                    "Evaluate alternative providers or endpoints",
                    "Implement request batching where possible",
                    "Consider regional endpoint selection"
                ],
                estimated_improvement={"latency_reduction_percent": 40.0},
                alternative_providers=self._get_alternative_providers(metrics.metadata.provider)
            )
            bottlenecks.append(bottleneck)
        
        # Rate limiting detection
        if metrics.rate_limited:
            bottleneck = IntegrationBottleneck(
                bottleneck_id=f"rate_limiting_{int(time.time())}",
                provider=metrics.metadata.provider,
                bottleneck_type="rate_limiting",
                severity="high",
                description="Rate limiting affecting integration performance",
                current_performance={"rate_limited": 1.0},
                expected_performance={"rate_limited": 0.0},
                impact_percentage=100.0,
                affected_operations=[metrics.metadata.operation_name],
                affected_users=[metrics.metadata.user_id] if metrics.metadata.user_id else [],
                provider_status={"rate_limits": "exceeded"},
                rate_limit_analysis={
                    "remaining": metrics.rate_limit_remaining,
                    "reset_time": metrics.rate_limit_reset_time.isoformat() if metrics.rate_limit_reset_time else None,
                    "quota_type": "requests"
                },
                cost_impact={"potential_lost_revenue": "unknown"},
                recommendations=[
                    "Implement intelligent request queuing",
                    "Optimize request patterns and timing",
                    "Consider upgrading to higher tier plans",
                    "Implement request prioritization",
                    "Use multiple provider accounts if allowed"
                ],
                estimated_improvement={"rate_limit_reduction_percent": 80.0},
                alternative_providers=self._get_alternative_providers(metrics.metadata.provider)
            )
            bottlenecks.append(bottleneck)
        
        # High retry count detection
        if metrics.retry_count > self.thresholds['max_retry_count']:
            bottleneck = IntegrationBottleneck(
                bottleneck_id=f"high_retries_{int(time.time())}",
                provider=metrics.metadata.provider,
                bottleneck_type="high_retries",
                severity="medium",
                description=f"High retry count: {metrics.retry_count} retries",
                current_performance={"retry_count": metrics.retry_count},
                expected_performance={"retry_count": self.thresholds['max_retry_count']},
                impact_percentage=(metrics.retry_count - self.thresholds['max_retry_count']) / self.thresholds['max_retry_count'] * 100,
                affected_operations=[metrics.metadata.operation_name],
                affected_users=[metrics.metadata.user_id] if metrics.metadata.user_id else [],
                provider_status={"reliability": "degraded"},
                rate_limit_analysis={"retries_due_to_rate_limit": metrics.rate_limited},
                cost_impact={"additional_cost_per_retry": metrics.api_cost_usd or 0.0},
                recommendations=[
                    "Review and optimize retry logic",
                    "Implement circuit breaker pattern",
                    "Monitor provider status and health",
                    "Consider exponential backoff strategies",
                    "Implement fallback mechanisms"
                ],
                estimated_improvement={"retry_reduction_percent": 60.0},
                alternative_providers=self._get_alternative_providers(metrics.metadata.provider)
            )
            bottlenecks.append(bottleneck)
        
        # Store bottlenecks
        for bottleneck in bottlenecks:
            self.bottlenecks.append(bottleneck)
            self.prometheus_metrics['integration_bottlenecks'].labels(
                provider=bottleneck.provider.provider_name,
                severity=bottleneck.severity
            ).inc()
    
    def _get_alternative_providers(self, current_provider: ExternalProvider) -> List[str]:
        """Get alternative providers for the same integration type"""
        alternatives = []
        
        # Map common alternatives
        alternatives_map = {
            ProviderType.YOUTUBE: ["Vimeo", "Twitch"],
            ProviderType.STRIPE: ["PayPal", "Square"],
            ProviderType.AWS_S3: ["Google Cloud Storage", "Azure Blob"],
            ProviderType.SENDGRID: ["Mailgun", "Amazon SES"],
            ProviderType.OPENAI: ["Anthropic", "Hugging Face"]
        }
        
        return alternatives_map.get(current_provider.provider_type, [])
    
    async def _monitoring_loop(self):
        """Background monitoring loop"""
        while self.is_monitoring:
            try:
                # Monitor provider health
                await self._monitor_provider_health()
                
                # Monitor integration patterns
                await self._monitor_integration_patterns()
                
                # Monitor quota usage
                await self._monitor_quota_usage()
                
                # Clean up old data
                await self._cleanup_old_data()
                
                await asyncio.sleep(self.monitoring_interval)
                
            except Exception as e:
                logger.error(f"Error in integration monitoring loop: {e}")
                await asyncio.sleep(self.monitoring_interval)
    
    async def _monitor_provider_health(self):
        """Monitor external provider health"""
        try:
            for provider_name, provider in self.registered_providers.items():
                # Update provider health metrics
                reliability = self.provider_reliability.get(provider_name, {}).get(provider.integration_type.value, 100.0)
                
                self.prometheus_metrics['provider_reliability'].labels(
                    provider=provider_name,
                    integration_type=provider.integration_type.value
                ).set(reliability)
        
        except Exception as e:
            logger.error(f"Error monitoring provider health: {e}")
    
    async def _monitor_integration_patterns(self):
        """Monitor integration patterns for optimization opportunities"""
        try:
            with self._lock:
                for pattern, times in self.integration_patterns.items():
                    if len(times) > 10:  # Enough data points
                        avg_time = statistics.mean(times)
                        if avg_time > self.high_latency_threshold_ms:
                            logger.warning(f"Slow integration pattern: {pattern} - avg {avg_time:.2f}ms")
        
        except Exception as e:
            logger.error(f"Error monitoring integration patterns: {e}")
    
    async def _monitor_quota_usage(self):
        """Monitor API quota usage"""
        try:
            with self._lock:
                for quota_key, usage in self.quota_usage.items():
                    total_requests = usage.get("requests", 0)
                    successful_requests = usage.get("successful", 0)
                    
                    if total_requests > 0:
                        success_rate = (successful_requests / total_requests) * 100
                        if success_rate < self.thresholds['min_success_rate_percent']:
                            logger.warning(f"Low success rate for {quota_key}: {success_rate:.1f}%")
        
        except Exception as e:
            logger.error(f"Error monitoring quota usage: {e}")
    
    async def _cleanup_old_data(self):
        """Clean up old monitoring data"""
        cutoff_time = datetime.utcnow() - timedelta(hours=1)
        
        # Clean up old bottlenecks
        self.bottlenecks = [b for b in self.bottlenecks if b.timestamp > cutoff_time]
        
        # Clean up old requests
        old_requests = [req_id for req_id, metrics in self.active_requests.items() 
                       if metrics.timestamp < cutoff_time]
        for req_id in old_requests:
            del self.active_requests[req_id]
    
    def register_provider(self, provider: ExternalProvider):
        """Register an external provider"""
        with self._lock:
            self.registered_providers[provider.provider_name] = provider
            logger.info(f"External provider registered: {provider.provider_name} ({provider.provider_type.value})")
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """Get integration performance summary"""
        if not self.metrics_history:
            return {}
        
        recent_metrics = list(self.metrics_history)[-100:]  # Last 100 requests
        
        # Calculate averages
        avg_response_time = statistics.mean([m.total_time_ms for m in recent_metrics])
        success_rate = sum(1 for m in recent_metrics if m.success) / len(recent_metrics) * 100
        
        # Provider breakdown
        provider_breakdown = defaultdict(list)
        for metric in recent_metrics:
            provider_breakdown[metric.metadata.provider.provider_name].append(metric)
        
        # Cost analysis
        total_cost = sum(m.api_cost_usd for m in recent_metrics if m.api_cost_usd is not None)
        
        return {
            "overall_performance": {
                "average_response_time_ms": avg_response_time,
                "success_rate_percent": success_rate,
                "total_requests": len(recent_metrics),
                "total_cost_usd": total_cost,
                "registered_providers": len(self.registered_providers)
            },
            "provider_breakdown": {
                provider: {
                    "request_count": len(metrics),
                    "avg_response_time_ms": statistics.mean([m.total_time_ms for m in metrics]),
                    "success_rate_percent": sum(1 for m in metrics if m.success) / len(metrics) * 100,
                    "total_cost_usd": sum(m.api_cost_usd for m in metrics if m.api_cost_usd is not None)
                }
                for provider, metrics in provider_breakdown.items()
            },
            "active_bottlenecks": len([b for b in self.bottlenecks if b.timestamp > datetime.utcnow() - timedelta(minutes=5)]),
            "quota_usage": dict(self.quota_usage),
            "timestamp": datetime.utcnow().isoformat()
        }
    
    def get_bottleneck_report(self) -> List[Dict[str, Any]]:
        """Get detailed bottleneck report"""
        return [
            {
                "bottleneck_id": b.bottleneck_id,
                "provider": b.provider.provider_name,
                "provider_type": b.provider.provider_type.value,
                "integration_type": b.provider.integration_type.value,
                "type": b.bottleneck_type,
                "severity": b.severity,
                "description": b.description,
                "impact_percentage": b.impact_percentage,
                "affected_operations": b.affected_operations,
                "affected_users": b.affected_users,
                "provider_status": b.provider_status,
                "rate_limit_analysis": b.rate_limit_analysis,
                "cost_impact": b.cost_impact,
                "recommendations": b.recommendations,
                "estimated_improvement": b.estimated_improvement,
                "alternative_providers": b.alternative_providers,
                "timestamp": b.timestamp.isoformat()
            }
            for b in self.bottlenecks
        ]


def create_external_integration_profiler(
    monitoring_interval: float = 10.0,
    enable_rate_limit_tracking: bool = True,
    enable_cost_tracking: bool = True,
    high_latency_threshold_ms: float = 2000.0,
    start_monitoring: bool = False
) -> ExternalIntegrationProfiler:
    """
    Factory function to create external integration profiler
    
    Args:
        monitoring_interval: Monitoring interval in seconds
        enable_rate_limit_tracking: Enable rate limiting tracking
        enable_cost_tracking: Enable API cost tracking
        high_latency_threshold_ms: Threshold for high latency detection
        start_monitoring: Start monitoring immediately
    
    Returns:
        ExternalIntegrationProfiler: Configured integration profiler instance
    """
    profiler = ExternalIntegrationProfiler(
        monitoring_interval=monitoring_interval,
        enable_rate_limit_tracking=enable_rate_limit_tracking,
        enable_cost_tracking=enable_cost_tracking,
        high_latency_threshold_ms=high_latency_threshold_ms
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
async def example_external_integration_profiling():
    """Example of profiling Creator Economy external integrations"""
    profiler = create_external_integration_profiler(start_monitoring=True)
    
    # Register YouTube provider
    youtube_provider = ExternalProvider(
        provider_name="youtube_api",
        provider_type=ProviderType.YOUTUBE,
        integration_type=IntegrationType.SOCIAL_MEDIA,
        category=IntegrationCategory.CONTENT_DISTRIBUTION,
        base_url="https://www.googleapis.com/youtube/v3",
        api_version="v3",
        auth_method="oauth2",
        rate_limit_per_minute=1000,
        rate_limit_per_day=10000,
        expected_response_time_ms=500.0
    )
    
    profiler.register_provider(youtube_provider)
    
    # Example: Profile YouTube video upload
    async def upload_to_youtube(video_data: bytes, metadata: dict):
        # Simulate YouTube API call
        await asyncio.sleep(0.3)  # Simulate upload time
        return {
            "status_code": 200,
            "data": {
                "video_id": "abc123",
                "upload_status": "processed"
            },
            "rate_limit_remaining": 950,
            "api_cost": 0.05
        }
    
    request_metadata = IntegrationRequestMetadata(
        request_id="upload_video_456",
        provider=youtube_provider,
        operation_name="upload_video",
        endpoint_path="/videos",
        http_method="POST",
        payload_size_bytes=50 * 1024 * 1024,  # 50MB video
        headers_count=8,
        query_params_count=3,
        max_retries=2,
        cacheable=False,
        user_id="creator_789",
        creator_id="creator_789",
        business_operation="content_upload"
    )
    
    metrics = await profiler.profile_integration_request(
        request_metadata,
        upload_to_youtube,
        b"video_data",
        {"title": "My Gaming Video", "description": "Epic gameplay"}
    )
    
    print(f"External integration profiled:")
    print(f"- Total time: {metrics.total_time_ms:.2f}ms")
    print(f"- Auth time: {metrics.auth_time_ms:.2f}ms" if metrics.auth_time_ms else "- No auth timing")
    print(f"- API call time: {metrics.api_call_time_ms:.2f}ms" if metrics.api_call_time_ms else "- No API timing")
    print(f"- Retry count: {metrics.retry_count}")
    print(f"- API cost: ${metrics.api_cost_usd}" if metrics.api_cost_usd else "- No cost info")
    print(f"- Success: {metrics.success}")
    
    # Get performance summary
    summary = profiler.get_performance_summary()
    print(f"Performance summary: {json.dumps(summary, indent=2)}")
    
    await profiler.stop_monitoring()


if __name__ == "__main__":
    asyncio.run(example_external_integration_profiling())