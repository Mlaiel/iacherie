#!/usr/bin/env python3
"""🎯 Processing Exceptions - Centralized Error Handling System
================================================================================
Module: backend/media_processing/processing_exceptions.py
Author: Fahed Mlaiel (mlaiel@live.de)
Team: Lead Dev IA + Backend Senior + Security Expert + DBA + DevOps Engineer
Type: Enterprise Error Management System - Production-Ready
Responsibility: Centralized exception handling with comprehensive error categorization
===================================================================================

⚠️  EXCLUSIVE INTELLECTUAL PROPERTY - FAHED MLAIEL ⚠️
(c) 2025 Fahed Mlaiel. All rights reserved.
Unauthorized use strictly prohibited and subject to legal prosecution.
Contact: mlaiel@live.de

🎯 ERROR HANDLING STRATEGY:
- Hierarchical exception classes for precise error categorization
- Structured error context with debugging information
- Security-conscious error messages (no sensitive data exposure)
- Database transaction-aware error handling
- Performance monitoring integration
- Logging compliance for audit trails
"""

import logging
import traceback
from datetime import datetime
from typing import Any, Dict, List, Optional, Union
from enum import Enum
import structlog

# Structured logging configuration
logger = structlog.get_logger(__name__)

class ErrorSeverity(Enum):
    """Error severity levels for monitoring and alerting"""
    CRITICAL = "critical"  # System failure, immediate action required
    HIGH = "high"         # Major functionality impacted
    MEDIUM = "medium"     # Limited functionality impacted
    LOW = "low"          # Minor issues, graceful degradation
    INFO = "info"        # Informational, no action required

class ErrorCategory(Enum):
    """Error categories for better debugging and monitoring"""
    SYSTEM = "system"                    # System-level errors
    PROCESSING = "processing"            # Content processing errors
    AI_MODEL = "ai_model"               # AI/ML model errors
    SECURITY = "security"               # Security and authentication errors
    DATABASE = "database"               # Database operation errors
    NETWORK = "network"                 # Network and API errors
    VALIDATION = "validation"           # Input validation errors
    BUSINESS_LOGIC = "business_logic"   # Business rule violations
    PERFORMANCE = "performance"         # Performance-related issues
    INTEGRATION = "integration"         # External service integration errors

class MediaProcessingError(Exception):
    """Base exception class for all media processing errors"""
    
    def __init__(
        self,
        message: str,
        error_code: str = "MEDIA_PROC_ERROR",
        severity: ErrorSeverity = ErrorSeverity.MEDIUM,
        category: ErrorCategory = ErrorCategory.PROCESSING,
        context: Optional[Dict[str, Any]] = None,
        cause: Optional[Exception] = None,
        user_message: Optional[str] = None
    ):
        super().__init__(message)
        
        self.message = message
        self.error_code = error_code
        self.severity = severity
        self.category = category
        self.context = context or {}
        self.cause = cause
        self.user_message = user_message or "An error occurred during processing"
        self.timestamp = datetime.utcnow()
        self.traceback_info = traceback.format_exc()
        
        # Log the error with structured logging
        self._log_error()
    
    def _log_error(self):
        """Log error with structured information"""
        logger.error(
            "Media processing error occurred",
            error_code=self.error_code,
            severity=self.severity.value,
            category=self.category.value,
            message=self.message,
            user_message=self.user_message,
            context=self.context,
            timestamp=self.timestamp.isoformat(),
            traceback=self.traceback_info if self.severity in [ErrorSeverity.CRITICAL, ErrorSeverity.HIGH] else None
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert error to dictionary for API responses"""
        return {
            "error": {
                "code": self.error_code,
                "message": self.user_message,
                "severity": self.severity.value,
                "category": self.category.value,
                "timestamp": self.timestamp.isoformat(),
                "context": self._sanitize_context()
            }
        }
    
    def _sanitize_context(self) -> Dict[str, Any]:
        """Remove sensitive information from context for external exposure"""
        sanitized = {}
        for key, value in self.context.items():
            if key.lower() in ['password', 'token', 'secret', 'key', 'auth']:
                sanitized[key] = "[REDACTED]"
            elif isinstance(value, str) and len(value) > 100:
                sanitized[key] = f"{value[:97]}..."
            else:
                sanitized[key] = value
        return sanitized

# =============================================================================
# AI PROCESSING ERRORS
# =============================================================================

class AIProcessingError(MediaProcessingError):
    """Base class for AI/ML processing errors"""
    
    def __init__(self, message: str, **kwargs):
        kwargs.setdefault('error_code', 'AI_PROC_ERROR')
        kwargs.setdefault('category', ErrorCategory.AI_MODEL)
        super().__init__(message, **kwargs)

class ModelLoadError(AIProcessingError):
    """Error loading AI models"""
    
    def __init__(self, model_name: str, model_path: str, cause: Exception, **kwargs):
        message = f"Failed to load AI model '{model_name}' from path '{model_path}'"
        kwargs.update({
            'error_code': 'MODEL_LOAD_ERROR',
            'severity': ErrorSeverity.CRITICAL,
            'context': {'model_name': model_name, 'model_path': model_path},
            'cause': cause,
            'user_message': f"AI model '{model_name}' is temporarily unavailable"
        })
        super().__init__(message, **kwargs)

class ModelInferenceError(AIProcessingError):
    """Error during AI model inference"""
    
    def __init__(self, model_name: str, input_shape: tuple, cause: Exception, **kwargs):
        message = f"Model '{model_name}' inference failed for input shape {input_shape}"
        kwargs.update({
            'error_code': 'MODEL_INFERENCE_ERROR',
            'severity': ErrorSeverity.HIGH,
            'context': {'model_name': model_name, 'input_shape': str(input_shape)},
            'cause': cause,
            'user_message': "AI processing temporarily unavailable"
        })
        super().__init__(message, **kwargs)

class MultimodalProcessingError(AIProcessingError):
    """Error in cross-modal processing"""
    
    def __init__(self, modalities: List[str], processing_mode: str, cause: Exception, **kwargs):
        message = f"Multimodal processing failed for modalities {modalities} in mode '{processing_mode}'"
        kwargs.update({
            'error_code': 'MULTIMODAL_ERROR',
            'severity': ErrorSeverity.HIGH,
            'context': {'modalities': modalities, 'processing_mode': processing_mode},
            'cause': cause,
            'user_message': "Cross-modal AI analysis temporarily unavailable"
        })
        super().__init__(message, **kwargs)

# =============================================================================
# CONTENT PROCESSING ERRORS
# =============================================================================

class ContentProcessingError(MediaProcessingError):
    """Base class for content processing errors"""
    
    def __init__(self, message: str, **kwargs):
        kwargs.setdefault('error_code', 'CONTENT_PROC_ERROR')
        kwargs.setdefault('category', ErrorCategory.PROCESSING)
        super().__init__(message, **kwargs)

class UnsupportedFormatError(ContentProcessingError):
    """Unsupported content format error"""
    
    def __init__(self, file_format: str, supported_formats: List[str], **kwargs):
        message = f"Unsupported format '{file_format}'. Supported: {supported_formats}"
        kwargs.update({
            'error_code': 'UNSUPPORTED_FORMAT',
            'severity': ErrorSeverity.MEDIUM,
            'context': {'format': file_format, 'supported_formats': supported_formats},
            'user_message': f"File format '{file_format}' is not supported"
        })
        super().__init__(message, **kwargs)

class FileCorruptionError(ContentProcessingError):
    """File corruption or invalid content error"""
    
    def __init__(self, file_path: str, corruption_type: str, **kwargs):
        message = f"File corruption detected in '{file_path}': {corruption_type}"
        kwargs.update({
            'error_code': 'FILE_CORRUPTION',
            'severity': ErrorSeverity.HIGH,
            'context': {'file_path': file_path, 'corruption_type': corruption_type},
            'user_message': "File appears to be corrupted or invalid"
        })
        super().__init__(message, **kwargs)

class ProcessingTimeoutError(ContentProcessingError):
    """Processing timeout error"""
    
    def __init__(self, operation: str, timeout_seconds: int, **kwargs):
        message = f"Operation '{operation}' timed out after {timeout_seconds} seconds"
        kwargs.update({
            'error_code': 'PROCESSING_TIMEOUT',
            'severity': ErrorSeverity.HIGH,
            'context': {'operation': operation, 'timeout_seconds': timeout_seconds},
            'user_message': "Processing is taking longer than expected. Please try again."
        })
        super().__init__(message, **kwargs)

# =============================================================================
# PROTECTION & SECURITY ERRORS
# =============================================================================

class ProtectionError(MediaProcessingError):
    """Base class for content protection errors"""
    
    def __init__(self, message: str, **kwargs):
        kwargs.setdefault('error_code', 'PROTECTION_ERROR')
        kwargs.setdefault('category', ErrorCategory.SECURITY)
        super().__init__(message, **kwargs)

class WatermarkError(ProtectionError):
    """Error in watermarking operations"""
    
    def __init__(self, operation: str, content_type: str, cause: Exception, **kwargs):
        message = f"Watermark {operation} failed for {content_type} content"
        kwargs.update({
            'error_code': 'WATERMARK_ERROR',
            'severity': ErrorSeverity.HIGH,
            'context': {'operation': operation, 'content_type': content_type},
            'cause': cause,
            'user_message': "Content protection processing failed"
        })
        super().__init__(message, **kwargs)

class FingerprintGenerationError(ProtectionError):
    """Error generating content fingerprints"""
    
    def __init__(self, content_type: str, algorithm: str, cause: Exception, **kwargs):
        message = f"Fingerprint generation failed for {content_type} using {algorithm}"
        kwargs.update({
            'error_code': 'FINGERPRINT_ERROR',
            'severity': ErrorSeverity.HIGH,
            'context': {'content_type': content_type, 'algorithm': algorithm},
            'cause': cause,
            'user_message': "Content identification processing failed"
        })
        super().__init__(message, **kwargs)

class BlockchainRegistrationError(ProtectionError):
    """Error registering content on blockchain"""
    
    def __init__(self, blockchain_network: str, transaction_hash: str, cause: Exception, **kwargs):
        message = f"Blockchain registration failed on {blockchain_network}, tx: {transaction_hash}"
        kwargs.update({
            'error_code': 'BLOCKCHAIN_ERROR',
            'severity': ErrorSeverity.MEDIUM,
            'context': {'network': blockchain_network, 'transaction': transaction_hash},
            'cause': cause,
            'user_message': "Content rights registration temporarily unavailable"
        })
        super().__init__(message, **kwargs)

# =============================================================================
# DATABASE & PERFORMANCE ERRORS
# =============================================================================

class DatabaseError(MediaProcessingError):
    """Database operation errors"""
    
    def __init__(self, message: str, **kwargs):
        kwargs.setdefault('error_code', 'DATABASE_ERROR')
        kwargs.setdefault('category', ErrorCategory.DATABASE)
        kwargs.setdefault('severity', ErrorSeverity.HIGH)
        super().__init__(message, **kwargs)

class PerformanceError(MediaProcessingError):
    """Performance-related errors"""
    
    def __init__(self, message: str, **kwargs):
        kwargs.setdefault('error_code', 'PERFORMANCE_ERROR')
        kwargs.setdefault('category', ErrorCategory.PERFORMANCE)
        kwargs.setdefault('severity', ErrorSeverity.MEDIUM)
        super().__init__(message, **kwargs)

# =============================================================================
# VALIDATION ERRORS
# =============================================================================

class ValidationError(MediaProcessingError):
    """Input validation errors"""
    
    def __init__(self, field: str, value: Any, constraint: str, **kwargs):
        message = f"Validation failed for field '{field}' with value '{value}': {constraint}"
        kwargs.update({
            'error_code': 'VALIDATION_ERROR',
            'category': ErrorCategory.VALIDATION,
            'severity': ErrorSeverity.LOW,
            'context': {'field': field, 'value': str(value), 'constraint': constraint},
            'user_message': f"Invalid value for {field}: {constraint}"
        })
        super().__init__(message, **kwargs)

# =============================================================================
# BUSINESS LOGIC ERRORS
# =============================================================================

class BusinessLogicError(MediaProcessingError):
    """Business rule violation errors"""
    
    def __init__(self, rule: str, violation: str, **kwargs):
        message = f"Business rule violation: {rule} - {violation}"
        kwargs.update({
            'error_code': 'BUSINESS_LOGIC_ERROR',
            'category': ErrorCategory.BUSINESS_LOGIC,
            'severity': ErrorSeverity.MEDIUM,
            'context': {'rule': rule, 'violation': violation},
            'user_message': f"Operation not allowed: {violation}"
        })
        super().__init__(message, **kwargs)

# =============================================================================
# ERROR HANDLER UTILITIES
# =============================================================================

class ErrorHandler:
    """Centralized error handling utilities"""
    
    @staticmethod
    def handle_exception(
        exc: Exception,
        operation: str,
        context: Optional[Dict[str, Any]] = None
    ) -> MediaProcessingError:
        """Convert generic exceptions to MediaProcessingError"""
        
        if isinstance(exc, MediaProcessingError):
            return exc
        
        # Map common exception types
        error_mappings = {
            FileNotFoundError: lambda e: ContentProcessingError(
                f"File not found during {operation}",
                error_code="FILE_NOT_FOUND",
                severity=ErrorSeverity.HIGH,
                cause=e,
                context=context
            ),
            PermissionError: lambda e: ProtectionError(
                f"Permission denied during {operation}",
                error_code="PERMISSION_DENIED",
                severity=ErrorSeverity.HIGH,
                cause=e,
                context=context
            ),
            MemoryError: lambda e: PerformanceError(
                f"Out of memory during {operation}",
                error_code="OUT_OF_MEMORY",
                severity=ErrorSeverity.CRITICAL,
                cause=e,
                context=context
            ),
            TimeoutError: lambda e: ProcessingTimeoutError(
                operation=operation,
                timeout_seconds=context.get('timeout', 0) if context else 0,
                cause=e,
                context=context
            )
        }
        
        exception_type = type(exc)
        if exception_type in error_mappings:
            return error_mappings[exception_type](exc)
        
        # Generic fallback
        return MediaProcessingError(
            f"Unexpected error during {operation}: {str(exc)}",
            error_code="UNEXPECTED_ERROR",
            severity=ErrorSeverity.HIGH,
            cause=exc,
            context=context
        )
    
    @staticmethod
    def log_performance_issue(
        operation: str,
        duration_ms: int,
        threshold_ms: int,
        context: Optional[Dict[str, Any]] = None
    ):
        """Log performance issues when operations exceed thresholds"""
        if duration_ms > threshold_ms:
            logger.warning(
                "Performance threshold exceeded",
                operation=operation,
                duration_ms=duration_ms,
                threshold_ms=threshold_ms,
                context=context or {}
            )

# =============================================================================
# DECORATORS FOR ERROR HANDLING
# =============================================================================

from functools import wraps
from typing import Callable, TypeVar

T = TypeVar('T')

def handle_processing_errors(operation_name: str):
    """Decorator to automatically handle and convert exceptions"""
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            try:
                return await func(*args, **kwargs)
            except MediaProcessingError:
                raise  # Re-raise our custom exceptions as-is
            except Exception as e:
                context = {
                    'function': func.__name__,
                    'args_count': len(args),
                    'kwargs_keys': list(kwargs.keys())
                }
                raise ErrorHandler.handle_exception(e, operation_name, context)
        
        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except MediaProcessingError:
                raise  # Re-raise our custom exceptions as-is
            except Exception as e:
                context = {
                    'function': func.__name__,
                    'args_count': len(args),
                    'kwargs_keys': list(kwargs.keys())
                }
                raise ErrorHandler.handle_exception(e, operation_name, context)
        
        # Return appropriate wrapper based on function type
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
    
    return decorator

# =============================================================================
# MONITORING INTEGRATION
# =============================================================================

class ErrorMetrics:
    """Error metrics collection for monitoring"""
    
    def __init__(self):
        self.error_counts = {}
        self.severity_counts = {}
        self.category_counts = {}
    
    def record_error(self, error: MediaProcessingError):
        """Record error for metrics collection"""
        # Count by error code
        self.error_counts[error.error_code] = self.error_counts.get(error.error_code, 0) + 1
        
        # Count by severity
        severity = error.severity.value
        self.severity_counts[severity] = self.severity_counts.get(severity, 0) + 1
        
        # Count by category
        category = error.category.value
        self.category_counts[category] = self.category_counts.get(category, 0) + 1
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get current error metrics"""
        return {
            'error_counts': self.error_counts,
            'severity_counts': self.severity_counts,
            'category_counts': self.category_counts,
            'total_errors': sum(self.error_counts.values())
        }

# Global error metrics instance
error_metrics = ErrorMetrics()

# =============================================================================
# MODULE EXPORTS
# =============================================================================

__all__ = [
    # Base classes
    'MediaProcessingError',
    'ErrorSeverity',
    'ErrorCategory',
    
    # AI Processing errors
    'AIProcessingError',
    'ModelLoadError',
    'ModelInferenceError',
    'MultimodalProcessingError',
    
    # Content processing errors
    'ContentProcessingError',
    'UnsupportedFormatError',
    'FileCorruptionError',
    'ProcessingTimeoutError',
    
    # Protection errors
    'ProtectionError',
    'WatermarkError',
    'FingerprintGenerationError',
    'BlockchainRegistrationError',
    
    # System errors
    'DatabaseError',
    'PerformanceError',
    'ValidationError',
    'BusinessLogicError',
    
    # Utilities
    'ErrorHandler',
    'ErrorMetrics',
    'error_metrics',
    'handle_processing_errors'
]

# Initialize logging
logger.info(
    "Processing exceptions module initialized",
    module="media_processing.processing_exceptions",
    error_types=len(__all__),
    version="3.0.0"
)
