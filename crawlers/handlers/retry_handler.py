"""Retry Handler Module
===================

Professional retry handling system with intelligent backoff strategies and failure management.
Provides enterprise-grade retry mechanisms for robust crawler operations and API interactions.

Retry Strategies Supported:
- Exponential Backoff with Jitter
- Linear Backoff
- Fixed Delay
- Custom Backoff Functions
- Circuit Breaker Pattern
- Adaptive Retry Based on Error Types

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: All rights reserved. Unauthorized use, reproduction, or distribution prohibited.

Project Team:
- Lead Dev IA: Fahed Mlaiel
- Backend Senior: Fahed Mlaiel
- ML Engineer: Fahed Mlaiel
- DBA: Fahed Mlaiel
- Security Expert: Fahed Mlaiel
- Microservices Architect: Fahed Mlaiel
- Audio Specialist: Fahed Mlaiel
- DevOps Engineer: Fahed Mlaiel
- IA Prompt Engineer: Fahed Mlaiel

WARNING: This code is protected intellectual property. Any attempt to steal, copy, or use 
without explicit written authorization from Fahed Mlaiel (mlaiel@live.de) will result 
in legal action under German law.
"""import asyncio
import logging
import json
import uuid
import time
import random
from typing import Dict, List, Optional, Any, Union, Callable, Coroutine, Type
from datetime import datetime, timedelta
from enum import Enum
from dataclasses import dataclass, asdict
from functools import wraps
import aiohttp
import aioredis
from contextlib import asynccontextmanager

from backend.core.exceptions import (
    RetryError,
    CircuitBreakerError,
    MaxRetriesExceededError,
    RetryConfigurationError
)
from backend.core.logging import get_logger
from backend.core.config import settings
from backend.database.models import RetryLog, User
from backend.database.session import async_session
from backend.utils.metrics_utils import MetricsCollector
from backend.utils.redis_client import get_redis_client

logger = get_logger(__name__)


class RetryStrategy(Enum):
    """Retry strategy types."""    EXPONENTIAL_BACKOFF = "exponential_backoff"
    LINEAR_BACKOFF = "linear_backoff"
    FIXED_DELAY = "fixed_delay"
    CUSTOM = "custom"


class CircuitBreakerState(Enum):
    """Circuit breaker states."""    CLOSED = "closed"      # Normal operation
    OPEN = "open"          # Failing, rejecting requests
    HALF_OPEN = "half_open"  # Testing if service recovered


@dataclass
class RetryConfig:
    """Retry configuration settings."""    
    max_attempts: int = 3
    strategy: RetryStrategy = RetryStrategy.EXPONENTIAL_BACKOFF
    base_delay: float = 1.0  # seconds
    max_delay: float = 300.0  # 5 minutes
    multiplier: float = 2.0
    jitter: bool = True
    jitter_max: float = 0.1  # 10% jitter
    stop_on_exceptions: List[Type[Exception]] = None
    retry_on_exceptions: List[Type[Exception]] = None
    backoff_function: Optional[Callable[[int, float], float]] = None
    timeout_per_attempt: Optional[float] = None
    
    def __post_init__(self):
        if self.stop_on_exceptions is None:
            self.stop_on_exceptions = []
        if self.retry_on_exceptions is None:
            self.retry_on_exceptions = []


@dataclass
class RetryAttempt:
    """Information about a retry attempt."""    
    attempt_number: int
    timestamp: datetime
    delay_before: float
    exception: Optional[Exception] = None
    success: bool = False
    duration: float = 0.0
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


@dataclass
class RetryResult:
    """Result of retry operation."""    
    success: bool
    result: Any = None
    total_attempts: int = 0
    total_duration: float = 0.0
    attempts: List[RetryAttempt] = None
    final_exception: Optional[Exception] = None
    
    def __post_init__(self):
        if self.attempts is None:
            self.attempts = []


class CircuitBreaker:
    """Circuit breaker pattern implementation for resilient operations."""    
    def __init__(
        self,
        failure_threshold: int = 5,
        recovery_timeout: float = 60.0,
        expected_exception: Type[Exception] = Exception,
        name: Optional[str] = None
    ):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.expected_exception = expected_exception
        self.name = name or str(uuid.uuid4())
        
        self._failure_count = 0
        self._last_failure_time = None
        self._state = CircuitBreakerState.CLOSED
        self._lock = asyncio.Lock()
    
    @property
    def state(self) -> CircuitBreakerState:
        """Get current circuit breaker state."""        return self._state
    
    @property
    def failure_count(self) -> int:
        """Get current failure count."""        return self._failure_count
    
    async def __aenter__(self):
        """Async context manager entry."""        await self._check_state()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""        if exc_type is None:
            await self._on_success()
        elif issubclass(exc_type, self.expected_exception):
            await self._on_failure()
    
    async def _check_state(self):
        """Check and update circuit breaker state."""        async with self._lock:
            now = time.time()
            
            if self._state == CircuitBreakerState.OPEN:
                if (self._last_failure_time and 
                    now - self._last_failure_time >= self.recovery_timeout):
                    self._state = CircuitBreakerState.HALF_OPEN
                    logger.info(f"Circuit breaker {self.name} moved to HALF_OPEN")
                else:
                    raise CircuitBreakerError(
                        f"Circuit breaker {self.name} is OPEN. "
                        f"Retry in {self.recovery_timeout - (now - self._last_failure_time):.1f}s"
                    )
    
    async def _on_success(self):
        """Handle successful operation."""        async with self._lock:
            self._failure_count = 0
            if self._state == CircuitBreakerState.HALF_OPEN:
                self._state = CircuitBreakerState.CLOSED
                logger.info(f"Circuit breaker {self.name} recovered to CLOSED")
    
    async def _on_failure(self):
        """Handle failed operation."""        async with self._lock:
            self._failure_count += 1
            self._last_failure_time = time.time()
            
            if (self._state == CircuitBreakerState.CLOSED and 
                self._failure_count >= self.failure_threshold):
                self._state = CircuitBreakerState.OPEN
                logger.warning(
                    f"Circuit breaker {self.name} tripped to OPEN "
                    f"after {self._failure_count} failures"
                )
            elif self._state == CircuitBreakerState.HALF_OPEN:
                self._state = CircuitBreakerState.OPEN
                logger.warning(f"Circuit breaker {self.name} returned to OPEN")


class BackoffCalculator:
    """Calculate backoff delays for different retry strategies."""    
    @staticmethod
    def exponential_backoff(
        attempt: int, 
        base_delay: float, 
        multiplier: float = 2.0,
        max_delay: float = 300.0,
        jitter: bool = True,
        jitter_max: float = 0.1
    ) -> float:
        """Calculate exponential backoff delay."""        delay = base_delay * (multiplier ** (attempt - 1))
        delay = min(delay, max_delay)
        
        if jitter:
            jitter_amount = delay * random.uniform(0, jitter_max)
            delay += jitter_amount
        
        return delay
    
    @staticmethod
    def linear_backoff(
        attempt: int,
        base_delay: float,
        increment: float = 1.0,
        max_delay: float = 300.0,
        jitter: bool = True,
        jitter_max: float = 0.1
    ) -> float:
        """Calculate linear backoff delay."""        delay = base_delay + (increment * (attempt - 1))
        delay = min(delay, max_delay)
        
        if jitter:
            jitter_amount = delay * random.uniform(0, jitter_max)
            delay += jitter_amount
        
        return delay
    
    @staticmethod
    def fixed_delay(
        attempt: int,
        base_delay: float,
        jitter: bool = True,
        jitter_max: float = 0.1
    ) -> float:
        """Calculate fixed delay."""        delay = base_delay
        
        if jitter:
            jitter_amount = delay * random.uniform(0, jitter_max)
            delay += jitter_amount
        
        return delay


class RetryPolicyManager:
    """Manage retry policies for different operation types."""    
    def __init__(self):
        self.policies = self._load_default_policies()
    
    def _load_default_policies(self) -> Dict[str, RetryConfig]:
        """Load default retry policies."""        return {
            'api_request': RetryConfig(
                max_attempts=3,
                strategy=RetryStrategy.EXPONENTIAL_BACKOFF,
                base_delay=1.0,
                max_delay=60.0,
                multiplier=2.0,
                jitter=True,
                stop_on_exceptions=[
                    aiohttp.ClientResponseError  # For 4xx errors
                ]
            ),
            'database_operation': RetryConfig(
                max_attempts=3,
                strategy=RetryStrategy.EXPONENTIAL_BACKOFF,
                base_delay=0.5,
                max_delay=10.0,
                multiplier=2.0,
                jitter=False
            ),
            'file_operation': RetryConfig(
                max_attempts=2,
                strategy=RetryStrategy.FIXED_DELAY,
                base_delay=1.0,
                jitter=True
            ),
            'network_request': RetryConfig(
                max_attempts=5,
                strategy=RetryStrategy.EXPONENTIAL_BACKOFF,
                base_delay=2.0,
                max_delay=120.0,
                multiplier=2.0,
                jitter=True,
                timeout_per_attempt=30.0
            ),
            'content_processing': RetryConfig(
                max_attempts=2,
                strategy=RetryStrategy.LINEAR_BACKOFF,
                base_delay=2.0,
                max_delay=30.0,
                jitter=True
            ),
            'rate_limited_api': RetryConfig(
                max_attempts=5,
                strategy=RetryStrategy.EXPONENTIAL_BACKOFF,
                base_delay=60.0,  # Start with 1 minute for rate limits
                max_delay=600.0,  # Max 10 minutes
                multiplier=1.5,
                jitter=True
            )
        }
    
    def get_policy(self, operation_type: str) -> RetryConfig:
        """Get retry policy for operation type."""        return self.policies.get(operation_type, self.policies['api_request'])
    
    def register_policy(self, operation_type: str, config: RetryConfig):
        """Register custom retry policy."""        self.policies[operation_type] = config


class AdaptiveRetryManager:
    """Adaptive retry manager that learns from failures."""    
    def __init__(self, redis_client: aioredis.Redis):
        self.redis = redis_client
        self.stats_key_prefix = "retry_stats:"
        self.learning_window = timedelta(hours=1)
    
    async def get_adaptive_config(
        self, 
        operation_type: str, 
        base_config: RetryConfig
    ) -> RetryConfig:
        """Get adaptive retry configuration based on recent failures."""        try:
            stats_key = f"{self.stats_key_prefix}{operation_type}"
            stats_data = await self.redis.hgetall(stats_key)
            
            if not stats_data:
                return base_config
            
            # Decode stats
            stats = {k.decode(): float(v.decode()) for k, v in stats_data.items()}
            
            success_rate = stats.get('success_rate', 1.0)
            avg_attempts = stats.get('avg_attempts', 1.0)
            
            # Adapt configuration based on recent performance
            adapted_config = RetryConfig(
                max_attempts=base_config.max_attempts,
                strategy=base_config.strategy,
                base_delay=base_config.base_delay,
                max_delay=base_config.max_delay,
                multiplier=base_config.multiplier,
                jitter=base_config.jitter,
                jitter_max=base_config.jitter_max,
                stop_on_exceptions=base_config.stop_on_exceptions,
                retry_on_exceptions=base_config.retry_on_exceptions
            )
            
            # Increase max attempts if success rate is low
            if success_rate < 0.7:
                adapted_config.max_attempts = min(
                    base_config.max_attempts + 2, 
                    10
                )
            
            # Increase base delay if requiring many attempts
            if avg_attempts > 2.0:
                adapted_config.base_delay = min(
                    base_config.base_delay * 1.5,
                    30.0
                )
            
            return adapted_config
            
        except Exception as e:
            logger.warning(f"Adaptive config generation failed: {e}")
            return base_config
    
    async def record_retry_result(self, operation_type: str, result: RetryResult):
        """Record retry result for adaptive learning."""        try:
            stats_key = f"{self.stats_key_prefix}{operation_type}"
            
            # Update statistics
            pipe = self.redis.pipeline()
            pipe.hincrby(stats_key, 'total_operations', 1)
            
            if result.success:
                pipe.hincrby(stats_key, 'successful_operations', 1)
            
            pipe.hincrby(stats_key, 'total_attempts', result.total_attempts)
            pipe.hincrbyfloat(stats_key, 'total_duration', result.total_duration)
            
            # Set expiration to maintain sliding window
            pipe.expire(stats_key, int(self.learning_window.total_seconds()))
            
            await pipe.execute()
            
            # Calculate and update derived metrics
            await self._update_derived_metrics(stats_key)
            
        except Exception as e:
            logger.warning(f"Retry result recording failed: {e}")
    
    async def _update_derived_metrics(self, stats_key: str):
        """Update derived metrics like success rate and average attempts."""        try:
            stats_data = await self.redis.hgetall(stats_key)
            
            if not stats_data:
                return
            
            stats = {k.decode(): float(v.decode()) for k, v in stats_data.items()}
            
            total_ops = stats.get('total_operations', 0)
            successful_ops = stats.get('successful_operations', 0)
            total_attempts = stats.get('total_attempts', 0)
            total_duration = stats.get('total_duration', 0)
            
            if total_ops > 0:
                success_rate = successful_ops / total_ops
                avg_attempts = total_attempts / total_ops
                avg_duration = total_duration / total_ops
                
                pipe = self.redis.pipeline()
                pipe.hset(stats_key, 'success_rate', success_rate)
                pipe.hset(stats_key, 'avg_attempts', avg_attempts)
                pipe.hset(stats_key, 'avg_duration', avg_duration)
                await pipe.execute()
                
        except Exception as e:
            logger.warning(f"Derived metrics update failed: {e}")


class RetryExecutor:
    """Execute operations with retry logic."""    
    def __init__(
        self,
        policy_manager: RetryPolicyManager,
        adaptive_manager: Optional[AdaptiveRetryManager] = None,
        metrics_collector: Optional[MetricsCollector] = None
    ):
        self.policy_manager = policy_manager
        self.adaptive_manager = adaptive_manager
        self.metrics_collector = metrics_collector
        self.circuit_breakers: Dict[str, CircuitBreaker] = {}
    
    async def execute_with_retry(
        self,
        operation: Callable[[], Coroutine[Any, Any, Any]],
        operation_type: str = 'api_request',
        config: Optional[RetryConfig] = None,
        circuit_breaker_name: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> RetryResult:
        """        Execute operation with retry logic.
        
        Args:
            operation: Async operation to execute
            operation_type: Type of operation for policy selection
            config: Override retry configuration
            circuit_breaker_name: Circuit breaker to use
            context: Additional context for logging
            
        Returns:
            RetryResult with execution details
        """        start_time = time.time()
        attempts = []
        
        try:
            # Get retry configuration
            if config is None:
                base_config = self.policy_manager.get_policy(operation_type)
                if self.adaptive_manager:
                    config = await self.adaptive_manager.get_adaptive_config(
                        operation_type, base_config
                    )
                else:
                    config = base_config
            
            # Get circuit breaker if specified
            circuit_breaker = None
            if circuit_breaker_name:
                circuit_breaker = self._get_circuit_breaker(circuit_breaker_name)
            
            # Execute with retries
            for attempt in range(1, config.max_attempts + 1):
                attempt_start = time.time()
                delay_before = 0.0
                
                # Calculate delay before attempt (except first)
                if attempt > 1:
                    delay_before = self._calculate_delay(config, attempt - 1)
                    logger.debug(f"Waiting {delay_before:.2f}s before attempt {attempt}")
                    await asyncio.sleep(delay_before)
                
                try:
                    # Use circuit breaker if available
                    if circuit_breaker:
                        async with circuit_breaker:
                            if config.timeout_per_attempt:
                                result = await asyncio.wait_for(
                                    operation(), 
                                    timeout=config.timeout_per_attempt
                                )
                            else:
                                result = await operation()
                    else:
                        if config.timeout_per_attempt:
                            result = await asyncio.wait_for(
                                operation(), 
                                timeout=config.timeout_per_attempt
                            )
                        else:
                            result = await operation()
                    
                    # Success!
                    attempt_duration = time.time() - attempt_start
                    attempts.append(RetryAttempt(
                        attempt_number=attempt,
                        timestamp=datetime.utcnow(),
                        delay_before=delay_before,
                        success=True,
                        duration=attempt_duration,
                        metadata=context or {}
                    ))
                    
                    total_duration = time.time() - start_time
                    
                    result_obj = RetryResult(
                        success=True,
                        result=result,
                        total_attempts=attempt,
                        total_duration=total_duration,
                        attempts=attempts
                    )
                    
                    # Record success for adaptive learning
                    if self.adaptive_manager:
                        await self.adaptive_manager.record_retry_result(
                            operation_type, result_obj
                        )
                    
                    # Update metrics
                    if self.metrics_collector:
                        await self.metrics_collector.record_retry_success(
                            operation_type, attempt, total_duration
                        )
                    
                    logger.info(
                        f"Operation succeeded on attempt {attempt}/{config.max_attempts} "
                        f"after {total_duration:.2f}s"
                    )
                    
                    return result_obj
                
                except Exception as e:
                    attempt_duration = time.time() - attempt_start
                    
                    # Check if should stop retrying
                    if self._should_stop_retry(e, config):
                        attempts.append(RetryAttempt(
                            attempt_number=attempt,
                            timestamp=datetime.utcnow(),
                            delay_before=delay_before,
                            exception=e,
                            success=False,
                            duration=attempt_duration,
                            metadata=context or {}
                        ))
                        break
                    
                    # Record failed attempt
                    attempts.append(RetryAttempt(
                        attempt_number=attempt,
                        timestamp=datetime.utcnow(),
                        delay_before=delay_before,
                        exception=e,
                        success=False,
                        duration=attempt_duration,
                        metadata=context or {}
                    ))
                    
                    logger.warning(
                        f"Attempt {attempt}/{config.max_attempts} failed: "
                        f"{type(e).__name__}: {e}"
                    )
                    
                    # If this was the last attempt, break
                    if attempt >= config.max_attempts:
                        break
            
            # All attempts failed
            total_duration = time.time() - start_time
            final_exception = attempts[-1].exception if attempts else None
            
            result_obj = RetryResult(
                success=False,
                total_attempts=len(attempts),
                total_duration=total_duration,
                attempts=attempts,
                final_exception=final_exception
            )
            
            # Record failure for adaptive learning
            if self.adaptive_manager:
                await self.adaptive_manager.record_retry_result(
                    operation_type, result_obj
                )
            
            # Update metrics
            if self.metrics_collector:
                await self.metrics_collector.record_retry_failure(
                    operation_type, len(attempts), total_duration
                )
            
            logger.error(
                f"Operation failed after {len(attempts)} attempts "
                f"over {total_duration:.2f}s"
            )
            
            return result_obj
            
        except Exception as e:
            logger.error(f"Retry execution system error: {e}")
            return RetryResult(
                success=False,
                total_attempts=0,
                total_duration=time.time() - start_time,
                final_exception=e
            )
    
    def _calculate_delay(self, config: RetryConfig, attempt: int) -> float:
        """Calculate delay before retry attempt."""        if config.backoff_function:
            return config.backoff_function(attempt, config.base_delay)
        
        if config.strategy == RetryStrategy.EXPONENTIAL_BACKOFF:
            return BackoffCalculator.exponential_backoff(
                attempt, config.base_delay, config.multiplier,
                config.max_delay, config.jitter, config.jitter_max
            )
        elif config.strategy == RetryStrategy.LINEAR_BACKOFF:
            return BackoffCalculator.linear_backoff(
                attempt, config.base_delay, config.multiplier,
                config.max_delay, config.jitter, config.jitter_max
            )
        elif config.strategy == RetryStrategy.FIXED_DELAY:
            return BackoffCalculator.fixed_delay(
                attempt, config.base_delay, config.jitter, config.jitter_max
            )
        else:
            return config.base_delay
    
    def _should_stop_retry(self, exception: Exception, config: RetryConfig) -> bool:
        """Determine if retrying should stop based on exception."""        # Check stop conditions
        for stop_exception in config.stop_on_exceptions:
            if isinstance(exception, stop_exception):
                # Additional logic for HTTP errors
                if isinstance(exception, aiohttp.ClientResponseError):
                    # Don't retry on 4xx client errors (except 429)
                    if 400 <= exception.status < 500 and exception.status != 429:
                        return True
                return True
        
        # Check retry conditions (if specified, only retry on these)
        if config.retry_on_exceptions:
            for retry_exception in config.retry_on_exceptions:
                if isinstance(exception, retry_exception):
                    return False
            return True  # Not in retry list, so stop
        
        return False  # Continue retrying
    
    def _get_circuit_breaker(self, name: str) -> CircuitBreaker:
        """Get or create circuit breaker."""        if name not in self.circuit_breakers:
            self.circuit_breakers[name] = CircuitBreaker(
                name=name,
                failure_threshold=5,
                recovery_timeout=60.0
            )
        return self.circuit_breakers[name]


class RetryHandler:
    """Main retry handler orchestrating all retry operations."""    
    def __init__(
        self,
        redis_client: Optional[aioredis.Redis] = None,
        metrics_collector: Optional[MetricsCollector] = None
    ):
        self.policy_manager = RetryPolicyManager()
        self.adaptive_manager = None
        self.metrics_collector = metrics_collector
        
        if redis_client:
            self.adaptive_manager = AdaptiveRetryManager(redis_client)
        
        self.executor = RetryExecutor(
            self.policy_manager,
            self.adaptive_manager,
            self.metrics_collector
        )
        
        logger.info("Retry Handler initialized successfully")
    
    async def retry_operation(
        self,
        operation: Callable[[], Coroutine[Any, Any, Any]],
        operation_type: str = 'api_request',
        config: Optional[RetryConfig] = None,
        circuit_breaker_name: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> Any:
        """        Retry operation and return result or raise exception.
        
        Args:
            operation: Async operation to execute
            operation_type: Type of operation for policy selection
            config: Override retry configuration
            circuit_breaker_name: Circuit breaker to use
            context: Additional context for logging
            
        Returns:
            Operation result
            
        Raises:
            MaxRetriesExceededError: If all retries failed
        """        result = await self.executor.execute_with_retry(
            operation, operation_type, config, circuit_breaker_name, context
        )
        
        if result.success:
            return result.result
        else:
            raise MaxRetriesExceededError(
                f"Operation failed after {result.total_attempts} attempts",
                attempts=result.attempts,
                final_exception=result.final_exception
            )
    
    def retry_decorator(
        self,
        operation_type: str = 'api_request',
        config: Optional[RetryConfig] = None,
        circuit_breaker_name: Optional[str] = None
    ):
        """Decorator for automatic retry handling."""        def decorator(func: Callable):
            @wraps(func)
            async def wrapper(*args, **kwargs):
                async def operation():
                    return await func(*args, **kwargs)
                
                return await self.retry_operation(
                    operation, operation_type, config, circuit_breaker_name
                )
            
            return wrapper
        return decorator
    
    def register_policy(self, operation_type: str, config: RetryConfig):
        """Register custom retry policy."""        self.policy_manager.register_policy(operation_type, config)
    
    async def get_retry_statistics(self) -> Dict[str, Any]:
        """Get retry statistics for monitoring."""        try:
            stats = {}
            
            if self.adaptive_manager:
                # Get adaptive statistics from Redis
                pattern = f"{self.adaptive_manager.stats_key_prefix}*"
                keys = await self.adaptive_manager.redis.keys(pattern)
                
                for key in keys:
                    operation_type = key.decode().replace(
                        self.adaptive_manager.stats_key_prefix, ''
                    )
                    stats_data = await self.adaptive_manager.redis.hgetall(key)
                    
                    if stats_data:
                        stats[operation_type] = {
                            k.decode(): float(v.decode()) 
                            for k, v in stats_data.items()
                        }
            
            return {
                'policies': list(self.policy_manager.policies.keys()),
                'circuit_breakers': {
                    name: {
                        'state': cb.state.value,
                        'failure_count': cb.failure_count
                    }
                    for name, cb in self.executor.circuit_breakers.items()
                },
                'adaptive_stats': stats
            }
            
        except Exception as e:
            logger.error(f"Retry statistics collection failed: {e}")
            return {}


# Utility functions
def create_retry_config(
    max_attempts: int = 3,
    strategy: RetryStrategy = RetryStrategy.EXPONENTIAL_BACKOFF,
    base_delay: float = 1.0,
    **kwargs
) -> RetryConfig:
    """Create retry configuration with specified parameters."""    return RetryConfig(
        max_attempts=max_attempts,
        strategy=strategy,
        base_delay=base_delay,
        **kwargs
    )


# Factory function
async def create_retry_handler(
    redis_client: Optional[aioredis.Redis] = None,
    metrics_collector: Optional[MetricsCollector] = None
) -> RetryHandler:
    """Create and return a RetryHandler instance."""    if redis_client is None:
        redis_client = await get_redis_client()
    
    return RetryHandler(
        redis_client=redis_client,
        metrics_collector=metrics_collector
    )
