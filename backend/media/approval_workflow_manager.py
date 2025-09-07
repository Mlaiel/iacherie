"""Approval Workflow Manager - Content Approval System

Enterprise-grade approval workflow system for managing content review processes,
stakeholder approvals, and compliance validation across media assets.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel - All Rights Reserved

LEGAL WARNING: This code is the exclusive property of Fahed Mlaiel.
Unauthorized use, reproduction, or distribution is strictly prohibited.
"""

import asyncio
import json
import logging
from datetime import datetime, timedelta, timezone
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Any, Tuple, Union, Callable
import uuid
from collections import defaultdict

# External dependencies with graceful fallbacks
try:
    from sqlalchemy.ext.asyncio import AsyncSession
    HAS_SQLALCHEMY = True
except ImportError:
    HAS_SQLALCHEMY = False
    logging.warning("SQLAlchemy async not available - using in-memory storage")

try:
    import redis
    HAS_REDIS = True
except ImportError:
    HAS_REDIS = False
    logging.warning("Redis not available - using in-memory notifications")

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ApprovalStatus(Enum):
    """Approval status types"""
    PENDING = "pending"
    IN_REVIEW = "in_review"
    APPROVED = "approved"
    REJECTED = "rejected"
    CONDITIONAL_APPROVAL = "conditional_approval"
    ESCALATED = "escalated"
    CANCELLED = "cancelled"
    EXPIRED = "expired"


class ApprovalType(Enum):
    """Types of approval workflows"""
    CONTENT_REVIEW = "content_review"
    LEGAL_COMPLIANCE = "legal_compliance"
    BRAND_APPROVAL = "brand_approval"
    TECHNICAL_REVIEW = "technical_review"
    CREATIVE_APPROVAL = "creative_approval"
    BUDGET_APPROVAL = "budget_approval"
    PUBLISH_APPROVAL = "publish_approval"
    COLLABORATION_APPROVAL = "collaboration_approval"


class ReviewerRole(Enum):
    """Reviewer role types"""
    CONTENT_REVIEWER = "content_reviewer"
    LEGAL_REVIEWER = "legal_reviewer"
    BRAND_MANAGER = "brand_manager"
    TECHNICAL_REVIEWER = "technical_reviewer"
    CREATIVE_DIRECTOR = "creative_director"
    PROJECT_MANAGER = "project_manager"
    COMPLIANCE_OFFICER = "compliance_officer"
    STAKEHOLDER = "stakeholder"


class Priority(Enum):
    """Approval priority levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"
    CRITICAL = "critical"


class EscalationReason(Enum):
    """Escalation reasons"""
    TIMEOUT = "timeout"
    CONFLICT = "conflict"
    COMPLEXITY = "complexity"
    POLICY_VIOLATION = "policy_violation"
    BUDGET_THRESHOLD = "budget_threshold"
    MANUAL_REQUEST = "manual_request"


@dataclass
class ApprovalCriteria:
    """Approval criteria definition"""
    id: str
    name: str
    description: str
    required: bool = True
    weight: float = 1.0
    auto_checkable: bool = False
    check_function: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ReviewComment:
    """Review comment from approver"""
    id: str
    reviewer_id: str
    reviewer_role: ReviewerRole
    comment: str
    timestamp: datetime
    is_blocking: bool = False
    resolved: bool = False
    resolved_by: Optional[str] = None
    resolved_at: Optional[datetime] = None
    attachments: List[str] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)


@dataclass
class ApprovalStep:
    """Individual approval step in workflow"""
    id: str
    step_number: int
    name: str
    description: str
    
    # Reviewers
    required_reviewers: List[str]
    optional_reviewers: List[str] = field(default_factory=list)
    reviewer_roles: List[ReviewerRole] = field(default_factory=list)
    
    # Approval criteria
    criteria: List[ApprovalCriteria] = field(default_factory=list)
    min_approvals: int = 1
    allow_delegation: bool = True
    
    # Timing
    sla_hours: Optional[int] = None
    reminder_hours: Optional[int] = None
    auto_escalate_hours: Optional[int] = None
    
    # Status
    status: ApprovalStatus = ApprovalStatus.PENDING
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    
    # Results
    approvals: Dict[str, bool] = field(default_factory=dict)
    comments: List[ReviewComment] = field(default_factory=list)
    conditions: List[str] = field(default_factory=list)


@dataclass
class EscalationRule:
    """Escalation rule definition"""
    id: str
    name: str
    trigger_condition: EscalationReason
    trigger_threshold: Optional[Union[int, float]] = None
    escalate_to: List[str] = field(default_factory=list)
    escalate_roles: List[ReviewerRole] = field(default_factory=list)
    notification_template: Optional[str] = None
    auto_assign: bool = True
    priority_boost: bool = True


@dataclass
class ApprovalWorkflow:
    """Complete approval workflow definition"""
    id: str
    name: str
    type: ApprovalType
    description: str
    
    # Workflow structure
    steps: List[ApprovalStep] = field(default_factory=list)
    is_parallel: bool = False
    allow_skip_steps: bool = False
    
    # Configuration
    priority: Priority = Priority.MEDIUM
    sla_hours: Optional[int] = None
    auto_start: bool = True
    
    # Escalation
    escalation_rules: List[EscalationRule] = field(default_factory=list)
    max_escalations: int = 3
    
    # Notifications
    notification_settings: Dict[str, bool] = field(default_factory=dict)
    
    # Metadata
    created_by: str = ""
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    
    # Status tracking
    active: bool = True
    version: str = "1.0"


@dataclass
class ApprovalRequest:
    """Individual approval request instance"""
    id: str
    workflow_id: str
    content_id: str
    content_type: str
    
    # Request information
    title: str
    description: str
    requested_by: str
    requested_at: datetime
    
    # Urgency and priority
    priority: Priority
    due_date: Optional[datetime] = None
    business_justification: str = ""
    
    # Status
    status: ApprovalStatus = ApprovalStatus.PENDING
    current_step: int = 0
    progress_percentage: float = 0.0
    
    # Results
    final_decision: Optional[bool] = None
    decision_date: Optional[datetime] = None
    decision_by: Optional[str] = None
    final_comments: str = ""
    
    # Tracking
    step_history: List[Dict[str, Any]] = field(default_factory=list)
    escalations: List[Dict[str, Any]] = field(default_factory=list)
    
    # Metadata
    metadata: Dict[str, Any] = field(default_factory=dict)
    attachments: List[str] = field(default_factory=list)
    
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


class ApprovalWorkflowManager:
    """Advanced approval workflow management system"""
    
    def __init__(self, redis_url: Optional[str] = None):
        """Initialize approval workflow manager
        
        Args:
            redis_url: Optional Redis connection URL
        """
        self.workflows: Dict[str, ApprovalWorkflow] = {}
        self.requests: Dict[str, ApprovalRequest] = {}
        self.notification_handlers: List[Callable] = []
        self.escalation_handlers: List[Callable] = []
        
        # Initialize Redis if available
        self.redis_client = None
        if HAS_REDIS and redis_url:
            try:
                self.redis_client = redis.from_url(redis_url)
                logger.info("Connected to Redis for notifications")
            except Exception as e:
                logger.warning(f"Failed to connect to Redis: {e}")
        
        # Load default workflows
        self._load_default_workflows()
        
        logger.info("ApprovalWorkflowManager initialized successfully")
    
    def _load_default_workflows(self):
        """Load default approval workflows"""
        # Content Review Workflow
        content_workflow = ApprovalWorkflow(
            id="content_review_standard",
            name="Standard Content Review",
            type=ApprovalType.CONTENT_REVIEW,
            description="Standard content approval workflow",
            sla_hours=48,
            priority=Priority.MEDIUM
        )
        
        # Content review step
        content_step = ApprovalStep(
            id="content_review_step",
            step_number=1,
            name="Content Review",
            description="Review content for quality and compliance",
            required_reviewers=[],
            reviewer_roles=[ReviewerRole.CONTENT_REVIEWER],
            min_approvals=1,
            sla_hours=24
        )
        content_workflow.steps.append(content_step)
        
        # Legal review step
        legal_step = ApprovalStep(
            id="legal_review_step",
            step_number=2,
            name="Legal Review",
            description="Review for legal compliance and copyright",
            required_reviewers=[],
            reviewer_roles=[ReviewerRole.LEGAL_REVIEWER],
            min_approvals=1,
            sla_hours=24
        )
        content_workflow.steps.append(legal_step)
        
        self.workflows[content_workflow.id] = content_workflow
        
        # Brand Approval Workflow
        brand_workflow = ApprovalWorkflow(
            id="brand_approval_standard",
            name="Brand Approval Workflow",
            type=ApprovalType.BRAND_APPROVAL,
            description="Brand guidelines compliance approval",
            sla_hours=24,
            priority=Priority.HIGH
        )
        
        brand_step = ApprovalStep(
            id="brand_review_step",
            step_number=1,
            name="Brand Review",
            description="Review for brand guidelines compliance",
            required_reviewers=[],
            reviewer_roles=[ReviewerRole.BRAND_MANAGER, ReviewerRole.CREATIVE_DIRECTOR],
            min_approvals=1,
            sla_hours=12
        )
        brand_workflow.steps.append(brand_step)
        
        self.workflows[brand_workflow.id] = brand_workflow
    
    async def create_workflow(self, workflow_data: Dict[str, Any]) -> str:
        """Create a new approval workflow
        
        Args:
            workflow_data: Workflow configuration
            
        Returns:
            Workflow ID
        """
        try:
            workflow_id = str(uuid.uuid4())
            
            workflow = ApprovalWorkflow(
                id=workflow_id,
                name=workflow_data["name"],
                type=ApprovalType(workflow_data["type"]),
                description=workflow_data.get("description", ""),
                priority=Priority(workflow_data.get("priority", "medium")),
                sla_hours=workflow_data.get("sla_hours"),
                created_by=workflow_data.get("created_by", "system")
            )
            
            # Add steps
            for step_data in workflow_data.get("steps", []):
                step = ApprovalStep(
                    id=str(uuid.uuid4()),
                    step_number=step_data["step_number"],
                    name=step_data["name"],
                    description=step_data.get("description", ""),
                    required_reviewers=step_data.get("required_reviewers", []),
                    reviewer_roles=[ReviewerRole(role) for role in step_data.get("reviewer_roles", [])],
                    min_approvals=step_data.get("min_approvals", 1),
                    sla_hours=step_data.get("sla_hours")
                )
                workflow.steps.append(step)
            
            self.workflows[workflow_id] = workflow
            
            logger.info(f"Created workflow {workflow_id}: {workflow.name}")
            return workflow_id
            
        except Exception as e:
            logger.error(f"Error creating workflow: {e}")
            raise
    
    async def submit_approval_request(self, request_data: Dict[str, Any]) -> str:
        """Submit a new approval request
        
        Args:
            request_data: Approval request information
            
        Returns:
            Request ID
        """
        try:
            request_id = str(uuid.uuid4())
            now = datetime.now(timezone.utc)
            
            # Validate workflow exists
            workflow_id = request_data["workflow_id"]
            if workflow_id not in self.workflows:
                raise ValueError(f"Workflow {workflow_id} not found")
            
            workflow = self.workflows[workflow_id]
            
            # Create approval request
            request = ApprovalRequest(
                id=request_id,
                workflow_id=workflow_id,
                content_id=request_data["content_id"],
                content_type=request_data["content_type"],
                title=request_data["title"],
                description=request_data.get("description", ""),
                requested_by=request_data["requested_by"],
                requested_at=now,
                priority=Priority(request_data.get("priority", workflow.priority.value)),
                due_date=datetime.fromisoformat(request_data["due_date"]) if request_data.get("due_date") else None,
                business_justification=request_data.get("business_justification", "")
            )
            
            # Add metadata and attachments
            request.metadata = request_data.get("metadata", {})
            request.attachments = request_data.get("attachments", [])
            
            self.requests[request_id] = request
            
            # Auto-start if configured
            if workflow.auto_start:
                await self._start_request_processing(request)
            
            # Send notifications
            await self._notify_request_submitted(request)
            
            logger.info(f"Submitted approval request {request_id}: {request.title}")
            return request_id
            
        except Exception as e:
            logger.error(f"Error submitting approval request: {e}")
            raise
    
    async def provide_approval(self, request_id: str, reviewer_id: str, 
                             decision: bool, comments: str = "", 
                             conditions: List[str] = None) -> bool:
        """Provide approval decision for a request
        
        Args:
            request_id: Request identifier
            reviewer_id: Reviewer identifier
            decision: Approval decision (True = approve, False = reject)
            comments: Reviewer comments
            conditions: Conditional approval conditions
            
        Returns:
            Success status
        """
        try:
            request = self.requests.get(request_id)
            if not request:
                return False
            
            workflow = self.workflows.get(request.workflow_id)
            if not workflow:
                return False
            
            # Get current step
            if request.current_step >= len(workflow.steps):
                logger.warning(f"Request {request_id} already completed")
                return False
            
            current_step = workflow.steps[request.current_step]
            
            # Validate reviewer authorization
            if not self._is_authorized_reviewer(current_step, reviewer_id):
                logger.warning(f"Reviewer {reviewer_id} not authorized for step {current_step.name}")
                return False
            
            # Record approval
            current_step.approvals[reviewer_id] = decision
            
            # Add comment if provided
            if comments:
                comment = ReviewComment(
                    id=str(uuid.uuid4()),
                    reviewer_id=reviewer_id,
                    reviewer_role=self._get_reviewer_role(current_step, reviewer_id),
                    comment=comments,
                    timestamp=datetime.now(timezone.utc),
                    is_blocking=not decision
                )
                current_step.comments.append(comment)
            
            # Add conditions if conditional approval
            if decision and conditions:
                current_step.conditions.extend(conditions)
                current_step.status = ApprovalStatus.CONDITIONAL_APPROVAL
            
            # Check if step is complete
            step_complete = await self._check_step_completion(current_step)
            
            if step_complete:
                # Mark step as complete
                current_step.completed_at = datetime.now(timezone.utc)
                
                # Determine step result
                approvals = list(current_step.approvals.values())
                step_approved = sum(approvals) >= current_step.min_approvals
                
                if step_approved:
                    current_step.status = ApprovalStatus.APPROVED
                    await self._advance_to_next_step(request)
                else:
                    current_step.status = ApprovalStatus.REJECTED
                    request.status = ApprovalStatus.REJECTED
                    request.final_decision = False
                    request.decision_date = datetime.now(timezone.utc)
                    request.decision_by = reviewer_id
                    
                    await self._notify_request_rejected(request)
            
            # Update request
            request.updated_at = datetime.now(timezone.utc)
            await self._update_request_progress(request, workflow)
            
            # Send notifications
            await self._notify_approval_provided(request, reviewer_id, decision)
            
            logger.info(f"Approval provided for request {request_id} by {reviewer_id}: {decision}")
            return True
            
        except Exception as e:
            logger.error(f"Error providing approval: {e}")
            return False
    
    async def escalate_request(self, request_id: str, reason: EscalationReason, 
                             escalated_by: str, notes: str = "") -> bool:
        """Escalate an approval request
        
        Args:
            request_id: Request identifier
            reason: Escalation reason
            escalated_by: User escalating
            notes: Escalation notes
            
        Returns:
            Success status
        """
        try:
            request = self.requests.get(request_id)
            if not request:
                return False
            
            workflow = self.workflows.get(request.workflow_id)
            if not workflow:
                return False
            
            # Check escalation limits
            if len(request.escalations) >= workflow.max_escalations:
                logger.warning(f"Maximum escalations reached for request {request_id}")
                return False
            
            # Find applicable escalation rule
            escalation_rule = self._find_escalation_rule(workflow, reason)
            
            escalation = {
                "id": str(uuid.uuid4()),
                "reason": reason.value,
                "escalated_by": escalated_by,
                "escalated_at": datetime.now(timezone.utc).isoformat(),
                "notes": notes,
                "rule_id": escalation_rule.id if escalation_rule else None
            }
            
            request.escalations.append(escalation)
            request.status = ApprovalStatus.ESCALATED
            
            # Apply escalation actions
            if escalation_rule:
                # Boost priority
                if escalation_rule.priority_boost:
                    if request.priority == Priority.LOW:
                        request.priority = Priority.MEDIUM
                    elif request.priority == Priority.MEDIUM:
                        request.priority = Priority.HIGH
                    elif request.priority == Priority.HIGH:
                        request.priority = Priority.URGENT
                
                # Add escalation reviewers
                current_step = workflow.steps[request.current_step]
                current_step.required_reviewers.extend(escalation_rule.escalate_to)
            
            # Send notifications
            await self._notify_request_escalated(request, escalation)
            
            # Call escalation handlers
            for handler in self.escalation_handlers:
                try:
                    await handler(request, escalation)
                except Exception as e:
                    logger.warning(f"Escalation handler failed: {e}")
            
            logger.info(f"Escalated request {request_id} for reason: {reason.value}")
            return True
            
        except Exception as e:
            logger.error(f"Error escalating request: {e}")
            return False
    
    async def get_pending_approvals(self, reviewer_id: str) -> List[Dict[str, Any]]:
        """Get pending approvals for a reviewer
        
        Args:
            reviewer_id: Reviewer identifier
            
        Returns:
            List of pending approval requests
        """
        try:
            pending = []
            
            for request in self.requests.values():
                if request.status not in [ApprovalStatus.PENDING, ApprovalStatus.IN_REVIEW]:
                    continue
                
                workflow = self.workflows.get(request.workflow_id)
                if not workflow:
                    continue
                
                if request.current_step >= len(workflow.steps):
                    continue
                
                current_step = workflow.steps[request.current_step]
                
                # Check if reviewer is authorized for current step
                if self._is_authorized_reviewer(current_step, reviewer_id):
                    # Check if already provided approval
                    if reviewer_id not in current_step.approvals:
                        pending.append({
                            "request_id": request.id,
                            "title": request.title,
                            "description": request.description,
                            "content_type": request.content_type,
                            "priority": request.priority.value,
                            "requested_by": request.requested_by,
                            "requested_at": request.requested_at.isoformat(),
                            "due_date": request.due_date.isoformat() if request.due_date else None,
                            "current_step": current_step.name,
                            "step_description": current_step.description,
                            "sla_hours": current_step.sla_hours,
                            "overdue": self._is_overdue(request, current_step),
                            "business_justification": request.business_justification
                        })
            
            # Sort by priority and due date
            pending.sort(key=lambda x: (
                ["low", "medium", "high", "urgent", "critical"].index(x["priority"]),
                x.get("due_date", "9999-12-31")
            ), reverse=True)
            
            return pending
            
        except Exception as e:
            logger.error(f"Error getting pending approvals: {e}")
            return []
    
    async def get_request_status(self, request_id: str) -> Dict[str, Any]:
        """Get detailed status of approval request
        
        Args:
            request_id: Request identifier
            
        Returns:
            Request status information
        """
        try:
            request = self.requests.get(request_id)
            if not request:
                return {}
            
            workflow = self.workflows.get(request.workflow_id)
            if not workflow:
                return {}
            
            status = {
                "request": {
                    "id": request.id,
                    "title": request.title,
                    "description": request.description,
                    "status": request.status.value,
                    "priority": request.priority.value,
                    "progress": request.progress_percentage,
                    "requested_by": request.requested_by,
                    "requested_at": request.requested_at.isoformat(),
                    "due_date": request.due_date.isoformat() if request.due_date else None
                },
                "workflow": {
                    "id": workflow.id,
                    "name": workflow.name,
                    "type": workflow.type.value,
                    "total_steps": len(workflow.steps),
                    "current_step": request.current_step + 1
                },
                "steps": [],
                "escalations": request.escalations,
                "final_decision": request.final_decision
            }
            
            # Add step details
            for i, step in enumerate(workflow.steps):
                step_info = {
                    "step_number": step.step_number,
                    "name": step.name,
                    "description": step.description,
                    "status": step.status.value if i <= request.current_step else "pending",
                    "required_approvals": step.min_approvals,
                    "received_approvals": len([a for a in step.approvals.values() if a]),
                    "comments": len(step.comments),
                    "conditions": step.conditions,
                    "sla_hours": step.sla_hours,
                    "started_at": step.started_at.isoformat() if step.started_at else None,
                    "completed_at": step.completed_at.isoformat() if step.completed_at else None
                }
                
                if i == request.current_step:
                    step_info["is_current"] = True
                    step_info["overdue"] = self._is_overdue(request, step)
                
                status["steps"].append(step_info)
            
            return status
            
        except Exception as e:
            logger.error(f"Error getting request status: {e}")
            return {}
    
    async def get_approval_analytics(self, date_range: Tuple[datetime, datetime]) -> Dict[str, Any]:
        """Get approval analytics for date range
        
        Args:
            date_range: Start and end dates
            
        Returns:
            Analytics data
        """
        try:
            start_date, end_date = date_range
            
            # Filter requests in date range
            filtered_requests = [
                r for r in self.requests.values()
                if start_date <= r.requested_at <= end_date
            ]
            
            analytics = {
                "summary": {
                    "total_requests": len(filtered_requests),
                    "approved_requests": len([r for r in filtered_requests if r.final_decision is True]),
                    "rejected_requests": len([r for r in filtered_requests if r.final_decision is False]),
                    "pending_requests": len([r for r in filtered_requests if r.final_decision is None]),
                    "escalated_requests": len([r for r in filtered_requests if r.escalations])
                },
                "performance": {},
                "by_workflow": {},
                "by_priority": {},
                "response_times": {}
            }
            
            # Calculate approval rate
            total_completed = analytics["summary"]["approved_requests"] + analytics["summary"]["rejected_requests"]
            if total_completed > 0:
                analytics["summary"]["approval_rate"] = (analytics["summary"]["approved_requests"] / total_completed) * 100
            
            # Performance metrics
            if filtered_requests:
                processing_times = []
                for request in filtered_requests:
                    if request.decision_date:
                        processing_time = (request.decision_date - request.requested_at).total_seconds() / 3600
                        processing_times.append(processing_time)
                
                if processing_times:
                    analytics["performance"] = {
                        "avg_processing_time_hours": sum(processing_times) / len(processing_times),
                        "min_processing_time_hours": min(processing_times),
                        "max_processing_time_hours": max(processing_times)
                    }
            
            # Workflow breakdown
            workflow_stats = defaultdict(lambda: {"total": 0, "approved": 0, "rejected": 0})
            for request in filtered_requests:
                workflow_stats[request.workflow_id]["total"] += 1
                if request.final_decision is True:
                    workflow_stats[request.workflow_id]["approved"] += 1
                elif request.final_decision is False:
                    workflow_stats[request.workflow_id]["rejected"] += 1
            
            analytics["by_workflow"] = dict(workflow_stats)
            
            # Priority breakdown
            priority_stats = defaultdict(lambda: {"total": 0, "approved": 0, "rejected": 0})
            for request in filtered_requests:
                priority_stats[request.priority.value]["total"] += 1
                if request.final_decision is True:
                    priority_stats[request.priority.value]["approved"] += 1
                elif request.final_decision is False:
                    priority_stats[request.priority.value]["rejected"] += 1
            
            analytics["by_priority"] = dict(priority_stats)
            
            return analytics
            
        except Exception as e:
            logger.error(f"Error getting approval analytics: {e}")
            return {}
    
    async def _start_request_processing(self, request: ApprovalRequest):
        """Start processing an approval request"""
        workflow = self.workflows[request.workflow_id]
        
        if workflow.steps:
            request.status = ApprovalStatus.IN_REVIEW
            request.current_step = 0
            
            # Start first step
            first_step = workflow.steps[0]
            first_step.started_at = datetime.now(timezone.utc)
            first_step.status = ApprovalStatus.IN_REVIEW
            
            # Notify reviewers
            await self._notify_step_started(request, first_step)
    
    async def _advance_to_next_step(self, request: ApprovalRequest):
        """Advance request to next step or complete"""
        workflow = self.workflows[request.workflow_id]
        
        # Record step in history
        current_step = workflow.steps[request.current_step]
        request.step_history.append({
            "step_number": current_step.step_number,
            "step_name": current_step.name,
            "status": current_step.status.value,
            "completed_at": current_step.completed_at.isoformat() if current_step.completed_at else None,
            "approvals": current_step.approvals,
            "conditions": current_step.conditions
        })
        
        # Check if more steps
        if request.current_step + 1 < len(workflow.steps):
            # Move to next step
            request.current_step += 1
            next_step = workflow.steps[request.current_step]
            next_step.started_at = datetime.now(timezone.utc)
            next_step.status = ApprovalStatus.IN_REVIEW
            
            await self._notify_step_started(request, next_step)
        else:
            # Complete approval process
            request.status = ApprovalStatus.APPROVED
            request.final_decision = True
            request.decision_date = datetime.now(timezone.utc)
            request.progress_percentage = 100.0
            
            await self._notify_request_approved(request)
    
    async def _check_step_completion(self, step: ApprovalStep) -> bool:
        """Check if approval step is complete"""
        # Check if minimum approvals received
        approvals = [decision for decision in step.approvals.values() if decision]
        return len(approvals) >= step.min_approvals
    
    async def _update_request_progress(self, request: ApprovalRequest, workflow: ApprovalWorkflow):
        """Update request progress percentage"""
        if workflow.steps:
            completed_steps = request.current_step
            if request.status == ApprovalStatus.APPROVED:
                completed_steps = len(workflow.steps)
            
            request.progress_percentage = (completed_steps / len(workflow.steps)) * 100
    
    def _is_authorized_reviewer(self, step: ApprovalStep, reviewer_id: str) -> bool:
        """Check if reviewer is authorized for step"""
        return (reviewer_id in step.required_reviewers or 
                reviewer_id in step.optional_reviewers or
                not step.required_reviewers)  # Allow if no specific reviewers required
    
    def _get_reviewer_role(self, step: ApprovalStep, reviewer_id: str) -> ReviewerRole:
        """Get reviewer role for step"""
        # Simplified role detection
        if step.reviewer_roles:
            return step.reviewer_roles[0]
        return ReviewerRole.STAKEHOLDER
    
    def _is_overdue(self, request: ApprovalRequest, step: ApprovalStep) -> bool:
        """Check if step is overdue"""
        if not step.sla_hours or not step.started_at:
            return False
        
        deadline = step.started_at + timedelta(hours=step.sla_hours)
        return datetime.now(timezone.utc) > deadline
    
    def _find_escalation_rule(self, workflow: ApprovalWorkflow, reason: EscalationReason) -> Optional[EscalationRule]:
        """Find applicable escalation rule"""
        for rule in workflow.escalation_rules:
            if rule.trigger_condition == reason:
                return rule
        return None
    
    async def _notify_request_submitted(self, request: ApprovalRequest):
        """Send request submission notification"""
        for handler in self.notification_handlers:
            try:
                await handler("request_submitted", {
                    "request_id": request.id,
                    "title": request.title,
                    "requested_by": request.requested_by
                })
            except Exception as e:
                logger.warning(f"Notification handler failed: {e}")
    
    async def _notify_step_started(self, request: ApprovalRequest, step: ApprovalStep):
        """Send step started notification"""
        for handler in self.notification_handlers:
            try:
                await handler("step_started", {
                    "request_id": request.id,
                    "step_name": step.name,
                    "reviewers": step.required_reviewers + step.optional_reviewers
                })
            except Exception as e:
                logger.warning(f"Notification handler failed: {e}")
    
    async def _notify_approval_provided(self, request: ApprovalRequest, reviewer_id: str, decision: bool):
        """Send approval provided notification"""
        for handler in self.notification_handlers:
            try:
                await handler("approval_provided", {
                    "request_id": request.id,
                    "reviewer_id": reviewer_id,
                    "decision": decision
                })
            except Exception as e:
                logger.warning(f"Notification handler failed: {e}")
    
    async def _notify_request_approved(self, request: ApprovalRequest):
        """Send request approved notification"""
        for handler in self.notification_handlers:
            try:
                await handler("request_approved", {
                    "request_id": request.id,
                    "title": request.title,
                    "requested_by": request.requested_by
                })
            except Exception as e:
                logger.warning(f"Notification handler failed: {e}")
    
    async def _notify_request_rejected(self, request: ApprovalRequest):
        """Send request rejected notification"""
        for handler in self.notification_handlers:
            try:
                await handler("request_rejected", {
                    "request_id": request.id,
                    "title": request.title,
                    "requested_by": request.requested_by
                })
            except Exception as e:
                logger.warning(f"Notification handler failed: {e}")
    
    async def _notify_request_escalated(self, request: ApprovalRequest, escalation: Dict[str, Any]):
        """Send request escalated notification"""
        for handler in self.notification_handlers:
            try:
                await handler("request_escalated", {
                    "request_id": request.id,
                    "title": request.title,
                    "escalation": escalation
                })
            except Exception as e:
                logger.warning(f"Notification handler failed: {e}")
    
    def add_notification_handler(self, handler: Callable):
        """Add notification handler"""
        self.notification_handlers.append(handler)
    
    def add_escalation_handler(self, handler: Callable):
        """Add escalation handler"""
        self.escalation_handlers.append(handler)


# Convenience functions for easy usage
async def submit_content_approval(content_id: str, content_type: str, title: str,
                                requested_by: str, workflow_type: str = "content_review_standard") -> str:
    """Submit content for approval
    
    Args:
        content_id: Content identifier
        content_type: Type of content
        title: Approval request title
        requested_by: User requesting approval
        workflow_type: Workflow type to use
        
    Returns:
        Request ID
    """
    manager = ApprovalWorkflowManager()
    
    request_data = {
        "workflow_id": workflow_type,
        "content_id": content_id,
        "content_type": content_type,
        "title": title,
        "description": f"Approval request for {content_type}: {title}",
        "requested_by": requested_by,
        "priority": "medium"
    }
    
    return await manager.submit_approval_request(request_data)


async def approve_content(request_id: str, reviewer_id: str, approved: bool, 
                        comments: str = "") -> bool:
    """Provide approval decision
    
    Args:
        request_id: Request identifier
        reviewer_id: Reviewer identifier
        approved: Approval decision
        comments: Optional comments
        
    Returns:
        Success status
    """
    manager = ApprovalWorkflowManager()
    return await manager.provide_approval(request_id, reviewer_id, approved, comments)


async def get_my_pending_approvals(reviewer_id: str) -> List[Dict[str, Any]]:
    """Get pending approvals for reviewer
    
    Args:
        reviewer_id: Reviewer identifier
        
    Returns:
        List of pending approvals
    """
    manager = ApprovalWorkflowManager()
    return await manager.get_pending_approvals(reviewer_id)


if __name__ == "__main__":
    # Example usage
    async def main():
        # Create approval workflow manager
        manager = ApprovalWorkflowManager()
        
        # Submit approval request
        request_data = {
            "workflow_id": "content_review_standard",
            "content_id": "video_123",
            "content_type": "video",
            "title": "Marketing Campaign Video",
            "description": "Video for summer marketing campaign",
            "requested_by": "creator_1",
            "priority": "high",
            "business_justification": "Critical for campaign launch next week"
        }
        
        request_id = await manager.submit_approval_request(request_data)
        print(f"Submitted approval request: {request_id}")
        
        # Provide approval
        approved = await manager.provide_approval(
            request_id,
            "reviewer_1",
            True,
            "Content looks good, approved for publication"
        )
        print(f"Approval provided: {approved}")
        
        # Get request status
        status = await manager.get_request_status(request_id)
        print(f"Request status: {json.dumps(status, indent=2, default=str)}")
    
    asyncio.run(main())