"""
Log Aggregation Configuration for IA-Influencer Agent Platform
=============================================================

Advanced log aggregation and centralized logging with Elasticsearch,
real-time streaming, and distributed tracing for multi-format content processing.

Author: Fahed Mlaiel <mlaiel@live.de>
Project: IA-Influencer Agent + Content Protection Platform
Team: Lead Dev IA + Backend Senior + ML Engineer + DBA + Security + Microservices + Audio + DevOps

Copyright Notice:
This code is the intellectual property of Fahed Mlaiel.
Any unauthorized use, reproduction, or distribution of this code
without explicit written permission from the author is strictly prohibited.

Contact: mlaiel@live.de for licensing inquiries.
"""

import json
import time
import threading
import queue
from datetime import datetime, timezone
from typing import Dict, Any, Optional, List, Union, Callable
from dataclasses import dataclass, field, asdict
from enum import Enum
import logging
import logging.handlers
from urllib.parse import urlparse
import asyncio
import aiohttp
import ssl

from elasticsearch import Elasticsearch, AsyncElasticsearch
from elasticsearch.helpers import bulk, async_bulk
import redis
import kafka
from kafka import KafkaProducer, KafkaConsumer


class AggregationBackend(str, Enum):
    """Supported log aggregation backends"""
    ELASTICSEARCH = "elasticsearch"
    KAFKA = "kafka"
    REDIS_STREAMS = "redis_streams"
    FLUENTD = "fluentd"
    LOGSTASH = "logstash"
    CLICKHOUSE = "clickhouse"
    LOKI = "loki"
    DATADOG = "datadog"
    SPLUNK = "splunk"


class StreamingMode(str, Enum):
    """Log streaming modes"""
    SYNCHRONOUS = "synchronous"
    ASYNCHRONOUS = "asynchronous"
    BATCH = "batch"
    REAL_TIME = "real_time"


class IndexingStrategy(str, Enum):
    """Elasticsearch indexing strategies"""
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    BY_SIZE = "by_size"
    BY_LOG_LEVEL = "by_log_level"
    BY_COMPONENT = "by_component"


@dataclass
class ElasticsearchConfig:
    """Elasticsearch configuration"""
    hosts: List[str] = field(default_factory=lambda: ["localhost:9200"])
    username: Optional[str] = None
    password: Optional[str] = None
    api_key: Optional[str] = None
    cloud_id: Optional[str] = None
    
    # SSL/TLS configuration
    use_ssl: bool = False
    verify_certs: bool = True
    ssl_cert_path: Optional[str] = None
    ssl_key_path: Optional[str] = None
    ca_certs_path: Optional[str] = None
    
    # Connection settings
    timeout: int = 30
    max_retries: int = 3
    retry_on_timeout: bool = True
    sniff_on_start: bool = True
    sniff_on_connection_fail: bool = True
    sniffer_timeout: int = 60
    
    # Index settings
    index_pattern: str = "ia-influencer-logs-{date}"
    index_template_name: str = "ia-influencer-logs-template"
    number_of_shards: int = 1
    number_of_replicas: int = 1
    refresh_interval: str = "1s"
    
    # Indexing strategy
    indexing_strategy: IndexingStrategy = IndexingStrategy.DAILY
    index_rotation_size: Optional[str] = None  # e.g., "1gb"
    
    # Performance settings
    bulk_size: int = 500
    bulk_timeout: int = 10
    max_concurrent_requests: int = 10
    request_timeout: int = 60


@dataclass
class KafkaConfig:
    """Kafka configuration"""
    bootstrap_servers: List[str] = field(default_factory=lambda: ["localhost:9092"])
    topic: str = "ia-influencer-logs"
    
    # Security settings
    security_protocol: str = "PLAINTEXT"  # PLAINTEXT, SSL, SASL_PLAINTEXT, SASL_SSL
    sasl_mechanism: Optional[str] = None  # PLAIN, SCRAM-SHA-256, SCRAM-SHA-512
    sasl_username: Optional[str] = None
    sasl_password: Optional[str] = None
    ssl_cert_path: Optional[str] = None
    ssl_key_path: Optional[str] = None
    ssl_ca_path: Optional[str] = None
    
    # Producer settings
    batch_size: int = 16384
    linger_ms: int = 10
    max_request_size: int = 1048576
    compression_type: str = "gzip"  # none, gzip, snappy, lz4, zstd
    acks: Union[int, str] = "all"  # 0, 1, all
    retries: int = 5
    
    # Consumer settings (for log processing)
    group_id: str = "ia-influencer-log-processor"
    auto_offset_reset: str = "latest"  # earliest, latest
    enable_auto_commit: bool = True
    auto_commit_interval_ms: int = 5000


@dataclass
class RedisStreamsConfig:
    """Redis Streams configuration"""
    host: str = "localhost"
    port: int = 6379
    db: int = 0
    password: Optional[str] = None
    
    # Connection settings
    connection_pool_kwargs: Dict[str, Any] = field(default_factory=dict)
    socket_timeout: int = 5
    socket_connect_timeout: int = 5
    
    # Stream settings
    stream_name: str = "ia-influencer-logs"
    consumer_group: str = "log-processors"
    consumer_name: str = "log-aggregator"
    max_stream_length: int = 10000
    
    # Batch settings
    batch_size: int = 100
    block_ms: int = 1000


@dataclass
class FluentdConfig:
    """Fluentd configuration"""
    host: str = "localhost"
    port: int = 24224
    tag: str = "ia-influencer.logs"
    
    # Connection settings
    timeout: float = 3.0
    retry_limit: int = 3
    retry_wait: float = 1.0
    
    # Buffer settings
    buffer_size: int = 8 * 1024 * 1024  # 8MB
    queue_size: int = 1024


class LogAggregationConfig:
    """
    Enterprise log aggregation configuration for IA-Influencer platform.
    
    Provides centralized logging with multiple backends, real-time streaming,
    distributed tracing, and advanced search capabilities for multi-format
    content processing and protection operations.
    """
    
    def __init__(
        self,
        backends: List[AggregationBackend] = None,
        streaming_mode: StreamingMode = StreamingMode.ASYNCHRONOUS,
        elasticsearch_config: Optional[ElasticsearchConfig] = None,
        kafka_config: Optional[KafkaConfig] = None,
        redis_config: Optional[RedisStreamsConfig] = None,
        fluentd_config: Optional[FluentdConfig] = None,
        enable_tracing: bool = True,
        enable_metrics: bool = True,
        buffer_size: int = 10000,
        flush_interval: int = 10,
        max_retries: int = 3,
        enable_compression: bool = True,
        enable_encryption: bool = False,
        custom_processors: Optional[List[Callable]] = None
    ):
        """
        Initialize log aggregation configuration.
        
        Args:
            backends: List of aggregation backends to use
            streaming_mode: Log streaming mode
            elasticsearch_config: Elasticsearch configuration
            kafka_config: Kafka configuration
            redis_config: Redis Streams configuration
            fluentd_config: Fluentd configuration
            enable_tracing: Enable distributed tracing
            enable_metrics: Enable metrics collection
            buffer_size: Internal buffer size
            flush_interval: Flush interval in seconds
            max_retries: Maximum retry attempts
            enable_compression: Enable log compression
            enable_encryption: Enable log encryption
            custom_processors: Custom log processors
        """
        self.backends = backends or [AggregationBackend.ELASTICSEARCH]
        self.streaming_mode = streaming_mode
        self.enable_tracing = enable_tracing
        self.enable_metrics = enable_metrics
        self.buffer_size = buffer_size
        self.flush_interval = flush_interval
        self.max_retries = max_retries
        self.enable_compression = enable_compression
        self.enable_encryption = enable_encryption
        self.custom_processors = custom_processors or []
        
        # Backend configurations
        self.elasticsearch_config = elasticsearch_config or ElasticsearchConfig()
        self.kafka_config = kafka_config or KafkaConfig()
        self.redis_config = redis_config or RedisStreamsConfig()
        self.fluentd_config = fluentd_config or FluentdConfig()
        
        # Initialize components
        self._initialize_backends()
        self._initialize_buffers()
        self._start_background_processes()
    
    def _initialize_backends(self) -> None:
        """Initialize aggregation backends"""
        self._backend_clients = {}
        
        for backend in self.backends:
            try:
                if backend == AggregationBackend.ELASTICSEARCH:
                    self._initialize_elasticsearch()
                elif backend == AggregationBackend.KAFKA:
                    self._initialize_kafka()
                elif backend == AggregationBackend.REDIS_STREAMS:
                    self._initialize_redis_streams()
                elif backend == AggregationBackend.FLUENTD:
                    self._initialize_fluentd()
                
                logging.info(f"Initialized log aggregation backend: {backend}")
                
            except Exception as e:
                logging.error(f"Failed to initialize backend {backend}: {e}")
    
    def _initialize_elasticsearch(self) -> None:
        """Initialize Elasticsearch client"""



        try:
            es_config = self.elasticsearch_config
            
            # Build client configuration
            client_config = {
                "hosts": es_config.hosts,
                "timeout": es_config.timeout,
                "max_retries": es_config.max_retries,
                "retry_on_timeout": es_config.retry_on_timeout,
                "sniff_on_start": es_config.sniff_on_start,
                "sniff_on_connection_fail": es_config.sniff_on_connection_fail,
                "sniffer_timeout": es_config.sniffer_timeout
            }
            
            # Add authentication
            if es_config.api_key:
                client_config["api_key"] = es_config.api_key
            elif es_config.cloud_id:
                client_config["cloud_id"] = es_config.cloud_id
                if es_config.username and es_config.password:
                    client_config["basic_auth"] = (es_config.username, es_config.password)
            elif es_config.username and es_config.password:
                client_config["basic_auth"] = (es_config.username, es_config.password)
            
            # Add SSL configuration
            if es_config.use_ssl:
                client_config["use_ssl"] = True
                client_config["verify_certs"] = es_config.verify_certs
                
                if es_config.ca_certs_path:
                    client_config["ca_certs"] = es_config.ca_certs_path
                if es_config.ssl_cert_path and es_config.ssl_key_path:
                    client_config["client_cert"] = es_config.ssl_cert_path
                    client_config["client_key"] = es_config.ssl_key_path
            
            # Create clients
            self._backend_clients["elasticsearch"] = Elasticsearch(**client_config)
            self._backend_clients["elasticsearch_async"] = AsyncElasticsearch(**client_config)
            
            # Create index template
            self._create_elasticsearch_template()
            
        except Exception as e:
            logging.error(f"Failed to initialize Elasticsearch: {e}")
            raise
    
    def _create_elasticsearch_template(self) -> None:
        """Create Elasticsearch index template"""



        try:
            es_client = self._backend_clients["elasticsearch"]
            es_config = self.elasticsearch_config
            
            template = {
                "index_patterns": [es_config.index_pattern.replace("{date}", "*")],
                "settings": {
                    "number_of_shards": es_config.number_of_shards,
                    "number_of_replicas": es_config.number_of_replicas,
                    "refresh_interval": es_config.refresh_interval,
                    "index": {
                        "lifecycle": {
                            "name": "ia-influencer-logs-policy",
                            "rollover_alias": "ia-influencer-logs"
                        }
                    }
                },
                "mappings": {
                    "properties": {
                        "@timestamp": {"type": "date"},
                        "timestamp": {"type": "date"},
                        "level": {"type": "keyword"},
                        "logger": {"type": "keyword"},
                        "message": {"type": "text", "analyzer": "standard"},
                        "module": {"type": "keyword"},
                        "function": {"type": "keyword"},
                        "line": {"type": "integer"},
                        "thread": {"type": "keyword"},
                        "process": {"type": "keyword"},
                        
                        # Request context fields
                        "request_id": {"type": "keyword"},
                        "correlation_id": {"type": "keyword"},
                        "user_id": {"type": "keyword"},
                        "tenant_id": {"type": "keyword"},
                        "session_id": {"type": "keyword"},
                        "ip_address": {"type": "ip"},
                        "user_agent": {"type": "text"},
                        "api_endpoint": {"type": "keyword"},
                        "http_method": {"type": "keyword"},
                        
                        # Content context fields
                        "content_id": {"type": "keyword"},
                        "content_type": {"type": "keyword"},
                        "content_format": {"type": "keyword"},
                        "file_size": {"type": "long"},
                        "duration": {"type": "float"},
                        "fingerprint_id": {"type": "keyword"},
                        
                        # AI context fields
                        "model_name": {"type": "keyword"},
                        "model_version": {"type": "keyword"},
                        "inference_type": {"type": "keyword"},
                        "processing_time": {"type": "float"},
                        "confidence_score": {"type": "float"},
                        
                        # Performance fields
                        "operation": {"type": "keyword"},
                        "start_time": {"type": "float"},
                        "end_time": {"type": "float"},
                        "cpu_usage": {"type": "float"},
                        "memory_usage": {"type": "float"},
                        
                        # Security fields
                        "threat_level": {"type": "keyword"},
                        "attack_type": {"type": "keyword"},
                        "source_ip": {"type": "ip"},
                        "blocked": {"type": "boolean"},
                        
                        # Business fields
                        "event_type": {"type": "keyword"},
                        "outcome": {"type": "keyword"},
                        "resource_type": {"type": "keyword"},
                        "resource_id": {"type": "keyword"},
                        
                        # Platform identification
                        "platform": {"type": "keyword"},
                        "environment": {"type": "keyword"},
                        "version": {"type": "keyword"},
                        "hostname": {"type": "keyword"},
                        "service": {"type": "keyword"},
                        
                        # Flexible fields
                        "tags": {"type": "keyword"},
                        "labels": {"type": "object"},
                        "metadata": {"type": "object"},
                        "details": {"type": "object"}
                    }
                }
            }
            
            # Create or update template
            es_client.indices.put_index_template(
                name=es_config.index_template_name,
                body=template
            )
            
            logging.info(f"Created Elasticsearch index template: {es_config.index_template_name}")
            
        except Exception as e:
            logging.error(f"Failed to create Elasticsearch template: {e}")
    
    def _initialize_kafka(self) -> None:
        """Initialize Kafka producer"""



        try:
            kafka_config = self.kafka_config
            
            producer_config = {
                "bootstrap_servers": kafka_config.bootstrap_servers,
                "batch_size": kafka_config.batch_size,
                "linger_ms": kafka_config.linger_ms,
                "max_request_size": kafka_config.max_request_size,
                "compression_type": kafka_config.compression_type,
                "acks": kafka_config.acks,
                "retries": kafka_config.retries,
                "value_serializer": lambda v: json.dumps(v).encode('utf-8')
            }
            
            # Add security configuration
            if kafka_config.security_protocol != "PLAINTEXT":
                producer_config["security_protocol"] = kafka_config.security_protocol
                
                if kafka_config.sasl_mechanism:
                    producer_config["sasl_mechanism"] = kafka_config.sasl_mechanism
                    producer_config["sasl_plain_username"] = kafka_config.sasl_username
                    producer_config["sasl_plain_password"] = kafka_config.sasl_password
                
                if kafka_config.ssl_cert_path:
                    producer_config["ssl_certfile"] = kafka_config.ssl_cert_path
                    producer_config["ssl_keyfile"] = kafka_config.ssl_key_path
                    producer_config["ssl_cafile"] = kafka_config.ssl_ca_path
            
            self._backend_clients["kafka_producer"] = KafkaProducer(**producer_config)
            
        except Exception as e:
            logging.error(f"Failed to initialize Kafka: {e}")
            raise
    
    def _initialize_redis_streams(self) -> None:
        """Initialize Redis Streams client"""



        try:
            redis_config = self.redis_config
            
            connection_config = {
                "host": redis_config.host,
                "port": redis_config.port,
                "db": redis_config.db,
                "socket_timeout": redis_config.socket_timeout,
                "socket_connect_timeout": redis_config.socket_connect_timeout,
                **redis_config.connection_pool_kwargs
            }
            
            if redis_config.password:
                connection_config["password"] = redis_config.password
            
            self._backend_clients["redis"] = redis.Redis(**connection_config)
            
            # Create consumer group
            try:
                self._backend_clients["redis"].xgroup_create(
                    redis_config.stream_name,
                    redis_config.consumer_group,
                    id="0",
                    mkstream=True
                )
            except redis.ResponseError as e:
                if "BUSYGROUP" not in str(e):
                    raise
            
        except Exception as e:
            logging.error(f"Failed to initialize Redis Streams: {e}")
            raise
    
    def _initialize_fluentd(self) -> None:
        """Initialize Fluentd client"""



        try:
            from fluent import sender
            
            fluentd_config = self.fluentd_config
            
            self._backend_clients["fluentd"] = sender.FluentSender(
                tag=fluentd_config.tag,
                host=fluentd_config.host,
                port=fluentd_config.port,
                timeout=fluentd_config.timeout,
                retry_limit=fluentd_config.retry_limit,
                retry_wait=fluentd_config.retry_wait,
                buffer_size=fluentd_config.buffer_size,
                queue_size=fluentd_config.queue_size
            )
            
        except ImportError:
            logging.error("fluent-logger package not installed for Fluentd support")
            raise
        except Exception as e:
            logging.error(f"Failed to initialize Fluentd: {e}")
            raise
    
    def _initialize_buffers(self) -> None:
        """Initialize internal log buffers"""
        self._log_buffer = queue.Queue(maxsize=self.buffer_size)
        self._metrics_buffer = queue.Queue(maxsize=1000)
        self._buffer_lock = threading.Lock()
    
    def _start_background_processes(self) -> None:
        """Start background processing threads"""
        self._stop_event = threading.Event()
        
        # Start buffer flush thread
        self._flush_thread = threading.Thread(
            target=self._flush_buffer_worker,
            daemon=True
        )
        self._flush_thread.start()
        
        # Start metrics collection thread if enabled
        if self.enable_metrics:
            self._metrics_thread = threading.Thread(
                target=self._metrics_worker,
                daemon=True
            )
            self._metrics_thread.start()
    
    def _flush_buffer_worker(self) -> None:
        """Background worker to flush log buffer"""
        while not self._stop_event.is_set():
            try:
                # Collect logs from buffer
                logs_to_send = []
                
                # Get logs with timeout
                try:
                    while len(logs_to_send) < self.elasticsearch_config.bulk_size:
                        log_entry = self._log_buffer.get(timeout=1)
                        logs_to_send.append(log_entry)
                except queue.Empty:
                    pass
                
                # Send logs if we have any
                if logs_to_send:
                    self._send_logs_to_backends(logs_to_send)
                
                # Wait for flush interval
                time.sleep(self.flush_interval)
                
            except Exception as e:
                logging.error(f"Error in flush buffer worker: {e}")
                time.sleep(1)
    
    def _metrics_worker(self) -> None:
        """Background worker for metrics collection"""
        while not self._stop_event.is_set():
            try:
                # Collect internal metrics
                metrics = self._collect_internal_metrics()
                
                # Send metrics to backends
                for backend in self.backends:
                    if backend == AggregationBackend.ELASTICSEARCH:
                        self._send_metrics_to_elasticsearch(metrics)
                
                time.sleep(60)  # Collect metrics every minute
                
            except Exception as e:
                logging.error(f"Error in metrics worker: {e}")
                time.sleep(60)
    
    def _collect_internal_metrics(self) -> Dict[str, Any]:
        """Collect internal aggregation metrics"""



        return {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "buffer_size": self._log_buffer.qsize(),
            "metrics_buffer_size": self._metrics_buffer.qsize(),
            "active_backends": len(self._backend_clients),
            "flush_interval": self.flush_interval,
            "streaming_mode": self.streaming_mode.value
        }
    
    def send_log(self, log_entry: Dict[str, Any]) -> None:
        """
        Send a log entry to aggregation backends.
        
        Args:
            log_entry: Log entry to send
        """



        try:
            # Enrich log entry
            enriched_entry = self._enrich_log_entry(log_entry)
            
            # Apply custom processors
            for processor in self.custom_processors:
                enriched_entry = processor(enriched_entry)
            
            if self.streaming_mode == StreamingMode.SYNCHRONOUS:
                # Send immediately
                self._send_logs_to_backends([enriched_entry])
            else:
                # Add to buffer
                try:
                    self._log_buffer.put(enriched_entry, timeout=1)
                except queue.Full:
                    logging.warning("Log buffer full, dropping log entry")
            
        except Exception as e:
            logging.error(f"Failed to send log entry: {e}")
    
    def _enrich_log_entry(self, log_entry: Dict[str, Any]) -> Dict[str, Any]:
        """Enrich log entry with additional metadata"""
        enriched = log_entry.copy()
        
        # Add timestamp if not present
        if "@timestamp" not in enriched and "timestamp" not in enriched:
            enriched["@timestamp"] = datetime.now(timezone.utc).isoformat()
        
        # Add platform metadata
        enriched.update({
            "platform": "ia-influencer-agent",
            "aggregation_backend": [backend.value for backend in self.backends],
            "streaming_mode": self.streaming_mode.value,
            "version": "1.0.0"  # Should come from app config
        })
        
        # Add hostname
        import socket
        enriched["hostname"] = socket.gethostname()
        
        return enriched
    
    def _send_logs_to_backends(self, log_entries: List[Dict[str, Any]]) -> None:
        """Send log entries to all configured backends"""
        for backend in self.backends:
            try:
                if backend == AggregationBackend.ELASTICSEARCH:
                    self._send_to_elasticsearch(log_entries)
                elif backend == AggregationBackend.KAFKA:
                    self._send_to_kafka(log_entries)
                elif backend == AggregationBackend.REDIS_STREAMS:
                    self._send_to_redis_streams(log_entries)
                elif backend == AggregationBackend.FLUENTD:
                    self._send_to_fluentd(log_entries)
                
            except Exception as e:
                logging.error(f"Failed to send logs to {backend}: {e}")
    
    def _send_to_elasticsearch(self, log_entries: List[Dict[str, Any]]) -> None:
        """Send log entries to Elasticsearch"""



        try:
            es_client = self._backend_clients["elasticsearch"]
            es_config = self.elasticsearch_config
            
            # Prepare bulk actions
            actions = []
            for entry in log_entries:
                index_name = self._get_elasticsearch_index_name(entry)
                action = {
                    "_index": index_name,
                    "_source": entry
                }
                actions.append(action)
            
            # Send in bulk
            if actions:
                success, failed = bulk(
                    es_client,
                    actions,
                    chunk_size=es_config.bulk_size,
                    request_timeout=es_config.request_timeout,
                    max_retries=self.max_retries,
                    initial_backoff=2,
                    max_backoff=600
                )
                
                if failed:
                    logging.error(f"Failed to index {len(failed)} log entries to Elasticsearch")
        
        except Exception as e:
            logging.error(f"Elasticsearch bulk indexing failed: {e}")
            raise
    
    def _get_elasticsearch_index_name(self, log_entry: Dict[str, Any]) -> str:
        """Generate Elasticsearch index name based on strategy"""
        es_config = self.elasticsearch_config
        strategy = es_config.indexing_strategy
        
        # Get timestamp
        timestamp = log_entry.get("@timestamp") or log_entry.get("timestamp")
        if timestamp:
            if isinstance(timestamp, str):
                dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
            else:
                dt = timestamp
        else:
            dt = datetime.now(timezone.utc)
        
        if strategy == IndexingStrategy.DAILY:
            date_suffix = dt.strftime("%Y.%m.%d")
        elif strategy == IndexingStrategy.WEEKLY:
            year, week, _ = dt.isocalendar()
            date_suffix = f"{year}.W{week:02d}"
        elif strategy == IndexingStrategy.MONTHLY:
            date_suffix = dt.strftime("%Y.%m")
        elif strategy == IndexingStrategy.BY_LOG_LEVEL:
            level = log_entry.get("level", "info").lower()
            date_suffix = f"{dt.strftime('%Y.%m.%d')}-{level}"
        elif strategy == IndexingStrategy.BY_COMPONENT:
            component = log_entry.get("logger", "unknown").replace("ia_influencer_", "")
            date_suffix = f"{dt.strftime('%Y.%m.%d')}-{component}"
        else:
            date_suffix = dt.strftime("%Y.%m.%d")
        
        return es_config.index_pattern.replace("{date}", date_suffix)
    
    def _send_to_kafka(self, log_entries: List[Dict[str, Any]]) -> None:
        """Send log entries to Kafka"""



        try:
            producer = self._backend_clients["kafka_producer"]
            topic = self.kafka_config.topic
            
            for entry in log_entries:
                # Use correlation_id or request_id as key for partitioning
                key = entry.get("correlation_id") or entry.get("request_id")
                if key:
                    key = key.encode('utf-8')
                
                producer.send(topic, value=entry, key=key)
            
            # Ensure all messages are sent
            producer.flush()
            
        except Exception as e:
            logging.error(f"Failed to send logs to Kafka: {e}")
            raise
    
    def _send_to_redis_streams(self, log_entries: List[Dict[str, Any]]) -> None:
        """Send log entries to Redis Streams"""



        try:
            redis_client = self._backend_clients["redis"]
            redis_config = self.redis_config
            
            pipe = redis_client.pipeline()
            
            for entry in log_entries:
                pipe.xadd(
                    redis_config.stream_name,
                    entry,
                    maxlen=redis_config.max_stream_length,
                    approximate=True
                )
            
            pipe.execute()
            
        except Exception as e:
            logging.error(f"Failed to send logs to Redis Streams: {e}")
            raise
    
    def _send_to_fluentd(self, log_entries: List[Dict[str, Any]]) -> None:
        """Send log entries to Fluentd"""



        try:
            fluentd_client = self._backend_clients["fluentd"]
            
            for entry in log_entries:
                # Extract timestamp
                timestamp = entry.get("@timestamp") or entry.get("timestamp")
                if timestamp and isinstance(timestamp, str):
                    dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                    timestamp = int(dt.timestamp())
                
                fluentd_client.emit_with_time(
                    "log",
                    timestamp or int(time.time()),
                    entry
                )
            
        except Exception as e:
            logging.error(f"Failed to send logs to Fluentd: {e}")
            raise
    
    def _send_metrics_to_elasticsearch(self, metrics: Dict[str, Any]) -> None:
        """Send metrics to Elasticsearch"""



        try:
            es_client = self._backend_clients["elasticsearch"]
            
            index_name = f"ia-influencer-metrics-{datetime.now().strftime('%Y.%m.%d')}"
            
            es_client.index(
                index=index_name,
                body=metrics
            )
            
        except Exception as e:
            logging.error(f"Failed to send metrics to Elasticsearch: {e}")
    
    async def send_log_async(self, log_entry: Dict[str, Any]) -> None:
        """
        Send a log entry asynchronously.
        
        Args:
            log_entry: Log entry to send
        """



        try:
            # Enrich log entry
            enriched_entry = self._enrich_log_entry(log_entry)
            
            # Apply custom processors
            for processor in self.custom_processors:
                enriched_entry = processor(enriched_entry)
            
            # Send to async backends
            await self._send_logs_to_backends_async([enriched_entry])
            
        except Exception as e:
            logging.error(f"Failed to send log entry async: {e}")
    
    async def _send_logs_to_backends_async(self, log_entries: List[Dict[str, Any]]) -> None:
        """Send log entries to backends asynchronously"""
        tasks = []
        
        for backend in self.backends:
            if backend == AggregationBackend.ELASTICSEARCH:
                tasks.append(self._send_to_elasticsearch_async(log_entries))
            # Add other async backends as needed
        
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)
    
    async def _send_to_elasticsearch_async(self, log_entries: List[Dict[str, Any]]) -> None:
        """Send log entries to Elasticsearch asynchronously"""



        try:
            es_client = self._backend_clients["elasticsearch_async"]
            es_config = self.elasticsearch_config
            
            # Prepare bulk actions
            actions = []
            for entry in log_entries:
                index_name = self._get_elasticsearch_index_name(entry)
                action = {
                    "_index": index_name,
                    "_source": entry
                }
                actions.append(action)
            
            # Send in bulk
            if actions:
                success, failed = await async_bulk(
                    es_client,
                    actions,
                    chunk_size=es_config.bulk_size,
                    request_timeout=es_config.request_timeout,
                    max_retries=self.max_retries
                )
                
                if failed:
                    logging.error(f"Failed to index {len(failed)} log entries to Elasticsearch async")
        
        except Exception as e:
            logging.error(f"Elasticsearch async bulk indexing failed: {e}")
            raise
    
    def flush(self) -> None:
        """Force flush all buffered logs"""



        try:
            # Get all remaining logs from buffer
            logs_to_send = []
            
            while not self._log_buffer.empty():
                try:
                    log_entry = self._log_buffer.get_nowait()
                    logs_to_send.append(log_entry)
                except queue.Empty:
                    break
            
            # Send logs if we have any
            if logs_to_send:
                self._send_logs_to_backends(logs_to_send)
            
            # Flush backend clients
            for client in self._backend_clients.values():
                if hasattr(client, 'flush'):
                    client.flush()
            
        except Exception as e:
            logging.error(f"Failed to flush logs: {e}")
    
    def stop(self) -> None:
        """Stop log aggregation and cleanup resources"""



        try:
            # Signal stop to background threads
            self._stop_event.set()
            
            # Flush remaining logs
            self.flush()
            
            # Wait for threads to finish
            if hasattr(self, '_flush_thread'):
                self._flush_thread.join(timeout=30)
            
            if hasattr(self, '_metrics_thread'):
                self._metrics_thread.join(timeout=10)
            
            # Close backend clients
            for name, client in self._backend_clients.items():
                try:
                    if hasattr(client, 'close'):
                        client.close()
                    elif hasattr(client, 'stop'):
                        client.stop()
                except Exception as e:
                    logging.error(f"Error closing {name} client: {e}")
            
            logging.info("Log aggregation stopped")
            
        except Exception as e:
            logging.error(f"Error stopping log aggregation: {e}")
    
    def get_aggregation_status(self) -> Dict[str, Any]:
        """Get current aggregation status"""



        return {
            "enabled": True,
            "backends": [backend.value for backend in self.backends],
            "streaming_mode": self.streaming_mode.value,
            "buffer_size": self._log_buffer.qsize(),
            "max_buffer_size": self.buffer_size,
            "flush_interval": self.flush_interval,
            "active_backends": len(self._backend_clients),
            "enable_tracing": self.enable_tracing,
            "enable_metrics": self.enable_metrics,
            "threads_running": {
                "flush_thread": hasattr(self, '_flush_thread') and self._flush_thread.is_alive(),
                "metrics_thread": hasattr(self, '_metrics_thread') and self._metrics_thread.is_alive()
            }
        }


class ElasticsearchHandler(logging.Handler):
    """Custom logging handler for Elasticsearch integration"""
    
    def __init__(self, aggregation_config: LogAggregationConfig):
        super().__init__()
        self.aggregation_config = aggregation_config
    
    def emit(self, record: logging.LogRecord) -> None:
        """Emit a log record to Elasticsearch"""



        try:
            # Convert log record to dictionary
            log_entry = {
                "timestamp": datetime.fromtimestamp(record.created, timezone.utc).isoformat(),
                "level": record.levelname,
                "logger": record.name,
                "message": record.getMessage(),
                "module": record.module,
                "function": record.funcName,
                "line": record.lineno,
                "thread": record.thread,
                "process": record.process
            }
            
            # Add exception information
            if record.exc_info:
                log_entry["exception"] = self.format(record)
            
            # Send to aggregation config
            self.aggregation_config.send_log(log_entry)
            
        except Exception:
            self.handleError(record)


# Global log aggregation configuration instance
_aggregation_config: Optional[LogAggregationConfig] = None


def initialize_log_aggregation(
    config: Optional[LogAggregationConfig] = None
) -> LogAggregationConfig:
    """
    Initialize global log aggregation configuration.
    
    Args:
        config: Custom LogAggregationConfig instance
        
    Returns:
        Initialized log aggregation configuration
    """
    global _aggregation_config
    
    if config:
        _aggregation_config = config
    else:
        _aggregation_config = LogAggregationConfig()
    
    return _aggregation_config


def get_aggregation_config() -> LogAggregationConfig:
    """Get the global log aggregation configuration"""
    if not _aggregation_config:
        initialize_log_aggregation()
    
    return _aggregation_config


def send_log(log_entry: Dict[str, Any]) -> None:
    """
    Send a log entry using global aggregation configuration.
    
    Args:
        log_entry: Log entry to send
    """
    config = get_aggregation_config()
    config.send_log(log_entry)
