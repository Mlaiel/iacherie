"""Base Event Classes

Foundational event classes for the IA Influencer Agent event system.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import logging
from typing import Dict, Any, Optional
from datetime import datetime
from uuid import uuid4

logger = logging.getLogger(__name__)


class BaseEvent:
    """Base class for all events in the system"""
    
    def __init__(self, 
                 event_type -> None: str, 
                 data -> None: Dict[str, Any] = None, 
                 event_id -> None: str = None, 
                 timestamp -> None: datetime = None,
                 metadata -> None: Dict[str, Any] = None,
                 priority=None,  # Import after to avoid circular imports
                 status=None,
                 source -> None: Optional[str] = None,
                 correlation_id -> None: Optional[str] = None,
                 causation_id -> None: Optional[str] = None,
                 aggregate_id -> None: Optional[str] = None,
                 aggregate_version -> None: Optional[int] = None,
                 error_message -> None: Optional[str] = None) -> None:
        self.event_id = event_id or str(uuid4())
        self.event_type = event_type
        self.data = data or {}
        self.timestamp = timestamp or datetime.utcnow()
        self.metadata = metadata or {}
        self.version = "1.0"
        
        # Advanced event properties
        self.source = source
        self.correlation_id = correlation_id
        self.causation_id = causation_id
        self.aggregate_id = aggregate_id
        self.aggregate_version = aggregate_version
        self.error_message = error_message
        
        # Set priority and status after import to avoid circular imports
        if priority is not None:
            self.priority = priority
        if status is not None:
            self.status = status
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert event to dictionary"""
        result = {
            'event_id': self.event_id,
            'event_type': self.event_type,
            'data': self.data,
            'timestamp': self.timestamp.isoformat(),
            'version': self.version,
            'metadata': self.metadata
        }
        
        # Add optional fields if present
        if hasattr(self, 'priority') and self.priority:
            result['priority'] = self.priority.value if hasattr(self.priority, 'value') else str(self.priority)
        if hasattr(self, 'status') and self.status:
            result['status'] = self.status.value if hasattr(self.status, 'value') else str(self.status)
        if self.source:
            result['source'] = self.source
        if self.correlation_id:
            result['correlation_id'] = self.correlation_id
        if self.causation_id:
            result['causation_id'] = self.causation_id
        if self.aggregate_id:
            result['aggregate_id'] = self.aggregate_id
        if self.aggregate_version:
            result['aggregate_version'] = self.aggregate_version
        if self.error_message:
            result['error_message'] = self.error_message
            
        return result
    
    @classmethod
    def from_dict(cls, data -> None: Dict[str, Any]) -> None:
        """Create event from dictionary"""
        kwargs = {
            'event_type': data['event_type'],
            'data': data.get('data', {}),
            'event_id': data.get('event_id'),
            'metadata': data.get('metadata', {}),
            'source': data.get('source'),
            'correlation_id': data.get('correlation_id'),
            'causation_id': data.get('causation_id'),
            'aggregate_id': data.get('aggregate_id'),
            'aggregate_version': data.get('aggregate_version'),
            'error_message': data.get('error_message')
        }
        
        if 'timestamp' in data:
            kwargs['timestamp'] = datetime.fromisoformat(data['timestamp'])
            
        # Handle priority and status after class creation
        event = cls(**kwargs)
        
        if 'priority' in data:
            try:
                from .event_priority import EventPriority
                event.priority = EventPriority(data['priority'])
            except (ImportError, ValueError):
                pass
                
        if 'status' in data:
            try:
                from .event_status import EventStatus
                event.status = EventStatus(data['status'])
            except (ImportError, ValueError):
                pass
        
        return event
    
    def __str__(self) -> None:
        return f"{self.__class__.__name__}(id={self.event_id}, type={self.event_type})"
    
    def __repr__(self) -> None:
        return self.__str__()
    
    def __repr__(self) -> None:
        return self.__str__()


# Export for compatibility
__all__ = ['BaseEvent']