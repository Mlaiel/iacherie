"""
Media API Routes
Handles photo/video upload, live streaming, and media management
"""

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, status
from fastapi.responses import StreamingResponse
from sqlalchemy import select, and_, or_, func as sql_func
from typing import Optional, List
from uuid import UUID
import os
import sys
import secrets
import io
from datetime import datetime

from database import get_db
from models.media import Media, LiveStream, StreamComment, StreamReaction, MediaType, MediaStatus, StreamStatus
from api.schemas.media import (
    MediaUploadRequest, MediaUploadResponse, MediaResponse, MediaUpdate, MediaListFilter,
    LiveStreamCreate, LiveStreamUpdate, LiveStreamResponse, LiveStreamListResponse,
    StreamCommentCreate, StreamCommentResponse, StreamReactionCreate, StreamStatsResponse,
    PresignedUrlRequest, PresignedUrlResponse
)
from api.dependencies import get_current_user

# Import file storage services
from services.file_storage.s3_handler import S3Handler
from services.file_storage.file_validator import FileValidator
from services.media_processor import media_processor


router = APIRouter()


# Initialize handlers
s3_handler = S3Handler()
file_validator = FileValidator()


# ========== HELPER FUNCTIONS ==========

def media_to_dict(media: Media, include_sensitive: bool = False) -> dict:
    """Convert Media model to dict"""
    data = {
        "id": str(media.id),
        "type": media.type,
        "status": media.status,
        "title": media.title,
        "description": media.description,
        "original_filename": media.original_filename,
        "file_url": media.file_url,
        "thumbnail_url": media.thumbnail_url,
        "mime_type": media.mime_type,
        "file_size": media.file_size,
        "duration": media.duration,
        "width": media.width,
        "height": media.height,
        "variants": media.variants,
        "uploaded_by": str(media.uploaded_by),
        "entity_type": media.entity_type,
        "entity_id": str(media.entity_id) if media.entity_id else None,
        "views_count": media.views_count,
        "downloads_count": media.downloads_count,
        "tags": media.tags,
        "is_public": media.is_public,
        "is_featured": media.is_featured,
        "moderation_status": media.moderation_status,
        "created_at": media.created_at,
        "updated_at": media.updated_at
    }
    
    if include_sensitive:
        data["file_key"] = media.file_key
        data["processing_error"] = media.processing_error
    
    return data


def stream_to_dict(stream: LiveStream, user_id: Optional[str] = None) -> dict:
    """Convert LiveStream model to dict"""
    is_owner = user_id and str(stream.streamer_id) == user_id
    
    data = {
        "id": str(stream.id),
        "title": stream.title,
        "description": stream.description,
        "status": stream.status,
        "playback_url": stream.playback_url,
        "embed_code": stream.embed_code,
        "scheduled_start": stream.scheduled_start,
        "scheduled_end": stream.scheduled_end,
        "actual_start": stream.actual_start,
        "actual_end": stream.actual_end,
        "streamer_id": str(stream.streamer_id),
        "entity_type": stream.entity_type,
        "entity_id": str(stream.entity_id) if stream.entity_id else None,
        "current_viewers": stream.current_viewers,
        "peak_viewers": stream.peak_viewers,
        "total_views": stream.total_views,
        "likes_count": stream.likes_count,
        "comments_count": stream.comments_count,
        "recording_url": stream.recording_url,
        "is_public": stream.is_public,
        "is_featured": stream.is_featured,
        "created_at": stream.created_at
    }
    
    # Only show sensitive data to stream owner
    if is_owner:
        data["stream_key"] = stream.stream_key
        data["stream_url"] = stream.stream_url
    
    return data


# ========== MEDIA ENDPOINTS ==========

@router.post("/media/upload", response_model=MediaUploadResponse)
async def upload_media(
    file: UploadFile = File(...),
    title: Optional[str] = Form(None),
    description: Optional[str] = Form(None),
    entity_type: Optional[str] = Form(None),
    entity_id: Optional[str] = Form(None),
    tags: Optional[str] = Form(None),  # Comma-separated
    is_public: bool = Form(True),
    auto_process: bool = Form(True),  # NEW: Enable intelligent processing
    current_user: dict = Depends(get_current_user),
    db = Depends(get_db)
):
    """
    Upload a media file with intelligent automatic processing
    
    🚀 NEW: Now accepts ALL file formats!
    
    The system automatically:
    - ✅ Accepts any file format (no restrictions)
    - ✅ Detects media type automatically
    - ✅ Compresses images to WebP
    - ✅ Generates multiple sizes (small, medium, large)
    - ✅ Creates thumbnails automatically
    - ✅ Transcodes videos to multiple qualities (async)
    - ✅ Extracts and removes EXIF data for privacy
    - ✅ Optimizes for web delivery
    
    Supports:
    - Images: ANY format → auto-converted to WebP
    - Videos: ANY format → auto-transcoded to MP4 (H.264)
    - Audio: ANY format → stored as-is
    - Documents: ANY format → stored as-is
    
    Processing is automatic and happens in the background!
    """
    try:
        # Read file content
        file_content = await file.read()
        file_size = len(file_content)
        
        # Create media record immediately (status: uploading)
        media = Media(
            type=MediaType.photo.value,  # Will be updated after detection
            status=MediaStatus.uploading.value,
            title=title or file.filename,
            description=description,
            original_filename=file.filename,
            file_key=f"temp/{file.filename}",  # Temporary
            file_size=file_size,
            uploaded_by=current_user['user_id'],
            entity_type=entity_type,
            entity_id=UUID(entity_id) if entity_id else None,
            tags=[tag.strip() for tag in tags.split(',')] if tags else [],
            is_public=is_public
        )
        
        db.add(media)
        db.commit()
        db.refresh(media)
        
        media_id = str(media.id)
        
        # Step 1: Upload original file to S3
        file_data = io.BytesIO(file_content)
        upload_result = await s3_handler.upload_file(
            file_data=file_data,
            file_name=file.filename,
            content_type=file.content_type or 'application/octet-stream',
            folder=f"media/original/{media_id}"
        )
        
        if not upload_result.get('success'):
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Upload failed: {upload_result.get('error', 'Unknown error')}"
            )
        
        # Update with original file URL
        media.file_key = upload_result['file_key']
        media.file_url = upload_result['file_url']
        media.mime_type = upload_result['content_type']
        
        # Step 2: Intelligent processing (if enabled)
        if auto_process:
            media.status = MediaStatus.processing.value
            db.commit()
            
            try:
                # Process media intelligently
                processing_result = await media_processor.process_media(
                    file_content=file_content,
                    filename=file.filename,
                    media_id=media_id
                )
                
                # Update media type based on detection
                detected_category = processing_result.get('category', 'photo')
                media_type_map = {
                    'image': MediaType.photo.value,
                    'video': MediaType.video.value,
                    'audio': MediaType.audio.value,
                    'document': MediaType.document.value,
                    'other': MediaType.document.value
                }
                media.type = media_type_map.get(detected_category, MediaType.photo.value)
                
                # Update with processing results
                if 'width' in processing_result:
                    media.width = processing_result['width']
                if 'height' in processing_result:
                    media.height = processing_result['height']
                if 'duration' in processing_result:
                    media.duration = processing_result['duration']
                
                # Upload processed variants
                if 'processed_files' in processing_result:
                    variants_urls = {}
                    
                    for variant_name, variant_data in processing_result['processed_files'].items():
                        if variant_name == 'optimized':
                            continue  # Skip, we'll use variants
                        
                        variant_file = io.BytesIO(variant_data)
                        variant_upload = await s3_handler.upload_file(
                            file_data=variant_file,
                            file_name=f"{variant_name}.webp",
                            content_type='image/webp',
                            folder=f"media/{media_id}"
                        )
                        
                        if variant_upload.get('success'):
                            variants_urls[variant_name] = variant_upload['file_url']
                    
                    # Store variants
                    if 'variants' in processing_result and isinstance(processing_result['variants'], dict):
                        for variant_name, variant_info in processing_result['variants'].items():
                            if variant_name in variants_urls:
                                variant_info['url'] = variants_urls[variant_name]
                        
                        media.variants = processing_result['variants']
                    
                    # Set thumbnail URL
                    if 'thumbnail' in variants_urls:
                        media.thumbnail_url = variants_urls['thumbnail']
                
                # Mark as ready
                media.status = MediaStatus.ready.value
                media.processed_at = datetime.utcnow()
                
            except Exception as proc_error:
                # Processing failed, but original file is uploaded
                media.status = MediaStatus.failed.value
                media.processing_error = str(proc_error)
                print(f"Processing error for {media_id}: {proc_error}")
        else:
            # No processing, mark as ready immediately
            media.status = MediaStatus.ready.value
            media.processed_at = datetime.utcnow()
        
        db.commit()
        db.refresh(media)
        
        return MediaUploadResponse(
            id=media.id,
            file_url=media.file_url,
            thumbnail_url=media.thumbnail_url,
            type=media.type,
            status=media.status,
            file_size=media.file_size,
            mime_type=media.mime_type,
            created_at=media.created_at
        )
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Upload failed: {str(e)}"
        )


@router.get("/media", response_model=List[MediaResponse])
async def list_media(
    type: Optional[str] = None,
    entity_type: Optional[str] = None,
    entity_id: Optional[str] = None,
    uploaded_by: Optional[str] = None,
    is_public: Optional[bool] = None,
    status: Optional[str] = None,
    skip: int = 0,
    limit: int = 20,
    db = Depends(get_db)
):
    """
    List media files with filters
    """
    query = select(Media).where(Media.deleted_at.is_(None))
    
    if type:
        query = query.where(Media.type == type)
    if entity_type:
        query = query.where(Media.entity_type == entity_type)
    if entity_id:
        query = query.where(Media.entity_id == UUID(entity_id))
    if uploaded_by:
        query = query.where(Media.uploaded_by == UUID(uploaded_by))
    if is_public is not None:
        query = query.where(Media.is_public == is_public)
    if status:
        query = query.where(Media.status == status)
    
    query = query.order_by(Media.created_at.desc()).offset(skip).limit(limit)
    
    result = db.execute(query)
    media_list = result.scalars().all()
    
    return [media_to_dict(media) for media in media_list]


@router.get("/media/{media_id}", response_model=MediaResponse)
async def get_media(
    media_id: UUID,
    db = Depends(get_db)
):
    """
    Get media details by ID
    """
    result = db.execute(
        select(Media).where(
            and_(Media.id == media_id, Media.deleted_at.is_(None))
        )
    )
    media = result.scalar_one_or_none()
    
    if not media:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Media not found"
        )
    
    # Increment views
    media.views_count += 1
    db.commit()
    
    return media_to_dict(media)


@router.put("/media/{media_id}", response_model=MediaResponse)
async def update_media(
    media_id: UUID,
    update_data: MediaUpdate,
    current_user: dict = Depends(get_current_user),
    db = Depends(get_db)
):
    """
    Update media information (owner only)
    """
    result = db.execute(
        select(Media).where(
            and_(Media.id == media_id, Media.deleted_at.is_(None))
        )
    )
    media = result.scalar_one_or_none()
    
    if not media:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Media not found"
        )
    
    # Check ownership
    if str(media.uploaded_by) != current_user['user_id']:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this media"
        )
    
    # Update fields
    if update_data.title is not None:
        media.title = update_data.title
    if update_data.description is not None:
        media.description = update_data.description
    if update_data.tags is not None:
        media.tags = update_data.tags
    if update_data.is_public is not None:
        media.is_public = update_data.is_public
    
    media.updated_at = datetime.utcnow()
    
    db.commit()
    db.refresh(media)
    
    return media_to_dict(media)


@router.delete("/media/{media_id}")
async def delete_media(
    media_id: UUID,
    current_user: dict = Depends(get_current_user),
    db = Depends(get_db)
):
    """
    Delete media (soft delete, owner only)
    """
    result = db.execute(
        select(Media).where(
            and_(Media.id == media_id, Media.deleted_at.is_(None))
        )
    )
    media = result.scalar_one_or_none()
    
    if not media:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Media not found"
        )
    
    # Check ownership or admin
    if str(media.uploaded_by) != current_user['user_id'] and 'admin' not in current_user.get('roles', []):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this media"
        )
    
    # Soft delete
    media.deleted_at = datetime.utcnow()
    media.status = MediaStatus.deleted.value
    
    db.commit()
    
    return {"message": "Media deleted successfully"}


@router.get("/media/{media_id}/download")
async def download_media(
    media_id: UUID,
    db = Depends(get_db)
):
    """
    Download media file
    """
    result = db.execute(
        select(Media).where(
            and_(Media.id == media_id, Media.deleted_at.is_(None))
        )
    )
    media = result.scalar_one_or_none()
    
    if not media:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Media not found"
        )
    
    # Increment downloads
    media.downloads_count += 1
    db.commit()
    
    # Generate presigned URL for download
    download_url = await s3_handler.generate_presigned_url(
        file_key=media.file_key,
        expiration=3600,
        operation='get_object'
    )
    
    if not download_url:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate download URL"
        )
    
    return {"download_url": download_url, "filename": media.original_filename}


# ========== LIVE STREAM ENDPOINTS ==========

@router.post("/streams", response_model=LiveStreamResponse)
async def create_stream(
    stream_data: LiveStreamCreate,
    current_user: dict = Depends(get_current_user),
    db = Depends(get_db)
):
    """
    Create a new live stream
    
    Returns stream key and RTMP URL for OBS/streaming software
    """
    # Generate unique stream key
    stream_key = secrets.token_urlsafe(32)
    
    # Generate URLs (in production, use actual streaming server)
    stream_url = f"rtmp://streaming.ia2good.com/live/{stream_key}"
    playback_url = f"https://streaming.ia2good.com/hls/{stream_key}/index.m3u8"
    embed_code = f'<iframe src="https://streaming.ia2good.com/embed/{stream_key}" width="640" height="360" frameborder="0" allowfullscreen></iframe>'
    
    # Create stream
    stream = LiveStream(
        title=stream_data.title,
        description=stream_data.description,
        stream_key=stream_key,
        stream_url=stream_url,
        playback_url=playback_url,
        embed_code=embed_code,
        max_quality=stream_data.max_quality.value,
        enable_recording=stream_data.enable_recording,
        enable_chat=stream_data.enable_chat,
        scheduled_start=stream_data.scheduled_start,
        scheduled_end=stream_data.scheduled_end,
        streamer_id=current_user['user_id'],
        co_streamers=stream_data.co_streamers or [],
        entity_type=stream_data.entity_type,
        entity_id=stream_data.entity_id,
        is_public=stream_data.is_public,
        password_protected=bool(stream_data.password)
    )
    
    # Handle password protection
    if stream_data.password:
        from passlib.hash import bcrypt
        stream.password_hash = bcrypt.hash(stream_data.password)
    
    db.add(stream)
    db.commit()
    db.refresh(stream)
    
    return stream_to_dict(stream, user_id=current_user['user_id'])


@router.get("/streams", response_model=List[LiveStreamListResponse])
async def list_streams(
    status: Optional[str] = None,
    is_live: bool = False,
    entity_type: Optional[str] = None,
    entity_id: Optional[str] = None,
    skip: int = 0,
    limit: int = 20,
    db = Depends(get_db)
):
    """
    List live streams
    """
    query = select(LiveStream).where(LiveStream.is_public == True)
    
    if status:
        query = query.where(LiveStream.status == status)
    if is_live:
        query = query.where(LiveStream.status == StreamStatus.live.value)
    if entity_type:
        query = query.where(LiveStream.entity_type == entity_type)
    if entity_id:
        query = query.where(LiveStream.entity_id == UUID(entity_id))
    
    query = query.order_by(LiveStream.created_at.desc()).offset(skip).limit(limit)
    
    result = db.execute(query)
    streams = result.scalars().all()
    
    return [stream_to_dict(stream) for stream in streams]


@router.get("/streams/{stream_id}", response_model=LiveStreamResponse)
async def get_stream(
    stream_id: UUID,
    current_user: dict = Depends(get_current_user),
    db = Depends(get_db)
):
    """
    Get stream details
    """
    result = db.execute(select(LiveStream).where(LiveStream.id == stream_id))
    stream = result.scalar_one_or_none()
    
    if not stream:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Stream not found"
        )
    
    # Increment views if stream is live
    if stream.status == StreamStatus.live.value:
        stream.total_views += 1
        stream.current_viewers += 1
        db.commit()
    
    return stream_to_dict(stream, user_id=current_user['user_id'])


@router.put("/streams/{stream_id}", response_model=LiveStreamResponse)
async def update_stream(
    stream_id: UUID,
    update_data: LiveStreamUpdate,
    current_user: dict = Depends(get_current_user),
    db = Depends(get_db)
):
    """
    Update stream (owner only)
    """
    result = db.execute(select(LiveStream).where(LiveStream.id == stream_id))
    stream = result.scalar_one_or_none()
    
    if not stream:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Stream not found"
        )
    
    # Check ownership
    if str(stream.streamer_id) != current_user['user_id']:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this stream"
        )
    
    # Update fields
    if update_data.title is not None:
        stream.title = update_data.title
    if update_data.description is not None:
        stream.description = update_data.description
    if update_data.scheduled_start is not None:
        stream.scheduled_start = update_data.scheduled_start
    if update_data.scheduled_end is not None:
        stream.scheduled_end = update_data.scheduled_end
    if update_data.enable_chat is not None:
        stream.enable_chat = update_data.enable_chat
    if update_data.enable_recording is not None:
        stream.enable_recording = update_data.enable_recording
    if update_data.is_public is not None:
        stream.is_public = update_data.is_public
    
    stream.updated_at = datetime.utcnow()
    
    db.commit()
    db.refresh(stream)
    
    return stream_to_dict(stream, user_id=current_user['user_id'])


@router.post("/streams/{stream_id}/start")
async def start_stream(
    stream_id: UUID,
    current_user: dict = Depends(get_current_user),
    db = Depends(get_db)
):
    """
    Start a live stream (owner only)
    """
    result = db.execute(select(LiveStream).where(LiveStream.id == stream_id))
    stream = result.scalar_one_or_none()
    
    if not stream:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Stream not found"
        )
    
    # Check ownership
    if str(stream.streamer_id) != current_user['user_id']:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to start this stream"
        )
    
    # Update status
    stream.status = StreamStatus.live.value
    stream.actual_start = datetime.utcnow()
    stream.current_viewers = 0
    
    db.commit()
    
    return {"message": "Stream started successfully", "status": "live"}


@router.post("/streams/{stream_id}/end")
async def end_stream(
    stream_id: UUID,
    current_user: dict = Depends(get_current_user),
    db = Depends(get_db)
):
    """
    End a live stream (owner only)
    """
    result = db.execute(select(LiveStream).where(LiveStream.id == stream_id))
    stream = result.scalar_one_or_none()
    
    if not stream:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Stream not found"
        )
    
    # Check ownership
    if str(stream.streamer_id) != current_user['user_id']:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to end this stream"
        )
    
    # Update status
    from datetime import timezone
    stream.status = StreamStatus.ended.value
    stream.actual_end = datetime.now(timezone.utc)
    stream.current_viewers = 0
    
    # Calculate duration
    if stream.actual_start:
        # Make both datetimes timezone-aware
        if stream.actual_start.tzinfo is None:
            from datetime import timezone
            stream.actual_start = stream.actual_start.replace(tzinfo=timezone.utc)
        duration = (stream.actual_end - stream.actual_start).total_seconds()
        stream.recording_duration = int(duration)
    
    db.commit()
    
    return {"message": "Stream ended successfully", "status": "ended"}


@router.post("/streams/{stream_id}/comments", response_model=StreamCommentResponse)
async def add_stream_comment(
    stream_id: UUID,
    comment_data: StreamCommentCreate,
    current_user: dict = Depends(get_current_user),
    db = Depends(get_db)
):
    """
    Add comment to live stream
    """
    # Check if stream exists
    result = db.execute(select(LiveStream).where(LiveStream.id == stream_id))
    stream = result.scalar_one_or_none()
    
    if not stream:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Stream not found"
        )
    
    # Create comment
    comment = StreamComment(
        stream_id=stream_id,
        user_id=current_user['user_id'],
        content=comment_data.content
    )
    
    db.add(comment)
    
    # Increment comments count
    stream.comments_count += 1
    
    db.commit()
    db.refresh(comment)
    
    return {
        "id": comment.id,
        "stream_id": comment.stream_id,
        "user_id": comment.user_id,
        "content": comment.content,
        "is_pinned": comment.is_pinned,
        "likes_count": comment.likes_count,
        "created_at": comment.created_at
    }


@router.get("/streams/{stream_id}/comments", response_model=List[StreamCommentResponse])
async def get_stream_comments(
    stream_id: UUID,
    skip: int = 0,
    limit: int = 50,
    db = Depends(get_db)
):
    """
    Get stream comments
    """
    query = select(StreamComment).where(
        and_(
            StreamComment.stream_id == stream_id,
            StreamComment.is_deleted == False
        )
    ).order_by(StreamComment.created_at.desc()).offset(skip).limit(limit)
    
    result = db.execute(query)
    comments = result.scalars().all()
    
    return [
        {
            "id": c.id,
            "stream_id": c.stream_id,
            "user_id": c.user_id,
            "content": c.content,
            "is_pinned": c.is_pinned,
            "likes_count": c.likes_count,
            "created_at": c.created_at
        }
        for c in comments
    ]


@router.post("/streams/{stream_id}/react")
async def react_to_stream(
    stream_id: UUID,
    reaction_data: StreamReactionCreate,
    current_user: dict = Depends(get_current_user),
    db = Depends(get_db)
):
    """
    React to live stream (like, love, wow, etc.)
    """
    # Check if stream exists
    result = db.execute(select(LiveStream).where(LiveStream.id == stream_id))
    stream = result.scalar_one_or_none()
    
    if not stream:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Stream not found"
        )
    
    # Create reaction
    reaction = StreamReaction(
        stream_id=stream_id,
        user_id=current_user['user_id'],
        reaction_type=reaction_data.reaction_type
    )
    
    db.add(reaction)
    
    # Increment likes count (all reactions count as likes)
    stream.likes_count += 1
    
    db.commit()
    
    return {"message": "Reaction added successfully", "reaction": reaction_data.reaction_type}


@router.get("/streams/{stream_id}/stats", response_model=StreamStatsResponse)
async def get_stream_stats(
    stream_id: UUID,
    db = Depends(get_db)
):
    """
    Get stream statistics
    """
    result = db.execute(select(LiveStream).where(LiveStream.id == stream_id))
    stream = result.scalar_one_or_none()
    
    if not stream:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Stream not found"
        )
    
    return {
        "stream_id": stream.id,
        "current_viewers": stream.current_viewers,
        "peak_viewers": stream.peak_viewers,
        "total_views": stream.total_views,
        "likes_count": stream.likes_count,
        "comments_count": stream.comments_count,
        "average_watch_time": None,  # TODO: Calculate from analytics
        "engagement_rate": None  # TODO: Calculate from analytics
    }


# ========== USER'S MEDIA ==========

@router.get("/media/my/uploads", response_model=List[MediaResponse])
async def get_my_uploads(
    skip: int = 0,
    limit: int = 20,
    current_user: dict = Depends(get_current_user),
    db = Depends(get_db)
):
    """
    Get current user's uploaded media
    """
    query = select(Media).where(
        and_(
            Media.uploaded_by == current_user['user_id'],
            Media.deleted_at.is_(None)
        )
    ).order_by(Media.created_at.desc()).offset(skip).limit(limit)
    
    result = db.execute(query)
    media_list = result.scalars().all()
    
    return [media_to_dict(media, include_sensitive=True) for media in media_list]


@router.get("/streams/my/streams", response_model=List[LiveStreamResponse])
async def get_my_streams(
    skip: int = 0,
    limit: int = 20,
    current_user: dict = Depends(get_current_user),
    db = Depends(get_db)
):
    """
    Get current user's streams
    """
    query = select(LiveStream).where(
        LiveStream.streamer_id == current_user['user_id']
    ).order_by(LiveStream.created_at.desc()).offset(skip).limit(limit)
    
    result = db.execute(query)
    streams = result.scalars().all()
    
    return [stream_to_dict(stream, user_id=current_user['user_id']) for stream in streams]
