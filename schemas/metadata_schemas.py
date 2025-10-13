"""IA Influencer Agent Platform - Metadata Management Schemas
Comprehensive metadata patterns for content, system, and business data.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

This module provides metadata schemas for:
- Content metadata (title, description, tags, etc.)
- Technical metadata (file format, encoding, etc.)
- Business metadata (categories, pricing, etc.)
- System metadata (versions, permissions, etc.)
- Custom metadata extensibility
"""

from typing import Optional, List, Dict, Any, Union
from enum import Enum
from datetime import datetime, date
from decimal import Decimal
from pydantic import BaseModel, Field, validator
from .base import BaseSchema, UUIDSchema, TimestampSchema
from .primitive_types import TagType, LanguageCodeType, CountryCodeType, CurrencyAmountType


class MetadataType(str, Enum):
    """Types of metadata."""
    CONTENT = "content"
    TECHNICAL = "technical"
    BUSINESS = "business"
    SYSTEM = "system"
    CUSTOM = "custom"
    WORKFLOW = "workflow"
    LEGAL = "legal"
    PERFORMANCE = "performance"


class DataFormat(str, Enum):
    """Data format types."""
    JSON = "json"
    XML = "xml"
    YAML = "yaml"
    CSV = "csv"
    BINARY = "binary"
    TEXT = "text"
    MARKDOWN = "markdown"
    HTML = "html"


class MetadataScope(str, Enum):
    """Metadata scope levels."""
    GLOBAL = "global"
    PLATFORM = "platform"
    TENANT = "tenant"
    USER = "user"
    SESSION = "session"
    REQUEST = "request"


class AccessLevel(str, Enum):
    """Metadata access levels."""
    PUBLIC = "public"
    INTERNAL = "internal"
    PRIVATE = "private"
    RESTRICTED = "restricted"
    CONFIDENTIAL = "confidential"


class ContentClassification(str, Enum):
    """Content classification levels."""
    PUBLIC = "public"
    INTERNAL = "internal"
    CONFIDENTIAL = "confidential"
    RESTRICTED = "restricted"
    TOP_SECRET = "top_secret"


# =================== CORE METADATA SCHEMAS ===================

class MetadataField(BaseSchema):
    """Individual metadata field definition."""
    
    key: str = Field(..., description="Metadata key")
    value: Any = Field(..., description="Metadata value")
    data_type: str = Field(..., description="Data type of the value")
    description: Optional[str] = Field(None, description="Field description")
    is_required: bool = Field(False, description="Whether field is required")
    is_indexed: bool = Field(True, description="Whether field is indexed for search")
    is_encrypted: bool = Field(False, description="Whether field value is encrypted")
    access_level: AccessLevel = Field(AccessLevel.PUBLIC, description="Access level")
    validation_rules: List[str] = Field(default=[], description="Validation rules")
    
    @validator('key')
    def validate_key(cls, v):
        """Validate metadata key format."""
        import re
        if not re.match(r'^[a-zA-Z][a-zA-Z0-9_.-]*$', v):
            raise ValueError('Invalid metadata key format')
        return v.lower()


class BaseMetadata(UUIDSchema, TimestampSchema):
    """Base metadata schema with common fields."""
    
    metadata_type: MetadataType = Field(..., description="Type of metadata")
    scope: MetadataScope = Field(MetadataScope.PLATFORM, description="Metadata scope")
    entity_type: str = Field(..., description="Type of entity this metadata belongs to")
    entity_id: str = Field(..., description="ID of the entity")
    
    fields: List[MetadataField] = Field(..., description="Metadata fields")
    schema_version: str = Field("1.0.0", description="Metadata schema version")
    
    # System information
    created_by: Optional[str] = Field(None, description="User who created metadata")
    last_modified_by: Optional[str] = Field(None, description="User who last modified metadata")
    version: int = Field(1, description="Metadata version number")
    
    # Access control
    access_level: AccessLevel = Field(AccessLevel.PUBLIC, description="Overall access level")
    permissions: Dict[str, List[str]] = Field(default={}, description="Permission mappings")
    
    # Validation
    is_valid: bool = Field(True, description="Whether metadata is valid")
    validation_errors: List[str] = Field(default=[], description="Validation errors")
    validation_timestamp: Optional[datetime] = Field(None, description="Last validation timestamp")


# =================== CONTENT METADATA ===================

class ContentMetadata(BaseMetadata):
    """Content-specific metadata."""
    
    # Basic content information
    title: str = Field(..., max_length=500, description="Content title")
    description: Optional[str] = Field(None, max_length=5000, description="Content description")
    summary: Optional[str] = Field(None, max_length=1000, description="Content summary")
    
    # Categorization
    category: str = Field(..., description="Primary content category")
    subcategory: Optional[str] = Field(None, description="Content subcategory")
    tags: List[TagType] = Field(default=[], description="Content tags")
    keywords: List[str] = Field(default=[], description="SEO keywords")
    
    # Language and location
    language: LanguageCodeType = Field(..., description="Content language")
    secondary_languages: List[LanguageCodeType] = Field(default=[], description="Secondary languages")
    country: Optional[CountryCodeType] = Field(None, description="Target country")
    region: Optional[str] = Field(None, description="Target region")
    
    # Content properties
    content_type: str = Field(..., description="MIME type or content type")
    format: str = Field(..., description="Content format")
    duration: Optional[int] = Field(None, ge=0, description="Duration in seconds")
    file_size: Optional[int] = Field(None, ge=0, description="File size in bytes")
    resolution: Optional[str] = Field(None, description="Content resolution")
    quality: Optional[str] = Field(None, description="Content quality level")
    
    # Publishing information
    publication_date: Optional[datetime] = Field(None, description="Publication date")
    expiration_date: Optional[datetime] = Field(None, description="Expiration date")
    is_published: bool = Field(False, description="Whether content is published")
    is_featured: bool = Field(False, description="Whether content is featured")
    is_trending: bool = Field(False, description="Whether content is trending")
    
    # Audience information
    target_audience: List[str] = Field(default=[], description="Target audience segments")
    age_rating: Optional[str] = Field(None, description="Age rating")
    content_warnings: List[str] = Field(default=[], description="Content warnings")
    
    # Engagement metrics
    view_count: int = Field(0, ge=0, description="View count")
    like_count: int = Field(0, ge=0, description="Like count")
    share_count: int = Field(0, ge=0, description="Share count")
    comment_count: int = Field(0, ge=0, description="Comment count")
    rating: Optional[float] = Field(None, ge=0, le=5, description="Average rating")
    
    # SEO metadata
    seo_title: Optional[str] = Field(None, max_length=60, description="SEO title")
    seo_description: Optional[str] = Field(None, max_length=160, description="SEO description")
    canonical_url: Optional[str] = Field(None, description="Canonical URL")
    open_graph_data: Dict[str, str] = Field(default={}, description="Open Graph metadata")
    twitter_card_data: Dict[str, str] = Field(default={}, description="Twitter Card metadata")


class TechnicalMetadata(BaseMetadata):
    """Technical metadata for files and media."""
    
    # File information
    file_name: str = Field(..., description="Original file name")
    file_extension: str = Field(..., description="File extension")
    mime_type: str = Field(..., description="MIME type")
    file_size: int = Field(..., ge=0, description="File size in bytes")
    checksum: str = Field(..., description="File checksum (MD5/SHA256)")
    
    # Media properties
    codec: Optional[str] = Field(None, description="Media codec")
    bitrate: Optional[int] = Field(None, description="Bitrate")
    sample_rate: Optional[int] = Field(None, description="Sample rate")
    channels: Optional[int] = Field(None, description="Number of channels")
    color_space: Optional[str] = Field(None, description="Color space")
    frame_rate: Optional[float] = Field(None, description="Frame rate")
    aspect_ratio: Optional[str] = Field(None, description="Aspect ratio")
    
    # Encoding information
    encoder: Optional[str] = Field(None, description="Encoder used")
    encoding_settings: Dict[str, Any] = Field(default={}, description="Encoding settings")
    compression_ratio: Optional[float] = Field(None, description="Compression ratio")
    
    # Storage information
    storage_location: str = Field(..., description="Storage location")
    storage_tier: str = Field("standard", description="Storage tier")
    backup_locations: List[str] = Field(default=[], description="Backup locations")
    cdn_urls: List[str] = Field(default=[], description="CDN URLs")
    
    # Processing history
    processing_pipeline: List[str] = Field(default=[], description="Processing steps applied")
    transformations: List[Dict[str, Any]] = Field(default=[], description="Applied transformations")
    quality_scores: Dict[str, float] = Field(default={}, description="Quality assessment scores")
    
    # Security
    encryption_algorithm: Optional[str] = Field(None, description="Encryption algorithm")
    encryption_key_id: Optional[str] = Field(None, description="Encryption key ID")
    digital_signature: Optional[str] = Field(None, description="Digital signature")
    watermark_applied: bool = Field(False, description="Whether watermark is applied")


class BusinessMetadata(BaseMetadata):
    """Business-specific metadata."""
    
    # Commercial information
    price: Optional[CurrencyAmountType] = Field(None, description="Content price")
    currency: Optional[str] = Field(None, description="Currency code")
    pricing_model: Optional[str] = Field(None, description="Pricing model")
    license_type: Optional[str] = Field(None, description="License type")
    usage_rights: List[str] = Field(default=[], description="Usage rights")
    
    # Business categorization
    business_unit: Optional[str] = Field(None, description="Business unit")
    department: Optional[str] = Field(None, description="Department")
    project: Optional[str] = Field(None, description="Project name")
    campaign: Optional[str] = Field(None, description="Marketing campaign")
    
    # Revenue tracking
    revenue_generated: Optional[CurrencyAmountType] = Field(None, description="Revenue generated")
    cost_to_produce: Optional[CurrencyAmountType] = Field(None, description="Production cost")
    roi: Optional[float] = Field(None, description="Return on investment")
    
    # Performance metrics
    conversion_rate: Optional[float] = Field(None, ge=0, le=1, description="Conversion rate")
    engagement_rate: Optional[float] = Field(None, ge=0, le=1, description="Engagement rate")
    retention_rate: Optional[float] = Field(None, ge=0, le=1, description="Retention rate")
    
    # Business rules
    approval_required: bool = Field(False, description="Approval required")
    approval_workflow: Optional[str] = Field(None, description="Approval workflow")
    business_rules: List[str] = Field(default=[], description="Applicable business rules")
    compliance_requirements: List[str] = Field(default=[], description="Compliance requirements")


class SystemMetadata(BaseMetadata):
    """System-level metadata."""
    
    # System identification
    system_name: str = Field(..., description="System name")
    system_version: str = Field(..., description="System version")
    environment: str = Field(..., description="Environment (dev/staging/prod)")
    hostname: Optional[str] = Field(None, description="Server hostname")
    
    # Performance data
    processing_time: Optional[float] = Field(None, description="Processing time in milliseconds")
    memory_usage: Optional[float] = Field(None, description="Memory usage in MB")
    cpu_usage: Optional[float] = Field(None, description="CPU usage percentage")
    storage_usage: Optional[float] = Field(None, description="Storage usage in bytes")
    
    # System state
    status: str = Field("active", description="System status")
    health_score: Optional[float] = Field(None, ge=0, le=1, description="Health score")
    error_count: int = Field(0, ge=0, description="Error count")
    warning_count: int = Field(0, ge=0, description="Warning count")
    
    # Configuration
    configuration_hash: Optional[str] = Field(None, description="Configuration hash")
    feature_flags: Dict[str, bool] = Field(default={}, description="Feature flags")
    system_parameters: Dict[str, Any] = Field(default={}, description="System parameters")
    
    # Monitoring
    last_health_check: Optional[datetime] = Field(None, description="Last health check")
    monitoring_enabled: bool = Field(True, description="Monitoring enabled")
    alert_thresholds: Dict[str, float] = Field(default={}, description="Alert thresholds")


class CustomMetadata(BaseMetadata):
    """Custom extensible metadata."""
    
    schema_name: str = Field(..., description="Custom schema name")
    schema_definition: Dict[str, Any] = Field(..., description="Schema definition")
    custom_fields: Dict[str, Any] = Field(..., description="Custom field values")
    
    # Validation
    validation_schema: Optional[Dict[str, Any]] = Field(None, description="JSON schema for validation")
    is_schema_valid: bool = Field(True, description="Whether schema is valid")
    schema_errors: List[str] = Field(default=[], description="Schema validation errors")
    
    # Extensions
    field_definitions: Dict[str, Dict[str, Any]] = Field(default={}, description="Field definitions")
    constraints: List[Dict[str, Any]] = Field(default=[], description="Field constraints")
    relationships: List[Dict[str, Any]] = Field(default=[], description="Field relationships")


# =================== METADATA MANAGEMENT ===================

class MetadataTemplate(UUIDSchema, TimestampSchema):
    """Metadata template for standardization."""
    
    name: str = Field(..., description="Template name")
    description: str = Field(..., description="Template description")
    metadata_type: MetadataType = Field(..., description="Type of metadata")
    
    # Template structure
    required_fields: List[str] = Field(..., description="Required field names")
    optional_fields: List[str] = Field(default=[], description="Optional field names")
    field_definitions: Dict[str, Dict[str, Any]] = Field(..., description="Field definitions")
    default_values: Dict[str, Any] = Field(default={}, description="Default field values")
    
    # Validation rules
    validation_rules: List[Dict[str, Any]] = Field(default=[], description="Validation rules")
    business_rules: List[str] = Field(default=[], description="Business rules")
    
    # Usage information
    usage_count: int = Field(0, ge=0, description="Number of times used")
    is_active: bool = Field(True, description="Whether template is active")
    version: str = Field("1.0.0", description="Template version")


class MetadataSchema(UUIDSchema, TimestampSchema):
    """Metadata schema definition."""
    
    name: str = Field(..., description="Schema name")
    version: str = Field(..., description="Schema version")
    description: str = Field(..., description="Schema description")
    
    # Schema structure
    properties: Dict[str, Dict[str, Any]] = Field(..., description="Schema properties")
    required_properties: List[str] = Field(default=[], description="Required properties")
    additional_properties: bool = Field(True, description="Allow additional properties")
    
    # Inheritance
    extends: Optional[str] = Field(None, description="Parent schema name")
    mixins: List[str] = Field(default=[], description="Mixin schemas")
    
    # Validation
    json_schema: Dict[str, Any] = Field(..., description="JSON Schema definition")
    examples: List[Dict[str, Any]] = Field(default=[], description="Example data")
    
    # Metadata
    author: str = Field(..., description="Schema author")
    tags: List[TagType] = Field(default=[], description="Schema tags")
    is_published: bool = Field(False, description="Whether schema is published")


class MetadataValidationResult(BaseSchema):
    """Result of metadata validation."""
    
    is_valid: bool = Field(..., description="Whether metadata is valid")
    errors: List[str] = Field(default=[], description="Validation errors")
    warnings: List[str] = Field(default=[], description="Validation warnings")
    suggestions: List[str] = Field(default=[], description="Improvement suggestions")
    
    # Detailed results
    field_results: Dict[str, Dict[str, Any]] = Field(default={}, description="Per-field validation results")
    schema_compliance: bool = Field(True, description="Schema compliance")
    business_rule_compliance: bool = Field(True, description="Business rule compliance")
    
    # Performance
    validation_time: float = Field(..., description="Validation time in milliseconds")
    rules_checked: int = Field(..., description="Number of rules checked")


class MetadataSearchQuery(BaseSchema):
    """Query for searching metadata."""
    
    # Basic search
    text_query: Optional[str] = Field(None, description="Text search query")
    metadata_types: List[MetadataType] = Field(default=[], description="Filter by metadata types")
    entity_types: List[str] = Field(default=[], description="Filter by entity types")
    
    # Field-specific search
    field_filters: Dict[str, Any] = Field(default={}, description="Field-specific filters")
    tag_filters: List[TagType] = Field(default=[], description="Tag filters")
    
    # Time-based filters
    created_after: Optional[datetime] = Field(None, description="Created after date")
    created_before: Optional[datetime] = Field(None, description="Created before date")
    modified_after: Optional[datetime] = Field(None, description="Modified after date")
    modified_before: Optional[datetime] = Field(None, description="Modified before date")
    
    # Access control
    access_level: Optional[AccessLevel] = Field(None, description="Filter by access level")
    user_permissions: List[str] = Field(default=[], description="User permissions")
    
    # Pagination and sorting
    page: int = Field(1, ge=1, description="Page number")
    page_size: int = Field(20, ge=1, le=100, description="Items per page")
    sort_by: str = Field("created_at", description="Sort field")
    sort_direction: str = Field("desc", pattern="^(asc|desc)$", description="Sort direction")


class MetadataStatistics(BaseSchema):
    """Metadata usage statistics."""
    
    total_metadata_records: int = Field(..., description="Total metadata records")
    metadata_by_type: Dict[str, int] = Field(..., description="Metadata count by type")
    metadata_by_entity_type: Dict[str, int] = Field(..., description="Metadata count by entity type")
    
    # Usage statistics
    most_used_fields: List[Dict[str, Any]] = Field(default=[], description="Most used metadata fields")
    most_used_templates: List[Dict[str, Any]] = Field(default=[], description="Most used templates")
    
    # Quality statistics
    validation_success_rate: float = Field(..., description="Validation success rate")
    completeness_score: float = Field(..., description="Average completeness score")
    consistency_score: float = Field(..., description="Average consistency score")
    
    # Performance statistics
    average_processing_time: float = Field(..., description="Average processing time")
    storage_usage: float = Field(..., description="Storage usage in bytes")
    
    # Trends
    growth_rate: float = Field(..., description="Metadata growth rate")
    usage_trends: Dict[str, List[float]] = Field(default={}, description="Usage trends over time")