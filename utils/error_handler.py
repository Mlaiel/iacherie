"""
Error Handler Utilities - Enterprise Grade
==========================================

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.

Expert Roles: DevOps Expert + Backend Senior + Lead Dev IA
Provides comprehensive error handling and management for enterprise applications.
"""

import traceback
import logging
import json
import uuid
import asyncio
from typing import Any, Dict, List, Optional, Union, Callable, Type
from datetime import datetime, timezone
from dataclasses import dataclass, asdict
from enum import Enum
import functools
import threading
import time
from collections import defaultdict, deque
import smtplib
from email.mime.text import MimeText
from email.mime.multipart import MimeMultipart


class ErrorSeverity(Enum):
    """Error severity levels."""
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"
    FATAL = "FATAL"


class ErrorCategory(Enum):
    """Error categories for classification."""
    AUTHENTICATION = "AUTHENTICATION"
    AUTHORIZATION = "AUTHORIZATION"
    VALIDATION = "VALIDATION"
    DATABASE = "DATABASE"
    NETWORK = "NETWORK"
    FILE_SYSTEM = "FILE_SYSTEM"
    EXTERNAL_API = "EXTERNAL_API"
    BUSINESS_LOGIC = "BUSINESS_LOGIC"
    CONFIGURATION = "CONFIGURATION"
    PERFORMANCE = "PERFORMANCE"
    SECURITY = "SECURITY"
    UNKNOWN = "UNKNOWN"


@dataclass
class ErrorContext:
    """Context information for errors."""
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    request_id: Optional[str] = None
    endpoint: Optional[str] = None
    method: Optional[str] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    timestamp: Optional[datetime] = None
    additional_data: Optional[Dict[str, Any]] = None


@dataclass
class ErrorRecord:
    """Complete error record with all metadata."""
    error_id: str
    severity: ErrorSeverity
    category: ErrorCategory
    message: str
    exception_type: str
    traceback_info: str
    context: ErrorContext
    timestamp: datetime
    resolved: bool = False
    resolution_notes: Optional[str] = None
    occurrences: int = 1
    first_occurrence: Optional[datetime] = None
    last_occurrence: Optional[datetime] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            'error_id': self.error_id,
            'severity': self.severity.value,
            'category': self.category.value,
            'message': self.message,
            'exception_type': self.exception_type,
            'traceback_info': self.traceback_info,
            'context': asdict(self.context) if self.context else None,
            'timestamp': self.timestamp.isoformat(),
            'resolved': self.resolved,
            'resolution_notes': self.resolution_notes,
            'occurrences': self.occurrences,
            'first_occurrence': self.first_occurrence.isoformat() if self.first_occurrence else None,
            'last_occurrence': self.last_occurrence.isoformat() if self.last_occurrence else None
        }


class ErrorHandler:
    """
    Enterprise-grade error handling utility.
    
    Features:
    - Centralized error capture and logging
    - Error categorization and severity classification
    - Context-aware error tracking
    - Error aggregation and deduplication
    - Automatic alerting and notifications
    - Error resolution tracking
    - Performance impact monitoring
    - Custom error recovery strategies
    """
    
    def __init__(self, 
                 app_name -> None: str = "Ainflue",
                 log_level -> None: str = "INFO",
                 enable_alerts -> None: bool = True,
                 alert_threshold -> None: int = 5,
                 aggregation_window -> None: int = 300) -> None:  # 5 minutes
        
        self.app_name = app_name
        self.enable_alerts = enable_alerts
        self.alert_threshold = alert_threshold
        self.aggregation_window = aggregation_window
        
        # Initialize logging
        self.logger = self._setup_logger(log_level)
        
        # Error storage and tracking
        self.error_records: Dict[str, ErrorRecord] = {}
        self.error_counts: defaultdict = defaultdict(int)
        self.recent_errors: deque = deque(maxlen=1000)
        
        # Thread safety
        self._lock = threading.RLock()
        
        # Error categorization patterns
        self.categorization_patterns = {
            ErrorCategory.AUTHENTICATION: [
                'authentication', 'login', 'token', 'unauthorized', 'credentials'
            ],
            ErrorCategory.AUTHORIZATION: [
                'permission', 'access denied', 'forbidden', 'privilege'
            ],
            ErrorCategory.VALIDATION: [
                'validation', 'invalid', 'format', 'required field', 'constraint'
            ],
            ErrorCategory.DATABASE: [
                'database', 'sql', 'connection', 'query', 'orm', 'transaction'
            ],
            ErrorCategory.NETWORK: [
                'network', 'connection', 'timeout', 'dns', 'socket', 'http'
            ],
            ErrorCategory.FILE_SYSTEM: [
                'file', 'directory', 'path', 'permission denied', 'disk space'
            ],
            ErrorCategory.EXTERNAL_API: [
                'api', 'service', 'external', 'third-party', 'integration'
            ],
            ErrorCategory.PERFORMANCE: [
                'timeout', 'slow', 'memory', 'cpu', 'performance', 'throttle'
            ],
            ErrorCategory.SECURITY: [
                'security', 'attack', 'vulnerability', 'injection', 'xss', 'csrf'
            ]
        }
        
        # Recovery strategies
        self.recovery_strategies: Dict[ErrorCategory, List[Callable]] = defaultdict(list)
        self._setup_default_recovery_strategies()
        
        # Alert handlers
        self.alert_handlers: List[Callable] = []
    
    def _setup_logger(self, log_level: str) -> logging.Logger:
        """Setup structured logging."""
        logger = logging.getLogger(f"{self.app_name}.error_handler")
        logger.setLevel(getattr(logging, log_level.upper()))
        
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
        
        return logger
    
    def _setup_default_recovery_strategies(self) -> None:
        """Setup default error recovery strategies."""
        # Database connection recovery
        self.recovery_strategies[ErrorCategory.DATABASE].append(
            self._recover_database_connection
        )
        
        # Network retry strategy
        self.recovery_strategies[ErrorCategory.NETWORK].append(
            self._recover_network_request
        )
        
        # External API retry with backoff
        self.recovery_strategies[ErrorCategory.EXTERNAL_API].append(
            self._recover_external_api
        )
    
    def capture_exception(self, 
                         exception: Exception,
                         context: Optional[ErrorContext] = None,
                         category: Optional[ErrorCategory] = None,
                         severity: Optional[ErrorSeverity] = None,
                         custom_message: Optional[str] = None) -> str:
        """
        Capture and process an exception.
        
        Returns:
            str: Unique error ID
        """
        with self._lock:
            error_id = str(uuid.uuid4())
            
            # Determine category if not provided
            if category is None:
                category = self._categorize_error(exception)
            
            # Determine severity if not provided
            if severity is None:
                severity = self._determine_severity(exception, category)
            
            # Create error context if not provided
            if context is None:
                context = ErrorContext(timestamp=datetime.now(timezone.utc))
            elif context.timestamp is None:
                context.timestamp = datetime.now(timezone.utc)
            
            # Create error record
            error_record = ErrorRecord(
                error_id=error_id,
                severity=severity,
                category=category,
                message=custom_message or str(exception),
                exception_type=type(exception).__name__,
                traceback_info=traceback.format_exc(),
                context=context,
                timestamp=datetime.now(timezone.utc),
                first_occurrence=datetime.now(timezone.utc),
                last_occurrence=datetime.now(timezone.utc)
            )
            
            # Check for duplicate errors
            duplicate_id = self._find_duplicate_error(error_record)
            if duplicate_id:
                self._update_duplicate_error(duplicate_id, error_record)
                error_id = duplicate_id
            else:
                self.error_records[error_id] = error_record
            
            # Add to recent errors
            self.recent_errors.append(error_id)
            
            # Update error counts
            self.error_counts[f"{category.value}:{severity.value}"] += 1
            
            # Log the error
            self._log_error(error_record)
            
            # Check if alert should be triggered
            if self.enable_alerts and self._should_trigger_alert(error_record):
                self._trigger_alert(error_record)
            
            # Attempt automatic recovery
            if severity in [ErrorSeverity.ERROR, ErrorSeverity.CRITICAL]:
                self._attempt_recovery(error_record, exception)
            
            return error_id
    
    def capture_error_message(self,
                             message: str,
                             category: ErrorCategory,
                             severity: ErrorSeverity = ErrorSeverity.ERROR,
                             context: Optional[ErrorContext] = None) -> str:
        """Capture a custom error message."""
        # Create a custom exception for the message
        exception = Exception(message)
        return self.capture_exception(exception, context, category, severity, message)
    
    def mark_error_resolved(self, error_id -> None: str, resolution_notes -> None: str = "") -> None:
        """Mark an error as resolved."""
        with self._lock:
            if error_id in self.error_records:
                self.error_records[error_id].resolved = True
                self.error_records[error_id].resolution_notes = resolution_notes
                
                self.logger.info(f"Error {error_id} marked as resolved: {resolution_notes}")
    
    def get_error_record(self, error_id: str) -> Optional[ErrorRecord]:
        """Get error record by ID."""
        return self.error_records.get(error_id)
    
    def get_error_statistics(self, 
                           time_window: int = 3600,
                           group_by: str = "category") -> Dict[str, Any]:
        """Get error statistics for a time window."""
        cutoff_time = datetime.now(timezone.utc) - timedelta(seconds=time_window)
        
        stats = {
            'total_errors': 0,
            'by_severity': defaultdict(int),
            'by_category': defaultdict(int),
            'unresolved_count': 0,
            'most_frequent': []
        }
        
        error_frequency = defaultdict(int)
        
        for error_record in self.error_records.values():
            if error_record.timestamp >= cutoff_time:
                stats['total_errors'] += error_record.occurrences
                stats['by_severity'][error_record.severity.value] += error_record.occurrences
                stats['by_category'][error_record.category.value] += error_record.occurrences
                
                if not error_record.resolved:
                    stats['unresolved_count'] += 1
                
                # Track frequency by error message
                error_frequency[error_record.message] += error_record.occurrences
        
        # Get most frequent errors
        stats['most_frequent'] = sorted(
            error_frequency.items(),
            key=lambda x: x[1],
            reverse=True
        )[:10]
        
        return stats
    
    def get_recent_errors(self, 
                         limit: int = 50,
                         severity_filter: Optional[ErrorSeverity] = None,
                         category_filter: Optional[ErrorCategory] = None) -> List[ErrorRecord]:
        """Get recent errors with optional filtering."""
        recent_error_ids = list(self.recent_errors)[-limit:]
        
        filtered_errors = []
        for error_id in reversed(recent_error_ids):
            if error_id in self.error_records:
                error_record = self.error_records[error_id]
                
                # Apply filters
                if severity_filter and error_record.severity != severity_filter:
                    continue
                
                if category_filter and error_record.category != category_filter:
                    continue
                
                filtered_errors.append(error_record)
        
        return filtered_errors
    
    def add_alert_handler(self, handler -> None: Callable[[ErrorRecord], None]) -> None:
        """Add custom alert handler."""
        self.alert_handlers.append(handler)
    
    def add_recovery_strategy(self, 
                             category -> None: ErrorCategory,
                             strategy -> None: Callable[[ErrorRecord, Exception], bool]) -> None:
        """Add custom recovery strategy."""
        self.recovery_strategies[category].append(strategy)
    
    def _categorize_error(self, exception: Exception) -> ErrorCategory:
        """Automatically categorize error based on exception type and message."""
        exception_str = str(exception).lower()
        exception_type = type(exception).__name__.lower()
        
        for category, patterns in self.categorization_patterns.items():
            for pattern in patterns:
                if pattern in exception_str or pattern in exception_type:
                    return category
        
        # Special handling for common exception types
        if isinstance(exception, (ConnectionError, TimeoutError)):
            return ErrorCategory.NETWORK
        elif isinstance(exception, (FileNotFoundError, PermissionError)):
            return ErrorCategory.FILE_SYSTEM
        elif isinstance(exception, ValueError):
            return ErrorCategory.VALIDATION
        elif isinstance(exception, KeyError):
            return ErrorCategory.CONFIGURATION
        
        return ErrorCategory.UNKNOWN
    
    def _determine_severity(self, exception: Exception, category: ErrorCategory) -> ErrorSeverity:
        """Determine error severity based on exception and category."""
        # Critical errors that could crash the system
        if isinstance(exception, (SystemExit, KeyboardInterrupt, MemoryError)):
            return ErrorSeverity.FATAL
        
        # Security-related errors are critical
        if category == ErrorCategory.SECURITY:
            return ErrorSeverity.CRITICAL
        
        # Database and authentication errors are typically errors
        if category in [ErrorCategory.DATABASE, ErrorCategory.AUTHENTICATION]:
            return ErrorSeverity.ERROR
        
        # Validation and configuration issues are warnings
        if category in [ErrorCategory.VALIDATION, ErrorCategory.CONFIGURATION]:
            return ErrorSeverity.WARNING
        
        # Default to ERROR for unhandled exceptions
        return ErrorSeverity.ERROR
    
    def _find_duplicate_error(self, error_record: ErrorRecord) -> Optional[str]:
        """Find if this error is a duplicate of an existing one."""
        for existing_id, existing_record in self.error_records.items():
            if (existing_record.exception_type == error_record.exception_type and
                existing_record.message == error_record.message and
                existing_record.category == error_record.category and
                not existing_record.resolved):
                return existing_id
        
        return None
    
    def _update_duplicate_error(self, error_id -> None: str, new_error -> None: ErrorRecord) -> None:
        """Update existing error record with new occurrence."""
        existing_record = self.error_records[error_id]
        existing_record.occurrences += 1
        existing_record.last_occurrence = new_error.timestamp
        
        # Update context if more detailed
        if (new_error.context and new_error.context.additional_data and
            (not existing_record.context or not existing_record.context.additional_data)):
            existing_record.context = new_error.context
    
    def _log_error(self, error_record -> None: ErrorRecord) -> None:
        """Log error record using structured logging."""
        log_data = {
            'error_id': error_record.error_id,
            'severity': error_record.severity.value,
            'category': error_record.category.value,
            'message': error_record.message,
            'exception_type': error_record.exception_type,
            'context': asdict(error_record.context) if error_record.context else None
        }
        
        if error_record.severity in [ErrorSeverity.FATAL, ErrorSeverity.CRITICAL]:
            self.logger.critical(json.dumps(log_data))
        elif error_record.severity == ErrorSeverity.ERROR:
            self.logger.error(json.dumps(log_data))
        elif error_record.severity == ErrorSeverity.WARNING:
            self.logger.warning(json.dumps(log_data))
        else:
            self.logger.info(json.dumps(log_data))
    
    def _should_trigger_alert(self, error_record: ErrorRecord) -> bool:
        """Determine if an alert should be triggered."""
        # Always alert for critical and fatal errors
        if error_record.severity in [ErrorSeverity.FATAL, ErrorSeverity.CRITICAL]:
            return True
        
        # Alert if error threshold exceeded
        category_key = f"{error_record.category.value}:{error_record.severity.value}"
        recent_count = self.error_counts[category_key]
        
        return recent_count >= self.alert_threshold
    
    def _trigger_alert(self, error_record -> None: ErrorRecord) -> None:
        """Trigger alerts for the error."""
        for handler in self.alert_handlers:
            try:
                handler(error_record)
            except Exception as e:
                self.logger.error(f"Alert handler failed: {str(e)}")
    
    def _attempt_recovery(self, error_record -> None: ErrorRecord, exception -> None: Exception) -> None:
        """Attempt automatic error recovery."""
        strategies = self.recovery_strategies.get(error_record.category, [])
        
        for strategy in strategies:
            try:
                if strategy(error_record, exception):
                    self.logger.info(f"Recovery successful for error {error_record.error_id}")
                    self.mark_error_resolved(error_record.error_id, "Automatic recovery")
                    break
            except Exception as recovery_error:
                self.logger.error(f"Recovery strategy failed: {str(recovery_error)}")
    
    def _recover_database_connection(self, error_record: ErrorRecord, exception: Exception) -> bool:
        """Attempt to recover database connection."""
        # This is a placeholder - actual implementation would depend on the database system
        self.logger.info("Attempting database connection recovery")
        return False
    
    def _recover_network_request(self, error_record: ErrorRecord, exception: Exception) -> bool:
        """Attempt to recover network request with retry."""
        # This is a placeholder - actual implementation would retry the request
        self.logger.info("Attempting network request recovery")
        return False
    
    def _recover_external_api(self, error_record: ErrorRecord, exception: Exception) -> bool:
        """Attempt to recover external API call with exponential backoff."""
        # This is a placeholder - actual implementation would use exponential backoff
        self.logger.info("Attempting external API recovery")
        return False


# Decorator for automatic error handling
def handle_errors(category -> None: ErrorCategory = ErrorCategory.UNKNOWN,
                 severity -> None: ErrorSeverity = ErrorSeverity.ERROR,
                 reraise -> None: bool = True,
                 fallback_return -> None: Any = None) -> None:
    """Decorator for automatic error handling."""
    def decorator(func) -> None:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> None:
            try:
                return func(*args, **kwargs)
            except Exception as e:
                # Get error handler from global context or create one
                error_handler = getattr(wrapper, '_error_handler', None)
                if error_handler is None:
                    error_handler = ErrorHandler()
                
                # Create context
                context = ErrorContext(
                    additional_data={
                        'function': func.__name__,
                        'args': str(args)[:200],
                        'kwargs': str(kwargs)[:200]
                    }
                )
                
                # Capture error
                error_id = error_handler.capture_exception(e, context, category, severity)
                
                if reraise:
                    raise
                else:
                    return fallback_return
        
        return wrapper
    return decorator


# Async version of the decorator
def handle_errors_async(category -> None: ErrorCategory = ErrorCategory.UNKNOWN,
                       severity -> None: ErrorSeverity = ErrorSeverity.ERROR,
                       reraise -> None: bool = True,
                       fallback_return -> None: Any = None) -> None:
    """Async decorator for automatic error handling."""
    def decorator(func) -> None:
        @functools.wraps(func)
        async def wrapper(*args, **kwargs) -> None:
            try:
                return await func(*args, **kwargs)
            except Exception as e:
                # Get error handler from global context or create one
                error_handler = getattr(wrapper, '_error_handler', None)
                if error_handler is None:
                    error_handler = ErrorHandler()
                
                # Create context
                context = ErrorContext(
                    additional_data={
                        'function': func.__name__,
                        'args': str(args)[:200],
                        'kwargs': str(kwargs)[:200]
                    }
                )
                
                # Capture error
                error_id = error_handler.capture_exception(e, context, category, severity)
                
                if reraise:
                    raise
                else:
                    return fallback_return
        
        return wrapper
    return decorator


# Global error handler instance
global_error_handler = ErrorHandler()


# Convenience functions
def capture_exception(exception: Exception, 
                     context: Optional[ErrorContext] = None,
                     category: Optional[ErrorCategory] = None,
                     severity: Optional[ErrorSeverity] = None) -> str:
    """Capture exception using global error handler."""
    return global_error_handler.capture_exception(exception, context, category, severity)


def capture_error(message: str,
                 category: ErrorCategory,
                 severity: ErrorSeverity = ErrorSeverity.ERROR,
                 context: Optional[ErrorContext] = None) -> str:
    """Capture error message using global error handler."""
    return global_error_handler.capture_error_message(message, category, severity, context)


def get_error_stats(time_window: int = 3600) -> Dict[str, Any]:
    """Get error statistics from global error handler."""
    return global_error_handler.get_error_statistics(time_window)


# Example usage and testing
if __name__ == "__main__":
    from datetime import timedelta
    
    # Initialize error handler
    error_handler = ErrorHandler()
    
    # Test error capture
    try:
        raise ValueError("Test validation error")
    except Exception as e:
        error_id = error_handler.capture_exception(e)
        print(f"Captured error with ID: {error_id}")
    
    # Test decorator
    @handle_errors(category=ErrorCategory.BUSINESS_LOGIC)
    def risky_function() -> None:
        raise RuntimeError("Something went wrong")
    
    try:
        risky_function()
    except Exception:
        print("Error was captured and re-raised")
    
    # Get statistics
    stats = error_handler.get_error_statistics()
    print(f"Error statistics: {stats}")
    
    # Get recent errors
    recent = error_handler.get_recent_errors(limit=5)
    print(f"Recent errors: {len(recent)}")
    
    for error in recent:
        print(f"  {error.error_id}: {error.message} ({error.severity.value})")