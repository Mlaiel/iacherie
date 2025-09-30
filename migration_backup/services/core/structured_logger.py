"""
Structured Logger - Enterprise JSON Logging with Correlation IDs
===============================================================

**Author**: Fahed Mlaiel (mlaiel@live.de)
**Role**: DevOps Engineer & Backend Senior
**Module**: Core Logging Services
**Version**: 1.0.0 Enterprise
**Created**: 2025-01-07

Enterprise structured logging with:
- JSON structured logging format
- Correlation ID tracking across services
- Performance metrics integration
- Security audit trail
- Real-time log aggregation ready
"""

import json
import logging
import logging.handlers
import time
import uuid
from datetime import datetime
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, field, asdict
from enum import Enum
from contextlib import contextmanager
from contextvars import ContextVar
import threading
import traceback
import sys
import os

# Context variables for correlation tracking
correlation_id: ContextVar[Optional[str]] = ContextVar('correlation_id', default=None)
user_id: ContextVar[Optional[str]] = ContextVar('user_id', default=None)
request_id: ContextVar[Optional[str]] = ContextVar('request_id', default=None)
trace_id: ContextVar[Optional[str]] = ContextVar('trace_id', default=None)


class LogLevel(Enum):
    """Enhanced log levels for enterprise logging"""
    TRACE = "TRACE"
    DEBUG = "DEBUG" 
    INFO = "INFO"
    WARN = "WARN"
    ERROR = "ERROR"
    FATAL = "FATAL"
    AUDIT = "AUDIT"
    SECURITY = "SECURITY"
    PERFORMANCE = "PERFORMANCE"


class LogCategory(Enum):
    """Log categories for better organization"""
    API = "api"
    DATABASE = "database"
    CACHE = "cache"
    SECURITY = "security"
    PERFORMANCE = "performance"
    BUSINESS = "business"
    INTEGRATION = "integration"
    MONITORING = "monitoring"
    AUDIT = "audit"
    ERROR = "error"


@dataclass
class LogContext:
    """Enhanced logging context with enterprise metadata"""
    correlation_id: Optional[str] = None
    request_id: Optional[str] = None
    user_id: Optional[str] = None
    trace_id: Optional[str] = None
    session_id: Optional[str] = None
    service_name: str = "ainflue-services"
    service_version: str = "1.0.0"
    environment: str = "production"
    component: Optional[str] = None
    operation: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class LogEntry:
    """Structured log entry with all enterprise fields"""
    timestamp: str
    level: str
    message: str
    logger_name: str
    category: str
    context: LogContext
    performance: Optional[Dict[str, Any]] = None
    security: Optional[Dict[str, Any]] = None
    error: Optional[Dict[str, Any]] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_json(self) -> str:
        """Convert log entry to JSON string"""
        return json.dumps(asdict(self), default=str, ensure_ascii=False)


class StructuredFormatter(logging.Formatter):
    """Custom formatter for structured JSON logging"""
    
    def __init__(self, service_name: str = "ainflue-services", include_trace: bool = True):
        super().__init__()
        self.service_name = service_name
        self.include_trace = include_trace
    
    def format(self, record: logging.LogRecord) -> str:
        """Format log record as structured JSON"""
        # Get context from context variables
        context = LogContext(
            correlation_id=correlation_id.get(),
            request_id=request_id.get(),
            user_id=user_id.get(),
            trace_id=trace_id.get(),
            service_name=self.service_name,
            component=getattr(record, 'component', None),
            operation=getattr(record, 'operation', None)
        )
        
        # Build log entry
        log_entry = LogEntry(
            timestamp=datetime.utcnow().isoformat() + "Z",
            level=record.levelname,
            message=record.getMessage(),
            logger_name=record.name,
            category=getattr(record, 'category', LogCategory.API.value),
            context=context
        )
        
        # Add performance metrics if available
        if hasattr(record, 'performance'):
            log_entry.performance = record.performance
        
        # Add security context if available
        if hasattr(record, 'security'):
            log_entry.security = record.security
        
        # Add error details if exception
        if record.exc_info:
            log_entry.error = {
                "exception_type": record.exc_info[0].__name__ if record.exc_info[0] else None,
                "exception_message": str(record.exc_info[1]) if record.exc_info[1] else None,
                "stack_trace": self.formatException(record.exc_info) if self.include_trace else None
            }
        
        # Add any additional metadata
        metadata = {}
        for key, value in record.__dict__.items():
            if key not in {
                'name', 'msg', 'args', 'levelname', 'levelno', 'pathname', 
                'filename', 'module', 'lineno', 'funcName', 'created', 
                'msecs', 'relativeCreated', 'thread', 'threadName', 
                'processName', 'process', 'getMessage', 'exc_info', 'exc_text', 
                'stack_info', 'category', 'component', 'operation', 'performance', 'security'
            }:
                metadata[key] = value
        
        if metadata:
            log_entry.metadata = metadata
        
        return log_entry.to_json()


class PerformanceLogger:
    """Specialized logger for performance metrics"""
    
    def __init__(self, logger: logging.Logger):
        self.logger = logger
    
    def log_api_performance(
        self,
        endpoint: str,
        method: str,
        status_code: int,
        response_time: float,
        user_id: Optional[str] = None,
        **kwargs
    ) -> None:
        """Log API performance metrics"""
        performance_data = {
            "endpoint": endpoint,
            "method": method,
            "status_code": status_code,
            "response_time_ms": response_time * 1000,
            "user_id": user_id,
            **kwargs
        }
        
        # Determine log level based on performance
        if response_time > 1.0:
            level = logging.WARNING
        elif response_time > 0.5:
            level = logging.INFO
        else:
            level = logging.DEBUG
        
        self.logger.log(
            level,
            f"API {method} {endpoint} completed in {response_time*1000:.2f}ms",
            extra={
                "category": LogCategory.PERFORMANCE.value,
                "component": "api",
                "operation": "request",
                "performance": performance_data
            }
        )
    
    def log_database_performance(
        self,
        query_type: str,
        table: str,
        execution_time: float,
        rows_affected: Optional[int] = None,
        **kwargs
    ) -> None:
        """Log database performance metrics"""
        performance_data = {
            "query_type": query_type,
            "table": table,
            "execution_time_ms": execution_time * 1000,
            "rows_affected": rows_affected,
            **kwargs
        }
        
        self.logger.info(
            f"Database {query_type} on {table} completed in {execution_time*1000:.2f}ms",
            extra={
                "category": LogCategory.DATABASE.value,
                "component": "database",
                "operation": query_type.lower(),
                "performance": performance_data
            }
        )
    
    def log_cache_performance(
        self,
        operation: str,
        key: str,
        hit: bool,
        execution_time: Optional[float] = None,
        **kwargs
    ) -> None:
        """Log cache performance metrics"""
        performance_data = {
            "operation": operation,
            "key": key,
            "cache_hit": hit,
            "execution_time_ms": execution_time * 1000 if execution_time else None,
            **kwargs
        }
        
        self.logger.debug(
            f"Cache {operation} for key {key} - {'HIT' if hit else 'MISS'}",
            extra={
                "category": LogCategory.CACHE.value,
                "component": "cache",
                "operation": operation,
                "performance": performance_data
            }
        )


class SecurityLogger:
    """Specialized logger for security events"""
    
    def __init__(self, logger: logging.Logger):
        self.logger = logger
    
    def log_authentication(
        self,
        user_id: str,
        success: bool,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        **kwargs
    ) -> None:
        """Log authentication events"""
        security_data = {
            "event_type": "authentication",
            "user_id": user_id,
            "success": success,
            "ip_address": ip_address,
            "user_agent": user_agent,
            **kwargs
        }
        
        level = logging.INFO if success else logging.WARNING
        message = f"Authentication {'successful' if success else 'failed'} for user {user_id}"
        
        self.logger.log(
            level,
            message,
            extra={
                "category": LogCategory.SECURITY.value,
                "component": "auth",
                "operation": "authenticate",
                "security": security_data
            }
        )
    
    def log_authorization(
        self,
        user_id: str,
        resource: str,
        action: str,
        granted: bool,
        **kwargs
    ) -> None:
        """Log authorization events"""
        security_data = {
            "event_type": "authorization",
            "user_id": user_id,
            "resource": resource,
            "action": action,
            "granted": granted,
            **kwargs
        }
        
        level = logging.INFO if granted else logging.WARNING
        message = f"Authorization {'granted' if granted else 'denied'} for user {user_id} on {resource}:{action}"
        
        self.logger.log(
            level,
            message,
            extra={
                "category": LogCategory.SECURITY.value,
                "component": "authz",
                "operation": "authorize",
                "security": security_data
            }
        )
    
    def log_security_incident(
        self,
        incident_type: str,
        severity: str,
        description: str,
        ip_address: Optional[str] = None,
        **kwargs
    ) -> None:
        """Log security incidents"""
        security_data = {
            "event_type": "security_incident",
            "incident_type": incident_type,
            "severity": severity,
            "description": description,
            "ip_address": ip_address,
            **kwargs
        }
        
        # Map severity to log level
        severity_mapping = {
            "low": logging.INFO,
            "medium": logging.WARNING,
            "high": logging.ERROR,
            "critical": logging.CRITICAL
        }
        
        level = severity_mapping.get(severity.lower(), logging.WARNING)
        
        self.logger.log(
            level,
            f"Security incident ({severity}): {description}",
            extra={
                "category": LogCategory.SECURITY.value,
                "component": "security",
                "operation": "incident",
                "security": security_data
            }
        )


class AuditLogger:
    """Specialized logger for audit trail"""
    
    def __init__(self, logger: logging.Logger):
        self.logger = logger
    
    def log_data_access(
        self,
        user_id: str,
        resource: str,
        action: str,
        result: str,
        **kwargs
    ) -> None:
        """Log data access for audit trail"""
        audit_data = {
            "event_type": "data_access",
            "user_id": user_id,
            "resource": resource,
            "action": action,
            "result": result,
            "timestamp": datetime.utcnow().isoformat(),
            **kwargs
        }
        
        self.logger.info(
            f"Data access: {user_id} performed {action} on {resource} - {result}",
            extra={
                "category": LogCategory.AUDIT.value,
                "component": "audit",
                "operation": "data_access",
                "metadata": audit_data
            }
        )
    
    def log_configuration_change(
        self,
        user_id: str,
        component: str,
        change_type: str,
        old_value: Any,
        new_value: Any,
        **kwargs
    ) -> None:
        """Log configuration changes"""
        audit_data = {
            "event_type": "configuration_change",
            "user_id": user_id,
            "component": component,
            "change_type": change_type,
            "old_value": str(old_value),
            "new_value": str(new_value),
            "timestamp": datetime.utcnow().isoformat(),
            **kwargs
        }
        
        self.logger.warning(
            f"Configuration change: {user_id} changed {component}.{change_type}",
            extra={
                "category": LogCategory.AUDIT.value,
                "component": "audit",
                "operation": "config_change",
                "metadata": audit_data
            }
        )


class StructuredLogger:
    """
    Enterprise Structured Logger
    
    Comprehensive logging solution with:
    - JSON structured logging
    - Correlation ID tracking
    - Performance metrics logging
    - Security event logging
    - Audit trail logging
    - Context management
    """
    
    def __init__(
        self, 
        name: str,
        service_name: str = "ainflue-services",
        log_level: str = "INFO",
        log_file: Optional[str] = None,
        console_output: bool = True
    ):
        self.name = name
        self.service_name = service_name
        
        # Create main logger
        self.logger = logging.getLogger(name)
        self.logger.setLevel(getattr(logging, log_level.upper()))
        
        # Clear existing handlers
        self.logger.handlers.clear()
        
        # Create structured formatter
        formatter = StructuredFormatter(service_name=service_name)
        
        # Add console handler if requested
        if console_output:
            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.setFormatter(formatter)
            self.logger.addHandler(console_handler)
        
        # Add file handler if log file specified
        if log_file:
            file_handler = logging.handlers.RotatingFileHandler(
                log_file,
                maxBytes=100 * 1024 * 1024,  # 100MB
                backupCount=10,
                encoding='utf-8'
            )
            file_handler.setFormatter(formatter)
            self.logger.addHandler(file_handler)
        
        # Create specialized loggers
        self.performance = PerformanceLogger(self.logger)
        self.security = SecurityLogger(self.logger)
        self.audit = AuditLogger(self.logger)
    
    @contextmanager
    def correlation_context(
        self,
        correlation_id: Optional[str] = None,
        user_id: Optional[str] = None,
        request_id: Optional[str] = None,
        trace_id: Optional[str] = None
    ):
        """Context manager for correlation ID tracking"""
        # Generate IDs if not provided
        corr_id = correlation_id or str(uuid.uuid4())
        req_id = request_id or str(uuid.uuid4())
        tr_id = trace_id or str(uuid.uuid4())
        
        # Set context variables
        corr_token = correlation_id.set(corr_id)
        user_token = user_id.set(user_id) if user_id else None
        req_token = request_id.set(req_id)
        trace_token = trace_id.set(tr_id)
        
        try:
            yield {
                "correlation_id": corr_id,
                "request_id": req_id,
                "trace_id": tr_id,
                "user_id": user_id
            }
        finally:
            # Reset context variables
            correlation_id.reset(corr_token)
            request_id.reset(req_token)
            trace_id.reset(trace_token)
            if user_token:
                user_id.reset(user_token)
    
    def debug(self, message: str, **kwargs) -> None:
        """Log debug message"""
        self.logger.debug(message, extra=kwargs)
    
    def info(self, message: str, **kwargs) -> None:
        """Log info message"""
        self.logger.info(message, extra=kwargs)
    
    def warning(self, message: str, **kwargs) -> None:
        """Log warning message"""
        self.logger.warning(message, extra=kwargs)
    
    def error(self, message: str, exc_info: bool = True, **kwargs) -> None:
        """Log error message"""
        self.logger.error(message, exc_info=exc_info, extra=kwargs)
    
    def critical(self, message: str, exc_info: bool = True, **kwargs) -> None:
        """Log critical message"""
        self.logger.critical(message, exc_info=exc_info, extra=kwargs)
    
    def log_with_context(
        self,
        level: str,
        message: str,
        category: LogCategory = LogCategory.API,
        component: Optional[str] = None,
        operation: Optional[str] = None,
        **kwargs
    ) -> None:
        """Log message with enhanced context"""
        extra = {
            "category": category.value,
            "component": component,
            "operation": operation,
            **kwargs
        }
        
        log_level = getattr(logging, level.upper())
        self.logger.log(log_level, message, extra=extra)


def get_logger(
    name: str,
    service_name: str = "ainflue-services",
    log_level: str = "INFO"
) -> StructuredLogger:
    """Factory function to create structured logger"""
    return StructuredLogger(
        name=name,
        service_name=service_name,
        log_level=log_level,
        console_output=True
    )


# Global logger instances for common use
api_logger = get_logger("ainflue.api")
service_logger = get_logger("ainflue.services")
security_logger = get_logger("ainflue.security")
performance_logger = get_logger("ainflue.performance")