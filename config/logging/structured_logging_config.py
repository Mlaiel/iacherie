"""Structured Logging Configuration for IA-Influencer Agent Platform
===============================================================

Advanced structured logging with context management, correlation tracking,
and multi-format content processing metadata enrichment.

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
import uuid
import time
import threading
from contextlib import contextmanager
from datetime import datetime, timezone
from typing import Dict, Any, Optional, Union, List, Callable
from dataclasses import dataclass, field, asdict
from enum import Enum
import contextvars

import structlog
from structlog import processors, stdlib, dev
from structlog.contextvars import bind_contextvars, clear_contextvars


class EventType(str, Enum):
    """
Standard event types for structured logging"""
    # Platform Events
    PLATFORM_START = "platform.start"
    PLATFORM_STOP = "platform.stop"
    PLATFORM_ERROR = "platform.error"
    
    # API Events
    API_REQUEST = "api.request"
    API_RESPONSE = "api.response"
    API_ERROR = "api.error"
    API_TIMEOUT = "api.timeout"
    
    # Authentication Events
    AUTH_LOGIN = "auth.login"
    AUTH_LOGOUT = "auth.logout"
    AUTH_FAILED = "auth.failed"
    AUTH_TOKEN_REFRESH = "auth.token_refresh"
    AUTH_UNAUTHORIZED = "auth.unauthorized"
    
    # Content Processing Events
    CONTENT_UPLOAD = "content.upload"
    CONTENT_PROCESSED = "content.processed"
    CONTENT_FINGERPRINT_CREATED = "content.fingerprint_created"
    CONTENT_PROTECTION_ENABLED = "content.protection_enabled"
    CONTENT_VIOLATION_DETECTED = "content.violation_detected"
    
    # AI Processing Events
    AI_MODEL_LOADED = "ai.model_loaded"
    AI_INFERENCE_START = "ai.inference_start"
    AI_INFERENCE_COMPLETE = "ai.inference_complete"
    AI_INFERENCE_ERROR = "ai.inference_error"
    
    # Audio Processing Events
    AUDIO_FINGERPRINT_GENERATED = "audio.fingerprint_generated"
    AUDIO_ANALYSIS_COMPLETE = "audio.analysis_complete"
    AUDIO_MATCHING_FOUND = "audio.matching_found"
    
    # Video Processing Events
    VIDEO_FRAME_EXTRACTED = "video.frame_extracted"
    VIDEO_FINGERPRINT_GENERATED = "video.fingerprint_generated"
    VIDEO_ANALYSIS_COMPLETE = "video.analysis_complete"
    
    # Image Processing Events
    IMAGE_FINGERPRINT_GENERATED = "image.fingerprint_generated"
    IMAGE_SIMILARITY_CHECK = "image.similarity_check"
    IMAGE_MATCHING_FOUND = "image.matching_found"
    
    # Text Processing Events
    TEXT_FINGERPRINT_GENERATED = "text.fingerprint_generated"
    TEXT_SIMILARITY_CHECK = "text.similarity_check"
    TEXT_PLAGIARISM_DETECTED = "text.plagiarism_detected"
    
    # Database Events
    DB_QUERY_START = "db.query_start"
    DB_QUERY_COMPLETE = "db.query_complete"
    DB_QUERY_ERROR = "db.query_error"
    DB_TRANSACTION_START = "db.transaction_start"
    DB_TRANSACTION_COMMIT = "db.transaction_commit"
    DB_TRANSACTION_ROLLBACK = "db.transaction_rollback"
    
    # Cache Events
    CACHE_HIT = "cache.hit"
    CACHE_MISS = "cache.miss"
    CACHE_SET = "cache.set"
    CACHE_DELETE = "cache.delete"
    CACHE_FLUSH = "cache.flush"
    
    # Security Events
    SECURITY_THREAT_DETECTED = "security.threat_detected"
    SECURITY_ACCESS_DENIED = "security.access_denied"
    SECURITY_SUSPICIOUS_ACTIVITY = "security.suspicious_activity"
    SECURITY_BREACH_ATTEMPT = "security.breach_attempt"
    
    # Business Events
    MONETIZATION_REVENUE_CALCULATED = "monetization.revenue_calculated"
    COLLABORATION_REQUEST = "collaboration.request"
    DISTRIBUTION_STARTED = "distribution.started"
    DISTRIBUTION_COMPLETE = "distribution.complete"
    
    # External Integration Events
    SPOTIFY_API_CALL = "spotify.api_call"
    YOUTUBE_API_CALL = "youtube.api_call"
    INSTAGRAM_API_CALL = "instagram.api_call"
    TIKTOK_API_CALL = "tiktok.api_call"
    
    # Performance Events
    PERFORMANCE_METRIC = "performance.metric"
    PERFORMANCE_ALERT = "performance.alert"
    PERFORMANCE_THRESHOLD_EXCEEDED = "performance.threshold_exceeded"


@dataclass
class RequestContext:
    """Request context for correlation and tracking"""
    request_id: str
    user_id: Optional[str] = None
    tenant_id: Optional[str] = None
    session_id: Optional[str] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    endpoint: Optional[str] = None
    method: Optional[str] = None
    trace_id: Optional[str] = None
    span_id: Optional[str] = None


@dataclass
class ContentContext:
    """
Content processing context"""
    content_id: Optional[str] = None
    content_type: Optional[str] = None  # audio, video, image, text
    content_format: Optional[str] = None  # mp3, mp4, jpg, txt
    file_size: Optional[int] = None
    duration: Optional[float] = None
    fingerprint_id: Optional[str] = None
    processing_pipeline: Optional[str] = None


@dataclass
class AIContext:
    """
AI processing context"""
    model_name: Optional[str] = None
    model_version: Optional[str] = None
    inference_type: Optional[str] = None
    input_shape: Optional[tuple] = None
    output_shape: Optional[tuple] = None
    processing_time: Optional[float] = None
    confidence_score: Optional[float] = None


@dataclass
class PerformanceContext:
    """
Performance monitoring context"""
    operation: Optional[str] = None
    start_time: Optional[float] = None
    end_time: Optional[float] = None
    duration: Optional[float] = None
    cpu_usage: Optional[float] = None
    memory_usage: Optional[float] = None
    disk_io: Optional[Dict[str, float]] = None
    network_io: Optional[Dict[str, float]] = None


@dataclass
class SecurityContext:
    """
Security context for threat tracking"""
    threat_level: Optional[str] = None
    attack_type: Optional[str] = None
    source_ip: Optional[str] = None
    blocked: Optional[bool] = None
    rule_triggered: Optional[str] = None
    evidence: Optional[Dict[str, Any]] = None


class StructuredLoggingConfig:
    """
    Advanced structured logging configuration for IA-Influencer platform.
    
    Provides context management, correlation tracking, and metadata enrichment
    for comprehensive observability across multi-format content processing.
    """
    
    def __init__(
        self,
        enable_context_vars: bool = True,
        enable_correlation: bool = True,
        enable_performance_tracking: bool = True,
        enable_security_context: bool = True,
        custom_processors: Optional[List[Callable]] = None,
        exclude_keys: Optional[List[str]] = None
    ):
        """
        Initialize structured logging configuration.
        
        Args:
            enable_context_vars: Enable context variables support
            enable_correlation: Enable correlation ID tracking
            enable_performance_tracking: Enable performance metrics
            enable_security_context: Enable security context enrichment
            custom_processors: Custom structlog processors
            exclude_keys: Keys to exclude from log records
        """
        self.enable_context_vars = enable_context_vars
        self.enable_correlation = enable_correlation
        self.enable_performance_tracking = enable_performance_tracking
        self.enable_security_context = enable_security_context
        self.custom_processors = custom_processors or []
        self.exclude_keys = exclude_keys or []
        
        # Context variables for thread-local storage
        if self.enable_context_vars:
            self.request_context: contextvars.ContextVar[Optional[RequestContext]] = \
                contextvars.ContextVar('request_context', default=None)
            self.content_context: contextvars.ContextVar[Optional[ContentContext]] = \
                contextvars.ContextVar('content_context', default=None)
            self.ai_context: contextvars.ContextVar[Optional[AIContext]] = \
                contextvars.ContextVar('ai_context', default=None)
            self.performance_context: contextvars.ContextVar[Optional[PerformanceContext]] = \
                contextvars.ContextVar('performance_context', default=None)
            self.security_context: contextvars.ContextVar[Optional[SecurityContext]] = \
                contextvars.ContextVar('security_context', default=None)
        
        # Thread-local storage for non-async contexts
        self._thread_local = threading.local()
        
        # Initialize processors
        self._configure_processors()
    
    def _configure_processors(self) -> None:
        """
Configure structlog processors"""
        processors_list = [
            # Standard processors
            stdlib.filter_by_level,
            stdlib.add_logger_name,
            stdlib.add_log_level,
            stdlib.PositionalArgumentsFormatter(),
            
            # Custom processors
            self._add_timestamp_processor,
            self._add_correlation_processor,
            self._add_context_processor,
            self._add_performance_processor,
            self._add_security_processor,
            self._filter_sensitive_data_processor,
            
            # Stack info and exception formatting
            processors.StackInfoRenderer(),
            processors.format_exc_info,
            processors.UnicodeDecoder(),
        ]
        
        # Add custom processors
        processors_list.extend(self.custom_processors)
        
        # Final formatting processor
        processors_list.append(processors.JSONRenderer())
        
        # Configure structlog
        structlog.configure(
            processors=processors_list,
            wrapper_class=stdlib.BoundLogger,
            logger_factory=stdlib.LoggerFactory(),
            context_class=dict,
            cache_ctor_on_first_use=True,
        )
    
    def _add_timestamp_processor(self, logger, method_name, event_dict):
        """
Add ISO timestamp to log records"""
        event_dict['timestamp'] = datetime.now(timezone.utc).isoformat()
        return event_dict
    
    def _add_correlation_processor(self, logger, method_name, event_dict):
        """
Add correlation tracking information"""
        if not self.enable_correlation:
            return event_dict
        
        # Add correlation ID if not present
        if 'correlation_id' not in event_dict:
            correlation_id = getattr(self._thread_local, 'correlation_id', None)
            if correlation_id:
                event_dict['correlation_id'] = correlation_id
            else:
                event_dict['correlation_id'] = str(uuid.uuid4())
        
        return event_dict
    
    def _add_context_processor(self, logger, method_name, event_dict):
        """
Add context information from context variables"""
        if not self.enable_context_vars:
            return event_dict
        
        # Add request context
        if hasattr(self, 'request_context'):
            request_ctx = self.request_context.get(None)
            if request_ctx:
                ctx_dict = asdict(request_ctx)
                ctx_dict = {k: v for k, v in ctx_dict.items() if v is not None}
                event_dict.update(ctx_dict)
        
        # Add content context
        if hasattr(self, 'content_context'):
            content_ctx = self.content_context.get(None)
            if content_ctx:
                ctx_dict = asdict(content_ctx)
                ctx_dict = {k: v for k, v in ctx_dict.items() if v is not None}
                event_dict.update(ctx_dict)
        
        # Add AI context
        if hasattr(self, 'ai_context'):
            ai_ctx = self.ai_context.get(None)
            if ai_ctx:
                ctx_dict = asdict(ai_ctx)
                ctx_dict = {k: v for k, v in ctx_dict.items() if v is not None}
                event_dict.update(ctx_dict)
        
        return event_dict
    
    def _add_performance_processor(self, logger, method_name, event_dict):
        """
Add performance metrics"""
        if not self.enable_performance_tracking:
            return event_dict
        
        if hasattr(self, 'performance_context'):
            perf_ctx = self.performance_context.get(None)
            if perf_ctx:
                ctx_dict = asdict(perf_ctx)
                ctx_dict = {k: v for k, v in ctx_dict.items() if v is not None}
                event_dict.update(ctx_dict)
        
        return event_dict
    
    def _add_security_processor(self, logger, method_name, event_dict):
        """
Add security context"""
        if not self.enable_security_context:
            return event_dict
        
        if hasattr(self, 'security_context'):
            sec_ctx = self.security_context.get(None)
            if sec_ctx:
                ctx_dict = asdict(sec_ctx)
                ctx_dict = {k: v for k, v in ctx_dict.items() if v is not None}
                event_dict.update(ctx_dict)
        
        return event_dict
    
    def _filter_sensitive_data_processor(self, logger, method_name, event_dict):
        """
Filter sensitive data from log records"""
        sensitive_keys = [
            'password', 'token', 'secret', 'key', 'auth',
            'credential', 'api_key', 'private_key'
        ]
        
        # Remove or mask sensitive data
        for key in list(event_dict.keys()):
            if any(sensitive in key.lower() for sensitive in sensitive_keys):
                event_dict[key] = '[REDACTED]'
            elif key in self.exclude_keys:
                del event_dict[key]
        
        return event_dict
    
    def set_request_context(self, context: RequestContext) -> None:
        """
Set request context for current execution"""
        if self.enable_context_vars and hasattr(self, 'request_context'):
            self.request_context.set(context)
        else:
            self._thread_local.request_context = context
    
    def get_request_context(self) -> Optional[RequestContext]:
        """
Get current request context"""
        if self.enable_context_vars and hasattr(self, 'request_context'):
            return self.request_context.get(None)
        return getattr(self._thread_local, 'request_context', None)
    
    def set_content_context(self, context: ContentContext) -> None:
        """
Set content processing context"""
        if self.enable_context_vars and hasattr(self, 'content_context'):
            self.content_context.set(context)
        else:
            self._thread_local.content_context = context
    
    def get_content_context(self) -> Optional[ContentContext]:
        """
Get current content context"""
        if self.enable_context_vars and hasattr(self, 'content_context'):
            return self.content_context.get(None)
        return getattr(self._thread_local, 'content_context', None)
    
    def set_ai_context(self, context: AIContext) -> None:
        """
Set AI processing context"""
        if self.enable_context_vars and hasattr(self, 'ai_context'):
            self.ai_context.set(context)
        else:
            self._thread_local.ai_context = context
    
    def get_ai_context(self) -> Optional[AIContext]:
        """
Get current AI context"""
        if self.enable_context_vars and hasattr(self, 'ai_context'):
            return self.ai_context.get(None)
        return getattr(self._thread_local, 'ai_context', None)
    
    def set_performance_context(self, context: PerformanceContext) -> None:
        """
Set performance monitoring context"""
        if self.enable_context_vars and hasattr(self, 'performance_context'):
            self.performance_context.set(context)
        else:
            self._thread_local.performance_context = context
    
    def get_performance_context(self) -> Optional[PerformanceContext]:
        """
Get current performance context"""
        if self.enable_context_vars and hasattr(self, 'performance_context'):
            return self.performance_context.get(None)
        return getattr(self._thread_local, 'performance_context', None)
    
    def set_security_context(self, context: SecurityContext) -> None:
        """
Set security context"""
        if self.enable_context_vars and hasattr(self, 'security_context'):
            self.security_context.set(context)
        else:
            self._thread_local.security_context = context
    
    def get_security_context(self) -> Optional[SecurityContext]:
        """
Get current security context"""
        if self.enable_context_vars and hasattr(self, 'security_context'):
            return self.security_context.get(None)
        return getattr(self._thread_local, 'security_context', None)
    
    def set_correlation_id(self, correlation_id: str) -> None:
        """
Set correlation ID for request tracking"""
        if self.enable_context_vars:
            bind_contextvars(correlation_id=correlation_id)
        else:
            self._thread_local.correlation_id = correlation_id
    
    def get_correlation_id(self) -> Optional[str]:
        """
Get current correlation ID"""
        if self.enable_context_vars:
            try:
                return structlog.get_logger().bind().context.get('correlation_id')
            except:
                pass
        return getattr(self._thread_local, 'correlation_id', None)
    
    def clear_context(self) -> None:
        """
Clear all context information"""
        if self.enable_context_vars:
            clear_contextvars()
            
            # Clear context vars
            if hasattr(self, 'request_context'):
                self.request_context.set(None)
            if hasattr(self, 'content_context'):
                self.content_context.set(None)
            if hasattr(self, 'ai_context'):
                self.ai_context.set(None)
            if hasattr(self, 'performance_context'):
                self.performance_context.set(None)
            if hasattr(self, 'security_context'):
                self.security_context.set(None)
        
        # Clear thread local
        if hasattr(self._thread_local, '__dict__'):
            self._thread_local.__dict__.clear()
    
    @contextmanager
    def request_context_manager(self, context: RequestContext):
        """
Context manager for request scope"""
        old_context = self.get_request_context()
        self.set_request_context(context)
        try:
            yield
        finally:
            if old_context:
                self.set_request_context(old_context)
            else:
                if self.enable_context_vars and hasattr(self, 'request_context'):
                    self.request_context.set(None)
    
    @contextmanager
    def content_context_manager(self, context: ContentContext):
        """
Context manager for content processing scope"""
        old_context = self.get_content_context()
        self.set_content_context(context)
        try:
            yield
        finally:
            if old_context:
                self.set_content_context(old_context)
            else:
                if self.enable_context_vars and hasattr(self, 'content_context'):
                    self.content_context.set(None)
    
    @contextmanager
    def ai_context_manager(self, context: AIContext):
        """
Context manager for AI processing scope"""
        old_context = self.get_ai_context()
        self.set_ai_context(context)
        try:
            yield
        finally:
            if old_context:
                self.set_ai_context(old_context)
            else:
                if self.enable_context_vars and hasattr(self, 'ai_context'):
                    self.ai_context.set(None)
    
    @contextmanager
    def performance_context_manager(self, operation: str):
        """
Context manager for performance monitoring"""
        start_time = time.time()
        context = PerformanceContext(
            operation=operation,
            start_time=start_time
        )
        
        old_context = self.get_performance_context()
        self.set_performance_context(context)
        try:
            yield context
        finally:
            end_time = time.time()
            context.end_time = end_time
            context.duration = end_time - start_time
            
            if old_context:
                self.set_performance_context(old_context)
            else:
                if self.enable_context_vars and hasattr(self, 'performance_context'):
                    self.performance_context.set(None)
    
    @contextmanager
    def security_context_manager(self, context: SecurityContext):
        """
Context manager for security monitoring"""
        old_context = self.get_security_context()
        self.set_security_context(context)
        try:
            yield
        finally:
            if old_context:
                self.set_security_context(old_context)
            else:
                if self.enable_context_vars and hasattr(self, 'security_context'):
                    self.security_context.set(None)
    
    def log_event(
        self,
        logger: structlog.BoundLogger,
        event_type: Union[str, EventType],
        message: str,
        level: str = 'info',
        **kwargs
    ) -> None:
        """
        Log a structured event with context.
        
        Args:
            logger: Structured logger instance
            event_type: Type of event
            message: Event message
            level: Log level
            **kwargs: Additional event data
        """
        event_data = {
            'event_type': event_type.value if isinstance(event_type, EventType) else event_type,
            'message': message,
            **kwargs
        }
        
        # Get the appropriate log method
        log_method = getattr(logger, level.lower(), logger.info)
        log_method(**event_data)
    
    def get_logger(self, name: str) -> structlog.BoundLogger:
        """
        Get a structured logger with current context.
        
        Args:
            name: Logger name
            
        Returns:
            Bound structured logger
        """
        logger = structlog.get_logger(name)
        
        # Bind current context if available
        context = {}
        
        if self.get_correlation_id():
            context['correlation_id'] = self.get_correlation_id()
        
        request_ctx = self.get_request_context()
        if request_ctx:
            context.update({k: v for k, v in asdict(request_ctx).items() if v is not None})
        
        if context:
            logger = logger.bind(**context)
        
        return logger
    
    def create_child_logger(
        self,
        parent_logger: structlog.BoundLogger,
        **context
    ) -> structlog.BoundLogger:
        """
        Create a child logger with additional context.
        
        Args:
            parent_logger: Parent logger
            **context: Additional context to bind
            
        Returns:
            Child logger with inherited and additional context
        """
        return parent_logger.bind(**context)


# Global structured logging configuration
_structured_config: Optional[StructuredLoggingConfig] = None


def initialize_structured_logging(
    config: Optional[StructuredLoggingConfig] = None
) -> StructuredLoggingConfig:
    """
    Initialize global structured logging configuration.
    
    Args:
        config: Custom StructuredLoggingConfig instance
        
    Returns:
        Initialized configuration
    """
    global _structured_config
    
    if config:
        _structured_config = config
    else:
        _structured_config = StructuredLoggingConfig()
    
    return _structured_config


def get_structured_config() -> StructuredLoggingConfig:
    """
Get the global structured logging configuration"""
    if not _structured_config:
        initialize_structured_logging()
    
    return _structured_config


def get_structured_logger(name: str) -> structlog.BoundLogger:
    """
    Get a structured logger with global configuration.
    
    Args:
        name: Logger name
        
    Returns:
        Structured logger instance
    """
    config = get_structured_config()
    return config.get_logger(name)
