"""Content Protection API Routes
Content protection monitoring and violation management.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""
from typing import Dict, Any, List, Optional
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel

from ...core.database import database_manager
from ...core.security import security_manager
from ...core.logging import logger
from ...protection.monitoring import protection_monitor


# Pydantic models
class ProtectionRequest(BaseModel):
    content_id: str
    platforms: List[str]
    monitoring_frequency: int = 24  # hours
    alert_threshold: float = 0.85


class ViolationResponse(BaseModel):
    violation_id: str
    content_id: str
    platform: str
    violation_url: str
    similarity_score: float
    status: str
    detected_at: datetime


class ProtectionStatus(BaseModel):
    content_id: str
    monitoring_active: bool
    platforms: List[str]
    last_check: Optional[datetime]
    violations_count: int


# Router setup
router = APIRouter()


@router.post("/enable")
async def enable_protection(
    protection_request: ProtectionRequest,
    current_user: Dict[str, Any] = Depends(security_manager.get_current_user)
):
    """Enable protection monitoring for content"""
    try:
        user_id = current_user["user_id"]
        
        # Get content and fingerprint data
        async with database_manager.get_postgres_session() as session:
            result = await session.execute(
                """
                SELECT content_type, fingerprint_id 
                FROM content 
                WHERE id = %s AND user_id = %s AND active = true
                """,
                (protection_request.content_id, user_id)
            )
            
            row = result.fetchone()
            if not row:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Content not found"
                )
        
        # Get fingerprint data from MongoDB
        processing_collection = await database_manager.get_mongodb_collection("content_processing")
        processing_doc = await processing_collection.find_one({
            "content_id": protection_request.content_id
        })
        
        if not processing_doc:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Content fingerprint not found"
            )
        
        # Add to monitoring system
        success = await protection_monitor.add_content_monitoring(
            user_id=user_id,
            content_id=protection_request.content_id,
            content_type=row[0],
            fingerprint_data=processing_doc.get("fingerprint_data", {}),
            platforms=protection_request.platforms,
            monitoring_frequency=protection_request.monitoring_frequency,
            alert_threshold=protection_request.alert_threshold
        )
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to enable protection"
            )
        
        logger.info(f"Protection enabled for content {protection_request.content_id}")
        
        return {"message": "Protection monitoring enabled successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Enable protection failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to enable protection"
        )


@router.get("/status", response_model=Dict[str, Any])
async def get_protection_status(
    current_user: Dict[str, Any] = Depends(security_manager.get_current_user)
):
    """Get protection monitoring status for user"""
    try:
        user_id = current_user["user_id"]
        
        status_data = await protection_monitor.get_monitoring_status(user_id)
        
        return status_data
        
    except Exception as e:
        logger.error(f"Get protection status failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get protection status"
        )


@router.get("/violations", response_model=List[ViolationResponse])
async def get_violations(
    limit: int = 20,
    offset: int = 0,
    status_filter: Optional[str] = None,
    current_user: Dict[str, Any] = Depends(security_manager.get_current_user)
):
    """Get content violations for user"""
    try:
        user_id = current_user["user_id"]
        
        # Build query
        query = "SELECT id, original_content_id, platform, violation_url, similarity_score, status, detected_at FROM protection_violations WHERE user_id = %s"
        params = [user_id]
        
        if status_filter:
            query += " AND status = %s"
            params.append(status_filter)
        
        query += " ORDER BY detected_at DESC LIMIT %s OFFSET %s"
        params.extend([limit, offset])
        
        async with database_manager.get_postgres_session() as session:
            result = await session.execute(query, params)
            
            violations = []
            for row in result.fetchall():
                violations.append(ViolationResponse(
                    violation_id=row[0],
                    content_id=row[1],
                    platform=row[2],
                    violation_url=row[3],
                    similarity_score=row[4],
                    status=row[5],
                    detected_at=row[6]
                ))
            
            return violations
            
    except Exception as e:
        logger.error(f"Get violations failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve violations"
        )


@router.post("/disable/{content_id}")
async def disable_protection(
    content_id: str,
    current_user: Dict[str, Any] = Depends(security_manager.get_current_user)
):
    """Disable protection monitoring for content"""
    try:
        user_id = current_user["user_id"]
        
        # Verify content ownership
        async with database_manager.get_postgres_session() as session:
            result = await session.execute(
                "SELECT id FROM content WHERE id = %s AND user_id = %s",
                (content_id, user_id)
            )
            
            if not result.fetchone():
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Content not found"
                )
        
        # Remove from monitoring
        success = await protection_monitor.remove_content_monitoring(content_id)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to disable protection"
            )
        
        logger.info(f"Protection disabled for content {content_id}")
        
        return {"message": "Protection monitoring disabled successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Disable protection failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to disable protection"
        )