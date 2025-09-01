"""Fingerprinting API Routes
Multi-format content fingerprinting and analysis endpoints.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
from typing import List, Dict, Any, Optional, Union
from datetime import datetime
import os
import hashlib
import uuid

from fastapi import APIRouter, Depends, HTTPException, status, File, UploadFile, Form
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, Field, validator
import aiofiles

from ...core.database import database_manager
from ...core.security import security_manager
from ...core.cache import cache_manager
from ...core.logging import logger
from ...ai_engine.fingerprinting.audio_fingerprint_engine import AudioFingerprintEngine
from ...ai_engine.fingerprinting.video_fingerprint_engine import VideoFingerprintEngine
from ...ai_engine.fingerprinting.image_fingerprint_engine import ImageFingerprintEngine
from ...ai_engine.fingerprinting.text_fingerprint_engine import TextFingerprintEngine
from ...ai_engine.fingerprinting.vector_matching_engine import VectorMatchingEngine

# Import production audio fingerprinting
from .audio_fingerprinting_production import router as audio_production_router


# Pydantic models
class FingerprintRequest(BaseModel):
    file_id: str
    content_type: str = Field(..., regex="^(audio|video|image|text)$")
    analysis_level: str = Field(default="standard", regex="^(basic|standard|advanced|enterprise)$")
    priority: str = Field(default="normal", regex="^(low|normal|high|urgent)$")
    metadata: Optional[Dict[str, Any]] = None


class FingerprintResponse(BaseModel):
    fingerprint_id: str
    file_id: str
    content_type: str
    status: str
    fingerprint_data: Dict[str, Any]
    similarity_matches: List[Dict[str, Any]]
    confidence_score: float
    processing_time: float
    created_at: datetime


class SimilaritySearchRequest(BaseModel):
    fingerprint_data: Dict[str, Any]
    content_type: str
    threshold: float = Field(default=0.8, ge=0.0, le=1.0)
    max_results: int = Field(default=10, ge=1, le=100)


class BatchFingerprintRequest(BaseModel):
    file_ids: List[str] = Field(..., max_items=50)
    content_types: List[str]
    analysis_level: str = Field(default="standard")
    priority: str = Field(default="normal")

    @validator('content_types')
    def validate_content_types_match_files(cls, v, values):
        if 'file_ids' in values and len(v) != len(values['file_ids']):
            raise ValueError('content_types must match file_ids length')
        return v


class FingerprintStatus(BaseModel):
    fingerprint_id: str
    status: str
    progress: float
    estimated_completion: Optional[datetime] = None
    error_message: Optional[str] = None


# Router setup
router = APIRouter()
security = HTTPBearer(auto_error=False)

# Initialize fingerprinting engines
audio_engine = AudioFingerprintEngine()
video_engine = VideoFingerprintEngine()
image_engine = ImageFingerprintEngine()
text_engine = TextFingerprintEngine()
vector_engine = VectorMatchingEngine()


async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Get current authenticated user"""
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required"
        )
    
    try:
        user_data = await security_manager.verify_token(credentials.credentials)
        return user_data
    except Exception as e:
        logger.error(f"Token verification failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication token"
        )


@router.post("/upload", response_model=Dict[str, str])
async def upload_file_for_fingerprinting(
    file: UploadFile = File(...),
    content_type: str = Form(...),
    user: dict = Depends(get_current_user)
):
    """Upload a file for fingerprinting analysis"""
    try:
        # Validate file type
        allowed_types = {
            'audio': ['.mp3', '.wav', '.flac', '.m4a', '.ogg', '.aac'],
            'video': ['.mp4', '.avi', '.mov', '.mkv', '.wmv', '.flv'],
            'image': ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp'],
            'text': ['.txt', '.pdf', '.docx', '.html', '.md']
        }
        
        if content_type not in allowed_types:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid content type. Supported: {list(allowed_types.keys())}"
            )
        
        file_extension = os.path.splitext(file.filename)[1].lower()
        if file_extension not in allowed_types[content_type]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid file extension for {content_type}. Supported: {allowed_types[content_type]}"
            )
        
        # Generate unique file ID
        file_id = str(uuid.uuid4())
        file_path = f"/tmp/uploads/{file_id}{file_extension}"
        
        # Ensure upload directory exists
        os.makedirs("/tmp/uploads", exist_ok=True)
        
        # Save uploaded file
        async with aiofiles.open(file_path, 'wb') as f:
            content = await file.read()
            await f.write(content)
        
        # Store file metadata in database
        async with database_manager.get_postgres_session() as session:
            await session.execute("""
                INSERT INTO uploaded_files (file_id, user_id, original_filename, file_path, 
                                          content_type, file_size, upload_timestamp)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (
                file_id, user['user_id'], file.filename, file_path,
                content_type, len(content), datetime.utcnow()
            ))
            await session.commit()
        
        logger.info(f"File uploaded successfully: {file_id} by user {user['user_id']}")
        
        return {
            "file_id": file_id,
            "message": "File uploaded successfully",
            "filename": file.filename,
            "content_type": content_type,
            "file_size": len(content)
        }
        
    except Exception as e:
        logger.error(f"File upload failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="File upload failed"
        )


@router.post("/analyze", response_model=FingerprintResponse)
async def create_fingerprint(
    request: FingerprintRequest,
    user: dict = Depends(get_current_user)
):
    """Create fingerprint for uploaded content"""
    try:
        start_time = datetime.utcnow()
        
        # Get file information
        async with database_manager.get_postgres_session() as session:
            result = await session.execute("""
                SELECT file_path, original_filename, content_type, file_size
                FROM uploaded_files 
                WHERE file_id = %s AND user_id = %s
            """, (request.file_id, user['user_id']))
            
            file_data = result.fetchone()
            if not file_data:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="File not found or access denied"
                )
        
        file_path, filename, content_type, file_size = file_data
        
        # Validate content type matches
        if request.content_type != content_type:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Content type mismatch"
            )
        
        # Check if file exists
        if not os.path.exists(file_path):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Physical file not found"
            )
        
        # Generate fingerprint based on content type
        fingerprint_id = str(uuid.uuid4())
        fingerprint_data = {}
        
        if content_type == "audio":
            fingerprint_data = await audio_engine.generate_fingerprint(
                file_path, analysis_level=request.analysis_level
            )
        elif content_type == "video":
            fingerprint_data = await video_engine.generate_fingerprint(
                file_path, analysis_level=request.analysis_level
            )
        elif content_type == "image":
            fingerprint_data = await image_engine.generate_fingerprint(
                file_path, analysis_level=request.analysis_level
            )
        elif content_type == "text":
            fingerprint_data = await text_engine.generate_fingerprint(
                file_path, analysis_level=request.analysis_level
            )
        
        # Search for similar content
        similarity_matches = await vector_engine.find_similar(
            fingerprint_data, content_type, threshold=0.8
        )
        
        # Calculate confidence score
        confidence_score = fingerprint_data.get('confidence', 0.95)
        
        # Store fingerprint in database
        async with database_manager.get_postgres_session() as session:
            await session.execute("""
                INSERT INTO content_fingerprints (fingerprint_id, file_id, user_id, content_type,
                                                fingerprint_data, confidence_score, analysis_level,
                                                processing_time, created_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                fingerprint_id, request.file_id, user['user_id'], content_type,
                fingerprint_data, confidence_score, request.analysis_level,
                (datetime.utcnow() - start_time).total_seconds(), datetime.utcnow()
            ))
            await session.commit()
        
        # Store in vector database for fast similarity search
        await vector_engine.index_fingerprint(fingerprint_id, fingerprint_data, content_type)
        
        processing_time = (datetime.utcnow() - start_time).total_seconds()
        
        logger.info(f"Fingerprint created: {fingerprint_id} for file {request.file_id}")
        
        return FingerprintResponse(
            fingerprint_id=fingerprint_id,
            file_id=request.file_id,
            content_type=content_type,
            status="completed",
            fingerprint_data=fingerprint_data,
            similarity_matches=similarity_matches,
            confidence_score=confidence_score,
            processing_time=processing_time,
            created_at=datetime.utcnow()
        )
        
    except Exception as e:
        logger.error(f"Fingerprint creation failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Fingerprint creation failed"
        )


@router.post("/search", response_model=List[Dict[str, Any]])
async def search_similar_content(
    request: SimilaritySearchRequest,
    user: dict = Depends(get_current_user)
):
    """Search for similar content using fingerprint data"""
    try:
        # Search in vector database
        matches = await vector_engine.find_similar(
            request.fingerprint_data,
            request.content_type,
            threshold=request.threshold,
            max_results=request.max_results
        )
        
        # Enrich results with metadata
        enriched_matches = []
        async with database_manager.get_postgres_session() as session:
            for match in matches:
                result = await session.execute("""
                    SELECT cf.fingerprint_id, cf.file_id, cf.confidence_score, cf.created_at,
                           uf.original_filename, uf.user_id
                    FROM content_fingerprints cf
                    JOIN uploaded_files uf ON cf.file_id = uf.file_id
                    WHERE cf.fingerprint_id = %s
                """, (match['fingerprint_id'],))
                
                fingerprint_info = result.fetchone()
                if fingerprint_info:
                    enriched_matches.append({
                        "fingerprint_id": fingerprint_info[0],
                        "file_id": fingerprint_info[1],
                        "similarity_score": match['similarity_score'],
                        "confidence_score": fingerprint_info[2],
                        "filename": fingerprint_info[4],
                        "owner_id": fingerprint_info[5],
                        "created_at": fingerprint_info[3]
                    })
        
        logger.info(f"Similarity search completed: {len(enriched_matches)} matches found")
        
        return enriched_matches
        
    except Exception as e:
        logger.error(f"Similarity search failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Similarity search failed"
        )


@router.post("/batch", response_model=Dict[str, Any])
async def batch_fingerprint(
    request: BatchFingerprintRequest,
    user: dict = Depends(get_current_user)
):
    """Create fingerprints for multiple files in batch"""
    try:
        batch_id = str(uuid.uuid4())
        
        # Validate all files exist and belong to user
        async with database_manager.get_postgres_session() as session:
            for file_id in request.file_ids:
                result = await session.execute("""
                    SELECT COUNT(*) FROM uploaded_files 
                    WHERE file_id = %s AND user_id = %s
                """, (file_id, user['user_id']))
                
                count = result.fetchone()[0]
                if count == 0:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail=f"File not found or access denied: {file_id}"
                    )
        
        # Create batch processing job
        processing_tasks = []
        for i, (file_id, content_type) in enumerate(zip(request.file_ids, request.content_types)):
            task_data = FingerprintRequest(
                file_id=file_id,
                content_type=content_type,
                analysis_level=request.analysis_level,
                priority=request.priority
            )
            processing_tasks.append(task_data)
        
        # Store batch job in database
        async with database_manager.get_postgres_session() as session:
            await session.execute("""
                INSERT INTO batch_fingerprint_jobs (batch_id, user_id, file_count, 
                                                  status, priority, created_at)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (
                batch_id, user['user_id'], len(request.file_ids),
                "queued", request.priority, datetime.utcnow()
            ))
            await session.commit()
        
        # Schedule background processing
        # Note: In production, this would use Celery or similar task queue
        asyncio.create_task(_process_batch_fingerprints(batch_id, processing_tasks, user))
        
        logger.info(f"Batch fingerprint job created: {batch_id} with {len(request.file_ids)} files")
        
        return {
            "batch_id": batch_id,
            "file_count": len(request.file_ids),
            "status": "queued",
            "estimated_completion": datetime.utcnow().isoformat() + "Z"
        }
        
    except Exception as e:
        logger.error(f"Batch fingerprint creation failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Batch fingerprint creation failed"
        )


@router.get("/status/{fingerprint_id}", response_model=FingerprintStatus)
async def get_fingerprint_status(
    fingerprint_id: str,
    user: dict = Depends(get_current_user)
):
    """Get fingerprint processing status"""
    try:
        async with database_manager.get_postgres_session() as session:
            result = await session.execute("""
                SELECT cf.fingerprint_id, 'completed' as status, 1.0 as progress,
                       cf.created_at, NULL as error_message
                FROM content_fingerprints cf
                JOIN uploaded_files uf ON cf.file_id = uf.file_id
                WHERE cf.fingerprint_id = %s AND uf.user_id = %s
            """, (fingerprint_id, user['user_id']))
            
            fingerprint_info = result.fetchone()
            if not fingerprint_info:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Fingerprint not found or access denied"
                )
        
        return FingerprintStatus(
            fingerprint_id=fingerprint_info[0],
            status=fingerprint_info[1],
            progress=fingerprint_info[2],
            estimated_completion=None,
            error_message=fingerprint_info[4]
        )
        
    except Exception as e:
        logger.error(f"Get fingerprint status failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get fingerprint status"
        )


@router.delete("/{fingerprint_id}")
async def delete_fingerprint(
    fingerprint_id: str,
    user: dict = Depends(get_current_user)
):
    """Delete a fingerprint"""
    try:
        async with database_manager.get_postgres_session() as session:
            # Verify ownership
            result = await session.execute("""
                SELECT cf.fingerprint_id
                FROM content_fingerprints cf
                JOIN uploaded_files uf ON cf.file_id = uf.file_id
                WHERE cf.fingerprint_id = %s AND uf.user_id = %s
            """, (fingerprint_id, user['user_id']))
            
            if not result.fetchone():
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Fingerprint not found or access denied"
                )
            
            # Delete from database
            await session.execute("""
                DELETE FROM content_fingerprints WHERE fingerprint_id = %s
            """, (fingerprint_id,))
            await session.commit()
        
        # Remove from vector database
        await vector_engine.remove_fingerprint(fingerprint_id)
        
        logger.info(f"Fingerprint deleted: {fingerprint_id}")
        
        return {"message": "Fingerprint deleted successfully"}
        
    except Exception as e:
        logger.error(f"Delete fingerprint failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete fingerprint"
        )


async def _process_batch_fingerprints(batch_id: str, tasks: List[FingerprintRequest], user: dict):
    """Background task to process batch fingerprints"""
    try:
        completed = 0
        total = len(tasks)
        
        # Update batch status to processing
        async with database_manager.get_postgres_session() as session:
            await session.execute("""
                UPDATE batch_fingerprint_jobs 
                SET status = 'processing', started_at = %s
                WHERE batch_id = %s
            """, (datetime.utcnow(), batch_id))
            await session.commit()
        
        # Process each task
        for task in tasks:
            try:
                await create_fingerprint(task, user)
                completed += 1
                
                # Update progress
                progress = completed / total
                async with database_manager.get_postgres_session() as session:
                    await session.execute("""
                        UPDATE batch_fingerprint_jobs 
                        SET progress = %s WHERE batch_id = %s
                    """, (progress, batch_id))
                    await session.commit()
                    
            except Exception as e:
                logger.error(f"Batch task failed for file {task.file_id}: {e}")
        
        # Mark batch as completed
        async with database_manager.get_postgres_session() as session:
            await session.execute("""
                UPDATE batch_fingerprint_jobs 
                SET status = 'completed', completed_at = %s, progress = 1.0
                WHERE batch_id = %s
            """, (datetime.utcnow(), batch_id))
            await session.commit()
        
        logger.info(f"Batch fingerprint job completed: {batch_id}")
        
    except Exception as e:
        logger.error(f"Batch processing failed: {e}")
        
        # Mark batch as failed
        async with database_manager.get_postgres_session() as session:
            await session.execute("""
                UPDATE batch_fingerprint_jobs 
                SET status = 'failed', error_message = %s
                WHERE batch_id = %s
            """, (str(e), batch_id))
            await session.commit()