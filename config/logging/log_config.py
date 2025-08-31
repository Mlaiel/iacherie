"""
Professional Logging Configuration for IA-Influencer Agent Platform
==================================================================

Core logging configuration management with enterprise-grade features
for multi-format content protection and AI processing pipeline.

Author: Fahed Mlaiel <mlaiel@live.de>
Project: IA-Influencer Agent + Content Protection Platform
Team: Lead Dev IA + Backend Senior + ML Engineer + DBA + Security + Microservices + Audio + DevOps

Copyright Notice:
This code is the intellectual property of Fahed Mlaiel.
Any unauthorized use, reproduction, or distribution of this code
without explicit written permission from the author is strictly prohibited.

Contact: mlaiel@live.de for licensing inquiries.
"""

import logging
import logging.config
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional, List, Union
from dataclasses import dataclass, field
from enum import Enum

import structlog
import colorama
from pythonjsonlogger import jsonlogger
from logging_tree import printout


class LogLevel(str, Enum):
    """Standardized logging levels for the platform"""
    CRITICAL = "CRITICAL"
    ERROR = "ERROR"
    WARNING = "WARNING"
    INFO = "INFO"
    DEBUG = "DEBUG"
    TRACE = "TRACE"


class LoggerName(str, Enum):
    """Standard logger names for different platform components"""
    # Core Platform Loggers
    PLATFORM = "ia_influencer_platform"
    API = "ia_influencer_api"
    AUTH = "ia_influencer_auth"
    
    # Content Protection Loggers
    FINGERPRINTING = "ia_influencer_fingerprinting"
    PROTECTION = "ia_influencer_protection"
    DETECTION = "ia_influencer_detection"
    
    # AI Processing Loggers
    AI_ENGINE = "ia_influencer_ai_engine"
    ML_PIPELINE = "ia_influencer_ml_pipeline"
    AUDIO_PROCESSING = "ia_influencer_audio"
    VIDEO_PROCESSING = "ia_influencer_video"
    IMAGE_PROCESSING = "ia_influencer_image"
    TEXT_PROCESSING = "ia_influencer_text"
    
    # Business Logic Loggers
    MONETIZATION = "ia_influencer_monetization"
    COLLABORATION = "ia_influencer_collaboration"
    DISTRIBUTION = "ia_influencer_distribution"
    
    # Infrastructure Loggers
    DATABASE = "ia_influencer_database"
    CACHE = "ia_influencer_cache"
    QUEUE = "ia_influencer_queue"
    STORAGE = "ia_influencer_storage"
    
    # Security & Audit Loggers
    SECURITY = "ia_influencer_security"
    AUDIT = "ia_influencer_audit"
    COMPLIANCE = "ia_influencer_compliance"
    
    # External Integration Loggers
    SPOTIFY = "ia_influencer_spotify"
    YOUTUBE = "ia_influencer_youtube"
    INSTAGRAM = "ia_influencer_instagram"
    TIKTOK = "ia_influencer_tiktok"
    
    # Performance & Monitoring
    PERFORMANCE = "ia_influencer_performance"
    MONITORING = "ia_influencer_monitoring"
    METRICS = "ia_influencer_metrics"


@dataclass
class LogFormatConfig:
    """Configuration for log formatting"""
    use_json: bool = True
    use_colors: bool = True
    include_timestamp: bool = True
    include_level: bool = True
    include_logger_name: bool = True
    include_module: bool = True
    include_function: bool = True
    include_line_number: bool = True
    include_thread_id: bool = True
    include_process_id: bool = True
    include_request_id: bool = True
    include_user_id: bool = True
    include_tenant_id: bool = True
    include_correlation_id: bool = True
    custom_fields: Dict[str, Any] = field(default_factory=dict)


@dataclass
class LogFileConfig:
    """Configuration for log file handling"""
    enabled: bool = True
    base_path: str = "/var/log/ia_influencer"
    filename_pattern: str = "{logger_name}_{date}.log"
    max_file_size: str = "100MB"
    backup_count: int = 30
    compression: Optional[str] = "gzip"
    separate_errors: bool = True
    separate_security: bool = True
    separate_audit: bool = True
    separate_performance: bool = True


@dataclass
class LogElasticConfig:
    """Configuration for Elasticsearch integration"""
    enabled: bool = True
    hosts: List[str] = field(default_factory=lambda: ["localhost:9200"])
    index_pattern: str = "ia-influencer-logs-{date}"
    buffer_size: int = 1000
    flush_interval: int = 30
    include_metadata: bool = True
    ssl_enabled: bool = False
    username: Optional[str] = None
    password: Optional[str] = None


class LogConfig:
    """
    Enterprise-grade logging configuration manager for IA-Influencer platform.
    
    Handles multi-tenant, multi-format content processing logging with
    advanced features like structured logging, audit trails, performance monitoring,
    and security event tracking.
    """
    
    def __init__(
        self,
        environment: str = "development",
        log_level: str = LogLevel.INFO,
        format_config: Optional[LogFormatConfig] = None,
        file_config: Optional[LogFileConfig] = None,
        elastic_config: Optional[LogElasticConfig] = None,
        enable_console: bool = True,
        enable_sentry: bool = False,
        sentry_dsn: Optional[str] = None
    ):
        """
        Initialize logging configuration.
        
        Args:
            environment: Deployment environment (development, staging, production)
            log_level: Default logging level
            format_config: Log format configuration
            file_config: File logging configuration  
            elastic_config: Elasticsearch logging configuration
            enable_console: Enable console output
            enable_sentry: Enable Sentry error tracking
            sentry_dsn: Sentry DSN for error reporting
        """
        self.environment = environment
        self.log_level = log_level
        self.format_config = format_config or LogFormatConfig()
        self.file_config = file_config or LogFileConfig()
        self.elastic_config = elastic_config or LogElasticConfig()
        self.enable_console = enable_console
        self.enable_sentry = enable_sentry
        self.sentry_dsn = sentry_dsn
        
        # Initialize colorama for colored console output
        colorama.init()
        
        # Configure structlog for structured logging
        self._configure_structlog()
        
        # Build logging configuration
        self._config = self._build_logging_config()
        
        # Apply configuration
        self._apply_configuration()
    
    def _configure_structlog(self) -> None:
        """Configure structlog for structured logging"""
        processors = [
            structlog.stdlib.filter_by_level,
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            structlog.stdlib.PositionalArgumentsFormatter(),
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.UnicodeDecoder(),
        ]
        
        if self.format_config.use_json:
            processors.append(structlog.processors.JSONRenderer())
        else:
            processors.append(structlog.dev.ConsoleRenderer(colors=self.format_config.use_colors))
        
        structlog.configure(
            processors=processors,
            wrapper_class=structlog.stdlib.BoundLogger,
            logger_factory=structlog.stdlib.LoggerFactory(),
            cache_ctor_on_first_use=True,
        )
    
    def _build_logging_config(self) -> Dict[str, Any]:
        """Build comprehensive logging configuration"""
        config = {
            'version': 1,
            'disable_existing_loggers': False,
            'formatters': self._build_formatters(),
            'filters': self._build_filters(),
            'handlers': self._build_handlers(),
            'loggers': self._build_loggers(),
            'root': {
                'level': self.log_level,
                'handlers': ['console', 'file'] if self.enable_console else ['file']
            }
        }
        
        return config
    
    def _build_formatters(self) -> Dict[str, Any]:
        """Build formatter configurations"""
        formatters = {}
        
        # JSON Formatter for structured logging
        json_format = {
            'timestamp': 'asctime',
            'level': 'levelname',
            'logger': 'name',
            'module': 'module',
            'function': 'funcName',
            'line': 'lineno',
            'thread': 'thread',
            'process': 'process',
            'message': 'message'
        }
        
        if self.format_config.include_request_id:
            json_format['request_id'] = 'request_id'
        if self.format_config.include_user_id:
            json_format['user_id'] = 'user_id'
        if self.format_config.include_tenant_id:
            json_format['tenant_id'] = 'tenant_id'
        if self.format_config.include_correlation_id:
            json_format['correlation_id'] = 'correlation_id'
        
        formatters['json'] = {
            '()': jsonlogger.JsonFormatter,
            'format': ' '.join(f'%({k})s' for k in json_format.keys())
        }
        
        # Detailed formatter for file logging
        formatters['detailed'] = {
            'format': (
                '%(asctime)s | %(levelname)-8s | %(name)s | '
                '%(module)s.%(funcName)s:%(lineno)d | '
                'PID:%(process)d TID:%(thread)d | %(message)s'
            ),
            'datefmt': '%Y-%m-%d %H:%M:%S'
        }
        
        # Console formatter with colors
        if self.format_config.use_colors:
            formatters['colored'] = {
                'format': (
                    '\033[36m%(asctime)s\033[0m | '
                    '\033[%(levelcolor)sm%(levelname)-8s\033[0m | '
                    '\033[35m%(name)s\033[0m | '
                    '\033[32m%(module)s.%(funcName)s:%(lineno)d\033[0m | '
                    '%(message)s'
                ),
                'datefmt': '%H:%M:%S'
            }
        
        # Simple formatter for basic logging
        formatters['simple'] = {
            'format': '%(levelname)s | %(name)s | %(message)s'
        }
        
        return formatters
    
    def _build_filters(self) -> Dict[str, Any]:
        """Build filter configurations"""



        return {
            'security_filter': {
                '()': 'backend.config.logging.log_filtering_config.SecurityLogFilter'
            },
            'performance_filter': {
                '()': 'backend.config.logging.log_filtering_config.PerformanceLogFilter'
            },
            'audit_filter': {
                '()': 'backend.config.logging.log_filtering_config.AuditLogFilter'
            }
        }
    
    def _build_handlers(self) -> Dict[str, Any]:
        """Build handler configurations"""
        handlers = {}
        
        # Console handler
        if self.enable_console:
            handlers['console'] = {
                'class': 'logging.StreamHandler',
                'level': self.log_level,
                'formatter': 'colored' if self.format_config.use_colors else 'simple',
                'stream': 'ext://sys.stdout'
            }
        
        # File handlers
        if self.file_config.enabled:
            # Main application log
            handlers['file'] = {
                'class': 'logging.handlers.RotatingFileHandler',
                'level': self.log_level,
                'formatter': 'detailed',
                'filename': os.path.join(
                    self.file_config.base_path,
                    f'{LoggerName.PLATFORM}_{datetime.now().strftime("%Y-%m-%d")}.log'
                ),
                'maxBytes': self._parse_file_size(self.file_config.max_file_size),
                'backupCount': self.file_config.backup_count
            }
            
            # Error log file
            if self.file_config.separate_errors:
                handlers['error_file'] = {
                    'class': 'logging.handlers.RotatingFileHandler',
                    'level': 'ERROR',
                    'formatter': 'json',
                    'filename': os.path.join(
                        self.file_config.base_path,
                        f'errors_{datetime.now().strftime("%Y-%m-%d")}.log'
                    ),
                    'maxBytes': self._parse_file_size(self.file_config.max_file_size),
                    'backupCount': self.file_config.backup_count
                }
            
            # Security log file
            if self.file_config.separate_security:
                handlers['security_file'] = {
                    'class': 'logging.handlers.RotatingFileHandler',
                    'level': 'INFO',
                    'formatter': 'json',
                    'filters': ['security_filter'],
                    'filename': os.path.join(
                        self.file_config.base_path,
                        f'security_{datetime.now().strftime("%Y-%m-%d")}.log'
                    ),
                    'maxBytes': self._parse_file_size(self.file_config.max_file_size),
                    'backupCount': self.file_config.backup_count
                }
            
            # Audit log file
            if self.file_config.separate_audit:
                handlers['audit_file'] = {
                    'class': 'logging.handlers.RotatingFileHandler',
                    'level': 'INFO',
                    'formatter': 'json',
                    'filters': ['audit_filter'],
                    'filename': os.path.join(
                        self.file_config.base_path,
                        f'audit_{datetime.now().strftime("%Y-%m-%d")}.log'
                    ),
                    'maxBytes': self._parse_file_size(self.file_config.max_file_size),
                    'backupCount': self.file_config.backup_count
                }
            
            # Performance log file
            if self.file_config.separate_performance:
                handlers['performance_file'] = {
                    'class': 'logging.handlers.RotatingFileHandler',
                    'level': 'INFO',
                    'formatter': 'json',
                    'filters': ['performance_filter'],
                    'filename': os.path.join(
                        self.file_config.base_path,
                        f'performance_{datetime.now().strftime("%Y-%m-%d")}.log'
                    ),
                    'maxBytes': self._parse_file_size(self.file_config.max_file_size),
                    'backupCount': self.file_config.backup_count
                }
        
        # Elasticsearch handler
        if self.elastic_config.enabled:
            handlers['elasticsearch'] = {
                'class': 'backend.config.logging.log_aggregation_config.ElasticsearchHandler',
                'level': 'INFO',
                'formatter': 'json',
                'hosts': self.elastic_config.hosts,
                'index_pattern': self.elastic_config.index_pattern,
                'buffer_size': self.elastic_config.buffer_size,
                'flush_interval': self.elastic_config.flush_interval
            }
        
        # Sentry handler for error tracking
        if self.enable_sentry and self.sentry_dsn:
            handlers['sentry'] = {
                'class': 'sentry_sdk.integrations.logging.SentryHandler',
                'level': 'ERROR',
                'formatter': 'json'
            }
        
        return handlers
    
    def _build_loggers(self) -> Dict[str, Any]:
        """Build logger configurations for all platform components"""
        loggers = {}
        
        # Default handlers for all loggers
        default_handlers = ['console', 'file'] if self.enable_console else ['file']
        
        if self.elastic_config.enabled:
            default_handlers.append('elasticsearch')
        
        if self.enable_sentry:
            default_handlers.append('sentry')
        
        # Configure all standard loggers
        for logger_name in LoggerName:
            loggers[logger_name.value] = {
                'level': self.log_level,
                'handlers': default_handlers.copy(),
                'propagate': False
            }
        
        # Security logger gets additional security file handler
        if LoggerName.SECURITY.value in loggers and self.file_config.separate_security:
            loggers[LoggerName.SECURITY.value]['handlers'].append('security_file')
        
        # Audit logger gets additional audit file handler
        if LoggerName.AUDIT.value in loggers and self.file_config.separate_audit:
            loggers[LoggerName.AUDIT.value]['handlers'].append('audit_file')
        
        # Performance logger gets additional performance file handler
        if LoggerName.PERFORMANCE.value in loggers and self.file_config.separate_performance:
            loggers[LoggerName.PERFORMANCE.value]['handlers'].append('performance_file')
        
        # External library loggers
        external_loggers = [
            'uvicorn', 'fastapi', 'sqlalchemy', 'celery', 'redis',
            'elasticsearch', 'boto3', 'requests', 'httpx'
        ]
        
        for logger_name in external_loggers:
            loggers[logger_name] = {
                'level': 'WARNING',
                'handlers': default_handlers,
                'propagate': False
            }
        
        return loggers
    
    def _parse_file_size(self, size_str: str) -> int:
        """Parse file size string to bytes"""
        size_str = size_str.upper()
        multipliers = {'B': 1, 'KB': 1024, 'MB': 1024**2, 'GB': 1024**3}
        
        for suffix, multiplier in multipliers.items():
            if size_str.endswith(suffix):
                return int(size_str[:-len(suffix)]) * multiplier
        
        # Default to bytes if no suffix
        return int(size_str)
    
    def _apply_configuration(self) -> None:
        """Apply the logging configuration"""
        # Ensure log directory exists
        if self.file_config.enabled:
            Path(self.file_config.base_path).mkdir(parents=True, exist_ok=True)
        
        # Apply logging configuration
        logging.config.dictConfig(self._config)
        
        # Initialize Sentry if enabled
        if self.enable_sentry and self.sentry_dsn:
            import sentry_sdk
            sentry_sdk.init(dsn=self.sentry_dsn)
    
    def get_logger(self, name: Union[str, LoggerName]) -> logging.Logger:
        """
        Get a configured logger instance.
        
        Args:
            name: Logger name (string or LoggerName enum)
            
        Returns:
            Configured logger instance
        """
        logger_name = name.value if isinstance(name, LoggerName) else name
        return logging.getLogger(logger_name)
    
    def get_structured_logger(self, name: Union[str, LoggerName]) -> structlog.BoundLogger:
        """
        Get a structured logger instance.
        
        Args:
            name: Logger name (string or LoggerName enum)
            
        Returns:
            Structured logger instance
        """
        logger_name = name.value if isinstance(name, LoggerName) else name
        return structlog.get_logger(logger_name)
    
    def set_context(self, **kwargs) -> None:
        """
        Set global logging context (request ID, user ID, etc.)
        
        Args:
            **kwargs: Context key-value pairs
        """
        for key, value in kwargs.items():
            structlog.contextvars.bind_contextvars(**{key: value})
    
    def clear_context(self) -> None:
        """Clear global logging context"""
        structlog.contextvars.clear_contextvars()
    
    def print_logger_tree(self) -> None:
        """Print the current logger configuration tree for debugging"""
        print("Current Logger Configuration Tree:")
        print("=" * 50)
        printout()
    
    def get_config_dict(self) -> Dict[str, Any]:
        """Get the current logging configuration as dictionary"""



        return self._config.copy()
    
    def update_log_level(self, logger_name: str, level: Union[str, int]) -> None:
        """
        Update log level for a specific logger.
        
        Args:
            logger_name: Name of the logger to update
            level: New log level
        """
        logger = logging.getLogger(logger_name)
        logger.setLevel(level)
    
    def add_custom_handler(self, name: str, handler_config: Dict[str, Any]) -> None:
        """
        Add a custom handler to the logging configuration.
        
        Args:
            name: Handler name
            handler_config: Handler configuration dictionary
        """
        self._config['handlers'][name] = handler_config
        logging.config.dictConfig(self._config)
    
    def remove_handler(self, logger_name: str, handler_name: str) -> None:
        """
        Remove a handler from a specific logger.
        
        Args:
            logger_name: Name of the logger
            handler_name: Name of the handler to remove
        """
        logger = logging.getLogger(logger_name)
        handlers_to_remove = [h for h in logger.handlers if h.name == handler_name]
        
        for handler in handlers_to_remove:
            logger.removeHandler(handler)


def create_default_log_config(
    environment: str = "development",
    log_level: str = LogLevel.INFO
) -> LogConfig:
    """
    Create a default logging configuration for the platform.
    
    Args:
        environment: Deployment environment
        log_level: Default log level
        
    Returns:
        Configured LogConfig instance
    """
    # Environment-specific configurations
    if environment == "production":
        format_config = LogFormatConfig(
            use_json=True,
            use_colors=False,
            include_request_id=True,
            include_user_id=True,
            include_tenant_id=True,
            include_correlation_id=True
        )
        
        file_config = LogFileConfig(
            enabled=True,
            base_path="/var/log/ia_influencer",
            max_file_size="500MB",
            backup_count=60,
            compression="gzip",
            separate_errors=True,
            separate_security=True,
            separate_audit=True,
            separate_performance=True
        )
        
        elastic_config = LogElasticConfig(
            enabled=True,
            hosts=os.getenv("ELASTICSEARCH_HOSTS", "localhost:9200").split(","),
            buffer_size=5000,
            flush_interval=10
        )
        
        return LogConfig(
            environment=environment,
            log_level=log_level,
            format_config=format_config,
            file_config=file_config,
            elastic_config=elastic_config,
            enable_console=False,
            enable_sentry=True,
            sentry_dsn=os.getenv("SENTRY_DSN")
        )
    
    elif environment == "staging":
        format_config = LogFormatConfig(
            use_json=True,
            use_colors=True,
            include_request_id=True,
            include_user_id=True,
            include_tenant_id=True
        )
        
        file_config = LogFileConfig(
            enabled=True,
            base_path="/var/log/ia_influencer",
            max_file_size="200MB",
            backup_count=30,
            separate_errors=True,
            separate_security=True,
            separate_audit=True
        )
        
        elastic_config = LogElasticConfig(
            enabled=True,
            buffer_size=1000,
            flush_interval=30
        )
        
        return LogConfig(
            environment=environment,
            log_level=log_level,
            format_config=format_config,
            file_config=file_config,
            elastic_config=elastic_config,
            enable_console=True,
            enable_sentry=True,
            sentry_dsn=os.getenv("SENTRY_DSN")
        )
    
    else:  # development
        format_config = LogFormatConfig(
            use_json=False,
            use_colors=True,
            include_request_id=True
        )
        
        file_config = LogFileConfig(
            enabled=True,
            base_path="./logs",
            max_file_size="50MB",
            backup_count=7,
            separate_errors=False,
            separate_security=False,
            separate_audit=False
        )
        
        elastic_config = LogElasticConfig(enabled=False)
        
        return LogConfig(
            environment=environment,
            log_level=LogLevel.DEBUG,
            format_config=format_config,
            file_config=file_config,
            elastic_config=elastic_config,
            enable_console=True,
            enable_sentry=False
        )


# Global logging configuration instance
_log_config: Optional[LogConfig] = None


def initialize_logging(
    environment: str = None,
    log_level: str = None,
    config: Optional[LogConfig] = None
) -> LogConfig:
    """
    Initialize global logging configuration for the platform.
    
    Args:
        environment: Deployment environment
        log_level: Default log level
        config: Custom LogConfig instance
        
    Returns:
        Initialized LogConfig instance
    """
    global _log_config
    
    if config:
        _log_config = config
    else:
        environment = environment or os.getenv("ENVIRONMENT", "development")
        log_level = log_level or os.getenv("LOG_LEVEL", LogLevel.INFO)
        _log_config = create_default_log_config(environment, log_level)
    
    return _log_config


def get_logger(name: Union[str, LoggerName]) -> logging.Logger:
    """
    Get a logger instance using the global configuration.
    
    Args:
        name: Logger name
        
    Returns:
        Logger instance
    """
    if not _log_config:
        initialize_logging()
    
    return _log_config.get_logger(name)


def get_structured_logger(name: Union[str, LoggerName]) -> structlog.BoundLogger:
    """
    Get a structured logger instance using the global configuration.
    
    Args:
        name: Logger name
        
    Returns:
        Structured logger instance
    """
    if not _log_config:
        initialize_logging()
    
    return _log_config.get_structured_logger(name)
