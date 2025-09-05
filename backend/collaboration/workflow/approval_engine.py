"""Approval Engine - Intelligent Workflow Approval and Authorization System
=========================================================================

Advanced approval workflow system providing:
- Multi-level approval workflows
- Automated approval decisions
- Role-based approval routing
- Escalation policies and rules
- Approval analytics and insights
- Integration with project milestones

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️ STRICT COPYRIGHT WARNING - INTELLECTUAL PROPERTY PROTECTION
================================================================
This code and concept are the EXCLUSIVE PROPERTY of Fahed Mlaiel.
Unauthorized access, copying, modification, distribution, reverse engineering,
or commercialization without explicit written permission from Fahed Mlaiel
(mlaiel@live.de) is STRICTLY PROHIBITED and will result in immediate legal
action under German and International copyright laws.
"""

import asyncio
import logging
import numpy as np
from typing import Dict, List, Optional, Any, Tuple, Set, Union
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta
import json
import uuid
from collections import defaultdict

logger = logging.getLogger(__name__)


class ApprovalType(Enum):
    """Types of approval requests"""
    PROJECT_MILESTONE = "project_milestone"
    BUDGET_APPROVAL = "budget_approval"
    QUALITY_GATE = "quality_gate"
    DELIVERABLE_REVIEW = "deliverable_review"
    CHANGE_REQUEST = "change_request"
    RESOURCE_REQUEST = "resource_request"
    CONTRACT_APPROVAL = "contract_approval"
    CONTENT_APPROVAL = "content_approval"


class ApprovalStatus(Enum):
    """Status of approval requests"""
    PENDING = "pending"
    IN_REVIEW = "in_review"
    APPROVED = "approved"
    REJECTED = "rejected"
    ESCALATED = "escalated"
    EXPIRED = "expired"
    WITHDRAWN = "withdrawn"
    CONDITIONAL = "conditional"


class ApprovalPriority(Enum):
    """Priority levels for approval requests"""
    LOW = 1
    NORMAL = 2
    HIGH = 3
    URGENT = 4
    CRITICAL = 5


class EscalationTrigger(Enum):
    """Triggers for approval escalation"""
    TIMEOUT = "timeout"
    REJECTION = "rejection"
    COMPLEXITY = "complexity"
    VALUE_THRESHOLD = "value_threshold"
    MANUAL = "manual"
    RISK_LEVEL = "risk_level"


@dataclass
class ApprovalRule:
    """Approval rule definition"""
    rule_id: str
    name: str
    approval_type: ApprovalType
    conditions: Dict[str, Any]
    required_approvers: List[str]
    minimum_approvals: int
    maximum_rejections: int
    timeout_hours: float = 24.0
    auto_approve_conditions: Dict[str, Any] = field(default_factory=dict)
    escalation_rules: List[Dict[str, Any]] = field(default_factory=list)
    
    def __post_init__(self):
        if not self.rule_id:
            self.rule_id = str(uuid.uuid4())


@dataclass
class ApprovalRequest:
    """Approval request definition"""
    request_id: str
    approval_type: ApprovalType
    title: str
    description: str
    requester_id: str
    project_id: Optional[str] = None
    data: Dict[str, Any] = field(default_factory=dict)
    priority: ApprovalPriority = ApprovalPriority.NORMAL
    deadline: Optional[datetime] = None
    status: ApprovalStatus = ApprovalStatus.PENDING
    created_at: datetime = field(default_factory=datetime.now)
    
    def __post_init__(self):
        if not self.request_id:
            self.request_id = str(uuid.uuid4())


@dataclass
class ApprovalDecision:
    """Individual approval decision"""
    decision_id: str
    request_id: str
    approver_id: str
    decision: str  # "approved", "rejected", "conditional"
    comments: str = ""
    conditions: List[str] = field(default_factory=list)
    timestamp: datetime = field(default_factory=datetime.now)
    confidence_score: float = 1.0
    
    def __post_init__(self):
        if not self.decision_id:
            self.decision_id = str(uuid.uuid4())


@dataclass
class AutomatedApproval:
    """Automated approval logic result"""
    approval_id: str
    request_id: str
    decision: str
    reasoning: List[str]
    confidence: float
    rules_applied: List[str]
    timestamp: datetime = field(default_factory=datetime.now)
    
    def __post_init__(self):
        if not self.approval_id:
            self.approval_id = str(uuid.uuid4())


@dataclass
class EscalationPolicy:
    """Escalation policy definition"""
    policy_id: str
    name: str
    triggers: List[EscalationTrigger]
    escalation_chain: List[str]  # User IDs in order
    timeout_hours: float = 24.0
    conditions: Dict[str, Any] = field(default_factory=dict)
    notification_settings: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        if not self.policy_id:
            self.policy_id = str(uuid.uuid4())


@dataclass
class ApprovalWorkflow:
    """Complete approval workflow"""
    workflow_id: str
    name: str
    approval_type: ApprovalType
    stages: List[Dict[str, Any]]
    rules: List[ApprovalRule]
    escalation_policies: List[EscalationPolicy]
    automation_rules: Dict[str, Any] = field(default_factory=dict)
    analytics: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        if not self.workflow_id:
            self.workflow_id = str(uuid.uuid4())


class ApprovalEngine:
    """
    Intelligent Approval and Authorization Engine
    
    Provides automated approval workflows, intelligent routing,
    and escalation management for collaboration projects.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize the approval engine"""
        self.config = config or {}
        
        # Engine settings
        self.auto_approval_threshold = self.config.get('auto_approval_threshold', 0.8)
        self.default_timeout_hours = self.config.get('default_timeout_hours', 24.0)
        self.max_escalation_levels = self.config.get('max_escalation_levels', 3)
        
        # User roles and permissions
        self.user_roles = self.config.get('user_roles', {})
        self.approval_permissions = self.config.get('approval_permissions', {})
        
        # Data storage
        self.workflows = {}
        self.approval_rules = {}
        self.requests = {}
        self.decisions = {}
        self.escalation_policies = {}
        
        # Analytics
        self.approval_metrics = defaultdict(dict)
        self.performance_stats = defaultdict(list)
        
        logger.info("ApprovalEngine initialized with intelligent workflow management")
    
    async def create_approval_workflow(
        self,
        name: str,
        approval_type: ApprovalType,
        stages: List[Dict[str, Any]],
        automation_rules: Optional[Dict[str, Any]] = None
    ) -> ApprovalWorkflow:
        """
        Create a new approval workflow
        
        Args:
            name: Workflow name
            approval_type: Type of approvals this workflow handles
            stages: List of workflow stages
            automation_rules: Rules for automated decisions
            
        Returns:
            Created approval workflow
        """
        try:
            # Create workflow rules
            rules = []
            for stage in stages:
                rule = ApprovalRule(
                    rule_id=str(uuid.uuid4()),
                    name=stage['name'],
                    approval_type=approval_type,
                    conditions=stage.get('conditions', {}),
                    required_approvers=stage.get('approvers', []),
                    minimum_approvals=stage.get('min_approvals', 1),
                    maximum_rejections=stage.get('max_rejections', 1),
                    timeout_hours=stage.get('timeout_hours', self.default_timeout_hours),
                    auto_approve_conditions=stage.get('auto_approve', {}),
                    escalation_rules=stage.get('escalation', [])
                )
                rules.append(rule)
                self.approval_rules[rule.rule_id] = rule
            
            # Create default escalation policies
            escalation_policies = await self._create_default_escalation_policies(
                approval_type
            )
            
            workflow = ApprovalWorkflow(
                workflow_id=str(uuid.uuid4()),
                name=name,
                approval_type=approval_type,
                stages=stages,
                rules=rules,
                escalation_policies=escalation_policies,
                automation_rules=automation_rules or {}
            )
            
            self.workflows[workflow.workflow_id] = workflow
            
            logger.info(f"Approval workflow '{name}' created with {len(stages)} stages")
            return workflow
            
        except Exception as e:
            logger.error(f"Failed to create approval workflow: {str(e)}")
            raise
    
    async def submit_approval_request(
        self,
        approval_type: ApprovalType,
        title: str,
        description: str,
        requester_id: str,
        data: Dict[str, Any],
        project_id: Optional[str] = None,
        priority: ApprovalPriority = ApprovalPriority.NORMAL,
        deadline: Optional[datetime] = None
    ) -> ApprovalRequest:
        """
        Submit a new approval request
        
        Args:
            approval_type: Type of approval needed
            title: Request title
            description: Detailed description
            requester_id: ID of the requester
            data: Request data and context
            project_id: Associated project ID
            priority: Request priority
            deadline: Required approval deadline
            
        Returns:
            Created approval request
        """
        try:
            request = ApprovalRequest(
                request_id=str(uuid.uuid4()),
                approval_type=approval_type,
                title=title,
                description=description,
                requester_id=requester_id,
                project_id=project_id,
                data=data,
                priority=priority,
                deadline=deadline
            )
            
            self.requests[request.request_id] = request
            
            # Route to appropriate workflow
            await self._route_approval_request(request)
            
            # Check for automated approval
            auto_decision = await self._check_automated_approval(request)
            if auto_decision:
                await self._apply_automated_decision(request, auto_decision)
            else:
                # Start manual approval process
                await self._start_approval_process(request)
            
            logger.info(f"Approval request '{title}' submitted")
            return request
            
        except Exception as e:
            logger.error(f"Failed to submit approval request: {str(e)}")
            raise
    
    async def process_approval_decision(
        self,
        request_id: str,
        approver_id: str,
        decision: str,
        comments: str = "",
        conditions: Optional[List[str]] = None
    ) -> ApprovalDecision:
        """
        Process an approval decision
        
        Args:
            request_id: Request being decided on
            approver_id: ID of the approver
            decision: "approved", "rejected", or "conditional"
            comments: Decision comments
            conditions: Conditions for conditional approval
            
        Returns:
            Recorded approval decision
        """
        try:
            if request_id not in self.requests:
                raise ValueError(f"Approval request {request_id} not found")
            
            request = self.requests[request_id]
            
            # Validate approver permissions
            await self._validate_approver_permissions(request, approver_id)
            
            # Create decision record
            decision_record = ApprovalDecision(
                decision_id=str(uuid.uuid4()),
                request_id=request_id,
                approver_id=approver_id,
                decision=decision,
                comments=comments,
                conditions=conditions or []
            )
            
            self.decisions[decision_record.decision_id] = decision_record
            
            # Update request status
            await self._update_request_status(request, decision_record)
            
            # Check if approval process is complete
            await self._check_approval_completion(request)
            
            logger.info(f"Approval decision '{decision}' processed for request {request_id}")
            return decision_record
            
        except Exception as e:
            logger.error(f"Failed to process approval decision: {str(e)}")
            raise
    
    async def escalate_approval(
        self,
        request_id: str,
        trigger: EscalationTrigger,
        reason: str = ""
    ) -> bool:
        """
        Escalate an approval request
        
        Args:
            request_id: Request to escalate
            trigger: Escalation trigger
            reason: Escalation reason
            
        Returns:
            Success status
        """
        try:
            if request_id not in self.requests:
                raise ValueError(f"Approval request {request_id} not found")
            
            request = self.requests[request_id]
            
            # Find applicable escalation policy
            escalation_policy = await self._find_escalation_policy(request, trigger)
            
            if not escalation_policy:
                logger.warning(f"No escalation policy found for request {request_id}")
                return False
            
            # Execute escalation
            success = await self._execute_escalation(
                request, escalation_policy, trigger, reason
            )
            
            if success:
                request.status = ApprovalStatus.ESCALATED
                logger.info(f"Approval request {request_id} escalated due to {trigger.value}")
            
            return success
            
        except Exception as e:
            logger.error(f"Failed to escalate approval: {str(e)}")
            raise
    
    async def get_approval_analytics(
        self,
        time_period: int = 30,  # days
        approval_type: Optional[ApprovalType] = None
    ) -> Dict[str, Any]:
        """
        Get approval process analytics
        
        Args:
            time_period: Analysis period in days
            approval_type: Filter by approval type
            
        Returns:
            Analytics data
        """
        try:
            cutoff_date = datetime.now() - timedelta(days=time_period)
            
            # Filter requests by time period and type
            filtered_requests = []
            for request in self.requests.values():
                if request.created_at >= cutoff_date:
                    if not approval_type or request.approval_type == approval_type:
                        filtered_requests.append(request)
            
            # Calculate metrics
            analytics = await self._calculate_approval_metrics(filtered_requests)
            
            return analytics
            
        except Exception as e:
            logger.error(f"Failed to get approval analytics: {str(e)}")
            raise
    
    async def _route_approval_request(self, request: ApprovalRequest):
        """Route approval request to appropriate workflow"""
        # Find matching workflow
        matching_workflows = [
            workflow for workflow in self.workflows.values()
            if workflow.approval_type == request.approval_type
        ]
        
        if matching_workflows:
            # Use first matching workflow (could be enhanced with more sophisticated routing)
            workflow = matching_workflows[0]
            request.data['workflow_id'] = workflow.workflow_id
            request.data['current_stage'] = 0
        else:
            # Create default workflow if none exists
            default_workflow = await self._create_default_workflow(request.approval_type)
            request.data['workflow_id'] = default_workflow.workflow_id
            request.data['current_stage'] = 0
    
    async def _check_automated_approval(
        self, 
        request: ApprovalRequest
    ) -> Optional[AutomatedApproval]:
        """Check if request can be automatically approved"""
        workflow_id = request.data.get('workflow_id')
        if not workflow_id or workflow_id not in self.workflows:
            return None
        
        workflow = self.workflows[workflow_id]
        automation_rules = workflow.automation_rules
        
        if not automation_rules:
            return None
        
        # Evaluate automation conditions
        reasoning = []
        confidence = 0.0
        decision = "pending"
        rules_applied = []
        
        # Check value-based auto-approval
        if 'value_threshold' in automation_rules:
            threshold = automation_rules['value_threshold']
            request_value = request.data.get('value', 0)
            
            if request_value <= threshold:
                confidence += 0.3
                decision = "approved"
                reasoning.append(f"Value ${request_value} below auto-approval threshold ${threshold}")
                rules_applied.append('value_threshold')
        
        # Check requester role
        if 'trusted_roles' in automation_rules:
            trusted_roles = automation_rules['trusted_roles']
            requester_role = self.user_roles.get(request.requester_id, "")
            
            if requester_role in trusted_roles:
                confidence += 0.4
                if decision != "approved":
                    decision = "approved"
                reasoning.append(f"Requester has trusted role: {requester_role}")
                rules_applied.append('trusted_roles')
        
        # Check request type patterns
        if 'auto_approve_types' in automation_rules:
            auto_types = automation_rules['auto_approve_types']
            if request.approval_type.value in auto_types:
                confidence += 0.3
                if decision != "approved":
                    decision = "approved"
                reasoning.append(f"Request type {request.approval_type.value} is auto-approved")
                rules_applied.append('auto_approve_types')
        
        # Only auto-approve if confidence is high enough
        if confidence >= self.auto_approval_threshold and decision == "approved":
            return AutomatedApproval(
                approval_id=str(uuid.uuid4()),
                request_id=request.request_id,
                decision=decision,
                reasoning=reasoning,
                confidence=confidence,
                rules_applied=rules_applied
            )
        
        return None
    
    async def _apply_automated_decision(
        self, 
        request: ApprovalRequest, 
        auto_decision: AutomatedApproval
    ):
        """Apply automated approval decision"""
        if auto_decision.decision == "approved":
            request.status = ApprovalStatus.APPROVED
        else:
            request.status = ApprovalStatus.REJECTED
        
        # Record the automated decision
        self.decisions[auto_decision.approval_id] = auto_decision
        
        # Update analytics
        self.approval_metrics[request.approval_type.value]['automated_approvals'] = (
            self.approval_metrics[request.approval_type.value].get('automated_approvals', 0) + 1
        )
    
    async def _start_approval_process(self, request: ApprovalRequest):
        """Start manual approval process"""
        request.status = ApprovalStatus.IN_REVIEW
        
        # Get workflow and current stage
        workflow_id = request.data.get('workflow_id')
        if workflow_id in self.workflows:
            workflow = self.workflows[workflow_id]
            current_stage = request.data.get('current_stage', 0)
            
            if current_stage < len(workflow.stages):
                stage = workflow.stages[current_stage]
                
                # Notify required approvers
                await self._notify_approvers(request, stage.get('approvers', []))
                
                # Set timeout if specified
                timeout_hours = stage.get('timeout_hours', self.default_timeout_hours)
                if timeout_hours > 0:
                    timeout_time = datetime.now() + timedelta(hours=timeout_hours)
                    request.data['timeout'] = timeout_time.isoformat()
    
    async def _validate_approver_permissions(
        self, 
        request: ApprovalRequest, 
        approver_id: str
    ):
        """Validate that approver has permission to approve this request"""
        # Get workflow and stage information
        workflow_id = request.data.get('workflow_id')
        if workflow_id not in self.workflows:
            raise ValueError("No workflow found for request")
        
        workflow = self.workflows[workflow_id]
        current_stage = request.data.get('current_stage', 0)
        
        if current_stage >= len(workflow.stages):
            raise ValueError("Invalid workflow stage")
        
        stage = workflow.stages[current_stage]
        required_approvers = stage.get('approvers', [])
        
        # Check if approver is in the required list or has appropriate role
        if approver_id not in required_approvers:
            approver_role = self.user_roles.get(approver_id, "")
            permitted_roles = self.approval_permissions.get(
                request.approval_type.value, []
            )
            
            if approver_role not in permitted_roles:
                raise ValueError(f"Approver {approver_id} not authorized for this request")
    
    async def _update_request_status(
        self, 
        request: ApprovalRequest, 
        decision: ApprovalDecision
    ):
        """Update request status based on decision"""
        if decision.decision == "approved":
            # Check if more approvals are needed
            workflow_id = request.data.get('workflow_id')
            current_stage = request.data.get('current_stage', 0)
            
            if workflow_id in self.workflows:
                workflow = self.workflows[workflow_id]
                
                if current_stage < len(workflow.stages):
                    stage = workflow.stages[current_stage]
                    
                    # Count current approvals for this stage
                    stage_approvals = sum(
                        1 for d in self.decisions.values()
                        if (d.request_id == request.request_id and 
                            d.decision == "approved" and
                            d.timestamp >= datetime.now() - timedelta(hours=24))
                    )
                    
                    min_approvals = stage.get('min_approvals', 1)
                    
                    if stage_approvals >= min_approvals:
                        # Move to next stage or complete
                        if current_stage + 1 < len(workflow.stages):
                            request.data['current_stage'] = current_stage + 1
                            await self._start_approval_process(request)
                        else:
                            request.status = ApprovalStatus.APPROVED
                    
        elif decision.decision == "rejected":
            # Check rejection limits
            workflow_id = request.data.get('workflow_id')
            current_stage = request.data.get('current_stage', 0)
            
            if workflow_id in self.workflows:
                workflow = self.workflows[workflow_id]
                
                if current_stage < len(workflow.stages):
                    stage = workflow.stages[current_stage]
                    
                    # Count rejections for this stage
                    stage_rejections = sum(
                        1 for d in self.decisions.values()
                        if (d.request_id == request.request_id and 
                            d.decision == "rejected" and
                            d.timestamp >= datetime.now() - timedelta(hours=24))
                    )
                    
                    max_rejections = stage.get('max_rejections', 1)
                    
                    if stage_rejections >= max_rejections:
                        request.status = ApprovalStatus.REJECTED
                    
        elif decision.decision == "conditional":
            request.status = ApprovalStatus.CONDITIONAL
            request.data['conditions'] = decision.conditions
    
    async def _check_approval_completion(self, request: ApprovalRequest):
        """Check if approval process is complete"""
        if request.status in [ApprovalStatus.APPROVED, ApprovalStatus.REJECTED]:
            # Record completion metrics
            completion_time = datetime.now() - request.created_at
            
            self.performance_stats[request.approval_type.value].append({
                'completion_time_hours': completion_time.total_seconds() / 3600,
                'status': request.status.value,
                'priority': request.priority.value,
                'timestamp': datetime.now()
            })
    
    async def _find_escalation_policy(
        self, 
        request: ApprovalRequest, 
        trigger: EscalationTrigger
    ) -> Optional[EscalationPolicy]:
        """Find applicable escalation policy"""
        workflow_id = request.data.get('workflow_id')
        if workflow_id not in self.workflows:
            return None
        
        workflow = self.workflows[workflow_id]
        
        for policy in workflow.escalation_policies:
            if trigger in policy.triggers:
                # Check if policy conditions are met
                if await self._evaluate_escalation_conditions(request, policy):
                    return policy
        
        return None
    
    async def _evaluate_escalation_conditions(
        self, 
        request: ApprovalRequest, 
        policy: EscalationPolicy
    ) -> bool:
        """Evaluate escalation policy conditions"""
        conditions = policy.conditions
        
        # Check value threshold
        if 'min_value' in conditions:
            request_value = request.data.get('value', 0)
            if request_value < conditions['min_value']:
                return False
        
        # Check priority level
        if 'min_priority' in conditions:
            if request.priority.value < conditions['min_priority']:
                return False
        
        # Check approval type
        if 'approval_types' in conditions:
            if request.approval_type.value not in conditions['approval_types']:
                return False
        
        return True
    
    async def _execute_escalation(
        self,
        request: ApprovalRequest,
        policy: EscalationPolicy,
        trigger: EscalationTrigger,
        reason: str
    ) -> bool:
        """Execute escalation according to policy"""
        try:
            escalation_chain = policy.escalation_chain
            
            if not escalation_chain:
                return False
            
            # Find current escalation level
            current_level = request.data.get('escalation_level', 0)
            
            if current_level >= len(escalation_chain):
                logger.warning(f"Maximum escalation level reached for request {request.request_id}")
                return False
            
            # Escalate to next level
            next_approver = escalation_chain[current_level]
            request.data['escalation_level'] = current_level + 1
            request.data['escalated_to'] = next_approver
            request.data['escalation_reason'] = reason
            request.data['escalation_trigger'] = trigger.value
            
            # Notify escalated approver
            await self._notify_escalation(request, next_approver, policy)
            
            return True
            
        except Exception as e:
            logger.error(f"Escalation execution failed: {str(e)}")
            return False
    
    async def _notify_approvers(self, request: ApprovalRequest, approvers: List[str]):
        """Notify approvers of pending request"""
        # This would integrate with notification system
        logger.info(f"Notifying approvers {approvers} for request {request.request_id}")
        
        # Store notification data
        request.data['notified_approvers'] = approvers
        request.data['notification_sent'] = datetime.now().isoformat()
    
    async def _notify_escalation(
        self, 
        request: ApprovalRequest, 
        approver_id: str, 
        policy: EscalationPolicy
    ):
        """Notify approver of escalated request"""
        logger.info(f"Notifying escalated approver {approver_id} for request {request.request_id}")
        
        # Store escalation notification data
        request.data['escalation_notification'] = {
            'approver_id': approver_id,
            'policy_id': policy.policy_id,
            'timestamp': datetime.now().isoformat()
        }
    
    async def _create_default_workflow(
        self, 
        approval_type: ApprovalType
    ) -> ApprovalWorkflow:
        """Create default workflow for approval type"""
        # Define default stages based on approval type
        if approval_type == ApprovalType.BUDGET_APPROVAL:
            stages = [
                {
                    'name': 'Manager Review',
                    'approvers': ['manager'],
                    'min_approvals': 1,
                    'timeout_hours': 24
                },
                {
                    'name': 'Finance Approval', 
                    'approvers': ['finance_director'],
                    'min_approvals': 1,
                    'timeout_hours': 48
                }
            ]
        elif approval_type == ApprovalType.QUALITY_GATE:
            stages = [
                {
                    'name': 'Quality Review',
                    'approvers': ['quality_lead'],
                    'min_approvals': 1,
                    'timeout_hours': 12
                }
            ]
        else:
            # Generic single-stage approval
            stages = [
                {
                    'name': 'Standard Review',
                    'approvers': ['project_manager'],
                    'min_approvals': 1,
                    'timeout_hours': 24
                }
            ]
        
        return await self.create_approval_workflow(
            name=f"Default {approval_type.value}",
            approval_type=approval_type,
            stages=stages
        )
    
    async def _create_default_escalation_policies(
        self, 
        approval_type: ApprovalType
    ) -> List[EscalationPolicy]:
        """Create default escalation policies"""
        policies = []
        
        # Timeout escalation
        timeout_policy = EscalationPolicy(
            policy_id=str(uuid.uuid4()),
            name="Timeout Escalation",
            triggers=[EscalationTrigger.TIMEOUT],
            escalation_chain=['senior_manager', 'director', 'executive'],
            timeout_hours=self.default_timeout_hours
        )
        policies.append(timeout_policy)
        self.escalation_policies[timeout_policy.policy_id] = timeout_policy
        
        # High-value escalation
        if approval_type == ApprovalType.BUDGET_APPROVAL:
            value_policy = EscalationPolicy(
                policy_id=str(uuid.uuid4()),
                name="High Value Escalation",
                triggers=[EscalationTrigger.VALUE_THRESHOLD],
                escalation_chain=['finance_director', 'cfo'],
                conditions={'min_value': 10000}
            )
            policies.append(value_policy)
            self.escalation_policies[value_policy.policy_id] = value_policy
        
        return policies
    
    async def _calculate_approval_metrics(
        self, 
        requests: List[ApprovalRequest]
    ) -> Dict[str, Any]:
        """Calculate approval process metrics"""
        if not requests:
            return {}
        
        # Basic metrics
        total_requests = len(requests)
        approved_count = sum(1 for r in requests if r.status == ApprovalStatus.APPROVED)
        rejected_count = sum(1 for r in requests if r.status == ApprovalStatus.REJECTED)
        pending_count = sum(1 for r in requests if r.status == ApprovalStatus.PENDING)
        
        # Completion times
        completed_requests = [
            r for r in requests 
            if r.status in [ApprovalStatus.APPROVED, ApprovalStatus.REJECTED]
        ]
        
        completion_times = []
        for request in completed_requests:
            # Find latest decision for this request
            request_decisions = [
                d for d in self.decisions.values()
                if d.request_id == request.request_id
            ]
            
            if request_decisions:
                latest_decision = max(request_decisions, key=lambda d: d.timestamp)
                completion_time = (latest_decision.timestamp - request.created_at).total_seconds() / 3600
                completion_times.append(completion_time)
        
        # Calculate statistics
        avg_completion_time = np.mean(completion_times) if completion_times else 0
        median_completion_time = np.median(completion_times) if completion_times else 0
        
        # Approval rate by priority
        priority_stats = {}
        for priority in ApprovalPriority:
            priority_requests = [r for r in requests if r.priority == priority]
            if priority_requests:
                priority_approved = sum(
                    1 for r in priority_requests if r.status == ApprovalStatus.APPROVED
                )
                priority_stats[priority.name] = {
                    'total': len(priority_requests),
                    'approved': priority_approved,
                    'approval_rate': priority_approved / len(priority_requests)
                }
        
        # Escalation metrics
        escalated_count = sum(1 for r in requests if r.status == ApprovalStatus.ESCALATED)
        
        return {
            'total_requests': total_requests,
            'approved_count': approved_count,
            'rejected_count': rejected_count,
            'pending_count': pending_count,
            'escalated_count': escalated_count,
            'approval_rate': approved_count / total_requests if total_requests > 0 else 0,
            'rejection_rate': rejected_count / total_requests if total_requests > 0 else 0,
            'avg_completion_time_hours': avg_completion_time,
            'median_completion_time_hours': median_completion_time,
            'priority_statistics': priority_stats,
            'automated_approvals': sum(
                1 for d in self.decisions.values()
                if isinstance(d, AutomatedApproval) and 
                d.request_id in [r.request_id for r in requests]
            )
        }
    
    async def get_pending_approvals(self, approver_id: str) -> List[ApprovalRequest]:
        """Get pending approval requests for an approver"""
        pending_requests = []
        
        for request in self.requests.values():
            if request.status in [ApprovalStatus.PENDING, ApprovalStatus.IN_REVIEW]:
                # Check if this approver is required for current stage
                workflow_id = request.data.get('workflow_id')
                if workflow_id in self.workflows:
                    workflow = self.workflows[workflow_id]
                    current_stage = request.data.get('current_stage', 0)
                    
                    if current_stage < len(workflow.stages):
                        stage = workflow.stages[current_stage]
                        if approver_id in stage.get('approvers', []):
                            pending_requests.append(request)
        
        return pending_requests
    
    async def get_request_history(self, request_id: str) -> Dict[str, Any]:
        """Get complete history of an approval request"""
        if request_id not in self.requests:
            raise ValueError(f"Request {request_id} not found")
        
        request = self.requests[request_id]
        
        # Get all decisions for this request
        request_decisions = [
            d for d in self.decisions.values()
            if d.request_id == request_id
        ]
        
        # Sort by timestamp
        request_decisions.sort(key=lambda d: d.timestamp)
        
        history = {
            'request': {
                'id': request.request_id,
                'type': request.approval_type.value,
                'title': request.title,
                'status': request.status.value,
                'priority': request.priority.value,
                'created_at': request.created_at.isoformat(),
                'requester_id': request.requester_id
            },
            'decisions': [
                {
                    'decision_id': d.decision_id,
                    'approver_id': d.approver_id,
                    'decision': d.decision,
                    'comments': d.comments,
                    'timestamp': d.timestamp.isoformat(),
                    'conditions': getattr(d, 'conditions', [])
                }
                for d in request_decisions
            ],
            'escalations': request.data.get('escalation_level', 0),
            'current_stage': request.data.get('current_stage', 0)
        }
        
        return history


# Export main classes
__all__ = [
    'ApprovalEngine',
    'ApprovalWorkflow',
    'ApprovalRule',
    'ApprovalRequest',
    'ApprovalDecision',
    'AutomatedApproval',
    'EscalationPolicy',
    'ApprovalType',
    'ApprovalStatus',
    'ApprovalPriority',
    'EscalationTrigger'
]