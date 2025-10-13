"""
Audit log model for tracking user actions and system events
"""

from sqlalchemy import Column, String, DateTime, Text, ForeignKey, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from .base import Base, TimestampMixin, UUIDMixin


class AuditLog(Base, UUIDMixin, TimestampMixin):
    """Audit log for tracking all user actions and system events"""
    
    __tablename__ = 'audit_logs'
    
    # Actor (who performed the action)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id', ondelete='SET NULL'), nullable=True, index=True)
    actor_type = Column(String(50), default='user', nullable=False)  # user, system, api, cron
    
    # Action details
    action = Column(String(100), nullable=False, index=True)  # create, update, delete, login, etc.
    resource_type = Column(String(100), nullable=False, index=True)  # user, case, appointment, etc.
    resource_id = Column(UUID(as_uuid=True), nullable=True, index=True)
    
    # Module/Channel
    module = Column(String(50), nullable=False, index=True)  # ia2good, guardian, eduverify, medcare, system
    
    # Context
    description = Column(Text, nullable=True)
    changes = Column(JSON, nullable=True)  # Before/after values
    metadata = Column(JSON, default={}, nullable=False)  # Additional context
    
    # Request info
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(String(500), nullable=True)
    request_method = Column(String(10), nullable=True)  # GET, POST, PUT, DELETE
    request_path = Column(String(500), nullable=True)
    
    # Result
    status = Column(String(20), default='success', nullable=False, index=True)  # success, failure, error
    error_message = Column(Text, nullable=True)
    
    # Relationships
    user = relationship('User')
    
    def __repr__(self):
        return f"<AuditLog {self.action} on {self.resource_type} by user={self.user_id}>"
    
    @classmethod
    def log_action(
        cls,
        session,
        user_id,
        action: str,
        resource_type: str,
        resource_id=None,
        module: str = 'system',
        description: str = None,
        changes: dict = None,
        metadata: dict = None,
        ip_address: str = None,
        user_agent: str = None,
        status: str = 'success'
    ):
        """Helper method to create audit log entry"""
        log_entry = cls(
            user_id=user_id,
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            module=module,
            description=description,
            changes=changes,
            metadata=metadata or {},
            ip_address=ip_address,
            user_agent=user_agent,
            status=status
        )
        session.add(log_entry)
        return log_entry
