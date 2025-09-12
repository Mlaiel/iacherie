"""{{service_name}} Content Service for Ainflue Platform
{{service_description}}

Author: {{author_name}} ({{author_email}})
Created: {{created_date}}
"""

import logging
import asyncio
from typing import Dict, Any, Optional, List, Union, BinaryIO
from datetime import datetime, timedelta
from enum import Enum
import uuid
import json
import mimetypes
from pathlib import Path

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete, and_, or_, func
from pydantic import BaseModel, Field, validator
import aiofiles
import aioredis
from PIL import Image
import cv2
import librosa
import soundfile as sf

from core.base_service import BaseService
from core.config import get_settings
from core.database import get_async_session
from core.exceptions import ServiceException, ValidationError, AuthorizationError
from models.content import Content, ContentMetadata, ContentStats, ContentTag
from models.creator import Creator
from services.ai_service import AIService
from services.storage_service import StorageService
from services.analytics_service import AnalyticsService
from services.moderation_service import ModerationService
from utils.content_processing import process_image, process_audio, process_video
from utils.metadata_extraction import extract_metadata
from monitoring.content_metrics import ContentMetricsCollector

logger = logging.getLogger(__name__)
settings = get_settings()


class ContentType(Enum):
    """Types of content"""
    IMAGE = "image"
    AUDIO = "audio"
    VIDEO = "video"
    TEXT = "text"
    DOCUMENT = "document"
    LIVESTREAM = "livestream"
    PODCAST = "podcast"
    BLOG_POST = "blog_post"
    STORY = "story"
    REEL = "reel"


class ContentStatus(Enum):
    """Content publication status"""
    DRAFT = "draft"
    PENDING_REVIEW = "pending_review"
    PUBLISHED = "published"
    ARCHIVED = "archived"
    REMOVED = "removed"
    FLAGGED = "flagged"
    PROCESSING = "processing"


class PrivacyLevel(Enum):
    """Content privacy levels"""
    PUBLIC = "public"
    UNLISTED = "unlisted"
    PRIVATE = "private"
    FOLLOWERS_ONLY = "followers_only"
    PREMIUM_ONLY = "premium_only"


class ContentQuality(Enum):
    """Content quality levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    ULTRA_HD = "ultra_hd"
    LOSSLESS = "lossless"


class ContentUploadRequest(BaseModel):
    """Content upload request model"""
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=5000)
    content_type: ContentType
    privacy_level: PrivacyLevel = PrivacyLevel.PUBLIC
    tags: List[str] = Field(default_factory=list, max_items=20)
    category: Optional[str] = None
    language: str = "en"
    allow_comments: bool = True
    allow_downloads: bool = False
    monetization_enabled: bool = False
    schedule_publish: Optional[datetime] = None
    thumbnail_timestamp: Optional[float] = None  # For video thumbnail
    custom_metadata: Dict[str, Any] = Field(default_factory=dict)

    @validator('tags')
    def validate_tags(cls, v):
        return [tag.strip().lower() for tag in v if tag.strip()]


class ContentUpdateRequest(BaseModel):
    """Content update request model"""
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=5000)
    privacy_level: Optional[PrivacyLevel] = None
    tags: Optional[List[str]] = Field(None, max_items=20)
    category: Optional[str] = None
    allow_comments: Optional[bool] = None
    allow_downloads: Optional[bool] = None
    monetization_enabled: Optional[bool] = None
    custom_metadata: Optional[Dict[str, Any]] = None


class ContentResponse(BaseModel):
    """Content response model"""
    content_id: str
    title: str
    description: Optional[str]
    content_type: ContentType
    status: ContentStatus
    privacy_level: PrivacyLevel
    creator_id: str
    creator_username: str
    file_url: str
    thumbnail_url: Optional[str] = None
    preview_url: Optional[str] = None
    duration: Optional[float] = None  # For audio/video
    file_size: int
    quality: ContentQuality
    tags: List[str] = Field(default_factory=list)
    category: Optional[str] = None
    language: str
    view_count: int = 0
    like_count: int = 0
    comment_count: int = 0
    share_count: int = 0
    download_count: int = 0
    upload_date: datetime
    publish_date: Optional[datetime] = None
    last_modified: datetime
    allow_comments: bool = True
    allow_downloads: bool = False
    monetization_enabled: bool = False
    ai_analysis: Optional[Dict[str, Any]] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)


class ContentSearchRequest(BaseModel):
    """Content search request model"""
    query: Optional[str] = None
    content_types: List[ContentType] = Field(default_factory=list)
    creator_ids: List[str] = Field(default_factory=list)
    tags: List[str] = Field(default_factory=list)
    categories: List[str] = Field(default_factory=list)
    language: Optional[str] = None
    privacy_levels: List[PrivacyLevel] = Field(default_factory=list)
    min_duration: Optional[float] = None
    max_duration: Optional[float] = None
    min_views: Optional[int] = None
    max_views: Optional[int] = None
    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None
    sort_by: str = "relevance"  # relevance, upload_date, views, likes, trending
    sort_order: str = "desc"  # asc, desc
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=20, ge=1, le=100)


class ContentConfig(BaseModel):
    """Content service configuration"""
    enable_ai_analysis: bool = True
    enable_auto_moderation: bool = True
    enable_content_compression: bool = True
    enable_thumbnail_generation: bool = True
    enable_preview_generation: bool = True
    max_file_size: int = 1024 * 1024 * 1024  # 1GB
    supported_image_formats: List[str] = Field(default_factory=lambda: ["jpg", "jpeg", "png", "gif", "webp"])
    supported_audio_formats: List[str] = Field(default_factory=lambda: ["mp3", "wav", "flac", "aac", "ogg"])
    supported_video_formats: List[str] = Field(default_factory=lambda: ["mp4", "avi", "mov", "mkv", "webm"])
    thumbnail_size: tuple = (320, 240)
    preview_duration: int = 30  # seconds
    cache_ttl_seconds: int = 3600


class {{service_class_name}}(BaseService):
    """
    Advanced content service for Ainflue platform.
    
    Features:
    - Multi-format content upload and processing
    - AI-powered content analysis and tagging
    - Content moderation and quality control
    - Thumbnail and preview generation
    - Content compression and optimization
    - Advanced search and discovery
    - Privacy and access control
    - Analytics and performance tracking
    - Content monetization support
    - Batch processing capabilities
    - Real-time content streaming
    - Content versioning and history
    """
    
    def __init__(
        self,
        name: str = "{{service_name}}",
        config: Optional[ContentConfig] = None,
        **kwargs
    ):
        super().__init__(name=name, **kwargs)
        self.config = config or ContentConfig()
        
        # Initialize related services
        self.ai_service = AIService()
        self.storage_service = StorageService()
        self.analytics_service = AnalyticsService()
        self.moderation_service = ModerationService()
        
        # Initialize metrics collector
        self.metrics = ContentMetricsCollector()
        
        # Redis client for caching
        self.redis_client = None
        
        logger.info(f"Content service '{name}' initialized successfully")

    async def initialize(self) -> None:
        """Initialize the content service"""
        try:
            # Initialize Redis for caching
            self.redis_client = await aioredis.from_url(
                settings.redis_url,
                encoding="utf-8",
                decode_responses=True
            )
            
            # Initialize storage service
            await self.storage_service.initialize()
            
            logger.info("Content service initialized successfully")
            
        except Exception as e:
            logger.error(f"Content service initialization failed: {str(e)}")
            raise ServiceException(f"Initialization failed: {str(e)}")

    async def upload_content(
        self,
        file_data: BinaryIO,
        upload_request: ContentUploadRequest,
        creator_id: str,
        db: AsyncSession = None
    ) -> ContentResponse:
        """
        Upload and process content.
        
        Args:
            file_data: Content file data
            upload_request: Upload request parameters
            creator_id: ID of creator uploading content
            db: Database session
            
        Returns:
            ContentResponse with uploaded content data
        """
        if not db:
            db = await get_async_session()
        
        try:
            # Validate file and request
            await self._validate_upload_request(file_data, upload_request, creator_id, db)
            
            # Generate content ID
            content_id = str(uuid.uuid4())
            
            # Read file data
            file_data.seek(0)
            content_bytes = file_data.read()
            file_size = len(content_bytes)
            
            # Detect file format and validate
            file_format, mime_type = await self._detect_file_format(content_bytes)
            await self._validate_file_format(file_format, upload_request.content_type)
            
            # Store original file
            file_path = await self.storage_service.store_file(
                content_bytes,
                f"content/{creator_id}/{content_id}/original.{file_format}",
                mime_type
            )
            
            # Extract metadata
            extracted_metadata = await self._extract_content_metadata(
                content_bytes, upload_request.content_type, file_format
            )
            
            # Process content (compress, optimize, etc.)
            processed_files = await self._process_content(
                content_bytes, upload_request.content_type, content_id, creator_id
            )
            
            # Generate thumbnails and previews
            media_assets = await self._generate_media_assets(
                content_bytes, upload_request.content_type, content_id, creator_id,
                thumbnail_timestamp=upload_request.thumbnail_timestamp
            )
            
            # AI analysis if enabled
            ai_analysis = None
            if self.config.enable_ai_analysis:
                ai_analysis = await self._perform_ai_analysis(
                    content_bytes, upload_request.content_type, upload_request.title,
                    upload_request.description
                )
            
            # Content moderation if enabled
            moderation_result = None
            if self.config.enable_auto_moderation:
                moderation_result = await self._moderate_content(
                    content_bytes, upload_request, ai_analysis
                )
            
            # Determine initial status
            initial_status = ContentStatus.PROCESSING
            if moderation_result and moderation_result.get('requires_review'):
                initial_status = ContentStatus.PENDING_REVIEW
            elif upload_request.schedule_publish:
                initial_status = ContentStatus.DRAFT
            else:
                initial_status = ContentStatus.PUBLISHED
            
            # Create content record
            content = Content(
                content_id=content_id,
                creator_id=creator_id,
                title=upload_request.title,
                description=upload_request.description,
                content_type=upload_request.content_type,
                status=initial_status,
                privacy_level=upload_request.privacy_level,
                file_path=file_path,
                file_size=file_size,
                file_format=file_format,
                mime_type=mime_type,
                duration=extracted_metadata.get('duration'),
                quality=self._determine_quality(extracted_metadata),
                category=upload_request.category,
                language=upload_request.language,
                allow_comments=upload_request.allow_comments,
                allow_downloads=upload_request.allow_downloads,
                monetization_enabled=upload_request.monetization_enabled,
                upload_date=datetime.utcnow(),
                publish_date=upload_request.schedule_publish,
                thumbnail_url=media_assets.get('thumbnail_url'),
                preview_url=media_assets.get('preview_url')
            )
            
            db.add(content)
            
            # Create content metadata
            metadata = ContentMetadata(
                content_id=content_id,
                extracted_metadata=extracted_metadata,
                ai_analysis=ai_analysis,
                moderation_result=moderation_result,
                processed_files=processed_files,
                custom_metadata=upload_request.custom_metadata
            )
            
            db.add(metadata)
            
            # Create content stats
            stats = ContentStats(
                content_id=content_id,
                view_count=0,
                like_count=0,
                comment_count=0,
                share_count=0,
                download_count=0
            )
            
            db.add(stats)
            
            # Add tags
            for tag_name in upload_request.tags:
                tag = ContentTag(
                    content_id=content_id,
                    tag_name=tag_name
                )
                db.add(tag)
            
            await db.commit()
            
            # Convert to response
            content_response = await self._content_to_response(content, metadata, stats, upload_request.tags)
            
            # Record metrics
            await self.metrics.record_content_uploaded(
                content_type=upload_request.content_type.value,
                file_size=file_size,
                creator_id=creator_id,
                processing_time=0  # Would be calculated
            )
            
            # Schedule post-processing tasks
            await self._schedule_post_processing(content_id, creator_id)
            
            return content_response
            
        except Exception as e:
            await db.rollback()
            logger.error(f"Content upload failed: {str(e)}")
            raise ServiceException(f"Upload failed: {str(e)}")

    async def get_content(
        self,
        content_id: str,
        requester_id: Optional[str] = None,
        track_view: bool = True,
        db: AsyncSession = None
    ) -> Optional[ContentResponse]:
        """
        Get content by ID.
        
        Args:
            content_id: Content identifier
            requester_id: ID of user requesting content
            track_view: Whether to track this as a view
            db: Database session
            
        Returns:
            ContentResponse if found and accessible
        """
        if not db:
            db = await get_async_session()
        
        try:
            # Check cache first
            cache_key = f"content:{content_id}"
            cached_data = await self._get_from_cache(cache_key)
            
            if cached_data:
                content_response = ContentResponse(**cached_data)
                
                # Check access permissions
                if await self._can_access_content(content_response, requester_id, db):
                    if track_view:
                        await self._track_content_view(content_id, requester_id, db)
                    return content_response
                else:
                    raise AuthorizationError("Access denied to content")
            
            # Query database
            content_query = select(Content).where(Content.content_id == content_id)
            content_result = await db.execute(content_query)
            content = content_result.scalar_one_or_none()
            
            if not content:
                return None
            
            # Get metadata
            metadata_query = select(ContentMetadata).where(ContentMetadata.content_id == content_id)
            metadata_result = await db.execute(metadata_query)
            metadata = metadata_result.scalar_one_or_none()
            
            # Get stats
            stats_query = select(ContentStats).where(ContentStats.content_id == content_id)
            stats_result = await db.execute(stats_query)
            stats = stats_result.scalar_one_or_none()
            
            # Get tags
            tags_query = select(ContentTag.tag_name).where(ContentTag.content_id == content_id)
            tags_result = await db.execute(tags_query)
            tags = [row[0] for row in tags_result.fetchall()]
            
            # Convert to response
            content_response = await self._content_to_response(content, metadata, stats, tags)
            
            # Check access permissions
            if not await self._can_access_content(content_response, requester_id, db):
                raise AuthorizationError("Access denied to content")
            
            # Cache the result
            await self._set_cache(cache_key, content_response.dict())
            
            # Track view
            if track_view:
                await self._track_content_view(content_id, requester_id, db)
            
            return content_response
            
        except Exception as e:
            logger.error(f"Failed to get content {content_id}: {str(e)}")
            if isinstance(e, AuthorizationError):
                raise
            raise ServiceException(f"Failed to get content: {str(e)}")

    async def update_content(
        self,
        content_id: str,
        updates: ContentUpdateRequest,
        updater_id: str,
        db: AsyncSession = None
    ) -> ContentResponse:
        """
        Update content information.
        
        Args:
            content_id: Content identifier
            updates: Updates to apply
            updater_id: ID of user making updates
            db: Database session
            
        Returns:
            Updated ContentResponse
        """
        if not db:
            db = await get_async_session()
        
        try:
            # Get current content
            content = await self._get_content_by_id(content_id, db)
            if not content:
                raise ValidationError("Content not found")
            
            # Check permissions
            if not await self._can_modify_content(content, updater_id, db):
                raise AuthorizationError("Not authorized to modify this content")
            
            # Prepare updates
            content_updates = {}
            
            if updates.title is not None:
                content_updates['title'] = updates.title
            if updates.description is not None:
                content_updates['description'] = updates.description
            if updates.privacy_level is not None:
                content_updates['privacy_level'] = updates.privacy_level
            if updates.category is not None:
                content_updates['category'] = updates.category
            if updates.allow_comments is not None:
                content_updates['allow_comments'] = updates.allow_comments
            if updates.allow_downloads is not None:
                content_updates['allow_downloads'] = updates.allow_downloads
            if updates.monetization_enabled is not None:
                content_updates['monetization_enabled'] = updates.monetization_enabled
            
            if content_updates:
                content_updates['last_modified'] = datetime.utcnow()
                
                await db.execute(
                    update(Content)
                    .where(Content.content_id == content_id)
                    .values(**content_updates)
                )
            
            # Update tags if provided
            if updates.tags is not None:
                # Remove existing tags
                await db.execute(
                    delete(ContentTag).where(ContentTag.content_id == content_id)
                )
                
                # Add new tags
                for tag_name in updates.tags:
                    tag = ContentTag(content_id=content_id, tag_name=tag_name)
                    db.add(tag)
            
            # Update custom metadata if provided
            if updates.custom_metadata is not None:
                await db.execute(
                    update(ContentMetadata)
                    .where(ContentMetadata.content_id == content_id)
                    .values(custom_metadata=updates.custom_metadata)
                )
            
            await db.commit()
            
            # Clear cache
            await self._clear_content_cache(content_id)
            
            # Get updated content
            updated_content = await self.get_content(content_id, updater_id, track_view=False, db=db)
            
            # Record metrics
            await self.metrics.record_content_updated(
                content_id=content_id,
                fields_updated=list(content_updates.keys()),
                updater_id=updater_id
            )
            
            return updated_content
            
        except Exception as e:
            await db.rollback()
            logger.error(f"Failed to update content {content_id}: {str(e)}")
            raise ServiceException(f"Update failed: {str(e)}")

    async def search_content(
        self,
        search_request: ContentSearchRequest,
        requester_id: Optional[str] = None,
        db: AsyncSession = None
    ) -> Dict[str, Any]:
        """
        Search for content based on criteria.
        
        Args:
            search_request: Search parameters
            requester_id: ID of user making the request
            db: Database session
            
        Returns:
            Search results with pagination
        """
        if not db:
            db = await get_async_session()
        
        try:
            # Build base query
            query = (
                select(Content, ContentStats, ContentTag.tag_name)
                .join(ContentStats, isouter=True)
                .join(ContentTag, isouter=True)
                .where(Content.status == ContentStatus.PUBLISHED)
            )
            
            # Apply privacy filters
            privacy_conditions = [Content.privacy_level == PrivacyLevel.PUBLIC]
            if requester_id:
                privacy_conditions.extend([
                    Content.privacy_level == PrivacyLevel.UNLISTED,
                    and_(
                        Content.privacy_level == PrivacyLevel.PRIVATE,
                        Content.creator_id == requester_id
                    )
                ])
            
            query = query.where(or_(*privacy_conditions))
            
            # Apply filters
            conditions = []
            
            # Text search
            if search_request.query:
                text_conditions = [
                    Content.title.ilike(f"%{search_request.query}%"),
                    Content.description.ilike(f"%{search_request.query}%"),
                    ContentTag.tag_name.ilike(f"%{search_request.query}%")
                ]
                conditions.append(or_(*text_conditions))
            
            # Content types
            if search_request.content_types:
                conditions.append(Content.content_type.in_([ct.value for ct in search_request.content_types]))
            
            # Creator IDs
            if search_request.creator_ids:
                conditions.append(Content.creator_id.in_(search_request.creator_ids))
            
            # Tags
            if search_request.tags:
                conditions.append(ContentTag.tag_name.in_(search_request.tags))
            
            # Categories
            if search_request.categories:
                conditions.append(Content.category.in_(search_request.categories))
            
            # Language
            if search_request.language:
                conditions.append(Content.language == search_request.language)
            
            # Duration range
            if search_request.min_duration is not None:
                conditions.append(Content.duration >= search_request.min_duration)
            
            if search_request.max_duration is not None:
                conditions.append(Content.duration <= search_request.max_duration)
            
            # View count range
            if search_request.min_views is not None:
                conditions.append(ContentStats.view_count >= search_request.min_views)
            
            if search_request.max_views is not None:
                conditions.append(ContentStats.view_count <= search_request.max_views)
            
            # Date range
            if search_request.date_from:
                conditions.append(Content.publish_date >= search_request.date_from)
            
            if search_request.date_to:
                conditions.append(Content.publish_date <= search_request.date_to)
            
            # Apply all conditions
            if conditions:
                query = query.where(and_(*conditions))
            
            # Apply sorting
            if search_request.sort_by == "upload_date":
                order_col = Content.upload_date
            elif search_request.sort_by == "views":
                order_col = ContentStats.view_count
            elif search_request.sort_by == "likes":
                order_col = ContentStats.like_count
            elif search_request.sort_by == "trending":
                # Trending algorithm (simplified)
                order_col = (ContentStats.view_count + ContentStats.like_count * 10)
            else:  # relevance
                order_col = Content.upload_date
            
            if search_request.sort_order == "asc":
                query = query.order_by(order_col.asc())
            else:
                query = query.order_by(order_col.desc())
            
            # Group by content to avoid duplicates from joins
            query = query.group_by(Content.content_id, ContentStats.content_id)
            
            # Count total results
            count_query = select(func.count(func.distinct(Content.content_id))).select_from(query.subquery())
            total_count = (await db.execute(count_query)).scalar()
            
            # Apply pagination
            offset = (search_request.page - 1) * search_request.page_size
            query = query.offset(offset).limit(search_request.page_size)
            
            # Execute query
            result = await db.execute(query)
            content_rows = result.fetchall()
            
            # Process results and get tags for each content
            content_responses = []
            content_ids = list(set([row.Content.content_id for row in content_rows]))
            
            for content_id in content_ids:
                content_data = next((row for row in content_rows if row.Content.content_id == content_id), None)
                if content_data:
                    # Get all tags for this content
                    tags_query = select(ContentTag.tag_name).where(ContentTag.content_id == content_id)
                    tags_result = await db.execute(tags_query)
                    tags = [row[0] for row in tags_result.fetchall()]
                    
                    # Get metadata
                    metadata_query = select(ContentMetadata).where(ContentMetadata.content_id == content_id)
                    metadata_result = await db.execute(metadata_query)
                    metadata = metadata_result.scalar_one_or_none()
                    
                    response = await self._content_to_response(
                        content_data.Content, metadata, content_data.ContentStats, tags
                    )
                    content_responses.append(response)
            
            # Calculate pagination info
            total_pages = (total_count + search_request.page_size - 1) // search_request.page_size
            
            search_results = {
                'content': content_responses,
                'pagination': {
                    'current_page': search_request.page,
                    'page_size': search_request.page_size,
                    'total_pages': total_pages,
                    'total_count': total_count,
                    'has_next': search_request.page < total_pages,
                    'has_prev': search_request.page > 1
                },
                'search_metadata': {
                    'query': search_request.query,
                    'filters_applied': len([f for f in [
                        search_request.content_types,
                        search_request.creator_ids,
                        search_request.tags,
                        search_request.categories
                    ] if f]),
                    'sort_by': search_request.sort_by,
                    'sort_order': search_request.sort_order
                }
            }
            
            # Record search metrics
            await self.metrics.record_content_search(
                query=search_request.query,
                filters_count=search_results['search_metadata']['filters_applied'],
                results_count=len(content_responses),
                requester_id=requester_id
            )
            
            return search_results
            
        except Exception as e:
            logger.error(f"Content search failed: {str(e)}")
            raise ServiceException(f"Search failed: {str(e)}")

    async def delete_content(
        self,
        content_id: str,
        deleter_id: str,
        hard_delete: bool = False,
        db: AsyncSession = None
    ) -> bool:
        """
        Delete content.
        
        Args:
            content_id: Content identifier
            deleter_id: ID of user deleting content
            hard_delete: Whether to permanently delete or just mark as removed
            db: Database session
            
        Returns:
            True if successful
        """
        if not db:
            db = await get_async_session()
        
        try:
            # Get content
            content = await self._get_content_by_id(content_id, db)
            if not content:
                raise ValidationError("Content not found")
            
            # Check permissions
            if not await self._can_modify_content(content, deleter_id, db):
                raise AuthorizationError("Not authorized to delete this content")
            
            if hard_delete:
                # Delete associated records
                await db.execute(delete(ContentTag).where(ContentTag.content_id == content_id))
                await db.execute(delete(ContentStats).where(ContentStats.content_id == content_id))
                await db.execute(delete(ContentMetadata).where(ContentMetadata.content_id == content_id))
                await db.execute(delete(Content).where(Content.content_id == content_id))
                
                # Delete files from storage
                await self.storage_service.delete_file(content.file_path)
                if content.thumbnail_url:
                    await self.storage_service.delete_file(content.thumbnail_url)
                if content.preview_url:
                    await self.storage_service.delete_file(content.preview_url)
            else:
                # Soft delete - mark as removed
                await db.execute(
                    update(Content)
                    .where(Content.content_id == content_id)
                    .values(
                        status=ContentStatus.REMOVED,
                        last_modified=datetime.utcnow()
                    )
                )
            
            await db.commit()
            
            # Clear cache
            await self._clear_content_cache(content_id)
            
            # Record metrics
            await self.metrics.record_content_deleted(
                content_id=content_id,
                content_type=content.content_type.value,
                hard_delete=hard_delete,
                deleter_id=deleter_id
            )
            
            return True
            
        except Exception as e:
            await db.rollback()
            logger.error(f"Content deletion failed: {str(e)}")
            raise ServiceException(f"Deletion failed: {str(e)}")

    # Helper methods (simplified implementations)

    async def _validate_upload_request(
        self, file_data: BinaryIO, request: ContentUploadRequest, creator_id: str, db: AsyncSession
    ) -> None:
        """Validate upload request"""
        file_data.seek(0, 2)  # Seek to end
        file_size = file_data.tell()
        file_data.seek(0)  # Reset to beginning
        
        if file_size > self.config.max_file_size:
            raise ValidationError(f"File too large: {file_size} bytes")
        
        if file_size == 0:
            raise ValidationError("Empty file")

    async def _detect_file_format(self, content_bytes: bytes) -> Tuple[str, str]:
        """Detect file format and MIME type"""
        # Simplified implementation
        return "mp4", "video/mp4"

    async def _validate_file_format(self, file_format: str, content_type: ContentType) -> None:
        """Validate file format matches content type"""
        format_map = {
            ContentType.IMAGE: self.config.supported_image_formats,
            ContentType.AUDIO: self.config.supported_audio_formats,
            ContentType.VIDEO: self.config.supported_video_formats
        }
        
        if content_type in format_map and file_format not in format_map[content_type]:
            raise ValidationError(f"Unsupported format {file_format} for {content_type.value}")

    async def _extract_content_metadata(
        self, content_bytes: bytes, content_type: ContentType, file_format: str
    ) -> Dict[str, Any]:
        """Extract metadata from content"""
        # Simplified implementation
        return {"width": 1920, "height": 1080, "duration": 120.5}

    async def _process_content(
        self, content_bytes: bytes, content_type: ContentType, content_id: str, creator_id: str
    ) -> Dict[str, Any]:
        """Process content (compression, optimization, etc.)"""
        # Simplified implementation
        return {"processed_file_url": f"processed/{content_id}.mp4"}

    async def _generate_media_assets(
        self, content_bytes: bytes, content_type: ContentType, content_id: str, 
        creator_id: str, thumbnail_timestamp: Optional[float] = None
    ) -> Dict[str, Any]:
        """Generate thumbnails and previews"""
        # Simplified implementation
        return {
            "thumbnail_url": f"thumbnails/{content_id}.jpg",
            "preview_url": f"previews/{content_id}.mp4"
        }

    async def _perform_ai_analysis(
        self, content_bytes: bytes, content_type: ContentType, title: str, description: Optional[str]
    ) -> Dict[str, Any]:
        """Perform AI analysis on content"""
        # Would use AI service
        return {"sentiment": "positive", "tags": ["music", "upbeat"], "quality_score": 0.85}

    async def _moderate_content(
        self, content_bytes: bytes, request: ContentUploadRequest, ai_analysis: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Moderate content for policy violations"""
        # Would use moderation service
        return {"approved": True, "requires_review": False, "flags": []}

    def _determine_quality(self, metadata: Dict[str, Any]) -> ContentQuality:
        """Determine content quality based on metadata"""
        # Simplified implementation
        return ContentQuality.HIGH

    async def _content_to_response(
        self, content: Content, metadata: ContentMetadata, stats: ContentStats, tags: List[str]
    ) -> ContentResponse:
        """Convert content model to response"""
        # Get creator username
        creator_username = "unknown"  # Would query from database
        
        return ContentResponse(
            content_id=content.content_id,
            title=content.title,
            description=content.description,
            content_type=content.content_type,
            status=content.status,
            privacy_level=content.privacy_level,
            creator_id=content.creator_id,
            creator_username=creator_username,
            file_url=content.file_path,
            thumbnail_url=content.thumbnail_url,
            preview_url=content.preview_url,
            duration=content.duration,
            file_size=content.file_size,
            quality=content.quality,
            tags=tags,
            category=content.category,
            language=content.language,
            view_count=stats.view_count if stats else 0,
            like_count=stats.like_count if stats else 0,
            comment_count=stats.comment_count if stats else 0,
            share_count=stats.share_count if stats else 0,
            download_count=stats.download_count if stats else 0,
            upload_date=content.upload_date,
            publish_date=content.publish_date,
            last_modified=content.last_modified,
            allow_comments=content.allow_comments,
            allow_downloads=content.allow_downloads,
            monetization_enabled=content.monetization_enabled,
            ai_analysis=metadata.ai_analysis if metadata else None,
            metadata=metadata.custom_metadata if metadata else {}
        )

    async def _can_access_content(
        self, content: ContentResponse, requester_id: Optional[str], db: AsyncSession
    ) -> bool:
        """Check if user can access content"""
        if content.privacy_level == PrivacyLevel.PUBLIC:
            return True
        elif content.privacy_level == PrivacyLevel.PRIVATE:
            return requester_id == content.creator_id
        # Add more privacy logic
        return True

    async def _can_modify_content(
        self, content: Content, user_id: str, db: AsyncSession
    ) -> bool:
        """Check if user can modify content"""
        return content.creator_id == user_id  # Simplified check

    async def _get_content_by_id(self, content_id: str, db: AsyncSession) -> Optional[Content]:
        """Get content by ID"""
        query = select(Content).where(Content.content_id == content_id)
        result = await db.execute(query)
        return result.scalar_one_or_none()

    async def _track_content_view(
        self, content_id: str, viewer_id: Optional[str], db: AsyncSession
    ) -> None:
        """Track content view"""
        # Update view count
        await db.execute(
            update(ContentStats)
            .where(ContentStats.content_id == content_id)
            .values(view_count=ContentStats.view_count + 1)
        )
        await db.commit()

    async def _schedule_post_processing(self, content_id: str, creator_id: str) -> None:
        """Schedule post-processing tasks"""
        # Would schedule background tasks
        pass

    async def _get_from_cache(self, key: str) -> Optional[Dict[str, Any]]:
        """Get data from cache"""
        try:
            if self.redis_client:
                data = await self.redis_client.get(key)
                if data:
                    return json.loads(data)
        except Exception as e:
            logger.error(f"Cache get failed: {str(e)}")
        return None

    async def _set_cache(self, key: str, data: Dict[str, Any]) -> None:
        """Set data in cache"""
        try:
            if self.redis_client:
                await self.redis_client.setex(
                    key, self.config.cache_ttl_seconds, json.dumps(data, default=str)
                )
        except Exception as e:
            logger.error(f"Cache set failed: {str(e)}")

    async def _clear_content_cache(self, content_id: str) -> None:
        """Clear content cache"""
        try:
            if self.redis_client:
                await self.redis_client.delete(f"content:{content_id}")
        except Exception as e:
            logger.error(f"Cache clear failed: {str(e)}")

    def get_service_status(self) -> Dict[str, Any]:
        """Get service status"""
        return {
            "service_name": self.name,
            "status": "active",
            "config": {
                "ai_analysis": self.config.enable_ai_analysis,
                "auto_moderation": self.config.enable_auto_moderation,
                "content_compression": self.config.enable_content_compression,
                "thumbnail_generation": self.config.enable_thumbnail_generation
            },
            "metrics": self.metrics.get_summary()
        }

    def get_capabilities(self) -> Dict[str, Any]:
        """Get service capabilities"""
        return {
            "content_types": [ct.value for ct in ContentType],
            "privacy_levels": [pl.value for pl in PrivacyLevel],
            "content_statuses": [cs.value for cs in ContentStatus],
            "quality_levels": [q.value for q in ContentQuality],
            "supported_formats": {
                "image": self.config.supported_image_formats,
                "audio": self.config.supported_audio_formats,
                "video": self.config.supported_video_formats
            },
            "features": [
                "multi_format_upload",
                "ai_analysis",
                "content_moderation",
                "thumbnail_generation",
                "preview_generation",
                "content_compression",
                "advanced_search",
                "privacy_control",
                "analytics_integration",
                "monetization_support",
                "batch_processing",
                "real_time_streaming"
            ],
            "max_file_size": self.config.max_file_size,
            "thumbnail_size": self.config.thumbnail_size,
            "preview_duration": self.config.preview_duration
        }