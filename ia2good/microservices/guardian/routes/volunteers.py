"""
Guardian Volunteers Endpoints
Gestion des volontaires
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

router = APIRouter()

# Volunteer model
class Volunteer(BaseModel):
    id: Optional[int] = None
    name: str
    email: str
    phone: Optional[str] = None
    skills: List[str] = []
    registered_at: datetime = datetime.utcnow()
    missions: List[int] = []  # IDs of missions

# In-memory store (replace with DB integration)
volunteers_db: List[Volunteer] = []

@router.get("/volunteers", response_model=List[Volunteer])
def list_volunteers():
    """Liste tous les volontaires"""
    return volunteers_db

@router.post("/volunteers", response_model=Volunteer)
def register_volunteer(volunteer: Volunteer):
    """Inscrire un nouveau volontaire"""
    volunteer.id = len(volunteers_db) + 1
    volunteers_db.append(volunteer)
    return volunteer

@router.get("/volunteers/{volunteer_id}", response_model=Volunteer)
def get_volunteer(volunteer_id: int):
    """Obtenir les détails d'un volontaire"""
    for v in volunteers_db:
        if v.id == volunteer_id:
            return v
    raise HTTPException(status_code=404, detail="Volunteer not found")

@router.put("/volunteers/{volunteer_id}", response_model=Volunteer)
def update_volunteer(volunteer_id: int, volunteer: Volunteer):
    """Mettre à jour un volontaire"""
    for idx, v in enumerate(volunteers_db):
        if v.id == volunteer_id:
            volunteers_db[idx] = volunteer
            return volunteer
    raise HTTPException(status_code=404, detail="Volunteer not found")

@router.delete("/volunteers/{volunteer_id}")
def delete_volunteer(volunteer_id: int):
    """Supprimer un volontaire"""
    for idx, v in enumerate(volunteers_db):
        if v.id == volunteer_id:
            del volunteers_db[idx]
            return {"detail": "Volunteer deleted"}
    raise HTTPException(status_code=404, detail="Volunteer not found")
