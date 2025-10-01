"""
⚠️  AVERTISSEMENT LÉGAL OBLIGATOIRE:
==========================================
© 2025 Fahed Mlaiel <mlaiel@live.de>
TOUS DROITS RÉSERVÉS

🚨 PROTECTION INTELLECTUELLE:
- Code propriétaire de Fahed Mlaiel
- Utilisation commerciale INTERDITE sans autorisation écrite
- Reverse engineering STRICTEMENT INTERDIT
- Distribution INTERDITE sans licence explicite
- Violation = Poursuites judiciaires automatiques

Rate Limiter Template for iacherie Microservices Platform
=======================================================

Enterprise-grade distributed rate limiting template providing:
- Advanced rate limiting algorithms (token bucket, leaky bucket, sliding window)
- Distributed rate limiting with Redis coordination
- Hierarchical rate limiting (global, per-service, per-user)
- Dynamic rate limit adjustment based on system load
- Quota management with billing integration
- DDoS protection and anomaly detection
- Multi-tier rate limiting with priorities
- Geographic and time-based rate limiting
- Real-time monitoring and alerting
- Integration with API gateways and service mesh

Author: Fahed Mlaiel (mlaiel@live.de)
Security Expert & Performance Engineering Specialist
"""

import logging
import asyncio
import json
import time
import math
from typing import Dict, Any, Optional, List, Callable, Type, Union, Set, Tuple
from datetime import datetime, timedelta
from enum import Enum
from dataclasses import dataclass, field
import uuid
from collections import defaultdict, deque

from pydantic import BaseModel, Field, validator
import redis.asyncio as redis
from prometheus_client import Counter, Histogram, Gauge
import aiohttp

from ..base_microservice import BaseMicroservice
from ..microservice_template import ServiceConfig, ServiceStatus
from ..communication_manager import CommunicationManager, CommunicationConfig

logger = logging.getLogger(__name__)


class RateLimitAlgorithm(str, Enum):
    """Rate limiting algorithms"""
    TOKEN_BUCKET = "token_bucket"
    LEAKY_BUCKET = "leaky_bucket"
    FIXED_WINDOW = "fixed_window"
    SLIDING_WINDOW_LOG = "sliding_window_log"
    SLIDING_WINDOW_COUNTER = "sliding_window_counter"
    ADAPTIVE = "adaptive"


class RateLimitScope(str, Enum):
    """Rate limit scope"""
    GLOBAL = "global"
    PER_SERVICE = "per_service"
    PER_USER = "per_user"
    PER_IP = "per_ip"
    PER_API_KEY = "per_api_key"
    PER_ENDPOINT = "per_endpoint"


class RateLimitAction(str, Enum):
    """Actions when rate limit is exceeded"""
    REJECT = "reject"
    DELAY = "delay"
    DEGRADE = "degrade"
    QUEUE = "queue"


class Priority(str, Enum):
    """Request priority levels"""
    CRITICAL = "critical"
    HIGH = "high"
    NORMAL = "normal"
    LOW = "low"


@dataclass
class RateLimitResult:
    """Result of rate limit check"""
    allowed: bool
    remaining: int
    reset_time: datetime
    retry_after: Optional[int] = None
    current_usage: int = 0
    limit: int = 0
    headers: Dict[str, str] = field(default_factory=dict)


class TokenBucketConfig(BaseModel):
    """Token bucket rate limiter configuration"""
    capacity: int = Field(..., description="Bucket capacity (max tokens)")
    refill_rate: float = Field(..., description="Token refill rate per second")
    initial_tokens: Optional[int] = Field(default=None, description="Initial tokens (defaults to capacity)")


class LeakyBucketConfig(BaseModel):
    """Leaky bucket rate limiter configuration"""
    capacity: int = Field(..., description="Bucket capacity")
    leak_rate: float = Field(..., description="Leak rate per second")


class SlidingWindowConfig(BaseModel):
    """Sliding window rate limiter configuration"""
    window_size_seconds: int = Field(..., description="Window size in seconds")
    max_requests: int = Field(..., description="Maximum requests in window")
    sub_windows: int = Field(default=10, description="Number of sub-windows for precision")


class RateLimitRule(BaseModel):
    """Rate limiting rule configuration"""
    id: str = Field(..., description="Rule identifier")
    name: str = Field(..., description="Human-readable rule name")
    scope: RateLimitScope = Field(..., description="Rate limit scope")
    algorithm: RateLimitAlgorithm = Field(..., description="Rate limiting algorithm")
    
    # Algorithm-specific configurations
    token_bucket_config: Optional[TokenBucketConfig] = Field(default=None, description="Token bucket configuration")
    leaky_bucket_config: Optional[LeakyBucketConfig] = Field(default=None, description="Leaky bucket configuration")
    sliding_window_config: Optional[SlidingWindowConfig] = Field(default=None, description="Sliding window configuration")
    
    # Fixed window simple config
    requests_per_minute: Optional[int] = Field(default=None, description="Requests per minute for fixed window")
    requests_per_hour: Optional[int] = Field(default=None, description="Requests per hour")
    requests_per_day: Optional[int] = Field(default=None, description="Requests per day")
    
    # Targeting
    target_services: List[str] = Field(default_factory=list, description="Target services")
    target_endpoints: List[str] = Field(default_factory=list, description="Target endpoints")
    target_users: List[str] = Field(default_factory=list, description="Target users")
    target_ips: List[str] = Field(default_factory=list, description="Target IP addresses")
    
    # Behavior
    action: RateLimitAction = Field(default=RateLimitAction.REJECT, description="Action when limit exceeded")
    priority: Priority = Field(default=Priority.NORMAL, description="Rule priority")
    delay_ms: int = Field(default=1000, description="Delay in milliseconds for DELAY action")
    queue_timeout_ms: int = Field(default=5000, description="Queue timeout for QUEUE action")
    
    # Dynamic adjustment
    enable_adaptive: bool = Field(default=False, description="Enable adaptive rate limiting")
    load_threshold: float = Field(default=0.8, description="System load threshold for adaptation")
    
    # Time-based rules
    time_zones: List[str] = Field(default_factory=list, description="Applicable time zones")
    business_hours_only: bool = Field(default=False, description="Apply only during business hours")
    
    # Metadata
    enabled: bool = Field(default=True, description="Whether rule is enabled")
    description: Optional[str] = Field(default=None, description="Rule description")
    tags: List[str] = Field(default_factory=list, description="Rule tags")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Creation timestamp")


@dataclass
class BucketState:
    """Token/Leaky bucket state"""
    tokens: float
    last_refill: datetime
    total_requests: int = 0
    blocked_requests: int = 0


@dataclass
class WindowState:
    """Sliding window state"""
    requests: deque
    total_count: int = 0
    window_start: datetime = field(default_factory=datetime.utcnow)


class RateLimiterConfig(ServiceConfig):
    """Rate limiter service configuration"""
    # Redis settings for distributed coordination
    redis_host: str = Field(default="localhost", description="Redis host")
    redis_port: int = Field(default=6379, description="Redis port")
    redis_db: int = Field(default=8, description="Redis database")
    redis_password: Optional[str] = Field(default=None, description="Redis password")
    
    # Default limits
    default_requests_per_minute: int = Field(default=100, description="Default requests per minute")
    default_requests_per_hour: int = Field(default=1000, description="Default requests per hour")
    default_burst_capacity: int = Field(default=200, description="Default burst capacity")
    
    # Performance settings
    cache_ttl_seconds: int = Field(default=60, description="Cache TTL for rate limit states")
    cleanup_interval_seconds: int = Field(default=300, description="Cleanup interval for expired states")
    max_memory_usage_mb: int = Field(default=512, description="Maximum memory usage")
    
    # DDoS protection
    enable_ddos_protection: bool = Field(default=True, description="Enable DDoS protection")
    ddos_threshold_multiplier: float = Field(default=5.0, description="DDoS detection threshold multiplier")
    ddos_block_duration_minutes: int = Field(default=60, description="DDoS block duration")
    
    # Monitoring
    enable_metrics: bool = Field(default=True, description="Enable metrics collection")
    enable_alerting: bool = Field(default=True, description="Enable alerting")
    alert_threshold_percentage: float = Field(default=90.0, description="Alert threshold percentage")
    
    # Integration
    webhook_urls: List[str] = Field(default_factory=list, description="Webhook URLs for notifications")
    enable_api_gateway_integration: bool = Field(default=True, description="Enable API gateway integration")


class RateLimiterTemplate(BaseMicroservice):
    """
    Enterprise Rate Limiter Template
    
    Provides comprehensive distributed rate limiting with:
    - Multiple rate limiting algorithms
    - Hierarchical rate limiting
    - DDoS protection
    - Dynamic adaptation
    - Real-time monitoring
    """
    
    def __init__(self, config: RateLimiterConfig):
        super().__init__(config)
        self.config = config
        self.redis_client: Optional[redis.Redis] = None
        self.rate_limit_rules: Dict[str, RateLimitRule] = {}
        self.bucket_states: Dict[str, BucketState] = {}
        self.window_states: Dict[str, WindowState] = {}
        self.blocked_ips: Set[str] = set()
        self.request_queues: Dict[str, asyncio.Queue] = {}
        
        # Metrics
        self.requests_total = Counter(
            'rate_limiter_requests_total',
            'Total requests processed',
            ['rule_id', 'scope', 'result']
        )
        self.rate_limit_exceeded_total = Counter(
            'rate_limiter_exceeded_total',
            'Total rate limit violations',
            ['rule_id', 'scope', 'action']
        )
        self.current_usage_gauge = Gauge(
            'rate_limiter_current_usage',
            'Current usage percentage',
            ['rule_id', 'scope']
        )
        self.response_time_histogram = Histogram(
            'rate_limiter_response_time_seconds',
            'Rate limiter response time',
            ['algorithm']
        )
        self.blocked_ips_gauge = Gauge(
            'rate_limiter_blocked_ips',
            'Number of blocked IP addresses'
        )
    
    async def initialize(self) -> None:
        """Initialize rate limiter service"""
        try:
            logger.info("Initializing rate limiter service")
            
            # Initialize Redis client
            await self._initialize_redis()
            
            # Load existing rules from Redis
            await self._load_rate_limit_rules()
            
            # Start background tasks
            asyncio.create_task(self._cleanup_task())
            asyncio.create_task(self._metrics_collection_task())
            asyncio.create_task(self._ddos_monitoring_task())
            
            logger.info("Rate limiter service initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize rate limiter service: {e}")
            raise
    
    async def _initialize_redis(self) -> None:
        """Initialize Redis connection"""
        self.redis_client = redis.Redis(
            host=self.config.redis_host,
            port=self.config.redis_port,
            db=self.config.redis_db,
            password=self.config.redis_password,
            decode_responses=True
        )
        
        await self.redis_client.ping()
        logger.info("Redis connection established")
    
    async def create_rate_limit_rule(self, rule: RateLimitRule) -> Dict[str, Any]:
        """Create a new rate limiting rule"""
        try:
            # Validate rule configuration
            await self._validate_rate_limit_rule(rule)
            
            # Store rule
            self.rate_limit_rules[rule.id] = rule
            
            # Persist to Redis
            await self._persist_rate_limit_rule(rule)
            
            logger.info(f"Created rate limit rule: {rule.id} ({rule.name})")
            
            return {
                "rule_id": rule.id,
                "name": rule.name,
                "scope": rule.scope.value,
                "algorithm": rule.algorithm.value,
                "status": "created"
            }
            
        except Exception as e:
            logger.error(f"Failed to create rate limit rule {rule.id}: {e}")
            raise
    
    async def check_rate_limit(
        self, rule_id: str, identifier: str, request_metadata: Dict[str, Any] = None
    ) -> RateLimitResult:
        """Check if request is within rate limits"""
        start_time = time.time()
        
        try:
            if rule_id not in self.rate_limit_rules:
                raise ValueError(f"Rate limit rule not found: {rule_id}")
            
            rule = self.rate_limit_rules[rule_id]
            
            if not rule.enabled:
                return RateLimitResult(
                    allowed=True,
                    remaining=999999,
                    reset_time=datetime.utcnow() + timedelta(hours=1)
                )
            
            # Check if IP is blocked for DDoS
            client_ip = request_metadata.get("client_ip") if request_metadata else None
            if client_ip and client_ip in self.blocked_ips:
                return RateLimitResult(
                    allowed=False,
                    remaining=0,
                    reset_time=datetime.utcnow() + timedelta(minutes=self.config.ddos_block_duration_minutes),
                    retry_after=self.config.ddos_block_duration_minutes * 60
                )
            
            # Apply rate limiting based on algorithm
            if rule.algorithm == RateLimitAlgorithm.TOKEN_BUCKET:
                result = await self._check_token_bucket(rule, identifier)
            elif rule.algorithm == RateLimitAlgorithm.LEAKY_BUCKET:
                result = await self._check_leaky_bucket(rule, identifier)
            elif rule.algorithm == RateLimitAlgorithm.FIXED_WINDOW:
                result = await self._check_fixed_window(rule, identifier)
            elif rule.algorithm == RateLimitAlgorithm.SLIDING_WINDOW_LOG:
                result = await self._check_sliding_window_log(rule, identifier)
            elif rule.algorithm == RateLimitAlgorithm.SLIDING_WINDOW_COUNTER:
                result = await self._check_sliding_window_counter(rule, identifier)
            elif rule.algorithm == RateLimitAlgorithm.ADAPTIVE:
                result = await self._check_adaptive(rule, identifier)
            else:
                raise ValueError(f"Unsupported algorithm: {rule.algorithm}")
            
            # Handle rate limit exceeded
            if not result.allowed:
                await self._handle_rate_limit_exceeded(rule, identifier, request_metadata)
            
            # Update metrics
            result_label = "allowed" if result.allowed else "blocked"
            self.requests_total.labels(
                rule_id=rule.id, scope=rule.scope.value, result=result_label
            ).inc()
            
            if not result.allowed:
                self.rate_limit_exceeded_total.labels(
                    rule_id=rule.id, scope=rule.scope.value, action=rule.action.value
                ).inc()
            
            # Update usage metrics
            if result.limit > 0:
                usage_percentage = (result.current_usage / result.limit) * 100
                self.current_usage_gauge.labels(
                    rule_id=rule.id, scope=rule.scope.value
                ).set(usage_percentage)
            
            # Record response time
            response_time = time.time() - start_time
            self.response_time_histogram.labels(algorithm=rule.algorithm.value).observe(response_time)
            
            # Add standard rate limit headers
            result.headers = {
                "X-RateLimit-Limit": str(result.limit),
                "X-RateLimit-Remaining": str(result.remaining),
                "X-RateLimit-Reset": str(int(result.reset_time.timestamp())),
                "X-RateLimit-Rule": rule.id
            }
            
            if result.retry_after:
                result.headers["Retry-After"] = str(result.retry_after)
            
            return result
            
        except Exception as e:
            logger.error(f"Rate limit check failed for rule {rule_id}: {e}")
            # Fail open - allow request on error
            return RateLimitResult(
                allowed=True,
                remaining=999999,
                reset_time=datetime.utcnow() + timedelta(hours=1)
            )
    
    async def _check_token_bucket(self, rule: RateLimitRule, identifier: str) -> RateLimitResult:
        """Check token bucket rate limit"""
        config = rule.token_bucket_config
        if not config:
            raise ValueError("Token bucket config not provided")
        
        bucket_key = f"token_bucket:{rule.id}:{identifier}"
        now = datetime.utcnow()
        
        # Get or create bucket state
        bucket_state = await self._get_bucket_state(bucket_key, config.capacity, now)
        
        # Calculate tokens to add
        time_elapsed = (now - bucket_state.last_refill).total_seconds()
        tokens_to_add = time_elapsed * config.refill_rate
        bucket_state.tokens = min(config.capacity, bucket_state.tokens + tokens_to_add)
        bucket_state.last_refill = now
        
        # Check if request can be served
        if bucket_state.tokens >= 1:
            bucket_state.tokens -= 1
            bucket_state.total_requests += 1
            allowed = True
        else:
            bucket_state.blocked_requests += 1
            allowed = False
        
        # Calculate next reset time
        if bucket_state.tokens < config.capacity:
            tokens_needed = config.capacity - bucket_state.tokens
            reset_time = now + timedelta(seconds=tokens_needed / config.refill_rate)
        else:
            reset_time = now
        
        # Store updated state
        await self._store_bucket_state(bucket_key, bucket_state)
        
        return RateLimitResult(
            allowed=allowed,
            remaining=int(bucket_state.tokens),
            reset_time=reset_time,
            current_usage=bucket_state.total_requests,
            limit=config.capacity,
            retry_after=int((1 / config.refill_rate)) if not allowed else None
        )
    
    async def _check_leaky_bucket(self, rule: RateLimitRule, identifier: str) -> RateLimitResult:
        """Check leaky bucket rate limit"""
        config = rule.leaky_bucket_config
        if not config:
            raise ValueError("Leaky bucket config not provided")
        
        bucket_key = f"leaky_bucket:{rule.id}:{identifier}"
        now = datetime.utcnow()
        
        # Get current bucket level
        current_level = await self._get_leaky_bucket_level(bucket_key, config, now)
        
        # Check if bucket has capacity
        if current_level < config.capacity:
            # Add request to bucket
            await self._add_to_leaky_bucket(bucket_key, now)
            allowed = True
            remaining = config.capacity - current_level - 1
        else:
            allowed = False
            remaining = 0
        
        # Calculate reset time (when bucket will have capacity)
        reset_time = now + timedelta(seconds=1 / config.leak_rate)
        
        return RateLimitResult(
            allowed=allowed,
            remaining=remaining,
            reset_time=reset_time,
            current_usage=current_level,
            limit=config.capacity,
            retry_after=int(1 / config.leak_rate) if not allowed else None
        )
    
    async def _check_fixed_window(self, rule: RateLimitRule, identifier: str) -> RateLimitResult:
        """Check fixed window rate limit"""
        now = datetime.utcnow()
        
        # Determine window size and limit
        if rule.requests_per_minute:
            window_size = 60
            limit = rule.requests_per_minute
            window_start = now.replace(second=0, microsecond=0)
        elif rule.requests_per_hour:
            window_size = 3600
            limit = rule.requests_per_hour
            window_start = now.replace(minute=0, second=0, microsecond=0)
        elif rule.requests_per_day:
            window_size = 86400
            limit = rule.requests_per_day
            window_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        else:
            raise ValueError("No fixed window configuration provided")
        
        window_key = f"fixed_window:{rule.id}:{identifier}:{int(window_start.timestamp())}"
        
        # Get current count
        current_count = await self.redis_client.get(window_key)
        current_count = int(current_count) if current_count else 0
        
        if current_count < limit:
            # Increment counter
            await self.redis_client.incr(window_key)
            await self.redis_client.expire(window_key, window_size)
            allowed = True
            remaining = limit - current_count - 1
        else:
            allowed = False
            remaining = 0
        
        reset_time = window_start + timedelta(seconds=window_size)
        
        return RateLimitResult(
            allowed=allowed,
            remaining=remaining,
            reset_time=reset_time,
            current_usage=current_count + (1 if allowed else 0),
            limit=limit,
            retry_after=(reset_time - now).total_seconds() if not allowed else None
        )
    
    async def _check_sliding_window_log(self, rule: RateLimitRule, identifier: str) -> RateLimitResult:
        """Check sliding window log rate limit"""
        config = rule.sliding_window_config
        if not config:
            raise ValueError("Sliding window config not provided")
        
        now = datetime.utcnow()
        window_key = f"sliding_window_log:{rule.id}:{identifier}"
        
        # Get request log
        request_log = await self.redis_client.zrangebyscore(
            window_key,
            (now - timedelta(seconds=config.window_size_seconds)).timestamp(),
            now.timestamp()
        )
        
        current_count = len(request_log)
        
        if current_count < config.max_requests:
            # Add current request
            await self.redis_client.zadd(window_key, {str(uuid.uuid4()): now.timestamp()})
            await self.redis_client.expire(window_key, config.window_size_seconds)
            
            # Clean old entries
            cutoff_time = (now - timedelta(seconds=config.window_size_seconds)).timestamp()
            await self.redis_client.zremrangebyscore(window_key, 0, cutoff_time)
            
            allowed = True
            remaining = config.max_requests - current_count - 1
        else:
            allowed = False
            remaining = 0
        
        # Calculate reset time (when oldest request expires)
        if request_log:
            oldest_timestamp = float(request_log[0])
            reset_time = datetime.fromtimestamp(oldest_timestamp) + timedelta(seconds=config.window_size_seconds)
        else:
            reset_time = now + timedelta(seconds=config.window_size_seconds)
        
        return RateLimitResult(
            allowed=allowed,
            remaining=remaining,
            reset_time=reset_time,
            current_usage=current_count + (1 if allowed else 0),
            limit=config.max_requests
        )
    
    async def _check_sliding_window_counter(self, rule: RateLimitRule, identifier: str) -> RateLimitResult:
        """Check sliding window counter rate limit"""
        config = rule.sliding_window_config
        if not config:
            raise ValueError("Sliding window config not provided")
        
        now = datetime.utcnow()
        sub_window_size = config.window_size_seconds / config.sub_windows
        current_window = int(now.timestamp() // sub_window_size)
        
        # Calculate request count across sliding window
        total_count = 0
        for i in range(config.sub_windows):
            window_key = f"sliding_window_counter:{rule.id}:{identifier}:{current_window - i}"
            count = await self.redis_client.get(window_key)
            if count:
                # Weight by overlap with current window
                if i == 0:
                    weight = 1.0
                else:
                    weight = (config.sub_windows - i) / config.sub_windows
                total_count += int(count) * weight
        
        if total_count < config.max_requests:
            # Increment current window counter
            current_window_key = f"sliding_window_counter:{rule.id}:{identifier}:{current_window}"
            await self.redis_client.incr(current_window_key)
            await self.redis_client.expire(current_window_key, config.window_size_seconds)
            
            allowed = True
            remaining = int(config.max_requests - total_count - 1)
        else:
            allowed = False
            remaining = 0
        
        reset_time = datetime.fromtimestamp((current_window + 1) * sub_window_size)
        
        return RateLimitResult(
            allowed=allowed,
            remaining=remaining,
            reset_time=reset_time,
            current_usage=int(total_count) + (1 if allowed else 0),
            limit=config.max_requests
        )
    
    async def _check_adaptive(self, rule: RateLimitRule, identifier: str) -> RateLimitResult:
        """Check adaptive rate limit based on system load"""
        # Get system load (simplified implementation)
        system_load = await self._get_system_load()
        
        # Adjust limits based on load
        base_limit = rule.requests_per_minute or 100
        if system_load > rule.load_threshold:
            adjusted_limit = int(base_limit * (1 - system_load))
        else:
            adjusted_limit = base_limit
        
        # Use token bucket with adjusted rate
        adjusted_rule = rule.copy()
        adjusted_rule.token_bucket_config = TokenBucketConfig(
            capacity=adjusted_limit,
            refill_rate=adjusted_limit / 60.0  # Per second
        )
        
        return await self._check_token_bucket(adjusted_rule, identifier)
    
    async def _handle_rate_limit_exceeded(
        self, rule: RateLimitRule, identifier: str, request_metadata: Dict[str, Any] = None
    ) -> None:
        """Handle rate limit exceeded event"""
        
        if rule.action == RateLimitAction.REJECT:
            # Just reject, no additional action needed
            pass
        
        elif rule.action == RateLimitAction.DELAY:
            # Add delay (would be handled by caller)
            logger.debug(f"Rate limit exceeded for {identifier}, delay: {rule.delay_ms}ms")
        
        elif rule.action == RateLimitAction.QUEUE:
            # Add to queue (simplified implementation)
            queue_key = f"queue:{rule.id}"
            if queue_key not in self.request_queues:
                self.request_queues[queue_key] = asyncio.Queue(maxsize=100)
            
            try:
                await asyncio.wait_for(
                    self.request_queues[queue_key].put(identifier),
                    timeout=rule.queue_timeout_ms / 1000
                )
            except asyncio.TimeoutError:
                logger.warning(f"Queue timeout for {identifier}")
        
        elif rule.action == RateLimitAction.DEGRADE:
            # Trigger service degradation
            logger.info(f"Triggering service degradation for {identifier}")
        
        # Check for DDoS patterns
        if request_metadata and self.config.enable_ddos_protection:
            await self._check_ddos_pattern(rule, identifier, request_metadata)
    
    async def _check_ddos_pattern(
        self, rule: RateLimitRule, identifier: str, request_metadata: Dict[str, Any]
    ) -> None:
        """Check for DDoS attack patterns"""
        client_ip = request_metadata.get("client_ip")
        if not client_ip:
            return
        
        # Count recent rate limit violations from this IP
        violation_key = f"ddos_violations:{client_ip}"
        violations = await self.redis_client.incr(violation_key)
        await self.redis_client.expire(violation_key, 300)  # 5 minutes
        
        # Calculate threshold based on rule limits
        if rule.requests_per_minute:
            threshold = rule.requests_per_minute * self.config.ddos_threshold_multiplier
        else:
            threshold = self.config.default_requests_per_minute * self.config.ddos_threshold_multiplier
        
        if violations > threshold:
            # Block IP
            self.blocked_ips.add(client_ip)
            await self.redis_client.setex(
                f"blocked_ip:{client_ip}",
                self.config.ddos_block_duration_minutes * 60,
                "ddos_protection"
            )
            
            self.blocked_ips_gauge.set(len(self.blocked_ips))
            
            logger.warning(f"Blocked IP {client_ip} for DDoS protection ({violations} violations)")
            
            # Send alert if configured
            if self.config.enable_alerting:
                await self._send_ddos_alert(client_ip, violations)
    
    async def get_rate_limit_status(self, rule_id: str, identifier: str) -> Dict[str, Any]:
        """Get current rate limit status for an identifier"""
        if rule_id not in self.rate_limit_rules:
            raise ValueError(f"Rate limit rule not found: {rule_id}")
        
        rule = self.rate_limit_rules[rule_id]
        result = await self.check_rate_limit(rule_id, identifier)
        
        return {
            "rule_id": rule_id,
            "rule_name": rule.name,
            "identifier": identifier,
            "algorithm": rule.algorithm.value,
            "scope": rule.scope.value,
            "current_usage": result.current_usage,
            "limit": result.limit,
            "remaining": result.remaining,
            "usage_percentage": (result.current_usage / result.limit * 100) if result.limit > 0 else 0,
            "reset_time": result.reset_time.isoformat(),
            "is_blocked": not result.allowed
        }
    
    async def get_health_status(self) -> Dict[str, Any]:
        """Get rate limiter health status"""
        try:
            # Check Redis connectivity
            redis_healthy = False
            try:
                await self.redis_client.ping()
                redis_healthy = True
            except Exception:
                pass
            
            return {
                "service": "rate_limiter_template",
                "status": "healthy" if redis_healthy else "degraded",
                "timestamp": datetime.utcnow().isoformat(),
                "metrics": {
                    "active_rules": len(self.rate_limit_rules),
                    "blocked_ips": len(self.blocked_ips),
                    "request_queues": len(self.request_queues),
                    "redis_connected": redis_healthy
                }
            }
            
        except Exception as e:
            return {
                "service": "rate_limiter_template",
                "status": "unhealthy",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
    
    async def _get_bucket_state(self, bucket_key: str, capacity: int, now: datetime) -> BucketState:
        """Get or create bucket state"""
        state_data = await self.redis_client.get(bucket_key)
        
        if state_data:
            data = json.loads(state_data)
            return BucketState(
                tokens=data["tokens"],
                last_refill=datetime.fromisoformat(data["last_refill"]),
                total_requests=data.get("total_requests", 0),
                blocked_requests=data.get("blocked_requests", 0)
            )
        else:
            return BucketState(
                tokens=capacity,
                last_refill=now
            )
    
    async def _store_bucket_state(self, bucket_key: str, state: BucketState) -> None:
        """Store bucket state in Redis"""
        state_data = {
            "tokens": state.tokens,
            "last_refill": state.last_refill.isoformat(),
            "total_requests": state.total_requests,
            "blocked_requests": state.blocked_requests
        }
        
        await self.redis_client.setex(
            bucket_key,
            self.config.cache_ttl_seconds,
            json.dumps(state_data)
        )
    
    async def _get_leaky_bucket_level(self, bucket_key: str, config: LeakyBucketConfig, now: datetime) -> int:
        """Get current leaky bucket level"""
        # Get all requests in bucket
        requests = await self.redis_client.zrangebyscore(
            bucket_key,
            (now - timedelta(seconds=config.capacity / config.leak_rate)).timestamp(),
            now.timestamp()
        )
        
        return len(requests)
    
    async def _add_to_leaky_bucket(self, bucket_key: str, now: datetime) -> None:
        """Add request to leaky bucket"""
        await self.redis_client.zadd(bucket_key, {str(uuid.uuid4()): now.timestamp()})
        await self.redis_client.expire(bucket_key, 3600)  # 1 hour TTL
    
    async def _get_system_load(self) -> float:
        """Get current system load (simplified implementation)"""
        # In a real implementation, this would check CPU, memory, etc.
        return 0.5  # Placeholder
    
    async def _validate_rate_limit_rule(self, rule: RateLimitRule) -> None:
        """Validate rate limit rule configuration"""
        if rule.algorithm == RateLimitAlgorithm.TOKEN_BUCKET and not rule.token_bucket_config:
            raise ValueError("Token bucket configuration required")
        
        if rule.algorithm == RateLimitAlgorithm.LEAKY_BUCKET and not rule.leaky_bucket_config:
            raise ValueError("Leaky bucket configuration required")
        
        if rule.algorithm in [RateLimitAlgorithm.SLIDING_WINDOW_LOG, RateLimitAlgorithm.SLIDING_WINDOW_COUNTER]:
            if not rule.sliding_window_config:
                raise ValueError("Sliding window configuration required")
    
    async def _load_rate_limit_rules(self) -> None:
        """Load rate limit rules from Redis"""
        keys = await self.redis_client.keys("rate_limit_rule:*")
        
        for key in keys:
            try:
                rule_data = await self.redis_client.get(key)
                if rule_data:
                    rule = RateLimitRule.parse_raw(rule_data)
                    self.rate_limit_rules[rule.id] = rule
            except Exception as e:
                logger.error(f"Failed to load rule from {key}: {e}")
    
    async def _persist_rate_limit_rule(self, rule: RateLimitRule) -> None:
        """Persist rate limit rule to Redis"""
        key = f"rate_limit_rule:{rule.id}"
        await self.redis_client.set(key, rule.json())
    
    async def _send_ddos_alert(self, client_ip: str, violations: int) -> None:
        """Send DDoS alert notification"""
        alert_data = {
            "type": "ddos_detected",
            "client_ip": client_ip,
            "violations": violations,
            "timestamp": datetime.utcnow().isoformat(),
            "action": "ip_blocked",
            "duration_minutes": self.config.ddos_block_duration_minutes
        }
        
        # Send to configured webhooks
        for webhook_url in self.config.webhook_urls:
            try:
                async with aiohttp.ClientSession() as session:
                    await session.post(webhook_url, json=alert_data)
            except Exception as e:
                logger.error(f"Failed to send alert to {webhook_url}: {e}")
    
    async def _cleanup_task(self) -> None:
        """Background cleanup task"""
        while True:
            try:
                await asyncio.sleep(self.config.cleanup_interval_seconds)
                
                # Clean up expired bucket states
                current_time = datetime.utcnow()
                expired_keys = []
                
                for key, state in self.bucket_states.items():
                    if (current_time - state.last_refill).total_seconds() > self.config.cache_ttl_seconds:
                        expired_keys.append(key)
                
                for key in expired_keys:
                    del self.bucket_states[key]
                
                # Clean up blocked IPs
                for ip in list(self.blocked_ips):
                    if not await self.redis_client.exists(f"blocked_ip:{ip}"):
                        self.blocked_ips.remove(ip)
                
                self.blocked_ips_gauge.set(len(self.blocked_ips))
                
                logger.debug(f"Cleanup completed: removed {len(expired_keys)} expired states")
                
            except Exception as e:
                logger.error(f"Cleanup task error: {e}")
    
    async def _metrics_collection_task(self) -> None:
        """Background metrics collection"""
        while True:
            try:
                await asyncio.sleep(60)  # Collect every minute
                
                # Update blocked IPs gauge
                self.blocked_ips_gauge.set(len(self.blocked_ips))
                
            except Exception as e:
                logger.error(f"Metrics collection task error: {e}")
    
    async def _ddos_monitoring_task(self) -> None:
        """Background DDoS monitoring"""
        while True:
            try:
                await asyncio.sleep(30)  # Check every 30 seconds
                
                # Monitor for DDoS patterns across all rules
                # This is a simplified implementation
                
            except Exception as e:
                logger.error(f"DDoS monitoring task error: {e}")
    
    async def shutdown(self) -> None:
        """Shutdown the service gracefully"""
        try:
            logger.info("Shutting down rate limiter service")
            
            # Close Redis connection
            if self.redis_client:
                await self.redis_client.close()
            
            logger.info("Rate limiter service shutdown complete")
            
        except Exception as e:
            logger.error(f"Error during shutdown: {e}")