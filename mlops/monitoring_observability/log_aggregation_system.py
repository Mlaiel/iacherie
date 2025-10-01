#!/usr/bin/env python3
"""
📚 Log Aggregation System - Enterprise MLOps Platform
ELK Stack integrated log aggregation for Creator Economy microservices
Lead Dev IA + Backend Senior + ML Engineer + DBA + Security + Microservices + Audio + DevOps

⚠️  PROPRIETARY SOFTWARE - COPYRIGHT NOTICE
==========================================
© 2025 Fahed Mlaiel <mlaiel@live.de>
ALL RIGHTS RESERVED

🚨 INTELLECTUAL PROPERTY PROTECTION:
- Proprietary code owned by Fahed Mlaiel
- Commercial use PROHIBITED without written authorization
- Reverse engineering STRICTLY FORBIDDEN
- Distribution PROHIBITED without explicit license
- Violations will result in immediate legal prosecution

🏢 ENTERPRISE USAGE:
- Enterprise license available on request
- Technical support included with license
- Maintenance and updates provided
- Team training included

Logique métier iacherie: Créateurs multi-format → IA processing → Protection → 
Monétisation → Collaboration & Gamification → SEO → Distribution
"""

import asyncio
import logging
import json
import time
import threading
import gzip
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union, Callable, TextIO
from dataclasses import dataclass, field
from enum import Enum
from collections import defaultdict, deque
from pathlib import Path
import warnings
import re

# Suppress non-critical warnings
warnings.filterwarnings('ignore', category=UserWarning)
warnings.filterwarnings('ignore', category=FutureWarning)

# Configure enterprise logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

# Optional ELK Stack dependencies
try:
    from elasticsearch import Elasticsearch
    from elasticsearch.helpers import bulk
    ELASTICSEARCH_AVAILABLE = True
    logger.info("✅ Elasticsearch client available")
except ImportError:
    logger.warning("⚠️  Elasticsearch not available. Log aggregation will use fallback.")
    ELASTICSEARCH_AVAILABLE = False
    
    # Mock Elasticsearch for fallback
    class Elasticsearch:
        def __init__(self, *args, **kwargs):
            pass
        def index(self, *args, **kwargs):
            return {"result": "created"}
        def search(self, *args, **kwargs):
            return {"hits": {"hits": []}}
        def indices(self):
            return MockIndices()
    
    class MockIndices:
        def create(self, *args, **kwargs):
            return {"acknowledged": True}
        def exists(self, *args, **kwargs):
            return False

# Creator Economy types
class CreatorType(Enum):
    MUSICIAN = "musician"
    BLOGGER = "blogger"
    PHOTOGRAPHER = "photographer"
    INFLUENCER = "influencer"
    COMEDIAN = "comedian"
    ALL = "all"

class LogLevel(Enum):
    """Niveaux de log"""
    DEBUG = "debug"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"

class LogCategory(Enum):
    """Catégories de logs"""
    APPLICATION = "application"
    SECURITY = "security"
    PERFORMANCE = "performance"
    BUSINESS = "business"
    ML_MODEL = "ml_model"
    CREATOR_ACTIVITY = "creator_activity"
    SYSTEM = "system"
    AUDIT = "audit"
    ERROR = "error"
    ACCESS = "access"

class LogFormat(Enum):
    """Formats de log"""
    JSON = "json"
    STRUCTURED = "structured"
    PLAIN_TEXT = "plain_text"
    ELK = "elk"

@dataclass
class LogEntry:
    """Entrée de log structurée"""
    timestamp: datetime
    level: LogLevel
    message: str
    category: LogCategory
    service_name: str
    
    # Context information
    creator_type: Optional[CreatorType] = None
    creator_id: Optional[str] = None
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    request_id: Optional[str] = None
    trace_id: Optional[str] = None
    
    # Technical details
    hostname: Optional[str] = None
    process_id: Optional[int] = None
    thread_id: Optional[int] = None
    
    # Custom fields
    tags: Dict[str, str] = field(default_factory=dict)
    fields: Dict[str, Any] = field(default_factory=dict)
    
    # Error details (if applicable)
    error_type: Optional[str] = None
    error_stack: Optional[str] = None
    
    # Performance metrics (if applicable)
    duration_ms: Optional[float] = None
    memory_mb: Optional[float] = None
    cpu_percent: Optional[float] = None

@dataclass
class AggregationConfig:
    """Configuration de l'agrégation de logs"""
    service_name: str
    environment: str = "production"
    
    # Elasticsearch configuration
    elasticsearch_hosts: List[str] = field(default_factory=lambda: ["localhost:9200"])
    elasticsearch_index_prefix: str = "iacherie-logs"
    elasticsearch_enabled: bool = True
    
    # File output configuration
    file_output_enabled: bool = True
    log_directory: str = "/var/log/iacherie"
    max_file_size_mb: int = 100
    max_files_per_service: int = 10
    compress_old_files: bool = True
    
    # Buffer and performance
    buffer_size: int = 10000
    flush_interval_seconds: int = 5
    batch_size: int = 1000
    max_workers: int = 4
    
    # Security and compliance
    pii_scrubbing_enabled: bool = True
    log_encryption_enabled: bool = False
    audit_trail_enabled: bool = True
    
    # Retention policies
    retention_days: int = 30
    hot_data_days: int = 7  # Keep in fast storage
    archive_enabled: bool = True
    
    # Filtering and sampling
    log_level_filter: LogLevel = LogLevel.INFO
    sampling_rate: float = 1.0  # 100% sampling
    max_message_length: int = 10000

@dataclass
class LogQuery:
    """Requête de recherche de logs"""
    query: str
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    level: Optional[LogLevel] = None
    category: Optional[LogCategory] = None
    service_name: Optional[str] = None
    creator_type: Optional[CreatorType] = None
    creator_id: Optional[str] = None
    user_id: Optional[str] = None
    limit: int = 100
    offset: int = 0

class LogAggregationSystem:
    """
    📚 Système d'agrégation de logs enterprise
    
    Expertise combinée:
    - Lead Dev IA: Analytics et pattern recognition dans les logs
    - Backend Senior: Architecture haute performance et scalabilité
    - ML Engineer: Logs des modèles ML et monitoring performance
    - DBA: Optimisation stockage et indexation logs
    - Sécurité: Protection PII, audit trails et compliance
    - Microservices: Agrégation cross-service et corrélation
    - Audio: Logs spécialisés traitement multimédia
    - DevOps: Infrastructure logging et monitoring production
    """
    
    def __init__(
        self,
        config: AggregationConfig,
        creator_type: Optional[CreatorType] = None
    ):
        """
        Initialise le système d'agrégation de logs
        
        Args:
            config: Configuration de l'agrégation
            creator_type: Type de créateur pour les logs spécialisés
        """
        self.config = config
        self.creator_type = creator_type
        
        # État du système
        self.system_state = {
            "initialized": False,
            "running": False,
            "logs_received": 0,
            "logs_processed": 0,
            "logs_indexed": 0,
            "errors_count": 0,
            "last_flush": None,
            "buffer_usage": 0.0
        }
        
        # Buffers et stockage
        self.log_buffer = deque(maxlen=config.buffer_size)
        self.logs_by_category = defaultdict(deque)
        self.recent_errors = deque(maxlen=100)
        
        # Threading et async
        self.executor = None
        self.aggregation_thread: Optional[threading.Thread] = None
        self.flush_thread: Optional[threading.Thread] = None
        self.stop_event = threading.Event()
        
        # Elasticsearch client
        self.elasticsearch_client = None
        
        # File handlers
        self.file_handlers: Dict[str, TextIO] = {}
        
        # Performance metrics
        self.performance_metrics = {
            "ingestion_latency_ms": deque(maxlen=1000),
            "processing_latency_ms": deque(maxlen=1000),
            "indexing_latency_ms": deque(maxlen=1000),
            "flush_latency_ms": deque(maxlen=100)
        }
        
        # PII scrubbing patterns
        self.pii_patterns = [
            (r'\b\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}\b', '****-****-****-****'),  # Credit cards
            (r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', '***@***.***'),  # Email
            (r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b', '***-***-****'),  # Phone numbers
            (r'\b\d{3}[-]?\d{2}[-]?\d{4}\b', '***-**-****'),  # SSN
        ]
        
        # Copyright protection
        self._display_copyright_notice()
        
        # Initialize system
        self._initialize_system()
        
        logger.info(f"📚 LogAggregationSystem initialized")
        logger.info(f"🏷️  Service: {config.service_name}")
        logger.info(f"👤 Creator: {creator_type.value if creator_type else 'All'}")
        logger.info(f"📊 Buffer size: {config.buffer_size}")
    
    def _display_copyright_notice(self):
        """Afficher la notice de protection des droits d'auteur"""
        logger.info("="*80)
        logger.info("📚 Log Aggregation System - Enterprise MLOps")
        logger.info("🔒 PROPRIETARY SOFTWARE - Fahed Mlaiel (mlaiel@live.de)")
        logger.info("⚠️  Unauthorized use, reproduction, or distribution is prohibited")
        logger.info("="*80)
    
    def _initialize_system(self):
        """Initialise le système d'agrégation"""
        try:
            # Initialize Elasticsearch if enabled
            if self.config.elasticsearch_enabled:
                self._initialize_elasticsearch()
            
            # Initialize file output if enabled
            if self.config.file_output_enabled:
                self._initialize_file_output()
            
            # Initialize processing threads
            self._initialize_processing_threads()
            
            self.system_state["initialized"] = True
            logger.info("✅ Log aggregation system initialized")
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize log aggregation system: {e}")
            self.system_state["errors_count"] += 1
    
    def _initialize_elasticsearch(self):
        """Initialise Elasticsearch"""
        try:
            if ELASTICSEARCH_AVAILABLE:
                self.elasticsearch_client = Elasticsearch(
                    hosts=self.config.elasticsearch_hosts,
                    timeout=30,
                    max_retries=3,
                    retry_on_timeout=True
                )
                
                # Create index template
                self._create_elasticsearch_template()
                
                logger.info("✅ Elasticsearch client initialized")
            else:
                logger.warning("⚠️  Using mock Elasticsearch client")
                self.elasticsearch_client = Elasticsearch()
                
        except Exception as e:
            logger.error(f"❌ Failed to initialize Elasticsearch: {e}")
            self.elasticsearch_client = None
    
    def _create_elasticsearch_template(self):
        """Crée le template d'index Elasticsearch"""
        try:
            template_name = f"{self.config.elasticsearch_index_prefix}-template"
            
            template = {
                "index_patterns": [f"{self.config.elasticsearch_index_prefix}-*"],
                "settings": {
                    "number_of_shards": 3,
                    "number_of_replicas": 1,
                    "index.lifecycle.name": "logs-policy",
                    "index.lifecycle.rollover_alias": f"{self.config.elasticsearch_index_prefix}-write"
                },
                "mappings": {
                    "properties": {
                        "@timestamp": {"type": "date"},
                        "level": {"type": "keyword"},
                        "message": {"type": "text", "analyzer": "standard"},
                        "category": {"type": "keyword"},
                        "service_name": {"type": "keyword"},
                        "creator_type": {"type": "keyword"},
                        "creator_id": {"type": "keyword"},
                        "user_id": {"type": "keyword"},
                        "session_id": {"type": "keyword"},
                        "request_id": {"type": "keyword"},
                        "trace_id": {"type": "keyword"},
                        "hostname": {"type": "keyword"},
                        "process_id": {"type": "integer"},
                        "thread_id": {"type": "integer"},
                        "tags": {"type": "object"},
                        "fields": {"type": "object"},
                        "error_type": {"type": "keyword"},
                        "error_stack": {"type": "text"},
                        "duration_ms": {"type": "float"},
                        "memory_mb": {"type": "float"},
                        "cpu_percent": {"type": "float"}
                    }
                }
            }
            
            # Create template (this will work with mock client too)
            response = self.elasticsearch_client.indices.put_template(
                name=template_name,
                body=template
            )
            
            logger.info(f"✅ Elasticsearch template created: {template_name}")
            
        except Exception as e:
            logger.error(f"❌ Failed to create Elasticsearch template: {e}")
    
    def _initialize_file_output(self):
        """Initialise la sortie fichier"""
        try:
            # Create log directory
            Path(self.config.log_directory).mkdir(parents=True, exist_ok=True)
            
            # Initialize log file handlers will be created on demand
            logger.info(f"✅ File output initialized: {self.config.log_directory}")
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize file output: {e}")
    
    def _initialize_processing_threads(self):
        """Initialise les threads de traitement"""
        try:
            from concurrent.futures import ThreadPoolExecutor
            self.executor = ThreadPoolExecutor(max_workers=self.config.max_workers)
            
            logger.info(f"✅ Processing threads initialized: {self.config.max_workers} workers")
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize processing threads: {e}")
    
    def start_aggregation(self) -> bool:
        """Démarre l'agrégation de logs"""
        try:
            if not self.system_state["initialized"]:
                logger.error("❌ Cannot start aggregation - system not initialized")
                return False
            
            if self.system_state["running"]:
                logger.warning("⚠️  Log aggregation already running")
                return True
            
            self.system_state["running"] = True
            self.stop_event.clear()
            
            # Start aggregation thread
            self.aggregation_thread = threading.Thread(
                target=self._aggregation_loop,
                daemon=True
            )
            self.aggregation_thread.start()
            
            # Start flush thread
            self.flush_thread = threading.Thread(
                target=self._flush_loop,
                daemon=True
            )
            self.flush_thread.start()
            
            logger.info("🚀 Log aggregation started")
            logger.info(f"🔄 Flush interval: {self.config.flush_interval_seconds}s")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to start log aggregation: {e}")
            self.system_state["errors_count"] += 1
            return False
    
    def stop_aggregation(self):
        """Arrête l'agrégation de logs"""
        try:
            logger.info("⏹️  Stopping log aggregation...")
            
            self.system_state["running"] = False
            self.stop_event.set()
            
            # Wait for threads to finish
            if self.aggregation_thread and self.aggregation_thread.is_alive():
                self.aggregation_thread.join(timeout=10.0)
            
            if self.flush_thread and self.flush_thread.is_alive():
                self.flush_thread.join(timeout=10.0)
            
            # Final flush
            self._flush_logs()
            
            # Close file handlers
            self._close_file_handlers()
            
            # Shutdown executor
            if self.executor:
                self.executor.shutdown(wait=True)
            
            logger.info("🛑 Log aggregation stopped")
            
        except Exception as e:
            logger.error(f"❌ Error stopping log aggregation: {e}")
    
    def ingest_log(
        self,
        level: Union[LogLevel, str],
        message: str,
        category: Union[LogCategory, str] = LogCategory.APPLICATION,
        **kwargs
    ) -> bool:
        """
        Ingère un log dans le système
        
        Args:
            level: Niveau de log
            message: Message de log
            category: Catégorie de log
            **kwargs: Champs additionnels
        
        Returns:
            bool: True si le log a été ingéré avec succès
        """
        try:
            start_time = time.time()
            
            # Convert string enums
            if isinstance(level, str):
                level = LogLevel(level.lower())
            if isinstance(category, str):
                category = LogCategory(category.lower())
            
            # Check level filter
            if self._should_filter_level(level):
                return True  # Filtered out, but not an error
            
            # Apply sampling
            if not self._should_sample():
                return True  # Sampled out, but not an error
            
            # Scrub PII if enabled
            if self.config.pii_scrubbing_enabled:
                message = self._scrub_pii(message)
            
            # Truncate message if too long
            if len(message) > self.config.max_message_length:
                message = message[:self.config.max_message_length] + "... [TRUNCATED]"
            
            # Create log entry
            log_entry = LogEntry(
                timestamp=datetime.now(),
                level=level,
                message=message,
                category=category,
                service_name=self.config.service_name,
                creator_type=self.creator_type,
                hostname=kwargs.get('hostname'),
                process_id=kwargs.get('process_id', os.getpid()),
                thread_id=kwargs.get('thread_id', threading.get_ident()),
                creator_id=kwargs.get('creator_id'),
                user_id=kwargs.get('user_id'),
                session_id=kwargs.get('session_id'),
                request_id=kwargs.get('request_id'),
                trace_id=kwargs.get('trace_id'),
                tags=kwargs.get('tags', {}),
                fields=kwargs.get('fields', {}),
                error_type=kwargs.get('error_type'),
                error_stack=kwargs.get('error_stack'),
                duration_ms=kwargs.get('duration_ms'),
                memory_mb=kwargs.get('memory_mb'),
                cpu_percent=kwargs.get('cpu_percent')
            )
            
            # Add to buffer
            self.log_buffer.append(log_entry)
            
            # Add to category-specific buffer
            self.logs_by_category[category].append(log_entry)
            
            # Track error logs separately
            if level in [LogLevel.ERROR, LogLevel.CRITICAL]:
                self.recent_errors.append(log_entry)
            
            # Update state
            self.system_state["logs_received"] += 1
            self.system_state["buffer_usage"] = len(self.log_buffer) / self.config.buffer_size
            
            # Track performance
            ingestion_time = (time.time() - start_time) * 1000
            self.performance_metrics["ingestion_latency_ms"].append(ingestion_time)
            
            logger.debug(f"📚 Ingested log: {level.value} - {message[:100]}...")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error ingesting log: {e}")
            self.system_state["errors_count"] += 1
            return False
    
    def _should_filter_level(self, level: LogLevel) -> bool:
        """Vérifie si le niveau de log doit être filtré"""
        level_priorities = {
            LogLevel.DEBUG: 0,
            LogLevel.INFO: 1,
            LogLevel.WARNING: 2,
            LogLevel.ERROR: 3,
            LogLevel.CRITICAL: 4
        }
        
        return level_priorities[level] < level_priorities[self.config.log_level_filter]
    
    def _should_sample(self) -> bool:
        """Vérifie si le log doit être échantillonné"""
        import random
        return random.random() < self.config.sampling_rate
    
    def _scrub_pii(self, message: str) -> str:
        """Supprime les informations personnelles du message"""
        try:
            scrubbed = message
            
            for pattern, replacement in self.pii_patterns:
                scrubbed = re.sub(pattern, replacement, scrubbed)
            
            return scrubbed
            
        except Exception as e:
            logger.error(f"❌ Error scrubbing PII: {e}")
            return message  # Return original if scrubbing fails
    
    def _aggregation_loop(self):
        """Boucle principale d'agrégation"""
        logger.info("🔄 Starting log aggregation loop...")
        
        while not self.stop_event.is_set():
            try:
                start_time = time.time()
                
                # Process log buffer
                if self.log_buffer:
                    self._process_log_buffer()
                
                # Track processing performance
                processing_time = (time.time() - start_time) * 1000
                self.performance_metrics["processing_latency_ms"].append(processing_time)
                
                # Sleep briefly to avoid high CPU usage
                time.sleep(0.1)
                
            except Exception as e:
                logger.error(f"❌ Error in aggregation loop: {e}")
                self.system_state["errors_count"] += 1
                time.sleep(1)  # Error recovery delay
    
    def _process_log_buffer(self):
        """Traite le buffer de logs"""
        try:
            batch_size = min(len(self.log_buffer), self.config.batch_size)
            
            if batch_size == 0:
                return
            
            # Extract batch from buffer
            batch = []
            for _ in range(batch_size):
                if self.log_buffer:
                    batch.append(self.log_buffer.popleft())
            
            # Process batch
            if batch:
                self._process_log_batch(batch)
                self.system_state["logs_processed"] += len(batch)
            
        except Exception as e:
            logger.error(f"❌ Error processing log buffer: {e}")
            self.system_state["errors_count"] += 1
    
    def _process_log_batch(self, batch: List[LogEntry]):
        """Traite un batch de logs"""
        try:
            # Submit to different outputs concurrently
            futures = []
            
            if self.config.elasticsearch_enabled and self.elasticsearch_client:
                future = self.executor.submit(self._index_to_elasticsearch, batch)
                futures.append(future)
            
            if self.config.file_output_enabled:
                future = self.executor.submit(self._write_to_files, batch)
                futures.append(future)
            
            # Wait for all outputs to complete
            for future in futures:
                try:
                    future.result(timeout=10)  # 10 second timeout
                except Exception as e:
                    logger.error(f"❌ Error in batch processing: {e}")
                    self.system_state["errors_count"] += 1
            
            logger.debug(f"📚 Processed batch of {len(batch)} logs")
            
        except Exception as e:
            logger.error(f"❌ Error processing log batch: {e}")
    
    def _index_to_elasticsearch(self, batch: List[LogEntry]):
        """Indexe un batch de logs dans Elasticsearch"""
        try:
            start_time = time.time()
            
            # Prepare documents for bulk indexing
            docs = []
            
            for log_entry in batch:
                # Generate index name with date rotation
                index_name = f"{self.config.elasticsearch_index_prefix}-{log_entry.timestamp.strftime('%Y.%m.%d')}"
                
                doc = {
                    "_index": index_name,
                    "_source": {
                        "@timestamp": log_entry.timestamp.isoformat(),
                        "level": log_entry.level.value,
                        "message": log_entry.message,
                        "category": log_entry.category.value,
                        "service_name": log_entry.service_name,
                        "creator_type": log_entry.creator_type.value if log_entry.creator_type else None,
                        "creator_id": log_entry.creator_id,
                        "user_id": log_entry.user_id,
                        "session_id": log_entry.session_id,
                        "request_id": log_entry.request_id,
                        "trace_id": log_entry.trace_id,
                        "hostname": log_entry.hostname,
                        "process_id": log_entry.process_id,
                        "thread_id": log_entry.thread_id,
                        "tags": log_entry.tags,
                        "fields": log_entry.fields,
                        "error_type": log_entry.error_type,
                        "error_stack": log_entry.error_stack,
                        "duration_ms": log_entry.duration_ms,
                        "memory_mb": log_entry.memory_mb,
                        "cpu_percent": log_entry.cpu_percent
                    }
                }
                docs.append(doc)
            
            # Bulk index (mock for fallback)
            if ELASTICSEARCH_AVAILABLE:
                success_count, failed_items = bulk(
                    self.elasticsearch_client,
                    docs,
                    chunk_size=500,
                    request_timeout=60
                )
                
                if failed_items:
                    logger.warning(f"⚠️  {len(failed_items)} documents failed to index")
                    
            else:
                # Mock bulk indexing
                success_count = len(docs)
            
            # Track performance
            indexing_time = (time.time() - start_time) * 1000
            self.performance_metrics["indexing_latency_ms"].append(indexing_time)
            
            self.system_state["logs_indexed"] += success_count
            
            logger.debug(f"📊 Indexed {success_count} logs to Elasticsearch in {indexing_time:.2f}ms")
            
        except Exception as e:
            logger.error(f"❌ Error indexing to Elasticsearch: {e}")
            self.system_state["errors_count"] += 1
    
    def _write_to_files(self, batch: List[LogEntry]):
        """Écrit un batch de logs dans des fichiers"""
        try:
            # Group logs by category for separate files
            logs_by_category = defaultdict(list)
            
            for log_entry in batch:
                logs_by_category[log_entry.category].append(log_entry)
            
            # Write to category-specific files
            for category, logs in logs_by_category.items():
                self._write_category_logs(category, logs)
            
        except Exception as e:
            logger.error(f"❌ Error writing to files: {e}")
            self.system_state["errors_count"] += 1
    
    def _write_category_logs(self, category: LogCategory, logs: List[LogEntry]):
        """Écrit les logs d'une catégorie dans un fichier"""
        try:
            # Generate filename
            date_str = datetime.now().strftime('%Y-%m-%d')
            filename = f"{self.config.service_name}-{category.value}-{date_str}.log"
            filepath = os.path.join(self.config.log_directory, filename)
            
            # Get or create file handler
            if filepath not in self.file_handlers:
                self.file_handlers[filepath] = open(filepath, 'a', encoding='utf-8')
            
            file_handler = self.file_handlers[filepath]
            
            # Write logs
            for log_entry in logs:
                log_line = self._format_log_entry(log_entry)
                file_handler.write(log_line + '\n')
            
            # Flush immediately for critical logs
            if any(log.level == LogLevel.CRITICAL for log in logs):
                file_handler.flush()
            
            # Check file size and rotate if needed
            self._check_file_rotation(filepath)
            
        except Exception as e:
            logger.error(f"❌ Error writing category logs: {e}")
    
    def _format_log_entry(self, log_entry: LogEntry) -> str:
        """Formate une entrée de log"""
        try:
            if self.config.elasticsearch_enabled:  # Use JSON format
                return json.dumps({
                    "timestamp": log_entry.timestamp.isoformat(),
                    "level": log_entry.level.value,
                    "message": log_entry.message,
                    "category": log_entry.category.value,
                    "service_name": log_entry.service_name,
                    "creator_type": log_entry.creator_type.value if log_entry.creator_type else None,
                    "creator_id": log_entry.creator_id,
                    "user_id": log_entry.user_id,
                    "session_id": log_entry.session_id,
                    "request_id": log_entry.request_id,
                    "trace_id": log_entry.trace_id,
                    "hostname": log_entry.hostname,
                    "process_id": log_entry.process_id,
                    "thread_id": log_entry.thread_id,
                    "tags": log_entry.tags,
                    "fields": log_entry.fields,
                    "error_type": log_entry.error_type,
                    "error_stack": log_entry.error_stack,
                    "duration_ms": log_entry.duration_ms,
                    "memory_mb": log_entry.memory_mb,
                    "cpu_percent": log_entry.cpu_percent
                }, separators=(',', ':'))
            else:  # Use structured text format
                return (f"{log_entry.timestamp.isoformat()} "
                       f"[{log_entry.level.value.upper()}] "
                       f"{log_entry.service_name} "
                       f"({log_entry.category.value}) "
                       f"- {log_entry.message}")
                
        except Exception as e:
            logger.error(f"❌ Error formatting log entry: {e}")
            return f"{log_entry.timestamp.isoformat()} [ERROR] Failed to format log: {e}"
    
    def _check_file_rotation(self, filepath: str):
        """Vérifie et effectue la rotation des fichiers si nécessaire"""
        try:
            if os.path.getsize(filepath) > self.config.max_file_size_mb * 1024 * 1024:
                # Close current handler
                if filepath in self.file_handlers:
                    self.file_handlers[filepath].close()
                    del self.file_handlers[filepath]
                
                # Rotate file
                timestamp = datetime.now().strftime('%H%M%S')
                rotated_name = f"{filepath}.{timestamp}"
                
                os.rename(filepath, rotated_name)
                
                # Compress old file if enabled
                if self.config.compress_old_files:
                    self._compress_file(rotated_name)
                
                logger.info(f"🔄 Rotated log file: {filepath}")
                
        except Exception as e:
            logger.error(f"❌ Error checking file rotation: {e}")
    
    def _compress_file(self, filepath: str):
        """Compresse un fichier de log"""
        try:
            compressed_path = f"{filepath}.gz"
            
            with open(filepath, 'rb') as f_in:
                with gzip.open(compressed_path, 'wb') as f_out:
                    f_out.writelines(f_in)
            
            # Remove original file
            os.remove(filepath)
            
            logger.debug(f"📦 Compressed log file: {compressed_path}")
            
        except Exception as e:
            logger.error(f"❌ Error compressing file: {e}")
    
    def _flush_loop(self):
        """Boucle de flush périodique"""
        logger.info("🔄 Starting log flush loop...")
        
        while not self.stop_event.is_set():
            try:
                # Wait for flush interval
                if self.stop_event.wait(self.config.flush_interval_seconds):
                    break  # Stop event was set
                
                # Perform flush
                self._flush_logs()
                
            except Exception as e:
                logger.error(f"❌ Error in flush loop: {e}")
                self.system_state["errors_count"] += 1
                time.sleep(1)  # Error recovery delay
    
    def _flush_logs(self):
        """Flush les logs vers le stockage"""
        try:
            start_time = time.time()
            
            # Flush file handlers
            for file_handler in self.file_handlers.values():
                file_handler.flush()
            
            # Track flush performance
            flush_time = (time.time() - start_time) * 1000
            self.performance_metrics["flush_latency_ms"].append(flush_time)
            
            self.system_state["last_flush"] = datetime.now()
            
            logger.debug(f"📚 Flushed logs in {flush_time:.2f}ms")
            
        except Exception as e:
            logger.error(f"❌ Error flushing logs: {e}")
    
    def _close_file_handlers(self):
        """Ferme tous les gestionnaires de fichier"""
        try:
            for filepath, handler in self.file_handlers.items():
                handler.close()
            
            self.file_handlers.clear()
            logger.info("📚 Closed all file handlers")
            
        except Exception as e:
            logger.error(f"❌ Error closing file handlers: {e}")
    
    # Public API methods
    
    def search_logs(self, query: LogQuery) -> List[Dict[str, Any]]:
        """Recherche des logs selon une requête"""
        try:
            if not self.elasticsearch_client or not ELASTICSEARCH_AVAILABLE:
                return self._search_logs_fallback(query)
            
            # Build Elasticsearch query
            es_query = {
                "query": {
                    "bool": {
                        "must": [],
                        "filter": []
                    }
                },
                "sort": [{"@timestamp": {"order": "desc"}}],
                "size": query.limit,
                "from": query.offset
            }
            
            # Add text search
            if query.query:
                es_query["query"]["bool"]["must"].append({
                    "multi_match": {
                        "query": query.query,
                        "fields": ["message", "error_stack"],
                        "type": "best_fields"
                    }
                })
            
            # Add filters
            if query.start_time and query.end_time:
                es_query["query"]["bool"]["filter"].append({
                    "range": {
                        "@timestamp": {
                            "gte": query.start_time.isoformat(),
                            "lte": query.end_time.isoformat()
                        }
                    }
                })
            
            if query.level:
                es_query["query"]["bool"]["filter"].append({
                    "term": {"level": query.level.value}
                })
            
            if query.category:
                es_query["query"]["bool"]["filter"].append({
                    "term": {"category": query.category.value}
                })
            
            if query.service_name:
                es_query["query"]["bool"]["filter"].append({
                    "term": {"service_name": query.service_name}
                })
            
            if query.creator_type:
                es_query["query"]["bool"]["filter"].append({
                    "term": {"creator_type": query.creator_type.value}
                })
            
            if query.creator_id:
                es_query["query"]["bool"]["filter"].append({
                    "term": {"creator_id": query.creator_id}
                })
            
            if query.user_id:
                es_query["query"]["bool"]["filter"].append({
                    "term": {"user_id": query.user_id}
                })
            
            # Execute search
            index_pattern = f"{self.config.elasticsearch_index_prefix}-*"
            response = self.elasticsearch_client.search(
                index=index_pattern,
                body=es_query
            )
            
            # Extract results
            results = []
            for hit in response["hits"]["hits"]:
                results.append(hit["_source"])
            
            logger.debug(f"📚 Found {len(results)} logs matching query")
            return results
            
        except Exception as e:
            logger.error(f"❌ Error searching logs: {e}")
            return []
    
    def _search_logs_fallback(self, query: LogQuery) -> List[Dict[str, Any]]:
        """Recherche de logs en mode fallback"""
        try:
            # Simple in-memory search on recent logs
            results = []
            
            for trace in self.completed_traces:
                # Simple text matching
                if query.query and query.query.lower() not in trace.get("message", "").lower():
                    continue
                
                # Level filter
                if query.level and trace.get("level") != query.level.value:
                    continue
                
                # Category filter
                if query.category and trace.get("category") != query.category.value:
                    continue
                
                results.append(trace)
            
            # Apply limit and offset
            start_idx = query.offset
            end_idx = start_idx + query.limit
            
            return results[start_idx:end_idx]
            
        except Exception as e:
            logger.error(f"❌ Error in fallback search: {e}")
            return []
    
    def get_system_status(self) -> Dict[str, Any]:
        """Obtient le statut du système d'agrégation"""
        return {
            "state": self.system_state.copy(),
            "config": {
                "service_name": self.config.service_name,
                "environment": self.config.environment,
                "elasticsearch_enabled": self.config.elasticsearch_enabled,
                "file_output_enabled": self.config.file_output_enabled,
                "buffer_size": self.config.buffer_size,
                "flush_interval": self.config.flush_interval_seconds
            },
            "creator_type": self.creator_type.value if self.creator_type else None,
            "buffer_usage_percent": self.system_state["buffer_usage"] * 100,
            "recent_errors_count": len(self.recent_errors),
            "performance": self._get_performance_summary()
        }
    
    def _get_performance_summary(self) -> Dict[str, Any]:
        """Obtient un résumé des performances"""
        try:
            summary = {}
            
            for metric_name, values in self.performance_metrics.items():
                if values:
                    summary[metric_name] = {
                        "count": len(values),
                        "avg": sum(values) / len(values),
                        "min": min(values),
                        "max": max(values),
                        "p95": sorted(values)[int(0.95 * (len(values) - 1))] if len(values) > 1 else values[0]
                    }
                else:
                    summary[metric_name] = {"count": 0}
            
            return summary
            
        except Exception as e:
            logger.error(f"❌ Error generating performance summary: {e}")
            return {}
    
    def get_log_statistics(self, hours_back: int = 1) -> Dict[str, Any]:
        """Obtient les statistiques de logs"""
        try:
            cutoff_time = datetime.now() - timedelta(hours=hours_back)
            
            # This would typically query Elasticsearch for statistics
            # For now, provide basic statistics from system state
            
            statistics = {
                "period_hours": hours_back,
                "total_logs_received": self.system_state["logs_received"],
                "total_logs_processed": self.system_state["logs_processed"],
                "total_logs_indexed": self.system_state["logs_indexed"],
                "error_rate": (self.system_state["errors_count"] / 
                              max(1, self.system_state["logs_received"])),
                "processing_rate": (self.system_state["logs_processed"] / 
                                   max(1, self.system_state["logs_received"])),
                "indexing_rate": (self.system_state["logs_indexed"] / 
                                 max(1, self.system_state["logs_processed"])),
                "recent_errors": len(self.recent_errors),
                "buffer_usage": self.system_state["buffer_usage"],
                "categories": {
                    category.value: len(logs) 
                    for category, logs in self.logs_by_category.items()
                }
            }
            
            return statistics
            
        except Exception as e:
            logger.error(f"❌ Error generating log statistics: {e}")
            return {"error": str(e)}
    
    def export_logs(self, filepath: str, hours_back: int = 24):
        """Exporte les logs vers un fichier"""
        try:
            # For this example, export recent error logs
            export_data = {
                "export_metadata": {
                    "timestamp": datetime.now().isoformat(),
                    "service_name": self.config.service_name,
                    "creator_type": self.creator_type.value if self.creator_type else None,
                    "period_hours": hours_back
                },
                "system_status": self.get_system_status(),
                "log_statistics": self.get_log_statistics(hours_back),
                "recent_errors": [
                    {
                        "timestamp": error.timestamp.isoformat(),
                        "level": error.level.value,
                        "message": error.message,
                        "category": error.category.value,
                        "error_type": error.error_type,
                        "creator_id": error.creator_id,
                        "user_id": error.user_id
                    }
                    for error in list(self.recent_errors)
                ]
            }
            
            with open(filepath, 'w') as f:
                json.dump(export_data, f, indent=2, default=str)
            
            logger.info(f"📚 Logs exported to {filepath}")
            
        except Exception as e:
            logger.error(f"❌ Error exporting logs: {e}")
            raise

# Factory function for easy usage

def create_log_aggregator(
    service_name: str,
    creator_type: str,
    environment: str = "production",
    elasticsearch_hosts: Optional[List[str]] = None,
    log_directory: str = "/tmp/iacherie_logs"
) -> LogAggregationSystem:
    """
    Factory function pour créer un système d'agrégation de logs
    
    Args:
        service_name: Nom du service
        creator_type: Type de créateur
        environment: Environnement
        elasticsearch_hosts: Hosts Elasticsearch
        log_directory: Répertoire des logs
    
    Returns:
        Instance configurée de LogAggregationSystem
    """
    
    # Convert string to enum
    try:
        creator_enum = CreatorType(creator_type.lower())
    except ValueError:
        logger.warning(f"⚠️  Unknown creator type: {creator_type}, using ALL")
        creator_enum = CreatorType.ALL
    
    # Create configuration
    config = AggregationConfig(
        service_name=service_name,
        environment=environment,
        elasticsearch_hosts=elasticsearch_hosts or ["localhost:9200"],
        log_directory=log_directory,
        elasticsearch_enabled=ELASTICSEARCH_AVAILABLE
    )
    
    # Create aggregation system
    aggregator = LogAggregationSystem(
        config=config,
        creator_type=creator_enum
    )
    
    logger.info(f"📚 Created log aggregator for {creator_type} service {service_name}")
    
    return aggregator

# Enterprise usage example
if __name__ == "__main__":
    """
    Exemple d'utilisation enterprise du système d'agrégation de logs
    """
    
    # Create log aggregator for musician service
    aggregator = create_log_aggregator(
        service_name="iacherie_music_service",
        creator_type="musician",
        environment="development",
        log_directory="/tmp/iacherie_logs"
    )
    
    try:
        logger.info("🎵 Starting log aggregation demo...")
        
        # Start aggregation
        aggregator.start_aggregation()
        
        # Simulate various log types
        aggregator.ingest_log(
            LogLevel.INFO,
            "Music upload processing started",
            LogCategory.CREATOR_ACTIVITY,
            creator_id="musician_123",
            user_id="user_456",
            session_id="session_789",
            tags={"workflow": "upload", "file_type": "mp3"},
            fields={"file_size_mb": 25.4, "duration_seconds": 180.5}
        )
        
        aggregator.ingest_log(
            LogLevel.INFO,
            "Audio quality analysis completed",
            LogCategory.ML_MODEL,
            creator_id="musician_123",
            model_id="audio_quality_v2",
            duration_ms=1250,
            fields={"quality_score": 0.89, "noise_level": 0.12}
        )
        
        aggregator.ingest_log(
            LogLevel.WARNING,
            "High CPU usage during audio processing",
            LogCategory.PERFORMANCE,
            creator_id="musician_123",
            cpu_percent=85.2,
            memory_mb=512.8
        )
        
        aggregator.ingest_log(
            LogLevel.ERROR,
            "Failed to classify music genre - model timeout",
            LogCategory.ML_MODEL,
            creator_id="musician_123",
            model_id="genre_classifier_v1",
            error_type="TimeoutError",
            error_stack="TimeoutError: Model inference timeout after 30s",
            duration_ms=30000
        )
        
        aggregator.ingest_log(
            LogLevel.CRITICAL,
            "Security violation: unauthorized access attempt",
            LogCategory.SECURITY,
            user_id="unknown_user",
            tags={"source_ip": "192.168.1.100", "attack_type": "brute_force"},
            fields={"attempts": 15, "blocked": True}
        )
        
        # Simulate more logs
        import random
        for i in range(50):
            level = random.choice(list(LogLevel))
            category = random.choice(list(LogCategory))
            
            aggregator.ingest_log(
                level,
                f"Simulated log message {i}: Random operation completed",
                category,
                creator_id=f"creator_{i % 10}",
                user_id=f"user_{i % 20}",
                duration_ms=random.uniform(10, 1000),
                fields={"operation_id": i, "success": random.choice([True, False])}
            )
            
            time.sleep(0.01)  # Small delay between logs
        
        # Wait for processing
        time.sleep(3)
        
        # Get system status
        status = aggregator.get_system_status()
        logger.info(f"📊 System Status: {json.dumps(status, indent=2, default=str)}")
        
        # Get log statistics
        stats = aggregator.get_log_statistics(hours_back=1)
        logger.info(f"📈 Log Statistics: {json.dumps(stats, indent=2, default=str)}")
        
        # Search for error logs
        error_query = LogQuery(
            query="error",
            level=LogLevel.ERROR,
            limit=10
        )
        error_logs = aggregator.search_logs(error_query)
        logger.info(f"❌ Found {len(error_logs)} error logs")
        
        # Export logs
        aggregator.export_logs("/tmp/logs_export.json", hours_back=1)
        
    finally:
        # Stop aggregation
        aggregator.stop_aggregation()
        logger.info("✅ Log aggregation demo completed successfully")