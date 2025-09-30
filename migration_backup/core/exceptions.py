"""Core Exceptions Module
======================

Basic exception classes for the data ingestion module.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel - All Rights Reserved
"""


class BaseIngestionError(Exception):
    """Base exception for ingestion module"""
    pass


class IngestionError(BaseIngestionError):
    """General ingestion error"""
    pass


class WorkflowError(BaseIngestionError):
    """Workflow execution error"""
    pass


class ValidationError(BaseIngestionError):
    """Content validation error"""
    pass


class PipelineException(BaseIngestionError):
    """Pipeline execution error"""
    pass


class ProcessingError(BaseIngestionError):
    """Content processing error"""
    pass


class TransformationError(BaseIngestionError):
    """Content transformation error"""
    pass


class RoutingError(BaseIngestionError):
    """Content routing error"""
    pass


class StreamingError(BaseIngestionError):
    """Streaming operation error"""
    pass


class BatchProcessingError(BaseIngestionError):
    """Batch processing error"""
    pass


class ConnectionError(BaseIngestionError):
    """Connection error"""
    pass


class SecurityError(BaseIngestionError):
    """Security validation error"""
    pass


class QualityError(BaseIngestionError):
    """Quality assessment error"""
    pass


class MetadataExtractionError(BaseIngestionError):
    """Metadata extraction error"""
    pass