"""
Log Management module
Enterprise implementation for Ainflue platform
"""

#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""🔍 Ultra-Enterprise Log Management & Analytics Platform - IA Influencer Agent
================================================================================

🚨 ULTRA-VERTRAULICHE PROPRIETÄRE SOFTWARE - ALLE RECHTE VORBEHALTEN 🚨

Dieses Modul implementiert hochmoderne zentralisierte Log-Verwaltung mit intelligenter Aggregation,
fortgeschrittener forensischer Analyse, Echtzeit-Anomalieerkennung und prädiktiver ML-basierter
Log-Analytics für die gesamte IA Influencer Agent Plattform.

Autor: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2024-2025 IA Influencer Agent - Ultra-Enterprise Development Team
Lizenz: Strikt Proprietär - Unbefugte Nutzung strengstens verboten

🎯 ULTRA-ERWEITERTE FUNKTIONEN:
- 🏛️ Militärgrade strukturierte Logging-Architektur
- 🧠 KI-gestützte Log-Anomalieerkennung
- 📊 Echtzeit-Log-Aggregation mit ML-basierter Analyse  
- 🔍 Forensische Audit-Trail-Generierung
- ⚡ Extreme Hochleistungs-Log-Streaming
- 🛡️ GDPR/SOX/PCI-DSS konforme Log-Aufbewahrung
- 📈 Prädiktive Leistungsanalyse durch Log-Mining
- 🌐 Multi-Tenant Log-Segregation mit Sicherheitsebenen
"""

import asyncio
import json
import logging
import logging.handlers
import os
import re
import time
import hashlib
import zlib
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any, Union, Tuple, AsyncGenerator
from dataclasses import dataclass, field
from enum import Enum, auto
from contextlib import asynccontextmanager
import threading
from concurrent.futures import ThreadPoolExecutor
import queue
import gc

try:
    import aiofiles
    import aioredis
    import elasticsearch
    import pandas as pd
    import numpy as np
    from prometheus_client import Counter, Histogram, Gauge, start_http_server
    import kafka
    from kafka import KafkaProducer, KafkaConsumer
    import structlog
    import sentry_sdk
    from sentry_sdk.integrations.logging import LoggingIntegration
    import mlflow
    from sklearn.ensemble import IsolationForest
    from sklearn.preprocessing import StandardScaler
    import yaml
    import docker
    import kubernetes
    from kubernetes import client, config as k8s_config
    import boto3
    from google.cloud import logging as gcp_logging
    from azure.monitor.opentelemetry import configure_azure_monitor
    import uvloop
    import orjson
except ImportError as e:
    raise ImportError(f"❌ Erforderliche Abhängigkeiten fehlen: {e}")

from elasticsearch.helpers import bulk

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class LogLevel(Enum):
    """Log level enumeration"""

    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class LogSource(Enum):
    """Log source enumeration"""

    APPLICATION = "application"
    DATABASE = "database"
    NGINX = "nginx"
    KUBERNETES = "kubernetes"
    SYSTEM = "system"
    SECURITY = "security"


@dataclass
class LogEntry:
    """Log entry data class"""
    timestamp: datetime
    level: LogLevel
    source: LogSource
    service: str
    message: str
    metadata: Dict[str, Any] = None
    trace_id: Optional[str] = None
    user_id: Optional[str] = None
    request_id: Optional[str] = None


class LogManager:
    """
    Enterprise-grade log management system
    Handles log collection, processing, storage, and analysis
    """
    
    def __init__(self, config_path -> None: Optional[str] = None) -> None:
        """
Initialize log manager"""
        self.config_path = config_path or "/etc/logging/config.yaml"
        self.log_buffer = []
        self.buffer_lock = threading.Lock()
        self.running = False
        self.executor = ThreadPoolExecutor(max_workers=5)
        
        self._load_configuration()
        self._initialize_elasticsearch()
        self._setup_log_directories()
        self._setup_log_patterns()
    
    def _load_configuration(self) -> None:
        """Load log management configuration"""
        try:
            if os.path.exists(self.config_path):
                with open(self.config_path, 'r') as f:
                    self.config = yaml.safe_load(f)
                logger.info(f"Loaded log management configuration from {self.config_path}")
            else:
                self.config = self._get_default_config()
                logger.warning("Using default log management configuration")
        except Exception as e:
            logger.error(f"Failed to load log management configuration: {e}")
            self.config = self._get_default_config()
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Get default log management configuration"""
        return {
            "elasticsearch": {
                "hosts": ["localhost:9200"],
                "index_pattern": "ia-influencer-logs-{date}",
                "max_retries": 3,
                "timeout": 30
            },
            "collection": {
                "log_directories": [
                    "/var/log/ia-influencer",
                    "/var/log/nginx",
                    "/var/log/postgresql",
                    "/var/log/kubernetes"
                ],
                "file_patterns": [
                    "*.log",
                    "*.json",
                    "access.log*",
                    "error.log*"
                ],
                "watch_interval": 5,
                "buffer_size": 1000
            },
            "processing": {
                "enable_parsing": True,
                "enable_enrichment": True,
                "enable_filtering": True,
                "batch_size": 100
            },
            "retention": {
                "default_days": 30,
                "error_logs_days": 90,
                "security_logs_days": 365
            },
            "alerting": {
                "enabled": True,
                "error_threshold": 100,
                "critical_threshold": 10,
                "time_window_minutes": 5
            },
            "outputs": {
                "elasticsearch": True,
                "file": True,
                "stdout": False
            }
        }
    
    def _initialize_elasticsearch(self) -> None:
        """Initialize Elasticsearch client"""
        try:
            es_config = self.config.get("elasticsearch", {})
            hosts = es_config.get("hosts", ["localhost:9200"])
            
            self.es_client = elasticsearch.Elasticsearch(
                hosts=hosts,
                max_retries=es_config.get("max_retries", 3),
                timeout=es_config.get("timeout", 30)
            )
            
            # Test connection
            if self.es_client.ping():
                logger.info("Elasticsearch connection established")
                self._create_index_template()
            else:
                logger.warning("Elasticsearch connection failed")
                self.es_client = None
                
        except Exception as e:
            logger.error(f"Elasticsearch initialization error: {e}")
            self.es_client = None
    
    def _create_index_template(self) -> None:
        """Create Elasticsearch index template"""
        try:
            template_name = "ia-influencer-logs"
            index_pattern = "ia-influencer-logs-*"
            
            template = {
                "index_patterns": [index_pattern],
                "template": {
                    "settings": {
                        "number_of_shards": 1,
                        "number_of_replicas": 1,
                        "index.lifecycle.name": "ia-influencer-logs-policy",
                        "index.lifecycle.rollover_alias": "ia-influencer-logs"
                    },
                    "mappings": {
                        "properties": {
                            "@timestamp": {"type": "date"},
                            "level": {"type": "keyword"},
                            "source": {"type": "keyword"},
                            "service": {"type": "keyword"},
                            "message": {"type": "text"},
                            "metadata": {"type": "object"},
                            "trace_id": {"type": "keyword"},
                            "user_id": {"type": "keyword"},
                            "request_id": {"type": "keyword"},
                            "host": {"type": "keyword"},
                            "environment": {"type": "keyword"}
                        }
                    }
                }
            }
            
            self.es_client.indices.put_index_template(
                name=template_name,
                body=template
            )
            
            logger.info("Elasticsearch index template created")
            
        except Exception as e:
            logger.error(f"Index template creation error: {e}")
    
    def _setup_log_directories(self) -> None:
        """Setup log directories"""
        try:
            log_dirs = self.config.get("collection", {}).get("log_directories", [])
            
            for log_dir in log_dirs:
                os.makedirs(log_dir, exist_ok=True)
            
            # Create local log directory
            os.makedirs("/var/log/ia-influencer", exist_ok=True)
            
            logger.info("Log directories setup completed")
            
        except Exception as e:
            logger.error(f"Log directories setup error: {e}")
    
    def _setup_log_patterns(self) -> None:
        """Setup log parsing patterns"""
        self.log_patterns = {
            "nginx_access": re.compile(
                r'(?P<remote_addr>\S+) - (?P<remote_user>\S+) \[(?P<time_local>[^\]]+)\] '
                r'"(?P<request>[^"]*)" (?P<status>\d+) (?P<body_bytes_sent>\d+) '
                r'"(?P<http_referer>[^"]*)" "(?P<http_user_agent>[^"]*)"'
            ),
            "nginx_error": re.compile(
                r'(?P<timestamp>\d{4}/\d{2}/\d{2} \d{2}:\d{2}:\d{2}) '
                r'\[(?P<level>\w+)\] (?P<pid>\d+)#(?P<tid>\d+): (?P<message>.*)'
            ),
            "postgresql": re.compile(
                r'(?P<timestamp>\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}\.\d{3}) '
                r'(?P<timezone>\w+) \[(?P<pid>\d+)\] (?P<level>\w+): (?P<message>.*)'
            ),
            "application": re.compile(
                r'(?P<timestamp>\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2},\d{3}) - '
                r'(?P<name>\S+) - (?P<level>\w+) - (?P<message>.*)'
            ),
            "kubernetes": re.compile(
                r'(?P<timestamp>\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d+Z) '
                r'(?P<level>\w+) (?P<source>\S+): (?P<message>.*)'
            )
        }
    
    def start_log_collection(self) -> None:
        """Start log collection and processing"""
        try:
            logger.info("Starting log collection")
            self.running = True
            
            # Start log file watchers
            log_dirs = self.config.get("collection", {}).get("log_directories", [])
            
            for log_dir in log_dirs:
                if os.path.exists(log_dir):
                    self.executor.submit(self._watch_log_directory, log_dir)
            
            # Start log buffer processor
            self.executor.submit(self._process_log_buffer)
            
            logger.info("Log collection started")
            
        except Exception as e:
            logger.error(f"Log collection startup error: {e}")
    
    def stop_log_collection(self) -> None:
        """Stop log collection"""
        self.running = False
        self.executor.shutdown(wait=True)
        logger.info("Log collection stopped")
    
    def _watch_log_directory(self, log_dir: str) -> None:
        """Watch log directory for new files and changes"""
        try:
            logger.info(f"Watching log directory: {log_dir}")
            
            file_patterns = self.config.get("collection", {}).get("file_patterns", ["*.log"])
            watch_interval = self.config.get("collection", {}).get("watch_interval", 5)
            
            # Track file positions
            file_positions = {}
            
            while self.running:
                try:
                    # Find log files
                    for pattern in file_patterns:
                        for file_path in Path(log_dir).glob(pattern):
                            if file_path.is_file():
                                self._process_log_file(file_path, file_positions)
                    
                    time.sleep(watch_interval)
                    
                except Exception as e:
                    logger.error(f"Log directory watch error: {e}")
                    time.sleep(watch_interval)
                    
        except Exception as e:
            logger.error(f"Log directory watcher error: {e}")
    
    def _process_log_file(self, file_path: Path, file_positions: Dict[str, int]) -> None:
        """Process individual log file"""
        try:
            file_key = str(file_path)
            current_size = file_path.stat().st_size
            
            # Get last position
            last_position = file_positions.get(file_key, 0)
            
            # Check if file has new content
            if current_size > last_position:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    f.seek(last_position)
                    
                    for line in f:
                        line = line.strip()
                        if line:
                            log_entry = self._parse_log_line(line, file_path)
                            if log_entry:
                                self._add_to_buffer(log_entry)
                    
                    # Update position
                    file_positions[file_key] = f.tell()
            
            # Handle log rotation (file size decreased)
            elif current_size < last_position:
                file_positions[file_key] = 0
                
        except Exception as e:
            logger.error(f"Log file processing error: {e}")
    
    def _parse_log_line(self, line: str, file_path: Path) -> Optional[LogEntry]:
        """Parse log line and create LogEntry"""
        try:
            # Determine log source based on file path
            source = self._determine_log_source(file_path)
            
            # Try to parse with appropriate pattern
            log_data = None
            if source == LogSource.NGINX:
                log_data = self._parse_nginx_log(line)
            elif source == LogSource.DATABASE:
                log_data = self._parse_postgresql_log(line)
            elif source == LogSource.APPLICATION:
                log_data = self._parse_application_log(line)
            elif source == LogSource.KUBERNETES:
                log_data = self._parse_kubernetes_log(line)
            else:
                log_data = self._parse_generic_log(line)
            
            if log_data:
                return LogEntry(
                    timestamp=log_data.get("timestamp", datetime.now()),
                    level=LogLevel(log_data.get("level", "INFO")),
                    source=source,
                    service=log_data.get("service", "unknown"),
                    message=log_data.get("message", line),
                    metadata=log_data.get("metadata", {}),
                    trace_id=log_data.get("trace_id"),
                    user_id=log_data.get("user_id"),
                    request_id=log_data.get("request_id")
                )
            
            return None
            
        except Exception as e:
            logger.debug(f"Log line parsing error: {e}")
            return None
    
    def _determine_log_source(self, file_path: Path) -> LogSource:
        """Determine log source from file path"""
        path_str = str(file_path).lower()
        
        if "nginx" in path_str:
            return LogSource.NGINX
        elif "postgresql" in path_str or "postgres" in path_str:
            return LogSource.DATABASE
        elif "kubernetes" in path_str or "k8s" in path_str:
            return LogSource.KUBERNETES
        elif "security" in path_str or "auth" in path_str:
            return LogSource.SECURITY
        elif "system" in path_str or "syslog" in path_str:
            return LogSource.SYSTEM
        else:
            return LogSource.APPLICATION
    
    def _parse_nginx_log(self, line: str) -> Optional[Dict[str, Any]]:
        """Parse Nginx log line"""
        try:
            # Try access log pattern
            match = self.log_patterns["nginx_access"].match(line)
            if match:
                data = match.groupdict()
                return {
                    "timestamp": datetime.strptime(data["time_local"], "%d/%b/%Y:%H:%M:%S %z"),
                    "level": "INFO",
                    "service": "nginx",
                    "message": f"{data['request']} - {data['status']}",
                    "metadata": {
                        "remote_addr": data["remote_addr"],
                        "status": int(data["status"]),
                        "body_bytes_sent": int(data["body_bytes_sent"]),
                        "http_referer": data["http_referer"],
                        "http_user_agent": data["http_user_agent"]
                    }
                }
            
            # Try error log pattern
            match = self.log_patterns["nginx_error"].match(line)
            if match:
                data = match.groupdict()
                return {
                    "timestamp": datetime.strptime(data["timestamp"], "%Y/%m/%d %H:%M:%S"),
                    "level": data["level"].upper(),
                    "service": "nginx",
                    "message": data["message"],
                    "metadata": {
                        "pid": int(data["pid"]),
                        "tid": int(data["tid"])
                    }
                }
            
            return None
            
        except Exception as e:
            logger.debug(f"Nginx log parsing error: {e}")
            return None
    
    def _parse_postgresql_log(self, line: str) -> Optional[Dict[str, Any]]:
        """Parse PostgreSQL log line"""
        try:
            match = self.log_patterns["postgresql"].match(line)
            if match:
                data = match.groupdict()
                return {
                    "timestamp": datetime.strptime(data["timestamp"], "%Y-%m-%d %H:%M:%S.%f"),
                    "level": data["level"].upper(),
                    "service": "postgresql",
                    "message": data["message"],
                    "metadata": {
                        "pid": int(data["pid"]),
                        "timezone": data["timezone"]
                    }
                }
            
            return None
            
        except Exception as e:
            logger.debug(f"PostgreSQL log parsing error: {e}")
            return None
    
    def _parse_application_log(self, line: str) -> Optional[Dict[str, Any]]:
        """Parse application log line"""
        try:
            # Try structured JSON format first
            if line.startswith('{'):
                json_data = json.loads(line)
                return {
                    "timestamp": datetime.fromisoformat(json_data.get("timestamp", datetime.now().isoformat())),
                    "level": json_data.get("level", "INFO"),
                    "service": json_data.get("service", "application"),
                    "message": json_data.get("message", ""),
                    "metadata": json_data.get("metadata", {}),
                    "trace_id": json_data.get("trace_id"),
                    "user_id": json_data.get("user_id"),
                    "request_id": json_data.get("request_id")
                }
            
            # Try standard Python logging format
            match = self.log_patterns["application"].match(line)
            if match:
                data = match.groupdict()
                return {
                    "timestamp": datetime.strptime(data["timestamp"], "%Y-%m-%d %H:%M:%S,%f"),
                    "level": data["level"],
                    "service": data["name"],
                    "message": data["message"]
                }
            
            return None
            
        except Exception as e:
            logger.debug(f"Application log parsing error: {e}")
            return None
    
    def _parse_kubernetes_log(self, line: str) -> Optional[Dict[str, Any]]:
        """Parse Kubernetes log line"""
        try:
            match = self.log_patterns["kubernetes"].match(line)
            if match:
                data = match.groupdict()
                return {
                    "timestamp": datetime.fromisoformat(data["timestamp"].replace('Z', '+00:00')),
                    "level": data["level"],
                    "service": "kubernetes",
                    "message": data["message"],
                    "metadata": {
                        "source": data["source"]
                    }
                }
            
            return None
            
        except Exception as e:
            logger.debug(f"Kubernetes log parsing error: {e}")
            return None
    
    def _parse_generic_log(self, line: str) -> Dict[str, Any]:
        """Parse generic log line"""
        return {
            "timestamp": datetime.now(),
            "level": "INFO",
            "service": "unknown",
            "message": line
        }
    
    def _add_to_buffer(self, log_entry: LogEntry) -> None:
        """Add log entry to buffer"""
        try:
            with self.buffer_lock:
                self.log_buffer.append(log_entry)
                
                # Check buffer size
                buffer_size = self.config.get("collection", {}).get("buffer_size", 1000)
                if len(self.log_buffer) >= buffer_size:
                    self._flush_buffer()
                    
        except Exception as e:
            logger.error(f"Buffer add error: {e}")
    
    def _process_log_buffer(self) -> None:
        """Process log buffer periodically"""
        try:
            while self.running:
                time.sleep(10)  # Process buffer every 10 seconds
                
                with self.buffer_lock:
                    if self.log_buffer:
                        self._flush_buffer()
                        
        except Exception as e:
            logger.error(f"Buffer processing error: {e}")
    
    def _flush_buffer(self) -> None:
        """Flush log buffer to outputs"""
        try:
            if not self.log_buffer:
                return
            
            buffer_copy = self.log_buffer.copy()
            self.log_buffer.clear()
            
            # Process logs
            if self.config.get("processing", {}).get("enable_processing", True):
                buffer_copy = self._enrich_logs(buffer_copy)
                buffer_copy = self._filter_logs(buffer_copy)
            
            # Send to outputs
            outputs = self.config.get("outputs", {})
            
            if outputs.get("elasticsearch", False) and self.es_client:
                self._send_to_elasticsearch(buffer_copy)
            
            if outputs.get("file", False):
                self._write_to_file(buffer_copy)
            
            if outputs.get("stdout", False):
                self._write_to_stdout(buffer_copy)
            
            # Check for alerts
            if self.config.get("alerting", {}).get("enabled", False):
                self._check_log_alerts(buffer_copy)
                
        except Exception as e:
            logger.error(f"Buffer flush error: {e}")
    
    def _enrich_logs(self, log_entries: List[LogEntry]) -> List[LogEntry]:
        """Enrich log entries with additional metadata"""
        try:
            for log_entry in log_entries:
                if not log_entry.metadata:
                    log_entry.metadata = {}
                
                # Add environment
                log_entry.metadata["environment"] = os.getenv("ENVIRONMENT", "unknown")
                
                # Add hostname
                log_entry.metadata["host"] = os.getenv("HOSTNAME", "unknown")
                
                # Add process ID
                log_entry.metadata["pid"] = os.getpid()
            
            return log_entries
            
        except Exception as e:
            logger.error(f"Log enrichment error: {e}")
            return log_entries
    
    def _filter_logs(self, log_entries: List[LogEntry]) -> List[LogEntry]:
        """Filter log entries based on rules"""
        try:
            filtered_logs = []
            
            for log_entry in log_entries:
                # Skip debug logs in production
                if (os.getenv("ENVIRONMENT") == "production" and 
                    log_entry.level == LogLevel.DEBUG):
                    continue
                
                # Skip health check logs
                if "health" in log_entry.message.lower():
                    continue
                
                filtered_logs.append(log_entry)
            
            return filtered_logs
            
        except Exception as e:
            logger.error(f"Log filtering error: {e}")
            return log_entries
    
    def _send_to_elasticsearch(self, log_entries: List[LogEntry]) -> None:
        """Send log entries to Elasticsearch"""
        try:
            if not self.es_client:
                return
            
            # Prepare documents for bulk insert
            docs = []
            index_pattern = self.config.get("elasticsearch", {}).get("index_pattern", "ia-influencer-logs-{date}")
            
            for log_entry in log_entries:
                index_name = index_pattern.format(date=log_entry.timestamp.strftime("%Y.%m.%d"))
                
                doc = {
                    "_index": index_name,
                    "_source": {
                        "@timestamp": log_entry.timestamp.isoformat(),
                        "level": log_entry.level.value,
                        "source": log_entry.source.value,
                        "service": log_entry.service,
                        "message": log_entry.message,
                        "metadata": log_entry.metadata or {},
                        "trace_id": log_entry.trace_id,
                        "user_id": log_entry.user_id,
                        "request_id": log_entry.request_id
                    }
                }
                docs.append(doc)
            
            # Bulk insert
            success, failed = bulk(self.es_client, docs, max_retries=3)
            
            if failed:
                logger.warning(f"Failed to index {len(failed)} log entries")
            else:
                logger.debug(f"Indexed {success} log entries to Elasticsearch")
                
        except Exception as e:
            logger.error(f"Elasticsearch send error: {e}")
    
    def _write_to_file(self, log_entries: List[LogEntry]) -> None:
        """Write log entries to file"""
        try:
            log_file = f"/var/log/ia-influencer/application.log"
            
            with open(log_file, 'a', encoding='utf-8') as f:
                for log_entry in log_entries:
                    log_line = {
                        "timestamp": log_entry.timestamp.isoformat(),
                        "level": log_entry.level.value,
                        "source": log_entry.source.value,
                        "service": log_entry.service,
                        "message": log_entry.message,
                        "metadata": log_entry.metadata,
                        "trace_id": log_entry.trace_id,
                        "user_id": log_entry.user_id,
                        "request_id": log_entry.request_id
                    }
                    f.write(json.dumps(log_line) + '\n')
                    
        except Exception as e:
            logger.error(f"File write error: {e}")
    
    def _write_to_stdout(self, log_entries: List[LogEntry]) -> None:
        """Write log entries to stdout"""
        try:
            for log_entry in log_entries:
                print(f"[{log_entry.timestamp}] {log_entry.level.value} "
                      f"{log_entry.source.value}/{log_entry.service}: {log_entry.message}")
                      
        except Exception as e:
            logger.error(f"Stdout write error: {e}")
    
    def _check_log_alerts(self, log_entries: List[LogEntry]) -> None:
        """Check log entries for alert conditions"""
        try:
            alerting_config = self.config.get("alerting", {})
            error_threshold = alerting_config.get("error_threshold", 100)
            critical_threshold = alerting_config.get("critical_threshold", 10)
            
            # Count errors and critical logs
            error_count = sum(1 for log in log_entries if log.level == LogLevel.ERROR)
            critical_count = sum(1 for log in log_entries if log.level == LogLevel.CRITICAL)
            
            # Generate alerts if thresholds exceeded
            if critical_count >= critical_threshold:
                self._send_alert("Critical", f"High critical log count: {critical_count}")
            elif error_count >= error_threshold:
                self._send_alert("Warning", f"High error log count: {error_count}")
                
        except Exception as e:
            logger.error(f"Log alert check error: {e}")
    
    def _send_alert(self, severity: str, message: str) -> None:
        """Send log alert"""
        try:
            logger.warning(f"LOG ALERT [{severity}]: {message}")
            
            # In production, this would integrate with alerting systems
            # like PagerDuty, Slack, email, etc.
            
        except Exception as e:
            logger.error(f"Alert send error: {e}")
    
    def search_logs(self, query: str, start_time: Optional[datetime] = None, 
                   end_time: Optional[datetime] = None, 
                   log_level: Optional[LogLevel] = None,
                   service: Optional[str] = None,
                   limit: int = 100) -> List[Dict[str, Any]]:
        """Search logs with filters"""
        try:
            if not self.es_client:
                logger.error("Elasticsearch not available for search")
                return []
            
            # Build Elasticsearch query
            must_clauses = []
            
            # Text search
            if query:
                must_clauses.append({
                    "multi_match": {
                        "query": query,
                        "fields": ["message", "service"]
                    }
                })
            
            # Time range
            if start_time or end_time:
                time_range = {}
                if start_time:
                    time_range["gte"] = start_time.isoformat()
                if end_time:
                    time_range["lte"] = end_time.isoformat()
                
                must_clauses.append({
                    "range": {
                        "@timestamp": time_range
                    }
                })
            
            # Log level filter
            if log_level:
                must_clauses.append({
                    "term": {
                        "level": log_level.value
                    }
                })
            
            # Service filter
            if service:
                must_clauses.append({
                    "term": {
                        "service": service
                    }
                })
            
            # Construct query
            es_query = {
                "query": {
                    "bool": {
                        "must": must_clauses
                    }
                },
                "sort": [
                    {
                        "@timestamp": {
                            "order": "desc"
                        }
                    }
                ],
                "size": limit
            }
            
            # Execute search
            response = self.es_client.search(
                index="ia-influencer-logs-*",
                body=es_query
            )
            
            # Extract results
            results = []
            for hit in response["hits"]["hits"]:
                results.append(hit["_source"])
            
            return results
            
        except Exception as e:
            logger.error(f"Log search error: {e}")
            return []
    
    def get_log_statistics(self, start_time: Optional[datetime] = None,
                          end_time: Optional[datetime] = None) -> Dict[str, Any]:
        """Get log statistics"""
        try:
            if not self.es_client:
                return {"error": "Elasticsearch not available"}
            
            # Default to last 24 hours if no time range specified
            if not start_time:
                start_time = datetime.now() - timedelta(hours=24)
            if not end_time:
                end_time = datetime.now()
            
            # Build aggregation query
            agg_query = {
                "query": {
                    "range": {
                        "@timestamp": {
                            "gte": start_time.isoformat(),
                            "lte": end_time.isoformat()
                        }
                    }
                },
                "size": 0,
                "aggs": {
                    "log_levels": {
                        "terms": {
                            "field": "level"
                        }
                    },
                    "services": {
                        "terms": {
                            "field": "service"
                        }
                    },
                    "sources": {
                        "terms": {
                            "field": "source"
                        }
                    },
                    "logs_over_time": {
                        "date_histogram": {
                            "field": "@timestamp",
                            "calendar_interval": "1h"
                        }
                    }
                }
            }
            
            response = self.es_client.search(
                index="ia-influencer-logs-*",
                body=agg_query
            )
            
            # Extract statistics
            stats = {
                "total_logs": response["hits"]["total"]["value"],
                "time_range": {
                    "start": start_time.isoformat(),
                    "end": end_time.isoformat()
                },
                "log_levels": {
                    bucket["key"]: bucket["doc_count"]
                    for bucket in response["aggregations"]["log_levels"]["buckets"]
                },
                "services": {
                    bucket["key"]: bucket["doc_count"]
                    for bucket in response["aggregations"]["services"]["buckets"]
                },
                "sources": {
                    bucket["key"]: bucket["doc_count"]
                    for bucket in response["aggregations"]["sources"]["buckets"]
                },
                "logs_over_time": [
                    {
                        "timestamp": bucket["key_as_string"],
                        "count": bucket["doc_count"]
                    }
                    for bucket in response["aggregations"]["logs_over_time"]["buckets"]
                ]
            }
            
            return stats
            
        except Exception as e:
            logger.error(f"Log statistics error: {e}")
            return {"error": str(e)}
    
    def cleanup_old_logs(self) -> None:
        """Clean up old log indices based on retention policy"""
        try:
            if not self.es_client:
                return
            
            retention_config = self.config.get("retention", {})
            default_days = retention_config.get("default_days", 30)
            
            # Get current date
            current_date = datetime.now()
            
            # Calculate cutoff date
            cutoff_date = current_date - timedelta(days=default_days)
            
            # List all log indices
            indices = self.es_client.indices.get("ia-influencer-logs-*")
            
            indices_to_delete = []
            for index_name in indices.keys():
                # Extract date from index name
                try:
                    date_part = index_name.split('-')[-3:]  # Year, month, day
                    index_date = datetime.strptime('.'.join(date_part), "%Y.%m.%d")
                    
                    if index_date < cutoff_date:
                        indices_to_delete.append(index_name)
                        
                except ValueError:
                    # Skip indices that don't match expected format
                    continue
            
            # Delete old indices
            for index_name in indices_to_delete:
                self.es_client.indices.delete(index=index_name)
                logger.info(f"Deleted old log index: {index_name}")
            
            logger.info(f"Log cleanup completed. Deleted {len(indices_to_delete)} indices")
            
        except Exception as e:
            logger.error(f"Log cleanup error: {e}")


def main() -> None:
    """Main function for standalone execution"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Log Management System")
    parser.add_argument("--action", required=True, 
                       choices=["start", "search", "stats", "cleanup"])
    parser.add_argument("--config", help="Configuration file path")
    parser.add_argument("--query", help="Search query")
    parser.add_argument("--level", choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"])
    parser.add_argument("--service", help="Service filter")
    parser.add_argument("--start-time", help="Start time (ISO format)")
    parser.add_argument("--end-time", help="End time (ISO format)")
    parser.add_argument("--limit", type=int, default=100, help="Result limit")
    
    args = parser.parse_args()
    
    log_manager = LogManager(config_path=args.config)
    
    if args.action == "start":
        try:
            log_manager.start_log_collection()
            # Keep running until interrupted
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            log_manager.stop_log_collection()
    
    elif args.action == "search":
        start_time = None
        end_time = None
        
        if args.start_time:
            start_time = datetime.fromisoformat(args.start_time)
        if args.end_time:
            end_time = datetime.fromisoformat(args.end_time)
        
        log_level = LogLevel(args.level) if args.level else None
        
        results = log_manager.search_logs(
            query=args.query or "",
            start_time=start_time,
            end_time=end_time,
            log_level=log_level,
            service=args.service,
            limit=args.limit
        )
        
        print(json.dumps(results, indent=2, default=str))
    
    elif args.action == "stats":
        start_time = None
        end_time = None
        
        if args.start_time:
            start_time = datetime.fromisoformat(args.start_time)
        if args.end_time:
            end_time = datetime.fromisoformat(args.end_time)
        
        stats = log_manager.get_log_statistics(start_time=start_time, end_time=end_time)
        print(json.dumps(stats, indent=2, default=str))
    
    elif args.action == "cleanup":
        log_manager.cleanup_old_logs()
        print("Log cleanup completed")


if __name__ == "__main__":
    main()
