"""Business logic for case management"""
from datetime import datetime
from typing import List, Optional
from uuid import UUID

from sqlalchemy.orm import Session
from sqlalchemy import and_, or_

from api.schemas.case import CaseCreate, CaseUpdate, CaseFilters
from models.case import Case
from models.activity import ActivityLog


class CaseService:
    """Service for case management operations"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create_case(self, case_data: CaseCreate, user_id: UUID) -> Case:
        """
        Create a new humanitarian case
        
        Business logic:
        1. Validate data
        2. Upload photos to S3 (placeholder)
        3. Geocoding if necessary
        4. Create case in DB
        5. Schedule AI classification (async)
        6. Notify nearby volunteers
        7. Log activity
        
        Args:
            case_data: Case creation data
            user_id: ID of user creating the case
            
        Returns:
            Created Case object
        """
        # Create case instance
        case = Case(
            user_id=user_id,
            type=case_data.type,
            title=case_data.title,
            description=case_data.description,
            location=f"POINT({case_data.location.longitude} {case_data.location.latitude})",
            address=case_data.address,
            city=case_data.city,
            country=case_data.country,
            urgency_level=case_data.urgency_level or 5,
            tags=case_data.tags,
            volunteers_needed=case_data.volunteers_needed,
            photos=case_data.photos,
            main_photo=case_data.photos[0] if case_data.photos else None,
            status='open'
        )
        
        self.db.add(case)
        self.db.commit()
        self.db.refresh(case)
        
        # Log activity
        self._log_activity(
            case_id=case.id,
            user_id=user_id,
            activity_type='case_created',
            description=f'Case "{case.title}" created'
        )
        
        # TODO: Trigger async tasks
        # - AI classification
        # - Notify volunteers
        
        return case
    
    def get_cases(
        self,
        filters: Optional[CaseFilters] = None,
        page: int = 1,
        per_page: int = 20
    ) -> tuple[List[Case], int]:
        """
        Get cases with filters and pagination
        
        Args:
            filters: Filter criteria
            page: Page number
            per_page: Items per page
            
        Returns:
            Tuple of (cases list, total count)
        """
        query = self.db.query(Case).filter(Case.deleted_at.is_(None))
        
        if filters:
            if filters.type:
                query = query.filter(Case.type == filters.type)
            if filters.status:
                query = query.filter(Case.status == filters.status)
            if filters.urgency_min:
                query = query.filter(Case.urgency_level >= filters.urgency_min)
            if filters.city:
                query = query.filter(Case.city.ilike(f'%{filters.city}%'))
            if filters.tags:
                query = query.filter(Case.tags.overlap(filters.tags))
        
        total = query.count()
        
        # Apply sorting
        if filters and filters.sort_by:
            if filters.sort_order == 'desc':
                query = query.order_by(getattr(Case, filters.sort_by).desc())
            else:
                query = query.order_by(getattr(Case, filters.sort_by).asc())
        else:
            query = query.order_by(Case.created_at.desc())
        
        # Apply pagination
        offset = (page - 1) * per_page
        cases = query.offset(offset).limit(per_page).all()
        
        return cases, total
    
    def get_case_by_id(self, case_id: UUID, increment_views: bool = True) -> Optional[Case]:
        """
        Get case by ID
        
        Args:
            case_id: Case UUID
            increment_views: Whether to increment view count
            
        Returns:
            Case object or None
        """
        case = self.db.query(Case).filter(
            Case.id == case_id,
            Case.deleted_at.is_(None)
        ).first()
        
        if case and increment_views:
            case.views_count += 1
            self.db.commit()
        
        return case
    
    def update_case(
        self,
        case_id: UUID,
        updates: CaseUpdate,
        user_id: UUID
    ) -> Optional[Case]:
        """
        Update a case
        
        Args:
            case_id: Case UUID
            updates: Update data
            user_id: User making the update
            
        Returns:
            Updated case or None
        """
        case = self.get_case_by_id(case_id, increment_views=False)
        if not case:
            return None
        
        # Verify permissions (owner or admin)
        if case.user_id != user_id:
            # TODO: Check if user is admin
            return None
        
        # Apply updates
        update_data = updates.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(case, field, value)
        
        case.updated_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(case)
        
        # Log activity
        self._log_activity(
            case_id=case_id,
            user_id=user_id,
            activity_type='case_updated',
            description=f'Case "{case.title}" updated'
        )
        
        return case
    
    def delete_case(self, case_id: UUID, user_id: UUID) -> bool:
        """
        Soft delete a case
        
        Args:
            case_id: Case UUID
            user_id: User requesting deletion
            
        Returns:
            True if deleted, False otherwise
        """
        case = self.get_case_by_id(case_id, increment_views=False)
        if not case:
            return False
        
        # Verify permissions
        if case.user_id != user_id:
            # TODO: Check if user is admin
            return False
        
        # Soft delete
        case.deleted_at = datetime.utcnow()
        case.status = 'cancelled'
        self.db.commit()
        
        # Log activity
        self._log_activity(
            case_id=case_id,
            user_id=user_id,
            activity_type='case_deleted',
            description=f'Case "{case.title}" deleted'
        )
        
        # TODO: Cancel ongoing assignments
        # TODO: Notify assigned volunteers
        
        return True
    
    def search_cases(self, query: str, limit: int = 20) -> List[Case]:
        """
        Full-text search for cases
        
        Args:
            query: Search query
            limit: Max results
            
        Returns:
            List of matching cases
        """
        # TODO: Implement full-text search with PostgreSQL
        # For now, simple LIKE search
        cases = self.db.query(Case).filter(
            Case.deleted_at.is_(None),
            or_(
                Case.title.ilike(f'%{query}%'),
                Case.description.ilike(f'%{query}%')
            )
        ).limit(limit).all()
        
        return cases
    
    def get_nearby_cases(
        self,
        latitude: float,
        longitude: float,
        radius_km: float = 10.0,
        limit: int = 20
    ) -> List[Case]:
        """
        Get cases near a location
        
        Args:
            latitude: Latitude
            longitude: Longitude
            radius_km: Search radius in kilometers
            limit: Max results
            
        Returns:
            List of nearby cases
        """
        # TODO: Implement PostGIS geographic queries
        # For now, return all open cases
        cases = self.db.query(Case).filter(
            Case.deleted_at.is_(None),
            Case.status == 'open'
        ).limit(limit).all()
        
        return cases
    
    def add_case_photos(
        self,
        case_id: UUID,
        photo_urls: List[str],
        user_id: UUID
    ) -> Optional[Case]:
        """
        Add photos to a case
        
        Args:
            case_id: Case UUID
            photo_urls: List of photo URLs
            user_id: User adding photos
            
        Returns:
            Updated case or None
        """
        case = self.get_case_by_id(case_id, increment_views=False)
        if not case:
            return None
        
        # Verify permissions
        if case.user_id != user_id:
            return None
        
        # Add photos (max 5 total)
        current_photos = case.photos or []
        new_photos = current_photos + photo_urls
        case.photos = new_photos[:5]  # Limit to 5
        
        if not case.main_photo and new_photos:
            case.main_photo = new_photos[0]
        
        case.updated_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(case)
        
        return case
    
    def _log_activity(
        self,
        case_id: UUID,
        user_id: UUID,
        activity_type: str,
        description: str,
        metadata: dict = None
    ):
        """
        Log case activity
        
        Args:
            case_id: Case UUID
            user_id: User UUID
            activity_type: Type of activity
            description: Description
            metadata: Additional metadata
        """
        activity = ActivityLog(
            case_id=case_id,
            user_id=user_id,
            activity_type=activity_type,
            description=description,
            meta=metadata or {}
        )
        self.db.add(activity)
        self.db.commit()
