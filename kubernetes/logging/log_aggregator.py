"""IA Influencer Agent - Log Aggregation Service
Advanced log aggregation and centralized logging management

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: All rights reserved - Unauthorized use prohibited

WARNING: This code is the intellectual property of Fahed Mlaiel.
Any unauthorized use, reproduction, or distribution without explicit 
written permission is strictly prohibited and will result in legal action.
Contact: mlaiel@live.de for licensing inquiries.

Team Expertise:
- Lead Developer & AI Architect: Fahed Mlaiel
- Backend Senior Engineer: Advanced Python/FastAPI
- ML Engineer: AI/ML Algorithms & Analytics
- DevOps Engineer: Infrastructure & Deployment
- Database Administrator: Performance & Optimization
- Security Specialist: Enterprise Security & Compliance
- Microservices Architect: Distributed Systems
- IA Prompt Engineer: Advanced AI Integration
"""import asyncio
import json
import logging
import structlog
import socket
import os
import ssl
import gzip
import traceback
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any, Union, Callable, Protocol
from dataclasses import dataclass, asdict
from enum import Enum
from pathlib import Path
from contextlib import asynccontextmanager
import aioredis
from elasticsearch import AsyncElasticsearch
import sentry_sdk
from sentry_sdk.integrations.logging import LoggingIntegration
from urllib.parse import urlparse
import httpx
import boto3
from botocore.exceptions import ClientError
from fluent import asyncsender as fluentd

from ...core.config import settings
from ...core.exceptions import LoggingError, ConfigurationError


class LogLevel(str, Enum):
    """Log levels enumeration for structured logging"""    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class LogFormat(str, Enum):
    """Log output format types"""    JSON = "json"
    STRUCTURED = "structured"
    PLAIN = "plain"
    CONSOLE = "console"
    ECS = "ecs"  # Elastic Common Schema
    GELF = "gelf"  # Graylog Extended Log Format


class LogDestination(str, Enum):
    """Log destination types for multi-target logging"""    CONSOLE = "console"
    FILE = "file"
    ELASTICSEARCH = "elasticsearch"
    REDIS = "redis"
    SENTRY = "sentry"
    S3 = "s3"
    FLUENTD = "fluentd"
    WEBHOOK = "webhook"
    KINESIS = "kinesis"
    CLOUDWATCH = "cloudwatch"


@dataclass
class LogEntry:
    """Structured log entry data class for IA Influencer Agent"""    
    # Core fields
    timestamp: datetime
    level: LogLevel
    message: str
    service: str
    module: str
    
    # Context fields
    trace_id: Optional[str] = None
    span_id: Optional[str] = None
    user_id: Optional[str] = None
    tenant_id: Optional[str] = None
    request_id: Optional[str] = None
    session_id: Optional[str] = None
    
    # Technical fields
    hostname: Optional[str] = None
    environment: Optional[str] = None
    version: Optional[str] = None
    region: Optional[str] = None
    
    # Metadata for AI/ML operations
    metadata: Optional[Dict[str, Any]] = None
    
    # Error context
    error_type: Optional[str] = None
    error_code: Optional[str] = None
    stack_trace: Optional[str] = None
    
    # Performance metrics
    processing_time_ms: Optional[float] = None
    memory_usage_mb: Optional[float] = None
    cpu_usage_percent: Optional[float] = None
    
    # Business context for IA Influencer Agent
    content_type: Optional[str] = None  # audio, video, image, text
    fingerprint_id: Optional[str] = None
    protection_action: Optional[str] = None
    monetization_event: Optional[str] = None
    ai_model_version: Optional[str] = None
    pipeline_stage: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert log entry to dictionary for serialization"""        data = asdict(self)
        
        # Convert datetime to ISO format
        if self.timestamp:
            data['timestamp'] = self.timestamp.isoformat()
        
        # Clean None values
        return {k: v for k, v in data.items() if v is not None}
    
    def to_json(self) -> str:
        """Convert log entry to JSON string"""        return json.dumps(self.to_dict())
    
    def to_ecs_format(self) -> Dict[str, Any]:
        """Convert to Elastic Common Schema format"""        ecs_data = {
            "@timestamp": self.timestamp.isoformat(),
            "log": {
                "level": self.level.value,
                "logger": self.module
            },
            "message": self.message,
            "service": {
                "name": self.service,
                "version": self.version,
                "environment": self.environment
            },
            "host": {
                "hostname": self.hostname
            }
        }
        
        if self.user_id:
            ecs_data["user"] = {"id": self.user_id}
        
        if self.trace_id:
            ecs_data["trace"] = {"id": self.trace_id}
            
        if self.error_type:
            ecs_data["error"] = {
                "type": self.error_type,
                "code": self.error_code,
                "stack_trace": self.stack_trace
            }
            
        if self.metadata:
            ecs_data["metadata"] = self.metadata
            
        return ecs_data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'LogEntry':
        """Create LogEntry from dictionary"""        if 'timestamp' in data and isinstance(data['timestamp'], str):
            data['timestamp'] = datetime.fromisoformat(data['timestamp'])
        
        return cls(**data)


class LogProcessor:
    """Advanced log processor with enrichment and filtering capabilities"""    
    def __init__(self, 
                 service_name: str = "ia-influencer-agent",
                 environment: str = "production",
                 version: str = "1.0.0"):
        self.service_name = service_name
        self.environment = environment
        self.version = version
        self.enrichers: List[Callable[[LogEntry], LogEntry]] = []
        self.filters: List[Callable[[LogEntry], bool]] = []
        
    def add_enricher(self, enricher_func: Callable[[LogEntry], LogEntry]):
        """Add log enricher function"""        self.enrichers.append(enricher_func)
    
    def add_filter(self, filter_func: Callable[[LogEntry], bool]):
        """Add log filter function"""        self.filters.append(filter_func)
    
    def process(self, log_entry: LogEntry) -> Optional[LogEntry]:
        """Process log entry through enrichers and filters"""        try:
            # Apply filters first
            for filter_func in self.filters:
                if not filter_func(log_entry):
                    return None
            
            # Apply enrichers
            for enricher_func in self.enrichers:
                log_entry = enricher_func(log_entry)
            
            # Add default enrichments
            if not log_entry.service:
                log_entry.service = self.service_name
            if not log_entry.environment:
                log_entry.environment = self.environment
            if not log_entry.version:
                log_entry.version = self.version
            if not log_entry.hostname:
                log_entry.hostname = socket.gethostname()
            
            return log_entry
            
        except Exception as e:
            # Don't fail logging due to processing errors
            logging.error(f"Error processing log entry: {e}")
            return log_entry


class LogBuffer:
    """High-performance log buffer with configurable flushing strategies"""    
    def __init__(self, 
                 max_size: int = 1000,
                 flush_interval: float = 30.0,
                 force_flush_level: LogLevel = LogLevel.ERROR):
        self.max_size = max_size
        self.flush_interval = flush_interval
        self.force_flush_level = force_flush_level
        self.buffer: List[LogEntry] = []
        self.last_flush = datetime.now(timezone.utc)
        self._lock = asyncio.Lock()
        
    async def add(self, log_entry: LogEntry) -> bool:
        """Add log entry to buffer, returns True if flush is needed"""        async with self._lock:
            self.buffer.append(log_entry)
            
            # Force flush on critical errors
            if log_entry.level == self.force_flush_level:
                return True
            
            # Flush if buffer is full
            if len(self.buffer) >= self.max_size:
                return True
            
            # Flush if interval exceeded
            now = datetime.now(timezone.utc)
            if (now - self.last_flush).total_seconds() >= self.flush_interval:
                return True
                
            return False
    
    async def flush(self) -> List[LogEntry]:
        """Flush buffer and return all entries"""        async with self._lock:
            entries = self.buffer.copy()
            self.buffer.clear()
            self.last_flush = datetime.now(timezone.utc)
            return entries
    
    async def size(self) -> int:
        """Get current buffer size"""        async with self._lock:
            return len(self.buffer)


class LogWriter(Protocol):
    """Protocol for log writers"""    
    async def write(self, entries: List[LogEntry]) -> bool:
        """Write log entries to destination"""        ...
    
    async def close(self) -> None:
        """Close writer and cleanup resources"""        ...


class ConsoleLogWriter:
    """Console log writer with colored output"""    
    def __init__(self, format_type: LogFormat = LogFormat.JSON):
        self.format_type = format_type
        
        # Color codes for different log levels
        self.colors = {
            LogLevel.DEBUG: "\033[36m",    # Cyan
            LogLevel.INFO: "\033[32m",     # Green
            LogLevel.WARNING: "\033[33m",  # Yellow
            LogLevel.ERROR: "\033[31m",    # Red
            LogLevel.CRITICAL: "\033[35m"  # Magenta
        }
        self.reset_color = "\033[0m"
    
    async def write(self, entries: List[LogEntry]) -> bool:
        """Write entries to console with colors"""        try:
            for entry in entries:
                if self.format_type == LogFormat.JSON:
                    output = entry.to_json()
                elif self.format_type == LogFormat.CONSOLE:
                    color = self.colors.get(entry.level, "")
                    output = f"{color}[{entry.timestamp}] {entry.level} {entry.service}.{entry.module}: {entry.message}{self.reset_color}"
                else:
                    output = f"{entry.timestamp} {entry.level} {entry.service}.{entry.module}: {entry.message}"
                
                print(output)
            return True
        except Exception as e:
            logging.error(f"Console writer error: {e}")
            return False
    
    async def close(self) -> None:
        """Nothing to close for console"""        pass


class FileLogWriter:
    """File log writer with rotation and compression"""    
    def __init__(self, 
                 file_path: str,
                 max_file_size: int = 100 * 1024 * 1024,  # 100MB
                 max_files: int = 10,
                 compress: bool = True,
                 format_type: LogFormat = LogFormat.JSON):
        self.file_path = Path(file_path)
        self.max_file_size = max_file_size
        self.max_files = max_files
        self.compress = compress
        self.format_type = format_type
        self.current_file = None
        self._lock = asyncio.Lock()
        
        # Ensure directory exists
        self.file_path.parent.mkdir(parents=True, exist_ok=True)
    
    async def write(self, entries: List[LogEntry]) -> bool:
        """Write entries to file with rotation"""        async with self._lock:
            try:
                # Check if rotation is needed
                await self._rotate_if_needed()
                
                # Open file if not open
                if not self.current_file:
                    self.current_file = open(self.file_path, 'a', encoding='utf-8')
                
                # Write entries
                for entry in entries:
                    if self.format_type == LogFormat.JSON:
                        line = entry.to_json()
                    else:
                        line = f"{entry.timestamp} {entry.level} {entry.service}.{entry.module}: {entry.message}"
                    
                    self.current_file.write(line + "\n")
                
                self.current_file.flush()
                return True
                
            except Exception as e:
                logging.error(f"File writer error: {e}")
                return False
    
    async def _rotate_if_needed(self):
        """Rotate log file if size exceeds limit"""        if not self.file_path.exists():
            return
        
        if self.file_path.stat().st_size >= self.max_file_size:
            # Close current file
            if self.current_file:
                self.current_file.close()
                self.current_file = None
            
            # Rotate files
            for i in range(self.max_files - 1, 0, -1):
                old_file = self.file_path.with_suffix(f".{i}")
                new_file = self.file_path.with_suffix(f".{i + 1}")
                
                if old_file.exists():
                    if i == self.max_files - 1:
                        old_file.unlink()  # Delete oldest
                    else:
                        old_file.rename(new_file)
            
            # Move current to .1
            rotated_file = self.file_path.with_suffix(".1")
            self.file_path.rename(rotated_file)
            
            # Compress if enabled
            if self.compress:
                await self._compress_file(rotated_file)
    
    async def _compress_file(self, file_path: Path):
        """Compress rotated log file"""        try:
            compressed_path = file_path.with_suffix(file_path.suffix + ".gz")
            
            with open(file_path, 'rb') as f_in:
                with gzip.open(compressed_path, 'wb') as f_out:
                    f_out.writelines(f_in)
            
            file_path.unlink()  # Remove uncompressed file
            
        except Exception as e:
            logging.error(f"Compression error: {e}")
    
    async def close(self) -> None:
        """Close file handle"""        if self.current_file:
            self.current_file.close()
            self.current_file = None


class ElasticsearchLogWriter:
    """Elasticsearch log writer with bulk operations"""    
    def __init__(self, 
                 hosts: List[str],
                 index_pattern: str = "ia-influencer-logs-%Y.%m.%d",
                 username: Optional[str] = None,
                 password: Optional[str] = None,
                 use_ssl: bool = False,
                 verify_certs: bool = True):
        
        self.index_pattern = index_pattern
        self.client = AsyncElasticsearch(
            hosts=hosts,
            http_auth=(username, password) if username and password else None,
            use_ssl=use_ssl,
            verify_certs=verify_certs,
            timeout=30,
            max_retries=3,
            retry_on_timeout=True
        )
    
    async def write(self, entries: List[LogEntry]) -> bool:
        """Write entries to Elasticsearch using bulk API"""        try:
            if not entries:
                return True
            
            # Prepare bulk operations
            bulk_ops = []
            
            for entry in entries:
                index_name = entry.timestamp.strftime(self.index_pattern)
                
                # Index operation
                bulk_ops.append({
                    "index": {
                        "_index": index_name,
                        "_id": f"{entry.service}-{entry.timestamp.isoformat()}-{hash(entry.message)}"
                    }
                })
                
                # Document
                bulk_ops.append(entry.to_ecs_format())
            
            # Execute bulk operation
            response = await self.client.bulk(
                operations=bulk_ops,
                refresh=False
            )
            
            # Check for errors
            if response.get("errors"):
                error_count = sum(1 for item in response["items"] if "error" in item.get("index", {}))
                logging.error(f"Elasticsearch bulk errors: {error_count}/{len(entries)}")
                return False
            
            return True
            
        except Exception as e:
            logging.error(f"Elasticsearch writer error: {e}")
            return False
    
    async def close(self) -> None:
        """Close Elasticsearch client"""        await self.client.close()


class RedisLogWriter:
    """Redis log writer using streams"""    
    def __init__(self, 
                 redis_url: str,
                 stream_name: str = "ia-influencer-logs",
                 max_stream_length: int = 10000):
        self.redis_url = redis_url
        self.stream_name = stream_name
        self.max_stream_length = max_stream_length
        self.redis = None
    
    async def _get_redis(self):
        """Get or create Redis connection"""        if not self.redis:
            self.redis = await aioredis.from_url(self.redis_url)
        return self.redis
    
    async def write(self, entries: List[LogEntry]) -> bool:
        """Write entries to Redis stream"""        try:
            redis = await self._get_redis()
            
            # Use pipeline for efficiency
            async with redis.pipeline() as pipe:
                for entry in entries:
                    # Add to stream
                    pipe.xadd(
                        self.stream_name,
                        entry.to_dict(),
                        maxlen=self.max_stream_length,
                        approximate=True
                    )
                
                await pipe.execute()
            
            return True
            
        except Exception as e:
            logging.error(f"Redis writer error: {e}")
            return False
    
    async def close(self) -> None:
        """Close Redis connection"""        if self.redis:
            await self.redis.close()


class S3LogWriter:
    """S3 log writer for long-term storage"""    
    def __init__(self, 
                 bucket_name: str,
                 prefix: str = "logs",
                 region: str = "eu-central-1",
                 compress: bool = True):
        self.bucket_name = bucket_name
        self.prefix = prefix
        self.region = region
        self.compress = compress
        self.s3_client = boto3.client('s3', region_name=region)
    
    async def write(self, entries: List[LogEntry]) -> bool:
        """Write entries to S3 as compressed JSON"""        try:
            if not entries:
                return True
            
            # Create S3 key with timestamp
            timestamp = datetime.now(timezone.utc)
            key = f"{self.prefix}/{timestamp.strftime('%Y/%m/%d')}/logs-{timestamp.strftime('%H%M%S')}-{os.getpid()}.json"
            
            if self.compress:
                key += ".gz"
            
            # Prepare data
            log_data = [entry.to_dict() for entry in entries]
            json_data = json.dumps(log_data, indent=2)
            
            # Compress if enabled
            if self.compress:
                data = gzip.compress(json_data.encode('utf-8'))
            else:
                data = json_data.encode('utf-8')
            
            # Upload to S3
            self.s3_client.put_object(
                Bucket=self.bucket_name,
                Key=key,
                Body=data,
                ContentType="application/json",
                ContentEncoding="gzip" if self.compress else None
            )
            
            return True
            
        except ClientError as e:
            logging.error(f"S3 writer error: {e}")
            return False
    
    async def close(self) -> None:
        """Nothing to close for S3"""        pass


class FluentdLogWriter:
    """Fluentd log writer"""    
    def __init__(self, 
                 host: str = "localhost",
                 port: int = 24224,
                 tag: str = "ia.app"):
        self.host = host
        self.port = port
        self.tag = tag
        self.sender = fluentd.FluentSender(tag, host=host, port=port)
    
    async def write(self, entries: List[LogEntry]) -> bool:
        """Write entries to Fluentd"""        try:
            for entry in entries:
                self.sender.emit(entry.to_dict())
            return True
            
        except Exception as e:
            logging.error(f"Fluentd writer error: {e}")
            return False
    
    async def close(self) -> None:
        """Close Fluentd sender"""        self.sender.close()


class LogAggregator:
    """Advanced log aggregator with multiple destinations and buffering"""    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.processor = LogProcessor(
            service_name=self.config.get("service_name", "ia-influencer-agent"),
            environment=self.config.get("environment", "production"),
            version=self.config.get("version", "1.0.0")
        )
        self.buffer = LogBuffer(
            max_size=self.config.get("buffer_size", 1000),
            flush_interval=self.config.get("flush_interval", 30.0),
            force_flush_level=LogLevel.ERROR
        )
        self.writers: Dict[LogDestination, LogWriter] = {}
        self.running = False
        self.flush_task: Optional[asyncio.Task] = None
        
        # Initialize Sentry if configured
        self._setup_sentry()
        
        # Setup default enrichers and filters
        self._setup_default_enrichers()
        self._setup_default_filters()
    
    def _setup_sentry(self):
        """Setup Sentry integration if configured"""        sentry_config = self.config.get("sentry", {})
        if sentry_config.get("enabled") and sentry_config.get("dsn"):
            sentry_sdk.init(
                dsn=sentry_config["dsn"],
                environment=sentry_config.get("environment", "production"),
                traces_sample_rate=sentry_config.get("traces_sample_rate", 0.1),
                integrations=[LoggingIntegration(level=logging.INFO, event_level=logging.ERROR)]
            )
    
    def _setup_default_enrichers(self):
        """Setup default log enrichers"""        
        def add_trace_context(entry: LogEntry) -> LogEntry:
            """Add distributed tracing context"""            # This would integrate with your tracing system (e.g., OpenTelemetry)
            # For now, just ensure we have some context
            if not entry.trace_id:
                entry.trace_id = f"trace-{datetime.now().timestamp()}"
            return entry
        
        def add_performance_metrics(entry: LogEntry) -> LogEntry:
            """Add basic performance metrics"""            if not entry.metadata:
                entry.metadata = {}
            
            # Add basic system metrics
            import psutil
            entry.memory_usage_mb = psutil.virtual_memory().percent
            entry.cpu_usage_percent = psutil.cpu_percent()
            
            return entry
        
        self.processor.add_enricher(add_trace_context)
        self.processor.add_enricher(add_performance_metrics)
    
    def _setup_default_filters(self):
        """Setup default log filters"""        
        def filter_sensitive_data(entry: LogEntry) -> bool:
            """Filter out logs containing sensitive data"""            sensitive_patterns = ["password", "token", "secret", "key", "credential"]
            message_lower = entry.message.lower()
            
            return not any(pattern in message_lower for pattern in sensitive_patterns)
        
        def filter_noisy_logs(entry: LogEntry) -> bool:
            """Filter out noisy debug logs in production"""            if self.config.get("environment") == "production" and entry.level == LogLevel.DEBUG:
                # Only allow debug logs from critical modules
                critical_modules = ["ai", "fingerprinting", "monetization", "protection"]
                return any(module in entry.module.lower() for module in critical_modules)
            return True
        
        self.processor.add_filter(filter_sensitive_data)
        self.processor.add_filter(filter_noisy_logs)
    
    def add_writer(self, destination: LogDestination, writer: LogWriter):
        """Add a log writer for a destination"""        self.writers[destination] = writer
    
    def setup_console_writer(self, format_type: LogFormat = LogFormat.JSON):
        """Setup console log writer"""        writer = ConsoleLogWriter(format_type)
        self.add_writer(LogDestination.CONSOLE, writer)
    
    def setup_file_writer(self, 
                         file_path: str,
                         max_file_size: int = 100 * 1024 * 1024,
                         max_files: int = 10,
                         compress: bool = True):
        """Setup file log writer"""        writer = FileLogWriter(file_path, max_file_size, max_files, compress)
        self.add_writer(LogDestination.FILE, writer)
    
    def setup_elasticsearch_writer(self, 
                                  hosts: List[str],
                                  index_pattern: str = "ia-influencer-logs-%Y.%m.%d",
                                  username: Optional[str] = None,
                                  password: Optional[str] = None):
        """Setup Elasticsearch log writer"""        writer = ElasticsearchLogWriter(hosts, index_pattern, username, password)
        self.add_writer(LogDestination.ELASTICSEARCH, writer)
    
    def setup_redis_writer(self, 
                          redis_url: str,
                          stream_name: str = "ia-influencer-logs"):
        """Setup Redis log writer"""        writer = RedisLogWriter(redis_url, stream_name)
        self.add_writer(LogDestination.REDIS, writer)
    
    def setup_s3_writer(self, 
                       bucket_name: str,
                       prefix: str = "logs",
                       region: str = "eu-central-1"):
        """Setup S3 log writer"""        writer = S3LogWriter(bucket_name, prefix, region)
        self.add_writer(LogDestination.S3, writer)
    
    async def log(self, 
                  level: LogLevel,
                  message: str,
                  module: str,
                  **kwargs):
        """Log a message"""        
        # Create log entry
        entry = LogEntry(
            timestamp=datetime.now(timezone.utc),
            level=level,
            message=message,
            service=self.config.get("service_name", "ia-influencer-agent"),
            module=module,
            **kwargs
        )
        
        # Process entry
        processed_entry = self.processor.process(entry)
        if not processed_entry:
            return  # Filtered out
        
        # Add to buffer
        should_flush = await self.buffer.add(processed_entry)
        
        # Flush if needed
        if should_flush:
            await self._flush_buffer()
    
    async def _flush_buffer(self):
        """Flush buffer to all writers"""        entries = await self.buffer.flush()
        if not entries:
            return
        
        # Write to all destinations concurrently
        tasks = []
        for destination, writer in self.writers.items():
            task = asyncio.create_task(self._write_safe(writer, entries, destination))
            tasks.append(task)
        
        # Wait for all writes to complete
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)
    
    async def _write_safe(self, 
                         writer: LogWriter, 
                         entries: List[LogEntry],
                         destination: LogDestination):
        """Safely write to a destination with error handling"""        try:
            success = await writer.write(entries)
            if not success:
                logging.error(f"Failed to write to {destination}")
        except Exception as e:
            logging.error(f"Error writing to {destination}: {e}")
    
    async def start(self):
        """Start the aggregator"""        if self.running:
            return
        
        self.running = True
        
        # Start background flush task
        self.flush_task = asyncio.create_task(self._background_flush())
    
    async def stop(self):
        """Stop the aggregator and flush remaining logs"""        if not self.running:
            return
        
        self.running = False
        
        # Cancel background task
        if self.flush_task:
            self.flush_task.cancel()
            try:
                await self.flush_task
            except asyncio.CancelledError:
                pass
        
        # Final flush
        await self._flush_buffer()
        
        # Close all writers
        for writer in self.writers.values():
            await writer.close()
    
    async def _background_flush(self):
        """Background task to periodically flush buffer"""        while self.running:
            try:
                await asyncio.sleep(5)  # Check every 5 seconds
                
                buffer_size = await self.buffer.size()
                if buffer_size > 0:
                    # Check if flush interval exceeded
                    now = datetime.now(timezone.utc)
                    if (now - self.buffer.last_flush).total_seconds() >= self.buffer.flush_interval:
                        await self._flush_buffer()
                        
            except asyncio.CancelledError:
                break
            except Exception as e:
                logging.error(f"Background flush error: {e}")
    
    @asynccontextmanager
    async def context(self):
        """Context manager for the aggregator"""        await self.start()
        try:
            yield self
        finally:
            await self.stop()


# Factory function for creating pre-configured aggregators
def create_production_aggregator(config: Dict[str, Any]) -> LogAggregator:
    """Create a production-ready log aggregator"""    
    aggregator = LogAggregator(config)
    
    # Setup writers based on configuration
    if config.get("console", {}).get("enabled", True):
        aggregator.setup_console_writer(LogFormat.JSON)
    
    if config.get("file", {}).get("enabled", True):
        file_config = config.get("file", {})
        aggregator.setup_file_writer(
            file_path=file_config.get("path", "/var/log/ia-influencer/app.log"),
            max_file_size=file_config.get("max_size", 100 * 1024 * 1024),
            max_files=file_config.get("max_files", 10)
        )
    
    if config.get("elasticsearch", {}).get("enabled", False):
        es_config = config.get("elasticsearch", {})
        aggregator.setup_elasticsearch_writer(
            hosts=es_config.get("hosts", ["localhost:9200"]),
            index_pattern=es_config.get("index_pattern", "ia-influencer-logs-%Y.%m.%d"),
            username=es_config.get("username"),
            password=es_config.get("password")
        )
    
    if config.get("redis", {}).get("enabled", False):
        redis_config = config.get("redis", {})
        aggregator.setup_redis_writer(
            redis_url=redis_config.get("url", "redis://localhost:6379"),
            stream_name=redis_config.get("stream_name", "ia-influencer-logs")
        )
    
    if config.get("s3", {}).get("enabled", False):
        s3_config = config.get("s3", {})
        aggregator.setup_s3_writer(
            bucket_name=s3_config.get("bucket"),
            prefix=s3_config.get("prefix", "logs"),
            region=s3_config.get("region", "eu-central-1")
        )
    
    return aggregator


# Convenience functions for different log levels
async def log_debug(aggregator: LogAggregator, message: str, module: str, **kwargs):
    """Log debug message"""    await aggregator.log(LogLevel.DEBUG, message, module, **kwargs)

async def log_info(aggregator: LogAggregator, message: str, module: str, **kwargs):
    """Log info message"""    await aggregator.log(LogLevel.INFO, message, module, **kwargs)

async def log_warning(aggregator: LogAggregator, message: str, module: str, **kwargs):
    """Log warning message"""    await aggregator.log(LogLevel.WARNING, message, module, **kwargs)

async def log_error(aggregator: LogAggregator, message: str, module: str, **kwargs):
    """Log error message"""    await aggregator.log(LogLevel.ERROR, message, module, **kwargs)

async def log_critical(aggregator: LogAggregator, message: str, module: str, **kwargs):
    """Log critical message"""    await aggregator.log(LogLevel.CRITICAL, message, module, **kwargs)
    timestamp: datetime
    level: LogLevel
    message: str
    service: str
    module: str
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    trace_id: Optional[str] = None
    span_id: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    environment: str = "production"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert log entry to dictionary"""        data = asdict(self)
        data['timestamp'] = self.timestamp.isoformat()
        return data
    
    def to_json(self) -> str:
        """Convert log entry to JSON string"""        return json.dumps(self.to_dict())


class LogProcessor:
    """Advanced log processing and filtering"""    
    def __init__(self):
        self.filters = []
        self.enrichers = []
        self.sanitizers = []
    
    def add_filter(self, filter_func):
        """Add log filter function"""        self.filters.append(filter_func)
    
    def add_enricher(self, enricher_func):
        """Add log enrichment function"""        self.enrichers.append(enricher_func)
    
    def add_sanitizer(self, sanitizer_func):
        """Add data sanitization function"""        self.sanitizers.append(sanitizer_func)
    
    def process_log(self, log_entry: LogEntry) -> Optional[LogEntry]:
        """Process log entry through all filters and enrichers"""        # Apply filters
        for filter_func in self.filters:
            if not filter_func(log_entry):
                return None
        
        # Apply enrichers
        for enricher_func in self.enrichers:
            log_entry = enricher_func(log_entry)
        
        # Apply sanitizers
        for sanitizer_func in self.sanitizers:
            log_entry = sanitizer_func(log_entry)
        
        return log_entry


class LogBuffer:
    """Buffered logging for batch processing"""    
    def __init__(self, max_size: int = 1000, flush_interval: int = 30):
        self.max_size = max_size
        self.flush_interval = flush_interval
        self.buffer: List[LogEntry] = []
        self.last_flush = datetime.now(timezone.utc)
        self._lock = asyncio.Lock()
    
    async def add_log(self, log_entry: LogEntry) -> bool:
        """Add log entry to buffer"""        async with self._lock:
            self.buffer.append(log_entry)
            
            # Check if buffer needs flushing
            if (len(self.buffer) >= self.max_size or 
                (datetime.now(timezone.utc) - self.last_flush).seconds >= self.flush_interval):
                return True
        return False
    
    async def get_logs(self, clear: bool = True) -> List[LogEntry]:
        """Get logs from buffer"""        async with self._lock:
            logs = self.buffer.copy()
            if clear:
                self.buffer.clear()
                self.last_flush = datetime.now(timezone.utc)
            return logs


class LogDestination:
    """Base class for log destinations"""    
    async def send_logs(self, logs: List[LogEntry]) -> bool:
        """Send logs to destination"""        # Default implementation for log destinations without sending support
        logging.warning(f"Log sending not implemented for {self.__class__.__name__}")
        return False


class ElasticsearchDestination(LogDestination):
    """Elasticsearch log destination"""    
    def __init__(self, hosts: List[str], index_pattern: str = "ia-influencer-logs-%Y.%m.%d"):
        self.hosts = hosts
        self.index_pattern = index_pattern
        self.client = None
    
    async def connect(self):
        """Connect to Elasticsearch"""        self.client = AsyncElasticsearch(hosts=self.hosts)
    
    async def send_logs(self, logs: List[LogEntry]) -> bool:
        """Send logs to Elasticsearch"""        if not self.client:
            await self.connect()
        
        try:
            bulk_body = []
            for log in logs:
                index_name = log.timestamp.strftime(self.index_pattern)
                bulk_body.append({
                    "index": {
                        "_index": index_name,
                        "_type": "_doc"
                    }
                })
                bulk_body.append(log.to_dict())
            
            response = await self.client.bulk(body=bulk_body)
            return not response.get('errors', False)
        
        except Exception as e:
            logging.error(f"Failed to send logs to Elasticsearch: {e}")
            return False


class RedisDestination(LogDestination):
    """Redis log destination for real-time processing"""    
    def __init__(self, redis_url: str, stream_name: str = "ia-influencer-logs"):
        self.redis_url = redis_url
        self.stream_name = stream_name
        self.client = None
    
    async def connect(self):
        """Connect to Redis"""        self.client = await aioredis.from_url(self.redis_url)
    
    async def send_logs(self, logs: List[LogEntry]) -> bool:
        """Send logs to Redis stream"""        if not self.client:
            await self.connect()
        
        try:
            for log in logs:
                await self.client.xadd(
                    self.stream_name,
                    log.to_dict()
                )
            return True
        
        except Exception as e:
            logging.error(f"Failed to send logs to Redis: {e}")
            return False


class FileDestination(LogDestination):
    """File-based log destination"""    
    def __init__(self, log_directory: str, rotation_size: int = 100 * 1024 * 1024):
        self.log_directory = Path(log_directory)
        self.rotation_size = rotation_size
        self.log_directory.mkdir(parents=True, exist_ok=True)
    
    async def send_logs(self, logs: List[LogEntry]) -> bool:
        """Send logs to file"""        try:
            for log in logs:
                log_file = self.log_directory / f"{log.service}-{datetime.now().strftime('%Y-%m-%d')}.log"
                
                # Check file rotation
                if log_file.exists() and log_file.stat().st_size > self.rotation_size:
                    rotated_file = log_file.with_suffix(f".{int(datetime.now().timestamp())}.log")
                    log_file.rename(rotated_file)
                
                with open(log_file, 'a') as f:
                    f.write(log.to_json() + '\n')
            
            return True
        
        except Exception as e:
            logging.error(f"Failed to write logs to file: {e}")
            return False


class LogAggregator:
    """Advanced log aggregation service for IA Influencer Agent"""    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.processor = LogProcessor()
        self.buffer = LogBuffer(
            max_size=self.config.get('buffer_size', 1000),
            flush_interval=self.config.get('flush_interval', 30)
        )
        self.destinations: List[LogDestination] = []
        self.is_running = False
        self._setup_logging()
        self._setup_destinations()
        self._setup_filters()
    
    def _setup_logging(self):
        """Setup structured logging configuration"""        # Configure structlog
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
        
        # Configure Sentry integration
        if self.config.get('sentry_dsn'):
            sentry_logging = LoggingIntegration(
                level=logging.INFO,
                event_level=logging.ERROR
            )
            sentry_sdk.init(
                dsn=self.config['sentry_dsn'],
                integrations=[sentry_logging],
                traces_sample_rate=0.1
            )
    
    def _setup_destinations(self):
        """Setup log destinations based on configuration"""        # Elasticsearch destination
        if self.config.get('elasticsearch', {}).get('enabled', False):
            es_config = self.config['elasticsearch']
            es_dest = ElasticsearchDestination(
                hosts=es_config.get('hosts', ['localhost:9200']),
                index_pattern=es_config.get('index_pattern', 'ia-influencer-logs-%Y.%m.%d')
            )
            self.destinations.append(es_dest)
        
        # Redis destination
        if self.config.get('redis', {}).get('enabled', False):
            redis_config = self.config['redis']
            redis_dest = RedisDestination(
                redis_url=redis_config.get('url', 'redis://localhost:6379'),
                stream_name=redis_config.get('stream_name', 'ia-influencer-logs')
            )
            self.destinations.append(redis_dest)
        
        # File destination
        if self.config.get('file', {}).get('enabled', True):
            file_config = self.config.get('file', {})
            file_dest = FileDestination(
                log_directory=file_config.get('directory', '/var/log/ia-influencer'),
                rotation_size=file_config.get('rotation_size', 100 * 1024 * 1024)
            )
            self.destinations.append(file_dest)
    
    def _setup_filters(self):
        """Setup default log filters and enrichers"""        # Filter sensitive data
        def sanitize_sensitive_data(log_entry: LogEntry) -> LogEntry:
            """Remove sensitive information from logs"""            if log_entry.metadata:
                sensitive_fields = ['password', 'token', 'secret', 'key', 'credential']
                for field in sensitive_fields:
                    if field in log_entry.metadata:
                        log_entry.metadata[field] = '[REDACTED]'
            return log_entry
        
        # Enrich with service metadata
        def enrich_service_metadata(log_entry: LogEntry) -> LogEntry:
            """Add service-specific metadata"""            if not log_entry.metadata:
                log_entry.metadata = {}
            
            log_entry.metadata.update({
                'environment': log_entry.environment,
                'service_version': getattr(settings, 'VERSION', '1.0.0'),
                'hostname': getattr(settings, 'HOSTNAME', 'unknown'),
                'region': getattr(settings, 'AWS_REGION', 'eu-central-1')
            })
            return log_entry
        
        # Add rate limiting filter
        def rate_limit_filter(log_entry: LogEntry) -> bool:
            """Rate limit log entries to prevent spam"""            # Implement rate limiting logic based on service and level
            if log_entry.level == LogLevel.DEBUG:
                # Limit debug logs more aggressively
                return True  # Simplified - implement actual rate limiting
            return True
        
        self.processor.add_sanitizer(sanitize_sensitive_data)
        self.processor.add_enricher(enrich_service_metadata)
        self.processor.add_filter(rate_limit_filter)
    
    async def log(self, 
                  level: LogLevel,
                  message: str,
                  service: str,
                  module: str,
                  user_id: Optional[str] = None,
                  session_id: Optional[str] = None,
                  trace_id: Optional[str] = None,
                  span_id: Optional[str] = None,
                  metadata: Optional[Dict[str, Any]] = None) -> bool:
        """Log a message through the aggregation system"""        
        log_entry = LogEntry(
            timestamp=datetime.now(timezone.utc),
            level=level,
            message=message,
            service=service,
            module=module,
            user_id=user_id,
            session_id=session_id,
            trace_id=trace_id,
            span_id=span_id,
            metadata=metadata,
            environment=getattr(settings, 'ENVIRONMENT', 'production')
        )
        
        # Process log entry
        processed_log = self.processor.process_log(log_entry)
        if not processed_log:
            return False
        
        # Add to buffer
        should_flush = await self.buffer.add_log(processed_log)
        
        if should_flush:
            await self._flush_logs()
        
        return True
    
    async def _flush_logs(self):
        """Flush logs to all destinations"""        logs = await self.buffer.get_logs()
        if not logs:
            return
        
        # Send to all destinations
        tasks = []
        for destination in self.destinations:
            tasks.append(destination.send_logs(logs))
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Log any failures
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                logging.error(f"Failed to send logs to destination {i}: {result}")
    
    async def start(self):
        """Start the log aggregator service"""        self.is_running = True
        
        # Start background flush task
        asyncio.create_task(self._background_flush())
        
        logging.info("Log aggregator service started")
    
    async def stop(self):
        """Stop the log aggregator service"""        self.is_running = False
        
        # Final flush
        await self._flush_logs()
        
        logging.info("Log aggregator service stopped")
    
    async def _background_flush(self):
        """Background task to periodically flush logs"""        while self.is_running:
            await asyncio.sleep(self.buffer.flush_interval)
            await self._flush_logs()
    
    async def get_logs(self, 
                      service: Optional[str] = None,
                      level: Optional[LogLevel] = None,
                      start_time: Optional[datetime] = None,
                      end_time: Optional[datetime] = None,
                      limit: int = 100) -> List[Dict[str, Any]]:
        """Query logs from destinations"""        # This would typically query Elasticsearch or other destinations
        # Simplified implementation for now
        return []
    
    def create_service_logger(self, service_name: str, module_name: str):
        """Create a service-specific logger"""        class ServiceLogger:
            def __init__(self, aggregator: LogAggregator, service: str, module: str):
                self.aggregator = aggregator
                self.service = service
                self.module = module
            
            async def debug(self, message: str, **kwargs):
                await self.aggregator.log(LogLevel.DEBUG, message, self.service, self.module, **kwargs)
            
            async def info(self, message: str, **kwargs):
                await self.aggregator.log(LogLevel.INFO, message, self.service, self.module, **kwargs)
            
            async def warning(self, message: str, **kwargs):
                await self.aggregator.log(LogLevel.WARNING, message, self.service, self.module, **kwargs)
            
            async def error(self, message: str, **kwargs):
                await self.aggregator.log(LogLevel.ERROR, message, self.service, self.module, **kwargs)
            
            async def critical(self, message: str, **kwargs):
                await self.aggregator.log(LogLevel.CRITICAL, message, self.service, self.module, **kwargs)
        
        return ServiceLogger(self, service_name, module_name)
