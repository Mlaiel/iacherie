"""
Models package for MedCare-AI
"""
from .patient import Patient, PatientCreate
from .consultation import Consultation, ConsultationCreate, ConsultationRequest, ConsultationSummary
from .prescription import Prescription, PrescriptionCreate, PrescriptionVerification
from .medical_record import (
    SymptomReport, SymptomReportCreate, SymptomReportWithAnalysis,
    Diagnosis, DiagnosisCreate, DiagnosisResponse, UrgencyLevel
)

__all__ = [
    "Patient", "PatientCreate",
    "Consultation", "ConsultationCreate", "ConsultationRequest", "ConsultationSummary",
    "Prescription", "PrescriptionCreate", "PrescriptionVerification",
    "SymptomReport", "SymptomReportCreate", "SymptomReportWithAnalysis",
    "Diagnosis", "DiagnosisCreate", "DiagnosisResponse", "UrgencyLevel"
]
