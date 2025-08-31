"""Archival System Exceptions

Defines comprehensive exception hierarchy for the archival system
with specific error types for different operational scenarios.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️  AVERTISSEMENT LÉGAL / LEGAL WARNING ⚠️
Ce code est la propriété intellectuelle exclusive de Fahed Mlaiel.
This code is the exclusive intellectual property of Fahed Mlaiel.
Toute utilisation non autorisée est strictement interdite.
Any unauthorized use is strictly prohibited.
"""
class ArchivalError(Exception):
    """Base exception for archival system errors"""
    
    def __init__(self, message: str, error_code: str = None, details: dict = None):
        super().__init__(message)
        self.message = message
        self.error_code = error_code or "ARCHIVAL_ERROR"
        self.details = details or {}
    
    def to_dict(self) -> dict:
        """Convert exception to dictionary representation"""
        return {
            "error_type": self.__class__.__name__,
            "error_code": self.error_code,
            "message": self.message,
            "details": self.details
        }


class StorageQuotaExceededError(ArchivalError):
    """Raised when storage quota is exceeded"""
    
    def __init__(self, tier: str, used_bytes: int, limit_bytes: int, details: dict = None):
        message = f"Storage quota exceeded for tier '{tier}': {used_bytes} bytes used, limit is {limit_bytes} bytes"
        super().__init__(
            message=message,
            error_code="STORAGE_QUOTA_EXCEEDED",
            details={
                "tier": tier,
                "used_bytes": used_bytes,
                "limit_bytes": limit_bytes,
                "excess_bytes": used_bytes - limit_bytes,
                **(details or {})
            }
        )


class RetentionPolicyViolationError(ArchivalError):
    """Raised when a retention policy would be violated"""
    
    def __init__(self, content_id: str, policy_id: str, violation_type: str, details: dict = None):
        message = f"Retention policy violation for content '{content_id}': {violation_type}"
        super().__init__(
            message=message,
            error_code="RETENTION_POLICY_VIOLATION",
            details={
                "content_id": content_id,
                "policy_id": policy_id,
                "violation_type": violation_type,
                **(details or {})
            }
        )


class CompressionError(ArchivalError):
    """Raised when compression/decompression operations fail"""
    
    def __init__(self, operation: str, content_id: str = None, details: dict = None):
        message = f"Compression operation '{operation}' failed"
        if content_id:
            message += f" for content '{content_id}'"
        
        super().__init__(
            message=message,
            error_code="COMPRESSION_ERROR",
            details={
                "operation": operation,
                "content_id": content_id,
                **(details or {})
            }
        )


class RetrievalTimeoutError(ArchivalError):
    """Raised when content retrieval times out"""
    
    def __init__(self, archive_id: str, timeout_seconds: int, details: dict = None):
        message = f"Content retrieval timed out for archive '{archive_id}' after {timeout_seconds} seconds"
        super().__init__(
            message=message,
            error_code="RETRIEVAL_TIMEOUT",
            details={
                "archive_id": archive_id,
                "timeout_seconds": timeout_seconds,
                **(details or {})
            }
        )


class ArchiveNotFoundError(ArchivalError):
    """Raised when an archive cannot be found"""
    
    def __init__(self, archive_id: str, search_locations: list = None, details: dict = None):
        message = f"Archive '{archive_id}' not found"
        if search_locations:
            message += f" in locations: {', '.join(search_locations)}"
        
        super().__init__(
            message=message,
            error_code="ARCHIVE_NOT_FOUND",
            details={
                "archive_id": archive_id,
                "search_locations": search_locations or [],
                **(details or {})
            }
        )


class ArchiveCorruptionError(ArchivalError):
    """Raised when archive data is corrupted"""
    
    def __init__(self, archive_id: str, corruption_type: str, details: dict = None):
        message = f"Archive '{archive_id}' is corrupted: {corruption_type}"
        super().__init__(
            message=message,
            error_code="ARCHIVE_CORRUPTION",
            details={
                "archive_id": archive_id,
                "corruption_type": corruption_type,
                **(details or {})
            }
        )


class PolicyConfigurationError(ArchivalError):
    """Raised when archival or retention policies are misconfigured"""
    
    def __init__(self, policy_id: str, configuration_issue: str, details: dict = None):
        message = f"Policy '{policy_id}' configuration error: {configuration_issue}"
        super().__init__(
            message=message,
            error_code="POLICY_CONFIGURATION_ERROR",
            details={
                "policy_id": policy_id,
                "configuration_issue": configuration_issue,
                **(details or {})
            }
        )


class StorageBackendError(ArchivalError):
    """Raised when storage backend operations fail"""
    
    def __init__(self, backend_type: str, operation: str, details: dict = None):
        message = f"Storage backend '{backend_type}' operation '{operation}' failed"
        super().__init__(
            message=message,
            error_code="STORAGE_BACKEND_ERROR",
            details={
                "backend_type": backend_type,
                "operation": operation,
                **(details or {})
            }
        )


class LifecycleTransitionError(ArchivalError):
    """Raised when lifecycle transitions fail"""
    
    def __init__(self, archive_id: str, from_stage: str, to_stage: str, reason: str, details: dict = None):
        message = f"Lifecycle transition failed for archive '{archive_id}' from '{from_stage}' to '{to_stage}': {reason}"
        super().__init__(
            message=message,
            error_code="LIFECYCLE_TRANSITION_ERROR",
            details={
                "archive_id": archive_id,
                "from_stage": from_stage,
                "to_stage": to_stage,
                "reason": reason,
                **(details or {})
            }
        )


class MetadataExtractionError(ArchivalError):
    """Raised when content metadata extraction fails"""
    
    def __init__(self, content_id: str, content_type: str, extraction_stage: str, details: dict = None):
        message = f"Metadata extraction failed for content '{content_id}' (type: {content_type}) at stage '{extraction_stage}'"
        super().__init__(
            message=message,
            error_code="METADATA_EXTRACTION_ERROR",
            details={
                "content_id": content_id,
                "content_type": content_type,
                "extraction_stage": extraction_stage,
                **(details or {})
            }
        )


class EncryptionError(ArchivalError):
    """Raised when encryption/decryption operations fail"""
    
    def __init__(self, operation: str, archive_id: str = None, details: dict = None):
        message = f"Encryption operation '{operation}' failed"
        if archive_id:
            message += f" for archive '{archive_id}'"
        
        super().__init__(
            message=message,
            error_code="ENCRYPTION_ERROR",
            details={
                "operation": operation,
                "archive_id": archive_id,
                **(details or {})
            }
        )


class AccessDeniedError(ArchivalError):
    """Raised when access to archive is denied"""
    
    def __init__(self, archive_id: str, user_id: str = None, required_permission: str = None, details: dict = None):
        message = f"Access denied to archive '{archive_id}'"
        if user_id:
            message += f" for user '{user_id}'"
        if required_permission:
            message += f" (requires permission: {required_permission})"
        
        super().__init__(
            message=message,
            error_code="ACCESS_DENIED",
            details={
                "archive_id": archive_id,
                "user_id": user_id,
                "required_permission": required_permission,
                **(details or {})
            }
        )


class ConcurrencyLimitError(ArchivalError):
    """Raised when concurrent operation limits are exceeded"""
    
    def __init__(self, operation_type: str, current_count: int, max_allowed: int, details: dict = None):
        message = f"Concurrency limit exceeded for '{operation_type}': {current_count} operations running, maximum allowed is {max_allowed}"
        super().__init__(
            message=message,
            error_code="CONCURRENCY_LIMIT_EXCEEDED",
            details={
                "operation_type": operation_type,
                "current_count": current_count,
                "max_allowed": max_allowed,
                **(details or {})
            }
        )


class ValidationError(ArchivalError):
    """Raised when data validation fails"""
    
    def __init__(self, field: str, value: any, validation_rule: str, details: dict = None):
        message = f"Validation failed for field '{field}' with value '{value}': {validation_rule}"
        super().__init__(
            message=message,
            error_code="VALIDATION_ERROR",
            details={
                "field": field,
                "value": str(value),
                "validation_rule": validation_rule,
                **(details or {})
            }
        )


class ConfigurationError(ArchivalError):
    """Raised when system configuration is invalid"""
    
    def __init__(self, component: str, configuration_issue: str, details: dict = None):
        message = f"Configuration error in component '{component}': {configuration_issue}"
        super().__init__(
            message=message,
            error_code="CONFIGURATION_ERROR",
            details={
                "component": component,
                "configuration_issue": configuration_issue,
                **(details or {})
            }
        )


class IntegrityCheckError(ArchivalError):
    """Raised when data integrity checks fail"""
    
    def __init__(self, archive_id: str, check_type: str, expected: str, actual: str, details: dict = None):
        message = f"Integrity check '{check_type}' failed for archive '{archive_id}': expected '{expected}', got '{actual}'"
        super().__init__(
            message=message,
            error_code="INTEGRITY_CHECK_FAILED",
            details={
                "archive_id": archive_id,
                "check_type": check_type,
                "expected": expected,
                "actual": actual,
                **(details or {})
            }
        )


class ResourceExhaustionError(ArchivalError):
    """Raised when system resources are exhausted"""
    
    def __init__(self, resource_type: str, current_usage: str, limit: str, details: dict = None):
        message = f"Resource exhaustion: {resource_type} usage ({current_usage}) exceeds limit ({limit})"
        super().__init__(
            message=message,
            error_code="RESOURCE_EXHAUSTION",
            details={
                "resource_type": resource_type,
                "current_usage": current_usage,
                "limit": limit,
                **(details or {})
            }
        )


class SchedulingError(ArchivalError):
    """Raised when task scheduling fails"""
    
    def __init__(self, task_type: str, schedule_time: str, failure_reason: str, details: dict = None):
        message = f"Failed to schedule {task_type} task for {schedule_time}: {failure_reason}"
        super().__init__(
            message=message,
            error_code="SCHEDULING_ERROR",
            details={
                "task_type": task_type,
                "schedule_time": schedule_time,
                "failure_reason": failure_reason,
                **(details or {})
            }
        )
