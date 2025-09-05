"""🗃️ Database Models - Core Data Models
======================================
Module: database/models.py
Author: Fahed Mlaiel (mlaiel@live.de)
Type: Database Models - Production-Ready
Responsibility: Data models for content protection and monetization

⚠️  EXCLUSIVE INTELLECTUAL PROPERTY - FAHED MLAIEL ⚠️
(c) 2025 Fahed Mlaiel. All rights reserved.
Unauthorized use strictly prohibited and subject to legal prosecution.
Contact: mlaiel@live.de

This models module provides core data models for:
- User and creator management
- Content and fingerprint management
- Revenue tracking and analytics
- System configuration and logs
"""

import datetime
from typing import Optional, List, Dict, Any
from enum import Enum

# Optional imports for production features
try:
    from sqlalchemy import Column, Integer, String, DateTime, Float, Boolean, Text, JSON, ForeignKey
    from sqlalchemy.ext.declarative import declarative_base
    from sqlalchemy.orm import relationship
    SQLALCHEMY_AVAILABLE = True
    Base = declarative_base()
except ImportError:
    SQLALCHEMY_AVAILABLE = False
    Base = None

# Enums for data models
class ContentType(Enum):
    """Content type enumeration"""
    AUDIO = "audio"
    VIDEO = "video"
    IMAGE = "image"
    TEXT = "text"
    MIXED = "mixed"

class UserRole(Enum):
    """User role enumeration"""
    ADMIN = "admin"
    CREATOR = "creator"
    USER = "user"
    MODERATOR = "moderator"

class ContentStatus(Enum):
    """Content status enumeration"""
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    PROCESSING = "processing"

# Base model class for non-SQLAlchemy environments
class BaseModel:
    """Base model class for all data models"""
    
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)
        self.created_at = datetime.datetime.utcnow()
        self.updated_at = datetime.datetime.utcnow()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert model to dictionary"""
        result = {}
        for key, value in self.__dict__.items():
            if not key.startswith('_'):
                if isinstance(value, datetime.datetime):
                    result[key] = value.isoformat()
                elif isinstance(value, Enum):
                    result[key] = value.value
                else:
                    result[key] = value
        return result
    
    def update(self, **kwargs):
        """Update model attributes"""
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
        self.updated_at = datetime.datetime.utcnow()

# SQLAlchemy models (if available)
if SQLALCHEMY_AVAILABLE:
    
    class User(Base):
        """User model for SQLAlchemy"""
        __tablename__ = "users"
        
        id = Column(Integer, primary_key=True, index=True)
        username = Column(String(100), unique=True, index=True, nullable=False)
        email = Column(String(255), unique=True, index=True, nullable=False)
        full_name = Column(String(255))
        role = Column(String(50), default="user")
        is_active = Column(Boolean, default=True)
        created_at = Column(DateTime, default=datetime.datetime.utcnow)
        updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
        
        # Relationships
        contents = relationship("Content", back_populates="owner")
        
        def to_dict(self) -> Dict[str, Any]:
            """Convert model to dictionary"""
            return {
                'id': self.id,
                'username': self.username,
                'email': self.email,
                'full_name': self.full_name,
                'role': self.role,
                'is_active': self.is_active,
                'created_at': self.created_at.isoformat() if self.created_at else None,
                'updated_at': self.updated_at.isoformat() if self.updated_at else None
            }
    
    class Content(Base):
        """Content model for SQLAlchemy"""
        __tablename__ = "contents"
        
        id = Column(Integer, primary_key=True, index=True)
        title = Column(String(255), nullable=False)
        description = Column(Text)
        content_type = Column(String(50), nullable=False)
        status = Column(String(50), default="pending")
        file_path = Column(String(500))
        file_size = Column(Integer)
        duration = Column(Float)  # For audio/video content
        owner_id = Column(Integer, ForeignKey("users.id"))
        created_at = Column(DateTime, default=datetime.datetime.utcnow)
        updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
        
        # Relationships
        owner = relationship("User", back_populates="contents")
        fingerprints = relationship("Fingerprint", back_populates="content")
        
        def to_dict(self) -> Dict[str, Any]:
            """Convert model to dictionary"""
            return {
                'id': self.id,
                'title': self.title,
                'description': self.description,
                'content_type': self.content_type,
                'status': self.status,
                'file_path': self.file_path,
                'file_size': self.file_size,
                'duration': self.duration,
                'owner_id': self.owner_id,
                'created_at': self.created_at.isoformat() if self.created_at else None,
                'updated_at': self.updated_at.isoformat() if self.updated_at else None
            }
    
    class Fingerprint(Base):
        """Fingerprint model for SQLAlchemy"""
        __tablename__ = "fingerprints"
        
        id = Column(Integer, primary_key=True, index=True)
        content_id = Column(Integer, ForeignKey("contents.id"))
        algorithm = Column(String(100), nullable=False)
        fingerprint_data = Column(JSON)
        confidence_score = Column(Float)
        created_at = Column(DateTime, default=datetime.datetime.utcnow)
        
        # Relationships
        content = relationship("Content", back_populates="fingerprints")
        
        def to_dict(self) -> Dict[str, Any]:
            """Convert model to dictionary"""
            return {
                'id': self.id,
                'content_id': self.content_id,
                'algorithm': self.algorithm,
                'fingerprint_data': self.fingerprint_data,
                'confidence_score': self.confidence_score,
                'created_at': self.created_at.isoformat() if self.created_at else None
            }

else:
    # Fallback models for environments without SQLAlchemy
    
    class User(BaseModel):
        """User model fallback"""
        
        def __init__(self, username: str, email: str, full_name: str = None, 
                     role: str = "user", **kwargs):
            super().__init__(**kwargs)
            self.id = kwargs.get('id')
            self.username = username
            self.email = email
            self.full_name = full_name
            self.role = role
            self.is_active = kwargs.get('is_active', True)
    
    class Content(BaseModel):
        """Content model fallback"""
        
        def __init__(self, title: str, content_type: str, owner_id: int,
                     description: str = None, **kwargs):
            super().__init__(**kwargs)
            self.id = kwargs.get('id')
            self.title = title
            self.description = description
            self.content_type = content_type
            self.status = kwargs.get('status', 'pending')
            self.file_path = kwargs.get('file_path')
            self.file_size = kwargs.get('file_size')
            self.duration = kwargs.get('duration')
            self.owner_id = owner_id
    
    class Fingerprint(BaseModel):
        """Fingerprint model fallback"""
        
        def __init__(self, content_id: int, algorithm: str, 
                     fingerprint_data: Dict[str, Any], **kwargs):
            super().__init__(**kwargs)
            self.id = kwargs.get('id')
            self.content_id = content_id
            self.algorithm = algorithm
            self.fingerprint_data = fingerprint_data
            self.confidence_score = kwargs.get('confidence_score', 0.0)

# Model registry
MODELS = {
    'User': User,
    'Content': Content,
    'Fingerprint': Fingerprint
}

def get_model(model_name: str):
    """Get model class by name"""
    return MODELS.get(model_name)

def get_all_models() -> Dict[str, Any]:
    """Get all available models"""
    return MODELS.copy()

def create_tables(engine=None):
    """Create all tables in the database"""
    if SQLALCHEMY_AVAILABLE and Base and engine:
        Base.metadata.create_all(bind=engine)
        return True
    return False

def get_models_info() -> Dict[str, Any]:
    """Get information about available models"""
    return {
        "sqlalchemy_available": SQLALCHEMY_AVAILABLE,
        "models_count": len(MODELS),
        "models": list(MODELS.keys()),
        "base_class": Base.__name__ if Base else "BaseModel"
    }