"""🤝 Collaboration Models - IA Influencer Agent Platform Enterprise
=================================================================
Module: backend/data_management/models/collaboration_model.py
Author: Fahed Mlaiel (mlaiel@live.de)
=================================================================

⚠️  PROPRIÉTÉ INTELLECTUELLE EXCLUSIVE - FAHED MLAIEL ⚠️
(c) 2025 Fahed Mlaiel. Tous droits réservés.
Usage non autorisé strictement interdit et passible de poursuites judiciaires.
Contact: mlaiel@live.de
"""

from typing import Dict, List, Optional, Any
from datetime import datetime, timezone
from enum import Enum

from dataclasses import dataclass, field
import uuid

class CollaborationStatus(Enum):
    PROPOSED = "proposed"
    ACCEPTED = "accepted"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

@dataclass
class CollaborationModel:
    collaboration_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    project_id: str = ""
    initiator_id: str = ""
    collaborator_id: str = ""
    tenant_id: str = ""
    collaboration_type: str = "music_production"
    status: CollaborationStatus = CollaborationStatus.PROPOSED
    revenue_split: Dict[str, float] = field(default_factory=dict)
    deadline: Optional[datetime] = None
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "collaboration_id": self.collaboration_id,
            "project_id": self.project_id,
            "initiator_id": self.initiator_id,
            "collaborator_id": self.collaborator_id,
            "tenant_id": self.tenant_id,
            "collaboration_type": self.collaboration_type,
            "status": self.status.value,
            "revenue_split": self.revenue_split,
            "deadline": self.deadline.isoformat() if self.deadline else None,
            "created_at": self.created_at.isoformat()
        }

@dataclass
class MatchingModel:
    match_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    creator_a_id: str = ""
    creator_b_id: str = ""
    compatibility_score: float = 0.0
    match_type: str = "skill_complement"
    mutual_interest: bool = False
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "match_id": self.match_id,
            "creator_a_id": self.creator_a_id,
            "creator_b_id": self.creator_b_id,
            "compatibility_score": self.compatibility_score,
            "match_type": self.match_type,
            "mutual_interest": self.mutual_interest,
            "created_at": self.created_at.isoformat()
        }

@dataclass
class ProjectModel:
    project_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    owner_id: str = ""
    tenant_id: str = ""
    project_name: str = ""
    project_type: str = "music_album"
    collaborators: List[str] = field(default_factory=list)
    content_ids: List[str] = field(default_factory=list)
    status: str = "active"
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "project_id": self.project_id,
            "owner_id": self.owner_id,
            "tenant_id": self.tenant_id,
            "project_name": self.project_name,
            "project_type": self.project_type,
            "collaborators": self.collaborators,
            "content_ids": self.content_ids,
            "status": self.status,
            "created_at": self.created_at.isoformat()
        }
