"""Logging Configuration - IA Influencer Agent Platform
Advanced logging configuration with structured logging and multiple handlers

Author: Fahed Mlaiel <mlaiel@live.de>
WARNING: This code is protected by copyright. Any unauthorized use, reproduction,
or distribution without written permission from Fahed Mlaiel is strictly prohibited.
"""
import os
import logging
import logging.handlers
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, field
from enum import Enum
import json
from pathlib import Path


class LogLevel(Enum):
    """Supported logging levels"""
    CRITICAL = "CRITICAL"
    ERROR = "ERROR"
    WARNING = "WARNING"
    INFO = "INFO"
    DEBUG = "DEBUG"
    NOTSET = "NOTSET"


class LogFormat(Enum):
    """Supported log formats"""
    STANDARD = "standard"
    DETAILED = "detailed"
    JSON = "json"
    SYSLOG = "syslog"
    CUSTOM = "custom"


class LogHandler(Enum):
    """Supported log handlers"""
    CONSOLE = "console"
    FILE = "file"
    ROTATING_FILE = "rotating_file"
    TIMED_ROTATING_FILE = "timed_rotating_file"
    SYSLOG = "syslog"
    ELASTICSEARCH = "elasticsearch"
    KAFKA = "kafka"
    WEBHOOK = "webhook"


@dataclass
class StructuredLogConfig:
    """Configuration for structured logging"""
    
    enabled: bool = field(default_factory=lambda: 
        os.getenv("STRUCTURED_LOGGING_ENABLED", "true").lower() == "true")
    
    # Standard fields to include in all log messages
    include_timestamp: bool = True
    include_level: bool = True
    include_logger_name: bool = True
    include_module: bool = True
    include_function: bool = True
    include_line_number: bool = True
    include_thread_id: bool = True
    include_process_id: bool = True
    include_hostname: bool = True
    
    # Application-specific fields
    include_user_id: bool = field(default_factory=lambda: 
        os.getenv("LOG_INCLUDE_USER_ID", "true").lower() == "true")
    include_request_id: bool = field(default_factory=lambda: 
        os.getenv("LOG_INCLUDE_REQUEST_ID", "true").lower() == "true")
    include_session_id: bool = field(default_factory=lambda: 
        os.getenv("LOG_INCLUDE_SESSION_ID", "false").lower() == "true")
    include_ip_address: bool = field(default_factory=lambda: 
        os.getenv("LOG_INCLUDE_IP_ADDRESS", "true").lower() == "true")
    include_user_agent: bool = field(default_factory=lambda: 
        os.getenv("LOG_INCLUDE_USER_AGENT", "false").lower() == "true")
    
    # Performance fields
    include_execution_time: bool = field(default_factory=lambda: 
        os.getenv("LOG_INCLUDE_EXECUTION_TIME", "true").lower() == "true")
    include_memory_usage: bool = field(default_factory=lambda: 
        os.getenv("LOG_INCLUDE_MEMORY_USAGE", "false").lower() == "true")
    
    # Business context fields
    include_content_type: bool = field(default_factory=lambda: 
        os.getenv("LOG_INCLUDE_CONTENT_TYPE", "true").lower() == "true")
    include_operation_type: bool = field(default_factory=lambda: 
        os.getenv("LOG_INCLUDE_OPERATION_TYPE", "true").lower() == "true")
    
    # Sensitive data handling
    mask_sensitive_data: bool = field(default_factory=lambda: 
        os.getenv("LOG_MASK_SENSITIVE_DATA", "true").lower() == "true")
    sensitive_fields: List[str] = field(default_factory=lambda: [
        "password", "token", "api_key", "secret", "private_key", 
        "credit_card", "ssn", "email", "phone"
    ])


@dataclass
class FileHandlerConfig:
    """Configuration for file-based log handlers"""
    
    # Basic file settings
    filename: str = field(default_factory=lambda: 
        os.getenv("LOG_FILE_PATH", "/var/log/ia_influencer_agent.log"))
    mode: str = "a"
    encoding: str = "utf-8"
    delay: bool = False
    
    # File rotation settings
    max_bytes: int = field(default_factory=lambda: 
        int(os.getenv("LOG_FILE_MAX_BYTES", "10485760")))  # 10MB
    backup_count: int = field(default_factory=lambda: 
        int(os.getenv("LOG_FILE_BACKUP_COUNT", "5")))
    
    # Time-based rotation settings
    when: str = field(default_factory=lambda: os.getenv("LOG_ROTATION_WHEN", "midnight"))
    interval: int = field(default_factory=lambda: int(os.getenv("LOG_ROTATION_INTERVAL", "1")))
    utc: bool = field(default_factory=lambda: 
        os.getenv("LOG_ROTATION_UTC", "true").lower() == "true")
    
    # File permissions
    file_permissions: int = 0o644
    directory_permissions: int = 0o755
    
    def __post_init__(self):
        """Ensure log directory exists"""
        log_dir = Path(self.filename).parent
        log_dir.mkdir(parents=True, exist_ok=True, mode=self.directory_permissions)


@dataclass
class SyslogHandlerConfig:
    """Configuration for syslog handler"""
    
    enabled: bool = field(default_factory=lambda: 
        os.getenv("SYSLOG_ENABLED", "false").lower() == "true")
    host: str = field(default_factory=lambda: os.getenv("SYSLOG_HOST", "localhost"))
    port: int = field(default_factory=lambda: int(os.getenv("SYSLOG_PORT", "514")))
    facility: str = field(default_factory=lambda: os.getenv("SYSLOG_FACILITY", "user"))
    socktype: str = field(default_factory=lambda: os.getenv("SYSLOG_SOCKTYPE", "UDP"))
    
    @property
    def address(self) -> tuple:
        """Get syslog server address"""
        return (self.host, self.port)


@dataclass
class ElasticsearchHandlerConfig:
    """Configuration for Elasticsearch log handler"""
    
    enabled: bool = field(default_factory=lambda: 
        os.getenv("ELASTICSEARCH_LOGGING_ENABLED", "false").lower() == "true")
    hosts: List[str] = field(default_factory=lambda: 
        os.getenv("ELASTICSEARCH_HOSTS", "localhost:9200").split(","))
    index_prefix: str = field(default_factory=lambda: 
        os.getenv("ELASTICSEARCH_LOG_INDEX_PREFIX", "ia-influencer-logs"))
    doc_type: str = "_doc"
    
    # Authentication
    username: Optional[str] = field(default_factory=lambda: os.getenv("ELASTICSEARCH_USERNAME"))
    password: Optional[str] = field(default_factory=lambda: os.getenv("ELASTICSEARCH_PASSWORD"))
    api_key: Optional[str] = field(default_factory=lambda: os.getenv("ELASTICSEARCH_API_KEY"))
    
    # SSL settings
    use_ssl: bool = field(default_factory=lambda: 
        os.getenv("ELASTICSEARCH_USE_SSL", "false").lower() == "true")
    verify_certs: bool = field(default_factory=lambda: 
        os.getenv("ELASTICSEARCH_VERIFY_CERTS", "true").lower() == "true")
    
    # Performance settings
    buffer_size: int = field(default_factory=lambda: int(os.getenv("ELASTICSEARCH_BUFFER_SIZE", "100")))
    flush_frequency: int = field(default_factory=lambda: int(os.getenv("ELASTICSEARCH_FLUSH_FREQUENCY", "1")))
    timeout: int = field(default_factory=lambda: int(os.getenv("ELASTICSEARCH_TIMEOUT", "30")))


@dataclass
class WebhookHandlerConfig:
    """Configuration for webhook log handler"""
    
    enabled: bool = field(default_factory=lambda: 
        os.getenv("WEBHOOK_LOGGING_ENABLED", "false").lower() == "true")
    url: Optional[str] = field(default_factory=lambda: os.getenv("LOG_WEBHOOK_URL"))
    method: str = "POST"
    timeout: int = field(default_factory=lambda: int(os.getenv("LOG_WEBHOOK_TIMEOUT", "10")))
    
    # Headers
    headers: Dict[str, str] = field(default_factory=lambda: {
        "Content-Type": "application/json",
        "User-Agent": "IA-Influencer-Agent-Logger/1.0"
    })
    
    # Authentication
    auth_header: Optional[str] = field(default_factory=lambda: os.getenv("LOG_WEBHOOK_AUTH_HEADER"))
    auth_token: Optional[str] = field(default_factory=lambda: os.getenv("LOG_WEBHOOK_AUTH_TOKEN"))
    
    # Retry configuration
    retry_attempts: int = field(default_factory=lambda: int(os.getenv("LOG_WEBHOOK_RETRY_ATTEMPTS", "3")))
    retry_delay: int = field(default_factory=lambda: int(os.getenv("LOG_WEBHOOK_RETRY_DELAY", "1")))


@dataclass
class LoggingConfig:
    """Comprehensive logging configuration"""
    
    # Global logging settings
    enabled: bool = field(default_factory=lambda: 
        os.getenv("LOGGING_ENABLED", "true").lower() == "true")
    root_level: LogLevel = field(default_factory=lambda: 
        LogLevel(os.getenv("LOG_LEVEL", "INFO")))
    
    # Log format configuration
    log_format: LogFormat = field(default_factory=lambda: 
        LogFormat(os.getenv("LOG_FORMAT", "json")))
    date_format: str = field(default_factory=lambda: 
        os.getenv("LOG_DATE_FORMAT", "%Y-%m-%d %H:%M:%S"))
    timezone: str = field(default_factory=lambda: os.getenv("LOG_TIMEZONE", "UTC"))
    
    # Handler configurations
    console_enabled: bool = field(default_factory=lambda: 
        os.getenv("LOG_CONSOLE_ENABLED", "true").lower() == "true")
    file_enabled: bool = field(default_factory=lambda: 
        os.getenv("LOG_FILE_ENABLED", "true").lower() == "true")
    
    # Component configurations
    structured: StructuredLogConfig = field(default_factory=StructuredLogConfig)
    file_handler: FileHandlerConfig = field(default_factory=FileHandlerConfig)
    syslog_handler: SyslogHandlerConfig = field(default_factory=SyslogHandlerConfig)
    elasticsearch_handler: ElasticsearchHandlerConfig = field(default_factory=ElasticsearchHandlerConfig)
    webhook_handler: WebhookHandlerConfig = field(default_factory=WebhookHandlerConfig)
    
    # Logger-specific configurations
    logger_configs: Dict[str, Dict[str, Any]] = field(default_factory=lambda: {
        "uvicorn": {"level": "INFO", "handlers": ["console", "file"]},
        "uvicorn.access": {"level": "INFO", "handlers": ["file"]},
        "fastapi": {"level": "INFO", "handlers": ["console", "file"]},
        "sqlalchemy": {"level": "WARNING", "handlers": ["file"]},
        "celery": {"level": "INFO", "handlers": ["console", "file"]},
        "ia_influencer_agent": {"level": "DEBUG", "handlers": ["console", "file", "elasticsearch"]},
        "ia_influencer_agent.security": {"level": "INFO", "handlers": ["console", "file", "webhook"]},
        "ia_influencer_agent.business": {"level": "INFO", "handlers": ["console", "file"]},
        "ia_influencer_agent.ml": {"level": "INFO", "handlers": ["console", "file"]},
        "ia_influencer_agent.protection": {"level": "INFO", "handlers": ["console", "file", "elasticsearch"]}
    })
    
    # Performance settings
    disable_existing_loggers: bool = False
    capture_warnings: bool = True
    
    # Security settings
    sanitize_urls: bool = field(default_factory=lambda: 
        os.getenv("LOG_SANITIZE_URLS", "true").lower() == "true")
    log_sql_queries: bool = field(default_factory=lambda: 
        os.getenv("LOG_SQL_QUERIES", "false").lower() == "true")
    log_request_body: bool = field(default_factory=lambda: 
        os.getenv("LOG_REQUEST_BODY", "false").lower() == "true")
    log_response_body: bool = field(default_factory=lambda: 
        os.getenv("LOG_RESPONSE_BODY", "false").lower() == "true")
    
    # Sampling settings for high-volume logs
    enable_sampling: bool = field(default_factory=lambda: 
        os.getenv("LOG_ENABLE_SAMPLING", "false").lower() == "true")
    sampling_rate: float = field(default_factory=lambda: 
        float(os.getenv("LOG_SAMPLING_RATE", "0.1")))  # 10%
    
    def __post_init__(self):
        """Initialize logging configuration"""
        self._validate_configuration()
        if self.file_handler.auth_header and self.file_handler.auth_token:
            self.webhook_handler.headers[self.webhook_handler.auth_header] = self.webhook_handler.auth_token
    
    def _validate_configuration(self):
        """Validate logging configuration"""
        if not any([self.console_enabled, self.file_enabled, 
                   self.syslog_handler.enabled, self.elasticsearch_handler.enabled,
                   self.webhook_handler.enabled]):
            raise ValueError("At least one log handler must be enabled")
        
        if self.sampling_rate < 0 or self.sampling_rate > 1:
            raise ValueError("Sampling rate must be between 0 and 1")
        
        if self.webhook_handler.enabled and not self.webhook_handler.url:
            raise ValueError("Webhook URL is required when webhook logging is enabled")
    
    @property
    def log_level_int(self) -> int:
        """Get log level as integer"""
        return getattr(logging, self.root_level.value)
    
    def get_format_string(self, handler_type: LogHandler = LogHandler.CONSOLE) -> str:
        """Get format string based on log format type"""
        if self.log_format == LogFormat.JSON:
            return "%(message)s"  # JSON formatter will handle structure
        elif self.log_format == LogFormat.DETAILED:
            return (
                "%(asctime)s | %(levelname)-8s | %(name)s | "
                "%(funcName)s:%(lineno)d | %(message)s"
            )
        elif self.log_format == LogFormat.SYSLOG:
            return "%(name)s[%(process)d]: %(levelname)s %(message)s"
        elif self.log_format == LogFormat.STANDARD:
            return "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        else:  # CUSTOM
            return os.getenv("LOG_CUSTOM_FORMAT", 
                           "%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    
    def get_handlers_config(self) -> Dict[str, Dict[str, Any]]:
        """Get handlers configuration dictionary"""
        handlers = {}
        
        if self.console_enabled:
            handlers["console"] = {
                "class": "logging.StreamHandler",
                "level": self.root_level.value,
                "formatter": "default",
                "stream": "ext://sys.stdout"
            }
        
        if self.file_enabled:
            if self.file_handler.max_bytes > 0:
                handlers["file"] = {
                    "class": "logging.handlers.RotatingFileHandler",
                    "level": self.root_level.value,
                    "formatter": "detailed",
                    "filename": self.file_handler.filename,
                    "mode": self.file_handler.mode,
                    "maxBytes": self.file_handler.max_bytes,
                    "backupCount": self.file_handler.backup_count,
                    "encoding": self.file_handler.encoding
                }
            else:
                handlers["file"] = {
                    "class": "logging.FileHandler",
                    "level": self.root_level.value,
                    "formatter": "detailed",
                    "filename": self.file_handler.filename,
                    "mode": self.file_handler.mode,
                    "encoding": self.file_handler.encoding
                }
        
        if self.syslog_handler.enabled:
            handlers["syslog"] = {
                "class": "logging.handlers.SysLogHandler",
                "level": self.root_level.value,
                "formatter": "syslog",
                "address": self.syslog_handler.address,
                "facility": self.syslog_handler.facility
            }
        
        if self.elasticsearch_handler.enabled:
            handlers["elasticsearch"] = {
                "class": "ia_influencer_agent.utils.logging.ElasticsearchHandler",
                "level": self.root_level.value,
                "formatter": "json",
                "hosts": self.elasticsearch_handler.hosts,
                "index_prefix": self.elasticsearch_handler.index_prefix
            }
        
        if self.webhook_handler.enabled:
            handlers["webhook"] = {
                "class": "ia_influencer_agent.utils.logging.WebhookHandler",
                "level": self.root_level.value,
                "formatter": "json",
                "url": self.webhook_handler.url,
                "timeout": self.webhook_handler.timeout
            }
        
        return handlers
    
    def get_formatters_config(self) -> Dict[str, Dict[str, Any]]:
        """Get formatters configuration dictionary"""
        formatters = {
            "default": {
                "format": self.get_format_string(LogHandler.CONSOLE),
                "datefmt": self.date_format
            },
            "detailed": {
                "format": self.get_format_string(LogHandler.FILE),
                "datefmt": self.date_format
            },
            "syslog": {
                "format": self.get_format_string(LogHandler.SYSLOG),
                "datefmt": self.date_format
            }
        }
        
        if self.log_format == LogFormat.JSON or self.structured.enabled:
            formatters["json"] = {
                "class": "ia_influencer_agent.utils.logging.JSONFormatter",
                "datefmt": self.date_format
            }
        
        return formatters
    
    def get_loggers_config(self) -> Dict[str, Dict[str, Any]]:
        """Get loggers configuration dictionary"""
        loggers = {}
        
        for logger_name, config in self.logger_configs.items():
            loggers[logger_name] = {
                "level": config.get("level", self.root_level.value),
                "handlers": config.get("handlers", ["console"]),
                "propagate": config.get("propagate", False),
                "qualname": logger_name
            }
        
        return loggers
    
    def get_logging_dict_config(self) -> Dict[str, Any]:
        """Get complete logging configuration dictionary for dictConfig"""
        return {
            "version": 1,
            "disable_existing_loggers": self.disable_existing_loggers,
            "formatters": self.get_formatters_config(),
            "handlers": self.get_handlers_config(),
            "loggers": self.get_loggers_config(),
            "root": {
                "level": self.root_level.value,
                "handlers": ["console"] if self.console_enabled else []
            }
        }
    
    def configure_logging(self):
        """Configure Python logging using dictConfig"""
        if not self.enabled:
            logging.disable(logging.CRITICAL)
            return
        
        # Configure warnings capture
        if self.capture_warnings:
            logging.captureWarnings(True)
        
        # Apply configuration
        config_dict = self.get_logging_dict_config()
        logging.config.dictConfig(config_dict)
        
        # Set up sampling if enabled
        if self.enable_sampling:
            self._setup_sampling()
    
    def _setup_sampling(self):
        """Set up log sampling for high-volume loggers"""
        import random
        
        class SamplingFilter(logging.Filter):
            def __init__(self, rate: float):
                super().__init__()
                self.rate = rate
            
            def filter(self, record):
                return random.random() < self.rate
        
        # Apply sampling to high-volume loggers
        high_volume_loggers = ["uvicorn.access", "sqlalchemy.engine"]
        for logger_name in high_volume_loggers:
            logger = logging.getLogger(logger_name)
            logger.addFilter(SamplingFilter(self.sampling_rate))
    
    def get_logger(self, name: str) -> logging.Logger:
        """Get configured logger instance"""
        if not self.enabled:
            return logging.getLogger(name)
        
        logger = logging.getLogger(name)
        
        # Apply structured logging context if enabled
        if self.structured.enabled:
            # Add structured logging adapter
            from ia_influencer_agent.utils.logging import StructuredLoggerAdapter
            return StructuredLoggerAdapter(logger, self.structured)
        
        return logger
    
    def create_request_logger(self, request_id: str, user_id: Optional[str] = None) -> logging.Logger:
        """Create logger with request context"""
        logger = self.get_logger("ia_influencer_agent.request")
        
        if self.structured.enabled:
            extra = {"request_id": request_id}
            if user_id:
                extra["user_id"] = user_id
            
            from ia_influencer_agent.utils.logging import StructuredLoggerAdapter
            return StructuredLoggerAdapter(logger, self.structured, extra)
        
        return logger
