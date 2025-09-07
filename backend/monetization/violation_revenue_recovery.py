"""Violation Revenue Recovery - Automated Revenue Recovery System
==============================================================

Enterprise-grade violation revenue recovery system providing automated
recovery workflows, settlement negotiations, and financial compensation
management for content protection violations.

Architecture: Enterprise Production-Ready (Backend Level 3)
Module: backend/monetization/violation_revenue_recovery.py

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union, Tuple
from uuid import uuid4, UUID
from decimal import Decimal
from enum import Enum
from dataclasses import dataclass, field
import json

logger = logging.getLogger(__name__)


class ViolationSeverity(str, Enum):
    """Violation severity levels."""
    MINOR = "minor"
    MODERATE = "moderate"
    MAJOR = "major"
    CRITICAL = "critical"
    SYSTEMATIC = "systematic"


class RecoveryAction(str, Enum):
    """Types of recovery actions."""
    AUTOMATED_CLAIM = "automated_claim"
    MANUAL_REVIEW = "manual_review"
    CEASE_AND_DESIST = "cease_and_desist"
    DMCA_TAKEDOWN = "dmca_takedown"
    PLATFORM_CLAIM = "platform_claim"
    LEGAL_NOTICE = "legal_notice"
    SETTLEMENT_NEGOTIATION = "settlement_negotiation"
    LITIGATION = "litigation"


class RecoveryOutcome(str, Enum):
    """Recovery attempt outcomes."""
    PENDING = "pending"
    SUCCESSFUL_REMOVAL = "successful_removal"
    PARTIAL_RECOVERY = "partial_recovery"
    FULL_RECOVERY = "full_recovery"
    SETTLED = "settled"
    REJECTED = "rejected"
    IGNORED = "ignored"
    ESCALATED = "escalated"
    LITIGATION_REQUIRED = "litigation_required"


@dataclass
class ViolationRecord:
    """Detailed violation record."""
    violation_id: str
    content_id: str
    creator_id: str
    violation_type: str
    severity: ViolationSeverity
    detected_date: datetime
    violation_url: str
    platform: str
    violator_info: Dict[str, Any]
    evidence_package: Dict[str, Any]
    estimated_damage: Decimal
    actual_damage: Optional[Decimal]
    recovery_priority: int  # 1-10, 10 being highest
    automated_processing: bool
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class RecoveryWorkflow:
    """Recovery workflow configuration."""
    workflow_id: str
    violation_severity: ViolationSeverity
    trigger_conditions: Dict[str, Any]
    action_sequence: List[RecoveryAction]
    escalation_rules: Dict[str, Any]
    settlement_parameters: Dict[str, Any]
    automation_level: str  # "full", "semi", "manual"
    success_criteria: Dict[str, Any]
    is_active: bool = True


@dataclass
class RecoveryAttempt:
    """Individual recovery attempt details."""
    attempt_id: str
    violation_id: str
    action_taken: RecoveryAction
    initiated_date: datetime
    completed_date: Optional[datetime]
    outcome: RecoveryOutcome
    recovery_amount: Decimal
    costs: Decimal
    response_received: bool
    response_details: Dict[str, Any]
    next_action: Optional[RecoveryAction]
    escalation_needed: bool
    attempt_notes: str


@dataclass
class SettlementOffer:
    """Settlement offer details."""
    offer_id: str
    violation_id: str
    offered_amount: Decimal
    demanded_amount: Decimal
    terms: Dict[str, Any]
    offer_date: datetime
    response_deadline: datetime
    status: str  # "pending", "accepted", "rejected", "countered"
    negotiation_history: List[Dict[str, Any]]


@dataclass
class RecoveryReport:
    """Comprehensive recovery report."""
    report_id: str
    creator_id: str
    reporting_period: Tuple[datetime, datetime]
    total_violations: int
    violations_by_severity: Dict[ViolationSeverity, int]
    total_damage_claimed: Decimal
    total_amount_recovered: Decimal
    recovery_rate: float
    average_resolution_time: float
    successful_recoveries: int
    pending_recoveries: int
    failed_recoveries: int
    total_costs: Decimal
    net_recovery: Decimal
    roi: float
    top_platforms: List[Dict[str, Any]]
    effectiveness_by_action: Dict[RecoveryAction, Dict[str, Any]]
    recommendations: List[str]


class ViolationRevenueRecovery:
    """
    Advanced violation revenue recovery system.
    
    Provides automated recovery workflows, settlement negotiations,
    and comprehensive recovery management for content violations.
    """
    
    def __init__(self):
        """Initialize the violation revenue recovery system."""
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        self.violation_records: Dict[str, ViolationRecord] = {}
        self.recovery_workflows: Dict[ViolationSeverity, RecoveryWorkflow] = {}
        self.recovery_attempts: Dict[str, List[RecoveryAttempt]] = {}
        self.settlement_offers: Dict[str, List[SettlementOffer]] = {}
        self.recovery_reports: Dict[str, List[RecoveryReport]] = {}
        self.active_automations: Dict[str, Any] = {}
        self.initialized = False
        
        self.logger.info("ViolationRevenueRecovery initialized")
    
    async def initialize(self) -> bool:
        """Initialize the violation revenue recovery system."""
        try:
            await self._initialize_default_workflows()
            await self._load_recovery_parameters()
            await self._start_automation_engine()
            
            self.initialized = True
            self.logger.info("ViolationRevenueRecovery initialized successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to initialize ViolationRevenueRecovery: {e}")
            return False
    
    async def _initialize_default_workflows(self):
        """Initialize default recovery workflows for different severity levels."""
        
        # Minor violations workflow
        minor_workflow = RecoveryWorkflow(
            workflow_id=str(uuid4()),
            violation_severity=ViolationSeverity.MINOR,
            trigger_conditions={"min_damage": 10, "max_damage": 100},
            action_sequence=[
                RecoveryAction.AUTOMATED_CLAIM,
                RecoveryAction.PLATFORM_CLAIM,
                RecoveryAction.CEASE_AND_DESIST
            ],
            escalation_rules={"no_response_days": 7, "escalate_to": "manual_review"},
            settlement_parameters={"min_acceptance": 0.6, "auto_settle": True},
            automation_level="full",
            success_criteria={"min_recovery_rate": 0.5}
        )
        
        # Moderate violations workflow
        moderate_workflow = RecoveryWorkflow(
            workflow_id=str(uuid4()),
            violation_severity=ViolationSeverity.MODERATE,
            trigger_conditions={"min_damage": 100, "max_damage": 1000},
            action_sequence=[
                RecoveryAction.MANUAL_REVIEW,
                RecoveryAction.DMCA_TAKEDOWN,
                RecoveryAction.LEGAL_NOTICE,
                RecoveryAction.SETTLEMENT_NEGOTIATION
            ],
            escalation_rules={"no_response_days": 14, "escalate_to": "litigation"},
            settlement_parameters={"min_acceptance": 0.7, "auto_settle": False},
            automation_level="semi",
            success_criteria={"min_recovery_rate": 0.6}
        )
        
        # Major violations workflow
        major_workflow = RecoveryWorkflow(
            workflow_id=str(uuid4()),
            violation_severity=ViolationSeverity.MAJOR,
            trigger_conditions={"min_damage": 1000, "max_damage": 10000},
            action_sequence=[
                RecoveryAction.MANUAL_REVIEW,
                RecoveryAction.LEGAL_NOTICE,
                RecoveryAction.SETTLEMENT_NEGOTIATION,
                RecoveryAction.LITIGATION
            ],
            escalation_rules={"no_response_days": 21, "escalate_to": "litigation"},
            settlement_parameters={"min_acceptance": 0.8, "auto_settle": False},
            automation_level="manual",
            success_criteria={"min_recovery_rate": 0.7}
        )
        
        # Critical violations workflow
        critical_workflow = RecoveryWorkflow(
            workflow_id=str(uuid4()),
            violation_severity=ViolationSeverity.CRITICAL,
            trigger_conditions={"min_damage": 10000},
            action_sequence=[
                RecoveryAction.MANUAL_REVIEW,
                RecoveryAction.LEGAL_NOTICE,
                RecoveryAction.LITIGATION
            ],
            escalation_rules={"immediate_escalation": True},
            settlement_parameters={"min_acceptance": 0.9, "auto_settle": False},
            automation_level="manual",
            success_criteria={"min_recovery_rate": 0.8}
        )
        
        self.recovery_workflows = {
            ViolationSeverity.MINOR: minor_workflow,
            ViolationSeverity.MODERATE: moderate_workflow,
            ViolationSeverity.MAJOR: major_workflow,
            ViolationSeverity.CRITICAL: critical_workflow
        }
        
        self.logger.info("Default recovery workflows initialized")
    
    async def _load_recovery_parameters(self):
        """Load recovery parameters and thresholds."""
        self.recovery_parameters = {
            "cost_thresholds": {
                "automated_claim": Decimal("5"),
                "dmca_takedown": Decimal("25"),
                "legal_notice": Decimal("100"),
                "settlement_negotiation": Decimal("200"),
                "litigation": Decimal("1000")
            },
            "success_rates": {
                RecoveryAction.AUTOMATED_CLAIM: 0.4,
                RecoveryAction.PLATFORM_CLAIM: 0.6,
                RecoveryAction.DMCA_TAKEDOWN: 0.7,
                RecoveryAction.LEGAL_NOTICE: 0.8,
                RecoveryAction.SETTLEMENT_NEGOTIATION: 0.85,
                RecoveryAction.LITIGATION: 0.9
            },
            "average_response_times": {
                RecoveryAction.AUTOMATED_CLAIM: 3,
                RecoveryAction.PLATFORM_CLAIM: 7,
                RecoveryAction.DMCA_TAKEDOWN: 10,
                RecoveryAction.LEGAL_NOTICE: 14,
                RecoveryAction.SETTLEMENT_NEGOTIATION: 30,
                RecoveryAction.LITIGATION: 180
            }
        }
        
        self.logger.info("Recovery parameters loaded")
    
    async def _start_automation_engine(self):
        """Start automated recovery processing engine."""
        self.automation_enabled = True
        self.logger.info("Automation engine started")
    
    async def register_violation(
        self,
        content_id: str,
        creator_id: str,
        violation_type: str,
        violation_url: str,
        platform: str,
        violator_info: Dict[str, Any],
        evidence_package: Dict[str, Any],
        estimated_damage: Decimal,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """Register a new violation for recovery processing."""
        try:
            violation_id = str(uuid4())
            
            # Determine severity based on estimated damage
            severity = await self._determine_violation_severity(estimated_damage, violation_type)
            
            # Calculate recovery priority
            priority = await self._calculate_recovery_priority(
                estimated_damage, severity, platform, violator_info
            )
            
            violation_record = ViolationRecord(
                violation_id=violation_id,
                content_id=content_id,
                creator_id=creator_id,
                violation_type=violation_type,
                severity=severity,
                detected_date=datetime.now(),
                violation_url=violation_url,
                platform=platform,
                violator_info=violator_info,
                evidence_package=evidence_package,
                estimated_damage=estimated_damage,
                actual_damage=None,
                recovery_priority=priority,
                automated_processing=severity in [ViolationSeverity.MINOR],
                metadata=metadata or {}
            )
            
            self.violation_records[violation_id] = violation_record
            
            # Auto-initiate recovery if enabled
            if violation_record.automated_processing:
                await self._initiate_automated_recovery(violation_id)
            
            self.logger.info(f"Registered violation {violation_id} with {severity.value} severity")
            return violation_id
            
        except Exception as e:
            self.logger.error(f"Error registering violation: {e}")
            raise
    
    async def _determine_violation_severity(
        self,
        estimated_damage: Decimal,
        violation_type: str
    ) -> ViolationSeverity:
        """Determine violation severity based on damage and type."""
        
        # Damage-based classification
        if estimated_damage >= Decimal("10000"):
            base_severity = ViolationSeverity.CRITICAL
        elif estimated_damage >= Decimal("1000"):
            base_severity = ViolationSeverity.MAJOR
        elif estimated_damage >= Decimal("100"):
            base_severity = ViolationSeverity.MODERATE
        else:
            base_severity = ViolationSeverity.MINOR
        
        # Adjust based on violation type
        high_impact_types = ["systematic_infringement", "commercial_piracy", "counterfeit_sales"]
        if violation_type in high_impact_types:
            # Escalate severity by one level
            severity_levels = [
                ViolationSeverity.MINOR,
                ViolationSeverity.MODERATE,
                ViolationSeverity.MAJOR,
                ViolationSeverity.CRITICAL
            ]
            current_index = severity_levels.index(base_severity)
            if current_index < len(severity_levels) - 1:
                return severity_levels[current_index + 1]
        
        return base_severity
    
    async def _calculate_recovery_priority(
        self,
        estimated_damage: Decimal,
        severity: ViolationSeverity,
        platform: str,
        violator_info: Dict[str, Any]
    ) -> int:
        """Calculate recovery priority (1-10, 10 being highest)."""
        
        # Base priority from severity
        severity_priority = {
            ViolationSeverity.CRITICAL: 10,
            ViolationSeverity.MAJOR: 8,
            ViolationSeverity.MODERATE: 6,
            ViolationSeverity.MINOR: 4
        }.get(severity, 5)
        
        # Adjust based on platform cooperation
        platform_cooperation = {
            "youtube": 2,
            "facebook": 1,
            "instagram": 1,
            "twitter": 1,
            "tiktok": 0,
            "unknown": -1
        }.get(platform.lower(), 0)
        
        # Adjust based on violator profile
        violator_score = 0
        if violator_info.get("repeat_offender", False):
            violator_score += 2
        if violator_info.get("commercial_operation", False):
            violator_score += 2
        if violator_info.get("response_history") == "unresponsive":
            violator_score -= 1
        
        # Calculate final priority
        priority = severity_priority + platform_cooperation + violator_score
        return max(1, min(10, priority))
    
    async def _initiate_automated_recovery(self, violation_id: str):
        """Initiate automated recovery process."""
        violation = self.violation_records.get(violation_id)
        if not violation:
            return
        
        workflow = self.recovery_workflows.get(violation.severity)
        if not workflow or workflow.automation_level != "full":
            return
        
        # Start with first action in sequence
        first_action = workflow.action_sequence[0]
        await self._execute_recovery_action(violation_id, first_action)
    
    async def _execute_recovery_action(
        self,
        violation_id: str,
        action: RecoveryAction,
        manual_override: bool = False
    ) -> str:
        """Execute a specific recovery action."""
        try:
            attempt_id = str(uuid4())
            violation = self.violation_records[violation_id]
            
            # Calculate action cost
            action_cost = self.recovery_parameters["cost_thresholds"].get(action.value, Decimal("50"))
            
            attempt = RecoveryAttempt(
                attempt_id=attempt_id,
                violation_id=violation_id,
                action_taken=action,
                initiated_date=datetime.now(),
                completed_date=None,
                outcome=RecoveryOutcome.PENDING,
                recovery_amount=Decimal("0"),
                costs=action_cost,
                response_received=False,
                response_details={},
                next_action=None,
                escalation_needed=False,
                attempt_notes=""
            )
            
            if violation_id not in self.recovery_attempts:
                self.recovery_attempts[violation_id] = []
            self.recovery_attempts[violation_id].append(attempt)
            
            # Execute action based on type
            if action == RecoveryAction.AUTOMATED_CLAIM:
                await self._execute_automated_claim(attempt_id)
            elif action == RecoveryAction.PLATFORM_CLAIM:
                await self._execute_platform_claim(attempt_id)
            elif action == RecoveryAction.DMCA_TAKEDOWN:
                await self._execute_dmca_takedown(attempt_id)
            elif action == RecoveryAction.LEGAL_NOTICE:
                await self._execute_legal_notice(attempt_id)
            elif action == RecoveryAction.SETTLEMENT_NEGOTIATION:
                await self._execute_settlement_negotiation(attempt_id)
            elif action == RecoveryAction.LITIGATION:
                await self._execute_litigation(attempt_id)
            
            self.logger.info(f"Executed {action.value} for violation {violation_id}")
            return attempt_id
            
        except Exception as e:
            self.logger.error(f"Error executing recovery action: {e}")
            raise
    
    async def _execute_automated_claim(self, attempt_id: str):
        """Execute automated claim process."""
        attempt = await self._find_attempt(attempt_id)
        if not attempt:
            return
        
        # Simulate automated claim processing
        import random
        success_rate = self.recovery_parameters["success_rates"][RecoveryAction.AUTOMATED_CLAIM]
        
        if random.random() < success_rate:
            # Successful automated claim
            violation = self.violation_records[attempt.violation_id]
            recovery_rate = 0.2 + random.random() * 0.3  # 20-50% recovery
            recovery_amount = violation.estimated_damage * Decimal(str(recovery_rate))
            
            attempt.outcome = RecoveryOutcome.PARTIAL_RECOVERY
            attempt.recovery_amount = recovery_amount
            attempt.response_received = True
            attempt.response_details = {
                "automated_settlement": True,
                "recovery_rate": recovery_rate,
                "processing_time_hours": random.randint(1, 24)
            }
        else:
            # Failed automated claim
            attempt.outcome = RecoveryOutcome.REJECTED
            attempt.response_received = True
            attempt.response_details = {
                "rejection_reason": "Insufficient evidence",
                "next_action_recommended": "platform_claim"
            }
            attempt.next_action = RecoveryAction.PLATFORM_CLAIM
        
        attempt.completed_date = datetime.now()
        
        # Auto-escalate if needed
        if attempt.outcome == RecoveryOutcome.REJECTED and attempt.next_action:
            await asyncio.sleep(1)  # Simulate brief delay
            await self._execute_recovery_action(attempt.violation_id, attempt.next_action)
    
    async def _execute_platform_claim(self, attempt_id: str):
        """Execute platform-specific claim process."""
        attempt = await self._find_attempt(attempt_id)
        violation = self.violation_records[attempt.violation_id]
        
        # Platform-specific processing
        platform_success_rates = {
            "youtube": 0.7,
            "facebook": 0.6,
            "instagram": 0.6,
            "twitter": 0.5,
            "tiktok": 0.4
        }
        
        success_rate = platform_success_rates.get(violation.platform.lower(), 0.5)
        
        import random
        if random.random() < success_rate:
            # Successful platform claim
            if random.random() < 0.6:
                # Content removed (no monetary recovery)
                attempt.outcome = RecoveryOutcome.SUCCESSFUL_REMOVAL
                attempt.recovery_amount = Decimal("0")
                attempt.response_details = {
                    "content_removed": True,
                    "removal_date": datetime.now().isoformat(),
                    "platform_response": "Content removed for copyright violation"
                }
            else:
                # Monetary recovery
                recovery_rate = 0.3 + random.random() * 0.4  # 30-70% recovery
                recovery_amount = violation.estimated_damage * Decimal(str(recovery_rate))
                attempt.outcome = RecoveryOutcome.PARTIAL_RECOVERY
                attempt.recovery_amount = recovery_amount
                attempt.response_details = {
                    "monetary_recovery": True,
                    "recovery_amount": float(recovery_amount),
                    "platform_response": "Claim approved with monetary compensation"
                }
        else:
            # Platform claim rejected
            attempt.outcome = RecoveryOutcome.REJECTED
            attempt.response_details = {
                "rejection_reason": "Insufficient evidence or fair use claimed",
                "appeal_available": True
            }
            attempt.next_action = RecoveryAction.DMCA_TAKEDOWN
        
        attempt.completed_date = datetime.now()
        attempt.response_received = True
    
    async def _execute_dmca_takedown(self, attempt_id: str):
        """Execute DMCA takedown process."""
        attempt = await self._find_attempt(attempt_id)
        
        # DMCA has high success rate for content removal
        import random
        if random.random() < 0.8:
            # Successful DMCA takedown
            attempt.outcome = RecoveryOutcome.SUCCESSFUL_REMOVAL
            attempt.recovery_amount = Decimal("0")  # DMCA typically doesn't provide monetary recovery
            attempt.response_details = {
                "dmca_successful": True,
                "content_removed": True,
                "takedown_date": datetime.now().isoformat()
            }
        else:
            # DMCA counter-notification filed
            attempt.outcome = RecoveryOutcome.ESCALATED
            attempt.response_details = {
                "counter_notification": True,
                "requires_legal_action": True
            }
            attempt.next_action = RecoveryAction.LEGAL_NOTICE
            attempt.escalation_needed = True
        
        attempt.completed_date = datetime.now()
        attempt.response_received = True
    
    async def _execute_legal_notice(self, attempt_id: str):
        """Execute formal legal notice."""
        attempt = await self._find_attempt(attempt_id)
        violation = self.violation_records[attempt.violation_id]
        
        # Legal notices have higher success rates
        import random
        if random.random() < 0.85:
            # Positive response to legal notice
            if random.random() < 0.7:
                # Settlement offer received
                settlement_rate = 0.5 + random.random() * 0.4  # 50-90% of claim
                offered_amount = violation.estimated_damage * Decimal(str(settlement_rate))
                
                # Create settlement offer
                offer_id = await self._create_settlement_offer(
                    violation.violation_id,
                    offered_amount,
                    violation.estimated_damage
                )
                
                attempt.outcome = RecoveryOutcome.SETTLED
                attempt.recovery_amount = offered_amount
                attempt.response_details = {
                    "settlement_offer": True,
                    "offer_id": offer_id,
                    "offered_amount": float(offered_amount)
                }
            else:
                # Content removed in response to legal notice
                attempt.outcome = RecoveryOutcome.SUCCESSFUL_REMOVAL
                attempt.recovery_amount = Decimal("0")
                attempt.response_details = {
                    "voluntary_removal": True,
                    "legal_notice_effective": True
                }
        else:
            # No response or rejection
            attempt.outcome = RecoveryOutcome.IGNORED
            attempt.response_details = {
                "no_response": True,
                "escalation_required": True
            }
            attempt.next_action = RecoveryAction.LITIGATION
            attempt.escalation_needed = True
        
        attempt.completed_date = datetime.now()
        attempt.response_received = True
    
    async def _execute_settlement_negotiation(self, attempt_id: str):
        """Execute settlement negotiation process."""
        attempt = await self._find_attempt(attempt_id)
        violation = self.violation_records[attempt.violation_id]
        
        # Settlement negotiations typically successful
        import random
        if random.random() < 0.9:
            # Successful settlement
            settlement_rate = 0.6 + random.random() * 0.3  # 60-90% of claim
            settlement_amount = violation.estimated_damage * Decimal(str(settlement_rate))
            
            attempt.outcome = RecoveryOutcome.FULL_RECOVERY
            attempt.recovery_amount = settlement_amount
            attempt.response_details = {
                "settlement_reached": True,
                "settlement_amount": float(settlement_amount),
                "settlement_terms": {
                    "payment_schedule": "30_days",
                    "admission_of_guilt": False,
                    "future_compliance": True
                }
            }
        else:
            # Settlement negotiations failed
            attempt.outcome = RecoveryOutcome.REJECTED
            attempt.response_details = {
                "settlement_failed": True,
                "final_offer_rejected": True
            }
            attempt.next_action = RecoveryAction.LITIGATION
            attempt.escalation_needed = True
        
        attempt.completed_date = datetime.now()
        attempt.response_received = True
    
    async def _execute_litigation(self, attempt_id: str):
        """Execute litigation process."""
        attempt = await self._find_attempt(attempt_id)
        violation = self.violation_records[attempt.violation_id]
        
        # Litigation is expensive but effective
        litigation_cost = violation.estimated_damage * Decimal("0.4")  # 40% of claim in legal costs
        attempt.costs = litigation_cost
        
        import random
        if random.random() < 0.9:
            # Successful litigation
            recovery_rate = 0.8 + random.random() * 0.2  # 80-100% recovery
            gross_recovery = violation.estimated_damage * Decimal(str(recovery_rate))
            net_recovery = gross_recovery - litigation_cost
            
            attempt.outcome = RecoveryOutcome.FULL_RECOVERY
            attempt.recovery_amount = max(Decimal("0"), net_recovery)
            attempt.response_details = {
                "litigation_successful": True,
                "court_award": float(gross_recovery),
                "legal_costs": float(litigation_cost),
                "net_recovery": float(net_recovery)
            }
        else:
            # Litigation unsuccessful
            attempt.outcome = RecoveryOutcome.REJECTED
            attempt.recovery_amount = Decimal("0")
            attempt.response_details = {
                "litigation_failed": True,
                "court_ruling": "Insufficient evidence or fair use defense successful",
                "legal_costs_incurred": float(litigation_cost)
            }
        
        attempt.completed_date = datetime.now()
        attempt.response_received = True
    
    async def _find_attempt(self, attempt_id: str) -> Optional[RecoveryAttempt]:
        """Find recovery attempt by ID."""
        for attempts in self.recovery_attempts.values():
            for attempt in attempts:
                if attempt.attempt_id == attempt_id:
                    return attempt
        return None
    
    async def _create_settlement_offer(
        self,
        violation_id: str,
        offered_amount: Decimal,
        demanded_amount: Decimal
    ) -> str:
        """Create a settlement offer."""
        offer_id = str(uuid4())
        
        offer = SettlementOffer(
            offer_id=offer_id,
            violation_id=violation_id,
            offered_amount=offered_amount,
            demanded_amount=demanded_amount,
            terms={
                "payment_deadline": (datetime.now() + timedelta(days=30)).isoformat(),
                "confidentiality": True,
                "no_admission": True,
                "future_compliance": True
            },
            offer_date=datetime.now(),
            response_deadline=datetime.now() + timedelta(days=14),
            status="pending",
            negotiation_history=[]
        )
        
        if violation_id not in self.settlement_offers:
            self.settlement_offers[violation_id] = []
        self.settlement_offers[violation_id].append(offer)
        
        return offer_id
    
    async def accept_settlement_offer(
        self,
        offer_id: str,
        acceptance_terms: Optional[Dict[str, Any]] = None
    ) -> bool:
        """Accept a settlement offer."""
        try:
            # Find the offer
            offer = None
            for offers in self.settlement_offers.values():
                for o in offers:
                    if o.offer_id == offer_id:
                        offer = o
                        break
                if offer:
                    break
            
            if not offer:
                self.logger.error(f"Settlement offer {offer_id} not found")
                return False
            
            # Accept the offer
            offer.status = "accepted"
            offer.negotiation_history.append({
                "action": "accepted",
                "date": datetime.now().isoformat(),
                "terms": acceptance_terms or {}
            })
            
            # Update related recovery attempt
            violation_attempts = self.recovery_attempts.get(offer.violation_id, [])
            for attempt in violation_attempts:
                if attempt.outcome == RecoveryOutcome.SETTLED:
                    attempt.recovery_amount = offer.offered_amount
                    attempt.response_details["settlement_accepted"] = True
                    break
            
            self.logger.info(f"Settlement offer {offer_id} accepted for ${offer.offered_amount}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error accepting settlement offer: {e}")
            return False
    
    async def get_violation_status(self, violation_id: str) -> Optional[Dict[str, Any]]:
        """Get current status of a violation."""
        violation = self.violation_records.get(violation_id)
        if not violation:
            return None
        
        attempts = self.recovery_attempts.get(violation_id, [])
        
        # Calculate totals
        total_recovery = sum(attempt.recovery_amount for attempt in attempts)
        total_costs = sum(attempt.costs for attempt in attempts)
        net_recovery = total_recovery - total_costs
        
        # Get latest attempt
        latest_attempt = max(attempts, key=lambda a: a.initiated_date) if attempts else None
        
        return {
            "violation_id": violation_id,
            "severity": violation.severity.value,
            "estimated_damage": float(violation.estimated_damage),
            "total_recovery": float(total_recovery),
            "total_costs": float(total_costs),
            "net_recovery": float(net_recovery),
            "attempts_count": len(attempts),
            "latest_action": latest_attempt.action_taken.value if latest_attempt else None,
            "latest_outcome": latest_attempt.outcome.value if latest_attempt else None,
            "recovery_rate": float(total_recovery / violation.estimated_damage) if violation.estimated_damage > 0 else 0,
            "created_at": violation.detected_date.isoformat()
        }
    
    async def get_creator_recovery_report(
        self,
        creator_id: str,
        period_days: int = 90
    ) -> RecoveryReport:
        """Generate comprehensive recovery report for creator."""
        end_date = datetime.now()
        start_date = end_date - timedelta(days=period_days)
        
        # Get creator violations in period
        creator_violations = [
            violation for violation in self.violation_records.values()
            if violation.creator_id == creator_id and start_date <= violation.detected_date <= end_date
        ]
        
        if not creator_violations:
            return RecoveryReport(
                report_id=str(uuid4()),
                creator_id=creator_id,
                reporting_period=(start_date, end_date),
                total_violations=0,
                violations_by_severity={},
                total_damage_claimed=Decimal("0"),
                total_amount_recovered=Decimal("0"),
                recovery_rate=0.0,
                average_resolution_time=0.0,
                successful_recoveries=0,
                pending_recoveries=0,
                failed_recoveries=0,
                total_costs=Decimal("0"),
                net_recovery=Decimal("0"),
                roi=0.0,
                top_platforms=[],
                effectiveness_by_action={},
                recommendations=[]
            )
        
        # Calculate metrics
        total_violations = len(creator_violations)
        
        # Violations by severity
        violations_by_severity = {}
        for violation in creator_violations:
            violations_by_severity[violation.severity] = violations_by_severity.get(violation.severity, 0) + 1
        
        # Financial metrics
        total_damage_claimed = sum(v.estimated_damage for v in creator_violations)
        
        # Recovery metrics from attempts
        all_attempts = []
        for violation in creator_violations:
            attempts = self.recovery_attempts.get(violation.violation_id, [])
            all_attempts.extend(attempts)
        
        total_amount_recovered = sum(attempt.recovery_amount for attempt in all_attempts)
        total_costs = sum(attempt.costs for attempt in all_attempts)
        net_recovery = total_amount_recovered - total_costs
        
        recovery_rate = float(total_amount_recovered / total_damage_claimed) if total_damage_claimed > 0 else 0.0
        roi = float(net_recovery / total_costs) if total_costs > 0 else 0.0
        
        # Success metrics
        successful_recoveries = len([a for a in all_attempts if a.outcome in [
            RecoveryOutcome.PARTIAL_RECOVERY, RecoveryOutcome.FULL_RECOVERY, RecoveryOutcome.SETTLED
        ]])
        pending_recoveries = len([a for a in all_attempts if a.outcome == RecoveryOutcome.PENDING])
        failed_recoveries = len([a for a in all_attempts if a.outcome in [
            RecoveryOutcome.REJECTED, RecoveryOutcome.IGNORED
        ]])
        
        # Platform analysis
        platform_counts = {}
        for violation in creator_violations:
            platform_counts[violation.platform] = platform_counts.get(violation.platform, 0) + 1
        
        top_platforms = [
            {"platform": platform, "violations": count}
            for platform, count in sorted(platform_counts.items(), key=lambda x: x[1], reverse=True)[:5]
        ]
        
        # Action effectiveness
        effectiveness_by_action = {}
        for action in RecoveryAction:
            action_attempts = [a for a in all_attempts if a.action_taken == action]
            if action_attempts:
                successful = len([a for a in action_attempts if a.outcome in [
                    RecoveryOutcome.PARTIAL_RECOVERY, RecoveryOutcome.FULL_RECOVERY, RecoveryOutcome.SETTLED
                ]])
                effectiveness_by_action[action] = {
                    "attempts": len(action_attempts),
                    "successful": successful,
                    "success_rate": successful / len(action_attempts),
                    "average_recovery": float(sum(a.recovery_amount for a in action_attempts) / len(action_attempts))
                }
        
        # Generate recommendations
        recommendations = await self._generate_recovery_recommendations(
            creator_violations, all_attempts, effectiveness_by_action
        )
        
        return RecoveryReport(
            report_id=str(uuid4()),
            creator_id=creator_id,
            reporting_period=(start_date, end_date),
            total_violations=total_violations,
            violations_by_severity=violations_by_severity,
            total_damage_claimed=total_damage_claimed,
            total_amount_recovered=total_amount_recovered,
            recovery_rate=recovery_rate,
            average_resolution_time=0.0,  # Would calculate from attempt data
            successful_recoveries=successful_recoveries,
            pending_recoveries=pending_recoveries,
            failed_recoveries=failed_recoveries,
            total_costs=total_costs,
            net_recovery=net_recovery,
            roi=roi,
            top_platforms=top_platforms,
            effectiveness_by_action=effectiveness_by_action,
            recommendations=recommendations
        )
    
    async def _generate_recovery_recommendations(
        self,
        violations: List[ViolationRecord],
        attempts: List[RecoveryAttempt],
        effectiveness: Dict[RecoveryAction, Dict[str, Any]]
    ) -> List[str]:
        """Generate recovery strategy recommendations."""
        recommendations = []
        
        if not violations:
            return ["No violations detected - maintain monitoring"]
        
        # Recovery rate analysis
        successful_attempts = [a for a in attempts if a.outcome in [
            RecoveryOutcome.PARTIAL_RECOVERY, RecoveryOutcome.FULL_RECOVERY, RecoveryOutcome.SETTLED
        ]]
        
        if len(attempts) > 0:
            success_rate = len(successful_attempts) / len(attempts)
            if success_rate < 0.5:
                recommendations.append("⚠️ Low recovery success rate - review evidence collection process")
        
        # Platform analysis
        platform_counts = {}
        for violation in violations:
            platform_counts[violation.platform] = platform_counts.get(violation.platform, 0) + 1
        
        if platform_counts:
            top_platform = max(platform_counts, key=platform_counts.get)
            if platform_counts[top_platform] > len(violations) * 0.5:
                recommendations.append(f"🎯 Focus on {top_platform} - represents majority of violations")
        
        # Severity analysis
        critical_violations = [v for v in violations if v.severity == ViolationSeverity.CRITICAL]
        if len(critical_violations) > 0:
            recommendations.append("🚨 Prioritize critical violations for immediate legal action")
        
        # Action effectiveness
        if effectiveness:
            best_action = max(effectiveness.keys(), key=lambda k: effectiveness[k]["success_rate"])
            worst_action = min(effectiveness.keys(), key=lambda k: effectiveness[k]["success_rate"])
            
            if effectiveness[best_action]["success_rate"] > 0.8:
                recommendations.append(f"✅ {best_action.value.replace('_', ' ')} showing high success - expand usage")
            
            if effectiveness[worst_action]["success_rate"] < 0.3:
                recommendations.append(f"❌ {worst_action.value.replace('_', ' ')} showing poor results - review strategy")
        
        return recommendations[:5]


# Global instance
_violation_revenue_recovery = None


async def get_violation_revenue_recovery() -> ViolationRevenueRecovery:
    """Get the global violation revenue recovery instance."""
    global _violation_revenue_recovery
    
    if _violation_revenue_recovery is None:
        _violation_revenue_recovery = ViolationRevenueRecovery()
        await _violation_revenue_recovery.initialize()
    
    return _violation_revenue_recovery


# Example usage
async def main():
    """Example usage of ViolationRevenueRecovery."""
    recovery_system = await get_violation_revenue_recovery()
    
    creator_id = "creator_123"
    
    # Register a violation
    violation_id = await recovery_system.register_violation(
        content_id="content_456",
        creator_id=creator_id,
        violation_type="copyright_infringement",
        violation_url="https://pirate-site.com/stolen-content",
        platform="unknown",
        violator_info={
            "site": "pirate-site.com",
            "operator": "unknown",
            "commercial_operation": True,
            "repeat_offender": False
        },
        evidence_package={
            "original_content_proof": "blockchain_timestamp",
            "similarity_score": 0.98,
            "screenshots": ["evidence1.jpg", "evidence2.jpg"],
            "metadata_comparison": "match"
        },
        estimated_damage=Decimal("500.00"),
        metadata={"detection_method": "automated_scan"}
    )
    
    print(f"Registered violation: {violation_id}")
    
    # Wait for processing
    await asyncio.sleep(2)
    
    # Check violation status
    status = await recovery_system.get_violation_status(violation_id)
    if status:
        print(f"\n📋 Violation Status:")
        print(f"Severity: {status['severity']}")
        print(f"Estimated Damage: ${status['estimated_damage']:.2f}")
        print(f"Total Recovery: ${status['total_recovery']:.2f}")
        print(f"Net Recovery: ${status['net_recovery']:.2f}")
        print(f"Recovery Rate: {status['recovery_rate']:.1%}")
        print(f"Attempts: {status['attempts_count']}")
        print(f"Latest Action: {status['latest_action']}")
        print(f"Latest Outcome: {status['latest_outcome']}")
    
    # Get comprehensive recovery report
    report = await recovery_system.get_creator_recovery_report(creator_id, period_days=30)
    
    print(f"\n📊 Recovery Report (Last 30 days):")
    print(f"Total Violations: {report.total_violations}")
    print(f"Total Damage Claimed: ${report.total_damage_claimed:.2f}")
    print(f"Total Amount Recovered: ${report.total_amount_recovered:.2f}")
    print(f"Net Recovery: ${report.net_recovery:.2f}")
    print(f"Recovery Rate: {report.recovery_rate:.1%}")
    print(f"ROI: {report.roi:.1f}x")
    
    print(f"\nViolations by Severity:")
    for severity, count in report.violations_by_severity.items():
        print(f"  • {severity.value.title()}: {count}")
    
    print(f"\nTop Platforms:")
    for platform_data in report.top_platforms:
        print(f"  • {platform_data['platform']}: {platform_data['violations']} violations")
    
    print(f"\nAction Effectiveness:")
    for action, data in report.effectiveness_by_action.items():
        print(f"  • {action.value.replace('_', ' ').title()}: {data['success_rate']:.1%} success rate")
    
    print(f"\n💡 Recommendations:")
    for i, rec in enumerate(report.recommendations, 1):
        print(f"  {i}. {rec}")


if __name__ == "__main__":
    asyncio.run(main())