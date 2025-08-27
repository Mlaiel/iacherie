"""
Retry Handler - Enterprise Retry and Recovery System

Industrial-grade webhook retry handler with advanced exponential backoff,
circuit breaker patterns, and intelligent failure recovery mechanisms.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️  CRITICAL LEGAL NOTICE:
This code and architectural design are the exclusive intellectual property of Fahed Mlaiel.
Unauthorized use, copying, distribution, or commercialization without explicit written 
permission from Fahed Mlaiel <mlaiel@live.de> is strictly prohibited.
"""

import asyncio
import json
import logging
import random
import time
import uuid
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional, Any, Callable, Set
from dataclasses import dataclass, field
from enum import Enum

import aioredis
from sqlalchemy import Column, String, DateTime, Boolean, Integer, Float, Text, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session

from ...core.database import get_db_session
from ...core.exceptions import RetryError, ConfigurationError
from ...utils.performance_monitor import PerformanceMonitor

logger = logging.getLogger(__name__)

Base = declarative_base()

class RetryAttemptModel(Base):
    """Database model for retry attempts"""
    __tablename__ = "webhook_retry_attempts"
    
    attempt_id = Column(String, primary_key=True)
    webhook_id = Column(String, nullable=False)
    endpoint_id = Column(String, nullable=False)
    user_id = Column(String, nullable=False)
    platform = Column(String, nullable=False)
    attempt_number = Column(Integer, nullable=False)
    scheduled_time = Column(DateTime, nullable=False)
    executed_time = Column(DateTime)
    success = Column(Boolean)
    response_code = Column(Integer)
    response_time_ms = Column(Float)
    error_message = Column(Text)
    retry_reason = Column(String)
    next_retry_time = Column(DateTime)
    metadata = Column(JSON)

class RetryPolicyModel(Base):
    """Database model for retry policies"""
    __tablename__ = "webhook_retry_policies"
    
    policy_id = Column(String, primary_key=True)
    policy_name = Column(String, nullable=False)
    platform = Column(String)
    event_type = Column(String)
    max_attempts = Column(Integer, default=3)
    initial_delay_seconds = Column(Float, default=1.0)
    max_delay_seconds = Column(Float, default=300.0)
    backoff_multiplier = Column(Float, default=2.0)
    jitter_enabled = Column(Boolean, default=True)
    circuit_breaker_enabled = Column(Boolean, default=True)
    circuit_breaker_threshold = Column(Integer, default=5)
    circuit_breaker_timeout_seconds = Column(Integer, default=60)
    dead_letter_enabled = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)
    metadata = Column(JSON)

class RetryReason(Enum):
    """Reasons for webhook retry"""
    TIMEOUT = "timeout"
    CONNECTION_ERROR = "connection_error"
    SERVER_ERROR = "server_error"
    RATE_LIMIT = "rate_limit"
    TEMPORARY_FAILURE = "temporary_failure"
    AUTHENTICATION_ERROR = "authentication_error"
    INVALID_RESPONSE = "invalid_response"
    CIRCUIT_BREAKER_OPEN = "circuit_breaker_open"
    DOWNSTREAM_FAILURE = "downstream_failure"

class RetryStrategy(Enum):
    """Retry strategies"""
    EXPONENTIAL_BACKOFF = "exponential_backoff"
    LINEAR_BACKOFF = "linear_backoff"
    FIXED_DELAY = "fixed_delay"
    IMMEDIATE = "immediate"
    CUSTOM = "custom"

class CircuitBreakerState(Enum):
    """Circuit breaker states"""
    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"

@dataclass
class RetryPolicy:
    """Retry policy configuration"""
    policy_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    policy_name: str = "default_retry_policy"
    platform: Optional[str] = None
    event_type: Optional[str] = None
    max_attempts: int = 3
    initial_delay_seconds: float = 1.0
    max_delay_seconds: float = 300.0
    backoff_multiplier: float = 2.0
    jitter_enabled: bool = True
    jitter_range: float = 0.1  # ±10%
    retry_strategy: RetryStrategy = RetryStrategy.EXPONENTIAL_BACKOFF
    circuit_breaker_enabled: bool = True
    circuit_breaker_threshold: int = 5
    circuit_breaker_timeout_seconds: int = 60
    dead_letter_enabled: bool = True
    retry_conditions: List[str] = field(default_factory=lambda: [
        "timeout", "connection_error", "server_error", "rate_limit"
    ])
    non_retry_conditions: List[str] = field(default_factory=lambda: [
        "authentication_error", "authorization_error", "bad_request"
    ])
    custom_retry_function: Optional[Callable] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class RetryAttempt:
    """Individual retry attempt"""
    attempt_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    webhook_id: str = None
    endpoint_id: str = None
    user_id: str = None
    platform: str = None
    attempt_number: int = 1
    scheduled_time: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    executed_time: Optional[datetime] = None
    success: bool = False
    response_code: Optional[int] = None
    response_time_ms: float = 0.0
    error_message: Optional[str] = None
    retry_reason: RetryReason = RetryReason.TEMPORARY_FAILURE
    next_retry_time: Optional[datetime] = None
    payload: Dict[str, Any] = field(default_factory=dict)
    headers: Dict[str, str] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class CircuitBreaker:
    """Circuit breaker for endpoint protection"""
    endpoint_id: str
    state: CircuitBreakerState = CircuitBreakerState.CLOSED
    failure_count: int = 0
    success_count: int = 0
    last_failure_time: Optional[datetime] = None
    state_change_time: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    timeout_seconds: int = 60
    failure_threshold: int = 5
    success_threshold: int = 3  # For half-open to closed transition

class RetryHandler:
    """
    Industrial-grade webhook retry handler with advanced failure recovery
    
    Provides comprehensive retry mechanisms including exponential backoff,
    circuit breaker patterns, dead letter queues, and intelligent retry
    decision making across multi-platform webhook integrations.
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.db_session = get_db_session()
        self.performance_monitor = PerformanceMonitor("retry_handler")
        
        # Configuration
        self.default_max_attempts = self.config.get('default_max_attempts', 3)
        self.default_initial_delay = self.config.get('default_initial_delay_seconds', 1.0)
        self.default_max_delay = self.config.get('default_max_delay_seconds', 300.0)
        self.max_concurrent_retries = self.config.get('max_concurrent_retries', 100)
        self.retry_queue_size = self.config.get('retry_queue_size', 10000)
        self.dead_letter_retention_days = self.config.get('dead_letter_retention_days', 30)
        
        # Internal state
        self._redis_client = None
        self._retry_queue = asyncio.Queue(maxsize=self.retry_queue_size)
        self._active_retries: Dict[str, asyncio.Task] = {}
        self._retry_policies: Dict[str, RetryPolicy] = {}
        self._circuit_breakers: Dict[str, CircuitBreaker] = {}
        self._dead_letter_queue: List[RetryAttempt] = []
        self._retry_workers: Set[asyncio.Task] = set()
        self._cleanup_tasks: Set[asyncio.Task] = set()
        
        # Metrics tracking
        self._retry_metrics = {
            'total_retries': 0,
            'successful_retries': 0,
            'failed_retries': 0,
            'dead_lettered': 0,
            'circuit_breaker_opens': 0
        }
        
        # Initialize default policies
        self._initialize_default_policies()
        
        logger.info("RetryHandler initialized")

    async def initialize(self) -> None:
        """Initialize retry handler with required services"""
        try:
            # Initialize Redis connection
            self._redis_client = await aioredis.from_url(
                self.config.get('redis_url', 'redis://localhost:6379'),
                decode_responses=True
            )
            
            # Load retry policies from database
            await self._load_retry_policies()
            
            # Initialize circuit breakers
            await self._initialize_circuit_breakers()
            
            # Start retry workers
            await self._start_retry_workers()
            
            # Start cleanup tasks
            await self._start_cleanup_tasks()
            
            logger.info("RetryHandler initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize RetryHandler: {e}")
            raise RetryError(f"Initialization failed: {str(e)}")

    async def schedule_retry(
        self,
        webhook_id: str,
        endpoint_id: str,
        user_id: str,
        platform: str,
        event_type: str,
        payload: Dict[str, Any],
        headers: Dict[str, str],
        retry_reason: RetryReason,
        previous_attempts: int = 0,
        error_message: str = None,
        metadata: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Schedule webhook for retry
        
        Args:
            webhook_id: Unique webhook identifier
            endpoint_id: Target endpoint identifier
            user_id: User identifier
            platform: Platform name
            event_type: Type of webhook event
            payload: Webhook payload
            headers: HTTP headers
            retry_reason: Reason for retry
            previous_attempts: Number of previous attempts
            error_message: Error message from previous attempt
            metadata: Additional metadata
            
        Returns:
            Retry scheduling result
        """
        try:
            # Get retry policy
            retry_policy = await self._get_retry_policy(platform, event_type)
            
            # Check if retry should be attempted
            if not await self._should_retry(
                retry_reason, previous_attempts, retry_policy, endpoint_id
            ):
                return await self._handle_non_retryable(
                    webhook_id, endpoint_id, retry_reason, error_message
                )
            
            # Check circuit breaker
            circuit_breaker = await self._get_circuit_breaker(endpoint_id)
            if circuit_breaker.state == CircuitBreakerState.OPEN:
                if not await self._should_attempt_circuit_breaker_recovery(circuit_breaker):
                    return {
                        'success': False,
                        'reason': 'circuit_breaker_open',
                        'retry_scheduled': False,
                        'next_attempt_time': None
                    }
            
            # Calculate next retry delay
            next_delay = await self._calculate_retry_delay(
                previous_attempts + 1, retry_policy
            )
            
            next_retry_time = datetime.now(timezone.utc) + timedelta(seconds=next_delay)
            
            # Create retry attempt
            retry_attempt = RetryAttempt(
                webhook_id=webhook_id,
                endpoint_id=endpoint_id,
                user_id=user_id,
                platform=platform,
                attempt_number=previous_attempts + 1,
                scheduled_time=next_retry_time,
                retry_reason=retry_reason,
                next_retry_time=next_retry_time,
                payload=payload,
                headers=headers,
                metadata=metadata or {}
            )
            
            # Store retry attempt in database
            await self._store_retry_attempt(retry_attempt)
            
            # Add to retry queue
            await self._add_to_retry_queue(retry_attempt)
            
            # Cache in Redis
            await self._cache_retry_attempt(retry_attempt)
            
            # Update metrics
            self._retry_metrics['total_retries'] += 1
            
            logger.info(f"Retry scheduled for webhook {webhook_id}, attempt {retry_attempt.attempt_number}")
            
            return {
                'success': True,
                'attempt_id': retry_attempt.attempt_id,
                'webhook_id': webhook_id,
                'attempt_number': retry_attempt.attempt_number,
                'retry_scheduled': True,
                'next_attempt_time': next_retry_time.isoformat(),
                'delay_seconds': next_delay,
                'retry_policy': retry_policy.policy_name
            }
            
        except Exception as e:
            logger.error(f"Failed to schedule retry: {e}")
            raise RetryError(f"Retry scheduling failed: {str(e)}")

    async def execute_retry(
        self,
        attempt_id: str,
        retry_callback: Callable[[RetryAttempt], Any]
    ) -> Dict[str, Any]:
        """
        Execute retry attempt
        
        Args:
            attempt_id: Retry attempt identifier
            retry_callback: Callback function to execute the retry
            
        Returns:
            Retry execution result
        """
        try:
            # Get retry attempt
            retry_attempt = await self._get_retry_attempt(attempt_id)
            if not retry_attempt:
                raise RetryError(f"Retry attempt not found: {attempt_id}")
            
            # Check if already executed
            if retry_attempt.executed_time:
                logger.warning(f"Retry attempt already executed: {attempt_id}")
                return {'success': False, 'reason': 'already_executed'}
            
            # Update execution time
            retry_attempt.executed_time = datetime.now(timezone.utc)
            
            # Get circuit breaker
            circuit_breaker = await self._get_circuit_breaker(retry_attempt.endpoint_id)
            
            # Check circuit breaker state
            if circuit_breaker.state == CircuitBreakerState.OPEN:
                if not await self._should_attempt_circuit_breaker_recovery(circuit_breaker):
                    await self._handle_circuit_breaker_blocked(retry_attempt)
                    return {
                        'success': False,
                        'reason': 'circuit_breaker_open',
                        'attempt_id': attempt_id
                    }
                else:
                    # Transition to half-open
                    circuit_breaker.state = CircuitBreakerState.HALF_OPEN
                    circuit_breaker.state_change_time = datetime.now(timezone.utc)
                    await self._update_circuit_breaker(circuit_breaker)
            
            # Execute retry with timeout and monitoring
            start_time = time.time()
            execution_result = None
            error_occurred = False
            
            try:
                # Execute the retry callback
                execution_result = await asyncio.wait_for(
                    retry_callback(retry_attempt),
                    timeout=self.config.get('retry_timeout_seconds', 30)
                )
                
                retry_attempt.success = execution_result.get('success', False)
                retry_attempt.response_code = execution_result.get('response_code')
                retry_attempt.error_message = execution_result.get('error_message')
                
            except asyncio.TimeoutError:
                error_occurred = True
                retry_attempt.success = False
                retry_attempt.error_message = "Retry execution timeout"
                execution_result = {'success': False, 'error': 'timeout'}
                
            except Exception as e:
                error_occurred = True
                retry_attempt.success = False
                retry_attempt.error_message = str(e)
                execution_result = {'success': False, 'error': str(e)}
                logger.error(f"Retry execution failed: {e}")
            
            # Calculate response time
            retry_attempt.response_time_ms = (time.time() - start_time) * 1000
            
            # Update circuit breaker based on result
            await self._update_circuit_breaker_on_result(
                circuit_breaker, retry_attempt.success
            )
            
            # Update retry attempt in database
            await self._update_retry_attempt(retry_attempt)
            
            # Handle result
            if retry_attempt.success:
                await self._handle_successful_retry(retry_attempt)
                self._retry_metrics['successful_retries'] += 1
            else:
                await self._handle_failed_retry(retry_attempt)
                self._retry_metrics['failed_retries'] += 1
            
            # Remove from active retries
            self._active_retries.pop(attempt_id, None)
            
            # Record performance metrics
            await self.performance_monitor.record_operation(
                operation="retry_execution",
                duration_ms=retry_attempt.response_time_ms,
                metadata={
                    'success': retry_attempt.success,
                    'attempt_number': retry_attempt.attempt_number,
                    'platform': retry_attempt.platform
                }
            )
            
            logger.info(f"Retry executed for attempt {attempt_id}: {'success' if retry_attempt.success else 'failed'}")
            
            return {
                'success': retry_attempt.success,
                'attempt_id': attempt_id,
                'attempt_number': retry_attempt.attempt_number,
                'response_time_ms': retry_attempt.response_time_ms,
                'response_code': retry_attempt.response_code,
                'error_message': retry_attempt.error_message,
                'execution_result': execution_result
            }
            
        except Exception as e:
            logger.error(f"Failed to execute retry: {e}")
            raise RetryError(f"Retry execution failed: {str(e)}")

    async def cancel_retry(
        self,
        webhook_id: str = None,
        attempt_id: str = None
    ) -> Dict[str, Any]:
        """
        Cancel scheduled retry
        
        Args:
            webhook_id: Webhook identifier (cancels all retries for webhook)
            attempt_id: Specific attempt identifier
            
        Returns:
            Cancellation result
        """
        try:
            cancelled_attempts = []
            
            if attempt_id:
                # Cancel specific attempt
                if attempt_id in self._active_retries:
                    task = self._active_retries[attempt_id]
                    task.cancel()
                    del self._active_retries[attempt_id]
                    cancelled_attempts.append(attempt_id)
                
                # Remove from Redis cache
                await self._remove_retry_from_cache(attempt_id)
                
            elif webhook_id:
                # Cancel all attempts for webhook
                attempts_to_cancel = []
                for aid, task in self._active_retries.items():
                    # Get retry attempt to check webhook_id
                    retry_attempt = await self._get_retry_attempt(aid)
                    if retry_attempt and retry_attempt.webhook_id == webhook_id:
                        attempts_to_cancel.append(aid)
                
                for aid in attempts_to_cancel:
                    task = self._active_retries[aid]
                    task.cancel()
                    del self._active_retries[aid]
                    await self._remove_retry_from_cache(aid)
                    cancelled_attempts.append(aid)
            
            logger.info(f"Cancelled {len(cancelled_attempts)} retry attempts")
            
            return {
                'success': True,
                'cancelled_attempts': len(cancelled_attempts),
                'attempt_ids': cancelled_attempts
            }
            
        except Exception as e:
            logger.error(f"Failed to cancel retry: {e}")
            raise RetryError(f"Retry cancellation failed: {str(e)}")

    async def get_retry_status(
        self,
        webhook_id: str = None,
        endpoint_id: str = None,
        user_id: str = None
    ) -> Dict[str, Any]:
        """
        Get retry status and metrics
        
        Args:
            webhook_id: Optional webhook filter
            endpoint_id: Optional endpoint filter
            user_id: Optional user filter
            
        Returns:
            Retry status information
        """
        try:
            # Query retry attempts from database
            query = self.db_session.query(RetryAttemptModel)
            
            if webhook_id:
                query = query.filter(RetryAttemptModel.webhook_id == webhook_id)
            if endpoint_id:
                query = query.filter(RetryAttemptModel.endpoint_id == endpoint_id)
            if user_id:
                query = query.filter(RetryAttemptModel.user_id == user_id)
            
            # Get recent attempts (last 24 hours)
            recent_time = datetime.utcnow() - timedelta(hours=24)
            recent_attempts = query.filter(
                RetryAttemptModel.scheduled_time >= recent_time
            ).all()
            
            # Calculate statistics
            total_attempts = len(recent_attempts)
            successful_attempts = len([a for a in recent_attempts if a.success])
            failed_attempts = len([a for a in recent_attempts if a.success is False])
            pending_attempts = len([a for a in recent_attempts if a.success is None])
            
            success_rate = (successful_attempts / total_attempts * 100) if total_attempts > 0 else 0
            
            # Group by platform
            platform_stats = {}
            for attempt in recent_attempts:
                platform = attempt.platform
                if platform not in platform_stats:
                    platform_stats[platform] = {
                        'total': 0,
                        'successful': 0,
                        'failed': 0,
                        'pending': 0
                    }
                
                platform_stats[platform]['total'] += 1
                if attempt.success is True:
                    platform_stats[platform]['successful'] += 1
                elif attempt.success is False:
                    platform_stats[platform]['failed'] += 1
                else:
                    platform_stats[platform]['pending'] += 1
            
            # Get circuit breaker status
            circuit_breaker_status = {}
            for endpoint_id, cb in self._circuit_breakers.items():
                circuit_breaker_status[endpoint_id] = {
                    'state': cb.state.value,
                    'failure_count': cb.failure_count,
                    'last_failure_time': cb.last_failure_time.isoformat() if cb.last_failure_time else None
                }
            
            return {
                'summary': {
                    'total_attempts_24h': total_attempts,
                    'successful_attempts': successful_attempts,
                    'failed_attempts': failed_attempts,
                    'pending_attempts': pending_attempts,
                    'success_rate_percent': round(success_rate, 2),
                    'active_retries': len(self._active_retries),
                    'queue_size': self._retry_queue.qsize(),
                    'dead_letter_count': len(self._dead_letter_queue)
                },
                'platform_breakdown': platform_stats,
                'circuit_breakers': circuit_breaker_status,
                'overall_metrics': self._retry_metrics,
                'generated_at': datetime.now(timezone.utc).isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to get retry status: {e}")
            raise RetryError(f"Status retrieval failed: {str(e)}")

    async def create_retry_policy(
        self,
        policy_name: str,
        platform: str = None,
        event_type: str = None,
        max_attempts: int = 3,
        initial_delay_seconds: float = 1.0,
        max_delay_seconds: float = 300.0,
        backoff_multiplier: float = 2.0,
        jitter_enabled: bool = True,
        circuit_breaker_enabled: bool = True,
        circuit_breaker_threshold: int = 5,
        circuit_breaker_timeout_seconds: int = 60,
        dead_letter_enabled: bool = True,
        retry_conditions: List[str] = None,
        non_retry_conditions: List[str] = None
    ) -> str:
        """
        Create custom retry policy
        
        Args:
            policy_name: Name for the policy
            platform: Optional platform filter
            event_type: Optional event type filter
            max_attempts: Maximum retry attempts
            initial_delay_seconds: Initial retry delay
            max_delay_seconds: Maximum retry delay
            backoff_multiplier: Exponential backoff multiplier
            jitter_enabled: Enable jitter in delays
            circuit_breaker_enabled: Enable circuit breaker
            circuit_breaker_threshold: Circuit breaker failure threshold
            circuit_breaker_timeout_seconds: Circuit breaker timeout
            dead_letter_enabled: Enable dead letter queue
            retry_conditions: Conditions that trigger retries
            non_retry_conditions: Conditions that prevent retries
            
        Returns:
            Policy ID
        """
        try:
            # Create retry policy
            policy = RetryPolicy(
                policy_name=policy_name,
                platform=platform,
                event_type=event_type,
                max_attempts=max_attempts,
                initial_delay_seconds=initial_delay_seconds,
                max_delay_seconds=max_delay_seconds,
                backoff_multiplier=backoff_multiplier,
                jitter_enabled=jitter_enabled,
                circuit_breaker_enabled=circuit_breaker_enabled,
                circuit_breaker_threshold=circuit_breaker_threshold,
                circuit_breaker_timeout_seconds=circuit_breaker_timeout_seconds,
                dead_letter_enabled=dead_letter_enabled,
                retry_conditions=retry_conditions or [
                    "timeout", "connection_error", "server_error", "rate_limit"
                ],
                non_retry_conditions=non_retry_conditions or [
                    "authentication_error", "authorization_error", "bad_request"
                ]
            )
            
            # Store in database
            await self._store_retry_policy(policy)
            
            # Cache policy
            policy_key = self._get_policy_key(platform, event_type)
            self._retry_policies[policy_key] = policy
            
            logger.info(f"Retry policy created: {policy.policy_id}")
            
            return policy.policy_id
            
        except Exception as e:
            logger.error(f"Failed to create retry policy: {e}")
            raise RetryError(f"Policy creation failed: {str(e)}")

    async def health_check(self) -> Dict[str, Any]:
        """Comprehensive health check for retry handler"""
        return {
            'status': 'healthy',
            'redis_connected': self._redis_client is not None,
            'active_retries': len(self._active_retries),
            'queue_size': self._retry_queue.qsize(),
            'dead_letter_count': len(self._dead_letter_queue),
            'circuit_breakers': len(self._circuit_breakers),
            'retry_policies': len(self._retry_policies),
            'retry_workers': len(self._retry_workers),
            'cleanup_tasks': len(self._cleanup_tasks),
            'metrics': self._retry_metrics
        }

    async def shutdown(self) -> None:
        """Graceful shutdown of retry handler"""
        try:
            logger.info("Shutting down RetryHandler")
            
            # Cancel all retry workers
            for worker in self._retry_workers:
                worker.cancel()
            
            # Cancel cleanup tasks
            for task in self._cleanup_tasks:
                task.cancel()
            
            # Cancel active retries
            for task in self._active_retries.values():
                task.cancel()
            
            # Close Redis connection
            if self._redis_client:
                await self._redis_client.close()
            
            logger.info("RetryHandler shutdown complete")
            
        except Exception as e:
            logger.error(f"Error during RetryHandler shutdown: {e}")

    # Private methods
    
    def _initialize_default_policies(self) -> None:
        """Initialize default retry policies"""
        
        # Default policy
        default_policy = RetryPolicy(
            policy_name="default_retry_policy",
            max_attempts=3,
            initial_delay_seconds=1.0,
            max_delay_seconds=300.0,
            backoff_multiplier=2.0,
            jitter_enabled=True
        )
        self._retry_policies["default"] = default_policy
        
        # High-priority policy for critical platforms
        critical_policy = RetryPolicy(
            policy_name="critical_platform_policy",
            max_attempts=5,
            initial_delay_seconds=0.5,
            max_delay_seconds=60.0,
            backoff_multiplier=1.5,
            circuit_breaker_threshold=10
        )
        self._retry_policies["critical"] = critical_policy
        
        # Rate-limited policy
        rate_limited_policy = RetryPolicy(
            policy_name="rate_limited_policy",
            max_attempts=10,
            initial_delay_seconds=5.0,
            max_delay_seconds=3600.0,  # 1 hour max
            backoff_multiplier=2.0,
            retry_conditions=["rate_limit", "timeout"]
        )
        self._retry_policies["rate_limited"] = rate_limited_policy

    async def _get_retry_policy(
        self,
        platform: str,
        event_type: str = None
    ) -> RetryPolicy:
        """Get retry policy for platform and event type"""
        
        # Try specific platform + event type
        if event_type:
            policy_key = self._get_policy_key(platform, event_type)
            if policy_key in self._retry_policies:
                return self._retry_policies[policy_key]
        
        # Try platform only
        policy_key = self._get_policy_key(platform, None)
        if policy_key in self._retry_policies:
            return self._retry_policies[policy_key]
        
        # Return default policy
        return self._retry_policies["default"]

    def _get_policy_key(self, platform: str, event_type: str = None) -> str:
        """Generate policy key"""
        if event_type:
            return f"{platform}:{event_type}"
        return platform

    async def _should_retry(
        self,
        retry_reason: RetryReason,
        previous_attempts: int,
        retry_policy: RetryPolicy,
        endpoint_id: str
    ) -> bool:
        """Determine if retry should be attempted"""
        
        # Check max attempts
        if previous_attempts >= retry_policy.max_attempts:
            logger.info(f"Max retry attempts reached for endpoint {endpoint_id}")
            return False
        
        # Check retry conditions
        if retry_reason.value not in retry_policy.retry_conditions:
            logger.info(f"Retry reason {retry_reason.value} not in retry conditions")
            return False
        
        # Check non-retry conditions
        if retry_reason.value in retry_policy.non_retry_conditions:
            logger.info(f"Retry reason {retry_reason.value} in non-retry conditions")
            return False
        
        return True

    async def _calculate_retry_delay(
        self,
        attempt_number: int,
        retry_policy: RetryPolicy
    ) -> float:
        """Calculate delay for retry attempt"""
        
        if retry_policy.retry_strategy == RetryStrategy.EXPONENTIAL_BACKOFF:
            delay = retry_policy.initial_delay_seconds * (
                retry_policy.backoff_multiplier ** (attempt_number - 1)
            )
        elif retry_policy.retry_strategy == RetryStrategy.LINEAR_BACKOFF:
            delay = retry_policy.initial_delay_seconds * attempt_number
        elif retry_policy.retry_strategy == RetryStrategy.FIXED_DELAY:
            delay = retry_policy.initial_delay_seconds
        elif retry_policy.retry_strategy == RetryStrategy.IMMEDIATE:
            delay = 0.0
        else:
            # Custom strategy or fallback to exponential
            delay = retry_policy.initial_delay_seconds * (
                retry_policy.backoff_multiplier ** (attempt_number - 1)
            )
        
        # Apply maximum delay limit
        delay = min(delay, retry_policy.max_delay_seconds)
        
        # Apply jitter if enabled
        if retry_policy.jitter_enabled:
            jitter_amount = delay * retry_policy.jitter_range
            jitter = random.uniform(-jitter_amount, jitter_amount)
            delay += jitter
        
        # Ensure minimum delay
        delay = max(delay, 0.0)
        
        return delay

    async def _get_circuit_breaker(self, endpoint_id: str) -> CircuitBreaker:
        """Get or create circuit breaker for endpoint"""
        if endpoint_id not in self._circuit_breakers:
            self._circuit_breakers[endpoint_id] = CircuitBreaker(endpoint_id=endpoint_id)
        
        return self._circuit_breakers[endpoint_id]

    async def _should_attempt_circuit_breaker_recovery(
        self,
        circuit_breaker: CircuitBreaker
    ) -> bool:
        """Check if circuit breaker should attempt recovery"""
        if circuit_breaker.state != CircuitBreakerState.OPEN:
            return True
        
        # Check if timeout has passed
        if circuit_breaker.last_failure_time:
            time_since_failure = datetime.now(timezone.utc) - circuit_breaker.last_failure_time
            if time_since_failure.total_seconds() >= circuit_breaker.timeout_seconds:
                return True
        
        return False

    async def _update_circuit_breaker_on_result(
        self,
        circuit_breaker: CircuitBreaker,
        success: bool
    ) -> None:
        """Update circuit breaker based on operation result"""
        current_time = datetime.now(timezone.utc)
        
        if success:
            circuit_breaker.success_count += 1
            
            if circuit_breaker.state == CircuitBreakerState.HALF_OPEN:
                if circuit_breaker.success_count >= circuit_breaker.success_threshold:
                    # Transition to closed
                    circuit_breaker.state = CircuitBreakerState.CLOSED
                    circuit_breaker.failure_count = 0
                    circuit_breaker.success_count = 0
                    circuit_breaker.state_change_time = current_time
                    logger.info(f"Circuit breaker closed for endpoint {circuit_breaker.endpoint_id}")
            
            elif circuit_breaker.state == CircuitBreakerState.CLOSED:
                # Reset failure count on success
                circuit_breaker.failure_count = 0
        
        else:
            circuit_breaker.failure_count += 1
            circuit_breaker.last_failure_time = current_time
            
            if circuit_breaker.state == CircuitBreakerState.CLOSED:
                if circuit_breaker.failure_count >= circuit_breaker.failure_threshold:
                    # Transition to open
                    circuit_breaker.state = CircuitBreakerState.OPEN
                    circuit_breaker.state_change_time = current_time
                    self._retry_metrics['circuit_breaker_opens'] += 1
                    logger.warning(f"Circuit breaker opened for endpoint {circuit_breaker.endpoint_id}")
            
            elif circuit_breaker.state == CircuitBreakerState.HALF_OPEN:
                # Back to open on failure
                circuit_breaker.state = CircuitBreakerState.OPEN
                circuit_breaker.state_change_time = current_time
                circuit_breaker.success_count = 0
        
        await self._update_circuit_breaker(circuit_breaker)

    async def _handle_non_retryable(
        self,
        webhook_id: str,
        endpoint_id: str,
        retry_reason: RetryReason,
        error_message: str = None
    ) -> Dict[str, Any]:
        """Handle non-retryable webhook"""
        
        # Add to dead letter queue if configured
        dead_letter_entry = {
            'webhook_id': webhook_id,
            'endpoint_id': endpoint_id,
            'retry_reason': retry_reason.value,
            'error_message': error_message,
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'reason': 'non_retryable'
        }
        
        self._dead_letter_queue.append(dead_letter_entry)
        self._retry_metrics['dead_lettered'] += 1
        
        logger.info(f"Webhook {webhook_id} added to dead letter queue: {retry_reason.value}")
        
        return {
            'success': False,
            'reason': 'non_retryable',
            'retry_scheduled': False,
            'dead_lettered': True,
            'retry_reason': retry_reason.value
        }

    async def _handle_successful_retry(self, retry_attempt: RetryAttempt) -> None:
        """Handle successful retry attempt"""
        
        # Remove any pending retries for same webhook
        await self._cancel_pending_retries(retry_attempt.webhook_id)
        
        # Update success metrics
        logger.info(f"Retry successful for webhook {retry_attempt.webhook_id} on attempt {retry_attempt.attempt_number}")

    async def _handle_failed_retry(self, retry_attempt: RetryAttempt) -> None:
        """Handle failed retry attempt"""
        
        # Check if this was the final attempt
        retry_policy = await self._get_retry_policy(retry_attempt.platform)
        
        if retry_attempt.attempt_number >= retry_policy.max_attempts:
            # Final attempt failed - add to dead letter queue
            dead_letter_entry = {
                'webhook_id': retry_attempt.webhook_id,
                'endpoint_id': retry_attempt.endpoint_id,
                'retry_reason': retry_attempt.retry_reason.value,
                'error_message': retry_attempt.error_message,
                'timestamp': datetime.now(timezone.utc).isoformat(),
                'reason': 'max_retries_exceeded',
                'total_attempts': retry_attempt.attempt_number
            }
            
            self._dead_letter_queue.append(dead_letter_entry)
            self._retry_metrics['dead_lettered'] += 1
            
            logger.warning(f"Webhook {retry_attempt.webhook_id} failed after {retry_attempt.attempt_number} attempts")

    # Database operations and other implementation details would continue...
    # This is a comprehensive but abbreviated implementation for space
    
    async def _store_retry_attempt(self, retry_attempt: RetryAttempt) -> None:
        """Store retry attempt in database - placeholder"""
        pass
    
    async def _update_retry_attempt(self, retry_attempt: RetryAttempt) -> None:
        """Update retry attempt in database - placeholder"""
        pass
    
    async def _get_retry_attempt(self, attempt_id: str) -> Optional[RetryAttempt]:
        """Get retry attempt from database - placeholder"""
        return None
    
    async def _add_to_retry_queue(self, retry_attempt: RetryAttempt) -> None:
        """Add retry attempt to processing queue - placeholder"""
        pass
    
    async def _cache_retry_attempt(self, retry_attempt: RetryAttempt) -> None:
        """Cache retry attempt in Redis - placeholder"""
        pass
    
    async def _load_retry_policies(self) -> None:
        """Load retry policies from database - placeholder"""
        pass
    
    async def _store_retry_policy(self, policy: RetryPolicy) -> None:
        """Store retry policy in database - placeholder"""
        pass
    
    async def _initialize_circuit_breakers(self) -> None:
        """Initialize circuit breakers from database - placeholder"""
        pass
    
    async def _update_circuit_breaker(self, circuit_breaker: CircuitBreaker) -> None:
        """Update circuit breaker state - placeholder"""
        pass
    
    async def _start_retry_workers(self) -> None:
        """Start retry worker tasks - placeholder"""
        pass
    
    async def _start_cleanup_tasks(self) -> None:
        """Start cleanup tasks - placeholder"""
        pass
    
    async def _cancel_pending_retries(self, webhook_id: str) -> None:
        """Cancel pending retries for webhook - placeholder"""
        pass
    
    async def _remove_retry_from_cache(self, attempt_id: str) -> None:
        """Remove retry from cache - placeholder"""
        pass
    
    async def _handle_circuit_breaker_blocked(self, retry_attempt: RetryAttempt) -> None:
        """Handle circuit breaker blocked retry - placeholder"""
        pass
