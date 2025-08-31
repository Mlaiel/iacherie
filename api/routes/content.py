"""Content Management API Routes
Content upload, processing, and management endpoints.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""
from typing import Dict, Any, List, Optional
from datetime import datetime
import uuid

from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from pydantic import BaseModel

from ...core.database import database_manager
from ...core.security import security_manager
from ...core.cache import cache_manager
from ...core.logging import logger
from ...ai_engine.content_processor import content_processor
from ...ai_engine.fingerprinting import fingerprint_engine
from ...ai_engine.vector_database import vector_database
from ...ai_engine.content_analyzer import content_analyzer


# Pydantic models
class ContentMetadata(BaseModel):
    title: str
    description: Optional[str] = None
    tags: Optional[List[str]] = []
    target_platforms: Optional[List[str]] = []


class ContentResponse(BaseModel):
    content_id: str
    user_id: str
    title: str
    description: Optional[str]
    content_type: str
    file_size: int
    status: str
    fingerprint_id: Optional[str]
    created_at: datetime
    analysis_data: Optional[Dict[str, Any]] = None


# Router setup
router = APIRouter()


@router.post("/upload", response_model=ContentResponse)
async def upload_content(
    file: UploadFile = File(...),
    title: str = Form(...),
    description: Optional[str] = Form(None),
    tags: Optional[str] = Form(None),  # JSON string of tags
    target_platforms: Optional[str] = Form(None),  # JSON string of platforms
    current_user: Dict[str, Any] = Depends(security_manager.get_current_user)
):
    """Upload and process content"""    try:
        user_id = current_user["user_id"]
        content_id = str(uuid.uuid4())
        
        # Read file data
        file_data = await file.read()
        
        # Validate file size
        max_size = 500 * 1024 * 1024  # 500MB
        if len(file_data) > max_size:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail="File too large"
            )
        
        # Process content
        logger.info(f"Processing content upload: {file.filename}")
        
        processing_result = await content_processor.process_content(
            file_data, file.filename
        )
        
        content_type = processing_result.get("content_type", "unknown")
        
        # Generate fingerprint
        fingerprint_data = await fingerprint_engine.generate_fingerprint(
            content_type, 
            _extract_content_for_fingerprint(processing_result, content_type)
        )
        
        fingerprint_id = str(uuid.uuid4())
        
        # Store in vector database
        await vector_database.add_fingerprint(
            content_type,
            content_id,
            fingerprint_data,
            {
                "user_id": user_id,
                "title": title,
                "filename": file.filename,
                "created_at": datetime.utcnow().isoformat()
            }
        )
        
        # Store content metadata in database
        async with database_manager.get_postgres_session() as session:
            await session.execute(
                """                INSERT INTO content 
                (id, user_id, title, description, content_type, filename, 
                 file_size, fingerprint_id, status, created_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """,
                (content_id, user_id, title, description, content_type,
                 file.filename, len(file_data), fingerprint_id, "processed",
                 datetime.utcnow())
            )
        
        # Store processing results in MongoDB
        processing_collection = await database_manager.get_mongodb_collection("content_processing")
        await processing_collection.insert_one({
            "content_id": content_id,
            "processing_result": processing_result,
            "fingerprint_data": fingerprint_data,
            "created_at": datetime.utcnow()
        })
        
        logger.info(f"Content uploaded successfully: {content_id}")
        
        return ContentResponse(
            content_id=content_id,
            user_id=user_id,
            title=title,
            description=description,
            content_type=content_type,
            file_size=len(file_data),
            status="processed",
            fingerprint_id=fingerprint_id,
            created_at=datetime.utcnow()
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Content upload failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Content upload failed"
        )


@router.get("/list", response_model=List[ContentResponse])
async def list_user_content(
    limit: int = 20,
    offset: int = 0,
    current_user: Dict[str, Any] = Depends(security_manager.get_current_user)
):
    """List user's content"""    try:
        user_id = current_user["user_id"]
        
        async with database_manager.get_postgres_session() as session:
            result = await session.execute(
                """                SELECT id, user_id, title, description, content_type, 
                       file_size, fingerprint_id, status, created_at
                FROM content 
                WHERE user_id = %s AND active = true
                ORDER BY created_at DESC
                LIMIT %s OFFSET %s
                """,
                (user_id, limit, offset)
            )
            
            content_list = []
            for row in result.fetchall():
                content_list.append(ContentResponse(
                    content_id=row[0],
                    user_id=row[1],
                    title=row[2],
                    description=row[3],
                    content_type=row[4],
                    file_size=row[5],
                    fingerprint_id=row[6],
                    status=row[7],
                    created_at=row[8]
                ))
            
            return content_list
            
    except Exception as e:
        logger.error(f"Content listing failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve content"
        )


@router.get("/{content_id}", response_model=ContentResponse)
async def get_content(
    content_id: str,
    current_user: Dict[str, Any] = Depends(security_manager.get_current_user)
):
    """Get specific content details"""    try:
        user_id = current_user["user_id"]
        
        # Validate access
        if not security_manager.validate_content_access(user_id, user_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied"
            )
        
        async with database_manager.get_postgres_session() as session:
            result = await session.execute(
                """                SELECT id, user_id, title, description, content_type,
                       file_size, fingerprint_id, status, created_at
                FROM content 
                WHERE id = %s AND user_id = %s AND active = true
                """,
                (content_id, user_id)
            )
            
            row = result.fetchone()
            if not row:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Content not found"
                )
            
            # Get analysis data from MongoDB
            processing_collection = await database_manager.get_mongodb_collection("content_processing")
            processing_doc = await processing_collection.find_one({"content_id": content_id})
            
            analysis_data = None
            if processing_doc:
                analysis_data = processing_doc.get("processing_result")
            
            return ContentResponse(
                content_id=row[0],
                user_id=row[1],
                title=row[2],
                description=row[3],
                content_type=row[4],
                file_size=row[5],
                fingerprint_id=row[6],
                status=row[7],
                created_at=row[8],
                analysis_data=analysis_data
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get content failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve content"
        )


@router.post("/{content_id}/analyze")
async def analyze_content(
    content_id: str,
    target_platforms: Optional[List[str]] = None,
    user_goals: Optional[List[str]] = None,
    current_user: Dict[str, Any] = Depends(security_manager.get_current_user)
):
    """Analyze content for SEO and platform optimization"""    try:
        user_id = current_user["user_id"]
        
        # Get content data
        processing_collection = await database_manager.get_mongodb_collection("content_processing")
        processing_doc = await processing_collection.find_one({"content_id": content_id})
        
        if not processing_doc:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Content not found"
            )
        
        # Perform analysis
        analysis_result = await content_analyzer.analyze_content(
            processing_doc["processing_result"],
            target_platforms,
            user_goals
        )
        
        # Store analysis results
        analysis_collection = await database_manager.get_mongodb_collection("content_analysis")
        await analysis_collection.insert_one({
            "content_id": content_id,
            "user_id": user_id,
            "analysis_result": analysis_result,
            "target_platforms": target_platforms,
            "user_goals": user_goals,
            "created_at": datetime.utcnow()
        })
        
        return analysis_result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Content analysis failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Content analysis failed"
        )


@router.delete("/{content_id}")
async def delete_content(
    content_id: str,
    current_user: Dict[str, Any] = Depends(security_manager.get_current_user)
):
    """Delete content"""    try:
        user_id = current_user["user_id"]
        
        # Soft delete in PostgreSQL
        async with database_manager.get_postgres_session() as session:
            result = await session.execute(
                "UPDATE content SET active = false WHERE id = %s AND user_id = %s",
                (content_id, user_id)
            )
            
            if result.rowcount == 0:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Content not found"
                )
        
        # Remove from vector database
        await vector_database.remove_content("unknown", content_id)  # Content type would be stored
        
        logger.info(f"Content deleted: {content_id}")
        
        return {"message": "Content deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Content deletion failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Content deletion failed"
        )


def _extract_content_for_fingerprint(processing_result: Dict[str, Any], content_type: str):
    """Extract appropriate data for fingerprinting"""    if content_type == "audio":
        # For audio, we'd extract the actual audio array
        # For demo, return processing result
        return processing_result.get("features", {})
    elif content_type == "video":
        # For video, return frames and fps
        return ([], 30)  # Placeholder
    elif content_type == "image":
        # For image, return PIL Image object
        return None  # Placeholder
    elif content_type == "text":
        # For text, return the text content
        return processing_result.get("content_preview", "")
    
    return None