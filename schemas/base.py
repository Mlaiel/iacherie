"""Professional Base Schemas for IA Influencer Agent Platform
Core foundational schemas for data validation and serialization

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

🚨 INTELLECTUAL PROPERTY WARNING: Unauthorized use prohibited.
Contact: mlaiel@live.de for licensing and permissions.
"""

from datetime import datetime
from typing import Any, Dict, Generic, List, Optional, TypeVar, Union
from uuid import UUID

from pydantic import BaseModel, Field, ConfigDict
from pydantic.generics import GenericModel


# Configuration for all schemas
class BaseSchema(BaseModel):
    """
Base schema with common configuration for all Pydantic models."""
    
    model_config = ConfigDict(
        # Allow population by field name or alias
        populate_by_name=True,
        # Validate assignments after object creation
        validate_assignment=True,
        # Use enum values instead of names
        use_enum_values=True,
        # Allow arbitrary types (for complex types like numpy arrays)
        arbitrary_types_allowed=True,
        # Strict validation
        str_strip_whitespace=True,
        # JSON serialization config
        json_encoders={
            datetime: lambda v: v.isoformat(),
            UUID: str,
        },
        # Schema generation config
        extra='forbid'
    )


# Generic type for paginated responses
DataT = TypeVar('DataT')


class PaginatedResponse(GenericModel, Generic[DataT]):
    """
Professional paginated response schema for API endpoints."""
    
    items: List[DataT] = Field(description="List of items in current page")
    total: int = Field(description="Total number of items across all pages")
    page: int = Field(description="Current page number (1-indexed)")
    page_size: int = Field(description="Number of items per page")
    total_pages: int = Field(description="Total number of pages")
    has_next: bool = Field(description="Whether there is a next page")
    has_previous: bool = Field(description="Whether there is a previous page")
    
    @classmethod
    def create(
        cls,
        items: List[DataT],
        total: int,
        page: int,
        page_size: int
    ) -> "PaginatedResponse[DataT]":
        """Create paginated response with calculated metadata."""
        total_pages = (total + page_size - 1) // page_size if total > 0 else 0
        
        return cls(
            items=items,
            total=total,
            page=page,
            page_size=page_size,
            total_pages=total_pages,
            has_next=page < total_pages,
            has_previous=page > 1
        )


class ApiResponse(GenericModel, Generic[DataT]):
    """
Professional API response wrapper with status and metadata."""
    
    success: bool = Field(description="Whether the operation was successful")
    data: Optional[DataT] = Field(None, description="Response data")
    message: str = Field(description="Human-readable message")
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    request_id: Optional[str] = Field(None, description="Unique request identifier")
    metadata: Dict[str, Any] = Field(default_factory=dict)
    
    @classmethod
    def success_response(
        cls,
        data: DataT,
        message: str = "Operation completed successfully",
        metadata: Optional[Dict[str, Any]] = None
    ) -> "ApiResponse[DataT]":
        """Create a successful API response."""
        return cls(
            success=True,
            data=data,
            message=message,
            metadata=metadata or {}
        )
    
    @classmethod
    def error_response(
        cls,
        message: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> "ApiResponse[None]":
        """Create an error API response."""
        return cls(
            success=False,
            data=None,
            message=message,
            metadata=metadata or {}
        )


class ValidationError(BaseSchema):
    """
Professional validation error schema."""
    
    field: str = Field(description="Field that failed validation")
    message: str = Field(description="Validation error message")
    value: Optional[Any] = Field(None, description="Invalid value that caused error")
    constraint: Optional[str] = Field(None, description="Validation constraint that was violated")


class BulkOperationResult(BaseSchema):
    """Result schema for bulk operations."""
    
    total_processed: int = Field(description="Total number of items processed")
    successful: int = Field(description="Number of successfully processed items")
    failed: int = Field(description="Number of failed items")
    errors: List[ValidationError] = Field(default_factory=list)
    processing_time_seconds: float = Field(description="Total processing time")
    
    @property
    def success_rate(self) -> float:
        """Calculate success rate percentage."""
        if self.total_processed == 0:
            return 0.0
        return (self.successful / self.total_processed) * 100


class TimestampSchema(BaseSchema):
    """
Schema mixin for timestamp fields."""
    
    created_at: datetime = Field(description="Creation timestamp")
    updated_at: datetime = Field(description="Last update timestamp")


class UUIDSchema(BaseSchema):
    """Schema mixin for UUID-based identifiers."""
    
    id: UUID = Field(description="Unique identifier")


class AuditSchema(BaseSchema):
    """Schema mixin for audit trail fields."""
    
    created_by: Optional[UUID] = Field(None, description="ID of user who created this record")
    updated_by: Optional[UUID] = Field(None, description="ID of user who last updated this record")
    version: int = Field(default=1, description="Record version for optimistic locking")


class SoftDeleteSchema(BaseSchema):
    """Schema mixin for soft delete functionality."""
    
    is_deleted: bool = Field(default=False, description="Whether this record is soft deleted")
    deleted_at: Optional[datetime] = Field(None, description="Soft deletion timestamp")
    deleted_by: Optional[UUID] = Field(None, description="ID of user who soft deleted this record")


class MetadataSchema(BaseSchema):
    """Schema for flexible metadata storage."""
    
    metadata: Dict[str, Any] = Field(
        default_factory=dict,
        description="Flexible metadata storage for additional properties"
    )


class SearchQuerySchema(BaseSchema):
    """Professional search query schema with filtering and sorting."""
    
    query: Optional[str] = Field(None, description="Search query string")
    filters: Dict[str, Any] = Field(default_factory=dict, description="Search filters")
    sort_by: Optional[str] = Field(None, description="Field to sort by")
    sort_order: str = Field("desc", regex="^(asc|desc)$", description="Sort order")
    page: int = Field(1, ge=1, description="Page number")
    page_size: int = Field(10, ge=1, le=100, description="Items per page")
    include_deleted: bool = Field(False, description="Include soft deleted records")


class FileUploadSchema(BaseSchema):
    """Schema for file upload operations."""
    
    filename: str = Field(description="Original filename")
    content_type: str = Field(description="MIME content type")
    size: int = Field(ge=0, description="File size in bytes")
    checksum: str = Field(description="File checksum for integrity verification")
    upload_url: Optional[str] = Field(None, description="Pre-signed upload URL")
    

class ProcessingStatusSchema(BaseSchema):
    """Schema for async processing status."""
    
    task_id: str = Field(description="Unique task identifier")
    status: str = Field(description="Processing status")
    progress: float = Field(ge=0.0, le=1.0, description="Progress percentage (0-1)")
    started_at: datetime = Field(description="Processing start time")
    completed_at: Optional[datetime] = Field(None, description="Processing completion time")
    error_message: Optional[str] = Field(None, description="Error message if failed")
    result_data: Optional[Dict[str, Any]] = Field(None, description="Processing result data")


class HealthCheckSchema(BaseSchema):
    """System health check schema."""
    
    service: str = Field(description="Service name")
    status: str = Field(description="Health status")
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    response_time_ms: float = Field(description="Response time in milliseconds")
    dependencies: List[Dict[str, Any]] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)
