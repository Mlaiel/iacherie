"""Business logic for assignment management"""
from datetime import datetime
from typing import Optional
from uuid import UUID

from sqlalchemy.orm import Session

from api.schemas.matching import AssignmentCreate, AssignmentCompletion, RatingData
from models.assignment import Assignment


class AssignmentService:
    """Service for assignment workflow management"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create_assignment(
        self,
        case_id: UUID,
        volunteer_id: UUID,
        match_score: float,
        match_reasons: dict
    ) -> Assignment:
        """
        Create a new assignment
        
        Args:
            case_id: Case UUID
            volunteer_id: Volunteer profile UUID
            match_score: Match score (0-100)
            match_reasons: Reasons for match
            
        Returns:
            Created assignment
        """
        assignment = Assignment(
            case_id=case_id,
            volunteer_id=volunteer_id,
            match_score=match_score,
            match_reasons=match_reasons,
            status='pending'
        )
        
        self.db.add(assignment)
        self.db.commit()
        self.db.refresh(assignment)
        
        # TODO: Send notification to volunteer
        # TODO: Send notification to reporter
        # TODO: Update case.volunteers_assigned++
        
        return assignment
    
    def get_assignment_by_id(self, assignment_id: UUID) -> Optional[Assignment]:
        """
        Get assignment by ID
        
        Args:
            assignment_id: Assignment UUID
            
        Returns:
            Assignment or None
        """
        return self.db.query(Assignment).filter(
            Assignment.id == assignment_id
        ).first()
    
    def accept_assignment(
        self,
        assignment_id: UUID,
        volunteer_id: UUID
    ) -> Optional[Assignment]:
        """
        Volunteer accepts the assignment
        
        Logic:
        1. Verify status=pending
        2. Update status=accepted
        3. Update case status=claimed
        4. Calculate response_time
        5. Notify reporter
        
        Args:
            assignment_id: Assignment UUID
            volunteer_id: Volunteer profile UUID
            
        Returns:
            Updated assignment or None
        """
        assignment = self.get_assignment_by_id(assignment_id)
        if not assignment:
            return None
        
        # Verify volunteer
        if assignment.volunteer_id != volunteer_id:
            return None
        
        # Verify status
        if assignment.status != 'pending':
            return None
        
        # Update assignment
        assignment.status = 'accepted'
        assignment.accepted_at = datetime.utcnow()
        
        # Calculate response time
        if assignment.assigned_at:
            delta = assignment.accepted_at - assignment.assigned_at
            assignment.response_time_minutes = int(delta.total_seconds() / 60)
        
        self.db.commit()
        self.db.refresh(assignment)
        
        # TODO: Update case status to 'claimed'
        # TODO: Notify reporter
        
        return assignment
    
    def decline_assignment(
        self,
        assignment_id: UUID,
        volunteer_id: UUID,
        reason: Optional[str] = None
    ) -> Optional[Assignment]:
        """
        Volunteer declines the assignment
        
        Logic:
        1. Update status=declined
        2. Log decline reason
        3. If no other volunteers, trigger re-match
        4. Small impact on reliability_score (-2)
        
        Args:
            assignment_id: Assignment UUID
            volunteer_id: Volunteer profile UUID
            reason: Decline reason
            
        Returns:
            Updated assignment or None
        """
        assignment = self.get_assignment_by_id(assignment_id)
        if not assignment:
            return None
        
        # Verify volunteer
        if assignment.volunteer_id != volunteer_id:
            return None
        
        # Verify status
        if assignment.status != 'pending':
            return None
        
        # Update assignment
        assignment.status = 'declined'
        assignment.declined_at = datetime.utcnow()
        if reason:
            assignment.completion_notes = f"Declined: {reason}"
        
        self.db.commit()
        self.db.refresh(assignment)
        
        # TODO: Impact reliability score
        # TODO: Check if re-match needed
        
        return assignment
    
    def start_assignment(
        self,
        assignment_id: UUID,
        volunteer_id: UUID
    ) -> Optional[Assignment]:
        """
        Volunteer starts the mission
        
        Logic:
        1. Update status=in_progress
        2. Update case status=in_progress
        3. Timestamp started_at
        4. Notify reporter
        
        Args:
            assignment_id: Assignment UUID
            volunteer_id: Volunteer profile UUID
            
        Returns:
            Updated assignment or None
        """
        assignment = self.get_assignment_by_id(assignment_id)
        if not assignment:
            return None
        
        # Verify volunteer
        if assignment.volunteer_id != volunteer_id:
            return None
        
        # Verify status
        if assignment.status != 'accepted':
            return None
        
        # Update assignment
        assignment.status = 'in_progress'
        assignment.started_at = datetime.utcnow()
        
        self.db.commit()
        self.db.refresh(assignment)
        
        # TODO: Update case status to 'in_progress'
        # TODO: Notify reporter "volunteer on the way"
        
        return assignment
    
    def complete_assignment(
        self,
        assignment_id: UUID,
        volunteer_id: UUID,
        completion_data: AssignmentCompletion
    ) -> Optional[Assignment]:
        """
        Complete the assignment
        
        Logic:
        1. Update status=completed
        2. Update case status=completed
        3. Calculate completion_time
        4. Store notes
        5. Request rating
        6. Update volunteer stats
        7. Check achievement unlocks
        8. Notify reporter
        
        Args:
            assignment_id: Assignment UUID
            volunteer_id: Volunteer profile UUID
            completion_data: Completion data
            
        Returns:
            Updated assignment or None
        """
        assignment = self.get_assignment_by_id(assignment_id)
        if not assignment:
            return None
        
        # Verify volunteer
        if assignment.volunteer_id != volunteer_id:
            return None
        
        # Verify status
        if assignment.status != 'in_progress':
            return None
        
        # Update assignment
        assignment.status = 'completed'
        assignment.completed_at = datetime.utcnow()
        assignment.completion_notes = completion_data.notes
        
        # Calculate completion time
        if assignment.started_at:
            delta = assignment.completed_at - assignment.started_at
            assignment.completion_time_minutes = int(delta.total_seconds() / 60)
        
        self.db.commit()
        self.db.refresh(assignment)
        
        # TODO: Update case status to 'completed'
        # TODO: Update volunteer stats (total_cases_completed++)
        # TODO: Check achievements
        # TODO: Send rating request
        # TODO: Notify reporter
        
        return assignment
    
    def cancel_assignment(
        self,
        assignment_id: UUID,
        volunteer_id: UUID,
        reason: str
    ) -> Optional[Assignment]:
        """
        Cancel the assignment
        
        Logic:
        1. Update status=cancelled
        2. Update case status=open
        3. Impact reliability_score (-5)
        4. Trigger re-match
        5. Notify reporter
        
        Args:
            assignment_id: Assignment UUID
            volunteer_id: Volunteer profile UUID
            reason: Cancellation reason
            
        Returns:
            Updated assignment or None
        """
        assignment = self.get_assignment_by_id(assignment_id)
        if not assignment:
            return None
        
        # Verify volunteer
        if assignment.volunteer_id != volunteer_id:
            return None
        
        # Can't cancel completed assignments
        if assignment.status == 'completed':
            return None
        
        # Update assignment
        assignment.status = 'cancelled'
        assignment.cancelled_at = datetime.utcnow()
        assignment.completion_notes = f"Cancelled: {reason}"
        
        self.db.commit()
        self.db.refresh(assignment)
        
        # TODO: Update case status to 'open'
        # TODO: Impact reliability score (-5)
        # TODO: Trigger re-match
        # TODO: Notify reporter
        
        return assignment
    
    def rate_assignment(
        self,
        assignment_id: UUID,
        rating_data: RatingData,
        rater_type: str  # 'volunteer' or 'reporter'
    ) -> Optional[Assignment]:
        """
        Rate the assignment
        
        Logic:
        1. Store rating (1-5 stars)
        2. Store feedback
        3. Update volunteer.average_rating
        4. Update volunteer.reliability_score
        5. Alert admin if rating < 3
        
        Args:
            assignment_id: Assignment UUID
            rating_data: Rating data
            rater_type: Who is rating ('volunteer' or 'reporter')
            
        Returns:
            Updated assignment or None
        """
        assignment = self.get_assignment_by_id(assignment_id)
        if not assignment:
            return None
        
        # Can only rate completed assignments
        if assignment.status != 'completed':
            return None
        
        # Store rating based on rater type
        if rater_type == 'volunteer':
            assignment.volunteer_rating = rating_data.rating
            assignment.volunteer_feedback = rating_data.feedback
        else:  # reporter
            assignment.reporter_rating = rating_data.rating
            assignment.reporter_feedback = rating_data.feedback
        
        self.db.commit()
        self.db.refresh(assignment)
        
        # TODO: Update volunteer average rating
        # TODO: Update volunteer reliability score
        # TODO: Alert admin if rating < 3
        
        return assignment
    
    def get_volunteer_assignments(
        self,
        volunteer_id: UUID,
        status: Optional[str] = None
    ) -> list[Assignment]:
        """
        Get assignments for a volunteer
        
        Args:
            volunteer_id: Volunteer profile UUID
            status: Filter by status
            
        Returns:
            List of assignments
        """
        query = self.db.query(Assignment).filter(
            Assignment.volunteer_id == volunteer_id
        )
        
        if status:
            query = query.filter(Assignment.status == status)
        
        return query.order_by(Assignment.assigned_at.desc()).all()
    
    def get_case_assignments(
        self,
        case_id: UUID,
        status: Optional[str] = None
    ) -> list[Assignment]:
        """
        Get assignments for a case
        
        Args:
            case_id: Case UUID
            status: Filter by status
            
        Returns:
            List of assignments
        """
        query = self.db.query(Assignment).filter(
            Assignment.case_id == case_id
        )
        
        if status:
            query = query.filter(Assignment.status == status)
        
        return query.order_by(Assignment.assigned_at.desc()).all()
