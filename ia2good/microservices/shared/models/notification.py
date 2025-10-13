"""
Notification model for multi-channel notifications
"""

from sqlalchemy import Column, String, Boolean, DateTime, Text, ForeignKey, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from .base import Base, TimestampMixin, UUIDMixin


class Notification(Base, UUIDMixin, TimestampMixin):
    """Notifications sent to users across all channels"""
    
    __tablename__ = 'notifications'
    
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    
    # Notification details
    type = Column(String(50), nullable=False, index=True)      # push, sms, email, in_app, websocket
    channel = Column(String(50), nullable=False, index=True)   # ia2good, guardian, eduverify, medcare, system
    priority = Column(String(20), default='normal', nullable=False, index=True)  # low, normal, high, urgent
    
    # Content
    title = Column(String(255), nullable=False)
    message = Column(Text, nullable=False)
    data = Column(JSON, default={}, nullable=False)  # Additional data payload
    action_url = Column(Text, nullable=True)  # Link to related resource
    
    # Status
    read = Column(Boolean, default=False, nullable=False, index=True)
    read_at = Column(DateTime(timezone=True), nullable=True)
    
    sent = Column(Boolean, default=False, nullable=False, index=True)
    sent_at = Column(DateTime(timezone=True), nullable=True)
    
    delivered = Column(Boolean, default=False, nullable=False)
    delivered_at = Column(DateTime(timezone=True), nullable=True)
    
    failed = Column(Boolean, default=False, nullable=False)
    error_message = Column(Text, nullable=True)
    
    # Retry tracking
    retry_count = Column(String(20), default='0', nullable=False)
    next_retry_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    user = relationship('User')
    
    def __repr__(self):
        return f"<Notification {self.type} to user={self.user_id} channel={self.channel}>"
    
    def mark_as_read(self):
        """Mark notification as read"""
        from datetime import datetime
        self.read = True
        self.read_at = datetime.utcnow()
    
    def mark_as_sent(self):
        """Mark notification as sent"""
        from datetime import datetime
        self.sent = True
        self.sent_at = datetime.utcnow()
    
    def mark_as_delivered(self):
        """Mark notification as delivered"""
        from datetime import datetime
        self.delivered = True
        self.delivered_at = datetime.utcnow()
    
    def mark_as_failed(self, error_message: str):
        """Mark notification as failed"""
        self.failed = True
        self.error_message = error_message
