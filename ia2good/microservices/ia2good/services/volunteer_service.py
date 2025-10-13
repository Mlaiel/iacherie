"""Business logic for volunteer management"""
from datetime import datetime
from typing import List, Optional
from uuid import UUID

from sqlalchemy.orm import Session
from sqlalchemy import and_, or_

from api.schemas.volunteer import VolunteerProfileCreate, VolunteerProfileUpdate
from models.volunteer import VolunteerProfile


class VolunteerService:
    """Service for volunteer profile management"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create_profile(
        self,
        data: VolunteerProfileCreate,
        user_id: UUID
    ) -> Optional[VolunteerProfile]:
        """
        Create volunteer profile
        
        Business logic:
        1. Check if user already has profile
        2. Validate skills
        3. Geocode location if needed
        4. Create profile (status=pending)
        5. Send verification email
        6. Assign 'volunteer' role
        
        Args:
            data: Profile creation data
            user_id: User ID
            
        Returns:
            Created profile or None if already exists
        """
        # Check for existing profile
        existing = self.db.query(VolunteerProfile).filter(
            VolunteerProfile.user_id == user_id
        ).first()
        
        if existing:
            return None
        
        # Create profile
        profile = VolunteerProfile(
            user_id=user_id,
            location=f"POINT({data.location.longitude} {data.location.latitude})",
            address=data.address,
            city=data.city,
            country=data.country,
            skills=data.skills,
            languages=data.languages,
            certifications=data.certifications,
            availability_status=True,
            availability_schedule=data.availability_schedule,
            max_distance_km=data.max_distance_km,
            notification_radius_km=data.notification_radius_km,
            preferred_case_types=data.preferred_case_types,
            verification_status='pending'
        )
        
        self.db.add(profile)
        self.db.commit()
        self.db.refresh(profile)
        
        # TODO: Send verification email
        # TODO: Assign volunteer role
        
        return profile
    
    def get_profile_by_id(self, profile_id: UUID) -> Optional[VolunteerProfile]:
        """
        Get volunteer profile by ID
        
        Args:
            profile_id: Profile UUID
            
        Returns:
            Profile or None
        """
        return self.db.query(VolunteerProfile).filter(
            VolunteerProfile.id == profile_id
        ).first()
    
    def get_profile_by_user_id(self, user_id: UUID) -> Optional[VolunteerProfile]:
        """
        Get volunteer profile by user ID
        
        Args:
            user_id: User UUID
            
        Returns:
            Profile or None
        """
        return self.db.query(VolunteerProfile).filter(
            VolunteerProfile.user_id == user_id
        ).first()
    
    def get_volunteers(
        self,
        skills: Optional[List[str]] = None,
        city: Optional[str] = None,
        available: Optional[bool] = None,
        verified_only: bool = True,
        page: int = 1,
        per_page: int = 20
    ) -> tuple[List[VolunteerProfile], int]:
        """
        Get volunteers with filters
        
        Args:
            skills: Filter by skills
            city: Filter by city
            available: Filter by availability
            verified_only: Only verified volunteers
            page: Page number
            per_page: Items per page
            
        Returns:
            Tuple of (profiles list, total count)
        """
        query = self.db.query(VolunteerProfile)
        
        if verified_only:
            query = query.filter(VolunteerProfile.verification_status == 'verified')
        
        if skills:
            query = query.filter(VolunteerProfile.skills.overlap(skills))
        
        if city:
            query = query.filter(VolunteerProfile.city.ilike(f'%{city}%'))
        
        if available is not None:
            query = query.filter(VolunteerProfile.availability_status == available)
        
        total = query.count()
        
        # Sort by reliability score
        query = query.order_by(VolunteerProfile.reliability_score.desc())
        
        # Pagination
        offset = (page - 1) * per_page
        profiles = query.offset(offset).limit(per_page).all()
        
        return profiles, total
    
    def get_nearby_volunteers(
        self,
        latitude: float,
        longitude: float,
        radius_km: float = 10.0,
        skills: Optional[List[str]] = None,
        available_only: bool = True
    ) -> List[VolunteerProfile]:
        """
        Get volunteers near a location
        
        Args:
            latitude: Latitude
            longitude: Longitude
            radius_km: Search radius in km
            skills: Required skills
            available_only: Only available volunteers
            
        Returns:
            List of nearby volunteers
        """
        # TODO: Implement PostGIS ST_DWithin query
        # For now, return available verified volunteers
        query = self.db.query(VolunteerProfile).filter(
            VolunteerProfile.verification_status == 'verified'
        )
        
        if available_only:
            query = query.filter(VolunteerProfile.availability_status == True)
        
        if skills:
            query = query.filter(VolunteerProfile.skills.overlap(skills))
        
        volunteers = query.limit(20).all()
        
        return volunteers
    
    def update_profile(
        self,
        profile_id: UUID,
        updates: VolunteerProfileUpdate,
        user_id: UUID
    ) -> Optional[VolunteerProfile]:
        """
        Update volunteer profile
        
        Args:
            profile_id: Profile UUID
            updates: Update data
            user_id: User making update
            
        Returns:
            Updated profile or None
        """
        profile = self.get_profile_by_id(profile_id)
        if not profile:
            return None
        
        # Verify ownership
        if profile.user_id != user_id:
            return None
        
        # Apply updates
        update_data = updates.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            if field == 'location' and value:
                # Convert location to PostGIS format
                setattr(profile, field, f"POINT({value.longitude} {value.latitude})")
            else:
                setattr(profile, field, value)
        
        profile.updated_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(profile)
        
        return profile
    
    def update_availability(
        self,
        profile_id: UUID,
        status: bool,
        user_id: UUID
    ) -> Optional[VolunteerProfile]:
        """
        Toggle volunteer availability
        
        Args:
            profile_id: Profile UUID
            status: New availability status
            user_id: User making update
            
        Returns:
            Updated profile or None
        """
        profile = self.get_profile_by_id(profile_id)
        if not profile:
            return None
        
        # Verify ownership
        if profile.user_id != user_id:
            return None
        
        profile.availability_status = status
        profile.last_active_at = datetime.utcnow()
        profile.updated_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(profile)
        
        return profile
    
    def verify_volunteer(
        self,
        profile_id: UUID,
        verified_by: UUID,
        identity_verified: bool = False,
        background_check: bool = False
    ) -> Optional[VolunteerProfile]:
        """
        Verify volunteer (admin only)
        
        Args:
            profile_id: Profile UUID
            verified_by: Admin user ID
            identity_verified: Identity verification status
            background_check: Background check status
            
        Returns:
            Updated profile or None
        """
        profile = self.get_profile_by_id(profile_id)
        if not profile:
            return None
        
        # TODO: Check if verified_by is admin
        
        profile.verification_status = 'verified'
        profile.verified_at = datetime.utcnow()
        profile.verified_by = verified_by
        profile.identity_verified = identity_verified
        profile.background_check = background_check
        profile.updated_at = datetime.utcnow()
        
        self.db.commit()
        self.db.refresh(profile)
        
        # TODO: Send verification confirmation email
        
        return profile
    
    def calculate_reliability_score(self, profile_id: UUID) -> float:
        """
        Calculate volunteer reliability score
        
        Formula:
        - Completion rate (60%): completed / (completed + cancelled)
        - Response time (20%): avg_response_time (inversed)
        - Rating (20%): average_rating / 5 * 100
        
        Args:
            profile_id: Profile UUID
            
        Returns:
            Score between 0-100
        """
        profile = self.get_profile_by_id(profile_id)
        if not profile:
            return 0.0
        
        # TODO: Query assignments to calculate real metrics
        # For now, return current score or default
        
        if profile.total_cases_completed == 0:
            return 100.0  # New volunteers start at 100
        
        # Simplified calculation
        completion_rate = 100.0  # Assume perfect for now
        response_score = 100.0
        rating_score = (profile.average_rating / 5.0 * 100.0) if profile.average_rating else 100.0
        
        score = (
            completion_rate * 0.6 +
            response_score * 0.2 +
            rating_score * 0.2
        )
        
        return min(max(score, 0.0), 100.0)
    
    def update_stats(
        self,
        profile_id: UUID,
        cases_completed: int = 0,
        hours_volunteered: int = 0
    ):
        """
        Update volunteer statistics
        
        Args:
            profile_id: Profile UUID
            cases_completed: Number of cases to add
            hours_volunteered: Hours to add
        """
        profile = self.get_profile_by_id(profile_id)
        if not profile:
            return
        
        profile.total_cases_completed += cases_completed
        profile.total_hours_volunteered += hours_volunteered
        profile.reliability_score = self.calculate_reliability_score(profile_id)
        profile.updated_at = datetime.utcnow()
        
        self.db.commit()
    
    def add_rating(
        self,
        profile_id: UUID,
        rating: int
    ):
        """
        Add a rating to volunteer
        
        Args:
            profile_id: Profile UUID
            rating: Rating value (1-5)
        """
        profile = self.get_profile_by_id(profile_id)
        if not profile:
            return
        
        # Calculate new average
        current_total = (profile.average_rating or 0) * profile.total_ratings
        new_total = current_total + rating
        profile.total_ratings += 1
        profile.average_rating = new_total / profile.total_ratings
        profile.updated_at = datetime.utcnow()
        
        self.db.commit()
