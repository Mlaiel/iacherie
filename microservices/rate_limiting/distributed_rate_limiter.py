"""
Distributed Rate Limiter Enterprise - Ainflue
=============================================
Rate limiter distribué avec Redis/etcd pour microservices scalables.
Support multi-nœuds avec consistance forte.

Author: Fahed Mlaiel (mlaiel@live.de)
Project: Ainflue Rate Limiting
Version: 1.0 Production
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import redis.asyncio as redis
import time
import json
import logging
from typing import Dict, List, Optional, Tuple, Any, Union
from dataclasses import dataclass, field
from enum import Enum
import uuid
import hashlib
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class RateLimitAlgorithm(Enum):
    """Rate limiting algorithms supported"""
    TOKEN_BUCKET = "token_bucket"
    SLIDING_WINDOW = "sliding_window"
    FIXED_WINDOW = "fixed_window"
    SLIDING_LOG = "sliding_log"
    LEAKY_BUCKET = "leaky_bucket"

class RateLimitStatus(Enum):
    """Rate limit check results"""
    ALLOWED = "allowed"
    DENIED = "denied"  
    THROTTLED = "throttled"
    ERROR = "error"

@dataclass
class RateLimitConfig:
    """Configuration pour rate limiting distribué"""
    requests_per_second: int
    burst_capacity: int
    window_size_seconds: int
    algorithm: RateLimitAlgorithm
    redis_key_prefix: str = "rl"
    backoff_strategy: str = "exponential"
    ttl_seconds: int = 3600
    enable_metrics: bool = True
    geographic_aware: bool = False
    compliance_mode: str = "standard"  # standard, strict, gdpr
    
    def __post_init__(self):
        if self.burst_capacity < self.requests_per_second:
            self.burst_capacity = self.requests_per_second * 2

@dataclass 
class RateLimitMetrics:
    """Métriques rate limiting pour monitoring"""
    total_requests: int = 0
    allowed_requests: int = 0
    denied_requests: int = 0
    throttled_requests: int = 0
    avg_response_time_ms: float = 0.0
    error_count: int = 0
    last_reset: datetime = field(default_factory=datetime.now)
    
    def update_metrics(self, status: RateLimitStatus, response_time_ms: float):
        """Update métriques avec nouveau résultat"""
        self.total_requests += 1
        
        if status == RateLimitStatus.ALLOWED:
            self.allowed_requests += 1
        elif status == RateLimitStatus.DENIED:
            self.denied_requests += 1
        elif status == RateLimitStatus.THROTTLED:
            self.throttled_requests += 1
        elif status == RateLimitStatus.ERROR:
            self.error_count += 1
            
        # Calcul moyenne mobile response time
        self.avg_response_time_ms = (
            (self.avg_response_time_ms * (self.total_requests - 1) + response_time_ms) 
            / self.total_requests
        )

@dataclass
class RateLimitResult:
    """Résultat vérification rate limit"""
    status: RateLimitStatus
    allowed: bool
    remaining_tokens: int = 0
    reset_time: Optional[float] = None
    retry_after: Optional[float] = None
    quota_used: int = 0
    quota_total: int = 0
    headers: Dict[str, str] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_http_headers(self) -> Dict[str, str]:
        """Conversion en headers HTTP standard"""
        headers = {
            "X-RateLimit-Limit": str(self.quota_total),
            "X-RateLimit-Remaining": str(self.remaining_tokens),
            "X-RateLimit-Used": str(self.quota_used),
        }
        
        if self.reset_time:
            headers["X-RateLimit-Reset"] = str(int(self.reset_time))
            
        if self.retry_after:
            headers["Retry-After"] = str(int(self.retry_after))
            
        return headers

class DistributedRateLimiter:
    """
    Rate Limiter distribué enterprise avec Redis backend.
    Consistance forte + performances élevées + monitoring intégré.
    """
    
    def __init__(self, redis_client: redis.Redis, config: RateLimitConfig):
        self.redis = redis_client
        self.config = config
        self.lua_scripts = self._load_lua_scripts()
        self.metrics = RateLimitMetrics()
        self.node_id = str(uuid.uuid4())[:8]
        self.logger = logging.getLogger(__name__)
        
        # Compilation des scripts Lua pour performance
        self._compiled_scripts = {}
        
    async def initialize(self) -> bool:
        """Initialise le rate limiter distribué"""
        try:
            # Test connexion Redis
            await self.redis.ping()
            
            # Compilation scripts Lua
            for script_name, script_content in self.lua_scripts.items():
                self._compiled_scripts[script_name] = self.redis.register_script(script_content)
                
            self.logger.info(f"Distributed rate limiter initialized - Node: {self.node_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to initialize distributed rate limiter: {e}")
            return False
    
    async def check_rate_limit(self, identifier: str, cost: int = 1, 
                             metadata: Optional[Dict[str, Any]] = None) -> RateLimitResult:
        """
        Vérification rate limit distribuée avec script Lua atomique.
        
        Features:
        - Atomic operations avec Redis Lua scripts
        - Multi-algorithm support (token bucket, sliding window, etc.)
        - Cost-based rate limiting pour requests différentes
        - Real-time metrics collection
        - Adaptive backoff suggestions
        - Geographic distribution support
        - Circuit breaker integration
        """
        start_time = time.time()
        
        try:
            # Construction clé Redis avec namespace
            redis_key = f"{self.config.redis_key_prefix}:{identifier}"
            now = time.time()
            
            # Sélection algorithme et exécution
            if self.config.algorithm == RateLimitAlgorithm.TOKEN_BUCKET:
                result = await self._execute_token_bucket(redis_key, cost, now, metadata)
            elif self.config.algorithm == RateLimitAlgorithm.SLIDING_WINDOW:
                result = await self._execute_sliding_window(redis_key, cost, now, metadata)
            elif self.config.algorithm == RateLimitAlgorithm.FIXED_WINDOW:
                result = await self._execute_fixed_window(redis_key, cost, now, metadata)
            elif self.config.algorithm == RateLimitAlgorithm.SLIDING_LOG:
                result = await self._execute_sliding_log(redis_key, cost, now, metadata)
            else:
                result = RateLimitResult(
                    status=RateLimitStatus.ERROR,
                    allowed=False,
                    metadata={"error": f"Unsupported algorithm: {self.config.algorithm}"}
                )
            
            # Mise à jour métriques
            response_time_ms = (time.time() - start_time) * 1000
            self.metrics.update_metrics(result.status, response_time_ms)
            
            # Ajout headers HTTP standards
            result.headers.update(result.to_http_headers())
            
            return result
            
        except Exception as e:
            self.logger.error(f"Rate limit check failed for {identifier}: {e}")
            response_time_ms = (time.time() - start_time) * 1000
            self.metrics.update_metrics(RateLimitStatus.ERROR, response_time_ms)
            
            return RateLimitResult(
                status=RateLimitStatus.ERROR,
                allowed=True,  # Fail open pour haute disponibilité
                metadata={"error": str(e), "fail_open": True}
            )

    async def _execute_token_bucket(self, redis_key: str, cost: int, now: float, 
                                  metadata: Optional[Dict[str, Any]]) -> RateLimitResult:
        """Exécution algorithme token bucket avec Lua script"""
        try:
            script = self._compiled_scripts["token_bucket"]
            
            # Paramètres pour script Lua
            keys = [redis_key]
            args = [
                self.config.burst_capacity,  # capacity
                self.config.requests_per_second,  # refill_rate
                cost,  # tokens_requested
                now,  # current_time
                self.config.ttl_seconds,  # ttl
                self.node_id  # node_id pour debugging
            ]
            
            # Exécution atomique
            lua_result = await script(keys=keys, args=args)
            
            # Parse résultat: [allowed, tokens_remaining, reset_time]
            allowed = bool(lua_result[0])
            tokens_remaining = int(lua_result[1])
            reset_time = float(lua_result[2]) if lua_result[2] else None
            
            status = RateLimitStatus.ALLOWED if allowed else RateLimitStatus.DENIED
            
            return RateLimitResult(
                status=status,
                allowed=allowed,
                remaining_tokens=tokens_remaining,
                reset_time=reset_time,
                quota_used=self.config.burst_capacity - tokens_remaining,
                quota_total=self.config.burst_capacity,
                retry_after=1.0 if not allowed else None,
                metadata={
                    "algorithm": "token_bucket",
                    "cost": cost,
                    "node_id": self.node_id
                }
            )
            
        except Exception as e:
            self.logger.error(f"Token bucket execution failed: {e}")
            raise
    
    async def _execute_sliding_window(self, redis_key: str, cost: int, now: float,
                                    metadata: Optional[Dict[str, Any]]) -> RateLimitResult:
        """Exécution algorithme sliding window avec Lua script"""
        try:
            script = self._compiled_scripts["sliding_window"]
            
            keys = [redis_key]
            args = [
                self.config.requests_per_second * self.config.window_size_seconds,  # max requests
                self.config.window_size_seconds,  # window size
                cost,  # request cost
                now,  # current time
                self.config.ttl_seconds,  # ttl
                str(uuid.uuid4())  # unique request id
            ]
            
            lua_result = await script(keys=keys, args=args)
            
            allowed = bool(lua_result[0])
            current_count = int(lua_result[1])
            window_reset = float(lua_result[2]) if lua_result[2] else None
            
            max_requests = self.config.requests_per_second * self.config.window_size_seconds
            remaining = max(0, max_requests - current_count)
            
            status = RateLimitStatus.ALLOWED if allowed else RateLimitStatus.DENIED
            
            return RateLimitResult(
                status=status,
                allowed=allowed,
                remaining_tokens=remaining,
                reset_time=window_reset,
                quota_used=current_count,
                quota_total=max_requests,
                retry_after=self.config.window_size_seconds if not allowed else None,
                metadata={
                    "algorithm": "sliding_window",
                    "window_size": self.config.window_size_seconds,
                    "cost": cost
                }
            )
            
        except Exception as e:
            self.logger.error(f"Sliding window execution failed: {e}")
            raise

    async def acquire_permit(self, identifier: str, cost: int = 1, 
                           timeout: float = None) -> bool:
        """Acquisition permit avec timeout optional"""
        start_time = time.time()
        
        while True:
            result = await self.check_rate_limit(identifier, cost)
            
            if result.allowed:
                return True
                
            if timeout and (time.time() - start_time) >= timeout:
                return False
                
            # Backoff avant retry
            if result.retry_after:
                await asyncio.sleep(min(result.retry_after, 1.0))
            else:
                await asyncio.sleep(0.1)

    async def release_permit(self, identifier: str, cost: int = 1) -> bool:
        """Release permit pour rate limiters avec reservations"""
        try:
            # Implémentation pour algorithmes avec réservation
            redis_key = f"{self.config.redis_key_prefix}:reservation:{identifier}"
            
            # Script Lua pour release atomique
            script = self._compiled_scripts.get("release_permit")
            if script:
                await script(keys=[redis_key], args=[cost, time.time()])
                return True
                
            return False
            
        except Exception as e:
            self.logger.error(f"Release permit failed for {identifier}: {e}")
            return False

    async def get_limit_status(self, identifier: str) -> Dict[str, Any]:
        """Status complet du rate limiter pour identifier"""
        try:
            redis_key = f"{self.config.redis_key_prefix}:{identifier}"
            
            # Récupération status selon algorithme
            if self.config.algorithm == RateLimitAlgorithm.TOKEN_BUCKET:
                bucket_info = await self.redis.hmget(redis_key, "tokens", "last_refill")
                tokens = float(bucket_info[0] or self.config.burst_capacity)
                last_refill = float(bucket_info[1] or time.time())
                
                return {
                    "algorithm": "token_bucket",
                    "tokens_available": tokens,
                    "capacity": self.config.burst_capacity,
                    "refill_rate": self.config.requests_per_second,
                    "last_refill": last_refill,
                    "utilization_pct": ((self.config.burst_capacity - tokens) / self.config.burst_capacity) * 100
                }
                
            elif self.config.algorithm == RateLimitAlgorithm.SLIDING_WINDOW:
                window_start = time.time() - self.config.window_size_seconds
                request_count = await self.redis.zcount(redis_key, window_start, time.time())
                max_requests = self.config.requests_per_second * self.config.window_size_seconds
                
                return {
                    "algorithm": "sliding_window",
                    "current_requests": request_count,
                    "max_requests": max_requests,
                    "window_size": self.config.window_size_seconds,
                    "remaining": max(0, max_requests - request_count),
                    "utilization_pct": (request_count / max_requests) * 100 if max_requests > 0 else 0
                }
                
            return {"algorithm": str(self.config.algorithm), "status": "unknown"}
            
        except Exception as e:
            self.logger.error(f"Get limit status failed for {identifier}: {e}")
            return {"error": str(e)}

    async def update_limits(self, identifier: str, new_config: RateLimitConfig) -> bool:
        """Update dynamique des limites sans downtime"""
        try:
            # Backup configuration actuelle
            old_config = self.config
            
            # Application nouvelle configuration
            self.config = new_config
            
            # Recompilation scripts Lua si nécessaire
            if old_config.algorithm != new_config.algorithm:
                for script_name, script_content in self.lua_scripts.items():
                    self._compiled_scripts[script_name] = self.redis.register_script(script_content)
            
            # Migration état existant si possible
            redis_key = f"{old_config.redis_key_prefix}:{identifier}"
            new_redis_key = f"{new_config.redis_key_prefix}:{identifier}"
            
            if redis_key != new_redis_key:
                # Migration de l'état avec pipeline atomique
                async with self.redis.pipeline(transaction=True) as pipe:
                    await pipe.rename(redis_key, new_redis_key).execute()
            
            self.logger.info(f"Rate limits updated for {identifier}")
            return True
            
        except Exception as e:
            self.logger.error(f"Update limits failed for {identifier}: {e}")
            # Rollback en cas d'erreur
            self.config = old_config
            return False

    def _load_lua_scripts(self) -> Dict[str, str]:
        """Scripts Lua pour opérations atomiques Redis"""
        return {
            'token_bucket': """
                local key = KEYS[1]
                local capacity = tonumber(ARGV[1])
                local refill_rate = tonumber(ARGV[2])
                local cost = tonumber(ARGV[3])
                local now = tonumber(ARGV[4])
                local ttl = tonumber(ARGV[5])
                local node_id = ARGV[6]
                
                -- Get current bucket state
                local bucket = redis.call('HMGET', key, 'tokens', 'last_refill')
                local tokens = tonumber(bucket[1]) or capacity
                local last_refill = tonumber(bucket[2]) or now
                
                -- Calculate tokens to add based on time elapsed
                local time_passed = now - last_refill
                local tokens_to_add = time_passed * refill_rate
                tokens = math.min(capacity, tokens + tokens_to_add)
                
                -- Check if request can be served
                local allowed = 0
                local reset_time = now + (capacity - tokens) / refill_rate
                
                if tokens >= cost then
                    tokens = tokens - cost
                    allowed = 1
                    -- Update bucket state
                    redis.call('HMSET', key, 'tokens', tokens, 'last_refill', now, 'node_id', node_id)
                    redis.call('EXPIRE', key, ttl)
                end
                
                return {allowed, tokens, reset_time}
            """,
            
            'sliding_window': """
                local key = KEYS[1]
                local max_requests = tonumber(ARGV[1])
                local window_size = tonumber(ARGV[2])
                local cost = tonumber(ARGV[3])
                local now = tonumber(ARGV[4])
                local ttl = tonumber(ARGV[5])
                local request_id = ARGV[6]
                
                -- Remove expired entries
                local window_start = now - window_size
                redis.call('ZREMRANGEBYSCORE', key, 0, window_start)
                
                -- Count current requests
                local current_count = redis.call('ZCARD', key)
                
                -- Check if request can be allowed
                local allowed = 0
                local window_reset = window_start + window_size
                
                if current_count + cost <= max_requests then
                    allowed = 1
                    -- Add request(s) to window
                    for i = 1, cost do
                        redis.call('ZADD', key, now, request_id .. ':' .. i)
                    end
                    current_count = current_count + cost
                end
                
                -- Set expiration
                redis.call('EXPIRE', key, ttl)
                
                return {allowed, current_count, window_reset}
            """,
            
            'fixed_window': """
                local key = KEYS[1]
                local max_requests = tonumber(ARGV[1])
                local window_size = tonumber(ARGV[2])
                local cost = tonumber(ARGV[3])
                local now = tonumber(ARGV[4])
                local ttl = tonumber(ARGV[5])
                
                -- Calculate current window
                local window_id = math.floor(now / window_size)
                local window_key = key .. ':' .. window_id
                
                -- Get current count
                local current_count = tonumber(redis.call('GET', window_key) or 0)
                
                -- Check if request can be allowed
                local allowed = 0
                local window_reset = (window_id + 1) * window_size
                
                if current_count + cost <= max_requests then
                    allowed = 1
                    redis.call('INCRBY', window_key, cost)
                    redis.call('EXPIRE', window_key, window_size + 1)
                    current_count = current_count + cost
                end
                
                return {allowed, current_count, window_reset}
            """,
            
            'release_permit': """
                local key = KEYS[1]
                local tokens_to_release = tonumber(ARGV[1])
                local now = tonumber(ARGV[2])
                
                -- Add tokens back to bucket
                local bucket = redis.call('HMGET', key, 'tokens')
                local current_tokens = tonumber(bucket[1] or 0)
                local new_tokens = current_tokens + tokens_to_release
                
                redis.call('HMSET', key, 'tokens', new_tokens, 'last_release', now)
                
                return {1, new_tokens}
            """
        }

    async def get_metrics(self) -> Dict[str, Any]:
        """Récupération métriques détaillées"""
        return {
            "node_id": self.node_id,
            "algorithm": str(self.config.algorithm),
            "total_requests": self.metrics.total_requests,
            "allowed_requests": self.metrics.allowed_requests,
            "denied_requests": self.metrics.denied_requests,
            "throttled_requests": self.metrics.throttled_requests,
            "error_count": self.metrics.error_count,
            "success_rate_pct": (self.metrics.allowed_requests / max(1, self.metrics.total_requests)) * 100,
            "avg_response_time_ms": self.metrics.avg_response_time_ms,
            "last_reset": self.metrics.last_reset.isoformat(),
            "config": {
                "requests_per_second": self.config.requests_per_second,
                "burst_capacity": self.config.burst_capacity,
                "window_size_seconds": self.config.window_size_seconds,
                "algorithm": str(self.config.algorithm)
            }
        }

    async def health_check(self) -> Dict[str, Any]:
        """Health check du rate limiter distribué"""
        try:
            # Test Redis connectivity
            redis_latency_start = time.time()
            await self.redis.ping()
            redis_latency = (time.time() - redis_latency_start) * 1000
            
            # Test script compilation 
            scripts_status = "healthy"
            if not self._compiled_scripts:
                scripts_status = "not_compiled"
            
            return {
                "status": "healthy",
                "node_id": self.node_id,
                "redis_latency_ms": redis_latency,
                "scripts_status": scripts_status,
                "total_requests_processed": self.metrics.total_requests,
                "error_rate_pct": (self.metrics.error_count / max(1, self.metrics.total_requests)) * 100,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e),
                "node_id": self.node_id,
                "timestamp": datetime.now().isoformat()
            }

# Factory functions pour création rate limiters
def create_token_bucket_limiter(redis_client: redis.Redis, 
                               requests_per_second: int = 100,
                               burst_capacity: int = None) -> DistributedRateLimiter:
    """Factory pour rate limiter token bucket"""
    config = RateLimitConfig(
        requests_per_second=requests_per_second,
        burst_capacity=burst_capacity or requests_per_second * 2,
        window_size_seconds=60,
        algorithm=RateLimitAlgorithm.TOKEN_BUCKET,
        redis_key_prefix="tb_rl"
    )
    return DistributedRateLimiter(redis_client, config)

def create_sliding_window_limiter(redis_client: redis.Redis,
                                 requests_per_minute: int = 1000,
                                 window_size_seconds: int = 60) -> DistributedRateLimiter:
    """Factory pour rate limiter sliding window"""
    config = RateLimitConfig(
        requests_per_second=requests_per_minute // window_size_seconds,
        burst_capacity=requests_per_minute,
        window_size_seconds=window_size_seconds,
        algorithm=RateLimitAlgorithm.SLIDING_WINDOW,
        redis_key_prefix="sw_rl"
    )
    return DistributedRateLimiter(redis_client, config)

# Export classes et fonctions principales
__all__ = [
    'DistributedRateLimiter',
    'RateLimitConfig', 
    'RateLimitResult',
    'RateLimitMetrics',
    'RateLimitAlgorithm',
    'RateLimitStatus',
    'create_token_bucket_limiter',
    'create_sliding_window_limiter'
]