"""
Ainflue Platform - DMCA Compliance Tracker
==========================================

Comprehensive DMCA compliance monitoring system for tracking takedown
requests, safe harbor provisions, counter-notifications, and legal
compliance across digital content platforms.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Set
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
import uuid
import json
from collections import defaultdict, deque

logger = logging.getLogger(__name__)

class DMCARequestType(Enum):
    """Types of DMCA requests."""
    TAKEDOWN_NOTICE = "takedown_notice"
    COUNTER_NOTIFICATION = "counter_notification"
    REPEAT_INFRINGER = "repeat_infringer"
    SAFE_HARBOR_CLAIM = "safe_harbor_claim"
    SUBPOENA_REQUEST = "subpoena_request"
    REINSTATEMENT_REQUEST = "reinstatement_request"

class DMCAStatus(Enum):
    """DMCA request processing status."""
    RECEIVED = "received"
    UNDER_REVIEW = "under_review"
    VALID = "valid"
    INVALID = "invalid"
    PROCESSED = "processed"
    COMPLIED = "complied"
    REJECTED = "rejected"
    DISPUTED = "disputed"
    EXPIRED = "expired"

class ComplianceLevel(Enum):
    """DMCA compliance levels."""
    FULL_COMPLIANCE = "full_compliance"
    PARTIAL_COMPLIANCE = "partial_compliance"
    NON_COMPLIANCE = "non_compliance"
    SAFE_HARBOR_PROTECTED = "safe_harbor_protected"
    UNDER_INVESTIGATION = "under_investigation"

@dataclass
class DMCARequest:
    """DMCA request record."""
    request_id: str
    request_type: DMCARequestType
    content_id: str
    requestor_name: str
    requestor_email: str
    requestor_organization: Optional[str]
    infringing_urls: List[str]
    original_work_description: str
    good_faith_statement: bool
    accuracy_statement: bool
    authorization_statement: bool
    digital_signature: str
    submission_method: str  # email, web_form, api
    status: DMCAStatus
    priority_level: str  # high, medium, low
    response_deadline: datetime
    processing_notes: str
    compliance_score: float
    metadata: Dict[str, Any] = field(default_factory=dict)
    submitted_at: datetime = field(default_factory=datetime.utcnow)
    processed_at: Optional[datetime] = None

@dataclass
class ComplianceAudit:
    """DMCA compliance audit record."""
    audit_id: str
    audit_period_start: datetime
    audit_period_end: datetime
    total_requests: int
    valid_requests: int
    processed_requests: int
    complied_requests: int
    response_time_avg_hours: float
    compliance_rate: float
    compliance_level: ComplianceLevel
    violations: List[str]
    recommendations: List[str]
    legal_risk_assessment: str
    audit_notes: str
    auditor: str
    created_at: datetime = field(default_factory=datetime.utcnow)

@dataclass
class SafeHarborAssessment:
    """Safe harbor provision assessment."""
    assessment_id: str
    platform: str
    has_dmca_agent: bool
    agent_registered_with_copyright_office: bool
    has_notice_takedown_procedure: bool
    has_repeat_infringer_policy: bool
    responds_to_takedown_notices: bool
    removes_content_expeditiously: bool
    has_no_actual_knowledge: bool
    safe_harbor_eligible: bool
    compliance_gaps: List[str]
    risk_level: str  # low, medium, high
    assessment_date: datetime = field(default_factory=datetime.utcnow)

class DMCAComplianceTracker:
    """
    Enterprise DMCA compliance tracking and monitoring system.
    
    Features:
    - Comprehensive DMCA request processing and tracking
    - Automated compliance assessment and scoring
    - Safe harbor provision monitoring
    - Response time tracking and deadline management
    - Legal risk assessment and reporting
    - Integration with content protection systems
    - Audit trail and documentation management
    """
    
    def __init__(self, config -> None: Optional[Dict[str, Any]] = None) -> None:
        self.config = config or {}
        self.dmca_requests: deque = deque(maxlen=50000)
        self.compliance_audits: List[ComplianceAudit] = []
        self.safe_harbor_assessments: List[SafeHarborAssessment] = []
        self.dmca_agent_info = self._initialize_dmca_agent_info()
        self.compliance_thresholds = self._initialize_compliance_thresholds()
        self.legal_templates = self._initialize_legal_templates()
        
        logger.info("DMCA Compliance Tracker initialized")
    
    def _initialize_dmca_agent_info(self) -> Dict[str, Any]:
        """Initialize DMCA agent information."""
        return {
            'agent_name': 'Ainflue DMCA Agent',
            'organization': 'Ainflue Platform',
            'address': '1234 Tech Street, San Francisco, CA 94105',
            'phone': '+1 (555) 123-4567',
            'email': 'dmca@ainflue.com',
            'registered_with_copyright_office': True,
            'registration_date': datetime(2024, 1, 1),
            'public_contact_info': 'https://ainflue.com/dmca-agent'
        }
    
    def _initialize_compliance_thresholds(self) -> Dict[str, Any]:
        """Initialize compliance thresholds and requirements."""
        return {
            'response_time_hours': {
                'target': 24,
                'warning': 48,
                'violation': 72
            },
            'compliance_rates': {
                'excellent': 0.95,
                'good': 0.85,
                'acceptable': 0.75,
                'poor': 0.60
            },
            'safe_harbor_requirements': {
                'dmca_agent_registered': True,
                'notice_takedown_procedure': True,
                'repeat_infringer_policy': True,
                'expeditious_removal': True,
                'no_actual_knowledge': True
            },
            'audit_frequency_days': 90,
            'legal_review_threshold': 0.70  # Compliance rate below this triggers legal review
        }
    
    def _initialize_legal_templates(self) -> Dict[str, str]:
        """Initialize legal response templates."""
        return {
            'takedown_acknowledgment': """
            Dear {requestor_name},
            
            We have received your DMCA takedown notice dated {submission_date} regarding alleged copyright infringement.
            
            Notice ID: {request_id}
            Content: {content_description}
            
            We are reviewing your request and will respond within the timeframe required by law.
            
            Sincerely,
            Ainflue DMCA Agent
            """,
            'content_removed': """
            Dear {requestor_name},
            
            We have removed the content identified in your DMCA takedown notice.
            
            Notice ID: {request_id}
            URLs Removed: {removed_urls}
            Removal Date: {removal_date}
            
            The content has been disabled and the uploader has been notified.
            
            Sincerely,
            Ainflue DMCA Agent
            """,
            'invalid_notice': """
            Dear {requestor_name},
            
            We have reviewed your DMCA notice but found it to be incomplete or invalid.
            
            Notice ID: {request_id}
            Issues Identified: {validation_issues}
            
            Please resubmit with the required information.
            
            Sincerely,
            Ainflue DMCA Agent
            """
        }
    
    async def submit_dmca_request(self, request_type: DMCARequestType,
                                content_id: str, requestor_name: str,
                                requestor_email: str, infringing_urls: List[str],
                                original_work_description: str,
                                digital_signature: str,
                                submission_method: str = "web_form",
                                metadata: Optional[Dict[str, Any]] = None) -> str:
        """Submit a new DMCA request for processing."""
        request_id = str(uuid.uuid4())
        
        # Calculate response deadline based on request type
        response_deadline = self._calculate_response_deadline(request_type)
        
        # Determine priority level
        priority_level = self._determine_priority_level(request_type, metadata or {})
        
        dmca_request = DMCARequest(
            request_id=request_id,
            request_type=request_type,
            content_id=content_id,
            requestor_name=requestor_name,
            requestor_email=requestor_email,
            requestor_organization=metadata.get('organization') if metadata else None,
            infringing_urls=infringing_urls,
            original_work_description=original_work_description,
            good_faith_statement=metadata.get('good_faith_statement', False) if metadata else False,
            accuracy_statement=metadata.get('accuracy_statement', False) if metadata else False,
            authorization_statement=metadata.get('authorization_statement', False) if metadata else False,
            digital_signature=digital_signature,
            submission_method=submission_method,
            status=DMCAStatus.RECEIVED,
            priority_level=priority_level,
            response_deadline=response_deadline,
            processing_notes="",
            compliance_score=0.0,
            metadata=metadata or {}
        )
        
        self.dmca_requests.append(dmca_request)
        
        # Validate request
        await self._validate_dmca_request(dmca_request)
        
        # Send acknowledgment
        await self._send_acknowledgment(dmca_request)
        
        # Schedule processing if high priority
        if priority_level == "high":
            await self._schedule_priority_processing(dmca_request)
        
        logger.info(f"DMCA request submitted: {request_id} "
                   f"({request_type.value}, priority: {priority_level})")
        
        return request_id
    
    def _calculate_response_deadline(self, request_type: DMCARequestType) -> datetime:
        """Calculate response deadline based on request type."""
        base_hours = {
            DMCARequestType.TAKEDOWN_NOTICE: 24,
            DMCARequestType.COUNTER_NOTIFICATION: 72,
            DMCARequestType.REPEAT_INFRINGER: 48,
            DMCARequestType.SAFE_HARBOR_CLAIM: 72,
            DMCARequestType.SUBPOENA_REQUEST: 168,  # 7 days
            DMCARequestType.REINSTATEMENT_REQUEST: 48
        }
        
        hours = base_hours.get(request_type, 24)
        return datetime.utcnow() + timedelta(hours=hours)
    
    def _determine_priority_level(self, request_type: DMCARequestType,
                                metadata: Dict[str, Any]) -> str:
        """Determine priority level for DMCA request."""
        # High priority criteria
        if (request_type == DMCARequestType.SUBPOENA_REQUEST or
            metadata.get('commercial_harm', False) or
            metadata.get('repeat_infringer', False)):
            return "high"
        
        # Medium priority criteria
        if (request_type in [DMCARequestType.TAKEDOWN_NOTICE, DMCARequestType.COUNTER_NOTIFICATION] or
            metadata.get('verified_rights_holder', False)):
            return "medium"
        
        return "low"
    
    async def _validate_dmca_request(self, dmca_request -> None: DMCARequest) -> None:
        """Validate DMCA request for completeness and compliance."""
        dmca_request.status = DMCAStatus.UNDER_REVIEW
        validation_issues = []
        
        # Required field validation
        if not dmca_request.requestor_name:
            validation_issues.append("Missing requestor name")
        
        if not dmca_request.requestor_email or "@" not in dmca_request.requestor_email:
            validation_issues.append("Invalid requestor email")
        
        if not dmca_request.infringing_urls:
            validation_issues.append("No infringing URLs provided")
        
        if not dmca_request.original_work_description:
            validation_issues.append("Missing original work description")
        
        if not dmca_request.digital_signature:
            validation_issues.append("Missing digital signature")
        
        # DMCA-specific requirements for takedown notices
        if dmca_request.request_type == DMCARequestType.TAKEDOWN_NOTICE:
            if not dmca_request.good_faith_statement:
                validation_issues.append("Missing good faith statement")
            
            if not dmca_request.accuracy_statement:
                validation_issues.append("Missing accuracy statement")
            
            if not dmca_request.authorization_statement:
                validation_issues.append("Missing authorization statement")
        
        # Calculate compliance score
        total_requirements = 8  # Total validation points
        passed_requirements = total_requirements - len(validation_issues)
        dmca_request.compliance_score = passed_requirements / total_requirements
        
        # Update status based on validation
        if validation_issues:
            dmca_request.status = DMCAStatus.INVALID
            dmca_request.processing_notes = "; ".join(validation_issues)
            
            # Send invalid notice response
            await self._send_invalid_notice_response(dmca_request, validation_issues)
        else:
            dmca_request.status = DMCAStatus.VALID
            dmca_request.processing_notes = "Request validated successfully"
    
    async def _send_acknowledgment(self, dmca_request -> None: DMCARequest) -> None:
        """Send acknowledgment to requestor."""
        template = self.legal_templates['takedown_acknowledgment']
        
        message = template.format(
            requestor_name=dmca_request.requestor_name,
            submission_date=dmca_request.submitted_at.strftime('%Y-%m-%d'),
            request_id=dmca_request.request_id,
            content_description=dmca_request.original_work_description[:100] + "..."
        )
        
        # Simulate sending email
        logger.info(f"Acknowledgment sent for DMCA request {dmca_request.request_id}")
    
    async def _send_invalid_notice_response(self, dmca_request -> None: DMCARequest,
                                          validation_issues -> None: List[str]) -> None:
        """Send response for invalid DMCA notice."""
        template = self.legal_templates['invalid_notice']
        
        message = template.format(
            requestor_name=dmca_request.requestor_name,
            request_id=dmca_request.request_id,
            validation_issues="; ".join(validation_issues)
        )
        
        # Simulate sending email
        logger.warning(f"Invalid notice response sent for DMCA request {dmca_request.request_id}")
    
    async def _schedule_priority_processing(self, dmca_request -> None: DMCARequest) -> None:
        """Schedule priority processing for high-priority requests."""
        # Simulate priority queue processing
        logger.info(f"Priority processing scheduled for DMCA request {dmca_request.request_id}")
        
        # Auto-process if clear-cut case
        if dmca_request.compliance_score >= 0.95:
            await self._auto_process_takedown(dmca_request)
    
    async def _auto_process_takedown(self, dmca_request -> None: DMCARequest) -> None:
        """Automatically process clear-cut takedown requests."""
        if dmca_request.request_type != DMCARequestType.TAKEDOWN_NOTICE:
            return
        
        # Simulate content removal
        dmca_request.status = DMCAStatus.PROCESSED
        dmca_request.processed_at = datetime.utcnow()
        dmca_request.processing_notes += "; Auto-processed due to high compliance score"
        
        # Send removal confirmation
        await self._send_removal_confirmation(dmca_request)
        
        logger.info(f"Auto-processed takedown request {dmca_request.request_id}")
    
    async def _send_removal_confirmation(self, dmca_request -> None: DMCARequest) -> None:
        """Send content removal confirmation."""
        template = self.legal_templates['content_removed']
        
        message = template.format(
            requestor_name=dmca_request.requestor_name,
            request_id=dmca_request.request_id,
            removed_urls="; ".join(dmca_request.infringing_urls),
            removal_date=datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')
        )
        
        # Simulate sending email
        logger.info(f"Removal confirmation sent for DMCA request {dmca_request.request_id}")
    
    async def process_dmca_request(self, request_id: str, action: str,
                                 processing_notes: Optional[str] = None) -> bool:
        """Manually process DMCA request."""
        dmca_request = self._get_request_by_id(request_id)
        if not dmca_request:
            return False
        
        old_status = dmca_request.status
        
        if action == "approve":
            dmca_request.status = DMCAStatus.PROCESSED
            await self._send_removal_confirmation(dmca_request)
        elif action == "reject":
            dmca_request.status = DMCAStatus.REJECTED
        elif action == "dispute":
            dmca_request.status = DMCAStatus.DISPUTED
        
        dmca_request.processed_at = datetime.utcnow()
        if processing_notes:
            dmca_request.processing_notes += f"; Manual processing: {processing_notes}"
        
        logger.info(f"DMCA request {request_id} processed: {old_status.value} → {dmca_request.status.value}")
        return True
    
    def _get_request_by_id(self, request_id: str) -> Optional[DMCARequest]:
        """Get DMCA request by ID."""
        for request in self.dmca_requests:
            if request.request_id == request_id:
                return request
        return None
    
    async def conduct_compliance_audit(self, audit_period_days: int = 90) -> str:
        """Conduct comprehensive DMCA compliance audit."""
        audit_id = str(uuid.uuid4())
        audit_end = datetime.utcnow()
        audit_start = audit_end - timedelta(days=audit_period_days)
        
        # Get requests in audit period
        audit_requests = [
            request for request in self.dmca_requests
            if audit_start <= request.submitted_at <= audit_end
        ]
        
        if not audit_requests:
            logger.warning(f"No DMCA requests found for audit period")
            return audit_id
        
        # Calculate audit metrics
        total_requests = len(audit_requests)
        valid_requests = len([r for r in audit_requests if r.status != DMCAStatus.INVALID])
        processed_requests = len([r for r in audit_requests if r.processed_at is not None])
        complied_requests = len([r for r in audit_requests if r.status == DMCAStatus.PROCESSED])
        
        # Calculate response times
        response_times = []
        for request in audit_requests:
            if request.processed_at:
                response_time = (request.processed_at - request.submitted_at).total_seconds() / 3600
                response_times.append(response_time)
        
        avg_response_time = sum(response_times) / len(response_times) if response_times else 0
        
        # Calculate compliance rate
        compliance_rate = complied_requests / total_requests if total_requests > 0 else 0
        
        # Determine compliance level
        compliance_level = self._determine_compliance_level(compliance_rate, avg_response_time)
        
        # Identify violations and recommendations
        violations = self._identify_compliance_violations(audit_requests, avg_response_time)
        recommendations = self._generate_compliance_recommendations(violations, compliance_rate)
        
        # Assess legal risk
        legal_risk = self._assess_legal_risk(compliance_rate, violations)
        
        audit = ComplianceAudit(
            audit_id=audit_id,
            audit_period_start=audit_start,
            audit_period_end=audit_end,
            total_requests=total_requests,
            valid_requests=valid_requests,
            processed_requests=processed_requests,
            complied_requests=complied_requests,
            response_time_avg_hours=avg_response_time,
            compliance_rate=compliance_rate,
            compliance_level=compliance_level,
            violations=violations,
            recommendations=recommendations,
            legal_risk_assessment=legal_risk,
            audit_notes=f"Automated compliance audit for {audit_period_days}-day period",
            auditor="Automated Compliance System"
        )
        
        self.compliance_audits.append(audit)
        
        logger.info(f"Compliance audit completed: {audit_id} "
                   f"(compliance_rate={compliance_rate:.3f}, level={compliance_level.value})")
        
        return audit_id
    
    def _determine_compliance_level(self, compliance_rate: float,
                                  avg_response_time: float) -> ComplianceLevel:
        """Determine overall compliance level."""
        thresholds = self.compliance_thresholds['compliance_rates']
        response_threshold = self.compliance_thresholds['response_time_hours']['violation']
        
        if compliance_rate >= thresholds['excellent'] and avg_response_time <= response_threshold:
            return ComplianceLevel.FULL_COMPLIANCE
        elif compliance_rate >= thresholds['good']:
            return ComplianceLevel.PARTIAL_COMPLIANCE
        elif compliance_rate >= thresholds['acceptable']:
            return ComplianceLevel.PARTIAL_COMPLIANCE
        else:
            return ComplianceLevel.NON_COMPLIANCE
    
    def _identify_compliance_violations(self, audit_requests: List[DMCARequest],
                                      avg_response_time: float) -> List[str]:
        """Identify compliance violations."""
        violations = []
        thresholds = self.compliance_thresholds
        
        # Response time violations
        if avg_response_time > thresholds['response_time_hours']['violation']:
            violations.append(f"Average response time ({avg_response_time:.1f}h) exceeds 72-hour requirement")
        
        # Processing violations
        overdue_requests = [
            r for r in audit_requests
            if r.status in [DMCAStatus.RECEIVED, DMCAStatus.UNDER_REVIEW, DMCAStatus.VALID]
            and datetime.utcnow() > r.response_deadline
        ]
        
        if overdue_requests:
            violations.append(f"{len(overdue_requests)} requests past response deadline")
        
        # Invalid request rate
        invalid_rate = len([r for r in audit_requests if r.status == DMCAStatus.INVALID]) / len(audit_requests)
        if invalid_rate > 0.20:  # More than 20% invalid
            violations.append(f"High invalid request rate ({invalid_rate:.1%})")
        
        return violations
    
    def _generate_compliance_recommendations(self, violations: List[str],
                                           compliance_rate: float) -> List[str]:
        """Generate compliance improvement recommendations."""
        recommendations = []
        
        if compliance_rate < self.compliance_thresholds['compliance_rates']['good']:
            recommendations.append("Implement automated processing for clear-cut cases")
            recommendations.append("Increase staffing for DMCA request processing")
        
        if any("response time" in violation.lower() for violation in violations):
            recommendations.append("Implement priority queuing system")
            recommendations.append("Set up automated acknowledgment system")
        
        if any("invalid request" in violation.lower() for violation in violations):
            recommendations.append("Improve DMCA request submission form validation")
            recommendations.append("Provide clearer guidance for requestors")
        
        recommendations.append("Conduct regular staff training on DMCA procedures")
        recommendations.append("Review and update DMCA policies quarterly")
        
        return recommendations[:5]  # Limit to top 5
    
    def _assess_legal_risk(self, compliance_rate: float, violations: List[str]) -> str:
        """Assess legal risk based on compliance metrics."""
        if compliance_rate >= 0.95 and not violations:
            return "Low - Excellent compliance with DMCA requirements"
        elif compliance_rate >= 0.85:
            return "Medium - Good compliance but room for improvement"
        elif compliance_rate >= 0.70:
            return "High - Compliance issues may affect safe harbor protection"
        else:
            return "Critical - Poor compliance poses significant legal risk"
    
    async def assess_safe_harbor_eligibility(self, platform: str) -> str:
        """Assess safe harbor eligibility for platform."""
        assessment_id = str(uuid.uuid4())
        
        # Check safe harbor requirements
        requirements = self.compliance_thresholds['safe_harbor_requirements']
        
        has_dmca_agent = bool(self.dmca_agent_info.get('agent_name'))
        agent_registered = self.dmca_agent_info.get('registered_with_copyright_office', False)
        
        # Assess based on recent compliance
        recent_audit = self.compliance_audits[-1] if self.compliance_audits else None
        has_notice_takedown = True  # Assume implemented
        has_repeat_infringer_policy = True  # Assume implemented
        responds_to_notices = recent_audit.compliance_rate >= 0.80 if recent_audit else False
        removes_expeditiously = recent_audit.response_time_avg_hours <= 72 if recent_audit else False
        has_no_actual_knowledge = True  # Requires case-by-case analysis
        
        # Determine eligibility
        eligible = all([
            has_dmca_agent,
            agent_registered,
            has_notice_takedown,
            has_repeat_infringer_policy,
            responds_to_notices,
            removes_expeditiously,
            has_no_actual_knowledge
        ])
        
        # Identify compliance gaps
        compliance_gaps = []
        if not has_dmca_agent:
            compliance_gaps.append("No designated DMCA agent")
        if not agent_registered:
            compliance_gaps.append("DMCA agent not registered with Copyright Office")
        if not responds_to_notices:
            compliance_gaps.append("Poor response rate to takedown notices")
        if not removes_expeditiously:
            compliance_gaps.append("Slow content removal response times")
        
        # Assess risk level
        if eligible:
            risk_level = "low"
        elif len(compliance_gaps) <= 2:
            risk_level = "medium"
        else:
            risk_level = "high"
        
        assessment = SafeHarborAssessment(
            assessment_id=assessment_id,
            platform=platform,
            has_dmca_agent=has_dmca_agent,
            agent_registered_with_copyright_office=agent_registered,
            has_notice_takedown_procedure=has_notice_takedown,
            has_repeat_infringer_policy=has_repeat_infringer_policy,
            responds_to_takedown_notices=responds_to_notices,
            removes_content_expeditiously=removes_expeditiously,
            has_no_actual_knowledge=has_no_actual_knowledge,
            safe_harbor_eligible=eligible,
            compliance_gaps=compliance_gaps,
            risk_level=risk_level
        )
        
        self.safe_harbor_assessments.append(assessment)
        
        logger.info(f"Safe harbor assessment completed: {assessment_id} "
                   f"(eligible={eligible}, risk={risk_level})")
        
        return assessment_id
    
    def get_dmca_statistics(self, hours: int = 24) -> Dict[str, Any]:
        """Get comprehensive DMCA compliance statistics."""
        cutoff_time = datetime.utcnow() - timedelta(hours=hours)
        
        recent_requests = [
            request for request in self.dmca_requests
            if request.submitted_at >= cutoff_time
        ]
        
        if not recent_requests:
            return {"message": f"No DMCA requests in last {hours} hours"}
        
        # Calculate statistics
        total_requests = len(recent_requests)
        valid_requests = len([r for r in recent_requests if r.status != DMCAStatus.INVALID])
        processed_requests = len([r for r in recent_requests if r.processed_at is not None])
        
        # Status distribution
        status_counts = {}
        for status in DMCAStatus:
            count = len([r for r in recent_requests if r.status == status])
            if count > 0:
                status_counts[status.value] = count
        
        # Request type distribution
        type_counts = {}
        for request_type in DMCARequestType:
            count = len([r for r in recent_requests if r.request_type == request_type])
            if count > 0:
                type_counts[request_type.value] = count
        
        # Response time analysis
        response_times = []
        for request in recent_requests:
            if request.processed_at:
                response_time = (request.processed_at - request.submitted_at).total_seconds() / 3600
                response_times.append(response_time)
        
        avg_response_time = sum(response_times) / len(response_times) if response_times else 0
        
        # Overdue requests
        overdue_requests = [
            r for r in recent_requests
            if datetime.utcnow() > r.response_deadline and r.status not in [DMCAStatus.PROCESSED, DMCAStatus.REJECTED]
        ]
        
        return {
            'period_hours': hours,
            'request_summary': {
                'total_requests': total_requests,
                'valid_requests': valid_requests,
                'processed_requests': processed_requests,
                'processing_rate': processed_requests / total_requests if total_requests > 0 else 0,
                'overdue_requests': len(overdue_requests)
            },
            'status_distribution': status_counts,
            'request_type_distribution': type_counts,
            'response_time_analysis': {
                'average_hours': avg_response_time,
                'target_hours': self.compliance_thresholds['response_time_hours']['target'],
                'on_time_rate': len([t for t in response_times if t <= 72]) / len(response_times) if response_times else 0
            },
            'compliance_indicators': {
                'dmca_agent_registered': self.dmca_agent_info.get('registered_with_copyright_office', False),
                'agent_contact_available': bool(self.dmca_agent_info.get('email')),
                'recent_audit_compliance': self.compliance_audits[-1].compliance_rate if self.compliance_audits else 0
            },
            'recent_audits': len(self.compliance_audits),
            'safe_harbor_assessments': len(self.safe_harbor_assessments)
        }

# Global DMCA compliance tracker instance
dmca_compliance_tracker = DMCAComplianceTracker()

# Export main components
__all__ = [
    'DMCAComplianceTracker',
    'DMCARequest',
    'ComplianceAudit',
    'SafeHarborAssessment',
    'DMCARequestType',
    'DMCAStatus',
    'ComplianceLevel',
    'dmca_compliance_tracker'
]