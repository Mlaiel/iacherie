"""SQLAlchemy models for Achievements (Gamification)"""
from datetime import datetime
from uuid import uuid4

from sqlalchemy import (
    Column, String, Text, Integer,
    DateTime, JSON, Index, UniqueConstraint
)
from sqlalchemy.dialects.postgresql import UUID

from .base import Base


class Achievement(Base):
    """Achievement model - defines available achievements"""
    
    __tablename__ = 'ia2good_achievements'
    
    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    code = Column(String(50), unique=True, nullable=False)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    icon_url = Column(Text)
    category = Column(String(50))  # milestone, streak, special
    criteria = Column(JSON, nullable=False)  # Conditions to unlock
    points = Column(Integer, default=0)
    rarity = Column(String(20), default='common')  # common, rare, epic, legendary
    
    # Timestamp
    created_at = Column(DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f"<Achievement(code='{self.code}', name='{self.name}')>"


class UserAchievement(Base):
    """User Achievement model - tracks unlocked achievements"""
    
    __tablename__ = 'ia2good_user_achievements'
    
    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    user_id = Column(UUID(as_uuid=True), nullable=False)  # Foreign key to users
    achievement_id = Column(UUID(as_uuid=True), nullable=False)  # Foreign key to achievements
    
    # Progress
    unlocked_at = Column(DateTime, default=datetime.utcnow)
    progress = Column(Integer, default=100)  # Percentage
    
    # Constraints
    __table_args__ = (
        UniqueConstraint('user_id', 'achievement_id', name='uq_user_achievement'),
    )
    
    def __repr__(self):
        return f"<UserAchievement(user_id={self.user_id}, achievement_id={self.achievement_id})>"
