# WARNING: Potential SQL injection risk - use parameterized queries
"""
Incident Lifecycle Tracker for PagerDuty - Ainflue Platform
Complete incident timeline and state transition monitoring

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️  AVERTISSEMENT LÉGAL:
© 2025 Fahed Mlaiel <mlaiel@live.de>
TOUS DROITS RÉSERVÉS

🚨 PROTECTION INTELLECTUELLE:
- Code propriétaire de Fahed Mlaiel
- Utilisation commerciale INTERDITE sans autorisation écrite
- Reverse engineering STRICTEMENT INTERDIT
- Distribution INTERDITE sans licence explicite
- Violation = Poursuites judiciaires automatiques
"""

import logging
import json
import asyncio
from typing import Dict, Any, List, Optional, Set, Tuple
from dataclasses import dataclass, asdict, field
from datetime import datetime, timedelta
from enum import Enum
import uuid
import hashlib

logger = logging.getLogger(__name__)


class IncidentState(Enum):
    """Incident lifecycle states"""
    DETECTED = "detected"
    ACKNOWLEDGED = "acknowledged"
    INVESTIGATING = "investigating"
    IDENTIFIED = "identified"
    MONITORING = "monitoring"
    RESOLVED = "resolved"
    CLOSED = "closed"
    REOPENED = "reopened"


class StateTransitionTrigger(Enum):
    """What triggered a state transition"""
    AUTOMATIC = "automatic"
    MANUAL = "manual"
    SYSTEM = "system"
    TIMEOUT = "timeout"
    ESCALATION = "escalation"
    EXTERNAL = "external"


class ResourceType(Enum):
    """Types of resources allocated to incidents"""
    ENGINEER = "engineer"
    SRE = "sre"
    MANAGER = "manager"
    SUPPORT = "support"
    SECURITY = "security"
    LEGAL = "legal"
    COMMUNICATIONS = "communications"
    VENDOR_CONTACT = "vendor_contact"


class IncidentPriority(Enum):
    """Incident priority levels"""
    P1 = "p1"  # Critical
    P2 = "p2"  # High
    P3 = "p3"  # Medium
    P4 = "p4"  # Low


@dataclass
class StateTransition:
    """State transition record"""
    transition_id: str
    incident_id: str
    from_state: Optional[IncidentState]
    to_state: IncidentState
    timestamp: datetime
    trigger: StateTransitionTrigger
    actor: str
    reason: str
    duration_in_previous_state: Optional[float]  # seconds
    automated: bool
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ResourceAllocation:
    """Resource allocation record"""
    allocation_id: str
    incident_id: str
    resource_type: ResourceType
    resource_identifier: str
    allocated_at: datetime
    deallocated_at: Optional[datetime]
    utilization_percentage: float
    cost_per_hour: float
    total_cost: float
    notes: str
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class IncidentTimeline:
    """Complete incident timeline"""
    incident_id: str
    title: str
    description: str
    priority: IncidentPriority
    created_at: datetime
    first_detected_at: datetime
    first_acknowledged_at: Optional[datetime]
    first_resolved_at: Optional[datetime]
    closed_at: Optional[datetime]
    current_state: IncidentState
    total_duration: Optional[float]  # seconds
    time_to_acknowledge: Optional[float]  # seconds
    time_to_resolve: Optional[float]  # seconds
    affected_services: List[str]
    affected_users_count: int
    business_impact: str
    financial_impact: float
    state_transitions: List[StateTransition] = field(default_factory=list)
    resource_allocations: List[ResourceAllocation] = field(default_factory=list)
    timeline_events: List[Dict[str, Any]] = field(default_factory=list)
    sla_targets: Dict[str, float] = field(default_factory=dict)
    sla_breaches: List[Dict[str, Any]] = field(default_factory=list)
    post_mortem_required: bool = False
    post_mortem_completed: bool = False
    lessons_learned: List[str] = field(default_factory=list)
    preventive_actions: List[Dict[str, Any]] = field(default_factory=list)


@dataclass
class LifecycleMetrics:
    """Incident lifecycle metrics"""
    metric_id: str
    period_start: datetime
    period_end: datetime
    total_incidents: int
    incidents_by_priority: Dict[str, int]
    incidents_by_state: Dict[str, int]
    average_time_to_acknowledge: float
    average_time_to_resolve: float
    median_time_to_resolve: float
    p95_time_to_resolve: float
    sla_compliance_rate: float
    reopened_incidents_count: int
    escalated_incidents_count: int
    resource_utilization: Dict[ResourceType, float]
    total_incident_cost: float
    most_frequent_failure_modes: List[Dict[str, Any]]
    improvement_trends: Dict[str, float]


class IncidentLifecycleTracker:
    """
    Incident lifecycle tracking and optimization for Creator Economy
    Monitors complete incident journey from detection to closure
    """
    
    def __init__(self, pagerduty_client=None):
        """Initialize incident lifecycle tracker"""
        self.pagerduty_client = pagerduty_client
        self.active_incidents = {}
        self.completed_incidents = {}
        self.state_machine_rules = {}
        self.sla_targets = {}
        self.resource_pools = {}
        
        # Initialize configuration
        self._initialize_state_machine()
        self._initialize_sla_targets()
        self._initialize_resource_pools()
        
        # Configuration
        self.config = {
            "auto_state_transitions": True,
            "resource_cost_tracking": True,
            "sla_monitoring": True,
            "timeline_retention_days": 365,
            "metrics_calculation_interval": 3600,  # 1 hour
            "post_mortem_threshold": "p2",
            "auto_close_resolved_after_hours": 24
        }
        
        logger.info("Incident Lifecycle Tracker initialized")
    
    def _initialize_state_machine(self):
        """Initialize incident state machine rules"""
        self.state_machine_rules = {
            IncidentState.DETECTED: {
                "allowed_transitions": [IncidentState.ACKNOWLEDGED, IncidentState.INVESTIGATING],
                "auto_transition_timeout": 300,  # 5 minutes
                "auto_transition_target": IncidentState.ACKNOWLEDGED,
                "required_actions": ["assign_responder", "initial_assessment"]
            },
            IncidentState.ACKNOWLEDGED: {
                "allowed_transitions": [IncidentState.INVESTIGATING, IncidentState.RESOLVED],
                "auto_transition_timeout": 900,  # 15 minutes
                "auto_transition_target": IncidentState.INVESTIGATING,
                "required_actions": ["start_investigation"]
            },
            IncidentState.INVESTIGATING: {
                "allowed_transitions": [IncidentState.IDENTIFIED, IncidentState.RESOLVED, IncidentState.MONITORING],
                "auto_transition_timeout": None,
                "required_actions": ["root_cause_analysis", "impact_assessment"]
            },
            IncidentState.IDENTIFIED: {
                "allowed_transitions": [IncidentState.MONITORING, IncidentState.RESOLVED],
                "auto_transition_timeout": None,
                "required_actions": ["implement_fix", "verify_solution"]
            },
            IncidentState.MONITORING: {
                "allowed_transitions": [IncidentState.RESOLVED, IncidentState.INVESTIGATING],
                "auto_transition_timeout": 3600,  # 1 hour
                "auto_transition_target": IncidentState.RESOLVED,
                "required_actions": ["confirm_stability"]
            },
            IncidentState.RESOLVED: {
                "allowed_transitions": [IncidentState.CLOSED, IncidentState.REOPENED],
                "auto_transition_timeout": 86400,  # 24 hours
                "auto_transition_target": IncidentState.CLOSED,
                "required_actions": ["confirm_resolution", "update_stakeholders"]
            },
            IncidentState.CLOSED: {
                "allowed_transitions": [IncidentState.REOPENED],
                "auto_transition_timeout": None,
                "required_actions": ["complete_documentation", "schedule_post_mortem"]
            },
            IncidentState.REOPENED: {
                "allowed_transitions": [IncidentState.INVESTIGATING, IncidentState.IDENTIFIED],
                "auto_transition_timeout": None,
                "required_actions": ["reassess_situation", "reallocate_resources"]
            }
        }
    
    def _initialize_sla_targets(self):
        """Initialize SLA targets for Creator Economy"""
        self.sla_targets = {
            IncidentPriority.P1: {
                "time_to_acknowledge": 300,    # 5 minutes
                "time_to_resolve": 3600,       # 1 hour
                "time_to_communicate": 180,    # 3 minutes
                "escalation_threshold": 1800   # 30 minutes
            },
            IncidentPriority.P2: {
                "time_to_acknowledge": 900,    # 15 minutes
                "time_to_resolve": 14400,      # 4 hours
                "time_to_communicate": 600,    # 10 minutes
                "escalation_threshold": 7200   # 2 hours
            },
            IncidentPriority.P3: {
                "time_to_acknowledge": 1800,   # 30 minutes
                "time_to_resolve": 86400,      # 24 hours
                "time_to_communicate": 1800,   # 30 minutes
                "escalation_threshold": 43200  # 12 hours
            },
            IncidentPriority.P4: {
                "time_to_acknowledge": 3600,   # 1 hour
                "time_to_resolve": 259200,     # 72 hours
                "time_to_communicate": 3600,   # 1 hour
                "escalation_threshold": 86400  # 24 hours
            }
        }
    
    def _initialize_resource_pools(self):
        """Initialize resource pools with costs"""
        self.resource_pools = {
            ResourceType.ENGINEER: {
                "available_count": 10,
                "cost_per_hour": 100.0,
                "skills": ["backend", "frontend", "database", "infrastructure"]
            },
            ResourceType.SRE: {
                "available_count": 5,
                "cost_per_hour": 120.0,
                "skills": ["monitoring", "infrastructure", "automation", "performance"]
            },
            ResourceType.MANAGER: {
                "available_count": 3,
                "cost_per_hour": 150.0,
                "skills": ["coordination", "escalation", "communication"]
            },
            ResourceType.SUPPORT: {
                "available_count": 8,
                "cost_per_hour": 50.0,
                "skills": ["customer_communication", "documentation", "triage"]
            },
            ResourceType.SECURITY: {
                "available_count": 2,
                "cost_per_hour": 130.0,
                "skills": ["security_analysis", "compliance", "forensics"]
            },
            ResourceType.LEGAL: {
                "available_count": 1,
                "cost_per_hour": 200.0,
                "skills": ["compliance", "regulatory", "contracts"]
            },
            ResourceType.COMMUNICATIONS: {
                "available_count": 2,
                "cost_per_hour": 80.0,
                "skills": ["public_relations", "stakeholder_communication", "social_media"]
            }
        }
    
    async def start_incident_tracking(self, incident_data: Dict[str, Any]) -> Optional[IncidentTimeline]:
        """Start tracking new incident lifecycle"""
        try:
            # Create incident timeline
            timeline = IncidentTimeline(
                incident_id=incident_data.get("incident_id", str(uuid.uuid4())),
                title=incident_data.get("title", "Unknown Incident"),
                description=incident_data.get("description", ""),
                priority=IncidentPriority(incident_data.get("priority", "p3")),
                created_at=datetime.utcnow(),
                first_detected_at=incident_data.get("detected_at", datetime.utcnow()),
                first_acknowledged_at=None,
                first_resolved_at=None,
                closed_at=None,
                current_state=IncidentState.DETECTED,
                total_duration=None,
                time_to_acknowledge=None,
                time_to_resolve=None,
                affected_services=incident_data.get("affected_services", []),
                affected_users_count=incident_data.get("affected_users", 0),
                business_impact=incident_data.get("business_impact", "unknown"),
                financial_impact=incident_data.get("financial_impact", 0.0),
                sla_targets=self.sla_targets.get(IncidentPriority(incident_data.get("priority", "p3")), {}),
                post_mortem_required=incident_data.get("priority") in ["p1", "p2"]
            )
            
            # Add initial timeline event
            await self._add_timeline_event(
                timeline,
                "incident_created",
                "Incident detected and tracking started",
                {"source": incident_data.get("source", "unknown")}
            )
            
            # Initial state transition
            await self._record_state_transition(
                timeline,
                None,
                IncidentState.DETECTED,
                StateTransitionTrigger.SYSTEM,
                "system",
                "Incident detected"
            )
            
            # Store active incident
            self.active_incidents[timeline.incident_id] = timeline
            
            # Auto-allocate initial resources
            await self._auto_allocate_resources(timeline)
            
            # Start SLA monitoring
            if self.config["sla_monitoring"]:
                asyncio.create_task(self._monitor_sla_compliance(timeline))
            
            logger.info(f"Started tracking incident {timeline.incident_id}")
            return timeline
            
        except Exception as e:
            logger.error(f"Incident tracking start failed: {e}")
            return None
    
    async def transition_incident_state(self, incident_id: str, new_state: IncidentState,
                                      actor: str, reason: str = "",
                                      trigger: StateTransitionTrigger = StateTransitionTrigger.MANUAL) -> bool:
        """Transition incident to new state"""
        try:
            timeline = self.active_incidents.get(incident_id)
            if not timeline:
                logger.error(f"Incident {incident_id} not found")
                return False
            
            # Validate transition
            current_state = timeline.current_state
            allowed_transitions = self.state_machine_rules.get(current_state, {}).get("allowed_transitions", [])
            
            if new_state not in allowed_transitions:
                logger.error(f"Invalid transition from {current_state.value} to {new_state.value}")
                return False
            
            # Record state transition
            await self._record_state_transition(
                timeline, current_state, new_state, trigger, actor, reason
            )
            
            # Update timeline state
            timeline.current_state = new_state
            
            # Update timeline timestamps
            await self._update_timeline_timestamps(timeline, new_state)
            
            # Add timeline event
            await self._add_timeline_event(
                timeline,
                "state_transition",
                f"State changed from {current_state.value} to {new_state.value}",
                {"actor": actor, "reason": reason, "trigger": trigger.value}
            )
            
            # Handle state-specific actions
            await self._handle_state_specific_actions(timeline, new_state)
            
            # Check if incident is completed
            if new_state in [IncidentState.CLOSED]:
                await self._complete_incident(timeline)
            
            logger.info(f"Incident {incident_id} transitioned to {new_state.value}")
            return True
            
        except Exception as e:
            logger.error(f"State transition failed: {e}")
            return False
    
    async def _record_state_transition(self, timeline: IncidentTimeline,
                                     from_state: Optional[IncidentState],
                                     to_state: IncidentState,
                                     trigger: StateTransitionTrigger,
                                     actor: str, reason: str):
        """Record state transition"""
        try:
            # Calculate duration in previous state
            duration = None
            if from_state and timeline.state_transitions:
                last_transition = timeline.state_transitions[-1]
                duration = (datetime.utcnow() - last_transition.timestamp).total_seconds()
            
            transition = StateTransition(
                transition_id=str(uuid.uuid4()),
                incident_id=timeline.incident_id,
                from_state=from_state,
                to_state=to_state,
                timestamp=datetime.utcnow(),
                trigger=trigger,
                actor=actor,
                reason=reason,
                duration_in_previous_state=duration,
                automated=trigger in [StateTransitionTrigger.AUTOMATIC, StateTransitionTrigger.TIMEOUT]
            )
            
            timeline.state_transitions.append(transition)
            
        except Exception as e:
            logger.error(f"State transition recording failed: {e}")
    
    async def _update_timeline_timestamps(self, timeline: IncidentTimeline, new_state: IncidentState):
        """Update timeline timestamps based on state"""
        try:
            now = datetime.utcnow()
            
            if new_state == IncidentState.ACKNOWLEDGED and not timeline.first_acknowledged_at:
                timeline.first_acknowledged_at = now
                timeline.time_to_acknowledge = (now - timeline.first_detected_at).total_seconds()
            
            elif new_state == IncidentState.RESOLVED and not timeline.first_resolved_at:
                timeline.first_resolved_at = now
                timeline.time_to_resolve = (now - timeline.first_detected_at).total_seconds()
            
            elif new_state == IncidentState.CLOSED:
                timeline.closed_at = now
                timeline.total_duration = (now - timeline.first_detected_at).total_seconds()
            
        except Exception as e:
            logger.error(f"Timeline timestamp update failed: {e}")
    
    async def _handle_state_specific_actions(self, timeline: IncidentTimeline, state: IncidentState):
        """Handle actions required for specific states"""
        try:
            rules = self.state_machine_rules.get(state, {})
            required_actions = rules.get("required_actions", [])
            
            for action in required_actions:
                await self._execute_required_action(timeline, action)
            
            # Setup auto-transition if configured
            auto_timeout = rules.get("auto_transition_timeout")
            auto_target = rules.get("auto_transition_target")
            
            if auto_timeout and auto_target and self.config["auto_state_transitions"]:
                asyncio.create_task(
                    self._schedule_auto_transition(timeline, auto_timeout, auto_target)
                )
            
        except Exception as e:
            logger.error(f"State-specific action handling failed: {e}")
    
    async def _execute_required_action(self, timeline: IncidentTimeline, action: str):
        """Execute required action for state"""
        try:
            if action == "assign_responder":
                await self._assign_initial_responder(timeline)
            
            elif action == "initial_assessment":
                await self._perform_initial_assessment(timeline)
            
            elif action == "start_investigation":
                await self._start_investigation(timeline)
            
            elif action == "root_cause_analysis":
                await self._add_timeline_event(
                    timeline, "action_required", "Root cause analysis needed",
                    {"action": action, "priority": timeline.priority.value}
                )
            
            elif action == "implement_fix":
                await self._add_timeline_event(
                    timeline, "action_required", "Fix implementation needed",
                    {"action": action}
                )
            
            elif action == "confirm_stability":
                await self._add_timeline_event(
                    timeline, "monitoring", "Monitoring system stability",
                    {"action": action, "duration": "1 hour"}
                )
            
            elif action == "complete_documentation":
                await self._add_timeline_event(
                    timeline, "documentation", "Completing incident documentation",
                    {"action": action, "post_mortem_required": timeline.post_mortem_required}
                )
            
        except Exception as e:
            logger.error(f"Required action execution failed: {e}")
    
    async def _schedule_auto_transition(self, timeline: IncidentTimeline, 
                                      timeout_seconds: int, target_state: IncidentState):
        """Schedule automatic state transition"""
        try:
            await asyncio.sleep(timeout_seconds)
            
            # Check if incident still in expected state
            current_incident = self.active_incidents.get(timeline.incident_id)
            if current_incident and current_incident.current_state == timeline.current_state:
                await self.transition_incident_state(
                    timeline.incident_id,
                    target_state,
                    "system",
                    f"Auto-transition after {timeout_seconds} seconds",
                    StateTransitionTrigger.TIMEOUT
                )
            
        except Exception as e:
            logger.error(f"Auto-transition scheduling failed: {e}")
    
    async def _auto_allocate_resources(self, timeline: IncidentTimeline):
        """Auto-allocate resources based on incident priority"""
        try:
            # Determine required resources based on priority
            if timeline.priority == IncidentPriority.P1:
                required_resources = [
                    (ResourceType.SRE, 2),
                    (ResourceType.ENGINEER, 3),
                    (ResourceType.MANAGER, 1),
                    (ResourceType.COMMUNICATIONS, 1)
                ]
            elif timeline.priority == IncidentPriority.P2:
                required_resources = [
                    (ResourceType.SRE, 1),
                    (ResourceType.ENGINEER, 2),
                    (ResourceType.SUPPORT, 1)
                ]
            else:
                required_resources = [
                    (ResourceType.ENGINEER, 1),
                    (ResourceType.SUPPORT, 1)
                ]
            
            # Allocate resources
            for resource_type, count in required_resources:
                for i in range(count):
                    await self._allocate_resource(timeline, resource_type, f"{resource_type.value}_{i+1}")
            
        except Exception as e:
            logger.error(f"Auto-resource allocation failed: {e}")
    
    async def _allocate_resource(self, timeline: IncidentTimeline, 
                               resource_type: ResourceType, resource_id: str):
        """Allocate specific resource to incident"""
        try:
            pool = self.resource_pools.get(resource_type, {})
            cost_per_hour = pool.get("cost_per_hour", 0.0)
            
            allocation = ResourceAllocation(
                allocation_id=str(uuid.uuid4()),
                incident_id=timeline.incident_id,
                resource_type=resource_type,
                resource_identifier=resource_id,
                allocated_at=datetime.utcnow(),
                deallocated_at=None,
                utilization_percentage=100.0,
                cost_per_hour=cost_per_hour,
                total_cost=0.0,
                notes=f"Auto-allocated for {timeline.priority.value} incident"
            )
            
            timeline.resource_allocations.append(allocation)
            
            await self._add_timeline_event(
                timeline,
                "resource_allocated",
                f"Allocated {resource_type.value}: {resource_id}",
                {"resource_type": resource_type.value, "cost_per_hour": cost_per_hour}
            )
            
        except Exception as e:
            logger.error(f"Resource allocation failed: {e}")
    
    async def _assign_initial_responder(self, timeline: IncidentTimeline):
        """Assign initial responder to incident"""
        try:
            # Find best available responder based on skills and availability
            responder = await self._find_best_responder(timeline)
            
            await self._add_timeline_event(
                timeline,
                "responder_assigned",
                f"Initial responder assigned: {responder}",
                {"responder": responder, "assignment_method": "automatic"}
            )
            
        except Exception as e:
            logger.error(f"Responder assignment failed: {e}")
    
    async def _find_best_responder(self, timeline: IncidentTimeline) -> str:
        """Find best available responder"""
        try:
            # Determine required skills based on affected services
            required_skills = []
            for service in timeline.affected_services:
                if "api" in service.lower():
                    required_skills.append("backend")
                elif "ui" in service.lower() or "frontend" in service.lower():
                    required_skills.append("frontend")
                elif "db" in service.lower() or "database" in service.lower():
                    required_skills.append("database")
                elif "infra" in service.lower():
                    required_skills.append("infrastructure")
            
            # Mock responder selection
            if timeline.priority in [IncidentPriority.P1, IncidentPriority.P2]:
                return "senior-sre-on-call"
            else:
                return "engineer-on-call"
                
        except Exception as e:
            logger.error(f"Responder selection failed: {e}")
            return "default-responder"
    
    async def _perform_initial_assessment(self, timeline: IncidentTimeline):
        """Perform initial incident assessment"""
        try:
            assessment = {
                "affected_services": len(timeline.affected_services),
                "estimated_user_impact": timeline.affected_users_count,
                "business_impact": timeline.business_impact,
                "initial_priority": timeline.priority.value,
                "assessment_timestamp": datetime.utcnow().isoformat()
            }
            
            await self._add_timeline_event(
                timeline,
                "initial_assessment",
                "Initial impact assessment completed",
                assessment
            )
            
        except Exception as e:
            logger.error(f"Initial assessment failed: {e}")
    
    async def _start_investigation(self, timeline: IncidentTimeline):
        """Start incident investigation"""
        try:
            investigation_plan = {
                "investigation_areas": [
                    "Service dependencies",
                    "Recent deployments", 
                    "Infrastructure changes",
                    "Third-party services",
                    "Security events"
                ],
                "investigation_lead": await self._find_best_responder(timeline),
                "estimated_duration": self._estimate_investigation_duration(timeline),
                "tools_to_use": [
                    "Application logs",
                    "Metrics dashboard", 
                    "Distributed tracing",
                    "Error tracking"
                ]
            }
            
            await self._add_timeline_event(
                timeline,
                "investigation_started",
                "Investigation phase started",
                investigation_plan
            )
            
        except Exception as e:
            logger.error(f"Investigation start failed: {e}")
    
    def _estimate_investigation_duration(self, timeline: IncidentTimeline) -> str:
        """Estimate investigation duration"""
        if timeline.priority == IncidentPriority.P1:
            return "30 minutes"
        elif timeline.priority == IncidentPriority.P2:
            return "2 hours"
        else:
            return "4 hours"
    
    async def _add_timeline_event(self, timeline: IncidentTimeline, 
                                event_type: str, message: str, metadata: Dict[str, Any] = None):
        """Add event to incident timeline"""
        try:
            event = {
                "event_id": str(uuid.uuid4()),
                "timestamp": datetime.utcnow().isoformat(),
                "event_type": event_type,
                "message": message,
                "metadata": metadata or {}
            }
            
            timeline.timeline_events.append(event)
            
        except Exception as e:
            logger.error(f"Timeline event addition failed: {e}")
    
    async def _monitor_sla_compliance(self, timeline: IncidentTimeline):
        """Monitor SLA compliance for incident"""
        try:
            sla_targets = timeline.sla_targets
            
            # Monitor time to acknowledge
            if "time_to_acknowledge" in sla_targets:
                await asyncio.sleep(sla_targets["time_to_acknowledge"])
                
                if timeline.current_state == IncidentState.DETECTED:
                    breach = {
                        "sla_type": "time_to_acknowledge",
                        "target_seconds": sla_targets["time_to_acknowledge"],
                        "actual_seconds": (datetime.utcnow() - timeline.first_detected_at).total_seconds(),
                        "breach_time": datetime.utcnow().isoformat()
                    }
                    timeline.sla_breaches.append(breach)
                    
                    await self._add_timeline_event(
                        timeline,
                        "sla_breach",
                        "SLA breach: Time to acknowledge exceeded",
                        breach
                    )
            
            # Monitor time to resolve
            if "time_to_resolve" in sla_targets:
                await asyncio.sleep(sla_targets["time_to_resolve"])
                
                if timeline.current_state not in [IncidentState.RESOLVED, IncidentState.CLOSED]:
                    breach = {
                        "sla_type": "time_to_resolve",
                        "target_seconds": sla_targets["time_to_resolve"],
                        "actual_seconds": (datetime.utcnow() - timeline.first_detected_at).total_seconds(),
                        "breach_time": datetime.utcnow().isoformat()
                    }
                    timeline.sla_breaches.append(breach)
                    
                    await self._add_timeline_event(
                        timeline,
                        "sla_breach",
                        "SLA breach: Time to resolve exceeded",
                        breach
                    )
            
        except Exception as e:
            logger.error(f"SLA monitoring failed: {e}")
    
    async def _complete_incident(self, timeline: IncidentTimeline):
        """Complete incident and move to historical data"""
        try:
            # Calculate final costs
            await self._calculate_final_costs(timeline)
            
            # Deallocate all resources
            await self._deallocate_all_resources(timeline)
            
            # Move to completed incidents
            self.completed_incidents[timeline.incident_id] = timeline
            del self.active_incidents[timeline.incident_id]
            
            # Schedule post-mortem if required
            if timeline.post_mortem_required and not timeline.post_mortem_completed:
                await self._schedule_post_mortem(timeline)
            
            await self._add_timeline_event(
                timeline,
                "incident_completed",
                "Incident lifecycle completed",
                {
                    "total_duration": timeline.total_duration,
                    "total_cost": sum(alloc.total_cost for alloc in timeline.resource_allocations),
                    "sla_breaches": len(timeline.sla_breaches),
                    "post_mortem_required": timeline.post_mortem_required
                }
            )
            
            logger.info(f"Incident {timeline.incident_id} completed")
            
        except Exception as e:
            logger.error(f"Incident completion failed: {e}")
    
    async def _calculate_final_costs(self, timeline: IncidentTimeline):
        """Calculate final incident costs"""
        try:
            for allocation in timeline.resource_allocations:
                if not allocation.deallocated_at:
                    allocation.deallocated_at = datetime.utcnow()
                
                duration_hours = (allocation.deallocated_at - allocation.allocated_at).total_seconds() / 3600
                allocation.total_cost = duration_hours * allocation.cost_per_hour
                
                # Update timeline financial impact
                timeline.financial_impact += allocation.total_cost
            
        except Exception as e:
            logger.error(f"Final cost calculation failed: {e}")
    
    async def _deallocate_all_resources(self, timeline: IncidentTimeline):
        """Deallocate all resources from incident"""
        try:
            now = datetime.utcnow()
            
            for allocation in timeline.resource_allocations:
                if not allocation.deallocated_at:
                    allocation.deallocated_at = now
                    
                    await self._add_timeline_event(
                        timeline,
                        "resource_deallocated",
                        f"Deallocated {allocation.resource_type.value}: {allocation.resource_identifier}",
                        {
                            "resource_type": allocation.resource_type.value,
                            "total_cost": allocation.total_cost,
                            "duration_hours": (now - allocation.allocated_at).total_seconds() / 3600
                        }
                    )
            
        except Exception as e:
            logger.error(f"Resource deallocation failed: {e}")
    
    async def _schedule_post_mortem(self, timeline: IncidentTimeline):
        """Schedule post-mortem meeting"""
        try:
            post_mortem_data = {
                "incident_id": timeline.incident_id,
                "scheduled_for": (datetime.utcnow() + timedelta(days=2)).isoformat(),
                "attendees": ["incident_commander", "engineering_leads", "sre_team"],
                "agenda": [
                    "Timeline review",
                    "Root cause analysis",
                    "Impact assessment",
                    "Response effectiveness",
                    "Preventive actions"
                ]
            }
            
            await self._add_timeline_event(
                timeline,
                "post_mortem_scheduled",
                "Post-mortem meeting scheduled",
                post_mortem_data
            )
            
        except Exception as e:
            logger.error(f"Post-mortem scheduling failed: {e}")
    
    async def get_incident_metrics(self, period_days: int = 30) -> LifecycleMetrics:
        """Calculate incident lifecycle metrics"""
        try:
            end_time = datetime.utcnow()
            start_time = end_time - timedelta(days=period_days)
            
            # Get incidents in period
            period_incidents = []
            for incident in list(self.completed_incidents.values()) + list(self.active_incidents.values()):
                if start_time <= incident.created_at <= end_time:
                    period_incidents.append(incident)
            
            # Calculate metrics
            metrics = LifecycleMetrics(
                metric_id=str(uuid.uuid4()),
                period_start=start_time,
                period_end=end_time,
                total_incidents=len(period_incidents),
                incidents_by_priority={},
                incidents_by_state={},
                average_time_to_acknowledge=0.0,
                average_time_to_resolve=0.0,
                median_time_to_resolve=0.0,
                p95_time_to_resolve=0.0,
                sla_compliance_rate=0.0,
                reopened_incidents_count=0,
                escalated_incidents_count=0,
                resource_utilization={},
                total_incident_cost=0.0,
                most_frequent_failure_modes=[],
                improvement_trends={}
            )
            
            # Count by priority
            for priority in IncidentPriority:
                metrics.incidents_by_priority[priority.value] = sum(
                    1 for inc in period_incidents if inc.priority == priority
                )
            
            # Count by state
            for state in IncidentState:
                metrics.incidents_by_state[state.value] = sum(
                    1 for inc in period_incidents if inc.current_state == state
                )
            
            # Calculate timing metrics
            ack_times = [inc.time_to_acknowledge for inc in period_incidents if inc.time_to_acknowledge]
            resolve_times = [inc.time_to_resolve for inc in period_incidents if inc.time_to_resolve]
            
            if ack_times:
                metrics.average_time_to_acknowledge = sum(ack_times) / len(ack_times)
            
            if resolve_times:
                metrics.average_time_to_resolve = sum(resolve_times) / len(resolve_times)
                resolve_times.sort()
                metrics.median_time_to_resolve = resolve_times[len(resolve_times) // 2]
                metrics.p95_time_to_resolve = resolve_times[int(len(resolve_times) * 0.95)]
            
            # Calculate SLA compliance
            total_with_sla = 0
            compliant_count = 0
            
            for incident in period_incidents:
                if incident.sla_targets and incident.time_to_resolve:
                    total_with_sla += 1
                    if incident.time_to_resolve <= incident.sla_targets.get("time_to_resolve", float('inf')):
                        compliant_count += 1
            
            if total_with_sla > 0:
                metrics.sla_compliance_rate = (compliant_count / total_with_sla) * 100
            
            # Count reopened incidents
            metrics.reopened_incidents_count = sum(
                1 for inc in period_incidents
                if any(t.to_state == IncidentState.REOPENED for t in inc.state_transitions)
            )
            
            # Calculate total cost
            metrics.total_incident_cost = sum(inc.financial_impact for inc in period_incidents)
            
            # Calculate resource utilization
            for resource_type in ResourceType:
                total_hours = sum(
                    sum((alloc.deallocated_at or datetime.utcnow() - alloc.allocated_at).total_seconds() / 3600
                        for alloc in inc.resource_allocations if alloc.resource_type == resource_type)
                    for inc in period_incidents
                )
                metrics.resource_utilization[resource_type] = total_hours
            
            return metrics
            
        except Exception as e:
            logger.error(f"Metrics calculation failed: {e}")
            return LifecycleMetrics(
                metric_id=str(uuid.uuid4()),
                period_start=datetime.utcnow(),
                period_end=datetime.utcnow(),
                total_incidents=0,
                incidents_by_priority={},
                incidents_by_state={},
                average_time_to_acknowledge=0.0,
                average_time_to_resolve=0.0,
                median_time_to_resolve=0.0,
                p95_time_to_resolve=0.0,
                sla_compliance_rate=0.0,
                reopened_incidents_count=0,
                escalated_incidents_count=0,
                resource_utilization={},
                total_incident_cost=0.0,
                most_frequent_failure_modes=[],
                improvement_trends={}
            )
    
    async def get_incident_timeline(self, incident_id: str) -> Optional[IncidentTimeline]:
        """Get complete incident timeline"""
        try:
            timeline = self.active_incidents.get(incident_id) or self.completed_incidents.get(incident_id)
            return timeline
            
        except Exception as e:
            logger.error(f"Timeline retrieval failed: {e}")
            return None
    
    async def get_lifecycle_dashboard(self) -> Dict[str, Any]:
        """Get lifecycle tracking dashboard"""
        try:
            active_count = len(self.active_incidents)
            completed_count = len(self.completed_incidents)
            
            # Get recent metrics
            metrics = await self.get_incident_metrics(7)  # Last 7 days
            
            dashboard = {
                "summary": {
                    "active_incidents": active_count,
                    "completed_incidents": completed_count,
                    "total_incidents": active_count + completed_count,
                    "avg_resolution_time": f"{metrics.average_time_to_resolve / 3600:.1f} hours" if metrics.average_time_to_resolve else "N/A",
                    "sla_compliance_rate": f"{metrics.sla_compliance_rate:.1f}%"
                },
                "active_incidents": [
                    {
                        "incident_id": inc.incident_id,
                        "title": inc.title,
                        "priority": inc.priority.value,
                        "state": inc.current_state.value,
                        "duration": f"{(datetime.utcnow() - inc.created_at).total_seconds() / 3600:.1f}h",
                        "resources_allocated": len(inc.resource_allocations)
                    }
                    for inc in list(self.active_incidents.values())[:10]
                ],
                "metrics": {
                    "incidents_by_priority": metrics.incidents_by_priority,
                    "incidents_by_state": metrics.incidents_by_state,
                    "resource_utilization": {rt.value: hours for rt, hours in metrics.resource_utilization.items()},
                    "total_cost": f"${metrics.total_incident_cost:.2f}"
                },
                "trends": {
                    "resolution_time_trend": "improving",  # Mock data
                    "incident_frequency_trend": "stable",  # Mock data
                    "cost_trend": "increasing"  # Mock data
                }
            }
            
            return dashboard
            
        except Exception as e:
            logger.error(f"Dashboard generation failed: {e}")
            return {}


# Global incident lifecycle tracker instance
_incident_lifecycle_tracker = None


def get_incident_lifecycle_tracker(pagerduty_client=None) -> IncidentLifecycleTracker:
    """Get incident lifecycle tracker instance"""
    global _incident_lifecycle_tracker
    if _incident_lifecycle_tracker is None:
        _incident_lifecycle_tracker = IncidentLifecycleTracker(pagerduty_client)
    return _incident_lifecycle_tracker


def create_incident_lifecycle_tracker(pagerduty_client=None) -> IncidentLifecycleTracker:
    """Create new incident lifecycle tracker instance"""
    return IncidentLifecycleTracker(pagerduty_client)


# Export main classes and functions
__all__ = [
    'IncidentLifecycleTracker',
    'IncidentTimeline',
    'StateTransition',
    'ResourceAllocation',
    'LifecycleMetrics',
    'IncidentState',
    'StateTransitionTrigger',
    'ResourceType',
    'IncidentPriority',
    'get_incident_lifecycle_tracker',
    'create_incident_lifecycle_tracker'
]