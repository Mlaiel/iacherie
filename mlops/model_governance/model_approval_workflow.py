"""
✅ Model Approval Workflow - Enterprise DevOps & Business
© 2025 Fahed Mlaiel <mlaiel@live.de> - Tous droits réservés

⚠️ AVERTISSEMENT LÉGAL:
==========================================
TOUS DROITS RÉSERVÉS - Code propriétaire de Fahed Mlaiel
- Utilisation commerciale INTERDITE sans autorisation écrite
- Reverse engineering STRICTEMENT INTERDIT
- Distribution INTERDITE sans licence explicite
- Violation = Poursuites judiciaires automatiques

🏢 USAGE ENTREPRISE: Licence entreprise disponible sur demande
📧 Contact: mlaiel@live.de

Workflow approbation modèles enterprise avec Creator Economy
Expertise: DevOps + Backend Senior + ML Engineer + Business Analyst
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Union, Callable, Set
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import json
import uuid
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)


class ApprovalStatus(Enum):
    """Approval status states"""
    PENDING = "pending"
    IN_REVIEW = "in_review"
    APPROVED = "approved"
    REJECTED = "rejected"
    CONDITIONAL_APPROVAL = "conditional_approval"
    ESCALATED = "escalated"
    EXPIRED = "expired"
    CANCELLED = "cancelled"


class ApprovalStageType(Enum):
    """Types of approval stages"""
    TECHNICAL_REVIEW = "technical_review"
    SECURITY_REVIEW = "security_review"
    BUSINESS_REVIEW = "business_review"
    CREATOR_APPROVAL = "creator_approval"
    STAKEHOLDER_REVIEW = "stakeholder_review"
    COMPLIANCE_REVIEW = "compliance_review"
    EXECUTIVE_APPROVAL = "executive_approval"
    AUTOMATED_VALIDATION = "automated_validation"


class Priority(Enum):
    """Approval priority levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"
    EMERGENCY = "emergency"


class NotificationType(Enum):
    """Types of notifications"""
    EMAIL = "email"
    DASHBOARD = "dashboard"
    WEBHOOK = "webhook"
    SMS = "sms"
    SLACK = "slack"


@dataclass
class ApprovalCriteria:
    """Criteria for approval decision"""
    stage_type: ApprovalStageType
    required_approvers: List[str]
    minimum_approvals: int
    maximum_rejections: int = 0
    timeout_hours: int = 72
    auto_approve_conditions: Dict[str, Any] = field(default_factory=dict)
    escalation_rules: Dict[str, Any] = field(default_factory=dict)
    creator_tier_specific: bool = False
    business_impact_threshold: float = 0.5
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert criteria to dictionary"""
        return {
            "stage_type": self.stage_type.value,
            "required_approvers": self.required_approvers,
            "minimum_approvals": self.minimum_approvals,
            "maximum_rejections": self.maximum_rejections,
            "timeout_hours": self.timeout_hours,
            "auto_approve_conditions": self.auto_approve_conditions,
            "escalation_rules": self.escalation_rules,
            "creator_tier_specific": self.creator_tier_specific,
            "business_impact_threshold": self.business_impact_threshold
        }


@dataclass
class ApprovalDecision:
    """Individual approval decision"""
    decision_id: str
    approver_id: str
    approver_role: str
    decision: ApprovalStatus
    comments: str
    decided_at: datetime
    confidence_score: float = 1.0
    conditions: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert decision to dictionary"""
        return {
            "decision_id": self.decision_id,
            "approver_id": self.approver_id,
            "approver_role": self.approver_role,
            "decision": self.decision.value,
            "comments": self.comments,
            "decided_at": self.decided_at.isoformat(),
            "confidence_score": self.confidence_score,
            "conditions": self.conditions,
            "metadata": self.metadata
        }


@dataclass
class ApprovalStage:
    """Single stage in approval workflow"""
    stage_id: str
    stage_type: ApprovalStageType
    criteria: ApprovalCriteria
    status: ApprovalStatus = ApprovalStatus.PENDING
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    decisions: List[ApprovalDecision] = field(default_factory=list)
    notifications_sent: List[str] = field(default_factory=list)
    escalated: bool = False
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert stage to dictionary"""
        return {
            "stage_id": self.stage_id,
            "stage_type": self.stage_type.value,
            "criteria": self.criteria.to_dict(),
            "status": self.status.value,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "decisions": [d.to_dict() for d in self.decisions],
            "notifications_sent": self.notifications_sent,
            "escalated": self.escalated
        }


@dataclass
class ApprovalRequest:
    """Complete approval request"""
    request_id: str
    model_name: str
    model_version: str
    requested_by: str
    requested_at: datetime
    priority: Priority
    description: str
    target_environment: str  # staging, production, etc.
    model_metadata: Dict[str, Any]
    creator_context: Optional[Dict[str, Any]] = None
    business_justification: str = ""
    stages: List[ApprovalStage] = field(default_factory=list)
    current_stage_index: int = 0
    overall_status: ApprovalStatus = ApprovalStatus.PENDING
    approved_at: Optional[datetime] = None
    approved_by: Optional[str] = None
    rejection_reason: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert request to dictionary"""
        return {
            "request_id": self.request_id,
            "model_name": self.model_name,
            "model_version": self.model_version,
            "requested_by": self.requested_by,
            "requested_at": self.requested_at.isoformat(),
            "priority": self.priority.value,
            "description": self.description,
            "target_environment": self.target_environment,
            "model_metadata": self.model_metadata,
            "creator_context": self.creator_context,
            "business_justification": self.business_justification,
            "stages": [s.to_dict() for s in self.stages],
            "current_stage_index": self.current_stage_index,
            "overall_status": self.overall_status.value,
            "approved_at": self.approved_at.isoformat() if self.approved_at else None,
            "approved_by": self.approved_by,
            "rejection_reason": self.rejection_reason
        }


class ApprovalNotificationHandler(ABC):
    """Abstract notification handler"""
    
    @abstractmethod
    async def send_notification(
        self,
        notification_type: NotificationType,
        recipient: str,
        subject: str,
        message: str,
        metadata: Dict[str, Any]
    ) -> bool:
        """Send notification"""
        pass


class DefaultNotificationHandler(ApprovalNotificationHandler):
    """Default notification handler implementation"""
    
    async def send_notification(
        self,
        notification_type: NotificationType,
        recipient: str,
        subject: str,
        message: str,
        metadata: Dict[str, Any]
    ) -> bool:
        """Send notification (mock implementation)"""
        try:
            logger.info(f"📧 Sending {notification_type.value} to {recipient}: {subject}")
            # In real implementation, would integrate with email/Slack/etc APIs
            return True
        except Exception as e:
            logger.error(f"❌ Notification failed: {str(e)}")
            return False


class ModelApprovalWorkflow:
    """
    ✅ Workflow approbation modèles enterprise
    
    Enterprise approval workflow with:
    - Multi-stage approval process with parallel/sequential stages
    - Business impact assessment et risk-based routing
    - Creator community feedback integration
    - Stakeholder notification automation avec escalation
    - Automated validation hooks avec quality gates
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize approval workflow engine
        
        Args:
            config: Workflow configuration
        """
        self.config = config or self._get_default_config()
        self.workflow_id = str(uuid.uuid4())
        
        # Workflow state
        self._approval_requests: Dict[str, ApprovalRequest] = {}
        self._workflow_templates: Dict[str, List[ApprovalCriteria]] = {}
        self._approver_registry: Dict[str, Dict[str, Any]] = {}
        
        # Notification system
        self._notification_handler: ApprovalNotificationHandler = DefaultNotificationHandler()
        self._notification_templates: Dict[str, str] = {}
        
        # Automated validators
        self._automated_validators: Dict[ApprovalStageType, Callable] = {}
        
        # Business rules
        self._business_rules: Dict[str, Callable] = {}
        
        # Performance metrics
        self._workflow_metrics = {
            "requests_submitted": 0,
            "requests_approved": 0,
            "requests_rejected": 0,
            "avg_approval_time_hours": 0.0,
            "escalations_triggered": 0,
            "auto_approvals": 0
        }
        
        # Initialize default workflow templates
        self._initialize_workflow_templates()
        
        # Initialize automated validators
        self._initialize_automated_validators()
        
        # Initialize notification templates
        self._initialize_notification_templates()
        
        logger.info(f"✅ ModelApprovalWorkflow initialized with ID: {self.workflow_id}")
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Get default workflow configuration"""
        return {
            "workflows": {
                "default_timeout_hours": 72,
                "auto_escalation": True,
                "parallel_stages": True,
                "approval_thresholds": {
                    "low_risk": 1,
                    "medium_risk": 2,
                    "high_risk": 3
                }
            },
            "creator_economy": {
                "creator_approval_required": True,
                "tier_based_workflows": True,
                "community_feedback": True,
                "revenue_impact_assessment": True
            },
            "business_rules": {
                "risk_based_routing": True,
                "impact_assessment": True,
                "compliance_validation": True,
                "performance_gating": True
            },
            "notifications": {
                "enabled": True,
                "channels": ["email", "dashboard", "webhook"],
                "reminder_intervals": [24, 48, 72],  # hours
                "escalation_delay": 96  # hours
            },
            "automation": {
                "auto_approve_low_risk": True,
                "parallel_validation": True,
                "smart_routing": True,
                "ml_assisted_decisions": False
            }
        }
    
    def _initialize_workflow_templates(self) -> None:
        """Initialize predefined workflow templates"""
        
        # Production deployment workflow
        production_workflow = [
            ApprovalCriteria(
                stage_type=ApprovalStageType.AUTOMATED_VALIDATION,
                required_approvers=["system"],
                minimum_approvals=1,
                timeout_hours=2,
                auto_approve_conditions={
                    "quality_gates_passed": True,
                    "security_scan_clean": True,
                    "performance_benchmarks_met": True
                }
            ),
            ApprovalCriteria(
                stage_type=ApprovalStageType.TECHNICAL_REVIEW,
                required_approvers=["ml_engineer", "platform_engineer"],
                minimum_approvals=2,
                timeout_hours=48,
                escalation_rules={"escalate_after_hours": 72}
            ),
            ApprovalCriteria(
                stage_type=ApprovalStageType.SECURITY_REVIEW,
                required_approvers=["security_engineer"],
                minimum_approvals=1,
                timeout_hours=24,
                auto_approve_conditions={"security_score": ">0.9"}
            ),
            ApprovalCriteria(
                stage_type=ApprovalStageType.CREATOR_APPROVAL,
                required_approvers=["creator"],
                minimum_approvals=1,
                timeout_hours=168,  # 1 week
                creator_tier_specific=True
            ),
            ApprovalCriteria(
                stage_type=ApprovalStageType.BUSINESS_REVIEW,
                required_approvers=["product_manager", "business_analyst"],
                minimum_approvals=1,
                timeout_hours=72,
                business_impact_threshold=0.7
            ),
            ApprovalCriteria(
                stage_type=ApprovalStageType.EXECUTIVE_APPROVAL,
                required_approvers=["technical_director"],
                minimum_approvals=1,
                timeout_hours=96,
                escalation_rules={"high_business_impact": True}
            )
        ]
        
        # Staging deployment workflow
        staging_workflow = [
            ApprovalCriteria(
                stage_type=ApprovalStageType.AUTOMATED_VALIDATION,
                required_approvers=["system"],
                minimum_approvals=1,
                timeout_hours=1,
                auto_approve_conditions={
                    "basic_tests_passed": True,
                    "no_critical_vulnerabilities": True
                }
            ),
            ApprovalCriteria(
                stage_type=ApprovalStageType.TECHNICAL_REVIEW,
                required_approvers=["ml_engineer"],
                minimum_approvals=1,
                timeout_hours=24
            ),
            ApprovalCriteria(
                stage_type=ApprovalStageType.CREATOR_APPROVAL,
                required_approvers=["creator"],
                minimum_approvals=1,
                timeout_hours=72,
                creator_tier_specific=True
            )
        ]
        
        # Emergency hotfix workflow
        emergency_workflow = [
            ApprovalCriteria(
                stage_type=ApprovalStageType.AUTOMATED_VALIDATION,
                required_approvers=["system"],
                minimum_approvals=1,
                timeout_hours=0.5,
                auto_approve_conditions={"emergency_validated": True}
            ),
            ApprovalCriteria(
                stage_type=ApprovalStageType.TECHNICAL_REVIEW,
                required_approvers=["on_call_engineer"],
                minimum_approvals=1,
                timeout_hours=2
            ),
            ApprovalCriteria(
                stage_type=ApprovalStageType.EXECUTIVE_APPROVAL,
                required_approvers=["technical_director", "cto"],
                minimum_approvals=1,
                timeout_hours=4
            )
        ]
        
        # Store templates
        self._workflow_templates = {
            "production": production_workflow,
            "staging": staging_workflow,
            "emergency": emergency_workflow
        }
        
        logger.info(f"📋 {len(self._workflow_templates)} workflow templates initialized")
    
    def _initialize_automated_validators(self) -> None:
        """Initialize automated validation functions"""
        
        async def validate_technical_requirements(
            request: ApprovalRequest,
            stage: ApprovalStage
        ) -> ApprovalDecision:
            """Automated technical validation"""
            try:
                model_metadata = request.model_metadata
                
                # Check quality gates
                quality_gates = model_metadata.get("quality_gates", {})
                tests_passed = quality_gates.get("tests_passed", False)
                coverage = quality_gates.get("coverage", 0.0)
                performance_score = quality_gates.get("performance_score", 0.0)
                
                # Validation logic
                passed = tests_passed and coverage >= 0.8 and performance_score >= 0.85
                
                decision = ApprovalDecision(
                    decision_id=str(uuid.uuid4()),
                    approver_id="automated_validator",
                    approver_role="system",
                    decision=ApprovalStatus.APPROVED if passed else ApprovalStatus.REJECTED,
                    comments=f"Automated validation - Tests: {tests_passed}, Coverage: {coverage:.2f}, Performance: {performance_score:.2f}",
                    decided_at=datetime.now(),
                    confidence_score=0.95,
                    metadata={"validation_type": "technical", "metrics": quality_gates}
                )
                
                return decision
                
            except Exception as e:
                logger.error(f"❌ Technical validation error: {str(e)}")
                return ApprovalDecision(
                    decision_id=str(uuid.uuid4()),
                    approver_id="automated_validator",
                    approver_role="system",
                    decision=ApprovalStatus.REJECTED,
                    comments=f"Validation failed: {str(e)}",
                    decided_at=datetime.now(),
                    confidence_score=1.0
                )
        
        async def validate_security_requirements(
            request: ApprovalRequest,
            stage: ApprovalStage
        ) -> ApprovalDecision:
            """Automated security validation"""
            try:
                model_metadata = request.model_metadata
                
                # Check security metrics
                security_data = model_metadata.get("security_scan", {})
                vulnerabilities = security_data.get("vulnerabilities", [])
                security_score = security_data.get("security_score", 0.0)
                
                # Security validation
                critical_vulns = [v for v in vulnerabilities if v.get("severity") == "critical"]
                high_vulns = [v for v in vulnerabilities if v.get("severity") == "high"]
                
                passed = len(critical_vulns) == 0 and len(high_vulns) <= 2 and security_score >= 0.8
                
                decision = ApprovalDecision(
                    decision_id=str(uuid.uuid4()),
                    approver_id="security_validator",
                    approver_role="system",
                    decision=ApprovalStatus.APPROVED if passed else ApprovalStatus.REJECTED,
                    comments=f"Security validation - Critical: {len(critical_vulns)}, High: {len(high_vulns)}, Score: {security_score:.2f}",
                    decided_at=datetime.now(),
                    confidence_score=0.98,
                    metadata={"validation_type": "security", "vulnerabilities": vulnerabilities}
                )
                
                return decision
                
            except Exception as e:
                logger.error(f"❌ Security validation error: {str(e)}")
                return ApprovalDecision(
                    decision_id=str(uuid.uuid4()),
                    approver_id="security_validator",
                    approver_role="system",
                    decision=ApprovalStatus.REJECTED,
                    comments=f"Security validation failed: {str(e)}",
                    decided_at=datetime.now(),
                    confidence_score=1.0
                )
        
        async def validate_compliance_requirements(
            request: ApprovalRequest,
            stage: ApprovalStage
        ) -> ApprovalDecision:
            """Automated compliance validation"""
            try:
                model_metadata = request.model_metadata
                
                # Check compliance status
                compliance_data = model_metadata.get("compliance", {})
                gdpr_compliant = compliance_data.get("gdpr_compliant", False)
                ccpa_compliant = compliance_data.get("ccpa_compliant", False)
                data_lineage_complete = compliance_data.get("data_lineage_complete", False)
                
                # Creator-specific compliance
                creator_context = request.creator_context
                creator_consent = True
                if creator_context:
                    creator_consent = creator_context.get("consent_status") == "granted"
                
                passed = gdpr_compliant and ccpa_compliant and data_lineage_complete and creator_consent
                
                decision = ApprovalDecision(
                    decision_id=str(uuid.uuid4()),
                    approver_id="compliance_validator",
                    approver_role="system",
                    decision=ApprovalStatus.APPROVED if passed else ApprovalStatus.CONDITIONAL_APPROVAL,
                    comments=f"Compliance validation - GDPR: {gdpr_compliant}, CCPA: {ccpa_compliant}, Lineage: {data_lineage_complete}, Creator consent: {creator_consent}",
                    decided_at=datetime.now(),
                    confidence_score=0.9,
                    conditions=[] if passed else ["Address compliance gaps before production"],
                    metadata={"validation_type": "compliance", "compliance_status": compliance_data}
                )
                
                return decision
                
            except Exception as e:
                logger.error(f"❌ Compliance validation error: {str(e)}")
                return ApprovalDecision(
                    decision_id=str(uuid.uuid4()),
                    approver_id="compliance_validator",
                    approver_role="system",
                    decision=ApprovalStatus.REJECTED,
                    comments=f"Compliance validation failed: {str(e)}",
                    decided_at=datetime.now(),
                    confidence_score=1.0
                )
        
        # Register validators
        self._automated_validators = {
            ApprovalStageType.AUTOMATED_VALIDATION: validate_technical_requirements,
            ApprovalStageType.SECURITY_REVIEW: validate_security_requirements,
            ApprovalStageType.COMPLIANCE_REVIEW: validate_compliance_requirements
        }
        
        logger.info(f"🔍 {len(self._automated_validators)} automated validators initialized")
    
    def _initialize_notification_templates(self) -> None:
        """Initialize notification message templates"""
        self._notification_templates = {
            "approval_request": """
            🔔 New Model Approval Request
            
            Model: {model_name} v{model_version}
            Requested by: {requested_by}
            Target: {target_environment}
            Priority: {priority}
            
            {description}
            
            Please review and provide your approval decision.
            """,
            
            "approval_granted": """
            ✅ Model Approval Granted
            
            Model: {model_name} v{model_version}
            Approved by: {approved_by}
            Stage: {stage_name}
            
            {comments}
            """,
            
            "approval_rejected": """
            ❌ Model Approval Rejected
            
            Model: {model_name} v{model_version}
            Rejected by: {rejected_by}
            Stage: {stage_name}
            
            Reason: {rejection_reason}
            """,
            
            "escalation_notice": """
            ⚠️ Approval Request Escalated
            
            Model: {model_name} v{model_version}
            Original Stage: {stage_name}
            Escalated due to: {escalation_reason}
            
            Immediate attention required.
            """,
            
            "reminder": """
            ⏰ Approval Request Reminder
            
            Model: {model_name} v{model_version}
            Pending since: {pending_since}
            Time remaining: {time_remaining}
            
            Please review and provide your decision.
            """
        }
        
        logger.info(f"📧 {len(self._notification_templates)} notification templates initialized")
    
    async def submit_approval_request(
        self,
        model_name: str,
        model_version: str,
        target_environment: str,
        requested_by: str,
        description: str,
        model_metadata: Dict[str, Any],
        priority: Priority = Priority.MEDIUM,
        creator_context: Optional[Dict[str, Any]] = None,
        business_justification: str = "",
        workflow_template: str = "production"
    ) -> str:
        """
        Submit model approval request
        
        Args:
            model_name: Name of the model
            model_version: Version of the model
            target_environment: Target deployment environment
            requested_by: User submitting the request
            description: Description of the request
            model_metadata: Model metadata for validation
            priority: Request priority
            creator_context: Creator-specific context
            business_justification: Business justification
            workflow_template: Workflow template to use
            
        Returns:
            Request ID
        """
        try:
            request_id = str(uuid.uuid4())
            
            # Get workflow template
            if workflow_template not in self._workflow_templates:
                workflow_template = "production"
            
            template_criteria = self._workflow_templates[workflow_template]
            
            # Create approval stages
            stages = []
            for i, criteria in enumerate(template_criteria):
                stage = ApprovalStage(
                    stage_id=f"{request_id}_stage_{i}",
                    stage_type=criteria.stage_type,
                    criteria=criteria
                )
                stages.append(stage)
            
            # Create approval request
            request = ApprovalRequest(
                request_id=request_id,
                model_name=model_name,
                model_version=model_version,
                requested_by=requested_by,
                requested_at=datetime.now(),
                priority=priority,
                description=description,
                target_environment=target_environment,
                model_metadata=model_metadata,
                creator_context=creator_context,
                business_justification=business_justification,
                stages=stages
            )
            
            # Store request
            self._approval_requests[request_id] = request
            
            # Start first stage
            await self._start_next_stage(request)
            
            self._workflow_metrics["requests_submitted"] += 1
            
            logger.info(f"📝 Approval request submitted: {request_id} for {model_name} v{model_version}")
            
            return request_id
            
        except Exception as e:
            logger.error(f"❌ Failed to submit approval request: {str(e)}")
            raise
    
    async def _start_next_stage(self, request: ApprovalRequest) -> None:
        """Start the next stage in the approval workflow"""
        try:
            if request.current_stage_index >= len(request.stages):
                # All stages completed - approve request
                await self._complete_approval_request(request, ApprovalStatus.APPROVED)
                return
            
            current_stage = request.stages[request.current_stage_index]
            current_stage.status = ApprovalStatus.IN_REVIEW
            current_stage.started_at = datetime.now()
            
            logger.info(f"🔄 Starting stage {current_stage.stage_type.value} for request {request.request_id}")
            
            # Handle automated validation stages
            if current_stage.stage_type == ApprovalStageType.AUTOMATED_VALIDATION:
                await self._run_automated_validation(request, current_stage)
            else:
                # Manual approval stage - send notifications
                await self._send_stage_notifications(request, current_stage)
            
            # Set up timeout monitoring
            asyncio.create_task(self._monitor_stage_timeout(request, current_stage))
            
        except Exception as e:
            logger.error(f"❌ Stage start error: {str(e)}")
    
    async def _run_automated_validation(self, request: ApprovalRequest, stage: ApprovalStage) -> None:
        """Run automated validation for a stage"""
        try:
            if stage.stage_type in self._automated_validators:
                validator = self._automated_validators[stage.stage_type]
                decision = await validator(request, stage)
                
                # Add decision to stage
                stage.decisions.append(decision)
                
                # Process decision
                if decision.decision == ApprovalStatus.APPROVED:
                    await self._complete_stage(request, stage, ApprovalStatus.APPROVED)
                elif decision.decision == ApprovalStatus.CONDITIONAL_APPROVAL:
                    await self._complete_stage(request, stage, ApprovalStatus.CONDITIONAL_APPROVAL)
                else:
                    await self._complete_stage(request, stage, ApprovalStatus.REJECTED)
            else:
                # No validator available - skip stage
                logger.warning(f"⚠️ No validator for stage type {stage.stage_type.value}")
                await self._complete_stage(request, stage, ApprovalStatus.APPROVED)
                
        except Exception as e:
            logger.error(f"❌ Automated validation error: {str(e)}")
            # Fail the stage on validation error
            await self._complete_stage(request, stage, ApprovalStatus.REJECTED)
    
    async def _send_stage_notifications(self, request: ApprovalRequest, stage: ApprovalStage) -> None:
        """Send notifications for manual approval stage"""
        try:
            template = self._notification_templates["approval_request"]
            
            message = template.format(
                model_name=request.model_name,
                model_version=request.model_version,
                requested_by=request.requested_by,
                target_environment=request.target_environment,
                priority=request.priority.value,
                description=request.description
            )
            
            # Send notifications to required approvers
            for approver in stage.criteria.required_approvers:
                success = await self._notification_handler.send_notification(
                    NotificationType.EMAIL,
                    approver,
                    f"Approval Request: {request.model_name} v{request.model_version}",
                    message,
                    {"request_id": request.request_id, "stage_id": stage.stage_id}
                )
                
                if success:
                    stage.notifications_sent.append(approver)
            
        except Exception as e:
            logger.error(f"❌ Notification error: {str(e)}")
    
    async def submit_approval_decision(
        self,
        request_id: str,
        approver_id: str,
        decision: ApprovalStatus,
        comments: str,
        conditions: Optional[List[str]] = None
    ) -> bool:
        """
        Submit an approval decision
        
        Args:
            request_id: Request ID
            approver_id: ID of the approver
            decision: Approval decision
            comments: Comments from approver
            conditions: Conditions if conditional approval
            
        Returns:
            Success status
        """
        try:
            if request_id not in self._approval_requests:
                logger.error(f"❌ Request {request_id} not found")
                return False
            
            request = self._approval_requests[request_id]
            
            if request.current_stage_index >= len(request.stages):
                logger.error(f"❌ No active stage for request {request_id}")
                return False
            
            current_stage = request.stages[request.current_stage_index]
            
            # Verify approver is authorized for this stage
            if approver_id not in current_stage.criteria.required_approvers:
                logger.error(f"❌ Approver {approver_id} not authorized for stage {current_stage.stage_type.value}")
                return False
            
            # Check if approver already provided decision
            existing_decisions = [d for d in current_stage.decisions if d.approver_id == approver_id]
            if existing_decisions:
                logger.error(f"❌ Approver {approver_id} already provided decision")
                return False
            
            # Create decision record
            approval_decision = ApprovalDecision(
                decision_id=str(uuid.uuid4()),
                approver_id=approver_id,
                approver_role=self._get_approver_role(approver_id),
                decision=decision,
                comments=comments,
                decided_at=datetime.now(),
                conditions=conditions or []
            )
            
            current_stage.decisions.append(approval_decision)
            
            # Check if stage is complete
            await self._evaluate_stage_completion(request, current_stage)
            
            logger.info(f"✅ Decision recorded: {approver_id} {decision.value} for {request_id}")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Decision submission error: {str(e)}")
            return False
    
    def _get_approver_role(self, approver_id: str) -> str:
        """Get role for approver"""
        # In real implementation, would look up from user database
        role_mapping = {
            "ml_engineer": "ML Engineer",
            "platform_engineer": "Platform Engineer",
            "security_engineer": "Security Engineer",
            "product_manager": "Product Manager",
            "business_analyst": "Business Analyst",
            "technical_director": "Technical Director",
            "creator": "Creator",
            "on_call_engineer": "On-call Engineer",
            "cto": "CTO"
        }
        
        return role_mapping.get(approver_id, "Unknown Role")
    
    async def _evaluate_stage_completion(self, request: ApprovalRequest, stage: ApprovalStage) -> None:
        """Evaluate if a stage is complete"""
        try:
            approvals = [d for d in stage.decisions if d.decision == ApprovalStatus.APPROVED]
            rejections = [d for d in stage.decisions if d.decision == ApprovalStatus.REJECTED]
            conditional_approvals = [d for d in stage.decisions if d.decision == ApprovalStatus.CONDITIONAL_APPROVAL]
            
            # Check rejection threshold
            if len(rejections) > stage.criteria.maximum_rejections:
                await self._complete_stage(request, stage, ApprovalStatus.REJECTED)
                return
            
            # Check approval threshold
            total_approvals = len(approvals) + len(conditional_approvals)
            if total_approvals >= stage.criteria.minimum_approvals:
                # Determine stage outcome
                if len(conditional_approvals) > 0:
                    await self._complete_stage(request, stage, ApprovalStatus.CONDITIONAL_APPROVAL)
                else:
                    await self._complete_stage(request, stage, ApprovalStatus.APPROVED)
                return
            
            # Stage still pending - check if all required approvers responded
            responded_approvers = {d.approver_id for d in stage.decisions}
            required_approvers = set(stage.criteria.required_approvers)
            
            if responded_approvers >= required_approvers:
                # All approvers responded but didn't meet threshold
                await self._complete_stage(request, stage, ApprovalStatus.REJECTED)
            
        except Exception as e:
            logger.error(f"❌ Stage evaluation error: {str(e)}")
    
    async def _complete_stage(self, request: ApprovalRequest, stage: ApprovalStage, status: ApprovalStatus) -> None:
        """Complete a stage with given status"""
        try:
            stage.status = status
            stage.completed_at = datetime.now()
            
            logger.info(f"🏁 Stage {stage.stage_type.value} completed with status {status.value} for request {request.request_id}")
            
            if status == ApprovalStatus.APPROVED or status == ApprovalStatus.CONDITIONAL_APPROVAL:
                # Move to next stage
                request.current_stage_index += 1
                await self._start_next_stage(request)
            else:
                # Stage rejected - complete entire request as rejected
                await self._complete_approval_request(request, ApprovalStatus.REJECTED)
            
        except Exception as e:
            logger.error(f"❌ Stage completion error: {str(e)}")
    
    async def _complete_approval_request(self, request: ApprovalRequest, final_status: ApprovalStatus) -> None:
        """Complete the entire approval request"""
        try:
            request.overall_status = final_status
            
            if final_status == ApprovalStatus.APPROVED:
                request.approved_at = datetime.now()
                request.approved_by = "workflow_system"
                self._workflow_metrics["requests_approved"] += 1
            else:
                self._workflow_metrics["requests_rejected"] += 1
            
            # Calculate approval time
            approval_time = (datetime.now() - request.requested_at).total_seconds() / 3600
            self._workflow_metrics["avg_approval_time_hours"] = (
                (self._workflow_metrics["avg_approval_time_hours"] * (self._workflow_metrics["requests_approved"] + self._workflow_metrics["requests_rejected"] - 1) + approval_time)
                / (self._workflow_metrics["requests_approved"] + self._workflow_metrics["requests_rejected"])
            )
            
            # Send completion notification
            await self._send_completion_notification(request, final_status)
            
            logger.info(f"🎯 Approval request {request.request_id} completed with status {final_status.value}")
            
        except Exception as e:
            logger.error(f"❌ Request completion error: {str(e)}")
    
    async def _send_completion_notification(self, request: ApprovalRequest, status: ApprovalStatus) -> None:
        """Send completion notification"""
        try:
            if status == ApprovalStatus.APPROVED:
                template = self._notification_templates["approval_granted"]
                message = template.format(
                    model_name=request.model_name,
                    model_version=request.model_version,
                    approved_by="workflow_system",
                    stage_name="final",
                    comments="All approval stages completed successfully"
                )
            else:
                template = self._notification_templates["approval_rejected"]
                message = template.format(
                    model_name=request.model_name,
                    model_version=request.model_version,
                    rejected_by="workflow_system",
                    stage_name="workflow",
                    rejection_reason=request.rejection_reason or "Approval criteria not met"
                )
            
            # Notify requester
            await self._notification_handler.send_notification(
                NotificationType.EMAIL,
                request.requested_by,
                f"Approval {'Granted' if status == ApprovalStatus.APPROVED else 'Rejected'}: {request.model_name}",
                message,
                {"request_id": request.request_id, "final_status": status.value}
            )
            
        except Exception as e:
            logger.error(f"❌ Completion notification error: {str(e)}")
    
    async def _monitor_stage_timeout(self, request: ApprovalRequest, stage: ApprovalStage) -> None:
        """Monitor stage timeout and trigger escalation"""
        try:
            timeout_seconds = stage.criteria.timeout_hours * 3600
            await asyncio.sleep(timeout_seconds)
            
            # Check if stage is still active
            if stage.status == ApprovalStatus.IN_REVIEW:
                # Stage timed out - trigger escalation
                await self._escalate_stage(request, stage, "timeout")
                
        except asyncio.CancelledError:
            # Stage completed before timeout
            pass
        except Exception as e:
            logger.error(f"❌ Timeout monitoring error: {str(e)}")
    
    async def _escalate_stage(self, request: ApprovalRequest, stage: ApprovalStage, reason: str) -> None:
        """Escalate a stage"""
        try:
            stage.escalated = True
            
            # Add escalation decision
            escalation_decision = ApprovalDecision(
                decision_id=str(uuid.uuid4()),
                approver_id="escalation_system",
                approver_role="system",
                decision=ApprovalStatus.ESCALATED,
                comments=f"Stage escalated due to: {reason}",
                decided_at=datetime.now(),
                metadata={"escalation_reason": reason}
            )
            
            stage.decisions.append(escalation_decision)
            
            # Send escalation notification
            template = self._notification_templates["escalation_notice"]
            message = template.format(
                model_name=request.model_name,
                model_version=request.model_version,
                stage_name=stage.stage_type.value,
                escalation_reason=reason
            )
            
            # Notify escalation recipients (would be configured per stage)
            escalation_recipients = ["technical_director", "cto"]
            for recipient in escalation_recipients:
                await self._notification_handler.send_notification(
                    NotificationType.EMAIL,
                    recipient,
                    f"ESCALATION: {request.model_name} Approval",
                    message,
                    {"request_id": request.request_id, "stage_id": stage.stage_id}
                )
            
            self._workflow_metrics["escalations_triggered"] += 1
            
            logger.warning(f"⚠️ Stage escalated: {stage.stage_id} due to {reason}")
            
        except Exception as e:
            logger.error(f"❌ Escalation error: {str(e)}")
    
    def get_approval_request(self, request_id: str) -> Optional[Dict[str, Any]]:
        """Get approval request by ID"""
        if request_id in self._approval_requests:
            return self._approval_requests[request_id].to_dict()
        return None
    
    def get_pending_approvals(self, approver_id: str) -> List[Dict[str, Any]]:
        """Get pending approvals for an approver"""
        pending_approvals = []
        
        for request in self._approval_requests.values():
            if request.overall_status in [ApprovalStatus.PENDING, ApprovalStatus.IN_REVIEW]:
                if request.current_stage_index < len(request.stages):
                    current_stage = request.stages[request.current_stage_index]
                    
                    if approver_id in current_stage.criteria.required_approvers:
                        # Check if approver already decided
                        existing_decisions = [d for d in current_stage.decisions if d.approver_id == approver_id]
                        if not existing_decisions:
                            pending_approvals.append({
                                "request": request.to_dict(),
                                "stage": current_stage.to_dict()
                            })
        
        return pending_approvals
    
    def get_workflow_metrics(self) -> Dict[str, Any]:
        """Get workflow performance metrics"""
        return {
            **self._workflow_metrics,
            "active_requests": len([r for r in self._approval_requests.values() if r.overall_status in [ApprovalStatus.PENDING, ApprovalStatus.IN_REVIEW]]),
            "workflow_templates": len(self._workflow_templates),
            "automated_validators": len(self._automated_validators)
        }
    
    def health_check(self) -> str:
        """Health check for approval workflow"""
        try:
            # Check for stuck requests
            now = datetime.now()
            stuck_requests = [
                r for r in self._approval_requests.values()
                if r.overall_status == ApprovalStatus.IN_REVIEW and 
                (now - r.requested_at).total_seconds() > 7 * 24 * 3600  # 1 week
            ]
            
            if stuck_requests:
                return f"WARNING: {len(stuck_requests)} requests stuck for over 1 week"
            
            # Check workflow templates
            if not self._workflow_templates:
                return "ERROR: No workflow templates configured"
            
            return "OPERATIONAL"
            
        except Exception as e:
            return f"ERROR: {str(e)}"


# Export main class and enums
__all__ = [
    "ModelApprovalWorkflow",
    "ApprovalStatus",
    "ApprovalStageType",
    "Priority",
    "NotificationType",
    "ApprovalCriteria",
    "ApprovalDecision",
    "ApprovalStage",
    "ApprovalRequest",
    "ApprovalNotificationHandler",
    "DefaultNotificationHandler"
]