"""
Medical Document models for MedCare-AI
Supports: prescriptions, lab results, X-rays, MRI, dialysis reports, etc.
"""
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List, Dict
from uuid import UUID
from datetime import datetime
from enum import Enum

class DocumentType(str, Enum):
    """Types of medical documents"""
    PRESCRIPTION = "prescription"
    LAB_RESULT = "lab_result"
    XRAY = "xray"
    MRI = "mri"
    CT_SCAN = "ct_scan"
    DIALYSIS_REPORT = "dialysis_report"
    BLOOD_TEST = "blood_test"
    ULTRASOUND = "ultrasound"
    ECG = "ecg"
    PATHOLOGY_REPORT = "pathology_report"
    VACCINATION_RECORD = "vaccination_record"
    SURGICAL_REPORT = "surgical_report"
    OTHER = "other"

class MedicalDocumentUpload(BaseModel):
    """Upload medical document"""
    patient_id: UUID
    document_type: DocumentType
    original_filename: str
    mime_type: str
    language_detected: Optional[str] = "auto"  # Auto-detect
    
class MedicalDocumentCreate(MedicalDocumentUpload):
    """Create medical document after upload"""
    file_url: str
    file_size_bytes: int
    ocr_text: Optional[str] = None
    ai_analysis: Optional[Dict] = None

class MedicalDocument(BaseModel):
    """Complete medical document"""
    id: UUID
    patient_id: UUID
    document_type: DocumentType
    original_filename: str
    file_url: str
    file_size_bytes: int
    mime_type: str
    language_detected: Optional[str]
    ocr_text: Optional[str]
    ai_analysis: Optional[Dict]
    is_shared_anonymously: bool = False
    anonymous_share_id: Optional[UUID] = None
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)

class DocumentAnalysisResult(BaseModel):
    """Result of AI analysis on document"""
    document_id: UUID
    document_type: DocumentType
    detected_language: str
    ocr_confidence: float = Field(ge=0, le=1)
    extracted_text: str
    structured_data: Dict  # Parsed medical data
    key_findings: List[str]
    abnormal_values: List[Dict]  # [{parameter, value, normal_range, severity}]
    recommendations: List[str]
    requires_attention: bool
    urgency_level: str  # normal, elevated, urgent, critical
    
class ShareDocumentRequest(BaseModel):
    """Request to share document anonymously for community review"""
    share_reason: str
    specific_questions: Optional[List[str]] = None
    target_specialties: Optional[List[str]] = None  # cardiologist, radiologist, etc.
