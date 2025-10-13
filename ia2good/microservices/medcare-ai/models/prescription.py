"""
Prescription model for MedCare-AI
"""
from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional
from uuid import UUID
from datetime import date, datetime

class Medication(BaseModel):
    """Medication details"""
    name: str
    dosage: str
    frequency: str
    duration_days: int
    instructions: Optional[str] = None

class PrescriptionBase(BaseModel):
    """Base prescription information"""
    medications: List[Medication]
    instructions: Optional[str] = None
    valid_until: date

class PrescriptionCreate(BaseModel):
    """Prescription creation model"""
    consultation_id: Optional[UUID] = None
    patient_id: UUID
    medications: List[Medication]
    instructions: Optional[str] = None
    valid_until: Optional[date] = None  # Auto-calculated if not provided

class Prescription(PrescriptionBase):
    """Complete prescription model"""
    id: UUID
    consultation_id: Optional[UUID] = None
    patient_id: UUID
    doctor_id: UUID
    qr_code: str
    dispensed: bool = False
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)

class PrescriptionVerification(BaseModel):
    """Prescription verification result"""
    valid: bool
    prescription_id: Optional[UUID] = None
    patient_name: Optional[str] = None
    doctor_name: Optional[str] = None
    medications: Optional[List[Medication]] = None
    issued_date: Optional[datetime] = None
    expiry_date: Optional[date] = None
    already_dispensed: bool = False
    error: Optional[str] = None
