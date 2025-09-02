"""Vector Agent Exceptions - Comprehensive Error Handling System

Ultra-advanced exception hierarchy providing detailed error information,
debugging context, and recovery strategies for all vector operations.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️  CRITICAL LEGAL NOTICE:
This code and architectural design are the exclusive intellectual property of Fahed Mlaiel.
Unauthorized use, copying, distribution, or commercialization is strictly prohibited.
Any attempt to steal the concept, idea, or code without explicit written authorization
from Fahed Mlaiel will result in immediate legal prosecution under German and international law.
"""

import traceback
from typing import Dict, List, Optional, Any
from datetime import datetime, timezone


class VectorAgentBaseException(Exception):
    """
    Base exception class for all Vector Agent errors
    
    Provides comprehensive error information including:
    - Detailed error messages
    - Error codes for programmatic handling
    - Context information for debugging
    - Recovery suggestions
    - Timestamp and stack trace information
    """
    
    def __init__(
        self,
        message: str,
        error_code: str = "VECTOR_UNKNOWN_ERROR",
        context: Optional[Dict[str, Any]] = None,
        recovery_suggestions: Optional[List[str]] = None,
        original_exception: Optional[Exception] = None
    ):
        super().__init__(message)
        self.message = message
        self.error_code = error_code
        self.context = context or {}
        self.recovery_suggestions = recovery_suggestions or []
        self.original_exception = original_exception
        self.timestamp = datetime.now(timezone.utc)
        self.stack_trace = traceback.format_stack()
        
    def to_dict(self) -> Dict[str, Any]:
        """Convert exception to dictionary for logging/serialization"""
        return {
            "error_type": self.__class__.__name__,
            "error_code": self.error_code,
            "message": self.message,
            "context": self.context,
            "recovery_suggestions": self.recovery_suggestions,
            "timestamp": self.timestamp.isoformat(),
            "original_exception": str(self.original_exception) if self.original_exception else None
        }
    
    def __str__(self) -> str:
        """Enhanced string representation"""
        base_msg = f"[{self.error_code}] {self.message}"
        if self.context:
            context_str = ", ".join(f"{k}={v}" for k, v in self.context.items())
            base_msg += f" (Context: {context_str})"
        return base_msg


# ===============================
# PROCESSING & ORCHESTRATION ERRORS
# ===============================

class VectorProcessingError(VectorAgentBaseException):
    """General vector processing error"""
    
    def __init__(self, message: str, **kwargs):
        try:
            logger.info(f"Executing __init__")
            
            # Implementation for __init__
            # TODO: Add specific business logic here
            
            result = None  # Replace with actual implementation
            
            logger.info(f"__init__ completed successfully")
            return result
            
        except Exception as e:
        try:
            logger.info(f"Executing __init__")
            
            # Implementation for __init__
            # TODO: Add specific business logic here
            
            result = None  # Replace with actual implementation
            
            logger.info(f"__init__ completed successfully")
            return result
            
        except Exception as e:
            logger.error(f"__init__ failed: {e}")
            raise
            logger.error(f"__init__ failed: {e}")
            raise
            message,
            error_code=kwargs.get("error_code", "VECTOR_PROCESSING_ERROR"),
            **kwargs
        )


class VectorOrchestrationError(VectorAgentBaseException):
    """Vector orchestrator-specific errors"""
    
    def __init__(self, message: str, **kwargs):
        super().__init__(
            message,
            error_code=kwargs.get("error_code", "VECTOR_ORCHESTRATION_ERROR"),
            recovery_suggestions=kwargs.get("recovery_suggestions", [
                "Check system resources and memory usage",
                "Verify vector orchestrator configuration",
                "Restart the vector orchestrator service"
            ]),
            **kwargs
        )


class BatchProcessingError(VectorAgentBaseException):
    """Batch processing operation errors"""
    
    def __init__(self, message: str, batch_id: str = None, failed_count: int = 0, **kwargs):
        context = kwargs.get("context", {})
        if batch_id:
            context["batch_id"] = batch_id
        if failed_count > 0:
            context["failed_count"] = failed_count
        
        super().__init__(
            message,
            error_code=kwargs.get("error_code", "BATCH_PROCESSING_ERROR"),
            context=context,
            recovery_suggestions=kwargs.get("recovery_suggestions", [
                "Reduce batch size and retry",
                "Check individual document validity",
                "Verify available system resources"
            ]),
            **kwargs
        )


# ===============================
# FAISS & INDEX ERRORS
# ===============================

class VectorIndexError(VectorAgentBaseException):
    """Vector indexing and FAISS-related errors"""
    
    def __init__(self, message: str, index_name: str = None, **kwargs):
        context = kwargs.get("context", {})
        if index_name:
            context["index_name"] = index_name
        
        super().__init__(
            message,
            error_code=kwargs.get("error_code", "VECTOR_INDEX_ERROR"),
            context=context,
            recovery_suggestions=kwargs.get("recovery_suggestions", [
                "Verify FAISS installation and compatibility",
                "Check vector dimensions and data types",
                "Ensure sufficient memory for index operations"
            ]),
            **kwargs
        )


class FAISSIndexError(VectorIndexError):
        try:
            logger.info(f"Executing __init__")
            
            # Implementation for __init__
            # TODO: Add specific business logic here
            
            result = None  # Replace with actual implementation
            
            logger.info(f"__init__ completed successfully")
            return result
            
        except Exception as e:
            logger.error(f"__init__ failed: {e}")
            raise
class FAISSIndexError(VectorIndexError):
    """FAISS-specific indexing errors"""
    
    def __init__(self, message: str, faiss_error: str = None, **kwargs):
        context = kwargs.get("context", {})
        if faiss_error:
            context["faiss_error"] = faiss_error
        
        super().__init__(
            message,
            error_code=kwargs.get("error_code", "FAISS_INDEX_ERROR"),
            context=context,
            recovery_suggestions=kwargs.get("recovery_suggestions", [
                "Verify FAISS library installation",
                "Check vector data format and dimensions",
                "Ensure index type compatibility with data"
            ]),
            **kwargs
        )


class IndexNotFoundError(VectorIndexError):
    """Index not found error"""
    
    def __init__(self, index_name: str, **kwargs):
        super().__init__(
            f"Vector index '{index_name}' not found",
            index_name=index_name,
            error_code="INDEX_NOT_FOUND",
            recovery_suggestions=[
                f"Create the index '{index_name}' before use",
                "Verify index name spelling and case",
                "Check if index was properly initialized"
            ],
            **kwargs
        )


class IndexCorruptionError(VectorIndexError):
    """Index corruption or integrity error"""
    
    def __init__(self, index_name: str, corruption_details: str = None, **kwargs):
        context = kwargs.get("context", {})
        context["corruption_details"] = corruption_details
        
        super().__init__(
            f"Vector index '{index_name}' is corrupted or invalid",
            index_name=index_name,
            context=context,
            error_code="INDEX_CORRUPTION",
            recovery_suggestions=[
                "Rebuild the corrupted index from source data",
                "Restore index from backup if available",
                "Clear and reinitialize the index"
            ],
            **kwargs
        )


# ===============================
# SIMILARITY & SEARCH ERRORS
# ===============================

class SimilarityComputationError(VectorAgentBaseException):
    """Similarity computation and algorithm errors"""
    
    def __init__(self, message: str, algorithm: str = None, **kwargs):
        context = kwargs.get("context", {})
        if algorithm:
            context["algorithm"] = algorithm
        
        super().__init__(
            message,
            error_code=kwargs.get("error_code", "SIMILARITY_COMPUTATION_ERROR"),
            context=context,
            recovery_suggestions=kwargs.get("recovery_suggestions", [
                "Verify vector data integrity and format",
                "Check similarity algorithm parameters",
                "Ensure vectors have compatible dimensions"
            ]),
            **kwargs
        )


class VectorSearchError(VectorAgentBaseException):
    """Vector search operation errors"""
    
    def __init__(self, message: str, query_id: str = None, **kwargs):
        context = kwargs.get("context", {})
        if query_id:
            context["query_id"] = query_id
        
        super().__init__(
            message,
            error_code=kwargs.get("error_code", "VECTOR_SEARCH_ERROR"),
            context=context,
            recovery_suggestions=kwargs.get("recovery_suggestions", [
                "Verify search query parameters",
                "Check index availability and health",
                "Adjust similarity threshold if needed"
            ]),
            **kwargs
        )


class SearchOptimizationError(VectorAgentBaseException):
    """Search optimization and caching errors"""
    
    def __init__(self, message: str, optimization_type: str = None, **kwargs):
        context = kwargs.get("context", {})
        if optimization_type:
            context["optimization_type"] = optimization_type
        
        super().__init__(
            message,
            error_code=kwargs.get("error_code", "SEARCH_OPTIMIZATION_ERROR"),
            context=context,
            recovery_suggestions=kwargs.get("recovery_suggestions", [
                "Clear search optimization cache",
                "Adjust optimization parameters",
                "Disable optimization temporarily if needed"
            ]),
            **kwargs
        )


# ===============================
# STORAGE & PERSISTENCE ERRORS
# ===============================

class VectorStorageError(VectorAgentBaseException):
        try:
            logger.info(f"Executing __init__")
            
            # Implementation for __init__
            # TODO: Add specific business logic here
            
            result = None  # Replace with actual implementation
            
            logger.info(f"__init__ completed successfully")
            return result
            
        except Exception as e:
            logger.error(f"__init__ failed: {e}")
            raise
        try:
            logger.info(f"Executing __init__")
            
            # Implementation for __init__
            # TODO: Add specific business logic here
            
            result = None  # Replace with actual implementation
            
            logger.info(f"__init__ completed successfully")
            return result
            
        except Exception as e:
            logger.error(f"__init__ failed: {e}")
            raise
            message,
            error_code=kwargs.get("error_code", "SEARCH_OPTIMIZATION_ERROR"),
            context=context,
            recovery_suggestions=kwargs.get("recovery_suggestions", [
                "Clear search optimization cache",
                "Adjust optimization parameters",
                "Disable optimization temporarily if needed"
            ]),
            **kwargs
        )


# ===============================
# STORAGE & PERSISTENCE ERRORS
# ===============================

class VectorStorageError(VectorAgentBaseException):
        try:
            logger.info(f"Executing __init__")
            
            # Implementation for __init__
            # TODO: Add specific business logic here
            
            result = None  # Replace with actual implementation
            
            logger.info(f"__init__ completed successfully")
            return result
            
        except Exception as e:
            logger.error(f"__init__ failed: {e}")
            raise
class VectorStorageError(VectorAgentBaseException):
    """Vector storage and persistence errors"""
    
    def __init__(self, message: str, storage_path: str = None, **kwargs):
        context = kwargs.get("context", {})
        if storage_path:
            context["storage_path"] = storage_path
        
        super().__init__(
            message,
            error_code=kwargs.get("error_code", "VECTOR_STORAGE_ERROR"),
            context=context,
            recovery_suggestions=kwargs.get("recovery_suggestions", [
                "Verify storage path permissions and disk space",
                "Check file system integrity",
                "Ensure proper database connectivity"
            ]),
            **kwargs
        )


class DocumentNotFoundError(VectorStorageError):
    """Document not found in storage"""
    
    def __init__(self, document_id: str, **kwargs):
        super().__init__(
            f"Vector document '{document_id}' not found in storage",
            error_code="DOCUMENT_NOT_FOUND",
            context={"document_id": document_id},
            recovery_suggestions=[
                f"Verify document ID '{document_id}' exists",
                "Check if document was properly stored",
                "Ensure storage system is accessible"
            ],
            **kwargs
        )


class StorageCorruptionError(VectorStorageError):
    """Storage corruption or integrity error"""
    
    def __init__(self, message: str, **kwargs):
        super().__init__(
            message,
            error_code="STORAGE_CORRUPTION",
            recovery_suggestions=[
                "Run storage integrity check",
                "Restore from backup if available",
                "Reinitialize storage system"
            ],
            **kwargs
        )


# ===============================
# VALIDATION & INPUT ERRORS
# ===============================

class VectorValidationError(VectorAgentBaseException):
    """Vector data validation errors"""
    
    def __init__(self, message: str, validation_type: str = None, **kwargs):
        context = kwargs.get("context", {})
        if validation_type:
            context["validation_type"] = validation_type
        
        super().__init__(
            message,
            error_code=kwargs.get("error_code", "VECTOR_VALIDATION_ERROR"),
            context=context,
            recovery_suggestions=kwargs.get("recovery_suggestions", [
                "Check vector data format and values",
                "Ensure vectors contain valid numerical data",
                "Verify vector dimensions are consistent"
            ]),
            **kwargs
        )


class DimensionMismatchError(VectorValidationError):
    """Vector dimension mismatch error"""
    
    def __init__(self, expected_dim: int, actual_dim: int, **kwargs):
        super().__init__(
            f"Vector dimension mismatch: expected {expected_dim}, got {actual_dim}",
            validation_type="dimension_mismatch",
            context={"expected_dimension": expected_dim, "actual_dimension": actual_dim},
            error_code="DIMENSION_MISMATCH",
            recovery_suggestions=[
                f"Ensure all vectors have dimension {expected_dim}",
                "Check vector preprocessing and feature extraction",
                "Verify data pipeline consistency"
            ],
            **kwargs
        )


class InvalidVectorDataError(VectorValidationError):
    """Invalid vector data format or content"""
    
    def __init__(self, message: str, data_issue: str = None, **kwargs):
        context = kwargs.get("context", {})
        if data_issue:
            context["data_issue"] = data_issue
        
        super().__init__(
            message,
            validation_type="invalid_data",
            context=context,
            error_code="INVALID_VECTOR_DATA",
            recovery_suggestions=[
                "Check for NaN or infinite values in vectors",
                "Ensure vector data is numerical",
                "Verify data preprocessing steps"
            ],
            **kwargs
        )


# ===============================
# CONFIGURATION ERRORS
# ===============================

class VectorConfigurationError(VectorAgentBaseException):
    """Vector configuration and setup errors"""
    
    def __init__(self, message: str, config_parameter: str = None, **kwargs):
        context = kwargs.get("context", {})
        if config_parameter:
            context["config_parameter"] = config_parameter
        
        super().__init__(
            message,
            error_code=kwargs.get("error_code", "VECTOR_CONFIGURATION_ERROR"),
            context=context,
            recovery_suggestions=kwargs.get("recovery_suggestions", [
                "Review and validate configuration parameters",
                "Check environment variable settings",
                "Refer to configuration documentation"
            ]),
            **kwargs
        )


class InvalidConfigurationError(VectorConfigurationError):
    """Invalid configuration parameter error"""
    
    def __init__(self, parameter: str, value: Any, reason: str = None, **kwargs):
        message = f"Invalid configuration parameter '{parameter}' = {value}"
        if reason:
            message += f": {reason}"
        
        super().__init__(
            message,
            config_parameter=parameter,
            context={"parameter": parameter, "value": value, "reason": reason},
        try:
            logger.info(f"Executing wrapper")
            
            # Implementation for wrapper
            # TODO: Add specific business logic here
            
            result = None  # Replace with actual implementation
            
            logger.info(f"wrapper completed successfully")
            return result
            
        except Exception as e:
            logger.error(f"wrapper failed: {e}")
            raise
            error_code="INVALID_CONFIGURATION",
            recovery_suggestions=[
                f"Correct the '{parameter}' configuration parameter",
                "Check parameter value ranges and constraints",
                "Refer to configuration schema documentation"
            ],
            **kwargs
        )


# ===============================
# RESOURCE & SYSTEM ERRORS
# ===============================

class VectorResourceError(VectorAgentBaseException):
    """System resource and capacity errors"""
    
    def __init__(self, message: str, resource_type: str = None, **kwargs):
        context = kwargs.get("context", {})
        if resource_type:
            context["resource_type"] = resource_type
        
        super().__init__(
            message,
            error_code=kwargs.get("error_code", "VECTOR_RESOURCE_ERROR"),
            context=context,
            recovery_suggestions=kwargs.get("recovery_suggestions", [
                "Check available system resources",
                "Reduce processing batch size",
                "Clear caches to free memory"
            ]),
            **kwargs
        )


class OutOfMemoryError(VectorResourceError):
    """Out of memory error"""
    
    def __init__(self, operation: str = None, required_mb: int = None, **kwargs):
        context = kwargs.get("context", {})
        if operation:
            context["operation"] = operation
        if required_mb:
            context["required_memory_mb"] = required_mb
        
        message = "Insufficient memory for vector operation"
        if operation:
            message += f" ({operation})"
        if required_mb:
            message += f" - requires ~{required_mb}MB"
        
        super().__init__(
            message,
            resource_type="memory",
            context=context,
            error_code="OUT_OF_MEMORY",
            recovery_suggestions=[
                "Reduce batch size or vector dimensions",
                "Clear vector caches and indices",
                "Increase available system memory",
                "Use memory-efficient processing modes"
            ],
            **kwargs
        )


class TimeoutError(VectorResourceError):
    """Operation timeout error"""
    
    def __init__(self, operation: str, timeout_seconds: float = None, **kwargs):
        context = kwargs.get("context", {})
        context["operation"] = operation
        if timeout_seconds:
            context["timeout_seconds"] = timeout_seconds
        
        message = f"Operation '{operation}' timed out"
        if timeout_seconds:
            message += f" after {timeout_seconds} seconds"
        
        super().__init__(
            message,
            resource_type="time",
            context=context,
            error_code="OPERATION_TIMEOUT",
            recovery_suggestions=[
                "Increase timeout configuration",
                "Optimize operation parameters",
                "Check system performance",
                "Break large operations into smaller chunks"
            ],
            **kwargs
        )


# ===============================
# UTILITY FUNCTIONS
# ===============================

def handle_vector_exception(func):
    """Decorator to handle and wrap vector exceptions"""
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except VectorAgentBaseException:
            # Re-raise vector agent exceptions as-is
            raise
        except Exception as e:
            # Wrap other exceptions
            raise VectorProcessingError(
                f"Unexpected error in {func.__name__}: {str(e)}",
                error_code="UNEXPECTED_ERROR",
                original_exception=e,
                context={"function": func.__name__}
            )
    return wrapper


def create_error_response(exception: VectorAgentBaseException) -> Dict[str, Any]:
    """Create standardized error response from exception"""
    return {
        "success": False,
        "error": {
            "type": exception.__class__.__name__,
            "code": exception.error_code,
            "message": exception.message,
            "context": exception.context,
            "recovery_suggestions": exception.recovery_suggestions,
            "timestamp": exception.timestamp.isoformat()
        }
    }


def log_vector_exception(logger, exception: VectorAgentBaseException, level: str = "error"):
    """Log vector exception with appropriate detail level"""
    log_method = getattr(logger, level, logger.error)
    
    log_data = {
        "error_type": exception.__class__.__name__,
        "error_code": exception.error_code,
        "message": exception.message,
        "context": exception.context
    }
    
    log_method(f"Vector Agent Error: {exception}", extra=log_data)
