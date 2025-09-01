"""Dunning Management for Failed Payments
Automated dunning process to recover failed payments with intelligent retry strategies.

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


class PaymentFailureReason(Enum):
    """Payment failure reasons"""
    INSUFFICIENT_FUNDS = "insufficient_funds"
    CARD_DECLINED = "card_declined"
    EXPIRED_CARD = "expired_card"
    INVALID_CARD = "invalid_card"
    PROCESSING_ERROR = "processing_error"
    FRAUD_DETECTED = "fraud_detected"
    BLOCKED_TRANSACTION = "blocked_transaction"
    AUTHENTICATION_FAILED = "authentication_failed"
    LIMIT_EXCEEDED = "limit_exceeded"
    UNKNOWN_ERROR = "unknown_error"


class DunningStatus(Enum):
    """Dunning process status"""
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"
    ABANDONED = "abandoned"
    MANUAL_REVIEW = "manual_review"


class NotificationType(Enum):
    """Types of dunning notifications"""
    EMAIL = "email"
    SMS = "sms"
    PUSH_NOTIFICATION = "push_notification"
    IN_APP = "in_app"
    PHONE_CALL = "phone_call"


class DunningAction(Enum):
    """Actions to take during dunning"""
    RETRY_PAYMENT = "retry_payment"
    SEND_NOTIFICATION = "send_notification"
    UPDATE_PAYMENT_METHOD = "update_payment_method"
    SUSPEND_SERVICE = "suspend_service"
    CANCEL_SUBSCRIPTION = "cancel_subscription"
    ESCALATE_TO_HUMAN = "escalate_to_human"
    OFFER_DISCOUNT = "offer_discount"
    PAUSE_DUNNING = "pause_dunning"


@dataclass
class FailedPayment:
    """Failed payment record"""
    id: str
    subscription_id: str
    customer_id: str
    amount: Decimal
    currency: str
    failure_reason: PaymentFailureReason
    failure_date: datetime
    attempt_count: int = 0
    last_retry_date: Optional[datetime] = None
    payment_method_id: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


@dataclass
class DunningStep:
    """Individual step in dunning sequence"""
    id: str
    sequence_number: int
    delay_days: int
    action: DunningAction
    notification_types: List[NotificationType]
    retry_payment: bool = False
    offer_incentive: bool = False
    incentive_percentage: Decimal = Decimal("0.00")
    escalation_trigger: bool = False
    max_attempts: int = 1


@dataclass
class DunningSequence:
    """Complete dunning sequence configuration"""
    id: str
    name: str
    steps: List[DunningStep]
    max_total_attempts: int = 10
    abandon_after_days: int = 30
    pause_on_holidays: bool = True
    respect_customer_timezone: bool = True


@dataclass
class DunningProcess:
    """Active dunning process"""
    id: str
    failed_payment_id: str
    sequence_id: str
    customer_id: str
    current_step: int = 0
    status: DunningStatus = DunningStatus.ACTIVE
    started_at: datetime = None
    last_action_at: Optional[datetime] = None
    paused_until: Optional[datetime] = None
    total_attempts: int = 0
    notifications_sent: int = 0
    metadata: Optional[Dict[str, Any]] = None
    
    def __post_init__(self):
        if self.started_at is None:
            self.started_at = datetime.now()


@dataclass
class DunningAction:
    """Dunning action taken"""
    id: str
    process_id: str
    step_id: str
    action_type: DunningAction
    executed_at: datetime
    success: bool
    details: Dict[str, Any]
    next_action_scheduled: Optional[datetime] = None


class DunningManager:
    """Automated dunning management system"""
    
    def __init__(self):
        self.failed_payments: Dict[str, FailedPayment] = {}
        self.dunning_processes: Dict[str, DunningProcess] = {}
        self.dunning_sequences = self._initialize_dunning_sequences()
        self.dunning_actions: Dict[str, List[DunningAction]] = {}
        self.notification_handlers: Dict[NotificationType, Callable] = {}
        self.payment_retry_handler: Optional[Callable] = None
        self.customer_preferences: Dict[str, Dict[str, Any]] = {}
    
    def _initialize_dunning_sequences(self) -> Dict[str, DunningSequence]:
        """Initialize default dunning sequences"""
        sequences = {}
        
        # Standard dunning sequence
        sequences["standard"] = DunningSequence(
            id="standard",
            name="Standard Dunning Sequence",
            steps=[
                DunningStep(
                    id="immediate_retry",
                    sequence_number=1,
                    delay_days=0,
                    action=DunningAction.RETRY_PAYMENT,
                    notification_types=[],
                    retry_payment=True,
                    max_attempts=1
                ),
                DunningStep(
                    id="day_1_notification",
                    sequence_number=2,
                    delay_days=1,
                    action=DunningAction.SEND_NOTIFICATION,
                    notification_types=[NotificationType.EMAIL],
                    retry_payment=True,
                    max_attempts=1
                ),
                DunningStep(
                    id="day_3_reminder",
                    sequence_number=3,
                    delay_days=3,
                    action=DunningAction.SEND_NOTIFICATION,
                    notification_types=[NotificationType.EMAIL, NotificationType.PUSH_NOTIFICATION],
                    retry_payment=True,
                    max_attempts=1
                ),
                DunningStep(
                    id="day_7_final_notice",
                    sequence_number=4,
                    delay_days=7,
                    action=DunningAction.SEND_NOTIFICATION,
                    notification_types=[NotificationType.EMAIL, NotificationType.SMS],
                    retry_payment=True,
                    offer_incentive=True,
                    incentive_percentage=Decimal("10.00"),
                    max_attempts=1
                ),
                DunningStep(
                    id="day_14_suspend",
                    sequence_number=5,
                    delay_days=14,
                    action=DunningAction.SUSPEND_SERVICE,
                    notification_types=[NotificationType.EMAIL],
                    max_attempts=1
                ),
                DunningStep(
                    id="day_30_cancel",
                    sequence_number=6,
                    delay_days=30,
                    action=DunningAction.CANCEL_SUBSCRIPTION,
                    notification_types=[NotificationType.EMAIL, NotificationType.SMS],
                    max_attempts=1
                )
            ],
            max_total_attempts=6,
            abandon_after_days=30
        )
        
        # High-value customer sequence (more gentle)
        sequences["high_value"] = DunningSequence(
            id="high_value",
            name="High-Value Customer Dunning",
            steps=[
                DunningStep(
                    id="immediate_retry",
                    sequence_number=1,
                    delay_days=0,
                    action=DunningAction.RETRY_PAYMENT,
                    notification_types=[],
                    retry_payment=True,
                    max_attempts=2
                ),
                DunningStep(
                    id="day_1_personal_email",
                    sequence_number=2,
                    delay_days=1,
                    action=DunningAction.SEND_NOTIFICATION,
                    notification_types=[NotificationType.EMAIL],
                    retry_payment=True,
                    max_attempts=1
                ),
                DunningStep(
                    id="day_5_offer_help",
                    sequence_number=3,
                    delay_days=5,
                    action=DunningAction.SEND_NOTIFICATION,
                    notification_types=[NotificationType.EMAIL, NotificationType.PHONE_CALL],
                    retry_payment=True,
                    offer_incentive=True,
                    incentive_percentage=Decimal("15.00"),
                    max_attempts=1
                ),
                DunningStep(
                    id="day_10_manual_review",
                    sequence_number=4,
                    delay_days=10,
                    action=DunningAction.ESCALATE_TO_HUMAN,
                    notification_types=[NotificationType.EMAIL],
                    escalation_trigger=True,
                    max_attempts=1
                )
            ],
            max_total_attempts=5,
            abandon_after_days=45
        )
        
        # Low-value customer sequence (faster)
        sequences["low_value"] = DunningSequence(
            id="low_value",
            name="Low-Value Customer Dunning",
            steps=[
                DunningStep(
                    id="immediate_retry",
                    sequence_number=1,
                    delay_days=0,
                    action=DunningAction.RETRY_PAYMENT,
                    notification_types=[],
                    retry_payment=True,
                    max_attempts=1
                ),
                DunningStep(
                    id="day_2_notification",
                    sequence_number=2,
                    delay_days=2,
                    action=DunningAction.SEND_NOTIFICATION,
                    notification_types=[NotificationType.EMAIL],
                    retry_payment=True,
                    max_attempts=1
                ),
                DunningStep(
                    id="day_7_suspend",
                    sequence_number=3,
                    delay_days=7,
                    action=DunningAction.SUSPEND_SERVICE,
                    notification_types=[NotificationType.EMAIL],
                    max_attempts=1
                ),
                DunningStep(
                    id="day_14_cancel",
                    sequence_number=4,
                    delay_days=14,
                    action=DunningAction.CANCEL_SUBSCRIPTION,
                    notification_types=[NotificationType.EMAIL],
                    max_attempts=1
                )
            ],
            max_total_attempts=4,
            abandon_after_days=14
        )
        
        return sequences
    
    async def register_failed_payment(
        self,
        subscription_id: str,
        customer_id: str,
        amount: Decimal,
        currency: str,
        failure_reason: PaymentFailureReason,
        payment_method_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Register a failed payment and start dunning process"""
        try:
            failed_payment_id = str(uuid.uuid4())
            
            failed_payment = FailedPayment(
                id=failed_payment_id,
                subscription_id=subscription_id,
                customer_id=customer_id,
                amount=amount,
                currency=currency,
                failure_reason=failure_reason,
                failure_date=datetime.now(),
                payment_method_id=payment_method_id,
                metadata=metadata
            )
            
            self.failed_payments[failed_payment_id] = failed_payment
            
            # Determine appropriate dunning sequence
            sequence_id = await self._determine_dunning_sequence(customer_id, amount)
            
            # Start dunning process
            dunning_result = await self._start_dunning_process(failed_payment, sequence_id)
            
            logger.info(f"Failed payment registered and dunning started: {failed_payment_id}")
            return {
                "success": True,
                "failed_payment_id": failed_payment_id,
                "dunning_process_id": dunning_result.get("process_id"),
                "sequence_id": sequence_id
            }
            
        except Exception as e:
            logger.error(f"Error registering failed payment: {str(e)}")
            return {"success": False, "error": str(e)}
    
    async def process_dunning_actions(self) -> Dict[str, Any]:
        """Process all pending dunning actions"""
        try:
            now = datetime.now()
            processed_count = 0
            results = []
            
            for process in self.dunning_processes.values():
                if process.status != DunningStatus.ACTIVE:
                    continue
                
                # Check if paused
                if process.paused_until and now < process.paused_until:
                    continue
                
                # Get current sequence and step
                sequence = self.dunning_sequences.get(process.sequence_id)
                if not sequence or process.current_step >= len(sequence.steps):
                    continue
                
                current_step = sequence.steps[process.current_step]
                
                # Check if it's time to execute this step
                if await self._should_execute_step(process, current_step, now):
                    result = await self._execute_dunning_step(process, current_step)
                    processed_count += 1
                    results.append({
                        "process_id": process.id,
                        "step": current_step.id,
                        "result": result
                    })
                    
                    # Move to next step if successful
                    if result.get("success"):
                        await self._advance_to_next_step(process, sequence)
            
            logger.info(f"Dunning actions processed: {processed_count}")
            return {
                "success": True,
                "processed": processed_count,
                "results": results
            }
            
        except Exception as e:
            logger.error(f"Error processing dunning actions: {str(e)}")
            return {"success": False, "error": str(e)}
    
    async def retry_failed_payment(self, failed_payment_id: str) -> Dict[str, Any]:
        """Manually retry a failed payment"""
        try:
            if failed_payment_id not in self.failed_payments:
                return {"success": False, "error": "Failed payment not found"}
            
            failed_payment = self.failed_payments[failed_payment_id]
            
            # Attempt payment retry
            if self.payment_retry_handler:
                retry_result = await self.payment_retry_handler(failed_payment)
                
                if retry_result.get("success"):
                    # Payment succeeded - complete dunning process
                    await self._complete_dunning_process(failed_payment_id, "payment_recovered")
                    
                    logger.info(f"Failed payment recovered: {failed_payment_id}")
                    return {
                        "success": True,
                        "message": "Payment recovered successfully",
                        "transaction_id": retry_result.get("transaction_id")
                    }
                else:
                    # Payment failed again - update attempt count
                    failed_payment.attempt_count += 1
                    failed_payment.last_retry_date = datetime.now()
                    
                    return {
                        "success": False,
                        "message": "Payment retry failed",
                        "error": retry_result.get("error")
                    }
            else:
                return {"success": False, "error": "Payment retry handler not configured"}
                
        except Exception as e:
            logger.error(f"Error retrying failed payment: {str(e)}")
            return {"success": False, "error": str(e)}
    
    async def pause_dunning_process(
        self,
        process_id: str,
        pause_days: int,
        reason: str
    ) -> Dict[str, Any]:
        """Pause a dunning process"""
        try:
            if process_id not in self.dunning_processes:
                return {"success": False, "error": "Dunning process not found"}
            
            process = self.dunning_processes[process_id]
            process.status = DunningStatus.PAUSED
            process.paused_until = datetime.now() + timedelta(days=pause_days)
            
            if not process.metadata:
                process.metadata = {}
            process.metadata["pause_reason"] = reason
            process.metadata["paused_at"] = datetime.now().isoformat()
            
            logger.info(f"Dunning process paused: {process_id} for {pause_days} days")
            return {
                "success": True,
                "message": f"Dunning process paused for {pause_days} days",
                "paused_until": process.paused_until.isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error pausing dunning process: {str(e)}")
            return {"success": False, "error": str(e)}
    
    async def update_customer_payment_method(
        self,
        customer_id: str,
        new_payment_method_id: str
    ) -> Dict[str, Any]:
        """Update customer's payment method and retry failed payments"""
        try:
            updated_count = 0
            results = []
            
            # Find all failed payments for this customer
            customer_failed_payments = [
                fp for fp in self.failed_payments.values()
                if fp.customer_id == customer_id
            ]
            
            for failed_payment in customer_failed_payments:
                # Update payment method
                failed_payment.payment_method_id = new_payment_method_id
                
                # Retry payment
                retry_result = await self.retry_failed_payment(failed_payment.id)
                updated_count += 1
                results.append({
                    "failed_payment_id": failed_payment.id,
                    "retry_result": retry_result
                })
            
            logger.info(f"Payment method updated for customer {customer_id}, {updated_count} payments retried")
            return {
                "success": True,
                "updated_payments": updated_count,
                "results": results
            }
            
        except Exception as e:
            logger.error(f"Error updating customer payment method: {str(e)}")
            return {"success": False, "error": str(e)}
    
    async def _determine_dunning_sequence(self, customer_id: str, amount: Decimal) -> str:
        """Determine appropriate dunning sequence for customer"""
        try:
            # Get customer preferences if available
            customer_prefs = self.customer_preferences.get(customer_id, {})
            
            # Check for explicit sequence preference
            if "dunning_sequence" in customer_prefs:
                return customer_prefs["dunning_sequence"]
            
            # Determine based on customer value
            customer_value = customer_prefs.get("lifetime_value", 0)
            
            if customer_value >= 1000 or amount >= 100:
                return "high_value"
            elif amount <= 20:
                return "low_value"
            else:
                return "standard"
                
        except Exception as e:
            logger.error(f"Error determining dunning sequence: {str(e)}")
            return "standard"
    
    async def _start_dunning_process(
        self,
        failed_payment: FailedPayment,
        sequence_id: str
    ) -> Dict[str, Any]:
        """Start dunning process for failed payment"""
        try:
            process_id = str(uuid.uuid4())
            
            dunning_process = DunningProcess(
                id=process_id,
                failed_payment_id=failed_payment.id,
                sequence_id=sequence_id,
                customer_id=failed_payment.customer_id,
                metadata={
                    "original_amount": float(failed_payment.amount),
                    "failure_reason": failed_payment.failure_reason.value
                }
            )
            
            self.dunning_processes[process_id] = dunning_process
            self.dunning_actions[process_id] = []
            
            logger.info(f"Dunning process started: {process_id} with sequence {sequence_id}")
            return {"success": True, "process_id": process_id}
            
        except Exception as e:
            logger.error(f"Error starting dunning process: {str(e)}")
            return {"success": False, "error": str(e)}
    
    async def _should_execute_step(
        self,
        process: DunningProcess,
        step: DunningStep,
        current_time: datetime
    ) -> bool:
        """Check if dunning step should be executed"""
        try:
            # Check if step has already been executed
            process_actions = self.dunning_actions.get(process.id, [])
            step_executed = any(action.step_id == step.id for action in process_actions)
            
            if step_executed:
                return False
            
            # Check if enough time has passed
            execution_time = process.started_at + timedelta(days=step.delay_days)
            
            if current_time < execution_time:
                return False
            
            # Check for holidays if configured
            sequence = self.dunning_sequences.get(process.sequence_id)
            if sequence and sequence.pause_on_holidays:
                if await self._is_holiday(current_time):
                    return False
            
            # Check customer timezone if configured
            if sequence and sequence.respect_customer_timezone:
                customer_tz_hour = await self._get_customer_timezone_hour(process.customer_id)
                # Don't execute during night hours (10 PM - 8 AM)
                if customer_tz_hour < 8 or customer_tz_hour >= 22:
                    return False
            
            return True
            
        except Exception as e:
            logger.error(f"Error checking step execution: {str(e)}")
            return False
    
    async def _execute_dunning_step(
        self,
        process: DunningProcess,
        step: DunningStep
    ) -> Dict[str, Any]:
        """Execute a dunning step"""
        try:
            action_id = str(uuid.uuid4())
            execution_details = {}
            success = True
            
            # Execute based on action type
            if step.action == DunningAction.RETRY_PAYMENT:
                result = await self._execute_payment_retry(process, step)
                execution_details.update(result)
                success = result.get("success", False)
                
            elif step.action == DunningAction.SEND_NOTIFICATION:
                result = await self._execute_send_notifications(process, step)
                execution_details.update(result)
                success = result.get("success", False)
                
            elif step.action == DunningAction.SUSPEND_SERVICE:
                result = await self._execute_suspend_service(process, step)
                execution_details.update(result)
                success = result.get("success", False)
                
            elif step.action == DunningAction.CANCEL_SUBSCRIPTION:
                result = await self._execute_cancel_subscription(process, step)
                execution_details.update(result)
                success = result.get("success", False)
                
            elif step.action == DunningAction.ESCALATE_TO_HUMAN:
                result = await self._execute_escalate_to_human(process, step)
                execution_details.update(result)
                success = result.get("success", False)
            
            # Record the action
            dunning_action = DunningAction(
                id=action_id,
                process_id=process.id,
                step_id=step.id,
                action_type=step.action,
                executed_at=datetime.now(),
                success=success,
                details=execution_details
            )
            
            self.dunning_actions[process.id].append(dunning_action)
            
            # Update process
            process.last_action_at = datetime.now()
            process.total_attempts += 1
            
            if step.notification_types:
                process.notifications_sent += len(step.notification_types)
            
            logger.info(f"Dunning step executed: {process.id} - {step.id}")
            return {"success": success, "action_id": action_id, "details": execution_details}
            
        except Exception as e:
            logger.error(f"Error executing dunning step: {str(e)}")
            return {"success": False, "error": str(e)}
    
    async def _execute_payment_retry(
        self,
        process: DunningProcess,
        step: DunningStep
    ) -> Dict[str, Any]:
        """Execute payment retry"""
        try:
            failed_payment = self.failed_payments[process.failed_payment_id]
            
            if self.payment_retry_handler:
                retry_result = await self.payment_retry_handler(failed_payment)
                
                if retry_result.get("success"):
                    # Payment recovered
                    await self._complete_dunning_process(process.failed_payment_id, "payment_recovered")
                    return {
                        "success": True,
                        "payment_recovered": True,
                        "transaction_id": retry_result.get("transaction_id")
                    }
                else:
                    return {
                        "success": False,
                        "payment_recovered": False,
                        "error": retry_result.get("error")
                    }
            else:
                return {"success": False, "error": "Payment retry handler not configured"}
                
        except Exception as e:
            logger.error(f"Error executing payment retry: {str(e)}")
            return {"success": False, "error": str(e)}
    
    async def _execute_send_notifications(
        self,
        process: DunningProcess,
        step: DunningStep
    ) -> Dict[str, Any]:
        """Execute notification sending"""
        try:
            notifications_sent = []
            
            for notification_type in step.notification_types:
                if notification_type in self.notification_handlers:
                    handler = self.notification_handlers[notification_type]
                    
                    # Prepare notification data
                    notification_data = {
                        "process_id": process.id,
                        "customer_id": process.customer_id,
                        "step": step,
                        "failed_payment": self.failed_payments[process.failed_payment_id],
                        "offer_incentive": step.offer_incentive,
                        "incentive_percentage": float(step.incentive_percentage)
                    }
                    
                    try:
                        result = await handler(notification_data)
                        notifications_sent.append({
                            "type": notification_type.value,
                            "success": result.get("success", False),
                            "details": result
                        })
                    except Exception as e:
                        notifications_sent.append({
                            "type": notification_type.value,
                            "success": False,
                            "error": str(e)
                        })
            
            success = any(n["success"] for n in notifications_sent)
            
            return {
                "success": success,
                "notifications_sent": notifications_sent,
                "total_sent": len([n for n in notifications_sent if n["success"]])
            }
            
        except Exception as e:
            logger.error(f"Error executing send notifications: {str(e)}")
            return {"success": False, "error": str(e)}
    
    async def _execute_suspend_service(
        self,
        process: DunningProcess,
        step: DunningStep
    ) -> Dict[str, Any]:
        """Execute service suspension"""
        try:
            # In production, this would integrate with subscription management
            # For now, just log the action
            
            logger.info(f"Service suspended for customer {process.customer_id}")
            
            return {
                "success": True,
                "action": "service_suspended",
                "customer_id": process.customer_id
            }
            
        except Exception as e:
            logger.error(f"Error executing suspend service: {str(e)}")
            return {"success": False, "error": str(e)}
    
    async def _execute_cancel_subscription(
        self,
        process: DunningProcess,
        step: DunningStep
    ) -> Dict[str, Any]:
        """Execute subscription cancellation"""
        try:
            # In production, this would integrate with subscription management
            # Mark dunning process as completed
            process.status = DunningStatus.COMPLETED
            
            logger.info(f"Subscription cancelled for customer {process.customer_id}")
            
            return {
                "success": True,
                "action": "subscription_cancelled",
                "customer_id": process.customer_id
            }
            
        except Exception as e:
            logger.error(f"Error executing cancel subscription: {str(e)}")
            return {"success": False, "error": str(e)}
    
    async def _execute_escalate_to_human(
        self,
        process: DunningProcess,
        step: DunningStep
    ) -> Dict[str, Any]:
        """Execute escalation to human review"""
        try:
            process.status = DunningStatus.MANUAL_REVIEW
            
            # In production, this would create a ticket or alert for human review
            
            logger.info(f"Dunning process escalated to human review: {process.id}")
            
            return {
                "success": True,
                "action": "escalated_to_human",
                "process_id": process.id
            }
            
        except Exception as e:
            logger.error(f"Error executing escalate to human: {str(e)}")
            return {"success": False, "error": str(e)}
    
    async def _advance_to_next_step(
        self,
        process: DunningProcess,
        sequence: DunningSequence
    ):
        """Advance dunning process to next step"""
        try:
            process.current_step += 1
            
            # Check if we've reached the end of the sequence
            if process.current_step >= len(sequence.steps):
                process.status = DunningStatus.COMPLETED
                logger.info(f"Dunning process completed: {process.id}")
            
            # Check if we've exceeded max attempts
            elif process.total_attempts >= sequence.max_total_attempts:
                process.status = DunningStatus.ABANDONED
                logger.info(f"Dunning process abandoned - max attempts reached: {process.id}")
            
            # Check if we've exceeded time limit
            elif (datetime.now() - process.started_at).days >= sequence.abandon_after_days:
                process.status = DunningStatus.ABANDONED
                logger.info(f"Dunning process abandoned - time limit reached: {process.id}")
                
        except Exception as e:
            logger.error(f"Error advancing to next step: {str(e)}")
    
    async def _complete_dunning_process(self, failed_payment_id: str, reason: str):
        """Complete dunning process"""
        try:
            # Find the dunning process for this failed payment
            for process in self.dunning_processes.values():
                if process.failed_payment_id == failed_payment_id:
                    process.status = DunningStatus.COMPLETED
                    if not process.metadata:
                        process.metadata = {}
                    process.metadata["completion_reason"] = reason
                    process.metadata["completed_at"] = datetime.now().isoformat()
                    
                    logger.info(f"Dunning process completed: {process.id} - {reason}")
                    break
                    
        except Exception as e:
            logger.error(f"Error completing dunning process: {str(e)}")
    
    # Helper methods
    
    async def _is_holiday(self, date: datetime) -> bool:
        """Check if date is a holiday (simplified)"""
        # In production, use a proper holiday API or database
        return False
    
    async def _get_customer_timezone_hour(self, customer_id: str) -> int:
        """Get current hour in customer's timezone"""
        # In production, get customer's timezone from database
        # For now, assume UTC
        return datetime.utcnow().hour
    
    def set_payment_retry_handler(self, handler: Callable):
        """Set payment retry handler"""
        self.payment_retry_handler = handler
    
    def set_notification_handler(self, notification_type: NotificationType, handler: Callable):
        """Set notification handler for specific type"""
        self.notification_handlers[notification_type] = handler
    
    def set_customer_preferences(self, customer_id: str, preferences: Dict[str, Any]):
        """Set customer preferences"""
        self.customer_preferences[customer_id] = preferences
    
    async def get_dunning_statistics(self) -> Dict[str, Any]:
        """Get dunning process statistics"""
        try:
            total_failed_payments = len(self.failed_payments)
            total_dunning_processes = len(self.dunning_processes)
            
            status_counts = {}
            for status in DunningStatus:
                status_counts[status.value] = sum(
                    1 for p in self.dunning_processes.values() if p.status == status
                )
            
            recovery_rate = 0
            if total_dunning_processes > 0:
                recovered_count = status_counts.get("completed", 0)
                recovery_rate = (recovered_count / total_dunning_processes) * 100
            
            return {
                "success": True,
                "statistics": {
                    "total_failed_payments": total_failed_payments,
                    "total_dunning_processes": total_dunning_processes,
                    "status_breakdown": status_counts,
                    "recovery_rate_percentage": round(recovery_rate, 2),
                    "total_notifications_sent": sum(
                        p.notifications_sent for p in self.dunning_processes.values()
                    ),
                    "average_attempts_per_process": round(
                        sum(p.total_attempts for p in self.dunning_processes.values()) / 
                        max(total_dunning_processes, 1), 2
                    )
                }
            }
            
        except Exception as e:
            logger.error(f"Error getting dunning statistics: {str(e)}")
            return {"success": False, "error": str(e)}
    
    async def get_process_status(self, process_id: str) -> Dict[str, Any]:
        """Get detailed status of specific dunning process"""
        try:
            if process_id not in self.dunning_processes:
                return {"success": False, "error": "Dunning process not found"}
            
            process = self.dunning_processes[process_id]
            sequence = self.dunning_sequences.get(process.sequence_id)
            actions = self.dunning_actions.get(process_id, [])
            failed_payment = self.failed_payments.get(process.failed_payment_id)
            
            return {
                "success": True,
                "process": asdict(process),
                "sequence": asdict(sequence) if sequence else None,
                "actions": [asdict(action) for action in actions],
                "failed_payment": asdict(failed_payment) if failed_payment else None
            }
            
        except Exception as e:
            logger.error(f"Error getting process status: {str(e)}")
            return {"success": False, "error": str(e)}