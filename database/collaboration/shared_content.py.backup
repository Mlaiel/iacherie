"""Shared Content Database Module

Enterprise content sharing system for multi-format collaborative projects.
Handles content versioning, access control, and real-time synchronization.

Author: Fahed Mlaiel <mlaiel@live.de>
Team: Lead AI Developer + Backend Senior + ML Engineer + DBA + Security + Microservices
"""
from typing import List, Dict, Any, Optional, Union, Tuple, Set
from datetime import datetime, timedelta
from enum import Enum
import json
import uuid
import logging
import hashlib
import mimetypes
from pathlib import Path
from sqlalchemy import (
    Column, Integer, String, DateTime, Boolean, Text, 
    ForeignKey, DECIMAL, ARRAY, JSON, Index, LargeBinary, BigInteger
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy.dialects.postgresql import UUID, JSONB, ENUM
import asyncio
import aioredis
import aiofiles
from dataclasses import dataclass, asdict
import boto3
from botocore.exceptions import ClientError

logger = logging.getLogger(__name__)

Base = declarative_base()

class ContentType(Enum):
    """Content type enumeration for multi-format support"""
    AUDIO = "audio"
    VIDEO = "video"
    IMAGE = "image"
    TEXT = "text"
    DOCUMENT = "document"
    ARCHIVE = "archive"
    DESIGN = "design"
    SCRIPT = "script"
    LYRICS = "lyrics"
    NOTES = "notes"

class ContentStatus(Enum):
    """Content status enumeration"""
    DRAFT = "draft"
    IN_PROGRESS = "in_progress"
    REVIEW = "review"
    APPROVED = "approved"
    PUBLISHED = "published"
    ARCHIVED = "archived"
    DELETED = "deleted"

class AccessLevel(Enum):
    """Access level enumeration"""
    OWNER = "owner"
    EDITOR = "editor"
    VIEWER = "viewer"
    COMMENTER = "commenter"
    RESTRICTED = "restricted"

class ContentFormat(Enum):
    """Specific content format enumeration"""
    # Audio formats
    MP3 = "mp3"
    WAV = "wav"
    FLAC = "flac"
    AAC = "aac"
    OGG = "ogg"
    
    # Video formats
    MP4 = "mp4"
    AVI = "avi"
    MOV = "mov"
    WMV = "wmv"
    MKV = "mkv"
    
    # Image formats
    JPEG = "jpeg"
    PNG = "png"
    GIF = "gif"
    SVG = "svg"
    TIFF = "tiff"
    
    # Document formats
    PDF = "pdf"
    DOCX = "docx"
    TXT = "txt"
    MD = "md"
    HTML = "html"

class SharedContent(Base):
    """
    Core shared content model for collaborative projects.
    Supports multi-format content with advanced versioning and access control.
    """
    __tablename__ = 'shared_content'
    
    # Primary identification
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    content_id = Column(String(100), unique=True, nullable=False, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text)
    
    # Content classification
    content_type = Column(ENUM(ContentType), nullable=False)
    content_format = Column(ENUM(ContentFormat))
    mime_type = Column(String(100))
    file_extension = Column(String(10))
    
    # Project and ownership
    project_id = Column(UUID(as_uuid=True), ForeignKey('collaboration_projects.id'), nullable=False)
    owner_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False)
    created_by = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False)
    
    # File information
    original_filename = Column(String(255))
    file_size_bytes = Column(BigInteger)
    file_checksum = Column(String(64))  # SHA-256
    storage_path = Column(String(500))
    storage_bucket = Column(String(100))
    cdn_url = Column(String(500))
    
    # Content metadata
    content_metadata = Column(JSONB)  # Format-specific metadata
    technical_specs = Column(JSONB)   # Resolution, bitrate, etc.
    ai_analysis = Column(JSONB)       # AI-extracted features
    tags = Column(ARRAY(String))
    keywords = Column(ARRAY(String))
    
    # Version control
    version = Column(String(20), default='1.0.0')
    parent_version_id = Column(UUID(as_uuid=True), ForeignKey('shared_content.id'))
    is_latest_version = Column(Boolean, default=True)
    version_notes = Column(Text)
    branch_name = Column(String(100), default='main')
    
    # Status and workflow
    status = Column(ENUM(ContentStatus), default=ContentStatus.DRAFT)
    workflow_stage = Column(String(50))
    approval_required = Column(Boolean, default=False)
    approved_by = Column(UUID(as_uuid=True), ForeignKey('users.id'))
    approved_at = Column(DateTime)
    
    # Access control
    visibility = Column(String(20), default='project')  # project, team, public, private
    access_permissions = Column(JSONB)
    sharing_settings = Column(JSONB)
    download_allowed = Column(Boolean, default=True)
    
    # Collaboration features
    comments_enabled = Column(Boolean, default=True)
    real_time_editing = Column(Boolean, default=False)
    lock_status = Column(JSONB)  # Who has content locked
    edit_history = Column(JSONB)
    
    # Analytics and tracking
    view_count = Column(Integer, default=0)
    download_count = Column(Integer, default=0)
    share_count = Column(Integer, default=0)
    last_accessed = Column(DateTime)
    access_log = Column(JSONB)
    
    # AI and processing
    ai_processed = Column(Boolean, default=False)
    ai_processing_status = Column(String(50))
    ai_features = Column(JSONB)
    content_fingerprint = Column(String(255))
    similarity_hash = Column(String(64))
    
    # Quality and validation
    quality_score = Column(DECIMAL(3, 2))
    content_warnings = Column(ARRAY(String))
    moderation_status = Column(String(20), default='pending')
    moderation_notes = Column(Text)
    
    # Timestamps and audit
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_modified_by = Column(UUID(as_uuid=True), ForeignKey('users.id'))
    published_at = Column(DateTime)
    archived_at = Column(DateTime)
    
    # Indexes for performance
    __table_args__ = (
        Index('idx_content_project_type', 'project_id', 'content_type'),
        Index('idx_content_owner_status', 'owner_id', 'status'),
        Index('idx_content_created_date', 'created_at'),
        Index('idx_content_version', 'parent_version_id', 'version'),
        Index('idx_content_fingerprint', 'content_fingerprint'),
    )

class ContentAccess(Base):
    """
    Content access control and permissions model.
    Manages fine-grained access to shared content.
    """
    __tablename__ = 'content_access'
    
    # Primary identification
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    content_id = Column(UUID(as_uuid=True), ForeignKey('shared_content.id'), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False)
    
    # Access control
    access_level = Column(ENUM(AccessLevel), nullable=False)
    granted_by = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False)
    granted_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime)
    
    # Permissions
    can_view = Column(Boolean, default=True)
    can_edit = Column(Boolean, default=False)
    can_comment = Column(Boolean, default=True)
    can_download = Column(Boolean, default=True)
    can_share = Column(Boolean, default=False)
    can_delete = Column(Boolean, default=False)
    
    # Restrictions
    ip_restrictions = Column(ARRAY(String))
    time_restrictions = Column(JSONB)
    usage_limits = Column(JSONB)
    watermark_required = Column(Boolean, default=False)
    
    # Tracking
    last_accessed = Column(DateTime)
    access_count = Column(Integer, default=0)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Indexes
    __table_args__ = (
        Index('idx_access_content_user', 'content_id', 'user_id'),
        Index('idx_access_user_level', 'user_id', 'access_level'),
    )

class ContentComment(Base):
    """
    Content comments and review system.
    Supports threaded discussions and review workflows.
    """
    __tablename__ = 'content_comments'
    
    # Primary identification
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    content_id = Column(UUID(as_uuid=True), ForeignKey('shared_content.id'), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False)
    
    # Comment structure
    parent_comment_id = Column(UUID(as_uuid=True), ForeignKey('content_comments.id'))
    thread_id = Column(UUID(as_uuid=True))
    comment_text = Column(Text, nullable=False)
    
    # Position and annotation
    timestamp_start = Column(DECIMAL(10, 3))  # For audio/video comments
    timestamp_end = Column(DECIMAL(10, 3))
    position_x = Column(Integer)  # For image comments
    position_y = Column(Integer)
    annotation_data = Column(JSONB)
    
    # Comment metadata
    comment_type = Column(String(20), default='general')  # general, review, suggestion, issue
    priority = Column(String(10), default='normal')
    status = Column(String(20), default='open')  # open, addressed, resolved, dismissed
    
    # Rich content
    attachments = Column(JSONB)
    mentions = Column(ARRAY(UUID(as_uuid=True)))
    reactions = Column(JSONB)
    
    # Resolution tracking
    resolved_by = Column(UUID(as_uuid=True), ForeignKey('users.id'))
    resolved_at = Column(DateTime)
    resolution_notes = Column(Text)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Indexes
    __table_args__ = (
        Index('idx_comment_content_thread', 'content_id', 'thread_id'),
        Index('idx_comment_user_date', 'user_id', 'created_at'),
        Index('idx_comment_parent', 'parent_comment_id'),
    )

@dataclass
class ContentUploadRequest:
    """Data class for content upload requests"""
    title: str
    project_id: str
    owner_id: str
    content_type: ContentType
    file_path: str = None
    file_data: bytes = None
    filename: str = None
    description: str = None
    tags: List[str] = None
    metadata: Dict[str, Any] = None
    access_level: AccessLevel = AccessLevel.EDITOR
    enable_versioning: bool = True

@dataclass
class ContentUpdateRequest:
    """Data class for content update requests"""
    content_id: str
    title: str = None
    description: str = None
    status: ContentStatus = None
    tags: List[str] = None
    metadata: Dict[str, Any] = None
    version_notes: str = None

class SharedContentManager:
    """
    Enterprise shared content management system.
    Handles upload, versioning, access control, and collaboration features.
    """
    
    def __init__(self, db_session, redis_client: aioredis.Redis = None, s3_client = None):
        self.db_session = db_session
        self.redis_client = redis_client
        self.s3_client = s3_client or boto3.client('s3')
        self.cache_ttl = 3600  # 1 hour cache
        self.default_bucket = 'ia-influencer-content'
        
        # Content processing settings
        self.max_file_size = 500 * 1024 * 1024  # 500MB
        self.allowed_extensions = {
            '.mp3', '.wav', '.flac', '.mp4', '.avi', '.mov',
            '.jpg', '.jpeg', '.png', '.gif', '.pdf', '.docx', '.txt'
        }
    
    async def upload_content(self, request: ContentUploadRequest) -> Optional[SharedContent]:
        """
        Upload and process new content with enterprise features.
        
        Args:
            request: Content upload request
            
        Returns:
            Created content instance
        """
        try:
            # Validate file
            if request.file_path:
                if not Path(request.file_path).exists():
                    raise ValueError(f"File not found: {request.file_path}")
                
                async with aiofiles.open(request.file_path, 'rb') as f:
                    file_data = await f.read()
                    filename = Path(request.file_path).name
            elif request.file_data:
                file_data = request.file_data
                filename = request.filename or 'uploaded_file'
            else:
                raise ValueError("Either file_path or file_data must be provided")
            
            # Validate file size
            if len(file_data) > self.max_file_size:
                raise ValueError(f"File too large: {len(file_data)} bytes")
            
            # Validate file extension
            file_ext = Path(filename).suffix.lower()
            if file_ext not in self.allowed_extensions:
                raise ValueError(f"Unsupported file type: {file_ext}")
            
            # Generate content ID and paths
            content_id = self._generate_content_id(request.content_type)
            file_checksum = hashlib.sha256(file_data).hexdigest()
            storage_path = self._generate_storage_path(content_id, filename)
            
            # Upload to S3
            s3_key = await self._upload_to_s3(file_data, storage_path)
            cdn_url = self._generate_cdn_url(s3_key)
            
            # Detect content format and mime type
            content_format, mime_type = self._detect_content_format(filename, file_data)
            
            # Extract metadata
            content_metadata = await self._extract_content_metadata(file_data, content_format)
            technical_specs = await self._analyze_technical_specs(file_data, content_format)
            
            # Create content record
            content = SharedContent(
                content_id=content_id,
                title=request.title,
                description=request.description,
                content_type=request.content_type,
                content_format=content_format,
                mime_type=mime_type,
                file_extension=file_ext,
                project_id=uuid.UUID(request.project_id),
                owner_id=uuid.UUID(request.owner_id),
                created_by=uuid.UUID(request.owner_id),
                original_filename=filename,
                file_size_bytes=len(file_data),
                file_checksum=file_checksum,
                storage_path=storage_path,
                storage_bucket=self.default_bucket,
                cdn_url=cdn_url,
                content_metadata=content_metadata,
                technical_specs=technical_specs,
                tags=request.tags or [],
                access_permissions=self._default_access_permissions(request.access_level),
                sharing_settings=self._default_sharing_settings()
            )
            
            # Save to database
            self.db_session.add(content)
            await self.db_session.commit()
            await self.db_session.refresh(content)
            
            # Create owner access record
            await self._create_owner_access(content.id, request.owner_id)
            
            # Process with AI (async)
            asyncio.create_task(self._process_content_with_ai(content.id))
            
            # Cache content
            if self.redis_client:
                await self._cache_content(content)
            
            logger.info(f"Content uploaded: {content_id}")
            
            return content
            
        except Exception as e:
            await self.db_session.rollback()
            logger.error(f"Failed to upload content: {str(e)}")
            raise
    
    async def get_content(self, content_id: str, user_id: str = None) -> Optional[SharedContent]:
        """
        Retrieve content with access control validation.
        
        Args:
            content_id: Content identifier
            user_id: Requesting user ID
            
        Returns:
            Content instance or None
        """
        try:
            # Check cache first
            if self.redis_client:
                cached_data = await self.redis_client.get(f"content:{content_id}")
                if cached_data:
                    content = self._deserialize_content(json.loads(cached_data))
                    if await self._check_content_access(content.id, user_id):
                        return content
            
            # Query database
            content = await self.db_session.query(SharedContent)\
                .filter(SharedContent.content_id == content_id)\
                .first()
            
            if not content:
                return None
            
            # Check access permissions
            if user_id and not await self._check_content_access(content.id, user_id):
                logger.warning(f"Access denied for user {user_id} to content {content_id}")
                return None
            
            # Update access tracking
            if user_id:
                await self._track_content_access(content.id, user_id)
            
            # Cache result
            if self.redis_client:
                await self._cache_content(content)
            
            return content
            
        except Exception as e:
            logger.error(f"Failed to retrieve content {content_id}: {str(e)}")
            return None
    
    async def update_content(self, request: ContentUpdateRequest, user_id: str) -> Optional[SharedContent]:
        """
        Update content with versioning support.
        
        Args:
            request: Content update request
            user_id: User making the update
            
        Returns:
            Updated content instance
        """
        try:
            content = await self.get_content(request.content_id, user_id)
            if not content:
                return None
            
            # Check edit permissions
            if not await self._check_edit_permission(content.id, user_id):
                raise PermissionError("Insufficient permissions to edit content")
            
            # Track changes for versioning
            changes = {}
            
            if request.title and request.title != content.title:
                changes['title'] = {'old': content.title, 'new': request.title}
                content.title = request.title
            
            if request.description and request.description != content.description:
                changes['description'] = {'old': content.description, 'new': request.description}
                content.description = request.description
            
            if request.status and request.status != content.status:
                changes['status'] = {'old': content.status.value, 'new': request.status.value}
                content.status = request.status
            
            if request.tags is not None:
                changes['tags'] = {'old': content.tags, 'new': request.tags}
                content.tags = request.tags
            
            if request.metadata:
                old_metadata = content.content_metadata or {}
                new_metadata = {**old_metadata, **request.metadata}
                changes['metadata'] = {'old': old_metadata, 'new': new_metadata}
                content.content_metadata = new_metadata
            
            # Update modification tracking
            content.updated_at = datetime.utcnow()
            content.last_modified_by = uuid.UUID(user_id)
            
            # Store edit history
            if changes:
                edit_entry = {
                    'timestamp': datetime.utcnow().isoformat(),
                    'user_id': user_id,
                    'changes': changes,
                    'version_notes': request.version_notes
                }
                
                edit_history = content.edit_history or []
                edit_history.append(edit_entry)
                content.edit_history = edit_history
            
            # Save changes
            await self.db_session.commit()
            
            # Update cache
            if self.redis_client:
                await self._cache_content(content)
            
            logger.info(f"Content updated: {request.content_id} by {user_id}")
            
            return content
            
        except Exception as e:
            await self.db_session.rollback()
            logger.error(f"Failed to update content {request.content_id}: {str(e)}")
            raise
    
    async def create_content_version(
        self, 
        content_id: str, 
        user_id: str, 
        file_data: bytes = None,
        version_notes: str = None
    ) -> Optional[SharedContent]:
        """
        Create a new version of existing content.
        
        Args:
            content_id: Original content ID
            user_id: User creating the version
            file_data: New file data (optional)
            version_notes: Version change notes
            
        Returns:
            New version content instance
        """
        try:
            original_content = await self.get_content(content_id, user_id)
            if not original_content:
                return None
            
            # Check edit permissions
            if not await self._check_edit_permission(original_content.id, user_id):
                raise PermissionError("Insufficient permissions to create version")
            
            # Generate new version number
            new_version = self._increment_version(original_content.version)
            
            # Mark original as not latest
            original_content.is_latest_version = False
            
            # Create new version
            new_content = SharedContent(
                content_id=self._generate_content_id(original_content.content_type),
                title=f"{original_content.title} (v{new_version})",
                description=original_content.description,
                content_type=original_content.content_type,
                content_format=original_content.content_format,
                mime_type=original_content.mime_type,
                file_extension=original_content.file_extension,
                project_id=original_content.project_id,
                owner_id=original_content.owner_id,
                created_by=uuid.UUID(user_id),
                parent_version_id=original_content.id,
                version=new_version,
                version_notes=version_notes,
                original_filename=original_content.original_filename,
                tags=original_content.tags,
                access_permissions=original_content.access_permissions,
                sharing_settings=original_content.sharing_settings
            )
            
            # Handle new file data
            if file_data:
                file_checksum = hashlib.sha256(file_data).hexdigest()
                storage_path = self._generate_storage_path(new_content.content_id, original_content.original_filename)
                
                # Upload to S3
                s3_key = await self._upload_to_s3(file_data, storage_path)
                cdn_url = self._generate_cdn_url(s3_key)
                
                new_content.file_size_bytes = len(file_data)
                new_content.file_checksum = file_checksum
                new_content.storage_path = storage_path
                new_content.cdn_url = cdn_url
                
                # Extract metadata for new file
                content_metadata = await self._extract_content_metadata(file_data, new_content.content_format)
                technical_specs = await self._analyze_technical_specs(file_data, new_content.content_format)
                new_content.content_metadata = content_metadata
                new_content.technical_specs = technical_specs
            else:
                # Copy file references from original
                new_content.file_size_bytes = original_content.file_size_bytes
                new_content.file_checksum = original_content.file_checksum
                new_content.storage_path = original_content.storage_path
                new_content.storage_bucket = original_content.storage_bucket
                new_content.cdn_url = original_content.cdn_url
                new_content.content_metadata = original_content.content_metadata
                new_content.technical_specs = original_content.technical_specs
            
            # Save both records
            self.db_session.add(new_content)
            await self.db_session.commit()
            await self.db_session.refresh(new_content)
            
            # Copy access permissions
            await self._copy_access_permissions(original_content.id, new_content.id)
            
            # Cache new version
            if self.redis_client:
                await self._cache_content(new_content)
            
            logger.info(f"Content version created: {new_content.content_id} from {content_id}")
            
            return new_content
            
        except Exception as e:
            await self.db_session.rollback()
            logger.error(f"Failed to create content version: {str(e)}")
            raise
    
    async def add_content_comment(
        self,
        content_id: str,
        user_id: str,
        comment_text: str,
        comment_type: str = 'general',
        parent_comment_id: str = None,
        annotation_data: Dict[str, Any] = None
    ) -> Optional[ContentComment]:
        """
        Add comment to content with annotation support.
        
        Args:
            content_id: Content identifier
            user_id: Commenting user ID
            comment_text: Comment text
            comment_type: Type of comment
            parent_comment_id: Parent comment for threading
            annotation_data: Position/timing data
            
        Returns:
            Created comment instance
        """
        try:
            # Get content and check access
            content = await self.get_content(content_id, user_id)
            if not content:
                return None
            
            # Check comment permissions
            if not await self._check_comment_permission(content.id, user_id):
                raise PermissionError("Insufficient permissions to comment")
            
            # Generate thread ID for new threads
            thread_id = uuid.uuid4() if not parent_comment_id else None
            if parent_comment_id:
                parent_comment = await self.db_session.query(ContentComment)\
                    .filter(ContentComment.id == uuid.UUID(parent_comment_id))\
                    .first()
                if parent_comment:
                    thread_id = parent_comment.thread_id
            
            # Create comment
            comment = ContentComment(
                content_id=content.id,
                user_id=uuid.UUID(user_id),
                parent_comment_id=uuid.UUID(parent_comment_id) if parent_comment_id else None,
                thread_id=thread_id,
                comment_text=comment_text,
                comment_type=comment_type,
                annotation_data=annotation_data or {}
            )
            
            # Handle annotation positioning
            if annotation_data:
                if 'timestamp_start' in annotation_data:
                    comment.timestamp_start = annotation_data['timestamp_start']
                if 'timestamp_end' in annotation_data:
                    comment.timestamp_end = annotation_data['timestamp_end']
                if 'position_x' in annotation_data:
                    comment.position_x = annotation_data['position_x']
                if 'position_y' in annotation_data:
                    comment.position_y = annotation_data['position_y']
            
            # Save comment
            self.db_session.add(comment)
            await self.db_session.commit()
            await self.db_session.refresh(comment)
            
            # Notify relevant users
            asyncio.create_task(self._notify_comment_stakeholders(comment))
            
            logger.info(f"Comment added to content {content_id} by {user_id}")
            
            return comment
            
        except Exception as e:
            await self.db_session.rollback()
            logger.error(f"Failed to add comment to content {content_id}: {str(e)}")
            raise
    
    async def grant_content_access(
        self,
        content_id: str,
        user_id: str,
        granted_by: str,
        access_level: AccessLevel,
        expires_at: datetime = None
    ) -> bool:
        """
        Grant user access to content with specific permissions.
        
        Args:
            content_id: Content identifier
            user_id: User to grant access to
            granted_by: User granting access
            access_level: Level of access to grant
            expires_at: Optional expiration date
            
        Returns:
            Success status
        """
        try:
            # Get content and check admin permissions
            content = await self.get_content(content_id, granted_by)
            if not content:
                return False
            
            if not await self._check_admin_permission(content.id, granted_by):
                raise PermissionError("Insufficient permissions to grant access")
            
            # Check if access already exists
            existing_access = await self.db_session.query(ContentAccess)\
                .filter(
                    ContentAccess.content_id == content.id,
                    ContentAccess.user_id == uuid.UUID(user_id)
                )\
                .first()
            
            if existing_access:
                # Update existing access
                existing_access.access_level = access_level
                existing_access.granted_by = uuid.UUID(granted_by)
                existing_access.granted_at = datetime.utcnow()
                existing_access.expires_at = expires_at
                existing_access.updated_at = datetime.utcnow()
            else:
                # Create new access record
                access_permissions = self._get_permissions_for_level(access_level)
                
                content_access = ContentAccess(
                    content_id=content.id,
                    user_id=uuid.UUID(user_id),
                    access_level=access_level,
                    granted_by=uuid.UUID(granted_by),
                    expires_at=expires_at,
                    **access_permissions
                )
                
                self.db_session.add(content_access)
            
            await self.db_session.commit()
            
            # Clear access cache
            if self.redis_client:
                await self.redis_client.delete(f"content_access:{content.id}:{user_id}")
            
            logger.info(f"Access granted to user {user_id} for content {content_id}")
            
            return True
            
        except Exception as e:
            await self.db_session.rollback()
            logger.error(f"Failed to grant content access: {str(e)}")
            return False
    
    async def list_project_content(
        self,
        project_id: str,
        user_id: str,
        content_type: ContentType = None,
        status: ContentStatus = None,
        limit: int = 50,
        offset: int = 0
    ) -> Tuple[List[SharedContent], int]:
        """
        List content for a project with filtering and access control.
        
        Args:
            project_id: Project UUID
            user_id: Requesting user ID
            content_type: Filter by content type
            status: Filter by status
            limit: Results limit
            offset: Results offset
            
        Returns:
            Tuple of (content list, total count)
        """
        try:
            # Base query with access control
            query = self.db_session.query(SharedContent)\
                .filter(SharedContent.project_id == uuid.UUID(project_id))
            
            # Apply filters
            if content_type:
                query = query.filter(SharedContent.content_type == content_type)
            
            if status:
                query = query.filter(SharedContent.status == status)
            
            # Filter by access permissions
            accessible_content_ids = await self._get_accessible_content_ids(user_id, project_id)
            if accessible_content_ids:
                query = query.filter(SharedContent.id.in_(accessible_content_ids))
            
            # Get total count
            total_count = await query.count()
            
            # Apply pagination and ordering
            content_list = await query\
                .order_by(SharedContent.updated_at.desc())\
                .offset(offset)\
                .limit(limit)\
                .all()
            
            return content_list, total_count
            
        except Exception as e:
            logger.error(f"Failed to list project content: {str(e)}")
            return [], 0
    
    async def get_content_analytics(self, content_id: str) -> Dict[str, Any]:
        """
        Get comprehensive content analytics and insights.
        
        Args:
            content_id: Content identifier
            
        Returns:
            Analytics data dictionary
        """
        try:
            content = await self.get_content(content_id)
            if not content:
                return {}
            
            # Get access statistics
            access_stats = await self._calculate_access_statistics(content.id)
            
            # Get comment statistics
            comment_stats = await self._calculate_comment_statistics(content.id)
            
            # Get version history
            version_history = await self._get_version_history(content.id)
            
            analytics = {
                'basic_info': {
                    'content_id': content.content_id,
                    'title': content.title,
                    'type': content.content_type.value,
                    'format': content.content_format.value if content.content_format else None,
                    'status': content.status.value,
                    'file_size_mb': round(content.file_size_bytes / (1024 * 1024), 2) if content.file_size_bytes else 0
                },
                'engagement': {
                    'view_count': content.view_count,
                    'download_count': content.download_count,
                    'share_count': content.share_count,
                    'comment_count': comment_stats.get('total_comments', 0),
                    'last_accessed': content.last_accessed.isoformat() if content.last_accessed else None
                },
                'access_analytics': access_stats,
                'comment_analytics': comment_stats,
                'version_info': {
                    'current_version': content.version,
                    'is_latest': content.is_latest_version,
                    'version_history': version_history
                },
                'technical_specs': content.technical_specs or {},
                'ai_analysis': content.ai_features or {},
                'quality_metrics': {
                    'quality_score': float(content.quality_score) if content.quality_score else None,
                    'content_warnings': content.content_warnings or [],
                    'moderation_status': content.moderation_status
                }
            }
            
            return analytics
            
        except Exception as e:
            logger.error(f"Failed to get content analytics for {content_id}: {str(e)}")
            return {}
    
    # Private helper methods
    
    def _generate_content_id(self, content_type: ContentType) -> str:
        """Generate unique content identifier"""
        type_prefix = {
            ContentType.AUDIO: 'AUD',
            ContentType.VIDEO: 'VID',
            ContentType.IMAGE: 'IMG',
            ContentType.TEXT: 'TXT',
            ContentType.DOCUMENT: 'DOC',
            ContentType.ARCHIVE: 'ARC',
            ContentType.DESIGN: 'DES',
            ContentType.SCRIPT: 'SCR',
            ContentType.LYRICS: 'LYR',
            ContentType.NOTES: 'NOT'
        }
        
        prefix = type_prefix.get(content_type, 'GEN')
        timestamp = datetime.utcnow().strftime('%Y%m%d%H%M%S')
        random_suffix = str(uuid.uuid4())[:8].upper()
        
        return f"{prefix}-{timestamp}-{random_suffix}"
    
    def _generate_storage_path(self, content_id: str, filename: str) -> str:
        """Generate S3 storage path"""
        date_path = datetime.utcnow().strftime('%Y/%m/%d')
        safe_filename = self._sanitize_filename(filename)
        return f"content/{date_path}/{content_id}/{safe_filename}"
    
    def _sanitize_filename(self, filename: str) -> str:
        """Sanitize filename for safe storage"""
        import re
        # Remove or replace unsafe characters
        safe_name = re.sub(r'[^\w\-_\.]', '_', filename)
        return safe_name[:100]  # Limit length
    
    async def _upload_to_s3(self, file_data: bytes, storage_path: str) -> str:
        """Upload file to S3 storage"""
        try:
            response = self.s3_client.put_object(
                Bucket=self.default_bucket,
                Key=storage_path,
                Body=file_data,
                ServerSideEncryption='AES256'
            )
            
            return storage_path
            
        except ClientError as e:
            logger.error(f"Failed to upload to S3: {str(e)}")
            raise
    
    def _generate_cdn_url(self, s3_key: str) -> str:
        """Generate CDN URL for content"""
        return f"https://cdn.ia-influencer.com/{s3_key}"
    
    def _detect_content_format(self, filename: str, file_data: bytes) -> Tuple[ContentFormat, str]:
        """Detect content format and MIME type"""
        mime_type, _ = mimetypes.guess_type(filename)
        file_ext = Path(filename).suffix.lower()
        
        # Map extensions to ContentFormat
        format_mapping = {
            '.mp3': ContentFormat.MP3,
            '.wav': ContentFormat.WAV,
            '.flac': ContentFormat.FLAC,
            '.mp4': ContentFormat.MP4,
            '.avi': ContentFormat.AVI,
            '.mov': ContentFormat.MOV,
            '.jpg': ContentFormat.JPEG,
            '.jpeg': ContentFormat.JPEG,
            '.png': ContentFormat.PNG,
            '.gif': ContentFormat.GIF,
            '.pdf': ContentFormat.PDF,
            '.docx': ContentFormat.DOCX,
            '.txt': ContentFormat.TXT,
            '.md': ContentFormat.MD,
            '.html': ContentFormat.HTML
        }
        
        content_format = format_mapping.get(file_ext)
        
        return content_format, mime_type or 'application/octet-stream'
    
    async def _extract_content_metadata(self, file_data: bytes, content_format: ContentFormat) -> Dict[str, Any]:
        """Extract format-specific metadata"""
        metadata = {}
        
        # This would integrate with libraries like:
        # - mutagen for audio metadata
        # - Pillow for image metadata
        # - cv2 for video metadata
        # - python-docx for document metadata
        
        # Placeholder implementation
        metadata['file_size'] = len(file_data)
        metadata['extracted_at'] = datetime.utcnow().isoformat()
        
        return metadata
    
    async def _analyze_technical_specs(self, file_data: bytes, content_format: ContentFormat) -> Dict[str, Any]:
        """Analyze technical specifications"""
        specs = {}
        
        # This would analyze:
        # - Audio: bitrate, sample rate, channels, duration
        # - Video: resolution, frame rate, bitrate, duration, codec
        # - Image: dimensions, color depth, compression
        # - Document: page count, word count, language
        
        # Placeholder implementation
        specs['analyzed_at'] = datetime.utcnow().isoformat()
        
        return specs
    
    def _default_access_permissions(self, access_level: AccessLevel) -> Dict[str, Any]:
        """Generate default access permissions"""
        return {
            'default_access_level': access_level.value,
            'inheritance_enabled': True,
            'auto_grant_team_members': True,
            'require_approval_for_external': True
        }
    
    def _default_sharing_settings(self) -> Dict[str, Any]:
        """Generate default sharing settings"""
        return {
            'public_sharing_enabled': False,
            'link_sharing_enabled': True,
            'download_tracking_enabled': True,
            'watermark_enabled': False,
            'expiration_enabled': False
        }
    
    async def _create_owner_access(self, content_id: uuid.UUID, owner_id: str):
        """Create owner access record"""
        owner_access = ContentAccess(
            content_id=content_id,
            user_id=uuid.UUID(owner_id),
            access_level=AccessLevel.OWNER,
            granted_by=uuid.UUID(owner_id),
            can_view=True,
            can_edit=True,
            can_comment=True,
            can_download=True,
            can_share=True,
            can_delete=True
        )
        
        self.db_session.add(owner_access)
    
    def _get_permissions_for_level(self, access_level: AccessLevel) -> Dict[str, bool]:
        """Get permissions dictionary for access level"""
        permissions = {
            AccessLevel.OWNER: {
                'can_view': True,
                'can_edit': True,
                'can_comment': True,
                'can_download': True,
                'can_share': True,
                'can_delete': True
            },
            AccessLevel.EDITOR: {
                'can_view': True,
                'can_edit': True,
                'can_comment': True,
                'can_download': True,
                'can_share': False,
                'can_delete': False
            },
            AccessLevel.VIEWER: {
                'can_view': True,
                'can_edit': False,
                'can_comment': True,
                'can_download': True,
                'can_share': False,
                'can_delete': False
            },
            AccessLevel.COMMENTER: {
                'can_view': True,
                'can_edit': False,
                'can_comment': True,
                'can_download': False,
                'can_share': False,
                'can_delete': False
            },
            AccessLevel.RESTRICTED: {
                'can_view': True,
                'can_edit': False,
                'can_comment': False,
                'can_download': False,
                'can_share': False,
                'can_delete': False
            }
        }
        
        return permissions.get(access_level, permissions[AccessLevel.RESTRICTED])
    
    # Additional helper methods for caching, access control, etc.
    # would be implemented here...

# Export main classes
__all__ = [
    'SharedContent',
    'ContentAccess',
    'ContentComment',
    'ContentType',
    'ContentStatus',
    'AccessLevel',
    'ContentFormat',
    'ContentUploadRequest',
    'ContentUpdateRequest',
    'SharedContentManager'
]
