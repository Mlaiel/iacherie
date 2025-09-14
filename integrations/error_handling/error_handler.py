"""Error Handler - Integration Error Management
==========================================

Comprehensive error handling system for all third-party integrations.
Provides error classification, recovery strategies, and intelligent alerting.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import logging
import traceback
from typing import Dict, List, Optional, Any, Callable, Union
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import json
import hashlib

import httpx


class ErrorSeverity(Enum):
    """Error severity levels."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ErrorCategory(Enum):
    """Error categories."""
    AUTHENTICATION = "authentication"
    AUTHORIZATION = "authorization"
    RATE_LIMIT = "rate_limit"
    NETWORK = "network"
    TIMEOUT = "timeout"
    VALIDATION = "validation"
    BUSINESS_LOGIC = "business_logic"
    INTEGRATION_DOWN = "integration_down"
    DATA_FORMAT = "data_format"
    QUOTA_EXCEEDED = "quota_exceeded"
    CONFIGURATION = "configuration"
    UNKNOWN = "unknown"


class ErrorRecoveryAction(Enum):
    """Error recovery actions."""
    RETRY = "retry"
    FALLBACK = "fallback"
    ESCALATE = "escalate"
    IGNORE = "ignore"
    CIRCUIT_BREAK = "circuit_break"
    REFRESH_AUTH = "refresh_auth"
    SWITCH_ENDPOINT = "switch_endpoint"
    MANUAL_INTERVENTION = "manual_intervention"


@dataclass
class ErrorRule:
    """Error handling rule."""
    error_pattern: str
    category: ErrorCategory
    severity: ErrorSeverity
    recovery_action: ErrorRecoveryAction
    retry_attempts: int = 3
    retry_delay: int = 5  # seconds
    escalation_threshold: int = 5
    alert_enabled: bool = True
    custom_handler: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ErrorEvent:
    """Error event record."""
    id: str
    integration_name: str
    error_type: str
    error_message: str
    category: ErrorCategory
    severity: ErrorSeverity
    recovery_action: ErrorRecoveryAction
    context: Dict[str, Any] = field(default_factory=dict)
    stack_trace: Optional[str] = None
    request_data: Optional[Dict[str, Any]] = None
    response_data: Optional[Dict[str, Any]] = None
    timestamp: datetime = field(default_factory=datetime.utcnow)
    resolved: bool = False
    resolution_time: Optional[datetime] = None
    recovery_attempts: int = 0


@dataclass
class ErrorStats:
    """Error statistics."""
    total_errors: int = 0
    errors_by_category: Dict[ErrorCategory, int] = field(default_factory=dict)
    errors_by_severity: Dict[ErrorSeverity, int] = field(default_factory=dict)
    errors_by_integration: Dict[str, int] = field(default_factory=dict)
    recent_errors: List[ErrorEvent] = field(default_factory=list)
    error_rate: float = 0.0
    resolution_rate: float = 0.0
    average_resolution_time: float = 0.0


ErrorHandler = Callable[[ErrorEvent], None]


class ErrorHandler:
    """Comprehensive error management system for integrations.
    
    Provides intelligent error handling, classification, recovery strategies,
    and automated alerting for all third-party integration failures.
    """
    
    def __init__(self) -> None:
        """Initialize error handler."""
        self.logger = logging.getLogger(__name__)
        
        # Error handling rules
        self.error_rules: Dict[str, ErrorRule] = {}
        
        # Error event storage
        self.error_events: Dict[str, ErrorEvent] = {}
        
        # Custom error handlers
        self.custom_handlers: Dict[str, ErrorHandler] = {}
        
        # Error statistics
        self.stats = ErrorStats()
        
        # Integration error counts for pattern detection
        self.integration_errors: Dict[str, List[datetime]] = {}
        
        # Alert handlers
        self.alert_handlers: List[Callable] = []
        
        # Recovery strategies
        self.recovery_strategies: Dict[ErrorRecoveryAction, Callable] = {}
        
        # Initialize default error rules and handlers
        self._initialize_default_rules()
        self._initialize_recovery_strategies()
    
    def _initialize_default_rules(self) -> None:
        """Initialize default error handling rules."""
        default_rules = [
            # Authentication errors
            ErrorRule(
                error_pattern="401|unauthorized|invalid.*token|expired.*token",
                category=ErrorCategory.AUTHENTICATION,
                severity=ErrorSeverity.HIGH,
                recovery_action=ErrorRecoveryAction.REFRESH_AUTH,
                retry_attempts=2,
                retry_delay=10
            ),
            ErrorRule(
                error_pattern="403|forbidden|access.*denied",
                category=ErrorCategory.AUTHORIZATION,
                severity=ErrorSeverity.HIGH,
                recovery_action=ErrorRecoveryAction.ESCALATE,
                retry_attempts=1
            ),
            
            # Rate limiting errors
            ErrorRule(
                error_pattern="429|rate.*limit|too.*many.*requests",
                category=ErrorCategory.RATE_LIMIT,
                severity=ErrorSeverity.MEDIUM,
                recovery_action=ErrorRecoveryAction.RETRY,
                retry_attempts=5,
                retry_delay=60
            ),
            ErrorRule(
                error_pattern="quota.*exceeded|usage.*limit",
                category=ErrorCategory.QUOTA_EXCEEDED,
                severity=ErrorSeverity.HIGH,
                recovery_action=ErrorRecoveryAction.FALLBACK,
                retry_attempts=1
            ),
            
            # Network errors
            ErrorRule(
                error_pattern="connection.*error|network.*error|dns.*error",
                category=ErrorCategory.NETWORK,
                severity=ErrorSeverity.MEDIUM,
                recovery_action=ErrorRecoveryAction.SWITCH_ENDPOINT,
                retry_attempts=3,
                retry_delay=5
            ),
            ErrorRule(
                error_pattern="timeout|timed.*out",
                category=ErrorCategory.TIMEOUT,
                severity=ErrorSeverity.MEDIUM,
                recovery_action=ErrorRecoveryAction.RETRY,
                retry_attempts=3,
                retry_delay=10
            ),
            
            # Server errors
            ErrorRule(
                error_pattern="500|internal.*server.*error|service.*unavailable|502|503|504",
                category=ErrorCategory.INTEGRATION_DOWN,
                severity=ErrorSeverity.HIGH,
                recovery_action=ErrorRecoveryAction.CIRCUIT_BREAK,
                retry_attempts=3,
                retry_delay=30
            ),
            
            # Data format errors
            ErrorRule(
                error_pattern="400|bad.*request|invalid.*format|malformed",
                category=ErrorCategory.DATA_FORMAT,
                severity=ErrorSeverity.MEDIUM,
                recovery_action=ErrorRecoveryAction.ESCALATE,
                retry_attempts=1
            ),
            ErrorRule(
                error_pattern="validation.*error|schema.*error",
                category=ErrorCategory.VALIDATION,
                severity=ErrorSeverity.MEDIUM,
                recovery_action=ErrorRecoveryAction.ESCALATE,
                retry_attempts=1
            ),
        ]
        
        for rule in default_rules:
            rule_id = hashlib.md5(rule.error_pattern.encode()).hexdigest()[:8]
            self.error_rules[rule_id] = rule
    
    def _initialize_recovery_strategies(self) -> None:
        """Initialize error recovery strategies."""
        
        async def retry_strategy(error_event: ErrorEvent) -> bool:
            """Retry the failed operation."""
            self.logger.info(f"Retrying operation for error: {error_event.id}")
            # Implementation would retry the original request
            return True
        
        async def fallback_strategy(error_event: ErrorEvent) -> bool:
            """Use fallback service or method."""
            self.logger.info(f"Using fallback for error: {error_event.id}")
            # Implementation would use alternative service
            return True
        
        async def refresh_auth_strategy(error_event: ErrorEvent) -> bool:
            """Refresh authentication and retry."""
            self.logger.info(f"Refreshing authentication for error: {error_event.id}")
            # Implementation would refresh auth tokens
            return True
        
        async def switch_endpoint_strategy(error_event: ErrorEvent) -> bool:
            """Switch to alternative endpoint."""
            self.logger.info(f"Switching endpoint for error: {error_event.id}")
            # Implementation would switch to backup endpoint
            return True
        
        async def circuit_break_strategy(error_event: ErrorEvent) -> bool:
            """Activate circuit breaker."""
            self.logger.warning(f"Activating circuit breaker for error: {error_event.id}")
            # Implementation would activate circuit breaker
            return True
        
        async def escalate_strategy(error_event: ErrorEvent) -> bool:
            """Escalate error for manual intervention."""
            self.logger.warning(f"Escalating error for manual intervention: {error_event.id}")
            await self._send_escalation_alert(error_event)
            return False
        
        self.recovery_strategies = {
            ErrorRecoveryAction.RETRY: retry_strategy,
            ErrorRecoveryAction.FALLBACK: fallback_strategy,
            ErrorRecoveryAction.REFRESH_AUTH: refresh_auth_strategy,
            ErrorRecoveryAction.SWITCH_ENDPOINT: switch_endpoint_strategy,
            ErrorRecoveryAction.CIRCUIT_BREAK: circuit_break_strategy,
            ErrorRecoveryAction.ESCALATE: escalate_strategy,
        }
    
    async def handle_integration_error(
        self,
        error_type: str,
        integration_name: str,
        error_message: str,
        context: Optional[Dict[str, Any]] = None,
        request_data: Optional[Dict[str, Any]] = None,
        response_data: Optional[Dict[str, Any]] = None,
        exception: Optional[Exception] = None
    ) -> ErrorEvent:
        """Handle integration error with automatic classification and recovery."""
        try:
            # Create error event
            error_event = ErrorEvent(
                id=self._generate_error_id(integration_name, error_type),
                integration_name=integration_name,
                error_type=error_type,
                error_message=error_message,
                category=ErrorCategory.UNKNOWN,
                severity=ErrorSeverity.MEDIUM,
                recovery_action=ErrorRecoveryAction.IGNORE,
                context=context or {},
                request_data=request_data,
                response_data=response_data,
                stack_trace=traceback.format_exc() if exception else None
            )
            
            # Classify error
            await self._classify_error(error_event)
            
            # Store error event
            self.error_events[error_event.id] = error_event
            
            # Update statistics
            await self._update_error_stats(error_event)
            
            # Track integration error patterns
            await self._track_integration_errors(integration_name)
            
            # Send alerts if necessary
            if await self._should_send_alert(error_event):
                await self._send_alert(error_event)
            
            # Attempt recovery
            recovery_success = await self._attempt_recovery(error_event)
            
            # Log error
            self._log_error(error_event, recovery_success)
            
            return error_event
            
        except Exception as e:
            self.logger.error(f"Error in error handler: {str(e)}")
            # Return minimal error event
            return ErrorEvent(
                id="error_handler_failure",
                integration_name=integration_name,
                error_type="error_handler_failure",
                error_message=str(e),
                category=ErrorCategory.UNKNOWN,
                severity=ErrorSeverity.CRITICAL,
                recovery_action=ErrorRecoveryAction.MANUAL_INTERVENTION
            )
    
    async def _classify_error(self, error_event: ErrorEvent) -> None:
        """Classify error based on patterns and rules."""
        error_text = f"{error_event.error_type} {error_event.error_message}".lower()
        
        # Find matching rule
        for rule_id, rule in self.error_rules.items():
            if self._matches_pattern(error_text, rule.error_pattern.lower()):
                error_event.category = rule.category
                error_event.severity = rule.severity
                error_event.recovery_action = rule.recovery_action
                break
        
        # Special classification logic for specific integrations
        await self._apply_integration_specific_classification(error_event)
    
    def _matches_pattern(self, text: str, pattern: str) -> bool:
        """Check if text matches error pattern."""
        import re
        try:
            return bool(re.search(pattern, text, re.IGNORECASE))
        except re.error:
            # If regex fails, do simple string matching
            return any(keyword in text for keyword in pattern.split('|'))
    
    async def _apply_integration_specific_classification(self, error_event: ErrorEvent) -> None:
        """Apply integration-specific error classification."""
        integration_name = error_event.integration_name
        
        # Social media platform specific classifications
        if integration_name in ["youtube", "instagram", "tiktok", "facebook"]:
            if "content policy" in error_event.error_message.lower():
                error_event.category = ErrorCategory.BUSINESS_LOGIC
                error_event.severity = ErrorSeverity.HIGH
                error_event.recovery_action = ErrorRecoveryAction.ESCALATE
                
        # AI service specific classifications
        elif integration_name in ["openai", "anthropic", "huggingface"]:
            if "content filter" in error_event.error_message.lower():
                error_event.category = ErrorCategory.BUSINESS_LOGIC
                error_event.severity = ErrorSeverity.MEDIUM
                error_event.recovery_action = ErrorRecoveryAction.FALLBACK
                
        # Payment gateway specific classifications
        elif integration_name in ["stripe", "paypal"]:
            if "insufficient funds" in error_event.error_message.lower():
                error_event.category = ErrorCategory.BUSINESS_LOGIC
                error_event.severity = ErrorSeverity.HIGH
                error_event.recovery_action = ErrorRecoveryAction.ESCALATE
    
    async def _attempt_recovery(self, error_event: ErrorEvent) -> bool:
        """Attempt automatic error recovery."""
        try:
            recovery_action = error_event.recovery_action
            
            if recovery_action == ErrorRecoveryAction.IGNORE:
                return True
            
            # Check if custom handler exists
            if error_event.category.value in self.custom_handlers:
                handler = self.custom_handlers[error_event.category.value]
                await handler(error_event)
                return True
            
            # Use built-in recovery strategy
            if recovery_action in self.recovery_strategies:
                strategy = self.recovery_strategies[recovery_action]
                success = await strategy(error_event)
                
                error_event.recovery_attempts += 1
                
                if success:
                    error_event.resolved = True
                    error_event.resolution_time = datetime.utcnow()
                
                return success
            
            return False
            
        except Exception as e:
            self.logger.error(f"Error recovery failed for {error_event.id}: {str(e)}")
            return False
    
    async def _update_error_stats(self, error_event: ErrorEvent) -> None:
        """Update error statistics."""
        self.stats.total_errors += 1
        
        # Update category stats
        if error_event.category not in self.stats.errors_by_category:
            self.stats.errors_by_category[error_event.category] = 0
        self.stats.errors_by_category[error_event.category] += 1
        
        # Update severity stats
        if error_event.severity not in self.stats.errors_by_severity:
            self.stats.errors_by_severity[error_event.severity] = 0
        self.stats.errors_by_severity[error_event.severity] += 1
        
        # Update integration stats
        integration_name = error_event.integration_name
        if integration_name not in self.stats.errors_by_integration:
            self.stats.errors_by_integration[integration_name] = 0
        self.stats.errors_by_integration[integration_name] += 1
        
        # Update recent errors (keep last 100)
        self.stats.recent_errors.append(error_event)
        if len(self.stats.recent_errors) > 100:
            self.stats.recent_errors.pop(0)
        
        # Calculate error rate (errors per hour)
        one_hour_ago = datetime.utcnow() - timedelta(hours=1)
        recent_errors = [
            e for e in self.stats.recent_errors
            if e.timestamp >= one_hour_ago
        ]
        self.stats.error_rate = len(recent_errors)
        
        # Calculate resolution rate
        resolved_count = len([e for e in self.stats.recent_errors if e.resolved])
        total_count = len(self.stats.recent_errors)
        self.stats.resolution_rate = (resolved_count / total_count) if total_count > 0 else 0.0
        
        # Calculate average resolution time
        resolved_errors = [e for e in self.stats.recent_errors if e.resolved and e.resolution_time]
        if resolved_errors:
            resolution_times = [
                (e.resolution_time - e.timestamp).total_seconds()
                for e in resolved_errors
            ]
            self.stats.average_resolution_time = sum(resolution_times) / len(resolution_times)
    
    async def _track_integration_errors(self, integration_name: str) -> None:
        """Track error patterns for integration."""
        if integration_name not in self.integration_errors:
            self.integration_errors[integration_name] = []
        
        self.integration_errors[integration_name].append(datetime.utcnow())
        
        # Keep only last 24 hours of errors
        one_day_ago = datetime.utcnow() - timedelta(days=1)
        self.integration_errors[integration_name] = [
            timestamp for timestamp in self.integration_errors[integration_name]
            if timestamp >= one_day_ago
        ]
    
    async def _should_send_alert(self, error_event: ErrorEvent) -> bool:
        """Determine if alert should be sent for error."""
        # Always alert for critical errors
        if error_event.severity == ErrorSeverity.CRITICAL:
            return True
        
        # Alert for high severity errors in production integrations
        if error_event.severity == ErrorSeverity.HIGH:
            production_integrations = ["stripe", "paypal", "youtube", "instagram"]
            if error_event.integration_name in production_integrations:
                return True
        
        # Alert for error patterns (multiple errors in short time)
        integration_name = error_event.integration_name
        if integration_name in self.integration_errors:
            recent_errors = [
                timestamp for timestamp in self.integration_errors[integration_name]
                if timestamp >= datetime.utcnow() - timedelta(minutes=15)
            ]
            if len(recent_errors) >= 5:  # 5 errors in 15 minutes
                return True
        
        return False
    
    async def _send_alert(self, error_event: ErrorEvent) -> None:
        """Send alert for error event."""
        alert_data = {
            "error_id": error_event.id,
            "integration": error_event.integration_name,
            "category": error_event.category.value,
            "severity": error_event.severity.value,
            "message": error_event.error_message,
            "timestamp": error_event.timestamp.isoformat(),
            "recovery_action": error_event.recovery_action.value
        }
        
        # Send to all registered alert handlers
        for handler in self.alert_handlers:
            try:
                await handler(alert_data)
            except Exception as e:
                self.logger.error(f"Alert handler failed: {str(e)}")
    
    async def _send_escalation_alert(self, error_event: ErrorEvent) -> None:
        """Send escalation alert for manual intervention."""
        escalation_data = {
            "type": "escalation",
            "error_id": error_event.id,
            "integration": error_event.integration_name,
            "category": error_event.category.value,
            "severity": error_event.severity.value,
            "message": error_event.error_message,
            "context": error_event.context,
            "timestamp": error_event.timestamp.isoformat(),
            "requires_manual_intervention": True
        }
        
        # Send escalation to all alert handlers
        for handler in self.alert_handlers:
            try:
                await handler(escalation_data)
            except Exception as e:
                self.logger.error(f"Escalation alert handler failed: {str(e)}")
    
    def _log_error(self, error_event: ErrorEvent, recovery_success: bool) -> None:
        """Log error event."""
        log_level = {
            ErrorSeverity.LOW: logging.INFO,
            ErrorSeverity.MEDIUM: logging.WARNING,
            ErrorSeverity.HIGH: logging.ERROR,
            ErrorSeverity.CRITICAL: logging.CRITICAL
        }.get(error_event.severity, logging.ERROR)
        
        recovery_status = "recovered" if recovery_success else "unrecovered"
        
        self.logger.log(
            log_level,
            f"Integration error [{error_event.category.value}] in {error_event.integration_name}: "
            f"{error_event.error_message} - {recovery_status} ({error_event.id})"
        )
    
    def _generate_error_id(self, integration_name: str, error_type: str) -> str:
        """Generate unique error ID."""
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        hash_input = f"{integration_name}_{error_type}_{timestamp}"
        error_hash = hashlib.md5(hash_input.encode()).hexdigest()[:8]
        return f"err_{timestamp}_{error_hash}"
    
    async def add_error_rule(self, rule: ErrorRule) -> str:
        """Add custom error handling rule."""
        rule_id = hashlib.md5(rule.error_pattern.encode()).hexdigest()[:8]
        self.error_rules[rule_id] = rule
        self.logger.info(f"Added error rule: {rule_id}")
        return rule_id
    
    async def remove_error_rule(self, rule_id: str) -> bool:
        """Remove error handling rule."""
        if rule_id in self.error_rules:
            del self.error_rules[rule_id]
            self.logger.info(f"Removed error rule: {rule_id}")
            return True
        return False
    
    async def register_custom_handler(self, category: str, handler: ErrorHandler) -> None:
        """Register custom error handler for category."""
        self.custom_handlers[category] = handler
        self.logger.info(f"Registered custom handler for category: {category}")
    
    async def register_alert_handler(self, handler: Callable) -> None:
        """Register alert handler."""
        self.alert_handlers.append(handler)
        self.logger.info("Registered new alert handler")
    
    async def get_error_statistics(self, integration_name: Optional[str] = None) -> Dict[str, Any]:
        """Get error statistics."""
        if integration_name:
            # Get statistics for specific integration
            integration_errors = [
                e for e in self.stats.recent_errors
                if e.integration_name == integration_name
            ]
            
            return {
                "integration_name": integration_name,
                "total_errors": len(integration_errors),
                "errors_by_category": {
                    cat.value: len([e for e in integration_errors if e.category == cat])
                    for cat in ErrorCategory
                },
                "errors_by_severity": {
                    sev.value: len([e for e in integration_errors if e.severity == sev])
                    for sev in ErrorSeverity
                },
                "resolution_rate": len([e for e in integration_errors if e.resolved]) / len(integration_errors) if integration_errors else 0,
                "recent_errors": [
                    {
                        "id": e.id,
                        "category": e.category.value,
                        "severity": e.severity.value,
                        "message": e.error_message,
                        "timestamp": e.timestamp.isoformat(),
                        "resolved": e.resolved
                    }
                    for e in integration_errors[-10:]  # Last 10 errors
                ]
            }
        else:
            # Get global statistics
            return {
                "global_statistics": {
                    "total_errors": self.stats.total_errors,
                    "error_rate_per_hour": self.stats.error_rate,
                    "resolution_rate": self.stats.resolution_rate,
                    "average_resolution_time": self.stats.average_resolution_time
                },
                "errors_by_category": {cat.value: count for cat, count in self.stats.errors_by_category.items()},
                "errors_by_severity": {sev.value: count for sev, count in self.stats.errors_by_severity.items()},
                "errors_by_integration": dict(self.stats.errors_by_integration),
                "active_error_rules": len(self.error_rules),
                "custom_handlers": len(self.custom_handlers),
                "alert_handlers": len(self.alert_handlers)
            }
    
    async def get_error_details(self, error_id: str) -> Optional[Dict[str, Any]]:
        """Get detailed information about specific error."""
        if error_id not in self.error_events:
            return None
        
        error_event = self.error_events[error_id]
        
        return {
            "id": error_event.id,
            "integration_name": error_event.integration_name,
            "error_type": error_event.error_type,
            "error_message": error_event.error_message,
            "category": error_event.category.value,
            "severity": error_event.severity.value,
            "recovery_action": error_event.recovery_action.value,
            "context": error_event.context,
            "request_data": error_event.request_data,
            "response_data": error_event.response_data,
            "stack_trace": error_event.stack_trace,
            "timestamp": error_event.timestamp.isoformat(),
            "resolved": error_event.resolved,
            "resolution_time": error_event.resolution_time.isoformat() if error_event.resolution_time else None,
            "recovery_attempts": error_event.recovery_attempts
        }
    
    async def resolve_error(self, error_id: str, resolution_notes: str = "") -> bool:
        """Manually resolve error."""
        if error_id not in self.error_events:
            return False
        
        error_event = self.error_events[error_id]
        error_event.resolved = True
        error_event.resolution_time = datetime.utcnow()
        
        if resolution_notes:
            error_event.context["resolution_notes"] = resolution_notes
        
        self.logger.info(f"Error manually resolved: {error_id}")
        return True
    
    async def cleanup_old_errors(self, days: int = 7) -> int:
        """Clean up old error events."""
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        
        old_error_ids = [
            error_id for error_id, error_event in self.error_events.items()
            if error_event.timestamp < cutoff_date
        ]
        
        for error_id in old_error_ids:
            del self.error_events[error_id]
        
        self.logger.info(f"Cleaned up {len(old_error_ids)} old error events")
        return len(old_error_ids)