"""SQLAlchemy model for Activity Log"""
from datetime import datetime
from uuid import uuid4

from sqlalchemy import (
    Column, String, Text,
    DateTime, JSON, Index
)
from sqlalchemy.dialects.postgresql import UUID

from .base import Base


class ActivityLog(Base):
    """Activity Log model - tracks all activities for cases"""
    
    __tablename__ = 'ia2good_activity_log'
    
    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    case_id = Column(UUID(as_uuid=True))  # Foreign key to cases
    user_id = Column(UUID(as_uuid=True))  # Foreign key to users
    volunteer_id = Column(UUID(as_uuid=True))  # Foreign key to volunteer_profiles
    
    # Activity details
    activity_type = Column(String(50), nullable=False)  # case_created, case_updated, volunteer_assigned, etc.
    description = Column(Text)
    meta = Column('metadata', JSON, default={})
    
    # Timestamp
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Indexes
    __table_args__ = (
        Index('idx_ia2good_activity_case', 'case_id'),
        Index('idx_ia2good_activity_user', 'user_id'),
        Index('idx_ia2good_activity_created', 'created_at'),
    )
    
    def __repr__(self):
        return f"<ActivityLog(id={self.id}, type='{self.activity_type}')>"
