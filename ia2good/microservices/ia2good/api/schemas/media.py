"""
Media Pydantic Schemas
"""

from pydantic import BaseModel, Field, field_validator
from typing import Optional, List, Dict, Any
from datetime import datetime
from uuid import UUID
import enum


class MediaType(str, enum.Enum):
    """Media type enum"""
    photo = "photo"
    video = "video"
    live_stream = "live_stream"
    audio = "audio"
    document = "document"


class MediaStatus(str, enum.Enum):
    """Media processing status"""
    uploading = "uploading"
    processing = "processing"
    ready = "ready"
    failed = "failed"
    deleted = "deleted"


class StreamStatus(str, enum.Enum):
    """Live stream status"""
    scheduled = "scheduled"
    live = "live"
    ended = "ended"
    cancelled = "cancelled"


class StreamQuality(str, enum.Enum):
    """Stream quality levels"""
    low = "low"          # 360p
    medium = "medium"    # 480p
    high = "high"        # 720p
    hd = "hd"           # 1080p


# ========== MEDIA SCHEMAS ==========

class MediaUploadRequest(BaseModel):
    """Request for direct file upload"""
    title: Optional[str] = None
    description: Optional[str] = None
    entity_type: Optional[str] = None  # issue, event, campaign, case, profile
    entity_id: Optional[UUID] = None
    tags: Optional[List[str]] = []
    is_public: bool = True


class MediaUploadResponse(BaseModel):
    """Response after media upload"""
    id: UUID
    file_url: str
    thumbnail_url: Optional[str] = None
    type: MediaType
    status: MediaStatus
    file_size: int
    mime_type: str
    created_at: datetime
    
    class Config:
        from_attributes = True


class MediaResponse(BaseModel):
    """Complete media information"""
    id: UUID
    type: MediaType
    status: MediaStatus
    title: Optional[str] = None
    description: Optional[str] = None
    original_filename: str
    file_url: str
    thumbnail_url: Optional[str] = None
    mime_type: str
    file_size: int
    duration: Optional[int] = None
    width: Optional[int] = None
    height: Optional[int] = None
    variants: Optional[Dict[str, str]] = None
    uploaded_by: UUID
    entity_type: Optional[str] = None
    entity_id: Optional[UUID] = None
    views_count: int = 0
    downloads_count: int = 0
    tags: Optional[List[str]] = []
    is_public: bool = True
    is_featured: bool = False
    moderation_status: str = "pending"
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class MediaUpdate(BaseModel):
    """Update media information"""
    title: Optional[str] = None
    description: Optional[str] = None
    tags: Optional[List[str]] = None
    is_public: Optional[bool] = None


class MediaListFilter(BaseModel):
    """Filter for media listing"""
    type: Optional[MediaType] = None
    entity_type: Optional[str] = None
    entity_id: Optional[UUID] = None
    uploaded_by: Optional[UUID] = None
    is_public: Optional[bool] = None
    status: Optional[MediaStatus] = None
    skip: int = 0
    limit: int = 20


# ========== LIVE STREAM SCHEMAS ==========

class LiveStreamCreate(BaseModel):
    """Create a live stream"""
    title: str = Field(..., min_length=3, max_length=255)
    description: Optional[str] = None
    entity_type: Optional[str] = None  # event, campaign, etc.
    entity_id: Optional[UUID] = None
    scheduled_start: Optional[datetime] = None
    scheduled_end: Optional[datetime] = None
    max_quality: StreamQuality = StreamQuality.high
    enable_recording: bool = True
    enable_chat: bool = True
    is_public: bool = True
    password: Optional[str] = None  # For private streams
    co_streamers: Optional[List[UUID]] = []
    
    @field_validator('scheduled_end')
    @classmethod
    def validate_end_after_start(cls, v, info):
        if v and info.data.get('scheduled_start') and v <= info.data['scheduled_start']:
            raise ValueError('scheduled_end must be after scheduled_start')
        return v


class LiveStreamUpdate(BaseModel):
    """Update a live stream"""
    title: Optional[str] = Field(None, min_length=3, max_length=255)
    description: Optional[str] = None
    scheduled_start: Optional[datetime] = None
    scheduled_end: Optional[datetime] = None
    enable_chat: Optional[bool] = None
    enable_recording: Optional[bool] = None
    is_public: Optional[bool] = None


class LiveStreamResponse(BaseModel):
    """Live stream information"""
    id: UUID
    title: str
    description: Optional[str] = None
    status: StreamStatus
    stream_key: Optional[str] = None  # Only for streamer
    stream_url: Optional[str] = None  # Only for streamer (RTMP)
    playback_url: str
    embed_code: Optional[str] = None
    thumbnail_url: Optional[str] = None
    scheduled_start: Optional[datetime] = None
    scheduled_end: Optional[datetime] = None
    actual_start: Optional[datetime] = None
    actual_end: Optional[datetime] = None
    streamer_id: UUID
    entity_type: Optional[str] = None
    entity_id: Optional[UUID] = None
    current_viewers: int = 0
    peak_viewers: int = 0
    total_views: int = 0
    likes_count: int = 0
    comments_count: int = 0
    recording_url: Optional[str] = None
    is_public: bool = True
    is_featured: bool = False
    created_at: datetime
    
    class Config:
        from_attributes = True


class LiveStreamListResponse(BaseModel):
    """Simplified stream list item"""
    id: UUID
    title: str
    description: Optional[str] = None
    status: StreamStatus
    playback_url: str
    thumbnail_url: Optional[str] = None
    scheduled_start: Optional[datetime] = None
    streamer_id: UUID
    current_viewers: int = 0
    is_public: bool = True
    is_featured: bool = False
    created_at: datetime
    
    class Config:
        from_attributes = True


class StreamCommentCreate(BaseModel):
    """Create a stream comment"""
    content: str = Field(..., min_length=1, max_length=500)


class StreamCommentResponse(BaseModel):
    """Stream comment information"""
    id: UUID
    stream_id: UUID
    user_id: UUID
    content: str
    is_pinned: bool = False
    likes_count: int = 0
    created_at: datetime
    
    class Config:
        from_attributes = True


class StreamReactionCreate(BaseModel):
    """Create a stream reaction"""
    reaction_type: str = Field(..., pattern="^(like|love|wow|sad|angry)$")


class StreamStatsResponse(BaseModel):
    """Stream statistics"""
    stream_id: UUID
    current_viewers: int
    peak_viewers: int
    total_views: int
    likes_count: int
    comments_count: int
    average_watch_time: Optional[int] = None  # seconds
    engagement_rate: Optional[float] = None


# ========== PRESIGNED URL ==========

class PresignedUrlRequest(BaseModel):
    """Request for presigned upload URL"""
    filename: str
    content_type: str
    file_size: int
    entity_type: Optional[str] = None
    entity_id: Optional[UUID] = None


class PresignedUrlResponse(BaseModel):
    """Presigned URL for upload"""
    upload_url: str
    media_id: UUID
    expires_in: int = 3600  # seconds
    
    class Config:
        from_attributes = True
