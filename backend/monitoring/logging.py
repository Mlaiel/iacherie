"""📝 Unified Logging Module - IA Influencer Agent Platform
========================================================

Consolidated logging and error tracking system combining:
- Structured logging with JSON format
- Error aggregation and analysis
- Sentry integration for error tracking
- Log correlation and distributed tracing

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import logging
import logging.handlers
import json
import time
import traceback
import uuid
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
import sys
from collections import defaultdict, deque

logger = logging.getLogger(__name__)


class LogLevel(Enum):
    """Log levels"""
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class LogCategory(Enum):
    """Log categories for better organization"""
    SYSTEM = "system"
    APPLICATION = "application"
    BUSINESS = "business"
    SECURITY = "security"
    PERFORMANCE = "performance"
    AUDIT = "audit"
    ERROR = "error"
    ACCESS = "access"


class ErrorSeverity(Enum):
    """Error severity levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class LogEntry:
    """Structured log entry"""
    timestamp: datetime
    level: LogLevel
    category: LogCategory
    message: str
    logger_name: str = ""
    module: str = ""
    function: str = ""
    line_number: int = 0
    correlation_id: str = ""
    user_id: str = ""
    session_id: str = ""
    tags: Dict[str, str] = field(default_factory=dict)
    extra: Dict[str, Any] = field(default_factory=dict)
    stack_trace: str = ""


@dataclass
class ErrorReport:
    """Error report for tracking and analysis"""
    id: str
    title: str
    message: str
    severity: ErrorSeverity
    error_type: str
    occurred_at: datetime
    count: int = 1
    first_seen: datetime = field(default_factory=datetime.now)
    last_seen: datetime = field(default_factory=datetime.now)
    stack_trace: str = ""
    context: Dict[str, Any] = field(default_factory=dict)
    tags: Dict[str, str] = field(default_factory=dict)
    fingerprint: str = ""


class StructuredFormatter(logging.Formatter):
    """JSON formatter for structured logging"""
    
    def __init__(self) -> None:
        super().__init__()
    
    def format(self, record: logging.LogRecord) -> str:
        """Format log record as JSON"""
        
        # Base log data
        log_data = {
            "timestamp": datetime.fromtimestamp(record.created).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
            "process": record.process,
            "thread": record.thread
        }
        
        # Add correlation ID if available
        correlation_id = getattr(record, 'correlation_id', None)
        if correlation_id:
            log_data["correlation_id"] = correlation_id
        
        # Add user context if available
        user_id = getattr(record, 'user_id', None)
        if user_id:
            log_data["user_id"] = user_id
        
        session_id = getattr(record, 'session_id', None)
        if session_id:
            log_data["session_id"] = session_id
        
        # Add category if available
        category = getattr(record, 'category', None)
        if category:
            log_data["category"] = category
        
        # Add extra fields
        extra = getattr(record, 'extra', {})
        if extra:
            log_data["extra"] = extra
        
        # Add exception information if available
        if record.exc_info:
            log_data["exception"] = {
                "type": record.exc_info[0].__name__ if record.exc_info[0] else None,
                "message": str(record.exc_info[1]) if record.exc_info[1] else None,
                "traceback": traceback.format_exception(*record.exc_info)
            }
        
        return json.dumps(log_data, default=str, ensure_ascii=False)


class ErrorAggregator:
    """Aggregate and track errors for analysis"""
    
    def __init__(self) -> None:
        self.errors: Dict[str, ErrorReport] = {}
        self.error_history: deque = deque(maxlen=10000)
        self.error_stats = defaultdict(int)
    
    def record_error(
        self,
        title: str,
        message: str,
        error_type: str,
        severity: ErrorSeverity = ErrorSeverity.MEDIUM,
        stack_trace: str = "",
        context: Optional[Dict[str, Any]] = None,
        tags: Optional[Dict[str, str]] = None
    ) -> str:
        """Record an error occurrence"""
        
        # Generate fingerprint for grouping similar errors
        fingerprint = self._generate_fingerprint(title, error_type, stack_trace)
        
        if fingerprint in self.errors:
            # Update existing error
            error = self.errors[fingerprint]
            error.count += 1
            error.last_seen = datetime.now()
            error.message = message  # Update with latest message
            if context:
                error.context.update(context)
        else:
            # Create new error report
            error_id = str(uuid.uuid4())[:8]
            error = ErrorReport(
                id=error_id,
                title=title,
                message=message,
                severity=severity,
                error_type=error_type,
                occurred_at=datetime.now(),
                stack_trace=stack_trace,
                context=context or {},
                tags=tags or {},
                fingerprint=fingerprint
            )
            self.errors[fingerprint] = error
        
        # Add to history
        self.error_history.append({
            "timestamp": datetime.now(),
            "fingerprint": fingerprint,
            "error_id": error.id,
            "severity": severity.value
        })
        
        # Update statistics
        self.error_stats[error_type] += 1
        self.error_stats[f"severity_{severity.value}"] += 1
        
        return error.id
    
    def _generate_fingerprint(self, title: str, error_type: str, stack_trace: str) -> str:
        """Generate fingerprint for error grouping"""
        # Use title and error type for basic grouping
        base = f"{title}_{error_type}"
        
        # Add stack trace signature if available
        if stack_trace:
            # Extract the most relevant part of stack trace
            lines = stack_trace.split('\n')
            relevant_lines = [line.strip() for line in lines if 'File "' in line]
            if relevant_lines:
                base += "_" + str(hash("".join(relevant_lines[-3:])))  # Last 3 stack frames
        
        return str(hash(base))
    
    def get_error_summary(self) -> Dict[str, Any]:
        """Get error summary statistics"""
        now = datetime.now()
        hour_ago = now - timedelta(hours=1)
        day_ago = now - timedelta(days=1)
        
        # Count recent errors
        recent_errors_1h = sum(
            1 for entry in self.error_history
            if entry["timestamp"] >= hour_ago
        )
        
        recent_errors_24h = sum(
            1 for entry in self.error_history
            if entry["timestamp"] >= day_ago
        )
        
        # Group by severity
        severity_counts = defaultdict(int)
        for error in self.errors.values():
            severity_counts[error.severity.value] += error.count
        
        return {
            "total_unique_errors": len(self.errors),
            "total_error_occurrences": sum(error.count for error in self.errors.values()),
            "recent_errors_1h": recent_errors_1h,
            "recent_errors_24h": recent_errors_24h,
            "errors_by_severity": dict(severity_counts),
            "error_types": dict(self.error_stats)
        }
    
    def get_top_errors(self, limit: int = 10) -> List[ErrorReport]:
        """Get top errors by occurrence count"""
        return sorted(
            self.errors.values(),
            key=lambda x: x.count,
            reverse=True
        )[:limit]
    
    def get_error_by_id(self, error_id: str) -> Optional[ErrorReport]:
        """Get error report by ID"""
        for error in self.errors.values():
            if error.id == error_id:
                return error
        return None


class SentryIntegration:
    """Sentry integration for error tracking"""
    
    def __init__(self, config -> None: Dict[str, Any]) -> None:
        self.config = config
        self.dsn = config.get("dsn", "")
        self.environment = config.get("environment", "production")
        self.enabled = bool(self.dsn)
        
        if self.enabled:
            try:
                import sentry_sdk
                sentry_sdk.init(
                    dsn=self.dsn,
                    environment=self.environment,
                    traces_sample_rate=config.get("traces_sample_rate", 0.1)
                )
                logger.info("Sentry integration initialized")
            except ImportError:
                logger.warning("Sentry SDK not available")
                self.enabled = False
    
    def capture_error(
        self,
        error -> None: Exception,
        context -> None: Optional[Dict[str, Any]] = None,
        tags -> None: Optional[Dict[str, str]] = None,
        user -> None: Optional[Dict[str, str]] = None
    ) -> None:
        """Capture error to Sentry"""
        if not self.enabled:
            return
        
        try:
            import sentry_sdk
            
            with sentry_sdk.push_scope() as scope:
                if context:
                    for key, value in context.items():
                        scope.set_context(key, value)
                
                if tags:
                    for key, value in tags.items():
                        scope.set_tag(key, value)
                
                if user:
                    scope.set_user(user)
                
                sentry_sdk.capture_exception(error)
                
        except Exception as e:
            logger.error(f"Failed to capture error to Sentry: {e}")
    
    def capture_message(
        self,
        message -> None: str,
        level -> None: str = "info",
        tags -> None: Optional[Dict[str, str]] = None
    ) -> None:
        """Capture message to Sentry"""
        if not self.enabled:
            return
        
        try:
            import sentry_sdk
            
            with sentry_sdk.push_scope() as scope:
                if tags:
                    for key, value in tags.items():
                        scope.set_tag(key, value)
                
                sentry_sdk.capture_message(message, level=level)
                
        except Exception as e:
            logger.error(f"Failed to capture message to Sentry: {e}")


class LogCorrelation:
    """Log correlation for distributed tracing"""
    
    def __init__(self) -> None:
        self.active_correlations: Dict[str, Dict[str, Any]] = {}
        self.correlation_history: deque = deque(maxlen=1000)
    
    def start_correlation(self, operation: str, **kwargs) -> str:
        """Start a new log correlation"""
        correlation_id = str(uuid.uuid4())
        
        correlation = {
            "id": correlation_id,
            "operation": operation,
            "started_at": datetime.now(),
            "context": kwargs,
            "log_count": 0
        }
        
        self.active_correlations[correlation_id] = correlation
        return correlation_id
    
    def add_log(self, correlation_id -> None: str, log_entry -> None: LogEntry) -> None:
        """Add log entry to correlation"""
        if correlation_id in self.active_correlations:
            self.active_correlations[correlation_id]["log_count"] += 1
    
    def end_correlation(self, correlation_id -> None: str, **kwargs) -> None:
        """End a log correlation"""
        if correlation_id in self.active_correlations:
            correlation = self.active_correlations.pop(correlation_id)
            correlation["ended_at"] = datetime.now()
            correlation["duration_ms"] = (
                correlation["ended_at"] - correlation["started_at"]
            ).total_seconds() * 1000
            correlation["end_context"] = kwargs
            
            self.correlation_history.append(correlation)
    
    def get_correlation(self, correlation_id: str) -> Optional[Dict[str, Any]]:
        """Get correlation by ID"""
        return self.active_correlations.get(correlation_id)


class UnifiedLoggingManager:
    """
    Unified logging system that consolidates all logging functionality
    """
    
    def __init__(self, config -> None: Optional[Dict[str, Any]] = None) -> None:
        self.config = config or {}
        
        # Initialize components
        self.error_aggregator = ErrorAggregator()
        self.sentry = SentryIntegration(self.config.get("sentry", {}))
        self.correlation = LogCorrelation()
        
        # Logging state
        self.log_buffer: deque = deque(maxlen=10000)
        self.log_stats = defaultdict(int)
        
        # Setup structured logging
        self._setup_structured_logging()
    
    def _setup_structured_logging(self) -> None:
        """Setup structured logging configuration"""
        
        # Create structured formatter
        formatter = StructuredFormatter()
        
        # Setup console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)
        console_handler.setLevel(logging.INFO)
        
        # Setup file handler if configured
        if self.config.get("log_file"):
            log_file = Path(self.config["log_file"])
            log_file.parent.mkdir(parents=True, exist_ok=True)
            
            file_handler = logging.handlers.RotatingFileHandler(
                log_file,
                maxBytes=self.config.get("max_log_size", 100 * 1024 * 1024),  # 100MB
                backupCount=self.config.get("backup_count", 5)
            )
            file_handler.setFormatter(formatter)
            file_handler.setLevel(logging.DEBUG)
            
            # Add handlers to root logger
            root_logger = logging.getLogger()
            root_logger.addHandler(file_handler)
        
        # Add console handler to root logger
        root_logger = logging.getLogger()
        root_logger.addHandler(console_handler)
        root_logger.setLevel(logging.DEBUG)
        
        # Setup error handler
        error_handler = ErrorCapturingHandler(self)
        error_handler.setLevel(logging.ERROR)
        root_logger.addHandler(error_handler)
    
    def log_structured(
        self,
        level -> None: LogLevel,
        message -> None: str,
        category -> None: LogCategory = LogCategory.APPLICATION,
        correlation_id -> None: Optional[str] = None,
        user_id -> None: Optional[str] = None,
        session_id -> None: Optional[str] = None,
        tags -> None: Optional[Dict[str, str]] = None,
        extra -> None: Optional[Dict[str, Any]] = None,
        logger_name -> None: str = "",
        **kwargs
    ) -> None:
        """Log structured message"""
        
        # Create log entry
        log_entry = LogEntry(
            timestamp=datetime.now(),
            level=level,
            category=category,
            message=message,
            logger_name=logger_name or __name__,
            correlation_id=correlation_id or "",
            user_id=user_id or "",
            session_id=session_id or "",
            tags=tags or {},
            extra=extra or {}
        )
        
        # Add to buffer
        self.log_buffer.append(log_entry)
        
        # Update statistics
        self.log_stats[f"level_{level.value.lower()}"] += 1
        self.log_stats[f"category_{category.value}"] += 1
        
        # Add to correlation if available
        if correlation_id:
            self.correlation.add_log(correlation_id, log_entry)
        
        # Use standard logging
        logger_instance = logging.getLogger(logger_name or __name__)
        
        # Add extra attributes to log record
        extra_attrs = {
            "category": category.value,
            "correlation_id": correlation_id,
            "user_id": user_id,
            "session_id": session_id,
            "extra": extra or {}
        }
        
        # Log with appropriate level
        if level == LogLevel.DEBUG:
            logger_instance.debug(message, extra=extra_attrs, **kwargs)
        elif level == LogLevel.INFO:
            logger_instance.info(message, extra=extra_attrs, **kwargs)
        elif level == LogLevel.WARNING:
            logger_instance.warning(message, extra=extra_attrs, **kwargs)
        elif level == LogLevel.ERROR:
            logger_instance.error(message, extra=extra_attrs, **kwargs)
        elif level == LogLevel.CRITICAL:
            logger_instance.critical(message, extra=extra_attrs, **kwargs)
    
    def log_error(
        self,
        error: Exception,
        title: str = "",
        severity: ErrorSeverity = ErrorSeverity.MEDIUM,
        context: Optional[Dict[str, Any]] = None,
        tags: Optional[Dict[str, str]] = None,
        user_id: Optional[str] = None,
        correlation_id: Optional[str] = None
    ) -> str:
        """Log and track error"""
        
        error_title = title or f"{type(error).__name__}: {str(error)}"
        stack_trace = traceback.format_exc()
        
        # Record in error aggregator
        error_id = self.error_aggregator.record_error(
            title=error_title,
            message=str(error),
            error_type=type(error).__name__,
            severity=severity,
            stack_trace=stack_trace,
            context=context,
            tags=tags
        )
        
        # Send to Sentry
        user_context = {"id": user_id} if user_id else None
        self.sentry.capture_error(error, context, tags, user_context)
        
        # Log structured error
        self.log_structured(
            level=LogLevel.ERROR,
            message=error_title,
            category=LogCategory.ERROR,
            correlation_id=correlation_id,
            user_id=user_id,
            tags=tags,
            extra={
                "error_id": error_id,
                "error_type": type(error).__name__,
                "severity": severity.value,
                "stack_trace": stack_trace,
                **(context or {})
            }
        )
        
        return error_id
    
    def log_business_event(
        self,
        event -> None: str,
        details -> None: Dict[str, Any],
        user_id -> None: Optional[str] = None,
        correlation_id -> None: Optional[str] = None
    ) -> None:
        """Log business event"""
        self.log_structured(
            level=LogLevel.INFO,
            message=f"Business event: {event}",
            category=LogCategory.BUSINESS,
            correlation_id=correlation_id,
            user_id=user_id,
            extra=details
        )
    
    def log_security_event(
        self,
        event -> None: str,
        details -> None: Dict[str, Any],
        user_id -> None: Optional[str] = None,
        severity -> None: LogLevel = LogLevel.WARNING
    ) -> None:
        """Log security event"""
        self.log_structured(
            level=severity,
            message=f"Security event: {event}",
            category=LogCategory.SECURITY,
            user_id=user_id,
            extra=details,
            tags={"security": "true"}
        )
        
        # Also send to Sentry for security events
        if severity in [LogLevel.ERROR, LogLevel.CRITICAL]:
            self.sentry.capture_message(
                f"Security event: {event}",
                level=severity.value.lower(),
                tags={"security": "true", "user_id": user_id or "unknown"}
            )
    
    def log_performance_metric(
        self,
        metric_name -> None: str,
        value -> None: float,
        unit -> None: str,
        tags -> None: Optional[Dict[str, str]] = None,
        correlation_id -> None: Optional[str] = None
    ) -> None:
        """Log performance metric"""
        self.log_structured(
            level=LogLevel.INFO,
            message=f"Performance metric: {metric_name} = {value} {unit}",
            category=LogCategory.PERFORMANCE,
            correlation_id=correlation_id,
            tags=tags,
            extra={
                "metric_name": metric_name,
                "metric_value": value,
                "metric_unit": unit
            }
        )
    
    def start_operation(self, operation: str, **kwargs) -> str:
        """Start a tracked operation with correlation"""
        correlation_id = self.correlation.start_correlation(operation, **kwargs)
        
        self.log_structured(
            level=LogLevel.INFO,
            message=f"Started operation: {operation}",
            category=LogCategory.APPLICATION,
            correlation_id=correlation_id,
            extra=kwargs
        )
        
        return correlation_id
    
    def end_operation(self, correlation_id -> None: str, success -> None: bool = True, **kwargs) -> None:
        """End a tracked operation"""
        correlation = self.correlation.get_correlation(correlation_id)
        if correlation:
            operation = correlation["operation"]
            
            self.log_structured(
                level=LogLevel.INFO if success else LogLevel.ERROR,
                message=f"{'Completed' if success else 'Failed'} operation: {operation}",
                category=LogCategory.APPLICATION,
                correlation_id=correlation_id,
                extra={**kwargs, "success": success}
            )
        
        self.correlation.end_correlation(correlation_id, success=success, **kwargs)
    
    def get_log_statistics(self) -> Dict[str, Any]:
        """Get logging statistics"""
        return {
            "total_logs": len(self.log_buffer),
            "log_levels": {k: v for k, v in self.log_stats.items() if k.startswith("level_")},
            "log_categories": {k: v for k, v in self.log_stats.items() if k.startswith("category_")},
            "error_summary": self.error_aggregator.get_error_summary(),
            "active_correlations": len(self.correlation.active_correlations),
            "completed_correlations": len(self.correlation.correlation_history)
        }
    
    def get_recent_logs(self, count: int = 100, level: Optional[LogLevel] = None) -> List[LogEntry]:
        """Get recent log entries"""
        logs = list(self.log_buffer)
        
        if level:
            logs = [log for log in logs if log.level == level]
        
        return logs[-count:]
    
    def get_error_reports(self) -> List[ErrorReport]:
        """Get error reports"""
        return self.error_aggregator.get_top_errors()
    
    def search_logs(
        self,
        query: str,
        category: Optional[LogCategory] = None,
        level: Optional[LogLevel] = None,
        hours: int = 24
    ) -> List[LogEntry]:
        """Search logs with filters"""
        cutoff_time = datetime.now() - timedelta(hours=hours)
        
        matching_logs = []
        for log_entry in self.log_buffer:
            if log_entry.timestamp < cutoff_time:
                continue
            
            if category and log_entry.category != category:
                continue
            
            if level and log_entry.level != level:
                continue
            
            if query.lower() in log_entry.message.lower():
                matching_logs.append(log_entry)
        
        return matching_logs


class ErrorCapturingHandler(logging.Handler):
    """Custom logging handler to capture errors"""
    
    def __init__(self, logging_manager -> None: UnifiedLoggingManager) -> None:
        super().__init__()
        self.logging_manager = logging_manager
    
    def emit(self, record -> None: logging.LogRecord) -> None:
        """Emit log record and capture errors"""
        if record.levelno >= logging.ERROR and record.exc_info:
            # Extract error information
            error = record.exc_info[1]
            if error:
                # Determine severity based on log level
                severity = ErrorSeverity.HIGH if record.levelno >= logging.CRITICAL else ErrorSeverity.MEDIUM
                
                # Capture error
                self.logging_manager.error_aggregator.record_error(
                    title=record.getMessage(),
                    message=str(error),
                    error_type=type(error).__name__,
                    severity=severity,
                    stack_trace=self.format(record)
                )


# Global logging manager instance
logging_manager = UnifiedLoggingManager()


# Convenience functions for external use
def log_info(message -> None: str, **kwargs) -> None:
    """Log info message"""
    logging_manager.log_structured(LogLevel.INFO, message, **kwargs)


def log_warning(message -> None: str, **kwargs) -> None:
    """Log warning message"""
    logging_manager.log_structured(LogLevel.WARNING, message, **kwargs)


def log_error(message -> None: str, **kwargs) -> None:
    """Log error message"""
    logging_manager.log_structured(LogLevel.ERROR, message, **kwargs)


def log_debug(message -> None: str, **kwargs) -> None:
    """Log debug message"""
    logging_manager.log_structured(LogLevel.DEBUG, message, **kwargs)


def capture_error(error: Exception, **kwargs) -> str:
    """Capture and log error"""
    return logging_manager.log_error(error, **kwargs)


def log_business_event(event -> None: str, details -> None: Dict[str, Any], **kwargs) -> None:
    """Log business event"""
    logging_manager.log_business_event(event, details, **kwargs)


def log_security_event(event -> None: str, details -> None: Dict[str, Any], **kwargs) -> None:
    """Log security event"""
    logging_manager.log_security_event(event, details, **kwargs)


def start_operation(operation: str, **kwargs) -> str:
    """Start tracked operation"""
    return logging_manager.start_operation(operation, **kwargs)


def end_operation(correlation_id -> None: str, success -> None: bool = True, **kwargs) -> None:
    """End tracked operation"""
    logging_manager.end_operation(correlation_id, success, **kwargs)


def get_log_statistics() -> Dict[str, Any]:
    """Get logging statistics"""
    return logging_manager.get_log_statistics()


def get_error_reports() -> List[ErrorReport]:
    """Get error reports"""
    return logging_manager.get_error_reports()