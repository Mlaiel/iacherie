"""Content Management Schemas for IA Influencer Agent Platform
Professional multi-format content upload, processing, and management schemas

Business Logic Flow: Upload → AI Processing → Protection → SEO → Distribution → Monetization

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

🚨 INTELLECTUAL PROPERTY WARNING: Unauthorized use prohibited.
Contact: mlaiel@live.de for licensing and permissions.
"""

from datetime import datetime
from decimal import Decimal
from typing import Any, Dict, List, Optional, Set, Union
from uuid import UUID

from pydantic import Field, HttpUrl, validator

from .base import BaseSchema, TimestampSchema, UUIDSchema, AuditSchema, FileUploadSchema


class ContentUpload(BaseSchema):
    """
Professional multi-format content upload schema."""
    
    creator_id: UUID = Field(description="Content creator ID")
    title: str = Field(min_length=1, max_length=200, description="Content title")
    description: Optional[str] = Field(None, max_length=5000, description="Content description")
    content_type: str = Field(description="Content type (audio, video, image, text, multimodal)")
    media_format: str = Field(description="Media format/MIME type")
    
    # File information
    filename: str = Field(description="Original filename")
    file_size: int = Field(gt=0, description="File size in bytes")
    file_checksum: str = Field(description="File integrity checksum")
    upload_method: str = Field(default="direct", description="Upload method (direct, url, bulk)")
    
    # Content classification
    genres: List[str] = Field(default_factory=list, description="Content genres/categories")
    tags: List[str] = Field(default_factory=list, description="Content tags")
    language: str = Field(default="en", description="Content language")
    mood: Optional[str] = Field(None, description="Content mood/emotion")
    
    # Rights and ownership
    copyright_status: str = Field(default="original", description="Copyright status")
    ownership_percentage: float = Field(default=100.0, ge=0.0, le=100.0)
    collaborators: List[UUID] = Field(default_factory=list, description="Collaborator IDs")
    
    # Privacy and distribution settings
    privacy_level: str = Field(default="private", description="Content privacy level")
    auto_protection: bool = Field(default=True, description="Enable automatic protection")
    auto_seo_optimization: bool = Field(default=True, description="Enable SEO optimization")
    distribution_channels: List[str] = Field(default_factory=list)
    
    # Metadata
    custom_metadata: Dict[str, Any] = Field(default_factory=dict)
    source_platform: Optional[str] = Field(None, description="Original platform")
    external_id: Optional[str] = Field(None, description="External platform ID")
    
    @validator('content_type')
    def validate_content_type(cls, v):
        """Validate content type."""
        allowed_types = {
            'audio', 'video', 'image', 'text', 'multimodal',
            'music', 'podcast', 'document', 'animation'
        }
        if v.lower() not in allowed_types:
            raise ValueError(f'Content type must be one of: {", ".join(allowed_types)}')
        return v.lower()
    
    @validator('privacy_level')
    def validate_privacy_level(cls, v):
        """Validate privacy level."""
        allowed_levels = {'public', 'unlisted', 'private', 'collaborators_only'}
        if v not in allowed_levels:
            raise ValueError(f'Privacy level must be one of: {", ".join(allowed_levels)}')
        return v


class ContentUpdate(BaseSchema):
    """Schema for updating content information."""
    
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=5000)
    genres: Optional[List[str]] = None
    tags: Optional[List[str]] = None
    language: Optional[str] = None
    mood: Optional[str] = None
    privacy_level: Optional[str] = None
    collaborators: Optional[List[UUID]] = None
    custom_metadata: Optional[Dict[str, Any]] = None


class ContentOut(UUIDSchema, TimestampSchema):
    """
Public content information schema."""
    
    creator_id: UUID
    title: str
    description: Optional[str]
    content_type: str
    media_format: str
    
    # File information (public)
    filename: str
    file_size: int
    duration_seconds: Optional[float] = Field(None, description="Content duration")
    dimensions: Optional[Dict[str, int]] = Field(None, description="Image/video dimensions")
    
    # Content classification
    genres: List[str]
    tags: List[str]
    language: str
    mood: Optional[str]
    
    # Status and metrics
    processing_status: str = Field(default="pending")
    is_protected: bool = Field(default=False)
    is_seo_optimized: bool = Field(default=False)
    
    # Public URLs
    public_url: Optional[HttpUrl] = None
    thumbnail_url: Optional[HttpUrl] = None
    preview_url: Optional[HttpUrl] = None
    
    # Statistics
    view_count: int = Field(default=0, ge=0)
    like_count: int = Field(default=0, ge=0)
    comment_count: int = Field(default=0, ge=0)
    share_count: int = Field(default=0, ge=0)
    download_count: int = Field(default=0, ge=0)
    
    # Revenue
    total_revenue: Decimal = Field(default=Decimal('0.00'), ge=0)
    monetization_enabled: bool = Field(default=False)
    
    # Rights status
    copyright_status: str
    protection_level: str = Field(default="none")
    violation_count: int = Field(default=0, ge=0)
    
    @property
    def engagement_rate(self) -> float:
        """Calculate engagement rate."""
        if self.view_count == 0:
            return 0.0
        total_engagement = self.like_count + self.comment_count + self.share_count
        return min(1.0, total_engagement / self.view_count)


class ContentMetadata(UUIDSchema, TimestampSchema):
    """
Extended content metadata schema."""
    
    content_id: UUID
    
    # Technical metadata
    technical_metadata: Dict[str, Any] = Field(default_factory=dict)
    processing_metadata: Dict[str, Any] = Field(default_factory=dict)
    ai_analysis_metadata: Dict[str, Any] = Field(default_factory=dict)
    
    # SEO metadata
    seo_title: Optional[str] = Field(None, max_length=60)
    seo_description: Optional[str] = Field(None, max_length=160)
    seo_keywords: List[str] = Field(default_factory=list)
    canonical_url: Optional[HttpUrl] = None
    alt_text: Optional[str] = Field(None, description="Alternative text for accessibility")
    
    # Social media metadata
    og_title: Optional[str] = Field(None, description="Open Graph title")
    og_description: Optional[str] = Field(None, description="Open Graph description")
    og_image: Optional[HttpUrl] = Field(None, description="Open Graph image")
    twitter_card_type: Optional[str] = Field(None, description="Twitter card type")
    
    # Content analysis
    quality_score: float = Field(default=0.0, ge=0.0, le=1.0)
    sentiment_score: Optional[float] = Field(None, ge=-1.0, le=1.0)
    complexity_score: Optional[float] = Field(None, ge=0.0, le=1.0)
    uniqueness_score: Optional[float] = Field(None, ge=0.0, le=1.0)
    
    # Geographic and demographic data
    target_audience: Dict[str, Any] = Field(default_factory=dict)
    geographic_relevance: List[str] = Field(default_factory=list)
    demographic_tags: List[str] = Field(default_factory=list)


class ContentVersion(UUIDSchema, TimestampSchema, AuditSchema):
    """Content version control schema."""
    
    content_id: UUID
    version_number: str = Field(description="Semantic version number")
    version_type: str = Field(description="Version type (major, minor, patch, revision)")
    
    # Version details
    change_summary: str = Field(description="Summary of changes")
    change_log: List[Dict[str, str]] = Field(default_factory=list)
    file_diff: Optional[str] = Field(None, description="File difference information")
    
    # Version status
    is_current: bool = Field(default=False)
    is_published: bool = Field(default=False)
    approval_status: str = Field(default="pending")
    approved_by: Optional[UUID] = None
    approved_at: Optional[datetime] = None
    
    # File information for this version
    file_path: str = Field(description="File storage path")
    file_size: int = Field(ge=0)
    file_checksum: str = Field(description="File checksum")
    
    # Metadata changes
    metadata_changes: Dict[str, Any] = Field(default_factory=dict)
    
    @validator('version_type')
    def validate_version_type(cls, v):
        """Validate version type."""
        allowed_types = {'major', 'minor', 'patch', 'revision', 'hotfix'}
        if v not in allowed_types:
            raise ValueError(f'Version type must be one of: {", ".join(allowed_types)}')
        return v


class ContentTag(UUIDSchema, TimestampSchema):
    """Content tagging system schema."""
    
    name: str = Field(min_length=1, max_length=50, description="Tag name")
    category: str = Field(description="Tag category")
    description: Optional[str] = Field(None, max_length=200)
    
    # Tag properties
    is_system_tag: bool = Field(default=False)
    is_trending: bool = Field(default=False)
    usage_count: int = Field(default=0, ge=0)
    relevance_score: float = Field(default=0.0, ge=0.0, le=1.0)
    
    # Relationships
    parent_tag_id: Optional[UUID] = None
    related_tags: List[UUID] = Field(default_factory=list)
    
    # Metadata
    color: Optional[str] = Field(None, regex="^#[0-9A-Fa-f]{6}$")
    icon: Optional[str] = Field(None, description="Tag icon identifier")
    
    @validator('name')
    def validate_tag_name(cls, v):
        """Validate tag name format."""
        # Remove extra whitespace and convert to lowercase
        return v.strip().lower()


class ContentSearch(BaseSchema):
    """
Advanced content search schema."""
    
    query: Optional[str] = Field(None, description="Search query string")
    creator_id: Optional[UUID] = Field(None, description="Filter by creator")
    content_types: Optional[List[str]] = Field(None, description="Filter by content types")
    genres: Optional[List[str]] = Field(None, description="Filter by genres")
    tags: Optional[List[str]] = Field(None, description="Filter by tags")
    language: Optional[str] = Field(None, description="Filter by language")
    
    # Date filters
    created_after: Optional[datetime] = None
    created_before: Optional[datetime] = None
    updated_after: Optional[datetime] = None
    updated_before: Optional[datetime] = None
    
    # Quality and status filters
    min_quality_score: Optional[float] = Field(None, ge=0.0, le=1.0)
    processing_status: Optional[str] = None
    privacy_level: Optional[str] = None
    is_protected: Optional[bool] = None
    monetization_enabled: Optional[bool] = None
    
    # Popularity filters
    min_view_count: Optional[int] = Field(None, ge=0)
    min_like_count: Optional[int] = Field(None, ge=0)
    min_engagement_rate: Optional[float] = Field(None, ge=0.0, le=1.0)
    
    # File properties
    min_file_size: Optional[int] = Field(None, ge=0)
    max_file_size: Optional[int] = Field(None, ge=0)
    min_duration: Optional[float] = Field(None, ge=0)
    max_duration: Optional[float] = Field(None, ge=0)
    
    # Sorting and pagination
    sort_by: str = Field(default="created_at", description="Sort field")
    sort_order: str = Field(default="desc", regex="^(asc|desc)$")
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=20, ge=1, le=100)
    
    # Advanced search options
    include_deleted: bool = Field(default=False)
    include_private: bool = Field(default=False)
    search_in_description: bool = Field(default=True)
    search_in_tags: bool = Field(default=True)
    search_in_metadata: bool = Field(default=False)
    fuzzy_search: bool = Field(default=True)


class ContentBulkOperation(BaseSchema):
    """Bulk content operations schema."""
    
    content_ids: List[UUID] = Field(description="List of content IDs to process")
    operation_type: str = Field(description="Type of bulk operation")
    parameters: Dict[str, Any] = Field(default_factory=dict, description="Operation parameters")
    
    # Processing options
    batch_size: int = Field(default=10, ge=1, le=100, description="Processing batch size")
    parallel_processing: bool = Field(default=True, description="Enable parallel processing")
    continue_on_error: bool = Field(default=False, description="Continue processing on individual errors")
    
    @validator('operation_type')
    def validate_operation_type(cls, v):
        """Validate bulk operation type."""
        allowed_operations = {
            'update_metadata', 'change_privacy', 'add_tags', 'remove_tags',
            'enable_protection', 'disable_protection', 'export', 'delete',
            'optimize_seo', 'distribute', 'monetize'
        }
        if v not in allowed_operations:
            raise ValueError(f'Operation type must be one of: {", ".join(allowed_operations)}')
        return v


class ContentAnalysis(UUIDSchema, TimestampSchema):
    """AI content analysis results schema."""
    
    content_id: UUID
    analysis_type: str = Field(description="Type of analysis performed")
    analysis_version: str = Field(description="Analysis algorithm version")
    
    # Analysis results
    analysis_results: Dict[str, Any] = Field(default_factory=dict)
    confidence_score: float = Field(ge=0.0, le=1.0, description="Analysis confidence")
    processing_time_seconds: float = Field(ge=0.0, description="Processing time")
    
    # Content insights
    content_insights: Dict[str, Any] = Field(default_factory=dict)
    recommendations: List[Dict[str, str]] = Field(default_factory=list)
    potential_issues: List[Dict[str, str]] = Field(default_factory=list)
    
    # Quality metrics
    quality_metrics: Dict[str, float] = Field(default_factory=dict)
    performance_predictions: Dict[str, float] = Field(default_factory=dict)
    
    @validator('analysis_type')
    def validate_analysis_type(cls, v):
        """Validate analysis type."""
        allowed_types = {
            'content_classification', 'quality_assessment', 'sentiment_analysis',
            'copyright_detection', 'seo_analysis', 'performance_prediction',
            'audience_targeting', 'monetization_potential'
        }
        if v not in allowed_types:
            raise ValueError(f'Analysis type must be one of: {", ".join(allowed_types)}')
        return v


class ContentExport(BaseSchema):
    """Content export configuration schema."""
    
    content_ids: List[UUID] = Field(description="Content to export")
    export_format: str = Field(description="Export format")
    export_quality: str = Field(default="original", description="Export quality")
    include_metadata: bool = Field(default=True, description="Include metadata in export")
    include_analytics: bool = Field(default=False, description="Include analytics data")
    
    # Export customization
    watermark_enabled: bool = Field(default=False, description="Add watermark to export")
    compression_enabled: bool = Field(default=False, description="Enable compression")
    archive_format: Optional[str] = Field(None, description="Archive format for multiple files")
    
    @validator('export_format')
    def validate_export_format(cls, v):
        """Validate export format."""
        allowed_formats = {
            'original', 'mp3', 'wav', 'flac', 'mp4', 'webm', 'jpg', 'png', 
            'pdf', 'json', 'xml', 'csv'
        }
        if v not in allowed_formats:
            raise ValueError(f'Export format must be one of: {", ".join(allowed_formats)}')
        return v
