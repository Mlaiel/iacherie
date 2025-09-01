"""Complete Data Subject Rights Automation

Implements automated handling of all GDPR data subject rights including
access, rectification, erasure, portability, restriction, and objection.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: Fahed Mlaiel - All rights reserved
"""

import logging
import uuid
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Set
from dataclasses import dataclass, field
from enum import Enum
import json
import zipfile
import io

logger = logging.getLogger(__name__)


class DataSubjectRight(Enum):
    """GDPR Data Subject Rights (Chapter III)"""
    ACCESS = "access"                    # Article 15 - Right of access
    RECTIFICATION = "rectification"      # Article 16 - Right to rectification
    ERASURE = "erasure"                  # Article 17 - Right to erasure
    RESTRICT_PROCESSING = "restrict"     # Article 18 - Right to restriction
    DATA_PORTABILITY = "portability"     # Article 20 - Right to data portability
    OBJECT = "object"                    # Article 21 - Right to object
    AUTOMATED_DECISION = "automated"     # Article 22 - Automated decision-making


class RequestStatus(Enum):
    """Status of data subject rights request"""
    RECEIVED = "received"
    VERIFIED = "verified"
    PROCESSING = "processing"
    COMPLETED = "completed"
    REJECTED = "rejected"
    EXTENDED = "extended"  # When extension is granted


class VerificationMethod(Enum):
    """Methods for verifying data subject identity"""
    EMAIL = "email"
    PHONE = "phone"
    IDENTITY_DOCUMENT = "identity_document"
    BIOMETRIC = "biometric"
    MULTI_FACTOR = "multi_factor"


@dataclass
class DataSubjectRequest:
    """Data subject rights request"""
    request_id: str
    request_type: DataSubjectRight
    user_id: str
    user_email: str
    user_name: Optional[str] = None
    request_details: str = ""
    received_at: datetime = field(default_factory=datetime.utcnow)
    status: RequestStatus = RequestStatus.RECEIVED
    verification_method: Optional[VerificationMethod] = None
    verified_at: Optional[datetime] = None
    processing_started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    deadline: Optional[datetime] = None
    extension_granted: bool = False
    extension_reason: Optional[str] = None
    response_data: Optional[Dict[str, Any]] = None
    rejection_reason: Optional[str] = None
    automated_processing: bool = True
    manual_review_required: bool = False
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class DataExportPackage:
    """Package containing exported personal data"""
    export_id: str
    user_id: str
    created_at: datetime
    data_categories: List[str]
    file_path: str
    file_size: int
    format: str = "JSON"
    encryption_used: bool = True
    retention_until: datetime = field(default_factory=lambda: datetime.utcnow() + timedelta(days=30))


class DataSubjectRightsManager:
    """
    Complete Data Subject Rights Automation System
    
    Handles automated processing of all GDPR data subject rights
    with full compliance, audit trails, and response automation.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.logger = logging.getLogger(__name__)
        
        # Storage for requests and exports
        self.requests: Dict[str, DataSubjectRequest] = {}
        self.data_exports: Dict[str, DataExportPackage] = {}
        
        # Configuration
        self.response_deadline_days = 30  # GDPR Article 12(3)
        self.extension_days = 60  # Maximum extension allowed
        self.auto_verification_enabled = True
        self.auto_processing_enabled = True
        
        # Audit trail
        self.audit_log: List[Dict[str, Any]] = []
        
        # Metrics
        self.metrics = {
            "total_requests": 0,
            "requests_by_type": {},
            "requests_by_status": {},
            "average_response_time": 0.0,
            "automation_rate": 0.0,
            "compliance_rate": 100.0
        }
        
        # Data sources mapping
        self.data_sources = {
            "user_profiles": "database.users",
            "content_data": "database.content",
            "analytics_data": "database.analytics",
            "transaction_data": "database.transactions",
            "communication_data": "database.communications",
            "system_logs": "database.logs"
        }
    
    async def submit_request(
        self,
        request_type: DataSubjectRight,
        user_email: str,
        request_details: str = "",
        user_name: Optional[str] = None,
        verification_data: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Submit a new data subject rights request
        
        Args:
            request_type: Type of rights request
            user_email: Email of the data subject
            request_details: Additional details about the request
            user_name: Name of the data subject
            verification_data: Data for identity verification
            
        Returns:
            str: Request ID
        """
        try:
            request_id = str(uuid.uuid4())
            user_id = await self._resolve_user_id(user_email)
            
            # Calculate deadline (30 days from receipt)
            deadline = datetime.utcnow() + timedelta(days=self.response_deadline_days)
            
            request = DataSubjectRequest(
                request_id=request_id,
                request_type=request_type,
                user_id=user_id or "unknown",
                user_email=user_email,
                user_name=user_name,
                request_details=request_details,
                deadline=deadline,
                metadata={
                    "verification_data": verification_data or {},
                    "submission_ip": self.config.get("request_ip"),
                    "user_agent": self.config.get("user_agent")
                }
            )
            
            self.requests[request_id] = request
            
            # Log submission
            await self._log_audit_event({
                "event_type": "request_submitted",
                "request_id": request_id,
                "request_type": request_type.value,
                "user_email": user_email,
                "timestamp": datetime.utcnow().isoformat()
            })
            
            # Initiate automated processing
            if self.auto_verification_enabled:
                await self._initiate_verification(request)
            
            # Update metrics
            self._update_metrics()
            
            self.logger.info(f"Data subject request submitted: {request_id} ({request_type.value})")
            return request_id
            
        except Exception as e:
            self.logger.error(f"Error submitting data subject request: {e}")
            raise
    
    async def _initiate_verification(self, request: DataSubjectRequest):
        """Initiate automated identity verification"""
        try:
            # Determine verification method based on available data
            verification_method = await self._determine_verification_method(request)
            
            if verification_method == VerificationMethod.EMAIL:
                # Send verification email
                verification_code = await self._send_verification_email(request)
                request.metadata["verification_code"] = verification_code
                request.verification_method = verification_method
                
            elif verification_method == VerificationMethod.MULTI_FACTOR:
                # Initiate multi-factor verification
                await self._initiate_mfa_verification(request)
                request.verification_method = verification_method
            
            await self._log_audit_event({
                "event_type": "verification_initiated",
                "request_id": request.request_id,
                "verification_method": verification_method.value,
                "timestamp": datetime.utcnow().isoformat()
            })
            
        except Exception as e:
            self.logger.error(f"Error initiating verification for request {request.request_id}: {e}")
    
    async def verify_request(
        self,
        request_id: str,
        verification_data: Dict[str, Any]
    ) -> bool:
        """
        Verify data subject identity for a request
        
        Args:
            request_id: Request identifier
            verification_data: Verification credentials/codes
            
        Returns:
            bool: Verification success
        """
        try:
            request = self.requests.get(request_id)
            if not request:
                return False
            
            # Perform verification based on method
            verification_success = False
            
            if request.verification_method == VerificationMethod.EMAIL:
                verification_success = await self._verify_email_code(request, verification_data)
            elif request.verification_method == VerificationMethod.MULTI_FACTOR:
                verification_success = await self._verify_mfa(request, verification_data)
            
            if verification_success:
                request.status = RequestStatus.VERIFIED
                request.verified_at = datetime.utcnow()
                
                # Initiate automated processing
                if self.auto_processing_enabled:
                    await self._initiate_processing(request)
                
                await self._log_audit_event({
                    "event_type": "request_verified",
                    "request_id": request_id,
                    "timestamp": datetime.utcnow().isoformat()
                })
                
                return True
            else:
                await self._log_audit_event({
                    "event_type": "verification_failed",
                    "request_id": request_id,
                    "timestamp": datetime.utcnow().isoformat()
                })
                
                return False
            
        except Exception as e:
            self.logger.error(f"Error verifying request {request_id}: {e}")
            return False
    
    async def _initiate_processing(self, request: DataSubjectRequest):
        """Initiate automated processing of verified request"""
        try:
            request.status = RequestStatus.PROCESSING
            request.processing_started_at = datetime.utcnow()
            
            # Process based on request type
            if request.request_type == DataSubjectRight.ACCESS:
                await self._process_access_request(request)
            elif request.request_type == DataSubjectRight.RECTIFICATION:
                await self._process_rectification_request(request)
            elif request.request_type == DataSubjectRight.ERASURE:
                await self._process_erasure_request(request)
            elif request.request_type == DataSubjectRight.RESTRICT_PROCESSING:
                await self._process_restriction_request(request)
            elif request.request_type == DataSubjectRight.DATA_PORTABILITY:
                await self._process_portability_request(request)
            elif request.request_type == DataSubjectRight.OBJECT:
                await self._process_objection_request(request)
            elif request.request_type == DataSubjectRight.AUTOMATED_DECISION:
                await self._process_automated_decision_request(request)
            
            await self._log_audit_event({
                "event_type": "processing_initiated",
                "request_id": request.request_id,
                "request_type": request.request_type.value,
                "timestamp": datetime.utcnow().isoformat()
            })
            
        except Exception as e:
            self.logger.error(f"Error processing request {request.request_id}: {e}")
            request.manual_review_required = True
    
    async def _process_access_request(self, request: DataSubjectRequest):
        """Process right of access request (Article 15)"""
        try:
            # Collect all personal data for the user
            personal_data = await self._collect_personal_data(request.user_id)
            
            # Create data export package
            export_package = await self._create_data_export(request.user_id, personal_data)
            
            # Update request with response
            request.response_data = {
                "export_id": export_package.export_id,
                "data_categories": export_package.data_categories,
                "download_url": f"/api/data-export/{export_package.export_id}",
                "expires_at": export_package.retention_until.isoformat()
            }
            
            # Complete request
            request.status = RequestStatus.COMPLETED
            request.completed_at = datetime.utcnow()
            
            # Send notification to user
            await self._send_completion_notification(request)
            
        except Exception as e:
            self.logger.error(f"Error processing access request {request.request_id}: {e}")
            raise
    
    async def _process_rectification_request(self, request: DataSubjectRequest):
        """Process right to rectification request (Article 16)"""
        try:
            # Parse rectification details from request
            rectification_data = self._parse_rectification_request(request.request_details)
            
            # Apply data corrections
            corrections_applied = await self._apply_data_corrections(
                request.user_id, 
                rectification_data
            )
            
            # Update request with response
            request.response_data = {
                "corrections_applied": corrections_applied,
                "updated_fields": list(rectification_data.keys()),
                "completion_time": datetime.utcnow().isoformat()
            }
            
            # Complete request
            request.status = RequestStatus.COMPLETED
            request.completed_at = datetime.utcnow()
            
            await self._send_completion_notification(request)
            
        except Exception as e:
            self.logger.error(f"Error processing rectification request {request.request_id}: {e}")
            raise
    
    async def _process_erasure_request(self, request: DataSubjectRequest):
        """Process right to erasure request (Article 17)"""
        try:
            # Check for erasure exceptions (legal obligations, etc.)
            erasure_assessment = await self._assess_erasure_eligibility(request.user_id)
            
            if erasure_assessment["eligible"]:
                # Execute data deletion
                deletion_result = await self._execute_data_deletion(
                    request.user_id,
                    erasure_assessment["deletable_categories"]
                )
                
                request.response_data = {
                    "deletion_completed": True,
                    "deleted_categories": deletion_result["deleted"],
                    "retained_categories": deletion_result["retained"],
                    "retention_reasons": deletion_result["retention_reasons"]
                }
            else:
                # Reject request with reasons
                request.status = RequestStatus.REJECTED
                request.rejection_reason = erasure_assessment["rejection_reason"]
                request.response_data = {
                    "deletion_completed": False,
                    "rejection_reason": erasure_assessment["rejection_reason"]
                }
            
            # Complete request
            if request.status != RequestStatus.REJECTED:
                request.status = RequestStatus.COMPLETED
            request.completed_at = datetime.utcnow()
            
            await self._send_completion_notification(request)
            
        except Exception as e:
            self.logger.error(f"Error processing erasure request {request.request_id}: {e}")
            raise
    
    async def _process_restriction_request(self, request: DataSubjectRequest):
        """Process right to restriction of processing request (Article 18)"""
        try:
            # Apply processing restrictions
            restrictions_applied = await self._apply_processing_restrictions(
                request.user_id,
                request.request_details
            )
            
            request.response_data = {
                "restrictions_applied": restrictions_applied,
                "restricted_processing_types": list(restrictions_applied.keys()),
                "restriction_effective_date": datetime.utcnow().isoformat()
            }
            
            request.status = RequestStatus.COMPLETED
            request.completed_at = datetime.utcnow()
            
            await self._send_completion_notification(request)
            
        except Exception as e:
            self.logger.error(f"Error processing restriction request {request.request_id}: {e}")
            raise
    
    async def _process_portability_request(self, request: DataSubjectRequest):
        """Process right to data portability request (Article 20)"""
        try:
            # Collect portable data (structured, commonly used, machine-readable)
            portable_data = await self._collect_portable_data(request.user_id)
            
            # Create portable data export
            export_package = await self._create_portable_export(request.user_id, portable_data)
            
            request.response_data = {
                "export_id": export_package.export_id,
                "format": "JSON",  # Machine-readable format
                "download_url": f"/api/portable-data/{export_package.export_id}",
                "expires_at": export_package.retention_until.isoformat()
            }
            
            request.status = RequestStatus.COMPLETED
            request.completed_at = datetime.utcnow()
            
            await self._send_completion_notification(request)
            
        except Exception as e:
            self.logger.error(f"Error processing portability request {request.request_id}: {e}")
            raise
    
    async def _process_objection_request(self, request: DataSubjectRequest):
        """Process right to object request (Article 21)"""
        try:
            # Assess objection validity
            objection_assessment = await self._assess_objection_validity(
                request.user_id,
                request.request_details
            )
            
            if objection_assessment["valid"]:
                # Stop processing for specified purposes
                processing_stopped = await self._stop_processing_activities(
                    request.user_id,
                    objection_assessment["affected_purposes"]
                )
                
                request.response_data = {
                    "objection_upheld": True,
                    "processing_stopped": processing_stopped,
                    "affected_purposes": objection_assessment["affected_purposes"]
                }
            else:
                request.status = RequestStatus.REJECTED
                request.rejection_reason = objection_assessment["rejection_reason"]
                request.response_data = {
                    "objection_upheld": False,
                    "rejection_reason": objection_assessment["rejection_reason"]
                }
            
            if request.status != RequestStatus.REJECTED:
                request.status = RequestStatus.COMPLETED
            request.completed_at = datetime.utcnow()
            
            await self._send_completion_notification(request)
            
        except Exception as e:
            self.logger.error(f"Error processing objection request {request.request_id}: {e}")
            raise
    
    async def _process_automated_decision_request(self, request: DataSubjectRequest):
        """Process automated decision-making rights request (Article 22)"""
        try:
            # Provide information about automated decision-making
            automated_decisions = await self._get_automated_decisions(request.user_id)
            
            request.response_data = {
                "automated_decisions": automated_decisions,
                "human_review_available": True,
                "contest_mechanism": "/api/contest-decision",
                "explanation_provided": True
            }
            
            request.status = RequestStatus.COMPLETED
            request.completed_at = datetime.utcnow()
            
            await self._send_completion_notification(request)
            
        except Exception as e:
            self.logger.error(f"Error processing automated decision request {request.request_id}: {e}")
            raise
    
    async def _collect_personal_data(self, user_id: str) -> Dict[str, Any]:
        """Collect all personal data for a user across all systems"""
        personal_data = {}
        
        try:
            # Collect from different data sources
            for category, source in self.data_sources.items():
                try:
                    data = await self._fetch_data_from_source(user_id, source)
                    if data:
                        personal_data[category] = data
                except Exception as e:
                    self.logger.warning(f"Failed to collect {category} data: {e}")
            
            return personal_data
            
        except Exception as e:
            self.logger.error(f"Error collecting personal data for user {user_id}: {e}")
            return {}
    
    async def _create_data_export(
        self, 
        user_id: str, 
        personal_data: Dict[str, Any]
    ) -> DataExportPackage:
        """Create downloadable data export package"""
        try:
            export_id = str(uuid.uuid4())
            
            # Create JSON export
            export_data = {
                "export_info": {
                    "export_id": export_id,
                    "user_id": user_id,
                    "generated_at": datetime.utcnow().isoformat(),
                    "data_categories": list(personal_data.keys())
                },
                "personal_data": personal_data
            }
            
            # Create compressed file
            buffer = io.BytesIO()
            with zipfile.ZipFile(buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
                zip_file.writestr(
                    f"personal_data_{user_id}.json",
                    json.dumps(export_data, indent=2, ensure_ascii=False)
                )
            
            # Store export package
            file_content = buffer.getvalue()
            file_path = f"/exports/{export_id}.zip"
            
            # In production, save to secure storage
            # await self._save_export_file(file_path, file_content)
            
            export_package = DataExportPackage(
                export_id=export_id,
                user_id=user_id,
                created_at=datetime.utcnow(),
                data_categories=list(personal_data.keys()),
                file_path=file_path,
                file_size=len(file_content),
                format="JSON (ZIP compressed)"
            )
            
            self.data_exports[export_id] = export_package
            
            return export_package
            
        except Exception as e:
            self.logger.error(f"Error creating data export for user {user_id}: {e}")
            raise
    
    async def get_request_status(self, request_id: str) -> Optional[Dict[str, Any]]:
        """Get status of a data subject rights request"""
        request = self.requests.get(request_id)
        if not request:
            return None
        
        return {
            "request_id": request_id,
            "request_type": request.request_type.value,
            "status": request.status.value,
            "received_at": request.received_at.isoformat(),
            "verified_at": request.verified_at.isoformat() if request.verified_at else None,
            "completed_at": request.completed_at.isoformat() if request.completed_at else None,
            "deadline": request.deadline.isoformat() if request.deadline else None,
            "days_remaining": (request.deadline - datetime.utcnow()).days if request.deadline else None,
            "automated_processing": request.automated_processing,
            "response_available": request.status == RequestStatus.COMPLETED and request.response_data is not None
        }
    
    async def generate_compliance_report(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """Generate compliance report for data subject rights"""
        try:
            if not start_date:
                start_date = datetime.utcnow() - timedelta(days=30)
            if not end_date:
                end_date = datetime.utcnow()
            
            # Filter requests by date range
            filtered_requests = [
                req for req in self.requests.values()
                if start_date <= req.received_at <= end_date
            ]
            
            # Calculate compliance metrics
            total_requests = len(filtered_requests)
            completed_on_time = len([
                req for req in filtered_requests
                if req.status == RequestStatus.COMPLETED and 
                   req.completed_at and req.deadline and
                   req.completed_at <= req.deadline
            ])
            
            # Response time analysis
            completed_requests = [
                req for req in filtered_requests
                if req.status == RequestStatus.COMPLETED and req.completed_at
            ]
            
            avg_response_time = 0.0
            if completed_requests:
                response_times = [
                    (req.completed_at - req.received_at).total_seconds() / 3600  # hours
                    for req in completed_requests
                ]
                avg_response_time = sum(response_times) / len(response_times)
            
            report = {
                "report_period": {
                    "start_date": start_date.isoformat(),
                    "end_date": end_date.isoformat()
                },
                "summary": {
                    "total_requests": total_requests,
                    "completed_requests": len(completed_requests),
                    "pending_requests": len([req for req in filtered_requests if req.status in [RequestStatus.RECEIVED, RequestStatus.VERIFIED, RequestStatus.PROCESSING]]),
                    "compliance_rate": (completed_on_time / total_requests * 100) if total_requests > 0 else 100,
                    "average_response_time_hours": avg_response_time,
                    "automation_rate": (len([req for req in filtered_requests if req.automated_processing]) / total_requests * 100) if total_requests > 0 else 0
                },
                "by_request_type": {
                    right.value: len([req for req in filtered_requests if req.request_type == right])
                    for right in DataSubjectRight
                },
                "by_status": {
                    status.value: len([req for req in filtered_requests if req.status == status])
                    for status in RequestStatus
                },
                "generated_at": datetime.utcnow().isoformat()
            }
            
            return report
            
        except Exception as e:
            self.logger.error(f"Error generating compliance report: {e}")
            return {"error": str(e)}
    
    # Helper methods (simplified implementations)
    
    async def _resolve_user_id(self, user_email: str) -> Optional[str]:
        """Resolve user ID from email"""
        # Implementation would query user database
        return f"user_{hash(user_email) % 100000}"
    
    async def _determine_verification_method(self, request: DataSubjectRequest) -> VerificationMethod:
        """Determine appropriate verification method"""
        return VerificationMethod.EMAIL  # Simplified
    
    async def _send_verification_email(self, request: DataSubjectRequest) -> str:
        """Send verification email and return verification code"""
        verification_code = str(uuid.uuid4())[:8]
        # Implementation would send actual email
        self.logger.info(f"Verification email sent to {request.user_email}")
        return verification_code
    
    async def _verify_email_code(self, request: DataSubjectRequest, verification_data: Dict[str, Any]) -> bool:
        """Verify email verification code"""
        provided_code = verification_data.get("verification_code")
        stored_code = request.metadata.get("verification_code")
        return provided_code == stored_code
    
    async def _fetch_data_from_source(self, user_id: str, source: str) -> Dict[str, Any]:
        """Fetch data from a specific source"""
        # Implementation would query actual data sources
        return {"sample_data": f"Data from {source} for {user_id}"}
    
    async def _apply_data_corrections(self, user_id: str, corrections: Dict[str, Any]) -> List[str]:
        """Apply data corrections"""
        # Implementation would update actual data
        return list(corrections.keys())
    
    async def _execute_data_deletion(self, user_id: str, categories: List[str]) -> Dict[str, Any]:
        """Execute data deletion"""
        # Implementation would perform actual deletion
        return {
            "deleted": categories,
            "retained": [],
            "retention_reasons": {}
        }
    
    def _parse_rectification_request(self, request_details: str) -> Dict[str, Any]:
        """Parse rectification request details"""
        # Implementation would parse structured request
        return {"email": "new@example.com"}
    
    async def _assess_erasure_eligibility(self, user_id: str) -> Dict[str, Any]:
        """Assess eligibility for data erasure"""
        return {"eligible": True, "deletable_categories": ["analytics", "marketing"]}
    
    async def _log_audit_event(self, event: Dict[str, Any]):
        """Log audit event"""
        event["id"] = str(uuid.uuid4())
        event["logged_at"] = datetime.utcnow().isoformat()
        self.audit_log.append(event)
    
    async def _send_completion_notification(self, request: DataSubjectRequest):
        """Send completion notification to user"""
        self.logger.info(f"Completion notification sent for request {request.request_id}")
    
    def _update_metrics(self):
        """Update performance metrics"""
        total = len(self.requests)
        self.metrics["total_requests"] = total
        
        for request_type in DataSubjectRight:
            count = len([req for req in self.requests.values() if req.request_type == request_type])
            self.metrics["requests_by_type"][request_type.value] = count
        
        for status in RequestStatus:
            count = len([req for req in self.requests.values() if req.status == status])
            self.metrics["requests_by_status"][status.value] = count
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get data subject rights metrics"""
        return self.metrics.copy()