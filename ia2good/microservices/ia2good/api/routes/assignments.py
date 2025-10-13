"""API routes for assignments"""
from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from api.dependencies import get_db, get_current_user
from api.schemas.matching import (
    AssignmentCreate,
    AssignmentResponse,
    AssignmentCompletion,
    AssignmentStatus,
    RatingData,
)

router = APIRouter()


# Placeholder dependencies



@router.post("/assignments", response_model=AssignmentResponse, status_code=status.HTTP_201_CREATED)
async def create_assignment(
    assignment: AssignmentCreate,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Assign a volunteer to a case
    
    Business logic:
    1. Verify case exists and status=open
    2. Verify volunteer is available
    3. Calculate match_score
    4. Create assignment (status=pending)
    5. Send notification to volunteer (push + SMS if urgent)
    6. Send notification to reporter
    7. Update case.volunteers_assigned++
    8. Log activity
    """
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Endpoint not yet implemented"
    )


@router.get("/assignments/me", response_model=List[AssignmentResponse])
async def get_my_assignments(
    status_filter: Optional[AssignmentStatus] = None,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get my assignments (volunteer view)
    
    Returns assignments for the authenticated volunteer
    """
    from models.assignment import Assignment
    from models.volunteer import VolunteerProfile
    from models.case import Case
    import uuid
    
    # Helper function to get user_id from JWT
    def get_user_id(user_dict):
        return str(user_dict.get("user_id") or user_dict.get("id") or user_dict.get("sub"))
    
    # Get volunteer profile
    volunteer = db.query(VolunteerProfile).filter(
        VolunteerProfile.user_id == uuid.UUID(get_user_id(current_user))
    ).first()
    
    if not volunteer:
        return []
    
    # Query assignments
    query = db.query(Assignment).filter(Assignment.volunteer_id == volunteer.id)
    
    if status_filter:
        query = query.filter(Assignment.status == status_filter.value)
    
    assignments = query.order_by(Assignment.assigned_at.desc()).limit(50).all()
    
    # Format response
    result = []
    for a in assignments:
        case = db.query(Case).filter(Case.id == a.case_id).first()
        
        result.append({
            "id": str(a.id),
            "case_id": str(a.case_id),
            "volunteer_id": str(a.volunteer_id),
            "status": a.status,
            "match_score": float(a.match_score) if a.match_score else None,
            "match_reasons": a.match_reasons or [],
            "assigned_at": a.assigned_at.isoformat() if a.assigned_at else None,
            "accepted_at": a.accepted_at.isoformat() if a.accepted_at else None,
            "declined_at": a.declined_at.isoformat() if a.declined_at else None,
            "started_at": a.started_at.isoformat() if a.started_at else None,
            "completed_at": a.completed_at.isoformat() if a.completed_at else None,
            "cancelled_at": a.cancelled_at.isoformat() if a.cancelled_at else None,
            "response_time_minutes": a.response_time_minutes,
            "completion_time_minutes": a.completion_time_minutes,
            "completion_notes": a.completion_notes,
            "volunteer_rating": a.volunteer_rating,
            "volunteer_feedback": a.volunteer_feedback,
            "reporter_rating": a.reporter_rating,
            "reporter_feedback": a.reporter_feedback,
            "case": {
                "title": case.title if case else None,
                "type": case.type if case else None,
                "status": case.status if case else None,
            } if case else None
        })
    
    return result


@router.get("/assignments")
async def list_assignments(
    status_filter: Optional[AssignmentStatus] = None,
    limit: int = 20,
    offset: int = 0,
    db: Session = Depends(get_db)
):
    """
    List all assignments (admin/moderator view)
    
    Returns paginated list of all assignments
    """
    from models.assignment import Assignment
    from models.case import Case
    
    query = db.query(Assignment)
    
    if status_filter:
        query = query.filter(Assignment.status == status_filter.value)
    
    assignments = query.order_by(Assignment.assigned_at.desc()).limit(limit).offset(offset).all()
    
    # Format response
    result = []
    for a in assignments:
        case = db.query(Case).filter(Case.id == a.case_id).first()
        
        result.append({
            "id": str(a.id),
            "case_id": str(a.case_id),
            "volunteer_id": str(a.volunteer_id),
            "status": a.status,
            "match_score": float(a.match_score) if a.match_score else None,
            "match_reasons": a.match_reasons or [],
            "assigned_at": a.assigned_at.isoformat() if a.assigned_at else None,
            "accepted_at": a.accepted_at.isoformat() if a.accepted_at else None,
            "declined_at": a.declined_at.isoformat() if a.declined_at else None,
            "started_at": a.started_at.isoformat() if a.started_at else None,
            "completed_at": a.completed_at.isoformat() if a.completed_at else None,
            "cancelled_at": a.cancelled_at.isoformat() if a.cancelled_at else None,
            "response_time_minutes": a.response_time_minutes,
            "completion_time_minutes": a.completion_time_minutes,
            "completion_notes": a.completion_notes,
            "volunteer_rating": a.volunteer_rating,
            "volunteer_feedback": a.volunteer_feedback,
            "reporter_rating": a.reporter_rating,
            "reporter_feedback": a.reporter_feedback,
            "case": {
                "title": case.title if case else None,
                "type": case.type if case else None,
                "status": case.status if case else None,
            } if case else None
        })
    
    return result


@router.get("/assignments/{assignment_id}", response_model=AssignmentResponse)
async def get_assignment(
    assignment_id: UUID,
    db: Session = Depends(get_db)
):
    """Get assignment details"""
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Endpoint not yet implemented"
    )


@router.put("/assignments/{assignment_id}/accept")
async def accept_assignment(
    assignment_id: UUID,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Volunteer accepts the case
    
    Logic:
    1. Verify status=pending
    2. Update status=accepted
    3. Update case status=claimed
    4. Calculate response_time
    5. Notify reporter
    6. Start completion timer
    """
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Endpoint not yet implemented"
    )


@router.put("/assignments/{assignment_id}/decline")
async def decline_assignment(
    assignment_id: UUID,
    reason: Optional[str] = None,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Volunteer declines the case
    
    Logic:
    1. Update status=declined
    2. Log decline reason
    3. If no other volunteers → trigger re-match
    4. Minor impact on reliability_score (-2)
    """
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Endpoint not yet implemented"
    )


@router.put("/assignments/{assignment_id}/start")
async def start_assignment(
    assignment_id: UUID,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Volunteer starts the mission
    
    Logic:
    1. Update status=in_progress
    2. Update case status=in_progress
    3. Timestamp started_at
    4. Notify reporter "volunteer en route"
    """
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Endpoint not yet implemented"
    )


@router.put("/assignments/{assignment_id}/complete")
async def complete_assignment(
    assignment_id: UUID,
    completion_data: AssignmentCompletion,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Complete the mission
    
    Logic:
    1. Update status=completed
    2. Update case status=completed
    3. Calculate completion_time
    4. Store completion notes
    5. Request rating (push notification)
    6. Update volunteer stats (total_cases_completed++)
    7. Check achievement unlocks
    8. Notify reporter "case resolved"
    """
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Endpoint not yet implemented"
    )


@router.put("/assignments/{assignment_id}/cancel")
async def cancel_assignment(
    assignment_id: UUID,
    reason: str,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Cancel assignment
    
    Logic:
    1. Update status=cancelled
    2. Update case status=open
    3. Impact reliability_score (-5)
    4. Trigger automatic re-match
    5. Notify reporter
    """
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Endpoint not yet implemented"
    )


@router.post("/assignments/{assignment_id}/rate")
async def rate_assignment(
    assignment_id: UUID,
    rating_data: RatingData,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Rate the intervention
    
    Logic:
    1. Store rating (1-5 stars)
    2. Store feedback
    3. Update volunteer.average_rating
    4. Update volunteer.reliability_score
    5. If rating < 3 → alert admin
    """
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Endpoint not yet implemented"
    )
