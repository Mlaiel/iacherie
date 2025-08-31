"""
 Custom Exceptions for Content Fingerprinting System
=======================================================

Comprehensive exception hierarchy for multi-modal content fingerprinting,
providing detailed error handling and diagnostic information.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: © 2025 Fahed Mlaiel. All rights reserved.

WARNING: This code and concept are protected by intellectual property rights.
Any unauthorized use, reproduction, or distribution without explicit written 
permission from Fahed Mlaiel is strictly prohibited and will result in legal action.
Contact: mlaiel@live.de for authorization requests.
"""

from typing import Dict, List, Optional, Any, Union
from enum import Enum
import traceback
from datetime import datetime

class ErrorSeverity(str, Enum):
    """Error severity levels."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class ErrorCategory(str, Enum):
    """Error categories for classification."""
    FILE_IO = "file_io"
    CONTENT_PROCESSING = "content_processing"
    ALGORITHM_FAILURE = "algorithm_failure"
    VALIDATION = "validation"
    CONFIGURATION = "configuration"
    RESOURCE = "resource"
    NETWORK = "network"
    DATABASE = "database"
    PERMISSION = "permission"
    TIMEOUT = "timeout"

class FingerprintingBaseException(Exception):
    """Base exception for all fingerprinting-related errors."""
    
    def __init__(self, 
                 message: str,
                 error_code: str = "FINGERPRINT_ERROR",
                 severity: ErrorSeverity = ErrorSeverity.MEDIUM,
                 category: ErrorCategory = ErrorCategory.CONTENT_PROCESSING,
                 details: Optional[Dict[str, Any]] = None,
                 suggestions: Optional[List[str]] = None,
                 original_exception: Optional[Exception] = None):
        """
        Initialize base fingerprinting exception.
        
        Args:
            message: Human-readable error message
            error_code: Unique error identifier
            severity: Error severity level
            category: Error category for classification
            details: Additional error details
            suggestions: Suggested solutions
            original_exception: Original exception that caused this error
        """
        super().__init__(message)
        self.message = message
        self.error_code = error_code
        self.severity = severity
        self.category = category
        self.details = details or {}
        self.suggestions = suggestions or []
        self.original_exception = original_exception
        self.timestamp = datetime.utcnow()
        self.traceback_info = traceback.format_exc() if original_exception else None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert exception to dictionary for serialization."""



        return {
            'error_code': self.error_code,
            'message': self.message,
            'severity': self.severity.value,
            'category': self.category.value,
            'details': self.details,
            'suggestions': self.suggestions,
            'timestamp': self.timestamp.isoformat(),
            'traceback': self.traceback_info,
            'original_exception': str(self.original_exception) if self.original_exception else None
        }
    
    def __str__(self) -> str:
        """String representation of the exception."""



        return f"[{self.error_code}] {self.message}"
    
    def __repr__(self) -> str:
        """Detailed representation of the exception."""



        return (f"{self.__class__.__name__}(error_code='{self.error_code}', "
                f"message='{self.message}', severity='{self.severity.value}')")

# File and I/O related exceptions

class FileProcessingError(FingerprintingBaseException):
    """Exception raised when file processing fails."""
    
    def __init__(self, file_path: str, operation: str, reason: str, **kwargs):
        message = f"Failed to {operation} file '{file_path}': {reason}"
        details = {'file_path': file_path, 'operation': operation, 'reason': reason}
        super().__init__(
            message=message,
            error_code="FILE_PROCESSING_ERROR",
            category=ErrorCategory.FILE_IO,
            details=details,
            **kwargs
        )

class UnsupportedFileFormatError(FingerprintingBaseException):
    """Exception raised when file format is not supported."""
    
    def __init__(self, file_path: str, file_format: str, supported_formats: List[str], **kwargs):
        message = f"Unsupported file format '{file_format}' for file '{file_path}'"
        details = {
            'file_path': file_path,
            'file_format': file_format,
            'supported_formats': supported_formats
        }
        suggestions = [f"Convert file to one of: {', '.join(supported_formats)}"]
        super().__init__(
            message=message,
            error_code="UNSUPPORTED_FORMAT",
            category=ErrorCategory.VALIDATION,
            details=details,
            suggestions=suggestions,
            **kwargs
        )

class FileCorruptionError(FingerprintingBaseException):
    """Exception raised when file is corrupted or unreadable."""
    
    def __init__(self, file_path: str, corruption_type: str, **kwargs):
        message = f"File '{file_path}' appears to be corrupted: {corruption_type}"
        details = {'file_path': file_path, 'corruption_type': corruption_type}
        suggestions = [
            "Verify file integrity",
            "Try re-downloading or re-creating the file",
            "Check file permissions"
        ]
        super().__init__(
            message=message,
            error_code="FILE_CORRUPTION",
            severity=ErrorSeverity.HIGH,
            category=ErrorCategory.FILE_IO,
            details=details,
            suggestions=suggestions,
            **kwargs
        )

class FileSizeError(FingerprintingBaseException):
    """Exception raised when file size exceeds limits."""
    
    def __init__(self, file_path: str, file_size: int, max_size: int, **kwargs):
        message = f"File '{file_path}' is too large: {file_size} bytes > {max_size} bytes"
        details = {
            'file_path': file_path,
            'file_size': file_size,
            'max_size': max_size,
            'size_mb': file_size / (1024 * 1024),
            'max_size_mb': max_size / (1024 * 1024)
        }
        suggestions = [
            "Compress the file",
            "Split into smaller chunks",
            "Use a different quality/resolution setting"
        ]
        super().__init__(
            message=message,
            error_code="FILE_SIZE_EXCEEDED",
            category=ErrorCategory.VALIDATION,
            details=details,
            suggestions=suggestions,
            **kwargs
        )

# Algorithm and processing exceptions

class AlgorithmError(FingerprintingBaseException):
    """Exception raised when fingerprinting algorithm fails."""
    
    def __init__(self, algorithm_name: str, operation: str, reason: str, **kwargs):
        message = f"Algorithm '{algorithm_name}' failed during {operation}: {reason}"
        details = {
            'algorithm_name': algorithm_name,
            'operation': operation,
            'reason': reason
        }
        super().__init__(
            message=message,
            error_code="ALGORITHM_FAILURE",
            severity=ErrorSeverity.HIGH,
            category=ErrorCategory.ALGORITHM_FAILURE,
            details=details,
            **kwargs
        )

class InsufficientDataError(FingerprintingBaseException):
    """Exception raised when content has insufficient data for processing."""
    
    def __init__(self, content_type: str, min_requirement: str, actual: str, **kwargs):
        message = f"Insufficient {content_type} data: requires {min_requirement}, got {actual}"
        details = {
            'content_type': content_type,
            'min_requirement': min_requirement,
            'actual': actual
        }
        suggestions = [
            "Use longer content",
            "Check content quality",
            "Try different preprocessing settings"
        ]
        super().__init__(
            message=message,
            error_code="INSUFFICIENT_DATA",
            category=ErrorCategory.VALIDATION,
            details=details,
            suggestions=suggestions,
            **kwargs
        )

class ModelLoadError(FingerprintingBaseException):
    """Exception raised when ML model fails to load."""
    
    def __init__(self, model_name: str, model_path: str, reason: str, **kwargs):
        message = f"Failed to load model '{model_name}' from '{model_path}': {reason}"
        details = {
            'model_name': model_name,
            'model_path': model_path,
            'reason': reason
        }
        suggestions = [
            "Check model file exists",
            "Verify model file integrity",
            "Check model compatibility",
            "Download model from official source"
        ]
        super().__init__(
            message=message,
            error_code="MODEL_LOAD_FAILURE",
            severity=ErrorSeverity.HIGH,
            category=ErrorCategory.ALGORITHM_FAILURE,
            details=details,
            suggestions=suggestions,
            **kwargs
        )

class FeatureExtractionError(FingerprintingBaseException):
    """Exception raised when feature extraction fails."""
    
    def __init__(self, feature_type: str, content_type: str, stage: str, reason: str, **kwargs):
        message = f"Failed to extract {feature_type} features from {content_type} at {stage}: {reason}"
        details = {
            'feature_type': feature_type,
            'content_type': content_type,
            'stage': stage,
            'reason': reason
        }
        super().__init__(
            message=message,
            error_code="FEATURE_EXTRACTION_FAILURE",
            category=ErrorCategory.ALGORITHM_FAILURE,
            details=details,
            **kwargs
        )

# Audio-specific exceptions

class AudioProcessingError(FingerprintingBaseException):
    """Exception raised during audio processing."""
    
    def __init__(self, file_path: str, operation: str, reason: str, **kwargs):
        message = f"Audio processing failed for '{file_path}' during {operation}: {reason}"
        details = {
            'file_path': file_path,
            'operation': operation,
            'reason': reason,
            'content_type': 'audio'
        }
        super().__init__(
            message=message,
            error_code="AUDIO_PROCESSING_ERROR",
            category=ErrorCategory.CONTENT_PROCESSING,
            details=details,
            **kwargs
        )

class UnsupportedAudioFormatError(UnsupportedFileFormatError):
    """Exception raised for unsupported audio formats."""
    
    def __init__(self, file_path: str, file_format: str, **kwargs):
        supported_formats = ['.mp3', '.wav', '.flac', '.ogg', '.m4a', '.aac']
        super().__init__(file_path, file_format, supported_formats, **kwargs)
        self.error_code = "UNSUPPORTED_AUDIO_FORMAT"

class AudioDurationError(FingerprintingBaseException):
    """Exception raised when audio duration is insufficient."""
    
    def __init__(self, file_path: str, duration: float, min_duration: float, **kwargs):
        message = f"Audio '{file_path}' too short: {duration:.2f}s < {min_duration:.2f}s"
        details = {
            'file_path': file_path,
            'duration': duration,
            'min_duration': min_duration
        }
        suggestions = [
            "Use longer audio clips",
            "Reduce minimum duration requirement",
            "Combine multiple short clips"
        ]
        super().__init__(
            message=message,
            error_code="AUDIO_DURATION_ERROR",
            category=ErrorCategory.VALIDATION,
            details=details,
            suggestions=suggestions,
            **kwargs
        )

# Video-specific exceptions

class VideoProcessingError(FingerprintingBaseException):
    """Exception raised during video processing."""
    
    def __init__(self, file_path: str, operation: str, reason: str, **kwargs):
        message = f"Video processing failed for '{file_path}' during {operation}: {reason}"
        details = {
            'file_path': file_path,
            'operation': operation,
            'reason': reason,
            'content_type': 'video'
        }
        super().__init__(
            message=message,
            error_code="VIDEO_PROCESSING_ERROR",
            category=ErrorCategory.CONTENT_PROCESSING,
            details=details,
            **kwargs
        )

class UnsupportedVideoFormatError(UnsupportedFileFormatError):
    """Exception raised for unsupported video formats."""
    
    def __init__(self, file_path: str, file_format: str, **kwargs):
        supported_formats = ['.mp4', '.avi', '.mkv', '.mov', '.wmv', '.flv', '.webm']
        super().__init__(file_path, file_format, supported_formats, **kwargs)
        self.error_code = "UNSUPPORTED_VIDEO_FORMAT"

class VideoCodecError(FingerprintingBaseException):
    """Exception raised when video codec is not supported."""
    
    def __init__(self, file_path: str, codec: str, **kwargs):
        message = f"Unsupported video codec '{codec}' in file '{file_path}'"
        details = {'file_path': file_path, 'codec': codec}
        suggestions = [
            "Convert video to H.264 or H.265",
            "Install additional codec support",
            "Use different video player/processor"
        ]
        super().__init__(
            message=message,
            error_code="UNSUPPORTED_VIDEO_CODEC",
            category=ErrorCategory.CONTENT_PROCESSING,
            details=details,
            suggestions=suggestions,
            **kwargs
        )

# Image-specific exceptions

class ImageProcessingError(FingerprintingBaseException):
    """Exception raised during image processing."""
    
    def __init__(self, file_path: str, operation: str, reason: str, **kwargs):
        message = f"Image processing failed for '{file_path}' during {operation}: {reason}"
        details = {
            'file_path': file_path,
            'operation': operation,
            'reason': reason,
            'content_type': 'image'
        }
        super().__init__(
            message=message,
            error_code="IMAGE_PROCESSING_ERROR",
            category=ErrorCategory.CONTENT_PROCESSING,
            details=details,
            **kwargs
        )

class UnsupportedImageFormatError(UnsupportedFileFormatError):
    """Exception raised for unsupported image formats."""
    
    def __init__(self, file_path: str, file_format: str, **kwargs):
        supported_formats = ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.webp']
        super().__init__(file_path, file_format, supported_formats, **kwargs)
        self.error_code = "UNSUPPORTED_IMAGE_FORMAT"

class ImageDimensionError(FingerprintingBaseException):
    """Exception raised when image dimensions are invalid."""
    
    def __init__(self, file_path: str, width: int, height: int, min_size: int, **kwargs):
        message = f"Image '{file_path}' too small: {width}x{height} < {min_size}x{min_size}"
        details = {
            'file_path': file_path,
            'width': width,
            'height': height,
            'min_size': min_size
        }
        suggestions = [
            "Use higher resolution images",
            "Upscale image using AI tools",
            "Reduce minimum size requirement"
        ]
        super().__init__(
            message=message,
            error_code="IMAGE_DIMENSION_ERROR",
            category=ErrorCategory.VALIDATION,
            details=details,
            suggestions=suggestions,
            **kwargs
        )

# Text-specific exceptions

class TextProcessingError(FingerprintingBaseException):
    """Exception raised during text processing."""
    
    def __init__(self, operation: str, reason: str, **kwargs):
        message = f"Text processing failed during {operation}: {reason}"
        details = {
            'operation': operation,
            'reason': reason,
            'content_type': 'text'
        }
        super().__init__(
            message=message,
            error_code="TEXT_PROCESSING_ERROR",
            category=ErrorCategory.CONTENT_PROCESSING,
            details=details,
            **kwargs
        )

class TextEncodingError(FingerprintingBaseException):
    """Exception raised when text encoding is problematic."""
    
    def __init__(self, file_path: str, encoding: str, reason: str, **kwargs):
        message = f"Text encoding error in '{file_path}' with encoding '{encoding}': {reason}"
        details = {
            'file_path': file_path,
            'encoding': encoding,
            'reason': reason
        }
        suggestions = [
            "Try UTF-8 encoding",
            "Auto-detect encoding",
            "Clean text data",
            "Use encoding detection library"
        ]
        super().__init__(
            message=message,
            error_code="TEXT_ENCODING_ERROR",
            category=ErrorCategory.CONTENT_PROCESSING,
            details=details,
            suggestions=suggestions,
            **kwargs
        )

class TextLengthError(FingerprintingBaseException):
    """Exception raised when text is too short or too long."""
    
    def __init__(self, text_length: int, min_length: int, max_length: int, **kwargs):
        if text_length < min_length:
            message = f"Text too short: {text_length} < {min_length} characters"
            suggestions = ["Use longer text", "Combine multiple texts"]
        else:
            message = f"Text too long: {text_length} > {max_length} characters"
            suggestions = ["Split text into chunks", "Summarize text", "Use excerpts"]
        
        details = {
            'text_length': text_length,
            'min_length': min_length,
            'max_length': max_length
        }
        super().__init__(
            message=message,
            error_code="TEXT_LENGTH_ERROR",
            category=ErrorCategory.VALIDATION,
            details=details,
            suggestions=suggestions,
            **kwargs
        )

# Resource and system exceptions

class ResourceError(FingerprintingBaseException):
    """Exception raised when system resources are insufficient."""
    
    def __init__(self, resource_type: str, required: str, available: str, **kwargs):
        message = f"Insufficient {resource_type}: requires {required}, available {available}"
        details = {
            'resource_type': resource_type,
            'required': required,
            'available': available
        }
        suggestions = [
            "Free up system resources",
            "Use smaller batch sizes",
            "Reduce processing complexity",
            "Use more powerful hardware"
        ]
        super().__init__(
            message=message,
            error_code="RESOURCE_INSUFFICIENT",
            severity=ErrorSeverity.HIGH,
            category=ErrorCategory.RESOURCE,
            details=details,
            suggestions=suggestions,
            **kwargs
        )

class MemoryError(ResourceError):
    """Exception raised when memory is insufficient."""
    
    def __init__(self, required_mb: float, available_mb: float, **kwargs):
        super().__init__(
            resource_type="memory",
            required=f"{required_mb:.1f} MB",
            available=f"{available_mb:.1f} MB",
            **kwargs
        )
        self.error_code = "MEMORY_INSUFFICIENT"

class GPUError(FingerprintingBaseException):
    """Exception raised when GPU operations fail."""
    
    def __init__(self, operation: str, reason: str, **kwargs):
        message = f"GPU operation '{operation}' failed: {reason}"
        details = {'operation': operation, 'reason': reason}
        suggestions = [
            "Check GPU availability",
            "Update GPU drivers",
            "Free GPU memory",
            "Fall back to CPU processing"
        ]
        super().__init__(
            message=message,
            error_code="GPU_OPERATION_FAILURE",
            severity=ErrorSeverity.HIGH,
            category=ErrorCategory.RESOURCE,
            details=details,
            suggestions=suggestions,
            **kwargs
        )

# Configuration and validation exceptions

class ConfigurationError(FingerprintingBaseException):
    """Exception raised when configuration is invalid."""
    
    def __init__(self, config_key: str, config_value: Any, reason: str, **kwargs):
        message = f"Invalid configuration for '{config_key}' = '{config_value}': {reason}"
        details = {
            'config_key': config_key,
            'config_value': config_value,
            'reason': reason
        }
        suggestions = [
            "Check configuration documentation",
            "Use default values",
            "Validate configuration schema"
        ]
        super().__init__(
            message=message,
            error_code="CONFIGURATION_INVALID",
            category=ErrorCategory.CONFIGURATION,
            details=details,
            suggestions=suggestions,
            **kwargs
        )

class ValidationError(FingerprintingBaseException):
    """Exception raised when data validation fails."""
    
    def __init__(self, data_type: str, validation_rule: str, value: Any, **kwargs):
        message = f"Validation failed for {data_type}: {validation_rule} (value: {value})"
        details = {
            'data_type': data_type,
            'validation_rule': validation_rule,
            'value': value
        }
        super().__init__(
            message=message,
            error_code="VALIDATION_FAILURE",
            category=ErrorCategory.VALIDATION,
            details=details,
            **kwargs
        )

# Database and storage exceptions

class DatabaseError(FingerprintingBaseException):
    """Exception raised when database operations fail."""
    
    def __init__(self, operation: str, reason: str, **kwargs):
        message = f"Database operation '{operation}' failed: {reason}"
        details = {'operation': operation, 'reason': reason}
        suggestions = [
            "Check database connection",
            "Verify database schema",
            "Check database permissions",
            "Retry operation"
        ]
        super().__init__(
            message=message,
            error_code="DATABASE_OPERATION_FAILURE",
            severity=ErrorSeverity.HIGH,
            category=ErrorCategory.DATABASE,
            details=details,
            suggestions=suggestions,
            **kwargs
        )

class StorageError(FingerprintingBaseException):
    """Exception raised when storage operations fail."""
    
    def __init__(self, operation: str, path: str, reason: str, **kwargs):
        message = f"Storage operation '{operation}' failed for '{path}': {reason}"
        details = {
            'operation': operation,
            'path': path,
            'reason': reason
        }
        suggestions = [
            "Check disk space",
            "Verify file permissions",
            "Check path exists",
            "Use different storage location"
        ]
        super().__init__(
            message=message,
            error_code="STORAGE_OPERATION_FAILURE",
            category=ErrorCategory.FILE_IO,
            details=details,
            suggestions=suggestions,
            **kwargs
        )

# Timeout and network exceptions

class TimeoutError(FingerprintingBaseException):
    """Exception raised when operations timeout."""
    
    def __init__(self, operation: str, timeout_seconds: float, **kwargs):
        message = f"Operation '{operation}' timed out after {timeout_seconds} seconds"
        details = {
            'operation': operation,
            'timeout_seconds': timeout_seconds
        }
        suggestions = [
            "Increase timeout value",
            "Optimize operation performance",
            "Use smaller batch sizes",
            "Check system performance"
        ]
        super().__init__(
            message=message,
            error_code="OPERATION_TIMEOUT",
            severity=ErrorSeverity.HIGH,
            category=ErrorCategory.TIMEOUT,
            details=details,
            suggestions=suggestions,
            **kwargs
        )

class NetworkError(FingerprintingBaseException):
    """Exception raised when network operations fail."""
    
    def __init__(self, operation: str, url: str, reason: str, **kwargs):
        message = f"Network operation '{operation}' failed for '{url}': {reason}"
        details = {
            'operation': operation,
            'url': url,
            'reason': reason
        }
        suggestions = [
            "Check internet connection",
            "Verify URL accessibility",
            "Check firewall settings",
            "Use offline alternatives"
        ]
        super().__init__(
            message=message,
            error_code="NETWORK_OPERATION_FAILURE",
            category=ErrorCategory.NETWORK,
            details=details,
            suggestions=suggestions,
            **kwargs
        )

# Utility functions for exception handling

def handle_exception(exception: Exception, context: Dict[str, Any] = None) -> FingerprintingBaseException:
    """Convert generic exceptions to fingerprinting exceptions."""
    if isinstance(exception, FingerprintingBaseException):
        return exception
    
    # Map common exceptions
    exception_mapping = {
        FileNotFoundError: lambda e: FileProcessingError(
            file_path=str(getattr(e, 'filename', 'unknown')),
            operation="access",
            reason="file not found",
            original_exception=e
        ),
        PermissionError: lambda e: FingerprintingBaseException(
            message=f"Permission denied: {str(e)}",
            error_code="PERMISSION_DENIED",
            category=ErrorCategory.PERMISSION,
            original_exception=e
        ),
        MemoryError: lambda e: MemoryError(
            required_mb=0,
            available_mb=0,
            original_exception=e
        ),
        TimeoutError: lambda e: TimeoutError(
            operation="unknown",
            timeout_seconds=0,
            original_exception=e
        )
    }
    
    exception_type = type(exception)
    if exception_type in exception_mapping:
        return exception_mapping[exception_type](exception)
    
    # Generic fallback
    return FingerprintingBaseException(
        message=f"Unexpected error: {str(exception)}",
        error_code="UNEXPECTED_ERROR",
        severity=ErrorSeverity.HIGH,
        details=context or {},
        original_exception=exception
    )

def log_exception(exception: FingerprintingBaseException, logger=None):
    """Log exception with appropriate level based on severity."""
    if logger is None:
        import logging
        logger = logging.getLogger(__name__)
    
    level_mapping = {
        ErrorSeverity.LOW: logger.debug,
        ErrorSeverity.MEDIUM: logger.warning,
        ErrorSeverity.HIGH: logger.error,
        ErrorSeverity.CRITICAL: logger.critical
    }
    
    log_func = level_mapping.get(exception.severity, logger.error)
    log_func(f"{exception.error_code}: {exception.message}", extra={
        'error_details': exception.details,
        'suggestions': exception.suggestions,
        'category': exception.category.value
    })

# Export all exceptions
__all__ = [
    # Base classes
    'FingerprintingBaseException', 'ErrorSeverity', 'ErrorCategory',
    
    # File and I/O exceptions
    'FileProcessingError', 'UnsupportedFileFormatError', 'FileCorruptionError', 'FileSizeError',
    
    # Algorithm exceptions
    'AlgorithmError', 'InsufficientDataError', 'ModelLoadError', 'FeatureExtractionError',
    
    # Content-specific exceptions
    'AudioProcessingError', 'UnsupportedAudioFormatError', 'AudioDurationError',
    'VideoProcessingError', 'UnsupportedVideoFormatError', 'VideoCodecError',
    'ImageProcessingError', 'UnsupportedImageFormatError', 'ImageDimensionError',
    'TextProcessingError', 'TextEncodingError', 'TextLengthError',
    
    # Resource exceptions
    'ResourceError', 'MemoryError', 'GPUError',
    
    # Configuration exceptions
    'ConfigurationError', 'ValidationError',
    
    # Database exceptions
    'DatabaseError', 'StorageError',
    
    # Network exceptions
    'TimeoutError', 'NetworkError',
    
    # Utility functions
    'handle_exception', 'log_exception'
]
