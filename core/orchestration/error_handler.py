"""
Error Handler - Advanced Error Management & Recovery System

Comprehensive error handling framework for orchestration workflows with
intelligent error categorization, recovery strategies, and fault tolerance.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️  CRITICAL LEGAL WARNING:
This code is the EXCLUSIVE INTELLECTUAL PROPERTY of Fahed Mlaiel.
Unauthorized use, copying, or distribution is strictly prohibited.
Contact: mlaiel@live.de for licensing inquiries.
"""

import asyncio
import logging
import traceback
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Callable, Union
from dataclasses import dataclass, field
from enum import Enum
import uuid
import json

from backend.core.utils.metrics_collector import MetricsCollector
from backend.core.utils.event_dispatcher import EventDispatcher


class ErrorSeverity(Enum):
    """Error severity levels."""
    DEBUG = "debug"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"
    FATAL = "fatal"


class ErrorCategory(Enum):
    """Error category classification."""
    SYSTEM = "system"
    BUSINESS = "business"
    NETWORK = "network"
    DATABASE = "database"
    AUTHENTICATION = "authentication"
    AUTHORIZATION = "authorization"
    VALIDATION = "validation"
    RESOURCE = "resource"
    TIMEOUT = "timeout"
    CONFIGURATION = "configuration"


class RecoveryStrategy(Enum):
    """Error recovery strategies."""
    RETRY = "retry"
    FALLBACK = "fallback"
    CIRCUIT_BREAKER = "circuit_breaker"
    GRACEFUL_DEGRADATION = "graceful_degradation"
    FAIL_FAST = "fail_fast"
    COMPENSATE = "compensate"
    ESCALATE = "escalate"
    IGNORE = "ignore"


class ErrorStatus(Enum):
    """Error handling status."""
    NEW = "new"
    PROCESSING = "processing"
    RESOLVED = "resolved"
    FAILED = "failed"
    ESCALATED = "escalated"
    SUPPRESSED = "suppressed"


@dataclass
class ErrorDefinition:
    """Error type definition and handling rules."""
    error_id: str
    name: str
    category: ErrorCategory
    severity: ErrorSeverity
    recovery_strategy: RecoveryStrategy
    retry_policy: Dict[str, Any] = field(default_factory=dict)
    fallback_config: Dict[str, Any] = field(default_factory=dict)
    escalation_rules: Dict[str, Any] = field(default_factory=dict)
    notification_config: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ErrorInstance:
    """Individual error occurrence."""
    instance_id: str
    error_id: str
    component_id: str
    message: str
    details: Dict[str, Any]
    severity: ErrorSeverity
    category: ErrorCategory
    timestamp: datetime = field(default_factory=datetime.now)
    context: Dict[str, Any] = field(default_factory=dict)
    stack_trace: Optional[str] = None
    correlation_id: Optional[str] = None
    retry_count: int = 0
    status: ErrorStatus = ErrorStatus.NEW
    resolution_time: Optional[datetime] = None
    handled_by: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class RecoveryAction:
    """Error recovery action definition."""
    action_id: str
    error_id: str
    strategy: RecoveryStrategy
    handler_function: Callable
    conditions: Dict[str, Any] = field(default_factory=dict)
    timeout: Optional[int] = None
    priority: int = 1
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ErrorPattern:
    """Error pattern for analysis and prediction."""
    pattern_id: str
    name: str
    conditions: Dict[str, Any]
    frequency_threshold: int
    time_window: int
    severity: ErrorSeverity
    predicted_impact: str
    prevention_actions: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ErrorAnalysis:
    """Error analysis result."""
    analysis_id: str
    component_id: str
    time_window: int
    total_errors: int
    error_rate: float
    severity_distribution: Dict[str, int]
    category_distribution: Dict[str, int]
    top_errors: List[Dict[str, Any]]
    trends: Dict[str, Any]
    patterns_detected: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)


class ErrorHandler:
    """
    Advanced error handling and recovery system for orchestration workflows.
    
    Provides comprehensive error management capabilities including:
    - Intelligent error categorization and severity assessment
    - Multi-strategy recovery mechanisms with fallback options
    - Pattern-based error prediction and prevention
    - Circuit breaker and bulkhead patterns
    - Error correlation and root cause analysis
    - Automated escalation and notification systems
    """
    
    def __init__(self, max_retry_attempts: int = 3, error_retention_hours: int = 24):
        self.logger = logging.getLogger(__name__)
        self.metrics_collector = MetricsCollector()
        self.event_dispatcher = EventDispatcher()
        
        # Core configuration
        self.max_retry_attempts = max_retry_attempts
        self.error_retention_hours = error_retention_hours
        
        # Error management
        self.error_definitions: Dict[str, ErrorDefinition] = {}
        self.recovery_actions: Dict[str, List[RecoveryAction]] = {}
        self.error_patterns: Dict[str, ErrorPattern] = {}
        
        # Error tracking
        self.active_errors: Dict[str, ErrorInstance] = {}
        self.error_history: List[ErrorInstance] = []
        self.pattern_matches: Dict[str, List[str]] = {}
        
        # Circuit breakers
        self.circuit_breakers: Dict[str, Dict[str, Any]] = {}
        
        # Error statistics
        self.error_stats = {
            'total_errors': 0,
            'resolved_errors': 0,
            'failed_recoveries': 0,
            'escalated_errors': 0,
            'average_resolution_time': 0.0,
            'error_rate_by_category': {},
            'error_rate_by_severity': {},
            'recovery_success_rate': 0.0,
            'pattern_detection_rate': 0.0
        }
        
        # Background tasks
        self._start_background_tasks()
        
        self.logger.info("ErrorHandler initialized")
    
    def _start_background_tasks(self) -> None:
        """Start background error management tasks."""
        asyncio.create_task(self._error_cleanup_task())
        asyncio.create_task(self._pattern_detection_task())
        asyncio.create_task(self._circuit_breaker_monitor())
        asyncio.create_task(self._error_analysis_task())
    
    async def register_error_definition(self, definition: ErrorDefinition) -> bool:
        """
        Register error definition and handling rules.
        
        Args:
            definition: Error definition to register
            
        Returns:
            bool: Success status
        """
        try:
            # Validate definition
            if not await self._validate_error_definition(definition):
                return False
            
            self.error_definitions[definition.error_id] = definition
            
            # Initialize circuit breaker if needed
            if definition.recovery_strategy == RecoveryStrategy.CIRCUIT_BREAKER:
                self.circuit_breakers[definition.error_id] = {
                    'state': 'closed',
                    'failure_count': 0,
                    'last_failure_time': None,
                    'timeout': definition.retry_policy.get('circuit_timeout', 60),
                    'failure_threshold': definition.retry_policy.get('failure_threshold', 5)
                }
            
            await self.event_dispatcher.emit('error_definition_registered', {
                'error_id': definition.error_id,
                'category': definition.category.value,
                'severity': definition.severity.value,
                'recovery_strategy': definition.recovery_strategy.value
            })
            
            await self.metrics_collector.increment('error_definitions.registered')
            
            self.logger.info(f"Error definition registered: {definition.error_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to register error definition: {e}")
            return False
    
    async def register_recovery_action(self, action: RecoveryAction) -> bool:
        """
        Register recovery action for error handling.
        
        Args:
            action: Recovery action to register
            
        Returns:
            bool: Success status
        """
        try:
            if not await self._validate_recovery_action(action):
                return False
            
            if action.error_id not in self.recovery_actions:
                self.recovery_actions[action.error_id] = []
            
            self.recovery_actions[action.error_id].append(action)
            
            # Sort by priority
            self.recovery_actions[action.error_id].sort(key=lambda x: x.priority)
            
            await self.event_dispatcher.emit('recovery_action_registered', {
                'action_id': action.action_id,
                'error_id': action.error_id,
                'strategy': action.strategy.value
            })
            
            await self.metrics_collector.increment('recovery_actions.registered')
            
            self.logger.info(f"Recovery action registered: {action.action_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to register recovery action: {e}")
            return False
    
    async def register_error_pattern(self, pattern: ErrorPattern) -> bool:
        """
        Register error pattern for prediction and prevention.
        
        Args:
            pattern: Error pattern to register
            
        Returns:
            bool: Success status
        """
        try:
            if not await self._validate_error_pattern(pattern):
                return False
            
            self.error_patterns[pattern.pattern_id] = pattern
            self.pattern_matches[pattern.pattern_id] = []
            
            await self.event_dispatcher.emit('error_pattern_registered', {
                'pattern_id': pattern.pattern_id,
                'name': pattern.name,
                'severity': pattern.severity.value
            })
            
            await self.metrics_collector.increment('error_patterns.registered')
            
            self.logger.info(f"Error pattern registered: {pattern.pattern_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to register error pattern: {e}")
            return False
    
    async def handle_error(self, error: ErrorInstance) -> str:
        """
        Handle error occurrence with recovery strategies.
        
        Args:
            error: Error instance to handle
            
        Returns:
            str: Error handling ID
        """
        try:
            # Validate error
            if not await self._validate_error_instance(error):
                raise ValueError("Invalid error instance")
            
            # Store error
            self.active_errors[error.instance_id] = error
            self.error_stats['total_errors'] += 1
            
            # Update error rate statistics
            await self._update_error_statistics(error)
            
            # Check for patterns
            await self._check_error_patterns(error)
            
            # Process error asynchronously
            asyncio.create_task(self._handle_error_async(error))
            
            await self.event_dispatcher.emit('error_occurred', {
                'instance_id': error.instance_id,
                'error_id': error.error_id,
                'component_id': error.component_id,
                'severity': error.severity.value,
                'category': error.category.value
            })
            
            await self.metrics_collector.increment('errors.occurred')
            await self.metrics_collector.increment(f'errors.{error.severity.value}')
            await self.metrics_collector.increment(f'errors.{error.category.value}')
            
            self.logger.debug(f"Error handling started: {error.instance_id}")
            return error.instance_id
            
        except Exception as e:
            self.logger.error(f"Failed to handle error: {e}")
            raise
    
    async def _handle_error_async(self, error: ErrorInstance) -> None:
        """Handle error asynchronously with recovery strategies."""
        try:
            error.status = ErrorStatus.PROCESSING
            start_time = datetime.now()
            
            # Get error definition
            definition = self.error_definitions.get(error.error_id)
            if not definition:
                # Use default handling
                definition = await self._create_default_error_definition(error)
            
            # Check circuit breaker
            if not await self._check_circuit_breaker(error.error_id):
                error.status = ErrorStatus.SUPPRESSED
                await self._finalize_error_handling(error, start_time)
                return
            
            # Execute recovery strategy
            success = await self._execute_recovery_strategy(error, definition)
            
            if success:
                error.status = ErrorStatus.RESOLVED
                self.error_stats['resolved_errors'] += 1
                await self._reset_circuit_breaker(error.error_id)
            else:
                # Check if should escalate
                if await self._should_escalate(error, definition):
                    await self._escalate_error(error, definition)
                    error.status = ErrorStatus.ESCALATED
                    self.error_stats['escalated_errors'] += 1
                else:
                    error.status = ErrorStatus.FAILED
                    self.error_stats['failed_recoveries'] += 1
                    await self._record_circuit_breaker_failure(error.error_id)
            
            await self._finalize_error_handling(error, start_time)
            
        except Exception as e:
            error.status = ErrorStatus.FAILED
            error.metadata['handling_error'] = str(e)
            self.logger.error(f"Error handling failed: {e}")
            
            await self.event_dispatcher.emit('error_handling_failed', {
                'instance_id': error.instance_id,
                'handling_error': str(e)
            })
    
    async def _execute_recovery_strategy(self, error: ErrorInstance, definition: ErrorDefinition) -> bool:
        """Execute recovery strategy for error."""
        strategy = definition.recovery_strategy
        
        try:
            if strategy == RecoveryStrategy.RETRY:
                return await self._execute_retry_strategy(error, definition)
            elif strategy == RecoveryStrategy.FALLBACK:
                return await self._execute_fallback_strategy(error, definition)
            elif strategy == RecoveryStrategy.GRACEFUL_DEGRADATION:
                return await self._execute_degradation_strategy(error, definition)
            elif strategy == RecoveryStrategy.COMPENSATE:
                return await self._execute_compensation_strategy(error, definition)
            elif strategy == RecoveryStrategy.FAIL_FAST:
                return False  # Immediate failure
            elif strategy == RecoveryStrategy.IGNORE:
                return True  # Ignore error
            else:
                # Execute custom recovery actions
                return await self._execute_custom_recovery(error, definition)
                
        except Exception as e:
            self.logger.error(f"Recovery strategy failed: {strategy.value} - {e}")
            return False
    
    async def _execute_retry_strategy(self, error: ErrorInstance, definition: ErrorDefinition) -> bool:
        """Execute retry recovery strategy."""
        retry_policy = definition.retry_policy
        max_retries = retry_policy.get('max_retries', self.max_retry_attempts)
        delay = retry_policy.get('delay', 1.0)
        backoff_factor = retry_policy.get('backoff_factor', 2.0)
        
        for attempt in range(max_retries):
            if attempt > 0:
                await asyncio.sleep(delay * (backoff_factor ** (attempt - 1)))
            
            error.retry_count = attempt + 1
            
            # Execute recovery actions
            if await self._execute_recovery_actions(error):
                return True
            
            # Check if should continue retrying
            if not await self._should_retry(error, definition, attempt + 1):
                break
        
        return False
    
    async def _execute_fallback_strategy(self, error: ErrorInstance, definition: ErrorDefinition) -> bool:
        """Execute fallback recovery strategy."""
        fallback_config = definition.fallback_config
        
        # Try primary fallback
        if await self._execute_fallback_action(error, fallback_config.get('primary')):
            return True
        
        # Try secondary fallback
        if await self._execute_fallback_action(error, fallback_config.get('secondary')):
            return True
        
        # Try default fallback
        return await self._execute_fallback_action(error, fallback_config.get('default'))
    
    async def _execute_degradation_strategy(self, error: ErrorInstance, definition: ErrorDefinition) -> bool:
        """Execute graceful degradation strategy."""
        # Reduce service quality but maintain basic functionality
        degradation_config = definition.fallback_config.get('degradation', {})
        
        # Apply degradation settings
        for setting, value in degradation_config.items():
            error.context[f'degraded_{setting}'] = value
        
        # Execute with degraded settings
        return await self._execute_recovery_actions(error)
    
    async def _execute_compensation_strategy(self, error: ErrorInstance, definition: ErrorDefinition) -> bool:
        """Execute compensation recovery strategy."""
        compensation_config = definition.fallback_config.get('compensation', {})
        
        # Execute compensation actions
        for action in compensation_config.get('actions', []):
            try:
                await self._execute_compensation_action(error, action)
            except Exception as e:
                self.logger.error(f"Compensation action failed: {e}")
                return False
        
        return True
    
    async def _execute_custom_recovery(self, error: ErrorInstance, definition: ErrorDefinition) -> bool:
        """Execute custom recovery actions."""
        actions = self.recovery_actions.get(error.error_id, [])
        
        for action in actions:
            try:
                if await self._check_action_conditions(action, error):
                    success = await self._execute_recovery_action(action, error)
                    if success:
                        return True
            except Exception as e:
                self.logger.error(f"Custom recovery action failed: {action.action_id} - {e}")
        
        return False
    
    async def _execute_recovery_actions(self, error: ErrorInstance) -> bool:
        """Execute registered recovery actions for error."""
        actions = self.recovery_actions.get(error.error_id, [])
        
        for action in actions:
            try:
                if await self._check_action_conditions(action, error):
                    if await self._execute_recovery_action(action, error):
                        error.handled_by = action.action_id
                        return True
            except Exception as e:
                self.logger.error(f"Recovery action execution failed: {e}")
        
        return False
    
    async def _execute_recovery_action(self, action: RecoveryAction, error: ErrorInstance) -> bool:
        """Execute individual recovery action."""
        try:
            timeout = action.timeout or 30
            
            result = await asyncio.wait_for(
                action.handler_function(error),
                timeout=timeout
            )
            
            return bool(result)
            
        except asyncio.TimeoutError:
            self.logger.error(f"Recovery action timeout: {action.action_id}")
            return False
        except Exception as e:
            self.logger.error(f"Recovery action error: {action.action_id} - {e}")
            return False
    
    async def _execute_fallback_action(self, error: ErrorInstance, fallback_config: Optional[Dict[str, Any]]) -> bool:
        """Execute fallback action."""
        if not fallback_config:
            return False
        
        try:
            # Simple fallback simulation
            fallback_type = fallback_config.get('type', 'default')
            
            if fallback_type == 'cached_response':
                error.context['fallback_response'] = fallback_config.get('cached_data')
                return True
            elif fallback_type == 'alternative_service':
                error.context['alternative_service'] = fallback_config.get('service_url')
                return True
            else:
                # Default fallback
                return True
                
        except Exception as e:
            self.logger.error(f"Fallback action failed: {e}")
            return False
    
    async def _execute_compensation_action(self, error: ErrorInstance, action: Dict[str, Any]) -> None:
        """Execute compensation action."""
        action_type = action.get('type')
        
        if action_type == 'revert_transaction':
            # Simulate transaction reversal
            error.context['transaction_reverted'] = True
        elif action_type == 'cleanup_resources':
            # Simulate resource cleanup
            error.context['resources_cleaned'] = True
        elif action_type == 'notify_stakeholders':
            # Simulate stakeholder notification
            error.context['stakeholders_notified'] = True
    
    async def _check_action_conditions(self, action: RecoveryAction, error: ErrorInstance) -> bool:
        """Check if recovery action conditions are met."""
        conditions = action.conditions
        
        if not conditions:
            return True
        
        # Check retry count condition
        if 'max_retry_count' in conditions:
            if error.retry_count > conditions['max_retry_count']:
                return False
        
        # Check severity condition
        if 'min_severity' in conditions:
            required_severity = ErrorSeverity(conditions['min_severity'])
            if error.severity.value < required_severity.value:
                return False
        
        # Check component condition
        if 'component_patterns' in conditions:
            patterns = conditions['component_patterns']
            if not any(pattern in error.component_id for pattern in patterns):
                return False
        
        return True
    
    async def _should_retry(self, error: ErrorInstance, definition: ErrorDefinition, attempt: int) -> bool:
        """Check if error should be retried."""
        retry_policy = definition.retry_policy
        
        # Check max retries
        max_retries = retry_policy.get('max_retries', self.max_retry_attempts)
        if attempt >= max_retries:
            return False
        
        # Check retryable conditions
        retryable_categories = retry_policy.get('retryable_categories', [])
        if retryable_categories and error.category.value not in retryable_categories:
            return False
        
        # Check circuit breaker
        if not await self._check_circuit_breaker(error.error_id):
            return False
        
        return True
    
    async def _should_escalate(self, error: ErrorInstance, definition: ErrorDefinition) -> bool:
        """Check if error should be escalated."""
        escalation_rules = definition.escalation_rules
        
        if not escalation_rules:
            return False
        
        # Check severity threshold
        severity_threshold = escalation_rules.get('severity_threshold')
        if severity_threshold:
            threshold_severity = ErrorSeverity(severity_threshold)
            if error.severity.value >= threshold_severity.value:
                return True
        
        # Check retry count threshold
        retry_threshold = escalation_rules.get('retry_threshold')
        if retry_threshold and error.retry_count >= retry_threshold:
            return True
        
        # Check time threshold
        time_threshold = escalation_rules.get('time_threshold')
        if time_threshold:
            elapsed = (datetime.now() - error.timestamp).seconds
            if elapsed >= time_threshold:
                return True
        
        return False
    
    async def _escalate_error(self, error: ErrorInstance, definition: ErrorDefinition) -> None:
        """Escalate error to higher level handling."""
        escalation_rules = definition.escalation_rules
        
        # Send notifications
        notification_config = definition.notification_config
        if notification_config:
            await self._send_error_notifications(error, notification_config)
        
        # Create escalation event
        await self.event_dispatcher.emit('error_escalated', {
            'instance_id': error.instance_id,
            'error_id': error.error_id,
            'component_id': error.component_id,
            'severity': error.severity.value,
            'retry_count': error.retry_count,
            'escalation_reason': escalation_rules.get('reason', 'threshold_exceeded')
        })
        
        # Update error context
        error.context['escalated'] = True
        error.context['escalation_time'] = datetime.now().isoformat()
    
    async def _send_error_notifications(self, error: ErrorInstance, config: Dict[str, Any]) -> None:
        """Send error notifications."""
        # Simulate notification sending
        notification_types = config.get('types', [])
        
        for notification_type in notification_types:
            if notification_type == 'email':
                self.logger.info(f"Email notification sent for error: {error.instance_id}")
            elif notification_type == 'slack':
                self.logger.info(f"Slack notification sent for error: {error.instance_id}")
            elif notification_type == 'webhook':
                self.logger.info(f"Webhook notification sent for error: {error.instance_id}")
    
    async def _check_error_patterns(self, error: ErrorInstance) -> None:
        """Check error against registered patterns."""
        for pattern_id, pattern in self.error_patterns.items():
            if await self._matches_pattern(error, pattern):
                self.pattern_matches[pattern_id].append(error.instance_id)
                
                # Check if pattern threshold is reached
                recent_matches = [
                    match for match in self.pattern_matches[pattern_id]
                    if self._is_recent_match(match, pattern.time_window)
                ]
                
                if len(recent_matches) >= pattern.frequency_threshold:
                    await self._handle_pattern_detection(pattern, recent_matches)
    
    async def _matches_pattern(self, error: ErrorInstance, pattern: ErrorPattern) -> bool:
        """Check if error matches pattern conditions."""
        conditions = pattern.conditions
        
        # Check component condition
        if 'component_pattern' in conditions:
            if conditions['component_pattern'] not in error.component_id:
                return False
        
        # Check category condition
        if 'category' in conditions:
            if error.category.value != conditions['category']:
                return False
        
        # Check severity condition
        if 'min_severity' in conditions:
            min_severity = ErrorSeverity(conditions['min_severity'])
            if error.severity.value < min_severity.value:
                return False
        
        # Check message pattern
        if 'message_pattern' in conditions:
            if conditions['message_pattern'] not in error.message:
                return False
        
        return True
    
    def _is_recent_match(self, match_id: str, time_window: int) -> bool:
        """Check if match is within time window."""
        # Find error instance
        error = self.active_errors.get(match_id)
        if not error:
            error = next((e for e in self.error_history if e.instance_id == match_id), None)
        
        if not error:
            return False
        
        age = (datetime.now() - error.timestamp).seconds
        return age <= time_window
    
    async def _handle_pattern_detection(self, pattern: ErrorPattern, matches: List[str]) -> None:
        """Handle detected error pattern."""
        await self.event_dispatcher.emit('error_pattern_detected', {
            'pattern_id': pattern.pattern_id,
            'pattern_name': pattern.name,
            'match_count': len(matches),
            'predicted_impact': pattern.predicted_impact,
            'prevention_actions': pattern.prevention_actions
        })
        
        # Execute prevention actions
        for action in pattern.prevention_actions:
            try:
                await self._execute_prevention_action(action, pattern, matches)
            except Exception as e:
                self.logger.error(f"Prevention action failed: {action} - {e}")
        
        self.error_stats['pattern_detection_rate'] += 1
    
    async def _execute_prevention_action(self, action: str, pattern: ErrorPattern, matches: List[str]) -> None:
        """Execute error prevention action."""
        if action == 'circuit_breaker':
            # Open circuit breaker for pattern components
            affected_components = set()
            for match_id in matches:
                error = self.active_errors.get(match_id)
                if error:
                    affected_components.add(error.component_id)
            
            for component_id in affected_components:
                await self._open_circuit_breaker(component_id)
        
        elif action == 'scale_up':
            # Trigger scaling for affected components
            self.logger.info(f"Triggering scale-up for pattern: {pattern.pattern_id}")
        
        elif action == 'alert':
            # Send high-priority alert
            await self.event_dispatcher.emit('pattern_alert', {
                'pattern_id': pattern.pattern_id,
                'severity': 'high',
                'matches': len(matches)
            })
    
    async def _check_circuit_breaker(self, error_id: str) -> bool:
        """Check circuit breaker state for error type."""
        cb = self.circuit_breakers.get(error_id, {})
        
        if cb.get('state') == 'open':
            # Check if timeout period has passed
            last_failure = cb.get('last_failure_time')
            timeout = cb.get('timeout', 60)
            
            if last_failure and (datetime.now() - last_failure).seconds > timeout:
                cb['state'] = 'half_open'
                return True
            
            return False
        
        return True
    
    async def _record_circuit_breaker_failure(self, error_id: str) -> None:
        """Record circuit breaker failure."""
        if error_id not in self.circuit_breakers:
            return
        
        cb = self.circuit_breakers[error_id]
        cb['failure_count'] = cb.get('failure_count', 0) + 1
        cb['last_failure_time'] = datetime.now()
        
        threshold = cb.get('failure_threshold', 5)
        
        if cb['failure_count'] >= threshold:
            cb['state'] = 'open'
            
            await self.event_dispatcher.emit('circuit_breaker_opened', {
                'error_id': error_id,
                'failure_count': cb['failure_count']
            })
    
    async def _reset_circuit_breaker(self, error_id: str) -> None:
        """Reset circuit breaker after successful recovery."""
        if error_id in self.circuit_breakers:
            cb = self.circuit_breakers[error_id]
            cb['state'] = 'closed'
            cb['failure_count'] = 0
            cb['last_failure_time'] = None
    
    async def _open_circuit_breaker(self, component_id: str) -> None:
        """Open circuit breaker for component."""
        # Find relevant circuit breakers
        for error_id, cb in self.circuit_breakers.items():
            cb['state'] = 'open'
            cb['last_failure_time'] = datetime.now()
    
    async def _finalize_error_handling(self, error: ErrorInstance, start_time: datetime) -> None:
        """Finalize error handling and update statistics."""
        error.resolution_time = datetime.now()
        resolution_duration = (error.resolution_time - start_time).total_seconds()
        
        # Update statistics
        current_avg = self.error_stats['average_resolution_time']
        total_resolved = self.error_stats['resolved_errors']
        
        if error.status == ErrorStatus.RESOLVED:
            if total_resolved > 0:
                self.error_stats['average_resolution_time'] = (
                    (current_avg * total_resolved + resolution_duration) / (total_resolved + 1)
                )
            else:
                self.error_stats['average_resolution_time'] = resolution_duration
        
        # Calculate recovery success rate
        total_handled = (self.error_stats['resolved_errors'] + 
                        self.error_stats['failed_recoveries'] + 
                        self.error_stats['escalated_errors'])
        
        if total_handled > 0:
            self.error_stats['recovery_success_rate'] = (
                self.error_stats['resolved_errors'] / total_handled
            )
        
        # Emit completion event
        await self.event_dispatcher.emit('error_handling_completed', {
            'instance_id': error.instance_id,
            'status': error.status.value,
            'resolution_time': resolution_duration,
            'retry_count': error.retry_count,
            'handled_by': error.handled_by
        })
        
        # Move to history
        if error.instance_id in self.active_errors:
            del self.active_errors[error.instance_id]
        self.error_history.append(error)
    
    async def _update_error_statistics(self, error: ErrorInstance) -> None:
        """Update error rate statistics."""
        # Update category statistics
        category = error.category.value
        if category not in self.error_stats['error_rate_by_category']:
            self.error_stats['error_rate_by_category'][category] = 0
        self.error_stats['error_rate_by_category'][category] += 1
        
        # Update severity statistics
        severity = error.severity.value
        if severity not in self.error_stats['error_rate_by_severity']:
            self.error_stats['error_rate_by_severity'][severity] = 0
        self.error_stats['error_rate_by_severity'][severity] += 1
    
    async def _create_default_error_definition(self, error: ErrorInstance) -> ErrorDefinition:
        """Create default error definition for unregistered errors."""
        return ErrorDefinition(
            error_id=error.error_id,
            name=f"Auto-generated for {error.error_id}",
            category=error.category,
            severity=error.severity,
            recovery_strategy=RecoveryStrategy.RETRY,
            retry_policy={'max_retries': 2, 'delay': 1.0}
        )
    
    async def analyze_errors(self, component_id: str, time_window: int = 3600) -> ErrorAnalysis:
        """
        Analyze errors for a component within time window.
        
        Args:
            component_id: Component identifier
            time_window: Analysis time window in seconds
            
        Returns:
            ErrorAnalysis: Analysis results
        """
        analysis_id = str(uuid.uuid4())
        cutoff_time = datetime.now() - timedelta(seconds=time_window)
        
        # Collect relevant errors
        relevant_errors = []
        
        # From active errors
        relevant_errors.extend([
            error for error in self.active_errors.values()
            if error.component_id == component_id and error.timestamp >= cutoff_time
        ])
        
        # From error history
        relevant_errors.extend([
            error for error in self.error_history
            if error.component_id == component_id and error.timestamp >= cutoff_time
        ])
        
        total_errors = len(relevant_errors)
        error_rate = total_errors / (time_window / 3600)  # Errors per hour
        
        # Severity distribution
        severity_dist = {}
        for error in relevant_errors:
            severity = error.severity.value
            severity_dist[severity] = severity_dist.get(severity, 0) + 1
        
        # Category distribution
        category_dist = {}
        for error in relevant_errors:
            category = error.category.value
            category_dist[category] = category_dist.get(category, 0) + 1
        
        # Top errors
        error_counts = {}
        for error in relevant_errors:
            error_counts[error.error_id] = error_counts.get(error.error_id, 0) + 1
        
        top_errors = [
            {'error_id': error_id, 'count': count}
            for error_id, count in sorted(error_counts.items(), key=lambda x: x[1], reverse=True)[:10]
        ]
        
        # Trend analysis
        trends = await self._analyze_error_trends(relevant_errors, time_window)
        
        # Pattern detection
        patterns_detected = []
        for pattern_id, matches in self.pattern_matches.items():
            if any(match in [e.instance_id for e in relevant_errors] for match in matches):
                patterns_detected.append(pattern_id)
        
        # Recommendations
        recommendations = await self._generate_error_recommendations(
            component_id, relevant_errors, severity_dist, category_dist
        )
        
        return ErrorAnalysis(
            analysis_id=analysis_id,
            component_id=component_id,
            time_window=time_window,
            total_errors=total_errors,
            error_rate=error_rate,
            severity_distribution=severity_dist,
            category_distribution=category_dist,
            top_errors=top_errors,
            trends=trends,
            patterns_detected=patterns_detected,
            recommendations=recommendations
        )
    
    async def _analyze_error_trends(self, errors: List[ErrorInstance], time_window: int) -> Dict[str, Any]:
        """Analyze error trends."""
        if len(errors) < 2:
            return {'trend': 'insufficient_data'}
        
        # Sort by timestamp
        sorted_errors = sorted(errors, key=lambda x: x.timestamp)
        
        # Calculate hourly error counts
        hourly_counts = {}
        for error in sorted_errors:
            hour = error.timestamp.replace(minute=0, second=0, microsecond=0)
            hourly_counts[hour] = hourly_counts.get(hour, 0) + 1
        
        # Analyze trend
        if len(hourly_counts) < 2:
            return {'trend': 'stable'}
        
        counts = list(hourly_counts.values())
        recent_avg = sum(counts[-3:]) / min(3, len(counts))
        overall_avg = sum(counts) / len(counts)
        
        if recent_avg > overall_avg * 1.2:
            trend = 'increasing'
        elif recent_avg < overall_avg * 0.8:
            trend = 'decreasing'
        else:
            trend = 'stable'
        
        return {
            'trend': trend,
            'hourly_counts': {hour.isoformat(): count for hour, count in hourly_counts.items()},
            'recent_average': recent_avg,
            'overall_average': overall_avg
        }
    
    async def _generate_error_recommendations(
        self,
        component_id: str,
        errors: List[ErrorInstance],
        severity_dist: Dict[str, int],
        category_dist: Dict[str, int]
    ) -> List[str]:
        """Generate error handling recommendations."""
        recommendations = []
        
        # High error rate
        if len(errors) > 50:
            recommendations.append("High error rate detected - consider implementing circuit breaker")
        
        # High severity errors
        critical_errors = severity_dist.get('critical', 0) + severity_dist.get('fatal', 0)
        if critical_errors > 5:
            recommendations.append("Multiple critical errors - immediate attention required")
        
        # Specific category issues
        if category_dist.get('timeout', 0) > 10:
            recommendations.append("Frequent timeout errors - consider increasing timeout values or optimizing performance")
        
        if category_dist.get('resource', 0) > 10:
            recommendations.append("Resource-related errors detected - consider scaling resources")
        
        if category_dist.get('network', 0) > 10:
            recommendations.append("Network errors detected - check network connectivity and retry policies")
        
        # Pattern-based recommendations
        if not recommendations:
            recommendations.append("Error patterns are within normal ranges")
        
        return recommendations
    
    async def _error_cleanup_task(self) -> None:
        """Background task to clean up old errors."""
        while True:
            try:
                cutoff_time = datetime.now() - timedelta(hours=self.error_retention_hours)
                
                # Clean error history
                self.error_history = [
                    error for error in self.error_history
                    if error.timestamp >= cutoff_time
                ]
                
                # Clean pattern matches
                for pattern_id in self.pattern_matches:
                    self.pattern_matches[pattern_id] = [
                        match for match in self.pattern_matches[pattern_id]
                        if self._is_recent_match(match, self.error_retention_hours * 3600)
                    ]
                
                await asyncio.sleep(3600)  # Clean every hour
                
            except Exception as e:
                self.logger.error(f"Error cleanup failed: {e}")
                await asyncio.sleep(300)
    
    async def _pattern_detection_task(self) -> None:
        """Background task for pattern detection."""
        while True:
            try:
                # Analyze error patterns across all components
                for pattern_id, pattern in self.error_patterns.items():
                    matches = self.pattern_matches.get(pattern_id, [])
                    recent_matches = [
                        match for match in matches
                        if self._is_recent_match(match, pattern.time_window)
                    ]
                    
                    if len(recent_matches) >= pattern.frequency_threshold:
                        await self._handle_pattern_detection(pattern, recent_matches)
                        # Clear matches to avoid duplicate detections
                        self.pattern_matches[pattern_id] = []
                
                await asyncio.sleep(300)  # Check every 5 minutes
                
            except Exception as e:
                self.logger.error(f"Pattern detection failed: {e}")
                await asyncio.sleep(60)
    
    async def _circuit_breaker_monitor(self) -> None:
        """Monitor circuit breaker states."""
        while True:
            try:
                for error_id, cb in self.circuit_breakers.items():
                    if cb.get('state') == 'half_open':
                        # Auto-close if no recent failures
                        last_failure = cb.get('last_failure_time')
                        if last_failure:
                            time_since_failure = (datetime.now() - last_failure).seconds
                            if time_since_failure > cb.get('timeout', 60) * 2:
                                cb['state'] = 'closed'
                                cb['failure_count'] = 0
                
                await asyncio.sleep(60)  # Check every minute
                
            except Exception as e:
                self.logger.error(f"Circuit breaker monitor failed: {e}")
                await asyncio.sleep(60)
    
    async def _error_analysis_task(self) -> None:
        """Background task for periodic error analysis."""
        while True:
            try:
                # Analyze errors for all active components
                active_components = set()
                for error in list(self.active_errors.values()) + self.error_history[-100:]:
                    active_components.add(error.component_id)
                
                for component_id in active_components:
                    analysis = await self.analyze_errors(component_id, 3600)
                    
                    # Emit analysis results
                    await self.event_dispatcher.emit('error_analysis_completed', {
                        'component_id': component_id,
                        'total_errors': analysis.total_errors,
                        'error_rate': analysis.error_rate,
                        'recommendations': len(analysis.recommendations)
                    })
                
                await asyncio.sleep(1800)  # Analyze every 30 minutes
                
            except Exception as e:
                self.logger.error(f"Error analysis task failed: {e}")
                await asyncio.sleep(300)
    
    async def _validate_error_definition(self, definition: ErrorDefinition) -> bool:
        """Validate error definition."""
        return bool(definition.error_id and definition.name)
    
    async def _validate_recovery_action(self, action: RecoveryAction) -> bool:
        """Validate recovery action."""
        return bool(action.action_id and action.error_id and action.handler_function)
    
    async def _validate_error_pattern(self, pattern: ErrorPattern) -> bool:
        """Validate error pattern."""
        return bool(pattern.pattern_id and pattern.name and pattern.conditions)
    
    async def _validate_error_instance(self, error: ErrorInstance) -> bool:
        """Validate error instance."""
        return bool(error.instance_id and error.error_id and error.component_id and error.message)
    
    async def get_error_status(self, instance_id: str) -> Optional[Dict[str, Any]]:
        """Get error handling status."""
        # Check active errors
        if instance_id in self.active_errors:
            error = self.active_errors[instance_id]
        else:
            error = next((e for e in self.error_history if e.instance_id == instance_id), None)
        
        if not error:
            return None
        
        return {
            'instance_id': error.instance_id,
            'error_id': error.error_id,
            'component_id': error.component_id,
            'status': error.status.value,
            'severity': error.severity.value,
            'category': error.category.value,
            'timestamp': error.timestamp.isoformat(),
            'retry_count': error.retry_count,
            'resolution_time': error.resolution_time.isoformat() if error.resolution_time else None,
            'handled_by': error.handled_by
        }
    
    async def get_component_errors(self, component_id: str, hours: int = 24) -> List[Dict[str, Any]]:
        """Get recent errors for component."""
        cutoff_time = datetime.now() - timedelta(hours=hours)
        
        errors = []
        
        # From active errors
        errors.extend([
            {
                'instance_id': error.instance_id,
                'error_id': error.error_id,
                'message': error.message,
                'severity': error.severity.value,
                'category': error.category.value,
                'timestamp': error.timestamp.isoformat(),
                'status': error.status.value
            }
            for error in self.active_errors.values()
            if error.component_id == component_id and error.timestamp >= cutoff_time
        ])
        
        # From history
        errors.extend([
            {
                'instance_id': error.instance_id,
                'error_id': error.error_id,
                'message': error.message,
                'severity': error.severity.value,
                'category': error.category.value,
                'timestamp': error.timestamp.isoformat(),
                'status': error.status.value
            }
            for error in self.error_history
            if error.component_id == component_id and error.timestamp >= cutoff_time
        ])
        
        # Sort by timestamp (newest first)
        errors.sort(key=lambda x: x['timestamp'], reverse=True)
        
        return errors
    
    async def get_error_stats(self) -> Dict[str, Any]:
        """Get error handling statistics."""
        return {
            **self.error_stats,
            'active_errors': len(self.active_errors),
            'error_history_size': len(self.error_history),
            'registered_patterns': len(self.error_patterns),
            'active_circuit_breakers': len([
                cb for cb in self.circuit_breakers.values() 
                if cb.get('state') != 'closed'
            ]),
            'recovery_actions_registered': sum(len(actions) for actions in self.recovery_actions.values())
        }
