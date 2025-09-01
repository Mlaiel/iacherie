"""Error Recovery Manager
=====================

Advanced error recovery and fault tolerance system for crawler operations.
Provides intelligent retry logic, circuit breaker patterns, and automated recovery.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: All rights reserved. Unauthorized use, reproduction, or distribution prohibited.
"""

import asyncio
import json
import logging
import time
import random
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Callable, Union, Set, Tuple
from dataclasses import dataclass, field, asdict
from enum import Enum
import hashlib
import pickle
from collections import defaultdict, deque
import traceback
import sys

from ..config.recovery_config import RecoveryConfig
from ..utils.circuit_breaker import CircuitBreaker
from ..utils.backoff_strategy import BackoffStrategy
from ...core.database import get_database_session
from ...core.logging import get_logger
from ...models.error_log import ErrorLog, RecoveryAction
from ...monitoring.metrics_collector import MetricsCollector


class ErrorSeverity(Enum):
    """
Error severity levels."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ErrorCategory(Enum):
    """Error category classification."""

    NETWORK = "network"
    AUTHENTICATION = "authentication"
    RATE_LIMIT = "rate_limit"
    PARSING = "parsing"
    VALIDATION = "validation"
    TIMEOUT = "timeout"
    SERVER_ERROR = "server_error"
    CLIENT_ERROR = "client_error"
    RESOURCE = "resource"
    CONFIGURATION = "configuration"
    UNKNOWN = "unknown"


class RecoveryStrategy(Enum):
    """Recovery strategy types."""

    IMMEDIATE_RETRY = "immediate_retry"
    EXPONENTIAL_BACKOFF = "exponential_backoff"
    LINEAR_BACKOFF = "linear_backoff"
    JITTERED_BACKOFF = "jittered_backoff"
    CIRCUIT_BREAKER = "circuit_breaker"
    FAILOVER = "failover"
    DEGRADED_MODE = "degraded_mode"
    MANUAL_INTERVENTION = "manual_intervention"
    SKIP = "skip"


class RecoveryStatus(Enum):
    """Recovery attempt status."""

    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    SUCCESSFUL = "successful"
    FAILED = "failed"
    EXHAUSTED = "exhausted"
    ABANDONED = "abandoned"


@dataclass
class ErrorContext:
    """Error context information."""
    error_id: str
    operation: str
    url: Optional[str]
    timestamp: datetime
    error_type: str
    error_message: str
    stack_trace: Optional[str]
    severity: ErrorSeverity
    category: ErrorCategory
    metadata: Dict[str, Any] = field(default_factory=dict)
    retry_count: int = 0
    max_retries: int = 3
    recovery_strategy: RecoveryStrategy = RecoveryStrategy.EXPONENTIAL_BACKOFF
    recovery_status: RecoveryStatus = RecoveryStatus.PENDING


@dataclass
class RecoveryAttempt:
    """
Recovery attempt record."""
    attempt_id: str
    error_id: str
    strategy: RecoveryStrategy
    started_at: datetime
    completed_at: Optional[datetime] = None
    status: RecoveryStatus = RecoveryStatus.PENDING
    result: Optional[Any] = None
    error_message: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class RecoveryMetrics:
    """
Recovery system metrics."""
    total_errors: int = 0
    recovered_errors: int = 0
    failed_recoveries: int = 0
    recovery_success_rate: float = 0.0
    average_recovery_time: float = 0.0
    errors_by_category: Dict[str, int] = field(default_factory=dict)
    errors_by_severity: Dict[str, int] = field(default_factory=dict)
    recovery_by_strategy: Dict[str, int] = field(default_factory=dict)
    last_updated: datetime = field(default_factory=datetime.utcnow)


class ErrorClassifier:
    """
    Intelligent error classification system.
    """
    
    def __init__(self):
        """
Initialize error classifier."""
        self.logger = get_logger(self.__class__.__name__)
        
        # Classification patterns
        self.network_patterns = [
            'connection', 'timeout', 'dns', 'socket', 'network',
            'unreachable', 'connection refused', 'connection reset'
        ]
        
        self.auth_patterns = [
            'unauthorized', 'forbidden', 'authentication', 'token',
            'credential', 'login', 'permission', 'access denied'
        ]
        
        self.rate_limit_patterns = [
            'rate limit', 'too many requests', 'quota exceeded',
            'throttled', 'rate exceeded', '429'
        ]
        
        self.server_error_patterns = [
            'internal server error', '500', '502', '503', '504',
            'bad gateway', 'service unavailable', 'gateway timeout'
        ]
        
        self.client_error_patterns = [
            '400', '401', '403', '404', '405', '406', '408', '409',
            'bad request', 'not found', 'method not allowed'
        ]
        
    def classify_error(self, error: Exception, context: Dict[str, Any] = None) -> Tuple[ErrorCategory, ErrorSeverity]:
        """
Classify error by category and severity."""
        try:
            error_message = str(error).lower()
            error_type = type(error).__name__.lower()
            
            # Determine category
            category = self._determine_category(error_message, error_type, context)
            
            # Determine severity
            severity = self._determine_severity(error, category, context)
            
            return category, severity
            
        except Exception as e:
            self.logger.error(f"Error classification failed: {e}")
            return ErrorCategory.UNKNOWN, ErrorSeverity.MEDIUM
            
    def _determine_category(self, error_message: str, error_type: str, context: Dict[str, Any] = None) -> ErrorCategory:
        """Determine error category."""
        # Network errors
        if any(pattern in error_message for pattern in self.network_patterns):
            return ErrorCategory.NETWORK
            
        # Authentication errors
        if any(pattern in error_message for pattern in self.auth_patterns):
            return ErrorCategory.AUTHENTICATION
            
        # Rate limiting
        if any(pattern in error_message for pattern in self.rate_limit_patterns):
            return ErrorCategory.RATE_LIMIT
            
        # Server errors
        if any(pattern in error_message for pattern in self.server_error_patterns):
            return ErrorCategory.SERVER_ERROR
            
        # Client errors
        if any(pattern in error_message for pattern in self.client_error_patterns):
            return ErrorCategory.CLIENT_ERROR
            
        # Timeout errors
        if 'timeout' in error_message or 'timeout' in error_type:
            return ErrorCategory.TIMEOUT
            
        # Parsing errors
        if any(keyword in error_type for keyword in ['parse', 'json', 'xml', 'decode']):
            return ErrorCategory.PARSING
            
        # Validation errors
        if any(keyword in error_type for keyword in ['validation', 'schema', 'format']):
            return ErrorCategory.VALIDATION
            
        # Resource errors
        if any(keyword in error_message for keyword in ['memory', 'disk', 'resource', 'limit']):
            return ErrorCategory.RESOURCE
            
        return ErrorCategory.UNKNOWN
        
    def _determine_severity(self, error: Exception, category: ErrorCategory, context: Dict[str, Any] = None) -> ErrorSeverity:
        """
Determine error severity."""
        # Critical errors
        if category in [ErrorCategory.RESOURCE, ErrorCategory.CONFIGURATION]:
            return ErrorSeverity.CRITICAL
            
        # High severity errors
        if category in [ErrorCategory.AUTHENTICATION, ErrorCategory.SERVER_ERROR]:
            return ErrorSeverity.HIGH
            
        # Medium severity errors
        if category in [ErrorCategory.NETWORK, ErrorCategory.TIMEOUT, ErrorCategory.RATE_LIMIT]:
            return ErrorSeverity.MEDIUM
            
        # Low severity errors
        if category in [ErrorCategory.PARSING, ErrorCategory.VALIDATION, ErrorCategory.CLIENT_ERROR]:
            return ErrorSeverity.LOW
            
        return ErrorSeverity.MEDIUM


class RecoveryStrategySelector:
    """
    Intelligent recovery strategy selection system.
    """
    
    def __init__(self, config: RecoveryConfig):
        """
Initialize recovery strategy selector."""
        self.config = config
        self.logger = get_logger(self.__class__.__name__)
        
    def select_strategy(self, error_context: ErrorContext) -> RecoveryStrategy:
        """
Select appropriate recovery strategy."""
        try:
            category = error_context.category
            severity = error_context.severity
            retry_count = error_context.retry_count
            
            # Critical errors - manual intervention
            if severity == ErrorSeverity.CRITICAL:
                return RecoveryStrategy.MANUAL_INTERVENTION
                
            # Rate limiting - exponential backoff
            if category == ErrorCategory.RATE_LIMIT:
                return RecoveryStrategy.EXPONENTIAL_BACKOFF
                
            # Network issues - circuit breaker pattern
            if category == ErrorCategory.NETWORK and retry_count > 2:
                return RecoveryStrategy.CIRCUIT_BREAKER
                
            # Authentication - immediate retry (might be temporary)
            if category == ErrorCategory.AUTHENTICATION and retry_count == 0:
                return RecoveryStrategy.IMMEDIATE_RETRY
                
            # Server errors - jittered backoff
            if category == ErrorCategory.SERVER_ERROR:
                return RecoveryStrategy.JITTERED_BACKOFF
                
            # Timeout - linear backoff
            if category == ErrorCategory.TIMEOUT:
                return RecoveryStrategy.LINEAR_BACKOFF
                
            # Client errors - usually non-recoverable
            if category == ErrorCategory.CLIENT_ERROR:
                return RecoveryStrategy.SKIP
                
            # Parsing/validation errors - immediate retry once
            if category in [ErrorCategory.PARSING, ErrorCategory.VALIDATION]:
                if retry_count == 0:
                    return RecoveryStrategy.IMMEDIATE_RETRY
                else:
                    return RecoveryStrategy.SKIP
                    
            # Default strategy
            return RecoveryStrategy.EXPONENTIAL_BACKOFF
            
        except Exception as e:
            self.logger.error(f"Strategy selection failed: {e}")
            return RecoveryStrategy.EXPONENTIAL_BACKOFF


class ErrorRecoveryManager:
    """
    Advanced error recovery and fault tolerance system.
    
    Provides intelligent error classification, recovery strategy selection,
    circuit breaker patterns, and automated recovery mechanisms.
    """
    
    def __init__(self, config: Optional[RecoveryConfig] = None):
        """
Initialize error recovery manager."""
        self.config = config or RecoveryConfig()
        self.logger = get_logger(self.__class__.__name__)
        self.metrics_collector = MetricsCollector()
        
        # Error tracking
        self.active_errors: Dict[str, ErrorContext] = {}
        self.error_history: deque = deque(maxlen=self.config.ERROR_HISTORY_SIZE)
        self.recovery_attempts: Dict[str, List[RecoveryAttempt]] = defaultdict(list)
        
        # Recovery components
        self.error_classifier = ErrorClassifier()
        self.strategy_selector = RecoveryStrategySelector(self.config)
        self.circuit_breakers: Dict[str, CircuitBreaker] = {}
        self.backoff_strategies: Dict[str, BackoffStrategy] = {}
        
        # Recovery handlers
        self.recovery_handlers: Dict[RecoveryStrategy, Callable] = {
            RecoveryStrategy.IMMEDIATE_RETRY: self._immediate_retry,
            RecoveryStrategy.EXPONENTIAL_BACKOFF: self._exponential_backoff_retry,
            RecoveryStrategy.LINEAR_BACKOFF: self._linear_backoff_retry,
            RecoveryStrategy.JITTERED_BACKOFF: self._jittered_backoff_retry,
            RecoveryStrategy.CIRCUIT_BREAKER: self._circuit_breaker_retry,
            RecoveryStrategy.FAILOVER: self._failover_retry,
            RecoveryStrategy.DEGRADED_MODE: self._degraded_mode,
            RecoveryStrategy.SKIP: self._skip_error,
        }
        
        # Metrics
        self.metrics = RecoveryMetrics()
        
        # Background tasks
        self.monitoring_task: Optional[asyncio.Task] = None
        self.cleanup_task: Optional[asyncio.Task] = None
        self.monitoring_active = False
        
    async def start(self):
        """
Start error recovery manager."""
        try:
            self.monitoring_active = True
            
            # Start monitoring tasks
            self.monitoring_task = asyncio.create_task(self._monitoring_loop())
            self.cleanup_task = asyncio.create_task(self._cleanup_loop())
            
            self.logger.info("Error recovery manager started")
            
        except Exception as e:
            self.logger.error(f"Failed to start error recovery manager: {e}")
            raise
            
    async def handle_error(self, error: Exception, operation: str, url: Optional[str] = None, 
                          context: Dict[str, Any] = None, retry_func: Optional[Callable] = None) -> Any:
        """
        Handle an error with intelligent recovery.
        
        Args:
            error: The exception that occurred
            operation: Description of the operation that failed
            url: URL associated with the error (if applicable)
            context: Additional context information
            retry_func: Function to call for retry
            
        Returns:
            Result of successful recovery or None if recovery failed
        """
        try:
            # Create error context
            error_context = await self._create_error_context(error, operation, url, context)
            
            # Classify error
            category, severity = self.error_classifier.classify_error(error, context)
            error_context.category = category
            error_context.severity = severity
            
            # Update metrics
            self.metrics.total_errors += 1
            self.metrics.errors_by_category[category.value] = self.metrics.errors_by_category.get(category.value, 0) + 1
            self.metrics.errors_by_severity[severity.value] = self.metrics.errors_by_severity.get(severity.value, 0) + 1
            
            # Store error
            self.active_errors[error_context.error_id] = error_context
            self.error_history.append(error_context)
            
            # Log error
            await self._log_error(error_context)
            
            # Attempt recovery if retry function provided
            if retry_func:
                result = await self._attempt_recovery(error_context, retry_func)
                return result
                
            return None
            
        except Exception as e:
            self.logger.error(f"Error handling failed: {e}")
            return None
            
    async def _create_error_context(self, error: Exception, operation: str, url: Optional[str], 
                                   context: Dict[str, Any] = None) -> ErrorContext:
        """Create error context from exception."""
        error_id = f"error_{int(time.time())}_{hashlib.md5(str(error).encode()).hexdigest()[:8]}"
        
        return ErrorContext(
            error_id=error_id,
            operation=operation,
            url=url,
            timestamp=datetime.utcnow(),
            error_type=type(error).__name__,
            error_message=str(error),
            stack_trace=traceback.format_exc(),
            severity=ErrorSeverity.MEDIUM,  # Will be updated by classifier
            category=ErrorCategory.UNKNOWN,  # Will be updated by classifier
            metadata=context or {},
            max_retries=self.config.DEFAULT_MAX_RETRIES
        )
        
    async def _attempt_recovery(self, error_context: ErrorContext, retry_func: Callable) -> Any:
        """Attempt to recover from error."""
        try:
            # Check if max retries exceeded
            if error_context.retry_count >= error_context.max_retries:
                error_context.recovery_status = RecoveryStatus.EXHAUSTED
                self.logger.warning(f"Max retries exceeded for error {error_context.error_id}")
                return None
                
            # Select recovery strategy
            strategy = self.strategy_selector.select_strategy(error_context)
            error_context.recovery_strategy = strategy
            
            # Create recovery attempt
            attempt = RecoveryAttempt(
                attempt_id=f"attempt_{error_context.error_id}_{error_context.retry_count}",
                error_id=error_context.error_id,
                strategy=strategy,
                started_at=datetime.utcnow()
            )
            
            self.recovery_attempts[error_context.error_id].append(attempt)
            
            # Update metrics
            self.metrics.recovery_by_strategy[strategy.value] = self.metrics.recovery_by_strategy.get(strategy.value, 0) + 1
            
            # Execute recovery
            handler = self.recovery_handlers.get(strategy)
            if handler:
                error_context.recovery_status = RecoveryStatus.IN_PROGRESS
                attempt.status = RecoveryStatus.IN_PROGRESS
                
                result = await handler(error_context, retry_func, attempt)
                
                if result is not None:
                    # Recovery successful
                    error_context.recovery_status = RecoveryStatus.SUCCESSFUL
                    attempt.status = RecoveryStatus.SUCCESSFUL
                    attempt.completed_at = datetime.utcnow()
                    attempt.result = result
                    
                    # Update metrics
                    self.metrics.recovered_errors += 1
                    
                    # Calculate recovery time
                    recovery_time = (attempt.completed_at - attempt.started_at).total_seconds()
                    self._update_average_recovery_time(recovery_time)
                    
                    # Remove from active errors
                    if error_context.error_id in self.active_errors:
                        del self.active_errors[error_context.error_id]
                        
                    self.logger.info(f"Error {error_context.error_id} recovered using {strategy.value}")
                    return result
                else:
                    # Recovery failed
                    error_context.recovery_status = RecoveryStatus.FAILED
                    attempt.status = RecoveryStatus.FAILED
                    attempt.completed_at = datetime.utcnow()
                    
                    # Increment retry count
                    error_context.retry_count += 1
                    
                    self.logger.warning(f"Recovery attempt failed for error {error_context.error_id}")
                    
            return None
            
        except Exception as e:
            self.logger.error(f"Recovery attempt failed: {e}")
            error_context.recovery_status = RecoveryStatus.FAILED
            return None
            
    async def _immediate_retry(self, error_context: ErrorContext, retry_func: Callable, 
                             attempt: RecoveryAttempt) -> Any:
        """Immediate retry strategy."""
        try:
            self.logger.info(f"Immediate retry for error {error_context.error_id}")
            result = await retry_func()
            return result
            
        except Exception as e:
            attempt.error_message = str(e)
            return None
            
    async def _exponential_backoff_retry(self, error_context: ErrorContext, retry_func: Callable, 
                                       attempt: RecoveryAttempt) -> Any:
        """Exponential backoff retry strategy."""
        try:
            # Calculate backoff delay
            base_delay = self.config.BASE_BACKOFF_DELAY
            max_delay = self.config.MAX_BACKOFF_DELAY
            
            delay = min(base_delay * (2 ** error_context.retry_count), max_delay)
            
            self.logger.info(f"Exponential backoff retry for error {error_context.error_id}, delay: {delay}s")
            
            await asyncio.sleep(delay)
            result = await retry_func()
            return result
            
        except Exception as e:
            attempt.error_message = str(e)
            return None
            
    async def _linear_backoff_retry(self, error_context: ErrorContext, retry_func: Callable, 
                                  attempt: RecoveryAttempt) -> Any:
        """Linear backoff retry strategy."""
        try:
            # Calculate linear delay
            delay = self.config.BASE_BACKOFF_DELAY * (error_context.retry_count + 1)
            delay = min(delay, self.config.MAX_BACKOFF_DELAY)
            
            self.logger.info(f"Linear backoff retry for error {error_context.error_id}, delay: {delay}s")
            
            await asyncio.sleep(delay)
            result = await retry_func()
            return result
            
        except Exception as e:
            attempt.error_message = str(e)
            return None
            
    async def _jittered_backoff_retry(self, error_context: ErrorContext, retry_func: Callable, 
                                    attempt: RecoveryAttempt) -> Any:
        """Jittered backoff retry strategy."""
        try:
            # Calculate jittered delay
            base_delay = self.config.BASE_BACKOFF_DELAY * (2 ** error_context.retry_count)
            jitter = random.uniform(0, 0.1) * base_delay
            delay = min(base_delay + jitter, self.config.MAX_BACKOFF_DELAY)
            
            self.logger.info(f"Jittered backoff retry for error {error_context.error_id}, delay: {delay:.2f}s")
            
            await asyncio.sleep(delay)
            result = await retry_func()
            return result
            
        except Exception as e:
            attempt.error_message = str(e)
            return None
            
    async def _circuit_breaker_retry(self, error_context: ErrorContext, retry_func: Callable, 
                                   attempt: RecoveryAttempt) -> Any:
        """Circuit breaker retry strategy."""
        try:
            # Get or create circuit breaker for this operation
            circuit_key = f"{error_context.operation}:{error_context.url or 'global'}"
            
            if circuit_key not in self.circuit_breakers:
                self.circuit_breakers[circuit_key] = CircuitBreaker(
                    failure_threshold=self.config.CIRCUIT_BREAKER_FAILURE_THRESHOLD,
                    recovery_timeout=self.config.CIRCUIT_BREAKER_RECOVERY_TIMEOUT,
                    expected_exception=Exception
                )
                
            circuit_breaker = self.circuit_breakers[circuit_key]
            
            # Check circuit breaker state
            if circuit_breaker.state == 'open':
                attempt.error_message = "Circuit breaker is open"
                return None
                
            self.logger.info(f"Circuit breaker retry for error {error_context.error_id}")
            
            # Execute with circuit breaker
            result = await circuit_breaker.call(retry_func)
            return result
            
        except Exception as e:
            attempt.error_message = str(e)
            return None
            
    async def _failover_retry(self, error_context: ErrorContext, retry_func: Callable, 
                            attempt: RecoveryAttempt) -> Any:
        """Failover retry strategy."""
        try:
            # Failover logic would depend on specific implementation
            # This is a placeholder
            self.logger.info(f"Failover retry for error {error_context.error_id}")
            
            # Try alternative endpoints or methods
            # Implementation would be specific to the operation
            
            return None
            
        except Exception as e:
            attempt.error_message = str(e)
            return None
            
    async def _degraded_mode(self, error_context: ErrorContext, retry_func: Callable, 
                           attempt: RecoveryAttempt) -> Any:
        """Degraded mode strategy."""
        try:
            # Switch to degraded mode operation
            self.logger.info(f"Degraded mode for error {error_context.error_id}")
            
            # Return partial result or simplified operation
            # Implementation would be specific to the operation
            
            return {"status": "degraded", "error": error_context.error_message}
            
        except Exception as e:
            attempt.error_message = str(e)
            return None
            
    async def _skip_error(self, error_context: ErrorContext, retry_func: Callable, 
                         attempt: RecoveryAttempt) -> Any:
        """Skip error strategy."""
        self.logger.info(f"Skipping error {error_context.error_id}")
        error_context.recovery_status = RecoveryStatus.ABANDONED
        attempt.status = RecoveryStatus.ABANDONED
        return None
        
    def _update_average_recovery_time(self, recovery_time: float):
        """Update average recovery time metric."""
        if self.metrics.recovered_errors == 1:
            self.metrics.average_recovery_time = recovery_time
        else:
            current_avg = self.metrics.average_recovery_time
            self.metrics.average_recovery_time = (
                (current_avg * (self.metrics.recovered_errors - 1) + recovery_time) / 
                self.metrics.recovered_errors
            )
            
    async def _log_error(self, error_context: ErrorContext):
        """
Log error to database."""
        try:
            if self.config.ENABLE_DATABASE_LOGGING:
                async with get_database_session() as db:
                    error_log = ErrorLog(
                        error_id=error_context.error_id,
                        operation=error_context.operation,
                        url=error_context.url,
                        error_type=error_context.error_type,
                        error_message=error_context.error_message,
                        stack_trace=error_context.stack_trace,
                        severity=error_context.severity.value,
                        category=error_context.category.value,
                        metadata=error_context.metadata,
                        timestamp=error_context.timestamp
                    )
                    
                    db.add(error_log)
                    await db.commit()
                    
        except Exception as e:
            self.logger.error(f"Failed to log error to database: {e}")
            
    async def _monitoring_loop(self):
        """Background monitoring loop."""
        while self.monitoring_active:
            try:
                # Update metrics
                await self._update_metrics()
                
                # Check circuit breakers
                await self._check_circuit_breakers()
                
                # Send metrics to collector
                if self.config.ENABLE_METRICS_COLLECTION:
                    await self._send_metrics()
                    
                await asyncio.sleep(self.config.MONITORING_INTERVAL)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"Monitoring loop error: {e}")
                await asyncio.sleep(1)
                
    async def _cleanup_loop(self):
        """Background cleanup loop."""
        while self.monitoring_active:
            try:
                # Clean up old errors
                await self._cleanup_old_errors()
                
                await asyncio.sleep(self.config.CLEANUP_INTERVAL)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"Cleanup loop error: {e}")
                await asyncio.sleep(1)
                
    async def _update_metrics(self):
        """Update recovery metrics."""
        try:
            # Calculate success rate
            if self.metrics.total_errors > 0:
                self.metrics.recovery_success_rate = self.metrics.recovered_errors / self.metrics.total_errors
                
            self.metrics.last_updated = datetime.utcnow()
            
        except Exception as e:
            self.logger.error(f"Metrics update failed: {e}")
            
    async def _check_circuit_breakers(self):
        """Check and update circuit breaker states."""
        try:
            for key, circuit_breaker in self.circuit_breakers.items():
                if circuit_breaker.state == 'half_open':
                    # Try to close the circuit breaker
                    await circuit_breaker.attempt_reset()
                    
        except Exception as e:
            self.logger.error(f"Circuit breaker check failed: {e}")
            
    async def _send_metrics(self):
        """Send metrics to monitoring system."""
        try:
            metrics_data = {
                'timestamp': datetime.utcnow().isoformat(),
                'recovery_metrics': asdict(self.metrics),
                'active_errors': len(self.active_errors),
                'circuit_breakers': {
                    key: {
                        'state': cb.state,
                        'failure_count': cb.failure_count,
                        'last_failure_time': cb.last_failure_time.isoformat() if cb.last_failure_time else None
                    }
                    for key, cb in self.circuit_breakers.items()
                }
            }
            
            await self.metrics_collector.send_metrics('error_recovery', metrics_data)
            
        except Exception as e:
            self.logger.error(f"Failed to send metrics: {e}")
            
    async def _cleanup_old_errors(self):
        """Clean up old error records."""
        try:
            cutoff_time = datetime.utcnow() - timedelta(hours=self.config.ERROR_RETENTION_HOURS)
            
            # Clean up active errors
            old_errors = [
                error_id for error_id, error_context in self.active_errors.items()
                if error_context.timestamp < cutoff_time
            ]
            
            for error_id in old_errors:
                del self.active_errors[error_id]
                if error_id in self.recovery_attempts:
                    del self.recovery_attempts[error_id]
                    
            if old_errors:
                self.logger.info(f"Cleaned up {len(old_errors)} old error records")
                
        except Exception as e:
            self.logger.error(f"Error cleanup failed: {e}")
            
    async def get_error_status(self, error_id: str) -> Optional[Dict[str, Any]]:
        """Get status of a specific error."""
        if error_id in self.active_errors:
            error_context = self.active_errors[error_id]
            attempts = self.recovery_attempts.get(error_id, [])
            
            return {
                'error_id': error_id,
                'operation': error_context.operation,
                'category': error_context.category.value,
                'severity': error_context.severity.value,
                'retry_count': error_context.retry_count,
                'max_retries': error_context.max_retries,
                'recovery_status': error_context.recovery_status.value,
                'recovery_strategy': error_context.recovery_strategy.value,
                'timestamp': error_context.timestamp.isoformat(),
                'attempts': len(attempts),
                'last_attempt': attempts[-1].started_at.isoformat() if attempts else None
            }
            
        return None
        
    async def get_recovery_metrics(self) -> RecoveryMetrics:
        """
Get recovery system metrics."""
        await self._update_metrics()
        return self.metrics
        
    async def get_circuit_breaker_status(self) -> Dict[str, Dict[str, Any]]:
        """
Get status of all circuit breakers."""
        status = {}
        
        for key, circuit_breaker in self.circuit_breakers.items():
            status[key] = {
                'state': circuit_breaker.state,
                'failure_count': circuit_breaker.failure_count,
                'success_count': circuit_breaker.success_count,
                'last_failure_time': circuit_breaker.last_failure_time.isoformat() if circuit_breaker.last_failure_time else None,
                'next_attempt_time': circuit_breaker.next_attempt_time.isoformat() if circuit_breaker.next_attempt_time else None
            }
            
        return status
        
    async def force_recover_error(self, error_id: str) -> bool:
        """
Force recovery attempt for a specific error."""
        try:
            if error_id not in self.active_errors:
                return False
                
            error_context = self.active_errors[error_id]
            error_context.retry_count = 0  # Reset retry count
            error_context.recovery_status = RecoveryStatus.PENDING
            
            self.logger.info(f"Forced recovery triggered for error {error_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Force recovery failed: {e}")
            return False
            
    async def reset_circuit_breaker(self, circuit_key: str) -> bool:
        """Reset a specific circuit breaker."""
        try:
            if circuit_key in self.circuit_breakers:
                await self.circuit_breakers[circuit_key].reset()
                self.logger.info(f"Circuit breaker reset: {circuit_key}")
                return True
                
            return False
            
        except Exception as e:
            self.logger.error(f"Circuit breaker reset failed: {e}")
            return False
            
    async def shutdown(self):
        """Shutdown error recovery manager."""
        try:
            self.monitoring_active = False
            
            # Cancel monitoring tasks
            if self.monitoring_task:
                self.monitoring_task.cancel()
                
            if self.cleanup_task:
                self.cleanup_task.cancel()
                
            # Wait for tasks to complete
            if self.monitoring_task:
                await self.monitoring_task
                
            if self.cleanup_task:
                await self.cleanup_task
                
            self.logger.info("Error recovery manager shutdown completed")
            
        except Exception as e:
            self.logger.error(f"Shutdown error: {e}")


# Factory function
def create_error_recovery_manager(config: Optional[RecoveryConfig] = None) -> ErrorRecoveryManager:
    """Create and return an error recovery manager instance."""
    return ErrorRecoveryManager(config)


# Decorator for automatic error recovery
def with_error_recovery(manager: ErrorRecoveryManager, operation: str, max_retries: int = 3):
    """
Decorator to add automatic error recovery to functions."""
    def decorator(func):
        async def wrapper(*args, **kwargs):
            async def retry_func():
                return await func(*args, **kwargs)
                
            try:
                return await func(*args, **kwargs)
            except Exception as e:
                result = await manager.handle_error(
                    error=e,
                    operation=operation,
                    context={'function': func.__name__, 'args': str(args), 'kwargs': str(kwargs)},
                    retry_func=retry_func
                )
                
                if result is None:
                    raise e
                    
                return result
                
        return wrapper
    return decorator


# Utility functions
async def create_resilient_operation(operation_func: Callable, operation_name: str, 
                                   config: Optional[RecoveryConfig] = None) -> Callable:
    """
Create a resilient operation with automatic error recovery."""
    manager = create_error_recovery_manager(config)
    await manager.start()
    
    @with_error_recovery(manager, operation_name)
    async def resilient_func(*args, **kwargs):
        return await operation_func(*args, **kwargs)
        
    return resilient_func
