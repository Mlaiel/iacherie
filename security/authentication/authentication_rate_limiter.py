#!/usr/bin/env python3
"""
🔒 Authentication Rate Limiter - Anti-Brute Force Protection
============================================================

Enterprise authentication rate limiting system with adaptive algorithms,
distributed synchronization, and intelligent threat detection.

⚠️  PROPRIÉTÉ INTELLECTUELLE EXCLUSIVE - FAHED MLAIEL ⚠️
© 2025 Fahed Mlaiel. Tous droits réservés.
Contact: mlaiel@live.de

Author: Fahed Mlaiel (mlaiel@live.de)
Multi-Expert Implementation: Security + Redis + ML + Backend
Version: 2.0.0 Enterprise
Created: 2025-01-09
"""

import asyncio
import json
import logging
import time
import math
from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, List, Optional, Any, Tuple, Set
from dataclasses import dataclass, asdict
from pathlib import Path
import hashlib
import redis
from collections import defaultdict, deque
import threading
from concurrent.futures import ThreadPoolExecutor

# ML imports for adaptive rate limiting
import numpy as np
from sklearn.cluster import DBSCAN
from sklearn.preprocessing import StandardScaler


class RateLimitAlgorithm(Enum):
    """Rate limiting algorithms"""
    TOKEN_BUCKET = "token_bucket"
    SLIDING_WINDOW = "sliding_window"
    FIXED_WINDOW = "fixed_window"
    ADAPTIVE = "adaptive"
    EXPONENTIAL_BACKOFF = "exponential_backoff"
    PROGRESSIVE = "progressive"


class LimitScope(Enum):
    """Rate limit scope"""
    USER = "user"
    IP_ADDRESS = "ip_address"
    USER_AGENT = "user_agent"
    DEVICE = "device"
    SESSION = "session"
    GLOBAL = "global"
    SUBNET = "subnet"
    COUNTRY = "country"


class ActionType(Enum):
    """Types of actions to rate limit"""
    LOGIN_ATTEMPT = "login_attempt"
    PASSWORD_RESET = "password_reset"
    MFA_ATTEMPT = "mfa_attempt"
    ACCOUNT_CREATION = "account_creation"
    PASSWORD_CHANGE = "password_change"
    API_REQUEST = "api_request"
    FILE_UPLOAD = "file_upload"
    DATA_EXPORT = "data_export"


class LimitStatus(Enum):
    """Rate limit status"""
    ALLOWED = "allowed"
    THROTTLED = "throttled"
    BLOCKED = "blocked"
    SUSPENDED = "suspended"


@dataclass
class RateLimit:
    """Rate limit configuration"""
    limit_id: str
    action_type: ActionType
    scope: LimitScope
    algorithm: RateLimitAlgorithm
    
    # Limit parameters
    max_requests: int
    time_window_seconds: int
    burst_allowance: int
    
    # Adaptive parameters
    base_limit: int
    max_limit: int
    increase_factor: float
    decrease_factor: float
    
    # Backoff parameters
    initial_delay: float
    max_delay: float
    backoff_factor: float
    
    # Thresholds
    warning_threshold: float
    block_threshold: float
    suspend_threshold: float
    
    # Configuration
    enabled: bool
    priority: int
    created_at: datetime
    updated_at: datetime


@dataclass
class LimitBucket:
    """Token bucket for rate limiting"""
    bucket_id: str
    scope_key: str
    algorithm: RateLimitAlgorithm
    
    # Bucket state
    tokens: float
    max_tokens: int
    refill_rate: float
    last_refill: datetime
    
    # Tracking
    total_requests: int
    blocked_requests: int
    last_request: datetime
    
    # Adaptive state
    current_limit: int
    violation_count: int
    consecutive_violations: int
    last_violation: Optional[datetime]
    
    # Backoff state
    current_delay: float
    backoff_until: Optional[datetime]


@dataclass
class RateLimitResult:
    """Rate limiting result"""
    status: LimitStatus
    allowed: bool
    remaining_requests: int
    reset_time: datetime
    retry_after: Optional[int]
    
    # Details
    limit_id: str
    scope_key: str
    algorithm: str
    violated_limits: List[str]
    
    # Adaptive information
    current_limit: int
    violation_count: int
    
    # Headers for HTTP responses
    headers: Dict[str, str]


@dataclass
class RateLimitMetrics:
    """Rate limiting metrics"""
    total_requests: int
    allowed_requests: int
    throttled_requests: int
    blocked_requests: int
    
    # By scope
    requests_by_scope: Dict[str, int]
    blocks_by_scope: Dict[str, int]
    
    # By action
    requests_by_action: Dict[str, int]
    blocks_by_action: Dict[str, int]
    
    # Adaptive metrics
    adaptations_count: int
    limits_increased: int
    limits_decreased: int
    
    # Performance
    avg_processing_time: float
    cache_hit_rate: float


class AuthenticationRateLimiter:
    """
    🔒 Enterprise Authentication Rate Limiter
    
    Advanced rate limiting with adaptive algorithms, ML-powered threat detection,
    and distributed synchronization for comprehensive brute force protection.
    """
    
    def __init__(self, config_path: Optional[str] = None):
        """Initialize authentication rate limiter"""
        self.logger = logging.getLogger(__name__)
        self.config_path = config_path or "security/config/rate_limit_config.json"
        
        # Load configuration
        self.config = self._load_config()
        
        # Rate limits configuration
        self.rate_limits: Dict[str, RateLimit] = {}
        self.load_rate_limits()
        
        # Bucket storage (in-memory and Redis)
        self.buckets: Dict[str, LimitBucket] = {}
        self.redis_client = None
        self._setup_redis_connection()
        
        # ML components for adaptive limiting
        self.scaler = StandardScaler()
        self.clustering_model = DBSCAN(eps=0.5, min_samples=3)
        
        # Request tracking
        self.request_history: deque = deque(maxlen=10000)
        self.suspicious_patterns: Dict[str, Any] = {}
        
        # Metrics
        self.metrics = RateLimitMetrics(
            total_requests=0,
            allowed_requests=0,
            throttled_requests=0,
            blocked_requests=0,
            requests_by_scope={},
            blocks_by_scope={},
            requests_by_action={},
            blocks_by_action={},
            adaptations_count=0,
            limits_increased=0,
            limits_decreased=0,
            avg_processing_time=0.0,
            cache_hit_rate=0.0
        )
        
        # Background processing
        self.executor = ThreadPoolExecutor(max_workers=2)
        self.cleanup_task = None
        self.adaptation_task = None
        
        # Start background tasks
        self._start_background_tasks()
        
        # Cache for performance
        self.bucket_cache = {}
        self.cache_ttl = 300  # 5 minutes
    
    async def check_rate_limit(
        self,
        action_type: ActionType,
        scope_key: str,
        scope_type: LimitScope,
        request_context: Optional[Dict[str, Any]] = None
    ) -> RateLimitResult:
        """
        Check rate limit for an action
        
        Args:
            action_type: Type of action being performed
            scope_key: Unique identifier for the scope (user ID, IP, etc.)
            scope_type: Type of scope being limited
            request_context: Additional request context
            
        Returns:
            Rate limit result
        """
        start_time = time.time()
        
        try:
            # Find applicable rate limits
            applicable_limits = self._find_applicable_limits(action_type, scope_type)
            
            if not applicable_limits:
                # No limits configured, allow request
                return self._create_allowed_result(scope_key, "no_limits")
            
            # Check each applicable limit
            violated_limits = []
            most_restrictive_result = None
            
            for rate_limit in applicable_limits:
                bucket_key = self._generate_bucket_key(rate_limit, scope_key)
                bucket = await self._get_or_create_bucket(rate_limit, bucket_key, scope_key)
                
                # Check if limit is violated
                result = await self._check_bucket_limit(rate_limit, bucket, request_context)
                
                if result.status != LimitStatus.ALLOWED:
                    violated_limits.append(rate_limit.limit_id)
                    
                    # Keep the most restrictive result
                    if (most_restrictive_result is None or 
                        self._is_more_restrictive(result, most_restrictive_result)):
                        most_restrictive_result = result
                
                # Update bucket state
                await self._update_bucket_state(rate_limit, bucket, result.allowed)
            
            # Return the most restrictive result or allow if no violations
            final_result = most_restrictive_result or self._create_allowed_result(scope_key, "within_limits")
            final_result.violated_limits = violated_limits
            
            # Update metrics
            self._update_metrics(action_type, scope_type, final_result)
            
            # Track request for adaptive learning
            await self._track_request(action_type, scope_key, scope_type, final_result, request_context)
            
            # Update processing time metric
            processing_time = time.time() - start_time
            self._update_processing_time(processing_time)
            
            return final_result
            
        except Exception as e:
            self.logger.error(f"Rate limit check error: {e}")
            # Fail open - allow request but log error
            return self._create_allowed_result(scope_key, "error_occurred")
    
    async def record_successful_action(
        self,
        action_type: ActionType,
        scope_key: str,
        scope_type: LimitScope
    ) -> None:
        """
        Record successful action (for adaptive learning)
        
        Args:
            action_type: Type of action that succeeded
            scope_key: Scope identifier
            scope_type: Type of scope
        """
        try:
            # Find applicable limits for adaptive adjustment
            applicable_limits = self._find_applicable_limits(action_type, scope_type)
            
            for rate_limit in applicable_limits:
                if rate_limit.algorithm == RateLimitAlgorithm.ADAPTIVE:
                    bucket_key = self._generate_bucket_key(rate_limit, scope_key)
                    bucket = await self._get_bucket(bucket_key)
                    
                    if bucket:
                        # Reset violation counters on successful action
                        bucket.consecutive_violations = 0
                        
                        # Gradually decrease limit if it was previously increased
                        if bucket.current_limit > rate_limit.base_limit:
                            new_limit = max(
                                rate_limit.base_limit,
                                int(bucket.current_limit * rate_limit.decrease_factor)
                            )
                            bucket.current_limit = new_limit
                            self.metrics.limits_decreased += 1
                        
                        await self._store_bucket(bucket)
            
        except Exception as e:
            self.logger.error(f"Record successful action error: {e}")
    
    async def get_rate_limit_status(
        self,
        scope_key: str,
        scope_type: LimitScope
    ) -> Dict[str, Any]:
        """
        Get current rate limit status for a scope
        
        Args:
            scope_key: Scope identifier
            scope_type: Type of scope
            
        Returns:
            Current status information
        """
        try:
            status = {
                "scope_key": scope_key,
                "scope_type": scope_type.value,
                "limits": {},
                "is_blocked": False,
                "is_suspended": False
            }
            
            # Check all rate limits for this scope
            for rate_limit in self.rate_limits.values():
                if rate_limit.scope == scope_type and rate_limit.enabled:
                    bucket_key = self._generate_bucket_key(rate_limit, scope_key)
                    bucket = await self._get_bucket(bucket_key)
                    
                    if bucket:
                        remaining = max(0, int(bucket.tokens))
                        reset_time = self._calculate_reset_time(rate_limit, bucket)
                        
                        limit_status = {
                            "limit_id": rate_limit.limit_id,
                            "action_type": rate_limit.action_type.value,
                            "algorithm": rate_limit.algorithm.value,
                            "max_requests": bucket.current_limit,
                            "remaining_requests": remaining,
                            "reset_time": reset_time.isoformat(),
                            "total_requests": bucket.total_requests,
                            "blocked_requests": bucket.blocked_requests,
                            "violation_count": bucket.violation_count,
                            "is_in_backoff": bucket.backoff_until and datetime.utcnow() < bucket.backoff_until
                        }
                        
                        status["limits"][rate_limit.limit_id] = limit_status
                        
                        # Check if blocked or suspended
                        if bucket.tokens <= 0:
                            if bucket.violation_count >= rate_limit.suspend_threshold:
                                status["is_suspended"] = True
                            else:
                                status["is_blocked"] = True
            
            return status
            
        except Exception as e:
            self.logger.error(f"Get rate limit status error: {e}")
            return {"error": str(e)}
    
    async def reset_rate_limit(
        self,
        scope_key: str,
        scope_type: LimitScope,
        limit_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Reset rate limits for a scope
        
        Args:
            scope_key: Scope identifier
            scope_type: Type of scope
            limit_id: Specific limit to reset (None for all)
            
        Returns:
            Reset operation result
        """
        try:
            reset_count = 0
            
            for rate_limit in self.rate_limits.values():
                if (rate_limit.scope == scope_type and 
                    (limit_id is None or rate_limit.limit_id == limit_id)):
                    
                    bucket_key = self._generate_bucket_key(rate_limit, scope_key)
                    bucket = await self._get_bucket(bucket_key)
                    
                    if bucket:
                        # Reset bucket to initial state
                        bucket.tokens = rate_limit.max_requests
                        bucket.violation_count = 0
                        bucket.consecutive_violations = 0
                        bucket.last_violation = None
                        bucket.current_delay = rate_limit.initial_delay
                        bucket.backoff_until = None
                        
                        if rate_limit.algorithm == RateLimitAlgorithm.ADAPTIVE:
                            bucket.current_limit = rate_limit.base_limit
                        
                        await self._store_bucket(bucket)
                        reset_count += 1
            
            self.logger.info(f"Reset {reset_count} rate limits for {scope_key}")
            
            return {
                "success": True,
                "reset_count": reset_count,
                "scope_key": scope_key,
                "scope_type": scope_type.value
            }
            
        except Exception as e:
            self.logger.error(f"Reset rate limit error: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def add_rate_limit(self, limit_config: Dict[str, Any]) -> str:
        """Add new rate limit configuration"""
        try:
            rate_limit = RateLimit(
                limit_id=limit_config["limit_id"],
                action_type=ActionType(limit_config["action_type"]),
                scope=LimitScope(limit_config["scope"]),
                algorithm=RateLimitAlgorithm(limit_config["algorithm"]),
                max_requests=limit_config["max_requests"],
                time_window_seconds=limit_config["time_window_seconds"],
                burst_allowance=limit_config.get("burst_allowance", 0),
                base_limit=limit_config.get("base_limit", limit_config["max_requests"]),
                max_limit=limit_config.get("max_limit", limit_config["max_requests"] * 2),
                increase_factor=limit_config.get("increase_factor", 1.5),
                decrease_factor=limit_config.get("decrease_factor", 0.9),
                initial_delay=limit_config.get("initial_delay", 1.0),
                max_delay=limit_config.get("max_delay", 300.0),
                backoff_factor=limit_config.get("backoff_factor", 2.0),
                warning_threshold=limit_config.get("warning_threshold", 0.8),
                block_threshold=limit_config.get("block_threshold", 1.0),
                suspend_threshold=limit_config.get("suspend_threshold", 10),
                enabled=limit_config.get("enabled", True),
                priority=limit_config.get("priority", 0),
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            
            self.rate_limits[rate_limit.limit_id] = rate_limit
            
            self.logger.info(f"Added rate limit: {rate_limit.limit_id}")
            
            return rate_limit.limit_id
            
        except Exception as e:
            self.logger.error(f"Add rate limit error: {e}")
            raise
    
    async def get_metrics(self) -> RateLimitMetrics:
        """Get current rate limiting metrics"""
        return self.metrics
    
    async def analyze_patterns(
        self,
        time_range: Optional[timedelta] = None
    ) -> Dict[str, Any]:
        """
        Analyze attack patterns and trends
        
        Args:
            time_range: Time range for analysis
            
        Returns:
            Pattern analysis results
        """
        try:
            if not time_range:
                time_range = timedelta(hours=24)
            
            cutoff_time = datetime.utcnow() - time_range
            
            # Filter recent requests
            recent_requests = [
                req for req in self.request_history
                if req["timestamp"] > cutoff_time
            ]
            
            if not recent_requests:
                return {"message": "No recent requests to analyze"}
            
            # Analyze patterns
            patterns = {
                "total_requests": len(recent_requests),
                "blocked_percentage": len([r for r in recent_requests if not r["allowed"]]) / len(recent_requests) * 100,
                "top_blocked_ips": self._analyze_top_blocked_ips(recent_requests),
                "attack_patterns": self._detect_attack_patterns(recent_requests),
                "temporal_patterns": self._analyze_temporal_patterns(recent_requests),
                "geographic_patterns": self._analyze_geographic_patterns(recent_requests)
            }
            
            return patterns
            
        except Exception as e:
            self.logger.error(f"Pattern analysis error: {e}")
            return {"error": str(e)}
    
    # Private methods
    
    def _load_config(self) -> Dict[str, Any]:
        """Load rate limiting configuration"""
        default_config = {
            "redis": {
                "enabled": True,
                "host": "localhost",
                "port": 6379,
                "db": 1,
                "password": None
            },
            "cleanup_interval_seconds": 3600,
            "adaptation_interval_seconds": 300,
            "bucket_cleanup_threshold": 10000,
            "enable_ml_adaptation": True,
            "suspicious_threshold": 0.8
        }
        
        try:
            if Path(self.config_path).exists():
                with open(self.config_path, 'r') as f:
                    config = json.load(f)
                return {**default_config, **config}
        except Exception as e:
            self.logger.warning(f"Config loading failed: {e}")
        
        return default_config
    
    def load_rate_limits(self):
        """Load rate limit configurations"""
        limits_config_path = Path(self.config_path).parent / "rate_limits.json"
        
        if not limits_config_path.exists():
            # Create default rate limits
            self._create_default_rate_limits()
            return
        
        try:
            with open(limits_config_path, 'r') as f:
                limits_config = json.load(f)
            
            for limit_config in limits_config["rate_limits"]:
                asyncio.create_task(self.add_rate_limit(limit_config))
                
        except Exception as e:
            self.logger.error(f"Rate limits loading error: {e}")
            self._create_default_rate_limits()
    
    def _create_default_rate_limits(self):
        """Create default rate limit configurations"""
        default_limits = [
            {
                "limit_id": "login_per_user",
                "action_type": "login_attempt",
                "scope": "user",
                "algorithm": "adaptive",
                "max_requests": 5,
                "time_window_seconds": 300,
                "base_limit": 5,
                "max_limit": 10,
                "increase_factor": 1.5,
                "decrease_factor": 0.9,
                "suspend_threshold": 10
            },
            {
                "limit_id": "login_per_ip",
                "action_type": "login_attempt",
                "scope": "ip_address",
                "algorithm": "sliding_window",
                "max_requests": 20,
                "time_window_seconds": 300,
                "suspend_threshold": 50
            },
            {
                "limit_id": "mfa_per_user",
                "action_type": "mfa_attempt",
                "scope": "user",
                "algorithm": "exponential_backoff",
                "max_requests": 3,
                "time_window_seconds": 60,
                "initial_delay": 5.0,
                "max_delay": 300.0,
                "backoff_factor": 2.0
            }
        ]
        
        for limit_config in default_limits:
            try:
                asyncio.create_task(self.add_rate_limit(limit_config))
            except Exception as e:
                self.logger.error(f"Default limit creation error: {e}")
    
    def _setup_redis_connection(self):
        """Setup Redis connection for distributed rate limiting"""
        if not self.config["redis"]["enabled"]:
            return
        
        try:
            redis_config = self.config["redis"]
            self.redis_client = redis.Redis(
                host=redis_config["host"],
                port=redis_config["port"],
                db=redis_config["db"],
                password=redis_config["password"],
                decode_responses=True
            )
            
            # Test connection
            self.redis_client.ping()
            self.logger.info("Redis connection established for rate limiting")
            
        except Exception as e:
            self.logger.warning(f"Redis connection failed: {e}")
            self.redis_client = None
    
    def _find_applicable_limits(
        self,
        action_type: ActionType,
        scope_type: LimitScope
    ) -> List[RateLimit]:
        """Find rate limits applicable to the action and scope"""
        applicable_limits = []
        
        for rate_limit in self.rate_limits.values():
            if (rate_limit.enabled and
                rate_limit.action_type == action_type and
                rate_limit.scope == scope_type):
                applicable_limits.append(rate_limit)
        
        # Sort by priority (higher priority first)
        applicable_limits.sort(key=lambda x: x.priority, reverse=True)
        
        return applicable_limits
    
    def _generate_bucket_key(self, rate_limit: RateLimit, scope_key: str) -> str:
        """Generate unique bucket key"""
        combined = f"{rate_limit.limit_id}:{scope_key}"
        return hashlib.md5(combined.encode()).hexdigest()
    
    async def _get_or_create_bucket(
        self,
        rate_limit: RateLimit,
        bucket_key: str,
        scope_key: str
    ) -> LimitBucket:
        """Get existing bucket or create new one"""
        bucket = await self._get_bucket(bucket_key)
        
        if bucket is None:
            # Create new bucket
            bucket = LimitBucket(
                bucket_id=bucket_key,
                scope_key=scope_key,
                algorithm=rate_limit.algorithm,
                tokens=rate_limit.max_requests,
                max_tokens=rate_limit.max_requests,
                refill_rate=rate_limit.max_requests / rate_limit.time_window_seconds,
                last_refill=datetime.utcnow(),
                total_requests=0,
                blocked_requests=0,
                last_request=datetime.utcnow(),
                current_limit=rate_limit.base_limit if rate_limit.algorithm == RateLimitAlgorithm.ADAPTIVE else rate_limit.max_requests,
                violation_count=0,
                consecutive_violations=0,
                last_violation=None,
                current_delay=rate_limit.initial_delay,
                backoff_until=None
            )
            
            await self._store_bucket(bucket)
        
        return bucket
    
    async def _get_bucket(self, bucket_key: str) -> Optional[LimitBucket]:
        """Get bucket from storage"""
        # Check local cache first
        if bucket_key in self.bucket_cache:
            cached_data = self.bucket_cache[bucket_key]
            if time.time() - cached_data["timestamp"] < self.cache_ttl:
                return cached_data["bucket"]
        
        # Try Redis if available
        if self.redis_client:
            try:
                bucket_data = self.redis_client.get(f"rate_limit_bucket:{bucket_key}")
                if bucket_data:
                    data = json.loads(bucket_data)
                    
                    # Convert datetime strings back
                    data["last_refill"] = datetime.fromisoformat(data["last_refill"])
                    data["last_request"] = datetime.fromisoformat(data["last_request"])
                    data["last_violation"] = datetime.fromisoformat(data["last_violation"]) if data["last_violation"] else None
                    data["backoff_until"] = datetime.fromisoformat(data["backoff_until"]) if data["backoff_until"] else None
                    
                    # Convert enum
                    data["algorithm"] = RateLimitAlgorithm(data["algorithm"])
                    
                    bucket = LimitBucket(**data)
                    
                    # Cache locally
                    self.bucket_cache[bucket_key] = {
                        "bucket": bucket,
                        "timestamp": time.time()
                    }
                    
                    return bucket
                    
            except Exception as e:
                self.logger.error(f"Redis bucket retrieval error: {e}")
        
        # Check local storage
        return self.buckets.get(bucket_key)
    
    async def _store_bucket(self, bucket: LimitBucket):
        """Store bucket in storage"""
        # Store locally
        self.buckets[bucket.bucket_id] = bucket
        
        # Cache locally
        self.bucket_cache[bucket.bucket_id] = {
            "bucket": bucket,
            "timestamp": time.time()
        }
        
        # Store in Redis if available
        if self.redis_client:
            try:
                bucket_data = asdict(bucket)
                
                # Convert datetime objects to strings
                bucket_data["last_refill"] = bucket.last_refill.isoformat()
                bucket_data["last_request"] = bucket.last_request.isoformat()
                bucket_data["last_violation"] = bucket.last_violation.isoformat() if bucket.last_violation else None
                bucket_data["backoff_until"] = bucket.backoff_until.isoformat() if bucket.backoff_until else None
                bucket_data["algorithm"] = bucket.algorithm.value
                
                # Store with expiration
                self.redis_client.setex(
                    f"rate_limit_bucket:{bucket.bucket_id}",
                    3600,  # 1 hour expiration
                    json.dumps(bucket_data)
                )
                
            except Exception as e:
                self.logger.error(f"Redis bucket storage error: {e}")
    
    async def _check_bucket_limit(
        self,
        rate_limit: RateLimit,
        bucket: LimitBucket,
        request_context: Optional[Dict[str, Any]]
    ) -> RateLimitResult:
        """Check if request exceeds bucket limit"""
        now = datetime.utcnow()
        
        # Check if in backoff period
        if bucket.backoff_until and now < bucket.backoff_until:
            retry_after = int((bucket.backoff_until - now).total_seconds())
            return RateLimitResult(
                status=LimitStatus.BLOCKED,
                allowed=False,
                remaining_requests=0,
                reset_time=bucket.backoff_until,
                retry_after=retry_after,
                limit_id=rate_limit.limit_id,
                scope_key=bucket.scope_key,
                algorithm=rate_limit.algorithm.value,
                violated_limits=[rate_limit.limit_id],
                current_limit=bucket.current_limit,
                violation_count=bucket.violation_count,
                headers=self._generate_headers(bucket, rate_limit, retry_after)
            )
        
        # Refill tokens based on algorithm
        await self._refill_bucket(rate_limit, bucket)
        
        # Check if request can be allowed
        if bucket.tokens >= 1.0:
            # Allow request
            bucket.tokens -= 1.0
            bucket.total_requests += 1
            bucket.last_request = now
            
            remaining = max(0, int(bucket.tokens))
            reset_time = self._calculate_reset_time(rate_limit, bucket)
            
            return RateLimitResult(
                status=LimitStatus.ALLOWED,
                allowed=True,
                remaining_requests=remaining,
                reset_time=reset_time,
                retry_after=None,
                limit_id=rate_limit.limit_id,
                scope_key=bucket.scope_key,
                algorithm=rate_limit.algorithm.value,
                violated_limits=[],
                current_limit=bucket.current_limit,
                violation_count=bucket.violation_count,
                headers=self._generate_headers(bucket, rate_limit)
            )
        else:
            # Rate limit exceeded
            bucket.violation_count += 1
            bucket.consecutive_violations += 1
            bucket.last_violation = now
            bucket.blocked_requests += 1
            
            # Determine status based on violation count
            if bucket.violation_count >= rate_limit.suspend_threshold:
                status = LimitStatus.SUSPENDED
            elif bucket.violation_count >= rate_limit.block_threshold:
                status = LimitStatus.BLOCKED
            else:
                status = LimitStatus.THROTTLED
            
            # Apply adaptive adjustments
            if rate_limit.algorithm == RateLimitAlgorithm.ADAPTIVE:
                await self._apply_adaptive_adjustment(rate_limit, bucket)
            
            # Apply exponential backoff
            if rate_limit.algorithm == RateLimitAlgorithm.EXPONENTIAL_BACKOFF:
                await self._apply_exponential_backoff(rate_limit, bucket)
            
            reset_time = self._calculate_reset_time(rate_limit, bucket)
            retry_after = int((reset_time - now).total_seconds())
            
            return RateLimitResult(
                status=status,
                allowed=False,
                remaining_requests=0,
                reset_time=reset_time,
                retry_after=retry_after,
                limit_id=rate_limit.limit_id,
                scope_key=bucket.scope_key,
                algorithm=rate_limit.algorithm.value,
                violated_limits=[rate_limit.limit_id],
                current_limit=bucket.current_limit,
                violation_count=bucket.violation_count,
                headers=self._generate_headers(bucket, rate_limit, retry_after)
            )
    
    async def _refill_bucket(self, rate_limit: RateLimit, bucket: LimitBucket):
        """Refill bucket tokens based on algorithm"""
        now = datetime.utcnow()
        time_passed = (now - bucket.last_refill).total_seconds()
        
        if rate_limit.algorithm in [RateLimitAlgorithm.TOKEN_BUCKET, RateLimitAlgorithm.ADAPTIVE]:
            # Token bucket refill
            tokens_to_add = bucket.refill_rate * time_passed
            bucket.tokens = min(bucket.max_tokens, bucket.tokens + tokens_to_add)
            bucket.last_refill = now
            
        elif rate_limit.algorithm == RateLimitAlgorithm.SLIDING_WINDOW:
            # Sliding window - reset tokens if window has passed
            if time_passed >= rate_limit.time_window_seconds:
                bucket.tokens = bucket.max_tokens
                bucket.last_refill = now
            
        elif rate_limit.algorithm == RateLimitAlgorithm.FIXED_WINDOW:
            # Fixed window - reset at fixed intervals
            window_start = bucket.last_refill.replace(second=0, microsecond=0)
            current_window = now.replace(second=0, microsecond=0)
            
            if current_window > window_start:
                bucket.tokens = bucket.max_tokens
                bucket.last_refill = now
    
    async def _apply_adaptive_adjustment(self, rate_limit: RateLimit, bucket: LimitBucket):
        """Apply adaptive adjustment to rate limit"""
        if bucket.consecutive_violations >= 3:
            # Increase limit (more restrictive)
            new_limit = min(
                rate_limit.max_limit,
                int(bucket.current_limit * rate_limit.increase_factor)
            )
            
            if new_limit != bucket.current_limit:
                bucket.current_limit = new_limit
                bucket.max_tokens = new_limit
                self.metrics.adaptations_count += 1
                self.metrics.limits_increased += 1
                
                self.logger.info(
                    f"Adaptive increase: {rate_limit.limit_id} limit increased to {new_limit} "
                    f"for {bucket.scope_key}"
                )
    
    async def _apply_exponential_backoff(self, rate_limit: RateLimit, bucket: LimitBucket):
        """Apply exponential backoff"""
        if bucket.consecutive_violations > 1:
            # Calculate new delay
            bucket.current_delay = min(
                rate_limit.max_delay,
                bucket.current_delay * rate_limit.backoff_factor
            )
            
            # Set backoff period
            bucket.backoff_until = datetime.utcnow() + timedelta(seconds=bucket.current_delay)
            
            self.logger.info(
                f"Exponential backoff: {rate_limit.limit_id} backoff {bucket.current_delay}s "
                f"for {bucket.scope_key}"
            )
    
    async def _update_bucket_state(
        self,
        rate_limit: RateLimit,
        bucket: LimitBucket,
        request_allowed: bool
    ):
        """Update bucket state after request"""
        if request_allowed:
            # Reset consecutive violations on successful request
            if bucket.consecutive_violations > 0:
                bucket.consecutive_violations = max(0, bucket.consecutive_violations - 1)
                
                # Reset backoff delay
                if rate_limit.algorithm == RateLimitAlgorithm.EXPONENTIAL_BACKOFF:
                    bucket.current_delay = rate_limit.initial_delay
        
        # Store updated bucket
        await self._store_bucket(bucket)
    
    def _calculate_reset_time(self, rate_limit: RateLimit, bucket: LimitBucket) -> datetime:
        """Calculate when the rate limit will reset"""
        if rate_limit.algorithm == RateLimitAlgorithm.FIXED_WINDOW:
            # Next minute boundary
            now = datetime.utcnow()
            return now.replace(second=0, microsecond=0) + timedelta(minutes=1)
        else:
            # Time until bucket is full
            if bucket.refill_rate > 0:
                tokens_needed = bucket.max_tokens - bucket.tokens
                seconds_to_fill = tokens_needed / bucket.refill_rate
                return datetime.utcnow() + timedelta(seconds=seconds_to_fill)
            else:
                return datetime.utcnow() + timedelta(seconds=rate_limit.time_window_seconds)
    
    def _generate_headers(
        self,
        bucket: LimitBucket,
        rate_limit: RateLimit,
        retry_after: Optional[int] = None
    ) -> Dict[str, str]:
        """Generate HTTP headers for rate limiting"""
        headers = {
            "X-RateLimit-Limit": str(bucket.current_limit),
            "X-RateLimit-Remaining": str(max(0, int(bucket.tokens))),
            "X-RateLimit-Reset": str(int(self._calculate_reset_time(rate_limit, bucket).timestamp()))
        }
        
        if retry_after:
            headers["Retry-After"] = str(retry_after)
        
        return headers
    
    def _create_allowed_result(self, scope_key: str, reason: str) -> RateLimitResult:
        """Create allowed result"""
        return RateLimitResult(
            status=LimitStatus.ALLOWED,
            allowed=True,
            remaining_requests=-1,  # Unknown
            reset_time=datetime.utcnow() + timedelta(hours=1),
            retry_after=None,
            limit_id=reason,
            scope_key=scope_key,
            algorithm="none",
            violated_limits=[],
            current_limit=-1,
            violation_count=0,
            headers={}
        )
    
    def _is_more_restrictive(self, result1: RateLimitResult, result2: RateLimitResult) -> bool:
        """Check if result1 is more restrictive than result2"""
        priority_order = {
            LimitStatus.SUSPENDED: 4,
            LimitStatus.BLOCKED: 3,
            LimitStatus.THROTTLED: 2,
            LimitStatus.ALLOWED: 1
        }
        
        return priority_order.get(result1.status, 0) > priority_order.get(result2.status, 0)
    
    def _update_metrics(
        self,
        action_type: ActionType,
        scope_type: LimitScope,
        result: RateLimitResult
    ):
        """Update metrics"""
        self.metrics.total_requests += 1
        
        if result.allowed:
            self.metrics.allowed_requests += 1
        else:
            if result.status == LimitStatus.THROTTLED:
                self.metrics.throttled_requests += 1
            else:
                self.metrics.blocked_requests += 1
            
            # Update scope-specific metrics
            scope_key = scope_type.value
            self.metrics.blocks_by_scope[scope_key] = self.metrics.blocks_by_scope.get(scope_key, 0) + 1
        
        # Update action-specific metrics
        action_key = action_type.value
        self.metrics.requests_by_action[action_key] = self.metrics.requests_by_action.get(action_key, 0) + 1
        
        if not result.allowed:
            self.metrics.blocks_by_action[action_key] = self.metrics.blocks_by_action.get(action_key, 0) + 1
    
    async def _track_request(
        self,
        action_type: ActionType,
        scope_key: str,
        scope_type: LimitScope,
        result: RateLimitResult,
        request_context: Optional[Dict[str, Any]]
    ):
        """Track request for pattern analysis"""
        request_record = {
            "timestamp": datetime.utcnow(),
            "action_type": action_type.value,
            "scope_key": scope_key,
            "scope_type": scope_type.value,
            "allowed": result.allowed,
            "status": result.status.value,
            "violation_count": result.violation_count,
            "context": request_context or {}
        }
        
        self.request_history.append(request_record)
    
    def _update_processing_time(self, processing_time: float):
        """Update average processing time metric"""
        if self.metrics.avg_processing_time == 0:
            self.metrics.avg_processing_time = processing_time
        else:
            # Exponential moving average
            alpha = 0.1
            self.metrics.avg_processing_time = (
                alpha * processing_time + 
                (1 - alpha) * self.metrics.avg_processing_time
            )
    
    def _start_background_tasks(self):
        """Start background cleanup and adaptation tasks"""
        async def cleanup_task():
            while True:
                try:
                    await asyncio.sleep(self.config["cleanup_interval_seconds"])
                    await self._cleanup_buckets()
                except Exception as e:
                    self.logger.error(f"Background cleanup error: {e}")
        
        async def adaptation_task():
            while True:
                try:
                    await asyncio.sleep(self.config["adaptation_interval_seconds"])
                    if self.config["enable_ml_adaptation"]:
                        await self._ml_adaptation()
                except Exception as e:
                    self.logger.error(f"Background adaptation error: {e}")
        
        self.cleanup_task = asyncio.create_task(cleanup_task())
        self.adaptation_task = asyncio.create_task(adaptation_task())
    
    async def _cleanup_buckets(self):
        """Clean up old buckets"""
        cutoff_time = datetime.utcnow() - timedelta(hours=24)
        cleaned_count = 0
        
        for bucket_id, bucket in list(self.buckets.items()):
            if bucket.last_request < cutoff_time:
                del self.buckets[bucket_id]
                cleaned_count += 1
        
        # Clean up local cache
        for bucket_id in list(self.bucket_cache.keys()):
            cached_data = self.bucket_cache[bucket_id]
            if time.time() - cached_data["timestamp"] > self.cache_ttl:
                del self.bucket_cache[bucket_id]
        
        if cleaned_count > 0:
            self.logger.info(f"Cleaned up {cleaned_count} old buckets")
    
    async def _ml_adaptation(self):
        """ML-based adaptation of rate limits"""
        try:
            # Analyze recent patterns
            recent_time = datetime.utcnow() - timedelta(hours=1)
            recent_requests = [
                req for req in self.request_history
                if req["timestamp"] > recent_time
            ]
            
            if len(recent_requests) < 10:
                return  # Not enough data
            
            # Detect suspicious patterns
            await self._detect_suspicious_patterns(recent_requests)
            
        except Exception as e:
            self.logger.error(f"ML adaptation error: {e}")
    
    async def _detect_suspicious_patterns(self, requests: List[Dict[str, Any]]):
        """Detect suspicious patterns using ML"""
        try:
            # Extract features for clustering
            features = []
            for req in requests:
                feature_vector = [
                    1 if not req["allowed"] else 0,  # Blocked request
                    req["violation_count"],
                    hash(req["scope_key"]) % 1000,  # Scope key hash
                    req["timestamp"].hour,  # Hour of day
                ]
                features.append(feature_vector)
            
            if len(features) < 5:
                return
            
            # Scale features
            X = self.scaler.fit_transform(features)
            
            # Perform clustering
            clusters = self.clustering_model.fit_predict(X)
            
            # Analyze clusters for suspicious patterns
            for cluster_id in set(clusters):
                if cluster_id == -1:  # Outliers
                    continue
                
                cluster_requests = [req for i, req in enumerate(requests) if clusters[i] == cluster_id]
                blocked_ratio = len([r for r in cluster_requests if not r["allowed"]]) / len(cluster_requests)
                
                if blocked_ratio > self.config["suspicious_threshold"]:
                    # Found suspicious cluster
                    scope_keys = list(set(req["scope_key"] for req in cluster_requests))
                    self.logger.warning(
                        f"Suspicious pattern detected: {len(cluster_requests)} requests, "
                        f"{blocked_ratio:.2%} blocked, scope keys: {scope_keys[:5]}"
                    )
                    
                    # Could trigger additional security measures here
        
        except Exception as e:
            self.logger.error(f"Suspicious pattern detection error: {e}")
    
    def _analyze_top_blocked_ips(self, requests: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Analyze top blocked IP addresses"""
        ip_blocks = defaultdict(int)
        
        for req in requests:
            if not req["allowed"] and req["scope_type"] == "ip_address":
                ip_blocks[req["scope_key"]] += 1
        
        # Sort by block count
        sorted_ips = sorted(ip_blocks.items(), key=lambda x: x[1], reverse=True)
        
        return [{"ip": ip, "blocks": count} for ip, count in sorted_ips[:10]]
    
    def _detect_attack_patterns(self, requests: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Detect attack patterns"""
        patterns = {
            "distributed_attack": False,
            "credential_stuffing": False,
            "brute_force": False
        }
        
        # Check for distributed attack (many IPs, few requests each)
        ip_counts = defaultdict(int)
        for req in requests:
            if req["scope_type"] == "ip_address":
                ip_counts[req["scope_key"]] += 1
        
        unique_ips = len(ip_counts)
        avg_requests_per_ip = len(requests) / max(1, unique_ips)
        
        if unique_ips > 50 and avg_requests_per_ip < 5:
            patterns["distributed_attack"] = True
        
        # Check for credential stuffing (high failure rate)
        login_requests = [r for r in requests if r["action_type"] == "login_attempt"]
        if login_requests:
            failure_rate = len([r for r in login_requests if not r["allowed"]]) / len(login_requests)
            if failure_rate > 0.8:
                patterns["credential_stuffing"] = True
        
        # Check for brute force (high violation counts)
        high_violation_requests = [r for r in requests if r["violation_count"] > 5]
        if len(high_violation_requests) > len(requests) * 0.3:
            patterns["brute_force"] = True
        
        return patterns
    
    def _analyze_temporal_patterns(self, requests: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze temporal patterns"""
        hourly_counts = defaultdict(int)
        
        for req in requests:
            hour = req["timestamp"].hour
            hourly_counts[hour] += 1
        
        # Find peak hours
        peak_hours = sorted(hourly_counts.items(), key=lambda x: x[1], reverse=True)[:3]
        
        return {
            "peak_hours": [{"hour": hour, "requests": count} for hour, count in peak_hours],
            "total_hours_active": len(hourly_counts)
        }
    
    def _analyze_geographic_patterns(self, requests: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze geographic patterns"""
        # This would integrate with GeoIP database
        # For now, return placeholder
        return {
            "unique_countries": 0,
            "top_countries": [],
            "suspicious_locations": []
        }


# Export main classes
__all__ = [
    "AuthenticationRateLimiter",
    "RateLimitAlgorithm",
    "LimitScope",
    "ActionType",
    "LimitStatus",
    "RateLimit",
    "LimitBucket",
    "RateLimitResult",
    "RateLimitMetrics"
]