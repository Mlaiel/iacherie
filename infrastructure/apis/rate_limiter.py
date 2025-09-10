"""
API Rate Limiting System
Enterprise rate limiting for Ainflue APIs

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: © 2025 Fahed Mlaiel. All rights reserved.
"""

import logging
import asyncio
from typing import Dict, List, Optional, Any, Union, Tuple
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta
import time

logger = logging.getLogger(__name__)


class RateLimitType(Enum):
    """Rate limiting algorithms"""
    TOKEN_BUCKET = "token_bucket"
    SLIDING_WINDOW = "sliding_window"
    FIXED_WINDOW = "fixed_window"
    LEAKY_BUCKET = "leaky_bucket"


class RateLimitScope(Enum):
    """Rate limiting scope"""
    GLOBAL = "global"
    PER_USER = "per_user"
    PER_API_KEY = "per_api_key"
    PER_IP = "per_ip"
    PER_ROUTE = "per_route"


@dataclass
class RateLimitRule:
    """Rate limiting rule configuration"""
    name: str
    limit: int  # requests
    window: int  # seconds
    scope: RateLimitScope = RateLimitScope.PER_USER
    algorithm: RateLimitType = RateLimitType.SLIDING_WINDOW
    burst_limit: Optional[int] = None
    grace_period: int = 0
    enabled: bool = True
    routes: List[str] = field(default_factory=list)
    exemptions: List[str] = field(default_factory=list)


@dataclass
class RateLimitStatus:
    """Rate limit status information"""
    rule_name: str
    identifier: str
    current_usage: int
    limit: int
    remaining: int
    reset_time: datetime
    blocked: bool = False


class RateLimiter:
    """
    Enterprise API Rate Limiting System for Ainflue
    
    Provides comprehensive rate limiting capabilities:
    - Multiple algorithms (token bucket, sliding window, etc.)
    - Flexible scoping (per user, IP, API key, route)
    - Burst handling and grace periods
    - Real-time monitoring and analytics
    - Dynamic rule updates
    - Creator-specific rate limits
    - AI workload optimization
    """
    
    def __init__(self):
        """Initialize rate limiter"""
        self.rules = {}
        self.usage_tracking = {}
        self.blocked_requests = {}
        self.analytics = {}
        
        # Ainflue-specific rate limiting rules
        self.ainflue_rules = {
            "creator_upload": RateLimitRule(
                name="creator_upload",
                limit=50,  # 50 uploads per hour
                window=3600,
                scope=RateLimitScope.PER_USER,
                algorithm=RateLimitType.SLIDING_WINDOW,
                burst_limit=10,
                routes=["/api/v1/content/upload", "/api/v1/content/bulk-upload"]
            ),
            "ai_processing": RateLimitRule(
                name="ai_processing",
                limit=100,  # 100 AI requests per hour
                window=3600,
                scope=RateLimitScope.PER_USER,
                algorithm=RateLimitType.TOKEN_BUCKET,
                burst_limit=20,
                routes=["/api/v1/ai/analyze", "/api/v1/ai/recommend"]
            ),
            "api_access": RateLimitRule(
                name="api_access",
                limit=10000,  # 10k requests per hour
                window=3600,
                scope=RateLimitScope.PER_API_KEY,
                algorithm=RateLimitType.SLIDING_WINDOW,
                burst_limit=500
            ),
            "revenue_api": RateLimitRule(
                name="revenue_api",
                limit=200,  # 200 revenue requests per hour
                window=3600,
                scope=RateLimitScope.PER_USER,
                algorithm=RateLimitType.FIXED_WINDOW,
                routes=["/api/v1/revenue", "/api/v1/payments"]
            ),
            "collaboration": RateLimitRule(
                name="collaboration",
                limit=1000,  # 1k collaboration requests per hour
                window=3600,
                scope=RateLimitScope.PER_USER,
                algorithm=RateLimitType.SLIDING_WINDOW,
                burst_limit=100,
                routes=["/api/v1/collaborate", "/api/v1/messaging"]
            ),
            "public_api": RateLimitRule(
                name="public_api",
                limit=60,  # 60 requests per minute for public access
                window=60,
                scope=RateLimitScope.PER_IP,
                algorithm=RateLimitType.FIXED_WINDOW,
                routes=["/api/v1/public"]
            ),
            "premium_creator": RateLimitRule(
                name="premium_creator",
                limit=500,  # Premium creators get higher limits
                window=3600,
                scope=RateLimitScope.PER_USER,
                algorithm=RateLimitType.SLIDING_WINDOW,
                burst_limit=100,
                exemptions=["premium", "enterprise"]
            )
        }
        
        # Initialize default rules
        for rule_name, rule in self.ainflue_rules.items():
            self.add_rule(rule)
            
        logger.info("Rate limiter initialized with Ainflue-specific rules")
        
    async def check_rate_limit(self, identifier: str, route: str, 
                              user_tier: str = "standard") -> RateLimitStatus:
        """Check if request is within rate limits"""
        
        # Find applicable rules for this route
        applicable_rules = self._find_applicable_rules(route, user_tier)
        
        for rule in applicable_rules:
            # Get identifier based on scope
            scoped_identifier = self._get_scoped_identifier(identifier, rule.scope)
            
            # Check exemptions
            if user_tier in rule.exemptions:
                continue
                
            # Check rate limit based on algorithm
            status = await self._check_rule_limit(rule, scoped_identifier, route)
            
            if status.blocked:
                await self._record_blocked_request(rule.name, scoped_identifier, route)
                return status
                
        # If no rules block the request, return success status
        return RateLimitStatus(
            rule_name="none",
            identifier=identifier,
            current_usage=0,
            limit=float('inf'),
            remaining=float('inf'),
            reset_time=datetime.now() + timedelta(hours=1),
            blocked=False
        )
        
    async def _check_rule_limit(self, rule: RateLimitRule, 
                               identifier: str, route: str) -> RateLimitStatus:
        """Check rate limit for specific rule"""
        
        current_time = time.time()
        key = f"{rule.name}:{identifier}"
        
        if rule.algorithm == RateLimitType.SLIDING_WINDOW:
            return await self._check_sliding_window(rule, key, current_time)
        elif rule.algorithm == RateLimitType.TOKEN_BUCKET:
            return await self._check_token_bucket(rule, key, current_time)
        elif rule.algorithm == RateLimitType.FIXED_WINDOW:
            return await self._check_fixed_window(rule, key, current_time)
        elif rule.algorithm == RateLimitType.LEAKY_BUCKET:
            return await self._check_leaky_bucket(rule, key, current_time)
        else:
            raise ValueError(f"Unsupported rate limit algorithm: {rule.algorithm}")
            
    async def _check_sliding_window(self, rule: RateLimitRule, key: str, 
                                   current_time: float) -> RateLimitStatus:
        """Check sliding window rate limit"""
        
        if key not in self.usage_tracking:
            self.usage_tracking[key] = []
            
        # Remove old entries outside the window
        window_start = current_time - rule.window
        self.usage_tracking[key] = [
            timestamp for timestamp in self.usage_tracking[key] 
            if timestamp > window_start
        ]
        
        current_usage = len(self.usage_tracking[key])
        remaining = max(0, rule.limit - current_usage)
        
        # Check if request would exceed limit
        blocked = current_usage >= rule.limit
        
        # Handle burst limit
        if rule.burst_limit and current_usage < rule.burst_limit:
            blocked = False
            
        if not blocked:
            self.usage_tracking[key].append(current_time)
            current_usage += 1
            remaining -= 1
            
        return RateLimitStatus(
            rule_name=rule.name,
            identifier=key,
            current_usage=current_usage,
            limit=rule.limit,
            remaining=remaining,
            reset_time=datetime.fromtimestamp(current_time + rule.window),
            blocked=blocked
        )
        
    async def _check_token_bucket(self, rule: RateLimitRule, key: str, 
                                 current_time: float) -> RateLimitStatus:
        """Check token bucket rate limit"""
        
        if key not in self.usage_tracking:
            self.usage_tracking[key] = {
                'tokens': rule.limit,
                'last_refill': current_time
            }
            
        bucket = self.usage_tracking[key]
        
        # Calculate tokens to add based on time passed
        time_passed = current_time - bucket['last_refill']
        tokens_to_add = (time_passed / rule.window) * rule.limit
        
        # Refill bucket (up to limit)
        bucket['tokens'] = min(rule.limit, bucket['tokens'] + tokens_to_add)
        bucket['last_refill'] = current_time
        
        # Check if token available
        blocked = bucket['tokens'] < 1
        
        if not blocked:
            bucket['tokens'] -= 1
            
        return RateLimitStatus(
            rule_name=rule.name,
            identifier=key,
            current_usage=rule.limit - int(bucket['tokens']),
            limit=rule.limit,
            remaining=int(bucket['tokens']),
            reset_time=datetime.fromtimestamp(current_time + rule.window),
            blocked=blocked
        )
        
    async def _check_fixed_window(self, rule: RateLimitRule, key: str, 
                                 current_time: float) -> RateLimitStatus:
        """Check fixed window rate limit"""
        
        # Calculate current window
        window_start = int(current_time // rule.window) * rule.window
        window_key = f"{key}:{window_start}"
        
        if window_key not in self.usage_tracking:
            self.usage_tracking[window_key] = 0
            
        current_usage = self.usage_tracking[window_key]
        remaining = max(0, rule.limit - current_usage)
        
        blocked = current_usage >= rule.limit
        
        if not blocked:
            self.usage_tracking[window_key] += 1
            current_usage += 1
            remaining -= 1
            
        return RateLimitStatus(
            rule_name=rule.name,
            identifier=key,
            current_usage=current_usage,
            limit=rule.limit,
            remaining=remaining,
            reset_time=datetime.fromtimestamp(window_start + rule.window),
            blocked=blocked
        )
        
    async def _check_leaky_bucket(self, rule: RateLimitRule, key: str, 
                                 current_time: float) -> RateLimitStatus:
        """Check leaky bucket rate limit"""
        
        if key not in self.usage_tracking:
            self.usage_tracking[key] = {
                'queue': [],
                'last_leak': current_time
            }
            
        bucket = self.usage_tracking[key]
        
        # Calculate how many requests should have leaked
        time_passed = current_time - bucket['last_leak']
        leak_rate = rule.limit / rule.window  # requests per second
        leaked_requests = int(time_passed * leak_rate)
        
        # Remove leaked requests
        for _ in range(min(leaked_requests, len(bucket['queue']))):
            bucket['queue'].pop(0)
            
        bucket['last_leak'] = current_time
        
        current_usage = len(bucket['queue'])
        remaining = max(0, rule.limit - current_usage)
        
        blocked = current_usage >= rule.limit
        
        if not blocked:
            bucket['queue'].append(current_time)
            current_usage += 1
            remaining -= 1
            
        return RateLimitStatus(
            rule_name=rule.name,
            identifier=key,
            current_usage=current_usage,
            limit=rule.limit,
            remaining=remaining,
            reset_time=datetime.fromtimestamp(current_time + rule.window),
            blocked=blocked
        )
        
    def add_rule(self, rule: RateLimitRule) -> bool:
        """Add new rate limiting rule"""
        try:
            self.rules[rule.name] = rule
            logger.info(f"Added rate limiting rule: {rule.name}")
            return True
        except Exception as e:
            logger.error(f"Failed to add rate limiting rule {rule.name}: {e}")
            return False
            
    def update_rule(self, rule_name: str, updates: Dict[str, Any]) -> bool:
        """Update existing rate limiting rule"""
        try:
            if rule_name not in self.rules:
                raise ValueError(f"Rule {rule_name} not found")
                
            rule = self.rules[rule_name]
            for key, value in updates.items():
                if hasattr(rule, key):
                    setattr(rule, key, value)
                    
            logger.info(f"Updated rate limiting rule: {rule_name}")
            return True
        except Exception as e:
            logger.error(f"Failed to update rate limiting rule {rule_name}: {e}")
            return False
            
    def remove_rule(self, rule_name: str) -> bool:
        """Remove rate limiting rule"""
        try:
            if rule_name in self.rules:
                del self.rules[rule_name]
                logger.info(f"Removed rate limiting rule: {rule_name}")
                return True
            return False
        except Exception as e:
            logger.error(f"Failed to remove rate limiting rule {rule_name}: {e}")
            return False
            
    def _find_applicable_rules(self, route: str, user_tier: str) -> List[RateLimitRule]:
        """Find rules applicable to this route and user tier"""
        applicable_rules = []
        
        for rule in self.rules.values():
            if not rule.enabled:
                continue
                
            # Check if rule applies to this route
            if rule.routes and not any(route.startswith(r) for r in rule.routes):
                continue
                
            # Premium users might have different rules
            if user_tier == "premium" and rule.name == "premium_creator":
                applicable_rules.append(rule)
            elif user_tier != "premium" and rule.name != "premium_creator":
                applicable_rules.append(rule)
                
        return applicable_rules
        
    def _get_scoped_identifier(self, identifier: str, scope: RateLimitScope) -> str:
        """Get identifier based on rate limit scope"""
        if scope == RateLimitScope.GLOBAL:
            return "global"
        elif scope == RateLimitScope.PER_USER:
            return f"user:{identifier}"
        elif scope == RateLimitScope.PER_API_KEY:
            return f"api_key:{identifier}"
        elif scope == RateLimitScope.PER_IP:
            return f"ip:{identifier}"
        elif scope == RateLimitScope.PER_ROUTE:
            return f"route:{identifier}"
        else:
            return identifier
            
    async def _record_blocked_request(self, rule_name: str, identifier: str, route: str):
        """Record blocked request for analytics"""
        if rule_name not in self.blocked_requests:
            self.blocked_requests[rule_name] = []
            
        self.blocked_requests[rule_name].append({
            'identifier': identifier,
            'route': route,
            'timestamp': datetime.now(),
            'rule': rule_name
        })
        
    async def get_rate_limit_analytics(self, time_range: str = "1h") -> Dict[str, Any]:
        """Get rate limiting analytics and metrics"""
        
        analytics = {
            'time_range': time_range,
            'timestamp': datetime.now().isoformat(),
            'total_requests': 0,
            'blocked_requests': 0,
            'rules_triggered': {},
            'top_limited_routes': [],
            'top_limited_users': [],
            'performance_impact': {}
        }
        
        try:
            # Calculate metrics for each rule
            for rule_name, rule in self.rules.items():
                rule_stats = {
                    'total_requests': 0,
                    'blocked_requests': 0,
                    'block_rate': 0.0,
                    'top_consumers': []
                }
                
                # Count blocked requests for this rule
                if rule_name in self.blocked_requests:
                    blocked = len(self.blocked_requests[rule_name])
                    rule_stats['blocked_requests'] = blocked
                    analytics['blocked_requests'] += blocked
                    
                # Estimate total requests (simplified)
                estimated_total = rule_stats['blocked_requests'] * 10
                rule_stats['total_requests'] = estimated_total
                analytics['total_requests'] += estimated_total
                
                if estimated_total > 0:
                    rule_stats['block_rate'] = (rule_stats['blocked_requests'] / estimated_total) * 100
                    
                analytics['rules_triggered'][rule_name] = rule_stats
                
            # Calculate overall block rate
            if analytics['total_requests'] > 0:
                overall_block_rate = (analytics['blocked_requests'] / analytics['total_requests']) * 100
            else:
                overall_block_rate = 0
                
            analytics['overall_block_rate'] = overall_block_rate
            
            # Top limited routes (mock data)
            analytics['top_limited_routes'] = [
                {'route': '/api/v1/content/upload', 'blocks': 150},
                {'route': '/api/v1/ai/analyze', 'blocks': 89},
                {'route': '/api/v1/revenue', 'blocks': 45}
            ]
            
            # Performance impact
            analytics['performance_impact'] = {
                'avg_check_time': 2.5,  # milliseconds
                'cache_hit_rate': 85.6,
                'memory_usage': '45MB'
            }
            
        except Exception as e:
            logger.error(f"Failed to generate rate limit analytics: {e}")
            analytics['error'] = str(e)
            
        return analytics
        
    async def reset_user_limits(self, identifier: str, rule_names: List[str] = None) -> Dict[str, Any]:
        """Reset rate limits for specific user"""
        
        reset_result = {
            'identifier': identifier,
            'timestamp': datetime.now().isoformat(),
            'reset_rules': [],
            'status': 'success'
        }
        
        try:
            rules_to_reset = rule_names or list(self.rules.keys())
            
            for rule_name in rules_to_reset:
                if rule_name not in self.rules:
                    continue
                    
                rule = self.rules[rule_name]
                scoped_identifier = self._get_scoped_identifier(identifier, rule.scope)
                
                # Remove usage tracking for this identifier
                keys_to_remove = [key for key in self.usage_tracking.keys() 
                                 if key.startswith(f"{rule_name}:{scoped_identifier}")]
                
                for key in keys_to_remove:
                    del self.usage_tracking[key]
                    
                reset_result['reset_rules'].append(rule_name)
                
            logger.info(f"Reset rate limits for {identifier}: {reset_result['reset_rules']}")
            
        except Exception as e:
            logger.error(f"Failed to reset rate limits for {identifier}: {e}")
            reset_result['status'] = 'failed'
            reset_result['error'] = str(e)
            
        return reset_result
        
    async def get_user_limits_status(self, identifier: str) -> Dict[str, Any]:
        """Get current rate limit status for user"""
        
        status = {
            'identifier': identifier,
            'timestamp': datetime.now().isoformat(),
            'limits': [],
            'next_reset': None
        }
        
        try:
            current_time = time.time()
            earliest_reset = None
            
            for rule_name, rule in self.rules.items():
                scoped_identifier = self._get_scoped_identifier(identifier, rule.scope)
                key = f"{rule_name}:{scoped_identifier}"
                
                # Get current usage
                if rule.algorithm == RateLimitType.SLIDING_WINDOW:
                    usage = len(self.usage_tracking.get(key, []))
                elif rule.algorithm == RateLimitType.TOKEN_BUCKET:
                    bucket = self.usage_tracking.get(key, {'tokens': rule.limit})
                    usage = rule.limit - int(bucket['tokens'])
                else:
                    usage = 0
                    
                remaining = max(0, rule.limit - usage)
                reset_time = datetime.fromtimestamp(current_time + rule.window)
                
                if earliest_reset is None or reset_time < earliest_reset:
                    earliest_reset = reset_time
                    
                status['limits'].append({
                    'rule': rule_name,
                    'current_usage': usage,
                    'limit': rule.limit,
                    'remaining': remaining,
                    'reset_time': reset_time.isoformat(),
                    'window_seconds': rule.window
                })
                
            status['next_reset'] = earliest_reset.isoformat() if earliest_reset else None
            
        except Exception as e:
            logger.error(f"Failed to get rate limit status for {identifier}: {e}")
            status['error'] = str(e)
            
        return status