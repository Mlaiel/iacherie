"""Automated Refund Processing with Workflows
Comprehensive refund management system with automated workflows and approval chains.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import logging
import uuid
from typing import Dict, List, Optional, Any, Union, Callable
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from enum import Enum
from decimal import Decimal
import json

logger = logging.getLogger(__name__)


class RefundReason(Enum):
    """Refund request reasons"""
    CUSTOMER_REQUEST = "customer_request"
    DUPLICATE_CHARGE = "duplicate_charge"
    FRAUDULENT_CHARGE = "fraudulent_charge"
    SERVICE_NOT_DELIVERED = "service_not_delivered"
    TECHNICAL_ERROR = "technical_error"
    BILLING_ERROR = "billing_error"
    CHARGEBACK = "chargeback"
    SUBSCRIPTION_CANCELLED = "subscription_cancelled"
    POLICY_VIOLATION = "policy_violation"
    MERCHANT_ERROR = "merchant_error"


class RefundStatus(Enum):
    """Refund processing status"""
    REQUESTED = "requested"
    PENDING_REVIEW = "pending_review"
    UNDER_INVESTIGATION = "under_investigation"
    APPROVED = "approved"
    REJECTED = "rejected"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class RefundType(Enum):
    """Types of refunds"""
    FULL_REFUND = "full_refund"
    PARTIAL_REFUND = "partial_refund"
    PRORATION_REFUND = "proration_refund"
    CREDIT_REFUND = "credit_refund"
    CHARGEBACK_REFUND = "chargeback_refund"


class ApprovalLevel(Enum):
    """Approval levels for refunds"""
    AUTOMATIC = "automatic"
    SUPERVISOR = "supervisor"
    MANAGER = "manager"
    DIRECTOR = "director"
    EXECUTIVE = "executive"


class WorkflowAction(Enum):
    """Workflow actions"""
    APPROVE = "approve"
    REJECT = "reject"
    ESCALATE = "escalate"
    REQUEST_INFO = "request_info"
    INVESTIGATE = "investigate"
    HOLD = "hold"


@dataclass
class RefundRequest:
    """Refund request structure"""
    id: str
    transaction_id: str
    customer_id: str
    original_amount: Decimal
    refund_amount: Decimal
    currency: str
    reason: RefundReason
    refund_type: RefundType
    status: RefundStatus
    description: str
    created_at: datetime
    requested_by: str
    evidence: Optional[Dict[str, Any]] = None
    metadata: Optional[Dict[str, Any]] = None
    processing_notes: Optional[List[str]] = None
    
    def __post_init__(self):
        if self.processing_notes is None:
            self.processing_notes = []


@dataclass
class WorkflowStep:
    """Workflow step configuration"""
    id: str
    name: str
    approval_level: ApprovalLevel
    conditions: Dict[str, Any]
    timeout_hours: int = 24
    auto_approve: bool = False
    escalation_conditions: Optional[Dict[str, Any]] = None


@dataclass
class ApprovalAction:
    """Approval action record"""
    id: str
    refund_id: str
    approver_id: str
    action: WorkflowAction
    level: ApprovalLevel
    timestamp: datetime
    comments: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class RefundWorkflowEngine:
    """Automated refund processing with workflows"""
    
    def __init__(self):
        self.refund_requests: Dict[str, RefundRequest] = {}
        self.approval_actions: Dict[str, List[ApprovalAction]] = {}
        self.workflow_steps = self._initialize_workflow_steps()
        self.auto_approval_rules = self._initialize_auto_approval_rules()
        self.refund_policies = self._initialize_refund_policies()
        self.notification_handlers: List[Callable] = []
    
    def _initialize_workflow_steps(self) -> Dict[str, List[WorkflowStep]]:
        """Initialize refund workflow steps by reason"""
        return {
            "customer_request": [
                WorkflowStep(
                    id="initial_review",
                    name="Initial Review",
                    approval_level=ApprovalLevel.AUTOMATIC,
                    conditions={"amount_threshold": 100.00},
                    auto_approve=True
                ),
                WorkflowStep(
                    id="supervisor_review",
                    name="Supervisor Review",
                    approval_level=ApprovalLevel.SUPERVISOR,
                    conditions={"amount_threshold": 500.00},
                    timeout_hours=4
                ),
                WorkflowStep(
                    id="manager_approval",
                    name="Manager Approval",
                    approval_level=ApprovalLevel.MANAGER,
                    conditions={"amount_threshold": 2000.00},
                    timeout_hours=24
                )
            ],
            "fraudulent_charge": [
                WorkflowStep(
                    id="fraud_investigation",
                    name="Fraud Investigation",
                    approval_level=ApprovalLevel.SUPERVISOR,
                    conditions={},
                    timeout_hours=48
                ),
                WorkflowStep(
                    id="security_review",
                    name="Security Review",
                    approval_level=ApprovalLevel.MANAGER,
                    conditions={"amount_threshold": 1000.00},
                    timeout_hours=72
                )
            ],
            "chargeback": [
                WorkflowStep(
                    id="chargeback_response",
                    name="Chargeback Response",
                    approval_level=ApprovalLevel.MANAGER,
                    conditions={},
                    timeout_hours=168  # 7 days
                )
            ],
            "technical_error": [
                WorkflowStep(
                    id="automatic_approval",
                    name="Automatic Approval",
                    approval_level=ApprovalLevel.AUTOMATIC,
                    conditions={},
                    auto_approve=True
                )
            ]
        }
    
    def _initialize_auto_approval_rules(self) -> Dict[str, Any]:
        """Initialize automatic approval rules"""
        return {
            "max_auto_approve_amount": Decimal("100.00"),
            "customer_account_age_days": 30,
            "max_refunds_per_month": 3,
            "auto_approve_reasons": [
                RefundReason.TECHNICAL_ERROR,
                RefundReason.BILLING_ERROR,
                RefundReason.DUPLICATE_CHARGE
            ],
            "blacklisted_customers": set(),
            "time_limits": {
                "same_day_refund": 24,  # hours
                "standard_refund": 168,  # 7 days
                "extended_refund": 720   # 30 days
            }
        }
    
    def _initialize_refund_policies(self) -> Dict[str, Any]:
        """Initialize refund policies"""
        return {
            "subscription_refund_policy": {
                "trial_period_full_refund": True,
                "prorated_cancellation": True,
                "minimum_usage_days": 3
            },
            "content_protection_policy": {
                "refund_period_days": 30,
                "partial_refund_after_usage": True,
                "no_refund_after_days": 90
            },
            "payment_processing_fees": {
                "deduct_from_refund": True,
                "fee_percentage": Decimal("0.03"),
                "minimum_fee": Decimal("0.30")
            }
        }
    
    async def create_refund_request(
        self,
        transaction_id: str,
        customer_id: str,
        refund_amount: Decimal,
        original_amount: Decimal,
        currency: str,
        reason: RefundReason,
        description: str,
        requested_by: str,
        evidence: Optional[Dict[str, Any]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Create a new refund request"""
        try:
            refund_id = str(uuid.uuid4())
            
            # Determine refund type
            if refund_amount >= original_amount:
                refund_type = RefundType.FULL_REFUND
            elif refund_amount < original_amount:
                refund_type = RefundType.PARTIAL_REFUND
            else:
                refund_type = RefundType.PARTIAL_REFUND
            
            # Validate refund request
            validation_result = await self._validate_refund_request(
                customer_id, refund_amount, original_amount, reason
            )
            
            if not validation_result["valid"]:
                return {
                    "success": False,
                    "error": validation_result["error"],
                    "details": validation_result
                }
            
            refund_request = RefundRequest(
                id=refund_id,
                transaction_id=transaction_id,
                customer_id=customer_id,
                original_amount=original_amount,
                refund_amount=refund_amount,
                currency=currency,
                reason=reason,
                refund_type=refund_type,
                status=RefundStatus.REQUESTED,
                description=description,
                created_at=datetime.now(),
                requested_by=requested_by,
                evidence=evidence,
                metadata=metadata
            )
            
            self.refund_requests[refund_id] = refund_request
            self.approval_actions[refund_id] = []
            
            # Start workflow processing
            workflow_result = await self._start_workflow(refund_request)
            
            # Send notifications
            await self._send_notifications(refund_request, "created")
            
            logger.info(f"Refund request created: {refund_id}")
            return {
                "success": True,
                "refund_id": refund_id,
                "refund_request": asdict(refund_request),
                "workflow_status": workflow_result
            }
            
        except Exception as e:
            logger.error(f"Error creating refund request: {str(e)}")
            return {"success": False, "error": str(e)}
    
    async def process_approval_action(
        self,
        refund_id: str,
        approver_id: str,
        action: WorkflowAction,
        approval_level: ApprovalLevel,
        comments: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Process an approval action"""
        try:
            if refund_id not in self.refund_requests:
                return {"success": False, "error": "Refund request not found"}
            
            refund_request = self.refund_requests[refund_id]
            
            # Create approval action
            action_id = str(uuid.uuid4())
            approval_action = ApprovalAction(
                id=action_id,
                refund_id=refund_id,
                approver_id=approver_id,
                action=action,
                level=approval_level,
                timestamp=datetime.now(),
                comments=comments,
                metadata=metadata
            )
            
            self.approval_actions[refund_id].append(approval_action)
            
            # Update refund status based on action
            if action == WorkflowAction.APPROVE:
                # Check if this is final approval
                if await self._is_final_approval(refund_request, approval_level):
                    refund_request.status = RefundStatus.APPROVED
                    # Process the refund
                    await self._process_approved_refund(refund_request)
                else:
                    # Continue to next approval level
                    await self._escalate_to_next_level(refund_request)
                    
            elif action == WorkflowAction.REJECT:
                refund_request.status = RefundStatus.REJECTED
                refund_request.processing_notes.append(
                    f"Rejected by {approval_level.value}: {comments or 'No reason provided'}"
                )
                
            elif action == WorkflowAction.ESCALATE:
                await self._escalate_to_next_level(refund_request)
                
            elif action == WorkflowAction.REQUEST_INFO:
                refund_request.status = RefundStatus.PENDING_REVIEW
                refund_request.processing_notes.append(
                    f"Additional information requested: {comments or 'No details provided'}"
                )
                
            elif action == WorkflowAction.INVESTIGATE:
                refund_request.status = RefundStatus.UNDER_INVESTIGATION
                refund_request.processing_notes.append(
                    f"Investigation started: {comments or 'No details provided'}"
                )
                
            elif action == WorkflowAction.HOLD:
                refund_request.status = RefundStatus.PENDING_REVIEW
                refund_request.processing_notes.append(
                    f"Request on hold: {comments or 'No reason provided'}"
                )
            
            # Send notifications
            await self._send_notifications(refund_request, f"action_{action.value}")
            
            logger.info(f"Approval action processed: {refund_id} - {action.value}")
            return {
                "success": True,
                "action_id": action_id,
                "refund_status": refund_request.status.value,
                "approval_action": asdict(approval_action)
            }
            
        except Exception as e:
            logger.error(f"Error processing approval action: {str(e)}")
            return {"success": False, "error": str(e)}
    
    async def process_automated_approvals(self) -> Dict[str, Any]:
        """Process all pending automated approvals"""
        try:
            processed_count = 0
            results = []
            
            for refund_request in self.refund_requests.values():
                if refund_request.status == RefundStatus.REQUESTED:
                    # Check if eligible for auto-approval
                    auto_approval_result = await self._check_auto_approval_eligibility(refund_request)
                    
                    if auto_approval_result["eligible"]:
                        # Auto-approve
                        await self.process_approval_action(
                            refund_request.id,
                            "system_auto_approval",
                            WorkflowAction.APPROVE,
                            ApprovalLevel.AUTOMATIC,
                            f"Auto-approved: {auto_approval_result['reason']}"
                        )
                        processed_count += 1
                        results.append({
                            "refund_id": refund_request.id,
                            "action": "auto_approved",
                            "reason": auto_approval_result["reason"]
                        })
            
            logger.info(f"Automated approvals processed: {processed_count}")
            return {
                "success": True,
                "processed": processed_count,
                "results": results
            }
            
        except Exception as e:
            logger.error(f"Error processing automated approvals: {str(e)}")
            return {"success": False, "error": str(e)}
    
    async def process_timeout_escalations(self) -> Dict[str, Any]:
        """Process refunds that have timed out for escalation"""
        try:
            now = datetime.now()
            escalated_count = 0
            results = []
            
            for refund_request in self.refund_requests.values():
                if refund_request.status in [RefundStatus.PENDING_REVIEW, RefundStatus.UNDER_INVESTIGATION]:
                    # Check if timeout exceeded
                    last_action_time = refund_request.created_at
                    if self.approval_actions.get(refund_request.id):
                        last_action_time = max(
                            action.timestamp for action in self.approval_actions[refund_request.id]
                        )
                    
                    # Get current workflow step timeout
                    workflow_steps = self.workflow_steps.get(refund_request.reason.value, [])
                    current_step = self._get_current_workflow_step(refund_request, workflow_steps)
                    
                    if current_step:
                        timeout_threshold = last_action_time + timedelta(hours=current_step.timeout_hours)
                        
                        if now > timeout_threshold:
                            # Escalate due to timeout
                            await self._escalate_to_next_level(refund_request)
                            escalated_count += 1
                            results.append({
                                "refund_id": refund_request.id,
                                "action": "timeout_escalated",
                                "timeout_hours": current_step.timeout_hours
                            })
            
            logger.info(f"Timeout escalations processed: {escalated_count}")
            return {
                "success": True,
                "escalated": escalated_count,
                "results": results
            }
            
        except Exception as e:
            logger.error(f"Error processing timeout escalations: {str(e)}")
            return {"success": False, "error": str(e)}
    
    async def _validate_refund_request(
        self,
        customer_id: str,
        refund_amount: Decimal,
        original_amount: Decimal,
        reason: RefundReason
    ) -> Dict[str, Any]:
        """Validate refund request against policies"""
        try:
            # Check refund amount
            if refund_amount <= 0:
                return {"valid": False, "error": "Refund amount must be positive"}
            
            if refund_amount > original_amount:
                return {"valid": False, "error": "Refund amount cannot exceed original amount"}
            
            # Check customer blacklist
            if customer_id in self.auto_approval_rules["blacklisted_customers"]:
                return {"valid": False, "error": "Customer is blacklisted for refunds"}
            
            # Check refund frequency
            recent_refunds = await self._get_customer_recent_refunds(customer_id)
            max_refunds = self.auto_approval_rules["max_refunds_per_month"]
            
            if len(recent_refunds) >= max_refunds:
                return {
                    "valid": False,
                    "error": f"Customer has exceeded maximum refunds per month ({max_refunds})"
                }
            
            return {"valid": True}
            
        except Exception as e:
            logger.error(f"Error validating refund request: {str(e)}")
            return {"valid": False, "error": str(e)}
    
    async def _start_workflow(self, refund_request: RefundRequest) -> Dict[str, Any]:
        """Start the appropriate workflow for the refund"""
        try:
            reason_key = refund_request.reason.value
            workflow_steps = self.workflow_steps.get(reason_key, [])
            
            if not workflow_steps:
                # Default workflow
                workflow_steps = self.workflow_steps["customer_request"]
            
            first_step = workflow_steps[0]
            
            if first_step.auto_approve:
                # Check auto-approval eligibility
                auto_approval_result = await self._check_auto_approval_eligibility(refund_request)
                
                if auto_approval_result["eligible"]:
                    refund_request.status = RefundStatus.APPROVED
                    await self._process_approved_refund(refund_request)
                    return {"status": "auto_approved", "reason": auto_approval_result["reason"]}
            
            # Set status for manual review
            refund_request.status = RefundStatus.PENDING_REVIEW
            return {"status": "pending_review", "workflow": reason_key}
            
        except Exception as e:
            logger.error(f"Error starting workflow: {str(e)}")
            return {"status": "error", "error": str(e)}
    
    async def _check_auto_approval_eligibility(self, refund_request: RefundRequest) -> Dict[str, Any]:
        """Check if refund is eligible for auto-approval"""
        try:
            rules = self.auto_approval_rules
            
            # Check amount threshold
            if refund_request.refund_amount > rules["max_auto_approve_amount"]:
                return {"eligible": False, "reason": "Amount exceeds auto-approval threshold"}
            
            # Check reason
            if refund_request.reason not in rules["auto_approve_reasons"]:
                return {"eligible": False, "reason": "Reason not eligible for auto-approval"}
            
            # Check customer history
            recent_refunds = await self._get_customer_recent_refunds(refund_request.customer_id)
            if len(recent_refunds) >= 2:  # More than 1 recent refund
                return {"eligible": False, "reason": "Customer has recent refunds"}
            
            # Check time since transaction
            time_since_transaction = datetime.now() - refund_request.created_at
            if time_since_transaction.total_seconds() / 3600 > rules["time_limits"]["same_day_refund"]:
                return {"eligible": False, "reason": "Request not made within same-day window"}
            
            return {"eligible": True, "reason": "Meets all auto-approval criteria"}
            
        except Exception as e:
            logger.error(f"Error checking auto-approval eligibility: {str(e)}")
            return {"eligible": False, "reason": f"Error: {str(e)}"}
    
    async def _process_approved_refund(self, refund_request: RefundRequest):
        """Process an approved refund"""
        try:
            refund_request.status = RefundStatus.PROCESSING
            
            # Calculate processing fees
            fees = self._calculate_processing_fees(refund_request.refund_amount)
            net_refund_amount = refund_request.refund_amount - fees
            
            # In production, this would integrate with payment processor
            # For now, simulate processing
            await asyncio.sleep(0.1)  # Simulate processing delay
            
            # Simulate success (95% success rate)
            import random
            if random.random() < 0.95:
                refund_request.status = RefundStatus.COMPLETED
                refund_request.processing_notes.append(
                    f"Refund processed successfully. Net amount: {net_refund_amount}, Fees: {fees}"
                )
                logger.info(f"Refund processed successfully: {refund_request.id}")
            else:
                refund_request.status = RefundStatus.FAILED
                refund_request.processing_notes.append("Refund processing failed - payment processor error")
                logger.error(f"Refund processing failed: {refund_request.id}")
            
            # Send notifications
            await self._send_notifications(refund_request, "processed")
            
        except Exception as e:
            logger.error(f"Error processing approved refund: {str(e)}")
            refund_request.status = RefundStatus.FAILED
            refund_request.processing_notes.append(f"Processing error: {str(e)}")
    
    async def _escalate_to_next_level(self, refund_request: RefundRequest):
        """Escalate refund to next approval level"""
        try:
            reason_key = refund_request.reason.value
            workflow_steps = self.workflow_steps.get(reason_key, self.workflow_steps["customer_request"])
            
            current_step = self._get_current_workflow_step(refund_request, workflow_steps)
            next_step_index = workflow_steps.index(current_step) + 1 if current_step else 0
            
            if next_step_index < len(workflow_steps):
                next_step = workflow_steps[next_step_index]
                refund_request.processing_notes.append(
                    f"Escalated to {next_step.approval_level.value} level"
                )
                logger.info(f"Refund escalated: {refund_request.id} -> {next_step.approval_level.value}")
            else:
                # No more escalation levels - requires executive approval
                refund_request.processing_notes.append("Escalated to executive level - maximum escalation reached")
                logger.info(f"Refund reached maximum escalation: {refund_request.id}")
            
        except Exception as e:
            logger.error(f"Error escalating refund: {str(e)}")
    
    async def _is_final_approval(self, refund_request: RefundRequest, approval_level: ApprovalLevel) -> bool:
        """Check if this is the final approval needed"""
        try:
            reason_key = refund_request.reason.value
            workflow_steps = self.workflow_steps.get(reason_key, self.workflow_steps["customer_request"])
            
            # Find the highest required approval level
            required_levels = []
            for step in workflow_steps:
                if self._step_conditions_met(refund_request, step):
                    required_levels.append(step.approval_level)
            
            if not required_levels:
                return True  # No specific levels required
            
            highest_required = max(required_levels, key=lambda x: self._get_approval_level_rank(x))
            current_rank = self._get_approval_level_rank(approval_level)
            required_rank = self._get_approval_level_rank(highest_required)
            
            return current_rank >= required_rank
            
        except Exception as e:
            logger.error(f"Error checking final approval: {str(e)}")
            return False
    
    def _step_conditions_met(self, refund_request: RefundRequest, step: WorkflowStep) -> bool:
        """Check if workflow step conditions are met"""
        conditions = step.conditions
        
        if "amount_threshold" in conditions:
            if refund_request.refund_amount >= Decimal(str(conditions["amount_threshold"])):
                return True
        
        return len(conditions) == 0  # No conditions means always applicable
    
    def _get_approval_level_rank(self, level: ApprovalLevel) -> int:
        """Get numeric rank for approval level"""
        ranks = {
            ApprovalLevel.AUTOMATIC: 1,
            ApprovalLevel.SUPERVISOR: 2,
            ApprovalLevel.MANAGER: 3,
            ApprovalLevel.DIRECTOR: 4,
            ApprovalLevel.EXECUTIVE: 5
        }
        return ranks.get(level, 0)
    
    def _get_current_workflow_step(
        self,
        refund_request: RefundRequest,
        workflow_steps: List[WorkflowStep]
    ) -> Optional[WorkflowStep]:
        """Get current workflow step for refund"""
        # Find applicable steps based on conditions
        applicable_steps = [
            step for step in workflow_steps
            if self._step_conditions_met(refund_request, step)
        ]
        
        if applicable_steps:
            return applicable_steps[0]  # Return first applicable step
        
        return None
    
    def _calculate_processing_fees(self, refund_amount: Decimal) -> Decimal:
        """Calculate processing fees for refund"""
        try:
            fee_config = self.refund_policies["payment_processing_fees"]
            
            if not fee_config["deduct_from_refund"]:
                return Decimal("0.00")
            
            percentage_fee = refund_amount * fee_config["fee_percentage"]
            total_fee = percentage_fee + fee_config["minimum_fee"]
            
            # Cap fee at 10% of refund amount
            max_fee = refund_amount * Decimal("0.1")
            return min(total_fee, max_fee)
            
        except Exception as e:
            logger.error(f"Error calculating processing fees: {str(e)}")
            return Decimal("0.00")
    
    async def _get_customer_recent_refunds(self, customer_id: str) -> List[RefundRequest]:
        """Get customer's recent refunds (last 30 days)"""
        try:
            thirty_days_ago = datetime.now() - timedelta(days=30)
            
            recent_refunds = [
                refund for refund in self.refund_requests.values()
                if (refund.customer_id == customer_id and
                    refund.created_at >= thirty_days_ago and
                    refund.status in [RefundStatus.COMPLETED, RefundStatus.APPROVED])
            ]
            
            return recent_refunds
            
        except Exception as e:
            logger.error(f"Error getting customer recent refunds: {str(e)}")
            return []
    
    async def _send_notifications(self, refund_request: RefundRequest, event_type: str):
        """Send notifications for refund events"""
        try:
            for handler in self.notification_handlers:
                await handler(refund_request, event_type)
                
        except Exception as e:
            logger.error(f"Error sending notifications: {str(e)}")
    
    def add_notification_handler(self, handler: Callable):
        """Add notification handler"""
        self.notification_handlers.append(handler)
    
    async def get_refund_status(self, refund_id: str) -> Dict[str, Any]:
        """Get detailed refund status"""
        try:
            if refund_id not in self.refund_requests:
                return {"success": False, "error": "Refund request not found"}
            
            refund_request = self.refund_requests[refund_id]
            approval_actions = self.approval_actions.get(refund_id, [])
            
            return {
                "success": True,
                "refund_request": asdict(refund_request),
                "approval_actions": [asdict(action) for action in approval_actions],
                "workflow_status": await self._get_workflow_status(refund_request)
            }
            
        except Exception as e:
            logger.error(f"Error getting refund status: {str(e)}")
            return {"success": False, "error": str(e)}
    
    async def _get_workflow_status(self, refund_request: RefundRequest) -> Dict[str, Any]:
        """Get current workflow status"""
        try:
            reason_key = refund_request.reason.value
            workflow_steps = self.workflow_steps.get(reason_key, [])
            current_step = self._get_current_workflow_step(refund_request, workflow_steps)
            
            return {
                "current_step": current_step.name if current_step else "Unknown",
                "approval_level": current_step.approval_level.value if current_step else "Unknown",
                "timeout_hours": current_step.timeout_hours if current_step else 0,
                "workflow_reason": reason_key
            }
            
        except Exception as e:
            logger.error(f"Error getting workflow status: {str(e)}")
            return {"error": str(e)}
    
    async def get_refund_analytics(self) -> Dict[str, Any]:
        """Get refund processing analytics"""
        try:
            total_refunds = len(self.refund_requests)
            
            status_counts = {}
            for status in RefundStatus:
                status_counts[status.value] = sum(
                    1 for r in self.refund_requests.values() if r.status == status
                )
            
            reason_counts = {}
            for reason in RefundReason:
                reason_counts[reason.value] = sum(
                    1 for r in self.refund_requests.values() if r.reason == reason
                )
            
            # Calculate average processing time
            completed_refunds = [
                r for r in self.refund_requests.values() 
                if r.status == RefundStatus.COMPLETED
            ]
            
            avg_processing_time = 0
            if completed_refunds:
                total_processing_time = sum(
                    (datetime.now() - r.created_at).total_seconds() / 3600
                    for r in completed_refunds
                )
                avg_processing_time = total_processing_time / len(completed_refunds)
            
            return {
                "success": True,
                "analytics": {
                    "total_refunds": total_refunds,
                    "status_breakdown": status_counts,
                    "reason_breakdown": reason_counts,
                    "average_processing_time_hours": round(avg_processing_time, 2),
                    "total_refund_amount": float(sum(
                        r.refund_amount for r in self.refund_requests.values()
                    )),
                    "auto_approval_rate": round(
                        status_counts.get("completed", 0) / max(total_refunds, 1) * 100, 2
                    )
                }
            }
            
        except Exception as e:
            logger.error(f"Error getting refund analytics: {str(e)}")
            return {"success": False, "error": str(e)}