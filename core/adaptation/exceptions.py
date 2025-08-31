"""Enterprise Adaptation Engine Exceptions - Comprehensive Error Handling System

Ultra-advanced exception management for the content adaptation engine providing
detailed error information, debugging capabilities, and recovery suggestions
for all creator types and enterprise scenarios.

Author: Fahed Mlaiel
Email: mlaiel@live.de
Copyright: All rights reserved. Unauthorized use strictly prohibited.
"""
from typing import Dict, List, Optional, Any
from datetime import datetime
import uuid


class AdaptationError(Exception):
    """Base exception for content adaptation errors with enterprise-grade error tracking"""
    
    def __init__(
        self, 
        message: str, 
        error_code: str = None, 
        details: dict = None,
        recovery_suggestions: List[str] = None,
        creator_type: str = None,
        content_type: str = None
    ):
        super().__init__(message)
        self.message = message
        self.error_code = error_code or "ADAPTATION_ERROR"
        self.details = details or {}
        self.recovery_suggestions = recovery_suggestions or []
        self.creator_type = creator_type
        self.content_type = content_type
        self.timestamp = datetime.utcnow()
        self.error_id = str(uuid.uuid4())
    
    def to_dict(self) -> dict:
        """Convert exception to comprehensive dictionary format"""
        return {
            "error_id": self.error_id,
            "error_type": self.__class__.__name__,
            "message": self.message,
            "error_code": self.error_code,
            "details": self.details,
            "recovery_suggestions": self.recovery_suggestions,
            "creator_type": self.creator_type,
            "content_type": self.content_type,
            "timestamp": self.timestamp.isoformat()
        }


# Core Engine Exceptions
class ContentAdapterError(AdaptationError):
    """Exception raised during content adaptation operations"""
    pass


class AdaptationEngineError(AdaptationError):
    """Exception raised by the main adaptation engine"""
    pass


class WorkflowError(AdaptationError):
    """Exception raised during workflow execution"""
    pass


class ProcessingTimeoutError(AdaptationError):
    """Exception raised when processing exceeds timeout limits"""
    pass


# Format and Conversion Exceptions
class FormatConversionError(AdaptationError):
    """Exception raised during format conversion operations"""
    pass


class ConversionError(FormatConversionError):
    """Alias for FormatConversionError for backward compatibility"""
    pass


class UnsupportedFormatError(AdaptationError):
    """Exception raised for unsupported file formats"""
    pass


class QualityValidationError(AdaptationError):
    """Exception raised during quality validation processes"""
    pass


# Platform and Optimization Exceptions
class PlatformOptimizationError(AdaptationError):
    """Exception raised during platform optimization"""
    pass


class OptimizationError(PlatformOptimizationError):
    """Alias for PlatformOptimizationError"""
    pass


class UnsupportedPlatformError(AdaptationError):
    """Exception raised for unsupported platforms"""
    pass


class AlgorithmError(AdaptationError):
    """Exception raised during algorithm processing"""
    pass


# Audience and Targeting Exceptions
class AudienceTargetingError(AdaptationError):
    """Exception raised during audience targeting operations"""
    pass


class TargetingError(AudienceTargetingError):
    """Alias for AudienceTargetingError"""
    pass


class InsufficientDataError(AdaptationError):
    """Exception raised when insufficient data is available for processing"""
    pass


class ModelTrainingError(AdaptationError):
    """Exception raised during AI model training"""
    pass


# Performance and Quality Exceptions
class PerformanceOptimizationError(AdaptationError):
    """Exception raised during performance optimization"""
    pass


class QualityControlError(AdaptationError):
    """Exception raised during quality control operations"""
    pass


class QualityError(QualityControlError):
    """Alias for QualityControlError"""
    pass


class ModelValidationError(AdaptationError):
    """Exception raised during model validation"""
    pass


# Metadata and Enhancement Exceptions
class MetadataEnhancementError(AdaptationError):
    """Exception raised during metadata enhancement"""
    pass


class MetadataError(MetadataEnhancementError):
    """Alias for MetadataEnhancementError"""
    pass


class ProcessingError(AdaptationError):
    """Exception raised during general processing operations"""
    pass


# Validation and Compliance Exceptions
class ValidationError(AdaptationError):
    """Exception raised during content validation"""
    pass


class ContentValidationError(ValidationError):
    """Exception raised during specific content validation operations"""
    pass


class ComplianceError(AdaptationError):
    """Exception raised during compliance checking"""
    pass


# Strategy and Configuration Exceptions
class StrategyError(AdaptationError):
    """Exception raised during strategy operations"""
    pass


class InvalidStrategyError(StrategyError):
    """Exception raised for invalid strategy definitions"""
    pass


class ConfigurationError(AdaptationError):
    """Exception raised for configuration issues"""
    pass


# Content Type and Support Exceptions
class UnsupportedContentTypeError(AdaptationError):
    """Exception raised for unsupported content types"""
    
    def __init__(self, content_type: str, supported_types: list = None, creator_type: str = None):
        message = f"Unsupported content type: {content_type}"
        if supported_types:
            message += f". Supported types: {', '.join(supported_types)}"
        
        recovery_suggestions = [
            f"Convert content to one of the supported formats: {', '.join(supported_types) if supported_types else 'check documentation'}",
            "Contact support for format extension requests",
            "Use format conversion tools before upload"
        ]
        
        super().__init__(
            message, 
            "UNSUPPORTED_CONTENT_TYPE", 
            {
                "content_type": content_type,
                "supported_types": supported_types or []
            },
            recovery_suggestions,
            creator_type
        )
            "supported_types": supported_types or []
        })


class UnsupportedPlatformError(AdaptationError):
    """Exception raised for unsupported platforms"""
    
    def __init__(self, platform: str, supported_platforms: list = None):
        message = f"Unsupported platform: {platform}"
        if supported_platforms:
            message += f". Supported platforms: {', '.join(supported_platforms)}"
        
        super().__init__(message, "UNSUPPORTED_PLATFORM", {
            "platform": platform,
            "supported_platforms": supported_platforms or []
        })


class ConfigurationError(AdaptationError):
    """Exception raised for configuration-related errors"""
    pass


class ResourceLimitError(AdaptationError):
    """Exception raised when resource limits are exceeded"""
    
    def __init__(self, resource_type: str, limit: str, current: str):
        message = f"Resource limit exceeded for {resource_type}: {current} > {limit}"
        super().__init__(message, "RESOURCE_LIMIT_EXCEEDED", {
            "resource_type": resource_type,
            "limit": limit,
            "current": current
        })


class ProcessingTimeoutError(AdaptationError):
    """Exception raised when processing operations timeout"""
    
    def __init__(self, operation: str, timeout: int):
        message = f"Operation '{operation}' timed out after {timeout} seconds"
        super().__init__(message, "PROCESSING_TIMEOUT", {
            "operation": operation,
            "timeout": timeout
        })


class FileNotFoundError(AdaptationError):
    """Exception raised when required files are not found"""
    
    def __init__(self, file_path: str):
        message = f"File not found: {file_path}"
        super().__init__(message, "FILE_NOT_FOUND", {
            "file_path": file_path
        })


class FilePermissionError(AdaptationError):
    """Exception raised for file permission issues"""
    
    def __init__(self, file_path: str, operation: str):
        message = f"Permission denied for {operation} operation on: {file_path}"
        super().__init__(message, "FILE_PERMISSION_DENIED", {
            "file_path": file_path,
            "operation": operation
        })


class DependencyError(AdaptationError):
    """Exception raised when external dependencies are missing or incompatible"""
    
    def __init__(self, dependency: str, required_version: str = None):
        message = f"Missing or incompatible dependency: {dependency}"
        if required_version:
            message += f" (required version: {required_version})"
        
        super().__init__(message, "DEPENDENCY_ERROR", {
            "dependency": dependency,
            "required_version": required_version
        })


class DatabaseError(AdaptationError):
    """Exception raised for database-related errors"""
    pass


class APIError(AdaptationError):
    """Exception raised for external API errors"""
    
    def __init__(self, api_name: str, status_code: int = None, response: str = None):
        message = f"API error from {api_name}"
        if status_code:
            message += f" (status: {status_code})"
        
        super().__init__(message, "API_ERROR", {
            "api_name": api_name,
            "status_code": status_code,
            "response": response
        })


class AuthenticationError(AdaptationError):
    """Exception raised for authentication failures"""
    
    def __init__(self, service: str):
        message = f"Authentication failed for service: {service}"
        super().__init__(message, "AUTHENTICATION_FAILED", {
            "service": service
        })


class QuotaExceededError(AdaptationError):
    """Exception raised when service quotas are exceeded"""
    
    def __init__(self, service: str, quota_type: str, limit: str):
        message = f"Quota exceeded for {service} ({quota_type}): {limit}"
        super().__init__(message, "QUOTA_EXCEEDED", {
            "service": service,
            "quota_type": quota_type,
            "limit": limit
        })


class ContentCorruptionError(AdaptationError):
    """Exception raised when content corruption is detected"""
    
    def __init__(self, content_path: str, corruption_type: str):
        message = f"Content corruption detected in {content_path}: {corruption_type}"
        super().__init__(message, "CONTENT_CORRUPTION", {
            "content_path": content_path,
            "corruption_type": corruption_type
        })


class IncompatibleFormatError(AdaptationError):
    """Exception raised for format incompatibility issues"""
    
    def __init__(self, source_format: str, target_format: str, reason: str = None):
        message = f"Incompatible format conversion: {source_format} -> {target_format}"
        if reason:
            message += f" ({reason})"
        
        super().__init__(message, "INCOMPATIBLE_FORMAT", {
            "source_format": source_format,
            "target_format": target_format,
            "reason": reason
        })


class QualityDegradationError(AdaptationError):
    """Exception raised when quality degradation exceeds acceptable limits"""
    
    def __init__(self, metric: str, degradation: float, threshold: float):
        message = f"Quality degradation in {metric}: {degradation:.2%} > {threshold:.2%} threshold"
        super().__init__(message, "QUALITY_DEGRADATION", {
            "metric": metric,
            "degradation": degradation,
            "threshold": threshold
        })


class ComplianceViolationError(AdaptationError):
    """Exception raised for compliance violations"""
    
    def __init__(self, compliance_standard: str, violation_details: str):
        message = f"Compliance violation ({compliance_standard}): {violation_details}"
        super().__init__(message, "COMPLIANCE_VIOLATION", {
            "compliance_standard": compliance_standard,
            "violation_details": violation_details
        })


class WorkflowError(AdaptationError):
    """Exception raised during workflow execution"""
    
    def __init__(self, workflow_id: str, step: str, reason: str):
        message = f"Workflow {workflow_id} failed at step '{step}': {reason}"
        super().__init__(message, "WORKFLOW_ERROR", {
            "workflow_id": workflow_id,
            "failed_step": step,
            "reason": reason
        })


class CancellationError(AdaptationError):
    """Exception raised when operations are cancelled"""
    
    def __init__(self, operation: str, reason: str = "User cancellation"):
        message = f"Operation cancelled: {operation} ({reason})"
        super().__init__(message, "OPERATION_CANCELLED", {
            "operation": operation,
            "reason": reason
        })


# Convenience functions for common error scenarios
def raise_unsupported_content_type(content_type: str, supported_types: list = None):
    """Raise UnsupportedContentTypeError with standardized message"""
    raise UnsupportedContentTypeError(content_type, supported_types)


def raise_unsupported_platform(platform: str, supported_platforms: list = None):
    """Raise UnsupportedPlatformError with standardized message"""
    raise UnsupportedPlatformError(platform, supported_platforms)


def raise_resource_limit_exceeded(resource_type: str, limit: str, current: str):
    """Raise ResourceLimitError with standardized message"""
    raise ResourceLimitError(resource_type, limit, current)


def raise_processing_timeout(operation: str, timeout: int):
    """Raise ProcessingTimeoutError with standardized message"""
    raise ProcessingTimeoutError(operation, timeout)


def raise_file_not_found(file_path: str):
    """Raise FileNotFoundError with standardized message"""
    raise FileNotFoundError(file_path)


def raise_quality_degradation(metric: str, degradation: float, threshold: float):
    """Raise QualityDegradationError with standardized message"""
    raise QualityDegradationError(metric, degradation, threshold)


def raise_compliance_violation(compliance_standard: str, violation_details: str):
    """Raise ComplianceViolationError with standardized message"""
    raise ComplianceViolationError(compliance_standard, violation_details)


def handle_adaptation_error(func):
    """
    Decorator to handle and standardize adaptation errors
    
    Usage:
        @handle_adaptation_error
        async def my_adaptation_function():
            # function implementation
    """
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except AdaptationError:
            # Re-raise adaptation errors as-is
            raise
        except FileNotFoundError as e:
            raise FileNotFoundError(str(e))
        except PermissionError as e:
            raise FilePermissionError(str(e), "access")
        except TimeoutError as e:
            raise ProcessingTimeoutError(func.__name__, 0)
        except Exception as e:
            # Wrap other exceptions in generic AdaptationError
            raise AdaptationError(
                f"Unexpected error in {func.__name__}: {str(e)}",
                "UNEXPECTED_ERROR",
                {"function": func.__name__, "original_error": str(e)}
            )
    
    return wrapper
