"""
User models for authentication and authorization
"""

from sqlalchemy import Column, String, Boolean, DateTime, Integer, ForeignKey, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from .base import Base, TimestampMixin, UUIDMixin, SoftDeleteMixin
import uuid


class User(Base, UUIDMixin, TimestampMixin, SoftDeleteMixin):
    """User model shared across all modules"""
    
    __tablename__ = 'users'
    
    # Basic Info
    email = Column(String(255), unique=True, nullable=False, index=True)
    phone = Column(String(20), unique=True, nullable=True, index=True)
    password_hash = Column(String(255), nullable=False)
    
    # Profile
    full_name = Column(String(255), nullable=False)
    avatar_url = Column(String(500), nullable=True)
    bio = Column(String(1000), nullable=True)
    
    # Preferences
    language = Column(String(10), default='fr', nullable=False)
    timezone = Column(String(50), default='UTC', nullable=False)
    
    # Status
    status = Column(String(20), default='active', nullable=False)  # active, suspended, deleted
    email_verified = Column(Boolean, default=False, nullable=False)
    phone_verified = Column(Boolean, default=False, nullable=False)
    
    # Terms & Privacy
    terms_accepted = Column(Boolean, default=False, nullable=False)
    terms_accepted_at = Column(DateTime(timezone=True), nullable=True)
    privacy_policy_accepted = Column(Boolean, default=False, nullable=False)
    
    # 2FA/MFA
    mfa_enabled = Column(Boolean, default=False, nullable=False)
    mfa_secret = Column(String(32), nullable=True)
    backup_codes = Column(JSON, nullable=True)  # List of hashed backup codes
    
    # Login tracking
    last_login_at = Column(DateTime(timezone=True), nullable=True)
    last_login_ip = Column(String(45), nullable=True)  # IPv6 compatible
    login_count = Column(Integer, default=0, nullable=False)
    failed_login_attempts = Column(Integer, default=0, nullable=False)
    locked_until = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    roles = relationship('UserRole', back_populates='user', cascade='all, delete-orphan')
    sessions = relationship('UserSession', back_populates='user', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f"<User {self.email}>"
    
    def is_active(self):
        """Check if user is active"""
        return self.status == 'active' and not self.is_deleted
    
    def is_locked(self):
        """Check if user account is locked"""
        from datetime import datetime
        return self.locked_until and self.locked_until > datetime.utcnow()


class UserRole(Base, UUIDMixin, TimestampMixin):
    """User roles for RBAC across modules"""
    
    __tablename__ = 'user_roles'
    
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    module = Column(String(50), nullable=False, index=True)  # ia2good, guardian, eduverify, medcare, system
    role = Column(String(50), nullable=False, index=True)    # role name
    permissions = Column(JSON, default={}, nullable=False)   # Additional permissions
    
    # Grant tracking
    granted_by = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=True)
    granted_at = Column(DateTime(timezone=True), nullable=False)
    expires_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    user = relationship('User', foreign_keys=[user_id], back_populates='roles')
    granted_by_user = relationship('User', foreign_keys=[granted_by])
    
    def __repr__(self):
        return f"<UserRole user={self.user_id} module={self.module} role={self.role}>"
    
    def is_expired(self):
        """Check if role is expired"""
        from datetime import datetime
        return self.expires_at and self.expires_at < datetime.utcnow()


class UserSession(Base, UUIDMixin, TimestampMixin):
    """User sessions for tracking active logins"""
    
    __tablename__ = 'user_sessions'
    
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    refresh_token_hash = Column(String(255), nullable=False, unique=True, index=True)
    
    # Session info
    device_info = Column(String(255), nullable=True)
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(String(500), nullable=True)
    
    # Status
    is_active = Column(Boolean, default=True, nullable=False)
    expires_at = Column(DateTime(timezone=True), nullable=False)
    last_activity_at = Column(DateTime(timezone=True), nullable=False)
    revoked_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    user = relationship('User', back_populates='sessions')
    
    def __repr__(self):
        return f"<UserSession user={self.user_id} active={self.is_active}>"
    
    def is_expired(self):
        """Check if session is expired"""
        from datetime import datetime
        return self.expires_at < datetime.utcnow()
    
    def revoke(self):
        """Revoke session"""
        from datetime import datetime
        self.is_active = False
        self.revoked_at = datetime.utcnow()
