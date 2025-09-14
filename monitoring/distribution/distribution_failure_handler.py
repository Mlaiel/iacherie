"""
Distribution Failure Handler - Distribution Module
================================================

Advanced failure handling and recovery system for content distribution
across multiple platforms with intelligent retry mechanisms and incident management.

Features:
- Intelligent failure detection and classification
- Automated retry strategies with exponential backoff
- Circuit breaker pattern implementation
- Failure pattern analysis and prediction
- Incident escalation and notification
- Recovery optimization and learning

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Set, Callable
from dataclasses import dataclass, field
from enum import Enum
import uuid
import json
from collections import defaultdict, deque

logger = logging.getLogger(__name__)

class FailureType(Enum):
    """Types of distribution failures"""
    NETWORK_ERROR = "network_error"
    AUTHENTICATION_FAILED = "authentication_failed"
    RATE_LIMIT_EXCEEDED = "rate_limit_exceeded"
    CONTENT_REJECTED = "content_rejected"
    FORMAT_ERROR = "format_error"
    QUOTA_EXCEEDED = "quota_exceeded"
    PLATFORM_UNAVAILABLE = "platform_unavailable"
    TIMEOUT = "timeout"
    UNKNOWN_ERROR = "unknown_error"

class FailureSeverity(Enum):
    """Failure severity levels"""
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4
    CATASTROPHIC = 5

class RetryStrategy(Enum):
    """Retry strategy types"""
    EXPONENTIAL_BACKOFF = "exponential_backoff"
    FIXED_INTERVAL = "fixed_interval"
    IMMEDIATE = "immediate"
    MANUAL = "manual"
    CIRCUIT_BREAKER = "circuit_breaker"

class CircuitState(Enum):
    """Circuit breaker states"""
    CLOSED = "closed"      # Normal operation
    OPEN = "open"          # Failing fast
    HALF_OPEN = "half_open"  # Testing recovery

@dataclass
class DistributionFailure:
    """Distribution failure record"""
    failure_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    content_id: str = ""
    platform: str = ""
    failure_type: FailureType = FailureType.UNKNOWN_ERROR
    severity: FailureSeverity = FailureSeverity.MEDIUM
    error_message: str = ""
    error_code: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.now)
    context: Dict[str, Any] = field(default_factory=dict)
    stack_trace: Optional[str] = None
    retry_count: int = 0
    resolved: bool = False
    resolution_time: Optional[datetime] = None

@dataclass
class RetryAttempt:
    """Retry attempt record"""
    attempt_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    failure_id: str = ""
    attempt_number: int = 1
    scheduled_at: datetime = field(default_factory=datetime.now)
    executed_at: Optional[datetime] = None
    success: bool = False
    error_message: Optional[str] = None
    duration_seconds: float = 0.0

@dataclass
class CircuitBreaker:
    """Circuit breaker for platform/service protection"""
    name: str = ""
    state: CircuitState = CircuitState.CLOSED
    failure_threshold: int = 5
    recovery_timeout_seconds: int = 60
    last_failure_time: Optional[datetime] = None
    failure_count: int = 0
    success_count: int = 0
    state_changed_at: datetime = field(default_factory=datetime.now)

@dataclass
class FailurePattern:
    """Detected failure pattern"""
    pattern_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    pattern_type: str = ""  # "time_based", "platform_based", "content_based"
    description: str = ""
    failure_count: int = 0
    first_occurrence: datetime = field(default_factory=datetime.now)
    last_occurrence: datetime = field(default_factory=datetime.now)
    confidence_score: float = 0.0
    suggested_action: str = ""

class DistributionFailureHandler:
    """Main distribution failure handling system"""
    
    def __init__(self) -> None:
        self.failures: List[DistributionFailure] = []
        self.retry_attempts: List[RetryAttempt] = []
        self.circuit_breakers: Dict[str, CircuitBreaker] = {}
        self.failure_patterns: List[FailurePattern] = []
        self.retry_strategies: Dict[FailureType, RetryStrategy] = self._initialize_retry_strategies()
        self.notification_handlers: List[Callable] = []
        self.recovery_callbacks: Dict[str, Callable] = {}
        
        # Configuration
        self.max_retry_attempts = 5
        self.base_retry_delay = 1.0  # seconds
        self.max_retry_delay = 300.0  # 5 minutes
        self.pattern_detection_window = timedelta(hours=24)
        
    def _initialize_retry_strategies(self) -> Dict[FailureType, RetryStrategy]:
        """Initialize default retry strategies for different failure types"""
        return {
            FailureType.NETWORK_ERROR: RetryStrategy.EXPONENTIAL_BACKOFF,
            FailureType.RATE_LIMIT_EXCEEDED: RetryStrategy.EXPONENTIAL_BACKOFF,
            FailureType.TIMEOUT: RetryStrategy.EXPONENTIAL_BACKOFF,
            FailureType.PLATFORM_UNAVAILABLE: RetryStrategy.EXPONENTIAL_BACKOFF,
            FailureType.AUTHENTICATION_FAILED: RetryStrategy.MANUAL,
            FailureType.CONTENT_REJECTED: RetryStrategy.MANUAL,
            FailureType.FORMAT_ERROR: RetryStrategy.MANUAL,
            FailureType.QUOTA_EXCEEDED: RetryStrategy.CIRCUIT_BREAKER,
            FailureType.UNKNOWN_ERROR: RetryStrategy.FIXED_INTERVAL
        }
        
    async def handle_failure(self, 
                           content_id: str,
                           platform: str,
                           error: Exception,
                           context: Dict[str, Any] = None) -> DistributionFailure:
        """Handle a distribution failure"""
        # Classify the failure
        failure_type = self._classify_failure(error)
        severity = self._assess_severity(failure_type, context or {})
        
        # Create failure record
        failure = DistributionFailure(
            content_id=content_id,
            platform=platform,
            failure_type=failure_type,
            severity=severity,
            error_message=str(error),
            error_code=getattr(error, 'code', None),
            context=context or {},
            stack_trace=self._get_stack_trace(error)
        )
        
        self.failures.append(failure)
        
        # Update circuit breaker
        await self._update_circuit_breaker(platform, failure_type, success=False)
        
        # Determine retry strategy
        retry_strategy = self.retry_strategies.get(failure_type, RetryStrategy.EXPONENTIAL_BACKOFF)
        
        # Schedule retry if appropriate
        if await self._should_retry(failure, retry_strategy):
            await self._schedule_retry(failure, retry_strategy)
            
        # Send notifications for high severity failures
        if severity.value >= FailureSeverity.HIGH.value:
            await self._send_failure_notification(failure)
            
        # Detect patterns
        await self._detect_failure_patterns()
        
        logger.warning(f"Distribution failure handled: {failure.failure_id}")
        return failure
        
    def _classify_failure(self, error: Exception) -> FailureType:
        """Classify the type of failure based on error"""
        error_message = str(error).lower()
        
        if "network" in error_message or "connection" in error_message:
            return FailureType.NETWORK_ERROR
        elif "auth" in error_message or "unauthorized" in error_message:
            return FailureType.AUTHENTICATION_FAILED
        elif "rate limit" in error_message or "too many requests" in error_message:
            return FailureType.RATE_LIMIT_EXCEEDED
        elif "timeout" in error_message:
            return FailureType.TIMEOUT
        elif "quota" in error_message or "limit exceeded" in error_message:
            return FailureType.QUOTA_EXCEEDED
        elif "rejected" in error_message or "not allowed" in error_message:
            return FailureType.CONTENT_REJECTED
        elif "format" in error_message or "encoding" in error_message:
            return FailureType.FORMAT_ERROR
        elif "unavailable" in error_message or "service down" in error_message:
            return FailureType.PLATFORM_UNAVAILABLE
        else:
            return FailureType.UNKNOWN_ERROR
            
    def _assess_severity(self, failure_type: FailureType, context: Dict[str, Any]) -> FailureSeverity:
        """Assess the severity of a failure"""
        # Base severity for each failure type
        base_severity = {
            FailureType.NETWORK_ERROR: FailureSeverity.MEDIUM,
            FailureType.AUTHENTICATION_FAILED: FailureSeverity.HIGH,
            FailureType.RATE_LIMIT_EXCEEDED: FailureSeverity.MEDIUM,
            FailureType.CONTENT_REJECTED: FailureSeverity.HIGH,
            FailureType.FORMAT_ERROR: FailureSeverity.MEDIUM,
            FailureType.QUOTA_EXCEEDED: FailureSeverity.HIGH,
            FailureType.PLATFORM_UNAVAILABLE: FailureSeverity.CRITICAL,
            FailureType.TIMEOUT: FailureSeverity.MEDIUM,
            FailureType.UNKNOWN_ERROR: FailureSeverity.MEDIUM
        }
        
        severity = base_severity.get(failure_type, FailureSeverity.MEDIUM)
        
        # Adjust based on context
        if context.get('is_live_content', False):
            severity = FailureSeverity(min(5, severity.value + 1))
        if context.get('retry_count', 0) > 3:
            severity = FailureSeverity(min(5, severity.value + 1))
        if context.get('affected_users', 0) > 1000:
            severity = FailureSeverity(min(5, severity.value + 1))
            
        return severity
        
    def _get_stack_trace(self, error: Exception) -> Optional[str]:
        """Extract stack trace from exception"""
        import traceback
        try:
            return traceback.format_exc()
        except:
            return None
            
    async def _update_circuit_breaker(self, platform -> None: str, failure_type -> None: FailureType, success -> None: bool) -> None:
        """Update circuit breaker state"""
        breaker_key = f"{platform}_{failure_type.value}"
        
        if breaker_key not in self.circuit_breakers:
            self.circuit_breakers[breaker_key] = CircuitBreaker(
                name=breaker_key,
                failure_threshold=5,
                recovery_timeout_seconds=60
            )
            
        breaker = self.circuit_breakers[breaker_key]
        
        if success:
            breaker.success_count += 1
            breaker.failure_count = 0  # Reset failure count on success
            
            # Close circuit if it was open/half-open
            if breaker.state != CircuitState.CLOSED:
                breaker.state = CircuitState.CLOSED
                breaker.state_changed_at = datetime.now()
                logger.info(f"Circuit breaker closed: {breaker_key}")
        else:
            breaker.failure_count += 1
            breaker.last_failure_time = datetime.now()
            
            # Open circuit if failure threshold exceeded
            if breaker.failure_count >= breaker.failure_threshold and breaker.state == CircuitState.CLOSED:
                breaker.state = CircuitState.OPEN
                breaker.state_changed_at = datetime.now()
                logger.warning(f"Circuit breaker opened: {breaker_key}")
                
        # Check if we should move from OPEN to HALF_OPEN
        if breaker.state == CircuitState.OPEN and breaker.last_failure_time:
            if datetime.now() - breaker.last_failure_time > timedelta(seconds=breaker.recovery_timeout_seconds):
                breaker.state = CircuitState.HALF_OPEN
                breaker.state_changed_at = datetime.now()
                logger.info(f"Circuit breaker half-opened: {breaker_key}")
                
    async def _should_retry(self, failure: DistributionFailure, retry_strategy: RetryStrategy) -> bool:
        """Determine if a failure should be retried"""
        if failure.retry_count >= self.max_retry_attempts:
            return False
            
        if retry_strategy == RetryStrategy.MANUAL:
            return False
            
        if retry_strategy == RetryStrategy.CIRCUIT_BREAKER:
            breaker_key = f"{failure.platform}_{failure.failure_type.value}"
            breaker = self.circuit_breakers.get(breaker_key)
            if breaker and breaker.state == CircuitState.OPEN:
                return False
                
        # Don't retry certain high-severity failures
        if failure.severity in [FailureSeverity.CRITICAL, FailureSeverity.CATASTROPHIC]:
            return False
            
        return True
        
    async def _schedule_retry(self, failure -> None: DistributionFailure, retry_strategy -> None: RetryStrategy) -> None:
        """Schedule a retry attempt"""
        delay = self._calculate_retry_delay(failure.retry_count, retry_strategy)
        scheduled_time = datetime.now() + timedelta(seconds=delay)
        
        retry_attempt = RetryAttempt(
            failure_id=failure.failure_id,
            attempt_number=failure.retry_count + 1,
            scheduled_at=scheduled_time
        )
        
        self.retry_attempts.append(retry_attempt)
        
        # Schedule the actual retry
        asyncio.create_task(self._execute_retry_after_delay(delay, failure, retry_attempt))
        
        logger.info(f"Retry scheduled for {failure.failure_id} in {delay} seconds")
        
    def _calculate_retry_delay(self, retry_count: int, strategy: RetryStrategy) -> float:
        """Calculate delay before next retry attempt"""
        if strategy == RetryStrategy.IMMEDIATE:
            return 0.0
        elif strategy == RetryStrategy.FIXED_INTERVAL:
            return self.base_retry_delay
        elif strategy == RetryStrategy.EXPONENTIAL_BACKOFF:
            delay = self.base_retry_delay * (2 ** retry_count)
            return min(delay, self.max_retry_delay)
        else:
            return self.base_retry_delay
            
    async def _execute_retry_after_delay(self, 
                                       delay -> None: float, 
                                       failure -> None: DistributionFailure, 
                                       retry_attempt -> None: RetryAttempt) -> None:
        """Execute retry after specified delay"""
        await asyncio.sleep(delay)
        await self._execute_retry(failure, retry_attempt)
        
    async def _execute_retry(self, failure -> None: DistributionFailure, retry_attempt -> None: RetryAttempt) -> None:
        """Execute a retry attempt"""
        retry_attempt.executed_at = datetime.now()
        start_time = datetime.now()
        
        try:
            # Check circuit breaker
            breaker_key = f"{failure.platform}_{failure.failure_type.value}"
            breaker = self.circuit_breakers.get(breaker_key)
            if breaker and breaker.state == CircuitState.OPEN:
                raise Exception("Circuit breaker is open")
                
            # Execute the retry logic
            success = await self._attempt_redistribution(failure)
            
            if success:
                retry_attempt.success = True
                failure.resolved = True
                failure.resolution_time = datetime.now()
                failure.retry_count += 1
                
                # Update circuit breaker
                await self._update_circuit_breaker(failure.platform, failure.failure_type, success=True)
                
                # Notify recovery
                await self._send_recovery_notification(failure)
                
                logger.info(f"Retry successful for failure: {failure.failure_id}")
            else:
                raise Exception("Redistribution failed")
                
        except Exception as e:
            retry_attempt.success = False
            retry_attempt.error_message = str(e)
            failure.retry_count += 1
            
            # Update circuit breaker
            await self._update_circuit_breaker(failure.platform, failure.failure_type, success=False)
            
            # Schedule another retry if appropriate
            retry_strategy = self.retry_strategies.get(failure.failure_type, RetryStrategy.EXPONENTIAL_BACKOFF)
            if await self._should_retry(failure, retry_strategy):
                await self._schedule_retry(failure, retry_strategy)
            else:
                logger.error(f"Retry failed and no more retries scheduled: {failure.failure_id}")
                
        finally:
            retry_attempt.duration_seconds = (datetime.now() - start_time).total_seconds()
            
    async def _attempt_redistribution(self, failure: DistributionFailure) -> bool:
        """Attempt to redistribute content (mock implementation)"""
        # This would contain the actual redistribution logic
        # For now, simulate with random success/failure
        import random
        
        # Simulate network delay
        await asyncio.sleep(random.uniform(0.1, 1.0))
        
        # Higher success rate for subsequent attempts
        success_probability = 0.3 + (failure.retry_count * 0.2)
        return random.random() < success_probability
        
    async def _send_failure_notification(self, failure -> None: DistributionFailure) -> None:
        """Send failure notification to registered handlers"""
        notification_data = {
            'type': 'failure',
            'failure_id': failure.failure_id,
            'content_id': failure.content_id,
            'platform': failure.platform,
            'failure_type': failure.failure_type.value,
            'severity': failure.severity.value,
            'error_message': failure.error_message,
            'timestamp': failure.timestamp.isoformat()
        }
        
        for handler in self.notification_handlers:
            try:
                await handler(notification_data)
            except Exception as e:
                logger.error(f"Notification handler failed: {e}")
                
    async def _send_recovery_notification(self, failure -> None: DistributionFailure) -> None:
        """Send recovery notification"""
        notification_data = {
            'type': 'recovery',
            'failure_id': failure.failure_id,
            'content_id': failure.content_id,
            'platform': failure.platform,
            'retry_count': failure.retry_count,
            'resolution_time': failure.resolution_time.isoformat() if failure.resolution_time else None
        }
        
        for handler in self.notification_handlers:
            try:
                await handler(notification_data)
            except Exception as e:
                logger.error(f"Recovery notification handler failed: {e}")
                
    async def _detect_failure_patterns(self) -> None:
        """Detect patterns in failures"""
        if len(self.failures) < 10:  # Need minimum data
            return
            
        cutoff_time = datetime.now() - self.pattern_detection_window
        recent_failures = [f for f in self.failures if f.timestamp > cutoff_time]
        
        # Pattern 1: Platform-based failures
        platform_failures = defaultdict(list)
        for failure in recent_failures:
            platform_failures[failure.platform].append(failure)
            
        for platform, failures in platform_failures.items():
            if len(failures) >= 5:  # Pattern threshold
                pattern = FailurePattern(
                    pattern_type="platform_based",
                    description=f"High failure rate on {platform}",
                    failure_count=len(failures),
                    first_occurrence=min(f.timestamp for f in failures),
                    last_occurrence=max(f.timestamp for f in failures),
                    confidence_score=min(1.0, len(failures) / 10.0),
                    suggested_action=f"Investigate {platform} API status"
                )
                
                # Check if pattern already exists
                existing = any(p.pattern_type == "platform_based" and platform in p.description 
                             for p in self.failure_patterns)
                if not existing:
                    self.failure_patterns.append(pattern)
                    logger.warning(f"Failure pattern detected: {pattern.description}")
                    
        # Pattern 2: Time-based failures
        hour_failures = defaultdict(list)
        for failure in recent_failures:
            hour = failure.timestamp.hour
            hour_failures[hour].append(failure)
            
        for hour, failures in hour_failures.items():
            if len(failures) >= 3:
                pattern = FailurePattern(
                    pattern_type="time_based",
                    description=f"High failure rate at hour {hour}",
                    failure_count=len(failures),
                    first_occurrence=min(f.timestamp for f in failures),
                    last_occurrence=max(f.timestamp for f in failures),
                    confidence_score=min(1.0, len(failures) / 5.0),
                    suggested_action=f"Check system load during hour {hour}"
                )
                
                existing = any(p.pattern_type == "time_based" and f"hour {hour}" in p.description 
                             for p in self.failure_patterns)
                if not existing:
                    self.failure_patterns.append(pattern)
                    
    def get_failure_statistics(self) -> Dict[str, Any]:
        """Get comprehensive failure statistics"""
        if not self.failures:
            return {'total_failures': 0}
            
        # Calculate time ranges
        last_24h = datetime.now() - timedelta(hours=24)
        last_7d = datetime.now() - timedelta(days=7)
        
        recent_failures_24h = [f for f in self.failures if f.timestamp > last_24h]
        recent_failures_7d = [f for f in self.failures if f.timestamp > last_7d]
        
        # Failure type distribution
        failure_type_counts = defaultdict(int)
        for failure in self.failures:
            failure_type_counts[failure.failure_type.value] += 1
            
        # Platform failure distribution
        platform_failure_counts = defaultdict(int)
        for failure in self.failures:
            platform_failure_counts[failure.platform] += 1
            
        # Resolution statistics
        resolved_failures = [f for f in self.failures if f.resolved]
        total_retry_attempts = sum(len([r for r in self.retry_attempts if r.failure_id == f.failure_id]) 
                                 for f in self.failures)
        
        # Average resolution time
        resolution_times = []
        for failure in resolved_failures:
            if failure.resolution_time:
                resolution_time = (failure.resolution_time - failure.timestamp).total_seconds()
                resolution_times.append(resolution_time)
                
        avg_resolution_time = sum(resolution_times) / len(resolution_times) if resolution_times else 0
        
        # Circuit breaker status
        circuit_breaker_status = {}
        for name, breaker in self.circuit_breakers.items():
            circuit_breaker_status[name] = {
                'state': breaker.state.value,
                'failure_count': breaker.failure_count,
                'success_count': breaker.success_count
            }
            
        return {
            'total_failures': len(self.failures),
            'resolved_failures': len(resolved_failures),
            'resolution_rate': len(resolved_failures) / len(self.failures),
            'failures_last_24h': len(recent_failures_24h),
            'failures_last_7d': len(recent_failures_7d),
            'failure_type_distribution': dict(failure_type_counts),
            'platform_failure_distribution': dict(platform_failure_counts),
            'total_retry_attempts': total_retry_attempts,
            'average_resolution_time_seconds': avg_resolution_time,
            'active_patterns': len(self.failure_patterns),
            'circuit_breaker_status': circuit_breaker_status
        }
        
    def register_notification_handler(self, handler -> None: Callable) -> None:
        """Register a notification handler for failures and recoveries"""
        self.notification_handlers.append(handler)
        
    def register_recovery_callback(self, platform -> None: str, callback -> None: Callable) -> None:
        """Register a recovery callback for specific platform"""
        self.recovery_callbacks[platform] = callback

# Export main classes
__all__ = [
    'DistributionFailureHandler',
    'DistributionFailure',
    'RetryAttempt',
    'CircuitBreaker',
    'FailurePattern',
    'FailureType',
    'FailureSeverity',
    'RetryStrategy',
    'CircuitState'
]