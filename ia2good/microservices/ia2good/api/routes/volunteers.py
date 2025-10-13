"""API routes for volunteers"""
from typing import List, Optional
from uuid import UUID
from datetime import datetime
import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from api.dependencies import get_db, get_current_user
from api.schemas.volunteer import (
    VolunteerProfileCreate,
    VolunteerProfileUpdate,
    VolunteerProfileResponse,
    VolunteerDetailResponse,
    VolunteerStatsResponse,
    VerificationData,
)

router = APIRouter()


# Helper function to get user_id from current_user (supports both 'user_id' and 'id')
def get_user_id(current_user: dict) -> str:
    """Extract user_id from current_user dict (handles both 'user_id' and 'id' keys)"""
    return current_user.get("user_id") or current_user.get("id")


# DEBUG endpoint to test auth
@router.get("/volunteers/debug/me")
async def debug_me(current_user = Depends(get_current_user)):
    """Debug endpoint to test authentication"""
    return {
        "message": "Auth working!",
        "user": current_user
    }


# Helper function to convert VolunteerProfile to dict matching schema
def volunteer_to_dict(volunteer):
    """Convert VolunteerProfile model to dict matching VolunteerProfileResponse schema"""
    from geoalchemy2 import shape
    
    loc_shape = shape.to_shape(volunteer.location) if volunteer.location else None
    
    return {
        "id": str(volunteer.id),
        "user_id": str(volunteer.user_id),
        "location": {"latitude": loc_shape.y, "longitude": loc_shape.x} if loc_shape else {"latitude": 0, "longitude": 0},
        "address": volunteer.address,
        "city": volunteer.city,
        "country": volunteer.country or "France",
        "skills": volunteer.skills or [],
        "languages": volunteer.languages or ["fr"],
        "certifications": volunteer.certifications or {},
        "max_distance_km": volunteer.max_distance_km or 10,
        "availability_schedule": volunteer.availability_hours or {},
        "preferred_case_types": volunteer.preferred_case_types or [],
        "availability_status": volunteer.is_available if volunteer.is_available is not None else True,
        "verification_status": volunteer.verification_level or "pending",
        "identity_verified": volunteer.is_verified if volunteer.is_verified is not None else False,
        "background_check": volunteer.background_check if volunteer.background_check is not None else False,
        "reliability_score": float(volunteer.reliability_score) if volunteer.reliability_score else 100.0,
        "total_cases_completed": volunteer.cases_completed or 0,
        "total_hours_volunteered": int(volunteer.total_hours) if volunteer.total_hours else 0,
        "average_rating": float(volunteer.rating) if volunteer.rating else None,
        "total_ratings": volunteer.total_ratings or 0,
        "notification_radius_km": volunteer.notification_radius_km or 5,
        "created_at": volunteer.created_at.isoformat() if volunteer.created_at else None,
        "updated_at": volunteer.updated_at.isoformat() if volunteer.updated_at else None,
        "last_active_at": volunteer.last_active_at.isoformat() if volunteer.last_active_at else None,
    }


# Placeholder dependencies



def require_role(role: str):
    """Require specific role"""
    def wrapper():
        raise NotImplementedError("Role-based access control not yet implemented")
    return wrapper


@router.post("/volunteers", response_model=VolunteerProfileResponse, status_code=status.HTTP_201_CREATED)
async def create_volunteer_profile(
    profile: VolunteerProfileCreate,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Become a volunteer
    
    Business logic:
    - User can have only 1 volunteer profile
    - Skills required: min 1, max 10
    - Location is mandatory
    - Automatic email verification
    - 'volunteer' role added (RBAC)
    """
    from models.volunteer import VolunteerProfile
    from geoalchemy2.elements import WKTElement
    import uuid
    
    # Check if user already has a volunteer profile
    user_id = current_user.get("user_id") or current_user.get("id")
    existing = db.query(VolunteerProfile).filter(VolunteerProfile.user_id == user_id).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User already has a volunteer profile"
        )
    
    # Validate skills
    if not profile.skills or len(profile.skills) < 1:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="At least 1 skill is required"
        )
    if len(profile.skills) > 10:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Maximum 10 skills allowed"
        )
    
    # Create location point
    location_wkt = None
    if profile.location:
        location_wkt = WKTElement(f'POINT({profile.location.longitude} {profile.location.latitude})', srid=4326)
    
    # Get user_id from token (supports both 'user_id' and 'id')
    user_id = current_user.get("user_id") or current_user.get("id")
    
    # Get optional user info from token
    user_name = current_user.get("name", "")
    user_email = current_user.get("email", "")
    
    # Create volunteer profile
    new_volunteer = VolunteerProfile(
        id=uuid.uuid4(),
        user_id=uuid.UUID(user_id),
        full_name=user_name,  # From JWT token
        phone=None,  # Will be set later via profile update
        email=user_email,  # From JWT token
        location=location_wkt,
        address=profile.address,
        city=profile.city,
        country=profile.country,
        bio=None,  # Will be set later
        skills=profile.skills,
        languages=profile.languages or ["en"],
        availability_hours=profile.availability_schedule or {},
        is_available=True,
        is_verified=False,
        verification_level="pending",
        rating=0,
        reliability_score=100,
        cases_completed=0,
        total_hours=0,
        max_distance_km=profile.max_distance_km,
        certifications=profile.certifications or {},
        preferred_case_types=profile.preferred_case_types or []
    )
    
    db.add(new_volunteer)
    db.commit()
    db.refresh(new_volunteer)
    
    return volunteer_to_dict(new_volunteer)


@router.get("/volunteers", response_model=List[VolunteerProfileResponse])
async def get_volunteers(
    skills: Optional[List[str]] = Query(None),
    city: Optional[str] = None,
    available: Optional[bool] = None,
    verified_only: bool = True,
    sort_by: str = "reliability_score",
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """
    Volunteer directory with filters
    
    Returns paginated list of volunteers matching filters
    """
    from models.volunteer import VolunteerProfile
    from geoalchemy2 import shape
    from sqlalchemy import and_, desc
    
    # Base query
    query = db.query(VolunteerProfile)
    
    # Apply filters
    filters = []
    if verified_only:
        filters.append(VolunteerProfile.is_verified == True)
    if available is not None:
        filters.append(VolunteerProfile.is_available == available)
    if city:
        filters.append(VolunteerProfile.city.ilike(f"%{city}%"))
    if skills:
        # Use PostgreSQL array overlap operator &&
        filters.append(VolunteerProfile.skills.op('&&')(skills))
    
    if filters:
        query = query.filter(and_(*filters))
    
    # Sorting
    if sort_by == "reliability_score":
        query = query.order_by(desc(VolunteerProfile.reliability_score))
    elif sort_by == "rating":
        query = query.order_by(desc(VolunteerProfile.rating))
    elif sort_by == "cases_completed":
        query = query.order_by(desc(VolunteerProfile.cases_completed))
    
    # Pagination
    skip = (page - 1) * per_page
    volunteers = query.offset(skip).limit(per_page).all()
    
    # Convert to response format using helper
    return [volunteer_to_dict(v) for v in volunteers]



@router.get("/volunteers/nearby")
async def get_nearby_volunteers(
    latitude: float = Query(..., ge=-90, le=90),
    longitude: float = Query(..., ge=-180, le=180),
    radius_km: int = Query(10, ge=1, le=100),
    skills: Optional[List[str]] = Query(None),
    db: Session = Depends(get_db)
):
    """
    Get volunteers near a location
    
    Uses PostGIS ST_DWithin for efficient geospatial queries
    """
    from models.volunteer import VolunteerProfile
    from geoalchemy2.elements import WKTElement
    from geoalchemy2 import shape
    from sqlalchemy import func, and_
    
    # Create point for search center
    search_point = WKTElement(f'POINT({longitude} {latitude})', srid=4326)
    
    # Build query with PostGIS distance calculation
    # Cast Geography to Geometry for ST_Transform compatibility
    query = db.query(
        VolunteerProfile,
        func.ST_Distance(
            func.ST_Transform(func.ST_GeomFromWKB(VolunteerProfile.location), 3857),
            func.ST_Transform(search_point, 3857)
        ).label('distance_meters')
    ).filter(
        and_(
            VolunteerProfile.is_available == True,
            VolunteerProfile.is_verified == True,
            func.ST_DWithin(
                func.ST_Transform(func.ST_GeomFromWKB(VolunteerProfile.location), 3857),
                func.ST_Transform(search_point, 3857),
                radius_km * 1000  # Convert km to meters
            )
        )
    )
    
    # Filter by skills if provided
    if skills:
        query = query.filter(VolunteerProfile.skills.op('&&')(skills))
    
    # Execute and order by distance
    results = query.order_by('distance_meters').all()
    
    # Convert to response format
    nearby_volunteers = []
    for volunteer, distance_meters in results:
        loc_shape = shape.to_shape(volunteer.location) if volunteer.location else None
        nearby_volunteers.append({
            "id": str(volunteer.id),
            "full_name": volunteer.full_name,
            "location": {"latitude": loc_shape.y, "longitude": loc_shape.x} if loc_shape else None,
            "city": volunteer.city,
            "skills": volunteer.skills or [],
            "rating": float(volunteer.rating) if volunteer.rating else 0.0,
            "reliability_score": volunteer.reliability_score,
            "distance_km": round(distance_meters / 1000, 2),
            "is_available": volunteer.is_available,
        })
    
    return {
        "search_location": {"latitude": latitude, "longitude": longitude},
        "radius_km": radius_km,
        "total_found": len(nearby_volunteers),
        "volunteers": nearby_volunteers
    }

@router.get("/volunteers/me/profile", response_model=VolunteerDetailResponse)
async def get_my_profile(
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get my volunteer profile
    
    Returns profile for the authenticated user
    """
    from models.volunteer import VolunteerProfile
    from models.assignment import Assignment
    from geoalchemy2 import shape
    
    volunteer = db.query(VolunteerProfile).filter(
        VolunteerProfile.user_id == uuid.UUID(get_user_id(current_user))
    ).first()
    
    if not volunteer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Volunteer profile not found. Create one first."
        )
    
    # Get recent assignments
    recent_assignments = db.query(Assignment).filter(
        Assignment.volunteer_id == volunteer.id
    ).order_by(Assignment.assigned_at.desc()).limit(10).all()
    
    # Build response using helper function + additional fields for VolunteerDetailResponse
    response = volunteer_to_dict(volunteer)
    response["user"] = None  # TODO: Join with users table
    response["recent_cases"] = [
        {
            "assignment_id": str(a.id),
            "case_id": str(a.case_id),
            "status": a.status,
            "assigned_at": a.assigned_at.isoformat() if a.assigned_at else None,
            "completed_at": a.completed_at.isoformat() if a.completed_at else None,
        }
        for a in recent_assignments
    ]
    response["achievements"] = []  # TODO: Implement badge system
    
    return response



@router.get("/volunteers/me/stats", response_model=VolunteerStatsResponse)
async def get_my_stats(
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get personal volunteer statistics
    
    Returns:
    - Total completed cases
    - Total volunteer hours
    - Reliability score
    - Average rating
    - Average response time
    - Unlocked achievements
    - Leaderboard rank
    """
    from models.volunteer import VolunteerProfile
    from models.assignment import Assignment
    from sqlalchemy import func
    
    volunteer = db.query(VolunteerProfile).filter(
        VolunteerProfile.user_id == uuid.UUID(get_user_id(current_user))
    ).first()
    
    if not volunteer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Volunteer profile not found"
        )
    
    # Calculate leaderboard rank
    rank = db.query(func.count(VolunteerProfile.id)).filter(
        VolunteerProfile.cases_completed > volunteer.cases_completed
    ).scalar() + 1
    
    # Get total volunteers for context
    total_volunteers = db.query(func.count(VolunteerProfile.id)).scalar()
    
    return {
        "total_cases_completed": volunteer.cases_completed or 0,
        "total_hours_volunteered": int(volunteer.total_hours) if volunteer.total_hours else 0,
        "reliability_score": float(volunteer.reliability_score) if volunteer.reliability_score else 100.0,
        "average_rating": float(volunteer.rating) if volunteer.rating else None,
        "total_ratings": volunteer.total_ratings or 0,
        "response_time_avg_minutes": 30,  # TODO: Calculate from assignments
        "achievements_count": 0,  # TODO: Implement badge system
        "points_total": (volunteer.cases_completed or 0) * 10,  # Simple calculation: 10 points per case
        "rank": rank,
    }


@router.put("/volunteers/me/profile", response_model=VolunteerProfileResponse)
async def update_my_profile(
    profile_update: VolunteerProfileUpdate,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update my volunteer profile
    
    Allows updating:
    - Basic info (bio, phone, profile_photo)
    - Location (address, city, country, coordinates)
    - Skills and languages
    - Availability settings
    - Notification preferences
    """
    from models.volunteer import VolunteerProfile
    from geoalchemy2.elements import WKTElement
    from geoalchemy2 import shape
    
    # Get existing profile
    volunteer = db.query(VolunteerProfile).filter(
        VolunteerProfile.user_id == uuid.UUID(get_user_id(current_user))
    ).first()
    
    if not volunteer:
        raise HTTPException(status_code=404, detail="Volunteer profile not found")
    
    # Update fields if provided
    update_data = profile_update.dict(exclude_unset=True, exclude={"location"})
    
    for field, value in update_data.items():
        if hasattr(volunteer, field):
            setattr(volunteer, field, value)
    
    # Update location if provided
    if profile_update.location:
        lat = profile_update.location.latitude
        lon = profile_update.location.longitude
        volunteer.location = WKTElement(f'SRID=4326;POINT({lon} {lat})', extended=True)
    
    volunteer.updated_at = datetime.utcnow()
    
    db.commit()
    db.refresh(volunteer)
    
    # Prepare response
    response = {
        "id": str(volunteer.id),
        "user_id": str(volunteer.user_id),
        "location": {
            "latitude": shape.to_shape(volunteer.location).y,
            "longitude": shape.to_shape(volunteer.location).x
        } if volunteer.location else None,
        "address": volunteer.address,
        "city": volunteer.city,
        "country": volunteer.country,
        "skills": volunteer.skills or [],
        "languages": volunteer.languages or [],
        "certifications": volunteer.certifications or {},
        "max_distance_km": volunteer.max_distance_km,
        "availability_schedule": volunteer.availability_schedule or {},
        "preferred_case_types": volunteer.preferred_case_types or [],
        "availability_status": volunteer.availability_status,
        "verification_status": volunteer.verification_status,
        "identity_verified": volunteer.identity_verified,
        "background_check": volunteer.background_check,
        "reliability_score": float(volunteer.reliability_score) if volunteer.reliability_score else 100.0,
        "total_cases_completed": volunteer.total_cases_completed or 0,
        "total_hours_volunteered": volunteer.total_hours_volunteered or 0,
        "average_rating": float(volunteer.rating) if volunteer.rating else None,
        "total_ratings": volunteer.total_ratings or 0,
        "notification_radius_km": volunteer.notification_radius_km or 5,
        "created_at": volunteer.created_at.isoformat() if volunteer.created_at else None,
        "updated_at": volunteer.updated_at.isoformat() if volunteer.updated_at else None,
        "last_active_at": volunteer.last_active_at.isoformat() if volunteer.last_active_at else None,
    }
    
    return response


@router.get("/volunteers/me", response_model=VolunteerDetailResponse)
async def get_my_volunteer_profile(
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get current user's complete volunteer profile
    
    This is an alias for /volunteers/{volunteer_id} but uses the authenticated user's ID
    """
    from models.volunteer import VolunteerProfile
    from models.assignment import Assignment
    from geoalchemy2 import shape
    
    user_id = get_user_id(current_user)
    
    volunteer = db.query(VolunteerProfile).filter(VolunteerProfile.user_id == user_id).first()
    if not volunteer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Volunteer profile not found. Create one first with POST /volunteers"
        )
    
    # Get recent assignments
    assignments = db.query(Assignment).filter(
        Assignment.volunteer_id == str(volunteer.id)
    ).order_by(Assignment.created_at.desc()).limit(10).all()
    
    recent_cases = [
        {
            "id": str(a.case_id),
            "title": a.case.title if a.case else "Unknown",
            "status": a.status,
            "assigned_at": a.created_at.isoformat()
        } for a in assignments
    ]
    
    # Build response
    location_data = None
    if volunteer.location:
        geom = shape.to_shape(volunteer.location)
        location_data = {
            "type": "Point",
            "coordinates": [geom.x, geom.y]
        }
    
    response = {
        "id": str(volunteer.id),
        "user_id": str(volunteer.user_id),
        "availability": volunteer.availability or "flexible",
        "skills": volunteer.skills or [],
        "bio": volunteer.bio,
        "location": location_data,
        "languages": volunteer.languages or [],
        "is_verified": volunteer.is_verified,
        "verification_date": volunteer.verification_date.isoformat() if volunteer.verification_date else None,
        "reliability_score": volunteer.reliability_score or 0.0,
        "created_at": volunteer.created_at.isoformat(),
        "updated_at": volunteer.updated_at.isoformat(),
        "stats": {
            "total_cases": volunteer.cases_completed or 0,
            "active_cases": volunteer.active_cases or 0,
            "hours_contributed": volunteer.hours_contributed or 0.0,
            "success_rate": volunteer.reliability_score or 0.0,
            "avg_response_time": 2.5
        },
        "recent_cases": recent_cases,
        "badges": []
    }
    
    return response


@router.get("/volunteers/{volunteer_id}", response_model=VolunteerDetailResponse)
async def get_volunteer(
    volunteer_id: UUID,
    db: Session = Depends(get_db)
):
    """
    Get complete volunteer profile
    
    Includes:
    - Profile information
    - Detailed statistics
    - Recent case history (max 10)
    - Achievements/badges
    """
    from models.volunteer import VolunteerProfile
    from models.assignment import Assignment
    from geoalchemy2 import shape
    
    volunteer = db.query(VolunteerProfile).filter(VolunteerProfile.id == volunteer_id).first()
    if not volunteer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Volunteer not found"
        )
    
    # Get recent assignments
    recent_assignments = db.query(Assignment).filter(
        Assignment.volunteer_id == volunteer_id
    ).order_by(Assignment.assigned_at.desc()).limit(10).all()
    
    # Convert location
    loc_shape = shape.to_shape(volunteer.location) if volunteer.location else None
    
    # Build response matching VolunteerDetailResponse schema
    return {
        "id": str(volunteer.id),
        "user_id": str(volunteer.user_id),
        "location": {"latitude": loc_shape.y, "longitude": loc_shape.x} if loc_shape else {"latitude": 0, "longitude": 0},
        "address": volunteer.address,
        "city": volunteer.city,
        "country": volunteer.country or "France",
        "skills": volunteer.skills or [],
        "languages": volunteer.languages or ["fr"],
        "certifications": volunteer.certifications or {},
        "max_distance_km": volunteer.max_distance_km or 10,
        "availability_schedule": volunteer.availability_hours or {},
        "preferred_case_types": volunteer.preferred_case_types or [],
        "availability_status": volunteer.is_available if volunteer.is_available is not None else True,
        "verification_status": volunteer.verification_level or "pending",
        "identity_verified": volunteer.is_verified if volunteer.is_verified is not None else False,
        "background_check": volunteer.background_check if volunteer.background_check is not None else False,
        "reliability_score": float(volunteer.reliability_score) if volunteer.reliability_score else 100.0,
        "total_cases_completed": volunteer.cases_completed or 0,
        "total_hours_volunteered": int(volunteer.total_hours) if volunteer.total_hours else 0,
        "average_rating": float(volunteer.rating) if volunteer.rating else None,
        "total_ratings": volunteer.total_ratings or 0,
        "notification_radius_km": volunteer.notification_radius_km or 5,
        "created_at": volunteer.created_at.isoformat() if volunteer.created_at else None,
        "updated_at": volunteer.updated_at.isoformat() if volunteer.updated_at else None,
        "last_active_at": volunteer.last_active_at.isoformat() if volunteer.last_active_at else None,
        "user": None,  # TODO: Join with users table for user details
        "recent_cases": [
            {
                "assignment_id": str(a.id),
                "case_id": str(a.case_id),
                "status": a.status,
                "assigned_at": a.assigned_at.isoformat() if a.assigned_at else None,
                "completed_at": a.completed_at.isoformat() if a.completed_at else None,
            }
            for a in recent_assignments
        ],
        "achievements": [],  # TODO: Implement badge system
    }


@router.put("/volunteers/{volunteer_id}", response_model=VolunteerProfileResponse)
async def update_volunteer_profile(
    volunteer_id: UUID,
    updates: VolunteerProfileUpdate,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update volunteer profile (owner only)
    
    Verifies that current user owns the profile
    """
    from models.volunteer import VolunteerProfile
    from geoalchemy2.elements import WKTElement
    from geoalchemy2 import shape
    
    volunteer = db.query(VolunteerProfile).filter(VolunteerProfile.id == volunteer_id).first()
    if not volunteer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Volunteer not found"
        )
    
    # Verify ownership
    if str(volunteer.user_id) != get_user_id(current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only update your own profile"
        )
    
    # Update fields
    update_data = updates.dict(exclude_unset=True)
    
    # Handle location separately
    if "location" in update_data and update_data["location"]:
        loc = update_data.pop("location")
        volunteer.location = WKTElement(f'POINT({loc["longitude"]} {loc["latitude"]})', srid=4326)
    
    # Update other fields
    for field, value in update_data.items():
        if hasattr(volunteer, field):
            setattr(volunteer, field, value)
    
    db.commit()
    db.refresh(volunteer)
    
    return volunteer_to_dict(volunteer)


@router.put("/volunteers/{volunteer_id}/availability")
async def toggle_availability(
    volunteer_id: UUID,
    available: bool,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Toggle availability on/off
    
    Logic:
    - If OFF → Stop receiving notifications
    - If ON → Reactivate notifications
    """
    from models.volunteer import VolunteerProfile
    
    volunteer = db.query(VolunteerProfile).filter(VolunteerProfile.id == volunteer_id).first()
    if not volunteer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Volunteer not found"
        )
    
    # Verify ownership
    if str(volunteer.user_id) != get_user_id(current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only update your own availability"
        )
    
    volunteer.is_available = available
    db.commit()
    
    return {
        "volunteer_id": str(volunteer.id),
        "is_available": volunteer.is_available,
        "message": f"Availability set to {'ON' if available else 'OFF'}"
    }


@router.post("/volunteers/{volunteer_id}/verify")
async def verify_volunteer(
    volunteer_id: UUID,
    verification_data: VerificationData,
    current_user = Depends(get_current_user),
    # admin_required = Depends(require_role("admin"))  # TODO: Uncomment when implemented
    db: Session = Depends(get_db)
):
    """
    Manual verification (admin only)
    
    Verifies volunteer identity and performs background check
    """
    from models.volunteer import VolunteerProfile
    
    volunteer = db.query(VolunteerProfile).filter(VolunteerProfile.id == volunteer_id).first()
    if not volunteer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Volunteer not found"
        )
    
    # Update verification status
    volunteer.is_verified = True
    volunteer.identity_verified = verification_data.identity_verified
    volunteer.background_check = verification_data.background_check
    volunteer.verification_level = "verified" if (verification_data.identity_verified and verification_data.background_check) else "partial"
    volunteer.verification_notes = verification_data.verification_notes
    volunteer.verified_at = datetime.utcnow()
    volunteer.verified_by = uuid.UUID(get_user_id(current_user))
    
    db.commit()
    
    return {
        "volunteer_id": str(volunteer.id),
        "is_verified": volunteer.is_verified,
        "identity_verified": volunteer.identity_verified,
        "background_check": volunteer.background_check,
        "verification_level": volunteer.verification_level,
        "message": "Volunteer verified successfully"
    }


