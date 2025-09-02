"""Case Escalation Management System
Professional escalation workflow for unresolved copyright enforcement cases
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Set, Tuple, Callable
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import json
import hashlib
from pathlib import Path

from pydantic import BaseModel, Field


logger = logging.getLogger(__name__)


class EscalationLevel(Enum):
    """
Escalation levels for enforcement cases"""

    INITIAL = "initial"              # First enforcement action
    AUTOMATED_RETRY = "automated_retry"  # Automated follow-up
    MANUAL_REVIEW = "manual_review"      # Human review required
    LEGAL_NOTICE = "legal_notice"        # Legal notice sent
    ATTORNEY_REVIEW = "attorney_review"   # Attorney involvement
    FORMAL_COMPLAINT = "formal_complaint" # Formal legal complaint
    LITIGATION = "litigation"            # Court proceedings
    SETTLEMENT = "settlement"            # Settlement negotiation


class EscalationTrigger(Enum):
    """Triggers that cause case escalation"""

    TIME_EXPIRED = "time_expired"
    PLATFORM_REJECTION = "platform_rejection"
    COUNTER_NOTICE = "counter_notice"
    REPEAT_INFRINGEMENT = "repeat_infringement"
    HIGH_VALUE_CONTENT = "high_value_content"
    COMMERCIAL_USE = "commercial_use"
    MANUAL_REQUEST = "manual_request"
    AUTOMATED_THRESHOLD = "automated_threshold"
    PATTERN_DETECTION = "pattern_detection"


class EscalationStatus(Enum):
    """Status of escalation processes"""

    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    PAUSED = "paused"
    CANCELLED = "cancelled"
    FAILED = "failed"


class EscalationOutcome(Enum):
    """Possible outcomes of escalation"""

    CONTENT_REMOVED = "content_removed"
    REVENUE_CLAIMED = "revenue_claimed"
    SETTLEMENT_REACHED = "settlement_reached"
    CASE_DISMISSED = "case_dismissed"
    LITIGATION_WON = "litigation_won"
    LITIGATION_LOST = "litigation_lost"
    COUNTER_CLAIM_FILED = "counter_claim_filed"
    ONGOING = "ongoing"


@dataclass
class EscalationRule:
    """Rule defining when and how to escalate cases"""
    id: str
    name: str
    description: str
    enabled: bool = True
    
    # Trigger conditions
    trigger_type: EscalationTrigger
    time_threshold: Optional[timedelta] = None
    value_threshold: Optional[float] = None
    similarity_threshold: Optional[float] = None
    
    # Current and target levels
    from_level: EscalationLevel
    to_level: EscalationLevel
    
    # Conditions
    requires_manual_approval: bool = False
    min_evidence_quality: str = "fair"
    platforms: List[str] = field(default_factory=list)
    content_types: List[str] = field(default_factory=list)
    
    # Actions to take
    automated_actions: List[str] = field(default_factory=list)
    notifications: List[str] = field(default_factory=list)
    
    # Metadata
    priority: int = 5  # 1-10, higher = more important
    created_at: datetime = field(default_factory=datetime.utcnow)
    last_updated: datetime = field(default_factory=datetime.utcnow)


@dataclass
class EscalationAction:
    """Action taken during escalation"""
    id: str
    case_id: str
    escalation_id: str
    action_type: str
    description: str
    
    # Execution details
    status: EscalationStatus = EscalationStatus.PENDING
    started_at: datetime = field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None
    
    # Results
    success: bool = False
    result_data: Dict[str, Any] = field(default_factory=dict)
    error_message: Optional[str] = None
    
    # Tracking
    assigned_to: Optional[str] = None
    estimated_completion: Optional[datetime] = None
    actual_duration: Optional[timedelta] = None


@dataclass
class EscalationHistory:
    """
Complete escalation history for a case"""
    case_id: str
    escalations: List['CaseEscalation'] = field(default_factory=list)
    total_escalations: int = 0
    current_level: EscalationLevel = EscalationLevel.INITIAL
    highest_level_reached: EscalationLevel = EscalationLevel.INITIAL
    total_time_spent: timedelta = timedelta()
    total_cost: float = 0.0
    
    def add_escalation(self, escalation: 'CaseEscalation'):
        """
Add escalation to history"""
        self.escalations.append(escalation)
        self.total_escalations = len(self.escalations)
        
        if escalation.to_level.value > self.highest_level_reached.value:
            self.highest_level_reached = escalation.to_level
        
        self.current_level = escalation.to_level
    
    def calculate_totals(self):
        """
Calculate total time and cost"""
        total_time = timedelta()
        total_cost = 0.0
        
        for escalation in self.escalations:
            if escalation.completed_at and escalation.started_at:
                duration = escalation.completed_at - escalation.started_at
                total_time += duration
            
            total_cost += escalation.estimated_cost
        
        self.total_time_spent = total_time
        self.total_cost = total_cost


@dataclass
class CaseEscalation:
    """
Individual case escalation instance"""
    id: str
    case_id: str
    triggered_by: EscalationTrigger
    trigger_data: Dict[str, Any] = field(default_factory=dict)
    
    # Escalation path
    from_level: EscalationLevel
    to_level: EscalationLevel
    escalation_rule_id: Optional[str] = None
    
    # Status and timing
    status: EscalationStatus = EscalationStatus.PENDING
    started_at: datetime = field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None
    deadline: Optional[datetime] = None
    
    # Actions and results
    actions: List[EscalationAction] = field(default_factory=list)
    outcome: Optional[EscalationOutcome] = None
    
    # Resource allocation
    assigned_to: Optional[str] = None
    estimated_cost: float = 0.0
    actual_cost: float = 0.0
    priority: int = 5
    
    # Documentation
    notes: List[str] = field(default_factory=list)
    evidence_updates: List[str] = field(default_factory=list)
    
    def add_action(self, action: EscalationAction):
        """
Add action to escalation"""
        self.actions.append(action)
    
    def add_note(self, note: str):
        """
Add note to escalation"""
        timestamp = datetime.utcnow().isoformat()
        self.notes.append(f"{timestamp}: {note}")
    
    def calculate_duration(self) -> Optional[timedelta]:
        """Calculate escalation duration"""
        if self.completed_at and self.started_at:
            return self.completed_at - self.started_at
        return None


class AutomatedEscalationEngine:
    """
Engine for automated case escalation"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.escalation_rules: Dict[str, EscalationRule] = {}
        self.active_escalations: Dict[str, CaseEscalation] = {}
        self.escalation_history: Dict[str, EscalationHistory] = {}
        
        # Engine settings
        self.monitoring_interval = self.config.get('monitoring_interval', 300)  # 5 minutes
        self.max_concurrent_escalations = self.config.get('max_concurrent_escalations', 50)
        self.auto_escalation_enabled = self.config.get('auto_escalation_enabled', True)
        
        # Cost estimation
        self.cost_per_level = {
            EscalationLevel.INITIAL: 0.0,
            EscalationLevel.AUTOMATED_RETRY: 5.0,
            EscalationLevel.MANUAL_REVIEW: 50.0,
            EscalationLevel.LEGAL_NOTICE: 200.0,
            EscalationLevel.ATTORNEY_REVIEW: 500.0,
            EscalationLevel.FORMAL_COMPLAINT: 2000.0,
            EscalationLevel.LITIGATION: 10000.0,
            EscalationLevel.SETTLEMENT: 1000.0
        }
        
        self._setup_default_rules()
        logger.info("Automated escalation engine initialized")
    
    def _setup_default_rules(self):
        """Setup default escalation rules"""
        default_rules = [
            EscalationRule(
                id="time_based_retry",
                name="Time-Based Automated Retry",
                description="Retry enforcement after initial failure with time delay",
                trigger_type=EscalationTrigger.TIME_EXPIRED,
                time_threshold=timedelta(hours=24),
                from_level=EscalationLevel.INITIAL,
                to_level=EscalationLevel.AUTOMATED_RETRY,
                automated_actions=["retry_platform_action", "collect_additional_evidence"],
                priority=7
            ),
            EscalationRule(
                id="platform_rejection_review",
                name="Platform Rejection Manual Review",
                description="Escalate to manual review when platform rejects takedown",
                trigger_type=EscalationTrigger.PLATFORM_REJECTION,
                from_level=EscalationLevel.AUTOMATED_RETRY,
                to_level=EscalationLevel.MANUAL_REVIEW,
                requires_manual_approval=True,
                notifications=["human_reviewer", "case_manager"],
                priority=8
            ),
            EscalationRule(
                id="high_value_legal_notice",
                name="High Value Content Legal Notice",
                description="Send legal notice for high-value content infringement",
                trigger_type=EscalationTrigger.HIGH_VALUE_CONTENT,
                value_threshold=10000.0,
                from_level=EscalationLevel.MANUAL_REVIEW,
                to_level=EscalationLevel.LEGAL_NOTICE,
                automated_actions=["generate_legal_notice", "collect_damages_evidence"],
                priority=9
            ),
            EscalationRule(
                id="repeat_infringer_attorney",
                name="Repeat Infringer Attorney Review",
                description="Involve attorney for repeat infringers",
                trigger_type=EscalationTrigger.REPEAT_INFRINGEMENT,
                from_level=EscalationLevel.LEGAL_NOTICE,
                to_level=EscalationLevel.ATTORNEY_REVIEW,
                requires_manual_approval=True,
                notifications=["attorney", "legal_team"],
                priority=8
            ),
            EscalationRule(
                id="counter_notice_formal_complaint",
                name="Counter Notice Formal Complaint",
                description="File formal complaint when counter notice received",
                trigger_type=EscalationTrigger.COUNTER_NOTICE,
                from_level=EscalationLevel.ATTORNEY_REVIEW,
                to_level=EscalationLevel.FORMAL_COMPLAINT,
                requires_manual_approval=True,
                min_evidence_quality="excellent",
                priority=9
            ),
            EscalationRule(
                id="commercial_use_litigation",
                name="Commercial Use Litigation",
                description="Proceed to litigation for commercial infringement",
                trigger_type=EscalationTrigger.COMMERCIAL_USE,
                similarity_threshold=0.9,
                from_level=EscalationLevel.FORMAL_COMPLAINT,
                to_level=EscalationLevel.LITIGATION,
                requires_manual_approval=True,
                notifications=["legal_team", "executive_team"],
                priority=10
            )
        ]
        
        for rule in default_rules:
            self.escalation_rules[rule.id] = rule
    
    async def evaluate_case_for_escalation(
        self,
        case_id: str,
        case_data: Dict[str, Any]
    ) -> List[EscalationRule]:
        """Evaluate if case should be escalated and return applicable rules"""
        try:
            applicable_rules = []
            current_level = EscalationLevel(case_data.get('current_escalation_level', 'initial'))
            
            for rule in self.escalation_rules.values():
                if not rule.enabled:
                    continue
                
                # Check if rule applies to current level
                if rule.from_level != current_level:
                    continue
                
                # Check trigger conditions
                if await self._check_trigger_conditions(rule, case_data):
                    applicable_rules.append(rule)
            
            # Sort by priority (highest first)
            applicable_rules.sort(key=lambda r: r.priority, reverse=True)
            
            return applicable_rules
            
        except Exception as e:
            logger.error(f"Error evaluating escalation for case {case_id}: {e}")
            return []
    
    async def _check_trigger_conditions(
        self,
        rule: EscalationRule,
        case_data: Dict[str, Any]
    ) -> bool:
        """Check if trigger conditions are met"""
        try:
            trigger = rule.trigger_type
            
            if trigger == EscalationTrigger.TIME_EXPIRED:
                last_action_time = case_data.get('last_action_timestamp')
                if last_action_time and rule.time_threshold:
                    elapsed = datetime.utcnow() - datetime.fromisoformat(last_action_time)
                    return elapsed >= rule.time_threshold
            
            elif trigger == EscalationTrigger.PLATFORM_REJECTION:
                return case_data.get('platform_status') == 'rejected'
            
            elif trigger == EscalationTrigger.COUNTER_NOTICE:
                return case_data.get('counter_notice_received', False)
            
            elif trigger == EscalationTrigger.REPEAT_INFRINGEMENT:
                infringer_id = case_data.get('infringer_id')
                if infringer_id:
                    # Check for previous cases against same infringer
                    previous_cases = await self._get_previous_cases_for_infringer(infringer_id)
                    return len(previous_cases) >= 2
            
            elif trigger == EscalationTrigger.HIGH_VALUE_CONTENT:
                estimated_value = case_data.get('estimated_content_value', 0)
                return estimated_value >= (rule.value_threshold or 0)
            
            elif trigger == EscalationTrigger.COMMERCIAL_USE:
                return case_data.get('commercial_use_detected', False)
            
            elif trigger == EscalationTrigger.AUTOMATED_THRESHOLD:
                similarity_score = case_data.get('similarity_score', 0)
                return similarity_score >= (rule.similarity_threshold or 0)
            
            elif trigger == EscalationTrigger.PATTERN_DETECTION:
                return case_data.get('pattern_detected', False)
            
            elif trigger == EscalationTrigger.MANUAL_REQUEST:
                return case_data.get('manual_escalation_requested', False)
            
            return False
            
        except Exception as e:
            logger.error(f"Error checking trigger conditions: {e}")
            return False
    
    async def _get_previous_cases_for_infringer(self, infringer_id: str) -> List[str]:
        """Get previous cases for the same infringer"""
        try:
            # In real implementation, would query database
            # For now, simulate with empty list
            return []
        except Exception as e:
            logger.error(f"Error getting previous cases for {infringer_id}: {e}")
            return []
    
    async def escalate_case(
        self,
        case_id: str,
        rule: EscalationRule,
        trigger_data: Optional[Dict[str, Any]] = None
    ) -> CaseEscalation:
        """Escalate case according to rule"""
        try:
            logger.info(f"Escalating case {case_id} from {rule.from_level.value} to {rule.to_level.value}")
            
            # Create escalation
            escalation_id = f"ESC-{case_id}-{int(datetime.utcnow().timestamp())}"
            
            escalation = CaseEscalation(
                id=escalation_id,
                case_id=case_id,
                triggered_by=rule.trigger_type,
                trigger_data=trigger_data or {},
                from_level=rule.from_level,
                to_level=rule.to_level,
                escalation_rule_id=rule.id,
                assigned_to=self._assign_escalation_handler(rule.to_level),
                estimated_cost=self.cost_per_level.get(rule.to_level, 0),
                priority=rule.priority,
                deadline=datetime.utcnow() + self._calculate_deadline(rule.to_level)
            )
            
            escalation.add_note(f"Escalated by rule: {rule.name}")
            
            # Track escalation
            self.active_escalations[escalation_id] = escalation
            
            # Update escalation history
            if case_id not in self.escalation_history:
                self.escalation_history[case_id] = EscalationHistory(case_id=case_id)
            
            self.escalation_history[case_id].add_escalation(escalation)
            
            # Execute automated actions
            if rule.automated_actions and not rule.requires_manual_approval:
                await self._execute_automated_actions(escalation, rule.automated_actions)
            
            # Send notifications
            if rule.notifications:
                await self._send_escalation_notifications(escalation, rule.notifications)
            
            escalation.status = EscalationStatus.IN_PROGRESS
            
            logger.info(f"Case {case_id} escalated successfully: {escalation_id}")
            return escalation
            
        except Exception as e:
            logger.error(f"Error escalating case {case_id}: {e}")
            raise
    
    def _assign_escalation_handler(self, level: EscalationLevel) -> Optional[str]:
        """Assign handler based on escalation level"""
        handlers = {
            EscalationLevel.AUTOMATED_RETRY: "automated_system",
            EscalationLevel.MANUAL_REVIEW: "human_reviewer",
            EscalationLevel.LEGAL_NOTICE: "legal_specialist",
            EscalationLevel.ATTORNEY_REVIEW: "attorney",
            EscalationLevel.FORMAL_COMPLAINT: "litigation_attorney",
            EscalationLevel.LITIGATION: "litigation_team",
            EscalationLevel.SETTLEMENT: "settlement_specialist"
        }
        
        return handlers.get(level)
    
    def _calculate_deadline(self, level: EscalationLevel) -> timedelta:
        """Calculate deadline based on escalation level"""
        deadlines = {
            EscalationLevel.AUTOMATED_RETRY: timedelta(hours=6),
            EscalationLevel.MANUAL_REVIEW: timedelta(days=2),
            EscalationLevel.LEGAL_NOTICE: timedelta(days=5),
            EscalationLevel.ATTORNEY_REVIEW: timedelta(days=7),
            EscalationLevel.FORMAL_COMPLAINT: timedelta(days=14),
            EscalationLevel.LITIGATION: timedelta(days=30),
            EscalationLevel.SETTLEMENT: timedelta(days=21)
        }
        
        return deadlines.get(level, timedelta(days=7))
    
    async def _execute_automated_actions(
        self,
        escalation: CaseEscalation,
        actions: List[str]
    ):
        """
Execute automated actions for escalation"""
        try:
            for action_type in actions:
                action_id = f"ACT-{escalation.id}-{len(escalation.actions)}"
                
                action = EscalationAction(
                    id=action_id,
                    case_id=escalation.case_id,
                    escalation_id=escalation.id,
                    action_type=action_type,
                    description=f"Automated action: {action_type}",
                    assigned_to="automated_system"
                )
                
                # Execute action based on type
                if action_type == "retry_platform_action":
                    success = await self._retry_platform_action(escalation.case_id)
                elif action_type == "collect_additional_evidence":
                    success = await self._collect_additional_evidence(escalation.case_id)
                elif action_type == "generate_legal_notice":
                    success = await self._generate_legal_notice(escalation.case_id)
                elif action_type == "collect_damages_evidence":
                    success = await self._collect_damages_evidence(escalation.case_id)
                else:
                    logger.warning(f"Unknown automated action: {action_type}")
                    success = False
                
                # Update action status
                action.completed_at = datetime.utcnow()
                action.success = success
                
                if not success:
                    action.error_message = f"Failed to execute {action_type}"
                
                escalation.add_action(action)
                
                logger.debug(f"Executed automated action {action_type}: {'success' if success else 'failed'}")
                
        except Exception as e:
            logger.error(f"Error executing automated actions: {e}")
    
    async def _retry_platform_action(self, case_id: str) -> bool:
        """Retry platform enforcement action"""
        try:
            # In real implementation, would integrate with platform handlers
            logger.info(f"Retrying platform action for case {case_id}")
            return True
        except Exception as e:
            logger.error(f"Error retrying platform action: {e}")
            return False
    
    async def _collect_additional_evidence(self, case_id: str) -> bool:
        """Collect additional evidence for case"""
        try:
            # In real implementation, would integrate with evidence collector
            logger.info(f"Collecting additional evidence for case {case_id}")
            return True
        except Exception as e:
            logger.error(f"Error collecting additional evidence: {e}")
            return False
    
    async def _generate_legal_notice(self, case_id: str) -> bool:
        """Generate legal notice for case"""
        try:
            # In real implementation, would integrate with legal document generator
            logger.info(f"Generating legal notice for case {case_id}")
            return True
        except Exception as e:
            logger.error(f"Error generating legal notice: {e}")
            return False
    
    async def _collect_damages_evidence(self, case_id: str) -> bool:
        """Collect evidence of damages"""
        try:
            # In real implementation, would calculate and document damages
            logger.info(f"Collecting damages evidence for case {case_id}")
            return True
        except Exception as e:
            logger.error(f"Error collecting damages evidence: {e}")
            return False
    
    async def _send_escalation_notifications(
        self,
        escalation: CaseEscalation,
        recipients: List[str]
    ):
        """Send notifications about escalation"""
        try:
            for recipient in recipients:
                # In real implementation, would send actual notifications
                logger.info(f"Sending escalation notification to {recipient} for case {escalation.case_id}")
                
        except Exception as e:
            logger.error(f"Error sending escalation notifications: {e}")
    
    async def approve_escalation(
        self,
        escalation_id: str,
        approver: str,
        notes: Optional[str] = None
    ) -> bool:
        """Approve manual escalation"""
        try:
            escalation = self.active_escalations.get(escalation_id)
            if not escalation:
                logger.error(f"Escalation not found: {escalation_id}")
                return False
            
            escalation.status = EscalationStatus.IN_PROGRESS
            escalation.assigned_to = approver
            
            if notes:
                escalation.add_note(f"Approved by {approver}: {notes}")
            else:
                escalation.add_note(f"Approved by {approver}")
            
            # Execute any pending automated actions
            rule = self.escalation_rules.get(escalation.escalation_rule_id)
            if rule and rule.automated_actions:
                await self._execute_automated_actions(escalation, rule.automated_actions)
            
            logger.info(f"Escalation {escalation_id} approved by {approver}")
            return True
            
        except Exception as e:
            logger.error(f"Error approving escalation {escalation_id}: {e}")
            return False
    
    async def reject_escalation(
        self,
        escalation_id: str,
        rejector: str,
        reason: str
    ) -> bool:
        """Reject manual escalation"""
        try:
            escalation = self.active_escalations.get(escalation_id)
            if not escalation:
                logger.error(f"Escalation not found: {escalation_id}")
                return False
            
            escalation.status = EscalationStatus.CANCELLED
            escalation.completed_at = datetime.utcnow()
            escalation.outcome = EscalationOutcome.CASE_DISMISSED
            
            escalation.add_note(f"Rejected by {rejector}: {reason}")
            
            # Remove from active escalations
            del self.active_escalations[escalation_id]
            
            logger.info(f"Escalation {escalation_id} rejected by {rejector}")
            return True
            
        except Exception as e:
            logger.error(f"Error rejecting escalation {escalation_id}: {e}")
            return False
    
    async def complete_escalation(
        self,
        escalation_id: str,
        outcome: EscalationOutcome,
        notes: Optional[str] = None
    ) -> bool:
        """Mark escalation as completed"""
        try:
            escalation = self.active_escalations.get(escalation_id)
            if not escalation:
                logger.error(f"Escalation not found: {escalation_id}")
                return False
            
            escalation.status = EscalationStatus.COMPLETED
            escalation.completed_at = datetime.utcnow()
            escalation.outcome = outcome
            
            if notes:
                escalation.add_note(f"Completed: {notes}")
            
            # Calculate actual cost and duration
            duration = escalation.calculate_duration()
            if duration:
                escalation.actual_cost = escalation.estimated_cost
            
            # Update escalation history
            history = self.escalation_history.get(escalation.case_id)
            if history:
                history.calculate_totals()
            
            # Remove from active escalations
            del self.active_escalations[escalation_id]
            
            logger.info(f"Escalation {escalation_id} completed with outcome: {outcome.value}")
            return True
            
        except Exception as e:
            logger.error(f"Error completing escalation {escalation_id}: {e}")
            return False
    
    async def get_escalation_status(self, escalation_id: str) -> Optional[Dict[str, Any]]:
        """Get detailed escalation status"""
        try:
            escalation = self.active_escalations.get(escalation_id)
            if not escalation:
                # Check completed escalations in history
                for history in self.escalation_history.values():
                    for esc in history.escalations:
                        if esc.id == escalation_id:
                            escalation = esc
                            break
                    if escalation:
                        break
                
                if not escalation:
                    return None
            
            status = {
                'id': escalation.id,
                'case_id': escalation.case_id,
                'triggered_by': escalation.triggered_by.value,
                'from_level': escalation.from_level.value,
                'to_level': escalation.to_level.value,
                'status': escalation.status.value,
                'started_at': escalation.started_at.isoformat(),
                'completed_at': escalation.completed_at.isoformat() if escalation.completed_at else None,
                'deadline': escalation.deadline.isoformat() if escalation.deadline else None,
                'assigned_to': escalation.assigned_to,
                'estimated_cost': escalation.estimated_cost,
                'actual_cost': escalation.actual_cost,
                'priority': escalation.priority,
                'outcome': escalation.outcome.value if escalation.outcome else None,
                'actions_count': len(escalation.actions),
                'notes_count': len(escalation.notes),
                'duration': str(escalation.calculate_duration()) if escalation.calculate_duration() else None
            }
            
            return status
            
        except Exception as e:
            logger.error(f"Error getting escalation status {escalation_id}: {e}")
            return None
    
    async def get_case_escalation_history(self, case_id: str) -> Optional[EscalationHistory]:
        """Get complete escalation history for case"""
        return self.escalation_history.get(case_id)
    
    async def monitor_escalations(self):
        """
Monitor active escalations for deadlines and status updates"""
        try:
            current_time = datetime.utcnow()
            overdue_escalations = []
            
            for escalation in self.active_escalations.values():
                # Check for overdue escalations
                if escalation.deadline and current_time > escalation.deadline:
                    overdue_escalations.append(escalation)
                
                # Check for stalled escalations
                if escalation.status == EscalationStatus.IN_PROGRESS:
                    time_since_start = current_time - escalation.started_at
                    max_duration = self._calculate_deadline(escalation.to_level) * 2
                    
                    if time_since_start > max_duration:
                        escalation.add_note("Escalation appears stalled - requires attention")
                        await self._send_escalation_notifications(
                            escalation,
                            ["case_manager", "supervisor"]
                        )
            
            # Handle overdue escalations
            for escalation in overdue_escalations:
                escalation.add_note("Escalation overdue - automatic follow-up")
                await self._handle_overdue_escalation(escalation)
            
            if overdue_escalations:
                logger.warning(f"Found {len(overdue_escalations)} overdue escalations")
            
        except Exception as e:
            logger.error(f"Error monitoring escalations: {e}")
    
    async def _handle_overdue_escalation(self, escalation: CaseEscalation):
        """Handle overdue escalation"""
        try:
            # Send urgent notifications
            await self._send_escalation_notifications(
                escalation,
                ["supervisor", "manager", "urgent_queue"]
            )
            
            # Optionally auto-escalate further if configured
            if self.config.get('auto_escalate_overdue', False):
                next_level = self._get_next_escalation_level(escalation.to_level)
                if next_level:
                    logger.info(f"Auto-escalating overdue case {escalation.case_id} to {next_level.value}")
                    # Would trigger new escalation here
            
        except Exception as e:
            logger.error(f"Error handling overdue escalation: {e}")
    
    def _get_next_escalation_level(self, current_level: EscalationLevel) -> Optional[EscalationLevel]:
        try:
                    # Request validation
                    if not current_level:
                        raise ValueError("Invalid request")
            
                    # Process request
                    result = await self._handle__get_next_escalation_level_request(current_level)
            
                    # Return response
                    return {"status": "success", "data": result}
            
                except Exception as e:
                    logger.error(f"API handler _get_next_escalation_level failed: {e}")
                    return {"status": "error", "message": str(e)}
    async def get_escalation_statistics(self) -> Dict[str, Any]:
        """
Get escalation engine statistics"""
        try:
            active_count = len(self.active_escalations)
            total_cases = len(self.escalation_history)
            
            # Count by level
            active_by_level = {}
            for escalation in self.active_escalations.values():
                level = escalation.to_level.value
                active_by_level[level] = active_by_level.get(level, 0) + 1
            
            # Count by status
            active_by_status = {}
            for escalation in self.active_escalations.values():
                status = escalation.status.value
                active_by_status[status] = active_by_status.get(status, 0) + 1
            
            # Calculate completion rates
            completed_escalations = []
            for history in self.escalation_history.values():
                for esc in history.escalations:
                    if esc.status == EscalationStatus.COMPLETED:
                        completed_escalations.append(esc)
            
            # Average times by level
            avg_times_by_level = {}
            for level in EscalationLevel:
                level_escalations = [e for e in completed_escalations if e.to_level == level]
                if level_escalations:
                    durations = [e.calculate_duration() for e in level_escalations if e.calculate_duration()]
                    if durations:
                        avg_duration = sum(durations, timedelta()) / len(durations)
                        avg_times_by_level[level.value] = str(avg_duration)
            
            stats = {
                'active_escalations': active_count,
                'total_cases_with_escalations': total_cases,
                'active_by_level': active_by_level,
                'active_by_status': active_by_status,
                'total_completed': len(completed_escalations),
                'average_times_by_level': avg_times_by_level,
                'auto_escalation_enabled': self.auto_escalation_enabled,
                'monitoring_interval': self.monitoring_interval,
                'total_rules': len(self.escalation_rules)
            }
            
            return stats
            
        except Exception as e:
            logger.error(f"Error getting escalation statistics: {e}")
            return {}
    
    async def shutdown(self):
        """Shutdown escalation engine"""
        try:
            # Save state of active escalations
            # In real implementation, would persist to database
            
            logger.info(f"Shutting down escalation engine with {len(self.active_escalations)} active escalations")
            
            self.active_escalations.clear()
            self.escalation_history.clear()
            
            logger.info("Escalation engine shutdown complete")
            
        except Exception as e:
            logger.error(f"Error shutting down escalation engine: {e}")


# Global instance
escalation_engine = AutomatedEscalationEngine()


async def get_escalation_engine() -> AutomatedEscalationEngine:
    """Get the global escalation engine instance"""
    return escalation_engine


__all__ = [
    'AutomatedEscalationEngine',
    'EscalationRule',
    'CaseEscalation',
    'EscalationAction',
    'EscalationHistory',
    'EscalationLevel',
    'EscalationTrigger',
    'EscalationStatus',
    'EscalationOutcome',
    'get_escalation_engine'
]
