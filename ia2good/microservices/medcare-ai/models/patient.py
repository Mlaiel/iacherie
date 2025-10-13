"""
Patient model for MedCare-AI
"""
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List
from uuid import UUID
from datetime import date

class MedicalHistory(BaseModel):
    """Medical history embedded in patient"""
    allergies: List[str] = Field(default_factory=list)
    chronic_conditions: List[str] = Field(default_factory=list)
    current_medications: List[dict] = Field(default_factory=list)
    
class EmergencyContact(BaseModel):
    """Emergency contact information"""
    name: str
    relationship: str
    phone: str
    email: Optional[str] = None

class InsuranceInfo(BaseModel):
    """Insurance information"""
    provider: str
    policy_number: str
    group_number: Optional[str] = None
    expiry_date: Optional[date] = None

class PatientBase(BaseModel):
    """Base patient information"""
    birth_date: date
    gender: str
    blood_type: Optional[str] = None
    height_cm: Optional[int] = None
    weight_kg: Optional[float] = None

class PatientCreate(PatientBase):
    """Patient creation model"""
    user_id: UUID
    allergies: List[str] = Field(default_factory=list)
    chronic_conditions: List[str] = Field(default_factory=list)
    current_medications: List[dict] = Field(default_factory=list)
    emergency_contact: Optional[EmergencyContact] = None
    insurance_info: Optional[InsuranceInfo] = None

class Patient(PatientBase):
    """Complete patient model"""
    id: UUID
    user_id: UUID
    allergies: List[str]
    chronic_conditions: List[str]
    current_medications: List[dict]
    emergency_contact: Optional[EmergencyContact]
    insurance_info: Optional[InsuranceInfo]
    
    model_config = ConfigDict(from_attributes=True)
