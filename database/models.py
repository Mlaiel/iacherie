"""
Database Models
SQLAlchemy models for the database schema.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

from sqlalchemy import Column, String, Integer, Float, Boolean, Text, DateTime, ForeignKey, JSON, BigInteger
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()


class User(Base):
    """User model"""
    __tablename__ = "users"
    
    id = Column(String(32), primary_key=True)
    email = Column(String(255), unique=True, nullable=False)
    username = Column(String(50), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    first_name = Column(String(50), nullable=False)
    last_name = Column(String(50), nullable=False)
    creator_type = Column(String(20), nullable=False)
    tenant_id = Column(String(16), nullable=False)
    is_verified = Column(Boolean, default=False)
    subscription_tier = Column(String(20), default="free")
    active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    content = relationship("Content", back_populates="user")
    monitoring = relationship("ContentMonitoring", back_populates="user")
    violations = relationship("ProtectionViolation", back_populates="user")


class Content(Base):
    """Content model"""
    __tablename__ = "content"
    
    id = Column(String(36), primary_key=True)
    user_id = Column(String(32), ForeignKey("users.id"), nullable=False)
    title = Column(String(255), nullable=False)
    description = Column(Text)
    content_type = Column(String(20), nullable=False)
    filename = Column(String(255), nullable=False)
    file_size = Column(BigInteger, nullable=False)
    fingerprint_id = Column(String(36))
    status = Column(String(20), default="processing")
    active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="content")
    monitoring = relationship("ContentMonitoring", back_populates="content")
    violations = relationship("ProtectionViolation", back_populates="content")


class ContentMonitoring(Base):
    """Content monitoring model"""
    __tablename__ = "content_monitoring"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String(32), ForeignKey("users.id"), nullable=False)
    content_id = Column(String(36), ForeignKey("content.id"), nullable=False)
    content_type = Column(String(20), nullable=False)
    fingerprint_data = Column(JSON, nullable=False)
    platforms = Column(JSON, nullable=False)
    monitoring_frequency = Column(Integer, default=24)
    alert_threshold = Column(Float, default=0.85)
    active = Column(Boolean, default=True)
    last_checked = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="monitoring")
    content = relationship("Content", back_populates="monitoring")


class ProtectionViolation(Base):
    """Protection violation model"""
    __tablename__ = "protection_violations"
    
    id = Column(String(36), primary_key=True)
    original_content_id = Column(String(36), ForeignKey("content.id"), nullable=False)
    user_id = Column(String(32), ForeignKey("users.id"), nullable=False)
    platform = Column(String(50), nullable=False)
    violation_url = Column(Text, nullable=False)
    similarity_score = Column(Float, nullable=False)
    status = Column(String(20), default="pending_review")
    evidence_data = Column(JSON)
    detected_at = Column(DateTime, default=datetime.utcnow)
    resolved_at = Column(DateTime)
    
    # Relationships
    user = relationship("User", back_populates="violations")
    content = relationship("Content", back_populates="violations")