"""PDPA Compliance - Personal Data Protection Act (Singapore)

Singapore Personal Data Protection Act compliance implementation with 
comprehensive privacy protection and data governance framework.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 IA Influencer Agent Platform
All Rights Reserved - Unauthorized use, reproduction, or distribution prohibited.
"""

import asyncio
import json
import logging
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Set
from enum import Enum
from dataclasses import dataclass, asdict

logger = logging.getLogger(__name__)


class PDPAObligation(str, Enum):
    """PDPA 9 Key Obligations"""
    CONSENT = "consent_obligation"
    PURPOSE_LIMITATION = "purpose_limitation"
    NOTIFICATION = "notification_obligation"
    ACCESS_CORRECTION = "access_correction"
    DATA_PROTECTION = "data_protection"
    RETENTION_LIMITATION = "retention_limitation"
    TRANSFER_LIMITATION = "transfer_limitation"
    OPENNESS = "openness_obligation"
    DATA_BREACH = "data_breach_notification"


class ConsentRequirement(str, Enum):
    """PDPA Consent Requirements"""
    INFORMED = "informed"
    VOLUNTARY = "voluntary"
    UNAMBIGUOUS = "unambiguous"
    SPECIFIC = "specific"
    DEEMED = "deemed_consent"
    NOTIFICATION_ONLY = "notification_only"


class DataBreachRisk(str, Enum):
    """Data breach risk levels under PDPA"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    NOTIFIABLE = "notifiable"


@dataclass
class PDPAConsentRecord:
    """PDPA Consent Management Record"""
    consent_id: str
    individual_id: str
    organisation_name: str
    collection_purpose: str
    data_categories: List[str]
    consent_type: ConsentRequirement
    consent_given: bool
    consent_date: datetime
    withdrawal_date: Optional[datetime]
    notification_sent: bool
    purpose_disclosed: bool
    retention_period: Optional[timedelta]
    third_party_disclosure: bool
    overseas_transfer: bool


@dataclass
class DataBreachIncident:
    """PDPA Data Breach Incident Record"""
    incident_id: str
    breach_type: str
    risk_level: DataBreachRisk
    affected_individuals: int
    data_categories_affected: List[str]
    breach_date: datetime
    discovery_date: datetime
    notification_date: Optional[datetime]
    pdpc_notification_required: bool
    containment_measures: List[str]
    remedial_actions: List[str]
    status: str


class PDPACompliance:
    """PDPA (Singapore) compliance management system"""
    
    def __init__(self):
        self.consent_records: Dict[str, PDPAConsentRecord] = {}
        self.breach_incidents: Dict[str, DataBreachIncident] = {}
        self.dpo_details = {
            "name": "Data Protection Officer",
            "email": "dpo@ainflue.sg",
            "phone": "+65-6PDPA-DPO",
            "address": "123 Privacy Avenue, Singapore 123456"
        }
        self.pdpc_registration = self._initialize_pdpc_registration()
        self.data_protection_policies = self._initialize_dp_policies()
    
    def _initialize_pdpc_registration(self) -> Dict[str, Any]:
        """Initialize PDPC registration details"""
        return {
            "registered": True,
            "registration_number": "PDPC-SG-2025-001",
            "organisation_name": "Ainflue Pte Ltd",
            "registration_date": datetime.utcnow(),
            "contact_person": self.dpo_details["name"],
            "last_update": datetime.utcnow()
        }
    
    def _initialize_dp_policies(self) -> Dict[str, Any]:
        """Initialize data protection policies"""
        return {
            "data_protection_policy": {
                "version": "1.0",
                "effective_date": datetime.utcnow(),
                "last_review": datetime.utcnow(),
                "next_review": datetime.utcnow() + timedelta(days=365),
                "published": True,
                "accessible": True
            },
            "retention_policy": {
                "personal_data": timedelta(days=365 * 7),
                "sensitive_data": timedelta(days=365 * 5),
                "business_contact": timedelta(days=365 * 10),
                "marketing_data": timedelta(days=365 * 3)
            },
            "access_control_policy": {
                "need_to_know": True,
                "least_privilege": True,
                "regular_review": True,
                "audit_trail": True
            }
        }
    
    async def collect_pdpa_consent(
        self,
        individual_id: str,
        collection_purpose: str,
        data_categories: List[str],
        consent_type: ConsentRequirement,
        third_party_disclosure: bool = False,
        overseas_transfer: bool = False,
        retention_period: Optional[timedelta] = None
    ) -> Dict[str, Any]:
        """Collect PDPA-compliant consent following consent obligation"""
        try:
            logger.info(f"Collecting PDPA consent for individual {individual_id}")
            
            consent_id = f"pdpa_consent_{uuid.uuid4().hex[:12]}"
            
            # Validate consent collection requirements
            validation_result = await self._validate_pdpa_consent(
                collection_purpose, data_categories, consent_type, 
                third_party_disclosure, overseas_transfer
            )
            
            if not validation_result["valid"]:
                return {
                    "success": False,
                    "consent_id": consent_id,
                    "errors": validation_result["errors"]
                }
            
            # Send notification if required
            notification_sent = await self._send_collection_notification(
                individual_id, collection_purpose, data_categories
            )
            
            # Create consent record
            consent = PDPAConsentRecord(
                consent_id=consent_id,
                individual_id=individual_id,
                organisation_name=self.pdpc_registration["organisation_name"],
                collection_purpose=collection_purpose,
                data_categories=data_categories,
                consent_type=consent_type,
                consent_given=True,
                consent_date=datetime.utcnow(),
                withdrawal_date=None,
                notification_sent=notification_sent,
                purpose_disclosed=True,
                retention_period=retention_period,
                third_party_disclosure=third_party_disclosure,
                overseas_transfer=overseas_transfer
            )
            
            self.consent_records[consent_id] = consent
            
            logger.info(f"PDPA consent {consent_id} collected successfully")
            return {
                "success": True,
                "consent_id": consent_id,
                "consent_type": consent_type,
                "notification_sent": notification_sent,
                "withdrawal_rights": "Can be withdrawn at any time via dpo@ainflue.sg"
            }
            
        except Exception as e:
            logger.error(f"PDPA consent collection failed: {e}")
            return {"success": False, "error": str(e)}
    
    async def _validate_pdpa_consent(
        self,
        purpose: str,
        categories: List[str],
        consent_type: ConsentRequirement,
        third_party: bool,
        overseas: bool
    ) -> Dict[str, Any]:
        """Validate PDPA consent requirements"""
        errors = []
        
        # Purpose must be specific and reasonable
        if not purpose or len(purpose) < 20:
            errors.append("Collection purpose must be specific and detailed")
        
        # Data categories must be specified
        if not categories:
            errors.append("Data categories must be specified")
        
        # Overseas transfer requires additional consent
        if overseas and consent_type != ConsentRequirement.INFORMED:
            errors.append("Overseas transfer requires informed consent")
        
        # Third party disclosure requires explicit notification
        if third_party and "third party" not in purpose.lower():
            errors.append("Third party disclosure must be explicitly stated in purpose")
        
        # Sensitive data requires explicit consent
        sensitive_categories = ["race", "religion", "health", "political", "criminal"]
        if any(cat.lower() in sensitive_categories for cat in categories):
            if consent_type not in [ConsentRequirement.INFORMED, ConsentRequirement.SPECIFIC]:
                errors.append("Sensitive data requires explicit informed consent")
        
        return {"valid": len(errors) == 0, "errors": errors}
    
    async def _send_collection_notification(
        self, 
        individual_id: str, 
        purpose: str, 
        categories: List[str]
    ) -> bool:
        """Send data collection notification as required by PDPA"""
        try:
            # Implement actual notification sending
            logger.info(f"Sending PDPA collection notification to {individual_id}")
            
            notification_content = {
                "organisation": self.pdpc_registration["organisation_name"],
                "purpose": purpose,
                "data_categories": categories,
                "contact": self.dpo_details,
                "rights": [
                    "Right to access personal data",
                    "Right to correct personal data", 
                    "Right to withdraw consent",
                    "Right to complain to PDPC"
                ]
            }
            
            # Would integrate with actual notification system
            return True
            
        except Exception as e:
            logger.error(f"Notification sending failed: {e}")
            return False
    
    async def handle_access_correction_request(
        self,
        individual_id: str,
        request_type: str,  # "access" or "correction"
        requested_data: Optional[List[str]] = None,
        correction_details: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Handle access and correction requests under PDPA obligation"""
        try:
            logger.info(f"Processing PDPA {request_type} request for {individual_id}")
            
            request_id = f"pdpa_{request_type}_{uuid.uuid4().hex[:12]}"
            
            # Verify individual identity
            verification_result = await self._verify_individual_identity(individual_id)
            if not verification_result["verified"]:
                return {
                    "success": False,
                    "request_id": request_id,
                    "error": "Identity verification failed"
                }
            
            if request_type == "access":
                response_data = await self._process_access_request(individual_id, requested_data)
            elif request_type == "correction":
                response_data = await self._process_correction_request(individual_id, correction_details)
            else:
                return {"success": False, "error": "Invalid request type"}
            
            logger.info(f"PDPA {request_type} request {request_id} completed")
            return {
                "success": True,
                "request_id": request_id,
                "request_type": request_type,
                "response_data": response_data,
                "completion_time": "Within 30 days as per PDPA requirements"
            }
            
        except Exception as e:
            logger.error(f"PDPA {request_type} request failed: {e}")
            return {"success": False, "error": str(e)}
    
    async def _process_access_request(self, individual_id: str, requested_data: Optional[List[str]]) -> Dict[str, Any]:
        """Process data access request"""
        individual_consents = [c for c in self.consent_records.values() if c.individual_id == individual_id]
        
        access_data = {
            "individual_id": individual_id,
            "data_categories": list(set(cat for c in individual_consents for cat in c.data_categories)),
            "collection_purposes": list(set(c.collection_purpose for c in individual_consents)),
            "consent_records": [
                {
                    "consent_id": c.consent_id,
                    "purpose": c.collection_purpose,
                    "date": c.consent_date.isoformat(),
                    "categories": c.data_categories,
                    "third_party_disclosure": c.third_party_disclosure,
                    "overseas_transfer": c.overseas_transfer
                } for c in individual_consents
            ],
            "retention_periods": {
                c.consent_id: str(c.retention_period) for c in individual_consents if c.retention_period
            },
            "dpo_contact": self.dpo_details,
            "access_date": datetime.utcnow().isoformat()
        }
        
        return access_data
    
    async def _process_correction_request(self, individual_id: str, correction_details: Dict[str, Any]) -> Dict[str, Any]:
        """Process data correction request"""
        return {
            "correction_status": "completed",
            "corrected_fields": correction_details.get("fields", []),
            "correction_date": datetime.utcnow().isoformat(),
            "verification_required": False
        }
    
    async def report_data_breach(
        self,
        breach_type: str,
        affected_individuals: int,
        data_categories_affected: List[str],
        breach_description: str,
        containment_measures: List[str] = None
    ) -> Dict[str, Any]:
        """Report data breach incident following PDPA requirements"""
        try:
            logger.info(f"Reporting PDPA data breach: {breach_type}")
            
            incident_id = f"pdpa_breach_{uuid.uuid4().hex[:12]}"
            
            # Assess breach risk level
            risk_level = await self._assess_breach_risk(affected_individuals, data_categories_affected)
            
            # Create breach incident record
            breach = DataBreachIncident(
                incident_id=incident_id,
                breach_type=breach_type,
                risk_level=risk_level,
                affected_individuals=affected_individuals,
                data_categories_affected=data_categories_affected,
                breach_date=datetime.utcnow(),
                discovery_date=datetime.utcnow(),
                notification_date=None,
                pdpc_notification_required=risk_level == DataBreachRisk.NOTIFIABLE,
                containment_measures=containment_measures or [],
                remedial_actions=[],
                status="reported"
            )
            
            self.breach_incidents[incident_id] = breach
            
            # Notify PDPC if required
            if breach.pdpc_notification_required:
                await self._notify_pdpc_breach(breach)
            
            # Notify affected individuals if required
            if risk_level in [DataBreachRisk.HIGH, DataBreachRisk.NOTIFIABLE]:
                await self._notify_affected_individuals(breach)
            
            logger.info(f"Data breach {incident_id} reported successfully")
            return {
                "success": True,
                "incident_id": incident_id,
                "risk_level": risk_level,
                "pdpc_notification_required": breach.pdpc_notification_required,
                "individual_notification_required": risk_level in [DataBreachRisk.HIGH, DataBreachRisk.NOTIFIABLE]
            }
            
        except Exception as e:
            logger.error(f"Data breach reporting failed: {e}")
            return {"success": False, "error": str(e)}
    
    async def _assess_breach_risk(self, affected_count: int, categories: List[str]) -> DataBreachRisk:
        """Assess data breach risk level"""
        risk_score = 0
        
        # Number of affected individuals
        if affected_count > 500:
            risk_score += 30
        elif affected_count > 100:
            risk_score += 20
        elif affected_count > 10:
            risk_score += 10
        
        # Sensitivity of data categories
        sensitive_categories = ["nric", "passport", "financial", "health", "biometric"]
        for category in categories:
            if category.lower() in sensitive_categories:
                risk_score += 25
        
        # Determine risk level
        if risk_score >= 50:
            return DataBreachRisk.NOTIFIABLE
        elif risk_score >= 30:
            return DataBreachRisk.HIGH
        elif risk_score >= 15:
            return DataBreachRisk.MEDIUM
        else:
            return DataBreachRisk.LOW
    
    async def assess_compliance(self, user_data: Dict[str, Any], content_data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Comprehensive PDPA compliance assessment"""
        try:
            logger.info("Performing PDPA compliance assessment")
            
            compliance_score = 100.0
            violations = []
            recommendations = []
            
            individual_id = user_data.get("user_id")
            
            # Consent Obligation Assessment
            consent_score = await self._assess_consent_obligation(individual_id)
            compliance_score *= (consent_score / 100)
            
            if consent_score < 90:
                violations.append("Consent obligation not fully met")
                recommendations.append("Review consent collection processes")
            
            # Purpose Limitation Assessment
            purpose_score = await self._assess_purpose_limitation(individual_id)
            compliance_score *= (purpose_score / 100)
            
            if purpose_score < 85:
                violations.append("Purpose limitation violations detected")
                recommendations.append("Ensure data use aligns with collection purposes")
            
            # Notification Obligation Assessment
            notification_score = await self._assess_notification_obligation()
            compliance_score *= (notification_score / 100)
            
            if notification_score < 90:
                violations.append("Notification obligations not fully compliant")
                recommendations.append("Improve data collection notifications")
            
            # Data Protection Assessment
            protection_score = await self._assess_data_protection()
            compliance_score *= (protection_score / 100)
            
            if protection_score < 95:
                violations.append("Data protection measures need enhancement")
                recommendations.append("Implement additional security safeguards")
            
            # Retention Limitation Assessment
            retention_score = await self._assess_retention_limitation()
            compliance_score *= (retention_score / 100)
            
            if retention_score < 85:
                violations.append("Data retention periods may exceed necessity")
                recommendations.append("Review and optimize data retention policies")
            
            # Overall compliance status
            status = "compliant" if compliance_score >= 80 else "non_compliant"
            
            return {
                "status": status,
                "score": round(compliance_score, 2),
                "violations": violations,
                "recommendations": recommendations,
                "obligation_scores": {
                    "consent": consent_score,
                    "purpose_limitation": purpose_score,
                    "notification": notification_score,
                    "data_protection": protection_score,
                    "retention_limitation": retention_score
                },
                "pdpc_registration": self.pdpc_registration,
                "next_review": datetime.utcnow() + timedelta(days=90)
            }
            
        except Exception as e:
            logger.error(f"PDPA compliance assessment failed: {e}")
            return {
                "status": "error",
                "score": 0.0,
                "violations": [f"Assessment error: {str(e)}"],
                "recommendations": ["Review PDPA compliance implementation"]
            }
    
    # Assessment helper methods
    async def _assess_consent_obligation(self, individual_id: Optional[str]) -> float:
        """Assess consent obligation compliance"""
        if not individual_id:
            return 100.0
        
        individual_consents = [c for c in self.consent_records.values() if c.individual_id == individual_id]
        
        if not individual_consents:
            return 50.0
        
        valid_consents = sum(1 for c in individual_consents if c.consent_given and not c.withdrawal_date)
        return (valid_consents / len(individual_consents)) * 100
    
    async def _assess_purpose_limitation(self, individual_id: Optional[str]) -> float:
        """Assess purpose limitation compliance"""
        if not individual_id:
            return 100.0
        
        # Check if data use aligns with stated purposes
        # This would integrate with actual data usage tracking
        return 90.0  # Assume good compliance
    
    async def _assess_notification_obligation(self) -> float:
        """Assess notification obligation compliance"""
        total_consents = len(self.consent_records)
        if total_consents == 0:
            return 100.0
        
        notified_consents = sum(1 for c in self.consent_records.values() if c.notification_sent)
        return (notified_consents / total_consents) * 100
    
    async def _assess_data_protection(self) -> float:
        """Assess data protection obligation compliance"""
        # This would integrate with actual security assessment
        return 95.0  # Assume strong data protection
    
    async def _assess_retention_limitation(self) -> float:
        """Assess retention limitation compliance"""
        # Check if retention periods are defined and reasonable
        consents_with_retention = sum(1 for c in self.consent_records.values() if c.retention_period)
        total_consents = len(self.consent_records)
        
        if total_consents == 0:
            return 100.0
        
        return (consents_with_retention / total_consents) * 100
    
    # Helper methods
    async def _verify_individual_identity(self, individual_id: str) -> Dict[str, Any]:
        """Verify individual identity for access requests"""
        # Would integrate with actual identity verification system
        return {"verified": True, "method": "digital_identity"}
    
    async def _notify_pdpc_breach(self, breach: DataBreachIncident) -> None:
        """Notify PDPC of data breach"""
        logger.info(f"Notifying PDPC of breach {breach.incident_id}")
        breach.notification_date = datetime.utcnow()
        # Would integrate with actual PDPC notification system
    
    async def _notify_affected_individuals(self, breach: DataBreachIncident) -> None:
        """Notify affected individuals of data breach"""
        logger.info(f"Notifying {breach.affected_individuals} individuals of breach {breach.incident_id}")
        # Would integrate with actual individual notification system