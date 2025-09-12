"""{{model_name}} Pydantic Model Template for Ainflue Platform
{{model_description}}

Author: {{author_name}} ({{author_email}})
Created: {{created_date}}
DBA Role: Advanced Pydantic models with validation, serialization, and enterprise features
"""

import logging
from typing import Dict, Any, Optional, List, Union, Set, Callable, Type
from datetime import datetime, timezone
from enum import Enum
from uuid import UUID, uuid4
import re
from decimal import Decimal

from pydantic import (
    BaseModel, 
    Field, 
    validator, 
    root_validator,
    ConfigDict,
    EmailStr,
    HttpUrl,
    AnyUrl,
    SecretStr,
    StrictBool,
    StrictInt,
    StrictFloat,
    constr,
    conint,
    confloat,
    conlist
)
from pydantic.types import PositiveInt, NonNegativeInt, PositiveFloat
from pydantic.json import custom_pydantic_encoder

logger = logging.getLogger(__name__)


class RecordStatus(str, Enum):
    """Enterprise record status enumeration"""
    ACTIVE = "active"
    INACTIVE = "inactive" 
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    DRAFT = "draft"
    PUBLISHED = "published"
    ARCHIVED = "archived"
    DELETED = "deleted"
    SUSPENDED = "suspended"


class Priority(int, Enum):
    """Priority levels for records"""
    LOW = 1
    MEDIUM = 5
    HIGH = 8
    CRITICAL = 10


class ValidationMode(str, Enum):
    """Validation modes for different environments"""
    STRICT = "strict"
    LENIENT = "lenient"
    DEVELOPMENT = "development"
    PRODUCTION = "production"


class BaseAuditModel(BaseModel):
    """Base audit model with common enterprise fields"""
    
    model_config = ConfigDict(
        # Core configuration
        str_strip_whitespace=True,
        validate_assignment=True,
        use_enum_values=True,
        extra='forbid',
        frozen=False,
        populate_by_name=True,
        
        # JSON configuration
        json_encoders={
            datetime: lambda v: v.isoformat(),
            UUID: lambda v: str(v),
            Decimal: lambda v: float(v),
            set: lambda v: list(v)
        },
        
        # Schema configuration
        title="{{model_name}} Audit Model",
        description="Enterprise audit model with comprehensive tracking"
    )
    
    # Core audit fields
    id: Optional[UUID] = Field(
        default_factory=uuid4,
        description="Unique identifier",
        json_schema_extra={"example": "123e4567-e89b-12d3-a456-426614174000"}
    )
    
    created_at: Optional[datetime] = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="Creation timestamp",
        json_schema_extra={"example": "2025-01-01T00:00:00Z"}
    )
    
    updated_at: Optional[datetime] = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="Last update timestamp",
        json_schema_extra={"example": "2025-01-01T00:00:00Z"}
    )
    
    created_by: Optional[UUID] = Field(
        default=None,
        description="User who created the record",
        json_schema_extra={"example": "123e4567-e89b-12d3-a456-426614174000"}
    )
    
    updated_by: Optional[UUID] = Field(
        default=None,
        description="User who last updated the record",
        json_schema_extra={"example": "123e4567-e89b-12d3-a456-426614174000"}
    )
    
    version: PositiveInt = Field(
        default=1,
        description="Record version for optimistic locking",
        json_schema_extra={"example": 1}
    )
    
    def update_timestamp(self, user_id: Optional[UUID] = None):
        """Update the timestamp and user tracking"""
        self.updated_at = datetime.now(timezone.utc)
        if user_id:
            self.updated_by = user_id
        self.version += 1


class BaseSoftDeleteModel(BaseAuditModel):
    """Base model with soft delete functionality"""
    
    is_deleted: StrictBool = Field(
        default=False,
        description="Soft delete flag",
        json_schema_extra={"example": False}
    )
    
    deleted_at: Optional[datetime] = Field(
        default=None,
        description="Deletion timestamp",
        json_schema_extra={"example": "2025-01-01T00:00:00Z"}
    )
    
    deleted_by: Optional[UUID] = Field(
        default=None,
        description="User who deleted the record",
        json_schema_extra={"example": "123e4567-e89b-12d3-a456-426614174000"}
    )
    
    def soft_delete(self, user_id: Optional[UUID] = None):
        """Perform soft delete"""
        self.is_deleted = True
        self.deleted_at = datetime.now(timezone.utc)
        if user_id:
            self.deleted_by = user_id
        self.update_timestamp(user_id)
    
    def restore(self, user_id: Optional[UUID] = None):
        """Restore soft deleted record"""
        self.is_deleted = False
        self.deleted_at = None
        self.deleted_by = None
        self.update_timestamp(user_id)


class {{model_name}}Model(BaseSoftDeleteModel):
    """{{model_description}}
    
    Enterprise Pydantic model providing:
    - Comprehensive field validation with custom validators
    - JSON serialization/deserialization
    - Audit trail and version control
    - Soft delete functionality
    - Multi-tenant support
    - Search and filtering capabilities
    - Data transformation and normalization
    - Security and compliance features
    - Performance optimization
    - API documentation generation
    """
    
    model_config = ConfigDict(
        **BaseSoftDeleteModel.model_config.copy(),
        title="{{model_name}} Enterprise Model",
        description="{{model_description}}"
    )
    
    # Core business fields
    name: constr(min_length=1, max_length=255, strip_whitespace=True) = Field(
        ...,
        description="Record name",
        json_schema_extra={
            "example": "Sample {{model_name}}",
            "pattern": r"^[a-zA-Z0-9\s\-_\.]+$"
        }
    )
    
    description: Optional[constr(max_length=2000, strip_whitespace=True)] = Field(
        default=None,
        description="Detailed description",
        json_schema_extra={"example": "This is a sample description"}
    )
    
    status: RecordStatus = Field(
        default=RecordStatus.ACTIVE,
        description="Record status",
        json_schema_extra={"example": "active"}
    )
    
    # Business categorization
    category: Optional[constr(max_length=100, strip_whitespace=True)] = Field(
        default=None,
        description="Business category",
        json_schema_extra={"example": "general"}
    )
    
    subcategory: Optional[constr(max_length=100, strip_whitespace=True)] = Field(
        default=None,
        description="Business subcategory",
        json_schema_extra={"example": "content"}
    )
    
    # Tagging and metadata
    tags: Optional[conlist(str, min_items=0, max_items=20)] = Field(
        default=None,
        description="Record tags for categorization",
        json_schema_extra={"example": ["tag1", "tag2", "tag3"]}
    )
    
    metadata: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Additional metadata as JSON",
        json_schema_extra={"example": {"key": "value", "config": {"enabled": True}}}
    )
    
    config: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Configuration data",
        json_schema_extra={"example": {"settings": {"auto_save": True}}}
    )
    
    # Business logic fields
    priority: Priority = Field(
        default=Priority.MEDIUM,
        description="Business priority level",
        json_schema_extra={"example": 5}
    )
    
    weight: PositiveFloat = Field(
        default=1.0,
        description="Relative weight for calculations",
        json_schema_extra={"example": 1.5}
    )
    
    score: Optional[confloat(ge=0.0, le=100.0)] = Field(
        default=None,
        description="Quality or relevance score (0-100)",
        json_schema_extra={"example": 85.5}
    )
    
    # Visibility and access control
    is_public: StrictBool = Field(
        default=False,
        description="Public visibility flag",
        json_schema_extra={"example": False}
    )
    
    is_featured: StrictBool = Field(
        default=False,
        description="Featured content flag",
        json_schema_extra={"example": False}
    )
    
    is_locked: StrictBool = Field(
        default=False,
        description="Edit lock flag",
        json_schema_extra={"example": False}
    )
    
    is_verified: StrictBool = Field(
        default=False,
        description="Verification status",
        json_schema_extra={"example": False}
    )
    
    # Multi-tenant support
    tenant_id: Optional[UUID] = Field(
        default=None,
        description="Tenant identifier for multi-tenancy",
        json_schema_extra={"example": "123e4567-e89b-12d3-a456-426614174000"}
    )
    
    workspace_id: Optional[UUID] = Field(
        default=None,
        description="Workspace identifier",
        json_schema_extra={"example": "123e4567-e89b-12d3-a456-426614174000"}
    )
    
    # Relationship fields
    owner_id: Optional[UUID] = Field(
        default=None,
        description="Owner user identifier",
        json_schema_extra={"example": "123e4567-e89b-12d3-a456-426614174000"}
    )
    
    parent_id: Optional[UUID] = Field(
        default=None,
        description="Parent record identifier",
        json_schema_extra={"example": "123e4567-e89b-12d3-a456-426614174000"}
    )
    
    # Search and indexing
    search_terms: Optional[conlist(str, min_items=0, max_items=50)] = Field(
        default=None,
        description="Search terms for full-text search",
        json_schema_extra={"example": ["search", "term", "keyword"]}
    )
    
    keywords: Optional[conlist(str, min_items=0, max_items=30)] = Field(
        default=None,
        description="SEO keywords",
        json_schema_extra={"example": ["keyword1", "keyword2"]}
    )
    
    # External references
    external_id: Optional[constr(max_length=255)] = Field(
        default=None,
        description="External system identifier",
        json_schema_extra={"example": "ext_123456"}
    )
    
    source_url: Optional[AnyUrl] = Field(
        default=None,
        description="Source URL reference",
        json_schema_extra={"example": "https://example.com/source"}
    )
    
    # Validation and business rules
    
    @validator('name')
    def validate_name(cls, v):
        """Validate name field with business rules"""
        if not v or not v.strip():
            raise ValueError('Name cannot be empty')
        
        # Business rule: No profanity or inappropriate content
        inappropriate_words = ['spam', 'test123', 'dummy']  # Extend as needed
        if any(word.lower() in v.lower() for word in inappropriate_words):
            raise ValueError('Name contains inappropriate content')
        
        # Business rule: Must not be just numbers
        if v.strip().isdigit():
            raise ValueError('Name cannot be just numbers')
        
        return v.strip()
    
    @validator('tags')
    def validate_tags(cls, v):
        """Validate and normalize tags"""
        if v is not None:
            # Normalize tags: lowercase, remove duplicates, strip whitespace
            normalized_tags = []
            seen = set()
            
            for tag in v:
                if isinstance(tag, str) and tag.strip():
                    normalized_tag = tag.strip().lower()
                    if normalized_tag not in seen and len(normalized_tag) <= 50:
                        normalized_tags.append(normalized_tag)
                        seen.add(normalized_tag)
            
            return normalized_tags if normalized_tags else None
        return v
    
    @validator('metadata', 'config')
    def validate_json_fields(cls, v):
        """Validate JSON fields for security and size"""
        if v is not None:
            # Convert to JSON string and check size
            import json
            json_str = json.dumps(v)
            if len(json_str) > 10000:  # 10KB limit
                raise ValueError('JSON field too large (max 10KB)')
            
            # Check for suspicious patterns
            if any(pattern in json_str.lower() for pattern in ['<script', 'javascript:', 'data:']):
                raise ValueError('JSON contains potentially malicious content')
        
        return v
    
    @validator('score')
    def validate_score(cls, v):
        """Validate score field"""
        if v is not None:
            if not 0.0 <= v <= 100.0:
                raise ValueError('Score must be between 0 and 100')
        return v
    
    @root_validator
    def validate_model_consistency(cls, values):
        """Validate model-level business rules"""
        # Business rule: Featured items must be public
        if values.get('is_featured') and not values.get('is_public'):
            raise ValueError('Featured items must be public')
        
        # Business rule: Locked items cannot be deleted
        if values.get('is_locked') and values.get('is_deleted'):
            raise ValueError('Locked items cannot be deleted')
        
        # Business rule: Parent cannot be self
        if values.get('parent_id') and values.get('id'):
            if values['parent_id'] == values['id']:
                raise ValueError('Record cannot be its own parent')
        
        return values
    
    # Business methods
    
    def add_tag(self, tag: str) -> None:
        """Add a tag to the record"""
        if self.tags is None:
            self.tags = []
        
        normalized_tag = tag.strip().lower()
        if normalized_tag and normalized_tag not in self.tags and len(self.tags) < 20:
            self.tags.append(normalized_tag)
    
    def remove_tag(self, tag: str) -> None:
        """Remove a tag from the record"""
        if self.tags:
            normalized_tag = tag.strip().lower()
            if normalized_tag in self.tags:
                self.tags.remove(normalized_tag)
    
    def set_metadata(self, key: str, value: Any) -> None:
        """Set metadata key-value pair"""
        if self.metadata is None:
            self.metadata = {}
        self.metadata[key] = value
    
    def get_metadata(self, key: str, default: Any = None) -> Any:
        """Get metadata value by key"""
        if self.metadata is None:
            return default
        return self.metadata.get(key, default)
    
    def calculate_relevance_score(self) -> float:
        """Calculate relevance score based on various factors"""
        score = 0.0
        
        # Priority contribution (0-40 points)
        score += (self.priority.value / 10.0) * 40
        
        # Feature status contribution (0-20 points)
        if self.is_featured:
            score += 20
        
        # Public visibility contribution (0-10 points)
        if self.is_public:
            score += 10
        
        # Verification contribution (0-15 points)
        if self.is_verified:
            score += 15
        
        # Tags contribution (0-15 points)
        if self.tags:
            score += min(len(self.tags) * 3, 15)
        
        return min(score, 100.0)
    
    def generate_search_terms(self) -> List[str]:
        """Generate search terms for indexing"""
        terms = []
        
        if self.name:
            terms.extend(self.name.lower().split())
        
        if self.description:
            terms.extend(self.description.lower().split())
        
        if self.category:
            terms.append(self.category.lower())
        
        if self.subcategory:
            terms.append(self.subcategory.lower())
        
        if self.tags:
            terms.extend(self.tags)
        
        # Remove duplicates and filter out common stop words
        stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by'}
        unique_terms = list(set(term for term in terms if term and term not in stop_words))
        
        return unique_terms[:50]  # Limit to 50 terms
    
    def to_search_document(self) -> Dict[str, Any]:
        """Convert to search document format"""
        return {
            'id': str(self.id),
            'name': self.name,
            'description': self.description,
            'category': self.category,
            'subcategory': self.subcategory,
            'tags': self.tags or [],
            'status': self.status.value,
            'is_public': self.is_public,
            'is_featured': self.is_featured,
            'is_verified': self.is_verified,
            'priority': self.priority.value,
            'score': self.score,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'search_terms': self.generate_search_terms(),
            'tenant_id': str(self.tenant_id) if self.tenant_id else None,
            'workspace_id': str(self.workspace_id) if self.workspace_id else None,
            'owner_id': str(self.owner_id) if self.owner_id else None
        }
    
    class Config:
        """Pydantic configuration"""
        # JSON serialization
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            UUID: lambda v: str(v),
            set: lambda v: list(v)
        }
        
        # Schema generation
        schema_extra = {
            "example": {
                "name": "Sample {{model_name}}",
                "description": "This is a sample {{model_name}} record",
                "status": "active",
                "category": "general",
                "tags": ["sample", "example"],
                "priority": 5,
                "weight": 1.0,
                "is_public": False,
                "is_featured": False,
                "metadata": {"key": "value"}
            }
        }


# Specialized models for different operations

class {{model_name}}Create(BaseModel):
    """Schema for creating {{model_name}} records"""
    
    model_config = ConfigDict(
        str_strip_whitespace=True,
        extra='forbid'
    )
    
    name: constr(min_length=1, max_length=255, strip_whitespace=True)
    description: Optional[constr(max_length=2000, strip_whitespace=True)] = None
    category: Optional[constr(max_length=100, strip_whitespace=True)] = None
    subcategory: Optional[constr(max_length=100, strip_whitespace=True)] = None
    tags: Optional[conlist(str, min_items=0, max_items=20)] = None
    metadata: Optional[Dict[str, Any]] = None
    config: Optional[Dict[str, Any]] = None
    priority: Optional[Priority] = Priority.MEDIUM
    weight: Optional[PositiveFloat] = 1.0
    is_public: Optional[StrictBool] = False
    is_featured: Optional[StrictBool] = False
    tenant_id: Optional[UUID] = None
    workspace_id: Optional[UUID] = None
    owner_id: Optional[UUID] = None
    parent_id: Optional[UUID] = None


class {{model_name}}Update(BaseModel):
    """Schema for updating {{model_name}} records"""
    
    model_config = ConfigDict(
        str_strip_whitespace=True,
        extra='forbid'
    )
    
    name: Optional[constr(min_length=1, max_length=255, strip_whitespace=True)] = None
    description: Optional[constr(max_length=2000, strip_whitespace=True)] = None
    status: Optional[RecordStatus] = None
    category: Optional[constr(max_length=100, strip_whitespace=True)] = None
    subcategory: Optional[constr(max_length=100, strip_whitespace=True)] = None
    tags: Optional[conlist(str, min_items=0, max_items=20)] = None
    metadata: Optional[Dict[str, Any]] = None
    config: Optional[Dict[str, Any]] = None
    priority: Optional[Priority] = None
    weight: Optional[PositiveFloat] = None
    score: Optional[confloat(ge=0.0, le=100.0)] = None
    is_public: Optional[StrictBool] = None
    is_featured: Optional[StrictBool] = None
    is_locked: Optional[StrictBool] = None
    is_verified: Optional[StrictBool] = None


class {{model_name}}Response({{model_name}}Model):
    """Schema for API responses"""
    
    model_config = ConfigDict(
        from_attributes=True
    )


class {{model_name}}List(BaseModel):
    """Schema for list responses with pagination"""
    
    items: List[{{model_name}}Response]
    total: NonNegativeInt
    page: PositiveInt
    size: PositiveInt
    pages: PositiveInt
    
    @validator('pages', pre=True, always=True)
    def calculate_pages(cls, v, values):
        """Calculate total pages"""
        if 'total' in values and 'size' in values:
            total = values['total']
            size = values['size']
            return (total + size - 1) // size if size > 0 else 1
        return v


class {{model_name}}Filter(BaseModel):
    """Schema for filtering {{model_name}} records"""
    
    name: Optional[str] = None
    status: Optional[List[RecordStatus]] = None
    category: Optional[List[str]] = None
    tags: Optional[List[str]] = None
    is_public: Optional[bool] = None
    is_featured: Optional[bool] = None
    is_verified: Optional[bool] = None
    created_after: Optional[datetime] = None
    created_before: Optional[datetime] = None
    updated_after: Optional[datetime] = None
    updated_before: Optional[datetime] = None
    tenant_id: Optional[UUID] = None
    workspace_id: Optional[UUID] = None
    owner_id: Optional[UUID] = None
    
    # Search and sorting
    search: Optional[str] = None
    sort_by: Optional[str] = 'created_at'
    sort_order: Optional[str] = 'desc'
    
    @validator('sort_order')
    def validate_sort_order(cls, v):
        if v not in ['asc', 'desc']:
            raise ValueError('Sort order must be "asc" or "desc"')
        return v


# Export models for easy import
__all__ = [
    'RecordStatus',
    'Priority', 
    'ValidationMode',
    'BaseAuditModel',
    'BaseSoftDeleteModel',
    '{{model_name}}Model',
    '{{model_name}}Create',
    '{{model_name}}Update', 
    '{{model_name}}Response',
    '{{model_name}}List',
    '{{model_name}}Filter'
]