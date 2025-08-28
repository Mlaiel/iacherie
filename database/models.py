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


class RevenueTracking(Base):
    """Revenue tracking model"""
    __tablename__ = "revenue_tracking"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String(32), ForeignKey("users.id"), nullable=False)
    content_id = Column(String(36), ForeignKey("content.id"), nullable=False)
    platform = Column(String(50), nullable=False)
    revenue_amount = Column(Float, nullable=False)
    currency = Column(String(3), default="EUR")
    revenue_type = Column(String(30), nullable=False)  # views, streams, licensing, etc.
    period_start = Column(DateTime, nullable=False)
    period_end = Column(DateTime, nullable=False)
    platform_transaction_id = Column(String(100))
    metadata = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)


class PlatformConnections(Base):
    """Platform connections model"""
    __tablename__ = "platform_connections"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String(32), ForeignKey("users.id"), nullable=False)
    platform = Column(String(50), nullable=False)
    platform_user_id = Column(String(100))
    platform_username = Column(String(100))
    access_token = Column(Text)
    refresh_token = Column(Text)
    token_expires_at = Column(DateTime)
    scopes = Column(JSON)  # Array of scopes
    is_active = Column(Boolean, default=True)
    connected_at = Column(DateTime, default=datetime.utcnow)
    last_sync = Column(DateTime)


class LicensingAgreements(Base):
    """Licensing agreements model"""
    __tablename__ = "licensing_agreements"
    
    id = Column(String(36), primary_key=True)
    content_id = Column(String(36), ForeignKey("content.id"), nullable=False)
    licensee_id = Column(String(32))
    license_type = Column(String(50), nullable=False)
    usage_rights = Column(JSON)  # Array of usage rights
    price = Column(Float)
    currency = Column(String(3))
    territory = Column(String(100))
    duration_months = Column(Integer)
    status = Column(String(20), default="pending")
    created_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime)


class PaymentTransactions(Base):
    """Payment transactions model"""
    __tablename__ = "payment_transactions"
    
    id = Column(String(36), primary_key=True)
    user_id = Column(String(32), ForeignKey("users.id"), nullable=False)
    transaction_type = Column(String(30), nullable=False)
    amount = Column(Float, nullable=False)
    currency = Column(String(3), nullable=False)
    payment_provider = Column(String(20), nullable=False)
    provider_transaction_id = Column(String(100))
    status = Column(String(20), default="pending")
    metadata = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)
    processed_at = Column(DateTime)


class CollaborationProjects(Base):
    """Collaboration projects model"""
    __tablename__ = "collaboration_projects"
    
    id = Column(String(36), primary_key=True)
    creator_id = Column(String(32), ForeignKey("users.id"), nullable=False)
    collaborator_id = Column(String(32), ForeignKey("users.id"), nullable=False)
    project_name = Column(String(255), nullable=False)
    project_type = Column(String(50), nullable=False)
    revenue_split = Column(JSON, nullable=False)
    status = Column(String(20), default="proposed")
    created_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime)


class ContentPerformance(Base):
    """Content performance model"""
    __tablename__ = "content_performance"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    content_id = Column(String(36), ForeignKey("content.id"), nullable=False)
    platform = Column(String(50), nullable=False)
    views = Column(BigInteger, default=0)
    likes = Column(BigInteger, default=0)
    shares = Column(BigInteger, default=0)
    comments = Column(BigInteger, default=0)
    revenue_generated = Column(Float, default=0.0)
    engagement_rate = Column(Float)
    collected_at = Column(DateTime, default=datetime.utcnow)


class CrawlResult(Base):
    """Crawl result model for storing crawler data"""
    __tablename__ = "crawl_results"
    
    id = Column(String(36), primary_key=True)
    platform = Column(String(50), nullable=False)
    crawler_type = Column(String(50), nullable=False)
    source_url = Column(Text, nullable=False)
    content_data = Column(JSON, nullable=False)
    metadata = Column(JSON)
    status = Column(String(20), default="success")
    error_message = Column(Text)
    crawled_at = Column(DateTime, default=datetime.utcnow)
    processed = Column(Boolean, default=False)


class ContentMatch(Base):
    """Content match model for storing detected matches"""
    __tablename__ = "content_matches"
    
    id = Column(String(36), primary_key=True)
    original_content_id = Column(String(36), ForeignKey("content.id"), nullable=False)
    matched_url = Column(Text, nullable=False)
    platform = Column(String(50), nullable=False)
    similarity_score = Column(Float, nullable=False)
    match_type = Column(String(30), nullable=False)  # exact, similar, partial
    detection_method = Column(String(50), nullable=False)
    match_data = Column(JSON)
    confidence_score = Column(Float)
    status = Column(String(20), default="pending")
    verified = Column(Boolean, default=False)
    detected_at = Column(DateTime, default=datetime.utcnow)
    verified_at = Column(DateTime)
    recorded_at = Column(DateTime, default=datetime.utcnow)