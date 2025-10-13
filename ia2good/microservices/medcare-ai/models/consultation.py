"""
Consultation model for MedCare-AI
"""
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List
from uuid import UUID
from datetime import datetime
from enum import Enum

class ConsultationType(str, Enum):
    """Types of consultations"""
    VIDEO = "video"
    CHAT = "chat"
    PHONE = "phone"
    IN_PERSON = "in_person"

class ConsultationStatus(str, Enum):
    """Consultation status"""
    SCHEDULED = "scheduled"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    NO_SHOW = "no_show"

class ConsultationBase(BaseModel):
    """Base consultation information"""
    type: ConsultationType
    scheduled_at: Optional[datetime] = None

class ConsultationCreate(ConsultationBase):
    """Consultation creation model"""
    patient_id: UUID
    symptom_report_id: Optional[UUID] = None
    notes: Optional[str] = None

class ConsultationUpdate(BaseModel):
    """Consultation update model avec support multilingue (644+ langues)"""
    status: Optional[ConsultationStatus] = None
    started_at: Optional[datetime] = None
    ended_at: Optional[datetime] = None
    notes: Optional[str] = None
    notes_translations: Optional[dict] = None  # {"EN": "...", "FR": "...", ...}
    diagnosis: Optional[str] = None
    diagnosis_translations: Optional[dict] = None  # 644 langues

class Consultation(ConsultationBase):
    """Complete consultation model avec support multilingue (644+ langues)"""
    id: UUID
    patient_id: UUID
    doctor_id: Optional[UUID] = None
    symptom_report_id: Optional[UUID] = None
    status: ConsultationStatus
    scheduled_at: Optional[datetime] = None
    started_at: Optional[datetime] = None
    ended_at: Optional[datetime] = None
    duration_minutes: Optional[int] = None
    notes: Optional[str] = None
    notes_translations: Optional[dict] = None  # Traductions dans 644 langues
    diagnosis: Optional[str] = None
    diagnosis_translations: Optional[dict] = None  # 644 langues
    prescription_translations: Optional[dict] = None  # 644 langues
    treatment_plan_translations: Optional[dict] = None  # 644 langues
    language: Optional[str] = "EN"  # Langue du patient
    amount: Optional[float] = None
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)

class ConsultationRequest(BaseModel):
    """Request for a consultation"""
    symptom_report_id: Optional[UUID] = None
    preferred_specialty: Optional[str] = None
    urgency: str  # emergency, urgent, routine
    preferred_time: Optional[datetime] = None
    consultation_type: Optional[ConsultationType] = ConsultationType.VIDEO
    
class ConsultationSummary(BaseModel):
    """Summary after consultation completion - Support multilingue (644+ langues)"""
    diagnosis: str
    diagnosis_translations: Optional[dict] = None  # 644 langues
    notes: str
    notes_translations: Optional[dict] = None  # 644 langues
    follow_up_required: bool = False
    follow_up_date: Optional[datetime] = None
    follow_up_instructions_translations: Optional[dict] = None  # 644 langues
    prescriptions: Optional[List[dict]] = None
    language: str = "EN"  # Langue préférée du patient
