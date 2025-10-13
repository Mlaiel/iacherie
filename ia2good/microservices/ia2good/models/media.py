"""
Media Models
Handles photos, videos, and live streaming for the IA2GOOD platform
"""

from sqlalchemy import Column, String, Integer, DateTime, Boolean, Text, Enum as SQLEnum, JSON, ARRAY, Float
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
import uuid
import enum

from database import Base


class MediaType(enum.Enum):
    """Media type enum"""
    photo = "photo"
    video = "video"
    live_stream = "live_stream"
    audio = "audio"
    document = "document"


class MediaStatus(enum.Enum):
    """Media processing status"""
    uploading = "uploading"
    processing = "processing"
    ready = "ready"
    failed = "failed"
    deleted = "deleted"


class StreamStatus(enum.Enum):
    """Live stream status"""
    scheduled = "scheduled"
    live = "live"
    ended = "ended"
    cancelled = "cancelled"


class StreamQuality(enum.Enum):
    """Stream quality levels"""
    low = "low"          # 360p
    medium = "medium"    # 480p
    high = "high"        # 720p
    hd = "hd"           # 1080p


class Media(Base):
    """Media files (photos, videos, documents)"""
    __tablename__ = "ia2good_media"
    
    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Media info
    type = Column(SQLEnum(MediaType, values_callable=lambda x: [e.value for e in x]), nullable=False)
    status = Column(
        SQLEnum(MediaStatus, values_callable=lambda x: [e.value for e in x]),
        default=MediaStatus.uploading.value,
        nullable=False
    )
    title = Column(String(255))
    description = Column(Text)
    
    # File details
    original_filename = Column(String(500), nullable=False)
    file_key = Column(String(500), nullable=False, unique=True)  # S3 key
    file_url = Column(String(1000))  # Public URL or CDN URL
    thumbnail_url = Column(String(1000))  # Thumbnail for videos/photos
    
    # Technical details
    mime_type = Column(String(100))
    file_size = Column(Integer)  # bytes
    duration = Column(Integer)  # seconds (for videos/audio)
    width = Column(Integer)  # pixels (for images/videos)
    height = Column(Integer)  # pixels (for images/videos)
    bitrate = Column(Integer)  # kbps (for videos)
    codec = Column(String(50))  # video codec
    
    # Processing info
    processed_at = Column(DateTime(timezone=True))
    processing_error = Column(Text)
    
    # Variants (different sizes/qualities)
    variants = Column(JSON)  # {"small": "url", "medium": "url", "large": "url"}
    
    # Owner and context
    uploaded_by = Column(UUID(as_uuid=True), nullable=False)  # user_id
    entity_type = Column(String(50))  # issue, event, campaign, case, profile, etc.
    entity_id = Column(UUID(as_uuid=True))  # FK to related entity
    
    # Engagement
    views_count = Column(Integer, default=0)
    downloads_count = Column(Integer, default=0)
    
    # Tags and metadata
    tags = Column(ARRAY(String))
    extra_metadata = Column(JSON)  # EXIF data, etc.
    
    # Moderation
    is_public = Column(Boolean, default=True)
    is_featured = Column(Boolean, default=False)
    moderation_status = Column(String(20), default="pending")  # pending, approved, rejected
    moderated_at = Column(DateTime(timezone=True))
    moderated_by = Column(UUID(as_uuid=True))
    moderation_notes = Column(Text)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    deleted_at = Column(DateTime(timezone=True))
    
    def __repr__(self):
        return f"<Media {self.id} - {self.type} - {self.original_filename}>"


class LiveStream(Base):
    """Live streaming sessions"""
    __tablename__ = "ia2good_live_streams"
    
    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Stream info
    title = Column(String(255), nullable=False)
    description = Column(Text)
    status = Column(
        SQLEnum(StreamStatus, values_callable=lambda x: [e.value for e in x]),
        default=StreamStatus.scheduled.value,
        nullable=False
    )
    
    # Streaming details
    stream_key = Column(String(100), unique=True, nullable=False)  # Secret key for OBS
    stream_url = Column(String(500))  # RTMP ingest URL
    playback_url = Column(String(500))  # HLS/DASH playback URL
    embed_code = Column(Text)  # Embed HTML code
    
    # Quality settings
    max_quality = Column(
        SQLEnum(StreamQuality, values_callable=lambda x: [e.value for e in x]),
        default=StreamQuality.high.value
    )
    enable_recording = Column(Boolean, default=True)
    enable_chat = Column(Boolean, default=True)
    
    # Scheduling
    scheduled_start = Column(DateTime(timezone=True))
    scheduled_end = Column(DateTime(timezone=True))
    actual_start = Column(DateTime(timezone=True))
    actual_end = Column(DateTime(timezone=True))
    
    # Streamer
    streamer_id = Column(UUID(as_uuid=True), nullable=False)
    co_streamers = Column(ARRAY(UUID(as_uuid=True)))  # Multiple streamers
    
    # Context
    entity_type = Column(String(50))  # event, campaign, case, etc.
    entity_id = Column(UUID(as_uuid=True))
    
    # Engagement
    current_viewers = Column(Integer, default=0)
    peak_viewers = Column(Integer, default=0)
    total_views = Column(Integer, default=0)
    likes_count = Column(Integer, default=0)
    comments_count = Column(Integer, default=0)
    
    # Recording
    recording_url = Column(String(500))  # URL of recorded stream
    recording_duration = Column(Integer)  # seconds
    recording_size = Column(Integer)  # bytes
    
    # Privacy
    is_public = Column(Boolean, default=True)
    is_featured = Column(Boolean, default=False)
    password_protected = Column(Boolean, default=False)
    password_hash = Column(String(255))
    allowed_viewers = Column(ARRAY(UUID(as_uuid=True)))  # Whitelist
    
    # Technical details
    bitrate = Column(Integer)  # kbps
    resolution = Column(String(20))  # "1920x1080"
    fps = Column(Integer)  # frames per second
    codec = Column(String(50))
    
    # Moderation
    moderation_enabled = Column(Boolean, default=True)
    banned_words = Column(ARRAY(String))
    moderator_ids = Column(ARRAY(UUID(as_uuid=True)))
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    def __repr__(self):
        return f"<LiveStream {self.id} - {self.title} - {self.status}>"


class StreamComment(Base):
    """Comments on live streams"""
    __tablename__ = "ia2good_stream_comments"
    
    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Relations
    stream_id = Column(UUID(as_uuid=True), nullable=False)
    user_id = Column(UUID(as_uuid=True), nullable=False)
    
    # Content
    content = Column(Text, nullable=False)
    is_pinned = Column(Boolean, default=False)
    
    # Moderation
    is_deleted = Column(Boolean, default=False)
    deleted_by = Column(UUID(as_uuid=True))
    deleted_at = Column(DateTime(timezone=True))
    
    # Engagement
    likes_count = Column(Integer, default=0)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    def __repr__(self):
        return f"<StreamComment {self.id} on stream {self.stream_id}>"


class StreamReaction(Base):
    """Live reactions during stream (likes, hearts, etc.)"""
    __tablename__ = "ia2good_stream_reactions"
    
    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Relations
    stream_id = Column(UUID(as_uuid=True), nullable=False)
    user_id = Column(UUID(as_uuid=True), nullable=False)
    
    # Reaction type
    reaction_type = Column(String(20), nullable=False)  # like, love, wow, sad, angry
    
    # Timestamp
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    def __repr__(self):
        return f"<StreamReaction {self.reaction_type} by {self.user_id}>"
