"""
Rate Limiter - Enterprise Rate Limiting and Throttling
© 2025 Fahed Mlaiel. All rights reserved.

Advanced rate limiting system for Ainflue creator platform with multi-tier
rate limiting, burst protection, and creator-specific quotas.
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum
import time
import uuid

logger = logging.getLogger(__name__)


class RateLimitAlgorithm(Enum):
    """Rate limiting algorithms"""
    TOKEN_BUCKET = "token_bucket"
    SLIDING_WINDOW = "sliding_window"
    FIXED_WINDOW = "fixed_window"
    LEAKY_BUCKET = "leaky_bucket"


class RateLimitScope(Enum):
    """Rate limit scope levels"""
    GLOBAL = "global"
    USER = "user"
    CREATOR = "creator"
    IP_ADDRESS = "ip_address"
    API_KEY = "api_key"
    ENDPOINT = "endpoint"


@dataclass
class RateLimitRule:
    """Rate limit rule definition"""
    rule_id: str
    scope: RateLimitScope
    algorithm: RateLimitAlgorithm
    limit: int
    window_seconds: int
    burst_limit: Optional[int]
    priority: int
    description: str
    enabled: bool


@dataclass
class RateLimitResult:
    """Rate limit check result"""
    allowed: bool
    limit: int
    remaining: int
    reset_time: int
    retry_after: Optional[int]
    headers: Dict[str, str]


class RateLimiter:
    """
    Enterprise Rate Limiting for Creator Platform
    
    Advanced rate limiting capabilities:
    - Multi-algorithm support (token bucket, sliding window, etc.)
    - Creator-specific rate limits
    - Content upload quotas
    - AI processing throttling
    - Platform integration limits
    - Burst protection
    - Dynamic rate limit adjustment
    - Distributed rate limiting support
    """
    
    def __init__(self):
        self.rate_limit_rules = {}
        self.rate_limit_storage = {}  # In-memory storage (would use Redis in production)
        self.rate_limit_violations = {}
        
        # Rate limiter configuration
        self.config = {
            'default_algorithm': RateLimitAlgorithm.TOKEN_BUCKET,
            'cleanup_interval_seconds': 300,  # 5 minutes
            'violation_tracking_enabled': True,
            'dynamic_adjustment_enabled': True,
            'distributed_mode': False  # Would be True with Redis backend
        }
        
        # Initialize Ainflue-specific rate limiting rules
        self.ainflue_rate_limits = self._initialize_ainflue_rate_limits()
        
        # Rate limiting metrics
        self.metrics = {
            'total_requests': 0,
            'allowed_requests': 0,
            'denied_requests': 0,
            'active_rate_limits': 0,
            'violation_count': 0,
            'average_response_time_ms': 0.0
        }
        
        logger.info("Rate limiter initialized for creator platform")
    
    def _initialize_ainflue_rate_limits(self) -> Dict[str, RateLimitRule]:
        """Initialize Ainflue creator platform rate limiting rules"""
        
        rules = {}
        
        # Creator content upload limits
        rules['creator_content_upload'] = RateLimitRule(
            rule_id='creator_content_upload',
            scope=RateLimitScope.CREATOR,
            algorithm=RateLimitAlgorithm.TOKEN_BUCKET,
            limit=10,  # 10 uploads per minute
            window_seconds=60,
            burst_limit=5,  # Allow burst of 5 uploads
            priority=1,
            description='Creator content upload rate limit',
            enabled=True
        )
        
        # AI processing limits
        rules['ai_processing_requests'] = RateLimitRule(
            rule_id='ai_processing_requests',
            scope=RateLimitScope.CREATOR,
            algorithm=RateLimitAlgorithm.SLIDING_WINDOW,
            limit=20,  # 20 AI requests per minute
            window_seconds=60,
            burst_limit=10,
            priority=1,
            description='AI processing rate limit for creators',
            enabled=True
        )
        
        # Platform distribution limits
        rules['platform_distribution'] = RateLimitRule(
            rule_id='platform_distribution',
            scope=RateLimitScope.CREATOR,
            algorithm=RateLimitAlgorithm.TOKEN_BUCKET,
            limit=30,  # 30 distribution requests per minute
            window_seconds=60,
            burst_limit=15,
            priority=1,
            description='Content distribution to platforms rate limit',
            enabled=True
        )
        
        # Analytics queries
        rules['analytics_queries'] = RateLimitRule(
            rule_id='analytics_queries',
            scope=RateLimitScope.USER,
            algorithm=RateLimitAlgorithm.SLIDING_WINDOW,
            limit=100,  # 100 analytics queries per minute
            window_seconds=60,
            burst_limit=50,
            priority=2,
            description='Analytics API rate limit',
            enabled=True
        )
        
        # Platform integration OAuth
        rules['platform_oauth'] = RateLimitRule(
            rule_id='platform_oauth',
            scope=RateLimitScope.IP_ADDRESS,
            algorithm=RateLimitAlgorithm.FIXED_WINDOW,
            limit=10,  # 10 OAuth attempts per minute per IP
            window_seconds=60,
            burst_limit=5,
            priority=1,
            description='Platform OAuth rate limit',
            enabled=True
        )
        
        # User registration
        rules['user_registration'] = RateLimitRule(
            rule_id='user_registration',
            scope=RateLimitScope.IP_ADDRESS,
            algorithm=RateLimitAlgorithm.FIXED_WINDOW,
            limit=5,  # 5 registrations per hour per IP
            window_seconds=3600,
            burst_limit=2,
            priority=1,
            description='User registration rate limit',
            enabled=True
        )
        
        # Creator collaboration requests
        rules['collaboration_requests'] = RateLimitRule(
            rule_id='collaboration_requests',
            scope=RateLimitScope.CREATOR,
            algorithm=RateLimitAlgorithm.TOKEN_BUCKET,
            limit=20,  # 20 collaboration requests per hour
            window_seconds=3600,
            burst_limit=10,
            priority=2,
            description='Creator collaboration request rate limit',
            enabled=True
        )
        
        # Revenue analytics exports
        rules['revenue_data_export'] = RateLimitRule(
            rule_id='revenue_data_export',
            scope=RateLimitScope.CREATOR,
            algorithm=RateLimitAlgorithm.FIXED_WINDOW,
            limit=5,  # 5 exports per day
            window_seconds=86400,
            burst_limit=2,
            priority=1,
            description='Revenue data export rate limit',
            enabled=True
        )
        
        # Global API limits (fallback)
        rules['global_api_limit'] = RateLimitRule(
            rule_id='global_api_limit',
            scope=RateLimitScope.GLOBAL,
            algorithm=RateLimitAlgorithm.SLIDING_WINDOW,
            limit=1000000,  # 1M requests per hour globally
            window_seconds=3600,
            burst_limit=100000,
            priority=10,
            description='Global API rate limit',
            enabled=True
        )
        
        return rules
    
    async def check_rate_limit(
        self,
        key: str,
        limit: int,
        window_seconds: int,
        algorithm: RateLimitAlgorithm = None,
        burst_limit: int = None
    ) -> Dict[str, Any]:
        """Check rate limit for specific key"""
        
        start_time = time.time()
        self.metrics['total_requests'] += 1
        
        try:
            # Use specified algorithm or default
            algorithm = algorithm or self.config['default_algorithm']
            
            # Check rate limit based on algorithm
            if algorithm == RateLimitAlgorithm.TOKEN_BUCKET:
                result = await self._check_token_bucket(key, limit, window_seconds, burst_limit)
            elif algorithm == RateLimitAlgorithm.SLIDING_WINDOW:
                result = await self._check_sliding_window(key, limit, window_seconds)
            elif algorithm == RateLimitAlgorithm.FIXED_WINDOW:
                result = await self._check_fixed_window(key, limit, window_seconds)
            elif algorithm == RateLimitAlgorithm.LEAKY_BUCKET:
                result = await self._check_leaky_bucket(key, limit, window_seconds)
            else:
                # Default to token bucket
                result = await self._check_token_bucket(key, limit, window_seconds, burst_limit)
            
            # Update metrics
            if result['allowed']:
                self.metrics['allowed_requests'] += 1
            else:
                self.metrics['denied_requests'] += 1
                self.metrics['violation_count'] += 1
                
                # Track violations
                if self.config['violation_tracking_enabled']:
                    await self._track_violation(key, limit, window_seconds)
            
            # Update response time metric
            response_time_ms = (time.time() - start_time) * 1000
            self._update_average_response_time(response_time_ms)
            
            return result
            
        except Exception as e:
            logger.error(f"Error checking rate limit for key {key}: {e}")
            # Allow request on error (fail-open)
            return {
                'allowed': True,
                'limit': limit,
                'remaining': limit - 1,
                'reset_time': int(time.time()) + window_seconds,
                'retry_after': None,
                'headers': {}
            }
    
    async def _check_token_bucket(
        self,
        key: str,
        limit: int,
        window_seconds: int,
        burst_limit: int = None
    ) -> Dict[str, Any]:
        """Token bucket algorithm implementation"""
        
        current_time = time.time()
        bucket_key = f"token_bucket:{key}"
        
        # Get or initialize bucket
        if bucket_key not in self.rate_limit_storage:
            self.rate_limit_storage[bucket_key] = {
                'tokens': limit,
                'last_refill': current_time,
                'burst_tokens': burst_limit or limit
            }
        
        bucket = self.rate_limit_storage[bucket_key]
        
        # Calculate tokens to add based on time elapsed
        time_elapsed = current_time - bucket['last_refill']
        tokens_to_add = int(time_elapsed * (limit / window_seconds))
        
        # Refill tokens
        bucket['tokens'] = min(limit, bucket['tokens'] + tokens_to_add)
        bucket['last_refill'] = current_time
        
        # Check if request can be allowed
        if bucket['tokens'] >= 1:
            bucket['tokens'] -= 1
            allowed = True
            remaining = bucket['tokens']
        else:
            allowed = False
            remaining = 0
        
        # Calculate reset time
        reset_time = int(current_time + window_seconds)
        retry_after = None if allowed else int(window_seconds - (bucket['tokens'] * window_seconds / limit))
        
        return {
            'allowed': allowed,
            'limit': limit,
            'remaining': remaining,
            'reset_time': reset_time,
            'retry_after': retry_after,
            'headers': {
                'X-RateLimit-Limit': str(limit),
                'X-RateLimit-Remaining': str(remaining),
                'X-RateLimit-Reset': str(reset_time)
            }
        }
    
    async def _check_sliding_window(
        self,
        key: str,
        limit: int,
        window_seconds: int
    ) -> Dict[str, Any]:
        """Sliding window algorithm implementation"""
        
        current_time = time.time()
        window_key = f"sliding_window:{key}"
        
        # Get or initialize window
        if window_key not in self.rate_limit_storage:
            self.rate_limit_storage[window_key] = []
        
        request_times = self.rate_limit_storage[window_key]
        
        # Remove old requests outside the window
        cutoff_time = current_time - window_seconds
        request_times[:] = [t for t in request_times if t > cutoff_time]
        
        # Check if we can allow this request
        if len(request_times) < limit:
            request_times.append(current_time)
            allowed = True
            remaining = limit - len(request_times)
        else:
            allowed = False
            remaining = 0
        
        # Calculate reset time (when oldest request will expire)
        reset_time = int(request_times[0] + window_seconds) if request_times else int(current_time + window_seconds)
        retry_after = None if allowed else int(reset_time - current_time)
        
        return {
            'allowed': allowed,
            'limit': limit,
            'remaining': remaining,
            'reset_time': reset_time,
            'retry_after': retry_after,
            'headers': {
                'X-RateLimit-Limit': str(limit),
                'X-RateLimit-Remaining': str(remaining),
                'X-RateLimit-Reset': str(reset_time)
            }
        }
    
    async def _check_fixed_window(
        self,
        key: str,
        limit: int,
        window_seconds: int
    ) -> Dict[str, Any]:
        """Fixed window algorithm implementation"""
        
        current_time = time.time()
        window_start = int(current_time // window_seconds) * window_seconds
        window_key = f"fixed_window:{key}:{window_start}"
        
        # Get or initialize window counter
        if window_key not in self.rate_limit_storage:
            self.rate_limit_storage[window_key] = {
                'count': 0,
                'window_start': window_start
            }
        
        window_data = self.rate_limit_storage[window_key]
        
        # Check if we can allow this request
        if window_data['count'] < limit:
            window_data['count'] += 1
            allowed = True
            remaining = limit - window_data['count']
        else:
            allowed = False
            remaining = 0
        
        # Calculate reset time
        reset_time = int(window_start + window_seconds)
        retry_after = None if allowed else int(reset_time - current_time)
        
        return {
            'allowed': allowed,
            'limit': limit,
            'remaining': remaining,
            'reset_time': reset_time,
            'retry_after': retry_after,
            'headers': {
                'X-RateLimit-Limit': str(limit),
                'X-RateLimit-Remaining': str(remaining),
                'X-RateLimit-Reset': str(reset_time)
            }
        }
    
    async def _check_leaky_bucket(
        self,
        key: str,
        limit: int,
        window_seconds: int
    ) -> Dict[str, Any]:
        """Leaky bucket algorithm implementation"""
        
        current_time = time.time()
        bucket_key = f"leaky_bucket:{key}"
        
        # Get or initialize bucket
        if bucket_key not in self.rate_limit_storage:
            self.rate_limit_storage[bucket_key] = {
                'volume': 0,
                'last_leak': current_time
            }
        
        bucket = self.rate_limit_storage[bucket_key]
        
        # Calculate leak amount based on time elapsed
        time_elapsed = current_time - bucket['last_leak']
        leak_amount = time_elapsed * (limit / window_seconds)
        
        # Apply leak
        bucket['volume'] = max(0, bucket['volume'] - leak_amount)
        bucket['last_leak'] = current_time
        
        # Check if we can add this request
        if bucket['volume'] < limit:
            bucket['volume'] += 1
            allowed = True
            remaining = int(limit - bucket['volume'])
        else:
            allowed = False
            remaining = 0
        
        # Calculate reset time
        reset_time = int(current_time + window_seconds)
        retry_after = None if allowed else int(bucket['volume'] / (limit / window_seconds))
        
        return {
            'allowed': allowed,
            'limit': limit,
            'remaining': remaining,
            'reset_time': reset_time,
            'retry_after': retry_after,
            'headers': {
                'X-RateLimit-Limit': str(limit),
                'X-RateLimit-Remaining': str(remaining),
                'X-RateLimit-Reset': str(reset_time)
            }
        }
    
    async def _track_violation(self, key: str, limit: int, window_seconds: int):
        """Track rate limit violations for analysis"""
        
        violation_key = f"violations:{key}"
        
        if violation_key not in self.rate_limit_violations:
            self.rate_limit_violations[violation_key] = []
        
        violation = {
            'timestamp': datetime.utcnow(),
            'key': key,
            'limit': limit,
            'window_seconds': window_seconds
        }
        
        self.rate_limit_violations[violation_key].append(violation)
        
        # Keep only recent violations (last 24 hours)
        cutoff_time = datetime.utcnow() - timedelta(hours=24)
        self.rate_limit_violations[violation_key] = [
            v for v in self.rate_limit_violations[violation_key]
            if v['timestamp'] > cutoff_time
        ]
    
    def _update_average_response_time(self, response_time_ms: float):
        """Update average response time metric"""
        current_avg = self.metrics['average_response_time_ms']
        total_requests = self.metrics['total_requests']
        
        self.metrics['average_response_time_ms'] = (
            (current_avg * (total_requests - 1) + response_time_ms) / total_requests
        )
    
    async def check_creator_rate_limit(
        self,
        creator_id: str,
        action: str,
        **kwargs
    ) -> Dict[str, Any]:
        """Check rate limit for creator-specific action"""
        
        rule_mapping = {
            'content_upload': 'creator_content_upload',
            'ai_processing': 'ai_processing_requests',
            'distribution': 'platform_distribution',
            'collaboration': 'collaboration_requests',
            'revenue_export': 'revenue_data_export'
        }
        
        rule_id = rule_mapping.get(action)
        if not rule_id or rule_id not in self.ainflue_rate_limits:
            # Use default creator limits
            return await self.check_rate_limit(
                key=f"creator:{creator_id}:{action}",
                limit=100,
                window_seconds=3600
            )
        
        rule = self.ainflue_rate_limits[rule_id]
        key = f"creator:{creator_id}:{action}"
        
        return await self.check_rate_limit(
            key=key,
            limit=rule.limit,
            window_seconds=rule.window_seconds,
            algorithm=rule.algorithm,
            burst_limit=rule.burst_limit
        )
    
    async def adjust_rate_limit(
        self,
        key: str,
        new_limit: int,
        window_seconds: int = None
    ) -> bool:
        """Dynamically adjust rate limit for key"""
        
        try:
            # This would update the limit in distributed storage
            # For now, just log the adjustment
            logger.info(f"Rate limit adjusted for {key}: new limit {new_limit}")
            return True
            
        except Exception as e:
            logger.error(f"Error adjusting rate limit for {key}: {e}")
            return False
    
    async def whitelist_key(self, key: str, duration_seconds: int = 3600) -> bool:
        """Temporarily whitelist a key from rate limiting"""
        
        try:
            whitelist_key = f"whitelist:{key}"
            self.rate_limit_storage[whitelist_key] = {
                'expires_at': time.time() + duration_seconds,
                'whitelisted': True
            }
            
            logger.info(f"Key whitelisted: {key} for {duration_seconds} seconds")
            return True
            
        except Exception as e:
            logger.error(f"Error whitelisting key {key}: {e}")
            return False
    
    async def is_whitelisted(self, key: str) -> bool:
        """Check if key is whitelisted"""
        
        whitelist_key = f"whitelist:{key}"
        
        if whitelist_key in self.rate_limit_storage:
            whitelist_data = self.rate_limit_storage[whitelist_key]
            
            if whitelist_data.get('whitelisted') and time.time() < whitelist_data.get('expires_at', 0):
                return True
            else:
                # Remove expired whitelist entry
                del self.rate_limit_storage[whitelist_key]
        
        return False
    
    async def get_status(self) -> Dict[str, Any]:
        """Get rate limiter status and metrics"""
        
        status = {
            'timestamp': datetime.utcnow().isoformat(),
            'metrics': self.metrics.copy(),
            'configuration': {
                'default_algorithm': self.config['default_algorithm'].value,
                'violation_tracking_enabled': self.config['violation_tracking_enabled'],
                'dynamic_adjustment_enabled': self.config['dynamic_adjustment_enabled'],
                'distributed_mode': self.config['distributed_mode']
            },
            'active_rules': len(self.ainflue_rate_limits),
            'active_rate_limits': len(self.rate_limit_storage),
            'recent_violations': 0,
            'top_violated_keys': []
        }
        
        # Calculate recent violations
        cutoff_time = datetime.utcnow() - timedelta(hours=1)
        recent_violations = 0
        
        for violations in self.rate_limit_violations.values():
            recent_violations += len([
                v for v in violations 
                if v['timestamp'] > cutoff_time
            ])
        
        status['recent_violations'] = recent_violations
        
        # Get top violated keys
        violation_counts = {}
        for key, violations in self.rate_limit_violations.items():
            recent_violations_for_key = [
                v for v in violations 
                if v['timestamp'] > cutoff_time
            ]
            if recent_violations_for_key:
                violation_counts[key] = len(recent_violations_for_key)
        
        status['top_violated_keys'] = sorted(
            violation_counts.items(),
            key=lambda x: x[1],
            reverse=True
        )[:10]
        
        return status
    
    async def cleanup_expired_entries(self):
        """Clean up expired rate limit entries"""
        
        current_time = time.time()
        expired_keys = []
        
        for key, data in self.rate_limit_storage.items():
            # Check for expired entries based on key type
            if key.startswith('fixed_window:'):
                window_start = data.get('window_start', 0)
                window_seconds = 3600  # Default window
                if current_time > window_start + window_seconds + 300:  # 5 minute grace period
                    expired_keys.append(key)
            
            elif key.startswith('whitelist:'):
                expires_at = data.get('expires_at', 0)
                if current_time > expires_at:
                    expired_keys.append(key)
        
        # Remove expired entries
        for key in expired_keys:
            del self.rate_limit_storage[key]
        
        if expired_keys:
            logger.info(f"Cleaned up {len(expired_keys)} expired rate limit entries")
    
    async def start_cleanup_task(self):
        """Start background cleanup task"""
        
        while True:
            try:
                await asyncio.sleep(self.config['cleanup_interval_seconds'])
                await self.cleanup_expired_entries()
            except Exception as e:
                logger.error(f"Error in rate limiter cleanup task: {e}")
                await asyncio.sleep(60)  # Wait 1 minute before retrying