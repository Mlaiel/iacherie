"""
Ainflue Platform - Multimedia Collaboration - Approval Pipeline System
Professional multi-stage approval pipeline for content publication workflow

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
Version: 3.1.0 Enterprise
"""

import asyncio
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union, Callable
from enum import Enum
from dataclasses import dataclass, field
import json
import logging
from pathlib import Path

logger = logging.getLogger(__name__)


class ApprovalStage(Enum):
    """Approval stage enumeration"""
    CONTENT_REVIEW = "content_review"
    TECHNICAL_APPROVAL = "technical_approval"
    LEGAL_APPROVAL = "legal_approval"
    CREATIVE_APPROVAL = "creative_approval"
    COMPLIANCE_CHECK = "compliance_check"
    FINAL_APPROVAL = "final_approval"
    PUBLICATION_READY = "publication_ready"


class ApprovalStatus(Enum):
    """Approval status enumeration"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    APPROVED = "approved"
    REJECTED = "rejected"
    CONDITIONAL_APPROVAL = "conditional_approval"
    ESCALATED = "escalated"
    CANCELLED = "cancelled"
    EXPIRED = "expired"


class ApprovalAction(Enum):
    """Approval actions"""
    APPROVE = "approve"
    REJECT = "reject"
    REQUEST_CHANGES = "request_changes"
    ESCALATE = "escalate"
    DEFER = "defer"
    CANCEL = "cancel"


@dataclass
class ApprovalCondition:
    """Approval condition data structure"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    condition: str = ""
    description: str = ""
    required: bool = True
    satisfied: bool = False
    satisfied_by: Optional[str] = None
    satisfied_at: Optional[float] = None
    notes: str = ""


@dataclass
class ApprovalDecision:
    """Approval decision data structure"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    approver_id: str = ""
    action: ApprovalAction = ApprovalAction.APPROVE
    timestamp: Optional[float] = None
    comments: str = ""
    conditions: List[ApprovalCondition] = field(default_factory=list)
    attachments: List[str] = field(default_factory=list)
    confidence_score: Optional[float] = None
    
    def __post_init__(self) -> None:
        if self.timestamp is None:
            self.timestamp = datetime.now().timestamp()


@dataclass
class ApprovalStageConfig:
    """Approval stage configuration"""
    stage: ApprovalStage
    required_approvers: List[str] = field(default_factory=list)
    required_approvals: int = 1
    timeout_hours: Optional[int] = None
    auto_escalate: bool = False
    escalation_rules: Dict[str, Any] = field(default_factory=dict)
    conditions: List[str] = field(default_factory=list)
    parallel_processing: bool = False


@dataclass
class ApprovalRequest:
    """Approval request data structure"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    content_id: str = ""
    submitter_id: str = ""
    pipeline_name: str = ""
    current_stage: Optional[ApprovalStage] = None
    overall_status: ApprovalStatus = ApprovalStatus.PENDING
    created_at: Optional[float] = None
    completed_at: Optional[float] = None
    deadline: Optional[float] = None
    decisions: List[ApprovalDecision] = field(default_factory=list)
    conditions: List[ApprovalCondition] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self) -> None:
        if self.created_at is None:
            self.created_at = datetime.now().timestamp()


class ApprovalPipelineManager:
    """Professional multi-stage approval pipeline system"""
    
    def __init__(self, config -> None: Optional[Dict[str, Any]] = None) -> None:
        """Initialize approval pipeline manager"""
        self.config = config or {}
        self.pipelines: Dict[str, List[ApprovalStageConfig]] = {}
        self.requests: Dict[str, ApprovalRequest] = {}
        self.approvers: Dict[str, Dict[str, Any]] = {}
        self.conditions_handlers: Dict[str, Callable] = {}
        self.notifications_enabled = self.config.get('notifications', True)
        
        # Initialize default pipelines
        self._initialize_default_pipelines()
    
    def _initialize_default_pipelines(self) -> None:
        """Initialize default approval pipelines"""
        # Standard content pipeline
        self.pipelines['standard_content'] = [
            ApprovalStageConfig(
                stage=ApprovalStage.CONTENT_REVIEW,
                required_approvals=1,
                timeout_hours=24,
                auto_escalate=True
            ),
            ApprovalStageConfig(
                stage=ApprovalStage.TECHNICAL_APPROVAL,
                required_approvals=1,
                timeout_hours=12,
                auto_escalate=True
            ),
            ApprovalStageConfig(
                stage=ApprovalStage.FINAL_APPROVAL,
                required_approvals=1,
                timeout_hours=6,
                auto_escalate=True
            )
        ]
        
        # Legal compliance pipeline
        self.pipelines['legal_compliance'] = [
            ApprovalStageConfig(
                stage=ApprovalStage.CONTENT_REVIEW,
                required_approvals=1,
                timeout_hours=24
            ),
            ApprovalStageConfig(
                stage=ApprovalStage.LEGAL_APPROVAL,
                required_approvals=2,
                timeout_hours=48,
                auto_escalate=True
            ),
            ApprovalStageConfig(
                stage=ApprovalStage.COMPLIANCE_CHECK,
                required_approvals=1,
                timeout_hours=24
            ),
            ApprovalStageConfig(
                stage=ApprovalStage.FINAL_APPROVAL,
                required_approvals=1,
                timeout_hours=12
            )
        ]
        
        # Creative content pipeline
        self.pipelines['creative_content'] = [
            ApprovalStageConfig(
                stage=ApprovalStage.CREATIVE_APPROVAL,
                required_approvals=2,
                timeout_hours=48,
                parallel_processing=True
            ),
            ApprovalStageConfig(
                stage=ApprovalStage.CONTENT_REVIEW,
                required_approvals=1,
                timeout_hours=24
            ),
            ApprovalStageConfig(
                stage=ApprovalStage.FINAL_APPROVAL,
                required_approvals=1,
                timeout_hours=12
            )
        ]
        
        # Express pipeline
        self.pipelines['express'] = [
            ApprovalStageConfig(
                stage=ApprovalStage.CONTENT_REVIEW,
                required_approvals=1,
                timeout_hours=6,
                auto_escalate=True
            ),
            ApprovalStageConfig(
                stage=ApprovalStage.FINAL_APPROVAL,
                required_approvals=1,
                timeout_hours=3,
                auto_escalate=True
            )
        ]
    
    async def submit_for_approval(
        self,
        content_id: str,
        submitter_id: str,
        pipeline_name: str = 'standard_content',
        deadline_hours: Optional[int] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> ApprovalRequest:
        """Submit content for approval through specified pipeline"""
        try:
            if pipeline_name not in self.pipelines:
                raise ValueError(f"Unknown pipeline: {pipeline_name}")
            
            deadline = None
            if deadline_hours:
                deadline = (datetime.now() + timedelta(hours=deadline_hours)).timestamp()
            
            request = ApprovalRequest(
                content_id=content_id,
                submitter_id=submitter_id,
                pipeline_name=pipeline_name,
                deadline=deadline,
                metadata=metadata or {}
            )
            
            self.requests[request.id] = request
            
            # Start the first stage
            await self._advance_to_next_stage(request.id)
            
            # Send notification to submitter
            if self.notifications_enabled:
                await self._send_approval_notification(request, 'submitted')
            
            logger.info(f"Submitted approval request {request.id} for content {content_id}")
            return request
            
        except Exception as e:
            logger.error(f"Error submitting for approval: {e}")
            raise
    
    async def make_approval_decision(
        self,
        request_id: str,
        approver_id: str,
        action: ApprovalAction,
        comments: str = "",
        conditions: Optional[List[ApprovalCondition]] = None,
        attachments: Optional[List[str]] = None,
        confidence_score: Optional[float] = None
    ) -> bool:
        """Make an approval decision"""
        try:
            if request_id not in self.requests:
                raise ValueError(f"Approval request {request_id} not found")
            
            request = self.requests[request_id]
            
            if request.overall_status not in [ApprovalStatus.PENDING, ApprovalStatus.IN_PROGRESS]:
                raise ValueError(f"Cannot make decision on request in status {request.overall_status.value}")
            
            # Verify approver is authorized for current stage
            await self._verify_approver_authorization(request, approver_id)
            
            decision = ApprovalDecision(
                approver_id=approver_id,
                action=action,
                comments=comments,
                conditions=conditions or [],
                attachments=attachments or [],
                confidence_score=confidence_score
            )
            
            request.decisions.append(decision)
            
            # Process the decision
            await self._process_approval_decision(request, decision)
            
            logger.info(f"Approval decision made for request {request_id}: {action.value}")
            return True
            
        except Exception as e:
            logger.error(f"Error making approval decision: {e}")
            raise
    
    async def _process_approval_decision(
        self,
        request -> None: ApprovalRequest,
        decision -> None: ApprovalDecision
    ) -> None:
        """Process an approval decision and update request status"""
        try:
            if decision.action == ApprovalAction.REJECT:
                request.overall_status = ApprovalStatus.REJECTED
                request.completed_at = datetime.now().timestamp()
                await self._send_approval_notification(request, 'rejected')
                
            elif decision.action == ApprovalAction.CANCEL:
                request.overall_status = ApprovalStatus.CANCELLED
                request.completed_at = datetime.now().timestamp()
                await self._send_approval_notification(request, 'cancelled')
                
            elif decision.action == ApprovalAction.REQUEST_CHANGES:
                request.overall_status = ApprovalStatus.CONDITIONAL_APPROVAL
                if decision.conditions:
                    request.conditions.extend(decision.conditions)
                await self._send_approval_notification(request, 'changes_requested')
                
            elif decision.action == ApprovalAction.ESCALATE:
                request.overall_status = ApprovalStatus.ESCALATED
                await self._handle_escalation(request, decision)
                
            elif decision.action == ApprovalAction.APPROVE:
                # Check if stage is complete
                if await self._is_stage_approved(request):
                    await self._advance_to_next_stage(request.id)
                
            elif decision.action == ApprovalAction.DEFER:
                # Update deadline if specified
                if decision.comments and 'defer_hours' in decision.comments:
                    defer_hours = int(decision.comments.split('defer_hours:')[1].split(',')[0])
                    new_deadline = (datetime.now() + timedelta(hours=defer_hours)).timestamp()
                    request.deadline = new_deadline
                
        except Exception as e:
            logger.error(f"Error processing approval decision: {e}")
            raise
    
    async def _is_stage_approved(self, request: ApprovalRequest) -> bool:
        """Check if current stage has enough approvals"""
        try:
            if not request.current_stage:
                return False
            
            pipeline = self.pipelines.get(request.pipeline_name, [])
            current_stage_config = None
            
            for stage_config in pipeline:
                if stage_config.stage == request.current_stage:
                    current_stage_config = stage_config
                    break
            
            if not current_stage_config:
                return False
            
            # Count approvals for current stage
            approvals_count = 0
            for decision in request.decisions:
                if decision.action == ApprovalAction.APPROVE:
                    approvals_count += 1
            
            return approvals_count >= current_stage_config.required_approvals
            
        except Exception as e:
            logger.error(f"Error checking stage approval: {e}")
            return False
    
    async def _advance_to_next_stage(self, request_id -> None: str) -> None:
        """Advance request to next approval stage"""
        try:
            request = self.requests[request_id]
            pipeline = self.pipelines.get(request.pipeline_name, [])
            
            if not request.current_stage:
                # Starting first stage
                if pipeline:
                    request.current_stage = pipeline[0].stage
                    request.overall_status = ApprovalStatus.IN_PROGRESS
                    await self._send_approval_notification(request, 'stage_started')
                return
            
            # Find current stage index
            current_index = -1
            for i, stage_config in enumerate(pipeline):
                if stage_config.stage == request.current_stage:
                    current_index = i
                    break
            
            if current_index == -1:
                raise ValueError(f"Current stage {request.current_stage} not found in pipeline")
            
            # Check if this was the last stage
            if current_index == len(pipeline) - 1:
                request.overall_status = ApprovalStatus.APPROVED
                request.completed_at = datetime.now().timestamp()
                await self._send_approval_notification(request, 'approved')
                logger.info(f"Approval request {request_id} completed successfully")
                return
            
            # Advance to next stage
            next_stage_config = pipeline[current_index + 1]
            request.current_stage = next_stage_config.stage
            
            await self._send_approval_notification(request, 'stage_started')
            logger.info(f"Advanced request {request_id} to stage {request.current_stage.value}")
            
        except Exception as e:
            logger.error(f"Error advancing to next stage: {e}")
            raise
    
    async def _verify_approver_authorization(
        self,
        request: ApprovalRequest,
        approver_id: str
    ) -> bool:
        """Verify approver is authorized for current stage"""
        try:
            if not request.current_stage:
                return False
            
            pipeline = self.pipelines.get(request.pipeline_name, [])
            current_stage_config = None
            
            for stage_config in pipeline:
                if stage_config.stage == request.current_stage:
                    current_stage_config = stage_config
                    break
            
            if not current_stage_config:
                return False
            
            # If no specific approvers required, allow any approver
            if not current_stage_config.required_approvers:
                return True
            
            # Check if approver is in required list
            return approver_id in current_stage_config.required_approvers
            
        except Exception as e:
            logger.error(f"Error verifying approver authorization: {e}")
            return False
    
    async def _handle_escalation(
        self,
        request -> None: ApprovalRequest,
        decision -> None: ApprovalDecision
    ) -> None:
        """Handle approval escalation"""
        try:
            # Add escalation metadata
            request.metadata['escalation'] = {
                'escalated_by': decision.approver_id,
                'escalated_at': decision.timestamp,
                'reason': decision.comments,
                'original_stage': request.current_stage.value if request.current_stage else None
            }
            
            # Send escalation notification
            await self._send_approval_notification(request, 'escalated')
            
            logger.info(f"Approval request {request.id} escalated by {decision.approver_id}")
            
        except Exception as e:
            logger.error(f"Error handling escalation: {e}")
            raise
    
    async def satisfy_condition(
        self,
        request_id: str,
        condition_id: str,
        satisfied_by: str,
        notes: str = ""
    ) -> bool:
        """Mark an approval condition as satisfied"""
        try:
            if request_id not in self.requests:
                raise ValueError(f"Approval request {request_id} not found")
            
            request = self.requests[request_id]
            
            for condition in request.conditions:
                if condition.id == condition_id:
                    condition.satisfied = True
                    condition.satisfied_by = satisfied_by
                    condition.satisfied_at = datetime.now().timestamp()
                    condition.notes = notes
                    
                    # Check if all conditions are satisfied
                    all_satisfied = all(
                        not cond.required or cond.satisfied 
                        for cond in request.conditions
                    )
                    
                    if all_satisfied and request.overall_status == ApprovalStatus.CONDITIONAL_APPROVAL:
                        # Resume approval process
                        request.overall_status = ApprovalStatus.IN_PROGRESS
                        await self._send_approval_notification(request, 'conditions_satisfied')
                    
                    logger.info(f"Condition {condition_id} satisfied for request {request_id}")
                    return True
            
            raise ValueError(f"Condition {condition_id} not found")
            
        except Exception as e:
            logger.error(f"Error satisfying condition: {e}")
            raise
    
    async def get_pending_approvals(
        self,
        approver_id: str
    ) -> List[ApprovalRequest]:
        """Get pending approval requests for an approver"""
        try:
            pending_requests = []
            
            for request in self.requests.values():
                if request.overall_status in [ApprovalStatus.PENDING, ApprovalStatus.IN_PROGRESS]:
                    if await self._verify_approver_authorization(request, approver_id):
                        pending_requests.append(request)
            
            return sorted(pending_requests, key=lambda x: x.created_at or 0)
            
        except Exception as e:
            logger.error(f"Error getting pending approvals: {e}")
            raise
    
    async def get_overdue_approvals(self) -> List[ApprovalRequest]:
        """Get overdue approval requests"""
        try:
            current_time = datetime.now().timestamp()
            overdue_requests = []
            
            for request in self.requests.values():
                if (request.deadline and 
                    request.deadline < current_time and 
                    request.overall_status in [ApprovalStatus.PENDING, ApprovalStatus.IN_PROGRESS]):
                    overdue_requests.append(request)
            
            return sorted(overdue_requests, key=lambda x: x.deadline or 0)
            
        except Exception as e:
            logger.error(f"Error getting overdue approvals: {e}")
            raise
    
    async def cancel_approval_request(
        self,
        request_id: str,
        cancelled_by: str,
        reason: str = ""
    ) -> bool:
        """Cancel an approval request"""
        try:
            if request_id not in self.requests:
                raise ValueError(f"Approval request {request_id} not found")
            
            request = self.requests[request_id]
            
            if request.overall_status in [ApprovalStatus.APPROVED, ApprovalStatus.REJECTED, ApprovalStatus.CANCELLED]:
                raise ValueError(f"Cannot cancel request in status {request.overall_status.value}")
            
            request.overall_status = ApprovalStatus.CANCELLED
            request.completed_at = datetime.now().timestamp()
            request.metadata['cancellation'] = {
                'cancelled_by': cancelled_by,
                'cancelled_at': datetime.now().timestamp(),
                'reason': reason
            }
            
            await self._send_approval_notification(request, 'cancelled')
            
            logger.info(f"Approval request {request_id} cancelled by {cancelled_by}")
            return True
            
        except Exception as e:
            logger.error(f"Error cancelling approval request: {e}")
            raise
    
    async def _send_approval_notification(
        self,
        request -> None: ApprovalRequest,
        notification_type -> None: str
    ) -> None:
        """Send approval-related notifications"""
        try:
            notification_data = {
                'type': notification_type,
                'request_id': request.id,
                'content_id': request.content_id,
                'submitter_id': request.submitter_id,
                'current_stage': request.current_stage.value if request.current_stage else None,
                'status': request.overall_status.value,
                'timestamp': datetime.now().timestamp()
            }
            
            logger.info(f"Sending {notification_type} notification for approval request {request.id}")
            # TODO: Implement actual notification sending
            
        except Exception as e:
            logger.error(f"Error sending approval notification: {e}")
    
    async def get_approval_statistics(
        self,
        approver_id: Optional[str] = None,
        time_range_days: int = 30
    ) -> Dict[str, Any]:
        """Get approval statistics"""
        try:
            cutoff_time = (datetime.now() - timedelta(days=time_range_days)).timestamp()
            
            relevant_requests = [
                request for request in self.requests.values()
                if (request.created_at or 0) >= cutoff_time
            ]
            
            if approver_id:
                # Filter by approver participation
                relevant_requests = [
                    request for request in relevant_requests
                    if any(decision.approver_id == approver_id for decision in request.decisions)
                ]
            
            stats = {
                'total_requests': len(relevant_requests),
                'by_status': {},
                'by_pipeline': {},
                'average_processing_time': 0,
                'approval_rate': 0,
                'overdue_count': 0,
                'escalation_count': 0
            }
            
            processing_times = []
            approved_count = 0
            escalated_count = 0
            
            for request in relevant_requests:
                # Count by status
                status = request.overall_status.value
                stats['by_status'][status] = stats['by_status'].get(status, 0) + 1
                
                # Count by pipeline
                pipeline = request.pipeline_name
                stats['by_pipeline'][pipeline] = stats['by_pipeline'].get(pipeline, 0) + 1
                
                # Calculate processing time
                if request.completed_at and request.created_at:
                    processing_time = request.completed_at - request.created_at
                    processing_times.append(processing_time)
                
                # Count approvals
                if request.overall_status == ApprovalStatus.APPROVED:
                    approved_count += 1
                
                # Count escalations
                if request.overall_status == ApprovalStatus.ESCALATED or 'escalation' in request.metadata:
                    escalated_count += 1
                
                # Count overdue
                if (request.deadline and 
                    request.deadline < datetime.now().timestamp() and 
                    request.overall_status in [ApprovalStatus.PENDING, ApprovalStatus.IN_PROGRESS]):
                    stats['overdue_count'] += 1
            
            if processing_times:
                stats['average_processing_time'] = sum(processing_times) / len(processing_times)
            
            if relevant_requests:
                stats['approval_rate'] = approved_count / len(relevant_requests) * 100
            
            stats['escalation_count'] = escalated_count
            
            return stats
            
        except Exception as e:
            logger.error(f"Error getting approval statistics: {e}")
            raise


# Export main classes
__all__ = [
    'ApprovalPipelineManager',
    'ApprovalRequest',
    'ApprovalDecision',
    'ApprovalCondition',
    'ApprovalStageConfig',
    'ApprovalStage',
    'ApprovalStatus',
    'ApprovalAction'
]