"""
🎯 Logging Microservice
Distributed logging and monitoring service with structured logging, log aggregation, and real-time analysis.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import json
import time
import logging
import sys
from typing import Dict, List, Any, Optional, Callable, Union
from dataclasses import dataclass, field, asdict
from enum import Enum
from abc import ABC, abstractmethod
import traceback
from datetime import datetime, timedelta
from pathlib import Path
import threading
import queue
from concurrent.futures import ThreadPoolExecutor
import structlog
from pydantic import BaseModel, Field

# Configure structlog
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.processors.JSONRenderer()
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger(__name__)


class LogLevel(str, Enum):
    """Log levels"""
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class LogFormat(str, Enum):
    """Log formats"""
    JSON = "json"
    TEXT = "text"
    STRUCTURED = "structured"
    ELK = "elk"
    SYSLOG = "syslog"


class LogDestination(str, Enum):
    """Log destinations"""
    CONSOLE = "console"
    FILE = "file"
    ELASTICSEARCH = "elasticsearch"
    LOGSTASH = "logstash"
    KAFKA = "kafka"
    REDIS = "redis"
    DATABASE = "database"
    WEBHOOK = "webhook"
    S3 = "s3"


@dataclass
class LogEntry:
    """Structured log entry"""
    timestamp: datetime
    level: LogLevel
    message: str
    service_name: str
    service_version: str = "1.0.0"
    correlation_id: Optional[str] = None
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    request_id: Optional[str] = None
    trace_id: Optional[str] = None
    span_id: Optional[str] = None
    hostname: Optional[str] = None
    process_id: Optional[int] = None
    thread_id: Optional[int] = None
    module: Optional[str] = None
    function: Optional[str] = None
    line_number: Optional[int] = None
    exception_type: Optional[str] = None
    exception_message: Optional[str] = None
    stack_trace: Optional[str] = None
    extra_fields: Dict[str, Any] = field(default_factory=dict)
    tags: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        data = asdict(self)
        data['timestamp'] = self.timestamp.isoformat()
        data['level'] = self.level.value
        return data
        
    def to_json(self) -> str:
        """Convert to JSON string"""
        return json.dumps(self.to_dict(), default=str)


@dataclass
class LoggerConfiguration:
    """Logger configuration"""
    name: str
    level: LogLevel = LogLevel.INFO
    format: LogFormat = LogFormat.JSON
    destinations: List[LogDestination] = field(default_factory=lambda: [LogDestination.CONSOLE])
    file_path: Optional[str] = None
    max_file_size: int = 10 * 1024 * 1024  # 10MB
    backup_count: int = 5
    elasticsearch_url: Optional[str] = None
    elasticsearch_index: Optional[str] = None
    kafka_brokers: List[str] = field(default_factory=list)
    kafka_topic: Optional[str] = None
    redis_url: Optional[str] = None
    webhook_url: Optional[str] = None
    include_fields: List[str] = field(default_factory=list)
    exclude_fields: List[str] = field(default_factory=list)
    filters: List[Dict[str, Any]] = field(default_factory=list)
    sampling_rate: float = 1.0  # 1.0 = log everything, 0.5 = log 50%
    buffer_size: int = 1000
    flush_interval: int = 5  # seconds


class LogFilter:
    """Log filtering"""
    
    @staticmethod
    def apply_filters(log_entry: LogEntry, filters: List[Dict[str, Any]]) -> bool:
        """Apply filters to log entry"""
        for filter_config in filters:
            if not LogFilter._apply_single_filter(log_entry, filter_config):
                return False
        return True
        
    @staticmethod
    def _apply_single_filter(log_entry: LogEntry, filter_config: Dict[str, Any]) -> bool:
        """Apply single filter"""
        filter_type = filter_config.get('type', 'include')
        field = filter_config.get('field')
        value = filter_config.get('value')
        operator = filter_config.get('operator', 'equals')
        
        if not field:
            return True
            
        log_value = getattr(log_entry, field, None)
        if log_value is None and field in log_entry.extra_fields:
            log_value = log_entry.extra_fields[field]
            
        # Apply operator
        result = False
        if operator == 'equals':
            result = log_value == value
        elif operator == 'not_equals':
            result = log_value != value
        elif operator == 'contains':
            result = value in str(log_value) if log_value else False
        elif operator == 'starts_with':
            result = str(log_value).startswith(str(value)) if log_value else False
        elif operator == 'ends_with':
            result = str(log_value).endswith(str(value)) if log_value else False
        elif operator == 'regex':
            import re
            result = bool(re.search(value, str(log_value))) if log_value else False
        elif operator == 'greater_than':
            result = log_value > value if log_value else False
        elif operator == 'less_than':
            result = log_value < value if log_value else False
            
        # Return based on filter type
        if filter_type == 'include':
            return result
        else:  # exclude
            return not result


class LogDestinationHandler(ABC):
    """Abstract log destination handler"""
    
    @abstractmethod
    async def send_logs(self, logs: List[LogEntry]) -> bool:
        """Send logs to destination"""
        pass
        
    @abstractmethod
    async def close(self):
        """Close connection"""
        pass


class ConsoleLogHandler(LogDestinationHandler):
    """Console log handler"""
    
    def __init__(self, format: LogFormat = LogFormat.JSON):
        self.format = format
        
    async def send_logs(self, logs: List[LogEntry]) -> bool:
        """Send logs to console"""
        try:
            for log_entry in logs:
                if self.format == LogFormat.JSON:
                    print(log_entry.to_json())
                else:
                    formatted_msg = f"{log_entry.timestamp.isoformat()} [{log_entry.level.value}] {log_entry.service_name}: {log_entry.message}"
                    print(formatted_msg)
            return True
        except Exception as e:
            print(f"Error sending logs to console: {str(e)}", file=sys.stderr)
            return False
            
    async def close(self):
        """Close console handler"""
        pass


class FileLogHandler(LogDestinationHandler):
    """File log handler with rotation"""
    
    def __init__(self, file_path: str, max_size: int = 10*1024*1024, backup_count: int = 5, format: LogFormat = LogFormat.JSON):
        self.file_path = Path(file_path)
        self.max_size = max_size
        self.backup_count = backup_count
        self.format = format
        self.current_size = 0
        self._ensure_directory()
        
    def _ensure_directory(self):
        """Ensure log directory exists"""
        self.file_path.parent.mkdir(parents=True, exist_ok=True)
        
    async def send_logs(self, logs: List[LogEntry]) -> bool:
        """Send logs to file"""
        try:
            # Check if rotation is needed
            if self.file_path.exists():
                self.current_size = self.file_path.stat().st_size
                if self.current_size >= self.max_size:
                    self._rotate_file()
                    
            # Write logs
            with open(self.file_path, 'a', encoding='utf-8') as f:
                for log_entry in logs:
                    if self.format == LogFormat.JSON:
                        line = log_entry.to_json() + '\n'
                    else:
                        line = f"{log_entry.timestamp.isoformat()} [{log_entry.level.value}] {log_entry.service_name}: {log_entry.message}\n"
                    f.write(line)
                    self.current_size += len(line.encode('utf-8'))
                    
            return True
            
        except Exception as e:
            logger.error(f"Error sending logs to file: {str(e)}")
            return False
            
    def _rotate_file(self):
        """Rotate log file"""
        try:
            # Remove oldest backup
            oldest_backup = self.file_path.with_suffix(f".{self.backup_count}")
            if oldest_backup.exists():
                oldest_backup.unlink()
                
            # Rename existing backups
            for i in range(self.backup_count - 1, 0, -1):
                old_backup = self.file_path.with_suffix(f".{i}")
                new_backup = self.file_path.with_suffix(f".{i + 1}")
                if old_backup.exists():
                    old_backup.rename(new_backup)
                    
            # Rename current file to .1
            if self.file_path.exists():
                backup_file = self.file_path.with_suffix(".1")
                self.file_path.rename(backup_file)
                
            self.current_size = 0
            
        except Exception as e:
            logger.error(f"Error rotating log file: {str(e)}")
            
    async def close(self):
        """Close file handler"""
        pass


class ElasticsearchLogHandler(LogDestinationHandler):
    """Elasticsearch log handler"""
    
    def __init__(self, elasticsearch_url: str, index: str = "ainflue-logs"):
        self.elasticsearch_url = elasticsearch_url
        self.index = index
        self.client = None
        
    async def _ensure_client(self):
        """Ensure Elasticsearch client is initialized"""
        if self.client is None:
            try:
                from elasticsearch import AsyncElasticsearch
                self.client = AsyncElasticsearch([self.elasticsearch_url])
            except ImportError:
                logger.error("elasticsearch library not available")
                raise
                
    async def send_logs(self, logs: List[LogEntry]) -> bool:
        """Send logs to Elasticsearch"""
        try:
            await self._ensure_client()
            
            # Prepare bulk operations
            operations = []
            for log_entry in logs:
                # Index operation
                operations.append({
                    "index": {
                        "_index": f"{self.index}-{log_entry.timestamp.strftime('%Y.%m.%d')}",
                        "_type": "_doc"
                    }
                })
                # Document
                operations.append(log_entry.to_dict())
                
            # Bulk insert
            response = await self.client.bulk(body=operations)
            
            # Check for errors
            if response.get('errors'):
                logger.error(f"Elasticsearch bulk insert errors: {response['errors']}")
                return False
                
            return True
            
        except Exception as e:
            logger.error(f"Error sending logs to Elasticsearch: {str(e)}")
            return False
            
    async def close(self):
        """Close Elasticsearch client"""
        if self.client:
            await self.client.close()


class KafkaLogHandler(LogDestinationHandler):
    """Kafka log handler"""
    
    def __init__(self, brokers: List[str], topic: str = "ainflue-logs"):
        self.brokers = brokers
        self.topic = topic
        self.producer = None
        
    async def _ensure_producer(self):
        """Ensure Kafka producer is initialized"""
        if self.producer is None:
            try:
                from aiokafka import AIOKafkaProducer
                self.producer = AIOKafkaProducer(
                    bootstrap_servers=self.brokers,
                    value_serializer=lambda x: json.dumps(x).encode('utf-8')
                )
                await self.producer.start()
            except ImportError:
                logger.error("aiokafka library not available")
                raise
                
    async def send_logs(self, logs: List[LogEntry]) -> bool:
        """Send logs to Kafka"""
        try:
            await self._ensure_producer()
            
            for log_entry in logs:
                await self.producer.send(self.topic, log_entry.to_dict())
                
            return True
            
        except Exception as e:
            logger.error(f"Error sending logs to Kafka: {str(e)}")
            return False
            
    async def close(self):
        """Close Kafka producer"""
        if self.producer:
            await self.producer.stop()


class LogBuffer:
    """Log buffer for batching"""
    
    def __init__(self, max_size: int = 1000, flush_interval: int = 5):
        self.max_size = max_size
        self.flush_interval = flush_interval
        self.buffer: List[LogEntry] = []
        self.last_flush = time.time()
        self._lock = threading.Lock()
        
    def add_log(self, log_entry: LogEntry) -> bool:
        """Add log to buffer, returns True if buffer should be flushed"""
        with self._lock:
            self.buffer.append(log_entry)
            
            # Check if buffer should be flushed
            should_flush = (
                len(self.buffer) >= self.max_size or
                time.time() - self.last_flush >= self.flush_interval
            )
            
            return should_flush
            
    def get_and_clear_buffer(self) -> List[LogEntry]:
        """Get buffer contents and clear it"""
        with self._lock:
            logs = self.buffer.copy()
            self.buffer.clear()
            self.last_flush = time.time()
            return logs
            
    def is_empty(self) -> bool:
        """Check if buffer is empty"""
        with self._lock:
            return len(self.buffer) == 0


class DistributedLogger:
    """Distributed logger with multiple destinations"""
    
    def __init__(self, config: LoggerConfiguration):
        self.config = config
        self.handlers: List[LogDestinationHandler] = []
        self.buffer = LogBuffer(config.buffer_size, config.flush_interval)
        self.executor = ThreadPoolExecutor(max_workers=2)
        self.running = False
        self.flush_task = None
        
        self._setup_handlers()
        
    def _setup_handlers(self):
        """Setup log destination handlers"""
        for destination in self.config.destinations:
            handler = None
            
            if destination == LogDestination.CONSOLE:
                handler = ConsoleLogHandler(self.config.format)
                
            elif destination == LogDestination.FILE and self.config.file_path:
                handler = FileLogHandler(
                    self.config.file_path,
                    self.config.max_file_size,
                    self.config.backup_count,
                    self.config.format
                )
                
            elif destination == LogDestination.ELASTICSEARCH and self.config.elasticsearch_url:
                handler = ElasticsearchLogHandler(
                    self.config.elasticsearch_url,
                    self.config.elasticsearch_index or f"ainflue-{self.config.name}"
                )
                
            elif destination == LogDestination.KAFKA and self.config.kafka_brokers:
                handler = KafkaLogHandler(
                    self.config.kafka_brokers,
                    self.config.kafka_topic or f"ainflue-{self.config.name}"
                )
                
            if handler:
                self.handlers.append(handler)
                
    async def start(self):
        """Start the logger"""
        if not self.running:
            self.running = True
            self.flush_task = asyncio.create_task(self._flush_periodically())
            
    async def stop(self):
        """Stop the logger"""
        self.running = False
        
        if self.flush_task:
            self.flush_task.cancel()
            try:
                await self.flush_task
            except asyncio.CancelledError:
                pass
                
        # Flush remaining logs
        await self._flush_buffer()
        
        # Close handlers
        for handler in self.handlers:
            await handler.close()
            
    def log(self, level: LogLevel, message: str, **kwargs):
        """Log a message"""
        # Check sampling rate
        if self.config.sampling_rate < 1.0:
            import random
            if random.random() > self.config.sampling_rate:
                return
                
        # Create log entry
        log_entry = self._create_log_entry(level, message, **kwargs)
        
        # Apply filters
        if not LogFilter.apply_filters(log_entry, self.config.filters):
            return
            
        # Add to buffer
        should_flush = self.buffer.add_log(log_entry)
        
        # Flush if needed
        if should_flush and self.running:
            asyncio.create_task(self._flush_buffer())
            
    def _create_log_entry(self, level: LogLevel, message: str, **kwargs) -> LogEntry:
        """Create log entry"""
        import socket
        import os
        import threading
        
        # Get caller information
        frame = sys._getframe(2)  # Skip this method and log method
        
        log_entry = LogEntry(
            timestamp=datetime.utcnow(),
            level=level,
            message=message,
            service_name=self.config.name,
            hostname=socket.gethostname(),
            process_id=os.getpid(),
            thread_id=threading.get_ident(),
            module=frame.f_globals.get('__name__'),
            function=frame.f_code.co_name,
            line_number=frame.f_lineno,
            **kwargs
        )
        
        # Handle exception information
        if level in [LogLevel.ERROR, LogLevel.CRITICAL]:
            exc_info = sys.exc_info()
            if exc_info[0] is not None:
                log_entry.exception_type = exc_info[0].__name__
                log_entry.exception_message = str(exc_info[1])
                log_entry.stack_trace = ''.join(traceback.format_exception(*exc_info))
                
        return log_entry
        
    async def _flush_buffer(self):
        """Flush log buffer"""
        try:
            logs = self.buffer.get_and_clear_buffer()
            if not logs:
                return
                
            # Send to all handlers
            for handler in self.handlers:
                try:
                    await handler.send_logs(logs)
                except Exception as e:
                    # Log to stderr to avoid infinite loop
                    print(f"Error in log handler {type(handler).__name__}: {str(e)}", file=sys.stderr)
                    
        except Exception as e:
            print(f"Error flushing log buffer: {str(e)}", file=sys.stderr)
            
    async def _flush_periodically(self):
        """Periodically flush buffer"""
        while self.running:
            try:
                await asyncio.sleep(self.config.flush_interval)
                if not self.buffer.is_empty():
                    await self._flush_buffer()
            except asyncio.CancelledError:
                break
            except Exception as e:
                print(f"Error in periodic flush: {str(e)}", file=sys.stderr)


class LoggingService:
    """Distributed Logging Service"""
    
    def __init__(self, name: str = "logging_service"):
        self.name = name
        self.loggers: Dict[str, DistributedLogger] = {}
        self.default_config = LoggerConfiguration(
            name="default",
            level=LogLevel.INFO,
            destinations=[LogDestination.CONSOLE, LogDestination.FILE],
            file_path="logs/ainflue.log"
        )
        self.running = False
        
    async def start(self):
        """Start logging service"""
        self.running = True
        
        # Start all loggers
        for logger in self.loggers.values():
            await logger.start()
            
        logger.info(f"Started logging service: {self.name}")
        
    async def stop(self):
        """Stop logging service"""
        self.running = False
        
        # Stop all loggers
        for logger in self.loggers.values():
            await logger.stop()
            
        logger.info(f"Stopped logging service: {self.name}")
        
    def create_logger(self, config: LoggerConfiguration) -> DistributedLogger:
        """Create a new logger"""
        if config.name in self.loggers:
            return self.loggers[config.name]
            
        distributed_logger = DistributedLogger(config)
        self.loggers[config.name] = distributed_logger
        
        if self.running:
            asyncio.create_task(distributed_logger.start())
            
        logger.info(f"Created logger: {config.name}")
        return distributed_logger
        
    def get_logger(self, name: str = "default") -> DistributedLogger:
        """Get logger by name"""
        if name not in self.loggers:
            # Create default logger if it doesn't exist
            config = LoggerConfiguration(
                name=name,
                level=self.default_config.level,
                format=self.default_config.format,
                destinations=self.default_config.destinations,
                file_path=f"logs/{name}.log" if self.default_config.file_path else None
            )
            return self.create_logger(config)
            
        return self.loggers[name]
        
    def remove_logger(self, name: str):
        """Remove logger"""
        if name in self.loggers:
            logger_instance = self.loggers[name]
            asyncio.create_task(logger_instance.stop())
            del self.loggers[name]
            logger.info(f"Removed logger: {name}")
            
    def configure_logger(self, name: str, config: LoggerConfiguration):
        """Configure or reconfigure logger"""
        if name in self.loggers:
            # Stop existing logger
            asyncio.create_task(self.loggers[name].stop())
            
        # Create new logger with new config
        self.create_logger(config)
        
    def set_global_level(self, level: LogLevel):
        """Set global log level for all loggers"""
        for logger_instance in self.loggers.values():
            logger_instance.config.level = level
            
    def get_status(self) -> Dict[str, Any]:
        """Get service status"""
        return {
            "name": self.name,
            "status": "running" if self.running else "stopped",
            "loggers_count": len(self.loggers),
            "loggers": {
                name: {
                    "level": logger.config.level.value,
                    "destinations": [dest.value for dest in logger.config.destinations],
                    "buffer_size": len(logger.buffer.buffer),
                    "handlers_count": len(logger.handlers)
                }
                for name, logger in self.loggers.items()
            },
            "timestamp": datetime.utcnow().isoformat()
        }


def create_logging_service(config: Dict[str, Any] = None) -> LoggingService:
    """Factory function to create Logging service"""
    config = config or {}
    service_name = config.get('name', 'logging_service')
    
    service = LoggingService(service_name)
    
    # Configure default logger
    if 'default_logger' in config:
        default_config = config['default_logger']
        service.default_config = LoggerConfiguration(
            name=default_config.get('name', 'default'),
            level=LogLevel(default_config.get('level', 'INFO')),
            format=LogFormat(default_config.get('format', 'JSON')),
            destinations=[LogDestination(dest) for dest in default_config.get('destinations', ['console'])],
            file_path=default_config.get('file_path'),
            max_file_size=default_config.get('max_file_size', 10*1024*1024),
            backup_count=default_config.get('backup_count', 5),
            elasticsearch_url=default_config.get('elasticsearch_url'),
            elasticsearch_index=default_config.get('elasticsearch_index'),
            kafka_brokers=default_config.get('kafka_brokers', []),
            kafka_topic=default_config.get('kafka_topic'),
            buffer_size=default_config.get('buffer_size', 1000),
            flush_interval=default_config.get('flush_interval', 5)
        )
        
    # Create additional loggers
    if 'loggers' in config:
        for logger_config in config['loggers']:
            logger_configuration = LoggerConfiguration(
                name=logger_config.get('name', 'custom'),
                level=LogLevel(logger_config.get('level', 'INFO')),
                format=LogFormat(logger_config.get('format', 'JSON')),
                destinations=[LogDestination(dest) for dest in logger_config.get('destinations', ['console'])],
                file_path=logger_config.get('file_path'),
                max_file_size=logger_config.get('max_file_size', 10*1024*1024),
                backup_count=logger_config.get('backup_count', 5),
                elasticsearch_url=logger_config.get('elasticsearch_url'),
                elasticsearch_index=logger_config.get('elasticsearch_index'),
                kafka_brokers=logger_config.get('kafka_brokers', []),
                kafka_topic=logger_config.get('kafka_topic'),
                buffer_size=logger_config.get('buffer_size', 1000),
                flush_interval=logger_config.get('flush_interval', 5),
                filters=logger_config.get('filters', []),
                sampling_rate=logger_config.get('sampling_rate', 1.0)
            )
            service.create_logger(logger_configuration)
            
    return service


__all__ = [
    'LoggingService', 'DistributedLogger', 'LogEntry', 'LoggerConfiguration',
    'LogLevel', 'LogFormat', 'LogDestination',
    'ConsoleLogHandler', 'FileLogHandler', 'ElasticsearchLogHandler', 'KafkaLogHandler',
    'create_logging_service'
]