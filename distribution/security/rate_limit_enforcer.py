"""
Security Module - Rate Limit Enforcer
Advanced rate limiting system for Ainflue Distribution Platform

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import time
from typing import Dict, Optional, List, Tuple
from dataclasses import dataclass
from enum import Enum
import redis.asyncio as redis
from datetime import datetime, timedelta
import json
import hashlib

class RateLimitType(Enum):
    """Rate limit types for different scenarios"""
    API_CALLS = "api_calls"
    CONTENT_UPLOADS = "content_uploads"
    DISTRIBUTION_REQUESTS = "distribution_requests"
    PLATFORM_API_CALLS = "platform_api_calls"
    USER_ACTIONS = "user_actions"
    BULK_OPERATIONS = "bulk_operations"

@dataclass
class RateLimitRule:
    """Rate limit rule configuration"""
    requests_per_minute: int
    requests_per_hour: int
    requests_per_day: int
    burst_allowance: int
    penalty_duration: int  # seconds
    whitelist_override: bool = False

@dataclass
class RateLimitResult:
    """Result of rate limit check"""
    allowed: bool
    current_count: int
    limit: int
    reset_time: datetime
    retry_after: Optional[int] = None
    warning_threshold_reached: bool = False

class RateLimitEnforcer:
    """
    Advanced rate limiting system with Redis backend
    Supports multiple rate limit strategies and intelligent enforcement
    """
    
    def __init__(self, redis_client -> None: redis.Redis) -> None:
        self.redis = redis_client
        self.default_rules = self._get_default_rules()
        self.whitelist_cache = {}
        self.blacklist_cache = {}
        
    def _get_default_rules(self) -> Dict[RateLimitType, RateLimitRule]:
        """Get default rate limit rules for different operations"""
        return {
            RateLimitType.API_CALLS: RateLimitRule(
                requests_per_minute=1000,
                requests_per_hour=50000,
                requests_per_day=1000000,
                burst_allowance=50,
                penalty_duration=300
            ),
            RateLimitType.CONTENT_UPLOADS: RateLimitRule(
                requests_per_minute=100,
                requests_per_hour=2000,
                requests_per_day=20000,
                burst_allowance=10,
                penalty_duration=600
            ),
            RateLimitType.DISTRIBUTION_REQUESTS: RateLimitRule(
                requests_per_minute=500,
                requests_per_hour=10000,
                requests_per_day=100000,
                burst_allowance=25,
                penalty_duration=300
            ),
            RateLimitType.PLATFORM_API_CALLS: RateLimitRule(
                requests_per_minute=50,
                requests_per_hour=1000,
                requests_per_day=10000,
                burst_allowance=5,
                penalty_duration=900
            ),
            RateLimitType.USER_ACTIONS: RateLimitRule(
                requests_per_minute=200,
                requests_per_hour=5000,
                requests_per_day=50000,
                burst_allowance=20,
                penalty_duration=180
            ),
            RateLimitType.BULK_OPERATIONS: RateLimitRule(
                requests_per_minute=10,
                requests_per_hour=100,
                requests_per_day=1000,
                burst_allowance=2,
                penalty_duration=1800
            )
        }
    
    async def check_rate_limit(
        self,
        identifier: str,
        limit_type: RateLimitType,
        custom_rule: Optional[RateLimitRule] = None
    ) -> RateLimitResult:
        """
        Check if request is within rate limits
        
        Args:
            identifier: Unique identifier (user_id, api_key, ip_address)
            limit_type: Type of rate limit to enforce
            custom_rule: Optional custom rule override
            
        Returns:
            RateLimitResult with rate limit decision
        """
        rule = custom_rule or self.default_rules[limit_type]
        
        # Check whitelist first
        if await self._is_whitelisted(identifier):
            return RateLimitResult(
                allowed=True,
                current_count=0,
                limit=rule.requests_per_minute,
                reset_time=datetime.now() + timedelta(minutes=1)
            )
        
        # Check blacklist
        if await self._is_blacklisted(identifier):
            return RateLimitResult(
                allowed=False,
                current_count=999999,
                limit=rule.requests_per_minute,
                reset_time=datetime.now() + timedelta(hours=24),
                retry_after=86400
            )
        
        # Check penalty status
        penalty_key = f"penalty:{identifier}:{limit_type.value}"
        if await self.redis.exists(penalty_key):
            penalty_ttl = await self.redis.ttl(penalty_key)
            return RateLimitResult(
                allowed=False,
                current_count=0,
                limit=rule.requests_per_minute,
                reset_time=datetime.now() + timedelta(seconds=penalty_ttl),
                retry_after=penalty_ttl
            )
        
        # Perform rate limit checks for different time windows
        current_time = time.time()
        minute_window = int(current_time // 60)
        hour_window = int(current_time // 3600)
        day_window = int(current_time // 86400)
        
        # Check minute limit
        minute_key = f"rate_limit:{identifier}:{limit_type.value}:minute:{minute_window}"
        minute_count = await self._increment_counter(minute_key, 60)
        
        if minute_count > rule.requests_per_minute + rule.burst_allowance:
            await self._apply_penalty(identifier, limit_type, rule.penalty_duration)
            return RateLimitResult(
                allowed=False,
                current_count=minute_count,
                limit=rule.requests_per_minute,
                reset_time=datetime.fromtimestamp((minute_window + 1) * 60),
                retry_after=rule.penalty_duration
            )
        
        # Check hour limit
        hour_key = f"rate_limit:{identifier}:{limit_type.value}:hour:{hour_window}"
        hour_count = await self._increment_counter(hour_key, 3600)
        
        if hour_count > rule.requests_per_hour:
            await self._apply_penalty(identifier, limit_type, rule.penalty_duration)
            return RateLimitResult(
                allowed=False,
                current_count=hour_count,
                limit=rule.requests_per_hour,
                reset_time=datetime.fromtimestamp((hour_window + 1) * 3600),
                retry_after=rule.penalty_duration
            )
        
        # Check day limit
        day_key = f"rate_limit:{identifier}:{limit_type.value}:day:{day_window}"
        day_count = await self._increment_counter(day_key, 86400)
        
        if day_count > rule.requests_per_day:
            await self._apply_penalty(identifier, limit_type, rule.penalty_duration * 2)
            return RateLimitResult(
                allowed=False,
                current_count=day_count,
                limit=rule.requests_per_day,
                reset_time=datetime.fromtimestamp((day_window + 1) * 86400),
                retry_after=rule.penalty_duration * 2
            )
        
        # Check for warning threshold
        warning_threshold = minute_count > (rule.requests_per_minute * 0.8)
        
        return RateLimitResult(
            allowed=True,
            current_count=minute_count,
            limit=rule.requests_per_minute,
            reset_time=datetime.fromtimestamp((minute_window + 1) * 60),
            warning_threshold_reached=warning_threshold
        )
    
    async def _increment_counter(self, key: str, ttl: int) -> int:
        """Increment counter with TTL"""
        pipe = self.redis.pipeline()
        pipe.incr(key)
        pipe.expire(key, ttl)
        results = await pipe.execute()
        return results[0]
    
    async def _apply_penalty(self, identifier -> None: str, limit_type -> None: RateLimitType, duration -> None: int) -> None:
        """Apply penalty for rate limit violation"""
        penalty_key = f"penalty:{identifier}:{limit_type.value}"
        await self.redis.setex(penalty_key, duration, "1")
        
        # Log penalty application
        await self._log_rate_limit_violation(identifier, limit_type, duration)
    
    async def _log_rate_limit_violation(self, identifier -> None: str, limit_type -> None: RateLimitType, duration -> None: int) -> None:
        """Log rate limit violation for monitoring"""
        violation_data = {
            "identifier": identifier,
            "limit_type": limit_type.value,
            "penalty_duration": duration,
            "timestamp": datetime.now().isoformat(),
            "severity": "warning" if duration < 600 else "critical"
        }
        
        log_key = f"violations:{datetime.now().strftime('%Y-%m-%d')}"
        await self.redis.lpush(log_key, json.dumps(violation_data))
        await self.redis.expire(log_key, 86400 * 7)  # Keep for 7 days
    
    async def _is_whitelisted(self, identifier: str) -> bool:
        """Check if identifier is whitelisted"""
        if identifier in self.whitelist_cache:
            return True
        
        whitelist_key = f"whitelist:{identifier}"
        is_whitelisted = await self.redis.exists(whitelist_key)
        
        if is_whitelisted:
            self.whitelist_cache[identifier] = True
        
        return bool(is_whitelisted)
    
    async def _is_blacklisted(self, identifier: str) -> bool:
        """Check if identifier is blacklisted"""
        if identifier in self.blacklist_cache:
            return True
        
        blacklist_key = f"blacklist:{identifier}"
        is_blacklisted = await self.redis.exists(blacklist_key)
        
        if is_blacklisted:
            self.blacklist_cache[identifier] = True
        
        return bool(is_blacklisted)
    
    async def add_to_whitelist(self, identifier -> None: str, ttl -> None: Optional[int] = None) -> None:
        """Add identifier to whitelist"""
        whitelist_key = f"whitelist:{identifier}"
        if ttl:
            await self.redis.setex(whitelist_key, ttl, "1")
        else:
            await self.redis.set(whitelist_key, "1")
        
        self.whitelist_cache[identifier] = True
    
    async def add_to_blacklist(self, identifier -> None: str, ttl -> None: int = 86400) -> None:
        """Add identifier to blacklist"""
        blacklist_key = f"blacklist:{identifier}"
        await self.redis.setex(blacklist_key, ttl, "1")
        self.blacklist_cache[identifier] = True
    
    async def remove_from_whitelist(self, identifier -> None: str) -> None:
        """Remove identifier from whitelist"""
        whitelist_key = f"whitelist:{identifier}"
        await self.redis.delete(whitelist_key)
        self.whitelist_cache.pop(identifier, None)
    
    async def remove_from_blacklist(self, identifier -> None: str) -> None:
        """Remove identifier from blacklist"""
        blacklist_key = f"blacklist:{identifier}"
        await self.redis.delete(blacklist_key)
        self.blacklist_cache.pop(identifier, None)
    
    async def get_rate_limit_status(self, identifier: str, limit_type: RateLimitType) -> Dict:
        """Get current rate limit status for identifier"""
        current_time = time.time()
        minute_window = int(current_time // 60)
        hour_window = int(current_time // 3600)
        day_window = int(current_time // 86400)
        
        minute_key = f"rate_limit:{identifier}:{limit_type.value}:minute:{minute_window}"
        hour_key = f"rate_limit:{identifier}:{limit_type.value}:hour:{hour_window}"
        day_key = f"rate_limit:{identifier}:{limit_type.value}:day:{day_window}"
        penalty_key = f"penalty:{identifier}:{limit_type.value}"
        
        pipe = self.redis.pipeline()
        pipe.get(minute_key)
        pipe.get(hour_key)
        pipe.get(day_key)
        pipe.ttl(penalty_key)
        
        results = await pipe.execute()
        
        rule = self.default_rules[limit_type]
        
        return {
            "identifier": identifier,
            "limit_type": limit_type.value,
            "minute_count": int(results[0] or 0),
            "hour_count": int(results[1] or 0),
            "day_count": int(results[2] or 0),
            "minute_limit": rule.requests_per_minute,
            "hour_limit": rule.requests_per_hour,
            "day_limit": rule.requests_per_day,
            "penalty_remaining": max(0, results[3]),
            "is_whitelisted": await self._is_whitelisted(identifier),
            "is_blacklisted": await self._is_blacklisted(identifier)
        }
    
    async def clear_rate_limits(self, identifier -> None: str, limit_type -> None: Optional[RateLimitType] = None) -> None:
        """Clear rate limits for identifier"""
        pattern = f"rate_limit:{identifier}:"
        if limit_type:
            pattern += f"{limit_type.value}:*"
        else:
            pattern += "*"
        
        keys = await self.redis.keys(pattern)
        if keys:
            await self.redis.delete(*keys)
    
    async def get_violation_stats(self, date: Optional[str] = None) -> List[Dict]:
        """Get rate limit violation statistics"""
        if not date:
            date = datetime.now().strftime('%Y-%m-%d')
        
        log_key = f"violations:{date}"
        violations = await self.redis.lrange(log_key, 0, -1)
        
        return [json.loads(violation) for violation in violations]
    
    async def create_custom_rule(
        self,
        identifier -> None: str,
        limit_type -> None: RateLimitType,
        rule -> None: RateLimitRule,
        ttl -> None: int = 3600
    ) -> None:
        """Create custom rate limit rule for specific identifier"""
        rule_key = f"custom_rule:{identifier}:{limit_type.value}"
        rule_data = {
            "requests_per_minute": rule.requests_per_minute,
            "requests_per_hour": rule.requests_per_hour,
            "requests_per_day": rule.requests_per_day,
            "burst_allowance": rule.burst_allowance,
            "penalty_duration": rule.penalty_duration,
            "whitelist_override": rule.whitelist_override
        }
        
        await self.redis.setex(rule_key, ttl, json.dumps(rule_data))
    
    async def apply_adaptive_limits(self, identifier -> None: str) -> None:
        """Apply adaptive rate limits based on historical behavior"""
        # Analyze historical patterns
        violation_history = await self._get_violation_history(identifier)
        trust_score = await self._calculate_trust_score(identifier, violation_history)
        
        # Adjust limits based on trust score
        if trust_score >= 0.8:
            # High trust - increase limits
            await self._apply_trust_multiplier(identifier, 2.0)
        elif trust_score <= 0.3:
            # Low trust - decrease limits
            await self._apply_trust_multiplier(identifier, 0.5)
    
    async def _get_violation_history(self, identifier: str) -> List[Dict]:
        """Get violation history for identifier"""
        history = []
        for days_back in range(7):
            date = (datetime.now() - timedelta(days=days_back)).strftime('%Y-%m-%d')
            violations = await self.get_violation_stats(date)
            history.extend([v for v in violations if v["identifier"] == identifier])
        
        return history
    
    async def _calculate_trust_score(self, identifier: str, violation_history: List[Dict]) -> float:
        """Calculate trust score based on violation history"""
        if not violation_history:
            return 1.0
        
        total_violations = len(violation_history)
        critical_violations = len([v for v in violation_history if v["severity"] == "critical"])
        
        # Base score calculation
        base_score = max(0.0, 1.0 - (total_violations * 0.1))
        
        # Penalty for critical violations
        critical_penalty = critical_violations * 0.2
        
        return max(0.0, base_score - critical_penalty)
    
    async def _apply_trust_multiplier(self, identifier -> None: str, multiplier -> None: float) -> None:
        """Apply trust-based multiplier to rate limits"""
        for limit_type in RateLimitType:
            base_rule = self.default_rules[limit_type]
            adjusted_rule = RateLimitRule(
                requests_per_minute=int(base_rule.requests_per_minute * multiplier),
                requests_per_hour=int(base_rule.requests_per_hour * multiplier),
                requests_per_day=int(base_rule.requests_per_day * multiplier),
                burst_allowance=int(base_rule.burst_allowance * multiplier),
                penalty_duration=base_rule.penalty_duration
            )
            
            await self.create_custom_rule(identifier, limit_type, adjusted_rule, ttl=86400)

class RateLimitMiddleware:
    """
    FastAPI middleware for automatic rate limiting
    """
    
    def __init__(self, enforcer -> None: RateLimitEnforcer) -> None:
        self.enforcer = enforcer
    
    async def __call__(self, request, call_next) -> None:
        """Process request with rate limiting"""
        # Extract identifier from request
        identifier = self._extract_identifier(request)
        
        # Determine rate limit type based on endpoint
        limit_type = self._determine_limit_type(request)
        
        # Check rate limit
        result = await self.enforcer.check_rate_limit(identifier, limit_type)
        
        if not result.allowed:
            # Return rate limit exceeded response
            return self._create_rate_limit_response(result)
        
        # Add rate limit headers to response
        response = await call_next(request)
        self._add_rate_limit_headers(response, result)
        
        return response
    
    def _extract_identifier(self, request) -> str:
        """Extract unique identifier from request"""
        # Try API key first
        api_key = request.headers.get("X-API-Key")
        if api_key:
            return f"api_key:{hashlib.sha256(api_key.encode()).hexdigest()[:16]}"
        
        # Try user ID from auth
        user_id = getattr(request.state, "user_id", None)
        if user_id:
            return f"user:{user_id}"
        
        # Fall back to IP address
        client_ip = request.client.host
        return f"ip:{client_ip}"
    
    def _determine_limit_type(self, request) -> RateLimitType:
        """Determine rate limit type based on request"""
        path = request.url.path
        
        if "/upload" in path:
            return RateLimitType.CONTENT_UPLOADS
        elif "/distribute" in path:
            return RateLimitType.DISTRIBUTION_REQUESTS
        elif "/bulk" in path:
            return RateLimitType.BULK_OPERATIONS
        else:
            return RateLimitType.API_CALLS
    
    def _create_rate_limit_response(self, result -> None: RateLimitResult) -> None:
        """Create rate limit exceeded response"""
        from fastapi.responses import JSONResponse
        
        return JSONResponse(
            status_code=429,
            content={
                "error": "Rate limit exceeded",
                "message": f"Too many requests. Current: {result.current_count}, Limit: {result.limit}",
                "retry_after": result.retry_after,
                "reset_time": result.reset_time.isoformat()
            },
            headers={
                "Retry-After": str(result.retry_after) if result.retry_after else "60",
                "X-RateLimit-Limit": str(result.limit),
                "X-RateLimit-Remaining": "0",
                "X-RateLimit-Reset": str(int(result.reset_time.timestamp()))
            }
        )
    
    def _add_rate_limit_headers(self, response, result -> None: RateLimitResult) -> None:
        """Add rate limit headers to successful response"""
        response.headers["X-RateLimit-Limit"] = str(result.limit)
        response.headers["X-RateLimit-Remaining"] = str(max(0, result.limit - result.current_count))
        response.headers["X-RateLimit-Reset"] = str(int(result.reset_time.timestamp()))
        
        if result.warning_threshold_reached:
            response.headers["X-RateLimit-Warning"] = "Approaching rate limit"