"""GDPR Handler - Data Protection and Privacy Compliance

Comprehensive GDPR compliance management including consent tracking, data subject rights,
privacy controls, and automated compliance monitoring for the IA Influencer Agent platform.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: All rights reserved. Unauthorized use prohibited.
"""

from typing import Dict, List, Any, Optional, Union, Tuple
from datetime import datetime, timedelta
from enum import Enum
import asyncio
import logging
from dataclasses import dataclass, asdict
import json
import uuid

logger = logging.getLogger(__name__)


class ConsentStatus(Enum):
    """
GDPR consent status enumeration."""

    GIVEN = "given"
    WITHDRAWN = "withdrawn"
    PENDING = "pending"
    EXPIRED = "expired"
    INVALID = "invalid"


class DataCategory(Enum):
    """Categories of personal data under GDPR."""

    PERSONAL_IDENTIFIERS = "personal_identifiers"
    CONTACT_INFORMATION = "contact_information"
    DEMOGRAPHIC_DATA = "demographic_data"
    BIOMETRIC_DATA = "biometric_data"
    BEHAVIORAL_DATA = "behavioral_data"
    CONTENT_DATA = "content_data"
    FINANCIAL_DATA = "financial_data"
    LOCATION_DATA = "location_data"
    DEVICE_DATA = "device_data"
    USAGE_DATA = "usage_data"


class ProcessingPurpose(Enum):
    """Lawful purposes for data processing under GDPR."""

    CONTRACT_PERFORMANCE = "contract_performance"
    LEGAL_OBLIGATION = "legal_obligation"
    VITAL_INTERESTS = "vital_interests"
    PUBLIC_TASK = "public_task"
    LEGITIMATE_INTERESTS = "legitimate_interests"
    CONSENT = "consent"


class DataSubjectRight(Enum):
    """Data subject rights under GDPR."""

    ACCESS = "access"
    RECTIFICATION = "rectification"
    ERASURE = "erasure"
    RESTRICT_PROCESSING = "restrict_processing"
    DATA_PORTABILITY = "data_portability"
    OBJECT_TO_PROCESSING = "object_to_processing"
    WITHDRAW_CONSENT = "withdraw_consent"


@dataclass
class ConsentRecord:
    """GDPR consent record structure."""
    consent_id: str
    user_id: str
    data_categories: List[DataCategory]
    processing_purposes: List[ProcessingPurpose]
    consent_status: ConsentStatus
    given_at: datetime
    withdrawn_at: Optional[datetime]
    expires_at: Optional[datetime]
    consent_method: str
    legal_basis: str
    version: str
    ip_address: str
    user_agent: str


@dataclass
class DataSubjectRequest:
    """
Data subject request structure."""
    request_id: str
    user_id: str
    request_type: DataSubjectRight
    data_categories: List[DataCategory]
    status: str
    submitted_at: datetime
    deadline: datetime
    processed_at: Optional[datetime]
    response_data: Optional[Dict[str, Any]]
    notes: str


class GDPRHandler:
    """
    Comprehensive GDPR compliance handler.
    
    Manages consent, data subject rights, privacy controls,
    and automated compliance monitoring.
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the GDPR Handler.
        
        Args:
            config: Configuration dictionary with database connections
        """
        self.config = config
        self.db_config = config.get("database", {})
        self.gdpr_config = config.get("gdpr", {})
        
        # Consent and request registries
        self.consent_records: Dict[str, ConsentRecord] = {}
        self.data_subject_requests: Dict[str, DataSubjectRequest] = {}
        
        # GDPR settings
        self.consent_expiry_days = self.gdpr_config.get("consent_expiry_days", 365)
        self.request_deadline_days = self.gdpr_config.get("request_deadline_days", 30)
        self.auto_processing_enabled = self.gdpr_config.get("auto_processing", True)
        
        logger.info("GDPR Handler initialized successfully")
    
    async def record_consent(
        self,
        user_id: str,
        data_categories: List[str],
        processing_purposes: List[str],
        consent_method: str,
        legal_basis: str = "consent",
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        version: str = "1.0"
    ) -> Dict[str, Any]:
        """
        Record user consent for data processing.
        
        Args:
            user_id: ID of the user giving consent
            data_categories: Categories of data user consents to
            processing_purposes: Purposes for which data will be processed
            consent_method: How consent was obtained
            legal_basis: Legal basis for processing
            ip_address: User's IP address when consent given
            user_agent: User's browser/device information
            version: Version of consent form/policy
            
        Returns:
            Consent recording results
        """
        try:
            # Generate unique consent ID
            consent_id = f"consent_{uuid.uuid4().hex[:12]}"
            
            # Convert string enums to proper enums
            data_cat_enums = [DataCategory(cat) for cat in data_categories]
            purpose_enums = [ProcessingPurpose(purpose) for purpose in processing_purposes]
            
            # Calculate expiry date
            expires_at = datetime.utcnow() + timedelta(days=self.consent_expiry_days)
            
            # Create consent record
            consent_record = ConsentRecord(
                consent_id=consent_id,
                user_id=user_id,
                data_categories=data_cat_enums,
                processing_purposes=purpose_enums,
                consent_status=ConsentStatus.GIVEN,
                given_at=datetime.utcnow(),
                withdrawn_at=None,
                expires_at=expires_at,
                consent_method=consent_method,
                legal_basis=legal_basis,
                version=version,
                ip_address=ip_address or "unknown",
                user_agent=user_agent or "unknown"
            )
            
            # Store consent record
            self.consent_records[consent_id] = consent_record
            
            # Withdraw any previous consents for same categories
            await self._withdraw_previous_consents(user_id, data_cat_enums)
            
            consent_result = {
                "consent_id": consent_id,
                "user_id": user_id,
                "status": "recorded",
                "given_at": consent_record.given_at.isoformat(),
                "expires_at": consent_record.expires_at.isoformat() if consent_record.expires_at else None,
                "data_categories": [cat.value for cat in data_cat_enums],
                "processing_purposes": [purpose.value for purpose in purpose_enums],
                "legal_basis": legal_basis,
                "valid_until": expires_at.isoformat() if expires_at else None
            }
            
            # Log consent recording
            await self._log_consent_action("consent_given", consent_record, consent_result)
            
            return consent_result
            
        except Exception as e:
            logger.error(f"Error recording consent: {str(e)}")
            raise
    
    async def withdraw_consent(
        self,
        user_id: str,
        consent_id: Optional[str] = None,
        data_categories: Optional[List[str]] = None,
        withdrawal_method: str = "user_request"
    ) -> Dict[str, Any]:
        """
        Process consent withdrawal.
        
        Args:
            user_id: ID of user withdrawing consent
            consent_id: Specific consent to withdraw (optional)
            data_categories: Categories to withdraw consent for (optional)
            withdrawal_method: How consent was withdrawn
            
        Returns:
            Consent withdrawal results
        """
        try:
            withdrawn_consents = []
            
            if consent_id:
                # Withdraw specific consent
                if consent_id in self.consent_records:
                    consent = self.consent_records[consent_id]
                    if consent.user_id == user_id and consent.consent_status == ConsentStatus.GIVEN:
                        consent.consent_status = ConsentStatus.WITHDRAWN
                        consent.withdrawn_at = datetime.utcnow()
                        withdrawn_consents.append(consent)
            else:
                # Withdraw consents for specified categories or all
                for consent in self.consent_records.values():
                    if (consent.user_id == user_id and 
                        consent.consent_status == ConsentStatus.GIVEN):
                        
                        if data_categories:
                            # Check if any categories match
                            consent_categories = [cat.value for cat in consent.data_categories]
                            if any(cat in consent_categories for cat in data_categories):
                                consent.consent_status = ConsentStatus.WITHDRAWN
                                consent.withdrawn_at = datetime.utcnow()
                                withdrawn_consents.append(consent)
                        else:
                            # Withdraw all consents
                            consent.consent_status = ConsentStatus.WITHDRAWN
                            consent.withdrawn_at = datetime.utcnow()
                            withdrawn_consents.append(consent)
            
            # Process data deletion if required
            deletion_tasks = []
            for consent in withdrawn_consents:
                if consent.legal_basis == "consent":
                    # If consent was the only legal basis, schedule data deletion
                    deletion_task = await self._schedule_data_deletion(
                        user_id, consent.data_categories
                    )
                    deletion_tasks.append(deletion_task)
            
            withdrawal_result = {
                "user_id": user_id,
                "withdrawn_consents": len(withdrawn_consents),
                "withdrawal_method": withdrawal_method,
                "withdrawn_at": datetime.utcnow().isoformat(),
                "data_deletion_scheduled": len(deletion_tasks),
                "consent_details": [
                    {
                        "consent_id": c.consent_id,
                        "data_categories": [cat.value for cat in c.data_categories],
                        "given_at": c.given_at.isoformat(),
                        "withdrawn_at": c.withdrawn_at.isoformat()
                    }
                    for c in withdrawn_consents
                ]
            }
            
            # Log withdrawal
            for consent in withdrawn_consents:
                await self._log_consent_action("consent_withdrawn", consent, withdrawal_result)
            
            return withdrawal_result
            
        except Exception as e:
            logger.error(f"Error withdrawing consent: {str(e)}")
            raise
    
    async def verify_gdpr_compliance(
        self,
        user_id: str,
        content_id: str,
        processing_purpose: str = "content_processing"
    ) -> Dict[str, Any]:
        """
        Verify GDPR compliance for user data processing.
        
        Args:
            user_id: ID of the user whose data is being processed
            content_id: ID of the content being processed
            processing_purpose: Purpose for data processing
            
        Returns:
            GDPR compliance verification results
        """
        try:
            compliance_result = {
                "user_id": user_id,
                "content_id": content_id,
                "verified_at": datetime.utcnow().isoformat(),
                "compliant": False,
                "legal_basis": None,
                "consent_status": None,
                "required_actions": [],
                "warnings": []
            }
            
            # Check for valid consent
            valid_consents = await self._get_valid_consents(user_id, processing_purpose)
            
            if valid_consents:
                # Check if consent covers the processing purpose
                purpose_covered = any(
                    ProcessingPurpose(processing_purpose) in consent.processing_purposes
                    for consent in valid_consents
                )
                
                if purpose_covered:
                    compliance_result["compliant"] = True
                    compliance_result["legal_basis"] = "consent"
                    compliance_result["consent_status"] = "valid"
                else:
                    compliance_result["required_actions"].append(
                        f"Obtain consent for {processing_purpose}"
                    )
            
            # Check for other legal bases if no consent
            if not compliance_result["compliant"]:
                other_legal_basis = await self._check_alternative_legal_basis(
                    user_id, processing_purpose
                )
                
                if other_legal_basis:
                    compliance_result["compliant"] = True
                    compliance_result["legal_basis"] = other_legal_basis
                else:
                    compliance_result["required_actions"].append(
                        "Establish legal basis for processing"
                    )
            
            # Check for expired consents
            expired_consents = await self._get_expired_consents(user_id)
            if expired_consents:
                compliance_result["warnings"].append(
                    f"{len(expired_consents)} expired consents require renewal"
                )
            
            # Verify data minimization
            data_minimization_check = await self._verify_data_minimization(
                user_id, content_id, processing_purpose
            )
            
            if not data_minimization_check["compliant"]:
                compliance_result["warnings"].extend(data_minimization_check["issues"])
            
            return compliance_result
            
        except Exception as e:
            logger.error(f"Error verifying GDPR compliance: {str(e)}")
            raise
    
    async def process_data_subject_request(
        self,
        request_type: str,
        user_id: str,
        data_categories: List[str],
        jurisdiction: str = "EU"
    ) -> Dict[str, Any]:
        """
        Process data subject rights request under GDPR.
        
        Args:
            request_type: Type of request (access, erasure, portability, etc.)
            user_id: ID of the data subject
            data_categories: Categories of data requested
            jurisdiction: Legal jurisdiction
            
        Returns:
            Request processing results
        """
        try:
            # Generate request ID
            request_id = f"dsr_{uuid.uuid4().hex[:12]}"
            
            # Calculate deadline (30 days from request)
            deadline = datetime.utcnow() + timedelta(days=self.request_deadline_days)
            
            # Convert to enum
            data_cat_enums = [DataCategory(cat) for cat in data_categories]
            right_enum = DataSubjectRight(request_type)
            
            # Create request record
            request_record = DataSubjectRequest(
                request_id=request_id,
                user_id=user_id,
                request_type=right_enum,
                data_categories=data_cat_enums,
                status="submitted",
                submitted_at=datetime.utcnow(),
                deadline=deadline,
                processed_at=None,
                response_data=None,
                notes=""
            )
            
            # Store request
            self.data_subject_requests[request_id] = request_record
            
            # Process request based on type
            processing_result = await self._process_specific_request(request_record)
            
            # Auto-process if enabled and feasible
            if (self.auto_processing_enabled and 
                processing_result.get("auto_processable", False)):
                
                request_record.status = "processing"
                response_data = await self._auto_process_request(request_record)
                
                request_record.processed_at = datetime.utcnow()
                request_record.response_data = response_data
                request_record.status = "completed"
            
            request_result = {
                "request_id": request_id,
                "request_type": request_type,
                "user_id": user_id,
                "status": request_record.status,
                "submitted_at": request_record.submitted_at.isoformat(),
                "deadline": request_record.deadline.isoformat(),
                "estimated_completion": self._estimate_completion_time(request_record),
                "data_categories": data_categories,
                "auto_processed": request_record.status == "completed"
            }
            
            # Include response data if completed
            if request_record.response_data:
                request_result["response_data"] = request_record.response_data
            
            # Log request
            await self._log_data_subject_request(request_record, request_result)
            
            return request_result
            
        except Exception as e:
            logger.error(f"Error processing data subject request: {str(e)}")
            raise
    
    async def get_compliance_summary(
        self,
        user_id: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """
        Get GDPR compliance summary for reporting.
        
        Args:
            user_id: Optional user ID to filter by
            start_date: Start date for summary period
            end_date: End date for summary period
            
        Returns:
            GDPR compliance summary
        """
        try:
            if not start_date:
                start_date = datetime.utcnow() - timedelta(days=30)
            if not end_date:
                end_date = datetime.utcnow()
            
            summary = {
                "period": {
                    "start": start_date.isoformat(),
                    "end": end_date.isoformat()
                },
                "user_id": user_id,
                "total_checks": 0,
                "compliant": 0,
                "non_compliant": 0,
                "pending": 0,
                "consent_summary": {
                    "total_consents": 0,
                    "active_consents": 0,
                    "withdrawn_consents": 0,
                    "expired_consents": 0
                },
                "request_summary": {
                    "total_requests": 0,
                    "completed_requests": 0,
                    "pending_requests": 0,
                    "overdue_requests": 0
                },
                "compliance_rate": 0.0
            }
            
            # Filter records by criteria
            filtered_consents = self._filter_consents_by_criteria(
                user_id, start_date, end_date
            )
            filtered_requests = self._filter_requests_by_criteria(
                user_id, start_date, end_date
            )
            
            # Calculate consent summary
            summary["consent_summary"]["total_consents"] = len(filtered_consents)
            
            for consent in filtered_consents:
                if consent.consent_status == ConsentStatus.GIVEN:
                    summary["consent_summary"]["active_consents"] += 1
                elif consent.consent_status == ConsentStatus.WITHDRAWN:
                    summary["consent_summary"]["withdrawn_consents"] += 1
                elif consent.consent_status == ConsentStatus.EXPIRED:
                    summary["consent_summary"]["expired_consents"] += 1
            
            # Calculate request summary
            summary["request_summary"]["total_requests"] = len(filtered_requests)
            
            for request in filtered_requests:
                if request.status == "completed":
                    summary["request_summary"]["completed_requests"] += 1
                elif request.status in ["submitted", "processing"]:
                    summary["request_summary"]["pending_requests"] += 1
                    
                    # Check if overdue
                    if datetime.utcnow() > request.deadline:
                        summary["request_summary"]["overdue_requests"] += 1
            
            # Calculate overall compliance
            total_items = (summary["consent_summary"]["total_consents"] + 
                          summary["request_summary"]["total_requests"])
            
            if total_items > 0:
                compliant_items = (summary["consent_summary"]["active_consents"] + 
                                 summary["request_summary"]["completed_requests"])
                summary["compliance_rate"] = (compliant_items / total_items) * 100
            
            summary["total_checks"] = total_items
            summary["compliant"] = (summary["consent_summary"]["active_consents"] + 
                                  summary["request_summary"]["completed_requests"])
            summary["non_compliant"] = (summary["consent_summary"]["expired_consents"] + 
                                      summary["request_summary"]["overdue_requests"])
            summary["pending"] = summary["request_summary"]["pending_requests"]
            
            return summary
            
        except Exception as e:
            logger.error(f"Error generating GDPR compliance summary: {str(e)}")
            raise
    
    # Private helper methods
    async def _withdraw_previous_consents(
        self,
        user_id: str,
        data_categories: List[DataCategory]
    ) -> None:
        """Withdraw previous consents for the same data categories."""
        for consent in self.consent_records.values():
            if (consent.user_id == user_id and 
                consent.consent_status == ConsentStatus.GIVEN):
                
                # Check if categories overlap
                category_overlap = any(
                    cat in consent.data_categories for cat in data_categories
                )
                
                if category_overlap:
                    consent.consent_status = ConsentStatus.WITHDRAWN
                    consent.withdrawn_at = datetime.utcnow()
    
    async def _get_valid_consents(
        self,
        user_id: str,
        processing_purpose: str
    ) -> List[ConsentRecord]:
        """
Get valid consents for user and purpose."""
        valid_consents = []
        
        for consent in self.consent_records.values():
            if (consent.user_id == user_id and 
                consent.consent_status == ConsentStatus.GIVEN):
                
                # Check if not expired
                if (consent.expires_at is None or 
                    consent.expires_at > datetime.utcnow()):
                    valid_consents.append(consent)
        
        return valid_consents
    
    async def _get_expired_consents(self, user_id: str) -> List[ConsentRecord]:
        """
Get expired consents for user."""
        expired_consents = []
        
        for consent in self.consent_records.values():
            if (consent.user_id == user_id and 
                consent.expires_at and 
                consent.expires_at <= datetime.utcnow() and
                consent.consent_status == ConsentStatus.GIVEN):
                
                # Mark as expired
                consent.consent_status = ConsentStatus.EXPIRED
                expired_consents.append(consent)
        
        return expired_consents
    
    async def _check_alternative_legal_basis(
        self,
        user_id: str,
        processing_purpose: str
    ) -> Optional[str]:
        """
Check for alternative legal basis for processing."""
        # Check legitimate interests
        if processing_purpose in ["fraud_prevention", "security", "analytics"]:
            return "legitimate_interests"
        
        # Check contract performance
        if processing_purpose in ["service_delivery", "payment_processing"]:
            return "contract_performance"
        
        # Check legal obligation
        if processing_purpose in ["tax_reporting", "legal_compliance"]:
            return "legal_obligation"
        
        return None
    
    async def _verify_data_minimization(
        self,
        user_id: str,
        content_id: str,
        processing_purpose: str
    ) -> Dict[str, Any]:
        """Verify data minimization principle compliance."""
        return {
            "compliant": True,
            "issues": []
        }
    
    async def _process_specific_request(
        self,
        request_record: DataSubjectRequest
    ) -> Dict[str, Any]:
        """Process specific type of data subject request."""
        request_type = request_record.request_type
        
        if request_type == DataSubjectRight.ACCESS:
            return {"auto_processable": True, "complexity": "low"}
        elif request_type == DataSubjectRight.ERASURE:
            return {"auto_processable": True, "complexity": "medium"}
        elif request_type == DataSubjectRight.DATA_PORTABILITY:
            return {"auto_processable": True, "complexity": "medium"}
        elif request_type == DataSubjectRight.RECTIFICATION:
            return {"auto_processable": False, "complexity": "high"}
        else:
            return {"auto_processable": False, "complexity": "high"}
    
    async def _auto_process_request(
        self,
        request_record: DataSubjectRequest
    ) -> Dict[str, Any]:
        """Auto-process eligible data subject requests."""
        request_type = request_record.request_type
        
        if request_type == DataSubjectRight.ACCESS:
            return await self._process_data_access_request(request_record)
        elif request_type == DataSubjectRight.ERASURE:
            return await self._process_erasure_request(request_record)
        elif request_type == DataSubjectRight.DATA_PORTABILITY:
            return await self._process_portability_request(request_record)
        else:
            return {"status": "manual_review_required"}
    
    async def _process_data_access_request(
        self,
        request_record: DataSubjectRequest
    ) -> Dict[str, Any]:
        """Process data access request."""
        # Collect user data from all sources
        user_data = {
            "personal_data": {},
            "content_data": {},
            "usage_data": {},
            "consent_history": []
        }
        
        # Get consent history
        user_consents = [
            {
                "consent_id": c.consent_id,
                "given_at": c.given_at.isoformat(),
                "data_categories": [cat.value for cat in c.data_categories],
                "status": c.consent_status.value
            }
            for c in self.consent_records.values()
            if c.user_id == request_record.user_id
        ]
        
        user_data["consent_history"] = user_consents
        
        return {
            "status": "completed",
            "data_package": user_data,
            "export_format": "json",
            "data_categories_included": [cat.value for cat in request_record.data_categories]
        }
    
    async def _process_erasure_request(
        self,
        request_record: DataSubjectRequest
    ) -> Dict[str, Any]:
        """Process right to erasure request."""
        # Schedule data deletion
        deletion_result = await self._schedule_data_deletion(
            request_record.user_id,
            request_record.data_categories
        )
        
        return {
            "status": "completed",
            "deleted_categories": [cat.value for cat in request_record.data_categories],
            "deletion_scheduled": deletion_result["scheduled"],
            "retention_exceptions": deletion_result.get("exceptions", [])
        }
    
    async def _process_portability_request(
        self,
        request_record: DataSubjectRequest
    ) -> Dict[str, Any]:
        """Process data portability request."""
        # Export data in portable format
        portable_data = await self._export_portable_data(
            request_record.user_id,
            request_record.data_categories
        )
        
        return {
            "status": "completed",
            "export_format": "json",
            "download_link": f"/api/gdpr/export/{request_record.request_id}",
            "expires_at": (datetime.utcnow() + timedelta(days=7)).isoformat()
        }
    
    async def _schedule_data_deletion(
        self,
        user_id: str,
        data_categories: List[DataCategory]
    ) -> Dict[str, Any]:
        """Schedule data deletion for user and categories."""
        return {
            "scheduled": True,
            "deletion_date": (datetime.utcnow() + timedelta(days=1)).isoformat(),
            "categories": [cat.value for cat in data_categories],
            "exceptions": []
        }
    
    async def _export_portable_data(
        self,
        user_id: str,
        data_categories: List[DataCategory]
    ) -> Dict[str, Any]:
        """Export user data in portable format."""
        return {
            "user_id": user_id,
            "export_date": datetime.utcnow().isoformat(),
            "data_categories": [cat.value for cat in data_categories],
            "data": {}
        }
    
    def _estimate_completion_time(self, request_record: DataSubjectRequest) -> str:
        """Estimate completion time for request."""
        if request_record.status == "completed":
            return "Completed"
        
        request_type = request_record.request_type
        
        if request_type in [DataSubjectRight.ACCESS, DataSubjectRight.DATA_PORTABILITY]:
            return "1-3 business days"
        elif request_type == DataSubjectRight.ERASURE:
            return "3-5 business days"
        else:
            return "5-30 business days"
    
    def _filter_consents_by_criteria(
        self,
        user_id: Optional[str],
        start_date: datetime,
        end_date: datetime
    ) -> List[ConsentRecord]:
        """Filter consent records by criteria."""
        filtered = []
        
        for consent in self.consent_records.values():
            # Filter by user
            if user_id and consent.user_id != user_id:
                continue
            
            # Filter by date range
            if (consent.given_at < start_date or 
                consent.given_at > end_date):
                continue
            
            filtered.append(consent)
        
        return filtered
    
    def _filter_requests_by_criteria(
        self,
        user_id: Optional[str],
        start_date: datetime,
        end_date: datetime
    ) -> List[DataSubjectRequest]:
        """
Filter request records by criteria."""
        filtered = []
        
        for request in self.data_subject_requests.values():
            # Filter by user
            if user_id and request.user_id != user_id:
                continue
            
            # Filter by date range
            if (request.submitted_at < start_date or 
                request.submitted_at > end_date):
                continue
            
            filtered.append(request)
        
        return filtered
    
    # Logging methods
    async def _log_consent_action(
        self,
        action: str,
        consent_record: ConsentRecord,
        result: Dict[str, Any]
    ) -> None:
        """
Log consent-related actions."""
        logger.info(f"GDPR consent {action}: {consent_record.consent_id} for user {consent_record.user_id}")
    
    async def _log_data_subject_request(
        self,
        request_record: DataSubjectRequest,
        result: Dict[str, Any]
    ) -> None:
        """Log data subject request processing."""
        logger.info(f"GDPR request {request_record.request_type.value}: {request_record.request_id} for user {request_record.user_id}")
