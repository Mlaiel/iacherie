"""MLOps Rate Limiter - Adaptive Rate Limiting with Creator Type Priorities
Rate limiter adaptatif avec priorités basées sur les types de créateurs.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

🎯 Business Logic Integration:
Creator (Type-Based Priority) → API Request → Rate Limiting → Resource Protection → Fair Usage

🚀 Multi-Expert Implementation:
- Backend Senior: High-performance rate limiting with minimal latency impact
- Security: DDoS protection and abuse prevention
- ML Engineer: Intelligent rate adaptation based on model load and creator behavior
- Microservices: Distributed rate limiting across service mesh
"""

import asyncio
import logging
import json
import time
import hashlib
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple, Union
from dataclasses import dataclass, asdict
from enum import Enum
import redis.asyncio as redis
import numpy as np
from collections import defaultdict, deque
import statistics

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CreatorType(Enum):
    """Types de créateurs avec priorités différentes."""
    PREMIUM_INFLUENCER = "premium_influencer"  # Highest priority
    PROFESSIONAL_MUSICIAN = "professional_musician"
    PROFESSIONAL_PHOTOGRAPHER = "professional_photographer"
    VERIFIED_COMEDIAN = "verified_comedian"
    VERIFIED_BLOGGER = "verified_blogger"
    STANDARD_INFLUENCER = "standard_influencer"
    AMATEUR_MUSICIAN = "amateur_musician"
    AMATEUR_PHOTOGRAPHER = "amateur_photographer"
    AMATEUR_COMEDIAN = "amateur_comedian"
    AMATEUR_BLOGGER = "amateur_blogger"
    GUEST = "guest"  # Lowest priority

class RequestType(Enum):
    """Types de requêtes avec limites différentes."""
    AI_INFERENCE = "ai_inference"
    CONTENT_UPLOAD = "content_upload"
    CONTENT_PROCESSING = "content_processing"
    SEARCH_QUERY = "search_query"
    ANALYTICS_REQUEST = "analytics_request"
    API_CALL = "api_call"
    STREAMING = "streaming"
    COLLABORATION = "collaboration"

class LimitingStrategy(Enum):
    """Stratégies de limitation de débit."""
    TOKEN_BUCKET = "token_bucket"
    SLIDING_WINDOW = "sliding_window"
    FIXED_WINDOW = "fixed_window"
    ADAPTIVE = "adaptive"

@dataclass
class RateLimit:
    """Configuration de limite de débit."""
    requests_per_second: int
    requests_per_minute: int
    requests_per_hour: int
    burst_capacity: int
    creator_type: CreatorType
    request_type: RequestType

@dataclass
class RequestContext:
    """Contexte d'une requête pour rate limiting."""
    user_id: str
    creator_type: CreatorType
    request_type: RequestType
    ip_address: str
    user_agent: str
    timestamp: float
    content_size_mb: Optional[float] = None
    priority_score: float = 1.0

@dataclass
class RateLimitResult:
    """Résultat d'une vérification de rate limit."""
    allowed: bool
    remaining_requests: int
    reset_time: float
    retry_after: Optional[int]
    priority_boost_applied: bool
    dynamic_adjustment_factor: float
    reason: Optional[str] = None

class TokenBucket:
    """Implementation du Token Bucket algorithm avec Redis."""
    
    def __init__(self, redis_client, bucket_key: str, capacity: int, refill_rate: float):
        self.redis = redis_client
        self.bucket_key = bucket_key
        self.capacity = capacity
        self.refill_rate = refill_rate
        
    async def consume(self, tokens: int = 1) -> Tuple[bool, int]:
        """Consommer des tokens du bucket."""
        lua_script = """
        local bucket_key = KEYS[1]
        local capacity = tonumber(ARGV[1])
        local refill_rate = tonumber(ARGV[2])
        local tokens_requested = tonumber(ARGV[3])
        local now = tonumber(ARGV[4])
        
        -- Get current bucket state
        local bucket_data = redis.call('HMGET', bucket_key, 'tokens', 'last_refill')
        local current_tokens = tonumber(bucket_data[1]) or capacity
        local last_refill = tonumber(bucket_data[2]) or now
        
        -- Calculate tokens to add based on time elapsed
        local time_elapsed = math.max(0, now - last_refill)
        local tokens_to_add = time_elapsed * refill_rate
        current_tokens = math.min(capacity, current_tokens + tokens_to_add)
        
        -- Check if request can be satisfied
        if current_tokens >= tokens_requested then
            current_tokens = current_tokens - tokens_requested
            -- Update bucket state
            redis.call('HMSET', bucket_key, 'tokens', current_tokens, 'last_refill', now)
            redis.call('EXPIRE', bucket_key, 3600)  -- 1 hour TTL
            return {1, math.floor(current_tokens)}
        else
            -- Update bucket state without consuming tokens
            redis.call('HMSET', bucket_key, 'tokens', current_tokens, 'last_refill', now)
            redis.call('EXPIRE', bucket_key, 3600)
            return {0, math.floor(current_tokens)}
        end
        """
        
        try:
            result = await self.redis.eval(lua_script, 1, self.bucket_key, 
                                         self.capacity, self.refill_rate, tokens, time.time())
            return bool(result[0]), int(result[1])
        except Exception as e:
            logger.error(f"Token bucket error: {e}")
            return True, self.capacity  # Fail open

class SlidingWindowCounter:
    """Implementation du Sliding Window algorithm avec Redis."""
    
    def __init__(self, redis_client, window_key: str, window_size_seconds: int, max_requests: int):
        self.redis = redis_client
        self.window_key = window_key
        self.window_size = window_size_seconds
        self.max_requests = max_requests
    
    async def is_allowed(self) -> Tuple[bool, int]:
        """Vérifier si la requête est autorisée dans la fenêtre glissante."""
        lua_script = """
        local window_key = KEYS[1]
        local window_size = tonumber(ARGV[1])
        local max_requests = tonumber(ARGV[2])
        local now = tonumber(ARGV[3])
        local window_start = now - window_size
        
        -- Remove expired entries
        redis.call('ZREMRANGEBYSCORE', window_key, 0, window_start)
        
        -- Count current requests in window
        local current_count = redis.call('ZCARD', window_key)
        
        if current_count < max_requests then
            -- Add current request
            redis.call('ZADD', window_key, now, now)
            redis.call('EXPIRE', window_key, window_size)
            return {1, max_requests - current_count - 1}
        else
            return {0, 0}
        end
        """
        
        try:
            result = await self.redis.eval(lua_script, 1, self.window_key,
                                         self.window_size, self.max_requests, time.time())
            return bool(result[0]), int(result[1])
        except Exception as e:
            logger.error(f"Sliding window error: {e}")
            return True, self.max_requests  # Fail open

class AdaptiveRateLimiter:
    """Rate limiter adaptatif avec priorités créateur et intelligence ML."""
    
    def __init__(self, redis_url: str = "redis://localhost:6379"):
        """Initialize adaptive rate limiter."""
        self.redis = None
        self.redis_url = redis_url
        
        # Rate limits configuration par type de créateur et requête
        self.rate_limits = self._initialize_rate_limits()
        
        # Priority weights for creator types
        self.creator_priorities = {
            CreatorType.PREMIUM_INFLUENCER: 1.0,
            CreatorType.PROFESSIONAL_MUSICIAN: 0.9,
            CreatorType.PROFESSIONAL_PHOTOGRAPHER: 0.9,
            CreatorType.VERIFIED_COMEDIAN: 0.8,
            CreatorType.VERIFIED_BLOGGER: 0.8,
            CreatorType.STANDARD_INFLUENCER: 0.7,
            CreatorType.AMATEUR_MUSICIAN: 0.6,
            CreatorType.AMATEUR_PHOTOGRAPHER: 0.6,
            CreatorType.AMATEUR_COMEDIAN: 0.5,
            CreatorType.AMATEUR_BLOGGER: 0.5,
            CreatorType.GUEST: 0.3
        }
        
        # Request type costs (tokens per request)
        self.request_costs = {
            RequestType.AI_INFERENCE: 10,
            RequestType.CONTENT_PROCESSING: 8,
            RequestType.CONTENT_UPLOAD: 5,
            RequestType.STREAMING: 3,
            RequestType.ANALYTICS_REQUEST: 2,
            RequestType.COLLABORATION: 2,
            RequestType.SEARCH_QUERY: 1,
            RequestType.API_CALL: 1
        }
        
        # Performance monitoring
        self.request_history = deque(maxlen=10000)
        self.adaptive_factors = defaultdict(lambda: 1.0)
        
        logger.info("🚦 AdaptiveRateLimiter initialized with creator priority system")

    def _initialize_rate_limits(self) -> Dict[Tuple[CreatorType, RequestType], RateLimit]:
        """Initialiser les limites de débit par créateur et type de requête."""
        limits = {}
        
        # Base limits for different creator tiers
        base_limits = {
            CreatorType.PREMIUM_INFLUENCER: {"rps": 100, "rpm": 5000, "rph": 200000, "burst": 200},
            CreatorType.PROFESSIONAL_MUSICIAN: {"rps": 80, "rpm": 4000, "rph": 150000, "burst": 150},
            CreatorType.PROFESSIONAL_PHOTOGRAPHER: {"rps": 80, "rpm": 4000, "rph": 150000, "burst": 150},
            CreatorType.VERIFIED_COMEDIAN: {"rps": 60, "rpm": 3000, "rph": 120000, "burst": 120},
            CreatorType.VERIFIED_BLOGGER: {"rps": 60, "rpm": 3000, "rph": 120000, "burst": 120},
            CreatorType.STANDARD_INFLUENCER: {"rps": 50, "rpm": 2500, "rph": 100000, "burst": 100},
            CreatorType.AMATEUR_MUSICIAN: {"rps": 30, "rpm": 1500, "rph": 60000, "burst": 60},
            CreatorType.AMATEUR_PHOTOGRAPHER: {"rps": 30, "rpm": 1500, "rph": 60000, "burst": 60},
            CreatorType.AMATEUR_COMEDIAN: {"rps": 20, "rpm": 1000, "rph": 40000, "burst": 40},
            CreatorType.AMATEUR_BLOGGER: {"rps": 20, "rpm": 1000, "rph": 40000, "burst": 40},
            CreatorType.GUEST: {"rps": 10, "rpm": 500, "rph": 10000, "burst": 20}
        }
        
        # Request type multipliers
        request_multipliers = {
            RequestType.AI_INFERENCE: 0.3,        # More restrictive for expensive operations
            RequestType.CONTENT_PROCESSING: 0.4,
            RequestType.CONTENT_UPLOAD: 0.6,
            RequestType.STREAMING: 0.8,
            RequestType.ANALYTICS_REQUEST: 1.0,    # Standard rate
            RequestType.COLLABORATION: 1.0,
            RequestType.SEARCH_QUERY: 1.5,        # More generous for light operations
            RequestType.API_CALL: 1.2
        }
        
        # Generate limits for each combination
        for creator_type in CreatorType:
            for request_type in RequestType:
                base = base_limits[creator_type]
                multiplier = request_multipliers[request_type]
                
                limits[(creator_type, request_type)] = RateLimit(
                    requests_per_second=int(base["rps"] * multiplier),
                    requests_per_minute=int(base["rpm"] * multiplier),
                    requests_per_hour=int(base["rph"] * multiplier),
                    burst_capacity=int(base["burst"] * multiplier),
                    creator_type=creator_type,
                    request_type=request_type
                )
        
        return limits

    async def initialize_redis(self):
        """Initialize Redis connection."""
        if not self.redis:
            try:
                self.redis = redis.from_url(self.redis_url, decode_responses=True)
                await self.redis.ping()
                logger.info("✅ Redis connection established for rate limiting")
            except Exception as e:
                logger.error(f"❌ Failed to connect to Redis: {e}")
                self.redis = None

    async def check_rate_limit(self, context: RequestContext) -> RateLimitResult:
        """Vérifier les limites de débit pour une requête."""
        try:
            await self.initialize_redis()
            
            # Get rate limit configuration
            rate_limit = self.rate_limits.get(
                (context.creator_type, context.request_type),
                self.rate_limits[(CreatorType.GUEST, RequestType.API_CALL)]
            )
            
            # Calculate dynamic adjustments
            dynamic_factor = await self._calculate_dynamic_factor(context)
            priority_boost = self._calculate_priority_boost(context)
            
            # Apply adjustments to limits
            adjusted_limit = self._apply_adjustments(rate_limit, dynamic_factor, priority_boost)
            
            # Determine tokens needed
            tokens_needed = self.request_costs.get(context.request_type, 1)
            
            # Apply content size multiplier for uploads
            if context.content_size_mb and context.request_type == RequestType.CONTENT_UPLOAD:
                tokens_needed = max(1, int(tokens_needed * context.content_size_mb))
            
            # Check multiple rate limiting strategies
            results = await self._check_multiple_limits(context, adjusted_limit, tokens_needed)
            
            # Determine final result
            final_result = self._evaluate_limit_results(results, adjusted_limit, dynamic_factor, priority_boost)
            
            # Record request for adaptive learning
            await self._record_request_metrics(context, final_result)
            
            return final_result
            
        except Exception as e:
            logger.error(f"❌ Rate limit check error: {e}")
            # Fail open - allow request but with basic limits
            return RateLimitResult(
                allowed=True,
                remaining_requests=10,
                reset_time=time.time() + 60,
                retry_after=None,
                priority_boost_applied=False,
                dynamic_adjustment_factor=1.0,
                reason="rate_limiter_error_fail_open"
            )

    async def _calculate_dynamic_factor(self, context: RequestContext) -> float:
        """Calculer le facteur d'ajustement dynamique basé sur la charge système."""
        
        # Get current system load indicators
        current_load = await self._get_system_load()
        
        # Creator type historical performance
        creator_key = f"creator_perf:{context.creator_type.value}"
        historical_perf = await self._get_creator_performance(creator_key)
        
        # Base dynamic factor on system load
        if current_load < 0.3:  # Low load
            load_factor = 1.5
        elif current_load < 0.7:  # Medium load
            load_factor = 1.0
        else:  # High load
            load_factor = 0.7
        
        # Adjust based on creator historical behavior
        behavior_factor = historical_perf.get("success_rate", 0.8)
        
        # Time-based adjustments (off-peak hours)
        time_factor = self._get_time_based_factor()
        
        # Combine factors
        dynamic_factor = load_factor * behavior_factor * time_factor
        
        return max(0.1, min(3.0, dynamic_factor))  # Clamp between 0.1 and 3.0

    async def _get_system_load(self) -> float:
        """Obtenir la charge système actuelle (simulation)."""
        # In production, this would query actual system metrics
        if self.redis:
            try:
                # Check Redis for cached system metrics
                load_data = await self.redis.get("system:load")
                if load_data:
                    return float(load_data)
            except:
                pass
        
        # Simulate load based on request history
        recent_requests = len([r for r in self.request_history 
                             if time.time() - r < 60])  # Last minute
        
        # Assume max 1000 requests/minute is full load
        return min(1.0, recent_requests / 1000)

    async def _get_creator_performance(self, creator_key: str) -> Dict[str, float]:
        """Obtenir les performances historiques d'un créateur."""
        if not self.redis:
            return {"success_rate": 0.8, "avg_response_time": 1.0}
        
        try:
            perf_data = await self.redis.hgetall(creator_key)
            if perf_data:
                return {
                    "success_rate": float(perf_data.get("success_rate", 0.8)),
                    "avg_response_time": float(perf_data.get("avg_response_time", 1.0)),
                    "abuse_score": float(perf_data.get("abuse_score", 0.0))
                }
        except Exception as e:
            logger.warning(f"Error getting creator performance: {e}")
        
        return {"success_rate": 0.8, "avg_response_time": 1.0, "abuse_score": 0.0}

    def _get_time_based_factor(self) -> float:
        """Calculer le facteur basé sur l'heure (off-peak hours get bonus)."""
        current_hour = datetime.now().hour
        
        # Peak hours: 9-17 and 19-23
        if (9 <= current_hour <= 17) or (19 <= current_hour <= 23):
            return 0.9  # Slightly more restrictive during peak
        else:
            return 1.2  # More generous during off-peak

    def _calculate_priority_boost(self, context: RequestContext) -> float:
        """Calculer le boost de priorité pour un créateur."""
        base_priority = self.creator_priorities.get(context.creator_type, 0.5)
        
        # Additional boosts based on context
        boost_factors = []
        
        # Priority score from context
        if context.priority_score > 1.0:
            boost_factors.append(context.priority_score)
        
        # Request type priority
        high_priority_requests = [RequestType.AI_INFERENCE, RequestType.CONTENT_PROCESSING]
        if context.request_type in high_priority_requests:
            boost_factors.append(1.2)
        
        # Calculate final boost
        final_boost = base_priority
        for factor in boost_factors:
            final_boost *= factor
        
        return min(2.0, final_boost)  # Cap at 2x boost

    def _apply_adjustments(self, 
                          rate_limit: RateLimit,
                          dynamic_factor: float,
                          priority_boost: float) -> RateLimit:
        """Appliquer les ajustements dynamiques aux limites."""
        total_multiplier = dynamic_factor * priority_boost
        
        return RateLimit(
            requests_per_second=int(rate_limit.requests_per_second * total_multiplier),
            requests_per_minute=int(rate_limit.requests_per_minute * total_multiplier),
            requests_per_hour=int(rate_limit.requests_per_hour * total_multiplier),
            burst_capacity=int(rate_limit.burst_capacity * total_multiplier),
            creator_type=rate_limit.creator_type,
            request_type=rate_limit.request_type
        )

    async def _check_multiple_limits(self,
                                   context: RequestContext,
                                   rate_limit: RateLimit,
                                   tokens_needed: int) -> Dict[str, Any]:
        """Vérifier plusieurs stratégies de limitation."""
        results = {}
        
        user_key = f"ratelimit:{context.user_id}:{context.request_type.value}"
        
        # Token bucket check (per second)
        bucket = TokenBucket(
            self.redis,
            f"{user_key}:bucket",
            rate_limit.burst_capacity,
            rate_limit.requests_per_second
        )
        bucket_allowed, bucket_remaining = await bucket.consume(tokens_needed)
        results["token_bucket"] = {
            "allowed": bucket_allowed,
            "remaining": bucket_remaining
        }
        
        # Sliding window checks
        # Per minute
        minute_window = SlidingWindowCounter(
            self.redis,
            f"{user_key}:minute",
            60,
            rate_limit.requests_per_minute
        )
        minute_allowed, minute_remaining = await minute_window.is_allowed()
        results["minute_window"] = {
            "allowed": minute_allowed,
            "remaining": minute_remaining
        }
        
        # Per hour
        hour_window = SlidingWindowCounter(
            self.redis,
            f"{user_key}:hour",
            3600,
            rate_limit.requests_per_hour
        )
        hour_allowed, hour_remaining = await hour_window.is_allowed()
        results["hour_window"] = {
            "allowed": hour_allowed,
            "remaining": hour_remaining
        }
        
        # IP-based limiting (abuse prevention)
        ip_key = f"ratelimit:ip:{context.ip_address}"
        ip_window = SlidingWindowCounter(
            self.redis,
            f"{ip_key}:minute",
            60,
            1000  # Max 1000 requests per minute per IP
        )
        ip_allowed, ip_remaining = await ip_window.is_allowed()
        results["ip_window"] = {
            "allowed": ip_allowed,
            "remaining": ip_remaining
        }
        
        return results

    def _evaluate_limit_results(self,
                               results: Dict[str, Any],
                               rate_limit: RateLimit,
                               dynamic_factor: float,
                               priority_boost: float) -> RateLimitResult:
        """Évaluer les résultats de toutes les vérifications de limites."""
        
        # All checks must pass
        all_allowed = all(check["allowed"] for check in results.values())
        
        if all_allowed:
            # Find the most restrictive remaining count
            remaining_counts = [check["remaining"] for check in results.values()]
            min_remaining = min(remaining_counts)
            
            return RateLimitResult(
                allowed=True,
                remaining_requests=min_remaining,
                reset_time=time.time() + 60,  # Next minute reset
                retry_after=None,
                priority_boost_applied=priority_boost > 1.0,
                dynamic_adjustment_factor=dynamic_factor
            )
        else:
            # Determine which limit was hit and calculate retry after
            failed_checks = [name for name, check in results.items() if not check["allowed"]]
            
            # Calculate retry after based on the type of limit hit
            if "token_bucket" in failed_checks:
                retry_after = 1  # Token bucket refills quickly
            elif "minute_window" in failed_checks:
                retry_after = 60
            elif "hour_window" in failed_checks:
                retry_after = 300  # 5 minutes for hour window
            elif "ip_window" in failed_checks:
                retry_after = 60  # IP limit
            else:
                retry_after = 60
            
            return RateLimitResult(
                allowed=False,
                remaining_requests=0,
                reset_time=time.time() + retry_after,
                retry_after=retry_after,
                priority_boost_applied=priority_boost > 1.0,
                dynamic_adjustment_factor=dynamic_factor,
                reason=f"rate_limit_exceeded_{failed_checks[0]}"
            )

    async def _record_request_metrics(self, 
                                    context: RequestContext,
                                    result: RateLimitResult) -> None:
        """Enregistrer les métriques de requête pour l'apprentissage adaptatif."""
        
        # Add to request history
        request_record = {
            "timestamp": context.timestamp,
            "creator_type": context.creator_type.value,
            "request_type": context.request_type.value,
            "allowed": result.allowed,
            "priority_boost": result.priority_boost_applied
        }
        self.request_history.append(request_record)
        
        # Update Redis metrics if available
        if self.redis:
            try:
                # Update creator performance metrics
                creator_key = f"creator_perf:{context.creator_type.value}"
                
                # Increment counters
                await self.redis.hincrby(creator_key, "total_requests", 1)
                if result.allowed:
                    await self.redis.hincrby(creator_key, "allowed_requests", 1)
                
                # Calculate and update success rate
                total = int(await self.redis.hget(creator_key, "total_requests") or 1)
                allowed = int(await self.redis.hget(creator_key, "allowed_requests") or 0)
                success_rate = allowed / total
                
                await self.redis.hset(creator_key, "success_rate", success_rate)
                await self.redis.expire(creator_key, 86400)  # 24 hour TTL
                
                # Update global metrics
                global_key = "global:rate_limit_metrics"
                await self.redis.hincrby(global_key, "total_requests", 1)
                if result.allowed:
                    await self.redis.hincrby(global_key, "allowed_requests", 1)
                
            except Exception as e:
                logger.warning(f"Error recording metrics: {e}")

    async def get_rate_limit_status(self, user_id: str, creator_type: CreatorType) -> Dict[str, Any]:
        """Obtenir le statut actuel des limites de débit pour un utilisateur."""
        try:
            await self.initialize_redis()
            
            status = {}
            
            for request_type in RequestType:
                rate_limit = self.rate_limits.get(
                    (creator_type, request_type),
                    self.rate_limits[(CreatorType.GUEST, RequestType.API_CALL)]
                )
                
                user_key = f"ratelimit:{user_id}:{request_type.value}"
                
                # Check current bucket state
                bucket = TokenBucket(
                    self.redis,
                    f"{user_key}:bucket",
                    rate_limit.burst_capacity,
                    rate_limit.requests_per_second
                )
                
                # Get remaining tokens without consuming
                try:
                    result = await self.redis.eval("""
                        local bucket_key = KEYS[1]
                        local capacity = tonumber(ARGV[1])
                        local refill_rate = tonumber(ARGV[2])
                        local now = tonumber(ARGV[3])
                        
                        local bucket_data = redis.call('HMGET', bucket_key, 'tokens', 'last_refill')
                        local current_tokens = tonumber(bucket_data[1]) or capacity
                        local last_refill = tonumber(bucket_data[2]) or now
                        
                        local time_elapsed = math.max(0, now - last_refill)
                        local tokens_to_add = time_elapsed * refill_rate
                        current_tokens = math.min(capacity, current_tokens + tokens_to_add)
                        
                        return math.floor(current_tokens)
                    """, 1, f"{user_key}:bucket", 
                    rate_limit.burst_capacity, rate_limit.requests_per_second, time.time())
                    
                    current_tokens = int(result)
                except:
                    current_tokens = rate_limit.burst_capacity
                
                status[request_type.value] = {
                    "rate_limit": asdict(rate_limit),
                    "current_tokens": current_tokens,
                    "requests_per_second_limit": rate_limit.requests_per_second,
                    "requests_per_minute_limit": rate_limit.requests_per_minute,
                    "requests_per_hour_limit": rate_limit.requests_per_hour
                }
            
            # Add priority information
            status["creator_priority"] = {
                "creator_type": creator_type.value,
                "priority_weight": self.creator_priorities.get(creator_type, 0.5),
                "priority_tier": self._get_priority_tier(creator_type)
            }
            
            return status
            
        except Exception as e:
            logger.error(f"❌ Error getting rate limit status: {e}")
            return {"error": str(e)}

    def _get_priority_tier(self, creator_type: CreatorType) -> str:
        """Obtenir le tier de priorité pour un type de créateur."""
        priority_weight = self.creator_priorities.get(creator_type, 0.5)
        
        if priority_weight >= 0.9:
            return "premium"
        elif priority_weight >= 0.7:
            return "professional"
        elif priority_weight >= 0.5:
            return "standard"
        else:
            return "basic"

    async def reset_user_limits(self, user_id: str) -> bool:
        """Réinitialiser les limites pour un utilisateur (admin function)."""
        try:
            await self.initialize_redis()
            
            if not self.redis:
                return False
            
            # Find all keys for this user
            pattern = f"ratelimit:{user_id}:*"
            keys = await self.redis.keys(pattern)
            
            if keys:
                await self.redis.delete(*keys)
                logger.info(f"🔄 Reset rate limits for user {user_id}")
                return True
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Error resetting user limits: {e}")
            return False

    async def get_abuse_metrics(self) -> Dict[str, Any]:
        """Obtenir les métriques d'abus et de performance."""
        try:
            await self.initialize_redis()
            
            metrics = {
                "total_requests_last_hour": 0,
                "blocked_requests_last_hour": 0,
                "top_requesters": [],
                "top_blocked_ips": [],
                "creator_type_distribution": {},
                "request_type_distribution": {}
            }
            
            # Analyze request history
            now = time.time()
            hour_ago = now - 3600
            
            recent_requests = [r for r in self.request_history if r["timestamp"] > hour_ago]
            
            metrics["total_requests_last_hour"] = len(recent_requests)
            metrics["blocked_requests_last_hour"] = len([r for r in recent_requests if not r["allowed"]])
            
            # Creator type distribution
            creator_counts = defaultdict(int)
            request_counts = defaultdict(int)
            
            for req in recent_requests:
                creator_counts[req["creator_type"]] += 1
                request_counts[req["request_type"]] += 1
            
            metrics["creator_type_distribution"] = dict(creator_counts)
            metrics["request_type_distribution"] = dict(request_counts)
            
            # Get additional metrics from Redis if available
            if self.redis:
                try:
                    global_metrics = await self.redis.hgetall("global:rate_limit_metrics")
                    if global_metrics:
                        metrics["global_total_requests"] = int(global_metrics.get("total_requests", 0))
                        metrics["global_allowed_requests"] = int(global_metrics.get("allowed_requests", 0))
                        
                        if metrics["global_total_requests"] > 0:
                            metrics["global_success_rate"] = metrics["global_allowed_requests"] / metrics["global_total_requests"]
                except:
                    pass
            
            return metrics
            
        except Exception as e:
            logger.error(f"❌ Error getting abuse metrics: {e}")
            return {"error": str(e)}

# Factory for creating specialized rate limiters
class RateLimiterFactory:
    """Factory pour créer des rate limiters spécialisés."""
    
    @staticmethod
    def create_for_environment(environment: str = "production") -> AdaptiveRateLimiter:
        """Créer un rate limiter pour un environnement spécifique."""
        redis_urls = {
            "production": "redis://prod-redis:6379",
            "staging": "redis://staging-redis:6379",
            "development": "redis://localhost:6379"
        }
        
        redis_url = redis_urls.get(environment, "redis://localhost:6379")
        limiter = AdaptiveRateLimiter(redis_url)
        
        logger.info(f"🏭 Created rate limiter for {environment} environment")
        return limiter

    @staticmethod
    def create_high_performance() -> AdaptiveRateLimiter:
        """Créer un rate limiter haute performance."""
        limiter = AdaptiveRateLimiter()
        
        # Increase all limits for high performance scenario
        for key, rate_limit in limiter.rate_limits.items():
            limiter.rate_limits[key] = RateLimit(
                requests_per_second=rate_limit.requests_per_second * 2,
                requests_per_minute=rate_limit.requests_per_minute * 2,
                requests_per_hour=rate_limit.requests_per_hour * 2,
                burst_capacity=rate_limit.burst_capacity * 2,
                creator_type=rate_limit.creator_type,
                request_type=rate_limit.request_type
            )
        
        logger.info("⚡ Created high-performance rate limiter")
        return limiter

# Example usage and testing
async def main():
    """Example usage of adaptive rate limiter."""
    print("🚦 MLOps Adaptive Rate Limiter - Enterprise Demo")
    print("="*60)
    
    # Create rate limiter
    limiter = RateLimiterFactory.create_for_environment("development")
    
    # Test different creator types and request types
    test_cases = [
        {
            "user_id": "musician_001",
            "creator_type": CreatorType.PROFESSIONAL_MUSICIAN,
            "request_type": RequestType.AI_INFERENCE,
            "ip_address": "192.168.1.100"
        },
        {
            "user_id": "influencer_001", 
            "creator_type": CreatorType.PREMIUM_INFLUENCER,
            "request_type": RequestType.CONTENT_UPLOAD,
            "ip_address": "192.168.1.101"
        },
        {
            "user_id": "guest_001",
            "creator_type": CreatorType.GUEST,
            "request_type": RequestType.SEARCH_QUERY,
            "ip_address": "192.168.1.102"
        }
    ]
    
    print(f"\n🧪 Testing rate limiting for different creator types...")
    
    for i, test_case in enumerate(test_cases):
        print(f"\n--- Test Case {i+1}: {test_case['creator_type'].value} ---")
        
        # Create request context
        context = RequestContext(
            user_id=test_case["user_id"],
            creator_type=test_case["creator_type"],
            request_type=test_case["request_type"],
            ip_address=test_case["ip_address"],
            user_agent="TestAgent/1.0",
            timestamp=time.time(),
            priority_score=1.0 if test_case["creator_type"] != CreatorType.PREMIUM_INFLUENCER else 1.5
        )
        
        # Check rate limit
        result = await limiter.check_rate_limit(context)
        
        print(f"   Request allowed: {result.allowed}")
        print(f"   Remaining requests: {result.remaining_requests}")
        print(f"   Priority boost applied: {result.priority_boost_applied}")
        print(f"   Dynamic factor: {result.dynamic_adjustment_factor:.2f}")
        
        if not result.allowed:
            print(f"   Retry after: {result.retry_after} seconds")
            print(f"   Reason: {result.reason}")
    
    # Test burst scenarios
    print(f"\n🚀 Testing burst request handling...")
    
    burst_context = RequestContext(
        user_id="burst_test_user",
        creator_type=CreatorType.PROFESSIONAL_PHOTOGRAPHER,
        request_type=RequestType.CONTENT_UPLOAD,
        ip_address="192.168.1.103",
        user_agent="BurstTest/1.0",
        timestamp=time.time(),
        content_size_mb=5.0  # Large upload
    )
    
    allowed_count = 0
    for i in range(20):  # Try 20 rapid requests
        result = await limiter.check_rate_limit(burst_context)
        if result.allowed:
            allowed_count += 1
        
        if i < 5 or not result.allowed:  # Show first 5 and all blocked
            print(f"   Request {i+1}: {'✅ Allowed' if result.allowed else '❌ Blocked'} "
                  f"(Remaining: {result.remaining_requests})")
    
    print(f"   Burst test result: {allowed_count}/20 requests allowed")
    
    # Get rate limit status
    print(f"\n📊 Getting rate limit status for professional musician...")
    status = await limiter.get_rate_limit_status("musician_001", CreatorType.PROFESSIONAL_MUSICIAN)
    
    if "creator_priority" in status:
        priority = status["creator_priority"]
        print(f"   Creator tier: {priority['priority_tier']}")
        print(f"   Priority weight: {priority['priority_weight']}")
    
    # Show AI inference limits
    if "ai_inference" in status:
        ai_limits = status["ai_inference"]
        print(f"   AI Inference limits:")
        print(f"     Per second: {ai_limits['requests_per_second_limit']}")
        print(f"     Per minute: {ai_limits['requests_per_minute_limit']}")
        print(f"     Current tokens: {ai_limits['current_tokens']}")
    
    # Get abuse metrics
    print(f"\n🛡️ Checking abuse metrics...")
    abuse_metrics = await limiter.get_abuse_metrics()
    
    print(f"   Total requests last hour: {abuse_metrics.get('total_requests_last_hour', 0)}")
    print(f"   Blocked requests: {abuse_metrics.get('blocked_requests_last_hour', 0)}")
    
    if abuse_metrics.get('creator_type_distribution'):
        print(f"   Creator type distribution:")
        for creator_type, count in abuse_metrics['creator_type_distribution'].items():
            print(f"     {creator_type}: {count}")
    
    print(f"\n✅ Rate limiter testing complete!")

if __name__ == "__main__":
    asyncio.run(main())