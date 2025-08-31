"""IA Influencer Agent Platform - User Models
Comprehensive user management system with enterprise security features

Author: Fahed Mlaiel <mlaiel@live.de>
Project Team: Lead Dev IA + Backend Senior + ML Engineer + DBA + Security Expert + 
              Microservices Architect + Audio Engineer + DevOps + IA Prompt Engineer

WARNING: This code and concept are protected by copyright law and intellectual property rights.
Any unauthorized use, reproduction, copying, distribution, or commercial exploitation 
without explicit written permission from Fahed Mlaiel is strictly prohibited and 
will result in legal action.

Contact: mlaiel@live.de
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""
from datetime import datetime, timezone
from typing import Optional, Dict, Any, List
from sqlalchemy import (
    String, Text, Boolean, DateTime, Integer, Numeric,
    ForeignKey, UniqueConstraint, Index, CheckConstraint
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID, JSONB, INET

from .base import (
    BaseModel, UUIDMixin, TimestampMixin, SoftDeleteMixin,
    AuditMixin, MetadataMixin, GeoLocationMixin
)


class User(BaseModel, UUIDMixin, TimestampMixin, SoftDeleteMixin, AuditMixin):
    """Core user model with enterprise authentication"""    
    __tablename__ = 'users'
    
    # Basic Information
    email: Mapped[str] = mapped_column(
        String(320),
        unique=True,
        nullable=False,
        index=True
    )
    
    username: Mapped[str] = mapped_column(
        String(50),
        unique=True,
        nullable=False,
        index=True
    )
    
    password_hash: Mapped[str] = mapped_column(
        String(255),
        nullable=False
    )
    
    first_name: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True
    )
    
    last_name: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True
    )
    
    display_name: Mapped[Optional[str]] = mapped_column(
        String(150),
        nullable=True
    )
    
    # Account Status
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
        index=True
    )
    
    is_verified: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
        index=True
    )
    
    is_premium: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
        index=True
    )
    
    # Security
    password_changed_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True
    )
    
    last_login_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        index=True
    )
    
    failed_login_attempts: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False
    )
    
    locked_until: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True
    )
    
    # Multi-factor Authentication
    mfa_enabled: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False
    )
    
    mfa_secret: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True
    )
    
    # Relationships
    profile: Mapped["UserProfile"] = relationship(
        "UserProfile", 
        back_populates="user",
        cascade="all, delete-orphan",
        uselist=False
    )
    
    settings: Mapped["UserSettings"] = relationship(
        "UserSettings",
        back_populates="user",
        cascade="all, delete-orphan",
        uselist=False
    )
    
    sessions: Mapped[List["UserSession"]] = relationship(
        "UserSession",
        back_populates="user",
        cascade="all, delete-orphan"
    )
    
    verifications: Mapped[List["UserVerification"]] = relationship(
        "UserVerification",
        back_populates="user",
        cascade="all, delete-orphan"
    )
    
    # Indexes
    __table_args__ = (
        Index('idx_users_email_active', 'email', 'is_active'),
        Index('idx_users_username_active', 'username', 'is_active'),
        Index('idx_users_created_at', 'created_at'),
        CheckConstraint('email ~* \'^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}$\'', name='valid_email'),
        CheckConstraint('username ~* \'^[A-Za-z0-9_]{3,50}$\'', name='valid_username'),
    )


class UserProfile(BaseModel, UUIDMixin, TimestampMixin, MetadataMixin, GeoLocationMixin):
    """Extended user profile information"""    
    __tablename__ = 'user_profiles'
    
    user_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey('users.id', ondelete='CASCADE'),
        nullable=False,
        unique=True,
        index=True
    )
    
    # Personal Information
    bio: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True
    )
    
    avatar_url: Mapped[Optional[str]] = mapped_column(
        String(500),
        nullable=True
    )
    
    cover_image_url: Mapped[Optional[str]] = mapped_column(
        String(500),
        nullable=True
    )
    
    website_url: Mapped[Optional[str]] = mapped_column(
        String(500),
        nullable=True
    )
    
    phone_number: Mapped[Optional[str]] = mapped_column(
        String(20),
        nullable=True
    )
    
    birth_date: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True
    )
    
    gender: Mapped[Optional[str]] = mapped_column(
        String(20),
        nullable=True
    )
    
    # Professional Information
    profession: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True
    )
    
    company: Mapped[Optional[str]] = mapped_column(
        String(150),
        nullable=True
    )
    
    industry: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True
    )
    
    experience_years: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True
    )
    
    # Social Media Links
    social_links: Mapped[Optional[Dict[str, str]]] = mapped_column(
        JSONB,
        default=dict,
        nullable=True
    )
    
    # Statistics
    followers_count: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False
    )
    
    following_count: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False
    )
    
    content_count: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False
    )
    
    # Relationships
    user: Mapped["User"] = relationship(
        "User",
        back_populates="profile"
    )


class UserSettings(BaseModel, UUIDMixin, TimestampMixin):
    """User preferences and configuration settings"""    
    __tablename__ = 'user_settings'
    
    user_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey('users.id', ondelete='CASCADE'),
        nullable=False,
        unique=True,
        index=True
    )
    
    # Notification Preferences
    email_notifications: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False
    )
    
    push_notifications: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False
    )
    
    sms_notifications: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False
    )
    
    # Privacy Settings
    profile_visibility: Mapped[str] = mapped_column(
        String(20),
        default='public',
        nullable=False
    )
    
    show_email: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False
    )
    
    show_phone: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False
    )
    
    allow_messaging: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False
    )
    
    # Content Settings
    default_content_visibility: Mapped[str] = mapped_column(
        String(20),
        default='public',
        nullable=False
    )
    
    auto_publish: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False
    )
    
    watermark_enabled: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False
    )
    
    # AI Settings
    ai_recommendations: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False
    )
    
    ai_content_analysis: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False
    )
    
    ai_protection_level: Mapped[str] = mapped_column(
        String(20),
        default='standard',
        nullable=False
    )
    
    # Language and Localization
    language: Mapped[str] = mapped_column(
        String(10),
        default='en',
        nullable=False
    )
    
    timezone: Mapped[str] = mapped_column(
        String(50),
        default='UTC',
        nullable=False
    )
    
    currency: Mapped[str] = mapped_column(
        String(3),
        default='USD',
        nullable=False
    )
    
    # Advanced Settings
    custom_settings: Mapped[Optional[Dict[str, Any]]] = mapped_column(
        JSONB,
        default=dict,
        nullable=True
    )
    
    # Relationships
    user: Mapped["User"] = relationship(
        "User",
        back_populates="settings"
    )


class UserSession(BaseModel, UUIDMixin, TimestampMixin):
    """User session management for security tracking"""    
    __tablename__ = 'user_sessions'
    
    user_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey('users.id', ondelete='CASCADE'),
        nullable=False,
        index=True
    )
    
    # Session Information
    session_token: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        nullable=False,
        index=True
    )
    
    refresh_token: Mapped[Optional[str]] = mapped_column(
        String(255),
        unique=True,
        nullable=True
    )
    
    expires_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        index=True
    )
    
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
        index=True
    )
    
    # Device and Location Information
    user_agent: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True
    )
    
    ip_address: Mapped[Optional[str]] = mapped_column(
        INET,
        nullable=True,
        index=True
    )
    
    device_type: Mapped[Optional[str]] = mapped_column(
        String(50),
        nullable=True
    )
    
    device_name: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True
    )
    
    browser_name: Mapped[Optional[str]] = mapped_column(
        String(50),
        nullable=True
    )
    
    os_name: Mapped[Optional[str]] = mapped_column(
        String(50),
        nullable=True
    )
    
    # Geographic Information
    country: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True
    )
    
    city: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True
    )
    
    # Activity Tracking
    last_activity_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        index=True
    )
    
    login_method: Mapped[str] = mapped_column(
        String(50),
        default='email',
        nullable=False
    )
    
    # Relationships
    user: Mapped["User"] = relationship(
        "User",
        back_populates="sessions"
    )
    
    # Indexes
    __table_args__ = (
        Index('idx_sessions_user_active', 'user_id', 'is_active'),
        Index('idx_sessions_expires_at', 'expires_at'),
        Index('idx_sessions_ip_address', 'ip_address'),
    )


class UserVerification(BaseModel, UUIDMixin, TimestampMixin):
    """User verification tokens and processes"""    
    __tablename__ = 'user_verifications'
    
    user_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey('users.id', ondelete='CASCADE'),
        nullable=False,
        index=True
    )
    
    # Verification Information
    verification_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        index=True
    )  # email, phone, identity, professional
    
    verification_token: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        nullable=False,
        index=True
    )
    
    verification_code: Mapped[Optional[str]] = mapped_column(
        String(20),
        nullable=True
    )
    
    # Status and Timing
    is_verified: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
        index=True
    )
    
    expires_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        index=True
    )
    
    verified_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True
    )
    
    attempts_count: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False
    )
    
    max_attempts: Mapped[int] = mapped_column(
        Integer,
        default=3,
        nullable=False
    )
    
    # Additional Data
    verification_data: Mapped[Optional[Dict[str, Any]]] = mapped_column(
        JSONB,
        nullable=True
    )
    
    # Relationships
    user: Mapped["User"] = relationship(
        "User",
        back_populates="verifications"
    )
    
    # Indexes
    __table_args__ = (
        Index('idx_verifications_type_status', 'verification_type', 'is_verified'),
        Index('idx_verifications_expires_at', 'expires_at'),
        UniqueConstraint('user_id', 'verification_type', name='unique_user_verification_type'),
    )
