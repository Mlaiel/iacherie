"""Compliance Processor - GDPR and regulatory compliance for IA Influencer Agent Platform
======================================================================================

Enterprise compliance engine providing GDPR, CCPA, COPPA compliance processing,
data protection, privacy controls, and regulatory audit trails for creator workflows.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel - All Rights Reserved
Warning: Unauthorized use strictly prohibited
"""

import asyncio
import logging
from typing import Dict, List, Optional, Union, Any, Tuple, Set
from pathlib import Path
from dataclasses import dataclass, field
from enum import Enum
import json
import time
import re
import hashlib
import uuid
from datetime import datetime, timezone, timedelta

logger = logging.getLogger(__name__)


class ComplianceRegulation(Enum):
    """Supported compliance regulations."""
    
    GDPR = "gdpr"           # General Data Protection Regulation (EU)
    CCPA = "ccpa"           # California Consumer Privacy Act (US)
    COPPA = "coppa"         # Children's Online Privacy Protection Act (US)
    PIPEDA = "pipeda"       # Personal Information Protection and Electronic Documents Act (Canada)
    LGPD = "lgpd"           # Lei Geral de Proteção de Dados (Brazil)
    SOC2 = "soc2"           # SOC 2 Type II
    ISO27001 = "iso27001"   # ISO 27001
    HIPAA = "hipaa"         # Health Insurance Portability and Accountability Act (US)


class DataCategory(Enum):
    """Categories of personal data."""
    
    PERSONAL_IDENTIFIERS = "personal_identifiers"
    CONTACT_INFORMATION = "contact_information"
    FINANCIAL_DATA = "financial_data"
    HEALTH_DATA = "health_data"
    BIOMETRIC_DATA = "biometric_data"
    LOCATION_DATA = "location_data"
    BEHAVIORAL_DATA = "behavioral_data"
    PREFERENCES = "preferences"
    TECHNICAL_DATA = "technical_data"
    CONTENT_DATA = "content_data"
    SPECIAL_CATEGORY = "special_category"  # Sensitive data under GDPR


class ProcessingPurpose(Enum):
    """Purposes for data processing."""
    
    CONTENT_CREATION = "content_creation"
    CONTENT_ANALYSIS = "content_analysis"
    PERSONALIZATION = "personalization"
    ANALYTICS = "analytics"
    MARKETING = "marketing"
    SECURITY = "security"
    LEGAL_COMPLIANCE = "legal_compliance"
    TECHNICAL_OPERATION = "technical_operation"
    CUSTOMER_SUPPORT = "customer_support"
    RESEARCH = "research"


class LegalBasis(Enum):
    """Legal basis for data processing under GDPR."""
    
    CONSENT = "consent"
    CONTRACT = "contract"
    LEGAL_OBLIGATION = "legal_obligation"
    VITAL_INTERESTS = "vital_interests"
    PUBLIC_TASK = "public_task"
    LEGITIMATE_INTERESTS = "legitimate_interests"


class DataSubjectRights(Enum):
    """Data subject rights under privacy regulations."""
    
    ACCESS = "access"                   # Right to access personal data
    RECTIFICATION = "rectification"     # Right to rectify inaccurate data
    ERASURE = "erasure"                # Right to be forgotten
    PORTABILITY = "portability"        # Right to data portability
    RESTRICTION = "restriction"        # Right to restrict processing
    OBJECTION = "objection"            # Right to object to processing
    WITHDRAW_CONSENT = "withdraw_consent" # Right to withdraw consent


@dataclass
class DataProcessingRecord:
    """Record of data processing activity."""
    
    record_id: str
    user_id: str
    data_categories: List[DataCategory]
    processing_purposes: List[ProcessingPurpose]
    legal_basis: LegalBasis
    consent_id: Optional[str] = None
    retention_period: int = 365  # days
    data_location: str = "EU"
    third_party_sharing: bool = False
    automated_decision_making: bool = False
    processing_timestamp: float = field(default_factory=time.time)
    expiry_timestamp: Optional[float] = None
    compliance_regulations: List[ComplianceRegulation] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ConsentRecord:
    """User consent record."""
    
    consent_id: str
    user_id: str
    purposes: List[ProcessingPurpose]
    data_categories: List[DataCategory]
    consent_given: bool
    consent_timestamp: float
    withdrawal_timestamp: Optional[float] = None
    consent_version: str = "1.0"
    consent_method: str = "explicit"  # explicit, implied, opt_in, opt_out
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    is_minor: bool = False
    parent_consent: bool = False
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class DataSubjectRequest:
    """Data subject rights request."""
    
    request_id: str
    user_id: str
    right_type: DataSubjectRights
    request_timestamp: float = field(default_factory=time.time)
    verification_status: str = "pending"  # pending, verified, rejected
    processing_status: str = "received"   # received, processing, completed, rejected
    completion_timestamp: Optional[float] = None
    request_details: Dict[str, Any] = field(default_factory=dict)
    response_data: Optional[Dict[str, Any]] = None
    verification_method: Optional[str] = None
    notes: List[str] = field(default_factory=list)


@dataclass
class ComplianceCheck:
    """Result of compliance checking."""
    
    check_id: str
    regulation: ComplianceRegulation
    compliant: bool
    violations: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    risk_level: str = "low"  # low, medium, high, critical
    check_timestamp: float = field(default_factory=time.time)
    details: Dict[str, Any] = field(default_factory=dict)


@dataclass
class PrivacyImpactAssessment:
    """Privacy Impact Assessment (PIA) result."""
    
    pia_id: str
    processing_activity: str
    data_categories: List[DataCategory]
    processing_purposes: List[ProcessingPurpose]
    risk_assessment: Dict[str, str]  # risk type -> risk level
    mitigation_measures: List[str]
    residual_risk: str = "low"
    pia_timestamp: float = field(default_factory=time.time)
    assessor: str = "system"
    review_required: bool = False
    approval_status: str = "pending"


class ComplianceProcessor:
    """Enterprise compliance processing engine."""
    
    def __init__(self, config -> None: Optional[Dict[str, Any]] = None) -> None:
        """Initialize compliance processor with configuration."""
        self.config = config or {}
        
        # Data processing records
        self.processing_records = {}
        self.consent_records = {}
        self.data_subject_requests = {}
        
        # Compliance rules and patterns
        self.data_patterns = self._load_data_detection_patterns()
        self.compliance_rules = self._load_compliance_rules()
        
        # Privacy settings
        self.default_retention_period = self.config.get("default_retention_days", 365)
        self.require_explicit_consent = self.config.get("require_explicit_consent", True)
        
        logger.info("ComplianceProcessor initialized")
    
    def _load_data_detection_patterns(self) -> Dict[str, List[str]]:
        """Load patterns for detecting personal data categories."""
        return {
            DataCategory.PERSONAL_IDENTIFIERS.value: [
                r'\b\d{3}-\d{2}-\d{4}\b',  # SSN
                r'\b[A-Z]{2}\d{6}[A-Z]\b',  # Passport pattern
                r'\b\d{4}\s*\d{4}\s*\d{4}\s*\d{4}\b'  # Credit card pattern
            ],
            DataCategory.CONTACT_INFORMATION.value: [
                r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',  # Email
                r'\b\+?1?[-.\s]?\(?[0-9]{3}\)?[-.\s]?[0-9]{3}[-.\s]?[0-9]{4}\b',  # Phone
                r'\b\d{1,5}\s+[A-Za-z\s]+(?:Street|St|Avenue|Ave|Road|Rd|Boulevard|Blvd)\b'  # Address
            ],
            DataCategory.FINANCIAL_DATA.value: [
                r'\b(?:4[0-9]{12}(?:[0-9]{3})?|5[1-5][0-9]{14}|3[47][0-9]{13}|3[0-9]{13}|6(?:011|5[0-9]{2})[0-9]{12})\b',  # Credit cards
                r'\bIBAN\s*[A-Z]{2}\d{2}[A-Z0-9]{4}\d{7}([A-Z0-9]?){0,16}\b',  # IBAN
                r'\b[A-Z]{6}[A-Z0-9]{2}([A-Z0-9]{3})?\b'  # SWIFT/BIC
            ],
            DataCategory.LOCATION_DATA.value: [
                r'\b[-+]?([1-8]?\d(\.\d+)?|90(\.0+)?),\s*[-+]?(180(\.0+)?|((1[0-7]\d)|([1-9]?\d))(\.\d+)?)\b',  # GPS coordinates
                r'\b\d{5}(-\d{4})?\b'  # ZIP codes
            ]
        }
    
    def _load_compliance_rules(self) -> Dict[str, Dict[str, Any]]:
        """Load compliance rules for different regulations."""
        return {
            ComplianceRegulation.GDPR.value: {
                "requires_consent": True,
                "allows_legitimate_interest": True,
                "max_retention_period": 2555,  # 7 years in days
                "requires_dpo": False,  # Depends on organization size
                "breach_notification_hours": 72,
                "special_category_protection": True,
                "data_portability_required": True,
                "right_to_be_forgotten": True
            },
            ComplianceRegulation.CCPA.value: {
                "requires_consent": False,  # Opt-out model
                "allows_sale_opt_out": True,
                "max_retention_period": 1095,  # 3 years
                "requires_privacy_policy": True,
                "data_portability_required": True,
                "right_to_delete": True,
                "financial_incentive_disclosure": True
            },
            ComplianceRegulation.COPPA.value: {
                "requires_parental_consent": True,
                "age_threshold": 13,
                "limited_data_collection": True,
                "no_behavioral_advertising": True,
                "secure_data_handling": True,
                "parental_access_rights": True
            }
        }
    
    async def process_with_compliance(
        self,
        content: Union[str, bytes],
        user_id: str,
        processing_purposes: List[ProcessingPurpose],
        legal_basis: LegalBasis,
        applicable_regulations: List[ComplianceRegulation]
    ) -> Dict[str, Any]:
        """
        Process content with compliance checks and controls.
        
        Args:
            content: Content to process
            user_id: User identifier
            processing_purposes: Purposes for processing
            legal_basis: Legal basis for processing
            applicable_regulations: Applicable compliance regulations
            
        Returns:
            Processing result with compliance information
        """
        try:
            # Detect personal data in content
            detected_data = await self._detect_personal_data(content)
            
            # Check compliance requirements
            compliance_checks = []
            for regulation in applicable_regulations:
                check = await self._check_regulation_compliance(
                    detected_data, processing_purposes, legal_basis, regulation
                )
                compliance_checks.append(check)
            
            # Verify consent if required
            consent_status = await self._verify_consent(
                user_id, processing_purposes, detected_data["categories"]
            )
            
            # Create processing record
            processing_record = await self._create_processing_record(
                user_id, detected_data["categories"], processing_purposes, legal_basis
            )
            
            # Apply data protection measures
            protected_content = await self._apply_data_protection(
                content, detected_data, applicable_regulations
            )
            
            # Check if all compliance requirements are met
            all_compliant = all(check.compliant for check in compliance_checks)
            
            return {
                "compliant": all_compliant,
                "processed_content": protected_content if all_compliant else None,
                "detected_data": detected_data,
                "compliance_checks": compliance_checks,
                "consent_status": consent_status,
                "processing_record": processing_record,
                "violations": [
                    violation for check in compliance_checks 
                    for violation in check.violations
                ],
                "recommendations": [
                    rec for check in compliance_checks 
                    for rec in check.recommendations
                ]
            }
            
        except Exception as e:
            logger.error(f"Compliance processing failed: {str(e)}")
            return {
                "compliant": False,
                "error": str(e),
                "processed_content": None
            }
    
    async def _detect_personal_data(self, content: Union[str, bytes]) -> Dict[str, Any]:
        """Detect personal data categories in content."""
        if isinstance(content, bytes):
            content_str = content.decode('utf-8', errors='ignore')
        else:
            content_str = content
        
        detected_categories = []
        detection_details = {}
        
        for category, patterns in self.data_patterns.items():
            matches = []
            for pattern in patterns:
                found = re.findall(pattern, content_str, re.IGNORECASE)
                matches.extend(found)
            
            if matches:
                detected_categories.append(DataCategory(category))
                detection_details[category] = {
                    "count": len(matches),
                    "samples": matches[:3]  # First 3 matches for verification
                }
        
        return {
            "categories": detected_categories,
            "details": detection_details,
            "has_personal_data": len(detected_categories) > 0
        }
    
    async def _check_regulation_compliance(
        self,
        detected_data: Dict[str, Any],
        purposes: List[ProcessingPurpose],
        legal_basis: LegalBasis,
        regulation: ComplianceRegulation
    ) -> ComplianceCheck:
        """Check compliance with specific regulation."""
        check_id = f"compliance_check_{int(time.time() * 1000)}"
        violations = []
        recommendations = []
        risk_level = "low"
        
        rules = self.compliance_rules.get(regulation.value, {})
        
        if regulation == ComplianceRegulation.GDPR:
            # GDPR-specific checks
            if detected_data["has_personal_data"]:
                # Check consent requirement
                if rules.get("requires_consent") and legal_basis == LegalBasis.CONSENT:
                    # Would verify consent exists and is valid
                    pass
                
                # Check special category data
                if DataCategory.SPECIAL_CATEGORY in detected_data["categories"]:
                    if legal_basis not in [LegalBasis.CONSENT, LegalBasis.VITAL_INTERESTS]:
                        violations.append("Special category data requires explicit consent or vital interests")
                        risk_level = "high"
                
                # Check data minimization
                if len(purposes) > 3:
                    recommendations.append("Consider data minimization - limit processing purposes")
        
        elif regulation == ComplianceRegulation.CCPA:
            # CCPA-specific checks
            if ProcessingPurpose.MARKETING in purposes:
                recommendations.append("Ensure opt-out mechanism for sale of personal information")
        
        elif regulation == ComplianceRegulation.COPPA:
            # COPPA-specific checks
            if detected_data["has_personal_data"]:
                violations.append("COPPA requires parental consent for children under 13")
                risk_level = "critical"
        
        return ComplianceCheck(
            check_id=check_id,
            regulation=regulation,
            compliant=len(violations) == 0,
            violations=violations,
            recommendations=recommendations,
            risk_level=risk_level
        )
    
    async def _verify_consent(
        self, user_id: str, purposes: List[ProcessingPurpose], data_categories: List[DataCategory]
    ) -> Dict[str, Any]:
        """Verify user consent for processing."""
        # Find relevant consent records
        user_consents = [
            consent for consent in self.consent_records.values()
            if consent.user_id == user_id and consent.consent_given and not consent.withdrawal_timestamp
        ]
        
        if not user_consents:
            return {
                "has_valid_consent": False,
                "missing_purposes": purposes,
                "missing_categories": data_categories
            }
        
        # Check if consent covers all purposes and categories
        covered_purposes = set()
        covered_categories = set()
        
        for consent in user_consents:
            covered_purposes.update(consent.purposes)
            covered_categories.update(consent.data_categories)
        
        missing_purposes = [p for p in purposes if p not in covered_purposes]
        missing_categories = [c for c in data_categories if c not in covered_categories]
        
        return {
            "has_valid_consent": len(missing_purposes) == 0 and len(missing_categories) == 0,
            "covered_purposes": list(covered_purposes),
            "covered_categories": list(covered_categories),
            "missing_purposes": missing_purposes,
            "missing_categories": missing_categories,
            "consent_records": [c.consent_id for c in user_consents]
        }
    
    async def _create_processing_record(
        self,
        user_id: str,
        data_categories: List[DataCategory],
        purposes: List[ProcessingPurpose],
        legal_basis: LegalBasis
    ) -> DataProcessingRecord:
        """Create data processing record."""
        record_id = f"processing_{uuid.uuid4().hex}"
        
        # Calculate expiry based on retention period
        expiry_timestamp = time.time() + (self.default_retention_period * 24 * 3600)
        
        record = DataProcessingRecord(
            record_id=record_id,
            user_id=user_id,
            data_categories=data_categories,
            processing_purposes=purposes,
            legal_basis=legal_basis,
            expiry_timestamp=expiry_timestamp
        )
        
        self.processing_records[record_id] = record
        
        logger.debug(f"Created processing record {record_id} for user {user_id}")
        return record
    
    async def _apply_data_protection(
        self,
        content: Union[str, bytes],
        detected_data: Dict[str, Any],
        regulations: List[ComplianceRegulation]
    ) -> Union[str, bytes]:
        """Apply data protection measures to content."""
        if not detected_data["has_personal_data"]:
            return content
        
        # Apply pseudonymization/anonymization based on regulations
        protected_content = content
        
        if isinstance(content, str):
            # Apply text-based protection
            for category, details in detected_data["details"].items():
                if category == DataCategory.CONTACT_INFORMATION.value:
                    # Mask email addresses
                    protected_content = re.sub(
                        r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
                        '[EMAIL_REDACTED]',
                        protected_content
                    )
        
        # Additional protection measures would be applied here
        
        return protected_content
    
    async def record_consent(
        self,
        user_id: str,
        purposes: List[ProcessingPurpose],
        data_categories: List[DataCategory],
        consent_given: bool,
        consent_method: str = "explicit",
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        is_minor: bool = False
    ) -> ConsentRecord:
        """Record user consent."""
        consent_id = f"consent_{uuid.uuid4().hex}"
        
        consent_record = ConsentRecord(
            consent_id=consent_id,
            user_id=user_id,
            purposes=purposes,
            data_categories=data_categories,
            consent_given=consent_given,
            consent_timestamp=time.time(),
            consent_method=consent_method,
            ip_address=ip_address,
            user_agent=user_agent,
            is_minor=is_minor,
            parent_consent=is_minor and consent_given  # Assume parental consent for minors
        )
        
        self.consent_records[consent_id] = consent_record
        
        logger.info(f"Recorded consent {consent_id} for user {user_id}: {consent_given}")
        return consent_record
    
    async def withdraw_consent(self, user_id: str, consent_id: str) -> bool:
        """Withdraw user consent."""
        if consent_id not in self.consent_records:
            return False
        
        consent_record = self.consent_records[consent_id]
        if consent_record.user_id != user_id:
            return False
        
        consent_record.withdrawal_timestamp = time.time()
        
        logger.info(f"Consent {consent_id} withdrawn for user {user_id}")
        return True
    
    async def handle_data_subject_request(
        self, user_id: str, right_type: DataSubjectRights, request_details: Optional[Dict[str, Any]] = None
    ) -> DataSubjectRequest:
        """Handle data subject rights request."""
        request_id = f"dsr_{uuid.uuid4().hex}"
        
        request = DataSubjectRequest(
            request_id=request_id,
            user_id=user_id,
            right_type=right_type,
            request_details=request_details or {}
        )
        
        self.data_subject_requests[request_id] = request
        
        # Auto-process certain types of requests
        if right_type == DataSubjectRights.ACCESS:
            await self._process_access_request(request)
        elif right_type == DataSubjectRights.ERASURE:
            await self._process_erasure_request(request)
        elif right_type == DataSubjectRights.PORTABILITY:
            await self._process_portability_request(request)
        
        logger.info(f"Created data subject request {request_id} for user {user_id}: {right_type.value}")
        return request
    
    async def _process_access_request(self, request -> None: DataSubjectRequest) -> None:
        """Process data access request."""
        user_id = request.user_id
        
        # Collect all data for the user
        user_data = {
            "processing_records": [
                record for record in self.processing_records.values()
                if record.user_id == user_id
            ],
            "consent_records": [
                consent for consent in self.consent_records.values()
                if consent.user_id == user_id
            ],
            "data_categories_processed": [],
            "retention_periods": [],
            "third_party_sharing": []
        }
        
        request.response_data = user_data
        request.processing_status = "completed"
        request.completion_timestamp = time.time()
    
    async def _process_erasure_request(self, request -> None: DataSubjectRequest) -> None:
        """Process right to be forgotten request."""
        user_id = request.user_id
        
        # Mark for deletion (in production, implement actual deletion)
        deleted_records = []
        
        for record_id, record in list(self.processing_records.items()):
            if record.user_id == user_id:
                # Check if deletion is legally required
                if self._can_delete_record(record):
                    del self.processing_records[record_id]
                    deleted_records.append(record_id)
        
        request.response_data = {"deleted_records": deleted_records}
        request.processing_status = "completed"
        request.completion_timestamp = time.time()
    
    async def _process_portability_request(self, request -> None: DataSubjectRequest) -> None:
        """Process data portability request."""
        user_id = request.user_id
        
        # Export user data in structured format
        exportable_data = {
            "user_id": user_id,
            "export_timestamp": time.time(),
            "data_categories": [],
            "processing_purposes": [],
            "consent_history": [
                {
                    "consent_id": consent.consent_id,
                    "purposes": [p.value for p in consent.purposes],
                    "timestamp": consent.consent_timestamp,
                    "withdrawn": consent.withdrawal_timestamp is not None
                }
                for consent in self.consent_records.values()
                if consent.user_id == user_id
            ]
        }
        
        request.response_data = exportable_data
        request.processing_status = "completed"
        request.completion_timestamp = time.time()
    
    def _can_delete_record(self, record: DataProcessingRecord) -> bool:
        """Check if a processing record can be deleted."""
        # Legal obligations may prevent deletion
        if LegalBasis.LEGAL_OBLIGATION in [record.legal_basis]:
            return False
        
        # Check retention requirements
        if record.expiry_timestamp and time.time() < record.expiry_timestamp:
            # Still within retention period, but erasure request overrides
            return True
        
        return True
    
    async def conduct_privacy_impact_assessment(
        self,
        processing_activity: str,
        data_categories: List[DataCategory],
        purposes: List[ProcessingPurpose]
    ) -> PrivacyImpactAssessment:
        """Conduct Privacy Impact Assessment."""
        pia_id = f"pia_{uuid.uuid4().hex}"
        
        # Assess risks for each data category
        risk_assessment = {}
        mitigation_measures = []
        
        for category in data_categories:
            if category == DataCategory.SPECIAL_CATEGORY:
                risk_assessment[category.value] = "high"
                mitigation_measures.append("Implement additional safeguards for special category data")
            elif category in [DataCategory.FINANCIAL_DATA, DataCategory.HEALTH_DATA]:
                risk_assessment[category.value] = "medium"
                mitigation_measures.append("Apply encryption and access controls")
            else:
                risk_assessment[category.value] = "low"
        
        # Assess processing purposes
        for purpose in purposes:
            if purpose == ProcessingPurpose.MARKETING:
                mitigation_measures.append("Ensure opt-out mechanisms are available")
            elif purpose == ProcessingPurpose.ANALYTICS:
                mitigation_measures.append("Consider data anonymization for analytics")
        
        # Determine overall residual risk
        risk_levels = list(risk_assessment.values())
        if "high" in risk_levels:
            residual_risk = "medium"  # After mitigation
        elif "medium" in risk_levels:
            residual_risk = "low"
        else:
            residual_risk = "low"
        
        pia = PrivacyImpactAssessment(
            pia_id=pia_id,
            processing_activity=processing_activity,
            data_categories=data_categories,
            processing_purposes=purposes,
            risk_assessment=risk_assessment,
            mitigation_measures=mitigation_measures,
            residual_risk=residual_risk,
            review_required=residual_risk in ["high", "medium"]
        )
        
        logger.info(f"Conducted PIA {pia_id} for {processing_activity}")
        return pia
    
    def get_compliance_dashboard(self) -> Dict[str, Any]:
        """Get compliance dashboard metrics."""
        current_time = time.time()
        
        # Count active processing records
        active_records = [
            record for record in self.processing_records.values()
            if not record.expiry_timestamp or record.expiry_timestamp > current_time
        ]
        
        # Count consent records
        valid_consents = [
            consent for consent in self.consent_records.values()
            if consent.consent_given and not consent.withdrawal_timestamp
        ]
        
        # Count pending data subject requests
        pending_requests = [
            request for request in self.data_subject_requests.values()
            if request.processing_status in ["received", "processing"]
        ]
        
        # Calculate compliance metrics
        return {
            "active_processing_records": len(active_records),
            "valid_consent_records": len(valid_consents),
            "pending_data_subject_requests": len(pending_requests),
            "data_categories_processed": len(set(
                category for record in active_records 
                for category in record.data_categories
            )),
            "processing_purposes_active": len(set(
                purpose for record in active_records 
                for purpose in record.processing_purposes
            )),
            "consent_withdrawal_rate": self._calculate_withdrawal_rate(),
            "average_processing_duration": self._calculate_avg_processing_duration(),
            "compliance_violations": 0,  # Would track actual violations
            "last_updated": current_time
        }
    
    def _calculate_withdrawal_rate(self) -> float:
        """Calculate consent withdrawal rate."""
        total_consents = len(self.consent_records)
        if total_consents == 0:
            return 0.0
        
        withdrawn_consents = len([
            consent for consent in self.consent_records.values()
            if consent.withdrawal_timestamp
        ])
        
        return (withdrawn_consents / total_consents) * 100
    
    def _calculate_avg_processing_duration(self) -> float:
        """Calculate average processing duration for completed requests."""
        completed_requests = [
            request for request in self.data_subject_requests.values()
            if request.completion_timestamp
        ]
        
        if not completed_requests:
            return 0.0
        
        durations = [
            request.completion_timestamp - request.request_timestamp
            for request in completed_requests
        ]
        
        return sum(durations) / len(durations) / 3600  # Convert to hours
    
    async def cleanup_expired_data(self) -> None:
        """Clean up expired processing records and data."""
        current_time = time.time()
        expired_records = []
        
        for record_id, record in list(self.processing_records.items()):
            if record.expiry_timestamp and record.expiry_timestamp <= current_time:
                expired_records.append(record_id)
                del self.processing_records[record_id]
        
        logger.info(f"Cleaned up {len(expired_records)} expired processing records")
        return expired_records


# Export all classes for module imports
__all__ = [
    "ComplianceProcessor",
    "ComplianceRegulation",
    "DataCategory",
    "ProcessingPurpose",
    "LegalBasis",
    "DataSubjectRights",
    "DataProcessingRecord",
    "ConsentRecord",
    "DataSubjectRequest",
    "ComplianceCheck",
    "PrivacyImpactAssessment"
]

logger.info("Compliance processor module loaded successfully")