"""
Content Manager - Multi-format content handling for creators.

Manages upload, processing, and organization of various content types
including audio, video, images, and text for IA Influencer platform.

Author: Fahed Mlaiel <mlaiel@live.de>
Project: IA Influencer Agent with Advanced Content Protection
"""

from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, BinaryIO, Tuple
from uuid import UUID, uuid4
import logging
from pathlib import Path
import mimetypes
from enum import Enum
import hashlib
import asyncio

from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from pydantic import BaseModel, validator
from PIL import Image
import ffmpeg

from ...core.database import get_db
from ...core.exceptions import (
    ContentNotFoundError,
    InvalidContentError,
    ContentServiceError,
    StorageError
)
from ...models.content import Content, ContentType, ContentStatus, ProcessingStage
from ...services.storage.file_storage import FileStorageService
from ...services.ai.content_analysis import ContentAnalysisService
from ...services.protection.fingerprinting import FingerprintingService
from ...utils.file_utils import FileUtils
from ...utils.validation import ValidationUtils


logger = logging.getLogger(__name__)


class SupportedFormat(str, Enum):
    """Supported content formats by type."""
    # Audio formats
    MP3 = "mp3"
    WAV = "wav" 
    FLAC = "flac"
    M4A = "m4a"
    OGG = "ogg"
    
    # Video formats
    MP4 = "mp4"
    AVI = "avi"
    MOV = "mov"
    MKV = "mkv"
    WEBM = "webm"
    
    # Image formats
    JPEG = "jpeg"
    JPG = "jpg"
    PNG = "png"
    GIF = "gif"
    WEBP = "webp"
    TIFF = "tiff"
    
    # Text formats
    TXT = "txt"
    MD = "md"
    HTML = "html"
    PDF = "pdf"


class ContentUploadData(BaseModel):
    """Content upload metadata validation."""
    title: str
    description: Optional[str] = None
    tags: List[str] = []
    category: Optional[str] = None
    language: str = "en"
    is_private: bool = False
    allow_downloads: bool = False
    licensing_terms: Optional[str] = None
    custom_metadata: Optional[Dict[str, Any]] = None
    
    @validator('title')
    def validate_title(cls, v):
        if len(v.strip()) < 3:
            raise ValueError('Title must be at least 3 characters long')
        return v.strip()
    
    @validator('tags')
    def validate_tags(cls, v):
        if len(v) > 20:
            raise ValueError('Maximum 20 tags allowed')
        return [tag.strip().lower() for tag in v if tag.strip()]


class ContentProcessingOptions(BaseModel):
    """Content processing configuration."""
    generate_thumbnails: bool = True
    extract_metadata: bool = True
    create_fingerprint: bool = True
    analyze_content: bool = True
    generate_transcription: bool = False  # For audio/video
    auto_seo_optimize: bool = True
    quality_optimization: bool = True


class ContentManager:
    """
    Multi-format content management system for creators.
    
    Handles comprehensive content lifecycle including:
    - Upload processing and validation
    - Multi-format support (audio, video, image, text)
    - Content analysis and optimization
    - Fingerprinting for protection
    - Storage and organization
    - Metadata extraction and management
    """
    
    def __init__(
        self,
        db: Session,
        file_storage: FileStorageService,
        content_analysis: ContentAnalysisService,
        fingerprinting: FingerprintingService
    ):
        self.db = db
        self.file_storage = file_storage
        self.content_analysis = content_analysis
        self.fingerprinting = fingerprinting
        self.file_utils = FileUtils()
        self.validation_utils = ValidationUtils()
        
        # File size limits (in bytes)
        self.size_limits = {
            ContentType.AUDIO: 500 * 1024 * 1024,  # 500MB
            ContentType.VIDEO: 2 * 1024 * 1024 * 1024,  # 2GB
            ContentType.IMAGE: 50 * 1024 * 1024,  # 50MB
            ContentType.TEXT: 10 * 1024 * 1024,  # 10MB
        }
        
    async def upload_content(
        self,
        client_id: UUID,
        file_stream: BinaryIO,
        filename: str,
        upload_data: ContentUploadData,
        processing_options: ContentProcessingOptions = ContentProcessingOptions()
    ) -> Dict[str, Any]:
        """
        Upload and process new content.
        
        Args:
            client_id: Client uploading the content
            file_stream: File data stream
            filename: Original filename
            upload_data: Content metadata
            processing_options: Processing configuration
            
        Returns:
            Content upload result with processing status
            
        Raises:
            InvalidContentError: If file format not supported
            StorageError: If upload fails
        """



        try:
            # Validate file and determine content type
            content_type, file_extension = self._determine_content_type(filename)
            if not content_type:
                raise InvalidContentError(f"Unsupported file format: {file_extension}")
                
            # Validate file size
            file_size = self._get_file_size(file_stream)
            if file_size > self.size_limits[content_type]:
                max_size_mb = self.size_limits[content_type] / (1024 * 1024)
                raise InvalidContentError(
                    f"File size exceeds limit of {max_size_mb}MB for {content_type.value}"
                )
                
            # Generate unique content ID and storage path
            content_id = uuid4()
            storage_path = self._generate_storage_path(
                client_id, content_id, file_extension
            )
            
            # Create content record
            content = Content(
                id=content_id,
                client_id=client_id,
                title=upload_data.title,
                description=upload_data.description,
                content_type=content_type,
                file_extension=file_extension,
                original_filename=filename,
                file_size=file_size,
                storage_path=storage_path,
                tags=upload_data.tags,
                category=upload_data.category,
                language=upload_data.language,
                is_private=upload_data.is_private,
                allow_downloads=upload_data.allow_downloads,
                licensing_terms=upload_data.licensing_terms,
                custom_metadata=upload_data.custom_metadata or {},
                status=ContentStatus.UPLOADING,
                processing_stage=ProcessingStage.UPLOAD_PENDING
            )
            
            self.db.add(content)
            self.db.commit()
            
            # Upload file to storage
            file_stream.seek(0)  # Reset stream position
            upload_result = await self.file_storage.upload_file(
                file_stream=file_stream,
                storage_path=storage_path,
                content_type=self._get_mime_type(filename)
            )
            
            if not upload_result.get('success'):
                raise StorageError("Failed to upload file to storage")
                
            # Update content with upload success
            content.status = ContentStatus.PROCESSING
            content.processing_stage = ProcessingStage.FILE_VALIDATION
            content.uploaded_at = datetime.utcnow()
            self.db.commit()
            
            # Start async processing pipeline
            asyncio.create_task(
                self._process_content_pipeline(content.id, processing_options)
            )
            
            logger.info(f"Content upload initiated: {content.id}")
            
            return {
                "content_id": str(content.id),
                "status": "upload_successful",
                "processing_stage": content.processing_stage.value,
                "estimated_processing_time": self._estimate_processing_time(
                    content_type, file_size
                )
            }
            
        except Exception as e:
            if 'content' in locals():
                content.status = ContentStatus.FAILED
                self.db.commit()
            logger.error(f"Content upload failed: {e}")
            raise ContentServiceError("Content upload failed") from e
            
    async def get_content_by_id(
        self,
        content_id: UUID,
        client_id: Optional[UUID] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Retrieve content information by ID.
        
        Args:
            content_id: Content identifier
            client_id: Optional client ID for access validation
            
        Returns:
            Content data or None if not found/accessible
        """



        try:
            query = self.db.query(Content).filter(Content.id == content_id)
            
            if client_id:
                query = query.filter(Content.client_id == client_id)
                
            content = query.first()
            if not content:
                return None
                
            return await self._format_content_data(content)
            
        except Exception as e:
            logger.error(f"Error retrieving content {content_id}: {e}")
            return None
            
    async def list_client_content(
        self,
        client_id: UUID,
        content_type: Optional[ContentType] = None,
        status: Optional[ContentStatus] = None,
        page: int = 1,
        limit: int = 50
    ) -> Dict[str, Any]:
        """
        List content for a specific client.
        
        Args:
            client_id: Client identifier
            content_type: Optional filter by content type
            status: Optional filter by status
            page: Page number
            limit: Items per page
            
        Returns:
            Paginated content list
        """



        try:
            query = self.db.query(Content).filter(Content.client_id == client_id)
            
            if content_type:
                query = query.filter(Content.content_type == content_type)
            if status:
                query = query.filter(Content.status == status)
                
            total = query.count()
            offset = (page - 1) * limit
            
            content_items = query.order_by(Content.created_at.desc()).offset(offset).limit(limit).all()
            
            formatted_items = []
            for item in content_items:
                formatted_item = await self._format_content_data(item)
                formatted_items.append(formatted_item)
                
            return {
                "items": formatted_items,
                "total": total,
                "page": page,
                "limit": limit,
                "pages": (total + limit - 1) // limit
            }
            
        except Exception as e:
            logger.error(f"Error listing content for client {client_id}: {e}")
            raise ContentServiceError("Failed to retrieve content list") from e
            
    async def delete_content(
        self,
        content_id: UUID,
        client_id: UUID,
        permanent: bool = False
    ) -> bool:
        """
        Delete or soft-delete content.
        
        Args:
            content_id: Content identifier
            client_id: Client identifier for ownership validation
            permanent: If True, permanently delete; otherwise soft delete
            
        Returns:
            True if successful
        """



        try:
            content = self.db.query(Content).filter(
                Content.id == content_id,
                Content.client_id == client_id
            ).first()
            
            if not content:
                raise ContentNotFoundError(f"Content not found: {content_id}")
                
            if permanent:
                # Delete file from storage
                await self.file_storage.delete_file(content.storage_path)
                
                # Delete from database
                self.db.delete(content)
            else:
                # Soft delete
                content.status = ContentStatus.DELETED
                content.deleted_at = datetime.utcnow()
                
            self.db.commit()
            
            logger.info(f"Content {'permanently ' if permanent else ''}deleted: {content_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error deleting content {content_id}: {e}")
            return False
            
    async def _process_content_pipeline(
        self,
        content_id: UUID,
        processing_options: ContentProcessingOptions
    ) -> None:
        """
        Async content processing pipeline.
        
        Handles all content processing steps including:
        - File validation and analysis
        - Metadata extraction
        - Thumbnail generation
        - Fingerprinting for protection
        - SEO optimization
        """



        try:
            content = self.db.query(Content).filter(Content.id == content_id).first()
            if not content:
                logger.error(f"Content not found for processing: {content_id}")
                return
                
            # Stage 1: File validation
            content.processing_stage = ProcessingStage.FILE_VALIDATION
            self.db.commit()
            
            file_validation = await self._validate_content_file(content)
            if not file_validation['valid']:
                content.status = ContentStatus.FAILED
                content.processing_error = file_validation['error']
                self.db.commit()
                return
                
            # Stage 2: Metadata extraction
            if processing_options.extract_metadata:
                content.processing_stage = ProcessingStage.METADATA_EXTRACTION
                self.db.commit()
                
                metadata = await self._extract_metadata(content)
                content.extracted_metadata = metadata
                
            # Stage 3: Content analysis
            if processing_options.analyze_content:
                content.processing_stage = ProcessingStage.CONTENT_ANALYSIS
                self.db.commit()
                
                analysis = await self.content_analysis.analyze_content(
                    content.storage_path,
                    content.content_type
                )
                content.analysis_results = analysis
                
            # Stage 4: Thumbnail generation
            if processing_options.generate_thumbnails:
                content.processing_stage = ProcessingStage.THUMBNAIL_GENERATION
                self.db.commit()
                
                thumbnails = await self._generate_thumbnails(content)
                content.thumbnail_paths = thumbnails
                
            # Stage 5: Fingerprinting
            if processing_options.create_fingerprint:
                content.processing_stage = ProcessingStage.FINGERPRINTING
                self.db.commit()
                
                fingerprint = await self.fingerprinting.create_fingerprint(
                    content.storage_path,
                    content.content_type
                )
                content.fingerprint_hash = fingerprint.get('hash')
                content.fingerprint_vector = fingerprint.get('vector')
                
            # Stage 6: SEO optimization
            if processing_options.auto_seo_optimize:
                content.processing_stage = ProcessingStage.SEO_OPTIMIZATION
                self.db.commit()
                
                seo_data = await self._optimize_for_seo(content)
                content.seo_metadata = seo_data
                
            # Processing complete
            content.status = ContentStatus.ACTIVE
            content.processing_stage = ProcessingStage.COMPLETED
            content.processed_at = datetime.utcnow()
            self.db.commit()
            
            logger.info(f"Content processing completed: {content_id}")
            
        except Exception as e:
            content = self.db.query(Content).filter(Content.id == content_id).first()
            if content:
                content.status = ContentStatus.FAILED
                content.processing_error = str(e)
                self.db.commit()
            logger.error(f"Content processing failed for {content_id}: {e}")
            
    def _determine_content_type(self, filename: str) -> Tuple[Optional[ContentType], str]:
        """Determine content type from filename."""
        file_extension = Path(filename).suffix.lower().lstrip('.')
        
        if file_extension in ['mp3', 'wav', 'flac', 'm4a', 'ogg']:
            return ContentType.AUDIO, file_extension
        elif file_extension in ['mp4', 'avi', 'mov', 'mkv', 'webm']:
            return ContentType.VIDEO, file_extension
        elif file_extension in ['jpg', 'jpeg', 'png', 'gif', 'webp', 'tiff']:
            return ContentType.IMAGE, file_extension
        elif file_extension in ['txt', 'md', 'html', 'pdf']:
            return ContentType.TEXT, file_extension
        else:
            return None, file_extension
            
    def _get_file_size(self, file_stream: BinaryIO) -> int:
        """Get file size from stream."""
        current_pos = file_stream.tell()
        file_stream.seek(0, 2)  # Seek to end
        size = file_stream.tell()
        file_stream.seek(current_pos)  # Reset position
        return size
        
    def _generate_storage_path(
        self,
        client_id: UUID,
        content_id: UUID,
        file_extension: str
    ) -> str:
        """Generate storage path for content file."""
        date_path = datetime.utcnow().strftime("%Y/%m/%d")
        return f"content/{client_id}/{date_path}/{content_id}.{file_extension}"
        
    def _get_mime_type(self, filename: str) -> str:
        """Get MIME type for filename."""
        mime_type, _ = mimetypes.guess_type(filename)
        return mime_type or "application/octet-stream"
        
    def _estimate_processing_time(self, content_type: ContentType, file_size: int) -> int:
        """Estimate processing time in seconds."""
        base_times = {
            ContentType.AUDIO: 30,
            ContentType.VIDEO: 120,
            ContentType.IMAGE: 10,
            ContentType.TEXT: 5
        }
        
        # Add time based on file size (rough estimation)
        size_factor = min(file_size / (10 * 1024 * 1024), 5)  # Max 5x multiplier
        return int(base_times[content_type] * (1 + size_factor))
        
    async def _format_content_data(self, content: Content) -> Dict[str, Any]:
        """Format content data for API response."""



        return {
            "id": str(content.id),
            "title": content.title,
            "description": content.description,
            "content_type": content.content_type.value,
            "file_extension": content.file_extension,
            "original_filename": content.original_filename,
            "file_size": content.file_size,
            "status": content.status.value,
            "processing_stage": content.processing_stage.value if content.processing_stage else None,
            "tags": content.tags,
            "category": content.category,
            "language": content.language,
            "is_private": content.is_private,
            "allow_downloads": content.allow_downloads,
            "view_count": content.view_count,
            "download_count": content.download_count,
            "created_at": content.created_at.isoformat(),
            "uploaded_at": content.uploaded_at.isoformat() if content.uploaded_at else None,
            "processed_at": content.processed_at.isoformat() if content.processed_at else None,
            "thumbnail_url": await self._get_thumbnail_url(content),
            "download_url": await self._get_download_url(content) if not content.is_private else None
        }
        
    async def _validate_content_file(self, content: Content) -> Dict[str, Any]:
        """Validate uploaded content file."""



        try:
            # Implementation would validate file integrity, format, etc.
            return {"valid": True}
        except Exception as e:
            return {"valid": False, "error": str(e)}
            
    async def _extract_metadata(self, content: Content) -> Dict[str, Any]:
        """Extract metadata from content file."""
        # Implementation would extract metadata based on content type
        return {}
        
    async def _generate_thumbnails(self, content: Content) -> List[str]:
        """Generate thumbnails for content."""
        # Implementation would generate thumbnails based on content type
        return []
        
    async def _optimize_for_seo(self, content: Content) -> Dict[str, Any]:
        """Optimize content metadata for SEO."""
        # Implementation would generate SEO-optimized metadata
        return {}
        
    async def _get_thumbnail_url(self, content: Content) -> Optional[str]:
        """Get thumbnail URL for content."""
        # Implementation would return thumbnail URL
        return None
        
    async def _get_download_url(self, content: Content) -> Optional[str]:
        """Get download URL for content."""
        # Implementation would return secure download URL
        return None
