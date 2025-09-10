"""
Privacy and Data Protection Module - GDPR/CCPA Compliance System
=================================================================

Comprehensive privacy and data protection system providing automated GDPR,
CCPA, and international privacy compliance with advanced user rights management.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel - All Rights Reserved
"""

import asyncio
import json
import logging
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional, Set, Tuple

logger = logging.getLogger(__name__)


class PrivacyRegulation(Enum):
    """Privacy regulation types"""
    GDPR = "gdpr"
    CCPA = "ccpa"
    LGPD = "lgpd"
    PIPEDA = "pipeda"
    PDPA = "pdpa"


class ConsentStatus(Enum):
    """User consent status"""
    GRANTED = "granted"
    DENIED = "denied"
    WITHDRAWN = "withdrawn"
    PENDING = "pending"
    EXPIRED = "expired"


class DataCategory(Enum):
    """Categories of personal data"""
    IDENTITY = "identity"
    CONTACT = "contact"
    DEMOGRAPHIC = "demographic"
    FINANCIAL = "financial"
    LOCATION = "location"
    BEHAVIOR = "behavior"
    PREFERENCES = "preferences"
    BIOMETRIC = "biometric"
    HEALTH = "health"
    SENSITIVE = "sensitive"


class PrivacyRequestType(Enum):
    """Types of privacy requests"""
    ACCESS = "access"
    RECTIFICATION = "rectification"
    ERASURE = "erasure"
    PORTABILITY = "portability"
    RESTRICTION = "restriction"
    OBJECTION = "objection"
    WITHDRAW_CONSENT = "withdraw_consent"


@dataclass
class ConsentRecord:
    """User consent record"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str = ""
    purpose: str = ""
    data_categories: List[DataCategory] = field(default_factory=list)
    status: ConsentStatus = ConsentStatus.PENDING
    granted_at: Optional[datetime] = None
    expires_at: Optional[datetime] = None
    withdrawn_at: Optional[datetime] = None
    legal_basis: str = ""
    consent_text: str = ""
    version: str = "1.0"


@dataclass
class PrivacyRequest:
    """Privacy request record"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str = ""
    request_type: PrivacyRequestType = PrivacyRequestType.ACCESS
    data_categories: List[DataCategory] = field(default_factory=list)
    status: str = "pending"
    created_at: datetime = field(default_factory=datetime.utcnow)
    processed_at: Optional[datetime] = None
    response_data: Optional[Dict[str, Any]] = None
    verification_status: str = "pending"


@dataclass
class DataProcessingRecord:
    """Data processing activity record"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    purpose: str = ""
    data_categories: List[DataCategory] = field(default_factory=list)
    legal_basis: str = ""
    retention_period: int = 365  # days
    recipients: List[str] = field(default_factory=list)
    cross_border_transfers: bool = False
    automated_decision_making: bool = False
    security_measures: List[str] = field(default_factory=list)


class GDPRComplianceManager:
    """
    GDPR Compliance Manager for EU data protection
    
    Provides comprehensive GDPR compliance including consent management,
    user rights processing, and data protection by design.
    """
    
    def __init__(self):
        """Initialize GDPR compliance manager"""
        self.consent_records: Dict[str, ConsentRecord] = {}
        self.privacy_requests: Dict[str, PrivacyRequest] = {}
        self.processing_activities: Dict[str, DataProcessingRecord] = {}
        self.data_subjects: Dict[str, Dict[str, Any]] = {}
        logger.info("🇪🇺 GDPR Compliance Manager initialized")
    
    async def collect_consent(
        self,
        user_id: str,
        purpose: str,
        data_categories: List[DataCategory],
        consent_text: str,
        retention_period: Optional[int] = None
    ) -> str:
        """
        Collect and record user consent under GDPR
        
        Args:
            user_id: User identifier
            purpose: Purpose of data processing
            data_categories: Categories of data to be processed
            consent_text: Clear consent text shown to user
            retention_period: Consent validity period in days
            
        Returns:
            Consent record ID
        """
        expires_at = None
        if retention_period:
            expires_at = datetime.utcnow() + timedelta(days=retention_period)
        
        consent = ConsentRecord(
            user_id=user_id,
            purpose=purpose,
            data_categories=data_categories,
            status=ConsentStatus.GRANTED,
            granted_at=datetime.utcnow(),
            expires_at=expires_at,
            legal_basis="consent",
            consent_text=consent_text
        )
        
        self.consent_records[consent.id] = consent
        
        # Update user's consent profile
        if user_id not in self.data_subjects:
            self.data_subjects[user_id] = {"consents": [], "requests": []}
        
        self.data_subjects[user_id]["consents"].append(consent.id)
        
        logger.info(f"GDPR consent collected: {consent.id} for user {user_id}")
        return consent.id
    
    async def withdraw_consent(self, user_id: str, consent_id: str) -> bool:
        """
        Process consent withdrawal under GDPR Article 7(3)
        
        Args:
            user_id: User withdrawing consent
            consent_id: Consent record to withdraw
            
        Returns:
            True if withdrawal was successful
        """
        if consent_id not in self.consent_records:
            logger.error(f"Consent record not found: {consent_id}")
            return False
        
        consent = self.consent_records[consent_id]
        
        if consent.user_id != user_id:
            logger.error(f"Consent {consent_id} does not belong to user {user_id}")
            return False
        
        consent.status = ConsentStatus.WITHDRAWN
        consent.withdrawn_at = datetime.utcnow()
        
        # Trigger data processing cessation
        await self._cease_data_processing(user_id, consent.purpose, consent.data_categories)
        
        logger.info(f"GDPR consent withdrawn: {consent_id} by user {user_id}")
        return True
    
    async def process_subject_access_request(self, user_id: str) -> str:
        """
        Process subject access request under GDPR Article 15
        
        Args:
            user_id: User requesting data access
            
        Returns:
            Privacy request ID
        """
        request = PrivacyRequest(
            user_id=user_id,
            request_type=PrivacyRequestType.ACCESS,
            data_categories=list(DataCategory)  # All categories
        )
        
        self.privacy_requests[request.id] = request
        
        # Process request asynchronously
        asyncio.create_task(self._process_access_request(request.id))
        
        logger.info(f"GDPR access request created: {request.id} for user {user_id}")
        return request.id
    
    async def _process_access_request(self, request_id: str):
        """Process subject access request asynchronously"""
        request = self.privacy_requests[request_id]
        
        try:
            # Verify user identity
            await self._verify_user_identity(request.user_id)
            request.verification_status = "verified"
            
            # Collect user data
            user_data = await self._collect_user_data(request.user_id, request.data_categories)
            
            # Format response
            response = {
                "user_id": request.user_id,
                "request_date": request.created_at.isoformat(),
                "data_categories": [cat.value for cat in request.data_categories],
                "personal_data": user_data,
                "processing_purposes": await self._get_processing_purposes(request.user_id),
                "data_recipients": await self._get_data_recipients(request.user_id),
                "retention_periods": await self._get_retention_periods(request.user_id),
                "user_rights": self._get_user_rights_information()
            }
            
            request.response_data = response
            request.status = "completed"
            request.processed_at = datetime.utcnow()
            
            logger.info(f"GDPR access request processed: {request_id}")
            
        except Exception as e:
            logger.error(f"Failed to process access request {request_id}: {e}")
            request.status = "failed"
    
    async def process_erasure_request(self, user_id: str, specific_data: Optional[List[str]] = None) -> str:
        """
        Process right to erasure request under GDPR Article 17
        
        Args:
            user_id: User requesting data erasure
            specific_data: Specific data items to erase (None for complete erasure)
            
        Returns:
            Privacy request ID
        """
        request = PrivacyRequest(
            user_id=user_id,
            request_type=PrivacyRequestType.ERASURE,
            data_categories=list(DataCategory)
        )
        
        if specific_data:
            request.response_data = {"specific_data": specific_data}
        
        self.privacy_requests[request.id] = request
        
        # Process erasure asynchronously
        asyncio.create_task(self._process_erasure_request(request.id))
        
        logger.info(f"GDPR erasure request created: {request.id} for user {user_id}")
        return request.id
    
    async def _process_erasure_request(self, request_id: str):
        """Process right to erasure request asynchronously"""
        request = self.privacy_requests[request_id]
        
        try:
            # Verify erasure eligibility
            if await self._verify_erasure_eligibility(request.user_id):
                # Perform data erasure
                await self._erase_user_data(request.user_id, request.response_data)
                request.status = "completed"
                logger.info(f"GDPR erasure completed: {request_id}")
            else:
                request.status = "denied"
                request.response_data = {"reason": "Erasure not permitted under legal obligation"}
                logger.info(f"GDPR erasure denied: {request_id}")
            
            request.processed_at = datetime.utcnow()
            
        except Exception as e:
            logger.error(f"Failed to process erasure request {request_id}: {e}")
            request.status = "failed"
    
    async def _cease_data_processing(self, user_id: str, purpose: str, data_categories: List[DataCategory]):
        """Cease data processing when consent is withdrawn"""
        logger.info(f"Ceasing data processing for user {user_id}, purpose: {purpose}")
        # Implementation would stop relevant data processing activities
    
    async def _verify_user_identity(self, user_id: str) -> bool:
        """Verify user identity for privacy requests"""
        # Simulate identity verification
        await asyncio.sleep(0.5)
        return True
    
    async def _collect_user_data(self, user_id: str, categories: List[DataCategory]) -> Dict[str, Any]:
        """Collect all user data for access request"""
        # Simulate data collection from various systems
        await asyncio.sleep(1.0)
        
        return {
            "profile_data": {"user_id": user_id, "created_at": "2024-01-01"},
            "consent_records": [c.id for c in self.consent_records.values() if c.user_id == user_id],
            "privacy_requests": [r.id for r in self.privacy_requests.values() if r.user_id == user_id]
        }
    
    async def _get_processing_purposes(self, user_id: str) -> List[str]:
        """Get data processing purposes for user"""
        return ["Content personalization", "Security monitoring", "Communication"]
    
    async def _get_data_recipients(self, user_id: str) -> List[str]:
        """Get data recipients for user"""
        return ["Platform operators", "Third-party analytics", "Security services"]
    
    async def _get_retention_periods(self, user_id: str) -> Dict[str, str]:
        """Get data retention periods"""
        return {
            "Profile data": "Account lifetime + 2 years",
            "Usage data": "2 years",
            "Marketing data": "Until consent withdrawal"
        }
    
    def _get_user_rights_information(self) -> Dict[str, str]:
        """Get information about user rights under GDPR"""
        return {
            "right_to_access": "You have the right to obtain confirmation whether your personal data is being processed",
            "right_to_rectification": "You have the right to have inaccurate personal data corrected",
            "right_to_erasure": "You have the right to have your personal data erased in certain circumstances",
            "right_to_portability": "You have the right to receive your personal data in a structured format",
            "right_to_object": "You have the right to object to processing based on legitimate interests",
            "right_to_withdraw_consent": "You have the right to withdraw consent at any time"
        }
    
    async def _verify_erasure_eligibility(self, user_id: str) -> bool:
        """Verify if user data can be erased"""
        # Check legal obligations, legitimate interests, etc.
        return True  # Simplified for demo
    
    async def _erase_user_data(self, user_id: str, specific_data: Optional[Dict[str, Any]]):
        """Erase user data across all systems"""
        logger.info(f"Erasing data for user {user_id}")
        # Implementation would delete user data from all systems


class PrivacyPolicyManager:
    """
    Privacy policy management and compliance system
    
    Manages privacy policies across jurisdictions with automated
    updates and compliance verification.
    """
    
    def __init__(self):
        """Initialize privacy policy manager"""
        self.privacy_policies: Dict[str, Dict[str, Any]] = {}
        self.policy_versions: Dict[str, List[Dict[str, Any]]] = {}
        self.user_acknowledgments: Dict[str, Dict[str, Any]] = {}
        logger.info("📋 Privacy Policy Manager initialized")
    
    async def create_privacy_policy(
        self,
        jurisdiction: str,
        regulation: PrivacyRegulation,
        policy_content: Dict[str, Any]
    ) -> str:
        """
        Create privacy policy for specific jurisdiction
        
        Args:
            jurisdiction: Legal jurisdiction (e.g., "EU", "CA", "US")
            regulation: Applicable privacy regulation
            policy_content: Policy content and clauses
            
        Returns:
            Privacy policy ID
        """
        policy_id = f"{jurisdiction}_{regulation.value}_{datetime.utcnow().strftime('%Y%m%d')}"
        
        policy = {
            "id": policy_id,
            "jurisdiction": jurisdiction,
            "regulation": regulation.value,
            "content": policy_content,
            "version": "1.0",
            "effective_date": datetime.utcnow().isoformat(),
            "created_at": datetime.utcnow().isoformat(),
            "status": "active"
        }
        
        self.privacy_policies[policy_id] = policy
        
        if policy_id not in self.policy_versions:
            self.policy_versions[policy_id] = []
        self.policy_versions[policy_id].append(policy)
        
        logger.info(f"Privacy policy created: {policy_id}")
        return policy_id
    
    async def update_privacy_policy(
        self,
        policy_id: str,
        updated_content: Dict[str, Any],
        change_reason: str
    ) -> str:
        """
        Update existing privacy policy
        
        Args:
            policy_id: Existing policy identifier
            updated_content: Updated policy content
            change_reason: Reason for policy update
            
        Returns:
            New policy version ID
        """
        if policy_id not in self.privacy_policies:
            raise ValueError(f"Privacy policy not found: {policy_id}")
        
        current_policy = self.privacy_policies[policy_id]
        
        # Create new version
        version_number = float(current_policy["version"]) + 0.1
        new_policy = {
            **current_policy,
            "content": updated_content,
            "version": f"{version_number:.1f}",
            "effective_date": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat(),
            "change_reason": change_reason,
            "previous_version": current_policy["version"]
        }
        
        # Archive current version and activate new one
        current_policy["status"] = "archived"
        self.privacy_policies[policy_id] = new_policy
        self.policy_versions[policy_id].append(new_policy)
        
        # Notify users of policy changes
        await self._notify_policy_update(policy_id, change_reason)
        
        logger.info(f"Privacy policy updated: {policy_id} to version {new_policy['version']}")
        return policy_id
    
    async def _notify_policy_update(self, policy_id: str, change_reason: str):
        """Notify users of privacy policy updates"""
        # Implementation would send notifications to affected users
        logger.info(f"Notifying users of policy update: {policy_id}")


class ConsentManagementSystem:
    """
    Comprehensive consent management system
    
    Provides granular consent collection, management, and automated
    compliance across multiple privacy regulations.
    """
    
    def __init__(self):
        """Initialize consent management system"""
        self.consent_forms: Dict[str, Dict[str, Any]] = {}
        self.consent_preferences: Dict[str, Dict[str, Any]] = {}
        self.consent_history: Dict[str, List[Dict[str, Any]]] = {}
        logger.info("✅ Consent Management System initialized")
    
    async def create_consent_form(
        self,
        purpose: str,
        data_categories: List[DataCategory],
        legal_basis: str,
        retention_period: int,
        regulation: PrivacyRegulation
    ) -> str:
        """
        Create consent form for specific purpose
        
        Args:
            purpose: Purpose of data processing
            data_categories: Categories of data to be collected
            legal_basis: Legal basis for processing
            retention_period: Data retention period in days
            regulation: Applicable privacy regulation
            
        Returns:
            Consent form ID
        """
        form_id = str(uuid.uuid4())
        
        consent_form = {
            "id": form_id,
            "purpose": purpose,
            "data_categories": [cat.value for cat in data_categories],
            "legal_basis": legal_basis,
            "retention_period": retention_period,
            "regulation": regulation.value,
            "created_at": datetime.utcnow().isoformat(),
            "consent_text": await self._generate_consent_text(
                purpose, data_categories, retention_period, regulation
            )
        }
        
        self.consent_forms[form_id] = consent_form
        
        logger.info(f"Consent form created: {form_id}")
        return form_id
    
    async def _generate_consent_text(
        self,
        purpose: str,
        data_categories: List[DataCategory],
        retention_period: int,
        regulation: PrivacyRegulation
    ) -> str:
        """Generate compliant consent text"""
        categories_text = ", ".join([cat.value for cat in data_categories])
        
        consent_text = f"""
By clicking "I agree", you consent to the processing of your personal data for the following purpose: {purpose}.

Data categories: {categories_text}

Your data will be retained for {retention_period} days unless you withdraw your consent earlier.

You have the right to withdraw your consent at any time. Withdrawal will not affect the lawfulness of processing based on consent before its withdrawal.

This consent is collected in compliance with {regulation.value.upper()} requirements.

For more information about your rights and how we process your data, please see our Privacy Policy.
"""
        return consent_text.strip()


class DataMinimizationEngine:
    """
    Data minimization engine for privacy by design
    
    Implements data minimization principles to ensure only necessary
    data is collected and processed in compliance with privacy regulations.
    """
    
    def __init__(self):
        """Initialize data minimization engine"""
        self.minimization_rules: Dict[str, Dict[str, Any]] = {}
        self.data_assessments: Dict[str, Dict[str, Any]] = {}
        logger.info("🔒 Data Minimization Engine initialized")
    
    async def assess_data_necessity(
        self,
        purpose: str,
        requested_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Assess whether requested data is necessary for purpose
        
        Args:
            purpose: Purpose of data processing
            requested_data: Data fields being requested
            
        Returns:
            Assessment result with necessary/unnecessary data categorization
        """
        assessment_id = str(uuid.uuid4())
        
        necessary_data = {}
        unnecessary_data = {}
        
        # Apply minimization rules (simplified logic)
        for field, value in requested_data.items():
            if await self._is_data_necessary(field, purpose):
                necessary_data[field] = value
            else:
                unnecessary_data[field] = value
        
        assessment = {
            "assessment_id": assessment_id,
            "purpose": purpose,
            "necessary_data": necessary_data,
            "unnecessary_data": unnecessary_data,
            "compliance_score": len(necessary_data) / max(len(requested_data), 1),
            "recommendations": await self._generate_minimization_recommendations(
                purpose, unnecessary_data
            ),
            "assessed_at": datetime.utcnow().isoformat()
        }
        
        self.data_assessments[assessment_id] = assessment
        
        logger.info(f"Data minimization assessment completed: {assessment_id}")
        return assessment
    
    async def _is_data_necessary(self, field: str, purpose: str) -> bool:
        """Determine if data field is necessary for given purpose"""
        # Simplified necessity logic - would be more sophisticated in production
        necessity_map = {
            "authentication": ["email", "password", "user_id"],
            "content_personalization": ["preferences", "behavior", "location"],
            "communication": ["email", "contact"],
            "security": ["ip_address", "device_info", "behavior"],
            "analytics": ["behavior", "demographic", "preferences"]
        }
        
        necessary_fields = necessity_map.get(purpose, [])
        return any(necessary_field in field.lower() for necessary_field in necessary_fields)
    
    async def _generate_minimization_recommendations(
        self, purpose: str, unnecessary_data: Dict[str, Any]
    ) -> List[str]:
        """Generate recommendations for data minimization"""
        recommendations = []
        
        if unnecessary_data:
            recommendations.append(
                f"Consider removing {len(unnecessary_data)} unnecessary data fields"
            )
            recommendations.append(
                "Implement purpose-specific data collection"
            )
            recommendations.append(
                "Review data necessity on regular basis"
            )
        
        return recommendations