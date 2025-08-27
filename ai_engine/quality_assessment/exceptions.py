"""
Quality Assessment Exceptions

Custom exception classes for quality assessment module error handling.
Provides comprehensive error classification and debugging information.

Created by: Fahed Mlaiel (mlaiel@live.de)
© 2025 Fahed Mlaiel. All rights reserved.

⚠️ STRICT COPYRIGHT WARNING ⚠️
This software and all associated concepts, algorithms, and implementations are the exclusive 
intellectual property of Fahed Mlaiel (mlaiel@live.de). Any unauthorized use, reproduction, 
distribution, modification, or appropriation of this code, in whole or in part, without 
explicit written permission from Fahed Mlaiel is strictly prohibited and will be prosecuted 
to the full extent of the law.
"""

from typing import Dict, List, Optional, Any
from enum import Enum
import traceback
from datetime import datetime


class ErrorSeverity(Enum):
    """Error severity levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"
    FATAL = "fatal"


class ErrorCategory(Enum):
    """Error category classifications"""
    VALIDATION_ERROR = "validation_error"
    PROCESSING_ERROR = "processing_error"
    CONFIGURATION_ERROR = "configuration_error"
    RESOURCE_ERROR = "resource_error"
    NETWORK_ERROR = "network_error"
    SECURITY_ERROR = "security_error"
    COMPLIANCE_ERROR = "compliance_error"
    PERFORMANCE_ERROR = "performance_error"
    DATA_ERROR = "data_error"
    SYSTEM_ERROR = "system_error"


class QualityAssessmentBaseException(Exception):
    """
    Base exception class for Quality Assessment Module
    
    Provides common error handling functionality and structured error information.
    """
    
    def __init__(
        self,
        message: str,
        error_code: str = "UNKNOWN_ERROR",
        severity: ErrorSeverity = ErrorSeverity.MEDIUM,
        category: ErrorCategory = ErrorCategory.SYSTEM_ERROR,
        details: Optional[Dict[str, Any]] = None,
        suggestions: Optional[List[str]] = None,
        context: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize base exception
        
        Args:
            message: Human-readable error message
            error_code: Unique error code for classification
            severity: Error severity level
            category: Error category classification
            details: Additional error details and metadata
            suggestions: List of suggestions to resolve the error
            context: Context information when error occurred
        """
        super().__init__(message)
        
        self.message = message
        self.error_code = error_code
        self.severity = severity
        self.category = category
        self.details = details or {}
        self.suggestions = suggestions or []
        self.context = context or {}
        self.timestamp = datetime.now()
        self.traceback = traceback.format_exc()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert exception to dictionary format"""
        return {
            'error_type': self.__class__.__name__,
            'message': self.message,
            'error_code': self.error_code,
            'severity': self.severity.value,
            'category': self.category.value,
            'details': self.details,
            'suggestions': self.suggestions,
            'context': self.context,
            'timestamp': self.timestamp.isoformat(),
            'traceback': self.traceback
        }
    
    def __str__(self) -> str:
        """String representation of the exception"""
        return f"[{self.error_code}] {self.message} (Severity: {self.severity.value})"


class ContentValidationError(QualityAssessmentBaseException):
    """
    Raised when content validation fails
    
    This includes format validation, file integrity checks, and content structure validation.
    """
    
    def __init__(
        self,
        message: str,
        error_code: str = "CONTENT_VALIDATION_ERROR",
        file_path: Optional[str] = None,
        content_type: Optional[str] = None,
        validation_failures: Optional[List[str]] = None,
        **kwargs
    ):
        super().__init__(
            message=message,
            error_code=error_code,
            severity=ErrorSeverity.HIGH,
            category=ErrorCategory.VALIDATION_ERROR,
            **kwargs
        )
        
        self.file_path = file_path
        self.content_type = content_type
        self.validation_failures = validation_failures or []
        
        # Add to details
        self.details.update({
            'file_path': file_path,
            'content_type': content_type,
            'validation_failures': validation_failures
        })


class UnsupportedFormatError(ContentValidationError):
    """Raised when an unsupported file format is encountered"""
    
    def __init__(
        self,
        message: str,
        file_path: str,
        detected_format: str,
        supported_formats: List[str],
        **kwargs
    ):
        super().__init__(
            message=message,
            error_code="UNSUPPORTED_FORMAT",
            file_path=file_path,
            **kwargs
        )
        
        self.detected_format = detected_format
        self.supported_formats = supported_formats
        
        self.details.update({
            'detected_format': detected_format,
            'supported_formats': supported_formats
        })
        
        self.suggestions = [
            f"Convert file to supported format: {', '.join(supported_formats)}",
            "Check file extension and MIME type",
            "Verify file is not corrupted"
        ]


class QualityCheckError(QualityAssessmentBaseException):
    """
    Raised when quality assessment fails
    
    This includes analysis failures, metric calculation errors, and quality scoring issues.
    """
    
    def __init__(
        self,
        message: str,
        error_code: str = "QUALITY_CHECK_ERROR",
        analysis_type: Optional[str] = None,
        failed_metrics: Optional[List[str]] = None,
        partial_results: Optional[Dict[str, Any]] = None,
        **kwargs
    ):
        super().__init__(
            message=message,
            error_code=error_code,
            severity=ErrorSeverity.MEDIUM,
            category=ErrorCategory.PROCESSING_ERROR,
            **kwargs
        )
        
        self.analysis_type = analysis_type
        self.failed_metrics = failed_metrics or []
        self.partial_results = partial_results or {}
        
        self.details.update({
            'analysis_type': analysis_type,
            'failed_metrics': failed_metrics,
            'partial_results': partial_results
        })


class AudioProcessingError(QualityCheckError):
    """Raised when audio processing fails"""
    
    def __init__(
        self,
        message: str,
        error_code: str = "AUDIO_PROCESSING_ERROR",
        sample_rate: Optional[int] = None,
        channels: Optional[int] = None,
        duration: Optional[float] = None,
        **kwargs
    ):
        super().__init__(
            message=message,
            error_code=error_code,
            analysis_type="audio",
            **kwargs
        )
        
        self.details.update({
            'sample_rate': sample_rate,
            'channels': channels,
            'duration': duration
        })


class VideoProcessingError(QualityCheckError):
    """Raised when video processing fails"""
    
    def __init__(
        self,
        message: str,
        error_code: str = "VIDEO_PROCESSING_ERROR",
        width: Optional[int] = None,
        height: Optional[int] = None,
        frame_rate: Optional[float] = None,
        duration: Optional[float] = None,
        **kwargs
    ):
        super().__init__(
            message=message,
            error_code=error_code,
            analysis_type="video",
            **kwargs
        )
        
        self.details.update({
            'width': width,
            'height': height,
            'frame_rate': frame_rate,
            'duration': duration
        })


class ImageProcessingError(QualityCheckError):
    """Raised when image processing fails"""
    
    def __init__(
        self,
        message: str,
        error_code: str = "IMAGE_PROCESSING_ERROR",
        width: Optional[int] = None,
        height: Optional[int] = None,
        color_mode: Optional[str] = None,
        **kwargs
    ):
        super().__init__(
            message=message,
            error_code=error_code,
            analysis_type="image",
            **kwargs
        )
        
        self.details.update({
            'width': width,
            'height': height,
            'color_mode': color_mode
        })


class TextProcessingError(QualityCheckError):
    """Raised when text processing fails"""
    
    def __init__(
        self,
        message: str,
        error_code: str = "TEXT_PROCESSING_ERROR",
        text_length: Optional[int] = None,
        language: Optional[str] = None,
        **kwargs
    ):
        super().__init__(
            message=message,
            error_code=error_code,
            analysis_type="text",
            **kwargs
        )
        
        self.details.update({
            'text_length': text_length,
            'language': language
        })


class ConfigurationError(QualityAssessmentBaseException):
    """
    Raised when configuration is invalid or missing
    
    This includes missing configuration files, invalid settings, and initialization failures.
    """
    
    def __init__(
        self,
        message: str,
        error_code: str = "CONFIGURATION_ERROR",
        config_key: Optional[str] = None,
        expected_type: Optional[str] = None,
        actual_value: Optional[Any] = None,
        **kwargs
    ):
        super().__init__(
            message=message,
            error_code=error_code,
            severity=ErrorSeverity.HIGH,
            category=ErrorCategory.CONFIGURATION_ERROR,
            **kwargs
        )
        
        self.config_key = config_key
        self.expected_type = expected_type
        self.actual_value = actual_value
        
        self.details.update({
            'config_key': config_key,
            'expected_type': expected_type,
            'actual_value': str(actual_value) if actual_value is not None else None
        })


class ResourceError(QualityAssessmentBaseException):
    """
    Raised when system resources are insufficient or unavailable
    
    This includes memory errors, disk space issues, and processing capacity limitations.
    """
    
    def __init__(
        self,
        message: str,
        error_code: str = "RESOURCE_ERROR",
        resource_type: Optional[str] = None,
        available_amount: Optional[str] = None,
        required_amount: Optional[str] = None,
        **kwargs
    ):
        super().__init__(
            message=message,
            error_code=error_code,
            severity=ErrorSeverity.HIGH,
            category=ErrorCategory.RESOURCE_ERROR,
            **kwargs
        )
        
        self.resource_type = resource_type
        self.available_amount = available_amount
        self.required_amount = required_amount
        
        self.details.update({
            'resource_type': resource_type,
            'available_amount': available_amount,
            'required_amount': required_amount
        })
        
        self.suggestions = [
            "Free up system memory",
            "Close other applications",
            "Reduce processing complexity",
            "Process content in smaller chunks"
        ]


class SecurityError(QualityAssessmentBaseException):
    """
    Raised when security violations are detected
    
    This includes malware detection, unauthorized access attempts, and content security issues.
    """
    
    def __init__(
        self,
        message: str,
        error_code: str = "SECURITY_ERROR",
        threat_type: Optional[str] = None,
        risk_level: Optional[str] = None,
        **kwargs
    ):
        super().__init__(
            message=message,
            error_code=error_code,
            severity=ErrorSeverity.CRITICAL,
            category=ErrorCategory.SECURITY_ERROR,
            **kwargs
        )
        
        self.threat_type = threat_type
        self.risk_level = risk_level
        
        self.details.update({
            'threat_type': threat_type,
            'risk_level': risk_level
        })


class ComplianceViolationError(QualityAssessmentBaseException):
    """
    Raised when content violates platform or legal compliance rules
    
    This includes copyright violations, content policy violations, and regulatory non-compliance.
    """
    
    def __init__(
        self,
        message: str,
        error_code: str = "COMPLIANCE_VIOLATION",
        violation_type: Optional[str] = None,
        platform: Optional[str] = None,
        regulation: Optional[str] = None,
        **kwargs
    ):
        super().__init__(
            message=message,
            error_code=error_code,
            severity=ErrorSeverity.HIGH,
            category=ErrorCategory.COMPLIANCE_ERROR,
            **kwargs
        )
        
        self.violation_type = violation_type
        self.platform = platform
        self.regulation = regulation
        
        self.details.update({
            'violation_type': violation_type,
            'platform': platform,
            'regulation': regulation
        })


class PerformanceError(QualityAssessmentBaseException):
    """
    Raised when performance thresholds are exceeded
    
    This includes timeout errors, slow processing, and performance degradation.
    """
    
    def __init__(
        self,
        message: str,
        error_code: str = "PERFORMANCE_ERROR",
        operation: Optional[str] = None,
        processing_time: Optional[float] = None,
        timeout_threshold: Optional[float] = None,
        **kwargs
    ):
        super().__init__(
            message=message,
            error_code=error_code,
            severity=ErrorSeverity.MEDIUM,
            category=ErrorCategory.PERFORMANCE_ERROR,
            **kwargs
        )
        
        self.operation = operation
        self.processing_time = processing_time
        self.timeout_threshold = timeout_threshold
        
        self.details.update({
            'operation': operation,
            'processing_time': processing_time,
            'timeout_threshold': timeout_threshold
        })


class BusinessMetricsError(QualityAssessmentBaseException):
    """
    Raised when business metrics calculation fails
    
    This includes ROI calculation errors, monetization analysis failures, and performance metric issues.
    """
    
    def __init__(
        self,
        message: str,
        error_code: str = "BUSINESS_METRICS_ERROR",
        metric_type: Optional[str] = None,
        data_source: Optional[str] = None,
        **kwargs
    ):
        super().__init__(
            message=message,
            error_code=error_code,
            severity=ErrorSeverity.MEDIUM,
            category=ErrorCategory.DATA_ERROR,
            **kwargs
        )
        
        self.metric_type = metric_type
        self.data_source = data_source
        
        self.details.update({
            'metric_type': metric_type,
            'data_source': data_source
        })


class ReportingError(QualityAssessmentBaseException):
    """
    Raised when report generation fails
    
    This includes template errors, data formatting issues, and export failures.
    """
    
    def __init__(
        self,
        message: str,
        error_code: str = "REPORTING_ERROR",
        report_type: Optional[str] = None,
        output_format: Optional[str] = None,
        **kwargs
    ):
        super().__init__(
            message=message,
            error_code=error_code,
            severity=ErrorSeverity.LOW,
            category=ErrorCategory.PROCESSING_ERROR,
            **kwargs
        )
        
        self.report_type = report_type
        self.output_format = output_format
        
        self.details.update({
            'report_type': report_type,
            'output_format': output_format
        })


# Error code mappings for quick reference
ERROR_CODES = {
    # Content validation errors
    "UNSUPPORTED_FORMAT": UnsupportedFormatError,
    "CORRUPTED_FILE": ContentValidationError,
    "INVALID_CONTENT_STRUCTURE": ContentValidationError,
    "MISSING_METADATA": ContentValidationError,
    
    # Processing errors
    "AUDIO_CODEC_ERROR": AudioProcessingError,
    "VIDEO_CODEC_ERROR": VideoProcessingError,
    "IMAGE_FORMAT_ERROR": ImageProcessingError,
    "TEXT_ENCODING_ERROR": TextProcessingError,
    
    # Resource errors
    "INSUFFICIENT_MEMORY": ResourceError,
    "DISK_SPACE_LOW": ResourceError,
    "GPU_UNAVAILABLE": ResourceError,
    "PROCESSING_TIMEOUT": PerformanceError,
    
    # Security errors
    "MALWARE_DETECTED": SecurityError,
    "UNAUTHORIZED_ACCESS": SecurityError,
    "CONTENT_UNSAFE": SecurityError,
    
    # Compliance errors
    "COPYRIGHT_VIOLATION": ComplianceViolationError,
    "PLATFORM_POLICY_VIOLATION": ComplianceViolationError,
    "GDPR_VIOLATION": ComplianceViolationError,
    
    # Configuration errors
    "INVALID_CONFIG": ConfigurationError,
    "MISSING_CONFIG": ConfigurationError,
    "CONFIG_TYPE_MISMATCH": ConfigurationError
}


def get_exception_class(error_code: str) -> type:
    """
    Get exception class by error code
    
    Args:
        error_code: Error code string
        
    Returns:
        Exception class for the error code
    """
    return ERROR_CODES.get(error_code, QualityAssessmentBaseException)


def create_exception(
    error_code: str,
    message: str,
    **kwargs
) -> QualityAssessmentBaseException:
    """
    Create exception instance by error code
    
    Args:
        error_code: Error code string
        message: Error message
        **kwargs: Additional exception parameters
        
    Returns:
        Exception instance
    """
    exception_class = get_exception_class(error_code)
    return exception_class(message=message, error_code=error_code, **kwargs)


# Export all exception classes
__all__ = [
    'QualityAssessmentBaseException',
    'ContentValidationError',
    'UnsupportedFormatError',
    'QualityCheckError',
    'AudioProcessingError',
    'VideoProcessingError',
    'ImageProcessingError',
    'TextProcessingError',
    'ConfigurationError',
    'ResourceError',
    'SecurityError',
    'ComplianceViolationError',
    'PerformanceError',
    'BusinessMetricsError',
    'ReportingError',
    'ErrorSeverity',
    'ErrorCategory',
    'ERROR_CODES',
    'get_exception_class',
    'create_exception'
]
