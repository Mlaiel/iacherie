"""⬆️ Escalation Manager - Enterprise ML Infrastructure
=====================================================
Module: ml/monitoring/escalation_manager.py
Author: Fahed Mlaiel (mlaiel@live.de)
=====================================================

⚠️  PROPRIÉTÉ INTELLECTUELLE EXCLUSIVE - FAHED MLAIEL ⚠️
(c) 2025 Fahed Mlaiel. Tous droits réservés.
Contact: mlaiel@live.de

🎯 INTELLIGENT ESCALATION MANAGEMENT SYSTEM
Intelligent escalation management for critical model issues
- Multi-tier escalation workflows
- Creator-priority based escalation
- Automated escalation triggers
- Executive dashboard integration
"""

import asyncio
import logging
import time
import uuid
from typing import Dict, List, Optional, Any, Union, Tuple, Callable
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
import json
from pathlib import Path

logger = logging.getLogger(__name__)


class EscalationLevel(Enum):
    """Escalation levels"""
    L1_SUPPORT = "l1_support"
    L2_ENGINEERING = "l2_engineering"
    L3_SENIOR = "l3_senior"
    L4_EXECUTIVE = "l4_executive"
    L5_EMERGENCY = "l5_emergency"


class EscalationTrigger(Enum):
    """Escalation triggers"""
    TIME_BASED = "time_based"
    SEVERITY_BASED = "severity_based"
    BUSINESS_IMPACT = "business_impact"
    CREATOR_PRIORITY = "creator_priority"
    MANUAL = "manual"
    SLA_VIOLATION = "sla_violation"
    MULTIPLE_FAILURES = "multiple_failures"


class TeamMemberRole(Enum):
    """Team member roles"""
    SUPPORT_AGENT = "support_agent"
    ML_ENGINEER = "ml_engineer"
    SENIOR_ENGINEER = "senior_engineer"
    TEAM_LEAD = "team_lead"
    ENGINEERING_MANAGER = "engineering_manager"
    VP_ENGINEERING = "vp_engineering"
    CTO = "cto"
    CEO = "ceo"


class EscalationStatus(Enum):
    """Escalation status"""
    PENDING = "pending"
    ACKNOWLEDGED = "acknowledged"
    IN_PROGRESS = "in_progress"
    RESOLVED = "resolved"
    DEESCALATED = "de_escalated"


@dataclass
class TeamMember:
    """Team member information"""
    member_id: str
    name: str
    role: TeamMemberRole
    contact_info: Dict[str, str]
    escalation_level: EscalationLevel
    availability_schedule: Dict[str, List[str]] = field(default_factory=dict)
    specializations: List[str] = field(default_factory=list)
    current_load: int = 0
    max_concurrent_escalations: int = 5


@dataclass
class EscalationRule:
    """Escalation rule definition"""
    rule_id: str
    name: str
    trigger: EscalationTrigger
    conditions: Dict[str, Any]
    escalation_level: EscalationLevel
    timeout_minutes: int
    enabled: bool = True
    creator_types: List[str] = field(default_factory=list)
    business_hours_only: bool = False


@dataclass
class EscalationPath:
    """Escalation path definition"""
    path_id: str
    name: str
    levels: List[EscalationLevel]
    level_timeouts: Dict[EscalationLevel, int]  # minutes
    creator_specific: bool = False
    business_critical: bool = False


@dataclass
class EscalationEvent:
    """Escalation event record"""
    event_id: str
    incident_id: str
    escalation_level: EscalationLevel
    trigger: EscalationTrigger
    assigned_to: Optional[str] = None
    status: EscalationStatus = EscalationStatus.PENDING
    created_at: datetime = field(default_factory=datetime.utcnow)
    acknowledged_at: Optional[datetime] = None
    resolved_at: Optional[datetime] = None
    escalation_reason: str = ""
    business_impact_score: float = 0.0
    creator_impact: Dict[str, Any] = field(default_factory=dict)
    communication_log: List[Dict[str, Any]] = field(default_factory=list)


class EscalationManager:
    """Enterprise Escalation Manager"""
    
    def __init__(self, config -> None: Optional[Dict[str, Any]] = None) -> None:
        self.config = config or {}
        
        # Storage
        self.team_members: Dict[str, TeamMember] = {}
        self.escalation_rules: Dict[str, EscalationRule] = {}
        self.escalation_paths: Dict[str, EscalationPath] = {}
        self.escalation_events: Dict[str, EscalationEvent] = {}
        
        # Configuration
        self.business_hours_start = self.config.get('business_hours_start', 9)  # 9 AM
        self.business_hours_end = self.config.get('business_hours_end', 17)    # 5 PM
        self.weekend_escalation_enabled = self.config.get('weekend_escalation_enabled', True)
        self.auto_assignment_enabled = self.config.get('auto_assignment_enabled', True)
        
        # Creator priority weights
        self.creator_priority_weights = {
            'musician': 1.2,
            'blogger': 1.0,
            'photographer': 1.1,
            'influencer': 1.3,
            'comedian': 1.0
        }
        
        # Performance tracking
        self.escalation_metrics = {
            'total_escalations': 0,
            'resolved_escalations': 0,
            'average_resolution_time': 0.0,
            'sla_violations': 0,
            'auto_resolved_escalations': 0,
            'executive_escalations': 0,
            'weekend_escalations': 0
        }
        
        # Initialize default data
        self._initialize_team_members()
        self._initialize_escalation_rules()
        self._initialize_escalation_paths()
        
        logger.info("⬆️ Escalation Manager initialized")
    
    def _initialize_team_members(self) -> None:
        """Initialize default team members"""
        team_members = [
            TeamMember(
                member_id="support_001",
                name="Sarah Chen",
                role=TeamMemberRole.SUPPORT_AGENT,
                contact_info={"email": "sarah.chen@ainflue.com", "phone": "+1-555-0101"},
                escalation_level=EscalationLevel.L1_SUPPORT,
                specializations=["general_support", "creator_onboarding"]
            ),
            TeamMember(
                member_id="ml_engineer_001",
                name="Alex Rodriguez",
                role=TeamMemberRole.ML_ENGINEER,
                contact_info={"email": "alex.rodriguez@ainflue.com", "phone": "+1-555-0102"},
                escalation_level=EscalationLevel.L2_ENGINEERING,
                specializations=["model_deployment", "performance_optimization"]
            ),
            TeamMember(
                member_id="senior_001",
                name="Dr. Emily Watson",
                role=TeamMemberRole.SENIOR_ENGINEER,
                contact_info={"email": "emily.watson@ainflue.com", "phone": "+1-555-0103"},
                escalation_level=EscalationLevel.L3_SENIOR,
                specializations=["ml_architecture", "incident_resolution", "creator_experience"]
            ),
            TeamMember(
                member_id="team_lead_001",
                name="Michael Kim",
                role=TeamMemberRole.TEAM_LEAD,
                contact_info={"email": "michael.kim@ainflue.com", "phone": "+1-555-0104"},
                escalation_level=EscalationLevel.L3_SENIOR,
                specializations=["team_coordination", "business_alignment"]
            ),
            TeamMember(
                member_id="eng_manager_001",
                name="Lisa Thompson",
                role=TeamMemberRole.ENGINEERING_MANAGER,
                contact_info={"email": "lisa.thompson@ainflue.com", "phone": "+1-555-0105"},
                escalation_level=EscalationLevel.L4_EXECUTIVE,
                specializations=["strategic_planning", "resource_allocation"]
            ),
            TeamMember(
                member_id="vp_eng_001",
                name="Robert Chen",
                role=TeamMemberRole.VP_ENGINEERING,
                contact_info={"email": "robert.chen@ainflue.com", "phone": "+1-555-0106"},
                escalation_level=EscalationLevel.L4_EXECUTIVE,
                specializations=["executive_decisions", "business_strategy"]
            ),
            TeamMember(
                member_id="cto_001",
                name="Dr. Jennifer Park",
                role=TeamMemberRole.CTO,
                contact_info={"email": "jennifer.park@ainflue.com", "phone": "+1-555-0107"},
                escalation_level=EscalationLevel.L5_EMERGENCY,
                specializations=["technical_strategy", "crisis_management"]
            )
        ]
        
        for member in team_members:
            self.team_members[member.member_id] = member
    
    def _initialize_escalation_rules(self) -> None:
        """Initialize default escalation rules"""
        rules = [
            EscalationRule(
                rule_id="critical_severity",
                name="Critical Severity Auto-Escalation",
                trigger=EscalationTrigger.SEVERITY_BASED,
                conditions={"severity": "critical"},
                escalation_level=EscalationLevel.L3_SENIOR,
                timeout_minutes=15
            ),
            EscalationRule(
                rule_id="high_business_impact",
                name="High Business Impact Escalation",
                trigger=EscalationTrigger.BUSINESS_IMPACT,
                conditions={"business_impact_score": 0.8},
                escalation_level=EscalationLevel.L4_EXECUTIVE,
                timeout_minutes=30
            ),
            EscalationRule(
                rule_id="creator_priority_escalation",
                name="High-Priority Creator Escalation",
                trigger=EscalationTrigger.CREATOR_PRIORITY,
                conditions={"affected_creators": 100, "creator_types": ["influencer", "musician"]},
                escalation_level=EscalationLevel.L3_SENIOR,
                timeout_minutes=20
            ),
            EscalationRule(
                rule_id="sla_violation",
                name="SLA Violation Escalation",
                trigger=EscalationTrigger.SLA_VIOLATION,
                conditions={"sla_breach_minutes": 30},
                escalation_level=EscalationLevel.L2_ENGINEERING,
                timeout_minutes=10
            ),
            EscalationRule(
                rule_id="multiple_failures",
                name="Multiple System Failures",
                trigger=EscalationTrigger.MULTIPLE_FAILURES,
                conditions={"failure_count": 3, "time_window_minutes": 15},
                escalation_level=EscalationLevel.L4_EXECUTIVE,
                timeout_minutes=5
            ),
            EscalationRule(
                rule_id="l1_timeout",
                name="L1 Support Timeout",
                trigger=EscalationTrigger.TIME_BASED,
                conditions={"level": "l1_support", "timeout_minutes": 30},
                escalation_level=EscalationLevel.L2_ENGINEERING,
                timeout_minutes=30
            ),
            EscalationRule(
                rule_id="l2_timeout",
                name="L2 Engineering Timeout",
                trigger=EscalationTrigger.TIME_BASED,
                conditions={"level": "l2_engineering", "timeout_minutes": 60},
                escalation_level=EscalationLevel.L3_SENIOR,
                timeout_minutes=60
            )
        ]
        
        for rule in rules:
            self.escalation_rules[rule.rule_id] = rule
    
    def _initialize_escalation_paths(self) -> None:
        """Initialize escalation paths"""
        paths = [
            EscalationPath(
                path_id="standard_path",
                name="Standard Escalation Path",
                levels=[
                    EscalationLevel.L1_SUPPORT,
                    EscalationLevel.L2_ENGINEERING,
                    EscalationLevel.L3_SENIOR,
                    EscalationLevel.L4_EXECUTIVE
                ],
                level_timeouts={
                    EscalationLevel.L1_SUPPORT: 30,
                    EscalationLevel.L2_ENGINEERING: 60,
                    EscalationLevel.L3_SENIOR: 120,
                    EscalationLevel.L4_EXECUTIVE: 240
                }
            ),
            EscalationPath(
                path_id="creator_priority_path",
                name="Creator Priority Escalation Path",
                levels=[
                    EscalationLevel.L2_ENGINEERING,
                    EscalationLevel.L3_SENIOR,
                    EscalationLevel.L4_EXECUTIVE
                ],
                level_timeouts={
                    EscalationLevel.L2_ENGINEERING: 20,
                    EscalationLevel.L3_SENIOR: 45,
                    EscalationLevel.L4_EXECUTIVE: 90
                },
                creator_specific=True
            ),
            EscalationPath(
                path_id="emergency_path",
                name="Emergency Escalation Path",
                levels=[
                    EscalationLevel.L3_SENIOR,
                    EscalationLevel.L4_EXECUTIVE,
                    EscalationLevel.L5_EMERGENCY
                ],
                level_timeouts={
                    EscalationLevel.L3_SENIOR: 15,
                    EscalationLevel.L4_EXECUTIVE: 30,
                    EscalationLevel.L5_EMERGENCY: 60
                },
                business_critical=True
            )
        ]
        
        for path in paths:
            self.escalation_paths[path.path_id] = path
    
    async def evaluate_escalation(
        self,
        incident_id: str,
        incident_data: Dict[str, Any]
    ) -> List[str]:
        """Evaluate if incident should be escalated"""
        try:
            escalation_events = []
            
            # Check all escalation rules
            for rule in self.escalation_rules.values():
                if not rule.enabled:
                    continue
                
                should_escalate = await self._evaluate_rule(rule, incident_data)
                
                if should_escalate:
                    event_id = await self._create_escalation_event(
                        incident_id, rule, incident_data
                    )
                    if event_id:
                        escalation_events.append(event_id)
            
            # Execute escalations
            for event_id in escalation_events:
                await self._execute_escalation(event_id)
            
            logger.info(f"✅ Escalation evaluation completed: {len(escalation_events)} escalations triggered")
            return escalation_events
            
        except Exception as e:
            logger.error(f"❌ Error evaluating escalation: {e}")
            return []
    
    async def _evaluate_rule(
        self,
        rule: EscalationRule,
        incident_data: Dict[str, Any]
    ) -> bool:
        """Evaluate if escalation rule should trigger"""
        try:
            conditions = rule.conditions
            
            if rule.trigger == EscalationTrigger.SEVERITY_BASED:
                incident_severity = incident_data.get('severity', '').lower()
                required_severity = conditions.get('severity', '').lower()
                return incident_severity == required_severity
            
            elif rule.trigger == EscalationTrigger.BUSINESS_IMPACT:
                business_impact = incident_data.get('business_impact_score', 0)
                threshold = conditions.get('business_impact_score', 1.0)
                return business_impact >= threshold
            
            elif rule.trigger == EscalationTrigger.CREATOR_PRIORITY:
                affected_creators = incident_data.get('affected_creators', 0)
                creator_threshold = conditions.get('affected_creators', 0)
                
                creator_types = incident_data.get('creator_types', [])
                required_types = conditions.get('creator_types', [])
                
                return (affected_creators >= creator_threshold and 
                       any(ct in required_types for ct in creator_types))
            
            elif rule.trigger == EscalationTrigger.SLA_VIOLATION:
                incident_age_minutes = incident_data.get('age_minutes', 0)
                sla_breach_threshold = conditions.get('sla_breach_minutes', 0)
                return incident_age_minutes >= sla_breach_threshold
            
            elif rule.trigger == EscalationTrigger.MULTIPLE_FAILURES:
                failure_count = incident_data.get('related_failures', 0)
                required_count = conditions.get('failure_count', 1)
                return failure_count >= required_count
            
            elif rule.trigger == EscalationTrigger.TIME_BASED:
                current_level = incident_data.get('current_escalation_level', '').lower()
                rule_level = conditions.get('level', '').lower()
                timeout_minutes = conditions.get('timeout_minutes', 0)
                age_at_level = incident_data.get('age_at_current_level_minutes', 0)
                
                return (current_level == rule_level and 
                       age_at_level >= timeout_minutes)
            
            return False
            
        except Exception as e:
            logger.error(f"❌ Error evaluating rule {rule.rule_id}: {e}")
            return False
    
    async def _create_escalation_event(
        self,
        incident_id: str,
        rule: EscalationRule,
        incident_data: Dict[str, Any]
    ) -> Optional[str]:
        """Create escalation event"""
        try:
            event_id = str(uuid.uuid4())
            
            # Calculate business impact score
            business_impact = await self._calculate_business_impact(incident_data)
            
            # Extract creator impact
            creator_impact = {
                'affected_creators': incident_data.get('affected_creators', 0),
                'primary_creator_types': incident_data.get('creator_types', []),
                'revenue_impact': incident_data.get('revenue_impact', 0)
            }
            
            event = EscalationEvent(
                event_id=event_id,
                incident_id=incident_id,
                escalation_level=rule.escalation_level,
                trigger=rule.trigger,
                escalation_reason=f"Rule triggered: {rule.name}",
                business_impact_score=business_impact,
                creator_impact=creator_impact
            )
            
            self.escalation_events[event_id] = event
            self.escalation_metrics['total_escalations'] += 1
            
            # Track weekend escalations
            if datetime.utcnow().weekday() >= 5:  # Saturday or Sunday
                self.escalation_metrics['weekend_escalations'] += 1
            
            # Track executive escalations
            if rule.escalation_level in [EscalationLevel.L4_EXECUTIVE, EscalationLevel.L5_EMERGENCY]:
                self.escalation_metrics['executive_escalations'] += 1
            
            logger.info(f"📋 Escalation event created: {event_id} (Level: {rule.escalation_level.value})")
            return event_id
            
        except Exception as e:
            logger.error(f"❌ Error creating escalation event: {e}")
            return None
    
    async def _execute_escalation(self, event_id -> None: str) -> None:
        """Execute escalation event"""
        try:
            event = self.escalation_events[event_id]
            
            # Find appropriate team member
            assigned_member = await self._assign_team_member(event)
            
            if assigned_member:
                event.assigned_to = assigned_member.member_id
                assigned_member.current_load += 1
                
                # Send notification
                await self._send_escalation_notification(event, assigned_member)
                
                # Start timeout monitoring
                asyncio.create_task(self._monitor_escalation_timeout(event_id))
                
                logger.info(f"✅ Escalation executed: {event_id} → {assigned_member.name}")
            else:
                logger.warning(f"⚠️ No available team member for escalation: {event_id}")
                # Escalate to next level
                await self._auto_escalate_to_next_level(event_id)
                
        except Exception as e:
            logger.error(f"❌ Error executing escalation: {e}")
    
    async def _assign_team_member(self, event: EscalationEvent) -> Optional[TeamMember]:
        """Assign appropriate team member to escalation"""
        try:
            # Filter team members by escalation level
            eligible_members = [
                member for member in self.team_members.values()
                if member.escalation_level == event.escalation_level
            ]
            
            if not eligible_members:
                return None
            
            # Filter by availability
            available_members = [
                member for member in eligible_members
                if member.current_load < member.max_concurrent_escalations
            ]
            
            if not available_members:
                # All members at this level are busy, escalate to next level
                return None
            
            # Check business hours for non-emergency escalations
            if (event.escalation_level != EscalationLevel.L5_EMERGENCY and
                not self._is_business_hours()):
                
                # Filter to members available outside business hours
                after_hours_members = [
                    member for member in available_members
                    if 'after_hours' in member.specializations
                ]
                
                if after_hours_members:
                    available_members = after_hours_members
            
            # Prioritize by specialization match
            creator_types = event.creator_impact.get('primary_creator_types', [])
            
            specialized_members = []
            for member in available_members:
                for creator_type in creator_types:
                    if creator_type in member.specializations:
                        specialized_members.append(member)
                        break
            
            if specialized_members:
                available_members = specialized_members
            
            # Select member with lowest current load
            selected_member = min(available_members, key=lambda m: m.current_load)
            
            return selected_member
            
        except Exception as e:
            logger.error(f"❌ Error assigning team member: {e}")
            return None
    
    async def _send_escalation_notification(
        self,
        event -> None: EscalationEvent,
        assigned_member -> None: TeamMember
    ) -> None:
        """Send escalation notification"""
        try:
            message = f"""
            🚨 ESCALATION ALERT 🚨
            
            Incident ID: {event.incident_id}
            Escalation Level: {event.escalation_level.value}
            Trigger: {event.trigger.value}
            Reason: {event.escalation_reason}
            
            Business Impact Score: {event.business_impact_score:.2f}
            Creator Impact: {event.creator_impact}
            
            Assigned to: {assigned_member.name} ({assigned_member.role.value})
            
            Please acknowledge within 15 minutes.
            """
            
            # Log notification (in practice, would send via email/SMS/Slack)
            logger.info(f"📧 Escalation notification sent to {assigned_member.name}")
            
            # Record communication
            event.communication_log.append({
                'timestamp': datetime.utcnow().isoformat(),
                'type': 'notification_sent',
                'recipient': assigned_member.member_id,
                'method': 'email'
            })
            
        except Exception as e:
            logger.error(f"❌ Error sending escalation notification: {e}")
    
    async def acknowledge_escalation(
        self,
        event_id: str,
        acknowledger_id: str,
        estimated_resolution_time: Optional[int] = None
    ) -> bool:
        """Acknowledge escalation"""
        try:
            if event_id not in self.escalation_events:
                return False
            
            event = self.escalation_events[event_id]
            
            if event.status != EscalationStatus.PENDING:
                return False
            
            event.status = EscalationStatus.ACKNOWLEDGED
            event.acknowledged_at = datetime.utcnow()
            
            # Record acknowledgment
            event.communication_log.append({
                'timestamp': datetime.utcnow().isoformat(),
                'type': 'acknowledged',
                'acknowledger': acknowledger_id,
                'estimated_resolution_time': estimated_resolution_time
            })
            
            logger.info(f"✅ Escalation acknowledged: {event_id} by {acknowledger_id}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error acknowledging escalation: {e}")
            return False
    
    async def resolve_escalation(
        self,
        event_id: str,
        resolver_id: str,
        resolution_details: str
    ) -> bool:
        """Resolve escalation"""
        try:
            if event_id not in self.escalation_events:
                return False
            
            event = self.escalation_events[event_id]
            event.status = EscalationStatus.RESOLVED
            event.resolved_at = datetime.utcnow()
            
            # Calculate resolution time
            resolution_time = (event.resolved_at - event.created_at).total_seconds() / 60
            
            # Update metrics
            self.escalation_metrics['resolved_escalations'] += 1
            
            # Update average resolution time
            total_resolved = self.escalation_metrics['resolved_escalations']
            current_avg = self.escalation_metrics['average_resolution_time']
            new_avg = (current_avg * (total_resolved - 1) + resolution_time) / total_resolved
            self.escalation_metrics['average_resolution_time'] = new_avg
            
            # Reduce assigned member's load
            if event.assigned_to and event.assigned_to in self.team_members:
                member = self.team_members[event.assigned_to]
                member.current_load = max(0, member.current_load - 1)
            
            # Record resolution
            event.communication_log.append({
                'timestamp': datetime.utcnow().isoformat(),
                'type': 'resolved',
                'resolver': resolver_id,
                'resolution_details': resolution_details,
                'resolution_time_minutes': resolution_time
            })
            
            logger.info(f"✅ Escalation resolved: {event_id} in {resolution_time:.1f} minutes")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error resolving escalation: {e}")
            return False
    
    async def _monitor_escalation_timeout(self, event_id -> None: str) -> None:
        """Monitor escalation timeout and auto-escalate if needed"""
        try:
            event = self.escalation_events[event_id]
            
            # Get timeout for this escalation level
            timeout_minutes = 30  # Default
            
            for rule in self.escalation_rules.values():
                if rule.escalation_level == event.escalation_level:
                    timeout_minutes = rule.timeout_minutes
                    break
            
            # Wait for timeout
            await asyncio.sleep(timeout_minutes * 60)
            
            # Check if still unresolved
            current_event = self.escalation_events.get(event_id)
            if (current_event and 
                current_event.status not in [EscalationStatus.RESOLVED, EscalationStatus.DEESCALATED]):
                
                # Auto-escalate to next level
                await self._auto_escalate_to_next_level(event_id)
                
        except Exception as e:
            logger.error(f"❌ Error monitoring escalation timeout: {e}")
    
    async def _auto_escalate_to_next_level(self, event_id -> None: str) -> None:
        """Auto-escalate to next level"""
        try:
            event = self.escalation_events[event_id]
            
            # Determine next escalation level
            level_order = [
                EscalationLevel.L1_SUPPORT,
                EscalationLevel.L2_ENGINEERING,
                EscalationLevel.L3_SENIOR,
                EscalationLevel.L4_EXECUTIVE,
                EscalationLevel.L5_EMERGENCY
            ]
            
            current_index = level_order.index(event.escalation_level)
            
            if current_index < len(level_order) - 1:
                next_level = level_order[current_index + 1]
                
                # Create new escalation event at next level
                new_event_id = str(uuid.uuid4())
                new_event = EscalationEvent(
                    event_id=new_event_id,
                    incident_id=event.incident_id,
                    escalation_level=next_level,
                    trigger=EscalationTrigger.TIME_BASED,
                    escalation_reason=f"Auto-escalated from {event.escalation_level.value} due to timeout",
                    business_impact_score=event.business_impact_score,
                    creator_impact=event.creator_impact
                )
                
                self.escalation_events[new_event_id] = new_event
                
                # Execute new escalation
                await self._execute_escalation(new_event_id)
                
                logger.warning(f"⬆️ Auto-escalated to {next_level.value}: {new_event_id}")
            else:
                logger.critical(f"🚨 Maximum escalation level reached for: {event_id}")
                
        except Exception as e:
            logger.error(f"❌ Error auto-escalating: {e}")
    
    async def _calculate_business_impact(self, incident_data: Dict[str, Any]) -> float:
        """Calculate business impact score"""
        try:
            impact_score = 0.0
            
            # Severity impact
            severity = incident_data.get('severity', 'low').lower()
            severity_scores = {
                'critical': 1.0,
                'high': 0.8,
                'medium': 0.5,
                'low': 0.2
            }
            impact_score += severity_scores.get(severity, 0.2) * 0.4
            
            # Creator impact
            affected_creators = incident_data.get('affected_creators', 0)
            creator_impact = min(affected_creators / 1000, 1.0)  # Normalize to 1000 creators
            impact_score += creator_impact * 0.3
            
            # Revenue impact
            revenue_impact = incident_data.get('revenue_impact', 0)
            revenue_impact_normalized = min(revenue_impact / 100000, 1.0)  # Normalize to $100k
            impact_score += revenue_impact_normalized * 0.3
            
            return min(impact_score, 1.0)
            
        except Exception as e:
            logger.error(f"❌ Error calculating business impact: {e}")
            return 0.5
    
    def _is_business_hours(self) -> bool:
        """Check if current time is within business hours"""
        try:
            now = datetime.utcnow()
            current_hour = now.hour
            
            # Check weekend
            if now.weekday() >= 5 and not self.weekend_escalation_enabled:
                return False
            
            # Check business hours
            return self.business_hours_start <= current_hour < self.business_hours_end
            
        except Exception as e:
            logger.error(f"❌ Error checking business hours: {e}")
            return True  # Default to business hours
    
    async def get_escalation_dashboard(self) -> Dict[str, Any]:
        """Get escalation dashboard data"""
        try:
            active_escalations = [
                event for event in self.escalation_events.values()
                if event.status not in [EscalationStatus.RESOLVED, EscalationStatus.DEESCALATED]
            ]
            
            # Group by level
            by_level = {}
            for event in active_escalations:
                level = event.escalation_level.value
                if level not in by_level:
                    by_level[level] = []
                by_level[level].append({
                    'event_id': event.event_id,
                    'incident_id': event.incident_id,
                    'assigned_to': event.assigned_to,
                    'age_minutes': (datetime.utcnow() - event.created_at).total_seconds() / 60,
                    'business_impact': event.business_impact_score
                })
            
            # Team member utilization
            team_utilization = {}
            for member in self.team_members.values():
                utilization = member.current_load / member.max_concurrent_escalations
                team_utilization[member.name] = {
                    'role': member.role.value,
                    'current_load': member.current_load,
                    'max_load': member.max_concurrent_escalations,
                    'utilization_percent': utilization * 100
                }
            
            return {
                'active_escalations_count': len(active_escalations),
                'escalations_by_level': by_level,
                'team_utilization': team_utilization,
                'metrics': self.escalation_metrics,
                'business_hours': self._is_business_hours()
            }
            
        except Exception as e:
            logger.error(f"❌ Error getting escalation dashboard: {e}")
            return {}
    
    async def get_metrics(self) -> Dict[str, Any]:
        """Get escalation metrics"""
        return {
            **self.escalation_metrics,
            'active_escalations': len([
                e for e in self.escalation_events.values()
                if e.status not in [EscalationStatus.RESOLVED, EscalationStatus.DEESCALATED]
            ]),
            'total_team_members': len(self.team_members),
            'total_rules': len(self.escalation_rules),
            'enabled_rules': len([r for r in self.escalation_rules.values() if r.enabled])
        }


# Global instance
escalation_manager = EscalationManager()


async def main() -> None:
    """Test the Escalation Manager"""
    manager = EscalationManager()
    
    print("⬆️ Testing Escalation Manager...")
    
    # Test incident data
    incident_data = {
        'severity': 'critical',
        'business_impact_score': 0.9,
        'affected_creators': 150,
        'creator_types': ['influencer', 'musician'],
        'age_minutes': 35,
        'current_escalation_level': 'l1_support',
        'age_at_current_level_minutes': 35
    }
    
    # Evaluate escalation
    escalations = await manager.evaluate_escalation("incident_001", incident_data)
    print(f"Escalations triggered: {len(escalations)}")
    
    # Wait for processing
    await asyncio.sleep(1)
    
    # Check dashboard
    dashboard = await manager.get_escalation_dashboard()
    print(f"Active escalations: {dashboard['active_escalations_count']}")
    
    # Acknowledge escalation
    if escalations:
        success = await manager.acknowledge_escalation(
            escalations[0], "senior_001", 30
        )
        print(f"Escalation acknowledged: {success}")
        
        # Resolve escalation
        success = await manager.resolve_escalation(
            escalations[0], "senior_001", "Issue resolved by model rollback"
        )
        print(f"Escalation resolved: {success}")
    
    # Get metrics
    metrics = await manager.get_metrics()
    print(f"Metrics: {metrics}")


if __name__ == "__main__":
    asyncio.run(main())