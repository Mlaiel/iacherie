"""API routes for cases"""
from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File, status
from sqlalchemy.orm import Session
from geoalchemy2.shape import to_shape

from api.schemas.case import (
    CaseCreate,
    CaseUpdate,
    CaseResponse,
    CaseDetailResponse,
    CaseFilters,
    CaseType,
    CaseStatus,
)
from api.schemas.matching import ActivityResponse
from api.dependencies import get_db, get_current_user
from services.case_service import CaseService
from models.user import User
from models.case import Case

router = APIRouter()


def case_to_dict(case: Case) -> dict:
    """Convert Case model to dictionary with proper location conversion"""
    case_dict = {
        "id": case.id,
        "user_id": case.user_id,
        "type": case.type,
        "title": case.title,
        "description": case.description,
        "location": {
            "latitude": to_shape(case.location).y,
            "longitude": to_shape(case.location).x
        } if case.location else None,
        "address": case.address,
        "city": case.city,
        "country": case.country,
        "urgency_level": case.urgency_level,
        "tags": case.tags or [],
        "volunteers_needed": case.volunteers_needed,
        "status": case.status,
        "ai_classification": case.ai_classification or {},
        "photos": case.photos or [],
        "main_photo": case.main_photo,
        "volunteers_assigned": case.volunteers_assigned,
        "views_count": case.views_count,
        "shares_count": case.shares_count,
        "created_at": case.created_at,
        "updated_at": case.updated_at,
        "completed_at": case.completed_at
    }
    return case_dict


@router.post("/cases", response_model=CaseResponse, status_code=status.HTTP_201_CREATED)
async def create_case(
    case: CaseCreate,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Create a new humanitarian case
    
    Business logic:
    - Validate data (title 5-255 chars, description 20+ chars)
    - Upload photos (max 5, 10MB each)
    - Automatic geocoding if address provided
    - Trigger AI classification (Celery async)
    - Create case in DB
    - Send notifications to nearby volunteers (5km radius by default)
    - Log activity
    - Return created case
    """
    # Helper to get user_id from JWT
    def get_user_id(user_dict):
        return str(user_dict.get("user_id") or user_dict.get("id") or user_dict.get("sub"))
    
    try:
        case_service = CaseService(db)
        new_case = case_service.create_case(case, get_user_id(current_user))
        
        # TODO: Trigger async tasks
        # - classify_case_async.delay(new_case.id, new_case.title, new_case.description)
        # - notify_volunteers_nearby.delay(new_case.id, ...)
        
        return CaseResponse(**case_to_dict(new_case))
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create case: {str(e)}"
        )


@router.get("/cases", response_model=List[CaseResponse])
async def get_cases(
    type: Optional[CaseType] = None,
    status_filter: Optional[CaseStatus] = Query(None, alias="status"),
    urgency_min: Optional[int] = Query(None, ge=1, le=10),
    city: Optional[str] = None,
    tags: Optional[List[str]] = Query(None),
    sort_by: str = "created_at",
    sort_order: str = "desc",
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """
    List cases with filters and pagination
    
    Logic:
    - Apply filters (type, status, urgency, city, tags)
    - Sort by (created_at, urgency_level, distance)
    - Pagination
    - Include preview of assigned volunteers
    """
    try:
        case_service = CaseService(db)
        
        # Build filters
        filters = CaseFilters(
            type=type,
            status=status_filter,
            urgency_min=urgency_min,
            city=city,
            tags=tags,
            sort_by=sort_by,
            sort_order=sort_order
        )
        
        cases, total = case_service.get_cases(filters, page, per_page)
        
        return [CaseResponse(**case_to_dict(case)) for case in cases]
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve cases: {str(e)}"
        )


@router.get("/cases/{case_id}", response_model=CaseDetailResponse)
async def get_case(
    case_id: UUID,
    db: Session = Depends(get_db)
):
    """
    Get complete details of a case
    
    Logic:
    - Retrieve case + relations (user, assignments, activity_log)
    - Increment views_count
    - If authenticated user, mark notification as read
    """
    try:
        case_service = CaseService(db)
        case = case_service.get_case_by_id(case_id, increment_views=True)
        
        if not case:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Case {case_id} not found"
            )
        
        return CaseDetailResponse(**case_to_dict(case))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve case: {str(e)}"
        )


@router.put("/cases/{case_id}", response_model=CaseResponse)
async def update_case(
    case_id: UUID,
    updates: CaseUpdate,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update a case
    
    Logic:
    - Verify permissions (owner or admin)
    - Update allowed fields
    - Re-run AI classification if description changed
    - Log activity
    """
    try:
        case_service = CaseService(db)
        updated_case = case_service.update_case(case_id, updates, current_user.id)
        
        if not updated_case:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Case {case_id} not found or you don't have permission"
            )
        
        return CaseResponse(**case_to_dict(updated_case))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update case: {str(e)}"
        )


@router.delete("/cases/{case_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_case(
    case_id: UUID,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Delete a case (soft delete)
    
    Logic:
    - Verify permissions (owner or admin)
    - Soft delete (deleted_at = NOW())
    - Cancel ongoing assignments
    - Notify assigned volunteers
    - Log activity
    """
    try:
        case_service = CaseService(db)
        deleted = case_service.delete_case(case_id, current_user.id)
        
        if not deleted:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Case {case_id} not found or you don't have permission"
            )
        
        return None
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete case: {str(e)}"
        )


@router.post("/cases/{case_id}/photos", response_model=CaseResponse)
async def add_case_photos(
    case_id: UUID,
    photos: List[str],  # TODO: Change to UploadFile when implementing
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Add photos to a case
    
    Logic:
    - Verify permissions
    - Validate photos (format, size)
    - Upload to S3
    - AI image analysis (classification)
    - Update case
    """
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Endpoint not yet implemented"
    )


@router.get("/cases/{case_id}/activity", response_model=List[ActivityResponse])
async def get_case_activity(
    case_id: UUID,
    db: Session = Depends(get_db)
):
    """Get activity timeline for a case"""
    from models.activity import ActivityLog
    from datetime import datetime
    
    # Check if case exists
    from models.case import Case
    case = db.query(Case).filter(Case.id == case_id).first()
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
    
    # Get activity logs
    activities = db.query(ActivityLog).filter(
        ActivityLog.case_id == case_id
    ).order_by(ActivityLog.created_at.desc()).limit(50).all()
    
    # Format response
    result = []
    for activity in activities:
        result.append({
            "id": str(activity.id),
            "case_id": str(activity.case_id),
            "user_id": str(activity.user_id) if activity.user_id else None,
            "activity_type": activity.activity_type,
            "description": activity.description,
            "metadata": activity.meta or {},
            "created_at": activity.created_at.isoformat() if activity.created_at else None,
        })
    
    return result


@router.get("/cases/{case_id}/recommendations")
async def get_volunteer_recommendations(
    case_id: UUID,
    limit: int = Query(10, ge=1, le=50),
    db: Session = Depends(get_db)
):
    """
    Get recommended volunteers for a case
    
    Matches volunteers based on:
    - Skills matching case requirements
    - Distance from case location
    - Availability status
    - Reliability score
    """
    from models.case import Case
    from models.volunteer import VolunteerProfile
    from geoalchemy2.functions import ST_Distance, ST_Transform, ST_GeomFromText
    from sqlalchemy import func
    
    # Check if case exists
    case = db.query(Case).filter(Case.id == case_id).first()
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
    
    # Get case location
    from geoalchemy2 import shape as geoshape
    if not case.location:
        return []
    
    case_location = geoshape.to_shape(case.location)
    search_point = f'POINT({case_location.x} {case_location.y})'
    
    # Query volunteers
    volunteers = db.query(VolunteerProfile).filter(
        VolunteerProfile.is_available == True,
        VolunteerProfile.is_verified == True
    ).order_by(
        VolunteerProfile.reliability_score.desc()
    ).limit(limit).all()
    
    # Format response with match score
    result = []
    for vol in volunteers:
        match_score = vol.reliability_score or 50.0
        
        result.append({
            "volunteer_id": str(vol.id),
            "user_id": str(vol.user_id),
            "match_score": float(match_score),
            "skills": vol.skills or [],
            "languages": vol.languages or [],
            "reliability_score": float(vol.reliability_score) if vol.reliability_score else 100.0,
            "total_cases_completed": vol.total_cases_completed or 0,
            "average_rating": float(vol.rating) if vol.rating else None,
        })
    
    return result


@router.get("/cases/search", response_model=List[CaseResponse])
async def search_cases(
    query: str = Query(..., min_length=3),
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """
    Full-text search for cases
    
    Uses PostgreSQL full-text search on title and description
    """
    try:
        case_service = CaseService(db)
        cases = case_service.search_cases(query, limit=per_page)
        
        return [CaseResponse(**case_to_dict(case)) for case in cases]
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Search failed: {str(e)}"
        )
