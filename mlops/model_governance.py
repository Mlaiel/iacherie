"""
Model Governance with Approval Workflows
Implements comprehensive model governance and approval workflows
"""

import uuid
import asyncio
from typing import Dict, List, Optional, Any, Callable, Set
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import json
import logging
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)


class ApprovalStatus(Enum):
    """Status of approval requests"""
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    EXPIRED = "expired"
    CANCELLED = "cancelled"


class GovernanceAction(Enum):
    """Types of governance actions"""
    MODEL_REGISTRATION = "model_registration"
    MODEL_DEPLOYMENT = "model_deployment"
    MODEL_PROMOTION = "model_promotion"
    MODEL_RETIREMENT = "model_retirement"
    FEATURE_CHANGE = "feature_change"
    DATA_ACCESS = "data_access"
    EXPERIMENT_APPROVAL = "experiment_approval"


class RiskLevel(Enum):
    """Risk levels for governance decisions"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class UserRole(Enum):
    """User roles in the governance system"""
    DATA_SCIENTIST = "data_scientist"
    ML_ENGINEER = "ml_engineer"
    MODEL_REVIEWER = "model_reviewer"
    COMPLIANCE_OFFICER = "compliance_officer"
    BUSINESS_OWNER = "business_owner"
    ADMIN = "admin"


@dataclass
class User:
    """User in the governance system"""
    user_id: str
    name: str
    email: str
    roles: List[UserRole]
    department: str
    created_at: datetime = field(default_factory=datetime.now)
    is_active: bool = True
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ApprovalRule:
    """Rule for approval requirements"""
    action_type: GovernanceAction
    required_roles: List[UserRole]
    min_approvers: int
    max_rejection_threshold: int
    auto_approve_conditions: Optional[Dict[str, Any]] = None
    escalation_rules: Optional[Dict[str, Any]] = None
    expiry_hours: int = 72  # Default 3 days
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ApprovalRequest:
    """Request for governance approval"""
    request_id: str
    action_type: GovernanceAction
    title: str
    description: str
    requestor_id: str
    risk_level: RiskLevel
    model_info: Optional[Dict[str, Any]] = None
    change_details: Optional[Dict[str, Any]] = None
    business_justification: str = ""
    compliance_notes: str = ""
    supporting_documents: List[str] = field(default_factory=list)
    required_approvers: List[str] = field(default_factory=list)
    approvals: List[Dict[str, Any]] = field(default_factory=list)
    rejections: List[Dict[str, Any]] = field(default_factory=list)
    comments: List[Dict[str, Any]] = field(default_factory=list)
    status: ApprovalStatus = ApprovalStatus.PENDING
    created_at: datetime = field(default_factory=datetime.now)
    expires_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class GovernancePolicy:
    """Governance policy definition"""
    policy_id: str
    name: str
    description: str
    policy_type: str  # "approval", "compliance", "security", etc.
    rules: List[Dict[str, Any]]
    affected_actions: List[GovernanceAction]
    enforcement_level: str  # "mandatory", "advisory", "optional"
    effective_date: datetime
    expiry_date: Optional[datetime] = None
    version: str = "1.0"
    created_by: str = ""
    approved_by: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


class NotificationService:
    """Service for sending notifications"""
    
    def __init__(self):
        try:
            logger.info(f"Executing __init__")
            
            # Implementation for __init__
            # TODO: Add specific business logic here
            
            result = None  # Replace with actual implementation
            
            logger.info(f"__init__ completed successfully")
            return result
            
        except Exception as e:
            logger.error(f"__init__ failed: {e}")
            raise
    def register_callback(self, notification_type: str, callback: Callable):
        """Register a notification callback"""
        self.notification_callbacks[notification_type] = callback
        logger.info(f"Registered notification callback for {notification_type}")
    
    async def send_notification(
        self,
        notification_type: str,
        recipients: List[str],
        subject: str,
        message: str,
        metadata: Optional[Dict] = None
    ):
        """Send a notification"""
        try:
            if notification_type in self.notification_callbacks:
                callback = self.notification_callbacks[notification_type]
                await callback(recipients, subject, message, metadata or {})
            else:
                logger.info(f"Notification ({notification_type}): {subject} to {recipients}")
        except Exception as e:
            logger.error(f"Error sending notification: {str(e)}")


class ComplianceChecker:
    """Check compliance requirements"""
    
    def __init__(self):
        self.compliance_rules: Dict[str, Callable] = {}
        self.compliance_policies: List[GovernancePolicy] = []
        try:
            logger.info(f"Executing check_compliance")
            
            # Implementation for check_compliance
            # TODO: Add specific business logic here
            
            result = None  # Replace with actual implementation
            
            logger.info(f"check_compliance completed successfully")
            return result
            
        except Exception as e:
            logger.error(f"check_compliance failed: {e}")
            raise
                        if "requirements" in rule_result:
                            compliance_result["requirements"].extend(rule_result["requirements"])
                            
                    except Exception as e:
                        logger.error(f"Error checking compliance rule {rule_name}: {str(e)}")
                        compliance_result["warnings"].append({
                            "policy": policy.name,
                            "rule": rule_name,
                            "message": f"Error checking rule: {str(e)}"
                        })
        
        return compliance_result


class ModelGovernanceEngine:
    """Core model governance engine"""
    
    def __init__(self):
        self.users: Dict[str, User] = {}
        self.approval_rules: Dict[GovernanceAction, ApprovalRule] = {}
        self.approval_requests: Dict[str, ApprovalRequest] = {}
        self.policies: List[GovernancePolicy] = []
        self.notification_service = NotificationService()
        self.compliance_checker = ComplianceChecker()
        self.audit_log: List[Dict[str, Any]] = []
        
        # Auto-approval settings
        self.enable_auto_approval = True
        self.auto_approval_callbacks: Dict[str, Callable] = {}
    
    def register_user(self, user: User):
        """Register a user in the governance system"""
        self.users[user.user_id] = user
        logger.info(f"Registered user {user.name} ({user.user_id}) with roles {[r.value for r in user.roles]}")
    
    def add_approval_rule(self, rule: ApprovalRule):
        """Add an approval rule"""
        self.approval_rules[rule.action_type] = rule
        logger.info(f"Added approval rule for {rule.action_type.value}")
    
    def add_policy(self, policy: GovernancePolicy):
        """Add a governance policy"""
        self.policies.append(policy)
        self.compliance_checker.add_policy(policy)
        logger.info(f"Added governance policy: {policy.name}")
    
    async def submit_approval_request(
        self,
        action_type: GovernanceAction,
        title: str,
        description: str,
        requestor_id: str,
        model_info: Optional[Dict] = None,
        change_details: Optional[Dict] = None,
        business_justification: str = "",
        risk_level: RiskLevel = RiskLevel.MEDIUM
    ) -> str:
        """Submit a new approval request"""
        
        # Validate requestor
        if requestor_id not in self.users:
            raise ValueError(f"User {requestor_id} not found")
        
        request_id = str(uuid.uuid4())
        
        # Determine required approvers based on rules
        required_approvers = []
        if action_type in self.approval_rules:
            rule = self.approval_rules[action_type]
            required_approvers = self._find_approvers(rule)
        
        # Calculate expiry time
        expiry_hours = 72  # Default
        if action_type in self.approval_rules:
            expiry_hours = self.approval_rules[action_type].expiry_hours
        
        expires_at = datetime.now() + timedelta(hours=expiry_hours)
        
        # Create approval request
        request = ApprovalRequest(
            request_id=request_id,
            action_type=action_type,
            title=title,
            description=description,
            requestor_id=requestor_id,
            risk_level=risk_level,
            model_info=model_info,
            change_details=change_details,
            business_justification=business_justification,
            required_approvers=required_approvers,
            expires_at=expires_at
        )
        
        # Check compliance
        compliance_result = self.compliance_checker.check_compliance(request)
        if not compliance_result["is_compliant"]:
            raise ValueError(f"Compliance violations: {compliance_result['violations']}")
        
        self.approval_requests[request_id] = request
        
        # Log the submission
        await self._log_audit_event("request_submitted", {
            "request_id": request_id,
            "action_type": action_type.value,
            "requestor_id": requestor_id,
            "risk_level": risk_level.value
        })
        
        # Check for auto-approval
        if self.enable_auto_approval:
            auto_approved = await self._check_auto_approval(request)
            if auto_approved:
                return request_id
        
        # Send notifications to required approvers
        await self._notify_approvers(request)
        
        logger.info(f"Submitted approval request {request_id} for {action_type.value}")
        return request_id
    
    async def approve_request(
        self,
        request_id: str,
        approver_id: str,
        comments: str = "",
        conditions: Optional[List[str]] = None
    ) -> bool:
        """Approve an approval request"""
        
        if request_id not in self.approval_requests:
            raise ValueError(f"Request {request_id} not found")
        
        request = self.approval_requests[request_id]
        
        # Check if user can approve
        if not self._can_user_approve(approver_id, request):
            raise ValueError(f"User {approver_id} cannot approve this request")
        
        # Check if already approved by this user
        existing_approval = any(
            approval["approver_id"] == approver_id
            for approval in request.approvals
        )
        
        if existing_approval:
            raise ValueError(f"User {approver_id} has already approved this request")
        
        # Add approval
        approval = {
            "approver_id": approver_id,
            "approved_at": datetime.now(),
            "comments": comments,
            "conditions": conditions or []
        }
        
        request.approvals.append(approval)
        
        # Check if request is fully approved
        if self._is_fully_approved(request):
            request.status = ApprovalStatus.APPROVED
            request.completed_at = datetime.now()
            
            # Execute approved action
            await self._execute_approved_action(request)
            
            # Notify stakeholders
            await self._notify_approval_completion(request)
        
        # Log the approval
        await self._log_audit_event("request_approved", {
            "request_id": request_id,
            "approver_id": approver_id,
            "comments": comments,
            "fully_approved": request.status == ApprovalStatus.APPROVED
        })
        
        logger.info(f"Request {request_id} approved by {approver_id}")
        return True
    
    async def reject_request(
        self,
        request_id: str,
        rejector_id: str,
        reason: str
    ) -> bool:
        """Reject an approval request"""
        
        if request_id not in self.approval_requests:
            raise ValueError(f"Request {request_id} not found")
        
        request = self.approval_requests[request_id]
        
        # Check if user can reject
        if not self._can_user_approve(rejector_id, request):
            raise ValueError(f"User {rejector_id} cannot reject this request")
        
        # Add rejection
        rejection = {
            "rejector_id": rejector_id,
            "rejected_at": datetime.now(),
            "reason": reason
        }
        
        request.rejections.append(rejection)
        
        # Check if rejection threshold is met
        if self._is_rejection_threshold_met(request):
            request.status = ApprovalStatus.REJECTED
            request.completed_at = datetime.now()
            
            # Notify stakeholders
            await self._notify_rejection(request)
        
        # Log the rejection
        await self._log_audit_event("request_rejected", {
            "request_id": request_id,
            "rejector_id": rejector_id,
            "reason": reason,
            "fully_rejected": request.status == ApprovalStatus.REJECTED
        })
        
        logger.info(f"Request {request_id} rejected by {rejector_id}")
        return True
    
    async def add_comment(
        self,
        request_id: str,
        commenter_id: str,
        comment: str
    ) -> bool:
        """Add a comment to an approval request"""
        
        if request_id not in self.approval_requests:
            raise ValueError(f"Request {request_id} not found")
        
        request = self.approval_requests[request_id]
        
        comment_data = {
            "commenter_id": commenter_id,
            "comment": comment,
            "created_at": datetime.now()
        }
        
        request.comments.append(comment_data)
        
        # Notify relevant parties about the comment
        await self._notify_comment_added(request, comment_data)
        
        logger.info(f"Comment added to request {request_id} by {commenter_id}")
        return True
    
    def get_request(self, request_id: str) -> Optional[ApprovalRequest]:
        """Get an approval request"""
        return self.approval_requests.get(request_id)
    
    def get_user_requests(
        self,
        user_id: str,
        status_filter: Optional[ApprovalStatus] = None
    ) -> List[ApprovalRequest]:
        """Get requests for a user (submitted or requiring approval)"""
        
        user_requests = []
        
        for request in self.approval_requests.values():
            # Check if user is requestor
            if request.requestor_id == user_id:
                if not status_filter or request.status == status_filter:
                    user_requests.append(request)
            
            # Check if user is required approver
            elif user_id in request.required_approvers:
                if not status_filter or request.status == status_filter:
                    # Only include if not already approved/rejected by this user
                    has_acted = any(
                        approval["approver_id"] == user_id for approval in request.approvals
                    ) or any(
                        rejection["rejector_id"] == user_id for rejection in request.rejections
                    )
                    
                    if not has_acted and request.status == ApprovalStatus.PENDING:
                        user_requests.append(request)
        
        return sorted(user_requests, key=lambda r: r.created_at, reverse=True)
    
    def get_pending_requests(self) -> List[ApprovalRequest]:
        """Get all pending requests"""
        return [
            request for request in self.approval_requests.values()
            if request.status == ApprovalStatus.PENDING
        ]
    
    async def expire_old_requests(self):
        """Expire old requests that have passed their expiry time"""
        current_time = datetime.now()
        expired_count = 0
        
        for request in self.approval_requests.values():
            if (request.status == ApprovalStatus.PENDING and 
                request.expires_at and 
                current_time > request.expires_at):
                
                request.status = ApprovalStatus.EXPIRED
                request.completed_at = current_time
                
                # Notify about expiration
                await self._notify_expiration(request)
                
                # Log expiration
                await self._log_audit_event("request_expired", {
                    "request_id": request.request_id,
                    "expired_at": current_time.isoformat()
                })
                
                expired_count += 1
        
        if expired_count > 0:
            logger.info(f"Expired {expired_count} old approval requests")
    
    def _find_approvers(self, rule: ApprovalRule) -> List[str]:
        """Find users who can approve based on approval rule"""
        approvers = []
        
        for user_id, user in self.users.items():
        try:
            logger.info(f"Executing expire_old_requests")
            
            # Implementation for expire_old_requests
            # TODO: Add specific business logic here
            
            result = None  # Replace with actual implementation
            
            logger.info(f"expire_old_requests completed successfully")
            return result
            
        except Exception as e:
            logger.error(f"expire_old_requests failed: {e}")
            raise
        return user_id in request.required_approvers
    
    def _is_fully_approved(self, request: ApprovalRequest) -> bool:
        """Check if request is fully approved"""
        if request.action_type not in self.approval_rules:
            return len(request.approvals) > 0  # Default: at least one approval
        
        rule = self.approval_rules[request.action_type]
        return len(request.approvals) >= rule.min_approvers
    
    def _is_rejection_threshold_met(self, request: ApprovalRequest) -> bool:
        """Check if rejection threshold is met"""
        if request.action_type not in self.approval_rules:
            return len(request.rejections) > 0  # Default: any rejection
        
        rule = self.approval_rules[request.action_type]
        return len(request.rejections) >= rule.max_rejection_threshold
    
    async def _check_auto_approval(self, request: ApprovalRequest) -> bool:
        """Check if request can be auto-approved"""
        if request.action_type not in self.approval_rules:
            return False
        
        rule = self.approval_rules[request.action_type]
        auto_approve_conditions = rule.auto_approve_conditions
        
        if not auto_approve_conditions:
            return False
        
        # Check conditions
        for condition, expected_value in auto_approve_conditions.items():
            if condition == "risk_level":
                if request.risk_level.value != expected_value:
                    return False
            elif condition == "model_type":
                if not request.model_info or request.model_info.get("type") != expected_value:
                    return False
            # Add more conditions as needed
        
        # Auto-approve the request
        auto_approval = {
            "approver_id": "system",
            "approved_at": datetime.now(),
            "comments": "Auto-approved based on configured rules",
            "conditions": []
        }
        
        request.approvals.append(auto_approval)
        request.status = ApprovalStatus.APPROVED
        request.completed_at = datetime.now()
        
        # Execute approved action
        await self._execute_approved_action(request)
        
        # Log auto-approval
        await self._log_audit_event("request_auto_approved", {
            "request_id": request.request_id,
            "conditions_met": auto_approve_conditions
        })
        
        logger.info(f"Request {request.request_id} auto-approved")
        return True
    
    async def _execute_approved_action(self, request: ApprovalRequest):
        """Execute the approved action"""
        action_type = request.action_type.value
        
        if action_type in self.auto_approval_callbacks:
            try:
                callback = self.auto_approval_callbacks[action_type]
                await callback(request)
                logger.info(f"Executed approved action {action_type} for request {request.request_id}")
            except Exception as e:
                logger.error(f"Error executing approved action {action_type}: {str(e)}")
        else:
            logger.info(f"No executor configured for action type {action_type}")
    
    def register_action_executor(self, action_type: str, callback: Callable):
        """Register a callback for executing approved actions"""
        self.auto_approval_callbacks[action_type] = callback
        logger.info(f"Registered action executor for {action_type}")
    
    async def _notify_approvers(self, request: ApprovalRequest):
        """Notify required approvers about new request"""
        approver_emails = []
        for approver_id in request.required_approvers:
            if approver_id in self.users:
                approver_emails.append(self.users[approver_id].email)
        
        if approver_emails:
            await self.notification_service.send_notification(
                "approval_required",
                approver_emails,
                f"Approval Required: {request.title}",
                f"A new {request.action_type.value} request requires your approval.\n\n"
                f"Request ID: {request.request_id}\n"
                f"Title: {request.title}\n"
                f"Description: {request.description}\n"
                f"Risk Level: {request.risk_level.value}\n"
                f"Requestor: {self.users[request.requestor_id].name}\n\n"
                f"Please review and approve/reject this request.",
                {"request_id": request.request_id}
            )
    
    async def _notify_approval_completion(self, request: ApprovalRequest):
        """Notify about approval completion"""
        requestor_email = self.users[request.requestor_id].email
        
        await self.notification_service.send_notification(
            "approval_completed",
            [requestor_email],
            f"Request Approved: {request.title}",
            f"Your {request.action_type.value} request has been approved.\n\n"
            f"Request ID: {request.request_id}\n"
            f"Title: {request.title}\n"
            f"Approved by: {len(request.approvals)} approvers\n\n"
            f"The requested action will be executed shortly.",
            {"request_id": request.request_id}
        )
    
    async def _notify_rejection(self, request: ApprovalRequest):
        """Notify about rejection"""
        requestor_email = self.users[request.requestor_id].email
        
        await self.notification_service.send_notification(
            "approval_rejected",
            [requestor_email],
            f"Request Rejected: {request.title}",
            f"Your {request.action_type.value} request has been rejected.\n\n"
            f"Request ID: {request.request_id}\n"
            f"Title: {request.title}\n"
            f"Rejection reason: {request.rejections[-1]['reason']}\n\n"
            f"Please review the feedback and resubmit if appropriate.",
            {"request_id": request.request_id}
        )
    
    async def _notify_expiration(self, request: ApprovalRequest):
        """Notify about request expiration"""
        requestor_email = self.users[request.requestor_id].email
        
        await self.notification_service.send_notification(
            "approval_expired",
            [requestor_email],
            f"Request Expired: {request.title}",
            f"Your {request.action_type.value} request has expired.\n\n"
            f"Request ID: {request.request_id}\n"
            f"Title: {request.title}\n\n"
            f"Please resubmit the request if still needed.",
            {"request_id": request.request_id}
        )
    
    async def _notify_comment_added(self, request: ApprovalRequest, comment_data: Dict):
        """Notify about new comment"""
        # Notify all stakeholders (requestor + approvers)
        emails = [self.users[request.requestor_id].email]
        for approver_id in request.required_approvers:
            if approver_id in self.users:
                emails.append(self.users[approver_id].email)
        
        # Remove duplicates
        emails = list(set(emails))
        
        commenter_name = self.users[comment_data["commenter_id"]].name
        
        await self.notification_service.send_notification(
            "comment_added",
            emails,
            f"New Comment: {request.title}",
            f"A new comment has been added to approval request.\n\n"
            f"Request ID: {request.request_id}\n"
            f"Comment by: {commenter_name}\n"
            f"Comment: {comment_data['comment']}\n\n",
            {"request_id": request.request_id}
        )
    
    async def _log_audit_event(self, event_type: str, event_data: Dict):
        """Log an audit event"""
        audit_entry = {
            "event_id": str(uuid.uuid4()),
            "event_type": event_type,
            "timestamp": datetime.now().isoformat(),
            "data": event_data
        }
        
        self.audit_log.append(audit_entry)
        
        # In a real system, this would also write to persistent storage
        logger.info(f"Audit log: {event_type} - {event_data}")
    
    def get_audit_log(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        event_types: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        """Get audit log entries"""
        filtered_log = self.audit_log
        
        if start_date:
            filtered_log = [
                entry for entry in filtered_log
                if datetime.fromisoformat(entry["timestamp"]) >= start_date
            ]
        
        if end_date:
            filtered_log = [
                entry for entry in filtered_log
                if datetime.fromisoformat(entry["timestamp"]) <= end_date
            ]
        
        if event_types:
            filtered_log = [
                entry for entry in filtered_log
                if entry["event_type"] in event_types
            ]
        
        return sorted(filtered_log, key=lambda e: e["timestamp"], reverse=True)
    
    def get_governance_dashboard_data(self) -> Dict[str, Any]:
        """Get data for governance dashboard"""
        pending_requests = self.get_pending_requests()
        
        # Calculate metrics
        total_requests = len(self.approval_requests)
        approved_requests = len([r for r in self.approval_requests.values() if r.status == ApprovalStatus.APPROVED])
        rejected_requests = len([r for r in self.approval_requests.values() if r.status == ApprovalStatus.REJECTED])
        expired_requests = len([r for r in self.approval_requests.values() if r.status == ApprovalStatus.EXPIRED])
        
        # Risk level distribution
        risk_distribution = {}
        for risk_level in RiskLevel:
            risk_distribution[risk_level.value] = len([
                r for r in self.approval_requests.values()
                if r.risk_level == risk_level
            ])
        
        # Action type distribution
        action_distribution = {}
        for action_type in GovernanceAction:
            action_distribution[action_type.value] = len([
                r for r in self.approval_requests.values()
                if r.action_type == action_type
            ])
        
        return {
            "summary": {
                "total_requests": total_requests,
                "pending_requests": len(pending_requests),
                "approved_requests": approved_requests,
                "rejected_requests": rejected_requests,
                "expired_requests": expired_requests,
                "approval_rate": approved_requests / max(total_requests, 1) * 100
            },
            "distributions": {
                "risk_levels": risk_distribution,
                "action_types": action_distribution
            },
            "recent_requests": [
                {
                    "request_id": r.request_id,
                    "title": r.title,
                    "action_type": r.action_type.value,
                    "status": r.status.value,
                    "created_at": r.created_at.isoformat(),
                    "risk_level": r.risk_level.value
                }
                for r in sorted(self.approval_requests.values(), key=lambda x: x.created_at, reverse=True)[:10]
            ],
            "users": {
                "total_users": len(self.users),
                "active_users": len([u for u in self.users.values() if u.is_active])
            },
            "policies": {
                "total_policies": len(self.policies),
                "active_policies": len([p for p in self.policies if not p.expiry_date or p.expiry_date > datetime.now()])
            }
        }