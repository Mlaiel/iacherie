"""SQLAlchemy model for Assignment"""
from datetime import datetime
from uuid import uuid4

from sqlalchemy import (
    Column, String, Text, Integer, Float,
    DateTime, JSON, Index, UniqueConstraint
)
from sqlalchemy.dialects.postgresql import UUID

from .base import Base


class Assignment(Base):
    """Assignment model - represents volunteer assignments to cases"""
    
    __tablename__ = 'ia2good_case_assignments'
    
    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    case_id = Column(UUID(as_uuid=True), nullable=False)  # Foreign key to cases
    volunteer_id = Column(UUID(as_uuid=True), nullable=False)  # Foreign key to volunteer_profiles
    
    # Status
    status = Column(String(20), default='pending')  # pending, accepted, declined, in_progress, completed, cancelled
    
    # Matching
    match_score = Column(Float)  # 0-100
    match_reasons = Column(JSON, default={})
    
    # Timestamps
    assigned_at = Column(DateTime, default=datetime.utcnow)
    accepted_at = Column(DateTime)
    declined_at = Column(DateTime)
    started_at = Column(DateTime)
    completed_at = Column(DateTime)
    cancelled_at = Column(DateTime)
    
    # Response time
    response_time_minutes = Column(Integer)
    completion_time_minutes = Column(Integer)
    
    # Feedback
    completion_notes = Column(Text)
    volunteer_rating = Column(Integer)  # 1-5
    volunteer_feedback = Column(Text)
    reporter_rating = Column(Integer)  # 1-5
    reporter_feedback = Column(Text)
    
    # Constraints & Indexes
    __table_args__ = (
        UniqueConstraint('case_id', 'volunteer_id', name='uq_case_volunteer'),
        Index('idx_ia2good_assignments_case', 'case_id'),
        Index('idx_ia2good_assignments_volunteer', 'volunteer_id'),
        Index('idx_ia2good_assignments_status', 'status'),
        Index('idx_ia2good_assignments_assigned', 'assigned_at'),
    )
    
    def __repr__(self):
        return f"<Assignment(id={self.id}, case_id={self.case_id}, status='{self.status}')>"
