"""
Guardian Missions Endpoints
Gestion des missions humanitaires, environnementales, animaux, sans-abri
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from moderation import get_moderator
from rate_limiting import get_rate_limiter
from audit import get_audit_logger, AuditAction, AuditLevel

router = APIRouter()

# Mission model
class Mission(BaseModel):
    id: Optional[int] = None
    title: str
    description: str
    category: str  # e.g. "environment", "animal", "homeless", "humanitarian"
    location: str
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    volunteers_needed: int
    volunteers_registered: int = 0
    status: str = "open"  # open, ongoing, completed, cancelled

# In-memory store (replace with DB integration)
missions_db: List[Mission] = []

@router.get("/missions", response_model=List[Mission])
def list_missions():
    """Liste toutes les missions"""
    return missions_db

@router.post("/missions", response_model=Mission)
def create_mission(mission: Mission):
    """Créer une nouvelle mission"""
    
    # Rate limit
    rate_limiter = get_rate_limiter()
    user_id = "system"  # In production, get from auth context
    if not rate_limiter.check_rate_limit(f"mission_create:{user_id}", 10, 3600):
        raise HTTPException(status_code=429, detail="Too many missions created. Max 10 per hour.")
    
    # Moderate title and description
    moderator = get_moderator()
    title_mod = moderator.moderate_text(mission.title, strict=True)
    desc_mod = moderator.moderate_text(mission.description, strict=False)
    
    if title_mod.suggested_action == "block" or desc_mod.suggested_action == "block":
        audit_logger = get_audit_logger()
        audit_logger.log(
            AuditAction.CONTENT_BLOCKED,
            level=AuditLevel.WARNING,
            user_id=user_id,
            resource_type="mission",
            details={
                "title": mission.title,
                "reasons": title_mod.reasons + desc_mod.reasons
            },
            success=False
        )
        raise HTTPException(
            status_code=400,
            detail=f"Mission content blocked: {', '.join(title_mod.reasons + desc_mod.reasons)}"
        )
    
    # Filter profanity if needed
    if title_mod.suggested_action == "warn":
        mission.title = moderator.filter_text(mission.title)
    if desc_mod.suggested_action == "warn":
        mission.description = moderator.filter_text(mission.description)
    
    mission.id = len(missions_db) + 1
    missions_db.append(mission)
    
    # Audit log
    audit_logger = get_audit_logger()
    audit_logger.log(
        AuditAction.MISSION_CREATED,
        user_id=user_id,
        resource_type="mission",
        resource_id=str(mission.id),
        details={
            "title": mission.title,
            "category": mission.category,
            "location": mission.location
        }
    )
    
    return mission

@router.get("/missions/{mission_id}", response_model=Mission)
def get_mission(mission_id: int):
    """Obtenir les détails d'une mission"""
    for m in missions_db:
        if m.id == mission_id:
            return m
    raise HTTPException(status_code=404, detail="Mission not found")

@router.put("/missions/{mission_id}", response_model=Mission)
def update_mission(mission_id: int, mission: Mission):
    """Mettre à jour une mission"""
    for idx, m in enumerate(missions_db):
        if m.id == mission_id:
            missions_db[idx] = mission
            return mission
    raise HTTPException(status_code=404, detail="Mission not found")

@router.delete("/missions/{mission_id}")
def delete_mission(mission_id: int):
    """Supprimer une mission"""
    for idx, m in enumerate(missions_db):
        if m.id == mission_id:
            del missions_db[idx]
            return {"detail": "Mission deleted"}
    raise HTTPException(status_code=404, detail="Mission not found")
