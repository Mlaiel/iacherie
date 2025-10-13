"""SQLAlchemy model for Volunteer Profile"""
from datetime import datetime
from uuid import uuid4

from sqlalchemy import (
    Column, String, Text, Integer, Float, Boolean,
    DateTime, ARRAY, JSON, Index
)
from sqlalchemy.dialects.postgresql import UUID
from geoalchemy2 import Geography

from .base import Base


class VolunteerProfile(Base):
    """Volunteer Profile model"""
    
    __tablename__ = 'ia2good_volunteer_profiles'
    
    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    user_id = Column(UUID(as_uuid=True), unique=True, nullable=False)  # Foreign key to users table
    
    # Personal Information
    full_name = Column(String(200), nullable=False)
    phone = Column(String(20))
    email = Column(String(255), nullable=False)
    bio = Column(Text)
    profile_photo = Column(String(500))
    
    # Location
    location = Column(Geography('POINT', srid=4326))
    address = Column(Text)
    city = Column(String(100))
    country = Column(String(50), default='France')
    
    # Skills & Availability
    skills = Column(ARRAY(String(50)), default=[])  # medical, transport, shelter, food, legal, psychological
    languages = Column(ARRAY(String(10)), default=['fr'])
    certifications = Column(JSON, default={})  # {first_aid: true, driver_license: true}
    
    # Availability
    availability_status = Column(Boolean, default=True)
    is_available = Column(Boolean, default=True)  # Alias for compatibility
    availability_schedule = Column(JSON, default={})  # {monday: {start: "09:00", end: "18:00"}}
    availability_hours = Column(JSON, default={})  # Alias for compatibility
    max_distance_km = Column(Integer, default=10)
    
    # Verification
    verification_status = Column(String(20), default='pending')  # pending, verified, rejected
    is_verified = Column(Boolean, default=False)  # Alias for compatibility
    verification_level = Column(String(20), default='pending')  # Alias for compatibility
    verification_notes = Column(Text)
    verified_at = Column(DateTime)
    verified_by = Column(UUID(as_uuid=True))  # Foreign key to users table
    identity_verified = Column(Boolean, default=False)
    background_check = Column(Boolean, default=False)
    
    # Statistics
    total_cases_completed = Column(Integer, default=0)
    cases_completed = Column(Integer, default=0)  # Alias for compatibility
    total_hours_volunteered = Column(Integer, default=0)
    total_hours = Column(Integer, default=0)  # Alias for compatibility
    reliability_score = Column(Float, default=100.0)
    average_rating = Column(Float)
    rating = Column(Float, default=0.0)  # Alias for compatibility
    total_ratings = Column(Integer, default=0)
    
    # Preferences
    notification_radius_km = Column(Integer, default=5)
    preferred_case_types = Column(ARRAY(String(20)), default=[])
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_active_at = Column(DateTime)
    
    # Indexes
    __table_args__ = (
        Index('idx_ia2good_volunteers_user_id', 'user_id'),
        Index('idx_ia2good_volunteers_status', 'availability_status'),
        Index('idx_ia2good_volunteers_location', 'location', postgresql_using='gist'),
        Index('idx_ia2good_volunteers_skills', 'skills', postgresql_using='gin'),
        Index('idx_ia2good_volunteers_verification', 'verification_status'),
    )
    
    def __repr__(self):
        return f"<VolunteerProfile(id={self.id}, user_id={self.user_id}, status='{self.verification_status}')>"
