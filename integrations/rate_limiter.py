"""Rate Limiter - Global Rate Limiting System
==========================================

Intelligent rate limiting system for all third-party integrations.
Provides configurable limits, adaptive throttling, and fair usage management.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import time
import logging
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import math
import json

import aioredis


class RateLimitStrategy(Enum):
    """Rate limiting strategies."""
    FIXED_WINDOW = "fixed_window"
    SLIDING_WINDOW = "sliding_window"
    TOKEN_BUCKET = "token_bucket"
    LEAKY_BUCKET = "leaky_bucket"
    ADAPTIVE = "adaptive"


class RateLimitScope(Enum):
    """Rate limit scope levels."""
    GLOBAL = "global"
    INTEGRATION = "integration"
    USER = "user"
    IP = "ip"
    API_KEY = "api_key"


@dataclass
class RateLimitConfig:
    """Rate limit configuration."""
    integration_name: str
    strategy: RateLimitStrategy = RateLimitStrategy.SLIDING_WINDOW
    requests_per_second: int = 10
    requests_per_minute: int = 600
    requests_per_hour: int = 10000
    requests_per_day: int = 100000
    burst_capacity: int = 100
    scope: RateLimitScope = RateLimitScope.INTEGRATION
    priority: int = 1  # 1-10, higher is more priority
    backoff_multiplier: float = 1.5
    max_retry_delay: int = 300  # seconds
    adaptive_threshold: float = 0.8  # Trigger adaptive at 80% capacity
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class RateLimitState:
    """Current rate limit state."""
    integration_name: str
    current_requests: int = 0
    window_start: datetime = field(default_factory=datetime.utcnow)
    tokens_available: int = 0
    last_refill: datetime = field(default_factory=datetime.utcnow)
    backoff_until: Optional[datetime] = None
    consecutive_failures: int = 0
    average_response_time: float = 0.0
    success_rate: float = 1.0


@dataclass
class RateLimitResult:
    """Rate limit check result."""
    allowed: bool
    remaining_requests: int
    reset_time: datetime
    retry_after: Optional[int] = None
    current_limit: int = 0
    strategy_used: str = ""
    backoff_active: bool = False


class RateLimiter:
    """Global rate limiting system for third-party integrations.
    
    Implements intelligent rate limiting with multiple strategies,
    adaptive throttling, and integration-specific configurations.
    """
    
    def __init__(self, redis_url: Optional[str] = None):
        """Initialize rate limiter with optional Redis backend."""
        self.logger = logging.getLogger(__name__)
        
        # Configuration storage
        self.configs: Dict[str, RateLimitConfig] = {}
        
        # In-memory state (fallback when Redis unavailable)
        self.local_state: Dict[str, RateLimitState] = {}
        
        # Redis client for distributed rate limiting
        self.redis_client: Optional[aioredis.Redis] = None
        self.redis_url = redis_url
        
        # Performance metrics
        self.metrics: Dict[str, Dict[str, Any]] = {}
        
        # Global emergency brake
        self.emergency_brake_active = False
        self.emergency_threshold = 0.95  # 95% failure rate triggers brake
        
        # Initialize default configurations
        self._initialize_default_configs()
    
    async def initialize(self) -> None:
        """Initialize rate limiter components."""
        if self.redis_url:
            try:
                self.redis_client = await aioredis.from_url(self.redis_url)
                await self.redis_client.ping()
                self.logger.info("Redis connection established for rate limiting")
            except Exception as e:
                self.logger.warning(f"Redis connection failed, using local state: {str(e)}")
        
        self.logger.info("Rate limiter initialized successfully")
    
    def _initialize_default_configs(self) -> None:
        """Initialize default rate limit configurations."""
        default_configs = [
            # High-priority social media platforms
            RateLimitConfig(
                integration_name="youtube",
                strategy=RateLimitStrategy.ADAPTIVE,
                requests_per_second=50,
                requests_per_minute=1000,
                requests_per_hour=50000,
                burst_capacity=200,
                priority=1
            ),
            RateLimitConfig(
                integration_name="instagram",
                strategy=RateLimitStrategy.SLIDING_WINDOW,
                requests_per_second=20,
                requests_per_minute=600,
                requests_per_hour=25000,
                burst_capacity=100,
                priority=1
            ),
            RateLimitConfig(
                integration_name="tiktok",
                strategy=RateLimitStrategy.TOKEN_BUCKET,
                requests_per_second=15,
                requests_per_minute=300,
                requests_per_hour=10000,
                burst_capacity=75,
                priority=1
            ),
            RateLimitConfig(
                integration_name="spotify",
                strategy=RateLimitStrategy.SLIDING_WINDOW,
                requests_per_second=30,
                requests_per_minute=1000,
                requests_per_hour=30000,
                burst_capacity=150,
                priority=1
            ),
            
            # AI services with special handling
            RateLimitConfig(
                integration_name="openai",
                strategy=RateLimitStrategy.ADAPTIVE,
                requests_per_second=5,
                requests_per_minute=200,
                requests_per_hour=5000,
                burst_capacity=20,
                priority=2,
                adaptive_threshold=0.7  # More conservative for AI
            ),
            RateLimitConfig(
                integration_name="anthropic",
                strategy=RateLimitStrategy.TOKEN_BUCKET,
                requests_per_second=3,
                requests_per_minute=100,
                requests_per_hour=2000,
                burst_capacity=15,
                priority=2
            ),
            
            # Payment gateways - critical priority
            RateLimitConfig(
                integration_name="stripe",
                strategy=RateLimitStrategy.SLIDING_WINDOW,
                requests_per_second=25,
                requests_per_minute=500,
                requests_per_hour=15000,
                burst_capacity=100,
                priority=1,
                adaptive_threshold=0.9  # Very conservative for payments
            ),
            RateLimitConfig(
                integration_name="paypal",
                strategy=RateLimitStrategy.FIXED_WINDOW,
                requests_per_second=10,
                requests_per_minute=300,
                requests_per_hour=10000,
                burst_capacity=50,
                priority=1
            ),
            
            # Cloud providers
            RateLimitConfig(
                integration_name="aws",
                strategy=RateLimitStrategy.ADAPTIVE,
                requests_per_second=100,
                requests_per_minute=5000,
                requests_per_hour=200000,
                burst_capacity=500,
                priority=2
            ),
            RateLimitConfig(
                integration_name="gcp",
                strategy=RateLimitStrategy.SLIDING_WINDOW,
                requests_per_second=80,
                requests_per_minute=4000,
                requests_per_hour=150000,
                burst_capacity=400,
                priority=2
            ),
        ]
        
        for config in default_configs:
            self.configs[config.integration_name] = config
    
    async def initialize_limiter(self, integration_name: str, custom_limit: Optional[int] = None) -> bool:
        """Initialize rate limiter for specific integration."""
        try:
            if integration_name not in self.configs:
                # Create default configuration
                self.configs[integration_name] = RateLimitConfig(
                    integration_name=integration_name,
                    requests_per_second=custom_limit or 10
                )
            
            # Initialize state
            await self._initialize_state(integration_name)
            
            # Initialize metrics
            self.metrics[integration_name] = {
                "total_requests": 0,
                "allowed_requests": 0,
                "denied_requests": 0,
                "average_response_time": 0.0,
                "success_rate": 1.0,
                "last_reset": datetime.utcnow()
            }
            
            self.logger.info(f"Rate limiter initialized for integration: {integration_name}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to initialize rate limiter for {integration_name}: {str(e)}")
            return False
    
    async def can_proceed(
        self,
        integration_name: str,
        scope_id: Optional[str] = None,
        priority_boost: int = 0
    ) -> bool:
        """Check if request can proceed based on rate limits."""
        try:
            # Check emergency brake
            if self.emergency_brake_active:
                return False
            
            # Get configuration
            if integration_name not in self.configs:
                await self.initialize_limiter(integration_name)
            
            config = self.configs[integration_name]
            
            # Check rate limit
            result = await self._check_rate_limit(integration_name, scope_id, priority_boost)
            
            # Update metrics
            await self._update_metrics(integration_name, result.allowed)
            
            return result.allowed
            
        except Exception as e:
            self.logger.error(f"Error checking rate limit for {integration_name}: {str(e)}")
            # Fail open for availability
            return True
    
    async def record_request(
        self,
        integration_name: str,
        success: bool,
        response_time: float,
        scope_id: Optional[str] = None
    ) -> None:
        """Record request completion for adaptive rate limiting."""
        try:
            # Update state
            state = await self._get_state(integration_name)
            
            # Update performance metrics
            if success:
                state.consecutive_failures = 0
                # Update average response time with exponential smoothing
                state.average_response_time = (
                    0.7 * state.average_response_time + 0.3 * response_time
                )
            else:
                state.consecutive_failures += 1
            
            # Update success rate (exponential moving average)
            new_success = 1.0 if success else 0.0
            state.success_rate = 0.9 * state.success_rate + 0.1 * new_success
            
            # Save state
            await self._save_state(integration_name, state)
            
            # Update global metrics
            if integration_name in self.metrics:
                metrics = self.metrics[integration_name]
                metrics["total_requests"] += 1
                
                if success:
                    metrics["allowed_requests"] += 1
                
                metrics["success_rate"] = state.success_rate
                metrics["average_response_time"] = state.average_response_time
            
            # Check for emergency brake activation
            await self._check_emergency_brake()
            
            # Adaptive limit adjustment
            if self.configs[integration_name].strategy == RateLimitStrategy.ADAPTIVE:
                await self._adjust_adaptive_limits(integration_name)
            
        except Exception as e:
            self.logger.error(f"Error recording request for {integration_name}: {str(e)}")
    
    async def set_custom_limit(
        self,
        integration_name: str,
        requests_per_second: int,
        requests_per_minute: Optional[int] = None,
        requests_per_hour: Optional[int] = None
    ) -> bool:
        """Set custom rate limits for integration."""
        try:
            if integration_name not in self.configs:
                await self.initialize_limiter(integration_name)
            
            config = self.configs[integration_name]
            config.requests_per_second = requests_per_second
            
            if requests_per_minute:
                config.requests_per_minute = requests_per_minute
            
            if requests_per_hour:
                config.requests_per_hour = requests_per_hour
            
            # Reset state to apply new limits
            await self._initialize_state(integration_name)
            
            self.logger.info(f"Custom rate limits set for {integration_name}: {requests_per_second}/s")
            return True
            
        except Exception as e:
            self.logger.error(f"Error setting custom limit for {integration_name}: {str(e)}")
            return False
    
    async def get_current_limits(self, integration_name: str) -> Optional[Dict[str, Any]]:
        """Get current rate limit status."""
        try:
            if integration_name not in self.configs:
                return None
            
            config = self.configs[integration_name]
            state = await self._get_state(integration_name)
            
            return {
                "integration_name": integration_name,
                "strategy": config.strategy.value,
                "limits": {
                    "requests_per_second": config.requests_per_second,
                    "requests_per_minute": config.requests_per_minute,
                    "requests_per_hour": config.requests_per_hour,
                    "burst_capacity": config.burst_capacity
                },
                "current_state": {
                    "current_requests": state.current_requests,
                    "tokens_available": state.tokens_available,
                    "backoff_active": state.backoff_until is not None and state.backoff_until > datetime.utcnow(),
                    "success_rate": round(state.success_rate, 3),
                    "average_response_time": round(state.average_response_time, 3),
                    "consecutive_failures": state.consecutive_failures
                },
                "metrics": self.metrics.get(integration_name, {}),
                "priority": config.priority
            }
            
        except Exception as e:
            self.logger.error(f"Error getting limits for {integration_name}: {str(e)}")
            return None
    
    async def reset_limits(self, integration_name: str) -> bool:
        """Reset rate limits for integration."""
        try:
            await self._initialize_state(integration_name)
            
            if integration_name in self.metrics:
                self.metrics[integration_name]["last_reset"] = datetime.utcnow()
            
            self.logger.info(f"Rate limits reset for integration: {integration_name}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error resetting limits for {integration_name}: {str(e)}")
            return False
    
    async def activate_emergency_brake(self, reason: str = "") -> None:
        """Activate emergency brake to stop all requests."""
        self.emergency_brake_active = True
        self.logger.critical(f"Emergency brake activated: {reason}")
    
    async def deactivate_emergency_brake(self) -> None:
        """Deactivate emergency brake."""
        self.emergency_brake_active = False
        self.logger.info("Emergency brake deactivated")
    
    async def get_global_statistics(self) -> Dict[str, Any]:
        """Get global rate limiting statistics."""
        total_requests = sum(m.get("total_requests", 0) for m in self.metrics.values())
        total_allowed = sum(m.get("allowed_requests", 0) for m in self.metrics.values())
        total_denied = sum(m.get("denied_requests", 0) for m in self.metrics.values())
        
        global_success_rate = (total_allowed / total_requests) if total_requests > 0 else 1.0
        
        return {
            "total_integrations": len(self.configs),
            "active_integrations": len(self.metrics),
            "global_statistics": {
                "total_requests": total_requests,
                "allowed_requests": total_allowed,
                "denied_requests": total_denied,
                "success_rate": round(global_success_rate, 3)
            },
            "emergency_brake_active": self.emergency_brake_active,
            "integrations": {
                name: self.metrics.get(name, {})
                for name in self.configs.keys()
            }
        }
    
    async def _check_rate_limit(
        self,
        integration_name: str,
        scope_id: Optional[str],
        priority_boost: int
    ) -> RateLimitResult:
        """Check rate limit using configured strategy."""
        config = self.configs[integration_name]
        state = await self._get_state(integration_name)
        
        # Check if in backoff period
        if state.backoff_until and state.backoff_until > datetime.utcnow():
            return RateLimitResult(
                allowed=False,
                remaining_requests=0,
                reset_time=state.backoff_until,
                retry_after=int((state.backoff_until - datetime.utcnow()).total_seconds()),
                backoff_active=True,
                strategy_used=config.strategy.value
            )
        
        # Apply strategy-specific logic
        if config.strategy == RateLimitStrategy.FIXED_WINDOW:
            return await self._check_fixed_window(config, state)
        elif config.strategy == RateLimitStrategy.SLIDING_WINDOW:
            return await self._check_sliding_window(config, state)
        elif config.strategy == RateLimitStrategy.TOKEN_BUCKET:
            return await self._check_token_bucket(config, state)
        elif config.strategy == RateLimitStrategy.LEAKY_BUCKET:
            return await self._check_leaky_bucket(config, state)
        elif config.strategy == RateLimitStrategy.ADAPTIVE:
            return await self._check_adaptive(config, state, priority_boost)
        
        # Default to sliding window
        return await self._check_sliding_window(config, state)
    
    async def _check_fixed_window(self, config: RateLimitConfig, state: RateLimitState) -> RateLimitResult:
        """Check fixed window rate limit."""
        current_time = datetime.utcnow()
        window_duration = timedelta(seconds=60)  # 1-minute windows
        
        # Reset window if expired
        if current_time - state.window_start >= window_duration:
            state.window_start = current_time
            state.current_requests = 0
        
        # Check limit
        allowed = state.current_requests < config.requests_per_minute
        
        if allowed:
            state.current_requests += 1
        
        reset_time = state.window_start + window_duration
        remaining = max(0, config.requests_per_minute - state.current_requests)
        
        await self._save_state(config.integration_name, state)
        
        return RateLimitResult(
            allowed=allowed,
            remaining_requests=remaining,
            reset_time=reset_time,
            current_limit=config.requests_per_minute,
            strategy_used="fixed_window"
        )
    
    async def _check_sliding_window(self, config: RateLimitConfig, state: RateLimitState) -> RateLimitResult:
        """Check sliding window rate limit."""
        current_time = datetime.utcnow()
        
        # For simplicity, implement as multiple fixed windows
        # Check per-second limit
        if hasattr(state, 'last_second') and current_time.second == state.last_second:
            if state.current_requests >= config.requests_per_second:
                return RateLimitResult(
                    allowed=False,
                    remaining_requests=0,
                    reset_time=current_time.replace(microsecond=0) + timedelta(seconds=1),
                    current_limit=config.requests_per_second,
                    strategy_used="sliding_window"
                )
        else:
            state.current_requests = 0
            state.last_second = current_time.second
        
        state.current_requests += 1
        remaining = max(0, config.requests_per_second - state.current_requests)
        
        await self._save_state(config.integration_name, state)
        
        return RateLimitResult(
            allowed=True,
            remaining_requests=remaining,
            reset_time=current_time.replace(microsecond=0) + timedelta(seconds=1),
            current_limit=config.requests_per_second,
            strategy_used="sliding_window"
        )
    
    async def _check_token_bucket(self, config: RateLimitConfig, state: RateLimitState) -> RateLimitResult:
        """Check token bucket rate limit."""
        current_time = datetime.utcnow()
        
        # Calculate tokens to add based on time elapsed
        time_elapsed = (current_time - state.last_refill).total_seconds()
        tokens_to_add = int(time_elapsed * config.requests_per_second)
        
        # Add tokens (up to burst capacity)
        state.tokens_available = min(
            config.burst_capacity,
            state.tokens_available + tokens_to_add
        )
        state.last_refill = current_time
        
        # Check if token available
        if state.tokens_available >= 1:
            state.tokens_available -= 1
            allowed = True
        else:
            allowed = False
        
        # Calculate when next token will be available
        next_token_time = current_time + timedelta(seconds=1/config.requests_per_second)
        
        await self._save_state(config.integration_name, state)
        
        return RateLimitResult(
            allowed=allowed,
            remaining_requests=state.tokens_available,
            reset_time=next_token_time if not allowed else current_time,
            current_limit=config.burst_capacity,
            strategy_used="token_bucket"
        )
    
    async def _check_leaky_bucket(self, config: RateLimitConfig, state: RateLimitState) -> RateLimitResult:
        """Check leaky bucket rate limit."""
        current_time = datetime.utcnow()
        
        # Calculate requests that have "leaked" out
        time_elapsed = (current_time - state.last_refill).total_seconds()
        leaked_requests = int(time_elapsed * config.requests_per_second)
        
        # Remove leaked requests
        state.current_requests = max(0, state.current_requests - leaked_requests)
        state.last_refill = current_time
        
        # Check if bucket has capacity
        if state.current_requests < config.burst_capacity:
            state.current_requests += 1
            allowed = True
        else:
            allowed = False
        
        remaining_capacity = max(0, config.burst_capacity - state.current_requests)
        
        await self._save_state(config.integration_name, state)
        
        return RateLimitResult(
            allowed=allowed,
            remaining_requests=remaining_capacity,
            reset_time=current_time + timedelta(seconds=1/config.requests_per_second),
            current_limit=config.burst_capacity,
            strategy_used="leaky_bucket"
        )
    
    async def _check_adaptive(
        self,
        config: RateLimitConfig,
        state: RateLimitState,
        priority_boost: int
    ) -> RateLimitResult:
        """Check adaptive rate limit based on performance metrics."""
        # Start with token bucket as base
        result = await self._check_token_bucket(config, state)
        
        # Adjust based on performance
        adjustment_factor = 1.0
        
        # Reduce limit if success rate is low
        if state.success_rate < config.adaptive_threshold:
            adjustment_factor *= state.success_rate
        
        # Reduce limit if response time is high
        if state.average_response_time > 5.0:  # 5 seconds threshold
            adjustment_factor *= 0.7
        
        # Increase limit for high priority
        effective_priority = config.priority + priority_boost
        if effective_priority <= 2:  # High priority
            adjustment_factor *= 1.2
        
        # Apply backoff for consecutive failures
        if state.consecutive_failures > 3:
            backoff_duration = min(
                config.max_retry_delay,
                int(config.backoff_multiplier ** state.consecutive_failures)
            )
            state.backoff_until = datetime.utcnow() + timedelta(seconds=backoff_duration)
            await self._save_state(config.integration_name, state)
            
            result.allowed = False
            result.backoff_active = True
            result.retry_after = backoff_duration
        
        # Adjust token availability
        adjusted_tokens = int(result.remaining_requests * adjustment_factor)
        result.remaining_requests = max(0, adjusted_tokens)
        
        if not result.allowed and adjustment_factor < 1.0:
            result.allowed = False
        
        result.strategy_used = "adaptive"
        
        return result
    
    async def _adjust_adaptive_limits(self, integration_name: str) -> None:
        """Dynamically adjust limits for adaptive strategy."""
        config = self.configs[integration_name]
        state = await self._get_state(integration_name)
        
        # Increase limits if performing well
        if state.success_rate > 0.95 and state.average_response_time < 2.0:
            config.requests_per_second = min(
                config.requests_per_second * 1.1,
                config.requests_per_second * 2  # Cap at 2x original
            )
        
        # Decrease limits if performing poorly
        elif state.success_rate < 0.8 or state.average_response_time > 10.0:
            config.requests_per_second = max(
                config.requests_per_second * 0.8,
                config.requests_per_second * 0.5  # Minimum 50% of original
            )
    
    async def _check_emergency_brake(self) -> None:
        """Check if emergency brake should be activated."""
        if self.emergency_brake_active:
            return
        
        # Calculate global failure rate
        total_requests = sum(m.get("total_requests", 0) for m in self.metrics.values())
        total_failures = sum(m.get("denied_requests", 0) for m in self.metrics.values())
        
        if total_requests > 100:  # Minimum sample size
            failure_rate = total_failures / total_requests
            
            if failure_rate > self.emergency_threshold:
                await self.activate_emergency_brake(f"High failure rate: {failure_rate:.2%}")
    
    async def _initialize_state(self, integration_name: str) -> None:
        """Initialize rate limit state for integration."""
        config = self.configs[integration_name]
        
        state = RateLimitState(
            integration_name=integration_name,
            tokens_available=config.burst_capacity,
            last_refill=datetime.utcnow(),
            window_start=datetime.utcnow()
        )
        
        await self._save_state(integration_name, state)
    
    async def _get_state(self, integration_name: str) -> RateLimitState:
        """Get current rate limit state."""
        if self.redis_client:
            try:
                state_data = await self.redis_client.get(f"rate_limit:{integration_name}")
                if state_data:
                    state_dict = json.loads(state_data)
                    return self._deserialize_state(state_dict)
            except Exception as e:
                self.logger.warning(f"Error reading Redis state for {integration_name}: {str(e)}")
        
        # Fallback to local state
        if integration_name not in self.local_state:
            await self._initialize_state(integration_name)
        
        return self.local_state[integration_name]
    
    async def _save_state(self, integration_name: str, state: RateLimitState) -> None:
        """Save rate limit state."""
        # Save to Redis if available
        if self.redis_client:
            try:
                state_data = json.dumps(self._serialize_state(state))
                await self.redis_client.setex(
                    f"rate_limit:{integration_name}",
                    300,  # 5 minutes TTL
                    state_data
                )
            except Exception as e:
                self.logger.warning(f"Error saving Redis state for {integration_name}: {str(e)}")
        
        # Always save to local state as backup
        self.local_state[integration_name] = state
    
    def _serialize_state(self, state: RateLimitState) -> Dict[str, Any]:
        """Serialize state for Redis storage."""
        return {
            "integration_name": state.integration_name,
            "current_requests": state.current_requests,
            "window_start": state.window_start.isoformat(),
            "tokens_available": state.tokens_available,
            "last_refill": state.last_refill.isoformat(),
            "backoff_until": state.backoff_until.isoformat() if state.backoff_until else None,
            "consecutive_failures": state.consecutive_failures,
            "average_response_time": state.average_response_time,
            "success_rate": state.success_rate
        }
    
    def _deserialize_state(self, data: Dict[str, Any]) -> RateLimitState:
        """Deserialize state from Redis storage."""
        return RateLimitState(
            integration_name=data["integration_name"],
            current_requests=data["current_requests"],
            window_start=datetime.fromisoformat(data["window_start"]),
            tokens_available=data["tokens_available"],
            last_refill=datetime.fromisoformat(data["last_refill"]),
            backoff_until=datetime.fromisoformat(data["backoff_until"]) if data["backoff_until"] else None,
            consecutive_failures=data["consecutive_failures"],
            average_response_time=data["average_response_time"],
            success_rate=data["success_rate"]
        )
    
    async def _update_metrics(self, integration_name: str, allowed: bool) -> None:
        """Update request metrics."""
        if integration_name not in self.metrics:
            return
        
        metrics = self.metrics[integration_name]
        metrics["total_requests"] += 1
        
        if allowed:
            metrics["allowed_requests"] += 1
        else:
            metrics["denied_requests"] += 1