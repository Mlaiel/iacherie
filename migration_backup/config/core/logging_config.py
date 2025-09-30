#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Ainflue Logging Configuration Module
=======================================

Enterprise-grade logging configuration for the Ainflue platform.
Handles structured logging, log aggregation, log rotation, security logging,
audit trails, and comprehensive monitoring across all system components.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
License: Proprietary - All rights reserved
"""

import os
import logging
import logging.handlers
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
import json
import sys
from datetime import datetime
import gzip
import asyncio

class LogLevel(str, Enum):
    """Logging levels"""
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"

class LogFormat(str, Enum):
    """Log format types"""
    SIMPLE = "simple"
    DETAILED = "detailed"
    JSON = "json"
    STRUCTURED = "structured"
    CUSTOM = "custom"

class LogDestination(str, Enum):
    """Log destinations"""
    CONSOLE = "console"
    FILE = "file"
    SYSLOG = "syslog"
    ELASTICSEARCH = "elasticsearch"
    FLUENTD = "fluentd"
    DATADOG = "datadog"
    CLOUDWATCH = "cloudwatch"

@dataclass
class LogRotationConfig:
    """Log rotation configuration"""
    max_file_size: str = "100MB"
    backup_count: int = 10
    rotation_type: str = "size"  # size, time
    rotation_interval: str = "daily"  # daily, weekly, monthly
    compress_rotated: bool = True
    
    def get_rotation_config(self) -> Dict[str, Any]:
        """Get rotation configuration"""
        return {
            "max_file_size": self.max_file_size,
            "backup_count": self.backup_count,
            "rotation_type": self.rotation_type,
            "rotation_interval": self.rotation_interval,
            "compress_rotated": self.compress_rotated
        }

@dataclass
class SecurityLoggingConfig:
    """Security logging configuration"""
    enable_audit_logging: bool = True
    log_authentication_events: bool = True
    log_authorization_events: bool = True
    log_data_access: bool = True
    log_configuration_changes: bool = True
    
    # Security event categories
    log_login_attempts: bool = True
    log_failed_authentications: bool = True
    log_privilege_escalations: bool = True
    log_suspicious_activities: bool = True
    
    # Compliance logging
    gdpr_compliance_logging: bool = True
    hipaa_compliance_logging: bool = False
    sox_compliance_logging: bool = False
    
    def get_security_config(self) -> Dict[str, Any]:
        """Get security logging configuration"""
        return {
            "enable_audit_logging": self.enable_audit_logging,
            "log_authentication_events": self.log_authentication_events,
            "log_authorization_events": self.log_authorization_events,
            "log_data_access": self.log_data_access,
            "log_configuration_changes": self.log_configuration_changes,
            "log_login_attempts": self.log_login_attempts,
            "log_failed_authentications": self.log_failed_authentications,
            "log_privilege_escalations": self.log_privilege_escalations,
            "log_suspicious_activities": self.log_suspicious_activities,
            "gdpr_compliance_logging": self.gdpr_compliance_logging,
            "hipaa_compliance_logging": self.hipaa_compliance_logging,
            "sox_compliance_logging": self.sox_compliance_logging
        }

@dataclass
class BusinessLoggingConfig:
    """Business logic logging configuration"""
    log_creator_activities: bool = True
    log_content_operations: bool = True
    log_monetization_events: bool = True
    log_collaboration_events: bool = True
    log_distribution_activities: bool = True
    
    # AI and ML logging
    log_ai_processing: bool = True
    log_model_predictions: bool = True
    log_training_metrics: bool = True
    
    # Protection and security
    log_copyright_violations: bool = True
    log_content_protection: bool = True
    log_rights_management: bool = True
    
    def get_business_config(self) -> Dict[str, Any]:
        """Get business logging configuration"""
        return {
            "log_creator_activities": self.log_creator_activities,
            "log_content_operations": self.log_content_operations,
            "log_monetization_events": self.log_monetization_events,
            "log_collaboration_events": self.log_collaboration_events,
            "log_distribution_activities": self.log_distribution_activities,
            "log_ai_processing": self.log_ai_processing,
            "log_model_predictions": self.log_model_predictions,
            "log_training_metrics": self.log_training_metrics,
            "log_copyright_violations": self.log_copyright_violations,
            "log_content_protection": self.log_content_protection,
            "log_rights_management": self.log_rights_management
        }

@dataclass
class PerformanceLoggingConfig:
    """Performance logging configuration"""
    log_response_times: bool = True
    log_database_queries: bool = True
    log_cache_operations: bool = True
    log_api_performance: bool = True
    log_memory_usage: bool = True
    log_cpu_usage: bool = True
    
    # Thresholds for performance alerts
    slow_query_threshold: float = 1.0  # seconds
    high_memory_threshold: float = 0.8  # 80% of available memory
    high_cpu_threshold: float = 0.8    # 80% CPU usage
    
    def get_performance_config(self) -> Dict[str, Any]:
        """Get performance logging configuration"""
        return {
            "log_response_times": self.log_response_times,
            "log_database_queries": self.log_database_queries,
            "log_cache_operations": self.log_cache_operations,
            "log_api_performance": self.log_api_performance,
            "log_memory_usage": self.log_memory_usage,
            "log_cpu_usage": self.log_cpu_usage,
            "slow_query_threshold": self.slow_query_threshold,
            "high_memory_threshold": self.high_memory_threshold,
            "high_cpu_threshold": self.high_cpu_threshold
        }

class CustomJSONFormatter(logging.Formatter):
    """Custom JSON formatter for structured logging"""
    
    def format(self, record):
        """Format log record as JSON"""
        log_entry = {
            "timestamp": datetime.utcfromtimestamp(record.created).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
            "thread": record.thread,
            "process": record.process
        }
        
        # Add exception information if present
        if record.exc_info:
            log_entry["exception"] = self.formatException(record.exc_info)
        
        # Add extra fields
        for key, value in record.__dict__.items():
            if key not in ['name', 'msg', 'args', 'levelname', 'levelno', 'pathname',
                          'filename', 'module', 'exc_info', 'exc_text', 'stack_info',
                          'lineno', 'funcName', 'created', 'msecs', 'relativeCreated',
                          'thread', 'threadName', 'processName', 'process', 'getMessage']:
                log_entry[key] = value
        
        return json.dumps(log_entry, ensure_ascii=False)

class LoggingConfiguration:
    """Main logging configuration manager"""
    
    def __init__(self, 
                 level: LogLevel = LogLevel.INFO,
                 format_type: LogFormat = LogFormat.JSON,
                 destinations: List[LogDestination] = None):
        """Initialize logging configuration"""
        self.level = level
        self.format_type = format_type
        self.destinations = destinations or [LogDestination.CONSOLE, LogDestination.FILE]
        
        # Configuration components
        self.rotation_config = LogRotationConfig()
        self.security_config = SecurityLoggingConfig()
        self.business_config = BusinessLoggingConfig()
        self.performance_config = PerformanceLoggingConfig()
        
        # Log directories
        self.log_dir = Path("/var/log/ainflue")
        self.log_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize loggers
        self.loggers: Dict[str, logging.Logger] = {}
        self._setup_logging()
    
    def _setup_logging(self):
        """Setup logging configuration"""
        # Root logger configuration
        root_logger = logging.getLogger()
        root_logger.setLevel(getattr(logging, self.level.value))
        
        # Clear existing handlers
        root_logger.handlers.clear()
        
        # Setup formatters
        formatters = self._create_formatters()
        
        # Setup handlers based on destinations
        for destination in self.destinations:
            handler = self._create_handler(destination)
            if handler:
                handler.setFormatter(formatters[self.format_type])
                root_logger.addHandler(handler)
        
        # Setup specific loggers
        self._setup_specific_loggers()
    
    def _create_formatters(self) -> Dict[LogFormat, logging.Formatter]:
        """Create logging formatters"""
        formatters = {}
        
        formatters[LogFormat.SIMPLE] = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        
        formatters[LogFormat.DETAILED] = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(module)s:%(funcName)s:%(lineno)d - %(message)s'
        )
        
        formatters[LogFormat.JSON] = CustomJSONFormatter()
        
        formatters[LogFormat.STRUCTURED] = logging.Formatter(
            '%(asctime)s | %(levelname)-8s | %(name)-20s | %(module)-15s | %(funcName)-20s | %(message)s'
        )
        
        return formatters
    
    def _create_handler(self, destination: LogDestination) -> Optional[logging.Handler]:
        """Create logging handler for destination"""
        if destination == LogDestination.CONSOLE:
            handler = logging.StreamHandler(sys.stdout)
            handler.setLevel(getattr(logging, self.level.value))
            return handler
        
        elif destination == LogDestination.FILE:
            log_file = self.log_dir / "ainflue.log"
            handler = logging.handlers.RotatingFileHandler(
                log_file,
                maxBytes=self._parse_size(self.rotation_config.max_file_size),
                backupCount=self.rotation_config.backup_count
            )
            handler.setLevel(getattr(logging, self.level.value))
            return handler
        
        elif destination == LogDestination.SYSLOG:
            handler = logging.handlers.SysLogHandler(address='/dev/log')
            handler.setLevel(getattr(logging, self.level.value))
            return handler
        
        # Add other destinations as needed
        return None
    
    def _parse_size(self, size_str: str) -> int:
        """Parse size string to bytes"""
        size_str = size_str.upper()
        if size_str.endswith('KB'):
            return int(size_str[:-2]) * 1024
        elif size_str.endswith('MB'):
            return int(size_str[:-2]) * 1024 * 1024
        elif size_str.endswith('GB'):
            return int(size_str[:-2]) * 1024 * 1024 * 1024
        else:
            return int(size_str)
    
    def _setup_specific_loggers(self):
        """Setup specific loggers for different components"""
        # Security logger
        security_logger = logging.getLogger('ainflue.security')
        security_handler = logging.handlers.RotatingFileHandler(
            self.log_dir / "security.log",
            maxBytes=self._parse_size("50MB"),
            backupCount=20
        )
        security_handler.setFormatter(CustomJSONFormatter())
        security_logger.addHandler(security_handler)
        security_logger.setLevel(logging.INFO)
        self.loggers['security'] = security_logger
        
        # Audit logger
        audit_logger = logging.getLogger('ainflue.audit')
        audit_handler = logging.handlers.RotatingFileHandler(
            self.log_dir / "audit.log",
            maxBytes=self._parse_size("100MB"),
            backupCount=30
        )
        audit_handler.setFormatter(CustomJSONFormatter())
        audit_logger.addHandler(audit_handler)
        audit_logger.setLevel(logging.INFO)
        self.loggers['audit'] = audit_logger
        
        # Performance logger
        performance_logger = logging.getLogger('ainflue.performance')
        performance_handler = logging.handlers.RotatingFileHandler(
            self.log_dir / "performance.log",
            maxBytes=self._parse_size("200MB"),
            backupCount=10
        )
        performance_handler.setFormatter(CustomJSONFormatter())
        performance_logger.addHandler(performance_handler)
        performance_logger.setLevel(logging.DEBUG)
        self.loggers['performance'] = performance_logger
        
        # Business logger
        business_logger = logging.getLogger('ainflue.business')
        business_handler = logging.handlers.RotatingFileHandler(
            self.log_dir / "business.log",
            maxBytes=self._parse_size("500MB"),
            backupCount=15
        )
        business_handler.setFormatter(CustomJSONFormatter())
        business_logger.addHandler(business_handler)
        business_logger.setLevel(logging.INFO)
        self.loggers['business'] = business_logger
        
        # AI/ML logger
        ai_logger = logging.getLogger('ainflue.ai')
        ai_handler = logging.handlers.RotatingFileHandler(
            self.log_dir / "ai.log",
            maxBytes=self._parse_size("1GB"),
            backupCount=5
        )
        ai_handler.setFormatter(CustomJSONFormatter())
        ai_logger.addHandler(ai_handler)
        ai_logger.setLevel(logging.DEBUG)
        self.loggers['ai'] = ai_logger
    
    def get_logger(self, name: str) -> logging.Logger:
        """Get specific logger by name"""
        if name in self.loggers:
            return self.loggers[name]
        return logging.getLogger(f'ainflue.{name}')
    
    def get_complete_config(self) -> Dict[str, Any]:
        """Get complete logging configuration"""
        return {
            "level": self.level.value,
            "format_type": self.format_type.value,
            "destinations": [dest.value for dest in self.destinations],
            "log_directory": str(self.log_dir),
            "rotation": self.rotation_config.get_rotation_config(),
            "security": self.security_config.get_security_config(),
            "business": self.business_config.get_business_config(),
            "performance": self.performance_config.get_performance_config(),
            "loggers": list(self.loggers.keys())
        }
    
    async def rotate_logs(self):
        """Manually rotate logs"""
        for logger_name, logger in self.loggers.items():
            for handler in logger.handlers:
                if isinstance(handler, logging.handlers.RotatingFileHandler):
                    handler.doRollover()
    
    def log_security_event(self, event_type: str, details: Dict[str, Any]):
        """Log security event"""
        security_logger = self.get_logger('security')
        security_logger.info(
            f"Security event: {event_type}",
            extra={
                "event_type": event_type,
                "details": details,
                "category": "security"
            }
        )
    
    def log_business_event(self, event_type: str, user_id: str, details: Dict[str, Any]):
        """Log business event"""
        business_logger = self.get_logger('business')
        business_logger.info(
            f"Business event: {event_type}",
            extra={
                "event_type": event_type,
                "user_id": user_id,
                "details": details,
                "category": "business"
            }
        )
    
    def log_performance_metric(self, metric_name: str, value: float, unit: str):
        """Log performance metric"""
        performance_logger = self.get_logger('performance')
        performance_logger.debug(
            f"Performance metric: {metric_name}",
            extra={
                "metric_name": metric_name,
                "value": value,
                "unit": unit,
                "category": "performance"
            }
        )

# Global logging configuration instance
logging_config = LoggingConfiguration()

# Export main classes
__all__ = [
    "LoggingConfiguration",
    "LogLevel",
    "LogFormat", 
    "LogDestination",
    "LogRotationConfig",
    "SecurityLoggingConfig",
    "BusinessLoggingConfig",
    "PerformanceLoggingConfig",
    "CustomJSONFormatter",
    "logging_config"
]
