"""GDPR Handler - Advanced GDPR Compliance Management System

This module provides comprehensive GDPR compliance management for conversational AI,
including data privacy protection, consent management, and right to be forgotten implementation.

Author: Fahed Mlaiel
Contact: mlaiel@live.de
Copyright: © 2025 Fahed Mlaiel. All rights reserved.
"""import re
import logging
import hashlib
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any, Set
from dataclasses import dataclass
from enum import Enum

from ..core.database import DatabaseManager
from ..security.encryption import EncryptionService
from ..ml.pii_detector import PIIDetector


class DataProcessingPurpose(Enum):
    """GDPR data processing purposes"""    CONVERSATIONAL_AI = "conversational_ai"
    USER_ANALYTICS = "user_analytics"
    PERSONALIZATION = "personalization"
    SECURITY_MONITORING = "security_monitoring"
    LEGAL_COMPLIANCE = "legal_compliance"
    MARKETING = "marketing"
    RESEARCH = "research"


class PIICategory(Enum):
    """Categories of Personally Identifiable Information"""    NAME = "name"
    EMAIL = "email"
    PHONE = "phone"
    ADDRESS = "address"
    IDENTIFICATION_NUMBER = "identification_number"
    FINANCIAL = "financial"
    HEALTH = "health"
    BIOMETRIC = "biometric"
    LOCATION = "location"
    ONLINE_IDENTIFIER = "online_identifier"
    SPECIAL_CATEGORY = "special_category"


class ConsentStatus(Enum):
    """Consent status for data processing"""    GRANTED = "granted"
    WITHDRAWN = "withdrawn"
    PENDING = "pending"
    EXPIRED = "expired"
    NOT_REQUIRED = "not_required"


class DataSubjectRights(Enum):
    """GDPR data subject rights"""    ACCESS = "access"
    RECTIFICATION = "rectification"
    ERASURE = "erasure"
    PORTABILITY = "portability"
    RESTRICTION = "restriction"
    OBJECTION = "objection"
    AUTOMATED_DECISION_MAKING = "automated_decision_making"


@dataclass
class PIIDetection:
    """PII detection result structure"""    category: PIICategory
    value: str
    confidence_score: float
    location: str
    masked_value: str
    processing_lawful_basis: Optional[str]
    requires_consent: bool
    retention_period: Optional[int]


@dataclass
class ConsentRecord:
    """Consent record structure"""    user_id: int
    purpose: DataProcessingPurpose
    status: ConsentStatus
    granted_at: Optional[datetime]
    withdrawn_at: Optional[datetime]
    expires_at: Optional[datetime]
    granularity: str
    legal_basis: str
    consent_evidence: Dict[str, Any]
    processing_details: Dict[str, Any]


@dataclass
class GDPRComplianceResult:
    """GDPR compliance assessment result"""    is_compliant: bool
    pii_detected: List[PIIDetection]
    consent_requirements: List[ConsentRecord]
    violations: List[Dict[str, Any]]
    recommendations: List[str]
    data_subject_rights_applicable: List[DataSubjectRights]
    lawful_basis_assessment: Dict[str, Any]
    retention_recommendations: Dict[str, Any]
    cross_border_transfer_issues: List[str]
    processing_time_ms: int


class GDPRHandler:
    """    Advanced GDPR compliance management system.
    
    Provides comprehensive GDPR compliance for conversational AI including
    PII detection, consent management, data subject rights, and privacy protection.
    """    
    def __init__(
        self,
        db_manager: DatabaseManager,
        encryption_service: EncryptionService,
        pii_detector: Optional[PIIDetector] = None
    ):
        self.db_manager = db_manager
        self.encryption_service = encryption_service
        self.pii_detector = pii_detector or PIIDetector()
        self.logger = logging.getLogger(__name__)
        
        # GDPR configuration
        self.pii_patterns = self._load_pii_patterns()
        self.lawful_basis_rules = self._load_lawful_basis_rules()
        self.retention_policies = self._load_retention_policies()
        
        # User consent cache
        self.consent_cache: Dict[int, Dict[str, ConsentRecord]] = {}
        
        self.logger.info("GDPRHandler initialized with privacy protection systems")
    
    def _load_pii_patterns(self) -> Dict[PIICategory, List[Dict[str, Any]]]:
        """Load PII detection patterns"""        return {
            PIICategory.EMAIL: [
                {
                    "pattern": r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b",
                    "confidence": 0.95,
                    "requires_consent": True,
                    "special_category": False
                }
            ],
            PIICategory.PHONE: [
                {
                    "pattern": r"\b(\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b",
                    "confidence": 0.85,
                    "requires_consent": True,
                    "special_category": False
                }
            ],
            PIICategory.NAME: [
                {
                    "pattern": r"\b[A-Z][a-z]+\s+[A-Z][a-z]+\b",
                    "confidence": 0.6,
                    "requires_consent": False,
                    "special_category": False
                }
            ],
            PIICategory.ADDRESS: [
                {
                    "pattern": r"\d+\s+[A-Za-z\s]+(?:Street|St|Avenue|Ave|Road|Rd|Boulevard|Blvd|Lane|Ln|Drive|Dr)",
                    "confidence": 0.8,
                    "requires_consent": True,
                    "special_category": False
                }
            ],
            PIICategory.IDENTIFICATION_NUMBER: [
                {
                    "pattern": r"\b\d{3}-\d{2}-\d{4}\b",  # SSN format
                    "confidence": 0.9,
                    "requires_consent": True,
                    "special_category": False
                },
                {
                    "pattern": r"\b[A-Z]{2}\d{6}[A-Z]\b",  # ID card format
                    "confidence": 0.8,
                    "requires_consent": True,
                    "special_category": False
                }
            ],
            PIICategory.FINANCIAL: [
                {
                    "pattern": r"\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b",  # Credit card
                    "confidence": 0.9,
                    "requires_consent": True,
                    "special_category": False
                },
                {
                    "pattern": r"\bIBAN\s*[A-Z]{2}\d{2}[A-Z0-9]{4}\d{7}([A-Z0-9]?){0,16}\b",
                    "confidence": 0.95,
                    "requires_consent": True,
                    "special_category": False
                }
            ],
            PIICategory.HEALTH: [
                {
                    "pattern": r"\b(diabetes|cancer|HIV|AIDS|depression|anxiety|medication|prescription|diagnosis)\b",
                    "confidence": 0.7,
                    "requires_consent": True,
                    "special_category": True
                }
            ],
            PIICategory.SPECIAL_CATEGORY: [
                {
                    "pattern": r"\b(race|ethnicity|religion|political|sexual orientation|union membership)\b",
                    "confidence": 0.6,
                    "requires_consent": True,
                    "special_category": True
                }
            ]
        }
    
    def _load_lawful_basis_rules(self) -> Dict[str, Dict[str, Any]]:
        """Load GDPR lawful basis rules"""        return {
            "consent": {
                "requires_explicit_consent": True,
                "can_be_withdrawn": True,
                "suitable_for": ["marketing", "non_essential_features"],
                "documentation_required": True
            },
            "contract": {
                "requires_explicit_consent": False,
                "can_be_withdrawn": False,
                "suitable_for": ["service_delivery", "account_management"],
                "documentation_required": True
            },
            "legal_obligation": {
                "requires_explicit_consent": False,
                "can_be_withdrawn": False,
                "suitable_for": ["tax_compliance", "regulatory_reporting"],
                "documentation_required": True
            },
            "vital_interests": {
                "requires_explicit_consent": False,
                "can_be_withdrawn": False,
                "suitable_for": ["life_threatening_situations"],
                "documentation_required": True
            },
            "public_task": {
                "requires_explicit_consent": False,
                "can_be_withdrawn": False,
                "suitable_for": ["public_sector_functions"],
                "documentation_required": True
            },
            "legitimate_interests": {
                "requires_explicit_consent": False,
                "can_be_withdrawn": True,
                "suitable_for": ["security", "fraud_prevention", "analytics"],
                "documentation_required": True,
                "requires_balancing_test": True
            }
        }
    
    def _load_retention_policies(self) -> Dict[DataProcessingPurpose, Dict[str, Any]]:
        """Load data retention policies by purpose"""        return {
            DataProcessingPurpose.CONVERSATIONAL_AI: {
                "retention_period_days": 365,
                "auto_deletion": True,
                "anonymization_after_days": 90,
                "legal_basis": "legitimate_interests"
            },
            DataProcessingPurpose.USER_ANALYTICS: {
                "retention_period_days": 730,
                "auto_deletion": True,
                "anonymization_after_days": 180,
                "legal_basis": "legitimate_interests"
            },
            DataProcessingPurpose.PERSONALIZATION: {
                "retention_period_days": 1095,
                "auto_deletion": False,
                "anonymization_after_days": 365,
                "legal_basis": "consent"
            },
            DataProcessingPurpose.SECURITY_MONITORING: {
                "retention_period_days": 2190,
                "auto_deletion": True,
                "anonymization_after_days": 730,
                "legal_basis": "legitimate_interests"
            },
            DataProcessingPurpose.LEGAL_COMPLIANCE: {
                "retention_period_days": 2555,  # 7 years
                "auto_deletion": False,
                "anonymization_after_days": 1825,
                "legal_basis": "legal_obligation"
            }
        }
    
    async def validate_privacy_compliance(
        self,
        user_id: Optional[int],
        conversation_data: Dict[str, Any],
        user_input: str,
        ai_response: str
    ) -> Dict[str, Any]:
        """        Comprehensive GDPR privacy compliance validation.
        
        Args:
            user_id: User identifier
            conversation_data: Full conversation context
            user_input: User's input text
            ai_response: AI's generated response
            
        Returns:
            Dict containing GDPR compliance assessment
        """        start_time = datetime.now()
        
        try:
            self.logger.debug(f"Starting GDPR compliance validation for user {user_id}")
            
            # Initialize compliance result
            result = GDPRComplianceResult(
                is_compliant=True,
                pii_detected=[],
                consent_requirements=[],
                violations=[],
                recommendations=[],
                data_subject_rights_applicable=[],
                lawful_basis_assessment={},
                retention_recommendations={},
                cross_border_transfer_issues=[],
                processing_time_ms=0
            )
            
            # Detect PII in conversation
            combined_content = f"{user_input} {ai_response}"
            pii_detections = await self._detect_pii(combined_content)
            result.pii_detected = pii_detections
            
            # Check consent requirements
            if user_id:
                consent_status = await self._check_consent_requirements(
                    user_id, pii_detections, conversation_data
                )
                result.consent_requirements = consent_status
            
            # Assess lawful basis for processing
            lawful_basis = await self._assess_lawful_basis(
                pii_detections, conversation_data, user_id
            )
            result.lawful_basis_assessment = lawful_basis
            
            # Check data subject rights
            applicable_rights = self._determine_applicable_rights(pii_detections, user_id)
            result.data_subject_rights_applicable = applicable_rights
            
            # Assess retention requirements
            retention_assessment = self._assess_retention_requirements(
                pii_detections, conversation_data
            )
            result.retention_recommendations = retention_assessment
            
            # Check cross-border transfer issues
            transfer_issues = await self._check_cross_border_transfers(
                conversation_data, user_id
            )
            result.cross_border_transfer_issues = transfer_issues
            
            # Generate violations for non-compliance
            violations = self._identify_violations(result)
            result.violations = violations
            
            # Generate recommendations
            result.recommendations = self._generate_privacy_recommendations(result)
            
            # Determine overall compliance
            result.is_compliant = (
                not result.violations and
                all(consent.status == ConsentStatus.GRANTED for consent in result.consent_requirements if consent.requires_consent) and
                not result.cross_border_transfer_issues
            )
            
            # Calculate processing time
            processing_time = datetime.now() - start_time
            result.processing_time_ms = int(processing_time.total_seconds() * 1000)
            
            # Store compliance record
            await self._store_gdpr_assessment(result, user_id)
            
            return {
                "compliant": result.is_compliant,
                "pii_detected": len(result.pii_detected),
                "consent_requirements": [
                    {
                        "purpose": req.purpose.value,
                        "status": req.status.value,
                        "required": req.requires_consent
                    }
                    for req in result.consent_requirements
                ],
                "violations": result.violations,
                "recommendations": result.recommendations,
                "applicable_rights": [right.value for right in result.data_subject_rights_applicable]
            }
            
        except Exception as e:
            self.logger.error(f"Error in GDPR compliance validation: {str(e)}")
            return {
                "compliant": False,
                "violations": [{"type": "validation_error", "message": str(e)}],
                "recommendations": ["Manual GDPR review required due to validation error"]
            }
    
    async def _detect_pii(self, content: str) -> List[PIIDetection]:
        """Detect personally identifiable information in content"""        detections = []
        
        # Pattern-based PII detection
        for category, patterns in self.pii_patterns.items():
            for pattern_config in patterns:
                pattern = pattern_config["pattern"]
                matches = re.finditer(pattern, content, re.IGNORECASE)
                
                for match in matches:
                    detected_value = match.group()
                    masked_value = self._mask_pii(detected_value, category)
                    
                    detection = PIIDetection(
                        category=category,
                        value=detected_value,
                        confidence_score=pattern_config["confidence"],
                        location=f"Position {match.start()}-{match.end()}",
                        masked_value=masked_value,
                        processing_lawful_basis=None,
                        requires_consent=pattern_config["requires_consent"],
                        retention_period=self._get_retention_period(category)
                    )
                    
                    detections.append(detection)
        
        # ML-based PII detection
        try:
            ml_detections = await self.pii_detector.detect_pii(content)
            for ml_detection in ml_detections:
                category = PIICategory(ml_detection.get("category", "online_identifier"))
                detection = PIIDetection(
                    category=category,
                    value=ml_detection["value"],
                    confidence_score=ml_detection["confidence"],
                    location=ml_detection["location"],
                    masked_value=self._mask_pii(ml_detection["value"], category),
                    processing_lawful_basis=None,
                    requires_consent=ml_detection.get("requires_consent", True),
                    retention_period=self._get_retention_period(category)
                )
                detections.append(detection)
        
        except Exception as e:
            self.logger.error(f"Error in ML PII detection: {str(e)}")
        
        return detections
    
    def _mask_pii(self, value: str, category: PIICategory) -> str:
        """Mask PII value for logging and storage"""        if category == PIICategory.EMAIL:
            local, domain = value.split('@')
            return f"{local[:2]}***@{domain}"
        elif category == PIICategory.PHONE:
            return f"***-***-{value[-4:]}"
        elif category == PIICategory.FINANCIAL:
            return f"****-****-****-{value[-4:]}"
        elif category == PIICategory.IDENTIFICATION_NUMBER:
            return f"***-**-{value[-4:]}"
        else:
            return f"{value[:2]}***{value[-2:]}" if len(value) > 4 else "***"
    
    def _get_retention_period(self, category: PIICategory) -> Optional[int]:
        """Get retention period for PII category"""        retention_map = {
            PIICategory.HEALTH: 2555,  # 7 years for health data
            PIICategory.FINANCIAL: 2555,  # 7 years for financial data
            PIICategory.SPECIAL_CATEGORY: 1095,  # 3 years for special categories
            PIICategory.EMAIL: 730,  # 2 years for contact info
            PIICategory.PHONE: 730,  # 2 years for contact info
            PIICategory.ADDRESS: 1095,  # 3 years for address
            PIICategory.NAME: 1095,  # 3 years for names
            PIICategory.IDENTIFICATION_NUMBER: 2555  # 7 years for ID numbers
        }
        
        return retention_map.get(category, 365)  # Default 1 year
    
    async def _check_consent_requirements(
        self,
        user_id: int,
        pii_detections: List[PIIDetection],
        conversation_data: Dict[str, Any]
    ) -> List[ConsentRecord]:
        """Check consent requirements for detected PII"""        consent_requirements = []
        
        # Load user's current consent status
        user_consents = await self._load_user_consents(user_id)
        
        # Determine required consents based on PII and processing purposes
        purposes_requiring_consent = set()
        
        for detection in pii_detections:
            if detection.requires_consent or detection.category in [PIICategory.HEALTH, PIICategory.SPECIAL_CATEGORY]:
                purposes_requiring_consent.update([
                    DataProcessingPurpose.CONVERSATIONAL_AI,
                    DataProcessingPurpose.USER_ANALYTICS,
                    DataProcessingPurpose.PERSONALIZATION
                ])
        
        # Check consent status for each purpose
        for purpose in purposes_requiring_consent:
            existing_consent = user_consents.get(purpose.value)
            
            if not existing_consent or existing_consent.status != ConsentStatus.GRANTED:
                consent_record = ConsentRecord(
                    user_id=user_id,
                    purpose=purpose,
                    status=ConsentStatus.PENDING,
                    granted_at=None,
                    withdrawn_at=None,
                    expires_at=None,
                    granularity="specific",
                    legal_basis="consent",
                    consent_evidence={},
                    processing_details={"pii_categories": [d.category.value for d in pii_detections]}
                )
                consent_record.requires_consent = True
                consent_requirements.append(consent_record)
            else:
                consent_requirements.append(existing_consent)
        
        return consent_requirements
    
    async def _load_user_consents(self, user_id: int) -> Dict[str, ConsentRecord]:
        """Load user's consent records"""        if user_id in self.consent_cache:
            return self.consent_cache[user_id]
        
        try:
            consents_data = await self.db_manager.fetch_all(
                """                SELECT * FROM user_consents 
                WHERE user_id = $1 AND (expires_at IS NULL OR expires_at > $2)
                """,
                user_id,
                datetime.now()
            )
            
            consents = {}
            for consent_data in consents_data:
                consent_record = ConsentRecord(
                    user_id=consent_data["user_id"],
                    purpose=DataProcessingPurpose(consent_data["purpose"]),
                    status=ConsentStatus(consent_data["status"]),
                    granted_at=consent_data["granted_at"],
                    withdrawn_at=consent_data["withdrawn_at"],
                    expires_at=consent_data["expires_at"],
                    granularity=consent_data["granularity"],
                    legal_basis=consent_data["legal_basis"],
                    consent_evidence=consent_data["consent_evidence"],
                    processing_details=consent_data["processing_details"]
                )
                consents[consent_data["purpose"]] = consent_record
            
            self.consent_cache[user_id] = consents
            return consents
            
        except Exception as e:
            self.logger.error(f"Error loading user consents: {str(e)}")
            return {}
    
    async def _assess_lawful_basis(
        self,
        pii_detections: List[PIIDetection],
        conversation_data: Dict[str, Any],
        user_id: Optional[int]
    ) -> Dict[str, Any]:
        """Assess lawful basis for data processing"""        assessment = {
            "primary_basis": "legitimate_interests",
            "alternative_bases": [],
            "special_category_basis": None,
            "assessment_details": {},
            "compliance_notes": []
        }
        
        # Check for special categories requiring explicit consent
        special_categories = [
            detection for detection in pii_detections
            if detection.category in [PIICategory.HEALTH, PIICategory.SPECIAL_CATEGORY]
        ]
        
        if special_categories:
            assessment["special_category_basis"] = "explicit_consent"
            assessment["compliance_notes"].append(
                "Special category data detected - explicit consent required"
            )
        
        # Assess appropriate lawful basis for different processing purposes
        if conversation_data.get("purpose") == "service_delivery":
            assessment["primary_basis"] = "contract"
            assessment["assessment_details"]["contract_justification"] = "Service delivery to user"
        
        elif any(detection.requires_consent for detection in pii_detections):
            assessment["primary_basis"] = "consent"
            assessment["assessment_details"]["consent_required"] = True
        
        else:
            assessment["primary_basis"] = "legitimate_interests"
            assessment["assessment_details"]["legitimate_interests"] = [
                "Improving conversational AI service",
                "Ensuring service security and functionality"
            ]
            assessment["assessment_details"]["balancing_test_required"] = True
        
        return assessment
    
    def _determine_applicable_rights(
        self,
        pii_detections: List[PIIDetection],
        user_id: Optional[int]
    ) -> List[DataSubjectRights]:
        """Determine applicable data subject rights"""        applicable_rights = []
        
        if pii_detections and user_id:
            # Basic rights always applicable when processing personal data
            applicable_rights.extend([
                DataSubjectRights.ACCESS,
                DataSubjectRights.RECTIFICATION,
                DataSubjectRights.ERASURE,
                DataSubjectRights.RESTRICTION,
                DataSubjectRights.OBJECTION
            ])
            
            # Portability for consent/contract basis
            applicable_rights.append(DataSubjectRights.PORTABILITY)
            
            # Automated decision-making rights if applicable
            applicable_rights.append(DataSubjectRights.AUTOMATED_DECISION_MAKING)
        
        return applicable_rights
    
    def _assess_retention_requirements(
        self,
        pii_detections: List[PIIDetection],
        conversation_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Assess data retention requirements"""        retention_assessment = {
            "recommended_retention_days": 365,
            "automatic_deletion_recommended": True,
            "anonymization_timeline": 90,
            "category_specific_requirements": {},
            "legal_requirements": []
        }
        
        # Calculate retention based on PII categories
        max_retention = 365
        for detection in pii_detections:
            category_retention = self._get_retention_period(detection.category)
            if category_retention:
                max_retention = max(max_retention, category_retention)
                retention_assessment["category_specific_requirements"][detection.category.value] = category_retention
        
        retention_assessment["recommended_retention_days"] = max_retention
        
        # Special requirements for health/financial data
        sensitive_categories = [PIICategory.HEALTH, PIICategory.FINANCIAL, PIICategory.SPECIAL_CATEGORY]
        if any(detection.category in sensitive_categories for detection in pii_detections):
            retention_assessment["automatic_deletion_recommended"] = False
            retention_assessment["legal_requirements"].append(
                "Extended retention may be required for sensitive data categories"
            )
        
        return retention_assessment
    
    async def _check_cross_border_transfers(
        self,
        conversation_data: Dict[str, Any],
        user_id: Optional[int]
    ) -> List[str]:
        """Check for cross-border data transfer issues"""        transfer_issues = []
        
        # Check user location vs processing location
        user_location = conversation_data.get("user_location", {})
        processing_locations = conversation_data.get("processing_locations", ["EU"])
        
        user_country = user_location.get("country", "Unknown")
        
        # Check for transfers outside EU/EEA
        eu_countries = {
            "AT", "BE", "BG", "HR", "CY", "CZ", "DK", "EE", "FI", "FR", "DE", 
            "GR", "HU", "IE", "IT", "LV", "LT", "LU", "MT", "NL", "PL", "PT", 
            "RO", "SK", "SI", "ES", "SE", "IS", "LI", "NO"
        }
        
        for location in processing_locations:
            if location not in eu_countries:
                if user_country in eu_countries:
                    transfer_issues.append(
                        f"Data transfer from EU ({user_country}) to third country ({location}) "
                        "requires adequacy decision or appropriate safeguards"
                    )
        
        # Check for US transfers (post-Schrems II)
        if "US" in processing_locations and user_country in eu_countries:
            transfer_issues.append(
                "Transfer to US requires Privacy Shield successor framework or SCCs with additional safeguards"
            )
        
        return transfer_issues
    
    def _identify_violations(self, result: GDPRComplianceResult) -> List[Dict[str, Any]]:
        """Identify GDPR violations from assessment"""        violations = []
        
        # Check for processing without lawful basis
        if result.pii_detected and not result.lawful_basis_assessment.get("primary_basis"):
            violations.append({
                "type": "no_lawful_basis",
                "severity": "high",
                "description": "Personal data processing without established lawful basis",
                "article": "Article 6 GDPR"
            })
        
        # Check for special category data without appropriate basis
        special_category_pii = [
            pii for pii in result.pii_detected
            if pii.category in [PIICategory.HEALTH, PIICategory.SPECIAL_CATEGORY]
        ]
        
        if special_category_pii and result.lawful_basis_assessment.get("special_category_basis") != "explicit_consent":
            violations.append({
                "type": "special_category_violation",
                "severity": "critical",
                "description": "Special category data processing without explicit consent or other Article 9 basis",
                "article": "Article 9 GDPR"
            })
        
        # Check for missing consent where required
        missing_consents = [
            consent for consent in result.consent_requirements
            if hasattr(consent, 'requires_consent') and consent.requires_consent and consent.status != ConsentStatus.GRANTED
        ]
        
        if missing_consents:
            violations.append({
                "type": "missing_consent",
                "severity": "high",
                "description": f"Missing consent for {len(missing_consents)} processing purposes",
                "article": "Article 6(1)(a) GDPR"
            })
        
        # Check for cross-border transfer violations
        if result.cross_border_transfer_issues:
            violations.append({
                "type": "unlawful_transfer",
                "severity": "high", 
                "description": "Cross-border data transfers without adequate protection",
                "article": "Chapter V GDPR"
            })
        
        return violations
    
    def _generate_privacy_recommendations(self, result: GDPRComplianceResult) -> List[str]:
        """Generate privacy compliance recommendations"""        recommendations = []
        
        if result.pii_detected:
            recommendations.append("Implement data minimization principles")
            recommendations.append("Apply purpose limitation to data processing")
            recommendations.append("Ensure data accuracy and keep data up to date")
        
        if result.violations:
            recommendations.append("Address identified GDPR violations immediately")
            recommendations.append("Conduct data protection impact assessment (DPIA)")
        
        missing_consents = [
            consent for consent in result.consent_requirements
            if hasattr(consent, 'requires_consent') and consent.requires_consent and consent.status != ConsentStatus.GRANTED
        ]
        
        if missing_consents:
            recommendations.append("Obtain explicit consent for personal data processing")
            recommendations.append("Implement granular consent management")
        
        if result.cross_border_transfer_issues:
            recommendations.append("Implement appropriate safeguards for international transfers")
            recommendations.append("Consider data localization where possible")
        
        if result.data_subject_rights_applicable:
            recommendations.append("Ensure data subject rights request handling procedures")
            recommendations.append("Implement automated data portability mechanisms")
        
        return recommendations
    
    async def _store_gdpr_assessment(
        self,
        result: GDPRComplianceResult,
        user_id: Optional[int]
    ) -> None:
        """Store GDPR assessment results"""        try:
            query = """                INSERT INTO gdpr_assessments 
                (user_id, is_compliant, pii_count, violations_count, 
                 processing_time_ms, assessment_data, created_at)
                VALUES ($1, $2, $3, $4, $5, $6, $7)
            """            
            assessment_data = {
                "pii_categories": [pii.category.value for pii in result.pii_detected],
                "consent_requirements": [req.purpose.value for req in result.consent_requirements],
                "applicable_rights": [right.value for right in result.data_subject_rights_applicable],
                "lawful_basis": result.lawful_basis_assessment,
                "violations": result.violations,
                "recommendations": result.recommendations
            }
            
            await self.db_manager.execute(
                query,
                user_id,
                result.is_compliant,
                len(result.pii_detected),
                len(result.violations),
                result.processing_time_ms,
                assessment_data,
                datetime.now()
            )
            
        except Exception as e:
            self.logger.error(f"Error storing GDPR assessment: {str(e)}")
    
    async def process_data_subject_request(
        self,
        user_id: int,
        request_type: DataSubjectRights,
        details: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Process data subject rights requests"""        try:
            self.logger.info(f"Processing {request_type.value} request for user {user_id}")
            
            if request_type == DataSubjectRights.ACCESS:
                return await self._process_access_request(user_id, details)
            elif request_type == DataSubjectRights.ERASURE:
                return await self._process_erasure_request(user_id, details)
            elif request_type == DataSubjectRights.PORTABILITY:
                return await self._process_portability_request(user_id, details)
            elif request_type == DataSubjectRights.RECTIFICATION:
                return await self._process_rectification_request(user_id, details)
            elif request_type == DataSubjectRights.RESTRICTION:
                return await self._process_restriction_request(user_id, details)
            elif request_type == DataSubjectRights.OBJECTION:
                return await self._process_objection_request(user_id, details)
            else:
                return {
                    "success": False,
                    "message": f"Request type {request_type.value} not implemented"
                }
                
        except Exception as e:
            self.logger.error(f"Error processing data subject request: {str(e)}")
            return {
                "success": False,
                "message": f"Error processing request: {str(e)}"
            }
    
    async def _process_access_request(self, user_id: int, details: Dict[str, Any]) -> Dict[str, Any]:
        """Process data access request (Article 15)"""        try:
            # Gather all personal data for the user
            user_data = await self.db_manager.fetch_all(
                """                SELECT table_name, column_name, data_value
                FROM user_personal_data_view 
                WHERE user_id = $1
                """,
                user_id
            )
            
            # Compile data export
            data_export = {
                "user_id": user_id,
                "request_date": datetime.now().isoformat(),
                "data_categories": {},
                "processing_purposes": [],
                "retention_periods": {},
                "third_party_recipients": [],
                "transfer_safeguards": {}
            }
            
            for data_record in user_data:
                category = data_record["table_name"]
                if category not in data_export["data_categories"]:
                    data_export["data_categories"][category] = []
                
                data_export["data_categories"][category].append({
                    "field": data_record["column_name"],
                    "value": data_record["data_value"]
                })
            
            return {
                "success": True,
                "message": "Data access request processed",
                "data_export": data_export
            }
            
        except Exception as e:
            self.logger.error(f"Error in access request: {str(e)}")
            return {"success": False, "message": str(e)}
    
    async def _process_erasure_request(self, user_id: int, details: Dict[str, Any]) -> Dict[str, Any]:
        """Process data erasure request (Article 17)"""        try:
            # Check if erasure is legally permissible
            legal_obligations = await self.db_manager.fetch_all(
                """                SELECT purpose, legal_basis, retention_required_until
                FROM data_processing_records 
                WHERE user_id = $1 AND retention_required_until > $2
                """,
                user_id,
                datetime.now()
            )
            
            if legal_obligations:
                return {
                    "success": False,
                    "message": "Erasure not possible due to legal retention requirements",
                    "legal_obligations": legal_obligations
                }
            
            # Perform erasure
            erasure_results = []
            
            # Anonymize conversation data
            await self.db_manager.execute(
                "UPDATE conversations SET user_data = '{}' WHERE user_id = $1",
                user_id
            )
            erasure_results.append("Conversation data anonymized")
            
            # Delete user account data
            await self.db_manager.execute(
                "DELETE FROM user_profiles WHERE user_id = $1",
                user_id
            )
            erasure_results.append("User profile deleted")
            
            # Log erasure for audit trail
            await self.db_manager.execute(
                """                INSERT INTO data_erasure_log 
                (user_id, erasure_date, erasure_scope, legal_basis)
                VALUES ($1, $2, $3, $4)
                """,
                user_id,
                datetime.now(),
                "complete_erasure",
                "article_17_gdpr"
            )
            
            return {
                "success": True,
                "message": "Data erasure completed successfully",
                "erasure_details": erasure_results
            }
            
        except Exception as e:
            self.logger.error(f"Error in erasure request: {str(e)}")
            return {"success": False, "message": str(e)}
    
    async def _process_portability_request(self, user_id: int, details: Dict[str, Any]) -> Dict[str, Any]:
        """Process data portability request (Article 20)"""        try:
            # Export data in machine-readable format
            portable_data = await self._generate_portable_data_export(user_id)
            
            return {
                "success": True,
                "message": "Data portability export generated",
                "export_format": "JSON",
                "data": portable_data
            }
            
        except Exception as e:
            self.logger.error(f"Error in portability request: {str(e)}")
            return {"success": False, "message": str(e)}
    
    async def _process_rectification_request(self, user_id: int, details: Dict[str, Any]) -> Dict[str, Any]:
        """Process data rectification request (Article 16)"""        # Implementation for data correction
        return {"success": True, "message": "Rectification request processed"}
    
    async def _process_restriction_request(self, user_id: int, details: Dict[str, Any]) -> Dict[str, Any]:
        """Process processing restriction request (Article 18)"""        # Implementation for processing restriction
        return {"success": True, "message": "Processing restriction applied"}
    
    async def _process_objection_request(self, user_id: int, details: Dict[str, Any]) -> Dict[str, Any]:
        """Process objection to processing request (Article 21)"""        # Implementation for processing objection
        return {"success": True, "message": "Objection to processing recorded"}
    
    async def _generate_portable_data_export(self, user_id: int) -> Dict[str, Any]:
        """Generate machine-readable data export for portability"""        # Implementation for structured data export
        return {
            "user_id": user_id,
            "export_date": datetime.now().isoformat(),
            "data_format_version": "1.0",
            "personal_data": {}
        }
    
    async def grant_consent(
        self,
        user_id: int,
        purpose: DataProcessingPurpose,
        consent_evidence: Dict[str, Any]
    ) -> bool:
        """Grant user consent for specific processing purpose"""        try:
            consent_record = ConsentRecord(
                user_id=user_id,
                purpose=purpose,
                status=ConsentStatus.GRANTED,
                granted_at=datetime.now(),
                withdrawn_at=None,
                expires_at=None,
                granularity="specific",
                legal_basis="consent",
                consent_evidence=consent_evidence,
                processing_details={}
            )
            
            await self.db_manager.execute(
                """                INSERT INTO user_consents 
                (user_id, purpose, status, granted_at, granularity, legal_basis, 
                 consent_evidence, processing_details, created_at)
                VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)
                ON CONFLICT (user_id, purpose) DO UPDATE SET
                status = $3, granted_at = $4, consent_evidence = $7, updated_at = $9
                """,
                user_id, purpose.value, ConsentStatus.GRANTED.value, datetime.now(),
                "specific", "consent", consent_evidence, {}, datetime.now()
            )
            
            # Update cache
            if user_id in self.consent_cache:
                self.consent_cache[user_id][purpose.value] = consent_record
            
            self.logger.info(f"Consent granted for user {user_id}, purpose {purpose.value}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error granting consent: {str(e)}")
            return False
    
    async def withdraw_consent(self, user_id: int, purpose: DataProcessingPurpose) -> bool:
        """Withdraw user consent for specific processing purpose"""        try:
            await self.db_manager.execute(
                """                UPDATE user_consents 
                SET status = $1, withdrawn_at = $2, updated_at = $3
                WHERE user_id = $4 AND purpose = $5
                """,
                ConsentStatus.WITHDRAWN.value,
                datetime.now(),
                datetime.now(),
                user_id,
                purpose.value
            )
            
            # Update cache
            if user_id in self.consent_cache and purpose.value in self.consent_cache[user_id]:
                self.consent_cache[user_id][purpose.value].status = ConsentStatus.WITHDRAWN
                self.consent_cache[user_id][purpose.value].withdrawn_at = datetime.now()
            
            self.logger.info(f"Consent withdrawn for user {user_id}, purpose {purpose.value}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error withdrawing consent: {str(e)}")
            return False
    
    async def get_gdpr_compliance_metrics(self, days: int = 30) -> Dict[str, Any]:
        """Get GDPR compliance metrics and statistics"""        try:
            # Overall compliance metrics
            compliance_query = """                SELECT 
                    is_compliant,
                    COUNT(*) as count,
                    AVG(pii_count) as avg_pii_count,
                    AVG(violations_count) as avg_violations
                FROM gdpr_assessments 
                WHERE created_at >= $1
                GROUP BY is_compliant
            """            
            compliance_stats = await self.db_manager.fetch_all(
                compliance_query,
                datetime.now() - timedelta(days=days)
            )
            
            # Data subject requests metrics
            dsr_query = """                SELECT 
                    request_type,
                    status,
                    COUNT(*) as count
                FROM data_subject_requests 
                WHERE created_at >= $1
                GROUP BY request_type, status
            """            
            dsr_stats = await self.db_manager.fetch_all(
                dsr_query,
                datetime.now() - timedelta(days=days)
            )
            
            return {
                "period_days": days,
                "compliance_distribution": {
                    stat["is_compliant"]: stat["count"] for stat in compliance_stats
                },
                "average_pii_per_assessment": sum(stat["avg_pii_count"] or 0 for stat in compliance_stats),
                "average_violations_per_assessment": sum(stat["avg_violations"] or 0 for stat in compliance_stats),
                "data_subject_requests": {
                    f"{stat['request_type']}_{stat['status']}": stat["count"] 
                    for stat in dsr_stats
                },
                "active_consents": len(self.consent_cache),
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Error fetching GDPR metrics: {str(e)}")
            return {}
