#!/usr/bin/env python3
"""
⚡ Rate Limiting Middleware Template - Enterprise Performance & Security
🏗️ Architecture: iacherie Creator Economy Platform
🔒 Protection IP: © 2025 Fahed Mlaiel <mlaiel@live.de>

🚨 AVERTISSEMENT LÉGAL:
==========================================
© 2025 Fahed Mlaiel <mlaiel@live.de>
TOUS DROITS RÉSERVÉS

🚨 PROTECTION INTELLECTUELLE:
- Code propriétaire de Fahed Mlaiel
- Utilisation commerciale INTERDITE sans autorisation écrite
- Reverse engineering STRICTEMENT INTERDIT
- Distribution INTERDITE sans licence explicite
- Violation = Poursuites judiciaires automatiques

🏢 USAGE ENTREPRISE:
- Licence entreprise disponible sur demande
- Support technique inclus avec licence
- Maintenance et mises à jour assurées
- Formation équipe technique fournie
"""

from typing import Dict, List, Optional, Set, Union, Any, Callable, Tuple
from fastapi import FastAPI, Request, Response, HTTPException
from fastapi.middleware.base import BaseHTTPMiddleware
from fastapi.responses import JSONResponse
import time
import asyncio
import json
import hashlib
from datetime import datetime, timedelta
from collections import defaultdict, deque
import logging
from dataclasses import dataclass, field
from enum import Enum
import redis
import math

# Expert Team: Lead Dev IA + Backend Senior + Performance Expert + DevOps Engineer
__author__ = "Fahed Mlaiel"
__copyright__ = "© 2025 Fahed Mlaiel. All rights reserved."
__license__ = "Proprietary - Commercial license required"
__version__ = "1.0.0"
__email__ = "mlaiel@live.de"


class RateLimitStrategy(str, Enum):
    """Rate limiting strategies"""
    FIXED_WINDOW = "fixed_window"
    SLIDING_WINDOW = "sliding_window"
    TOKEN_BUCKET = "token_bucket"
    LEAKY_BUCKET = "leaky_bucket"
    ADAPTIVE = "adaptive"


class RateLimitScope(str, Enum):
    """Rate limiting scope"""
    IP = "ip"
    USER = "user"
    API_KEY = "api_key"
    ENDPOINT = "endpoint"
    GLOBAL = "global"
    CUSTOM = "custom"


class RateLimitAction(str, Enum):
    """Actions when rate limit is exceeded"""
    BLOCK = "block"
    DELAY = "delay"
    WARN = "warn"
    DEGRADE = "degrade"


class RateLimitTier(str, Enum):
    """Rate limiting tiers for different user types"""
    FREE = "free"
    BASIC = "basic"
    PREMIUM = "premium"
    ENTERPRISE = "enterprise"
    CREATOR = "creator"
    ADMIN = "admin"


@dataclass
class RateLimitRule:
    """Individual rate limiting rule"""
    name: str
    scope: RateLimitScope
    strategy: RateLimitStrategy
    limit: int  # requests per window
    window: int  # window size in seconds
    action: RateLimitAction = RateLimitAction.BLOCK
    tier: Optional[RateLimitTier] = None
    path_pattern: Optional[str] = None
    method: Optional[str] = None
    burst_allowance: int = 0  # additional requests allowed in burst
    custom_identifier: Optional[Callable] = None
    priority: int = 100  # lower number = higher priority


@dataclass
class RateLimitConfig:
    """Enterprise rate limiting configuration"""
    # Default rules
    default_rules: List[RateLimitRule] = field(default_factory=list)
    
    # Storage backend
    use_redis: bool = False
    redis_url: Optional[str] = None
    redis_key_prefix: str = "ratelimit:"
    
    # Global settings
    enable_global_rate_limiting: bool = True
    global_requests_per_minute: int = 10000
    
    # IP-based limiting
    enable_ip_rate_limiting: bool = True
    ip_requests_per_minute: int = 100
    ip_burst_allowance: int = 20
    
    # User-based limiting (requires authentication)
    enable_user_rate_limiting: bool = True
    user_requests_per_minute: int = 200
    
    # API key limiting
    enable_api_key_limiting: bool = True
    api_key_requests_per_minute: int = 1000
    
    # Endpoint-specific limiting
    enable_endpoint_limiting: bool = True
    
    # Adaptive limiting
    enable_adaptive_limiting: bool = True
    adaptive_threshold: float = 0.8  # CPU/memory threshold
    adaptive_scale_factor: float = 0.5  # scale down factor
    
    # Security features
    enable_progressive_delays: bool = True
    enable_blacklist: bool = True
    auto_blacklist_threshold: int = 10  # violations before blacklist
    blacklist_duration: int = 3600  # 1 hour
    
    # Whitelist
    whitelisted_ips: Set[str] = field(default_factory=set)
    whitelisted_user_agents: Set[str] = field(default_factory=set)
    whitelisted_api_keys: Set[str] = field(default_factory=set)
    
    # Creator-specific settings
    creator_enhanced_limits: bool = True
    creator_upload_limit: int = 50  # per hour
    creator_api_limit: int = 500  # per minute
    
    # Monitoring and alerting
    enable_metrics: bool = True
    enable_alerts: bool = True
    alert_threshold: float = 0.9  # alert when 90% of limit reached
    
    # Response customization
    include_rate_limit_headers: bool = True
    custom_error_message: Optional[str] = None
    custom_error_code: int = 429


@dataclass
class RateLimitBucket:
    """Rate limit bucket for token bucket algorithm"""
    capacity: int
    tokens: float
    last_refill: float
    refill_rate: float  # tokens per second
    
    def refill(self, current_time: float):
        """Refill tokens based on time elapsed"""
        if self.last_refill == 0:
            self.last_refill = current_time
            return
        
        elapsed = current_time - self.last_refill
        tokens_to_add = elapsed * self.refill_rate
        self.tokens = min(self.capacity, self.tokens + tokens_to_add)
        self.last_refill = current_time
    
    def consume(self, tokens: int = 1) -> bool:
        """Try to consume tokens from bucket"""
        if self.tokens >= tokens:
            self.tokens -= tokens
            return True
        return False


@dataclass
class RateLimitWindow:
    """Rate limit window for sliding window algorithm"""
    limit: int
    window_size: int
    requests: deque = field(default_factory=deque)
    
    def add_request(self, timestamp: float) -> bool:
        """Add request to window and check if limit exceeded"""
        current_time = timestamp
        cutoff_time = current_time - self.window_size
        
        # Remove old requests
        while self.requests and self.requests[0] <= cutoff_time:
            self.requests.popleft()
        
        # Check if we can add new request
        if len(self.requests) < self.limit:
            self.requests.append(current_time)
            return True
        
        return False


@dataclass
class RateLimitMetrics:
    """Rate limiting metrics"""
    total_requests: int = 0
    rate_limited_requests: int = 0
    blocked_requests: int = 0
    delayed_requests: int = 0
    warnings_issued: int = 0
    blacklisted_ips: int = 0
    adaptive_adjustments: int = 0
    
    # Per-tier metrics
    tier_metrics: Dict[str, Dict[str, int]] = field(default_factory=dict)
    
    # Per-endpoint metrics
    endpoint_metrics: Dict[str, Dict[str, int]] = field(default_factory=dict)
    
    @property
    def rate_limit_percentage(self) -> float:
        if self.total_requests == 0:
            return 0.0
        return (self.rate_limited_requests / self.total_requests) * 100


class RateLimitingMiddleware(BaseHTTPMiddleware):
    """
    🛡️ Enterprise Rate Limiting Middleware
    
    Features:
    - Multiple rate limiting algorithms
    - Multi-tier user support
    - Adaptive rate limiting based on system load
    - Progressive delay mechanisms
    - Auto-blacklisting for abuse
    - Creator-specific optimizations
    - Real-time metrics and alerts
    - Redis backend support
    - Custom rate limiting rules
    """
    
    def __init__(
        self,
        app: FastAPI,
        config: Optional[RateLimitConfig] = None,
        logger: Optional[logging.Logger] = None
    ):
        super().__init__(app)
        self.config = config or RateLimitConfig()
        self.logger = logger or self._setup_logger()
        
        # Storage backends
        self.redis_client = None
        if self.config.use_redis:
            self._setup_redis()
        
        # In-memory storage (fallback or primary)
        self.buckets: Dict[str, RateLimitBucket] = {}
        self.windows: Dict[str, RateLimitWindow] = {}
        self.blacklisted_ips: Dict[str, datetime] = {}
        self.violation_counts: Dict[str, int] = defaultdict(int)
        
        # Metrics
        self.metrics = RateLimitMetrics()
        
        # System load monitoring for adaptive limiting
        self.system_load = 0.0
        self.last_load_check = 0.0
        
        # Setup default rules
        self._setup_default_rules()
        
        self.logger.info(f"Rate Limiting initialized with {len(self.config.default_rules)} rules")
    
    def _setup_logger(self) -> logging.Logger:
        """Setup rate limiting logger"""
        logger = logging.getLogger("rate_limiting")
        logger.setLevel(logging.INFO)
        
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
        
        return logger
    
    def _setup_redis(self):
        """Setup Redis connection for distributed rate limiting"""
        try:
            if self.config.redis_url:
                self.redis_client = redis.from_url(self.config.redis_url)
            else:
                self.redis_client = redis.Redis(host='localhost', port=6379, db=0)
            
            # Test connection
            self.redis_client.ping()
            self.logger.info("Redis connection established for distributed rate limiting")
        except Exception as e:
            self.logger.warning(f"Failed to connect to Redis: {e}. Using in-memory storage.")
            self.redis_client = None
    
    def _setup_default_rules(self):
        """Setup default rate limiting rules"""
        if not self.config.default_rules:
            self.config.default_rules = [
                # Global rate limiting
                RateLimitRule(
                    name="global_limit",
                    scope=RateLimitScope.GLOBAL,
                    strategy=RateLimitStrategy.SLIDING_WINDOW,
                    limit=self.config.global_requests_per_minute,
                    window=60,
                    priority=1
                ),
                
                # IP-based limiting
                RateLimitRule(
                    name="ip_limit",
                    scope=RateLimitScope.IP,
                    strategy=RateLimitStrategy.TOKEN_BUCKET,
                    limit=self.config.ip_requests_per_minute,
                    window=60,
                    burst_allowance=self.config.ip_burst_allowance,
                    priority=10
                ),
                
                # User-based limiting
                RateLimitRule(
                    name="user_limit",
                    scope=RateLimitScope.USER,
                    strategy=RateLimitStrategy.SLIDING_WINDOW,
                    limit=self.config.user_requests_per_minute,
                    window=60,
                    priority=20
                ),
                
                # API key limiting
                RateLimitRule(
                    name="api_key_limit",
                    scope=RateLimitScope.API_KEY,
                    strategy=RateLimitStrategy.SLIDING_WINDOW,
                    limit=self.config.api_key_requests_per_minute,
                    window=60,
                    priority=5
                ),
            ]
            
            # Add creator-specific rules
            if self.config.creator_enhanced_limits:
                self.config.default_rules.extend([
                    RateLimitRule(
                        name="creator_upload",
                        scope=RateLimitScope.ENDPOINT,
                        strategy=RateLimitStrategy.SLIDING_WINDOW,
                        limit=self.config.creator_upload_limit,
                        window=3600,  # per hour
                        path_pattern="/api/v1/content/upload",
                        tier=RateLimitTier.CREATOR,
                        priority=15
                    ),
                    RateLimitRule(
                        name="creator_api",
                        scope=RateLimitScope.USER,
                        strategy=RateLimitStrategy.TOKEN_BUCKET,
                        limit=self.config.creator_api_limit,
                        window=60,
                        tier=RateLimitTier.CREATOR,
                        priority=15
                    ),
                ])
    
    async def dispatch(self, request: Request, call_next) -> Response:
        """Main middleware dispatch with rate limiting"""
        start_time = time.time()
        
        try:
            self.metrics.total_requests += 1
            
            # Check if request should be whitelisted
            if await self._is_whitelisted(request):
                return await call_next(request)
            
            # Check blacklist
            client_ip = self._get_client_ip(request)
            if await self._is_blacklisted(client_ip):
                self.metrics.blocked_requests += 1
                return await self._create_blocked_response(request, "IP blacklisted")
            
            # Update system load for adaptive limiting
            await self._update_system_load()
            
            # Apply rate limiting rules
            rate_limit_result = await self._apply_rate_limits(request)
            
            if not rate_limit_result["allowed"]:
                self.metrics.rate_limited_requests += 1
                
                # Record violation
                await self._record_violation(client_ip, rate_limit_result["rule"])
                
                # Take action based on rule
                action = rate_limit_result["action"]
                
                if action == RateLimitAction.BLOCK:
                    self.metrics.blocked_requests += 1
                    return await self._create_rate_limit_response(request, rate_limit_result)
                
                elif action == RateLimitAction.DELAY:
                    self.metrics.delayed_requests += 1
                    delay = rate_limit_result.get("delay", 1.0)
                    await asyncio.sleep(delay)
                
                elif action == RateLimitAction.WARN:
                    self.metrics.warnings_issued += 1
                    self.logger.warning(
                        f"Rate limit warning: {client_ip} exceeded {rate_limit_result['rule']['name']}"
                    )
                
                elif action == RateLimitAction.DEGRADE:
                    # Implement service degradation (e.g., return cached data)
                    pass
            
            # Process request
            response = await call_next(request)
            
            # Add rate limit headers
            if self.config.include_rate_limit_headers:
                response = await self._add_rate_limit_headers(response, request, rate_limit_result)
            
            # Update metrics
            await self._update_endpoint_metrics(request, True)
            
            return response
            
        except Exception as e:
            self.logger.error(f"Rate limiting middleware error: {e}")
            return JSONResponse(
                status_code=500,
                content={"error": "Internal server error"},
                headers={"X-Content-Type-Options": "nosniff"}
            )
    
    async def _is_whitelisted(self, request: Request) -> bool:
        """Check if request should be whitelisted"""
        client_ip = self._get_client_ip(request)
        
        # IP whitelist
        if client_ip in self.config.whitelisted_ips:
            return True
        
        # User agent whitelist
        user_agent = request.headers.get("user-agent", "")
        if any(ua in user_agent for ua in self.config.whitelisted_user_agents):
            return True
        
        # API key whitelist
        api_key = request.headers.get("x-api-key") or request.headers.get("authorization")
        if api_key and api_key in self.config.whitelisted_api_keys:
            return True
        
        return False
    
    async def _is_blacklisted(self, ip: str) -> bool:
        """Check if IP is blacklisted"""
        if not self.config.enable_blacklist:
            return False
        
        if ip in self.blacklisted_ips:
            if datetime.utcnow() > self.blacklisted_ips[ip]:
                # Blacklist expired
                del self.blacklisted_ips[ip]
                return False
            return True
        
        return False
    
    async def _update_system_load(self):
        """Update system load for adaptive rate limiting"""
        current_time = time.time()
        
        # Update every 30 seconds
        if current_time - self.last_load_check < 30:
            return
        
        try:
            import psutil
            cpu_percent = psutil.cpu_percent(interval=1)
            memory_percent = psutil.virtual_memory().percent
            self.system_load = max(cpu_percent, memory_percent) / 100.0
            self.last_load_check = current_time
        except ImportError:
            # psutil not available, use basic metrics
            self.system_load = 0.0
    
    async def _apply_rate_limits(self, request: Request) -> Dict[str, Any]:
        """Apply rate limiting rules to request"""
        client_ip = self._get_client_ip(request)
        current_time = time.time()
        
        # Sort rules by priority
        sorted_rules = sorted(self.config.default_rules, key=lambda r: r.priority)
        
        for rule in sorted_rules:
            # Check if rule applies to this request
            if not await self._rule_applies(rule, request):
                continue
            
            # Get rate limit identifier
            identifier = await self._get_rate_limit_identifier(rule, request)
            
            # Apply adaptive limiting if enabled
            effective_limit = rule.limit
            if self.config.enable_adaptive_limiting and self.system_load > self.config.adaptive_threshold:
                effective_limit = int(rule.limit * self.config.adaptive_scale_factor)
                self.metrics.adaptive_adjustments += 1
            
            # Check rate limit based on strategy
            allowed = await self._check_rate_limit(
                rule, identifier, effective_limit, current_time
            )
            
            if not allowed:
                return {
                    "allowed": False,
                    "rule": {
                        "name": rule.name,
                        "limit": effective_limit,
                        "window": rule.window,
                        "scope": rule.scope.value
                    },
                    "action": rule.action,
                    "identifier": identifier,
                    "retry_after": await self._calculate_retry_after(rule, identifier),
                    "delay": await self._calculate_delay(rule, client_ip)
                }
        
        return {"allowed": True}
    
    async def _rule_applies(self, rule: RateLimitRule, request: Request) -> bool:
        """Check if rate limiting rule applies to request"""
        # Check path pattern
        if rule.path_pattern and not request.url.path.startswith(rule.path_pattern):
            return False
        
        # Check HTTP method
        if rule.method and request.method != rule.method:
            return False
        
        # Check tier (requires user context)
        if rule.tier:
            user_tier = await self._get_user_tier(request)
            if user_tier != rule.tier:
                return False
        
        return True
    
    async def _get_rate_limit_identifier(self, rule: RateLimitRule, request: Request) -> str:
        """Get identifier for rate limiting"""
        if rule.custom_identifier:
            return rule.custom_identifier(request)
        
        if rule.scope == RateLimitScope.IP:
            return f"ip:{self._get_client_ip(request)}"
        
        elif rule.scope == RateLimitScope.USER:
            user_id = await self._get_user_id(request)
            return f"user:{user_id}" if user_id else f"ip:{self._get_client_ip(request)}"
        
        elif rule.scope == RateLimitScope.API_KEY:
            api_key = request.headers.get("x-api-key") or request.headers.get("authorization")
            if api_key:
                # Hash API key for privacy
                key_hash = hashlib.sha256(api_key.encode()).hexdigest()[:16]
                return f"api_key:{key_hash}"
            return f"ip:{self._get_client_ip(request)}"
        
        elif rule.scope == RateLimitScope.ENDPOINT:
            return f"endpoint:{request.url.path}:{request.method}"
        
        elif rule.scope == RateLimitScope.GLOBAL:
            return "global"
        
        return f"custom:{rule.name}"
    
    async def _check_rate_limit(
        self, 
        rule: RateLimitRule, 
        identifier: str, 
        limit: int, 
        current_time: float
    ) -> bool:
        """Check rate limit based on strategy"""
        key = f"{rule.name}:{identifier}"
        
        if rule.strategy == RateLimitStrategy.TOKEN_BUCKET:
            return await self._check_token_bucket(key, rule, limit, current_time)
        
        elif rule.strategy == RateLimitStrategy.SLIDING_WINDOW:
            return await self._check_sliding_window(key, rule, limit, current_time)
        
        elif rule.strategy == RateLimitStrategy.FIXED_WINDOW:
            return await self._check_fixed_window(key, rule, limit, current_time)
        
        elif rule.strategy == RateLimitStrategy.LEAKY_BUCKET:
            return await self._check_leaky_bucket(key, rule, limit, current_time)
        
        elif rule.strategy == RateLimitStrategy.ADAPTIVE:
            return await self._check_adaptive_limit(key, rule, limit, current_time)
        
        return True
    
    async def _check_token_bucket(
        self, 
        key: str, 
        rule: RateLimitRule, 
        limit: int, 
        current_time: float
    ) -> bool:
        """Check token bucket rate limit"""
        if self.redis_client:
            return await self._check_token_bucket_redis(key, rule, limit, current_time)
        
        # In-memory implementation
        if key not in self.buckets:
            capacity = limit + rule.burst_allowance
            refill_rate = limit / rule.window  # tokens per second
            self.buckets[key] = RateLimitBucket(
                capacity=capacity,
                tokens=capacity,
                last_refill=current_time,
                refill_rate=refill_rate
            )
        
        bucket = self.buckets[key]
        bucket.refill(current_time)
        return bucket.consume(1)
    
    async def _check_token_bucket_redis(
        self, 
        key: str, 
        rule: RateLimitRule, 
        limit: int, 
        current_time: float
    ) -> bool:
        """Check token bucket rate limit using Redis"""
        redis_key = f"{self.config.redis_key_prefix}{key}"
        
        try:
            # Lua script for atomic token bucket operation
            lua_script = """
            local key = KEYS[1]
            local capacity = tonumber(ARGV[1])
            local refill_rate = tonumber(ARGV[2])
            local current_time = tonumber(ARGV[3])
            local tokens_requested = tonumber(ARGV[4])
            
            local bucket = redis.call('HMGET', key, 'tokens', 'last_refill')
            local tokens = tonumber(bucket[1]) or capacity
            local last_refill = tonumber(bucket[2]) or current_time
            
            local elapsed = current_time - last_refill
            local tokens_to_add = elapsed * refill_rate
            tokens = math.min(capacity, tokens + tokens_to_add)
            
            if tokens >= tokens_requested then
                tokens = tokens - tokens_requested
                redis.call('HMSET', key, 'tokens', tokens, 'last_refill', current_time)
                redis.call('EXPIRE', key, 3600)
                return 1
            else
                redis.call('HMSET', key, 'tokens', tokens, 'last_refill', current_time)
                redis.call('EXPIRE', key, 3600)
                return 0
            end
            """
            
            capacity = limit + rule.burst_allowance
            refill_rate = limit / rule.window
            
            result = self.redis_client.eval(
                lua_script, 1, redis_key, capacity, refill_rate, current_time, 1
            )
            
            return bool(result)
            
        except Exception as e:
            self.logger.error(f"Redis token bucket error: {e}")
            return True  # Fail open
    
    async def _check_sliding_window(
        self, 
        key: str, 
        rule: RateLimitRule, 
        limit: int, 
        current_time: float
    ) -> bool:
        """Check sliding window rate limit"""
        if self.redis_client:
            return await self._check_sliding_window_redis(key, rule, limit, current_time)
        
        # In-memory implementation
        if key not in self.windows:
            self.windows[key] = RateLimitWindow(
                limit=limit,
                window_size=rule.window
            )
        
        window = self.windows[key]
        return window.add_request(current_time)
    
    async def _check_sliding_window_redis(
        self, 
        key: str, 
        rule: RateLimitRule, 
        limit: int, 
        current_time: float
    ) -> bool:
        """Check sliding window rate limit using Redis"""
        redis_key = f"{self.config.redis_key_prefix}{key}"
        
        try:
            # Use Redis sorted set for sliding window
            cutoff_time = current_time - rule.window
            
            pipe = self.redis_client.pipeline()
            pipe.zremrangebyscore(redis_key, 0, cutoff_time)
            pipe.zcard(redis_key)
            pipe.zadd(redis_key, {str(current_time): current_time})
            pipe.expire(redis_key, rule.window + 1)
            
            results = pipe.execute()
            current_count = results[1]
            
            return current_count < limit
            
        except Exception as e:
            self.logger.error(f"Redis sliding window error: {e}")
            return True  # Fail open
    
    async def _check_fixed_window(
        self, 
        key: str, 
        rule: RateLimitRule, 
        limit: int, 
        current_time: float
    ) -> bool:
        """Check fixed window rate limit"""
        window_start = int(current_time // rule.window) * rule.window
        window_key = f"{key}:{window_start}"
        
        if self.redis_client:
            try:
                current_count = self.redis_client.incr(window_key)
                if current_count == 1:
                    self.redis_client.expire(window_key, rule.window)
                return current_count <= limit
            except Exception as e:
                self.logger.error(f"Redis fixed window error: {e}")
                return True
        
        # In-memory implementation
        if window_key not in self.windows:
            self.windows[window_key] = RateLimitWindow(
                limit=limit,
                window_size=rule.window
            )
        
        window = self.windows[window_key]
        return len(window.requests) < limit
    
    async def _check_leaky_bucket(
        self, 
        key: str, 
        rule: RateLimitRule, 
        limit: int, 
        current_time: float
    ) -> bool:
        """Check leaky bucket rate limit"""
        # Simplified leaky bucket implementation
        # In practice, this would need more sophisticated leak rate management
        return await self._check_token_bucket(key, rule, limit, current_time)
    
    async def _check_adaptive_limit(
        self, 
        key: str, 
        rule: RateLimitRule, 
        limit: int, 
        current_time: float
    ) -> bool:
        """Check adaptive rate limit based on system load"""
        # Adjust limit based on system load and historical patterns
        historical_load = await self._get_historical_load(key)
        adaptive_limit = int(limit * (1.0 - max(self.system_load, historical_load)))
        
        return await self._check_sliding_window(key, rule, adaptive_limit, current_time)
    
    async def _get_historical_load(self, key: str) -> float:
        """Get historical load for adaptive limiting"""
        # Simplified implementation - in practice, this would analyze
        # historical request patterns and system performance
        return 0.0
    
    async def _calculate_retry_after(self, rule: RateLimitRule, identifier: str) -> int:
        """Calculate retry-after header value"""
        if rule.strategy == RateLimitStrategy.FIXED_WINDOW:
            current_time = time.time()
            window_start = int(current_time // rule.window) * rule.window
            next_window = window_start + rule.window
            return int(next_window - current_time)
        
        return rule.window
    
    async def _calculate_delay(self, rule: RateLimitRule, client_ip: str) -> float:
        """Calculate progressive delay for rate limited requests"""
        if not self.config.enable_progressive_delays:
            return 1.0
        
        violation_count = self.violation_counts[client_ip]
        
        # Progressive delay: 1s, 2s, 4s, 8s, max 30s
        delay = min(2 ** violation_count, 30.0)
        return delay
    
    async def _record_violation(self, client_ip: str, rule: Dict[str, Any]):
        """Record rate limit violation"""
        self.violation_counts[client_ip] += 1
        
        # Check for auto-blacklisting
        if (self.config.enable_blacklist and 
            self.violation_counts[client_ip] >= self.config.auto_blacklist_threshold):
            
            blacklist_until = datetime.utcnow() + timedelta(seconds=self.config.blacklist_duration)
            self.blacklisted_ips[client_ip] = blacklist_until
            self.metrics.blacklisted_ips += 1
            
            self.logger.warning(
                f"IP {client_ip} auto-blacklisted until {blacklist_until} "
                f"for {self.violation_counts[client_ip]} violations"
            )
    
    def _get_client_ip(self, request: Request) -> str:
        """Extract client IP from request"""
        forwarded_for = request.headers.get("x-forwarded-for")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()
        
        real_ip = request.headers.get("x-real-ip")
        if real_ip:
            return real_ip
        
        if hasattr(request, "client") and request.client:
            return request.client.host
        
        return "unknown"
    
    async def _get_user_id(self, request: Request) -> Optional[str]:
        """Extract user ID from request (requires authentication context)"""
        # This would integrate with your authentication system
        # For example, from JWT token or session
        auth_header = request.headers.get("authorization")
        if auth_header and auth_header.startswith("Bearer "):
            # Extract user ID from JWT token
            # This is a placeholder - implement based on your auth system
            return "user_123"
        
        return None
    
    async def _get_user_tier(self, request: Request) -> Optional[RateLimitTier]:
        """Get user tier for tiered rate limiting"""
        # This would integrate with your user management system
        user_id = await self._get_user_id(request)
        if user_id:
            # Placeholder - implement based on your user system
            return RateLimitTier.PREMIUM
        
        return None
    
    async def _create_blocked_response(self, request: Request, reason: str) -> Response:
        """Create response for blocked requests"""
        self.logger.warning(f"Request blocked: {reason} - {self._get_client_ip(request)}")
        
        return JSONResponse(
            status_code=403,
            content={
                "error": "Request blocked",
                "message": reason
            },
            headers={
                "X-Content-Type-Options": "nosniff",
                "Retry-After": "3600"
            }
        )
    
    async def _create_rate_limit_response(self, request: Request, rate_limit_result: Dict[str, Any]) -> Response:
        """Create response for rate limited requests"""
        rule = rate_limit_result["rule"]
        retry_after = rate_limit_result.get("retry_after", 60)
        
        error_message = (
            self.config.custom_error_message or 
            f"Rate limit exceeded for {rule['scope']}: {rule['limit']} requests per {rule['window']} seconds"
        )
        
        self.logger.info(
            f"Rate limit exceeded: {self._get_client_ip(request)} - {rule['name']}"
        )
        
        return JSONResponse(
            status_code=self.config.custom_error_code,
            content={
                "error": "Rate limit exceeded",
                "message": error_message,
                "limit": rule["limit"],
                "window": rule["window"],
                "retry_after": retry_after
            },
            headers={
                "X-RateLimit-Limit": str(rule["limit"]),
                "X-RateLimit-Window": str(rule["window"]),
                "X-RateLimit-Scope": rule["scope"],
                "Retry-After": str(retry_after),
                "X-Content-Type-Options": "nosniff"
            }
        )
    
    async def _add_rate_limit_headers(
        self, 
        response: Response, 
        request: Request, 
        rate_limit_result: Dict[str, Any]
    ) -> Response:
        """Add rate limit headers to response"""
        if not rate_limit_result.get("allowed", True):
            return response
        
        # Add headers showing current rate limit status
        # This would require tracking current usage for each rule
        response.headers["X-RateLimit-Limit"] = "100"  # Placeholder
        response.headers["X-RateLimit-Remaining"] = "95"  # Placeholder
        response.headers["X-RateLimit-Reset"] = str(int(time.time() + 60))
        
        return response
    
    async def _update_endpoint_metrics(self, request: Request, success: bool):
        """Update per-endpoint metrics"""
        endpoint = f"{request.method}:{request.url.path}"
        
        if endpoint not in self.metrics.endpoint_metrics:
            self.metrics.endpoint_metrics[endpoint] = {
                "total": 0, "success": 0, "rate_limited": 0
            }
        
        self.metrics.endpoint_metrics[endpoint]["total"] += 1
        if success:
            self.metrics.endpoint_metrics[endpoint]["success"] += 1
        else:
            self.metrics.endpoint_metrics[endpoint]["rate_limited"] += 1
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get current rate limiting metrics"""
        return {
            "total_requests": self.metrics.total_requests,
            "rate_limited_requests": self.metrics.rate_limited_requests,
            "blocked_requests": self.metrics.blocked_requests,
            "delayed_requests": self.metrics.delayed_requests,
            "warnings_issued": self.metrics.warnings_issued,
            "blacklisted_ips": self.metrics.blacklisted_ips,
            "adaptive_adjustments": self.metrics.adaptive_adjustments,
            "rate_limit_percentage": self.metrics.rate_limit_percentage,
            "active_buckets": len(self.buckets),
            "active_windows": len(self.windows),
            "system_load": self.system_load,
            "endpoint_metrics": self.metrics.endpoint_metrics
        }
    
    def get_rate_limit_status(self, identifier: str) -> Dict[str, Any]:
        """Get current rate limit status for identifier"""
        status = {}
        
        for rule in self.config.default_rules:
            key = f"{rule.name}:{identifier}"
            
            if rule.strategy == RateLimitStrategy.TOKEN_BUCKET and key in self.buckets:
                bucket = self.buckets[key]
                bucket.refill(time.time())
                status[rule.name] = {
                    "strategy": "token_bucket",
                    "tokens_remaining": int(bucket.tokens),
                    "capacity": bucket.capacity,
                    "refill_rate": bucket.refill_rate
                }
            
            elif rule.strategy == RateLimitStrategy.SLIDING_WINDOW and key in self.windows:
                window = self.windows[key]
                current_time = time.time()
                cutoff_time = current_time - rule.window
                
                # Count recent requests
                recent_requests = sum(1 for req_time in window.requests if req_time > cutoff_time)
                
                status[rule.name] = {
                    "strategy": "sliding_window",
                    "requests_made": recent_requests,
                    "limit": rule.limit,
                    "window": rule.window,
                    "remaining": rule.limit - recent_requests
                }
        
        return status
    
    def reset_metrics(self):
        """Reset all metrics"""
        self.metrics = RateLimitMetrics()
        self.logger.info("Rate limiting metrics reset")
    
    def clear_rate_limits(self, identifier: Optional[str] = None):
        """Clear rate limits for specific identifier or all"""
        if identifier:
            # Clear specific identifier
            keys_to_remove = [key for key in self.buckets.keys() if identifier in key]
            for key in keys_to_remove:
                del self.buckets[key]
            
            keys_to_remove = [key for key in self.windows.keys() if identifier in key]
            for key in keys_to_remove:
                del self.windows[key]
        else:
            # Clear all
            self.buckets.clear()
            self.windows.clear()
            self.blacklisted_ips.clear()
            self.violation_counts.clear()
        
        self.logger.info(f"Rate limits cleared for: {identifier or 'all'}")


# Factory function for easy integration
def create_rate_limiting_middleware(
    app: FastAPI,
    default_limit: int = 100,
    default_window: int = 60,
    **kwargs
) -> RateLimitingMiddleware:
    """
    🏭 Factory function to create rate limiting middleware
    
    Args:
        app: FastAPI application
        default_limit: Default requests per window
        default_window: Default window size in seconds
        **kwargs: Additional configuration options
    
    Returns:
        Configured rate limiting middleware instance
    """
    config = RateLimitConfig(
        ip_requests_per_minute=default_limit,
        **kwargs
    )
    
    return RateLimitingMiddleware(app, config)


def setup_creator_rate_limiting(app: FastAPI) -> RateLimitingMiddleware:
    """
    🎯 Creator-specific rate limiting setup
    Optimized for content creation platforms
    """
    config = RateLimitConfig(
        # Enhanced limits for creators
        creator_enhanced_limits=True,
        creator_upload_limit=100,  # uploads per hour
        creator_api_limit=1000,    # API calls per minute
        
        # Tiered limiting
        ip_requests_per_minute=200,
        user_requests_per_minute=500,
        api_key_requests_per_minute=2000,
        
        # Advanced features
        enable_adaptive_limiting=True,
        enable_progressive_delays=True,
        enable_blacklist=True,
        
        # Creator-friendly settings
        auto_blacklist_threshold=20,  # Higher threshold
        blacklist_duration=1800,      # 30 minutes instead of 1 hour
        
        # Enhanced monitoring
        enable_metrics=True,
        enable_alerts=True,
        alert_threshold=0.8,
        
        # Redis for scalability
        use_redis=True,  # Configure redis_url separately
        
        # Custom rules for creator endpoints
        default_rules=[
            RateLimitRule(
                name="content_upload",
                scope=RateLimitScope.ENDPOINT,
                strategy=RateLimitStrategy.SLIDING_WINDOW,
                limit=50,
                window=3600,  # per hour
                path_pattern="/api/v1/content/upload",
                action=RateLimitAction.DELAY,
                priority=5
            ),
            RateLimitRule(
                name="media_processing",
                scope=RateLimitScope.USER,
                strategy=RateLimitStrategy.TOKEN_BUCKET,
                limit=20,
                window=3600,  # per hour
                burst_allowance=5,
                path_pattern="/api/v1/media/process",
                priority=10
            ),
            RateLimitRule(
                name="creator_analytics",
                scope=RateLimitScope.USER,
                strategy=RateLimitStrategy.SLIDING_WINDOW,
                limit=1000,
                window=3600,  # per hour
                path_pattern="/api/v1/analytics",
                tier=RateLimitTier.CREATOR,
                priority=15
            ),
        ]
    )
    
    return RateLimitingMiddleware(app, config)


if __name__ == "__main__":
    # Example usage
    from fastapi import FastAPI
    
    app = FastAPI(title="Rate Limiting Demo")
    
    # Setup rate limiting
    rate_limiter = create_rate_limiting_middleware(
        app,
        default_limit=100,
        default_window=60
    )
    
    app.add_middleware(RateLimitingMiddleware, middleware=rate_limiter)
    
    @app.get("/")
    async def root():
        return {"message": "Rate Limiting Template Active"}
    
    @app.get("/api/data")
    async def get_data():
        return {"data": "sample data"}
    
    @app.post("/api/upload")
    async def upload_content(data: dict):
        return {"message": "Content uploaded", "id": "123"}
    
    @app.get("/metrics")
    async def get_metrics():
        return rate_limiter.get_metrics()
    
    @app.get("/status/{identifier}")
    async def get_status(identifier: str):
        return rate_limiter.get_rate_limit_status(identifier)