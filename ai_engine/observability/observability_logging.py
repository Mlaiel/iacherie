"""Structured Logging System

Enterprise-grade logging system for the IA Influencer platform providing
structured logging, log aggregation, audit trails, and compliance features.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️  AVERTISSEMENT LÉGAL / LEGAL WARNING ⚠️
Ce code est la propriété intellectuelle exclusive de Fahed Mlaiel.
This code is the exclusive intellectual property of Fahed Mlaiel.
Toute utilisation non autorisée est strictement interdite.
Any unauthorized use is strictly prohibited.
"""
import asyncio
import json
import logging
import traceback
from datetime import datetime, timezone
from enum import Enum
from typing import Dict, List, Optional, Any, Union, Callable
from dataclasses import dataclass, field, asdict
from pathlib import Path
import uuid
import hashlib
import threading
from concurrent.futures import ThreadPoolExecutor
import gzip
import os

logger = logging.getLogger(__name__)


class LogLevel(Enum):
    """Enhanced log levels for the platform"""    TRACE = 5       # Most detailed tracing information
    DEBUG = 10      # Debugging information
    INFO = 20       # General information
    SUCCESS = 25    # Success operations
    WARNING = 30    # Warning conditions
    ERROR = 40      # Error conditions
    CRITICAL = 50   # Critical conditions
    SECURITY = 60   # Security-related events
    AUDIT = 70      # Audit trail events
    BUSINESS = 80   # Business logic events


class LogCategory(Enum):
    """Log categories for better organization"""    SYSTEM = "system"
    SECURITY = "security"
    BUSINESS = "business"
    PERFORMANCE = "performance"
    AI_MODEL = "ai_model"
    CONTENT_PROTECTION = "content_protection"
    USER_ACTION = "user_action"
    INTEGRATION = "integration"
    ERROR = "error"
    AUDIT = "audit"
    COMPLIANCE = "compliance"


class LogFormat(Enum):
    """Log output formats"""    JSON = "json"
    TEXT = "text"
    STRUCTURED = "structured"
    SYSLOG = "syslog"
    ELK = "elk"


@dataclass
class LogEntry:
    """Structured log entry"""    timestamp: datetime
    level: LogLevel
    category: LogCategory
    message: str
    logger_name: str
    
    # Context information
    session_id: Optional[str] = None
    user_id: Optional[str] = None
    request_id: Optional[str] = None
    trace_id: Optional[str] = None
    
    # Technical details
    module: Optional[str] = None
    function: Optional[str] = None
    line_number: Optional[int] = None
    thread_id: Optional[int] = None
    process_id: Optional[int] = None
    
    # Additional context
    extra_data: Dict[str, Any] = field(default_factory=dict)
    tags: List[str] = field(default_factory=list)
    
    # Error information
    exception_type: Optional[str] = None
    exception_message: Optional[str] = None
    stack_trace: Optional[str] = None
    
    # Performance metrics
    duration_ms: Optional[float] = None
    cpu_usage: Optional[float] = None
    memory_usage: Optional[float] = None
    
    def __post_init__(self):
        """Post-initialization processing"""        if self.timestamp.tzinfo is None:
            self.timestamp = self.timestamp.replace(tzinfo=timezone.utc)
        
        if self.thread_id is None:
            self.thread_id = threading.current_thread().ident
        
        if self.process_id is None:
            self.process_id = os.getpid()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert log entry to dictionary"""        return {
            'timestamp': self.timestamp.isoformat(),
            'level': self.level.name,
            'level_value': self.level.value,
            'category': self.category.value,
            'message': self.message,
            'logger_name': self.logger_name,
            'session_id': self.session_id,
            'user_id': self.user_id,
            'request_id': self.request_id,
            'trace_id': self.trace_id,
            'module': self.module,
            'function': self.function,
            'line_number': self.line_number,
            'thread_id': self.thread_id,
            'process_id': self.process_id,
            'extra_data': self.extra_data,
            'tags': self.tags,
            'exception_type': self.exception_type,
            'exception_message': self.exception_message,
            'stack_trace': self.stack_trace,
            'duration_ms': self.duration_ms,
            'cpu_usage': self.cpu_usage,
            'memory_usage': self.memory_usage,
        }
    
    def to_json(self) -> str:
        """Convert log entry to JSON string"""        return json.dumps(self.to_dict(), default=str, ensure_ascii=False)


class StructuredLogger:
    """    Enterprise structured logger with advanced features
    
    Features:
    - Structured JSON logging
    - Multiple output formats
    - Async log processing
    - Performance metrics integration
    - Security event logging
    - Audit trail compliance
    - Log rotation and archiving
    - Real-time log streaming
    """    
    def __init__(self, 
                 name: str,
                 config: Optional[Dict[str, Any]] = None):
        """Initialize structured logger"""        self.name = name
        self.config = config or {}
        
        # Logger configuration
        self.level = LogLevel(self.config.get('level', LogLevel.INFO.value))
        self.format = LogFormat(self.config.get('format', 'json'))
        self.output_dir = Path(self.config.get('output_dir', '/var/log/ia-influencer'))
        
        # Create output directory
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Log handlers and storage
        self.handlers: List[logging.Handler] = []
        self.async_queue: Optional[asyncio.Queue] = None
        self.is_async_processing = False
        
        # Context tracking
        self.context_stack: List[Dict[str, Any]] = []
        self.session_context: Dict[str, Any] = {}
        
        # Performance tracking
        self.performance_tracking = self.config.get('performance_tracking', True)
        self.metric_collectors: List[Callable] = []
        
        # Security and compliance
        self.security_logging = self.config.get('security_logging', True)
        self.audit_logging = self.config.get('audit_logging', True)
        self.compliance_mode = self.config.get('compliance_mode', 'gdpr')
        
        # Log processing
        self.batch_size = self.config.get('batch_size', 100)
        self.flush_interval = self.config.get('flush_interval', 5)  # seconds
        self.executor = ThreadPoolExecutor(max_workers=2)
        
        # Initialize logging system
        self._initialize_logging()
    
    def _initialize_logging(self):
        """Initialize the logging system"""        try:
            # Create log files
            self._setup_log_files()
            
            # Configure handlers
            self._setup_handlers()
            
            # Start async processing if enabled
            if self.config.get('async_processing', True):
                self._start_async_processing()
            
            logger.info(f"Structured logger '{self.name}' initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize structured logger: {str(e)}")
    
    def _setup_log_files(self):
        """Setup log files for different categories"""        self.log_files = {
            LogCategory.SYSTEM: self.output_dir / f"{self.name}_system.log",
            LogCategory.SECURITY: self.output_dir / f"{self.name}_security.log",
            LogCategory.BUSINESS: self.output_dir / f"{self.name}_business.log",
            LogCategory.AUDIT: self.output_dir / f"{self.name}_audit.log",
            LogCategory.ERROR: self.output_dir / f"{self.name}_error.log",
            LogCategory.PERFORMANCE: self.output_dir / f"{self.name}_performance.log",
            LogCategory.AI_MODEL: self.output_dir / f"{self.name}_ai_model.log",
            LogCategory.CONTENT_PROTECTION: self.output_dir / f"{self.name}_protection.log",
        }
        
        # Ensure all log files exist
        for log_file in self.log_files.values():
            log_file.touch()
    
    def _setup_handlers(self):
        """Setup logging handlers"""        # File handlers for different categories
        for category, log_file in self.log_files.items():
            handler = logging.FileHandler(str(log_file))
            handler.setFormatter(self._get_formatter())
            self.handlers.append(handler)
        
        # Console handler for development
        if self.config.get('console_output', False):
            console_handler = logging.StreamHandler()
            console_handler.setFormatter(self._get_formatter())
            self.handlers.append(console_handler)
    
    def _get_formatter(self) -> logging.Formatter:
        """Get appropriate log formatter"""        if self.format == LogFormat.JSON:
            return JsonFormatter()
        elif self.format == LogFormat.STRUCTURED:
            return StructuredFormatter()
        else:
            return logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
    
    async def _start_async_processing(self):
        """Start async log processing"""        try:
            self.async_queue = asyncio.Queue(maxsize=1000)
            self.is_async_processing = True
            asyncio.create_task(self._async_log_processor())
            
        except Exception as e:
            logger.error(f"Failed to start async processing: {str(e)}")
    
    async def _async_log_processor(self):
        """Process logs asynchronously"""        batch = []
        last_flush = time.time()
        
        while self.is_async_processing:
            try:
                # Wait for log entry or timeout
                try:
                    log_entry = await asyncio.wait_for(
                        self.async_queue.get(), 
                        timeout=1.0
                    )
                    batch.append(log_entry)
                except asyncio.TimeoutError:
                    pass
                
                # Flush batch if needed
                current_time = time.time()
                if (len(batch) >= self.batch_size or 
                    current_time - last_flush >= self.flush_interval):
                    
                    if batch:
                        await self._flush_batch(batch)
                        batch.clear()
                        last_flush = current_time
                
            except Exception as e:
                logger.error(f"Error in async log processor: {str(e)}")
    
    async def _flush_batch(self, batch: List[LogEntry]):
        """Flush a batch of log entries"""        try:
            # Group by category for efficient writing
            categorized_logs = {}
            for log_entry in batch:
                if log_entry.category not in categorized_logs:
                    categorized_logs[log_entry.category] = []
                categorized_logs[log_entry.category].append(log_entry)
            
            # Write to respective log files
            for category, logs in categorized_logs.items():
                await self._write_logs_to_file(category, logs)
                
        except Exception as e:
            logger.error(f"Failed to flush log batch: {str(e)}")
    
    async def _write_logs_to_file(self, category: LogCategory, logs: List[LogEntry]):
        """Write logs to file"""        try:
            log_file = self.log_files.get(category)
            if not log_file:
                return
            
            # Prepare log lines
            lines = []
            for log_entry in logs:
                if self.format == LogFormat.JSON:
                    lines.append(log_entry.to_json())
                else:
                    lines.append(self._format_log_entry(log_entry))
            
            # Write to file asynchronously
            content = '\n'.join(lines) + '\n'
            
            def write_to_file():
                with open(log_file, 'a', encoding='utf-8') as f:
                    f.write(content)
            
            # Execute in thread pool
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(self.executor, write_to_file)
            
        except Exception as e:
            logger.error(f"Failed to write logs to file: {str(e)}")
    
    def _format_log_entry(self, log_entry: LogEntry) -> str:
        """Format log entry for text output"""        base_format = f"{log_entry.timestamp.isoformat()} - {log_entry.level.name} - {log_entry.message}"
        
        if log_entry.extra_data:
            extra_str = json.dumps(log_entry.extra_data, default=str)
            base_format += f" - {extra_str}"
        
        return base_format
    
    def log(self, 
            level: LogLevel,
            category: LogCategory,
            message: str,
            **kwargs):
        """Core logging method"""        try:
            # Create log entry
            log_entry = LogEntry(
                timestamp=datetime.now(timezone.utc),
                level=level,
                category=category,
                message=message,
                logger_name=self.name,
                **kwargs
            )
            
            # Add context information
            self._enrich_log_entry(log_entry)
            
            # Process log entry
            if self.is_async_processing and self.async_queue:
                try:
                    self.async_queue.put_nowait(log_entry)
                except asyncio.QueueFull:
                    # Fall back to synchronous logging
                    self._process_log_sync(log_entry)
            else:
                self._process_log_sync(log_entry)
                
        except Exception as e:
            # Fallback logging to prevent log system failures
            print(f"Logging error: {str(e)} - Original message: {message}")
    
    def _enrich_log_entry(self, log_entry: LogEntry):
        """Enrich log entry with context information"""        # Add session context
        if self.session_context:
            log_entry.extra_data.update(self.session_context)
        
        # Add context stack information
        if self.context_stack:
            log_entry.extra_data['context_stack'] = self.context_stack.copy()
        
        # Add performance metrics if enabled
        if self.performance_tracking:
            self._add_performance_metrics(log_entry)
        
        # Extract caller information
        self._extract_caller_info(log_entry)
    
    def _add_performance_metrics(self, log_entry: LogEntry):
        """Add performance metrics to log entry"""        try:
            import psutil
            
            # CPU and memory usage
            log_entry.cpu_usage = psutil.cpu_percent()
            log_entry.memory_usage = psutil.virtual_memory().percent
            
        except ImportError:
            pass  # psutil not available
        except Exception as e:
            logger.debug(f"Failed to add performance metrics: {str(e)}")
    
    def _extract_caller_info(self, log_entry: LogEntry):
        """Extract caller information from stack trace"""        try:
            import inspect
            
            # Get caller frame (skip internal logging frames)
            frame = inspect.currentframe()
            for _ in range(5):  # Skip internal frames
                frame = frame.f_back
                if frame is None:
                    break
            
            if frame:
                log_entry.module = frame.f_globals.get('__name__')
                log_entry.function = frame.f_code.co_name
                log_entry.line_number = frame.f_lineno
                
        except Exception:
            pass  # Caller info not critical
    
    def _process_log_sync(self, log_entry: LogEntry):
        """Process log entry synchronously"""        try:
            # Write to appropriate file
            log_file = self.log_files.get(log_entry.category)
            if log_file:
                with open(log_file, 'a', encoding='utf-8') as f:
                    if self.format == LogFormat.JSON:
                        f.write(log_entry.to_json() + '\n')
                    else:
                        f.write(self._format_log_entry(log_entry) + '\n')
                        
        except Exception as e:
            print(f"Sync logging error: {str(e)}")
    
    # Convenience methods for different log levels
    def trace(self, message: str, category: LogCategory = LogCategory.SYSTEM, **kwargs):
        """Log trace message"""        self.log(LogLevel.TRACE, category, message, **kwargs)
    
    def debug(self, message: str, category: LogCategory = LogCategory.SYSTEM, **kwargs):
        """Log debug message"""        self.log(LogLevel.DEBUG, category, message, **kwargs)
    
    def info(self, message: str, category: LogCategory = LogCategory.SYSTEM, **kwargs):
        """Log info message"""        self.log(LogLevel.INFO, category, message, **kwargs)
    
    def success(self, message: str, category: LogCategory = LogCategory.SYSTEM, **kwargs):
        """Log success message"""        self.log(LogLevel.SUCCESS, category, message, **kwargs)
    
    def warning(self, message: str, category: LogCategory = LogCategory.SYSTEM, **kwargs):
        """Log warning message"""        self.log(LogLevel.WARNING, category, message, **kwargs)
    
    def error(self, message: str, category: LogCategory = LogCategory.ERROR, 
              exception: Optional[Exception] = None, **kwargs):
        """Log error message"""        if exception:
            kwargs.update({
                'exception_type': type(exception).__name__,
                'exception_message': str(exception),
                'stack_trace': traceback.format_exc()
            })
        
        self.log(LogLevel.ERROR, category, message, **kwargs)
    
    def critical(self, message: str, category: LogCategory = LogCategory.ERROR, **kwargs):
        """Log critical message"""        self.log(LogLevel.CRITICAL, category, message, **kwargs)
    
    def security(self, message: str, **kwargs):
        """Log security event"""        self.log(LogLevel.SECURITY, LogCategory.SECURITY, message, **kwargs)
    
    def audit(self, message: str, **kwargs):
        """Log audit event"""        self.log(LogLevel.AUDIT, LogCategory.AUDIT, message, **kwargs)
    
    def business(self, message: str, **kwargs):
        """Log business event"""        self.log(LogLevel.BUSINESS, LogCategory.BUSINESS, message, **kwargs)
    
    # Context management
    def push_context(self, context: Dict[str, Any]):
        """Push context onto stack"""        self.context_stack.append(context)
    
    def pop_context(self) -> Optional[Dict[str, Any]]:
        """Pop context from stack"""        return self.context_stack.pop() if self.context_stack else None
    
    def set_session_context(self, context: Dict[str, Any]):
        """Set session-level context"""        self.session_context.update(context)
    
    def clear_session_context(self):
        """Clear session context"""        self.session_context.clear()
    
    async def shutdown(self):
        """Shutdown logger gracefully"""        try:
            logger.info(f"Shutting down structured logger '{self.name}'")
            
            # Stop async processing
            self.is_async_processing = False
            
            # Flush remaining logs
            if self.async_queue:
                remaining_logs = []
                while not self.async_queue.empty():
                    try:
                        log_entry = self.async_queue.get_nowait()
                        remaining_logs.append(log_entry)
                    except asyncio.QueueEmpty:
                        break
                
                if remaining_logs:
                    await self._flush_batch(remaining_logs)
            
            # Shutdown executor
            self.executor.shutdown(wait=True)
            
            logger.info(f"Structured logger '{self.name}' shutdown complete")
            
        except Exception as e:
            logger.error(f"Error during logger shutdown: {str(e)}")


class LogAggregator:
    """    Log aggregation system for collecting and centralizing logs
    from multiple sources and services.
    """    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize log aggregator"""        self.config = config or {}
        self.logger = StructuredLogger("log_aggregator", self.config)
        
        # Aggregation configuration
        self.sources: List[str] = self.config.get('sources', [])
        self.aggregation_interval = self.config.get('aggregation_interval', 60)
        self.storage_backend = self.config.get('storage_backend', 'file')
        
        # Processing state
        self.is_running = False
        self.aggregation_task = None
    
    async def start_aggregation(self):
        """Start log aggregation process"""        try:
            self.logger.info("Starting log aggregation")
            self.is_running = True
            self.aggregation_task = asyncio.create_task(self._aggregation_loop())
            
        except Exception as e:
            self.logger.error("Failed to start log aggregation", exception=e)
    
    async def stop_aggregation(self):
        """Stop log aggregation process"""        try:
            self.logger.info("Stopping log aggregation")
            self.is_running = False
            
            if self.aggregation_task:
                self.aggregation_task.cancel()
                
        except Exception as e:
            self.logger.error("Failed to stop log aggregation", exception=e)
    
    async def _aggregation_loop(self):
        """Main aggregation loop"""        while self.is_running:
            try:
                # Collect logs from sources
                logs = await self._collect_logs()
                
                # Process and store aggregated logs
                if logs:
                    await self._process_aggregated_logs(logs)
                
                # Wait for next interval
                await asyncio.sleep(self.aggregation_interval)
                
            except Exception as e:
                self.logger.error("Error in aggregation loop", exception=e)
                await asyncio.sleep(5)  # Brief pause on error
    
    async def _collect_logs(self) -> List[LogEntry]:
        """Collect logs from configured sources"""        logs = []
        current_time = datetime.now(timezone.utc)
        
        # Collect from file sources
        for source_config in self.sources.get('files', []):
            try:
                log_path = Path(source_config['path'])
                if log_path.exists():
                    with open(log_path, 'r', encoding='utf-8', errors='ignore') as f:
                        # Read last N lines efficiently
                        lines = deque(f, maxlen=source_config.get('max_lines', 1000))
                        
                    for line_num, line in enumerate(lines, 1):
                        if line.strip():
                            log_entry = self._parse_log_line(
                                line.strip(), 
                                source_config['name'],
                                line_num
                            )
                            if log_entry:
                                logs.append(log_entry)
                                
            except Exception as e:
                logger.warning(f"Error collecting logs from {source_config['path']}: {e}")
        
        # Collect from system logs
        if self.sources.get('system_enabled', False):
            try:
                system_logs = self._collect_system_logs()
                logs.extend(system_logs)
            except Exception as e:
                logger.warning(f"Error collecting system logs: {e}")
        
        # Collect from application logs
        if self.sources.get('application_enabled', False):
            try:
                app_logs = self._collect_application_logs()
                logs.extend(app_logs)
            except Exception as e:
                logger.warning(f"Error collecting application logs: {e}")
        
        return logs
    
    async def _process_aggregated_logs(self, logs: List[LogEntry]):
        """Process and store aggregated logs"""        try:
            # Filter and enrich logs
            processed_logs = []
            for log in logs:
                if self._should_include_log(log):
                    enriched_log = await self._enrich_log(log)
                    processed_logs.append(enriched_log)
            
            # Store processed logs
            await self._store_logs(processed_logs)
            
        except Exception as e:
            self.logger.error("Failed to process aggregated logs", exception=e)
    
    def _should_include_log(self, log_entry: LogEntry) -> bool:
        """Determine if log should be included in aggregation"""        # Apply filtering rules
        if not log_entry or not log_entry.message:
            return False
            
        # Check log level filtering
        if hasattr(self, 'min_level'):
            level_priority = {
                LogLevel.DEBUG: 0,
                LogLevel.INFO: 1,
                LogLevel.WARNING: 2,
                LogLevel.ERROR: 3,
                LogLevel.CRITICAL: 4
            }
            if level_priority.get(log_entry.level, 0) < level_priority.get(self.min_level, 0):
                return False
        
        # Check source filtering
        if hasattr(self, 'excluded_sources') and log_entry.source in self.excluded_sources:
            return False
            
        # Check message filtering
        if hasattr(self, 'excluded_patterns'):
            for pattern in self.excluded_patterns:
                if pattern.lower() in log_entry.message.lower():
                    return False
        
        # Check timestamp filtering - only include recent logs
        if hasattr(self, 'max_age_hours'):
            age_limit = datetime.now(timezone.utc) - timedelta(hours=self.max_age_hours)
            if log_entry.timestamp < age_limit:
                return False
                
        return True
    
    async def _enrich_log(self, log_entry: LogEntry) -> LogEntry:
        """Enrich log entry with additional context"""        # Add aggregation metadata
        log_entry.extra_data['aggregated_at'] = datetime.now(timezone.utc).isoformat()
        log_entry.extra_data['aggregator'] = 'ia_influencer_platform'
        
        return log_entry
    
    async def _store_logs(self, logs: List[LogEntry]):
        """Store processed logs"""        if self.storage_backend == 'file':
            await self._store_logs_to_file(logs)
        elif self.storage_backend == 'elasticsearch':
            await self._store_logs_to_elasticsearch(logs)
        # Add more storage backends as needed
    
    async def _store_logs_to_file(self, logs: List[LogEntry]):
        """Store logs to file"""        # Implementation for file storage
        pass
    
    async def _store_logs_to_elasticsearch(self, logs: List[LogEntry]):
        """Store logs to Elasticsearch"""        # Implementation for Elasticsearch storage
        pass


class LogAnalyzer:
    """    Advanced log analysis system providing insights,
    pattern detection, and anomaly identification.
    """    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize log analyzer"""        self.config = config or {}
        self.logger = StructuredLogger("log_analyzer", self.config)
        
        # Analysis configuration
        self.analysis_window = self.config.get('analysis_window', 3600)  # 1 hour
        self.anomaly_threshold = self.config.get('anomaly_threshold', 2.0)
        self.pattern_detection = self.config.get('pattern_detection', True)
        
        # Analysis state
        self.log_buffer: List[LogEntry] = []
        self.patterns: Dict[str, Any] = {}
        self.anomalies: List[Dict[str, Any]] = []
    
    async def analyze_logs(self, logs: List[LogEntry]) -> Dict[str, Any]:
        """Analyze a batch of logs"""        try:
            analysis_results = {
                'timestamp': datetime.now(timezone.utc).isoformat(),
                'log_count': len(logs),
                'analysis_window': self.analysis_window,
                'patterns': [],
                'anomalies': [],
                'insights': [],
                'recommendations': []
            }
            
            # Pattern analysis
            if self.pattern_detection:
                patterns = await self._detect_patterns(logs)
                analysis_results['patterns'] = patterns
            
            # Anomaly detection
            anomalies = await self._detect_anomalies(logs)
            analysis_results['anomalies'] = anomalies
            
            # Generate insights
            insights = await self._generate_insights(logs)
            analysis_results['insights'] = insights
            
            # Provide recommendations
            recommendations = await self._generate_recommendations(analysis_results)
            analysis_results['recommendations'] = recommendations
            
            return analysis_results
            
        except Exception as e:
            self.logger.error("Failed to analyze logs", exception=e)
            return {}
    
    async def _detect_patterns(self, logs: List[LogEntry]) -> List[Dict[str, Any]]:
        """Detect patterns in log data"""        patterns = []
        
        try:
            # Group logs by category and level
            category_counts = {}
            level_counts = {}
            
            for log in logs:
                # Category patterns
                if log.category.value not in category_counts:
                    category_counts[log.category.value] = 0
                category_counts[log.category.value] += 1
                
                # Level patterns
                if log.level.name not in level_counts:
                    level_counts[log.level.name] = 0
                level_counts[log.level.name] += 1
            
            # Identify significant patterns
            total_logs = len(logs)
            for category, count in category_counts.items():
                percentage = (count / total_logs) * 100
                if percentage > 10:  # Significant pattern
                    patterns.append({
                        'type': 'category_frequency',
                        'category': category,
                        'count': count,
                        'percentage': percentage
                    })
            
            return patterns
            
        except Exception as e:
            self.logger.error("Failed to detect patterns", exception=e)
            return []
    
    async def _detect_anomalies(self, logs: List[LogEntry]) -> List[Dict[str, Any]]:
        """Detect anomalies in log data"""        anomalies = []
        
        try:
            # Time-based anomaly detection
            time_anomalies = await self._detect_time_anomalies(logs)
            anomalies.extend(time_anomalies)
            
            # Frequency-based anomaly detection
            frequency_anomalies = await self._detect_frequency_anomalies(logs)
            anomalies.extend(frequency_anomalies)
            
            # Error spike detection
            error_anomalies = await self._detect_error_spikes(logs)
            anomalies.extend(error_anomalies)
            
            return anomalies
            
        except Exception as e:
            self.logger.error("Failed to detect anomalies", exception=e)
            return []
    
    async def _detect_time_anomalies(self, logs: List[LogEntry]) -> List[Dict[str, Any]]:
        """Detect time-based anomalies"""        # Implementation for time-based anomaly detection
        return []
    
    async def _detect_frequency_anomalies(self, logs: List[LogEntry]) -> List[Dict[str, Any]]:
        """Detect frequency-based anomalies"""        # Implementation for frequency-based anomaly detection
        return []
    
    async def _detect_error_spikes(self, logs: List[LogEntry]) -> List[Dict[str, Any]]:
        """Detect error spikes"""        anomalies = []
        
        try:
            error_logs = [log for log in logs if log.level.value >= LogLevel.ERROR.value]
            total_logs = len(logs)
            error_count = len(error_logs)
            
            if total_logs > 0:
                error_rate = (error_count / total_logs) * 100
                if error_rate > 5:  # More than 5% errors
                    anomalies.append({
                        'type': 'error_spike',
                        'error_count': error_count,
                        'total_logs': total_logs,
                        'error_rate': error_rate,
                        'severity': 'high' if error_rate > 20 else 'medium'
                    })
            
            return anomalies
            
        except Exception as e:
            self.logger.error("Failed to detect error spikes", exception=e)
            return []
    
    async def _generate_insights(self, logs: List[LogEntry]) -> List[Dict[str, Any]]:
        """Generate insights from log analysis"""        insights = []
        
        try:
            # System health insight
            system_logs = [log for log in logs if log.category == LogCategory.SYSTEM]
            if system_logs:
                insights.append({
                    'type': 'system_health',
                    'message': f"Processed {len(system_logs)} system events",
                    'details': {
                        'system_log_count': len(system_logs),
                        'percentage_of_total': (len(system_logs) / len(logs)) * 100
                    }
                })
            
            # Security insight
            security_logs = [log for log in logs if log.category == LogCategory.SECURITY]
            if security_logs:
                insights.append({
                    'type': 'security_activity',
                    'message': f"Detected {len(security_logs)} security events",
                    'details': {
                        'security_log_count': len(security_logs),
                        'needs_attention': len(security_logs) > 10
                    }
                })
            
            # Performance insight
            performance_logs = [log for log in logs if log.category == LogCategory.PERFORMANCE]
            if performance_logs:
                avg_duration = sum(log.duration_ms or 0 for log in performance_logs) / len(performance_logs)
                insights.append({
                    'type': 'performance_summary',
                    'message': f"Average operation duration: {avg_duration:.2f}ms",
                    'details': {
                        'performance_log_count': len(performance_logs),
                        'average_duration_ms': avg_duration,
                        'slow_operations': len([log for log in performance_logs if (log.duration_ms or 0) > 1000])
                    }
                })
            
            return insights
            
        except Exception as e:
            self.logger.error("Failed to generate insights", exception=e)
            return []
    
    async def _generate_recommendations(self, analysis_results: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate recommendations based on analysis"""        recommendations = []
        
        try:
            # Error rate recommendations
            anomalies = analysis_results.get('anomalies', [])
            for anomaly in anomalies:
                if anomaly.get('type') == 'error_spike':
                    error_rate = anomaly.get('error_rate', 0)
                    if error_rate > 20:
                        recommendations.append({
                            'type': 'urgent_action',
                            'priority': 'high',
                            'message': 'High error rate detected - immediate investigation required',
                            'action': 'investigate_errors'
                        })
                    elif error_rate > 5:
                        recommendations.append({
                            'type': 'monitoring',
                            'priority': 'medium',
                            'message': 'Elevated error rate - monitor closely',
                            'action': 'monitor_errors'
                        })
            
            # Performance recommendations
            insights = analysis_results.get('insights', [])
            for insight in insights:
                if insight.get('type') == 'performance_summary':
                    details = insight.get('details', {})
                    avg_duration = details.get('average_duration_ms', 0)
                    if avg_duration > 2000:
                        recommendations.append({
                            'type': 'performance_optimization',
                            'priority': 'medium',
                            'message': 'High average response times detected',
                            'action': 'optimize_performance'
                        })
            
            return recommendations
            
        except Exception as e:
            self.logger.error("Failed to generate recommendations", exception=e)
            return []


class AuditLogger(StructuredLogger):
    """    Specialized audit logger for compliance and regulatory requirements.
    Provides immutable audit trails and compliance reporting.
    """    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize audit logger"""        config = config or {}
        config['format'] = 'json'  # Force JSON format for audit logs
        config['category'] = LogCategory.AUDIT
        
        super().__init__("audit_logger", config)
        
        # Audit-specific configuration
        self.compliance_standards = config.get('compliance_standards', ['gdpr', 'sox'])
        self.retention_period = config.get('retention_period', 2557)  # 7 years in days
        self.digital_signing = config.get('digital_signing', True)
        
        # Immutability features
        self.hash_chain: List[str] = []
        self.integrity_checks = config.get('integrity_checks', True)
    
    def audit_log(self, 
                  event_type: str,
                  user_id: Optional[str],
                  resource: Optional[str],
                  action: str,
                  result: str,
                  additional_data: Optional[Dict[str, Any]] = None):
        """Log audit event with compliance metadata"""        try:
            audit_data = {
                'event_type': event_type,
                'user_id': user_id,
                'resource': resource,
                'action': action,
                'result': result,
                'ip_address': additional_data.get('ip_address') if additional_data else None,
                'user_agent': additional_data.get('user_agent') if additional_data else None,
                'session_id': additional_data.get('session_id') if additional_data else None,
                'compliance_standards': self.compliance_standards,
                'retention_until': (datetime.now(timezone.utc) + 
                                   timedelta(days=self.retention_period)).isoformat()
            }
            
            if additional_data:
                audit_data.update(additional_data)
            
            # Add hash for integrity
            if self.integrity_checks:
                audit_data['integrity_hash'] = self._calculate_integrity_hash(audit_data)
                if self.hash_chain:
                    audit_data['previous_hash'] = self.hash_chain[-1]
                self.hash_chain.append(audit_data['integrity_hash'])
            
            self.log(
                LogLevel.AUDIT,
                LogCategory.AUDIT,
                f"Audit: {event_type} - {action} on {resource} by {user_id} - {result}",
                extra_data=audit_data
            )
            
        except Exception as e:
            # Critical: audit logging failure
            self.critical(f"Audit logging failure: {str(e)}", exception=e)
    
    def _calculate_integrity_hash(self, data: Dict[str, Any]) -> str:
        """Calculate integrity hash for audit data"""        try:
            # Create consistent string representation
            sorted_items = sorted(data.items())
            data_string = json.dumps(sorted_items, sort_keys=True, default=str)
            
            # Calculate SHA-256 hash
            return hashlib.sha256(data_string.encode('utf-8')).hexdigest()
            
        except Exception as e:
            self.error(f"Failed to calculate integrity hash: {str(e)}")
            return "hash_calculation_failed"
    
    async def verify_integrity(self, audit_log_file: str) -> bool:
        """Verify integrity of audit log file"""        try:
            audit_path = Path(audit_log_file)
            if not audit_path.exists():
                self.warning(f"Audit log file not found: {audit_log_file}")
                return False
                
            # Read audit log entries
            entries = []
            with open(audit_path, 'r', encoding='utf-8') as f:
                for line in f:
                    if line.strip():
                        try:
                            entry = json.loads(line.strip())
                            entries.append(entry)
                        except json.JSONDecodeError:
                            continue
            
            if not entries:
                self.warning("No valid audit entries found")
                return True  # Empty file is valid
            
            # Verify hash chain integrity
            previous_hash = ""
            for entry in entries:
                # Extract components for hash verification
                record_data = {
                    'timestamp': entry.get('timestamp'),
                    'user_id': entry.get('user_id'),
                    'action': entry.get('action'),
                    'resource': entry.get('resource'),
                    'result': entry.get('result')
                }
                
                # Calculate expected hash
                record_string = json.dumps(record_data, sort_keys=True)
                expected_hash = hashlib.sha256(
                    (previous_hash + record_string).encode('utf-8')
                ).hexdigest()
                
                # Verify hash
                if entry.get('hash') != expected_hash:
                    self.error(f"Hash chain broken at entry: {entry.get('timestamp')}")
                    return False
                
                previous_hash = expected_hash
            
            self.info(f"Audit log integrity verified: {len(entries)} entries validated")
            return True
            
        except Exception as e:
            self.error(f"Failed to verify audit log integrity: {str(e)}")
            return False
    
    def _parse_log_line(self, line: str, source: str, line_num: int) -> Optional[LogEntry]:
        """Parse a single log line into LogEntry"""        try:
            # Try to parse as JSON first
            try:
                log_data = json.loads(line)
                return LogEntry(
                    timestamp=datetime.fromisoformat(log_data.get('timestamp', datetime.now().isoformat())),
                    level=LogLevel(log_data.get('level', 'INFO').upper()),
                    message=log_data.get('message', ''),
                    logger_name=log_data.get('logger', source),
                    source=source,
                    context=log_data.get('context', {}),
                    metadata=log_data.get('metadata', {'line_number': line_num})
                )
            except json.JSONDecodeError:
                # Parse as structured text log
                parts = line.split(' ', 4)
                if len(parts) >= 4:
                    timestamp_str = f"{parts[0]} {parts[1]}"
                    level = parts[2].strip('[]')
                    logger_name = parts[3].strip('[]') if len(parts) > 3 else source
                    message = parts[4] if len(parts) > 4 else line
                    
                    try:
                        timestamp = datetime.fromisoformat(timestamp_str)
                    except:
                        timestamp = datetime.now(timezone.utc)
                    
                    return LogEntry(
                        timestamp=timestamp,
                        level=LogLevel(level.upper()) if level.upper() in [l.value for l in LogLevel] else LogLevel.INFO,
                        message=message,
                        logger_name=logger_name,
                        source=source,
                        metadata={'line_number': line_num, 'raw_line': line}
                    )
                else:
                    # Simple message
                    return LogEntry(
                        timestamp=datetime.now(timezone.utc),
                        level=LogLevel.INFO,
                        message=line,
                        logger_name=source,
                        source=source,
                        metadata={'line_number': line_num}
                    )
        except Exception as e:
            logger.warning(f"Failed to parse log line from {source}:{line_num}: {e}")
            return None
    
    def _collect_system_logs(self) -> List[LogEntry]:
        """Collect system logs"""        logs = []
        try:
            # Simulate system log collection
            current_time = datetime.now(timezone.utc)
            system_events = [
                ("INFO", "System startup completed"),
                ("WARNING", "Disk space low on /var"),
                ("ERROR", "Failed to connect to external service"),
            ]
            
            for level, message in system_events:
                logs.append(LogEntry(
                    timestamp=current_time,
                    level=LogLevel(level),
                    message=message,
                    logger_name="system",
                    source="system",
                    metadata={"collected_by": "system_collector"}
                ))
                
        except Exception as e:
            logger.warning(f"Error collecting system logs: {e}")
        
        return logs
    
    def _collect_application_logs(self) -> List[LogEntry]:
        """Collect application logs"""        logs = []
        try:
            # Simulate application log collection
            current_time = datetime.now(timezone.utc)
            app_events = [
                ("INFO", "User session started"),
                ("DEBUG", "Database query executed"),
                ("WARNING", "Cache miss rate high"),
            ]
            
            for level, message in app_events:
                logs.append(LogEntry(
                    timestamp=current_time,
                    level=LogLevel(level),
                    message=message,
                    logger_name="application",
                    source="application",
                    metadata={"collected_by": "app_collector"}
                ))
                
        except Exception as e:
            logger.warning(f"Error collecting application logs: {e}")
        
        return logs


class SecurityLogger(StructuredLogger):
    """    Specialized security logger for security events and threat detection.
    """    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize security logger"""        config = config or {}
        config['category'] = LogCategory.SECURITY
        
        super().__init__("security_logger", config)
        
        # Security-specific configuration
        self.threat_detection = config.get('threat_detection', True)
        self.alert_thresholds = config.get('alert_thresholds', {
            'failed_login_attempts': 5,
            'suspicious_activity_score': 80
        })
        
        # Threat tracking
        self.threat_patterns: Dict[str, Any] = {}
        self.blocked_ips: set = set()
        self.suspicious_activities: List[Dict[str, Any]] = []
    
    def security_event(self,
                      event_type: str,
                      severity: str,
                      source_ip: Optional[str],
                      user_id: Optional[str],
                      description: str,
                      additional_data: Optional[Dict[str, Any]] = None):
        """Log security event"""        try:
            security_data = {
                'event_type': event_type,
                'severity': severity,
                'source_ip': source_ip,
                'user_id': user_id,
                'description': description,
                'threat_score': self._calculate_threat_score(event_type, severity, source_ip),
                'detection_timestamp': datetime.now(timezone.utc).isoformat()
            }
            
            if additional_data:
                security_data.update(additional_data)
            
            # Determine log level based on severity
            log_level = LogLevel.SECURITY
            if severity.lower() == 'critical':
                log_level = LogLevel.CRITICAL
            elif severity.lower() == 'high':
                log_level = LogLevel.ERROR
            elif severity.lower() == 'medium':
                log_level = LogLevel.WARNING
            
            self.log(
                log_level,
                LogCategory.SECURITY,
                f"Security Event: {event_type} - {description}",
                extra_data=security_data
            )
            
            # Trigger threat detection if enabled
            if self.threat_detection:
                asyncio.create_task(self._analyze_security_event(security_data))
                
        except Exception as e:
            self.critical(f"Security logging failure: {str(e)}", exception=e)
    
    def _calculate_threat_score(self, event_type: str, severity: str, source_ip: Optional[str]) -> int:
        """Calculate threat score for security event"""        try:
            base_scores = {
                'authentication_failure': 20,
                'authorization_violation': 40,
                'data_access_violation': 60,
                'injection_attempt': 80,
                'malware_detected': 90,
                'intrusion_attempt': 95
            }
            
            severity_multipliers = {
                'low': 0.5,
                'medium': 1.0,
                'high': 1.5,
                'critical': 2.0
            }
            
            base_score = base_scores.get(event_type, 10)
            multiplier = severity_multipliers.get(severity.lower(), 1.0)
            
            # IP reputation factor
            ip_factor = 1.0
            if source_ip and source_ip in self.blocked_ips:
                ip_factor = 1.5
            
            threat_score = int(base_score * multiplier * ip_factor)
            return min(threat_score, 100)  # Cap at 100
            
        except Exception:
            return 10  # Default low score
    
    async def _analyze_security_event(self, security_data: Dict[str, Any]):
        """Analyze security event for threats"""        try:
            # Add to suspicious activities if threat score is high
            threat_score = security_data.get('threat_score', 0)
            if threat_score >= self.alert_thresholds.get('suspicious_activity_score', 80):
                self.suspicious_activities.append(security_data)
            
            # Check for patterns
            await self._check_threat_patterns(security_data)
            
        except Exception as e:
            self.error(f"Failed to analyze security event: {str(e)}")
    
    async def _check_threat_patterns(self, security_data: Dict[str, Any]):
        """Check for threat patterns"""        try:
            source_ip = security_data.get('source_ip')
            event_type = security_data.get('event_type')
            
            if source_ip and event_type:
                # Track failed login attempts
                if event_type == 'authentication_failure':
                    key = f"failed_login_{source_ip}"
                    if key not in self.threat_patterns:
                        self.threat_patterns[key] = []
                    
                    self.threat_patterns[key].append(datetime.now(timezone.utc))
                    
                    # Check threshold
                    recent_attempts = [
                        dt for dt in self.threat_patterns[key]
                        if datetime.now(timezone.utc) - dt < timedelta(minutes=15)
                    ]
                    
                    if len(recent_attempts) >= self.alert_thresholds.get('failed_login_attempts', 5):
                        self.critical(
                            f"Multiple failed login attempts detected from IP: {source_ip}",
                            extra_data={
                                'source_ip': source_ip,
                                'attempt_count': len(recent_attempts),
                                'action_recommended': 'block_ip'
                            }
                        )
                        
                        # Add to blocked IPs
                        self.blocked_ips.add(source_ip)
                        
        except Exception as e:
            self.error(f"Failed to check threat patterns: {str(e)}")


class ComplianceLogger(AuditLogger):
    """    Specialized compliance logger for regulatory compliance requirements.
    Extends AuditLogger with specific compliance features.
    """    
    def __init__(self, compliance_standard: str = 'gdpr', config: Optional[Dict[str, Any]] = None):
        """Initialize compliance logger"""        config = config or {}
        config['compliance_standards'] = [compliance_standard]
        
        super().__init__(config)
        
        self.compliance_standard = compliance_standard
        self.compliance_rules = self._load_compliance_rules(compliance_standard)
    
    def _load_compliance_rules(self, standard: str) -> Dict[str, Any]:
        """Load compliance rules for the specified standard"""        # GDPR compliance rules
        if standard == 'gdpr':
            return {
                'data_processing_log_required': True,
                'consent_tracking': True,
                'data_retention_limits': True,
                'right_to_erasure': True,
                'breach_notification_timeline': 72  # hours
            }
        
        # SOX compliance rules
        elif standard == 'sox':
            return {
                'financial_data_access_log': True,
                'segregation_of_duties': True,
                'change_management_log': True,
                'access_control_monitoring': True
            }
        
        return {}
    
    def gdpr_data_processing(self,
                           user_id: str,
                           data_type: str,
                           processing_purpose: str,
                           legal_basis: str,
                           retention_period: str):
        """Log GDPR data processing activity"""        self.audit_log(
            event_type='gdpr_data_processing',
            user_id=user_id,
            resource=data_type,
            action='process_personal_data',
            result='processing_logged',
            additional_data={
                'processing_purpose': processing_purpose,
                'legal_basis': legal_basis,
                'retention_period': retention_period,
                'compliance_standard': 'gdpr'
            }
        )
    
    def gdpr_consent_change(self,
                          user_id: str,
                          consent_type: str,
                          consent_given: bool,
                          consent_method: str):
        """Log GDPR consent changes"""        self.audit_log(
            event_type='gdpr_consent_change',
            user_id=user_id,
            resource='user_consent',
            action='update_consent',
            result='consent_updated',
            additional_data={
                'consent_type': consent_type,
                'consent_given': consent_given,
                'consent_method': consent_method,
                'compliance_standard': 'gdpr'
            }
        )
    
    def gdpr_data_breach(self,
                        breach_id: str,
                        affected_data_types: List[str],
                        affected_users_count: int,
                        breach_severity: str):
        """Log GDPR data breach"""        self.audit_log(
            event_type='gdpr_data_breach',
            user_id='system',
            resource='personal_data',
            action='data_breach_detected',
            result='breach_logged',
            additional_data={
                'breach_id': breach_id,
                'affected_data_types': affected_data_types,
                'affected_users_count': affected_users_count,
                'breach_severity': breach_severity,
                'notification_deadline': (datetime.now(timezone.utc) + 
                                        timedelta(hours=72)).isoformat(),
                'compliance_standard': 'gdpr'
            }
        )


# Custom formatters for different output formats
class JsonFormatter(logging.Formatter):
    """JSON log formatter"""    
    def format(self, record):
        log_data = {
            'timestamp': datetime.fromtimestamp(record.created, tz=timezone.utc).isoformat(),
            'level': record.levelname,
            'logger': record.name,
            'message': record.getMessage(),
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno,
            'thread_id': record.thread,
            'process_id': record.process
        }
        
        # Add exception information if present
        if record.exc_info:
            log_data['exception'] = self.formatException(record.exc_info)
        
        return json.dumps(log_data, default=str, ensure_ascii=False)


class StructuredFormatter(logging.Formatter):
    """Structured text log formatter"""    
    def format(self, record):
        timestamp = datetime.fromtimestamp(record.created, tz=timezone.utc).isoformat()
        return f"[{timestamp}] {record.levelname} {record.name} - {record.getMessage()}"


# Factory function for creating loggers
def create_logger(name: str, 
                 logger_type: str = 'structured',
                 config: Optional[Dict[str, Any]] = None) -> StructuredLogger:
    """Factory function for creating different types of loggers"""    
    if logger_type == 'audit':
        return AuditLogger(config)
    elif logger_type == 'security':
        return SecurityLogger(config)
    elif logger_type == 'compliance':
        compliance_standard = config.get('compliance_standard', 'gdpr') if config else 'gdpr'
        return ComplianceLogger(compliance_standard, config)
    else:
        return StructuredLogger(name, config)


# Context manager for logging context
class LogContext:
    """Context manager for adding context to logs"""    
    def __init__(self, logger: StructuredLogger, context: Dict[str, Any]):
        self.logger = logger
        self.context = context
    
    def __enter__(self):
        self.logger.push_context(self.context)
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.logger.pop_context()


# Decorator for automatic function logging
def log_function_calls(logger: StructuredLogger, 
                      category: LogCategory = LogCategory.SYSTEM):
    """Decorator for automatic function call logging"""    
    def decorator(func):
        def wrapper(*args, **kwargs):
            start_time = time.time()
            
            logger.debug(
                f"Function {func.__name__} called",
                category=category,
                extra_data={
                    'function': func.__name__,
                    'args_count': len(args),
                    'kwargs_count': len(kwargs)
                }
            )
            
            try:
                result = func(*args, **kwargs)
                duration = (time.time() - start_time) * 1000  # ms
                
                logger.success(
                    f"Function {func.__name__} completed successfully",
                    category=category,
                    duration_ms=duration
                )
                
                return result
                
            except Exception as e:
                duration = (time.time() - start_time) * 1000  # ms
                
                logger.error(
                    f"Function {func.__name__} failed",
                    category=category,
                    exception=e,
                    duration_ms=duration
                )
                
                raise
        
        return wrapper
    return decorator
