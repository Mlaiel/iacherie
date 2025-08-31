"""Approval System Database Module

Enterprise approval workflow system with hierarchical approvals, 
automated routing, compliance tracking, and audit trail for 
multi-format content creators and collaboration teams.

Author: Fahed Mlaiel <mlaiel@live.de>
Project: IA Influencer Agent + Content Protection Platform
Copyright: All rights reserved. Unauthorized use, modification, or distribution prohibited.

🚨 INTELLECTUAL PROPERTY WARNING: This code, concept, and architecture are 
the exclusive intellectual property of Fahed Mlaiel (mlaiel@live.de). 
Any use, copying, distribution, or exploitation without explicit written 
authorization is STRICTLY PROHIBITED and will be prosecuted.

Expert Project Team - Fahed Mlaiel:
- Lead AI Developer & Software Architect
- Senior Backend Engineer (Python/FastAPI/Django)  
- Machine Learning Engineer (TensorFlow/PyTorch/Hugging Face)
- Database Administrator & Data Engineer (PostgreSQL/Redis/MongoDB)
- Backend Security Specialist
- Microservices Architect
- Audio Processing Engineer
- DevOps Engineer
- AI Prompt Engineer
"""
import uuid
import json
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, asdict
from enum import Enum
from decimal import Decimal
from sqlalchemy import Column, String, DateTime, JSON, Boolean, Integer, Text, Index, BigInteger, Numeric
from sqlalchemy.dialects.postgresql import UUID, ARRAY
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session
import asyncio
import logging

Base = declarative_base()
logger = logging.getLogger(__name__)


class ApprovalType(Enum):
    """Types of approval requests"""
    CONTENT_PUBLICATION = "content_publication"
    COLLABORATION_REQUEST = "collaboration_request"
    MONETIZATION_SETUP = "monetization_setup"
    BRAND_PARTNERSHIP = "brand_partnership"
    CONTRACT_AGREEMENT = "contract_agreement"
    BUDGET_ALLOCATION = "budget_allocation"
    PLATFORM_ACCESS = "platform_access"
    SENSITIVE_CONTENT = "sensitive_content"
    LEGAL_REVIEW = "legal_review"
    COMPLIANCE_CHECK = "compliance_check"
    CUSTOM_WORKFLOW = "custom_workflow"


class ApprovalStatus(Enum):
    """Approval request status"""
    PENDING = "pending"
    IN_REVIEW = "in_review"
    APPROVED = "approved"
    REJECTED = "rejected"
    CANCELLED = "cancelled"
    EXPIRED = "expired"
    ESCALATED = "escalated"
    CONDITIONAL = "conditional"
    DEFERRED = "deferred"


class ApprovalPriority(Enum):
    """Approval priority levels"""
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"
    CRITICAL = "critical"


class ApproverRole(Enum):
    """Approver role types"""
    CONTENT_MANAGER = "content_manager"
    LEGAL_COUNSEL = "legal_counsel"
    COMPLIANCE_OFFICER = "compliance_officer"
    FINANCIAL_CONTROLLER = "financial_controller"
    BRAND_MANAGER = "brand_manager"
    TECHNICAL_LEAD = "technical_lead"
    EXECUTIVE_SPONSOR = "executive_sponsor"
    EXTERNAL_REVIEWER = "external_reviewer"
    AUTOMATED_SYSTEM = "automated_system"


@dataclass
class ApprovalCriteria:
    """Approval decision criteria"""
    criterion_name: str
    required_value: Any
    actual_value: Any
    weight: float = 1.0
    is_met: bool = False


@dataclass
class ApprovalAction:
    """Approval workflow action"""
    action_type: str
    parameters: Dict[str, Any]
    condition: Optional[str] = None


class ApprovalWorkflow(Base):
    """
    Database model for approval workflow definitions
    """
    __tablename__ = "approval_workflows"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    workflow_name = Column(String(200), nullable=False)
    workflow_description = Column(Text)
    organization_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    
    # Workflow configuration
    approval_type = Column(String(50), nullable=False)
    workflow_definition = Column(JSON, nullable=False)  # Steps, conditions, routing
    default_priority = Column(String(20), default="normal")
    auto_escalation_enabled = Column(Boolean, default=True)
    
    # Routing rules
    routing_rules = Column(JSON, nullable=False)  # How to route requests
    fallback_approvers = Column(JSON)  # Backup approvers
    delegation_rules = Column(JSON)  # Delegation configuration
    
    # Timing constraints
    default_sla_hours = Column(Integer, default=72)  # Default SLA in hours
    escalation_threshold_hours = Column(Integer, default=48)
    expiration_hours = Column(Integer, default=168)  # 1 week default
    reminder_intervals = Column(JSON)  # When to send reminders
    
    # Compliance and audit
    compliance_requirements = Column(JSON)  # Regulatory requirements
    audit_trail_required = Column(Boolean, default=True)
    retention_policy = Column(JSON)  # Data retention rules
    
    # Conditional logic
    approval_criteria = Column(JSON)  # Automated approval criteria
    bypass_conditions = Column(JSON)  # When to bypass approval
    parallel_approval_enabled = Column(Boolean, default=False)
    
    # Performance metrics
    average_approval_time = Column(Integer, default=0)  # Hours
    approval_rate = Column(Numeric(5, 4), default=1.0)
    total_requests = Column(Integer, default=0)
    
    # Status and lifecycle
    is_active = Column(Boolean, default=True, nullable=False)
    version = Column(String(20), default="1.0.0")
    last_modified_by = Column(UUID(as_uuid=True))
    
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    
    __table_args__ = (
        Index('idx_approval_workflow_org', 'organization_id'),
        Index('idx_approval_workflow_type', 'approval_type'),
        Index('idx_approval_workflow_active', 'is_active'),
    )


class ApprovalRequest(Base):
    """
    Database model for individual approval requests
    """
    __tablename__ = "approval_requests"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    workflow_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    request_title = Column(String(300), nullable=False)
    request_description = Column(Text)
    
    # Request metadata
    requester_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    organization_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    approval_type = Column(String(50), nullable=False)
    priority = Column(String(20), default="normal", nullable=False)
    
    # Request content
    request_data = Column(JSON, nullable=False)  # What needs approval
    supporting_documents = Column(JSON)  # Document references
    context_information = Column(JSON)  # Additional context
    
    # Status and routing
    status = Column(String(20), default="pending", nullable=False)
    current_step = Column(Integer, default=1)
    total_steps = Column(Integer, nullable=False)
    current_approvers = Column(ARRAY(UUID))
    
    # Timing information
    submitted_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    due_date = Column(DateTime(timezone=True), nullable=False)
    escalation_date = Column(DateTime(timezone=True))
    expiration_date = Column(DateTime(timezone=True))
    
    # Decision tracking
    approved_by = Column(ARRAY(UUID))
    rejected_by = Column(ARRAY(UUID))
    final_decision = Column(String(20))
    decision_rationale = Column(Text)
    
    # Performance metrics
    approval_duration_hours = Column(Integer)
    escalation_count = Column(Integer, default=0)
    reminder_count = Column(Integer, default=0)
    
    # Related entities
    related_content_id = Column(UUID(as_uuid=True))  # Content being approved
    related_workflow_id = Column(UUID(as_uuid=True))  # Related workflow
    parent_request_id = Column(UUID(as_uuid=True))  # Parent approval if nested
    
    # Compliance tracking
    compliance_flags = Column(JSON)
    risk_assessment = Column(JSON)
    regulatory_requirements = Column(JSON)
    
    completed_at = Column(DateTime(timezone=True))
    is_active = Column(Boolean, default=True, nullable=False)
    
    __table_args__ = (
        Index('idx_approval_req_workflow', 'workflow_id'),
        Index('idx_approval_req_requester', 'requester_id'),
        Index('idx_approval_req_org', 'organization_id'),
        Index('idx_approval_req_status', 'status'),
        Index('idx_approval_req_priority', 'priority'),
        Index('idx_approval_req_due', 'due_date'),
        Index('idx_approval_req_content', 'related_content_id'),
    )


class ApprovalStep(Base):
    """
    Database model for individual approval workflow steps
    """
    __tablename__ = "approval_steps"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    approval_request_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    step_number = Column(Integer, nullable=False)
    step_name = Column(String(200), nullable=False)
    
    # Step configuration
    step_type = Column(String(50), nullable=False)  # manual, automated, conditional
    required_approver_count = Column(Integer, default=1)
    approver_roles = Column(ARRAY(String))
    specific_approvers = Column(ARRAY(UUID))
    
    # Step status
    status = Column(String(20), default="pending", nullable=False)
    assigned_approvers = Column(ARRAY(UUID))
    completed_approvers = Column(ARRAY(UUID))
    
    # Decision criteria
    approval_criteria = Column(JSON)
    bypass_conditions = Column(JSON)
    escalation_rules = Column(JSON)
    
    # Timing
    started_at = Column(DateTime(timezone=True))
    due_date = Column(DateTime(timezone=True))
    completed_at = Column(DateTime(timezone=True))
    duration_hours = Column(Integer)
    
    # Step results
    step_decision = Column(String(20))  # approved, rejected, conditional
    decision_notes = Column(Text)
    conditions_attached = Column(JSON)
    
    # Automated evaluation
    automated_score = Column(Numeric(5, 2))
    automated_recommendation = Column(String(20))
    ai_confidence = Column(Numeric(3, 2))
    
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    
    __table_args__ = (
        Index('idx_approval_step_request', 'approval_request_id'),
        Index('idx_approval_step_number', 'step_number'),
        Index('idx_approval_step_status', 'status'),
        Index('idx_approval_step_due', 'due_date'),
    )


class ApprovalDecision(Base):
    """
    Database model for individual approval decisions
    """
    __tablename__ = "approval_decisions"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    approval_request_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    approval_step_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    
    # Decision details
    approver_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    approver_role = Column(String(50), nullable=False)
    decision = Column(String(20), nullable=False)  # approved, rejected, conditional
    
    # Decision content
    decision_rationale = Column(Text)
    conditions = Column(JSON)  # Conditions if conditional approval
    recommendations = Column(JSON)
    risk_assessment = Column(JSON)
    
    # Decision context
    decision_criteria_met = Column(JSON)  # Which criteria were evaluated
    supporting_evidence = Column(JSON)
    alternative_suggestions = Column(JSON)
    
    # Timing and metadata
    decision_timestamp = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    time_to_decision_hours = Column(Integer)
    decision_confidence = Column(Numeric(3, 2))  # Approver confidence 0-1
    
    # Delegation information
    delegated_from = Column(UUID(as_uuid=True))  # If decision was delegated
    delegation_reason = Column(String(200))
    
    # Compliance and audit
    compliance_checked = Column(Boolean, default=False)
    regulatory_notes = Column(Text)
    audit_trail = Column(JSON)
    
    # Follow-up actions
    follow_up_required = Column(Boolean, default=False)
    follow_up_actions = Column(JSON)
    follow_up_due_date = Column(DateTime(timezone=True))
    
    is_active = Column(Boolean, default=True, nullable=False)
    
    __table_args__ = (
        Index('idx_approval_decision_request', 'approval_request_id'),
        Index('idx_approval_decision_step', 'approval_step_id'),
        Index('idx_approval_decision_approver', 'approver_id'),
        Index('idx_approval_decision_timestamp', 'decision_timestamp'),
        Index('idx_approval_decision_type', 'decision'),
    )


class ApprovalDelegate(Base):
    """
    Database model for approval delegation relationships
    """
    __tablename__ = "approval_delegates"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    delegator_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    delegate_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    organization_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    
    # Delegation scope
    approval_types = Column(ARRAY(String))  # Which approval types can be delegated
    workflows = Column(ARRAY(UUID))  # Specific workflows
    priority_levels = Column(ARRAY(String))  # Which priority levels
    
    # Delegation constraints
    is_active = Column(Boolean, default=True, nullable=False)
    effective_from = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    effective_until = Column(DateTime(timezone=True))
    max_approval_amount = Column(Numeric(15, 2))  # For financial approvals
    
    # Delegation rules
    require_notification = Column(Boolean, default=True)
    auto_delegate = Column(Boolean, default=False)
    delegation_conditions = Column(JSON)
    
    # Usage tracking
    total_delegations = Column(Integer, default=0)
    last_used = Column(DateTime(timezone=True))
    
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    created_by = Column(UUID(as_uuid=True), nullable=False)
    
    __table_args__ = (
        Index('idx_approval_delegate_delegator', 'delegator_id'),
        Index('idx_approval_delegate_delegate', 'delegate_id'),
        Index('idx_approval_delegate_org', 'organization_id'),
        Index('idx_approval_delegate_active', 'is_active'),
        Index('idx_approval_delegate_effective', 'effective_from', 'effective_until'),
    )


class ApprovalSystemManager:
    """
    Enterprise approval system manager with automated routing and AI assistance
    """
    
    def __init__(self, db_session: Session):
        self.db_session = db_session
        self.notification_service = NotificationService()
        self.ai_evaluator = AIApprovalEvaluator(db_session)
        self.compliance_checker = ComplianceChecker()
    
    async def create_approval_workflow(
        self,
        workflow_name: str,
        organization_id: str,
        approval_type: ApprovalType,
        workflow_definition: Dict[str, Any],
        routing_rules: Dict[str, Any],
        metadata: Dict[str, Any] = None
    ) -> str:
        """
        Create new approval workflow
        
        Args:
            workflow_name: Name of the workflow
            organization_id: Organization ID
            approval_type: Type of approval workflow
            workflow_definition: Workflow steps and logic
            routing_rules: Approval routing configuration
            metadata: Additional workflow metadata
            
        Returns:
            Workflow ID
        """
        workflow = ApprovalWorkflow(
            workflow_name=workflow_name,
            workflow_description=metadata.get('description', '') if metadata else '',
            organization_id=organization_id,
            approval_type=approval_type.value,
            workflow_definition=workflow_definition,
            default_priority=metadata.get('default_priority', 'normal') if metadata else 'normal',
            routing_rules=routing_rules,
            fallback_approvers=metadata.get('fallback_approvers') if metadata else None,
            delegation_rules=metadata.get('delegation_rules', {}) if metadata else {},
            default_sla_hours=metadata.get('sla_hours', 72) if metadata else 72,
            escalation_threshold_hours=metadata.get('escalation_hours', 48) if metadata else 48,
            expiration_hours=metadata.get('expiration_hours', 168) if metadata else 168,
            compliance_requirements=metadata.get('compliance_requirements', {}) if metadata else {},
            approval_criteria=metadata.get('approval_criteria', {}) if metadata else {},
            bypass_conditions=metadata.get('bypass_conditions', {}) if metadata else {},
            parallel_approval_enabled=metadata.get('parallel_approval', False) if metadata else False
        )
        
        self.db_session.add(workflow)
        self.db_session.commit()
        
        logger.info(f"Created approval workflow: {workflow.id} - {workflow_name}")
        return str(workflow.id)
    
    async def submit_approval_request(
        self,
        workflow_id: str,
        requester_id: str,
        request_title: str,
        request_data: Dict[str, Any],
        priority: ApprovalPriority = ApprovalPriority.NORMAL,
        metadata: Dict[str, Any] = None
    ) -> str:
        """
        Submit new approval request
        
        Args:
            workflow_id: Workflow to use
            requester_id: User submitting request
            request_title: Title of the request
            request_data: Data requiring approval
            priority: Request priority level
            metadata: Additional request metadata
            
        Returns:
            Request ID
        """
        # Get workflow configuration
        workflow = self.db_session.query(ApprovalWorkflow).filter(
            ApprovalWorkflow.id == workflow_id,
            ApprovalWorkflow.is_active == True
        ).first()
        
        if not workflow:
            raise ValueError(f"Workflow not found: {workflow_id}")
        
        # Calculate timing
        now = datetime.now(timezone.utc)
        due_date = now + timedelta(hours=workflow.default_sla_hours)
        escalation_date = now + timedelta(hours=workflow.escalation_threshold_hours)
        expiration_date = now + timedelta(hours=workflow.expiration_hours)
        
        # Determine workflow steps
        workflow_steps = workflow.workflow_definition.get('steps', [])
        total_steps = len(workflow_steps)
        
        # Check for bypass conditions
        if await self._check_bypass_conditions(workflow, request_data):
            # Auto-approve if bypass conditions are met
            request_status = "approved"
            current_step = total_steps
        else:
            request_status = "pending"
            current_step = 1
        
        # Create approval request
        request = ApprovalRequest(
            workflow_id=workflow_id,
            request_title=request_title,
            request_description=metadata.get('description', '') if metadata else '',
            requester_id=requester_id,
            organization_id=workflow.organization_id,
            approval_type=workflow.approval_type,
            priority=priority.value,
            request_data=request_data,
            supporting_documents=metadata.get('documents', []) if metadata else [],
            context_information=metadata.get('context', {}) if metadata else {},
            status=request_status,
            current_step=current_step,
            total_steps=total_steps,
            due_date=due_date,
            escalation_date=escalation_date,
            expiration_date=expiration_date,
            related_content_id=metadata.get('content_id') if metadata else None,
            related_workflow_id=metadata.get('related_workflow_id') if metadata else None,
            compliance_flags=metadata.get('compliance_flags', {}) if metadata else {},
            risk_assessment=metadata.get('risk_assessment', {}) if metadata else {}
        )
        
        self.db_session.add(request)
        self.db_session.commit()
        
        if request_status == "approved":
            # Handle auto-approval
            await self._complete_approval_request(str(request.id), "approved", "Auto-approved via bypass conditions")
        else:
            # Start approval workflow
            await self._initiate_approval_workflow(str(request.id))
        
        # Update workflow statistics
        workflow.total_requests += 1
        self.db_session.commit()
        
        logger.info(f"Submitted approval request: {request.id} - {request_title}")
        return str(request.id)
    
    async def process_approval_decision(
        self,
        request_id: str,
        approver_id: str,
        decision: ApprovalStatus,
        rationale: str,
        conditions: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Process approval decision from approver
        
        Args:
            request_id: Request being decided on
            approver_id: User making decision
            decision: Approval decision
            rationale: Decision rationale
            conditions: Conditions if conditional approval
            
        Returns:
            Decision processing result
        """
        # Get approval request and current step
        request = self.db_session.query(ApprovalRequest).filter(
            ApprovalRequest.id == request_id
        ).first()
        
        if not request:
            raise ValueError(f"Approval request not found: {request_id}")
        
        if request.status not in ["pending", "in_review"]:
            raise ValueError(f"Request is not in approvable state: {request.status}")
        
        # Get current approval step
        current_step = self.db_session.query(ApprovalStep).filter(
            ApprovalStep.approval_request_id == request_id,
            ApprovalStep.step_number == request.current_step,
            ApprovalStep.status.in_(["pending", "in_review"])
        ).first()
        
        if not current_step:
            raise ValueError("No active approval step found")
        
        # Verify approver authorization
        if not await self._verify_approver_authorization(current_step, approver_id):
            raise ValueError("User is not authorized to approve this step")
        
        # Record decision
        decision_record = ApprovalDecision(
            approval_request_id=request_id,
            approval_step_id=current_step.id,
            approver_id=approver_id,
            approver_role=await self._get_approver_role(approver_id, current_step),
            decision=decision.value,
            decision_rationale=rationale,
            conditions=conditions or {},
            time_to_decision_hours=self._calculate_decision_time(current_step),
            decision_confidence=1.0,  # Would calculate based on various factors
            compliance_checked=await self.compliance_checker.check_decision_compliance(
                request, decision, approver_id
            )
        )
        
        self.db_session.add(decision_record)
        
        # Update step status
        if approver_id not in (current_step.completed_approvers or []):
            current_step.completed_approvers = (current_step.completed_approvers or []) + [approver_id]
        
        # Check if step is complete
        required_approvers = current_step.required_approver_count
        completed_approvers = len(current_step.completed_approvers or [])
        
        step_complete = False
        step_decision = None
        
        if decision in [ApprovalStatus.REJECTED, ApprovalStatus.CANCELLED]:
            # Step fails immediately on rejection
            step_complete = True
            step_decision = decision.value
            current_step.status = "completed"
            current_step.step_decision = decision.value
            current_step.completed_at = datetime.now(timezone.utc)
        elif completed_approvers >= required_approvers:
            # Step is complete
            step_complete = True
            step_decision = "approved"
            current_step.status = "completed"
            current_step.step_decision = "approved"
            current_step.completed_at = datetime.now(timezone.utc)
        
        self.db_session.commit()
        
        # Process workflow continuation
        if step_complete:
            if step_decision == "approved":
                await self._advance_approval_workflow(request)
            else:
                await self._complete_approval_request(request_id, step_decision, rationale)
        
        return {
            'decision_recorded': True,
            'step_complete': step_complete,
            'workflow_status': request.status,
            'next_step': request.current_step if not step_complete else None
        }
    
    async def _initiate_approval_workflow(self, request_id: str):
        """Initialize approval workflow steps"""
        request = self.db_session.query(ApprovalRequest).filter(
            ApprovalRequest.id == request_id
        ).first()
        
        workflow = self.db_session.query(ApprovalWorkflow).filter(
            ApprovalWorkflow.id == request.workflow_id
        ).first()
        
        # Create all workflow steps
        workflow_steps = workflow.workflow_definition.get('steps', [])
        
        for i, step_def in enumerate(workflow_steps, 1):
            # Determine step approvers
            approvers = await self._determine_step_approvers(
                step_def, request, workflow
            )
            
            step = ApprovalStep(
                approval_request_id=request_id,
                step_number=i,
                step_name=step_def.get('name', f'Step {i}'),
                step_type=step_def.get('type', 'manual'),
                required_approver_count=step_def.get('required_approvers', 1),
                approver_roles=step_def.get('roles', []),
                specific_approvers=step_def.get('specific_approvers', []),
                assigned_approvers=approvers,
                approval_criteria=step_def.get('criteria', {}),
                bypass_conditions=step_def.get('bypass_conditions', {}),
                due_date=datetime.now(timezone.utc) + timedelta(
                    hours=step_def.get('sla_hours', 24)
                ),
                status="pending" if i == 1 else "waiting"
            )
            
            self.db_session.add(step)
        
        # Start first step
        if workflow_steps:
            first_step = self.db_session.query(ApprovalStep).filter(
                ApprovalStep.approval_request_id == request_id,
                ApprovalStep.step_number == 1
            ).first()
            
            if first_step:
                first_step.status = "in_review"
                first_step.started_at = datetime.now(timezone.utc)
                
                # Notify approvers
                await self.notification_service.notify_approvers(
                    first_step.assigned_approvers, request, first_step
                )
        
        request.status = "in_review"
        self.db_session.commit()
    
    async def _advance_approval_workflow(self, request: ApprovalRequest):
        """Advance to next step in approval workflow"""
        if request.current_step >= request.total_steps:
            # Workflow complete - approve request
            await self._complete_approval_request(
                str(request.id), "approved", "All approval steps completed"
            )
            return
        
        # Move to next step
        request.current_step += 1
        next_step = self.db_session.query(ApprovalStep).filter(
            ApprovalStep.approval_request_id == request.id,
            ApprovalStep.step_number == request.current_step
        ).first()
        
        if next_step:
            next_step.status = "in_review"
            next_step.started_at = datetime.now(timezone.utc)
            
            # Check for automated evaluation
            if next_step.step_type == "automated":
                auto_result = await self.ai_evaluator.evaluate_step(
                    request, next_step
                )
                
                if auto_result['decision'] != 'manual_review_required':
                    # Auto-complete this step
                    await self._auto_complete_step(next_step, auto_result)
                    return
            
            # Notify approvers for manual review
            await self.notification_service.notify_approvers(
                next_step.assigned_approvers, request, next_step
            )
        
        self.db_session.commit()
    
    async def _complete_approval_request(
        self,
        request_id: str,
        final_decision: str,
        rationale: str
    ):
        """Complete approval request with final decision"""
        request = self.db_session.query(ApprovalRequest).filter(
            ApprovalRequest.id == request_id
        ).first()
        
        request.status = final_decision
        request.final_decision = final_decision
        request.decision_rationale = rationale
        request.completed_at = datetime.now(timezone.utc)
        request.approval_duration_hours = int(
            (request.completed_at - request.submitted_at).total_seconds() / 3600
        )
        
        # Update workflow statistics
        workflow = self.db_session.query(ApprovalWorkflow).filter(
            ApprovalWorkflow.id == request.workflow_id
        ).first()
        
        if workflow:
            if final_decision == "approved":
                workflow.approval_rate = (
                    (workflow.approval_rate * (workflow.total_requests - 1) + 1.0) /
                    workflow.total_requests
                )
            
            workflow.average_approval_time = int(
                (workflow.average_approval_time * (workflow.total_requests - 1) + 
                 request.approval_duration_hours) / workflow.total_requests
            )
        
        # Send completion notifications
        await self.notification_service.notify_completion(request, final_decision)
        
        self.db_session.commit()
        logger.info(f"Completed approval request: {request_id} - {final_decision}")
    
    async def _check_bypass_conditions(
        self,
        workflow: ApprovalWorkflow,
        request_data: Dict[str, Any]
    ) -> bool:
        """Check if request meets bypass conditions"""
        bypass_conditions = workflow.bypass_conditions or {}
        
        # Simplified bypass logic - would be more sophisticated in production
        for condition_name, condition_def in bypass_conditions.items():
            field = condition_def.get('field')
            operator = condition_def.get('operator')
            value = condition_def.get('value')
            
            if field in request_data:
                actual_value = request_data[field]
                
                if operator == 'less_than' and isinstance(actual_value, (int, float)):
                    if actual_value >= value:
                        return False
                elif operator == 'equals' and actual_value != value:
                    return False
        
        return len(bypass_conditions) > 0  # Only bypass if conditions exist and all pass
    
    async def _determine_step_approvers(
        self,
        step_def: Dict[str, Any],
        request: ApprovalRequest,
        workflow: ApprovalWorkflow
    ) -> List[str]:
        """Determine who should approve this step"""
        approvers = []
        
        # Add specific approvers
        if 'specific_approvers' in step_def:
            approvers.extend(step_def['specific_approvers'])
        
        # Add role-based approvers (would query user roles)
        if 'roles' in step_def:
            role_approvers = await self._get_users_by_roles(
                step_def['roles'], workflow.organization_id
            )
            approvers.extend(role_approvers)
        
        # Remove duplicates
        return list(set(approvers))
    
    async def _verify_approver_authorization(
        self,
        step: ApprovalStep,
        approver_id: str
    ) -> bool:
        """Verify user is authorized to approve this step"""
        if not step.assigned_approvers:
            return False
        
        return approver_id in step.assigned_approvers
    
    async def _get_approver_role(
        self,
        approver_id: str,
        step: ApprovalStep
    ) -> str:
        """Get approver's role for this step"""
        # Would query user's actual role
        return "content_manager"  # Simplified
    
    def _calculate_decision_time(self, step: ApprovalStep) -> int:
        """Calculate time taken to make decision"""
        if not step.started_at:
            return 0
        
        return int(
            (datetime.now(timezone.utc) - step.started_at).total_seconds() / 3600
        )
    
    async def _get_users_by_roles(
        self,
        roles: List[str],
        organization_id: str
    ) -> List[str]:
        """Get users with specific roles in organization"""
        # Would query user management system
        return []  # Simplified
    
    async def _auto_complete_step(
        self,
        step: ApprovalStep,
        auto_result: Dict[str, Any]
    ):
        """Auto-complete step based on AI evaluation"""
        step.status = "completed"
        step.step_decision = auto_result['decision']
        step.completed_at = datetime.now(timezone.utc)
        step.automated_score = auto_result.get('score', 0.0)
        step.automated_recommendation = auto_result['decision']
        step.ai_confidence = auto_result.get('confidence', 0.0)
        
        # Continue workflow
        request = self.db_session.query(ApprovalRequest).filter(
            ApprovalRequest.id == step.approval_request_id
        ).first()
        
        if auto_result['decision'] == 'approved':
            await self._advance_approval_workflow(request)
        else:
            await self._complete_approval_request(
                str(request.id), auto_result['decision'], 
                auto_result.get('rationale', 'Automated decision')
            )


class NotificationService:
    """Notification service for approval system"""
    
    async def notify_approvers(
        self,
        approver_ids: List[str],
        request: ApprovalRequest,
        step: ApprovalStep
    ):
        """Notify approvers of pending approval"""
        # Implementation would send notifications
        pass
    
    async def notify_completion(
        self,
        request: ApprovalRequest,
        decision: str
    ):
        """Notify requester of completion"""
        # Implementation would send completion notification
        pass


class AIApprovalEvaluator:
    """AI-powered approval evaluation system"""
    
    def __init__(self, db_session: Session):
        self.db_session = db_session
    
    async def evaluate_step(
        self,
        request: ApprovalRequest,
        step: ApprovalStep
    ) -> Dict[str, Any]:
        """Evaluate step using AI"""
        # Simplified AI evaluation
        return {
            'decision': 'approved',
            'confidence': 0.85,
            'score': 0.9,
            'rationale': 'AI evaluation completed successfully'
        }


class ComplianceChecker:
    """Compliance checking system"""
    
    async def check_decision_compliance(
        self,
        request: ApprovalRequest,
        decision: ApprovalStatus,
        approver_id: str
    ) -> bool:
        """Check if decision meets compliance requirements"""
        # Implementation would check compliance rules
        return True
