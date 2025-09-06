"""Retry Resilience Engine Module

Advanced retry mechanisms with intelligent backoff strategies and circuit breaker patterns
for the Ainflue Message Queues Enterprise system.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️ INTELLECTUAL PROPERTY WARNING ⚠️
This Retry Resilience Engine architecture and implementation are EXCLUSIVE PROPERTY
of Fahed Mlaiel. Unauthorized use, reproduction, or adaptation is STRICTLY PROHIBITED.
Legal consequences include substantial damages and criminal prosecution.

Authorization Contact: mlaiel@live.de
"""

import asyncio
import json
import logging
import random
import time
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional, Any, Callable, Union, Tuple
from dataclasses import dataclass, field
from enum import Enum
from uuid import uuid4
from collections import defaultdict, deque
import math

from ..core.exceptions import MessageQueueError
from ..utils.monitoring import MetricsCollector
from ..security.encryption import EncryptionManager

logger = logging.getLogger(__name__)


class BackoffStrategy(Enum):
    """Backoff strategies for retry attempts"""
    FIXED = "fixed"
    LINEAR = "linear"
    EXPONENTIAL = "exponential"
    FIBONACCI = "fibonacci"
    JITTERED_EXPONENTIAL = "jittered_exponential"


class ErrorCategory(Enum):
    """Error categories for different retry strategies"""
    TEMPORARY = "temporary"
    PERMANENT = "permanent"
    BUSINESS = "business"
    TIMEOUT = "timeout"
    RESOURCE = "resource"
    AUTHENTICATION = "authentication"
    RATE_LIMIT = "rate_limit"


class CircuitBreakerState(Enum):
    """Circuit breaker states"""
    CLOSED = "closed"      # Normal operation
    OPEN = "open"          # Blocking requests
    HALF_OPEN = "half_open"  # Testing recovery


@dataclass
class RetryPolicy:
    """Retry policy configuration"""
    max_attempts: int = 3
    backoff_strategy: BackoffStrategy = BackoffStrategy.EXPONENTIAL
    initial_delay: float = 1.0  # seconds
    max_delay: float = 300.0    # 5 minutes
    backoff_multiplier: float = 2.0
    jitter: bool = True
    jitter_max: float = 0.1  # 10% jitter
    
    # Error handling
    retryable_errors: List[str] = field(default_factory=list)
    non_retryable_errors: List[str] = field(default_factory=list)
    
    # Circuit breaker settings
    circuit_breaker_enabled: bool = True
    circuit_breaker_threshold: int = 5
    circuit_breaker_timeout: float = 60.0  # seconds


@dataclass
class RetryAttempt:
    """Individual retry attempt record"""
    attempt_number: int
    timestamp: datetime
    delay_before: float
    error: Optional[str] = None
    success: bool = False
    duration: float = 0.0


@dataclass
class RetryExecution:
    """Complete retry execution tracking"""
    execution_id: str = field(default_factory=lambda: str(uuid4()))
    message_id: str = ""
    policy: RetryPolicy = field(default_factory=RetryPolicy)
    attempts: List[RetryAttempt] = field(default_factory=list)
    started_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    completed_at: Optional[datetime] = None
    final_success: bool = False
    total_duration: float = 0.0
    error_category: Optional[ErrorCategory] = None


@dataclass
class CircuitBreakerMetrics:
    """Circuit breaker metrics"""
    service_name: str
    state: CircuitBreakerState = CircuitBreakerState.CLOSED
    failure_count: int = 0
    success_count: int = 0
    last_failure_time: Optional[datetime] = None
    last_success_time: Optional[datetime] = None
    total_requests: int = 0
    state_changed_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


class AinflueBusiness:
    """Ainflue Business Retry Strategies"""
    
    # Retry policies by event type
    RETRY_POLICIES = {
        # Critical payment processing - aggressive retry
        "payment_processing": RetryPolicy(
            max_attempts=10,
            backoff_strategy=BackoffStrategy.EXPONENTIAL,
            initial_delay=1.0,
            max_delay=300.0,
            backoff_multiplier=1.5,
            jitter=True,
            circuit_breaker_threshold=3
        ),
        
        # AI content analysis - moderate retry
        "ai_content_analysis": RetryPolicy(
            max_attempts=5,
            backoff_strategy=BackoffStrategy.LINEAR,
            initial_delay=10.0,
            max_delay=120.0,
            backoff_multiplier=2.0,
            jitter=False,
            circuit_breaker_threshold=5
        ),
        
        # Collaboration matching - balanced retry
        "collaboration_match": RetryPolicy(
            max_attempts=4,
            backoff_strategy=BackoffStrategy.JITTERED_EXPONENTIAL,
            initial_delay=5.0,
            max_delay=60.0,
            backoff_multiplier=2.0,
            jitter=True,
            circuit_breaker_threshold=4
        ),
        
        # Content upload - patient retry
        "content_upload": RetryPolicy(
            max_attempts=6,
            backoff_strategy=BackoffStrategy.EXPONENTIAL,
            initial_delay=2.0,
            max_delay=180.0,
            backoff_multiplier=2.0,
            jitter=True,
            circuit_breaker_threshold=8
        ),
        
        # Analytics processing - conservative retry
        "analytics_processing": RetryPolicy(
            max_attempts=3,
            backoff_strategy=BackoffStrategy.FIXED,
            initial_delay=30.0,
            max_delay=30.0,
            circuit_breaker_threshold=10
        ),
        
        # SEO optimization - standard retry
        "seo_optimization": RetryPolicy(
            max_attempts=4,
            backoff_strategy=BackoffStrategy.EXPONENTIAL,
            initial_delay=15.0,
            max_delay=240.0,
            backoff_multiplier=2.0,
            circuit_breaker_threshold=6
        )
    }
    
    # Error classification rules
    ERROR_HANDLING_RULES = {
        # Temporary errors - always retry
        "temporary_errors": [
            "ConnectionTimeout",
            "ServiceUnavailable", 
            "TemporaryDatabaseError",
            "NetworkError",
            "TemporaryServiceError",
            "TimeoutError",
            "Redis Connection Error",
            "Database Connection Lost"
        ],
        
        # Rate limiting - special retry with backoff
        "rate_limit_errors": [
            "RateLimitExceeded",
            "TooManyRequests",
            "QuotaExceeded",
            "ThrottlingError"
        ],
        
        # Permanent errors - no retry
        "permanent_errors": [
            "AuthenticationFailed",
            "InvalidPayload",
            "BusinessRuleViolation",
            "ContentNotFound",
            "PermissionDenied",
            "InvalidRequestFormat",
            "SchemaValidationError"
        ],
        
        # Business errors - escalate immediately
        "business_errors": [
            "CopyrightViolation",
            "PaymentFraud",
            "SecurityBreach",
            "ComplianceViolation",
            "ContentPolicyViolation",
            "TermsOfServiceViolation"
        ]
    }
    
    # Circuit breaker configurations by service
    CIRCUIT_BREAKER_CONFIGS = {
        "payment_gateway": {
            "failure_threshold": 3,
            "timeout": 30.0,
            "recovery_timeout": 60.0
        },
        "ai_service": {
            "failure_threshold": 5,
            "timeout": 60.0,
            "recovery_timeout": 120.0
        },
        "content_storage": {
            "failure_threshold": 8,
            "timeout": 45.0,
            "recovery_timeout": 90.0
        },
        "external_api": {
            "failure_threshold": 4,
            "timeout": 30.0,
            "recovery_timeout": 60.0
        }
    }


class RetryResilienceEngine:
    """
    Advanced retry mechanisms with intelligent backoff and circuit breaker patterns
    Provides comprehensive error handling and resilience for Ainflue business operations
    """
    
    def __init__(self,
                 metrics_collector: Optional[MetricsCollector] = None,
                 encryption_manager: Optional[EncryptionManager] = None):
        self.metrics = metrics_collector
        self.encryption = encryption_manager
        
        # Retry tracking
        self.active_retries = {}  # execution_id -> RetryExecution
        self.completed_retries = {}  # execution_id -> RetryExecution
        self.retry_statistics = defaultdict(lambda: {"attempts": 0, "successes": 0, "failures": 0})
        
        # Circuit breakers
        self.circuit_breakers = {}  # service_name -> CircuitBreakerMetrics
        self.circuit_breaker_callbacks = {}  # service_name -> callback
        
        # Error classification
        self.error_classifiers = {}
        self.custom_retry_policies = {}
        
        # Dead letter queue
        self.dead_letter_queue = deque(maxlen=10000)  # Last 10k failed messages
        
        logger.info("Initialized Retry Resilience Engine")
    
    async def execute_with_retry(self,
                               operation: Callable,
                               message_id: str,
                               event_type: str,
                               *args,
                               custom_policy: Optional[RetryPolicy] = None,
                               **kwargs) -> Tuple[bool, Any, Optional[str]]:
        """Execute operation with retry logic"""
        try:
            # Get retry policy
            policy = custom_policy or self._get_retry_policy(event_type)
            
            # Create retry execution
            execution = RetryExecution(
                message_id=message_id,
                policy=policy
            )
            
            self.active_retries[execution.execution_id] = execution
            
            # Execute with retries
            success, result, error = await self._execute_with_policy(
                operation, execution, *args, **kwargs
            )
            
            # Complete execution tracking
            execution.completed_at = datetime.now(timezone.utc)
            execution.final_success = success
            execution.total_duration = (execution.completed_at - execution.started_at).total_seconds()
            
            # Move to completed
            self.completed_retries[execution.execution_id] = execution
            del self.active_retries[execution.execution_id]
            
            # Update statistics
            await self._update_retry_statistics(event_type, execution)
            
            # Handle dead letter if final failure
            if not success:
                await self._handle_dead_letter(message_id, event_type, error, execution)
            
            return success, result, error
            
        except Exception as e:
            logger.error(f"Error in retry execution: {str(e)}")
            return False, None, str(e)
    
    async def register_circuit_breaker(self,
                                     service_name: str,
                                     failure_threshold: int = 5,
                                     timeout: float = 60.0,
                                     recovery_callback: Optional[Callable] = None):
        """Register a circuit breaker for a service"""
        config = AinflueBusiness.CIRCUIT_BREAKER_CONFIGS.get(service_name, {})
        
        self.circuit_breakers[service_name] = CircuitBreakerMetrics(
            service_name=service_name,
            state=CircuitBreakerState.CLOSED
        )
        
        if recovery_callback:
            self.circuit_breaker_callbacks[service_name] = recovery_callback
        
        logger.info(f"Registered circuit breaker for service: {service_name}")
    
    async def check_circuit_breaker(self, service_name: str) -> bool:
        """Check if circuit breaker allows request"""
        if service_name not in self.circuit_breakers:
            return True  # No circuit breaker = allow
        
        breaker = self.circuit_breakers[service_name]
        config = AinflueBusiness.CIRCUIT_BREAKER_CONFIGS.get(service_name, {})
        
        current_time = datetime.now(timezone.utc)
        
        if breaker.state == CircuitBreakerState.CLOSED:
            return True
        
        elif breaker.state == CircuitBreakerState.OPEN:
            # Check if timeout has passed
            timeout = config.get("recovery_timeout", 60.0)
            time_since_failure = (current_time - breaker.last_failure_time).total_seconds()
            
            if time_since_failure >= timeout:
                # Move to half-open
                await self._transition_circuit_breaker(service_name, CircuitBreakerState.HALF_OPEN)
                return True
            
            return False
        
        elif breaker.state == CircuitBreakerState.HALF_OPEN:
            # Allow limited requests to test recovery
            return True
        
        return False
    
    async def record_circuit_breaker_result(self, service_name: str, success: bool):
        """Record circuit breaker operation result"""
        if service_name not in self.circuit_breakers:
            return
        
        breaker = self.circuit_breakers[service_name]
        config = AinflueBusiness.CIRCUIT_BREAKER_CONFIGS.get(service_name, {})
        current_time = datetime.now(timezone.utc)
        
        breaker.total_requests += 1
        
        if success:
            breaker.success_count += 1
            breaker.last_success_time = current_time
            
            if breaker.state == CircuitBreakerState.HALF_OPEN:
                # Successful test - close circuit
                await self._transition_circuit_breaker(service_name, CircuitBreakerState.CLOSED)
                breaker.failure_count = 0
            
        else:
            breaker.failure_count += 1
            breaker.last_failure_time = current_time
            
            failure_threshold = config.get("failure_threshold", 5)
            
            if (breaker.state == CircuitBreakerState.CLOSED and 
                breaker.failure_count >= failure_threshold):
                # Open circuit
                await self._transition_circuit_breaker(service_name, CircuitBreakerState.OPEN)
            
            elif breaker.state == CircuitBreakerState.HALF_OPEN:
                # Failed test - back to open
                await self._transition_circuit_breaker(service_name, CircuitBreakerState.OPEN)
    
    async def get_retry_statistics(self, event_type: Optional[str] = None) -> Dict[str, Any]:
        """Get retry statistics"""
        try:
            if event_type:
                stats = self.retry_statistics.get(event_type, {})
                return {
                    "event_type": event_type,
                    "total_attempts": stats.get("attempts", 0),
                    "successes": stats.get("successes", 0),
                    "failures": stats.get("failures", 0),
                    "success_rate": self._calculate_success_rate(stats),
                    "active_retries": len([e for e in self.active_retries.values() 
                                         if e.message_id.startswith(event_type)])
                }
            else:
                # Global statistics
                total_attempts = sum(stats.get("attempts", 0) for stats in self.retry_statistics.values())
                total_successes = sum(stats.get("successes", 0) for stats in self.retry_statistics.values())
                total_failures = sum(stats.get("failures", 0) for stats in self.retry_statistics.values())
                
                return {
                    "global_statistics": {
                        "total_attempts": total_attempts,
                        "total_successes": total_successes,
                        "total_failures": total_failures,
                        "overall_success_rate": (total_successes / max(total_attempts, 1)) * 100,
                        "active_retries": len(self.active_retries),
                        "dead_letter_count": len(self.dead_letter_queue)
                    },
                    "by_event_type": {
                        event_type: {
                            "attempts": stats.get("attempts", 0),
                            "successes": stats.get("successes", 0),
                            "failures": stats.get("failures", 0),
                            "success_rate": self._calculate_success_rate(stats)
                        }
                        for event_type, stats in self.retry_statistics.items()
                    }
                }
        except Exception as e:
            logger.error(f"Error getting retry statistics: {str(e)}")
            return {"error": str(e)}
    
    async def get_circuit_breaker_status(self, service_name: Optional[str] = None) -> Dict[str, Any]:
        """Get circuit breaker status"""
        try:
            if service_name:
                if service_name not in self.circuit_breakers:
                    return {"error": f"Circuit breaker not found for service: {service_name}"}
                
                breaker = self.circuit_breakers[service_name]
                return {
                    "service_name": service_name,
                    "state": breaker.state.value,
                    "failure_count": breaker.failure_count,
                    "success_count": breaker.success_count,
                    "total_requests": breaker.total_requests,
                    "success_rate": (breaker.success_count / max(breaker.total_requests, 1)) * 100,
                    "last_failure": breaker.last_failure_time.isoformat() if breaker.last_failure_time else None,
                    "last_success": breaker.last_success_time.isoformat() if breaker.last_success_time else None,
                    "state_changed_at": breaker.state_changed_at.isoformat()
                }
            else:
                # All circuit breakers
                return {
                    "circuit_breakers": {
                        name: {
                            "state": breaker.state.value,
                            "failure_count": breaker.failure_count,
                            "success_count": breaker.success_count,
                            "total_requests": breaker.total_requests,
                            "success_rate": (breaker.success_count / max(breaker.total_requests, 1)) * 100
                        }
                        for name, breaker in self.circuit_breakers.items()
                    }
                }
        except Exception as e:
            logger.error(f"Error getting circuit breaker status: {str(e)}")
            return {"error": str(e)}
    
    async def get_dead_letter_messages(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get dead letter queue messages"""
        try:
            messages = list(self.dead_letter_queue)[-limit:]
            return [
                {
                    "message_id": msg.get("message_id"),
                    "event_type": msg.get("event_type"),
                    "error": msg.get("error"),
                    "attempts": msg.get("attempts"),
                    "timestamp": msg.get("timestamp")
                }
                for msg in messages
            ]
        except Exception as e:
            logger.error(f"Error getting dead letter messages: {str(e)}")
            return []
    
    async def replay_dead_letter_message(self, message_id: str) -> bool:
        """Replay a message from dead letter queue"""
        try:
            # Find message in dead letter queue
            for msg in self.dead_letter_queue:
                if msg.get("message_id") == message_id:
                    # Remove from DLQ and retry
                    self.dead_letter_queue.remove(msg)
                    
                    # TODO: Re-enqueue message for processing
                    logger.info(f"Replaying dead letter message: {message_id}")
                    return True
            
            return False
        except Exception as e:
            logger.error(f"Error replaying dead letter message: {str(e)}")
            return False
    
    # Core retry logic
    
    async def _execute_with_policy(self,
                                 operation: Callable,
                                 execution: RetryExecution,
                                 *args,
                                 **kwargs) -> Tuple[bool, Any, Optional[str]]:
        """Execute operation with retry policy"""
        policy = execution.policy
        
        for attempt_num in range(1, policy.max_attempts + 1):
            # Calculate delay before this attempt
            delay = self._calculate_delay(attempt_num, policy) if attempt_num > 1 else 0
            
            if delay > 0:
                await asyncio.sleep(delay)
            
            # Record attempt start
            attempt = RetryAttempt(
                attempt_number=attempt_num,
                timestamp=datetime.now(timezone.utc),
                delay_before=delay
            )
            
            try:
                # Execute operation
                start_time = time.time()
                result = await operation(*args, **kwargs)
                duration = time.time() - start_time
                
                # Success
                attempt.success = True
                attempt.duration = duration
                execution.attempts.append(attempt)
                
                logger.debug(f"Operation succeeded on attempt {attempt_num}")
                return True, result, None
                
            except Exception as e:
                duration = time.time() - start_time
                error_str = str(e)
                
                attempt.error = error_str
                attempt.duration = duration
                execution.attempts.append(attempt)
                
                # Classify error
                error_category = self._classify_error(error_str)
                execution.error_category = error_category
                
                # Check if error is retryable
                if not self._is_retryable_error(error_str, policy, error_category):
                    logger.info(f"Non-retryable error: {error_str}")
                    return False, None, error_str
                
                # Check if this was the last attempt
                if attempt_num >= policy.max_attempts:
                    logger.warning(f"Max attempts ({policy.max_attempts}) reached for operation")
                    return False, None, error_str
                
                logger.info(f"Attempt {attempt_num} failed: {error_str}, retrying...")
        
        return False, None, "Max retry attempts exceeded"
    
    def _get_retry_policy(self, event_type: str) -> RetryPolicy:
        """Get retry policy for event type"""
        # Check custom policies first
        if event_type in self.custom_retry_policies:
            return self.custom_retry_policies[event_type]
        
        # Check business policies
        if event_type in AinflueBusiness.RETRY_POLICIES:
            return AinflueBusiness.RETRY_POLICIES[event_type]
        
        # Default policy
        return RetryPolicy()
    
    def _calculate_delay(self, attempt_num: int, policy: RetryPolicy) -> float:
        """Calculate delay before retry attempt"""
        if policy.backoff_strategy == BackoffStrategy.FIXED:
            delay = policy.initial_delay
        
        elif policy.backoff_strategy == BackoffStrategy.LINEAR:
            delay = policy.initial_delay * attempt_num
        
        elif policy.backoff_strategy == BackoffStrategy.EXPONENTIAL:
            delay = policy.initial_delay * (policy.backoff_multiplier ** (attempt_num - 1))
        
        elif policy.backoff_strategy == BackoffStrategy.FIBONACCI:
            delay = policy.initial_delay * self._fibonacci(attempt_num)
        
        elif policy.backoff_strategy == BackoffStrategy.JITTERED_EXPONENTIAL:
            base_delay = policy.initial_delay * (policy.backoff_multiplier ** (attempt_num - 1))
            jitter_amount = base_delay * policy.jitter_max * random.random()
            delay = base_delay + jitter_amount
        
        else:
            delay = policy.initial_delay
        
        # Apply jitter if enabled (except for jittered exponential which has its own)
        if policy.jitter and policy.backoff_strategy != BackoffStrategy.JITTERED_EXPONENTIAL:
            jitter_amount = delay * policy.jitter_max * random.random()
            delay += jitter_amount
        
        # Cap at max delay
        return min(delay, policy.max_delay)
    
    def _fibonacci(self, n: int) -> int:
        """Calculate nth Fibonacci number"""
        if n <= 1:
            return n
        a, b = 0, 1
        for _ in range(2, n + 1):
            a, b = b, a + b
        return b
    
    def _classify_error(self, error_str: str) -> ErrorCategory:
        """Classify error into category"""
        error_rules = AinflueBusiness.ERROR_HANDLING_RULES
        
        # Check business errors first
        for business_error in error_rules["business_errors"]:
            if business_error.lower() in error_str.lower():
                return ErrorCategory.BUSINESS
        
        # Check permanent errors
        for permanent_error in error_rules["permanent_errors"]:
            if permanent_error.lower() in error_str.lower():
                return ErrorCategory.PERMANENT
        
        # Check rate limit errors
        for rate_error in error_rules["rate_limit_errors"]:
            if rate_error.lower() in error_str.lower():
                return ErrorCategory.RATE_LIMIT
        
        # Check temporary errors
        for temp_error in error_rules["temporary_errors"]:
            if temp_error.lower() in error_str.lower():
                return ErrorCategory.TEMPORARY
        
        # Check for timeout patterns
        if any(word in error_str.lower() for word in ["timeout", "timed out", "deadline"]):
            return ErrorCategory.TIMEOUT
        
        # Check for resource patterns
        if any(word in error_str.lower() for word in ["resource", "memory", "disk", "capacity"]):
            return ErrorCategory.RESOURCE
        
        # Check for authentication patterns
        if any(word in error_str.lower() for word in ["auth", "unauthorized", "forbidden", "token"]):
            return ErrorCategory.AUTHENTICATION
        
        # Default to temporary for unknown errors
        return ErrorCategory.TEMPORARY
    
    def _is_retryable_error(self, error_str: str, policy: RetryPolicy, category: ErrorCategory) -> bool:
        """Determine if error is retryable"""
        # Check policy-specific rules first
        if policy.non_retryable_errors:
            for non_retryable in policy.non_retryable_errors:
                if non_retryable.lower() in error_str.lower():
                    return False
        
        if policy.retryable_errors:
            for retryable in policy.retryable_errors:
                if retryable.lower() in error_str.lower():
                    return True
        
        # Use category-based rules
        if category == ErrorCategory.PERMANENT:
            return False
        elif category == ErrorCategory.BUSINESS:
            return False  # Business errors need manual intervention
        elif category in [ErrorCategory.TEMPORARY, ErrorCategory.TIMEOUT, ErrorCategory.RESOURCE]:
            return True
        elif category == ErrorCategory.RATE_LIMIT:
            return True  # Rate limits should be retried with backoff
        elif category == ErrorCategory.AUTHENTICATION:
            return False  # Auth errors usually permanent
        
        # Default to retryable for unknown categories
        return True
    
    async def _transition_circuit_breaker(self, service_name: str, new_state: CircuitBreakerState):
        """Transition circuit breaker to new state"""
        if service_name not in self.circuit_breakers:
            return
        
        breaker = self.circuit_breakers[service_name]
        old_state = breaker.state
        
        breaker.state = new_state
        breaker.state_changed_at = datetime.now(timezone.utc)
        
        logger.info(f"Circuit breaker {service_name} transitioned from {old_state.value} to {new_state.value}")
        
        # Call recovery callback if available
        if (new_state == CircuitBreakerState.CLOSED and 
            service_name in self.circuit_breaker_callbacks):
            try:
                await self.circuit_breaker_callbacks[service_name]()
            except Exception as e:
                logger.error(f"Error in circuit breaker recovery callback: {str(e)}")
    
    async def _update_retry_statistics(self, event_type: str, execution: RetryExecution):
        """Update retry statistics"""
        stats = self.retry_statistics[event_type]
        stats["attempts"] += len(execution.attempts)
        
        if execution.final_success:
            stats["successes"] += 1
        else:
            stats["failures"] += 1
    
    def _calculate_success_rate(self, stats: Dict[str, int]) -> float:
        """Calculate success rate from statistics"""
        total = stats.get("successes", 0) + stats.get("failures", 0)
        if total == 0:
            return 100.0
        return (stats.get("successes", 0) / total) * 100
    
    async def _handle_dead_letter(self, message_id: str, event_type: str, error: str, execution: RetryExecution):
        """Handle message that failed all retries"""
        dead_letter_entry = {
            "message_id": message_id,
            "event_type": event_type,
            "error": error,
            "attempts": len(execution.attempts),
            "error_category": execution.error_category.value if execution.error_category else "unknown",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "total_duration": execution.total_duration,
            "policy": {
                "max_attempts": execution.policy.max_attempts,
                "backoff_strategy": execution.policy.backoff_strategy.value
            }
        }
        
        self.dead_letter_queue.append(dead_letter_entry)
        
        logger.warning(f"Message {message_id} moved to dead letter queue after {len(execution.attempts)} attempts")
    
    # Configuration methods
    
    def register_custom_retry_policy(self, event_type: str, policy: RetryPolicy):
        """Register custom retry policy for event type"""
        self.custom_retry_policies[event_type] = policy
        logger.info(f"Registered custom retry policy for {event_type}")
    
    def register_error_classifier(self, classifier_name: str, classifier_func: Callable[[str], ErrorCategory]):
        """Register custom error classifier"""
        self.error_classifiers[classifier_name] = classifier_func
        logger.info(f"Registered error classifier: {classifier_name}")


# Export for public API
__all__ = [
    "RetryResilienceEngine",
    "RetryPolicy",
    "RetryExecution",
    "RetryAttempt",
    "CircuitBreakerMetrics",
    "BackoffStrategy",
    "ErrorCategory",
    "CircuitBreakerState",
    "AinflueBusiness"
]