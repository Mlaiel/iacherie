"""
Advanced Logging System
Structured logging with multiple outputs, correlation IDs, and performance tracking.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import logging
import json
import sys
from datetime import datetime
from typing import Dict, Any, Optional
from contextlib import contextmanager
import traceback
import uuid

from ..config import settings


class JSONFormatter(logging.Formatter):
    """JSON log formatter for structured logging"""
    
    def format(self, record: logging.LogRecord) -> str:
        """Format log record as JSON"""
        log_entry = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno
        }
        
        # Add extra fields
        for key, value in record.__dict__.items():
            if key not in ['name', 'msg', 'args', 'levelname', 'levelno', 'pathname', 'filename',
                          'module', 'lineno', 'funcName', 'created', 'msecs', 'relativeCreated',
                          'thread', 'threadName', 'processName', 'process', 'message']:
                log_entry[key] = value
        
        # Add exception info if present
        if record.exc_info:
            log_entry["exception"] = {
                "type": record.exc_info[0].__name__,
                "message": str(record.exc_info[1]),
                "traceback": traceback.format_exception(*record.exc_info)
            }
        
        return json.dumps(log_entry, default=str)


class CorrelationFilter(logging.Filter):
    """Add correlation ID to log records"""
    
    def __init__(self):
        super().__init__()
        self.correlation_id = None
    
    def filter(self, record: logging.LogRecord) -> bool:
        """Add correlation ID to record"""
        record.correlation_id = self.correlation_id or "no-correlation"
        return True
    
    def set_correlation_id(self, correlation_id: str):
        """Set correlation ID for current context"""
        self.correlation_id = correlation_id


class PerformanceLogger:
    """Performance tracking and logging"""
    
    def __init__(self, logger_name: str = "performance"):
        self.logger = logging.getLogger(logger_name)
        self.timers = {}
    
    @contextmanager
    def timer(self, operation: str, **context):
        """Context manager for timing operations"""
        timer_id = str(uuid.uuid4())
        start_time = datetime.utcnow()
        
        try:
            self.logger.info("Operation started", extra={
                "operation": operation,
                "timer_id": timer_id,
                "start_time": start_time.isoformat(),
                **context
            })
            
            yield timer_id
            
        except Exception as e:
            duration = (datetime.utcnow() - start_time).total_seconds()
            
            self.logger.error("Operation failed", extra={
                "operation": operation,
                "timer_id": timer_id,
                "duration_seconds": duration,
                "error": str(e),
                **context
            })
            raise
            
        else:
            duration = (datetime.utcnow() - start_time).total_seconds()
            
            self.logger.info("Operation completed", extra={
                "operation": operation,
                "timer_id": timer_id,
                "duration_seconds": duration,
                **context
            })


class SecurityLogger:
    """Security-specific logging"""
    
    def __init__(self, logger_name: str = "security"):
        self.logger = logging.getLogger(logger_name)
    
    def log_authentication_attempt(self, user_id: str, success: bool, 
                                 ip_address: str, user_agent: str):
        """Log authentication attempts"""
        self.logger.info("Authentication attempt", extra={
            "event_type": "authentication",
            "user_id": user_id,
            "success": success,
            "ip_address": ip_address,
            "user_agent": user_agent
        })
    
    def log_authorization_failure(self, user_id: str, resource: str, 
                                action: str, ip_address: str):
        """Log authorization failures"""
        self.logger.warning("Authorization failure", extra={
            "event_type": "authorization_failure",
            "user_id": user_id,
            "resource": resource,
            "action": action,
            "ip_address": ip_address
        })
    
    def log_suspicious_activity(self, user_id: str, activity: str, 
                              details: Dict[str, Any]):
        """Log suspicious activities"""
        self.logger.warning("Suspicious activity detected", extra={
            "event_type": "suspicious_activity",
            "user_id": user_id,
            "activity": activity,
            "details": details
        })
    
    def log_data_access(self, user_id: str, resource_type: str, 
                       resource_id: str, action: str):
        """Log sensitive data access"""
        self.logger.info("Data access", extra={
            "event_type": "data_access",
            "user_id": user_id,
            "resource_type": resource_type,
            "resource_id": resource_id,
            "action": action
        })


class BusinessLogger:
    """Business event logging"""
    
    def __init__(self, logger_name: str = "business"):
        self.logger = logging.getLogger(logger_name)
    
    def log_content_upload(self, user_id: str, content_type: str, 
                          file_size: int, fingerprint_id: str):
        """Log content upload events"""
        self.logger.info("Content uploaded", extra={
            "event_type": "content_upload",
            "user_id": user_id,
            "content_type": content_type,
            "file_size_bytes": file_size,
            "fingerprint_id": fingerprint_id
        })
    
    def log_protection_alert(self, user_id: str, content_id: str, 
                           platform: str, similarity_score: float):
        """Log content protection alerts"""
        self.logger.warning("Protection alert triggered", extra={
            "event_type": "protection_alert",
            "user_id": user_id,
            "content_id": content_id,
            "platform": platform,
            "similarity_score": similarity_score
        })
    
    def log_revenue_event(self, user_id: str, platform: str, 
                         amount: float, currency: str):
        """Log revenue tracking events"""
        self.logger.info("Revenue tracked", extra={
            "event_type": "revenue_tracking",
            "user_id": user_id,
            "platform": platform,
            "amount": amount,
            "currency": currency
        })
    
    def log_collaboration_match(self, user_id: str, partner_id: str, 
                              match_score: float, common_interests: list):
        """Log collaboration matching events"""
        self.logger.info("Collaboration match found", extra={
            "event_type": "collaboration_match",
            "user_id": user_id,
            "partner_id": partner_id,
            "match_score": match_score,
            "common_interests": common_interests
        })


class LoggerManager:
    """Main logger management system"""
    
    def __init__(self):
        self.correlation_filter = CorrelationFilter()
        self.performance_logger = PerformanceLogger()
        self.security_logger = SecurityLogger()
        self.business_logger = BusinessLogger()
        self._setup_loggers()
    
    def _setup_loggers(self):
        """Setup all loggers with appropriate handlers and formatters"""
        # Root logger configuration
        root_logger = logging.getLogger()
        root_logger.setLevel(getattr(logging, settings.monitoring.log_level.upper()))
        
        # Remove default handlers
        for handler in root_logger.handlers[:]:
            root_logger.removeHandler(handler)
        
        # Console handler
        console_handler = logging.StreamHandler(sys.stdout)
        
        if settings.monitoring.log_format == "json":
            console_handler.setFormatter(JSONFormatter())
        else:
            console_handler.setFormatter(logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(correlation_id)s - %(message)s'
            ))
        
        console_handler.addFilter(self.correlation_filter)
        root_logger.addHandler(console_handler)
        
        # File handler for errors
        error_handler = logging.FileHandler("logs/errors.log")
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(JSONFormatter())
        error_handler.addFilter(self.correlation_filter)
        root_logger.addHandler(error_handler)
        
        # Specific loggers
        loggers = [
            "uvicorn.access",
            "uvicorn.error",
            "fastapi",
            "sqlalchemy.engine",
            "redis",
            "mongodb"
        ]
        
        for logger_name in loggers:
            logger = logging.getLogger(logger_name)
            logger.setLevel(logging.INFO)
    
    def get_logger(self, name: str) -> logging.Logger:
        """Get logger with correlation filter"""
        logger = logging.getLogger(name)
        if not any(isinstance(f, CorrelationFilter) for f in logger.filters):
            logger.addFilter(self.correlation_filter)
        return logger
    
    def set_correlation_id(self, correlation_id: str):
        """Set correlation ID for current context"""
        self.correlation_filter.set_correlation_id(correlation_id)
    
    def generate_correlation_id(self) -> str:
        """Generate new correlation ID"""
        correlation_id = str(uuid.uuid4())
        self.set_correlation_id(correlation_id)
        return correlation_id
    
    @contextmanager
    def correlation_context(self, correlation_id: Optional[str] = None):
        """Context manager for correlation ID"""
        if correlation_id is None:
            correlation_id = self.generate_correlation_id()
        
        old_correlation_id = self.correlation_filter.correlation_id
        self.set_correlation_id(correlation_id)
        
        try:
            yield correlation_id
        finally:
            self.correlation_filter.correlation_id = old_correlation_id
    
    def log_startup(self):
        """Log application startup"""
        logger = self.get_logger("ainflue.startup")
        logger.info("Ainflue platform starting up", extra={
            "version": "1.0.0",
            "environment": settings.app.environment,
            "debug": settings.app.debug
        })
    
    def log_shutdown(self):
        """Log application shutdown"""
        logger = self.get_logger("ainflue.shutdown")
        logger.info("Ainflue platform shutting down")
    
    def log_health_check(self, component: str, status: bool, details: Dict[str, Any] = None):
        """Log health check results"""
        logger = self.get_logger("ainflue.health")
        logger.info("Health check", extra={
            "component": component,
            "status": "healthy" if status else "unhealthy",
            "details": details or {}
        })


# Global logger manager instance
logger_manager = LoggerManager()

# Convenience logger
logger = logger_manager.get_logger("ainflue")