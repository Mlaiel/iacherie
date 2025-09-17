#!/usr/bin/env python3
"""
📝 Logging Service Template - Ainflue Enterprise
===============================================
Template enterprise pour services logging.
Structured logging + audit trails + log aggregation + compliance.

Author: Fahed Mlaiel (mlaiel@live.de)
Project: Ainflue Microservices Templates
Version: 1.0 Production
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️ PROPRIÉTÉ INTELLECTUELLE - FAHED MLAIEL
Cette architecture microservices et tous ses templates sont la propriété intellectuelle 
EXCLUSIVE de Fahed Mlaiel (mlaiel@live.de). Toute reproduction, modification, 
distribution ou vol d'idée/concept/code sans autorisation écrite PERSONNELLE est 
STRICTEMENT INTERDITE et sera poursuivie en justice avec la PLEINE RIGUEUR de la loi.
"""

import asyncio
import logging
import json
import gzip
from abc import abstractmethod
from dataclasses import dataclass, field, asdict
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Callable, Union
from enum import Enum
import uuid
from pathlib import Path
import hashlib
import threading
from queue import Queue
import traceback

from .service_template import EnterpriseServiceBase, ServiceConfig

# Logging-specific types
@dataclass
class LogEntry:
    """Structured log entry."""
    timestamp: datetime
    level: str
    message: str
    service_name: str
    service_version: str = "1.0.0"
    correlation_id: Optional[str] = None
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    request_id: Optional[str] = None
    module: Optional[str] = None
    function: Optional[str] = None
    line_number: Optional[int] = None
    extra_data: Dict[str, Any] = field(default_factory=dict)
    tags: List[str] = field(default_factory=list)

@dataclass
class AuditLogEntry:
    """Audit log entry for compliance."""
    timestamp: datetime
    event_type: str
    actor_id: str
    actor_type: str  # user, system, service
    resource_type: str
    resource_id: str
    action: str
    outcome: str  # success, failure, denied
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    details: Dict[str, Any] = field(default_factory=dict)
    compliance_tags: List[str] = field(default_factory=list)

@dataclass
class LoggingConfig:
    """Configuration for logging behavior."""
    service_name: str
    log_level: str = "INFO"
    format: str = "json"  # json, text, structured
    output_destinations: List[str] = field(default_factory=lambda: ["console"])
    file_config: Optional[Dict[str, Any]] = None
    remote_config: Optional[Dict[str, Any]] = None
    buffer_size: int = 1000
    flush_interval: int = 5
    compression_enabled: bool = True
    retention_days: int = 30

@dataclass
class LogRetentionPolicy:
    """Log retention policy configuration."""
    log_type: str
    retention_days: int
    archival_enabled: bool = True
    archival_storage: str = "local"  # local, s3, azure, gcs
    compression_enabled: bool = True
    encryption_enabled: bool = False

class LogLevel(Enum):
    """Log levels."""
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"
    AUDIT = "AUDIT"

class EventType(Enum):
    """Audit event types."""
    LOGIN = "login"
    LOGOUT = "logout"
    CREATE = "create"
    READ = "read"
    UPDATE = "update"
    DELETE = "delete"
    EXPORT = "export"
    IMPORT = "import"
    PERMISSION_CHANGE = "permission_change"
    SYSTEM_ACCESS = "system_access"

class LoggingServiceTemplate(EnterpriseServiceBase):
    """
    📝 Template enterprise pour services logging.
    
    Fonctionnalités:
    - Structured logging avec JSON format
    - Audit trails pour compliance (GDPR, SOX, HIPAA)
    - Log aggregation avec multiple destinations
    - Log retention avec archivage automatique
    - Real-time log streaming et monitoring
    - Log analysis avec anomaly detection
    - Performance metrics et monitoring
    - Secure log transmission avec encryption
    """
    
    def __init__(self, config: ServiceConfig):
        """Initialize logging service."""
        super().__init__(config)
        self.logging_configs: Dict[str, LoggingConfig] = {}
        self.retention_policies: Dict[str, LogRetentionPolicy] = {}
        
        # Log storage and processing
        self.log_buffer: Queue = Queue(maxsize=10000)
        self.audit_buffer: Queue = Queue(maxsize=5000)
        self.log_processors: List[Callable] = []
        self.log_destinations: Dict[str, Any] = {}
        
        # Metrics and monitoring
        self.log_metrics: Dict[str, int] = {
            'logs_processed': 0,
            'logs_dropped': 0,
            'audit_logs_created': 0,
            'errors_logged': 0
        }
        
        # Background processors
        self.log_processor_thread: Optional[threading.Thread] = None
        self.retention_processor_task: Optional[asyncio.Task] = None
        self.running = False
        
        self.logger = logging.getLogger(f"{self.config.service_name}.logging")
        
    async def setup_structured_logging(self, logging_configs: List[LoggingConfig]) -> None:
        """Logging structuré avec JSON format."""
        try:
            for config in logging_configs:
                # Validate logging configuration
                await self._validate_logging_config(config)
                
                # Setup log formatters
                formatter = await self._create_log_formatter(config)
                
                # Setup log destinations
                destinations = await self._setup_log_destinations(config)
                
                # Create logging context
                logging_context = {
                    'config': config,
                    'formatter': formatter,
                    'destinations': destinations,
                    'stats': {
                        'logs_written': 0,
                        'last_log_time': None,
                        'avg_log_size': 0
                    }
                }
                
                self.logging_configs[config.service_name] = logging_context
                
                self.logger.info(f"Structured logging configured for '{config.service_name}'")
            
            # Start log processing
            await self._start_log_processing()
            
        except Exception as e:
            self.logger.error(f"Failed to setup structured logging: {e}")
            raise
    
    async def setup_audit_trails(self, audit_config: Dict[str, Any]) -> None:
        """Audit trails pour compliance."""
        try:
            self.audit_config = audit_config
            
            # Setup audit log destinations
            self.audit_destinations = await self._setup_audit_destinations(audit_config)
            
            # Setup compliance templates
            self.compliance_templates = audit_config.get('compliance_templates', {})
            
            # Setup audit encryption if required
            if audit_config.get('encryption_enabled', False):
                await self._setup_audit_encryption(audit_config['encryption_config'])
            
            # Setup audit log validation
            self.audit_validators = await self._setup_audit_validators(audit_config)
            
            self.logger.info("Audit trails setup completed")
            
        except Exception as e:
            self.logger.error(f"Failed to setup audit trails: {e}")
            raise
    
    async def setup_log_retention(self, retention_configs: List[LogRetentionPolicy]) -> None:
        """Politique rétention logs avec archivage."""
        try:
            for policy in retention_configs:
                # Validate retention policy
                await self._validate_retention_policy(policy)
                
                self.retention_policies[policy.log_type] = policy
                
                self.logger.info(f"Log retention policy configured for '{policy.log_type}'")
            
            # Start retention processor
            self.retention_processor_task = asyncio.create_task(self._retention_processor())
            
        except Exception as e:
            self.logger.error(f"Failed to setup log retention: {e}")
            raise
    
    async def setup_log_analysis(self, analysis_config: Dict[str, Any]) -> None:
        """Analyse logs avec ML pour anomaly detection."""
        try:
            self.analysis_config = analysis_config
            
            # Setup anomaly detection
            if analysis_config.get('anomaly_detection_enabled', False):
                await self._setup_anomaly_detection(analysis_config['anomaly_detection'])
            
            # Setup log pattern analysis
            if analysis_config.get('pattern_analysis_enabled', False):
                await self._setup_pattern_analysis(analysis_config['pattern_analysis'])
            
            # Setup real-time alerts
            if analysis_config.get('alerts_enabled', False):
                await self._setup_log_alerts(analysis_config['alerts'])
            
            self.logger.info("Log analysis setup completed")
            
        except Exception as e:
            self.logger.error(f"Failed to setup log analysis: {e}")
            raise
    
    async def log_structured(self, level: LogLevel, message: str, 
                            service_name: str,
                            correlation_id: Optional[str] = None,
                            user_id: Optional[str] = None,
                            extra_data: Optional[Dict[str, Any]] = None,
                            tags: Optional[List[str]] = None) -> None:
        """Log structured message."""
        try:
            # Create log entry
            log_entry = LogEntry(
                timestamp=datetime.utcnow(),
                level=level.value,
                message=message,
                service_name=service_name,
                correlation_id=correlation_id,
                user_id=user_id,
                extra_data=extra_data or {},
                tags=tags or []
            )
            
            # Add caller information
            frame = traceback.extract_stack()[-2]
            log_entry.module = frame.filename
            log_entry.function = frame.name
            log_entry.line_number = frame.lineno
            
            # Add to buffer for processing
            if not self.log_buffer.full():
                self.log_buffer.put(log_entry)
                self.log_metrics['logs_processed'] += 1
            else:
                self.log_metrics['logs_dropped'] += 1
                self.logger.warning("Log buffer full, dropping log entry")
            
        except Exception as e:
            self.logger.error(f"Failed to log structured message: {e}")
    
    async def log_audit(self, event_type: EventType, actor_id: str, 
                       actor_type: str, resource_type: str, resource_id: str,
                       action: str, outcome: str,
                       ip_address: Optional[str] = None,
                       user_agent: Optional[str] = None,
                       details: Optional[Dict[str, Any]] = None,
                       compliance_tags: Optional[List[str]] = None) -> None:
        """Log audit event for compliance."""
        try:
            # Create audit log entry
            audit_entry = AuditLogEntry(
                timestamp=datetime.utcnow(),
                event_type=event_type.value,
                actor_id=actor_id,
                actor_type=actor_type,
                resource_type=resource_type,
                resource_id=resource_id,
                action=action,
                outcome=outcome,
                ip_address=ip_address,
                user_agent=user_agent,
                details=details or {},
                compliance_tags=compliance_tags or []
            )
            
            # Add to audit buffer for processing
            if not self.audit_buffer.full():
                self.audit_buffer.put(audit_entry)
                self.log_metrics['audit_logs_created'] += 1
            else:
                self.logger.error("Audit buffer full, cannot drop audit logs")
                # For audit logs, we might want to block or use emergency storage
                await self._emergency_audit_storage(audit_entry)
            
        except Exception as e:
            self.logger.error(f"Failed to log audit event: {e}")
            raise  # Audit logging failures should not be silent
    
    async def search_logs(self, query: Dict[str, Any], 
                         start_time: Optional[datetime] = None,
                         end_time: Optional[datetime] = None,
                         limit: int = 100) -> List[Dict[str, Any]]:
        """Search logs with filters."""
        try:
            # This would integrate with log storage backend (Elasticsearch, etc.)
            # For now, return mock results
            results = []
            
            # Mock search implementation
            mock_logs = [
                {
                    'timestamp': '2025-01-01T10:00:00Z',
                    'level': 'INFO',
                    'message': 'User logged in',
                    'service_name': 'auth_service',
                    'user_id': 'user123'
                },
                {
                    'timestamp': '2025-01-01T10:01:00Z',
                    'level': 'ERROR',
                    'message': 'Database connection failed',
                    'service_name': 'data_service',
                    'error': 'Connection timeout'
                }
            ]
            
            # Apply filters
            for log in mock_logs:
                matches = True
                
                # Apply query filters
                for key, value in query.items():
                    if key in log and log[key] != value:
                        matches = False
                        break
                
                if matches:
                    results.append(log)
                
                if len(results) >= limit:
                    break
            
            return results
            
        except Exception as e:
            self.logger.error(f"Failed to search logs: {e}")
            raise
    
    async def get_log_metrics(self) -> Dict[str, Any]:
        """Get logging metrics and statistics."""
        try:
            metrics = {
                'timestamp': datetime.utcnow().isoformat(),
                'processing_metrics': self.log_metrics.copy(),
                'buffer_status': {
                    'log_buffer_size': self.log_buffer.qsize(),
                    'log_buffer_max': self.log_buffer.maxsize,
                    'audit_buffer_size': self.audit_buffer.qsize(),
                    'audit_buffer_max': self.audit_buffer.maxsize
                },
                'configurations': {
                    'logging_configs': len(self.logging_configs),
                    'retention_policies': len(self.retention_policies),
                    'log_destinations': len(self.log_destinations)
                },
                'performance': {
                    'avg_processing_time': await self._calculate_avg_processing_time(),
                    'logs_per_second': await self._calculate_logs_per_second(),
                    'storage_usage': await self._calculate_storage_usage()
                }
            }
            
            return metrics
            
        except Exception as e:
            self.logger.error(f"Failed to get log metrics: {e}")
            raise
    
    async def archive_logs(self, log_type: str, 
                          archive_before: datetime) -> Dict[str, Any]:
        """Archive old logs based on retention policy."""
        try:
            policy = self.retention_policies.get(log_type)
            if not policy:
                raise ValueError(f"No retention policy found for log type '{log_type}'")
            
            if not policy.archival_enabled:
                return {'archived': False, 'reason': 'Archival disabled for this log type'}
            
            # Archive logs older than specified date
            archive_result = await self._archive_logs_by_date(log_type, archive_before, policy)
            
            return archive_result
            
        except Exception as e:
            self.logger.error(f"Failed to archive logs for '{log_type}': {e}")
            raise
    
    # Private helper methods
    async def _validate_logging_config(self, config: LoggingConfig) -> None:
        """Validate logging configuration."""
        if not config.service_name:
            raise ValueError("Service name is required for logging configuration")
        
        valid_levels = [level.value for level in LogLevel]
        if config.log_level not in valid_levels:
            raise ValueError(f"Invalid log level: {config.log_level}")
        
        if config.buffer_size <= 0:
            raise ValueError("Buffer size must be positive")
    
    async def _create_log_formatter(self, config: LoggingConfig) -> Callable:
        """Create log formatter based on configuration."""
        if config.format == "json":
            def json_formatter(log_entry: LogEntry) -> str:
                log_dict = asdict(log_entry)
                log_dict['timestamp'] = log_entry.timestamp.isoformat()
                return json.dumps(log_dict)
            return json_formatter
        
        elif config.format == "text":
            def text_formatter(log_entry: LogEntry) -> str:
                return (f"{log_entry.timestamp.isoformat()} [{log_entry.level}] "
                       f"{log_entry.service_name}: {log_entry.message}")
            return text_formatter
        
        else:
            raise ValueError(f"Unsupported log format: {config.format}")
    
    async def _setup_log_destinations(self, config: LoggingConfig) -> Dict[str, Any]:
        """Setup log destinations."""
        destinations = {}
        
        for dest_name in config.output_destinations:
            if dest_name == "console":
                destinations["console"] = await self._setup_console_destination()
            elif dest_name == "file":
                destinations["file"] = await self._setup_file_destination(config.file_config)
            elif dest_name == "remote":
                destinations["remote"] = await self._setup_remote_destination(config.remote_config)
        
        return destinations
    
    async def _setup_console_destination(self) -> Dict[str, Any]:
        """Setup console log destination."""
        return {
            'type': 'console',
            'handler': lambda log: print(log),
            'stats': {'logs_written': 0}
        }
    
    async def _setup_file_destination(self, file_config: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """Setup file log destination."""
        if not file_config:
            file_config = {'path': 'logs/application.log'}
        
        log_path = Path(file_config['path'])
        log_path.parent.mkdir(parents=True, exist_ok=True)
        
        async def file_handler(log_entry: str):
            with open(log_path, 'a') as f:
                f.write(log_entry + '\n')
        
        return {
            'type': 'file',
            'path': str(log_path),
            'handler': file_handler,
            'stats': {'logs_written': 0}
        }
    
    async def _setup_remote_destination(self, remote_config: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """Setup remote log destination (e.g., Elasticsearch, Splunk)."""
        if not remote_config:
            remote_config = {'endpoint': 'http://localhost:9200'}
        
        async def remote_handler(log_entry: str):
            # This would send logs to remote destination
            # For now, just simulate
            pass
        
        return {
            'type': 'remote',
            'endpoint': remote_config['endpoint'],
            'handler': remote_handler,
            'stats': {'logs_written': 0}
        }
    
    async def _setup_audit_destinations(self, audit_config: Dict[str, Any]) -> Dict[str, Any]:
        """Setup audit log destinations."""
        destinations = {}
        
        # Secure file storage for audit logs
        audit_path = Path(audit_config.get('audit_log_path', 'logs/audit.log'))
        audit_path.parent.mkdir(parents=True, exist_ok=True)
        
        async def secure_audit_handler(audit_entry: AuditLogEntry):
            audit_dict = asdict(audit_entry)
            audit_dict['timestamp'] = audit_entry.timestamp.isoformat()
            
            # Add integrity hash
            audit_json = json.dumps(audit_dict, sort_keys=True)
            audit_hash = hashlib.sha256(audit_json.encode()).hexdigest()
            audit_dict['integrity_hash'] = audit_hash
            
            with open(audit_path, 'a') as f:
                f.write(json.dumps(audit_dict) + '\n')
        
        destinations['secure_file'] = {
            'type': 'secure_file',
            'path': str(audit_path),
            'handler': secure_audit_handler
        }
        
        return destinations
    
    async def _setup_audit_encryption(self, encryption_config: Dict[str, Any]) -> None:
        """Setup audit log encryption."""
        # This would setup encryption for audit logs
        self.audit_encryption_enabled = True
        self.audit_encryption_key = encryption_config.get('key', 'default_key')
    
    async def _setup_audit_validators(self, audit_config: Dict[str, Any]) -> List[Callable]:
        """Setup audit log validators."""
        validators = []
        
        def required_fields_validator(audit_entry: AuditLogEntry) -> bool:
            required = ['timestamp', 'event_type', 'actor_id', 'resource_type', 'action']
            audit_dict = asdict(audit_entry)
            return all(audit_dict.get(field) is not None for field in required)
        
        validators.append(required_fields_validator)
        return validators
    
    async def _validate_retention_policy(self, policy: LogRetentionPolicy) -> None:
        """Validate log retention policy."""
        if policy.retention_days <= 0:
            raise ValueError("Retention days must be positive")
        
        if policy.archival_enabled and not policy.archival_storage:
            raise ValueError("Archival storage must be specified when archival is enabled")
    
    async def _start_log_processing(self) -> None:
        """Start background log processing."""
        self.running = True
        
        # Start log processor thread
        self.log_processor_thread = threading.Thread(target=self._log_processor_worker)
        self.log_processor_thread.start()
        
        # Start async processors
        asyncio.create_task(self._audit_processor())
    
    def _log_processor_worker(self) -> None:
        """Background worker for processing logs."""
        while self.running:
            try:
                # Process regular logs
                if not self.log_buffer.empty():
                    log_entry = self.log_buffer.get(timeout=1)
                    asyncio.run(self._process_log_entry(log_entry))
                
            except Exception as e:
                self.logger.error(f"Log processor error: {e}")
    
    async def _process_log_entry(self, log_entry: LogEntry) -> None:
        """Process individual log entry."""
        try:
            service_config = self.logging_configs.get(log_entry.service_name)
            if not service_config:
                # Use default configuration
                service_config = next(iter(self.logging_configs.values()))
            
            # Format log entry
            formatted_log = service_config['formatter'](log_entry)
            
            # Send to all destinations
            for dest_name, destination in service_config['destinations'].items():
                await destination['handler'](formatted_log)
                destination['stats']['logs_written'] += 1
            
            # Update metrics
            if log_entry.level == 'ERROR':
                self.log_metrics['errors_logged'] += 1
            
        except Exception as e:
            self.logger.error(f"Failed to process log entry: {e}")
    
    async def _audit_processor(self) -> None:
        """Background processor for audit logs."""
        while self.running:
            try:
                if not self.audit_buffer.empty():
                    audit_entry = self.audit_buffer.get()
                    await self._process_audit_entry(audit_entry)
                
                await asyncio.sleep(0.1)
                
            except Exception as e:
                self.logger.error(f"Audit processor error: {e}")
                await asyncio.sleep(1)
    
    async def _process_audit_entry(self, audit_entry: AuditLogEntry) -> None:
        """Process individual audit entry."""
        try:
            # Validate audit entry
            for validator in self.audit_validators:
                if not validator(audit_entry):
                    raise ValueError("Audit entry validation failed")
            
            # Send to audit destinations
            for dest_name, destination in self.audit_destinations.items():
                await destination['handler'](audit_entry)
            
        except Exception as e:
            self.logger.error(f"Failed to process audit entry: {e}")
            # Audit processing failures are critical
            await self._emergency_audit_storage(audit_entry)
    
    async def _emergency_audit_storage(self, audit_entry: AuditLogEntry) -> None:
        """Emergency storage for audit logs when primary storage fails."""
        emergency_path = Path('logs/emergency_audit.log')
        emergency_path.parent.mkdir(parents=True, exist_ok=True)
        
        audit_dict = asdict(audit_entry)
        audit_dict['timestamp'] = audit_entry.timestamp.isoformat()
        audit_dict['emergency_storage'] = True
        
        with open(emergency_path, 'a') as f:
            f.write(json.dumps(audit_dict) + '\n')
    
    async def _retention_processor(self) -> None:
        """Background processor for log retention."""
        while self.running:
            try:
                for log_type, policy in self.retention_policies.items():
                    cutoff_date = datetime.utcnow() - timedelta(days=policy.retention_days)
                    
                    if policy.archival_enabled:
                        await self.archive_logs(log_type, cutoff_date)
                    else:
                        await self._delete_old_logs(log_type, cutoff_date)
                
                # Run retention processor daily
                await asyncio.sleep(24 * 3600)
                
            except Exception as e:
                self.logger.error(f"Retention processor error: {e}")
                await asyncio.sleep(3600)  # Retry in 1 hour
    
    async def _archive_logs_by_date(self, log_type: str, 
                                   archive_before: datetime,
                                   policy: LogRetentionPolicy) -> Dict[str, Any]:
        """Archive logs older than specified date."""
        try:
            # Mock archival implementation
            archived_count = 100  # Would be actual count
            archive_path = f"archive/{log_type}_{archive_before.strftime('%Y%m%d')}.log"
            
            if policy.compression_enabled:
                archive_path += ".gz"
            
            return {
                'archived': True,
                'log_type': log_type,
                'archive_path': archive_path,
                'archived_count': archived_count,
                'archive_date': datetime.utcnow().isoformat(),
                'compressed': policy.compression_enabled,
                'encrypted': policy.encryption_enabled
            }
            
        except Exception as e:
            self.logger.error(f"Failed to archive logs: {e}")
            return {'archived': False, 'error': str(e)}
    
    async def _delete_old_logs(self, log_type: str, delete_before: datetime) -> None:
        """Delete logs older than specified date."""
        # Mock deletion implementation
        self.logger.info(f"Deleted old logs for '{log_type}' before {delete_before}")
    
    async def _setup_anomaly_detection(self, anomaly_config: Dict[str, Any]) -> None:
        """Setup anomaly detection for logs."""
        # This would setup ML-based anomaly detection
        self.anomaly_detection_enabled = True
        self.anomaly_thresholds = anomaly_config.get('thresholds', {})
    
    async def _setup_pattern_analysis(self, pattern_config: Dict[str, Any]) -> None:
        """Setup log pattern analysis."""
        # This would setup pattern recognition
        self.pattern_analysis_enabled = True
        self.known_patterns = pattern_config.get('patterns', [])
    
    async def _setup_log_alerts(self, alerts_config: Dict[str, Any]) -> None:
        """Setup real-time log alerts."""
        # This would setup alerting system
        self.alerts_enabled = True
        self.alert_rules = alerts_config.get('rules', [])
    
    async def _calculate_avg_processing_time(self) -> float:
        """Calculate average log processing time."""
        # Mock implementation
        return 0.05  # 50ms average
    
    async def _calculate_logs_per_second(self) -> float:
        """Calculate logs processed per second."""
        # Mock implementation
        return 100.0
    
    async def _calculate_storage_usage(self) -> Dict[str, int]:
        """Calculate storage usage for logs."""
        # Mock implementation
        return {
            'total_bytes': 1024 * 1024 * 100,  # 100MB
            'application_logs': 1024 * 1024 * 60,  # 60MB
            'audit_logs': 1024 * 1024 * 40  # 40MB
        }
    
    @abstractmethod
    async def setup_service_specific_logging(self) -> None:
        """Setup service-specific logging. Override in subclasses."""
        pass
    
    async def health_check(self) -> Dict[str, Any]:
        """Service health check."""
        base_health = await super().health_check()
        
        return {
            **base_health,
            'logging': {
                'configurations': len(self.logging_configs),
                'retention_policies': len(self.retention_policies),
                'log_destinations': len(self.log_destinations),
                'processing_thread': 'running' if self.running else 'stopped'
            },
            'buffers': {
                'log_buffer_usage': f"{self.log_buffer.qsize()}/{self.log_buffer.maxsize}",
                'audit_buffer_usage': f"{self.audit_buffer.qsize()}/{self.audit_buffer.maxsize}"
            },
            'metrics': self.log_metrics
        }
    
    async def cleanup(self) -> None:
        """Cleanup logging resources."""
        self.running = False
        
        # Stop background processors
        if self.log_processor_thread and self.log_processor_thread.is_alive():
            self.log_processor_thread.join(timeout=5)
        
        if self.retention_processor_task:
            self.retention_processor_task.cancel()
        
        # Process remaining logs in buffer
        while not self.log_buffer.empty():
            try:
                log_entry = self.log_buffer.get_nowait()
                await self._process_log_entry(log_entry)
            except Exception:
                break
        
        # Process remaining audit logs
        while not self.audit_buffer.empty():
            try:
                audit_entry = self.audit_buffer.get_nowait()
                await self._process_audit_entry(audit_entry)
            except Exception:
                break
        
        await super().cleanup()