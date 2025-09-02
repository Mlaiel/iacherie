"""Refund Processing Workflow - Automated refund management system
=================================================================

Advanced refund processing system with automated workflows,
approval chains, financial reconciliation, and compliance tracking.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: All rights reserved. Unauthorized use prohibited.
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum
import redis
import asyncpg
from decimal import Decimal
from fastapi import HTTPException
import json

logger = logging.getLogger(__name__)

class RefundStatus(Enum):
    """Refund processing status"""
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class RefundReason(Enum):
    """Reasons for refund requests"""
    CUSTOMER_REQUEST = "customer_request"
    BILLING_ERROR = "billing_error"
    TECHNICAL_ISSUE = "technical_issue"
    FRAUD_PROTECTION = "fraud_protection"
    CHARGEBACK = "chargeback"
    SUBSCRIPTION_CANCELLATION = "subscription_cancellation"
    SERVICE_UNAVAILABLE = "service_unavailable"
    DUPLICATE_PAYMENT = "duplicate_payment"
    POLICY_VIOLATION = "policy_violation"

class RefundType(Enum):
    """Types of refunds"""
    FULL_REFUND = "full_refund"
    PARTIAL_REFUND = "partial_refund"
    PRORATED_REFUND = "prorated_refund"
    CREDIT_NOTE = "credit_note"
    ACCOUNT_CREDIT = "account_credit"

class WorkflowAction(Enum):
    """Workflow actions"""
    SUBMIT = "submit"
    APPROVE = "approve"
    REJECT = "reject"
    PROCESS = "process"
    COMPLETE = "complete"
    CANCEL = "cancel"
    ESCALATE = "escalate"
    REVIEW = "review"

@dataclass
class RefundRequest:
    """Refund request details"""
    request_id: str
    customer_id: str
    payment_id: str
    original_amount: Decimal
    refund_amount: Decimal
    currency: str
    reason: RefundReason
    refund_type: RefundType
    description: str
    status: RefundStatus
    requested_at: datetime
    requested_by: str
    metadata: Dict[str, Any]

@dataclass
class WorkflowStep:
    """Workflow step definition"""
    step_id: str
    name: str
    description: str
    required_role: Optional[str]
    auto_execute: bool
    timeout_hours: Optional[int]
    conditions: Dict[str, Any]
    actions: List[WorkflowAction]

@dataclass
class RefundWorkflow:
    """Refund processing workflow"""
    workflow_id: str
    request_id: str
    current_step: str
    status: RefundStatus
    steps_completed: List[str]
    assigned_to: Optional[str]
    deadline: Optional[datetime]
    created_at: datetime
    updated_at: datetime

class RefundProcessingWorkflow:
    """Advanced refund processing and workflow management"""
    
    def __init__(self, redis_client: redis.Redis, db_pool: asyncpg.Pool):
        self.redis = redis_client
        self.db_pool = db_pool
        self.workflow_templates = {}
        self.approval_limits = {}
        
    async def initialize(self) -> None:
        """Initialize refund processing workflow system"""
        try:
            await self._setup_database_tables()
            await self._load_workflow_templates()
            await self._load_approval_limits()
            logger.info("Refund Processing Workflow System initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Refund Processing Workflow System: {e}")
            raise
            
    async def _setup_database_tables(self) -> None:
        """Setup required database tables"""
        async with self.db_pool.acquire() as conn:
            # Refund requests table
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS refund_requests (
                    request_id VARCHAR PRIMARY KEY,
                    customer_id VARCHAR NOT NULL,
                    payment_id VARCHAR NOT NULL,
                    original_amount DECIMAL(15,2) NOT NULL,
                    refund_amount DECIMAL(15,2) NOT NULL,
                    currency VARCHAR(3) NOT NULL,
                    reason VARCHAR(30) NOT NULL,
                    refund_type VARCHAR(20) NOT NULL,
                    description TEXT,
                    status VARCHAR(20) NOT NULL,
                    requested_at TIMESTAMP DEFAULT NOW(),
                    requested_by VARCHAR(100),
                    metadata JSONB,
                    created_at TIMESTAMP DEFAULT NOW(),
                    updated_at TIMESTAMP DEFAULT NOW()
                )
            """)
            
            # Refund workflows table
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS refund_workflows (
                    workflow_id VARCHAR PRIMARY KEY,
                    request_id VARCHAR REFERENCES refund_requests(request_id),
                    current_step VARCHAR(50) NOT NULL,
                    status VARCHAR(20) NOT NULL,
                    steps_completed JSONB DEFAULT '[]',
                    assigned_to VARCHAR(100),
                    deadline TIMESTAMP,
                    created_at TIMESTAMP DEFAULT NOW(),
                    updated_at TIMESTAMP DEFAULT NOW()
                )
            """)
            
            # Workflow history table
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS refund_workflow_history (
                    history_id VARCHAR PRIMARY KEY,
                    workflow_id VARCHAR REFERENCES refund_workflows(workflow_id),
                    step_name VARCHAR(50) NOT NULL,
                    action VARCHAR(20) NOT NULL,
                    performed_by VARCHAR(100),
                    performed_at TIMESTAMP DEFAULT NOW(),
                    comments TEXT,
                    metadata JSONB
                )
            """)
            
            # Refund transactions table
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS refund_transactions (
                    transaction_id VARCHAR PRIMARY KEY,
                    request_id VARCHAR REFERENCES refund_requests(request_id),
                    gateway_transaction_id VARCHAR,
                    amount DECIMAL(15,2) NOT NULL,
                    currency VARCHAR(3) NOT NULL,
                    gateway VARCHAR(20),
                    status VARCHAR(20) NOT NULL,
                    processed_at TIMESTAMP,
                    failure_reason TEXT,
                    metadata JSONB,
                    created_at TIMESTAMP DEFAULT NOW()
                )
            """)
            
            # Create indexes
            await conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_refund_requests_customer 
                ON refund_requests(customer_id)
            """)
            await conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_refund_requests_status 
                ON refund_requests(status, requested_at)
            """)
            
    async def _load_workflow_templates(self) -> None:
        """Load refund workflow templates"""
        self.workflow_templates = {
            "standard_refund": [
                WorkflowStep(
                    step_id="validation",
                    name="Request Validation",
                    description="Validate refund request details",
                    required_role=None,
                    auto_execute=True,
                    timeout_hours=None,
                    conditions={"auto_validate": True},
                    actions=[WorkflowAction.APPROVE, WorkflowAction.REJECT]
                ),
                WorkflowStep(
                    step_id="approval",
                    name="Management Approval",
                    description="Require management approval for refund",
                    required_role="manager",
                    auto_execute=False,
                    timeout_hours=24,
                    conditions={"amount_threshold": 100},
                    actions=[WorkflowAction.APPROVE, WorkflowAction.REJECT, WorkflowAction.ESCALATE]
                ),
                WorkflowStep(
                    step_id="processing",
                    name="Process Refund",
                    description="Process refund through payment gateway",
                    required_role="finance",
                    auto_execute=True,
                    timeout_hours=4,
                    conditions={"gateway_available": True},
                    actions=[WorkflowAction.PROCESS, WorkflowAction.COMPLETE]
                ),
                WorkflowStep(
                    step_id="completion",
                    name="Complete Refund",
                    description="Finalize refund and update records",
                    required_role=None,
                    auto_execute=True,
                    timeout_hours=None,
                    conditions={},
                    actions=[WorkflowAction.COMPLETE]
                )
            ],
            "high_value_refund": [
                WorkflowStep(
                    step_id="validation",
                    name="Enhanced Validation",
                    description="Enhanced validation for high-value refunds",
                    required_role="senior_analyst",
                    auto_execute=False,
                    timeout_hours=4,
                    conditions={"enhanced_checks": True},
                    actions=[WorkflowAction.APPROVE, WorkflowAction.REJECT]
                ),
                WorkflowStep(
                    step_id="finance_review",
                    name="Finance Review",
                    description="Finance team review for high-value refund",
                    required_role="finance_manager",
                    auto_execute=False,
                    timeout_hours=12,
                    conditions={"amount_threshold": 1000},
                    actions=[WorkflowAction.APPROVE, WorkflowAction.REJECT, WorkflowAction.ESCALATE]
                ),
                WorkflowStep(
                    step_id="executive_approval",
                    name="Executive Approval",
                    description="Executive approval for high-value refund",
                    required_role="executive",
                    auto_execute=False,
                    timeout_hours=48,
                    conditions={"amount_threshold": 5000},
                    actions=[WorkflowAction.APPROVE, WorkflowAction.REJECT]
                ),
                WorkflowStep(
                    step_id="processing",
                    name="Secure Processing",
                    description="Secure processing for high-value refund",
                    required_role="finance_manager",
                    auto_execute=False,
                    timeout_hours=2,
                    conditions={"dual_authorization": True},
                    actions=[WorkflowAction.PROCESS, WorkflowAction.COMPLETE]
                )
            ]
        }
        
    async def _load_approval_limits(self) -> None:
        """Load approval limits by role"""
        self.approval_limits = {
            "support_agent": Decimal("50"),
            "supervisor": Decimal("200"),
            "manager": Decimal("1000"),
            "finance_manager": Decimal("5000"),
            "executive": Decimal("999999")
        }
        
    async def submit_refund_request(
        self,
        customer_id: str,
        payment_id: str,
        refund_amount: Decimal,
        currency: str,
        reason: RefundReason,
        refund_type: RefundType = RefundType.FULL_REFUND,
        description: str = "",
        requested_by: str = None,
        metadata: Dict[str, Any] = None
    ) -> RefundRequest:
        """Submit new refund request"""
        try:
            request_id = f"REF_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}_{customer_id[:8]}"
            
            # Get original payment amount (would query actual payment data)
            original_amount = refund_amount  # Simplified for now
            
            refund_request = RefundRequest(
                request_id=request_id,
                customer_id=customer_id,
                payment_id=payment_id,
                original_amount=original_amount,
                refund_amount=refund_amount,
                currency=currency,
                reason=reason,
                refund_type=refund_type,
                description=description,
                status=RefundStatus.PENDING,
                requested_at=datetime.utcnow(),
                requested_by=requested_by or "system",
                metadata=metadata or {}
            )
            
            # Store refund request
            async with self.db_pool.acquire() as conn:
                await conn.execute("""
                    INSERT INTO refund_requests (
                        request_id, customer_id, payment_id, original_amount,
                        refund_amount, currency, reason, refund_type,
                        description, status, requested_by, metadata
                    ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12)
                """, 
                request_id, customer_id, payment_id, original_amount,
                refund_amount, currency, reason.value, refund_type.value,
                description, RefundStatus.PENDING.value, requested_by,
                json.dumps(metadata or {})
                )
            
            # Create and start workflow
            await self._create_workflow(refund_request)
            
            logger.info(f"Refund request submitted: {request_id}")
            return refund_request
            
        except Exception as e:
            logger.error(f"Failed to submit refund request: {e}")
            raise
            
    async def _create_workflow(self, refund_request: RefundRequest) -> RefundWorkflow:
        """Create workflow for refund request"""
        try:
            workflow_id = f"WF_{refund_request.request_id}"
            
            # Determine workflow template based on amount and reason
            template_name = self._select_workflow_template(refund_request)
            workflow_steps = self.workflow_templates.get(template_name, self.workflow_templates["standard_refund"])
            
            # Create workflow
            workflow = RefundWorkflow(
                workflow_id=workflow_id,
                request_id=refund_request.request_id,
                current_step=workflow_steps[0].step_id,
                status=RefundStatus.PENDING,
                steps_completed=[],
                assigned_to=None,
                deadline=None,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            
            # Store workflow
            async with self.db_pool.acquire() as conn:
                await conn.execute("""
                    INSERT INTO refund_workflows (
                        workflow_id, request_id, current_step, status,
                        steps_completed, assigned_to, deadline
                    ) VALUES ($1, $2, $3, $4, $5, $6, $7)
                """, 
                workflow_id, refund_request.request_id, workflow.current_step,
                workflow.status.value, json.dumps(workflow.steps_completed),
                workflow.assigned_to, workflow.deadline
                )
            
            # Start workflow processing
            await self._process_workflow_step(workflow, workflow_steps[0], refund_request)
            
            return workflow
            
        except Exception as e:
            logger.error(f"Failed to create workflow: {e}")
            raise
            
    def _select_workflow_template(self, refund_request: RefundRequest) -> str:
        """Select appropriate workflow template"""
        # High-value refunds need additional approvals
        if refund_request.refund_amount >= Decimal("1000"):
            return "high_value_refund"
        
        # Fraud-related refunds need enhanced validation
        if refund_request.reason == RefundReason.FRAUD_PROTECTION:
            return "high_value_refund"
            
        return "standard_refund"
        
    async def _process_workflow_step(
        self,
        workflow: RefundWorkflow,
        step: WorkflowStep,
        refund_request: RefundRequest
    ) -> None:
        """Process individual workflow step"""
        try:
            if step.auto_execute:
                # Auto-execute step
                result = await self._execute_step_action(step, workflow, refund_request)
                
                if result["success"]:
                    await self._advance_workflow(workflow, step, result["action"])
                else:
                    await self._handle_step_failure(workflow, step, result["error"])
            else:
                # Manual step - assign to user and set deadline
                assigned_user = await self._assign_step_to_user(step, refund_request)
                deadline = datetime.utcnow() + timedelta(hours=step.timeout_hours) if step.timeout_hours else None
                
                # Update workflow
                async with self.db_pool.acquire() as conn:
                    await conn.execute("""
                        UPDATE refund_workflows 
                        SET assigned_to = $1, deadline = $2, updated_at = NOW()
                        WHERE workflow_id = $3
                    """, assigned_user, deadline, workflow.workflow_id)
                    
                # Log workflow history
                await self._log_workflow_history(
                    workflow.workflow_id, step.name, "assigned",
                    assigned_user, f"Step assigned to {assigned_user}"
                )
                
        except Exception as e:
            logger.error(f"Failed to process workflow step: {e}")
            raise
            
    async def _execute_step_action(
        self,
        step: WorkflowStep,
        workflow: RefundWorkflow,
        refund_request: RefundRequest
    ) -> Dict[str, Any]:
        """Execute automated step action"""
        try:
            if step.step_id == "validation":
                return await self._validate_refund_request(refund_request)
            elif step.step_id == "processing":
                return await self._process_refund_payment(refund_request)
            elif step.step_id == "completion":
                return await self._complete_refund(refund_request)
            else:
                return {"success": True, "action": WorkflowAction.APPROVE}
                
        except Exception as e:

                
            logger.error(f"Error: {e}")

                
            raise
            return {"success": False, "error": str(e)}
            
    async def _validate_refund_request(self, refund_request: RefundRequest) -> Dict[str, Any]:
        """Validate refund request"""
        try:
            # Validation checks
            validation_errors = []
            
            # Check refund amount
            if refund_request.refund_amount <= 0:
                validation_errors.append("Invalid refund amount")
                
            if refund_request.refund_amount > refund_request.original_amount:
                validation_errors.append("Refund amount exceeds original payment")
                
            # Check payment exists and is refundable
            # (Would check actual payment data in production)
            
            # Check refund policy
            if refund_request.reason == RefundReason.CUSTOMER_REQUEST:
                # Check if within refund window
                days_since_payment = 30  # Simulated
                if days_since_payment > 30:
                    validation_errors.append("Refund request outside policy window")
                    
            if validation_errors:
                return {
                    "success": False,
                    "action": WorkflowAction.REJECT,
                    "errors": validation_errors
                }
            else:
                return {"success": True, "action": WorkflowAction.APPROVE}
                
        except Exception as e:

                
            logger.error(f"Error: {e}")

                
            raise
            return {"success": False, "error": str(e)}
            
    async def _process_refund_payment(self, refund_request: RefundRequest) -> Dict[str, Any]:
        """Process refund through payment gateway"""
        try:
            transaction_id = f"RFTX_{refund_request.request_id}_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"
            
            # In production, this would integrate with actual payment gateways
            # For now, simulate successful refund processing
            
            # Store refund transaction
            async with self.db_pool.acquire() as conn:
                await conn.execute("""
                    INSERT INTO refund_transactions (
                        transaction_id, request_id, amount, currency,
                        gateway, status, processed_at, metadata
                    ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
                """, 
                transaction_id, refund_request.request_id,
                refund_request.refund_amount, refund_request.currency,
                "stripe", "completed", datetime.utcnow(),
                json.dumps({"gateway_ref": f"re_{transaction_id}"})
                )
            
            return {
                "success": True,
                "action": WorkflowAction.COMPLETE,
                "transaction_id": transaction_id
            }
            
        except Exception as e:

            
            logger.error(f"Error: {e}")

            
            raise
            return {"success": False, "error": str(e)}
            
    async def _complete_refund(self, refund_request: RefundRequest) -> Dict[str, Any]:
        """Complete refund processing"""
        try:
            # Update refund request status
            async with self.db_pool.acquire() as conn:
                await conn.execute("""
                    UPDATE refund_requests 
                    SET status = $1, updated_at = NOW()
                    WHERE request_id = $2
                """, RefundStatus.COMPLETED.value, refund_request.request_id)
            
            # Additional completion tasks (notifications, accounting entries, etc.)
            # would be performed here
            
            return {"success": True, "action": WorkflowAction.COMPLETE}
            
        except Exception as e:

            
            logger.error(f"Error: {e}")

            
            raise
            return {"success": False, "error": str(e)}
            
    async def _assign_step_to_user(self, step: WorkflowStep, refund_request: RefundRequest) -> str:
        """Assign workflow step to appropriate user"""
        # In production, this would use actual user management system
        # For now, simulate assignment based on role
        
        role_assignments = {
            "manager": "manager_001",
            "finance": "finance_001",
            "senior_analyst": "analyst_001",
            "finance_manager": "finance_mgr_001",
            "executive": "exec_001"
        }
        
        return role_assignments.get(step.required_role, "default_user")
        
    async def _advance_workflow(
        self,
        workflow: RefundWorkflow,
        completed_step: WorkflowStep,
        action: WorkflowAction
    ) -> None:
        """Advance workflow to next step"""
        try:
            # Get workflow template
            template_name = self._select_workflow_template_by_id(workflow.request_id)
            workflow_steps = self.workflow_templates.get(template_name, self.workflow_templates["standard_refund"])
            
            # Find current step index
            current_step_index = next(
                (i for i, step in enumerate(workflow_steps) if step.step_id == workflow.current_step),
                -1
            )
            
            if current_step_index == -1:
                raise ValueError(f"Current step not found: {workflow.current_step}")
                
            # Update completed steps
            workflow.steps_completed.append(completed_step.step_id)
            
            # Determine next step
            if action == WorkflowAction.REJECT:
                # Reject workflow
                new_status = RefundStatus.REJECTED
                next_step = None
            elif action == WorkflowAction.CANCEL:
                # Cancel workflow
                new_status = RefundStatus.CANCELLED
                next_step = None
            elif current_step_index < len(workflow_steps) - 1:
                # Move to next step
                next_step = workflow_steps[current_step_index + 1].step_id
                new_status = RefundStatus.PROCESSING
            else:
                # Workflow completed
                next_step = None
                new_status = RefundStatus.COMPLETED
                
            # Update workflow
            async with self.db_pool.acquire() as conn:
                await conn.execute("""
                    UPDATE refund_workflows 
                    SET current_step = $1, status = $2, steps_completed = $3,
                        assigned_to = NULL, deadline = NULL, updated_at = NOW()
                    WHERE workflow_id = $4
                """, 
                next_step, new_status.value, json.dumps(workflow.steps_completed),
                workflow.workflow_id
                )
                
            # Log workflow history
            await self._log_workflow_history(
                workflow.workflow_id, completed_step.name, action.value,
                None, f"Step completed with action: {action.value}"
            )
            
            # If there's a next step, process it
            if next_step and new_status == RefundStatus.PROCESSING:
                next_step_obj = next(
                    (step for step in workflow_steps if step.step_id == next_step),
                    None
                )
                if next_step_obj:
                    # Get refund request for next step
                    async with self.db_pool.acquire() as conn:
                        row = await conn.fetchrow("""
                            SELECT * FROM refund_requests WHERE request_id = $1
                        """, workflow.request_id)
                        
                    refund_request = RefundRequest(
                        request_id=row['request_id'],
                        customer_id=row['customer_id'],
                        payment_id=row['payment_id'],
                        original_amount=row['original_amount'],
                        refund_amount=row['refund_amount'],
                        currency=row['currency'],
                        reason=RefundReason(row['reason']),
                        refund_type=RefundType(row['refund_type']),
                        description=row['description'],
                        status=RefundStatus(row['status']),
                        requested_at=row['requested_at'],
                        requested_by=row['requested_by'],
                        metadata=row['metadata'] or {}
                    )
                    
                    workflow.current_step = next_step
                    workflow.status = new_status
                    await self._process_workflow_step(workflow, next_step_obj, refund_request)
                    
        except Exception as e:
            logger.error(f"Failed to advance workflow: {e}")
            raise
            
    def _select_workflow_template_by_id(self, request_id: str) -> str:
        """Select workflow template by request ID (simplified)"""
        # In production, this would look up the actual request
        return "standard_refund"
        
    async def _handle_step_failure(
        self,
        workflow: RefundWorkflow,
        step: WorkflowStep,
        error: str
    ) -> None:
        """Handle workflow step failure"""
        try:
            # Log failure
            await self._log_workflow_history(
                workflow.workflow_id, step.name, "failed",
                None, f"Step failed: {error}"
            )
            
            # Update workflow status
            async with self.db_pool.acquire() as conn:
                await conn.execute("""
                    UPDATE refund_workflows 
                    SET status = $1, updated_at = NOW()
                    WHERE workflow_id = $2
                """, RefundStatus.FAILED.value, workflow.workflow_id)
                
                # Update refund request status
                await conn.execute("""
                    UPDATE refund_requests 
                    SET status = $1, updated_at = NOW()
                    WHERE request_id = $2
                """, RefundStatus.FAILED.value, workflow.request_id)
                
        except Exception as e:
            logger.error(f"Failed to handle step failure: {e}")
            
    async def _log_workflow_history(
        self,
        workflow_id: str,
        step_name: str,
        action: str,
        performed_by: Optional[str],
        comments: str,
        metadata: Dict[str, Any] = None
    ) -> None:
        """Log workflow history entry"""
        try:
            history_id = f"WH_{workflow_id}_{action}_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"
            
            async with self.db_pool.acquire() as conn:
                await conn.execute("""
                    INSERT INTO refund_workflow_history (
                        history_id, workflow_id, step_name, action,
                        performed_by, comments, metadata
                    ) VALUES ($1, $2, $3, $4, $5, $6, $7)
                """, 
                history_id, workflow_id, step_name, action,
                performed_by, comments, json.dumps(metadata or {})
                )
                
        except Exception as e:
            logger.error(f"Failed to log workflow history: {e}")
            
    async def process_manual_action(
        self,
        workflow_id: str,
        action: WorkflowAction,
        performed_by: str,
        comments: str = ""
    ) -> Dict[str, Any]:
        """Process manual workflow action"""
        try:
            # Get workflow
            async with self.db_pool.acquire() as conn:
                workflow_row = await conn.fetchrow("""
                    SELECT * FROM refund_workflows WHERE workflow_id = $1
                """, workflow_id)
                
            if not workflow_row:
                raise ValueError(f"Workflow not found: {workflow_id}")
                
            # Get current step definition
            template_name = self._select_workflow_template_by_id(workflow_row['request_id'])
            workflow_steps = self.workflow_templates.get(template_name, self.workflow_templates["standard_refund"])
            
            current_step = next(
                (step for step in workflow_steps if step.step_id == workflow_row['current_step']),
                None
            )
            
            if not current_step:
                raise ValueError(f"Current step not found: {workflow_row['current_step']}")
                
            # Validate action is allowed
            if action not in current_step.actions:
                raise ValueError(f"Action {action.value} not allowed for step {current_step.step_id}")
                
            # Log action
            await self._log_workflow_history(
                workflow_id, current_step.name, action.value,
                performed_by, comments
            )
            
            # Create workflow object for advancement
            workflow = RefundWorkflow(
                workflow_id=workflow_row['workflow_id'],
                request_id=workflow_row['request_id'],
                current_step=workflow_row['current_step'],
                status=RefundStatus(workflow_row['status']),
                steps_completed=workflow_row['steps_completed'] or [],
                assigned_to=workflow_row['assigned_to'],
                deadline=workflow_row['deadline'],
                created_at=workflow_row['created_at'],
                updated_at=workflow_row['updated_at']
            )
            
            # Advance workflow
            await self._advance_workflow(workflow, current_step, action)
            
            return {
                "success": True,
                "workflow_id": workflow_id,
                "action": action.value,
                "performed_by": performed_by
            }
            
        except Exception as e:
            logger.error(f"Failed to process manual action: {e}")
            raise
            
    async def get_refund_analytics(
        self,
        start_date: datetime,
        end_date: datetime
    ) -> Dict[str, Any]:
        """Get refund processing analytics"""
        try:
            async with self.db_pool.acquire() as conn:
                # Refund summary
                refund_summary = await conn.fetchrow("""
                    SELECT 
                        COUNT(*) as total_requests,
                        COUNT(*) FILTER (WHERE status = 'completed') as completed,
                        COUNT(*) FILTER (WHERE status = 'rejected') as rejected,
                        SUM(refund_amount) as total_amount,
                        SUM(refund_amount) FILTER (WHERE status = 'completed') as refunded_amount
                    FROM refund_requests 
                    WHERE requested_at BETWEEN $1 AND $2
                """, start_date, end_date)
                
                # Refunds by reason
                refunds_by_reason = await conn.fetch("""
                    SELECT 
                        reason,
                        COUNT(*) as count,
                        SUM(refund_amount) as amount
                    FROM refund_requests 
                    WHERE requested_at BETWEEN $1 AND $2
                    GROUP BY reason
                    ORDER BY count DESC
                """, start_date, end_date)
                
                # Average processing time
                avg_processing_time = await conn.fetchrow("""
                    SELECT AVG(
                        EXTRACT(EPOCH FROM (updated_at - requested_at)) / 3600
                    ) as avg_hours
                    FROM refund_requests 
                    WHERE status IN ('completed', 'rejected')
                    AND requested_at BETWEEN $1 AND $2
                """, start_date, end_date)
                
            return {
                "summary": {
                    "total_requests": refund_summary['total_requests'],
                    "completed": refund_summary['completed'],
                    "rejected": refund_summary['rejected'],
                    "approval_rate": round(
                        (refund_summary['completed'] / refund_summary['total_requests']) * 100, 2
                    ) if refund_summary['total_requests'] > 0 else 0,
                    "total_amount": float(refund_summary['total_amount'] or 0),
                    "refunded_amount": float(refund_summary['refunded_amount'] or 0)
                },
                "refunds_by_reason": [
                    {
                        "reason": row['reason'],
                        "count": row['count'],
                        "amount": float(row['amount'])
                    } for row in refunds_by_reason
                ],
                "performance": {
                    "avg_processing_hours": round(
                        float(avg_processing_time['avg_hours'] or 0), 2
                    )
                },
                "period": {
                    "start_date": start_date.isoformat(),
                    "end_date": end_date.isoformat()
                }
            }
            
        except Exception as e:
            logger.error(f"Failed to get refund analytics: {e}")
            raise