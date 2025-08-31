"""AI Fingerprinting endpoints for IA Influencer Agent platform.

This module handles multi-format content fingerprinting (audio, video, image, text)
with advanced AI detection algorithms and vector similarity matching.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: All rights reserved. Unauthorized use, reproduction, or distribution 
of this code without explicit written permission from Fahed Mlaiel is strictly prohibited.
"""
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import asyncio
import hashlib
import logging
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form, BackgroundTasks
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field, validator
import numpy as np

from ..core.config import get_settings
from ..core.database import get_db
from ..core.security import get_current_user
from ..models.user import User
from ..models.fingerprint import ContentFingerprint, FingerprintMatch, ContentType
from ..business.fingerprinting_service import FingerprintingService
from ..business.vector_search_service import VectorSearchService
from ..business.content_analyzer import ContentAnalyzer
from ..utils.file_validator import FileValidator
from ..utils.response_handler import ResponseHandler

logger = logging.getLogger(__name__)
settings = get_settings()

router = APIRouter(prefix="/fingerprinting", tags=["AI Fingerprinting"])

# Pydantic models for request/response validation
class FingerprintRequest(BaseModel):
    """Request model for content fingerprinting"""    content_type: ContentType = Field(..., description="Type of content to fingerprint")
    metadata: Dict[str, Any] = Field(default={}, description="Optional metadata for content")
    protection_level: str = Field(default="standard", description="Protection level: basic, standard, premium")
    monitoring_enabled: bool = Field(default=True, description="Enable continuous monitoring")
    
    @validator('content_type')
    def validate_content_type(cls, v):
        allowed_types = ['audio', 'video', 'image', 'text', 'document']
        if v not in allowed_types:
            raise ValueError(f'Content type must be one of: {allowed_types}')
        return v

class FingerprintResponse(BaseModel):
    """Response model for fingerprinting operation"""    fingerprint_id: str = Field(..., description="Unique fingerprint identifier")
    content_hash: str = Field(..., description="SHA256 hash of content")
    vector_id: str = Field(..., description="Vector database identifier")
    processing_time: float = Field(..., description="Processing time in seconds")
    similarity_threshold: float = Field(..., description="Similarity threshold for matching")
    monitoring_status: str = Field(..., description="Monitoring activation status")
    metadata: Dict[str, Any] = Field(..., description="Processing metadata and statistics")

class SimilaritySearchRequest(BaseModel):
    """Request model for similarity search"""    fingerprint_id: Optional[str] = Field(None, description="Existing fingerprint ID to compare")
    similarity_threshold: float = Field(0.8, ge=0.0, le=1.0, description="Minimum similarity score")
    max_results: int = Field(100, ge=1, le=1000, description="Maximum number of results")
    platforms: List[str] = Field(default=[], description="Specific platforms to search")
    include_metadata: bool = Field(True, description="Include detailed metadata in results")

class SimilarityMatch(BaseModel):
    """Model for similarity search results"""    match_id: str = Field(..., description="Unique match identifier")
    similarity_score: float = Field(..., description="Similarity score (0.0-1.0)")
    original_fingerprint_id: str = Field(..., description="Original content fingerprint ID")
    detected_content_url: Optional[str] = Field(None, description="URL where content was detected")
    platform: str = Field(..., description="Platform where content was found")
    detection_timestamp: datetime = Field(..., description="When content was detected")
    content_metadata: Dict[str, Any] = Field(..., description="Additional content information")

class MonitoringSetupRequest(BaseModel):
    """Request model for monitoring setup"""    fingerprint_ids: List[str] = Field(..., description="List of fingerprint IDs to monitor")
    platforms: List[str] = Field(..., description="Platforms to monitor")
    monitoring_frequency: str = Field("realtime", description="Monitoring frequency: realtime, hourly, daily")
    notification_settings: Dict[str, Any] = Field(..., description="Notification preferences")
    advanced_detection: bool = Field(True, description="Enable advanced AI detection")

# Core fingerprinting endpoints
@router.post("/upload", response_model=FingerprintResponse, status_code=status.HTTP_201_CREATED)
async def create_fingerprint(
    background_tasks: BackgroundTasks,
    content_file: UploadFile = File(...),
    request_data: str = Form(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    fingerprinting_service: FingerprintingService = Depends(),
    vector_service: VectorSearchService = Depends()
):
    """    Create AI fingerprint for uploaded content with advanced detection.
    
    Supports multi-format fingerprinting:
    - Audio: Chromaprint + spectral analysis + Essentia features
    - Video: OpenCV frame analysis + motion patterns + YOLO detection  
    - Image: CLIP embeddings + perceptual hashing + ImageHash
    - Text: BERT/RoBERTa embeddings + semantic analysis
    - Document: OCR + structure analysis + content extraction
    """    try:
        # Parse request data
        import json
        request_obj = FingerprintRequest.parse_raw(request_data)
        
        # Validate file and user permissions
        if not await FileValidator.validate_content_file(content_file, request_obj.content_type):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid file format for specified content type"
            )
        
        # Check user quota and permissions
        quota_check = await fingerprinting_service.check_user_quota(current_user.id, request_obj.protection_level)
        if not quota_check['allowed']:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=f"Quota exceeded: {quota_check['message']}"
            )
        
        # Generate unique fingerprint ID
        fingerprint_id = str(uuid4())
        
        # Process content based on type
        processing_start = datetime.utcnow()
        
        if request_obj.content_type == 'audio':
            fingerprint_data = await fingerprinting_service.process_audio_content(
                content_file, fingerprint_id, request_obj.protection_level
            )
        elif request_obj.content_type == 'video':
            fingerprint_data = await fingerprinting_service.process_video_content(
                content_file, fingerprint_id, request_obj.protection_level
            )
        elif request_obj.content_type == 'image':
            fingerprint_data = await fingerprinting_service.process_image_content(
                content_file, fingerprint_id, request_obj.protection_level
            )
        elif request_obj.content_type == 'text':
            fingerprint_data = await fingerprinting_service.process_text_content(
                content_file, fingerprint_id, request_obj.protection_level
            )
        else:  # document
            fingerprint_data = await fingerprinting_service.process_document_content(
                content_file, fingerprint_id, request_obj.protection_level
            )
        
        processing_time = (datetime.utcnow() - processing_start).total_seconds()
        
        # Generate content hash
        content_hash = hashlib.sha256(await content_file.read()).hexdigest()
        await content_file.seek(0)  # Reset file pointer
        
        # Store fingerprint in vector database
        vector_id = await vector_service.store_fingerprint_vector(
            fingerprint_data['vector_embedding'],
            fingerprint_id,
            current_user.id,
            request_obj.metadata
        )
        
        # Save fingerprint record to database
        fingerprint_record = ContentFingerprint(
            id=fingerprint_id,
            user_id=current_user.id,
            content_type=request_obj.content_type,
            content_hash=content_hash,
            vector_id=vector_id,
            fingerprint_data=fingerprint_data['features'],
            metadata={
                **request_obj.metadata,
                'processing_time': processing_time,
                'protection_level': request_obj.protection_level,
                'file_info': {
                    'filename': content_file.filename,
                    'size': content_file.size,
                    'content_type': content_file.content_type
                }
            },
            monitoring_enabled=request_obj.monitoring_enabled,
            created_at=datetime.utcnow()
        )
        
        db.add(fingerprint_record)
        db.commit()
        
        # Setup monitoring if requested
        if request_obj.monitoring_enabled:
            background_tasks.add_task(
                fingerprinting_service.setup_content_monitoring,
                fingerprint_id,
                current_user.id,
                request_obj.protection_level
            )
        
        logger.info(f"Fingerprint created successfully: {fingerprint_id} for user: {current_user.id}")
        
        return FingerprintResponse(
            fingerprint_id=fingerprint_id,
            content_hash=content_hash,
            vector_id=vector_id,
            processing_time=processing_time,
            similarity_threshold=fingerprint_data.get('similarity_threshold', 0.85),
            monitoring_status="active" if request_obj.monitoring_enabled else "disabled",
            metadata={
                'content_type': request_obj.content_type,
                'protection_level': request_obj.protection_level,
                'features_extracted': len(fingerprint_data['features']),
                'vector_dimensions': len(fingerprint_data['vector_embedding']),
                'processing_algorithm': fingerprint_data.get('algorithm', 'unknown')
            }
        )
        
    except Exception as e:
        logger.error(f"Error creating fingerprint: {str(e)}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Fingerprinting failed: {str(e)}"
        )

@router.post("/search", response_model=List[SimilarityMatch])
async def search_similar_content(
    search_request: SimilaritySearchRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    vector_service: VectorSearchService = Depends(),
    fingerprinting_service: FingerprintingService = Depends()
):
    """    Search for similar content using advanced AI vector similarity matching.
    
    Features:
    - Multi-algorithm similarity detection
    - Cross-platform content monitoring
    - Fuzzy matching for modified content
    - Real-time detection alerts
    """    try:
        # Validate fingerprint ID exists
        if search_request.fingerprint_id:
            fingerprint = db.query(ContentFingerprint).filter(
                ContentFingerprint.id == search_request.fingerprint_id,
                ContentFingerprint.user_id == current_user.id
            ).first()
            
            if not fingerprint:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Fingerprint not found"
                )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Fingerprint ID is required for similarity search"
            )
        
        # Perform vector similarity search
        similar_vectors = await vector_service.search_similar_vectors(
            fingerprint.vector_id,
            threshold=search_request.similarity_threshold,
            limit=search_request.max_results,
            platforms=search_request.platforms
        )
        
        # Get detailed match information
        matches = []
        for vector_match in similar_vectors:
            # Get fingerprint details for matched content
            matched_fingerprint = db.query(ContentFingerprint).filter(
                ContentFingerprint.vector_id == vector_match['vector_id']
            ).first()
            
            if matched_fingerprint:
                # Get detection details from monitoring system
                detection_info = await fingerprinting_service.get_detection_details(
                    matched_fingerprint.id,
                    vector_match['similarity_score']
                )
                
                match_data = SimilarityMatch(
                    match_id=str(uuid4()),
                    similarity_score=vector_match['similarity_score'],
                    original_fingerprint_id=search_request.fingerprint_id,
                    detected_content_url=detection_info.get('detected_url'),
                    platform=detection_info.get('platform', 'unknown'),
                    detection_timestamp=detection_info.get('timestamp', datetime.utcnow()),
                    content_metadata={
                        'content_type': matched_fingerprint.content_type,
                        'original_filename': matched_fingerprint.metadata.get('file_info', {}).get('filename'),
                        'detection_method': detection_info.get('method', 'vector_similarity'),
                        'confidence_level': vector_match['confidence'],
                        **(matched_fingerprint.metadata if search_request.include_metadata else {})
                    }
                )
                matches.append(match_data)
        
        # Sort by similarity score (highest first)
        matches.sort(key=lambda x: x.similarity_score, reverse=True)
        
        logger.info(f"Similarity search completed: {len(matches)} matches found for fingerprint {search_request.fingerprint_id}")
        
        return matches[:search_request.max_results]
        
    except Exception as e:
        logger.error(f"Error in similarity search: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Similarity search failed: {str(e)}"
        )

@router.post("/monitoring/setup", response_model=Dict[str, Any])
async def setup_content_monitoring(
    monitoring_request: MonitoringSetupRequest,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    fingerprinting_service: FingerprintingService = Depends()
):
    """    Setup continuous content monitoring across multiple platforms.
    
    Platforms supported:
    - YouTube, Instagram, TikTok, Twitter/X, Facebook
    - Spotify, SoundCloud, Apple Music, Amazon Music
    - Generic web crawling with custom rules
    """    try:
        # Validate all fingerprint IDs belong to user
        fingerprints = db.query(ContentFingerprint).filter(
            ContentFingerprint.id.in_(monitoring_request.fingerprint_ids),
            ContentFingerprint.user_id == current_user.id
        ).all()
        
        if len(fingerprints) != len(monitoring_request.fingerprint_ids):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="One or more fingerprints not found"
            )
        
        # Validate monitoring platforms
        supported_platforms = settings.SUPPORTED_MONITORING_PLATFORMS
        invalid_platforms = set(monitoring_request.platforms) - set(supported_platforms)
        if invalid_platforms:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Unsupported platforms: {list(invalid_platforms)}"
            )
        
        # Setup monitoring for each fingerprint
        monitoring_configs = []
        for fingerprint in fingerprints:
            config = await fingerprinting_service.create_monitoring_config(
                fingerprint_id=fingerprint.id,
                platforms=monitoring_request.platforms,
                frequency=monitoring_request.monitoring_frequency,
                notifications=monitoring_request.notification_settings,
                advanced_detection=monitoring_request.advanced_detection
            )
            monitoring_configs.append(config)
            
            # Enable monitoring flag
            fingerprint.monitoring_enabled = True
            fingerprint.monitoring_config = config
            
        db.commit()
        
        # Start monitoring tasks in background
        for config in monitoring_configs:
            background_tasks.add_task(
                fingerprinting_service.start_monitoring_job,
                config,
                current_user.id
            )
        
        logger.info(f"Monitoring setup completed for {len(fingerprints)} fingerprints, user: {current_user.id}")
        
        return {
            "status": "success",
            "message": "Content monitoring activated successfully",
            "monitoring_jobs": len(monitoring_configs),
            "monitored_fingerprints": monitoring_request.fingerprint_ids,
            "platforms": monitoring_request.platforms,
            "frequency": monitoring_request.monitoring_frequency,
            "estimated_detection_time": "< 10 seconds for real-time monitoring",
            "notification_channels": list(monitoring_request.notification_settings.keys())
        }
        
    except Exception as e:
        logger.error(f"Error setting up monitoring: {str(e)}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Monitoring setup failed: {str(e)}"
        )

@router.get("/fingerprint/{fingerprint_id}", response_model=Dict[str, Any])
async def get_fingerprint_details(
    fingerprint_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get detailed information about a specific fingerprint."""    try:
        fingerprint = db.query(ContentFingerprint).filter(
            ContentFingerprint.id == fingerprint_id,
            ContentFingerprint.user_id == current_user.id
        ).first()
        
        if not fingerprint:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Fingerprint not found"
            )
        
        # Get monitoring statistics if enabled
        monitoring_stats = {}
        if fingerprint.monitoring_enabled:
            monitoring_stats = await fingerprinting_service.get_monitoring_statistics(fingerprint_id)
        
        return {
            "fingerprint_id": fingerprint.id,
            "content_type": fingerprint.content_type,
            "content_hash": fingerprint.content_hash,
            "created_at": fingerprint.created_at,
            "monitoring_enabled": fingerprint.monitoring_enabled,
            "metadata": fingerprint.metadata,
            "monitoring_statistics": monitoring_stats,
            "protection_status": "active" if fingerprint.monitoring_enabled else "inactive"
        }
        
    except Exception as e:
        logger.error(f"Error retrieving fingerprint details: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve fingerprint details: {str(e)}"
        )

@router.get("/user/fingerprints", response_model=List[Dict[str, Any]])
async def get_user_fingerprints(
    skip: int = 0,
    limit: int = 100,
    content_type: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all fingerprints for the current user with optional filtering."""    try:
        query = db.query(ContentFingerprint).filter(
            ContentFingerprint.user_id == current_user.id
        )
        
        if content_type:
            query = query.filter(ContentFingerprint.content_type == content_type)
        
        fingerprints = query.offset(skip).limit(limit).all()
        
        result = []
        for fp in fingerprints:
            result.append({
                "fingerprint_id": fp.id,
                "content_type": fp.content_type,
                "created_at": fp.created_at,
                "monitoring_enabled": fp.monitoring_enabled,
                "filename": fp.metadata.get('file_info', {}).get('filename', 'unknown'),
                "protection_level": fp.metadata.get('protection_level', 'standard')
            })
        
        return result
        
    except Exception as e:
        logger.error(f"Error retrieving user fingerprints: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve fingerprints: {str(e)}"
        )

@router.delete("/fingerprint/{fingerprint_id}", response_model=Dict[str, str])
async def delete_fingerprint(
    fingerprint_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    fingerprinting_service: FingerprintingService = Depends(),
    vector_service: VectorSearchService = Depends()
):
    """Delete a fingerprint and all associated monitoring."""    try:
        fingerprint = db.query(ContentFingerprint).filter(
            ContentFingerprint.id == fingerprint_id,
            ContentFingerprint.user_id == current_user.id
        ).first()
        
        if not fingerprint:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Fingerprint not found"
            )
        
        # Stop monitoring if enabled
        if fingerprint.monitoring_enabled:
            await fingerprinting_service.stop_monitoring_job(fingerprint_id)
        
        # Delete from vector database
        await vector_service.delete_fingerprint_vector(fingerprint.vector_id)
        
        # Delete from main database
        db.delete(fingerprint)
        db.commit()
        
        logger.info(f"Fingerprint deleted: {fingerprint_id} for user: {current_user.id}")
        
        return {"message": "Fingerprint deleted successfully"}
        
    except Exception as e:
        logger.error(f"Error deleting fingerprint: {str(e)}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete fingerprint: {str(e)}"
        )

__all__ = ["router"]
