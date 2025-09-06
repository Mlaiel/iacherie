"""Audio Collaboration Events - Industrial Grade Collaboration Event Management
==============================================================================

This module handles all events related to real-time collaboration, version control,
and collaborative audio creation workflows.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional, Any
from uuid import UUID
from enum import Enum

from ..core.base_event import BaseEvent


class CollaborationType(Enum):
    REAL_TIME = "real_time"
    ASYNCHRONOUS = "asynchronous"
    REMIX = "remix"
    SAMPLE = "sample"


class CollaborationStatus(Enum):
    PENDING = "pending"
    ACCEPTED = "accepted"
    REJECTED = "rejected"
    ACTIVE = "active"
    COMPLETED = "completed"


class RemixType(Enum):
    FULL_REMIX = "full_remix"
    PARTIAL_REMIX = "partial_remix"
    MASHUP = "mashup"
    COVER = "cover"


@dataclass
class AudioCollaborationRequestEvent(BaseEvent):
    user_id: UUID
    file_id: UUID
    collaboration_id: UUID
    requester_id: UUID
    collaboration_type: str
    
    def __post_init__(self):
        super().__init__(
            event_type="audio.collaboration.request",
            data={
                "file_id": str(self.file_id),
                "collaboration_id": str(self.collaboration_id),
                "collaboration_type": self.collaboration_type
            }
        )


@dataclass
class AudioCollaborationAcceptedEvent(BaseEvent):
    user_id: UUID
    file_id: UUID
    collaboration_id: UUID
    accepter_id: UUID
    
    def __post_init__(self):
        super().__init__(
            event_type="audio.collaboration.accepted",
            data={
                "file_id": str(self.file_id),
                "collaboration_id": str(self.collaboration_id)
            }
        )


@dataclass
class AudioCollaborationRejectedEvent(BaseEvent):
    user_id: UUID
    file_id: UUID
    collaboration_id: UUID
    rejecter_id: UUID
    rejection_reason: str
    
    def __post_init__(self):
        super().__init__(
            event_type="audio.collaboration.rejected",
            data={
                "file_id": str(self.file_id),
                "collaboration_id": str(self.collaboration_id),
                "rejection_reason": self.rejection_reason
            }
        )


@dataclass
class AudioRemixCreatedEvent(BaseEvent):
    user_id: UUID
    original_file_id: UUID
    remix_file_id: UUID
    remix_type: str
    
    def __post_init__(self):
        super().__init__(
            event_type="audio.collaboration.remix_created",
            data={
                "original_file_id": str(self.original_file_id),
                "remix_file_id": str(self.remix_file_id),
                "remix_type": self.remix_type
            }
        )


@dataclass
class AudioVersionCreatedEvent(BaseEvent):
    user_id: UUID
    file_id: UUID
    version_id: UUID
    version_number: str
    
    def __post_init__(self):
        super().__init__(
            event_type="audio.collaboration.version_created",
            data={
                "file_id": str(self.file_id),
                "version_id": str(self.version_id),
                "version_number": self.version_number
            }
        )


@dataclass
class AudioRealTimeCollaborationEvent(BaseEvent):
    user_id: UUID
    session_id: UUID
    file_id: UUID
    action_type: str
    participants: List[UUID] = field(default_factory=list)
    
    def __post_init__(self):
        super().__init__(
            event_type="audio.collaboration.real_time",
            data={
                "session_id": str(self.session_id),
                "file_id": str(self.file_id),
                "action_type": self.action_type,
                "participants_count": len(self.participants)
            }
        )


@dataclass
class AudioVersionControlEvent(BaseEvent):
    user_id: UUID
    file_id: UUID
    version_control_id: UUID
    operation: str  # commit, merge, branch, tag
    
    def __post_init__(self):
        super().__init__(
            event_type="audio.collaboration.version_control",
            data={
                "file_id": str(self.file_id),
                "version_control_id": str(self.version_control_id),
                "operation": self.operation
            }
        )


@dataclass
class AudioCollaborationRoomEvent(BaseEvent):
    user_id: UUID
    room_id: UUID
    action: str  # created, joined, left, closed
    participants: List[UUID] = field(default_factory=list)
    
    def __post_init__(self):
        super().__init__(
            event_type="audio.collaboration.room",
            data={
                "room_id": str(self.room_id),
                "action": self.action,
                "participants_count": len(self.participants)
            }
        )


@dataclass
class AudioLiveSessionEvent(BaseEvent):
    user_id: UUID
    session_id: UUID
    session_type: str
    status: str  # started, active, paused, ended
    
    def __post_init__(self):
        super().__init__(
            event_type="audio.collaboration.live_session",
            data={
                "session_id": str(self.session_id),
                "session_type": self.session_type,
                "status": self.status
            }
        )