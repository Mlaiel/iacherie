"""IA Influencer Agent - KYC Verification System
Know Your Customer verification and identity management

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: All rights reserved - Unauthorized use prohibited
"""
import asyncio
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Set
from enum import Enum
from dataclasses import dataclass, asdict
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, insert
from fastapi import HTTPException, UploadFile

from backend.core.database import get_db_session
from backend.core.config import settings
from backend.models.kyc import KYCVerification, IdentityDocument, RiskAssessment
from backend.utils.document_verification import verify_identity_document
from backend.utils.sanctions_screening import screen_against_sanctions
from backend.utils.ai_verification import analyze_document_authenticity
from backend.core.security import encrypt_sensitive_data, hash_pii
from backend.core.logging import get_logger
from .audit_logger import AuditLogger, AuditCategory, AuditLevel

logger = get_logger(__name__)


class KYCLevel(str, Enum):
    """KYC verification levels"""    BASIC = "basic"
    ENHANCED = "enhanced"
    PREMIUM = "premium"
    INSTITUTIONAL = "institutional"


class VerificationStatus(str, Enum):
    """Verification status states"""    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    APPROVED = "approved"
    REJECTED = "rejected"
    EXPIRED = "expired"
    SUSPENDED = "suspended"
    REQUIRES_REVIEW = "requires_review"


class DocumentType(str, Enum):
    """Identity document types"""    PASSPORT = "passport"
    NATIONAL_ID = "national_id"
    DRIVERS_LICENSE = "drivers_license"
    RESIDENCE_PERMIT = "residence_permit"
    UTILITY_BILL = "utility_bill"
    BANK_STATEMENT = "bank_statement"
    TAX_DOCUMENT = "tax_document"
    BUSINESS_REGISTRATION = "business_registration"


class RiskLevel(str, Enum):
    """Risk assessment levels"""    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class IdentityVerificationResult:
    """Identity verification analysis result"""    document_type: DocumentType
    authenticity_score: float
    ocr_confidence: float
    face_match_score: Optional[float]
    document_quality: str
    extracted_data: Dict[str, Any]
    verification_checks: Dict[str, bool]
    risk_indicators: List[str]
    recommendation: str


@dataclass
class ComplianceRequirement:
    """KYC compliance requirement definition"""    requirement_id: str
    name: str
    description: str
    required_documents: List[DocumentType]
    verification_level: KYCLevel
    jurisdiction: str
    regulation_reference: str
    expiry_period_days: int
    automated_verification: bool


class KYCVerificationSystem:
    """Enterprise KYC verification and compliance system"""    
    def __init__(self):
        self.logger = logger
        self.audit_logger = AuditLogger()
        self.automated_verification = settings.KYC_AUTOMATED_VERIFICATION
        self.ai_verification_enabled = settings.KYC_AI_VERIFICATION_ENABLED
        self.sanctions_screening_enabled = settings.KYC_SANCTIONS_SCREENING
        self.face_matching_enabled = settings.KYC_FACE_MATCHING
        
        # KYC compliance requirements by jurisdiction
        self.compliance_requirements = self._load_compliance_requirements()
        
        # Document verification thresholds
        self.verification_thresholds = {
            "document_authenticity": 0.85,
            "ocr_confidence": 0.90,
            "face_match": 0.85,
            "document_quality": 0.80
        }
        
        # Risk scoring weights
        self.risk_weights = {
            "sanctions_match": 100,
            "pep_match": 50,
            "adverse_media": 30,
            "high_risk_country": 20,
            "document_inconsistency": 40,
            "multiple_applications": 25
        }
    
    async def initiate_kyc_verification(
        self,
        user_id: int,
        verification_level: KYCLevel,
        jurisdiction: str = "EU",
        business_purpose: str = "platform_access"
    ) -> Dict[str, Any]:
        """Initiate KYC verification process for user"""        try:
            # Check existing verification
            existing_verification = await self._get_existing_verification(user_id)
            if existing_verification and existing_verification.status == VerificationStatus.APPROVED:
                if existing_verification.verification_level == verification_level:
                    return {
                        "verification_id": existing_verification.verification_id,
                        "status": "already_verified",
                        "level": verification_level.value,
                        "expires_at": existing_verification.expires_at.isoformat()
                    }
            
            # Generate verification ID
            verification_id = f"KYC-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}-{user_id:08d}"
            
            # Get compliance requirements
            requirements = self._get_compliance_requirements(verification_level, jurisdiction)
            
            # Create verification record
            async with get_db_session() as session:
                kyc_verification = KYCVerification(
                    verification_id=verification_id,
                    user_id=user_id,
                    verification_level=verification_level.value,
                    jurisdiction=jurisdiction,
                    business_purpose=business_purpose,
                    status=VerificationStatus.PENDING.value,
                    required_documents=json.dumps([doc.value for doc in requirements.required_documents]),
                    initiated_at=datetime.utcnow(),
                    expires_at=datetime.utcnow() + timedelta(days=requirements.expiry_period_days),
                    compliance_framework=requirements.regulation_reference
                )
                
                session.add(kyc_verification)
                await session.commit()
            
            # Log KYC initiation
            await self.audit_logger.log_audit_event(
                event_type="kyc_verification_initiated",
                category=AuditCategory.COMPLIANCE,
                level=AuditLevel.INFO,
                message=f"KYC verification initiated for user {user_id}",
                details={
                    "verification_id": verification_id,
                    "user_id": user_id,
                    "verification_level": verification_level.value,
                    "jurisdiction": jurisdiction,
                    "required_documents": [doc.value for doc in requirements.required_documents]
                },
                user_id=user_id
            )
            
            return {
                "verification_id": verification_id,
                "status": VerificationStatus.PENDING.value,
                "verification_level": verification_level.value,
                "jurisdiction": jurisdiction,
                "required_documents": [doc.value for doc in requirements.required_documents],
                "expires_at": (datetime.utcnow() + timedelta(days=requirements.expiry_period_days)).isoformat(),
                "submission_deadline": (datetime.utcnow() + timedelta(days=30)).isoformat(),
                "next_steps": [
                    "Upload required identity documents",
                    "Complete identity verification",
                    "Wait for verification review"
                ]
            }
            
        except Exception as e:
            self.logger.error(f"Error initiating KYC verification: {str(e)}")
            raise HTTPException(status_code=500, detail="Failed to initiate KYC verification")
    
    async def submit_identity_document(
        self,
        verification_id: str,
        document_type: DocumentType,
        document_file: UploadFile,
        selfie_file: Optional[UploadFile] = None,
        additional_data: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Submit identity document for verification"""        try:
            # Get verification record
            async with get_db_session() as session:
                verification_result = await session.execute(
                    select(KYCVerification).where(
                        KYCVerification.verification_id == verification_id
                    )
                )
                verification = verification_result.scalar_one_or_none()
                
                if not verification:
                    raise HTTPException(status_code=404, detail="Verification not found")
                
                if verification.status not in [VerificationStatus.PENDING.value, VerificationStatus.IN_PROGRESS.value]:
                    raise HTTPException(status_code=400, detail="Verification not accepting documents")
            
            # Process document upload
            document_id = f"DOC-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}-{verification_id[-8:]}"
            
            # Store document securely
            document_path = await self._store_document_securely(
                document_file, document_id, verification.user_id
            )
            
            selfie_path = None
            if selfie_file and self.face_matching_enabled:
                selfie_path = await self._store_document_securely(
                    selfie_file, f"{document_id}-selfie", verification.user_id
                )
            
            # Perform AI verification if enabled
            verification_result = None
            if self.ai_verification_enabled:
                verification_result = await self._verify_document_with_ai(
                    document_path, document_type, selfie_path
                )
            
            # Create document record
            async with get_db_session() as session:
                identity_document = IdentityDocument(
                    document_id=document_id,
                    verification_id=verification_id,
                    user_id=verification.user_id,
                    document_type=document_type.value,
                    document_path=document_path,
                    selfie_path=selfie_path,
                    verification_result=json.dumps(asdict(verification_result)) if verification_result else None,
                    status=VerificationStatus.IN_PROGRESS.value,
                    submitted_at=datetime.utcnow(),
                    additional_data=json.dumps(additional_data or {})
                )
                
                session.add(identity_document)
                
                # Update verification status
                await session.execute(
                    update(KYCVerification)
                    .where(KYCVerification.verification_id == verification_id)
                    .values(
                        status=VerificationStatus.IN_PROGRESS.value,
                        last_updated=datetime.utcnow()
                    )
                )
                
                await session.commit()
            
            # Perform automated verification if enabled
            if self.automated_verification and verification_result:
                await self._process_automated_verification(
                    verification_id, document_id, verification_result
                )
            
            # Log document submission
            await self.audit_logger.log_audit_event(
                event_type="kyc_document_submitted",
                category=AuditCategory.COMPLIANCE,
                level=AuditLevel.INFO,
                message=f"Identity document submitted for verification {verification_id}",
                details={
                    "verification_id": verification_id,
                    "document_id": document_id,
                    "document_type": document_type.value,
                    "has_selfie": bool(selfie_file),
                    "automated_verification": self.ai_verification_enabled,
                    "verification_score": verification_result.authenticity_score if verification_result else None
                },
                user_id=verification.user_id
            )
            
            return {
                "document_id": document_id,
                "verification_id": verification_id,
                "document_type": document_type.value,
                "status": VerificationStatus.IN_PROGRESS.value,
                "submitted_at": datetime.utcnow().isoformat(),
                "verification_result": asdict(verification_result) if verification_result else None,
                "automated_processing": self.automated_verification,
                "estimated_processing_time": "2-5 business days" if not self.automated_verification else "5-30 minutes"
            }
            
        except Exception as e:
            self.logger.error(f"Error submitting identity document: {str(e)}")
            raise HTTPException(status_code=500, detail="Failed to submit identity document")
    
    async def complete_verification_review(
        self,
        verification_id: str,
        reviewer_id: str,
        decision: VerificationStatus,
        review_notes: str = None
    ) -> Dict[str, Any]:
        """Complete manual review of KYC verification"""        try:
            if decision not in [VerificationStatus.APPROVED, VerificationStatus.REJECTED]:
                raise ValueError("Decision must be APPROVED or REJECTED")
            
            # Get verification record
            async with get_db_session() as session:
                verification_result = await session.execute(
                    select(KYCVerification).where(
                        KYCVerification.verification_id == verification_id
                    )
                )
                verification = verification_result.scalar_one_or_none()
                
                if not verification:
                    raise HTTPException(status_code=404, detail="Verification not found")
                
                # Perform final risk assessment
                risk_assessment = await self._perform_risk_assessment(
                    verification.user_id, verification_id
                )
                
                # Update verification status
                completion_time = datetime.utcnow()
                await session.execute(
                    update(KYCVerification)
                    .where(KYCVerification.verification_id == verification_id)
                    .values(
                        status=decision.value,
                        reviewed_by=reviewer_id,
                        review_notes=review_notes,
                        completed_at=completion_time,
                        risk_score=risk_assessment.overall_risk_score,
                        risk_level=risk_assessment.risk_level.value,
                        last_updated=completion_time
                    )
                )
                
                # Store risk assessment
                risk_record = RiskAssessment(
                    assessment_id=f"RISK-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}-{verification_id[-8:]}",
                    verification_id=verification_id,
                    user_id=verification.user_id,
                    risk_score=risk_assessment.overall_risk_score,
                    risk_level=risk_assessment.risk_level.value,
                    risk_factors=json.dumps(risk_assessment.risk_factors),
                    sanctions_result=json.dumps(risk_assessment.sanctions_screening),
                    pep_result=json.dumps(risk_assessment.pep_screening),
                    assessment_date=completion_time,
                    assessed_by="system"
                )
                
                session.add(risk_record)
                await session.commit()
            
            # Log verification completion
            await self.audit_logger.log_audit_event(
                event_type="kyc_verification_completed",
                category=AuditCategory.COMPLIANCE,
                level=AuditLevel.INFO if decision == VerificationStatus.APPROVED else AuditLevel.WARNING,
                message=f"KYC verification {decision.value} for {verification_id}",
                details={
                    "verification_id": verification_id,
                    "decision": decision.value,
                    "reviewer_id": reviewer_id,
                    "risk_score": risk_assessment.overall_risk_score,
                    "risk_level": risk_assessment.risk_level.value,
                    "processing_time_hours": (completion_time - verification.initiated_at).total_seconds() / 3600
                },
                user_id=verification.user_id
            )
            
            # Send notification to user
            await self._notify_user_verification_result(
                verification.user_id, verification_id, decision, review_notes
            )
            
            return {
                "verification_id": verification_id,
                "status": decision.value,
                "completed_at": completion_time.isoformat(),
                "risk_assessment": {
                    "risk_score": risk_assessment.overall_risk_score,
                    "risk_level": risk_assessment.risk_level.value,
                    "key_factors": risk_assessment.risk_factors[:3]  # Top 3 factors
                },
                "review_notes": review_notes,
                "reviewer_id": reviewer_id,
                "next_steps": self._get_next_steps_for_decision(decision)
            }
            
        except Exception as e:
            self.logger.error(f"Error completing verification review: {str(e)}")
            raise HTTPException(status_code=500, detail="Failed to complete verification review")
    
    async def check_verification_status(
        self,
        user_id: int,
        verification_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Check current KYC verification status for user"""        try:
            async with get_db_session() as session:
                query = select(KYCVerification).where(KYCVerification.user_id == user_id)
                
                if verification_id:
                    query = query.where(KYCVerification.verification_id == verification_id)
                else:
                    # Get most recent verification
                    query = query.order_by(KYCVerification.initiated_at.desc()).limit(1)
                
                result = await session.execute(query)
                verification = result.scalar_one_or_none()
                
                if not verification:
                    return {
                        "user_id": user_id,
                        "verification_status": "not_initiated",
                        "message": "No KYC verification found for user"
                    }
                
                # Get submitted documents
                docs_result = await session.execute(
                    select(IdentityDocument).where(
                        IdentityDocument.verification_id == verification.verification_id
                    )
                )
                documents = docs_result.scalars().all()
                
                # Calculate progress
                required_docs = json.loads(verification.required_documents)
                submitted_docs = [doc.document_type for doc in documents]
                progress_percentage = (len(submitted_docs) / len(required_docs)) * 100 if required_docs else 100
                
                return {
                    "verification_id": verification.verification_id,
                    "user_id": user_id,
                    "status": verification.status,
                    "verification_level": verification.verification_level,
                    "jurisdiction": verification.jurisdiction,
                    "progress_percentage": round(progress_percentage, 2),
                    "required_documents": required_docs,
                    "submitted_documents": submitted_docs,
                    "initiated_at": verification.initiated_at.isoformat(),
                    "expires_at": verification.expires_at.isoformat() if verification.expires_at else None,
                    "completed_at": verification.completed_at.isoformat() if verification.completed_at else None,
                    "risk_level": verification.risk_level,
                    "risk_score": verification.risk_score,
                    "review_notes": verification.review_notes,
                    "estimated_completion": self._estimate_completion_time(verification, len(submitted_docs), len(required_docs))
                }
                
        except Exception as e:
            self.logger.error(f"Error checking verification status: {str(e)}")
            raise HTTPException(status_code=500, detail="Failed to check verification status")
    
    async def _verify_document_with_ai(
        self,
        document_path: str,
        document_type: DocumentType,
        selfie_path: Optional[str] = None
    ) -> IdentityVerificationResult:
        """Verify document authenticity using AI"""        try:
            # Perform document verification
            document_analysis = await analyze_document_authenticity(document_path, document_type.value)
            
            # Perform face matching if selfie provided
            face_match_score = None
            if selfie_path and self.face_matching_enabled:
                face_match_score = await self._perform_face_matching(document_path, selfie_path)
            
            # Extract and validate data
            extracted_data = document_analysis.get("extracted_data", {})
            verification_checks = {
                "document_format_valid": document_analysis.get("format_valid", False),
                "security_features_present": document_analysis.get("security_features", False),
                "data_consistency": document_analysis.get("data_consistent", False),
                "tampering_detected": not document_analysis.get("tamper_free", True),
                "face_match_passed": face_match_score > self.verification_thresholds["face_match"] if face_match_score else None
            }
            
            # Identify risk indicators
            risk_indicators = []
            if document_analysis.get("authenticity_score", 0) < self.verification_thresholds["document_authenticity"]:
                risk_indicators.append("Low document authenticity score")
            if document_analysis.get("ocr_confidence", 0) < self.verification_thresholds["ocr_confidence"]:
                risk_indicators.append("Poor OCR confidence")
            if face_match_score and face_match_score < self.verification_thresholds["face_match"]:
                risk_indicators.append("Face matching failed")
            if verification_checks["tampering_detected"]:
                risk_indicators.append("Document tampering detected")
            
            # Generate recommendation
            passed_checks = sum(1 for check, result in verification_checks.items() 
                              if result is True or (result is None and check == "face_match_passed"))
            total_checks = len([check for check, result in verification_checks.items() if result is not None])
            
            if total_checks > 0 and (passed_checks / total_checks) >= 0.8 and not risk_indicators:
                recommendation = "APPROVE"
            elif risk_indicators or (total_checks > 0 and (passed_checks / total_checks) < 0.5):
                recommendation = "REJECT"
            else:
                recommendation = "MANUAL_REVIEW"
            
            return IdentityVerificationResult(
                document_type=document_type,
                authenticity_score=document_analysis.get("authenticity_score", 0.0),
                ocr_confidence=document_analysis.get("ocr_confidence", 0.0),
                face_match_score=face_match_score,
                document_quality=document_analysis.get("quality_assessment", "unknown"),
                extracted_data=extracted_data,
                verification_checks=verification_checks,
                risk_indicators=risk_indicators,
                recommendation=recommendation
            )
            
        except Exception as e:
            self.logger.error(f"Error in AI document verification: {str(e)}")
            raise
    
    def _load_compliance_requirements(self) -> Dict[str, ComplianceRequirement]:
        """Load KYC compliance requirements by jurisdiction"""        return {
            "EU_BASIC": ComplianceRequirement(
                requirement_id="EU_BASIC",
                name="EU Basic KYC",
                description="Basic KYC requirements for EU jurisdiction",
                required_documents=[DocumentType.NATIONAL_ID, DocumentType.UTILITY_BILL],
                verification_level=KYCLevel.BASIC,
                jurisdiction="EU",
                regulation_reference="AMLD5",
                expiry_period_days=365,
                automated_verification=True
            ),
            "EU_ENHANCED": ComplianceRequirement(
                requirement_id="EU_ENHANCED",
                name="EU Enhanced KYC",
                description="Enhanced KYC requirements for EU jurisdiction",
                required_documents=[
                    DocumentType.PASSPORT, 
                    DocumentType.UTILITY_BILL, 
                    DocumentType.BANK_STATEMENT
                ],
                verification_level=KYCLevel.ENHANCED,
                jurisdiction="EU",
                regulation_reference="AMLD5",
                expiry_period_days=730,
                automated_verification=False
            )
        }


# Export for use in other modules
__all__ = ["KYCVerificationSystem", "KYCLevel", "VerificationStatus", "DocumentType", "RiskLevel"]
