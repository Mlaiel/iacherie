"""IA Influencer Agent - Privacy Controls Manager
Advanced privacy protection and user control systems

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
from sqlalchemy import select, update, insert, delete
from fastapi import HTTPException

from backend.core.database import get_db_session
from backend.core.config import settings
from backend.models.privacy import PrivacySetting, DataProcessingConsent, PrivacyAudit
from backend.models.user import User
from backend.core.encryption import encrypt_personal_data, decrypt_personal_data
from backend.utils.anonymization import anonymize_data, pseudonymize_data
from backend.core.logging import get_logger
from .audit_logger import AuditLogger, AuditCategory, AuditLevel
from .gdpr_compliance import GDPRComplianceManager, ConsentPurpose

logger = get_logger(__name__)


class PrivacyLevel(str, Enum):
    """
Privacy protection levels"""

    MINIMAL = "minimal"
    STANDARD = "standard"
    ENHANCED = "enhanced"
    MAXIMUM = "maximum"


class DataMinimization(str, Enum):
    """Data minimization strategies"""

    COLLECT_MINIMAL = "collect_minimal"
    PROCESS_MINIMAL = "process_minimal"
    STORE_MINIMAL = "store_minimal"
    SHARE_MINIMAL = "share_minimal"


class AnonymizationLevel(str, Enum):
    """Data anonymization levels"""

    NONE = "none"
    PSEUDONYMIZATION = "pseudonymization"
    ANONYMIZATION = "anonymization"
    DIFFERENTIAL_PRIVACY = "differential_privacy"


class AccessRight(str, Enum):
    """Data subject access rights"""

    VIEW = "view"
    DOWNLOAD = "download"
    CORRECT = "correct"
    DELETE = "delete"
    RESTRICT = "restrict"
    OBJECT = "object"
    PORTABILITY = "portability"


@dataclass
class PrivacyConfiguration:
    """User privacy configuration"""
    user_id: int
    privacy_level: PrivacyLevel
    data_minimization: DataMinimization
    anonymization_level: AnonymizationLevel
    consent_preferences: Dict[str, bool]
    data_sharing_permissions: Dict[str, bool]
    marketing_preferences: Dict[str, bool]
    analytics_participation: bool
    third_party_sharing: bool
    cross_border_transfer: bool
    automated_decision_making: bool
    profiling_consent: bool


@dataclass
class PrivacyImpactAssessment:
    """
Privacy Impact Assessment (PIA) result"""
    assessment_id: str
    data_processing_activity: str
    privacy_risks: List[str]
    risk_severity: str
    mitigation_measures: List[str]
    residual_risk: str
    assessment_date: datetime
    assessor_id: str
    review_date: datetime
    approved: bool


@dataclass
class DataSubjectRequest:
    """
Data subject rights request"""
    request_id: str
    user_id: int
    request_type: AccessRight
    status: str
    requested_at: datetime
    processed_at: Optional[datetime]
    response_data: Optional[Dict[str, Any]]
    verification_status: str
    processing_notes: str


class PrivacyControlsManager:
    """
Advanced privacy protection and user control system"""
    
    def __init__(self) -> None:
        self.logger = logger
        self.audit_logger = AuditLogger()
        self.gdpr_manager = GDPRComplianceManager()
        self.privacy_by_design = settings.PRIVACY_BY_DESIGN_ENABLED
        self.automated_anonymization = settings.AUTOMATED_ANONYMIZATION_ENABLED
        self.differential_privacy = settings.DIFFERENTIAL_PRIVACY_ENABLED
        
        # Privacy configuration templates
        self.privacy_templates = self._load_privacy_templates()
        
        # Data processing purposes mapping
        self.processing_purposes = {
            "service_delivery": {
                "lawful_basis": "contract",
                "required": True,
                "user_controllable": False
            },
            "analytics": {
                "lawful_basis": "consent",
                "required": False,
                "user_controllable": True
            },
            "marketing": {
                "lawful_basis": "consent",
                "required": False,
                "user_controllable": True
            },
            "personalization": {
                "lawful_basis": "consent",
                "required": False,
                "user_controllable": True
            },
            "research": {
                "lawful_basis": "legitimate_interest",
                "required": False,
                "user_controllable": True
            }
        }
    
    async def initialize_user_privacy_settings(
        self,
        user_id: int,
        privacy_level: PrivacyLevel = PrivacyLevel.STANDARD,
        jurisdiction: str = "EU"
    ) -> Dict[str, Any]:
        """Initialize privacy settings for new user"""
        try:
            # Get privacy template for jurisdiction
            template = self._get_privacy_template(jurisdiction, privacy_level)
            
            # Create privacy configuration
            privacy_config = PrivacyConfiguration(
                user_id=user_id,
                privacy_level=privacy_level,
                data_minimization=template["data_minimization"],
                anonymization_level=template["anonymization_level"],
                consent_preferences=template["consent_preferences"],
                data_sharing_permissions=template["data_sharing_permissions"],
                marketing_preferences=template["marketing_preferences"],
                analytics_participation=template["analytics_participation"],
                third_party_sharing=template["third_party_sharing"],
                cross_border_transfer=template["cross_border_transfer"],
                automated_decision_making=template["automated_decision_making"],
                profiling_consent=template["profiling_consent"]
            )
            
            # Store privacy settings
            async with get_db_session() as session:
                privacy_setting = PrivacySetting(
                    user_id=user_id,
                    privacy_level=privacy_level.value,
                    configuration=json.dumps(asdict(privacy_config)),
                    jurisdiction=jurisdiction,
                    created_at=datetime.utcnow(),
                    updated_at=datetime.utcnow(),
                    version=1
                )
                
                session.add(privacy_setting)
                await session.commit()
            
            # Record consent for essential processing
            for purpose, config in self.processing_purposes.items():
                if config["required"]:
                    await self.gdpr_manager.record_consent(
                        user_id=user_id,
                        purpose=ConsentPurpose(purpose),
                        granted=True,
                        ip_address="system",
                        user_agent="initialization",
                        explicit_consent=False
                    )
            
            # Log privacy initialization
            await self.audit_logger.log_audit_event(
                event_type="privacy_settings_initialized",
                category=AuditCategory.PRIVACY,
                level=AuditLevel.INFO,
                message=f"Privacy settings initialized for user {user_id}",
                details={
                    "user_id": user_id,
                    "privacy_level": privacy_level.value,
                    "jurisdiction": jurisdiction,
                    "template_applied": template["template_id"]
                },
                user_id=user_id
            )
            
            return {
                "user_id": user_id,
                "privacy_level": privacy_level.value,
                "jurisdiction": jurisdiction,
                "configuration": asdict(privacy_config),
                "initialized_at": datetime.utcnow().isoformat(),
                "next_steps": [
                    "Review and adjust privacy preferences",
                    "Configure marketing preferences",
                    "Set data sharing permissions"
                ]
            }
            
        except Exception as e:
            self.logger.error(f"Error initializing privacy settings: {str(e)}")
            raise HTTPException(status_code=500, detail="Failed to initialize privacy settings")
    
    async def update_privacy_preferences(
        self,
        user_id: int,
        preferences_update: Dict[str, Any],
        ip_address: str,
        user_agent: str
    ) -> Dict[str, Any]:
        """Update user privacy preferences"""
        try:
            # Get current privacy settings
            async with get_db_session() as session:
                settings_result = await session.execute(
                    select(PrivacySetting).where(PrivacySetting.user_id == user_id)
                )
                current_settings = settings_result.scalar_one_or_none()
                
                if not current_settings:
                    raise HTTPException(status_code=404, detail="Privacy settings not found")
                
                # Parse current configuration
                current_config = json.loads(current_settings.configuration)
                
                # Track changes for consent management
                consent_changes = []
                
                # Update configuration
                for key, value in preferences_update.items():
                    if key in current_config:
                        old_value = current_config[key]
                        current_config[key] = value
                        
                        # Track consent-related changes
                        if key == "consent_preferences" and isinstance(value, dict):
                            for purpose, granted in value.items():
                                if purpose in old_value and old_value[purpose] != granted:
                                    consent_changes.append({
                                        "purpose": purpose,
                                        "old_value": old_value[purpose],
                                        "new_value": granted
                                    })
                
                # Update privacy settings
                await session.execute(
                    update(PrivacySetting)
                    .where(PrivacySetting.user_id == user_id)
                    .values(
                        configuration=json.dumps(current_config),
                        updated_at=datetime.utcnow(),
                        version=current_settings.version + 1
                    )
                )
                await session.commit()
            
            # Process consent changes
            for change in consent_changes:
                if change["purpose"] in [p.value for p in ConsentPurpose]:
                    if change["new_value"] != change["old_value"]:
                        if change["new_value"]:
                            await self.gdpr_manager.record_consent(
                                user_id=user_id,
                                purpose=ConsentPurpose(change["purpose"]),
                                granted=True,
                                ip_address=ip_address,
                                user_agent=user_agent,
                                explicit_consent=True
                            )
                        else:
                            await self.gdpr_manager.withdraw_consent(
                                user_id=user_id,
                                purpose=ConsentPurpose(change["purpose"]),
                                ip_address=ip_address
                            )
            
            # Apply privacy controls immediately
            await self._apply_privacy_controls(user_id, current_config)
            
            # Log privacy update
            await self.audit_logger.log_audit_event(
                event_type="privacy_preferences_updated",
                category=AuditCategory.PRIVACY,
                level=AuditLevel.INFO,
                message=f"Privacy preferences updated for user {user_id}",
                details={
                    "user_id": user_id,
                    "preferences_updated": list(preferences_update.keys()),
                    "consent_changes": consent_changes,
                    "ip_address": ip_address
                },
                user_id=user_id
            )
            
            return {
                "user_id": user_id,
                "updated_at": datetime.utcnow().isoformat(),
                "preferences_updated": list(preferences_update.keys()),
                "consent_changes_processed": len(consent_changes),
                "configuration": current_config
            }
            
        except Exception as e:
            self.logger.error(f"Error updating privacy preferences: {str(e)}")
            raise HTTPException(status_code=500, detail="Failed to update privacy preferences")
    
    async def process_data_subject_request(
        self,
        user_id: int,
        request_type: AccessRight,
        verification_data: Dict[str, Any],
        additional_details: str = None
    ) -> str:
        """Process data subject access rights request"""
        try:
            # Generate request ID
            request_id = f"DSR-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}-{user_id:08d}"
            
            # Verify user identity
            verification_status = await self._verify_data_subject_identity(
                user_id, verification_data
            )
            
            if not verification_status["verified"]:
                raise HTTPException(
                    status_code=400, 
                    detail="Identity verification failed"
                )
            
            # Create request record
            async with get_db_session() as session:
                dsr = DataSubjectRequest(
                    request_id=request_id,
                    user_id=user_id,
                    request_type=request_type.value,
                    status="pending",
                    requested_at=datetime.utcnow(),
                    processed_at=None,
                    response_data=None,
                    verification_status="verified",
                    processing_notes=additional_details or ""
                )
                
                db_request = DataSubjectRequest(
                    request_id=request_id,
                    user_id=user_id,
                    request_type=request_type.value,
                    status="pending",
                    requested_at=datetime.utcnow(),
                    verification_details=json.dumps(verification_data),
                    additional_details=additional_details
                )
                
                session.add(db_request)
                await session.commit()
            
            # Process request based on type
            if request_type in [AccessRight.VIEW, AccessRight.DOWNLOAD, AccessRight.PORTABILITY]:
                # Schedule data extraction
                await self._schedule_data_extraction(request_id, user_id, request_type)
            elif request_type == AccessRight.DELETE:
                # Schedule data deletion
                await self._schedule_data_deletion(request_id, user_id)
            elif request_type == AccessRight.CORRECT:
                # Mark for manual review
                await self._mark_for_manual_review(request_id, "data_correction")
            elif request_type in [AccessRight.RESTRICT, AccessRight.OBJECT]:
                # Apply processing restrictions
                await self._apply_processing_restrictions(user_id, request_type)
            
            # Log request
            await self.audit_logger.log_audit_event(
                event_type="data_subject_request_submitted",
                category=AuditCategory.PRIVACY,
                level=AuditLevel.INFO,
                message=f"Data subject request submitted: {request_type.value}",
                details={
                    "request_id": request_id,
                    "user_id": user_id,
                    "request_type": request_type.value,
                    "verification_status": verification_status["status"]
                },
                user_id=user_id
            )
            
            return request_id
            
        except Exception as e:
            self.logger.error(f"Error processing data subject request: {str(e)}")
            raise HTTPException(status_code=500, detail="Failed to process data subject request")
    
    async def conduct_privacy_impact_assessment(
        self,
        processing_activity: str,
        data_types: List[str],
        processing_purposes: List[str],
        risk_factors: List[str]
    ) -> PrivacyImpactAssessment:
        """Conduct Privacy Impact Assessment (PIA)"""
        try:
            assessment_id = f"PIA-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"
            
            # Analyze privacy risks
            privacy_risks = await self._analyze_privacy_risks(
                data_types, processing_purposes, risk_factors
            )
            
            # Assess risk severity
            risk_severity = self._calculate_risk_severity(privacy_risks)
            
            # Generate mitigation measures
            mitigation_measures = await self._generate_mitigation_measures(
                privacy_risks, processing_activity
            )
            
            # Calculate residual risk
            residual_risk = self._calculate_residual_risk(
                risk_severity, mitigation_measures
            )
            
            # Create assessment
            assessment = PrivacyImpactAssessment(
                assessment_id=assessment_id,
                data_processing_activity=processing_activity,
                privacy_risks=privacy_risks,
                risk_severity=risk_severity,
                mitigation_measures=mitigation_measures,
                residual_risk=residual_risk,
                assessment_date=datetime.utcnow(),
                assessor_id="system",
                review_date=datetime.utcnow() + timedelta(days=365),
                approved=residual_risk in ["low", "medium"]
            )
            
            # Store assessment
            async with get_db_session() as session:
                pia_record = PrivacyAudit(
                    assessment_id=assessment_id,
                    processing_activity=processing_activity,
                    risk_assessment=json.dumps(asdict(assessment)),
                    status="completed" if assessment.approved else "requires_review",
                    conducted_at=datetime.utcnow(),
                    next_review_date=assessment.review_date
                )
                
                session.add(pia_record)
                await session.commit()
            
            # Log PIA completion
            await self.audit_logger.log_audit_event(
                event_type="privacy_impact_assessment_completed",
                category=AuditCategory.PRIVACY,
                level=AuditLevel.INFO if assessment.approved else AuditLevel.WARNING,
                message=f"Privacy Impact Assessment completed: {assessment_id}",
                details={
                    "assessment_id": assessment_id,
                    "processing_activity": processing_activity,
                    "risk_severity": risk_severity,
                    "residual_risk": residual_risk,
                    "approved": assessment.approved,
                    "risks_identified": len(privacy_risks)
                }
            )
            
            return assessment
            
        except Exception as e:
            self.logger.error(f"Error conducting privacy impact assessment: {str(e)}")
            raise HTTPException(status_code=500, detail="Failed to conduct privacy impact assessment")
    
    async def apply_data_minimization(
        self,
        user_id: int,
        data_type: str,
        minimization_level: DataMinimization
    ) -> Dict[str, Any]:
        """Apply data minimization principles to user data"""
        try:
            # Get current data inventory
            data_inventory = await self._get_user_data_inventory(user_id, data_type)
            
            minimization_results = {
                "user_id": user_id,
                "data_type": data_type,
                "minimization_level": minimization_level.value,
                "original_records": len(data_inventory),
                "processed_records": 0,
                "deleted_records": 0,
                "anonymized_records": 0,
                "storage_reduced_mb": 0
            }
            
            for item in data_inventory:
                try:
                    if minimization_level == DataMinimization.COLLECT_MINIMAL:
                        # Remove unnecessary data fields
                        result = await self._remove_unnecessary_fields(item)
                    elif minimization_level == DataMinimization.PROCESS_MINIMAL:
                        # Restrict processing to essential purposes only
                        result = await self._restrict_processing_purposes(item)
                    elif minimization_level == DataMinimization.STORE_MINIMAL:
                        # Apply storage minimization
                        result = await self._apply_storage_minimization(item)
                    elif minimization_level == DataMinimization.SHARE_MINIMAL:
                        # Restrict data sharing
                        result = await self._restrict_data_sharing(item)
                    
                    minimization_results["processed_records"] += 1
                    if result["action"] == "deleted":
                        minimization_results["deleted_records"] += 1
                    elif result["action"] == "anonymized":
                        minimization_results["anonymized_records"] += 1
                    
                    minimization_results["storage_reduced_mb"] += result.get("storage_reduced", 0)
                    
                except Exception as e:
                    self.logger.error(f"Error processing data item {item.get('id', 'unknown')}: {str(e)}")
                    continue
            
            # Log data minimization
            await self.audit_logger.log_audit_event(
                event_type="data_minimization_applied",
                category=AuditCategory.PRIVACY,
                level=AuditLevel.INFO,
                message=f"Data minimization applied: {minimization_level.value}",
                details={
                    "user_id": user_id,
                    "data_type": data_type,
                    "minimization_level": minimization_level.value,
                    "records_processed": minimization_results["processed_records"],
                    "storage_reduced_mb": minimization_results["storage_reduced_mb"]
                },
                user_id=user_id
            )
            
            return minimization_results
            
        except Exception as e:
            self.logger.error(f"Error applying data minimization: {str(e)}")
            raise HTTPException(status_code=500, detail="Failed to apply data minimization")
    
    def _load_privacy_templates(self) -> Dict[str, Dict[str, Any]]:
        """Load privacy configuration templates"""
        return {
            "EU_MINIMAL": {
                "template_id": "EU_MINIMAL",
                "data_minimization": DataMinimization.COLLECT_MINIMAL,
                "anonymization_level": AnonymizationLevel.PSEUDONYMIZATION,
                "consent_preferences": {
                    "analytics": False,
                    "marketing": False,
                    "personalization": False,
                    "research": False
                },
                "data_sharing_permissions": {
                    "partners": False,
                    "affiliates": False,
                    "third_parties": False
                },
                "marketing_preferences": {
                    "email": False,
                    "sms": False,
                    "push": False,
                    "targeted_ads": False
                },
                "analytics_participation": False,
                "third_party_sharing": False,
                "cross_border_transfer": False,
                "automated_decision_making": False,
                "profiling_consent": False
            },
            "EU_STANDARD": {
                "template_id": "EU_STANDARD",
                "data_minimization": DataMinimization.PROCESS_MINIMAL,
                "anonymization_level": AnonymizationLevel.PSEUDONYMIZATION,
                "consent_preferences": {
                    "analytics": True,
                    "marketing": False,
                    "personalization": True,
                    "research": False
                },
                "data_sharing_permissions": {
                    "partners": False,
                    "affiliates": False,
                    "third_parties": False
                },
                "marketing_preferences": {
                    "email": False,
                    "sms": False,
                    "push": True,
                    "targeted_ads": False
                },
                "analytics_participation": True,
                "third_party_sharing": False,
                "cross_border_transfer": False,
                "automated_decision_making": True,
                "profiling_consent": True
            }
        }


# Export for use in other modules
__all__ = ["PrivacyControlsManager", "PrivacyLevel", "DataMinimization", "AnonymizationLevel", "AccessRight"]
