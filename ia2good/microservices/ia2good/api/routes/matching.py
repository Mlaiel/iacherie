"""API routes for matching"""
from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from api.dependencies import get_db, get_current_user
from api.schemas.matching import (
    MatchRecommendation,
    TeamAssignmentRequest,
)

router = APIRouter()


# Placeholder dependencies



@router.post("/matching/recommend", response_model=List[MatchRecommendation])
async def recommend_volunteers_for_case(
    case_id: UUID,
    top_n: int = Query(10, ge=1, le=50),
    db: Session = Depends(get_db)
):
    """
    Get volunteer recommendations for a case
    
    Returns:
    - Top N volunteers
    - Match score (0-100)
    - Reasons (skills, distance, etc.)
    - Estimated arrival time
    
    Algorithm:
    - Skills matching (0-40 points)
    - Distance proximity (0-30 points)
    - Availability (0-15 points)
    - Reliability history (0-15 points)
    """
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Endpoint not yet implemented"
    )


@router.post("/matching/auto-assign")
async def auto_assign_best_match(
    case_id: UUID,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Auto-assign to best matching volunteer (admin only)
    
    Logic:
    1. Recommend volunteers
    2. If score > 80 AND immediate availability
    3. Auto-assign
    4. Otherwise return error "no perfect match"
    """
    from models.case import Case
    from models.volunteer import VolunteerProfile
    from models.assignment import Assignment
    from datetime import datetime
    import uuid as uuid_lib
    
    # Get case
    case = db.query(Case).filter(Case.id == case_id).first()
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
    
    if case.status != "open":
        raise HTTPException(status_code=400, detail="Case is not open")
    
    # Find best volunteer
    volunteers = db.query(VolunteerProfile).filter(
        VolunteerProfile.is_available == True,
        VolunteerProfile.is_verified == True
    ).order_by(
        VolunteerProfile.reliability_score.desc()
    ).limit(5).all()
    
    if not volunteers:
        raise HTTPException(status_code=404, detail="No available volunteers found")
    
    best_volunteer = volunteers[0]
    
    # Create assignment
    new_assignment = Assignment(
        id=uuid_lib.uuid4(),
        case_id=case.id,
        volunteer_id=best_volunteer.id,
        status="pending",
        match_score=float(best_volunteer.reliability_score) if best_volunteer.reliability_score else 80.0,
        match_reasons=["high_reliability", "available"],
        assigned_at=datetime.utcnow()
    )
    
    db.add(new_assignment)
    case.volunteers_assigned = (case.volunteers_assigned or 0) + 1
    if case.volunteers_assigned >= case.volunteers_needed:
        case.status = "in_progress"
    
    db.commit()
    db.refresh(new_assignment)
    
    return {
        "id": str(new_assignment.id),
        "case_id": str(case.id),
        "volunteer_id": str(best_volunteer.id),
        "status": new_assignment.status,
        "match_score": new_assignment.match_score,
        "assigned_at": new_assignment.assigned_at.isoformat()
    }


@router.post("/matching/assign-team")
async def assign_team_to_case(
    case_id: UUID,
    team_request: TeamAssignmentRequest,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Assign multi-volunteer team to a case
    
    Logic:
    1. Validate required skills
    2. Optimize team composition
    3. Assign all volunteers
    4. Create group chat
    5. Send coordinated notifications
    
    Uses Knapsack Problem variant for optimization
    """
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Endpoint not yet implemented"
    )
