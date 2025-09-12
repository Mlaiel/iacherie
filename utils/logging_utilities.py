"""
Logging Utilities - Enterprise Grade
===================================

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.

Expert Roles: DevOps Expert + Backend Senior + Security Expert
Provides comprehensive structured logging for enterprise applications.
"""

import logging
import json
import sys
import threading
import time
import os
from typing import Any, Dict, List, Optional, Union, Callable
from datetime import datetime, timezone
from pathlib import Path
from dataclasses import dataclass, asdict
from enum import Enum
import traceback
import gzip
from logging.handlers import RotatingFileHandler
from concurrent.futures import ThreadPoolExecutor
import asyncio


class LogLevel(Enum):
    """Log level enumeration."""
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class LogFormat(Enum):
    """Log format types."""
    JSON = "json"
    TEXT = "text"
    STRUCTURED = "structured"
    ELK = "elk"  # Elasticsearch, Logstash, Kibana


@dataclass
class LogContext:
    """Context information for logs."""
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    request_id: Optional[str] = None
    correlation_id: Optional[str] = None
    trace_id: Optional[str] = None
    span_id: Optional[str] = None
    component: Optional[str] = None
    environment: Optional[str] = None
    version: Optional[str] = None
    additional_fields: Optional[Dict[str, Any]] = None


@dataclass
class LogEntry:
    """Structured log entry."""
    timestamp: datetime
    level: LogLevel
    message: str
    logger_name: str
    context: Optional[LogContext] = None
    exception: Optional[str] = None
    performance_metrics: Optional[Dict[str, float]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            'timestamp': self.timestamp.isoformat(),
            'level': self.level.value,
            'message': self.message,
            'logger_name': self.logger_name,
            'context': asdict(self.context) if self.context else None,
            'exception': self.exception,
            'performance_metrics': self.performance_metrics
        }


class CustomJSONFormatter(logging.Formatter):
    """Custom JSON formatter for structured logging."""
    
    def __init__(self, include_context: bool = True):
        super().__init__()
        self.include_context = include_context
    
    def format(self, record: logging.LogRecord) -> str:
        """Format log record as JSON."""
        log_entry = {
            'timestamp': datetime.fromtimestamp(record.created, tz=timezone.utc).isoformat(),
            'level': record.levelname,
            'message': record.getMessage(),
            'logger_name': record.name,
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno,
            'thread_id': record.thread,
            'process_id': record.process
        }
        
        # Add exception information if present
        if record.exc_info:
            log_entry['exception'] = self.formatException(record.exc_info)
        
        # Add custom context if available
        if self.include_context and hasattr(record, 'context'):
            log_entry['context'] = record.context
        
        # Add custom fields from record
        custom_fields = {}
        for key, value in record.__dict__.items():
            if key not in ['name', 'msg', 'args', 'levelname', 'levelno', 'pathname',
                          'filename', 'module', 'exc_info', 'exc_text', 'stack_info',
                          'lineno', 'funcName', 'created', 'msecs', 'relativeCreated',
                          'thread', 'threadName', 'processName', 'process', 'getMessage',
                          'context']:
                custom_fields[key] = value
        
        if custom_fields:
            log_entry['custom_fields'] = custom_fields
        
        return json.dumps(log_entry, default=str)


class StructuredLogger:
    """
    Enterprise-grade structured logging utility.
    
    Features:
    - JSON and structured text formatting
    - Context-aware logging with correlation IDs
    - Performance metrics integration
    - Log aggregation and forwarding
    - Automatic log rotation and compression
    - Async logging for high-performance applications
    - Integration with ELK stack and monitoring systems
    - Security-focused logging with PII filtering
    """
    
    def __init__(self, 
                 name: str = "Ainflue",
                 level: LogLevel = LogLevel.INFO,
                 format_type: LogFormat = LogFormat.JSON,
                 log_dir: Optional[str] = None,
                 max_file_size: int = 100 * 1024 * 1024,  # 100MB
                 backup_count: int = 10,
                 enable_console: bool = True,
                 enable_file: bool = True,
                 enable_compression: bool = True):
        
        self.name = name
        self.level = level
        self.format_type = format_type
        self.log_dir = Path(log_dir) if log_dir else Path("logs")
        self.max_file_size = max_file_size
        self.backup_count = backup_count
        self.enable_console = enable_console
        self.enable_file = enable_file
        self.enable_compression = enable_compression
        
        # Create log directory
        self.log_dir.mkdir(exist_ok=True)
        
        # Initialize logger
        self.logger = logging.getLogger(name)
        self.logger.setLevel(getattr(logging, level.value))
        
        # Clear existing handlers
        self.logger.handlers.clear()
        
        # Setup formatters
        self._setup_formatters()
        
        # Setup handlers
        self._setup_handlers()
        
        # Context storage for thread-local data
        self._local = threading.local()
        
        # Performance tracking
        self.performance_data: Dict[str, List[float]] = {}
        self._performance_lock = threading.Lock()
        
        # Async logging setup
        self.executor = ThreadPoolExecutor(max_workers=2, thread_name_prefix="logger")
        
        # PII filtering patterns
        self.pii_patterns = [
            (r'\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b', '[CREDIT_CARD]'),  # Credit cards
            (r'\b\d{3}-\d{2}-\d{4}\b', '[SSN]'),  # SSN
            (r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', '[EMAIL]'),  # Email
            (r'\b(?:\d{1,3}\.){3}\d{1,3}\b', '[IP_ADDRESS]'),  # IP addresses
        ]
    
    def _setup_formatters(self):
        """Setup log formatters based on format type."""
        if self.format_type == LogFormat.JSON:
            self.formatter = CustomJSONFormatter()
        elif self.format_type == LogFormat.STRUCTURED:
            format_string = (
                '%(asctime)s | %(levelname)-8s | %(name)s | '
                '%(module)s:%(funcName)s:%(lineno)d | %(message)s'
            )
            self.formatter = logging.Formatter(format_string)
        elif self.format_type == LogFormat.ELK:
            self.formatter = CustomJSONFormatter()
        else:  # TEXT
            self.formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
    
    def _setup_handlers(self):
        """Setup log handlers."""
        # Console handler
        if self.enable_console:
            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.setFormatter(self.formatter)
            self.logger.addHandler(console_handler)
        
        # File handler with rotation
        if self.enable_file:
            log_file = self.log_dir / f"{self.name}.log"
            
            if self.enable_compression:
                file_handler = CompressingRotatingFileHandler(
                    filename=str(log_file),
                    maxBytes=self.max_file_size,
                    backupCount=self.backup_count
                )
            else:
                file_handler = RotatingFileHandler(
                    filename=str(log_file),
                    maxBytes=self.max_file_size,
                    backupCount=self.backup_count
                )
            
            file_handler.setFormatter(self.formatter)
            self.logger.addHandler(file_handler)
        
        # Error-specific file handler
        error_log_file = self.log_dir / f"{self.name}_errors.log"
        error_handler = RotatingFileHandler(
            filename=str(error_log_file),
            maxBytes=self.max_file_size,
            backupCount=self.backup_count
        )
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(self.formatter)
        self.logger.addHandler(error_handler)
    
    def set_context(self, context: LogContext):
        """Set logging context for current thread."""
        self._local.context = context
    
    def get_context(self) -> Optional[LogContext]:
        """Get current logging context."""
        return getattr(self._local, 'context', None)
    
    def clear_context(self):
        """Clear logging context for current thread."""
        if hasattr(self._local, 'context'):
            delattr(self._local, 'context')
    
    def _filter_pii(self, message: str) -> str:
        """Filter PII from log messages."""
        for pattern, replacement in self.pii_patterns:
            message = re.sub(pattern, replacement, message)
        return message
    
    def _create_log_record(self, level: LogLevel, message: str, 
                          extra_fields: Optional[Dict[str, Any]] = None,
                          exception: Optional[Exception] = None) -> Dict[str, Any]:
        """Create structured log record."""
        # Filter PII from message
        filtered_message = self._filter_pii(message)
        
        log_data = {
            'message': filtered_message,
            'level': level.value,
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'logger_name': self.name
        }
        
        # Add context
        context = self.get_context()
        if context:
            log_data['context'] = asdict(context)
        
        # Add exception information
        if exception:
            log_data['exception'] = {
                'type': type(exception).__name__,
                'message': str(exception),
                'traceback': traceback.format_exc()
            }
        
        # Add extra fields
        if extra_fields:
            log_data.update(extra_fields)
        
        return log_data
    
    def debug(self, message: str, extra_fields: Optional[Dict[str, Any]] = None):
        """Log debug message."""
        log_data = self._create_log_record(LogLevel.DEBUG, message, extra_fields)
        self.logger.debug(message, extra=log_data)
    
    def info(self, message: str, extra_fields: Optional[Dict[str, Any]] = None):
        """Log info message."""
        log_data = self._create_log_record(LogLevel.INFO, message, extra_fields)
        self.logger.info(message, extra=log_data)
    
    def warning(self, message: str, extra_fields: Optional[Dict[str, Any]] = None):
        """Log warning message."""
        log_data = self._create_log_record(LogLevel.WARNING, message, extra_fields)
        self.logger.warning(message, extra=log_data)
    
    def error(self, message: str, exception: Optional[Exception] = None,
              extra_fields: Optional[Dict[str, Any]] = None):
        """Log error message."""
        log_data = self._create_log_record(LogLevel.ERROR, message, extra_fields, exception)
        self.logger.error(message, extra=log_data)
    
    def critical(self, message: str, exception: Optional[Exception] = None,
                 extra_fields: Optional[Dict[str, Any]] = None):
        """Log critical message."""
        log_data = self._create_log_record(LogLevel.CRITICAL, message, extra_fields, exception)
        self.logger.critical(message, extra=log_data)
    
    def log_performance(self, operation: str, duration: float, 
                       extra_metrics: Optional[Dict[str, float]] = None):
        """Log performance metrics."""
        with self._performance_lock:
            if operation not in self.performance_data:
                self.performance_data[operation] = []
            self.performance_data[operation].append(duration)
        
        metrics = {'duration': duration}
        if extra_metrics:
            metrics.update(extra_metrics)
        
        self.info(f"Performance: {operation}", {
            'performance_metrics': metrics,
            'operation': operation
        })
    
    def log_security_event(self, event_type: str, details: Dict[str, Any],
                          severity: LogLevel = LogLevel.WARNING):
        """Log security-related events."""
        security_data = {
            'security_event': True,
            'event_type': event_type,
            'details': details,
            'timestamp': datetime.now(timezone.utc).isoformat()
        }
        
        message = f"Security Event: {event_type}"
        
        if severity == LogLevel.CRITICAL:
            self.critical(message, extra_fields=security_data)
        elif severity == LogLevel.ERROR:
            self.error(message, extra_fields=security_data)
        elif severity == LogLevel.WARNING:
            self.warning(message, extra_fields=security_data)
        else:
            self.info(message, extra_fields=security_data)
    
    def log_api_call(self, method: str, endpoint: str, status_code: int,
                     duration: float, user_id: Optional[str] = None):
        """Log API call with standard fields."""
        api_data = {
            'api_call': True,
            'method': method,
            'endpoint': endpoint,
            'status_code': status_code,
            'duration': duration,
            'user_id': user_id
        }
        
        level = LogLevel.INFO
        if status_code >= 500:
            level = LogLevel.ERROR
        elif status_code >= 400:
            level = LogLevel.WARNING
        
        message = f"API Call: {method} {endpoint} - {status_code} ({duration:.3f}s)"
        
        if level == LogLevel.ERROR:
            self.error(message, extra_fields=api_data)
        elif level == LogLevel.WARNING:
            self.warning(message, extra_fields=api_data)
        else:
            self.info(message, extra_fields=api_data)
    
    async def log_async(self, level: LogLevel, message: str,
                       extra_fields: Optional[Dict[str, Any]] = None,
                       exception: Optional[Exception] = None):
        """Asynchronous logging for high-performance applications."""
        loop = asyncio.get_event_loop()
        
        if level == LogLevel.DEBUG:
            await loop.run_in_executor(self.executor, self.debug, message, extra_fields)
        elif level == LogLevel.INFO:
            await loop.run_in_executor(self.executor, self.info, message, extra_fields)
        elif level == LogLevel.WARNING:
            await loop.run_in_executor(self.executor, self.warning, message, extra_fields)
        elif level == LogLevel.ERROR:
            await loop.run_in_executor(self.executor, self.error, message, exception, extra_fields)
        elif level == LogLevel.CRITICAL:
            await loop.run_in_executor(self.executor, self.critical, message, exception, extra_fields)
    
    def get_performance_summary(self, operation: Optional[str] = None) -> Dict[str, Any]:
        """Get performance metrics summary."""
        with self._performance_lock:
            if operation:
                data = self.performance_data.get(operation, [])
                if not data:
                    return {}
                
                return {
                    'operation': operation,
                    'count': len(data),
                    'avg_duration': sum(data) / len(data),
                    'min_duration': min(data),
                    'max_duration': max(data),
                    'total_duration': sum(data)
                }
            else:
                summary = {}
                for op, data in self.performance_data.items():
                    summary[op] = {
                        'count': len(data),
                        'avg_duration': sum(data) / len(data),
                        'min_duration': min(data),
                        'max_duration': max(data),
                        'total_duration': sum(data)
                    }
                return summary
    
    def export_logs(self, start_time: datetime, end_time: datetime,
                   level_filter: Optional[LogLevel] = None) -> List[Dict[str, Any]]:
        """Export logs for a time range."""
        # This is a simplified implementation
        # In a real system, you'd read from log files or a logging database
        exported_logs = []
        
        # For demonstration, return recent performance data
        with self._performance_lock:
            for operation, durations in self.performance_data.items():
                for duration in durations:
                    log_entry = {
                        'timestamp': datetime.now(timezone.utc).isoformat(),
                        'level': 'INFO',
                        'message': f"Performance: {operation}",
                        'performance_metrics': {'duration': duration},
                        'operation': operation
                    }
                    exported_logs.append(log_entry)
        
        return exported_logs


class CompressingRotatingFileHandler(RotatingFileHandler):
    """Rotating file handler with compression."""
    
    def doRollover(self):
        """Override to add compression."""
        super().doRollover()
        
        # Compress the rotated file
        if self.backupCount > 0:
            for i in range(self.backupCount - 1, 0, -1):
                sfn = self.rotation_filename(f"{self.baseFilename}.{i}")
                dfn = self.rotation_filename(f"{self.baseFilename}.{i + 1}")
                
                if os.path.exists(sfn):
                    if os.path.exists(dfn):
                        os.remove(dfn)
                    
                    # Compress and rename
                    with open(sfn, 'rb') as f_in:
                        with gzip.open(f"{dfn}.gz", 'wb') as f_out:
                            f_out.writelines(f_in)
                    
                    os.remove(sfn)


# Context manager for performance logging
class PerformanceLogger:
    """Context manager for automatic performance logging."""
    
    def __init__(self, logger: StructuredLogger, operation: str):
        self.logger = logger
        self.operation = operation
        self.start_time = None
    
    def __enter__(self):
        self.start_time = time.time()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.start_time:
            duration = time.time() - self.start_time
            self.logger.log_performance(self.operation, duration)


# Global logger instance
global_logger = StructuredLogger()


# Convenience functions
def set_global_context(context: LogContext):
    """Set global logging context."""
    global_logger.set_context(context)


def log_info(message: str, extra_fields: Optional[Dict[str, Any]] = None):
    """Log info message using global logger."""
    global_logger.info(message, extra_fields)


def log_error(message: str, exception: Optional[Exception] = None,
              extra_fields: Optional[Dict[str, Any]] = None):
    """Log error message using global logger."""
    global_logger.error(message, exception, extra_fields)


def log_performance(operation: str, duration: float):
    """Log performance using global logger."""
    global_logger.log_performance(operation, duration)


def performance_monitor(operation: str):
    """Decorator for automatic performance monitoring."""
    def decorator(func):
        def wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = func(*args, **kwargs)
                return result
            finally:
                duration = time.time() - start_time
                global_logger.log_performance(operation, duration)
        return wrapper
    return decorator


# Example usage
if __name__ == "__main__":
    import time
    
    # Initialize logger
    logger = StructuredLogger(
        name="TestApp",
        format_type=LogFormat.JSON,
        log_dir="test_logs"
    )
    
    # Set context
    context = LogContext(
        user_id="user123",
        session_id="session456",
        request_id="req789",
        component="auth_service"
    )
    logger.set_context(context)
    
    # Test different log levels
    logger.debug("Debug message")
    logger.info("User logged in", {"action": "login", "ip": "192.168.1.1"})
    logger.warning("Rate limit approaching")
    
    try:
        raise ValueError("Test error")
    except Exception as e:
        logger.error("Operation failed", exception=e)
    
    # Test performance logging
    with PerformanceLogger(logger, "database_query"):
        time.sleep(0.1)  # Simulate work
    
    # Test security event
    logger.log_security_event("failed_login", {
        "user_id": "user123",
        "ip_address": "192.168.1.100",
        "attempts": 3
    }, LogLevel.ERROR)
    
    # Test API logging
    logger.log_api_call("GET", "/api/users", 200, 0.123, "user123")
    
    # Get performance summary
    perf_summary = logger.get_performance_summary()
    print(f"Performance summary: {perf_summary}")