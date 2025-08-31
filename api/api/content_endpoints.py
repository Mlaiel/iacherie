"""Content management endpoints for IA Influencer Agent platform.

This module handles multi-format content upload, processing, protection,
and distribution for musicians, bloggers, photographers, influencers, and actors.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: All rights reserved. Unauthorized use, reproduction, or distribution 
of this code without explicit written permission from Fahed Mlaiel is strictly prohibited.
"""import os
import uuid
from datetime import datetime
from typing import List, Optional, Dict, Any
import asyncio
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form, Query
from fastapi.responses import StreamingResponse
import aiofiles
import logging

from ..core.config import get_settings
from ..core.database import get_db
from ..models.user import User
from ..models.content import Content, ContentCreate, ContentUpdate, ContentMetadata
from ..business.content_service import ContentService
from ..business.ai_processing_service import AIProcessingService
from ..business.protection_service import ProtectionService
from ..security.auth_manager import AuthManager
from ..utils.file_handler import FileHandler
from ..utils.content_validator import ContentValidator

logger = logging.getLogger(__name__)
settings = get_settings()

router = APIRouter(prefix="/content", tags=["Content Management"])

# Content type mapping for different user roles
ROLE_CONTENT_MAPPING = {
    "musician": ["audio", "video", "image"],
    "blogger": ["text", "image", "video"],
    "photographer": ["image", "video"],
    "influencer": ["image", "video", "text"],
    "actor": ["video", "audio", "image"]
}

@router.post("/upload", response_model=Dict[str, Any], status_code=status.HTTP_201_CREATED)
async def upload_content(
    files: List[UploadFile] = File(...),
    title: str = Form(...),
    description: Optional[str] = Form(None),
    tags: Optional[str] = Form(None),
    category: str = Form(...),
    privacy_level: str = Form("public"),
    enable_collaboration: bool = Form(False),
    current_user: User = Depends(AuthManager.get_current_user),
    content_service: ContentService = Depends(),
    ai_service: AIProcessingService = Depends(),
    protection_service: ProtectionService = Depends()
):
    """    Upload multi-format content with AI processing and protection.
    
    Supports:
    - Audio files (MP3, WAV, FLAC) for musicians
    - Images (JPG, PNG, WEBP) for photographers/influencers
    - Videos (MP4, MOV, AVI) for actors/influencers
    - Text content for bloggers
    """    try:
        # Validate user role and content types
        allowed_types = ROLE_CONTENT_MAPPING.get(current_user.role.lower(), [])
        
        upload_results = []
        for file in files:
            # Validate file type
            file_type = ContentValidator.get_file_type(file.filename)
            if file_type not in allowed_types:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"File type {file_type} not allowed for role {current_user.role}"
                )
            
            # Validate file size and format
            if not await ContentValidator.validate_upload(file, current_user.role):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Invalid file: {file.filename}"
                )
            
            # Generate unique content ID
            content_id = str(uuid.uuid4())
            
            # Upload file to secure storage
            file_path = await FileHandler.save_uploaded_file(
                file, content_id, current_user.id
            )
            
            # Extract metadata
            metadata = await ContentValidator.extract_metadata(file_path, file_type)
            
            # Create content record
            content_data = ContentCreate(
                title=title,
                description=description,
                file_path=file_path,
                file_type=file_type,
                file_size=metadata.get("file_size", 0),
                original_filename=file.filename,
                category=category,
                privacy_level=privacy_level,
                enable_collaboration=enable_collaboration,
                tags=tags.split(",") if tags else [],
                metadata=metadata,
                owner_id=current_user.id
            )
            
            # Save to database
            content = await content_service.create_content(content_data)
            
            # Start AI processing pipeline asynchronously
            asyncio.create_task(
                ai_service.process_content_async(content.id, file_type)
            )
            
            # Apply content protection
            protection_result = await protection_service.protect_content(content.id)
            
            upload_results.append({
                "content_id": str(content.id),
                "filename": file.filename,
                "file_type": file_type,
                "status": "uploaded",
                "ai_processing": "started",
                "protection_applied": protection_result.get("protected", False),
                "fingerprint": protection_result.get("fingerprint")
            })
        
        logger.info(f"Content uploaded by {current_user.email}: {len(files)} files")
        
        return {
            "message": "Content uploaded successfully",
            "results": upload_results,
            "total_files": len(files)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Content upload error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Content upload failed"
        )

@router.get("/my-content", response_model=Dict[str, Any])
async def get_my_content(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    category: Optional[str] = Query(None),
    file_type: Optional[str] = Query(None),
    current_user: User = Depends(AuthManager.get_current_user),
    content_service: ContentService = Depends()
):
    """    Get current user's content with filtering and pagination.
    """    try:
        contents = await content_service.get_user_content(
            user_id=current_user.id,
            skip=skip,
            limit=limit,
            category=category,
            file_type=file_type
        )
        
        content_list = []
        for content in contents:
            content_dict = {
                "content_id": str(content.id),
                "title": content.title,
                "description": content.description,
                "file_type": content.file_type,
                "category": content.category,
                "privacy_level": content.privacy_level,
                "tags": content.tags,
                "created_at": content.created_at,
                "updated_at": content.updated_at,
                "views": content.view_count,
                "likes": content.like_count,
                "ai_status": content.ai_processing_status,
                "protection_status": content.protection_status,
                "collaboration_enabled": content.enable_collaboration
            }
            
            # Add thumbnail/preview if available
            if content.thumbnail_path:
                content_dict["thumbnail_url"] = f"/content/thumbnail/{content.id}"
            
            content_list.append(content_dict)
        
        return {
            "contents": content_list,
            "total": len(content_list),
            "skip": skip,
            "limit": limit
        }
        
    except Exception as e:
        logger.error(f"Get user content error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve content"
        )

@router.get("/{content_id}", response_model=Dict[str, Any])
async def get_content_details(
    content_id: str,
    current_user: Optional[User] = Depends(AuthManager.get_current_user_optional),
    content_service: ContentService = Depends()
):
    """    Get detailed content information with access control.
    """    try:
        content = await content_service.get_content_by_id(content_id)
        if not content:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Content not found"
            )
        
        # Check access permissions
        if not await content_service.check_content_access(content, current_user):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied"
            )
        
        # Increment view count if not owner
        if current_user and current_user.id != content.owner_id:
            await content_service.increment_view_count(content_id)
        
        # Get content statistics
        stats = await content_service.get_content_statistics(content_id)
        
        # Get AI analysis results
        ai_analysis = await content_service.get_ai_analysis_results(content_id)
        
        return {
            "content_id": str(content.id),
            "title": content.title,
            "description": content.description,
            "file_type": content.file_type,
            "file_size": content.file_size,
            "category": content.category,
            "tags": content.tags,
            "privacy_level": content.privacy_level,
            "created_at": content.created_at,
            "updated_at": content.updated_at,
            "owner": {
                "user_id": str(content.owner_id),
                "username": content.owner.username,
                "role": content.owner.role
            },
            "statistics": stats,
            "ai_analysis": ai_analysis,
            "collaboration_enabled": content.enable_collaboration,
            "protection_status": content.protection_status,
            "metadata": content.metadata
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get content details error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve content details"
        )

@router.put("/{content_id}", response_model=Dict[str, Any])
async def update_content(
    content_id: str,
    content_update: ContentUpdate,
    current_user: User = Depends(AuthManager.get_current_user),
    content_service: ContentService = Depends()
):
    """    Update content metadata and settings.
    """    try:
        content = await content_service.get_content_by_id(content_id)
        if not content:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Content not found"
            )
        
        # Check ownership
        if content.owner_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only content owner can update"
            )
        
        # Update content
        updated_content = await content_service.update_content(content_id, content_update)
        
        logger.info(f"Content updated: {content_id} by {current_user.email}")
        
        return {
            "message": "Content updated successfully",
            "content_id": str(updated_content.id),
            "updated_fields": content_update.dict(exclude_unset=True)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Update content error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Content update failed"
        )

@router.delete("/{content_id}")
async def delete_content(
    content_id: str,
    current_user: User = Depends(AuthManager.get_current_user),
    content_service: ContentService = Depends()
):
    """    Delete content and associated files.
    """    try:
        content = await content_service.get_content_by_id(content_id)
        if not content:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Content not found"
            )
        
        # Check ownership
        if content.owner_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only content owner can delete"
            )
        
        # Delete content and files
        await content_service.delete_content(content_id)
        
        logger.info(f"Content deleted: {content_id} by {current_user.email}")
        
        return {
            "message": "Content deleted successfully",
            "content_id": content_id
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Delete content error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Content deletion failed"
        )

@router.get("/download/{content_id}")
async def download_content(
    content_id: str,
    current_user: Optional[User] = Depends(AuthManager.get_current_user_optional),
    content_service: ContentService = Depends()
):
    """    Download content file with access control.
    """    try:
        content = await content_service.get_content_by_id(content_id)
        if not content:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Content not found"
            )
        
        # Check access permissions
        if not await content_service.check_content_access(content, current_user):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied"
            )
        
        # Check if file exists
        if not os.path.exists(content.file_path):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="File not found"
            )
        
        # Track download
        if current_user:
            await content_service.track_download(content_id, current_user.id)
        
        # Stream file response
        def generate_file_stream():
            with open(content.file_path, "rb") as file:
                while chunk := file.read(8192):
                    yield chunk
        
        return StreamingResponse(
            generate_file_stream(),
            media_type="application/octet-stream",
            headers={"Content-Disposition": f"attachment; filename={content.original_filename}"}
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Download content error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Download failed"
        )

@router.get("/thumbnail/{content_id}")
async def get_content_thumbnail(
    content_id: str,
    current_user: Optional[User] = Depends(AuthManager.get_current_user_optional),
    content_service: ContentService = Depends()
):
    """    Get content thumbnail/preview.
    """    try:
        content = await content_service.get_content_by_id(content_id)
        if not content:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Content not found"
            )
        
        # Check access permissions
        if not await content_service.check_content_access(content, current_user):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied"
            )
        
        # Get thumbnail path
        thumbnail_path = content.thumbnail_path or await content_service.generate_thumbnail(content_id)
        
        if not thumbnail_path or not os.path.exists(thumbnail_path):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Thumbnail not available"
            )
        
        # Stream thumbnail
        def generate_thumbnail_stream():
            with open(thumbnail_path, "rb") as file:
                while chunk := file.read(8192):
                    yield chunk
        
        return StreamingResponse(
            generate_thumbnail_stream(),
            media_type="image/jpeg"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get thumbnail error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Thumbnail retrieval failed"
        )

@router.post("/{content_id}/like")
async def like_content(
    content_id: str,
    current_user: User = Depends(AuthManager.get_current_user),
    content_service: ContentService = Depends()
):
    """    Like/unlike content.
    """    try:
        result = await content_service.toggle_like(content_id, current_user.id)
        
        return {
            "content_id": content_id,
            "liked": result["liked"],
            "total_likes": result["total_likes"]
        }
        
    except Exception as e:
        logger.error(f"Like content error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Like action failed"
        )

@router.get("/search", response_model=Dict[str, Any])
async def search_content(
    q: str = Query(..., min_length=2),
    category: Optional[str] = Query(None),
    file_type: Optional[str] = Query(None),
    tags: Optional[str] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=50),
    current_user: Optional[User] = Depends(AuthManager.get_current_user_optional),
    content_service: ContentService = Depends()
):
    """    Search public content with filters.
    """    try:
        search_results = await content_service.search_content(
            query=q,
            category=category,
            file_type=file_type,
            tags=tags.split(",") if tags else None,
            skip=skip,
            limit=limit,
            user_id=current_user.id if current_user else None
        )
        
        return {
            "query": q,
            "results": search_results["results"],
            "total": search_results["total"],
            "skip": skip,
            "limit": limit,
            "filters": {
                "category": category,
                "file_type": file_type,
                "tags": tags
            }
        }
        
    except Exception as e:
        logger.error(f"Search content error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Search failed"
        )

@router.get("/trending", response_model=Dict[str, Any])
async def get_trending_content(
    timeframe: str = Query("week", regex="^(day|week|month)$"),
    category: Optional[str] = Query(None),
    limit: int = Query(20, ge=1, le=50),
    content_service: ContentService = Depends()
):
    """    Get trending content based on views, likes, and engagement.
    """    try:
        trending = await content_service.get_trending_content(
            timeframe=timeframe,
            category=category,
            limit=limit
        )
        
        return {
            "trending": trending,
            "timeframe": timeframe,
            "category": category,
            "total": len(trending)
        }
        
    except Exception as e:
        logger.error(f"Get trending content error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve trending content"
        )
