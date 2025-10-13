"""
Base Models - Protection System
==============================

Base data models and common structures for the protection system.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

from datetime import datetime
from typing import Optional, Dict, Any
from dataclasses import dataclass, field
from abc import ABC, abstractmethod
import uuid

@dataclass
class BaseModel(ABC):
    """Base model with common fields"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None
    
    def update_timestamp(self):
        """Update the updated_at timestamp"""
        self.updated_at = datetime.utcnow()

@dataclass
class TimestampedModel(BaseModel):
    """Model with detailed timestamp tracking"""
    version: int = 1
    last_accessed: Optional[datetime] = None
    expires_at: Optional[datetime] = None
    
    def access(self):
        """Mark as accessed"""
        self.last_accessed = datetime.utcnow()
    
    def is_expired(self) -> bool:
        """Check if model has expired"""
        if self.expires_at is None:
            return False
        return datetime.utcnow() > self.expires_at

@dataclass
class AuditableModel(TimestampedModel):
    """Model with audit trail capability"""
    created_by: str = ""
    updated_by: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    audit_trail: list = field(default_factory=list)
    
    def add_audit_entry(self, action: str, user: str, details: Dict[str, Any] = None):
        """Add an audit trail entry"""
        entry = {
            "timestamp": datetime.utcnow(),
            "action": action,
            "user": user,
            "details": details or {}
        }
        self.audit_trail.append(entry)
        self.updated_by = user
        self.update_timestamp()

# Export all models
__all__ = [
    "BaseModel",
    "TimestampedModel", 
    "AuditableModel"
]
