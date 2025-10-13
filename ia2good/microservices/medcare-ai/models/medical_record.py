"""
Medical Record model for MedCare-AI
"""
from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional
from uuid import UUID
from datetime import datetime
from enum import Enum

class UrgencyLevel(str, Enum):
    """Urgency levels for medical conditions"""
    EMERGENCY = "emergency"
    URGENT = "urgent"
    ROUTINE = "routine"
    MONITOR = "monitor"

class SymptomReport(BaseModel):
    """Symptom report from patient"""
    symptoms: dict  # e.g., {"pain": {"location": "abdomen", "severity": 7}}
    severity: int = Field(ge=1, le=10)
    duration_hours: int
    body_parts: List[str] = Field(default_factory=list)
    images: List[str] = Field(default_factory=list)

class SymptomReportCreate(SymptomReport):
    """Create symptom report"""
    patient_id: UUID

class SymptomReportWithAnalysis(SymptomReport):
    """Symptom report with AI analysis"""
    id: UUID
    patient_id: UUID
    ai_analysis: Optional[dict] = None
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)

class Diagnosis(BaseModel):
    """AI-generated or doctor diagnosis"""
    condition_name: str
    confidence: float = Field(ge=0, le=1)
    icd10_code: Optional[str] = None
    urgency: UrgencyLevel
    recommendations: str
    differential_diagnoses: List[dict] = Field(default_factory=list)

class DiagnosisCreate(BaseModel):
    """Create diagnosis"""
    symptom_report_id: Optional[UUID] = None
    condition_name: Optional[str] = None
    confidence: Optional[float] = Field(default=None, ge=0, le=1)
    icd10_code: Optional[str] = None
    urgency: Optional[UrgencyLevel] = None
    recommendations: Optional[str] = None
    differential_diagnoses: Optional[List[dict]] = Field(default_factory=list)

class DiagnosisResponse(Diagnosis):
    """Diagnosis response"""
    id: UUID
    symptom_report_id: UUID
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)
