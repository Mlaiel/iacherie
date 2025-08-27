"""
Logging Aggregation Configuration Module for IA-Influencer Agent Platform
==========================================================================

Professional centralized logging configuration with structured logging,
log aggregation, and advanced filtering for comprehensive observability.

Author: Fahed Mlaiel <mlaiel@live.de>
Project: IA-Influencer Agent + Content Protection Platform
Team: Lead Dev IA + Backend Senior + ML Engineer + DBA + Security + Microservices + Audio + DevOps

Copyright Notice:
This code is the intellectual property of Fahed Mlaiel.
Any unauthorized use, reproduction, or distribution of this code
without explicit written permission from the author is strictly prohibited.

Contact: mlaiel@live.de for licensing inquiries.
"""

import os
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from enum import Enum
import json


class LogLevel(Enum):
    """Log levels"""
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class LogFormat(Enum):
    """Log output formats"""
    JSON = "json"
    TEXT = "text"
    LOGFMT = "logfmt"


class LogDestination(Enum):
    """Log destinations"""
    CONSOLE = "console"
    FILE = "file"
    ELASTICSEARCH = "elasticsearch"
    FLUENTD = "fluentd"
    SYSLOG = "syslog"
    KAFKA = "kafka"


@dataclass
class LoggerConfig:
    """Individual logger configuration"""
    name: str
    level: LogLevel
    handlers: List[str] = field(default_factory=list)
    propagate: bool = True
    filters: List[str] = field(default_factory=list)


@dataclass
class HandlerConfig:
    """Log handler configuration"""
    name: str
    handler_type: str
    level: LogLevel
    formatter: str
    destination: LogDestination
    config: Dict[str, Any] = field(default_factory=dict)


@dataclass
class FormatterConfig:
    """Log formatter configuration"""
    name: str
    format_type: LogFormat
    format_string: Optional[str] = None
    date_format: Optional[str] = None
    include_extra: bool = True


class LoggingAggregationConfig:
    """Professional logging aggregation configuration for IA-Influencer platform"""
    
    def __init__(self):
        self.log_level = LogLevel(os.getenv("LOG_LEVEL", "INFO"))
        self.log_format = LogFormat(os.getenv("LOG_FORMAT", "json"))
        self.elasticsearch_host = os.getenv("ELASTICSEARCH_HOST", "elasticsearch")
        self.elasticsearch_port = int(os.getenv("ELASTICSEARCH_PORT", "9200"))
        self.elasticsearch_index_prefix = os.getenv("ELASTICSEARCH_INDEX_PREFIX", "ia-influencer")
        self.fluentd_host = os.getenv("FLUENTD_HOST", "fluentd")
        self.fluentd_port = int(os.getenv("FLUENTD_PORT", "24224"))
        self.kafka_bootstrap_servers = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "kafka:9092")
        self.kafka_topic = os.getenv("KAFKA_LOG_TOPIC", "ia-influencer-logs")
        self.log_retention_days = int(os.getenv("LOG_RETENTION_DAYS", "30"))
        self.max_log_file_size = os.getenv("MAX_LOG_FILE_SIZE", "100MB")
        self.backup_count = int(os.getenv("LOG_BACKUP_COUNT", "10"))
        self.service_name = os.getenv("SERVICE_NAME", "ia-influencer-agent")
        self.environment = os.getenv("ENVIRONMENT", "production")
    
    def get_formatters(self) -> Dict[str, FormatterConfig]:
        """Get log formatter configurations"""
        return {
            "json": FormatterConfig(
                name="json",
                format_type=LogFormat.JSON,
                include_extra=True
            ),
            "detailed": FormatterConfig(
                name="detailed",
                format_type=LogFormat.TEXT,
                format_string="%(asctime)s - %(name)s - %(levelname)s - %(message)s - [%(filename)s:%(lineno)d] - [trace_id=%(trace_id)s span_id=%(span_id)s]",
                date_format="%Y-%m-%d %H:%M:%S"
            ),
            "simple": FormatterConfig(
                name="simple",
                format_type=LogFormat.TEXT,
                format_string="%(levelname)s - %(name)s - %(message)s",
                date_format="%H:%M:%S"
            ),
            "security": FormatterConfig(
                name="security",
                format_type=LogFormat.JSON,
                include_extra=True
            ),
            "audit": FormatterConfig(
                name="audit",
                format_type=LogFormat.JSON,
                include_extra=True
            )
        }
    
    def get_handlers(self) -> Dict[str, HandlerConfig]:
        """Get log handler configurations"""
        handlers = {}
        
        # Console handler
        handlers["console"] = HandlerConfig(
            name="console",
            handler_type="StreamHandler",
            level=self.log_level,
            formatter="json" if self.log_format == LogFormat.JSON else "detailed",
            destination=LogDestination.CONSOLE,
            config={"stream": "sys.stdout"}
        )
        
        # File handlers
        handlers["app_file"] = HandlerConfig(
            name="app_file",
            handler_type="RotatingFileHandler",
            level=LogLevel.INFO,
            formatter="json",
            destination=LogDestination.FILE,
            config={
                "filename": f"/var/log/{self.service_name}/app.log",
                "maxBytes": self._parse_file_size(self.max_log_file_size),
                "backupCount": self.backup_count,
                "encoding": "utf-8"
            }
        )
        
        handlers["error_file"] = HandlerConfig(
            name="error_file",
            handler_type="RotatingFileHandler",
            level=LogLevel.ERROR,
            formatter="json",
            destination=LogDestination.FILE,
            config={
                "filename": f"/var/log/{self.service_name}/error.log",
                "maxBytes": self._parse_file_size(self.max_log_file_size),
                "backupCount": self.backup_count,
                "encoding": "utf-8"
            }
        )
        
        handlers["security_file"] = HandlerConfig(
            name="security_file",
            handler_type="RotatingFileHandler",
            level=LogLevel.WARNING,
            formatter="security",
            destination=LogDestination.FILE,
            config={
                "filename": f"/var/log/{self.service_name}/security.log",
                "maxBytes": self._parse_file_size(self.max_log_file_size),
                "backupCount": self.backup_count * 2,  # Keep security logs longer
                "encoding": "utf-8"
            }
        )
        
        handlers["audit_file"] = HandlerConfig(
            name="audit_file",
            handler_type="RotatingFileHandler",
            level=LogLevel.INFO,
            formatter="audit",
            destination=LogDestination.FILE,
            config={
                "filename": f"/var/log/{self.service_name}/audit.log",
                "maxBytes": self._parse_file_size(self.max_log_file_size),
                "backupCount": self.backup_count * 3,  # Keep audit logs longer
                "encoding": "utf-8"
            }
        )
        
        # Elasticsearch handler
        if self.elasticsearch_host:
            handlers["elasticsearch"] = HandlerConfig(
                name="elasticsearch",
                handler_type="ElasticsearchHandler",
                level=LogLevel.INFO,
                formatter="json",
                destination=LogDestination.ELASTICSEARCH,
                config={
                    "hosts": [f"{self.elasticsearch_host}:{self.elasticsearch_port}"],
                    "index_name": f"{self.elasticsearch_index_prefix}-logs",
                    "doc_type": "_doc",
                    "timeout": 60,
                    "max_retries": 3,
                    "retry_on_timeout": True,
                    "buffer_size": 1000,
                    "flush_frequency_in_sec": 5
                }
            )
        
        # Fluentd handler
        if self.fluentd_host:
            handlers["fluentd"] = HandlerConfig(
                name="fluentd",
                handler_type="FluentdHandler",
                level=LogLevel.INFO,
                formatter="json",
                destination=LogDestination.FLUENTD,
                config={
                    "host": self.fluentd_host,
                    "port": self.fluentd_port,
                    "tag": f"{self.service_name}.logs",
                    "timeout": 3.0,
                    "verbose": False
                }
            )
        
        # Kafka handler
        if self.kafka_bootstrap_servers:
            handlers["kafka"] = HandlerConfig(
                name="kafka",
                handler_type="KafkaHandler",
                level=LogLevel.INFO,
                formatter="json",
                destination=LogDestination.KAFKA,
                config={
                    "bootstrap_servers": self.kafka_bootstrap_servers.split(","),
                    "topic": self.kafka_topic,
                    "key": self.service_name,
                    "partition": None,
                    "producer_config": {
                        "acks": "1",
                        "retries": 3,
                        "batch_size": 16384,
                        "linger_ms": 5
                    }
                }
            )
        
        return handlers
    
    def get_loggers(self) -> Dict[str, LoggerConfig]:
        """Get logger configurations"""
        return {
            "root": LoggerConfig(
                name="root",
                level=self.log_level,
                handlers=["console", "app_file", "error_file"]
            ),
            "ia_influencer": LoggerConfig(
                name="ia_influencer",
                level=LogLevel.DEBUG,
                handlers=["console", "app_file", "elasticsearch"],
                propagate=False
            ),
            "ia_influencer.security": LoggerConfig(
                name="ia_influencer.security",
                level=LogLevel.INFO,
                handlers=["console", "security_file", "elasticsearch"],
                propagate=False
            ),
            "ia_influencer.audit": LoggerConfig(
                name="ia_influencer.audit",
                level=LogLevel.INFO,
                handlers=["audit_file", "elasticsearch"],
                propagate=False
            ),
            "ia_influencer.ai": LoggerConfig(
                name="ia_influencer.ai",
                level=LogLevel.INFO,
                handlers=["console", "app_file", "elasticsearch"]
            ),
            "ia_influencer.protection": LoggerConfig(
                name="ia_influencer.protection",
                level=LogLevel.INFO,
                handlers=["console", "app_file", "elasticsearch"]
            ),
            "ia_influencer.audio": LoggerConfig(
                name="ia_influencer.audio",
                level=LogLevel.INFO,
                handlers=["console", "app_file", "elasticsearch"]
            ),
            "ia_influencer.monetization": LoggerConfig(
                name="ia_influencer.monetization",
                level=LogLevel.INFO,
                handlers=["console", "app_file", "elasticsearch"]
            ),
            "uvicorn": LoggerConfig(
                name="uvicorn",
                level=LogLevel.INFO,
                handlers=["console", "app_file"]
            ),
            "fastapi": LoggerConfig(
                name="fastapi",
                level=LogLevel.INFO,
                handlers=["console", "app_file"]
            ),
            "sqlalchemy": LoggerConfig(
                name="sqlalchemy",
                level=LogLevel.WARNING,
                handlers=["console", "app_file"]
            ),
            "celery": LoggerConfig(
                name="celery",
                level=LogLevel.INFO,
                handlers=["console", "app_file"]
            )
        }
    
    def get_log_filters(self) -> Dict[str, Dict[str, Any]]:
        """Get log filtering configuration"""
        return {
            "security_filter": {
                "type": "SecurityLogFilter",
                "config": {
                    "sensitive_fields": [
                        "password", "token", "secret", "key", "auth",
                        "credential", "session", "cookie"
                    ],
                    "mask_value": "[REDACTED]",
                    "ip_anonymization": True
                }
            },
            "performance_filter": {
                "type": "PerformanceLogFilter",
                "config": {
                    "slow_query_threshold": 1.0,
                    "memory_usage_threshold": 80.0,
                    "include_stack_trace": True
                }
            },
            "business_filter": {
                "type": "BusinessEventFilter",
                "config": {
                    "track_user_actions": True,
                    "track_revenue_events": True,
                    "track_content_events": True
                }
            },
            "debug_filter": {
                "type": "DebugModeFilter",
                "config": {
                    "enabled_in_production": False,
                    "max_debug_logs_per_minute": 100
                }
            }
        }
    
    def get_structured_logging_config(self) -> Dict[str, Any]:
        """Get structured logging configuration"""
        return {
            "default_fields": {
                "service": self.service_name,
                "environment": self.environment,
                "version": os.getenv("SERVICE_VERSION", "1.0.0"),
                "hostname": os.getenv("HOSTNAME", "unknown"),
                "pid": os.getpid()
            },
            "context_fields": {
                "request_id": "x-request-id",
                "correlation_id": "x-correlation-id",
                "user_id": "x-user-id",
                "tenant_id": "x-tenant-id",
                "session_id": "x-session-id"
            },
            "trace_fields": {
                "trace_id": "trace_id",
                "span_id": "span_id",
                "parent_span_id": "parent_span_id"
            },
            "business_fields": {
                "user_id": "user.id",
                "user_role": "user.role",
                "content_type": "content.type",
                "platform": "platform.name",
                "revenue_amount": "revenue.amount"
            }
        }
    
    def get_log_sampling_config(self) -> Dict[str, Any]:
        """Get log sampling configuration for high-volume scenarios"""
        return {
            "enabled": True,
            "default_sample_rate": 1.0,
            "level_based_sampling": {
                "DEBUG": 0.1,
                "INFO": 0.5,
                "WARNING": 1.0,
                "ERROR": 1.0,
                "CRITICAL": 1.0
            },
            "service_based_sampling": {
                "ai_inference": 0.3,
                "audio_processing": 0.2,
                "content_upload": 0.8,
                "security_events": 1.0
            },
            "adaptive_sampling": {
                "enabled": True,
                "target_logs_per_second": 1000,
                "adjustment_interval": 60,
                "min_sample_rate": 0.01,
                "max_sample_rate": 1.0
            }
        }
    
    def get_elasticsearch_mapping(self) -> Dict[str, Any]:
        """Get Elasticsearch index mapping for logs"""
        return {
            "mappings": {
                "properties": {
                    "@timestamp": {"type": "date"},
                    "level": {"type": "keyword"},
                    "message": {"type": "text", "analyzer": "standard"},
                    "logger": {"type": "keyword"},
                    "service": {"type": "keyword"},
                    "environment": {"type": "keyword"},
                    "version": {"type": "keyword"},
                    "hostname": {"type": "keyword"},
                    "pid": {"type": "integer"},
                    "thread": {"type": "keyword"},
                    "request_id": {"type": "keyword"},
                    "correlation_id": {"type": "keyword"},
                    "user_id": {"type": "keyword"},
                    "session_id": {"type": "keyword"},
                    "trace_id": {"type": "keyword"},
                    "span_id": {"type": "keyword"},
                    "duration": {"type": "float"},
                    "status_code": {"type": "integer"},
                    "method": {"type": "keyword"},
                    "endpoint": {"type": "keyword"},
                    "user_agent": {"type": "text"},
                    "ip_address": {"type": "ip"},
                    "content_type": {"type": "keyword"},
                    "platform": {"type": "keyword"},
                    "revenue_amount": {"type": "float"},
                    "error": {
                        "properties": {
                            "type": {"type": "keyword"},
                            "message": {"type": "text"},
                            "stack_trace": {"type": "text"}
                        }
                    },
                    "performance": {
                        "properties": {
                            "cpu_percent": {"type": "float"},
                            "memory_percent": {"type": "float"},
                            "query_time": {"type": "float"}
                        }
                    }
                }
            },
            "settings": {
                "number_of_shards": 3,
                "number_of_replicas": 1,
                "refresh_interval": "5s",
                "index": {
                    "lifecycle": {
                        "name": "logs-policy",
                        "rollover_alias": f"{self.elasticsearch_index_prefix}-logs"
                    }
                }
            }
        }
    
    def get_log_retention_policy(self) -> Dict[str, Any]:
        """Get log retention and archival policy"""
        return {
            "retention_periods": {
                "debug_logs": "7d",
                "info_logs": "30d",
                "warning_logs": "90d",
                "error_logs": "365d",
                "critical_logs": "1095d",  # 3 years
                "security_logs": "2555d",  # 7 years
                "audit_logs": "2555d"     # 7 years
            },
            "archival_config": {
                "enabled": True,
                "cold_storage_after": "30d",
                "archive_storage_after": "365d",
                "compression": "gzip",
                "archive_location": "s3://ia-influencer-logs-archive"
            },
            "cleanup_schedule": {
                "frequency": "daily",
                "time": "02:00",
                "batch_size": 1000
            }
        }
    
    def _parse_file_size(self, size_str: str) -> int:
        """Parse file size string to bytes"""
        size_str = size_str.upper()
        if size_str.endswith('KB'):
            return int(size_str[:-2]) * 1024
        elif size_str.endswith('MB'):
            return int(size_str[:-2]) * 1024 * 1024
        elif size_str.endswith('GB'):
            return int(size_str[:-2]) * 1024 * 1024 * 1024
        else:
            return int(size_str)
    
    def get_complete_logging_config(self) -> Dict[str, Any]:
        """Get complete logging configuration"""
        return {
            "version": 1,
            "disable_existing_loggers": False,
            "formatters": {
                name: {
                    "class": self._get_formatter_class(config.format_type),
                    "format": config.format_string,
                    "datefmt": config.date_format
                }
                for name, config in self.get_formatters().items()
            },
            "handlers": {
                name: {
                    "class": self._get_handler_class(config.handler_type),
                    "level": config.level.value,
                    "formatter": config.formatter,
                    **config.config
                }
                for name, config in self.get_handlers().items()
            },
            "loggers": {
                name: {
                    "level": config.level.value,
                    "handlers": config.handlers,
                    "propagate": config.propagate
                }
                for name, config in self.get_loggers().items()
            },
            "filters": self.get_log_filters(),
            "structured_logging": self.get_structured_logging_config(),
            "sampling": self.get_log_sampling_config(),
            "retention": self.get_log_retention_policy()
        }
    
    def _get_formatter_class(self, format_type: LogFormat) -> str:
        """Get formatter class name"""
        if format_type == LogFormat.JSON:
            return "pythonjsonlogger.jsonlogger.JsonFormatter"
        else:
            return "logging.Formatter"
    
    def _get_handler_class(self, handler_type: str) -> str:
        """Get handler class name"""
        handler_classes = {
            "StreamHandler": "logging.StreamHandler",
            "RotatingFileHandler": "logging.handlers.RotatingFileHandler",
            "TimedRotatingFileHandler": "logging.handlers.TimedRotatingFileHandler",
            "ElasticsearchHandler": "pythonjsonlogger.elasticsearch.ElasticsearchHandler",
            "FluentdHandler": "fluent.handler.FluentHandler",
            "KafkaHandler": "kafka_logger.KafkaLoggingHandler",
            "SysLogHandler": "logging.handlers.SysLogHandler"
        }
        return handler_classes.get(handler_type, "logging.StreamHandler")
