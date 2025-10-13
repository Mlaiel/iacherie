"""SQLAlchemy model for Case"""
from datetime import datetime
from uuid import uuid4

from sqlalchemy import (
    Column, String, Text, Integer, Float, Boolean,
    DateTime, ARRAY, JSON, Index
)
from sqlalchemy.dialects.postgresql import UUID
from geoalchemy2 import Geography

from .base import Base


class Case(Base):
    """Case model - represents humanitarian cases"""
    
    __tablename__ = 'ia2good_cases'
    
    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    user_id = Column(UUID(as_uuid=True), nullable=False)  # Foreign key to users table
    
    # Case information
    type = Column(String(20), nullable=False)  # homeless, animal, emergency, other
    status = Column(String(20), default='open', nullable=False)  # open, claimed, in_progress, completed, cancelled
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    
    # Geolocation
    location = Column(Geography('POINT', srid=4326), nullable=False)
    address = Column(Text)
    city = Column(String(100))
    country = Column(String(50), default='France')
    
    # Urgency & Classification
    urgency_level = Column(Integer, default=5)  # 1-10
    ai_classification = Column(JSON, default={})
    tags = Column(ARRAY(String(50)), default=[])
    
    # Media
    photos = Column(ARRAY(Text), default=[])
    main_photo = Column(Text)
    
    # Metadata
    views_count = Column(Integer, default=0)
    shares_count = Column(Integer, default=0)
    volunteers_needed = Column(Integer, default=1)
    volunteers_assigned = Column(Integer, default=0)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    completed_at = Column(DateTime)
    deleted_at = Column(DateTime)
    
    # Indexes
    __table_args__ = (
        Index('idx_ia2good_cases_user_id', 'user_id'),
        Index('idx_ia2good_cases_type', 'type'),
        Index('idx_ia2good_cases_status', 'status'),
        Index('idx_ia2good_cases_urgency', 'urgency_level'),
        Index('idx_ia2good_cases_created', 'created_at'),
        Index('idx_ia2good_cases_location', 'location', postgresql_using='gist'),
    )
    
    def __repr__(self):
        return f"<Case(id={self.id}, title='{self.title}', status='{self.status}')>"
