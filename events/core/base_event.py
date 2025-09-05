"""Base Event Classes

Foundational event classes for the IA Influencer Agent event system.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import logging
from typing import Dict, Any, Optional
from datetime import datetime
from uuid import uuid4
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)


class BaseEvent(ABC):
    """Base class for all events in the system"""
    
    def __init__(self, event_type: str, data: Dict[str, Any] = None, 
                 event_id: str = None, timestamp: datetime = None):
        self.event_id = event_id or str(uuid4())
        self.event_type = event_type
        self.data = data or {}
        self.timestamp = timestamp or datetime.utcnow()
        self.version = "1.0"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert event to dictionary"""
        return {
            'event_id': self.event_id,
            'event_type': self.event_type,
            'data': self.data,
            'timestamp': self.timestamp.isoformat(),
            'version': self.version
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]):
        """Create event from dictionary"""
        return cls(
            event_type=data['event_type'],
            data=data.get('data', {}),
            event_id=data.get('event_id'),
            timestamp=datetime.fromisoformat(data['timestamp']) if 'timestamp' in data else None
        )
    
    def __str__(self):
        return f"{self.__class__.__name__}(id={self.event_id}, type={self.event_type})"
    
    def __repr__(self):
        return self.__str__()


# Export for compatibility
__all__ = ['BaseEvent']